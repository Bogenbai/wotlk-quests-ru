import argparse
import json
import os
import sys
import time
import traceback

import numpy as np
import soundfile
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import luagen
import textprep

os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS

SAMPLE_RATE = 24000
PARAGRAPH_PAUSE = 0.6
CHUNK_CHARS = 180
TAIL_SILENCE = 0.4
MIN_REFERENCE_SECONDS = 6
SAVE_EVERY_SECONDS = 60
EVENTS = (("accept", "starters"), ("complete", "enders"))


def english_clip(wrath_sounds, quest_id, event):
    for prefix in ("", "m-"):
        path = os.path.join(wrath_sounds, f"{prefix}{quest_id}-{event}.ogg")
        if os.path.exists(path):
            return path
    return None


def clip_seconds(path):
    return soundfile.info(path).duration


def build_npc_references(quests, wrath_sounds):
    candidates = {}
    for quest in sorted(quests, key=lambda q: q["id"]):
        for event, npc_field in EVENTS:
            clip = english_clip(wrath_sounds, quest["id"], event)
            if not clip:
                continue
            for npc in quest[npc_field]:
                candidates.setdefault(npc["id"], []).append(clip)
    references = {}
    for npc_id, clips in candidates.items():
        long_enough = [c for c in clips if clip_seconds(c) >= MIN_REFERENCE_SECONDS]
        references[npc_id] = (long_enough or clips)[0]
    return references


def quest_reference(quest, event, npc_field, npc_references, wrath_sounds, defaults):
    npcs = quest[npc_field]
    clip = next((npc_references[n["id"]] for n in npcs if n["id"] in npc_references), None)
    clip = clip or english_clip(wrath_sounds, quest["id"], event)
    return clip or defaults.get(npcs[0]["gender"] if npcs else 0)


def gossip_reference(wrath_gossip, voice_hashes):
    clips = []
    for hash_ in voice_hashes:
        for prefix in ("", "m-"):
            path = os.path.join(wrath_gossip, f"{prefix}{hash_}.ogg")
            if os.path.exists(path):
                seconds = clip_seconds(path)
                if seconds >= MIN_REFERENCE_SECONDS:
                    return path
                clips.append((seconds, path))
                break
    return max(clips)[1] if clips else None


def default_references(quests, npc_references):
    defaults = {}
    for quest in quests:
        for _, npc_field in EVENTS:
            for npc in quest[npc_field]:
                if npc["id"] in npc_references:
                    defaults.setdefault(npc["gender"], npc_references[npc["id"]])
    defaults.setdefault(2, defaults.get(0))
    return defaults


class Voices:
    def __init__(self, model, cache_dir):
        self.model = model
        self.cache_dir = cache_dir
        self.latents = {}
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, clip):
        if clip not in self.latents:
            audio, sample_rate = soundfile.read(clip, dtype="float32")
            wav = os.path.join(self.cache_dir, os.path.basename(clip).replace(".ogg", ".wav"))
            soundfile.write(wav, audio, sample_rate)
            self.latents[clip] = self.model.get_conditioning_latents(audio_path=[wav])
        return self.latents[clip]


def resolve_device(requested):
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def synthesize(model, voice, text):
    gpt_cond_latent, speaker_embedding = voice
    pieces = []
    for paragraph in textprep.paragraphs(text):
        for chunk in textprep.chunks(paragraph, CHUNK_CHARS):
            out = model.inference(chunk, "ru", gpt_cond_latent, speaker_embedding)
            pieces.append(np.asarray(out["wav"], dtype=np.float32))
        pieces.append(np.zeros(int(SAMPLE_RATE * PARAGRAPH_PAUSE), dtype=np.float32))
    pieces[-1] = np.zeros(int(SAMPLE_RATE * TAIL_SILENCE), dtype=np.float32)
    return np.concatenate(pieces)


def write_ogg(path, audio):
    temp = path + ".tmp.ogg"
    with soundfile.SoundFile(temp, "w", SAMPLE_RATE, 1, format="OGG", subtype="VORBIS") as f:
        for start in range(0, len(audio), 4096):
            f.write(audio[start:start + 4096])
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("quests", nargs="+")
    parser.add_argument("wrath_sounds")
    parser.add_argument("module_dir")
    parser.add_argument("cache_dir")
    parser.add_argument("--gossip")
    parser.add_argument("--device", default="auto", choices=("auto", "cuda", "mps", "cpu"))
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    selections = [json.load(open(path, encoding="utf-8")) for path in args.quests]
    data = selections[0]
    selected = [quest for selection in selections for quest in selection["selected"]]
    gossip = json.load(open(args.gossip, encoding="utf-8")) if args.gossip else {"lines": [], "lookups": {"npc": {}, "object": {}}}
    luagen.write_static_files(args.module_dir, data["lookup"], gossip["lookups"])

    sounds_dirs = {kind: os.path.join(args.module_dir, "generated", "sounds", kind) for kind in ("quests", "gossip")}
    wrath_gossip = os.path.join(os.path.dirname(args.wrath_sounds), "gossip")
    progress_path = os.path.join(args.cache_dir, "lengths.json")
    lengths = json.load(open(progress_path, encoding="utf-8")) if os.path.exists(progress_path) else {}
    lengths = {name: length for name, length in lengths.items()
               if any(os.path.exists(os.path.join(d, name + ".ogg")) for d in sounds_dirs.values())}

    npc_references = build_npc_references(data["lookup"], args.wrath_sounds)
    defaults = default_references(data["lookup"], npc_references)

    jobs = []
    for quest in selected:
        for event, npc_field in EVENTS:
            name = f"{quest['id']}-{event}"
            if quest[event] and name not in lengths:
                clip = quest_reference(quest, event, npc_field, npc_references, args.wrath_sounds, defaults) or defaults[0]
                jobs.append({"name": name, "kind": "quests", "text": quest[event], "label": f"lvl {quest['level']}", "clip": clip})
    for line in gossip["lines"]:
        if line["hash"] not in lengths:
            clip = gossip_reference(wrath_gossip, line["voice_hashes"]) or defaults[0]
            jobs.append({"name": line["hash"], "kind": "gossip", "text": line["text"], "label": f"gossip lvl {line['level']}", "clip": clip})
    jobs = jobs[:args.limit]
    total_chars = sum(len(job["text"]) for job in jobs)
    print(f"done {len(lengths)}, remaining {len(jobs)} files, {total_chars} chars", flush=True)

    device = resolve_device(args.device)
    print(f"device {device}", flush=True)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    model = tts.synthesizer.tts_model
    voices = Voices(model, os.path.join(args.cache_dir, "references"))

    started = time.time()
    last_save = started
    done_chars = 0
    gpu_lost = False
    for index, job in enumerate(jobs, 1):
        name = job["name"]
        try:
            audio = synthesize(model, voices.get(job["clip"]), textprep.render(job["text"], "m"))
            write_ogg(os.path.join(sounds_dirs[job["kind"]], name + ".ogg"), audio)
            lengths[name] = round(len(audio) / SAMPLE_RATE, 2)
        except Exception as error:
            print(f"FAILED {name}", flush=True)
            traceback.print_exc()
            if "CUDA error" in str(error):
                gpu_lost = True
                break
            continue

        done_chars += len(job["text"])
        elapsed = time.time() - started
        eta_hours = (total_chars - done_chars) / (done_chars / elapsed) / 3600
        print(f"[{index}/{len(jobs)}] {job['label']} {name} {lengths[name]:.1f}s, eta {eta_hours:.1f}h", flush=True)

        if time.time() - last_save >= SAVE_EVERY_SECONDS or index == len(jobs):
            luagen.write_sound_lengths(args.module_dir, lengths)
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(lengths, f)
            last_save = time.time()

    luagen.write_sound_lengths(args.module_dir, lengths)
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(lengths, f)
    if gpu_lost:
        sys.exit("GPU lost, run start_voice.bat again")
    elapsed = time.time() - started
    print(f"finished in {elapsed / 60:.1f} min, {done_chars / elapsed:.1f} chars/s", flush=True)


if __name__ == "__main__":
    main()
