---
name: cartoon-presenter
description: Animated cartoon characters that stay on-model across every video — "Gia", the Grow Success Online presenter (lip-synced to the voiceover), plus how to make story-style cartoon shorts with a recurring character. Use when Sam asks for a cartoon/animated character, a mascot, a consistent character, a presenter/host for faceless videos, lip sync, "make the character talk", or animated story videos.
---

# Cartoon presenter and recurring characters

Consistency comes from **drawing the character in code**, not from image generation. The same function draws the same face, outfit and colours in every frame of every video, forever. AI image tools drift from shot to shot; code doesn't.

## 1. Gia, the channel presenter (use this by default)

`scripts/character.js` draws Gia waist-up: curly bun, teal Grow Success polo, amber "G" badge, amber earrings. Example: `examples/gia-demo.mp4` (12 s, lip-synced to the episode narration).

```js
// bottom-centre of the character at (0,0); she is ~560 units tall
ctx.save(); ctx.translate(500, 1080); ctx.scale(1.45, 1.45);
drawGia(ctx, { t, pose: 'point', lt, viseme: giaViseme(CUES, t), look: 0.4, blinkSeed: 0.7 });
ctx.restore();
```

- **Poses:** `idle, wave, point, worried, think, surprised, happy, cheer`. Each blends in from idle over 0.5 s (`lt` = seconds since the pose started), and the wave arm waves.
- **Face:** blinks every ~3.7 s (offset with `blinkSeed`). Eyes follow `look` (-1..1). Brows and the resting mouth change with the pose.
- **Lip sync:** `viseme` is a Rhubarb mouth shape (below). `mouth` (0..1 loudness) is a fallback if you don't have cues.
- To face left, `ctx.scale(-1, 1)` after translating. Her "pointing" arm then points left.

### Lip sync (Rhubarb Lip Sync, MIT)

```bash
.claude/skills/cartoon-presenter/scripts/lipsync.sh voiceover.wav cues.json [script.txt]
python3 -c "import json;print('window.CUES='+json.dumps(json.load(open('cues.json'))['mouthCues'])+';')" > cues.js
```

- It downloads Rhubarb 1.14.0 on first use (to `~/.cache/rhubarb`).
- It runs in `phonetic` mode, which is fast and works in any language. Measured about 5 s per 20 s of audio, so a 10-minute episode takes about 2–3 minutes.
- Passing the script text (`dialog.txt`) can improve accuracy in English.

| shape | sounds | Gia's mouth |
|---|---|---|
| A | M, B, P | closed line |
| B | K, S, T, EE | slightly open, teeth |
| C | EH, AE | open, tongue |
| D | AA | wide open |
| E | AO, ER | rounded |
| F | UW, OW, W | puckered |
| G | F, V | top teeth on lip |
| H | L | tongue up |
| X | silence | resting smile/pose mouth |

### Pose direction (choose per scene, not per word)

| scene | pose |
|---|---|
| intro, chapter title, end card | `wave` (first 2 s), then `point` |
| tools, steps, flow, "the fix" | `point` toward the content |
| a problem, a cost, "too late" | `worried` |
| a question, "where to start", deciding | `think` |
| a big stat | `surprised` |
| a win, "done", "paid" | `happy` or `cheer` |

### Putting her in an episode (`code-motion-video` HTML engine)

- Load `character.js` and `cues.js` in `video.html`.
- In beats where she appears, draw the content scaled to about 0.82 and shifted away from her side. She stands in a ~360 px column at the left or right edge, bottom-anchored, above the progress bar, with captions unchanged.
- Don't put her in every scene: she works best on intros, chapter titles, problems, stats, warnings and the end card. Leave dense tool, step and flow screens full width.
- Check a still per beat with `youtube/tools/stills.cjs` and a strip of a speaking moment (mouth shapes changing) before the full render.

### Changing Gia
Change her design only in `character.js`, never per video. If Sam wants a different look (outfit, skin tone, hair, a second character), add it as a new named function (e.g. `drawSam`) in the same file, and render a pose sheet of all 8 poses for Sam to approve before using it.

## 2. Story-style cartoon shorts (characters acting out a story)

For animated stories rather than a presenter, use one of these, in this order:

1. **`animation-studio` plugin** (Anthropic Directory, by Afaq Rashid). It draws hand-drawn shorts in code with a soundtrack generated in sync, and outputs a 1080p MP4 (16:9 or 9:16). Install it from the plugin card. Its own skill then drives the workflow.
2. **ClaudeAnimationBase** (github.com/JohnHeibel/ClaudeAnimationBase, MIT, about 958 stars). A p5.js + p5.brush watercolour cartoon kit with a recurring character (Clawd) that has 31 emotions, drawn turns and a renderer. Use: `git clone` it into its own folder, `npm install`, then read its `ANIMATION_GUIDE.md` in full before drawing. Build our own character in its `src/` in place of Clawd (Clawd is Anthropic's mascot, so don't use him on a client or Sam channel). The rules worth keeping from its guide:
   - Storyboard first: logline, world, motif, emotion arc and per-shot "reads" with times.
   - Time every read for a first-time viewer. One read at a time; fast actions, held meanings.
   - Faces act (anticipation, take, settle); they never snap. Nothing is ever fully still.
   - Every seam gets a transition: wipe, iris, match cut.
   - Review with contact sheets, frame strips and face crops before rendering.
   - Keep the character on model: same shape and features in every shot.
3. Add lip sync to either with `scripts/lipsync.sh` and map the A–H shapes to that character's mouths.

Not recommended: synctoon (GPL-3, needs paid ElevenLabs, known sync bugs). AI image generators for "consistent characters" drift between shots and cost credits per image.

## Guardrails
- Only original characters, or ones Sam owns. No copyrighted cartoon characters, and no other brands' mascots on client work.
- A cartoon presenter is not a real person, so no face or voice consent is needed. But never make Gia look like a specific real person.
- AI voice and animated character: the YouTube "altered or synthetic" label is not required for clearly animated content.
