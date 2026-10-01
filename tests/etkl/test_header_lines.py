"""Box-split § 10 (Task 3d.5): U13, the worker `CountHeaderLines` and its recorded readings.

Split out of `test_boxhead_absence.py` (U10, U11, U14) for the reason `test_row_zero_differs.py`
was: together they would pass the plan's ~600-line mark. Spec
`docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.3.3 / § 10.5 U13; plan Task 3d.5 as
amended by A2 (the dedupe is MODULE-GLOBAL and pinned here) and the listing-unit minor.

No case touches the network: the no-recording case asserts `BamlHeaderLinesReader` is never
constructed, and the dedupe case stubs the generated function itself.
"""
import dataclasses
import json

import pytest

from iladub.etkl import headerlines as H


@pytest.fixture
def region_pdf(tmp_path):
    """The RECORD region the U11 fixture compiles: 3 columns, a header line over 3 body lines."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import simple_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.regions import classify, RegionKind
    p = tmp_path / "x.pdf"; simple_table_pdf(str(p))
    region = classify(detect_bands(text_lines(extract_words(str(p))))[1])
    assert region.kind is RegionKind.RECORD_TABLE and len(region.band.lines) == 4
    return region, str(p)


@pytest.fixture(autouse=True)
def _fresh_cache_and_readings(monkeypatch, tmp_path):
    """The live cache is module-global (A2), so it leaks across tests unless cleared; and every
    test reads recordings from its own empty directory, never the committed ones.

    NO CASE MAY REACH THE MODEL, even under a mutant. Measured 2026-09-30: with
    `ANTHROPIC_API_KEY` in the shell, the falsification that builds the live reader
    unconditionally made one real call from the moved-cell case. So the key is removed (BAML reads
    env lazily, per call: `baml_client/globals.py`) and the generated function is a tripwire; the
    dedupe case replaces the tripwire with its own counting stub."""
    H._HEADER_LINES_CACHE.clear()
    d = tmp_path / "readings"
    d.mkdir()
    monkeypatch.setattr(H, "READINGS_DIR", d)
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.delenv("ILADUB_RECORD_READINGS", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        from baml_client import sync_client
    except ImportError:
        sync_client = None
    if sync_client is not None:
        def _tripwire(*a, **k):
            raise AssertionError("U13 reached the live CountHeaderLines")
        monkeypatch.setattr(sync_client.b, "CountHeaderLines", _tripwire, raising=True)
    yield d
    H._HEADER_LINES_CACHE.clear()


def _with_cell_text(region, row, col, text):
    """The same region with one cell's text replaced (its first word's text; geometry kept)."""
    cells = []
    for c in region.cells:
        if (c.row, c.col) == (row, col):
            w = dataclasses.replace(c.words[0], text=text)
            c = dataclasses.replace(c, words=(w,) + tuple(c.words[1:]))
        cells.append(c)
    return dataclasses.replace(region, cells=tuple(cells))


def _record(directory, region, header_lines, note="recorded"):
    key = H.question_key(region.grid.ncols, H.listing_of(region))
    (directory / f"{key}.json").write_text(
        json.dumps({"header_lines": header_lines, "note": note}), encoding="utf-8")


# ------------------------------------------------------------------ the question

def test_u13_listing_is_every_row_numbered_cells_in_column_order(region_pdf):
    region, _ = region_pdf
    assert H.listing_of(region) == (
        "L0: Analyte | Value | Unit\n"
        "L1: Hemoglobin | 13.2 | g/dL\n"
        "L2: Hematocrit | 39.5 | %\n"
        "L3: Platelets | 250 | x10^9/L")


def test_u13_a_wrapped_cell_stays_one_listing_line(region_pdf):
    """The listing unit (minor): a listing line IS a region row. A cell whose text carries a line
    break (the OCR path's `OcrRegion.text` is an unconstrained str) is joined with a space, so the
    listing's line count stays `nlines`."""
    region, _ = region_pdf
    wrapped = _with_cell_text(region, 1, 0, "Hemo\nglobin")
    listing = H.listing_of(wrapped)
    assert len(listing.splitlines()) == len(region.band.lines) == 4
    assert listing.splitlines()[1] == "L1: Hemo globin | 13.2 | g/dL"


def test_u13_the_key_is_the_whole_question(region_pdf):
    """Moving ONE BODY cell's text moves the key: the body rows are part of the question (spec
    § 10.3.3). The ncols half: the same listing under another column count is another question."""
    region, _ = region_pdf
    k = H.question_key(3, H.listing_of(region))
    assert H.question_key(3, H.listing_of(_with_cell_text(region, 2, 1, "39.6"))) != k
    assert H.question_key(4, H.listing_of(region)) != k
    assert H.question_key(3, H.listing_of(region)) == k


# ------------------------------------------------------------------ recorded readings

def test_u13_a_recorded_reading_replays_by_key(region_pdf, _fresh_cache_and_readings):
    region, pdf = region_pdf
    _record(_fresh_cache_and_readings, region, 0, note="row 0 reads as data")
    got = H.ask_header_lines(region, pdf, 0, H.default_reader())
    assert got == H.HeaderLinesReading(header_lines=0, note="row 0 reads as data")


def test_u13_a_moved_body_cell_misses_the_recording(region_pdf, _fresh_cache_and_readings):
    """The recording answers the question it was asked, and no other: the same region with one
    body cell moved finds no recording, and with no live reader that is no claim."""
    region, pdf = region_pdf
    _record(_fresh_cache_and_readings, region, 0)
    moved = _with_cell_text(region, 3, 2, "x10^6/L")
    assert H.ask_header_lines(moved, pdf, 0, H.default_reader()) is None


def test_u13_no_recording_and_no_baml_live_is_no_claim_and_no_network(region_pdf, monkeypatch):
    region, pdf = region_pdf
    built = []

    class _Spy:
        def __init__(self):
            built.append(self)

        def count_header_lines(self, crop_png, ncols, listing):
            return None

    monkeypatch.setattr(H, "BamlHeaderLinesReader", _Spy)
    assert H.ask_header_lines(region, pdf, 0, H.default_reader()) is None
    assert built == []


def test_u13_the_spy_is_live_only_under_baml_live(region_pdf, monkeypatch):
    """The positive control for the case above: under `BAML_LIVE=1` the same spy IS constructed,
    so `built == []` there is the gate working, not a spy that can never be reached."""
    import importlib.util
    if importlib.util.find_spec("baml_client") is None:
        pytest.skip("baml_client not generated")
    region, pdf = region_pdf
    built = []

    class _Spy:
        def __init__(self):
            built.append(self)

        def count_header_lines(self, crop_png, ncols, listing):
            return None

    monkeypatch.setattr(H, "BamlHeaderLinesReader", _Spy)
    monkeypatch.setenv("BAML_LIVE", "1")
    assert H.ask_header_lines(region, pdf, 0, H.default_reader()) is None
    assert len(built) == 1


# ------------------------------------------------------------------ the closed-answer check

@pytest.mark.parametrize("answer", [-1, 5])          # nlines = 4, so 5 is nlines + 1
def test_u13_an_out_of_range_answer_is_no_claim(region_pdf, answer):
    region, pdf = region_pdf
    reader = H.FakeHeaderLinesReader(H.HeaderLinesReading(header_lines=answer, note=""))
    assert H.ask_header_lines(region, pdf, 0, reader) is None


@pytest.mark.parametrize("answer", [0, 1, 4])        # both ends of 0..nlines stand
def test_u13_an_in_range_answer_stands(region_pdf, answer):
    region, pdf = region_pdf
    r = H.HeaderLinesReading(header_lines=answer, note="n")
    assert H.ask_header_lines(region, pdf, 0, H.FakeHeaderLinesReader(r)) == r


def test_u13_a_raising_reader_is_no_claim(region_pdf):
    region, pdf = region_pdf

    class _Raises:
        def count_header_lines(self, crop_png, ncols, listing):
            raise RuntimeError("the model is unreachable")

    assert H.ask_header_lines(region, pdf, 0, _Raises()) is None


def test_u13_no_reader_and_a_none_reading_are_no_claim(region_pdf):
    region, pdf = region_pdf
    assert H.ask_header_lines(region, pdf, 0, None) is None
    assert H.ask_header_lines(region, pdf, 0, H.FakeHeaderLinesReader(None)) is None


def test_u13_the_reader_is_asked_the_regions_question(region_pdf):
    """What reaches the reader is the region's own question: its column count, its listing, and
    a PNG crop of its extent."""
    region, pdf = region_pdf
    seen = []

    class _Spy:
        def count_header_lines(self, crop_png, ncols, listing):
            seen.append((crop_png, ncols, listing))
            return H.HeaderLinesReading(header_lines=1, note="")

    H.ask_header_lines(region, pdf, 0, _Spy())
    (crop, ncols, listing), = seen
    assert crop[:8] == b"\x89PNG\r\n\x1a\n"
    assert (ncols, listing) == (3, H.listing_of(region))


# ------------------------------------------------------------------ the dedupe (A2)

def test_u13_one_live_call_per_distinct_question_across_instances(monkeypatch):
    """`default_reader()` is called once per region, so an INSTANCE cache dedupes nothing: two
    `BamlHeaderLinesReader`s asked the same question make ONE call; another listing makes a
    second. The generated function is stubbed with a counter, so nothing leaves the machine."""
    pytest.importorskip("baml_py")
    sync_client = pytest.importorskip("baml_client.sync_client")
    from types import SimpleNamespace
    calls = []

    def _stub(page, ncols, listing):
        calls.append((ncols, listing))
        return SimpleNamespace(header_lines=1, note="stub")

    monkeypatch.setattr(sync_client.b, "CountHeaderLines", _stub, raising=True)
    crop, listing = b"\x89PNG\r\n\x1a\nnot-really", "L0: a | b\nL1: 1 | 2"
    a = H.BamlHeaderLinesReader().count_header_lines(crop, 2, listing)
    b = H.BamlHeaderLinesReader().count_header_lines(crop, 2, listing)
    assert a == b == H.HeaderLinesReading(header_lines=1, note="stub")
    assert len(calls) == 1
    H.BamlHeaderLinesReader().count_header_lines(crop, 2, listing + "\nL2: 3 | 4")
    assert len(calls) == 2
