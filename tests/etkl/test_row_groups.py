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


def _emit(g, rows, aggs, table=T):
    """Mirror the holon emission shape. rows: {row_index: {col_index: text}};
    aggs: {agg_row_index: member_row_indices}. y0 = 10*row (top-to-bottom order).
    `table` defaults to the module T so every existing call site is unaffected; pass a
    distinct table URI to emit a second, independent table in the same graph (I-1,
    cross-table collision pinning)."""
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
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
    for a, members in aggs.items():
        au = URIRef(f"{table}-r{a}")
        g.add((au, RDF.type, TAB.DetectedAggregationRow))
        g.add((au, TAB.aggregationFunction, Literal("sum")))
        for m in members:
            g.add((au, TAB.aggregates, URIRef(f"{table}-r{m}")))


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


def _tiles(g):
    from iladub.etkl.tiling import region_tiles
    return region_tiles(g)


def test_membrane_refuses_a_labelless_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#h0-r0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is False


def test_membrane_refuses_a_memberless_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#h0-e0_2")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is False


def test_membrane_accepts_a_wellformed_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#h0-e0_2")))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#h0-r0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is True


def test_membrane_refuses_a_double_parent_group():
    """M-1 (final review, loop I): row-group-nesting.rq can legitimately emit two parents
    for one child when the member family is non-laminar. tab:DerivedRowGroupShape's new
    sh:maxCount 1 on tab:parentHeader must membrane-refuse that instead of letting the
    Python engine glue pick an arbitrary one (graph-iteration-order dependent)."""
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#h0-e0_2")))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#h0-r0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    g.add((grp, TAB.parentHeader, URIRef("urn:doc#h0-rg4")))
    g.add((grp, TAB.parentHeader, URIRef("urn:doc#h0-rg5")))
    assert _tiles(g) is False


def test_partial_derived_coverage_passes_the_row_tiling_shapes():
    """THE LANDMINE THIS TASK EXISTS FOR. RowCoverageShape / UnambiguousRowAccessShape fire
    as soon as ANY coversRow header exists, demanding every leaf row be covered. Derived
    groups are honestly PARTIAL (aggregation rows and unconfirmed groups' rows stay
    uncovered) — they are carried annotations, not a claimed partition. Without the trigger
    scoping, every real document with subtotals would escalate REGION_TILING_FAILED."""
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "SUB", 3: "250"},
              3: {2: "Kembla", 3: "999"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 1
    # rows r2 (the aggregation) and r3 (no confirmed group) are UNCOVERED — must still pass
    assert _tiles(g) is True


def test_two_confirmed_groups_over_the_same_member_rows_still_tile():
    """C-1 (final review, loop I): a month with a SINGLE port child confirms two
    aggregations over the SAME member row (the port total, then the month total) — the
    nesting query rightly refuses to link groups with identical member sets (§7: refusal
    over a guess), so both stay headerLevel 0 and both coversRow the same row. Without the
    derived-group exemption on tab:RowNoOverlapShape this trips 'row overlap' and
    region_tiles returns False, escalating the WHOLE region REGION_TILING_FAILED (measured:
    14 cells -> 0) — this is not exotic, any single-child group family produces it."""
    g = Graph()
    _emit(g, {0: {1: "Jul", 2: "A", 3: "100"},
              1: {2: "A Total", 3: "100"},
              2: {1: "Jul Total", 3: "100"}}, {1: (0,), 2: (0,)})
    n = derive_row_groups(g, T, {1: (2, 3, (0,)), 2: (1, 3, (0,))})
    assert n == 2
    assert set(g.objects(_grp(1), TAB.coversRow)) == set(g.objects(_grp(2), TAB.coversRow))
    assert g.value(_grp(1), TAB.parentHeader) is None
    assert g.value(_grp(2), TAB.parentHeader) is None
    assert int(g.value(_grp(1), TAB.headerLevel)) == 0
    assert int(g.value(_grp(2), TAB.headerLevel)) == 0
    assert _tiles(g) is True


def test_authored_row_trees_keep_the_strict_invariant():
    """The scoping must NOT weaken the row-hier/matrix membrane: a plain HeaderNode row tree
    with a coverage gap still fails."""
    g = Graph()
    t = URIRef("urn:doc#rh0")
    for r in (0, 1):
        g.add((URIRef(f"urn:doc#rh0-r{r}"), RDF.type, TAB.LeafRow))
        g.add((t, TAB.hasLeafRow, URIRef(f"urn:doc#rh0-r{r}")))
    h = URIRef("urn:doc#rh0-rh0")
    g.add((h, RDF.type, TAB.HeaderNode))          # authored, NOT DerivedRowGroup
    g.add((t, TAB.hasHeaderNode, h))
    g.add((h, TAB.coversRow, URIRef("urn:doc#rh0-r0")))   # r1 uncovered -> gap
    assert _tiles(g) is False


def test_authored_row_overlap_still_fails():
    """C-1's exemption must stay scoped to derived groups: two AUTHORED (plain HeaderNode,
    not DerivedRowGroup) nodes at the same headerLevel covering the same row is a genuine
    overlap defect and must still fail region_tiles."""
    g = Graph()
    t = URIRef("urn:doc#rh1")
    r0 = URIRef("urn:doc#rh1-r0")
    g.add((r0, RDF.type, TAB.LeafRow))
    g.add((t, TAB.hasLeafRow, r0))
    for i in (0, 1):
        h = URIRef(f"urn:doc#rh1-rh{i}")
        g.add((h, RDF.type, TAB.HeaderNode))          # authored, NOT DerivedRowGroup
        g.add((t, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversRow, r0))
    assert _tiles(g) is False


def test_derived_overlay_does_not_corrupt_an_authored_partition():
    """THE MEASURE for UnambiguousRowAccessShape's count-exclusion (task 2 review Minor):
    an authored row tree that fully tiles its rows, PLUS a derived group overlaying one of
    them. With the exclusion the authored partition still counts exactly one leaf header
    per row -> passes; without it the derived node counts as a second leaf header ->
    false ambiguity. (RowCoverageShape's own exemption stays shadowed by this shape on
    every fixture — pre-existing redundancy from the loop C 8-shape gate, noted in the
    ledger, not re-measured here.)

    Production-realistic (final review C-1 closing note): real emission always stamps
    tab:headerLevel on every HeaderNode (derive_row_groups does so for every
    DerivedRowGroup; authored row-hier trees carry it too) — a fixture omitting it does not
    measure RowNoOverlapShape at all (it only fires between nodes sharing a headerLevel).
    Both authored nodes and the derived overlay are stamped level 0 here, as production
    would be. This only passes WITH the RowNoOverlapShape derived-group exemption (C-1) —
    without it, the derived overlay and authored rh0 (both level 0, both cover r0) trip
    'row overlap' and region_tiles flips to False (verified by reverting the exemption)."""
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    from rdflib.namespace import XSD
    from iladub.etkl.tiling import region_tiles
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    t = URIRef("urn:doc#mix0")
    for r in (0, 1):
        g.add((URIRef(f"urn:doc#mix0-r{r}"), RDF.type, TAB.LeafRow))
        g.add((t, TAB.hasLeafRow, URIRef(f"urn:doc#mix0-r{r}")))
        h = URIRef(f"urn:doc#mix0-rh{r}")
        g.add((h, RDF.type, TAB.HeaderNode))            # authored: tiles 1:1
        g.add((t, TAB.hasHeaderNode, h))
        g.add((h, TAB.coversRow, URIRef(f"urn:doc#mix0-r{r}")))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
    grp = URIRef("urn:doc#mix0-rg9")                    # derived overlay on r0
    g.add((grp, RDF.type, TAB.HeaderNode))
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((t, TAB.hasHeaderNode, grp))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#mix0-r0")))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#mix0-e0_0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#mix0-r1")))
    g.add((grp, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
    assert region_tiles(g) is True


def test_feed_collision_guard_two_rows_one_group(tmp_path=None):
    """PR #59's recorded minor made real: two rows in the SAME group share a path — without
    the guard they mint the SAME record URI and silently merge. RED against today's feed."""
    from iladub.feed import table_records, _record_uri
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "SUB", 3: "250"}}, {2: (0, 1)})
    g.add((T, RDF.type, TAB.HierarchicalTable))
    g.add((URIRef(f"{T}-r2"), RDF.type, TAB.AggregationRow))   # feed skips it
    derive_row_groups(g, T, {2: (2, 3, (0, 1))})
    recs = table_records(g)
    assert len(recs) == 2
    ids = [r.row_id for r in recs]
    assert len(set(_record_uri(i) for i in ids)) == 2, ids     # DISTINCT subjects
    assert all(i.startswith("Mackay") for i in ids), ids       # both carry the group path


def test_feed_collision_guard_is_cross_table():
    """I-1 (final review, loop I): the collision-guard multiplicity must be computed ACROSS
    all tables in the graph, not per table — two DIFFERENT HierarchicalTables each with a
    confirmed 'Mackay' group would otherwise mint the SAME urn:iladub:record:Mackay subject,
    a cross-table collision loop I itself created by giving hier tables path identities."""
    from iladub.feed import table_records, _record_uri
    g = Graph()
    t1 = URIRef("urn:doc#h1")
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Mackay Total", 3: "100"}}, {1: (0,)}, table=T)
    _emit(g, {0: {2: "Mackay", 3: "200"},
              1: {2: "Mackay Total", 3: "200"}}, {1: (0,)}, table=t1)
    g.add((T, RDF.type, TAB.HierarchicalTable))
    g.add((t1, RDF.type, TAB.HierarchicalTable))
    derive_row_groups(g, T, {1: (2, 3, (0,))})
    derive_row_groups(g, t1, {1: (2, 3, (0,))})
    recs = table_records(g)
    mackay_recs = [r for r in recs if r.row_id == "Mackay" or r.row_id.startswith("Mackay > ")]
    assert len(mackay_recs) == 2, [r.row_id for r in recs]
    subjects = {_record_uri(r.row_id) for r in mackay_recs}
    assert len(subjects) == 2, subjects                        # DISTINCT subjects across tables


def test_feed_uncovered_rows_keep_opaque_identity():
    from iladub.feed import table_records
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "SUB", 3: "100"},
              3: {2: "Kembla", 3: "999"}}, {1: (0,)})
    g.add((T, RDF.type, TAB.HierarchicalTable))
    g.add((URIRef(f"{T}-r1"), RDF.type, TAB.AggregationRow))
    derive_row_groups(g, T, {1: (2, 3, (0,))})
    recs = table_records(g)
    by_id = {r.row_id: r for r in recs}
    assert "Mackay" in by_id            # single-member group: clean path, no suffix
    assert any(i.endswith("-r3") or i == "h0-r3" for i in by_id), by_id.keys()


def test_e2e_compiled_fixture_carries_the_group(tmp_path):
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.compile import compile_tables
    from iladub.feed import table_records
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions), [r.reason for r in rep.regions]
    groups = list(rep.graph.subjects(RDF.type, TAB.DerivedRowGroup))
    assert len(groups) == 1, groups
    grp = groups[0]
    label = rep.graph.value(grp, TAB.hasLabel)
    assert str(rep.graph.value(label, TAB.cellText)) == "Mackay"    # key from members r0/r1 col 1 (measured)
    covers = {str(u).rsplit("-", 1)[-1] for u in rep.graph.objects(grp, TAB.coversRow)}
    assert covers == {"r0", "r1"}
    recs = table_records(rep.graph)
    assert len(recs) == 3
    pathed = [r.row_id for r in recs if r.row_id.startswith("Mackay > ") or r.row_id == "Mackay"]
    assert len(pathed) == 2 and len(set(pathed)) == 2, [r.row_id for r in recs]
