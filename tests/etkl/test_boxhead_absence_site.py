"""Box-split § 10.3.4 (Task 3d.6): the ask site on the RECORD path of `compile_tables`.

Spec `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.3.4 / § 10.5 (U12), the plan's
Review Focus 1, 2 and 5 for Task 3d, and the controller ruling that moves U14's merge-in case here.
Split out of `test_boxhead_absence.py` at the plan's ~600-line mark, as U9 and U13 were.

THE ORDER AT THE SITE, which every test below reads from outside:
  1. a region is asked only when it is not a donation (`donation.offer` and
     `donation.offer_single_line` both returned None for its band) and `row-zero-differs.rq` finds
     no witness;
  2. the reader is `headerlines.default_reader()`, looked up through the module, so the fake
     installed here reaches it;
  3. an answer is recorded as a `header_lines` decision BEFORE `assert_record_region`, and a `0`
     reaches it as `header_lines=0, absent_by=<that decision>`;
  4. no claim — no reader, a None reading, an answer outside `0..nlines` — records nothing, and the
     page is the page of a region never asked.

NO LIVE CALL. `_no_live` unsets `BAML_LIVE` and points `READINGS_DIR` at an empty directory, so
the only reader any test sees is the fake it installs.
"""
from __future__ import annotations

import pytest
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.compare import isomorphic

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from tests.etkl import fixtures as _F  # noqa: E402

TAB = Namespace("https://w3id.org/iladub/tab#")
DEC = Namespace("https://w3id.org/iladub/dec#")

_ALL_NUMBERS = [("ALB", "10"), ("ESP", "30"), ("GER", "50"), ("KWI", "70")]
_TEXT_OVER_NUMBERS = [("Port", "Tonnes"), ("ALB", "10"), ("ESP", "30"), ("GER", "50")]
_PLAIN_LISTING = "L0: ALB | 10\nL1: ESP | 30\nL2: GER | 50\nL3: KWI | 70"


class _Fake:
    """A fixed answer that records every question it is asked: `(crop_png, ncols, listing)`."""

    def __init__(self, reading):
        self.reading = reading
        self.calls: list[tuple[bytes, int, str]] = []

    def count_header_lines(self, crop_png, ncols, listing):
        self.calls.append((crop_png, ncols, listing))
        return self.reading


@pytest.fixture(autouse=True)
def _no_live(monkeypatch, tmp_path):
    from iladub.etkl import headerlines
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.delenv("ILADUB_RECORD_READINGS", raising=False)
    empty = tmp_path / "no-readings"
    empty.mkdir()
    monkeypatch.setattr(headerlines, "READINGS_DIR", empty)


@pytest.fixture
def reader(monkeypatch):
    """`reader(k, note)` installs a recording fake answering `k` (None: no reading) as
    `headerlines.default_reader()`, and returns it."""
    from iladub.etkl import headerlines

    def install(k, note="the first line is already data"):
        fake = _Fake(None if k is None else headerlines.HeaderLinesReading(k, note))
        monkeypatch.setattr(headerlines, "default_reader", lambda: fake)
        return fake
    return install


@pytest.fixture
def oracle_silent(monkeypatch):
    """`row-zero-differs.rq` finds no witness anywhere. Used ONLY where the subject is a guard
    that must hold on its own — a donated band's row 0 is the donor's labels, and the oracle
    witnesses it today, so without this the test would pass on the oracle and pin nothing."""
    from iladub.etkl import rowzero
    monkeypatch.setattr(rowzero, "row_zero_differs", lambda region, pdf, page: False)


def _box(tmp_path, rows, **kw):
    p = str(tmp_path / "box.pdf")
    _F.styled_box_pdf(p, rows, **kw)
    return p


def _compile(p, validate=True):
    from iladub.etkl.compile import compile_tables
    return compile_tables(p, 0, validate_shapes=validate)


def _decisions(g, label="header_lines"):
    return [d for d in g.subjects(RDF.type, DEC.DecisionHolon)
            if (d, RDFS.label, Literal(label)) in g]


def _chosen(g, d):
    return str(g.value(g.value(d, DEC.chosen), RDFS.label))


def _never_asked(monkeypatch, p, validate=True):
    """The page of a region that is never asked: the reader trips if it is reached, and the oracle
    witnesses every region. The reference for "byte-identical to today's" on synthetic input; the
    whole-corpus comparison is C2, `docs/superpowers/2026-09-28-box-split-evidence.md` § 4.6."""
    from iladub.etkl import headerlines, rowzero
    with monkeypatch.context() as m:
        m.setattr(rowzero, "row_zero_differs", lambda region, pdf, page: True)
        m.setattr(headerlines, "ask_header_lines",
                  lambda *a, **k: pytest.fail("a witnessed region was asked"))
        return _compile(p, validate)


def _same_page(a, b):
    assert isomorphic(a.graph, b.graph)
    assert a.regions == b.regions
    assert (a.asserted, a.escalated, a.score) == (b.asserted, b.escalated, b.score)


# ---------------------------------------------------------------------------------------------
# U12 — the four cases of § 10.5
# ---------------------------------------------------------------------------------------------

def test_u12_a_witnessed_region_is_never_asked(tmp_path, reader):
    """§ 10.5 case 1, first half. The fake would answer 0, so asking would be visible; it is never
    CALLED, which is the assertion — not only that nothing changed."""
    from iladub.etkl.rowzero import row_zero_differs
    from iladub.etkl.compile import page_bands
    from iladub.etkl.regions import classify
    p = _box(tmp_path, _TEXT_OVER_NUMBERS, head_font="Helvetica-Bold", head_fill=(0.8, 0.8, 0.8))
    assert row_zero_differs(classify(page_bands(p, 0)[0]), p, 0) is True, "precondition"
    fake = reader(0)
    rep = _compile(p)
    assert fake.calls == [], "a witnessed region was asked"
    assert _decisions(rep.graph) == []
    t = URIRef(rep.regions[0].table_uri)
    assert len(set(rep.graph.objects(t, TAB.hasHeaderNode))) == 2, "today's positional header"
    assert not list(rep.graph.subject_objects(TAB.boxheadAbsentBy))


def test_u12_a_donated_region_is_never_asked(tmp_path, reader, oracle_silent):
    """§ 10.5 case 1, second half. MEASURED: this page's only RECORD region is band 1, donated,
    and its row 0 (the donor's `Region | Total | Share`) is witnessed today — so the oracle is
    silenced, and the donated guard is the only thing that can keep the fake uncalled."""
    from tests.etkl.test_grid_donation_disposal import _page
    path = tmp_path / "donated.pdf"
    _page(path, (80.0, 210.0, 340.0))
    fake = reader(0)
    rep = _compile(str(path), validate=False)
    assert rep.regions[1].verdict == "asserted", "precondition: the donation is accepted"
    t = URIRef(rep.regions[1].table_uri)
    assert (t, TAB.headerDonatedBy, None) in rep.graph, "precondition: band 1 is donated"
    assert fake.calls == [], "a donated region was asked"
    assert _decisions(rep.graph) == []


def _lone_page(path):
    """`test_grid_donation_disposal._page`, plus a LONE data row set apart below the table — bfs
    p6's `Total`. MEASURED: band 2 is that one-line band; `offer_single_line` accepts it."""
    from reportlab.pdfgen import canvas
    from tests.etkl import test_grid_donation_disposal as GD
    xs = (80.0, 210.0, 340.0)
    c = canvas.Canvas(str(path), pagesize=GD.letter)
    c.setFont("Courier", 9)
    y = GD.PAGE_H - 90.0
    for x in GD.RULES:
        c.line(x, y - 4.0, x, y + 14.0)
    for (t, x) in GD.HEAD:
        c.drawString(x, y, t)
    y -= 150.0
    for i, row in enumerate(GD.ROWS):
        for x, cell in zip(xs, row):
            c.drawString(x, y - i * 14.0, cell)
    for x, cell in zip(xs, ("Total", "2799657", "30.1")):
        c.drawString(x, y - len(GD.ROWS) * 14.0 - 60.0, cell)
    c.save()


def test_u12_a_lone_line_donation_is_never_asked_even_when_offer_declines_it(
        tmp_path, reader, oracle_silent, monkeypatch):
    """The controller's precondition (3d.5 review): `headerlines` assumes `nlines ==
    len(region.band.lines)`, which only a `classify`-built region satisfies. A lone line's region
    is `donation.donated_region`'s — 2 rows over a 1-line band, the donor's labels in row 0. Today
    `offer` also accepts it, so `donated` is set; `offer` is refused here for one-line bands so
    that `donated is None` at the site, and only the lone-donation guard can keep it unasked."""
    from iladub.etkl import donation
    path = tmp_path / "lone.pdf"
    _lone_page(path)
    real_offer, real_lone = donation.offer, donation.offer_single_line
    lone_accepted = []

    def lone(bands, idx, ev, pn):
        r = real_lone(bands, idx, ev, pn)
        lone_accepted.append((idx, r is not None))
        return r

    monkeypatch.setattr(donation, "offer_single_line", lone)
    monkeypatch.setattr(donation, "offer", lambda bands, idx, region, ev, pn: (
        None if len(bands[idx].lines) == 1 else real_offer(bands, idx, region, ev, pn)))
    fake = reader(0)
    rep = _compile(str(path), validate=False)
    assert (2, True) in lone_accepted, "precondition: band 2 is a lone line, and it is donated"
    assert rep.regions[2].verdict == "asserted"
    assert fake.calls == [], (
        "a lone-line donation was asked: " + repr([c[2] for c in fake.calls]))
    assert _decisions(rep.graph) == []


_I103_STATEMENT_NOT_DECIDED = """
PREFIX tab: <https://w3id.org/iladub/tab#>  PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?t WHERE { ?t tab:boxheadAbsentBy ?d .
  FILTER NOT EXISTS { ?d a dec:DecisionHolon ; rdfs:label "header_lines" ;
                         dec:chosen/rdfs:label "no_boxhead" } }"""
_I103_STATEMENT_WITH_HEADER = """
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?t WHERE { ?t tab:boxheadAbsentBy ?d ; tab:hasHeaderNode ?h }"""
_I103_DECIDED_NOT_STATED = """
PREFIX tab: <https://w3id.org/iladub/tab#>  PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?d WHERE { ?d a dec:DecisionHolon ; rdfs:label "header_lines" ;
                     dec:chosen/rdfs:label "no_boxhead" .
  FILTER NOT EXISTS { ?t tab:boxheadAbsentBy ?d } }"""


def test_u12_answer_zero_gives_a_headerless_table_and_its_decision(tmp_path, reader,
                                                                    monkeypatch):
    """§ 10.5 case 2, on the page `validate_shapes=True` compiles (the membrane runs both legs
    over the page graph and the log: a refusal raises). The fake records its question, so the
    site is shown to reach it with THIS region on THIS page — `ask_header_lines` turns a wrong
    page or region into a silent no-claim (3d.5 review), which a None-only test cannot see."""
    from iladub.etkl import compile as compile_mod
    from iladub.etkl.compile import page_bands
    from iladub.etkl.unshownink import render_region
    p = _box(tmp_path, _ALL_NUMBERS)
    booked = []
    real_book = compile_mod._book_recovered_ink

    def book(band, words, extents):
        extents = tuple(extents)
        booked.append((len(words), len(extents)))
        return real_book(band, words, extents)

    monkeypatch.setattr(compile_mod, "_book_recovered_ink", book)
    fake = reader(0, "row 1 continues row 0's pattern")
    rep = _compile(p)
    g = rep.graph

    assert len(fake.calls) == 1
    crop, ncols, listing = fake.calls[0]
    assert (ncols, listing) == (2, _PLAIN_LISTING)
    assert crop == render_region(p, 0, page_bands(p, 0)[0]), "the crop is this band's, page 0"

    [d] = _decisions(g)
    t = URIRef(rep.regions[0].table_uri)
    assert rep.regions[0].verdict == "asserted" and rep.regions[0].cells == 8
    assert (t, TAB.boxheadAbsentBy, d) in g
    assert _chosen(g, d) == "no_boxhead"
    assert {str(g.value(o, RDFS.label)) for o in g.objects(d, DEC.optionSpace)} == {
        "boxhead", "no_boxhead"}
    rationale = str(g.value(d, DEC.rationale))
    for part in ("0", "row 1 continues row 0's pattern", "no witness"):
        assert part in rationale, (part, rationale)

    assert not list(g.objects(t, TAB.hasHeaderNode))
    assert not list(g.subjects(RDF.type, TAB.LabelCell))
    assert len(set(g.objects(t, TAB.hasLeafRow))) == 4, "row 0 is a LeafRow too"

    # I-10-3, by query, over the tables present: statement <=> a no_boxhead decision, 0 headers
    assert list(g.query(_I103_STATEMENT_NOT_DECIDED)) == []
    assert list(g.query(_I103_STATEMENT_WITH_HEADER)) == []
    assert list(g.query(_I103_DECIDED_NOT_STATED)) == []

    # The R176 mirror follows the count: every cell is booked as a data cell (8 words), and no
    # label extent is passed to the recovered-ink ledger.
    assert booked == [(8, 0)], booked
    assert (rep.regions[0].tokens_asserted, rep.regions[0].tokens_escalated) == (8, 0)


@pytest.mark.parametrize("k", [1])
def test_u12_an_answer_of_one_or_more_gives_todays_table_and_a_boxhead_decision(
        tmp_path, reader, monkeypatch, k):
    """§ 10.5 case 3. The TABLE is today's; the page differs from today's only by the decision
    (whose insertion renumbers the band's later judgements, so the comparison is table to table).
    An answer above 1 used to land here too (§ 10.6); since R293 it escalates — the next test."""
    from iladub.etkl.document import _band_subgraph
    p = _box(tmp_path, _ALL_NUMBERS)
    today = _never_asked(monkeypatch, p)
    fake = reader(k)
    rep = _compile(p)
    assert len(fake.calls) == 1
    t = URIRef(rep.regions[0].table_uri)
    assert isomorphic(_band_subgraph(rep.graph, t), _band_subgraph(today.graph, t))
    assert rep.regions == today.regions
    [d] = _decisions(rep.graph)
    assert _chosen(rep.graph, d) == "boxhead"
    assert f"{k}" in str(rep.graph.value(d, DEC.rationale))
    assert not list(rep.graph.subject_objects(TAB.boxheadAbsentBy))


@pytest.mark.parametrize("k", [2, 4])
def test_r293_an_answer_above_one_escalates_the_region_and_asserts_no_entry(
        tmp_path, reader, monkeypatch, k):
    """R293 (`2026-10-05-r293-p6-adopts.md` § 2.4): the record path carries ONE header level, so
    a reader's answer of k > 1 cannot be emitted without asserting lines 2..k as entries — on bfs
    p6 that put `Cantons` and `des jeunes 1` in `tab:EntryCell`s. The region is proposed instead:
    no entry cell at all, every token of the band escalated, and the decision still recorded."""
    p = _box(tmp_path, _ALL_NUMBERS)
    today = _never_asked(monkeypatch, p)
    fake = reader(k)
    rep = _compile(p)
    assert len(fake.calls) == 1
    assert today.regions[0].verdict == "asserted" and today.escalated == 0
    assert rep.regions[0].verdict == "escalated"
    assert rep.regions[0].reason == "BOXHEAD_EXCEEDS_RECORD"
    assert rep.regions[0].table_uri is None
    assert list(rep.graph.subjects(RDF.type, TAB.EntryCell)) == []
    assert (rep.asserted, rep.escalated) == (0, today.asserted + today.escalated)
    [d] = _decisions(rep.graph)
    assert _chosen(rep.graph, d) == "boxhead"
    assert f"{k} leading header line" in str(rep.graph.value(d, DEC.rationale))


@pytest.mark.parametrize("k", [None, -1, 5])
def test_u12_no_claim_is_byte_identical_and_records_nothing(tmp_path, reader, monkeypatch, k):
    """§ 10.5 case 4: a None reading, and answers outside `0..nlines` (nlines = 4), are no claim.
    The fake IS asked — the site ran — and the page is the page of a region never asked."""
    p = _box(tmp_path, _ALL_NUMBERS)
    today = _never_asked(monkeypatch, p)
    fake = reader(k)
    rep = _compile(p)
    assert len(fake.calls) == 1, "the site must have asked"
    _same_page(rep, today)
    assert _decisions(rep.graph) == []


# ---------------------------------------------------------------------------------------------
# Review Focus 2 and 5
# ---------------------------------------------------------------------------------------------

def test_rf2_a_zero_that_then_fails_tiling_escalates_and_keeps_its_decision(
        tmp_path, reader, monkeypatch):
    """Review Focus 2. The region gate refuses (patched: no natural fixture is needed to show what
    the site does with a refusal it did not cause). The decision stays in the log, the band
    escalates, and no statement is minted anywhere: I-10-3 ranges over the tables present."""
    from iladub.etkl import tiling
    monkeypatch.setattr(tiling, "region_tiles", lambda g: False)
    p = _box(tmp_path, _ALL_NUMBERS)
    reader(0)
    rep = _compile(p)
    assert (rep.regions[0].verdict, rep.regions[0].reason) == ("escalated", "REGION_TILING_FAILED")
    [d] = _decisions(rep.graph)
    assert _chosen(rep.graph, d) == "no_boxhead"
    assert not list(rep.graph.subject_objects(TAB.boxheadAbsentBy))
    assert not list(rep.graph.subjects(RDF.type, TAB.RecordTable))


def _one_line(monkeypatch):
    """Review Focus 5's region. MEASURED (U9, 3d.4): a one-line box classifies NON_TABLE and never
    reaches the RECORD path, and the only one-line regions that do are lone-line donations, which
    are never asked. So the region is the plain box's own, cut to row 0 and to its first line —
    the shape the oracle's stated blind spot names."""
    from dataclasses import replace
    from iladub.etkl import compile as compile_mod
    real = compile_mod.classify

    def classify(band):
        r = real(band)
        one = replace(band, lines=band.lines[:1])
        return replace(r, band=one, cells=tuple(c for c in r.cells if c.row == 0))

    monkeypatch.setattr(compile_mod, "classify", classify)


def test_rf5_a_one_line_region_answered_zero_is_a_one_row_headerless_table(
        tmp_path, reader, monkeypatch):
    p = _box(tmp_path, _ALL_NUMBERS)
    _one_line(monkeypatch)
    fake = reader(0)
    rep = _compile(p)
    assert [c[2] for c in fake.calls] == ["L0: ALB | 10"]
    t = URIRef(rep.regions[0].table_uri)
    [d] = _decisions(rep.graph)
    assert (t, TAB.boxheadAbsentBy, d) in rep.graph
    assert len(set(rep.graph.objects(t, TAB.hasLeafRow))) == 1
    assert rep.regions[0].cells == 2 and not list(rep.graph.objects(t, TAB.hasHeaderNode))


def test_rf5_a_one_line_region_answered_one_is_todays_table(tmp_path, reader, monkeypatch):
    from iladub.etkl.document import _band_subgraph
    p = _box(tmp_path, _ALL_NUMBERS)
    _one_line(monkeypatch)
    today = _never_asked(monkeypatch, p)
    reader(1)
    rep = _compile(p)
    t = URIRef(rep.regions[0].table_uri)
    assert isomorphic(_band_subgraph(rep.graph, t), _band_subgraph(today.graph, t))
    [d] = _decisions(rep.graph)
    assert _chosen(rep.graph, d) == "boxhead"


def test_rf5_a_one_line_region_answered_two_is_no_claim(tmp_path, reader, monkeypatch):
    p = _box(tmp_path, _ALL_NUMBERS)
    _one_line(monkeypatch)
    today = _never_asked(monkeypatch, p)
    fake = reader(2)
    rep = _compile(p)
    assert len(fake.calls) == 1
    _same_page(rep, today)
    assert _decisions(rep.graph) == []


# ---------------------------------------------------------------------------------------------
# Review Focus 1 (A2, the site's half) and U14's merge-in case (controller ruling 2026-09-30)
# ---------------------------------------------------------------------------------------------
#
# MEASURED (`docs/superpowers/2026-09-28-box-split-evidence.md` § 4.9): of every fixture in `fixtures.py` that builds from a path alone, NONE
# reaches the ask site on more than one pass, and none reaches `/r2` or `/adopt` unwitnessed. The
# two below are the fixtures whose RECORD regions reach those passes at all:
#   * `currency_marker_escalating_with_asserting_table_pdf`: band 1 on `p0` and on `/adopt`;
#   * `multi_section_ruled_pdf`: bands 0 and 1 on `/r2` only.
# Both are witnessed, so the oracle is silenced: the subject here is what the passes carry, not
# which regions the oracle spares. 3d.7 Step 1 checks the same on the corpus.

def _doc(tmp_path, name):
    from iladub.etkl.document import compile_document
    p = str(tmp_path / f"{name}.pdf")
    getattr(_F, name)(p)
    return compile_document(p, validate_shapes=True)


def test_rf1_a_band_reached_on_two_passes_asks_the_same_question_on_both(
        tmp_path, reader, oracle_silent):
    fake = reader(None)
    rep = _doc(tmp_path, "currency_marker_escalating_with_asserting_table_pdf")
    assert rep.adopted == (0,), "precondition: the page reaches the /adopt pass"
    assert len(fake.calls) == 2, [c[2] for c in fake.calls]
    assert fake.calls[0] == fake.calls[1], "the key moved between p0 and /adopt"


def _statements_decided_in(g):
    out = []
    for t, d in g.subject_objects(TAB.boxheadAbsentBy):
        assert (d, RDF.type, DEC.DecisionHolon) in g, f"{d} is not in the document graph"
        assert (d, RDFS.label, Literal("header_lines")) in g
        assert _chosen(g, d) == "no_boxhead"
        out.append(str(t))
    return sorted(out)


def test_u14_a_table_merged_from_r2_carries_its_statement_and_its_decision(
        tmp_path, reader, oracle_silent):
    reader(0)
    rep = _doc(tmp_path, "multi_section_ruled_pdf")
    assert rep.repaired_bands == ((0, 0), (0, 1)), "precondition: both tables merge from /r2"
    stated = _statements_decided_in(rep.graph)
    assert stated == ["https://example.org/etkl/doc/p0/r2#table0",
                      "https://example.org/etkl/doc/p0/r2#table1"], stated


def test_u14_adoption_withdraws_an_answered_table_exactly_as_it_would_without_the_edge(
        tmp_path, reader, oracle_silent, monkeypatch):
    """U14 at the site: band 1 is answered 0 on `p0`, so the pass-1 table adoption withdraws
    carries the edge into the log — the spy shows the withdrawn subgraph holding it — and adoption
    still withdraws it, exactly as with no answer at all. The decision stays in the log.

    NOTHING FROM `/adopt` IS STATED, by construction, not by this fixture: an adoption rebuilds
    the `/adopt` page graph from the data grid alone (`graph = Graph()` in `compile_tables`'
    `datagrid_adopt` block), log included, and a page whose graph is not rebuilt carries no grid
    region, so `document.compile_document` refuses to merge it. A RECORD table asked on `/adopt`
    therefore never reaches the document graph, and neither does its decision."""
    from iladub.etkl import document
    withdrawn = []
    real_sub = document._band_subgraph

    def spy(g, t):
        sub = real_sub(g, t)
        withdrawn.append((str(t), set(sub.subject_objects(TAB.boxheadAbsentBy))))
        return sub

    monkeypatch.setattr(document, "_band_subgraph", spy)
    reader(None)
    without = _doc(tmp_path, "currency_marker_escalating_with_asserting_table_pdf")
    reader(0)
    withdrawn.clear()
    rep = _doc(tmp_path, "currency_marker_escalating_with_asserting_table_pdf")
    assert rep.adopted == without.adopted == (0,)
    assert rep.notes == without.notes
    p0_table = "https://example.org/etkl/doc/p0#table1"
    [(t, edges)] = withdrawn
    assert t == p0_table and len(edges) == 1, withdrawn
    g = rep.graph
    assert (URIRef(p0_table), None, None) not in g, "the pass-1 table was not withdrawn"
    [(_t, d)] = edges
    assert (d, RDF.type, DEC.DecisionHolon) in g and _chosen(g, d) == "no_boxhead", (
        "the decision left the log with the table")
    assert _statements_decided_in(g) == []
