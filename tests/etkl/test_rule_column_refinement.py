"""Loop G — the author's rules are authoritative but not COMPLETE (residue R13).

An author may rule some column boundaries and leave others to whitespace. GrainCorp's measure
column holds 'Date Loading Completed | Commodity | Total' with no interior rule, so three real
columns compiled as one at confidence 1.0.

A persistent blank run inside a rule interval is an extra boundary — but ONLY if there is ink on
BOTH sides of it within that interval. Measured: without that condition the naive rule adds a
boundary to EVERY interval of ruled_tight_table_pdf (5 columns become 10), because short
left-aligned text leaves a blank run at each cell's trailing edge.
See docs/superpowers/specs/2026-07-30-rule-column-refinement-design.md §2 Finding 3.
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
