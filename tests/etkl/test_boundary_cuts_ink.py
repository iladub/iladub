"""R154 — a ruled boundary that cuts through ink is not a cell divider for that row.

Spec: docs/superpowers/specs/2026-08-31-a-boundary-that-cuts-ink-design.md

The defect: `rule_aware_lines` assigns every character to a ruled column by its CENTRE, so where
the rule x's arrive dense — WHO page 0 band 2 carries 48 raw x's in quads of twin stroke edges,
adjacent x's 0.72pt apart — consecutive characters of ONE WORD land in different columns and the
word emerges as one cell per character ('Z-scores' -> 'Z-s' // 'c' // 'o' // 'res (weight').

The repair is the predicate `ruledroles._within` already carries and already justifies: "the chop
is exact, so the clearance is exactly zero." A boundary divides a row only where the ink on both
sides CLEARS it. It is expressed with COORD_EPS alone — the repo's float-comparison epsilon, which
makes `>` mean `>` — and is NOT a clearance threshold: no minimum padding is required, only a
non-zero one.

The decision is ROW-LOCAL. `rule_xs` is not mutated and no boundary is removed from any other row;
that is what separates this from the global word-atomicity variant R154's row records as measured
to fail (it collapsed `header_body_split` from >=2 to 1 and `column_xs` to `()`).
"""
from iladub.etkl.geometry import Char, rule_aware_lines


def _glyphs(text: str, x0: float, width: float = 4.0, top: float = 10.0) -> list[Char]:
    """One abutting glyph box per character, left to right from `x0` — the layout a renderer
    produces for a single text run (advance-width boxes that touch)."""
    return [Char(ch, x0 + i * width, x0 + (i + 1) * width, top, top + 8.0)
            for i, ch in enumerate(text)]


def test_a_boundary_inside_a_text_run_does_not_divide_it():
    """The R154 shred, minimally. Two boundaries fall INSIDE the run's glyph boxes; neither may
    cut it, so the run stays one cell."""
    chars = _glyphs("Zscores", 100.0)                      # ink spans 100.0 .. 128.0
    lines = rule_aware_lines(chars, [90.0, 110.0, 118.0, 140.0])
    assert [w.text for w in lines[0].words] == ["Zscores"]


def test_a_boundary_in_a_genuine_gutter_still_divides():
    """The other half, and the one that must not regress: where both sides CLEAR the boundary,
    it divides exactly as before. Without this the fix is word-atomicity, which is measured to
    collapse the column grid."""
    chars = _glyphs("AB", 100.0) + _glyphs("CD", 140.0)    # 100..108 gutter 108..140 140..148
    lines = rule_aware_lines(chars, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["AB", "CD"]


def test_the_decision_is_row_local():
    """Invariant 1. One boundary, two rows: it cuts a run on the first and sits in a gutter on the
    second. The second row must still divide there — a boundary lost to one row is not lost to the
    document, which is precisely what the failed global variant did."""
    banner = _glyphs("SPANNING", 100.0, top=10.0)          # 100..132, the boundary at 120 cuts it
    data = _glyphs("AB", 100.0, top=30.0) + _glyphs("CD", 140.0, top=30.0)
    lines = rule_aware_lines(banner + data, [90.0, 120.0, 160.0])
    assert [w.text for w in lines[0].words] == ["SPANNING"]
    assert [w.text for w in lines[1].words] == ["AB", "CD"]


def test_ink_flush_against_the_boundary_is_a_chop_not_a_cell():
    """The sub-point case, which is why this is COORD_EPS and not a tolerance. WHO's overhang is
    0.03pt — three times COORD_EPS, far below any padding a human would call clearance, and the
    predicate must still call it a chop. `_within`'s docstring: ink that REACHES a boundary was
    not laid out in that cell."""
    chars = _glyphs("EF", 100.0) + _glyphs("GH", 108.03)   # left ink ends 0.03pt PAST x=108
    lines = rule_aware_lines(chars, [90.0, 108.0, 160.0])
    assert [w.text for w in lines[0].words] == ["EFGH"]
