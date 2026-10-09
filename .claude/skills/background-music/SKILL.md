---
name: background-music
description: Add a background music bed under a narrated video (YouTube episodes, explainers, Reels) — get a royalty-free track, loop it to length, duck it under the voice and normalise loudness. Use when Sam asks for background music, a soundtrack, "add music", "the video feels empty/flat", music ducking, or royalty-free music for a video.
---

# Background music for narrated videos

## Where the track comes from (in order)

1. **Saved library first**: `youtube/music/` in this repo. Reuse a track the channel already has, so episodes sound consistent and cost nothing.
   - `lofi-business-85bpm.mp3`: 178 s, warm lofi (e-piano, soft bass, brushed drums). Generated with vidIQ 2026-10-09; original and royalty-free.
2. **vidIQ music generator** (`vidiq_generate_music`, 25 credits per track, up to 180 s, returns WAV). Prompt pattern: genre + mood + instruments + tempo + "loop-friendly ending" + "Instrumental". Save every new track to `youtube/music/<style>-<bpm>bpm.mp3` with a line in this file.
3. **Runway** `generate_music` when the Runway workspace has credits.
4. **YouTube Audio Library** (Sam downloads it in YouTube Studio → Audio Library; safest for Content ID). Put the file in `youtube/music/`.

Avoid: tracks with unclear licences, anything from a "free music" site that needs scraping. Freesound's CDN refuses direct downloads, so don't work around it. MusicGen weights are non-commercial. ACE-Step 1.5 / Stable Audio Open need a 12 GB+ GPU (not available in cloud sessions).

## Mix it

```bash
.claude/skills/background-music/scripts/mix_music.sh voiceover.wav youtube/music/lofi-business-85bpm.mp3 mix.m4a [bed_db=-20] [xfade_s=4]
ffmpeg -i video.mp4 -i mix.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest final.mp4
```

The script:
- loops the track with 4 s crossfades until it covers the narration
- sets the bed level (default -20 dB)
- fades in over 2 s and out over the last 3 s
- ducks the music under the voice with a sidechain compressor (it comes back up in pauses)
- normalises the mix to **-14 LUFS / -1.5 dBTP**, YouTube's target

For code-rendered videos (`code-motion-video`, `yt-produce`), render the video silent, mix the audio with this script, then mux.

Tested 2026-10-09 on the 9:31 episode: about 80 s to run. The mix measured -14.1 LUFS; music in pauses was about -27 dB, and speech stayed on top at about -17 dB.

## Taste rules
- The music supports the voice; it never competes. If a viewer would notice the music, lower the bed (try -23 dB).
- One track per episode. Same track or same style across a series = channel identity.
- Lower the music or drop it out for stats, warnings and dense steps; bring it up on chapter titles and the end card (optional: split the bed and use `volume` per segment).
- No vocals under narration.

## Guardrails
- Only use tracks we generated, bought or have a clear licence for. Note the source in the episode README.
- If YouTube shows a Content ID claim on a generated track, dispute it with the generation record (vidIQ music ID or Runway task ID). Keep those IDs in the README.
