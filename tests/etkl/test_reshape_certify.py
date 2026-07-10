# tests/etkl/test_reshape_certify.py
import pytest
from rdflib import RDF, Namespace, URIRef
TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def test_certify_region_pivot_passes(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.reshape import certify
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    recipe, verdict, base = certify(rep.graph, t)
    assert verdict.ok, verdict.residue
    assert len(base) == 8


def test_emit_normalized_base_is_derived_projection(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.reshape import emit_normalized_base
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p)); g = rep.graph
    t = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    nb = emit_normalized_base(g, t)
    assert nb is not None
    assert (nb, RDF.type, TAB.NormalizedBase) in g
    assert (nb, PROV.wasDerivedFrom, t) in g               # derivation, not stored ground truth
    assert g.value(nb, TAB.derivedByRecipe) is not None
    facts = list(g.objects(nb, TAB.hasBaseFact))
    assert len(facts) == 8
    measures = sorted(float(g.value(f, TAB.measureValue)) for f in facts)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    # coordinates preserved (supersedes emit_base_facts behaviour)
    f0 = next(f for f in facts if float(g.value(f, TAB.measureValue)) == 10.0)
    coords = {(str(g.value(co, TAB.dimensionName)), str(g.value(co, TAB.value)))
              for co in g.objects(f0, TAB.atDimensionValue)}
    assert ("Region", "North") in coords and ("Year", "2020") in coords


def test_emit_returns_none_on_oracle_failure(tmp_path):
    """If recovery is corrupted so the recipe cannot reproduce the grid, nothing is
    asserted (residue escalates instead)."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl import reshape
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p)); g = rep.graph
    t = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    # monkeypatch recover_base to drop a fact → replay can't reproduce that cell
    orig = reshape.recover_base
    reshape.recover_base = lambda gg, tt, rr: orig(gg, tt, rr)[:-1]
    try:
        nb = reshape.emit_normalized_base(g, t)
    finally:
        reshape.recover_base = orig
    assert nb is None
    assert (None, RDF.type, TAB.NormalizedBase) not in g
