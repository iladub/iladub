import os
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF
from iladub.extract_baml import OfferExtraction, CodedConcept
from iladub.to_rdf import to_rdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")
ILADUB = Namespace("https://w3id.org/iladub#")


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


from types import SimpleNamespace
from iladub.to_rdf import ground_typed
from rdflib.namespace import RDF as _RDF

HEART = os.path.join(TXD, "heart-timeline.ttl")


def _heart():
    return Graph().parse(HEART, format="turtle")


def test_ground_typed_free_literal_field_is_asserted():
    # tx:recipientReady (M5) has no admissibleScheme -> asserted as a free literal
    typed = SimpleNamespace(recipientReady=CodedConcept("READY", "readiness: READY", 0.9))
    eg = ground_typed(typed, _heart(), TX["ctx-m5"], _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in eg.graph


def test_ground_typed_unresolved_scheme_field_becomes_proposition():
    # ctx-m4: organ has admissibleScheme; "Zebra" does not resolve -> proposition; abo "O" resolves
    typed = SimpleNamespace(organ=CodedConcept("Zebra", "organ: Zebra", 0.3),
                            aboGroup=CodedConcept("O", "blood group O", 0.9))
    eg = ground_typed(typed, _heart(), TX["ctx-m4"], _terms(), TX["offer"])
    assert (TX["offer"], TX.aboGroup, Literal("O")) in eg.graph
    assert len(list(eg.propositions.subjects(_RDF.type, ILADUB.CandidateConcept))) == 1
