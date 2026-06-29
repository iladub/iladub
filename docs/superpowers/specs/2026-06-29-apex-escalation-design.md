# Apex escalation — design

**Date:** 2026-06-29
**Status:** approved (brainstorming complete; next step is the implementation plan)
**Branch:** `apex-escalation` (public, transplant-only, domain-neutral)

## Goal

When a milestone decision realizes a severity beyond its declared autonomy scope, it
cannot resolve the matter locally — it must **escalate to a higher-authority decision at
the apex**, which makes the binding call. A SHACL constraint enforces that a matter
exceeding local autonomy can **never** be silently resolved within it.

This realizes the integration-map row *"Event cascade / escalation to the apex — a critical
donor/transport event surfacing to the transplant board apex."* It is the **public,
domain-neutral proxy** for the private maritime analog (a compliance/safety breach surfacing
up the authority holarchy to apex governance); the maritime framing stays unstated.

## Core idea

Escalation is the **vertical (authority-holarchy) analog of `reopen.py`'s temporal lineage**:

| | trigger | lineage edge | result |
| --- | --- | --- | --- |
| `reopen` (SP3a) | an event matches `hol:revisitIf` | `hol:supersedes` (new ⊳ prior) | a superseding decision over **time** |
| `escalate` (this) | realized severity exceeds `hol:withinScope` | `hol:escalatedTo` (local → apex) | a binding decision **up the authority chain** |

It rides the **authority/decision holarchy** (`hol:partOf` / the board), **not** the *place*
holarchy (integration-map gap #3) — the two stay independent, as planned. `evaluate_m4`
already computes `risk_severity`; escalation is a clean vertical layer on top of it and does
**not** modify the M4 evaluator or pipeline (it parallels `reopen.py`, which is also a
standalone capability, not auto-invoked by `compile_offer`).

## What already exists (build on, don't reinvent)

- **`vocab/ontology/risk.ttl`** — constitutional (apex) sensitivities cascade top-down; an
  ordinal `risk:Severity` scale with `risk:order` (`Ok` 0 · `Watch` 1 · `Breach` 2 · `Critical` 3).
  A `risk:Critical` *is* the realization of an apex sensitivity (e.g. absolute contraindication).
- **`vocab/ontology/hol.ttl`** — `hol:DecisionHolon`, `hol:Option`, `hol:partOf` (authority
  holarchy), `hol:Scope` + `hol:withinScope` (autonomy bounds — declared but currently unused
  in code), `hol:constrainedBy`, and the SP3a event/lineage vocab (`hol:Event`, `hol:condition`,
  `hol:supersedes`, `hol:triggeredBy`).
- **`src/iladub/reopen.py` + `events.py`** — the precedent pattern (decision lineage with
  `supersedes`/`triggeredBy`; an `Event` carrying a named condition key).
- **`src/iladub/decision.py`** — `evaluate_m4` already returns `risk_severity ∈
  {"ok","breach","critical"}`; `build_decision_holon` already emits `hol:constrainedBy
  risk:Severity` for breach/critical.
- **examples** — `transplant-risk.ttl` and `transplant-governance.ttl` already define the
  `tx:board` apex context and `tx:role-board` agent.

## Components

### 1. Vocabulary — `vocab/ontology/hol.ttl`

Two additions, kept **risk-agnostic** (hol and risk are siblings under etkl; neither imports
the other — the ordinal bridge lives only in the escalation shape and examples):

- `hol:escalatedTo` — `owl:ObjectProperty`, domain `hol:DecisionHolon`, range
  `hol:DecisionHolon`. *"Escalated this matter to a higher-authority decision because it
  exceeded this decision's autonomy scope (authority-holarchy lineage; the vertical analog of
  `hol:supersedes`)."*
- `hol:maxSeverity` — `owl:ObjectProperty`, domain `hol:Scope`. *"The highest severity the
  scope's holder may resolve within its own autonomy; a realized severity above it must be
  escalated."* Range deliberately left open (an ordinal severity resource); in practice a
  `risk:Severity`. The comment names `risk:Severity` as the typical filler without coupling
  the ontology.

### 2. Enforcement — `vocab/shapes/escalation-shapes.ttl` (new; one concern per file)

`esc:EscalationShape` — a SPARQL constraint (`advanced=True`, as `validate()` already uses).
Targets `hol:DecisionHolon`. For a decision `D` with `hol:constrainedBy` a severity `S` and
`hol:withinScope` a scope whose `hol:maxSeverity` is `M`:

> **if `S.order > M.order` then `D` MUST have `hol:escalatedTo` some `hol:DecisionHolon`.**

The ordinals (`risk:order`) are read from `risk.ttl` in the knowledge graph at validation time
— the shape bridges hol + risk without either ontology importing the other. The apex decision
itself is exempt: its own scope ceiling covers the severity (`S.order <= M.order`), so the
constraint does not fire on it.

### 3. Capability — `src/iladub/escalate.py` (new; parallels `reopen.py`)

Standalone vertical layer. `evaluate_m4` and the M4 pipeline are **unchanged**.

```python
HOL  = Namespace("https://w3id.org/etkl/hol#")
RISK = Namespace("https://w3id.org/etkl/risk#")
TX   = Namespace("https://example.org/transplant#")

# Mirrors risk:order in risk.ttl (kept in sync by the escalation SHACL test).
_SEVERITY_ORDER = {"ok": 0, "watch": 1, "breach": 2, "critical": 3}

def requires_escalation(realized: str, scope_ceiling: str) -> bool:
    """True when a realized severity exceeds the autonomy scope's ceiling."""
    return _SEVERITY_ORDER[realized] > _SEVERITY_ORDER[scope_ceiling]

@dataclass
class EscalationOutcome:
    apex_subject: URIRef
    chosen: URIRef            # the apex option chosen (confirm-decline)
    graph: Graph

def escalate(local_subject, realized_severity, *, new_subject, scope,
             agent=TX["role-board"], event_subject=TX["constitutional-event"],
             condition="absoluteContraindication", override=False) -> EscalationOutcome:
    """Build the binding apex hol:DecisionHolon and wire the authority-holarchy lineage.

    Apex option space = {confirm-decline, override}; chosen = confirm-decline by default
    (override=True selects the override option, with the other rejectedBecause). The apex
    decision is constrainedBy the realized severity, triggeredBy a constitutional hol:Event,
    decidedBy the board agent, withinScope `scope`; local_subject hol:escalatedTo new_subject.
    """
```

`escalate()` constructs the apex decision holon directly (its option space is
`confirm-decline`/`override`, distinct from M4's `accept`/`decline`, so it does **not** reuse
`build_decision_holon`). The apex holon still satisfies `hol:DecisionHolonShape`: ≥2 options,
exactly one `hol:chosen`, `hol:decidedBy`, `hol:rationale`, and `hol:rejectedBecause` on the
rejected option.

### 4. Worked example + negative test — `examples/transplant/`

**`transplant-escalation.ttl` (conformant).** A donor with active malignancy realizes a
constitutional `risk:Critical`. The local M4 decision is `hol:withinScope` a recipient-centre
scope whose `hol:maxSeverity` is `risk:Breach`; `Critical.order (3) > Breach.order (2)`, so it
`hol:escalatedTo tx:board-decision`. The apex `tx:board-decision` has option space
`{confirm-decline, override}`, chosen `confirm-decline`, `hol:decidedBy tx:role-board`,
`hol:constrainedBy risk:Critical`, `hol:withinScope` a board scope (`hol:maxSeverity
risk:Critical`), `hol:triggeredBy tx:constitutional-event`. Conforms to
`escalation-shapes.ttl` + `hol-shapes.ttl`.

**`transplant-escalation-leak.ttl` (must FAIL).** The same Critical-constrained local decision
within the recipient-centre scope, with **no** `hol:escalatedTo` — a constitutional matter
resolved within local autonomy. Must be flagged by `esc:EscalationShape`.

### 5. Tests — `tests/test_escalate.py`

- `requires_escalation` — true when realized > ceiling (critical vs breach), false when within
  (breach vs breach; breach vs critical).
- A guard test asserting `_SEVERITY_ORDER` matches `risk:order` parsed from `risk.ttl` (keeps
  the Python mirror honest).
- `escalate()` emits `hol:escalatedTo`, the apex decision holon, `hol:triggeredBy`, and (with
  `override=True`) flips the chosen option.
- The merged (local + apex) graph conforms to `hol-shapes.ttl` + `escalation-shapes.ttl`.
- SHACL pair (mirrors the existing leak-test style, e.g. `test_event_shacl.py`):
  `transplant-escalation.ttl` conforms; `transplant-escalation-leak.ttl` does **not**.

## Out of scope (explicit)

- The **place** holarchy (nested `holon:PlaceHolon`) — integration-map gap #3, independent.
- Auto-invoking escalation from `compile_offer` / `evaluate_m4` — escalation stays a standalone
  capability like `reopen`, composed by the caller.
- Multi-hop escalation chains (local → region → board) — the model supports it structurally
  (`hol:escalatedTo` is transitive in spirit), but only the single local→apex hop is built and
  tested here.

## Privacy discipline

Transplant-only, framed domain-neutrally. Never name the maritime/ag-trade initiative or
employer. All example data synthetic. (Durable record: integration map on the private
`maritime-voyage-design` branch.)
