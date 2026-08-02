---
title: Grounding portal and the contract membrane
type: concept
sources:
  - vocab/ontology/etkl-holons.ttl
  - vocab/ontology/etkl.ttl
  - docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
related: ["[[assert-propose-promote]]", "[[hga]]"]
confidence: medium
updated: 2026-08-01
promoted_to: docs/holonic-interaction.md
---

# Grounding portal and the contract membrane

`vocab/ontology/etkl-holons.ttl` declares the interaction model directly in
its own description: "A RawDocumentHolon and the SemanticHolons (provided
ontologies / SKOS terminology) interact through a governed GroundingPortal,
producing a CleanDocumentHolon whose interior is the grounded graph and
whose cleanliness IS its membrane health." `etkl:RawDocumentHolon`'s
projection is "the surface concepts / mentions it offers for grounding";
`etkl:SemanticHolon`'s projection is "the concepts available for grounding —
it is the grounding source the portal reconciles against." The
`etkl:GroundingPortal` class comment states the governance point precisely:
"Crossing the portal is governed by `iladub:PromotionDecision`" — assertions
sit inside the `etkl:CleanDocumentHolon`'s interior ("the grounded graph +
the promotion decisions that produced it"); propositions are candidates
still at the portal, not yet crossed. `vocab/ontology/etkl.ttl` supplies the
contract half of the same membrane: `etkl:SemanticDataContract` "declares
the target semantics ... the contract is an ontology, not a JSON/YAML
schema," and `etkl:hasTargetShape` binds it to the SHACL node shape(s) an
output must conform to — the membrane's actual rule-book.

**Shipped vs design-only (confidence: medium, deliberately).** `etkl-holons.ttl`
*ships* the vocabulary: the holon-type hierarchy (`DocumentHolon` →
`RawDocumentHolon`/`SemanticHolon`/`CleanDocumentHolon`/`AlignmentHolon`),
`GroundingPortal`, the `etkl:MembraneHealth` class with its three
individuals (`Intact`/`Weakened`/`Compromised`), and the `etkl:membraneHealth`,
`etkl:throughPortal`, `etkl:reconciles` properties are all declared OWL/RDFS
terms, standalone and reasoner-free per the file's own header. What is
**not** in this file, or in `etkl.ttl`: any computation that assigns a
`MembraneHealth` value from validation results, or a worked example
traversing Raw→Portal→Clean end to end. `docs/holonic-interaction.md` (this
page's promotion target) states both gaps itself under "Planned work (not
done yet)" — a membrane-health check is not built, and the one shipped
example (`examples/holon-grounding-conformant.ttl`) "covers the
grounding-governance crossing only," not a full document traversal. This
page's own three sources corroborate the vocabulary but not that computation.

What *is* shipped and exercised is the general membrane discipline the
portal model describes in the abstract, demonstrated concretely one layer
down: `docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md`
gates the two remaining direct-assert table-region sites to write into a
**scratch graph**, validate against the closed-world SHACL membrane
(`region_tiles`), merge on pass, and **escalate in-band** (`REGION_TILING_FAILED`)
on fail — never crash, never silently admit a broken region. It is a
region-tiling membrane, not the grounding-portal membrane the holon
ontology describes, but it is the same "gate, never crash" shape the
portal/promotion model calls for, already measured end to end (isomorphic
healthy-path graphs, GrainCorp unchanged).

**Settled vs open.** The holon-type and membrane-health *vocabulary* is
settled and shipped. Whether a document actually computes and reports its
`membraneHealth`, and whether a raw→portal→clean traversal exists as more
than a design diagram, remain open per `docs/holonic-interaction.md` — hence
`confidence: medium` rather than `high`.
