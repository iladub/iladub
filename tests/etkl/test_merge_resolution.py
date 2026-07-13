"""Loop B1.1 — centering-bounded merge resolution. Behavior + no-regression + escalation."""
import os
import tempfile

from rdflib import RDF

from iladub.etkl import compile_tables
from iladub.etkl.holon import TAB, ILADUB
from tests.etkl import fixtures


def _compile(fixture_fn):
    path = os.path.join(tempfile.mkdtemp(), "t.pdf")
    fixture_fn(path)
    return compile_tables(path)


def column_tree(g, t):
    """{label: sorted(col ints)} for every header node of table t that covers columns."""
    def _label(h):
        return " ".join(str(x) for lc in g.objects(h, TAB.hasLabel)
                        for x in g.objects(lc, TAB.cellText))

    def _cols(h):
        return sorted(int(str(c).rsplit("-c", 1)[-1]) for c in g.objects(h, TAB.coversColumn))

    out = {}
    for h in g.objects(t, TAB.hasHeaderNode):
        cols = _cols(h)
        if cols:
            out[_label(h)] = cols
    return out


def _tree_of(fixture_fn):
    rep = _compile(fixture_fn)
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    return column_tree(rep.graph, t)


def test_no_regression_pivoted():
    tree = _tree_of(fixtures.pivoted_table_pdf)
    assert tree["Current Visit"] == [1, 2, 3]
    assert tree["Prior Visit"] == [4, 5, 6]


def test_no_regression_region_pivot():
    tree = _tree_of(fixtures.region_pivot_pdf)
    assert tree["Region"] == [1, 2, 3, 4]


def test_no_regression_crosstab():
    tree = _tree_of(fixtures.crosstab_table_pdf)
    assert tree["Q1"] == [1, 2, 3]
    assert tree["Q2"] == [4, 5, 6]
