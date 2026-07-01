import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


def _shapes_knowledge():
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")
    return shapes, knowledge


def test_conformant_milestone_passes():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "heart-timeline-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_milestone_without_order_fails():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "heart-timeline-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
