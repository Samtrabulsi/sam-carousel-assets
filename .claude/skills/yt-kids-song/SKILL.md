---
name: yt-kids-song
description: Make educational songs for the kids channel (ages 4-8, school topics) — lyrics that teach one idea, a Suno song made from them, a bright cartoon lyric video timed to the vocals, Made-for-Kids upload settings, and 30-60 min compilations for watch hours. Use for "kids song", "make a song about X for kids", "nursery rhyme", "learning song", the kids channel, or when a routine picks up a card on the Kids learning songs channel.
---

# Kids learning songs

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
3. **Lyric timing** → `words.json`: word start/end times. Align the lyrics to `vocals.wav` with a Whisper word-timestamp tool (faster-whisper / stable-ts `align`). Check: each line starts within 0.15 s of the sung word.
4. **Video**: 1920×1080 cartoon lyric video rendered with the `code-motion-video` engine (deterministic canvas, `record.mjs`, chunked render as in `yt-produce`).
   - The kids engine template (`templates/kids-engine.html`) gets built with the first song. Spec: bright flat colours, 2 recurring original characters drawn in code (same method as Gia in `cartoon-presenter`), one big scene per line, the current word lights up and bounces as it's sung, fact pictures drawn as simple shapes (moon phases, plant parts), a sing-along banner on choruses.
   - Characters bounce on the beat (bpm from the niche or detected from `song.mp3`).
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
