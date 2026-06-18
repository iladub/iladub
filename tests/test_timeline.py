import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def test_heart_process_has_five_milestones():
    g = _heart_graph()
    ms = list(g.objects(TX["heart-process"], HOL.hasMilestone))
    assert len(ms) == 5
