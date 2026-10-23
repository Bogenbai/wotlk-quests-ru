import argparse
import contextlib
import io
import json
import os
import re
import shutil
import sys
import time
import traceback
from difflib import SequenceMatcher

import imageio_ffmpeg
import numpy as np
import soundfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import luagen
import textprep

SAMPLE_RATE = 24000
PARAGRAPH_PAUSE = 0.6
TAIL_SILENCE = 0.4
REFERENCE_SECONDS = 10
REFERENCE_GAP = 0.3
SAVE_EVERY_SECONDS = 60
ATTEMPTS = 4
GOOD_MATCH = 0.85
EVENTS = (("accept", "starters"), ("complete", "enders"))
FALLBACK_VOICES = {0: "humanmalestandardnpc", 1: "humanfemalestandardnpc"}
F5_REPO = "Misha24-10/F5-TTS_RUSSIAN"
F5_CHECKPOINT = "F5TTS_v1_Base_v2/model_last_inference.safetensors"
F5_VOCAB = "F5TTS_v1_Base/vocab.txt"


def provide_ffmpeg(cache_dir):
    bin_dir = os.path.join(cache_dir, "bin")
    target = os.path.join(bin_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if not os.path.exists(target):
        os.makedirs(bin_dir, exist_ok=True)
        shutil.copyfile(imageio_ffmpeg.get_ffmpeg_exe(), target)
        os.chmod(target, 0o755)
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]


def words(text):
    return re.findall(r"\w+", text.lower().replace("ё", "е").replace("+", ""))


def similarity(heard, expected):
    heard, expected = words(heard), words(expected)
    return SequenceMatcher(None, heard, expected).ratio() if heard and expected else 0


def voice_key(npc_ids, ru_voices):
    return next((ru_voices["npc"][str(n)] for n in npc_ids if str(n) in ru_voices["npc"]), None)


def quest_voice(quest, npc_field, ru_voices):
    npcs = quest[npc_field]
    gender = npcs[0]["gender"] if npcs else 0
    return voice_key([n["id"] for n in npcs], ru_voices) or FALLBACK_VOICES.get(gender, FALLBACK_VOICES[0])


def speech_segments(audio):
    window = int(SAMPLE_RATE * 0.25)
    quiet = np.convolve(np.abs(audio) < 0.005, np.ones(window), "same") >= window - 1
    segments, start = [], None
    for index, silent in enumerate(quiet):
        if not silent and start is None:
            start = index
        elif silent and start is not None:
            segments.append(audio[start:index])
            start = None
    if start is not None:
        segments.append(audio[start:])
    return [s for s in segments if len(s) > SAMPLE_RATE * 0.5]


class Speaker:
    def __init__(self, device, cache_dir):
        from f5_tts.api import F5TTS
        from f5_tts.infer.utils_infer import transcribe
        from huggingface_hub import hf_hub_download
        from ruaccent import RUAccent

        self.accent = RUAccent()
        self.accent.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
        self.f5 = F5TTS(model="F5TTS_v1_Base", ckpt_file=hf_hub_download(F5_REPO, F5_CHECKPOINT),
                        vocab_file=hf_hub_download(F5_REPO, F5_VOCAB), device=device)
        self.transcribe_fn = transcribe
        self.refs_dir = os.path.join(cache_dir, "f5_refs")
        os.makedirs(self.refs_dir, exist_ok=True)
        self.references = {}

    def transcribe(self, audio):
        return self.transcribe_fn({"raw": audio.astype(np.float32), "sampling_rate": SAMPLE_RATE}, "ru").strip()

    def reference(self, key, source):
        if key in self.references:
            return self.references[key]
        wav = os.path.join(self.refs_dir, key + ".wav")
        txt = os.path.join(self.refs_dir, key + ".txt")
        if not os.path.exists(txt):
            audio, _ = soundfile.read(source, dtype="float32")
            chosen, said_all, total = [], [], 0
            gap = np.zeros(int(SAMPLE_RATE * REFERENCE_GAP), dtype=np.float32)
            for segment in speech_segments(audio):
                if total + len(segment) > SAMPLE_RATE * REFERENCE_SECONDS:
                    continue
                said = self.transcribe(segment)
                if not words(said) or re.search(r"(\w)\1{3,}", said):
                    continue
                chosen += [segment, gap]
                said_all.append(said)
                total += len(segment) + len(gap)
            if not chosen:
                clip = audio[:SAMPLE_RATE * REFERENCE_SECONDS]
                chosen, said_all = [clip], [self.transcribe(clip)]
            soundfile.write(wav, np.concatenate(chosen), SAMPLE_RATE)
            with open(txt, "w", encoding="utf-8") as f:
                f.write(" ".join(said_all))
        self.references[key] = (wav, open(txt, encoding="utf-8").read())
        return self.references[key]

    def paragraph(self, reference, text):
        ref_wav, ref_text = reference
        stressed = self.accent.process_all(text)
        best = None
        for seed in range(ATTEMPTS):
            with contextlib.redirect_stdout(io.StringIO()):
                wav, _, _ = self.f5.infer(ref_wav, ref_text, stressed, seed=seed, show_info=lambda *a: None, progress=None)
            wav = np.asarray(wav, dtype=np.float32)
            score = similarity(self.transcribe(wav), text)
            if best is None or score > best[0]:
                best = (score, wav)
            if score >= GOOD_MATCH:
                break
        return best

    def synthesize(self, reference, text):
        pieces, scores = [], []
        for paragraph in textprep.paragraphs(text):
            score, wav = self.paragraph(reference, paragraph)
            scores.append(score)
            pieces += [wav, np.zeros(int(SAMPLE_RATE * PARAGRAPH_PAUSE), dtype=np.float32)]
        pieces[-1] = np.zeros(int(SAMPLE_RATE * TAIL_SILENCE), dtype=np.float32)
        return np.concatenate(pieces), min(scores)


def write_ogg(path, audio):
    temp = path + ".tmp.ogg"
    with soundfile.SoundFile(temp, "w", SAMPLE_RATE, 1, format="OGG", subtype="VORBIS") as f:
        for start in range(0, len(audio), 4096):
            f.write(audio[start:start + 4096])
    os.replace(temp, path)


def save_progress(module_dir, progress_path, lengths, redo_path, redone):
    luagen.write_sound_lengths(module_dir, lengths)
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(lengths, f)
    if redo_path:
        with open(redo_path, "w", encoding="utf-8") as f:
            json.dump(sorted(redone), f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("quests", nargs="+")
    parser.add_argument("module_dir")
    parser.add_argument("cache_dir")
    parser.add_argument("--ru-voices", required=True)
    parser.add_argument("--gossip")
    parser.add_argument("--redo")
    parser.add_argument("--catquest")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    selections = [json.load(open(path, encoding="utf-8")) for path in args.quests]
    data = selections[0]
    selected = [quest for selection in selections for quest in selection["selected"]]
    gossip = json.load(open(args.gossip, encoding="utf-8")) if args.gossip else {"lines": [], "lookups": {"npc": {}, "object": {}}}
    ru_voices = json.load(open(args.ru_voices, encoding="utf-8"))
    luagen.write_static_files(args.module_dir, data["lookup"], gossip["lookups"])

    sounds_dirs = {kind: os.path.join(args.module_dir, "generated", "sounds", kind) for kind in ("quests", "gossip")}
    progress_path = os.path.join(args.cache_dir, "lengths.json")
    lengths = json.load(open(progress_path, encoding="utf-8")) if os.path.exists(progress_path) else {}
    lengths = {name: length for name, length in lengths.items()
               if any(os.path.exists(os.path.join(d, name + ".ogg")) for d in sounds_dirs.values())}
    redone = set(json.load(open(args.redo, encoding="utf-8"))) if args.redo and os.path.exists(args.redo) else set()

    def pending(name):
        return name not in redone if args.redo else name not in lengths

    jobs = []
    for quest in selected:
        for event, npc_field in EVENTS:
            name = f"{quest['id']}-{event}"
            if quest[event] and pending(name):
                jobs.append({"name": name, "kind": "quests", "text": quest[event], "label": f"lvl {quest['level']}",
                             "voice": quest_voice(quest, npc_field, ru_voices)})
    for line in gossip["lines"]:
        if pending(line["hash"]):
            jobs.append({"name": line["hash"], "kind": "gossip", "text": line["text"], "label": f"gossip lvl {line['level']}",
                         "voice": voice_key(line["npcs"], ru_voices) or FALLBACK_VOICES[0]})
    if args.catquest:
        catquest_sounds = os.path.join(args.catquest, "generated", "sounds", "quests")
        covered = {n.removeprefix("m-").removeprefix("f-").removesuffix(".ogg") for n in os.listdir(catquest_sounds)}
        jobs.sort(key=lambda job: job["kind"] == "quests" and job["name"] in covered)
    jobs = jobs[:args.limit]
    total_chars = sum(len(job["text"]) for job in jobs)
    print(f"done {len(lengths)}, remaining {len(jobs)} files, {total_chars} chars", flush=True)

    provide_ffmpeg(args.cache_dir)
    speaker = Speaker(args.device, args.cache_dir)
    print(f"device {args.device}", flush=True)

    started = time.time()
    last_save = started
    done_chars = 0
    gpu_lost = False
    for index, job in enumerate(jobs, 1):
        name = job["name"]
        try:
            reference = speaker.reference(job["voice"], ru_voices["voices"][job["voice"]])
            audio, score = speaker.synthesize(reference, textprep.render(job["text"], "m"))
            write_ogg(os.path.join(sounds_dirs[job["kind"]], name + ".ogg"), audio)
            lengths[name] = round(len(audio) / SAMPLE_RATE, 2)
            redone.add(name)
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
        print(f"[{index}/{len(jobs)}] {job['label']} {name} {lengths[name]:.1f}s match {score:.2f}, eta {eta_hours:.1f}h", flush=True)

        if time.time() - last_save >= SAVE_EVERY_SECONDS or index == len(jobs):
            save_progress(args.module_dir, progress_path, lengths, args.redo, redone)
            last_save = time.time()

    save_progress(args.module_dir, progress_path, lengths, args.redo, redone)
    if gpu_lost:
        sys.exit("GPU lost, run start_voice.bat again")
    elapsed = time.time() - started
    print(f"finished in {elapsed / 60:.1f} min, {done_chars / elapsed:.1f} chars/s", flush=True)


if __name__ == "__main__":
    main()
