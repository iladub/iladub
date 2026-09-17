"""[[R249]] — the grounding pre-filter: a concept whose value NO contract field's oracle admits is
quarantined by rule, and the proposer is never asked (review `2026-09-17-neural-worker-spec-review.md`).

The transplant contract is the fixture: `tx:ejectionFraction` carries a decimal 0..100 value
constraint, so "55" is admissible there and "55%" is admissible nowhere (it is no decimal, and
no scheme carries it as a prefLabel)."""
from rdflib import Graph, URIRef
from iladub.ground import (ILADUB, SurfaceConcept, ground_concept, load_contract,
                           _NO_ADMISSIBLE_FIELD_RULE)
from iladub.propose_ground import GroundingProposal

GIST = "https://w3id.org/semanticarts/ns/ontology/gist/Category"


def _fixture():
    return (load_contract("examples/transplant/offer-contract.ttl"),
            Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle"),
            Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle"))


class _Counting:
    def __init__(self):
        self.asked = []

    def propose_grounding(self, concept, fields, page_context=None):
        self.asked.append(concept.value)
        return GroundingProposal(None, GIST, 0.2, "abstain", "urn:iladub:suggester/test-counting")


def _ground(value):
    contract, terms, shapes = _fixture()
    g, proposer = Graph(), _Counting()
    status = ground_concept(SurfaceConcept("mystery", value, "r3"), contract,
                            URIRef("urn:test:offer1"), proposer, terms, shapes, g)
    return status, proposer.asked, g


def test_a_value_no_field_admits_never_reaches_the_proposer():
    status, asked, g = _ground("55%")
    assert status == "proposed"
    assert asked == [], "the proposer was asked a question no answer could change"
    cand = next(g.subjects(ILADUB.status, ILADUB.proposed))
    assert g.value(cand, ILADUB.suggestedBy) == URIRef(_NO_ADMISSIBLE_FIELD_RULE)


def test_an_admissible_value_still_reaches_the_proposer():
    """The control: without it, a filter that skipped EVERY ask would pass the test above."""
    status, asked, g = _ground("55")
    assert asked == ["55"]
    cand = next(g.subjects(ILADUB.status, ILADUB.proposed))
    assert g.value(cand, ILADUB.suggestedBy) == URIRef("urn:iladub:suggester/test-counting")
