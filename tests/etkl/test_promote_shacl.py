# tests/etkl/test_promote_shacl.py
"""SHACL-conformance test for Loop A2 promotion output.

The whole point of A2 is that a GenAI-proposed name is an HONEST, SHACL-conformant
proposition with correct provenance. This test validates that the emitted
CandidateConcept (and PromotionDecision) conform to iladub:CandidateConceptShape and
iladub:PromotionDecisionShape in vocab/shapes/iladub-shapes.ttl.

It must FAIL before the fixes in promote.py (missing suggestedAnchor, fromRegion,
status, and float-backed confidence) and PASS after.
"""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

from iladub.etkl.propose import FakeProposer, Proposal
from iladub.etkl.reshape import certify_with_proposals
from tests.etkl.test_certify_proposals import _nameless_pivot

SHAPES_PATH = (
    Path(__file__).parents[2] / "vocab" / "shapes" / "iladub-shapes.ttl"
)


def test_promote_shacl_conforms():
    """After emit_promotion, the graph must satisfy iladub:CandidateConceptShape
    and iladub:PromotionDecisionShape — i.e. SHACL validation must pass."""
    g, t = _nameless_pivot()
    out = certify_with_proposals(
        g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters"))
    )
    assert out.normalized_base is not None, "setup: certify_with_proposals must succeed"

    shapes = Graph().parse(str(SHAPES_PATH), format="turtle")
    conforms, _, report = validate(
        g,
        shacl_graph=shapes,
        inference="rdfs",
        advanced=True,
    )
    if not conforms:
        print("\n=== SHACL violation report ===\n" + report)
    assert conforms, "emitted CandidateConcept must conform to iladub:CandidateConceptShape"
