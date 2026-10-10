#!/usr/bin/env python3
"""Batch Google Maps lead scrape: businesses with NO website, per city x category.

  python3 -I run_leads.py --targets lebanon_targets.json --out ~/gmb-leads/lebanon \
      [--cities Beirut,Jounieh] [--categories dentist,gym] [--limit 20]

Resumable: finished (city, category) pairs are recorded in <out>/done.txt and skipped.
Writes <out>/raw/<city>__<category>.csv per search, then merges to
<out>/leads_no_website.csv (deduped by place link/cid, sorted by reviews).
"""
import argparse, csv, json, os, re, subprocess, sys, time
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser("~/.cache/gmb-leads/google-maps-scraper")
SOCIAL = re.compile(r"facebook\.com|instagram\.com|linktr\.ee|wa\.me|business\.site|tiktok\.com", re.I)


def ensure_binary():
    if os.path.exists(BIN):
        return
    src = os.path.expanduser("~/.cache/gmb-leads/src")
    os.makedirs(os.path.dirname(BIN), exist_ok=True)
    if not os.path.isdir(src):
        subprocess.run(["git", "clone", "-q", "--depth", "1",
                        "https://github.com/gosom/google-maps-scraper", src], check=True)
    subprocess.run(["go", "build", "-o", BIN, "."], cwd=src, check=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def scrape(city, coords, cat, cfg, out):
    raw = os.path.join(out, "raw", f"{slug(city)}__{slug(cat)}.csv")
    q = os.path.join(out, "raw", f".q_{slug(city)}__{slug(cat)}.txt")
    with open(q, "w") as fh:
        fh.write(f"{cat} in {city}, {cfg['country']}\n")
    cmd = [BIN, "-input", q, "-results", raw, "-fast-mode", "-geo", coords,
           "-zoom", str(cfg.get("zoom", 14)), "-radius", str(cfg.get("radius_m", 6000)),
           "-depth", "3", "-exit-on-inactivity", "1m", "-lang", "en"]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=600)
    os.remove(q)
    return raw if r.returncode == 0 and os.path.exists(raw) else None


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def merge(out, cfg):
    seen, leads, total = set(), [], 0
    for name in sorted(os.listdir(os.path.join(out, "raw"))):
        if not name.endswith(".csv"):
            continue
        city, cat = name[:-4].split("__", 1)
        for r in csv.DictReader(open(os.path.join(out, "raw", name), encoding="utf-8")):
            if not r.get("title"):
                continue  # Google "limited view" rows carry no data
            total += 1
            key = (r.get("place_id") or r.get("cid") or r.get("data_id") or r.get("link")
                   or f'{r["title"]}|{r.get("address", "")}')
            if key in seen:
                continue
            seen.add(key)
            site = (r.get("website") or "").strip()
            if site and not SOCIAL.search(site):
                continue
            leads.append({
                "Business": r["title"], "Category": r.get("category", ""), "Searched": cat.replace("-", " "),
                "City": city.replace("-", " ").title(), "Rating": r.get("review_rating", "")[:3],
                "Reviews": int(num(r.get("review_count"))), "Phone": r.get("phone", ""),
                "Social link": site, "Address": r.get("address", ""), "Status": r.get("status", ""),
                "Google Maps link": r.get("link") or "https://www.google.com/maps/search/?api=1&query="
                + quote_plus(f'{r["title"]} {r.get("address", "")}'),
            })
    leads.sort(key=lambda d: (-d["Reviews"], -num(d["Rating"])))
    path = os.path.join(out, "leads_no_website.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(leads[0].keys()) if leads else ["Business"])
        w.writeheader()
        w.writerows(leads)
    print(f"merged: {total} listings, {len(seen)} unique, {len(leads)} without a website -> {path}")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=os.path.join(HERE, "lebanon_targets.json"))
    ap.add_argument("--out", default=os.path.expanduser("~/gmb-leads/lebanon"))
    ap.add_argument("--cities")
    ap.add_argument("--categories")
    ap.add_argument("--limit", type=int, default=0, help="max searches this run (0 = all)")
    ap.add_argument("--pause", type=float, default=4.0, help="seconds between searches")
    ap.add_argument("--merge-only", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(a.targets))
    os.makedirs(os.path.join(a.out, "raw"), exist_ok=True)
    if a.merge_only:
        merge(a.out, cfg)
        return
    ensure_binary()
    cities = {k: v for k, v in cfg["cities"].items() if not a.cities or k in a.cities.split(",")}
    cats = [c for c in cfg["categories"] if not a.categories or c in a.categories.split(",")]
    done_path = os.path.join(a.out, "done.txt")
    done = set(open(done_path).read().split("\n")) if os.path.exists(done_path) else set()
    jobs = [(c, g, k) for c, g in cities.items() for k in cats if f"{c}|{k}" not in done]
    if a.limit:
        jobs = jobs[: a.limit]
    print(f"{len(jobs)} searches to run ({len(done)} already done)", flush=True)
    empty_streak = 0
    for i, (city, coords, cat) in enumerate(jobs, 1):
        raw = scrape(city, coords, cat, cfg, a.out)
        rows = sum(1 for r in csv.DictReader(open(raw, encoding="utf-8")) if r.get("title")) if raw else 0
        print(f"[{i}/{len(jobs)}] {city} / {cat}: {rows} listings", flush=True)
        empty_streak = empty_streak + 1 if rows == 0 else 0
        if empty_streak >= 8:
            print("8 empty searches in a row: Google is probably blocking. Stopping; rerun later or add proxies.")
            break
        with open(done_path, "a") as fh:
            fh.write(f"{city}|{cat}\n")
        if i % 25 == 0:
            merge(a.out, cfg)
        time.sleep(a.pause)
    merge(a.out, cfg)


if __name__ == "__main__":
    main()
