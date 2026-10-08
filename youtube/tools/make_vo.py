import json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
S = sys.argv[1]; out = sys.argv[2]; voice = sys.argv[3]; speed = float(sys.argv[4])
k = Kokoro(f"{S}/kokoro/kokoro-v1.0.onnx", f"{S}/kokoro/voices-v1.0.bin")
beats = json.load(open(f"{out}/script.json"))
sr = 24000; parts = [np.zeros(int(0.4*sr), dtype=np.float32)]; t = 0.4; tl = []
for i, b in enumerate(beats):
    a, sr = k.create(b["say"], voice=voice, speed=speed, lang="en-us")
    a = a.astype(np.float32)
    tl.append({"start": round(t, 3), "dur": round(len(a)/sr, 3)})
    nxt = beats[i+1]["v"]["t"] if i+1 < len(beats) else None
    gap = 1.0 if nxt == "chapter" or b["v"]["t"] == "chapter" else 0.45
    parts += [a, np.zeros(int(gap*sr), dtype=np.float32)]; t += len(a)/sr + gap
    print(i, round(t,1), flush=True)
parts.append(np.zeros(int(1.5*sr), dtype=np.float32))
sf.write(f"{out}/voiceover.wav", np.concatenate(parts), sr)
json.dump({"total": round(t + 1.5, 2), "beats": tl}, open(f"{out}/timeline.json", "w"))
print("total", round(t+1.5,1))
