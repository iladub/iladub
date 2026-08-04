"""Loop Q Task 5 (spec 2026-08-04 §4.2) — section captions as candidate key concepts.

A repaired section table's peeled strips are already carried as `tab:RegionCaption`
(`tab:captionText`/`tab:captionRow`/`tab:hasCaption` — loop Q Tasks 3-4). This feeds them
into the grounding portal, imitating loop K's injected-keys SHAPE
(`feed._inject_group_keys`): one candidate `SurfaceConcept` per caption, appended to every
record of the table that carries it, provenanced to the caption node. Discriminating the
KEY ('GERALDTON') from a notice ('BERTH MAY BE UNAVAILABLE...') among those captions is NOT
this layer's job (§4.3's naming cascade does it later via scheme membership) — every caption
is injected as an undiscriminated candidate.

Attribution never waits for naming (§4.2): the record's OWN identity gains the table's FIRST
caption, positionally, before any field name is decided — the loop-I 'value without a name'
idiom carried to a NEW evidence source.
"""
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.feed import table_records
from iladub.ground import SurfaceConcept
from tests.test_feed_chain_walk import _chained

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _table(g, table, page, headers, rows):
    """A minimal RecordTable in the holon emission shape, on `page` — same shape the other
    top-level feed tests use (test_feed_chain_walk._table), duplicated rather than imported
    because that one hangs off a HierarchicalTable type; a flat RecordTable is the shape
    loop Q's section tables actually assert as (task 4 report: 'both sections as RECORD_TABLE')."""
    g.add((table, RDF.type, TAB.RecordTable))
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
            bb = URIRef(f"{table}-bb{r}_{c}")
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"{table}-src{r}_{c}")))


def _caption(g, table, k, text):
    """One `tab:RegionCaption`, positionally ordered by `tab:captionRow` — exactly the shape
    `compile._emit_band_captions` commits."""
    cap = URIRef(f"{table}-bandcap{k}")
    g.add((cap, RDF.type, TAB.RegionCaption))
    g.add((cap, TAB.captionText, Literal(text)))
    g.add((cap, TAB.captionRow, Literal(k, datatype=XSD.integer)))
    g.add((table, TAB.hasCaption, cap))
    return cap


G = URIRef("urn:doc/p0#table0")
K = URIRef("urn:doc/p0#table1")


def _geraldton_section():
    g = Graph()
    _table(g, G, 0, ["ID", "Client", "Volume"],
           {0: {0: "10097", 1: "Brahman", 2: "30000"},
            1: {0: "10076", 1: "CBH", 2: "50000"}})
    _caption(g, G, 0, "GERALDTON")
    _caption(g, G, 1, "BERTH MAY BE UNAVAILABLE 2000HRS")
    return g


def test_every_record_of_a_captioned_table_carries_every_caption_as_a_candidate():
    """(1) records of a captioned section table carry GERALDTON + the notice as candidate
    concepts, undiscriminated — both rows get BOTH captions."""
    recs = table_records(_geraldton_section())
    assert len(recs) == 2, recs
    for r in recs:
        markers = {c.value for c in r.concepts if c.is_section_marker}
        assert markers == {"GERALDTON", "BERTH MAY BE UNAVAILABLE 2000HRS"}, r.concepts


def test_injected_marker_text_is_the_caption_text():
    """The brief's interface: text = caption text (no column names a section marker — the
    field NAME is undecided until §4.3's cascade runs)."""
    recs = table_records(_geraldton_section())
    key = next(c for c in recs[0].concepts if c.value == "GERALDTON")
    assert key.text == "GERALDTON"
    assert key.is_section_marker is True


def test_injected_marker_provenance_is_the_caption_node():
    """Provenance follows the SAME shape every other SurfaceConcept in feed.py uses: the
    region is read off the SOURCE node's own fragment (a RegionCaption asserts no
    prov:wasDerivedFrom of its own, so this is the caption node's own fragment, exactly the
    `_read_table` fallback branch: `str(e).split('#')[-1]` when there is no separate
    provenance node)."""
    recs = table_records(_geraldton_section())
    key = next(c for c in recs[0].concepts if c.value == "GERALDTON")
    assert key.region == "table0-bandcap0", key.region
    notice = next(c for c in recs[0].concepts if c.value.startswith("BERTH"))
    assert notice.region == "table0-bandcap1", notice.region


def test_captions_do_not_disturb_the_row_s_own_cells():
    """Injection ADDS candidates; it must never touch what the row's own cells already say."""
    recs = table_records(_geraldton_section())
    r0 = recs[0]
    assert {c.text: c.value for c in r0.concepts if not c.is_section_marker} == \
        {"ID": "10097", "Client": "Brahman", "Volume": "30000"}


def test_identities_distinct_across_sections():
    """(2) GERALDTON-section r0 and KWINANA-section r0 stay distinct records, and each
    record's identity carries its OWN table's first caption positionally — the loop-I
    'value without a name' idiom, over the new caption evidence source."""
    g = _geraldton_section()
    _table(g, K, 0, ["ID", "Client", "Volume"], {0: {0: "20011", 1: "Viterra", 2: "40000"}})
    _caption(g, K, 0, "KWINANA")
    recs = table_records(g)
    ids = {r.row_id for r in recs}
    assert len(ids) == len(recs), ids                      # (byte) no collision at all
    geraldton_r0 = next(r for r in recs if any(c.value == "10097" for c in r.concepts))
    kwinana_r0 = next(r for r in recs if any(c.value == "20011" for c in r.concepts))
    assert geraldton_r0.row_id != kwinana_r0.row_id
    assert geraldton_r0.row_id.startswith("GERALDTON > "), geraldton_r0.row_id
    assert kwinana_r0.row_id.startswith("KWINANA > "), kwinana_r0.row_id


def test_table_without_captions_behaves_as_today():
    """(4) A section table (or any table) with NO `tab:hasCaption` is untouched: no section
    marker concepts, and the row_id keeps its plain (unprefixed) discriminator."""
    g = Graph()
    _table(g, G, 0, ["ID", "Client", "Volume"], {0: {0: "10097", 1: "Brahman", 2: "30000"}})
    recs = table_records(g)
    assert len(recs) == 1
    assert not any(c.is_section_marker for c in recs[0].concepts)
    assert recs[0].row_id == "p0 table0-r0", recs[0].row_id
    assert " > " not in recs[0].row_id


def test_byte_identity_pin_existing_chain_fixture_unchanged():
    """(3) An existing feed fixture with NO captions anywhere (loop M's `_chained()`, used by
    tests/test_feed_chain_walk.py) reads BYTE-IDENTICALLY: same record count, same row_ids,
    same concepts, in the same order. Pins that a table with no `tab:hasCaption` triple never
    exercises the new injection or identity-prefix path at all."""
    recs = table_records(_chained())
    got = [(r.row_id, tuple((c.text, c.value, c.is_section_marker) for c in r.concepts))
           for r in recs]
    assert got == [
        ("p0 h0-r0", (("Month", "Jul", False), ("Port", "Mackay", False), ("Qty", "100", False))),
        ("p0 h0-r1", (("Month", "Jul", False), ("Port", "Geelong", False), ("Qty", "150", False))),
        ("p1 h0-r0", (("Month", "Aug", False), ("Port", "Portland", False), ("Qty", "200", False))),
        ("p1 h0-r1", (("Month", "Aug", False), ("Port", "Carrington", False), ("Qty", "250", False))),
    ], got
