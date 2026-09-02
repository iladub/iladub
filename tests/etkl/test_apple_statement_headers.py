"""Spec 2026-09-02-the-body-starts-at-the-stub-design.md § 5 O5, the apple leg. Real document,
gitignored corpus/ — skips when absent, never in CI. Band indices measured 2026-09-02 (plan S4/S5).
These pin READINGS (levels, entries, tiling), never the score (spec § 1.4)."""
import os
import pytest
pytest.importorskip("pdfplumber")
from rdflib import Graph, URIRef
from iladub.etkl.compile import page_bands
from iladub.etkl.matrix import classify_matrix
from iladub.etkl.holon import assert_matrix_region
from iladub.etkl.tiling import region_tiles

pytestmark = pytest.mark.corpus
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")


def _band(page, idx):
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    return page_bands(APPLE, page)[idx]


def _asserted(band, page):
    mreg = classify_matrix(band)
    assert mreg is not None
    g = Graph()
    n = assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), page)
    assert region_tiles(g) is True
    return mreg, n


def test_p0_income_statement_header_is_three_levels():
    """Spec § 1.2: Three/Nine Months Ended over June 27,/June 28, over 2026/2025; 28 entries."""
    band = _band(0, 2)
    assert [w.text for w in band.lines[2].words] == ["2026", "2025", "2026", "2025"]
    mreg, n = _asserted(band, 0)
    assert mreg.body_line == 3
    assert sorted({x.level for x in mreg.col_tree}) == [0, 1, 2]
    assert len(mreg.leaf_rows) == 9 and n == 28


def test_p1_balance_sheet_header_is_two_levels():
    """Spec § 8 / plan Self-Review predicted classify_matrix(band) itself returns a 2-level,
    14-entry region here (June 27,/September 27, over 2026/2025) — PLAN DEFECT, measured 2026-09-02
    (Task 5): classify_matrix(band) is None. header_body_split returns 1 on this band (the years
    line 2026/2025 carries no stub cell, the identical class of defect apple p0 has), and matrix.py's
    `if split is None or split < 2: return None` — present since before this loop, untouched by
    Tasks 2-4, and evaluated on the RAW split before matrix_body_start ever runs — refuses before the
    stub-bearing-line derivation gets a chance to push the start to line 2. Spec § 8's own figures
    (and the plan's Self-Review 'body_line ... 2 on apple p1') were measured by calling
    matrix_body_start directly, not classify_matrix(band) end-to-end; nobody exercised the entry
    point this test uses. Reconciliation is symmetric with Task 3's `is_matrix_candidate` note
    (matrix.py:84-92, same reasoning, same untouched-gate shape) — that note did not cover
    classify_matrix's own copy of the gate. Substituted per plan-rule 1 with the satisfiable form of
    the same force: pin that classify_matrix(band) is None TODAY, and separately pin that the new
    AXIOM primitives (matrix_body_start + infer_column_tree_by_proximity), driven directly with the
    measured split/k, DO produce the predicted 2-level, 14-entry, tiling reading — proving the gap is
    the untouched early-exit, not the new derivation. See the task report for the residue."""
    from iladub.etkl.cells import recover_leaf_grid
    from iladub.etkl.headers import header_body_split
    from iladub.etkl.rowheaders import stub_data_split, infer_row_header_tree
    from iladub.etkl.matrix import matrix_body_start, infer_column_tree_by_proximity, MatrixRegion
    from iladub.etkl.rows import logical_rows

    band = _band(1, 2)
    assert classify_matrix(band) is None            # current end-to-end behavior — the plan defect

    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    k = stub_data_split(band, grid)
    assert (split, k) == (1, 1)                      # the raw type split undercounts, like p0's
    body_start = matrix_body_start(band, grid, split, k)
    assert body_start == 2                           # the derivation itself is correct

    data_cols = tuple(range(k, grid.ncols))
    stub_cols = tuple(range(k))
    col_tree = infer_column_tree_by_proximity(band, grid, body_start, data_cols)
    assert sorted({x.level for x in col_tree}) == [0, 1]
    leaf_rows = logical_rows(band, grid, band.lines[body_start].top)
    row_tree = infer_row_header_tree(band, grid, stub_cols, leaf_rows)
    mreg = MatrixRegion(grid, col_tree, tuple(row_tree), tuple(leaf_rows), stub_cols, data_cols,
                        body_start)
    g = Graph()
    n = assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), 1)
    assert region_tiles(g) is True
    assert n == 14


def test_p2_unruled_header_refuses_rather_than_dropping_ink():
    """Spec § 1.3 Finding B / § 3.2: 'Nine Months Ended' is three pdfplumber words on an unruled
    band; 'Months' and both 'June's would be carried by no node. Honest MATRIX_AMBIGUOUS."""
    band = _band(2, 2)
    assert band.rules == ()
    assert [w.text for w in band.lines[0].words] == ["Nine", "Months", "Ended"]
    assert classify_matrix(band) is None


def test_document_scope_adoption_is_pre_empted_and_recorded():
    """Spec § 1.4 predicted that once p1's header band asserts, adoption-candidate.rq's NOT EXISTS
    tab:EntryCell gate refuses the page-1 datagrid adoption: adopted (1,) -> (). PLAN DEFECT,
    downstream of test_p1_balance_sheet_header_is_two_levels's finding, not a second one:
    classify_matrix(band) is None for p1 at HEAD, so no tab:EntryCell is ever asserted there and the
    NOT EXISTS gate never fires — adopted stays (1,). Substituted per plan-rule 1. The MATRIX_AMBIGUOUS
    count (p2 band 2 only; p0's now asserts) is unaffected and matches the plan's own prediction.
    The score is printed, never asserted."""
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    from iladub.etkl.document import compile_document
    rep = compile_document(APPLE)
    print(f"apple score {rep.score:.4f} adopted {rep.adopted}")
    assert rep.adopted == (1,)
    reasons = [r.reason for p in rep.pages for r in p.regions]
    assert reasons.count("MATRIX_AMBIGUOUS") == 1          # p2 band 2 only; p0's is now asserted
