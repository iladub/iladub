"""Loop N — R35: subtotal confirmation over the LOGICAL table. Red until the
document-level pass lands."""
from rdflib import RDF
from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import cut_group_two_page_pdf


def test_cut_group_subtotal_confirms_at_document_level(tmp_path):
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 2
    aggs = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
    # the page-1 subtotal is confirmed (page-locally it cannot be)
    p1_aggs = [a for a in aggs if "/p1" in str(a)]
    assert p1_aggs, "cut-group subtotal must confirm against page-0 members"
    # and its aggregates edges CROSS the member tables
    for a in p1_aggs:
        members = list(rep.graph.objects(a, TAB.aggregates))
        assert any("/p0" in str(m) for m in members), members


def test_chain_arithmetic_is_reported_honestly(tmp_path):
    """The reconciliation ledger (loop N): what the document window changed, counted.

    On the cut-group fixture the numbers are known exactly — page-locally the `SUB`/450 row
    cannot confirm (its only visible member is V3=200), and the logical table confirms it
    against all three voyages. So: 0 page-confirmed, 1 document-confirmed, 0 retracted,
    1 newly-confirmed, no abstention. Retraction being ZERO here is the honest half: the
    wider window ADDED a subtotal and took none away."""
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    (a,) = rep.arithmetic
    assert a.chain == rep.chains[0]
    assert (a.page_confirmed, a.document_confirmed, a.retracted, a.newly_confirmed) == \
           (0, 1, 0, 1), a
    assert a.abstained is None


def test_single_page_and_case1_untouched(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf, two_page_unrelated_pdf
    p1 = str(tmp_path / "single.pdf"); simple_table_pdf(p1)
    single, doc = compile_tables(p1), compile_document(p1)
    assert doc.score == single.score
    # the reconciliation pass must not touch a single-page document's typing
    # (URIs are page-scoped in the driver, so compare counts, not subjects):
    assert len(list(doc.graph.subjects(RDF.type, TAB.DetectedAggregationRow))) == \
           len(list(single.graph.subjects(RDF.type, TAB.DetectedAggregationRow)))
    assert doc.arithmetic == ()   # a one-member chain is the page-local window: never re-run
    p2 = str(tmp_path / "unrel.pdf"); two_page_unrelated_pdf(p2)
    rep = compile_document(p2)
    assert rep.recognized == ()   # the document pass never runs across unrecognized pages
    assert rep.arithmetic == ()
