#!/usr/bin/env python3
"""Validate the @StephenJemalNY carousel series.

Usage:
  python3 validate.py                 # every carousel
  python3 validate.py --rewritten     # only carousels already rewritten
  python3 validate.py --ids 1,10,35   # specific carousels

Structural checks (52 carousels x 5 slides, studio and prompt files) always run
on the whole series. Exit code is 1 if any ERROR is found; WARN lines are for review.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDLE = "@StephenJemalNY"

BANNED = ["leveraging", "leverage", "synergy", "disrupting", "disrupt", "game-changing", "game changing",
          "revolutionary", "cutting-edge", "cutting edge", "unlock", "unlocks", "unlocking", "ecosystem",
          "world-class", "world class", "passionate", "thrilled", "journey"]
FORBIDDEN = [
    (r"(?<![\d.,])110(?![\d,])", "110 (Wiz store count)"),
    (r"(?<![\d.,])6,?000(?![\d,])", "6,000 (Wiz headcount)"),
    (r"\$\s?2\.5", "$2.5 (Wiz sales)"),
    (r"\b2\.5\s*billion\b", "2.5 billion (Wiz sales)"),
    (r"\bsix states\b", "six states"),
    (r"\b6 states\b", "6 states"),
]
# Facts awaiting client confirmation. Nothing matching these may appear in copy or captions.
# Move an entry to CONFIRMED once the client confirms it in writing (and log it in APPROVAL_CHECKLIST.md).
UNCONFIRMED = [
    (r"\bfour sons\b|\bhis sons\b|\bwith his sons\b", "Wiz opening by 'four sons' (Stephen's role unconfirmed)"),
    (r"\bmy sons\b|\bsons of JemRock\b", "sons' roles at JemRock"),
    (r"\bSolomon\b|\bchief operating officer\b|\bCOO\b", "Solomon's title"),
    (r"\bPASHA\b", "PASHA details"),
    (r"\bCENTRAL\b", "CENTRAL details"),
    (r"H\.O\.M\.E", "H.O.M.E."),
    (r"\b(co-?)?found(ed|er|ing)\b[^.]{0,40}\bWiz\b|\bWiz\b[^.]{0,20}\bfound(ed|er)\b", "Wiz founding role"),
]
CONFIRMED = set()
ALLOWED_PHOTOS = {(1, 1), (10, 1), (11, 3)}
TEMPLATES = {"cover", "cards_stack", "table_compare", "stats_rows", "stats_cards", "stats_grid", "timeline_vertical",
             "flow_steps", "name_cards_grid", "stat_flow_checklist", "numbered_cta"}
PLATFORMS = ["instagram", "facebook", "linkedin", "x", "threads"]
# Source labels required when a slide cites these numbers.
SOURCED = [
    (r"155\s?M|240\s?M|96,000|155 million|240 million|50%\+|more than 50%", "jemrock", "Per JemRock research"),
    (r"2\.8\s?(B|billion)|1\.1\s?(B|billion)|300\s?(M|million)", "un-habitat", "Source: UN-Habitat"),
    (r"20\s?[-–]\s?50%|up to 20%|up to 10%", "mckinsey", "McKinsey, 2019"),
    (r"0\.76\s?mm", "iso", "ISO/IEC 7810"),
]
OPINION = re.compile(r"\b(I think|I believe|I'd (say|ask|put|tell|argue|recommend|use)|I would|my advice|I learned|taught me|the lesson|my rule)\b", re.I)

errors, warns = [], []


def err(where, msg):
    errors.append(f"ERROR  {where}: {msg}")


def warn(where, msg):
    warns.append(f"WARN   {where}: {msg}")


def words(t):
    return len([w for w in re.split(r"\s+", t.strip()) if w])


def flatten(x):
    if isinstance(x, str):
        return [x]
    if isinstance(x, list):
        return [s for i in x for s in flatten(i)]
    if isinstance(x, dict):
        return [s for v in x.values() for s in flatten(v)]
    return []


SKIP_BODY = {"n", "template", "kicker", "headline", "sourceLine", "altText", "attachments", "scene", "photo",
             "photoUpgrade", "background", "illustrationTop", "hookAlternatives", "needsApproval", "approvalNote", "flow_icons"}


def body_texts(s):
    """On-slide text other than kicker, headline and source line."""
    out = []
    for k, v in s.items():
        if k in SKIP_BODY:
            continue
        if k == "flow":
            out += [x[0] for x in v]
        elif k == "cards":
            for cd in v:
                if isinstance(cd, dict):
                    out += flatten({kk: vv for kk, vv in cd.items() if kk not in ("icon", "accent", "italic")})
                else:
                    out += flatten(cd)
        elif k == "names":
            out += [x for n in v for x in n if x]
        else:
            out += flatten(v)
    return out


def slide_texts(s):
    return [s.get("kicker", ""), s.get("headline", "")] + body_texts(s)


def data_number(t):
    """Numbers that state a fact: 10+, years, %, $, M/B units. Single-digit counts are framing."""
    t = re.sub(r"@\w+", "", t)
    return re.search(r"\d{2,}|\d+(\.\d+)?\s?(%|M\b|B\b|million|billion|mm\b)|\$\s?\d", t)


def check_contrast():
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    def ratio(a, b):
        la, lb = sorted([lum(a), lum(b)], reverse=True)
        return (la + 0.05) / (lb + 0.05)
    pairs = [("#FFFFFF", "#0B1F3A", "white on navy"), ("#FFFFFF", "#12294A", "white on card navy"),
             ("#9AA5B1", "#0B1F3A", "muted on navy"), ("#9AA5B1", "#12294A", "muted on card navy"),
             ("#D4A84B", "#0B1F3A", "gold on navy"), ("#D4A84B", "#12294A", "gold on card navy"),
             ("#0B1F3A", "#D4A84B", "navy on gold (button)")]
    for fg, bg, name in pairs:
        r = ratio(fg, bg)
        if r < 4.5:
            err("contrast", f"{name} is {r:.2f}:1, below WCAG AA 4.5:1")
    return [(name, round(ratio(fg, bg), 2)) for fg, bg, name in pairs]


def check_carousel(c):
    cid = c["id"]
    W = f"C{cid}"
    slides = c["slides"]
    tmpl = [s["template"] for s in slides]
    if len(set(tmpl[1:4])) < 3:
        warn(W, f"slides 2-4 repeat a template: {tmpl[1:4]}")
    if max(tmpl.count(t) for t in tmpl) >= 5:
        err(W, "same template used five times")
    if tmpl[0] != "cover" or tmpl[4] != "numbered_cta":
        err(W, "slide 1 must be cover and slide 5 numbered_cta")
    any_flag = False
    for s in slides:
        w = f"C{cid}S{s['n']}"
        any_flag |= bool(s.get("needsApproval"))
        for f in ("template", "kicker", "headline", "altText"):
            if not s.get(f):
                err(w, f"missing {f}")
        if s.get("template") not in TEMPLATES:
            err(w, f"unknown template {s.get('template')}")
        alt = re.sub(r"'[^']*'|\"[^\"]*\"|\b[A-Z]\.", "", s.get("altText") or "")
        if alt and len(re.findall(r"[.!?](\s|$)", alt.strip())) > 1:
            warn(w, "altText should be one sentence")
        if words(s.get("headline", "")) > 12:
            err(w, f"headline has {words(s['headline'])} words (max 12)")
        bw = sum(words(t) for t in body_texts(s))
        if bw > 40:
            err(w, f"body has {bw} words (max 40)")
        for k in ("rows", "points", "checklist", "stats", "pills"):
            if isinstance(s.get(k), list) and len(s[k]) > 6:
                err(w, f"{k} has {len(s[k])} items (max 6)")
        for cd in s.get("cards") or []:
            if isinstance(cd, dict) and len(cd.get("checklist") or []) > 6:
                err(w, "card checklist has more than 6 items")
        if s["n"] in (2, 3, 4) and not s.get("scene") and not s.get("photo"):
            err(w, "content slide has no banner scene")
        if s.get("photo") and (cid, s["n"]) not in ALLOWED_PHOTOS:
            err(w, "photo slot outside the allowed slots (C1S1, C10S1, C11S3)")
        texts = slide_texts(s)
        joined = " ".join(texts)
        if re.search(r"Stephen", re.sub(r"@StephenJemalNY", "", joined)):
            err(w, "third-person 'Stephen' in slide copy")
        nums = [t for t in texts if data_number(t)]
        if nums and not s.get("sourceLine"):
            err(w, f"number without a source line: {nums[0]!r}")
        alltext = joined + " " + (s.get("sourceLine") or "")
        for pat, key, label in SOURCED:
            if re.search(pat, joined, re.I) and key not in (s.get("sourceLine") or "").lower().replace("jemrock", "jemrock"):
                if not (key == "jemrock" and "jemrock" in (s.get("sourceLine") or "").lower()):
                    err(w, f"cites a {label} number but the source line doesn't say so")
        if re.search(r"(?<![-\w])BUILT(?!®)\b", alltext) and not re.search(r"\b(I|WE|HE)\s+BUILT\b", alltext, re.I):
            for t in texts:
                if re.search(r"(?<![-\w])BUILT(?!®)", t) and t != t.upper():
                    err(w, f"BUILT without ®: {t!r}")
        if re.search(r"(?<![-\w])(PASHA|BUILT)\b", joined) and re.search(r"\b(first|only)\b", joined, re.I):
            warn(w, "'first'/'only' near PASHA or BUILT®: check it is not a claim about them")
        if OPINION.search(joined) and not s.get("needsApproval"):
            warn(w, "opinion/lesson phrasing without needsApproval")
        if 14 <= cid <= 26 and nums:
            err(w, "carousels 14-26 must stay stat-free")
        if s["template"] == "cover":
            h = s.get("hookAlternatives") or []
            if len(h) != 3:
                err(w, f"cover needs 3 hookAlternatives (has {len(h)})")
            elif s["headline"].rstrip(".").upper() not in [x["text"].upper().rstrip(".") for x in h]:
                warn(w, "headline is not one of the hookAlternatives")
        if s["n"] == 5:
            if not re.match(r"comment\b", s.get("button", ""), re.I):
                err(w, "slide 5 needs a comment prompt in 'button' (starts with 'Comment')")
            if "Follow @StephenJemalNY" not in s.get("followLine", ""):
                err(w, "slide 5 needs 'Follow @StephenJemalNY'")
    if cid == 18 and "General guidance, not legal advice" not in json.dumps(c):
        err(W, "lease carousel must say 'General guidance, not legal advice'")
    caps = c.get("captions") or {}
    for p in PLATFORMS:
        t = caps.get(p)
        if not t:
            err(W, f"missing {p} caption")
            continue
        if not t.rstrip().endswith("?"):
            err(W, f"{p} caption must end with a question")
        if len(re.findall(r"#\w+", t)) > 3:
            err(W, f"{p} caption has more than 3 hashtags")
        if not re.search(r"\b(I|I'm|I've|I'd|me|my|we|our|My|We|Our)\b", t):
            warn(W, f"{p} caption has no first-person word")
        if re.search(r"Stephen", t.replace(HANDLE, "")):
            err(W, f"{p} caption uses third-person 'Stephen'")
    if caps.get("x") and len(caps["x"]) > 280:
        err(W, f"x caption is {len(caps['x'])} characters (max 280)")
    if caps.get("linkedin") and words(caps["linkedin"]) > 150:
        err(W, f"linkedin caption is {words(caps['linkedin'])} words (max 150)")
    if any_flag != bool(c.get("needsApproval")) and not c.get("captionsNeedApproval"):
        warn(W, "carousel needsApproval does not match its slides")
    everything = json.dumps({k: v for k, v in c.items()}, ensure_ascii=False)
    everything = re.sub(r'"(altText|approvalNote|mechanism|captionsNeedApproval)": "(\\.|[^"\\])*"', "", everything)
    for b in BANNED:
        if re.search(r"(?<![\w-])" + re.escape(b) + r"(?![\w-])", everything, re.I):
            (warn if b == "journey" else err)(W, f"banned word: {b}")
    for pat, label in FORBIDDEN:
        if re.search(pat, json.dumps(c, ensure_ascii=False), re.I):
            err(W, f"forbidden figure: {label}")
    for pat, label in UNCONFIRMED:
        if label not in CONFIRMED and re.search(pat, everything):
            err(W, f"unconfirmed fact: {label}")


def check_files(cars):
    p = os.path.join(ROOT, "carruseles_flow_prompts.json")
    if not os.path.exists(p):
        err("files", "carruseles_flow_prompts.json missing")
        return
    pc = json.load(open(p))
    n = sum(len(c["slides"]) for c in pc)
    if n != 260:
        err("prompts", f"{n} prompts (expected 260)")
    for c, d in zip(pc, cars):
        if not d.get("rewritten"):
            continue
        for s, ds in zip(c["slides"], d["slides"]):
            w = f"C{c['id']}S{s['n']} prompt"
            pr = s["prompt"]
            for need in ("(1080x1350)", "center-crop", f'"{HANDLE}"', f'"{s["n"]}/5"'):
                if need not in pr:
                    err(w, f"missing {need}")
            if "USE THE ATTACHED PHOTO" in pr and (int(c["id"]), int(s["n"])) not in ALLOWED_PHOTOS:
                err(w, "photo block outside a photo slot")
            if (int(c["id"]), int(s["n"])) not in ALLOWED_PHOTOS and "No people, no faces" not in pr:
                err(w, "missing 'No people, no faces'")
            for t in slide_texts(ds):
                if '"' + t.replace('"', '\\"') + '"' not in pr:
                    err(w, f"slide text not in prompt verbatim: {t!r}")
    st = os.path.join(ROOT, "jemal_carousel_studio.html")
    if os.path.exists(st):
        h = open(st).read()
        for need in ("@StephenJemalNY</span>", "html2canvas", "JSZip", "Choose image", "const DATA = [{"):
            if need not in h:
                err("studio", f"missing {need!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    ap.add_argument("--rewritten", action="store_true")
    a = ap.parse_args()
    d = json.load(open(os.path.join(ROOT, "jemal_carousel_design.json")))
    cars = d["carousels"]
    if len(cars) != 52:
        err("series", f"{len(cars)} carousels (expected 52)")
    for c in cars:
        if len(c["slides"]) != 5:
            err(f"C{c['id']}", f"{len(c['slides'])} slides (expected 5)")
    sel = cars
    if a.ids:
        ids = {int(x) for x in a.ids.split(",")}
        sel = [c for c in cars if c["id"] in ids]
    elif a.rewritten:
        sel = [c for c in cars if c.get("rewritten")]
    for c in sel:
        check_carousel(c)
    ratios = check_contrast()
    check_files(cars)
    print("\n".join(errors + warns) or "No issues.")
    print(f"\nChecked {len(sel)} carousel(s): {len(errors)} error(s), {len(warns)} warning(s).")
    print("Contrast: " + ", ".join(f"{n} {r}:1" for n, r in ratios))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
