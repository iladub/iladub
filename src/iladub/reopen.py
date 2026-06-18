"""Event-driven decision reopening: when an event matches a decision's declared
hol:revisitIf keys, re-evaluate the decision and emit a superseding decision holon
with full lineage. Domain-agnostic — the caller supplies how to re-evaluate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .decision import DecisionResult, build_decision_holon
from .events import Event

HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def revisit_conditions(decision_graph: Graph, subject: URIRef) -> set[str]:
    return {str(o) for o in decision_graph.objects(subject, HOL.revisitIf)}


def should_reopen(decision_graph: Graph, subject: URIRef, event: Event) -> bool:
    return event.condition in revisit_conditions(decision_graph, subject)
