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


def test_merge_tiling_ok_rejects_ambiguous_node():
    from iladub.etkl.headers import merge_tiling_ok, HeaderNode
    from iladub.etkl.grid import LeafGrid
    grid = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0), ncols=3, pitch=100.0, confidence=1.0)
    # a structurally-fine tree, but one node flagged ambiguous -> gate must reject.
    tree = (HeaderNode(0, (1,), "X", None, 150.0, ambiguous=True),
            HeaderNode(0, (2,), "Y", None, 250.0))
    assert merge_tiling_ok(tree, grid) is False


def test_narrow_flank_tie_detects_narrow_endpoint_not_reached_by_ink():
    from iladub.etkl.headers import _narrow_flank_tie
    # boundaries [0,100,200,300,400,440]: cols 1-3 width 100, col 4 width 40 (< 0.5*pitch=50).
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    # covers 1..4, but raw ink only reaches cols 1..3 -> col 4 is the narrow tied flank.
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3), b) == 4


def test_narrow_flank_tie_none_when_flank_wide():
    from iladub.etkl.headers import _narrow_flank_tie
    # col 4 width 60 (> 0.5*pitch=50) -> NOT a tie (excluding it would leave the band).
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 460.0)
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3), b) is None


def test_narrow_flank_tie_none_when_ink_reaches_flank():
    from iladub.etkl.headers import _narrow_flank_tie
    # raw ink already reaches col 4 -> deterministic coverage, not a tie.
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3, 4), b) is None


def test_resolve_excludes_same_level_sibling_flank():
    from iladub.etkl.headers import resolve_narrow_flanks, HeaderNode
    from iladub.etkl.grid import LeafGrid
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    grid = LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0)
    # coarse node covers 1..4 (raw ink only 1..3); col 4 (400..440) HAS its own level-0 leaf header.
    # header_cells: the coarse label (level0, straddles 1-3) + col4's own level-0 label.
    header_cells = [(0, 105.0, 295.0, "Region"), (0, 405.0, 435.0, "Notes")]
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    # ink_cols supplied per node via the parallel list (see integration) — here 1..3.
    out = resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node=[(1, 2, 3)])
    assert out[0].covers == (1, 2, 3)     # col 4 excluded (same-level sibling)
    assert out[0].ambiguous is False


def test_resolve_escalates_header_empty_flank():
    from iladub.etkl.headers import resolve_narrow_flanks, HeaderNode
    from iladub.etkl.grid import LeafGrid
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    grid = LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0)
    # col 4 has NO own header cell at level 0 -> header-empty -> escalate (mark ambiguous).
    header_cells = [(0, 105.0, 295.0, "Region")]
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    out = resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node=[(1, 2, 3)])
    assert out[0].ambiguous is True
    assert out[0].covers == (1, 2, 3, 4)  # covers unchanged; escalation carries the residue
