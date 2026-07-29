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
