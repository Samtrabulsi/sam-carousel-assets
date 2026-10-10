---
name: yt-thumbnail
description: Make YouTube thumbnails from a small JSON spec — consistent per-channel layouts (title + checklist, title + cut-out face, combo, big number/year), rendered to 1280x720 JPG plus a phone-size preview, and 2 variants for YouTube Test & Compare. Use for "make the thumbnail", "thumbnail options", "A/B thumbnails", or the Producer routine.
---

# yt-thumbnail

```bash
python3 .claude/skills/yt-thumbnail/scripts/thumb.py episode/thumbnail.json episode/thumbnail.jpg
```
This writes `thumbnail.jpg` (1280x720) and `thumbnail-small.jpg` (320 px wide: how most viewers see it).

## thumbnail.json

```json
{"layout": "combo", "kicker": "SMALL BUSINESS", "lines": ["5 Problems", "AI Fixes", "*For You*"],
 "items": ["Missed leads", "Slow follow-ups"], "face": "face-crop.png", "tag": "Costing you money weekly",
 "colors": {"accent": "#FFB547", "alert": "#FF5C6C", "kicker": "#5FD3D9", "bg": "#0B1426"}}
```

| layout | use for | fields |
|---|---|---|
| `list` | problem/benefit lists | lines, items (✗ red; `"good": true` for ✓ green), tag |
| `face` | emotion-led topics | lines, face (cut-out PNG/JPG, right side) |
| `combo` | lists that also need a face | lines, items, face (middle), tag |
| `number` | histories, money stories | lines, number ("1964", "$100B"), tag |

- `*word*` in a line makes it the accent colour. `bg` adds a darkened full-bleed photo. `size` changes the title size (default 100).
- Each channel keeps one layout family and palette (set in its niche file), so viewers recognise it in the feed.

## Rules that move CTR
- 3 short lines max, 2–4 words each. It must read at 320 px: always open `thumbnail-small.jpg` and look.
- The thumbnail adds to the title; it doesn't repeat it. Title "The ENTIRE History of Nike in 18 Minutes" → thumbnail "1964 → $100B".
- One focal point: a face with a strong emotion, a big number, or a striking object.
- Make 2 variants for every video (different hook or layout) and upload both with YouTube Studio → Test & Compare.

## Faces and images
- Faces come from AI images of **fictional** people (vidIQ `vidiq_generate_thumbnail`, Runway, Canva), cut out by cropping. Earlier example: `youtube/2026-10-08-5-tasks-to-automate-v2/face-crop.png`.
- **Never** a real person's likeness (CEOs, politicians, celebrities). That means YouTube's AI-disclosure rules, impersonation and defamation risk. For a company-history video, use the product, a building or a year instead.
- No other brands' logos as the main element. Product photos from Pexels or CC0 are fine.
