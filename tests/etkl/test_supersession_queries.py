"""After section repair the record holds TWO chains for a band. Asking the obvious question
must not silently return the superseded one (spec §4.2/§4.3).

Both queries are read from disk — the .rq files are the artifact under test.
"""
import os

import pytest

from rdflib import URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")
CBH = os.path.join(ROOT, "corpus", "ag-trade", "cbh-stem-2026-08-03.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(CBH), reason="corpus doc not fetched")

REPAIRED = 1        # in repaired_bands ((0,1),(0,3),(0,5),(0,7))
UNREPAIRED = 0      # the control


@pytest.fixture(scope="module")
def cbh():
    """Compile CBH once — it takes minutes. Returns (merged graph, page-0 doc URI)."""
    from iladub.etkl.document import compile_document, page_doc_uri
    rep = compile_document(CBH)
    return rep.graph, page_doc_uri(0)


def _run(name, g, region):
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [r.asdict() for r in g.query(q, initBindings={"region": region})]


def _region(page_doc, idx):
    return URIRef(f"{page_doc}#region{idx}")


def test_a_superseded_chain_says_so_on_every_row(cbh):
    """The silent-misleading half of R70: a consumer reading ANY row must learn the chain
    they were handed has been replaced."""
    g, page_doc = cbh
    rows = _run("why-escalated.rq", g, _region(page_doc, REPAIRED))
    assert rows, f"no chain for repaired region {REPAIRED}"
    for r in rows:
        assert "supersededBy" in r, f"row without the marker: {r}"
    verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
    assert verdicts and str(verdicts[0]["chosen"]) == "escalated", \
        "the pass-1 chain should still read escalated — this query returns it as recorded"


def test_an_unsuperseded_chain_carries_no_marker(cbh):
    """The control. Without it, a query that ALWAYS bound the marker would pass the test
    above for the wrong reason."""
    g, page_doc = cbh
    rows = _run("why-escalated.rq", g, _region(page_doc, UNREPAIRED))
    assert rows, f"no chain for unrepaired region {UNREPAIRED}"
    for r in rows:
        assert "supersededBy" not in r, f"marker bound on an unsuperseded chain: {r}"


def test_effective_chain_returns_the_live_reading_after_repair(cbh):
    """The stale-answer half of R70."""
    g, page_doc = cbh
    rows = _run("effective-chain.rq", g, _region(page_doc, REPAIRED))
    assert rows, f"effective-chain returned nothing for repaired region {REPAIRED}"
    verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
    assert verdicts, f"no verdict in the effective chain: {rows}"
    assert str(verdicts[0]["chosen"]) == "asserted", \
        f"effective chain still reports the superseded verdict: {verdicts[0]}"


def test_effective_chain_equals_why_escalated_when_nothing_superseded_it(cbh):
    """A consumer must never need to know which case they are in."""
    g, page_doc = cbh
    region = _region(page_doc, UNREPAIRED)
    eff = [(int(r["order"]), str(r["judgement"])) for r in _run("effective-chain.rq", g, region)]
    why = [(int(r["order"]), str(r["judgement"])) for r in _run("why-escalated.rq", g, region)]
    assert eff == why, f"diverged on an unrepaired region:\n eff={eff}\n why={why}"


def test_effective_chain_is_ordered(cbh):
    g, page_doc = cbh
    orders = [int(r["order"]) for r in _run("effective-chain.rq", g, _region(page_doc, REPAIRED))]
    assert orders == sorted(orders), f"not ordered: {orders}"
