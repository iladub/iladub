"""Robust header/body split: a report with missing-value placeholders in a data column and a
text total/footer bottom row must still split at the true data-start. Reproduces the GrainCorp
failure mode synthetically (no third-party PDF). See docs/superpowers/specs/2026-07-26-header-body-split-robust-design.md."""
import os
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
HBS = os.path.join(QDIR, "header-body-split.rq")

# cols: 0=Ship(Text), 1=Date, 2=Qty(Numeric). Row 0 = header labels. Rows 1-4 = data
# (row 3 has a '(blank)' placeholder in the numeric Qty column). Row 5 = a text total row
# ('TOTAL' in the Date column flips its bottom-cell type; Qty stays numeric).
CELLS = [
    (0, 0, "Ship"), (0, 1, "Date"),        (0, 2, "Qty"),
    (1, 0, "Alpha"), (1, 1, "2020-01-02"), (1, 2, "100"),
    (2, 0, "Beta"),  (2, 1, "2020-03-04"), (2, 2, "200"),
    (3, 0, "Gamma"), (3, 1, "2020-05-06"), (3, 2, "(blank)"),   # placeholder in a numeric column
    (4, 0, "Delta"), (4, 1, "2020-07-08"), (4, 2, "300"),
    (5, 0, "Total"), (5, 1, "TOTAL"),      (5, 2, "600"),       # text total row
]


def _split(cells, ncols=3):
    g = celltype.grid_evidence(cells, ncols)
    return celltype.run_scalar(HBS, g)


def test_split_is_true_data_start_despite_placeholders_and_total_row():
    # The header is row 0; data starts at row 1. A robust split must return 1 — the Qty column
    # is Numeric once its '(blank)' placeholder is treated as missing, and the Date column's
    # 'TOTAL' bottom cell must not corrupt the boundary.
    assert _split(CELLS) == 1


# Multi-line (wrapped) header: a single column whose 2-row Text header ("Qty" / "(units)")
# outnumbers its 1-row Numeric body ("100"). If the modal datatype D were computed over ALL rows
# (the pre-fix bug), Text (2 votes) would out-vote Numeric (1 vote), so D=Text -> the column is
# excluded -> split wrongly returns None. With D computed over BODY ROWS ONLY (row>=1), the mode
# is Numeric (the sole body cell) regardless of how many header rows precede it, and the split
# correctly lands at row 2 (the data start).
WRAPPED_HEADER_CELLS = [(0, 0, "Qty"), (1, 0, "(units)"), (2, 0, "100")]


def test_split_survives_multiline_header_outvoting_body():
    assert _split(WRAPPED_HEADER_CELLS, ncols=1) == 2


def test_all_text_grid_still_returns_none():
    # Guard: an all-Text column (no non-Text body datatype ever) must still escalate to None —
    # the body-only mode fix must not manufacture a split where the source supports none.
    assert _split([(0, 0, "Ship"), (1, 0, "Alpha"), (2, 0, "Beta")], ncols=1) is None
