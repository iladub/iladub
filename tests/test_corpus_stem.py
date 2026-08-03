# tests/test_corpus_stem.py
"""Loop L — the real GrainCorp stem (spec 2026-08-02 §3): the fluent-reader
invariant's first specimen. Corpus-marked: skips when corpus/ is not populated."""
import pytest

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STEM = REPO / "corpus" / "ag-trade" / "graincorp-stem-2026-07-31.pdf"

pytestmark = pytest.mark.corpus

needs_stem = pytest.mark.skipif(not STEM.is_file(),
                                reason="corpus not populated (scripts/fetch_corpus.py)")


@needs_stem
def test_stem_page0_compiles():
    """The invariant (spec §2): a human reads this page without hesitation, so it
    must compile — not escalate. Red until the header-stack fix lands."""
    from iladub.etkl import compile_tables, RegionKind
    rep = compile_tables(str(STEM), page_number=0)
    verdicts = [(r.kind, r.verdict, r.reason) for r in rep.regions]
    compiled = [r for r in rep.regions
                if r.verdict not in ("escalated",) and r.kind not in (RegionKind.NON_TABLE,)]
    assert compiled, f"page 0 produced no compiled table region: {verdicts}"
    assert sum(r.cells for r in rep.regions) >= 400, verdicts
    # Loop-K neighborhood (0.9496 on its edition). If the fix compiles the page but
    # lands below this floor: STOP, report the measured score to the controller —
    # do not lower the bar (Global Constraints: honest failure).
    assert rep.score >= 0.9, f"score {rep.score:.4f}"


@needs_stem
def test_stem_page0_grounds_against_contract():
    """Loop K's capstone on the LIVE document: assert/propose split with accountable
    promotions; non-grain cargo refused. Tallies are printed (edition-dependent),
    invariants are asserted (edition-independent)."""
    from rdflib import Graph, Namespace, RDF
    from iladub.etkl import compile_tables
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    ILADUB = Namespace("https://w3id.org/iladub#")
    SHIP = Namespace("https://example.org/shipping#")
    rep = compile_tables(str(STEM), page_number=0)
    contract = load_contract("examples/shipping/stem-contract.ttl")
    terms = Graph().parse("examples/shipping/stem-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/shipping/stem-shapes.ttl", format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = set(g.subjects(RDF.type, ILADUB.GroundedNode))
    proposed = set(g.subjects(RDF.type, ILADUB.CandidateConcept))
    # NB: `proposed` (CandidateConcept nodes) is the TOTAL candidate pool, not the
    # still-quarantined count — _emit_candidate fires for every concept before the
    # grounded/proposed branch, and a promoted concept's CandidateConcept node stays in
    # the graph. The honest still-quarantined count is FeedResult.proposed (the concepts
    # that never crossed the membrane); pool = grounded + still-quarantined.
    print(f"\nstem 2026-07-31 p0: grounded={len(grounded)} "
          f"still-quarantined={result.proposed} candidate-pool={len(proposed)}")
    assert len(grounded) >= 50 and len(proposed) > 0
    # every grounded node behind exactly one accountable promotion (the §3 invariant)
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1
    # honest refusal: non-grain cargo visible on this edition (Woodchip, Cement rows
    # measured in the ascii render) must NOT ground through the grain scheme.
    # iladub:surfaceText's rdfs:domain is CandidateConcept, not GroundedNode (see
    # vocab/ontology/iladub.ttl:83-84) — a GroundedNode carries its surface text one hop
    # back, via wasPromotedBy -> PromotionDecision -> reviews -> CandidateConcept (the
    # same traversal tests/test_stem_contract.py::test_injected_key_grounds_end_to_end
    # uses to resolve provenance), so walk that chain rather than reading the predicate
    # off the grounded node directly.
    grounded_texts = set()
    for n in grounded:
        pd = g.value(n, ILADUB.wasPromotedBy)
        cand = g.value(pd, ILADUB.reviews)
        for t in g.objects(cand, ILADUB.surfaceText):
            grounded_texts.add(str(t))
    assert not any("Woodchip" in t or "Cement" in t for t in grounded_texts), \
        sorted(t for t in grounded_texts if "Wood" in t or "Cem" in t)


def _ruled_band_page(pdf_path, page_number):
    """The compiled band + HierRegion for the main ruled table on one page (production path,
    generalizing tests/etkl/test_header_stack.py::_ruled_band from page 0 to any page)."""
    from dataclasses import replace as _replace
    from iladub.etkl.geometry import (extract_words, text_lines, extract_rules,
                                      extract_chars, extract_hrules)
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.segment import segment
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.hierarchical import classify_hierarchical
    words = extract_words(pdf_path, page_number)
    pr = extract_rules(pdf_path, page_number)
    ph = extract_hrules(pdf_path, page_number)
    pc = extract_chars(pdf_path, page_number) if pr else []
    out = []
    for band in detect_bands(text_lines(words)):
        for sub in segment(band):
            sr = tuple(r for r in pr if r.top <= sub.bottom and r.bottom >= sub.top)
            sh = tuple(h for h in ph if sub.top <= h.y <= sub.bottom)
            out.append(_build_ruled_band(sub, sr, sh, pc) if sr
                       else (_replace(sub, hrules=sh) if sh else sub))
    band = max(out, key=lambda b: len(b.lines))
    return band, classify_hierarchical(band)


@needs_stem
@pytest.mark.parametrize("page", [1, 2])
def test_stem_continuation_pages_status(page):
    """Pages 1-2 escalated REGION_TILING_FAILED pre-loop (cause NOT localized).
    This test records the post-fix state honestly: they must either compile or
    escalate — never crash. If they still escalate after Task 2, that is a
    MEASURED RESULT: report it to the controller; it becomes a registered
    residue + follow-up loop, not a silent pass and not a forced fix.

    POST-TASK-3 READING (measured 2026-08-02): they still escalate HERE, and that
    is the correct standalone answer, not a failure of the carriage. This test
    calls compile_tables on ONE page: standalone, a continuation page really is a
    header block with no table under it, and no recognition has licensed anything.
    The carriage is a DOCUMENT-level act — compile_document recognizes the break
    first and only then compiles page N with page N-1's confirmed reading. The
    stitched measurement lives in test_stem_document_stitches_three_pages."""
    from iladub.etkl import compile_tables
    rep = compile_tables(str(STEM), page_number=page)
    assert rep.regions, "no regions at all"
    print(f"\nstem p{page}: score={rep.score:.4f} "
          f"regions={[(r.kind.name, r.verdict, r.reason) for r in rep.regions]}")


@needs_stem
def test_stem_continuation_case_classification():
    """Loop M intake evidence (spec 2026-08-02 §3b) — MEASURED, not assumed. Two facts,
    printed for the controller/Loop M, no pass/fail gate beyond non-crash:

    (1) does page 1's TOP band line equal page 0's LEAF header row (Excel print-titles ->
        taxonomy case 2 WITH repeated headers), or does the band open directly on a body
        row (headerless continuation)? The top line alone is not decisive on this specimen
        (page 0 carries one extra furniture line — a print timestamp — that page 1 does not,
        so the row indices are offset by one), so this also checks whether page 1's own LEAF
        header row (wherever it falls) is textually identical to page 0's — the repeated-
        header signature survives that offset even when the raw top-line compare does not.
    (2) do the ruled column x-positions — the author's own vertical rule MARKS, not loop G's
        derived/confirmed boundaries — match across pages 0/1/2 (same template => same x's
        under the same scale)?
    """
    from iladub.etkl.headers import header_rows_of

    band0, hreg0 = _ruled_band_page(str(STEM), 0)
    band1, hreg1 = _ruled_band_page(str(STEM), 1)
    band2, hreg2 = _ruled_band_page(str(STEM), 2)

    leaf0 = [c.text for c in header_rows_of(band0, hreg0.grid, hreg0.body_line)[-1]]
    leaf1 = [c.text for c in header_rows_of(band1, hreg1.grid, hreg1.body_line)[-1]]
    top1 = [w.text for w in band1.lines[0].words]

    print(f"\npage0 leaf header row ({len(leaf0)} cells): {leaf0}")
    print(f"page1 TOP band line: {top1}")
    print(f"page1 leaf header row ({len(leaf1)} cells): {leaf1}")
    print(f"FACT 1a: page1 top band line == page0 leaf header row: {top1 == leaf0}")
    print(f"FACT 1b: page1 leaf header row == page0 leaf header row "
          f"(repeated headers): {leaf1 == leaf0}")

    rule_xs = {p: sorted({round(r.x, 2) for r in b.rules})
               for p, b in ((0, band0), (1, band1), (2, band2))}
    print("ruled column x-positions (author marks, not derived boundaries):")
    for p, xs in rule_xs.items():
        print(f"  page{p}: {xs}")
    print(f"FACT 2a: page0 rules == page1 rules: {rule_xs[0] == rule_xs[1]}")
    print(f"FACT 2b: page1 rules == page2 rules: {rule_xs[1] == rule_xs[2]}")

    # No assertion beyond non-crash — this is Loop M's intake evidence, not a gate.
    assert band0.lines and band1.lines and band2.lines


@pytest.fixture(scope="module")
def stem_document():
    """The whole-document compile, ONCE per module (loop M task 4 review, F7).

    Two tests need it and each full 3-page compile costs ~3.5 minutes, so compiling per test
    spent ~7 minutes of every suite run on the identical graph. `DocumentReport` is frozen and
    the tests below only READ it (`table_records` and `ground_document` never mutate the source
    graph — they write into a caller-supplied graph), so sharing it changes no measurement."""
    if not STEM.is_file():
        pytest.skip("corpus not populated (scripts/fetch_corpus.py)")
    from iladub.etkl.document import compile_document
    return compile_document(str(STEM))


@needs_stem
def test_stem_document_stitches_three_pages(stem_document):
    """Loop M's verifier (spec §3b): the whole stem is ONE logical table.
    RED until the driver + recognition land."""
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    rep = stem_document
    assert len(rep.pages) == 3
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 3, rep.chains
    total_cells = sum(sum(r.cells for r in p.regions) for p in rep.pages)
    print(f"\nstem document: score={rep.score:.4f} total_cells={total_cells}")
    assert total_cells > 586          # more than page 0 alone
    assert rep.score >= 0.9           # floor; if compiled-but-lower, STOP and report
    # repeated headers carried, never data: RepeatedHeader facts exist on pages 1-2
    reps = list(rep.graph.subjects(RDF.type, TAB.RepeatedHeader))
    assert reps, "repeated header blocks must be carried as facts"
    # page provenance: cells exist on all three pages
    pages = {int(o) for o in rep.graph.objects(None, TAB.onPage)}
    assert pages == {0, 1, 2}, pages


@needs_stem
def test_stem_document_grounds_full(stem_document):
    """Loop-K's capstone over the WHOLE document (loop M task 4). Invariants asserted,
    edition-dependent tallies printed.

    The chain-walk's own invariant is the LAST assertion: one record per data row of the
    logical table, each on its OWN subject. The three pages compile under page-scoped
    document URIs, so page 1 and page 2 share 65 row fragments (measured); reading the
    chain as one table without page-qualifying the discriminator grounds two different
    voyages onto one subject. The unit battery is tests/test_feed_chain_walk.py."""
    from rdflib import Graph, Namespace, RDF
    from iladub.feed import ground_document, table_records, _record_uri
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    ILADUB = Namespace("https://w3id.org/iladub#")
    SHIP = Namespace("https://example.org/shipping#")
    rep = stem_document
    contract = load_contract("examples/shipping/stem-contract.ttl")
    terms = Graph().parse("examples/shipping/stem-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/shipping/stem-shapes.ttl", format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = set(g.subjects(RDF.type, ILADUB.GroundedNode))
    print(f"\nstem FULL document: records={result.records} grounded={len(grounded)} "
          f"still-quarantined={result.proposed}")
    assert result.records > 33         # page 0 alone had 33-record-scale; full doc more
    assert len(grounded) > 167         # more than page 0 alone
    # every grounded node behind exactly one accountable promotion (the §3 invariant)
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1
    # the chain-walk invariant: no two rows of the logical table share a record subject
    records = table_records(rep.graph)
    assert len(records) == result.records
    assert len({str(_record_uri(r.row_id)) for r in records}) == len(records)
