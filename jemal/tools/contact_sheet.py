#!/usr/bin/env python3
"""Contact sheet of rendered carousels: one row per carousel, five slides across.
Usage: python3 tools/contact_sheet.py OUT.png [ids...] [--w 216]   (reads out/StephenJemalNY carousels 1080x1350/)"""
import glob, os, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
w = int(args[args.index("--w") + 1]) if "--w" in args else 216
if "--w" in args:
    del args[args.index("--w"):args.index("--w") + 2]
out, ids = args[0], [int(a) for a in args[1:]]
dirs = sorted(glob.glob(os.path.join(ROOT, "out", "StephenJemalNY carousels 1080x1350", "* - *")))
dirs = [d for d in dirs if not ids or int(os.path.basename(d)[:2]) in ids]
h, g, lab = w * 1350 // 1080, 8, 18
sheet = Image.new("RGB", (5 * w + 6 * g, len(dirs) * (h + lab + g) + g), "#05080f")
d = ImageDraw.Draw(sheet)
for r, folder in enumerate(dirs):
    y = g + r * (h + lab + g)
    d.text((g, y + 2), os.path.basename(folder), fill="#cfd6e2")
    for i in range(5):
        im = Image.open(os.path.join(folder, f"{i + 1:02d}.png")).convert("RGB").resize((w, h), Image.LANCZOS)
        sheet.paste(im, (g + i * (w + g), y + lab))
sheet.save(out)
print(out, sheet.size)
