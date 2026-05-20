"""HTML -> PNG renderer using Playwright Chromium.

Size presets aligned with current IG / FB feed best practices (2026):
  - ig_portrait  1080x1350  (default, 4:5, best IG reach)
  - square       1080x1080  (universal FB+IG)
  - fb_landscape 1200x630   (FB feed, link cards)
  - story        1080x1920  (IG/FB Story, Reel cover)

The HTML is responsible for its own layout. The renderer just sets the viewport,
waits for webfonts to load, and screenshots a fixed clip.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SizePreset:
    name: str
    width: int
    height: int
    description: str


PRESETS: dict[str, SizePreset] = {
    "ig_portrait":  SizePreset("ig_portrait",  1080, 1350, "Instagram feed portrait 4:5 (default)"),
    "square":       SizePreset("square",       1080, 1080, "Universal IG+FB feed square"),
    "fb_landscape": SizePreset("fb_landscape", 1200, 630,  "Facebook feed / link preview"),
    "story":        SizePreset("story",        1080, 1920, "IG/FB Story or Reel cover"),
}

DEFAULT_PRESET = "ig_portrait"


def resolve_preset(name: str) -> SizePreset:
    key = name.lower().replace("-", "_")
    if key not in PRESETS:
        valid = ", ".join(PRESETS)
        raise ValueError(f"unknown size preset '{name}'. Valid: {valid}")
    return PRESETS[key]


def render(
    html_path: str | Path,
    output_path: str | Path,
    preset: str | SizePreset = DEFAULT_PRESET,
    *,
    wait_extra_ms: int = 600,
    device_scale_factor: int = 1,
) -> Path:
    """Render a single HTML file to PNG at the preset's exact pixel size."""
    from playwright.sync_api import sync_playwright

    p = preset if isinstance(preset, SizePreset) else resolve_preset(preset)
    src = Path(html_path).resolve()
    dst = Path(output_path).resolve()
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": p.width, "height": p.height},
            device_scale_factor=device_scale_factor,
        )
        page = ctx.new_page()
        page.goto(f"file://{src}")
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        if wait_extra_ms > 0:
            time.sleep(wait_extra_ms / 1000)
        page.screenshot(
            path=str(dst),
            full_page=False,
            clip={"x": 0, "y": 0, "width": p.width, "height": p.height},
            omit_background=False,
        )
        browser.close()
    return dst


def render_many(
    html_paths: Iterable[str | Path],
    output_dir: str | Path,
    preset: str | SizePreset = DEFAULT_PRESET,
    **kwargs,
) -> list[Path]:
    """Render N HTML files to PNGs (for carousel posts). Returns list in input order."""
    p = preset if isinstance(preset, SizePreset) else resolve_preset(preset)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    for src in html_paths:
        src_path = Path(src)
        dst = out_dir / f"{src_path.stem}.png"
        results.append(render(src_path, dst, p, **kwargs))
    return results


if __name__ == "__main__":  # quick manual test
    import sys
    if len(sys.argv) < 3:
        print("usage: python render.py <html> <out.png> [preset]")
        sys.exit(1)
    out = render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PRESET)
    print(f"rendered: {out}")
