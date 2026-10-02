"""R261 loop (b) Task 3: the `AskTotalRole` worker stack (spec § 3).

Mirrors `test_printed_total.py`'s isolation and unit-test shape for the sibling question "what role
does this number play" (`table_total | total_of_totals | other | cannot_tell`), asked over the
DERIVED crop (N8) of a candidate total's operands. No case touches the network: the isolation
fixture below tripwires `AskTotalRole` exactly as `test_printed_total.py`'s tripwires
`AskPrintedTotal`. The binding (a later task) is not tested here — only the worker stack.
"""
import hashlib
import json

import pytest

from iladub.etkl import totalrole as R
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word


@pytest.fixture(autouse=True)
def _fresh_cache_and_readings(monkeypatch, tmp_path):
    """Copied from `test_printed_total.py`'s `_fresh_cache_and_readings` (itself copied from
    `test_header_lines.py`, M9): the live cache is module-global, so it is cleared; every test reads
    recordings from its own empty directory; and NO CASE MAY REACH THE MODEL — the key is removed
    and the generated function is a tripwire."""
    R._TOTAL_ROLE_CACHE.clear()
    d = tmp_path / "readings"
    d.mkdir()
    monkeypatch.setattr(R, "READINGS_DIR", d)
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.delenv("ILADUB_RECORD_READINGS", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        from baml_client import sync_client
    except ImportError:
        sync_client = None
    if sync_client is not None:
        def _tripwire(*a, **k):
            raise AssertionError("a total-role test reached the live AskTotalRole")
        monkeypatch.setattr(sync_client.b, "AskTotalRole", _tripwire, raising=True)
    yield d
    R._TOTAL_ROLE_CACHE.clear()


# ------------------------------------------------------------------ helpers (duplicated on
# purpose: this module imports nothing from `printedtotal.py` or its tests — spec § 3, two stacks)

def _band(texts):
    """A minimal Band whose lines are one-word lines of `texts`, in order."""
    lines = tuple(Line((Word(t, 10.0, 60.0, 10.0 * i, 10.0 * i + 8.0),), 10.0 * i, 10.0 * i + 8.0)
                 for i, t in enumerate(texts))
    return Band(lines, 0.0, 10.0 * len(texts))


def _pdf(tmp_path, builder, **kw):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl import fixtures
    p = tmp_path / "tr.pdf"
    getattr(fixtures, builder)(str(p), **kw)
    return str(p)


def _operand_from_bands(bands, table_idx, total_idx):
    """An `Operand` built off real `page_bands` geometry: `table_idx`'s band as the intact table,
    and `total_idx`'s single-word line as the (soon-to-be-carved) total — its box read directly from
    the word, as `holon.emit_printed_total` would read it off `tab:hasBBox`."""
    tb = bands[table_idx]
    total_line = bands[total_idx].lines[0]
    w = total_line.words[0]
    box = (w.x0, bands[total_idx].top, w.x1, bands[total_idx].bottom)
    return R.Operand(table_band=tb, total_text=w.text, total_box=box)


# ------------------------------------------------------------------ the reading and its key

def test_the_reading_is_a_closed_enum_with_no_other_field():
    assert R.TotalRoleReading(answer="total_of_totals").answer == "total_of_totals"
    with pytest.raises(ValueError):
        R.TotalRoleReading(answer="probably")
    import dataclasses
    assert [f.name for f in dataclasses.fields(R.TotalRoleReading)] == ["answer"]


def test_the_key_is_text_facts_only_and_namespaced_differently_from_printed_total():
    from iladub.etkl import printedtotal as P
    k = R.question_key("1,951,264", "L0: a\nL1: 1,951,264")
    assert R.question_key("1,951,264", "L0: a\nL1: 1,951,264") == k
    assert R.question_key("1,951,265", "L0: a\nL1: 1,951,264") != k
    assert R.question_key("1,951,264", "L0: b\nL1: 1,951,264") != k
    assert k != hashlib.sha256("1,951,264\nL0: a\nL1: 1,951,264".encode()).hexdigest()
    # Namespaced against the sibling question for the SAME (value, listing):
    assert k != P.question_key("1,951,264", "L0: a\nL1: 1,951,264")
    import inspect
    assert list(inspect.signature(R.question_key).parameters) == ["value", "listing"]


# ------------------------------------------------------------------ D4: the listing

def test_listing_lists_each_operand_table_then_its_cell_text_then_the_candidates_own_prior_lines():
    """D4: operand table-band lines, then the operand's own total text (its line was carved away
    and has no `Line` to render), then the candidate's OWN band's earlier lines (line_no = 1 lists
    its band's line 0 before the candidate), then the candidate line."""
    table_band = _band(["Header"])
    op = R.Operand(table_band=table_band, total_text="1,200", total_box=(0.0, 0.0, 10.0, 10.0))
    band = _band(["Note: subject to change", "2,700"])
    line_no = 1
    line = band.lines[line_no]
    listing = R.listing_of([op], band, line_no, line)
    assert listing.splitlines() == [
        "L0: Header",
        "L1: 1,200",
        "L2: Note: subject to change",
        "L3: 2,700",
    ]


def test_review_focus_5_an_operand_table_word_change_moves_the_key():
    """Changing one word of one operand table band's lines changes the key — the listing covers
    every operand table band, so a recording moves when any word of any operand table moves."""
    table_band = _band(["Header"])
    op = R.Operand(table_band=table_band, total_text="1,200", total_box=(0.0, 0.0, 10.0, 10.0))
    band = _band(["2,700"])
    line = band.lines[0]
    listing = R.listing_of([op], band, 0, line)
    key = R.question_key("1,200", listing)

    other_table_band = _band(["HEADER"])
    other_op = R.Operand(table_band=other_table_band, total_text="1,200",
                         total_box=(0.0, 0.0, 10.0, 10.0))
    other_listing = R.listing_of([other_op], band, 0, line)
    assert R.question_key("1,200", other_listing) != key


# ------------------------------------------------------------------ crop_box (N8's derived_box)

def test_crop_box_matches_the_derived_box_rule_and_clamps_to_the_page():
    """top = min operand table-band `top` − 4; bottom = max of operand box bottoms and the
    candidate's bottom, + 4; x = the extreme of every operand table-band word, every operand's
    `total_box`, and every candidate word, ± 4; all clamped to the page."""
    tb1 = Band((Line((Word("10,200", 10.0, 30.0, 50.0, 58.0),), 50.0, 58.0),), 50.0, 58.0)
    tb2 = Band((Line((Word("4,000", 60.0, 90.0, 80.0, 88.0),), 80.0, 88.0),), 80.0, 88.0)
    op1 = R.Operand(table_band=tb1, total_text="10,200", total_box=(20.0, 58.0, 40.0, 66.0))
    op2 = R.Operand(table_band=tb2, total_text="4,000", total_box=(70.0, 88.0, 100.0, 96.0))
    cand = Line((Word("14,200", 120.0, 150.0, 150.0, 158.0),), 150.0, 158.0)
    # Unclamped: left = 10-4=6, top = 50-4=46, right = 150+4=154, bottom = 158+4=162.
    # A small page forces the right/bottom clamp while left/top stay the plain arithmetic.
    box = R.crop_box(100.0, 100.0, [op1, op2], cand)
    assert box == (6.0, 46.0, 100.0, 100.0)


# ------------------------------------------------------------------ render_crop (N8's rendering)

def test_render_crop_returns_png_bytes(tmp_path):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    line = bands[4].lines[0]
    word = line.words[0]
    png = R.render_crop(pdf, 0, (0.0, 0.0, 400.0, 700.0), word)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


# ------------------------------------------------------------------ recorded replay

def test_a_recorded_reading_replays_and_an_out_of_set_one_is_no_claim(
        tmp_path, _fresh_cache_and_readings):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]
    listing = R.listing_of([op], band, line_no, line)
    key = R.question_key("7,800", listing)
    path = _fresh_cache_and_readings / f"{key}.json"
    path.write_text(json.dumps({"answer": "total_of_totals"}), encoding="utf-8")
    got = R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800", R.default_reader())
    assert got == R.TotalRoleReading(answer="total_of_totals")
    path.write_text(json.dumps({"answer": "maybe"}), encoding="utf-8")
    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800",
                            R.default_reader()) is None


def test_no_recording_and_not_live_is_no_claim_and_never_builds_the_live_reader(
        tmp_path, monkeypatch):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]

    def _boom(*a, **k):
        raise AssertionError("the live reader was constructed")
    monkeypatch.setattr(R, "BamlTotalRoleReader", _boom)
    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800",
                            R.default_reader()) is None


# ------------------------------------------------------------------ ask_total_role's four failure kinds

def test_ask_total_role_returns_none_with_no_reader(tmp_path):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]
    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800", None) is None


def test_ask_total_role_returns_none_when_the_reader_raises(tmp_path):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]

    class _RaisingReader:
        def ask(self, crop_png, value, listing):
            raise RuntimeError("boom")

    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800", _RaisingReader()) is None


def test_ask_total_role_returns_none_when_the_reader_returns_none(tmp_path):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]
    reader = R.FakeTotalRoleReader(reading=None)
    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800", reader) is None


def test_ask_total_role_returns_none_when_the_reader_returns_the_wrong_type(tmp_path):
    from iladub.etkl.compile import page_bands
    pdf = _pdf(tmp_path, "printed_total_pdf")
    bands = page_bands(pdf, 0)
    op = _operand_from_bands(bands, 2, 3)
    band, line_no = bands[4], 0
    line = band.lines[line_no]

    class _WrongTypeReader:
        def ask(self, crop_png, value, listing):
            return "total_of_totals"

    assert R.ask_total_role(pdf, 0, [op], band, line_no, line, "7,800", _WrongTypeReader()) is None
