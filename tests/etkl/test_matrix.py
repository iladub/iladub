import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import crosstab_table_pdf, pivoted_table_pdf, simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl.matrix import (infer_column_tree_by_proximity, col_tree_tiles,
                                is_matrix_candidate, ColHeaderNode,
                                classify_matrix, matrix_tiles, MatrixRegion)


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_proximity_column_tree(tmp_path):
    band = _band(crosstab_table_pdf, tmp_path)
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    data_cols = tuple(range(1, grid.ncols))              # col 0 is the stub
    tree = infer_column_tree_by_proximity(band, grid, split, data_cols)
    l0 = {n.text: n.covers for n in tree if n.level == 0}
    assert l0["Q1"] == (1, 2, 3)                          # short label, wide span — proximity recovers it
    assert l0["Q2"] == (4, 5, 6)
    leaves = [n for n in tree if n.level == 1]
    assert len(leaves) == 6 and all(len(n.covers) == 1 for n in leaves)
    assert col_tree_tiles(tree, data_cols) is True


def test_col_tree_tiles_rejects_pathology():
    def node(level, covers, parent):
        return ColHeaderNode(level, covers, "x", parent, 0.0, 0.0, 1.0, 1.0, 0)
    gap = (node(0, (1,), None), node(0, (2,), None))       # data_cols {1,2,3}, col 3 uncovered
    assert col_tree_tiles(gap, (1, 2, 3)) is False
    overlap = (node(0, (1,), None), node(0, (1, 2), None))
    assert col_tree_tiles(overlap, (1, 2)) is False


def test_is_matrix_candidate(tmp_path):
    assert is_matrix_candidate(_band(crosstab_table_pdf, tmp_path)) is True
    # Loop 2 pivot: stub_data_split is None (mixed data cols) -> not a matrix
    assert is_matrix_candidate(_band(pivoted_table_pdf, tmp_path)) is False
    # flat single-level table: header_body_split 1 -> not a matrix
    assert is_matrix_candidate(_band(simple_table_pdf, tmp_path)) is False


def test_classify_matrix_composes_both_axes(tmp_path):
    mreg = classify_matrix(_band(crosstab_table_pdf, tmp_path))
    assert mreg is not None
    assert mreg.stub_cols == (0,)
    assert mreg.data_cols == (1, 2, 3, 4, 5, 6)
    assert len(mreg.leaf_rows) == 2
    l0c = {n.text: n.covers for n in mreg.col_tree if n.level == 0}
    assert l0c["Q1"] == (1, 2, 3) and l0c["Q2"] == (4, 5, 6)
    row_texts = {n.text for n in mreg.row_tree}
    assert {"North", "South"} <= row_texts
    assert matrix_tiles(mreg) is True


def test_classify_matrix_none_on_flat_header(tmp_path):
    # simple_table has a single-level header (header_body_split 1) -> not a matrix
    assert classify_matrix(_band(simple_table_pdf, tmp_path)) is None


def test_classify_matrix_none_on_pivot(tmp_path):
    # Loop 2 pivot: stub_data_split None -> not a matrix
    assert classify_matrix(_band(pivoted_table_pdf, tmp_path)) is None
