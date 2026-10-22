import argparse
import json
import os
import re
import shutil
from collections import Counter

import soundfile

MODULE_NAME = "AI_VoiceOverData_CatQuest"
MODULE_PRIORITY = 300
HEADER = "if not VoiceOver or not VoiceOver.DataModules then return end\n"
EVENTS = {"accept": "", "complete": "_t"}
CAPTION = re.compile(r'\{ [\d.]+, "((?:[^"\\]|\\.)*)" \}')

TOC = f"""## Interface: 30300
## Title: VoiceOver Data - Russian (CatQuest)
## Notes: Озвучка квестов 1-60 из CatQuest Voices
## Version: 1
## LoadOnDemand: 1
## OptionalDeps: AI_VoiceOver
## X-Part-Of: VoiceOver
## X-Child-Of: VoiceOver
## X-VoiceOver-DataModule-Version: 1
## X-VoiceOver-DataModule-Priority: {MODULE_PRIORITY}

Module.lua
generated\\sound_length_table.lua
"""

MODULE_LUA = f"""{HEADER}
{MODULE_NAME} = {{}}

function {MODULE_NAME}:GetSoundPath(fileName, event)
    return format([=[generated\\sounds\\quests\\%s.ogg]=], fileName)
end

VoiceOver.DataModules:Register("{MODULE_NAME}", {MODULE_NAME})
"""

NOTICE = """Озвучка в этой папке взята из CatQuest Voices (автор Cathey / daniilcathey,
https://www.curseforge.com/wow/addons/catquest-voices) и распространяется по лицензии
CC BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/
Изменения: файлы переименованы под формат AI VoiceOver для клиента 3.3.5a.
"""


def parse_index(path):
    pack = {}
    for line in open(path, encoding="utf-8"):
        entry = re.match(r"    \[(\d+)\] = \{(.*)\},\s*$", line)
        if not entry:
            continue
        detail, _, turnin = entry.group(2).partition(", t = {")
        pack[int(entry.group(1))] = {"accept": parse_part(detail), "complete": parse_part(turnin)}
    return pack


def parse_part(part):
    if " d = " not in part or "c = {" not in part:
        return None
    captions = part[part.index("c = {"):]
    first_variant = captions.split(" }, f = {")[0]
    return {"gendered": "g = 1" in part.split("c = {")[0], "text": " ".join(CAPTION.findall(first_variant))}


def words(text):
    text = re.sub(r"\$[gG]\s*([^:;]*):([^;]*);", r"\1", text)
    text = re.sub(r"\$[nNcCrRbB]", " ", text)
    return set(re.findall(r"\w+", text.lower().replace("ё", "е")))


def similarity(a, b):
    a, b = words(a), words(b)
    return len(a & b) / len(a | b) if a | b else 0


def place(source, target):
    if os.path.exists(target):
        os.remove(target)
    try:
        os.link(source, target)
    except OSError:
        shutil.copyfile(source, target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catquest_voices")
    parser.add_argument("quests")
    parser.add_argument("module_dir")
    parser.add_argument("--min-similarity", type=float, default=0.2)
    args = parser.parse_args()

    pack = parse_index(os.path.join(args.catquest_voices, "Index.lua"))
    quests = {quest["id"]: quest for quest in json.load(open(args.quests, encoding="utf-8"))["lookup"]}
    sounds_source = os.path.join(args.catquest_voices, "Sounds", "q")
    sounds_dir = os.path.join(args.module_dir, "generated", "sounds", "quests")
    if os.path.isdir(sounds_dir):
        shutil.rmtree(sounds_dir)
    os.makedirs(sounds_dir)

    lengths = {}
    stats = Counter()
    for quest_id, events in sorted(pack.items()):
        quest = quests.get(quest_id)
        if not quest:
            stats["not on 3.3.5a"] += 1
            continue
        for event, suffix in EVENTS.items():
            voiced = events[event]
            if not voiced or not quest[event]:
                continue
            if similarity(voiced["text"], quest[event]) < args.min_similarity:
                stats["text differs"] += 1
                continue
            variants = (("m-", "_m"), ("f-", "_f")) if voiced["gendered"] else (("", ""),)
            for prefix, gender in variants:
                source = os.path.join(sounds_source, f"{quest_id}{suffix}{gender}.ogg")
                name = f"{prefix}{quest_id}-{event}"
                target = os.path.join(sounds_dir, name + ".ogg")
                place(source, target)
                lengths[name] = round(soundfile.info(target).duration, 2)
            stats[event] += 1

    os.makedirs(os.path.join(args.module_dir, "generated"), exist_ok=True)
    with open(os.path.join(args.module_dir, MODULE_NAME + ".toc"), "w", encoding="utf-8", newline="\n") as f:
        f.write(TOC)
    with open(os.path.join(args.module_dir, "Module.lua"), "w", encoding="utf-8", newline="\n") as f:
        f.write(MODULE_LUA)
    with open(os.path.join(args.module_dir, "LICENSE-CatQuest.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(NOTICE)
    lines = [HEADER, f"{MODULE_NAME}.SoundLengthLookupByFileName = {{"]
    lines += [f'    ["{name}"] = {length:.2f},' for name, length in sorted(lengths.items())]
    lines.append("}")
    with open(os.path.join(args.module_dir, "generated", "sound_length_table.lua"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(dict(stats), "files", len(lengths), "hours", round(sum(lengths.values()) / 3600, 1))


if __name__ == "__main__":
    main()
