"""The feed's grid reader (loop A, tab:05; spec 2026-10-29 § 6.2 as amended by § 12).

`_read_grid` reads an adopted `tab:DataGrid` into the `(ordered, rows, row_cols)` shape
`_read_table` returns, plus the grid's stub columns. The fixtures are hand-built from the
triples `datagrid.emit_data_grid` writes (grid -tab:hasGridColumn-> column, -tab:hasGridRow->
row, -tab:hasDataCell-> EntryCell with atRow/atColumn/cellText/onPage/hasBBox), with Task 1's
`tab:rowIndex` (xsd:nonNegativeInteger) and `tab:colIndex` (xsd:integer).

Each fixture is built so the property it pins DISAGREES with every other order a reader could
fall back on: IRI suffix order, bbox y0 order, colX0 order. A reader that used any of those
would fail here, not pass by coincidence.
"""
from __future__ import annotations

import re
from decimal import Decimal

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

from iladub.feed import (TAB, _grid_row_keys, _read_grid, _read_table, _row_discriminator,
                         table_records)
from iladub.ground import ROLE_CELL_VALUE, ROLE_ROW_KEY, SHARED_ROW_KEY

G = "urn:test:doc#p1-datagrid"


def _bbox(g: Graph, cell: URIRef, x0: float, y0: float) -> None:
    b = URIRef(f"{cell}-bbox")
    g.add((b, RDF.type, TAB.BBox))
    g.add((b, TAB.x0, Literal(Decimal(str(x0)))))
    g.add((b, TAB.y0, Literal(Decimal(str(y0)))))
    g.add((b, TAB.x1, Literal(Decimal(str(x0 + 10)))))
    g.add((b, TAB.y1, Literal(Decimal(str(y0 + 8)))))
    g.add((cell, TAB.hasBBox, b))


def _grid(cols, rows) -> tuple[Graph, URIRef]:
    """cols: [(k_suffix, colIndex, is_measure, colX0)];
    rows: [(r_suffix, rowIndex, y0, is_aggregation, {k_suffix: (text, unshown_or_None)})]."""
    g = Graph()
    grid = URIRef(G)
    g.add((grid, RDF.type, TAB.DataGrid))
    g.add((grid, TAB.onPage, Literal(1, datatype=XSD.integer)))
    for k, idx, is_measure, x0 in cols:
        c = URIRef(f"{G}-c{k}")
        g.add((c, RDF.type, TAB.GridColumn))
        if is_measure:
            g.add((c, RDF.type, TAB.MeasureColumn))
        g.add((grid, TAB.hasGridColumn, c))
        g.add((c, TAB.colIndex, Literal(idx, datatype=XSD.integer)))
        g.add((c, TAB.colX0, Literal(Decimal(str(x0)))))
        g.add((c, TAB.colX1, Literal(Decimal(str(x0 + 40)))))
    for r, idx, y0, is_agg, cells in rows:
        row = URIRef(f"{G}-r{r}")
        g.add((row, RDF.type, TAB.LeafRow))
        g.add((row, TAB.rowIndex, Literal(idx, datatype=XSD.nonNegativeInteger)))
        if is_agg:
            g.add((row, RDF.type, TAB.AggregationRow))
            g.add((row, RDF.type, TAB.DetectedAggregationRow))
        g.add((grid, TAB.hasGridRow, row))
        for k, (text, unshown) in cells.items():
            e = URIRef(f"{G}-r{r}c{k}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((grid, TAB.hasDataCell, e))
            g.add((e, TAB.atRow, row))
            g.add((e, TAB.atColumn, URIRef(f"{G}-c{k}")))
            g.add((e, TAB.cellText, Literal(text)))
            if unshown is not None:
                g.add((e, TAB.unshownText, Literal(unshown)))
            g.add((e, TAB.onPage, Literal(1, datatype=XSD.integer)))
            _bbox(g, e, 100.0 + 50 * int(k), y0)
    return g, grid


def _record_table(rows) -> tuple[Graph, URIRef]:
    """The same cases on a tab:RecordTable: rows as in `_grid`, every cell in one column."""
    g = Graph()
    t = URIRef("urn:test:doc#p1-table0")
    g.add((t, RDF.type, TAB.RecordTable))
    col = URIRef(f"{t}-c1")
    for r, _idx, y0, is_agg, cells in rows:
        row = URIRef(f"{t}-r{r}")
        if is_agg:
            g.add((row, RDF.type, TAB.AggregationRow))
        for k, (text, unshown) in cells.items():
            e = URIRef(f"{t}-r{r}c{k}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, row))
            g.add((e, TAB.atColumn, col))
            g.add((e, TAB.cellText, Literal(text)))
            if unshown is not None:
                g.add((e, TAB.unshownText, Literal(unshown)))
            g.add((e, TAB.onPage, Literal(1, datatype=XSD.integer)))
            _bbox(g, e, 100.0, y0)
    return g, t


def _texts(rows) -> set[str]:
    return {entry[2].value for entries in rows.values() for entry in entries}


# ---------------------------------------------------------------------------------- O2


def test_O2_ordered_follows_row_index_not_y0_and_not_iri():
    # rowIndex order: r1 (0), r2 (1), r0 (2).
    # y0 order:       r2 (10), r0 (20), r1 (30).
    # IRI order:      r0, r1, r2.
    # Three distinct orders, so only a rowIndex reader gets [r1, r2, r0].
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [
        ("0", 2, 20.0, False, {"0": ("Gamma", None), "1": ("3", None)}),
        ("1", 0, 30.0, False, {"0": ("Alpha", None), "1": ("1", None)}),
        ("2", 1, 10.0, False, {"0": ("Beta", None), "1": ("2", None)}),
    ]
    g, grid = _grid(cols, rows)
    ordered, rows_out, row_cols, _stubs = _read_grid(g, grid, stubs_are_entries=True)
    assert ordered == [URIRef(f"{G}-r1"), URIRef(f"{G}-r2"), URIRef(f"{G}-r0")]
    assert set(rows_out) == set(ordered) == set(row_cols)


# ---------------------------------------------------------------------------------- O6

_KEEP = ("1", 0, 10.0, False, {"1": ("42", None)})

# (case, the case row) — every case cell sits in the measure column "1".
_SKIP_CASES = [
    ("aggregation-row", ("2", 1, 20.0, True, {"1": ("99", None)})),
    ("blank-cell", ("2", 1, 20.0, False, {"1": ("", None)})),
    ("nil-spelling-em-dash", ("2", 1, 20.0, False, {"1": ("—", None)})),
    ("unshown-empty", ("2", 1, 20.0, False, {"1": ("", "17")})),
]
_RAISE_CASE = ("2", 1, 20.0, False, {"1": ("17", "17")})


def _read_by(reader: str, rows):
    if reader == "grid":
        cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
        g, grid = _grid(cols, rows)
        ordered, out, row_cols, _ = _read_grid(g, grid, stubs_are_entries=True)
        return ordered, out, row_cols
    g, t = _record_table(rows)
    return _read_table(g, t)


@pytest.mark.parametrize("reader", ["grid", "table"])
@pytest.mark.parametrize("case,row", _SKIP_CASES, ids=[c for c, _ in _SKIP_CASES])
def test_O6_the_shared_skip_rules_drop_the_same_cells_from_both_readers(reader, case, row):
    ordered, rows_out, _ = _read_by(reader, [_KEEP, row])
    assert _texts(rows_out) == {"42"}, case
    assert len(ordered) == 1, case


@pytest.mark.parametrize("reader", ["grid", "table"])
def test_O6_an_unshown_cell_with_text_raises_in_both_readers(reader):
    with pytest.raises(AssertionError, match="unshownText"):
        _read_by(reader, [_KEEP, _RAISE_CASE])


# ---------------------------------------------------------------------------------- O3


def _one_stub_grid():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [("0", 0, 10.0, False, {"0": ("Revenue", None), "1": ("100", None)})]
    return _grid(cols, rows)


def test_O3_a_stub_cell_is_not_an_entry_when_stubs_are_keys():
    g, grid = _one_stub_grid()
    _ordered, rows_out, _rc, stubs = _read_grid(g, grid, stubs_are_entries=False)
    assert _texts(rows_out) == {"100"}
    assert stubs == (URIRef(f"{G}-c0"),)


def test_O3_a_stub_cell_is_an_entry_when_stubs_are_entries():
    g, grid = _one_stub_grid()
    _ordered, rows_out, _rc, stubs = _read_grid(g, grid, stubs_are_entries=True)
    assert _texts(rows_out) == {"Revenue", "100"}
    assert stubs == (URIRef(f"{G}-c0"),)


# ---------------------------------------------------------------------------------- O4


def test_O4_stubs_follow_col_index_not_iri_and_not_col_x0():
    # colIndex order: c2 (0), c0 (1), c1 (2).
    # IRI order:      c0, c1, c2.
    # colX0 order:    c1 (5), c2 (15), c0 (25).
    cols = [("0", 1, False, 25.0), ("1", 2, False, 5.0), ("2", 0, False, 15.0),
            ("3", 3, True, 80.0)]
    rows = [("0", 0, 10.0, False, {"0": ("a", None), "1": ("b", None), "2": ("c", None),
                                   "3": ("7", None)})]
    g, grid = _grid(cols, rows)
    _o, _r, _rc, stubs = _read_grid(g, grid, stubs_are_entries=False)
    assert stubs == (URIRef(f"{G}-c2"), URIRef(f"{G}-c0"), URIRef(f"{G}-c1"))


# ===================================================================== Task 3: table_records
#
# The grid branch of `table_records` (spec § 6.2 as amended by § 12.2). Every fixture below is
# built with `_grid`, so a grid row carries no `tab:onPage` and no `tab:hasLabel`, as on every
# corpus grid (§ 12.2, row-region bullet): its region is `_label_region(graph, row)[1]`.

def _row(r: str) -> URIRef:
    return URIRef(f"{G}-r{r}")


def _concepts_by_role(recs, role):
    return [c for rec in recs for c in rec.concepts if c.role == role]


def _O3_grid():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0), ("2", 2, True, 110.0)]
    rows = [
        ("0", 0, 10.0, False, {"0": ("Revenue", None), "1": ("100", None), "2": ("90", None)}),
        ("1", 1, 20.0, False, {"0": ("Cost", None), "1": ("40", None), "2": ("35", None)}),
    ]
    return _grid(cols, rows)


def test_a_O3_per_row_one_record_per_row_and_the_stub_is_a_concept():
    g, _grid_ = _O3_grid()
    recs = table_records(g)
    assert len(recs) == 2
    assert [sorted(c.value for c in r.concepts) for r in recs] == [
        ["100", "90", "Revenue"], ["35", "40", "Cost"]]


def test_a_O3_per_cell_the_stub_is_the_row_key_and_never_a_value():
    g, _grid_ = _O3_grid()
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    values = {c.value for c in _concepts_by_role(recs, ROLE_CELL_VALUE)}
    assert values == {"100", "90", "40", "35"}
    assert not values & {"Revenue", "Cost"}
    for rec in recs:
        keys = [c for c in rec.concepts if c.role == ROLE_ROW_KEY]
        assert len(keys) == 1
        (cell,) = [c for c in rec.concepts if c.role == ROLE_CELL_VALUE]
        assert keys[0].text == keys[0].value == {"100": "Revenue", "90": "Revenue",
                                                 "40": "Cost", "35": "Cost"}[cell.value]


def test_b_O4_the_row_key_joins_the_stubs_in_col_index_order():
    # colIndex order c2, c0, c1 -> "c a b"; IRI order would give "a b c", colX0 "b c a".
    cols = [("0", 1, False, 25.0), ("1", 2, False, 5.0), ("2", 0, False, 15.0),
            ("3", 3, True, 80.0)]
    rows = [("0", 0, 10.0, False, {"0": ("a", None), "1": ("b", None), "2": ("c", None),
                                   "3": ("7", None)})]
    g, grid = _grid(cols, rows)
    assert _grid_row_keys(g, grid) == {_row("0"): ("c a b", str(_row("0")))}
    recs = table_records(g, per_cell=True)
    assert [c.text for c in _concepts_by_role(recs, ROLE_ROW_KEY)] == ["c a b"]


def test_c_O5_a_stubless_grid_contributes_nothing_and_raises_nothing():
    cols = [("0", 0, True, 10.0), ("1", 1, True, 60.0)]
    rows = [("0", 0, 10.0, False, {"0": ("1", None), "1": ("2", None)})]
    g, _grid_ = _grid(cols, rows)
    assert table_records(g) == []
    assert table_records(g, per_cell=True) == []


def test_d_O7_three_Other_rows_are_three_shared_rows_of_six_records():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0), ("2", 2, True, 110.0)]
    rows = [(str(i), i, 10.0 * (i + 1), False,
             {"0": ("Other", None), "1": (f"{i}1", None), "2": (f"{i}2", None)})
            for i in range(3)]
    g, _grid_ = _grid(cols, rows)
    recs = table_records(g, per_cell=True)
    assert len(recs) == 6
    keys = [c for rec in recs for c in rec.concepts
            if c.role in (ROLE_ROW_KEY, SHARED_ROW_KEY)]
    assert len(keys) == 6
    assert {c.role for c in keys} == {SHARED_ROW_KEY}
    assert len({r.row_id for r in recs}) == 6
    assert {c.region for c in keys} == {str(_row(str(i))) for i in range(3)}


def test_e_O2_per_row_records_follow_row_index():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [
        ("0", 2, 20.0, False, {"0": ("Gamma", None), "1": ("3", None)}),
        ("1", 0, 30.0, False, {"0": ("Alpha", None), "1": ("1", None)}),
        ("2", 1, 10.0, False, {"0": ("Beta", None), "1": ("2", None)}),
    ]
    g, _grid_ = _grid(cols, rows)
    assert [r.row_id for r in table_records(g)] == ["Alpha", "Beta", "Gamma"]


def test_f_a_grid_with_a_spanning_key_raises_naming_the_grid():
    g, grid = _O3_grid()
    h = URIRef(f"{G}-h0")
    lab = URIRef(f"{G}-h0-label")
    g.add((grid, TAB.hasHeaderNode, h))
    g.add((h, TAB.hasLabel, lab))
    g.add((lab, TAB.cellText, Literal("Spanner")))
    g.add((h, TAB.coversColumn, URIRef(f"{G}-c1")))
    g.add((h, TAB.coversColumn, URIRef(f"{G}-c2")))
    for per_cell in (False, True):
        with pytest.raises(AssertionError, match=re.escape(str(grid))):
            table_records(g, per_cell=per_cell)


def test_g_O6_an_aggregation_row_mints_no_record_in_either_mode():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [
        ("0", 0, 10.0, False, {"0": ("A", None), "1": ("1", None)}),
        ("1", 1, 20.0, True, {"0": ("Total", None), "1": ("1", None)}),
    ]
    g, _grid_ = _grid(cols, rows)
    for per_cell in (False, True):
        recs = table_records(g, per_cell=per_cell)
        assert len(recs) == 1
        assert "Total" not in {c.value for c in recs[0].concepts}
        assert "Total" not in recs[0].row_id


def test_h_review_focus_1_a_table_row_and_a_grid_row_sharing_a_rid():
    tg, t = _record_table([("0", 0, 10.0, False, {"1": ("Gamma", None)})])
    table_row = URIRef(f"{t}-r0")
    rid = _row_discriminator(tg, table_row)
    gg, _grid_ = _grid([("0", 0, False, 10.0), ("1", 1, True, 60.0)],
                       [("0", 0, 10.0, False, {"0": (rid, None), "1": ("5", None)})])
    alone = table_records(tg)
    both = table_records(tg + gg)
    assert len(both) == 2
    assert len({r.row_id for r in both}) == 2
    table_rec = [r for r in both if "Gamma" in {c.value for c in r.concepts}]
    assert len(table_rec) == 1
    assert table_rec[0].concepts == alone[0].concepts


def test_i_review_focus_2_no_header_node_gives_one_id_per_value_cell():
    g, _grid_ = _O3_grid()
    recs = table_records(g, per_cell=True)
    assert len(recs) == 4
    assert len({r.row_id for r in recs}) == 4


def test_j_review_focus_3_a_blank_stub_row_takes_the_opaque_path():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0), ("2", 2, True, 110.0)]
    rows = [("0", 0, 10.0, False, {"0": ("", None), "1": ("1", None), "2": ("2", None)})]
    g, grid = _grid(cols, rows)
    assert _grid_row_keys(g, grid) == {}
    opaque = _row_discriminator(g, _row("0"))
    for per_cell in (False, True):
        recs = table_records(g, per_cell=per_cell)
        assert {c.value for rec in recs for c in rec.concepts} == {"1", "2"}
        assert {r.row_id for r in recs} == {opaque}


def test_k_review_focus_4_a_label_only_row():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    g, _grid_ = _grid(cols, [("0", 0, 10.0, False, {"0": ("Assets", None)})])
    per_row = table_records(g)
    assert len(per_row) == 1
    assert [c.value for c in per_row[0].concepts] == ["Assets"]
    assert table_records(g, per_cell=True) == []


def test_k_review_focus_4_a_label_only_Other_makes_a_valued_Other_shared():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [
        ("0", 0, 10.0, False, {"0": ("Other", None)}),
        ("1", 1, 20.0, False, {"0": ("Other", None), "1": ("9", None)}),
    ]
    g, _grid_ = _grid(cols, rows)
    recs = table_records(g, per_cell=True)
    assert len(recs) == 1
    (key,) = [c for c in recs[0].concepts if c.text == "Other"]
    assert key.role == SHARED_ROW_KEY


def test_grid_row_keys_covers_aggregation_rows_and_rows_with_no_value_cell():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [
        ("0", 0, 10.0, False, {"0": ("A", None)}),
        ("1", 1, 20.0, True, {"0": ("Total", None), "1": ("1", None)}),
    ]
    g, grid = _grid(cols, rows)
    assert _grid_row_keys(g, grid) == {_row("0"): ("A", str(_row("0"))),
                                       _row("1"): ("Total", str(_row("1")))}


# R213 on stub cells (controller ruling, Task 2 review): a stub cell is the row's key, so it
# never reaches `_read_entry` in per-cell mode. `_grid_row_keys` applies the same rules.

def test_an_unshown_stub_with_text_raises():
    cols = [("0", 0, False, 10.0), ("1", 1, True, 60.0)]
    rows = [("0", 0, 10.0, False, {"0": ("Revenue", "Revenue"), "1": ("1", None)})]
    g, grid = _grid(cols, rows)
    with pytest.raises(AssertionError, match="unshownText"):
        _grid_row_keys(g, grid)
    with pytest.raises(AssertionError, match="unshownText"):
        table_records(g, per_cell=True)


@pytest.mark.parametrize("stub", [("", "Revenue"), ("—", None), ("", None)],
                         ids=["unshown-empty", "nil-spelling", "blank"])
def test_an_unshown_empty_or_blank_stub_contributes_no_text(stub):
    cols = [("0", 0, False, 10.0), ("1", 1, False, 30.0), ("2", 2, True, 60.0)]
    rows = [("0", 0, 10.0, False, {"0": stub, "1": ("Revenue", None), "2": ("1", None)})]
    g, grid = _grid(cols, rows)
    assert _grid_row_keys(g, grid) == {_row("0"): ("Revenue", str(_row("0")))}
