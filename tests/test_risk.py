"""Contextual-risk vocabulary (etkl/risk) — invariants and the no-empiric-stamp guard.

Risk is contextual, not empiric: a severity may live only on a Sensitivity (a rule) or a
RiskAssessment (a context-local projection), never stamped on a domain subject.
"""
import os
from rdflib import Graph, RDFS, URIRef
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH  = os.path.join(ROOT, "vocab", "shapes")
EX  = os.path.join(ROOT, "examples", "transplant")
TST = os.path.join(ROOT, "tests")

RISK  = "https://w3id.org/iladub/risk#"
HOLON = "http://w3id.org/holon/"
HPROJ = "http://w3id.org/holon/projection/"

def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g

def _v(data, shapes, ont):
    c, _, t = validate(_g(*data), shacl_graph=_g(*shapes), ont_graph=_g(*ont),
                       inference="rdfs", advanced=True)
    return c, t

RISK_TTL = os.path.join(ONT, "risk.ttl")
RISK_SHAPES = os.path.join(SH, "risk-shapes.ttl")

def test_risk_vocab_parses_with_core_terms():
    g = _g(RISK_TTL)
    from rdflib.namespace import RDF, OWL
    for cls in ("RiskContext", "Sensitivity", "RiskAssessment", "Severity"):
        assert (URIRef(RISK + cls), RDF.type, OWL.Class) in g, f"missing class risk:{cls}"

def test_risk_module_is_standalone():
    """The core risk vocab must NOT hard-depend on the holon: namespace."""
    text = open(RISK_TTL).read()
    assert "w3id.org/holon" not in text, "core risk module leaked an HGA dependency"

def test_risk_alignment_axioms_present():
    g = _g(os.path.join(ONT, "risk-hga-align.ttl"))
    assert (URIRef(RISK + "RiskContext"), RDFS.subClassOf, URIRef(HOLON + "Holon")) in g
    assert (URIRef(RISK + "RiskAssessment"), RDFS.subClassOf, URIRef(HPROJ + "Projection")) in g
    assert (URIRef(RISK + "withinContext"), RDFS.subPropertyOf, URIRef(HOLON + "partOf")) in g

def test_transplant_contextual_risk_conformant():
    """Same condition, different context, derived assessments — all well-formed; no empiric stamp."""
    c, t = _v([os.path.join(EX, "transplant-risk.ttl")], [RISK_SHAPES], [RISK_TTL])
    assert c, t

def test_empiric_risk_stamp_rejected():
    """A domain subject carrying risk:severity directly MUST fail."""
    c, _ = _v([os.path.join(TST, "risk-leak.ttl")], [RISK_SHAPES], [RISK_TTL])
    assert not c
