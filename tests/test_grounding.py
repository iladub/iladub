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


def test_neural_to_unconstrained_field_quarantined():
    """A NEURAL proposal to ejectionFraction (no scheme, no distinguishing constraint) has no
    oracle → must quarantine, never ground (the soundness boundary)."""
    c = load_contract(CONTRACT); g = Graph()
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    p = FakeGroundingProposer(GroundingProposal(ef.iri, str(TX)+"Magnitude", 0.99, "looks like EF",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))


from iladub.validate import validate
from rdflib import BNode, Literal


def _epistemics_knowledge():
    g = Graph()
    for f in ["vocab/ontology/iladub.ttl", "vocab/ontology/dec.ttl"]:
        g.parse(f, format="turtle")
    return g


def _iladub_shapes():
    return Graph().parse("vocab/shapes/iladub-shapes.ttl", format="turtle")


def _build_offer():
    """organ (exact, scheme) + Blood type->aboGroup (NEURAL, scheme-verified) → a conformant offer;
    wrong "55%"->aboGroup (scheme-rejected), EF (NEURAL, unconstrained), novel → all quarantined."""
    c = load_contract(CONTRACT); terms = _terms(); shapes = _shapes(); g = Graph()
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    out = {}
    out["organ"] = ground_concept(SurfaceConcept("organ", "Heart", "r0"), c, OFFER, _noop_proposer(), terms, shapes, g)
    blood = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"Category", 0.8, "blood type is ABO", "urn:iladub:suggester/fake"))
    out["abo"]   = ground_concept(SurfaceConcept("Blood type", "A", "r1"), c, OFFER, blood, terms, shapes, g)
    wrong = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"x", 0.95, "guess", "urn:iladub:suggester/fake"))
    out["wrong"] = ground_concept(SurfaceConcept("mystery", "55%", "r3"), c, OFFER, wrong, terms, shapes, g)
    efp = FakeGroundingProposer(GroundingProposal(ef.iri, str(TX)+"Magnitude", 0.9, "cardiac EF", "urn:iladub:suggester/fake"))
    out["ef"]    = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, efp, terms, shapes, g)
    out["novel"] = ground_concept(SurfaceConcept("smoking pack-years", "20", "r4"), c, OFFER, _noop_proposer(), terms, shapes, g)
    return g, out


def test_end_to_end_grounds_and_quarantines():
    g, out = _build_offer()
    assert out == {"organ": "grounded", "abo": "grounded",
                   "wrong": "proposed", "ef": "proposed", "novel": "proposed"}


def test_grounded_offer_conforms_to_contract_and_epistemics():
    g, _ = _build_offer()
    contract_know = Graph().parse(CONTRACT, format="turtle"); contract_know += _terms()
    r1 = validate(g, _shapes(), contract_know)          # organ + aboGroup satisfy OrganOfferShape
    assert r1.conforms, r1.report_text
    r2 = validate(g, _iladub_shapes(), _epistemics_knowledge())   # promotion invariant + no leak
    assert r2.conforms, r2.report_text

# --- negative tests: the epistemics/contract are real; these MUST fail validation ---

def test_neg_grounded_without_promotion_fails():
    g = Graph(); gn = BNode()
    g.add((gn, RDF.type, ILA.GroundedNode))
    g.add((gn, ILA.groundsTo, TX.aboGroup))
    g.add((gn, ILA.status, ILA.asserted))               # missing wasPromotedBy
    r = validate(g, _iladub_shapes(), _epistemics_knowledge())
    assert not r.conforms and "promotion" in r.report_text.lower()


def test_neg_proposition_asserted_fails():
    g = Graph(); cc = BNode()
    g.add((cc, RDF.type, ILA.CandidateConcept))
    g.add((cc, ILA.surfaceText, Literal("x")))
    g.add((cc, ILA.status, ILA.asserted))               # a proposition must not be asserted
    r = validate(g, _iladub_shapes(), _epistemics_knowledge())
    assert not r.conforms


def test_neg_wrong_mapping_asserted_fails_contract():
    # force a 2nd aboGroup INTO the grounded offer -> maxCount 1 violation (what dispose prevents)
    g, _ = _build_offer()
    g.add((OFFER, TX.aboGroup, Literal("55%")))
    contract_know = Graph().parse(CONTRACT, format="turtle"); contract_know += _terms()
    r = validate(g, _shapes(), contract_know)
    assert not r.conforms
