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
PHYS_SH = os.path.join(SH, "tab-physical-shapes.ttl")


def _v(*data):
    c, _, t = validate(_g(*data), shacl_graph=_g(SHAPES), inference="rdfs", advanced=True)
    return c, t


def _vp(*data_paths):
    """Validate data against topology + physical shapes together."""
    data = _g(*data_paths)
    shapes = _g(os.path.join(SH, "tab-shapes.ttl"), PHYS_SH)
    conforms, _, text = validate(data, shacl_graph=shapes, ont_graph=_g(TAB_TTL),
                                 inference="rdfs", advanced=True)
    return conforms, text


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


def test_orphan_row_fails():
    """An entry cell whose row is not a leaf row of its table must fail."""
    c, t = _v(os.path.join(TST, "tab-orphan-row-leak.ttl"))
    assert not c
    assert "EntryRowBoundShape" in t


def test_tab_physical_terms_present():
    g = _g(TAB_TTL)
    for cls in ["RecordTable", "BBox"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing class tab:{cls}"
    for prop in ["cellText", "onPage", "hasBBox", "x0", "y0", "x1", "y1", "hasLabel"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing property tab:{prop}"


def test_tab_recordtable_is_table_subclass():
    g = _g(TAB_TTL)
    assert (TAB.RecordTable, RDFS.subClassOf, TAB.Table) in g


def test_record_conformant_passes_physical():
    c, t = _vp(os.path.join(EX, "record-conformant.ttl"))
    assert c, t


def test_missing_physical_fails():
    c, t = _vp(os.path.join(TST, "tab-missing-physical-leak.ttl"))
    assert not c
    assert "EntryCellPhysicalShape" in t


def test_wrapped_conformant_passes(tmp_path=None):
    c, t = _vp(os.path.join(EX, "hier-physical-conformant.ttl"))
    assert c, t


def test_wrapped_leak_fails():
    c, t = _vp(os.path.join(TST, "tab-wrapped-leak.ttl"))
    assert not c
    assert "WrappedCellShape" in t


def test_tab_transposedtable_term():
    g = _g(TAB_TTL)
    assert (TAB.TransposedTable, RDF.type, OWL.Class) in g
    assert (TAB.TransposedTable, RDFS.subClassOf, TAB.Table) in g


def test_tab_sourceorientation_term():
    from rdflib import Namespace as _NS
    XSD = _NS("http://www.w3.org/2001/XMLSchema#")
    g = _g(TAB_TTL)
    assert (TAB.sourceOrientation, RDF.type, OWL.DatatypeProperty) in g
    assert (TAB.sourceOrientation, RDFS.domain, TAB.Table) in g
    assert (TAB.sourceOrientation, RDFS.range, XSD.string) in g


ROW_CONFORMANT = os.path.join(EX, "row-hierarchy-conformant.ttl")
ROW_NEGATIVE = os.path.join(EX, "row-hierarchy-negative.ttl")


def test_tab_coversrow_term():
    g = _g(TAB_TTL)
    assert (TAB.coversRow, RDF.type, OWL.ObjectProperty) in g
    assert (TAB.coversRow, RDFS.domain, TAB.HeaderNode) in g
    assert (TAB.coversRow, RDFS.range, TAB.LeafRow) in g


def test_row_hierarchy_conformant_passes():
    c, t = _v(ROW_CONFORMANT)
    assert c, t


def test_row_hierarchy_negative_fails():
    c, t = _v(ROW_NEGATIVE)
    assert not c


def test_existing_column_examples_still_pass_with_row_shapes():
    # the guarded row shapes must NOT break a table that has leaf rows but no row axis
    c, t = _v(CONFORMANT)
    assert c, t


PIVDIM_CONF = os.path.join(EX, "pivoted-dimension-conformant.ttl")
PIVDIM_NEG = os.path.join(EX, "pivoted-dimension-negative.ttl")


def test_tab_pivoted_dimension_terms():
    g = _g(TAB_TTL)
    assert (TAB.PivotedDimension, RDF.type, OWL.Class) in g
    for prop in ["dimensionName", "onAxis", "atLevel", "hasDimensionValue"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_pivoted_dimension_shapes():
    c, t = _v(PIVDIM_CONF); assert c, t
    c, t = _v(PIVDIM_NEG); assert not c


AGG_CONF = os.path.join(EX, "aggregation-conformant.ttl")
AGG_NEG = os.path.join(EX, "aggregation-negative.ttl")


def test_tab_aggregation_terms():
    g = _g(TAB_TTL)
    for cls in ["AggregationCell", "AggregationRow", "AggregationColumn"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing tab:{cls}"
    for prop in ["aggregationFunction", "aggregates", "overAxis"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_aggregation_shapes():
    c, t = _v(AGG_CONF); assert c, t
    c, t = _v(AGG_NEG); assert not c


BF_CONF = os.path.join(EX, "basefact-conformant.ttl")
BF_NEG = os.path.join(EX, "basefact-negative.ttl")


def test_tab_basefact_terms():
    g = _g(TAB_TTL)
    assert (TAB.BaseFact, RDF.type, OWL.Class) in g
    for prop in ["measureValue", "atDimensionValue", "value"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_qb_align_separate_and_core_standalone():
    core = _g(TAB_TTL)
    for _, _, o in core:
        assert "linked-data/cube" not in str(o), "core tab.ttl references qb:"
    align = _g(os.path.join(ONT, "tab-qb-align.ttl"))
    assert any("linked-data/cube" in str(o) for o in align.objects()), "align module missing qb:"


def test_basefact_shapes():
    c, t = _v(BF_CONF); assert c, t
    c, t = _v(BF_NEG); assert not c
