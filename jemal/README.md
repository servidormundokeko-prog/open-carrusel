# @StephenJemalNY carousel series

Open `jemal_carousel_studio.html` in a browser to swipe the carousels, read the captions and export PNGs. It works offline, and on a phone, "Save" opens the share sheet.

| Path | What it is |
|---|---|
| `rewrite/cNN.json` | Rewritten carousels (the copy you edit) |
| `source/` | Original client files, untouched |
| `jemal_carousel_design.json` | Full series: templates, scenes, 52 carousels |
| `carruseles_flow_prompts.{txt,json,html}` | 260 Google Flow prompts |
| `APPROVAL_CHECKLIST.md`, `DESIGN_NOTES.md`, `CHANGELOG.md` | Review docs |
| `previews/` | 1080x1350 renders of rewritten carousels |

Rebuild and check:

```
python3 tools/build.py            # regenerate the studio, design JSON and prompts
python3 validate.py --rewritten   # check rewritten carousels (no flag = all 52)
node tools/render_previews.mjs 1 10 35
```
