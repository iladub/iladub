#!/usr/bin/env python3
"""arc_depends — render the arc's dependency landscape to a committed markdown cache.

WHY THIS EXISTS. `tests/arc-manifest.ttl` carries 43 criteria and, since 2026-08-22, a
criterion->criterion dependency graph (6 asserted edges, 22 propositions). *"What must land
before X"*, *"what can be started today"* and *"how much of the arc does this residue hold up"*
are now DERIVATIONS — `vocab/queries/arc-depends.rq`, `arc-ready.rq`, `arc-reach.rq` — but a
derivation nobody runs answers nobody's question. This renders all three into one file a human
opens (spec docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md §6).

ONE READER OF RECORD, AND THIS FILE IS NOT IT. Every fact below comes out of a `.rq` file that
is RUN, here, against the manifest. Nothing is recomputed in Python: not a closure, not a grade,
not a reach count. That is not fastidiousness — a second reader of a derived fact is the
M9/M9b defect generator this repo has already paid for once (scripts/cockpit.py's own § TWO
READERS OF ONE FACT), and the whole design argument for two predicates (arc-depends.rq's header)
dies the moment a renderer starts deciding what `asserted` means. What this file does with a
query answer is: sort it, name it, and put it in a table.

THE CACHE AND ITS GATE. The output is COMMITTED under `docs/superpowers/`, which is
evidence-class and *"immutable after loop close"* — except, per `CLAUDE.md` § Documentation
governance, for a **generated cache**: *"a file written by a script from a committed source and
gated by regenerate-and-diff, so CI fails unless the tracked bytes are exactly what the source
produces."* The gate is what earns the exception, it is `tests/test_arc_landscape.py`, and it is
a pytest test because CI runs `pytest -q` and nothing else (`.github/workflows/ci.yml:26-27`).
Ungated, this file must not exist. Which is also why the output must be DETERMINISTIC — sorted
rows, no timestamp, no absolute path, no run-dependent content — or the gate can never be green
twice and would be deleted within a week.

CODE NEVER WRITES `tests/arc-manifest.ttl` (that file's own head, spec §9). This script writes
exactly one path: `docs/superpowers/arc-dependency-landscape.md`, and `--out` exists so the gate
can regenerate into a tmp_path. `main()` REFUSES an `--out` that resolves to the manifest — the
tracked one, or whichever file `--manifest` named — because until 2026-08-22 that constraint was
held by an argparse default and by every call site happening to be correct, which is not
enforcement (task 6 review, Minor 1; pinned by `tests/test_arc_landscape.py`).

GATE CLASSIFICATION (CLAUDE.md §8): **PROCEDURAL, and irreducible for a stated reason** —
rendering markdown is not a derivation. There is no decision here to express as an axiom: the
decisions (what depends on what, at which grade; what is ready; what a residue gates) are all
made in SPARQL, open-world and evidence-positive, one directory over. What remains is string
formatting and a filesystem write, and neither is a triple. It scores nothing, ranks nothing it
was not handed, and infers nothing from an absence — where `arc-reach.rq` returns no row, this
prints `?`, never `0` (that query's header, and decision 6 of the 2026-08-20 loop: unknown is
not zero).

Usage:  ./.venv/bin/python scripts/arc_depends.py            # write the tracked cache
        ./.venv/bin/python scripts/arc_depends.py --out X.md # write elsewhere (the gate)
NEVER `python3` — it carries rdflib 7.1.4 and reports false reds across this repo.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from rdflib import RDF, Graph, Literal, Namespace, URIRef

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tests" / "arc-manifest.ttl"
QUERIES = REPO / "vocab" / "queries"
LANDSCAPE = REPO / "docs" / "superpowers" / "arc-dependency-landscape.md"

PROG = Namespace("https://w3id.org/iladub/progress#")
CRITERION = str(PROG) + "criterion:"

# What a residue with no `arc-reach.rq` row renders as. NOT a magic string standing in for a
# number: it is the honest reading of an absent row, and the reason it is a named constant is
# that the gate test asserts against THIS symbol rather than against a literal "?".
UNKNOWN = "?"

# The three derivations, in the order the landscape presents them.
DEPENDS, READY, REACH = "arc-depends.rq", "arc-ready.rq", "arc-reach.rq"


def _text(name: str) -> str:
    return (QUERIES / name).read_text(encoding="utf-8")


def _rows(graph: Graph, name: str, **bindings) -> list[tuple[str, ...]]:
    """Run one arc query and return its rows as tuples of plain strings, in query order.

    Same shape as `tests/test_arc_queries.py::rows` and deliberately so — that module is these
    queries' oracle, and a renderer that consumed them through a different idiom would be
    checked by nothing."""
    result = graph.query(_text(name), initBindings=bindings)
    return [tuple("" if v is None else str(v) for v in r) for r in result]


def short(iri: str) -> str:
    """`…progress#criterion:dec:16` -> `dec:16`. A DISPLAY name and nothing else."""
    return iri[len(CRITERION):] if iri.startswith(CRITERION) else iri


def criteria(graph: Graph) -> list[URIRef]:
    """Every criterion of the manifest, sorted. An ENUMERATION of typed subjects, not a
    derivation: `arc-depends.rq` answers about ONE criterion the caller binds, so somebody has
    to name them, and the graph is the only honest place to get the list."""
    return sorted(graph.subjects(RDF.type, PROG.Criterion), key=str)


def residues(graph: Graph) -> list[str]:
    """Every residue the manifest names as blocking something, sorted by its register number.

    Enumeration again, and the same seam `arc-orphan.rq`/`arc-reach.rq` state at length:
    `prog:blockedBy`'s values are PLAIN STRING LITERALS, because the residue register is a
    markdown file that is not part of the graph."""
    return sorted({str(o) for o in graph.objects(None, PROG.blockedBy)}, key=_residue_key)


def _residue_key(residue: str) -> tuple[int, str]:
    """Register order (R9 before R101), which string order gets wrong. Non-numeric ids sort
    last, by name, rather than crashing the renderer."""
    m = re.fullmatch(r"R(\d+)", residue)
    return (int(m.group(1)), "") if m else (sys.maxsize, residue)


def depends(graph: Graph, criterion: URIRef) -> list[tuple[str, str]]:
    """`arc-depends.rq` for ONE criterion: the graded transitive closure that must land first.

    THE GUARD IS THE POINT. Bound as a `Literal`, this query does not error — it matches
    nothing and returns `[]`, which reads as *"nothing must land before this criterion"*
    (measured; `tests/test_arc_landscape.py` re-measures it). That is the one wrong answer that
    looks like a right one, and rendering it would put a false fact in a committed file. The
    guard is producer-side (CLAUDE.md § Producer-side guards): it fails at the call site that
    built the bad term, with that call site on the stack, rather than downstream in a table."""
    if not isinstance(criterion, URIRef):
        raise TypeError(
            f"arc-depends.rq takes a criterion NODE of the graph, not {type(criterion).__name__}"
            f": {criterion!r}. Bound as a Literal it silently returns no rows, i.e. 'nothing "
            "must land before this' — construct rdflib.URIRef at the call site."
        )
    return [(dep, grade) for dep, grade in _rows(graph, DEPENDS, criterion=criterion)]


def ready(graph: Graph) -> list[tuple[str, str, str]]:
    """`arc-ready.rq`: unmet criteria whose DIRECT dependencies are all met. Query order."""
    return [(rung, crit, stmt) for rung, crit, stmt in _rows(graph, READY)]


def reach(graph: Graph, residue: str) -> str:
    """`arc-reach.rq` for ONE residue: how many unmet criteria its closure gates, or `?`.

    NO ROW MEANS "GATES NOTHING MEASURABLE", NOT "0" — that query's header, and decision 6 of
    the 2026-08-20 loop. A rendered `0` licenses a reading the evidence does not support, so the
    absent row is rendered as the absence it is."""
    rows = _rows(graph, REACH, residue=Literal(residue))
    return rows[0][1] if rows else UNKNOWN


def reach_all(graph: Graph) -> list[tuple[str, str]]:
    """Every named residue with its reach, ordered by that measured count, `?` last.

    ORDERING BY A MEASURED NUMBER IS NOT A RECOMMENDATION. Spec §6 is explicit that this query
    upgrades the cockpit's `frontier 15` from an adjacency count to a RANKING — *"closing R99
    unblocks tab:07, which gates tab:09"* is a strategy statement where *"R99 blocks one
    criterion"* is not. What is sorted here is the query's own answer; nothing in this file says
    which residue to close, which is a judgment and stays the reader's (scripts/cockpit.py's
    § THE TUNED-CONSTANT TRAP)."""
    pairs = [(r, reach(graph, r)) for r in residues(graph)]
    return sorted(
        pairs,
        key=lambda p: (p[1] == UNKNOWN, -int(p[1]) if p[1] != UNKNOWN else 0, _residue_key(p[0])),
    )


def render(graph: Graph) -> str:
    """The landscape, as markdown. Deterministic by construction: every table is built from a
    sorted list, and nothing here reads the clock, the environment or an absolute path."""
    out: list[str] = []
    w = out.append

    w("# The arc's dependency landscape")
    w("")
    w("<!-- GENERATED FILE — DO NOT EDIT BY HAND.")
    w("     Written by scripts/arc_depends.py, which RUNS vocab/queries/arc-depends.rq,")
    w("     arc-ready.rq and arc-reach.rq against tests/arc-manifest.ttl.")
    w("     Regenerate:  ./.venv/bin/python scripts/arc_depends.py")
    w("     Gated by:    tests/test_arc_landscape.py (regenerate-and-diff, byte identity).")
    w("     A hand edit here is reverted by the gate, not merged. -->")
    w("")
    w("A **generated cache** (`CLAUDE.md` § Documentation governance, the second exception to")
    w("evidence-immutability): every figure below is the answer a SPARQL derivation gives over")
    w("the hand-authored manifest, and CI fails unless the tracked bytes are exactly what")
    w("`scripts/arc_depends.py` produces. Nothing here is recomputed in Python.")
    w("")
    w("| | |")
    w("| --- | --- |")
    w("| source | `tests/arc-manifest.ttl` — hand-authored in reviewed commits; code never writes it |")
    w("| derivations | `vocab/queries/arc-depends.rq`, `arc-ready.rq`, `arc-reach.rq` (AXIOM, open world) |")
    w("| renderer | `scripts/arc_depends.py` (PROCEDURAL — markdown is not a derivation) |")
    w("| gate | `tests/test_arc_landscape.py` (regenerate-and-diff) |")
    w("")
    n_asserted = len(list(graph.triples((None, PROG.dependsOn, None))))
    n_proposed = len(list(graph.triples((None, PROG.proposedDependsOn, None))))
    w("**Absence of an edge is absence of a READING, never evidence of independence.** The "
      f"graph was read off {len(criteria(graph))} criteria by a human and then graded by the "
      f"membrane: {n_asserted} of its {n_asserted + n_proposed} edges are grounded by a "
      f"two-sided ablation and {n_proposed} are propositions. This is a monitor, not a "
      "scheduler.")
    w("")

    # ------------------------------------------------------------------ §1 ready
    rows_ready = ready(graph)
    w("## §1 What can be started today — `arc-ready.rq`")
    w("")
    w("Unmet criteria whose **direct** dependencies are all met. Direct and not transitive is a")
    w("CLAUDE.md §8 decision (spec §6): a criterion whose direct dependency is met but whose")
    w("grand-dependency is not still appears here, and transitive readiness follows by iterating.")
    w("A criterion for which no dependency has been read is ready by the same open-world reading:")
    w("there is no criterion this work is known to wait for.")
    w("")
    w(f"**{len(rows_ready)} ready.**")
    w("")
    w("| rung | criterion | statement |")
    w("| --- | --- | --- |")
    for rung, crit, stmt in rows_ready:
        w(f"| `{rung}` | `{short(crit)}` | {_cell(stmt)} |")
    w("")

    # ------------------------------------------------------------------ §2 depends
    w("## §2 What must land first — `arc-depends.rq`")
    w("")
    w("The transitive closure per criterion, **grade-labelled**, with the grounded closure")
    w("(`prog:dependsOn+`) and the full one reported apart so a reader sees where the chain")
    w("stops being grounded. A dependency reachable both by an asserted chain and by one")
    w("containing a proposition is graded `asserted` — the grounded chain exists, and that is")
    w("the fact.")
    w("")
    closures = [(c, depends(graph, c)) for c in criteria(graph)]
    with_edges = [(c, rows) for c, rows in closures if rows]
    w(f"**{len(with_edges)} of {len(closures)} criteria carry a closure**; for the other "
      f"{len(closures) - len(with_edges)} no dependency has been read, which is not a claim "
      "that they have none.")
    w("")
    w("| criterion | asserted — grounded by ablation | proposed — read, not grounded |")
    w("| --- | --- | --- |")
    for crit, rows in with_edges:
        asserted = [short(d) for d, g in rows if g == "asserted"]
        proposed = [short(d) for d, g in rows if g == "proposed"]
        w(f"| `{short(str(crit))}` | {_terms(asserted)} | {_terms(proposed)} |")
    w("")

    # ------------------------------------------------------------------ §3 reach
    rows_reach = reach_all(graph)
    w("## §3 How much of the arc each residue holds up — `arc-reach.rq`")
    w("")
    w("For every residue the manifest names in `prog:blockedBy`: the count of **unmet** criteria")
    w("that reach the criterion it blocks, that criterion included. A met criterion mid-chain")
    w("still transmits gating; a met criterion is never counted as gated.")
    w("")
    w(f"`{UNKNOWN}` means the derivation returns **no row** — the residue gates nothing")
    w("measurable — and is deliberately not `0`: unknown is not zero, and a rendered `0` would")
    w("be a measurement this evidence does not make. The order is by the measured count and is")
    w("not a recommendation; which residue to close is a judgment and stays the reader's.")
    w("")
    w("| residue | unmet criteria gated |")
    w("| --- | --- |")
    for residue, gated in rows_reach:
        w(f"| `{residue}` | {gated} |")
    w("")

    return "\n".join(out) + "\n"


def _cell(text: str) -> str:
    """A criterion statement inside a markdown table cell: pipes escaped, newlines flattened.
    Statements are hand-authored prose and one of them will eventually contain a `|`."""
    return " ".join(text.split()).replace("|", "\\|")


def _terms(names: list[str]) -> str:
    return ", ".join(f"`{n}`" for n in names) if names else "—"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="render the arc's dependency landscape")
    ap.add_argument("--out", type=Path, default=LANDSCAPE,
                    help="output path (default: the tracked cache; refuses the manifest)")
    ap.add_argument("--manifest", type=Path, default=MANIFEST,
                    help="the hand-authored source (default: tests/arc-manifest.ttl)")
    args = ap.parse_args(argv)

    # CODE NEVER WRITES `tests/arc-manifest.ttl` (that file's own head, :16-18; spec §9; Global
    # Constraint 4 of the 2026-08-22 plan). Until this refusal existed the constraint was held by
    # an argparse DEFAULT and by every call site happening to be correct — `arc_depends.py --out
    # tests/arc-manifest.ttl` would have had a renderer overwrite the hand-authored source it had
    # just read. A hard constraint enforced only by a default is enforced by nothing (task 6
    # review, Minor 1). The second member generalises it: a generator never writes its own source,
    # whichever file the caller named as that source.
    forbidden = {args.manifest.resolve(): "the manifest this run reads",
                 MANIFEST.resolve(): "tests/arc-manifest.ttl"}
    if args.out.resolve() in forbidden:
        raise SystemExit(
            f"arc_depends refuses to write {args.out} — that is "
            f"{forbidden[args.out.resolve()]}, and edges are hand-authored in reviewed commits "
            f"(tests/arc-manifest.ttl:16-18). This script writes exactly one kind of file: the "
            f"generated landscape cache.")

    graph = Graph()
    graph.parse(args.manifest, format="turtle")
    args.out.write_text(render(graph), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
