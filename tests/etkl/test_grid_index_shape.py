"""Loop A task 1 (O8): the membrane refuses a grid whose row ordinals or column indices are
missing, doubled, shared, or mistyped. Synthetic only; each case is read by its own message."""
import os

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl import membrane

TAB = Namespace("https://w3id.org/iladub/tab#")
VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")
G = "urn:test:grid"

ENGINES = ["pyshacl"] + (["rudof"] if membrane.rudof_available() else [])

MSG_ROW_INDEX = "(grid row index)"
MSG_COL_INDEX = "(grid column index)"
MSG_ROW_SHARED = "(grid rows share an index)"
MSG_COL_SHARED = "(grid columns share an index)"
ALL = (MSG_ROW_INDEX, MSG_COL_INDEX, MSG_ROW_SHARED, MSG_COL_SHARED)


def _grid(mutate=None):
    """A grid of 2 rows and 2 columns with correct indices; `mutate(g, rows, cols)` breaks one."""
    g = Graph()
    grid = URIRef(G)
    g.add((grid, RDF.type, TAB.DataGrid))
    rows = [URIRef(f"{G}-r{i}") for i in range(2)]
    cols = [URIRef(f"{G}-c{k}") for k in range(2)]
    for i, r in enumerate(rows):
        g.add((r, RDF.type, TAB.LeafRow))
        g.add((grid, TAB.hasGridRow, r))
        g.add((r, TAB.rowIndex, Literal(i, datatype=XSD.nonNegativeInteger)))
    for k, c in enumerate(cols):
        g.add((c, RDF.type, TAB.GridColumn))
        g.add((grid, TAB.hasGridColumn, c))
        g.add((c, TAB.colIndex, Literal(k, datatype=XSD.integer)))
    if mutate:
        mutate(g, rows, cols)
    return g


def _verdict(g, engine):
    s = Graph().parse(os.path.join(VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    o = Graph().parse(os.path.join(VOCAB, "ontology", "tab.ttl"), format="turtle")
    _, text = membrane.validate(g, s, o, engine=engine)
    return text


def _no_row_idx(g, rows, cols):
    g.remove((rows[0], TAB.rowIndex, None))


def _two_row_idx(g, rows, cols):
    g.add((rows[0], TAB.rowIndex, Literal(7, datatype=XSD.nonNegativeInteger)))


def _shared_row_idx(g, rows, cols):
    g.remove((rows[1], TAB.rowIndex, None))
    g.add((rows[1], TAB.rowIndex, Literal(0, datatype=XSD.nonNegativeInteger)))


def _no_col_idx(g, rows, cols):
    g.remove((cols[0], TAB.colIndex, None))


def _shared_col_idx(g, rows, cols):
    g.remove((cols[1], TAB.colIndex, None))
    g.add((cols[1], TAB.colIndex, Literal(0, datatype=XSD.integer)))


def _row_idx_integer(g, rows, cols):
    g.remove((rows[0], TAB.rowIndex, None))
    g.add((rows[0], TAB.rowIndex, Literal(0, datatype=XSD.integer)))


CASES = [
    ("row missing its index", _no_row_idx, MSG_ROW_INDEX),
    ("row with two indices", _two_row_idx, MSG_ROW_INDEX),
    ("two rows sharing an index", _shared_row_idx, MSG_ROW_SHARED),
    ("column missing its index", _no_col_idx, MSG_COL_INDEX),
    ("two columns sharing an index", _shared_col_idx, MSG_COL_SHARED),
    ("row index typed xsd:integer", _row_idx_integer, MSG_ROW_INDEX),
]


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("name,mutate,msg", CASES, ids=[c[0] for c in CASES])
def test_a_broken_index_is_refused_by_its_own_message(engine, name, mutate, msg):
    text = _verdict(_grid(mutate), engine)
    assert msg in text, text


@pytest.mark.parametrize("engine", ENGINES)
def test_control_a_correctly_indexed_grid_raises_none_of_the_four(engine):
    text = _verdict(_grid(), engine)
    assert not [m for m in ALL if m in text], text


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
@pytest.mark.parametrize("engine", ENGINES)
def test_control_an_emitted_grid_raises_none_of_the_four(engine, tmp_path):
    from tests.etkl.test_datagrid import _emitted_conforming_grid
    g, _, _ = _emitted_conforming_grid(tmp_path)
    text = _verdict(g, engine)
    assert not [m for m in ALL if m in text], text


def test_the_datatype_refusal_lands_on_the_mistyped_row_only():
    """The case list above reads only a message, which a shape that refused EVERY row would also
    satisfy. Name the focus node: r0 is typed xsd:integer, r1 is correct."""
    text = _verdict(_grid(_row_idx_integer), "pyshacl")
    assert "Focus Node: <urn:test:grid-r0>" in text, text
    assert "Focus Node: <urn:test:grid-r1>" not in text, text
