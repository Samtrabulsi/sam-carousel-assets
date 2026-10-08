---
name: photocraft
description: Automate image editing with PhotoCraft, the open-source Photoshop reimplementation (storytold/photocraft) that has a headless CLI and an MCP server. Use when Sam wants to batch-edit or batch-export images, fill a PSD template (swap text/photos) without Photoshop, convert PSD/PSB/TIFF to PNG/JPEG/WebP, apply the same grade to a folder of photos, or asks about PhotoCraft.
---

# PhotoCraft — scriptable Photoshop alternative

Repo: https://github.com/storytold/photocraft · License: MIT OR Apache-2.0 (ArtCraft name/logos are trademarks).
Status: **early alpha** — its makers say it's not yet a daily Photoshop replacement. No generative AI. Always check output visually before delivering.

## When to use it

- Batch jobs: same edit across a folder (sharpen, curves, resize, convert, LUT).
- PSD templates → filled variants (carousel slides, ad sizes) without opening Photoshop.
- Format conversion with real layer + ICC support (PSD, PSB, layered TIFF, `.pcraft`; PNG, JPEG, TIFF, WebP, GIF, AVIF, EXR… at 8/16/32-bit).

Not for: generative fill/AI images (use Runway/Canva), or Sam's existing HTML→PDF carousel pipeline (keep that as is unless Sam asks to switch).

## Install (Linux cloud session)

Prefer a prebuilt release; fall back to source.
```bash
# Find the latest release assets first (names include the version):
#   https://github.com/storytold/photocraft/releases
# Linux: AppImage, .deb, .rpm, tarball, Flatpak. macOS: photocraft-cli-<ver>-macos-universal.zip
# From source (needs Rust toolchain; slow first build):
git clone https://github.com/storytold/photocraft && cd photocraft
cargo build --release -p photocraft-cli      # CLI only — check AGENTS.md if the package name differs
```
Put the clone in its own directory (untrusted download). Headless CLI needs no GPU display; the desktop app does.

## CLI (`photocraft-cli`)

Subcommands: `convert`, `info`, `run`, `batch`, `commands`, `mcp`. Always run `photocraft-cli <sub> --help` first — flags change between releases.

```bash
photocraft-cli info template.psd                 # inspect layers
photocraft-cli commands                          # list the 500+ command ids + params

# Open → apply commands → save
photocraft-cli run wave.psd \
  --cmd filter.sharpen.smartSharpen     --params '{"amount":80}' \
  --cmd layer.newAdjustmentLayer.curves --params '{"points":[[0,0],[64,48],[192,212],[255,255]]}' \
  --out wave-final.png

# Same action list across a folder
photocraft-cli batch --actions grade.json --in ./raw --out ./graded
```

Every UI action is a command with an id (e.g. `filter.sharpen.smartSharpen`). Find ids with `photocraft-cli commands` or the repo's `docs/parity.md` (Photoshop menu → command mapping).

## MCP server

```bash
photocraft-cli mcp      # headless, or bridges to a running app
```
To use from Claude Code, register it as a stdio MCP server (e.g. in `.mcp.json`: `{"mcpServers":{"photocraft":{"command":"photocraft-cli","args":["mcp"]}}}`), then restart the session so the tools load. The desktop app also has a loopback-only authenticated JSON control channel (`photocraft --control`, see `docs/control-protocol.md`) for UI-level automation and offscreen screenshots.

## Template-fill workflow (carousels / ad sizes)

1. `info` the PSD → note text-layer and image-layer names.
2. Test one variant: replace text / place image via commands → `--out slide-01.png`.
3. Compare against the Photoshop/Canva original side by side (fonts, Arabic shaping & RTL, kerning, effects). Stop and report if anything renders wrong — don't ship.
4. Only then loop over all slides/sizes with `batch` or a script.
5. Save outputs under the repo's existing folders (`instagram/`, `linkedin/`, `x-style/`, `arabic/`) with the usual date-slug naming.

## Gotchas

- Alpha software: ~20 Photoshop tools missing, plugin support limited. Unsupported features return an error rather than crash — read errors, don't guess around them.
- Fonts: install the brand fonts in the session before rendering text or it will substitute. Japanese fonts come from `storytold/craft-fonts` (optional).
- HEIC import needs a build with `--features heif`.
