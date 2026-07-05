"""Tabular-topology ontology (tab:) — vocabulary + SHACL verifier-core tests."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")
EX = os.path.join(ROOT, "examples", "tables")
TST = os.path.join(ROOT, "tests")

TAB = Namespace("https://w3id.org/iladub/tab#")
TAB_TTL = os.path.join(ONT, "tab.ttl")


def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def test_tab_vocab_parses_and_declares_core_terms():
    g = _g(TAB_TTL)
    for cls in ["Table", "Cell", "LabelCell", "EntryCell", "HeaderNode",
                "LeafColumn", "LeafRow", "HierarchicalTable"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing class tab:{cls}"
    for prop in ["parentHeader", "coversColumn", "headerLevel", "hasHeaderNode",
                 "hasLeafColumn", "hasLeafRow", "hasCell", "atColumn", "atRow"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing property tab:{prop}"


def test_tab_core_is_standalone():
    """Core tab.ttl must not reference external namespaces as SUBJECTS (align-not-import)."""
    g = _g(TAB_TTL)
    forbidden = ("w3id.org/holon", "purl.org/linked-data/cube", "w3.org/ns/csvw",
                 "w3.org/ns/prov")
    for s in set(g.subjects()):
        assert not any(f in str(s) for f in forbidden), f"core references external subject {s}"
