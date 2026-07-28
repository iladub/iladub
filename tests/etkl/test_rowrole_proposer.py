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


def test_baml_function_and_python_proposer_agree_on_arity():
    """The check Loop C added after finding BamlSpanProposer calls a ProposeHeaderSpan that was
    never authored in baml_src/. The live path is env-gated off, so a mismatch would surface only
    in production — pin it here instead."""
    import os
    import re
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    baml = open(os.path.join(root, "baml_src", "header_rowrole.baml"), encoding="utf-8").read()
    sig = re.search(r"function ProposeHeaderRowRoles\((.*?)\)", baml, re.S).group(1)
    params = [p.split(":")[0].strip() for p in sig.split(",")]
    assert params == ["rows", "leaf_labels", "row_columns",
                      "merge_candidates", "row_cell_counts", "leaf_column_count"]

    src = open(os.path.join(root, "src", "iladub", "etkl", "propose.py"), encoding="utf-8").read()
    call = re.search(r"sync_client\.b\.ProposeHeaderRowRoles\((.*?)\n\s*\)\s*\n\s*return",
                     src, re.S).group(1)
    args = [a.strip() for a in call.split(",") if a.strip()]
    # six positional arguments, in the SAME order as the BAML signature above
    assert len(args) == 6, args
    assert args[0] == 'context.get("rows")', args
    assert args[1] == 'context.get("leaf_labels")', args
    assert args[2] == 'context.get("row_columns")', args
    assert args[4] == 'context.get("row_cell_counts")', args
    assert args[5] == 'context.get("leaf_column_count")', args
    # args[3] is the locally-built merged-text list (dicts are flattened before the wire)
