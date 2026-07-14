# tests/etkl/test_reshape_recover.py
import pytest
from rdflib import RDF, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


def test_recover_recipe_and_base_region(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.recipe import UnpivotOp
    from iladub.etkl.reshape import recover_recipe, recover_base
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    recipe = recover_recipe(rep.graph, t)
    unpivots = [o for o in recipe.operations if isinstance(o, UnpivotOp)]
    assert any(o.dimension == "Region" and o.stub == "Year" for o in unpivots)
    base = recover_base(rep.graph, t, recipe)
    assert len(base) == 8                                  # 2 years x 4 regions
    measures = sorted(row["__measure__"] for row in base)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    north_2020 = next(r for r in base if r["Region"] == "North" and r["Year"] == "2020")
    assert north_2020["__measure__"] == 10


def test_recover_strip_ops_from_totals(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import totals_table_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.recipe import StripAggregationOp
    from iladub.etkl.reshape import recover_recipe
    p = tmp_path / "t.pdf"; totals_table_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.RecordTable))
    recipe = recover_recipe(rep.graph, t)
    strips = [o for o in recipe.operations if isinstance(o, StripAggregationOp)]
    assert strips and any(o.function == "sum" for o in strips)


def test_materialize_recipe_serializes_strip_params():
    from rdflib import Graph, URIRef, Literal
    from iladub.etkl.reshape import _materialize_recipe
    from iladub.etkl.recipe import Recipe, UnpivotOp, StripAggregationOp
    g = Graph(); t = URIRef("https://example.org/d#tbl")
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    ru = _materialize_recipe(g, t, recipe)
    # find the strip op node
    strip = None
    for op in g.objects(ru, TAB.hasOperation):
        if (op, __import__("rdflib").RDF.type, TAB.StripAggregationOp) in g:
            strip = op
    assert strip is not None
    assert str(g.value(strip, TAB.opTargetLabel)) == "Total"
    assert {str(m) for m in g.objects(strip, TAB.opMember)} == {"North", "South"}
    assert str(g.value(strip, TAB.opFunction)) == "sum"
