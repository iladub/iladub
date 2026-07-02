import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_hol_defines_event_and_lineage():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")
    assert (DEC.Event, RDF.type, OWL.Class) in g
    assert (DEC.condition, RDF.type, OWL.DatatypeProperty) in g
    assert (DEC.supersedes, RDF.type, OWL.ObjectProperty) in g
    assert (DEC.triggeredBy, RDF.type, OWL.ObjectProperty) in g


def test_hol_shapes_still_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")
