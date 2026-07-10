# tests/etkl/test_denorm_integration.py
import pytest
from rdflib import RDF, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


def test_analyze_yields_certified_recipe_and_projection(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import analyze
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    dr = analyze(rep)
    assert dr.oracle_ok and dr.residue == ()
    assert dr.normalized_base is not None
    assert (dr.normalized_base, RDF.type, TAB.NormalizedBase) in rep.graph
    # 8a behaviour preserved
    assert any(d.name == "Region" for d in dr.dimensions)
    assert len(dr.base_facts) == 8
