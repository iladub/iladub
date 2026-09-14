"""R225 arm B probe: does the drawn rule set under-resolve the band's own word structure?

Compares, at the EXACT call site compile.py:133 gates (`len(xs) >= 2`):
  drawn_cols = len(xs) - 1          (what the author's marks resolve to)
  word_cols  = infer_leaf_grid(Band(lines only, NO rules)).ncols   (gutter path)
Stripping rules is required: infer_leaf_grid short-circuits on _rule_boundaries,
which would otherwise measure the drawn marks against themselves.

Gate classification (CLAUDE.md §8): PROCEDURAL. It READS band construction and writes
the counts down. It decides nothing about any document, changes no reading, and carries
no tolerance — the only comparison it makes is ordinal.
"""
import sys, pathlib
sys.path.insert(0, "src")
import pdfplumber
from iladub.etkl import compile as C
from iladub.etkl.bands import Band
from iladub.etkl.grid import infer_leaf_grid, _rule_boundaries

recs = []
orig = C._build_ruled_band

def wrapper(sub, sub_rules, sub_hrules, page_chars, section_repair=False):
    xs = sorted({round(r.x, 2) for r in sub_rules})
    drawn = max(0, len(xs) - 1)
    wordband = Band(tuple(sub.lines), sub.top, sub.bottom)   # no rules -> gutter path
    try:
        word = infer_leaf_grid(wordband).ncols
    except ValueError:
        word = None
    recs.append({"doc": CUR[0], "page": CUR[1], "drawn": drawn, "word": word,
                 "sep": _rule_boundaries(sub) is not None, "lines": len(sub.lines)})
    return orig(sub, sub_rules, sub_hrules, page_chars, section_repair)

C._build_ruled_band = wrapper
CUR = [None, None]

targets = sorted(pathlib.Path("corpus").rglob("*.pdf"))

for pdf in targets:
    with pdfplumber.open(str(pdf)) as d:
        npages = len(d.pages)
    for p in range(npages):
        CUR[0], CUR[1] = pdf.stem[:22], p
        try:
            C.page_bands(str(pdf), p)
        except Exception as e:
            print(f"  !! {pdf.stem} p{p}: {type(e).__name__}: {e}")

print(f"\n{'doc':<24}{'pg':>3}{'drawn':>7}{'word':>6}{'sep':>6}{'lines':>6}   VERDICT")
fires = under = 0
for r in recs:
    if r["word"] is None:
        continue
    underres = r["drawn"] < r["word"]
    if underres:
        under += 1
    if r["drawn"] == 1:
        fires += 1
    if underres or r["drawn"] <= 1:
        v = "UNDER-RESOLVED -> refuse re-bucket" if underres else "ok"
        print(f"{r['doc']:<24}{r['page']:>3}{r['drawn']:>7}{r['word']:>6}"
              f"{str(r['sep']):>6}{r['lines']:>6}   {v}")
print(f"\ntotal _build_ruled_band calls: {len(recs)}")
print(f"border-only (drawn == 1):      {fires}")
print(f"under-resolved (drawn < word): {under}   <- what arm B's test would refuse")

print("\n=== PER-DOCUMENT ===")
from collections import defaultdict
agg = defaultdict(lambda: [0, 0, 0])   # calls, border-only, under-resolved
for r in recs:
    a = agg[r["doc"]]
    a[0] += 1
    if r["drawn"] == 1:
        a[1] += 1
    if r["word"] is not None and r["drawn"] < r["word"]:
        a[2] += 1
print(f"{'document':<26}{'calls':>7}{'border1':>9}{'under':>7}")
for d in sorted(agg):
    a = agg[d]
    print(f"{d:<26}{a[0]:>7}{a[1]:>9}{a[2]:>7}")
