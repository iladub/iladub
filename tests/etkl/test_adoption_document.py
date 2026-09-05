"""Adoption at DOCUMENT scope (spec 2026-08-09, residue R73).

The decidability claim: a page's total reading failure is only final after carriage, section
repair and stitching have had their turn. The pass therefore runs LAST.

RE-BASELINED 2026-09-05 ([[R173]] 5a; `docs/superpowers/2026-09-04-r173-bisect.md` § 3).
Every pin in this module was written against apple page 1 — 0 asserted, 97 escalated, adopted.
Since `4cfee38` ([[R160]]) apple adopts NOTHING, and since the one-band merge ([[R165]]) page 1
asserts its whole statement outright (`asserted=56, escalated=0`), so six tests here were
failing on any machine with a corpus while CI, which cannot see the corpus at all, stayed green.

MEASURED before re-pointing anything, because "no fixture adopts" is the load-bearing claim:
`compile_document` was run over all SEVEN tracked corpus documents on 2026-09-05 and every one
reports `adopted=()`. Two pages still reach the candidate gate — bfs `p0` (0 asserted, 6
escalated) and `p4` (0/36) — and both refuse at the re-compile with *"adoption refused — no data
grid region"*. So the document-scope adoption BRANCH has no live corpus fixture at all.

It does have a synthetic one, and it is better than what it replaces: `currency_marker_escalating_pdf`
adopts page 0 at document scope (`adopted=(0,)`, one superseded band, a grid region asserting 16
tokens, a 2-token `DATAGRID_RESIDUE`, and the admission holon) — already relied on by
`tests/etkl/test_escalation_wiring.py::test_the_adopting_path_furnishes_nothing`. The withdrawal,
the supersession, the attribution, the ledger agreement and the zeroing-tautology refusal are
therefore re-pointed at it, NOT deleted and NOT weakened — and they now run **in CI**, which the
apple versions never could. Each carries its falsification evidence in its own docstring.

What stays on apple is what is still true of apple: that it adopts nothing, why, and the ledger
and query pins that never needed adoption.
"""
import pytest
from pathlib import Path

from rdflib import Literal, Namespace, RDF, URIRef

REPO = Path(__file__).resolve().parents[2]
APPLE = REPO / "corpus" / "financial" / "apple-fy2026q3-statements.pdf"
QDIR = REPO / "vocab" / "queries"
ILADUB = Namespace("https://w3id.org/iladub#")

#: The page apple used to adopt, and the page the synthetic fixture does adopt. Kept as one
#: name because every pin below indexes a single adopting page; the two documents differ in
#: WHICH page that is, so each fixture states its own.
ADOPTED_PAGE = 1
SYNTH_ADOPTED_PAGE = 0


def corpus_only(fn):
    """Tag AND gate. The tag was a module-level `pytestmark` until 2026-09-05; the synthetic
    tests below must not carry it, or `-m corpus` would report them as corpus coverage this
    module no longer has ([[R173]])."""
    fn = pytest.mark.skipif(not APPLE.is_file(), reason="corpus not populated")(fn)
    return pytest.mark.corpus(fn)


@pytest.fixture(scope="module")
def apple_doc():
    from iladub.etkl.document import compile_document
    return compile_document(str(APPLE))


@pytest.fixture(scope="module")
def adopting_doc(tmp_path_factory):
    """THE DOCUMENT-SCOPE ADOPTION FIXTURE, synthetic and therefore CI-visible.

    One page, one band, and that band escalates REGION_TILING_FAILED — so the candidate gate
    opens, the re-compile's own gate (`compile.py:1224`, `asserted_total == 0 and
    escalated_total > 0`) opens with it, the grid reads the page and supersedes the band.
    Measured 2026-09-05: `adopted=(0,)`, `score=0.888…`, regions
    `[superseded, asserted(grid, 16 tokens), escalated(DATAGRID_RESIDUE, 2 tokens)]`."""
    from tests.etkl.fixtures import currency_marker_escalating_pdf
    from iladub.etkl.document import compile_document
    p = tmp_path_factory.mktemp("adoption") / "adopting.pdf"
    currency_marker_escalating_pdf(str(p))
    return compile_document(str(p))


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


# ======================================================= the adoption driver, on the fixture
# that adopts. Re-pointed from apple 2026-09-05; the assertions are unchanged in force.


def test_the_document_adopts_the_page_the_pipeline_could_not_read(adopting_doc):
    """The page whose only band escalates is read by the grid and adopted.

    Was apple p1 (`0 asserted, 97 escalated`, and the grid read its 28 entry rows) until
    `4cfee38`; apple now asserts that page outright and adopts nothing (see the module
    docstring, and `test_apple_adopts_nothing_because_the_page_asserts_outright` below)."""
    assert SYNTH_ADOPTED_PAGE in adopting_doc.adopted, adopting_doc.adopted
    p = adopting_doc.pages[SYNTH_ADOPTED_PAGE]
    assert p.asserted > 0
    print(f"\nadopting document: score={adopting_doc.score!r} "
          f"p{SYNTH_ADOPTED_PAGE}={p.asserted}/{p.escalated} score={p.score:.4f}")


def test_the_adopted_page_keeps_the_ink_the_grid_did_not_read(adopting_doc):
    """THE ZEROING TAUTOLOGY, REFUSED: ink the grid did not read keeps escalating.

    This is the invariant `test_an_adopted_page_never_scores_one_by_construction` carried until
    2026-09-05, re-pointed to the page that actually adopts. That test keeps its name and its
    apple fixture because it has become something else — [[R172]]'s detector; see below."""
    p = adopting_doc.pages[SYNTH_ADOPTED_PAGE]
    assert p.escalated > 0
    assert p.score < 1.0


def test_the_adopted_pages_own_ledger_adds_up(adopting_doc):
    """The report's totals ARE the sum of its per-band token counts — no band's ink is
    counted twice and none goes missing between the ledger and the score."""
    p = adopting_doc.pages[SYNTH_ADOPTED_PAGE]
    assert sum(r.tokens_asserted for r in p.regions) == p.asserted
    assert sum(r.tokens_escalated for r in p.regions) == p.escalated
    assert p.score == p.asserted / (p.asserted + p.escalated)


def test_the_ledger_and_the_graph_agree_on_the_adopted_page(adopting_doc):
    """Every escalated token on an adopted page has something in the graph escalating it,
    and it is the SAME count the report books.

    Scoped to this page's own adoption doc URI: a global scan would pass on a second adopting
    page's residue and would never notice this one had vanished."""
    page_doc = _page_doc(SYNTH_ADOPTED_PAGE)
    p = adopting_doc.pages[SYNTH_ADOPTED_PAGE]

    residue = [s for s in adopting_doc.graph.subjects(RDF.type, ILADUB.CandidateConcept)
               if str(s).startswith(str(page_doc)) and str(s).endswith("-datagrid-residue")]
    assert len(residue) == 1, residue

    booked = sum(r.tokens_escalated for r in p.regions
                 if r.reason == "DATAGRID_RESIDUE")
    text = str(adopting_doc.graph.value(residue[0], ILADUB.surfaceText))
    assert len(text.split()) == booked > 0, (len(text.split()), booked)
    # On THIS specimen the grid touched every escalated band, so the residue is the page's
    # whole escalation. A regression that let an untouched band's count reappear beside the
    # residue — the double count R73 exists to prevent — breaks this equality.
    assert booked == p.escalated, (booked, p.escalated)


def test_no_superseded_band_keeps_its_escalation_candidate(adopting_doc):
    """THE WITHDRAWAL, pinned. `_remove_escalation_record` is what stops the graph carrying a
    pass-1 escalation over ink the grid now asserts as tab:EntryCell; without this assertion
    the suite passes with the withdrawal loop deleted (measured, on apple, 2026-08-09).

    FALSIFIED AGAIN ON THIS FIXTURE 2026-09-05, because a re-pointed pin is a proposition until
    it is: with `_remove_escalation_record` stubbed to `return None`, this test fails on the
    surviving `…#region0` candidate; restored, it passes."""
    page_doc = _page_doc(SYNTH_ADOPTED_PAGE)
    bands = _superseded(adopting_doc.pages[SYNTH_ADOPTED_PAGE])
    assert bands, "no band was superseded — the test below would be vacuous"
    for idx in bands:
        for cand in (URIRef(f"{page_doc}#region{idx}"),
                     URIRef(f"{page_doc}#htable{idx}-rt")):
            assert (cand, None, None) not in adopting_doc.graph, cand
            assert (cand, RDF.type, ILADUB.CandidateConcept) not in adopting_doc.graph, cand


def test_the_effective_reading_of_a_superseded_band_is_not_the_escalated_one(adopting_doc):
    """THE SUPERSESSION, pinned by the shipped query rather than by the triple we wrote.

    Measured before the lineage edge existed: effective-chain.rq returned the pass-1 chain,
    `verdict = escalated`, as the EFFECTIVE reading of a band the page had just adopted.

    FALSIFIED ON THIS FIXTURE 2026-09-05: with `document.py:1740`'s
    `graph.add((admission, DEC.supersedes, v1))` stubbed to `pass`, effective-chain.rq answers
    `chosen = "escalated"` for the superseded region and this test fails on that exact row —
    the original defect, reproduced; restored, it passes."""
    page_doc = _page_doc(SYNTH_ADOPTED_PAGE)
    bands = _superseded(adopting_doc.pages[SYNTH_ADOPTED_PAGE])
    assert bands
    for idx in bands:
        region = URIRef(f"{page_doc}#region{idx}")
        rows = _run("effective-chain.rq", adopting_doc.graph, region)
        assert rows, f"effective-chain returned NOTHING for superseded region {idx}"
        verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
        assert verdicts, f"no verdict in the effective chain for region {idx}: {rows}"
        assert str(verdicts[0].get("chosen", "")) != "escalated", verdicts[0]
        # ...and the superseded chain says so on every row, so a consumer reading the OLD
        # question still learns it was replaced.
        why = _run("why-escalated.rq", adopting_doc.graph, region)
        assert why and all("supersededBy" in r for r in why), why


def test_the_admission_verdict_names_its_agent(adopting_doc):
    """THE ATTRIBUTION, pinned (final review I1).

    The driver dresses the grid's admission holon as the effective VERDICT of every band it
    superseded. `vocab/shapes/dec-shapes.ttl:21` requires `dec:decidedBy` minCount 1 of any
    `dec:DecisionHolon` and CLAUDE.md §4 requires agent attribution for a membrane-crossing, so
    a judgement facade without an agent is a decision nobody made.

    It must also RESOLVE: the agent named is the reading compiler that decided the superseded
    verdicts themselves, and the node is required to be typed and labelled in the same graph —
    a bare IRI pointing at nothing attributes nothing.

    FALSIFIED ON THIS FIXTURE 2026-09-05, and the result is worth stating exactly rather than
    as a green tick: with `datagrid.py:706` (`g.add((dec_uri, DEC.decidedBy, _READER_AGENT))`)
    stubbed, this test does not fail its assertion — it ERRORS in the fixture, because an
    adoption sets `section_facts` and the document membrane refuses first on
    `dec:decidedBy` minCount (`MembraneRefusal` at `document.py:1331`). The emitter is pinned;
    the membrane is simply the first line of the two, and a reader should not infer from a red
    line here that the assertion below is what caught it."""
    from rdflib import Namespace, RDFS
    from iladub.etkl.decisionlog import _READER_AGENT
    DEC = Namespace("https://w3id.org/iladub/dec#")
    PROV = Namespace("http://www.w3.org/ns/prov#")
    g = adopting_doc.graph
    page_doc = _page_doc(SYNTH_ADOPTED_PAGE)

    admissions = [d for d in g.subjects(DEC.regarding, None)
                  if str(d).startswith(str(page_doc)) and str(d).endswith("-datagrid-admission")]
    assert len(admissions) == 1, admissions
    admission = admissions[0]
    assert (admission, RDFS.label, Literal("verdict")) in g

    agents = list(g.objects(admission, DEC.decidedBy))
    assert agents == [_READER_AGENT], agents
    # not a dangling reference: the node is real in THIS graph
    assert (_READER_AGENT, RDF.type, PROV.SoftwareAgent) in g
    assert list(g.objects(_READER_AGENT, RDFS.label)), "the agent carries no label"
    # ...and it is the SAME agent that decided every verdict this admission supersedes
    for v1 in g.objects(admission, DEC.supersedes):
        assert list(g.objects(v1, DEC.decidedBy)) == [_READER_AGENT], v1


# =========================================================================== apple, as it IS


@corpus_only
def test_apple_adopts_nothing_because_the_page_asserts_outright(apple_doc):
    """RE-BASELINED 2026-09-05, from `test_the_document_adopts_the_page_the_pipeline_could_not_read`
    and `test_pages_that_read_something_are_not_adopted` (which had become vacuous — it asserted
    `0 not in adopted and 2 not in adopted` of an empty tuple).

    WHAT THE NEW NUMBER MEANS. Page 1 is not adopted because it no longer needs adopting, not
    because adoption broke: [[R160]] measured the candidate gate closing at `4cfee38` the moment
    p1's header band asserted one `tab:EntryCell`, and [[R165]]'s one-band reading then took the
    page to `asserted=56, escalated=0`. Adoption is not defeated here, it is UNNECESSARY —
    which is [[R160]]'s open reader-authority question, not this test's to settle.

    It is still a detector: if any apple page is ever adopted again, this fails loudly, and the
    re-pointed driver pins above are then owed a corpus fixture."""
    assert apple_doc.adopted == (), apple_doc.adopted
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert (p1.asserted, p1.escalated) == (56, 0), (p1.asserted, p1.escalated)


@corpus_only
def test_an_adopted_page_never_scores_one_by_construction(apple_doc):
    """The zeroing tautology, refused: ink the grid did not read keeps escalating.

    **THIS TEST FAILS AT HEAD, BY DESIGN, AND MUST NOT BE RE-BASELINED** ([[R173]] 5a, and the
    bisect's own § 5). It is the ONE of the eight that the [[R165]] merge broke rather than
    R160's `adopted (1,) → ()`: apple p1 now reads `score=1.0, asserted=56, escalated=0`, so
    `p1.escalated > 0` fails `0 > 0` — a page that reached 1.0 WITHOUT adopting anything.

    That is exactly the state this assertion exists to refuse, so it is firing as [[R172]]'s
    detector: nobody has content-diffed the merged band's 124 entries against the 48 cells
    asserted before, and if 56 asserted cells is the wrong reading of apple p1, this found it.
    The invariant it used to carry is now pinned on the fixture that adopts, by
    `test_the_adopted_page_keeps_the_ink_the_grid_did_not_read`.

    Closing it is [[R172]]'s work: rule on apple p1's reading, then either delete this test with
    that ruling recorded, or repair the reading it caught."""
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert p1.escalated > 0
    assert p1.score < 1.0


@corpus_only
def test_the_document_score_rises(apple_doc):
    """Measured before this loop: 0.06068601583113457, and 0.35560344827586204 after.

    BOTH are pinned (final review m1). `> 0.0606…` alone lets the headline measurement regress
    all the way back to 0.07 and stay green; the second assertion is the floor, recorded in
    docs/superpowers/residues.md and docs/wiki/concepts/data-grid.md. Never lower it: a drop
    is a measurement to report, not a number to edit.

    2026-09-05: reads 0.6288659793814433 — clearing the floor by the [[R165]] one-band reading,
    NOT by adoption (which no longer fires here at all). The floor is deliberately left where it
    was: it is a floor, not a pin."""
    assert apple_doc.score > 0.06068601583113457
    assert apple_doc.score >= 0.35560344827586204, apple_doc.score


@corpus_only
def test_apples_page_one_ledger_adds_up(apple_doc):
    """The ledger arithmetic, on a page that is no longer adopted — it never needed adoption to
    be true. Renamed 2026-09-05 from `test_the_adopted_pages_own_ledger_adds_up`, which now
    names the fixture-side test above; assertions unchanged."""
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert sum(r.tokens_asserted for r in p1.regions) == p1.asserted
    assert sum(r.tokens_escalated for r in p1.regions) == p1.escalated
    assert p1.score == p1.asserted / (p1.asserted + p1.escalated)


@corpus_only
def test_an_unsuperseded_band_on_apples_page_one_is_untouched(apple_doc):
    """The control. Without it a change that superseded EVERY region would pass the two
    supersession tests above for the wrong reason.

    Renamed 2026-09-05 from `…_on_the_adopted_page_is_untouched`: apple p1 is not adopted any
    more, and the fixture that is has no `ignored` region to control with (its three regions
    are superseded / asserted-grid / residue). So the control stays on apple, where an
    unsuperseded band still exists — it pins that the two shipped queries agree on a band
    nothing superseded, which needs no adoption to mean something."""
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
