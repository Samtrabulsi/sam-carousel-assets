#!/usr/bin/env python3
"""Resolve photo queries in script.json into real, licence-safe photos.

In script.json, any v.bg / v.photo / v.photos entry written as "q:<search words>" is searched,
downloaded to <episode>/photos/<slug>.jpg (max 1920 px wide) and replaced with the slug.
Sources, in order:
  1. Pexels (free API key in env PEXELS_API_KEY; Pexels licence: free commercial use, no attribution needed)
  2. Openverse, CC0/public-domain only (no key; uses Openverse's thumbnail proxy so source hosts don't rate-limit us)
Every photo is logged in photos/CREDITS.md. The same photo is never used twice in one episode.

  python3 fetch_photos.py <episode-dir>
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request

EP = sys.argv[1]
UA = {"User-Agent": "Mozilla/5.0 (yt-produce)"}


def get(url, headers=None, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout).read()


def pexels(q):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    d = json.loads(get("https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "orientation": "landscape", "per_page": 10}), {"Authorization": key}))
    return [{"url": p["src"]["large2x"], "credit": f"Pexels: {p['photographer']} {p['url']}", "id": f"pexels-{p['id']}"} for p in d.get("photos", [])]


def openverse(q):
    d = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "license": "cc0,pdm", "aspect_ratio": "wide", "size": "large", "page_size": 12, "mature": "false"})))
    # the thumbnail proxy serves a resized copy from Openverse itself (full-size originals on Wikimedia rate-limit with 429)
    return [{"url": f"https://api.openverse.org/v1/images/{r['id']}/thumb/?full_size=true", "fallback": r["url"],
             "credit": f"Openverse {r['license'].upper()}: {r.get('title')} ({r.get('source')}) {r.get('foreign_landing_url')}", "id": f"ov-{r['id']}"}
            for r in d.get("results", [])]


def slugify(q):
    return re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:40] or "photo"


def main():
    sp = os.path.join(EP, "script.json")
    beats = json.load(open(sp))
    os.makedirs(os.path.join(EP, "photos"), exist_ok=True)
    used, credits, resolved = set(), [], {}
    cpath = os.path.join(EP, "photos", "CREDITS.md")
    if os.path.exists(cpath):
        credits = open(cpath).read().splitlines()[2:]

    def resolve(val):
        if not isinstance(val, str) or not val.startswith("q:"):
            return val
        q = val[2:].strip()
        if q in resolved:
            return resolved[q]
        slug = slugify(q); n = 2
        while os.path.exists(os.path.join(EP, "photos", slug + ".jpg")):
            slug = f"{slugify(q)}-{n}"; n += 1
        for src in (pexels, openverse):
            try:
                cands = src(q)
            except Exception as e:
                print(f"  {src.__name__} failed for '{q}': {e}", file=sys.stderr); cands = []
            for c in cands:
                if c["id"] in used:
                    continue
                for u in (c["url"], c.get("fallback")):
                    if not u:
                        continue
                    try:
                        raw = get(u)
                        tmp = os.path.join(EP, "photos", slug + ".src")
                        open(tmp, "wb").write(raw)
                        out = os.path.join(EP, "photos", slug + ".jpg")
                        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-vf", "scale='min(1920,iw)':-2", "-q:v", "4", out])
                        os.remove(tmp)
                        if r.returncode == 0 and os.path.getsize(out) > 20_000:
                            used.add(c["id"]); credits.append(f"- {slug}.jpg ← \"{q}\" · {c['credit']}")
                            resolved[q] = slug
                            print(f"  {q} -> {slug}.jpg", file=sys.stderr)
                            return slug
                    except Exception:
                        continue
        print(f"  NO PHOTO for '{q}' (left empty; scene renders without it)", file=sys.stderr)
        resolved[q] = None
        return None

    for b in beats:
        v = b["v"]
        for k in ("bg", "photo"):
            if k in v:
                v[k] = resolve(v[k])
                if v[k] is None:
                    del v[k]
        if "photos" in v:
            v["photos"] = [p for p in (resolve(p) for p in v["photos"]) if p]
    json.dump(beats, open(sp, "w"), indent=1, ensure_ascii=False)
    open(cpath, "w").write("# Photo credits\nPexels licence or CC0/public domain. Attribution not required; kept for the record.\n" + "\n".join(credits) + "\n")


if __name__ == "__main__":
    main()
