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


def test_render_region_ascii_legible(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import render_region_ascii
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    out = render_region_ascii(reg)
    assert len(out.splitlines()) >= 2
    assert "Current" in out and "Prior" in out      # merged parents rendered
    assert "Hemoglobin" in out                        # a body row rendered


def test_region_round_trip_rejects_straddling_body_cell(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Word, Line
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    # Inject a word in a body row whose x-extent crosses boundary[1] (139.5).
    # center 140.0 is inside the grid; cy is within row 0's padded extent.
    # This is the silent-wrong scenario: word is assigned to col 1 by center
    # but its ink spills into col 0 — region_round_trips must now reject it.
    b = reg.grid.boundaries            # (50.0, 139.5, 220.0, ...)
    body_top = reg.rows[0].top         # ~136.94
    straddle = Word("STRAD", b[1] - 9.5, b[1] + 10.5, body_top, body_top + 10.0)
    new_line = Line((straddle,), body_top, body_top + 10.0)
    band2 = Band(band.lines + (new_line,), band.top, band.bottom)
    assert region_round_trips(reg, band2) is False


def test_region_round_trip_rejects_gap_word(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Word, Line
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    # a word INSIDE the horizontal grid but at a y in NEITHER a header level nor a
    # body row band (placements == 0) must fail the exactly-one gate
    gx = (reg.grid.boundaries[0] + reg.grid.boundaries[-1]) / 2.0
    # Place gap_y midway between last header line and first body row, clearly in neither
    last_header_y = max(w.top for ln in band.lines[:reg.body_line] for w in ln.words)
    first_body_y = reg.rows[0].top
    gap_y = (last_header_y + first_body_y) / 2.0
    w = Word("GAP", gx, gx + 10.0, gap_y, gap_y + 8.0)
    band2 = Band(band.lines + (Line((w,), gap_y, gap_y + 8.0),), band.top, band.bottom)
    assert region_round_trips(reg, band2) is False
