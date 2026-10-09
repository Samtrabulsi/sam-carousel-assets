#!/usr/bin/env python3
"""Weekly channel report.

  python3 analytics.py --channel-url https://www.youtube.com/@Handle --slug <slug> [--out report.md]

Public mode (always, no key): yt-dlp lists the channel's long videos + current views; each run appends a snapshot to
youtube/<slug>/analytics/snapshots.jsonl so the report shows views gained since the last run.
Owner mode (if secret YT_OAUTH_<SLUG> is set): YouTube Analytics API, last 28 days per video: views, watch time,
average view duration/percentage, subscribers gained. These are the numbers that decide what to make next.
"""
import argparse, datetime, json, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--channel-url", required=True); ap.add_argument("--slug", required=True); ap.add_argument("--out")
ap.add_argument("--root", default="youtube")
a = ap.parse_args()
today = datetime.date.today().isoformat()
adir = os.path.join(a.root, a.slug, "analytics"); os.makedirs(adir, exist_ok=True)
snap_path = os.path.join(adir, "snapshots.jsonl")

out = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", a.channel_url.rstrip("/") + "/videos"],
                     capture_output=True, text=True, timeout=300).stdout
d = json.loads(out) if out.strip() else {}
vids = [{"id": e["id"], "title": e.get("title"), "views": e.get("view_count") or 0, "duration": e.get("duration")} for e in (d.get("entries") or []) if e]
prev = {}
if os.path.exists(snap_path):
    lines = open(snap_path).read().strip().splitlines()
    if lines:
        last = json.loads(lines[-1]); prev = {v["id"]: v["views"] for v in last["videos"]}
open(snap_path, "a").write(json.dumps({"date": today, "subs": d.get("channel_follower_count"), "videos": vids}) + "\n")

md = [f"# {d.get('channel', a.slug)}: weekly report {today}", "",
      f"Subscribers: **{d.get('channel_follower_count')}** · long videos: {len(vids)} · total views: {sum(v['views'] for v in vids):,}", "",
      "| Views | Since last report | Length | Video |", "|---|---|---|---|"]
for v in sorted(vids, key=lambda v: -v["views"]):
    gain = v["views"] - prev[v["id"]] if v["id"] in prev else None
    md.append(f"| {v['views']:,} | {('+' + format(gain, ',')) if gain is not None else 'new'} | {round((v['duration'] or 0) / 60)} min | [{(v['title'] or '').replace('|', '/')}](https://youtu.be/{v['id']}) |")

secret = "YT_OAUTH_" + a.slug.upper().replace("-", "_")
if os.environ.get(secret):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "yt-publish", "scripts"))
    from ytapi import analytics
    start = (datetime.date.today() - datetime.timedelta(days=28)).isoformat()
    r = analytics(a.slug).reports().query(ids="channel==MINE", startDate=start, endDate=today, dimensions="video",
        metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained", sort="-views", maxResults=25).execute()
    titles = {v["id"]: v["title"] for v in vids}
    md += ["", "## Last 28 days (YouTube Analytics)", "", "| Video | Views | Watch hours | Avg view | Avg % watched | Subs gained |", "|---|---|---|---|---|---|"]
    for vid, views, mins, avd, avp, subs in r.get("rows", []):
        md.append(f"| {titles.get(vid, vid)} | {views:,} | {mins / 60:,.0f} | {int(avd) // 60}:{int(avd) % 60:02d} | {avp:.0f}% | {subs} |")
    md += ["", "Read it like this: **avg % watched** ≥ 35 % on a 15-20 min video is strong; < 20 % means the opening or pacing lost people.",
           "**Subs gained per 1,000 views** shows which topics build the channel. Double down on topics that win both."]
else:
    md += ["", f"_Owner metrics (watch time, retention, subs per video) need the {secret} secret; see yt-publish setup._"]
text = "\n".join(md)
if a.out:
    open(a.out, "w").write(text + "\n")
print(text)
