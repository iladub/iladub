"""holon — map classified regions to RDF: assert faithful structure, propose the rest.

Assert: a tab: RecordTable with columns/rows/single-level header + EntryCells
carrying text, page, bbox and prov:wasDerivedFrom (structural facts; domain
grounding is a later loop, so no PromotionDecision here).
Propose: an iladub:CandidateConcept for regions the loop cannot validate.
"""
from __future__ import annotations

from decimal import Decimal

from rdflib import Graph, Namespace, Literal, BNode, URIRef, RDF, RDFS
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


def _emit_entry_cell(g: Graph, table_uri: URIRef, doc_uri: URIRef, page: int,
                     e_uri: URIRef, col_uri: URIRef, row_uri: URIRef, cell) -> None:
    """Emit one tab:EntryCell with structural links + provenance. Shared by the
    upright and transposed makers so provenance is single-sourced."""
    g.add((e_uri, RDF.type, TAB.EntryCell))
    g.add((table_uri, TAB.hasCell, e_uri))
    g.add((e_uri, TAB.atColumn, col_uri))
    g.add((e_uri, TAB.atRow, row_uri))
    g.add((e_uri, TAB.cellText, Literal(cell.text)))
    g.add((e_uri, TAB.onPage, Literal(page, datatype=XSD.integer)))
    g.add((e_uri, TAB.hasBBox, _bbox_node(g, cell)))
    x0, top, _, _ = cell.bbox
    g.add((e_uri, PROV.wasDerivedFrom,
           URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))


def _emit_roundtrip_fail_cell(g: Graph, doc_uri: URIRef, page: int,
                              cc_uri: URIRef, cell) -> None:
    """Emit a ROUND_TRIP_FAIL proposition for a data cell whose ink crosses a
    gutter — never silently dropped. Shared by both makers.

    Gate classification (CLAUDE.md §8): PROCEDURAL, as `escalate_region` — it records a
    refusal the round-trip oracle has already made.

    THE SECOND R69 SITE, and R19's root cause. This emitter wrote `dec:rationale` on a
    proposition (R69's mechanism: `dec:rationale rdfs:domain dec:DecisionHolon`,
    dec.ttl:76-77) AND `tab:onPage` + `tab:hasBBox` on it (R19's mechanism: both declare
    `rdfs:domain tab:Cell`, tab.ttl:103-107, so the proposition became a `tab:Cell` and was
    handed to every cell shape). Spec 2026-08-06 stopped the SHIPPED closure materialising
    domain typing, which stopped R19 crashing compiles — but the cell vocabulary is still IN
    the published graph, so it still fires for any consumer applying our axioms. Dropping the
    vocabulary closes it at the source rather than at the closure.

    THE BBOX IS NOT CARRIED, and that is a measured loss, not an oversight. `tab:hasBBox`
    cannot hang off a proposition without retyping it (above), and there is no owned property
    for geometry on an `iladub:SourceRegion`. `prov:wasDerivedFrom` still pins the cell's
    origin (its IRI encodes x0/top), and the loss is registered rather than papered over with
    an invented term.
    """
    x0, top, _, _ = cell.bbox
    region_uri = URIRef(f"{cc_uri}-source")
    agent = _suggester_uri("ROUND_TRIP_FAIL")

    g.add((cc_uri, RDF.type, ILADUB.CandidateConcept))
    g.add((cc_uri, ILADUB.surfaceText, Literal(cell.text)))
    # The anchor is the reading the maker ATTEMPTED and the oracle refused — not a guess:
    # this branch is reached only from the entry-cell path.
    g.add((cc_uri, ILADUB.suggestedAnchor, TAB.EntryCell))
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cc_uri, ILADUB.suggestedBy, agent))
    # 0.0 because the round-trip oracle REFUTED this reading — no confidence is claimed, and
    # none is invented. Shipped precedent for the same epistemic situation: compile.py's
    # DATAGRID_RESIDUE escalation, also 0.0. Not a tuned constant: it is the "none" boundary.
    g.add((cc_uri, ILADUB.confidence, Literal(Decimal("0.0"))))
    g.add((cc_uri, RDFS.label, Literal("ROUND_TRIP_FAIL")))
    g.add((cc_uri, ILADUB.status, ILADUB.proposed))
    g.add((cc_uri, ILADUB.fromRegion, region_uri))
    # UNCHANGED: adoption-candidate.rq binds ?doc from this edge — do not repoint it.
    g.add((cc_uri, PROV.wasDerivedFrom,
           URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))

    g.add((region_uri, RDF.type, ILADUB.SourceRegion))
    g.add((region_uri, ILADUB.onPage, Literal(int(page), datatype=XSD.integer)))
    g.add((region_uri, PROV.wasDerivedFrom,
           URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))


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
            cc = _region_uri(table_uri, f"cc{cell.row}_", cell.col)
            _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
            continue
        e = _region_uri(table_uri, f"e{cell.row}_", cell.col)
        _emit_entry_cell(g, table_uri, doc_uri, page, e, cols[cell.col], rows[cell.row], cell)
        asserted += 1
    return asserted


def assert_transposed_region(g: Graph, region: ClassifiedRegion, table_uri: URIRef,
                             doc_uri: URIRef, page: int) -> int:
    """Compile a detected transposed region into an un-inverted tab:RecordTable by
    axis-flip. The flip is a LOGICAL relabel over unmoved physical cells: logical
    column k <- physical row k (header label = cell (k,0)); logical row m <-
    physical column m>=1; EntryCell (row m, col k) <- physical cell (row k, col m),
    carrying that cell's own words so bbox/page/provenance are the true physical
    measurement, never a flipped coordinate. Certification is the SAME per-cell
    round-trip on the ORIGINAL grid; straddling cells escalate ROUND_TRIP_FAIL.
    Returns the asserted EntryCell count.
    """
    g.add((table_uri, RDF.type, TAB.RecordTable))
    g.add((table_uri, TAB.sourceOrientation, Literal("transposed")))
    b = region.grid.boundaries

    by_rc = {(c.row, c.col): c for c in region.cells}
    phys_rows = sorted({c.row for c in region.cells})              # -> logical columns
    phys_cols = sorted({c.col for c in region.cells if c.col >= 1})  # -> logical rows

    cols = {}
    for k in phys_rows:
        col_uri = _region_uri(table_uri, "c", k)
        cols[k] = col_uri
        g.add((col_uri, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, col_uri))
        h = _region_uri(table_uri, "h", k)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, col_uri))
        g.add((table_uri, TAB.hasHeaderNode, h))
        label = by_rc.get((k, 0))
        if label is not None:
            lc = _region_uri(table_uri, "lc", k)
            g.add((lc, RDF.type, TAB.LabelCell))
            g.add((table_uri, TAB.hasCell, lc))
            g.add((lc, TAB.cellText, Literal(label.text)))
            g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
            g.add((lc, TAB.hasBBox, _bbox_node(g, label)))
            g.add((h, TAB.hasLabel, lc))

    rows = {}
    for m in phys_cols:
        row_uri = _region_uri(table_uri, "r", m)
        rows[m] = row_uri
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))

    asserted = 0
    for k in phys_rows:
        for m in phys_cols:
            cell = by_rc.get((k, m))
            if cell is None:
                continue
            if cell_round_trips(cell, b):
                e = _region_uri(table_uri, f"e{m}_", k)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, cols[k], rows[m], cell)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{m}_", k)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
    return asserted


def assert_row_hier_region(g: Graph, rreg, band, table_uri: URIRef,
                           doc_uri: URIRef, page: int) -> int:
    """Emit a tab:HierarchicalTable with a ROW-header tree (Design A: stub columns are
    the row-header axis; only data columns are leaf columns). Returns the asserted
    entry count. Reuses the shared entry/round-trip emitters; row-header LabelCells and
    entries both carry physical provenance.
    """
    from .regions import column_of
    g.add((table_uri, RDF.type, TAB.HierarchicalTable))
    b = rreg.grid.boundaries

    # header line labels, by column — keep the Word object for geometry (provenance-to-the-page)
    header_by_col: dict[int, object] = {}
    if band.lines:
        for w in band.lines[0].words:
            header_by_col[column_of((w.x0 + w.x1) / 2.0, b)] = w

    # data leaf columns + flat column header nodes
    col_uris = {}
    for c in rreg.data_cols:
        cu = _region_uri(table_uri, "c", c)
        col_uris[c] = cu
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, cu))
        h = _region_uri(table_uri, "ch", c)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, cu))
        g.add((table_uri, TAB.hasHeaderNode, h))
        if c in header_by_col:
            hw = header_by_col[c]
            lc = _region_uri(table_uri, "clc", c)
            g.add((lc, RDF.type, TAB.LabelCell))
            g.add((table_uri, TAB.hasCell, lc))
            g.add((lc, TAB.cellText, Literal(hw.text)))
            g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(round(hw.x0, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(round(hw.top, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.x1, Literal(round(hw.x1, 2), datatype=XSD.decimal)))
            g.add((bb, TAB.y1, Literal(round(hw.bottom, 2), datatype=XSD.decimal)))
            g.add((lc, TAB.hasBBox, bb))
            g.add((h, TAB.hasLabel, lc))

    # leaf rows
    row_uris = {}
    for i in range(len(rreg.leaf_rows)):
        ru = _region_uri(table_uri, "r", i)
        row_uris[i] = ru
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, ru))

    # row-header tree (coversRow + parentHeader + LabelCell with physical provenance)
    node_uris = {}
    for idx, nd in enumerate(rreg.tree):
        h = _region_uri(table_uri, "rh", idx)
        node_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for rr in nd.covers_rows:
            g.add((h, TAB.coversRow, row_uris[rr]))
        lc = _region_uri(table_uri, "rlc", idx)
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(nd.text)))
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((bb, TAB.x0, Literal(round(nd.x0, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y0, Literal(round(nd.top, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.x1, Literal(round(nd.x1, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y1, Literal(round(nd.bottom, 2), datatype=XSD.decimal)))
        g.add((lc, TAB.hasBBox, bb))
        g.add((h, TAB.hasLabel, lc))
    for idx, nd in enumerate(rreg.tree):
        if nd.parent is not None:
            g.add((node_uris[idx], TAB.parentHeader, node_uris[nd.parent]))

    # entries: (data column x leaf row), certified per-cell by the round-trip
    asserted = 0
    for i, rb in enumerate(rreg.leaf_rows):
        by_col = {column_of((sc.x0 + sc.x1) / 2.0, b): sc for sc in rb.cells}
        for c in rreg.data_cols:
            cell = by_col.get(c)
            if cell is None:
                continue
            # column-specific containment check (NOT cell_round_trips, which checks full-table extent)
            fits = all(b[c] - 0.5 <= w.x0 and w.x1 <= b[c + 1] + 0.5 for w in cell.words)
            if fits:
                e = _region_uri(table_uri, f"e{i}_", c)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, col_uris[c], row_uris[i], cell)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{i}_", c)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
    return asserted


def assert_matrix_region(g: Graph, mreg, band, table_uri: URIRef,
                         doc_uri: URIRef, page: int) -> int:
    """Emit a tab:HierarchicalTable for a cross-tab: a column tree (coversColumn) over
    the data leaf columns + a row tree (coversRow) over the leaf rows, entries at
    (data-col x leaf-row). Composes the Loop 2 column-header and Loop 5 row-header
    emission patterns; reuses the shared entry emitters. Both axes' LabelCells carry
    physical bbox/onPage. Returns the asserted entry count.

    (band is accepted for signature symmetry with the other makers but is unused:
    all column-label geometry is pre-computed on mreg.col_tree by classify_matrix.)"""
    from .regions import column_of
    g.add((table_uri, RDF.type, TAB.HierarchicalTable))
    b = mreg.grid.boundaries

    def _label(uri_key, idx, text, x0, top, x1, bottom):
        lc = _region_uri(table_uri, uri_key, idx)
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(text)))
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((bb, TAB.x0, Literal(round(x0, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y0, Literal(round(top, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.x1, Literal(round(x1, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y1, Literal(round(bottom, 2), datatype=XSD.decimal)))
        g.add((lc, TAB.hasBBox, bb))
        return lc

    # data leaf columns
    col_uris = {}
    for c in mreg.data_cols:
        cu = _region_uri(table_uri, "c", c)
        col_uris[c] = cu
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, cu))

    # column-header tree (coversColumn + parentHeader + LabelCell)
    cnode_uris = {}
    for idx, nd in enumerate(mreg.col_tree):
        h = _region_uri(table_uri, "ch", idx)
        cnode_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for c in nd.covers:
            g.add((h, TAB.coversColumn, col_uris[c]))
        g.add((h, TAB.hasLabel, _label("chl", idx, nd.text, nd.x0, nd.top, nd.x1, nd.bottom)))
    for idx, nd in enumerate(mreg.col_tree):
        if nd.parent is not None:
            g.add((cnode_uris[idx], TAB.parentHeader, cnode_uris[nd.parent]))

    # leaf rows
    row_uris = {}
    for i in range(len(mreg.leaf_rows)):
        ru = _region_uri(table_uri, "r", i)
        row_uris[i] = ru
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, ru))

    # row-header tree (coversRow + parentHeader + LabelCell)
    rnode_uris = {}
    for idx, nd in enumerate(mreg.row_tree):
        h = _region_uri(table_uri, "rh", idx)
        rnode_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for rr in nd.covers_rows:
            g.add((h, TAB.coversRow, row_uris[rr]))
        g.add((h, TAB.hasLabel, _label("rhl", idx, nd.text, nd.x0, nd.top, nd.x1, nd.bottom)))
    for idx, nd in enumerate(mreg.row_tree):
        if nd.parent is not None:
            g.add((rnode_uris[idx], TAB.parentHeader, rnode_uris[nd.parent]))

    # entries at (data column x leaf row)
    asserted = 0
    for i, rb in enumerate(mreg.leaf_rows):
        by_col = {column_of((sc.x0 + sc.x1) / 2.0, b): sc for sc in rb.cells}
        for c in mreg.data_cols:
            sc = by_col.get(c)
            if sc is None:
                continue
            # column-specific containment (NOT cell_round_trips, which checks full-table extent)
            fits = all(b[c] - 0.5 <= w.x0 and w.x1 <= b[c + 1] + 0.5 for w in sc.words)
            if fits:
                e = _region_uri(table_uri, f"e{i}_", c)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, col_uris[c], row_uris[i], sc)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{i}_", c)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, sc)
    return asserted


def _suggester_uri(reason: str) -> URIRef:
    """One suggester IRI per escalation reason, derived MECHANICALLY from the reason string.

    Derivation, not a lookup table: a hand-maintained table drifts from the call sites the
    moment a new reason string is introduced, and the drift is silent. Precedent for the
    shape of the IRI: `ground.py:22 _EXACT_RULE = "urn:iladub:suggester/exact-match-rule"`.

    This is where the reason GOES (spec §5.1). A per-reason suggester makes "which rule
    proposed this" a join (`?c iladub:suggestedBy <…/matrix-ambiguous-rule>`) instead of a
    `FILTER regex` over a rationale string.
    """
    slug = reason.strip().lower().replace("_", "-")
    return URIRef(f"urn:iladub:suggester/{slug}-rule")


def escalate_region(g: Graph, cand_uri: URIRef, doc_uri: URIRef, ascii_text: str,
                    reason: str, anchor: URIRef, confidence: float, page: int) -> None:
    """Emit an escalated region as a PROPOSITION — never as a decision (R69).

    Gate classification (CLAUDE.md §8): PROCEDURAL. It records, in RDF, a decision the
    caller has ALREADY made (this region cannot be asserted, for this reason). It introduces
    no judgement of its own: every value written is either passed in or derived mechanically
    from one that was. Irreducible: writing triples is engine glue.

    THE EPISTEMICS (CLAUDE.md §3). A candidate is a proposition, so it carries the
    PROPOSITION vocabulary and no `dec:` property at all. Before this, it carried
    `dec:confidence` and `dec:rationale`; because `dec:confidence` declares
    `rdfs:domain dec:DecisionHolon` (dec.ttl:80-82), any consumer applying our published
    axioms entailed that every escalated region IS a decision holon — and then failed it
    against `dec:DecisionHolonShape` for having no option space, no chosen option and no
    agent. That is R69, and it is a PUBLICATION defect: the shipped subclass-only closure
    (spec 2026-08-06) never materialised domain typing, so it never fired in-house. With no
    `dec:` property on the node, no domain entailment can reach it under any reasoner.

    `page` is REQUIRED, not defaulted: `iladub:CandidateConceptShape` does not demand it, so
    an optional page would be dropped silently by any future call site and the SourceRegion
    would decay into the typed-but-empty stub that provenance-to-the-page (§6) exists to
    prevent. All twelve call sites have it in scope (measured 2026-08-10).
    """
    region_uri = URIRef(f"{cand_uri}-source")

    g.add((cand_uri, RDF.type, ILADUB.CandidateConcept))
    g.add((cand_uri, ILADUB.surfaceText, Literal(ascii_text)))
    g.add((cand_uri, ILADUB.suggestedAnchor, anchor))
    # xsd:decimal via Decimal, NOT via a float: Literal(round(x, 2), datatype=XSD.decimal)
    # builds a literal whose Python value is a float, which pySHACL reads as ill-typed
    # against sh:datatype xsd:decimal (measured 2026-08-10, loop Task 1).
    g.add((cand_uri, ILADUB.confidence, Literal(Decimal(str(round(confidence, 6))))))
    agent = _suggester_uri(reason)
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cand_uri, ILADUB.suggestedBy, agent))
    g.add((cand_uri, RDFS.label, Literal(reason)))      # the human-readable reason, as ground.py:91
    g.add((cand_uri, ILADUB.status, ILADUB.proposed))
    g.add((cand_uri, ILADUB.fromRegion, region_uri))
    g.add((cand_uri, PROV.wasDerivedFrom, doc_uri))

    # The source region is a node DISTINCT from the candidate: `cand_uri` is the candidate,
    # and pointing iladub:fromRegion at it would satisfy the shape while asserting nothing.
    # It carries the page as a typed integer — see iladub:onPage's comment for why not
    # tab:onPage, and why not the page-scoped document IRI.
    g.add((region_uri, RDF.type, ILADUB.SourceRegion))
    g.add((region_uri, ILADUB.onPage, Literal(int(page), datatype=XSD.integer)))
    g.add((region_uri, PROV.wasDerivedFrom, doc_uri))


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
                        "ROUND_TRIP_FAIL", TAB.HierarchicalTable, 0.3, page)
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

    # Leaf rows — with arithmetic aggregation detection (loop H, residue R4). A confirmed
    # subtotal is typed BOTH tab:AggregationRow (so raw-graph consumers like the concept feed
    # can exclude it without rdfs inference) and tab:DetectedAggregationRow (the operand-
    # requiring shape targets only this subclass, sparing denormalization's bare rows).
    from .rows import detect_aggregation_rows
    agg = detect_aggregation_rows(region.rows, region.grid)
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))
        if r in agg:
            _lcol, _mcol, members = agg[r]
            g.add((row_uri, RDF.type, TAB.AggregationRow))
            g.add((row_uri, RDF.type, TAB.DetectedAggregationRow))
            g.add((row_uri, TAB.aggregationFunction, Literal("sum")))
            for m in members:
                g.add((row_uri, TAB.aggregates, URIRef(f"{table_uri}-r{m}")))

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

    # Row groups from the confirmed aggregations (loop I, AXIOM): runs AFTER the entry
    # cells exist (the key query reads member cells), still inside the caller's scratch
    # graph when the loop G backstop gates this path — a malformed group escalates in-band.
    if agg:
        from .rowgroups import derive_row_groups
        derive_row_groups(g, table_uri, agg)

    return asserted
