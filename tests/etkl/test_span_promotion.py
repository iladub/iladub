from rdflib import Graph, RDF, RDFS, URIRef, Namespace
from iladub.etkl.promote import emit_span_promotion
from iladub.etkl.propose import SpanProposal

ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_emit_span_promotion_writes_candidate_and_decision():
    g = Graph()
    region = URIRef("urn:doc#htable0")
    proposal = SpanProposal("standalone", 0.82, "the flank reads as its own column")
    pd = emit_span_promotion(g, region, "Current Visit", 4, "standalone", proposal)

    # a proposition CandidateConcept exists, reviewed by the returned PromotionDecision
    cands = list(g.subjects(RDF.type, ILADUB.CandidateConcept))
    assert len(cands) == 1
    assert (pd, RDF.type, ILADUB.PromotionDecision) in g
    assert (pd, ILADUB.reviews, cands[0]) in g
    assert (cands[0], ILADUB.status, ILADUB.proposed) in g
    # rationale records the tie + choice (auditable proposition, not an assertion)
    rat = str(g.value(pd, DEC.rationale))
    assert "standalone" in rat and "tied" in rat.lower()
    # provenance links back to the region (§6 provenance-to-the-page chain)
    assert (pd, DEC.consideredEvidence, region) in g
