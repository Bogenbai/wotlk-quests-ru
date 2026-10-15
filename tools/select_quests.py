import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqldump

ALLIANCE_RACES = 1 | 4 | 8 | 64 | 1024
GROUP_ALLIANCE = 2
GROUP_HORDE = 4
HOLIDAY_ZONES = {-22, -41, -364, -366, -369, -370, -373, -374, -375, -376, -1002, -1003, -1005}

sql_dir, out_path, wrath_lengths = sys.argv[1:4]
wrath_voiced = {int(x) for x in re.findall(r'\["(?:[mf]-)?(\d+)-(?:accept|complete)"\]', open(wrath_lengths, encoding="utf-8").read())}


def table(name):
    return sqldump.load(os.path.join(sql_dir, name + ".sql"))


def ru(rows, key):
    return {int(r[key]): r for r in rows if r["locale"] == "ruRU"}


quests = {int(r["ID"]): r for r in table("quest_template")}
quest_ru = ru(table("quest_template_locale"), "ID")
reward_ru = ru(table("quest_offer_reward_locale"), "ID")
creature_ru = ru(table("creature_template_locale"), "entry")
creature_faction = {int(r["entry"]): int(r["faction"]) for r in table("creature_template")}
templates = {int(r["ID"]): r for r in table("factiontemplate_dbc")}

display_gender = {int(r["DisplayID"]): int(r["Gender"]) for r in table("creature_model_info")}
creature_gender = {}
for r in sorted(table("creature_template_model"), key=lambda r: int(r["Idx"])):
    creature_gender.setdefault(int(r["CreatureID"]), display_gender.get(int(r["CreatureDisplayID"]), 2))

starters = defaultdict(list)
for r in table("creature_queststarter"):
    starters[int(r["quest"])].append(int(r["id"]))
enders = defaultdict(list)
for r in table("creature_questender"):
    enders[int(r["quest"])].append(int(r["id"]))


def alliance_can_talk_to(creature):
    template = templates.get(creature_faction.get(creature, 0))
    if template is None:
        return True
    ours = int(template["FactionGroup"]) | int(template["FriendGroup"])
    if int(template["EnemyGroup"]) & GROUP_ALLIANCE:
        return False
    return not (ours & GROUP_HORDE) or bool(ours & GROUP_ALLIANCE)


def races_allow_alliance(quest_id):
    races = int(quests[quest_id]["AllowableRaces"])
    return races == 0 or bool(races & ALLIANCE_RACES)


def level_of(quest_id):
    quest = quests[quest_id]
    level = int(quest["QuestLevel"])
    return level if level > 0 else max(int(quest["MinLevel"]), 1)


def npc(entry):
    return {"id": entry, "name": (creature_ru.get(entry) or {}).get("Name"), "gender": creature_gender.get(entry, 2)}


title_count = Counter((q["Title"] or "").strip() for q in quest_ru.values())

lookup_entries = []
selected = []
excluded = Counter()
for quest_id in sorted(set(quest_ru) & set(quests)):
    loc = quest_ru[quest_id]
    title = (loc["Title"] or "").strip()
    entry = {
        "id": quest_id,
        "title": title,
        "title_unique": title_count[title] == 1,
        "level": level_of(quest_id),
        "zone": int(quests[quest_id]["QuestSortID"]),
        "accept": (loc["Details"] or "").strip(),
        "complete": ((reward_ru.get(quest_id) or {}).get("RewardText") or "").strip(),
        "starters": [npc(e) for e in starters.get(quest_id, [])],
        "enders": [npc(e) for e in enders.get(quest_id, [])],
    }
    lookup_entries.append(entry)
    if not races_allow_alliance(quest_id):
        excluded["horde races"] += 1
        continue
    givers = starters.get(quest_id) or enders.get(quest_id)
    if givers and not any(alliance_can_talk_to(c) for c in givers):
        excluded["horde quest giver"] += 1
        continue
    if not givers and quest_id not in wrath_voiced:
        excluded["no giver and not voiced in Wrath"] += 1
        continue
    if not entry["accept"] and not entry["complete"]:
        excluded["no text"] += 1
        continue
    selected.append(entry)

selected.sort(key=lambda q: (q["zone"] in HOLIDAY_ZONES, q["level"], q["zone"], q["id"]))

with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"selected": selected, "lookup": lookup_entries}, f, ensure_ascii=False)

print("ruRU quests", len(lookup_entries), "selected", len(selected), dict(excluded))
print("chars", sum(len(q["accept"]) + len(q["complete"]) for q in selected))
print("levels", Counter(min(q["level"] // 10 * 10, 80) for q in selected))
