"""The box-split DECISION (spec 2026-09-28-box-split-design.md § 3.2, ruling R-d).

`iladub.etkl.boxsplit` decides which text bands hold >= 2 of the author's closed ruled boxes
(spec's O1/N1/N2), on top of Task 1's box reader (boxes.py). Bands, exactly as `compile.page_bands`
builds its RAW band list (measured below, R2): `detect_bands(text_lines(extract_words(p)))`.
"""
import os

import pytest

from iladub.etkl.bands import detect_bands
from iladub.etkl.boxes import page_boxes
from iladub.etkl.boxsplit import _box_owner, bands_to_split, box_evidence
from iladub.etkl.geometry import extract_words, text_lines
from tests.etkl import fixtures as F

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")


def _raw_bands(pdf_path: str, page_number: int = 0):
    """R2: the IDENTICAL computation `compile.page_bands` uses to build `raw_bands`
    (`compile.py` — `words = extract_words(pdf_path, page_number)`;
    `raw_bands = detect_bands(text_lines(words))`), so an index this module returns names the
    same band `compile_tables`' `for band in raw_bands:` loop does."""
    return detect_bands(text_lines(extract_words(pdf_path, page_number)))


def corpus_only(fn):
    fn = pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")(fn)
    return pytest.mark.corpus(fn)


# --- Step 1/2: the decision, on Task 1's fixtures -----------------------------------------------

def test_two_boxes_one_band_selects_the_shared_band_with_both_boxes(tmp_path):
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    result = bands_to_split(bands, boxes)
    assert len(result) == 1
    (idx, selected), = result.items()
    assert len(selected) == 2
    assert {round(b.x0) for b in selected} == {40, 400}
    # every word of the shared band is accounted for by exactly one of the two boxes or by
    # neither (I-2a): both boxes must actually resolve to the SAME band index.
    assert {_box_owner(b, bands) for b in selected} == {idx}


def test_n1_one_box_with_ink_outside_does_not_split(tmp_path):
    p = str(tmp_path / "n1.pdf")
    F.one_box_with_title_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == 1              # Task 1's own pin; one box only, below the R-d floor
    assert bands_to_split(bands, boxes) == {}


def test_n2_open_lattices_do_not_split(tmp_path):
    p = str(tmp_path / "n2.pdf")
    F.open_lattices_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert boxes == []                  # Task 1's own pin; no closed box at all
    assert bands_to_split(bands, boxes) == {}


# --- the stroked-rect commission negative (Task 1 review) ---------------------------------------

def test_two_wordless_stroked_separators_do_not_split(tmp_path):
    """A band with two closed boxes (Task 1's own commission: a single thin STROKED rect reads
    as a closed box) but NEITHER contains a single word. I-2a's "a box containing no words
    belongs to no band" must exclude both, so the band must not split even though it
    geometrically holds two closed boxes."""
    p = str(tmp_path / "wordless.pdf")
    F.wordless_separator_boxes_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == 2                                  # the commission itself, confirmed
    assert all(_box_owner(b, bands) is None for b in boxes)  # I-2a's word-count clause
    assert bands_to_split(bands, boxes) == {}


def test_a_wordless_box_emits_no_evidence_node_at_all():
    """I-2c: a box with no owner emits NOTHING into `box_evidence`'s graph — the query cannot
    defend against a node with no `tab:boxBandIndex` fact, so the emitter must never mint one."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Word
    from iladub.etkl.boxes import Box

    band = Band(lines=(Line(words=(Word("x", 500.0, 510.0, 0.0, 9.0),), top=0.0, bottom=9.0),),
                top=0.0, bottom=9.0)
    box = Box(x0=0.0, x1=100.0, top=0.0, bottom=9.0, verticals=(), horizontals=(), title_bar=None)
    g = box_evidence([band], [box])
    assert len(g) == 0


# --- I-2a straddling protection (Step 3 falsification fixture) ----------------------------------

def test_a_box_straddling_two_bands_belongs_to_neither(tmp_path):
    """The fixture Step 3's falsification requires: a box whose frame covers two bands that
    `detect_bands` itself splits (an internal text-row gap past `gap_factor`). I-2a's exact
    rule must refuse it — the population this repo's own "belong by y-overlap alone" variant
    would move (recorded in the task report; not shipped, since I-2a is the spec)."""
    p = str(tmp_path / "straddle.pdf")
    F.straddling_box_pdf(p)
    bands = _raw_bands(p)
    assert len(bands) == 2, "the fixture's own contract: the internal gap must split the page"
    boxes = page_boxes(p, 0)
    assert len(boxes) == 1
    box = boxes[0]
    assert _box_owner(box, bands) is None
    assert bands_to_split(bands, boxes) == {}


# --- Step 4: the corpus preview (a preview of Task 4's C1) --------------------------------------

@corpus_only
def test_cbh_p0_selects_exactly_band_9_with_two_boxes():
    """MEASURED 2026-09-28: raw band 9 is y 683.5-761.5 (10 lines) — the exact band spec § 1
    names. `page_boxes` finds 6 closed boxes on the page (4 rosters, T1, T2); only band 9's T1/T2
    pair meets the R-d floor."""
    bands = _raw_bands(CBH, 0)
    assert (round(bands[9].top, 1), round(bands[9].bottom, 1)) == (683.5, 761.5)
    boxes = page_boxes(CBH, 0)
    result = bands_to_split(bands, boxes)
    assert set(result) == {9}
    assert len(result[9]) == 2
    assert {round(b.x0) for b in result[9]} == {38, 543}
