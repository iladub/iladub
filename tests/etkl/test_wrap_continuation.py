"""Wrap-continuation grouping. B3 (2026-07-22) gated on the adaptive `gap < lead` (the tuned
0.9 margin retired); its four pins stand: tight merges, at-pitch does not, the condition-2/3
structural filter, and the partial sub-line just under the pitch the 0.9 margin missed.
R208 (2026-09-10) replaced the threshold with `tightest_row_gap` — the minimum gap over the
band's certain pairs — after `gap < lead` at uniform pitch was shown to be decided by coordinate
noise; the detector below and the three tests after it pin the new rule, its fallback, and its
disclosed cost (`docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md`)."""
import pytest

from iladub.etkl.geometry import Word, Line, HRule
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


def _band_with_noisy_subline(noise):
    """`_band_with_subline(20.0)` — the at-pitch case — with the coordinate noise a real PDF
    carries: the sub-line sits `noise` ABOVE the pitch and the first body line `noise` below it,
    so the sub-line's gap is `20 - noise` against a median that stays exactly 20."""
    sub = _line([_w("x", 110, 160, 20.0 - noise)], 20.0 - noise)
    lines = [_row("A", 0.0), sub, _row("b0", 40.0 + noise), _row("b1", 60.0), _row("b2", 80.0)]
    return Band(tuple(lines), 0.0, lines[-1].bottom)


def test_at_pitch_partial_line_under_coordinate_noise_is_still_not_merged():
    # [[R208]]'s detector, formerly a strict xfail: the same intended reading as
    # test_at_pitch_partial_line_not_merged, on the coordinate noise a real PDF carries.
    # Under `gap < lead` the sub-line's gap (20 - 1e-5) fell under the median (20) and welded;
    # under the tightest-certain-boundary rule it is not tighter than every certified row gap.
    rows = group_wrapped(_band_with_noisy_subline(1e-5), GRID)
    assert len(rows) == 5
    assert "x" not in rows[0][1].text


# --- R208: the tightest certain boundary (specs/2026-09-10-the-tightest-certain-boundary-design.md § 5)

GRID5 = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0, 400.0, 500.0), ncols=5, pitch=100.0,
                 confidence=1.0)


def _partial(cols, top):
    """A line occupying exactly the given leaf columns (word k at x 100k+10 .. 100k+60)."""
    return _line([_w("c%d" % c, 100 * c + 10, 100 * c + 60, top) for c in cols], top)


def test_no_certain_pair_falls_back_to_lead():
    # T1 — every line is a strict subset of the one above, so the band certifies NO row boundary
    # and the rule has no minimum to take. Decision (spec § 3): fall back to `lead`, B3's rule —
    # the tighter candidate merges, the looser does not. Byte-identical to `gap < lead`; this pins
    # the fallback ARM against the refuse-when-nothing-certified arm, which would give 3 rows.
    lines = [_partial([0, 1, 2], 0.0), _partial([0, 1], 15.0), _partial([1], 20.0)]
    rows = group_wrapped(Band(tuple(lines), 0.0, lines[-1].bottom), GRID)
    assert len(rows) == 2                        # gaps 15, 5 -> lead 10: 15 stays a row, 5 merges
    assert "c1 c1" in rows[1][1].text            # the 1-col line welded onto the 2-col line's col 1
    assert rows[0][1].text == "c1"               # the anchor untouched


def test_hrule_vetoed_pair_certifies_the_boundary():
    # T2 — the band's ONLY certain pair is hrule-vetoed at gap 8, tighter than the median 15; the
    # candidate at gap 10 sits between them. `gap < lead` merged it; a vetoed pair is an
    # author-drawn row boundary, its gap enters the minimum, and 10 is not tighter than 8.
    lines = [_partial([0, 1, 2, 3, 4], 0.0), _partial([0, 1, 2, 3], 8.0), _partial([0, 1, 2], 18.0),
             _partial([0, 1], 38.0), _partial([0], 58.0)]
    band = Band(tuple(lines), 0.0, lines[-1].bottom, hrules=(HRule(4.0, 0.0, 500.0),))
    rows = group_wrapped(band, GRID5)
    assert len(rows) == 5                        # nothing welds (was 4: line 2 into line 1)
    assert rows[1][0].text == "c0"


def test_certified_boundary_tighter_than_the_pitch_refuses_the_wrap_between():
    # T3 — the disclosed cost (spec § 4(a)), pinned as INTENDED: a full row certifies a boundary at
    # gap 12, tighter than the body pitch 20; a partial line at gap 15 — which `gap < lead`
    # accepted — is refused, because a wrap must be tighter than every certified row boundary.
    lines = [_row("A", 0.0), _row("B", 12.0), _line([_w("x", 110, 160, 27.0)], 27.0),
             _row("b0", 47.0), _row("b1", 67.0), _row("b2", 87.0)]
    rows = group_wrapped(Band(tuple(lines), 0.0, lines[-1].bottom), GRID)
    assert len(rows) == 6                        # was 5 under `gap < lead` (x welded onto B)
    assert rows[1][1].text == "B1"
