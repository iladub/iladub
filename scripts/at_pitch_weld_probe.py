"""Every wrap-continuation candidate on one band, with its gap and the band's `lead` at full
float precision — the instrument behind [[R208]]'s located cause.

`cells.group_wrapped` absorbs line j into the line above iff the three structural conditions
hold (subset of open columns, fewer columns than the anchor, no author hrule between) AND
`gap < lead`, where `lead` is the median inter-line gap. On a table whose row pitch is uniform
(graincorp-stem p1: every body gap is 6.48 pt), every candidate's gap EQUALS the median up to
the coordinate noise the PDF's text matrices carry (~2e-5 pt), so the strict `<` is decided by
that noise: measured 2026-09-10, 3 of the 7 candidates on p1 band 1 fall under the median and
weld (`Mackay Mackay Mackay`), 4 fall over it and stay rows. `tests/etkl/test_wrap_continuation.py::
test_at_pitch_partial_line_not_merged` states the intended reading (at pitch is NOT a wrap) and
passes only because its fixture has exact integer coordinates.

Run from the repo root, corpus populated:

    PYTHONPATH=src .venv/bin/python scripts/at_pitch_weld_probe.py corpus/ag-trade/graincorp-stem-2026-07-31.pdf 1 1

Gate classification (CLAUDE.md §8): PROCEDURAL. It reads the page exactly as `group_wrapped`
does and prints what that function compares; it decides nothing and carries no tolerance.
"""
from __future__ import annotations

import sys
from statistics import median

from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import column_of


def main(pdf: str, page: int, band_idx: int) -> None:
    band = page_bands(pdf, page)[band_idx]
    grid = recover_leaf_grid(band)
    tops = [ln.top for ln in band.lines]
    gaps = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    lead = median([g for g in gaps if g > 0]) if any(g > 0 for g in gaps) else 0.0
    hrule_ys = sorted({round(h.y, 2) for h in band.hrules})
    print(f"band {band_idx} on page {page}: {len(band.lines)} lines, {grid.ncols} columns, "
          f"{len(hrule_ys)} hrule ys, lead={lead!r}")
    cols = [sorted({column_of((w.x0 + w.x1) / 2.0, grid.boundaries) for w in ln.words})
            for ln in band.lines]
    n_cand = n_weld = 0
    for i in range(1, len(band.lines)):
        prev, cur = cols[i - 1], cols[i]
        structural = bool(cur) and set(cur) <= set(prev) and len(cur) < len(prev)
        vetoed = any(tops[i - 1] < y <= tops[i] for y in hrule_ys)
        if not structural or vetoed:
            continue
        gap = tops[i] - tops[i - 1]
        welds = gap < lead
        n_cand += 1
        n_weld += welds
        text = " ".join(w.text for w in band.lines[i].words)[:48]
        print(f"  line {i - 1}->{i}: gap={gap!r} gap-lead={gap - lead:+.2e} "
              f"{'WELDS' if welds else 'row  '}  cols {len(prev)}->{len(cur)}  {text}")
    print(f"candidates {n_cand}, welded by gap<lead {n_weld}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
