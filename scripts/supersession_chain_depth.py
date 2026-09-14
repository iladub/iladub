"""How deep does a `dec:supersedes` chain actually get? — [[R227]]'s open half.

R227 shipped `document._effective_verdict`, a WALK from a band's pass-1 verdict to the head of
its supersession chain, guarded by a `seen` set against cycles. The row closes its own evidence
with what it could not measure: *"the walk is exercised at chain length 2 only — no corpus
document produces a third hop, so the `seen` cycle guard and any length>2 behaviour are
unmeasured."* This is the instrument for that claim.

**DEPTH IS COUNTED IN EDGES, and the unit is the whole point.** `v1 <- v2 <- admission` is THREE
nodes and TWO edges; a lone `v2 <- v1` is two nodes and ONE edge. A figure reported without its
unit cannot distinguish "the walk never chains at all" from "the walk chains exactly as the
ruling intended", and those are opposite findings about the same number. Every line below prints
`depth_edges` and the node count of the deepest chain together, so the reading is unambiguous
without a convention anyone has to remember.

What it prints per document: the number of `dec:supersedes` edges, how many distinct chains they
form, the maximum depth in edges, and — for the deepest chain — its node URIs in lineage order
(oldest first), which is what makes a length-2 chain legible as the ruled `v1 <- v2 <- admission`
shape rather than as an integer.

Cycle safety: the traversal carries its own `seen` set. A cycle in the data would otherwise hang
this script exactly as it would hang the driver, and an instrument that hangs reports nothing.

Run from the repo root (the corpus is gitignored; a fresh worktree needs it symlinked):

    PYTHONPATH=src .venv/bin/python scripts/supersession_chain_depth.py corpus/**/*.pdf

Gate classification (CLAUDE.md §8): PROCEDURAL. It READS a compiled graph and counts the length
of paths in it — field access, dictionary lookup and a maximum, with no threshold, no tolerance
and no tuned constant. It decides nothing about any document and changes no reading. Irreducible
to AXIOM only in that it reports a census over seven separately-compiled graphs that are never
all in one store; the per-graph question it asks (`dec:supersedes+`) is itself expressible in
SPARQL, and `vocab/queries/effective-chain.rq` already asks it of a single document.
"""
from __future__ import annotations

import pathlib
import sys

from rdflib import Graph, URIRef
from rdflib.namespace import Namespace

DEC = Namespace("https://w3id.org/iladub/dec#")


def _chains(graph: Graph) -> list[list[URIRef]]:
    """Every maximal `dec:supersedes` path, oldest node first.

    An edge `s dec:supersedes o` reads "s replaces o", so lineage runs from an object with no
    outgoing edge (the OLDEST reading) up to a subject nothing supersedes (the head). Paths are
    grown from each oldest node; a node with two superseders would yield two paths, which is
    exactly what `dec:SupersededOnceShape` forbids and therefore worth seeing rather than
    collapsing.
    """
    edges: list[tuple[URIRef, URIRef]] = [(s, o) for s, o in graph.subject_objects(DEC.supersedes)]
    supersedes: dict[URIRef, list[URIRef]] = {}
    for s, o in edges:
        supersedes.setdefault(o, []).append(s)
    objects = {o for _, o in edges}
    subjects = {s for s, _ in edges}
    oldest = sorted(objects - subjects, key=str)

    out: list[list[URIRef]] = []

    def walk(node: URIRef, path: list[URIRef], seen: set[URIRef]) -> None:
        nxt = [s for s in supersedes.get(node, ()) if s not in seen]
        if not nxt:
            out.append(path)
            return
        for s in sorted(nxt, key=str):
            walk(s, path + [s], seen | {s})

    for node in oldest:
        walk(node, [node], {node})
    return out


def main(argv):
    pdfs = argv[1:]
    if not pdfs:
        raise SystemExit("usage: supersession_chain_depth.py <pdf> [<pdf> ...]")
    from iladub.etkl.document import compile_document

    worst = 0
    for pdf in pdfs:
        rep = compile_document(pdf)
        chains = _chains(rep.graph)
        n_edges = len(list(rep.graph.subject_objects(DEC.supersedes)))
        deepest = max(chains, key=len, default=[])
        depth_edges = max((len(c) - 1 for c in chains), default=0)
        worst = max(worst, depth_edges)
        print(f"{pathlib.Path(pdf).stem:38} edges={n_edges:3} chains={len(chains):3} "
              f"max_depth_edges={depth_edges} (deepest chain has {len(deepest)} nodes)", flush=True)
        for node in deepest:
            print(f"      {node}", flush=True)

    print(f"\nmax depth over {len(pdfs)} documents: {worst} edge(s). "
          f"The ruled lineage v1 <- v2 <- admission is 2 edges / 3 nodes; "
          f"{'a third hop WAS reached' if worst > 2 else 'no third hop was reached'}.")


if __name__ == "__main__":
    main(sys.argv)
