"""The R234 lockout census: how many bands reach the NEURAL wrap-composer's locked door?

R234 measured, on ONE band (ons p4 band 0, cut `(L,T)=(2,1)`), a composition of two
correct behaviours that together refuse a real table:

  1. ``group_wrapped``'s wrap gate declines a structurally-valid wrap continuation
     because its gap EQUALS ``tightest_row_gap`` (``12.00 < 12.00`` is false). That is
     the AXIOM behaving correctly — a gap indistinguishable from a certified row
     boundary IS a row (R208 spec § 4, HONEST LIMIT (b)).
  2. The resulting TRUNCATED header tree nevertheless satisfies ``merge_tiling_ok``
     (centered, non-overlapping, one leaf per column — self-consistently wrong), so
     ``compile.py:1277``'s ``not merge_tiling_ok(...)`` is False and the NEURAL
     wrap-composer (``rowrole.build_row_reading``) — the remedy ``headers.py:412-427``
     names for exactly these rows — is NEVER ENTERED.

This script measures the POPULATION of that signature over the corpus, because the
remedy calculus differs completely between a population of one and a corpus-wide class.

THE PROXY, AND WHY IT IS NOT QUESTION-BEGGING. The handoff that ordered this census
(``2026-09-15-repair-plan-next-loop-handoff.md`` § 5b) graded itself PROPOSED and warned
that its own phrasing — bands where ``header_rows_of`` returns "fewer rows than the
boxhead actually occupies" — needs a proxy for *the boxhead's actual extent*, which is
THE VERY THING IN DISPUTE. Any such proxy would be circular in the way R235's v1 census
was circular. This script does NOT use that phrasing. It asks only questions the shipped
code already answers on its own terms:

    (a) does ``classify_hierarchical`` return a HierRegion whose ``merge_tiling_ok``
        is True — i.e. is the NEURAL branch gated shut? and
    (b) does ``group_wrapped`` see >= 1 consecutive pair that is a structural wrap
        candidate which the GAP TEST ALONE refuses?

Neither leg consults the author's intent, a ground truth, or a human reading. Leg (b)
reuses ``group_wrapped``'s OWN predicates rather than approximating them: its conditions
2 and 3 (``cols_j subset of open`` and ``len(cols_j) < len(anchor)``) are together
exactly ``_partial_of(prev, cur)`` (``cells.py:207``), and the CERTAIN pairs whose
minimum sets the threshold are exactly that predicate's complement plus the hrule veto
(``cells.py:210``). So no new threshold, tolerance or constant enters this instrument.

THE CONTROL (required: an instrument that cannot re-find its own founding case is
low-power, and R235's v1 census is this repo's measured counter-example). The control
re-runs the signature on ons p4 band 0 cut ``(2,1)`` and requires the R234 figures back:
``merge_tiling_ok`` True, >= 1 gap-refused candidate, ``tightest_row_gap == 12.00``, and
the refusal at EXACT equality. It prints ``FAIL -- instrument is low-power`` and exits
non-zero if any of that does not reproduce. The control band is a CUT band, so it is not
reachable by the natural-band sweep; it is run explicitly and reported separately.

The only float epsilon here (``1e-9``, distinguishing "gap equals the threshold" from
"gap exceeds it") is IEEE-754 equality slack, not a tolerance on the documents: the two
quantities being compared are gaps read from the same page by the same instrument.

§8 gate — PROCEDURAL: an instrument that calls shipped functions and prints what they
return. It decides nothing about any document, changes no behaviour, and carries no tuned
constant. The judgement of what the population MEANS is left to the reader, in prose.

Run it from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/r234_lockout_census.py [pdf ...]
"""
from __future__ import annotations

import glob
import os
import sys
from dataclasses import replace
from statistics import median

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iladub.etkl import cells as cells_mod  # noqa: E402
from iladub.etkl.cells import recover_leaf_grid  # noqa: E402
from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.document import page_count  # noqa: E402
from iladub.etkl.headers import merge_tiling_ok  # noqa: E402
from iladub.etkl.hierarchical import classify_hierarchical  # noqa: E402

EPS = 1e-9
ONS = "corpus/gov-stats/ons-index-of-services-2026-02.pdf"


def wrap_pairs(band, grid):
    """Re-run group_wrapped's OWN pair classification, reporting per-pair verdicts.

    Mirrors cells.group_wrapped:174-241 exactly — same tops, same lead, same hrule veto,
    same _partial_of, same certain-pair enumeration, same tightest_row_gap fallback.
    Returns None for a band too short to have a pair.
    """
    b = grid.boundaries
    lines = list(band.lines)
    if len(lines) < 2:
        return None
    tops = [ln.top for ln in lines]
    gaps = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    lead = median([g for g in gaps if g > 0]) if any(g > 0 for g in gaps) else 0.0
    hrule_ys = sorted({round(h.y, 2) for h in band.hrules})

    per_line = []
    for ln in lines:
        by_col: dict[int, list] = {}
        for w in ln.words:
            by_col.setdefault(cells_mod.column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        per_line.append(by_col)

    def vetoed(j):
        return any(tops[j - 1] < y <= tops[j] for y in hrule_ys)

    def partial_of(prev, cur):
        return bool(cur) and all(c in prev for c in cur) and len(cur) < len(prev)

    js = range(1, len(lines))
    certain = [j for j in js if vetoed(j) or not partial_of(per_line[j - 1], per_line[j])]
    certain_gaps = [tops[j] - tops[j - 1] for j in certain]
    tightest = min(certain_gaps) if certain_gaps else lead

    # A structural wrap candidate: conditions 2+3 hold (== _partial_of) and no hrule veto.
    cands = [j for j in js if not vetoed(j) and partial_of(per_line[j - 1], per_line[j])]
    # Refused by the GAP TEST ALONE: structurally a wrap, declined only because
    # `gap < tightest_row_gap` is false.
    refused = [j for j in cands if (tops[j] - tops[j - 1]) >= tightest - EPS]
    exact = [j for j in refused if abs((tops[j] - tops[j - 1]) - tightest) < EPS]
    return {
        "tightest": tightest, "lead": lead, "n_certain": len(certain),
        "cands": cands, "refused": refused, "exact": exact,
        "gaps": {j: tops[j] - tops[j - 1] for j in cands},
    }


def signature(band):
    """(state, tiling, wrap) for one band. state names why a band is out of scope."""
    grid = recover_leaf_grid(band)
    if grid.ncols < 2:
        return "ncols<2", None, None
    hreg = classify_hierarchical(band)
    if hreg is None:
        return "no-hierregion", None, None
    tiling = merge_tiling_ok(hreg.tree, hreg.grid)
    return "in-scope", tiling, wrap_pairs(band, hreg.grid)


def locked_out(tiling, wrap):
    """The R234 signature: the NEURAL branch is gated shut AND a wrap was gap-refused."""
    return bool(tiling) and bool(wrap) and bool(wrap["refused"])


def fmt_margins(margins):
    """Margins at FULL precision. Rounding these to 2dp hides R208 § 4(b)'s residual:
    the at-pitch cluster sits ~2.3e-5 pt above the certain minimum (spec § 4(b):
    "candidates >= 6.479988, certain minimum 6.479965"), which prints as 0.0 at 2dp and
    is NOT the same thing as a genuine row boundary 0.93 pt away. No cutoff is applied --
    a threshold separating "sub-precision" from "real" would be exactly the tuned constant
    CLAUDE.md § 8 forbids. The reader classifies these in prose."""
    return "{" + ", ".join(f"{j}: {m:.3e}" for j, m in margins.items()) + "}"


def cut(band, lead_n, trail_n):
    """Band with `lead_n` lines off the top and `trail_n` off the bottom, top/bottom recomputed."""
    ls = band.lines[lead_n: len(band.lines) - trail_n] if trail_n else band.lines[lead_n:]
    return replace(band, lines=tuple(ls),
                   top=min(ln.top for ln in ls), bottom=max(ln.bottom for ln in ls))


def control():
    """Re-find R234's founding case, or declare the instrument low-power."""
    print("=== CONTROL: ons p4 band 0 cut (L,T)=(2,1) -- R234's founding case")
    band = cut(page_bands(ONS, 4)[0], 2, 1)
    state, tiling, wrap = signature(band)
    print(f"    state={state} nlines={len(band.lines)} "
          f"words={sum(len(ln.words) for ln in band.lines)} merge_tiling_ok={tiling}")
    if wrap:
        print(f"    tightest_row_gap={wrap['tightest']:.2f} lead={wrap['lead']:.2f} "
              f"n_certain={wrap['n_certain']}")
        print(f"    wrap candidates={wrap['cands']} gap-refused={wrap['refused']} "
              f"at EXACT equality={wrap['exact']}")
        print(f"    candidate gaps={ {j: round(g, 2) for j, g in wrap['gaps'].items()} }")
    checks = {
        "state is in-scope": state == "in-scope",
        "merge_tiling_ok is True": tiling is True,
        ">=1 gap-refused wrap candidate": bool(wrap and wrap["refused"]),
        "refusal at EXACT equality": bool(wrap and wrap["exact"]),
        "tightest_row_gap == 12.00": bool(wrap and abs(wrap["tightest"] - 12.00) < 1e-6),
        "signature fires (locked out)": locked_out(tiling, wrap),
    }
    for name, got in checks.items():
        print(f"    [{'ok  ' if got else 'FAIL'}] {name}")
    if all(checks.values()):
        print("    CONTROL PASSED -- the instrument re-finds R234. Sweep is trustworthy.\n")
        return True
    print("    FAIL -- instrument is low-power, do not trust the sweep below.\n")
    return False


def main(argv):
    ok = control()
    pdfs = argv[1:] or sorted(glob.glob("corpus/*/*.pdf"))
    print("=== SWEEP: every natural band, all corpus documents")
    # `locked_out` is the BROAD leg (any gap-refused candidate). The narrow leg
    # `locked_out_at_EXACT_equality` is R234's ACTUAL signature: a wrap the AXIOM could not
    # distinguish from a certified row boundary. A candidate refused by a WIDE margin is a
    # row the AXIOM correctly declined -- R208's intended behaviour, not a lockout.
    tally = {"bands": 0, "ncols<2": 0, "no-hierregion": 0, "in-scope": 0,
             "tiling-ok": 0, "tiling-fail": 0, "locked_out": 0,
             "locked_out_at_EXACT_equality": 0, "with_cands": 0, "neural_open": 0}
    hits = []
    for pdf in pdfs:
        for p in range(page_count(pdf)):
            for i, band in enumerate(page_bands(pdf, p)):
                tally["bands"] += 1
                state, tiling, wrap = signature(band)
                if state != "in-scope":
                    tally[state] += 1
                    continue
                tally["in-scope"] += 1
                tally["tiling-ok" if tiling else "tiling-fail"] += 1
                if wrap and wrap["cands"]:
                    tally["with_cands"] += 1
                if not tiling and wrap and wrap["cands"]:
                    tally["neural_open"] += 1
                    print(f"  neural-OPEN  {os.path.basename(pdf)} p{p} band{i} "
                          f"(tiling FAILED -> rowrole CAN fire) cands={wrap['cands']}")
                if locked_out(tiling, wrap):
                    tally["locked_out"] += 1
                    if wrap["exact"]:
                        tally["locked_out_at_EXACT_equality"] += 1
                    margins = {j: wrap["gaps"][j] - wrap["tightest"]
                               for j in wrap["refused"]}
                    where = f"{os.path.basename(pdf)} p{p} band{i}"
                    hits.append((where, band, wrap, margins))
                    print(f"  LOCKED OUT  {where}  nlines={len(band.lines)} "
                          f"tightest={wrap['tightest']!r} refused={wrap['refused']} "
                          f"exact={wrap['exact']} margins(gap-tightest)={fmt_margins(margins)}")
    print("\n=== TALLY")
    for k, v in tally.items():
        print(f"    {k:>16} = {v}")
    narrow = [h for h in hits if h[2]["exact"]]
    print(f"\n=== R234's ACTUAL signature (refused at EXACT equality): {len(narrow)} band(s)")
    print("    A wide margin means the AXIOM declined a candidate that plainly IS a row --")
    print("    correct R208 behaviour, NOT the lockout R234 names.")
    print(f"\n=== THE {len(hits)} BROADLY LOCKED-OUT BAND(S), first 3 lines each")
    for where, band, wrap, margins in hits:
        print(f"  {where}  (refused {wrap['refused']}, exact {wrap['exact']}, "
              f"margins {fmt_margins(margins)})")
        for ln in band.lines[:3]:
            print(f"      | {' '.join(w.text for w in ln.words)[:96]}")
    if not ok:
        print("\nNB the CONTROL FAILED -- every number above is suspect.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
