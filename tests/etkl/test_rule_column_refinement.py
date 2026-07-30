"""Loop G — the author's rules are authoritative but not COMPLETE (residue R13).

An author may rule some column boundaries and leave others to whitespace. GrainCorp's measure
column holds 'Date Loading Completed | Commodity | Total' with no interior rule, so three real
columns compiled as one at confidence 1.0.

A persistent blank run inside a rule interval is an extra boundary CANDIDATE — but only if there
is ink on BOTH sides of it within that interval. TWO independent mechanisms reject trailing
padding, and the attribution matters (attempt 1 credited the wrong one; the final review measured
it): the NO-FLUSH behavior (a run still open at the interval's end is never emitted) is what keeps
both shipped ruled fixtures at +0 when the interior condition is removed ALONE; the naive +5/+2
over-split requires removing BOTH mechanisms. And the output is never trusted directly: candidates
become columns only when the header confirms them (boundary.py / confirm-boundary.rq).
See docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md §2 and the
refine_rule_columns docstring (which carries the same corrected attribution).
"""
from iladub.etkl.geometry import Char, refine_rule_columns

RULES = [100.0, 200.0]


def _c(x0, x1, top):
    return Char("X", x0, x1, top, top + 8.0)


def _rows(spans, n=4):
    """n rows, each carrying ink over every (x0, x1) span given."""
    return [_c(a, b, 10.0 * r) for r in range(n) for (a, b) in spans]


def test_an_interior_gutter_adds_a_boundary():
    # Ink on BOTH sides of the blank run -> a real separator the author did not rule.
    assert refine_rule_columns(_rows([(105, 140), (160, 195)]), RULES) == [100.0, 150.0, 200.0]


def test_trailing_padding_does_not_add_a_boundary():
    # THE CASE THAT KILLS THE NAIVE RULE. Short left-aligned text leaves the interval's right
    # side blank; there is no ink to the right of the run, so it is padding, not a separator.
    assert refine_rule_columns(_rows([(105, 140)]), RULES) == [100.0, 200.0]


def test_leading_padding_does_not_add_a_boundary():
    # The mirror case: right-aligned text, no ink to the LEFT of the run.
    assert refine_rule_columns(_rows([(160, 195)]), RULES) == [100.0, 200.0]


def test_a_gutter_must_be_persistent():
    # One gapped row among four is not a column separator.
    chars = _rows([(105, 195)], 3) + [_c(105, 140, 30.0), _c(160, 195, 30.0)]
    assert refine_rule_columns(chars, RULES) == [100.0, 200.0]


def test_no_chars_leaves_the_boundaries_alone():
    assert refine_rule_columns([], RULES) == [100.0, 200.0]


def test_refinement_is_additive():
    # Every author-drawn boundary survives, in order — refinement only ADDS.
    rules = [100.0, 200.0, 300.0]
    out = refine_rule_columns(_rows([(105, 140), (160, 195)]) + _rows([(205, 295)]), rules)
    assert set(rules) <= set(out)
    assert out == sorted(out)


def test_space_glyphs_are_not_ink():
    # A cell padded with space glyphs must still read as blank there.
    chars = _rows([(105, 140), (160, 195)]) + [Char(" ", 141.0, 159.0, 0.0, 8.0)]
    assert refine_rule_columns(chars, RULES) == [100.0, 150.0, 200.0]


def test_rule_boundaries_prefers_the_derived_list():
    """_rule_boundaries must use Band.column_xs when present, so the refinement reaches the grid."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Rule, Word
    from iladub.etkl.grid import _rule_boundaries

    def _w(t, x0, x1, top):
        return Word(t, x0, x1, top, top + 8.0)

    rows = tuple(Line((_w("a", 105, 140, 10.0 * r), _w("b", 160, 195, 10.0 * r)),
                      10.0 * r, 10.0 * r + 8.0) for r in range(4))
    author = (Rule(100.0, 0, 50), Rule(200.0, 0, 50))

    coarse = Band(rows, 0.0, 40.0, author)
    assert _rule_boundaries(coarse) is None, "2 boundaries = no interior separator (Loop D guard)"

    refined = Band(rows, 0.0, 40.0, author, (), (100.0, 150.0, 200.0))
    assert _rule_boundaries(refined) == [100.0, 150.0, 200.0]


def test_recover_leaf_grid_carries_derived_boundaries_onto_sub_bands():
    """THE DEFECT THIS LOOP ALMOST SHIPPED, and the second occurrence of its class.

    recover_leaf_grid tests row-suffixes by rebuilding a sub-Band. Loop D fixed it dropping
    `rules` there (which silently disabled the entire border-aware path); this loop initially
    repeated it for the new `column_xs`, so the refinement reached rule_aware_lines but never the
    grid — the real document compiled 17 columns as 15, with 'Date Loading Completed Commodity
    Total' as ONE label. Measured before the fix: ncols 15; after: 17.

    Pins that a derived boundary survives the sub-band round trip.
    """
    from iladub.etkl.bands import Band
    from iladub.etkl.cells import recover_leaf_grid
    from iladub.etkl.geometry import Line, Rule, Word

    def _w(t, x0, x1, top):
        return Word(t, x0, x1, top, top + 8.0)

    # Two ink runs per row with a wide gap between them, inside ONE author interval.
    rows = tuple(Line((_w("a", 105, 140, 10.0 * r), _w("b", 160, 195, 10.0 * r)),
                      10.0 * r, 10.0 * r + 8.0) for r in range(5))
    author = (Rule(100.0, 0, 60), Rule(200.0, 0, 60))

    coarse = Band(rows, 0.0, 50.0, author)
    refined = Band(rows, 0.0, 50.0, author, (), (100.0, 150.0, 200.0))

    assert recover_leaf_grid(refined).ncols == 2, "derived boundary must reach the grid"
    assert recover_leaf_grid(refined).boundaries == (100.0, 150.0, 200.0)
    # and the coarse band still falls back (2 boundaries = no interior separator, loop D's guard)
    assert recover_leaf_grid(coarse).boundaries != (100.0, 150.0, 200.0)
