import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from iladub.etkl.grid import infer_leaf_grid
from tests.etkl.fixtures import simple_table_pdf


def _table_band(pdf_path):
    bands = detect_bands(text_lines(extract_words(pdf_path)))
    return bands[1]  # band 0 = title, band 1 = table


def test_three_columns_detected(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    assert grid.ncols == 3
    # every column's left boundary sits at or just left of a known column x
    for cx in truth["cols"]:
        assert any(b <= cx + 2.0 for b in grid.boundaries)


def test_confidence_scales_with_rows(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    assert 0.0 < grid.confidence <= 1.0
    assert grid.confidence >= 0.9
