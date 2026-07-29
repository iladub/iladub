"""Loop D — the author's vertical rules as leaf-grid authority.

Two shipped defects made GrainCorp's grid 14 columns where the source has 15:
recover_leaf_grid rebuilt every sub-band WITHOUT band.rules (so the border-aware
path never ran), and double-drawn rules would otherwise yield hairline columns.
See docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md.

The fixture is deliberately TIGHT — 2pt gaps, below the 3-bin gutter minimum — so the
whitespace path merges all three columns into one. That is what makes these tests
discriminating: rule-derived 3 vs gutter-derived 1.
"""
from iladub.etkl.bands import Band
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.geometry import Line, Rule, Word
from iladub.etkl.grid import _rule_boundaries, infer_leaf_grid

# A deliberately NARROW (~1pt) but OCCUPIED interval, to guard against a collapse
# that drops real structure. See test_narrow_occupied_interval_survives_collapse
# below for why test_occupied_intervals_all_survive alone cannot catch this.
NARROW_RULES = (Rule(10.0, 0, 70), Rule(50.0, 0, 70), Rule(51.0, 0, 70), Rule(90.0, 0, 70))
NARROW_EXPECTED = (10.0, 50.0, 51.0, 90.0)

# 10.0 and 10.3 are the SAME physical rule drawn twice — the artefact that would
# otherwise produce a 0.3pt hairline column.
RULES = (Rule(10.0, 0, 70), Rule(10.3, 0, 70), Rule(50.0, 0, 70),
         Rule(90.0, 0, 70), Rule(130.0, 0, 70))
EXPECTED = (10.0, 50.0, 90.0, 130.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _body_rows():
    """Four data rows whose 2pt inter-column gaps are too narrow to be gutters."""
    return [_line([_w("a%d" % i, 12, 49, t), _w("b%d" % i, 51, 89, t),
                   _w("c%d" % i, 91, 128, t)], t)
            for i, t in enumerate((12.0, 24.0, 36.0, 48.0))]


def tight_ruled_band():
    rows = _body_rows()
    return Band(tuple(rows), 12.0, 58.0, RULES)


def straddling_caption_band():
    """Same table, but line 0 is a caption straddling the 50.0 rule — the GrainCorp
    shape ('Friday, 24 J' was the single word of 472 that vetoed the whole band)."""
    rows = [_line([_w("CAPTION", 40, 60, 0.0)], 0.0)] + _body_rows()
    return Band(tuple(rows), 0.0, 58.0, RULES)


def test_unoccupied_interval_is_not_a_column():
    # The 10.0-10.3 interval holds no word, so it is not a column. Threshold-free:
    # a presence test, never a distance comparison.
    assert _rule_boundaries(tight_ruled_band()) == list(EXPECTED)


def test_occupied_intervals_all_survive():
    # Guard against over-collapsing: every interval that DOES hold ink is kept.
    kept = _rule_boundaries(tight_ruled_band())
    assert len(kept) - 1 == 3


def test_rules_still_refused_when_a_word_straddles():
    # Honest failure preserved: the full band still falls through to whitespace.
    assert _rule_boundaries(straddling_caption_band()) is None


def test_no_rules_means_no_rule_boundaries():
    assert _rule_boundaries(Band(tuple(_body_rows()), 12.0, 58.0)) is None


def narrow_occupied_band():
    """Rules create a deliberately narrow (~1pt) interval [50.0, 51.0] that holds a
    real word (a genuine, if slender, column) — as distinct from the RULES fixture's
    [10.0, 10.3] interval, which is a double-drawn rule holding NO word.
    """
    row = _line([_w("a", 12, 49, 12.0), _w("b", 50.2, 50.8, 12.0), _w("c", 52, 89, 12.0)], 12.0)
    return Band((row,), 12.0, 22.0, NARROW_RULES)


def test_narrow_occupied_interval_survives_collapse():
    # Regression guard for a Critical-class risk: test_occupied_intervals_all_survive
    # (above) asserts only a COUNT against the RULES fixture, so a mutant that drops
    # the wrong interval and adds back a duplicate boundary elsewhere (e.g. returning
    # [10.0, 50.0, 130.0, 130.0]) still passes it — the count matches, the content is
    # wrong. This fixture makes a narrow OCCUPIED interval the discriminator: any
    # collapse that drops it changes the actual boundary list, which this test checks
    # directly rather than just its length.
    assert _rule_boundaries(narrow_occupied_band()) == list(NARROW_EXPECTED)


def test_rules_outrank_inferred_gutters():
    # THE LOOP'S POINT. The 2pt gaps are below the gutter minimum, so whitespace
    # inference merges all three columns into ONE. The author drew rules; they win.
    band = tight_ruled_band()
    gutter_only = infer_leaf_grid(Band(band.lines, band.top, band.bottom))
    assert gutter_only.ncols == 1, "fixture must be tight enough to defeat the gutter path"

    grid = recover_leaf_grid(band)
    assert grid.ncols == 3
    assert grid.boundaries == EXPECTED
    assert grid.confidence == 1.0


def test_straddling_caption_self_heals_via_the_suffix():
    # _rule_boundaries refuses the FULL band (the caption straddles a rule), but
    # recover_leaf_grid already walks row-suffixes to skip unstable top rows, so a
    # later suffix accepts. This is the GrainCorp shape: one word of 472 vetoed
    # the rules for the whole band.
    grid = recover_leaf_grid(straddling_caption_band())
    assert grid.ncols == 3
    assert grid.boundaries == EXPECTED


def test_ruleless_band_is_unchanged():
    # The modal-vote path is NOT being changed in this loop. A band with no rules
    # must return exactly what it returns today.
    band = Band(tuple(_body_rows()), 12.0, 58.0)
    assert recover_leaf_grid(band).ncols == 1
