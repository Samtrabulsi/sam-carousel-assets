#!/usr/bin/env python3
"""Scan web pages for hacked-site spam: hidden link blocks, link-farm/betting/pharma
links and suspicious injected markup. Exit code 1 if anything is found.

  python3 -I site_spam_scan.py https://site.com [https://site.com/about ...]
"""
import collections
import re
import sys
import urllib.request
from urllib.parse import urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
SPAM_WORDS = re.compile(
    r"\b(?:hacklinks?|backlink paket\w*|buy ?backlinks?|jojobet|casibom|bahis|bet ?(?:giris|giriş)|"
    r"slot ?gacor|judi ?online|togel|viagra|cialis|replica watches|escorts?|porn)\b",
    re.I)
HIDDEN = re.compile(
    r"<(?:div|p|span|marquee)[^>]*style=[\"'][^\"']*(?:display\s*:\s*none|visibility\s*:\s*hidden|"
    r"(?:width|height)\s*:\s*0(?:px)?\b|font-size\s*:\s*0|left\s*:\s*-\d{3,}px)",
    re.I)
MARQUEE_TAG = re.compile(r"<marquee\b", re.I)
TELEGRAM = re.compile(r"t\.me/[\w_]+", re.I)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.geturl(), r.status, r.read().decode("utf-8", "ignore")


def scan(url):
    final, status, html = fetch(url)
    host = urlparse(final).netloc.lower().removeprefix("www.")
    links = re.findall(r"<a\b[^>]*href=[\"'](https?://[^\"']+)[\"'][^>]*>(.*?)</a>", html, re.I | re.S)
    ext = []
    for href, text in links:
        dom = urlparse(href).netloc.lower().removeprefix("www.")
        if dom and not dom.endswith(host):
            ext.append((dom, re.sub(r"<[^>]+>", "", text).strip()))
    spam_links = [(d, t) for d, t in ext if SPAM_WORDS.search(d) or SPAM_WORDS.search(t)]
    words = collections.Counter(m.lower() for m in SPAM_WORDS.findall(html))
    findings = []
    if spam_links:
        findings.append(f"{len(spam_links)} spam-looking outbound links, e.g. "
                        + ", ".join(f"{t or '?'} -> {d}" for d, t in spam_links[:5]))
    if words:
        findings.append("spam keywords in page source: " + ", ".join(f"{w} x{n}" for w, n in words.most_common(6)))
    if MARQUEE_TAG.search(html):
        findings.append("<marquee> tag present (classic container for injected link blocks)")
    hidden = HIDDEN.findall(html)
    if hidden and (spam_links or words):
        findings.append(f"{len(hidden)} hidden elements alongside spam (likely concealed link block)")
    tg = set(TELEGRAM.findall(html))
    if tg and (spam_links or words):
        findings.append("Telegram contacts next to spam: " + ", ".join(sorted(tg)[:3]))
    top = collections.Counter(d for d, _ in ext).most_common(8)
    return final, status, len(ext), top, findings


def main(urls):
    bad = False
    for url in urls:
        try:
            final, status, n_ext, top, findings = scan(url)
        except Exception as e:  # network errors are reported, not fatal
            print(f"? {url}: could not fetch ({e})")
            bad = True
            continue
        print(f"{'FAIL' if findings else 'OK  '} {url}  (HTTP {status}, final {final}, {n_ext} external links)")
        print("     top external domains:", ", ".join(f"{d}({n})" for d, n in top) or "none")
        for f in findings:
            print("     -", f)
        bad |= bool(findings)
    if bad:
        print("\nSpam found: treat as a hacked site. Rotate passwords, update CMS/theme/plugins, "
              "scan (Wordfence/Sucuri) or restore a clean backup, then check Search Console > Security issues.")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
