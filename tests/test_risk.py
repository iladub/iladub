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


# --- dec:12 / dec:13 (arc): the negative halves of the two risk shapes, pinned to their constraints ---

def _violations(data, shapes, ont):
    """(focus, path, component) per violation from the results graph; `not c` alone could
    pass on a neighbour shape, and sh:sourceShape is an anonymous property shape here."""
    from rdflib.namespace import SH as SHACL
    _, r, _ = validate(_g(*data), shacl_graph=_g(*shapes), ont_graph=_g(*ont),
                       inference="rdfs", advanced=True)
    return {(r.value(v, SHACL.focusNode), r.value(v, SHACL.resultPath),
             r.value(v, SHACL.sourceConstraintComponent))
            for v in r.subjects(SHACL.sourceConstraintComponent, None)}


def test_contextless_assessment_rejected():
    """An assessment with a severity but no subject and no context trips both minCounts
    of RiskAssessmentShape at that node."""
    from rdflib.namespace import SH as SHACL
    node = URIRef("https://example.org/transplant#assessment-contextless")
    fired = _violations([os.path.join(TST, "risk-assessment-contextless-leak.ttl")],
                        [RISK_SHAPES], [RISK_TTL])
    for path in ("https://w3id.org/iladub/risk#ofSubject", "https://w3id.org/iladub/risk#inContext"):
        assert (node, URIRef(path), SHACL.MinCountConstraintComponent) in fired, fired


def test_sensitivity_without_reads_rejected():
    """A sensitivity with a severity and no risk:reads trips SensitivityShape's minCount on
    risk:reads at that node."""
    from rdflib.namespace import SH as SHACL
    node = URIRef("https://example.org/transplant#sensitivity-blind")
    fired = _violations([os.path.join(TST, "sensitivity-without-reads-leak.ttl")],
                        [RISK_SHAPES], [RISK_TTL])
    assert (node, URIRef("https://w3id.org/iladub/risk#reads"),
            SHACL.MinCountConstraintComponent) in fired, fired
