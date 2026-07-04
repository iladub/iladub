import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.geometry import Word, Line, extract_words, text_lines
from iladub.etkl.bands import detect_bands
from tests.etkl.fixtures import simple_table_pdf


# ---------------------------------------------------------------------------
# Helper (no PDF needed)
# ---------------------------------------------------------------------------

def _line(top, bottom=None):
    bottom = top + 10.0 if bottom is None else bottom
    w = Word("x", 0.0, 5.0, top, bottom)
    return Line((w,), top, bottom)


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
    table_lines = lines[1:]
    bands = detect_bands(table_lines)
    assert len(bands) == 1


# ---------------------------------------------------------------------------
# Fixture-free degenerate-input tests
# ---------------------------------------------------------------------------

def test_empty_input_returns_no_bands():
    assert detect_bands([]) == []


def test_single_line_is_one_band():
    bands = detect_bands([_line(100.0)])
    assert len(bands) == 1
    assert len(bands[0].lines) == 1


def test_two_close_lines_are_one_band():
    # gap = 5 between them; with only one gap, median == that gap, never exceeds 1.8x
    bands = detect_bands([_line(100.0, 110.0), _line(115.0, 125.0)])
    assert len(bands) == 1


def test_large_gap_splits_into_two_bands():
    # three evenly spaced lines then a big jump -> 2 bands
    lines = [_line(100.0, 110.0), _line(120.0, 130.0), _line(140.0, 150.0), _line(400.0, 410.0)]
    bands = detect_bands(lines)
    assert len(bands) == 2
    assert len(bands[0].lines) == 3
    assert len(bands[1].lines) == 1
