#!/usr/bin/env python3
"""R239 § 5d — is the straddle discriminator a UNIVERSAL QUANTIFIER, or does it need a count?

The 2026-09-16 handoff (`2026-09-16-r239-universe-not-key-handoff.md` § 5d) left one
PROPOSED claim and named its own falsifier. The contrast it rests on is real and measured:

    bfs p5   boundaries 156.9, 302.0, 381.8, 420.1, 479.7  straddled by 27, 19, 14, 19, 3 rows
    cbh p0   boundaries  76.0, 154.5, 608.7                straddled by  1 line, all three

A rule of the form "more than n rows straddle it" is the tuned constant CLAUDE.md § 8
forbids — the defect being repaired is itself a boundary decided by 0.04 pt. The handoff
named the only constant-free form available and the measurement that settles it:

    "on bfs's five boundaries, does EVERY admitted row carrying a cell in the affected
     column straddle, while cbh's banner is the ONLY line touching its three?"

That is what this script measures. If it holds, the rule is a universal quantifier and
needs no constant. If it fails, the § 5d remedy shape is dead and no § 8 classification is
owed on it.

WHAT "THE AFFECTED COLUMN" MEANS, AND WHY BOTH READINGS ARE REPORTED. An interior boundary
x separates two columns, and the handoff's phrase does not say which one is "affected".
That is a free parameter, and choosing the reading after seeing the numbers is how a
refuted claim gets rescued. So BOTH are measured and BOTH are printed, side by side,
before any verdict: EITHER (a row carrying a cell in either adjacent column) and BOTH (a
row carrying a cell in both). A rule that holds under one reading and not the other is not
a rule; it is a choice, and the print makes that visible instead of hiding it.

DEFINITIONS, taken from the shipped code rather than invented here:
  - admitted rows      `grid.rows` from `derive_data_grid`
  - a run STRADDLES x  `r.x0 < x - 0.5 and r.x1 > x + 0.5` — the same test the PR #237
                       instrument used, so the straddle counts are comparable
  - a run CARRIES col k  its CENTRE falls in `[bounds[k], bounds[k+1])` — `place`'s own
                       test (`datagrid.py:369-370`), not a re-invention
The `0.5` is the shipped rectangle tolerance from `_place_for_emit`, copied so the test
stays identical to the code it asks about. No other constant appears.

CONTROL. The straddle counts must reproduce PR #237's exactly (bfs 27/19/14/19/3, cbh
1/1/1). A different number means this script is measuring a different thing and its verdict
is void.

NULL CONTROL. The same universal test is run on every interior boundary that is NOT
straddled at all. Such a boundary has carriers and zero straddlers, so the universal MUST
come out false on every one of them. A test that says "drop it" there is not a rule, it is
a bug — and this is the direction a silently-inverted quantifier would fail in.

Gate classification (CLAUDE.md § 8): PROCEDURAL. It runs shipped derivations and prints
their results; it decides nothing about any document and repairs nothing.

Run it from the repo root:

    PYTHONPATH=src:. .venv/bin/python scripts/r239_straddle_universal.py
"""
from __future__ import annotations

import glob
import sys

import pdfplumber

import iladub.etkl.datagrid as dg
from iladub.etkl.datagrid import absorb_unit_markers, extract_words, ink_runs, text_lines

TOL = 0.5                      # the shipped rectangle tolerance, not this script's

# PR #237's measured straddle counts, as the control. Keyed by (document prefix, page).
EXPECTED_STRADDLE = {
    ("bfs-population-bilan-2", 5): {156.9: 27, 302.0: 19, 381.8: 14, 420.1: 19, 479.7: 3},
    ("cbh-stem-2026-08-03.pd", 0): {76.0: 1, 154.5: 1, 608.7: 1},
}


def _pages(pdf: str) -> int:
    with pdfplumber.open(pdf) as doc:
        return len(doc.pages)


def _runs(pdf: str, page: int):
    lines = [ln for ln in sorted(text_lines(extract_words(pdf, page)),
                                 key=lambda l: l.top) if ln.words]
    return lines, [absorb_unit_markers(ink_runs(ln)) for ln in lines]


def _bounds(grid) -> list[float]:
    return [c.x0 for c in grid.columns] + [grid.columns[-1].x1]


def _carries(run, k: int, bounds: list[float]) -> bool:
    """Does this run place a cell in column k? `place`'s own centre test."""
    centre = (run.x0 + run.x1) / 2
    return bounds[k] <= centre < bounds[k + 1]


def _straddles(run, x: float) -> bool:
    return run.x0 < x - TOL and run.x1 > x + TOL


def survey(pdf: str, page: int) -> list[dict]:
    """One record per interior boundary of this page's grid."""
    grid = dg.derive_data_grid(pdf, page)
    if grid is None:
        return []
    _, runs = _runs(pdf, page)
    bounds = _bounds(grid)
    out = []
    for j in range(1, len(bounds) - 1):            # interior boundaries only
        x = bounds[j]
        left, right = j - 1, j                     # the two columns x separates
        straddlers, either, both = set(), set(), set()
        for i in grid.rows:
            rs = runs[i]
            if any(_straddles(r, x) for r in rs):
                straddlers.add(i)
            l_hit = any(_carries(r, left, bounds) for r in rs)
            r_hit = any(_carries(r, right, bounds) for r in rs)
            if l_hit or r_hit:
                either.add(i)
            if l_hit and r_hit:
                both.add(i)
        out.append({
            "x": x, "cols": (left, right),
            "straddlers": straddlers, "either": either, "both": both,
            # the universal quantifier, in each reading of "the affected column"
            "univ_either": bool(either) and either <= straddlers,
            "univ_both": bool(both) and both <= straddlers,
            # THE VACUOUS VARIANT, reported because the numbers surfaced it and hiding it
            # would be choosing the reading after seeing the result. Dropping the
            # non-emptiness guard makes the BOTH form true wherever no admitted row
            # carries cells in both adjacent columns — which is no longer a straddle rule
            # at all. Printed with its drops so its cost is visible, NOT proposed.
            "univ_both_vacuous": both <= straddlers,
        })
    return out


def main() -> int:
    print("R239 § 5d — does the straddle discriminator hold as a UNIVERSAL quantifier?\n")
    control_ok, null_ok, null_seen = True, True, 0
    verdicts: dict = {}

    for pdf in sorted(glob.glob("corpus/*/*.pdf")):
        for page in range(_pages(pdf)):
            try:
                grid = dg.derive_data_grid(pdf, page)
            except Exception:
                continue
            if grid is None or grid.universe != "decoration":
                continue
            name = pdf.split("/")[-1][:22]
            rows = survey(pdf, page)
            print(f"{name} p{page}  {len(grid.columns)}c {len(grid.rows)}r  "
                  f"{len(rows)} interior boundaries")
            print(f"    {'bound':>9} {'cols':>7} {'strad':>6} {'either':>7} {'both':>5} "
                  f"{'UNIV(either)':>13} {'UNIV(both)':>11} {'UNIV(vacuous)':>14}")
            dropped_either, dropped_both, dropped_vac = [], [], []
            for rec in rows:
                s, e, b = len(rec["straddlers"]), len(rec["either"]), len(rec["both"])
                print(f"    {rec['x']:>9.2f} {str(rec['cols']):>7} {s:>6} {e:>7} {b:>5} "
                      f"{str(rec['univ_either']):>13} {str(rec['univ_both']):>11} "
                      f"{str(rec['univ_both_vacuous']):>14}")
                if rec["univ_either"]:
                    dropped_either.append(rec["x"])
                if rec["univ_both"]:
                    dropped_both.append(rec["x"])
                if rec["univ_both_vacuous"]:
                    dropped_vac.append(rec["x"])
                # NULL CONTROL: a boundary nothing straddles must never satisfy either
                # universal — it has carriers and zero straddlers.
                if s == 0:
                    null_seen += 1
                    if rec["univ_either"] or rec["univ_both"]:
                        null_ok = False
                        print("        NULL CONTROL FAILED: unstraddled boundary "
                              "satisfies a universal")
            verdicts[(name, page)] = (dropped_either, dropped_both, dropped_vac)

            # CONTROL: reproduce PR #237's straddle counts on the two recorded pages.
            want = EXPECTED_STRADDLE.get((name, page))
            if want is not None:
                got = {round(r["x"], 1): len(r["straddlers"])
                       for r in rows if len(r["straddlers"]) > 0}
                match = got == want
                control_ok = control_ok and match
                print(f"    CONTROL straddle counts vs PR #237: {got} "
                      f"expected {want} -> {'MATCH' if match else 'DIFFER'}")
            print()

    print("WHAT THE UNIVERSAL RULE WOULD DROP")
    target = {"bfs-population-bilan-2": [156.9, 302.0, 381.8, 420.1, 479.7]}
    for key in sorted(verdicts):
        de, db, dv = verdicts[key]
        print(f"    {key[0]:24} p{key[1]:<2} either-reading drops {de}   "
              f"both-reading drops {db}")
        want = target.get(key[0])
        extra = [x for x in dv if want is None or round(x, 1) not in want]
        missed = [x for x in (want or []) if x not in [round(v, 1) for v in dv]]
        print(f"    {'':24} {'':3} vacuous-variant drops {[round(v, 1) for v in dv]}"
              + (f"  -> misses {missed}, adds {[round(v, 1) for v in extra]}"
                 if want else f"  -> adds {[round(v, 1) for v in extra]}"))
    print(f"\n    null control: {null_seen} unstraddled boundaries checked, "
          f"{'all refused' if null_ok else 'A UNIVERSAL FIRED — see above'}")

    if not control_ok:
        print("\nREFUSED: the straddle counts do not reproduce PR #237. This script is "
              "measuring something else and its verdict is void.")
        return 1
    if not null_ok:
        print("\nREFUSED: the null control fired — the quantifier is inverted.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
