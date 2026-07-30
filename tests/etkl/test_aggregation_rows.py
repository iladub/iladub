"""Loop H — arithmetic subtotal detection (residue R4, detection half).

A SPARSE row (2 cells vs the modal shape) whose numeric measure equals the token-sum of the
non-aggregation rows above it — back to the previous confirmed aggregation of same-or-outer level
(the label's COLUMN encodes the level) — is an aggregation row, not a data record.

LANGUAGE-INDEPENDENT BY CONSTRUCTION: the label text is never read. A ' Total' suffix test is the
tuned constant of natural language and is expressly forbidden (spec §5).
See docs/superpowers/specs/2026-07-30-subtotal-rows-design.md §2 Findings 4-5.
"""
from iladub.etkl.geometry import Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.rows import RowBand, detect_aggregation_rows

GRID = LeafGrid((0.0, 50.0, 100.0, 150.0, 200.0), 4, 50.0, 1.0)
COLS = {0: (5, 45), 1: (55, 95), 2: (105, 145), 3: (155, 195)}


def _row(top, cells):
    """cells: dict of col->text. Builds a RowBand with one cell per named column."""
    out = []
    for col, text in sorted(cells.items()):
        x0, x1 = COLS[col]
        w = Word(text, x0, x1, top, top + 8.0)
        from iladub.etkl.cells import _cell_from
        out.append(_cell_from([w], 0))
    return RowBand(top, top + 8.0, tuple(out))


def _rows(*specs):
    return tuple(_row(10.0 * i, spec) for i, spec in enumerate(specs))


def test_single_level_group_confirms():
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg == {2: (1, 3, (0, 1))}


def test_label_text_is_never_read():
    # Same structure, label in another language entirely — identical result.
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "Zwischensumme", 3: "250"})
    assert detect_aggregation_rows(rows, GRID) == {2: (1, 3, (0, 1))}


def test_two_level_nesting_by_label_column():
    # Port totals label in c1; the month total labels in c0 (outer level) and sums the DATA
    # rows, with the inner aggregations excluded as members.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[1] == (1, 3, (0,))
    assert agg[3] == (1, 3, (2,))
    assert agg[4] == (0, 3, (0, 2))          # data rows only; inner aggs excluded


def test_inner_group_boundary_is_the_previous_same_level_agg():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[3] == (1, 3, (2,))            # stops at row 1 (same level), members = row 2 only


def test_blank_member_contributes_nothing():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "-"},
                 {1: "SUB", 3: "100"})
    assert detect_aggregation_rows(rows, GRID)[2] == (1, 3, (0, 1))


def test_blank_total_is_never_confirmed():
    # The Port Kembla honesty: a candidate with no numeric measure cannot be verified.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "-"},
                 {1: "SUB", 3: "-"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_non_reconciling_sparse_row_is_not_confirmed():
    # A lookup/reference row that happens to be sparse is NOT a subtotal.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "NOTE", 3: "999"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_multi_value_cell_sums_its_tokens():
    # The author may box two lines together (no hrule drawn between them — measured on the
    # real report: two TBA bookings in one box, measure cell '20,000 30,000'). The cell's
    # contribution is the sum of its numeric tokens.
    rows = _rows({0: "Jul", 1: "A", 2: "V1 V2", 3: "100 150"},
                 {1: "SUB", 3: "250"})
    assert detect_aggregation_rows(rows, GRID)[1] == (1, 3, (0,))


def test_unconfirmed_sparse_row_is_a_member_of_later_sums():
    # The cascade: a blank-total row stays a row AND contributes its token-sum (0) to the
    # enclosing group — measured on the real report (Portland Total reconciles past the
    # blank Fisherman total above it).
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "BLANKSUB", 3: "-"},
                 {1: "B", 2: "V2", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert 1 not in agg
    assert agg[3] == (0, 3, (0, 1, 2))
