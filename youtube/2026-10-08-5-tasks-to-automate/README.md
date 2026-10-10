# Pilot video: 5 Tasks to Automate First

**Files**
- `5-tasks-to-automate.mp4`: final video, 1920x1080, about 71s, with voiceover
- `thumbnail.jpg`: 1280x720
- `video.html` / `thumbnail.html`: source (edit and re-render)
- `voiceover.mp3`: vidIQ voiceover, voice "Eric - Smooth, Trustworthy"

Re-render:
```bash
ffmpeg -y -i voiceover.mp3 -af "adelay=300|300,apad=pad_dur=2" -ar 44100 vo_padded.wav
node ../../.claude/skills/code-motion-video/scripts/record.mjs video.html 5-tasks-to-automate.mp4 --w 1920 --h 1080 --fps 30 --sec 71 --audio vo_padded.wav
```

## Upload copy

**Title:** 5 Tasks Every Small Business Should Automate With AI (Start Here)

**Description:**
AI automation for small business doesn't have to mean a big tech project. These are the 5 tasks to hand to AI first, in the order most owners get the fastest win:

00:00 The hours you're losing every week
00:09 1. Answering the same questions (AI website chat)
00:21 2. Automatic follow-ups
00:31 3. AI meeting notes
00:41 4. Invoices and payment reminders
00:48 5. Turning one post into a week of content
00:56 Where to start

Pick the one that eats most of your time and automate it this week. Next video: setting up #1 step by step.

**Tags:** ai automation for small business, ai for small business, ai tools for small business, business automation, ai automation for beginners, ai for business owners, small business tips, ai workflow automation

**Upload settings:** turn on "Altered or synthetic content" if YouTube asks about realistic AI content. Not strictly required for animated graphics, but the voice is AI, so disclose it.

## Niche research (vidIQ, 2026-10-08)

| Niche / seed keyword | Est. monthly searches | Competition (0–100) | Trend vs 30-day baseline |
|---|---|---|---|
| ai automation for small business | 55.9K | 33 (low) | +100% |
| ai automation for beginners | 69.4K | 32 (low) | −23% |
| ai automation for business | 45.4K | 47 | +133% |
| ai tools for small business | 77.4K | 48 | +38% |
| ai workflow automation | 64.0K | 39 | +15% |
| personal finance for beginners | 254K | 37 | +4% |
| finance explained | 558K | 39 | +15% |
| everyday things explained | 92.9K | 28 | +20% |

**Small channels with breakout videos (last 6 months):**
- AI/tech explainers: Mido Explained (12K subs, 253K views, "How Amazon uses 1 million robots"), TES Data (5K subs, 403K views), Cool Dude Explains (13K subs, 195K views, "10 powerful AI sites")
- Finance explainers: Carl Invests (5.4K subs, 111K views), The Money Professor (4K subs, 63K views), Old Man Miller Finance (635 subs, 25K views)

**Decision:** AI and automation for small business owners.
- Search demand roughly doubled in the last month, and competition is low.
- Advertisers pay a lot to reach this audience (software and business).
- It fits the agency, so viewers can become clients.
- Backup niche: personal finance explainers (bigger demand, but more crowded, and finance advice gets stricter scrutiny from YouTube).

## Weekly pipeline (target)

1. Mon: pull keyword and outlier data (vidIQ), pick 3–4 topics
2. Claude writes scripts → voiceover → motion video → thumbnail
3. Sam reviews each video (~15 min) before it's scheduled
4. Cut 2–3 Shorts from each long video
5. Fri: check analytics, feed the winners back into topic picks
