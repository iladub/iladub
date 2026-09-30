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


# ------------------------------------------------------------------ U14, the log boundary (3d.2)
#
# Spec § 10.7 R-1, remedy (a), ruled 2026-09-29: `document._band_subgraph` does not traverse into
# a node the graph types `dec:DecisionHolon`. The statement triple (its subject is the table)
# still leaves with the table; the decision stays in the log. This is § 10.7's scratch probe
# (`probe_subgraph.py`) rebuilt as a test: a `ReadingRecorder` with two bands, and a table that
# does or does not carry the edge to one of its band's decisions. The merge-in half (the
# statement's object reaches the document graph after `/r2` / `/adopt`) needs the ask site and
# is written in 3d.6 (controller ruling, 2026-09-30).

_U14_DOC = URIRef("https://example.org/u14/doc")
_U14_T = URIRef("https://example.org/u14/doc#table3")


def _u14_page(*, edge: bool):
    """A page graph as `compile_tables` leaves it: the log (page process, two band processes,
    their judgements, options and the reader agent) beside table 3's own triples.

    Returns `(g, own, log, d)`. `own` is the exact set of triples minted under the table's URI
    space plus its BNode bbox — the value the null control is pinned to, written out here rather
    than snapshotted. `log` is every triple the recorder wrote. `d` is band 3's `header_lines`
    decision, the statement's object when `edge` is set."""
    from rdflib import BNode, XSD
    from iladub.etkl.decisionlog import ReadingRecorder
    g = Graph()
    rec = ReadingRecorder(g, _U14_DOC, 0)
    b3, b4 = rec.band(3), rec.band(4)
    b3.record("kind", ["RECORD_TABLE", "NON_TABLE"], "RECORD_TABLE", "U14 fixture")
    d = b3.record("header_lines", ["boxhead", "no_boxhead"], "no_boxhead", "U14 fixture")
    b3.record("verdict", ["asserted", "escalated", "ignored"], "asserted", "")
    b4.record("verdict", ["asserted", "escalated", "ignored"], "escalated", "U14 fixture")
    log = set(g)

    c0 = URIRef(f"{_U14_T}-c0")
    bbox = BNode()
    own = {
        (_U14_T, RDF.type, TAB.RecordTable),
        (_U14_T, TAB.hasLeafColumn, c0),
        (c0, RDF.type, TAB.LeafColumn),
        (c0, TAB.hasBBox, bbox),                    # a BNode must still ride along
        (bbox, RDF.type, TAB.BBox),
        (bbox, TAB.x0, Literal("1.5", datatype=XSD.decimal)),
    }
    for tr in own:
        g.add(tr)
    if edge:
        g.add((_U14_T, TAB.boxheadAbsentBy, d))
    return g, own, log, d


def _u14_pointed_into(g, sub):
    """Adoption's withdraw-or-refuse check (`compile_document`, the consumer of `_band_subgraph`
    over a pass-1 page graph), verbatim in shape: triples outside the subgraph that point into it."""
    nodes = set(sub.subjects())
    return [(s, p, n) for n in nodes for s, p in g.subject_predicates(n) if s not in nodes]


def test_u14_null_control_no_edge_is_pinned_by_value():
    from iladub.etkl.document import _band_subgraph
    g, own, _log, _d = _u14_page(edge=False)
    sub = _band_subgraph(g, _U14_T)
    assert set(sub) == own, (
        "without the edge, _band_subgraph must return exactly the table's own triples and its "
        f"BNode bbox — today's value. Extra: {set(sub) - own}; missing: {own - set(sub)}")
    assert _u14_pointed_into(g, sub) == []


def test_u14_the_edge_leaves_with_the_table_and_the_log_stays():
    from iladub.etkl.document import _band_subgraph
    g, own, log, d = _u14_page(edge=True)
    sub = _band_subgraph(g, _U14_T)
    statement = (_U14_T, TAB.boxheadAbsentBy, d)
    assert set(sub) == own | {statement}, (
        "with the edge, the subgraph must be the null control's value plus the statement triple "
        "and nothing else — the closure traversed into the decision log. Extra: "
        f"{sorted(map(str, {s for s, _, _ in set(sub) - own - {statement}}))}")
    outside = {s for s in sub.subjects()
               if isinstance(s, URIRef) and s != _U14_T and not str(s).startswith(f"{_U14_T}-")}
    assert outside == set(), f"subjects outside the table's URI space: {sorted(map(str, outside))}"
    assert _u14_pointed_into(g, sub) == [], (
        "adoption refuses a table that anything outside its subgraph points into; with the edge "
        "it must be withdrawable exactly when it is without it (spec § 10.7, U14)")
    g -= sub
    assert log <= set(g), (
        f"withdrawing the table deleted {len(log - set(g))} decision-log triple(s): the reader "
        "agent's and the page process's triples are shared by every decision on the page")
    assert (d, RDF.type, URIRef("https://w3id.org/iladub/dec#DecisionHolon")) in g
