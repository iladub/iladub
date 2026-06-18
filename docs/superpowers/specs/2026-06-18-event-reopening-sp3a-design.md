# Design — SP3a: event-driven decision reopening

**Date:** 2026-06-18
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## 1. Why

SP2 gave the timeline its *anticipation* (the forward pass: the next milestone's required
context is readied before the clock forces the decision). SP3a gives it the *contingency*:
when reality perturbs the plan — a transport delay, a biological rejection, a payment default
— the affected decision must **reopen**, be **re-evaluated** with the new context, and
**supersede** the prior decision with full lineage. Nothing is overwritten; the audit trail
is accountable end to end.

This completes the holonic decision story: `hol:revisitIf` ("a condition that, if it becomes
true, should reopen this decision") already exists in the vocabulary precisely for this. SP3a
makes it *operative*.

SP3a is **deterministic** — no LLM. It reuses the decision-holon machinery upgraded in SP2 and
is fully CI-testable.

## 2. Scope

**In scope**
- A small **event vocabulary** added to `hol`: `hol:Event` + `hol:condition`, and decision
  lineage `hol:supersedes` (DecisionHolon → DecisionHolon) and `hol:triggeredBy`
  (DecisionHolon → Event).
- An **`Event`** model (`events.py`): a named `condition` key + a `payload` of new values.
- A **reopen engine** (`reopen.py`, domain-agnostic): read a decision's `hol:revisitIf` keys,
  decide whether an event fires one, and — if so — re-evaluate and emit a new decision holon
  linked by `supersedes`/`triggeredBy`.
- A small change to `decision.py`'s `build_decision_holon` to emit `hol:revisitIf` keys.
- SHACL shape for events + conformant/negative examples.

**Out of scope (named, not assumed)**
- **Rewinding the SP2 cursor / re-running a whole milestone.** SP3a reopens at the *decision*
  level (re-evaluate + lineage); cursor rewind is deferred.
- **The closed-loop forward-pass → BAML funnel wiring** (SP3b).
- **Rich condition languages** (threshold expressions, SHACL-as-condition) — matching is by
  named key (`event.condition` ∈ the decision's `hol:revisitIf` keys).
- Automatic event *sources* (weather feeds, telemetry). Events are constructed by the caller.

## 3. The vocabulary (extends `hol`)

Added to `vocab/ontology/hol.ttl` (namespace `https://w3id.org/etkl/hol#`):

- `hol:Event` (rdfs:subClassOf `prov:Entity`) — a perturbation that may reopen a decision.
- `hol:condition` (DatatypeProperty, domain `hol:Event`, range `rdfs:Literal`) — the named
  trigger key the event carries (e.g. `"ischemiaExceeded"`).
- `hol:supersedes` (ObjectProperty, domain `hol:DecisionHolon`, range `hol:DecisionHolon`) —
  the re-evaluated decision supersedes the prior one (decision lineage).
- `hol:triggeredBy` (ObjectProperty, domain `hol:DecisionHolon`, range `hol:Event`) — the
  event that caused the reopening.
- `hol:revisitIf` (already in `hol`, literal) — the named trigger keys a decision declares.

`vocab/shapes/hol-shapes.ttl` gains `hol:EventShape` (an `hol:Event` must declare exactly one
`hol:condition`). The superseding decision is built via `build_decision_holon`, so it conforms
to the existing `hol:DecisionHolonShape` by construction.

## 4. The event model (`src/iladub/events.py`, deterministic)

```python
@dataclass(frozen=True)
class Event:
    condition: str          # the named revisitIf key this event may fire
    payload: dict           # new values folded into re-evaluation, e.g. {"projected_ischemia_minutes": 270}

    def to_rdf(self, subject: URIRef) -> Graph:
        # emits (subject a hol:Event) and (subject hol:condition <condition>)
        ...
```

The `payload` is intentionally generic (a dict) so the engine stays domain-agnostic; the
caller's `re_evaluate` interprets it.

## 5. The reopen engine (`src/iladub/reopen.py`, domain-agnostic)

- `revisit_conditions(decision_graph: Graph, subject: URIRef) -> set[str]` — the decision's
  declared `hol:revisitIf` keys.
- `should_reopen(decision_graph: Graph, subject: URIRef, event: Event) -> bool` —
  `event.condition` ∈ `revisit_conditions(...)`.
- `reopen(prior_subject, event, re_evaluate, *, new_subject, agent, event_subject) -> ReopenOutcome`
  where `re_evaluate: Callable[[Event], DecisionResult]` is supplied by the caller (it folds
  the event payload into a fresh decision input and returns a new `DecisionResult`). The engine:
  1. calls `re_evaluate(event)` → `new_result`;
  2. builds a new `hol:DecisionHolon` for `new_result` via `build_decision_holon(new_result,
     subject=new_subject, agent=agent)`;
  3. adds `(new_subject, hol:supersedes, prior_subject)` and `(new_subject, hol:triggeredBy,
     event_subject)`, and merges `event.to_rdf(event_subject)`;
  4. returns `ReopenOutcome(new_result, graph)` — the new result + the lineage graph.

`ReopenOutcome` is a dataclass `(result: DecisionResult, graph: Graph)`. The prior decision is
never modified or removed.

## 6. Decision wiring (small change to `decision.py`)

`build_decision_holon` gains an optional parameter:
```python
def build_decision_holon(result, subject=TX["m4-decision"], process=None,
                         agent=TX["surgeon-1"], evidence=(), revisit_if=()): ...
```
For each key in `revisit_if`, it emits `(subject, hol:revisitIf, Literal(key))`. All other
behaviour (the SP2 upgrade: options, chosen, decidedBy, withinProcess) is unchanged.

## 7. The money-shot scenario (test)

A *perturbed* transplant, end to end and deterministic:
1. M4 **accepts** (projected ischemia 95 min ≤ 240); the decision declares
   `revisit_if=("ischemiaExceeded",)`.
2. A transport-delay event arrives: `Event("ischemiaExceeded", {"projected_ischemia_minutes":
   270})`.
3. `should_reopen` → `True`; `reopen` re-runs `evaluate_m4` with the updated minutes → the new
   decision **declines** ("projected ischemia 270 min > limit 240 min").
4. Asserts: `new_result.recommendation == "decline"`; the lineage graph contains
   `(new hol:supersedes old)` and `(new hol:triggeredBy event)`; **both** decision holons are
   present (audit trail); the new holon **conforms to `hol:DecisionHolonShape`**.
5. A non-matching event `Event("weatherAlert", {})` → `should_reopen` is `False`, no reopening.

## 8. Testing (deterministic, CI-safe)

- `events`: `Event.to_rdf` emits `hol:Event` + `hol:condition`.
- `reopen`: `should_reopen` matches on a declared key and rejects an undeclared one;
  `reopen` produces a declining new decision with `supersedes` + `triggeredBy`; the new holon
  conforms to `hol:DecisionHolonShape`; the prior decision is still present.
- `decision`: `build_decision_holon(..., revisit_if=("ischemiaExceeded",))` emits the
  `hol:revisitIf` literal; all SP1/SP2 decision tests stay green.
- vocab: `hol:Event`/`hol:condition`/`hol:supersedes`/`hol:triggeredBy` defined; shapes parse.
- SHACL: an event with a `hol:condition` conforms to `hol:EventShape`; one without fails.

## 9. Files

**Vocabulary (domain-neutral, `vocab/`)**
- Modify `vocab/ontology/hol.ttl` — add `Event`, `condition`, `supersedes`, `triggeredBy`.
- Modify `vocab/shapes/hol-shapes.ttl` — add `EventShape`.

**Engine (`src/iladub/`)**
- Create `events.py` — the `Event` model.
- Create `reopen.py` — `revisit_conditions`, `should_reopen`, `reopen`, `ReopenOutcome`.
- Modify `decision.py` — `build_decision_holon` emits `hol:revisitIf` keys.

**Examples + tests**
- `examples/transplant/event-conformant.ttl`, `examples/transplant/event-leak.ttl`.
- `tests/test_events.py`, `tests/test_reopen.py`, `tests/test_event_shacl.py`, and an update to
  `tests/test_decision.py` for the `revisit_if` emission.

## 10. Open items to resolve during planning (not blockers)
- Confirm whether `hol:Event` should be `rdfs:subClassOf prov:Entity` (proposed) or stand-alone
  — the existing `hol` reuses `prov` for provenance, so `prov:Entity` is the consistent choice.
- Confirm the `re_evaluate` callable signature is ergonomic for the transplant case (a closure
  capturing the original `M4Context` and overriding from the event payload).
