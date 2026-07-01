import os
import pytest
from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.databook import read_databook
from iladub.m4 import compile_offer_databook
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")

DEC = Namespace("https://w3id.org/iladub/dec#")
TX = Namespace("https://example.org/transplant#")
ILADUB = Namespace("https://w3id.org/iladub#")

def test_raw_offer_databook_loads():
    db = read_databook(os.path.join(TXD, "offer.databook.md"))
    assert db.frontmatter["id"].endswith("offer-2026-0091")
    assert db.frontmatter["source"]["reference"] == "ET-2026-0091"
    assert "Organ offered: HEART" in db.prose

def _patch(monkeypatch):
    cc = lambda v, q, c=0.9: CodedConcept(value=v, source_quote=q, confidence=c)
    monkeypatch.setattr(sync_client.b, "ExtractDonorClinical",
        lambda doc: DonorClinical(organ=cc("Heart", "Organ offered: HEART"),
                                  ejectionFraction=cc("60", "LVEF 60%"),
                                  causeOfDeath=cc("takotsubo-pattern abnormality",
                                                  "transient takotsubo-pattern wall-motion abnormality"),
                                  sizeMetric=cc("78 kg", "Donor size: 78 kg")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractImmunology",
        lambda doc: Immunology(aboGroup=cc("O", "Blood group: O"),
                               hlaTyping=cc("A2, B7, DR15", "HLA: A2, B7, DR15"),
                               serology=cc("HIV negative", "HIV negative")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractLogistics",
        lambda doc: Logistics(projectedTransportMinutes=cc("95", "estimated transport 95 minutes")),
        raising=True)

def test_compile_offer_databook_emits_clean_holon(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = tmp_path / "offer.clean.databook.md"
    res = compile_offer_databook(os.path.join(TXD, "offer.databook.md"), str(out))
    assert res.decision.recommendation == "accept"

    db = read_databook(str(out))
    ids = {b.id for b in db.blocks}
    assert {"asserted", "propositions", "decision"} <= ids

    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert conforms

    props = db.graph("propositions")
    assert len(list(props.subjects(RDF.type, ILADUB.CandidateConcept))) == 1

    dec = db.graph("decision")
    assert (TX["m4-decision"], DEC.chosen, TX["opt-accept"]) in dec

    assert "process" in db.frontmatter
    inputs = db.frontmatter["process"]["inputs"]
    assert len(inputs) == 4
    assert {"primary", "contract", "knowledge", "constraint"} <= {i["role"] for i in inputs}


def test_curated_clean_conformant_passes_shacl():
    db = read_databook(os.path.join(TXD, "offer.clean.databook.md"))
    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert conforms
    from iladub.databook import validate_frontmatter
    assert validate_frontmatter(db.frontmatter, require_process=True) == []


def test_curated_clean_leak_fails_shacl():
    db = read_databook(os.path.join(TXD, "offer.clean.leak.databook.md"))
    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert not conforms


def test_frontmatter_leak_detected():
    from iladub.databook import validate_frontmatter
    db = read_databook(os.path.join(TXD, "offer.clean.leak.databook.md"))
    fm = dict(db.frontmatter)
    fm.pop("process")
    assert validate_frontmatter(fm, require_process=True)
