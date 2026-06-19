import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ILADUB = Namespace("https://w3id.org/etkl/iladub#")


def test_iladub_defines_extractor_property():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "iladub.ttl"), format="turtle")
    assert (ILADUB.extractor, RDF.type, OWL.DatatypeProperty) in g
