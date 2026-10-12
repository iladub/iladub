"""The per-cell reading: under `per_cell=True` a matrix row mints one record per entry cell.

Spec: docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md § 3.3, § 3.4,
§ 9.1, § 9.3 (§ 9 overrides). Plan: docs/superpowers/plans/2026-10-12-a-matrix-cell-is-an-observation.md,
Task 2 (decisions D1 to D5).

WHAT A MATRIX IS HERE, read off the graph and nothing else: a row covered by a header node through
`tab:coversRow` (it has a row header path), in a table with no spanning key. Each of its entry
cells becomes one record of up to three concepts: the row key, the column key, the cell.

THE FIXTURES ARE BUILT HERE, triple by triple, in the shape `holon` emits (compare
`tests/test_feed_chain_walk.py::_table`). Two tables hang off page-scoped document IRIs
(`urn:doc/p0#m`, `urn:doc/p1#m`), so the same fragment names different nodes on different pages,
which is what the compile produces and what § 9.1's region rule exists for. MEASURED on apple:
42 of 48 distinct label-cell fragments occur on both pages.

The corpus never reaches CI, so these synthetic arms carry the general claim (spec § 5, last
paragraph). apple's counts are measured in the task report, not pinned here.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.feed import _record_uri, table_records
from iladub.ground import (ROLE_CELL_VALUE, ROLE_COLUMN_KEY, ROLE_ROW_KEY, SHARED_ROW_KEY)

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")

M0 = URIRef("urn:doc/p0#m")
M1 = URIRef("urn:doc/p1#m")

QUARTERS = [("Three Months Ended", "June 27, 2026"), ("Three Months Ended", "June 28, 2025")]


def _label(g, table, name, text, page):
    lc = URIRef(f"{table}-{name}")
    g.add((lc, RDF.type, TAB.LabelCell))
    g.add((table, TAB.hasCell, lc))
    g.add((lc, TAB.cellText, Literal(text)))
    if page is not None:
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
    return lc


def _matrix(g, table, page, columns, rows, *, label_page=True, aggregation=()):
    """A HierarchicalTable with a column header tree and a row header per labelled row.

    `columns` is one header path per leaf column, root to leaf: `("Three Months Ended",
    "June 27, 2026")`, `("Qty",)`, or `()` for a column no header covers. Columns that share a
    path prefix share the parent node; every column has its OWN leaf node, so two columns may
    carry equal paths without one node spanning both.
    `rows` is `(label or None, {column index: cell text})` per row; `None` gives the row no
    header node. Row `r`'s label cell is `{table}-rhl{r}` and column `c`'s is `{table}-chl{c}`.
    """
    g.add((table, RDF.type, TAB.HierarchicalTable))
    lpage = page if label_page else None
    parents = {}
    for c, path in enumerate(columns):
        col = URIRef(f"{table}-c{c}")
        g.add((col, RDF.type, TAB.LeafColumn))
        g.add((table, TAB.hasLeafColumn, col))
        parent = None
        for depth, text in enumerate(path):
            leaf = depth == len(path) - 1
            if leaf:
                h = URIRef(f"{table}-ch{c}")
                g.add((h, TAB.hasLabel, _label(g, table, f"chl{c}", text, lpage)))
            else:
                key = path[:depth + 1]
                if key not in parents:
                    n = len(parents)
                    parents[key] = URIRef(f"{table}-cg{n}")
                    g.add((parents[key], TAB.hasLabel,
                           _label(g, table, f"cgl{n}", text, lpage)))
                h = parents[key]
            g.add((h, RDF.type, TAB.HeaderNode))
            g.add((table, TAB.hasHeaderNode, h))
            g.add((h, TAB.headerLevel, Literal(depth, datatype=XSD.integer)))
            g.add((h, TAB.coversColumn, col))
            if parent is not None:
                g.add((h, TAB.parentHeader, parent))
            parent = h
    for r, (label, cells) in enumerate(rows):
        row = URIRef(f"{table}-r{r}")
        g.add((row, RDF.type, TAB.LeafRow))
        g.add((table, TAB.hasLeafRow, row))
        if r in aggregation:
            g.add((row, RDF.type, TAB.AggregationRow))
        if label is not None:
            h = URIRef(f"{table}-rh{r}")
            g.add((h, RDF.type, TAB.HeaderNode))
            g.add((table, TAB.hasHeaderNode, h))
            g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
            g.add((h, TAB.coversRow, row))
            g.add((h, TAB.hasLabel, _label(g, table, f"rhl{r}", label, lpage)))
        for c, text in cells.items():
            e = URIRef(f"{table}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((table, TAB.hasCell, e))
            g.add((e, TAB.atRow, row))
            g.add((e, TAB.atColumn, URIRef(f"{table}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"urn:doc/src#p{page}-{c}-{r}")))
    return g


def _two_by_two(rows=(("Net sales", {0: "100", 1: "90"}),
                      ("Gross margin", {0: "40", 1: "35"}))):
    return _matrix(Graph(), M0, 0, QUARTERS, list(rows))


def _by_role(record):
    return {c.role: c for c in record.concepts}


def _keys(records, role):
    return [c for r in records for c in r.concepts if c.role == role]


# --- the reading -------------------------------------------------------------------------

def test_a_2x2_matrix_mints_four_records_of_three_concepts():
    recs = table_records(_two_by_two(), per_cell=True)
    assert len(recs) == 4
    assert all(len(r.concepts) == 3 for r in recs)
    read = {(k[ROLE_ROW_KEY].text, k[ROLE_COLUMN_KEY].text, k[ROLE_CELL_VALUE].value)
            for k in map(_by_role, recs)}
    assert read == {
        ("Net sales", "Three Months Ended June 27, 2026", "100"),
        ("Net sales", "Three Months Ended June 28, 2025", "90"),
        ("Gross margin", "Three Months Ended June 27, 2026", "40"),
        ("Gross margin", "Three Months Ended June 28, 2025", "35"),
    }
    for k in map(_by_role, recs):
        # a key's text IS its value; the cell names no field, the contract's role will
        assert k[ROLE_ROW_KEY].value == k[ROLE_ROW_KEY].text
        assert k[ROLE_COLUMN_KEY].value == k[ROLE_COLUMN_KEY].text
        assert k[ROLE_CELL_VALUE].text == ""
    # I4: the feed's own separator is in the id and in no key text
    assert all(" > " not in c.text for r in recs for c in r.concepts)
    assert {r.row_id for r in recs} == {
        "Net sales > Three Months Ended > June 27, 2026",
        "Net sales > Three Months Ended > June 28, 2025",
        "Gross margin > Three Months Ended > June 27, 2026",
        "Gross margin > Three Months Ended > June 28, 2025",
    }


def test_a_label_that_contains_the_separator_keeps_it():
    """I4's other half: ' > ' written by the author is ink, and is not the feed's to remove."""
    g = _matrix(Graph(), M0, 0, [("Assets > Current", "2026")], [("Cash > Bank", {0: "7"})])
    (rec,) = table_records(g, per_cell=True)
    k = _by_role(rec)
    assert k[ROLE_ROW_KEY].text == "Cash > Bank"
    assert k[ROLE_COLUMN_KEY].text == "Assets > Current 2026"


def test_default_mode_is_untouched():
    g = _two_by_two()
    recs = table_records(g)
    assert recs == table_records(g, per_cell=False)
    assert [r.row_id for r in recs] == ["Net sales", "Gross margin"]
    assert [[(c.text, c.value, c.role) for c in r.concepts] for r in recs] == [
        [("Three Months Ended > June 27, 2026", "100", None),
         ("Three Months Ended > June 28, 2025", "90", None)],
        [("Three Months Ended > June 27, 2026", "40", None),
         ("Three Months Ended > June 28, 2025", "35", None)],
    ]


# --- the shared row label (spec § 9.3, D5) -----------------------------------------------

def test_a_repeated_row_label_carries_the_shared_role():
    g = _two_by_two(rows=(("Products", {0: "100", 1: "90"}),
                          ("Products", {0: "40", 1: "35"})))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert [c.text for c in _keys(recs, SHARED_ROW_KEY)] == ["Products"] * 4
    assert _keys(recs, ROLE_ROW_KEY) == []
    assert len(_keys(recs, ROLE_COLUMN_KEY)) == 4
    assert sorted(c.value for c in _keys(recs, ROLE_CELL_VALUE)) == ["100", "35", "40", "90"]


def test_a_label_unique_in_each_of_two_tables_keeps_its_role():
    """Spec § 9.3's unconstructed case: the count is per logical table, not per document."""
    g = _matrix(Graph(), M0, 0, QUARTERS, [("Products", {0: "100", 1: "90"})])
    _matrix(g, M1, 1, QUARTERS, [("Products", {0: "40", 1: "35"})])
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert [c.text for c in _keys(recs, ROLE_ROW_KEY)] == ["Products"] * 4
    assert _keys(recs, SHARED_ROW_KEY) == []


def test_a_label_shared_with_a_row_that_mints_nothing_is_shared():
    """D5: the second 'Products' row has a row header path and only blank cells. It mints no
    record, and the label is still not a key for the row that does."""
    g = _two_by_two(rows=(("Products", {0: "100", 1: "90"}),
                          ("Products", {0: "", 1: ""})))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 2
    assert [c.text for c in _keys(recs, SHARED_ROW_KEY)] == ["Products"] * 2
    assert _keys(recs, ROLE_ROW_KEY) == []


def test_a_chain_is_one_logical_table_for_the_count():
    g = _matrix(Graph(), M0, 0, QUARTERS, [("Products", {0: "100", 1: "90"})])
    _matrix(g, M1, 1, QUARTERS, [("Products", {0: "40", 1: "35"})])
    g.add((M1, TAB.continuesTable, M0))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert [c.text for c in _keys(recs, SHARED_ROW_KEY)] == ["Products"] * 4
    assert _keys(recs, ROLE_ROW_KEY) == []


# --- identity (I2, D3, D4) ---------------------------------------------------------------

def test_two_cells_of_one_row_never_share_an_id():
    """Review Focus 1. Columns 0 and 1 carry EQUAL header paths; columns 2 and 3 carry none.
    The row's IRI is the same for all four cells, so it cannot settle anything between them."""
    same = ("Three Months Ended", "June 27, 2026")
    g = _matrix(Graph(), M0, 0, [same, same, (), ()],
                [("Net sales", {0: "100", 1: "90", 2: "7", 3: "8"})])
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert len({r.row_id for r in recs}) == 4
    assert len({_record_uri(r.row_id) for r in recs}) == 4
    by_value = {_by_role(r)[ROLE_CELL_VALUE].value: r for r in recs}
    for v in ("100", "90"):
        assert _by_role(by_value[v])[ROLE_COLUMN_KEY].text == "Three Months Ended June 27, 2026"
    for v in ("7", "8"):                        # D3: no column key is invented
        assert [c.role for c in by_value[v].concepts] == [ROLE_ROW_KEY, ROLE_CELL_VALUE]


def test_no_two_records_share_a_subject():
    """Review Focus 2. 'A > B C' and 'A B > C' are two ids and ONE slug: `_record_uri` maps
    every run of non-alphanumerics to '_'."""
    g = _matrix(Graph(), M0, 0, [("A", "B C"), ("A B", "C")],
                [("Net sales", {0: "100", 1: "90"}), ("Gross margin", {0: "40", 1: "35"})])
    assert _record_uri("Net sales > A > B C") == _record_uri("Net sales > A B > C")
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert len({r.row_id for r in recs}) == 4
    assert len({_record_uri(r.row_id) for r in recs}) == 4


# --- key regions (I3, spec § 9.1) --------------------------------------------------------

def test_key_regions_are_page_qualified_and_disjoint_from_cell_regions():
    """Two pages, the same label-cell fragments on each (`m-rhl0`, `m-chl0`, ...)."""
    g = _matrix(Graph(), M0, 0, QUARTERS, [("Net sales", {0: "100", 1: "90"})])
    _matrix(g, M1, 1, QUARTERS, [("Total assets", {0: "40", 1: "35"})])
    recs = table_records(g, per_cell=True)
    row_regions = {c.region for c in _keys(recs, ROLE_ROW_KEY)}
    col_regions = {c.region for c in _keys(recs, ROLE_COLUMN_KEY)}
    cell_regions = {c.region for c in _keys(recs, ROLE_CELL_VALUE)}
    assert row_regions == {"p0#m-rhl0", "p1#m-rhl0"}          # one row label cell per page
    assert col_regions == {"p0#m-chl0", "p0#m-chl1", "p1#m-chl0", "p1#m-chl1"}
    assert len(cell_regions) == 4
    assert not (row_regions & col_regions)
    assert not ((row_regions | col_regions) & cell_regions)
    # one label cell, one region: both cells of a row name the same row label cell
    by_text = {}
    for c in _keys(recs, ROLE_ROW_KEY):
        by_text.setdefault(c.text, set()).add(c.region)
    assert all(len(v) == 1 for v in by_text.values())


def test_a_key_region_never_equals_an_entry_region_that_spells_its_fragment():
    """I3's second clause, on the collision the bare fragment would have: an entry cell with no
    `prov:wasDerivedFrom` takes its own IRI fragment as its region, and here that fragment is
    the row label cell's on the other page."""
    g = _matrix(Graph(), M0, 0, QUARTERS, [("Net sales", {0: "100"})])
    e = URIRef("urn:doc/p1#m-rhl0")             # spells p0's row label cell fragment
    g.add((e, RDF.type, TAB.EntryCell))
    g.add((M0, TAB.hasCell, e))
    g.add((e, TAB.atRow, URIRef(f"{M0}-r0")))
    g.add((e, TAB.atColumn, URIRef(f"{M0}-c1")))
    g.add((e, TAB.cellText, Literal("90")))
    recs = table_records(g, per_cell=True)
    cell_regions = {c.region for c in _keys(recs, ROLE_CELL_VALUE)}
    assert "m-rhl0" in cell_regions
    assert not ({c.region for r in recs for c in r.concepts if c.role != ROLE_CELL_VALUE}
                & cell_regions)


def test_a_label_cell_with_no_page_is_named_by_its_own_iri():
    """The brief's seam: `tab:onPage` absent on the label cell. The fragment alone is shared by
    both tables' label cells, so the region is the label cell's IRI, which RDF keeps unique."""
    g = _matrix(Graph(), M0, 0, QUARTERS, [("Net sales", {0: "100"})], label_page=False)
    _matrix(g, M1, 1, QUARTERS, [("Net sales", {0: "40"})], label_page=False)
    recs = table_records(g, per_cell=True)
    assert {c.region for c in _keys(recs, ROLE_ROW_KEY)} == {f"{M0}-rhl0", f"{M1}-rhl0"}
    assert {c.region for c in _keys(recs, ROLE_COLUMN_KEY)} == {f"{M0}-chl0", f"{M1}-chl0"}


# --- the rows the branch does not take ---------------------------------------------------

def test_a_row_without_a_row_header_path_keeps_its_row_record():
    """Review Focus 5: a row is not given a path it does not have."""
    g = _two_by_two(rows=(("Net sales", {0: "100", 1: "90"}),
                          (None, {0: "40", 1: "35"})))
    default = table_records(g)
    recs = table_records(g, per_cell=True)
    assert len(recs) == 3
    assert recs[-1] == default[-1]
    assert len(recs[-1].concepts) == 2
    assert all(c.role is None for c in recs[-1].concepts)


def test_a_table_with_spanning_keys_keeps_the_key_split():
    """D1. 'Mackay' has no parent, no child and two columns: a spanning key. The rows have row
    header paths, and the table still reads by the key split."""
    g = _two_by_two()
    h = URIRef(f"{M0}-span")
    g.add((h, RDF.type, TAB.HeaderNode))
    g.add((M0, TAB.hasHeaderNode, h))
    g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
    g.add((h, TAB.coversColumn, URIRef(f"{M0}-c0")))
    g.add((h, TAB.coversColumn, URIRef(f"{M0}-c1")))
    g.add((h, TAB.hasLabel, _label(g, M0, "spanl", "Mackay", 0)))
    default = table_records(g)
    assert any(c.is_split_key for r in default for c in r.concepts), "fixture does not split"
    recs = table_records(g, per_cell=True)
    assert recs == default
    assert all(c.role is None for r in recs for c in r.concepts)


def test_an_injected_concept_rides_on_every_cell_record():
    """D2: a section caption names no column and is no cell. It rides on each cell's record,
    role-less, as the key split carries it onto each key's record."""
    g = _two_by_two()
    cap = URIRef(f"{M0}-cap0")
    g.add((M0, TAB.hasCaption, cap))
    g.add((cap, RDF.type, TAB.RegionCaption))
    g.add((cap, RDF.type, TAB.SectionCaption))
    g.add((cap, TAB.captionText, Literal("GERALDTON")))
    g.add((cap, TAB.captionRow, Literal(0, datatype=XSD.integer)))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    for r in recs:
        assert len(r.concepts) == 4
        (marker,) = [c for c in r.concepts if c.is_section_marker]
        assert (marker.text, marker.value, marker.role) == ("GERALDTON", "GERALDTON", None)
        assert {c.role for c in r.concepts} == {None, ROLE_ROW_KEY, ROLE_COLUMN_KEY,
                                                ROLE_CELL_VALUE}
        assert r.row_id.startswith("GERALDTON > ")


def test_an_injected_group_key_rides_on_every_cell_record():
    """D2's other population: a derived row group's key, which has a column and is no cell."""
    g = _matrix(Graph(), M0, 0, [("Month",), ("Q1",), ("Q2",)],
                [("North", {1: "100", 2: "90"}), ("South", {1: "40", 2: "35"})])
    grp = URIRef(f"{M0}-rg0")
    g.add((grp, RDF.type, TAB.HeaderNode))
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((M0, TAB.hasHeaderNode, grp))
    lc = _label(g, M0, "rgl0", "Jul", 0)
    g.add((lc, TAB.atColumn, URIRef(f"{M0}-c0")))
    g.add((grp, TAB.hasLabel, lc))
    for r in (0, 1):
        g.add((grp, TAB.coversRow, URIRef(f"{M0}-r{r}")))
        g.add((URIRef(f"{M0}-rh{r}"), TAB.parentHeader, grp))
        g.set((URIRef(f"{M0}-rh{r}"), TAB.headerLevel, Literal(1, datatype=XSD.integer)))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    for r in recs:
        (rider,) = [c for c in r.concepts if c.role is None]
        assert (rider.text, rider.value) == ("Month", "Jul")
        assert len(r.concepts) == 4
    assert {c.text for c in _keys(recs, ROLE_ROW_KEY)} == {"Jul North", "Jul South"}


def test_an_aggregation_row_mints_nothing():
    g = _matrix(Graph(), M0, 0, QUARTERS,
                [("Net sales", {0: "100", 1: "90"}), ("Total", {0: "100", 1: "90"})],
                aggregation=(1,))
    recs = table_records(g, per_cell=True)
    assert len(recs) == 2
    assert {c.text for c in _keys(recs, ROLE_ROW_KEY)} == {"Net sales"}


def test_a_blank_cell_mints_nothing():
    g = _two_by_two(rows=(("Net sales", {0: "100", 1: ""}),
                          ("Gross margin", {0: "40", 1: "35"})))
    recs = table_records(g, per_cell=True)
    assert sorted(c.value for c in _keys(recs, ROLE_CELL_VALUE)) == ["100", "35", "40"]
    assert len(recs) == 3
