from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.denormalization import recover_dimensions, PivotedDimension

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _hdr(g, t, uri, level, label, covers_pred, leaves):
    g.add((uri, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, uri))
    g.add((uri, TAB.headerLevel, Literal(level)))
    lc = URIRef(str(uri) + "-lc"); g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(label)))
    g.add((uri, TAB.hasLabel, lc))
    for lf in leaves:
        g.add((uri, covers_pred, lf))


def _cols(g, t, n):
    cols = [EX["c%d" % i] for i in range(n)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    return cols


def test_spanning_parent_names_dimension():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, cols)
    for c, nm in zip(cols, ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    d = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    assert len(d) == 1 and d[0].name == "Region"
    assert set(d[0].values) == {"North", "South", "East", "West"}


def test_sibling_parents_are_values_unnamed():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hQ1, 0, "Q1", TAB.coversColumn, cols[:2])
    _hdr(g, t, EX.hQ2, 0, "Q2", TAB.coversColumn, cols[2:])
    for c, nm in zip(cols, ["Rev", "Cost", "Rev", "Cost"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = {d.level: d for d in recover_dimensions(g, t) if d.axis == "column"}
    assert dims[0].name is None and set(dims[0].values) == {"Q1", "Q2"}
    assert set(dims[1].values) == {"Rev", "Cost"}


def test_spanning_parent_with_stub_names_dimension():
    """Region (level 0, covers cols 1-4) + single-leaf stub Year (level 0, covers col 0).
    The multi-leaf parent Region, together with stub Year, covers all leaves → names the
    dimension below (North/South/East/West)."""
    g = Graph(); t = EX.tbl
    # col 0 = stub; cols 1-4 = data
    all_cols = [EX["c%d" % i] for i in range(5)]
    for c in all_cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    _hdr(g, t, EX.hYear,   0, "Year",   TAB.coversColumn, [all_cols[0]])
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, all_cols[1:])
    for c, nm in zip(all_cols[1:], ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    region_dim = next(d for d in dims if d.name == "Region")
    assert set(region_dim.values) == {"North", "South", "East", "West"}


def test_flat_level_is_value_dimension():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 3)
    for c, nm in zip(cols, ["Analyte", "Value", "Unit"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 0, nm, TAB.coversColumn, [c])
    d = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    assert len(d) == 1 and set(d[0].values) == {"Analyte", "Value", "Unit"}


def test_annotate_dimensions_writes_triples():
    from iladub.etkl.denormalization import recover_dimensions, annotate_dimensions
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, cols)
    for c, nm in zip(cols, ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = recover_dimensions(g, t)
    annotate_dimensions(g, t, dims)
    du = next(g.subjects(RDF.type, TAB.PivotedDimension))
    assert str(g.value(du, TAB.dimensionName)) == "Region"
    assert {str(v) for v in g.objects(du, TAB.hasDimensionValue)} == {"North", "South", "East", "West"}
    assert str(g.value(du, TAB.onAxis)) == "column"


def test_region_pivot_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from rdflib import RDF as _RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(_RDF.type, TAB.HierarchicalTable))
    # Region (level 0, multi-leaf) + Year stub (level 0, single-leaf) → Region names
    # the dimension of the level below; North/South/East/West are its values.
    region_dim = next(d for d in recover_dimensions(rep.graph, t) if d.name == "Region")
    assert set(region_dim.values) == {"North", "South", "East", "West"}


def _matrix_graph(rows, cols, V):
    g = Graph(); t = EX.tbl
    ru = {r: EX["r_" + r] for r in rows}; cu = {c: EX["c_" + c] for c in cols}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
    for c in cols:
        g.add((cu[c], RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, cu[c]))
    for r in rows:
        for c in cols:
            e = EX["e_%s_%s" % (r, c)]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, cu[c]))
            g.add((e, TAB.cellText, Literal(str(V[r][c]))))
    return g, t, ru, cu


def test_verify_group_functions():
    from iladub.etkl.denormalization import verify_group
    assert verify_group([6.0], [[1.0, 2.0, 3.0]]) == "sum"
    assert verify_group([2.0], [[1.0, 2.0, 3.0]]) == "mean"
    assert verify_group([1.0], [[1.0, 2.0, 3.0]]) == "min"
    assert verify_group([100.0], [[7.0, 3.0]]) is None      # no function matches


def test_detect_grand_totals():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    assert ru["Total"] in ev.agg_rows and ev.funcs[ru["Total"]] == "sum"
    assert cu["Total"] in ev.agg_cols and ev.funcs[cu["Total"]] == "sum"
    assert set(ev.base_rows) == {ru["North"], ru["South"]}
    assert set(ev.base_cols) == {cu["Q1"], cu["Q2"]}


def test_no_false_aggregation():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["A", "B", "C"]; cols = ["X", "Y", "Z"]
    V = {"A": {"X": 3, "Y": 7, "Z": 2}, "B": {"X": 9, "Y": 1, "Z": 5},
         "C": {"X": 4, "Y": 8, "Z": 6}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    assert not ev.agg_rows and not ev.agg_cols


def test_totals_fixture_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import totals_table_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import detect_aggregations
    from rdflib import RDF as _RDF
    p = tmp_path / "t.pdf"; totals_table_pdf(str(p))
    rep = compile_tables(str(p))
    tbl = next(rep.graph.subjects(_RDF.type, TAB.RecordTable))
    ev = detect_aggregations(rep.graph, tbl)
    assert ev.agg_rows and ev.agg_cols


def test_annotate_marks_aggregations():
    from iladub.etkl.denormalization import detect_aggregations, annotate_aggregations
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    annotate_aggregations(g, t, ev)
    assert (ru["Total"], RDF.type, TAB.AggregationRow) in g
    assert (cu["Total"], RDF.type, TAB.AggregationColumn) in g
    # the grand-total cell carries both axes
    e = next(e for e in g.subjects(RDF.type, TAB.AggregationCell)
             if g.value(e, TAB.atRow) == ru["Total"] and g.value(e, TAB.atColumn) == cu["Total"])
    assert {str(o) for o in g.objects(e, TAB.overAxis)} == {"row", "column"}


def test_no_false_aggregation_single_value_col():
    """A 2-col table (1 text + 1 numeric) must never flag a coincidental count match:
    the lone numeric value 2 == count([B,C]) would be a false positive without the
    >=2-numeric-evidence guard."""
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["A", "B", "C"]; cols = ["Label", "Score"]
    V = {"A": {"Label": "x", "Score": 2},
         "B": {"Label": "y", "Score": 100},
         "C": {"Label": "z", "Score": 999}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    assert not ev.agg_rows and not ev.agg_cols


def test_emit_base_facts_unpivots_region(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import emit_base_facts
    from rdflib import RDF as _RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(_RDF.type, TAB.HierarchicalTable))
    facts = emit_base_facts(rep.graph, t)
    assert len(facts) == 8                                   # 2 years x 4 regions (melted)
    measures = sorted(float(rep.graph.value(f, TAB.measureValue)) for f in facts)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    # each fact carries a Region coordinate and a Year coordinate
    f0 = next(f for f in facts if float(rep.graph.value(f, TAB.measureValue)) == 10.0)
    coords = {(str(rep.graph.value(co, TAB.dimensionName)), str(rep.graph.value(co, TAB.value)))
              for co in rep.graph.objects(f0, TAB.atDimensionValue)}
    assert ("Region", "North") in coords and ("Year", "2020") in coords


def test_analyze_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import analyze
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    dr = analyze(rep)
    assert any(d.name == "Region" for d in dr.dimensions)
    assert len(dr.base_facts) == 8
    assert (None, RDF.type, TAB.PivotedDimension) in rep.graph   # evidence annotated in place


def test_emit_base_facts_strips_aggregation_column():
    """A pivoted table with a Total aggregation column: Total is not a measure column,
    so no base fact references it."""
    from iladub.etkl.denormalization import emit_base_facts
    # constructed: column dim 'Region' over N/S (cols c1,c2) named by a spanning parent;
    # a 'Total' agg column (c3 = N+S); one stub col c0 'Year'; two rows.
    g = Graph(); t = EX.tbl
    c0, c1, c2, c3 = EX.c0, EX.c1, EX.c2, EX.c3
    for c in (c0, c1, c2, c3):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    # header tree: Region (level 0) spans c1,c2 ; N/S leaf labels (level 1); Year stub label on c0; Total on c3
    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l"); g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(lbl)))
        g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hReg, 0, "Region", [c1, c2]); hdr(EX.hN, 1, "North", [c1]); hdr(EX.hS, 1, "South", [c2])
    hdr(EX.hYear, 0, "Year", [c0]); hdr(EX.hTot, 0, "Total", [c3])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
    V = {"2020": {c0: "2020", c1: "10", c2: "20", c3: "30"},
         "2021": {c0: "2021", c1: "11", c2: "21", c3: "32"}}
    for r in rows:
        for c in (c0, c1, c2, c3):
            e = EX["e_%s_%s" % (r, str(c)[-2:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(V[r][c])))
    facts = emit_base_facts(g, t)
    assert len(facts) == 4                                   # 2 years x 2 regions; Total NOT a measure
    # no base fact has a Region coordinate of a value derived from the Total column
    regions = {str(g.value(co, TAB.value)) for f in facts for co in g.objects(f, TAB.atDimensionValue)
               if str(g.value(co, TAB.dimensionName)) == "Region"}
    assert regions == {"North", "South"}
