"""propose — the injected proposer seam for GenAI-assisted reshape (Loop A2).

The proposer is how A2 reaches a model, boxed by BAML. It is INJECTED so all logic is
offline-testable (FakeProposer); the live path (BamlProposer) is lazy + env-gated.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Proposal:
    name: str
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/recorded-proposer"


class Proposer(Protocol):
    def propose_dimension_name(self, values: list, context: dict) -> "Proposal | None": ...


@dataclass(frozen=True)
class FakeProposer:
    """Deterministic offline proposer for tests/showcase. Returns its fixed proposal."""
    proposal: "Proposal | None"

    def propose_dimension_name(self, values, context):
        return self.proposal


def baml_proposer_available() -> bool:
    """True only when explicitly enabled AND baml_client is importable."""
    return os.environ.get("BAML_LIVE") == "1" and importlib.util.find_spec("baml_client") is not None


class BamlProposer:
    """Live proposer — calls the BAML ProposeDimensionName function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard."""

    def propose_dimension_name(self, values, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeDimensionName(values, context.get("stub"), context.get("title"))
        return Proposal(
            name=r.name,
            confidence=r.confidence,
            rationale=r.rationale,
            suggester_iri="urn:iladub:suggester/baml.ProposeDimensionName",
        )


@dataclass(frozen=True)
class SpanProposal:
    """A proposed reading for a narrow-flank merge tie (loop B1.3). `choice` is 'absorb'
    (the flank belongs under the span) or 'standalone' (the flank is its own top-level leaf).
    The reading is a PROPOSITION (§3): admitted only via a PromotionDecision after region_tiles
    confirms it is structurally legal — never asserted as grounded truth."""
    choice: str                 # "absorb" | "standalone"
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/recorded-span-proposer"


class SpanProposer(Protocol):
    def propose_header_span(self, context: dict) -> "SpanProposal | None": ...


@dataclass(frozen=True)
class FakeSpanProposer:
    """Deterministic offline span proposer for tests/showcase. Returns its fixed proposal
    (or None to model abstention)."""
    proposal: "SpanProposal | None"

    def propose_header_span(self, context):
        return self.proposal


class BamlSpanProposer:
    """Live span proposer — calls the BAML ProposeHeaderSpan function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard.
    NEURAL propose seam; env-gated by baml_proposer_available()."""

    def propose_header_span(self, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeHeaderSpan(
            context.get("span_label"),
            context.get("leaf_labels"),
            context.get("flank_label"),
            context.get("flank_side"),
        )
        return SpanProposal(
            choice=r.choice,
            confidence=r.confidence,
            rationale=r.rationale,
            suggester_iri="urn:iladub:suggester/baml.ProposeHeaderSpan",
        )
