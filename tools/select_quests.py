import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqldump

GROUP_ALLIANCE = 2
GROUP_HORDE = 4
FACTIONS = {
    "alliance": {"races": 1 | 4 | 8 | 64 | 1024, "own": GROUP_ALLIANCE, "enemy": GROUP_HORDE},
    "horde": {"races": 2 | 16 | 32 | 128 | 512, "own": GROUP_HORDE, "enemy": GROUP_ALLIANCE},
}
HOLIDAY_ZONES = {-22, -41, -364, -366, -369, -370, -373, -374, -375, -376, -1002, -1003, -1005}
TEXT_FIXES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "quest_text_fixes.json"), encoding="utf-8"))

sql_dir, out_path, wrath_lengths = sys.argv[1:4]
faction_name = sys.argv[4] if len(sys.argv) > 4 else "alliance"
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


def can_talk_to(creature, faction):
    template = templates.get(creature_faction.get(creature, 0))
    if template is None:
        return True
    ours = int(template["FactionGroup"]) | int(template["FriendGroup"])
    if int(template["EnemyGroup"]) & faction["own"]:
        return False
    return not (ours & faction["enemy"]) or bool(ours & faction["own"])


def exclusion_reason(quest_id, entry, faction):
    races = int(quests[quest_id]["AllowableRaces"])
    if races and not races & faction["races"]:
        return "other faction races"
    givers = starters.get(quest_id) or enders.get(quest_id)
    if givers and not any(can_talk_to(c, faction) for c in givers):
        return "other faction quest giver"
    if not givers and quest_id not in wrath_voiced:
        return "no giver and not voiced in Wrath"
    if not entry["accept"] and not entry["complete"]:
        return "no text"
    return None


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
    entry.update(TEXT_FIXES.get(str(quest_id), {}))
    lookup_entries.append(entry)
    reason = exclusion_reason(quest_id, entry, FACTIONS[faction_name])
    if reason is None and faction_name != "alliance" and exclusion_reason(quest_id, entry, FACTIONS["alliance"]) is None:
        reason = "already selected for alliance"
    if reason:
        excluded[reason] += 1
        continue
    selected.append(entry)

selected.sort(key=lambda q: (q["zone"] in HOLIDAY_ZONES, q["level"], q["zone"], q["id"]))

with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"selected": selected, "lookup": lookup_entries}, f, ensure_ascii=False)

print("ruRU quests", len(lookup_entries), "selected", len(selected), dict(excluded))
print("chars", sum(len(q["accept"]) + len(q["complete"]) for q in selected))
print("levels", Counter(min(q["level"] // 10 * 10, 80) for q in selected))
