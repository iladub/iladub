from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import XSD
from iladub.ground import (
    _property_shape, _has_value_constraint, _value_conforms,
    SurfaceConcept, load_contract, ground_concept,
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
