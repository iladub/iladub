"""escalation-furnish.rq — the derivation that turns a recorded escalation verdict into
the predicates dec:EscalationShape reads, plus the expansion request it escalates to.

OFFLINE in this task (plan 2026-08-15 Task 2): a pure function from graph to graph, wired
into nothing. The input is built by the REAL producer (ReadingRecorder), not a hand-rolled
imitation of it — a test that mints its own decision holon stops tracking the recorder the
moment the recorder changes.

T2.3 and T2.4 are the two that carry G3's conditions 1 and 3; they are what makes option (d)
distinguishable from option (b) (write the ordinals as literals) and from merging risk.ttl.
"""
import os

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")
ONT = os.path.join(ROOT, "vocab", "ontology")
RQ = os.path.join(QDIR, "escalation-furnish.rq")

DEC = Namespace("https://w3id.org/iladub/dec#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")
RISK = Namespace("https://w3id.org/iladub/risk#")
EX = Namespace("https://example.org/")

VERDICT_OPTIONS = ["asserted", "escalated", "ignored"]


def _vocab(breach_order=None):
    """risk.ttl u etkl.ttl — the graph the ordinals are BOUND from, never written from.

    `breach_order` retunes risk:Breach's ordinal in memory; T2.3 uses it to prove the
    query reads the vocabulary rather than restating it.
    """
    g = Graph()
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    g.parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    if breach_order is not None:
        g.remove((RISK.Breach, RISK.order, None))
        g.add((RISK.Breach, RISK.order, Literal(breach_order)))
    return g


def _recorded(chosen="escalated", rationale="the band's column boundaries are ambiguous"):
    """One page's reading, recorded by the real ReadingRecorder. Returns (graph, decision)."""
    from iladub.etkl.decisionlog import ReadingRecorder

    g = Graph()
    brec = ReadingRecorder(g, EX.doc, 0).band(0)
    d = brec.record("verdict", VERDICT_OPTIONS, chosen, rationale)
    return g, d


def _derive(data, vocab=None):
    from iladub.etkl import interpret

    return interpret.run(RQ, data, vocab if vocab is not None else _vocab())


def _carried(out):
    """The triples the derivation carried out of the vocabulary — subject in risk: or etkl:."""
    return {t for t in out if str(t[0]).startswith((str(RISK), str(ETKL)))}


# ---------------------------------------------------------------- T2.1


def test_it_furnishes_every_predicate_the_shape_reads():
    data, d = _recorded()
    out = _derive(data)

    assert (d, DEC.constrainedBy, RISK.Breach) in out
    assert (d, DEC.withinScope, ETKL.readerScope) in out

    req = next(out.objects(d, DEC.escalatedTo), None)
    assert req is not None, "no dec:escalatedTo apex was derived"
    assert (req, RDF.type, DEC.ExpansionRequest) in out
    # ?req's dec:regarding and dec:condition come from ?d's own record — the request is
    # ABOUT the region the decision was about, conditioned on why the reader could not read
    # it. Read the region off the recorder rather than restating its URI: the {doc}#region{n}
    # spelling is decisionlog.py:103's, and a test that hardcodes it pins the wrong thing.
    assert (req, DEC.regarding, next(data.objects(d, DEC.regarding))) in out
    assert (req, DEC.condition,
            Literal("the band's column boundaries are ambiguous")) in out


# ---------------------------------------------------------------- T2.2


def test_it_is_silent_where_nothing_escalated():
    # Including the vocabulary triples: CONSTRUCT semantics give the boundary for free, and
    # that is exactly what separates option (d) from merging risk.ttl unconditionally.
    data, _ = _recorded(chosen="asserted")
    assert len(_derive(data)) == 0


# ---------------------------------------------------------------- T2.3 (G3 condition 1)


def test_the_ordinals_are_bound_from_the_vocabulary_not_written():
    # A query that wrote the literal 2 passes T2.1 and fails HERE. This is the testable
    # property condition 1 demands, rather than a convention nobody can check.
    data, _ = _recorded()
    out = _derive(data, vocab=_vocab(breach_order=7))
    assert (RISK.Breach, RISK.order, Literal(7)) in out
    assert (RISK.Breach, RISK.order, Literal(2)) not in out


# ---------------------------------------------------------------- T2.4 (G3 condition 3)


def test_the_vocabulary_carry_is_bounded_to_three_triples():
    # Both directions must fail this: merging risk.ttl (too many) and asserting none (too few).
    data, _ = _recorded()
    out = _derive(data)
    assert _carried(out) == {
        (ETKL.readerScope, DEC.maxSeverity, RISK.Watch),
        (RISK.Breach, RISK.order, Literal(2)),
        (RISK.Watch, RISK.order, Literal(1)),
    }


# ---------------------------------------------------------------- T2.5 (G3 condition 2)


def test_the_licence_note_is_written_down():
    # Condition 2 is the only one with no runtime consequence, and an unenforced condition
    # is not a condition. Weak enforcement, stated as such in the plan's Self-Review.
    #
    # This asserts the note's SUBSTANCE, not the word "LICENCE": a keyword check passed with
    # the whole note deleted, because a cross-reference to it survived further down the file
    # (falsified 2026-08-15). A test on a comment is weak enough without also being fooled by
    # a stray mention of the thing it is looking for.
    text = " ".join(open(RQ, encoding="utf-8").read().lower().split())
    assert "bounded to the triples that shape's body reads from the terms this query names" in text
    assert "what this licence is not: permission to merge risk.ttl into a data graph" in text


# ---------------------------------------------------------------- T2.6


def test_it_is_idempotent():
    data, _ = _recorded()
    first = _derive(data)
    data += first
    second = _derive(data)
    assert len(second - first) == 0


# ---------------------------------------------------------------- T2.7 (invariant 5)


def test_a_decision_with_no_regarding_derives_nothing():
    # The datagrid.py:714-716 shape: a dec:DecisionHolon minted without going through
    # ReadingRecorder.record, carrying dec:chosen and NO dec:regarding. Measured to exist in
    # the code as it stands (grep for DEC.regarding in datagrid.py is empty), so this setup
    # is constructible rather than hypothetical.
    data = Graph()
    d, opt = EX.grid_decision, EX.grid_option
    data.add((d, RDF.type, DEC.DecisionHolon))
    data.add((d, DEC.chosen, opt))
    data.add((d, DEC.optionSpace, opt))
    data.add((d, DEC.rationale, Literal("admitted the grid")))
    # even labelled "escalated" — the guard is the dec:regarding JOIN, not the label
    data.add((opt, RDF.type, DEC.Option))
    data.add((opt, RDFS.label, Literal("escalated")))

    assert len(_derive(data)) == 0


# ---------------------------------------------------------------- T2.9 (supersession)


def _superseded_pair():
    """A pass-1 verdict that chose "escalated", withdrawn by a pass-2 re-read.

    The shape section repair produces: document.py links the two verdict decisions with
    dec:supersedes and the LATER reading is the live one. MEASURED on cbh-stem
    (2026-08-15): all 4 of its decisions that chose "escalated" carry an incoming
    dec:supersedes edge, which is why its region verdicts show zero escalated.
    """
    from iladub.etkl.decisionlog import ReadingRecorder

    g = Graph()
    brec = ReadingRecorder(g, EX.doc, 0).band(0)
    first = brec.record("verdict", VERDICT_OPTIONS, "escalated", "MERGE_AMBIGUOUS")
    second = brec.record("verdict", VERDICT_OPTIONS, "asserted", "pass-2 re-read admitted it")
    g.add((second, DEC.supersedes, first))
    return g, first


def test_a_superseded_escalation_is_not_furnished():
    """A withdrawn reading must not escalate a matter a later reading already resolved.

    Not in the plan's Task 2 contract — found by measuring cbh-stem. The guard is a
    HOLON-SCOPED closed-world selection between two PRESENT readings (the precedent and
    its classification are effective-chain.rq's header), not a fact derived from absence:
    ?d is bound by the surrounding pattern, so the NOT EXISTS is scoped to that decision.
    """
    data, _ = _superseded_pair()
    assert len(_derive(data)) == 0


# ---------------------------------------------------------------- T2.8 (the corpus census)

BFS = os.path.join(ROOT, "corpus", "gov-stats", "bfs-population-bilan-2023.pdf")
CBH = os.path.join(ROOT, "corpus", "ag-trade", "cbh-stem-2026-08-03.pdf")


def _census(g):
    escalating = {d for d in g.subjects(RDF.type, DEC.DecisionHolon)
                  if any(str(lbl) == "escalated"
                         for o in g.objects(d, DEC.chosen)
                         for lbl in g.objects(o, RDFS.label))}
    return (escalating,
            {d for d in escalating if list(g.objects(d, DEC.regarding))},
            {d for d in escalating if list(g.subjects(DEC.supersedes, d))})


@pytest.mark.corpus
@pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not populated")
def test_corpus_census_every_live_escalating_decision_is_furnished():
    """One expansion request per decision that chose "escalated", carries dec:regarding,
    and was NOT superseded.

    bfs-population is chosen because it escalates and NONE of its escalations are
    withdrawn (measured 2026-08-31 with _census itself: B=10, C=10, superseded=0,
    live=10); a test written against graincorp-stem or ons, which carry zero
    escalations, pins nothing. B - C is invariant 5's coverage hole.

    It replaces who-wfa (measured 2026-08-15: B=3, C=3, superseded=0), which R45 took
    to B=0 — a document that no longer escalates cannot pin this. apple was rejected
    though it escalates: 5 of its 15 are superseded (measured the same day), so it does
    not carry the "none withdrawn" property this test's choice rests on, and cbh-stem
    already covers the wholly-superseded case below.

    RE-RULED 2026-09-14 (R225 arm B, D2): **the `superseded == 0` guard is REMOVED, and the
    invariant it guarded is untouched and now harder to satisfy.** The widened adoption gate takes
    bfs p5, and adoption's admission holon is precisely what adds `dec:supersedes` to the bands it
    supersedes — so the "none withdrawn" property this test's SUBJECT CHOICE rested on is gone.
    Measured 2026-09-14: `B=10, C=10, B-C=0, superseded=4, live=6, requests=6`.

    WHY THIS IS A STRENGTHENING, not a relaxation. With `superseded=0`, `requests == live` and
    `requests == len(escalating)` were the SAME assertion — the test could not tell a derivation
    that respects supersession from one that ignores it. At 4 withdrawn and 6 live it can: a
    derivation blind to `dec:supersedes` furnishes 10 and fails here. bfs is now the only corpus
    document carrying live and withdrawn escalations AT ONCE (cbh-stem is wholly superseded, and
    the documents rejected above escalate nothing), so the mixed case has a fixture for the first
    time. (2026-09-30: since the box split, cbh-stem also has one live escalation, its residue;
    see its test below. 2026-10-02: R261 loop (b) withdraws that residue, so cbh-stem is wholly
    superseded again.)

    What replaces the guard is non-vacuity on the same axis: `live > 0`. A document whose
    escalations are ALL withdrawn pins nothing here — that is cbh-stem's test, below.
    """
    from iladub.etkl.document import compile_document

    g = compile_document(BFS).graph
    escalating, with_regarding, superseded = _census(g)
    live = with_regarding - superseded
    requests = set(_derive(g).subjects(RDF.type, DEC.ExpansionRequest))

    print(f"\nbfs-population: B(chose escalated)={len(escalating)} C(and dec:regarding)="
          f"{len(with_regarding)} B-C={len(escalating) - len(with_regarding)} "
          f"superseded={len(superseded)} live={len(live)} requests={len(requests)}")
    assert len(escalating) > 0, "chose a document that does not escalate — the test pins nothing"
    assert len(live) > 0, "chose a document whose escalations are ALL withdrawn — see cbh-stem"
    assert len(requests) == len(live)


@pytest.mark.corpus
@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not populated")
def test_corpus_cbh_furnishes_exactly_one_request_for_its_one_live_escalation_the_residue():
    """cbh-stem: every escalation that section repair withdraws furnishes nothing, and the one
    that stays live furnishes exactly one request. That one is the box split's residue.

    RENAMED AND RE-PINNED 2026-09-30 (box-split Task 4, controller ruling 2). This test was
    `test_corpus_a_wholly_superseded_document_furnishes_nothing`. Until the box split, cbh's
    region verdicts held zero "escalated" while 4 decisions chose it, all withdrawn by section
    repair, and the derivation furnished 0 requests. The split (spec
    2026-09-28-box-split-design.md § 3.3) leaves one residue band beside T1 and T2 on page 0.
    It holds `1,951,264`, the title line's orphan total (R-b: the totals family is deferred),
    and the four-line Note block. That band reads UNSUPPORTED_TABLE and is escalated
    KIND_NOT_SUPPORTED, and nothing supersedes it. Spec § 4 says how the residue reads is
    "measured and recorded", not engineered, and the controller accepted this reading as the
    recorded outcome (evidence 2026-09-28-box-split § 5.4, § 5.5).

    WHAT IS STILL EXACT. The mechanism assertions do not loosen:
    - the requests equal the escalated region verdicts;
    - the live decisions (chose "escalated", not superseded) equal those verdicts too.
    A derivation that ignored `dec:supersedes` would furnish 5 and fail. The one number that
    moved is cbh's live count, 0 to 1, and it is pinned exactly at 1. That one region is named
    structurally: the page-0 band holding `1,951,264`, with reason KIND_NOT_SUPPORTED.

    RE-READ AND RE-PINNED 2026-10-02 (R261 loop (b), Task 7): live count 1 -> 0. The name is
    kept, now historical, because `tests/corpus-manifest.ttl`'s cbh hold rationale and the
    append-only evidence cite it. The re-read: loop (b) binds `1,951,264` in the section-repair
    pass (`/r2`) as a total-of-totals `tab:PrintedTotal` (four table-level PrintedTotals as
    `tab:aggregates`, no `tab:totalOf`). It does so on the worker's `total_of_totals` AND the
    exact Decimal sum, carves the line out of band 9, and the remaining Note classifies
    `NON_TABLE` and is `ignored` (spec 2026-10-02-r261-grand-total-design.md § 0 concern 2,
    § 7 S5). R7 adopts that pass-2 band, so `/r2`'s band-9 verdict decision `dec:supersedes`
    the pass-1 `escalated` one: cbh is WHOLLY SUPERSEDED again (5 chose escalated, 5
    superseded, measured in evidence 2026-10-02-r261-grand-total-evidence.md § 7). The
    mechanism assertions stay exact. A derivation that ignored `dec:supersedes` would furnish
    5 and fail. The residue is still named structurally, and it is now pinned as WITHDRAWN:
    its pass-1 escalation is superseded by a decision that chose `ignored`. The Note is
    ignored, not read; this test records that, it does not endorse it.
    """
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document

    rep = compile_document(CBH)
    g = rep.graph
    escalating, _, superseded = _census(g)
    region_escalations = [(pi, i, r) for pi, p in enumerate(rep.pages)
                          for i, r in enumerate(p.regions) if r.verdict == "escalated"]
    requests = set(_derive(g).subjects(RDF.type, DEC.ExpansionRequest))

    print(f"\ncbh-stem: chose escalated={len(escalating)} superseded={len(superseded)} "
          f"region verdicts escalated={len(region_escalations)} requests={len(requests)}")
    assert len(requests) == len(region_escalations)
    assert len(escalating) - len(superseded) == len(region_escalations), \
        "a live escalating decision and the escalated region verdicts disagree"
    assert len(region_escalations) == 0, region_escalations
    # Non-vacuity: cbh still escalates in pass 1; every escalation is withdrawn, none absent.
    assert len(escalating) > 0 and superseded == escalating, (escalating, superseded)

    # The residue — the page-0 band that holds `1,951,264` — is withdrawn, not merely absent:
    # its region now reads `ignored` (the Note), and its pass-1 `escalated` verdict decision is
    # superseded by one that chose `ignored`.
    residue = [i for i, b in enumerate(page_bands(CBH, 0))
               if any(w.text == "1,951,264" for ln in b.lines for w in ln.words)]
    assert len(residue) == 1, residue
    assert rep.pages[0].regions[residue[0]].verdict == "ignored", rep.pages[0].regions[residue[0]]
    withdrawn = [d for d in superseded
                 if any(str(r).endswith(f"/p0#region{residue[0]}")
                        for r in g.objects(d, DEC.regarding))]
    assert len(withdrawn) == 1, withdrawn
    superseders = list(g.subjects(DEC.supersedes, withdrawn[0]))
    assert [str(lbl) for s in superseders for o in g.objects(s, DEC.chosen)
            for lbl in g.objects(o, RDFS.label)] == ["ignored"], superseders
