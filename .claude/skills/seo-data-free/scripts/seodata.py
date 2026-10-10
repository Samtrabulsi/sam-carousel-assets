#!/usr/bin/env python3
"""Free SEO data: speed, keyword ideas, rank tracking and backlinks.

  seodata.py speed     https://site.com [--strategy mobile|desktop|both]
  seodata.py keywords  "seed phrase" [--lang en|ar] [--country lb] [--deep]
  seodata.py ranks     sc-domain:site.com|https://site.com/ [--days 28] [--country lbn]
  seodata.py backlinks https://site.com/ [--top 50]

Free sources and the environment variables they read (all optional; missing keys are reported):
  PSI_API_KEY             Google Cloud API key with PageSpeed Insights API + Chrome UX Report API enabled
  GSC_CREDENTIALS_PATH    service-account JSON added as a user on the Search Console property
  GSC_SA_JSON_B64         (recommended for env settings) the JSON file base64-encoded on one line
  GSC_SA_JSON             (alternative) the service-account JSON content itself
  BING_WMT_API_KEY        Bing Webmaster Tools API key (site must be verified in Bing WMT)
  OPR_API_KEY             Open PageRank API key (domain authority for referring domains)
Snapshots are kept in ~/seo-data/<domain>/ so later runs report changes (new/lost links, rank moves).
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36"
DATA = os.path.expanduser(os.environ.get("SEO_DATA_DIR", "~/seo-data"))


def http(url, data=None, headers=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def jget(url, **kw):
    return json.loads(http(url, **kw))


def domain_of(site):
    s = re.sub(r"^sc-domain:", "", site)
    return re.sub(r"^https?://(www\.)?", "", s).split("/")[0].lower()


def store(site):
    d = os.path.join(DATA, domain_of(site))
    os.makedirs(d, exist_ok=True)
    return d


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def need(var, why):
    print(f"! {var} not set: {why}. Add it in the cloud environment settings (Edit > environment variables / secrets), then start a new session.")


# ---------------------------------------------------------------- speed
def cmd_speed(a):
    key = os.environ.get("PSI_API_KEY")
    if not key:
        need("PSI_API_KEY", "PageSpeed's shared keyless quota is usually exhausted")
    out, ts = [], dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    for strat in (["mobile", "desktop"] if a.strategy == "both" else [a.strategy]):
        q = {"url": a.url, "strategy": strat}
        qs = urllib.parse.urlencode(q) + "".join(f"&category={c}" for c in ("performance", "seo", "accessibility", "best-practices"))
        if key:
            qs += f"&key={key}"
        try:
            d = jget("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + qs, timeout=150)
        except urllib.error.HTTPError as e:
            print(f"{strat}: PageSpeed error {e.code}: {e.read().decode()[:160]}")
            continue
        lh = d["lighthouseResult"]; au = lh["audits"]
        scores = {k: round(v["score"] * 100) for k, v in lh["categories"].items() if v.get("score") is not None}
        field = {k: v.get("category") for k, v in d.get("loadingExperience", {}).get("metrics", {}).items()}
        row = {"time": ts, "strategy": strat, **{f"score_{k}": v for k, v in scores.items()},
               "LCP": au["largest-contentful-paint"]["displayValue"], "CLS": au["cumulative-layout-shift"]["displayValue"],
               "TBT": au["total-blocking-time"]["displayValue"], "FCP": au["first-contentful-paint"]["displayValue"],
               "field_LCP": field.get("LARGEST_CONTENTFUL_PAINT_MS", "n/a"), "field_INP": field.get("INTERACTION_TO_NEXT_PAINT", "n/a"),
               "field_CLS": field.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", "n/a")}
        out.append(row)
        print(f"\n{strat.upper()}: " + ", ".join(f"{k} {v}" for k, v in scores.items()))
        print(f"  lab: LCP {row['LCP']} | CLS {row['CLS']} | TBT {row['TBT']} | FCP {row['FCP']}")
        print(f"  real users (CrUX): LCP {row['field_LCP']} | INP {row['field_INP']} | CLS {row['field_CLS']}")
        opps = sorted(((v.get("details", {}).get("overallSavingsMs", 0), v["title"]) for v in au.values()
                       if v.get("details", {}).get("overallSavingsMs")), reverse=True)[:5]
        for ms, t in opps:
            print(f"  fix: {t} (~{ms/1000:.1f}s)")
    if out:
        p = os.path.join(store(a.url), "speed_history.csv")
        old = list(csv.DictReader(open(p, encoding="utf-8-sig"))) if os.path.exists(p) else []
        write_csv(p, old + out)
        print(f"\nsaved -> {p}")


# ---------------------------------------------------------------- keywords
MODS = {
    "en": ["how", "what", "why", "best", "cost", "price", "near me", "for", "vs", "course", "agency", "examples"],
    "ar": ["كيف", "ما هو", "أفضل", "سعر", "كم", "دورة", "شركة", "في لبنان", "مع", "طريقة"],
}


def suggest(q, lang, country, source):
    try:
        if source == "bing":
            d = jget("https://api.bing.com/osjson.aspx?" + urllib.parse.urlencode({"query": q, "mkt": f"{lang}-{country.upper()}"}), timeout=15)
        else:
            p = {"client": "firefox", "hl": lang, "gl": country, "q": q}
            if source == "youtube":
                p["ds"] = "yt"
            d = jget("https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(p), timeout=15)
        return [s for s in d[1] if isinstance(s, str)]
    except Exception:
        return []


def cmd_keywords(a):
    seeds = [a.seed]
    seeds += [f"{a.seed} {m}" for m in MODS[a.lang]] + [f"{m} {a.seed}" for m in MODS[a.lang][:5]]
    if a.deep and a.lang == "en":
        seeds += [f"{a.seed} {c}" for c in "abcdefghijklmnopqrstuvwxyz"]
    found = {}
    for s in seeds:
        for src in ("google", "youtube", "bing"):
            for kw in suggest(s, a.lang, a.country, src):
                k = kw.strip().lower()
                f = found.setdefault(k, {"keyword": k, "google": 0, "youtube": 0, "bing": 0, "seed": s})
                f[src] += 1
        time.sleep(0.15)
    rows = sorted(found.values(), key=lambda r: (-(r["google"] + r["youtube"] + r["bing"]), r["keyword"]))
    for r in rows:
        q = r["keyword"]
        r["intent"] = ("commercial" if re.search(r"price|cost|agency|company|hire|best|services?|سعر|اسعار|أسعار|شركة|شركات|أفضل|افضل|كم", q) else
                       "question" if re.search(r"^(how|what|why|when|is|can)\b|كيف|ما |لماذا|هل", q) else
                       "local" if re.search(r"near me|lebanon|beirut|dubai|لبنان|بيروت", q) else "info")
        r["score"] = r["google"] * 2 + r["youtube"] + r["bing"]
    rows.sort(key=lambda r: (-r["score"], r["keyword"]))
    p = os.path.join(DATA, "keywords", re.sub(r"\W+", "-", a.seed)[:40] + f"_{a.lang}-{a.country}.csv")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    write_csv(p, rows)
    print(f"{len(rows)} keyword ideas for '{a.seed}' ({a.lang}-{a.country}); top 25 by how often they're suggested:")
    for r in rows[:25]:
        print(f"  {r['score']:>2}  {r['intent']:<10} {r['keyword']}")
    print(f"saved -> {p}\nNote: autocomplete shows what people type, not search volume. Use `ranks` (Search Console impressions) for real demand on your own sites.")


# ---------------------------------------------------------------- ranks (Search Console)
def gsc_token():
    raw = os.environ.get("GSC_SA_JSON")
    b64 = os.environ.get("GSC_SA_JSON_B64")
    if not raw and b64:
        raw = b64
    if raw and not raw.lstrip().startswith("{"):   # accept base64 under either variable name
        import base64
        raw = base64.b64decode("".join(raw.split())).decode("utf-8")
    path = os.environ.get("GSC_CREDENTIALS_PATH") or os.path.expanduser("~/.config/gsc/service_account.json")
    if not raw and not os.path.exists(path):
        need("GSC_SA_JSON_B64", "rank tracking reads your real Google positions from Search Console "
             "(on a Mac: base64 -i key.json | pbcopy, then paste as the value)")
        return None
    lib = os.path.expanduser("~/.cache/seodata-pylib")
    sys.path.insert(0, lib)
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        os.system(f"{sys.executable} -m pip install -q --target {lib} google-auth requests >/dev/null 2>&1")
        import importlib; importlib.invalidate_caches()
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    info = json.loads(raw) if raw else json.load(open(path))
    cr = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    cr.refresh(Request())
    return cr.token


def gsc_query(tok, site, start, end, dims, country=None, limit=1000):
    body = {"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": limit, "dataState": "all"}
    if country:
        body["dimensionFilterGroups"] = [{"filters": [{"dimension": "country", "expression": country}]}]
    url = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(site, safe='')}/searchAnalytics/query"
    d = jget(url, data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    return d.get("rows", [])


def cmd_ranks(a):
    tok = gsc_token()
    if not tok:
        return
    end = dt.date.today() - dt.timedelta(days=2)
    cur_s = end - dt.timedelta(days=a.days - 1)
    prev_e = cur_s - dt.timedelta(days=1)
    prev_s = prev_e - dt.timedelta(days=a.days - 1)
    try:
        cur = {r["keys"][0]: r for r in gsc_query(tok, a.site, str(cur_s), str(end), ["query"], a.country)}
        prev = {r["keys"][0]: r for r in gsc_query(tok, a.site, str(prev_s), str(prev_e), ["query"], a.country)}
    except urllib.error.HTTPError as e:
        sites = jget("https://www.googleapis.com/webmasters/v3/sites", headers={"Authorization": f"Bearer {tok}"}).get("siteEntry", [])
        print(f"Search Console refused '{a.site}' (HTTP {e.code}). Properties this service account can read: "
              + (", ".join(x["siteUrl"] for x in sites) or "NONE"))
        print("Fix: Search Console > Settings > Users and permissions > Add user > the service account's client_email "
              "(Restricted is enough), on the exact property (sc-domain:site.com or https://site.com/).")
        return
    rows = []
    for q, r in cur.items():
        p = prev.get(q)
        rows.append({"query": q, "position": round(r["position"], 1), "prev_position": round(p["position"], 1) if p else "",
                     "change": round(p["position"] - r["position"], 1) if p else "new", "clicks": r["clicks"],
                     "impressions": r["impressions"], "ctr_%": round(r["ctr"] * 100, 1)})
    rows.sort(key=lambda r: -r["impressions"])
    d = store(a.site)
    write_csv(os.path.join(d, f"ranks_{end}.csv"), rows)
    print(f"{len(rows)} queries, {cur_s}..{end} vs previous {a.days} days" + (f" ({a.country})" if a.country else ""))
    print("top by impressions:")
    for r in rows[:15]:
        print(f"  pos {r['position']:>5} ({r['change']:>+5} )  {r['impressions']:>6} impr  {r['clicks']:>4} clicks  {r['query']}" if r["change"] != "new"
              else f"  pos {r['position']:>5} ( new )  {r['impressions']:>6} impr  {r['clicks']:>4} clicks  {r['query']}")
    movers = [r for r in rows if isinstance(r["change"], float)]
    up = sorted(movers, key=lambda r: -r["change"])[:5]; down = sorted(movers, key=lambda r: r["change"])[:5]
    print("biggest gains:", "; ".join(f"{r['query']} (+{r['change']})" for r in up if r["change"] > 0) or "none")
    print("biggest drops:", "; ".join(f"{r['query']} ({r['change']})" for r in down if r["change"] < 0) or "none")
    quick = [r for r in rows if 8 <= r["position"] <= 20 and r["impressions"] >= 20]
    print("quick wins (positions 8-20):", "; ".join(r["query"] for r in quick[:8]) or "none")
    print(f"saved -> {d}")


# ---------------------------------------------------------------- backlinks
def opr(domains):
    key = os.environ.get("OPR_API_KEY")
    if not key or not domains:
        return {}
    out = {}
    for i in range(0, len(domains), 100):
        q = "&".join("domains[]=" + urllib.parse.quote(x) for x in domains[i:i + 100])
        try:
            d = jget("https://openpagerank.com/api/v1.0/getPageRank?" + q, headers={"API-OPR": key})
            out.update({r["domain"]: r.get("page_rank_decimal") for r in d.get("response", [])})
        except Exception as e:
            print("Open PageRank error:", e)
    return out


def cmd_backlinks(a):
    key = os.environ.get("BING_WMT_API_KEY")
    if not key:
        need("BING_WMT_API_KEY", "backlinks come from Bing Webmaster Tools (free; verify the site there first)")
        return
    base = "https://ssl.bing.com/webmaster/api.svc/json"
    site = a.site if a.site.endswith("/") else a.site + "/"
    links = []
    try:
        counts = jget(f"{base}/GetLinkCounts?" + urllib.parse.urlencode({"siteUrl": site, "page": 0, "apikey": key}))
        pages = [(c["Url"], c["Count"]) for c in counts.get("d", {}).get("Links", [])]
        for url, _ in sorted(pages, key=lambda x: -x[1])[: a.top]:
            det = jget(f"{base}/GetUrlLinks?" + urllib.parse.urlencode({"siteUrl": site, "link": url, "page": 0, "apikey": key}))
            for l in det.get("d", {}).get("Details", []):
                links.append({"target": url, "source": l.get("Url", ""), "anchor": l.get("AnchorText", "")})
    except urllib.error.HTTPError as e:
        print(f"Bing WMT error {e.code}: {e.read().decode()[:200]}"); return
    for l in links:
        l["ref_domain"] = domain_of(l["source"])
    doms = sorted({l["ref_domain"] for l in links})
    ranks = opr(doms)
    for l in links:
        l["domain_rank_0_10"] = ranks.get(l["ref_domain"], "")
    d = store(site); today = str(dt.date.today())
    prev_files = sorted(f for f in os.listdir(d) if f.startswith("backlinks_") and f != f"backlinks_{today}.csv")
    write_csv(os.path.join(d, f"backlinks_{today}.csv"), links)
    print(f"{len(links)} backlinks from {len(doms)} referring domains (Bing index)")
    top = sorted(doms, key=lambda x: -(ranks.get(x) or 0))[:15]
    for x in top:
        print(f"  {ranks.get(x, '-')!s:>4}  {x}")
    if prev_files:
        old = {r["source"] for r in csv.DictReader(open(os.path.join(d, prev_files[-1]), encoding="utf-8-sig"))}
        new = {l["source"] for l in links}
        print(f"since {prev_files[-1][10:20]}: +{len(new - old)} new, -{len(old - new)} lost")
        for s in list(new - old)[:10]:
            print("  NEW ", s)
        for s in list(old - new)[:10]:
            print("  LOST", s)
    if not os.environ.get("OPR_API_KEY"):
        need("OPR_API_KEY", "optional: adds a 0-10 authority score per referring domain")
    print(f"saved -> {d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("speed"); s.add_argument("url"); s.add_argument("--strategy", default="both", choices=["mobile", "desktop", "both"])
    k = sp.add_parser("keywords"); k.add_argument("seed"); k.add_argument("--lang", default="en", choices=["en", "ar"])
    k.add_argument("--country", default="lb"); k.add_argument("--deep", action="store_true")
    r = sp.add_parser("ranks"); r.add_argument("site"); r.add_argument("--days", type=int, default=28); r.add_argument("--country")
    b = sp.add_parser("backlinks"); b.add_argument("site"); b.add_argument("--top", type=int, default=50)
    a = ap.parse_args()
    {"speed": cmd_speed, "keywords": cmd_keywords, "ranks": cmd_ranks, "backlinks": cmd_backlinks}[a.cmd](a)


if __name__ == "__main__":
    main()
