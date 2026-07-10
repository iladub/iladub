from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.propose import Proposal, FakeProposer
from iladub.etkl.reshape import certify_with_proposals
from tests.etkl.test_certify_proposals import _nameless_pivot
TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_promotion_records_the_name_as_a_proposition():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "Q1..Q4 are quarters")))
    assert out.normalized_base is not None and len(out.promotions) == 1
    pd = out.promotions[0]
    assert (pd, RDF.type, ILADUB.PromotionDecision) in g
    cand = g.value(pd, ILADUB.reviews)
    assert cand is not None and str(g.value(cand, RDF.type)) == str(ILADUB.CandidateConcept)
    assert str(g.value(cand, __import__("rdflib").RDFS.label)) == "Quarter"
    assert float(g.value(cand, ILADUB.confidence)) == 0.9
    assert g.value(cand, ILADUB.suggestedBy) is not None
    assert g.value(pd, DEC.decidedBy) is not None
    assert g.value(pd, DEC.produced) == out.normalized_base
    assert "proposition" in str(g.value(pd, DEC.rationale)).lower()
    # the admitted name links to its promotion via the rangeless tab link
    assert (None, TAB.namePromotedBy, pd) in g
