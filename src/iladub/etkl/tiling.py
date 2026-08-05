"""tiling — the SHACL-oracle region-admission gate (neurosymbolic loop C).

Tiling (coverage / no-overlap / refinement) is a CONFORMANCE check — closed-world — so it
belongs to SHACL, reusing the existing tab: tiling shapes (the closed-world mirror of loop B's
open-world SPARQL derivation). The gate also carries the two physical shapes (R19, 2026-08-05):
a physical-shape defect must refuse HERE, not crash compile.py's final whole-graph validation.
The ONLY Python here is PROCEDURAL engine glue: build the tiling + physical shapes subset once,
and invoke pySHACL. No transform logic, no tuned constant. Irreducible because a SHACL engine
must be invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

import os

from rdflib import Graph, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")
_VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab")
# The eleven tiling invariants: the original eight (loop C, 2026-07-16) + the ninth,
# tab:HeaderContentConservedShape, the header-content conservation oracle (loop C of the
# GrainCorp push, 2026-07-26) + the tenth, tab:DetectedAggregationRowShape, the detected-
# aggregation evidence oracle (loop H, 2026-07-30) + the eleventh, tab:DerivedRowGroupShape,
# the derived-row-group well-formedness oracle (loop I, 2026-07-30) — our OWN emission
# (assert_hier_region / derive_row_groups) must be gated here at the region, not crash at
# compile.py's final full-graph validation (the loop G lesson). One pySHACL call carries all
# four families; the conservation shape targets tab:HeaderSourceCell, the aggregation shape
# targets tab:DetectedAggregationRow, and the row-group shape targets tab:DerivedRowGroup, none
# of which any pre-existing region emits, so every previously-shipped region is unaffected.
_TILING_SHAPE_IRIS = [TAB.CoverageShape, TAB.NoOverlapShape, TAB.RefinementShape,
                      TAB.RowCoverageShape, TAB.RowNoOverlapShape, TAB.RowRefinementShape,
                      TAB.UnambiguousAccessShape, TAB.UnambiguousRowAccessShape,
                      TAB.HeaderContentConservedShape, TAB.DetectedAggregationRowShape,
                      TAB.DerivedRowGroupShape]

# R19 closure (2026-08-05): the TWO physical shapes join the gate. Measured activation:
# apple-fy2026q3 p1#mtable4 (matrix cells with bbox + empty cellText) crashed compile at
# final validation THROUGH this gate; the physical shapes were only in compile._validate's
# full set. Region defects expressible in the physical layer now refuse HERE, so every
# path's existing escalation branch handles them (never crash, always at worst escalate).
_PHYSICAL_SHAPE_IRIS = [TAB.EntryCellPhysicalShape, TAB.WrappedCellShape]


def _build_tiling_shapes():
    """The eleven tiling invariants + the two physical shapes (R19) (the original eight +
    tab:HeaderContentConservedShape + tab:DetectedAggregationRowShape +
    tab:DerivedRowGroupShape + tab:EntryCellPhysicalShape + tab:WrappedCellShape), extracted
    from tab-shapes.ttl + tab-physical-shapes.ttl as CBDs (+ tab:prefixes, which the
    sh:sparql shapes reference). Keeps ONE source of the shapes — no duplicate file. Includes
    Unambiguous(Row)AccessShape: exactly one LEAF header per column/row — the leaf-partition
    invariant the retired exact-partition Python backstops enforced."""
    full = Graph().parse(os.path.join(_VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    full.parse(os.path.join(_VOCAB, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    sub = Graph()
    for s in _TILING_SHAPE_IRIS + _PHYSICAL_SHAPE_IRIS + [TAB.prefixes]:
        sub += full.cbd(s)
    return sub


_TILING_SHAPES = _build_tiling_shapes()               # cached at import — parsed once
_ONT = Graph().parse(os.path.join(_VOCAB, "ontology", "tab.ttl"), format="turtle")


def region_tiles(graph):
    """True iff `graph` (one candidate region's RDF) conforms to the eleven tiling invariants
    + the two physical shapes (R19) (coverage / no-overlap / refinement / unambiguous-leaf-
    access, both axes, + header-content conservation + detected-aggregation evidence +
    derived-row-group well-formedness + entry-cell/wrapped-cell physical well-formedness).
    PROCEDURAL glue over the AXIOM shapes."""
    from pyshacl import validate
    conforms, _, _ = validate(graph, shacl_graph=_TILING_SHAPES, ont_graph=_ONT,
                              inference="rdfs", advanced=True)
    return conforms
