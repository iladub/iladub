"""The off-the-map boundary outcome (dec:ExpansionRequest): a worked example
that CONFORMS, a negative that must FAIL, and the vocabulary/alignment facts —
CandidateConcept's expansion-request event, iladub's gap-fill over HGA.
See docs/four-groundings.md and Cagle & Shannon, "Off the Edge of the Map" (2026-07-01)."""
import os
from rdflib import Graph, Namespace, RDFS
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")

DEC = Namespace("https://w3id.org/iladub/dec#")
HEV = Namespace("http://w3id.org/holon/event/")


def _shapes_knowledge():
    shapes = Graph().parse(os.path.join(SH, "dec-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ONT, "dec.ttl"), format="turtle")
    return shapes, knowledge


def test_expansion_request_conforms():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "examples", "expansion-request.ttl"), format="turtle")
    result = validate(data, shapes, knowledge)
    assert result.conforms, result.report_text


def test_expansion_request_without_regarding_fails():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "tests", "expansion-request-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms


def test_expansion_request_is_an_event():
    # It must inherit the dec:Event envelope (hence carry a condition, and be an
    # hev:HolonEvent once the alignment module is loaded).
    dec = Graph().parse(os.path.join(ONT, "dec.ttl"), format="turtle")
    assert (DEC.ExpansionRequest, RDFS.subClassOf, DEC.Event) in dec


def test_expansion_request_aligns_to_hga_event_envelope():
    # dec.ttl stays standalone (no HGA); the envelope alignment lives in the
    # optional module, where dec:Event is an hev:HolonEvent — inherited by ExpansionRequest.
    align = Graph().parse(os.path.join(ONT, "dec-hga-align.ttl"), format="turtle")
    assert (DEC.Event, RDFS.subClassOf, HEV.HolonEvent) in align
