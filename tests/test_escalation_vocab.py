import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def _hol():
    return Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")


def test_escalatedto_is_decision_to_decision_objectproperty():
    g = _hol()
    assert (HOL.escalatedTo, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.escalatedTo, RDFS.domain, HOL.DecisionHolon) in g
    assert (HOL.escalatedTo, RDFS.range, HOL.DecisionHolon) in g


def test_maxseverity_is_objectproperty_on_scope():
    g = _hol()
    assert (HOL.maxSeverity, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.maxSeverity, RDFS.domain, HOL.Scope) in g


def test_hol_stays_standalone_no_hga():
    text = open(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), encoding="utf-8").read()
    assert "w3id.org/holon" not in text
