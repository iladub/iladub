"""Loop N — R35: subtotal confirmation over the LOGICAL table. Red until the
document-level pass lands."""
from rdflib import BNode, Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import cut_group_two_page_pdf

PROV = URIRef("http://www.w3.org/ns/prov#wasDerivedFrom")


def _member(g, table, page, rows, ncols=3):
    """One chain member in the compile's emission shape: leaf columns, leaf rows, entry cells
    with page + bbox provenance. `rows` is {row_index: {col_index: text}}."""
    g.add((table, RDF.type, TAB.HierarchicalTable))
    for c in range(ncols):
        cu = URIRef(f"{table}-c{c}")
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table, TAB.hasLeafColumn, cu))
    for r, cols in rows.items():
        ru = URIRef(f"{table}-r{r}")
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table, TAB.hasLeafRow, ru))
        for c, text in cols.items():
            e = URIRef(f"{table}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((table, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru))
            g.add((e, TAB.atColumn, URIRef(f"{table}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))


def _two_member_chain():
    """A chain whose BOTH members confirm a subtotal page-locally AND at document level.

    Columns: 0 = Mon, 1 = Port, 2 = Qty. Each page carries one voyage and its port total, so
    the page-local pass (loop I) derives a group on EACH table — the state task 3 must
    supersede rather than leave standing beside the logical table's own group set.
    """
    from iladub.etkl.document import _link_columns
    from iladub.etkl.rowgroups import derive_row_groups
    g = Graph()
    p0 = URIRef("urn:doc/p0#h0")
    p1 = URIRef("urn:doc/p1#h0")
    _member(g, p0, 0, {0: {0: "Jul", 1: "Mackay", 2: "100"},
                       1: {1: "Mackay Total", 2: "100"}})
    _member(g, p1, 1, {0: {0: "Aug", 1: "Geelong", 2: "150"},
                       1: {1: "Geelong Total", 2: "150"}})
    for t in (p0, p1):                       # what the per-page pass left behind
        arow = URIRef(f"{t}-r1")
        g.add((arow, RDF.type, TAB.AggregationRow))
        g.add((arow, RDF.type, TAB.DetectedAggregationRow))
        g.add((arow, TAB.aggregationFunction, Literal("sum")))
        g.add((arow, TAB.aggregates, URIRef(f"{t}-r0")))
        derive_row_groups(g, t, {1: (1, 2, (0,))})
    g.add((p1, TAB.continuesTable, p0))
    _link_columns(g, p1, p0)
    return g, p0, p1


def test_cut_group_subtotal_confirms_at_document_level(tmp_path):
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 2
    aggs = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
    # the page-1 subtotal is confirmed (page-locally it cannot be)
    p1_aggs = [a for a in aggs if "/p1" in str(a)]
    assert p1_aggs, "cut-group subtotal must confirm against page-0 members"
    # and its aggregates edges CROSS the member tables
    for a in p1_aggs:
        members = list(rep.graph.objects(a, TAB.aggregates))
        assert any("/p0" in str(m) for m in members), members


def test_chain_arithmetic_is_reported_honestly(tmp_path):
    """The reconciliation ledger (loop N): what the document window changed, counted.

    On the cut-group fixture the numbers are known exactly — page-locally the `SUB`/450 row
    cannot confirm (its only visible member is V3=200), and the logical table confirms it
    against all three voyages. So: 0 page-confirmed, 1 document-confirmed, 0 retracted,
    1 newly-confirmed, no abstention. Retraction being ZERO here is the honest half: the
    wider window ADDED a subtotal and took none away."""
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    (a,) = rep.arithmetic
    assert a.chain == rep.chains[0]
    assert (a.page_confirmed, a.document_confirmed, a.retracted, a.newly_confirmed) == \
           (0, 1, 0, 1), a
    assert a.abstained is None


def test_retracted_witness_takes_its_derived_group(tmp_path):
    """A derivation cannot outlive its ground (loop-N review M-1).

    Loop I derives a `tab:DerivedRowGroup` FROM a confirmed aggregation row. When the document
    window refuses that row, the group's witness is gone — and a stale group is a SILENT defect:
    no shape catches it (`tab:DerivedRowGroupShape` only requires the `prov:wasDerivedFrom` to
    exist) and the feed goes on keying records off it. So the retraction takes the group with it,
    and the ledger says how many.
    """
    import re
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import page_local_group_two_page_pdf
    pdf = str(tmp_path / "pagelocal.pdf")
    page_local_group_two_page_pdf(pdf)

    # page 1 STANDALONE: the subtotal confirms page-locally and loop I derives its group
    p1 = compile_tables(pdf, page_number=1)
    assert list(p1.graph.subjects(RDF.type, TAB.DetectedAggregationRow)), \
        "fixture precondition: the SUB row must confirm page-locally"
    assert list(p1.graph.subjects(RDF.type, TAB.DerivedRowGroup)), \
        "fixture precondition: loop I must derive a group off it"

    # document level: the wider window refuses the row (500 != 250) and withdraws the derivation
    rep = compile_document(pdf)
    (a,) = rep.arithmetic
    assert (a.page_confirmed, a.document_confirmed, a.retracted, a.newly_confirmed) == \
           (1, 0, 1, 0), a
    assert a.groups_retracted == 1, a
    assert not list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
    assert not list(rep.graph.subjects(RDF.type, TAB.AggregationRow))
    assert not list(rep.graph.subjects(RDF.type, TAB.DerivedRowGroup))
    # and nothing DANGLES: no triple anywhere still mentions the withdrawn group node
    stale = [t for t in rep.graph if any(re.search(r"-rg\d+$", str(x)) for x in t)]
    assert not stale, stale


def test_cut_group_derives_its_group_on_the_head_across_the_break(tmp_path):
    """R35's second half: the group the pagination CUT is derived over the logical table.

    The subtotal confirms only at document level (the fixture's point), so the group it
    witnesses can only be derived there too — and its members are on BOTH pages. Two things
    are asserted that a page-local derivation cannot produce: the group hangs off the CHAIN'S
    HEAD, and its `tab:coversRow` edges cross into the other member table."""
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    head = rep.chains[0][0]
    groups = list(rep.graph.subjects(RDF.type, TAB.DerivedRowGroup))
    assert len(groups) == 1, groups
    grp = groups[0]
    assert (head, TAB.hasHeaderNode, grp) in rep.graph, grp
    label = rep.graph.value(grp, TAB.hasLabel)
    assert str(rep.graph.value(label, TAB.cellText)) == "Mackay"
    covers = set(rep.graph.objects(grp, TAB.coversRow))
    assert any("/p0" in str(m) for m in covers) and any("/p1" in str(m) for m in covers), covers
    # and the members are exactly the witness's document-level operands
    witness = rep.graph.value(grp, PROV)
    assert covers == set(rep.graph.objects(witness, TAB.aggregates))
    (a,) = rep.arithmetic
    assert (a.groups_retracted, a.groups_superseded, a.groups_derived) == (0, 0, 1), a


def test_page_groups_are_superseded_by_the_logical_ones(tmp_path):
    """ONE truth about a chain's row groups — the supersession decision, pinned.

    Both members confirm page-locally here, so nothing is orphaned (`groups_retracted` 0) and
    the page-derived groups would otherwise SURVIVE beside the document-level ones: two
    parallel group sets over one row axis, and the feed picking between them by iteration
    order. The pass withdraws the page-local set (counted) and re-derives over the logical
    table, attached to the head.
    """
    from iladub.etkl.document import reconcile_chain_arithmetic
    g, p0, p1 = _two_member_chain()
    assert len(list(g.subjects(RDF.type, TAB.DerivedRowGroup))) == 2   # precondition
    a = reconcile_chain_arithmetic(g, (p0, p1))
    assert (a.page_confirmed, a.document_confirmed, a.retracted, a.newly_confirmed) == \
           (2, 2, 0, 0), a
    assert (a.groups_retracted, a.groups_superseded, a.groups_derived) == (0, 2, 2), a
    groups = list(g.subjects(RDF.type, TAB.DerivedRowGroup))
    assert len(groups) == 2, groups
    # every surviving group belongs to the HEAD — the logical table's, not a page's
    assert all((p0, TAB.hasHeaderNode, grp) in g for grp in groups), groups
    assert not list(g.objects(p1, TAB.hasHeaderNode))
    # keys are still read positionally from the members' own cells
    assert {str(g.value(g.value(grp, TAB.hasLabel), TAB.cellText)) for grp in groups} == \
           {"Mackay", "Geelong"}


def test_the_re_derivation_leaves_no_stale_level_or_member(tmp_path):
    """Task-2 report appendix (c) and (d), made MOOT for chains rather than patched.

    (c) a surviving sibling's `tab:headerLevel` could be one level too deep after a retraction,
        because the depth walk that produced it may have run through a node just removed;
    (d) a surviving group's `tab:coversRow` could record the OLD member set after the wider
        window rewrote its witness's `tab:aggregates`.
    Both were properties of groups that SURVIVE the pass. After task 3 no page-derived group
    survives a chain: the set is withdrawn and rebuilt in one derivation from the
    document-confirmed facts. So the invariant is checkable directly — every group in the graph
    covers exactly its witness's CURRENT operands, and carries a level from this derivation.

    `_retract_orphaned_groups` runs only from `reconcile_chain_arithmetic`, which runs only on
    chains — so there is nowhere left for either residue to be reachable.
    """
    from iladub.etkl.document import _link_columns, reconcile_chain_arithmetic
    from iladub.etkl.rowgroups import derive_row_groups
    # THE CONSTRUCTED DRIFT CASE. Page 0 carries a Mackay voyage whose measure cell is the
    # author's '-' — a member of any enclosing group (it has a cell in the measure column) that
    # contributes NOTHING to the sum. So page 1's 'Mackay Total' = 150 confirms page-locally
    # over {p1-r0} AND at document level over {p0-r0, p1-r0}: the row SURVIVES the wider window
    # with a REWRITTEN operand set, which is exactly the state appendix (d) described.
    g = Graph()
    p0, p1 = URIRef("urn:doc/p0#h0"), URIRef("urn:doc/p1#h0")
    _member(g, p0, 0, {0: {0: "Jul", 1: "Mackay", 2: "-"}})
    _member(g, p1, 1, {0: {0: "Aug", 1: "Mackay", 2: "150"},
                       1: {1: "Mackay Total", 2: "150"}})
    arow = URIRef(f"{p1}-r1")
    g.add((arow, RDF.type, TAB.AggregationRow))
    g.add((arow, RDF.type, TAB.DetectedAggregationRow))
    g.add((arow, TAB.aggregationFunction, Literal("sum")))
    g.add((arow, TAB.aggregates, URIRef(f"{p1}-r0")))
    derive_row_groups(g, p1, {1: (1, 2, (0,))})
    g.add((p1, TAB.continuesTable, p0))
    _link_columns(g, p1, p0)
    stale, = list(g.subjects(RDF.type, TAB.DerivedRowGroup))
    assert set(g.objects(stale, TAB.coversRow)) == {URIRef(f"{p1}-r0")}   # the page reading

    a = reconcile_chain_arithmetic(g, (p0, p1))
    assert a.abstained is None, a
    assert (a.retracted, a.groups_retracted, a.groups_superseded, a.groups_derived) == \
           (0, 0, 1, 1), a
    for grp in g.subjects(RDF.type, TAB.DerivedRowGroup):
        witness = g.value(grp, PROV)
        assert set(g.objects(grp, TAB.coversRow)) == set(g.objects(witness, TAB.aggregates))
        assert g.value(grp, TAB.headerLevel) is not None, grp
    # the rewritten total's group covers a row on the OTHER page — proof the set was rebuilt
    rebuilt = [grp for grp in g.subjects(RDF.type, TAB.DerivedRowGroup)
               if any("/p0" in str(m) for m in g.objects(grp, TAB.coversRow))
               and any("/p1" in str(m) for m in g.objects(grp, TAB.coversRow))]
    assert rebuilt, "the widened operand set must produce a cross-member group"


def test_an_abstaining_chain_keeps_its_page_groups(tmp_path):
    """Refusal is not a verdict (§7): a chain the pass cannot read unambiguously is left
    exactly as the per-page pass left it — including its page-derived groups. Nothing is
    superseded by a derivation that never ran."""
    from iladub.etkl.document import reconcile_chain_arithmetic
    g, p0, p1 = _two_member_chain()
    stray = URIRef(f"{p1}-rXX")                 # a row URI outside the minting convention
    g.add((p1, TAB.hasLeafRow, stray))
    a = reconcile_chain_arithmetic(g, (p0, p1))
    assert a.abstained is not None, a
    assert (a.groups_retracted, a.groups_superseded, a.groups_derived) == (0, 0, 0), a
    assert len(list(g.subjects(RDF.type, TAB.DerivedRowGroup))) == 2
    assert list(g.objects(p1, TAB.hasHeaderNode))     # the member keeps its own group


def test_continues_column_is_asserted_at_equal_index_only(tmp_path):
    """The committed column correspondence: one edge per column index the two tables SHARE,
    at equal index, and none where the evidence stops. An index present on one side only gets
    no edge — the law licensed a bijection, and asserting more would be fabrication (§7)."""
    from iladub.etkl.document import _link_columns
    g = Graph()
    p0, p1 = URIRef("urn:doc/p0#h0"), URIRef("urn:doc/p1#h0")
    _member(g, p0, 0, {0: {0: "a"}}, ncols=3)
    _member(g, p1, 1, {0: {0: "b"}}, ncols=2)
    assert _link_columns(g, p1, p0) == 2
    assert set(g.subject_objects(TAB.continuesColumn)) == {
        (URIRef(f"{p1}-c0"), URIRef(f"{p0}-c0")), (URIRef(f"{p1}-c1"), URIRef(f"{p0}-c1"))}


def test_single_page_and_case1_untouched(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf, two_page_unrelated_pdf
    p1 = str(tmp_path / "single.pdf"); simple_table_pdf(p1)
    single, doc = compile_tables(p1), compile_document(p1)
    assert doc.score == single.score
    # the reconciliation pass must not touch a single-page document's typing
    # (URIs are page-scoped in the driver, so compare counts, not subjects):
    assert len(list(doc.graph.subjects(RDF.type, TAB.DetectedAggregationRow))) == \
           len(list(single.graph.subjects(RDF.type, TAB.DetectedAggregationRow)))
    assert doc.arithmetic == ()   # a one-member chain is the page-local window: never re-run
    p2 = str(tmp_path / "unrel.pdf"); two_page_unrelated_pdf(p2)
    rep = compile_document(p2)
    assert rep.recognized == ()   # the document pass never runs across unrecognized pages
    assert rep.arithmetic == ()
