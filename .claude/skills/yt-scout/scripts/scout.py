#!/usr/bin/env python3
"""Topic scout for faceless YouTube channels: no API key, no paid tools.

Uses yt-dlp (public YouTube pages) + YouTube autocomplete to answer:
  1. Which videos in this niche are OUTLIERS (far above their channel's usual views)?
  2. What do people actually type into YouTube search (autocomplete phrases)?
  3. For each candidate topic: how much proven demand vs how much competition?

  python3 scout.py niche.json [--out report.md] [--json data.json] [--per-query 20] [--channels 25]

niche.json (see ../../yt-automation/niches/*.json):
  {"name": "...", "queries": ["entire history of company", ...],
   "candidate_template": "the entire history of {}",   # optional
   "candidates": ["Walmart", "Nike", ...],             # optional
   "min_duration": 480}
"""
import argparse, json, os, statistics, subprocess, sys, time, urllib.parse, urllib.request

YTDLP = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", "--ignore-errors"]


def ytdlp_json(url, extra=()):
    try:
        out = subprocess.run(YTDLP + list(extra) + [url], capture_output=True, text=True, timeout=180).stdout
        d = json.loads(out) if out.strip() else {}
        return d if isinstance(d, dict) else {}
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}


def search(query, n, tries=3):
    for i in range(tries):  # YouTube sometimes returns nothing on a burst; retry gently
        res = [e for e in (ytdlp_json(f"ytsearch{n}:{query}").get("entries") or []) if e and e.get("id")]
        if res:
            return res
        time.sleep(3 * (i + 1))
    return []


def channel_baseline(channel_id, cache):
    """Median views of the channel's last ~30 long-form uploads + subscriber count."""
    if channel_id in cache:
        return cache[channel_id]
    d = ytdlp_json(f"https://www.youtube.com/channel/{channel_id}/videos", ["--playlist-end", "30"])
    views = [e.get("view_count") for e in (d.get("entries") or []) if e and e.get("view_count")]
    cache[channel_id] = {"median": statistics.median(views) if views else None, "subs": d.get("channel_follower_count"), "n": len(views)}
    time.sleep(0.5)  # be gentle with YouTube
    return cache[channel_id]


def autocomplete(q):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=" + urllib.parse.quote(q)
    try:
        return json.loads(urllib.request.urlopen(url, timeout=15).read().decode("utf-8", "ignore"))[1]
    except Exception:
        return []


def upload_dates(ids):
    """Upload dates via the official YouTube Data API (free key in env YT_API_KEY; 1 quota unit per 50 videos).
    yt-dlp can't do this from cloud servers: full video pages hit YouTube's bot check."""
    key = os.environ.get("YT_API_KEY")
    if not ids or not key:
        return {}
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + ",".join(ids[:50]) + "&key=" + key
    try:
        items = json.loads(urllib.request.urlopen(url, timeout=20).read()).get("items", [])
        return {it["id"]: it["snippet"]["publishedAt"][:10] for it in items}
    except Exception as e:
        print(f"upload dates unavailable: {e}", file=sys.stderr)
        return {}


def human(n):
    if n is None:
        return "?"
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}K" if n >= 1e3 else str(int(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("niche")
    ap.add_argument("--out")
    ap.add_argument("--json")
    ap.add_argument("--per-query", type=int, default=20)
    ap.add_argument("--channels", type=int, default=25, help="max channels to baseline (each is one request)")
    a = ap.parse_args()
    cfg = json.load(open(a.niche))
    min_dur = cfg.get("min_duration", 480)

    # 1. search every seed query
    videos = {}
    for q in cfg["queries"]:
        for e in search(q, a.per_query):
            if (e.get("duration") or 0) >= min_dur and e.get("view_count"):
                videos.setdefault(e["id"], {**{k: e.get(k) for k in ("id", "title", "channel", "channel_id", "view_count", "duration")}, "query": q})
        print(f"searched: {q} ({len(videos)} long videos so far)", file=sys.stderr)

    # 2. outlier score = views / channel median (biggest channels first are less interesting, so rank by views)
    cache = {}
    ranked = sorted(videos.values(), key=lambda v: -v["view_count"])
    for v in ranked[: a.channels * 2]:
        if len(cache) >= a.channels and v["channel_id"] not in cache:
            continue
        b = channel_baseline(v["channel_id"], cache)
        v["subs"], v["channel_median"] = b["subs"], b["median"]
        # need a real baseline: tiny/dormant channels give meaningless ratios
        ok = b["median"] and b["n"] >= 5 and b["median"] >= 2000
        v["outlier"] = round(v["view_count"] / b["median"], 1) if ok else None
    outliers = sorted([v for v in videos.values() if v.get("outlier")], key=lambda v: -v["outlier"])[:20]
    dates = upload_dates([v["id"] for v in outliers])
    for v in outliers:
        v["upload_date"] = dates.get(v["id"])

    # 3. autocomplete phrases (what people type)
    phrases = {}
    for q in cfg["queries"]:
        for s in autocomplete(q) + autocomplete(q + " how") + autocomplete(q + " why"):
            phrases[s] = q

    # 4. candidate topics: demand vs competition
    cands = []
    tmpl = cfg.get("candidate_template")
    for c in cfg.get("candidates", []):
        q = tmpl.format(c) if tmpl else c
        res = [e for e in search(q, 10) if (e.get("duration") or 0) >= min_dur]
        top = max((e.get("view_count") or 0 for e in res), default=0)
        strong = sum(1 for e in res if (e.get("view_count") or 0) >= 100_000)
        if not res:
            print(f"candidate: {c} (no search results, skipped)", file=sys.stderr)
            continue
        ac = autocomplete(f"history of {c}" if tmpl and "history" in tmpl else c)
        # opportunity: proven interest (top views, autocomplete) but few strong videos already covering it
        score = round((min(top, 2_000_000) / 100_000 + 2 * min(len(ac), 5)) / (1 + strong), 1)
        cands.append({"topic": c, "query": q, "top_views": top, "videos_100k_plus": strong, "autocomplete": ac[:4], "opportunity": score})
        print(f"candidate: {c} top={human(top)} strong={strong}", file=sys.stderr)
        time.sleep(0.5)
    cands.sort(key=lambda x: -x["opportunity"])

    data = {"niche": cfg["name"], "date": time.strftime("%Y-%m-%d"), "outliers": outliers, "phrases": phrases, "candidates": cands}
    if a.json:
        json.dump(data, open(a.json, "w"), indent=1)

    md = [f"# Scout report: {cfg['name']} ({data['date']})", "",
          "## Outliers (views ÷ channel's median views)", "",
          "| × | Views | Channel (subs) | Length | Uploaded | Title |", "|---|---|---|---|---|---|"]
    for v in outliers:
        md.append(f"| {v['outlier']}× | {human(v['view_count'])} | {v['channel'].replace('|', '/')} ({human(v.get('subs'))}) | {round(v['duration']/60)} min | {v.get('upload_date') or '?'} | [{v['title'].replace('|', '/')}](https://youtu.be/{v['id']}) |")
    if cands:
        md += ["", "## Candidate topics (higher opportunity = proven demand, fewer strong videos)", "",
               "| Opportunity | Topic | Best existing video | Videos ≥100K | People search |", "|---|---|---|---|---|"]
        for c in cands:
            md.append(f"| {c['opportunity']} | {c['topic']} | {human(c['top_views'])} | {c['videos_100k_plus']} | {'; '.join(c['autocomplete']) or '-'} |")
    md += ["", "## What people type (YouTube autocomplete)", ""] + [f"- {p}" for p in list(phrases)[:40]]
    md += ["", "_Outlier ≥3× on a small channel = the topic, not the channel, pulled the views. Opportunity score is a heuristic: check the top results by eye before committing._"]
    text = "\n".join(md)
    if a.out:
        open(a.out, "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
