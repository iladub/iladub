#!/usr/bin/env python
"""probe_domain_range_agreement — do the emitters and the tab ontology agree about types?

WHY THIS EXISTS. 2026-08-06's subclass-only closure made every `rdfs:domain`/`rdfs:range`
rule in the tab ontology (`ONT_FILES` below) inert *for typing purposes*. Each of those rules used
to be a path by which a node entered a shape's target set without an explicit `rdf:type`. Since
then, every shape's reach depends entirely on emitters typing every node explicitly (R61) — and
nothing enforced that invariant. This probe was built to enforce it.

WHAT IT ACTUALLY FOUND, AND WHY IT WAS RENAMED (2026-08-18). Measured over 27 corpus pages:
74 violations, of which **0** are a node missing its type. The invariant the old name claimed to
police has never once been observed to fail here. Every violation is one of three other things —
so the probe reports four classes and only two of them may gate:

  UNTYPED          the node carries no type in the page graph and none in any ontology.
                   R61's actual subject. Currently 0 of 74; a non-zero here is new news.
  DISAGREE         the node IS typed — just not as the domain/range rule says. The emitter and
                   the vocabulary contradict each other, which is a MODELLING decision, not a
                   forgotten `rdf:type`. Currently 60 of 74, 14 of them on a shape-targeted class.
  ONT_VISIBLE      the type is supplied by the membrane's own ontology (`MEMBRANE_ONT_FILES`,
                   mirroring `compile._FULL_ONT`). The membrane validates page graph + that
                   ontology, so it sees the type and there is no hazard. A false positive of the
                   page-graph-only reading. Currently 2 of 74.
  OUTSIDE_MEMBRANE the type is supplied ONLY by a vocabulary file the membrane never loads.
                   Currently 12 of 74 — the six `tab:GridAxiom` individuals, declared in
                   `tab-datagrid.ttl`, which `compile._FULL_ONT` does not parse. NOT a false
                   positive: it is evidence for R103's open membrane question. Reported, does
                   not gate (no shape targets those classes today).

The distinction between the last two is why `types_of` still reads the PAGE GRAPH ONLY and the
ontology is consulted separately, by name. Folding the ontology into `types_of` would collapse
ONT_VISIBLE and OUTSIDE_MEMBRANE into one silent "fine", discarding the R103 evidence.

WHY THE SCORE GATE CANNOT SUBSTITUTE FOR THIS. A lost or disagreeing type means a shape stops
seeing a node. The region it would have refused is then admitted, so the failure appears as a
region flipping escalated -> asserted: a score **improvement**. The corpus score gate cannot
distinguish that from a real fix. Only this probe can.

HOW TO READ THE OUTPUT. A violation is only a LIVE hazard when it is UNTYPED or DISAGREE *and*
its class is one some shape targets — otherwise the missing typing removes the node from nobody's
reach. The `sh:sparql` column is the sharpest form: those shapes are the ones whose constraints
silently stop applying.

Gate classification (CLAUDE.md §8): PROCEDURAL measurement harness. It makes no domain decision —
the decisions are the ontology's domain/range rules and the membrane's ontology list, which this
only applies and counts. No tuned constant, tolerance or threshold appears here.

Usage:
    ./.venv/bin/python scripts/probe_domain_range_agreement.py [--json OUT]

Exit code 0 when no UNTYPED/DISAGREE violation lands on a shape-targeted class, non-zero
otherwise — so it can be used as a gate once R61's modelling question is settled.
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

# The ontology the MEMBRANE validates against — `compile.py:441-454` builds `_FULL_ONT` from
# exactly these three and nothing else. It is deliberately NOT `ONT_FILES`: the difference
# between the two lists is what separates ONT_VISIBLE from OUTSIDE_MEMBRANE, so a drift here
# would silently reclassify. `tests/test_probe_domain_range_agreement.py` pins the mirroring.
MEMBRANE_ONT_FILES = ("tab.ttl", "dec.ttl", "iladub.ttl")

UNTYPED = "UNTYPED"
DISAGREE = "DISAGREE"
ONT_VISIBLE = "ONT-VISIBLE"
OUTSIDE_MEMBRANE = "OUTSIDE-MEMBRANE"
CLASSES = (UNTYPED, DISAGREE, ONT_VISIBLE, OUTSIDE_MEMBRANE)
GATING = (UNTYPED, DISAGREE)


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


def lookup_graphs(vocab: str):
    """(membrane ontology, wider probe ontology) — the two graphs a violation is classified
    against. The wider one is a superset by construction, so `ONT_VISIBLE => OUTSIDE_MEMBRANE`
    can never both be true and the order in `classify` is the only thing that decides."""
    membrane = Graph()
    for f in MEMBRANE_ONT_FILES:
        membrane.parse(os.path.join(vocab, "ontology", f), format="turtle")
    wider = Graph()
    wider += membrane
    for f in ONT_FILES:
        wider.parse(os.path.join(vocab, "ontology", f), format="turtle")
    return membrane, wider


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


def classify(cls, page_types, membrane_types, wider_types) -> str:
    """Which of the four findings this violation is. Total and mutually exclusive over CLASSES.

    `wider_types` is a superset of `membrane_types` (see `lookup_graphs`), so the first two tests
    are ordered deliberately: a type the membrane can see is never reported as outside it."""
    if cls in membrane_types:
        return ONT_VISIBLE
    if cls in wider_types:
        return OUTSIDE_MEMBRANE
    if not page_types and not wider_types:
        return UNTYPED
    return DISAGREE


def classified(graph: Graph, domains, ranges, sup, membrane: Graph, wider: Graph, cache=None):
    """Yield (rule_key, class, node, finding-class) for every violation `probe` reports.

    `cache` memoises the two ONTOLOGY lookups across pages — the ontology does not change between
    them, and without it the corpus run repeats the same traversal 27 times. The PAGE lookup is
    never cached: it is a different graph each call."""
    cache = {} if cache is None else cache
    for key, cls, node in probe(graph, domains, ranges, sup):
        if node not in cache:
            cache[node] = (types_of(membrane, node, sup), types_of(wider, node, sup))
        membrane_types, wider_types = cache[node]
        yield key, cls, node, classify(cls, types_of(graph, node, sup), membrane_types, wider_types)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the per-rule tally here")
    args = ap.parse_args()

    import pypdfium2 as pdfium
    from iladub.etkl import compile_tables

    vocab = os.path.join(ROOT, "vocab")
    ont, rule_src = rules_by_file(vocab)
    domains, ranges = typing_rules(ont)
    membrane_ont, wider_ont = lookup_graphs(vocab)
    targets, sparql = shape_targets(vocab)
    sup = _closure(ont)
    per_file = collections.Counter(rule_src.values())
    print(f"{' + '.join(ONT_FILES)}: {len(domains)} domain rules, {len(ranges)} non-literal "
          f"range rules ({', '.join(f'{n} from {f}' for f, n in sorted(per_file.items()))}); "
          f"{len(targets)} shape-targeted classes ({len(sparql)} of them sh:sparql)")
    print(f"membrane ontology (mirrors compile._FULL_ONT): {' + '.join(MEMBRANE_ONT_FILES)}")

    counts, example, cls_of, pages, cache = collections.Counter(), {}, {}, 0, {}
    for path in sorted(glob.glob(os.path.join(ROOT, "corpus", "*", "*.pdf"))):
        doc = pdfium.PdfDocument(path)
        n = len(doc)
        doc.close()
        for pg in range(n):
            rep = compile_tables(path, page_number=pg, validate_shapes=False)
            pages += 1
            for key, cls, node, klass in classified(
                    rep.graph, domains, ranges, sup, membrane_ont, wider_ont, cache):
                counts[(key, klass)] += 1
                cls_of[key] = cls
                example.setdefault((key, klass), f"{os.path.basename(path)} p{pg}: {node}")

    live = sum(n for (k, klass), n in counts.items()
               if klass in GATING and cls_of[k] in targets)
    live_sparql = sum(n for (k, klass), n in counts.items()
                      if klass in GATING and cls_of[k] in sparql)

    print(f"\npages probed: {pages}")
    print(f"{'rule':40} {'finding':>16} {'nodes':>6}  targeted  sh:sparql  declared in")
    for (key, klass), n in counts.most_common():
        print(f"{key:40} {klass:>16} {n:6}  {'YES' if cls_of[key] in targets else 'no ':8}  "
              f"{'YES' if cls_of[key] in sparql else 'no ':9}  {rule_src.get(key, '?')}"
              f"\n{'':6}e.g. {example[(key, klass)]}")

    print(f"\ntotal violating nodes: {sum(counts.values())}")
    for klass in CLASSES:
        n = sum(v for (_k, kl), v in counts.items() if kl == klass)
        note = "" if klass in GATING else "   (never gates)"
        print(f"  {klass:18}: {n:5}{note}")
    print(f"\n  {'/'.join(GATING)} on a shape-targeted class            : {live}")
    print(f"  {'/'.join(GATING)} on a class an sh:sparql shape targets: {live_sparql}"
          f"   <-- the live hazard")

    # R103: the same split, per ontology file. Widening the probe is only worth anything if the
    # report can say what the widening FOUND, separately from what tab.ttl was already finding.
    print("\nby declaring ontology file (R103):")
    print(f"  {'file':22} {'total':>6} " + " ".join(f"{c:>16}" for c in CLASSES)
          + f" {'live':>6} {'sh:sparql':>10}")
    for f in ONT_FILES:
        ks = [(k, kl) for (k, kl) in counts if rule_src.get(k) == f]
        per = [sum(counts[(k, kl)] for (k, kl) in ks if kl == c) for c in CLASSES]
        print(f"  {f:22} {sum(counts[k] for k in ks):6} " + " ".join(f"{n:16}" for n in per)
              + f" {sum(counts[(k, kl)] for (k, kl) in ks if kl in GATING and cls_of[k] in targets):6}"
              + f" {sum(counts[(k, kl)] for (k, kl) in ks if kl in GATING and cls_of[k] in sparql):10}")

    if args.json:
        json.dump({f"{klass} | {k}": {"nodes": n, "finding": klass, "class": str(cls_of[k]),
                                      "example": example[(k, klass)],
                                      "shape_targeted": cls_of[k] in targets,
                                      "sparql_targeted": cls_of[k] in sparql,
                                      "gates": klass in GATING,
                                      "declared_in": rule_src.get(k)}
                   for (k, klass), n in counts.items()}, open(args.json, "w"),
                  indent=1, sort_keys=True)
    return 0 if live == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
