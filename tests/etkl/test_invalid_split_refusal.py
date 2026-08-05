"""R41: a derived header/body split must leave >=1 body row. A $-sandwiched numeric column
(first and last body rows Currency, interior Numeric) pushes s_col = MAX(mismatch row)+1 one
past the band in every data column; pre-fix the AXIOM returned split == len(band.lines) and
every band.lines[split] indexer crashed (the apple-fy2026q3 IndexError, headers.py:400).
See docs/superpowers/specs/2026-08-05-r41-invalid-split-refusal-design.md."""
import os
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
HBS = os.path.join(QDIR, "header-body-split.rq")

# The apple segment-footnote band, cells-level (measured 2026-08-05: split=7 on 7 rows pre-fix).
# Col 0 = caption + text labels; col 1 = the $-sandwiched data column.
SANDWICH_CELLS = [(0, 0, "(1) Net sales by reportable segment:")] + [
    (r, 0, t) for r, t in enumerate(
        ["Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific",
         "Total net sales"], 1)
] + [
    (1, 1, "$ 45,781"), (2, 1, "29,395"), (3, 1, "18,816"),
    (4, 1, "6,554"), (5, 1, "8,871"), (6, 1, "$ 109,417"),
]

# Single-column minimal form (same mechanism, no label column).
SANDWICH_ONE_COL = [
    (0, 0, "Qty"), (1, 0, "$ 45,781"), (2, 0, "29,395"), (3, 0, "18,816"),
    (4, 0, "6,554"), (5, 0, "8,871"), (6, 0, "$ 109,417"),
]


def _split(cells, ncols):
    return celltype.run_scalar(HBS, celltype.grid_evidence(cells, ncols))


def test_axiom_refuses_past_the_end_split():
    # A split at row 7 of a 7-row grid leaves zero body rows: not a label->data
    # transition, refused (None -> caller falls back / escalates). Pre-fix: returns 7.
    assert _split(SANDWICH_CELLS, 2) is None
    assert _split(SANDWICH_ONE_COL, 1) is None


def test_split_still_derived_when_another_column_transitions():
    # Guard: the clause must only DROP past-the-end candidates, never block a valid
    # column's in-range split. Same sandwich column + a clean numeric column whose
    # transition is at row 1 -> MIN over surviving candidates = 1, exactly as today.
    cells = SANDWICH_CELLS + [
        (0, 2, "Qty"), (1, 2, "100"), (2, 2, "200"), (3, 2, "300"),
        (4, 2, "400"), (5, 2, "500"), (6, 2, "600"),
    ]
    assert _split(cells, 3) == 1


def _band(pdf_path):
    """The single band of a borderless one-table fixture page (production geometry path)."""
    from iladub.etkl.geometry import extract_words, text_lines
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.segment import segment
    words = extract_words(pdf_path, 0)
    out = []
    for band in detect_bands(text_lines(words)):
        out.extend(segment(band))
    return max(out, key=lambda b: len(b.lines))


def test_classify_hierarchical_returns_instead_of_raising(tmp_path):
    # Pre-fix this RAISES IndexError (the apple crash path: classify_hierarchical ->
    # infer_header_tree -> header_rows_of -> band.lines[split]). Post-fix it must
    # RETURN — None (escalate) or a HierRegion — never crash. No reading is claimed.
    from tests.etkl.fixtures import currency_sandwich_pdf
    from iladub.etkl.hierarchical import classify_hierarchical
    pdf = str(tmp_path / "sandwich.pdf")
    currency_sandwich_pdf(pdf)
    classify_hierarchical(_band(pdf))   # must not raise; return value unconstrained


def test_compile_returns_instead_of_crashing(tmp_path):
    # The fluent-reader invariant end to end: compile returns a report; every region
    # is asserted or escalated, never a crash. The verdict itself stays unpinned —
    # honest escalation is the expected outcome, but the gate is "returns at all"
    # (the corpus battery's own Unadjudicated gate).
    from tests.etkl.fixtures import currency_sandwich_pdf
    from iladub.etkl import compile_tables
    pdf = str(tmp_path / "sandwich.pdf")
    currency_sandwich_pdf(pdf)
    rep = compile_tables(pdf, page_number=0)
    assert rep.regions, "no regions at all"
    assert all(r.verdict in ("asserted", "escalated") for r in rep.regions)
