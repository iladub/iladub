#!/usr/bin/env python3
"""Which `prog:oracleTest` node ids the arc manifest names, and which of them COLLECT.

WHY THIS EXISTS. `tests/test_arc_manifest.py`'s M5b answers this question for MET criteria only,
and says so deliberately (`:313-316`: *"An UNMET criterion may name a TARGET oracle that does not
exist yet"*). So the repo has no reading at all of the unmet half — and the unmet half is where
the arc's remaining work is. This prints the whole population and separates two kinds of absence
that read alike in the manifest and are not alike at all:

  * **module absent** — the file the id names does not exist. An honestly future oracle for work
    nobody has started (the `substrate` rung is 0/3 and nothing under `tests/substrate/` exists).
  * **dangling in an existing file** — the file exists and the node id in it does not. The oracle's
    home is built and the oracle is not, which is the case a reader cannot see by opening the file.

It decides nothing. Which absence is a defect and which is a target is a judgment, and the two
counts are printed apart rather than ranked, per the `cockpit.py` rule on this repo's instruments.

THE CONTROL, and it comes from outside this file. Two known positives and one known negative, none
of them this script's own prose:

  * every MET criterion's named id MUST collect — not because this script says so but because M5b
    refuses `prog:met true` otherwise and CI is green at HEAD. A run that reports a met criterion's
    id as absent has found a bug in itself, or CI is red.
  * the three `tests/substrate/*` ids MUST be reported module-absent: the manifest's own
    `substrate` comments describe unbuilt runtime work and the rung reads 0/3.
  * a null: an id this script invents (`--null`) must be reported absent. An instrument that
    reports everything present cannot report anything absent.

Gate classification (CLAUDE.md §8): PROCEDURAL. It reads a committed manifest, runs pytest's own
collector as a subprocess, and compares two sets of strings. No reading judgment, no tolerance, no
threshold. Irreducible to AXIOM because collectability is a property of the RUNNER, not of the
graph — nothing in RDF can answer "does this node id collect under this interpreter"; irreducible
to NEURAL because set membership is decidable.

    $ ./.venv/bin/python scripts/oracle_test_census.py
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

import rdflib

REPO = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tests" / "arc-manifest.ttl"
PROG = rdflib.Namespace("https://w3id.org/iladub/progress#")

# Recorded independently of this file: tests/arc-manifest.ttl's substrate criteria describe
# runtime work no loop has started, and the cockpit reads that rung 0/3.
KNOWN_ABSENT = (
    "tests/substrate/test_event_ledger.py::test_committed_events_are_immutable",
    "tests/substrate/test_in_engine_policy.py::test_engine_enforces_ai_inherits_user",
    "tests/substrate/test_write_gate.py::test_engine_refuses_an_ungoverned_commit",
)


def declarations(graph):
    """(criterion iri, met, node id) for every prog:oracleTest in the manifest."""
    out = []
    for c in graph.subjects(rdflib.RDF.type, PROG.Criterion):
        met = graph.value(c, PROG.met)
        for t in graph.objects(c, PROG.oracleTest):
            out.append((str(c), bool(met), str(t)))
    return sorted(out, key=lambda r: (r[2], r[0]))


def collected(files):
    """Every node id pytest's own collector reports for these files."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header", *files],
        cwd=REPO, capture_output=True, text=True)
    ids = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith(("ERROR", "E ", "no tests")):
            ids.add(line)
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--null", default="tests/test_corpus.py::test_this_id_is_invented",
                    help="the null control: an id that must be reported absent")
    args = ap.parse_args()

    graph = rdflib.Graph().parse(args.manifest, format="turtle")
    rows = declarations(graph)
    named = sorted({t for _, _, t in rows})
    files = sorted({t.split("::")[0] for t in named if (REPO / t.split("::")[0]).exists()})
    present = collected(files)

    absent_module, dangling = [], []
    for t in named + [args.null]:
        owners = [(i, m) for i, m, x in rows if x == t]
        if not (REPO / t.split("::")[0]).exists():
            absent_module.append((t, owners))
        elif t not in present:
            dangling.append((t, owners))

    print(f"{len(rows)} declarations, {len(named)} distinct node ids, "
          f"{len(files)} files, {len(present)} ids collected\n")

    print(f"MODULE ABSENT — the file does not exist ({len(absent_module)}):")
    for t, owners in absent_module:
        print(f"  {t}\n      named by {', '.join(i.split('#')[-1] for i, _ in owners) or '(null control)'}")

    print(f"\nDANGLING IN AN EXISTING FILE — the file exists, the node id does not ({len(dangling)}):")
    for t, owners in dangling:
        names = ", ".join(f"{i.split('#')[-1]}{' MET' if m else ''}" for i, m in owners)
        print(f"  {t}\n      named by {names or '(null control)'}")

    print("\nCONTROL — three checks, none of them this file's own prose:")
    absent_ids = {t for t, _ in absent_module} | {t for t, _ in dangling}
    met_absent = sorted({t for i, m, t in rows if m and t in absent_ids})
    ok = True
    for label, good in (
            (f"every met criterion's id collects  ({sum(1 for _, m, _ in rows if m)} declarations)",
             not met_absent),
            (f"the {len(KNOWN_ABSENT)} substrate ids are reported absent",
             all(k in absent_ids for k in KNOWN_ABSENT)),
            ("the invented null id is reported absent", args.null in absent_ids)):
        print(f"  {label:<60} {'PASS' if good else 'FAIL'}")
        ok = ok and good
    if met_absent:
        print(f"    met criteria whose id did not collect: {met_absent}")
    if not ok:
        print("\nFAIL -- the census did not re-find its known positives; do not trust it.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
