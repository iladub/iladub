"""iladub <-> HGA (W3C Holon CG) alignment + grounding-governance invariants.

Anchor (settled 2026-06-23): Cagle's W3C HGA, `holon:` = http://w3id.org/holon/.
Alignment-not-import: iladub stays standalone; the alignment module carries only
rdfs:subClassOf axioms and is loaded explicitly here.
"""
import os
from rdflib import Graph, RDFS, URIRef
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH  = os.path.join(ROOT, "vocab", "shapes")
EX  = os.path.join(ROOT, "examples")
TST = os.path.join(ROOT, "tests")

HOLON  = "http://w3id.org/holon/"
ILADUB = "https://w3id.org/etkl/iladub#"
ETKL   = "https://w3id.org/etkl#"
HEV    = "http://w3id.org/holon/event/"
HOL_NS = "https://w3id.org/etkl/hol#"

def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g

def _v(data, shapes, ont):
    c, _, t = validate(_g(*data), shacl_graph=_g(*shapes), ont_graph=_g(*ont),
                       inference="rdfs", advanced=True)
    return c, t

ONTS = [os.path.join(ONT, "iladub.ttl"), os.path.join(ONT, "etkl-holons.ttl")]
SHAPES = [os.path.join(SH, "iladub-shapes.ttl"), os.path.join(SH, "iladub-hga-shapes.ttl")]
HGA_SHAPES = [os.path.join(SH, "iladub-hga-shapes.ttl")]

def test_alignment_axioms_present():
    """The optional alignment module anchors iladub holon types under HGA."""
    g = _g(os.path.join(ONT, "iladub-hga-align.ttl"))
    expected = {
        ("CleanDocumentHolon", "DataHolon"),
        ("RawDocumentHolon",   "DataHolon"),
        ("SemanticHolon",      "DataHolon"),
        ("GroundingPortal",    "Portal"),
    }
    for sub, obj in expected:
        assert (URIRef(ETKL + sub), RDFS.subClassOf, URIRef(HOLON + obj)) in g, \
            f"missing alignment: etkl:{sub} rdfs:subClassOf holon:{obj}"

def test_holons_module_standalone():
    """The core holon-types module must NOT hard-depend on the holon: namespace."""
    text = open(os.path.join(ONT, "etkl-holons.ttl")).read()
    assert "w3id.org/holon" not in text, "etkl-holons.ttl leaked an HGA dependency"

def test_governed_grounding_conformant():
    """A registered GroundingRecord produced by a PromotionDecision conforms."""
    c, t = _v([os.path.join(EX, "holon-grounding-conformant.ttl")], SHAPES, ONTS)
    assert c, t

def test_ungoverned_grounding_rejected():
    """A registered GroundingRecord with no promotion decision MUST fail."""
    c, _ = _v([os.path.join(TST, "holon-grounding-leak.ttl")], HGA_SHAPES, ONTS)
    assert not c


def test_hol_alignment_axioms_present():
    """The hol->HGA module anchors the authority holarchy and event envelope to HGA."""
    g = _g(os.path.join(ONT, "hol-hga-align.ttl"))
    assert (URIRef(HOL_NS + "partOf"), RDFS.subPropertyOf, URIRef(HOLON + "partOf")) in g
    assert (URIRef(HOL_NS + "Event"), RDFS.subClassOf, URIRef(HEV + "HolonEvent")) in g


def test_hol_module_standalone():
    """The core hol vocabulary must NOT hard-depend on the holon: namespace."""
    text = open(os.path.join(ONT, "hol.ttl")).read()
    assert "w3id.org/holon" not in text, "core hol module leaked an HGA dependency"
