---
name: seo-report
description: Produce a branded Brand Victory SEO & AI-search report PDF for ANY website, including a side-by-side comparison with its competitors, using only free data. Works without access to the site (speed, crawl, technical, on-page, AI visibility, schema, security, tracking, tech stack, domain age, rankings, keyword ideas, competitor gaps); adds Google Search Console and Bing backlink pages automatically when the site has given access. Use when Sam asks for "an SEO report/audit for X.com", a prospect/sales audit, a client SEO report, "compare X with its competitors", or a monthly/weekly report PDF.
---

# SEO report (any website)

Pipeline: `collect.py` gathers the data (incl. screenshots) → **you** gather social stats into `social.json` and write `notes.json` → `build.py` makes the branded HTML → `render.mjs` makes the A4 PDF → you check every page visually → deliver.

**Client-safe rule:** the PDF goes to clients. It must never mention API keys, missing access, setup steps or internal tools. Areas that couldn't be measured are left out silently (the builder already does this; keep your notes the same way).

```bash
S=.claude/skills/seo-report/scripts
O=<scratchpad>/seo-<domain>-<date>          # never inside the repo (it's public)
python3 -I $S/collect.py https://site.com --out $O \
  --kw "main service city" --kw "second service" --kw "خدمة بالعربي" \
  --competitor rival1.com --competitor rival2.com --competitor rival3.com \
  --brand "Person or brand name" \          # press-mention search (Arabic name for Arab brands)
  --country lb                              # 2-6 minutes; also saves img/ screenshots
cat $O/summary.md                           # read it all
# gather social stats -> $O/social.json (section 3a), then write $O/notes.json (section 3b)
python3 -I $S/build.py $O [--prepared-for "Client"]   # -> $O/report.html
node $S/render.mjs $O/report.html $O/<brand>-seo-report-<domain>-<date>.pdf
```

## 1. Before collecting

- **Keywords (`--kw`, 3-5):** the money searches for that business in its market, in English and Arabic for Arab markets (e.g. "dentist beirut", "طبيب أسنان بيروت"). They drive the rankings table, keyword ideas and competitor discovery. Arabic is detected automatically.
- **Competitors:** best is 3 real direct competitors from Sam or the client. If none are given, find them yourself with WebSearch on the keywords (skip directories, marketplaces, social sites, and namesakes like "Lebanon, Missouri"), then pass them with `--competitor`. Without `--competitor` the script auto-picks from DuckDuckGo results, which is fine for a quick prospect audit but check them in `summary.md` and rerun if they're wrong.
- **`--country`:** ISO code (lb, ae, sa, au…). Arab markets expect Arabic pages in the "Local & language reach" score.
- Options: `--max-pages 60` (target crawl), `--comp-pages 15`, `--no-gsc`, `--no-geo`, `--no-speed`.

## 2. What it collects

| Works for any site (no access) | Needs access |
|---|---|
| PageSpeed mobile/desktop + Core Web Vitals (PSI_API_KEY) | **Search Console** clicks, queries, countries, pages, monthly trend: the site adds `seo-reader@quick-heaven-382812.iam.gserviceaccount.com` as a user (Restricted is enough) |
| AI visibility (GEO Optimizer: ChatGPT / Perplexity / Google AI) | **Bing backlinks**: site verified in Sam's Bing Webmaster account (BING_WMT_API_KEY) |
| Crawl of up to 60 sitemap pages: titles, descriptions, H1s, words, alt text, canonicals, noindex, schema, Arabic pages, junk/empty/test pages, broken pages, public PDFs/docs | |
| robots.txt (AI bots blocked?), sitemap size, blog count + last post, llms.txt | |
| Security headers, version leaks, spam/hack scan, SPF/DMARC, SSL expiry (crt.sh), domain age + registrar (RDAP), email + DNS host | |
| Tech stack (WordPress, Elementor, Wix, Shopify…), tracking (GA4, GTM, Meta/TikTok pixel, Clarity), contact paths (WhatsApp, booking, forms, chat) | |
| Top-10 rankings for each keyword (DuckDuckGo = Bing index), content-gap topics, autocomplete keyword ideas | |
| Domain authority 0-10 for every site (Open PageRank; key in `OPR_API_KEY` or `ORP_API_KEY`), global traffic rank + 6-week trend (Tranco, no key), press pages mentioning the brand and whether they link back | |
| Above-the-fold screenshots, desktop + mobile, for the site and each competitor (`shots.mjs`, Playwright) | |

Every competitor gets the same public checks, so the competitor table compares like with like. The "public score" ignores Search Console so it's fair across sites.

## 3a. Social media & brand (social.json)

`summary.md` lists the social profiles linked from the site plus public Telegram/TikTok counts. Fill in the rest yourself:
- Instagram: `mcp__vidIQ__vidiq_ig_profile` (followers, posts, bio link, profile picture) and `vidiq_ig_profile_reels` (plays per reel, covers).
- YouTube: `mcp__vidIQ__vidiq_channel_stats` with the channel ID (subscribers, views, 30-day growth).
- Facebook/X/LinkedIn rarely expose counts; use a figure only if the person states it publicly, and label it ("as stated in his bio").
- Check where the bio link goes (Linktree pages: read `__NEXT_DATA__`), whether handles match, pinned content age, and whether press pages link back (`mentions` in summary.md).
- Copy images the tools return (profile picture, reel covers) into `$O/img/` and reference them as `img/<file>`.

```json
{"name": "…", "tagline": "…", "avatar": "img/avatar.jpg",
 "accounts": [{"platform": "YouTube", "handle": "…", "followers": 1290000, "posts": 1134, "note": "…"}],
 "top_title": "…", "top_content": [{"image": "img/reel1.jpg", "metric": "3.3M plays", "caption": "Pinned · Jul 2024"}],
 "brand_checks": [["ok|warn|bad", "…"]], "summary": "html",
 "improvements": [{"area": "…", "issue": "…", "fix": "…"}], "growth_callout": "html"}
```
This adds the "Social media & brand presence" and "Where the brand can grow" pages. No social.json, no pages. Skip it for businesses with no real social presence.

## 3b. Write notes.json (the part that makes it worth paying for)

Read `summary.md` fully. Verify anything surprising before writing it (open the page with curl, re-run a check). Then write `$O/notes.json`; every key is optional and falls back to auto text:

```json
{
  "cover_sub": "One line under the domain on the cover",
  "short": [{"title": "The site is solid, but invisible.", "body": "Only <b>4 clicks in 28 days</b>…"}, {…}, {…}],
  "priorities": [{"action": "…", "why": "…", "effort": "1 day"}],
  "plan": [{"when": "Week 1", "action": "…", "result": "…"}],
  "targets": [{"value": "100+", "label": "Google clicks / month (from 4)"}],
  "content_gap": ["topic", "…"],
  "keywords": {"seed or theme": [{"keyword": "…", "intent": "commercial|local|question|info"}]},
  "callouts": {"first_impression": "", "search": "", "queries": "", "competitors": "", "rankings": "", "speed": "",
               "technical": "", "onpage": "", "ai": "", "authority": "", "security": "", "plan": ""},
  "contact": "samtrabulsi.com · @samtrabulsi"
}
```

Writing rules:
- Plain words for business owners, Sam's voice: name the problem bluntly, then the fix. Numbers beat adjectives.
- Exactly 3 `short` cards and up to 5 `priorities`, ordered by business impact (security and confidentiality first).
- Competitor callout: where they beat the site and the one move that closes the gap.
- `content_gap`: replace the auto list (it's raw word pairs) with 6-12 real topics/pages the competitors have and the site doesn't.
- `keywords` (optional): up to 4 curated lists that replace the raw autocomplete tables; drop off-topic ideas.
- Values are HTML: `<b>`, `<i>` are fine; escape `&` and `<` in plain text.
- Never invent numbers. If a section's data is missing, leave its key out.

## 4. Check, then deliver

```bash
pdftoppm -r 60 -png $O/report.pdf $O/p     # look at every page image
```
Look for text overflowing the page, wrapped score columns, broken Arabic, empty sections, and odd competitors. Fix the notes or the data and rebuild (build + render take seconds; don't re-collect).

Deliver with SendUserFile (`display: render`). **Never commit reports or data to this repo**: it's public, and reports name client pages and documents. Give Sam a 5-line summary: overall score, the top 3 problems, where competitors win, and anything that needs his action (a hacked site, a public confidential document).

## Gotchas

- DuckDuckGo resets some connections; a keyword can come back "not checked". Rerun for a full table if it matters.
- PageSpeed lab scores vary ±10 between runs; quote ranges when comparing over time.
- GEO Optimizer runs through `uvx` (first run installs it, ~30 s).
- Sites behind Cloudflare bot protection can return 403 to the crawler; the report then shows near-empty on-page data. Say so instead of scoring it as bad SEO.
- Scores are Brand Victory's own weighted index (weights in build.py / the report appendix), not an industry standard. Say that if a client asks.
- For a white-label report: `--brand "Agency" --author "Name" --tagline "…"`.
- Related skills: `seo-data-free` (individual speed/keyword/rank/backlink checks), `geo-optimizer` (AI-visibility fixes, llms.txt), `claude-seo-cloud` (deep single-page audits), `gsc-*` (Search Console deep dives).
