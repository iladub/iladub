"""Loop M — the document driver (spec 2026-08-02 §3b): case-1 independence and
the DocumentReport contract. The case-2 stitching proof lives in
tests/test_corpus_stem.py against the real specimen."""
from iladub.etkl.document import compile_document
from tests.etkl.fixtures import two_page_unrelated_pdf


def test_case1_unrelated_pages_never_stitch(tmp_path):
    pdf = str(tmp_path / "unrelated.pdf")
    two_page_unrelated_pdf(pdf)
    rep = compile_document(pdf)
    assert len(rep.pages) == 2
    assert all(len(chain) == 1 for chain in rep.chains), rep.chains
    # both pages' tables asserted independently
    assert all(any(r.verdict == "asserted" for r in p.regions) for p in rep.pages)


def test_continuation_law_positive_and_negatives():
    """Law probes on hand-built evidence: identical leaves+x's -> continuation;
    one differing cell text -> not; one extra column -> not; shifted x -> not."""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    # helper builds the evidence graph directly from (col, text, x) triples per page
    same = [(0, "Port", 40.0), (1, "Ship", 110.0), (2, "Tonnes", 180.0)]
    assert is_continuation(continuation_evidence_from_facts(same, same))
    diff_text = [(0, "Port", 40.0), (1, "Vessel", 110.0), (2, "Tonnes", 180.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, diff_text))
    extra_col = same + [(3, "Flag", 250.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, extra_col))
    assert not is_continuation(continuation_evidence_from_facts(extra_col, same))
    shifted = [(0, "Port", 40.0), (1, "Ship", 111.5), (2, "Tonnes", 180.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, shifted))


def test_continuation_law_author_boundary_clause_is_load_bearing():
    """Clause (d): the author's DRAWN grid must agree. Same leaf row on both pages,
    but a boundary the author drew at a different x -> not a continuation. (The
    measured reason this clause compares author-drawn boundaries only, never loop-G's
    ink-inferred ones, is stated in continuation-of.rq's header.)"""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    same = [(0, "Port", 40.0), (1, "Ship", 110.0), (2, "Tonnes", 180.0)]
    xs = (30.0, 100.0, 170.0, 240.0)
    assert is_continuation(continuation_evidence_from_facts(same, same, xs, xs))
    moved = (30.0, 100.0, 171.5, 240.0)
    assert not is_continuation(continuation_evidence_from_facts(same, same, xs, moved))
    dropped = (30.0, 100.0, 240.0)
    assert not is_continuation(continuation_evidence_from_facts(same, same, xs, dropped))
    assert not is_continuation(continuation_evidence_from_facts(same, same, dropped, xs))


def test_continuation_law_needs_both_leaf_rows():
    """Clause (a): a page evidencing no leaf header row neither continues nor is continued."""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    same = [(0, "Port", 40.0), (1, "Ship", 110.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, []))
    assert not is_continuation(continuation_evidence_from_facts([], same))
    assert not is_continuation(continuation_evidence_from_facts([], []))


def test_leaf_block_reads_the_production_bands(tmp_path):
    """The PRODUCTION evidence path, not hand-built facts: the driver's leaf_block must read a
    real compiled band's leaf header row (one cell per ruled column, exact text, ink origin) and
    its author-DRAWN grid boundaries. Guards the emitter the law is only as good as."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import leaf_block, _recognition_blocks
    pdf = str(tmp_path / "unrelated.pdf")
    meta = two_page_unrelated_pdf(pdf)
    for page, headers in ((0, meta["page1_headers"]), (1, meta["page2_headers"])):
        blocks = _recognition_blocks(page_bands(pdf, page))
        assert blocks, f"page {page} evidences no leaf block"
        cells, bounds = blocks[max(blocks)]
        assert [t for _, t, _ in cells] == headers
        assert [c for c, _, _ in cells] == list(range(len(headers)))
        # every boundary reported is one the author drew (the fixture rules ARE the grid)
        assert len(bounds) >= 2
    # a band with no vertical rule evidences nothing — refusal, not a verdict
    assert all(leaf_block(b) is None for b in page_bands(pdf, 0) if not b.rules)


def test_single_page_document_matches_compile_tables(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf
    pdf = str(tmp_path / "single.pdf")
    simple_table_pdf(pdf)
    single = compile_tables(pdf)
    doc = compile_document(pdf)
    assert len(doc.pages) == 1
    assert doc.score == single.score
    assert len(doc.graph) >= len(single.graph)   # same assertions (URIs may be page-scoped)
