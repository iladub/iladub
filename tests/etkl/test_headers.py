import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split, infer_header_tree, is_numeric


def _piv(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return band, recover_leaf_grid(band)


def test_is_numeric():
    assert is_numeric("13.2") and is_numeric("252") and is_numeric("7.8")
    assert not is_numeric("Result") and not is_numeric("g/dL")


def test_boundary_after_header_rows(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    # header lines are the parent, leaf-label, and (SI) rows; body starts at 'Hemoglobin'
    assert band.lines[split].words[0].text == "Hemoglobin"


def test_tree_has_two_merged_parents(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    tree = infer_header_tree(band, grid, split)
    assert tree is not None
    parents = [n for n in tree if len(n.covers) >= 2]
    assert len(parents) == 2                      # Current Visit, Prior Visit
    assert {len(p.covers) for p in parents} == {3}   # each spans 3 leaf columns
