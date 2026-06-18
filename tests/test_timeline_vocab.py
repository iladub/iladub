import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def test_hol_defines_process_and_milestone():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    assert (HOL.Process, RDF.type, OWL.Class) in g
    assert (HOL.Milestone, RDF.type, OWL.Class) in g
    assert (HOL.windowLimitMinutes, RDF.type, OWL.DatatypeProperty) in g


def test_hol_shapes_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
