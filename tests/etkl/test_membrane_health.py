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
