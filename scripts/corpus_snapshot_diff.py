"""Diff two `corpus_verdict_snapshot.py` directories — the missing half of that instrument.

That script takes ONE reading and writes it to disk, because two readings of the same tree cannot
be taken in one process; the caller was then left to compare two directories by eye. Every loop
that has done so has re-derived the same comparison by hand, and the 2026-09-14 handoff records
the cost: the snapshots are session-local, so the *figures* in a spec become the only surviving
record of what moved.

Prints, per document: the score and canonical graph hash on both sides, then — only where they
differ — every page whose score, cells, adoption or region verdicts moved, and the `notes` the
after-side added (adoption refusals name themselves there, which is how a widened gate's REFUSALS
are read back).

    PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py <before-dir> <after-dir>

Gate classification (CLAUDE.md §8): PROCEDURAL. It reads two JSON files and prints their
differences. It decides nothing about any document, changes no reading, and carries no tolerance:
every comparison is exact equality over values another instrument already computed.
"""
from __future__ import annotations

import json
import pathlib
import sys


def _cells(page) -> int:
    return sum(r["cells"] for r in page["regions"])


def _verdicts(page) -> list[str]:
    return [f"{r['verdict']}:{r['cells']}" for r in page["regions"]]


def main(argv):
    before, after = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    names = sorted(p.stem for p in before.glob("*.json"))
    if not names:
        raise SystemExit(f"no snapshots in {before}")
    moved = 0
    for name in names:
        b = json.loads((before / f"{name}.json").read_text())
        a_path = after / f"{name}.json"
        if not a_path.exists():
            print(f"{name:30} MISSING on the after side")
            continue
        a = json.loads(a_path.read_text())
        same = b["graph_sha256"] == a["graph_sha256"]
        print(f"{name:30} {b['score']:.10f} -> {a['score']:.10f}  "
              f"triples {b['graph_triples']:6} -> {a['graph_triples']:6}  "
              f"{'IDENTICAL' if same else 'CHANGED'}")
        if same:
            continue
        moved += 1
        if b["adopted"] != a["adopted"]:
            print(f"    adopted  {b['adopted']} -> {a['adopted']}")
        if b["chains"] != a["chains"]:
            print(f"    chains   {len(b['chains'])} -> {len(a['chains'])}")
        for i, (pb, pa) in enumerate(zip(b["pages"], a["pages"])):
            if _verdicts(pb) == _verdicts(pa) and pb["asserted"] == pa["asserted"] \
                    and pb["escalated"] == pa["escalated"]:
                continue
            print(f"    p{i}: score {pb['score']:.4f} -> {pa['score']:.4f}   "
                  f"cells {_cells(pb):5} -> {_cells(pa):5}   "
                  f"asserted {pb['asserted']:5} -> {pa['asserted']:5}   "
                  f"escalated {pb['escalated']:5} -> {pa['escalated']:5}")
        for note in a["notes"]:
            if note not in b["notes"]:
                print(f"    + note: {note}")
        for note in b["notes"]:
            if note not in a["notes"]:
                print(f"    - note: {note}")
    print(f"\n{moved} of {len(names)} documents changed")


if __name__ == "__main__":
    main(sys.argv)
