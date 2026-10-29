"""stacked-grids.rq — the derivation that names a stack of tables on one page (R74).

Hand-built graphs only; no corpus. Each graph states exactly the facts the query is allowed to
read — `tab:continuesTable`, `tab:hasCell`, an explicit `rdf:type tab:EntryCell` /
`tab:LabelCell`, and `tab:onPage` — so every test is a statement about the query, not about a
producer. A table's page is the page of its ENTRY cells (spec 2026-10-28 § 11.2 F1, ruled Q1
arm (a)): test (c) is the graincorp-stem miniature that tells that rule apart from "any cell".

Every table gets TWO entry cells on its page (and label cells, where present, get two as well),
so each page-equality join in the query multiplies rows. CONSTRUCT dedupes triples; the exact
triple counts below are what prove the multiplication mints nothing spurious.
"""
import os

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, XSD

from iladub.etkl import interpret

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RQ = os.path.join(ROOT, "vocab", "queries", "stacked-grids.rq")
TAB_TTL = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")
TAB_SHAPES = os.path.join(ROOT, "vocab", "shapes", "tab-shapes.ttl")

TAB = Namespace("https://w3id.org/iladub/tab#")
SH = Namespace("http://www.w3.org/ns/shacl#")
DOC = Namespace("https://example.org/doc/")


def _page(n):
    return Literal(n, datatype=XSD.integer)


def _table(g, name, entry_page, label_page=None, entries=2, labels=2):
    """Add table `name` with `entries` EntryCells on `entry_page` and, if `label_page` is
    given, `labels` LabelCells on it. Returns the table IRI."""
    t = DOC[name]
    g.add((t, RDF.type, TAB.HierarchicalTable))
    for i in range(entries):
        c = DOC[f"{name}-e{i}"]
        g.add((t, TAB.hasCell, c))
        g.add((c, RDF.type, TAB.EntryCell))
        g.add((c, TAB.onPage, _page(entry_page)))
    if label_page is not None:
        for i in range(labels):
            c = DOC[f"{name}-l{i}"]
            g.add((t, TAB.hasCell, c))
            g.add((c, RDF.type, TAB.LabelCell))
            g.add((c, TAB.onPage, _page(label_page)))
    return t


def _stacks(out):
    """{stack IRI: frozenset(member IRIs)} read off the CONSTRUCT output."""
    return {s: frozenset(out.subjects(TAB.inStack, s))
            for s in out.subjects(RDF.type, TAB.StackedGrids)}


def _only_stack_vocabulary(out):
    """Nothing but (S a tab:StackedGrids) and (m tab:inStack S): no label, no provenance."""
    for s, p, o in out:
        assert (p == RDF.type and o == TAB.StackedGrids) or p == TAB.inStack, (s, p, o)


def test_a_two_tables_on_one_page_make_one_stack_of_three_triples():
    g = Graph()
    a = _table(g, "A", 0, label_page=0)
    b = _table(g, "B", 0, label_page=0)
    g.add((b, TAB.continuesTable, a))
    out = interpret.run(RQ, g)
    assert len(out) == 3
    _only_stack_vocabulary(out)
    stacks = _stacks(out)
    assert list(stacks.values()) == [frozenset({a, b})]
    # the stack is named from its head, A
    (s,) = stacks
    assert s == URIRef(str(a) + "-stack")


def test_b_a_four_table_run_on_one_page_is_one_stack_of_five_triples():
    """cbh's shape: four tables on page 0, each continuing the one before."""
    g = Graph()
    ts = [_table(g, n, 0, label_page=0) for n in ("T1", "T2", "T3", "T4")]
    for prev, cur in zip(ts, ts[1:]):
        g.add((cur, TAB.continuesTable, prev))
    out = interpret.run(RQ, g)
    assert len(out) == 5
    _only_stack_vocabulary(out)
    stacks = _stacks(out)
    assert len(stacks) == 1
    assert len(list(out.subject_objects(TAB.inStack))) == 4
    assert list(stacks.values()) == [frozenset(ts)]
    assert list(stacks) == [URIRef(str(ts[0]) + "-stack")]


def test_c_a_cross_page_link_whose_continuation_carries_head_labels_is_no_stack():
    """graincorp-stem miniature (spec § 11.2 F1): B's entries are on page 1, but B holds A's
    LabelCells on page 0. Reading "any cell" would put A and B on page 0 together."""
    g = Graph()
    a = _table(g, "A", 0, label_page=0)
    b = _table(g, "B", 1, label_page=0)
    g.add((b, TAB.continuesTable, a))
    out = interpret.run(RQ, g)
    assert len(out) == 0


def test_d_a_chain_crossing_a_page_contributes_only_its_same_page_run():
    """A (p0) <- B (p1) <- C (p1); B carries A's labels on page 0. One stack {B, C}, head B."""
    g = Graph()
    a = _table(g, "A", 0, label_page=0)
    b = _table(g, "B", 1, label_page=0)
    c = _table(g, "C", 1, label_page=0)
    g.add((b, TAB.continuesTable, a))
    g.add((c, TAB.continuesTable, b))
    out = interpret.run(RQ, g)
    assert len(out) == 3
    _only_stack_vocabulary(out)
    stacks = _stacks(out)
    assert list(stacks.values()) == [frozenset({b, c})]
    assert list(stacks) == [URIRef(str(b) + "-stack")]


def test_e_a_link_whose_earlier_table_has_no_entry_cell_is_no_stack():
    g = Graph()
    a = _table(g, "A", 0, label_page=0, entries=0)
    b = _table(g, "B", 0, label_page=0)
    g.add((b, TAB.continuesTable, a))
    out = interpret.run(RQ, g)
    assert len(out) == 0


def test_f_the_derivation_is_deterministic():
    g = Graph()
    ts = [_table(g, n, 0, label_page=0) for n in ("T1", "T2", "T3")]
    for prev, cur in zip(ts, ts[1:]):
        g.add((cur, TAB.continuesTable, prev))
    first = interpret.run(RQ, g)
    second = interpret.run(RQ, g)
    assert isomorphic(first, second)
    assert set(first.subjects(RDF.type, TAB.StackedGrids)) == \
        set(second.subjects(RDF.type, TAB.StackedGrids))
    assert len(first) == 4


def test_g_continuestable_plus_does_not_carry_a_later_page_table_into_the_stack():
    """B (p1) <- C (p1) <- D (p2): D reaches the head B through tab:continuesTable+, but its
    entries are on page 2, so it is not a member. Two disjoint same-page runs on two pages each
    make their own stack: E (p2) continues D, so {D, E} is the page-2 stack."""
    g = Graph()
    b = _table(g, "B", 1)
    c = _table(g, "C", 1)
    d = _table(g, "D", 2, label_page=1)
    e = _table(g, "E", 2, label_page=1)
    g.add((c, TAB.continuesTable, b))
    g.add((d, TAB.continuesTable, c))
    g.add((e, TAB.continuesTable, d))
    out = interpret.run(RQ, g)
    _only_stack_vocabulary(out)
    assert sorted(_stacks(out).values(), key=sorted) == sorted(
        [frozenset({b, c}), frozenset({d, e})], key=sorted)
    assert len(out) == 6


def test_the_derived_stack_conforms_to_stacked_grids_shape():
    """The query's product crosses Task 2's membrane (K1-K3) on the cbh-shaped graph."""
    g = Graph()
    ts = [_table(g, n, 0, label_page=0) for n in ("T1", "T2", "T3", "T4")]
    for prev, cur in zip(ts, ts[1:]):
        g.add((cur, TAB.continuesTable, prev))
    out = interpret.run(RQ, g)
    assert len(_stacks(out)) == 1  # not vacuous: the shape has a focus node
    data = g + out
    shapes = Graph().parse(TAB_SHAPES, format="turtle")
    ont = Graph().parse(TAB_TTL, format="turtle")
    _, results, text = validate(data, shacl_graph=shapes, ont_graph=ont,
                                inference="rdfs", advanced=True)
    # The hand-built cells are minimal (no tab:atRow etc.), so other tab shapes report on
    # them; only results focused on the stack itself are this query's business.
    (stack,) = _stacks(out)
    on_stack = list(results.subjects(SH.focusNode, stack))
    assert on_stack == [], text
