import os
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph, URIRef, RDF
from pyshacl import validate
from tests.etkl.fixtures import simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.holon import (assert_record_region, escalate_region,
                               TAB, ILADUB, PROV, DEC)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONT = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")
SH = os.path.join(ROOT, "vocab", "shapes")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SH, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SH, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _record_region(tmp_path):
    p = tmp_path / "x.pdf"; simple_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[1]
    return classify(band)


def test_assert_produces_conforming_holon(tmp_path):
    g = Graph()
    n = assert_record_region(g, _record_region(tmp_path),
                             URIRef("urn:t"), URIRef("urn:doc"), page=0)
    assert n == 9   # 3 data rows x 3 columns
    assert (URIRef("urn:t"), None, None) in g
    conforms, _, text = validate(g, shacl_graph=_shapes(),
                                 ont_graph=Graph().parse(ONT, format="turtle"),
                                 inference="rdfs", advanced=True)
    assert conforms, text


def test_asserted_entry_has_text_and_bbox(tmp_path):
    g = Graph()
    assert_record_region(g, _record_region(tmp_path),
                         URIRef("urn:t"), URIRef("urn:doc"), page=0)
    texts = {str(o) for o in g.objects(None, TAB.cellText)}
    assert "Hemoglobin" in texts and "13.2" in texts
    assert any(True for _ in g.triples((None, TAB.hasBBox, None)))
    assert any(True for _ in g.triples((None, PROV.wasDerivedFrom, None)))


def test_escalate_produces_candidate():
    g = Graph()
    escalate_region(g, URIRef("urn:reg"), URIRef("urn:doc"),
                    ascii_text="Current Visit  Prior Visit",
                    reason="KIND_NOT_SUPPORTED", anchor=TAB.HierarchicalTable,
                    confidence=0.4)
    assert (URIRef("urn:reg"), RDF.type, ILADUB.CandidateConcept) in g
    assert any(True for _ in g.triples((None, ILADUB.surfaceText, None)))
    assert any(g.triples((URIRef("urn:reg"), ILADUB.suggestedAnchor, None)))
    from iladub.etkl.holon import DEC
    assert any(g.triples((URIRef("urn:reg"), DEC.confidence, None)))
    assert any(g.triples((URIRef("urn:reg"), DEC.rationale, None)))
    assert any(g.triples((URIRef("urn:reg"), PROV.wasDerivedFrom, None)))


def test_header_labels_are_carried(tmp_path):
    g = Graph()
    assert_record_region(g, _record_region(tmp_path), URIRef("urn:t"), URIRef("urn:doc"), page=0)
    label_texts = {str(o) for s in g.subjects(RDF.type, TAB.LabelCell)
                   for o in g.objects(s, TAB.cellText)}
    assert {"Analyte", "Value", "Unit"} <= label_texts, label_texts
    # each header node links to its label
    assert any(g.triples((None, TAB.hasLabel, None)))


def test_straddling_cell_is_proposed_not_asserted():
    """A data cell whose ink crosses a column gutter must be emitted as an
    iladub:CandidateConcept (ROUND_TRIP_FAIL), never silently dropped or
    asserted as a TAB:EntryCell.
    """
    from iladub.etkl.regions import Cell, ClassifiedRegion, RegionKind
    from iladub.etkl.grid import LeafGrid
    from iladub.etkl.geometry import Word
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line

    # boundaries: two columns [0..100) and [100..200)
    boundaries = (0.0, 100.0, 200.0)
    grid = LeafGrid(boundaries=boundaries, ncols=2, pitch=100.0, confidence=1.0)

    # header row: one clean word per column
    hw0 = Word("ColA", 10.0, 60.0, 0.0, 10.0, page=0)
    hw1 = Word("ColB", 110.0, 160.0, 0.0, 10.0, page=0)
    hdr_line = Line(words=(hw0, hw1), top=0.0, bottom=10.0)

    # data row: col-0 clean, col-1 straddles the 100.0 boundary (x0=80 < 100)
    dw0 = Word("CleanVal", 10.0, 60.0, 20.0, 30.0, page=0)
    dw1 = Word("STRADDLE", 80.0, 140.0, 20.0, 30.0, page=0)
    data_line = Line(words=(dw0, dw1), top=20.0, bottom=30.0)

    band = Band(lines=(hdr_line, data_line), top=0.0, bottom=30.0)

    # cells built as assign_cells would produce them
    header_cell0 = Cell(row=0, col=0, words=(hw0,))
    header_cell1 = Cell(row=0, col=1, words=(hw1,))
    clean_cell   = Cell(row=1, col=0, words=(dw0,))
    straddle_cell = Cell(row=1, col=1, words=(dw1,))

    region = ClassifiedRegion(
        kind=RegionKind.RECORD_TABLE,
        band=band,
        grid=grid,
        cells=(header_cell0, header_cell1, clean_cell, straddle_cell),
        reason="flat single-level header",
    )

    g = Graph()
    n_asserted = assert_record_region(
        g, region, URIRef("urn:straddle-t"), URIRef("urn:doc"), page=1
    )

    # the straddling data cell is proposed, not asserted
    assert (None, RDF.type, ILADUB.CandidateConcept) in g
    rationales = {str(o) for o in g.objects(None, DEC.rationale)}
    assert "ROUND_TRIP_FAIL" in rationales

    # and it is NOT emitted as an EntryCell fact
    entry_texts = {str(o) for s in g.subjects(RDF.type, TAB.EntryCell)
                   for o in g.objects(s, TAB.cellText)}
    assert "STRADDLE" not in entry_texts

    # the clean data cell IS asserted; total asserted = 1 (not 2)
    assert n_asserted == 1
    assert "CleanVal" in entry_texts


# ---------------------------------------------------------------------------
# assert_transposed_region
# ---------------------------------------------------------------------------
from rdflib import Literal
from iladub.etkl.geometry import Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.regions import Cell, ClassifiedRegion, RegionKind
from iladub.etkl.holon import assert_transposed_region, TAB, ILADUB, DEC, PROV


def _word(text, x0, x1, top=100.0, bottom=110.0):
    return Word(text=text, x0=x0, x1=x1, top=top, bottom=bottom, page=0)


def _cell(row, col, text, x0, x1, top):
    return Cell(row=row, col=col, words=(_word(text, x0, x1, top, top + 10.0),))


def _transposed_region(straddle=False):
    # 3 physical cols (Field | rec1 | rec2), boundaries at 60/220/380/540.
    grid = LeafGrid(boundaries=(60.0, 220.0, 380.0, 540.0), ncols=3, pitch=160.0, confidence=1.0)
    cells = [
        _cell(0, 0, "Field", 60.0, 110.0, 100.0),
        _cell(0, 1, "Alice", 220.0, 270.0, 100.0),
        _cell(0, 2, "Bob", 380.0, 420.0, 100.0),
        _cell(1, 0, "Age", 60.0, 100.0, 120.0),
        _cell(1, 1, "30", 220.0, 250.0, 120.0),
        _cell(1, 2, "25", 380.0, 410.0, 120.0),
        _cell(2, 0, "City", 60.0, 110.0, 140.0),
        # straddle=True makes this value cross the 380 gutter (x1=420 > 380)
        _cell(2, 1, "NYC", 350.0 if straddle else 220.0, 420.0 if straddle else 270.0, 140.0),
        _cell(2, 2, "LA", 380.0, 410.0, 140.0),
    ]
    return ClassifiedRegion(RegionKind.RECORD_TABLE, None, grid, tuple(cells), "test")


def test_transposed_maker_builds_record_table():
    g = Graph()
    t = URIRef("https://example.org/t")
    n = assert_transposed_region(g, _transposed_region(), t, URIRef("https://example.org/doc"), 0)
    assert (t, RDF.type, TAB.RecordTable) in g
    assert (t, TAB.sourceOrientation, Literal("transposed")) in g
    # header labels come from physical column 0 (read down): Field, Age, City
    labels = {str(o) for s in g.subjects(RDF.type, TAB.LabelCell)
              for o in g.objects(s, TAB.cellText)}
    assert {"Field", "Age", "City"} <= labels
    # 3 logical cols, 2 logical rows (records), 6 entry cells
    assert len(list(g.subjects(RDF.type, TAB.LeafColumn))) == 3
    assert len(list(g.subjects(RDF.type, TAB.LeafRow))) == 2
    assert n == 6


def test_transposed_provenance_is_physical():
    g = Graph()
    t = URIRef("https://example.org/t")
    assert_transposed_region(g, _transposed_region(), t, URIRef("https://example.org/doc"), 0)
    # the entry carrying "30" must keep the PHYSICAL bbox of the "30" word (x0=220),
    # not a flipped coordinate.
    e = next(s for s in g.subjects(RDF.type, TAB.EntryCell)
             if str(next(g.objects(s, TAB.cellText))) == "30")
    bb = next(g.objects(e, TAB.hasBBox))
    assert float(next(g.objects(bb, TAB.x0))) == 220.0
    assert int(next(g.objects(e, TAB.onPage))) == 0


def test_transposed_straddle_escalates_that_cell():
    g = Graph()
    t = URIRef("https://example.org/t")
    n = assert_transposed_region(g, _transposed_region(straddle=True), t,
                                 URIRef("https://example.org/doc"), 0)
    # the straddling value cell is NOT asserted; it becomes a ROUND_TRIP_FAIL proposition
    assert n == 5
    rationales = {str(o) for s in g.subjects(RDF.type, ILADUB.CandidateConcept)
                  for o in g.objects(s, DEC.rationale)}
    assert "ROUND_TRIP_FAIL" in rationales


def test_row_hier_maker_builds_row_tree(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.rowheaders import classify_row_hier
    from iladub.etkl.holon import assert_row_hier_region, TAB
    from rdflib import Graph, URIRef, RDF, Literal

    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    rreg = classify_row_hier(band)
    g = Graph(); t = URIRef("https://example.org/t")
    n = assert_row_hier_region(g, rreg, band, t, URIRef("https://example.org/doc"), 0)

    assert (t, RDF.type, TAB.HierarchicalTable) in g
    assert len(list(g.objects(t, TAB.hasLeafColumn))) == 1          # Value only (Design A)
    assert len(list(g.objects(t, TAB.hasLeafRow))) == 5
    assert n == 5                                                   # 5 entries (Value x 5 rows)
    # row-header tree: North covers 3 rows, South covers 2
    def covers(text):
        h = next(s for s in g.subjects(RDF.type, TAB.HeaderNode)
                 if (s, TAB.hasLabel, None) in g
                 and str(next(g.objects(next(g.objects(s, TAB.hasLabel)), TAB.cellText))) == text)
        return len(list(g.objects(h, TAB.coversRow)))
    assert covers("North") == 3
    assert covers("South") == 2


def test_row_hier_provenance_is_physical(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.rowheaders import classify_row_hier
    from iladub.etkl.holon import assert_row_hier_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    words = extract_words(str(p))
    north = next(w for w in words if w.text == "North")
    band = detect_bands(text_lines(words))[-1]
    rreg = classify_row_hier(band)
    g = Graph(); t = URIRef("https://example.org/t")
    assert_row_hier_region(g, rreg, band, t, URIRef("https://example.org/doc"), 0)
    # the 'North' row-header LabelCell keeps the physical bbox of the 'North' word
    lc = next(s for s in g.subjects(RDF.type, TAB.LabelCell)
              if str(next(g.objects(s, TAB.cellText))) == "North")
    bb = next(g.objects(lc, TAB.hasBBox))
    assert abs(float(next(g.objects(bb, TAB.x0))) - north.x0) < 0.01


def test_column_header_label_cell_has_provenance(tmp_path):
    """Fix #1: data-column header LabelCell must carry tab:onPage + tab:hasBBox
    with physical coordinates from the header word (provenance-to-the-page §6).
    """
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.rowheaders import classify_row_hier
    from iladub.etkl.holon import assert_row_hier_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    words = extract_words(str(p))
    value_word = next(w for w in words if w.text == "Value")
    band = detect_bands(text_lines(words))[-1]
    rreg = classify_row_hier(band)
    g = Graph(); t = URIRef("https://example.org/t")
    assert_row_hier_region(g, rreg, band, t, URIRef("https://example.org/doc"), 0)

    # the 'Value' data-column header LabelCell must have onPage and hasBBox
    lc = next(s for s in g.subjects(RDF.type, TAB.LabelCell)
              if str(next(g.objects(s, TAB.cellText))) == "Value")
    # tab:onPage must be present
    pages = list(g.objects(lc, TAB.onPage))
    assert pages, "LabelCell 'Value' is missing tab:onPage"
    # tab:hasBBox must be present and x0 must match the physical word's x0
    bboxes = list(g.objects(lc, TAB.hasBBox))
    assert bboxes, "LabelCell 'Value' is missing tab:hasBBox"
    bb = bboxes[0]
    x0_vals = list(g.objects(bb, TAB.x0))
    assert x0_vals, "BBox node is missing tab:x0"
    assert abs(float(x0_vals[0]) - value_word.x0) < 0.01, (
        f"LabelCell 'Value' x0 {float(x0_vals[0])} != word x0 {value_word.x0}"
    )


def test_matrix_maker_builds_both_axes(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.matrix import classify_matrix
    from iladub.etkl.holon import assert_matrix_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    mreg = classify_matrix(band)
    g = Graph(); t = URIRef("https://example.org/t")
    n = assert_matrix_region(g, mreg, band, t, URIRef("https://example.org/doc"), 0)

    assert (t, RDF.type, TAB.HierarchicalTable) in g
    assert len(list(g.objects(t, TAB.hasLeafColumn))) == 6      # data columns only (Design A)
    assert len(list(g.objects(t, TAB.hasLeafRow))) == 2
    assert n == 12                                              # 6 data cols x 2 rows
    assert (None, TAB.coversColumn, None) in g                  # column tree
    assert (None, TAB.coversRow, None) in g                     # row tree
    # a column-group header 'Q1' covers 3 leaf columns
    q1 = next(s for s in g.subjects(RDF.type, TAB.HeaderNode)
              if (s, TAB.hasLabel, None) in g
              and str(next(g.objects(next(g.objects(s, TAB.hasLabel)), TAB.cellText))) == "Q1")
    assert len(list(g.objects(q1, TAB.coversColumn))) == 3


def test_matrix_provenance_is_physical(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.matrix import classify_matrix
    from iladub.etkl.holon import assert_matrix_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    words = extract_words(str(p))
    north = next(w for w in words if w.text == "North")
    band = detect_bands(text_lines(words))[-1]
    mreg = classify_matrix(band)
    g = Graph(); t = URIRef("https://example.org/t")
    assert_matrix_region(g, mreg, band, t, URIRef("https://example.org/doc"), 0)
    lc = next(s for s in g.subjects(RDF.type, TAB.LabelCell)
              if str(next(g.objects(s, TAB.cellText))) == "North")
    bb = next(g.objects(lc, TAB.hasBBox))
    assert abs(float(next(g.objects(bb, TAB.x0))) - north.x0) < 0.01
