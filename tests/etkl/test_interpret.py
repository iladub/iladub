import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")
QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")


def _named_region_pivot():
    """Region(North/South) pivoted across level-1 leaves under a level-0 'Region' header;
    Year stub column; two data rows 2020/2021. 4 measure cells → 4 base facts."""
    g = Graph(); t = EX.tbl
    c_year, c_north, c_south = EX.cYear, EX.cNorth, EX.cSouth
    for c in (c_year, c_north, c_south):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        if lbl is not None:
            lc = URIRef(str(u) + "l")
            g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(lbl)))
            g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hYear, 0, "Year", [c_year])
    hdr(EX.hRegion, 0, "Region", [c_north, c_south])       # named level-0 spanning header
    hdr(EX.hNorth, 1, "North", [c_north])
    hdr(EX.hSouth, 1, "South", [c_south])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"2020": {c_year: "2020", c_north: "10", c_south: "20"},
            "2021": {c_year: "2021", c_north: "11", c_south: "21"}}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c in (c_year, c_north, c_south):
            e = EX["e_%s_%s" % (r, str(c)[-5:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c))
            g.add((e, TAB.cellText, Literal(vals[r][c])))
    return g, t


def _recipe_graph_unpivot(dimension, stub):
    rg = Graph()
    op = EX.op0
    rg.add((op, RDF.type, TAB.UnpivotOp))
    rg.add((op, TAB.opIndex, Literal(0)))
    rg.add((op, TAB.opAxis, Literal("column")))
    rg.add((op, TAB.opDimension, Literal(dimension)))
    rg.add((op, TAB.opStub, Literal(stub)))
    return rg


def test_run_executes_construct_over_union():
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    facts = list(out.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 4                                  # 2 rows x 2 measure cols


def test_unpivot_inverse_yields_correct_coordinates():
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    # collect (measure, {(dimName, value), ...}) per fact
    got = set()
    for f in out.subjects(RDF.type, TAB.BaseFact):
        m = float(out.value(f, TAB.measureValue))
        coords = frozenset((str(out.value(co, TAB.dimensionName)), str(out.value(co, TAB.value)))
                           for co in out.objects(f, TAB.atDimensionValue))
        got.add((m, coords))
    assert (10.0, frozenset({("Region", "North"), ("Year", "2020")})) in got
    assert (21.0, frozenset({("Region", "South"), ("Year", "2021")})) in got
