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
    four fail. graincorp-stem alone loses 586 asserted cells."""
    from iladub.etkl.compile import compile_tables

    def cells(pdf, page):
        return sum(r.cells for r in compile_tables(pdf, page, validate_shapes=False).regions)

    assert cells(STEM, 0) == 586
    assert cells(CAPACITY, 0) == 390
    assert cells(BFS, 6) == 222
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
BASELINE_ASSERTED = {
    ("cbh-stem-2026-08-03", 0): 51,
    ("graincorp-capacity-2026-08-04", 0): 390,
    ("graincorp-stem-2026-07-31", 0): 586,
    ("graincorp-stem-2026-07-31", 1): 0,
    ("graincorp-stem-2026-07-31", 2): 0,
    ("apple-fy2026q3-statements", 0): 48,
    ("apple-fy2026q3-statements", 1): 14,
    ("apple-fy2026q3-statements", 2): 3,
    ("bfs-population-bilan-2023", 0): 0,
    ("bfs-population-bilan-2023", 1): 0,
    ("bfs-population-bilan-2023", 2): 0,
    ("bfs-population-bilan-2023", 3): 0,
    ("bfs-population-bilan-2023", 4): 0,
    ("bfs-population-bilan-2023", 5): 7,
    ("bfs-population-bilan-2023", 6): 222,
    ("ons-index-of-services-2026-02", 0): 0,
    ("ons-index-of-services-2026-02", 1): 0,
    ("ons-index-of-services-2026-02", 2): 0,
    ("ons-index-of-services-2026-02", 3): 0,
    ("ons-index-of-services-2026-02", 4): 19,
    ("ons-index-of-services-2026-02", 5): 0,
    ("ons-index-of-services-2026-02", 6): 0,
    ("ons-index-of-services-2026-02", 7): 0,
    ("ons-index-of-services-2026-02", 8): 0,
    ("who-wfa-boys-zscore-0-5", 0): 268,
    ("who-wfa-boys-zscore-0-5", 1): 257,
    ("who-wfa-boys-zscore-0-5", 2): 129,
}

# The ONLY two pages a merge may move, and both may only move UP. Every other page must be
# EQUAL: `>=` alone would not catch a page that silently gained ink for the wrong reason.
MERGE_MOVES = {("apple-fy2026q3-statements", 0), ("apple-fy2026q3-statements", 1)}

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
        else:
            assert rep.asserted == baseline, \
                f"{stem} p{page}: {rep.asserted} != {baseline} — the merge touches no " \
                f"page but apple p0 and p1, so a change here is a defect, not a gain"


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
        lambda merged, first, last, page_number: (first, last) == (2, 5))

    bands = page_bands(BFS, 5)
    assert len(bands) == 12, "the run 2..5 — four bands — must become one"

    rep = compile_tables(BFS, 5, validate_shapes=False)
    assert len(rep.regions) == 12
    minted = {int(m.group(2)) for m in re.finditer(_FRAGMENT_RE,
                                                   rep.graph.serialize(format="nt"))}
    assert minted, "no fragment was minted at all — the regex is wrong, not the code"
    assert max(minted) < 12, "a fragment index >= the band count means two index spaces"


@corpus_only
def test_o5_document_scope_completes_with_a_forced_non_tail_merge(monkeypatch):
    """The second half of O5: a document-scope compile over bfs completes, and adoption's
    grid_idx equals the page's band count on the merged page.

    THE LIMIT, stated because the spike measured it and the plan must not imply coverage
    it does not have: adoption's re-compile fires only on bfs p0 and p4 and is REFUSED on
    both, so ADOPTION'S BRANCH IS NEVER ENTERED on the merged page. This verifies an
    equality of counts, NOT a successful trip through document.py's adoption path. No
    corpus document both merges and adopts. That gap is R171."""
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document

    monkeypatch.setattr(
        compile_mod, "merged_run_admissible",
        lambda merged, first, last, page_number: (first, last) == (2, 5))

    doc = compile_document(BFS, validate_shapes=False)
    assert len(doc.pages[5].regions) == 12 == len(page_bands(BFS, 5))
