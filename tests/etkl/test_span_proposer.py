import dataclasses
from iladub.etkl.propose import SpanProposal, SpanProposer, FakeSpanProposer


def test_spanproposal_is_frozen():
    p = SpanProposal("absorb", 0.9, "reads as one span")
    assert dataclasses.is_dataclass(p) and p.choice == "absorb"
    try:
        p.choice = "standalone"  # type: ignore[misc]
        assert False, "SpanProposal must be frozen"
    except dataclasses.FrozenInstanceError:
        pass


def test_fake_span_proposer_returns_fixed_proposal():
    p = SpanProposal("standalone", 0.7, "flank is its own column")
    fp = FakeSpanProposer(p)
    assert fp.propose_header_span({"span_label": "Current Visit"}) is p


def test_fake_span_proposer_can_abstain():
    assert FakeSpanProposer(None).propose_header_span({}) is None


def test_span_proposer_protocol_shape():
    assert hasattr(SpanProposer, "propose_header_span")
    FakeSpanProposer(None).propose_header_span({})  # structural smoke
