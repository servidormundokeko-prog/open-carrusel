# @StephenJemalNY carousel series

Open `jemal_carousel_studio.html` in a browser to swipe the carousels, read the captions and export PNGs. It works offline, and on a phone, "Save" opens the share sheet.

| Path | What it is |
|---|---|
| `rewrite/cNN.json` | Rewritten carousels (the copy you edit) |
| `source/` | Original client files, untouched |
| `jemal_carousel_design.json` | Full series: templates, scenes, 52 carousels |
| `carruseles_flow_prompts.{txt,json,html}` | 260 Google Flow prompts |
| `APPROVAL_CHECKLIST.md`, `DESIGN_NOTES.md`, `CHANGELOG.md` | Review docs |
| `previews/` | 1080x1350 renders of all 52 carousels, plus a contact sheet each (portrait frames left empty) |
| `render/` | Remotion renderStill pipeline: final PNGs and ZIP in `out/` |
| `tools/slide_core.js`, `tools/slide.css`, `tools/palettes.py` | The shared slide renderer and the pillar palettes |
| `assets/photos/`, `IMAGE_CREDITS.md` | Grayscale Pixabay photos (duotoned at render time) and their credits |

Rebuild and check:

```
python3 tools/build.py            # regenerate the studio, design JSON and prompts
python3 validate.py --rewritten   # check rewritten carousels (no flag = all 52)
node tools/render_previews.mjs 1 10 35
```

Final PNGs with Remotion (one folder per carousel, `01.png`-`05.png`, plus a ZIP in `out/`):

```
cd render && npm install
PORTRAIT=/path/to/portrait.jpg node render.mjs        # all 52; or list ids: node render.mjs 1 27
python3 ../tools/contact_sheet.py sheet.png 1 27     # quick review sheet
```

The portrait is read from your disk and never committed. Without `PORTRAIT`, the three portrait frames stay empty.
