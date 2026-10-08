---
name: code-motion-video
description: Make motion-graphics videos by writing the animation as code (HTML/Canvas/SVG/GSAP/Three.js) and rendering it to MP4 — animated versions of carousels and LinkedIn/X posts, 15–30s business explainers, logo reveals, brand/launch promos, Reels/TikTok/Shorts. Uses the awesome-opus5-5-videos prompt library for proven prompts. Use when Sam asks for an animated post, motion graphics, an explainer/promo/launch video, a logo animation, "turn this carousel into a video/Reel", or mentions that repo.
---

# Code-made motion videos

Claude writes the animation as a single HTML file, then `scripts/record.mjs` renders it frame by frame to MP4. This sits next to Sam's existing HTML → PDF carousel pipeline: same brand HTML/CSS, now moving. No credits, exact brand fonts/colors, Arabic text renders as real text.

Use **Runway** instead when the shot needs photoreal footage, people, or camera-shot realism. Combine them when useful (Runway b-roll as a `<video>` layer in the HTML).

## Prompt library

Repo: https://github.com/yihui-dev/awesome-opus5-5-videos (MIT list; **each prompt belongs to its creator** — adapt, don't republish verbatim). 513 prompts with creator posts; side-by-side remakes at skillry.dev/ai-videos/opus-5-5.

Fetch one prompt when needed:
```bash
curl -sSfL https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/prompts/<slug>.md
# search all: data/videos.json (fields: slug, category, tech_tags, prompt, prompt_partial)
```
~45% of entries are partial (`prompt_partial: true`) — prefer complete ones.

Shortlist for Sam's work:

| Slug | Use it for |
|---|---|
| `alex-prompter-997524` | 30s business explainer, 5 scenes: problem → what I do → 3 steps → proof → name. Best default for client explainers. |
| `polydao-566862` | Topic "showreel" in brand colors — animated version of a carousel/post topic. |
| `daniel-mac8-306214` | Animation made to accompany a specific X/LinkedIn post. |
| `verbove-268381` | Strict product-promo spec (one canvas, `draw(t)`, 120 BPM beats, real data, 1:1/16:9/9:16). Good model for deterministic output. |
| `0xvalure-331584`, `mounnna-497266` | Logo → reel / wireframe-to-logo reveal. |
| `ceowinkz-683602` | 15s pitch for a company to a prospect (agency pitch video). |
| `gouthamjay8-910269`, `jhylee95-452427` | Product/SaaS launch video from a real site's assets. |

## Workflow

1. **Brief**: topic or source (carousel PDF/HTML in this repo, post text, client site), length (Reels 9:16 15–30s, LinkedIn 1:1 or 4:5, YouTube 16:9), language (EN/AR), music yes/no.
2. **Pick & adapt a prompt** from the shortlist; fill brand colors/fonts from the client's existing assets in this repo.
3. **Write one self-contained HTML file** at the exact output size. Rules that make rendering reliable:
   - Animation driven by `requestAnimationFrame` / GSAP / CSS animations / `setTimeout` — the recorder virtualises all of these. Best: a single `draw(t)` from `performance.now()`.
   - Total length fixed and known; no user interaction required; first frame meaningful.
   - Fonts via `@font-face` with local files or Google Fonts; RTL with `dir="rtl"` for Arabic.
   - No external video/audio autoplay dependence — add music at render time.
4. **Preview stills** before a full render: render 1–2s, extract frames with ffmpeg, look at them.
5. **Render**:
   ```bash
   node .claude/skills/code-motion-video/scripts/record.mjs page.html out.mp4 --w 1080 --h 1920 --fps 30 --sec 20 [--audio track.mp3]
   ```
   Sizes: 9:16 `1080x1920`, 4:5 `1080x1350`, 1:1 `1080x1080`, 16:9 `1920x1080`.
6. **Check** the MP4 (extract frames at hook, middle, end), then deliver; save under the repo's platform folders with the date-slug naming; schedule via `/schedule-post` / Metricool if asked.

## Recorder notes (`scripts/record.mjs`)

- Uses Playwright Chromium (preinstalled in cloud sessions; local or global `playwright`) + ffmpeg → H.264 MP4, yuv420p, CRF 18.
- Virtual clock: frame N is exactly N/fps seconds — smooth output regardless of machine speed. Tested: rAF canvas, CSS keyframes and setTimeout all stay in sync.
- Not virtualised: `<video>`/`<audio>` elements and WebGL shaders reading their own clocks — drive shader time from `performance.now()` and pass it as a uniform. For `<video>` layers, set `video.currentTime` from `performance.now()` each frame.
- Audio: only via `--audio` (cut to video length). Use royalty-free music Sam has rights to.
- Speed: ~2–5 frames/s at 1080p → a 20s Reel takes a few minutes.

## Guardrails

- Credit/adapt library prompts; never present someone's showcase video as Sam's work.
- Real logos/brands only for Sam's own clients with permission; no impersonation of other companies.
- Disclose AI-made content where the platform/client requires it.
