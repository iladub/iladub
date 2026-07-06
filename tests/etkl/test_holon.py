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
