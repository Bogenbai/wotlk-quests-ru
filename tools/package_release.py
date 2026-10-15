import os
import sys
import zipfile

repo_dir, module_dir, out_dir = sys.argv[1:4]
os.makedirs(out_dir, exist_ok=True)
license_path = os.path.join(repo_dir, "LICENSES", "CPML-1.0.txt")


def add_tree(archive, source, prefix):
    count = 0
    for root, _, files in os.walk(source):
        for name in sorted(files):
            if name.endswith((".tmp", ".tmp.ogg")):
                continue
            path = os.path.join(root, name)
            archive.write(path, os.path.join(prefix, os.path.relpath(path, source)))
            count += 1
    return count


voice_zip = os.path.join(out_dir, "AI_VoiceOverData_Russian.zip")
with zipfile.ZipFile(voice_zip, "w", zipfile.ZIP_STORED) as archive:
    files = add_tree(archive, module_dir, "AI_VoiceOverData_Russian")
    archive.write(license_path, os.path.join("AI_VoiceOverData_Russian", "LICENSE-CPML.txt"))
print(f"{voice_zip}: {files} files, {os.path.getsize(voice_zip) / 2**20:.0f} MB")

fix_zip = os.path.join(out_dir, "AI_VoiceOver-ruRU-fix.zip")
with zipfile.ZipFile(fix_zip, "w", zipfile.ZIP_DEFLATED) as archive:
    files = add_tree(archive, os.path.join(repo_dir, "addon", "AI_VoiceOver"), "AI_VoiceOver")
print(f"{fix_zip}: {files} files")
