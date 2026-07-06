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


def test_region_round_trips_pivot(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    assert region_round_trips(reg, band) is True


def test_region_round_trip_detects_missing_word(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    from iladub.etkl.bands import Band
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    # inject a stray word far outside the grid: must fail to place -> round-trip False
    from iladub.etkl.geometry import Word, Line
    stray = Line((Word("XXX", 5.0, 20.0, 400.0, 410.0),), 400.0, 410.0)
    band2 = Band(band.lines + (stray,), band.top, 410.0)
    assert region_round_trips(reg, band2) is False
