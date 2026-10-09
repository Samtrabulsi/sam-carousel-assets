#!/usr/bin/env python3
"""Bundle script.json + timeline.json + episode.json (+ cues.json) into data.js for the engine.
  python3 build_data.py <episode-dir>"""
import json, os, sys
ep = sys.argv[1]
j = lambda f: json.load(open(os.path.join(ep, f)))
out = ["const BEATS=" + json.dumps(j("script.json"), ensure_ascii=False) + ";",
       "const TL=" + json.dumps(j("timeline.json")) + ";",
       "window.EPISODE=" + json.dumps(j("episode.json") if os.path.exists(os.path.join(ep, "episode.json")) else {}, ensure_ascii=False) + ";"]
if os.path.exists(os.path.join(ep, "cues.json")):
    out.append("window.CUES=" + json.dumps(j("cues.json")["mouthCues"]) + ";")
open(os.path.join(ep, "data.js"), "w").write("\n".join(out) + "\n")
print("data.js written")
