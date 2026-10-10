#!/usr/bin/env python3
"""thumbnail.json -> 1280x720 JPG via the HTML template (Playwright/Chromium).
  python3 thumb.py thumbnail.json out.jpg
Paths in "face"/"bg" are relative to the JSON file. Keep text to 3-5 words a line; check it at phone size."""
import json, os, subprocess, sys, tempfile
cfg_path, out = sys.argv[1], os.path.abspath(sys.argv[2])
T = json.load(open(cfg_path)); base = os.path.dirname(os.path.abspath(cfg_path))
for k in ("face", "bg"):
    if T.get(k) and not T[k].startswith(("http", "file:")):
        T[k] = "file://" + os.path.join(base, T[k])
tpl = open(os.path.join(os.path.dirname(__file__), "..", "templates", "thumb.html")).read()
html = tpl.replace("<body><script>", "<body><script>window.T=" + json.dumps(T, ensure_ascii=False) + ";</script><script>", 1)
tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=base); tmp.write(html); tmp.close()
js = """const path=require('path');const {chromium}=require(path.join(require('child_process').execSync('npm root -g').toString().trim(),'playwright'));
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto('file://'+process.argv[1],{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
await p.screenshot({path:process.argv[2],type:'jpeg',quality:92});await b.close();})();"""
try:
    subprocess.run(["node", "-e", js, tmp.name, out], check=True)
    # also save a phone-size preview: thumbnails are judged at ~320px wide
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "scale=320:-1", out.replace(".jpg", "-small.jpg")], check=True)
    print("wrote", out)
finally:
    os.remove(tmp.name)
