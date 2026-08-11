---
title: Decision holon (dec)
type: concept
sources:
  - vocab/ontology/dec.ttl
  - vocab/shapes/dec-shapes.ttl
  - vocab/shapes/escalation-shapes.ttl
  - docs/superpowers/specs/2026-06-29-apex-escalation-design.md
related: ["[[promotion-decision]]"]
confidence: high
updated: 2026-08-11
promoted_to: docs/dec.md
---

# Decision holon (dec)

A `dec:DecisionHolon` is `vocab/ontology/dec.ttl`'s central class: declared
`⊑ prov:Activity`, and described in the ontology's own metadata as "an
accountable, re-evaluable decision that is simultaneously a whole (a
self-contained deliberation) and a part (a member of a larger decision
holarchy)." The ontology header is explicit about why it exists: it captures
what most data models (its example is FHIR) structurally cannot — the
rejected option and why, situated meaning, a holarchy of authority, a deontic
layer, and decision lineage.

**How it works.** The core deliberation shape is enforced, not just declared —
enforced at `compile._validate` (`src/iladub/etkl/compile.py`) and at
`feed.ground_document`'s gate (`src/iladub/feed.py`), which is where "enforced"
stops being a property of the shape file and starts being a property of the
pipeline. Until 2026-08-10 it *was* just declared: `dec-shapes.ttl` was in no
membrane, and every promotion decision iladub emitted failed it — 26 focus
nodes at compile scope and 719 at grounding scope, under both closures. Name
the call site whenever you write "enforced," or the word does no work:
`vocab/shapes/dec-shapes.ttl`'s `DecisionHolonShape` requires `dec:optionSpace`
with `sh:minCount 2` (the ontology notes the no-change option counts toward
that two), exactly one `dec:chosen` option, a `dec:decidedBy` agent, and a
SPARQL check that the chosen option is actually a member of the declared
option space — a decision that picks an option it never considered fails the
membrane. `vocab/ontology/dec.ttl` layers three further capabilities onto
this core. First, **timeline/process structure** (`dec:Process`, `dec:Milestone`,
`dec:hasMilestone`, `dec:order`, `dec:clockStart`/`dec:clockStop`,
`dec:windowLimitMinutes`): a milestone must declare exactly one integer
`dec:order` per `dec-shapes.ttl`'s `MilestoneShape`. Second, **events and
lineage** (`dec:Event`, `dec:condition`, `dec:supersedes`, `dec:triggeredBy`,
`dec:revisitIf`): an event that matches a decision's `revisitIf` can reopen
it, each event required to carry exactly one `dec:condition` (`EventShape`).
A specialized event, `dec:ExpansionRequest` (⊑ `dec:Event`), models the
"off-the-map" boundary outcome — content a holon's declared map cannot
classify as either valid or a violation — and must name what it is about via
`dec:regarding` (`ExpansionRequestShape`). Third, **apex escalation**
(`dec:escalatedTo`, `dec:maxSeverity` on `dec:Scope`): `vocab/shapes/escalation-shapes.ttl`'s
`EscalationShape` is a SPARQL invariant closed-world within each decision —
if a decision's realized severity (via `dec:constrainedBy`, ordered by
`risk:order`) exceeds its autonomy scope's `dec:maxSeverity` ceiling, it must
carry `dec:escalatedTo` a higher-authority decision, unless it is itself the
apex (whose own ceiling covers the severity, so the filter never fires).

`dec` is deliberately built to be **portable, not permanent**: it is scoped
as an HGA extension, authored now because — per CLAUDE.md's project-family
description — HGA is not yet ready for strict decidability, and designed to
be upstreamed to or replaced by an HGA equivalent later. That portability
claim is not itself asserted inside `dec.ttl`'s own text; it is architectural
framing carried by CLAUDE.md and repeated on the promoted site page, not a
property this page's three cited sources encode directly.

**Settled vs open.** The deliberation core, timeline/process layer, events/
lineage, and apex escalation are all shipped and SHACL-enforced by the three
sources here. What's not evidenced by these files: `dec`'s own comment that
"the tool that reads decisions out of documents governs its own reading with
the same decision model" is a design intent realized concretely by
`iladub:PromotionDecision` (see `[[promotion-decision]]`) — the mechanism
lives in `iladub.ttl`, not in `dec.ttl` itself, so this page does not
duplicate that evidence.
