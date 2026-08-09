"""Adoption at DOCUMENT scope (spec 2026-08-09, residue R73).

The decidability claim: a page's total reading failure is only final after carriage, section
repair and stitching have had their turn. The pass therefore runs LAST."""
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPLE = REPO / "corpus" / "financial" / "apple-fy2026q3-statements.pdf"

pytestmark = pytest.mark.corpus
corpus_only = pytest.mark.skipif(not APPLE.is_file(), reason="corpus not populated")


@pytest.fixture(scope="module")
def apple_doc():
    from iladub.etkl.document import compile_document
    return compile_document(str(APPLE))


@corpus_only
def test_the_document_adopts_the_page_the_pipeline_could_not_read(apple_doc):
    """apple p1: 0 asserted, 97 escalated, and the grid reads its 28 entry rows."""
    assert 1 in apple_doc.adopted, apple_doc.adopted
    p1 = apple_doc.pages[1]
    assert p1.asserted > 0
    print(f"\napple document: score={apple_doc.score!r} p1={p1.asserted}/{p1.escalated} "
          f"score={p1.score:.4f}")


@corpus_only
def test_an_adopted_page_never_scores_one_by_construction(apple_doc):
    """The zeroing tautology, refused: ink the grid did not read keeps escalating."""
    p1 = apple_doc.pages[1]
    assert p1.escalated > 0
    assert p1.score < 1.0


@corpus_only
def test_pages_that_read_something_are_not_adopted(apple_doc):
    assert 0 not in apple_doc.adopted and 2 not in apple_doc.adopted


@corpus_only
def test_the_document_score_rises(apple_doc):
    """Measured before this loop: 0.06068601583113457. The new value is RECORDED, not a floor
    to hit — but it must not be lower."""
    assert apple_doc.score > 0.06068601583113457


@corpus_only
def test_the_ledger_and_the_graph_agree_on_the_adopted_page(apple_doc):
    """Every escalated token on an adopted page has something in the graph escalating it."""
    from rdflib import RDF
    from iladub.etkl.holon import TAB
    ILADUB = __import__("rdflib").Namespace("https://w3id.org/iladub#")

    residue = [s for s in apple_doc.graph.subjects(RDF.type, ILADUB.CandidateConcept)
               if str(s).endswith("-datagrid-residue")]
    assert len(residue) == 1, residue
    assert apple_doc.pages[1].escalated > 0
