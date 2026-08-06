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


PAST_END_CELLS = [(0, 0, "(1) Net sales by reportable segment:")] + [
    (r, 0, t) for r, t in enumerate(
        ["Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific",
         "Total net sales"], 1)
] + [
    (1, 1, "45,781"), (2, 1, "29,395"), (3, 1, "18,816"),
    (4, 1, "6,554"), (5, 1, "8,871"), (6, 1, "2020-01-02"),
]

# Single-column minimal form of PAST_END_CELLS (mirrors SANDWICH_ONE_COL).
PAST_END_ONE_COL = [
    (0, 0, "Qty"), (1, 0, "45,781"), (2, 0, "29,395"), (3, 0, "18,816"),
    (4, 0, "6,554"), (5, 0, "8,871"), (6, 0, "2020-01-02"),
]


def test_currency_sandwich_no_longer_produces_a_past_the_end_split():
    """R41 (this test's former name/body) pinned that a $-sandwiched numeric column
    (first and last body rows Currency, interior Numeric) produced a past-the-end
    split candidate, refused by the ?maxrow clause: Currency and Numeric were
    DIFFERENT raw tab:cellDatatype values, so the modal type (Numeric, 4 interior
    rows) mismatched the first/last Currency rows, and the LAST mismatch (row 6 of a
    7-row grid) drove s_col = 7 — one past the last row.

    loop-quantity-typing (2026-08-06, docs/superpowers/specs/2026-08-06-quantity-typing-
    design.md) unifies tab:Currency and tab:Numeric under tab:inDatatypeFamily
    tab:Quantity, and header-body-split.rq now votes/mismatches on the NORMALISED
    family, not the raw type. SANDWICH_CELLS/SANDWICH_ONE_COL are therefore now
    HOMOGENEOUS quantity columns — no mismatch anywhere — so s_col = 1, an ordinary
    in-range split. The shape no longer exercises R41's invariant (the ?maxrow guard
    against a split that would leave zero body rows); that invariant is now pinned by
    test_axiom_refuses_past_the_end_split below, using a shape the Quantity family
    does NOT dissolve (a genuinely different, non-family, non-abstaining type on the
    last row)."""
    assert _split(SANDWICH_CELLS, 2) == 1
    assert _split(SANDWICH_ONE_COL, 1) == 1


def test_axiom_refuses_past_the_end_split():
    # R41's invariant, re-pinned post-quantity-typing (see the docstring above): a
    # split must leave >=1 body row. PAST_END_CELLS/PAST_END_ONE_COL keep the SAME
    # mechanism R41 exercised (modal-type-of-the-body vs. a mismatched LAST row
    # driving s_col = len(rows)) but with a last-row type the Quantity family does
    # NOT unify with Numeric: tab:Date ("2020-01-02"), a genuinely different,
    # non-abstaining, non-family type. Interior body rows 1-5 are plain Numeric (5
    # votes) so the modal type D = Numeric; row 6's Date mismatches D, giving
    # s_col = 6 + 1 = 7 on a 7-row (0..6) grid -- one past the last row, refused by
    # the ?maxrow clause exactly as R41 pinned. Verified empirically (measured
    # 2026-08-06): WITH the ?maxrow guard both fixtures return None; mechanically
    # removing the guard (`FILTER(?s_col >= 1 && ?s_col <= ?maxrow)` ->
    # `FILTER(?s_col >= 1)`) makes both return 7 -- confirming this shape genuinely
    # drives the clause under test, not some other refusal path.
    assert _split(PAST_END_CELLS, 2) is None
    assert _split(PAST_END_ONE_COL, 1) is None


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
