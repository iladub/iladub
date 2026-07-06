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
            # header label: carry its text + geometry (context is not discarded)
            # and link it to its column's HeaderNode. LabelCells are structural,
            # not scored facts.
            lc = _region_uri(table_uri, "lc", cell.col)
            g.add((lc, RDF.type, TAB.LabelCell))
            g.add((table_uri, TAB.hasCell, lc))
            g.add((lc, TAB.cellText, Literal(cell.text)))
            g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
            g.add((lc, TAB.hasBBox, _bbox_node(g, cell)))
            g.add((_region_uri(table_uri, "h", cell.col), TAB.hasLabel, lc))
            continue
        if not cell_round_trips(cell, b):
            # residue: a data cell whose ink crosses a gutter is NOT asserted.
            # Emit it as an in-band proposition — never silently dropped.
            cc = _region_uri(table_uri, f"cc{cell.row}_", cell.col)
            x0, top, _, _ = cell.bbox
            g.add((cc, RDF.type, ILADUB.CandidateConcept))
            g.add((cc, ILADUB.surfaceText, Literal(cell.text)))
            g.add((cc, DEC.rationale, Literal("ROUND_TRIP_FAIL")))
            g.add((cc, TAB.onPage, Literal(page, datatype=XSD.integer)))
            g.add((cc, TAB.hasBBox, _bbox_node(g, cell)))
            g.add((cc, PROV.wasDerivedFrom,
                   URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))
            continue
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


def assert_hier_region(g: Graph, region, band, table_uri: URIRef,
                       doc_uri: URIRef, page: int) -> int:
    """Emit a tab:HierarchicalTable holon for a HierRegion; return asserted body-token count.

    Orphan promotion: any HeaderNode with parent=None is a root regardless of the
    syntactic level it appears at in the header-row sequence. Such nodes are emitted
    at level 0 — exactly as the conformant example (hierarchical-conformant.ttl) shows
    for the stub Analyte column. This makes the tiling CoverageShape + NoOverlapShape
    + RefinementShape + UnambiguousAccessShape invariants provably satisfy for any
    hierarchical tree that has stub columns with no merged-group parent.

    If region_round_trips is False, escalates the whole region (ROUND_TRIP_FAIL)
    and returns 0.
    """
    from .roundtrip import region_round_trips, render_region_ascii
    from .regions import column_of

    if not region_round_trips(region, band):
        rt_uri = URIRef(f"{table_uri}-rt")
        escalate_region(g, rt_uri, doc_uri, render_region_ascii(region),
                        "ROUND_TRIP_FAIL", TAB.HierarchicalTable, 0.3)
        return 0

    g.add((table_uri, RDF.type, TAB.HierarchicalTable))

    # Leaf columns
    ncols = region.grid.ncols
    cols = {i: URIRef(f"{table_uri}-c{i}") for i in range(ncols)}
    for i, c in cols.items():
        g.add((c, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, c))

    # Header tree — orphan-promotion: nodes with parent=None are level-0 roots.
    # This is the general fix for stub columns (a column whose label spans no merged
    # group above it): emitting them at level 0 matches the conformant example and
    # satisfies CoverageShape (covered at ≥ 1 level) + NoOverlapShape (no same-level
    # overlap) + UnambiguousAccessShape (exactly one leaf-header per column, since the
    # stub's level-0 node has no children and is its own leaf-header).
    node_uris = {}
    for idx, n in enumerate(region.tree):
        h = URIRef(f"{table_uri}-h{idx}")
        node_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        # Orphan-promotion: a node with no parent is always a root (level 0).
        effective_level = 0 if n.parent is None else n.level
        g.add((h, TAB.headerLevel, Literal(effective_level, datatype=XSD.integer)))
        for col in n.covers:
            g.add((h, TAB.coversColumn, cols[col]))
        # LabelCell carries the header text + provenance context
        lc = URIRef(f"{table_uri}-hl{idx}")
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(n.text)))
        g.add((h, TAB.hasLabel, lc))

    # Parent links — using effective URIs (promotion doesn't affect parent-pointer logic)
    for idx, n in enumerate(region.tree):
        if n.parent is not None:
            g.add((node_uris[idx], TAB.parentHeader, node_uris[n.parent]))

    # Leaf rows
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))

    # Body entry cells
    b = region.grid.boundaries
    asserted = 0
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        for cell in rb.cells:
            col = column_of((cell.x0 + cell.x1) / 2.0, b)
            e = URIRef(f"{table_uri}-e{r}_{col}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((table_uri, TAB.hasCell, e))
            g.add((e, TAB.atColumn, cols[col]))
            g.add((e, TAB.atRow, row_uri))
            g.add((e, TAB.cellText, Literal(cell.text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(round(cell.x0, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(round(cell.top, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.x1, Literal(round(cell.x1, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.y1, Literal(round(cell.bottom, 2), datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom,
                   URIRef(f"{doc_uri}#p{page}-{int(cell.x0)}-{int(cell.top)}")))
            asserted += len(cell.words)

    return asserted
