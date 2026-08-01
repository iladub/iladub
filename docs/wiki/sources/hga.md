---
title: HGA — Cagle's W3C Holon CG ontology (consumed, never authored)
type: source
sources:
  - vocab/ontology/iladub-hga-align.ttl
  - vocab/ontology/dec-hga-align.ttl
  - vocab/ontology/risk-hga-align.ttl
  - vocab/ontology/tab-hga-align.ttl
  - CLAUDE.md
related: ["[[grounding-membrane]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-01
---

# HGA — Cagle's W3C Holon CG ontology

HGA (`holon:` = `http://w3id.org/holon/`) is the reference ontology of the
**W3C Holon Community Group**, chaired by Kurt Cagle. Every one of iladub's
four `*-hga-align.ttl` modules names it as "OPTIONAL alignment ... ALIGNMENT,
NOT IMPORT" and states the same discipline in near-identical wording: no
`owl:import`, only `rdfs:subClassOf`/`rdfs:subPropertyOf`/`rdfs:seeAlso`
axioms, loaded separately from the standalone reasoner-free core ontologies.
Two modules record the sub-namespace commit their class IRIs were verified
against (`iladub-hga-align.ttl`: `w3c-cg/holon` HEAD `2fcc928`, 2026-06-23;
`dec-hga-align.ttl`: HEAD `8612f5e`, 2026-06-24) — a dated provenance trail
for an external ontology iladub does not control.

**The invariant governing every file here** is stated in `CLAUDE.md` §
Source ownership: HGA terms appear only as objects of a triple, never as
subjects — this page cites that rule rather than restating it.

**Where iladub terms align (read directly from the four modules — nothing
invented):**

- `iladub-hga-align.ttl`: `etkl:DocumentHolon`, `etkl:RawDocumentHolon`,
  `etkl:CleanDocumentHolon`, `etkl:SemanticHolon` → `rdfs:subClassOf holon:DataHolon`;
  `etkl:GroundingPortal` → `rdfs:subClassOf holon:Portal`;
  `etkl:DocumentProjection` → `rdfs:subClassOf hproj:Projection`;
  `iladub:CandidateConcept` and `iladub:GroundedNode` → `rdfs:seeAlso holon:GroundingRecord`
  (at `holon:CandidateStatus` and `holon:RegisteredStatus` respectively, per
  the file's comments — "close, not strict-equivalent, mappings");
  `etkl:hasRole` → `rdfs:seeAlso hview:ViewerProfile`.
- `dec-hga-align.ttl`: `dec:partOf` → `rdfs:subPropertyOf holon:partOf`;
  `dec:Event` → `rdfs:subClassOf hev:HolonEvent`; `dec:ExpansionRequest` and
  `dec:escalatedTo` → `rdfs:seeAlso hmk:PropagationSignal`; `dec:DecisionHolon`
  → `rdfs:seeAlso hbayes:PolicySelection`; `dec:Scope` → `rdfs:seeAlso hpol:BoundaryPolicy`.
  Each `seeAlso` comment states *why* it isn't a subclass: e.g. HGA's
  `hbayes:PolicySelection` is "a belief-driven choice, not an accountable,
  agent-attributed, re-evaluable deliberation."
- `risk-hga-align.ttl`: `risk:RiskContext` → `rdfs:subClassOf holon:Holon`;
  `risk:withinContext` → `rdfs:subPropertyOf holon:partOf`; `risk:RiskAssessment`
  → `rdfs:subClassOf hproj:Projection`.
- `tab-hga-align.ttl`: `tab:NormalizedBase` → `rdfs:subClassOf hproj:Projection`
  (mirroring `risk:RiskAssessment`'s projection alignment — the file's own
  comment draws that parallel).

**What iladub deliberately does NOT build.** `CLAUDE.md`'s "Defer to the CG"
list: core holon vocabulary, portal/boundary machinery, the Markov-blanket /
Friston–Bayesian layer, federation, generic event/projection/camera infra,
and the DataBook format + CLI — all left to the Community Group rather than
reimplemented. iladub's stated differentiators sit instead in document
compilation, promotion epistemics (the `iladub:PromotionDecision` gate the
alignment files repeatedly cite as *stronger* than HGA's bare confidence
gate), the semantic-data-contract-as-ontology, provenance-to-the-page, and
contextual risk — the last named explicitly as "a genuine gap in HGA."

**Settled vs open — and the one thing this page demonstrates about itself.**
The alignment triples enumerated above are shipped, dated, and verified
against a specific upstream commit each. This page is `type: source`, not
`type: concept`: per the promotion-queue derivation
(`vocab/queries/docgov-promotion-queue.rq`), only `docClass "wiki"` pages
with `docType "concept"` and no `promoted_to` enter the queue — a source
page never does, regardless of `promoted_to`, because it is never asserted
content of iladub's own, only a citation trail to what iladub consumes.
