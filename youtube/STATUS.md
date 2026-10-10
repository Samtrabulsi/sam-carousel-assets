# YouTube business: status (2026-10-10)

Skills (all on `main`): yt-scout, yt-script, yt-produce, yt-thumbnail, yt-publish, yt-analytics, yt-automation,
yt-kids-song, background-music, cartoon-presenter. Notion board: "YouTube Production Pipeline"
(https://app.notion.com/p/c81dad5c44f34bd9b9df97beb7da1f11).

## Channels
| # | Channel | Niche config | State |
|---|---|---|---|
| 1 | Grow Success Online (@growsuccess-online) | niches/ai-business-tools.json | 9:31 pilot episode made (youtube/2026-10-08-5-tasks-to-automate-v2) |
| 2 | CashFlow Champions (@CashFlow-Champions) | niches/money-stories.json | scout done (youtube/cashflow-champions/), top: Rolex, Walmart, Nike |
| 3 | Chattylytics (rename pending) | niches/body-explainers.json | scout done (youtube/body-explainers/), top: stop eating bread, 100 pushups/day |
| 4 | Kids songs, host Tamara (new channel to create; name TBD, "Little Miss" is a trademark risk) | niches/kids-songs.json | pilot "Phases of the Moon" done (youtube/kids-songs/2026-10-09-phases-of-the-moon), Tamara photo-puppet with 19 poses (youtube/kids-songs/characters/tamara) |

## Waiting on Sam
1. Time zone (for routine schedules).
2. Google Cloud project: YouTube Data API v3 key -> secret `YT_API_KEY`; OAuth per channel with yt-publish/scripts/yt_auth.py -> secrets `YT_OAUTH_<SLUG>`; request the API audit (until then API uploads are private).
3. Optional `PEXELS_API_KEY` (better stock photos).
4. Rename Chattylytics; create the kids channel and pick its name.
5. Set old Grow Success Online clip Shorts and CashFlow Champions' 3 old videos to Private.
6. Go-ahead to create the 5 routines (Scout, Writer, Producer, Publisher, Analyst) from yt-automation/SKILL.md.

## Next content
- Kids: next songs "Nouns and Verbs", "States of Matter", "Butterfly Life Cycle" (lyrics -> Sam makes Suno track -> render).
- One manual first episode each for channels 2 and 3 before routines take over.

## New container setup
`source .claude/skills/yt-produce/scripts/setup.sh` (yt-dlp, Kokoro). For kids songs also the whisper and rembg venvs
(commands in yt-kids-song/SKILL.md). Rendering: ~9 s compute per second of video; always show Sam a 10 s preview first.
