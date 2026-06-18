# SP3a — Event-Driven Decision Reopening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let an event (matched by named key against a decision's `hol:revisitIf`) reopen that decision — re-evaluate it with the event payload and emit a new `hol:DecisionHolon` that `hol:supersedes` the prior one and is `hol:triggeredBy` the event, with the prior decision preserved as an audit trail.

**Architecture:** Deterministic (no LLM). A small `hol` vocabulary extension adds `Event`/`condition` and the lineage predicates `supersedes`/`triggeredBy`. A domain-agnostic reopen engine reads a decision's declared `hol:revisitIf` keys, tests an event against them, and — on a match — calls a caller-supplied `re_evaluate` callable and builds the superseding decision via the SP2 `build_decision_holon`. Reuses and lightly extends `decision.py`.

**Tech Stack:** Python ≥3.11, rdflib, pyshacl (all existing). No LLM. Fully CI-testable.

**Spec:** `docs/superpowers/specs/2026-06-18-event-reopening-sp3a-design.md`

---

## File structure & interfaces

| File | Responsibility |
|---|---|
| `vocab/ontology/hol.ttl` (modify) | Add `hol:Event`, `hol:condition`, `hol:supersedes`, `hol:triggeredBy`. |
| `vocab/shapes/hol-shapes.ttl` (modify) | Add `hol:EventShape` (an Event needs exactly one `hol:condition`). |
| `src/iladub/events.py` (create) | `Event` dataclass + `to_rdf`. |
| `src/iladub/reopen.py` (create) | `revisit_conditions`, `should_reopen`, `reopen`, `ReopenOutcome`. |
| `src/iladub/decision.py` (modify) | `build_decision_holon` gains `revisit_if=()` emitting `hol:revisitIf`. |
| `examples/transplant/event-conformant.ttl` / `event-leak.ttl` (create) | Pass/fail `EventShape`. |
| `tests/test_events.py`, `tests/test_reopen.py`, `tests/test_event_shacl.py` (create); `tests/test_decision.py` (modify) | Tests. |
| `docs/use-case-transplant-m4.md` (modify) | SP3a section. |

**Shared interfaces:**
```python
# events.py
@dataclass(frozen=True)
class Event:
    condition: str
    payload: dict
    def to_rdf(self, subject: URIRef) -> Graph: ...

# reopen.py
def revisit_conditions(decision_graph: Graph, subject: URIRef) -> set[str]: ...
def should_reopen(decision_graph: Graph, subject: URIRef, event: Event) -> bool: ...
@dataclass
class ReopenOutcome:
    result: DecisionResult
    graph: Graph                       # the lineage DELTA: new holon + event + supersedes/triggeredBy
def reopen(prior_subject: URIRef, event: Event,
           re_evaluate: Callable[[Event], DecisionResult], *,
           new_subject: URIRef, agent: URIRef = TX["surgeon-1"],
           event_subject: URIRef = TX["event-1"]) -> ReopenOutcome: ...
```

**Namespaces:**
```python
HOL = Namespace("https://w3id.org/etkl/hol#")
TX  = Namespace("https://example.org/transplant#")
```

## Notes for the implementer
- Repo root `/Volumes/WD Green/dev/git/iladub`, branch `event-reopening-sp3a` (already created). Commit per task. Venv `/Volumes/WD Green/dev/git/iladub/.venv/bin/python`; run `python -m pytest`.
- **`hol:supersedes`/`hol:triggeredBy` have ranges `DecisionHolon`/`Event`.** Validation runs with rdfs inference, so a referenced-but-undefined object gets typed by its predicate's range. The reopen `graph` is a *delta* (it does NOT re-include the prior decision's triples). Therefore the conformance test validates the **merged** graph (`prior_graph + outcome.graph`), where the prior decision is fully built and conforms. Do not validate the delta alone — the prior subject would be an under-specified inferred `DecisionHolon` and fail.
- Deterministic — no LLM, no network. Full suite must stay green.

---

### Task 1: Extend `hol` with event + lineage vocabulary

**Files:**
- Modify: `vocab/ontology/hol.ttl`, `vocab/shapes/hol-shapes.ttl`
- Test: `tests/test_event_vocab.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_event_vocab.py`:
```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def test_hol_defines_event_and_lineage():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    assert (HOL.Event, RDF.type, OWL.Class) in g
    assert (HOL.condition, RDF.type, OWL.DatatypeProperty) in g
    assert (HOL.supersedes, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.triggeredBy, RDF.type, OWL.ObjectProperty) in g


def test_hol_shapes_still_parse():
    Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_event_vocab.py -v`
Expected: `test_hol_defines_event_and_lineage` FAILS.

- [ ] **Step 3: Append to `vocab/ontology/hol.ttl`** (prefixes already declared at top):
```turtle
#################################################################
#  Events & decision lineage (SP3a)
#################################################################

hol:Event a owl:Class ;
    rdfs:subClassOf prov:Entity ;
    rdfs:label "Event"@en ;
    rdfs:comment "A perturbation that may reopen a decision when it matches the decision's hol:revisitIf."@en .

hol:condition a owl:DatatypeProperty ;
    rdfs:label "condition"@en ; rdfs:domain hol:Event ; rdfs:range rdfs:Literal ;
    rdfs:comment "The named trigger key this event carries (matched against a decision's hol:revisitIf)."@en .

hol:supersedes a owl:ObjectProperty ;
    rdfs:label "supersedes"@en ; rdfs:domain hol:DecisionHolon ; rdfs:range hol:DecisionHolon ;
    rdfs:comment "This (re-evaluated) decision supersedes a prior decision — decision lineage."@en .

hol:triggeredBy a owl:ObjectProperty ;
    rdfs:label "triggered by"@en ; rdfs:domain hol:DecisionHolon ; rdfs:range hol:Event ;
    rdfs:comment "The event that caused this decision to be reopened."@en .
```

- [ ] **Step 4: Append to `vocab/shapes/hol-shapes.ttl`:**
```turtle
#################################################################
#  An event must declare exactly one condition (SP3a).
#################################################################

hol:EventShape a sh:NodeShape ;
    sh:targetClass hol:Event ;
    sh:property [ sh:path hol:condition ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "An event must declare exactly one condition." ] .
```

- [ ] **Step 5: Run new + existing vocab/shape tests + full suite**

Run: `python -m pytest tests/test_event_vocab.py tests/test_timeline_vocab.py tests/test_vocab_shapes.py -v && python -m pytest -q`
Expected: new PASS; existing PASS; full suite green.

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/hol.ttl vocab/shapes/hol-shapes.ttl tests/test_event_vocab.py
git commit -m "feat(sp3a): hol event + decision-lineage vocabulary"
```

---

### Task 2: The `Event` model

**Files:**
- Create: `src/iladub/events.py`
- Test: `tests/test_events.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_events.py`:
```python
from rdflib import Namespace, Literal
from rdflib.namespace import RDF
from iladub.events import Event

HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def test_event_holds_condition_and_payload():
    e = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    assert e.condition == "ischemiaExceeded"
    assert e.payload["projected_ischemia_minutes"] == 270


def test_event_to_rdf_emits_typed_node_with_condition():
    e = Event("ischemiaExceeded", {})
    g = e.to_rdf(TX["event-1"])
    assert (TX["event-1"], RDF.type, HOL.Event) in g
    assert (TX["event-1"], HOL.condition, Literal("ischemiaExceeded")) in g
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_events.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.events'`.

- [ ] **Step 3: Implement `src/iladub/events.py`:**
```python
"""Events that may reopen a decision. An Event carries a named condition key
(matched against a decision's hol:revisitIf) and a payload of new values folded
into re-evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

HOL = Namespace("https://w3id.org/etkl/hol#")


@dataclass(frozen=True)
class Event:
    condition: str
    payload: dict = field(default_factory=dict)

    def to_rdf(self, subject: URIRef) -> Graph:
        g = Graph()
        g.add((subject, RDF.type, HOL.Event))
        g.add((subject, HOL.condition, Literal(self.condition)))
        return g
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest tests/test_events.py -v`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/events.py tests/test_events.py
git commit -m "feat(sp3a): Event model with RDF provenance"
```

---

### Task 3: `build_decision_holon` emits `hol:revisitIf` keys

**Files:**
- Modify: `src/iladub/decision.py`
- Modify: `tests/test_decision.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_decision.py`:
```python
def test_decision_holon_emits_revisit_if_keys():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx), revisit_if=("ischemiaExceeded", "donorDeterioration"))
    from rdflib import Literal
    keys = {str(o) for o in g.objects(None, HOL.revisitIf)}
    assert keys == {"ischemiaExceeded", "donorDeterioration"}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_decision.py -k revisit_if -v`
Expected: FAIL (`build_decision_holon` has no `revisit_if` parameter → `TypeError`).

- [ ] **Step 3: Add the `revisit_if` parameter**

In `src/iladub/decision.py`, change the `build_decision_holon` signature to add `revisit_if`:
```python
def build_decision_holon(result: DecisionResult,
                         subject: URIRef = TX["m4-decision"],
                         process: URIRef | None = None,
                         agent: URIRef = TX["surgeon-1"],
                         evidence: tuple[URIRef, ...] = (),
                         revisit_if: tuple[str, ...] = ()) -> Graph:
```
And immediately before the final `return g`, add:
```python
    for key in revisit_if:
        g.add((subject, HOL.revisitIf, Literal(key)))
```

- [ ] **Step 4: Run the decision tests + full suite**

Run: `python -m pytest tests/test_decision.py -v && python -m pytest -q`
Expected: the new test PASSES; all pre-existing decision tests (SP1 + SP2) still PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/decision.py tests/test_decision.py
git commit -m "feat(sp3a): build_decision_holon emits hol:revisitIf keys"
```

---

### Task 4: Reopen matching (`revisit_conditions`, `should_reopen`)

**Files:**
- Create: `src/iladub/reopen.py`
- Test: `tests/test_reopen.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_reopen.py`:
```python
from rdflib import Namespace
from iladub.decision import M4Context, evaluate_m4, build_decision_holon
from iladub.events import Event
from iladub.reopen import revisit_conditions, should_reopen

HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def _prior_decision_graph():
    res = evaluate_m4(M4Context("O", "O", 95, 240))   # accept
    return build_decision_holon(res, subject=TX["m4-decision"],
                                revisit_if=("ischemiaExceeded",))


def test_revisit_conditions_reads_declared_keys():
    g = _prior_decision_graph()
    assert revisit_conditions(g, TX["m4-decision"]) == {"ischemiaExceeded"}


def test_should_reopen_true_on_matching_event():
    g = _prior_decision_graph()
    assert should_reopen(g, TX["m4-decision"], Event("ischemiaExceeded", {})) is True


def test_should_reopen_false_on_unknown_event():
    g = _prior_decision_graph()
    assert should_reopen(g, TX["m4-decision"], Event("weatherAlert", {})) is False
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_reopen.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.reopen'`.

- [ ] **Step 3: Implement the matching part of `src/iladub/reopen.py`:**
```python
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
```

- [ ] **Step 4: Run the test**

Run: `python -m pytest tests/test_reopen.py -v`
Expected: all three PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/reopen.py tests/test_reopen.py
git commit -m "feat(sp3a): revisit-condition reading + should_reopen matching"
```

---

### Task 5: The reopen flow (`reopen`, `ReopenOutcome`) + lineage

**Files:**
- Modify: `src/iladub/reopen.py`
- Modify: `tests/test_reopen.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_reopen.py`:
```python
import os
from rdflib import Graph
from rdflib.namespace import RDF
from iladub.reopen import reopen
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _re_evaluate(event):
    # Fold the event payload into a fresh decision input.
    return evaluate_m4(M4Context("O", "O", event.payload["projected_ischemia_minutes"], 240))


def test_reopen_flips_to_decline_with_lineage():
    event = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    outcome = reopen(TX["m4-decision"], event, _re_evaluate, new_subject=TX["m4-decision-2"])
    assert outcome.result.recommendation == "decline"
    assert (TX["m4-decision-2"], HOL.supersedes, TX["m4-decision"]) in outcome.graph
    assert (TX["m4-decision-2"], HOL.triggeredBy, TX["event-1"]) in outcome.graph
    # the prior decision is preserved when the graphs are combined (audit trail)
    merged = _prior_decision_graph() + outcome.graph
    assert len(set(merged.subjects(RDF.type, HOL.DecisionHolon))) == 2


def test_reopened_lineage_conforms_to_hol_shapes():
    event = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    outcome = reopen(TX["m4-decision"], event, _re_evaluate, new_subject=TX["m4-decision-2"])
    # Validate the MERGED graph: supersedes/triggeredBy have DecisionHolon/Event ranges, so the
    # prior decision must be fully present (not just referenced) to conform under rdfs inference.
    merged = _prior_decision_graph() + outcome.graph
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    result = validate(merged, shapes, knowledge)
    assert result.conforms, result.report_text
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_reopen.py -k "flips or conforms" -v`
Expected: FAIL with `ImportError: cannot import name 'reopen'`.

- [ ] **Step 3: Implement `reopen` + `ReopenOutcome`**

Append to `src/iladub/reopen.py`:
```python
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
    graph.add((new_subject, HOL.supersedes, prior_subject))
    graph.add((new_subject, HOL.triggeredBy, event_subject))
    return ReopenOutcome(new_result, graph)
```

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_reopen.py -v && python -m pytest -q`
Expected: all reopen tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/reopen.py tests/test_reopen.py
git commit -m "feat(sp3a): reopen flow — re-evaluate + supersede with lineage"
```

---

### Task 6: Event SHACL conformant + negative

**Files:**
- Create: `examples/transplant/event-conformant.ttl`, `examples/transplant/event-leak.ttl`
- Test: `tests/test_event_shacl.py`

- [ ] **Step 1: Write the conformant + leak graphs**

Create `examples/transplant/event-conformant.ttl`:
```turtle
@prefix tx:  <https://example.org/transplant#> .
@prefix hol: <https://w3id.org/etkl/hol#> .
tx:ev a hol:Event ; hol:condition "ischemiaExceeded" .
```

Create `examples/transplant/event-leak.ttl` (missing `hol:condition`):
```turtle
@prefix tx:  <https://example.org/transplant#> .
@prefix hol: <https://w3id.org/etkl/hol#> .
tx:ev a hol:Event .
```

- [ ] **Step 2: Write the test**

Create `tests/test_event_shacl.py`:
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


def test_event_with_condition_conforms():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "event-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_event_without_condition_fails():
    shapes, knowledge = _shapes_knowledge()
    data = Graph().parse(os.path.join(TXD, "event-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
```

- [ ] **Step 3: Run the test + full suite**

Run: `python -m pytest tests/test_event_shacl.py -v && python -m pytest -q`
Expected: both PASS; full suite green.

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/event-conformant.ttl examples/transplant/event-leak.ttl tests/test_event_shacl.py
git commit -m "test(sp3a): SHACL conformant + negative for the event shape"
```

---

### Task 7: Documentation

**Files:**
- Modify: `docs/use-case-transplant-m4.md`

- [ ] **Step 1: Append the SP3a section**

Append to `docs/use-case-transplant-m4.md`:
```markdown

## When reality perturbs the plan (SP3a)

The timeline anticipates (SP2); SP3a reacts. An **event** (`iladub.events.Event` — a named
`condition` + payload) is matched against a decision's declared `hol:revisitIf` keys. If it
fires, `iladub.reopen.reopen` **re-evaluates** the decision with the event payload and emits a
new `hol:DecisionHolon` that `hol:supersedes` the prior one and is `hol:triggeredBy` the event.
The prior decision is preserved — an accountable audit trail.

Worked example: M4 *accepts* a heart (projected ischemia 95 min). A transport-delay event
`Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})` reopens the decision, which
now *declines* (270 > 240-min window) — superseding the acceptance, with the triggering event
recorded and both decisions retained.

> Deterministic — no LLM. Reopening is at the decision level; rewinding the timeline cursor and
> wiring the forward pass to the extraction funnel remain the next slice (SP3b).
```

- [ ] **Step 2: Verify markdown**

Run: `python -c "t=open('docs/use-case-transplant-m4.md').read(); assert 'SP3a' in t and 'hol:supersedes' in t; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 3: Commit**

```bash
git add docs/use-case-transplant-m4.md
git commit -m "docs(sp3a): event-driven reopening section in the transplant use case"
```

---

## Coverage map (plan ↔ spec)
- Spec §3 (vocabulary) → Task 1. §4 (Event model) → Task 2. §6 (decision wiring) → Task 3. §5 (reopen engine: matching) → Task 4, (reopen flow) → Task 5. §7 (money-shot scenario) → Task 5 tests. §8 (testing) → every task + Task 6 (SHACL). §9 (files) → all tasks.
- Spec §2 out-of-scope (cursor rewind, closed-loop funnel wiring, rich condition languages, event sources) → not built.

## Note on the merged-graph conformance check
`hol:supersedes`/`hol:triggeredBy` ranges (`DecisionHolon`/`Event`) mean rdfs inference types
their objects. The reopen `graph` is a delta, so its `supersedes` target (the prior decision) is
only fully specified when combined with the prior decision graph. Task 5's conformance test
validates the **merged** graph for this reason — validating the delta alone would fail on the
under-specified prior subject. (`supersedes → DecisionHolon` is semantically correct, so no
vocab change is warranted — unlike SP2's `partOf` fix.)
