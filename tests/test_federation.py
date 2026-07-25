"""Compile→federate loop: a CleanDocumentHolon's projection becomes the next
document's provided terminology. See docs/superpowers/specs/2026-07-24-compile-federate-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HPROJ = Namespace("http://w3id.org/holon/projection/")


def test_document_projection_class_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDF.type, OWL.Class) in g


def test_document_projection_aligns_to_hproj():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDFS.subClassOf, HPROJ.Projection) in g
