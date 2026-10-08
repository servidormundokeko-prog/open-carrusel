"""Per-pillar palettes for the @StephenJemalNY series. Shared by build.py and validate.py.

Text roles: white and `muted` sit on `bg` and `card`; `accent` (kickers, titles, numbers) and
`accent2` (sublines, pull lines) sit on `bg` and `card`; `bg` is the text colour on `accent`
buttons and number circles. Every pair is checked against WCAG AA (4.5:1) by validate.py.
`words` feed the Google Flow prompts.
"""

PALETTES = {
    "story": {"name": "Story", "bg": "#24120B", "card": "#3A1D12", "accent": "#F6A93B", "accent2": "#EE8A63",
              "muted": "#C4AEA3", "icon": "book-open",
              "words": {"bg": "deep espresso brown", "card": "dark brown", "accent": "amber", "accent2": "terracotta"}},
    "founder": {"name": "Founder lessons", "bg": "#0B1F3A", "card": "#12294A", "accent": "#D4A84B", "accent2": "#F0CF85",
                "muted": "#9AA5B1", "icon": "lightbulb",
                "words": {"bg": "deep navy", "card": "dark navy", "accent": "gold", "accent2": "warm gold"}},
    "scaling": {"name": "Scaling and systems", "bg": "#04262A", "card": "#0A3A3F", "accent": "#6EF0D6", "accent2": "#2CC9B5",
                "muted": "#9CC2BE", "icon": "settings",
                "words": {"bg": "deep teal-black", "card": "dark teal", "accent": "mint", "accent2": "teal"}},
    "built": {"name": "BUILT technology", "bg": "#0F0A28", "card": "#1C1544", "accent": "#2EE6FF", "accent2": "#B69CFF",
              "muted": "#AAA4CC", "icon": "cpu",
              "words": {"bg": "deep indigo-black", "card": "dark indigo", "accent": "electric cyan", "accent2": "violet"}},
    "housing": {"name": "Housing and authority", "bg": "#2A0E16", "card": "#401925", "accent": "#FF8A6B", "accent2": "#FFBE5C",
                "muted": "#D3B1B4", "icon": "house",
                "words": {"bg": "deep plum-red", "card": "dark plum", "accent": "coral", "accent2": "sunrise orange"}},
    "realestate": {"name": "Real estate and vision", "bg": "#05231A", "card": "#0B3527", "accent": "#B5F04A", "accent2": "#3FDDA0",
                   "muted": "#A2C5B6", "icon": "building-2",
                   "words": {"bg": "deep forest green", "card": "dark green", "accent": "lime", "accent2": "emerald"}},
}


def palette_for(pillar):
    p = (pillar or "").lower()
    if p.startswith("story"):
        return "story"
    if p.startswith("founder"):
        return "founder"
    if p.startswith("scaling"):
        return "scaling"
    if p.startswith("built"):
        return "built"
    if "housing" in p or "authority" in p:
        return "housing"
    if p.startswith("real estate"):
        return "realestate"
    raise ValueError(f"no palette for pillar {pillar!r}")


def _lum(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def text_pairs(p):
    """(foreground, background, label) for every text colour on every surface it is used on."""
    out = []
    for surf in ("bg", "card"):
        for fg in ("#FFFFFF", "muted", "accent", "accent2"):
            out.append((p.get(fg, fg), p[surf], f"{'white' if fg.startswith('#') else fg} on {surf}"))
    out += [(p["bg"], p["accent"], "bg on accent (button, number circles)"), (p["bg"], p["accent2"], "bg on accent2 (progress chip)")]
    return out
