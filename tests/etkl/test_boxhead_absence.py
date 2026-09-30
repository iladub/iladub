"""Box-split § 10 (Task 3d): a table the author drew with no boxhead says so.

Spec `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.3.1 / § 10.5. This file carries
U9–U14 as Task 3d's sub-tasks land; 3d.1 contributes U10, the statement's shapes.

U10 — the statement `tab:boxheadAbsentBy` and its four shapes' worth of consequences:

  1. leaf columns, 0 header nodes and the statement: `region_tiles` admits (the exemption guards
     on `tab:CoverageShape` / `tab:UnambiguousAccessShape`);
  2. the same without the statement: refused — today's refusal, unchanged;
  3. the statement plus one header node: refused (`tab:BoxheadAbsenceShape`, in the tiling gate),
     even though that header alone tiles the three columns;
  4. at compile scope, a statement whose object is not a `dec:DecisionHolon` that chose
     `no_boxhead` is refused (`tab:BoxheadAbsenceDecidedShape`), and one that did is admitted —
     the positive, without which a shape refusing everything would pass the negative.

Every case runs on BOTH engines (plan amendment A4): the tiling gate and `compile._validate`
select their engine per call from `ILADUB_MEMBRANE`, so each case is parametrized over it. A
rudof case skips without `pyrudof`, and a skip is not a pass.
"""
import importlib.util

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/u10#")

_ENGINES = [
    "pyshacl",
    pytest.param("rudof", marks=pytest.mark.skipif(
        importlib.util.find_spec("pyrudof") is None, reason="pyrudof not installed")),
]


@pytest.fixture(params=_ENGINES)
def engine(request, monkeypatch):
    monkeypatch.setenv("ILADUB_MEMBRANE", request.param)
    return request.param


def _table(g, *, statement_to=None, header=False):
    """A RecordTable with three leaf columns and one leaf row, as a RECORD region's scratch
    graph would carry them. `statement_to` adds `tab:boxheadAbsentBy`; `header` adds ONE level-0
    header node covering all three columns — a header that tiles the columns by itself, so case 3
    is refused by `tab:BoxheadAbsenceShape` alone and by nothing else."""
    t = EX.t
    g.add((t, RDF.type, TAB.RecordTable))
    for c in (EX.c0, EX.c1, EX.c2):
        g.add((c, RDF.type, TAB.LeafColumn))
        g.add((t, TAB.hasLeafColumn, c))
    g.add((EX.r0, RDF.type, TAB.LeafRow))
    g.add((t, TAB.hasLeafRow, EX.r0))
    if header:
        g.add((EX.h0, RDF.type, TAB.HeaderNode))
        g.add((EX.h0, TAB.headerLevel, Literal(0)))
        g.add((t, TAB.hasHeaderNode, EX.h0))
        for c in (EX.c0, EX.c1, EX.c2):
            g.add((EX.h0, TAB.coversColumn, c))
    if statement_to is not None:
        g.add((t, TAB.boxheadAbsentBy, statement_to))
    return g


# ------------------------------------------------------------------ U10, scratch (tiling gate)

def test_u10_1_statement_and_no_header_tiles(engine):
    from iladub.etkl.tiling import region_tiles
    g = _table(Graph(), statement_to=EX.d)
    assert region_tiles(g) is True, (
        f"[{engine}] a headerless table carrying tab:boxheadAbsentBy must tile: the exemption "
        f"guards on CoverageShape / UnambiguousAccessShape are missing or wrong")


def test_u10_2_no_statement_and_no_header_is_refused(engine):
    from iladub.etkl.tiling import region_tiles
    g = _table(Graph())
    assert region_tiles(g) is False, (
        f"[{engine}] a headerless table WITHOUT the statement must stay refused (today's refusal)")


def test_u10_3_statement_plus_a_header_is_refused(engine):
    from iladub.etkl.tiling import region_tiles
    control = _table(Graph(), header=True)
    assert region_tiles(control) is True, (
        f"[{engine}] precondition: the one header must tile the columns on its own, so that "
        f"case 3's refusal can only come from tab:BoxheadAbsenceShape")
    g = _table(Graph(), statement_to=EX.d, header=True)
    assert region_tiles(g) is False, (
        f"[{engine}] a table claiming no boxhead AND carrying a header node must be refused in "
        f"scratch — tab:BoxheadAbsenceShape is missing from the tiling gate")


# ------------------------------------------------------------------ U10, compile scope

def _logged(chosen):
    """A compile-scope graph: a real ReadingRecorder's log holding one `header_lines` decision
    that chose `chosen`, and a table whose statement points at it."""
    from iladub.etkl.decisionlog import ReadingRecorder
    g = Graph()
    brec = ReadingRecorder(g, URIRef("https://example.org/u10/doc"), 0).band(3)
    d = brec.record("header_lines", ["boxhead", "no_boxhead"], chosen,
                    "U10 fixture: the count the worker returned")
    _table(g, statement_to=d)
    return g, d


def test_u10_4_positive_a_no_boxhead_decision_is_admitted(engine):
    from iladub.etkl import compile as compile_mod
    g, _ = _logged("no_boxhead")
    ok, text, legs = compile_mod._validate(g)
    assert ok is True, f"[{engine}] a statement produced by a no_boxhead decision must cross: {text}"
    assert legs == ()


@pytest.mark.parametrize("case", ["chose_boxhead", "not_a_decision"])
def test_u10_4_negative_a_statement_without_a_no_boxhead_decision_is_refused(engine, case):
    from iladub.etkl import compile as compile_mod
    if case == "chose_boxhead":
        g, _ = _logged("boxhead")
    else:
        g, _ = _logged("no_boxhead")
        g.remove((EX.t, TAB.boxheadAbsentBy, None))
        g.add((EX.t, TAB.boxheadAbsentBy, URIRef("https://example.org/u10#bare")))
    ok, text, legs = compile_mod._validate(g)
    assert ok is False, (
        f"[{engine}] {case}: a statement whose object is not a no_boxhead decision must be "
        f"refused — a proposition passing as an assertion (CLAUDE.md § 3)")
    assert "tab" in legs
    assert "no_boxhead decision" in text, f"[{engine}] refused for the wrong reason: {text}"
