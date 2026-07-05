import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf, wide_cell_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify, RegionKind, assign_cells, column_of
from iladub.etkl.grid import infer_leaf_grid


def _bands(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))


def test_column_of_picks_span():
    assert column_of(80.0, [72.0, 186.0, 335.0, 442.0]) == 0
    assert column_of(250.0, [72.0, 186.0, 335.0, 442.0]) == 1


def test_simple_table_body_is_record(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[1]
    r = classify(band)
    assert r.kind is RegionKind.RECORD_TABLE, r.reason
    assert r.grid.ncols == 3


def test_title_band_is_non_table(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[0]
    assert classify(band).kind is RegionKind.NON_TABLE


def test_pivot_band_is_unsupported(tmp_path):
    # the band holding the merged parent header must NOT be read as a record table
    bands = _bands(pivoted_table_pdf, tmp_path)
    kinds = {classify(b).kind for b in bands}
    assert RegionKind.RECORD_TABLE not in kinds, "pivot silently asserted!"
    assert RegionKind.UNSUPPORTED_TABLE in kinds


def test_wide_cell_collapses_to_unsupported(tmp_path):
    bands = _bands(wide_cell_table_pdf, tmp_path)
    assert RegionKind.RECORD_TABLE not in {classify(b).kind for b in bands}


def test_assign_cells_groups_by_column(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[1]
    cells = assign_cells(band, infer_leaf_grid(band))
    header = [c for c in cells if c.row == 0]
    assert {c.col for c in header} == {0, 1, 2}
    assert next(c for c in header if c.col == 0).text == "Analyte"
