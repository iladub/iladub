"""test_hierarchical — HierRegion maker + classify_hierarchical."""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf, simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.hierarchical import classify_hierarchical


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_pivot_becomes_hier_region(tmp_path):
    reg = classify_hierarchical(_band(pivoted_table_pdf, tmp_path))
    assert reg is not None
    assert reg.grid.ncols == 7
    assert len([n for n in reg.tree if len(n.covers) >= 2]) == 2   # two merged parents
    assert len(reg.rows) == 5                                      # five body analytes


def test_flat_record_is_not_hierarchical(tmp_path):
    # a flat single-level header has no merged parent; classify_hierarchical may
    # return a region with no multi-column nodes — the orchestrator prefers the
    # Loop-1 record path for these (asserted by test in Task 7).
    reg = classify_hierarchical(_band(simple_table_pdf, tmp_path))
    assert reg is None or all(len(n.covers) == 1 for n in reg.tree)
