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


def test_analyze_escalates_on_oracle_failure(tmp_path):
    """analyze() must escalate in-band when recover_base is corrupted so the recipe cannot
    round-trip: oracle_ok=False, residue non-empty, normalized_base=None, base_facts empty,
    and no tab:NormalizedBase node asserted in the graph."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl import reshape
    from iladub.etkl.denormalization import analyze
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    orig = reshape.derive_base
    def _drop_one(gg, tt, rr):
        p = orig(gg, tt, rr)
        facts = list(p.subjects(RDF.type, TAB.BaseFact))
        if facts:
            victim = facts[0]
            for pr, o in list(p.predicate_objects(victim)):
                p.remove((victim, pr, o))
        return p
    reshape.derive_base = _drop_one
    try:
        dr = analyze(rep)
    finally:
        reshape.derive_base = orig
    assert dr.oracle_ok is False
    assert len(dr.residue) > 0
    assert dr.normalized_base is None
    assert len(dr.base_facts) == 0
    assert (None, RDF.type, TAB.NormalizedBase) not in rep.graph
