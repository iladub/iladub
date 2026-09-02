"""Spec 2026-09-02-the-body-starts-at-the-stub-design.md § 5 O5, the apple leg. Real document,
gitignored corpus/ — skips when absent, never in CI. Band indices measured 2026-09-02 (plan S4/S5).
These pin READINGS (levels, entries, tiling), never the score (spec § 1.4)."""
import os
import pytest
pytest.importorskip("pdfplumber")
from rdflib import Graph, URIRef
from iladub.etkl.compile import page_bands
from iladub.etkl.matrix import classify_matrix
from iladub.etkl.holon import assert_matrix_region
from iladub.etkl.tiling import region_tiles

pytestmark = pytest.mark.corpus
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")


def _band(page, idx):
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    return page_bands(APPLE, page)[idx]


def _asserted(band, page):
    mreg = classify_matrix(band)
    assert mreg is not None
    g = Graph()
    n = assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), page)
    assert region_tiles(g) is True
    return mreg, n


def test_p0_income_statement_header_is_three_levels():
    """Spec § 1.2: Three/Nine Months Ended over June 27,/June 28, over 2026/2025; 28 entries."""
    band = _band(0, 2)
    assert [w.text for w in band.lines[2].words] == ["2026", "2025", "2026", "2025"]
    mreg, n = _asserted(band, 0)
    assert mreg.body_line == 3
    assert sorted({x.level for x in mreg.col_tree}) == [0, 1, 2]
    assert len(mreg.leaf_rows) == 9 and n == 28


def test_p1_balance_sheet_header_is_two_levels():
    """Spec § 8 (measured after approval): June 27,/September 27, over 2026/2025; 14 entries.
    Confirmed 2026-09-02 (controller ruling, commit 80f0cdf, "Task 3b"): both matrix gates now
    count header levels at the DERIVED matrix_body_start rather than the raw header_body_split
    result, so this band's type_split=1/body_start=2 case is no longer refused before
    matrix_body_start runs (spec § 3.1's "use its result wherever they use split today")."""
    mreg, n = _asserted(_band(1, 2), 1)
    assert mreg.body_line == 2
    assert sorted({x.level for x in mreg.col_tree}) == [0, 1]
    assert n == 14


def test_p2_unruled_header_refuses_rather_than_dropping_ink():
    """Spec § 1.3 Finding B / § 3.2: 'Nine Months Ended' is three pdfplumber words on an unruled
    band; 'Months' and both 'June's would be carried by no node. Honest MATRIX_AMBIGUOUS."""
    band = _band(2, 2)
    assert band.rules == ()
    assert [w.text for w in band.lines[0].words] == ["Nine", "Months", "Ended"]
    assert classify_matrix(band) is None


def test_document_scope_adoption_is_pre_empted_and_recorded():
    """Spec § 1.4: once p1's header band asserts, adoption-candidate.rq's NOT EXISTS tab:EntryCell
    gate refuses the page-1 datagrid adoption. adopted (1,) -> (). Raised as R160, not fixed here.
    The score is printed, never asserted."""
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    from iladub.etkl.document import compile_document
    rep = compile_document(APPLE)
    print(f"apple score {rep.score:.4f} adopted {rep.adopted}")
    assert rep.adopted == ()
    reasons = [r.reason for p in rep.pages for r in p.regions]
    assert reasons.count("MATRIX_AMBIGUOUS") == 1          # p2 band 2 only; p0's is now asserted
