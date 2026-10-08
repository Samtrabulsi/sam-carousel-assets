#!/usr/bin/env python3
"""Build or check a Compositor .comp project from PNG layers.

Layers are given bottom-to-top:
  build_comp.py OUT.comp --size W H --layer FILE.png "Name" [--at X Y] [--fit W H]
                [--blend MODE] [--opacity 0-1] [--hidden] ...
  build_comp.py PROJECT.comp --check
"""
import argparse
import json
import os
import sys
import uuid

try:
    from PIL import Image
except ImportError:
    sys.exit("Needs Pillow: pip install pillow")

BLEND_MODES = {
    "Normal", "Darken", "Multiply", "Color Burn", "Linear Burn", "Lighten",
    "Screen", "Color Dodge", "Linear Dodge (Add)", "Overlay", "Soft Light",
    "Hard Light", "Vivid Light", "Linear Light", "Pin Light", "Hard Mix",
    "Difference", "Exclusion", "Subtract", "Divide", "Hue", "Saturation",
    "Color", "Luminosity",
}
MAX_SIDE = 30000


def parse_layers(argv):
    """Split argv into global args and per-layer option groups."""
    head, layers, cur = [], [], None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--layer":
            cur = {"file": argv[i + 1], "name": argv[i + 2], "at": (0, 0),
                   "fit": None, "blend": "Normal", "opacity": 1.0, "visible": True}
            layers.append(cur)
            i += 3
        elif cur is not None and a == "--at":
            cur["at"] = (int(argv[i + 1]), int(argv[i + 2])); i += 3
        elif cur is not None and a == "--fit":
            cur["fit"] = (int(argv[i + 1]), int(argv[i + 2])); i += 3
        elif cur is not None and a == "--blend":
            cur["blend"] = argv[i + 1]; i += 2
        elif cur is not None and a == "--opacity":
            cur["opacity"] = float(argv[i + 1]); i += 2
        elif cur is not None and a == "--hidden":
            cur["visible"] = False; i += 1
        else:
            head.append(a); i += 1
    return head, layers


def check(project):
    errors = []
    man_path = os.path.join(project, "manifest.json")
    try:
        with open(man_path) as f:
            man = json.load(f)
    except (OSError, ValueError) as e:
        return [f"manifest.json unreadable: {e}"]
    if man.get("format") != "com.compositor.project":
        errors.append("format must be com.compositor.project")
    for side in ("width", "height"):
        if not 0 < int(man.get(side, 0)) <= MAX_SIDE:
            errors.append(f"{side} out of range")
    ids = set()
    for layer in man.get("layers", []):
        lid = layer.get("id", "")
        if lid in ids:
            errors.append(f"duplicate id {lid}")
        ids.add(lid)
        if lid != lid.upper():
            errors.append(f"id not uppercase: {lid}")
        if layer.get("blendMode") not in BLEND_MODES:
            errors.append(f"{layer.get('name')}: bad blendMode {layer.get('blendMode')!r}")
        img = layer.get("imageFile")
        if img is not None:
            if img != f"{lid}.png":
                errors.append(f"{layer.get('name')}: imageFile must be {lid}.png")
            if not os.path.isfile(os.path.join(project, "images", img)):
                errors.append(f"{layer.get('name')}: missing images/{img}")
        mask = layer.get("maskFile")
        if mask and not os.path.isfile(os.path.join(project, "images", mask)):
            errors.append(f"{layer.get('name')}: missing images/{mask}")
    if man.get("activeLayerID") not in ids:
        errors.append("activeLayerID does not match a layer")
    return errors


def build(out, size, layers):
    if not layers:
        sys.exit("Give at least one --layer")
    w, h = size
    if not (0 < w <= MAX_SIDE and 0 < h <= MAX_SIDE):
        sys.exit("size out of range")
    images = os.path.join(out, "images")
    os.makedirs(images, exist_ok=True)
    manifest_layers = []
    for spec in layers:
        if spec["blend"] not in BLEND_MODES:
            sys.exit(f"Unknown blend mode {spec['blend']!r}")
        lid = str(uuid.uuid4()).upper()
        img = Image.open(spec["file"]).convert("RGBA")
        img.save(os.path.join(images, f"{lid}.png"), "PNG")
        lw, lh = spec["fit"] or img.size
        manifest_layers.append({
            "id": lid,
            "name": spec["name"],
            "imageFile": f"{lid}.png",
            "isVisible": spec["visible"],
            "isGroup": False,
            "opacity": max(0.0, min(1.0, spec["opacity"])),
            "blendMode": spec["blend"],
            "transform": {
                "origin": list(spec["at"]),
                "size": [lw, lh],
                "rotation": 0,
                "flipX": False,
                "flipY": False,
                "sampling": "High quality",
            },
        })
    manifest = {
        "format": "com.compositor.project",
        "version": 11,
        "colorSpace": "sRGB",
        "documentID": str(uuid.uuid4()).upper(),
        "width": w,
        "height": h,
        "resolution": 72,
        "activeLayerID": manifest_layers[-1]["id"],
        "layers": manifest_layers,
    }
    tmp = os.path.join(out, ".manifest.json.tmp")
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2)
    os.replace(tmp, os.path.join(out, "manifest.json"))
    return manifest


def main():
    head, layers = parse_layers(sys.argv[1:])
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("project")
    p.add_argument("--size", nargs=2, type=int, metavar=("W", "H"))
    p.add_argument("--check", action="store_true")
    args = p.parse_args(head)
    if not args.check:
        if not args.size:
            p.error("--size is required when building")
        build(args.project, tuple(args.size), layers)
    errors = check(args.project)
    for e in errors:
        print("ERROR:", e)
    if errors:
        sys.exit(1)
    print(f"OK: {args.project}")


if __name__ == "__main__":
    main()
