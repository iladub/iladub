"""A clock time is a cell datatype. A blank glyph that rescues a header row is still open (R299).

Raised by the held-out timetable `caltrain-weekend-timetable` (2026-10-07): every data cell
('6:51a') typed tab:Text, so the grid had no measure column and `derive_data_grid` refused it
(G1b, tab:NonDegeneracy). Typing the times exposed a second seam: the title line
"Northbound – WEEKEND SERVICE …" carries an en dash, a tab:nilSpelling, in one measure column,
and the every-measure refusal counted that blank as AGREEMENT, so the title was admitted as
the grid's first row and the "Train No." boxhead fell outside the header block. That second seam
is open (R299) and pinned below as a strict xfail.
"""
from __future__ import annotations

import pytest

from iladub.etkl.celltype import TAB, _cell_datatype, is_clock_time


@pytest.mark.parametrize("text", ["6:51a", "12:26p", "11:05 pm", "9:05 p.m.", "10:00AM",
                                  "07:30", "23:59", "00:00"])
def test_a_time_of_day_is_a_clock_time(text):
    assert is_clock_time(text)
    assert _cell_datatype(text) == TAB.ClockTime


@pytest.mark.parametrize("text", [
    "4:11",       # unpadded, no meridiem: a ratio, a score, a years:months age
    "13:05pm",    # a 12-hour time has no hour 13
    "24:00", "7:60", "1:2",
    "10:00:00",   # a duration column (graincorp-stem) is not this datatype
    "601",
])
def test_an_ambiguous_or_malformed_spelling_is_not(text):
    assert not is_clock_time(text)


def test_the_ontology_declares_it():
    from rdflib import RDF
    from iladub.etkl.celltype import _ONT
    assert (TAB.ClockTime, RDF.type, TAB.CellDatatype) in _ONT


def _timetable_page(tmp_path):
    """Stations down, trains across. A direction heading above the train-number row puts one
    nil glyph (an en dash) in a time column and words in the other two."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "timetable.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    xs = (60, 200, 260, 320)

    def row(y, cells):
        for x, t in zip(xs, cells):
            if t:
                c.drawString(x, y, t)

    row(780, ("Northbound", "–", "SERVICE", "CITY"))       # heading -> metadata
    row(750, ("Train No.", "101", "103", "105"))                # boxhead -> header block
    for i, cells in enumerate([("Alpha", "6:51a", "7:51a", "8:51a"),
                               ("Beta", "6:56a", "7:26a", "7:56a"),
                               ("Gamma", "7:03a", "7:33a", "8:03a"),
                               ("Delta", "7:08a", "", "8:08a")]):
        row(720 - i * 20, cells)
    c.save()
    return path


def test_a_timetable_derives_a_grid_of_clock_times(tmp_path):
    pytest.importorskip("reportlab")
    from iladub.etkl.datagrid import derive_data_grid
    g = derive_data_grid(_timetable_page(tmp_path), 0)
    assert g is not None, "a grid of clock times has measure columns"
    assert [c.family for c in g.columns] == ["Text", "ClockTime", "ClockTime", "ClockTime"]
    assert {2, 3, 4, 5} <= set(g.rows), "every station row is a data row"


@pytest.mark.xfail(strict=True, reason=(
    "R299: the heading's en dash (a tab:nilSpelling) rescues it from the every-measure refusal, "
    "and the heading relaxes its own columns' refusal (it is in `addressable`). Counting a blank "
    "as a wildcard fixes this page and refuses graincorp-stem p1's six shutdown rows "
    "(77 -> 71), so that remedy was refuted on 2026-10-07."))
def test_a_nil_glyph_does_not_admit_the_heading(tmp_path):
    pytest.importorskip("reportlab")
    from iladub.etkl.boxhead import header_block
    from iladub.etkl.datagrid import derive_data_grid
    from iladub.etkl.geometry import extract_words, text_lines
    path = _timetable_page(tmp_path)
    g = derive_data_grid(path, 0)
    assert g.refusals.get(0) == "HeterogeneousColumn/every-measure"
    lines = [ln for ln in sorted(text_lines(extract_words(path, 0)), key=lambda ln: ln.top)
             if ln.words]
    assert header_block(lines, g) == (0, 1), "the train-number row heads the grid"
