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

    Five tests need it and a full 3-page compile costs 180 s (measured 2026-08-03, loop N review;
    it was ~3.5 min before loop N's document-level pass, and 325 s at the first cut of that pass
    — the row-group KEY derivation was rewritten to the aggregation form and now costs 5 s where
    it cost 104 s). The dominant remaining cost is loop I's `row-group-nesting.rq`, 97 s over the
    logical table's 57 groups: registered, not silently absorbed — see the task-3 report.
    Compiling per test would spend ~15 minutes of every suite run on the identical graph.
    `DocumentReport` is frozen and
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
    # Loop Q fix round 2 (2026-08-04): the stem's own loop-C reading-furniture captions
    # ('Friday, 31'/'July 2026', a print-timestamp line inside a header region, carried by
    # rowrole.emit_reading_evidence as a plain tab:RegionCaption — never a section key) must
    # never be read as a candidate section key: no record identity may be furniture-prefixed,
    # and no record may carry a furniture-sourced is_section_marker concept. Measured before
    # this pin existed: still-quarantined drifted 1265->1341 and identities read
    # 'Friday, 31 > 2025/26 > Jul 26 > Mackay' instead of '2025/26 > Jul 26 > Mackay > r9'.
    assert not any(c.is_section_marker for r in records for c in r.concepts), \
        [c for r in records for c in r.concepts if c.is_section_marker]
    assert not any("Friday" in r.row_id or "July 2026" in r.row_id for r in records), \
        [r.row_id for r in records if "Friday" in r.row_id or "July 2026" in r.row_id]


@needs_stem
def test_stem_r35_closed(stem_document):
    """R35's closure, measured: p2 subtotals confirm, keys reach every page,
    identity is one kind. Red until loop N lands."""
    from rdflib import RDF
    from iladub.etkl.holon import TAB
    g = stem_document.graph
    p2_aggs = [a for a in g.subjects(RDF.type, TAB.DetectedAggregationRow)
               if "/p2" in str(a)]
    assert len(p2_aggs) >= 20, f"p2 confirmed aggregations: {len(p2_aggs)} (was 0)"
    # cross-page operands exist (the cut Portland group)
    assert any(any("/p1" in str(m) for m in g.objects(a, TAB.aggregates))
               for a in p2_aggs)


@needs_stem
def test_stem_record_identity_is_one_kind(stem_document):
    """R35's third face: the document's records are identified ONE way, not two (loop N).

    Before the document-level groups, a chain member's rows could only be covered by their own
    page's groups, so page 1 and page 2 minted a mixture: group paths where a page-local
    subtotal happened to confirm, opaque `p2 htable1-r41` discriminators everywhere else
    (measured: 47 opaque of 133, plus 19 truncated 2-level paths). The identity kind depended
    on which page a row landed on — an artefact of pagination, exactly what loop N un-does.

    The invariant asserted here is structural, not a tally: a record is identified by its group
    path IF AND ONLY IF a derived group covers its row. Anything else would mean the feed and
    the derivation disagree. The remaining opaque id is therefore not a second kind of identity
    but the honest §7 answer for a row no confirmed aggregation covers — on this edition exactly
    one, the document's 'Grand Total' row.

    WHY THAT ROW IS NOT CONFIRMED, measured rather than assumed (loop N review corrected an
    earlier claim here that the arithmetic disagreed with it — it does not): the 132
    non-aggregation rows other than the Grand Total itself sum to EXACTLY the printed 2,402,500
    (927,500 + 804,000 + 671,000 over pages 0/1/2, by `rows._numeric_token_sum`). The refusal
    is loop H's documented ZERO-MEMBER rule (rows.py: "a grand total directly after a same-level
    total is never confirmed"): the row immediately above it is `2026/27 Total`, an already-confirmed
    aggregation whose label column (0) is not deeper than the Grand Total's own (0), so the member
    walk-back stops before collecting a single operand. No members, no confirmation — the same
    honest refusal R18's family describes, not an arithmetic disagreement. Tallies printed, not pinned.
    """
    import re
    from collections import Counter
    from rdflib import Graph, RDF
    from iladub.etkl.holon import TAB
    from iladub.feed import table_records, _row_discriminator

    g = stem_document.graph
    recs = table_records(g)
    covered = {_row_discriminator(g, m)
               for grp in g.subjects(RDF.type, TAB.DerivedRowGroup)
               for m in g.objects(grp, TAB.coversRow)}
    frag = re.compile(r"^p\d+ \S+$")            # the page-qualified row discriminator

    def anatomy(rid):
        parts = rid.split(" > ")
        return sum(1 for p in parts if not frag.match(p)), sum(1 for p in parts if frag.match(p))

    shapes = Counter(anatomy(r.row_id) for r in recs)
    opaque = [r.row_id for r in recs if " > " not in r.row_id]
    print(f"\nstem record-id anatomy (group labels, row discriminators) -> count: "
          f"{ {k: v for k, v in sorted(shapes.items())} }  bare-discriminator={opaque}")
    # no opaque id names a row a group covers: the feed and the derivation agree
    assert not [rid for rid in opaque if rid in covered], opaque
    # Every id is a group path of at least one label, followed by AT MOST ONE row
    # discriminator (the collision guard's suffix) — never two, never a fragment in the
    # middle. NB the label depth is NOT uniform and the report says so: a row whose month
    # group confirmed but whose port group did not carries the shorter path, completed by
    # the discriminator. That is R18's cascade, not a second identity kind.
    for r in recs:
        labels, frags = anatomy(r.row_id)
        assert frags <= 1, r.row_id
        assert labels >= 1 or frags == 1, r.row_id
        assert not frag.match(r.row_id.split(" > ")[0]) or " > " not in r.row_id, r.row_id
    # DETERMINISM (loop N review): the same graph must mint the same subjects however its
    # triples are ordered. 7 of 132 covered rows are covered by two groups at one level, and
    # before the tie-break the winner was rdflib's iteration order.
    reordered = Graph()
    for t in reversed(list(g)):
        reordered.add(t)
    assert [r.row_id for r in table_records(reordered)] == [r.row_id for r in recs]


@needs_stem
def test_stem_document_is_byte_identical_under_adoption(stem_document):
    """The adjudicated floor, to the last digit (spec §V1). Adoption must not fire here:
    carriage makes p1/p2 assert BEFORE the gate can ask. If this number moves, STOP and
    report it — never lower it."""
    assert stem_document.score == 0.9654553611484971, stem_document.score
    assert stem_document.adopted == (), stem_document.adopted
    assert len(stem_document.chains) == 1 and len(stem_document.chains[0]) == 3


@needs_stem
def test_page_scope_adoption_would_have_taken_the_page_the_driver_reads():
    """THE REFUSAL BRANCH, on real evidence (spec §M3).

    The FIRST half of the refusal is structural, not numeric: a single-page compile is
    incapable of chaining AT ALL (`CompilationReport` carries no chain concept; chains exist
    only on the document driver's report), so page scope could never see the pages p1
    continues onto, whatever it scored. stem p1 compiled ALONE reads flat — 811 cells, no
    chain.

    The score corroborates it SAME-PAGE, which is the like-for-like comparison: standalone
    0.9588, against 0.9706 for the driver's own reading of that same page 1 (Loop M, recorded
    at docs/superpowers/residues.md R29). Page scope reads this page WORSE, not better. The
    two COUNTS are not comparable and are not compared: R29's 825 is TOKENS asserted under the
    driver, the standalone 811 is CELLS; only the scores share a scale.

    THE ASSERTION BELOW DELIBERATELY PINS THE DOCUMENT FLOOR, NOT 0.9706. 0.9706 is a
    4-decimal figure from an earlier loop and no full-precision value for it was measured
    here; pinning against a rounded number would be exactly the defect this loop closes. The
    prose cites R29; the assertion stays at the full-precision 0.9654553611484971, which the
    driver reads over all three pages as one chain of 3, 2152 cells (measured in
    test_stem_document_is_byte_identical_under_adoption / test_stem_document_stitches_three_pages,
    same fixture). This test is the reason adoption is the document's LAST reader and not
    the page's first."""
    from iladub.etkl.compile import compile_tables

    standalone = compile_tables(str(STEM), 1, validate_shapes=False, datagrid_adopt=True)
    assert standalone.asserted > 0, "the grid does read this page standalone"
    grid_cells = sum(r.cells for r in standalone.regions)
    # measured regression guard (loop review, not a placeholder): 811 flat cells exactly.
    assert grid_cells == 811, grid_cells
    # the invariant the docstring claims, pinned rather than left for a human to notice:
    # the isolated reading scores LOWER than the document floor, never higher or equal.
    assert standalone.score < 0.9654553611484971, standalone.score
    print(f"\nstem p1 standalone adopted: {grid_cells} FLAT cells, "
          f"score={standalone.score:.4f}")


@needs_stem
def test_stem_keys_reach_every_page(stem_document):
    """Every record carries the outer fiscal-year key (was: p1 1/51, p2 3/65).

    `table_records` returns `list[Record]` (a dataclass: `.row_id` + `.concepts`, each a
    `SurfaceConcept` carrying `.text`) — not `(row_id, concepts)` tuples, so this reads the
    dataclass's own attributes rather than unpacking it (loop-L precedent: adapt plumbing to
    reality, the assertions' meaning is unchanged)."""
    from iladub.feed import table_records
    recs = table_records(stem_document.graph)
    missing = [rec.row_id for rec in recs
               if not any(c.text == "GC Fin Year" for c in rec.concepts)]
    print(f"\nrecords={len(recs)} missing-year-key={len(missing)}")
    assert not missing, f"{len(missing)} records lack the outer key"
    # subtotal rows no longer mint records: count drops below 154
    assert len(recs) < 154
