"""Fluree f: enforcement compile: the governed ODRL tag-policy compiled to a data-driven
Fluree f:AccessPolicy, and certified faithful (f: grants == ODRL grants), no server.
See docs/superpowers/specs/2026-07-25-fluree-f-enforcement-design.md."""
import os
from rdflib import Graph, Namespace, RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")


def test_grantstag_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.grantsTag, RDF.type, OWL.ObjectProperty) in g
