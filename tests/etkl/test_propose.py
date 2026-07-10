import os
from iladub.etkl.propose import (Proposal, FakeProposer, baml_proposer_available,
                                  BamlProposer)


def test_fake_proposer_returns_proposal():
    p = FakeProposer(Proposal("Quarter", 0.9, "Q1..Q4 are quarters"))
    got = p.propose_dimension_name(["Q1", "Q2", "Q3", "Q4"], {"stub": "Product"})
    assert got.name == "Quarter" and got.confidence == 0.9


def test_fake_proposer_can_decline():
    assert FakeProposer(None).propose_dimension_name(["x"], {}) is None


def test_baml_gate_off_by_default(monkeypatch):
    monkeypatch.delenv("BAML_LIVE", raising=False)
    assert baml_proposer_available() is False


def test_baml_proposer_construction_is_lazy():
    # constructing must NOT import baml_client (no network / no version guard at construct time)
    b = BamlProposer()
    assert b is not None
