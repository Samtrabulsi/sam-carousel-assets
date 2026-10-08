---
name: compositor-projects
description: Build or edit layered image projects for Compositor (robbietilton/Compositor), the free Mac Photoshop alternative, by writing its .comp folder format (PNG layers + manifest.json) so Sam can open and finish them on a Mac. Use when Sam asks for a layered file to edit in Compositor, wants slides/ads delivered as editable layers instead of a flat image, or asks about Compositor.
---

# Compositor projects (.comp)

App: https://github.com/robbietilton/Compositor · MIT · **macOS 26+ on Apple silicon only**.
Install on Sam's Mac: `brew install --cask robbietilton-compositor`.
Claude can't run the app from a cloud session — it **writes the project files**; Sam opens them. Spec: `docs/writing-comp-files.md` in the repo (re-read it if anything below fails; format `version` may move past 11).

## Format

```
Name.comp/
├── manifest.json
└── images/
    ├── <UPPERCASE-UUID>.png        layer pixels, 8-bit RGBA
    └── <UPPERCASE-UUID>.mask.png   optional mask, 8-bit grayscale (white = show)
```

manifest.json top level: `format: "com.compositor.project"`, `version: 11`, `colorSpace: "sRGB"`, `documentID` (UUID; keep unchanged when editing), `width`, `height`, `resolution: 72`, `activeLayerID`, `layers` (**bottom → top**).

Layer: `id`, `name`, `imageFile` (= `<id>.png`), `isVisible`, `isGroup`, `opacity` 0–1, `blendMode`, `transform {origin:[x,y], size:[w,h], rotation (deg cw), flipX, flipY, sampling: "High quality"|"Smooth"|"Nearest"}`; optional `maskFile` + `maskEnabled`. Adjustment layers have no `imageFile` and an `adjustment` object — for anything beyond the basics, make one in the app, save, and copy its JSON shape.

Blend modes (exact spelling): Normal, Darken, Multiply, Color Burn, Linear Burn, Lighten, Screen, Color Dodge, Linear Dodge (Add), Overlay, Soft Light, Hard Light, Vivid Light, Linear Light, Pin Light, Hard Mix, Difference, Exclusion, Subtract, Divide, Hue, Saturation, Color, Luminosity.

## Rules (any violation → Compositor silently ignores the whole file)

- Image filename == layer id (uppercase) + `.png`; ids unique; every referenced PNG exists.
- Valid JSON; blend modes spelled exactly.
- Writing into an open project: PNGs first → manifest to a temp file inside the package → atomic rename over `manifest.json` → delete unreferenced PNGs → delete `QuickLook/`.
- Replacing a PNG with one of identical byte size isn't detected — also touch the manifest.
- Max 30,000 px per side.

## Helper

`scripts/build_comp.py` builds a project from ordered PNG layers (bottom first):
```bash
python3 .claude/skills/compositor-projects/scripts/build_comp.py out/Slide-01.comp \
  --size 1080 1350 \
  --layer background.png "Background" \
  --layer photo.png "Photo" --at 0 300 --blend Multiply --opacity 0.9 \
  --layer headline.png "Headline"
```
Render text/graphics to transparent PNGs first (e.g. via the existing HTML → Playwright pipeline with a transparent background), one PNG per editable element, so Sam can move/restyle each in Compositor. Validate with `--check` on an existing project.

## Delivery

Zip the `.comp` folder (`zip -r Slide-01.comp.zip Slide-01.comp`) — a bare folder doesn't survive most uploads. Tell Sam: unzip, double-click to open, export via File → Export (JPEG; check the app for other formats).
