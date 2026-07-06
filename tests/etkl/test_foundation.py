import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

import pdfplumber
from tests.etkl.fixtures import simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid


def test_fixture_pdf_is_readable(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    with pdfplumber.open(str(pdf)) as doc:
        text = doc.pages[0].extract_text() or ""
    assert truth["title"] in text
    assert "Hemoglobin" in text


def test_pdf_to_bands_and_grid(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    bands = detect_bands(text_lines(extract_words(str(pdf))))
    assert len(bands) == 2
    grid = infer_leaf_grid(bands[1])
    assert grid.ncols == len(truth["cols"])
