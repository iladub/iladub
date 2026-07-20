from rdflib import Graph
from iladub.ground import (
    SurfaceConcept, load_contract, exact_field, scheme_member,
)
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

CONTRACT = "examples/transplant/offer-contract.ttl"
TERMS = "examples/transplant/transplant-terms.ttl"


def _terms():
    return Graph().parse(TERMS, format="turtle")


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
