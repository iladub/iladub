---
title: Assert / propose / promote — the iladub epistemics
type: concept
sources:
  - vocab/ontology/iladub.ttl
  - vocab/shapes/iladub-shapes.ttl
  - docs/loops/2026-08-10-decision-membrane-baseline.md
  - docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
  - docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md
related: ["[[promotion-decision]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-11
promoted_to: docs/assertion-proposition.md
---

# Assert / propose / promote

iladub's epistemic core is a two-layer commitment: **assert only what can be
grounded in a provided ontology, propose everything else, and never let a
proposition pass as an assertion.** `vocab/ontology/iladub.ttl` names the two
layers directly in its ontology description — the grounded graph (assertions)
and a quarantined proposal graph (propositions) — and states that a proposal
may enter the grounded graph only as the product of a promotion decision.

**How it works.** `vocab/ontology/iladub.ttl` defines `iladub:CandidateConcept`
(⊑ `prov:Entity`) as content iladub could not ground: it carries `surfaceText`
(the literal trigger), a `suggestedAnchor` (e.g. a gist class — a proposition,
never an assertion), `suggestedBy` (the model/rule/person that proposed it),
a `confidence` in [0,1], and `fromRegion` (provenance to the source document
region). Its status is `iladub:proposed`. A `iladub:GroundedNode` is the
admitted counterpart: status `asserted`, bound via `iladub:groundsTo` to a
provided-ontology concept, and — the load-bearing property — `wasPromotedBy`
a `iladub:PromotionDecision`. `vocab/shapes/iladub-shapes.ttl` turns every one
of these into a checkable constraint rather than a convention: `CandidateConceptShape`
requires all five proposal-side properties plus `status = proposed`;
`GroundedNodeShape` requires `wasPromotedBy` with `sh:minCount 1` — the
invariant that *every* grounded node must be produced by a promotion decision;
and `NoLeakShape` is a SPARQL cross-check that a `CandidateConcept` must never
also carry `status = asserted`, catching any attempt to assert a proposition
directly.

This is not a paper commitment — it is measured. `docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md`
documents the discipline on the recovery side: two remaining direct-assert
sites (`assert_record_region`, `assert_transposed_region`) were gated to write
into a scratch graph and escalate `REGION_TILING_FAILED` in-band rather than
crash on a defective region — the same closed-world SHACL membrane pattern
that backs the assert/propose boundary, applied to structural recovery, not
grounding. The grounding side of the same discipline was measured end-to-end
by the loop-K capstone: `docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md`
records a GrainCorp run of 33 records → 460 concepts, **137 grounded** (each
behind exactly one `PromotionDecision` — 137 == 137) and **323 honestly
quarantined**. The quarantine is not failure: unconstrained fields (vessels,
exporters, dates, times) quarantine by design because the contract cannot
verify them, and the grain-commodity scheme correctly *refused* non-grain
cargo (`Woodchip` ×6, `Cement` ×3) rather than grounding it loosely.

**The proposition half was malformed on every real document until 2026-08-10,
and nothing noticed — because nothing was looking.** `iladub-shapes.ttl` was in
no membrane, so `CandidateConceptShape` only ever ran in unit tests against
synthetic graphs. Measured at the start of loop `loop-decision-membrane`
(`docs/loops/2026-08-10-decision-membrane-baseline.md`), over the seven-document
corpus: **every one of the 24 `iladub:CandidateConcept` nodes a compile emitted
was refused by its own shape** — apple 11, bfs 10, who-wfa 3, each refusing
under both closures (apple 11 foci / 44 results, bfs 10 / 40). The other four
documents emitted no candidate at all, which is why the total is 24 and not
larger. Cause: `escalate_region` wrote `dec:confidence` on the region, whose
`rdfs:domain` entailed the region was a `dec:DecisionHolon` (R69).

That is the honest shape of the lesson: **the epistemics were sound in the
vocabulary and broken in the emission**, and the gap survived because the
enforcement claim in the docs named a shape file rather than a call site. Both
halves are now checked where the nodes are made — see [[promotion-decision]]
for the two membranes and their `file:function` sites.

**Settled vs open.** The assert/propose split and its SHACL enforcement are
settled and shipped. What stays open is coverage, not the mechanism: R20
(registered against the loop-K capstone) names that fields without a
verifiable contract constraint will always quarantine — by design, not a
defect — and that richer grounding requires the contract author to declare
more verifiable fields, not a change to the compiler. The r17 spec is
single-sourced for the record/transposed gating detail; no second evidence
doc corroborates the exact timings it reports.
