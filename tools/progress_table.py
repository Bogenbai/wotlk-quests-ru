import argparse
import datetime
import json
import os
import re
import sys

START = "<!-- progress:start -->"
END = "<!-- progress:end -->"
BAR_WIDTH = 10
HOLIDAYS = "Праздничные события"
HOLIDAY_ZONES = {-22, -41, -364, -366, -369, -370, -373, -374, -375, -376, -1002, -1003, -1005}
GOSSIP_TITLE = "Реплики NPC вне квестов"

parser = argparse.ArgumentParser()
parser.add_argument("quests")
parser.add_argument("module_dir")
parser.add_argument("readme")
parser.add_argument("horde", nargs="?")
parser.add_argument("--gossip")
parser.add_argument("--redo")
parser.add_argument("--note")
args = parser.parse_args()

lengths_path = os.path.join(args.module_dir, "generated", "sound_length_table.lua")
done = set(re.findall(r'\["([^"]+)"\] =', open(lengths_path, encoding="utf-8").read())) if os.path.exists(lengths_path) else set()
if args.redo:
    done &= set(json.load(open(args.redo, encoding="utf-8"))) if os.path.exists(args.redo) else set()


def level_band(level):
    low = (min(max(level, 1), 80) - 1) // 10 * 10 + 1
    return f"Уровни {low}–{low + 9}"


def quest_items(path):
    for quest in json.load(open(path, encoding="utf-8"))["selected"]:
        band = HOLIDAYS if quest["zone"] in HOLIDAY_ZONES else level_band(quest["level"])
        yield band, [f"{quest['id']}-{event}" for event in ("accept", "complete") if quest[event]]


def gossip_items(path):
    for line in json.load(open(path, encoding="utf-8"))["lines"]:
        yield level_band(line["level"]), [line["hash"]]


def bar(fraction):
    filled = round(fraction * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def status(fraction):
    if fraction >= 1:
        return "✅ готово"
    if fraction > 0:
        return "🔄 в работе"
    return "⏳ в очереди"


def band_order(name):
    return (name == HOLIDAYS, int(re.search(r"\d+", name).group()) if "Уровни" in name else 0)


def progress_rows(title, items):
    bands = {}
    for band_name, names in items:
        band = bands.setdefault(band_name, {"items": 0, "items_done": 0, "files": 0, "files_done": 0})
        finished = sum(name in done for name in names)
        band["items"] += 1
        band["items_done"] += finished == len(names)
        band["files"] += len(names)
        band["files_done"] += finished

    rows = [f"| {title} | Готово | Прогресс | Статус |", "|---|---|---|---|"]
    total = {"items": 0, "items_done": 0, "files": 0, "files_done": 0}
    for name in sorted(bands, key=band_order):
        band = bands[name]
        fraction = band["files_done"] / band["files"]
        rows.append(f"| {name} | {band['items_done']} / {band['items']} | `{bar(fraction)}` {fraction:.0%} | {status(fraction)} |")
        for key in total:
            total[key] += band[key]
    fraction = total["files_done"] / total["files"]
    rows.append(f"| **Всего** | **{total['items_done']} / {total['items']}** | `{bar(fraction)}` **{fraction:.0%}** | |")
    print(f"{title}: {total['items_done']}/{total['items']} items, {total['files_done']}/{total['files']} files")
    return rows


not_started = ["Тексты для женских персонажей"]
rows = progress_rows("Квесты Альянса и нейтральные", quest_items(args.quests))
if args.horde:
    rows += [""] + progress_rows("Квесты Орды", quest_items(args.horde))
else:
    not_started.insert(0, "Квесты Орды")
if args.gossip:
    rows += [""] + progress_rows(GOSSIP_TITLE, gossip_items(args.gossip))
else:
    not_started.insert(0, GOSSIP_TITLE)
rows += ["", "| Ещё не озвучено | Статус |", "|---|---|"]
for name in not_started:
    rows.append(f"| {name} | ❌ не начато |")

updated = datetime.date.today().strftime("%d.%m.%Y")
header = [f"_Обновлено {updated}._"] + ([args.note] if args.note else [])
section = "\n".join([START, "\n\n".join(header), "", *rows, END])

readme = open(args.readme, encoding="utf-8").read()
if START not in readme or END not in readme:
    sys.exit(f"markers {START} / {END} not found in {args.readme}")
readme = readme[:readme.index(START)] + section + readme[readme.index(END) + len(END):]
with open(args.readme, "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
