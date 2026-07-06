import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.rows import logical_rows

PAGE_W, PAGE_H = letter


def wrapped_body_pdf(path):
    """3-col record; the Note column wraps to 2 lines on row 1, 1 line on row 2.
    Anchor = the single-word Analyte column."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    c.drawString(60, PAGE_H-100, "Analyte"); c.drawString(200, PAGE_H-100, "Value"); c.drawString(320, PAGE_H-100, "Note")
    c.drawString(60, PAGE_H-118, "Hemoglobin"); c.drawString(200, PAGE_H-118, "13.2"); c.drawString(320, PAGE_H-118, "slightly")
    c.drawString(320, PAGE_H-130, "low")                                   # wrap of the Note cell
    c.drawString(60, PAGE_H-152, "WBC"); c.drawString(200, PAGE_H-152, "7.8"); c.drawString(320, PAGE_H-152, "normal")
    c.save(); return {}


def test_wrapped_body_two_logical_rows(tmp_path):
    p = tmp_path / "w.pdf"; wrapped_body_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    grid = recover_leaf_grid(band)
    body_start = band.lines[1].top   # first data row top
    rows = logical_rows(band, grid, body_start)
    assert rows is not None
    assert len(rows) == 2                                   # not 3 physical lines
    note0 = [c for c in rows[0].cells if "slightly" in c.text][0]
    assert "low" in note0.text                              # wrap folded into row 0's Note
