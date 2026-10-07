#!/usr/bin/env python3
"""Build every output for the @StephenJemalNY series.

Source carousels come from source/ (the original studio DATA, or the original
jemal_carousel_design.json if it has been added). Each rewritten carousel lives
in rewrite/cNN.json and replaces the source carousel with the same id.

Outputs (written to the jemal/ folder):
  jemal_carousel_design.json, jemal_carousel_studio.html,
  carruseles_flow_prompts.json / .txt / .html
"""
import glob
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
TOOLS = os.path.join(ROOT, "tools")

TOKENS = {
    "colors": {"navy": "#0B1F3A", "cardNavy": "#12294A", "gold": "#D4A84B",
               "goldLight": "#F0CF85", "white": "#FFFFFF", "muted": "#9AA5B1"},
    "fonts": {"headline": "Montserrat 800", "body": "Inter 400-600"},
    "format": {"ratio": "4:5", "width": 1080, "height": 1350,
               "safeArea": "5% from every edge (54px sides, 72px top and bottom)",
               "generation": "Google Flow has no 4:5: generate at 3:4 (1080x1440) and center-crop to 1080x1350"},
}

TEMPLATES = {
    "cover": {"fields": ["kicker", "headline", "subline", "pills?", "photo?", "scene|background", "sourceLine?", "hookAlternatives"],
              "use": "Slide 1. Hook headline of 12 words or fewer, swipe cue in the subline."},
    "cards_stack": {"fields": ["kicker", "headline", "cards[{icon?, title?, body?, checklist?, pullLine?, accent?}]", "illustrationTop?", "pullLine?", "sourceLine?"],
                    "use": "2-3 ideas that each need a title and a short line."},
    "table_compare": {"fields": ["kicker", "headline", "columns[2]", "rows[[left, right]]", "pullLine?", "sourceLine?"],
                      "use": "Before/after, A vs B, or value-to-example pairs."},
    "stats_rows": {"fields": ["kicker", "headline", "rows[[label, text]]", "pullLine?", "sourceLine"],
                   "use": "A number or short label broken down row by row."},
    "stats_cards": {"fields": ["kicker", "headline", "stats[[number, label]]", "pullLine?", "sourceLine"],
                    "use": "Two or three big numbers that each deserve a full-width card."},
    "stats_grid": {"fields": ["kicker", "headline", "stats[[number, label]] | cards[[title, line]]", "pullLine?", "sourceLine?"],
                   "use": "Four short facts or numbers in a 2x2 grid."},
    "timeline_vertical": {"fields": ["kicker", "headline", "subtitle?", "points[]", "photo?", "sourceLine?"],
                          "use": "Dated or ordered events."},
    "flow_steps": {"fields": ["kicker", "headline", "body?", "flow[[label, icon]]", "cards?", "pullLine?", "sourceLine?"],
                   "use": "A 3-4 step process or path."},
    "name_cards_grid": {"fields": ["kicker", "headline", "body", "names[[monogram, name, tag?]]", "pullLine?", "sourceLine?"],
                        "use": "People named with monograms (no generated likeness)."},
    "stat_flow_checklist": {"fields": ["kicker", "headline", "topCard[number, text]", "flow", "checklistTitle", "checklist[]", "pullLine?", "sourceLine?"],
                            "use": "A dated fact, a 3-step flow and a checklist on one slide."},
    "numbered_cta": {"fields": ["kicker", "headline", "rows[] (6 or fewer)", "button (comment prompt)", "followLine (Follow @StephenJemalNY)"],
                     "use": "Slide 5. Save-worthy checklist plus one comment prompt and the follow line."},
}

# Banner / background descriptions, copied from the existing Flow prompts.
SCENES = {
    "houses": "a row of small houses with warm lit windows",
    "storefront": "a glowing lit corner storefront with an awning at dusk",
    "stairs": "gold steps rising with an upward arrow",
    "megaphone": "a gold megaphone with radiating arcs of light",
    "pillars": "four gold columns supporting a roof",
    "row": "a row of identical storefronts, one lit and the others in gold wireframe",
    "clipboard": "a clipboard with glowing gold check marks",
    "conveyor": "boxes riding a conveyor belt in warm light",
    "crane": "a construction crane beside an unfinished building frame",
    "map": "a top-down city street map with a glowing gold route and pins",
    "tower": "a lit apartment tower beside smaller buildings",
    "blueprint": "a gold blueprint grid with a house outline and dimension lines",
    "globe": "a glowing globe with gold meridians and pinpoint lights",
    "chart": "glowing gold bars rising like a skyline with an upward line",
    "factory": "a precision factory hall with a conveyor and glowing machines",
    "shield": "a gold shield with a check mark",
    "tag": "a gold price tag",
    "keys": "a large brass key beside a small house",
    "scale": "a golden balance scale in perfect balance",
    "clock": "a glowing clock with gold gears",
    "laser": "a laser beam scanning a building panel with fine measurement ticks",
    "cloud": "a glowing cloud linked by gold light lines to small buildings",
    "robot": "a robotic arm placing a panel on a conveyor in a gleaming factory",
    "skyline": "a dense city skyline at golden hour with lit windows",
}

LABELS = {1: "Portada", 2: "Contenido 1", 3: "Contenido 2", 4: "Contenido 3", 5: "Cierre y seguir"}
STYLE_REF = "Imagen 1 como referencia de estilo"
CROP = ("Generate it at 3:4 (1080x1440) and center-crop to 4:5: keep all text and every key element "
        "inside the central 1080x1350 area, at least 5% away from every edge of that area.")
CLOSE = "Clean spacing, strong hierarchy, easy to read on a phone. Strong contrast. No other text, no watermarks, no misspellings."
PHOTO_RULES = ("Do not redraw, retouch, restyle or alter any face, features or clothing in any way. Only crop it to fit "
               "the frame and add a soft gold edge glow. Do not generate any other person, face or figure anywhere in the image.")


def load_source():
    design = os.path.join(SRC, "jemal_carousel_design.json")
    if os.path.exists(design):
        with open(design) as f:
            d = json.load(f)
        return d, d["carousels"]
    with open(os.path.join(SRC, "data_extracted.json")) as f:
        return None, json.load(f)


def load_rewrites():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "rewrite", "c*.json"))):
        with open(p) as f:
            c = json.load(f)
        out[c["id"]] = c
    return out


def finalize(c, rewritten):
    c = dict(c)
    if rewritten:
        c["caption"] = c["captions"]["instagram"]
        c["needsApproval"] = any(s.get("needsApproval") for s in c["slides"]) or bool(c.get("captionsNeedApproval"))
        c["rewritten"] = True
    return c


def icon_name(n):
    return n.replace("-", " ")


def q(t):
    return '"' + t.replace('"', '\\"') + '"'


def text_block(s, total):
    t = s["template"]
    L = ["TEXT (render exactly as written, perfect spelling, bold modern sans-serif):",
         f"- Top, small gold caps: {q(s['kicker'])}"]
    if t == "cover":
        side = " on the left side" if s.get("photo") else ""
        L.append(f"- Very large white bold headline{side}: {q(s['headline'])}")
        L.append(f"- Under it, smaller gold line: {q(s['subline'])}")
        if s.get("pills"):
            L.append("- A row of small rounded pill labels near the bottom left: " + ", ".join(q(p) for p in s["pills"]))
    else:
        L.append(f"- Large white headline: {q(s['headline'])}")
        if s.get("subtitle"):
            L.append(f"- Small gold subtitle: {q(s['subtitle'])}")
        if s.get("body") and t in ("flow_steps", "name_cards_grid"):
            L.append(f"- White body text: {q(s['body'])}")
    if t == "cards_stack":
        numbered = all(not x.get("icon") and not x.get("title") for x in s["cards"])
        for i, cd in enumerate(s["cards"], 1):
            L.append(card_line(cd, i, numbered))
    elif t == "table_compare":
        L.append(f"TWO-COLUMN TABLE in a rounded dark navy card with thin gold borders. Gold caps column headers: left {q(s['columns'][0])}, right {q(s['columns'][1])}. A gold arrow between the columns on every row. Rows, white text:")
        L += [f"{q(a)} → {q(b)}" for a, b in s["rows"]]
    elif t == "stats_rows":
        L.append(f"{len(s['rows'])} STACKED ROWS in rounded dark navy cards with thin gold borders; big gold label on the left, white text on the right:")
        L += [f"{q(a)} - {q(b)}" for a, b in s["rows"]]
    elif t == "stats_cards":
        L.append(f"{len(s['stats'])} LARGE STAT CARDS stacked, each a rounded dark navy card with a thin gold border, a huge gold number and white text:")
        L += [f"{q(a)} - {q(b)}" for a, b in s["stats"]]
    elif t == "stats_grid":
        if s.get("stats"):
            L.append(f"{len(s['stats'])} STAT CARDS in a 2x2 grid, each a rounded dark navy card with a thin gold border, a big gold number and a white label:")
            L += [f"{q(a)} - {q(b)}" for a, b in s["stats"]]
        else:
            L.append(f"{len(s['cards'])} CARDS in a 2x2 grid, rounded dark navy with thin gold borders, each with a gold title and a short white line:")
            L += [f"{q(a)} - {q(b)}" for a, b in s["cards"]]
    elif t == "timeline_vertical":
        L.append("VERTICAL TIMELINE with gold dots joined by a gold line, white text:")
        L += [q(p) for p in s["points"]]
    elif t == "flow_steps":
        L.append(flow_line(s["flow"], False))
        for i, cd in enumerate(s.get("cards") or [], 1):
            L.append(card_line(cd, i, False))
    elif t == "name_cards_grid":
        parts = []
        for m, n, tag in s["names"]:
            parts.append(f"{q(m)} with {q(n)}" + (f" and small gold text {q(tag)}" if tag else ""))
        L.append("FOUR LARGE NAME CARDS in a 2x2 grid, rounded dark navy with thin gold borders, each with a big gold monogram circle and the name beneath: " + ", ".join(parts))
    elif t == "stat_flow_checklist":
        L.append(f"TOP CARD (rounded dark navy, gold border): big gold {q(s['topCard'][0])} with white text {q(s['topCard'][1])}.")
        L.append(flow_line(s["flow"], True))
        n = len(s["checklist"])
        words = {3: "three", 4: "four", 5: "five", 6: "six"}.get(n, str(n))
        L.append(f"CHECKLIST CARD with gold title {q(s['checklistTitle'])} and {words} short white lines with gold check icons: " + ", ".join(q(x) for x in s["checklist"]))
    elif t == "numbered_cta":
        L.append(f"{len(s['rows'])} NUMBERED ROWS, each a rounded dark navy bar with a gold number circle on the left and white text:")
        L += [f'"{i}" - {q(r)}' for i, r in enumerate(s["rows"], 1)]
        L.append(f"- Gold rounded button with dark navy text: {q(s['button'])}")
        L.append(f"- Below it, white text: {q(s['followLine'])}")
    if s.get("pullLine") and t != "numbered_cta":
        kind = "line" if s.get("pullStyle") == "plain" else "pull line"
        L.append(f"- Gold italic {kind}: {q(s['pullLine'])}")
    if s.get("sourceLine"):
        where = "under the gold line" if t == "cover" else "above the footer"
        L.append(f"- Small gray source line {where}: {q(s['sourceLine'])}")
    L.append('- Bottom left, tiny gray: "@StephenJemalNY"')
    L.append(f'- Bottom right, tiny gray: "{s["n"]}/{total}"')
    return "\n".join(L)


def card_line(cd, i, numbered):
    if cd.get("accent"):
        frame = "rounded dark navy card with a left gold accent bar"
    elif cd.get("icon"):
        frame = f"rounded dark navy card with a thin gold border, gold line icon of {icon_name(cd['icon'])} in a gold circle"
    elif numbered:
        frame = f"rounded dark navy card with a thin gold border, gold numbered circle {i}"
    else:
        frame = "rounded dark navy card with a thin gold border"
    bits = []
    if cd.get("title"):
        bits.append(f"gold title {q(cd['title'])}")
    if cd.get("body"):
        bits.append(("white italic text " if cd.get("italic") else "white body ") + q(cd["body"]))
    if cd.get("checklist"):
        bits.append("white lines with small gold check icons: " + ", ".join(q(x) for x in cd["checklist"]))
    if cd.get("pills"):
        bits.append("a row of small gold pill labels: " + ", ".join(q(x) for x in cd["pills"]))
    if cd.get("pullLine"):
        bits.append(f"gold italic line {q(cd['pullLine'])}")
    return f"CARD {i} ({frame}): " + ", ".join(bits)


def flow_line(f, compact):
    kind = "compact rounded dark navy tiles" if compact else "rounded dark navy tiles"
    lab = "a white caps label" if compact else "a small white caps label"
    tiles = ", ".join(f"gold line icon of {icon_name(ic)} with label {q(lb)}" for lb, ic in f)
    return f"FLOW of {len(f)} {kind} joined by gold arrows, each with a gold icon and {lab}: {tiles}"


def attach_for(s):
    if s["template"] == "cover":
        return "Portrait of Stephen Jemal (adjunta la foto)" if s.get("photo") else "Sin adjuntos"
    if s.get("photo"):
        return "1.º Imagen 1 como referencia de estilo; 2.º retrato de Stephen"
    return STYLE_REF


def slide_prompt(s, total):
    t = s["template"]
    P = []
    if t == "cover":
        people = "" if s.get("photo") else " No people, no faces."
        P.append("Create a 4:5 vertical social media carousel cover image (1080x1350). " + CROP +
                 " Style: premium cinematic stylized CGI 3D render background with a clean flat graphic text layer on top. "
                 "Deep navy and warm gold palette, soft volumetric glow." + people)
        if s.get("photo"):
            P.append("USE THE ATTACHED PHOTO: The attached image is a real portrait of Stephen Jemal. Place it exactly as provided "
                     f"in a rounded-rectangle frame with a thin gold border, {s['photo']['placement']}. " + PHOTO_RULES)
        if s.get("background"):
            bg = s["background"].rstrip(".") + "."
        else:
            bg = (f"A stylized CGI scene of {SCENES[s['scene']]}, rendered large in the upper half of the image, "
                  "darkened and blurred so the text stays readable.")
        P.append(f"BACKGROUND: {bg} Faint gold blueprint grid.")
    else:
        if s.get("photo"):
            P.append(f"Create a 4:5 vertical social media carousel slide (1080x1350), slide {s['n']} of {total}. " + CROP +
                     " The FIRST attached image is the style reference: match its deep navy background, warm gold accents and subtle blueprint grid.")
            P.append("USE THE ATTACHED PHOTO: The SECOND attached image is a real portrait of Stephen Jemal. Place it exactly as provided "
                     f"in a rounded-rectangle frame with a thin gold border, {s['photo']['placement']}. " + PHOTO_RULES)
        else:
            P.append(f"Create a 4:5 vertical social media carousel slide (1080x1350), slide {s['n']} of {total}. " + CROP +
                     " Match the style of the attached reference image: deep navy background, warm gold accents, subtle blueprint grid. No people, no faces.")
        if s.get("scene") and t != "numbered_cta" and not (t == "timeline_vertical" and s.get("photo")):
            P.append("ILLUSTRATION BANNER: directly under the headline, a wide rounded-rectangle illustration with a thin gold border, "
                     f"about 14% of the slide height: a stylized CGI 3D render of {SCENES[s['scene']]}, in deep navy and warm gold, "
                     "no people, no text. If space is tight, make the banner shorter rather than shrinking the text.")
        if s.get("illustrationTop"):
            P.append("ILLUSTRATION: at the top, about 20% of the slide height, in a rounded frame with a thin gold border: "
                     + s["illustrationTop"].rstrip(".") + ".")
    P.append(text_block(s, total))
    P.append(CLOSE)
    return "\n\n".join(P)


def build_prompts(cars):
    out = []
    for c in cars:
        total = len(c["slides"])
        ups = []
        for s in c["slides"]:
            if s.get("photoUpgrade"):
                ups.append(f"Imagen {s['n']}: {s['photoUpgrade']['description']}")
        out.append({
            "id": str(c["id"]), "title": c["title"], "pillar": c["pillar"], "caption": c["caption"],
            "slides": [{"n": str(s["n"]), "label": LABELS[s["n"]], "attach": attach_for(s),
                        "prompt": slide_prompt(s, total)} for s in c["slides"]],
            "upgrades": ups,
        })
    return out


def prompts_txt(pc):
    L = []
    for c in pc:
        L.append(f"=== CARRUSEL {c['id']}: {c['title']} ({c['pillar']}) ===")
        for s in c["slides"]:
            L.append(f"--- Imagen {s['n']}: {s['label']} [{s['attach']}] ---")
            L.append(s["prompt"])
            L.append("")
        L.append("--- Caption ---")
        L.append(c["caption"])
        L.append("")
        L.append("")
    return "\n".join(L)


def prompts_html(pc, rewritten_ids):
    e = html.escape
    secs = []
    for c in pc:
        tag = '<span class="tag">rewritten</span>' if int(c["id"]) in rewritten_ids else '<span class="tag old">original copy</span>'
        items = "".join(
            f'<article><header><h3>Imagen {s["n"]}: {e(s["label"])}</h3><span class="att">{e(s["attach"])}</span>'
            f'<button type="button" data-copy>Copy</button></header><pre>{e(s["prompt"])}</pre></article>'
            for s in c["slides"])
        secs.append(f'<section id="c{c["id"]}"><h2>Carousel {c["id"]}: {e(c["title"])} {tag}</h2><p class="pil">{e(c["pillar"])}</p>{items}'
                    f'<details><summary>Caption</summary><pre>{e(c["caption"])}</pre></details></section>')
    nav = "".join(f'<option value="c{c["id"]}">{c["id"]}: {e(c["title"])}</option>' for c in pc)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jemal Flow Prompts</title>
<style>
:root{{--bg:#070d18;--panel:#0f1a2c;--line:#22314a;--text:#e8edf5;--mute:#9AA5B1;--gold:#D4A84B}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,system-ui,sans-serif}}
.top{{position:sticky;top:0;background:var(--panel);border-bottom:1px solid var(--line);padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:2}}
.top h1{{font-size:16px;margin:0}}.top h1 span{{color:var(--gold)}}
select,button{{background:#16253d;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:7px 11px;font:inherit;cursor:pointer}}
button:hover,select:hover{{border-color:var(--gold)}}
main{{max-width:960px;margin:0 auto;padding:8px 16px 60px}}
section{{margin-top:28px}}h2{{font-size:20px;margin:0}}.pil{{color:var(--mute);margin:2px 0 10px}}
.tag{{font-size:12px;border:1px solid var(--gold);color:var(--gold);border-radius:6px;padding:1px 7px;margin-left:6px;vertical-align:middle}}.tag.old{{border-color:var(--line);color:var(--mute)}}
article{{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:10px 0;overflow:hidden}}
article header{{display:flex;gap:10px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}}
h3{{font-size:15px;margin:0}}.att{{color:var(--mute);font-size:13px;flex:1}}
pre{{margin:0;padding:12px 14px;white-space:pre-wrap;word-break:break-word;font:13px/1.55 ui-monospace,Menlo,monospace}}
details{{margin-top:6px}}summary{{cursor:pointer;color:var(--gold)}}
</style></head><body>
<div class="top"><h1><span>@StephenJemalNY</span> Google Flow prompts</h1><select id="jump" aria-label="Jump to carousel">{nav}</select>
<span style="color:var(--mute);font-size:13px">4:5 (1080x1350). Generate at 3:4, center-crop.</span></div>
<main>{''.join(secs)}</main>
<script>
document.getElementById('jump').onchange=e=>document.getElementById(e.target.value).scrollIntoView();
document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=async()=>{{const t=b.closest('article').querySelector('pre').textContent;
try{{await navigator.clipboard.writeText(t);b.textContent='Copied'}}catch(e){{b.textContent='Copy failed'}}setTimeout(()=>b.textContent='Copy',1500)}});
</script></body></html>
"""


def main():
    design, src = load_source()
    rw = load_rewrites()
    cars = [finalize(rw.get(c["id"], c), c["id"] in rw) for c in src]
    assert len(cars) == 52

    if design is None:
        design = {
            "_note": "Reconstructed from the studio DATA because the original jemal_carousel_design.json was not supplied. "
                     "When the original is added to source/, its tokens, components and rules are kept and only 'templates' and 'carousels' are updated.",
            "tokens": TOKENS,
        }
    design = dict(design)
    design["templates"] = {**design.get("templates", {}), **TEMPLATES} if isinstance(design.get("templates"), dict) else TEMPLATES
    design["scenes"] = SCENES
    design["carousels"] = cars
    with open(os.path.join(ROOT, "jemal_carousel_design.json"), "w") as f:
        json.dump(design, f, indent=1, ensure_ascii=False)

    with open(os.path.join(TOOLS, "studio_template.html")) as f:
        tpl = f.read()
    data = json.dumps(cars, ensure_ascii=False).replace("</", "<\\/")
    vendor = os.path.join(TOOLS, "vendor")
    libs = "\n".join(open(os.path.join(vendor, n)).read().replace("</script", "<\\/script")
                     for n in ("html2canvas.min.js", "jszip.min.js"))
    fonts = open(os.path.join(vendor, "fonts_embedded.css")).read()
    out = tpl.replace("/*FONTS*/", fonts).replace("/*LIBS*/", libs).replace("/*DATA*/[]", data)
    with open(os.path.join(ROOT, "jemal_carousel_studio.html"), "w") as f:
        f.write(out)

    pc = build_prompts(cars)
    with open(os.path.join(ROOT, "carruseles_flow_prompts.json"), "w") as f:
        json.dump(pc, f, indent=1, ensure_ascii=False)
    with open(os.path.join(ROOT, "carruseles_flow_prompts.txt"), "w") as f:
        f.write(prompts_txt(pc))
    with open(os.path.join(ROOT, "carruseles_flow_prompts.html"), "w") as f:
        f.write(prompts_html(pc, set(rw)))
    print(f"Built 52 carousels ({len(rw)} rewritten: {sorted(rw)}), {sum(len(c['slides']) for c in pc)} prompts.")


if __name__ == "__main__":
    main()
