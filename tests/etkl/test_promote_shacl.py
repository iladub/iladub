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


# --- the three BAML-path promotions deliberate (spec 2026-08-10 §5.3) --------------
#
# PREMISE TYPE: **FIXTURE**, not evidence (spec §3.5). These three emitters are reached only
# under a BAML or Fake proposer and appear ZERO times in the corpus measurement
# (`promotions=0` on all 7 compiled graphs, docs/loops/2026-08-10-decision-membrane-baseline.md).
# The corpus does NOT cover them; unit tests are their only oracle, and this file says so
# rather than implying otherwise.
#
# The oracle is vocab/shapes/dec-shapes.ttl, which this loop may not edit. Its
# dec:DecisionHolonShape requires >= 2 deliberated options, exactly one chosen, and — via
# sh:sparql — that the chosen option is IN the option space.

from rdflib import Namespace, RDF, RDFS, URIRef

DECNS = Namespace("https://w3id.org/iladub/dec#")
ONT_DIR = Path(__file__).parents[2] / "vocab" / "ontology"
DEC_SHAPES = Path(__file__).parents[2] / "vocab" / "shapes" / "dec-shapes.ttl"


def _dec_conforms(g):
    """(conforms, text) against the SHIPPED closure, through `membrane._payload` — matching
    `membrane._validate_pyshacl` exactly (spec 2026-08-13-membrane-parity-design.md §3: since
    parity, that function validates `_payload`'s re-parsed graph, not `subclass_closure`'s
    live one, and this helper must track it or the claim is false). Called directly rather
    than through `membrane.validate` because this helper pins pySHACL's verdict on a shape
    SUBSET (dec-shapes.ttl alone), not the process engine's verdict on the membrane's full set.

    That bypass used to be FORCED: these fixtures mint blank-node PromotionDecisions
    (promote.py:67,114,158) and rudof raised rather than answering on dec-shapes.ttl's
    sh:sparql constraint with a blank-node focus. It no longer is — `membrane._payload`
    skolemizes (spec 2026-08-13-membrane-parity-design.md §4.3, closing R88) — so the bypass
    is now a choice."""
    from iladub.etkl import membrane
    ont = Graph()
    for f in ("dec.ttl", "iladub.ttl", "etkl.ttl", "tab.ttl"):
        ont.parse(str(ONT_DIR / f), format="turtle")
    shapes = Graph().parse(str(DEC_SHAPES), format="turtle")
    expanded, _ = membrane._payload(g, ont)
    conforms, _, text = validate(expanded, shacl_graph=shapes,
                                 inference="none", advanced=True)
    return bool(conforms), text


def _assert_deliberated(g, pd, label):
    """The three assertions every promotion decision owes dec:DecisionHolonShape."""
    conforms, text = _dec_conforms(g)
    assert conforms, f"[{label}] {text}"
    options = list(g.objects(pd, DECNS.optionSpace))
    assert len(options) >= 2, f"[{label}] a real decision deliberates >= 2 options: {options}"
    chosen = list(g.objects(pd, DECNS.chosen))
    assert len(chosen) == 1, f"[{label}] exactly one chosen option: {chosen}"
    assert chosen[0] in options, f"[{label}] the chosen option must be in the option space"
    for o in options:
        assert g.value(o, RDFS.label) is not None, f"[{label}] an unlabelled option: {o}"
        if o != chosen[0]:
            assert g.value(o, DECNS.rejectedBecause) is not None, (
                f"[{label}] the rejected option {o} does not say why it lost")
    return options, chosen[0]


def test_the_dimension_name_promotion_deliberates():
    """`emit_promotion`. The alternative is the branch reshape.py ACTUALLY takes when the
    round-trip oracle refuses (reshape.py:206, :219 — `return ProposalOutcome(None, ...)`,
    escalate with nothing asserted). Naming it invents nothing."""
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters")))
    assert out.normalized_base is not None, "setup: certify_with_proposals must succeed"
    pd = out.promotions[0]
    options, chosen = _assert_deliberated(g, pd, "dimension-name")
    assert "Quarter" in str(g.value(chosen, RDFS.label)), (
        "the chosen option must name the dimension it promoted")


def test_the_span_reading_promotion_deliberates():
    """`emit_span_promotion`. MEASURED at span.py:90 — the legal choices are enumerated by the
    code itself, `proposal.choice not in ("absorb", "standalone")`, and a tie is precisely the
    case where the code could have taken either. The option space IS that pair."""
    from iladub.etkl.promote import emit_span_promotion
    from iladub.etkl.propose import SpanProposal

    g = Graph()
    region = URIRef("urn:doc#htable0")
    pd = emit_span_promotion(g, region, "Current Visit", 4, "standalone",
                             SpanProposal("standalone", 0.82, "the flank reads as its own column"))
    options, chosen = _assert_deliberated(g, pd, "span-reading")
    labels = {str(g.value(o, RDFS.label)) for o in options}
    assert labels == {"absorb", "standalone"}, (
        f"the option space must be the tie the code enumerates at span.py:90: {labels}")
    assert str(g.value(chosen, RDFS.label)) == "standalone"


def test_the_row_role_promotion_deliberates():
    """`emit_row_role_promotion`. MEASURED at rowrole.py:36 — `ROLES = ("furniture",
    "continuation", "level")` is the code's own enumeration of the legal readings, and
    rowrole.py:16-17 records that tiling CANNOT discriminate furniture from continuation.
    The option space is that enumeration; the reason each alternative lost differs by which
    of them an oracle could have ranked."""
    from iladub.etkl.promote import emit_row_role_promotion
    from iladub.etkl.propose import RowRoleProposal

    g = Graph()
    region = URIRef("urn:doc#htable0")
    pd = emit_row_role_promotion(g, region, 1, "continuation", ["Net", "sales"],
                                 RowRoleProposal(("level", "continuation"), 0.7, "wraps"))
    options, chosen = _assert_deliberated(g, pd, "row-role")
    labels = {str(g.value(o, RDFS.label)) for o in options}
    assert labels == {"furniture", "continuation", "level"}, labels
    assert str(g.value(chosen, RDFS.label)) == "continuation"
    # the reasons are not one constant: the furniture/continuation pair is INDISCRIMINABLE by
    # tiling, while 'level' is simply not what was proposed — different epistemic situations.
    reasons = {str(g.value(o, RDFS.label)): str(g.value(o, DECNS.rejectedBecause))
               for o in options if o != chosen}
    assert len(set(reasons.values())) == len(reasons), (
        f"every rejected option lost for the same stated reason: {reasons}")
