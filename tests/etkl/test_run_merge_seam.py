"""R165 — the seam. page_bands proposes a run; the tiling membrane disposes.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md § 3.0, § 3.2
Plan: docs/superpowers/plans/2026-09-04-the-run-is-one-band.md
"""
import os

import pytest

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
APPLE = os.path.join(CORPUS, "financial", "apple-fy2026q3-statements.pdf")
STEM = os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf")
CAPACITY = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not fetched")


@corpus_only
def test_apple_p0_reads_as_one_band_and_the_merge_is_what_did_it():
    """The headline. apple p0's eight bands become three; the merged band occupies
    index 2, mints #mtable2 — the IRI band 2 already mints today — and asserts 124
    entries where 48 cells are asserted at baseline. Page score 1.0.
    (spike § 2-3, § 8.4; reproduced from INSIDE page_bands in the pre-plan spike § 0.)"""
    from iladub.etkl.compile import compile_tables, page_bands

    assert len(page_bands(APPLE, 0)) == 3
    rep = compile_tables(APPLE, 0, validate_shapes=False)
    assert [r.verdict for r in rep.regions] == ["ignored", "ignored", "asserted"]
    assert rep.regions[2].cells == 124
    assert rep.regions[2].table_uri.endswith("#mtable2")
    assert rep.score == 1.0


@corpus_only
def test_apple_p1_reads_as_one_band():
    from iladub.etkl.compile import compile_tables, page_bands

    assert len(page_bands(APPLE, 1)) == 3
    rep = compile_tables(APPLE, 1, validate_shapes=False)
    assert rep.regions[2].cells == 56
    assert rep.score == 1.0


@corpus_only
def test_o2_the_fallback_is_what_saves_the_ink():
    """O2. Four documents propose a run the membrane REFUSES, and every one of them
    still asserts exactly what it asserts today. This is the test that pins § 2's D2
    and § 3.2 — and the reason the change is safe on 5 of the 7 documents.

    FALSIFIER (Step 5): make merged_run_admissible return True unconditionally. All
    four fail. graincorp-stem alone loses 586 asserted cells.

    RE-BASELINED 2026-09-12 by grid donation (R201/R203): bfs p6 moved 222 -> 267, and the
    other three figures did NOT move. The move is not this test's subject changing — no run
    is accepted on bfs p6 before or after, and the run membrane still refuses there. It is
    that p6's five continuation bands now read their column labels from band 2's wholly-drawn
    header, so 45 cells that were being consumed as a false header row are asserted as data.
    WHAT THE NEW NUMBER MEANS: a page whose proposed run the membrane refuses still asserts
    everything it asserts today, grid donation included — which is the same claim this line
    always made, measured against a page that now reads more of its own ink.

    RE-BASELINED AGAIN 2026-09-13 by SPAN donation ([[R211]]): graincorp-capacity p0 moved
    390 -> 406, and the other three figures did NOT move. It is the SAME mechanism as bfs p6's
    move one paragraph up, on the other donation arm: band 3 now reads its column labels from
    band 2's wholly-drawn spanning header, so its own line 0 stops being consumed as a header
    row and becomes a data row. +16 is exactly the page's leaf-column count, and that identity
    is the check — a move that is not `ncols` would be a different event wearing this one's
    number.

    THESE ARE ENTRY CELLS, NOT TOKENS, and it was measured rather than assumed: the span
    reading emits 406 `tab:EntryCell` nodes against the record reading's 390, and on this page
    every entry cell holds exactly one word (0 multi-word cells), so `assert_hier_region`'s
    token return and the cell count coincide. THE INK LEDGER DOES NOT MOVE AT ALL — `rep.
    asserted` is 406 before and after, because R176's `_book_recovered_ink` already booked
    those 16 label words on the record path. Cells +16, ink +0: that is the whole claim of this
    loop, and `test_o3` above is the pin on the ink half."""
    from iladub.etkl.compile import compile_tables

    def cells(pdf, page):
        return sum(r.cells for r in compile_tables(pdf, page, validate_shapes=False).regions)

    assert cells(STEM, 0) == 586
    assert cells(CAPACITY, 0) == 406
    # 267 -> 285 on 2026-09-18: bfs p6's two LONE rows (`Total`, `Zurich`) are now read by
    # `donation.offer_single_line`, 9 entries each. Same page, a different reading gained; the
    # run-merge fallback this test is about is untouched.
    # 285 -> 294 on 2026-09-19: `Tessin`, cut free of its notes (trailing.cut_trailing_notes).
    assert cells(BFS, 6) == 294
    assert cells(APPLE, 2) == 3


@corpus_only
def test_a_refused_run_leaves_the_page_byte_identical():
    """§ 3.2: 'a refusal must cost nothing observable: no triple, no decision-log node,
    no report.' Serialise the whole graph of a page whose run is refused and compare it
    against the same page with the proposal suppressed. Identical.

    SUBSTITUTED TWICE from the plan's verbatim form, both times after MEASURING what
    the assertion actually does (CLAUDE.md § Plan authoring discipline, rules 4-5):

    1. The plan asserted `a.splitlines().sort() == b.splitlines().sort()`.
       `list.sort()` returns None, so that reads `None == None` and passes with the
       whole seam deleted — it pins nothing (defect 5, verbatim).
    2. `sorted(...)` DOES compare the graphs, and fails: stem p0 carries 3516
       tab:hasBBox blank-node triples whose labels are minted fresh per Graph. The two
       graphs are the same size (8660 lines) with the same verdicts and the same
       score; only the bnode labels differ. "Byte-identical" is therefore not
       expressible over N-Triples lines at all here.

    `rdflib.compare.isomorphic` is the honest form of the same claim — graph identity
    up to blank-node labelling, which is what an unlabelled bbox node means — and it
    is STRICTLY STRONGER than the sorted-lines comparison, not weaker: it matches the
    bnodes structurally rather than ignoring them. Measured at 3.8s on this page.

    NOTE, and it is a real qualification the spike measured: this holds IN THE GRAPH and
    NOT ON THE CLOCK. graincorp-stem p0's refused run costs 3.06s at is_matrix_candidate
    alone (spike § Q-A A3) — see Task 7's budget."""
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import compile_tables

    with_proposal = compile_tables(STEM, 0, validate_shapes=False)
    real = compile_mod.merged_run_admissible
    try:
        compile_mod.merged_run_admissible = lambda merged, first, last, page_number: False
        suppressed = compile_tables(STEM, 0, validate_shapes=False)
    finally:
        compile_mod.merged_run_admissible = real
    from rdflib.compare import isomorphic

    assert len(with_proposal.graph) == len(suppressed.graph)
    assert isomorphic(with_proposal.graph, suppressed.graph)
    assert [r.verdict for r in with_proposal.regions] == [r.verdict for r in suppressed.regions]
    assert with_proposal.score == suppressed.score


@corpus_only
def test_m1_the_partition_does_not_depend_on_section_repair_bands():
    """INVARIANT M1 (§ 3.1). The partition is a pure function of the unrepaired build.

    THE HONEST LIMIT OF THIS TEST, which must be stated and not implied away: the only
    corpus page with a non-empty section_repair_bands is cbh p0, and cbh p0 has NO
    candidate run (spike § Q-A A4, § 'What this changes' item 7). So this pins that the
    band COUNT is stable across repair sets; it does NOT exercise 'the disposal verdict
    differs between a repaired and an unrepaired build', because no corpus page can.
    M1 is upheld by construction, not by evidence. That gap is R171."""
    from iladub.etkl.compile import page_bands

    assert len(page_bands(CBH, 0, None)) == len(
        page_bands(CBH, 0, frozenset({1, 3, 5, 7})))
    for pdf, page in [(APPLE, 0), (APPLE, 1), (STEM, 0)]:
        assert len(page_bands(pdf, page, None)) == len(
            page_bands(pdf, page, frozenset({0, 1, 2})))


# --- Task 6: O3, O4, O5 ---------------------------------------------------------------

# The pre-merge baseline, per (document, page). MEASURED 2026-09-04 on the CLEAN tree
# (not on the prototype) by scripts/page_ink_census.py — all 27 pages of all 7 documents,
# validate_shapes=False, datagrid_fallback=False, 27 compiled, 0 raised.
# RE-VERIFIED 2026-09-04 against the SHIPPED tree: 27 pages, and exactly the two apple
# entries marked below moved. RE-RUN IT rather than trusting this table if main has moved:
#     PYTHONPATH=src python3 scripts/page_ink_census.py
#
# RE-MEASURED 2026-09-07 by [[R176]], because main DID move and this table's own header
# says to re-run rather than trust it. EVERY entry changed that had label ink to book: an
# asserted band now books all of its ink, not only its data cells. **This is an accounting
# re-baseline, not a reading change** — the corpus census reports the identical band
# population before and after (asserted 24 / escalated 21 / ignored 146), and this test's
# force is untouched: 25 of 27 pages must still be EQUAL, and only apple p0/p1 may rise.
#
# THE TWO APPLE ENTRIES ARE MEASURED DIFFERENTLY FROM THE OTHER 25, and must stay that way.
# They are the PRE-MERGE reading — `compile_tables` with `compile.merged_run_admissible`
# forced to return False, the technique `scripts/entry_cell_diff.py:163-173` uses — because
# `>` against a post-merge number would be trivially false. Under R176 those baselines rise
# too (48 -> 72, 14 -> 27): the refusing reading books ITS label ink as well. Reproduce with:
#     PYTHONPATH=src python3 -c "from iladub.etkl import compile as C; \
#       C.merged_run_admissible = lambda *a, **k: False; \
#       print([C.compile_tables(APPLE, p, validate_shapes=False, \
#              datagrid_fallback=False).asserted for p in (0, 1)])"
BASELINE_ASSERTED = {
    ("cbh-stem-2026-08-03", 0): 54,
    ("graincorp-capacity-2026-08-04", 0): 406,
    ("graincorp-stem-2026-07-31", 0): 586,
    ("graincorp-stem-2026-07-31", 1): 0,
    ("graincorp-stem-2026-07-31", 2): 0,
    ("apple-fy2026q3-statements", 0): 72,    # PRE-MERGE (forced refusal); post-merge is 172
    ("apple-fy2026q3-statements", 1): 27,    # PRE-MERGE (forced refusal); post-merge is 98
    ("apple-fy2026q3-statements", 2): 6,
    ("bfs-population-bilan-2023", 0): 0,
    ("bfs-population-bilan-2023", 1): 0,
    ("bfs-population-bilan-2023", 2): 0,
    ("bfs-population-bilan-2023", 3): 0,
    ("bfs-population-bilan-2023", 4): 0,
    ("bfs-population-bilan-2023", 5): 16,
    ("bfs-population-bilan-2023", 6): 276,
    ("ons-index-of-services-2026-02", 0): 0,
    ("ons-index-of-services-2026-02", 1): 0,
    ("ons-index-of-services-2026-02", 2): 0,
    ("ons-index-of-services-2026-02", 3): 0,
    ("ons-index-of-services-2026-02", 4): 19,
    ("ons-index-of-services-2026-02", 5): 0,
    ("ons-index-of-services-2026-02", 6): 0,
    ("ons-index-of-services-2026-02", 7): 0,
    ("ons-index-of-services-2026-02", 8): 0,
    ("who-wfa-boys-zscore-0-5", 0): 301,
    ("who-wfa-boys-zscore-0-5", 1): 289,
    ("who-wfa-boys-zscore-0-5", 2): 148,
}

# The ONLY two pages a merge may move, and both may only move UP. Every other page must be
# EQUAL: `>=` alone would not catch a page that silently gained ink for the wrong reason.
MERGE_MOVES = {("apple-fy2026q3-statements", 0), ("apple-fy2026q3-statements", 1)}

# THE SECOND LEGITIMATE CAUSE OF A PAGE-SCOPE GAIN (R225 D1, 2026-09-14), kept as its own set
# rather than folded into MERGE_MOVES, because the two causes are different claims and this
# detector's whole value is telling them apart. D1 gives `_build_ruled_band` a resolution test, so
# a band whose only intersecting rules are the page BORDERS is no longer re-bucketed into one
# fused column — those bands now CLASSIFY, and a page that previously asserted nothing at page
# scope asserts real ink.
#
# WHY NOT JUST RELAX THE EQUALITY TO `>=`. That is the easy edit and it destroys the test: the
# equality clause is what catches a page silently gaining ink for the WRONG reason, which is the
# standing hazard this test exists for ([[R170]] — `is_matrix_candidate` is the sole guard on 976
# asserted cells it was never specified to guard). A detector that accepts every gain detects
# nothing.
#
# MEASURED 2026-09-14 on branch `r225-d1-resolution-test` (D1 applied, guard verified), by
# re-running O3's own 27-page table with `datagrid_fallback=False` exactly as the test does:
# 3 of 27 pages move, all UP, and the other 24 are byte-equal on this counter.
#
#     bfs-population-bilan-2023 p5      16 -> 180     border-only bands now classify
#     ons-index-of-services-2026-02 p7   0 -> 112     idem; the page also reports 216 escalated
#     ons-index-of-services-2026-02 p8   0 ->  12     idem
#
# NB apple p0/p1 are NOT here although a naive sweep reports them rising (72 -> 172, 27 -> 98).
# Their baselines are the PRE-MERGE readings (see the comment above BASELINE_ASSERTED: forced
# `merged_run_admissible = False`), so 172/98 are the post-merge numbers that comment already
# names, and MERGE_MOVES governs them. Adding them here would double-count one cause as two.
#
# A THIRD CAUSE, 2026-09-18, recorded in the same table because the detector's question is the
# same ("did this page's asserted ink move, and is the cause named?"): bfs p6 276 -> 312. The 36
# tokens are the `Total` and `Zurich` rows (20 + 16), one-line bands that were IGNORED and are now
# read under band 2's header by `donation.offer_single_line`. UP, like every other move here, and
# pinned pointwise in tests/etkl/test_grid_donation_seam.py.
#
# A FOURTH CAUSE, 2026-09-19: `trailing.cut_trailing_notes` cuts the notes set below a table's
# last row into a band of their own. bfs p6 312 -> 327 (`Tessin`, 15 tokens, read as a lone row)
# and bfs p5 180 -> 228 (the row blocks above T1's and T2's notes read without the notes' ink
# closing their gutters). Both UP.
D1_MOVES = {
    ("bfs-population-bilan-2023", 6): 327,
    ("bfs-population-bilan-2023", 5): 228,
    # 112 -> 105 on 2026-09-19, DOWN, and the 7 tokens were a MISREADING: the band [`2025 …` row,
    # a stray `"`] asserted ONE cell — the data row read as a header over the `"`. The cut gives
    # the `"` its own band; the row, alone, finds no donor on the band path and is ignored. The
    # document reading is untouched: p7 adopts, and the grid reads that row either way (315
    # asserted before and after).
    ("ons-index-of-services-2026-02", 7): 105,
    ("ons-index-of-services-2026-02", 8): 12,
}

# Every fragment compile.py mints, derived from its URIRef(f"{doc}#…") sites and
# decisionlog.py's band prefix — NOT guessed. Longest alternatives first so `rhtable`
# is not matched as `table`.
_FRAGMENT_RE = r"#(rhtable|mtable|ttable|htable|table|region)(\d+)"


def _pdf_for(stem):
    for family in ("ag-trade", "financial", "gov-stats", "health"):
        p = os.path.join(CORPUS, family, stem + ".pdf")
        if os.path.exists(p):
            return p
    raise AssertionError(f"no corpus PDF for {stem}")


@corpus_only
def test_o3_no_page_loses_asserted_ink_to_a_merge():
    """O3, and the STANDING DETECTOR for R170 (is_matrix_candidate is the sole guard on
    976 asserted cells it was never specified to guard).

    This is deliberately corpus-WIDE rather than a runtime guard. § 3.3 explains why a
    runtime guard is not implementable where the decision lives: page_bands decides the
    partition BEFORE anything is compiled, so it cannot know what the constituent bands
    would have asserted without compiling both readings. So the hazard is made
    FALSIFIABLE rather than guarded — and this generalises to any document later added
    to the corpus, which a guard tuned to today's evidence would not.

    MEASURED before this test was written, as the plan required: `sum(r.tokens_asserted
    for r in rep.regions) == rep.asserted` on all 27 pages, so the page-level counter is
    used. That is not an accident of arithmetic — compile.py writes tokens_* in ONE
    differencing pass over band_marks after every report is appended, so the invariant
    holds by construction. (This is the field of defect 2 in CLAUDE.md § Plan authoring
    discipline; the write site was measured, not assumed.)"""
    from iladub.etkl.compile import compile_tables

    for (stem, page), baseline in sorted(BASELINE_ASSERTED.items()):
        rep = compile_tables(_pdf_for(stem), page, validate_shapes=False,
                             datagrid_fallback=False)
        assert rep.asserted >= baseline, f"{stem} p{page}: {rep.asserted} < {baseline}"
        if (stem, page) in MERGE_MOVES:
            assert rep.asserted > baseline, \
                f"{stem} p{page}: the merge is supposed to move this page UP"
        elif (stem, page) in D1_MOVES:
            # R225 D1's three pages: pinned to their MEASURED figure, not merely allowed to
            # rise. A `>` here would let any later gain through on a page that already has a
            # licence to move, which is the hole the equality clause below exists to close.
            assert rep.asserted == D1_MOVES[(stem, page)], \
                f"{stem} p{page}: {rep.asserted} != {D1_MOVES[(stem, page)]} — this page's " \
                f"gain is D1's (border-only bands now classify) and is pinned to its measured " \
                f"value; a different number is a new cause, not this one"
        else:
            assert rep.asserted == baseline, \
                f"{stem} p{page}: {rep.asserted} != {baseline} — neither the merge (apple " \
                f"p0/p1) nor D1 (see D1_MOVES) touches this page, so a change here is a " \
                f"defect, not a gain"


@corpus_only
def test_o4_every_minted_fragment_index_names_its_report_position():
    """O4, SUBSTITUTED (spike § Q-B B2). The spec states O4 over `tab:bandIndex`, and that
    form is UNSATISFIABLE: tab:bandIndex never appears in the compile graph — it is emitted
    at exactly one site, into the transient section-recognition graph, which is discarded.
    This is a spec defect found by measuring the test's SETUP (plan rule 5), not a
    weakening: the satisfiable form carries the same force, that there is ONE index space.

    On apple p0/p1 page_bands returns 3 bands, the merged band occupies index 2 and mints
    #mtable2 — the IRI band 2 already minted today — and every minted fragment index is
    < len(regions) and names the report position it describes."""
    import re
    from iladub.etkl.compile import compile_tables

    for page in (0, 1):
        rep = compile_tables(APPLE, page, validate_shapes=False)
        assert len(rep.regions) == 3
        minted = {(m.group(1), int(m.group(2)))
                  for m in re.finditer(_FRAGMENT_RE, rep.graph.serialize(format="nt"))}
        assert minted, "no fragment was minted at all — the regex is wrong, not the code"
        for _kind, idx in minted:
            assert idx < len(rep.regions), (page, _kind, idx)
        assert ("mtable", 2) in minted


@corpus_only
def test_o5_a_forced_non_tail_merge_renumbers_consistently(monkeypatch):
    """O5. bfs p5 has 15 bands and produces runs (2,5) and (7,8) — both NON-TAIL, both
    refused today. Force (2,5) through by patching the ADMISSIBILITY PREDICATE, which is
    the disposal taken whole, not one of its four stages.

    Why not the spec's prescribed patch point: classify_matrix refuses this band
    INDEPENDENTLY of is_matrix_candidate, so patching those two cannot force an
    acceptance, and patching classify_matrix would mean fabricating a MatrixRegion —
    patching the geometry, which O5 forbids (spike § Q-B B1)."""
    import re
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import compile_tables, page_bands

    monkeypatch.setattr(
        compile_mod, "merged_run_admissible",
        lambda merged, first, last, page_number: (first, last) == (2, 6))

    # 15 bands / run (2,5) / 12 -> 17 bands / run (2,6) / 13 on 2026-09-19.
    # `trailing.cut_trailing_notes` gives the notes below T1 and below T2 a band each (15 -> 17),
    # and T1's notes band is RULED with a subset of the run's rule positions, so band-run.rq now
    # proposes 2..6 — five bands — where it proposed 2..5. Refused in production exactly as
    # (2,5) was; forced here. 17 - 4 = 13.
    bands = page_bands(BFS, 5)
    assert len(bands) == 13, "the run 2..6 — five bands — must become one"

    rep = compile_tables(BFS, 5, validate_shapes=False)
    assert len(rep.regions) == 13
    minted = {int(m.group(2)) for m in re.finditer(_FRAGMENT_RE,
                                                   rep.graph.serialize(format="nt"))}
    assert minted, "no fragment was minted at all — the regex is wrong, not the code"
    assert max(minted) < 13, "a fragment index >= the band count means two index spaces"


@corpus_only
def test_o5_document_scope_completes_with_a_forced_non_tail_merge(monkeypatch):
    """The second half of O5: a document-scope compile over bfs completes, and adoption's
    grid_idx equals the page's band count on the merged page.

    THE LIMIT IS RETIRED — R171's second case is now REAL (2026-09-14, R225 D2), and the
    paragraph this replaces is kept in substance because it dated the gap it closes. It read:
    "adoption's re-compile fires only on bfs p0 and p4 and is REFUSED on both, so ADOPTION'S
    BRANCH IS NEVER ENTERED on the merged page ... No corpus document both merges and adopts.
    That gap is R171." D2 widened the adoption gate from "the page asserted nothing" to "the
    page left ink unread", and bfs p5 now ADOPTS at 404 cells — so this test became the first
    place where one page both merges and adopts, which is exactly the state R171 recorded as
    unexercised. It is no longer an equality of counts; it is a real trip through
    document.py's adoption path.

    THE COUNT MOVED ON THE LEFT ONLY, and the right-hand 12 is NOT stale. `page_bands` under
    this monkeypatch is 12, not p5's natural 15, because forcing run (2,5) merges four bands
    into one (15 - 3 = 12) — the sibling test above asserts exactly that. What adoption adds
    are two regions the band count cannot contain: the grid's own RECORD_TABLE region
    (`#p5-datagrid`, 404 cells) and the DATAGRID_RESIDUE region carrying the tokens the grid
    left unread. MEASURED 2026-09-14: 14 regions = 12 + 1 + 1.

    So the assertion pins the DECOMPOSITION rather than the number 14. A bare count taught
    nothing when it broke — it could not say whether a region had been gained, lost, or
    renumbered — and the two additions are the ones adoption is defined to make."""
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document

    monkeypatch.setattr(
        compile_mod, "merged_run_admissible",
        lambda merged, first, last, page_number: (first, last) == (2, 6))

    doc = compile_document(BFS, validate_shapes=False)
    regions = doc.pages[5].regions
    n_bands = len(page_bands(BFS, 5))
    # 12 -> 13 on 2026-09-19 (run 2..6 of 17 bands; see the sibling test above).
    assert n_bands == 13, f"the run 2..6 must still merge five bands into one: {n_bands}"

    # the grid region adoption appends, and the residue region for what it left unread
    grid = [r for r in regions if r.table_uri and str(r.table_uri).endswith("p5-datagrid")]
    residue = [r for r in regions if r.reason == "DATAGRID_RESIDUE"]
    assert len(grid) == 1, f"adoption appended no single grid region: {len(grid)}"
    # 1 -> 0 on 2026-09-19, and the decomposition below is what still holds. The forced run is
    # now 2..6 and its fifth band is T1's NOTES (see the sibling test): their full-width ink
    # closes every gutter of the merged band, so it classifies NON_TABLE / "fewer than 2 columns"
    # and is IGNORED, where the forced 2..5 band escalated. The adoption ledger books residue
    # only from bands that had booked escalated tokens, so this forced page now leaves none from
    # T1 — and the UNFORCED page still carries its residue region (17 tokens, measured the same
    # day). Pinned as "at most one, and if present it books ink" rather than dropped.
    assert len(residue) <= 1, f"more than one DATAGRID_RESIDUE region: {len(residue)}"
    # 404 -> 496: STALE SINCE 2026-09-16, not moved today. R238's decoration->alignment switch
    # added the row-label and `%` columns to this grid (+92 cells — R240's row, and the figure
    # tests/test_carriage.py pins as P5_CELLS_WHEN_CARRIED). This assertion has failed on every
    # local run since; CI never saw it because the corpus is gitignored there and the test skips.
    # Found 2026-09-18 by sweeping the corpus-gated suite locally after the same blind spot let
    # two PRs merge with stale pins.
    assert grid[0].cells == 496, grid[0].cells
    assert all(r.tokens_escalated > 0 for r in residue), "a residue region that books no unread ink"

    # ...and nothing else appeared: every remaining region is one of the merged page's bands
    assert len(regions) == n_bands + 1 + len(residue), (
        f"{len(regions)} regions for {n_bands} bands + grid + {len(residue)} residue")
