# Compile → Federate — the CleanDocumentHolon becomes the next document's terminology

- **Date:** 2026-07-24
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Scoped to a **single vertical slice** ("loop F").
- **Context:** Steering topic 3 — *keep closing vertical slices toward federation*. iladub already
  has role-shaped `hproj:Projection`s (`examples/transplant/transplant-governance.ttl`), derived
  projections (`risk:RiskAssessment`, `tab:NormalizedBase` ⊑ `hproj:Projection`), the grounding
  portal (`ground.py`), and the reshape round-trip oracle (`reshape.certify` → `oracle.round_trip`).
  What is missing is **projection-*exchange* between two holons** — a compiled `CleanDocumentHolon`
  participating in Cagle's concentric-openness federation. This slice adds exactly that, at the
  **format-agnostic grounding seam**, and proves the big-picture HGA embrace end-to-end.

---

## 1. Purpose and scope

Demonstrate that a **compiled `CleanDocumentHolon` federates**: its outward projection is consumed
by a *second* document's compile as a provided terminology. This realises Cagle & Shannon's
concentric-openness thesis — *"nodes don't synchronise databases; they exchange projections"* — and
the sharpest iladub reading of it: **a compiled holon *is* a `SemanticHolon` (a terminology) for the
next compile.** Context is carried across documents; only *promoted* knowledge crosses; the interior
stays opaque.

**In scope (this slice):**
- Doc A: a **real document file** (CSV or HTML — non-PDF, to prove format-agnosticism) → `readers.py`
  → region-anchored `SurfaceConcept`s → the **real grounding portal** (`ground.py`:
  propose→promote→`GroundedNode`) → `CleanDocumentHolon` A.
- **`federate-projection.rq`** — a named SPARQL `CONSTRUCT` deriving A's `etkl:DocumentProjection`
  (promoted concepts only: IRI + `skos:prefLabel` + `skos:inScheme`).
- Doc B: a second real document → grounding portal, with **A's projection as the provided terminology**
  (zero new grounding code — the projection is SemanticHolon-shaped).
- **`federate.certify_federation`** — a round-trip oracle certifying *soundness ∧ opacity ∧ containment*.
- `etkl:DocumentProjection` vocab (⊑ `hproj:Projection`) + `etkl:DocumentProjectionShape` + a worked
  example pair + conformance/negative/oracle tests.

**Non-goals (out of scope, each a later increment):**
- The PDF geometric table front-end (`compile.py`/`geometry.py`/`bands`/`tiling`) — it lives *below*
  the region seam; this loop never touches PDF geometry.
- `hproj:NowGraph` Stage-8/9 machinery, ViewerPass role-parameterisation of the projection, and any
  access-governance overlay (that is the High Seas / governed-projection slice).
- A named-query *registry* / dispatch layer (topic 1 substrate) — the loop uses one named `CONSTRUCT`
  directly; a registry is not needed to prove federation.
- `hfed:` federation vocabulary — **reserved** in the HGA spec; deliberately NOT minted here.

**Success criteria:**
1. A real (non-PDF) document drives the loop end-to-end with **zero model calls** (deterministic
   surface concepts, e.g. CSV header cells), so the test is reproducible.
2. A's projection carries **only promoted grounded concepts** — no interior term ever appears in it
   (SHACL-enforced, not just oracle-checked).
3. B grounds against A's projection through the **unchanged** grounding portal.
4. The oracle certifies *consumer view ⊆ producer projection ⊆ producer promoted interior*, and any
   failure **escalates in-band** — never a silent wrong federation.
5. Adding a new source format means adding a `readers.py` adapter, **not** touching the loop.

---

## 2. Architecture and data flow

```
Doc A (real file)                          Doc B (real file)
   │ readers.py (csv/html/…)                  │ readers.py
   ▼                                          ▼
 SurfaceConcepts (region-anchored)          SurfaceConcepts
   │ ground.py  propose→promote               │ ground.py  propose→promote
   ▼                                          ▼   (terminology = A's projection)
CleanDocumentHolon A                        CleanDocumentHolon B
  interior: grounded graph +                  grounded nodes point at
  promotion decisions + regions               A's *projected* IRIs
   │ federate-projection.rq (named CONSTRUCT)         ▲
   ▼                                                  │ consumed as a provided terminology
A's etkl:DocumentProjection ────── exchange ──────────┘
  (promoted concepts only: IRI + prefLabel + inScheme)
                          │
                          ▼  federate.certify_federation(A_interior, A_projection, B_graph)
        verdict: sound ∧ opaque ∧ contained  →  dec record / in-band escalation
```

**The format-agnostic seam.** Everything from `SurfaceConcept`s rightward is format-neutral;
`readers.py` (already handling txt/html/pdf/docx/xlsx) is the only format-coupled part. The loop is
anchored at this seam, so it is format-agnostic *by construction*. PDF is merely one adapter, and the
one furthest along because it additionally has the geometric table engine below the region layer.

---

## 3. Components

### 3.1 A's compile (reuse + a thin format adapter)
`readers.py` → deterministic surface-concept extraction → `ground.py` (`propose`→`promote`→
`GroundedNode`). The grounding portal is reused unchanged. The one new, **format-scoped** piece is a
thin deterministic adapter that turns the chosen file into region-anchored `SurfaceConcept`s — for the
demonstrator, a **CSV** whose header cells map 1:1 to `SurfaceConcept(surface=header, region=cell-ref)`
(reproducible, no model calls). This adapter lives at the `readers`/region layer, below the seam; a new
format = a new adapter, and the loop is untouched.

### 3.2 The projection — `vocab/queries/federate-projection.rq` (AXIOM)
A single SPARQL `CONSTRUCT` over A's interior graph **∪ the terminology A grounded into** (the latter
supplies the public canonical label; `interpret.run` already unions its `*graphs`):
- **Selects** every `iladub:GroundedNode` that `iladub:wasPromotedBy` some `iladub:PromotionDecision`.
- **Emits**, per selected node, a `skos:Concept` (the grounded IRI) with `skos:prefLabel` — the grounded
  concept's **public canonical label** (from the terminology A grounded *into*, `iladub:groundsTo`), NOT
  A's raw interior surface text — and `skos:inScheme` a single `etkl:DocumentProjection` node for A. This
  keeps the interior (raw surface strings, regions) opaque while still giving B a groundable label.
- **Emits nothing** of the interior: no `iladub:SourceRegion`, `iladub:CandidateConcept`,
  `iladub:PromotionDecision`, `iladub:confidence`, `iladub:fromRegion`, or provenance-to-page.

The projection graph *is* A's `hproj:Projection`; being SKOS-shaped it is a valid provided terminology
for B's portal. Open-world derivation (evidence-positive: a concept is projected only because a
promotion is *present*), matching the neurosymbolic gate.

### 3.3 B's compile (reuse)
`ground.py` run with **`terms = A's projection graph`**. No change to the grounding portal — the
projection is just another terminology. B's grounded nodes resolve to A's projected IRIs. This is the
`SemanticHolon ⇄ CleanDocumentHolon` symmetry made operational.

### 3.4 The oracle — `src/iladub/etkl/federate.py` + `oracle.py` (PROCEDURAL glue, justified)
`certify_federation(a_interior, a_projection, b_graph) -> FederationVerdict`, three set-checks over
SPARQL/graph results (no domain heuristic, no tuned constant — irreducible engine glue, like
`interpret.run`):
- **Soundness** (projection ⊆ promoted interior): every `skos:Concept` in `a_projection` traces to a
  `GroundedNode` in `a_interior` that `wasPromotedBy` a `PromotionDecision`.
- **Opacity** (interior stays inside): the set of A interior-only terms (its `SourceRegion`s,
  `CandidateConcept`s, `PromotionDecision`s, confidences, provenance) is **disjoint** from both
  `a_projection` and `b_graph`.
- **Containment** (B ⊆ projection): every A-sourced IRI that B grounded to is a member of the projection
  concept set.

`FederationVerdict` reuses the `oracle.OracleVerdict`/`dec` verdict idiom. On any failure the loop
**escalates in-band** (a `dec` escalation / report entry), never silently federates.

### 3.5 Vocab & shapes
- `vocab/ontology/etkl.ttl` (**standalone**): `etkl:DocumentProjection a owl:Class` — the
  CleanDocumentHolon's outward concept surface (the `Projection` aspect made concrete). No HGA/`hfed:`.
- `vocab/ontology/etkl-holons.ttl` or the etkl align module: `etkl:DocumentProjection rdfs:subClassOf
  hproj:Projection` (HGA term as **object** only — source-ownership).
- `vocab/shapes/etkl-shapes.ttl`: `etkl:DocumentProjectionShape` — a `DocumentProjection`'s members may
  be **only** `skos:Concept`s; it must NOT carry `iladub:CandidateConcept`, `iladub:PromotionDecision`,
  or `iladub:SourceRegion` (membrane opacity as a closed-world constraint).

---

## 4. Testing and demonstrator

`examples/federation/` — a real document pair (`doc-a.csv`, `doc-b.csv` or `.html`) + the expected
projection. `tests/test_federation.py`:
- **E2E loop:** real Doc A → ground → `federate-projection.rq` → Doc B grounds against A's projection →
  `certify_federation` returns a passing verdict. Zero model calls.
- **Projection conforms:** A's projection passes `etkl:DocumentProjectionShape`.
- **Negative — leaky projection** (`tests/federation-projection-leak.ttl`): a projection carrying an
  interior term (`CandidateConcept`/`PromotionDecision`/`SourceRegion`) **must fail** the shape.
- **Negative — broken oracle:** a B graph grounding to an A IRI that A never projected → **containment
  fails**; and a projection carrying a concept with no promoted `GroundedNode` → **soundness fails**.

---

## 5. Neurosymbolic gate compliance (Global Constraint)

- **Projection derivation → AXIOM.** A fixed SPARQL `CONSTRUCT` in `vocab/queries/`, open-world,
  evidence-positive (project a concept only when its promotion is present). No procedural transform,
  no tuned constant.
- **Membrane → SHACL (closed-world).** `etkl:DocumentProjectionShape` validates what may appear in a
  projection — the closed-world constraint mirror of the open-world derivation. The projection graph is
  the closure boundary.
- **Oracle → PROCEDURAL, justified.** `federate.certify_federation` is set comparison over SPARQL/graph
  results — the same irreducible engine glue class as `interpret.run`/`oracle.round_trip`; it invokes a
  standard engine and compares sets, carrying **no** domain decision and **no** tuned tolerance. Stated
  in-code and here per the gate.
- **Grounding → reused**, already gate-classified.

No procedural geometry, no tuned constant, no span/read/group heuristic is introduced.

---

## 6. Source-ownership & alignment discipline

- `hproj:Projection` is a **normative** HGA term (`hproj:`, Pass E) — aligned via `rdfs:subClassOf` in
  the align module only, HGA term as **object**.
- `hfed:` (federation) is **reserved** in the spec — deliberately **not** used or mirrored. Federation
  here is projection-*exchange* using `hproj:`, exactly as Cagle defines it, so no federation vocab is
  minted.
- `etkl:DocumentProjection` is authored only in the owned `etkl:` namespace; `etkl.ttl` stays standalone
  and reasoner-free (alignment lives in the separate module).

---

## 7. Relation to prior work and steering

- Mirrors the **reshape round-trip** substrate (`reshape.certify` → `oracle.round_trip`): derive a
  projection via `CONSTRUCT`, certify with an oracle before emitting.
- Complements **topic 1** (`internal/decisions/2026-07-02-fluree-as-hga-substrate.md` §12): the projection
  is a derived `hproj:Projection`; a named-query *registry* is explicitly deferred (consume, don't clone).
- Complements **topic 2** (`dec:ExpansionRequest`, PR #62): a document B whose surface concept is
  ungroundable *even against A's projection* raises an expansion request — the two loops compose.
- Complements **`docs/four-groundings.md`**: this is Spatial grounding (containment/projection) made to
  *exchange* across holons.

---

## 8. Open questions / later increments

1. Drive Doc A from a **PDF or XLSX** via the geometric front-end (a `readers.py`/region increment) —
   proves the same loop over the richest format.
2. Make the projection **role-shaped** (`hproj:NowGraph` + ViewerPass) — the governed-projection / High
   Seas slice.
3. Register the projection as a **named query** on a Fluree substrate (topic 1) — federation over the
   enforcement layer, `f:` policy at the membrane.
4. Multi-hop federation (B's projection consumed by C) — convergence/apex behaviour.
