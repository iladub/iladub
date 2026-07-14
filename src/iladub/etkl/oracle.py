"""oracle — the round-trip reproduction oracle (loop one, SPARQL executor).

A recipe is certified iff running the FORWARD reshape CONSTRUCTs over the derived base
(a hproj:Projection RDF graph) regenerates the original grid cell values exactly. The
transform is AXIOM (standard SPARQL CONSTRUCT + SPARQL 1.1 aggregates in vocab/queries/);
the ONLY Python here is the exact-equality compare (_close / _TOL), which is decidable
arithmetic and irreducible (PYTHON-OK).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Namespace, RDF

from . import interpret
from .recipe import UnpivotOp, StripAggregationOp

TAB = Namespace("https://w3id.org/iladub/tab#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")
_TOL = 1e-6                    # PYTHON-OK: decidable exact-equality tolerance for the compare,
                              # NOT a transform tuning constant. It never enters the .rq files.


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


def _isnum(s):
    try:
        float(s); return True
    except (TypeError, ValueError):
        return False


@dataclass(frozen=True)
class OracleVerdict:
    ok: bool
    residue: tuple


def _repro_grid(base, recipe):
    """Run the forward CONSTRUCTs over the derived base -> {(row_label, col_label): text}."""
    from .reshape import _materialize_recipe   # local import avoids a cycle
    from rdflib import URIRef, Graph
    recipe_graph = Graph()
    _materialize_recipe(recipe_graph, URIRef("urn:reshape:t"), recipe)
    # 1. unpivot forward: base -> repro measure + stub cells
    grid = interpret.run(os.path.join(_QUERIES, "unpivot-forward.rq"), base, recipe_graph)
    # 2. strip forward (sum): re-add aggregate rows/cols over the repro grid, ordered by opIndex
    strips = [op for op in recipe.operations if isinstance(op, StripAggregationOp)]
    if strips:
        added = interpret.run(os.path.join(_QUERIES, "strip-aggregation-forward-sum.rq"),
                              grid, recipe_graph)
        grid += added
    out = {}
    for cell in grid.subjects(RDF.type, TAB.ReproCell):
        rrow = str(grid.value(cell, TAB.reproRow))
        rcol = str(grid.value(cell, TAB.reproCol))
        out[(rrow, rcol)] = str(grid.value(cell, TAB.reproText))
    return out


def round_trip(original, base, recipe):
    """Run the forward reshape CONSTRUCTs over `base` (the derived hproj:Projection graph)
    and exact-compare to `original` (from grid_values). Numeric cells compare with tolerance;
    text cells compare literally. Signature unchanged from the Python-replay era."""
    repro = _repro_grid(base, recipe)
    residue = []
    for key, want in original.items():
        got = repro.get(key)
        if got is None:
            residue.append("missing %r (want %r)" % (key, want)); continue
        if _isnum(want) and _isnum(got):
            if not _close(float(got), float(want)):
                residue.append("mismatch %r: want %s got %s" % (key, want, got))
        elif got != want:
            residue.append("mismatch %r: want %r got %r" % (key, want, got))
    for key in repro:
        if key not in original:
            residue.append("extra %r = %r" % (key, repro[key]))
    return OracleVerdict(not residue, tuple(residue))
