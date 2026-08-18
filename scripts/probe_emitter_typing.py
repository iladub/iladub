#!/usr/bin/env python
"""probe_emitter_typing — the R61 oracle: is emitter-typing actually holding?

WHY THIS EXISTS. 2026-08-06's subclass-only closure made every `rdfs:domain`/`rdfs:range`
rule in the tab ontology (`ONT_FILES` below) inert *for typing purposes*. Each of those rules used to be a
path by which a node entered a shape's target set without an explicit `rdf:type`. Since then,
every shape's reach depends entirely on emitters typing every node explicitly — and nothing
enforced that invariant. This probe is the enforcement.

WHY THE SCORE GATE CANNOT SUBSTITUTE FOR IT. A lost typing means a shape stops seeing a node.
The region it would have refused is then admitted, so the failure appears as a region flipping
escalated -> asserted: a score **improvement**. The corpus score gate cannot distinguish that
from a real fix. Only this probe can.

WHAT IT ASSERTS. For every `P rdfs:domain C` in `ONT_FILES`, every subject of `P` in a compiled
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

# R103, 2026-08-17: was `tab.ttl` alone, so every domain/range rule the DATA-GRID vocabulary
# declares was outside the probe's reach entirely — the emitter-typing invariant was unmeasured
# for that whole file. `SHAPE_FILES` above needs no matching widening and that is not an
# oversight: it is exactly the membrane's own `compile._TAB_SHAPE_FILES` (`compile.py:398`), and
# there is no `tab-datagrid-shapes.ttl`. So a data-grid class is a LIVE hazard only when one of
# these two files targets it, which is the question the split below actually asks.
ONT_FILES = ("tab.ttl", "tab-datagrid.ttl")


def typing_rules(ont: Graph):
    """(property, class) pairs that USED to type a node. Literal ranges cannot type, so drop."""
    domains = list(ont.subject_objects(RDFS.domain))
    ranges = [(p, c) for p, c in ont.subject_objects(RDFS.range)
              if not str(c).startswith(XSD_PREFIX)]
    return domains, ranges


def _key(kind: str, p, c) -> str:
    """The rule's report key. ONE definition, called by both `probe` and `rules_by_file` — a
    second copy of this format string would let attribution and counting drift apart silently,
    which is the R13-attempt-1 lesson (a checker that replicates the code instead of calling it
    checks nothing). Padding `kind` to 6 keeps the pre-widening key text byte-identical, so a
    `--json` tally from before this change is still comparable."""
    return f"{kind:6} {p.split('#')[-1]} -> {c.split('#')[-1]}"


def rules_by_file(vocab: str):
    """(merged ontology, {rule_key: the ONT_FILES entry that declares it}).

    The merge is what the closure and the probe run against — `tab-datagrid.ttl`'s own
    `rdfs:subClassOf` axioms have to be visible to `types_of`, or a node typed with a data-grid
    subclass would read as untyped and the probe would invent violations. The attribution map is
    what lets the summary answer R103's actual question: how many violations are attributable to
    `tab-datagrid.ttl`. A rule declared in both files is attributed to the first in ONT_FILES."""
    ont, src = Graph(), {}
    for f in ONT_FILES:
        g = Graph().parse(os.path.join(vocab, "ontology", f), format="turtle")
        domains, ranges = typing_rules(g)
        for kind, pairs in (("domain", domains), ("range", ranges)):
            for p, c in pairs:
                src.setdefault(_key(kind, p, c), f)
        ont += g
    return ont, src


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
                yield _key("domain", p, c), c, s
    for p, c in ranges:
        for o in set(graph.objects(None, p)):
            if not isinstance(o, Literal) and c not in types_of(graph, o, sup):
                yield _key("range", p, c), c, o


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the per-rule tally here")
    args = ap.parse_args()

    import pypdfium2 as pdfium
    from iladub.etkl import compile_tables

    vocab = os.path.join(ROOT, "vocab")
    ont, rule_src = rules_by_file(vocab)
    domains, ranges = typing_rules(ont)
    targets, sparql = shape_targets(vocab)
    sup = _closure(ont)
    per_file = collections.Counter(rule_src.values())
    print(f"{' + '.join(ONT_FILES)}: {len(domains)} domain rules, {len(ranges)} non-literal "
          f"range rules ({', '.join(f'{n} from {f}' for f, n in sorted(per_file.items()))}); "
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
    print(f"{'rule':40} {'nodes':>6}  targeted  sh:sparql  declared in")
    for key, n in counts.most_common():
        print(f"{key:40} {n:6}  {'YES' if cls_of[key] in targets else 'no ':8}  "
              f"{'YES' if cls_of[key] in sparql else 'no ':9}  {rule_src.get(key, '?')}"
              f"\n{'':6}e.g. {example[key]}")
    print(f"\ntotal violating nodes: {sum(counts.values())}")
    print(f"  on a shape-targeted class            : {live}")
    print(f"  on a class an sh:sparql shape targets: {live_sparql}   <-- the live hazard")

    # R103: the same split, per ontology file. Widening the probe is only worth anything if the
    # report can say what the widening FOUND, separately from what tab.ttl was already finding.
    print("\nby declaring ontology file (R103):")
    for f in ONT_FILES:
        ks = [k for k in counts if rule_src.get(k) == f]
        print(f"  {f:20} rules violated: {len(ks):3}  nodes: {sum(counts[k] for k in ks):6}"
              f"  live (shape-targeted): {sum(counts[k] for k in ks if cls_of[k] in targets):6}"
              f"  sh:sparql: {sum(counts[k] for k in ks if cls_of[k] in sparql):6}")

    if args.json:
        json.dump({k: {"nodes": n, "class": str(cls_of[k]), "example": example[k],
                       "shape_targeted": cls_of[k] in targets,
                       "sparql_targeted": cls_of[k] in sparql,
                       "declared_in": rule_src.get(k)}
                   for k, n in counts.items()}, open(args.json, "w"), indent=1, sort_keys=True)
    return 0 if live == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
