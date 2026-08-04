"""Loop Q Task 6 fix round (F2) — the CBH demo contract trio (examples/shipping/cbh-*.ttl)
was shipped but cbh-shapes.ttl was never exercised by any test. Imitates
tests/test_stem_contract.py's treatment of stem-shapes.ttl: parse the shapes, ground a
conforming instance through them (SHACL value-membrane path), and pin one negative
fixture that must fail conformance and quarantine instead."""
import pytest
from rdflib import Graph, Namespace, RDF, URIRef

from iladub.ground import SurfaceConcept, ground_concept, load_contract
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

ILADUB = Namespace("https://w3id.org/iladub#")
CBH = Namespace("https://example.org/cbh#")
CONTRACT = "examples/shipping/cbh-contract.ttl"
TERMS = "examples/shipping/cbh-terms.ttl"
SHAPES = "examples/shipping/cbh-shapes.ttl"

# Same idiom as test_stem_contract.py's ABSTAIN: field_iri=None -> any non-exact-match
# concept falls straight to quarantine.
ABSTAIN = FakeGroundingProposer(
    GroundingProposal(None, str(CBH) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))


def _ground(field_text, value):
    contract = load_contract(CONTRACT)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    g = Graph()
    verdict = ground_concept(SurfaceConcept(field_text, value, "p0-x-y"), contract,
                             URIRef("urn:record#r1"), ABSTAIN, terms, shapes, g)
    return verdict, g


def test_contract_loads_five_fields_two_schemes():
    c = load_contract(CONTRACT)
    assert len(c.fields) == 5
    assert sum(1 for f in c.fields if f.scheme) == 2           # port, commodity


def test_shapes_parse_and_declare_volume_pattern():
    shapes = Graph().parse(SHAPES, format="turtle")
    assert (None, None, CBH.volume) in shapes                  # sh:path cbh:volume present


@pytest.mark.parametrize("field,value", [
    ("Port", "GERALDTON"), ("Commodity", "Wheat"), ("Volume", "25,000")])
def test_conforming_instance_grounds_through_the_shape(field, value):
    """The positive case: cbh-shapes.ttl's `volume` pattern (a REAL SHACL value
    constraint, parsed from the shipped file, not a stand-in) accepts a conforming value —
    grounds exactly like the scheme-verified fields."""
    verdict, g = _ground(field, value)
    assert verdict == "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.PromotionDecision) in g


@pytest.mark.parametrize("field,value", [
    ("Volume", "TBA"), ("Volume", "a lot"), ("Port", "Vibranium"),
    ("Name Of Ship", "STAR EXPRESS")])                          # no contract field at all
def test_negative_fixture_fails_the_shape_and_quarantines(field, value):
    """The negative fixture: 'Volume'='TBA' fails cbh-shapes.ttl's pattern constraint —
    the SHACL validation this test exercises for the first time must actually REJECT it,
    not merely be present in the repo unused."""
    verdict, g = _ground(field, value)
    assert verdict != "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.CandidateConcept) in g
