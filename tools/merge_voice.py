import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import luagen

source_module, source_progress, target_module, target_progress = sys.argv[1:5]


def load_lengths(progress_dir):
    path = os.path.join(progress_dir, "lengths.json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def sounds(module_dir):
    return os.path.join(module_dir, "generated", "sounds", "quests")


source = load_lengths(source_progress)
target = load_lengths(target_progress)
os.makedirs(sounds(target_module), exist_ok=True)

copied = 0
for name, length in source.items():
    clip = os.path.join(sounds(source_module), name + ".ogg")
    if name in target or not os.path.exists(clip):
        continue
    shutil.copy2(clip, os.path.join(sounds(target_module), name + ".ogg"))
    target[name] = length
    copied += 1

luagen.write_sound_lengths(target_module, target)
with open(os.path.join(target_progress, "lengths.json"), "w", encoding="utf-8") as f:
    json.dump(target, f)
print(f"copied {copied}, total {len(target)}")
