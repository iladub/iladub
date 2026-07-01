# iladub semantic architecture — design

**Date:** 2026-07-01
**Status:** approved (brainstorming complete; next step is the migration plan)
**Scope:** a namespace/semantic re-rooting — **no functional change**. Behaviour (M4
pipeline, escalation, risk, validation) is unchanged; only IRIs, prefixes, and module
organization change.

## The decision

**`iladub` becomes the namespace root.** iladub is François's — it predates HGA (defined
from decades of work on brittle data pipelines; the ET(K)L method and a context-graph
notion both pre-date Cagle's Holon Graph). iladub adopts the holon graph as a *good
architecture for* ET(K)L, and consumes HGA as the external substrate.

> **iladub = a thin epistemic core + `etkl` + `dec`** — the carrier that lifts knowledge
> from raw documents into HGA holons and governs the decisions made about them.

```
HGA (holon:) ── external substrate; consumed, aligned, never cloned
     ▲
     │ extends (align-not-import)
 iladub/dec ───────── decidability / decisionality (an HGA extension)
     ▲                DecisionHolon, Option, Scope, escalation, events, timeline
     │ PromotionDecision ⊑ dec:DecisionHolon
 iladub  (thin core) ─ the epistemic signature (domain-neutral)
     ▲                CandidateConcept · GroundedNode · PromotionDecision
     │ the grounding portal produces core nodes    + "never a proposition as an assertion"
 iladub/etkl ──────── the K-transform for documents
                      contract (= a destination holon's required projection schema),
                      Extract/Transform/Load, Field, ResourceRule, SourceDocument,
                      + the doc-holon fabric: RawDocumentHolon, CleanDocumentHolon,
                        SemanticHolon, GroundingPortal, MembraneHealth

Root: https://w3id.org/iladub
```

## Why this shape (the rationale, recorded)

- **Authorship.** iladub is the owned artifact; `etkl` and `dec` are François's related
  concepts, arranged freely because they were designed before HGA existed. Keeping them
  under `iladub` reflects that provenance. (This overrides an earlier "keep the method as
  an independent root" argument: `etkl` here is *narrow-scope* — raw→holon + conform — not a
  grand general method competing with HGA, so nesting it under `iladub` is right.)
- **`dec` is a deliberately-portable bridge.** It exists because agentic technology is being
  onboarded into the transform to make it less brittle, and that needs *decidability
  measures* (accountable, tracked decisions) **now** — before HGA is mature enough for strict
  decidability. `dec` is therefore designed to be upstreamed to / replaced by an HGA
  equivalent later (François is in the W3C Holon CG). Consequence for design: keep `dec`
  cleanly aligned to HGA and minimal, so it lifts out easily.
- **`etkl` is narrow-scope and could itself become a future HGA contribution** — HGA starts
  from *defining* holons, not *building* them from unstructured data; `etkl` fills that gap.
  Not now; noted so the choice doesn't foreclose it.
- **A thin `iladub` core, not a fold-in.** The assertion/proposition epistemics ("assert only
  what you can ground; propose everything else; never let a proposition pass as an assertion")
  are iladub's signature and stay a named, domain-neutral core rather than dissolving into the
  method.

## The three modules

| Module | Target IRI | Prefix | Holds | Depends on |
|---|---|---|---|---|
| **core** (thin) | `https://w3id.org/iladub#` | `iladub:` | `CandidateConcept`, `GroundedNode`, `PromotionDecision` + the no-leak invariant (assertion/proposition epistemics) | `dec` |
| **etkl** | `https://w3id.org/iladub/etkl#` | `etkl:` | `SemanticDataContract`, `Extraction`, `Transformation`, `Load`, `Field`, `ResourceRule`, `SourceDocument`, and the doc-holon fabric (`RawDocumentHolon`, `CleanDocumentHolon`, `SemanticHolon`, `GroundingPortal`, `MembraneHealth`) | core, `dec` |
| **dec** | `https://w3id.org/iladub/dec#` | `dec:` | `DecisionHolon`, `Option`, `Scope`, escalation (`escalatedTo`, `maxSeverity`, `EscalationShape`), events (`Event`, `supersedes`, `triggeredBy`, `revisitIf`), process/milestone timeline | HGA (align) |
| **risk** | `https://w3id.org/iladub/risk#` | `risk:` | `RiskContext`, `Sensitivity`, `RiskAssessment`, `Severity` — contextual risk as a *decidability measure* (grouped with `dec`) | HGA (align) |

**Dependency order** (most general → most specific): `HGA ← dec ← core ← etkl`, with `risk`
a decidability sibling of `dec`. `iladub` (the root) *is* core + etkl + dec + risk.

**The `PromotionDecision` seam.** `PromotionDecision` is a **core** term that subclasses
**`dec:DecisionHolon`** — literally "the epistemics using decidability." It is where the
grounding portal (etkl) crosses the membrane and produces a grounded node — the exact point
where "once a holon is created, a decision must be made" happens.

**Fabric-types placement.** The doc-holon fabric (`RawDocumentHolon` … `MembraneHealth`) lives
in **etkl** (it is the doc-production machinery: raw in, clean out, portal transform), keeping
the core genuinely thin. The core defines the epistemic membrane vocabulary; etkl's portal
*uses* it.

## Term migration map (old IRI → new IRI)

| Today | → | Target |
|---|---|---|
| `https://w3id.org/etkl#` (`etkl:`) | → | `https://w3id.org/iladub/etkl#` (`etkl:`) |
| `https://w3id.org/etkl/hol#` (`hol:`) | → | `https://w3id.org/iladub/dec#` (`dec:`) |
| `https://w3id.org/etkl/iladub#` (`iladub:`) | → | `https://w3id.org/iladub#` (`iladub:`) |
| `https://w3id.org/etkl/risk#` (`risk:`) | → | `https://w3id.org/iladub/risk#` (`risk:`) |
| ontology-doc IRIs `…/etkl/iladub/holons`, `…/hga-alignment`, etc. | → | the corresponding `…/iladub/…` path |
| shapes namespaces (e.g. governance-shapes, escalation shapes) | → | re-rooted under `iladub/…` to match their module |

The prefix rename that matters most: **`hol:` → `dec:`**. "hol" now reads as *holon* (Cagle's);
`dec` names what the module actually is — decidability. This removes the standing confusion.

## What does NOT change

- **The `iladub` PyPI package name and `iladub.dev`** — namespace ≠ package; both are untouched.
- **Behaviour and tests' assertions about behaviour** — the M4 decision, escalation, risk,
  SHACL conformance all produce the same results; only the IRIs/prefixes they use change.
- **The source-ownership boundary** — still "we author only our namespaces; HGA is consumed,
  never cloned." The *ours* root simply becomes `https://w3id.org/iladub…`. The guard test and
  the alignment-not-import discipline carry over unchanged in spirit (the align modules now
  point from `iladub/*` terms to `holon:*`).
- **HGA alignment** — the align modules (`*-hga-align.ttl`) re-root their subjects to the new
  IRIs but keep HGA terms as objects only.

## w3id.org resolution (one external step)

Minting the IRIs is ours; making them *resolve* is a community step:

- **Choosing `w3id.org/iladub/…`** — ours, no permission needed. The whole in-repo migration
  can proceed with the new IRIs regardless of resolution.
- **Resolution** — requires a PR to `perma-id/w3id.org` (the same service/process as the
  merged `w3id.org/etkl` registration, PR #6144). w3id.org is a shared registry, not a domain
  we own. The PR adds an `/iladub` redirect config (content negotiation: RDF → raw `.ttl`,
  browsers → `iladub.dev`), and **301-redirects the old `/etkl/*` paths → `/iladub/*`** to
  preserve the dated record. Draftable here; submitted under a GitHub account; merged by a
  w3id maintainer.

This step is **not a blocker** for the repo migration — it wires up resolution, in parallel or
after.

## What this supersedes in CLAUDE.md

- **"The project family"** — currently names `etkl` as the umbrella with `hol`/`iladub`/`risk`
  under it. This inverts that: `iladub` is the root; `etkl` + `dec` (+ the thin core + `risk`)
  are its modules; HGA is the external substrate.
- **Namespace conventions** — the four namespace IRIs and the `hol:`→`dec:` prefix.
- **Source-ownership "ours" column** — root becomes `https://w3id.org/iladub…`.

CLAUDE.md is updated alongside this spec to record the decision and mark the migration
**pending** (artifacts stay on `w3id.org/etkl/*` until the migration plan runs).

## Migration approach (the plan will detail)

A mechanical, test-preserving rename executed as its own effort:
1. Re-root the four namespace IRIs + ontology-doc IRIs across `vocab/ontology/*.ttl` and
   `vocab/shapes/*.ttl`; rename `hol:`→`dec:`. Rename files where names encode the old module
   (e.g. `hol.ttl` → `dec.ttl`, `hol-shapes.ttl` → `dec-shapes.ttl`).
2. Update Python `Namespace(...)` constants and any hard-coded IRI strings across
   `src/iladub/` and `tests/`.
3. Update the source-ownership + HGA-alignment tests to the new roots.
4. Full suite green (same pass/skip counts as before — behaviour unchanged).
5. Draft the `perma-id/w3id.org` PR (new `/iladub` config + `/etkl/*` 301s) for submission.

## Out of scope

- Actually submitting/merging the w3id PR (external; drafted here, submitted by the author).
- Any functional change to compilation, decisions, escalation, or risk.
- Contributing `dec` or `etkl` upstream to the W3C Holon CG (future, dated acts).
