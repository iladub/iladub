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

It does have a synthetic one, and it is better than what it replaces: it adopts page 0 at
document scope (`adopted=(0,)`, one superseded band, a grid region asserting 16 tokens, a
2-token `DATAGRID_RESIDUE`, and the admission holon). The withdrawal, the supersession, the
attribution, the ledger agreement and the zeroing-tautology refusal are therefore re-pointed at
it, NOT deleted and NOT weakened — and they now run **in CI**, which the apple versions never
could. Each carries its falsification evidence in its own docstring.

[[R175]] CLOSED 2026-09-06. The fixture above was `currency_marker_escalating_pdf`, which has
exactly ONE band — so the control that keeps the two supersession pins non-vacuous had no
unsuperseded region to stand on and stayed behind on apple, corpus-gated, while the five pins it
controls ran in CI without it. `currency_marker_escalating_with_note_pdf` draws a second,
one-line band that classifies NON_TABLE and therefore CANNOT be superseded
(`compile.py:1276` supersedes only a report with `tokens_escalated > 0`), so the control now sits
on the same document, in the same run, in CI — at identical page arithmetic, which is why no pin
above was re-baselined to get it.

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

    One page, TWO bands. The first escalates REGION_TILING_FAILED — so the candidate gate
    opens, the re-compile's own gate (`compile.py:1224`, `asserted_total == 0 and
    escalated_total > 0`) opens with it, the grid reads the page and supersedes that band. The
    second is a one-line note that classifies NON_TABLE and books no tokens, so the grid cannot
    supersede it (`compile.py:1276` needs `tokens_escalated > 0`) and it survives as the
    CONTROL — see `test_an_unsuperseded_band_on_the_adopting_page_is_untouched`.

    CHANGED 2026-09-06 ([[R175]]) from `currency_marker_escalating_pdf`, whose single band left
    every pin below with no control on the same document. The page arithmetic is IDENTICAL —
    that is why this shape was chosen over a two-line note, which books 23 escalated tokens and
    would have re-baselined the residue equality below. Measured at document scope:
    `adopted=(0,)`, `score=0.8888888888888888`, page0 `asserted=16 escalated=2`, regions
    `[superseded, ignored(NON_TABLE), asserted(grid, 16 tokens), escalated(DATAGRID_RESIDUE, 2
    tokens)]`."""
    from tests.etkl.fixtures import currency_marker_escalating_with_note_pdf
    from iladub.etkl.document import compile_document
    p = tmp_path_factory.mktemp("adoption") / "adopting.pdf"
    currency_marker_escalating_with_note_pdf(str(p))
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


def test_an_unsuperseded_band_on_the_adopting_page_is_untouched(adopting_doc):
    """THE CONTROL, and it now runs in CI ([[R175]], closing it).

    Without it, a change that superseded EVERY region would pass
    `test_no_superseded_band_keeps_its_escalation_candidate` and
    `test_the_effective_reading_of_a_superseded_band_is_not_the_escalated_one` for the wrong
    reason: both iterate `_superseded(...)` and assert something about each member, so a graph
    in which nothing escaped supersession satisfies them vacuously. This pins that something
    did — and that the two shipped queries agree about it.

    It lived on apple until 2026-09-06 because the one-band fixture had no unsuperseded region
    to control with; the fixture now draws one, so the control and the five pins it controls sit
    on the same document, in the same run, in CI. What it asserts is unchanged in force.

    FALSIFICATION (2026-09-06, and it is the second half of [[R175]]'s criterion): widen
    `document.py:1737`'s supersession loop — the `dec:supersedes` one, NOT the
    `_remove_escalation_record` withdrawal loop at `:1682`, which is textually identical — from
    `for idx in superseded` to `for idx in range(grid_idx)` — the over-application this control exists to catch — and BOTH assertions
    below break, measured separately because the test can only report the first:

        eff = [(0, 'verdict')]                                       # the admission itself
        why = [(0, 'multi_table'), (1, 'kind'), (2, 'verdict')]      # the band's own chain
        rows carrying supersededBy: 3 of 3

    so `effective-chain.rq` now answers *the grid's admission* as the effective reading of a
    band the grid never touched. `eff == why` is what trips first; the `supersededBy` assertion
    is the same defect seen from the other query and is kept because it names it. Restored, the
    test passes.

    The OPPOSITE stub — deleting the `graph.add((admission, DEC.supersedes, v1))` edge entirely
    — does not fail here, and should not:
    `test_the_effective_reading_of_a_superseded_band_is_not_the_escalated_one` is what catches
    that direction. This control is one-sided by design."""
    page_doc = _page_doc(SYNTH_ADOPTED_PAGE)
    p = adopting_doc.pages[SYNTH_ADOPTED_PAGE]
    others = [i for i, r in enumerate(p.regions) if r.verdict == "ignored"]
    assert others, "no unsuperseded band to use as a control"
    # ...and the thing it controls really is non-empty, or the pins above are vacuous and this
    # test would not have noticed. Asserted here rather than left to the reader: the control and
    # the controlled must both be non-empty for either to mean anything.
    assert _superseded(p), "nothing was superseded — the supersession pins are vacuous"
    idx = others[0]
    region = URIRef(f"{page_doc}#region{idx}")
    eff = [(int(r["order"]), str(r["judgement"])) for r in
           _run("effective-chain.rq", adopting_doc.graph, region)]
    why = [(int(r["order"]), str(r["judgement"])) for r in
           _run("why-escalated.rq", adopting_doc.graph, region)]
    assert eff, f"effective-chain returned NOTHING for the unsuperseded region {idx}"
    assert eff == why, f"diverged on an unsuperseded region:\n eff={eff}\n why={why}"
    assert all("supersededBy" not in r
               for r in _run("why-escalated.rq", adopting_doc.graph, region))


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
    re-pointed driver pins above are then owed a corpus fixture.

    RE-BASELINED AGAIN 2026-09-07, `56 -> 98`, by [[R176]] — and the RULING is that this is an
    operand re-baseline, not a reading change. The page's SCORE is unchanged at 1.0, the band
    population is unchanged, and the cells it reads are unchanged; what moved is that the band's
    42 label words are now booked instead of dropped (`_book_recovered_ink`, compile.py:1051).
    98 IS the band's whole ink — measured, `scripts/unbooked_ink_census.py` — so this assertion
    is now strictly stronger than the one it replaces: it says the page read EVERYTHING it holds,
    where `56` only said it read every data cell and said nothing about the other 42 words."""
    assert apple_doc.adopted == (), apple_doc.adopted
    p1 = apple_doc.pages[ADOPTED_PAGE]
    assert (p1.asserted, p1.escalated) == (98, 0), (p1.asserted, p1.escalated)


# `test_an_adopted_page_never_scores_one_by_construction` STOOD HERE and was DELETED 2026-09-07,
# with the ruling that deletes it, per the fork [[R173]] 5a and this test's own docstring set for
# [[R172]]: *rule on apple p1's reading, then either delete this test with that ruling recorded,
# or repair the reading it caught.*
#
# THE RULING: apple p1's reading is CORRECT, and its `p1.escalated > 0` is REFUTED rather than
# stale. The cell-level diff (`scripts/entry_cell_diff.py`, evidence in
# docs/superpowers/2026-09-07-r172-the-cell-level-diff.md § 2) shows the merged reading of p1
# LOSES no baseline cell, CHANGES none, and GAINS 42 — every gain landing on a real baseline word
# with identical text, every one out of a band that escalated before, and none out of the three
# `ignored` prose bands. Nothing on that page is left unread, so `escalated == 0` is honest and an
# assertion demanding otherwise is asserting something false about the document.
#
# WHAT IT WAS RIGHT ABOUT IS RE-HOMED, NOT DROPPED. Its concern — a page reaching 1.0 without
# adopting — is real, and the diff located it at a different site: the score's DENOMINATOR moves
# when a verdict changes (24 words on p0, 28 on p1 leave `asserted+escalated` altogether, because
# an escalated band booked every word it holds while an asserted matrix band booked only its data
# cells' words). That is [[R176]] — CLOSED 2026-09-07: `_book_recovered_ink` books the rest, the
# corpus-wide unbooked ink of asserted bands went 262 words -> 0, and p1's operands read
# `(98, 0)` above rather than `(56, 0)`. (The two `compile.py:NNN` citations that stood here were
# deleted rather than re-pointed: the repair moved every line they named, and the sites are found
# by symbol — `_book_recovered_ink`'s four call sites — far more reliably than by number.) The invariant
# this test used to carry is pinned on the fixture that adopts, by
# `test_the_adopted_page_keeps_the_ink_the_grid_did_not_read` above, and the diff's own findings
# are pinned by `test_band_runs.py::test_the_merge_loses_no_cell_and_invents_no_ink`.
#
# DO NOT RESTORE IT. A page whose ink is entirely read must be allowed to say so.


@corpus_only
def test_the_document_score_rises(apple_doc):
    """Measured 2026-08-09: 0.06068601583113457 before this loop, 0.35560344827586204 after.

    BOTH are pinned (final review m1). `> 0.0606…` alone lets the headline measurement regress
    all the way back to 0.07 and stay green; the second assertion is the floor, recorded in
    docs/superpowers/residues.md and docs/wiki/concepts/data-grid.md. Never lower it: a drop
    is a measurement to report, not a number to edit.

    2026-09-05: reads 0.6288659793814433 — clearing the floor by the [[R165]] one-band reading,
    NOT by adoption (which no longer fires here at all). The floor is deliberately left where it
    was: it is a floor, not a pin.

    2026-09-07: reads 0.71875 = 276/384, by [[R176]]. **This rise is NOT a better reading and
    must not be reported as one** — it is 90 label words (48 on p0, 42 on p1) moving from
    counted-nowhere into `asserted`, plus 3 into the p2 numerator. The document read exactly
    what it read the day before. Recorded here because a headline number that moves for an
    accounting reason is the one most likely to be misread later as progress."""
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
def test_the_two_queries_agree_on_an_untouched_band_of_a_real_document(apple_doc):
    """The same query-agreement invariant, on a REAL document rather than a drawn one.

    NOT the control any more, and the previous name (`…_on_apples_page_one_is_untouched`) said
    it was. [[R175]], 2026-09-06: apple adopts NOTHING since `4cfee38`, so apple p1 has no
    superseded region for this to be the control OF — it was controlling tests that run on a
    different document. The control moved to the fixture that adopts, where it can be
    non-vacuous and where it runs in CI; this is kept, not deleted, because the assertion is
    still true and still worth making against 28 rows of a real statement rather than against a
    caption we drew ourselves.

    Read a red line here as *the shipped queries disagree on a band nothing touched*, never as
    *supersession over-applied* — that is now the fixture-side control's finding to report."""
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
