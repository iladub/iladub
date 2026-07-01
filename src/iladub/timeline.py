"""Generic timeline engine: drive a time-critical supply chain from a declarative
TimelineContract (a dec:Process of dec:Milestones). Domain-agnostic — it knows
nothing about organs, only about order, required context, and clocks."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .allen import Interval, feasible, relation

DEC = Namespace("https://w3id.org/iladub/dec#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")


@dataclass(frozen=True)
class Milestone:
    id: URIRef
    order: int
    requires: tuple[URIRef, ...]
    clock_start: bool
    clock_stop: bool
    window_limit_minutes: int | None


def _required_properties(g: Graph, milestone: URIRef) -> tuple[URIRef, ...]:
    props: list[URIRef] = []
    for ctx in g.objects(milestone, DEC.requiresContext):
        for field in g.objects(ctx, ETKL.hasField):
            prop = g.value(field, ETKL.fillsProperty)
            if prop is not None:
                props.append(prop)
    return tuple(props)


def _flag(g: Graph, milestone: URIRef, prop: URIRef) -> bool:
    # Robust boolean read: an rdflib Literal subclasses str, so bool(Literal("false"))
    # is True (non-empty string). Use toPython() to get the real xsd:boolean value.
    v = g.value(milestone, prop)
    return bool(v.toPython()) if v is not None else False


class Timeline:
    def __init__(self, process: URIRef, milestones: list[Milestone]):
        self.process = process
        self._milestones = sorted(milestones, key=lambda m: m.order)

    @classmethod
    def from_graph(cls, g: Graph) -> "Timeline":
        process = g.value(predicate=RDF.type, object=DEC.Process)
        milestones: list[Milestone] = []
        for m in g.objects(process, DEC.hasMilestone):
            order = g.value(m, DEC.order)
            limit = g.value(m, DEC.windowLimitMinutes)
            milestones.append(Milestone(
                id=m,
                order=int(order) if order is not None else 0,
                requires=_required_properties(g, m),
                clock_start=_flag(g, m, DEC.clockStart),
                clock_stop=_flag(g, m, DEC.clockStop),
                window_limit_minutes=int(limit) if limit is not None else None,
            ))
        return cls(process, milestones)

    def ordered(self) -> list[Milestone]:
        return list(self._milestones)

    def next_after(self, milestone: Milestone) -> "Milestone | None":
        seq = self._milestones
        for i, m in enumerate(seq):
            if m.id == milestone.id:
                return seq[i + 1] if i + 1 < len(seq) else None
        return None


@dataclass(frozen=True)
class Readiness:
    present: tuple[URIRef, ...]
    missing: tuple[URIRef, ...]

    @property
    def ready(self) -> bool:
        return not self.missing


def readiness(milestone: Milestone, context_graph: Graph, subject: URIRef) -> Readiness:
    present, missing = [], []
    for prop in milestone.requires:
        if (subject, prop, None) in context_graph:
            present.append(prop)
        else:
            missing.append(prop)
    return Readiness(tuple(present), tuple(missing))


@dataclass(frozen=True)
class CapturePlan:
    milestone_id: URIRef
    needed: tuple[URIRef, ...]


def next_capture_plan(timeline: "Timeline", current: Milestone,
                      context_graph: Graph, subject: URIRef) -> "CapturePlan | None":
    nxt = timeline.next_after(current)
    if nxt is None:
        return None
    return CapturePlan(nxt.id, readiness(nxt, context_graph, subject).missing)


class Cursor:
    def __init__(self, timeline: "Timeline"):
        self.timeline = timeline
        self._index = 0

    @property
    def current(self) -> Milestone:
        return self.timeline.ordered()[self._index]

    def advance(self, context_graph: Graph, subject: URIRef) -> bool:
        if not readiness(self.current, context_graph, subject).ready:
            return False
        if self._index + 1 >= len(self.timeline.ordered()):
            return False
        self._index += 1
        return True


@dataclass(frozen=True)
class Feasibility:
    relation: str
    feasible: bool
    slack_minutes: int


def feasibility(milestone: Milestone, cross_clamp_minute: int,
                transport: Interval) -> Feasibility:
    if milestone.window_limit_minutes is None:
        raise ValueError(f"milestone {milestone.id} has no window to assess")
    window = Interval(cross_clamp_minute, cross_clamp_minute + milestone.window_limit_minutes)
    return Feasibility(
        relation=relation(transport, window),
        feasible=feasible(window, transport),
        slack_minutes=window.end - transport.end,
    )
