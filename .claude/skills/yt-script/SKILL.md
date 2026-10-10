---
name: yt-script
description: Write a researched, sourced 15–20 minute faceless YouTube script as a scene-by-scene script.json for the yt-produce engine, plus episode.json, sources.md, thumbnail.json and 3 title options; then lint it and produce the fact-check list. Use for "write the script", "script this topic", the Writer routine, or any long-form faceless episode.
---

# yt-script: from approved topic to a script ready to produce

An episode folder: `youtube/<channel-slug>/<YYYY-MM-DD>-<topic-slug>/`

| file | what |
|---|---|
| `script.json` | the scenes ("beats"): `[{ "say": "narration", "v": { "t": "<scene type>", ...fields } }]` |
| `episode.json` | channel settings for this video (copy `format` from the niche file) |
| `sources.md` | every source used, with links and what it supports |
| `thumbnail.json` | 2 variants for yt-thumbnail (`thumbnail.json`, `thumbnail-b.json`) |
| `titles.md` | 3 title options + the chosen one |
| `FACTCHECK.md` | written by the checker, ticked by the human |

## 1. Research (before writing a word)
- Read at least 4 independent sources: company or official history pages, reputable press, books, filings, academic or museum pages. Use web search and fetch. Note every number, date, name and quote with the source that supports it, in `sources.md`.
- Two sources disagree? Say so in the script ("estimates range from…") or leave the claim out.
- Never invent quotes, numbers or dialogue. Paraphrase quotes unless a primary source has the exact words.
- Finance, health or legal topics (YMYL): stick to facts and general education, never advice ("not financial advice" in the description). These niches pay the most and get the most scrutiny.

## 2. Structure for 15–20 minutes (about 2,300–3,100 words at ~155 wpm)

| part | time | job |
|---|---|---|
| Cold open | 0:00–0:30 | The most surprising fact or moment, as a scene, not an intro. No "welcome back". |
| Promise | 0:30–0:50 | What they'll know by the end, plus a title card. |
| Chapters (5–8) | ~2–3 min each | Each opens with a chapter card and a question, and ends on an open loop into the next ("but that success nearly killed them"). |
| Midpoint reset | ~50 % | A pattern interrupt: a big stat, a quote, or "here's what most people get wrong". |
| Payoff | last 2 min | Answer the cold open, give the lesson, then what happened next. |
| End card | 15 s | Like + subscribe + the next video (`end` scene, `"outro": true`). |

Retention rules:
- The visual changes every 6–20 seconds. A scene longer than 25 s needs splitting.
- No 3 identical scene types in a row.
- Something concrete on screen for every abstract sentence: a year, a number, a photo, a list.
- Write for the ear: short sentences, one idea each, and numbers spoken the way people say them ("about a hundred billion").
- Run the narration through `ig-human` rules (no AI slop words, no em dashes in on-screen text).

## 3. Scene types (fields)

| type | use | fields |
|---|---|---|
| `photo` | story narration over a full-bleed photo (the workhorse in histories) | `bg` (photo), `title`, `kicker?`, `caption?` |
| `year` | dates/eras: counts up to the year | `year`, `from?`, `label`, `kicker?`, `bg?` |
| `title` | episode title card | `kicker`, `title`, `badge`, `bg?` |
| `chapter` | chapter card (numbered, light sweep) | `n`, `title`, `label?` (default from episode), `bg?` |
| `bigtext` | one punchline | `text`, `kicker`, `hl?` (words to highlight), `bg?` |
| `stat` | a number that counts up | `num`, `suffix`, `label`, `source?`, `bg?` |
| `quote` | quote typed in | `text`, `who` |
| `compare` | then vs now, A vs B | `title`, `left {head, rows[]}`, `right {head, rows[]}` |
| `list` | 2–7 items, optional side photo | `title`, `items[]`, `photo?`, `bullets: false?` |
| `timeline` | 3–5 dated marks | `title`, `marks [[top, label]...]`, `bad?`, `bg?` |
| `agenda` | "in this video" | `items[]`, `photos[]?`, `title?` |
| `steps` | build a list across several beats (same `title`) | `title`, `items[]` (cumulative), `of` |
| `flow` | process A→B→C | `title`, `nodes[]`, `bg?` |
| `scenario` | situation with a highlighted line | `title`, `lines[]`, `hl`, `bad?`, `photo?`/`icon` |
| `tools` | 4 named tools/brands | `items [[name, note]...]`, `title?`, `bg?` |
| `warning` | mistake/myth | `title`, `text` |
| `chat`, `email`, `notes`, `invoice`, `calendar`, `split`, `pick`, `roadmap` | how-to channels | see the engine template |
| `end` | like/subscribe/next | `next`, `outro: true` |

- **Photos:** write `"bg": "q:search words"` (or `photo`/`photos`). yt-produce fetches licence-safe photos (Pexels with a key, else CC0 Openverse). Search for **scenes**, not brands or people: "1960s running track", "factory floor", "stock market screen". Aim for photos on 40–60 % of scenes.
- **Presenter:** `"gia": "worried"` on a scene forces Gia's pose; `"gia": false` hides her there.

## 4. episode.json

```json
{"title": "The ENTIRE History of Nike in 18 Minutes", "brand": {"name": "BRAND HISTORIES", "initial": "B", "display": "Brand Histories"},
 "chapterLabel": "CHAPTER", "voice": "af_heart", "speed": 0.93, "music": "lofi-business-85bpm.mp3", "music_db": -20,
 "presenter": false, "colors": {"teal": "#12A4AE", "amber": "#FFB547"}}
```

## 5. Check, then hand over

```bash
python3 .claude/skills/yt-script/scripts/check_script.py <episode-dir> --target-min 15 --target-max 20
```

- Fix every FAIL and most WARNs.
- `FACTCHECK.md` lists every sentence with a number, date, name, record or quote. That's the human's fact-check list.
- A script is ready only when the checker passes and a human has ticked `FACTCHECK.md`.
- Titles: the niche's format first; one curiosity variant; one using the top autocomplete phrase from the scout report. Under 60 characters where possible.

## Never
- No copying a competitor's script, structure word for word, or narration. Use them for gaps, not text.
- No real people's likeness in generated images. No claims about living people without solid sources.
- No mass-producing near-identical scripts with swapped names. Each episode needs its own research and angle, or YouTube's "inauthentic content" rule demonetizes the channel.
