"""Loop B — header→column reconciliation: wide single-column labels + leading caption line.
See docs/superpowers/specs/2026-07-26-header-column-reconciliation-design.md."""
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import infer_header_tree, merge_tiling_ok


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


# 3 narrow columns: boundaries 100,150,200,250 -> centers 125,175,225. A single header row where
# the middle label "Reference" has wide ink [170,205] that straddles the col1/col2 gutter but whose
# CENTER-in-ink hits only col1. Old symmetrization -> covers(0,1,2) -> overlaps A(0)/C(2) -> escalate.
_GRID = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)


def _wide_label_band():
    header = [_w("A", 110, 140, 0.0), _w("Reference", 170, 205, 0.0), _w("C", 210, 240, 0.0)]
    d1 = [_w("a", 110, 140, 12.0), _w("56", 170, 205, 12.0), _w("c", 210, 240, 12.0)]
    d2 = [_w("a2", 110, 140, 24.0), _w("57", 170, 205, 24.0), _w("c2", 210, 240, 24.0)]
    return Band((_line(header, 0.0), _line(d1, 12.0), _line(d2, 24.0)), 0.0, 34.0)


def test_wide_single_column_label_tiles():
    # split=1: row 0 is the header, rows 1-2 are data. The wide "Reference" label must NOT be
    # over-spanned; the tree must tile (each column claimed by exactly one leaf label).
    tree = infer_header_tree(_wide_label_band(), _GRID, 1)
    assert tree is not None
    assert merge_tiling_ok(tree, _GRID) is True
