#!/usr/bin/env python
"""probe_emitter_typing — the R61 oracle: is emitter-typing actually holding?

WHY THIS EXISTS. 2026-08-06's subclass-only closure made every `rdfs:domain`/`rdfs:range`
rule in `vocab/ontology/tab.ttl` inert *for typing purposes*. Each of those rules used to be a
path by which a node entered a shape's target set without an explicit `rdf:type`. Since then,
every shape's reach depends entirely on emitters typing every node explicitly — and nothing
enforced that invariant. This probe is the enforcement.

WHY THE SCORE GATE CANNOT SUBSTITUTE FOR IT. A lost typing means a shape stops seeing a node.
The region it would have refused is then admitted, so the failure appears as a region flipping
escalated -> asserted: a score **improvement**. The corpus score gate cannot distinguish that
from a real fix. Only this probe can.

WHAT IT ASSERTS. For every `P rdfs:domain C` in tab.ttl, every subject of `P` in a compiled
page carries type `C` (explicitly, or via `rdfs:subClassOf` — the closure the membrane really
applies). Likewise every non-literal object of a `P rdfs:range C`.

HOW TO READ THE OUTPUT. A violation is only a LIVE hazard when `C` is a class some shape
targets — otherwise the lost typing removes the node from nobody's reach. The summary therefore
splits the count, and the `sh:sparql` column is the sharpest form: those shapes are the ones
whose constraints silently stop applying.

Gate classification (CLAUDE.md §8): PROCEDURAL measurement harness. It makes no domain
decision — the decisions are the ontology's domain/range rules, which this only applies and
counts. No tuned constant, tolerance or threshold appears here.

Usage:
    ./.venv/bin/python scripts/probe_emitter_typing.py [--json OUT]

Exit code 0 when no violation lands on a shape-targeted class, non-zero otherwise — so it can
be used as a gate once R61 is repaired.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS, SH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XSD_PREFIX = "http://www.w3.org/2001/XMLSchema#"
SHAPE_FILES = ("tab-shapes.ttl", "tab-physical-shapes.ttl")


def typing_rules(ont: Graph):
    """(property, class) pairs that USED to type a node. Literal ranges cannot type, so drop."""
    domains = list(ont.subject_objects(RDFS.domain))
    ranges = [(p, c) for p, c in ont.subject_objects(RDFS.range)
              if not str(c).startswith(XSD_PREFIX)]
    return domains, ranges


def shape_targets(vocab: str):
    """Classes some shape targets, and the subset targeted by a shape carrying sh:sparql."""
    targets, sparql = set(), set()
    for f in SHAPE_FILES:
        g = Graph().parse(os.path.join(vocab, "shapes", f), format="turtle")
        for shape, cls in g.subject_objects(SH.targetClass):
            targets.add(cls)
            if (shape, SH.sparql, None) in g:
                sparql.add(cls)
    return targets, sparql


def _closure(ont: Graph):
    sup = collections.defaultdict(set)
    for s, o in ont.subject_objects(RDFS.subClassOf):
        sup[s].add(o)
    return sup


def types_of(g: Graph, node, sup) -> set:
    """Explicit types, closed under rdfs:subClassOf — what the membrane's closure materialises."""
    out = set(g.objects(node, RDF.type))
    stack = list(out)
    while stack:
        for parent in sup.get(stack.pop(), ()):
            if parent not in out:
                out.add(parent)
                stack.append(parent)
    return out


def probe(graph: Graph, domains, ranges, sup):
    """Yield (rule_key, class, node) for every node missing a type its property implies."""
    for p, c in domains:
        for s in set(graph.subjects(p, None)):
            if c not in types_of(graph, s, sup):
                yield f"domain {p.split('#')[-1]} -> {c.split('#')[-1]}", c, s
    for p, c in ranges:
        for o in set(graph.objects(None, p)):
            if not isinstance(o, Literal) and c not in types_of(graph, o, sup):
                yield f"range  {p.split('#')[-1]} -> {c.split('#')[-1]}", c, o


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the per-rule tally here")
    args = ap.parse_args()

    import pypdfium2 as pdfium
    from iladub.etkl import compile_tables

    vocab = os.path.join(ROOT, "vocab")
    ont = Graph().parse(os.path.join(vocab, "ontology", "tab.ttl"), format="turtle")
    domains, ranges = typing_rules(ont)
    targets, sparql = shape_targets(vocab)
    sup = _closure(ont)
    print(f"tab.ttl: {len(domains)} domain rules, {len(ranges)} non-literal range rules; "
          f"{len(targets)} shape-targeted classes ({len(sparql)} of them sh:sparql)")

    counts, example, cls_of, pages = collections.Counter(), {}, {}, 0
    for path in sorted(glob.glob(os.path.join(ROOT, "corpus", "*", "*.pdf"))):
        doc = pdfium.PdfDocument(path)
        n = len(doc)
        doc.close()
        for pg in range(n):
            rep = compile_tables(path, page_number=pg, validate_shapes=False)
            pages += 1
            for key, cls, node in probe(rep.graph, domains, ranges, sup):
                counts[key] += 1
                cls_of[key] = cls
                example.setdefault(key, f"{os.path.basename(path)} p{pg}: {node}")

    live = sum(n for k, n in counts.items() if cls_of[k] in targets)
    live_sparql = sum(n for k, n in counts.items() if cls_of[k] in sparql)
    print(f"\npages probed: {pages}")
    print(f"{'rule':40} {'nodes':>6}  targeted  sh:sparql")
    for key, n in counts.most_common():
        print(f"{key:40} {n:6}  {'YES' if cls_of[key] in targets else 'no ':8}  "
              f"{'YES' if cls_of[key] in sparql else 'no'}\n{'':6}e.g. {example[key]}")
    print(f"\ntotal violating nodes: {sum(counts.values())}")
    print(f"  on a shape-targeted class            : {live}")
    print(f"  on a class an sh:sparql shape targets: {live_sparql}   <-- the live hazard")

    if args.json:
        json.dump({k: {"nodes": n, "class": str(cls_of[k]), "example": example[k],
                       "shape_targeted": cls_of[k] in targets,
                       "sparql_targeted": cls_of[k] in sparql}
                   for k, n in counts.items()}, open(args.json, "w"), indent=1, sort_keys=True)
    return 0 if live == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
