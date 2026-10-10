#!/usr/bin/env python3
"""Remove the light background fringe from cutouts: every semi-transparent edge pixel takes its colour from the
opaque pixels next to it (colour bleed: blur(rgb*alpha)/blur(alpha)), so hair edges stay dark on any background.
usage: fix_edges.py <cutout.png> [...]   (edits in place)"""
import sys
import numpy as np
from PIL import Image, ImageFilter
for f in sys.argv[1:]:
    im = Image.open(f).convert("RGBA"); a = np.asarray(im).astype(np.float32)
    al = a[..., 3:] / 255
    solid = (al > 0.95).astype(np.float32)
    num = np.zeros_like(a[..., :3]); den = np.zeros_like(al)
    for r in (2, 5, 10):  # wider radii fill pixels further from solid ones
        pr = Image.fromarray(np.uint8(np.clip(a[..., :3] * solid, 0, 255)))
        pw = Image.fromarray(np.uint8(solid[..., 0] * 255))
        n = np.asarray(pr.filter(ImageFilter.GaussianBlur(r))).astype(np.float32)
        d = np.asarray(pw.filter(ImageFilter.GaussianBlur(r))).astype(np.float32)[..., None] / 255
        take = (den < 0.02) & (d >= 0.02)
        num = np.where(take, n, num); den = np.where(take, d, den)
    bleed = num / np.maximum(den, 1e-3)
    edge = (al < 0.95)
    rgb = np.where(edge, bleed, a[..., :3])
    out = np.concatenate([np.clip(rgb, 0, 255), a[..., 3:]], -1).astype(np.uint8)
    Image.fromarray(out).save(f); print("fixed", f)
