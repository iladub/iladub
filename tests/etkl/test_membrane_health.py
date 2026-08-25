"""holon:05 — the membrane reports its health. Oracles O1-O11 (spec 2026-08-25 §7).

Vehicles are chosen for cost, and every one of them is MEASURED (plan M1, M4, M8):
`false_transposed_pdf` compiles at document scope in ~1.1 s and carries the refusal lever;
the corpus specimens are used only where reachability ON REAL INPUT is the claim (O2).
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD

from iladub.etkl import membrane
from iladub.etkl.compile import _DOC, _validate
from iladub.etkl.decisionlog import DEC
from iladub.etkl.document import compile_document, _legs_for_document, _seal
from tests.etkl import fixtures as F

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ILADUB = Namespace("https://w3id.org/iladub#")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
ACT = URIRef(f"{_DOC}#membrane-validation")


def _cheap_document(tmp_path, name="false_transposed.pdf"):
    """The cheapest document-scope vehicle in the tree: 1.12 s, legs ('dec',), and it
    carries a NON-SUPERSEDED escalated decision — i.e. the refusal lever (plan M8)."""
    p = os.path.join(str(tmp_path), name)
    F.false_transposed_pdf(p)
    return compile_document(p)


CORPUS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "corpus")


def _corpus(rel):
    """Corpus PDFs are gitignored, so an absent one SKIPS visibly rather than failing —
    the discipline `tests/test_corpus.py:66-67` already uses."""
    path = os.path.join(CORPUS_ROOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"corpus not populated: {rel} (scripts/fetch_corpus.py)")
    return path


@pytest.fixture(scope="module")
def apple_report():
    """ONE apple compile, shared by O2's second and third legs — the saving Task 4's Step 1
    was told to go and measure, and it landed: `apple` refuses under the R127 lever, so the
    third leg no longer needs its own corpus document.

    MEASURED 2026-08-25 (`compile_document` on each of the three, then the lever applied):

        graincorp-stem   162.8 s   Intact     legs ('tab','dec')
        apple             34.4 s   Weakened   legs ('dec',)   10 non-superseded escalations
                                              → lever REFUSES, legs=('dec',), Compromised
        bfs               24.1 s   Weakened   legs ('dec',)   10 non-superseded escalations
                                              → lever REFUSES, legs=('dec',), Compromised

    So the plan's `bfs` → `apple` substitution is TAKEN: it removes a 24.1 s compile and the
    two legs stand on one specimen. (The plan's 30.6 s figure for `bfs` is its own M1
    measurement; 24.1 s is what this machine measured today. Either way the compile is gone.)

    MODULE-SCOPED, and the third leg therefore mutates a TRIPLE-IDENTICAL COPY rather than
    this graph: `_seal` writes in place, and a shared mutable graph would make the second leg's
    verdict depend on which test pytest ran first. A copy is the real compiled graph for every
    purpose either leg has — the derivation and the membrane read triples, not namespace
    bindings — and it keeps the two legs independent, which is the whole reason they are two
    tests and not one."""
    return compile_document(_corpus("financial/apple-fy2026q3-statements.pdf"))


def _one_more_rationale(graph):
    """The R127 lever: a SECOND `dec:rationale` on a NON-SUPERSEDED escalated decision.
    `escalation-furnish.rq` then carries it into a second `dec:condition`, which
    `dec:EventShape` caps at 1 (`dec-shapes.ttl:60-63`). Returns the decision it mutated.

    The target is READ OFF THE GRAPH, never hardcoded: a SUPERSEDED escalation furnishes
    nothing and is not a lever (plan M8). `sorted(...)[0]` because a corpus document offers
    TEN of them (measured above) and one is as good as another — but the choice must be
    deterministic, or a failure here would not reproduce.

    Distinct from `_the_escalated_decision` below, which asserts the escalated decision is
    UNIQUE and selects it through `dec:chosen` + its `rdfs:label`. That helper is the right
    one for a fixture whose shape a change should not be allowed to grow silently; this one is
    the only one a ten-escalation corpus document can use at all."""
    targets = [d for d in graph.subjects(DEC.escalatedTo, None)
               if not list(graph.subjects(DEC.supersedes, d))]
    assert targets, "vehicle broken: no non-superseded escalated decision to mutate"
    d = sorted(targets)[0]
    existing = list(graph.objects(d, DEC.rationale))
    assert len(existing) == 1, existing
    graph.add((d, DEC.rationale, Literal("une seconde raison", lang="fr")))
    return d


def test_membrane_refusal_is_an_assertionerror_subclass():
    """O11 (half): the producer-side guard is not softened. Every one of the repo's
    AssertionError interceptors is isinstance-based (plan M2), so a subclass is
    transparent — but only if it really is one.

    RE-MEASURED 2026-08-25, because M2's count does not reproduce: `git ls-files '*.py' |
    xargs grep -n AssertionError | grep -E "except |raises\\("` finds **7**, not 17 — one bare
    `except AssertionError` (tests/test_corpus.py:129) and six `pytest.raises`. M2's claim that
    matters is unaffected and stronger with fewer sites: ZERO of them compares
    `type(e) is AssertionError`."""
    assert issubclass(membrane.MembraneRefusal, AssertionError)


def test_validate_shapes_false_mints_no_validation_act(tmp_path):
    """O4 (half — the health half lands in Task 3): no validation means no act. Absence,
    never a fourth state (spec 4.5, third row)."""
    p = os.path.join(str(tmp_path), "false_transposed.pdf")
    F.false_transposed_pdf(p)
    rep = compile_document(p, validate_shapes=False)
    assert (ACT, RDF.type, ETKL.MembraneValidation) not in rep.graph
    assert list(rep.graph.objects(ACT, SH.conforms)) == []


def test_the_conformance_literal_is_xsd_boolean(tmp_path):
    """O8, mint side (review B6 — the one finding that fails UPWARD). A Literal('false')
    with no datatype makes a REFUSING membrane report Intact, because SPARQL's effective
    boolean value of a non-empty string is true.

    It also pins the act's OTHER two triples (review round 1, finding 1). The type and the
    `prov:used` edge were minted by no standing assertion: deleting either line left all six
    tests green, because the only test that mentioned the type mentioned it NEGATIVELY, and an
    absent triple satisfies a `not in` just as well as a suppressed one. Both are what Task 3's
    derivation keys on — `?act a etkl:MembraneValidation … prov:used ?doc` — so an unpinned mint
    there fails upward exactly the way B6 did: the health triple would simply never be
    constructed, and nothing would say so."""
    rep = _cheap_document(tmp_path)
    assert (ACT, RDF.type, ETKL.MembraneValidation) in rep.graph
    assert list(rep.graph.objects(ACT, PROV.used)) == [_DOC]
    values = list(rep.graph.objects(ACT, SH.conforms))
    assert len(values) == 1, values
    assert values[0].datatype == XSD.boolean, values[0]
    assert values[0].toPython() is True


def test_a_conforming_validation_names_no_refusing_leg(tmp_path):
    """Spec 2.3: _validate's third element is the legs that REFUSED, and it is () on every
    conforming validation. A leg appears only when it has something to say."""
    rep = _cheap_document(tmp_path)
    assert list(rep.graph.objects(ACT, ETKL.refusingLeg)) == []


def test_re_entering_an_unmutated_graph_is_a_no_op(tmp_path):
    """Plan M8's no-op claim: re-entering _seal on a graph nothing has touched validates
    again, reaches the same verdict, and leaves the act saying what it already said.

    RENAMED from the brief's `test_re_entering_the_seam_leaves_exactly_one_conformance_value`.
    It is true and worth keeping, but it does NOT pin O10 — see the substituted test below for
    the measurement that showed why."""
    rep = _cheap_document(tmp_path)
    g = rep.graph
    legs = _legs_for_document(rep.recognized, False)
    _seal(g, legs, True)                       # unmutated re-entry: a no-op (plan M8)
    values = list(g.objects(ACT, SH.conforms))
    assert len(values) == 1, values
    assert values[0].toPython() is True


def _the_escalated_decision(g: Graph) -> URIRef:
    """The one NON-SUPERSEDED decision holon whose chosen option is labelled `escalated` —
    the subject the seam-6 refusal lever attaches to. Asserted to be unique, so a fixture
    change that grows a second one fails here rather than picking one silently."""
    superseded = set(g.objects(None, DEC.supersedes))
    escalated = {h for h in g.subjects(DEC.chosen, None)
                 if h not in superseded
                 and any(str(lab) == "escalated"
                         for opt in g.objects(h, DEC.chosen)
                         for lab in g.objects(opt, RDFS.label))}
    assert len(escalated) == 1, escalated
    return escalated.pop()


def test_re_entering_the_seam_leaves_exactly_one_conformance_value(tmp_path):
    """O10 — plan M9, a hazard neither the spec nor the (a') ruling names. O2's third leg
    and O7 re-enter _seal on a graph that ALREADY carries the act its first pass minted.
    The act IRI is a function of the doc URI, so a second mint lands on the SAME subject:
    unless the mint replaces, one document ends up carrying sh:conforms true AND false,
    and therefore Intact AND Compromised, with nothing at runtime to refuse it.

    SUBSTITUTED, and the substitution is the point (CLAUDE.md rule 1; plan defect reported in
    the Task 2 report). The brief's form re-entered on an UNMUTATED graph, whose second pass
    returns the SAME verdict — and an rdflib Graph is a SET, so a non-replacing mint of an
    identical triple collapses to one value and the test passes with `graph.remove` DELETED.
    MEASURED: it did. M9's symptom is `sh:conforms = ['false','true']` — two DIFFERENT
    verdicts — so the re-entry must actually change the verdict, and only then does the missing
    replacement leave two values behind.

    The verdict is changed by the MEASURED lever, not a fixture (spec 2026-08-25 §4.5 / the
    seam-6 measurement): one added `dec:rationale` on a non-superseded escalated decision, which
    the seam's own re-furnish carries into a second `dec:condition`, which `dec:EventShape`'s
    `sh:maxCount 1` refuses. It is also why the seam had to begin at the furnish and not at the
    validation — a seam starting at `_validate` cannot be driven by this lever at all.

    THE LEVER IS `R127`, AND CLOSING `R127` INVALIDATES IT. That a language-tagged second
    `dec:rationale` — which CLAUDE.md § Serialization explicitly permits — makes every document
    containing it refuse at document scope is the open defect `R127`, not a property of this
    test's fixture. holon:05 deliberately leaves it open because this oracle depends on it. When
    a later loop caps `dec:rationale` or collapses the rationales in `escalation-furnish.rq`,
    THIS TEST WILL FAIL with `DID NOT RAISE MembraneRefusal` and nothing else will explain why:
    the fix is then to find another way to make the re-entry's verdict DIFFER from the first
    pass's, not to delete the test — the invariant it pins (the mint replaces) is untouched by
    R127's closure."""
    rep = _cheap_document(tmp_path)
    g = rep.graph
    assert [v.toPython() for v in g.objects(ACT, SH.conforms)] == [True]
    g.add((_the_escalated_decision(g), DEC.rationale,
           Literal("une seconde justification", lang="fr")))
    legs = _legs_for_document(rep.recognized, False)
    with pytest.raises(membrane.MembraneRefusal) as exc:
        _seal(g, legs, True)

    values = list(g.objects(ACT, SH.conforms))
    assert len(values) == 1, values                 # NOT ['false', 'true']
    assert values[0].toPython() is False
    assert list(g.objects(ACT, ETKL.refusingLeg)) == [Literal("dec")]
    # The refusal carries the refused graph ITSELF, not a copy — the whole reason the raise
    # became a subclass rather than staying a bare AssertionError.
    assert exc.value.graph is g
    assert exc.value.legs == ("dec",)
    assert str(exc.value).startswith("document-level facts failed dec: SHACL:")


def test_compiled_document_reports_membrane_health(tmp_path):
    """THE PRE-DECLARED ORACLE (tests/arc-manifest.ttl:359 — this name is fixed and the
    manifest names it; do not rename it). A compiled document carries exactly one health
    value, and it is one of the three."""
    rep = _cheap_document(tmp_path)
    doc = URIRef(_DOC)
    assert (doc, RDF.type, ETKL.CompiledDocumentHolon) in rep.graph
    values = list(rep.graph.objects(doc, ETKL.membraneHealth))
    assert len(values) == 1, values
    assert values[0] in (ETKL.Intact, ETKL.Weakened, ETKL.Compromised), values[0]


def test_the_three_values_discriminate(tmp_path):
    """O1 — THE FALSIFYING ORACLE. Three hand-built graph states must yield three DIFFERENT
    values. Expected values are computed BY HAND from the fixture (spec §3), never by
    running the query and recording what it said. Falsify by collapsing the IF to a
    constant: this test must fail."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    def act(conforms):
        g = Graph()
        g.add((ACT, RDF.type, ETKL.MembraneValidation))
        g.add((ACT, PROV.used, URIRef(_DOC)))
        g.add((ACT, SH.conforms, Literal(conforms)))
        return g

    def health(g):
        return list(interpret.run(MEMBRANE_HEALTH_RQ, g).objects(None, ETKL.membraneHealth))

    conforming_empty = act(True)                                    # hand-computed: Intact
    conforming_held = act(True)                                     # hand-computed: Weakened
    conforming_held.add((URIRef(f"{_DOC}#c1"), RDF.type, ILADUB.CandidateConcept))
    refusing = act(False)                                           # hand-computed: Compromised

    assert health(conforming_empty) == [ETKL.Intact]
    assert health(conforming_held) == [ETKL.Weakened]
    assert health(refusing) == [ETKL.Compromised]
    assert len({str(health(g)[0]) for g in
                (conforming_empty, conforming_held, refusing)}) == 3


def test_a_reviewed_candidate_no_longer_weakens_the_membrane(tmp_path):
    """Spec §4.3 invariant 2 — the ONLY test that exercises the `FILTER NOT EXISTS`, which is
    the query's one closed-world guard and the clause §4.3's last paragraph says "STAYS".

    ADDED AT REVIEW, from a measurement: as first shipped, deleting that FILTER left all
    twelve tests green. Run against four hand-built states, shipped `.rq` vs the clause
    deleted:

        conforming_empty     as-shipped=['Intact']      filter-deleted=['Intact']      same
        conforming_held      as-shipped=['Weakened']    filter-deleted=['Weakened']    same
        reviewed_candidate   as-shipped=['Intact']      filter-deleted=['Weakened']    DIFFERS
        refusing             as-shipped=['Compromised'] filter-deleted=['Compromised'] same

    Only the third discriminates, and nothing built one: `_cheap_document` is 1 candidate /
    0 promotions, so no fixture-driven test can reach it either. The report's traceability
    table had claimed `test_the_three_values_discriminate`'s Weakened row pinned this; the
    measurement refutes that — that row fires identically with the negation deleted.

    A SEPARATE TEST rather than a fourth graph inside `test_the_three_values_discriminate`,
    for two reasons: that test's closing assertion counts THREE distinct values, and a fourth
    state deriving `Intact` (a value already in the set) would have to rewrite it — and it is
    plan-supplied text a deferred review item is already looking at. Its name would also stop
    describing it. What it pins is different in kind: not that the three values discriminate,
    but that a proposition WHICH HAS BEEN DECIDED is no longer held at the membrane — which is
    the promotion epistemics of CLAUDE.md §3 read back out of the health signal."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    g = Graph()
    g.add((ACT, RDF.type, ETKL.MembraneValidation))
    g.add((ACT, PROV.used, URIRef(_DOC)))
    g.add((ACT, SH.conforms, Literal(True)))
    cand, pd = URIRef(f"{_DOC}#c1"), URIRef(f"{_DOC}#pd1")
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))

    health = list(interpret.run(MEMBRANE_HEALTH_RQ, g).objects(None, ETKL.membraneHealth))
    assert health == [ETKL.Intact], health   # NOT Weakened: the candidate is no longer HELD


def test_a_document_compiled_without_the_membrane_has_no_health(tmp_path):
    """O4 — ABSENCE, NEVER A FOURTH STATE. No validation means no act means the WHERE has
    no support means no health triple. `validate_shapes` is the only route into this
    state — spec §5.4 refuted the zero-legs one."""
    p = os.path.join(str(tmp_path), "false_transposed.pdf")
    F.false_transposed_pdf(p)
    rep = compile_document(p, validate_shapes=False)
    assert list(rep.graph.objects(URIRef(_DOC), ETKL.membraneHealth)) == []
    assert (URIRef(_DOC), RDF.type, ETKL.CompiledDocumentHolon) not in rep.graph


def test_health_is_re_derived_not_stored(tmp_path):
    """O5 — NOT A STORED LABEL. Strip the health triple and the type triple, re-run the
    .rq, and the re-derived triples equal what was stripped, compared AS SETS OF TRIPLES
    (RDF has no byte identity without canonicalisation — spec §3). This is explicitly NOT
    the falsifying oracle, and it says nothing about the validation act."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    stripped = set(g.triples((doc, ETKL.membraneHealth, None))) | \
               set(g.triples((doc, RDF.type, ETKL.CompiledDocumentHolon)))
    assert stripped, "nothing to strip — the compile did not mint health"
    for t in stripped:
        g.remove(t)
    assert set(interpret.run(MEMBRANE_HEALTH_RQ, g)) == stripped


def test_a_slipped_datatype_yields_no_health_rather_than_intact(tmp_path):
    """O8, READ side (review B6 — the only finding that failed UPWARD). A validation act
    carrying Literal('false') with no datatype, or xsd:string, must yield NO health triple
    — and specifically NOT Intact, which is what SPARQL's effective boolean value of a
    non-empty string would otherwise produce. This fails DOWNWARD, into the silence spec
    §4.5's third row already licenses."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    for slipped in (Literal("false"), Literal("false", datatype=XSD.string)):
        g = Graph()
        g.add((ACT, RDF.type, ETKL.MembraneValidation))
        g.add((ACT, PROV.used, URIRef(_DOC)))
        g.add((ACT, SH.conforms, slipped))
        out = interpret.run(MEMBRANE_HEALTH_RQ, g)
        assert len(out) == 0, (slipped, list(out))


def test_re_entering_the_seam_leaves_exactly_one_health_value(tmp_path):
    """ADDED IN TASK 3, from a MEASUREMENT rather than from the brief (CLAUDE.md rule 1 —
    a plan-supplied step is a proposition). The brief's Step 4 says only "run it on both
    paths"; wired exactly that way (`graph += interpret.run(...)`), M9's
    replace-don't-accumulate hazard applies to the HEALTH triple just as it does to
    `sh:conforms`, which Task 2 fixed for the act ALONE.

    MEASURED before the fix, driving the same R127 lever as the test above:
        health: ['…#Weakened']
        refused; conforms: [False]
        health after re-entry: ['…#Compromised', '…#Weakened']
    That is precisely the harm spec §4.3 invariant 3 names for a unioned graph — two health
    values on one subject, with nothing at runtime to refuse them — reached by re-entry
    instead. `?doc` binds from `prov:used`, and `_DOC` is one constant IRI (`compile.py:22`),
    so the second derivation lands on the SAME subject; and health is minted AFTER the
    membrane has run (spec §4.2), so no shape ever sees the contradiction.

    Unlike the derivation's own idempotence (`test_health_is_re_derived_not_stored`), this
    needs the verdict to CHANGE: a re-entry that reaches the same verdict re-derives an
    identical triple, and an rdflib Graph is a set. Same lever, same R127 caveat as the test
    above: when a later loop closes R127 this fails with DID NOT RAISE, and the fix is
    another way to make the verdicts differ — not deleting the test."""
    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    assert list(g.objects(doc, ETKL.membraneHealth)) == [ETKL.Weakened]
    g.add((_the_escalated_decision(g), DEC.rationale,
           Literal("une seconde justification", lang="fr")))
    legs = _legs_for_document(rep.recognized, False)
    with pytest.raises(membrane.MembraneRefusal) as exc:
        _seal(g, legs, True)

    values = list(g.objects(doc, ETKL.membraneHealth))
    assert len(values) == 1, values            # NOT [Weakened, Compromised]
    assert values[0] == ETKL.Compromised, values[0]
    # the refused graph is the one that carries it — the whole point of the subclass
    assert list(exc.value.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Compromised]


@pytest.mark.corpus
def test_intact_and_weakened_are_reachable_on_real_input(apple_report):
    """O2, legs 1 and 2 — REACHABILITY ON REAL INPUT. NOT an independence check: these
    expectations were derived with the same held-candidate pattern the query uses, so if
    that reading of "held" is wrong, query and expectation share the error (spec §3, review
    P3). O1 is what carries independence. If a value cannot be produced from real input,
    THIS TEST FAILS AND SAYS WHICH — it does not fall back to a fixture.

    graincorp-stem is NOT interchangeable with a cheaper Intact document: it is the specimen
    that carries the point that health is not the score (spec §1, review B8) — it scores
    0.9655 with 77 escalated tokens of unread ink and is correctly Intact, because nothing
    is HELD at the membrane.

    Reads `apple_report.graph` and never writes it; O2's third leg mutates a copy."""
    doc = URIRef(_DOC)
    stem = compile_document(_corpus("ag-trade/graincorp-stem-2026-07-31.pdf"))
    assert list(stem.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Intact]

    assert list(apple_report.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Weakened]


@pytest.mark.corpus
def test_compromised_is_reachable_by_the_r127_lever_on_a_real_graph(apple_report):
    """O2, leg 3 — AMENDED 2026-08-25, option (a'), and the concession is written here
    rather than engineered around.

    COMPROMISED IS NOT REACHABLE FROM ANY PUBLIC INPUT TODAY. Measured on three independent
    routes: every tab-side lever refuses at the PAGE gate (`compile.py:1173`) before document
    validation is reached, and no compile can mint a second `dec:rationale`
    (`BandRecorder.record` writes exactly one, and the four decision-URI namespaces are
    disjoint). So this leg takes a REAL compiled corpus graph, adds ONE triple, and re-enters
    the REAL seam: no monkeypatch of `validate`/`_validate`, no `validate_shapes=False`, no
    hand-built graph.

    THE LEVER IS R127 — `dec:rationale` is uncapped while `dec:condition` is capped at 1, and
    CLAUDE.md explicitly permits language-tagged rationale literals. It is a latent REAL
    defect this loop deliberately does not fix, because it is the only measured route to this
    value. CLOSING R127 WITHOUT RE-HOMING THIS LEG TURNS THIS TEST RED FOR AN INVISIBLE
    REASON.

    VEHICLE SUBSTITUTED, and the substitution is the one the plan authorised in advance:
    `apple-fy2026q3-statements`, not `bfs-population-bilan-2023`. Step 1 measured apple's
    lever end-to-end (see `apple_report`) — it refuses, with `legs == ('dec',)` — so the leg
    rides a compile O2's second leg already pays for and one corpus document leaves the suite.

    THE CONTROL ARM IS `Weakened`, NOT `Intact`, and that is a MEASURED PLAN DEFECT rather
    than a vehicle swap: the plan asserted `Intact` for `bfs`, and `bfs` measures `Weakened`
    too (24.1 s compile, 2026-08-25). Neither candidate vehicle was ever Intact. Asserting the
    measured value is what makes this leg say something: the health value TRANSITIONS
    Weakened → Compromised across the mutation, so the added triple is demonstrably what moved
    it, which a control arm reading `Intact` could not have shown on either document.

    The mutation lands on a COPY of the module-scoped graph, so this leg cannot perturb the
    reachability leg above; the copy is triple-identical and is the real compiled graph for
    everything the furnish, the membrane and the derivation read."""
    doc = URIRef(_DOC)
    g = Graph()
    g += apple_report.graph
    assert list(g.objects(doc, ETKL.membraneHealth)) == [ETKL.Weakened], "control arm broken"

    _one_more_rationale(g)
    with pytest.raises(membrane.MembraneRefusal) as exc:
        _seal(g, _legs_for_document(apple_report.recognized, False), True)
    assert exc.value.legs == ("dec",), exc.value.legs
    assert list(exc.value.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Compromised]


def test_an_unmutated_re_entry_still_conforms(tmp_path):
    """O2's CONTROL ARM — the thing the (a') ruling explicitly left for the plan to measure.
    `escalation-furnish.rq` runs a second time over a graph already carrying its own output;
    that must be a no-op and the graph must still conform, or the leg above proves nothing
    about the mutation. MEASURED before this plan: 0 triples added, conforms=True.
    Structural, not incidental — `?req` is bound `IRI(CONCAT(STR(?d),"-expansion"))`, a pure
    function of `?d` (`escalation-furnish.rq:56-59`).

    SUBSTITUTED (CLAUDE.md rule 1 — a plan-supplied test is a proposition). The plan asserted
    the re-entered health is `ETKL.Intact`; `_cheap_document` measures `ETKL.Weakened`:

        $ ./.venv/bin/python -c "…compile_document(false_transposed.pdf)…"
        health: [rdflib.term.URIRef('https://w3id.org/iladub/etkl#Weakened')]

    and `test_re_entering_the_seam_leaves_exactly_one_health_value` above already asserts
    Weakened on the same vehicle, one screen up — so the plan contradicted a shipped
    measurement, not merely an unmeasured guess. The substituted form is STRICTLY STRONGER
    than a hardcoded value: it pins that the health value is UNCHANGED by the re-entry, which
    is the claim the plan was reaching for, and it additionally pins the conformance verdict
    the test's own name promises and the plan never checked."""
    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    before_len = len(g)
    before_health = list(g.objects(doc, ETKL.membraneHealth))
    assert before_health == [ETKL.Weakened], before_health
    _seal(g, _legs_for_document(rep.recognized, False), True)
    assert len(g) == before_len, "the re-entry was not a no-op"
    assert list(g.objects(doc, ETKL.membraneHealth)) == before_health
    assert [v.toPython() for v in g.objects(ACT, SH.conforms)] == [True]


def test_a_promoted_candidate_does_not_weaken_a_document(tmp_path):
    """O3 — PROMOTION IS NOT HELD, ON A REAL EXECUTION PATH. Vehicle: the caption-wrap
    fixture compiled AT DOCUMENT SCOPE with a proposer wired, at the default
    `validate_shapes=True` (plan M4: 2 candidates, 2 promotions, 0 held, 3.4 s — re-measured
    2026-08-25: 2 promotions, 2 candidates, 0 unreviewed, Intact). NOT a hand-built graph and
    NOT a corpus document — M1 measured promoted == 0 on all seven corpus documents, so no
    corpus specimen can exercise this clause at all.

    This is the ONLY test in the file that reaches the `FILTER NOT EXISTS` through a COMPILE.
    `test_a_reviewed_candidate_no_longer_weakens_the_membrane` above pins the same clause on a
    hand-built graph, and the pair is not redundant: that one proves the query discriminates,
    this one proves a real compile can actually produce the state it discriminates on.
    Falsify: delete the FILTER NOT EXISTS; held becomes 2 and this must fail."""
    p = os.path.join(str(tmp_path), "caption_wrap.pdf")
    F.caption_wrap_report_pdf(p)
    from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
    prop = RowRoleProposal(("furniture", "continuation"), 0.85, "date caption + wrap fragment")
    rep = compile_document(p, row_role_proposer=FakeRowRoleProposer(prop))

    promotions = list(rep.graph.subjects(RDF.type, ILADUB.PromotionDecision))
    assert promotions, "vehicle broken: no promotion, so this oracle proves nothing"
    reviewed = {c for pd in promotions for c in rep.graph.objects(pd, ILADUB.reviews)}
    candidates = set(rep.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert candidates and candidates <= reviewed, (candidates - reviewed)
    assert list(rep.graph.objects(URIRef(_DOC), ETKL.membraneHealth)) == [ETKL.Intact]


def test_the_minted_nodes_perturb_no_verdict(tmp_path):
    """O6 — spec §2.1 held as a regression rather than a one-off measurement. Re-validating
    a graph that carries the health triple, the type triple and the validation act yields
    the same verdict as before they were added, ON BOTH LEGS. Safe because none of the five
    wired shape files names an `etkl:` term and `etkl-holons.ttl` is not in `_FULL_ONT`
    (plan M6).

    BOTH LEGS deliberately, even though `_cheap_document` itself only RUNS ('dec',): the
    claim is about the five minted triples, and a `tab` shape that happened to name an
    `etkl:` term would be invisible to a dec-only validation. Re-measured 2026-08-25:
    5 minted triples, before=(True, ()) after=(True, ())."""
    rep = _cheap_document(tmp_path)
    g = rep.graph
    minted = set(g.triples((None, None, ETKL.MembraneValidation))) | \
             set(g.triples((ACT, None, None))) | \
             set(g.triples((URIRef(_DOC), ETKL.membraneHealth, None))) | \
             set(g.triples((URIRef(_DOC), RDF.type, ETKL.CompiledDocumentHolon)))
    assert minted, "nothing was minted — this oracle would be vacuous"
    after = _validate(g, ("tab", "dec"))
    before_graph = Graph()
    for t in g:
        if t not in minted:
            before_graph.add(t)
    before = _validate(before_graph, ("tab", "dec"))
    assert before[0] == after[0] and before[2] == after[2], (before[0], after[0])


def test_the_refusal_carries_the_graph(tmp_path):
    """O7 — THE HIGHEST-RISK ORACLE IN THE SET. Shares its SEAM with O2's third leg (ruled
    2026-08-25): the same real-graph-plus-one-triple mutation through the same `_seal`. It no
    longer shares that leg's VEHICLE — Step 1 moved the third leg onto `apple`, and this
    oracle is a claim about the exception object, not about real input, so it keeps the 1.1 s
    fixture and pays no corpus cost.

    A forced non-conforming document raises `MembraneRefusal`; the raised object's `.graph`
    carries `<doc> etkl:membraneHealth etkl:Compromised`; and a bare `except AssertionError`
    still catches it, because every one of the repo's interceptors is isinstance-based and
    none compares `type(e) is AssertionError`.

    THAT COUNT IS **7**, not plan M2's 17 — the census does not reproduce, and the corrected
    figure is derived once, in `test_membrane_refusal_is_an_assertionerror_subclass` above;
    this docstring cites it rather than re-deriving it (CLAUDE.md rule 6). The command there
    now returns 9 because its own two docstring lines match themselves, so the form that
    reproduces 7 on this branch is:

        $ git ls-files '*.py' | xargs grep -n AssertionError | grep -E "except |raises\\(" \\
              | grep -v test_membrane_health.py | wc -l
        7

    M2's substantive claim is unaffected and is stronger with fewer sites.
    Falsify: revert to a bare AssertionError; this must fail."""
    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    _one_more_rationale(g)
    with pytest.raises(AssertionError) as exc:          # deliberately the BASE class
        _seal(g, _legs_for_document(rep.recognized, False), True)
    assert isinstance(exc.value, membrane.MembraneRefusal)
    assert exc.value.graph is g
    assert list(exc.value.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Compromised]
    assert str(exc.value).startswith("document-level facts failed dec: SHACL:")
