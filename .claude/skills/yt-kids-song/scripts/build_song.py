#!/usr/bin/env python3
"""Bundle a song folder for rendering.
usage: build_song.py <song-dir> "<Title>" <bpm> <first-beat-s>
Writes data.js (window.SONG) and copies kids-engine.html -> video.html, tamara.js and fonts/.
The folder must already have words.json (align_lyrics.py), song.mp3 and visuals.js."""
import json, os, shutil, subprocess, sys
d, title, bpm, beat0 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
T = os.path.join(os.path.dirname(__file__), "..", "templates")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(d, "song.mp3")]))
lines = json.load(open(os.path.join(d, "words.json")))["lines"]
open(os.path.join(d, "data.js"), "w").write("window.SONG=" + json.dumps({"title": title, "bpm": bpm, "beat0": beat0, "duration": dur, "lines": lines}) + ";\n")
shutil.copy(os.path.join(T, "kids-engine.html"), os.path.join(d, "video.html"))
shutil.copy(os.path.join(T, "tamara.js"), os.path.join(d, "tamara.js"))
shutil.copytree(os.path.join(T, "fonts"), os.path.join(d, "fonts"), dirs_exist_ok=True)
print(f"built {d}: {dur:.1f}s, {len(lines)} lines")
