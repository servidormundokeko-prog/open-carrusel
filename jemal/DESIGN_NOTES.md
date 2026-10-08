# Design notes

Palette and fonts are unchanged: navy #0B1F3A, card navy #12294A, gold #D4A84B, white, muted #9AA5B1, Montserrat headlines, Inter body.

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

Checked by `validate.py`: white on navy 16.5, white on card 14.6, muted on navy 6.6, muted on card 5.8, gold on navy 7.5, gold on card 6.6, navy on gold button 7.5. All pass.

## Batch 1 fixes

- **New `row` illustration in the studio.** The original data used scene `row` on 7 slides, but the studio had no drawing for it, so those banners were blank. The Flow prompt description is unchanged.
- **`stats_rows` labels widen to fit.** Long labels such as "ADVERTISING" overlapped the text. They now take 250-440px, and the auto-fit shrinks the slide if a label still doesn't fit.
- **C11 slide 2 uses one illustration.** It had both a banner and a top illustration stacked.

## No new templates

None needed so far. `row` was an existing scene name that lacked a drawing.

## Template use across the series

Every carousel opens with `cover` and closes with `numbered_cta`. Slides 2-4 use three different templates in all 52 carousels. Counts across slides 2-4: flow_steps 44, cards_stack 37, table_compare 32, stats_grid 21, stats_rows 12, stats_cards 5, timeline_vertical 4, stat_flow_checklist 1. `name_cards_grid` is no longer used: its only slide (C11, the sons) depended on unconfirmed facts. The template stays in the JSON for when those facts are confirmed.
