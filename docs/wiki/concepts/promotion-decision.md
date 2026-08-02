---
title: Promotion decision
type: concept
sources:
  - vocab/ontology/iladub.ttl
  - vocab/ontology/dec.ttl
  - vocab/shapes/iladub-shapes.ttl
  - docs/superpowers/specs/2026-07-19-knowledge-first-grounding-design.md
related: ["[[assert-propose-promote]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-01
promoted_to: docs/assertion-proposition.md
---

# Promotion decision

A promotion decision is the *only* legal door from proposition to assertion:
`vocab/ontology/iladub.ttl` declares `iladub:PromotionDecision ⊑ dec:DecisionHolon`
and describes it as "the accountable act of reviewing a `CandidateConcept` and
accepting / refining / rejecting it" — a decision holon whose evidence is the
candidate and its suggested anchor, whose chosen option is the outcome, and
whose product (if accepted) is the grounded node. The comment names it
explicitly as "the iladub↔dec bridge": the same accountable-decision machinery
that models decisions found *inside* documents also governs iladub's own act
of admitting content into the grounded graph.

**How it works.** Because a `PromotionDecision` is a `dec:DecisionHolon`
(itself ⊑ `prov:Activity`, per `vocab/ontology/dec.ttl`), it inherits
provenance-standard properties rather than reinventing them: `dec:consideredEvidence`
(⊑ `prov:used`) carries the candidate and its anchor, `dec:decidedBy`
(⊑ `prov:wasAssociatedWith`) names the accountable agent, and `dec:produced`
(⊑ `prov:generated`) is the grounded node when the decision accepts. iladub
adds two of its own properties on top: `iladub:reviews` (⊑ `dec:consideredEvidence`)
points the decision at the specific candidate it is disposing of, and
`iladub:wasPromotedBy` (⊑ `prov:wasGeneratedBy`) is the property `vocab/shapes/iladub-shapes.ttl`'s
`GroundedNodeShape` requires with `sh:minCount 1` on every grounded node — the
enforcement point. `PromotionDecisionShape` in the same file adds the
iladub-specific requirement that a promotion decision must `reviews` at least
one candidate and record `dec:decidedBy`; the general decision mechanics
(an option space of at least two, exactly one chosen option, the chosen
option drawn from that space) are validated by `dec`'s own shapes, not
duplicated here — `iladub-shapes.ttl` layers only the parts specific to
promotion.

This makes promotion *stronger* than a bare confidence threshold: CLAUDE.md's
holonic-interaction-model section frames the comparison explicitly — HGA's
grounding lifecycle routes low-confidence content to a `CandidateStatus` but
does not require an accountable decision to leave it, whereas iladub's SHACL
membrane hard-fails any grounded node lacking `wasPromotedBy`. The same
shape shows up one layer up, in prose: this wiki's own `promoted_to`
frontmatter field is the documentation-governance analogue of `iladub:wasPromotedBy`
— a wiki proposition becomes site assertion only when a release records the
promotion, never silently.

**Settled vs open.** The vocabulary-level bridge (`PromotionDecision ⊑ DecisionHolon`,
the required `reviews`/`decidedBy`/`wasPromotedBy` triples) is settled and
SHACL-enforced across both sources. What decision-space content a real
promotion typically deliberates — accept-as-anchor vs. refine-to-domain-concept
vs. reject, as sketched on the promoted site page — is not itself asserted by
either `.ttl` source here; it is an implementation convention this page does
not independently verify.
