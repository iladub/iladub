import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def test_hol_defines_event_and_lineage():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    assert (HOL.Event, RDF.type, OWL.Class) in g
    assert (HOL.condition, RDF.type, OWL.DatatypeProperty) in g
    assert (HOL.supersedes, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.triggeredBy, RDF.type, OWL.ObjectProperty) in g


def test_hol_shapes_still_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
