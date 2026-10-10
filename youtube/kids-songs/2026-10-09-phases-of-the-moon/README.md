# Phases of the Moon — Little Miss Tamara pilot

- Song: Suno (Sam's paid plan, account trabulsi_sam), lyrics in `lyrics.md`, facts in `sources.md`. Add the Suno song link here for Content ID disputes.
- Host: Tamara, drawn in code (`.claude/skills/yt-kids-song/templates/tamara.js`), based on `tamara-reference.webp`. Pose sheet: `tamara-pose-sheet.jpg`.
- Lyric timing: `words.json` from `align_lyrics.py` (201/214 words matched). The last two final-chorus lines and the outro were not heard clearly and are spaced like chorus 2 (`"estimated": true`); check the sync from 2:15.
- Tempo: 107.75 bpm, first beat 0.081 s (estimated from the audio).
- Built with: `build_song.py . "Phases of the Moon" 107.75 0.081`, then `render_chunks.sh . 157.63 <workdir> 8 4 song.mp3 phases-of-the-moon.mp4`.
- Thumbnail: `thumbnail.jpg` (from `thumbnail.html`).

Upload (`upload.json`): title "Phases of the Moon Song | Learn the 8 Moon Phases | Little Miss Tamara", `"made_for_kids": true`, category 27.
