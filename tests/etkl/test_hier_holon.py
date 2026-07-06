"""test_hier_holon — assert_hier_region: multi-level holon emission + SHACL conformance."""
import os
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph, URIRef, RDF
from pyshacl import validate
from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.holon import assert_hier_region, TAB

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SH = os.path.join(ROOT, "vocab", "shapes")
ONT = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SH, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SH, "tab-physical-shapes.ttl"), format="turtle")
    return g


def test_hier_holon_conforms(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    g = Graph()
    assert_hier_region(g, reg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    # two merged parents present in the graph
    parents = [s for s in g.subjects(RDF.type, TAB.HeaderNode)
               if len(list(g.objects(s, TAB.coversColumn))) >= 2]
    assert len(parents) == 2
    conforms, _, txt = validate(g, shacl_graph=_shapes(),
                                ont_graph=Graph().parse(ONT, format="turtle"),
                                inference="rdfs", advanced=True)
    assert conforms, txt


def test_hier_holon_has_leaf_columns_and_rows(tmp_path):
    """The emitted holon must have 7 leaf columns and 5 leaf rows for the pivot fixture."""
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    g = Graph()
    assert_hier_region(g, reg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    tbl = URIRef("urn:t")
    assert (tbl, RDF.type, TAB.HierarchicalTable) in g
    leaf_cols = list(g.objects(tbl, TAB.hasLeafColumn))
    leaf_rows = list(g.objects(tbl, TAB.hasLeafRow))
    assert len(leaf_cols) == 7, f"expected 7 leaf columns, got {len(leaf_cols)}"
    assert len(leaf_rows) == 5, f"expected 5 leaf rows, got {len(leaf_rows)}"


def test_hier_holon_returns_positive_token_count(tmp_path):
    """assert_hier_region returns the count of asserted body word tokens (> 0)."""
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    g = Graph()
    n = assert_hier_region(g, reg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    assert n > 0, "expected positive asserted body-token count"


def test_stub_column_promoted_to_level_zero(tmp_path):
    """Analyte (col 0, no merged parent) must be emitted as a level-0 HeaderNode.

    The conformant example shows stubs at level 0 covering only their own column.
    A parent=None node is a root by definition; emitting it at the maker's syntactic
    level would be structurally incorrect regardless of which SHACL shapes happen to
    fire.  The current shapes do not trigger on this node for the pivot fixture, but
    level-0 emission is semantically required — it is not a shape-coerced workaround.
    """
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    g = Graph()
    assert_hier_region(g, reg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    from rdflib.namespace import XSD
    from rdflib import Literal
    level0_nodes = [s for s in g.subjects(RDF.type, TAB.HeaderNode)
                    if (s, TAB.headerLevel, Literal(0, datatype=XSD.integer)) in g]
    # must be 3 level-0 nodes: Analyte (stub) + Current Visit + Prior Visit
    assert len(level0_nodes) == 3, (
        f"expected 3 level-0 HeaderNodes (stub + two merged parents), got {len(level0_nodes)}: "
        f"{[str(n) for n in level0_nodes]}"
    )
