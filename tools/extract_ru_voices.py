import argparse
import io
import json
import os
import struct
import subprocess
import sys
from collections import defaultdict

import imageio_ffmpeg
import pympq
import numpy as np
import soundfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqldump

LOCALE_ARCHIVES = ["patch-ruRU-D.MPQ", "patch-ruRU-3.MPQ", "patch-ruRU-2.MPQ", "patch-ruRU.MPQ", "lichking-speech-ruRU.MPQ",
                   "expansion-speech-ruRU.MPQ", "speech-ruRU.MPQ", "locale-ruRU.MPQ"]
SAMPLE_RATE = 24000
GAP_SECONDS = 0.3
MAX_REFERENCE_SECONDS = 25
MIN_UNIQUE_SECONDS = 8
DISPLAY_NPC_SOUND_FIELD = 12


class LocaleFiles:
    def __init__(self, locale_dir, temp_dir):
        self.archives = [pympq.open_archive(os.path.join(locale_dir, name), [pympq.MPQ_OPEN_READ_ONLY])
                         for name in LOCALE_ARCHIVES if os.path.exists(os.path.join(locale_dir, name))]
        os.makedirs(temp_dir, exist_ok=True)
        self.temp = os.path.join(temp_dir, "extracted.bin")

    def read(self, path):
        for archive in self.archives:
            if archive.has_file(path):
                archive.extract_file(path, self.temp)
                with open(self.temp, "rb") as f:
                    return f.read()
        return None


def read_dbc(data):
    magic, records, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
    assert magic == b"WDBC"
    body = data[20:20 + records * record_size]
    strings = data[20 + records * record_size:]
    rows = [struct.unpack_from(f"<{fields}I", body, i * record_size) for i in range(records)]

    def string(offset):
        return strings[offset:strings.index(b"\0", offset)].decode("utf-8")

    return rows, string


def sound_entries(files):
    rows, string = read_dbc(files.read("DBFilesClient\\SoundEntries.dbc"))
    entries = {}
    for row in rows:
        directory = string(row[23])
        entries[row[0]] = [f"{directory}\\{string(o)}" for o in row[3:13] if o and string(o)]
    return entries


def npc_sound_entries(files):
    rows, _ = read_dbc(files.read("DBFilesClient\\NPCSounds.dbc"))
    npc_sounds = {row[0]: [s for s in row[1:4] if s] for row in rows}
    rows, _ = read_dbc(files.read("DBFilesClient\\CreatureDisplayInfo.dbc"))
    return {row[0]: npc_sounds.get(row[DISPLAY_NPC_SOUND_FIELD], []) for row in rows}


def decode(data):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run([ffmpeg, "-v", "quiet", "-i", "pipe:0", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "wav", "pipe:1"],
                            input=data, capture_output=True)
    if result.returncode or not result.stdout:
        return None
    audio, _ = soundfile.read(io.BytesIO(result.stdout), dtype="float32")
    return audio if len(audio) > SAMPLE_RATE * 0.4 else None


def trim(audio, threshold=0.01):
    if audio is None:
        return None
    loud = np.flatnonzero(np.abs(audio) > threshold)
    return audio[loud[0]:loud[-1] + 1] if len(loud) else audio


def voice_key(paths):
    return paths[0].rsplit("\\", 1)[0].lower().replace("sound\\creature\\", "").replace("\\", "_")


def catquest_clips(module_dir, quests_path):
    sounds = os.path.join(module_dir, "generated", "sounds", "quests")
    clips = defaultdict(list)
    for quest in json.load(open(quests_path, encoding="utf-8"))["lookup"]:
        for event, field in (("accept", "starters"), ("complete", "enders")):
            if len(quest[field]) != 1:
                continue
            for prefix in ("", "m-"):
                path = os.path.join(sounds, f"{prefix}{quest['id']}-{event}.ogg")
                if os.path.exists(path):
                    clips[quest[field][0]["id"]].append(os.path.abspath(path))
                    break
    return clips


def wanted_npcs(quest_lists, gossip_path):
    npcs = set()
    for path in quest_lists:
        for quest in json.load(open(path, encoding="utf-8"))["selected"]:
            npcs.update(n["id"] for field in ("starters", "enders") for n in quest[field])
    if gossip_path:
        for line in json.load(open(gossip_path, encoding="utf-8"))["lines"]:
            npcs.update(line["npcs"])
    return npcs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game_dir")
    parser.add_argument("sql_dir")
    parser.add_argument("out_dir")
    parser.add_argument("out_json")
    parser.add_argument("quests", nargs="+")
    parser.add_argument("--gossip")
    parser.add_argument("--catquest")
    args = parser.parse_args()

    files = LocaleFiles(os.path.join(args.game_dir, "Data", "ruRU"), args.out_dir)
    entries = sound_entries(files)
    display_sounds = npc_sound_entries(files)

    displays = defaultdict(list)
    for row in sqldump.load(os.path.join(args.sql_dir, "creature_template_model.sql")):
        displays[int(row["CreatureID"])].append(int(row["CreatureDisplayID"]))
    spoken = defaultdict(set)
    for row in sqldump.load(os.path.join(args.sql_dir, "creature_text.sql")):
        if row["Sound"] and int(row["Sound"]):
            spoken[int(row["CreatureID"])].add(int(row["Sound"]))

    catquest = catquest_clips(args.catquest, args.quests[0]) if args.catquest else {}
    clips = {}

    def load_clips(paths):
        loaded = []
        for path in paths:
            if path not in clips:
                data = open(path, "rb").read() if os.path.isabs(path) else files.read(path)
                clips[path] = trim(decode(data)) if data else None
            if clips[path] is not None:
                loaded.append(clips[path])
        return loaded

    voices = {}
    npc_voices = {}
    stats = defaultdict(int)
    for npc in sorted(wanted_npcs(args.quests, args.gossip)):
        unique = [p for s in sorted(spoken.get(npc, ())) for p in entries.get(s, [])]
        if npc in catquest:
            key, paths, kind = f"catquest_{npc}", catquest[npc], "catquest"
        elif sum(len(c) for c in load_clips(unique)) >= MIN_UNIQUE_SECONDS * SAMPLE_RATE:
            key, paths, kind = voice_key(unique), unique, "unique"
        else:
            paths = next(([p for s in display_sounds.get(d, []) for p in entries.get(s, [])]
                          for d in displays.get(npc, []) if display_sounds.get(d)), [])
            if not load_clips(paths):
                stats["none"] += 1
                continue
            key, kind = voice_key(paths), "generic"
        stats[kind] += 1
        npc_voices[npc] = key
        if key not in voices:
            voices[key] = paths

    os.makedirs(args.out_dir, exist_ok=True)
    references = {}
    gap = np.zeros(int(SAMPLE_RATE * GAP_SECONDS), dtype=np.float32)
    for key, paths in sorted(voices.items()):
        chosen, total = [], 0
        for clip in sorted(load_clips(paths), key=len, reverse=True):
            if total >= MAX_REFERENCE_SECONDS * SAMPLE_RATE:
                break
            chosen += [clip, gap]
            total += len(clip) + len(gap)
        audio = np.concatenate(chosen)
        audio = audio / max(np.abs(audio).max(), 1e-6) * 0.9
        path = os.path.join(args.out_dir, key + ".wav")
        soundfile.write(path, audio, SAMPLE_RATE)
        references[key] = path

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump({"npc": npc_voices, "voices": references}, f, ensure_ascii=False, indent=1)
    print(dict(stats), "voices", len(references))


if __name__ == "__main__":
    main()
