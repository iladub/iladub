"""R129 — a non-IRI suggester REFUSES at the mint site; it does not crash the membrane later.

The defect, as the register recorded it: a proposer returning `suggester_iri="not an iri at all"`
reached `URIRef(...)` unchallenged at five mint sites and died hundreds of triples later inside
`membrane._payload_nt`'s `skolemize(...).serialize(format="nt")` with a RAW `Exception` — not an
`AssertionError`, so neither a membrane verdict nor catchable as one, and `MembraneRefusal` (an
`AssertionError` subclass) would not catch it either.

The row also recorded precisely how far its own evidence went: *"the rdflib behaviour is measured;
the end-to-end route from a proposer through `membrane.py:348` is read from the call chain, not
driven by a test."* `test_a_proposer_returning_a_non_iri_suggester_refuses_at_the_public_seam`
below drives that route.
"""
import pytest
from rdflib import Graph, Namespace, RDF, URIRef

from iladub.etkl.membrane import suggester_agent, MembraneRefusal

BAD = "not an iri at all"


# ==================================================================== the guard itself

def test_the_guard_admits_a_serializable_iri():
    assert suggester_agent("urn:iladub:suggester/exact-match-rule") == \
        URIRef("urn:iladub:suggester/exact-match-rule")


def test_the_guard_refuses_a_non_iri_as_a_verdict_carrying_the_value():
    """The row's closure criterion, in one line: an `AssertionError` carrying the offending
    value, not a serialization crash."""
    with pytest.raises(AssertionError) as exc:
        suggester_agent(BAD)
    assert BAD in str(exc.value)


def test_the_guard_is_exactly_as_strict_as_the_serializer():
    """Not a hand-written IRI regex — a second opinion could drift out of step with rdflib in
    either direction, and the permissive direction puts the crash back. Anything `URIRef.n3()`
    accepts, the guard accepts; anything it rejects, the guard rejects."""
    for value in ("urn:iladub:suggester/ok", "https://ex.org/a#b", BAD, "urn:x:a b"):
        serializable = True
        try:
            URIRef(value).n3()
        except Exception:
            serializable = False
        refused = False
        try:
            suggester_agent(value)
        except AssertionError:
            refused = True
        assert refused is not serializable, value


def test_the_raw_exception_the_guard_replaces_is_not_catchable_as_a_verdict():
    """WHY this is a repair and not a style change. Without the guard the failure surfaces as a
    bare `Exception` from rdflib's serializer, which `except AssertionError` — the clause every
    membrane verdict in this repo shares — does not catch."""
    g = Graph()
    g.add((URIRef(BAD), RDF.type, URIRef("urn:iladub:Suggester")))
    with pytest.raises(Exception) as exc:
        g.serialize(format="nt")
    assert not isinstance(exc.value, AssertionError)
    assert not isinstance(exc.value, MembraneRefusal)


# ==================================================================== the five mint sites

def test_ground_emit_candidate_refuses(monkeypatch):
    from iladub.ground import SurfaceConcept, _emit_candidate
    with pytest.raises(AssertionError) as exc:
        _emit_candidate(Graph(), SurfaceConcept("x", "1", "r0"),
                        "https://ex.org/anchor", BAD, 0.5)
    assert BAD in str(exc.value)


def test_splitkey_emit_candidate_refuses():
    from iladub.splitkey import _emit_candidate
    with pytest.raises(AssertionError) as exc:
        _emit_candidate(Graph(), "Fiscal Quarter", ("Q1",), "https://ex.org/anchor", BAD, 0.5)
    assert BAD in str(exc.value)


def test_promote_suggester_refuses():
    from types import SimpleNamespace
    from iladub.etkl.promote import _suggester
    with pytest.raises(AssertionError) as exc:
        _suggester(Graph(), SimpleNamespace(suggester_iri=BAD))
    assert BAD in str(exc.value)


def test_promote_emit_span_promotion_refuses():
    from types import SimpleNamespace
    from iladub.etkl.promote import emit_span_promotion
    proposal = SimpleNamespace(suggester_iri=BAD, confidence=0.5)
    with pytest.raises(AssertionError) as exc:
        emit_span_promotion(Graph(), URIRef("urn:test:region"), "text", (0, 1), "merge", proposal)
    assert BAD in str(exc.value)


def test_holon_suggester_uri_refuses_a_reason_that_is_not_iri_safe():
    """The fifth site DERIVES its IRI from an escalation reason rather than taking one from a
    proposer — and a reason carrying a space produces exactly the same unserializable IRI, so it
    is guarded on the same footing rather than exempted for being 'internal'."""
    from iladub.etkl.holon import _suggester_uri
    assert _suggester_uri("ROUND_TRIP_FAIL") == URIRef("urn:iladub:suggester/round-trip-fail-rule")
    with pytest.raises(AssertionError) as exc:
        _suggester_uri("matrix ambiguous")
    assert "matrix ambiguous" in str(exc.value)


# ==================================================================== the public seam, driven

def test_a_proposer_returning_a_non_iri_suggester_refuses_at_the_public_seam():
    """The route the row could only READ off the call chain, now DRIVEN: a proposer hands
    `ground_concept` a malformed suggester IRI, and the refusal happens at the mint, with the
    mint on the stack — not later, inside the membrane's serializer, as an uncatchable crash."""
    from iladub.ground import SurfaceConcept, load_contract, ground_concept
    from iladub.propose_ground import GroundingProposal, FakeGroundingProposer
    TX = Namespace("https://example.org/transplant#")
    contract = load_contract("examples/transplant/offer-contract.ttl")
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    proposer = FakeGroundingProposer(
        GroundingProposal(None, str(TX) + "x", 0.1, "n/a", suggester_iri=BAD))
    with pytest.raises(AssertionError) as exc:
        ground_concept(SurfaceConcept("mystery", "55%", "r3"), contract,
                       URIRef("urn:test:offer1"), proposer, terms, shapes, Graph())
    assert BAD in str(exc.value)
