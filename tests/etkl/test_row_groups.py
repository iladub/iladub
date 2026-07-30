"""Loop I — row groups derived from confirmed aggregations (AXIOM).

A confirmed aggregation row witnesses its group: its label column = the level, its
tab:aggregates edges = the members, and the group KEY = the unique distinct non-blank
cell value in the label column among the members. No unique value -> no group (§7).
Nesting = strict member-set containment. Keys are read positionally — label text of the
aggregation row itself is NEVER parsed (no language).
See docs/superpowers/specs/2026-07-30-row-groups-design.md.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl.rowgroups import derive_row_groups

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
T = URIRef("urn:doc#h0")


def _emit(g, rows, aggs):
    """Mirror the holon emission shape. rows: {row_index: {col_index: text}};
    aggs: {agg_row_index: member_row_indices}. y0 = 10*row (top-to-bottom order)."""
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
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
    for a, members in aggs.items():
        au = URIRef(f"{T}-r{a}")
        g.add((au, RDF.type, TAB.DetectedAggregationRow))
        for m in members:
            g.add((au, TAB.aggregates, URIRef(f"{T}-r{m}")))


def _grp(i):
    return URIRef(f"{T}-rg{i}")


def test_unique_key_builds_a_group_with_label_and_members():
    g = Graph()
    _emit(g, {0: {1: "Jul 26", 2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "Mackay Total", 3: "250"}}, {2: (0, 1)})
    n = derive_row_groups(g, T, {2: (2, 3, (0, 1))})
    assert n == 1
    grp = _grp(2)
    assert (grp, RDF.type, TAB.DerivedRowGroup) in g
    assert (grp, RDF.type, TAB.HeaderNode) in g
    assert (T, TAB.hasHeaderNode, grp) in g
    covers = set(g.objects(grp, TAB.coversRow))
    assert covers == {URIRef(f"{T}-r0"), URIRef(f"{T}-r1")}
    label = g.value(grp, TAB.hasLabel)
    assert str(g.value(label, TAB.cellText)) == "Mackay"
    assert label == URIRef(f"{T}-e0_2")          # the TOPMOST source cell (by tab:y0)
    assert g.value(grp, PROV.wasDerivedFrom) == URIRef(f"{T}-r2")


def test_conflicting_keys_refuse():
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Gladstone", 3: "150"},
              2: {2: "X Total", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 0


def test_all_blank_keys_refuse():
    # Suppressed cells are ABSENT; an empty-text cell is also not a key.
    g = Graph()
    _emit(g, {0: {2: "", 3: "100"},
              1: {3: "150"},
              2: {0: "TOT", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (0, 3, (0, 1))}) == 0


def test_suppressed_key_month_shape():
    # The GrainCorp month shape: only the FIRST member carries the key in the label column.
    g = Graph()
    _emit(g, {0: {1: "Jul 26", 3: "100"},
              2: {3: "150"},
              4: {3: "200"},
              6: {1: "Jul 26 Total", 3: "450"}}, {6: (0, 2, 4)})
    n = derive_row_groups(g, T, {6: (1, 3, (0, 2, 4))})
    assert n == 1
    assert str(g.value(g.value(_grp(6), TAB.hasLabel), TAB.cellText)) == "Jul 26"


def test_nesting_by_containment_and_levels():
    # Two port groups inside one month group: parentHeader + headerLevel by ancestor count.
    g = Graph()
    _emit(g, {0: {1: "Jul", 2: "A", 3: "100"},
              1: {2: "A Total", 3: "100"},
              2: {2: "B", 3: "200"},
              3: {2: "B Total", 3: "200"},
              4: {1: "Jul Total", 3: "300"}},
          {1: (0,), 3: (2,), 4: (0, 2)})
    n = derive_row_groups(g, T, {1: (2, 3, (0,)), 3: (2, 3, (2,)), 4: (1, 3, (0, 2))})
    assert n == 3
    assert g.value(_grp(1), TAB.parentHeader) == _grp(4)
    assert g.value(_grp(3), TAB.parentHeader) == _grp(4)
    assert g.value(_grp(4), TAB.parentHeader) is None
    assert int(g.value(_grp(4), TAB.headerLevel)) == 0
    assert int(g.value(_grp(1), TAB.headerLevel)) == 1


def test_no_intermediate_skipping():
    # 3-level chain: the innermost group's parent is the MIDDLE group, never the outermost.
    g = Graph()
    _emit(g, {0: {0: "S", 1: "Jul", 2: "A", 3: "100"},
              1: {2: "A Total", 3: "100"},
              2: {1: "Jul Total", 3: "100"},
              3: {0: "S Total", 3: "100"}},
          {1: (0,), 2: (0,), 3: (0,)})
    n = derive_row_groups(g, T, {1: (2, 3, (0,)), 2: (1, 3, (0,)), 3: (0, 3, (0,))})
    assert n == 3
    # identical member sets are NOT strict containment -> no parent links at all here;
    # make the sets strictly nested instead:
    g2 = Graph()
    _emit(g2, {0: {0: "S", 1: "Jul", 2: "A", 3: "100"},
               1: {2: "A", 3: "50"},
               2: {2: "A Total", 3: "150"},
               3: {1: "Jul", 3: "10"},
               4: {1: "Jul Total", 3: "160"},
               5: {0: "S", 3: "5"},
               6: {0: "S Total", 3: "165"}},
           {2: (0, 1), 4: (0, 1, 3), 6: (0, 1, 3, 5)})
    assert derive_row_groups(
        g2, T, {2: (2, 3, (0, 1)), 4: (1, 3, (0, 1, 3)), 6: (0, 3, (0, 1, 3, 5))}) == 3
    assert g2.value(_grp(2), TAB.parentHeader) == _grp(4)     # not rg6
    assert g2.value(_grp(4), TAB.parentHeader) == _grp(6)
    assert int(g2.value(_grp(2), TAB.headerLevel)) == 2


def test_key_is_read_positionally_never_matched():
    # A key in another language derives identically — only position and uniqueness matter.
    g = Graph()
    _emit(g, {0: {2: "Zwischensumme-Gruppe", 3: "100"},
              1: {2: "Zwischensumme-Gruppe", 3: "150"},
              2: {2: "ZS", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 1
    assert str(g.value(g.value(_grp(2), TAB.hasLabel), TAB.cellText)) == "Zwischensumme-Gruppe"


def test_no_confirmed_aggregations_derives_nothing():
    g = Graph()
    _emit(g, {0: {2: "A", 3: "100"}}, {})
    assert derive_row_groups(g, T, {}) == 0
    assert (None, RDF.type, TAB.DerivedRowGroup) not in g
