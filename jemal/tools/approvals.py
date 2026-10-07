#!/usr/bin/env python3
"""Regenerate section C of APPROVAL_CHECKLIST.md from the needsApproval flags in rewrite/*.json."""
import glob, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ("headline", "pullLine", "body")
# Carousels the client approved as a whole (date in the heading).
APPROVED = {i: "Oct 7" for i in (*range(1, 23), 35)}

def quote(s):
    bits = [s[f] for f in FIELDS if isinstance(s.get(f), str)]
    for k in ("rows", "points", "checklist"):
        if s.get(k):
            v = s[k]
            bits.append(" / ".join(" → ".join(x) if isinstance(x, list) else x for x in v))
    for cd in s.get("cards") or []:
        if isinstance(cd, dict) and cd.get("body"):
            bits.append(cd["body"])
        elif isinstance(cd, list):
            bits.append(" → ".join(cd))
    if s.get("flow"):
        bits.append(" → ".join(x[0] for x in s["flow"]))
    return "; ".join(f'"{b}"' for b in bits)

out = ["## C. First-person lines that put words or opinions in Stephen's mouth", "",
       "Generated from `needsApproval: true` in `rewrite/*.json` by `tools/approvals.py`. Facts on these slides are confirmed; the flagged part is the opinion, framework or framing.", ""]
for p in sorted(glob.glob(os.path.join(ROOT, "rewrite", "c*.json"))):
    c = json.load(open(p))
    items = [s for s in c["slides"] if s.get("needsApproval")]
    if not items and not c.get("captionsNeedApproval"):
        continue
    box = "[x]" if c["id"] in APPROVED else "[ ]"
    out.append(f"### Carousel {c['id']}: {c['title']}" + (f" (approved {APPROVED[c['id']]})" if c["id"] in APPROVED else ""))
    for s in items:
        out.append(f"- {box} Slide {s['n']} ({s['template']}): {s.get('approvalNote','')} {quote(s)}")
    if c.get("captionsNeedApproval"):
        out.append(f"- {box} Captions: {c['captionsNeedApproval']}")
    out.append("")
path = os.path.join(ROOT, "APPROVAL_CHECKLIST.md")
doc = open(path).read()
doc = re.sub(r"## C\. .*?(?=\n## D\. )", "\n".join(out).rstrip() + "\n", doc, flags=re.S)
open(path, "w").write(doc)
print("approval items:", sum(1 for l in out if l.startswith("- [ ]")), "open")
