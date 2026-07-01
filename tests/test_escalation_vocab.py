import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = Namespace("https://w3id.org/iladub/dec#")


def _hol():
    return Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")


def test_escalatedto_is_decision_to_decision_objectproperty():
    g = _hol()
    assert (DEC.escalatedTo, RDF.type, OWL.ObjectProperty) in g
    assert (DEC.escalatedTo, RDFS.domain, DEC.DecisionHolon) in g
    assert (DEC.escalatedTo, RDFS.range, DEC.DecisionHolon) in g


def test_maxseverity_is_objectproperty_on_scope():
    g = _hol()
    assert (DEC.maxSeverity, RDF.type, OWL.ObjectProperty) in g
    assert (DEC.maxSeverity, RDFS.domain, DEC.Scope) in g
    # range intentionally left open — hol stays standalone (risk:Severity lives in a separate module)
    assert next(g.objects(DEC.maxSeverity, RDFS.range), None) is None


def test_hol_stays_standalone_no_hga():
    with open(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), encoding="utf-8") as fh:
        text = fh.read()
    assert "w3id.org/holon" not in text
