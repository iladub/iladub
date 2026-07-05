import os
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph, URIRef, RDF
from pyshacl import validate
from tests.etkl.fixtures import simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.holon import (assert_record_region, escalate_region,
                               TAB, ILADUB, PROV)

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
