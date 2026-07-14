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


def _recipe_graph_unpivot_with_row_strip(dimension, stub, target_label, members):
    rg = _recipe_graph_unpivot(dimension, stub)
    op = EX.op1
    rg.add((op, RDF.type, TAB.StripAggregationOp))
    rg.add((op, TAB.opIndex, Literal(1)))
    rg.add((op, TAB.opAxis, Literal("row")))
    rg.add((op, TAB.opFunction, Literal("sum")))
    rg.add((op, TAB.opTargetLabel, Literal(target_label)))
    for m in members:
        rg.add((op, TAB.opMember, Literal(m)))
    return rg


def test_unpivot_inverse_excludes_aggregate_row():
    """A 'Total' row (stub value 'Total') declared as a row StripAggregationOp target must
    NOT produce base facts — only the base rows 2020/2021 melt into facts."""
    import os
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    # add a Total row: stub 'Total', North=21, South=41
    tr = EX.rTotal
    g.add((tr, RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, tr))
    for c, txt in ((EX.cYear, "Total"), (EX.cNorth, "21"), (EX.cSouth, "41")):
        e = EX["e_total_%s" % str(c)[-5:]]
        g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
        g.add((e, TAB.atRow, tr)); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    rg = _recipe_graph_unpivot_with_row_strip("Region", "Year", "Total", ["2020", "2021"])
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    facts = list(out.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 4                                  # Total row excluded; 2020/2021 x North/South
    stubvals = {str(out.value(co, TAB.value))
                for f in facts for co in out.objects(f, TAB.atDimensionValue)
                if str(out.value(co, TAB.dimensionName)) == "Year"}
    assert stubvals == {"2020", "2021"}                     # no "Total" stub coordinate


def _projection_graph_region():
    """The 4-fact derived base for the Region×Year pivot, as native RDF (what unpivot-inverse
    produces). Measures: (2020,North)=10 (2020,South)=20 (2021,North)=11 (2021,South)=21."""
    p = Graph()
    facts = [("10", "North", "2020"), ("20", "South", "2020"),
             ("11", "North", "2021"), ("21", "South", "2021")]
    for i, (mv, region, year) in enumerate(facts):
        bf = EX["bf%d" % i]
        p.add((bf, RDF.type, TAB.BaseFact))
        p.add((bf, TAB.measureValue, Literal(mv, datatype=__import__("rdflib").namespace.XSD.decimal)))
        cd = EX["bf%d-dim" % i]; cs = EX["bf%d-stub" % i]
        p.add((bf, TAB.atDimensionValue, cd)); p.add((cd, TAB.dimensionName, Literal("Region"))); p.add((cd, TAB.value, Literal(region)))
        p.add((bf, TAB.atDimensionValue, cs)); p.add((cs, TAB.dimensionName, Literal("Year"))); p.add((cs, TAB.value, Literal(year)))
    return p


def _repro_dict(out):
    d = {}
    for cell in out.subjects(RDF.type, TAB.ReproCell):
        d[(str(out.value(cell, TAB.reproRow)), str(out.value(cell, TAB.reproCol)))] = str(out.value(cell, TAB.reproText))
    return d


def test_unpivot_forward_reconstructs_measure_and_stub_cells():
    import os
    from iladub.etkl import interpret
    p = _projection_graph_region()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-forward.rq"), p, rg)
    d = _repro_dict(out)
    assert float(d[("2020", "North")]) == 10.0
    assert float(d[("2021", "South")]) == 21.0
    assert d[("2020", "Year")] == "2020"                    # stub echo
    assert d[("2021", "Year")] == "2021"


def test_strip_forward_sum_readds_total_column():
    import os
    from iladub.etkl import interpret
    p = _projection_graph_region()
    rg = _recipe_graph_unpivot("Region", "Year")
    strip = EX.op1
    rg.add((strip, RDF.type, TAB.StripAggregationOp)); rg.add((strip, TAB.opIndex, Literal(1)))
    rg.add((strip, TAB.opAxis, Literal("column"))); rg.add((strip, TAB.opFunction, Literal("sum")))
    rg.add((strip, TAB.opTargetLabel, Literal("Total")))
    for m in ("North", "South"):
        rg.add((strip, TAB.opMember, Literal(m)))
    # forward strip runs over the repro grid produced by unpivot-forward
    grid = interpret.run(os.path.join(QUERIES, "unpivot-forward.rq"), p, rg)
    out = interpret.run(os.path.join(QUERIES, "strip-aggregation-forward-sum.rq"), grid, rg)
    d = _repro_dict(out)
    assert float(d[("2020", "Total")]) == 30.0              # 10 + 20
    assert float(d[("2021", "Total")]) == 32.0              # 11 + 21


def test_strip_forward_sum_row_axis_excludes_stub_column():
    """Regression (ported from the retired test_oracle row-axis guard): a row-axis sum strip
    must NOT write a total into any unpivot stub-echo column (numeric "Year"). Summing member
    rows ("2020","2021") across the "Year" stub-echo column would yield a spurious
    ("Total","Year")=4041 cell; the forward query must exclude every unpivot stub column."""
    import os
    from iladub.etkl import interpret
    p = _projection_graph_region()
    rg = _recipe_graph_unpivot("Region", "Year")
    strip = EX.op1
    rg.add((strip, RDF.type, TAB.StripAggregationOp)); rg.add((strip, TAB.opIndex, Literal(1)))
    rg.add((strip, TAB.opAxis, Literal("row"))); rg.add((strip, TAB.opFunction, Literal("sum")))
    rg.add((strip, TAB.opTargetLabel, Literal("Total")))
    for m in ("2020", "2021"):
        rg.add((strip, TAB.opMember, Literal(m)))
    grid = interpret.run(os.path.join(QUERIES, "unpivot-forward.rq"), p, rg)
    out = interpret.run(os.path.join(QUERIES, "strip-aggregation-forward-sum.rq"), grid, rg)
    d = _repro_dict(out)
    assert float(d[("Total", "North")]) == 21.0             # 10 + 11
    assert float(d[("Total", "South")]) == 41.0             # 20 + 21
    assert ("Total", "Year") not in d                       # stub-echo column excluded
