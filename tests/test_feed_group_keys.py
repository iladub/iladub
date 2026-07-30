"""Loop K — the feed carries recovered group keys to the grounding portal, and blank
placeholder cells stop minting noise propositions.

Injection is column-identity-driven (never text): a record gains one SurfaceConcept per
covering DerivedRowGroup whose column it does not already populate, valued with the group
key and provenanced to the SOURCE cell the key came from (§5/§6). Blank cells
(celltype.is_blank — loop A's one owned convention) are dropped; the literal string
'Blank' is NOT a marker and flows through to honest quarantine.
See docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.feed import table_records

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
T = URIRef("urn:doc#h0")


def _table(g, headers, rows):
    """Minimal HierarchicalTable in the holon emission shape. headers: list of column
    label texts (index = column). rows: {row_index: {col_index: text}}."""
    g.add((T, RDF.type, TAB.HierarchicalTable))
    for c, htext in enumerate(headers):
        cu = URIRef(f"{T}-c{c}")
        h = URIRef(f"{T}-h{c}")
        lc = URIRef(f"{T}-hl{c}")
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((T, TAB.hasHeaderNode, h))
        g.add((h, TAB.coversColumn, cu))
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((lc, TAB.cellText, Literal(htext)))
        g.add((h, TAB.hasLabel, lc))
    for r, cols in rows.items():
        ru = URIRef(f"{T}-r{r}")
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((T, TAB.hasLeafRow, ru))
        for c, text in cols.items():
            e = URIRef(f"{T}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((T, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru))
            g.add((e, TAB.atColumn, URIRef(f"{T}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"urn:doc#p0-{50 * c}-{10 * r}")))


def _group(g, i, label_cell, member_rows):
    grp = URIRef(f"{T}-rg{i}")
    g.add((grp, RDF.type, TAB.HeaderNode))
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((T, TAB.hasHeaderNode, grp))
    g.add((grp, TAB.hasLabel, URIRef(f"{T}-{label_cell}")))
    g.add((grp, PROV.wasDerivedFrom, URIRef(f"{T}-r{i}")))
    for m in member_rows:
        g.add((grp, TAB.coversRow, URIRef(f"{T}-r{m}")))
    return grp


def _by_row(recs):
    return {r.row_id.split(">")[-1].strip(): {c.text: c.value for c in r.concepts}
            for r in recs}


def test_suppressed_key_is_injected_with_source_provenance():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})                       # Month suppressed on r1
    _group(g, 9, "e0_0", (0, 1))                               # month group keyed at r0c0
    recs = table_records(g)
    concepts = {r.row_id: r.concepts for r in recs}
    r1 = [r for r in recs if "r1" in r.row_id][0]
    month = [c for c in r1.concepts if c.text == "Month"]
    assert len(month) == 1 and month[0].value == "Jul"
    assert month[0].region == "p0-0-0"                         # the SOURCE cell's fragment
    r0 = [r for r in recs if r.row_id.endswith("r0") or "r0" in r.row_id][0]
    assert sum(1 for c in r0.concepts if c.text == "Month") == 1   # r0: own cell, no dupe


def test_occupied_column_is_never_duplicated():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})
    _group(g, 8, "e0_1", (0, 1))                               # PORT group; both rows have Port
    recs = table_records(g)
    for r in recs:
        assert sum(1 for c in r.concepts if c.text == "Port") == 1, r.concepts


def test_nested_groups_sharing_a_label_cell_inject_once():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"], {0: {1: "Mackay", 2: "100"}})
    _group(g, 7, "e0_1", (0,))
    _group(g, 8, "e0_1", (0,))                                 # same label cell, same column
    recs = table_records(g)
    # r0's own Port cell occupies the column: zero injections, still exactly one Port
    assert sum(1 for c in recs[0].concepts if c.text == "Port") == 1


def test_blank_cells_are_dropped_but_do_not_block_injection():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {0: "(blank)", 1: "Mackay", 2: "-"}})           # blank Month AND blank Qty
    _group(g, 9, "e0_0", (0, 1))
    recs = table_records(g)
    r1 = [r for r in recs if "r1" in r.row_id][0]
    texts = {c.text: c.value for c in r1.concepts}
    assert texts.get("Month") == "Jul"                         # injected THROUGH the blank
    assert "Qty" not in texts                                  # blank dropped, nothing injected
    assert all(c.value not in ("(blank)", "-") for c in r1.concepts)


def test_literal_Blank_string_is_not_a_marker():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"], {0: {0: "Jul", 1: "Blank", 2: "100"}})
    recs = table_records(g)
    assert {c.text: c.value for c in recs[0].concepts}["Port"] == "Blank"


def test_all_blank_row_mints_no_record():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {0: "(blank)", 1: "-", 2: ""}})
    assert len(table_records(g)) == 1


def test_injected_concept_sorts_by_its_column_position():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})
    _group(g, 9, "e0_0", (0, 1))
    r1 = [r for r in table_records(g) if "r1" in r.row_id][0]
    assert [c.text for c in r1.concepts] == ["Month", "Port", "Qty"]


def test_injection_does_not_reorder_records():
    """Task 1 review ⚠️: the injected concept's y-sort key must be the ROW's own extent,
    not the label cell's y0 — mutation-verified: keying on the label's y0 silently sorts a
    later covered row ahead of an intervening uncovered row (r2 before r1). Pins the
    record order."""
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "A", 2: "100"},
            1: {1: "B", 2: "150"},
            2: {1: "C", 2: "200"}})
    _group(g, 9, "e0_0", (2,))           # key cell at y=0 covers ONLY r2 (y=20)
    recs = table_records(g)
    order = [{c.text: c.value for c in r.concepts}["Qty"] for r in recs]
    assert order == ["100", "150", "200"], order
