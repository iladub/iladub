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

def _logged(chosen, judgement="header_lines"):
    """A compile-scope graph: a real ReadingRecorder's log holding one decision named
    `judgement` that chose `chosen`, and a table whose statement points at it."""
    from iladub.etkl.decisionlog import ReadingRecorder
    g = Graph()
    brec = ReadingRecorder(g, URIRef("https://example.org/u10/doc"), 0).band(3)
    d = brec.record(judgement, ["boxhead", "no_boxhead"], chosen,
                    "U10 fixture: the count the worker returned")
    _table(g, statement_to=d)
    return g, d


def test_u10_4_positive_a_no_boxhead_decision_is_admitted(engine):
    from iladub.etkl import compile as compile_mod
    g, _ = _logged("no_boxhead")
    ok, text, legs = compile_mod._validate(g)
    assert ok is True, f"[{engine}] a statement produced by a no_boxhead decision must cross: {text}"
    assert legs == ()


@pytest.mark.parametrize("case", ["chose_boxhead", "not_a_decision", "another_judgement"])
def test_u10_4_negative_a_statement_without_a_no_boxhead_decision_is_refused(engine, case):
    """Each negative differs from the admitted positive in ONE conjunct of the shape, so each
    pins that conjunct alone (review I1: a bare IRI with no triples was refused by the missing
    `dec:chosen` first, and left the type test unpinned).

    - `chose_boxhead`: the recorder's `header_lines` decision chose the other option.
    - `not_a_decision`: the recorder's own decision, chose `no_boxhead`, with ONLY its
      `rdf:type dec:DecisionHolon` triple removed.
    - `another_judgement`: a real decision that chose an option labelled `no_boxhead`, but it is
      not the `header_lines` judgement. `BandRecorder.record` names the judgement only through
      the decision's `rdfs:label` (controller ruling on review M1: I-10-3 says "iff a
      `header_lines` decision chose `no_boxhead`")."""
    from iladub.etkl import compile as compile_mod
    from iladub.etkl.decisionlog import DEC
    if case == "chose_boxhead":
        g, _ = _logged("boxhead")
    elif case == "not_a_decision":
        g, d = _logged("no_boxhead")
        assert (d, RDF.type, DEC.DecisionHolon) in g, "precondition: the recorder typed it"
        g.remove((d, RDF.type, DEC.DecisionHolon))
    else:
        g, _ = _logged("no_boxhead", judgement="row_role")
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


# ------------------------------------------------------------------ U11, emission (3d.3)
#
# Spec § 10.3.4 / § 10.5 U11, as amended by plan A1: `assert_record_region(…, header_lines,
# absent_by)`. The region is `test_holon._record_region`'s RECORD fixture (`simple_table_pdf`,
# band 1: `Analyte | Value | Unit` over three data rows). The default-path identity is checked
# against `u11-record-region-default.nt`, which the UNMODIFIED function produced once, at
# `4e6a284` (`git diff 84827f5 4e6a284 -- src/iladub/etkl/holon.py` is empty) — not by this test.

import os as _os

_U11_REF = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                         "u11-record-region-default.nt")
_U11_T = URIRef("https://example.org/u11/doc#table1")
_U11_DOC = URIRef("https://example.org/u11/doc")
_U11_D = URIRef("https://example.org/u11/doc#decision-header_lines")


def _u11_region(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import simple_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.regions import classify
    p = tmp_path / "x.pdf"; simple_table_pdf(str(p))
    return classify(detect_bands(text_lines(extract_words(str(p))))[1])


def _u11_emit(region, **kw):
    from iladub.etkl.holon import assert_record_region
    g = Graph()
    n = assert_record_region(g, region, _U11_T, _U11_DOC, 0, **kw)
    return g, n


def test_u11_default_call_is_the_unmodified_functions_graph(tmp_path):
    from rdflib.compare import isomorphic, graph_diff, to_isomorphic
    ref = Graph().parse(_U11_REF, format="nt")
    assert len(ref) == 175, "precondition: the committed reference is the 175-triple graph"
    g, n = _u11_emit(_u11_region(tmp_path))
    assert n == 9, "the default call still counts 3 data rows x 3 columns of entry cells"
    if not isomorphic(g, ref):
        _both, only_new, only_ref = graph_diff(to_isomorphic(g), to_isomorphic(ref))
        raise AssertionError(
            "the default call is no longer the unmodified function's graph (I-10-2). "
            f"Only in the new graph: {sorted(map(str, only_new))[:6]}; "
            f"only in the reference: {sorted(map(str, only_ref))[:6]}")


def test_u11_headerless_emission(tmp_path):
    from iladub.etkl.holon import TAB as HTAB
    g, n = _u11_emit(_u11_region(tmp_path), header_lines=0, absent_by=_U11_D)
    assert not list(g.subjects(RDF.type, HTAB.HeaderNode)), "no tab:HeaderNode with 0 header lines"
    assert not list(g.objects(_U11_T, HTAB.hasHeaderNode))
    assert not list(g.subjects(RDF.type, HTAB.LabelCell)), "no tab:LabelCell with 0 header lines"
    assert (_U11_T, HTAB.boxheadAbsentBy, _U11_D) in g, "the statement triple is missing"

    rows = set(g.objects(_U11_T, HTAB.hasLeafRow))
    assert rows == {URIRef(f"{_U11_T}-r{r}") for r in range(4)}, (
        f"one tab:LeafRow per row, row 0 included: {sorted(map(str, rows))}")
    assert all((r, RDF.type, HTAB.LeafRow) in g for r in rows)

    row0 = URIRef(f"{_U11_T}-r0")
    row0_texts = {str(g.value(e, HTAB.cellText)) for e in g.subjects(HTAB.atRow, row0)
                  if (e, RDF.type, HTAB.EntryCell) in g}
    assert row0_texts == {"Analyte", "Value", "Unit"}, f"row 0's cells are entries: {row0_texts}"
    assert n == 12, "the return value counts entry cells, and row 0's three are now entries"


def test_u11_headerless_graph_tiles(tmp_path):
    """The emitted headerless graph crosses the real scratch gate: it is exactly the shape the
    3d.1 exemption guards admit (U10 case 1), produced by the emitter rather than written by hand."""
    from iladub.etkl.tiling import region_tiles
    g, _ = _u11_emit(_u11_region(tmp_path), header_lines=0, absent_by=_U11_D)
    assert region_tiles(g) is True


@pytest.mark.parametrize("kw", [
    {"header_lines": 0},                                   # 0 without the decision
    {"absent_by": _U11_D},                                 # a decision with today's header
    {"header_lines": 1, "absent_by": _U11_D},
    {"header_lines": 2},                                   # the caller maps >= 1 to 1 (§ 10.6)
    {"header_lines": 2, "absent_by": _U11_D},
    {"header_lines": -1, "absent_by": _U11_D},
])
def test_u11_guard_refuses_an_inconsistent_call(tmp_path, kw):
    """The producer-side guard (CLAUDE.md § Producer-side guards): the membrane does not provably
    cover every product, because `tab:BoxheadAbsenceDecidedShape` binds only at compile scope. It
    fails fast, before any triple is written."""
    from iladub.etkl.holon import assert_record_region
    g = Graph()
    with pytest.raises(ValueError):
        assert_record_region(g, _u11_region(tmp_path), _U11_T, _U11_DOC, 0, **kw)
    assert len(g) == 0, "the guard must refuse before the emitter writes anything"


def test_u11_unshown_row_zero_address_is_consumed_when_headerless(tmp_path):
    """Review Focus 3 (R213): with 0 header lines a row-0 address in `band.unshown` reaches an entry
    cell, which carries `tab:unshownText` and an empty `tab:cellText`, and the carriage's
    completeness check does not fire. The control is today's: with the default header, the same
    address reaches no entry cell and the carriage refuses the region."""
    from dataclasses import replace
    from iladub.etkl.holon import TAB as HTAB, UnshownCarriageError
    region = _u11_region(tmp_path)
    region = replace(region, band=replace(region.band, unshown=((0, 1),)))

    with pytest.raises(UnshownCarriageError):
        _u11_emit(region)

    g, _ = _u11_emit(region, header_lines=0, absent_by=_U11_D)
    e = URIRef(f"{_U11_T}-e0_1")
    assert (e, RDF.type, HTAB.EntryCell) in g
    assert str(g.value(e, HTAB.unshownText)) == "Value"
    assert str(g.value(e, HTAB.cellText)) == ""
    carried = {(s, str(o)) for s, o in g.subject_objects(HTAB.unshownText)}
    assert carried == {(e, "Value")}, f"exactly the one address is carried: {carried}"
