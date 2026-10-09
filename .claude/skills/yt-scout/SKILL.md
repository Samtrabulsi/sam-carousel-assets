---
name: yt-scout
description: Find proven YouTube video topics for a faceless channel without paid tools — outlier videos (views far above the channel's norm), what people type into YouTube search, and per-topic demand vs competition. Use for "find topics", "what should the channel make next", "research this niche", "is this topic saturated", the weekly Scout routine, or before writing any yt-script.
---

# yt-scout: topic research with free tools

Runs on **yt-dlp** (open source, reads public YouTube search and channel pages) and **YouTube autocomplete**. No vidIQ credits needed. Optional: the free **YouTube Data API key** (`YT_API_KEY` env) adds upload dates.

## Run

```bash
python3 -m pip install -q --user yt-dlp        # once per machine/session (yt-produce/scripts/setup.sh does it)
python3 .claude/skills/yt-scout/scripts/scout.py .claude/skills/yt-automation/niches/<niche>.json \
  --out youtube/<channel>/research/$(date +%F)-scout.md --json youtube/<channel>/research/$(date +%F)-scout.json
```

It takes about 2 minutes for 5 queries and 18 candidates. Niche files live in `yt-automation/niches/`. Each has `queries` (how viewers search), and optionally `candidate_template` + `candidates` (the topic list to rank).

## Reading the report

- **Outliers (×)**: video views ÷ the channel's median views over its last 30 uploads.
  - **≥3× on a channel under 100K subs** means the *topic* pulled the views. That's the strongest signal.
  - Big media channels (PBS, CNBC) show what the audience wants, but not what a new channel can win.
- **Candidate topics** are ranked by opportunity: proven demand (best existing video, autocomplete phrases) divided by competition (videos already over 100K).
  - It's a heuristic. Open the top 3 results for a topic before committing.
  - Prefer topics where the strong videos are old, short, or low quality.
- **Autocomplete phrases** are real searches. Use them for titles and angles ("dark history of walmart", "the true history of…").

## Pick topics (what the Scout routine posts as Idea cards)

For each pick, write:
- the topic
- the angle (what makes ours different: newer, deeper, a story angle)
- the evidence (2–3 outlier links and the autocomplete phrase)
- the competition level
- a working title in the niche's format

Pick 3 per channel per week, and avoid repeating a topic covered in the last 8 weeks (check the channel folder).

## Limits and etiquette
- Cloud servers hit YouTube's bot check on full **video** pages (upload dates, descriptions, transcripts). Search and channel listings work. Get dates and details from the free Data API key instead (10,000 units/day; one video lookup costs 1 unit per 50 videos).
- Keep it light: a few hundred lookups a week. The script sleeps between channel scans and retries empty searches.
- Study competitors to find gaps. Never copy scripts, titles word for word, or thumbnails.
