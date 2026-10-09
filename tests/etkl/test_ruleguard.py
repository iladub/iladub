"""R301 Task 3 — `ruleguard`: the producer withdraws and escalates a table whose cell an author's
rule separates (spec 2026-10-08-r301-producer-guard-design.md §§ 2.2, 2.3, § 8 S1–S3).

Synthetic graphs only. The page is the shape's own one-cell fixture (`_page`), imported, so the
guard is exercised on exactly the evidence `tab:RuleSeparatedInkShape` is pinned on."""
import os
from dataclasses import astuple, replace

import pytest
from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from rdflib.namespace import XSD

from iladub.etkl import compile as C
from iladub.etkl import ruleguard
from iladub.etkl.compile import RegionReport
from iladub.etkl.decisionlog import DEC
from iladub.etkl.document import _verdict_decision
from iladub.etkl.holon import ILADUB
from iladub.etkl.regions import RegionKind
from tests.test_rule_separated_ink import DOC, TAB, _page

D = URIRef(DOC)
T = URIRef(DOC + "#t")
CELL = URIRef(DOC + "#c")
REGION0 = URIRef(DOC + "#region0")
READER = URIRef("https://w3id.org/iladub/etkl#reader")
QDIR = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")


def _decision(g, d, label, order, regarding=REGION0, options=("asserted", "escalated"),
              chosen="asserted"):
    """A recorded judgement shaped as `BandRecorder.record` shapes one (decisionlog.py)."""
    g.add((d, RDF.type, DEC.DecisionHolon))
    g.add((d, RDFS.label, Literal(label)))
    if regarding is not None:
        g.add((d, DEC.regarding, regarding))
    if order is not None:
        g.add((d, DEC.order, Literal(order, datatype=XSD.integer)))
        g.add((d, DEC.rationale, Literal("")))
    g.add((d, DEC.decidedBy, READER))
    for name in options:
        o = URIRef(f"{d}-opt-{name}")
        g.add((o, RDF.type, DEC.Option))
        g.add((o, RDFS.label, Literal(name)))
        g.add((d, DEC.optionSpace, o))
        if name == chosen:
            g.add((d, DEC.chosen, o))
    return d


def _banded_page():
    """The refused one-cell page, plus the band's chain: `kind` at -d0, `verdict` at -d1."""
    g = _page(80, 90, rule_x=85)
    _decision(g, URIRef(DOC + "#region0-d0"), "kind", 0, options=("table", "prose"),
              chosen="table")
    head = _decision(g, URIRef(DOC + "#region0-d1"), "verdict", 1)
    return g, head


def _minted_page():
    """`_banded_page`, with the cell minted where the compile mints one: under its table's URI
    space (`{t}-r{row}c{col}`). `_page`'s `#c` sits outside every table space, and the extent
    (spec § 2.2) withdraws a table's OWN space only."""
    g, head = _banded_page()
    minted = URIRef(f"{T}-r0c0")
    out = Graph()
    for s, p, o in g:
        out.add((minted if s == CELL else s, p, minted if o == CELL else o))
    return out, head, minted


def _chain(g, region=REGION0):
    q = open(os.path.join(QDIR, "effective-chain.rq"), encoding="utf-8").read()
    return [r.asdict() for r in g.query(q, initBindings={"region": region})]


def _report(table_uri=T, tokens=5):
    return RegionReport(RegionKind.RECORD_TABLE, "asserted", 1, None, str(TAB.RecordTable),
                        "96,127+", table_uri, tokens_asserted=tokens, line_indices=(3, 4))


def _ntriples(g):
    return frozenset(g.serialize(format="nt").splitlines())


# ---------------------------------------------------------------- 1. the select is the shape's

def test_the_select_is_the_shapes_own_on_its_fixture_pair():
    assert ruleguard.rule_separated_cells(_page(80, 90, rule_x=85)) == frozenset({CELL})
    assert ruleguard.rule_separated_cells(_page(80, 90, rule_x=200)) == frozenset()


def test_owner_tables_are_the_cells_tables():
    g = _page(80, 90, rule_x=85)
    assert ruleguard.owner_tables(g, frozenset({CELL})) == frozenset({T})


# ---------------------------------------------------------------- 2. S1: the extent

def test_extent_excludes_a_sibling_grid_the_residue_and_decisions():
    """S1. The datagrid naming is the collision S1 was ruled for (handoff § 1): a sibling grid
    `-datagrid-2` and the residue `-datagrid-residue` both sit under `-datagrid-`."""
    g = Graph()
    t = URIRef(DOC + "#p0-datagrid")
    sib = URIRef(DOC + "#p0-datagrid-2")
    residue = URIRef(DOC + "#p0-datagrid-residue")
    own_cell, sib_cell = URIRef(f"{t}-r0c0"), URIRef(f"{sib}-r0c0")
    bbox = BNode()
    g.add((t, RDF.type, TAB.DataGrid))
    g.add((t, TAB.hasDataCell, own_cell))
    g.add((own_cell, TAB.cellText, Literal("63,061-")))
    g.add((own_cell, TAB.hasBBox, bbox))
    # a URIRef edge out of the withdrawn space: the closure follows blank nodes ONLY, so the
    # edge itself goes (its subject is a root) and the sibling's cell stays whole.
    g.add((own_cell, RDFS.seeAlso, sib_cell))
    g.add((bbox, TAB.x0, Literal(1)))
    g.add((sib, RDF.type, TAB.DataGrid))
    g.add((sib, TAB.hasDataCell, sib_cell))
    g.add((sib_cell, TAB.cellText, Literal("1")))
    g.add((residue, RDF.type, ILADUB.CandidateConcept))
    g.add((URIRef(f"{residue}-source"), RDF.type, ILADUB.SourceRegion))
    # The admission as `datagrid.emit_data_grid` mints it: its options live in the grid's own
    # space (`t` itself is the chosen option, `{t}-refuse-page` the no-change one). The holon is
    # excluded; its option NODES are withdrawn with the grid, as spec § 2.2 defines and handoff
    # U2 measured on p7 (the admission keeps all its triples; its options keep none).
    adm, refuse_page = URIRef(f"{t}-admission"), URIRef(f"{t}-refuse-page")
    g.add((adm, RDF.type, DEC.DecisionHolon))
    g.add((adm, DEC.optionSpace, t))
    g.add((adm, DEC.optionSpace, refuse_page))
    g.add((adm, DEC.chosen, t))
    g.add((adm, DEC.decidedBy, READER))
    g.add((refuse_page, RDF.type, DEC.Option))
    before = _ntriples(g)

    ext = ruleguard.withdrawal_extent(g, t, [sib], residue)

    assert set(ext.subjects()) == {t, own_cell, bbox, refuse_page}
    assert len(ext) == 7
    assert not set(ext.triples((sib_cell, None, None)))
    assert _ntriples(g) == before, "withdrawal_extent must not mutate its graph"


def test_extent_of_a_sibling_is_its_own_not_the_base_grids():
    """The other direction of S1: the sibling `-2` lies inside the base grid's URI space, so the
    base must not claim `-2`'s subjects back, and `-2`'s own subjects must not be excluded as
    the base's. A subject belongs to the MOST SPECIFIC table space that holds it."""
    g = Graph()
    t = URIRef(DOC + "#p0-datagrid")
    sib = URIRef(DOC + "#p0-datagrid-2")
    for u in (t, sib):
        g.add((u, RDF.type, TAB.DataGrid))
        g.add((u, TAB.hasDataCell, URIRef(f"{u}-r0c0")))
        g.add((URIRef(f"{u}-r0c0"), TAB.cellText, Literal("x")))
    residue = URIRef(DOC + "#p0-datagrid-residue")
    ext = ruleguard.withdrawal_extent(g, sib, [t], residue)
    assert set(ext.subjects()) == {sib, URIRef(f"{sib}-r0c0")}


# ---------------------------------------------------------------- 3. S2: the refusal

def test_the_refusal_supersedes_the_verdict_and_ends_the_chain():
    g, head = _banded_page()
    assert ruleguard.chain_head(g, D, 0, T) == head

    r = ruleguard.mint_refusal(g, D, 0, head, "tab:RuleSeparatedInkShape crosses <c>")

    assert r == URIRef(DOC + "#region0-refusal")
    assert _verdict_decision(g, D, 0) == head, "the refusal must not pass as the verdict"
    assert g.value(r, DEC.order).toPython() == 2
    assert (r, DEC.supersedes, head) in g
    rows = _chain(g)
    assert [int(x["order"]) for x in rows] == [0, 1, 2]
    assert str(rows[-1]["judgement"]) == "refusal"
    assert str(rows[-1]["chosen"]) == "refuse"
    conforms, text, legs = C._validate(g, legs=("dec",))
    assert conforms, text


# ---------------------------------------------------------------- 4. M9: an admission head

def test_an_admission_head_without_order_gives_order_zero_and_branch_b_reads_it():
    g = _page(80, 90, rule_x=85)
    adm = _decision(g, URIRef(f"{T}-admission"), "admission", None, regarding=None)
    head = ruleguard.chain_head(g, D, 0, T)
    assert head == adm

    r = ruleguard.mint_refusal(g, D, 0, head, "tab:RuleSeparatedInkShape crosses <c>")

    assert g.value(r, DEC.order).toPython() == 0
    rows = _chain(g)
    assert [(str(x["judgement"]), str(x["chosen"])) for x in rows] == [("refusal", "refuse")]
    conforms, text, _ = C._validate(g, legs=("dec",))
    assert conforms, text


# ---------------------------------------------------------------- 4b. the head is WALKED to

def test_a_superseded_verdict_is_walked_to_its_head_and_the_refusal_chains():
    """v1 <- v2 (section repair's pass-2 re-read). The refusal must supersede v2, the reading
    that STANDS; superseding v1 would give it a second superseder and
    `dec:SupersededOnceShape` refuses (the 2026-09-14 lineage ruling: chain, never fan in)."""
    g, v1 = _banded_page()
    v2 = _decision(g, URIRef(DOC + "/pass2#region0-d1"), "verdict", 1,
                   regarding=URIRef(DOC + "/pass2#region0"))
    g.add((v2, DEC.supersedes, v1))

    head = ruleguard.chain_head(g, D, 0, T)
    assert head == v2
    r = ruleguard.mint_refusal(g, D, 0, head, "tab:RuleSeparatedInkShape crosses <c>")

    assert (r, DEC.supersedes, v2) in g and (r, DEC.supersedes, v1) not in g
    conforms, text, _ = C._validate(g, legs=("dec",))
    assert conforms, text


# ---------------------------------------------------------------- 5. no head: raise

def test_no_standing_decision_raises_naming_the_table_and_index():
    g = _page(80, 90, rule_x=85)
    with pytest.raises(RuntimeError) as e:
        ruleguard.chain_head(g, D, 7, T)
    assert str(T) in str(e.value) and "region index 7" in str(e.value)


# ---------------------------------------------------------------- 6. ambiguous owner: identity

@pytest.mark.parametrize("named", [0, 2], ids=["zero-reports", "two-reports"])
def test_an_owner_named_by_zero_or_two_reports_is_left_to_the_membrane(named):
    g, _, _ = _minted_page()
    reports = [_report() for _ in range(named)] + [_report(table_uri=URIRef(DOC + "#other"))]
    before_g, before_r = _ntriples(g), tuple(astuple(r) for r in reports)

    total = sum(r.tokens_asserted for r in reports)
    out, a, e = ruleguard.guard(g, reports, total, 0, D, 0)

    assert _ntriples(g) == before_g
    assert tuple(astuple(r) for r in out) == before_r
    assert (a, e) == (total, 0)


# ---------------------------------------------------------------- 7. the happy path

def test_the_guard_withdraws_refuses_escalates_and_moves_the_tokens():
    g, head, cell = _minted_page()
    assert ruleguard.rule_separated_cells(g) == frozenset({cell})
    rep = _report(tokens=5)

    out, a, e = ruleguard.guard(g, [rep], 5, 2, D, 0)

    assert (cell, None, None) not in g and (T, None, None) not in g
    assert ruleguard.rule_separated_cells(g) == frozenset()
    (r,) = out
    assert (r.verdict, r.reason, r.cells, r.table_uri) == ("escalated", "RULE_SEPARATED_INK",
                                                           0, None)
    assert (r.tokens_asserted, r.tokens_escalated) == (0, 5)
    assert (r.kind, r.anchor, r.ascii, r.line_indices) == (rep.kind, rep.anchor, rep.ascii,
                                                           rep.line_indices)
    assert (a, e) == (0, 7)
    assert (REGION0, RDF.type, ILADUB.CandidateConcept) in g
    assert str(g.value(REGION0, RDFS.label)) == "RULE_SEPARATED_INK"
    assert g.value(REGION0, ILADUB.confidence).toPython() == 0
    assert g.value(REGION0, ILADUB.suggestedAnchor) == TAB.RecordTable
    refusal = URIRef(DOC + "#region0-refusal")
    assert (refusal, DEC.supersedes, head) in g
    rationale = str(g.value(refusal, DEC.rationale))
    assert "tab:RuleSeparatedInkShape" in rationale and str(cell) in rationale
    conforms, text, _ = C._validate(g, legs=("dec",))
    assert conforms, text


def test_the_refused_region_is_furnished_for_escalation_by_its_refusal():
    """R303: the withdrawn region reaches a human through a `dec:ExpansionRequest`. The furnish
    reads the refusal's chosen `"refuse"` (never relabelled: R301 § 8 S3), and the verdict the
    refusal supersedes is a withdrawn reading, so exactly one decision escalates."""
    from iladub.etkl import interpret
    from iladub.etkl.document import ESCALATION_FURNISH_RQ, _escalation_vocab
    g, _, _ = _minted_page()
    ruleguard.guard(g, [_report(tokens=5)], 5, 2, D, 0)

    g += interpret.run(ESCALATION_FURNISH_RQ, g, _escalation_vocab())

    refusal = URIRef(DOC + "#region0-refusal")
    assert list(g.subject_objects(DEC.escalatedTo)) == [(refusal,
                                                          URIRef(f"{refusal}-expansion"))]
    assert g.value(URIRef(f"{refusal}-expansion"), DEC.regarding) == REGION0
    conforms, text, _ = C._validate(g, legs=("dec",))
    assert conforms, text


def test_the_escalated_report_carries_no_header_reading_and_others_keep_theirs():
    """A refused table's reading must not be carried onto the next page (document driver):
    its row sources live in the withdrawn space."""
    g, _, _ = _minted_page()
    owner = replace(_report(tokens=5), header_reading="owner-reading")
    other = replace(_report(table_uri=URIRef(DOC + "#other"), tokens=3),
                    header_reading="other-reading")

    out, _, _ = ruleguard.guard(g, [owner, other], 8, 0, D, 0)

    assert out[0].verdict == "escalated" and out[0].header_reading is None
    assert out[1] == other
