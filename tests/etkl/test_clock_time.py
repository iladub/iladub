"""A clock time is a cell datatype. A blank glyph that rescues a header row is still open (R299).

Raised by the held-out timetable `caltrain-weekend-timetable` (2026-10-07): every data cell
('6:51a') typed tab:Text, so the grid had no measure column and `derive_data_grid` refused it
(G1b, tab:NonDegeneracy). Typing the times exposed a second seam: the title line
"Northbound – WEEKEND SERVICE …" carries an en dash, a tab:nilSpelling, in one measure column,
and the every-measure refusal counted that blank as AGREEMENT, so the title was admitted as
the grid's first row and the "Train No." boxhead fell outside the header block. That second seam
(R299) is closed: a row may not relax a column's refusal for itself, and a row refused as a
header relaxes nothing.
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


def _timetable_page(tmp_path, extra=()):
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
                               ("Delta", "7:08a", "", "8:08a"), *extra]):
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


def test_a_nil_glyph_does_not_admit_the_heading(tmp_path):
    pytest.importorskip("reportlab")
    from iladub.etkl.boxhead import header_block
    from iladub.etkl.datagrid import derive_data_grid
    from iladub.etkl.geometry import extract_words, text_lines
    path = _timetable_page(tmp_path)
    g = derive_data_grid(path, 0)
    # Not the every-measure universal (the en dash exempts it): the heading clashes with a
    # column family it is no longer allowed to null for itself.
    assert g.refusals.get(0, "").startswith("HeterogeneousColumn/col")
    lines = [ln for ln in sorted(text_lines(extract_words(path, 0)), key=lambda ln: ln.top)
             if ln.words]
    assert header_block(lines, g) == (0, 1), "the train-number row heads the grid"


def _grid(tmp_path, extra):
    pytest.importorskip("reportlab")
    from iladub.etkl.datagrid import derive_data_grid
    return derive_data_grid(_timetable_page(tmp_path, extra), 0)


def test_a_lone_exception_that_agrees_elsewhere_is_kept(tmp_path):
    """cbh p0's vessel row, in miniature: one contradicting cell, and measure cells that agree.
    It has its own evidence of belonging to the grid, so it may relax the column for itself."""
    g = _grid(tmp_path, [("Epsilon", "TBA", "7:45a", "8:15a")])
    assert 6 in g.rows
    assert g.refusals.get(0, "").startswith("HeterogeneousColumn/col"), "the heading is still refused"


def test_rows_that_agree_nowhere_relax_a_column_for_one_another(tmp_path):
    """graincorp-stem p1's shutdown rows, in miniature: the only non-blank measure cell is a word."""
    g = _grid(tmp_path, [("Zeta", "closed", "–", "–"), ("Eta", "closed", "–", "–")])
    assert {6, 7} <= set(g.rows)
    assert g.refusals.get(0, "").startswith("HeterogeneousColumn/col"), "the heading is still refused"


def test_a_lone_row_that_agrees_nowhere_is_refused(tmp_path):
    """The known cost, pinned so it is not rediscovered: one such row has no peer and no agreeing
    cell, so nothing distinguishes it from a heading. It is refused and escalated, never dropped."""
    # The word sits in the column where the heading holds its nil glyph, so no other row nulls
    # that column. (A refused row can still relax a column for OTHERS; the heading would here.)
    g = _grid(tmp_path, [("Zeta", "closed", "–", "–")])
    assert g.refusals.get(6, "").startswith("HeterogeneousColumn/col")


def test_a_lone_time_column_asserts_at_pass_one_and_is_never_repaired(tmp_path):
    """What typing a time changed OUTSIDE the data grid, pinned so it is not rediscovered in CI.

    `multi_section_ruled_pdf(time_only=True)` is ID | time | Client | Volume. While '15:01' typed
    Text the only data column was Volume, the band was a matrix candidate, the matrix did not
    tile, both bands escalated MATRIX_AMBIGUOUS and section repair read two record tables. Typed
    ClockTime, col 1 is a data column with a Text column after it, `stub-data-split.rq` finds no
    contiguous data suffix, and the hierarchical path asserts the band at pass 1. The CELLS are
    the same either way; the table type and the route are not, and four section-repair tests
    relied on the escalation (CI run 38115897575)."""
    from rdflib import RDF

    from iladub.etkl.document import compile_document
    from tests.etkl.fixtures import multi_section_ruled_pdf
    pdf = tmp_path / "multi.pdf"
    truth = multi_section_ruled_pdf(str(pdf), time_only=True)
    rep = compile_document(str(pdf))
    assert rep.repaired_bands == ()
    assert [(r.verdict, r.anchor) for r in rep.pages[0].regions] == [
        ("asserted", str(TAB.HierarchicalTable))] * 2
    drawn = sorted(c for s in truth["sections"] for row in s["rows"] for c in row)
    assert all(_cell_datatype(row[1]) == TAB.ClockTime
               for s in truth["sections"] for row in s["rows"])
    read = sorted(str(t) for e in rep.graph.subjects(RDF.type, TAB.EntryCell)
                  for t in rep.graph.objects(e, TAB.cellText))
    assert [t for t in read if t != "TOTAL" and t not in {s["total"] for s in truth["sections"]}] \
        == drawn
