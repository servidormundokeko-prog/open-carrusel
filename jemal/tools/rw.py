"""Helpers for writing rewrite/cNN.json files."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STY = ["Image 1 as style reference"]
FOLLOW = "Follow @StephenJemalNY for the next chapter"
FRAMEWORK = "Framework questions written in Stephen's voice."


def cover(headline, subline, hooks, alt, scene=None, background=None, source=None, approval=None):
    s = {"n": 1, "template": "cover", "kicker": "THE JEMAL BLUEPRINT", "headline": headline, "subline": subline,
         "hookAlternatives": [{"text": t, "mechanism": m, **({"chosen": True} if i == 0 else {})} for i, (t, m) in enumerate(hooks)]}
    if scene:
        s["scene"] = scene
    if background:
        s["background"] = background
    if source:
        s["sourceLine"] = source
    if approval:
        s["needsApproval"] = True
        s["approvalNote"] = approval
    s["attachments"] = []
    s["altText"] = alt
    return s


def sl(n, template, kicker, headline, alt, approval=None, **kw):
    s = {"n": n, "template": template, "kicker": kicker, "headline": headline, **kw}
    if approval:
        s["needsApproval"] = True
        s["approvalNote"] = approval
    s["attachments"] = STY
    s["altText"] = alt
    return s


def cta(headline, rows, button, alt, approval=FRAMEWORK, **kw):
    return sl(5, "numbered_cta", "SAVE THIS", headline, alt, approval, rows=rows, button=button, followLine=FOLLOW, **kw)


def car(i, title, pillar, captions, slides, cap_note=None):
    d = {"id": i, "week": i, "title": title, "pillar": pillar, "captions": captions, "slides": slides}
    if cap_note:
        d["captionsNeedApproval"] = cap_note
    with open(os.path.join(ROOT, "rewrite", f"c{i:02d}.json"), "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
