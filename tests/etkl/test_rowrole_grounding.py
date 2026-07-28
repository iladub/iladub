"""Loop C.1 — band-local evidence reported to the NEURAL row-role proposer.

The proposer previously saw only row texts, leaf labels and column indices. Three structural
tests (tiling, coverage, ink span) all fail to separate furniture/continuation/level, so the
judgment is correctly NEURAL — but the model was never shown WHAT a fragment would merge into.
These keys close that gap. They are REPORTED evidence: nothing branches on them.
See docs/superpowers/specs/2026-07-28-rowrole-grounding-design.md.
"""
from iladub.etkl.headers import header_rows_of
from iladub.etkl.rowrole import build_row_reading, row_role_context
from tests.etkl.test_rowrole_reading import (GRID, caption_and_wrap_band,
                                             out_of_grid_caption_band)


def _ctx(band, split):
    return row_role_context(header_rows_of(band, GRID, split), GRID)


def test_merge_candidates_show_what_each_fragment_would_become():
    # The loop's whole thesis, stated by the fixture: "Unit Ref" reads as a column name and
    # "Monday Qty" / "5 May Cost" do not. That contrast is only available if it is reported.
    assert _ctx(caption_and_wrap_band(), 3)["merge_candidates"] == [
        [{"column": 2, "leaf_label": "Qty", "merged": "Monday Qty"},
         {"column": 3, "leaf_label": "Cost", "merged": "5 May Cost"}],
        [{"column": 1, "leaf_label": "Ref", "merged": "Unit Ref"}],
    ]


def test_row_cell_counts_and_leaf_column_count():
    # The solitary-parent signal in raw form: one cell over four leaf columns. Reported as
    # exact counts, NOT as _covers_for_cell's symmetrized covers (which fabricated
    # "Date of Grain -> covers 1..12" from single-column ink).
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


def test_empty_header_rows_reports_empty_evidence():
    # The shipped empty-input contract extends to the new keys — no IndexError, no None.
    ctx = row_role_context([], GRID)
    assert ctx["merge_candidates"] == []
    assert ctx["row_cell_counts"] == []
    assert ctx["leaf_column_count"] == 0
