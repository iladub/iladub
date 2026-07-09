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


def test_flat_level_is_value_dimension():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 3)
    for c, nm in zip(cols, ["Analyte", "Value", "Unit"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 0, nm, TAB.coversColumn, [c])
    d = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    assert len(d) == 1 and set(d[0].values) == {"Analyte", "Value", "Unit"}


def test_region_pivot_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from rdflib import RDF as _RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(_RDF.type, TAB.HierarchicalTable))
    # The hierarchical compiler orphan-promotes the Year stub to level 0 alongside
    # Region, so level 0 has two nodes (Year + Region) → both become VALUES at level 0,
    # and North/South/East/West become VALUES at level 1 (no pending_name from level 0).
    # repair_coverage ensures Region spans all 4 data columns (the 8-pre unblock),
    # making North/South/East/West fully recoverable as a column dimension.
    dims = [d for d in recover_dimensions(rep.graph, t) if d.axis == "column"]
    leaf_dim = next(d for d in dims if "North" in d.values)  # level-1 dimension
    assert set(leaf_dim.values) == {"North", "South", "East", "West"}
