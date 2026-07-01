import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_hol_defines_process_and_milestone():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")
    assert (DEC.Process, RDF.type, OWL.Class) in g
    assert (DEC.Milestone, RDF.type, OWL.Class) in g
    assert (DEC.windowLimitMinutes, RDF.type, OWL.DatatypeProperty) in g


def test_hol_shapes_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")
