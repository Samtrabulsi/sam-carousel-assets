---
name: yt-analytics
description: Weekly performance report per YouTube channel — views gained per video (public, no key) plus watch time, retention, and subscribers per video from the YouTube Analytics API — and turn it into decisions for the next week's topics. Use for "how are the channels doing", "check analytics", "what's working", "watch hours", or the Analyst routine.
---

# yt-analytics

```bash
python3 .claude/skills/yt-analytics/scripts/analytics.py --channel-url https://www.youtube.com/@Handle --slug <slug> \
  --out youtube/<slug>/analytics/$(date +%F)-report.md
```

- **Public mode** always works, with no key. Every run appends a snapshot to `youtube/<slug>/analytics/snapshots.jsonl`, so the next report shows views gained per video. Commit the snapshots.
- **Owner mode** turns on automatically when the `YT_OAUTH_<SLUG>` secret exists (see yt-publish setup). It adds per-video views, watch hours, average view duration, % watched and subscribers gained over the last 28 days.

## Turning numbers into decisions (write these 3–5 lines at the end of each report)

| signal | meaning | action |
|---|---|---|
| A video gains views week after week | Search or suggested traffic found it | Make the sequel or the adjacent topic next (the Scout prioritises it) |
| Avg % watched < 20 % | The opening or pacing loses people | Shorter cold open; visual change every ≤15 s; cut the slow chapter |
| Avg % watched ≥ 35 % on 15–20 min | Format works | Keep the structure; vary only the topic |
| High views, few subs per 1K views | Topic is broad and not tied to the channel | Fine occasionally; prioritise topics that win both |
| A video flat after 7 days | Title/thumbnail didn't earn the click | Test a new thumbnail in Studio (Test & Compare), then a new title |

- **Monetization tracker:** public watch hours from the last 365 days (Owner mode, sum of watch hours), shown against the 4,000-hour target. Shorts don't count.
- **Never judge a video before 7 days**, and never delete low performers. They still pick up search traffic.
