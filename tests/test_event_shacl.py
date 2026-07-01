import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


def _shapes_knowledge():
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")
    return shapes, knowledge


def test_event_with_condition_conforms():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "event-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_event_without_condition_fails():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "event-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
