"""R295 arm (e): a band whose own rules tile a sub-span more finely than its grid is escalated.

Ruled by the maintainer 2026-10-06 (docs/superpowers/2026-10-06-r295-arm-b-census-handoff.md).
A title line drawn above a ruled grid straddles the rules, so the whole band never tiles, and the
whitespace fallback reads the band as one column (Caltrain p0, p1, p3) or as a 2-column misread
(Caltrain p2). The guard moves no line: it only refuses to assert or ignore a reading that
resolves fewer columns than the author's rules draw over a contiguous run of the band's lines.

The fixture body is TIGHT (2pt gaps, below the gutter minimum), so the whitespace path merges the
three columns into one. That is what makes the kind discriminating: NON_TABLE before, escalated
after.
"""
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word
from iladub.etkl.grid import widest_tiling_span
from iladub.etkl.regions import RegionKind, classify

# Rules drawn only over the grid (y 12..58), as Caltrain's are, below the title line.
GRID_RULES = (Rule(10.0, 12, 58), Rule(50.0, 12, 58), Rule(90.0, 12, 58), Rule(130.0, 12, 58))


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _grid_rows():
    return [_line([_w("a%d" % i, 12, 49, t), _w("b%d" % i, 51, 89, t),
                   _w("c%d" % i, 91, 128, t)], t)
            for i, t in enumerate((12.0, 24.0, 36.0, 48.0))]


def titled_band(rules=GRID_RULES):
    """Line 0 is a full-width title straddling every interior rule."""
    rows = [_line([_w("A-TITLE-ACROSS-THE-WHOLE-GRID", 11, 129, 0.0)], 0.0)] + _grid_rows()
    return Band(tuple(rows), 0.0, 58.0, rules)


def test_widest_tiling_span_is_the_grid_below_the_title():
    assert widest_tiling_span(titled_band()) == (1, 4, 3)


def test_rules_drawn_over_the_title_too_still_give_the_grid():
    # The span's rules are those overlapping the span's y-range, so a rule that also runs
    # through the title does not stop lines 1..4 tiling.
    tall = tuple(Rule(r.x, 0, 58) for r in GRID_RULES)
    assert widest_tiling_span(titled_band(tall)) == (1, 4, 3)


def test_no_span_when_the_whole_band_tiles():
    rows = _grid_rows()
    assert widest_tiling_span(Band(tuple(rows), 12.0, 58.0, GRID_RULES)) is None


def test_no_span_for_an_unruled_band():
    assert widest_tiling_span(titled_band(rules=())) is None


def test_a_single_line_is_not_a_span():
    # Only line 1 sits inside the rules' y-extent, and one line is not a table (classify's own
    # floor), so no span is offered.
    short = tuple(Rule(r.x, 12, 22) for r in GRID_RULES)
    rows = [_line([_w("TITLE-ACROSS", 11, 129, 0.0)], 0.0), _grid_rows()[0],
            _line([_w("FOOTER-ACROSS", 11, 129, 24.0)], 24.0)]
    assert widest_tiling_span(Band(tuple(rows), 0.0, 34.0, short)) is None


def test_titled_band_escalates_and_names_the_span():
    r = classify(titled_band())
    assert r.kind is RegionKind.UNSUPPORTED_TABLE
    assert r.reason == "author rules tile lines 1..4 into 3 columns but the band grid has 1"
    assert r.cells == ()


def test_without_rules_the_same_band_is_still_non_table():
    # Control: the escalation comes from the rules, not from the fixture's words.
    r = classify(titled_band(rules=()))
    assert r.kind is RegionKind.NON_TABLE


def _wide_rows():
    """Wide gutters (40..60, 80..100): whitespace alone reads columns A | B | C."""
    return [_line([_w("A%d" % i, 12, 40, t), _w("B%d" % i, 60, 80, t),
                   _w("C%d" % i, 100, 128, t)], t)
            for i, t in enumerate((12.0, 24.0, 36.0, 48.0))]


def _gutter_title_band(rules):
    """Line 0 is a short title at x 41..59: it closes the 40..60 gutter, so whitespace reads 2
    columns, and it straddles the rule at x 50, so the whole band never tiles."""
    rows = [_line([_w("TITLE", 41, 59, 0.0)], 0.0)] + _wide_rows()
    return Band(tuple(rows), 0.0, 58.0, rules)


def test_a_span_no_finer_than_the_grid_changes_nothing():
    # Coarse rules (10, 50, 130): lines 1..4 tile into 2 columns, and whitespace reads 2.
    coarse = (Rule(10.0, 12, 58), Rule(50.0, 12, 58), Rule(130.0, 12, 58))
    band = _gutter_title_band(coarse)
    assert widest_tiling_span(band) == (1, 4, 2)
    ruled, unruled = classify(band), classify(_gutter_title_band(()))
    assert (ruled.kind, ruled.reason) == (unruled.kind, unruled.reason)


def test_an_already_escalated_band_keeps_its_reason():
    # The span tiles into 3 > 2, but the band already escalates for its own reason. The guard
    # only refuses an assertion or an ignore; it does not rewrite an escalation's reason.
    band = _gutter_title_band(GRID_RULES)
    assert widest_tiling_span(band) == (1, 4, 3)
    r = classify(band)
    assert r.kind is RegionKind.UNSUPPORTED_TABLE
    assert r.reason == "header has 1 words but 2 columns"
