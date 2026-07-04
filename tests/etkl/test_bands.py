import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from tests.etkl.fixtures import simple_table_pdf


def test_title_splits_from_table(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    bands = detect_bands(text_lines(extract_words(str(pdf))))
    assert len(bands) == 2                         # title band + table band
    title_band, table_band = bands[0], bands[1]
    assert len(title_band.lines) == 1
    assert len(table_band.lines) == 4              # header row + 3 data rows


def test_single_band_when_no_large_gaps(tmp_path):
    # the 4 table rows alone form ONE band (uniform spacing)
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    lines = text_lines(extract_words(str(pdf)))
    table_lines = [ln for ln in lines if ln is not lines[0]]  # drop the title line
    bands = detect_bands(table_lines)
    assert len(bands) == 1
