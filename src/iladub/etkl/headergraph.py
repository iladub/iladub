"""headergraph — the header-covering evidence graph + query runner (neurosymbolic loop B).

The LEAF header row's column covering is a declarative DERIVATION over per-cell ink extents and
per-column centers (open-world → SPARQL, the loop-B side of the gate; vocab/queries/header-covers.rq).
This module is the PROCEDURAL layer only: emitting the transient evidence graph and invoking rdflib.
No decision logic, no tuned constant — the covering decision lives entirely in header-covers.rq.
The band is the closure boundary: a fresh Graph() per call (mirrors classifygraph.py, loop B2c).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .grid import LeafGrid

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:header:")     # transient per-band instance namespace

# three dirs up from src/iladub/etkl/headergraph.py -> repo root, then vocab/queries/
HEADER_COVERS_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "header-covers.rq"


def header_evidence(header_rows: Sequence[Sequence[object]], grid: LeafGrid) -> Graph:
    """Fresh Graph() for one band's header region. `header_rows` is top-to-bottom; each cell exposes
    .text/.x0/.x1. Emits one tab:GridColumn per leaf column (colIndex, colCenterX, colX0, colX1) and
    one tab:HeaderCell per cell (atHeaderRow = row index, cellIndex = position in row, headerText,
    inkX0/inkX1, and inkCenterX = the label's ink midpoint). The leaf row is MAX(atHeaderRow)."""
    g = Graph()
    b = grid.boundaries
    for i in range(grid.ncols):
        col = URIRef(f"{_EV}col{i}")
        g.add((col, RDF.type, TAB.GridColumn))
        g.add((col, TAB.colIndex, Literal(i, datatype=XSD.integer)))
        g.add((col, TAB.colCenterX, Literal((b[i] + b[i + 1]) / 2.0, datatype=XSD.double)))
        g.add((col, TAB.colX0, Literal(float(b[i]), datatype=XSD.double)))
        g.add((col, TAB.colX1, Literal(float(b[i + 1]), datatype=XSD.double)))
    for r, row in enumerate(header_rows):
        for j, cell in enumerate(row):
            hc = URIRef(f"{_EV}r{r}c{j}")
            g.add((hc, RDF.type, TAB.HeaderCell))
            g.add((hc, TAB.atHeaderRow, Literal(r, datatype=XSD.integer)))
            g.add((hc, TAB.cellIndex, Literal(j, datatype=XSD.integer)))
            g.add((hc, TAB.headerText, Literal(cell.text)))
            g.add((hc, TAB.inkX0, Literal(float(cell.x0), datatype=XSD.double)))
            g.add((hc, TAB.inkX1, Literal(float(cell.x1), datatype=XSD.double)))
            # The label's ink center is raw geometry (PROCEDURAL); the DECISION of which column
            # contains it stays in header-covers.rq (keeping the query free of numeric literals).
            g.add((hc, TAB.inkCenterX, Literal((float(cell.x0) + float(cell.x1)) / 2.0, datatype=XSD.double)))
    return g


def run_covers(rq_path, graph: Graph) -> dict:
    """Run header-covers.rq; return {(header_row_index, cell_index): tuple(sorted col indices)} for
    the LEAF row only (the query returns matches only, so cells covering no column are absent)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    out: dict[tuple[int, int], list[int]] = {}
    for row in graph.query(q):
        key = (int(row.hrow), int(row.cellIdx))
        out.setdefault(key, []).append(int(row.cidx))
    return {k: tuple(sorted(v)) for k, v in out.items()}
