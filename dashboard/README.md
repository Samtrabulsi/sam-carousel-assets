# Brand Victory Operations Dashboard (v1 — Instagram)

A local command center for the content operation. Runs on your laptop, in your
browser — not hosted anywhere. Instagram only in v1 (TikTok/YouTube come later).

## Pages
- **Command Center** (`dashboard.html`) — headline metrics + performance chart.
- **Content Pipeline** (`pipeline.html`) — drag-and-drop board: Idea → Scripted → Recorded → Scheduled → Published.
- **Content Research** (`research.html`) — capture ideas, push them into the pipeline.
- **Performance** (`performance.html`) — Instagram metrics in detail.
- **SOP Library** (`sops.html`) — saved processes.
- **Tasks** (`tasks.html`) — to-do list.

Everything you enter is saved in the browser's local storage, so the pipeline,
ideas, SOPs, tasks, saved scripts, and last Instagram numbers survive a refresh.

## Run it

```bash
cd dashboard
cp .env.example .env      # then paste your tokens into .env (see below)
node server.js            # or: npm start
```

Open **http://localhost:4000** in your browser.

No `npm install` is needed — the server uses only built-in Node modules
(Node 18+). Check your version with `node --version`.

## Secrets (.env)

Two optional tokens unlock the live features. Both go in `dashboard/.env`, which
is git-ignored. **Never paste a token into chat or into the code.**

| Variable            | Powers                              | Where to get it                                  |
|---------------------|-------------------------------------|--------------------------------------------------|
| `APIFY_TOKEN`       | "Refresh Instagram" button          | Apify → Settings → Integrations → API            |
| `ANTHROPIC_API_KEY` | "Generate Script for IG" button     | console.anthropic.com (falls back to `claude` CLI) |

The dashboard works without these — pages render with placeholder numbers and
the live buttons show a clear message until the tokens are present.

## How the live features work

**Refresh Instagram (Phase 4).** Calls the Apify actor
`apify/instagram-profile-scraper` for `@samtrabulsi` (an account you control),
server-side, using `APIFY_TOKEN`. It pulls followers, post count, recent-post
engagement, and an engagement rate. Instagram profile scrapes are typically a
small fraction of a cent per run; check current pricing on the actor's Apify
page before relying on it heavily. Reach is approximated from recent-post
engagement, since public scrapes don't expose true reach (that needs the
official Graph API — the documented v1→v2 upgrade path).

**Generate Script for IG (Phase 5).** Sends the idea title/notes to Claude and
returns a draft in Sam's voice — Hook → teach one thing → CTA — that you edit
in place before saving. Saving moves the card to **Scripted**.

## Design system
See `CLAUDE.md` for the full token list. Tokens live as CSS variables in
`assets/styles.css`; the shared nav and storage helpers live in `assets/app.js`.
