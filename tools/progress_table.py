import datetime
import json
import os
import re
import sys

START = "<!-- progress:start -->"
END = "<!-- progress:end -->"
BAR_WIDTH = 10
HOLIDAY_ZONES = {-22, -41, -364, -366, -369, -370, -373, -374, -375, -376, -1002, -1003, -1005}
NOT_STARTED = [
    "Реплики NPC вне квестов",
    "Тексты для женских персонажей",
]

quests_path, module_dir, readme_path = sys.argv[1:4]
horde_path = sys.argv[4] if len(sys.argv) > 4 else None

lengths_path = os.path.join(module_dir, "generated", "sound_length_table.lua")
done = set(re.findall(r'\["([^"]+)"\] =', open(lengths_path, encoding="utf-8").read())) if os.path.exists(lengths_path) else set()


def band_of(quest):
    if quest["zone"] in HOLIDAY_ZONES:
        return "Праздничные события"
    low = (min(quest["level"], 80) - 1) // 10 * 10 + 1
    return f"Уровни {low}–{low + 9}"


def bar(fraction):
    filled = round(fraction * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def status(fraction):
    if fraction >= 1:
        return "✅ готово"
    if fraction > 0:
        return "🔄 в работе"
    return "⏳ в очереди"


def progress_rows(title, selected):
    bands = {}
    for quest in selected:
        band = bands.setdefault(band_of(quest), {"quests": 0, "quests_done": 0, "files": 0, "files_done": 0})
        names = [f"{quest['id']}-{event}" for event in ("accept", "complete") if quest[event]]
        finished = sum(name in done for name in names)
        band["quests"] += 1
        band["quests_done"] += finished == len(names)
        band["files"] += len(names)
        band["files_done"] += finished

    rows = [f"| {title} | Готово | Прогресс | Статус |", "|---|---|---|---|"]
    order = sorted(bands, key=lambda name: (name == "Праздничные события", int(re.search(r"\d+", name).group()) if "Уровни" in name else 0))
    total = {"quests": 0, "quests_done": 0, "files": 0, "files_done": 0}
    for name in order:
        band = bands[name]
        fraction = band["files_done"] / band["files"]
        rows.append(f"| {name} | {band['quests_done']} / {band['quests']} | `{bar(fraction)}` {fraction:.0%} | {status(fraction)} |")
        for key in total:
            total[key] += band[key]
    fraction = total["files_done"] / total["files"]
    rows.append(f"| **Всего** | **{total['quests_done']} / {total['quests']}** | `{bar(fraction)}` **{fraction:.0%}** | |")
    print(f"{title}: {total['quests_done']}/{total['quests']} quests, {total['files_done']}/{total['files']} files")
    return rows


rows = progress_rows("Квесты Альянса и нейтральные", json.load(open(quests_path, encoding="utf-8"))["selected"])
if horde_path:
    rows += [""] + progress_rows("Квесты Орды", json.load(open(horde_path, encoding="utf-8"))["selected"])
else:
    NOT_STARTED.insert(0, "Квесты Орды")
rows += ["", "| Ещё не озвучено | Статус |", "|---|---|"]
for name in NOT_STARTED:
    rows.append(f"| {name} | ❌ не начато |")

updated = datetime.date.today().strftime("%d.%m.%Y")
section = "\n".join([START, f"_Обновлено {updated}._", "", *rows, END])

readme = open(readme_path, encoding="utf-8").read()
if START not in readme or END not in readme:
    sys.exit(f"markers {START} / {END} not found in {readme_path}")
readme = readme[:readme.index(START)] + section + readme[readme.index(END) + len(END):]
with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
