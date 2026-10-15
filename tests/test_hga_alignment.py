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
ETKL   = "https://w3id.org/iladub/etkl#"
HEV    = "http://w3id.org/holon/event/"
DEC_NS = "https://w3id.org/iladub/dec#"

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


def test_dec_alignment_axioms_present():
    """The dec->HGA module anchors the authority holarchy and event envelope to HGA."""
    g = _g(os.path.join(ONT, "dec-hga-align.ttl"))
    assert (URIRef(DEC_NS + "partOf"), RDFS.subPropertyOf, URIRef(HOLON + "partOf")) in g
    assert (URIRef(DEC_NS + "Event"), RDFS.subClassOf, URIRef(HEV + "HolonEvent")) in g


def test_dec_module_standalone():
    """The core dec vocabulary must NOT hard-depend on the holon: namespace."""
    text = open(os.path.join(ONT, "dec.ttl")).read()
    assert "w3id.org/holon" not in text, "core dec module leaked an HGA dependency"


# --- dec:17 (arc): the Contract's four provenance-reuse axioms are asserted, not just declared ---

def test_dec_provenance_axioms_present():
    """CLAUDE.md § Serialization: dec:DecisionHolon ⊑ prov:Activity and the three property
    alignments. dec.ttl alone (standalone module; PROV is not HGA — § Source ownership)."""
    from rdflib import Namespace
    DEC, PROV = Namespace("https://w3id.org/iladub/dec#"), Namespace("http://www.w3.org/ns/prov#")
    g = _g(os.path.join(ONT, "dec.ttl"))
    assert (DEC.DecisionHolon, RDFS.subClassOf, PROV.Activity) in g
    assert (DEC.consideredEvidence, RDFS.subPropertyOf, PROV.used) in g
    assert (DEC.decidedBy, RDFS.subPropertyOf, PROV.wasAssociatedWith) in g
    assert (DEC.produced, RDFS.subPropertyOf, PROV.generated) in g


def test_portal_property_alignment():
    """spec § 3.2: source aligns by subPropertyOf (both object properties); target only by
    seeAlso, because holon:portalTarget is a DatatypeProperty over xsd:anyURI."""
    from rdflib import OWL, RDF
    g = _g(os.path.join(ONT, "iladub-hga-align.ttl"))
    src, tgt = URIRef(ETKL + "portalSource"), URIRef(ETKL + "portalTarget")
    assert (src, RDFS.subPropertyOf, URIRef(HOLON + "sourceHolon")) in g
    assert (tgt, RDFS.seeAlso, URIRef(HOLON + "portalTarget")) in g
    assert (tgt, RDFS.subPropertyOf, URIRef(HOLON + "portalTarget")) not in g
    h = _g(os.path.join(ONT, "etkl-holons.ttl"))
    for p, rng in ((src, "RawDocumentHolon"), (tgt, "SemanticHolon")):
        assert (p, RDF.type, OWL.ObjectProperty) in h
        assert (p, RDFS.domain, URIRef(ETKL + "GroundingPortal")) in h
        assert (p, RDFS.range, URIRef(ETKL + rng)) in h


TRAVERSAL_SHAPES = [os.path.join(SH, f) for f in
                    ("iladub-shapes.ttl", "dec-shapes.ttl", "etkl-holon-shapes.ttl",
                     "iladub-hga-shapes.ttl")]
TRAVERSAL_ONTS = ONTS + [os.path.join(ONT, "dec.ttl")]
TRAVERSAL_EX = os.path.join(EX, "raw-to-clean-traversal.ttl")


def test_raw_to_clean_traversal_conformant():
    """holon:06's oracle (tests/arc-manifest.ttl): the compiler-produced example conforms and
    spans Raw → portal → Clean (spec § 5 item 1)."""
    from rdflib import RDF
    c, t = _v([TRAVERSAL_EX], TRAVERSAL_SHAPES, TRAVERSAL_ONTS)
    assert c, t
    g = _g(TRAVERSAL_EX)
    count = lambda cls: len(set(g.subjects(RDF.type, URIRef(ETKL + cls))))
    assert (count("CleanDocumentHolon"), count("GroundingPortal"),
            count("RawDocumentHolon")) == (1, 1, 1)
    assert count("SemanticHolon") >= 1


def test_raw_to_clean_example_is_what_the_compiler_emits():
    """spec § 4: regenerate and compare by graph isomorphism (decisions are blank nodes)."""
    import importlib.util
    import pytest
    from rdflib.compare import isomorphic
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    spec = importlib.util.spec_from_file_location(
        "raw_to_clean_example", os.path.join(ROOT, "scripts", "raw_to_clean_example.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert isomorphic(mod.build(), _g(TRAVERSAL_EX)), \
        "examples/raw-to-clean-traversal.ttl is stale: run scripts/raw_to_clean_example.py"
