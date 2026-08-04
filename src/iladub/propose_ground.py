"""propose_ground — the injected proposer seam for GenAI grounding (knowledge-first).

Mirrors iladub.etkl.propose: INJECTED so the pipeline is offline-testable (FakeGroundingProposer);
the live path (BamlGroundingProposer) is lazy + BAML_LIVE-gated.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Protocol

from .ground import ContractField, SurfaceConcept


@dataclass(frozen=True)
class GroundingProposal:
    field_iri: str | None
    anchor_iri: str
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/baml.ProposeGrounding"


class GroundingProposer(Protocol):
    def propose_grounding(self, concept: SurfaceConcept,
                          fields: tuple[ContractField, ...]) -> "GroundingProposal": ...


@dataclass(frozen=True)
class FakeGroundingProposer:
    """Deterministic offline proposer for tests/showcase. Returns its fixed proposal."""
    proposal: "GroundingProposal"

    def propose_grounding(self, concept, fields):
        return self.proposal


def baml_grounding_available() -> bool:
    """True only when explicitly enabled AND baml_client is importable."""
    return os.environ.get("BAML_LIVE") == "1" and importlib.util.find_spec("baml_client") is not None


class BamlGroundingProposer:
    """Live proposer — calls the BAML ProposeGrounding function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard."""

    def propose_grounding(self, concept, fields):
        from baml_client import sync_client
        labels = [f.fills_property.split("#")[-1] for f in fields]
        r = sync_client.b.ProposeGrounding(concept.text, concept.value, labels)
        # map the model's returned label back to a field IRI
        field_iri = None
        if r.field_iri:
            for f in fields:
                if f.fills_property.split("#")[-1] == r.field_iri or f.iri == r.field_iri:
                    field_iri = f.iri
                    break
        return GroundingProposal(field_iri=field_iri, anchor_iri=r.anchor_iri,
                                 confidence=r.confidence, rationale=r.rationale,
                                 suggester_iri="urn:iladub:suggester/baml.ProposeGrounding")


@dataclass(frozen=True)
class ScoredKeyCandidate:
    """One ranked candidate name for a denormalized split-key dimension (splitkey.py's
    naming cascade §4.3 step 3). `name` is a plain field-style name (e.g. "port"), matched
    by the cascade against the contract's admitting-field local names — NOT trusted as a
    field IRI directly, since the proposer never sees which fields verified."""
    name: str
    anchor_iri: str
    score: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/baml.ProposeSplitKeyName"


class SplitKeyNameProposer(Protocol):
    def propose_split_key_name(self, markers: list[str],
                               context: str) -> list["ScoredKeyCandidate"]: ...


@dataclass(frozen=True)
class FakeSplitKeyNameProposer:
    """Deterministic offline proposer for tests/showcase. Returns its fixed candidate list,
    ignoring markers/context (same idiom as FakeGroundingProposer)."""
    candidates: tuple["ScoredKeyCandidate", ...]

    def propose_split_key_name(self, markers, context):
        return list(self.candidates)


def baml_split_key_name_available() -> bool:
    """True only when explicitly enabled AND baml_client is importable."""
    return os.environ.get("BAML_LIVE") == "1" and importlib.util.find_spec("baml_client") is not None


class BamlSplitKeyNameProposer:
    """Live proposer — calls the BAML ProposeSplitKeyName function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard."""

    def propose_split_key_name(self, markers, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeSplitKeyName(list(markers), context)
        return [ScoredKeyCandidate(name=c.name, anchor_iri=c.anchor_iri, score=c.score,
                                   rationale=c.rationale,
                                   suggester_iri="urn:iladub:suggester/baml.ProposeSplitKeyName")
               for c in r]


@dataclass(frozen=True)
class MappingGroundingProposer:
    """Deterministic offline proposer for the concept feed: maps a concept's header TEXT to a
    fixed GroundingProposal (the honest stand-in for the BAML proposer's per-concept field
    proposal). An unmapped header returns a field_iri=None proposal -> the concept quarantines."""
    mapping: dict

    def propose_grounding(self, concept, fields):
        return self.mapping.get(
            concept.text,
            GroundingProposal(None, "https://w3id.org/semanticarts/ns/ontology/gist/Category",
                              0.0, "no mapping for %r" % concept.text,
                              "urn:iladub:suggester/mapping-proposer"),
        )
