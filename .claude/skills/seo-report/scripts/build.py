#!/usr/bin/env python3
"""Build the branded A4 SEO report (HTML) from collect.py output.

  python3 -I build.py DIR [--notes DIR/notes.json] [--brand "Brand Victory"] [--author "Sam Trabulsi"]
                      [--prepared-for "Client name"] [--tagline "The expert who positions sells."]

Reads DIR/data.json (+ DIR/notes.json if present) and writes DIR/report.html.
Render to PDF with: node render.mjs DIR/report.html DIR/report.pdf
Sections with no data are left out; narrative text comes from notes.json, else from the auto findings.
"""
import argparse, collections, datetime as dt, html, json, math, os, re, urllib.parse

esc = html.escape
C = {"bg": "#0b0b0b", "warm": "#1c1410", "cream": "#f5ede8", "copper": "#c17a5a", "ink": "#1a1512", "mute": "#7d726c", "line": "#e4d8d0"}
LABELS = {"visibility": "Search visibility", "authority": "Authority (backlinks)", "speed": "Page speed (mobile)",
          "onpage": "On-page SEO", "technical": "Technical & indexing", "ai": "AI-search visibility",
          "reach": "Local & language reach", "security": "Security & trust"}
WEIGHTS = {"visibility": 18, "authority": 15, "speed": 12, "onpage": 12, "technical": 12, "ai": 12, "reach": 11, "security": 8}
CNAME = {"usa": "United States", "lbn": "Lebanon", "aus": "Australia", "sau": "Saudi Arabia", "can": "Canada", "are": "UAE", "syr": "Syria",
         "dza": "Algeria", "gbr": "United Kingdom", "ind": "India", "egy": "Egypt", "fra": "France", "deu": "Germany", "kwt": "Kuwait",
         "qat": "Qatar", "jor": "Jordan", "irq": "Iraq", "bhr": "Bahrain", "omn": "Oman", "mar": "Morocco", "tun": "Tunisia", "tur": "Turkey",
         "nld": "Netherlands", "phl": "Philippines", "pak": "Pakistan", "nga": "Nigeria", "bra": "Brazil", "esp": "Spain", "ita": "Italy"}
EFFORT = {"security": "1 day", "technical": "1-2 days", "onpage": "1 week", "speed": "1-2 days", "ai": "1 day", "reach": "2-3 weeks",
          "authority": "Ongoing", "tracking": "1 day"}
GEO_LABELS = {"google_ai": "Google AI readiness", "robots": "AI crawler access (robots)", "content": "Content quality", "meta": "Meta tags",
              "schema": "Structured data", "brand_entity": "Brand / entity signals", "signals": "Technical signals", "llms": "llms.txt",
              "ai_discovery": "AI discovery files"}


def col(s):
    return C["mute"] if s is None else ("#b5432f" if s < 40 else ("#c9922e" if s < 70 else "#3f7d5a"))


def gauge(score, size=170, label="Overall"):
    r = size / 2 - 12; cx = cy = size / 2; circ = 2 * math.pi * r; off = circ * (1 - (score or 0) / 100)
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e9ddd4" stroke-width="12"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col(score)}" stroke-width="12" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off:.1f}" transform="rotate(-90 {cx} {cy})"/>'
            f'<text x="50%" y="48%" text-anchor="middle" font-size="{size*0.27:.0f}" font-weight="900" fill="{C["ink"]}">{score if score is not None else "–"}</text>'
            f'<text x="50%" y="66%" text-anchor="middle" font-size="{11 if size > 140 else 9}" fill="{C["mute"]}" letter-spacing="2">{esc(label.upper())}</text></svg>')


def bar(score, w=150):
    return f'<div class="bar" style="width:{w}px"><span style="width:{score or 0}%;background:{col(score)}"></span></div>'


def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="t {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def callout(text, kind=""):
    return f'<div class="call {kind}">{text}</div>' if text else ""


def checks(items):
    return '<div class="checks">' + "".join(f'<div class="{k}">{t}</div>' for k, t in items) + "</div>"


def kpis(items, cls=""):
    return f'<div class="kpis {cls}">' + "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in items) + "</div>"


def ar(t):
    return f'<span class="ar">{esc(t)}</span>' if re.search(r"[؀-ۿ]", t) else esc(t)


def path(u):
    p = urllib.parse.urlparse(u)
    return (p.path or "/") + (("?" + p.query) if p.query else "")


def short(t, n):
    t = t or ""
    return t if len(t) <= n else t[: n - 1] + "…"


def num(v, d=0):
    try:
        return round(float(str(v).replace(",", "").split()[0]), d)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir"); ap.add_argument("--notes"); ap.add_argument("--brand", default="Brand Victory")
    ap.add_argument("--author", default="Sam Trabulsi"); ap.add_argument("--prepared-for", default="")
    ap.add_argument("--tagline", default="The expert who <span>positions</span> sells.")
    a = ap.parse_args()
    D = json.load(open(os.path.join(a.dir, "data.json")))
    npath = a.notes or os.path.join(a.dir, "notes.json")
    N = json.load(open(npath)) if os.path.exists(npath) else {}
    CO = N.get("callouts", {})
    site = D["site"]; T = D["sites"][site]; P_ = T["profile"]; S = T["onpage"]; SC = T["scores"]
    SP = T.get("speed") or {}; GEO = T.get("geo") or {}; G = D["gsc"]; B = D["bing"]; F = T.get("findings", [])
    comps = [c for c in D.get("competitors", []) if c in D["sites"]]
    date = dt.date.fromisoformat(D["date"]); pdate = f"{date.day} {date:%B %Y}"
    brand = a.brand; BR = brand.upper()
    pages = []

    def page(title, kicker, body):
        n = len(pages) + 1
        pages.append(f'''<section class="page"><div class="ph"><div class="kick">{n-1:02d} · {kicker}</div><div class="brandmark">{esc(BR)} · SEO REPORT</div></div>
<h1>{title}</h1>{body}<div class="pf"><span>{esc(site)} · {pdate}</span><span>{n:02d}</span></div></section>''')

    mob = SP.get("mobile", {}); desk = SP.get("desktop", {})
    ms, ds = mob.get("scores", {}).get("performance"), desk.get("scores", {}).get("performance")
    plat = GEO.get("platforms", {})
    overall = SC.get("overall")

    # ------------------------------------------------ cover
    name, _, tld = site.partition(".")
    fs = 64 if len(site) <= 18 else (50 if len(site) <= 26 else 38)
    tiles = [(overall, "Overall score /100")]
    if G.get("available"):
        tiles.append((G["t28"].get("clicks", 0), "Google clicks · last 28 days"))
    else:
        tiles.append((ms if ms is not None else "–", "Mobile speed /100"))
    if comps:
        ranked = sorted([site] + comps, key=lambda s: -(D["sites"][s]["scores"].get("public") or 0))
        tiles.append((f"#{ranked.index(site)+1}<small>/{len(ranked)}</small>", "Rank vs competitors"))
    elif B.get("available"):
        tiles.append((B["ref_domains"], "Sites linking in (Bing)"))
    else:
        tiles.append((GEO.get("score", "–"), "AI visibility /100"))
    tiles.append((plat.get("chatgpt", "–"), "ChatGPT visibility /100"))
    sources = ["PageSpeed Insights", "GEO Optimizer", "site crawl", "public DNS/RDAP"]
    if G.get("available"): sources.insert(0, "Google Search Console")
    if B.get("available"): sources.insert(1, "Bing Webmaster Tools")
    if comps: sources.append(f"{len(comps)} competitor sites")
    pf = f" for <b>{esc(a.prepared_for)}</b>" if a.prepared_for else ""
    pages.append(f'''<section class="cover"><div class="ctop"><div class="kick lt">{esc(BR)}</div><div class="kick lt">CONFIDENTIAL</div></div>
<div class="cmid"><div class="kick lt">SEO &amp; AI-SEARCH VISIBILITY REPORT</div><div class="ctitle" style="font-size:{fs}px">{esc(name)}<span>.{esc(tld)}</span></div>
<div class="csub">{N.get("cover_sub") or "How Google, Bing and AI answer engines see the site" + (", how it compares with competitors," if comps else "") + " and the 90-day plan to fix it."}</div></div>
<div class="cgrid">{"".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in tiles)}</div>
<div class="cfoot"><div>Prepared{pf} by <b>{esc(a.author)}</b> · {esc(brand)}</div><div>{pdate} · Data: {", ".join(sources)}</div></div></section>''')

    # ------------------------------------------------ executive summary
    def detail(k):
        if k == "visibility":
            return f'{G["t28"].get("clicks", 0)} clicks / 28 days' if G.get("available") else "needs Search Console access"
        if k == "authority":
            if T.get("opr") not in (None, ""): return f'{T["opr"]}/10 Open PageRank'
            return f'{B["ref_domains"]} linking sites (Bing)' if B.get("available") else "not measured (add OPR key)"
        if k == "speed":
            return f"mobile {ms} · desktop {ds}" if ms is not None else "PageSpeed unavailable"
        if k == "onpage":
            return f'{S["no_desc"]} no description · {S["thin"]} thin pages'
        if k == "technical":
            return f'{len(set(S["junk"]) | set(S.get("empty", [])))} junk/empty pages · {S["errors"]} errors'
        if k == "ai":
            return f'ChatGPT {plat.get("chatgpt", "–")} · Google AI {plat.get("google_ai", "–")}' if plat else "audit unavailable"
        if k == "reach":
            return ("Arabic pages ✓" if T["reach"]["arabic"] else "no Arabic pages") + (" · local schema ✓" if T["reach"]["local_schema"] else " · no local schema")
        if k == "security":
            miss = sum(1 for v in P_["security_headers"].values() if not v)
            return "SPAM FOUND" if P_.get("spam") else f"clean · {miss} headers missing"
    rows = "".join(f'<tr><td>{LABELS[k]}</td><td>{bar(SC.get(k), 120)}</td><td class="r"><b style="color:{col(SC.get(k))}">{SC.get(k) if SC.get(k) is not None else "–"}</b></td><td class="m">{esc(detail(k))}</td></tr>' for k in WEIGHTS)
    short3 = N.get("short") or [{"title": LABELS.get(f["area"], f["area"].title()), "body": esc(f["issue"]) + ". " + esc(f["fix"]) + "."} for f in F[:3]]
    prios = N.get("priorities") or [{"action": esc(f["fix"]), "why": esc(f["issue"]), "effort": EFFORT.get(f["area"], "")} for f in F[:5]]
    page("Executive summary", "OVERVIEW", f'''
<div class="two"><div class="gauge">{gauge(overall)}<p class="m c">{esc(brand)} weighted index across {sum(1 for k in WEIGHTS if SC.get(k) is not None)} measured areas</p></div>
<div><table class="t sc">{rows}</table></div></div>
<h2>The short version</h2>
<div class="cards">{"".join(f'<div class="card"><div class="n">{i+1}</div><b>{c["title"]}</b><p>{c["body"]}</p></div>' for i, c in enumerate(short3))}</div>
<h2>Top {len(prios)} priorities</h2>
{table(["#", "Action", "Why it matters", "Effort"], [[str(i+1), p["action"], p["why"], p.get("effort", "")] for i, p in enumerate(prios)])}''')

    # ------------------------------------------------ search console
    if G.get("available"):
        t28, tp28, t90 = G["t28"], G["tp28"], G["t90"]
        def delta(c, p):
            if not p: return ""
            d = round((c - p) / p * 100)
            return f' <span class="{"up" if d >= 0 else "down"}">{"▲" if d >= 0 else "▼"} {abs(d)}%</span>'
        monthly = collections.OrderedDict()
        for r in sorted(G["monthly"], key=lambda r: r["keys"][0]):
            k = r["keys"][0][:7]; m = monthly.setdefault(k, [0, 0]); m[0] += r["clicks"]; m[1] += r["impressions"]
        cur = D["date"][:7]
        months = [(k, v) for k, v in monthly.items() if k < cur][-15:]
        chart = ""
        if len(months) >= 3:
            W, H, pad = 640, 210, 30
            mx_i = max(v[1] for _, v in months) or 1; mx_c = max(v[0] for _, v in months) or 1; bw = (W - pad * 2) / len(months)
            o = [f'<svg width="100%" viewBox="0 0 {W} {H+34}">']
            for i, (k, (c, im)) in enumerate(months):
                x = pad + i * bw; h = (im / mx_i) * (H - 30)
                o.append(f'<rect x="{x+4:.1f}" y="{H-h:.1f}" width="{bw-8:.1f}" height="{h:.1f}" rx="3" fill="#e2cfc3"/>')
                o.append(f'<text x="{x+bw/2:.1f}" y="{H-6:.1f}" font-size="9" text-anchor="middle" fill="{C["ink"]}" opacity="0.65">{im}</text>')
                o.append(f'<text x="{x+bw/2:.1f}" y="{H+14}" font-size="9" text-anchor="middle" fill="{C["mute"]}">{k[5:]}/{k[2:4]}</text>')
            pts = " ".join(f'{pad+i*bw+bw/2:.1f},{H-(c/mx_c)*(H-60)-10:.1f}' for i, (_, (c, _)) in enumerate(months))
            o.append(f'<polyline points="{pts}" fill="none" stroke="{C["copper"]}" stroke-width="2.5"/>')
            for i, (_, (c, _)) in enumerate(months):
                x = pad + i * bw + bw / 2; y = H - (c / mx_c) * (H - 60) - 10
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{C["copper"]}"/><text x="{x:.1f}" y="{y-7:.1f}" font-size="9" font-weight="700" text-anchor="middle" fill="{C["copper"]}">{c}</text>')
            o.append(f'<text x="{pad}" y="{H+30}" font-size="10" fill="{C["mute"]}">■ impressions (bars) &nbsp; <tspan fill="{C["copper"]}">● clicks (line)</tspan></text></svg>')
            mname = lambda k: dt.date(int(k[:4]), int(k[5:]), 1).strftime("%b %Y")
            chart = f"<h3>{len(months)}-month trend ({mname(months[0][0])} – {mname(months[-1][0])})</h3>" + "".join(o)
        ctry = [(CNAME.get(r["keys"][0].lower(), r["keys"][0].upper()), r["impressions"], r["clicks"]) for r in sorted(G["countries90"], key=lambda r: -r["impressions"])[:8]]
        cmax = max([c[1] for c in ctry] or [1])
        crow = "".join(f'<tr><td>{esc(n)}</td><td style="width:50%"><div class="hb"><span style="width:{i/cmax*100:.0f}%"></span></div></td><td class="r">{i}</td><td class="r">{c}</td></tr>' for n, i, c in ctry)
        prow = [[esc(short(path(r["keys"][0]) if site in r["keys"][0] else r["keys"][0], 38)) + (" <span class='m'>(www)</span>" if "//www." in r["keys"][0] else ""),
                 str(r["impressions"]), str(r["clicks"])] for r in sorted(G["pages90"], key=lambda r: -r["impressions"])[:8]]
        tot_i = sum(r["impressions"] for r in G["countries90"]) or 1
        top_c = ctry[0] if ctry else ("–", 0, 0)
        auto = (f"<b>Read this as:</b> {round(top_c[1]/tot_i*100)}% of impressions (last 90 days) come from {esc(top_c[0])}. "
                f"Average position is {t90.get('position', 0):.1f}" + (" (page 2), where almost nobody clicks." if t90.get("position", 0) > 10 else "."))
        page("Google search performance", "SEARCH CONSOLE (REAL DATA)", f'''
{kpis([(f'{t28.get("clicks", 0)}', f'Clicks · 28 days{delta(t28.get("clicks", 0), tp28.get("clicks", 0))}'),
       (f'{t28.get("impressions", 0)}', f'Impressions · 28 days{delta(t28.get("impressions", 0), tp28.get("impressions", 0))}'),
       (f'{t28.get("position", 0):.1f}', f'Avg position (was {tp28.get("position", 0):.1f})'),
       (f'{t90.get("clicks", 0)} / {t90.get("impressions", 0)}', 'Clicks / impressions · 90 days')])}
{chart}
<div class="two eq"><div><h3>Where impressions come from (90 days)</h3><table class="t sm"><thead><tr><th>Country</th><th></th><th class="r">Impr.</th><th class="r">Clicks</th></tr></thead><tbody>{crow}</tbody></table></div>
<div><h3>Top pages (90 days)</h3>{table(["Page", "Impr.", "Clicks"], prow, "sm")}</div></div>
{callout(CO.get("search") or auto)}''')
        qs = sorted(G["queries90"], key=lambda r: -r["impressions"])[:16]
        top3 = [r["keys"][0] for r in qs if r["position"] <= 3][:4]
        near = [r["keys"][0] for r in qs if 8 <= r["position"] <= 20][:4]
        auto_q = ""
        if top3: auto_q += callout("<b>Already in the top 3</b> for " + ", ".join(f"<i>{ar(q)}</i>" for q in top3) + ", but at small volumes.")
        if near: auto_q += callout("<b>Close to page 1:</b> " + ", ".join(f"<i>{ar(q)}</i>" for q in near) + ". Strengthening one page per topic is the quickest traffic gain.", "dark")
        page("What you rank for", "SEARCH QUERIES", table(["Search term (90 days)", "Impressions", "Clicks", "Avg position"],
             [[ar(r["keys"][0]), str(r["impressions"]), str(r["clicks"]), f'{r["position"]:.1f}'] for r in qs])
             + (callout(CO["queries"]) if CO.get("queries") else f'<div class="two eq">{auto_q}</div>'))

    # ------------------------------------------------ competitors
    if comps:
        allS = [site] + comps
        def v(s, f):
            try: return f(D["sites"][s])
            except Exception: return None
        metrics = [
            ("Public score /100", lambda x: x["scores"].get("public"), True),
            ("Mobile speed", lambda x: x["speed"]["mobile"]["scores"]["performance"], True),
            ("Desktop speed", lambda x: x["speed"]["desktop"]["scores"]["performance"], True),
            ("AI visibility", lambda x: x["geo"]["score"], True),
            ("ChatGPT visibility", lambda x: x["geo"]["platforms"]["chatgpt"], True),
        ]
        if D["keys"].get("opr"):
            metrics.append(("Authority (OPR 0-10)", lambda x: x["opr"], True))
        metrics += [
            ("Pages in sitemap", lambda x: x["profile"]["sitemap"]["urls"], True),
            ("Blog posts", lambda x: x["profile"]["sitemap"]["posts"], True),
            ("Last blog post", lambda x: x["profile"]["sitemap"]["latest_post"] or "–", None),
            ("Avg words / page", lambda x: x["onpage"]["avg_words"], True),
            ("Schema types", lambda x: len(x["onpage"]["schema_types"]), True),
            ("FAQ schema", lambda x: "✓" if "FAQPage" in x["onpage"]["schema_types"] else "–", None),
            ("Arabic pages", lambda x: x["onpage"]["arabic_pages"], True),
            ("Domain age (years)", lambda x: x["profile"]["facts"].get("age_years"), True),
            ("Security headers /6", lambda x: sum(x["profile"]["security_headers"].values()), True),
            ("llms.txt", lambda x: "✓" if x["profile"]["llms_txt"] else "–", None),
            ("WhatsApp / booking", lambda x: "✓" if {"WhatsApp", "Booking"} & set(x["profile"]["conversion"]) else "–", None),
            ("Analytics / pixel", lambda x: ", ".join(t.replace("Google Analytics 4", "GA4").replace("Google Tag Manager", "GTM") for t in x["profile"]["tracking"][:3]) or "none", None),
            ("Platform", lambda x: ", ".join([t for t in x["profile"]["tech"] if t not in ("Bootstrap",)][:3]) or "–", None),
        ]
        rows, beats = [], []
        for label, f, higher in metrics:
            vals = [v(s, f) for s in allS]
            best = None
            if higher and any(isinstance(x, (int, float)) for x in vals):
                best = max(x for x in vals if isinstance(x, (int, float)))
            cells = []
            for i, x in enumerate(vals):
                txt = "–" if x is None else esc(str(x))
                cells.append(f'<b class="best">{txt}</b>' if best is not None and x == best and vals.count(best) < len(vals) else txt)
            rows.append([label] + cells)
            tv = vals[0]
            if higher and isinstance(tv, (int, float)):
                w = [(allS[i], x) for i, x in enumerate(vals[1:], 1) if isinstance(x, (int, float)) and x > tv * 1.15 + 1]
                if w: beats.append(f"<b>{label}</b>: " + ", ".join(f"{s} {x}" for s, x in w) + f" vs your {tv}")
        head = ["Metric"] + [f'<span class="you">{esc(short(s, 22))}</span>' if s == site else esc(short(s, 22)) for s in allS]
        pub = [(s, D["sites"][s]["scores"].get("public") or 0) for s in allS]
        pmax = max([p for _, p in pub] or [1]) or 1
        bars = "".join(f'<div class="cbar"><span class="cl{" you" if s == site else ""}">{esc(short(s, 26))}</span><div class="hb"><span style="width:{p/pmax*100:.0f}%;{"background:" + C["ink"] if s == site else ""}"></span></div><b>{p}</b></div>' for s, p in sorted(pub, key=lambda x: -x[1]))
        note = (f'<p class="m">Competitors were picked from the top results for: {", ".join(ar(k) for k in D["keywords"])}.</p>' if D.get("competitors_auto")
                else '<p class="m">Same public checks run on every site on the same day. Best value per row in bold.</p>')
        auto_c = ("<b>Where they beat you:</b><br>" + "<br>".join(beats[:6])) if beats else "<b>You lead</b> on most public measures; keep the gap with content and links."
        page("You vs your competitors", "COMPETITOR SNAPSHOT", f'''{note}
<div class="cbars">{bars}</div>
{table(head, rows, "sm cmp")}
{callout(CO.get("competitors") or auto_c, "dark" if not CO.get("competitors") else "")}''')

    # ------------------------------------------------ rankings & content gap
    ranks = [r for r in D.get("ranks", []) if r.get("results") is not None]
    if ranks or D.get("content_gap"):
        body = ""
        if ranks:
            allS = [site] + comps
            def pos(r, s):
                p = r["positions"].get(s)
                return f'<b class="best">#{p}</b>' if p and p <= 3 else (f"#{p}" if p else "–")
            body += table(["Keyword", '<span class="you">You</span>'] + [esc(short(c, 16)) for c in comps] + ["Top 3 results"],
                          [[ar(r["keyword"]), pos(r, site)] + [pos(r, c) for c in comps] +
                           ["<span class='m'>" + ", ".join(esc(short(urllib.parse.urlparse(u).netloc.removeprefix("www."), 24)) for u in r["results"][:3]) + "</span>"] for r in ranks], "sm")
            body += f'<p class="m">Top-10 positions from DuckDuckGo (Bing index), region {esc(D["country"].upper())}, checked {pdate}. Google positions for your own site are in the Search Console pages.</p>'
        blocked = [r["keyword"] for r in D.get("ranks", []) if r.get("results") is None]
        if blocked:
            body += f'<p class="m">Not checked (search engine refused the request): {", ".join(ar(k) for k in blocked)}.</p>'
        gap = N.get("content_gap") or D.get("content_gap", [])
        if gap:
            body += f'<h2>Topics competitors cover that you don\'t</h2><div class="chips">{"".join(f"<span>{ar(g)}</span>" for g in gap[:20])}</div>'
        auto_r = ""
        if ranks:
            mine = [r["keyword"] for r in ranks if r["positions"].get(site)]
            auto_r = ("<b>You appear in the top 10 for:</b> " + ", ".join(ar(k) for k in mine) + ".") if mine else \
                     "<b>You're not in the top 10 for any of these searches.</b> Each needs a dedicated, well-linked page targeting it."
        page("Rankings &amp; content gaps", "WHO SHOWS UP WHEN PEOPLE SEARCH", body + callout(CO.get("rankings") or auto_r))

    # ------------------------------------------------ speed
    if mob or desk:
        def mrow(name, key, target, good):
            vv = mob.get(key, "–"); n = num(vv, 2)
            st = "–" if n is None else ('<b class="ok-t">Good</b>' if good(n) else '<b class="bad-t">Poor</b>')
            return [name, esc(str(vv)), target, st]
        sc_m = mob.get("scores", {})
        mt = [mrow("Largest Contentful Paint (main content visible)", "LCP", "&lt; 2.5 s", lambda n: n <= 2.5),
              mrow("First Contentful Paint", "FCP", "&lt; 1.8 s", lambda n: n <= 1.8),
              mrow("Total Blocking Time", "TBT", "&lt; 200 ms", lambda n: n <= 200),
              mrow("Cumulative Layout Shift", "CLS", "&lt; 0.1", lambda n: n <= 0.1),
              ["Accessibility / Best practices / SEO", f'{sc_m.get("accessibility", "–")} / {sc_m.get("best-practices", "–")} / {sc_m.get("seo", "–")}', "90+",
               '<b class="ok-t">Good</b>' if min(sc_m.get("accessibility", 0), sc_m.get("seo", 0)) >= 90 else '<b class="bad-t">Fix</b>']]
        fixes = [[esc(t), f"~{ms_/1000:.1f} s"] for ms_, t in mob.get("opps", [])[:5]]
        field = mob.get("field_LCP", "n/a")
        hm = P_["home"]
        auto_s = (f"<b>Why it's slow:</b> the homepage loads <b>{hm.get('scripts', 0)} script files and {hm.get('css', 0)} stylesheets</b>"
                  + (f" on {', '.join(t for t in P_['tech'] if t in ('WordPress', 'Elementor', 'Divi', 'Wix', 'Shopify', 'Webflow', 'Squarespace'))}" if P_["tech"] else "")
                  + ". " + ("Real-visitor (CrUX) data isn't available yet: too few Chrome visits." if field in ("n/a", None) else f"Real visitors: LCP rated <b>{esc(str(field))}</b>."))
        page("Page speed &amp; Core Web Vitals", "GOOGLE PAGESPEED INSIGHTS", f'''
<div class="two eq c"><div>{gauge(ms, 150, "Mobile")}</div><div>{gauge(ds, 150, "Desktop")}</div></div>
{table(["Metric (mobile, lab)", "Result", "Google target", "Status"], mt)}
{"<h3>Biggest fixes (estimated time saved on mobile)</h3>" + table(["Fix", "Saving"], fixes, "sm") if fixes else ""}
{callout(auto_s)}{callout(CO.get("speed"), "dark")}''')

    # ------------------------------------------------ technical
    rb = P_["robots"]; fct = P_.get("facts", {})
    ck = [("ok" if P_["https_redirect"] else "bad", "http → https redirect"),
          ("ok" if P_["one_host"] else "bad", "www and non-www merged" if P_["one_host"] else "www and non-www not merged"),
          ("ok" if rb["exists"] else "bad", "robots.txt present" + (", sitemap declared" if rb["sitemaps"] else "")),
          ("ok" if P_["sitemap"]["urls"] else "bad", f'Sitemap: {P_["sitemap"]["urls"]} URLs' if P_["sitemap"]["urls"] else "No XML sitemap found"),
          ("ok" if S["errors"] == 0 else "bad", f'{S["errors"]} broken pages in crawl' if S["errors"] else f'All {len(P_["crawl"])} crawled URLs load'),
          ("ok" if S["no_canonical"] == 0 else "warn", "Canonical tag on every page" if S["no_canonical"] == 0 else f'{S["no_canonical"]} pages without canonical'),
          ("ok" if not rb["ai_blocked"] else "warn", "AI crawlers allowed" if not rb["ai_blocked"] else "Blocks: " + ", ".join(rb["ai_blocked"][:3])),
          ("ok" if not (S["junk"] or S.get("empty")) else "bad", f'{len(set(S["junk"]) | set(S.get("empty", [])))} junk / empty pages public' if (S["junk"] or S.get("empty")) else "No junk pages found"),
          ("ok" if not P_["public_docs"] else "bad", f'{len(P_["public_docs"])} documents publicly reachable' if P_["public_docs"] else "No public documents linked")]
    if fct.get("ssl_days_left") is not None:
        ck.append(("ok" if fct["ssl_days_left"] > 14 else "bad", f'SSL valid {fct["ssl_days_left"]} more days ({esc(fct.get("ssl_issuer", ""))})'))
    if S["noindex"]:
        ck.append(("warn", f'{S["noindex"]} sitemap pages set to noindex'))
    fix = []
    for u in P_["public_docs"][:3]: fix.append([esc(short(path(u), 48)), "Public document", "Check for confidential content; delete + Google Removals"])
    for u in S["junk"][:8]: fix.append([esc(short(path(u), 48)), "Test / duplicate / old page", "Delete or 301 to the live page"])
    for u in [x for x in S.get("empty", []) if x not in S["junk"]][:8]: fix.append([esc(short(path(u), 48)), "Near-empty page (under 60 words)", "noindex + remove from sitemap, or delete"])
    for c in [c for c in P_["crawl"] if c.get("status", 200) >= 400 or c.get("status") == 0][:4]: fix.append([esc(short(path(c["requested"]), 48)), f'HTTP {c.get("status")}', "Fix or remove from sitemap"])
    page("Technical health &amp; indexing", f'CRAWL OF {len(P_["crawl"])} PAGES', checks(ck)
         + (("<h3>Pages to delete, redirect or hide from Google</h3>" + table(["Page", "Problem", "Recommended action"], fix[:14], "sm")) if fix else "")
         + callout(CO.get("technical")))

    # ------------------------------------------------ on-page
    good = [c for c in P_["crawl"] if c.get("status") == 200 and "title" in c and c["requested"] not in S["junk"] and c["requested"] not in S.get("empty", [])]
    def issue(c):
        if not c["desc"]: return '<b class="bad-t">No meta description</b>'
        if c["words"] < 300: return '<b class="bad-t">Thin page</b>'
        if c["h1_count"] != 1: return f'{c["h1_count"]} H1 headings'
        if c["title_len"] > 65: return "Title too long"
        if c["title_len"] < 15: return "Title too short"
        return '<b class="ok-t">Good</b>'
    kp = [[esc(short(path(c["url"]), 30)), esc(short(c["title"], 52)), str(c["words"]), issue(c)] for c in good[:10]]
    alt_pct = round(S["imgs_no_alt"] / S["imgs"] * 100) if S["imgs"] else 0
    page("On-page SEO &amp; content", "TITLES, HEADINGS, CONTENT", kpis([(S["no_desc"], "pages without a meta description"), (S["multi_h1"], "pages with 2+ H1 headings"),
         (S["thin"], "pages under 300 words"), (f"{alt_pct}%", f'images without alt text ({S["imgs_no_alt"]} of {S["imgs"]})')])
         + "<h3>Key pages</h3>" + table(["Page", "Current title", "Words", "Issue"], kp, "sm")
         + (f'<p class="m">Blog: {P_["sitemap"]["posts"]} posts, latest {P_["sitemap"]["latest_post"]}. Average {S["avg_words"]} words per page across {S["pages"]} pages crawled.</p>' if P_["sitemap"]["posts"] else "")
         + callout(CO.get("onpage")))

    # ------------------------------------------------ AI visibility
    if GEO:
        bd, mx = GEO.get("breakdown", {}), GEO.get("max", {})
        brs = "".join(f'<tr><td>{GEO_LABELS.get(k, k)}</td><td style="width:45%">{bar(round(bd.get(k, 0) / m * 100) if m else 0, 150)}</td><td class="r">{bd.get(k, 0)}/{m}</td></tr>'
                      for k, m in sorted(mx.items(), key=lambda x: -x[1]))
        recs = [[esc(short(r.split(":")[0] if len(r) > 110 else r, 120))] for r in GEO.get("recommendations", [])[:7]]
        page("AI-search visibility &amp; structured data", "CHATGPT · PERPLEXITY · GOOGLE AI", f'''
<div class="two"><div class="gauge">{gauge(GEO.get("score"), 160, "AI visibility")}<p class="m c">GEO Optimizer score (good band 68-85)</p></div>
<div>{kpis([(plat.get("chatgpt", "–"), "ChatGPT"), (plat.get("perplexity", "–"), "Perplexity"), (plat.get("google_ai", "–"), "Google AI Overviews")], "k3")}<table class="t sc">{brs}</table></div></div>
<h3>Structured data found</h3><div class="chips">{"".join(f"<span>{esc(t)}</span>" for t in S["schema_types"][:18]) or "<span>none</span>"}</div>
<h3>What to fix for AI answers</h3>{table(["Recommendation"], recs, "sm")}
{callout(CO.get("ai"))}''')

    # ------------------------------------------------ authority & keywords
    if T.get("opr") not in (None, ""):
        big, bl = T["opr"], "Open PageRank (0-10)"
    elif B.get("available"):
        big, bl = B["ref_domains"], f'websites linking to {esc(site)} in Bing\'s index'
    else:
        big, bl = "?", "authority not measured: add a free OPR_API_KEY"
    auth_txt = CO.get("authority") or ("<b>Authority is earned through links.</b> Other websites linking to you tell Google you're trusted. "
        "Quick wins: link the site from every social profile and Google Business Profile, add a credit link on client sites you built, "
        "list in local business directories, and publish guest articles and podcast appearances.")
    facts = []
    if fct.get("age_years") is not None: facts.append(f'Domain age: <b>{fct["age_years"]} years</b> (registered {fct.get("registered", "")})')
    if P_["social"]: facts.append("Social profiles linked from the site: " + ", ".join(P_["social"]))
    else: facts.append("<b>No social profiles linked</b> from the homepage")
    kwh = ""
    seeds = list(D.get("keyword_ideas", {}).items())[:4]
    if seeds:
        blocks = []
        for q, rows_ in seeds:
            sel = [r for r in rows_ if r["intent"] in ("commercial", "local", "question")][:7] or rows_[:7]
            blocks.append(f'<div><table class="t sm"><thead><tr><th>{ar(q)}</th><th>Intent</th></tr></thead><tbody>'
                          + "".join(f'<tr><td>{ar(r["keyword"])}</td><td class="m">{r["intent"]}</td></tr>' for r in sel) + "</tbody></table></div>")
        kwh = '<h2>Keyword ideas from Google, YouTube &amp; Bing autocomplete</h2><div class="two eq">' + "".join(blocks) + "</div>" \
              + '<p class="m">Autocomplete shows what people actually type, not exact search volumes.</p>'
    page("Authority &amp; keyword opportunities", "BACKLINKS + WHAT PEOPLE SEARCH", f'''
<div class="two"><div class="bigzero"><b>{big}</b><span>{bl}</span></div><div>{callout(auth_txt)}<p>{"<br>".join(facts)}</p></div></div>{kwh}''')

    # ------------------------------------------------ security, trust & tracking
    sh = P_["security_headers"]
    sk = [("bad" if P_.get("spam") else "ok", "Spam / hacked links found" if P_.get("spam") else "No injected spam links")]
    sk += [("ok" if v else "bad", ("" if v else "No ") + k) for k, v in sh.items()]
    sk.append(("bad" if P_["version_leak"] else "ok", "Server/CMS version visible" if P_["version_leak"] else "Versions hidden"))
    sk.append(("ok" if fct.get("spf") else "bad", "SPF email record" if fct.get("spf") else "No SPF record"))
    sk.append(("ok" if fct.get("dmarc") else "bad", f'DMARC ({fct.get("dmarc")})' if fct.get("dmarc") else "No DMARC (email spoofable)"))
    if fct.get("email_host"): sk.append(("ok" if fct["email_host"] != "none" else "warn", f'Email: {fct["email_host"]}'))
    tr = [("ok" if t in P_["tracking"] else "bad", t) for t in ("Google Analytics 4", "Google Tag Manager", "Meta Pixel", "TikTok Pixel", "LinkedIn Insight", "Microsoft Clarity")]
    cv = [("ok" if t in P_["conversion"] else "bad", t) for t in ("WhatsApp", "Booking", "Form", "Phone link", "Live chat", "Newsletter")]
    spam_box = callout("<b>Security incident:</b> " + esc("; ".join(P_["spam"][:3])) + ". Clean the site, update everything, rotate all passwords, then request a review in Search Console.", "red") if P_.get("spam") else ""
    page("Security, trust &amp; tracking", "SAFETY + CONVERSION CHECKS", f'''{spam_box}{checks(sk)}
<h3>Tracking (can you measure and retarget visitors?)</h3>{checks(tr)}
<h3>Ways for a visitor to contact or buy</h3>{checks(cv)}
<h3>Built with</h3><div class="chips">{"".join(f"<span>{esc(t)}</span>" for t in P_["tech"]) or "<span>unknown</span>"}{f"<span>{esc(P_['generator'])}</span>" if P_["generator"] else ""}</div>
{callout(CO.get("security"))}''')

    # ------------------------------------------------ plan
    plan = N.get("plan")
    if not plan:
        plan = []
        s3 = [f for f in F if f["sev"] == 3]; s2 = [f for f in F if f["sev"] == 2]; s1 = [f for f in F if f["sev"] == 1]
        if s3: plan.append({"when": "Week 1", "action": "; ".join(esc(f["fix"]) for f in s3[:3]), "result": "Biggest risks and blockers removed"})
        tech = [f for f in s2 if f["area"] in ("technical", "speed", "tracking")]
        if tech: plan.append({"when": "Week 2", "action": "; ".join(esc(f["fix"]) for f in tech[:3]), "result": "Clean index, faster site, measurable traffic"})
        onp = [f for f in s2 + s1 if f["area"] in ("onpage", "ai")]
        if onp: plan.append({"when": "Weeks 3-4", "action": "; ".join(esc(f["fix"]) for f in onp[:3]), "result": "Higher click-through, better AI citations"})
        rch = [f for f in s2 + s1 if f["area"] == "reach"]
        if rch: plan.append({"when": "Weeks 4-8", "action": "; ".join(esc(f["fix"]) for f in rch[:2]), "result": "Reach the local market in its own language"})
        plan.append({"when": "Ongoing", "action": "2 articles a month on service topics; earn links from profiles, directories, partners and press", "result": "Steady growth in impressions, clicks and authority"})
        sec = [f for f in s1 if f["area"] == "security"]
        if sec: plan.append({"when": "Any time", "action": "; ".join(esc(f["fix"]) for f in sec[:3]), "result": "Hardened site and email"})
        plan.append({"when": "Weekly", "action": f"Automated {esc(brand)} SEO check: rankings, speed, spam scan", "result": "Every change measured"})
    targets = N.get("targets")
    if not targets:
        targets = []
        if G.get("available"): targets.append({"value": f'{max(30, G["t28"].get("clicks", 0) * 3)}+', "label": f'Google clicks / month (from {G["t28"].get("clicks", 0)})'})
        if ms is not None: targets.append({"value": "70+", "label": f"mobile speed score (from {ms})"})
        if GEO.get("score") is not None: targets.append({"value": f'{min(95, max(80, GEO["score"] + 10))}+', "label": f'AI visibility (from {GEO["score"]})'})
        targets.append({"value": "15+", "label": "new sites linking to you"})
        targets = targets[:4]
    page("90-day action plan", "ROADMAP", table(["When", "Action", "Expected result"], [[f'<b>{p["when"]}</b>', p["action"], p["result"]] for p in plan])
         + f'<h2>Targets for day 90</h2>{kpis([(t["value"], t["label"]) for t in targets], "k3" if len(targets) == 3 else "")}' + callout(CO.get("plan")))

    # ------------------------------------------------ method
    src = []
    if G.get("available"): src.append(["Search performance", f'Google Search Console API ({esc(G["property"])})', "Real data: last 28/90 days and monthly trend"])
    src.append(["Speed", "Google PageSpeed Insights API (Lighthouse)", f"One run per device on {pdate}; lab scores vary run to run"])
    if B.get("available"): src.append(["Backlinks", "Bing Webmaster Tools API", "Bing's link index for the verified site"])
    if D["keys"].get("opr"): src.append(["Authority", "Open PageRank API", "0-10 domain authority for every site"])
    if GEO: src.append(["AI visibility", "GEO Optimizer (open source)", "AI crawlers, schema, content and trust checks"])
    src.append(["On-page & technical", f'Crawl of {len(P_["crawl"])} sitemap URLs', "Titles, descriptions, headings, canonicals, schema, images"])
    if comps: src.append(["Competitors", f"Same public checks on {len(comps)} sites", "Speed, AI visibility, crawl, schema, tech, tracking"])
    if D.get("ranks"): src.append(["Rankings", "DuckDuckGo results (Bing index)", f'Top 10 for {len(D["ranks"])} searches, region {esc(D["country"].upper())}'])
    if D.get("keyword_ideas"): src.append(["Keywords", "Google, YouTube & Bing autocomplete", "Search phrasing, not volumes"])
    src.append(["Security & trust", "HTTP headers, Google DNS, RDAP, crt.sh, spam-link scan", "Homepage, DNS and certificate checks"])
    wtxt = ", ".join(f"{LABELS[k].lower()} {WEIGHTS[k]}%" for k in WEIGHTS)
    pages_html_end = f'''<div class="endcard"><div class="kick">{esc(BR)}</div><div class="et">{a.tagline}</div><div class="m" style="color:#b9aca4">{esc(N.get("contact", site))}</div></div>'''
    page("Method &amp; data sources", "APPENDIX", table(["Area", "Source", "Notes"], src, "sm")
         + f'<h3>About the overall score</h3><p>The overall score ({overall}/100) is the {esc(brand)} weighted index: {wtxt}. Areas that could not be measured are left out and the rest re-weighted. '
         + ("The competitor “public score” uses only checks that can be run on any site (no Search Console)." if comps else "") + "</p>" + pages_html_end)

    from_css = CSS
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(brand)} SEO Report: {esc(site)}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Tajawal:wght@500;700&display=block" rel="stylesheet"><style>{from_css}</style></head><body>{"".join(pages)}</body></html>'''
    out = os.path.join(a.dir, "report.html")
    open(out, "w").write(doc)
    print(f"overall {overall} · {len(pages)} pages -> {out}")


CSS = f'''@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,Arial,sans-serif;color:{C["ink"]};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page,.cover{{width:210mm;height:297mm;padding:16mm 15mm 14mm;position:relative;overflow:hidden;page-break-after:always;background:{C["cream"]}}}
.cover{{background:linear-gradient(160deg,{C["bg"]} 0%,{C["warm"]} 100%);color:{C["cream"]};display:flex;flex-direction:column;justify-content:space-between;padding:18mm}}
.kick{{font-size:9.5px;letter-spacing:3px;font-weight:700;color:{C["copper"]}}}.lt{{color:{C["copper"]}}}
.ctop,.cfoot{{display:flex;justify-content:space-between;font-size:10px;color:#b9aca4}}.cfoot div:last-child{{max-width:60%;text-align:right}}
.ctitle{{font-weight:900;letter-spacing:-2px;margin:10px 0 8px;word-break:break-all}}.ctitle span{{color:{C["copper"]}}}.csub{{font-size:17px;color:#d9ccc4;max-width:80%;line-height:1.45}}
.cgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.cgrid div{{border:1px solid #3a2e28;border-radius:12px;padding:14px}}.cgrid b{{display:block;font-size:34px;font-weight:900;color:{C["cream"]}}}.cgrid b small{{font-size:16px;color:#b9aca4}}.cgrid span{{font-size:10px;color:#b9aca4}}
.ph{{display:flex;justify-content:space-between;align-items:center}}.brandmark{{font-size:8.5px;letter-spacing:2.5px;color:{C["mute"]}}}
h1{{font-size:27px;font-weight:900;letter-spacing:-.5px;margin:6px 0 12px}}h2{{font-size:15px;margin:14px 0 8px}}h3{{font-size:12.5px;margin:12px 0 6px;color:{C["ink"]}}}
p{{font-size:10.5px;line-height:1.5;margin:6px 0}}.m{{color:{C["mute"]};font-size:9.5px}}.c{{text-align:center}}
.pf{{position:absolute;bottom:9mm;left:15mm;right:15mm;display:flex;justify-content:space-between;font-size:8.5px;color:{C["mute"]};border-top:1px solid {C["line"]};padding-top:5px}}
.two{{display:grid;grid-template-columns:200px 1fr;gap:18px;align-items:center}}.two.eq{{grid-template-columns:1fr 1fr;align-items:start}}.gauge{{text-align:center}}
.t{{width:100%;border-collapse:collapse;font-size:9.8px;margin:4px 0 8px}}.t th{{text-align:left;font-size:8.5px;letter-spacing:1px;text-transform:uppercase;color:{C["mute"]};border-bottom:1.5px solid {C["copper"]};padding:5px 6px}}
.t td{{padding:5px 6px;border-bottom:1px solid {C["line"]};vertical-align:top;word-break:break-word}}.t.sm td{{font-size:9px;padding:4px 6px}}.t.sc td{{border:none;padding:4px 6px;font-size:10px}}.t.sc td.r{{white-space:nowrap;width:30px}}.t.sc td:first-child{{white-space:nowrap}}.r{{text-align:right}}
.t.cmp td:not(:first-child),.t.cmp th:not(:first-child){{text-align:center}}.t.cmp td:first-child{{color:{C["mute"]}}}.t.cmp th{{letter-spacing:0;text-transform:none;font-size:8.5px}}
.best{{color:#3f7d5a}}.you{{color:{C["copper"]};font-weight:800}}.ok-t{{color:#3f7d5a}}.bad-t{{color:#b5432f}}
.bar{{height:8px;background:#e9ddd4;border-radius:5px;overflow:hidden;display:inline-block;vertical-align:middle}}.bar span{{display:block;height:100%;border-radius:5px}}
.hb{{height:9px;background:#efe4dc;border-radius:5px}}.hb span{{display:block;height:100%;background:{C["copper"]};border-radius:5px}}
.cbars{{margin:6px 0 10px}}.cbar{{display:grid;grid-template-columns:150px 1fr 30px;gap:10px;align-items:center;font-size:10px;margin:5px 0}}.cbar b{{text-align:right}}.cl.you{{font-weight:800;color:{C["copper"]}}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}}.card{{background:#fff;border-radius:12px;padding:12px;border:1px solid {C["line"]}}}.card b{{font-size:11px}}.card p{{font-size:9.5px}}
.card .n{{width:22px;height:22px;border-radius:50%;background:{C["copper"]};color:#fff;font-weight:800;font-size:11px;display:flex;align-items:center;justify-content:center;margin-bottom:6px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:6px 0 10px}}.kpis.k3{{grid-template-columns:repeat(3,1fr)}}.kpis div{{background:#fff;border:1px solid {C["line"]};border-radius:10px;padding:10px}}
.kpis b{{display:block;font-size:22px;font-weight:900}}.kpis span{{font-size:9px;color:{C["mute"]}}}.up{{color:#3f7d5a;font-weight:700}}.down{{color:#b5432f;font-weight:700}}
.call{{border-radius:10px;padding:10px 12px;font-size:9.8px;line-height:1.5;margin:8px 0;background:#fff;border-left:4px solid {C["copper"]}}}.call.dark{{background:{C["warm"]};color:{C["cream"]};border-left-color:{C["copper"]}}}.call.red{{background:#fbe9e5;border-left-color:#b5432f}}
.checks{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:4px 0 10px}}.checks div{{font-size:9.5px;padding:7px 9px;border-radius:8px;background:#fff;border:1px solid {C["line"]}}}
.ok::before{{content:"✓ ";color:#3f7d5a;font-weight:900}}.bad::before{{content:"✕ ";color:#b5432f;font-weight:900}}.warn::before{{content:"! ";color:#c9922e;font-weight:900}}
.chips{{display:flex;flex-wrap:wrap;gap:5px;margin:4px 0 10px}}.chips span{{font-size:9px;background:#fff;border:1px solid {C["line"]};border-radius:20px;padding:4px 9px}}
.bigzero{{text-align:center;background:{C["warm"]};color:{C["cream"]};border-radius:14px;padding:18px}}.bigzero b{{font-size:64px;font-weight:900;color:{C["copper"]};display:block;line-height:1}}.bigzero span{{font-size:10px}}
.ar{{font-family:Tajawal,Arial;direction:rtl;unicode-bidi:embed;font-size:11px}}
.endcard{{position:absolute;left:15mm;right:15mm;bottom:22mm;background:linear-gradient(160deg,{C["bg"]},{C["warm"]});border-radius:16px;padding:22px;text-align:center}}.et{{font-size:24px;font-weight:900;color:{C["cream"]};margin:8px 0}}.et span{{color:{C["copper"]}}}'''

if __name__ == "__main__":
    main()
