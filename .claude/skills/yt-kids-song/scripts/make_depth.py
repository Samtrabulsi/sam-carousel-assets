#!/usr/bin/env python3
"""Depth map for a photo-puppet pose (Depth Anything V2 small, Apache-2.0, ONNX on CPU, ~2 s per picture).
usage: make_depth.py <pose-cutout.png> <out-depth.png>
White = close to the camera (nose, hands), black = far (back hair). Used by tamara-photo.js for 3D turns.
Run with the rembg venv: ~/.cache/yt-tools/rembg/bin/python (needs onnxruntime + huggingface_hub)."""
import sys
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from huggingface_hub import hf_hub_download
src, out = sys.argv[1:3]
im = Image.open(src).convert("RGBA"); W, H = im.size
rgb = Image.new("RGB", im.size, (128, 128, 128)); rgb.paste(im, mask=im.split()[3])
h = 518; w = int(round(W / H * h / 14)) * 14
x = (np.asarray(rgb.resize((w, h), Image.BICUBIC)).astype(np.float32) / 255 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
x = x.transpose(2, 0, 1)[None].astype(np.float32)
sess = ort.InferenceSession(hf_hub_download("onnx-community/depth-anything-v2-small", "onnx/model.onnx"), providers=["CPUExecutionProvider"])
d = sess.run(None, {sess.get_inputs()[0].name: x})[0][0]
alpha = np.asarray(im.split()[3].resize((w, h))) > 128
lo, hi = np.percentile(d[alpha], 2), np.percentile(d[alpha], 98)
d = np.clip((d - lo) / (hi - lo), 0, 1); d[~alpha] = np.percentile(d[alpha], 5)  # fill the background with a far value so edges move smoothly
Image.fromarray((d * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14)).save(out)
print("depth", out)
