#!/usr/bin/env python3
"""Publer bulk-import CSV for Instagram and Facebook: one row per carousel, in series order.

Schedule: two carousels a week (Thursday and Monday) at 4:00 pm CST, starting Thu Oct 8, 2026.
Text is the Instagram caption; alt texts are the five slide alt texts in order. Media URL(s) is
left empty unless MEDIA=path/to/links.json (carousel id -> five URLs) is set;
the filled file goes to out/ (gitignored) because the links open the portrait slides.
NETWORK=x writes the X version: the X caption (under 280 characters, no hashtags) and slides 1, 2, 3 and 5,
because X allows four images per post. Cells hold no line breaks, so every row is one line. Usage: python3 tools/publer_csv.py  ->  publer/StephenJemalNY_publer.csv
"""
import csv, datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = datetime.date(2026, 10, 8)   # Thursday
GAPS = (4, 3)                        # Thu -> Mon (4 days), Mon -> Thu (3 days)
TIME = "16:00 CST"
HEADER = ["Date - Intl. format or prompt", "Text", "Link(s) - Separated by comma for FB carousels",
          "Media URL(s) - Separated by comma", "Title - For the video, pin, PDF ..", "Label(s) - Separated by comma",
          "Alt text(s) - Separated by ||", "Comment(s) - Separated by ||", "Pin board, FB album, or Google category",
          "Post subtype - I.e. story, reel, PDF ..", "CTA - For Facebook links or Google",
          "Reminder - For stories, reels, shorts, and TikToks"]


def one_line(t):
    """No line breaks inside a cell: some importers read each break as a new (empty) row."""
    return " ".join(t.split())


def main():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from palettes import PALETTES
    cars = json.load(open(os.path.join(ROOT, "jemal_carousel_design.json")))["carousels"]
    os.makedirs(os.path.join(ROOT, "publer"), exist_ok=True)
    x = os.environ.get("NETWORK") == "x"
    keep = [0, 1, 2, 4] if x else [0, 1, 2, 3, 4]
    media = json.load(open(os.environ["MEDIA"])) if os.environ.get("MEDIA") else {}
    out = os.path.join(ROOT, "out" if media else "publer", "StephenJemalNY_publer_x.csv" if x else "StephenJemalNY_publer.csv")
    day = START
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(HEADER)
        for i, c in enumerate(cars):
            alts = [c["slides"][k]["altText"].replace("||", "|") for k in keep]
            text = one_line(c["captions"]["x" if x else "instagram"])
            if x:
                text = " ".join(w for w in text.split() if not w.startswith("#"))
                assert len(text) < 280, (c["id"], len(text))
            urls = media.get(str(c["id"]), [])
            urls = [urls[k] for k in keep if k < len(urls)]
            labels = f"Carousel {c['id']:02d}, {PALETTES[c['palette']]['name']}"
            w.writerow([f"{day.isoformat()} {TIME}", text, "", ",".join(urls), "", labels,
                        " || ".join(one_line(a) for a in alts), "", "", "", "", ""])
            day += datetime.timedelta(days=GAPS[i % 2])
    print(out, len(cars), "rows")


if __name__ == "__main__":
    main()
