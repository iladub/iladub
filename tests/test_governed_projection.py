"""Governed / ViewerPass projection: a viewer-relative federation projection derived
under ODRL policy over concept sensitivity tags. AI-inherits-user via a SPARQL property
path. See docs/superpowers/specs/2026-07-25-governed-viewerpass-projection-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HVIEW = Namespace("http://w3id.org/holon/viewer/")


def test_governance_properties_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    for p in (ETKL.sensitivity, ETKL.hasRole, ETKL.forViewer):
        assert (p, RDF.type, OWL.ObjectProperty) in g, p


def test_hasrole_aligns_to_hview_viewerprofile():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.hasRole, RDFS.seeAlso, HVIEW.ViewerProfile) in g
