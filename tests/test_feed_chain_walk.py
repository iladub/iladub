"""Loop M task 4 — a `tab:continuesTable` chain is read as ONE logical table.

Pagination is an accommodation: one logical table, cut to fit the page. The compile keeps the
cut visible (one page-scoped table per page, linked by the fact the continuation AXIOM
licensed); the FEED un-does it at reading time — the head table's rows first, then each
continuation's, in page order, in one identity space, and no continuation table read twice.

The three invariants pinned here, and why each has teeth:
  * ONE record per row, in page order — a continuation table is never read separately.
  * DISTINCT subjects across the break — pages compile under page-scoped document URIs, so the
    same row FRAGMENT names different rows on different pages (measured on the GrainCorp stem:
    65 of page 2's fragments also name a page-1 row). Merging without page-qualifying collapses
    two records onto one subject.
  * NO label identity assumed across a link (residue R34, third face) — recognition's evidence
    stops at the LEAF header row, so a licensed chain can span tables whose header blocks differ
    ABOVE it. Each member's fields come from ITS OWN header path, and each member's group keys
    reach only ITS OWN rows.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.feed import table_records, _record_uri

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _table(g, table, page, headers, rows):
    """A minimal HierarchicalTable in the holon emission shape, on `page`, under the
    page-scoped document URI `table` hangs off (document.page_doc_uri's shape)."""
    g.add((table, RDF.type, TAB.HierarchicalTable))
    for c, htext in enumerate(headers):
        h = URIRef(f"{table}-h{c}")
        lc = URIRef(f"{table}-hl{c}")
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table, TAB.hasHeaderNode, h))
        g.add((h, TAB.coversColumn, URIRef(f"{table}-c{c}")))
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((lc, TAB.cellText, Literal(htext)))
        g.add((h, TAB.hasLabel, lc))
    for r, cols in rows.items():
        ru = URIRef(f"{table}-r{r}")
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table, TAB.hasLeafRow, ru))
        for c, text in cols.items():
            e = URIRef(f"{table}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((table, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru))
            g.add((e, TAB.atColumn, URIRef(f"{table}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"{table}-src{r}_{c}")))


def _group(g, table, i, label_cell, member_rows):
    """A derived row group on `table`, keyed by `label_cell`, covering `member_rows`."""
    grp = URIRef(f"{table}-rg{i}")
    g.add((grp, RDF.type, TAB.HeaderNode))
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((table, TAB.hasHeaderNode, grp))
    g.add((grp, TAB.hasLabel, URIRef(f"{table}-{label_cell}")))
    for m in member_rows:
        g.add((grp, TAB.coversRow, URIRef(f"{table}-r{m}")))
    return grp


# The two pages of one cut table: SAME fragments (`h0-r0`…), different page-scoped doc URIs —
# exactly what document.page_doc_uri produces.
P0 = URIRef("urn:doc/p0#h0")
P1 = URIRef("urn:doc/p1#h0")


def _chained(headers1=("Month", "Port", "Qty")):
    g = Graph()
    _table(g, P0, 0, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {0: "Jul", 1: "Geelong", 2: "150"}})
    _table(g, P1, 1, list(headers1),
           {0: {0: "Aug", 1: "Portland", 2: "200"},
            1: {0: "Aug", 1: "Carrington", 2: "250"}})
    g.add((P1, TAB.continuesTable, P0))
    return g


def test_chain_reads_as_one_logical_table_in_page_order():
    """Four rows over two pages -> four records, head's first, in page order, read ONCE."""
    recs = table_records(_chained())
    assert len(recs) == 4, [r.row_id for r in recs]
    assert [{c.text: c.value for c in r.concepts}["Qty"] for r in recs] == \
        ["100", "150", "200", "250"]


def test_colliding_row_fragments_across_a_chain_stay_distinct_records():
    """The teeth: `h0-r0` on page 0 and `h0-r0` on page 1 are DIFFERENT voyages. Merging the
    chain under one identity space without page-qualifying the discriminator grounds them onto
    ONE subject — silent data loss, and the shape the stem is one unlucky page away from."""
    recs = table_records(_chained())
    subjects = [str(_record_uri(r.row_id)) for r in recs]
    assert len(set(subjects)) == len(recs), sorted(subjects)


def test_each_member_keeps_its_own_header_path():
    """R34's third face: recognition compares the LEAF row only, so a chain may span tables
    whose header blocks differ above it. A continuation's fields come from ITS OWN reading —
    never inherited from the head's (which would relabel its cells with the head's strings)."""
    recs = table_records(_chained(headers1=("Month", "Port", "Total Tonnes")))
    texts = [sorted(c.text for c in r.concepts) for r in recs]
    assert texts[0] == ["Month", "Port", "Qty"]
    assert texts[3] == ["Month", "Port", "Total Tonnes"], texts[3]


def test_a_group_never_injects_across_the_break():
    """A head-page group covers a head-page row. The continuation page has a row of the SAME
    fragment; the key must not reach it — a group is evidence about its own table's rows only
    (§7: never emit what the source does not support)."""
    g = _chained()
    g.remove((URIRef(f"{P1}-e1_0"), TAB.cellText, Literal("Aug")))   # Port-only row on page 1
    _group(g, P0, 9, "e0_0", (0, 1))                                 # 'Jul' group, page 0
    recs = table_records(g)
    page1 = [r for r in recs if any(c.value == "Carrington" for c in r.concepts)][0]
    assert not any(c.value == "Jul" for c in page1.concepts), page1.concepts


def test_unchained_pages_are_qualified_too():
    """The review's F1, pinned. An UNCHAINED two-page document is where the weld BITES: nothing
    else distinguishes page 0's `h0-r1` from page 1's, and the old collision suffix was a no-op
    (`h0-r1 > h0-r1` for both) whenever the id already WAS the fragment — every flat RecordTable.
    Measured on loop M's own case-1 fixture before the fix: 6 records, 3 subjects, one subject
    carrying a shipping row AND a lab row.

    So qualification is unconditional, and this test asserts the FIXED invariant. The version of
    it that asserted 'byte-identical when unchained' was pinning the defect as correct."""
    g = _chained()
    g.remove((P1, TAB.continuesTable, P0))
    recs = table_records(g)
    assert len(recs) == 4
    assert [r.row_id for r in recs] == ["p0 h0-r0", "p0 h0-r1", "p1 h0-r0", "p1 h0-r1"]
    assert len({str(_record_uri(r.row_id)) for r in recs}) == 4


def test_unpaged_graph_still_never_welds_two_rows():
    """F6/§7: a graph recording no `tab:onPage` loses the readable qualifier — it must NOT
    silently fall back to a discriminator that collides. The final pass settles any residual id
    with the row's own IRI, which RDF guarantees unique. Two tables under DIFFERENT document
    scopes, identical fragments, no pages, no chain: four rows, four subjects."""
    g = _chained()
    g.remove((P1, TAB.continuesTable, P0))
    for s, p, o in list(g.triples((None, TAB.onPage, None))):
        g.remove((s, p, o))
    recs = table_records(g)
    assert len(recs) == 4
    assert len({str(_record_uri(r.row_id)) for r in recs}) == 4, [r.row_id for r in recs]


def test_a_cycle_loses_no_records():
    """A malformed graph (each table continues the other) has no head. Records must still be
    read — once each — rather than vanishing into an unreachable cycle."""
    g = _chained()
    g.add((P0, TAB.continuesTable, P1))
    recs = table_records(g)
    assert len(recs) == 4, [r.row_id for r in recs]
    assert len({str(_record_uri(r.row_id)) for r in recs}) == 4
