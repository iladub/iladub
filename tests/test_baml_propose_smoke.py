import os
import pytest


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1", reason="live BAML gated behind BAML_LIVE=1")
def test_propose_dimension_name_live():
    pytest.importorskip("baml_client")
    from iladub.etkl.propose import BamlProposer
    got = BamlProposer().propose_dimension_name(["Q1", "Q2", "Q3", "Q4"], {"stub": "Product", "title": None})
    assert got is not None and got.name          # a plausible non-empty name
    assert 0.0 <= got.confidence <= 1.0
