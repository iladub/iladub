"""B3 — wrap-continuation grouping now gates on the adaptive `gap < lead` (the tuned
0.9 margin retired). These pin the endpoints (tight merges, at-pitch does not) and the
condition-2/3 structural filter, plus the one behaviour the fix newly enables: a partial
sub-line just under the row pitch is recognised as a continuation (the 0.9 margin missed it)."""
from iladub.etkl.geometry import Word, Line
from iladub.etkl.bands import Band
from iladub.etkl.grid import LeafGrid
from iladub.etkl.cells import group_wrapped

GRID = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0), ncols=3, pitch=100.0, confidence=1.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _row(prefix, top):
    return _line([_w(prefix + "0", 10, 60, top), _w(prefix + "1", 110, 160, top),
                  _w(prefix + "2", 210, 260, top)], top)


def _band_with_subline(sub_top, sub_full=False):
    """Anchor 3-col row at top 0, a sub-line at `sub_top` (col1 only unless sub_full),
    then body rows at pitch 20 -> lead (median gap) = 20."""
    sub = _row("s", sub_top) if sub_full else _line([_w("x", 110, 160, sub_top)], sub_top)
    body_tops = [sub_top + 20.0, sub_top + 40.0, sub_top + 60.0]
    lines = [_row("A", 0.0), sub] + [_row("b%d" % i, t) for i, t in enumerate(body_tops)]
    return Band(tuple(lines), 0.0, lines[-1].bottom)


def test_tight_partial_subline_merges():
    # gap 5 << lead 20 -> continuation merged into the anchor's col-1 cell
    rows = group_wrapped(_band_with_subline(5.0), GRID)
    assert len(rows) == 4                       # anchor(+x) + 3 body, the sub-line consumed
    assert "x" in rows[0][1].text               # merged into col-1 cell ("A1 x")


def test_near_pitch_partial_subline_merges_the_0_9_margin_missed():
    # gap 19 = 0.95*lead: `gap < lead` (new) merges; the retired `gap < lead*0.9=18` did NOT.
    rows = group_wrapped(_band_with_subline(19.0), GRID)
    assert len(rows) == 4                       # RED on the old 0.9 margin (would be 5)
    assert "x" in rows[0][1].text


def test_at_pitch_partial_line_not_merged():
    # gap == lead -> strict `<` excludes it; stays a distinct (partial) row
    rows = group_wrapped(_band_with_subline(20.0), GRID)
    assert len(rows) == 5                        # anchor + x-row + 3 body
    assert "x" not in rows[0][1].text


def test_full_row_never_merged_even_when_tight():
    # a tight FULL row fails condition 3 (len(cols_j) < len(anchor)) -> never a continuation
    rows = group_wrapped(_band_with_subline(5.0, sub_full=True), GRID)
    assert len(rows) == 5                        # anchor + tight full row + 3 body, nothing merged
    assert rows[0][1].text == "A1"               # anchor col-1 untouched
