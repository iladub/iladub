# SP2 — Generic Timeline Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a domain-agnostic timeline engine that drives time-critical supply chains from declarative TimelineContracts — proven by two instances (heart ~240 min, kidney ~1800 min) running on one engine — plus Allen-interval feasibility and an upgrade of the decision holon to the real `hol` vocabulary.

**Architecture:** Two layers. The engine (`timeline.py`, `allen.py`) is deterministic Python that knows nothing about organs; it reads a TimelineContract (declarative RDF, expressed in an extended `hol` vocabulary) and provides a cursor, readiness, a forward-pass capture plan, and clock feasibility. The instances (`examples/transplant/*-timeline.ttl`) are domain data. The decision holon emitted by `decision.py` is upgraded to conform to the existing `hol:DecisionHolonShape`.

**Tech Stack:** Python ≥3.11, rdflib, pyshacl (all existing). No LLM — SP2 is deterministic and fully CI-testable.

**Spec:** `docs/superpowers/specs/2026-06-18-timeline-engine-sp2-design.md`

---

## File structure & interfaces (the contract between tasks)

| File | Responsibility |
|---|---|
| `vocab/ontology/hol.ttl` (modify) | Add `hol:Process`, `hol:Milestone`, `hol:hasMilestone`, `hol:order`, `hol:requiresContext`, `hol:clockStart`, `hol:clockStop`, `hol:windowLimitMinutes`. |
| `vocab/shapes/hol-shapes.ttl` (modify) | Add `hol:MilestoneShape` (order required). |
| `src/iladub/allen.py` (create) | `Interval`, `relation(a,b)->str` (Allen's 13), `feasible(window,transport)->bool`. |
| `src/iladub/timeline.py` (create) | `Milestone`, `Timeline.from_graph`, `Cursor`, `readiness`, `next_capture_plan`, `feasibility`. |
| `src/iladub/decision.py` (modify) | Upgrade `build_decision_holon` to real `hol` vocab (Option/chosen/rejectedBecause/decidedBy/partOf). |
| `examples/transplant/heart-timeline.ttl` (create) | Heart-DBD process: M4–M8, inline required-context, cold-ischemia 240. |
| `examples/transplant/kidney-timeline.ttl` (create) | Kidney process: a *different* 4-milestone set, cold-ischemia 1800. |
| `examples/transplant/heart-timeline-conformant.ttl` / `-leak.ttl` (create) | Pass/fail the milestone shape. |
| `tests/test_allen.py`, `tests/test_timeline.py`, `tests/test_timeline_shacl.py` (create); `tests/test_decision.py` (modify) | Tests. |

**Shared dataclasses (defined in `allen.py` / `timeline.py`, imported by tests):**
```python
# allen.py
@dataclass(frozen=True)
class Interval:
    start: int   # minutes on a common axis
    end: int

# timeline.py
@dataclass(frozen=True)
class Milestone:
    id: URIRef
    order: int
    requires: tuple[URIRef, ...]      # required fillsProperty URIs (may be empty)
    clock_start: bool
    clock_stop: bool
    window_limit_minutes: int | None

@dataclass(frozen=True)
class Readiness:
    present: tuple[URIRef, ...]
    missing: tuple[URIRef, ...]
    @property
    def ready(self) -> bool: ...      # not self.missing

@dataclass(frozen=True)
class CapturePlan:
    milestone_id: URIRef
    needed: tuple[URIRef, ...]

@dataclass(frozen=True)
class Feasibility:
    relation: str
    feasible: bool
    slack_minutes: int
```

**Namespaces (consistent across tasks):**
```python
HOL  = Namespace("https://w3id.org/etkl/hol#")
ETKL = Namespace("https://w3id.org/etkl#")
TX   = Namespace("https://example.org/transplant#")
```

## Notes for the implementer
- Work from repo root `/Volumes/WD Green/dev/git/iladub` on branch `timeline-engine-sp2` (already created). This IS a git repo — commit per task. Venv: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python`; run tests with `python -m pytest`.
- SP2 is pure deterministic logic — no BAML, no API. The full suite (including SP1's offline tests) must stay green.
- `readiness` checks presence of a property on a subject in a *context graph* that the test supplies inline (a small rdflib Graph) — SP2 does not call SP1.

---

### Task 1: Extend the `hol` vocabulary + shape for timelines

**Files:**
- Modify: `vocab/ontology/hol.ttl`
- Modify: `vocab/shapes/hol-shapes.ttl`
- Test: `tests/test_timeline_vocab.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_timeline_vocab.py`:
```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def test_hol_defines_process_and_milestone():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    assert (HOL.Process, RDF.type, OWL.Class) in g
    assert (HOL.Milestone, RDF.type, OWL.Class) in g
    assert (HOL.windowLimitMinutes, RDF.type, OWL.DatatypeProperty) in g


def test_hol_shapes_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_timeline_vocab.py -v`
Expected: `test_hol_defines_process_and_milestone` FAILS (classes not yet defined).

- [ ] **Step 3: Add the classes/properties to `hol.ttl`**

Append to `vocab/ontology/hol.ttl` (before EOF; uses the prefixes already declared at the top of that file):
```turtle
#################################################################
#  Timeline / process holarchy (SP2)
#################################################################

hol:Process a owl:Class ;
    rdfs:label "Process"@en ;
    rdfs:comment "A holon whose parts are milestone decisions ordered over time — a time-critical supply chain."@en .

hol:Milestone a owl:Class ;
    rdfs:label "Milestone"@en ;
    rdfs:comment "A decision point in a process, with a required-context contract and optional clock role."@en .

hol:hasMilestone a owl:ObjectProperty ;
    rdfs:label "has milestone"@en ; rdfs:domain hol:Process ; rdfs:range hol:Milestone .

hol:order a owl:DatatypeProperty ;
    rdfs:label "order"@en ; rdfs:domain hol:Milestone ; rdfs:range xsd:integer ;
    rdfs:comment "Position of the milestone in the process sequence."@en .

hol:requiresContext a owl:ObjectProperty ;
    rdfs:label "requires context"@en ; rdfs:domain hol:Milestone ; rdfs:range etkl:SemanticDataContract ;
    rdfs:comment "The required-context contract that must be ready before this milestone's decision."@en .

hol:clockStart a owl:DatatypeProperty ;
    rdfs:label "clock start"@en ; rdfs:domain hol:Milestone ; rdfs:range xsd:boolean ;
    rdfs:comment "True if this milestone starts the dominant time-critical interval."@en .

hol:clockStop a owl:DatatypeProperty ;
    rdfs:label "clock stop"@en ; rdfs:domain hol:Milestone ; rdfs:range xsd:boolean ;
    rdfs:comment "True if this milestone stops the dominant time-critical interval."@en .

hol:windowLimitMinutes a owl:DatatypeProperty ;
    rdfs:label "window limit (minutes)"@en ; rdfs:domain hol:Milestone ; rdfs:range xsd:integer ;
    rdfs:comment "The maximum duration of the interval this milestone opens (e.g. cold-ischemia limit)."@en .
```

- [ ] **Step 4: Add the milestone shape to `hol-shapes.ttl`**

Append to `vocab/shapes/hol-shapes.ttl`:
```turtle
#################################################################
#  A milestone must declare its order (SP2).
#################################################################

hol:MilestoneShape a sh:NodeShape ;
    sh:targetClass hol:Milestone ;
    sh:property [ sh:path hol:order ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:datatype xsd:integer ;
        sh:message "A milestone must declare exactly one integer order." ] ;
    sh:property [ sh:path hol:windowLimitMinutes ; sh:maxCount 1 ; sh:datatype xsd:integer ;
        sh:message "windowLimitMinutes, if present, is a single integer." ] .
```

- [ ] **Step 5: Run the test + full suite**

Run: `python -m pytest tests/test_timeline_vocab.py tests/test_vocab_shapes.py -v && python -m pytest -q`
Expected: new tests PASS; existing vocab/shape tests still PASS; full suite green.

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/hol.ttl vocab/shapes/hol-shapes.ttl tests/test_timeline_vocab.py
git commit -m "feat(sp2): extend hol with Process/Milestone timeline vocabulary"
```

---

### Task 2: Allen interval feasibility (`allen.py`)

**Files:**
- Create: `src/iladub/allen.py`
- Test: `tests/test_allen.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_allen.py`:
```python
import pytest
from iladub.allen import Interval, relation, feasible


@pytest.mark.parametrize("a,b,expected", [
    (Interval(0, 10), Interval(20, 30), "before"),
    (Interval(20, 30), Interval(0, 10), "after"),
    (Interval(0, 10), Interval(10, 20), "meets"),
    (Interval(0, 15), Interval(10, 20), "overlaps"),
    (Interval(5, 8), Interval(0, 20), "during"),
    (Interval(0, 20), Interval(5, 8), "contains"),
    (Interval(0, 10), Interval(0, 20), "starts"),
    (Interval(10, 20), Interval(0, 20), "finishes"),
    (Interval(0, 20), Interval(0, 20), "equals"),
])
def test_relation_classifies(a, b, expected):
    assert relation(a, b) == expected


def test_feasible_when_transport_ends_within_window():
    window = Interval(0, 240)         # heart cold-ischemia
    assert feasible(window, Interval(0, 95)) is True


def test_infeasible_when_transport_exceeds_window():
    window = Interval(0, 240)
    assert feasible(window, Interval(0, 270)) is False
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_allen.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.allen'`.

- [ ] **Step 3: Implement `allen.py`**

Create `src/iladub/allen.py`:
```python
"""Allen's interval algebra over event start/end pairs.

The thirteen relations emerge from comparing the four endpoints of two intervals
(EventBasedModeling: a relation between a start event and an end event). `feasible`
is the supply-chain predicate: the carried thing reaches its terminus before the
critical window closes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    start: int
    end: int


def relation(a: Interval, b: Interval) -> str:
    """Return Allen's relation of interval ``a`` to interval ``b``."""
    if a.end < b.start:
        return "before"
    if a.start > b.end:
        return "after"
    if a.end == b.start:
        return "meets"
    if a.start == b.end:
        return "met-by"
    if a.start == b.start and a.end == b.end:
        return "equals"
    if a.start == b.start:
        return "starts" if a.end < b.end else "started-by"
    if a.end == b.end:
        return "finishes" if a.start > b.start else "finished-by"
    if a.start > b.start and a.end < b.end:
        return "during"
    if a.start < b.start and a.end > b.end:
        return "contains"
    if a.start < b.start and a.end > b.start and a.end < b.end:
        return "overlaps"
    return "overlapped-by"


def feasible(window: Interval, transport: Interval) -> bool:
    """True if the transport/prep interval terminates within the critical window."""
    return transport.end <= window.end
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest tests/test_allen.py -v`
Expected: all parametrized cases + both feasibility tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/allen.py tests/test_allen.py
git commit -m "feat(sp2): Allen interval algebra + supply-chain feasibility"
```

---

### Task 3: Heart TimelineContract instance

**Files:**
- Create: `examples/transplant/heart-timeline.ttl`
- Test: `tests/test_timeline.py` (first test; grows in later tasks)

- [ ] **Step 1: Write the heart timeline instance**

Create `examples/transplant/heart-timeline.ttl`:
```turtle
@prefix tx:   <https://example.org/transplant#> .
@prefix hol:  <https://w3id.org/etkl/hol#> .
@prefix etkl: <https://w3id.org/etkl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

tx:heart-process a hol:Process ;
    rdfs:label "Heart DBD transplant (M4–M8)"@en ;
    hol:hasMilestone tx:m4 , tx:m5 , tx:m6 , tx:m7 , tx:m8 .

tx:m4 a hol:Milestone ; rdfs:label "Offer → Acceptance"@en ; hol:order 4 ;
    hol:requiresContext tx:ctx-m4 .
tx:m5 a hol:Milestone ; rdfs:label "Mobilization"@en ; hol:order 5 ;
    hol:requiresContext tx:ctx-m5 .
tx:m6 a hol:Milestone ; rdfs:label "Cross-clamp"@en ; hol:order 6 ;
    hol:clockStart true ; hol:windowLimitMinutes 240 .
tx:m7 a hol:Milestone ; rdfs:label "Transport"@en ; hol:order 7 ;
    hol:requiresContext tx:ctx-m7 .
tx:m8 a hol:Milestone ; rdfs:label "Reperfusion"@en ; hol:order 8 ;
    hol:clockStop true .

tx:ctx-m4 a etkl:SemanticDataContract ; etkl:hasField tx:tf-organ , tx:tf-abo .
tx:ctx-m5 a etkl:SemanticDataContract ; etkl:hasField tx:tf-recipient-ready .
tx:ctx-m7 a etkl:SemanticDataContract ; etkl:hasField tx:tf-transport , tx:tf-crossclamp .

tx:tf-organ          a etkl:Field ; etkl:fillsProperty tx:organ .
tx:tf-abo            a etkl:Field ; etkl:fillsProperty tx:aboGroup .
tx:tf-recipient-ready a etkl:Field ; etkl:fillsProperty tx:recipientReady .
tx:tf-transport      a etkl:Field ; etkl:fillsProperty tx:projectedTransportMinutes .
tx:tf-crossclamp     a etkl:Field ; etkl:fillsProperty tx:crossClampTime .
```

- [ ] **Step 2: Write a parse/shape sanity test**

Create `tests/test_timeline.py`:
```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def test_heart_process_has_five_milestones():
    g = _heart_graph()
    ms = list(g.objects(TX["heart-process"], HOL.hasMilestone))
    assert len(ms) == 5
```

- [ ] **Step 3: Run the test**

Run: `python -m pytest tests/test_timeline.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/heart-timeline.ttl tests/test_timeline.py
git commit -m "feat(sp2): heart-DBD TimelineContract instance"
```

---

### Task 4: Timeline loader (`Timeline.from_graph`, `Milestone`, ordering)

**Files:**
- Create: `src/iladub/timeline.py`
- Test: add to `tests/test_timeline.py`

- [ ] **Step 1: Add the failing loader test**

Append to `tests/test_timeline.py`:
```python
from iladub.timeline import Timeline


def test_timeline_loads_ordered_milestones():
    tl = Timeline.from_graph(_heart_graph())
    orders = [m.order for m in tl.ordered()]
    assert orders == [4, 5, 6, 7, 8]


def test_m6_carries_the_clock_and_window():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)
    assert m6.clock_start is True
    assert m6.window_limit_minutes == 240


def test_m4_requires_organ_and_abo():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    assert set(m4.requires) == {TX.organ, TX.aboGroup}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_timeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.timeline'`.

- [ ] **Step 3: Implement the loader**

Create `src/iladub/timeline.py`:
```python
"""Generic timeline engine: drive a time-critical supply chain from a declarative
TimelineContract (a hol:Process of hol:Milestones). Domain-agnostic — it knows
nothing about organs, only about order, required context, and clocks."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .allen import Interval, feasible, relation

HOL = Namespace("https://w3id.org/etkl/hol#")
ETKL = Namespace("https://w3id.org/etkl#")


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
    for ctx in g.objects(milestone, HOL.requiresContext):
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
        process = g.value(predicate=RDF.type, object=HOL.Process)
        milestones: list[Milestone] = []
        for m in g.objects(process, HOL.hasMilestone):
            order = g.value(m, HOL.order)
            limit = g.value(m, HOL.windowLimitMinutes)
            milestones.append(Milestone(
                id=m,
                order=int(order) if order is not None else 0,
                requires=_required_properties(g, m),
                clock_start=_flag(g, m, HOL.clockStart),
                clock_stop=_flag(g, m, HOL.clockStop),
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
```

Note: clock flags use the `_flag` helper (not bare `bool(g.value(...))`). An rdflib `Literal`
subclasses `str`, so `bool(Literal("false"))` would be `True` (non-empty string) — `.toPython()`
returns the real `xsd:boolean`. Absent property → `None` → `False`.

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_timeline.py -v && python -m pytest -q`
Expected: the three new tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/timeline.py tests/test_timeline.py
git commit -m "feat(sp2): Timeline loader with ordered milestones + clock/context parsing"
```

---

### Task 5: Readiness check

**Files:**
- Modify: `src/iladub/timeline.py`
- Test: add to `tests/test_timeline.py`

- [ ] **Step 1: Add the failing readiness test**

Append to `tests/test_timeline.py`:
```python
from iladub.timeline import readiness


def _context(*present_props):
    g = Graph()
    for p in present_props:
        g.add((TX["offer"], p, __import__("rdflib").Literal("x")))
    return g


def test_readiness_reports_missing_required_property():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    r = readiness(m4, _context(TX.organ), TX["offer"])   # abo missing
    assert TX.aboGroup in r.missing
    assert r.ready is False


def test_readiness_true_when_all_present():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    r = readiness(m4, _context(TX.organ, TX.aboGroup), TX["offer"])
    assert r.ready is True
    assert r.missing == ()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_timeline.py -k readiness -v`
Expected: FAIL with `ImportError: cannot import name 'readiness'`.

- [ ] **Step 3: Implement `Readiness` + `readiness`**

Append to `src/iladub/timeline.py`:
```python
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
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest tests/test_timeline.py -k readiness -v`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/timeline.py tests/test_timeline.py
git commit -m "feat(sp2): milestone readiness over a context graph"
```

---

### Task 6: Cursor + forward-pass capture plan

**Files:**
- Modify: `src/iladub/timeline.py`
- Test: add to `tests/test_timeline.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_timeline.py`:
```python
from iladub.timeline import Cursor, next_capture_plan


def test_cursor_advances_when_current_ready():
    tl = Timeline.from_graph(_heart_graph())
    cur = Cursor(tl)                       # starts at M4
    assert cur.current.order == 4
    moved = cur.advance(_context(TX.organ, TX.aboGroup), TX["offer"])
    assert moved is True
    assert cur.current.order == 5


def test_cursor_blocks_when_current_not_ready():
    tl = Timeline.from_graph(_heart_graph())
    cur = Cursor(tl)
    moved = cur.advance(_context(TX.organ), TX["offer"])   # abo missing
    assert moved is False
    assert cur.current.order == 4


def test_forward_pass_lists_next_milestone_needs():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    # context has M4's needs but not M5's recipientReady
    plan = next_capture_plan(tl, m4, _context(TX.organ, TX.aboGroup), TX["offer"])
    assert plan.milestone_id == next(m.id for m in tl.ordered() if m.order == 5)
    assert TX.recipientReady in plan.needed
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_timeline.py -k "cursor or forward" -v`
Expected: FAIL with `ImportError: cannot import name 'Cursor'`.

- [ ] **Step 3: Implement `Cursor`, `CapturePlan`, `next_capture_plan`**

Append to `src/iladub/timeline.py`:
```python
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
```

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_timeline.py -v && python -m pytest -q`
Expected: cursor + forward-pass tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/timeline.py tests/test_timeline.py
git commit -m "feat(sp2): cursor advance + forward-pass capture plan (anticipation)"
```

---

### Task 7: Clock feasibility wiring

**Files:**
- Modify: `src/iladub/timeline.py`
- Test: add to `tests/test_timeline.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_timeline.py`:
```python
from iladub.allen import Interval
from iladub.timeline import feasibility


def test_feasibility_for_clock_milestone_heart():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)   # windowLimit 240
    f = feasibility(m6, cross_clamp_minute=0, transport=Interval(0, 95))
    assert f.feasible is True
    assert f.slack_minutes == 145
    assert f.relation in {"starts", "during", "overlaps", "finishes", "equals"}


def test_feasibility_infeasible_when_window_exceeded():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)
    f = feasibility(m6, cross_clamp_minute=0, transport=Interval(0, 270))
    assert f.feasible is False
    assert f.slack_minutes == -30
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_timeline.py -k feasibility -v`
Expected: FAIL with `ImportError: cannot import name 'feasibility'`.

- [ ] **Step 3: Implement `Feasibility` + `feasibility`**

Append to `src/iladub/timeline.py`:
```python
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
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest tests/test_timeline.py -k feasibility -v`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/timeline.py tests/test_timeline.py
git commit -m "feat(sp2): clock feasibility wiring (Allen window vs transport)"
```

---

### Task 8: Kidney instance + the one-engine-two-chains proof

**Files:**
- Create: `examples/transplant/kidney-timeline.ttl`
- Test: add to `tests/test_timeline.py`

- [ ] **Step 1: Write the kidney timeline (a genuinely different milestone set + clock)**

Create `examples/transplant/kidney-timeline.ttl`:
```turtle
@prefix tx:   <https://example.org/transplant#> .
@prefix hol:  <https://w3id.org/etkl/hol#> .
@prefix etkl: <https://w3id.org/etkl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Kidneys tolerate long cold ischemia; the chain differs from heart: fewer,
# less time-frantic milestones, and machine perfusion replaces a cross-clamp race.
tx:kidney-process a hol:Process ;
    rdfs:label "Kidney transplant chain"@en ;
    hol:hasMilestone tx:k1 , tx:k2 , tx:k3 , tx:k4 .

tx:k1 a hol:Milestone ; rdfs:label "Accept"@en ; hol:order 1 ;
    hol:requiresContext tx:kctx-1 .
tx:k2 a hol:Milestone ; rdfs:label "Recovery (cold-store start)"@en ; hol:order 2 ;
    hol:clockStart true ; hol:windowLimitMinutes 1800 .
tx:k3 a hol:Milestone ; rdfs:label "Machine perfusion + transport"@en ; hol:order 3 ;
    hol:requiresContext tx:kctx-3 .
tx:k4 a hol:Milestone ; rdfs:label "Implant (reperfusion)"@en ; hol:order 4 ;
    hol:clockStop true .

tx:kctx-1 a etkl:SemanticDataContract ; etkl:hasField tx:tf-abo .
tx:kctx-3 a etkl:SemanticDataContract ; etkl:hasField tx:tf-transport .

tx:tf-abo       a etkl:Field ; etkl:fillsProperty tx:aboGroup .
tx:tf-transport a etkl:Field ; etkl:fillsProperty tx:projectedTransportMinutes .
```

- [ ] **Step 2: Write the two-instance test (same engine, two chains)**

Append to `tests/test_timeline.py`:
```python
def _kidney_graph():
    return Graph().parse(os.path.join(TXD, "kidney-timeline.ttl"), format="turtle")


def test_same_engine_drives_two_distinct_chains():
    heart = Timeline.from_graph(_heart_graph())
    kidney = Timeline.from_graph(_kidney_graph())
    # Different milestone counts and orders — the engine handles both.
    assert [m.order for m in heart.ordered()] == [4, 5, 6, 7, 8]
    assert [m.order for m in kidney.ordered()] == [1, 2, 3, 4]
    # Different clocks, same feasibility code.
    heart_clock = next(m for m in heart.ordered() if m.window_limit_minutes)
    kidney_clock = next(m for m in kidney.ordered() if m.window_limit_minutes)
    assert heart_clock.window_limit_minutes == 240
    assert kidney_clock.window_limit_minutes == 1800
    # A 600-min kidney transport is feasible; the same transport would blow the heart window.
    assert feasibility(kidney_clock, 0, Interval(0, 600)).feasible is True
    assert feasibility(heart_clock, 0, Interval(0, 600)).feasible is False
```

- [ ] **Step 3: Run the test + full suite**

Run: `python -m pytest tests/test_timeline.py -k "two_distinct" -v && python -m pytest -q`
Expected: PASS; full suite green.

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/kidney-timeline.ttl tests/test_timeline.py
git commit -m "feat(sp2): kidney chain + one-engine-two-clocks proof"
```

---

### Task 9: Upgrade the decision holon to the real `hol` vocabulary

**Files:**
- Modify: `src/iladub/decision.py`
- Modify: `tests/test_decision.py`

- [ ] **Step 1: Add the failing conformance + structure tests**

Append to `tests/test_decision.py`:
```python
import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_decision_holon_has_two_options_and_one_chosen():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx))
    options = list(g.subjects(RDF.type, HOL.Option))
    chosen = list(g.objects(None, HOL.chosen))
    assert len(options) == 2
    assert len(chosen) == 1
    assert chosen[0] in options


def test_decision_holon_conforms_to_hol_shapes():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx))
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    result = validate(g, shapes, knowledge)
    assert result.conforms, result.report_text
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_decision.py -k "two_options or conforms" -v`
Expected: FAIL (current `build_decision_holon` emits no `hol:Option`/`hol:chosen`/`hol:decidedBy`, so both new tests fail).

- [ ] **Step 3: Rewrite `build_decision_holon`**

In `src/iladub/decision.py`, replace the existing `build_decision_holon` function with:
```python
def build_decision_holon(result: DecisionResult,
                         subject: URIRef = TX["m4-decision"],
                         process: URIRef | None = None,
                         agent: URIRef = TX["surgeon-1"],
                         evidence: tuple[URIRef, ...] = ()) -> Graph:
    """Emit the decision as a hol:DecisionHolon that conforms to hol:DecisionHolonShape:
    a deliberated option space (accept + decline), exactly one chosen option, an
    accountable agent, the rejected option's reason, and (optionally) its place in a
    process holarchy."""
    g = Graph()
    accept, decline = TX["opt-accept"], TX["opt-decline"]
    g.add((subject, RDF.type, HOL.DecisionHolon))
    g.add((accept, RDF.type, HOL.Option))
    g.add((decline, RDF.type, HOL.Option))
    g.add((subject, HOL.optionSpace, accept))
    g.add((subject, HOL.optionSpace, decline))

    chosen = accept if result.recommendation == "accept" else decline
    rejected = decline if result.recommendation == "accept" else accept
    g.add((subject, HOL.chosen, chosen))
    g.add((rejected, HOL.rejectedBecause, Literal(result.reason)))
    g.add((subject, HOL.decidedBy, agent))
    g.add((subject, HOL.rationale, Literal(result.reason)))
    for e in evidence:
        g.add((subject, HOL.consideredEvidence, e))
    if process is not None:
        g.add((subject, HOL.partOf, process))
    return g
```

- [ ] **Step 4: Run the decision tests + full suite**

Run: `python -m pytest tests/test_decision.py -v && python -m pytest -q`
Expected: all decision tests PASS (including the pre-existing `test_decision_holon_is_a_hol_decision_holon`, which still finds exactly one `hol:DecisionHolon`); full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/decision.py tests/test_decision.py
git commit -m "feat(sp2): upgrade decision holon to conform to hol:DecisionHolonShape"
```

---

### Task 10: Timeline SHACL conformant + negative

**Files:**
- Create: `examples/transplant/heart-timeline-conformant.ttl`, `examples/transplant/heart-timeline-leak.ttl`
- Test: `tests/test_timeline_shacl.py`

- [ ] **Step 1: Write the conformant and leak graphs**

Create `examples/transplant/heart-timeline-conformant.ttl`:
```turtle
@prefix tx:  <https://example.org/transplant#> .
@prefix hol: <https://w3id.org/etkl/hol#> .
tx:cm a hol:Milestone ; hol:order 6 ; hol:windowLimitMinutes 240 .
```

Create `examples/transplant/heart-timeline-leak.ttl` (missing the required `hol:order`):
```turtle
@prefix tx:  <https://example.org/transplant#> .
@prefix hol: <https://w3id.org/etkl/hol#> .
tx:cm a hol:Milestone ; hol:windowLimitMinutes 240 .
```

- [ ] **Step 2: Write the test**

Create `tests/test_timeline_shacl.py`:
```python
import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


def _shapes_knowledge():
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    return shapes, knowledge


def test_conformant_milestone_passes():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "heart-timeline-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_milestone_without_order_fails():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "heart-timeline-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
```

- [ ] **Step 3: Run the test + full suite**

Run: `python -m pytest tests/test_timeline_shacl.py -v && python -m pytest -q`
Expected: both PASS; full suite green.

Note: `hol:MilestoneShape` only constrains `hol:Milestone` targets, so this does not affect the existing `DecisionHolonShape` tests.

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/heart-timeline-conformant.ttl examples/transplant/heart-timeline-leak.ttl tests/test_timeline_shacl.py
git commit -m "test(sp2): SHACL conformant + negative for the milestone shape"
```

---

### Task 11: Documentation

**Files:**
- Modify: `docs/use-case-transplant-m4.md`

- [ ] **Step 1: Append the SP2 section**

Append to `docs/use-case-transplant-m4.md`:
```markdown

## The timeline around the decision (SP2)

M4 is one milestone in a known supply chain. The **timeline engine** (`iladub.timeline`)
drives that chain from a declarative `hol:Process` of `hol:Milestone`s: it tracks where we
are (a cursor), checks whether each milestone's required context is **ready**, runs the
**forward pass** (what the *next* milestone needs that isn't captured yet — anti-crisis
anticipation), and computes **clock feasibility** via Allen's interval algebra
(`iladub.allen`) — does transport finish before the cold-ischemia window closes?

The engine is domain-agnostic: the same code drives `heart-timeline.ttl` (≈240-min window)
and `kidney-timeline.ttl` (≈1800-min window) — distinct supply chains within one domain.
Swap the TimelineContract, get a new chain; no engine change.

> Deterministic — no LLM. Event-driven reopening (`hol:revisitIf`) and live wiring of the
> forward pass to the extraction funnel are the next slice (SP3).
```

- [ ] **Step 2: Verify it renders as valid markdown (no broken structure)**

Run: `python -c "p='docs/use-case-transplant-m4.md'; t=open(p).read(); assert 'timeline engine' in t and t.count('##') >= 2; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 3: Commit**

```bash
git add docs/use-case-transplant-m4.md
git commit -m "docs(sp2): timeline engine section in the transplant use case"
```

---

## Coverage map (plan ↔ spec)
- Spec §4 (vocabulary) → Task 1. §6 (Allen) → Task 2. §5 (engine: loader/readiness/forward-pass/feasibility) → Tasks 4–7. §8 (two instances) → Tasks 3, 8. §7 (decision upgrade) → Task 9. §9 (testing) → every task's tests + Task 10 (SHACL). §10 (files) → all tasks.
- Spec §3 out-of-scope (event processing, live forward-pass wiring, maritime) → not built; `hol:revisitIf` remains declared-only (documented in Task 11).

## Notes on `hol:order`-based ordering
The loader sorts by `hol:order` (spec §11 open item resolved in favour of the integer order, not a `hol:precedes` chain). If a partial order is needed later, `Timeline.from_graph` is the single place to change.
