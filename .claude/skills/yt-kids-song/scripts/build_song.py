#!/usr/bin/env python3
"""Bundle a song folder for rendering.
usage: build_song.py <song-dir> "<Title>" <bpm> <first-beat-s> [host=code|photo] [character-dir]
Writes data.js (window.SONG) and copies kids-engine.html -> video.html, tamara.js and fonts/.
The folder must already have words.json (align_lyrics.py), song.mp3 and visuals.js."""
import json, os, shutil, subprocess, sys
d, title, bpm, beat0 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
host = sys.argv[5] if len(sys.argv) > 5 else "code"  # photo = animate the reference picture (needs make_photo_puppet.py output)
T = os.path.join(os.path.dirname(__file__), "..", "templates")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(d, "song.mp3")]))
lines = json.load(open(os.path.join(d, "words.json")))["lines"]
open(os.path.join(d, "data.js"), "w").write("window.SONG=" + json.dumps({"title": title, "bpm": bpm, "beat0": beat0, "duration": dur, "host": host, "lines": lines}) + ";\n")
shutil.copy(os.path.join(T, "kids-engine.html"), os.path.join(d, "video.html"))
for f in ("tamara.js", "tamara-photo.js"):
    shutil.copy(os.path.join(T, f), os.path.join(d, f))
shutil.copytree(os.path.join(T, "fonts"), os.path.join(d, "fonts"), dirs_exist_ok=True)
if host == "photo":  # embed the pose cutouts + landmarks (WebGL can't load file:// images)
    import base64
    cdir = sys.argv[6] if len(sys.argv) > 6 else os.path.join(d, "..", "characters", "tamara")
    poses = {k: v for k, v in json.load(open(os.path.join(cdir, "poses.json"))).items() if not k.startswith("_")}
    for name, v in poses.items():
        v["src"] = "data:image/png;base64," + base64.b64encode(open(os.path.join(cdir, f"{name}-cutout.png"), "rb").read()).decode()
        dp = os.path.join(cdir, f"{name}-depth.png")  # from make_depth.py: 3D turns
        if os.path.exists(dp):
            v["depth"] = "data:image/png;base64," + base64.b64encode(open(dp, "rb").read()).decode()
    open(os.path.join(d, "tamara-cutout.js"), "w").write("window.TAMARA_POSES=" + json.dumps(poses) + ";\n")
print(f"built {d}: {dur:.1f}s, {len(lines)} lines")
