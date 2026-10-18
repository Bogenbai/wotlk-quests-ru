import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqldump

LUA_STRING = r'"((?:[^"\\]|\\.)*)"'
STAGE_DIRECTION = re.compile(r"<[^>]*>")

sql_dir, wrath_generated, out_path = sys.argv[1:4]


def table(name):
    return sqldump.load(os.path.join(sql_dir, name + ".sql"))


def parse_gossip_lookup(path):
    lookup = {}
    texts = None
    for line in open(path, encoding="utf-8"):
        owner = re.match(r"\s{4}\[(\d+)\] = \{", line)
        if owner:
            texts = lookup.setdefault(int(owner.group(1)), {})
            continue
        entry = re.match(r"\s{8}\[" + LUA_STRING + r'\] = "([0-9a-f]+)"', line)
        if entry and texts is not None:
            texts[unescape(entry.group(1))] = entry.group(2)
    return lookup


def unescape(text):
    return re.sub(r"\\(.)", lambda m: "\n" if m.group(1) == "n" else m.group(1), text)


def normalize(text):
    return re.sub(r"\s+", " ", text.replace('"', "'")).strip().lower()


def english_to_russian():
    russian = {r["ID"]: r for r in table("broadcast_text_locale") if r["locale"] == "ruRU"}
    mapping = {}
    for row in table("broadcast_text"):
        ru = russian.get(row["ID"])
        if not ru:
            continue
        for field, other in (("MaleText", "FemaleText"), ("FemaleText", "MaleText")):
            text = ru[field] or ru[other]
            if row[field] and text:
                mapping.setdefault(normalize(row[field]), text)
    greetings = {(r["ID"], r["type"]): r["Greeting"] for r in table("quest_greeting")}
    for row in table("quest_greeting_locale"):
        english = greetings.get((row["ID"], row["type"]))
        if row["locale"] == "ruRU" and english and row["Greeting"]:
            mapping.setdefault(normalize(english), row["Greeting"])
    return mapping


def shown_to_male(text):
    return re.sub(r"\$[gG]\s*([^:;]*):([^;]*);", lambda m: m.group(1), text)


def spoken(text):
    return re.sub(r"[ \t]+", " ", STAGE_DIRECTION.sub("", text)).strip()


npc_lookup = parse_gossip_lookup(os.path.join(wrath_generated, "npc_gossip_file_lookups.lua"))
object_lookup = parse_gossip_lookup(os.path.join(wrath_generated, "object_gossip_file_lookups.lua"))
min_level = {int(r["entry"]): int(r["minlevel"]) for r in table("creature_template")}
translations = english_to_russian()

lines = {}
lookups = {"npc": {}, "object": {}}
for kind, lookup in (("npc", npc_lookup), ("object", object_lookup)):
    for owner, texts in lookup.items():
        for english, hash_ in texts.items():
            russian = translations.get(normalize(english))
            if not russian or not spoken(russian):
                continue
            lookups[kind].setdefault(str(owner), {})[shown_to_male(russian)] = hash_
            line = lines.setdefault(hash_, {"hash": hash_, "text": spoken(russian), "level": 0, "npcs": [], "objects": []})
            line["npcs" if kind == "npc" else "objects"].append(owner)

for line in lines.values():
    levels = [min_level.get(npc, 0) for npc in line["npcs"]]
    line["level"] = min(levels) if levels else 0
    owner_texts = npc_lookup.get(line["npcs"][0]) if line["npcs"] else object_lookup.get(line["objects"][0])
    line["voice_hashes"] = [line["hash"]] + sorted(set(owner_texts.values()) - {line["hash"]})

ordered = sorted(lines.values(), key=lambda line: (line["level"], line["hash"]))
english_total = len({h for lookup in (npc_lookup, object_lookup) for texts in lookup.values() for h in texts.values()})
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"lines": ordered, "lookups": lookups}, f, ensure_ascii=False)
print(f"wrath gossip {english_total} translated {len(ordered)} chars {sum(len(line['text']) for line in ordered)}")
