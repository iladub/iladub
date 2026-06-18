import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


def _shapes_and_knowledge():
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    return shapes, knowledge


def test_conformant_offer_passes():
    shapes, knowledge = _shapes_and_knowledge()
    data = Graph().parse(os.path.join(TXD, "offer-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_leak_offer_fails():
    shapes, knowledge = _shapes_and_knowledge()
    data = Graph().parse(os.path.join(TXD, "offer-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
