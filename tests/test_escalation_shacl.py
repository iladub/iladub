import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")


def _knowledge():
    # dec.ttl gives the vocab; risk.ttl carries the risk:order ordinals the SPARQL compares.
    g = Graph()
    g.parse(os.path.join(ONT, "dec.ttl"), format="turtle")
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    return g


def _data(example_filename):
    # risk.ttl is also merged into the data graph so risk:order is visible to the SPARQL
    # constraint regardless of pySHACL ont-graph query semantics (deterministic).
    g = Graph()
    g.parse(os.path.join(TXD, example_filename), format="turtle")
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    return g


def test_escalation_conformant_passes():
    shapes = Graph()
    shapes.parse(os.path.join(SH, "dec-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    res = validate(_data("transplant-escalation.ttl"), shapes, _knowledge())
    assert res.conforms, res.report_text


def test_escalation_leak_fails():
    shapes = Graph().parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    res = validate(_data("transplant-escalation-leak.ttl"), shapes, _knowledge())
    assert not res.conforms
