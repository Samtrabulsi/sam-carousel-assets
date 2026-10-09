#!/usr/bin/env python3
"""Turn a character picture (plain background) into photo-puppet layers for tamara-photo.js.

usage: make_photo_puppet.py <picture> <out-dir> --head CX,CY,RX,RY --jaw x1,y1,x2,y2,...
  writes tamara-cutout.png (background removed, halo cleaned), tamara-headmask.png, tamara-jawmask.png
  --head: ellipse around face + crown (image pixels); --jaw: polygon around lower teeth, lower lip and chin,
          whose top edge is the line between the upper and lower teeth.
Needs rembg (one-time): python3 -m venv ~/.cache/yt-tools/rembg && ~/.cache/yt-tools/rembg/bin/pip install "rembg[cpu,cli]"
Find landmarks by viewing a gridded crop of the face, then put them in TAMARA_PHOTO (feet, neck, split, eyes).
Tamara's values are the defaults in templates/tamara-photo.js.
"""
import argparse, os, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ap = argparse.ArgumentParser(); ap.add_argument("picture"); ap.add_argument("out")
ap.add_argument("--head", default="490,275,185,195"); ap.add_argument("--jaw", default="422,358,450,362,484,364,518,362,546,356,560,380,545,415,505,440,470,444,432,425,412,392")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
tmp = tempfile.mkdtemp(); png = os.path.join(tmp, "in.png"); cut = os.path.join(tmp, "cut.png")
Image.open(a.picture).convert("RGB").save(png)
subprocess.run([os.path.expanduser("~/.cache/yt-tools/rembg/bin/rembg"), "i", "-m", "isnet-general-use", png, cut], check=True)
arr = np.array(Image.open(cut).convert("RGBA")).astype(float); al = arr[..., 3] / 255
edge = (al < 0.98) & (al > 0) & (arr[..., :3].mean(-1) > 120)
arr[edge, :3] *= 0.35                       # darken the light background fringe on hair
arr[..., 3] = np.clip((al - 0.3) / 0.7, 0, 1) * 255  # tighter edge, no faint halo ring
img = Image.fromarray(arr.astype("uint8")); img.save(os.path.join(a.out, "tamara-cutout.png"))

def save_mask(draw_fn, blur, name):
    m = Image.new("L", img.size, 0); draw_fn(ImageDraw.Draw(m)); m = m.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", img.size, (255, 255, 255, 0)); out.putalpha(m); out.save(os.path.join(a.out, name))  # alpha matters (canvas destination-in)
cx, cy, rx, ry = map(float, a.head.split(","))
save_mask(lambda d: d.ellipse((cx - rx, cy - ry - 20, cx + rx, cy + ry - 20)), 14, "tamara-headmask.png")
pts = list(map(float, a.jaw.split(","))); save_mask(lambda d: d.polygon(list(zip(pts[::2], pts[1::2])), fill=255), 3, "tamara-jawmask.png")
print("bbox", img.getbbox())
