"""Loop O — R33: stitching is licensed by page-invariance, not recognition alone.
Red until the licence lands (Tasks 2-3)."""
from rdflib import RDF
from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import (case3_with_subtotals_pdf,
                                 bare_identical_two_page_pdf,
                                 two_page_unrelated_pdf)


def test_marked_case3_does_not_stitch(tmp_path):
    """Differing per-page banners = non-invariant continuation content -> refuse."""
    for conflicting in (False, True):
        pdf = str(tmp_path / f"c3-{conflicting}.pdf")
        case3_with_subtotals_pdf(pdf, conflicting_labels=conflicting)
        rep = compile_document(pdf)
        assert all(len(c) == 1 for c in rep.chains), rep.chains
        assert not list(rep.graph.subjects(None, TAB.continuesTable)) \
            or not any(True for _ in rep.graph.subject_objects(TAB.continuesTable))
        # page-local subtotals keep their page-local confirmations (no window widening)
        aggs = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
        assert aggs, "page-local subtotals must remain confirmed"


def test_bare_identical_still_stitches(tmp_path):
    """No distinguishing marks -> a fluent reader reads ONE table -> stitching is
    the correct reading (the invariant cuts this way; registered as the narrowed
    residual, not a defect)."""
    pdf = str(tmp_path / "bare.pdf")
    bare_identical_two_page_pdf(pdf)
    rep = compile_document(pdf)
    assert any(len(c) == 2 for c in rep.chains), rep.chains


def test_unrelated_pages_still_never_stitch(tmp_path):
    pdf = str(tmp_path / "unrel.pdf")
    two_page_unrelated_pdf(pdf)
    rep = compile_document(pdf)
    assert rep.recognized == ()


# --------------------------------------------------------------- the LAW itself (task 2)
# These probe the AXIOM directly, over hand-built evidence: no PDF, no compile, no gate.
# Facts are `(text, page_side, below_its_own_table, page_ordinal)` with page_side 0 = the
# PRIOR page N-1 and 1 = the CONTINUATION page N. The law is V4 (François's call): page N's
# ABOVE-table blocks are constrained STRICTLY, EITHER page's BELOW-table blocks are
# constrained modulo that page's own printed ordinal, and page N-1's above-table blocks are
# unconstrained. See vocab/queries/continuation-licence.rq for the law in full.

def test_licence_law_probes():
    from iladub.etkl.document import licence_evidence_from_facts, is_licensed
    invariant_footer = [("Footer note", 0, True, 1), ("Footer note", 1, True, 2)]
    assert is_licensed(licence_evidence_from_facts(invariant_footer))
    differing_banner = [("STORE ALPHA", 0, False, 1), ("STORE BETA", 1, False, 2)]
    assert not is_licensed(licence_evidence_from_facts(differing_banner))
    head_only_title = [("GRAIN REPORT", 0, False, 1)]    # head furniture: unconstrained
    assert is_licensed(licence_evidence_from_facts(head_only_title))
    cur_page_extra = [("A fresh section", 1, False, 2)]  # non-invariant on the continuation
    assert not is_licensed(licence_evidence_from_facts(cur_page_extra))
    cur_page_extra_tail = [("A fresh section", 1, True, 2)]   # ...on either side of its table
    assert not is_licensed(licence_evidence_from_facts(cur_page_extra_tail))
    empty = []
    assert is_licensed(licence_evidence_from_facts(empty))   # bare documents license


def test_licence_law_tails_are_invariant_modulo_the_printed_page_ordinal():
    """Clause (b), V4: the stem's own footer shape — one invariant sentence plus the page
    number. Each side is normalized by ITS OWN emitted ordinal, so the numbers cancel and
    nothing else does."""
    from iladub.etkl.document import licence_evidence_from_facts, is_licensed
    numbered = [("GrainCorp advise ... subject to change 1", 0, True, 1),
                ("GrainCorp advise ... subject to change 2", 1, True, 2)]
    assert is_licensed(licence_evidence_from_facts(numbered))
    # a tail that differs by anything OTHER than its ordinal is still content, not furniture
    worded = [("Prepared for Alpha report", 0, True, 1),
              ("Prepared for Beta report", 1, True, 2)]
    assert not is_licensed(licence_evidence_from_facts(worded))
    # ...and the ordinal cancels only where it IS the ordinal: page 1's '2' is not page 2's
    wrong_number = [("Sheet 2 of 9", 0, True, 1), ("Sheet 3 of 9", 1, True, 2)]
    assert not is_licensed(licence_evidence_from_facts(wrong_number))


def test_licence_law_over_normalization_refuses_conservatively():
    """DOCUMENTED COST of clause (b) (query header, §7): an ordinal's digits occurring
    ELSEWHERE in a tail block over-normalize — each side cancels its own ordinal, so two
    genuinely invariant tails normalize differently and the pair REFUSES. Refusal is the
    safe direction (the pair stays two independent documents), and it is pinned here so the
    behaviour is a stated property rather than a surprise."""
    from iladub.etkl.document import licence_evidence_from_facts, is_licensed
    same_text_incidental_digit = [("Depot 1 line", 0, True, 1), ("Depot 1 line", 1, True, 2)]
    assert not is_licensed(licence_evidence_from_facts(same_text_incidental_digit))
    # the same two blocks, with no digit to cancel, license — isolating the cause
    same_text_no_digit = [("Depot line", 0, True, 1), ("Depot line", 1, True, 2)]
    assert is_licensed(licence_evidence_from_facts(same_text_no_digit))


def test_licence_law_ignores_the_prior_head_side_but_not_its_tail():
    """The asymmetry is load-bearing: the same non-invariant block licenses or refuses
    depending ONLY on which side of the prior page's table it sits."""
    from iladub.etkl.document import licence_evidence_from_facts, is_licensed
    head = [("PRINTED 31 JULY", 0, False, 1), ("Footer", 0, True, 1), ("Footer", 1, True, 2)]
    assert is_licensed(licence_evidence_from_facts(head))
    tail = [("PRINTED 31 JULY", 0, True, 1), ("Footer", 0, True, 1), ("Footer", 1, True, 2)]
    assert not is_licensed(licence_evidence_from_facts(tail))


def _pair_evidence(pdf):
    """The licence evidence for the (0, 1) pair of a two-page fixture, as Task 3 will emit it."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import _recognition_blocks, licence_evidence
    prev_bands, cur_bands = page_bands(pdf, 0), page_bands(pdf, 1)
    prev_blocks, cur_blocks = _recognition_blocks(prev_bands), _recognition_blocks(cur_bands)
    return licence_evidence(prev_bands, max(prev_blocks), cur_bands, min(cur_blocks), 0, 1)


def test_marked_case3_evidence_refuses_the_licence(tmp_path):
    """Evidence level, ahead of the gate (Task 3 wires it): the pinned case-3 shape's
    DIFFERING per-page banners are exactly the non-invariant continuation-page content
    clause (a) reads, so the licence refuses the pair the recognition AXIOM licensed."""
    from iladub.etkl.document import is_licensed
    for conflicting in (False, True):
        pdf = str(tmp_path / f"c3ev-{conflicting}.pdf")
        case3_with_subtotals_pdf(pdf, conflicting_labels=conflicting)
        assert not is_licensed(_pair_evidence(pdf))


def test_bare_identical_evidence_licenses(tmp_path):
    """The other direction of the same invariant: no marks, nothing to refuse on."""
    from iladub.etkl.document import is_licensed
    pdf = str(tmp_path / "bareev.pdf")
    bare_identical_two_page_pdf(pdf)
    assert is_licensed(_pair_evidence(pdf))
