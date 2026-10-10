# Motion direction: making code animation look professional

Read this before writing any animation prompt or HTML file. The rule behind all of it: **every adjective you replace with a number is a decision you take back from the model.** Without direction, Claude falls back on a few default looks (dark navy, glow, particles, everything fading up). Write numbers instead.

Source: "Opus 5.5 Motion Lab" by @flxrnc (X article, 2026-09-30), plus the references it cites (easings.net, Material 3 motion, NN/g, WCAG). Ideas summarised in our own words; the article's prompts belong to its author.

## 1. Brief template (fill every line before writing code)

```
GOAL:     One sentence: what the viewer should feel or do after watching.
TIME:     Length in seconds, fps, total frames. Loop or not.
CANVAS:   1080x1920 (Reels/TikTok) | 1080x1350 (IG/LinkedIn feed) | 1080x1080 | 1920x1080
BRAND:    Exact hex colours, fonts (EN + Tajawal/Cairo for AR), logo file, tone.
WORDS:    Exact on-screen text, EN and AR, in order. No invented taglines.
SHOTS:    Per shot: frame range, ONE hero move, handoff (hard cut on beat / match cut / mask wipe).
MOTION:   Easing per move type, spring damping ratio, stagger, BPM.
CAMERA:   (3D only) field of view, path in degrees, push-ins with easing and frame.
BAN:      Default looks to avoid (start from the list below, add to it every round).
OUTPUT:   Engine + numbers, e.g. "one HTML file, canvas draw(t), 1080x1920, 30 fps, 450 frames".
QA:       Before the full render, make a contact sheet and check it against SHOTS.
```

Write GOAL first; if it can't be one sentence, stop and ask Sam. Then TIME, because every other number depends on the frame count. Default handoff is a hard cut; a transition should be a choice.

## 2. Ban list (starting point; keep it growing)

- purple/blue gradients, glow, bloom, lens flares, neon
- floating particles as decoration, glowing orbs, halo rings
- dark navy "space" background unless the brand uses it
- everything fading in at once; fade-and-slide-up on every element
- centred-everything layouts
- text that moves while it is being read
- spinning turntable product shots
- made-up taglines or text not in WORDS

After every first render, name which defaults it used anyway and add them by name. "Avoid a generic AI look" doesn't work; it just swaps one default for another.

## 3. Hierarchy: one hero per shot

- One hero move per shot. Everything else waits, dims to ~40%, or holds still.
- Secondary moves travel 50–70% as far as the hero and start 100–200 ms after it.
- Ambient motion stays under 5% of the hero's travel, on a slow sine, and never stops.

## 4. The numbers

**Easing** (curves from easings.net)
- Enter: ease-out (quint/expo for premium). Exit: ease-in, 40–50% shorter than the entrance (e.g. 400 ms in, 200 ms out).
- Moving across the screen: ease-in-out. Camera: the softest, ease-in-out-quart.
- Linear only for rotation, progress bars and loop phase. A linear move is what makes a render look like a render.

**Springs**: describe by damping ratio ζ = damping / (2·√(stiffness·mass))
- 1.0 no bounce · 0.7–0.85 premium · 0.4–0.6 playful · under 0.3 cartoon.
- Remotion's default spring ≈ 0.5; react-spring's default ≈ 1.0.
- Position and scale may bounce; opacity and colour never do.
- Use a closed-form spring (progress as a function of t) so any frame renders on its own:

```js
// Underdamped spring progress 0→1 at time t (s). zeta<1, omega = natural frequency (rad/s).
function spring(t, zeta = 0.75, omega = 12) {
  if (t <= 0) return 0;
  const wd = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * t) * (Math.cos(wd * t) + (zeta * omega / wd) * Math.sin(wd * t));
}
```

**Durations and stagger**
- UI feedback 100–200 ms; UI moves 200–500 ms; hero reveals 600–900 ms.
- Stagger: letters 1 frame apart, words 60–120 ms, list items 40–80 ms.
- Start the next element when the previous one is 30–50% done.
- Think in frames: at 30 fps a frame is 33 ms (400 ms = 12 frames); at 24 fps 42 ms.

**Beat grid**
- Frames per beat = fps × 60 / BPM (120 BPM at 30 fps = 15; at 24 fps = 12).
- Compute each beat from time and round it (`Math.round(i * fps * 60 / bpm)`); adding a rounded step repeatedly drifts.
- Cut on the beat; change layout on the bar (every 4 beats), not every beat.

**Holds and readability**
- On-screen text holds ≥ 0.3 s per word + 0.5 s (two-word title = 1.1 s; a 6-word hook ≈ 2.3 s). Arabic: allow the same or a little more.
- During a hold, a slow ~2% push keeps the frame alive.
- Push key poses 10–30% further than feels right; phones shrink everything.

**Accessibility (WCAG)**
- Text contrast ≥ 4.5:1 on every frame, including over moving backgrounds.
- Never more than 3 flashes per second.

**Parallax**: foreground 1.0, middle 0.5, background 0.2.

## 5. Render contract (paste under every animation brief)

- Everything is a pure function of time: `draw(t)` with t from `performance.now()` (our recorder controls it). No `Math.random()` without a seed; use a seeded PRNG.
- No state carried between frames that a jump to frame N would skip (no accumulated physics; use closed-form springs and easing).
- Fonts loaded before frame 0 (`display=block` or `document.fonts.ready`).
- Frame 0 is a finished composition, not black (it's the thumbnail/first impression).
- Loops: render frames 0…N−1 only; drive motion by `phase = frame / N` with whole-number cycles; for organic drift, sample noise around a circle so it returns to the start.
- `?t=SECONDS` in the URL freezes the animation at that time (snippet below) so any frame can be inspected alone.

```html
<script>
// Freeze at ?t=2.5 for inspection (ignored by record.mjs, which drives its own clock).
const _t = new URLSearchParams(location.search).get('t');
if (_t !== null) { const T = parseFloat(_t) * 1000; performance.now = () => T; }
</script>
```

Every time a fix works, add it to the contract so the failure doesn't come back.

## 6. Review loop: render, look, fix

1. Contact sheet of the HTML before any full render:
   `node .claude/skills/code-motion-video/scripts/contact-sheet.mjs page.html sheet.png --w 1080 --h 1920 --fps 30 --sec 20`
2. Read the sheet against SHOTS and the ban list. Write notes **with frame numbers**, not feelings.
3. Fix one or two notes per round, not all at once (that turns a fix into a rewrite).
4. For a specific glitch, sheet the frames either side: `--frames 84,85,86 --cols 3`, and describe what changed.
5. Two to four rounds is normal. After the MP4 render, sheet the MP4 too (`contact-sheet.mjs out.mp4 sheet.png`).
6. Count the follow-ups. If Sam posts the process, post the prompt and the follow-ups, not "one prompt".

Notes that work (point at frames):
- "The punch at frame 84 peaks late; move the peak 2 frames earlier."
- "Frames 140–160: the title fades while still being read; hold it until 170."
- "Shot 2 has three things moving at once; keep the headline, delay the rest 150 ms at 60% travel."
- "Frame 0 is empty; start with the logo already placed."

Translate client feedback into numbers:

| Feedback | Change |
|---|---|
| "Make it pop" | scale 1.0 → 1.08 → 1.0 over 6 frames, peak on the beat |
| "Make it premium" | ease-out-quint entrances, springs at ζ 0.8, no overshoot on text |
| "It drags" | shorten each hold by one beat (15 frames at 120 BPM / 30 fps) |
| "Too busy" | one hero at a time; the rest start 150 ms later at 60% travel |
| "Looks like AI" | list the defaults it used by name, ban each, re-render |

## 7. Five animation principles as numbers (for characters, mascots, logos)

From Disney's 12 principles (Thomas & Johnston, *The Illusion of Life*):
- **Anticipation**: 2–4 frame dip opposite the move before it starts.
- **Squash and stretch**: keep volume (scaleX × scaleY ≈ 1); e.g. 1.15 × 0.87 on landing for 3 frames.
- **Overlapping action / follow-through**: parts settle on looser springs (main ζ 0.7, attachments ζ 0.5) and 2–4 frames later.
- **Arcs**: moving things travel on curves, not straight lines.
- **Slow in / slow out**: easing on every key, never linear.

Add a "must not change" line for any character or logo (exact proportions, colours), so style never drifts between shots. Pairs with the `cartoon-presenter` skill.

## 8. Fixes table

| Symptom | Cause | Fix |
|---|---|---|
| Hiccup at the loop seam | rendered frame N as well as 0 | render 0…N−1; whole-number cycles |
| Shapes jitter frame to frame | unseeded `Math.random()` in draw | seeded PRNG, generated once |
| Frame differs between runs | uses wall clock or accumulated state | pure `draw(t)`; closed-form springs |
| Fallback font in first frames | fonts not ready | `display=block` + wait for `document.fonts.ready` |
| Arabic letters disconnected / wrong order | canvas text without RTL | `ctx.direction='rtl'`, Arabic-capable font, or render text in DOM |
| Shader/WebGL ignores timing | shader reads its own clock | pass `performance.now()` as a uniform |
| Motion looks robotic | linear easing or even spacing | ease-out/in-out; check the contact sheet spacing |
| Generic AI look | adjectives instead of numbers | brief template + ban list |

## 9. Sound and export

- Instagram/LinkedIn/X autoplay muted: the picture must work in silence. Burned-in text carries the message.
- Music bed: use the `background-music` skill (ducking, loudness). Target about −14 LUFS, peaks ≤ −1 dBTP.
- Sound effects on hits: land the sound on or 1 frame after its picture, never before.
- Export MP4 for posts (record.mjs). GIF only for X inline loops: one palette for the whole GIF; at 24 fps alternate 40/50 ms frame delays to keep exact timing; X caps GIFs at 350 frames.

## 10. Engine choice

- One idea under ~10 s, 2D, brand text and shapes → plain HTML/canvas or CSS (default; our recorder handles it).
- GSAP timelines → fine in HTML (GSAP is free, including SplitText/MorphSVG).
- Anything 3D → Three.js, pinned version, time from the frame not the clock. Cloud sessions have no GPU, so keep scenes light or render 3D on Sam's machine.
- Series/templates/data-driven videos → consider Remotion (free up to 3 employees) or HyperFrames (Apache 2.0) later; not installed now.
