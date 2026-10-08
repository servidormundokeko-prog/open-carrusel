# Design notes

Fonts, layout and the @StephenJemalNY footer are the same on every slide: Montserrat headlines, Inter body. Colour now follows the pillar (see "Pillar palettes" below).

## Pillar palettes (Oct 8)

Defined once in `tools/palettes.py`; `build.py` writes each carousel's `palette` into `jemal_carousel_design.json`.

| Palette | Carousels | Background / card | Accent / accent2 |
|---|---|---|---|
| Story: amber and terracotta | 1, 8, 11, 51, 52 | #24120B / #3A1D12 | #F6A93B / #EE8A63 |
| Founder lessons: gold and navy | 2, 3, 5, 10, 12, 13, 50 | #0B1F3A / #12294A | #D4A84B / #F0CF85 |
| Scaling and systems: teal and mint | 4, 6, 7, 14-26 | #04262A / #0A3A3F | #6EF0D6 / #2CC9B5 |
| BUILT technology: electric cyan and violet | 27-33, 36-39 | #0F0A28 / #1C1544 | #2EE6FF / #B69CFF |
| Housing and authority: coral and sunrise orange | 9, 34, 35 | #2A0E16 / #401925 | #FF8A6B / #FFBE5C |
| Real estate and vision: emerald and lime | 40-49 | #05231A / #0B3527 | #B5F04A / #3FDDA0 |

The Flow prompts use the same colour words (for example "deep indigo-black with electric cyan and violet"). Founder prompts are unchanged.

## Design system (Oct 8)

- **One renderer.** `tools/slide_core.js` and `tools/slide.css` draw every slide. The studio inlines them for preview and PNG/ZIP export, and the Remotion pipeline (`render/`) imports the same code. Both read the slide data from `jemal_carousel_design.json`, so the two outputs match.
- **Lucide icons (ISC).** Badges use Lucide icons. Kickers, cards, grid cells and banners get an icon picked by keyword (lease → file, robot → bot, zoning → map, and so on). If no keyword matches, the palette's own icon is used. The icons the renderer uses are cached in `tools/lucide_icons.json`, so builds work without `node_modules`.
- **Progress-bar footer.** Five segments, filled up to the current slide, above the handle and slide number.
- **Stronger cover.** A full-bleed duotone photo behind a dark veil, a pillar chip with its icon, an accent bar, a larger headline with its last word in the accent colour, and the swipe line.
- **Photos.** 24 Pixabay photos, one per scene and none with people (credits in `IMAGE_CREDITS.md`). They are stored as grayscale files in `assets/photos/`, duotoned in the carousel's palette at render time (background in the shadows, accent2 in the highlights), and used as banners and cover backgrounds. Banners grow to fill free space on the slide.
- **No box-shadow** on rounded elements, so html2canvas exports clean circles.
- **Studio: "Import images".** Pick many files at once named like `c27-s2.png` (slide 2 of carousel 27). Each goes to that slide's photo slot, otherwise its banner or cover background. Add `-bg` or `-banner` to choose.
- **Studio: "Add portrait".** One photo fills the three portrait frames (C1 slide 1, C10 slide 1, C11 slide 3). It is cropped to fit and never edited. The portrait is not stored in the repo.
- The studio file is now about 3.9 MB because the 24 photos are embedded so it still works offline.


## Layout changes, and why

| Change | Why |
|---|---|
| Bottom padding raised from 52px to 72px | The handle and slide number sat 3.9% from the bottom edge, below the 5% rule (67.5px on 1080x1350, 72px on 1080x1440). All text now clears 5% on every side. |
| Source line renders on every template, including cover, table, timeline, stat-flow and name grid | Before, only some templates showed `sourceLine`, so a cited number could appear with no source on screen. |
| Pull line renders on every template except the closing slide | `stats_rows` and `stats_cards` silently dropped `pullLine`. |
| Timeline with no subtitle no longer prints "undefined" | Bug in the original renderer. |
| Slides 2 to 4 use three different templates in every rewritten carousel | Variety keeps the swipe moving. The old C1 used `cards_stack` twice; it is now `stats_grid` → `timeline_vertical` → `table_compare`. |
| Cover source line sits under the swipe line | Covers that lead with a number (C35) need their source on slide 1. |

## Export (PNG and ZIP)

- html2canvas 1.4.1 and JSZip 3.10.1 (MIT) are now inlined, and Inter and Montserrat (OFL, latin subset) are embedded as base64. The studio makes no network requests, so exports look the same offline, behind firewalls and in in-app viewers. The file is about 590 KB.
- On phones, "Save this slide" and "Save all 5" open the share sheet with real PNG files. Choosing "Save image" puts them in Photos, ready for Instagram. Desktop still downloads a PNG or a ZIP.
- An "Exported images" panel shows every exported PNG, so you can still save by hand if a viewer blocks downloads.
- Errors say what failed. Exporting with an empty portrait slot shows a warning.
- Tested headless (`tools/test_export.mjs`): with all network blocked, the single PNG and the ZIP of five export at 1080x1350 and match the previews. On an emulated iPhone, five PNG files reach the share sheet.

## Download every carousel in one click

"Download every carousel (ZIP)" exports all 52 carousels into one ZIP:

```
StephenJemalNY carousels 1080x1350/
  01 - Youngest of ten/        01.png 02.png 03.png 04.png 05.png
  02 - Four stores at 16/      01.png ... 05.png
  ...
  52 - From Fulton Street to BUILT/
```

- **Folder names.** Each folder is the carousel number plus its title. Characters Windows and macOS don't allow in names (such as `?`) are removed.
- **File names.** Slides are numbered 01 to 05, so they sort in posting order.
- **Portraits.** Photos you add to the portrait slots are included. Any slot that is still empty is listed in the status line.
- **Headless test, all network blocked:** 260 PNGs at 1080x1350 in about 70 seconds; the ZIP is about 175 MB. Use it on a computer; a phone may run out of memory.

## Studio (preview tool) additions

These don't change the exported PNGs.

- A caption selector for Instagram, Facebook, LinkedIn, X and Threads, with a character count.
- A "Slide notes" panel that shows alt text, the 3 hook options (the chosen one in gold) and any approval note.
- Carousels that need approval show "Needs approval" in the title and ⚑ in the picker.

## Flow prompts

- The header now says 4:5 (1080x1350): generate at 3:4 (1080x1440) and center-crop, keeping all text inside the central 4:5 area. Everything else matches the original format word for word. The generator reproduces 253 of the 254 untouched original prompts exactly after the header; the one difference is C9 slide 4, which will be rewritten.
- The photo block appears only on C1 slide 1, C10 slide 1 and C11 slide 3. Every other prompt says "No people, no faces."

## Contrast (WCAG AA, 4.5:1 for body text)

`validate.py` checks every text colour on every surface for all six palettes: white, muted, accent and accent2 on the background and on cards, plus background-coloured text on accent and accent2 buttons. The lowest ratio per palette: story 6.2, founder 5.8, scaling 6.0, BUILT 7.2, housing 6.6, real estate 7.2. All pass.

## Batch 1 fixes

- **New `row` illustration in the studio.** The original data used scene `row` on 7 slides, but the studio had no drawing for it, so those banners were blank. The Flow prompt description is unchanged.
- **`stats_rows` labels widen to fit.** Long labels such as "ADVERTISING" overlapped the text. They now take 250-440px, and the auto-fit shrinks the slide if a label still doesn't fit.
- **C11 slide 2 uses one illustration.** It had both a banner and a top illustration stacked.

## No new templates

None needed so far. `row` was an existing scene name that lacked a drawing.

## Template use across the series

Every carousel opens with `cover` and closes with `numbered_cta`. Slides 2-4 use three different templates in all 52 carousels. Counts across slides 2-4: flow_steps 44, cards_stack 37, table_compare 32, stats_grid 21, stats_rows 12, stats_cards 5, timeline_vertical 4, stat_flow_checklist 1. `name_cards_grid` is no longer used: its only slide (C11, the sons) depended on unconfirmed facts. The template stays in the JSON for when those facts are confirmed.
