import os
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF
from iladub.extract_baml import OfferExtraction, CodedConcept
from iladub.to_rdf import to_rdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")
ILADUB = Namespace("https://w3id.org/etkl/iladub#")


def _terms():
    return Graph().parse(os.path.join(TXD, "transplant-terms.ttl"), format="turtle")


def test_groundable_abo_becomes_asserted_literal():
    ext = OfferExtraction(abo_group=CodedConcept("O", "Blood group: O", 0.95))
    eg = to_rdf(ext, _terms())
    assert (TX["offer"], TX.aboGroup, Literal("O")) in eg.graph


def test_unmapped_term_becomes_quarantined_candidate_with_provenance():
    ext = OfferExtraction(
        cause_of_death=CodedConcept("takotsubo-pattern abnormality",
                                    "transient takotsubo-pattern wall-motion abnormality", 0.4))
    eg = to_rdf(ext, _terms())
    candidates = list(eg.propositions.subjects(RDF.type, ILADUB.CandidateConcept))
    assert len(candidates) == 1
    region = eg.propositions.value(candidates[0], ILADUB.fromRegion)
    assert region is not None
    assert "takotsubo" in str(eg.propositions.value(region, ILADUB.surfaceText))
