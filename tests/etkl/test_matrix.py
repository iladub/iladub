import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph, URIRef

from tests.etkl.fixtures import (crosstab_drifting_leafrow_pdf, crosstab_table_pdf,
                                 pivoted_table_pdf, simple_table_pdf,
                                 three_level_numeric_header_pdf,
                                 unruled_multiword_spanner_pdf)
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl.holon import assert_matrix_region
from iladub.etkl.matrix import (infer_column_tree_by_proximity,
                                is_matrix_candidate,
                                classify_matrix, matrix_body_start, MatrixRegion)
from iladub.etkl.rowheaders import stub_data_split
from iladub.etkl.tiling import region_tiles


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_proximity_column_tree(tmp_path):
    band = _band(crosstab_table_pdf, tmp_path)
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    data_cols = tuple(range(1, grid.ncols))              # col 0 is the stub
    tree = infer_column_tree_by_proximity(band, grid, split, data_cols)
    l0 = {n.text: n.covers for n in tree if n.level == 0}
    assert l0["Q1"] == (1, 2, 3)                          # short label, wide span — proximity recovers it
    assert l0["Q2"] == (4, 5, 6)
    leaves = [n for n in tree if n.level == 1]
    assert len(leaves) == 6 and all(len(n.covers) == 1 for n in leaves)


def _tree(maker, tmp_path, name):
    d = tmp_path / name; d.mkdir()
    band = _band(maker, d)
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    return infer_column_tree_by_proximity(band, grid, split, tuple(range(1, grid.ncols)))


def test_sub_point_leaf_drift_is_one_header_level(tmp_path):
    """R45: 0.9pt baseline drift inside ONE leaf header row is not a level boundary.

    Measured on who-wfa page 0, whose single visual header line carries two baselines
    (`Year: | Month | ... | L | M | S` at top 118.7, `-3 SD ...` at 119.6) — see spec
    docs/superpowers/specs/2026-08-31-a-header-level-is-a-band-line-design.md §3.2.
    Both band producers group those into one line; a level derivation that re-reads
    rounded word tops instead manufactures a THIRD level, tears the leaf row in half
    over overlapping columns and orphans two nodes, which tab:UnambiguousAccessShape
    then correctly refuses.

    The drift is a rendering accident, so the tree must be the undrifted one, node for
    node — including parents. Falsified by restoring a top-based level derivation.
    """
    drifted = _tree(crosstab_drifting_leafrow_pdf, tmp_path, "drift")
    flat = _tree(crosstab_table_pdf, tmp_path, "flat")
    assert drifted is not None and flat is not None
    shape = lambda t: [(n.level, n.text, n.covers, n.parent) for n in t]
    assert shape(drifted) == shape(flat)
    assert {n.level for n in drifted} == {0, 1}
    assert {n.text: n.covers for n in drifted if n.level == 0} == {"Q1": (1, 2, 3), "Q2": (4, 5, 6)}
    assert all(n.parent is not None for n in drifted if n.level > 0)


def test_is_matrix_candidate(tmp_path):
    assert is_matrix_candidate(_band(crosstab_table_pdf, tmp_path)) is True
    # Loop 2 pivot: stub_data_split is None (mixed data cols) -> not a matrix
    assert is_matrix_candidate(_band(pivoted_table_pdf, tmp_path)) is False
    # flat single-level table: header_body_split 1 -> not a matrix
    assert is_matrix_candidate(_band(simple_table_pdf, tmp_path)) is False


def test_classify_matrix_composes_both_axes(tmp_path):
    mreg = classify_matrix(_band(crosstab_table_pdf, tmp_path))
    assert mreg is not None
    assert mreg.stub_cols == (0,)
    assert mreg.data_cols == (1, 2, 3, 4, 5, 6)
    assert len(mreg.leaf_rows) == 2
    l0c = {n.text: n.covers for n in mreg.col_tree if n.level == 0}
    assert l0c["Q1"] == (1, 2, 3) and l0c["Q2"] == (4, 5, 6)
    row_texts = {n.text for n in mreg.row_tree}
    assert {"North", "South"} <= row_texts


def test_classify_matrix_none_on_flat_header(tmp_path):
    # simple_table has a single-level header (header_body_split 1) -> not a matrix
    assert classify_matrix(_band(simple_table_pdf, tmp_path)) is None


def test_classify_matrix_none_on_pivot(tmp_path):
    # Loop 2 pivot: stub_data_split None -> not a matrix
    assert classify_matrix(_band(pivoted_table_pdf, tmp_path)) is None


def test_numeric_third_header_level_is_a_header_level(tmp_path):
    """O1 (spec § 5). The years line is typed body by header-body-split.rq (a Numeric line over
    Currency lines is one Quantity family) but carries no stub cell, so the matrix body cannot
    start there. Reproduces apple p0 band 2 (spec § 1.2: three levels, tiles) on a synthetic.
    Falsified by reverting classify_matrix to the type split: logical_rows finds no anchor
    column and the region is None."""
    p = tmp_path / "x.pdf"; three_level_numeric_header_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    mreg = classify_matrix(band)
    assert mreg is not None
    assert mreg.body_line == 3
    assert sorted({n.level for n in mreg.col_tree}) == [0, 1, 2]
    years = {n.covers: n.text for n in mreg.col_tree if n.level == 2}
    assert years == {(1,): "2026", (2,): "2025", (3,): "2026", (4,): "2025"}
    for n in mreg.col_tree:
        if n.level == 2:
            parent = mreg.col_tree[n.parent]
            assert parent.level == 1 and parent.covers == n.covers
    assert len(mreg.leaf_rows) == 3                    # 'Sales:' section row + two data rows
    g = Graph()
    assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    assert region_tiles(g) is True


def test_a_header_word_carried_by_no_node_refuses_the_tree(tmp_path):
    """O3 (spec § 5; § 1.3 Finding B). On an unruled band a multi-word spanner is three pdfplumber
    words; nearest-centre assignment lets two of them win the two data columns and the third
    ('Months') becomes no node at all. Asserting that tree emits a header with a third of its
    ink gone (CLAUDE.md §7). The guard refuses; compile escalates MATRIX_AMBIGUOUS at the existing
    site. Falsified by deleting the guard: the tree has 6 nodes for 7 data-column header words
    and classify_matrix returns a region that tiles."""
    p = tmp_path / "x.pdf"; unruled_multiword_spanner_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    assert [w.text for w in band.lines[0].words] == ["Nine", "Months", "Ended"]   # measured, not assumed
    assert band.rules == ()
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid); k = stub_data_split(band, grid)
    body = matrix_body_start(band, grid, split, k)
    assert (split, k, body) == (2, 1, 3)
    assert infer_column_tree_by_proximity(band, grid, body, tuple(range(k, grid.ncols))) is None
    assert classify_matrix(band) is None


def test_a_stub_column_header_does_not_trigger_the_guard(tmp_path):
    """O4 (spec § 5; § 3.2). WHO's 'Year: Month' sits over the STUB column at a header level;
    it is never a column-tree node and must not be counted as dropped ink. Falsified by removing
    the data-column condition from the guard: 'Segment' is uncarried and the band refuses."""
    p = tmp_path / "x.pdf"; three_level_numeric_header_pdf(str(p), corner="Segment")
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    assert band.lines[1].words[0].text == "Segment"
    mreg = classify_matrix(band)
    assert mreg is not None
    assert "Segment" not in {n.text for n in mreg.col_tree}
    assert sorted({n.level for n in mreg.col_tree}) == [0, 1, 2]
