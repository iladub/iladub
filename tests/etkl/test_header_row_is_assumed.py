"""test_header_row_is_assumed — R166's class, on a synthetic band, in CI.

Twelve corpus bands assert a flat tab:RecordTable whose label row is not a header
(spec docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md § 2). Both
tests here run without corpus/ ([[R173]]): the first is a DETECTOR that pins the
defect as it stands today and turns RED the moment a header-evidence gate lands —
at which point it is the fixer's to invert, exactly as R167's closure inverted
test_one_band_matrix_spike's em-dash pin. The second pins the deduction that closes
one of the two candidate remedies for good.
"""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rdflib import RDF

from iladub.etkl import extract_words, text_lines, detect_bands, compile_tables
from iladub.etkl.regions import classify, RegionKind
from iladub.etkl.holon import TAB

PAGE_H = letter[1]
COLS = (72.0, 240.0, 400.0)


def _rows_pdf(path, rows, title="Population by canton"):
    """A title band, then `rows` laid out on a fixed 3-column grid."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    c.drawString(72.0, PAGE_H - 72.0, title)
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        for x, cell in zip(COLS, row):
            if cell:
                c.drawString(x, y0 - i * 18.0, cell)
    c.save()


def _band(path):
    return detect_bands(text_lines(extract_words(str(path))))[1]


# The band has NO header line at all: four data rows of identical shape, the shape
# bfs p6 band 4 has on the page (a region subtotal followed by its cantons).
_HEADERLESS = [
    ("Vaud", "845870", "184231"),
    ("Valais", "365844", "70577"),
    ("Geneve", "524410", "111028"),
    ("Berne", "1063533", "203904"),
]


def test_a_headerless_band_asserts_its_first_data_row_as_the_column_header(tmp_path):
    """R166's DETECTOR. Nothing in the band says 'Vaud 845870 184231' is a header —
    and it is asserted as one, its two values becoming tab:LabelCells rather than
    entries. RED when the class is fixed; invert it then, do not delete it."""
    p = tmp_path / "headerless.pdf"
    _rows_pdf(p, _HEADERLESS)
    assert classify(_band(p)).kind is RegionKind.RECORD_TABLE

    res = compile_tables(str(p), page_number=0)
    labels = {str(res.graph.value(s, TAB.cellText))
              for s in res.graph.subjects(RDF.type, TAB.LabelCell)}
    assert labels == {"Vaud", "845870", "184231"}, labels


def test_a_flat_record_table_can_never_have_a_blank_corner(tmp_path):
    """Spec § 3(b): tab:RecordTableKind requires one header word per leaf column, so
    the one mark that most plainly evidences a header row — an empty stub corner over
    a populated stub column — puts the band OUT of this branch instead of into it.
    The paired control is the same band with the corner filled."""
    blank = tmp_path / "blank-corner.pdf"
    _rows_pdf(blank, [("", "Value", "Unit")] + [(r[0], r[1], r[2]) for r in _HEADERLESS])
    assert classify(_band(blank)).kind is not RegionKind.RECORD_TABLE

    filled = tmp_path / "filled-corner.pdf"
    _rows_pdf(filled, [("Canton", "Value", "Unit")] + [(r[0], r[1], r[2]) for r in _HEADERLESS])
    assert classify(_band(filled)).kind is RegionKind.RECORD_TABLE
