#!/usr/bin/env python3
"""Collect everything for a Brand Victory SEO report: public checks on the site and its
competitors (no access needed), plus Search Console / Bing data when the site has given access.

  python3 -I collect.py https://site.com --out DIR \
      [--competitor rival1.com --competitor rival2.com | --auto-competitors 3] \
      [--kw "website design lebanon" --kw "تصميم مواقع"] [--country lb] \
      [--max-pages 60] [--no-gsc] [--no-geo] [--no-speed]

Writes DIR/data.json (input for build.py) and DIR/summary.md (read it before writing notes.json).

Public sources (no key): page crawl + sitemap + robots, HTTP headers, Google DNS (email security,
DNS host), RDAP (domain age), crt.sh (SSL), DuckDuckGo results (Bing-powered rankings, competitor
discovery), Google/YouTube/Bing autocomplete (keywords), GEO Optimizer (AI visibility), spam scan.
Keys used when present: PSI_API_KEY (speed), OPR_API_KEY (domain authority for every site),
GSC_SA_JSON_B64 / GSC_CREDENTIALS_PATH (Search Console, own/client sites only),
BING_WMT_API_KEY (backlinks, sites verified in Sam's Bing account only).
"""
import argparse, collections, concurrent.futures as cf, datetime as dt, html as htmlmod, json, math, os, re
import subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, "seo-data-free", "scripts"))
sys.path.insert(0, os.path.join(SKILLS, "geo-optimizer", "scripts"))
import seodata            # noqa: E402  psi(), keyword_ideas(), gsc_token(), gsc_query(), opr()
import site_spam_scan     # noqa: E402  scan()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
ARAB = {"lb", "ae", "sa", "kw", "qa", "bh", "om", "jo", "eg", "iq", "sy", "ps", "ma", "dz", "tn", "ly", "ye", "sd"}
MARKET_TERMS = {
    "lb": ["lebanon", "lebanese", "beirut", "jounieh", "tripoli", "byblos", "لبنان", "بيروت"],
    "ae": ["uae", "dubai", "abu dhabi", "sharjah", "الإمارات", "دبي", "أبوظبي"],
    "sa": ["saudi", "ksa", "riyadh", "jeddah", "السعودية", "الرياض", "جدة"],
    "kw": ["kuwait", "الكويت"], "qa": ["qatar", "doha", "قطر", "الدوحة"], "jo": ["jordan", "amman", "الأردن", "عمان"],
    "eg": ["egypt", "cairo", "مصر", "القاهرة"], "au": ["australia", "sydney", "melbourne", "brisbane"],
    "us": ["usa", "united states", "new york", "california"], "gb": ["uk", "london", "united kingdom"],
}
FAR_PLACES = {"india", "indian", "delhi", "mumbai", "chennai", "bangalore", "kerala", "hyderabad", "pune", "bangladesh", "pakistan",
              "karachi", "lahore", "nigeria", "lagos", "kenya", "philippines", "manila", "chicago", "texas", "florida", "toronto",
              "malaysia", "indonesia", "singapore", "oman", "iraq", "عراقية", "العراق", "مصري", "مدينة نصر", "المغرب", "الجزائر"}
DIRECTORIES = re.compile(
    r"(clutch\.co|designrush|goodfirms|upwork|fiverr|freelancer\.|linkedin|facebook|instagram|youtube|tiktok|"
    r"twitter|(^|\.)x\.com|wikipedia|reddit|quora|medium\.com|yelp|tripadvisor|yellowpages|sortlist|themanifest|"
    r"icreativez|glassdoor|indeed|amazon\.|pinterest|google\.|apple\.com|forbes|hubspot|semrush|ahrefs|wix\.com|"
    r"squarespace\.com|godaddy|shopify\.com|bing\.com|duckduckgo|yahoo\.|behance|dribbble|trustpilot|crunchbase|"
    r"ohhmybrand|topagencies|agencyspotter|expertise\.com|bark\.com|thumbtack|olx|dubizzle|bayt\.com)", re.I)
TECH = [("WordPress", r"wp-content|wp-includes"), ("Elementor", r"elementor"), ("Divi", r"et_pb_|/Divi/"),
        ("WooCommerce", r"woocommerce"), ("Yoast SEO", r"yoast"), ("Rank Math", r"rank-math|rankmath"),
        ("Wix", r"wixstatic|_wixCIDX|wix\.com"), ("Squarespace", r"squarespace"), ("Shopify", r"cdn\.shopify|Shopify\.theme"),
        ("Webflow", r"webflow"), ("Framer", r"framerusercontent|framer\.com/m/"), ("Next.js", r"__NEXT_DATA__|/_next/static"),
        ("Nuxt", r"__NUXT__"), ("Joomla", r"/media/jui/|content=\"Joomla"), ("Drupal", r"drupal-settings|Drupal\.settings"),
        ("GoDaddy builder", r"img1\.wsimg\.com"), ("Hostinger builder", r"zyrosite|zyro\.com"), ("Bootstrap", r"bootstrap(\.min)?\.(css|js)")]
TRACK = [("Google Analytics 4", r"googletagmanager\.com/gtag/js\?id=G-|gtag\(['\"]config['\"],\s*['\"]G-"),
         ("Google Tag Manager", r"GTM-[A-Z0-9]{4,}"), ("Meta Pixel", r"connect\.facebook\.net/[^\"']*fbevents|fbq\("),
         ("TikTok Pixel", r"analytics\.tiktok\.com"), ("LinkedIn Insight", r"snap\.licdn\.com"),
         ("Microsoft Clarity", r"clarity\.ms"), ("Hotjar", r"static\.hotjar\.com"), ("Google Ads", r"['\"]AW-\d{6,}")]
CONVERT = [("WhatsApp", r"wa\.me/|api\.whatsapp\.com|whatsapp://"), ("Phone link", r"href=[\"']tel:"),
           ("Email link", r"href=[\"']mailto:"), ("Booking", r"calendly\.com|cal\.com/|acuityscheduling|tidycal|setmore|simplybook|zcal\.co"),
           ("Live chat", r"tawk\.to|tidio|crisp\.chat|intercom|livechatinc|manychat|drift\.com"), ("Form", r"<form\b"),
           ("Newsletter", r"mailchimp|klaviyo|convertkit|mailerlite|brevo|sendinblue|beehiiv"),
           ("Google Maps link", r"google\.[a-z.]+/maps|maps\.app\.goo\.gl|goo\.gl/maps")]
SOCIAL = [("Instagram", r"instagram\.com/[A-Za-z0-9_.]+"), ("Facebook", r"facebook\.com/[A-Za-z0-9_.\-]+"),
          ("LinkedIn", r"linkedin\.com/(in|company)/[A-Za-z0-9_\-%]+"), ("X", r"(twitter|x)\.com/[A-Za-z0-9_]+"),
          ("YouTube", r"youtube\.com/(@|c/|channel/|user/)[A-Za-z0-9_\-]+"), ("TikTok", r"tiktok\.com/@[A-Za-z0-9_.]+"),
          ("Behance", r"behance\.net/[A-Za-z0-9_]+"), ("Pinterest", r"pinterest\.[a-z.]+/[A-Za-z0-9_]+")]
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Applebot-Extended", "Bytespider"]
SEC_HEADERS = [("strict-transport-security", "HSTS"), ("content-security-policy", "Content-Security-Policy"),
               ("x-frame-options", "X-Frame-Options"), ("x-content-type-options", "X-Content-Type-Options"),
               ("referrer-policy", "Referrer-Policy"), ("permissions-policy", "Permissions-Policy")]
JUNK = re.compile(r"(^|[/\-_])(test|testing|demo|sample|hello-world|copy|old|draft|trashed|lorem|untitled|new-page|"
                  r"temp|tmp|staging|dummy|elementor-\d+|home-?\d|homepage-new|new-website|coming-soon)([/\-_.]|$)|__trashed|-2/?$", re.I)
WEIGHTS = {"visibility": 18, "authority": 15, "speed": 12, "onpage": 12, "technical": 12, "ai": 12, "reach": 11, "security": 8}
LABELS = {"visibility": "Search visibility", "authority": "Authority (backlinks)", "speed": "Page speed (mobile)",
          "onpage": "On-page SEO", "technical": "Technical & indexing", "ai": "AI-search visibility",
          "reach": "Local & language reach", "security": "Security & trust"}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def get(url, timeout=25, tries=1):
    """GET with redirects. Returns dict(status, url, headers, body, ms, error)."""
    for i in range(tries):
        t = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,ar;q=0.8"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read(3_000_000).decode("utf-8", "ignore")
                return {"status": r.status, "url": r.geturl(), "headers": {k.lower(): v for k, v in r.headers.items()},
                        "body": body, "ms": round((time.time() - t) * 1000), "error": None}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "url": url, "headers": {k.lower(): v for k, v in (e.headers or {}).items()},
                    "body": "", "ms": round((time.time() - t) * 1000), "error": f"HTTP {e.code}"}
        except Exception as e:
            err = str(e)[:120]
            if i + 1 < tries:
                time.sleep(3 * (i + 1))
    return {"status": 0, "url": url, "headers": {}, "body": "", "ms": 0, "error": err}


def jget(url, timeout=25):
    r = get(url, timeout)
    return json.loads(r["body"]) if r["status"] == 200 and r["body"] else None


def host(u):
    return urllib.parse.urlparse(u if "//" in u else "https://" + u).netloc.lower().split(":")[0].removeprefix("www.")


# ---------------------------------------------------------------- HTML parsing
class Page(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self.meta = {}; self.h1 = []; self.h2 = []; self.links = []; self.imgs = []
        self.scripts = 0; self.css = 0; self.jsonld = []; self.canonical = ""; self.hreflang = []; self.lang = ""
        self.text = []; self._stack = []; self._cur = None; self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta":
            k = (a.get("name") or a.get("property") or "").lower()
            if k:
                self.meta[k] = a.get("content", "")
        elif tag == "link":
            rel = a.get("rel", "").lower()
            if "canonical" in rel:
                self.canonical = a.get("href", "")
            elif "alternate" in rel and a.get("hreflang"):
                self.hreflang.append(a["hreflang"].lower())
            elif "stylesheet" in rel:
                self.css += 1
        elif tag == "script":
            if a.get("src"):
                self.scripts += 1
            if "ld+json" in a.get("type", ""):
                self._cur, self._buf = "ld", ""
        elif tag == "img":
            self.imgs.append(a.get("alt"))
        elif tag == "a":
            self._cur, self._buf = ("a", a.get("href", "")), ""
        elif tag in ("title", "h1", "h2"):
            self._cur, self._buf = tag, ""
        if tag in self.SKIP:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        c = self._cur
        if c == "ld" and tag == "script":
            self.jsonld.append(self._buf); self._cur = None
        elif isinstance(c, tuple) and tag == "a":
            self.links.append((c[1], " ".join(self._buf.split()))); self._cur = None
        elif c == tag and tag in ("title", "h1", "h2"):
            t = " ".join(self._buf.split())
            if tag == "title":
                self.title = self.title or t
            else:
                getattr(self, tag).append(t)
            self._cur = None

    def handle_data(self, d):
        if self._cur:
            self._buf += d
        if not self._stack:
            self.text.append(d)


def schema_types(blocks):
    out = []

    def walk(x):
        if isinstance(x, dict):
            t = x.get("@type")
            for v in (t if isinstance(t, list) else [t]):
                if isinstance(v, str):
                    out.append(v)
            for v in x.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for b in blocks:
        try:
            walk(json.loads(b))
        except Exception:
            pass
    return out


def page_info(url, body):
    p = Page()
    try:
        p.feed(body)
    except Exception:
        pass
    text = " ".join(" ".join(p.text).split())
    letters = re.findall(r"[A-Za-z؀-ۿ]", text)
    arabic = len(re.findall(r"[؀-ۿ]", text)) / max(1, len(letters))
    h = host(url)
    internal = [l for l, _ in p.links if l.startswith("/") or host(l) == h]
    external = [l for l, _ in p.links if l.startswith("http") and host(l) != h]
    robots = (p.meta.get("robots", "") + " " + p.meta.get("googlebot", "")).lower()
    return {"url": url, "title": p.title, "title_len": len(p.title), "desc": p.meta.get("description", ""),
            "desc_len": len(p.meta.get("description", "")), "h1": p.h1[:4], "h1_count": len(p.h1), "h2_count": len(p.h2),
            "h2": p.h2[:12], "words": len(text.split()), "imgs": len(p.imgs), "imgs_no_alt": sum(1 for a in p.imgs if not (a or "").strip()),
            "internal_links": len(internal), "external_links": len(external), "canonical": p.canonical,
            "noindex": "noindex" in robots, "lang": p.lang, "hreflang": sorted(set(p.hreflang)),
            "schema": schema_types(p.jsonld), "og": bool(p.meta.get("og:title")), "viewport": "viewport" in p.meta,
            "generator": p.meta.get("generator", ""), "scripts": p.scripts, "css": p.css, "arabic": round(arabic, 2),
            "links": [l for l, _ in p.links][:400]}


# ---------------------------------------------------------------- site profile
def robots_info(base):
    r = get(base + "/robots.txt")
    txt = r["body"] if r["status"] == 200 and "<html" not in r["body"][:300].lower() else ""
    groups, cur, last_ua = collections.defaultdict(list), [], False
    for line in txt.splitlines():
        line = line.split("#")[0].strip()
        if ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        k = k.lower()
        if k == "user-agent":
            cur = cur if last_ua else []
            cur.append(v.lower()); last_ua = True
        else:
            last_ua = False
            for ua in cur:
                groups[ua].append((k, v))

    def blocked(ua):
        rules = groups.get(ua.lower()) or groups.get("*") or []
        return any(k == "disallow" and v == "/" for k, v in rules)
    return {"exists": bool(txt), "sitemaps": re.findall(r"(?im)^\s*sitemap:\s*(\S+)", txt),
            "ai_blocked": [b for b in AI_BOTS if blocked(b)], "blocks_all": blocked("*")}


def sitemap_urls(base, declared, cap=3000):
    queue = list(declared) or [base + "/sitemap.xml", base + "/sitemap_index.xml", base + "/wp-sitemap.xml"]
    seen, urls, files, tries = set(), {}, [], 0
    while queue and tries < 25 and len(urls) < cap:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm); tries += 1
        r = get(sm, 30)
        if r["status"] != 200 or "<" not in r["body"][:200]:
            continue
        files.append(sm)
        body = r["body"]
        if "<sitemapindex" in body:
            queue += [htmlmod.unescape(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)]
            continue
        for blk in re.findall(r"<url>(.*?)</url>", body, re.S):
            m = re.search(r"<loc>\s*([^<\s]+)\s*</loc>", blk)
            if m:
                lm = re.search(r"<lastmod>\s*([^<\s]+)", blk)
                kind = "post" if re.search(r"post-sitemap|posts?[-_]|/blog", sm + m.group(1), re.I) else "page"
                urls[htmlmod.unescape(m.group(1))] = {"lastmod": lm.group(1)[:10] if lm else "", "kind": kind}
        if not declared and urls:
            break
    return urls, files


def dns(name, typ):
    d = jget(f"https://dns.google/resolve?name={urllib.parse.quote(name)}&type={typ}", 15) or {}
    return [a.get("data", "") for a in d.get("Answer", []) if a.get("type") in (1, 2, 5, 15, 16)]


def domain_facts(dom):
    out = {}
    rd = jget(f"https://rdap.org/domain/{dom}", 25)
    if rd:
        ev = {e.get("eventAction"): e.get("eventDate", "")[:10] for e in rd.get("events", [])}
        out["registered"] = ev.get("registration", ""); out["expires"] = ev.get("expiration", "")
        for ent in rd.get("entities", []):
            if "registrar" in ent.get("roles", []):
                v = ent.get("vcardArray", [None, []])[1]
                out["registrar"] = next((x[3] for x in v if x[0] == "fn"), "")
        if out.get("registered"):
            out["age_years"] = round((dt.date.today() - dt.date.fromisoformat(out["registered"])).days / 365.25, 1)
    mx = " ".join(dns(dom, "MX")).lower()
    out["email_host"] = ("Google Workspace" if "google" in mx else "Microsoft 365" if "outlook" in mx or "microsoft" in mx
                         else "Zoho" if "zoho" in mx else ("other" if mx else "none"))
    txt = dns(dom, "TXT")
    out["spf"] = any("v=spf1" in t for t in txt)
    dm = [t for t in dns("_dmarc." + dom, "TXT") if "v=DMARC1" in t]
    out["dmarc"] = (re.search(r"p=(\w+)", dm[0]).group(1) if dm and re.search(r"p=(\w+)", dm[0]) else "none") if dm else ""
    ns = " ".join(dns(dom, "NS")).lower()
    out["dns_host"] = next((n for k, n in [("cloudflare", "Cloudflare"), ("hostinger", "Hostinger"), ("dns-parking", "Hostinger"),
                                             ("godaddy", "GoDaddy"), ("domaincontrol", "GoDaddy"), ("awsdns", "AWS"), ("google", "Google"),
                                             ("namecheap", "Namecheap"), ("registrar-servers", "Namecheap"), ("wix", "Wix"),
                                             ("siteground", "SiteGround"), ("bluehost", "Bluehost")] if k in ns), ns.split(" ")[0].rstrip(".") if ns else "")
    try:
        r = get(f"https://crt.sh/?q={dom}&output=json", 30)
        certs = json.loads(r["body"]) if r["status"] == 200 else []
        na = max((c["not_after"][:10] for c in certs if dom in c.get("name_value", "")), default="")
        if na:
            out["ssl_expires"] = na; out["ssl_days_left"] = (dt.date.fromisoformat(na) - dt.date.today()).days
            out["ssl_issuer"] = re.sub(r".*O=([^,]+).*", r"\1", next(c["issuer_name"] for c in certs if c["not_after"][:10] == na))
    except Exception:
        pass
    return out


def run_geo(url):
    try:
        p = subprocess.run(["uvx", "--from", "geo-optimizer-skill", "geo", "audit", "--url", url, "--format", "json"],
                           capture_output=True, text=True, timeout=300)
        g = json.loads(p.stdout[p.stdout.index("{"):])
        if g.get("error") or (g.get("http_status") or 200) >= 400:
            log(f"  geo: {url} answered HTTP {g.get('http_status')} (firewall/bot block); AI visibility not measured")
            return None
        return {"score": g.get("score"), "band": g.get("band"), "breakdown": g.get("score_breakdown", {}),
                "max": g.get("score_max", {}), "platforms": {x["platform"]: x["score"] for x in g.get("platform_citation", {}).get("platforms", [])},
                "platform_recs": {x["platform"]: x.get("recommendations", []) for x in g.get("platform_citation", {}).get("platforms", [])},
                "recommendations": g.get("recommendations", [])[:12]}
    except Exception as e:
        log("  geo failed for", url, e)
        return None


def run_speed(url):
    out = {}
    for strat in ("mobile", "desktop"):
        for attempt in range(2):
            try:
                row, scores, opps = seodata.psi(url, strat)
                out[strat] = {"scores": scores, "LCP": row["LCP"], "CLS": row["CLS"], "TBT": row["TBT"], "FCP": row["FCP"],
                              "field_LCP": row["field_LCP"], "field_INP": row["field_INP"], "field_CLS": row["field_CLS"],
                              "opps": [[round(ms), t] for ms, t in opps]}
                break
            except Exception as e:
                log(f"  speed {strat} failed for {url}: {str(e)[:100]}")
                time.sleep(5)
    return out or None


def crawl(urls, n):
    def one(u):
        r = get(u, 25)
        info = page_info(r["url"], r["body"]) if r["status"] == 200 else {"url": u}
        info.update({"requested": u, "status": r["status"], "redirected": r["url"].rstrip("/") != u.rstrip("/"), "ms": r["ms"]})
        info.pop("links", None)
        return info
    with cf.ThreadPoolExecutor(6) as ex:
        return list(ex.map(one, urls[:n]))


def profile(site, max_pages):
    dom = host(site)
    base = "https://" + dom
    log(f"· profiling {dom}")
    home = get(base + "/", 30, tries=2)
    if home["status"] == 0:
        home = get("https://www." + dom + "/", 30, tries=2)
    final = home["url"]
    fbase = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(final))
    hp = page_info(final, home["body"]) if home["body"] else {}
    body, hdr = home["body"], home["headers"]
    variants = {}
    for v in (f"http://{dom}/", f"http://www.{dom}/", f"https://www.{dom}/", f"https://{dom}/"):
        r = get(v, 20)
        variants[v] = r["url"] if r["status"] else "error"
    finals = {host(x) + ("" if x.startswith("https") else ":http") for x in variants.values() if x != "error"}
    rb = robots_info(fbase)
    sm, sm_files = sitemap_urls(fbase, rb["sitemaps"])
    pages = [u for u, m in sm.items() if m["kind"] == "page"]
    posts = sorted((u for u, m in sm.items() if m["kind"] == "post"), key=lambda u: sm[u]["lastmod"], reverse=True)
    order = [final] + [u for u in pages if u.rstrip("/") != final.rstrip("/")] + posts
    pdfs = sorted({u for u in list(sm) + [urllib.parse.urljoin(final, l) for l in hp.get("links", [])]
                   if re.search(r"\.(pdf|docx?|xlsx?|pptx?)(\?|$)", u, re.I) and host(u) == dom})
    crawled = crawl(order, max_pages)
    llms = get(fbase + "/llms.txt", 15)
    text_all = body + " ".join(hp.get("links", []))
    tech = [n for n, rx in TECH if re.search(rx, body, re.I)]
    server = hdr.get("server", "")
    if "cf-ray" in hdr:
        tech.append("Cloudflare")
    if server:
        sname = server.split("/")[0]
        tech.append({"litespeed": "LiteSpeed", "cloudflare": "Cloudflare", "nginx": "nginx", "apache": "Apache"}.get(sname.lower(), sname))
    gen = hp.get("generator", "").split(";")[0].strip()
    p = {
        "domain": dom, "url": final, "status": home["status"], "ms": home["ms"], "error": home["error"],
        "https_redirect": variants.get(f"http://{dom}/", "").startswith("https"),
        "one_host": len(finals) == 1, "variants": variants,
        "server": server, "powered_by": hdr.get("x-powered-by", ""),
        "version_leak": bool(re.search(r"\d", server + hdr.get("x-powered-by", ""))) or bool(re.search(r"\d", gen)),
        "generator": gen,
        "security_headers": {label: (k in hdr) for k, label in SEC_HEADERS},
        "tech": sorted(set(tech)), "tracking": [n for n, rx in TRACK if re.search(rx, body)],
        "conversion": [n for n, rx in CONVERT if re.search(rx, text_all, re.I)],
        "social": sorted({n for n, rx in SOCIAL if re.search(rx, text_all, re.I)}),
        "home": {k: v for k, v in hp.items() if k != "links"}, "robots": rb,
        "sitemap": {"files": sm_files, "urls": len(sm), "pages": len(pages), "posts": len(posts),
                    "latest_post": sm[posts[0]]["lastmod"] if posts else "",
                    "latest_update": max((m["lastmod"] for m in sm.values()), default="")},
        "llms_txt": llms["status"] == 200 and "<html" not in llms["body"][:300].lower() and len(llms["body"]) > 50,
        "public_docs": pdfs[:15], "crawl": crawled,
    }
    try:
        _, _, n_ext, top, findings = site_spam_scan.scan(final)
        p["spam"] = findings
    except Exception as e:
        p["spam"] = None; log("  spam scan failed", e)
    p["facts"] = domain_facts(dom)
    return p


# ---------------------------------------------------------------- rankings (DuckDuckGo, Bing-powered)
def ddg_region(country, arabic):
    if country in ARAB:
        return "xa-ar" if arabic else "xa-en"
    return {"au": "au-en", "us": "us-en", "gb": "uk-en", "ca": "ca-en", "fr": "fr-fr", "de": "de-de"}.get(country, "wt-wt")


def serp(q, country):
    reg = ddg_region(country, bool(re.search(r"[؀-ۿ]", q)))
    for attempt in range(5):
        r = get("https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": q, "kl": reg}), 25, tries=2)
        links = re.findall(r'class="result__a"[^>]*href="([^"]+)"', r["body"])
        if links:
            out = []
            for l in links:
                m = re.search(r"uddg=([^&]+)", l)
                u = urllib.parse.unquote(m.group(1)) if m else l
                if "duckduckgo.com/y.js" not in u:
                    out.append(u)
            return out[:10]
        time.sleep(4 * (attempt + 1))
    return None


# ---------------------------------------------------------------- Search Console / Bing (access needed)
def gsc_data(dom):
    if not (os.environ.get("GSC_SA_JSON") or os.environ.get("GSC_SA_JSON_B64") or os.environ.get("GSC_CREDENTIALS_PATH")
            or os.path.exists(os.path.expanduser("~/.config/gsc/service_account.json"))):
        return {"available": False, "reason": "no Search Console credential in this session"}
    try:
        tok = seodata.gsc_token()
        sites = seodata.jget("https://www.googleapis.com/webmasters/v3/sites", headers={"Authorization": f"Bearer {tok}"}).get("siteEntry", [])
    except Exception as e:
        return {"available": False, "reason": f"Search Console login failed ({str(e)[:80]})"}
    names = [s["siteUrl"] for s in sites]
    prop = next((n for n in (f"sc-domain:{dom}", f"https://{dom}/", f"https://www.{dom}/", f"http://{dom}/", f"http://www.{dom}/") if n in names), None)
    if not prop:
        return {"available": False, "reason": "the site hasn't added the service account in Search Console"}
    end = dt.date.today() - dt.timedelta(days=2)
    d = lambda n: str(end - dt.timedelta(days=n))
    q = lambda dims, s, e=str(end), lim=25: seodata.gsc_query(tok, prop, s, e, dims, limit=lim)
    tot = lambda s, e=str(end): (q([], s, e) or [{"clicks": 0, "impressions": 0, "ctr": 0, "position": 0}])[0]
    out = {"available": True, "property": prop, "end": str(end),
           "t28": tot(d(27)), "tp28": tot(d(55), d(28)), "t90": tot(d(89)),
           "queries90": q(["query"], d(89), lim=40), "pages90": q(["page"], d(89), lim=15),
           "countries90": q(["country"], d(89), lim=12), "devices90": q(["device"], d(89), lim=5),
           "monthly": q(["date"], d(480), lim=600)}
    return out


def bing_links(dom):
    key = os.environ.get("BING_WMT_API_KEY")
    if not key:
        return {"available": False, "reason": "BING_WMT_API_KEY not set in this session"}
    base = "https://ssl.bing.com/webmaster/api.svc/json"
    for site in (f"https://{dom}/", f"https://www.{dom}/", f"http://{dom}/"):
        try:
            c = seodata.jget(f"{base}/GetLinkCounts?" + urllib.parse.urlencode({"siteUrl": site, "page": 0, "apikey": key}))
        except Exception:
            continue
        pages = [(x["Url"], x["Count"]) for x in c.get("d", {}).get("Links", [])]
        refs = set()
        for url, _ in sorted(pages, key=lambda x: -x[1])[:10]:
            try:
                det = seodata.jget(f"{base}/GetUrlLinks?" + urllib.parse.urlencode({"siteUrl": site, "link": url, "page": 0, "apikey": key}))
                refs |= {host(l.get("Url", "")) for l in det.get("d", {}).get("Details", [])}
            except Exception:
                pass
        return {"available": True, "links": sum(n for _, n in pages), "linked_pages": len(pages), "ref_domains": len(refs - {dom}),
                "top_ref_domains": sorted(refs - {dom})[:15]}
    return {"available": False, "reason": "site not verified in Sam's Bing Webmaster account"}


# ---------------------------------------------------------------- scoring
def clamp(x):
    return max(0, min(100, round(x)))


def onpage_stats(p):
    pages = [c for c in p["crawl"] if c.get("status") == 200 and "title" in c]
    n = max(1, len(pages))
    titles = collections.Counter(c["title"].strip().lower() for c in pages if c["title"])
    imgs = sum(c["imgs"] for c in pages)
    s = {"pages": len(pages), "no_desc": sum(1 for c in pages if not c["desc"]),
         "multi_h1": sum(1 for c in pages if c["h1_count"] > 1), "no_h1": sum(1 for c in pages if c["h1_count"] == 0),
         "thin": sum(1 for c in pages if c["words"] < 300), "title_bad": sum(1 for c in pages if not c["title"] or c["title_len"] > 65 or c["title_len"] < 15),
         "dup_titles": sum(v for v in titles.values() if v > 1), "imgs": imgs, "imgs_no_alt": sum(c["imgs_no_alt"] for c in pages),
         "avg_words": round(sum(c["words"] for c in pages) / n), "no_canonical": sum(1 for c in pages if not c["canonical"]),
         "noindex": sum(1 for c in pages if c["noindex"]), "arabic_pages": sum(1 for c in pages if c["arabic"] >= 0.3),
         "errors": sum(1 for c in p["crawl"] if c.get("status", 0) >= 400 or c.get("status") == 0),
         "redirected": sum(1 for c in p["crawl"] if c.get("redirected")),
         "junk": [c["requested"] for c in p["crawl"] if JUNK.search(urllib.parse.urlparse(c["requested"]).path)],
         "empty": [c["requested"] for c in pages[1:] if c["words"] < 60],
         "schema_types": sorted({t for c in pages for t in c.get("schema", [])})}
    return s


def score_site(p, speed, geo, opr, country, gsc=None, bing=None):
    s = onpage_stats(p)
    n = max(1, s["pages"])
    sc = {}
    if speed and speed.get("mobile"):
        sc["speed"] = speed["mobile"]["scores"].get("performance")
    if geo and geo.get("score") is not None:
        sc["ai"] = geo["score"]
    if s["pages"]:
        sc["onpage"] = clamp(100 - 25 * s["no_desc"] / n - 15 * s["multi_h1"] / n - 25 * s["thin"] / n
                             - 15 * (s["imgs_no_alt"] / max(1, s["imgs"])) - 20 * max(s["title_bad"], s["dup_titles"]) / n)
    t = 100 - (0 if p["https_redirect"] else 20) - (0 if p["one_host"] else 10) - (0 if p["robots"]["exists"] else 10)
    t -= 0 if p["sitemap"]["urls"] else 15
    crawled = max(1, len(p["crawl"]))
    t -= 30 * s["errors"] / crawled + 100 * len(set(s["junk"]) | set(s["empty"])) / crawled + 10 * s["no_canonical"] / n + 20 * s["noindex"] / n
    t -= 10 if p["public_docs"] else 0
    sc["technical"] = clamp(t)
    sh = p["security_headers"]
    sec = 100 - 8 * sum(1 for k in ("HSTS", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy") if not sh[k])
    sec -= (0 if sh["Content-Security-Policy"] else 8) + (8 if p["version_leak"] else 0)
    f = p.get("facts", {})
    sec -= (0 if f.get("dmarc") else 10) + (0 if f.get("spf") else 5)
    sc["security"] = 0 if p.get("spam") else clamp(sec)
    terms = MARKET_TERMS.get(country, [])
    blob = " ".join((c.get("title", "") + " " + " ".join(c.get("h1", []))) for c in p["crawl"]).lower()
    arabic = s["arabic_pages"] > 0 or any(h.startswith("ar") for h in p["home"].get("hreflang", []))
    local_schema = any(t in s["schema_types"] for t in ("LocalBusiness", "ProfessionalService", "PostalAddress", "Place")) or \
        any(t.endswith("Business") or t.endswith("Store") for t in s["schema_types"])
    contact = any(x in p["conversion"] for x in ("WhatsApp", "Phone link"))
    reach = (35 if (arabic or country not in ARAB) else 0) + (15 if local_schema else 0) + (15 if contact else 0)
    reach += (10 if "Google Maps link" in p["conversion"] else 0) + (15 if any(t in blob for t in terms) else 0) + (10 if p["home"].get("lang") else 0)
    sc["reach"] = clamp(reach)
    if opr.get(p["domain"]) not in (None, ""):
        sc["authority"] = clamp(float(opr[p["domain"]]) * 10)
    elif bing and bing.get("available"):
        sc["authority"] = clamp(25 * math.log10(1 + bing["ref_domains"]) * 2)
    if gsc and gsc.get("available"):
        c28, i28 = gsc["t28"].get("clicks", 0), gsc["t28"].get("impressions", 0)
        sc["visibility"] = clamp(30 * math.log10(1 + c28 / 2) + 8 * math.log10(1 + i28 / 50))
    def wavg(keys):
        ks = [k for k in keys if sc.get(k) is not None]
        return round(sum(sc[k] * WEIGHTS[k] for k in ks) / sum(WEIGHTS[k] for k in ks)) if ks else None
    sc["overall"] = wavg(WEIGHTS)
    sc["public"] = wavg([k for k in WEIGHTS if k not in ("visibility",) and not (k == "authority" and not opr)])
    return sc, s, {"arabic": arabic, "local_schema": local_schema, "contact": contact}


def findings(t):
    """Auto-detected issues for the target, most severe first: (severity 1-3, area, issue, fix)."""
    p, s, sc, sp, geo = t["profile"], t["onpage"], t["scores"], t.get("speed") or {}, t.get("geo") or {}
    F = []
    add = lambda sev, area, issue, fix: F.append({"sev": sev, "area": area, "issue": issue, "fix": fix})
    if p.get("spam"):
        add(3, "security", "Hacked-site spam found on the homepage: " + "; ".join(p["spam"][:2]), "Treat as a security incident: clean, update, rotate passwords, request review")
    if p["public_docs"]:
        add(3, "technical", f"{len(p['public_docs'])} document file(s) publicly reachable (e.g. {p['public_docs'][0].split('/')[-1]})", "Check each for confidential content; delete + remove from Google")
    m = sp.get("mobile")
    if m and m["scores"].get("performance", 100) < 50:
        add(3, "speed", f"Mobile speed {m['scores']['performance']}/100, main content at {m['LCP']}", "Caching, defer/remove unused JS/CSS, compress images (WebP), fewer plugins")
    elif m and m["scores"].get("performance", 100) < 75:
        add(2, "speed", f"Mobile speed {m['scores']['performance']}/100", "Defer JS, compress images, enable caching")
    if s["junk"]:
        add(2, "technical", f"{len(s['junk'])} test/duplicate/old pages in the sitemap", "Delete, 301-redirect or noindex; remove from sitemap")
    if s["empty"]:
        add(2, "technical", f"{len(s['empty'])} near-empty pages (under 60 words) are public, e.g. " + ", ".join(urllib.parse.urlparse(u).path for u in s["empty"][:4]),
            "Delete, merge or noindex; keep internal tools out of the sitemap")
    if s["errors"]:
        add(2, "technical", f"{s['errors']} broken pages (4xx/5xx) in the sitemap", "Fix or remove from sitemap")
    if not p["https_redirect"]:
        add(3, "technical", "http:// doesn't redirect to https://", "Force HTTPS with a 301")
    if not p["one_host"]:
        add(2, "technical", "www and non-www versions don't resolve to one address", "301 one to the other; set canonical host")
    if s["pages"] and s["no_desc"] / s["pages"] > 0.2:
        add(2, "onpage", f"{s['no_desc']} of {s['pages']} pages have no meta description", "Write a unique 140-155 character description per page")
    if s["multi_h1"]:
        add(1, "onpage", f"{s['multi_h1']} pages have more than one H1", "One H1 per page")
    if s["pages"] and s["thin"] / s["pages"] > 0.25:
        add(2, "onpage", f"{s['thin']} of {s['pages']} pages are under 300 words", "Expand service pages to 800+ words or noindex thin ones")
    if s["imgs"] and s["imgs_no_alt"] / s["imgs"] > 0.3:
        add(1, "onpage", f"{s['imgs_no_alt']} of {s['imgs']} images have no alt text", "Add descriptive alt text")
    if geo.get("score") is not None and geo["score"] < 70:
        add(2, "ai", f"AI visibility {geo['score']}/100", "Schema (Organization/Person + FAQ), llms.txt, clear answer-style content")
    if not p["llms_txt"]:
        add(1, "ai", "No /llms.txt", "Publish llms.txt summarising services and key pages")
    hs = set(s["schema_types"])
    if not hs:
        add(2, "ai", "No structured data (schema) found", "Add Organization/LocalBusiness + WebSite + FAQ schema")
    elif not ({"Organization", "LocalBusiness", "ProfessionalService", "Person"} & hs):
        add(2, "ai", "No Organization/LocalBusiness/Person schema", "Add entity schema with logo, address, phone, sameAs")
    if p["robots"]["ai_blocked"]:
        add(2, "ai", "robots.txt blocks AI crawlers: " + ", ".join(p["robots"]["ai_blocked"]), "Allow GPTBot/PerplexityBot/ClaudeBot unless intentional")
    if t.get("country") in ARAB and not t["reach"]["arabic"]:
        add(2, "reach", "No Arabic pages", "Arabic versions of home + key service pages with hreflang")
    if not t["reach"]["local_schema"]:
        add(1, "reach", "No LocalBusiness / address schema", "Add LocalBusiness schema with address, phone, opening hours")
    if sc.get("authority") is not None and sc["authority"] < 30:
        add(3, "authority", "Very low authority (few or no sites link here)", "Profiles, directories, client credits, guest articles, PR")
    missing = [k for k, v in p["security_headers"].items() if not v and k != "Permissions-Policy"]
    if missing:
        add(1, "security", "Missing security headers: " + ", ".join(missing), "Add via host/caching plugin or .htaccess")
    if p["version_leak"]:
        add(1, "security", "Server/CMS version is publicly visible", "Hide version headers and generator tag")
    f = p.get("facts", {})
    if not f.get("dmarc"):
        add(1, "security", "No DMARC record (email can be spoofed)", "Add a DMARC TXT record (start with p=none)")
    if f.get("ssl_days_left") is not None and f["ssl_days_left"] < 14:
        add(3, "security", f"SSL certificate expires in {f['ssl_days_left']} days", "Renew / check auto-renewal")
    if "Google Analytics 4" not in p["tracking"] and "Google Tag Manager" not in p["tracking"]:
        add(2, "tracking", "No Google Analytics 4 / Tag Manager detected", "Install GA4 (via GTM) and link Search Console")
    if "Meta Pixel" not in p["tracking"]:
        add(1, "tracking", "No Meta Pixel (can't retarget visitors on Instagram/Facebook)", "Install Meta Pixel + Conversions API")
    if not any(x in p["conversion"] for x in ("WhatsApp", "Booking", "Form")):
        add(2, "tracking", "No WhatsApp, booking or form found on the homepage", "Add a clear WhatsApp/booking call to action")
    if p["sitemap"]["latest_post"] and p["sitemap"]["latest_post"] < str(dt.date.today() - dt.timedelta(days=180)):
        add(1, "onpage", f"Blog last updated {p['sitemap']['latest_post']}", "Publish 2 articles a month on service topics")
    F.sort(key=lambda x: -x["sev"])
    return F


def relevant(seed, rows, country):
    """Drop autocomplete ideas that only share a place name with the seed (e.g. 'capital of lebanon')."""
    places = {w for terms in MARKET_TERMS.values() for t in terms for w in t.split()}
    core = [w[:4] for w in re.findall(r"[a-z\u0600-\u06FF]{3,}", seed.lower()) if w not in places and w not in ("near", "best", "the")]
    if not core:
        return rows
    keep = set(MARKET_TERMS.get(country, [])) | ({w for c in ("ae", "sa", "kw", "qa") for w in MARKET_TERMS[c]} if country in ARAB else set())
    far = {t for c, terms in MARKET_TERMS.items() for t in terms if t not in keep} | FAR_PLACES
    far -= keep
    return [r for r in rows if any(c in r["keyword"] for c in core) and not any(re.search(r"(^|\s)" + re.escape(f) + r"(\s|$)", r["keyword"]) for f in far)]


def content_gap(target, comps):
    stop = set(("the a an and or of for to in on with your you our we is are at by from how what why best top new home page about contact blog "
                "services service us thank thanks submission privacy policy cookie cookies terms conditions cart checkout login account "
                "read more learn get free call now that this these those will can all its it's".split()))
    def grams(p):
        g = set()
        for c in p["crawl"]:
            for t in [re.split(r"\s[|\-–—]\s", c.get("title", ""))[0]] + c.get("h1", []):
                w = [x for x in re.findall(r"[a-z؀-ۿ]{3,}", t.lower()) if x not in stop]
                g |= {" ".join(w[i:i + 2]) for i in range(len(w) - 1)}
        return g
    mine = grams(target)
    mine_words = " ".join(mine)
    cnt = collections.Counter()
    for c in comps:
        for g in grams(c):
            if g not in mine and not all(w in mine_words for w in g.split()):
                cnt[g] += 1
    brand = {w for c in comps + [target] for w in re.findall(r"[a-z]{3,}", c["domain"].split(".")[0])}
    ranked = [(g, n) for g, n in cnt.most_common(200) if not any(w in brand for w in g.split())]
    shared = [g for g, n in ranked if n >= 2]
    return (shared if len(shared) >= 6 else [g for g, _ in ranked])[:20]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site"); ap.add_argument("--out", required=True)
    ap.add_argument("--competitor", action="append", default=[]); ap.add_argument("--auto-competitors", type=int, default=3)
    ap.add_argument("--kw", action="append", default=[]); ap.add_argument("--country", default="lb")
    ap.add_argument("--max-pages", type=int, default=60); ap.add_argument("--comp-pages", type=int, default=15)
    ap.add_argument("--no-gsc", action="store_true"); ap.add_argument("--no-geo", action="store_true"); ap.add_argument("--no-speed", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dom = host(a.site)
    t0 = time.time()
    data = {"site": dom, "date": str(dt.date.today()), "country": a.country, "keywords": a.kw}

    # rankings (+ competitor discovery when none were given: then rankings must run first)
    def do_ranks():
        out = []
        for q in a.kw:
            res = serp(q, a.country)
            out.append({"keyword": q, "results": res})
            log(f"· results for '{q}': {'not available' if res is None else len(res)}")
            time.sleep(2.5)
        for r in out:                      # DuckDuckGo often drops the first request of a run: one more pass
            if r["results"] is None:
                time.sleep(5)
                r["results"] = serp(r["keyword"], a.country)
                log(f"· retry '{r['keyword']}': {'not available' if r['results'] is None else len(r['results'])}")
        return out
    comps = [host(c) for c in a.competitor]
    data["competitors_auto"] = False
    ranks = None
    if not comps and a.auto_competitors and a.kw:
        ranks = do_ranks()
        score = collections.Counter()
        for r in ranks:
            for i, u in enumerate(r["results"] or []):
                h = host(u)
                if h != dom and not DIRECTORIES.search(h) and not h.endswith((".gov", ".edu", ".gov.lb", ".edu.lb")):
                    score[h] += 11 - i
        comps = [h for h, _ in score.most_common(a.auto_competitors)]
        data["competitors_auto"] = True
    data["competitors"] = comps
    log("· competitors:", ", ".join(comps) or "none")
    sites = [dom] + comps

    with cf.ThreadPoolExecutor(10) as ex:
        fut_prof = {s: ex.submit(profile, s, a.max_pages if s == dom else a.comp_pages) for s in sites}
        fut_speed = {s: ex.submit(run_speed, "https://" + s) for s in sites} if not a.no_speed else {}
        fut_geo = {s: ex.submit(run_geo, "https://" + s) for s in sites} if not a.no_geo else {}
        fut_kw = {q: ex.submit(seodata.keyword_ideas, q, "ar" if re.search(r"[؀-ۿ]", q) else "en", a.country) for q in a.kw}
        fut_gsc = ex.submit(gsc_data, dom) if not a.no_gsc else None
        fut_bing = ex.submit(bing_links, dom)
        fut_ranks = ex.submit(do_ranks) if ranks is None else None
        profs = {s: f.result() for s, f in fut_prof.items()}
        speeds = {s: f.result() for s, f in fut_speed.items()}
        geos = {s: f.result() for s, f in fut_geo.items()}
        kws = {q: relevant(q, f.result(), a.country)[:40] for q, f in fut_kw.items()}
        gsc = fut_gsc.result() if fut_gsc else {"available": False, "reason": "skipped (--no-gsc)"}
        bing = fut_bing.result()
        if fut_ranks:
            ranks = fut_ranks.result()
    opr = seodata.opr(sites) if os.environ.get("OPR_API_KEY") else {}

    out_sites = {}
    for s in sites:
        p = profs[s]
        sc, st, reach = score_site(p, speeds.get(s), geos.get(s), opr, a.country, gsc if s == dom else None, bing if s == dom else None)
        out_sites[s] = {"profile": p, "speed": speeds.get(s), "geo": geos.get(s), "scores": sc, "onpage": st, "reach": reach,
                        "opr": opr.get(s), "country": a.country}
    for r in ranks:
        r["positions"] = {s: next((i + 1 for i, u in enumerate(r["results"] or []) if host(u) == s), None) for s in sites}
    tgt = out_sites[dom]
    tgt["findings"] = findings(tgt)
    data.update({"sites": out_sites, "ranks": ranks, "keyword_ideas": kws, "gsc": gsc, "bing": bing,
                 "content_gap": content_gap(tgt["profile"], [out_sites[c]["profile"] for c in comps]) if comps else [],
                 "keys": {"psi": bool(os.environ.get("PSI_API_KEY")), "opr": bool(opr)}, "seconds": round(time.time() - t0)})
    json.dump(data, open(os.path.join(a.out, "data.json"), "w"), ensure_ascii=False, indent=1, default=str)
    open(os.path.join(a.out, "summary.md"), "w").write(summary(data))
    log(f"done in {data['seconds']}s -> {a.out}/data.json, summary.md")


def summary(d):
    L = [f"# {d['site']} · {d['date']} · market {d['country']}", ""]
    t = d["sites"][d["site"]]
    sc = t["scores"]
    L.append("## Scores (0-100)")
    L.append(" | ".join(f"{LABELS.get(k, k)} {v}" for k, v in sc.items() if v is not None))
    g = d["gsc"]
    L.append("\n## Search Console: " + ("yes " + g["property"] if g.get("available") else "NO (" + g.get("reason", "") + ")"))
    if g.get("available"):
        L.append(f"28d clicks {g['t28'].get('clicks')} (prev {g['tp28'].get('clicks')}), impressions {g['t28'].get('impressions')} (prev {g['tp28'].get('impressions')}); "
                 f"90d clicks {g['t90'].get('clicks')} impr {g['t90'].get('impressions')} avg pos {round(g['t90'].get('position', 0), 1)}")
        L.append("top countries 90d: " + ", ".join(f"{r['keys'][0]} {r['impressions']}" for r in g["countries90"][:6]))
        L.append("top queries 90d: " + "; ".join(f"{r['keys'][0]} ({r['impressions']} impr, pos {r['position']:.0f})" for r in sorted(g["queries90"], key=lambda r: -r["impressions"])[:12]))
    b = d["bing"]
    L.append("Bing backlinks: " + (f"{b['links']} links from {b['ref_domains']} domains" if b.get("available") else "NO (" + b.get("reason", "") + ")"))
    p, s = t["profile"], t["onpage"]
    sp = t.get("speed") or {}
    L.append("\n## Target")
    for k in ("mobile", "desktop"):
        if sp.get(k):
            x = sp[k]; L.append(f"{k}: perf {x['scores'].get('performance')} LCP {x['LCP']} TBT {x['TBT']} field LCP {x['field_LCP']}; fixes: " + "; ".join(o[1] for o in x["opps"][:3]))
    geo = t.get("geo") or {}
    L.append(f"GEO {geo.get('score')} platforms {geo.get('platforms')}; recs: " + " | ".join(r[:90] for r in geo.get("recommendations", [])[:5]))
    L.append(f"crawl {s['pages']} pages: no desc {s['no_desc']}, multi H1 {s['multi_h1']}, thin {s['thin']}, bad titles {s['title_bad']}, dup titles {s['dup_titles']}, "
             f"imgs no alt {s['imgs_no_alt']}/{s['imgs']}, avg words {s['avg_words']}, arabic pages {s['arabic_pages']}, errors {s['errors']}, junk {len(s['junk'])}")
    L.append("schema: " + ", ".join(s["schema_types"]) + f" | llms.txt {p['llms_txt']} | robots AI blocked {p['robots']['ai_blocked']}")
    L.append(f"sitemap {p['sitemap']} | public docs {p['public_docs'][:5]}")
    L.append(f"tech {p['tech']} | tracking {p['tracking']} | conversion {p['conversion']} | social {p['social']}")
    L.append(f"security headers {p['security_headers']} | version leak {p['version_leak']} ({p['server']} {p['powered_by']} {p['generator']}) | spam {p['spam']}")
    L.append(f"facts {p['facts']}")
    L.append("home: title '" + p["home"].get("title", "") + "' | desc '" + p["home"].get("desc", "")[:160] + "' | H1 " + str(p["home"].get("h1")))
    L.append("junk urls: " + ", ".join(s["junk"][:12]))
    L.append("key pages: " + "; ".join(f"{urllib.parse.urlparse(c['requested']).path} [{c.get('words', 0)}w, '{c.get('title', '')[:60]}']" for c in p["crawl"][:14]))
    if d["competitors"]:
        L.append("\n## Competitors" + (" (auto-picked from search results: CHECK they are real competitors)" if d["competitors_auto"] else ""))
        for c in d["competitors"]:
            x = d["sites"][c]; cs = x["scores"]; cp = x["profile"]; co = x["onpage"]
            ms = (x.get("speed") or {}).get("mobile", {}).get("scores", {}).get("performance")
            L.append(f"- {c}: public {cs.get('public')} | mobile {ms} | GEO {(x.get('geo') or {}).get('score')} | OPR {x.get('opr')} | sitemap {cp['sitemap']['urls']} urls, "
                     f"{cp['sitemap']['posts']} posts, latest {cp['sitemap']['latest_post']} | avg words {co['avg_words']} | schema {co['schema_types'][:8]} | "
                     f"arabic {x['reach']['arabic']} | age {cp['facts'].get('age_years')}y | tech {cp['tech']} | tracking {cp['tracking']} | conv {cp['conversion']}")
        L.append("content gap (their topics, not on target): " + ", ".join(d["content_gap"]))
    L.append(f"\n## Rankings (DuckDuckGo/Bing, region {d['country']})")
    for r in d["ranks"]:
        L.append(f"- {r['keyword']}: " + ("blocked" if r["results"] is None else ", ".join(f"{k} #{v}" for k, v in r["positions"].items() if v) or "none of the sites in top 10")
                 + " | top: " + ", ".join(host(u) for u in (r["results"] or [])[:5]))
    L.append("\n## Keyword ideas (top commercial/local)")
    for q, rows in d["keyword_ideas"].items():
        L.append(f"- {q}: " + "; ".join(r["keyword"] for r in rows if r["intent"] in ("commercial", "local", "question"))[:400])
    L.append("\n## Auto findings")
    for f in t["findings"]:
        L.append(f"- [{f['sev']}] {f['area']}: {f['issue']} -> {f['fix']}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
