"""Loop C — the injected row-role proposer seam. All logic is offline-testable via the
Fake; the live BAML path is lazy + env-gated. See spec §3.2."""
from iladub.etkl.propose import (BamlRowRoleProposer, FakeRowRoleProposer,
                                 RowRoleProposal, baml_proposer_available)


def test_fake_proposer_returns_its_fixed_proposal():
    p = RowRoleProposal(("furniture", "continuation"), 0.8, "date line, then a wrapped label")
    fake = FakeRowRoleProposer(p)
    assert fake.propose_header_row_roles({"rows": [], "leaf_labels": []}) is p


def test_fake_proposer_can_abstain():
    assert FakeRowRoleProposer(None).propose_header_row_roles({}) is None


def test_proposal_defaults_to_the_recorded_suggester_iri():
    p = RowRoleProposal(("level",), 0.5, "genuine group label")
    assert p.suggester_iri == "urn:iladub:suggester/recorded-rowrole-proposer"


def test_baml_proposer_constructs_without_baml_client():
    # lazy import guard: constructing the live proposer must never import baml_client
    # (mirrors BamlSpanProposer). Only CALLING it does.
    assert BamlRowRoleProposer() is not None


def test_live_path_is_env_gated():
    # the shipped gate: BAML_LIVE must be explicitly "1" AND baml_client importable
    import os
    if os.environ.get("BAML_LIVE") != "1":
        assert baml_proposer_available() is False
