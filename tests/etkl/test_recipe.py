# tests/etkl/test_recipe.py
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.recipe import (UnpivotOp, StripAggregationOp, Recipe,
                                 grid_values, col_leaf_label)

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _grid():
    """Year stub + Region(N/S) pivot; 2 rows. Values: 2020->10,20 ; 2021->11,21."""
    g = Graph(); t = EX.tbl
    cols = [EX.c0, EX.c1, EX.c2]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hYear, 0, "Year", [cols[0]]); hdr(EX.hReg, 0, "Region", cols[1:])
    hdr(EX.hN, 1, "North", [cols[1]]); hdr(EX.hS, 1, "South", [cols[2]])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"2020": ["2020", "10", "20"], "2021": ["2021", "11", "21"]}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c, txt in zip(cols, vals[r]):
            e = EX["e_%s_%s" % (r, str(c)[-1])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    return g, t


def test_col_leaf_label():
    g, t = _grid()
    assert col_leaf_label(g, EX.c1) == "North"
    assert col_leaf_label(g, EX.c0) == "Year"


def test_grid_values():
    g, t = _grid()
    gv = grid_values(g, t)
    assert gv[("2020", "North")] == "10"
    assert gv[("2021", "South")] == "21"
    assert gv[("2020", "Year")] == "2020"
    assert len(gv) == 6                                   # 2 rows x 3 cols


def test_recipe_is_ordered():
    r = Recipe((UnpivotOp("Region", "Year"), StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    assert [type(o).__name__ for o in r.operations] == ["UnpivotOp", "StripAggregationOp"]


def test_col_leaf_label_deepest_wins():
    """I1 regression: when a column has both a level-0 single-covering spanning header
    AND a level-1 leaf header, col_leaf_label must return the deepest one (level-1)."""
    g = Graph()
    c = EX.c_single

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l")
        g.add((lc, TAB.cellText, Literal(lbl)))
        g.add((u, TAB.hasLabel, lc))
        for col in covers:
            g.add((u, TAB.coversColumn, col))

    # level-1 leaf header covering the single column → label "Leaf"  (inserted first)
    hdr(EX.hLeaf, 1, "Leaf", [c])
    # level-0 spanning header that happens to span exactly one column → label "Span" (inserted last)
    # Without the max-level fix, last-wins returns "Span" — the wrong answer.
    hdr(EX.hSpan, 0, "Span", [c])

    # deepest (highest headerLevel) single-covering header must win
    assert col_leaf_label(g, c) == "Leaf"
