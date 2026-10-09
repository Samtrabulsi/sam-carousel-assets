---
name: yt-automation
description: Run Sam's multi-channel faceless YouTube business end to end — niche configs, the Notion production board, the 5 scheduled routines (Scout, Writer, Producer, Publisher, Analyst), the human checkpoints, and setup. Use when Sam or the assistant asks to run/set up the YouTube automation, start a new channel/niche, check the pipeline, "what's in the queue", or when any routine fires.
---

# yt-automation: the YouTube production system

```
Scout (Mon) ─▶ Idea cards ─▶ [assistant approves 3/channel] ─▶ Writer ─▶ Scripted
   ─▶ [assistant fact-checks FACTCHECK.md] ─▶ Producer ─▶ private upload/preview ─▶ Rendered
   ─▶ [assistant watches + approves] ─▶ Publisher (schedules) ─▶ Published ─▶ Analyst (Fri) ─▶ Scout
```

| piece | where |
|---|---|
| Skills | `yt-scout`, `yt-script`, `yt-produce`, `yt-thumbnail`, `yt-publish`, `yt-analytics`, plus `background-music`, `cartoon-presenter` |
| Niche configs | `.claude/skills/yt-automation/niches/<slug>.json` (queries, candidates, format, voice, music, brand, cadence) |
| Kids songs channel | `niches/kids-songs.json` uses `yt-kids-song` instead of yt-script/yt-produce. The Writer writes lyrics; the Suno song is a **manual assistant step** (no API), so the card waits at Scripted until `song.mp3` + `vocals.wav` are in the folder. Uploads set Made for Kids. |
| Episode folders | `youtube/<channel-slug>/<YYYY-MM-DD>-<topic-slug>/` in this repo (scripts, sources, thumbnails, results; videos stay out of git except small previews) |
| Production board | Notion **YouTube Production Pipeline**: https://app.notion.com/p/c81dad5c44f34bd9b9df97beb7da1f11 (data source `collection://e447cd9f-2973-4568-b7e6-1b4aa5175783`) |
| Assistant checklist | `ASSISTANT.md` in this folder |

## Board statuses (one card per video)
`Idea → Approved → Scripted → Fact-checked → Rendered → Approved to publish → Scheduled → Published` (or `Rejected`).

- **Routines only move cards they own.**
  - Scout: creates Idea cards
  - Writer: Approved → Scripted
  - Producer: Fact-checked → Rendered
  - Publisher: Approved to publish → Scheduled
  - Analyst: fills Views 7d / Avg % watched on published cards
- **Humans own the two quality gates.** Only a person sets `Fact-checked` and `Approved to publish`. A routine never sets them, and never publishes a card that isn't `Approved to publish`.

## The 5 routines
Each is a scheduled Claude Code routine (fresh session each run, on the repo's main branch, with the Notion connector). Every run starts with:
`source .claude/skills/yt-produce/scripts/setup.sh`.

Each routine:
- commits its outputs on a branch named `yt/<routine>-<date>`
- pushes, and merges or opens a PR per repo policy
- updates the cards
- ends with a 5-line summary

| routine | schedule | prompt (store it verbatim in the routine) |
|---|---|---|
| **Scout** | Mon 07:00 | "Use yt-automation + yt-scout. For each niche file with a channel in its cadence: run scout.py, save the report to `youtube/<slug>/research/`, then add the 3 best topics not covered in the last 8 weeks as Idea cards on the YouTube Production Pipeline board (Title = working title in the niche format; Angle; Evidence = outlier links + autocomplete phrase; Competition; Channel). Don't create duplicates of existing cards." |
| **Writer** | daily 08:00 | "Use yt-automation + yt-script. For up to 2 cards in status Approved: create the episode folder, research with web sources, write script.json (15–20 min), episode.json from the niche format, sources.md, titles.md, thumbnail.json + thumbnail-b.json, upload.json. Run check_script.py until it passes. Set the card to Scripted with the folder path, and write in Notes for assistant: 'Fact-check FACTCHECK.md (N claims)'." |
| **Producer** | daily 10:00 | "Use yt-automation + yt-produce. For up to 2 cards in status Fact-checked (check FACTCHECK.md is fully ticked; if not, move the card back to Scripted with a note): run produce.sh, look at stills-sheet.jpg and fix any broken scene before the full render, make both thumbnails, upload privately with publish.py (if the channel's OAuth secret exists; otherwise commit preview-720p.mp4), set Preview = the private YouTube or GitHub link and status Rendered." |
| **Publisher** | daily 14:00 | "Use yt-automation + yt-publish. For cards in status Approved to publish: schedule with `publish.py --schedule-existing --publish-at <next free slot in the niche cadence>` (or a full upload if not uploaded yet). Set YouTube URL, Publish at, status Scheduled. Mark past-dated Scheduled cards Published." |
| **Analyst** | Fri 16:00 | "Use yt-automation + yt-analytics. For every niche with a channel_url: run analytics.py, save the report, update Views 7d / Avg % watched on published cards, and append 3–5 decisions to the report (what to make more/less of) for next Monday's Scout. Summarise per channel." |

**Creating them:** use the `create_trigger` tool with `create_new_session_on_fire: true`, the cron in the user's time zone (ask), and `connectors: ["Notion"]`. Only create them after:
- the skills are merged to `main` (routines check out the default branch)
- the setup checklist below is done

## Setup checklist (one time)
1. Merge the skills to `main`.
2. Google Cloud project + `YT_API_KEY` + per-channel `YT_OAUTH_<SLUG>` secrets, and request the API audit (yt-publish).
3. Optional `PEXELS_API_KEY` (free at pexels.com/api): better photos than CC0 alone.
4. Fill each niche's `channel_url` once the channel exists. Create new channels as YouTube **brand accounts** owned by Sam, with the assistant added as Manager.
5. Share the Notion board with the assistant.
6. First episode per channel goes through the pipeline manually (in a session), so any problems surface before the routines take over.

## Starting a new niche
- Copy a niche file and set queries/candidates, format, brand, colours, voice, cadence.
- Run yt-scout once, then make 3 pilot episodes.
- Keep going only if the pilots' average % watched is ≥ 30 % after 2 weeks.
- One new channel at a time; each needs 6–12 months to reach monetization (1,000 subs + 4,000 public watch hours/year).

## Guardrails (protect monetization)
- **Every video gets its own research and angle.** Reused or templated content ("inauthentic content") gets channels demonetized.
- Never depict real people with AI. No defamation, and no unverified claims about living people or companies.
- YMYL niches (finance, health, legal): education only, with a disclaimer.
- Music, photos and fonts: only licensed sources; record them per episode.
- Routines never publish without a human `Approved to publish`.
- Secrets live only in environment settings; never in the repo or in Notion.
