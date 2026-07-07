import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import transposed_table_pdf, simple_table_pdf
from tests.etkl.fixtures import all_text_table_pdf, false_transposed_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.orientation import looks_transposed
from iladub.etkl.orientation import transpose_is_coherent


def _region(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return classify(band)


def test_transposed_is_flagged(tmp_path):
    # fields down col 0, numeric values run across the 'Age' row -> transposed
    assert looks_transposed(_region(transposed_table_pdf, tmp_path)) is True


def test_normal_numeric_table_not_flagged(tmp_path):
    # simple_table has an all-numeric 'Value' column -> a typed COLUMN -> not transposed
    assert looks_transposed(_region(simple_table_pdf, tmp_path)) is False


def test_transposed_is_coherent(tmp_path):
    # every field-row (Name/Age/City) is type-homogeneous across the record columns
    assert transpose_is_coherent(_region(transposed_table_pdf, tmp_path)) is True


def test_normal_record_not_coherent(tmp_path):
    # simple_table rows are records (e.g. "Hemoglobin 13.2 g/dL") -> mixed types -> not coherent
    assert transpose_is_coherent(_region(simple_table_pdf, tmp_path)) is False


def test_false_positive_detected_but_not_coherent(tmp_path):
    # trips looks_transposed (a numeric row, no numeric column) BUT the 'Mix' row
    # is type-mixed (5 numeric, ok text) -> coherence is False -> must NOT compile
    region = _region(false_transposed_pdf, tmp_path)
    assert looks_transposed(region) is True
    assert transpose_is_coherent(region) is False
