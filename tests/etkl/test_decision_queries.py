"""The record is an audit surface only if a question can be answered from it BY QUERY.
These tests run the committed .rq files against a real compiled graph (spec §4/§6)."""
import os
import pytest
from rdflib import Namespace, URIRef

DEC = Namespace("https://w3id.org/iladub/dec#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus doc not fetched")


@pytest.fixture(scope="module")
def g():
    """Compile apple page 0 once for the whole module — compiling takes ~1 minute."""
    from iladub.etkl import compile_tables
    return compile_tables(APPLE, page_number=0).graph


def _run(name, graph, region):
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [tuple(r) for r in graph.query(q, initBindings={"region": region})]


def _region(idx):
    from iladub.etkl.compile import _DOC
    return URIRef(f"{_DOC}#region{idx}")


def test_why_escalated_returns_an_ordered_chain(g):
    rows = _run("why-escalated.rq", g, _region(3))
    assert rows, "no chain for band 3"
    orders = [int(r[0]) for r in rows]
    assert orders == sorted(orders), "chain is not ordered"
    assert any("1 words" in str(r[3]) for r in rows), \
        f"band 3's kind rationale missing from the chain: {rows}"


def test_what_was_considered_shows_the_thin_option_space(g):
    """Spec §5: the record must show, truthfully, that the reader had almost no differential.
    This test asserts the record is HONEST about that, not that the space is large."""
    rows = _run("what-was-considered.rq", g, _region(3))
    kinds = {str(o) for j, o, _ in rows if str(j) == "kind"}
    assert kinds == {"RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"}, kinds
    refuted = [(o, r) for j, o, r in rows if r is not None]
    assert refuted, "no candidate carries its refutation"


def test_judgement_order_answers_the_r55_question(g):
    """Band 4: looks_transposed fired BEFORE the coherence oracle was consulted."""
    rows = _run("judgement-order.rq", g, _region(4))
    order = {str(j): int(o) for j, o in rows}
    assert "transposed" in order, f"got {sorted(order)}"
    if "transpose_coherent" in order:
        assert order["transposed"] < order["transpose_coherent"]
