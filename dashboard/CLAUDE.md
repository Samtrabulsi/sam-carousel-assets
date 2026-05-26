# CLAUDE.md — Brand Victory Operations Dashboard

This file captures the design system and hard rules for the dashboard. Apply it
automatically to every file in this `dashboard/` folder.

## Hard rules
1. **Secrets never touch code or chat.** All keys live in `dashboard/.env`
   (git-ignored). Read them server-side only. Never inline a token, never echo
   one back.
2. **Instagram = my own accounts only** (`@samtrabulsi`). This is not a tool for
   scraping other people or my audience.
3. **Local only.** Runs on my laptop via `node server.js`. No hosting, no deploy.
4. **Premium dark software feel** — blue on near-black, gold used sparingly.

## Design tokens (use exactly these)

| Token            | Value                                | Use                                  |
|------------------|--------------------------------------|--------------------------------------|
| Background       | `#0A0A0F`                            | Page background                      |
| Panel            | `#121218`                            | Card / panel background              |
| Primary action   | `#2D4FE8` (royal blue)               | Buttons, links, active states        |
| Primary light    | `#5B79F0`                            | Hover, accents                       |
| Highlight        | `#E8B53A` (gold)                     | Big numbers, key stats, dividers     |
| Body text        | `#EDEDF2`                            | Paragraph / UI text                  |
| Dim text         | `#9A9AA8`                            | Secondary / labels                   |
| Heading text     | `#FFFFFF`                            | Page titles, headings                |
| Card border      | `rgba(255,255,255,0.09)` (1px)       | All panels                           |
| Card fill        | very faint white wash                | All panels                           |
| Card radius      | `14px`                               | All panels                           |
| Heading font     | **Playfair Display** (700–900)       | Page titles, big numbers             |
| Body / UI font   | **DM Sans**                          | Everything else                      |
| Buttons          | Pill shape; primary = blue fill, secondary = outline | —                  |

These are wired up as CSS custom properties in `assets/styles.css`
(`--bg`, `--panel`, `--blue`, `--blue-light`, `--gold`, `--text`, `--dim`,
`--heading`, `--border`, `--radius`). Use the variables, do not hard-code hex
values in individual pages.

## Architecture
- Plain HTML files, one per page, all sharing `assets/styles.css` and
  `assets/app.js`. No build step.
- `assets/app.js` renders the shared sidebar nav into `#nav-root` and provides
  the `Store` localStorage helper used by every page.
- `server.js` is a zero-dependency Node server (built-in `http` + global
  `fetch`). It serves the static files and exposes three API routes:
  - `POST /api/instagram/refresh` — Apify Instagram profile scrape (own account).
  - `POST /api/competitors/refresh` — public profile-level metrics for a named
    list (user-authorized benchmarking; never harvests audience data).
  - `POST /api/script/generate` — draft script in my voice, with `brand-voice.md`
    injected as context (read fresh each request, so edits apply without restart).
- `brand-voice.md` holds my distilled voice + frameworks; it drives script quality.
- Persistence is `localStorage` (see `DATA_KEYS` / `Store` in `assets/app.js`),
  including dated metric `history` for trends and a JSON export/import backup.

## My script voice
Direct, no fluff, no preamble. Structure: **Hook → body that teaches one clear
thing → call to action.** Tight and recordable. The draft is a starting point —
I am always the final editor.
