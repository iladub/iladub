import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SKOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")


def test_ontology_parses_and_defines_organ():
    g = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    assert (TX.Organ, RDF.type, None) in {(s, p, None) for s, p, _ in g}


def test_terms_have_four_abo_concepts():
    g = Graph().parse(os.path.join(TXD, "transplant-terms.ttl"), format="turtle")
    abo = [s for s in g.subjects(SKOS.inScheme, TX["scheme-abo"])]
    assert len(abo) == 4, abo
