# Design — SP2: a generic timeline engine for time-critical supply chains

**Date:** 2026-06-18
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## 1. Why

SP1 (the M4 offer→acceptance compiler) proved that a raw document can be compiled into a
SHACL-validated, decision-ready context. SP2 builds the layer *around* the decision: the
**timeline** — the time-critical supply chain as a known sequence of decision milestones,
each needing a specific context to be **ready before the clock forces the decision**.

The governing principle is **anti-crisis**: the system always knows which segment it is in,
the next milestone, and that milestone's required-context schema — so knowledge capture is
*goal-directed by the next decision* (a forward pass), not reactive.

SP2 is **deterministic** — "logic application on clean concepts." No LLM. It consumes SP1's
grounded graph and is fully CI-testable.

## 2. The iladub thesis applied to time (two layers)

- **Engine (domain-agnostic code):** operates over a declarative timeline definition; knows
  nothing about organs, ABO, or ships.
- **TimelineContract (declarative RDF data):** one per supply chain. The engine + vocabulary
  are method-level (domain-neutral, live in `vocab/`); the instances are domain examples
  (live in `examples/`). Same split as SP1.

**Genericity is demonstrated, not asserted:** this slice ships **two** TimelineContracts that
the *same* engine drives — **heart-DBD** (cold-ischemia ≈ 240 min, milestones M4–M8) and
**kidney** (cold-ischemia ≈ 1800 min, a genuinely different milestone set/clock). Distinct
supply chains *within one domain* (by organ, donor type, geography) are the immediate payoff;
the maritime mirror later becomes "just another TimelineContract."

## 3. Scope

**In scope**
- A **timeline vocabulary**, added to `hol` (a timeline of milestone decisions is `hol`'s
  holarchy remit; extending `hol` avoids a new w3id namespace registration).
- A **generic engine** (`timeline.py`): load a TimelineContract → `Timeline`; a `Cursor`;
  `readiness`; `next_capture_plan` (the forward pass); `feasibility`.
- An **Allen-interval feasibility** module (`allen.py`): intervals as event start/stop pairs;
  `relation(a, b)` → Allen relation; `feasible(window, transport)`.
- **Two TimelineContract instances** (heart, kidney) the same engine drives.
- **Decision upgrade (refinement-in-passing):** rewrite SP1's `build_decision_holon` to use
  the real `hol` decision vocabulary (`Option`, `chosen`, `rejectedBecause`,
  `consideredEvidence`, `decidedBy`, `partOf`).
- SHACL shapes for the timeline vocabulary + conformant/negative examples.

**Out of scope (named, not assumed)**
- **Event-driven reopening engine.** Milestones *declare* `hol:revisitIf` conditions (cheap,
  completes the model), but the engine that processes events to reopen decisions (weather
  delay → reopen M7) is **SP3**.
- **Live forward-pass wiring.** `next_capture_plan` emits a deterministic *capture plan*; it
  does **not** re-invoke the SP1 BAML funnel per milestone. That closed-loop integration is a
  documented seam for SP3.
- Pre-clock milestones M0–M3 and post-clock M9–M10 as full content (the engine can represent
  them; the shipped instances focus on the clock-bearing M4–M8 for heart and the analogous
  set for kidney).
- The maritime mirror.

## 4. The vocabulary (extends `hol`)

Added to `vocab/ontology/hol.ttl` (namespace `https://w3id.org/etkl/hol#`):

- `hol:Process` — a holon whose parts are milestone decisions (the timeline as a whole).
- `hol:Milestone` — a node in the process. Properties:
  - `hol:order` (xsd:integer) — position in the sequence.
  - `hol:requiresContext` → an `etkl:SemanticDataContract` (the required-context schema,
    reusing SP1's contract/field pattern).
  - `hol:decision` → the milestone's `hol:DecisionHolon` template (its option space).
  - `hol:clockStart` / `hol:clockStop` (xsd:boolean flags) — does this milestone start/stop
    the dominant interval?
  - `hol:windowLimitMinutes` (xsd:integer) — the interval limit (e.g. 240 for heart).
- Each milestone's `hol:DecisionHolon` is `hol:partOf` the `hol:Process`.
- `hol:revisitIf` (already in `hol`) — declared on milestone decisions; processed in SP3.

## 5. The engine (`src/iladub/timeline.py`, deterministic)

- `Timeline.from_graph(contract_graph) -> Timeline` — parse a TimelineContract into ordered
  `Milestone`s with their required-context contract refs and clock constraints.
- `class Cursor` — holds the current milestone; `advance(context_graph)` moves to the next
  milestone when the current one's readiness is satisfied.
- `readiness(milestone, context_graph) -> Readiness` — returns the set of required-context
  properties that are **present/grounded** vs **missing**, checking against SP1's grounded
  graph (the asserted graph from `to_rdf`).
- `next_capture_plan(timeline, cursor, context_graph) -> CapturePlan` — **the forward pass**:
  the required-context items of the *next* milestone not yet present (what to capture now).
- `feasibility(milestone, clock) -> Feasibility` — for clock-bound milestones, the Allen
  check (delegates to `allen.py`).

Data shapes (dataclasses): `Milestone(id, order, requires_context, clock_start, clock_stop,
window_limit_minutes)`, `Readiness(present: list, missing: list, ready: bool)`,
`CapturePlan(milestone_id, needed: list)`, `Feasibility(relation: str, feasible: bool,
slack_minutes: int)`.

## 6. Allen feasibility (`src/iladub/allen.py`, deterministic)

- `@dataclass Interval: start: int; end: int` (minutes on a common axis).
- `relation(a: Interval, b: Interval) -> str` — returns one of Allen's thirteen relation
  names (`before`, `meets`, `overlaps`, `during`, `starts`, `finishes`, `equals`, and
  inverses) derived from the start/end pair comparison (the relations *emerge* from the
  endpoints, per the vault's EventBasedModeling/Allen grounding).
- `feasible(window: Interval, transport: Interval) -> bool` — the supply-chain feasibility
  predicate: the organ reaches reperfusion before the cold-ischemia window closes, i.e.
  `transport.end <= window.end`. The window is `Interval(cross_clamp, cross_clamp +
  window_limit_minutes)`; transport is `Interval(dispatch, projected_reperfusion)`.

Heart (limit 240) and kidney (limit ≈ 1800) use the *same* code with different instance data.
A deliberately delayed transport produces an infeasible case for the negative test.

## 7. Decision upgrade (refinement-in-passing)

Rewrite `src/iladub/decision.py`'s `build_decision_holon` to emit the real `hol` structure:
- two `hol:Option` nodes (accept, decline); `hol:chosen` → the recommendation;
  `hol:rejectedBecause` on the rejected option (carrying the reason);
- `hol:consideredEvidence` → the context nodes; `hol:decidedBy` → a synthetic agent;
- `hol:withinProcess` → the `hol:Process` (the timeline; `hol:partOf` stays decision→decision); `hol:rationale` retained.

`evaluate_m4`'s decision *logic* is unchanged; only the emitted graph is enriched. SP1's
existing tests still pass (they assert the `DecisionHolon` type and the `DecisionResult`
dataclass fields, not the specific predicates).

## 8. Two instances (`examples/transplant/`)

- `heart-timeline.ttl` — a `hol:Process` with milestones M4 (accept), M5 (mobilize), M6
  (cross-clamp; `clockStart`, `windowLimitMinutes 240`), M7 (transport), M8 (reperfusion;
  `clockStop`); each with a `requiresContext` contract ref and a decision.
- `kidney-timeline.ttl` — the analogous chain with `windowLimitMinutes 1800` and the
  kidney-appropriate milestone content (demonstrating a genuinely different clock over the
  same engine).
- `heart-timeline-conformant.ttl` / `heart-timeline-leak.ttl` — pass/fail the timeline shapes.
- A synthetic SKOS addition for the organs if needed (kidney term).

## 9. Testing (deterministic, CI-safe)

- `readiness`: a context missing `aboGroup` reports it missing and `ready=False`; a complete
  context reports `ready=True`.
- `next_capture_plan`: at M4, the plan lists M5's not-yet-captured required-context items.
- `allen.relation`: endpoint combinations classify to the correct Allen relation (table test).
- `allen.feasible`: heart transport 95 min within 240 → feasible; a 270-min projected
  reperfusion vs 240 window → infeasible.
- **Two-instance test:** the *same* engine loads heart and kidney TimelineContracts and
  advances each through its milestones; the heart window is 240 and kidney 1800 — same code.
- decision upgrade: `build_decision_holon` emits two `hol:Option`s, a `hol:chosen`, a
  `hol:rejectedBecause`, and `hol:withinProcess` the Process; SP1 decision tests still green.
- SHACL: `heart-timeline-conformant.ttl` conforms to the timeline shapes; `-leak.ttl` fails.

## 10. Files

**Vocabulary (domain-neutral, `vocab/`)**
- Modify `vocab/ontology/hol.ttl` — add `Process`, `Milestone`, and the timeline properties.
- Modify `vocab/shapes/hol-shapes.ttl` — add `ProcessShape`/`MilestoneShape`.

**Engine (`src/iladub/`)**
- Create `timeline.py` — the generic engine.
- Create `allen.py` — interval/Allen feasibility.
- Modify `decision.py` — upgrade `build_decision_holon` to the real `hol` vocabulary.

**Instances + tests**
- `examples/transplant/heart-timeline.ttl`, `kidney-timeline.ttl`,
  `heart-timeline-conformant.ttl`, `heart-timeline-leak.ttl`.
- `tests/test_timeline.py`, `tests/test_allen.py`, `tests/test_timeline_shacl.py`, and an
  update to `tests/test_decision.py` for the upgraded holon.

## 11. Open items to resolve during planning (not blockers)

- Confirm the exact `hol` predicate names against the existing `hol.ttl` style (e.g. whether
  to reuse `hol:produced`/`hol:governedBy` for milestone wiring).
- Confirm `Timeline.from_graph` ordering source (`hol:order` integer vs a `hol:precedes`
  chain) — the spec uses `hol:order`; revisit if a partial order is needed later.
- Decide whether `requiresContext` reuses the SP1 `etkl:Field` tags verbatim or a thinner
  per-milestone projection.
