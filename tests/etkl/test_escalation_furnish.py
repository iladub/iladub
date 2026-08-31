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
    # The datagrid.py:695-697 shape: a dec:DecisionHolon minted without going through
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
    assert len(superseded) == 0, "chose a document whose escalations are withdrawn — see cbh-stem"
    assert len(requests) == len(live)


@pytest.mark.corpus
@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not populated")
def test_corpus_a_wholly_superseded_document_furnishes_nothing():
    """cbh-stem's region verdicts carry zero "escalated" while 4 decisions chose it — every
    one withdrawn by section repair. The derivation must agree with the REGION verdict, or
    it escalates four resolved matters to a human (G4: a moved escalation count is a defect).
    """
    from iladub.etkl.document import compile_document

    rep = compile_document(CBH)
    escalating, _, superseded = _census(rep.graph)
    region_escalations = [r for p in rep.pages for r in p.regions if r.verdict == "escalated"]
    requests = set(_derive(rep.graph).subjects(RDF.type, DEC.ExpansionRequest))

    print(f"\ncbh-stem: chose escalated={len(escalating)} superseded={len(superseded)} "
          f"region verdicts escalated={len(region_escalations)} requests={len(requests)}")
    assert len(escalating) == len(superseded), "cbh-stem's escalations are no longer all withdrawn"
    assert len(requests) == len(region_escalations) == 0
