import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.geometry import Word, Line, extract_words, text_lines
from iladub.etkl.bands import Band, detect_bands
from iladub.etkl.grid import infer_leaf_grid
from tests.etkl.fixtures import simple_table_pdf


def _table_band(pdf_path):
    bands = detect_bands(text_lines(extract_words(pdf_path)))
    return bands[1]  # band 0 = title, band 1 = table


def _band(word_groups):
    """word_groups: list of lines, each a list of (x0, x1, text)."""
    lines = []
    for words in word_groups:
        ws = tuple(Word(t, x0, x1, 0.0, 10.0) for x0, x1, t in words)
        lines.append(Line(ws, 0.0, 10.0))
    return Band(tuple(lines), 0.0, 10.0)


def test_three_columns_detected(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    assert grid.ncols == 3
    # boundaries = (left_ink, gutter1_center, gutter2_center, right_ink)
    interior = grid.boundaries[1:-1]
    assert len(interior) == 2
    cols = truth["cols"]  # [72, 240, 400]
    assert cols[0] < interior[0] < cols[1], f"gutter 1 not between cols: {grid.boundaries}"
    assert cols[1] < interior[1] < cols[2], f"gutter 2 not between cols: {grid.boundaries}"


def test_confidence_scales_with_rows(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    assert 0.0 < grid.confidence <= 1.0
    assert grid.confidence >= 0.9


def test_one_solid_column():
    band = _band([[(0.0, 50.0, "hello")] for _ in range(4)])
    assert infer_leaf_grid(band).ncols == 1


def test_single_row_confidence():
    band = _band([[(0.0, 30.0, "A"), (60.0, 90.0, "B")]])
    assert infer_leaf_grid(band).confidence == pytest.approx(0.25)


def test_empty_band_raises():
    with pytest.raises(ValueError):
        infer_leaf_grid(Band((), 0.0, 0.0))
