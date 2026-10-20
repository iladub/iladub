import pytest
from rdflib import Graph

from iladub.etkl.writegate import commit_gate_shapes
from tests.substrate.doc_a import compiled_interior, ungoverned

pytestmark = pytest.mark.substrate

INVARIANT = "INVARIANT: every grounded node must be produced by a promotion decision."


def test_engine_refuses_an_ungoverned_commit(fluree_endpoint):
    ep, fresh_ledger = fluree_endpoint
    ledger = fresh_ledger()
    ep.provision(ledger, commit_gate_shapes())
    t0 = ep.head_t(ledger)

    refused = ep.commit(ledger, ungoverned(compiled_interior()))
    assert refused.accepted is False
    assert refused.status == 400
    assert INVARIANT in refused.report
    assert ep.head_t(ledger) == t0

    admitted = ep.commit(ledger, compiled_interior())
    assert admitted.accepted is True
    assert ep.head_t(ledger) == t0 + 1
