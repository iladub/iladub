import os
from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.m4 import compile_offer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


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


def test_compile_offer_validates_and_recommends_accept(monkeypatch):
    _patch(monkeypatch)
    res = compile_offer(os.path.join(TXD, "offer.txt"))
    assert res.validation.conforms, res.validation.report_text
    assert res.decision.recommendation == "accept"
    from rdflib.namespace import RDF
    from rdflib import Namespace
    ILADUB = Namespace("https://w3id.org/etkl/iladub#")
    assert len(list(res.extraction_graph.propositions.subjects(RDF.type, ILADUB.CandidateConcept))) == 1


import pytest


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1",
                    reason="set BAML_LIVE=1 to call the real API")
def test_compile_offer_live():
    res = compile_offer(os.path.join(TXD, "offer.txt"))
    assert res.validation.conforms, res.validation.report_text
    assert res.decision.recommendation in {"accept", "decline"}
