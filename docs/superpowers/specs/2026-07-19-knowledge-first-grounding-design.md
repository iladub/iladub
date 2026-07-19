# Knowledge-First Grounding — the first sound NEURAL slice (ground-or-propose)

**Date:** 2026-07-19
**Status:** Design — approved (brainstorm 2026-07-19).
**Scope:** the first NEURAL propose→oracle→dispose slice in the **iladub epistemic core** (not the
table-perception layer). Builds the working **ground-or-propose** pipeline over the *already-shipped*
grounding vocab + enforcement SHACL + a real semantic data contract. One vertical slice that closes
end-to-end; wiring the full ET(K)L/M4 extraction feed into it is an explicit follow-up.

## Why here (and not table-span perception)

Scoping the NEURAL layer against the shipped recovery layer found **no ready-oracle span-perception
slice**: merged-header span resolution has no distinguishing oracle (tiling SHACL checks *legality*,
not the specific partition; the centering check already escalates the ambiguous cases), so it repeats
the B1.2 `confidence ≠ validity` trap; the other "failures" are correct escalations or oracle-unsolved
Family-C grid/segmentation. See `docs/superpowers/specs/2026-07-18-neural-span-perception-design.md`
§2.0 for the B1.2 lesson that motivated this diligence.

The **grounding** decision is sound because the disposing oracle genuinely distinguishes right from
wrong: **the contract's SHACL shape rejects an implausible grounding** (a numeric value proposed as a
name, a free-text token proposed as an ABO group, a value outside an `admissibleScheme`). That is the
distinguishing power the perception layer lacked. And it is iladub's *actual differentiator* (the
promotion epistemics, §3/§4), not more table geometry.

## What already ships (this slice consumes, does not re-author)

- **Core vocab** `vocab/ontology/iladub.ttl` — `iladub:CandidateConcept`, `iladub:GroundedNode`,
  `iladub:PromotionDecision ⊑ dec:DecisionHolon`, `iladub:Suggester`, `iladub:SourceRegion`,
  `iladub:Status {proposed, asserted, rejected}`, and the properties (`surfaceText`,
  `suggestedAnchor`, `suggestedBy`, `confidence`, `fromRegion`, `groundsTo`, `wasPromotedBy`,
  `reviews`, `status`).
- **Enforcement SHACL** `vocab/shapes/iladub-shapes.ttl` — `CandidateConceptShape` (a proposition
  must carry surfaceText/suggestedAnchor/suggestedBy/confidence∈[0,1]/fromRegion, status=proposed),
  `GroundedNodeShape` (**the invariant**: every grounded node `wasPromotedBy` ≥1, `groundsTo` ≥1,
  status=asserted), `PromotionDecisionShape` (reviews ≥1, `dec:decidedBy` ≥1), `NoLeakShape` (a
  proposition must never also be asserted).
- **A real semantic data contract** `examples/transplant/offer-contract.ttl` —
  `tx:offer-contract a etkl:SemanticDataContract`, `etkl:targetClass tx:OrganOffer`, eight
  `etkl:Field`s (`etkl:fillsProperty`, optional `etkl:admissibleScheme` for SKOS-bound fields such as
  `tx:f-abo → tx:scheme-abo`), plus `examples/transplant/offer-shapes.ttl`
  (`tx:OrganOfferShape`: `tx:organ` 1..1, `tx:aboGroup` 1..1 xsd:string, `tx:ejectionFraction` 0..1).
- **The proposer seam** `src/iladub/etkl/propose.py` (injected `Proposer` Protocol +
  `FakeProposer`/`BamlProposer`, env-gated `BAML_LIVE`) and **the promotion emitter**
  `src/iladub/etkl/promote.py` (emits an `iladub:PromotionDecision` reviewing an
  `iladub:CandidateConcept` for the A2.1 dimension-name case). This slice **generalizes** both from
  the narrow reshape-name case to general document-concept grounding.

## The slice — ground-or-propose

### The decision (genuinely NEURAL, soundly disposed)

Given a **surface concept** from a source region (a `(text, value, region)` triple, e.g.
`("Ejection Fraction", "55%", region)`) and a `SemanticDataContract`, decide **which contract field
it grounds to, or that it is novel** — and never let an ungrounded concept pass as an assertion.

- **Exact / decidable match** (the surface text matches a field's `rdfs:label`/`fillsProperty` local
  name, or a scheme-bound value matches a SKOS `prefLabel`/`altLabel` in the field's
  `admissibleScheme`) → an assertion candidate. This lookup is **AXIOM/PROCEDURAL**, not NEURAL.
- **No exact match** → the **NEURAL** step: BAML proposes *map-to-field-F* vs *novel*, with a
  suggested upper-ontology anchor (gist), a calibrated confidence, a one-line rationale, and the
  source region carried through.

### The pipeline (extends `promote.py`/`propose.py`)

1. **`GroundingProposer` seam** (new, mirrors `propose.py`): `ProposeGrounding` BAML function +
   `Proposer`-style Protocol with `FakeGroundingProposer` (offline, deterministic) and
   `BamlGroundingProposer` (lazy, `BAML_LIVE`-gated). Returns
   `GroundingProposal{field_iri: str | None, anchor_iri: str, confidence: float, rationale: str}`
   (`field_iri=None` ⇒ proposed novel).
2. **Dispose against the contract (the sound oracle):** for a proposed `map-to-F`, tentatively build
   the grounded node — `tx:OrganOffer` with `F.fillsProperty = value` (+ a `groundsTo` to the SKOS
   term for scheme-bound fields) — and validate it against the **contract SHACL**
   (`offer-shapes.ttl`, `inference="rdfs"`, `advanced=True`) *and* the `admissibleScheme` membership.
   - **Conforms** → eligible: emit a `PromotionDecision` (accountable, `dec:decidedBy` the suggester)
     that admits the `GroundedNode` (status=asserted, `wasPromotedBy` the decision, `groundsTo` F's
     property/term). The concept crosses the membrane **only** via this decision.
   - **Fails the contract shape / scheme, or proposed novel** → **quarantine** as an
     `iladub:CandidateConcept` (status=proposed, carrying surfaceText, suggestedAnchor, suggestedBy,
     confidence, fromRegion). A proposition — **never asserted**.
3. **Confidence is recorded on the proposition, never promotes** (§3/§4; the standing
   `confidence ≠ validity` rule). Promotion is the *contract-shape pass* + the accountable
   `PromotionDecision`, not the confidence number.

### Why the oracle is sound (the crux the perception layer lacked)

The contract SHACL shape of the target field genuinely **distinguishes** a plausible grounding from a
wrong one: `"55%"` proposed as `tx:aboGroup` fails (`aboGroup` is `xsd:string` from `scheme-abo`, and
`"55%"` is not an ABO term); `"A"` proposed as `tx:ejectionFraction` fails a numeric/percent
expectation; a genuinely novel concept has no field to conform to → quarantined. So a **legal-but-wrong**
grounding is *rejected by construction*, not admitted on confidence. This is what makes the slice
sound where merged-header span resolution was not.

## Worked example (domain-neutral, synthetic — reuses the shipped contract)

Input: a small hand-built set of offer surface-concepts (as if from a `SourceRegion`), spanning the
four outcomes:
1. **Exact match** — `("ABO group", "A", r1)` → `tx:aboGroup`, value `"A"` ∈ `scheme-abo` → grounded.
2. **Semantic match (accepted by shape)** — `("EF", "55%", r2)` → BAML proposes `tx:ejectionFraction`
   (no scheme; conforms `OrganOfferShape` 0..1) → grounded via a PromotionDecision.
3. **Wrong mapping (rejected by shape)** — a distractor `("EF", "55%", r3)` where the proposer is
   fed a wrong `field_iri=tx:aboGroup` → contract shape + `scheme-abo` membership reject it →
   quarantined as a `CandidateConcept`, **not** asserted.
4. **Novel** — `("donor smoking pack-years", "20", r4)` → no field → `CandidateConcept` (proposition)
   with a gist anchor.

Output graph validated by **both** `iladub-shapes.ttl` (epistemics) and `offer-shapes.ttl` (contract).

## Definition of done (the loop CLOSES)

- End-to-end: groundable concepts asserted as `GroundedNode`s each `wasPromotedBy` a
  `PromotionDecision`; ungroundable/wrong ones quarantined as `CandidateConcept` propositions; the
  emitted graph **conforms** to `iladub-shapes.ttl` + `offer-shapes.ttl` under pySHACL.
- **Negative tests that MUST fail** (the epistemics are real, not decorative):
  (a) a `GroundedNode` emitted **without** a `PromotionDecision` → `GroundedNodeShape` violation;
  (b) a `CandidateConcept` marked `status=asserted` → `NoLeakShape` violation;
  (c) the wrong-mapping case asserted as grounded → contract-shape (`OrganOfferShape`/scheme) violation.
- **Gate (neurosymbolic §8):** the exact-match lookup and the SHACL/scheme dispose are
  AXIOM/PROCEDURAL (no tuned constant); the only NEURAL step is `ProposeGrounding`, and its output is
  **never asserted without passing the contract oracle** — the disposition is the contract shape, not
  confidence. All tests run offline via `FakeGroundingProposer` (the `propose.py` discipline);
  `BAML_LIVE` gates the live path.
- Residue (novel concepts, rejected mappings) is quarantined in-band as propositions, never dropped
  (§7 credibility over completeness).

## File structure (for the plan)

- **Create** `src/iladub/ground.py` — the ground-or-propose pipeline: contract loading, exact-match
  lookup, proposer invocation, contract-SHACL/scheme disposition, `GroundedNode` / `CandidateConcept`
  / `PromotionDecision` emission (reuses `promote.py`'s emission helpers, generalized).
- **Create** `baml_src/ground_propose.baml` — `ProposeGrounding` (+ `GroundingProposal` class).
- **Extend** `src/iladub/etkl/propose.py` *or* add `src/iladub/propose_ground.py` — the
  `GroundingProposer` Protocol + `FakeGroundingProposer` / `BamlGroundingProposer` (env-gated, lazy).
- **Extend** `src/iladub/etkl/promote.py` — generalize the PromotionDecision emitter beyond the
  dimension-name case (a `promote_grounding(g, candidate, field, decidedBy)` helper), or add it beside.
- **Reuse** `examples/transplant/offer-contract.ttl` + `offer-shapes.ttl` +
  `examples/transplant/transplant-terms.ttl` (the latter already defines `tx:scheme-abo` /
  `tx:scheme-organ` SKOS `ConceptScheme`s with `tx:abo-A "A"`, `tx:abo-O "O"`, … `skos:prefLabel`s —
  the exact-match/scheme lookup targets these; nothing new to author).
- **Create** `tests/test_grounding.py` — the end-to-end conformance proof + the three negative tests.

## Scope boundary (YAGNI)

- The slice takes **structured surface-concepts + the contract** and closes the grounding loop.
  Wiring the ET(K)L table output / M4 BAML extraction (`baml_src/agents.baml`) as the concept *feed*
  is an explicit **follow-up slice** — not this one.
- One contract (`offer-contract`), one target class (`tx:OrganOffer`). Multi-contract routing,
  contract discovery, and SKOS reasoning beyond exact prefLabel/altLabel match are out of scope.
- No new epistemics vocab or shapes — the shipped `iladub.ttl` / `iladub-shapes.ttl` are sufficient;
  if a genuinely missing term surfaces, that is a finding to raise, not to invent silently.
