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
