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
    assert any(True for _ in g.objects(OFFER, TX.aboGroup))   # the offer carries the aboGroup literal


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
    """A NEURAL proposal to causeOfDeath (no scheme, no value constraint in the shape) has no
    oracle → must quarantine, never ground (the preserved soundness boundary)."""
    c = load_contract(CONTRACT); g = Graph()
    cod = next(f for f in c.fields if f.fills_property.endswith("causeOfDeath"))
    p = FakeGroundingProposer(GroundingProposal(cod.iri, str(TX)+"Category", 0.99, "cause of death",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("COD", "MVA", "r5"), c, OFFER, p, _terms(), _shapes(), g)
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
    """organ (exact, scheme) + Blood type->aboGroup (NEURAL, scheme-verified) + EF (NEURAL,
    SHACL value-constraint-verified) → a conformant offer; wrong "55%"->aboGroup
    (scheme-rejected) and novel → quarantined."""
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
                   "wrong": "proposed", "ef": "grounded", "novel": "proposed"}


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


# --- the promotion decision deliberates (spec 2026-08-10 §5.3) ---------------------
#
# MEASURED before-state (docs/loops/2026-08-10-decision-membrane-baseline.md): every
# iladub:PromotionDecision iladub has ever produced on a real document fails
# dec:DecisionHolonShape — graincorp-stem 585, cbh-stem 134, all refusing BOTH
# dec:optionSpace (minCount 2) and dec:chosen (minCount 1), under both closures.
# The oracle is vocab/shapes/dec-shapes.ttl, which this loop may not edit.

DECNS = Namespace("https://w3id.org/iladub/dec#")


def _dec_conforms(g):
    """(conforms, text) against the SHIPPED closure, through `membrane._payload` — matching
    `membrane._validate_pyshacl` exactly (spec 2026-08-13-membrane-parity-design.md §3: since
    parity, that function validates `_payload`'s re-parsed graph, not `subclass_closure`'s
    live one, and this helper must track it or the claim is false). Called directly rather
    than through `membrane.validate` because this helper pins pySHACL's verdict on a shape
    SUBSET (dec-shapes.ttl alone), not the process engine's verdict on the membrane's full set.

    That bypass used to be FORCED: these fixtures mint blank-node PromotionDecisions
    (ground.py:90,145) and rudof raised rather than answering on dec-shapes.ttl's sh:sparql
    constraint with a blank-node focus. It no longer is — `membrane._payload` skolemizes (spec
    2026-08-13-membrane-parity-design.md §4.3, closing R88) — so the bypass is now a choice."""
    from pyshacl import validate as _v
    from iladub.etkl import membrane
    ont = Graph()
    for f in ("dec.ttl", "iladub.ttl", "etkl.ttl", "tab.ttl"):
        ont.parse(f"vocab/ontology/{f}", format="turtle")
    shapes = Graph().parse("vocab/shapes/dec-shapes.ttl", format="turtle")
    expanded, _ = membrane._payload(g, ont)
    conforms, _, text = _v(expanded, shacl_graph=shapes,
                           inference="none", advanced=True)
    return bool(conforms), text


def _ground_via_scheme():
    """Oracle 1: SKOS scheme membership (aboGroup is scheme-bound)."""
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("ABO group", "A", "r1"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    return out, g


def _ground_via_value_membrane():
    """Oracle 2: the SHACL value membrane (EF is proposed, not exact, and constrained)."""
    from iladub.propose_ground import GroundingProposal, FakeGroundingProposer
    c = load_contract(CONTRACT)
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    p = FakeGroundingProposer(GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                "cardiac EF", "urn:iladub:suggester/fake"))
    g = Graph()
    out = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    return out, g


def _ground_via_field_identity():
    """Oracle 3: field identity (causeOfDeath declares no value constraint at all)."""
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("causeOfDeath", "anoxia", "r0"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    return out, g


def _the_decision(g):
    pds = list(g.subjects(RDF.type, ILA.PromotionDecision))
    assert len(pds) == 1, pds
    return pds[0]


def test_a_quarantined_concept_mints_no_promotion_decision():
    """MEASURED, and it is why this module's O3 test is shaped as it is: a concept that
    REFUSES returns "proposed" at ground.py:158/161 with no decision emitted at all, so a
    rejected option cannot be read off a refusing concept. Corroborated by the baseline's
    own arithmetic: cbh-stem 909 candidates = 134 grounded + 775 quarantined, with
    PromotionDecision = 134."""
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("smoking pack-years", "20", "r4"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.PromotionDecision))


def test_a_promotion_decision_names_the_options_it_deliberated():
    """§5.3: the option space is READ OFF the branch ground_concept already takes — it
    branches on `field is None` and then on `grounds_to is None`, and the two outcomes are
    "grounded" and "proposed". Naming them invents nothing."""
    for name, (out, g) in [("scheme", _ground_via_scheme()),
                           ("value-membrane", _ground_via_value_membrane()),
                           ("field-identity", _ground_via_field_identity())]:
        assert out == "grounded", name
        conforms, text = _dec_conforms(g)
        assert conforms, f"[{name}] {text}"

        pd = _the_decision(g)
        options = list(g.objects(pd, DECNS.optionSpace))
        assert len(options) >= 2, f"[{name}] a real decision deliberates >= 2 options"
        chosen = list(g.objects(pd, DECNS.chosen))
        assert len(chosen) == 1, f"[{name}] exactly one chosen option: {chosen}"
        assert chosen[0] in options, f"[{name}] the chosen option must be in the space"
        # the chosen option is the ground-to-field one: it names where the concept landed
        from rdflib.namespace import RDFS
        label = g.value(chosen[0], RDFS.label)
        assert label is not None, f"[{name}] the chosen option is unlabelled"
        target = g.value(list(g.subjects(RDF.type, ILA.GroundedNode))[0], ILA.groundsTo)
        assert str(target) in str(label), (
            f"[{name}] the chosen option must name the grounding target {target}: {label}")
        # the OTHER option is the branch not taken, and it says why it lost
        rejected = [o for o in options if o != chosen[0]]
        assert len(rejected) == 1, f"[{name}] {rejected}"
        assert list(g.objects(rejected[0], DECNS.rejectedBecause)), (
            f"[{name}] the rejected option must say why")


def test_the_rejected_option_names_the_oracle_that_actually_applied():
    """THE O3 ANTI-DECORATION ASSERTION. A single hard-coded rejection string passes every
    assertion above and fails this one.

    NOTE ON SHAPE (a plan defect found by measurement, see the task report): the plan asked
    for two concepts that REFUSE for different reasons. A refusing concept mints no decision
    (pinned by test_a_quarantined_concept_mints_no_promotion_decision), so it has no options
    to compare. The satisfiable form with the same force: three concepts that GROUND through
    the three DIFFERENT oracles of `_grounds_to` must carry three DIFFERENT
    dec:rejectedBecause, because the refusal path quarantine would have taken differs."""
    reasons = {}
    for name, (out, g) in [("scheme", _ground_via_scheme()),
                           ("value-membrane", _ground_via_value_membrane()),
                           ("field-identity", _ground_via_field_identity())]:
        pd = _the_decision(g)
        chosen = next(iter(g.objects(pd, DECNS.chosen)))
        rejected = [o for o in g.objects(pd, DECNS.optionSpace) if o != chosen][0]
        reasons[name] = str(next(iter(g.objects(rejected, DECNS.rejectedBecause))))
    assert len(set(reasons.values())) == 3, (
        f"the rejected option says the same thing whatever oracle applied: {reasons}")
