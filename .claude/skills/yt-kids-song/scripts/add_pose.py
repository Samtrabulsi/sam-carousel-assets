#!/usr/bin/env python3
"""Add a pose picture to a photo-puppet character (cutout + depth map + landmarks in poses.json).
usage (rembg venv python): add_pose.py <character-dir> <name> <picture> [--no-rembg]
- picture with a transparent background is used as is; otherwise rembg removes the background
- landmarks are estimated from the silhouette (feet = bottom centre, neck ~28% down, chest below it); no eyes/mouth
  (blinks and lip movement need hand-measured landmarks, see SKILL.md). Edit poses.json to refine.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
cdir, name, pic = sys.argv[1:4]
im = Image.open(pic).convert("RGBA")
if np.asarray(im)[..., 3].min() == 255:  # opaque picture: cut out the background
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, "a.png"); b = os.path.join(tmp, "b.png"); im.convert("RGB").save(a)
    subprocess.run([os.path.expanduser("~/.cache/yt-tools/rembg/bin/rembg"), "i", "-m", "isnet-general-use", a, b], check=True, capture_output=True)
    im = Image.open(b).convert("RGBA")
arr = np.array(im).astype(float); al = arr[..., 3] / 255
edge = (al < 0.98) & (al > 0) & (arr[..., :3].mean(-1) > 150)
arr[edge, :3] *= 0.45
arr[..., 3] = np.clip((al - 0.3) / 0.7, 0, 1) * 255
out = Image.fromarray(arr.astype("uint8")); out.save(os.path.join(cdir, f"{name}-cutout.png"))
m = arr[..., 3] > 128; ys, xs = np.where(m); top, bot = ys.min(), ys.max(); hgt = bot - top
fx = float(xs[ys > bot - 50].mean())
ny = top + 0.285 * hgt; band = (ys > top + 0.12 * hgt) & (ys < top + 0.24 * hgt); nx = float(xs[band].mean())
lm = {"feet": [round(fx), int(bot)], "neck": [round(nx), round(ny)], "chest": [round(nx), round(ny + 0.13 * hgt)], "split": None, "eyes": None, "auto": True}
pj = os.path.join(cdir, "poses.json"); P = json.load(open(pj))
if name not in P or P[name].get("auto"):
    P[name] = lm; json.dump(P, open(pj, "w"), indent=1)
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "make_depth.py"), os.path.join(cdir, f"{name}-cutout.png"), os.path.join(cdir, f"{name}-depth.png")], check=True, capture_output=True)
print(name, P[name])
