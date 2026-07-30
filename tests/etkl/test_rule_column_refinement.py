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


def test_no_rule_is_ever_synthesised_for_a_derived_boundary(tmp_path):
    """Provenance stays honest: Band.rules is what the AUTHOR drew, Band.column_xs is derived.

    Loop D's review rejected synthesising fake Rule objects for derived boundaries. There is no
    band-level seam on compile_tables, so this replicates its ruled-band construction (the same
    dozen lines) and asserts directly that every Rule x was drawn in the document.
    """
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.bands import Band, detect_bands
    from iladub.etkl.geometry import (extract_chars, extract_rules, extract_words,
                                      rule_aware_lines, text_lines)
    from iladub.etkl.segment import segment
    from tests.etkl import fixtures as F

    p = os.path.join(str(tmp_path), "ruled.pdf")
    F.ruled_tight_table_pdf(p)
    page_rules = extract_rules(p, 0)
    page_chars = extract_chars(p, 0)
    authored = {round(r.x, 2) for r in page_rules}
    assert authored, "fixture must be ruled"

    checked = 0
    for band in detect_bands(text_lines(extract_words(p, 0))):
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules
                              if r.top <= sub.bottom and r.bottom >= sub.top)
            if not sub_rules:
                continue
            xs = sorted({round(r.x, 2) for r in sub_rules})
            band_chars = [c for c in page_chars
                          if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
            col_xs = refine_rule_columns(band_chars, xs)
            relines = rule_aware_lines(band_chars, col_xs)
            if not relines:
                continue
            b = Band(tuple(relines), sub.top, sub.bottom, sub_rules, (), tuple(col_xs))
            for r in b.rules:
                assert round(r.x, 2) in authored, "a Rule was synthesised for a derived boundary"
            assert set(xs) <= set(b.column_xs), "derived list must preserve every author boundary"
            checked += 1
    assert checked, "no ruled band was exercised"


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
