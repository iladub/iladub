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
