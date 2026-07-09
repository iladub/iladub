import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import (row_grouped_table_pdf, simple_table_pdf,
                                 all_text_table_pdf, single_stub_blank_pdf)
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.rowheaders import stub_data_split, looks_row_grouped


def _region(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return classify(band), band


def test_stub_data_split_row_grouped(tmp_path):
    reg, band = _region(row_grouped_table_pdf, tmp_path)
    assert stub_data_split(band, reg.grid) == 2   # cols 0,1 stub; col 2 data


def test_stub_data_split_flat_record(tmp_path):
    # simple_table: Analyte | Value(num) | Unit -> first data col is 1, but col 2 is
    # text -> not all cols from k are numeric -> None (not a stub/data table).
    reg, band = _region(simple_table_pdf, tmp_path)
    assert stub_data_split(band, reg.grid) is None


def test_looks_row_grouped_true(tmp_path):
    reg, _ = _region(row_grouped_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is True


def test_flat_record_not_row_grouped(tmp_path):
    reg, _ = _region(simple_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is False


def test_all_text_not_row_grouped(tmp_path):
    reg, _ = _region(all_text_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is False


def test_single_stub_blank_not_row_grouped(tmp_path):
    # one stub column with blanks but NO fully-populated finer stub -> leaf rows
    # unidentifiable -> not row-grouped (stays on record path).
    reg, _ = _region(single_stub_blank_pdf, tmp_path)
    assert looks_row_grouped(reg) is False
