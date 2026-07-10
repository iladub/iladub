# tests/etkl/test_reshape_certify.py
import pytest
from rdflib import RDF, Graph, Literal, Namespace, URIRef
TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
EX = Namespace("https://example.org/d#")


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


# ── FIX B: end-to-end strip-in-composition proof (A1.1) ─────────────────────

def _build_strip_composition_graph(col_add_order=None):
    """Construct the pivot+total graph: Region(North/South) spanning c1,c2; Total agg
    col c3=N+S; Year stub c0; two data rows 2020/2021.  Mirrors the pattern in
    test_denormalization::test_emit_base_facts_strips_aggregation_column.

    `col_add_order` controls the order the leaf columns are added to the graph (both
    Year c0 and Total c3 are level-0 single-leaf columns, so their relative order can
    influence stub selection — see the order-independence regression)."""
    g = Graph(); t = EX.tbl
    c0, c1, c2, c3 = EX.c0, EX.c1, EX.c2, EX.c3
    for c in (col_add_order or (c0, c1, c2, c3)):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l")
        g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(lbl)))
        g.add((u, TAB.hasLabel, lc))
        for col in covers:
            g.add((u, TAB.coversColumn, col))

    hdr(EX.hReg,  0, "Region", [c1, c2])
    hdr(EX.hN,    1, "North",  [c1])
    hdr(EX.hS,    1, "South",  [c2])
    hdr(EX.hYear, 0, "Year",   [c0])
    hdr(EX.hTot,  0, "Total",  [c3])

    rows = ["2020", "2021"]
    ru = {r: EX["r" + r] for r in rows}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))

    V = {"2020": {c0: "2020", c1: "10", c2: "20", c3: "30"},
         "2021": {c0: "2021", c1: "11", c2: "21", c3: "32"}}
    for r in rows:
        for c in (c0, c1, c2, c3):
            e = EX["e_%s_%s" % (r, str(c)[-2:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c))
            g.add((e, TAB.cellText, Literal(V[r][c])))

    return g, t


def test_certify_strip_in_composition_round_trips():
    """FIX B (A1.1): a pivoted report with a Total aggregation column round-trips through
    certify — unpivot lays the region cells, strip re-adds Total = sum(N, S), and the
    combined replay reproduces the original grid including the Total column.
    This is the primary A1 use of strip: excluding the total while inverting a pivot, then
    re-deriving it to prove the round-trip closed."""
    from iladub.etkl.reshape import certify, emit_normalized_base
    from iladub.etkl.recipe import UnpivotOp, StripAggregationOp

    g, t = _build_strip_composition_graph()

    recipe, verdict, base = certify(g, t)

    assert verdict.ok is True, verdict.residue
    assert verdict.residue == ()

    unpivots = [op for op in recipe.operations if isinstance(op, UnpivotOp)]
    strips   = [op for op in recipe.operations if isinstance(op, StripAggregationOp)]
    assert len(unpivots) == 1
    assert unpivots[0].dimension == "Region"
    assert any(op.function == "sum" for op in strips), strips

    # emit: 4 base facts (2 years × 2 regions); Total is NOT a base fact
    nb = emit_normalized_base(g, t)
    assert nb is not None
    facts = list(g.objects(nb, TAB.hasBaseFact))
    assert len(facts) == 4
    regions = {str(g.value(co, TAB.value))
               for f in facts
               for co in g.objects(f, TAB.atDimensionValue)
               if str(g.value(co, TAB.dimensionName)) == "Region"}
    assert "Total" not in regions
    assert regions == {"North", "South"}


def test_certify_stub_selection_is_order_independent():
    """FIX I2: stub selection must not depend on column insertion order. Both Year (c0)
    and Total (c3) are level-0 single-leaf columns; if the Total column is added BEFORE
    the Year stub, a stub-selector that treats every level-0 column as a candidate would
    pick 'Total' as the row-key stub → replay misses the Year cells → oracle fails.
    Excluding aggregation columns from stub candidacy makes 'Year' the stub regardless of
    order. (Fails before I2, passes after.)"""
    from iladub.etkl.reshape import certify, emit_normalized_base
    from iladub.etkl.recipe import UnpivotOp

    c0, c1, c2, c3 = EX.c0, EX.c1, EX.c2, EX.c3
    # Total (c3) inserted BEFORE Year stub (c0):
    g, t = _build_strip_composition_graph(col_add_order=(c3, c1, c2, c0))

    recipe, verdict, base = certify(g, t)
    assert verdict.ok is True, verdict.residue

    unpivots = [op for op in recipe.operations if isinstance(op, UnpivotOp)]
    assert len(unpivots) == 1
    assert unpivots[0].stub == "Year"          # NOT "Total"

    nb = emit_normalized_base(g, t)
    assert nb is not None
    assert len(list(g.objects(nb, TAB.hasBaseFact))) == 4


# ── FIX A: pivotless table must not produce a false oracle failure ────────────

def test_certify_pivotless_table_no_false_residue(tmp_path):
    """FIX A: a pure-totals RecordTable (no column pivot) has no base to invert.
    certify must short-circuit and return ok=True, residue=() rather than running the
    oracle against an empty replay and falsely reporting every cell as missing.
    emit_normalized_base must return None (nothing to emit — the guard on empty base
    applies regardless)."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import totals_table_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.reshape import certify, emit_normalized_base
    p = tmp_path / "tt.pdf"; totals_table_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.RecordTable))
    recipe, verdict, base = certify(rep.graph, t)
    assert base == []
    assert verdict.ok is True
    assert verdict.residue == ()
    nb = emit_normalized_base(rep.graph, t)
    assert nb is None
