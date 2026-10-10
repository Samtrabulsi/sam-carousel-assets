---
name: seo-data-free
description: Free replacements for paid SEO tools (SEOptimer, Semrush, Ahrefs) - page speed and Core Web Vitals, keyword research (English + Arabic, Google/YouTube/Bing), rank tracking with change reports, and backlink research with new/lost monitoring - using free Google, Bing and Open PageRank APIs. Use when Sam asks for page speed, keyword ideas, rankings, rank tracking, backlinks, "who links to my site", or a recurring SEO report for his or a client's site.
---

# Free SEO data (`scripts/seodata.py`)

```bash
S=.claude/skills/seo-data-free/scripts/seodata.py
python3 -I $S speed https://site.com                          # mobile + desktop scores, lab + real-user Core Web Vitals, top fixes
python3 -I $S keywords "website design" --lang en --country lb [--deep]
python3 -I $S keywords "تصميم مواقع" --lang ar --country lb
python3 -I $S ranks sc-domain:site.com [--days 28] [--country lbn]   # positions, clicks, movers, quick wins
python3 -I $S backlinks https://site.com/                     # links + referring domains, new/lost since last run
```
Snapshots go to `~/seo-data/<domain>/` (and `~/seo-data/keywords/`). That folder is wiped with the cloud session, so deliver CSVs with SendUserFile. **Never commit client data to this public repo.**

## What each command needs (all free)

| Command | Works without keys? | Free key (environment variable) |
|---|---|---|
| `keywords` | **Yes** (Google, YouTube and Bing autocomplete, EN/AR, by country) | none |
| `speed` | Rarely (shared keyless quota is usually used up) | `PSI_API_KEY`: Google Cloud API key with **PageSpeed Insights API** + **Chrome UX Report API** enabled (25k requests/day free) |
| `ranks` | No | `GSC_SA_JSON_B64` (the JSON file base64-encoded on one line; Mac: `base64 -i key.json \| pbcopy`), or `GSC_SA_JSON` / `GSC_CREDENTIALS_PATH`; add the service-account email as a user on each Search Console property. Same credential as `gsc-mcp`. |
| `backlinks` | No | `BING_WMT_API_KEY` (Bing Webmaster Tools > Settings > API access; the site must be verified there, and Bing can import it from Search Console). Optional `OPR_API_KEY` (openpagerank.com, free) adds a 0-10 authority per referring domain. |

Keys live in the cloud environment settings (environment menu > Edit > secrets / environment variables); a new session picks them up. Never ask Sam to paste keys into chat, and never write them to the repo.

## Honest limits (tell clients)
- **Keyword volume:** autocomplete shows what people type, not monthly volume. Real demand comes from Search Console impressions (`ranks`) on sites we can access. For competitor volumes use `openseo-keyword-research` (paid per request).
- **Rank tracking** covers sites in Search Console (Sam's and clients who grant access) with Google's own average positions. Tracking other sites' rankings needs SERP data (OpenSEO, paid); don't scrape Google results.
- **Backlinks** come from Bing's index for verified sites: free and reliable, but a smaller index than Ahrefs. Competitor backlink research needs OpenSEO/DataForSEO (paid).
- PageSpeed lab scores vary run to run; judge trends over several runs (they're saved in `speed_history.csv`).

## Monitoring
For "track it weekly", create a routine (one that starts a fresh session each run, with this repo attached and the keys set in the environment) that runs `ranks`, `backlinks` and `speed` for each site and emails the changes. Reports for clients: Brand Victory-branded PDF/HTML (dark/cream/copper).
