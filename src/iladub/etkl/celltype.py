"""celltype — the typed-cell evidence graph + query runner (neurosymbolic loop B2a).

The type/orientation boundary decisions (header/body split, stub/data split, transpose) are
declarative DERIVATIONS over per-cell datatype facts (open-world → SPARQL, the loop-B side of the
gate). This module is the PROCEDURAL layer only: raw datatype typing (via is_numeric), emitting the
transient typed-cell evidence graph, and invoking rdflib. No decision logic, no tuned constant —
the decisions live entirely in vocab/queries/*.rq (AXIOM). Irreducible: a SPARQL engine must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

from .headers import is_numeric

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")


def grid_evidence(cells, ncols):
    """Build the transient typed-cell evidence graph. `cells`: iterable of (row, col, text).
    Emits a tab:GridCell per cell (row/col/text/cellDatatype) + a column marker per index."""
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["cell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, TAB.Numeric if is_numeric(t) else TAB.Text))
    for c in range(ncols):
        g.add((_EV["col-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    return g


def run_scalar(rq_path, graph, bindings=None):
    """Run a SELECT that returns a single integer variable; return int or None (empty result)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    for row in graph.query(q, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None


def run_ask(rq_path, graph):
    """Run an ASK; return bool."""
    q = Path(rq_path).read_text(encoding="utf-8")
    return bool(graph.query(q).askAnswer)
