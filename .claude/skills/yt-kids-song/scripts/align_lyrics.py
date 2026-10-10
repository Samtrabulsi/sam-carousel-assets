#!/usr/bin/env python3
"""Time every lyric word against the sung audio.

usage: align_lyrics.py <song.mp3|vocals.wav> <lyrics.md> <words.json>

Runs faster-whisper (small.en) with word timestamps, then matches the recognised
words to the known lyrics (difflib), and interpolates times for words whisper
missed. Output: {"lines":[{"section","text","start","end","words":[{"w","start","end"}]}]}
Needs the venv from yt-kids-song SKILL.md (~/.cache/yt-tools/whisper).
"""
import json, re, sys, difflib, subprocess
import numpy as np
from faster_whisper import WhisperModel

audio, lyr_path, out = sys.argv[1:4]
txt = open(lyr_path).read()
m = re.search(r"```\n(.*?)```", txt, re.S)
txt = m.group(1) if m else txt

lines, section = [], ""
for raw in txt.splitlines():
    raw = raw.strip()
    if not raw:
        continue
    if raw.startswith("["):
        section = raw.strip("[]"); continue
    lines.append({"section": section, "text": raw, "words": [{"w": w} for w in raw.split()]})

norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
flat = [(li, wi, norm(w["w"])) for li, l in enumerate(lines) for wi, w in enumerate(l["words"])]

model = WhisperModel("small.en", device="cpu", compute_type="int8")
prompt = " ".join(l["text"] for l in lines)[:800]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
wav = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768  # decode with ffmpeg (avoids PyAV version issues)
segs, _ = model.transcribe(wav, word_timestamps=True, initial_prompt=prompt, vad_filter=False, beam_size=5)
rec = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
print(f"recognised {len(rec)} words, lyrics {len(flat)} words", file=sys.stderr)

sm = difflib.SequenceMatcher(a=[f[2] for f in flat], b=[r[0] for r in rec], autojunk=False)
times = [None] * len(flat)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        times[a + k] = (rec[b + k][1], rec[b + k][2])
matched = sum(t is not None for t in times)
print(f"matched {matched}/{len(flat)}", file=sys.stderr)

# interpolate gaps between known neighbours
known = [i for i, t in enumerate(times) if t]
for i in range(len(times)):
    if times[i]:
        continue
    prev = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
    if prev is None and nxt is None:
        continue
    if prev is None:
        s = times[nxt][0] - 0.4 * (nxt - i); times[i] = (s, s + 0.35); continue
    if nxt is None:
        s = times[prev][1] + 0.4 * (i - prev); times[i] = (s, s + 0.35); continue
    span = times[nxt][0] - times[prev][1]; step = span / (nxt - prev)
    s = times[prev][1] + step * (i - prev - 1) + 0.02; times[i] = (s, s + max(0.12, step * 0.9))

for (li, wi, _), t in zip(flat, times):
    lines[li]["words"][wi].update(start=round(t[0], 2), end=round(t[1], 2))
for l in lines:
    l["start"] = l["words"][0]["start"]; l["end"] = l["words"][-1]["end"]
json.dump({"matched": matched, "total": len(flat), "lines": lines,
           "heard": [[w, round(a, 2), round(b, 2)] for w, a, b in rec]}, open(out, "w"), indent=1)
