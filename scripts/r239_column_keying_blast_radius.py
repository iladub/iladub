#!/usr/bin/env python3
"""R239 — the blast radius of re-keying the data grid's column assignment.

[[R239]] as raised says: *"Column assignment for a right-aligned numeric column is keyed on
`x0`, so a 0.04 pt difference decides it."* **The first half is measured FALSE.** Every
placement site in the shipped data-grid path keys on the run's CENTRE, never on `x0`:

    datagrid.py  place()            centre = (r.x0 + r.x1) / 2
    datagrid.py  place_indexed()    centre = (r.x0 + r.x1) / 2
    datagrid.py  _place_for_emit()  centre = (r.x0 + r.x1) / 2

The row's coordinates were read off the EMITTED cell bbox (`emit_data_grid` writes `tab:x0`
from `r.x0`, the cell's own ink extent) and the key was inferred from them. The second half
survives and sharpens: for a right-aligned numeric, `x1` is fixed and `x0` moves ~12pt with
digit count, so the centre still moves ~6pt — the wrong edge, half as wrong.

The maintainer's ruling asks one question before anything is built:

    across the corpus, how many columns are right-aligned numerics, and does keying on span
    or x1 rather than x0 change any assignment that is currently CORRECT? If it regresses
    even one, the remedy is a different class.

This script answers it. It decides nothing about any document: it prints what moves, and
leaves repair-vs-regression to the reader, in prose.

THE CONTROL, AND WHY THE OBVIOUS ONE IS INERT
---------------------------------------------
To vary the key, this script re-implements the keying inline rather than calling the shipped
`_place_for_emit`. That is the wrong-seam hazard this repo has recorded twice, so the
re-implementation has to be shown to BE the shipped one before any number here is
load-bearing. Comparing the two under the CENTRE key agrees on every admitted line — and on
its own that proves nothing, because both sides evaluate the same expression.

**The null control is what makes the comparison discriminate**: run the SAME comparison with
a deliberately wrong key. `x0` and `x1` must DISAGREE. If a wrong key agrees just as well,
the comparison is inert and the centre agreement is not evidence of anything. This script
EXITS NON-ZERO when that happens, and when the centre key itself fails to agree.

Gate classification (CLAUDE.md §8): PROCEDURAL. It runs shipped derivations and prints their
results. It carries no tuned constant and makes no reading judgement of its own. The one
numeric literal below (`0.5`) is not this script's: it is copied from the shipped
`_place_for_emit` rectangle test so that the re-implementation stays identical to it.

Run it from the repo root:

    PYTHONPATH=src:. .venv/bin/python scripts/r239_column_keying_blast_radius.py
"""
from __future__ import annotations

import glob
import sys

import pdfplumber

from iladub.etkl.datagrid import (absorb_unit_markers, derive_data_grid, extract_words,
                                  ink_runs, text_lines, _place_for_emit)


def _pages(pdf: str) -> int:
    with pdfplumber.open(pdf) as doc:
        return len(doc.pages)


def _grids():
    """Every (pdf, page, grid, bounds, lines) the shipped derivation admits."""
    for pdf in sorted(glob.glob("corpus/*/*.pdf")):
        for page in range(_pages(pdf)):
            try:
                grid = derive_data_grid(pdf, page)
            except Exception as exc:                      # a page that cannot derive is not
                print(f"  !! {pdf} p{page}: {type(exc).__name__}")   # this script's subject
                continue
            if grid is None:
                continue
            bounds = [c.x0 for c in grid.columns] + [grid.columns[-1].x1]
            lines = [ln for ln in sorted(text_lines(extract_words(pdf, page)),
                                         key=lambda l: l.top) if ln.words]
            yield pdf, page, grid, bounds, lines


def _key(value: float, bounds: list[float]) -> int | None:
    return next((j for j in range(len(bounds) - 1)
                 if bounds[j] <= value < bounds[j + 1]), None)


def _edge(run, which: str, bounds: list[float]) -> float:
    if which == "centre":
        return (run.x0 + run.x1) / 2
    if which == "x0":
        return run.x0
    return min(run.x1 - 0.01, bounds[-1] - 0.01)          # x1, held inside the rectangle


def _inside(run, bounds: list[float]) -> bool:
    """The shipped rectangle test, copied verbatim from `_place_for_emit`."""
    return not (run.x1 <= bounds[0] - 0.5 or run.x0 >= bounds[-1] + 0.5)


def control(which: str) -> tuple[int, int]:
    """Lines on which this file's keying reproduces the shipped emitter's column set."""
    agree = disagree = 0
    for _pdf, _page, grid, bounds, lines in _grids():
        for i in grid.rows:
            mine = set()
            for run in absorb_unit_markers(ink_runs(lines[i])):
                if not _inside(run, bounds):
                    continue
                k = _key(_edge(run, which, bounds), bounds)
                if k is not None:
                    mine.add(k)
            if mine == set(_place_for_emit(lines[i], grid).keys()):
                agree += 1
            else:
                disagree += 1
    return agree, disagree


def alignment_class(runs) -> str:
    """Which edge of this column's own cells is the STEADY one.

    A column whose cells share an x1 to within a fraction of a point while their x0 spreads
    with digit count is right-aligned, and its x0 carries no column information; a column
    whose x0 is steady is left-aligned, and the mirror holds for its x1. Reported for both,
    because the remedy proposed for one is the defect for the other.
    """
    s0 = max(r.x0 for r in runs) - min(r.x0 for r in runs)
    s1 = max(r.x1 for r in runs) - min(r.x1 for r in runs)
    if s1 < s0 - 0.5:
        return "RIGHT"
    if s0 < s1 - 0.5:
        return "LEFT"
    return "neither"


def sweep() -> int:
    """Print every cell an x1 re-key would MOVE, with its source column's alignment."""
    print(f"\n{'doc':22} {'pg':>2} {'kc':>3} {'k1':>3} {'class(kc)':>10} {'n':>4} "
          f"{'sprd_x0':>8} {'sprd_x1':>8}  example")
    totals: dict[str, int] = {}
    cells = straddle = moved = 0
    for pdf, page, grid, bounds, lines in _grids():
        by_col: dict[int, list] = {}
        moves: dict[tuple[int, int | None], list] = {}
        for i in grid.rows:
            for run in absorb_unit_markers(ink_runs(lines[i])):
                if not _inside(run, bounds):
                    continue
                kc = _key(_edge(run, "centre", bounds), bounds)
                if kc is None:
                    continue
                cells += 1
                by_col.setdefault(kc, []).append(run)
                if not (bounds[kc] <= run.x0 and run.x1 <= bounds[kc + 1]):
                    straddle += 1          # the cell's ink crosses its own column boundary
                k1 = _key(_edge(run, "x1", bounds), bounds)
                if k1 != kc:
                    moved += 1
                    moves.setdefault((kc, k1), []).append(run)
        for (kc, k1), runs in sorted(moves.items()):
            col = by_col[kc]
            cls = alignment_class(col)
            totals[cls] = totals.get(cls, 0) + len(runs)
            s0 = max(r.x0 for r in col) - min(r.x0 for r in col)
            s1 = max(r.x1 for r in col) - min(r.x1 for r in col)
            print(f"{pdf.split('/')[-1][:22]:22} {page:>2} {kc:>3} {str(k1):>3} {cls:>10} "
                  f"{len(runs):>4} {s0:>8.2f} {s1:>8.2f}  {runs[0].text[:28]}")
    print(f"\ncells={cells}  straddling their own column boundary={straddle}  "
          f"moved by an x1 re-key={moved}")
    print(f"moved cells by SOURCE-column alignment class: {totals}")
    return totals.get("LEFT", 0)


def main() -> int:
    print("CONTROL — does this file's keying reproduce the shipped `_place_for_emit`?")
    print("  (the centre row alone is INERT; the wrong keys are what make it discriminate)")
    results = {}
    for which in ("centre", "x0", "x1"):
        agree, disagree = control(which)
        results[which] = disagree
        print(f"    key={which:<7} lines agreeing={agree:<5} disagreeing={disagree}")
    if results["centre"] != 0:
        print("REFUSED: this file's centre keying is NOT the shipped one.")
        return 1
    if results["x0"] == 0 or results["x1"] == 0:
        print("REFUSED: a deliberately wrong key agreed too — the control is inert.")
        return 1
    regressions = sweep()
    print(f"\nx1 re-key would move {regressions} cells out of a LEFT-aligned column, "
          f"where x1 is the noisy edge — the mirror of the defect R239 names.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
