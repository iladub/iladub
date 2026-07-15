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


from iladub.etkl.rowheaders import infer_row_header_tree, classify_row_hier


def test_infer_row_tree_groups(tmp_path):
    reg, band = _region(row_grouped_table_pdf, tmp_path)
    rreg = classify_row_hier(band)
    assert rreg is not None
    tree = rreg.tree
    # level-0 groups: North covers 3 leaf rows, South covers 2
    l0 = {n.text: n.covers_rows for n in tree if n.level == 0}
    assert l0["North"] == (0, 1, 2)
    assert l0["South"] == (3, 4)
    # level-1 leaves: one row each, parented to their group
    l1 = [n for n in tree if n.level == 1]
    assert len(l1) == 5
    north_idx = next(i for i, n in enumerate(tree) if n.text == "North")
    assert all(tree[n.parent].text == "North" for n in l1 if n.covers_rows[0] < 3)
    assert any(n.parent == north_idx for n in l1)


def test_classify_row_hier_flat_is_none(tmp_path):
    _, band = _region(simple_table_pdf, tmp_path)
    assert classify_row_hier(band) is None
