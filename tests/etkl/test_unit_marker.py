"""The accounting currency-marker column (spec 2026-08-05-unit-marker-column-design.md).

A borderless column whose every non-blank cell is the SAME currency symbol is a unit
marker on its numeric right neighbor, not a column of the table. Recognition is the
unit-marker-column.rq AXIOM over a DEDICATED typed-cell evidence graph (marker-local
tab:CurrencyGlyph typing — the shared celltype lattice is deliberately untouched so
every existing query stays byte-identical). Measured driver: apple p0, where `$`
columns fabricate ncols=9 for a 5-column statement."""
from iladub.etkl.unitmarker import derive_marker_columns

# The apple accounting shape: label col 0, `$` marker col 1 (first + total rows only),
# numeric value col 2.
APPLE_SHAPE = [
    (0, 0, "Net sales:"),
    (1, 0, "Products"), (1, 1, "$"), (1, 2, "78,678"),
    (2, 0, "Services"),              (2, 2, "30,739"),
    (3, 0, "Total net sales"), (3, 1, "$"), (3, 2, "109,417"),
]


def test_same_symbol_column_with_numeric_neighbor_is_derived():
    assert derive_marker_columns(APPLE_SHAPE, 3) == ((1, "$"),)


def test_footnote_star_column_is_refused():
    # `*` is not a currency symbol — the column stays an ordinary column.
    cells = [(r, c, t if t != "$" else "*") for (r, c, t) in APPLE_SHAPE]
    assert derive_marker_columns(cells, 3) == ()


def test_mixed_symbols_are_refused():
    # $ and € in one column: not the SAME symbol -> no absorption.
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "10"), (2, 1, "€"), (2, 2, "20")]
    assert derive_marker_columns(cells, 3) == ()


def test_symbol_column_without_numeric_neighbor_is_refused():
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "abc"), (2, 1, "$"), (2, 2, "def")]
    assert derive_marker_columns(cells, 3) == ()


def test_column_with_any_non_symbol_cell_is_refused():
    # One stray text cell among the symbols disqualifies the whole column.
    cells = APPLE_SHAPE + [(2, 1, "note")]
    assert derive_marker_columns(cells, 3) == ()


def test_blank_cells_do_not_disqualify():
    # Blanks are wildcards, exactly as in the split query's Blank convention.
    cells = APPLE_SHAPE + [(2, 1, "-")]
    assert derive_marker_columns(cells, 3) == ((1, "$"),)


def test_two_marker_columns_both_derive():
    cells = [
        (0, 0, "A"), (0, 1, "$"), (0, 2, "10"), (0, 3, "$"), (0, 4, "20"),
        (1, 0, "B"), (1, 1, "$"), (1, 2, "11"), (1, 3, "$"), (1, 4, "21"),
    ]
    assert derive_marker_columns(cells, 5) == ((1, "$"), (3, "$"))
