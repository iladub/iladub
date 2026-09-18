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


# R179: the membrane's label half. tab:EntryCellPhysicalShape required geometry of ENTRIES
# only, so R177's 79 boxless header LabelCells violated provenance-to-the-page with nothing
# validating it. The conformant example now carries three boxed labels AND the textless,
# boxless one (`span.build_reading`'s flank filler) that the shape must exempt.
def test_label_physical_conformant_passes():
    c, t = _vp(os.path.join(EX, "hier-physical-conformant.ttl"))
    assert c, t


def test_label_missing_box_leak_fails():
    c, t = _vp(os.path.join(TST, "tab-label-nobox-leak.ttl"))
    assert not c
    assert "LabelCellPhysicalShape" in t
    # BOTH halves must be reported — the fixture is missing a box on one label and a page
    # on another, and a merged constraint would surface only the first.
    assert "must carry a tab:hasBBox" in t
    assert "must carry a tab:onPage" in t


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


def test_tab_licence_refused_term():
    """LOOP O (R33) — the continuation licence's negative record is a COMMITTED term."""
    g = _g(TAB_TTL)
    assert (TAB.licenceRefused, RDF.type, OWL.ObjectProperty) in g
    assert (TAB.licenceRefused, RDFS.domain, TAB.Table) in g
    assert (TAB.licenceRefused, RDFS.range, TAB.Table) in g


def test_licence_refusal_and_stitch_are_exclusive():
    """A recognized pair is STITCHED or REFUSED, never both — the membrane refuses the
    contradiction. The positive side is the end-to-end one: a refused document's merged graph
    passes the whole-graph pass in
    tests/etkl/test_document.py::test_template_pages_are_refused_by_the_continuation_licence."""
    c, t = _v(os.path.join(TST, "tab-licence-refused-leak.ttl"))
    assert not c
    assert "LicenceRefusalShape" in t


# R211 (span donation, spec 2026-09-11 § 3.1) — the reading a SPANNING donor produces: every
# header node level 0, CHILDLESS, and covering MORE THAN ONE leaf column. No other example in
# this repo carries that combination (hierarchical-conformant.ttl's multi-column nodes all have
# children; its one childless node covers a single column). Span donation authors NO shape of
# its own — plan DECISION C — so what these three tests claim together is that the SHIPPED
# membrane already accepts the reading and already refuses both ways it can go wrong.
SPAN_CONFORMANT = os.path.join(EX, "span-donation-conformant.ttl")


def test_span_donation_reading_passes_tiling():
    """Three childless spanning nodes tile six leaf columns. tab:UnambiguousAccessShape
    DEFINES a leaf header as one nothing points at via tab:parentHeader, so this is the
    canonical shape it asks for, not one it tolerates."""
    c, t = _v(SPAN_CONFORMANT)
    assert c, t


def test_span_doubled_label_fails_both_shapes():
    """Two WORDS of one drawn interval emitted as two nodes — the one way this reading can go
    wrong when an interval holds more than one word. (MEASURED: graincorp's nine-words-for-
    nine-intervals is that document's coincidence, not a property of the relation, so the
    reading must join same-interval words rather than assume the 1:1.)

    BOTH shapes must fire, and that is what keeps this fixture from duplicating two that
    already exist: tab-overlap-leak.ttl fires NoOverlapShape alone on a single shared column,
    and tab-ambiguous-access-leak.ttl fires UnambiguousAccessShape alone on two leaf headers at
    DIFFERENT levels. Neither is a same-level double over a multi-column run."""
    c, t = _v(os.path.join(TST, "tab-span-doubled-label-leak.ttl"))
    assert not c
    assert "NoOverlapShape" in t
    assert "UnambiguousAccessShape" in t


def test_span_invented_child_fails_at_the_sibling_column():
    """DECISION C's "there are NO level-1 nodes", pinned. A second header level would be a node
    with no ink behind it (CLAUDE.md §7); mint one anyway and its spanning parent stops being a
    leaf header, leaving the parent's OTHER column with none at all.

    The focus node is asserted because the refusal is about the SIBLING, not the invented node
    — a test asserting only `not conforms` would pass against a membrane refusing this for any
    reason whatever, which is the fixture defect CLAUDE.md § Plan authoring records as defect 5.
    NoOverlapShape is asserted ABSENT for the same reason: it distinguishes this fixture's claim
    from the doubled-label one above."""
    c, t = _v(os.path.join(TST, "tab-span-invented-child-leak.ttl"))
    assert not c
    assert "UnambiguousAccessShape" in t
    assert "NoOverlapShape" not in t
    assert "ex:c1" in t, t


# ---------------------------------------------------------------------------
# R213 — ink the page does not show. tab:UnshownInk / tab:unshownText, the
# widened tab:WrappedCellShape (T1, O6) and tab:UnshownInkCellShape (T2, O4).
# ---------------------------------------------------------------------------

UNSHOWN_EX = os.path.join(EX, "unshown-ink-conformant.ttl")


def test_unshown_ink_terms_declared():
    g = _g(TAB_TTL)
    assert (TAB.UnshownInk, RDF.type, TAB.CellDatatype) in g
    # It abstains: a cell whose ink no reader can see must neither vote nor mismatch.
    assert (TAB.UnshownInk, TAB.datatypeAbstains, None) in g
    # It is in NO family -- unshown ink is not a kind of quantity, whatever it transcribes.
    assert (TAB.UnshownInk, TAB.inDatatypeFamily, None) not in g
    # It is NOT a nil spelling of tab:Blank: the author wrote something, the reader sees nothing.
    assert not any(str(o) for o in g.objects(TAB.UnshownInk, TAB.nilSpelling))
    # The transcription rides on the PERSISTED cell, so its domain is tab:EntryCell -- never
    # tab:GridCell, which is 0 triples in every compiled graph (RF1).
    assert (TAB.unshownText, RDF.type, OWL.DatatypeProperty) in g
    assert (TAB.unshownText, RDFS.domain, TAB.EntryCell) in g


def test_unshown_conformant_passes_both_membranes():
    """T1's blocking amendment: before it, RS1 measured this exact graph REFUSED."""
    c, t = _vp(UNSHOWN_EX)
    assert c, t


def test_unshown_cell_with_nonempty_celltext_fails():
    """O4: a cell cannot simultaneously be read and not read."""
    c, t = _vp(os.path.join(TST, "tab-unshown-ink-leak.ttl"))
    assert not c
    assert "UnshownInkCellShape" in t
    assert "must have an EMPTY tab:cellText" in t


def test_wrapped_guard_still_refuses_a_cell_carrying_neither(
):
    """O6 arm (a): the guard is WIDENED, not blinded. A dropped continuation carries
    neither property and is still refused -- this is tab-wrapped-leak.ttl unchanged."""
    c, t = _vp(os.path.join(TST, "tab-wrapped-leak.ttl"))
    assert not c
    assert "WrappedCellShape" in t


def test_wrapped_guard_still_refuses_an_empty_unshown_claim():
    """O6 arm (b): carriage CLAIMED and not delivered. This is the arm that separates the
    disjunct the spec required (§ 8.3) from the exemption it refused -- an exemption for
    'cells carrying tab:unshownText' would pass this graph."""
    c, t = _vp(os.path.join(TST, "tab-unshown-empty-leak.ttl"))
    assert not c
    assert "WrappedCellShape" in t
    # And the claim itself is refused where it is made, not only at the carriage guard.
    assert "UnshownInkCellShape" in t
    assert "exactly once and non-empty" in t
