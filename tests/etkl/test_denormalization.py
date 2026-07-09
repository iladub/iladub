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
