"""holon — map classified regions to RDF: assert faithful structure, propose the rest.

Assert: a tab: RecordTable with columns/rows/single-level header + EntryCells
carrying text, page, bbox and prov:wasDerivedFrom (structural facts; domain
grounding is a later loop, so no PromotionDecision here).
Propose: an iladub:CandidateConcept for regions the loop cannot validate.
"""
from __future__ import annotations

from rdflib import Graph, Namespace, Literal, BNode, URIRef, RDF
from rdflib.namespace import XSD

from .regions import ClassifiedRegion
from .roundtrip import cell_round_trips

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _bbox_node(g: Graph, cell) -> BNode:
    x0, y0, x1, y1 = cell.bbox
    n = BNode()
    g.add((n, RDF.type, TAB.BBox))
    g.add((n, TAB.x0, Literal(round(x0, 2), datatype=XSD.decimal)))
    g.add((n, TAB.y0, Literal(round(y0, 2), datatype=XSD.decimal)))
    g.add((n, TAB.x1, Literal(round(x1, 2), datatype=XSD.decimal)))
    g.add((n, TAB.y1, Literal(round(y1, 2), datatype=XSD.decimal)))
    return n


def _region_uri(base: URIRef, kind: str, idx: int) -> URIRef:
    return URIRef(f"{base}-{kind}{idx}")


def assert_record_region(g: Graph, region: ClassifiedRegion, table_uri: URIRef,
                         doc_uri: URIRef, page: int) -> int:
    g.add((table_uri, RDF.type, TAB.RecordTable))
    ncols = region.grid.ncols
    cols = {i: _region_uri(table_uri, "c", i) for i in range(ncols)}
    for i, c in cols.items():
        g.add((c, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, c))
        h = _region_uri(table_uri, "h", i)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, c))
        g.add((table_uri, TAB.hasHeaderNode, h))

    data_rows = sorted({cell.row for cell in region.cells if cell.row > 0})
    rows = {r: _region_uri(table_uri, "r", r) for r in data_rows}
    for r in rows.values():
        g.add((r, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, r))

    asserted = 0
    b = region.grid.boundaries
    for cell in region.cells:
        if cell.row == 0:
            continue  # header labels are structural, not scored facts
        if not cell_round_trips(cell, b):
            continue  # a straddling cell is not asserted (would be escalated per-cell)
        e = _region_uri(table_uri, f"e{cell.row}_", cell.col)
        g.add((e, RDF.type, TAB.EntryCell))
        g.add((table_uri, TAB.hasCell, e))
        g.add((e, TAB.atColumn, cols[cell.col]))
        g.add((e, TAB.atRow, rows[cell.row]))
        g.add((e, TAB.cellText, Literal(cell.text)))
        g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
        g.add((e, TAB.hasBBox, _bbox_node(g, cell)))
        x0, top, _, _ = cell.bbox
        g.add((e, PROV.wasDerivedFrom,
               URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))
        asserted += 1
    return asserted


def escalate_region(g: Graph, cand_uri: URIRef, doc_uri: URIRef, ascii_text: str,
                    reason: str, anchor: URIRef, confidence: float) -> None:
    g.add((cand_uri, RDF.type, ILADUB.CandidateConcept))
    g.add((cand_uri, ILADUB.surfaceText, Literal(ascii_text)))
    g.add((cand_uri, ILADUB.suggestedAnchor, anchor))
    g.add((cand_uri, DEC.confidence, Literal(round(confidence, 2), datatype=XSD.decimal)))
    g.add((cand_uri, DEC.rationale, Literal(reason)))
    g.add((cand_uri, PROV.wasDerivedFrom, doc_uri))
