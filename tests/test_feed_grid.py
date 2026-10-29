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

from decimal import Decimal

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

from iladub.feed import TAB, _read_grid, _read_table

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
