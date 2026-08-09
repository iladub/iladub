"""Adoption at DOCUMENT scope (spec 2026-08-09, residue R73).

The decidability claim: a page's total reading failure is only final after carriage, section
repair and stitching have had their turn. The pass therefore runs LAST."""
import pytest
from pathlib import Path

from rdflib import Namespace, RDF, URIRef

REPO = Path(__file__).resolve().parents[2]
APPLE = REPO / "corpus" / "financial" / "apple-fy2026q3-statements.pdf"
QDIR = REPO / "vocab" / "queries"
ILADUB = Namespace("https://w3id.org/iladub#")

pytestmark = pytest.mark.corpus
corpus_only = pytest.mark.skipif(not APPLE.is_file(), reason="corpus not populated")

ADOPTED_PAGE = 1


@pytest.fixture(scope="module")
def apple_doc():
    from iladub.etkl.document import compile_document
    return compile_document(str(APPLE))


def _page_doc(p=ADOPTED_PAGE):
    from iladub.etkl.document import page_doc_uri
    return page_doc_uri(p)


def _superseded(rep):
    """The band indices the grid superseded. Region index IS band index for the first
    `len(bands)` entries (the contract Task 3 pins), so these are band indices."""
    return [i for i, r in enumerate(rep.regions) if r.verdict == "superseded"]


def _run(name, graph, region):
    q = (QDIR / name).read_text(encoding="utf-8")
    return [r.asdict() for r in graph.query(q, initBindings={"region": region})]


@corpus_only
def test_the_document_adopts_the_page_the_pipeline_could_not_read(apple_doc):
    """apple p1: 0 asserted, 97 escalated, and the grid reads its 28 entry rows."""
    assert ADOPTED_PAGE in apple_doc.adopted, apple_doc.adopted
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert p1.asserted > 0
    print(f"\napple document: score={apple_doc.score!r} p1={p1.asserted}/{p1.escalated} "
          f"score={p1.score:.4f}")


@corpus_only
def test_an_adopted_page_never_scores_one_by_construction(apple_doc):
    """The zeroing tautology, refused: ink the grid did not read keeps escalating."""
    p1 = apple_doc.pages[ADOPTED_PAGE]
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
def test_the_adopted_pages_own_ledger_adds_up(apple_doc):
    """The report's totals ARE the sum of its per-band token counts — no band's ink is
    counted twice and none goes missing between the ledger and the score."""
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert sum(r.tokens_asserted for r in p1.regions) == p1.asserted
    assert sum(r.tokens_escalated for r in p1.regions) == p1.escalated
    assert p1.score == p1.asserted / (p1.asserted + p1.escalated)


@corpus_only
def test_the_ledger_and_the_graph_agree_on_the_adopted_page(apple_doc):
    """Every escalated token on an adopted page has something in the graph escalating it,
    and it is the SAME count the report books.

    Scoped to this page's own adoption doc URI: a global scan would pass on a second adopting
    page's residue and would never notice this one had vanished."""
    page_doc = _page_doc()
    p1 = apple_doc.pages[ADOPTED_PAGE]

    residue = [s for s in apple_doc.graph.subjects(RDF.type, ILADUB.CandidateConcept)
               if str(s).startswith(str(page_doc)) and str(s).endswith("-datagrid-residue")]
    assert len(residue) == 1, residue

    booked = sum(r.tokens_escalated for r in p1.regions
                 if r.reason == "DATAGRID_RESIDUE")
    text = str(apple_doc.graph.value(residue[0], ILADUB.surfaceText))
    assert len(text.split()) == booked > 0, (len(text.split()), booked)
    # On THIS specimen the grid touched every escalated band, so the residue is the page's
    # whole escalation. A regression that let an untouched band's count reappear beside the
    # residue — the double count R73 exists to prevent — breaks this equality.
    assert booked == p1.escalated, (booked, p1.escalated)


@corpus_only
def test_no_superseded_band_keeps_its_escalation_candidate(apple_doc):
    """THE WITHDRAWAL, pinned. `_remove_escalation_record` is what stops the graph carrying a
    pass-1 escalation over ink the grid now asserts as tab:EntryCell; without this assertion
    the suite passes with the withdrawal loop deleted (measured)."""
    page_doc = _page_doc()
    bands = _superseded(apple_doc.pages[ADOPTED_PAGE])
    assert bands, "no band was superseded — the test below would be vacuous"
    for idx in bands:
        for cand in (URIRef(f"{page_doc}#region{idx}"),
                     URIRef(f"{page_doc}#htable{idx}-rt")):
            assert (cand, None, None) not in apple_doc.graph, cand
            assert (cand, RDF.type, ILADUB.CandidateConcept) not in apple_doc.graph, cand


@corpus_only
def test_the_effective_reading_of_a_superseded_band_is_not_the_escalated_one(apple_doc):
    """THE SUPERSESSION, pinned by the shipped query rather than by the triple we wrote.

    Measured before the lineage edge existed: effective-chain.rq returned the pass-1 chain,
    `verdict = escalated`, as the EFFECTIVE reading of a band the page had just adopted."""
    page_doc = _page_doc()
    bands = _superseded(apple_doc.pages[ADOPTED_PAGE])
    assert bands
    for idx in bands:
        region = URIRef(f"{page_doc}#region{idx}")
        rows = _run("effective-chain.rq", apple_doc.graph, region)
        assert rows, f"effective-chain returned NOTHING for superseded region {idx}"
        verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
        assert verdicts, f"no verdict in the effective chain for region {idx}: {rows}"
        assert str(verdicts[0].get("chosen", "")) != "escalated", verdicts[0]
        # ...and the superseded chain says so on every row, so a consumer reading the OLD
        # question still learns it was replaced.
        why = _run("why-escalated.rq", apple_doc.graph, region)
        assert why and all("supersededBy" in r for r in why), why


@corpus_only
def test_an_unsuperseded_band_on_the_adopted_page_is_untouched(apple_doc):
    """The control. Without it a change that superseded EVERY region would pass the two
    tests above for the wrong reason."""
    page_doc = _page_doc()
    p1 = apple_doc.pages[ADOPTED_PAGE]
    others = [i for i, r in enumerate(p1.regions) if r.verdict == "ignored"]
    assert others, "no unsuperseded band to use as a control"
    idx = others[0]
    region = URIRef(f"{page_doc}#region{idx}")
    eff = [(int(r["order"]), str(r["judgement"])) for r in
           _run("effective-chain.rq", apple_doc.graph, region)]
    why = [(int(r["order"]), str(r["judgement"])) for r in
           _run("why-escalated.rq", apple_doc.graph, region)]
    assert eff and eff == why, f"diverged on an unsuperseded region:\n eff={eff}\n why={why}"
    assert all("supersededBy" not in r
               for r in _run("why-escalated.rq", apple_doc.graph, region))
