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
