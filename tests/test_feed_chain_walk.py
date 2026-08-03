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


def _cols(g, table, n):
    """The table's leaf columns — what `tab:continuesColumn` is asserted between."""
    for c in range(n):
        cu = URIRef(f"{table}-c{c}")
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table, TAB.hasLeafColumn, cu))


def test_document_level_group_keys_reach_every_member():
    """LOOP N: a chain's keys come from the LOGICAL table's own derivation.

    The document-level pass derives one group over the whole chain and hangs it off the HEAD,
    with `tab:coversRow` edges that deliberately cross into the continuation's rows. The feed
    must inject that key into EVERY covered record, on whichever page it sits — which is what
    'the chain reads as one table' means on the row axis. Before loop N a continuation's rows
    could only be keyed by their own page's groups, and the stem's page-1/page-2 records
    carried no fiscal-year key at all (measured: 1/51 and 2/44).

    The Month column of page 1's row is left EMPTY (the author suppressed the repeated key
    under the group) so the injection has somewhere to land.
    """
    g = _chained()
    _cols(g, P0, 3)
    _cols(g, P1, 3)
    for c in range(3):
        g.add((URIRef(f"{P1}-c{c}"), TAB.continuesColumn, URIRef(f"{P0}-c{c}")))
    g.remove((URIRef(f"{P1}-e0_0"), None, None))                     # suppressed under the group
    g.remove((None, None, URIRef(f"{P1}-e0_0")))
    grp = _group(g, P0, 9, "e0_0", ())                               # 'Jul', on the HEAD
    for t, r in ((P0, 0), (P0, 1), (P1, 0)):                         # covers rows on BOTH pages
        g.add((grp, TAB.coversRow, URIRef(f"{t}-r{r}")))
    recs = table_records(g)
    keyed = [r for r in recs if any(c.value == "Portland" for c in r.concepts)][0]
    month = [c for c in keyed.concepts if c.value == "Jul"]
    assert month, keyed.concepts
    assert month[0].text == "Month"          # named by the ROW's own member table (R34)


def test_an_injected_key_never_overwrites_the_row_s_own_value_across_the_break():
    """The occupancy guard is on the LOGICAL column (loop N): page 1's row writes its own
    'Aug' in the Month column, so the head group's 'Jul' must not reach it — even though the
    label cell and the row now live in different tables, where 'the same column' is a
    different node."""
    g = _chained()
    _cols(g, P0, 3)
    _cols(g, P1, 3)
    for c in range(3):
        g.add((URIRef(f"{P1}-c{c}"), TAB.continuesColumn, URIRef(f"{P0}-c{c}")))
    grp = _group(g, P0, 9, "e0_0", ())
    for t, r in ((P0, 0), (P1, 0)):
        g.add((grp, TAB.coversRow, URIRef(f"{t}-r{r}")))
    recs = table_records(g)
    keyed = [r for r in recs if any(c.value == "Portland" for c in r.concepts)][0]
    months = sorted(c.value for c in keyed.concepts if c.text == "Month")
    assert months == ["Aug"], keyed.concepts


def test_a_covered_row_takes_its_identity_from_the_logical_group():
    """Record identity follows the same reading: a continuation's row covered by the head's
    document-level group is identified by that group's path, not by an opaque discriminator.
    Read per member, the row would fall back to `p1 h0-r0` and the document would carry two
    kinds of record id (measured on the stem before loop N: 47 opaque of 133)."""
    g = _chained()
    grp = _group(g, P0, 9, "e0_0", ())
    g.add((grp, TAB.coversRow, URIRef(f"{P1}-r0")))
    recs = table_records(g)
    keyed = [r for r in recs if any(c.value == "Portland" for c in r.concepts)][0]
    assert keyed.row_id == "Jul", keyed.row_id


def _two_coresident_groups(order):
    """Two derived groups covering ONE row at the SAME level, inserted in `order`.

    R18's co-resident case: the nesting query REFUSES to link groups with identical member sets
    (§7 — refusal over a guess), so both stay level 0 and both cover the row. Which one names the
    record is a first-wins pick; this fixture exists to prove the pick does not depend on the
    order the triples happen to sit in.
    """
    g = _chained()
    g.remove((P1, TAB.continuesTable, P0))
    for i in order:
        label, gid = (("e0_0", 8) if i == 0 else ("e0_1", 9))
        grp = _group(g, P0, gid, label, ())
        g.add((grp, TAB.coversRow, URIRef(f"{P0}-r0")))
        g.add((grp, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
    return g


def test_same_level_cover_is_broken_deterministically():
    """The SAME document must mint the SAME record subjects — every run, every environment.

    Two groups covering one row at one level reach `_header_path`'s deepest-cover selection with
    nothing to separate them. Before the tie-break the winner was whichever `graph.objects()`
    yielded first — i.e. rdflib's iteration order, which follows insertion order for the default
    store — so a graph built in a different order (a different rdflib version, a different store,
    a re-serialized round trip) could mint a DIFFERENT subject for the same row. Measured on the
    stem: 7 of 132 covered rows are in this state after the document-level derivation.

    The tie-break carries no meaning (neither group is more the row's header than the other — the
    §5 context loss R18 records is unchanged); it only has to be the same one every time.
    """
    ids = [ {r.row_id for r in table_records(_two_coresident_groups(o))}
            for o in ((0, 1), (1, 0)) ]
    assert ids[0] == ids[1], ids
    # and the winner is the lexicographically first (label, node), not an accident of order
    assert any(i.startswith("Jul") for i in ids[0]), ids[0]


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
