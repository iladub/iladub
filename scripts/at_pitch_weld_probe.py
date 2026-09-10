"""Every wrap-continuation candidate on one band, with its gap, the band's `lead` and its
`tightest_row_gap` at full float precision, and BOTH verdicts — the instrument behind
[[R208]]'s located cause and the spec that closes it
(`docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md` § 7).

`cells.group_wrapped` absorbs line j into the line above iff the three structural conditions
hold (subset of open columns, fewer columns than the anchor, no author hrule between) AND the
gap is tighter than the band's threshold. Under B3 that threshold was `lead`, the median
inter-line gap: on a table whose row pitch is uniform (graincorp-stem p1: every body gap is
6.48 pt) every candidate's gap EQUALS the median up to the coordinate noise the PDF's text
matrices carry (~2e-5 pt), so the strict `<` was decided by that noise — measured 2026-09-10,
3 of the 7 candidates on p1 band 1 fell under the median and welded (`Mackay Mackay Mackay`),
4 fell over it and stayed rows. The threshold is now `tightest_row_gap`, the minimum gap over
the band's CERTAIN pairs (consecutive lines that fail the structural test or are hrule-vetoed:
row boundaries by construction), falling back to `lead` when the band certifies nothing.

Run from the repo root, corpus populated:

    PYTHONPATH=src .venv/bin/python scripts/at_pitch_weld_probe.py corpus/ag-trade/graincorp-stem-2026-07-31.pdf 1 1

prints, per candidate, `gap<lead` and `gap<tightest` side by side, and the band's certain-pair
count and threshold in the header.

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
    cols = [sorted({column_of((w.x0 + w.x1) / 2.0, grid.boundaries) for w in ln.words})
            for ln in band.lines]
    # The same enumeration group_wrapped makes: a raw consecutive pair is CERTAIN (a row
    # boundary by construction) iff it fails the structural test or an hrule separates it.
    verdicts = []
    certain_gaps = []
    for i in range(1, len(band.lines)):
        prev, cur = cols[i - 1], cols[i]
        structural = bool(cur) and set(cur) <= set(prev) and len(cur) < len(prev)
        vetoed = any(tops[i - 1] < y <= tops[i] for y in hrule_ys)
        gap = tops[i] - tops[i - 1]
        if not structural or vetoed:
            certain_gaps.append(gap)
        else:
            verdicts.append((i, gap))
    tightest = min(certain_gaps) if certain_gaps else None
    threshold = tightest if tightest is not None else lead
    print(f"band {band_idx} on page {page}: {len(band.lines)} lines, {grid.ncols} columns, "
          f"{len(hrule_ys)} hrule ys, lead={lead!r}, certain pairs={len(certain_gaps)}, "
          f"tightest_row_gap={tightest!r}{' (fallback to lead)' if tightest is None else ''}")
    n_weld_lead = n_weld_tight = 0
    for i, gap in verdicts:
        by_lead, by_tight = gap < lead, gap < threshold
        n_weld_lead += by_lead
        n_weld_tight += by_tight
        text = " ".join(w.text for w in band.lines[i].words)[:48]
        print(f"  line {i - 1}->{i}: gap={gap!r} gap-lead={gap - lead:+.2e} "
              f"gap-tightest={gap - threshold:+.2e}  "
              f"gap<lead:{'WELD' if by_lead else 'row '}  gap<tightest:{'WELD' if by_tight else 'row '}"
              f"  cols {len(cols[i - 1])}->{len(cols[i])}  {text}")
    print(f"candidates {len(verdicts)}, welded by gap<lead {n_weld_lead}, "
          f"welded by gap<tightest_row_gap {n_weld_tight}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
