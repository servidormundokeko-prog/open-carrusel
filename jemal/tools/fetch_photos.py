#!/usr/bin/env python3
"""Fetch one Pixabay photo per scene (no people), crop to 1080x1350 cover size,
convert to grayscale for duotoning, and record credits.

Needs PIXABAY_API_KEY. Usage: python3 tools/fetch_photos.py [scene ...]
Picks live in PICKS (scene -> Pixabay id) once chosen; QUERIES find candidates.
"""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "photos")
PICKS_FILE = os.path.join(OUT, "picks.json")
QUERIES = {
    "houses": "row houses street", "storefront": "storefront shop window night", "stairs": "staircase steps architecture",
    "megaphone": "megaphone", "pillars": "classical columns building", "row": "shop fronts street row",
    "clipboard": "clipboard checklist", "conveyor": "conveyor belt boxes warehouse", "crane": "construction crane building",
    "map": "city map aerial", "tower": "apartment tower building", "blueprint": "blueprint architecture plan",
    "globe": "globe earth", "chart": "stock chart graph", "factory": "factory hall machines", "shield": "shield metal",
    "tag": "price tag", "keys": "house keys", "scale": "balance scale", "clock": "clock gears",
    "laser": "laser beam", "cloud": "server data center", "robot": "industrial robot arm", "skyline": "new york skyline",
}
PEOPLE = {"person", "people", "man", "woman", "girl", "boy", "child", "men", "women", "worker", "workers", "face",
          "portrait", "human", "hand", "hands", "businessman", "businesswoman", "couple", "family", "crowd", "model", "lady"}


UA = {"User-Agent": "Mozilla/5.0 (jemal-carousel-build)"}


def get(url, t):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t)


def api(**kw):
    kw.update(key=os.environ["PIXABAY_API_KEY"], image_type="photo", safesearch="true", per_page=30)
    with get("https://pixabay.com/api/?" + urllib.parse.urlencode(kw), 30) as r:
        return json.load(r)["hits"]


def candidates(scene):
    hits = api(q=QUERIES[scene], orientation="vertical", min_width=1000) + api(q=QUERIES[scene], min_width=1600)
    seen, out = set(), []
    for h in hits:
        tags = {t.strip() for t in h["tags"].lower().split(",")} | set(h["tags"].lower().replace(",", " ").split())
        if h["id"] in seen or tags & PEOPLE:
            continue
        seen.add(h["id"])
        out.append(h)
    return out


def process(scene, h):
    with get(h["largeImageURL"], 60) as r:
        im = Image.open(io.BytesIO(r.read())).convert("L")
    im = ImageOps.fit(im, (864, 1080), method=Image.LANCZOS, centering=(0.5, 0.5))
    im = ImageOps.autocontrast(im, cutoff=1)
    im.save(os.path.join(OUT, f"{scene}.jpg"), quality=64, optimize=True, progressive=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    picks = json.load(open(PICKS_FILE)) if os.path.exists(PICKS_FILE) else {}
    for scene in sys.argv[1:] or QUERIES:
        cands = candidates(scene)
        want = picks.get(scene, {}).get("id")
        h = next((c for c in cands if c["id"] == want), None) or (api(id=want)[0] if want else cands[0])
        process(scene, h)
        picks[scene] = {"id": h["id"], "page": h["pageURL"], "user": h["user"], "tags": h["tags"],
                        "alternatives": [c["id"] for c in cands[1:6]]}
        print(scene, h["id"], h["pageURL"])
    json.dump(picks, open(PICKS_FILE, "w"), indent=1)
    with open(os.path.join(ROOT, "IMAGE_CREDITS.md"), "w") as f:
        f.write("# Image credits\n\nStock photos from [Pixabay](https://pixabay.com/service/license-summary/) under the Pixabay Content License "
                "(free for commercial use, no attribution required; credited here anyway). No people appear in any of them. "
                "Each is cropped to 4:5 (864x1080), converted to grayscale in `assets/photos/` and duotoned in its carousel's palette at render time. "
                "Refetch with `PIXABAY_API_KEY=... python3 tools/fetch_photos.py`.\n\n| Scene | Pixabay page | Photographer |\n|---|---|---|\n")
        for s in sorted(picks):
            p = picks[s]
            f.write(f"| {s} | {p['page']} | {p['user']} |\n")


if __name__ == "__main__":
    main()
