---
name: gmb-no-website-leads
description: Build lead lists of Google Business Profile (GMB / Google Maps) businesses that have NO website (or only a Facebook/Instagram link), by city and category, with name, phone, address, rating, reviews and a Maps link. Lebanon targets included (22 cities x 38 categories). Use when Sam asks for businesses without websites, GMB/Google Maps leads, "scrape Google Maps", website-sale prospects, or leads in a city/country.
---

# GMB "no website" leads

Engine: [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (MIT, Go), built from source into `~/.cache/gmb-leads/` on first run (needs `go`; builds in about a minute).

## Run

```bash
S=.claude/skills/gmb-no-website-leads/scripts
python3 -I $S/run_leads.py --out ~/gmb-leads/lebanon                         # everything in lebanon_targets.json
python3 -I $S/run_leads.py --cities Beirut,Jounieh --categories dentist,gym  # a slice
python3 -I $S/run_leads.py --limit 50                                        # next 50 searches only
python3 -I $S/run_leads.py --merge-only                                      # rebuild the merged CSV
```
- **Resumable:** finished city/category pairs are recorded in `<out>/done.txt` and skipped next time. A full Lebanon pass is about 836 searches (several hours); run it in the background (`run_in_background`) and report progress.
- **Output:** `<out>/leads_no_website.csv`, deduped and sorted by review count. Counts a listing as "no website" when the website field is empty or is only Facebook, Instagram, Linktree, WhatsApp, TikTok or business.site (the "Social link" column).
- **Other countries:** copy `lebanon_targets.json`, change `country`, the `cities` (name to "lat,lng") and `categories`.

## How it works (lessons from 2026-10-10)

- Uses **`-fast-mode` with `-geo` per city**. Normal mode came back as empty rows: Google serves a stripped "limited view" to automated visitors. Fast mode returns about 20 listings per search with name, phone, rating, reviews, address and website, but no place link (the script builds a Maps search link).
- The script **stops after 8 empty searches in a row**, which means Google is blocking. Wait or add `-proxies` before rerunning; never hammer it.
- Results per search are capped by Google, so coverage comes from many city x category searches, not depth.

## Data handling (important)

- **This repo is public.** Lead files must never be committed: `leads/`, `gmb-leads/` and `*leads*.csv` are in `.gitignore`. Keep output in `~/gmb-leads/` (wiped when the cloud session ends) and deliver it to Sam with SendUserFile, or upload it to his Google Drive or Notion.
- Scraping Google Maps breaks Google's Terms of Service: keep runs modest, and don't resell or publish the data. For regular, at-scale use, the compliant route is the Google Places API (Text Search, then drop results with a `websiteUri`); it needs Sam's API key.
- Outreach: published business contacts are fair game for a relevant, personal B2B message, but follow local anti-spam rules (e.g. Australia's Spam Act for email/SMS), honour opt-outs, and check each business by hand first (some have a site that just isn't linked on Google). Pair with `ig-dm` for openers.
