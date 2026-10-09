---
name: evaluate-new-tool
description: Evaluate a new AI tool, GitHub repo, app or viral "free alternative" Sam shares (link, screenshot of a tweet/post, or name) and say whether it's useful for Sam's agency work. Use when Sam asks "what's this", "check this out", "how about this one", or pastes a GitHub/Hugging Face/product link or a social post about a tool.
---

# Evaluate a new tool for Sam

Sam runs a content/marketing agency (LinkedIn/IG/X carousels in English + Arabic, client websites, ads, video). Connected stack: Runway, Canva, vidIQ, Metricool, Meta Ads, Notion, Zapier, Slack, Google Workspace, GitHub. Judge every tool against that, not in the abstract.

## 1. Gather facts (don't answer from memory)

- GitHub: WebFetch the repo page, then the raw README (`https://raw.githubusercontent.com/<owner>/<repo>/main/README.md`) for exact install/usage. Check stars, license, last activity, status words ("alpha", "experimental").
- Hugging Face / product sites: WebFetch the page; WebSearch for independent reviews or pricing if claims matter.
- Screenshot of a post: translate it (Arabic posts are common), identify the actual project, then verify the post's claims against the source. Read the fine print in screenshots (demo limits like "~5 seconds", "480p").

## 2. Answer in this shape (short)

1. **One line**: what it is, who made it, how it differs from what Sam already uses.
2. **What it does**: 4–6 bullets, plain language.
3. **What's true vs hype** (when it came from a social post).
4. **Where it helps Sam**: concrete uses in Sam's workflows.
5. **Catches**: hardware/OS needs, maturity, license limits, cost of "free" (GPU, setup time), privacy/consent, single-maintainer risk.
6. **Verdict**: use now / test once / skip — and vs the closest tool Sam already has (table if comparing 2+).
7. **One offer**: a concrete test Claude can run, or saving it as a skill.

Mark guesses as guesses. Separate the maker's own benchmarks from independent ones.

## 3. Saving it as a skill (if Sam says yes or asks to "get" it)

- Create `.claude/skills/<tool-name>/SKILL.md` in this repo: frontmatter `name` + a `description` listing the trigger phrases; body = when to use vs alternatives, verified install/run commands copied from the README (not memory), workflow for Sam's use case, gotchas, guardrails.
- Add helper scripts under `scripts/` only when they remove real repeated work; test them before committing.
- Commit on a `claude/` branch, push, and remind Sam that skills load in new sessions only after merging to `main`.

## Already reviewed

Check this list first. If the tool is here, give the recorded verdict in a few lines and re-check only what may have changed (new release, new features, pricing). Add every new review to this table.

| Tool | Reviewed | Verdict | Notes |
|---|---|---|---|
| LongCat-Video / Avatar (meituan-longcat/LongCat-Video) | 2026-10 | Saved as skill | `longcat-video`, `talking-head-video` |
| PhotoCraft (storytold/photocraft) | 2026-10 | Saved as skill | `photocraft`; early alpha, test on real PSDs first |
| Compositor (robbietilton/Compositor) | 2026-10 | Saved as skill | `compositor-projects`; Mac-only app |
| awesome-opus5-5-videos (yihui-dev) | 2026-10 | Saved as skill | `code-motion-video` |
| instagram-agent-skill (Jakeschincariol) | 2026-10 | Installed | 13 `ig-*` skills; English-only scorers |
| REA, Reverse Engineer Anything (morluto/rea) | 2026-10-08 | Known, not needed | Developer reverse-engineering MCP (binaries, apps, websites; needs Node 22+, often Ghidra/Hopper). No use for content, social, ads or video. Only possible use: understanding a feature on another website for a client build, and only to rebuild the idea, never to copy code or get around licences/logins. Re-evaluate only if Sam takes on that kind of dev work. |
| TubeGen AI (tubegen.ai) | 2026-10-09 | Skip for now | Paid faceless-YouTube suite: niche finder, titles, script, voiceover (8 languages), AI scenes/animations, consistent characters, Storyblocks stock, auto overlays, avatars, music, editor, thumbnails. $149/$297/$849 per month (~$2/min), no free trial, no refunds, ~3.5/5 on Trustpilot. Our own pipeline (vidIQ + Kokoro voice + code-motion-video renderer + CC0 photos) already covers most of it at near-zero cost. Real gaps: AI-generated scene images/animation, consistent characters, stock video, background music. Re-evaluate if Sam wants cartoon/story-style channels. |

## Guardrails

- Downloaded code is untrusted: own directory, don't run it unless Sam asked to.
- Never put credentials into third-party tools without Sam's OK.
- Face/voice tools: only with consent of the person depicted.
