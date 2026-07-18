"""flankgraph — header-cell evidence graph + sibling-column query runner (loop B1.2).

The narrow-flank *resolution* (is a tied flank a same-level sibling leaf?) is a declarative
DERIVATION over a per-band header-cell evidence graph (open-world -> SPARQL; the band is the
closure boundary). This module is the PROCEDURAL layer only: geometric containment (via the
unchanged regions._word_in_column), emitting the transient graph, and invoking rdflib. No
decision logic, no tuned constant -- the sibling decision lives entirely in
vocab/queries/flank-sibling.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

# three dirs up from src/iladub/etkl/flankgraph.py -> repo root, then vocab/queries/
FLANK_SIBLING_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "flank-sibling.rq"


def _strictly_in_column(x0: float, x1: float, boundaries: Sequence[float]) -> int | None:
    """The unique leaf column the cell ink [x0,x1] is strictly inside, or None if it straddles
    a gutter. Uses the unchanged regions._word_in_column (a lightweight shim word carries x0/x1).

    PROCEDURAL: exact geometric containment (raw extraction), irreducible to AXIOM/NEURAL.
    """
    # Call-time import: regions <-> headers/flankgraph form an import cycle; both modules are
    # fully loaded by the time any band is resolved (mirrors classifygraph._strictly_in_column).
    from .regions import _word_in_column
    from types import SimpleNamespace
    w = SimpleNamespace(x0=x0, x1=x1)
    for c in range(len(boundaries) - 1):
        if _word_in_column(w, c, boundaries):
            return c
    return None


def flank_evidence(header_cells, boundaries) -> Graph:
    """Emit the transient header-cell evidence graph.

    header_cells: iterable of (level:int, x0:float, x1:float, text:str) for each populated
    header cell across all header rows. Each becomes a tab:HeaderCell with tab:headerLevel and,
    when strictly inside one leaf column, tab:strictlyInColumn.
    """
    g = Graph()
    for i, (level, x0, x1, text) in enumerate(header_cells):
        u = _EV["hc-%d" % i]
        g.add((u, RDF.type, TAB.HeaderCell))
        g.add((u, TAB.headerLevel, Literal(int(level), datatype=XSD.integer)))
        col = _strictly_in_column(x0, x1, boundaries)
        if col is not None:
            g.add((u, TAB.strictlyInColumn, Literal(int(col), datatype=XSD.integer)))
    return g


# sibling_columns (runs FLANK_SIBLING_RQ over flank_evidence) is Task 3 -- the query file at
# FLANK_SIBLING_RQ does not exist yet.
