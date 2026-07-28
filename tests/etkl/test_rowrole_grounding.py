"""Loop C.1 — band-local evidence reported to the NEURAL row-role proposer.

The proposer previously saw only row texts, leaf labels and column indices. Three structural
tests (tiling, coverage, ink span) all fail to separate furniture/continuation/level, so the
judgment is correctly NEURAL — but the model was never shown WHAT a fragment would merge into.
These keys close that gap. They are REPORTED evidence: nothing branches on them.
See docs/superpowers/specs/2026-07-28-rowrole-grounding-design.md.
"""
from iladub.etkl.geometry import Word
from iladub.etkl.headers import header_rows_of
from iladub.etkl.rowrole import build_row_reading, row_role_context
from tests.etkl.test_rowrole_reading import (GRID, caption_and_wrap_band,
                                             out_of_grid_caption_band)


def _ctx(band, split):
    return row_role_context(header_rows_of(band, GRID, split), GRID)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def test_merge_candidates_show_what_each_fragment_would_become():
    # The loop's whole thesis, stated by the fixture: "Unit Ref" reads as a column name and
    # "Monday Qty" / "5 May Cost" do not. That contrast is only available if it is reported.
    assert _ctx(caption_and_wrap_band(), 3)["merge_candidates"] == [
        [{"column": 2, "leaf_label": "Qty", "merged": "Monday Qty"},
         {"column": 3, "leaf_label": "Cost", "merged": "5 May Cost"}],
        [{"column": 1, "leaf_label": "Ref", "merged": "Unit Ref"}],
    ]


def test_row_cell_counts_and_leaf_column_count():
    # The solitary-parent signal in raw form: one cell over four leaf columns. Reported as exact
    # counts, NOT as a derived cover set from the parent path — repair_coverage/_centered_run
    # widened "Date of Grain"'s single ink column to covers 1..12 on the real document.
    ctx = _ctx(caption_and_wrap_band(), 3)
    assert ctx["row_cell_counts"] == [2, 1]
    assert ctx["leaf_column_count"] == 4


def test_out_of_grid_cell_yields_no_merge_candidate():
    # Regression guard for the Loop C clamp defect, re-asserted at the context layer: a cell
    # whose ink centre lies outside every column must report None, never a fabricated merge
    # onto the rightmost label.
    ctx = _ctx(out_of_grid_caption_band(), 2)
    assert ctx["merge_candidates"] == [[None]]
    assert ctx["row_columns"] == [[-1]]


def test_merge_candidate_agrees_with_build_row_reading():
    # The context can never disagree with the rewrite: whatever it reports as the merged text
    # must appear in the label build_row_reading actually produces for that column.
    band = caption_and_wrap_band()
    rows = header_rows_of(band, GRID, 3)
    ctx = row_role_context(rows, GRID)
    cand = ctx["merge_candidates"][1][0]           # the "Unit" -> "Ref" continuation
    nodes, _caps, _src = build_row_reading(rows, GRID, ("furniture", "continuation"))
    label = next(n.text for n in nodes if cand["column"] in n.covers)
    assert cand["merged"] in label, (cand, label)


def test_existing_keys_are_unchanged():
    # The added keys must not disturb what the shipped code already reports.
    ctx = _ctx(caption_and_wrap_band(), 3)
    assert ctx["rows"] == [["Monday", "5 May"], ["Unit"]]
    assert ctx["leaf_labels"] == ["Item", "Ref", "Qty", "Cost"]
    assert ctx["row_columns"] == [[2, 3], [1]]


def test_merge_candidate_agrees_with_build_row_reading_when_two_leaf_cells_share_a_column():
    # I-2 regression: leaf_by_col must pick the SAME cell build_row_reading's node search picks
    # (first match, in row order) when two leaf cells' ink centers land in the same column. A
    # wide leaf cell ('STRAY Cost', ink [20,285]) centers at 152.5 -> column 1 -- the same column
    # 'Ref' [155,172] occupies. Plain assignment in row_role_context's leaf_by_col would let
    # 'STRAY Cost' (the LAST cell touching column 1 in iteration order) overwrite 'Ref', while
    # build_row_reading's `next(...)` over the node list always resolves to the FIRST node
    # (in row order) whose covers contain the column -- 'Ref'. The two must never disagree.
    wrap_row = [_w("Unit", 155, 175, 0.0)]
    leaf_row = [_w("Item", 110, 140, 12.0), _w("Ref", 155, 172, 12.0),
                _w("Qty", 205, 230, 12.0), _w("STRAY Cost", 20, 285, 12.0)]
    header_rows = [wrap_row, leaf_row]

    ctx = row_role_context(header_rows, GRID)
    cand = ctx["merge_candidates"][0][0]            # the "Unit" -> column-1 continuation
    assert cand["column"] == 1

    nodes, _caps, _src = build_row_reading(header_rows, GRID, ("continuation",))
    # same first-match-in-row-order rule build_row_reading itself uses (see its docstring)
    label = next(n.text for n in nodes if 1 in n.covers)
    assert cand["merged"] in label, (cand, label)
    # the reviewer's exact demonstration: both sides must agree on "Unit Ref", never
    # "Unit STRAY Cost" (what the pre-fix last-wins assignment fabricated).
    assert cand["merged"] == "Unit Ref"
    assert label == "Unit Ref"


def test_empty_header_rows_reports_empty_evidence():
    # The shipped empty-input contract extends to the new keys — no IndexError, no None.
    ctx = row_role_context([], GRID)
    assert ctx["merge_candidates"] == []
    assert ctx["row_cell_counts"] == []
    assert ctx["leaf_column_count"] == 0
