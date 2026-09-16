#!/usr/bin/env python3
"""R44 leg 1 — with p5's adoption suppressed, do the four superseded ROUND_TRIP_FAIL return live?

The 2026-09-15 handoff's § 5c is a PROPOSITION, and it says so: it proposes p5's round-trip
mechanism as the next build subject and then names the measurement that must precede it —

    with adoption suppressed, do the four superseded regions return as live ROUND_TRIP_FAIL,
    and does the adopted grid's reading of those rows agree with what the round-trip check
    rejects? If adoption already reads them correctly, R44's round-trip half is a REPORTING
    defect, not a reading defect, and the remedy is a different class entirely.

This script is LEG 1 only: does the round-trip failure still exist underneath the adoption, or
did adoption's arrival change what the underlying regions are? Leg 2 (does the adopted grid
read those rows CORRECTLY) is a different question and is not answered here — a region
returning live proves the failure is concealed, never that the concealment is wrong.

WHY SUPPRESSING GLOBALLY IS SUPPRESSING p5, and it is measured rather than assumed: the
baseline control re-reads `rep.adopted` and requires it to be exactly `[5]`. bfs adopts one
page, so `is_adoption_candidate -> False` everywhere is p5's suppression and nothing else's.
If that ever stops being true the control fails rather than the reading silently widening.

A PER-REGION JOIN NEEDS AN IDENTITY, AND THE OBVIOUS ONES ARE NOT ONE — measured 2026-09-16,
by this script printing a wrong answer. Adoption changes the region list on the page it fires
on (at HEAD it adds p5 region16, adoption's own residue), so the two runs' region INDICES are
not known to name the same region, and `table_uri` is minted `{doc}#htable{idx}` from that same
index (compile.py:1256, :1278, :1316). The first version joined on `anchor` instead — which is
the anchor CLASS IRI (`tab#HierarchicalTable`), carried identically by every escalated region —
so it cross-produced 4 subjects against every hit and printed "20 of 4 subjects returned live".

**Its control PASSED while it did so**, because the control validates the two RUNS and not the
JOIN laid over them. That is the generalisable defect, and the guard below is its remedy: the
join REFUSES ITSELF unless every key it uses is unique within each run. A key that collides is
reported as a refusal, never silently cross-produced.

The join key is `RegionReport.ascii` — the region as rendered, which is content and not
position. The shipped `corpus_verdict_snapshot.snapshot()` drops that field, which is the only
reason this file extracts the report itself instead of reusing it; every other field here is
read exactly as that instrument reads it.

THE CONTROL — four known positives, every one recorded INDEPENDENTLY of this file:
  1. baseline `adopted == [5]`            (R224/R225 closure)
  2. baseline p5 asserts 404 cells        (R224/R225 closure)
  3. baseline score equals a `cor:reading` recorded in tests/corpus-manifest.ttl, read from the
     manifest and never from a literal here — a control pinned to a literal goes stale exactly
     as the row it checks did (2026-09-15, bfs_reason_triage.py's own repair)
  4. suppressed `adopted == []`           — THE LOAD-BEARING ONE: it proves the patch took.
     Without it, a suppressed run that silently still adopted would print "nothing returned
     live" and be read as a refutation of § 5c when it measured nothing at all.
A run that cannot re-find all four prints FAIL and exits non-zero.

Both runs are persisted to JSON so any later join — leg 2 included — costs no compile.

Gate classification (CLAUDE.md §8): PROCEDURAL. It runs the shipped `compile_document` twice,
once with one shipped predicate forced to a constant, and counts what comes back. It decides
nothing, changes no reading, and carries no tolerance, threshold or tuned constant. Irreducible
to AXIOM because its input is a compile run rather than a store; irreducible to NEURAL because
nothing in it is underdetermined.

    PYTHONPATH=src:. .venv/bin/python scripts/r44_adoption_suppressed.py [outdir]
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "scripts")

from bfs_reason_triage import recorded_readings  # the manifest-reading score leg, reused

PDF = "corpus/gov-stats/bfs-population-bilan-2023.pdf"

# Recorded by the R224/R225 closure, independently of this script.
CONTROL_ADOPTED_PAGE = 5
CONTROL_ADOPTED_CELLS = 404

# The four p5 regions the 2026-09-15 triage found SUPERSEDED carrying ROUND_TRIP_FAIL, and the
# same four the 2026-09-14 decision census independently names withdrawn (#region9/10/11/12-d4).
# Indices are valid in the BASELINE run only; they are never carried into the other run.
SUBJECTS_AT_HEAD = [9, 10, 11, 12]


def rich_snapshot(pdf_path: str) -> dict:
    """The shipped report, keeping `ascii` — the one field a cross-run join can key on."""
    from iladub.etkl.document import compile_document

    rep = compile_document(pdf_path)
    return {
        "pdf": pdf_path,
        "score": rep.score,
        "adopted": list(rep.adopted),
        "chains": [[str(u) for u in c] for c in rep.chains],
        "graph_triples": len(rep.graph),
        "pages": [
            {
                "score": p.score,
                "asserted": p.asserted,
                "escalated": p.escalated,
                "regions": [
                    {"kind": str(r.kind), "verdict": r.verdict, "cells": r.cells,
                     "reason": r.reason, "anchor": r.anchor, "ascii": r.ascii,
                     "table": str(r.table_uri) if r.table_uri else None}
                    for r in p.regions
                ],
            }
            for p in rep.pages
        ],
    }


def reason_bearing(snap: dict) -> list[dict]:
    """Every region carrying an escalation reason, with its page, index and verdict."""
    out = []
    for pno, page in enumerate(snap["pages"]):
        for ridx, r in enumerate(page["regions"]):
            if r["reason"]:
                out.append({"page": pno, "index": ridx, "verdict": r["verdict"],
                            "kind": r["kind"], "reason": r["reason"],
                            "ascii": r["ascii"], "cells": r["cells"]})
    return out


def tally(rows: list[dict]) -> collections.Counter:
    return collections.Counter((r["reason"], r["verdict"]) for r in rows)


def show(title: str, snap: dict) -> list[dict]:
    rows = reason_bearing(snap)
    print(f"{title}")
    print(f"  score={snap['score']!r}  adopted={snap['adopted']}  "
          f"triples={snap['graph_triples']}")
    for r in rows:
        print(f"    p{r['page']} region{r['index']:<3} {r['verdict']:<11} {r['reason']}")
    print("  by (reason, verdict):")
    for (reason, verdict), n in sorted(tally(rows).items()):
        print(f"    {reason:<24} {verdict:<11} {n}")
    print()
    return rows


def join_by_ascii(subjects: list[dict], other: list[dict]) -> tuple[str, list[str]]:
    """Join subjects to `other` on rendered-region text, REFUSING unless every key is unique.

    The refusal is the point. The previous join keyed on a field that was identical across all
    escalated regions and cross-produced silently; nothing in it could notice. This one states
    its precondition and declines to report a number when the precondition does not hold.
    """
    dup_sub = [k for k, n in collections.Counter(r["ascii"] for r in subjects).items() if n > 1]
    dup_oth = [k for k, n in collections.Counter(r["ascii"] for r in other).items() if n > 1]
    if dup_sub or dup_oth:
        return ("REFUSED", [f"the key is not unique: {len(dup_sub)} colliding subject key(s), "
                            f"{len(dup_oth)} colliding key(s) in the compared run — "
                            f"a join on it would cross-produce, as the anchor join did"])
    index = {r["ascii"]: r for r in other}
    lines, returned = [], 0
    for r in subjects:
        hit = index.get(r["ascii"])
        if hit is None:
            lines.append(f"  p{r['page']} region{r['index']:<3} {r['reason']:<20} "
                         f"-> NOT FOUND (the region itself differs without adoption)")
            continue
        live = hit["verdict"] == "escalated" and hit["reason"] == r["reason"]
        returned += live
        lines.append(f"  p{r['page']} region{r['index']:<3} {r['reason']:<20} -> "
                     f"p{hit['page']} region{hit['index']:<3} {hit['verdict']}/{hit['reason']}"
                     f"{'   RETURNED LIVE' if live else ''}")
    lines.append(f"  {returned} of {len(subjects)} subjects returned as live "
                 f"{subjects[0]['reason'] if subjects else '?'} with adoption suppressed.")
    return ("JOINED", lines)


def main() -> int:
    outdir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("BASELINE — adoption as shipped")
    print("=" * 78)
    base = rich_snapshot(PDF)
    base_rows = show("baseline", base)
    base_cells = sum(r["cells"] for r in base["pages"][CONTROL_ADOPTED_PAGE]["regions"]
                     if r["verdict"] == "asserted")

    subjects = [r for r in base_rows
                if r["page"] == CONTROL_ADOPTED_PAGE and r["index"] in SUBJECTS_AT_HEAD]
    print("THE FOUR SUBJECTS, as the baseline reads them (indices valid in THIS run only):")
    for r in subjects:
        print(f"    p{r['page']} region{r['index']:<3} {r['verdict']:<11} {r['reason']}")
    print()

    print("=" * 78)
    print("SUPPRESSED — is_adoption_candidate forced False")
    print("=" * 78)
    import iladub.etkl.adoption as adoption
    adoption.is_adoption_candidate = lambda *a, **k: False
    supp = rich_snapshot(PDF)
    supp_rows = show("suppressed", supp)

    (outdir / "baseline.json").write_text(json.dumps(base, indent=1))
    (outdir / "suppressed.json").write_text(json.dumps(supp, indent=1))
    print(f"persisted -> {outdir}/baseline.json, {outdir}/suppressed.json\n")

    # THE SOUND ANSWER — no region identity required, so no join can corrupt it.
    print("=" * 78)
    print("LEG 1 (join-free) — the reason multiset of each run")
    print("=" * 78)
    bt, st = tally(base_rows), tally(supp_rows)
    reasons = sorted({r for r, _ in bt} | {r for r, _ in st})
    print(f"{'reason':<26} {'base live':>10} {'base sup.':>10} {'base tot':>9}"
          f" {'supp live':>10} {'supp tot':>9}")
    for reason in reasons:
        bl, bs = bt.get((reason, "escalated"), 0), bt.get((reason, "superseded"), 0)
        sl, ss = st.get((reason, "escalated"), 0), st.get((reason, "superseded"), 0)
        print(f"{reason:<26} {bl:>10} {bs:>10} {bl + bs:>9} {sl:>10} {sl + ss:>9}")
    print()

    # The per-region join, reported SEPARATELY and allowed to refuse itself.
    print("=" * 78)
    print("LEG 1 (per-region) — joined on rendered-region text, or refused")
    print("=" * 78)
    status, lines = join_by_ascii(subjects, supp_rows)
    print(f"  status: {status}")
    for line in lines:
        print(line)
    print()

    ladder = recorded_readings()
    matched = [t for t in ladder if abs(float(t[0]) - base["score"]) < 5e-13]
    ok_adopt = list(base["adopted"]) == [CONTROL_ADOPTED_PAGE]
    ok_cells = base_cells == CONTROL_ADOPTED_CELLS
    ok_supp = list(supp["adopted"]) == []

    print("CONTROL — four known positives, recorded independently of this script:")
    print(f"  baseline score matches a recorded reading  {'PASS' if matched else 'FAIL'}  "
          f"({matched[0][1] if matched else 'no reading equals ' + repr(base['score'])})")
    print(f"  baseline adopted == [{CONTROL_ADOPTED_PAGE}]                   "
          f"{'PASS' if ok_adopt else 'FAIL'}  (got {base['adopted']})")
    print(f"  baseline p{CONTROL_ADOPTED_PAGE} asserts {CONTROL_ADOPTED_CELLS} cells            "
          f"{'PASS' if ok_cells else 'FAIL'}  (got {base_cells})")
    print(f"  suppressed adopted == []  (patch took)     "
          f"{'PASS' if ok_supp else 'FAIL'}  (got {supp['adopted']})")
    print("  NOTE: the control validates the two RUNS. It does not validate the join above,")
    print("        which carries its own precondition and refuses when it fails.")

    if not (matched and ok_adopt and ok_cells and ok_supp):
        print("\nFAIL -- control did not re-find its known positives; the reading above is void.")
        return 1
    print("\nCONTROL PASSED -- the tallies above are a reading of HEAD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
