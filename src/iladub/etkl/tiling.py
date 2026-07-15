"""tiling — the SHACL-oracle region-admission gate (neurosymbolic loop C).

Tiling (coverage / no-overlap / refinement) is a CONFORMANCE check — closed-world — so it
belongs to SHACL, reusing the existing tab: tiling shapes (the closed-world mirror of loop B's
open-world SPARQL derivation). The ONLY Python here is PROCEDURAL engine glue: build the tiling
shapes subset once, and invoke pySHACL. No transform logic, no tuned constant. Irreducible
because a SHACL engine must be invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

import os

from rdflib import Graph, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")
_VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab")
_TILING_SHAPE_IRIS = [TAB.CoverageShape, TAB.NoOverlapShape, TAB.RefinementShape,
                      TAB.RowCoverageShape, TAB.RowNoOverlapShape, TAB.RowRefinementShape]


def _build_tiling_shapes():
    """The six tiling shapes extracted from the single tab-shapes.ttl as CBDs (+ tab:prefixes,
    which the sh:sparql shapes reference). Keeps ONE source of the shapes — no duplicate file."""
    full = Graph().parse(os.path.join(_VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    sub = Graph()
    for s in _TILING_SHAPE_IRIS + [TAB.prefixes]:
        sub += full.cbd(s)
    return sub


_TILING_SHAPES = _build_tiling_shapes()               # cached at import — parsed once
_ONT = Graph().parse(os.path.join(_VOCAB, "ontology", "tab.ttl"), format="turtle")


def region_tiles(graph):
    """True iff `graph` (one candidate region's RDF) conforms to the six tiling invariants
    (coverage / no-overlap / refinement, both axes). PROCEDURAL glue over the AXIOM shapes."""
    from pyshacl import validate
    conforms, _, _ = validate(graph, shacl_graph=_TILING_SHAPES, ont_graph=_ONT,
                              inference="rdfs", advanced=True)
    return conforms
