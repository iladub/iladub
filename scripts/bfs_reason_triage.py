#!/usr/bin/env python3
"""R44 triage — re-measure bfs's escalation reasons at HEAD, against a row dated 2026-08-04.

R44 (residues-open.md:39) records, from the 2026-08-04 corpus battery:

    2x KIND_NOT_SUPPORTED, 2x REGION_TILING_FAILED, 5x ROUND_TRIP_FAIL
    score 0.3438, chains [1,1,1,1,1,1,1], 8 RECORD_TABLE regions asserting

Its score is ALREADY KNOWN STALE (bfs reads 0.4033 today), so every other figure on that row
is suspect until re-measured. This prints today's reading field by field beside the row's.

THE CONTROL, per the 2026-09-15 repair #3 (an instrument that cannot find a known positive is
low-power and must say so). Three known positives recorded INDEPENDENTLY of this script: the score
must equal one of the `cor:reading` values the corpus manifest records for bfs (and the run says
WHICH, and whether it is the newest), page 5 must be adopted, and page 5 must assert exactly 404
cells — the latter two from the R224/R225 closure. It re-finds all three or prints FAIL and exits
non-zero. The control is not self-validating: every figure comes from a different loop's
measurement, not from this file's own prose.

THE SCORE LEG READS THE MANIFEST RATHER THAN A LITERAL, and that is a repair, not a preference.
Its first version asserted a hard-coded 0.4033 and FAILED against a correct measurement, because
that literal was two readings stale — the very defect `cor:reading` exists to prevent, committed
inside the instrument built to catch that class. A control pinned to a literal goes stale exactly
as the row it is checking did.

COUNTED BY VERDICT CLASS, and the split is the whole point. A first version counted
`verdict == "escalated"` alone and reported ROUND_TRIP_FAIL as having fallen 5 -> 1. It has not:
four of the five are `superseded` — page 5's adoption took the ink over — and a superseded firing
is a reading that was REPLACED, never one that was repaired. Counting live firings alone turns an
adoption into a fix.

Gate classification (CLAUDE.md §8): PROCEDURAL. It calls the shipped snapshot() and counts what
comes back. It decides nothing, changes no reading, and carries no tolerance or threshold — the
only operations are field access and counting. Irreducible to AXIOM because the input is a
compile run, not a store; irreducible to NEURAL because nothing here is underdetermined.

    PYTHONPATH=src:. .venv/bin/python scripts/bfs_reason_triage.py
"""
from __future__ import annotations

import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "scripts")

from corpus_verdict_snapshot import snapshot  # the shipped instrument, reused not copied

PDF = "corpus/gov-stats/bfs-population-bilan-2023.pdf"

# What R44 recorded on 2026-08-04. Quoted here to be COMPARED, never to be trusted.
ROW_2026_08_04 = {
    "KIND_NOT_SUPPORTED": 2,
    "REGION_TILING_FAILED": 2,
    "ROUND_TRIP_FAIL": 5,
}
ROW_SCORE = 0.3438
ROW_RECORD_TABLE_ASSERTED = 8

# The control's structural legs, measured by the R224/R225 closure independently of this script.
CONTROL_ADOPTED_PAGE = 5
CONTROL_ADOPTED_CELLS = 404

MANIFEST = "tests/corpus-manifest.ttl"
BFS_SUBJECT = "urn:iladub:corpus:bfs-population-bilan-2023"


def recorded_readings() -> list[tuple[str, str, str]]:
    """Every score this repo has RECORDED for bfs, newest last: (value, readAt, atCommit).

    The score leg of this script's control read a hard-coded 0.4033 on its first run and FAILED
    against a correct measurement, because that literal was two readings stale — the very defect
    `cor:reading` exists to prevent (a figure carries its date). A control pinned to a literal
    goes stale exactly as the row it is checking did, so it reads the refresh log instead.
    """
    from rdflib import Graph, URIRef

    g = Graph()
    g.parse(MANIFEST, format="turtle")
    out: list[tuple[str, str, str]] = []
    for _p, node in g.predicate_objects(URIRef(BFS_SUBJECT)):
        fields = {"value": "", "readAt": "", "atCommit": ""}
        hit = False
        for p2, o2 in g.predicate_objects(node):
            for key in fields:
                if str(p2).endswith("#" + key) or str(p2).endswith("/" + key):
                    fields[key] = str(o2)
                    hit = hit or key == "value"
        if hit:
            out.append((fields["value"], fields["readAt"], fields["atCommit"]))
    return sorted(out, key=lambda t: t[1])


def main() -> int:
    snap = snapshot(PDF)
    score = snap["score"]

    print(f"bfs  score={score!r}  triples={snap['graph_triples']}  sha={snap['graph_sha256'][:12]}")
    print(f"     adopted={snap['adopted']}  chains={[len(c) for c in snap['chains']]}")
    print(f"     recognized={snap['recognized']}  repaired_bands={snap['repaired_bands']}")
    print(f"     refused_licences={snap['refused_licences']}")
    print()

    # COUNTED BY VERDICT CLASS, and the split is load-bearing. A first version of this script
    # counted `verdict == "escalated"` alone and reported ROUND_TRIP_FAIL as having fallen 5 -> 1.
    # It has not: four of the five are `superseded` — p5's adoption took over the ink, so the
    # band's own record no longer describes what happened to it (compile.py:547-552) — and a
    # superseded firing is a reading that was REPLACED, never one that was repaired. Counting only
    # the live ones turns an adoption into a fix. Which side a count means is the same question
    # apple's 2026-08-20 adjudication raises about graph-side vs report-side.
    live: collections.Counter = collections.Counter()
    superseded: collections.Counter = collections.Counter()
    kinds_asserted: collections.Counter = collections.Counter()
    kinds_superseded: collections.Counter = collections.Counter()
    firings: list[str] = []
    adopted_cells = 0

    for pno, page in enumerate(snap["pages"]):
        for ridx, r in enumerate(page["regions"]):
            if r["reason"] and r["verdict"] in ("escalated", "superseded"):
                (live if r["verdict"] == "escalated" else superseded)[r["reason"]] += 1
                firings.append(f"  p{pno} region{ridx:<3} {r['verdict']:<11} "
                               f"{r['kind']:<28} {r['reason']}")
            if r["verdict"] == "asserted":
                kinds_asserted[r["kind"]] += 1
                if pno == CONTROL_ADOPTED_PAGE:
                    adopted_cells += r["cells"]
            elif r["verdict"] == "superseded":
                kinds_superseded[r["kind"]] += 1

    print("EVERY REASON-BEARING REGION AT HEAD, with its verdict:")
    for line in firings:
        print(line)
    print()

    print(f"{'reason':<26} {'2026-08-04':>11} {'live':>6} {'sup.':>6} {'total':>6}   moved?")
    for reason in sorted(set(ROW_2026_08_04) | set(live) | set(superseded)):
        was = ROW_2026_08_04.get(reason, 0)
        now_live, now_sup = live.get(reason, 0), superseded.get(reason, 0)
        total = now_live + now_sup
        print(f"{reason:<26} {was:>11} {now_live:>6} {now_sup:>6} {total:>6}   "
              f"{'MOVED' if was != total else '-'}")
    print()
    print(f"  live = still escalating.  sup. = superseded, i.e. REPLACED by p"
          f"{CONTROL_ADOPTED_PAGE}'s adoption, not repaired.")
    print(f"  'moved?' compares the row against the TOTAL, which is the like-for-like figure:")
    print(f"  nothing was adopted on bfs when the row was written, so both sides agreed then.")
    print()

    print("ASSERTED REGIONS BY KIND AT HEAD:")
    for kind, n in sorted(kinds_asserted.items()):
        print(f"  {kind:<28} {n}")
    print(f"  (row recorded {ROW_RECORD_TABLE_ASSERTED} RECORD_TABLE asserting)")
    print()

    print(f"SCORE  row 2026-08-04 {ROW_SCORE}   HEAD {score}")
    print()

    ladder = recorded_readings()
    print("EVERY SCORE THIS REPO HAS RECORDED FOR bfs (tests/corpus-manifest.ttl), oldest first:")
    for value, read_at, at_commit in ladder:
        mark = "  <-- today's reading" if abs(float(value) - score) < 5e-13 else ""
        print(f"  {value:<22} {read_at}  {at_commit or '(no commit)':<10}{mark}")
    print()

    matched = [t for t in ladder if abs(float(t[0]) - score) < 5e-13]
    newest = ladder[-1] if ladder else None
    is_newest = bool(newest) and abs(float(newest[0]) - score) < 5e-13
    ok_adopt = CONTROL_ADOPTED_PAGE in snap["adopted"]
    ok_cells = adopted_cells == CONTROL_ADOPTED_CELLS

    print("CONTROL — three known positives recorded INDEPENDENTLY of this script:")
    print(f"  score matches a recorded reading  {'PASS' if matched else 'FAIL'}  "
          f"({matched[0][1] + ' ' + (matched[0][2] or '') if matched else 'no recorded reading equals ' + repr(score)})")
    print(f"  page {CONTROL_ADOPTED_PAGE} is adopted                 {'PASS' if ok_adopt else 'FAIL'}  (adopted {snap['adopted']})")
    print(f"  page {CONTROL_ADOPTED_PAGE} asserts {CONTROL_ADOPTED_CELLS} cells           {'PASS' if ok_cells else 'FAIL'}  (got {adopted_cells})")
    print(f"  ...and it is the NEWEST reading   {'yes' if is_newest else 'NO — the log is stale or the reading moved'}")

    ok_score = bool(matched)

    if not (ok_score and ok_adopt and ok_cells):
        print("\nFAIL -- instrument did not re-find its known positives; do not trust the tally above.")
        return 1
    print("\nCONTROL PASSED -- the tally above is a reading of HEAD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
