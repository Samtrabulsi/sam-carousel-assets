---
name: yt-kids-song
description: Make educational songs for the kids channel (ages 4-8, school topics) — lyrics that teach one idea, a Suno song made from them, a bright cartoon lyric video timed to the vocals, Made-for-Kids upload settings, and 30-60 min compilations for watch hours. Use for "kids song", "make a song about X for kids", "nursery rhyme", "learning song", the kids channel, or when a routine picks up a card on the Kids learning songs channel.
---

# Kids learning songs (channel: Little Miss Tamara)

Niche config: `.claude/skills/yt-automation/niches/kids-songs.json`. Scout report: `youtube/kids-songs/scout-*.md`.

## Positioning (why school topics, not toddler basics)
The 2026-10-09 scout showed toddler basics (alphabet, colors, body parts) have 10+ videos over 100K each, with leaders at 0.7–1.7 **billion** views (Cocomelon, Super Simple). School topics for ages 4–8 have real demand and fewer strong videos: phases of the moon (7.5), nouns and verbs (6.0), states of matter (5.0), life cycles, place value. Teachers play these in class, so one good song gets replayed for years.

## Pipeline per song (folder `youtube/kids-songs/<date>-<slug>/`)
1. **Lyrics** → `lyrics.md`
   - One teaching idea per song, 3–5 facts, each fact checked against a school source (NASA Kids, National Geographic Kids, a state curriculum standard). List them in `sources.md`.
   - Structure: intro (4 bars) · verse · **chorus** · verse · chorus · bridge (quiz: "Can you say it with me?") · final chorus. The chorus carries the key fact and repeats 3–4 times.
   - Short lines (4–7 syllables), simple words, rhymes that land on the fact word, actions kids can copy ("Clap for the full moon!").
   - Length 2–3 minutes.
2. **Song in Suno** (Sam's account; paid plan required for monetized use)
   - Custom mode → paste the lyrics with `[Verse]`, `[Chorus]`, `[Bridge]` tags.
   - Style prompt pattern: `upbeat children's educational pop, cheerful female vocal, clear diction, ukulele, glockenspiel, handclaps, 110 bpm, bright, simple melody`.
   - Make 2 versions, pick the one with the clearest words. Download **MP3 + the vocal stem** (Studio → Get stems) to `song.mp3` and `vocals.wav`.
   - Save the Suno song link and plan in `README.md` (proof of licence for Content ID disputes).
3. **Lyric timing** → `words.json`:
   ```bash
   python3 -m venv ~/.cache/yt-tools/whisper && ~/.cache/yt-tools/whisper/bin/pip install faster-whisper   # once per container
   ~/.cache/yt-tools/whisper/bin/python .claude/skills/yt-kids-song/scripts/align_lyrics.py song.mp3 lyrics.md words.json
   ```
   Whisper (small.en) hears the sung words, then they're matched to the known lyrics; missed words are interpolated. Works on the full Suno mix (vocals stem is better if you have it). Lines whisper missed entirely: set them by the spacing of an earlier chorus and mark `"estimated": true`.
4. **Video** (`templates/kids-engine.html`, deterministic canvas):
   - **Tamara** (`templates/tamara.js`): the channel host, drawn in code so she's identical in every video. Poses `idle, sing, wave, point, clap, cheer, dance, open`; mouth shapes follow the sung words (`tamaraMouth`); dance/clap/bounce on the beat. Change her only in `tamara.js` and re-render `pose-sheet.html` for approval.
   - The engine draws the night-sky set, title card, karaoke lyrics (each word lights up and bounces when sung), logo and end card. Each song adds its own `visuals.js` (`window.VIS = {draw(c, t, E), pose(t, line)}`) for the teaching pictures — see `youtube/kids-songs/2026-10-09-phases-of-the-moon/visuals.js` (moon drawn accurately for every phase, 8-phase strip, orbit diagram, 29½-day calendar).
   - Build + check + render:
     ```bash
     python3 .claude/skills/yt-kids-song/scripts/build_song.py <dir> "<Title>" <bpm> <first-beat-s>
     node .claude/skills/yt-kids-song/scripts/stills.cjs <dir>/video.html <outdir> 5 20 40 ...   # look at them
     .claude/skills/yt-produce/scripts/render_chunks.sh <dir> <seconds> <workdir> 8 4 song.mp3 <name>.mp4
     ```
### Tamara as her real picture (photo puppet, free, default look)
`templates/tamara-photo.js` animates Sam's own Tamara picture (`tamara-reference.webp`) instead of the code-drawn one. It is one smooth WebGL warp of the whole picture, never cut-out pieces (Sam rejected the cut-out jaw and bouncing cut-out as "scary"): hip sway from planted feet, knee dip on the beat, breathing, head tilt fading through the neck, hair ends swinging, blinks using her real eyelid skin, and lips that part while singing (opening below the upper teeth, tapering into the corners, max ~9 px). Build with host `photo`:
```bash
python3 .claude/skills/yt-kids-song/scripts/make_photo_puppet.py tamara-reference.webp <song-dir>   # once per picture
python3 .claude/skills/yt-kids-song/scripts/build_song.py <song-dir> "<Title>" <bpm> <beat0> photo
```
Limits: one picture = one pose (arms stay where they are in the picture). For waving, pointing, cheering etc., Sam makes more pictures of Tamara in the same tool he made this one (same style, plain cream background, full body), and each gets its own cutout + landmarks; the engine can then switch poses per line. Landmarks (feet, neck, chest, `split` = bottom edge of the upper teeth, eyes) are per picture; check mouth close-ups with stills before a render. `build_song.py` embeds the cutout as `tamara-cutout.js` because WebGL refuses file:// textures.
   - No photos of real children, no real people.
5. **Thumbnail** (`yt-thumbnail`, layout `face` with a character cut-out): big topic word + one picture (e.g. 8 moons in a row). Max 3 words.
6. **Upload** (`yt-publish`): `upload.json` must include `"made_for_kids": true`. Title pattern `The {X} Song | {Learn X} | Kids Learning Songs`. Category 27 (Education).
7. **Compilation** every 4 songs: `ffmpeg concat` of the finals into a 30–60 min video titled `{Topic area} Songs for Kids | 30 Minutes of Learning`. Compilations bring most of the watch hours.

## Made for Kids: what it changes
- Required by law (COPPA) and YouTube policy for content aimed at children; mislabelling risks FTC fines.
- No personalised ads → RPM is low (often under $1–2). The channel wins on volume, replays and compilations, not RPM.
- No comments, no notification bell, no end screens, cards or Stories. Grow through search titles, playlists and compilations.
- Extra income: release the songs on Spotify/Apple Music through a distributor (only for songs made on a paid Suno plan; check Suno's current distribution terms), and later merch.

## Quality rules (YouTube's kids quality principles and the mass-produced content policy)
- Every song must teach something real and correct. "Low-quality, mass-produced" kids videos lose monetization.
- No scary, violent or gross-out content, no fake versions of famous kids' characters, no clickbait thumbnails.
- Each video is different: new lyrics, new pictures, a new teaching idea. Don't re-upload the same song with a different colour.
- The human checkpoint (ASSISTANT.md) for this channel also checks: lyrics are age-appropriate, facts correct, words readable on a phone, nothing a parent would object to.
