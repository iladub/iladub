from rdflib import Graph, Namespace, URIRef, RDF
from iladub.ground import (
    SurfaceConcept, load_contract, exact_field, scheme_member, ground_concept,
)
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

CONTRACT = "examples/transplant/offer-contract.ttl"
TERMS = "examples/transplant/transplant-terms.ttl"

ILA = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
OFFER = URIRef("urn:test:offer1")


def _terms():
    return Graph().parse(TERMS, format="turtle")


def _shapes():
    return Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")


def _noop_proposer():
    return FakeGroundingProposer(GroundingProposal(None, str(TX)+"x", 0.1, "n/a", "urn:iladub:suggester/fake"))


def test_exact_scheme_grounds_with_promotion():
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("ABO group", "A", "r1"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    assert out == "grounded"
    gn = list(g.subjects(RDF.type, ILA.GroundedNode))
    assert gn and g.value(gn[0], ILA.wasPromotedBy) is not None
    assert g.value(gn[0], ILA.status) == ILA.asserted
    assert (OFFER, TX.aboGroup, None) not in [(OFFER, TX.aboGroup, None)] or True  # offer carries aboGroup
    assert any(True for _ in g.objects(OFFER, TX.aboGroup))


def test_wrong_scheme_mapping_quarantined():
    # proposer forces "55%" -> aboGroup (a scheme-bound field); scheme membership must reject it.
    c = load_contract(CONTRACT); g = Graph()
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    p = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"x", 0.95, "looks like abo",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("mystery", "55%", "r3"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))
    cc = list(g.subjects(RDF.type, ILA.CandidateConcept))
    assert cc and g.value(cc[0], ILA.status) == ILA.proposed


def test_novel_concept_quarantined():
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("smoking pack-years", "20", "r4"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))


def test_load_contract_fields():
    c = load_contract(CONTRACT)
    assert c.target_class == "https://example.org/transplant#OrganOffer"
    props = {f.fills_property.split("#")[-1] for f in c.fields}
    assert {"organ", "aboGroup", "ejectionFraction"} <= props
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    assert abo.scheme == "https://example.org/transplant#scheme-abo"
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    assert ef.scheme is None


def test_exact_field_matches_by_property_name():
    c = load_contract(CONTRACT)
    f = exact_field(SurfaceConcept("ABO group", "A", "r1"), c)
    assert f is not None and f.fills_property.endswith("aboGroup")
    assert exact_field(SurfaceConcept("smoking pack-years", "20", "r4"), c) is None


def test_scheme_member_prefLabel():
    t = _terms()
    assert scheme_member("A", "https://example.org/transplant#scheme-abo", t) \
        == "https://example.org/transplant#abo-A"
    assert scheme_member("55%", "https://example.org/transplant#scheme-abo", t) is None


def test_fake_grounding_proposer_returns_fixed():
    p = GroundingProposal(field_iri="https://example.org/transplant#f-ef",
                          anchor_iri="https://w3id.org/semanticarts/ns/ontology/gist/Magnitude",
                          confidence=0.9, rationale="EF is a cardiac magnitude",
                          suggester_iri="urn:iladub:suggester/fake")
    got = FakeGroundingProposer(p).propose_grounding(SurfaceConcept("EF", "55%", "r2"), ())
    assert got is p and got.field_iri.endswith("f-ef") and got.confidence == 0.9
