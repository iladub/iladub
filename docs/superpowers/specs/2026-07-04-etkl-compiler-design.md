# ET(K)L compiler — multimodal extraction design

- **Date:** 2026-07-04
- **Author:** François Rosselet
- **Status:** Design (brainstormed). Scoped to the **first increment**; later increments listed at the end.
- **Context:** iladub's document compiler front-end. The grounding + small-model extraction already
  exist (`recognise.py` deterministic label matching; BAML + Claude Haiku, `source_quote` + confidence,
  "do not invent"). **The missing piece is the multimodal front-end** that turns a real PDF's layout,
  tables, and figures into the Document Region Graph *before* grounding. This spec designs that.

---

## 1. Purpose and scope

Build the layer that compiles a **human-addressed PDF** into a **contract-agnostic, span-anchored,
grounded region/table structure** — precisely, fast, and honestly — which a contract (FHIR first) then
projects. Precision comes from **verification against measured geometry**, not from trusting any parser
or model.

**First increment (this spec):** the deterministic **layout + hierarchical-table engine** for
**text-layer PDFs** — spatial geometry → bands → gutters → leaf grid → header-as-tiling → validated
structure + header-path anchors + a `dec` verdict per region — with a **VLM used only on the residue**.
Output is a **neutral table/region holon** (no FHIR baked in).

**Non-goals (this increment):** the FHIR projection itself, figure/image extraction, scanned-page OCR,
cross-page continued-table reconciliation. Each is a later increment (§12), with escape hatches designed
in now (everything unresolvable degrades through `dec`).

**Success criteria.** On text-layer PDFs with pivoted, merged-cell, hierarchical-header tables:
(1) correct leaf grid and header tree, or an **honest escalation** — never a silent wrong reading;
(2) every emitted cell carries a span anchor (page + bbox + header-path); (3) the common case makes
**zero model calls**; (4) adding a new document shape means adding a *validator invariant*, not a
*generator heuristic*.

---

## 2. Design principle — the determinism cursor (load-bearing)

**Place the cursor by one test: is there a cheap, closed-form check that tells you when the answer is
wrong?** Determinism goes as far as a checkable *oracle* exists, and not one step further.

| Task class | Cursor | Example |
|---|---|---|
| **Measurement** (never interpretation) | deterministic, always | points, bboxes, whitespace profiles, font advances |
| **Structure with invariants** | deterministic *generation* (output is checkable) | column grid = persistent gutters; header = tiling of leaf grid |
| **Open interpretation with a cheap check** | AI *generates*, determinism *validates* | ambiguous span; wrapped-vs-parent; region type |
| **Open interpretation with no check** | AI generates → irreducible → `dec`/`risk`/escalate | value↔analyte when rows are ambiguous; `"Hgb"`→LOINC |

Four corollaries that the whole compiler is built to:

- **Generation vs validation asymmetry.** Generating a table reading is open-ended; *checking* one is
  closed. So even where AI must generate, **determinism still owns the validation** — the AI is on a
  leash held by the oracle.
- **The deterministic layer's real job is to manufacture the oracle.** The comparison with
  LlamaParse/docling/unstructured is not deterministic-vs-AI; it is **AI-you-must-trust vs
  AI-you-can-verify**. Those tools fail *silently* on merged-cell headers (no measurement layer → no way
  to know they're wrong). The geometry layer is what earns the right to use a model without trusting it —
  and stays valuable *as models improve* (a better model still needs an oracle to be trusted).
- **Compression = decompose to the residue.** Advancing the cursor buys precision **and** velocity from
  one act: recovered structure both validates the AI *and* lets us hand it only the sub-question it must
  answer (leaf boundaries + labels + extents — a dozen tokens — not the page). S/N is maximised by
  **never sending the page**. Precision and velocity are the same lever, not a trade-off.
- **The cursor is per-region and dynamic.** Each region's *measured decidability* sets its own cursor:
  clean tiling + confident pitch estimate → no model call; wobbly calibration or a failed invariant →
  escalate that region only. The document tells us where the cursor goes, region by region.

**Two guardrails.** (a) *"Proven" = "has a bounded oracle," not "I wrote code for it."* If the
deterministic layer needs special-case #50 for band detection, that oracle is not closed-form → push the
cursor back to AI+validate. Determinism sprawl is as dangerous as model dependence. (b) *Deterministic-first
for the proven core; escalate the tail, marked.* Scans/exotic layouts/non-PDF are a `dec`-flagged
fallback regime, never a silent default.

---

## 3. Architecture — two layers

```
  PDF ──▶  [ Layer 1: neutral region/table compiler ]  ──▶  region/table holon
                                                              (span-anchored, contract-free)
                                     │
                                     ▼
           [ Layer 2: contract projection ]  ──▶  contract-conformed holon (FHIR first)
```

**Layer 1 is domain-neutral and is this increment.** It never mentions FHIR. It produces a *table holon*:
leaf grid, header tree, cells, and a **header-path anchor** per cell, each with span (page + bbox) and a
`dec` verdict. Keeping FHIR out of Layer 1 preserves the generality the manifesto promises — the same
engine serves any contract.

**Layer 2 (later increment)** is a `SemanticDataContract` (FHIR) that projects Layer 1's output:
structural resources deterministically; terminology codes `dec`-governed (assert a code only under high
decidability, else `code.text` + escalate).

### Layer 1 pipeline (cursor annotated)

```
PDF text layer (pdfplumber, points)                         [measure · deterministic]
  → row-whitespace profile → horizontal BANDS               [structure+invariant · deterministic]
      → per band: type-guess (title/para/table/footnote)
  → per table band: column-whitespace profile → GUTTERS → leaf grid (BODY rows only)
      → logical-row grouping (wrapped-cell merge within grid)
  → header band: snap each label to a leaf-column SPAN by gutter-crossing   [structure+invariant]
      → containment tree by interval nesting → header-path per leaf column
  → VALIDATOR: tiling invariants + round-trip diff → per-region dec verdict [oracle · deterministic]
      ├─ pass            → emit validated table holon (span-anchored)
      ├─ local fail      → emit what validated; escalate the failing region only  [partial]
      └─ global fail /   → decompose residue → small VLM proposes (constrained)   [AI · validated]
         ambiguous span     → re-run validator on the proposal → dec verdict
```

---

## 4. Components (isolated units)

Each is a small, independently testable unit — *what it does · how you use it · what it depends on*.

1. **`geometry`** — extract text runs with bboxes in **points** (pdfplumber). Also renders the faithful
   **monospace spatial-ASCII** (the human/model-legible view and the round-trip oracle's target).
   *Depends on:* pdfplumber. *Invariant:* strictly monospace-grid faithful (no proportional collapsing).
2. **`bands`** — row-whitespace profile → horizontal bands; per-band type guess. *Depends on:* geometry.
3. **`grid`** — per-band column-whitespace profile → gutters → leaf boundaries, **computed from body rows
   only**; per-band pitch `p` (column) and `l` (line) estimators **with a confidence** (sample size).
   *Depends on:* bands.
4. **`headers`** — snap each header label to a leaf-column **span by gutter-crossing** (ink-extent only as
   a tolerance check); build the **containment tree**; emit header-path per leaf column. *Depends on:* grid.
5. **`validator`** — the oracle. Tiling invariants (coverage, refinement, leaf-accounting), value-type
   homogeneity per column, and **round-trip** (re-render inferred structure to ASCII, diff against the
   faithful render). Deterministic. *This is the codebase we maintain; it stays small because validation
   is bounded.* *Depends on:* geometry, grid, headers.
6. **`decide`** — fold calibration confidence + span confidence + tiling/round-trip residual into one
   per-region `dec` verdict (`decidable` / `escalate`), lowering the ceiling when estimator sample is thin.
   *Depends on:* validator. Aligns to `dec:` vocabulary.
7. **`residue`** — when `decide` says escalate: decompose the region to the minimal high-signal input
   (leaf boundaries + labels + measured extents, or a thumbnail crop) and call a **small cloud VLM/LLM**
   with **constrained (schema) decoding**; feed the proposal back through `validator`. *Depends on:*
   decide, validator, a model client (reuse BAML). Never on the hot path for well-formed tables.
8. **`holon`** — assemble the validated structure into the neutral **table/region holon** (leaf grid,
   header tree, cells, header-paths, spans, `dec` verdicts); hand to Layer 2 / store. *Depends on:* all above.

Orchestration/storage (adopt, don't build):
- **CocoIndex** — the incremental, lineage-tracked flow: substrate (content hash) → spatial-ASCII → bands
  → grid → hypothesis → validated structure. Incremental caching means an unchanged page never re-runs;
  streaming subsumes batch and interactive.
- **LanceDB** — warm multimodal working store: validated cells with header-path columns, failing regions
  with their `dec` verdict, figure crops (later), embeddings for convergence/retrieval.

---

## 5. Decidability & graceful degradation

Three outcomes, never all-or-nothing, never fabricate, never silently drop:

- **Region validates** → emit cells with header-path anchors, high `dec`.
- **Local invariant fails** (one column won't type-check, one header won't tile) → **partial**: emit the
  validated cells, degrade the failing region to `.text`, attach it for escalation.
- **Global failure / irreducible ambiguity** (round-trip diverges; value↔analyte ambiguous; label spans
  visually-unstable columns) → **escalate**, keep the region as spatial-text media.

The residue the validator **cannot** catch (a grid parsed correctly but a value bound to the wrong
analyte) is irreducible; it belongs in `risk:` (clinical stakes) → escalation, **not** in the validator.
Knowing which errors the oracle can't catch is itself part of being honest at the membrane.

---

## 6. Robust measurement (kills resolution / margins / fonts)

- **Points, not pixels.** Read spans from the PDF text layer in points (device-independent) — resolution
  stops mattering. ASCII is the legible/oracle view, not the measurement source.
- **Topological, not metric.** A label's span = *which leaf gutters it crosses*, not its absolute x —
  margins shift everything together, crossings are invariant.
- **Fractional tolerances.** Every threshold is a fraction of the band-local column-pitch `p` / line-pitch
  `l` — a dense small-font table and a sparse large-font table use the same constants. Gutter threshold is
  a band-local percentile, not a global constant.
- **Recalibrate per band and per page.** Never carry a grid across a page; reconcile continued tables by
  **column-pattern**, not coordinates (later increment).
- **Measure the measurement.** When the sample supporting `p`/`l` is thin (small summary tables — common
  in medical reports), widen tolerances and **lower the decidability ceiling** so a shakily-measured grid
  can never be emitted as high-confidence.

---

## 7. Stack

pdfplumber (geometry, points) · numpy (whitespace profiles, estimators) · a small constrained-decoding
model client via **BAML** (reuse; Haiku-class + Haiku-vision for residue) · **CocoIndex** (incremental
flow) · **LanceDB** (warm multimodal store). No managed parser in the backbone — the VLM-for-residue *is*
the "parser" and it fires rarely; a managed parser (LlamaParse) is at most an optional **scan-only**
backend (later). This supersedes the earlier "managed parser as backbone" direction — validator-centric
geometry is faster (fewer calls), more precise (oracle), and less endpoint-dependent.

---

## 8. Testing strategy

- **Synthetic PDF fixtures** with known ground truth: flat tables, merged parents, centered labels,
  ragged/pivot headers, wrapped cells, sparse summary tables — generated programmatically (reportlab) so
  the expected grid/tree is known.
- **Invariant unit tests** — each validator invariant tested in isolation (coverage, refinement,
  leaf-accounting, type-homogeneity, round-trip diff) with positive and negative cases.
- **Oracle negative tests** — deliberately wrong structures must be *caught* (the validator must flag,
  not pass). The round-trip is the star: a mis-grid must produce a diff.
- **`dec` behaviour tests** — thin-sample → lowered ceiling; local fail → partial; global fail → escalate.
- **Golden real reports** (synthetic-but-realistic clinical) — end-to-end, asserting either correct
  structure *or* honest escalation (never silent wrong).
- The **round-trip oracle needs no semantic ground truth** — the geometry is the oracle — which is what
  makes the test suite tractable.

---

## 9. Relationship to existing iladub

- Layer 1's structure recovery **populates the Document Region Graph** (architecture.md's
  "structure-preserving intermediate"); header-path = the DRG's span anchor.
- `validator` + `decide` = the **membrane**: a region crosses only if it validates; low decidability → held.
- Header-path anchors + spans = **provenance-to-page**, made literal.
- `residue` reuses the existing **BAML** model layer; grounding reuses `recognise.py`. Assert/propose
  applies to codes in Layer 2 (`CandidateConcept` + `PromotionDecision`).
- A runnable **skeleton already exists** (built in a prior session, not yet in this repo:
  pdfplumber words → bands → gutters → body-only grid → gutter-crossing snap → containment tree → tiling
  validator → `dec` verdict). It will be brought in as the base for `geometry/bands/grid/headers/validator/decide`.

---

## 10. Open decisions (need a call)

1. **FHIR shape (Layer 2)** — R4 vs R5; **Bundle of discrete Observations** (queryable; recommended) vs
   **DocumentReference / FHIR-Document** ("return a doc"). Different downstream ergonomics.
2. **Terminology ownership** — iladub binds LOINC/SNOMED/UCUM itself with `dec` confidence, **or** stops at
   structural FHIR + `code.text` and hands terminology to a downstream terminology service. *Recommendation:*
   iladub emits `code.text` always and a code only under high decidability (assert), else propose+escalate —
   i.e. own the *decision*, allow a service as the *suggester*.
3. **Figures/images pipeline** — classify region-type first (chart / ECG / micrograph / signature) → route
   (media vs Observation-with-attachment vs opaque). A whole sub-pipeline; later increment.
4. **Scans (no text layer)** — deskew → normalise by line-height → OCR bbox → same pipeline in
   normalised-pixel space; OCR confidence → `dec`. Later increment.
5. **Continued tables across pages** — reconcile by column-pattern (count + type signature + relative
   pitch), not coordinates; mismatch → escalate. Later increment.
6. **VLM/model choice for residue** — Haiku-vision first; budget for the residue sometimes needing a
   bigger model or human (the residue is where small models are weakest). Escalation ladder is a `dec`/`risk`
   concern, not a fixed model.
7. **CocoIndex / LanceDB adoption** — confirm both, or start with a thin in-repo incremental cache + a
   simpler store and adopt them when the flow stabilises (validate with a spike).

---

## 11. Increment roadmap

1. **This spec** — Layer 1 deterministic layout+table engine + residue-VLM + `dec`, text-layer PDFs,
   contract-neutral holon. (Bring the skeleton in; harden; test suite.)
2. **Layer 2 — FHIR projection** (structural deterministic; terminology `dec`-governed).
3. **Figures/images** (classify → route).
4. **Scans / OCR** regime.
5. **Continued tables** across pages.
6. **CocoIndex/LanceDB** productionised flow + load of the resulting holons into the immutable-ledger
   enforcing substrate (per the internal substrate decision — later, once the holon is correctly built).
