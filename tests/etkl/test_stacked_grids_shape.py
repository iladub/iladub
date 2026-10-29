"""R74 Task 2: `tab:StackedGridsShape`, the membrane that disposes of every `tab:StackedGrids`
node the stack derivation mints. Synthetic only; each refusal is read by its own message.

A stack is two or more tables (K1), each a `tab:Table` (K2), each holding at least one
`tab:EntryCell`, and every entry cell of every member on one and the same page (K3). A table's
page is the page of its ENTRY cells (spec 2026-10-28 § 11.2 F1): a continuation table carries
the head page's `tab:LabelCell`s, so "any cell" would split a one-page stack across two pages.
"""
import os

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl import membrane

TAB = Namespace("https://w3id.org/iladub/tab#")
VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")
D = "urn:test:stack"

ENGINES = ["pyshacl"] + (["rudof"] if membrane.rudof_available() else [])

MSG_K1 = "(stack has fewer than two members)"
MSG_K2 = "(stack member is not a table)"
MSG_K3 = "(stack members are not on one page)"
ALL = (MSG_K1, MSG_K2, MSG_K3)


def _page(n):
    return Literal(n, datatype=XSD.integer)


def _stack(mutate=None):
    """Two `tab:HierarchicalTable`s, each with two entry cells on page 0 and one label cell on
    page 0, and one `tab:StackedGrids` node both are `tab:inStack` of.

    The miniature is NOT a conforming compile: its entry cells carry no `tab:atRow` /
    `tab:atColumn`, so `EntryCellShape` refuses them. As in `test_grid_index_shape.py`, every
    verdict here is read by THIS shape's own `sh:message` substrings, never by `conforms`.
    `mutate(g, stack, tables, cells)` breaks one thing; `cells[t]` is `[entry0, entry1, label]`."""
    g = Graph()
    stack = URIRef(f"{D}#stack")
    g.add((stack, RDF.type, TAB.StackedGrids))
    tables, cells = [], []
    for t in range(2):
        tbl = URIRef(f"{D}#htable{t}")
        g.add((tbl, RDF.type, TAB.HierarchicalTable))
        g.add((tbl, TAB.inStack, stack))
        mine = []
        for k, cls in enumerate((TAB.EntryCell, TAB.EntryCell, TAB.LabelCell)):
            c = URIRef(f"{D}#t{t}-c{k}")
            g.add((c, RDF.type, cls))
            g.add((c, TAB.onPage, _page(0)))
            g.add((tbl, TAB.hasCell, c))
            mine.append(c)
        tables.append(tbl)
        cells.append(mine)
    if mutate:
        mutate(g, stack, tables, cells)
    return g


def _verdict(g, engine):
    s = Graph().parse(os.path.join(VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    o = Graph().parse(os.path.join(VOCAB, "ontology", "tab.ttl"), format="turtle")
    return membrane.validate(g, s, o, engine=engine)


def _one_member(g, stack, tables, cells):
    g.remove((tables[1], TAB.inStack, stack))


def _second_member_on_page_1(g, stack, tables, cells):
    for c in cells[1][:2]:
        g.remove((c, TAB.onPage, None))
        g.add((c, TAB.onPage, _page(1)))


def _label_on_page_1(g, stack, tables, cells):
    """The F1 miniature: a continuation table carries a label cell from another page."""
    g.remove((cells[1][2], TAB.onPage, None))
    g.add((cells[1][2], TAB.onPage, _page(1)))


def _no_entry_cell(g, stack, tables, cells):
    for c in cells[1][:2]:
        g.remove((tables[1], TAB.hasCell, c))


@pytest.mark.parametrize("engine", ENGINES)
def test_a_worked_example_stack_conforms(engine):
    _, text = _verdict(_stack(), engine)
    assert not [m for m in ALL if m in text], text


@pytest.mark.parametrize("engine", ENGINES)
def test_b_a_one_member_stack_is_refused_by_k1(engine):
    _, text = _verdict(_stack(_one_member), engine)
    assert MSG_K1 in text, text


@pytest.mark.parametrize("engine", ENGINES)
def test_c_a_two_page_stack_is_refused_by_k3(engine):
    _, text = _verdict(_stack(_second_member_on_page_1), engine)
    assert MSG_K3 in text, text


@pytest.mark.parametrize("engine", ENGINES)
def test_d_f1_a_label_cell_on_another_page_does_not_split_the_stack(engine):
    """K3 reads ENTRY cells, not every cell (spec § 11.2 F1)."""
    _, text = _verdict(_stack(_label_on_page_1), engine)
    assert not [m for m in ALL if m in text], text


@pytest.mark.parametrize("engine", ENGINES)
def test_e_a_member_without_entry_cells_is_refused_by_k3(engine):
    _, text = _verdict(_stack(_no_entry_cell), engine)
    assert MSG_K3 in text, text


def _member_not_a_table(g, stack, tables, cells):
    g.remove((tables[1], RDF.type, TAB.HierarchicalTable))
    g.add((tables[1], RDF.type, TAB.DataGrid))


@pytest.mark.parametrize("engine", ENGINES)
def test_f_a_member_that_is_not_a_table_is_refused_by_k2(engine):
    """Beyond the brief's (a)-(e): pins K2, whose pass in (a) rests on the membrane's subclass
    closure reading `tab:HierarchicalTable rdfs:subClassOf tab:Table` out of tab.ttl."""
    _, text = _verdict(_stack(_member_not_a_table), engine)
    assert MSG_K2 in text, text
