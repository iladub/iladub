"""Closed-loop anticipation: drive capture to ready the current milestone, merge
the result, and advance. Deterministic — the only non-deterministic surface is the
supplied capture_fn (which, for the transplant case, runs the SP1 LLM funnel)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rdflib import Graph, URIRef

from .timeline import (Timeline, Cursor, Readiness, CapturePlan,
                       readiness, next_capture_plan)


@dataclass
class CaptureStep:
    captured: Graph
    readiness_before: Readiness
    readiness_after: Readiness
    advanced: bool
    still_missing: tuple[URIRef, ...]
    next_plan: CapturePlan | None


def advance_with_capture(timeline: Timeline, cursor: Cursor, context_graph: Graph,
                         capture_fn: Callable[[], Graph], subject: URIRef) -> CaptureStep:
    before = readiness(cursor.current, context_graph, subject)
    captured = capture_fn()
    for triple in captured:
        context_graph.add(triple)
    after = readiness(cursor.current, context_graph, subject)
    # Forward look BEFORE advancing: the next milestone and the needs it still has.
    plan = next_capture_plan(timeline, cursor.current, context_graph, subject)
    advanced = cursor.advance(context_graph, subject)
    return CaptureStep(captured=captured, readiness_before=before, readiness_after=after,
                       advanced=advanced, still_missing=after.missing, next_plan=plan)
