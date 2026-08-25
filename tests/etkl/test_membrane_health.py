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
