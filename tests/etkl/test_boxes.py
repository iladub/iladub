"""The box reader (spec 2026-09-28-box-split-design.md § 2, § 5 O1/N1-N3).

`iladub.etkl.boxes` reads the author's CLOSED RULED BOXES off a page: a rule reader (§ 2.1), touch
under the stroke-width bound (§ 2.2), closed frames (§ 2.3) and title bars (§ 2.4). These tests
pin each of those on synthetic fixtures (CI) and on the corpus pages the spec measured (§ 7.1-7.2,
local only).
"""
import math
import os

import pytest

from iladub.etkl.boxes import BoxRule, page_boxes, touches
from tests.etkl import fixtures as F

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")


def corpus_only(fn):
    fn = pytest.mark.skipif(not (os.path.exists(CBH) and os.path.exists(BFS)),
                            reason="corpus not fetched")(fn)
    return pytest.mark.corpus(fn)


# --- O1 / N1 / N2 / N3: synthetic, in CI ------------------------------------------------------

def test_two_boxes_in_one_band_are_two_boxes_each_with_its_title_bar(tmp_path):
    p = str(tmp_path / "two.pdf")
    exp = F.two_boxes_one_band_pdf(p)
    boxes = sorted(page_boxes(p, 0), key=lambda b: b.x0)
    assert len(boxes) == 2
    left, right = boxes
    assert len(left.verticals) == exp["left"]["n_verticals"] == 4
    assert len(right.verticals) == exp["right"]["n_verticals"] == 3
    assert len(left.horizontals) == exp["left"]["n_horizontals"]
    assert len(right.horizontals) == exp["right"]["n_horizontals"]
    assert left.title_bar is not None and right.title_bar is not None
    # each bar sits over its own box and above it
    for box in (left, right):
        tx0, tx1, ttop, tbottom = box.title_bar
        assert box.x0 <= tx0 and tx1 <= box.x1
        assert ttop < box.top


def test_n1_one_box_with_ink_outside_is_one_box_with_its_title_bar(tmp_path):
    p = str(tmp_path / "n1.pdf")
    exp = F.one_box_with_title_pdf(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == exp["n_boxes"] == 1
    (box,) = boxes
    assert box.title_bar is not None
    # stroked-rect edges + a black-filled rect + stroked lines, all read as rules
    assert len(box.verticals) == exp["n_verticals"]
    assert len(box.horizontals) == exp["n_horizontals"]


def test_n2_open_header_only_lattices_are_not_boxes(tmp_path):
    p = str(tmp_path / "n2.pdf")
    exp = F.open_lattices_pdf(p)
    assert page_boxes(p, 0) == [] and exp["n_boxes"] == 0


def test_n3_a_sub_stroke_gap_joins_the_frame(tmp_path):
    p = str(tmp_path / "n3.pdf")
    exp = F.sub_stroke_gap_box_pdf(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == 1
    assert len(boxes[0].verticals) == exp["n_verticals"]


def test_a_page_with_no_rules_has_no_boxes(tmp_path):
    # MEASURED 2026-09-28: simple_table_pdf draws 0 rects, 0 lines, 0 curves (drawString only).
    p = str(tmp_path / "plain.pdf")
    F.simple_table_pdf(p)
    assert page_boxes(p, 0) == []


# --- touch (§ 2.2, R-c): pure function ----------------------------------------------------------

def _h(x0, x1, top, bottom):
    return BoxRule("H", x0, x1, top, bottom)


def _v(x0, x1, top, bottom):
    return BoxRule("V", x0, x1, top, bottom)


def test_touch_a_the_cbh_corner_joins_across_a_sub_stroke_gap():
    # cbh p0's right box: a horizontal starting at 543.89, a 0.48-wide vertical ending at 543.88998.
    h = _h(543.89, 690.43, 689.64, 690.12)
    v = _v(543.41, 543.88998, 689.64, 722.28)
    assert touches(h, v) is True


def test_touch_b_a_zero_width_rule_touches_only_exactly():
    h = _h(543.89, 690.43, 689.64, 690.12)
    v = _v(543.88998, 543.88998, 689.64, 722.28)
    assert touches(h, v) is False
    assert touches(h, _v(543.89, 543.89, 689.64, 722.28)) is True   # gap 0


def test_touch_c_the_bound_is_the_thinner_stroke_exactly():
    v = _v(0.0, 0.5, 0.0, 10.0)                  # thickness 0.5
    h_at = _h(1.0, 5.0, 0.0, 1.0)                # thickness 1.0; x-gap exactly 0.5
    assert touches(h_at, v) is True
    h_past = _h(math.nextafter(1.0, math.inf), 5.0, 0.0, 1.0)   # 0.5 + the next float
    assert touches(h_past, v) is False
    # same in y
    h_y = _h(0.0, 5.0, 10.5, 11.0)               # thickness 0.5; y-gap exactly 0.5
    assert touches(h_y, v) is True
    assert touches(_h(0.0, 5.0, math.nextafter(10.5, math.inf), 11.0), v) is False


# --- corpus leg (§ 7.1-7.2), local only ----------------------------------------------------------

@corpus_only
def test_cbh_p0_has_six_closed_boxes_and_the_small_one_has_three_verticals():
    boxes = page_boxes(CBH, 0)
    assert len(boxes) == 6
    small = [b for b in boxes if b.x0 > 500 and b.x1 < 700]
    assert len(small) == 1
    assert len(small[0].verticals) == 3
    assert [round(v, 2) for v in (small[0].x0, small[0].x1, small[0].top, small[0].bottom)] \
        == [543.41, 690.43, 689.64, 722.28]
    assert all(b.title_bar is not None for b in boxes)


@corpus_only
@pytest.mark.parametrize("page", [5, 6])
def test_bfs_header_only_lattices_are_not_boxes(page):
    assert page_boxes(BFS, page) == []
