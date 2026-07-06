import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid
from iladub.etkl.cells import recover_leaf_grid


def _piv_band(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_naive_grid_collapses(tmp_path):
    band = _piv_band(tmp_path)
    assert infer_leaf_grid(band).ncols < 7   # merged parent collapses it


def test_recovered_grid_is_seven(tmp_path):
    band = _piv_band(tmp_path)
    assert recover_leaf_grid(band).ncols == 7   # true leaf columns
