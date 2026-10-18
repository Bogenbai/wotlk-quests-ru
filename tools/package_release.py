import argparse
import json
import os
import zipfile

MODULE_NAME = "AI_VoiceOverData_Russian"

parser = argparse.ArgumentParser()
parser.add_argument("repo_dir")
parser.add_argument("module_dir")
parser.add_argument("out_dir")
parser.add_argument("--horde")
args = parser.parse_args()

os.makedirs(args.out_dir, exist_ok=True)
license_path = os.path.join(args.repo_dir, "LICENSES", "CPML-1.0.txt")
horde_files = set()
if args.horde:
    for quest in json.load(open(args.horde, encoding="utf-8"))["selected"]:
        horde_files.update(f"{quest['id']}-{event}.ogg" for event in ("accept", "complete") if quest[event])


def module_files(source):
    for root, _, files in os.walk(source):
        for name in sorted(files):
            if not name.endswith((".tmp", ".tmp.ogg")):
                yield os.path.join(root, name)


def is_horde(path):
    return os.path.basename(os.path.dirname(path)) == "quests" and os.path.basename(path) in horde_files


def write_zip(path, files, compression, prefix, source, extra=()):
    count = 0
    with zipfile.ZipFile(path, "w", compression) as archive:
        for file in files:
            archive.write(file, os.path.join(prefix, os.path.relpath(file, source)))
            count += 1
        for file, name in extra:
            archive.write(file, os.path.join(prefix, name))
    print(f"{path}: {count} files, {os.path.getsize(path) / 2**20:.0f} MB")


files = list(module_files(args.module_dir))
license_entry = [(license_path, "LICENSE-CPML.txt")]
write_zip(os.path.join(args.out_dir, MODULE_NAME + ".zip"), [f for f in files if not is_horde(f)],
          zipfile.ZIP_STORED, MODULE_NAME, args.module_dir, license_entry)
if horde_files:
    write_zip(os.path.join(args.out_dir, MODULE_NAME + "-Horde.zip"), [f for f in files if is_horde(f)],
              zipfile.ZIP_STORED, MODULE_NAME, args.module_dir, license_entry)

addon_dir = os.path.join(args.repo_dir, "addon", "AI_VoiceOver")
write_zip(os.path.join(args.out_dir, "AI_VoiceOver-ruRU-fix.zip"), list(module_files(addon_dir)),
          zipfile.ZIP_DEFLATED, "AI_VoiceOver", addon_dir)
