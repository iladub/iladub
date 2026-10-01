"""Task 3b (box-split, spec § 8) — the R225 arm-B resolution guard refuses only what it can witness.

`compile._build_ruled_band` refuses to re-bucket a band on its author rules when the rules give
fewer columns than the band's rules-free gutter count (`compile._word_column_count`), on the stated
ground that such a re-bucket "can only FUSE". cbh T1 refuted the count as a proxy for fusion: its
header words sit wholly beside the body numbers of the same ruled cell, so the gutter profile
counts extra columns although nothing would fuse. The guard is now a conjunction — the count AND
an exact fusion witness (`vocab/queries/rebucket-fuses.rq`, AXIOM). These tests pin both halves:

* U1 — the T1 defect with no witness: the count refuses on its own (measured below, so the test
  pins the guard and not a band the count never touched), and the band now re-buckets into one
  header cell per rule interval. The middle cell's `MAIN WHEAT GRADES` is a multi-word cell whose
  inter-word gaps a wider body word bridges; it is what a witness without its `NOT EXISTS` fires on.
* U2 — the same grid plus one body line with two words in one rule interval across a gap no other
  line covers: a genuine witness, so the refusal stands and the header stays word-level.
* I-3b-3 — the Python glue carries no numeric tolerance (the `.rq` half is
  `test_transform_gate.test_no_tuned_constant_in_rq_files`).
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from tests.etkl import fixtures as F
from tests.etkl.test_transform_gate import _FLOAT, _strip_comments


def _ruled_sub(path):
    """The one ruled sub-band of the fixture page, with its rules and the page chars — the same
    selection `compile.page_bands` makes before it calls `_build_ruled_band`."""
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.geometry import extract_chars, extract_rules, extract_words, text_lines
    from iladub.etkl.segment import segment

    page_rules = extract_rules(path, 0)
    found = []
    for band in detect_bands(text_lines(extract_words(path, 0))):
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules
                              if r.top <= sub.bottom and r.bottom >= sub.top)
            if sub_rules:
                found.append((sub, sub_rules))
    assert len(found) == 1, f"fixture must yield exactly one ruled sub-band, got {len(found)}"
    sub, sub_rules = found[0]
    return sub, sub_rules, extract_chars(path, 0)


def _count_refuses(sub, sub_rules):
    """The R225 count, recomputed with the guard's own operands: True iff it refuses alone."""
    from iladub.etkl.compile import _word_column_count
    xs = sorted({round(r.x, 2) for r in sub_rules})
    return len(xs) - 1 < _word_column_count(sub), len(xs) - 1, _word_column_count(sub)


def test_u1_a_header_beside_its_body_rebuckets_one_cell_per_rule_interval(tmp_path):
    from iladub.etkl.compile import _build_ruled_band
    p = os.path.join(str(tmp_path), "u1.pdf")
    truth = F.header_beside_body_ruled_pdf(p)
    sub, sub_rules, chars = _ruled_sub(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, (f"the count must refuse this band on its own ({rule_cols} rule columns vs "
                     f"{word_cols} word columns), or U1 pins nothing")
    band = _build_ruled_band(sub, sub_rules, (), chars)
    assert [w.text for w in band.lines[0].words] == truth["header_cells"]
    assert len(band.lines[0].words) == len(truth["rule_xs"]) - 1


def test_u2_a_real_fusion_witness_keeps_the_refusal(tmp_path):
    from iladub.etkl.compile import _build_ruled_band
    p = os.path.join(str(tmp_path), "u2.pdf")
    F.header_beside_body_ruled_pdf(p, fusing_line=True)
    sub, sub_rules, chars = _ruled_sub(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, f"the count must refuse ({rule_cols} vs {word_cols}), or U2 pins nothing"
    band = _build_ruled_band(sub, sub_rules, (), chars)
    assert [w.text for w in band.lines[0].words] == ["PORT", "MAIN", "WHEAT", "GRADES", "TOTAL"]
    assert band.column_xs == ()
    assert [[w.text for w in ln.words] for ln in band.lines] == \
        [[w.text for w in ln.words] for ln in sub.lines], "a refused band is the word band"


def test_the_fusion_glue_carries_no_tolerance():
    """I-3b-3, Python half: the glue emits evidence and runs the query; it decides nothing."""
    import iladub.etkl.fusion as fusion
    body = _strip_comments(open(fusion.__file__, encoding="utf-8").read())
    assert not _FLOAT.search(body), "fusion.py (engine glue) must carry no numeric tolerance"


# --- fix round 1 (spec § 8.6): the witness reads the cells the re-bucket FORMS ---------------------
# § 8.2's witness modelled the re-bucket's cells as the author intervals, and `rule_aware_lines`
# forms different ones. U4 and U5 are the two holes the Task 3b review built on U1's geometry. In
# each, the count refuses on its own, the re-bucket FORMS a cell that joins two words across a gap
# no word of the band covers, and the interval witness saw nothing, so db47fde accepted the band
# and shipped the fused cell (measured). Both must stay refused.

def _formed_cells(sub, sub_rules, chars):
    """The cells the re-bucket would form — `compile._build_ruled_band`'s own `band_chars`
    selection over the ruled sub-band, re-bucketed on its rule x's."""
    from iladub.etkl.geometry import rule_aware_lines
    xs = sorted({round(r.x, 2) for r in sub_rules})
    band_chars = [c for c in chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
    return [[w.text for w in ln.words] for ln in rule_aware_lines(band_chars, xs)]


def _assert_refused_to_the_word_band(band, sub):
    assert band.column_xs == ()
    assert [[w.text for w in ln.words] for ln in band.lines] == \
        [[w.text for w in ln.words] for ln in sub.lines], "a refused band is the word band"


def test_u4_an_edge_column_formed_past_the_outer_rule_keeps_the_refusal(tmp_path):
    """Interior-only rules [110, 250, 330]: `rule_aware_lines` extends the left column to the ink,
    so `AB` and `CD` land in one formed cell although no author interval holds them."""
    from iladub.etkl.compile import _build_ruled_band
    p = os.path.join(str(tmp_path), "u4.pdf")
    F.header_beside_body_ruled_pdf(p, fusing_line=True, rules=[110.0, 250.0, 330.0])
    sub, sub_rules, chars = _ruled_sub(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, f"the count must refuse ({rule_cols} vs {word_cols}), or U4 pins nothing"
    assert ["ABCD", "APW1/ASW9/AWW1/ANW1", "1,293"] in _formed_cells(sub, sub_rules, chars), \
        "the re-bucket must FORM the fused cell, or U4 pins nothing"
    band = _build_ruled_band(sub, sub_rules, (), chars)
    _assert_refused_to_the_word_band(band, sub)


def test_u5_a_divider_dropped_by_a_straddling_word_keeps_the_refusal(tmp_path):
    """Rules [40, 110, 250, 330] with `STRADDLER` crossing x=110 beside `KWI`: `_row_dividers` drops
    110 for that row (R154), so `KWI` and `STRADDLER` land in one formed cell although the
    straddler lies wholly inside no author interval."""
    from iladub.etkl.compile import _build_ruled_band
    p = os.path.join(str(tmp_path), "u5.pdf")
    F.header_beside_body_ruled_pdf(p, extra_row=[(45.0, "KWI"), (98.0, "STRADDLER"), (255.0, "1,293")])
    sub, sub_rules, chars = _ruled_sub(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, f"the count must refuse ({rule_cols} vs {word_cols}), or U5 pins nothing"
    assert ["KWISTRADDLER", "1,293"] in _formed_cells(sub, sub_rules, chars), \
        "the re-bucket must FORM the fused cell, or U5 pins nothing"
    band = _build_ruled_band(sub, sub_rules, (), chars)
    _assert_refused_to_the_word_band(band, sub)


# --- fix round 2: the witness judges the lines the accept path SHIPS, after the weld -------------
# `geometry.weld_hrule_boxes` runs after the re-bucket and re-forms the welded header rows' cells
# by centre over the UNEXTENDED author rules, sending a cell left of the first rule into the LAST
# column. With interior-only rules and a two-line header in a leading full-width hrule box, the
# re-bucket forms no fused cell (so a witness read before the weld is False), and the weld then
# ships `PORT TOTAL NAME` spanning x 45 -> 325. Measured: 221087d shipped it; c68e437 refused
# (count alone). Task 3b re-review, N1.

def _ruled_sub_with_hrules(path):
    """`_ruled_sub` plus the sub-band's hrules, filtered as `compile.page_bands` filters them."""
    from iladub.etkl.geometry import extract_hrules
    sub, sub_rules, chars = _ruled_sub(path)
    sub_hrules = tuple(h for h in extract_hrules(path, 0) if sub.top <= h.y <= sub.bottom)
    return sub, sub_rules, sub_hrules, chars


def test_u4c_a_weld_that_joins_an_edge_cell_to_the_last_column_keeps_the_refusal(tmp_path):
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.geometry import rule_aware_lines
    p = os.path.join(str(tmp_path), "u4c.pdf")
    F.header_beside_body_ruled_pdf(p, rules=[110.0, 250.0, 330.0], welded_header=True)
    sub, sub_rules, sub_hrules, chars = _ruled_sub_with_hrules(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, f"the count must refuse ({rule_cols} vs {word_cols}), or U4c pins nothing"
    assert len(sub_hrules) >= 2, "the leading hrule box must reach the band, or nothing is welded"
    xs = sorted({round(r.x, 2) for r in sub_rules})
    band_chars = [c for c in chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
    rel = rule_aware_lines(band_chars, xs)
    assert [w.text for w in rel[0].words] == ["PORT", "MAIN WHEAT", "TOTAL"], \
        "the re-bucket alone must form no fused header cell, or U4c does not isolate the weld"
    band = _build_ruled_band(sub, sub_rules, sub_hrules, chars)
    _assert_refused_to_the_word_band(band, sub)


def test_u4c_control_a_licensed_weld_is_still_accepted(tmp_path):
    """The same page with a left rule at 40: the weld joins each column's two header lines, which
    is its licence (the wrapped header names), and no welded cell spans an uncovered point."""
    from iladub.etkl.compile import _build_ruled_band
    p = os.path.join(str(tmp_path), "u4c_ctl.pdf")
    F.header_beside_body_ruled_pdf(p, welded_header=True)
    sub, sub_rules, sub_hrules, chars = _ruled_sub_with_hrules(p)
    refuses, rule_cols, word_cols = _count_refuses(sub, sub_rules)
    assert refuses, f"the count must refuse ({rule_cols} vs {word_cols}), or the control pins nothing"
    band = _build_ruled_band(sub, sub_rules, sub_hrules, chars)
    assert [w.text for w in band.lines[0].words] == ["PORT NAME", "MAIN WHEAT GRADES", "TOTAL"]
