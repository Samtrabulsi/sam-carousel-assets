# /schedule-post [topic]

One-command routine to write, render, and schedule a **single post or story** directly into the GoHighLevel Social Planner. Uses the publisher/ CLI built on the Private Integration Token — no MCP, no third-party host, fully repeatable for any client.

> **Need a 7-slide multi-image deck?** Use `/carousel` or `/daily-posts` instead. This routine is for single-image posts and stories.

---

## When to use this

- "Schedule a post tomorrow at 10am Athens about positioning."
- "Send out a story for the day."
- "Drop a quick FB+IG post about why generalists stay broke."

---

## ARGUMENTS

```
/schedule-post [topic]            # all flags optional, asked if missing
  --type post|story               # default: post
  --platforms fb,ig,linkedin,x,tiktok   # default: all valid (FB+IG today)
  --when "YYYY-MM-DD HH:MM [TZ]"  # default: tomorrow 10:00 in client's default tz
  --size ig_portrait|square|story # default: ig_portrait (or story if --type story)
  --client SLUG                   # default: sam-trabulsi
  --dry-run                       # render only, do not schedule
```

If `topic` is omitted, pick from today's domain (see Weekly Rotation below) and avoid the last 14 days in Notion.

---

## CAPTION STYLE — LOCKED (carried over from /linkedin, /carousel)

**Voice:** Direct, conversational, anti-guru tone. No fluff. No emojis unless the topic explicitly warrants one.

**Long CTA (captions end with this verbatim):**
> Comment BRAND or DM BRAND and I'll add you to the Brand Victory Circle — a free community where experts and entrepreneurs learn the latest strategies to build brands and products that actually sell.

**Short CTA (single-image visual, if rendered on the image):** literal `Comment "BRAND"` in a grey box. Nothing else. Never `DM BRAND` on the image.

**Length targets — by platform + type:**

| Type | Platform | Words |
|---|---|---|
| post | Instagram-first | 80–200 (scannable) |
| post | Facebook-first | 60–150 |
| post | Multi (FB+IG) | 80–180 |
| post | LinkedIn solo | 350–600 (note: reconnect LinkedIn first — token expired) |
| story | any | 0–15 (overlay only — captions don't show on stories) |

**Structure (posts):** Hook → Problem → Reframe → Payoff → Long CTA.
**Structure (stories):** Single visual sentence on image. No caption needed.

---

## WEEKLY ROTATION (LOCKED — same as /carousel and /daily-posts)

Used only if `topic` is omitted. Use Sydney day-of-week (Sam's local) unless `--client` overrides.

| Day | Domain | Belief to break |
|---|---|---|
| Mon | Positioning Pain | "My expertise should speak for itself" |
| Tue | Content Delusion | "More content = more clients" |
| Wed | Conversion Gap | "Followers will eventually buy" |
| Thu | Authority / Identity Shift | "I need more credentials first" |
| Fri | Offer / Pricing | "Lower price = more clients" |
| Sat | Proof / Personal Truths | "Results speak for themselves" |
| Sun | System vs Chaos | "I'll systemize it when I scale" |

Full domain reference is in [.claude/commands/linkedin.md](.claude/commands/linkedin.md). Do not reinvent domains here.

---

## EXECUTION CONTRACT

The run is NOT complete unless:
1. An image has been rendered at the correct size
2. The image has been uploaded to GHL media library (real `fileId` returned)
3. A scheduled post exists in the GHL Social Planner queue (confirmed via `verify`)
4. The user has been shown: the rendered image, the caption, the schedule time in both their tz and the location tz, and the GHL post ID

If any step fails, surface the error verbatim — never silently degrade to draft, never skip verification.

---

## STEP 1 — Parse args & confirm

Read the `/schedule-post` arguments. For anything missing, use AskUserQuestion (NOT free-text follow-up) to fill in:

| Missing | Question | Options |
|---|---|---|
| `topic` | "What's the post about?" | One-line topic OR "Pick today's domain" |
| `--type` | "Post or story?" | post (Recommended) / story |
| `--platforms` | "Which platforms?" | FB+IG (Recommended) / FB only / IG only / IG Story (if `--type story`) |
| `--when` | "When should it go out?" | Tomorrow 10:00 location-tz (Recommended) / In 1 hour / Specific date+time / Save as draft |

`--client` defaults to `sam-trabulsi`. Only ask if explicitly handling a different client. For non-Sam clients, the operator must have already run `python -m publisher.cli setup` for that client.

---

## STEP 2 — Resolve topic + belief

If topic was provided: derive the underlying belief being broken (one short sentence) — needed to keep the copy sharp.

If topic was empty:
1. Get today's day of week in `client_cfg.default_timezone` (Athens for Sam)
2. Look up domain from the rotation table
3. Check Notion Carousel Pipeline DB `0b1141db-29f2-4219-b835-024b26c72115` for topics used in the last 14 days
4. Pick a fresh topic within today's domain that matches Sam's ICP (English- or Arabic-speaking coaches, therapists, entrepreneurs)
5. Set: `TOPIC`, `DOMAIN`, `BELIEF`, `SLUG` (kebab-case, ≤50 chars), `DATE_SLUG` (`YYYY-MM-DD` of the scheduled date)

---

## STEP 3 — Choose size preset

| `--type` | `--size` default | Pixel dims | Notes |
|---|---|---|---|
| post | `ig_portrait` | 1080×1350 | Current best IG reach (4:5). Letterboxes slightly on FB — acceptable. |
| post + platforms=facebook only | `square` | 1080×1080 | Universal-safe; better FB feed presence than portrait. |
| story | `story` | 1080×1920 | IG/FB story. `post_type` becomes `story`. |
| post + Reel intent | `story` | 1080×1920 | Reels use the same vertical canvas. `post_type=reel`. |

The user can override with `--size` explicitly.

---

## STEP 4 — Write caption + on-image text

### Caption (post only, skip for stories)

Write Sam-voice copy at the length target from the locked rules. Structure:

1. **Hook** — first line. Make the reader feel exposed (e.g. "Polished isn't the same as positioned.")
2. **Problem** — 2–4 lines naming the pain
3. **Reframe** — flip the false belief
4. **Payoff** — short line
5. **Long CTA verbatim** (see above)
6. **Hashtags** — 3–5 max, lowercase or PascalCase, brand-relevant only. No `#fyp` spam.

### On-image text (always)

- **Topline label** — e.g. `POSITIONING · BRAND VICTORY` (use today's `DOMAIN` upper-case)
- **Eyebrow** — short framing line, e.g. "The Authority Gap"
- **Headline** — the hook, max 6–8 words, all caps, accent the last word in `#C17A5A`
- **Subline** — one sentence explaining the hook
- **Footer left** — `Brandvictory.com`
- **Footer right** — `@samtrabulsi`

For **stories**: just the headline + a short subline. No subline overflow. Footers optional.

---

## STEP 5 — Build the HTML

Write the file at:
- Posts: `output/{DATE_SLUG}-fbig-{SLUG}.html`
- Stories: `output/{DATE_SLUG}-story-{SLUG}.html`

The HTML MUST declare its dimensions to match the chosen size preset:

```css
html, body, .frame {
  width:  1080px;
  height: 1350px;   /* match the preset: 1350 for ig_portrait, 1080 for square, 1920 for story */
}
```

**Reference template:** [output/2026-05-21-fbig-polished-vs-positioned.html](output/2026-05-21-fbig-polished-vs-positioned.html) — copy its structure (poster-dots, poster-curve, poster-arrow, poster-topline, poster-headline with `.accent`, footers) and adjust dimensions. For stories, scale all sizes up by `1920/1350 ≈ 1.42` and stretch the headline vertically.

**Brand colors (do not invent new ones):**
- `--brand-primary: #C17A5A` (terracotta accent — for headline accent span + topline)
- `--brand-dark: #8B4A2A`
- `--poster-bg: #0B0B0B`
- Font: Plus Jakarta Sans (Google Fonts), 800-weight uppercase for headline

---

## STEP 6 — Dry-run render

Run a dry-run first to verify the image looks right before uploading:

```bash
cd /Users/samtrabulsi/Downloads/carousel-system
python3 -m publisher.cli publish \
  --client {CLIENT_SLUG} \
  --html output/{DATE_SLUG}-fbig-{SLUG}.html \
  --caption "(dry)" \
  --schedule "{WHEN_NORMALIZED}" \
  --platforms {PLATFORMS} \
  --size {SIZE} \
  --post-type {post|story|reel} \
  --dry-run
```

Read the rendered PNG (publisher/.render_cache/{slug}.png) and confirm visually:
- Headline fits inside the frame (no clipped letters)
- Accent word renders in terracotta
- Footers are visible and aligned
- No empty void at the bottom (= HTML dimensions match preset dimensions)

If anything looks wrong, fix the HTML and re-render. Don't move on until the dry-run output is brand-correct.

---

## STEP 7 — Schedule for real

Save the caption to disk first (so the CLI reads it from file, preserving line breaks and special characters):

```
output/{DATE_SLUG}-fbig-{SLUG}-caption.txt
```

Then run the publisher live:

```bash
python3 -m publisher.cli publish \
  --client {CLIENT_SLUG} \
  --html output/{DATE_SLUG}-fbig-{SLUG}.html \
  --caption-file output/{DATE_SLUG}-fbig-{SLUG}-caption.txt \
  --schedule "{WHEN_NORMALIZED}" \
  --platforms {PLATFORMS} \
  --size {SIZE} \
  --post-type {post|story|reel}
```

Capture from the output:
- The uploaded `fileId` (GHL media library)
- The new post ID (if returned)
- The GHL API response

If `create_post` returns a 422 about `userId`, the client's TOML is missing it — re-run `python3 -m publisher.cli setup --client {slug} --token <PIT> --location-id <LOC> --user-id <USER>`.

---

## STEP 8 — Verify

```bash
python3 -m publisher.cli verify --client {CLIENT_SLUG} --status scheduled \
  --from-date {DATE_SLUG}T00:00:00Z \
  --to-date {DATE_SLUG_PLUS_1}T00:00:00Z
```

Confirm exactly 1 post returned for the window with the expected schedule, summary, and account list.

If `verify` returns `[]` even after a successful schedule, that may be the read-endpoint quirk noted in [[ghl-mcp-broken-reads]] — but with the PIT REST path, list_posts should work. If it fails, fall back to asking the user to refresh the Social Planner UI and screenshot.

---

## STEP 9 — Report to user

End the run with a short scannable block:

```
✅ Scheduled

Topic:      {TOPIC}
Domain:     {DOMAIN}
Type:       {post|story}
Platforms:  {PLATFORMS}
Schedule:   {WHEN} (local) = {WHEN_UTC} (UTC) = {WHEN_LOCATION_TZ}
Image:      output/{...}.png  ({KB} KB, {WxH})
Caption:    output/{...}-caption.txt
GHL post:   {POST_ID}
Edit:       https://app.growsuccessonline.com/v2/location/{LOC}/marketing/social-planner/planner
```

Then offer one short prompt: "Want me to log this to Notion?" (yes/no).

---

## STEP 10 — (Optional) Log to Notion

If user says yes, write a row to the Carousel Pipeline DB `0b1141db-29f2-4219-b835-024b26c72115` with:
- Title: `{DATE_SLUG} {TOPIC}`
- Status: `Scheduled` (or `Pending Review` if user wants Rosana to check first — ask)
- Language: `English` (or `Arabic` if topic was generated for AR ICP)
- Output Target: `GHL Social Planner`
- Domain: `{DOMAIN}`
- Caption (full): in body
- Image link: GitHub raw URL after committing the PNG (only if Sam wants the PNG mirrored to GitHub — ask)

---

## FAILURE MODES — handle these explicitly

| Error | Cause | Fix |
|---|---|---|
| `PIT token missing in .env` | Operator hasn't added `GHL_PIT_<SLUG>` | Stop and tell the user — point them at publisher/INSTALL.md step 2 |
| `GHL 401 invalid_token` | Token revoked or wrong client slug | Re-prompt for token, re-run `setup` |
| `GHL 403 scope missing` | PIT lacks required scope | Recreate PIT with all 8 scopes from publisher/INSTALL.md |
| `account_id for linkedin is missing` | Token expired (LinkedIn/X/TikTok common) | Tell user to reconnect in GHL UI → Social Planner → Socials, then re-run `setup` |
| `Image renders with empty void at bottom` | HTML dimensions don't match preset | Fix `width`/`height` in the HTML to match the preset's pixel size |
| `Playwright Chromium not installed` | One-time install missed | `python3 -m playwright install chromium` |
| `userId must be a string` from `create_post` | TOML missing user_id | Re-run setup with `--user-id` |
| Image looks wrong after render | Fonts didn't load before screenshot | Increase `wait_extra_ms` in [publisher/render.py](publisher/render.py) |

Never retry destructively (don't re-schedule the same post twice — verify first). Never proceed past a 4xx without surfacing it.

---

## DO NOT

- Do not call the `ghl-mcp-server` MCP for any read — it's stubbed (see [[ghl-mcp-broken-reads]]). Always use the publisher CLI which routes through PIT + REST.
- Do not host images on catbox.moe or any external host. The publisher uploads bytes directly to GHL via PIT.
- Do not change the long CTA wording or the on-image short CTA. They are locked.
- Do not invent brand colors. Use `#C17A5A`, `#8B4A2A`, `#0B0B0B`, Plus Jakarta Sans.
- Do not ScheduleWakeup with `prompt=/schedule-post` — same trap as [[no-self-wakeup-in-daily-posts]].
- Do not skip the dry-run step. The publisher renders before uploading; the dry-run catches layout bugs cheaply.
- Do not log credentials anywhere. Token lives in `.env`, never in Notion / commits / chat output.

---

## QUICK REFERENCE — the whole flow in one block

```bash
# 0. Prereqs (one time per client)
#    See publisher/INSTALL.md to create the PIT and run `setup`.

# 1. Render preview (no upload)
python3 -m publisher.cli publish \
  --client sam-trabulsi \
  --html output/2026-05-22-fbig-clarity-beats-credentials.html \
  --caption "(dry)" \
  --schedule "2026-05-22 10:00 Europe/Athens" \
  --platforms facebook instagram \
  --size ig_portrait \
  --dry-run

# 2. Real publish (uploads to GHL + schedules)
python3 -m publisher.cli publish \
  --client sam-trabulsi \
  --html output/2026-05-22-fbig-clarity-beats-credentials.html \
  --caption-file output/2026-05-22-caption.txt \
  --schedule "2026-05-22 10:00 Europe/Athens" \
  --platforms facebook instagram \
  --size ig_portrait

# 3. Verify
python3 -m publisher.cli verify --client sam-trabulsi --status scheduled
```

---

## SEE ALSO

- [publisher/README.md](publisher/README.md) — CLI reference
- [publisher/INSTALL.md](publisher/INSTALL.md) — per-client onboarding
- [publisher/GHL-Social-Publisher-Client-Setup-Guide.docx](publisher/GHL-Social-Publisher-Client-Setup-Guide.docx) — hand-off doc for new clients
- [.claude/commands/carousel.md](.claude/commands/carousel.md) — 7-slide carousel (Notion + Canva flow)
- [.claude/commands/linkedin.md](.claude/commands/linkedin.md) — LinkedIn handwriting card flow
- [.claude/commands/daily-posts.md](.claude/commands/daily-posts.md) — automated 4x daily pipeline
