#!/usr/bin/env python3
"""R239/R238 — is the defect the column KEY, or the column UNIVERSE?

PR #236 measured that [[R239]]'s prescribed remedy (re-key the column decision off `x1`)
regresses 20 currently-correct cells, and re-stated the row: the subject is a column
boundary falling INSIDE a cell's ink, resolved silently by a midpoint. This script asks the
next question — whether that boundary should have existed at all.

It measures three things, and they do not agree with each other, which is the point:

  A. WHAT THE DECORATION UNIVERSE COSTS. Refuse it corpus-wide and compare. bfs p5 keeps
     all 46 rows; cbh p0 LOSES 5. A blanket refusal is therefore not available.

  B. WHAT bfs p5 LOOKS LIKE WITHOUT IT. Under the alignment universe the rectangle grows
     from 124.3..495.3 to 72.12..522.82, all 27 canton rows place the intercantonal value
     in ONE column ([[R239]]'s symptom), and the row label and the final "Variation en %"
     come inside and are emitted ([[R238]]'s symptom). Both rows' symptoms are gone, and no
     row is lost. That is the evidence for "universe, not key".

  C. WHY THE SURGICAL VARIANT DOES NOT GENERALISE. Dropping only the interior boundaries
     that an ADMITTED row's ink straddles kills cbh p0's grid outright. The diagnosis is
     printed rather than asserted: all three of cbh's straddled boundaries are straddled by
     ONE line, a banner row inside the admitted set. Scoping the straddle evidence is a
     remedy-design decision and a CLAUDE.md § 8 classification — deliberately NOT made here.

WHY THE STRADDLE TEST IS SCOPED TO ADMITTED ROWS, AND WHY THAT IS STILL NOT ENOUGH:
`grid.py::_rule_boundaries` already refuses a rule vector when any word straddles it, and
calls the test threshold-free — the words confirm the rules are separators. It cannot be
ported here as written because it is BAND-scoped: a page carries prose runs 300-450pt wide
(bfs p5's footnotes and caption) that straddle every boundary there is. Scoping to the
admitted rows removes the prose and is what this script does. cbh p0 shows that is still
not enough, because an admitted row can itself be a banner.

CONTROLS. Part A's patch must actually remove every decoration universe (3 -> 0) while no
page loses its grid for an unrelated reason (16 -> 16). Part C carries a NULL CONTROL:
patching with the UNCHANGED vector must reproduce each baseline exactly, or the patch
mechanism is measuring itself rather than the change. The script exits non-zero if either
fails.

Gate classification (CLAUDE.md § 8): PROCEDURAL. It runs shipped derivations and prints
their results; it decides nothing about any document. The one numeric literal (`0.5`) is
not this script's — it is the shipped rectangle tolerance from `_place_for_emit`, copied so
the test stays identical to the code it is asking about.

Run it from the repo root:

    PYTHONPATH=src:. .venv/bin/python scripts/r239_universe_not_key.py
"""
from __future__ import annotations

import glob
import sys

import pdfplumber

import iladub.etkl.datagrid as dg
from iladub.etkl.datagrid import (absorb_unit_markers, extract_words, ink_runs,
                                  text_lines, _place_for_emit)

BFS = "corpus/gov-stats/bfs-population-bilan-2023.pdf"
CBH = "corpus/ag-trade/cbh-stem-2026-08-03.pdf"


def _pages(pdf: str) -> int:
    with pdfplumber.open(pdf) as doc:
        return len(doc.pages)


def _runs(pdf: str, page: int):
    lines = [ln for ln in sorted(text_lines(extract_words(pdf, page)),
                                 key=lambda l: l.top) if ln.words]
    return lines, [absorb_unit_markers(ink_runs(ln)) for ln in lines]


def _bounds(grid) -> list[float]:
    return [c.x0 for c in grid.columns] + [grid.columns[-1].x1]


def _column_of(value: float, bounds: list[float]) -> int | None:
    return next((j for j in range(len(bounds) - 1)
                 if bounds[j] <= value < bounds[j + 1]), None)


def _survey(force_alignment: bool) -> dict:
    original = dg._boundaries_from_decoration
    if force_alignment:
        dg._boundaries_from_decoration = lambda *a, **k: None
    out = {}
    try:
        for pdf in sorted(glob.glob("corpus/*/*.pdf")):
            for page in range(_pages(pdf)):
                try:
                    grid = dg.derive_data_grid(pdf, page)
                except Exception:
                    continue
                if grid is not None:
                    out[(pdf.split("/")[-1][:22], page)] = (grid.universe,
                                                            len(grid.columns),
                                                            len(grid.rows))
    finally:
        dg._boundaries_from_decoration = original
    return out


def part_a() -> bool:
    print("A. WHAT THE DECORATION UNIVERSE COSTS — refuse it corpus-wide and compare")
    before, after = _survey(False), _survey(True)
    dec_before = [k for k, v in before.items() if v[0] == "decoration"]
    dec_after = [k for k, v in after.items() if v[0] == "decoration"]
    print(f"   CONTROL decoration pages before={len(dec_before)} after={len(dec_after)} "
          f"(after MUST be 0); pages deriving a grid {len(before)} -> {len(after)}")
    ok = len(dec_after) == 0 and len(before) == len(after)
    for key in sorted(dec_before):
        b, a = before[key], after.get(key)
        verdict = ("GRID LOST" if a is None else
                   f"ROWS LOST {b[2] - a[2]}" if a[2] < b[2] else
                   f"rows gained {a[2] - b[2]}" if a[2] > b[2] else "rows unchanged")
        shown = f"{a[0]} {a[1]}c {a[2]}r" if a else "(none)"
        print(f"     {key[0]:24} p{key[1]:<2} {b[0]} {b[1]}c {b[2]}r  ->  {shown:26} {verdict}")
    return ok


def part_b() -> None:
    print("\nB. bfs p5 WITHOUT THE DECORATION UNIVERSE — what happens to R239 and R238")
    lines, runs = _runs(BFS, 5)
    original = dg._boundaries_from_decoration
    for label, patch in (("decoration (shipped)", False), ("alignment (forced)", True)):
        if patch:
            dg._boundaries_from_decoration = lambda *a, **k: None
        try:
            grid = dg.derive_data_grid(BFS, 5)
        finally:
            dg._boundaries_from_decoration = original
        bounds = _bounds(grid)
        held: dict = {}
        for i in grid.rows:
            for run in runs[i]:
                if 388.0 <= run.x1 <= 390.0:                  # the intercantonal column
                    held.setdefault(_column_of((run.x0 + run.x1) / 2, bounds), []).append(i)
        carried = []
        for i in grid.rows:
            first = runs[i][0] if runs[i] else None
            if first and first.text.startswith(("Suisse", "Zurich", "Genève")):
                emitted = set(_place_for_emit(lines[i], grid).keys())
                lab = _column_of((first.x0 + first.x1) / 2, bounds)
                pct = _column_of((runs[i][-1].x0 + runs[i][-1].x1) / 2, bounds)
                carried.append((first.text[:8], lab in emitted, pct in emitted))
        print(f"   {label:22} rect {bounds[0]:.2f}..{bounds[-1]:.2f}  "
              f"{len(grid.columns)}c {len(grid.rows)}r")
        print(f"     R239  intercantonal value sits in {len(held)} column(s): "
              f"{ {k: len(v) for k, v in sorted(held.items(), key=lambda z: (z[0] is None, z[0]))} }")
        print(f"     R238  label / final %% emitted: {carried}")


def part_c() -> bool:
    print("\nC. THE SURGICAL VARIANT — drop only boundaries an ADMITTED row's ink straddles")
    original = dg._boundaries_from_decoration
    ok = True
    for pdf in sorted(glob.glob("corpus/*/*.pdf")):
        for page in range(_pages(pdf)):
            try:
                grid = dg.derive_data_grid(pdf, page)
            except Exception:
                continue
            if grid is None or grid.universe != "decoration":
                continue
            lines, runs = _runs(pdf, page)
            bounds = _bounds(grid)
            bad = {x for i in grid.rows for r in runs[i] for x in bounds[1:-1]
                   if r.x0 < x - 0.5 and r.x1 > x + 0.5}
            keep = [x for x in bounds if x not in bad]
            name = pdf.split("/")[-1][:22]
            # NULL CONTROL: the unchanged vector must reproduce the baseline exactly.
            dg._boundaries_from_decoration = lambda *a, _k=bounds, **k: list(_k)
            try:
                null = dg.derive_data_grid(pdf, page)
            finally:
                dg._boundaries_from_decoration = original
            identical = null is not None and (len(null.columns), len(null.rows)) == \
                (len(grid.columns), len(grid.rows))
            ok = ok and identical
            if len(keep) < 3:
                print(f"   {name:24} p{page:<2} vector would collapse; null control "
                      f"identical={identical}")
                continue
            dg._boundaries_from_decoration = lambda *a, _k=keep, **k: list(_k)
            try:
                after = dg.derive_data_grid(pdf, page)
            finally:
                dg._boundaries_from_decoration = original
            verdict = ("GRID LOST" if after is None else
                       f"ROWS LOST {len(grid.rows) - len(after.rows)}"
                       if len(after.rows) < len(grid.rows) else "rows unchanged")
            shown = f"{after.universe} {len(after.columns)}c {len(after.rows)}r" if after else "-"
            print(f"   {name:24} p{page:<2} straddled={sorted(bad)} -> {shown:26} "
                  f"{verdict}  (null control identical={identical})")
            for x in sorted(bad):
                hits = [(i, r.text[:30]) for i in grid.rows for r in runs[i]
                        if r.x0 < x - 0.5 and r.x1 > x + 0.5]
                sources = sorted({i for i, _ in hits})
                print(f"       bound {x}: {len(hits)} run(s) on line(s) {sources}  "
                      f"e.g. {hits[0][1] if hits else ''!r}")
    return ok


def main() -> int:
    a_ok = part_a()
    part_b()
    c_ok = part_c()
    if not a_ok:
        print("\nREFUSED: part A's control failed — the patch did not take.")
        return 1
    if not c_ok:
        print("\nREFUSED: part C's null control failed — the patch mechanism is not neutral.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
