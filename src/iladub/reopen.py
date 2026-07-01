"""Event-driven decision reopening: when an event matches a decision's declared
dec:revisitIf keys, re-evaluate the decision and emit a superseding decision holon
with full lineage. Domain-agnostic — the caller supplies how to re-evaluate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rdflib import Graph, Namespace, URIRef

from .decision import DecisionResult, build_decision_holon
from .events import Event

DEC = Namespace("https://w3id.org/iladub/dec#")
TX = Namespace("https://example.org/transplant#")


def revisit_conditions(decision_graph: Graph, subject: URIRef) -> set[str]:
    return {str(o) for o in decision_graph.objects(subject, DEC.revisitIf)}


def should_reopen(decision_graph: Graph, subject: URIRef, event: Event) -> bool:
    return event.condition in revisit_conditions(decision_graph, subject)


@dataclass
class ReopenOutcome:
    result: DecisionResult
    graph: Graph


def reopen(prior_subject: URIRef, event: Event,
           re_evaluate: Callable[[Event], DecisionResult], *,
           new_subject: URIRef, agent: URIRef = TX["surgeon-1"],
           event_subject: URIRef = TX["event-1"]) -> ReopenOutcome:
    new_result = re_evaluate(event)
    graph = build_decision_holon(new_result, subject=new_subject, agent=agent)
    graph += event.to_rdf(event_subject)
    graph.add((new_subject, DEC.supersedes, prior_subject))
    graph.add((new_subject, DEC.triggeredBy, event_subject))
    return ReopenOutcome(new_result, graph)
