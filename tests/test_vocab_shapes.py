"""Conformance tests for the ET(K)L and hol vocabularies: a worked example
that CONFORMS and a negative example that must FAIL, for each shape set."""
import os
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


# --- hol decision accountability ---

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
