from rdflib import Graph, Namespace, URIRef, RDF, Literal, BNode
from rdflib.namespace import XSD
from rdflib.collection import Collection
from iladub.ground import (
    _property_shape, _has_value_constraint, _value_conforms,
    SurfaceConcept, load_contract, ground_concept, SH
)
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

TX = Namespace("https://example.org/transplant#")
OFFER = URIRef("urn:test:offer1")
TXO = "https://example.org/transplant#OrganOffer"
ILA = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
CONTRACT = "examples/transplant/offer-contract.ttl"


def _shapes():
    return Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")


def test_ef_property_shape_has_value_constraint():
    s = _shapes()
    ps = _property_shape(s, str(TX) + "ejectionFraction")
    assert ps is not None
    assert _has_value_constraint(s, ps) is True          # datatype + range declared


def test_unconstrained_field_has_no_property_shape():
    s = _shapes()
    # causeOfDeath has no property shape at all -> nothing to verify -> quarantine downstream
    assert _property_shape(s, str(TX) + "causeOfDeath") is None


def test_cardinality_only_is_not_a_value_constraint():
    # organ shape is cardinality-only (min/maxCount) -> not a value constraint
    s = _shapes()
    ps = _property_shape(s, str(TX) + "organ")
    assert ps is not None
    assert _has_value_constraint(s, ps) is False


def test_in_range_decimal_conforms():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "55", _shapes()) is True


def test_out_of_range_does_not_conform():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "150", _shapes()) is False


def test_wrong_datatype_does_not_conform():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "high", _shapes()) is False


def _terms():
    return Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")


def _ef_proposer(value_field="ejectionFraction"):
    c = load_contract(CONTRACT)
    ef = next(f for f in c.fields if f.fills_property.endswith(value_field))
    return c, FakeGroundingProposer(GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                      "cardiac EF", "urn:iladub:suggester/fake"))


def test_in_range_ef_grounds_with_typed_literal_and_mode_rationale():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "grounded"
    gn = list(g.subjects(RDF.type, ILA.GroundedNode))
    assert gn and g.value(gn[0], ILA.groundsTo) == URIRef(str(TX) + "ejectionFraction")
    # typed literal emission (xsd:decimal), not a bare string
    assert Literal("55", datatype=XSD.decimal) in list(g.objects(OFFER, URIRef(str(TX) + "ejectionFraction")))
    # rationale records the weaker verification mode
    pd = list(g.subjects(RDF.type, ILA.PromotionDecision))[0]
    assert "value-constraint" in str(g.value(pd, DEC.rationale)).lower()


def test_out_of_range_ef_quarantines():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "150", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed" and not list(g.subjects(RDF.type, ILA.GroundedNode))


def test_wrong_type_ef_quarantines():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "high", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed" and not list(g.subjects(RDF.type, ILA.GroundedNode))


def test_to_rdf_types_ef_as_decimal_from_shape():
    # the emitter types a free-literal value per the contract shape's sh:datatype (EF -> xsd:decimal)
    # NOTE: to_rdf's real callers (src/iladub/m4.py) pass an OfferExtraction (snake_case
    # fields), not the raw BAML DonorClinical (camelCase) — use the actual production
    # extraction type so this pins real emitter behavior.
    from iladub.to_rdf import to_rdf
    from iladub.extract_baml import OfferExtraction, CodedConcept
    from rdflib.namespace import XSD
    cc = lambda v, q: CodedConcept(value=v, source_quote=q, confidence=0.9)
    extraction = OfferExtraction(organ=cc("Heart", "HEART"), ejection_fraction=cc("60", "LVEF 60%"))
    eg = to_rdf(extraction, Graph(), _shapes())
    from rdflib import URIRef
    vals = list(eg.graph.objects(URIRef(str(TX) + "offer"), URIRef(str(TX) + "ejectionFraction")))
    assert vals == [Literal("60", datatype=XSD.decimal)]


def _noop():
    return FakeGroundingProposer(GroundingProposal(None, str(TX) + "x", 0.0, "n/a", "urn:iladub:suggester/fake"))


def test_exact_path_enforces_value_constraint():
    # "ejectionFraction" EXACT-matches the EF field -> is_exact, proposer never consulted.
    # Uniform membrane: an in-range value grounds; an out-of-range value quarantines (was: grounded).
    c = load_contract(CONTRACT); terms = _terms(); shapes = _shapes()
    for value, expect in [("60", "grounded"), ("999", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("ejectionFraction", value, "r0"), c, OFFER, _noop(), terms, shapes, g)
        assert out == expect, (value, out)
    # the out-of-range exact value emitted NO grounded node
    g = Graph()
    ground_concept(SurfaceConcept("ejectionFraction", "999", "r0"), c, OFFER, _noop(), terms, shapes, g)
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))


def _augmented_shapes(property_iri, add_constraint):
    """offer-shapes.ttl + an extra property shape on `property_iri` (built in-memory; the committed
    file is NEVER modified). add_constraint(shapes, ps) attaches the value constraint to ps."""
    s = _shapes()
    node = next(s.subjects(SH.targetClass, TX.OrganOffer))
    ps = BNode()
    s.add((node, SH.property, ps))
    s.add((ps, SH.path, URIRef(property_iri)))
    add_constraint(s, ps)
    return s


def test_sh_pattern_grounds_on_match_quarantines_on_miss():
    # header "Size" -> propose f-size (not exact); sh:pattern gates the value.
    c = load_contract(CONTRACT); terms = _terms()
    size = next(f for f in c.fields if f.fills_property.endswith("sizeMetric"))
    shapes = _augmented_shapes(str(TX) + "sizeMetric",
                               lambda s, ps: s.add((ps, SH.pattern, Literal("^[0-9]+(kg|cm)$"))))
    p = FakeGroundingProposer(GroundingProposal(size.iri, str(TX) + "Magnitude", 0.9, "size", "urn:iladub:suggester/fake"))
    for value, expect in [("78kg", "grounded"), ("big", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("Size", value, "r0"), c, OFFER, p, terms, shapes, g)
        assert out == expect, (value, out)


def test_sh_in_grounds_on_member_quarantines_on_non_member():
    # header "Sero" -> propose f-serology (not exact); sh:in (enum) gates the value.
    c = load_contract(CONTRACT); terms = _terms()
    sero = next(f for f in c.fields if f.fills_property.endswith("serology"))
    def add_enum(s, ps):
        lst = BNode(); Collection(s, lst, [Literal("positive"), Literal("negative")])
        s.add((ps, SH["in"], lst))
    shapes = _augmented_shapes(str(TX) + "serology", add_enum)
    p = FakeGroundingProposer(GroundingProposal(sero.iri, str(TX) + "Category", 0.8, "sero", "urn:iladub:suggester/fake"))
    for value, expect in [("negative", "grounded"), ("unknown", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("Sero", value, "r0"), c, OFFER, p, terms, shapes, g)
        assert out == expect, (value, out)
