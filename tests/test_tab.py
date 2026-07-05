"""Tabular-topology ontology (tab:) — vocabulary + SHACL verifier-core tests."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from pyshacl import validate

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


CONFORMANT = os.path.join(EX, "hierarchical-conformant.ttl")


def test_conformant_example_structure():
    g = _g(CONFORMANT)
    # 5 leaf columns, 2 leaf rows, 8 entry cells (cols c1..c4 x rows r0,r1)
    tbl = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(g.objects(tbl, TAB.hasLeafColumn))) == 5
    assert len(list(g.objects(tbl, TAB.hasLeafRow))) == 2
    assert len(list(g.subjects(RDF.type, TAB.EntryCell))) == 8


SHAPES = os.path.join(SH, "tab-shapes.ttl")


def _v(*data):
    c, _, t = validate(_g(*data), shacl_graph=_g(SHAPES), inference="rdfs", advanced=True)
    return c, t


def test_conformant_passes_tiling():
    c, t = _v(CONFORMANT)
    assert c, t


def test_uncovered_column_fails():
    c, t = _v(os.path.join(TST, "tab-uncovered-column-leak.ttl"))
    assert not c
    assert "CoverageShape" in t


def test_overlapping_headers_fail():
    c, t = _v(os.path.join(TST, "tab-overlap-leak.ttl"))
    assert not c
    assert "NoOverlapShape" in t


def test_refinement_break_fails():
    c, t = _v(os.path.join(TST, "tab-refinement-leak.ttl"))
    assert not c
    assert "RefinementShape" in t


def test_multitable_coverage_gap_fails():
    """A coverage gap in one table must NOT be silenced by another table's header."""
    c, t = _v(os.path.join(TST, "tab-multitable-coverage-leak.ttl"))
    assert not c
    assert "CoverageShape" in t


def test_orphan_entry_fails():
    """An entry cell whose column is not a leaf column of its table must fail."""
    c, t = _v(os.path.join(TST, "tab-orphan-entry-leak.ttl"))
    assert not c
    assert "EntryColumnBoundShape" in t


def test_ambiguous_access_fails():
    """A leaf column with two leaf-headers (ambiguous column path) must fail."""
    c, t = _v(os.path.join(TST, "tab-ambiguous-access-leak.ttl"))
    assert not c
    assert "UnambiguousAccessShape" in t


def test_conformant_passes_full_verifier():
    """The conformant example passes ALL shapes together (tiling + access)."""
    c, t = _v(CONFORMANT)
    assert c, t


def test_entry_cardinality_fails():
    """An entry cell with two atColumn violates the exactly-one cardinality."""
    c, t = _v(os.path.join(TST, "tab-cardinality-leak.ttl"))
    assert not c
    assert "EntryCellShape" in t
