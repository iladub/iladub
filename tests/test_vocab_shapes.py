"""Conformance tests for the ET(K)L and dec vocabularies: a worked example
that CONFORMS and a negative example that must FAIL, for each shape set."""
import os
import pytest
from rdflib import Graph
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")
EX = os.path.join(ROOT, "examples")
TST = os.path.join(ROOT, "tests")


def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def _validate(data, shapes, ont):
    conforms, _, text = validate(
        _g(*data), shacl_graph=_g(shapes), ont_graph=_g(*ont),
        inference="rdfs", advanced=True,
    )
    return conforms, text


# --- ET(K)L conformance (knowledge-first is a checkable property) ---

def test_etkl_conformant_pipeline():
    c, t = _validate(
        [os.path.join(EX, "etkl-conformant.ttl")],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl.ttl")],
    )
    assert c, t


def test_etkl_knowledge_free_pipeline_rejected():
    c, _ = _validate(
        [os.path.join(TST, "etkl-bad.ttl")],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl.ttl")],
    )
    assert not c


# --- dec decision accountability ---

def test_hol_decision_conformant():
    c, t = _validate(
        [os.path.join(EX, "promotion.ttl")],
        os.path.join(SH, "dec-shapes.ttl"),
        [os.path.join(ONT, "dec.ttl")],
    )
    assert c, t


def test_hol_rubber_stamp_rejected():
    c, _ = _validate(
        [os.path.join(TST, "dec-bad.ttl")],
        os.path.join(SH, "dec-shapes.ttl"),
        [os.path.join(ONT, "dec.ttl")],
    )
    assert not c


# --- membrane health: the signal minted after validation is governed by SHACL ---

def test_membrane_health_conformant():
    c, t = _validate(
        [os.path.join(EX, "membrane-health-conformant.ttl")],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl-holons.ttl")],
    )
    assert c, t


@pytest.mark.parametrize("bad", ["membrane-health-bad-two-values.ttl",
                                 "membrane-health-bad-outside-enum.ttl"])
def test_membrane_health_malformed_rejected(bad):
    c, _ = _validate(
        [os.path.join(TST, bad)],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl-holons.ttl")],
    )
    assert not c


# --- dec:02 (arc): the negative half of dec:ConfidenceShape, pinned to its constraints ---

def _violations(data, shapes, ont):
    """(focus node, result path, constraint component) per violation, read from pySHACL's
    results graph — not the bare verdict. A fixture that fails for a NEIGHBOUR shape's reason
    would pass `not conforms` while pinning nothing (CLAUDE.md § Plan authoring, defect 5, in
    fixture form). sh:sourceShape is not used: on a property constraint it is the anonymous
    property shape, which names nothing a test can spell."""
    from rdflib.namespace import SH as SHACL
    _, results, _ = validate(
        _g(*data), shacl_graph=_g(shapes), ont_graph=_g(*ont),
        inference="rdfs", advanced=True,
    )
    return {(results.value(r, SHACL.focusNode), results.value(r, SHACL.resultPath),
             results.value(r, SHACL.sourceConstraintComponent))
            for r in results.subjects(SHACL.sourceConstraintComponent, None)}


def test_confidence_out_of_range_rejected():
    """A decision holon carrying dec:confidence 1.5 AND a second value trips BOTH arms of
    dec:ConfidenceShape — [0,1] and maxCount 1 — on dec:confidence, at that node."""
    from rdflib import URIRef
    from rdflib.namespace import SH as SHACL
    node = URIRef("https://example.org/demo#decision-overconfident")
    path = URIRef("https://w3id.org/iladub/dec#confidence")
    fired = _violations(
        [os.path.join(TST, "dec-confidence-leak.ttl")],
        os.path.join(SH, "dec-shapes.ttl"),
        [os.path.join(ONT, "dec.ttl")],
    )
    assert (node, path, SHACL.MaxInclusiveConstraintComponent) in fired, fired
    assert (node, path, SHACL.MaxCountConstraintComponent) in fired, fired
