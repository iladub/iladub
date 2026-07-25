"""Compile→federate loop: a CleanDocumentHolon's projection becomes the next
document's provided terminology. See docs/superpowers/specs/2026-07-24-compile-federate-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from iladub.etkl import interpret
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH_DIR = os.path.join(ROOT, "vocab", "shapes")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HPROJ = Namespace("http://w3id.org/holon/projection/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ILADUB = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
PROJ = Namespace("urn:iladub:")
QUERIES = os.path.join(ROOT, "vocab", "queries")


def test_document_projection_class_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDF.type, OWL.Class) in g


def test_document_projection_aligns_to_hproj():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDFS.subClassOf, HPROJ.Projection) in g


def test_projection_construct_emits_only_promoted_concepts():
    interior = Graph().parse(os.path.join(ROOT, "tests", "federation-interior-a.ttl"), format="turtle")
    proj = interpret.run(os.path.join(QUERIES, "federate-projection.rq"), interior)
    # the promoted concept is projected, as SKOS, with its public label
    assert (TX.ABO_O, RDF.type, SKOS.Concept) in proj
    assert (TX.ABO_O, SKOS.prefLabel, None) in proj
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj
    # interior terms are OPAQUE — none leak into the projection
    for interior_type in (ILADUB.CandidateConcept, ILADUB.PromotionDecision, ILADUB.SourceRegion, ILADUB.GroundedNode):
        assert not any(proj.subjects(RDF.type, interior_type)), interior_type


def _proj_shapes_knowledge():
    shapes = Graph().parse(os.path.join(SH_DIR, "etkl-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    return shapes, knowledge


def test_conformant_projection_passes_shape():
    shapes, knowledge = _proj_shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "examples", "federation", "projection-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_leaky_projection_fails_shape():
    shapes, knowledge = _proj_shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "tests", "federation-projection-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
