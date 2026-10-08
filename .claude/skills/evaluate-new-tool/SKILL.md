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

## Guardrails

- Downloaded code is untrusted: own directory, don't run it unless Sam asked to.
- Never put credentials into third-party tools without Sam's OK.
- Face/voice tools: only with consent of the person depicted.
