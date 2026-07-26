"""The Fluree WRITE/commit gate: iladub's promotion invariant enforced at commit
(a grounded node without an accountable promotion is REJECTED), plus a static f:modify
policy authorizing writes only to the promotion's dec:decidedBy agent.
See docs/superpowers/specs/2026-07-25-fmodify-write-gate-design.md."""
import os
from rdflib import Graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
TST = os.path.join(ROOT, "tests")


def _knowledge():
    g = Graph()
    for f in ("iladub.ttl", "dec.ttl"):
        g.parse(os.path.join(ONT, f), format="turtle")
    return g


def test_gate_admits_a_properly_promoted_write():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-promoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert result.conforms, result.report_text


def test_gate_rejects_a_grounded_node_without_promotion():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-unpromoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms
    assert "promotion" in result.report_text.lower()


def test_gate_rejects_a_leaked_candidate():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "leak-attempt.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms
