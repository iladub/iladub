"""Loop C — build_row_reading: the pure structural rewrite under a proposed role vector.

The fixture reproduces GrainCorp's shape: a leaked caption row, a wrap-continuation row, and a
leaf label row, with UNIFORM 12pt line spacing so group_wrapped's wrap-continuation gate — the
adaptive `gap < lead` median-gap test (the fixture-tuned `0.9 x lead` margin was retired in B3,
2026-07-22, commit 947f6fa) — cannot absorb the header rows: lead is also 12pt here, so
`12 < 12` is false. This is the exact condition where header leading equals body leading.
Verified during planning: merge_tiling_ok is False before, True under the intended reading.
See docs/superpowers/specs/2026-07-26-header-row-roles-design.md.
"""
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import (header_body_split, header_rows_of, infer_header_tree,
                                 merge_tiling_ok)
from iladub.etkl.rowrole import build_row_reading, row_role_context

GRID = LeafGrid((100.0, 150.0, 200.0, 250.0, 300.0), 4, 50.0, 1.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def caption_and_wrap_band():
    """Row 0 = a leaked date caption, row 1 = a wrap fragment over column 1, row 2 = the leaf
    labels, rows 3-4 = body. Coordinates are load-bearing — do not change them."""
    cap = [_w("Monday", 205, 240, 0.0), _w("5 May", 242, 262, 0.0)]
    wrap = [_w("Unit", 155, 175, 12.0)]
    leaf = [_w("Item", 110, 140, 24.0), _w("Ref", 155, 172, 24.0),
            _w("Qty", 205, 230, 24.0), _w("Cost", 255, 285, 24.0)]
    d1 = [_w("aa", 110, 140, 36.0), _w("R1", 155, 172, 36.0),
          _w("10", 205, 230, 36.0), _w("1.5", 255, 285, 36.0)]
    d2 = [_w("bb", 110, 140, 48.0), _w("R2", 155, 172, 48.0),
          _w("20", 205, 230, 48.0), _w("2.5", 255, 285, 48.0)]
    return Band((_line(cap, 0.0), _line(wrap, 12.0), _line(leaf, 24.0),
                 _line(d1, 36.0), _line(d2, 48.0)), 0.0, 58.0)


def test_fixture_reproduces_the_escalation():
    # the red condition: the geometric tree does NOT tile (level-0 overlap on column 2)
    band = caption_and_wrap_band()
    assert header_body_split(band, GRID) == 3
    assert merge_tiling_ok(infer_header_tree(band, GRID, 3), GRID) is False


def test_header_rows_of_returns_three_unabsorbed_header_rows():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert [len(r) for r in rows] == [2, 1, 4]


def test_context_reports_geometry_without_deciding():
    ctx = row_role_context(header_rows_of(caption_and_wrap_band(), GRID, 3), GRID)
    assert ctx["rows"] == [["Monday", "5 May"], ["Unit"]]        # non-leaf rows only
    assert ctx["leaf_labels"] == ["Item", "Ref", "Qty", "Cost"]
    assert ctx["row_columns"] == [[2, 3], [1]]                   # ink-center columns


def test_furniture_plus_continuation_tiles_with_the_merged_label():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    out = build_row_reading(rows, GRID, ("furniture", "continuation"))
    assert out is not None
    nodes, captions, source_cells = out
    assert [n.text for n in nodes] == ["Item", "Unit Ref", "Qty", "Cost"]
    assert merge_tiling_ok(nodes, GRID) is True
    assert captions == ((0, "Monday"), (0, "5 May"))
    # every header-region cell is recorded for the conservation oracle (2 + 1 + 4)
    assert len(source_cells) == 7


def test_all_level_reproduces_the_failing_tree():
    # the contract guard at the unit level: reading every row as a genuine level must NOT
    # invent a tiling — it reproduces today's tree and stays illegal.
    band = caption_and_wrap_band()
    rows = header_rows_of(band, GRID, 3)
    nodes, _caps, _src = build_row_reading(rows, GRID, ("level", "level"))
    assert merge_tiling_ok(nodes, GRID) is False
    assert nodes == infer_header_tree(band, GRID, 3)


def test_wrong_length_role_vector_is_refused():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert build_row_reading(rows, GRID, ("furniture",)) is None


def test_unknown_role_is_refused():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert build_row_reading(rows, GRID, ("furniture", "wrap")) is None


def out_of_grid_caption_band():
    """Row 0's cell sits entirely LEFT of the grid boundaries (100..300): ink center 40, a
    page-margin-flush leaked line — reproduces the Critical finding's repro case (a text
    fragment with no covering column at all). Coordinates are load-bearing."""
    cap = [_w("Report", 20, 60, 0.0)]
    leaf = [_w("Item", 110, 140, 12.0), _w("Ref", 155, 172, 12.0),
            _w("Qty", 205, 230, 12.0), _w("Cost", 255, 285, 12.0)]
    d1 = [_w("aa", 110, 140, 24.0), _w("R1", 155, 172, 24.0),
          _w("10", 205, 230, 24.0), _w("1.5", 255, 285, 24.0)]
    d2 = [_w("bb", 110, 140, 36.0), _w("R2", 155, 172, 36.0),
          _w("20", 205, 230, 36.0), _w("2.5", 255, 285, 36.0)]
    return Band((_line(cap, 0.0), _line(leaf, 12.0), _line(d1, 24.0), _line(d2, 36.0)), 0.0, 46.0)


def test_out_of_grid_continuation_is_refused():
    # regression test for the Critical finding: column_of CLAMPED an out-of-grid ink center
    # onto the rightmost column, silently welding "Report" onto "Cost" -> "Report Cost". The
    # fix refuses instead of guessing a placement.
    rows = header_rows_of(out_of_grid_caption_band(), GRID, 2)
    assert build_row_reading(rows, GRID, ("continuation",)) is None


def test_context_reports_negative_one_for_out_of_grid_cell():
    ctx = row_role_context(header_rows_of(out_of_grid_caption_band(), GRID, 2), GRID)
    assert ctx["rows"] == [["Report"]]
    assert ctx["row_columns"] == [[-1]]


def test_empty_header_rows_refuses_and_returns_empty_context():
    assert build_row_reading([], GRID, ()) is None
    assert row_role_context([], GRID) == {"rows": [], "leaf_labels": [], "row_columns": []}


def test_unplaceable_continuation_is_refused():
    # "Monday"/"5 May" sit over columns 2 and 3; reading row 0 as a continuation is placeable.
    # Reading row 1 ("Unit", column 1) as a continuation while ALSO removing column 1's leaf
    # label is not expressible here, so instead assert the guard directly: a continuation cell
    # over a column no leaf node covers is refused.
    band = caption_and_wrap_band()
    rows = header_rows_of(band, GRID, 3)
    # drop the leaf label that covers column 1, leaving column 1 uncovered at the leaf level
    stripped = [rows[0], rows[1], [c for c in rows[2] if c.text != "Ref"]]
    assert build_row_reading(stripped, GRID, ("furniture", "continuation")) is None
