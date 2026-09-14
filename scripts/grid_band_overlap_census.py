"""The SECOND half of the ledger-contract question, which the ledger probe cannot reach.

document.py:1672-1674 withdraws only SUPERSEDED bands, then merges rep_a.graph wholesale.
A band that ASSERTED in pass 1 is never superseded — so under a widened gate, would the
grid re-read lines that an asserting band already holds? That is a graph-level double
count, independent of the ledger's arithmetic.

Measured structurally: for each population page, how many lines does the grid ADMIT that
lie inside a band whose report ASSERTED (tokens_asserted > 0)? Those are the contested
lines — read once by the band, and again by the grid.

Gate classification (CLAUDE.md §8): PROCEDURAL. It READS an existing accounting and
writes the figures down. It decides nothing about any document, changes no reading, and
carries no tolerance — every comparison it makes is exact integer arithmetic.
"""
import sys, pathlib
sys.path.insert(0, "src")   # run from the repo root
from iladub.etkl.compile import compile_tables, page_bands
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.geometry import extract_words, text_lines

POP = [("cbh-stem-2026-08-03", 0), ("graincorp-capacity-2026-08-04", 0),
       ("graincorp-stem-2026-07-31", 0), ("apple-fy2026q3-statements", 0),
       ("bfs-population-bilan-2023", 6), ("ons-index-of-services-2026-02", 4),
       ("who-wfa-boys-zscore-0-5", 0)]
pdfs = {p.stem: str(p) for p in pathlib.Path("corpus").rglob("*.pdf")}

print(f"{'document':<26}{'pg':>3}{'admitted':>10}{'contested':>11}{'ink@risk':>10}  verdict")
for stem, pg in POP:
    path = pdfs[stem]
    rep = compile_tables(path, pg, validate_shapes=False, datagrid_fallback=False)
    bands = page_bands(path, pg)
    grid = derive_data_grid(path, pg)
    if grid is None or len(rep.regions) != len(bands):
        print(f"{stem[:25]:<26}{pg:>3}  skipped")
        continue
    lines = sorted([l for l in text_lines(extract_words(path, pg)) if l.words],
                   key=lambda l: l.top)
    admitted = sorted(j for j in set(grid.rows) if 0 <= j < len(lines))
    asserting = [i for i, r in enumerate(rep.regions) if r.tokens_asserted > 0]
    contested = [j for j in admitted
                 if any(bands[i].top <= lines[j].top <= bands[i].bottom for i in asserting)]
    at_risk = sum(len(lines[j].words) for j in contested)
    v = "DOUBLE-READ under a widened gate" if contested else "disjoint — no overlap"
    print(f"{stem[:25]:<26}{pg:>3}{len(admitted):>10}{len(contested):>11}{at_risk:>10}  {v}")
