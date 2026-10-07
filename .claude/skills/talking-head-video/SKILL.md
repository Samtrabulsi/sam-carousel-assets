---
name: talking-head-video
description: Turn a headshot + script into a lip-synced talking-head video (photo → speaking person). Use when Sam asks for a talking-head, avatar, "make this photo speak", spokesperson clip, video version of a LinkedIn post, or a client explainer video from a headshot (e.g. a doctor explaining a treatment).
---

# Talking-head video from a photo

Pipeline: **script → voiceover → photo + audio → lip-synced video → captions/brand → deliver**.

## 0. Confirm before starting

Ask only for what's missing:
- **Whose face?** Must be someone who consented (Sam, team member, client with written OK). Refuse to animate anyone else.
- **Voice:** Sam's real recording, or AI voice? If cloning a real person's voice, that person must consent.
- **Length & platform:** Reel/TikTok/Shorts (9:16, 15–45s), LinkedIn (1:1 or 4:5, 30–90s), or website (16:9).
- **Language:** English or Arabic (Sam publishes both; Arabic voice must be natural, not transliterated).

## 1. Script

- Hook in first 2 seconds, one idea, one CTA. ~2.5 words/second → 30s ≈ 75 words.
- If adapting a LinkedIn post or carousel from this repo, pull its core line and rewrite for speech (short sentences, no lists).
- Show Sam the script before generating audio.

## 2. Voiceover

- Real recording: ask Sam to upload a clean WAV/MP3 (quiet room, no music).
- AI voice: use Runway — load `mcp__Runway__search_voices` and `mcp__Runway__generate_speech` via ToolSearch, pick a voice matching the person, generate, poll with `mcp__Runway__get_task`.

## 3. Photo → talking video (pick one route)

| Route | When | Notes |
|---|---|---|
| **Runway** (default) | Client deliverables, need 1080p, fast | Call `mcp__Runway__whoami` first, then check available models in `generate_video` / workflows for an audio-driven or character/lip-sync option. Image-to-video with the headshot as `startFrame` + audio-capable model if no dedicated lip-sync model is listed. |
| **LongCat-Video-Avatar 1.5 demo** (free) | Quick quality test | HF Space `victor/LongCat-Video-Avatar-1.5`: ~5s, ~480p, queue/quota. Sam uploads the photo + audio in the browser. See the `longcat-video` skill. |
| **LongCat self-hosted** | Long single take (minutes), high volume | Needs rented GPU; see `longcat-video` skill. |

Headshot requirements: front-facing, shoulders up, even lighting, mouth closed/neutral, no hands near face, ≥1024px, plain background.

## 4. Quality check before delivering

Watch the whole clip for: lip-sync drift, teeth/tongue artifacts, eye/identity drift over time, warped hands or jewelry, frozen background, audio pops. Regenerate or trim bad segments — never ship a clip Sam hasn't seen.

## 5. Finish & deliver

- Add burned-in captions (most viewers watch muted) and Sam's/client's branding.
- Disclose AI-generated video where the platform or client requires it.
- Deliver to Sam; optionally schedule via `/schedule-post` or Metricool, and log in Notion like other content.
