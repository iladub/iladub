# dec — the decision-context layer

`dec` represents **decisions as holons**: units that are at once a self-contained,
accountable deliberation *and* a part of a larger decision holarchy. It sits *above* a
data graph (e.g. a FHIR-derived graph) and captures what data models structurally cannot.

Namespace: `https://w3id.org/iladub/dec#`.

## What FHIR (and most data models) cannot capture

- **The deliberation space** — the options considered and *why one was rejected*, not
  just the recorded outcome.
- **Situated meaning** — the frame that makes a fact decision-relevant (the same lab
  value means different things in different decision contexts).
- **A holarchy of authority** — local decision ⊂ protocol ⊂ guideline ⊂ policy.
- **The deontic/commitment layer** — obligations, expectations, validity conditions.
- **Decision lineage** — what evidence supported a decision, and what upstream change
  should reopen it (`dec:revisitIf` / `onChange`).

## Core shape

A `dec:DecisionHolon` (⊑ `prov:Activity`) records: `consideredEvidence`,
`constrainedBy`, an `optionSpace` (≥2 — the no-change option counts), exactly one
`chosen` option (which must be in the option space — SPARQL-enforced), `decidedBy` (an
agent, human or automated), a `rationale`, optional `confidence` ∈ [0,1], `produced`
(the resulting node), `governedBy` (policy), `partOf` (holarchy), `withinScope`
(autonomy scope).

## Why it matters

For agentic AI safety: an agent reasoning inside a holon knows its autonomy scope, the
constraints reframing its options, the option space it must justify against, and how
its decision composes upward. That is the difference between emitting a plausible
output and making an *accountable, re-evaluable* decision.

It is also the most domain-neutral, transferable part of the project — the same holon
models a clinical therapy switch or a trading hedge decision unchanged. That makes it
the original contribution, distinct from the (reusable) terminology/shape bridging.
