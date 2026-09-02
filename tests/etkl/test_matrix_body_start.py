"""Spec 2026-09-02-the-body-starts-at-the-stub-design.md § 3.1, § 5 O2. The matrix body start
is the first cell-bearing line at/after the TYPE split that carries a STUB cell (AXIOM, open
world, matrix-scoped). header_body_split and its query are untouched by this loop."""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import crosstab_table_pdf, three_level_numeric_header_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl.rowheaders import stub_data_split
from iladub.etkl.matrix import matrix_body_start


def _prepared(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    k = stub_data_split(band, grid)
    return band, grid, split, k


def test_equals_split_when_the_split_line_carries_a_stub_cell(tmp_path):
    """O2, the invariant every non-apple corpus band rests on (spec § 1.5)."""
    band, grid, split, k = _prepared(crosstab_table_pdf, tmp_path)
    assert (split, k) == (2, 1)                       # measured, plan S2
    assert matrix_body_start(band, grid, split, k) == split


def test_advances_past_a_stubless_numeric_header_level(tmp_path):
    """The apple shape: the years line is typed body but carries no stub cell (spec § 1.1)."""
    band, grid, split, k = _prepared(three_level_numeric_header_pdf, tmp_path)
    assert (split, k) == (2, 1)                       # measured, plan S6
    assert [w.text for w in band.lines[2].words] == ["2026", "2025", "2026", "2025"]
    assert matrix_body_start(band, grid, split, k) == 3
    assert [w.text for w in band.lines[3].words] == ["Sales:"]


def test_a_stub_cell_above_the_split_does_not_pull_the_start_up(tmp_path):
    """The ?split binding is load-bearing: a corner label on a HEADER line is a stub-column cell
    at row 1, and MIN without the ?split bound would return 1. Falsified by dropping the
    ?row >= ?split condition from the query."""
    band, grid, split, k = _prepared(lambda p: three_level_numeric_header_pdf(p, corner="Segment"), tmp_path)
    assert (split, k) == (2, 1)
    assert band.lines[1].words[0].text == "Segment"
    body = matrix_body_start(band, grid, split, k)
    assert body == 3 and body >= split


def test_none_when_no_column_is_a_stub(tmp_path):
    """The None path: with k=0 no cell can satisfy ?col < ?k. (k=0 never leaves stub_data_split,
    which returns k>=1 or None; this pins the contract, not a reachable state.)"""
    band, grid, split, k = _prepared(crosstab_table_pdf, tmp_path)
    assert matrix_body_start(band, grid, split, 0) is None


def test_the_query_names_only_declared_terms():
    """O6 — the declaration instrument covers every tracked .rq; this test exists so the O6
    evidence is local to this loop and not only in the suite-wide sweep."""
    from tests.query_terms import query_files
    from pathlib import Path
    assert Path("vocab/queries/matrix-body-start.rq").resolve() in {p.resolve() for p in query_files()}
