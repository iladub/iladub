from iladub.etkl.geometry import Word, Line
from iladub.etkl.bands import Band
from iladub.etkl.regions import Cell
from iladub.etkl.roundtrip import cell_round_trips, render_ascii

BND = [72.0, 186.0, 335.0, 442.0]   # 3 columns


def test_contained_word_round_trips():
    w = Word("13.2", 240.0, 268.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w,)), BND) is True


def test_straddling_word_fails():
    # a word crossing the c1/c2 boundary (335.0) must fail — the oracle bites
    w = Word("TOOWIDE", 300.0, 360.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w,)), BND) is False


def test_multiword_cell_round_trips():
    w1 = Word("13.2", 240.0, 260.0, 100.0, 110.0)
    w2 = Word("mg", 265.0, 285.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w1, w2)), BND) is True


def test_render_ascii_places_words_left_to_right():
    line = Line((Word("A", 72.0, 82.0, 100.0, 110.0),
                 Word("B", 400.0, 410.0, 100.0, 110.0)), 100.0, 110.0)
    out = render_ascii(Band((line,), 100.0, 110.0), width=40)
    assert out.index("A") < out.index("B")
