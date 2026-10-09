---
name: yt-produce
description: Turn an episode folder (script.json + episode.json) into a finished faceless YouTube video with one command — licence-safe photos, Kokoro AI voice, per-scene timing, optional lip-synced presenter, captions, motion graphics, music bed, 1080p render, 720p preview and thumbnails. Use for "make the video", "render the episode", "produce it", or the Producer routine.
---

# yt-produce: script → finished video

```bash
source .claude/skills/yt-produce/scripts/setup.sh          # once per container (yt-dlp, Kokoro voice, models)
.claude/skills/yt-produce/scripts/produce.sh <episode-dir> --stills-only   # fast check: one still per scene
.claude/skills/yt-produce/scripts/produce.sh <episode-dir>                 # full run
```

| step | what | output |
|---|---|---|
| 1 photos | resolves `"q:search words"` in script.json (Pexels with `PEXELS_API_KEY`, else CC0 Openverse); no duplicates | `photos/*.jpg`, `photos/CREDITS.md` |
| 2 voice | Kokoro TTS, one call per scene, voice/speed from episode.json | `voiceover.wav`, `timeline.json` |
| 3 lip-sync | only if `"presenter": true`: Rhubarb mouth cues for Gia | `cues.json` |
| 4 data | bundles script + timeline + episode + cues; copies the engine | `data.js`, `video.html` |
| 5 stills | one still per scene + contact sheet | `stills-sheet.jpg`. **Look at it.** |
| 6 music | `background-music` mix: loop, duck under voice, -14 LUFS | `mix.m4a` |
| 7 render | 8 resumable chunks × 4 in parallel, then joined with the audio | `final.mp4`, `preview-720p.mp4` |
| 8 thumbnail | if `thumbnail.json` exists (yt-thumbnail) | `thumbnail.jpg` |

- Steps skip when their output is newer than their input, so a rerun after a crash or a container restart picks up where it stopped. Finished render chunks are kept in `.render/parts/`.
- **Speed:** about 9 s of compute per second of video on 4 cores. An 18-minute video takes about 2.5 hours. Run it in the background and keep the stills check first.
- **Tested** 2026-10-09 on a 51 s sample (`examples/nike-sample/`): every step passed, -14.2 LUFS, 1080p H.264/AAC.

## Before the full render, check the stills sheet for
- unreadable or overlapping text
- scenes with no photo where one was expected (a fetch found nothing, so change the query)
- photos that don't fit (wrong subject, a visible logo or watermark, a real person in a misleading context). Replace with a better `q:` query or a specific file in `photos/`
- Gia covering content (set `"gia": false` on that scene)

## The engine (`templates/engine.html`)
- A 1920×1080 canvas with a deterministic clock (the frame at time t is always the same), so chunks can render in parallel.
- **Branding per channel** comes from episode.json: `brand.name/initial/display`, `colors`, `chapterLabel`, `presenter`.
- **Scene types** and fields are listed in `yt-script/SKILL.md`. To add a type, add a `V.<name> = (b, lt, d) => {...}` function (lt = seconds into the scene, d = scene length) and document it there.
- **Motion on every scene:** slide in and out, a slow camera push, Ken Burns on photos, a chapter light sweep, particles, a progress bar, and captions synced to the voice.

## Video files and git
Commit the episode folder **without** `final.mp4`, `voiceover.wav`, `mix.m4a` and `.render/`; a `.gitignore` per episode covers that. The final video lives on YouTube (a private upload is the review copy). Commit `preview-720p.mp4` only if it's under 50 MB and there's no YouTube upload yet.
