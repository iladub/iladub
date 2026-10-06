"""boxhead — a data grid's column identity, proposed by a reader and disposed by the grid.

The gap (2026-09-18): ons-index-of-services asserts 552 data cells and 0 column labels, and every
one of its 175 escalated tokens is header metadata. `datagrid.py` derives entries and, by design,
no header. This file pins the disposal; nothing here needs a model or a network.
"""
import os
from types import SimpleNamespace

import pytest

from iladub.etkl.boxhead import (BoxheadReading, FakeBoxheadReader, dispose_boxhead,
                                 header_block, label_text, listing_of, read_grid_boxhead)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONS = os.path.join(ROOT, "corpus", "gov-stats", "ons-index-of-services-2026-02.pdf")


def _w(text, x0, x1):
    return SimpleNamespace(text=text, x0=x0, x1=x1, top=0.0, bottom=1.0)


def _grid(rows=(2, 3), refusals=(0, 1)):
    """Three columns at [0,100) [100,200) [200,300); lines 0-1 refused, 2-3 admitted."""
    cols = tuple(SimpleNamespace(x0=float(a), x1=float(a + 100)) for a in (0, 100, 200))
    return SimpleNamespace(rows=tuple(rows), columns=cols,
                           refusals={j: "HeterogeneousColumn/every-measure" for j in refusals})


def _lines():
    """L0 is a title sitting over everything; L1 is three leaf labels, one per column."""
    return [SimpleNamespace(words=[_w("Quarterly", 80, 150), _w("index", 155, 210)], top=0, bottom=1),
            SimpleNamespace(words=[_w("Period", 10, 60), _w("Total", 120, 170),
                                   _w("Retail", 220, 280)], top=2, bottom=3),
            SimpleNamespace(words=[_w("2025", 10, 40), _w("1.0", 130, 150), _w("2.0", 230, 250)],
                            top=4, bottom=5),
            SimpleNamespace(words=[_w("2026", 10, 40), _w("1.1", 130, 150), _w("2.1", 230, 250)],
                            top=6, bottom=7)]


def _good():
    return BoxheadReading(
        leaf_labels=((0, ((1, 0),)), (1, ((1, 1),)), (2, ((1, 2),))),
        other_words=((0, 0), (0, 1)))


def test_the_header_block_is_the_refused_run_directly_above_the_first_row():
    assert header_block(_lines(), _grid()) == (0, 1)
    # A refused line that is NOT contiguous with the first row is not part of the block.
    assert header_block(_lines(), _grid(rows=(3,), refusals=(0, 2))) == (2,)
    assert header_block(_lines(), None) == ()


def test_the_listing_numbers_lines_within_the_block_and_words_left_to_right():
    assert listing_of(_lines(), (0, 1)) == ("L0: [0]Quarterly [1]index\n"
                                            "L1: [0]Period [1]Total [2]Retail")


def test_a_good_reading_labels_every_column_and_the_text_comes_from_the_text_layer():
    got = dispose_boxhead(_good(), _lines(), (0, 1), _grid())
    assert got.refused is None and got.dropped == ()
    assert sorted(got.labels) == [0, 1, 2]
    # The reader supplied ADDRESSES. The label's text is read back from the text layer.
    assert [label_text(_lines(), (0, 1), got.labels[c]) for c in (0, 1, 2)] == [
        "Period", "Total", "Retail"]


def test_refusal_1_an_address_outside_the_listing_refuses_the_whole_reading():
    r = BoxheadReading(leaf_labels=((0, ((1, 0),)), (1, ((1, 1),)), (2, ((9, 9),))),
                       other_words=((0, 0), (0, 1)))
    assert dispose_boxhead(r, _lines(), (0, 1), _grid()).refused == "an address outside the listing"


def test_refusal_1_a_column_outside_the_grid_refuses_the_whole_reading():
    r = BoxheadReading(leaf_labels=((0, ((1, 0),)), (1, ((1, 1),)), (7, ((1, 2),))),
                       other_words=((0, 0), (0, 1)))
    assert dispose_boxhead(r, _lines(), (0, 1), _grid()).refused == "a column index outside the grid"


def test_refusal_2_a_word_left_unaccounted_for_refuses_the_whole_reading():
    """The null control, and it FIRES. Silence about a word is never read as 'not a header': a
    reader that skips one is not reading the header."""
    r = BoxheadReading(leaf_labels=((0, ((1, 0),)), (1, ((1, 1),)), (2, ((1, 2),))),
                       other_words=((0, 0),))                      # (0,1) "index" is missing
    assert dispose_boxhead(r, _lines(), (0, 1), _grid()).refused == "a listed word left unaccounted for"


def test_refusal_2_a_word_used_twice_refuses_the_whole_reading():
    r = BoxheadReading(leaf_labels=((0, ((1, 0),)), (1, ((1, 1), (1, 2))), (2, ((1, 2),))),
                       other_words=((0, 0), (0, 1)))
    assert dispose_boxhead(r, _lines(), (0, 1), _grid()).refused == "a word used twice"


def test_check_3_a_misplaced_label_is_DROPPED_and_the_rest_stand():
    """Two independent readings must agree label by label. The reader puts 'Retail' (centre 250,
    column 2) under column 1 and 'Total' under column 2: both misplaced labels are dropped — no
    claim — and column 0, placed correctly, stands. A whole-reading refusal here would throw away
    a right answer for the wrong ones beside it."""
    r = BoxheadReading(leaf_labels=((0, ((1, 0),)), (1, ((1, 2),)), (2, ((1, 1),))),
                       other_words=((0, 0), (0, 1)))
    got = dispose_boxhead(r, _lines(), (0, 1), _grid())
    assert got.refused is None
    assert sorted(got.labels) == [0] and got.dropped == (1, 2)


def _straddling_lines():
    """L0 is a two-line boxhead's top: `Period`, then `80 ans` whose `80` (92-104, centre 98)
    sits left of column 1's edge at 100 while the run (92-150, centre 121) is inside column 1 —
    bfs p6's `80 ans ou plus` in miniature. L1 is that label's second line, `ou plus` (110-160)."""
    return [SimpleNamespace(words=[_w("Period", 10, 60), _w("80", 92, 104), _w("ans", 110, 150),
                                   _w("Retail", 220, 280)], top=0, bottom=1),
            SimpleNamespace(words=[_w("ou", 110, 125), _w("plus", 130, 160)], top=2, bottom=3),
            SimpleNamespace(words=[_w("2025", 10, 40), _w("1.0", 130, 150), _w("2.0", 230, 250)],
                            top=4, bottom=5),
            SimpleNamespace(words=[_w("2026", 10, 40), _w("1.1", 130, 150), _w("2.1", 230, 250)],
                            top=6, bottom=7)]


def test_r293_a_label_is_placed_by_its_run_on_each_line_not_by_each_word():
    """R293 (`2026-10-05-r293-p6-adopts.md` § 2.3): `80`'s own centre is in column 0, but the
    label's ink on that line is one run centred in column 1, and so is its second line. It
    stands. Under the per-word rule it was dropped."""
    r = BoxheadReading(leaf_labels=((0, ((0, 0),)), (1, ((0, 1), (0, 2), (1, 0), (1, 1))),
                                    (2, ((0, 3),))), other_words=())
    got = dispose_boxhead(r, _straddling_lines(), (0, 1), _grid(rows=(2, 3), refusals=(0, 1)))
    assert got.refused is None
    assert sorted(got.labels) == [0, 1, 2] and got.dropped == ()


def test_r293_control_a_label_whose_run_on_one_line_sits_in_another_column_is_still_dropped():
    """The control, and it separates per-LINE from a pooled box: the label's line-0 run is `ans`
    (110-150, column 1) and its line-1 run is `ou plus` moved to 210-290 (column 2). Pooled, the
    box 110-290 is centred at 200, inside column 2, and would stand. Per line, the line-0 run is in
    column 1, so the label claimed by column 2 is dropped: a far-off line is not averaged in."""
    lines = _straddling_lines()
    lines[1] = SimpleNamespace(words=[_w("ou", 210, 240), _w("plus", 250, 290)], top=2, bottom=3)
    r = BoxheadReading(leaf_labels=((0, ((0, 0),)), (2, ((0, 2), (1, 0), (1, 1)))),
                       other_words=((0, 1), (0, 3)))
    got = dispose_boxhead(r, lines, (0, 1), _grid(rows=(2, 3), refusals=(0, 1)))
    assert got.refused is None
    assert sorted(got.labels) == [0] and got.dropped == (2,)


def test_a_refusing_reader_and_a_missing_one_label_nothing():
    assert dispose_boxhead(BoxheadReading(refuses_grid=True, cols_seen=5),
                           _lines(), (0, 1), _grid()).labels == {}
    assert dispose_boxhead(None, _lines(), (0, 1), _grid()).labels == {}


@pytest.mark.skipif(not os.path.exists(ONS), reason="corpus not fetched")
def test_ons_p7_has_a_header_block_that_covers_every_grid_column():
    """The real page. The grid derives 6 columns and admits its first row at page line 8; the 8
    lines above it are all refused, and they are the title, the spanners and a 4-line boxhead."""
    from iladub.etkl import extract_words, text_lines
    from iladub.etkl.datagrid import derive_data_grid
    grid = derive_data_grid(ONS, 7)
    lines = sorted([ln for ln in text_lines(extract_words(ONS, 7)) if ln.words],
                   key=lambda ln: ln.top)
    block = header_block(lines, grid)
    assert len(grid.columns) == 6 and block == tuple(range(8))
    assert "[0]Section" in listing_of(lines, block).splitlines()[-1]


@pytest.mark.skipif(not os.path.exists(ONS), reason="corpus not fetched")
def test_a_reader_that_RAISES_labels_nothing_and_does_not_propagate():
    from iladub.etkl import extract_words, text_lines
    from iladub.etkl.datagrid import derive_data_grid

    class _Raises:
        def read_boxhead(self, crop_png, ncols, listing):
            raise RuntimeError("unparseable")

    grid = derive_data_grid(ONS, 7)
    lines = sorted([ln for ln in text_lines(extract_words(ONS, 7)) if ln.words],
                   key=lambda ln: ln.top)
    got = read_grid_boxhead(ONS, 7, lines, grid, _Raises())
    assert got.labels == {} and got.refused == "the reader raised"
    assert read_grid_boxhead(ONS, 7, lines, grid, None).refused == "no reader"
    assert read_grid_boxhead(ONS, 7, lines, grid, FakeBoxheadReader(None)).refused == "no reading"
