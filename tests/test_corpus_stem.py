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
