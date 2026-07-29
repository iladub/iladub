"""Loop F — padding space glyphs must not split a contiguous number (residue R2).

Measured on a real report: the glyphs of 20,000 are TOUCHING (gaps -0.08 to -0.03), but padding
space glyphs OVERLAP them (a space at 811.9-813.4 sits inside the '2' at 811.6-814.5), and
rule_aware_lines joined every glyph in x-order -> '2 0,000'. 49 of 488 cells were wrong.

The rule inserts a space only where a space glyph exists AND the glyphs it separates are actually
apart. Both halves are presence tests — see the spec for two magnitude-based hypotheses that were
measured and refuted.
See docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md.
"""
from iladub.etkl.geometry import Char, rule_aware_lines

RULES = [800.0, 840.0]


def _c(t, x0, x1, top=10.0):
    return Char(t, x0, x1, top, top + 8.0)


def _texts(chars, rules=None):
    lines = rule_aware_lines(chars, rules or RULES)
    return [[w.text for w in ln.words] for ln in lines]


def _number_glyphs(top=10.0):
    """20,000 with touching glyphs, exactly as measured."""
    return [_c("2", 811.6, 814.5, top), _c("0", 814.4, 817.4, top),
            _c(",", 817.3, 818.8, top), _c("0", 818.8, 821.7, top),
            _c("0", 821.7, 824.6, top), _c("0", 824.5, 827.5, top)]


def _padding(top=10.0):
    """Leading padding spaces, the last of which OVERLAPS the '2'."""
    return [_c(" ", 807.6, 809.1, top), _c(" ", 809.0, 810.5, top),
            _c(" ", 810.5, 812.0, top), _c(" ", 811.9, 813.4, top)]


def test_padding_spaces_do_not_split_a_number():
    # THE DEFECT. Padding glyphs overlap the digits; the digits themselves are touching.
    assert _texts(_padding() + _number_glyphs()) == [["20,000"]]


def test_a_real_word_space_survives():
    # A genuine space: a space glyph AND a positive gap between the glyphs it separates
    # (measured at 1.38-1.39pt on the real document).
    chars = [_c("A", 805.0, 808.0), _c("B", 808.0, 811.0),
             _c(" ", 811.0, 812.4),
             _c("C", 812.4, 815.4), _c("D", 815.4, 818.4)]
    assert _texts(chars) == [["AB CD"]]


def test_both_in_one_cell():
    chars = ([_c("A", 801.0, 804.0), _c("B", 804.0, 807.0), _c(" ", 807.0, 808.4)]
             + _padding() + _number_glyphs())
    assert _texts(chars) == [["AB 20,000"]]


def test_a_large_gap_with_no_space_glyph_does_not_split():
    # That is a COLUMN gap (residue R13), not a word gap. rule_aware_lines emits one Word
    # per rule column and must keep doing so.
    chars = [_c("A", 802.0, 805.0), _c("B", 830.0, 833.0)]
    assert _texts(chars) == [["AB"]]


def test_word_bbox_excludes_leading_padding():
    # The Word must report the ink extent of its NON-space glyphs, not the padding's.
    lines = rule_aware_lines(_padding() + _number_glyphs(), RULES)
    w = lines[0].words[0]
    assert w.x0 == 811.6
    assert w.x1 == 827.5


def test_an_OVERLAPPING_real_word_space_survives():
    """THE LOAD-BEARING CASE, and the one the original fixtures missed.

    A review deleted the `inside` clause from _cell_text and all five tests above still passed —
    while every genuine word space in the real document was destroyed ('CARPE DIEM' -> 'CARPEDIEM',
    'Jul 26' -> 'Jul26'). The cause: the fixture above uses an ABUTTING space, which fires the
    `between` clause. Real word spaces OVERLAP both neighbours (measured on the document: 'E'
    271.81-275.33, ' ' 275.29-276.76, 'D' 276.72-280.53 — an overlap of 0.04 on each side), where
    `between` fails and only `inside` saves it. On the real page `inside`-only fires on 133 pairs
    and `between`-only on ZERO, so this shape — not the abutting one — is what the rule must handle.
    Coordinates are the measured ones; do not tidy them.
    """
    chars = [_c("E", 271.81, 275.33), _c(" ", 275.29, 276.76), _c("D", 276.72, 280.53)]
    assert _texts(chars, [270.0, 285.0]) == [["E D"]]
