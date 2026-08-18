---
title: Promotion decision
type: concept
sources:
  - vocab/ontology/iladub.ttl
  - vocab/ontology/dec.ttl
  - vocab/shapes/iladub-shapes.ttl
  - src/iladub/etkl/compile.py
  - src/iladub/feed.py
  - src/iladub/etkl/document.py
  - docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md
  - docs/superpowers/specs/2026-07-19-knowledge-first-grounding-design.md
  - docs/superpowers/specs/2026-08-17-the-gate-and-the-label-design.md
related: ["[[assert-propose-promote]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-17
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
membrane hard-fails any grounded node lacking `wasPromotedBy`.

**Where that enforcement actually happens** — and this sentence is the lesson,
not a footnote. When the paragraph above was first written it was *false for
every real document*: `iladub-shapes.ttl` was in no membrane, so nothing
checked it outside unit tests against synthetic graphs. It became true on
2026-08-10 (loop `loop-decision-membrane`), at two named call sites:

- `src/iladub/etkl/compile.py`'s `_validate` — the compile membrane, which now
  carries `dec-shapes.ttl` + `iladub-shapes.ttl` beside the tab shapes.
- `src/iladub/feed.py`'s `ground_document(..., validate_shapes=True)` — the
  grounding membrane, and **the one that matters for this claim**: a compiled
  graph has zero `iladub:GroundedNode`, so `GroundedNodeShape` is vacuous there
  no matter what the compile membrane validates. The nodes exist only after
  grounding.

Falsified on real evidence, not fixtures: remove one `iladub:wasPromotedBy`
from cbh-stem's 134 grounded nodes and the membrane flips to non-conforming,
reporting *"INVARIANT: every grounded node must be produced by a promotion
decision."*

**A claim about enforcement that does not name its call site is how this one
survived.** Prefer "enforced at `<file>`'s `<function>`" to "enforced by SHACL."

**And naming the call site is still not enough — ask whether it RUNS** (2026-08-17,
R102). Both bullets above were true and still described a membrane most of the
corpus never reached: `_validate` was called behind a gate asking a question about
*tabular* facts, so a document with no document-level table fact validated no
decision holon at all. Measured across the 7-document corpus: **769 decision holons
minted, 453 ever validated, 316 never** — bfs 113 and ons 203, whose promotion
epistemics were enforced by nothing but a producer-side guard in
`decisionlog.BandRecorder.record`. The `dec` leg is now **unconditional at document
scope** (`document._legs_for_document`), re-measured at 769 minted / 0 never; the
`tab` leg keeps its condition and the page gate is unchanged, so a caller running
`compile_tables` alone still validates no decision holon. Prefer "enforced at
`<file>`'s `<function>`, **which runs on every `<unit>`**" — and say which unit.

The same shape shows up one layer up, in prose: this wiki's own `promoted_to`
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
