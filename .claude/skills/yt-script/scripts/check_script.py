#!/usr/bin/env python3
"""Check an episode script before any audio/render time is spent.

  python3 check_script.py <episode-dir> [--target-min 15 --target-max 20]

Checks: valid JSON + known scene types + required fields, estimated length, visual variety
(no type >25 % of scenes, no 3 identical types in a row, scenes 6-25 s), photo coverage, chapter
numbering, sources.md present with links, and writes FACTCHECK.md: every sentence with a number,
date, name or superlative, for the human fact-check. Exit code 1 = must fix.
"""
import argparse, json, os, re, sys

REQ = {  # scene type -> required fields (see SKILL.md for the full reference)
    "title": ["title"], "bigtext": ["text"], "agenda": ["items"], "chapter": ["n", "title"], "scenario": ["title", "lines"],
    "chat": ["title", "msgs"], "flow": ["title", "nodes"], "tools": ["items"], "steps": ["title", "items", "of"],
    "warning": ["title", "text"], "timeline": ["title", "marks"], "stat": ["num", "suffix", "label"], "email": ["to", "subject", "body"],
    "notes": [], "invoice": [], "calendar": [], "split": ["src", "outs"], "pick": ["items", "pick"], "roadmap": ["items"],
    "end": ["next"], "photo": ["title"], "year": ["year", "label"], "quote": ["text"], "compare": ["title", "left", "right"], "list": ["title", "items"],
}
WPM = 155  # Kokoro af_heart at speed 0.93: measured 1547 words -> 9:49 with pauses (~157 wpm)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--target-min", type=float, default=15); ap.add_argument("--target-max", type=float, default=20)
    a = ap.parse_args()
    errs, warns = [], []
    try:
        beats = json.load(open(os.path.join(a.ep, "script.json")))
    except Exception as e:
        print(f"FAIL: script.json unreadable: {e}"); sys.exit(1)

    words = 0; types = []; chapters = []
    for i, b in enumerate(beats):
        say, v = b.get("say", ""), b.get("v", {})
        t = v.get("t")
        if not say.strip(): errs.append(f"beat {i}: empty 'say'")
        if t not in REQ: errs.append(f"beat {i}: unknown scene type '{t}'"); continue
        for f in REQ[t]:
            if f not in v: errs.append(f"beat {i} ({t}): missing '{f}'")
        n = len(say.split()); words += n
        secs = n / WPM * 60
        if secs > 25: warns.append(f"beat {i} ({t}): ~{secs:.0f}s on one visual; split it or the screen goes stale")
        if secs < 2.5 and t not in ("chapter", "title", "bigtext", "year"): warns.append(f"beat {i} ({t}): ~{secs:.0f}s is too short for a {t} scene to read")
        types.append(t)
        if t == "chapter": chapters.append(v.get("n"))
        for k in ("bg", "photo"):
            if isinstance(v.get(k), str) and not v[k].startswith("q:") and not os.path.exists(os.path.join(a.ep, "photos", v[k] + ".jpg")):
                warns.append(f"beat {i}: photo '{v[k]}' not in photos/ (use 'q:search words' to fetch one)")

    mins = words / WPM
    if not (a.target_min <= mins <= a.target_max):
        (errs if mins < a.target_min * 0.9 or mins > a.target_max * 1.1 else warns).append(f"length ~{mins:.1f} min ({words} words); target {a.target_min:g}-{a.target_max:g} min")
    from collections import Counter
    cnt = Counter(types)
    for t, c in cnt.items():
        if c / max(1, len(types)) > 0.25 and t != "photo": warns.append(f"'{t}' is {c}/{len(types)} scenes; vary the visuals")
        if t == "photo" and c / max(1, len(types)) > 0.45: warns.append(f"'photo' is {c}/{len(types)} scenes; mix in maps/stats/lists")
    for i in range(2, len(types)):
        if types[i] == types[i-1] == types[i-2] and types[i] not in ("steps", "photo"):
            warns.append(f"beats {i-2}-{i}: three '{types[i]}' scenes in a row")
    with_photo = sum(1 for b in beats if b["v"].get("bg") or b["v"].get("photo") or b["v"].get("photos"))
    if with_photo / max(1, len(beats)) < 0.3: warns.append(f"only {with_photo}/{len(beats)} scenes have a photo; aim for 40-60 % in long videos")
    if chapters and chapters != list(range(1, len(chapters) + 1)): errs.append(f"chapter numbers {chapters} are not 1..N")
    if mins >= 10 and len(chapters) < 3: warns.append("long video with <3 chapters; add chapters (they become YouTube chapters too)")
    if beats and beats[-1]["v"].get("t") != "end": warns.append("last scene isn't 'end' (like/subscribe card)")

    src = os.path.join(a.ep, "sources.md")
    links = len(re.findall(r"https?://", open(src).read())) if os.path.exists(src) else 0
    if links < 3: errs.append(f"sources.md has {links} links; every factual video needs its sources listed")

    # fact-check list: sentences with numbers, years, money, superlatives or quotes
    pat = re.compile(r"\d|\$|percent|billion|million|thousand|hundred|the first|largest|biggest|richest|oldest|record|\bsaid\b|\bcalled\b|founded|invented|study|according", re.I)
    fc = ["# Fact-check list", "", "Tick each line after checking it against sources.md (or fix the script).", ""]
    for i, b in enumerate(beats):
        for s in re.split(r"(?<=[.!?])\s+", b.get("say", "")):
            if pat.search(s): fc.append(f"- [ ] beat {i}: {s}")
    open(os.path.join(a.ep, "FACTCHECK.md"), "w").write("\n".join(fc) + "\n")

    print(f"scenes: {len(beats)} · words: {words} · est. {mins:.1f} min · chapters: {len(chapters)} · photos: {with_photo} · sources: {links}")
    print("types: " + ", ".join(f"{t}×{c}" for t, c in cnt.most_common()))
    for w in warns: print("WARN  " + w)
    for e in errs: print("FAIL  " + e)
    print(f"FACTCHECK.md: {len(fc) - 4} claims to verify")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
