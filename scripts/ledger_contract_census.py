"""Exact decomposition. The previous pass over-counted both terms by including ADMITTED
lines (which the grid books) and by putting a band that both asserts and escalates into
two buckets at once.

The identity: asserted_tokens is exactly the ink on admitted lines, so

    lost = (ink on UNADMITTED lines) - escalated_tokens

Split the unadmitted lines by the booking class of the band containing them, which is what
build_ledger itself selects on:

    prose      band booked nothing            -> dropped BY DESIGN
    escalating band booked escalated tokens   -> accounted (residue / untouched)
    ASSERT-ONLY band asserted, escalated 0    -> THE PREMISE BREAK: booked by no one

Gate classification (CLAUDE.md §8): PROCEDURAL. It READS an existing accounting and
writes the figures down. It decides nothing about any document, changes no reading, and
carries no tolerance — every comparison it makes is exact integer arithmetic.
"""
import sys, pathlib
sys.path.insert(0, "src")   # run from the repo root
import pdfplumber
from iladub.etkl.compile import compile_tables, page_bands
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.adoption import build_ledger

print(f"{'document':<26}{'pg':>3}{'kind':>18}{'lost':>6}{'prose':>7}{'escal':>7}{'ASSERT-ONLY':>12}{'outside':>8}")
ctl_bad = pop_bad = 0
for pdf in sorted(pathlib.Path("corpus").rglob("*.pdf")):
    with pdfplumber.open(str(pdf)) as d:
        npages = len(d.pages)
    for pg in range(npages):
        try:
            rep = compile_tables(str(pdf), pg, validate_shapes=False, datagrid_fallback=False)
            bands = page_bands(str(pdf), pg)
            grid = derive_data_grid(str(pdf), pg)
        except Exception:
            continue
        if grid is None or len(rep.regions) != len(bands):
            continue
        lines = sorted([l for l in text_lines(extract_words(str(pdf), pg)) if l.words],
                       key=lambda l: l.top)
        led = build_ledger(lines, grid.rows, bands, rep.regions)
        adm = set(j for j in set(grid.rows) if 0 <= j < len(lines))
        lost = sum(len(l.words) for l in lines) - (led.asserted_tokens + led.escalated_tokens)
        buckets = {"prose": 0, "escal": 0, "assert_only": 0, "outside": 0}
        for j, ln in enumerate(lines):
            if j in adm:
                continue
            owner = next((i for i in range(len(bands))
                          if bands[i].top <= ln.top <= bands[i].bottom), None)
            if owner is None:
                buckets["outside"] += len(ln.words); continue
            r = rep.regions[owner]
            if r.tokens_escalated > 0:      buckets["escal"] += len(ln.words)
            elif r.tokens_asserted > 0:     buckets["assert_only"] += len(ln.words)
            else:                           buckets["prose"] += len(ln.words)
        kind = "CONTROL(adopting)" if rep.asserted == 0 and rep.escalated > 0 else \
               ("population" if rep.asserted > 0 else "neither")
        if buckets["assert_only"]:
            if kind == "CONTROL(adopting)": ctl_bad += 1
            elif kind == "population":      pop_bad += 1
        if lost or kind == "CONTROL(adopting)":
            print(f"{pdf.stem[:25]:<26}{pg:>3}{kind:>18}{lost:>6}{buckets['prose']:>7}"
                  f"{buckets['escal']:>7}{buckets['assert_only']:>12}{buckets['outside']:>8}")
print(f"\ncontrol pages with ASSERT-ONLY ink dropped:    {ctl_bad}")
print(f"population pages with ASSERT-ONLY ink dropped: {pop_bad}")
