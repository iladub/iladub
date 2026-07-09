import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split, infer_header_tree, is_numeric


def _piv(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return band, recover_leaf_grid(band)


def test_is_numeric():
    assert is_numeric("13.2") and is_numeric("252") and is_numeric("7.8")
    assert not is_numeric("Result") and not is_numeric("g/dL")
    # Missing-data sentinels parse as float but are not finite — must return False.
    assert not is_numeric("nan")
    assert not is_numeric("inf")
    assert not is_numeric("-inf")


def test_boundary_after_header_rows(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    # header lines are the parent, leaf-label, and (SI) rows; body starts at 'Hemoglobin'
    assert band.lines[split].words[0].text == "Hemoglobin"


def test_tree_has_two_merged_parents(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    tree = infer_header_tree(band, grid, split)
    assert tree is not None
    parents = [n for n in tree if len(n.covers) >= 2]
    assert len(parents) == 2                      # Current Visit, Prior Visit
    assert {len(p.covers) for p in parents} == {3}   # each spans 3 leaf columns


def test_repair_noop_on_tiling_tree():
    from iladub.etkl.headers import repair_coverage, HeaderNode
    nodes = [HeaderNode(0, (1, 2, 3), "A", None), HeaderNode(0, (4, 5, 6), "B", None),
             HeaderNode(1, (0,), "stub", None)] + [HeaderNode(1, (i,), str(i), None) for i in range(1, 7)]
    out = repair_coverage(list(nodes), 7)
    assert {(n.level, n.covers, n.text) for n in out} == {(n.level, n.covers, n.text) for n in nodes}


def test_repair_absorbs_adjacent_orphan_not_stub():
    from iladub.etkl.headers import repair_coverage, HeaderNode
    nodes = [HeaderNode(0, (1, 2, 3), "Region", None),
             HeaderNode(1, (0,), "Year", None)] + [HeaderNode(1, (i,), n, None)
             for i, n in zip(range(1, 5), ["North", "South", "East", "West"])]
    out = repair_coverage(list(nodes), 5)
    region = next(n for n in out if n.text == "Region")
    assert set(region.covers) == {1, 2, 3, 4}          # West absorbed
    assert 0 not in region.covers                      # stub NOT absorbed


def test_short_parent_covers_full_span_end_to_end(tmp_path):
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    region = next(h for h in rep.graph.subjects(RDF.type, TAB.HeaderNode)
                  if str(rep.graph.value(rep.graph.value(h, TAB.hasLabel), TAB.cellText)) == "Region")
    assert len(list(rep.graph.objects(region, TAB.coversColumn))) == 4
