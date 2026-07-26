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
