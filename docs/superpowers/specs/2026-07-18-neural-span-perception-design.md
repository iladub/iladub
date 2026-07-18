# NEURAL Span-Perception Layer — Roadmap + Slice 1 (narrow-flank merge resolution)

**Date:** 2026-07-18
**Status:** Design — approved for spec (brainstorm 2026-07-18).
**Scope of this document:** (1) the ordered decomposition of the whole NEURAL column of the
recovery-layer audit (`docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md`)
into vertical loops with the disposing oracle named for each; (2) the full design for **Slice 1**,
the narrow-flank merge-resolution silent-wrong (loop **B1.2**). Each later slice gets its own
spec → plan → implementation cycle.

**Gate context (CLAUDE.md §8):** every decision below is classified before any procedural code.
The AXIOM reframes of the audit (loops one/B/C/B2a/B2b/B2c) have all shipped; what remains unbuilt is
the **NEURAL** column — the audit's "loop two: the visual-encoding perception grammar." This layer
builds it, retrofitting the rest of the perception code to the two shipped exemplars
(`reshape.certify_with_proposals`, `segment.find_table_gutter`), which already embody
propose → oracle → dispose.

---

## Part 1 — The NEURAL layer roadmap

The remaining NEURAL decisions split into two families. **The split is by oracle-readiness, and
that drives ordering** — a NEURAL slice ships only when a *sound, proposer-independent* oracle can
reject wrong proposals (else it is an LLM guess replacing geometry, which the gate forbids).

### Family A — span perception (oracle READY: tiling SHACL, shipped in loop C)

All are "which contiguous columns/rows does X span/cover" reading judgments. They share the shipped
Coverage / NoOverlap / Refinement shapes as their structural guardrail.

| Loop | Decision | Audit ref | Disposing oracle |
|---|---|---|---|
| **B1.2** | narrow-flank merge resolution — **SLICE 1 (this spec)** | C3 | tiling SHACL + independent-leaf-header corroboration + escalation |
| B2 | general merged-header span (`_covers_for_cell`) | C2 | tiling SHACL |
| B3 | wrap-continuation: tight sub-line = wrapped continuation vs distinct level | C5 | tiling + line-model |
| B4 | cross-tab column tree (Voronoi → propose) | D1 | `col_tree_tiles` SHACL |
| B5 | ditto-margin: blank cell = ditto-continuation vs genuinely empty | E2 | row-tree tiling |

### Family C — raw boundary/segmentation perception (oracle UNSOLVED — must be designed first)

These carry the worst tuned constants in the layer (`grid.infer_leaf_grid` `0.98/3/4` + per-document
tuning docstring; `bands.detect_bands` `1.8×`; `segment._widest_gutter_cut` `2.0×`) but have **no
round-trip oracle yet**. They come after the pattern is proven on Family A, and each begins by
*designing its oracle*, not by writing a perception slice.

| Loop | Decision | Audit ref | Oracle |
|---|---|---|---|
| C1 | column boundaries (`infer_leaf_grid`) | A1 | **needs design** (first task of the loop) |
| C2 | vertical band segmentation (`detect_bands`) | A2 | **needs design** |
| C3 | side-by-side table split (`_widest_gutter_cut`) | G1 | `find_table_gutter` reclassify (partial — extend) |

**Ordering rationale:** Family A first (shared, already-shipped oracle → establishes the
propose→oracle→dispose pattern cleanly); the narrow-flank silent-wrong as the entry slice (the *only*
documented silent-wrong in the whole layer, narrowest scope, retires the deferred B1.2 item at
`docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md`). Family C last, and
each Family-C loop's first task is designing its oracle — no perception slice ships on a confidence
threshold (per the standing "oracle not confidence" rule).

---

## Part 2 — Slice 1: narrow-flank merge resolution (loop B1.2)

### 2.1 The decision (one sentence)

When a spanning (multi-column, non-leaf) header's centered run is geometrically **tied** between
covering leaf columns `[1..k]` and `[1..k+1]` — because a flanking column narrower than half the
median pitch shifts the endpoint center by less than `_centered_run`'s `0.25·pitch` tie-band —
decide whether that flanking column is **under the span** or a **parentless leaf**.

### 2.2 Why it is NEURAL (the gate justification — stated in code and spec)

Both rival runs sit inside `_centered_run`'s `0.25·pitch` tie-band **and** inside
`merge_tiling_ok`'s `0.5·pitch` centering tolerance (`src/iladub/etkl/headers.py:218,279`). Geometry
and the current structural oracle are **both blind** to the 3-vs-4 call; the tie-band exists
*because geometry cannot decide*. The `0.25`/`0.5` constants are prima-facie evidence (CLAUDE.md §8)
that the decision belongs in NEURAL, not procedural code. The discriminating signal is a **reading
judgment** — does the spanning label subsume a flanking column that carries its own identity —
which is perceptual, not geometric.

Reproduction (from the deferred doc), boundaries `[0,100,200,300,400,400+w]`, `median_pitch=100`,
band `=25`:

```
col4 width 40 / 49 / 50  -> today: GROUP resolves to [1,2,3,4]  (col 4 SILENTLY over-absorbed, asserted)
col4 width 51            -> today: GROUP resolves to [1,2,3]    (correct; col 4 a parentless leaf)
```

### 2.3 The seam (mirrors the shipped A2.1 `certify_with_proposals` pattern)

Structurally identical to `reshape.py:certify_with_proposals` + `propose.py`: an **injected**
proposer (offline `FakeProposer`, live `BamlProposer` behind `BAML_LIVE`), a semantic oracle that
**disposes**, and a `PromotionDecision` as the only path into the asserted graph.

**Step 1 — Propose (BAML).** New BAML function `ProposeHeaderSpan` (in a new
`baml_src/span_propose.baml`) and a `SpanProposer` protocol with `FakeProposer` / `BamlProposer`
(added to `src/iladub/etkl/propose.py`, beside the existing dimension-name proposer). The proposer
reads, for the tied case only:

- the spanning header's **text**,
- each candidate contiguous leaf column's **own leaf-header text** (including the flanking column's),
- the spanning label's **ink x-extent** relative to the column boundaries.

It returns: the covered leaf-column run (`covers: int[]`), a one-sentence `rationale`, and a
calibrated `confidence` (0–1). BAML class `HeaderSpanProposal { covers int[]; confidence float;
rationale string }`.

**Step 2 — Dispose (two-oracle composition; confidence NEVER promotes).**

Confidence is used *only* to route toward escalation — never as the promotion gate (standing rule:
*confidence ≠ validity*). The disposition composes two oracles:

- **Structural oracle (tiling SHACL, already shipped, loop C):** the proposed run must form a legal
  partition of the header level — Coverage / NoOverlap / Refinement. Rejects gross errors. This is
  **necessary but not sufficient**: when the flank is otherwise unclaimed, *both* `[1..k]` and
  `[1..k+1]` pass tiling, so this oracle cannot pick between them on its own.

- **Distinguisher oracle — independent-leaf-header corroboration (the actual closer):** evaluate the
  flanking column against an independent structural signal:
  *does the flanking column carry its own leaf-header token that is NOT lexically part of the
  spanning label?*
  - **Flank has an independent leaf header** (a leaf-header token not contained in the spanning
    label) → the flank is a **parentless leaf** → the admissible run is `[1..k]`.
  - **Flank is header-empty (no own leaf header) and the spanning label's ink extent reaches it**
    → the flank is **under the span** → the admissible run is `[1..k+1]`.
  - Corroboration **agrees with BAML's proposed run** → the reading is admissible → **PromotionDecision**
    admits the resolved span into the header tree (an `iladub:PromotionDecision`, per §3/§4 — the same
    decision vocabulary that governs `certify_with_proposals`).
  - Corroboration is **absent or disagrees** with BAML, or BAML confidence is low, or *both* rival
    runs remain admissible → **escalate `MERGE_AMBIGUOUS`**. Never assert a guess.

**Invariant:** the 3-vs-4 resolution is produced by *BAML's reading corroborated by an independent
structural signal and validated by the tiling SHACL* — never by a geometric constant and never by a
confidence threshold. When no corroborated, uniquely-legal reading exists, the slice **escalates**
rather than asserts (honest failure > fake success).

### 2.4 Where it plugs in

`repair_coverage` (`headers.py:225`) currently calls `_centered_run` for every coarse node. The
change: `_centered_run` continues to resolve the unambiguous case unchanged (fast path). **Only when
the winning run is inside the tie-band with a rival run that differs by exactly one narrow flanking
column** does `repair_coverage` route the node through the propose→dispose seam. Unambiguous spans
never touch the proposer — it is invoked *only where geometry is provably undecided*, exactly where
it is earned (YAGNI; keeps the live-model path minimal and the offline path deterministic).

The escalation surfaces as the existing `MERGE_AMBIGUOUS` signal (`headers.py`), so downstream
routing/compile handling is unchanged — this slice adds a *third* outcome (proposed-and-promoted) to
the existing certify/escalate pair, it does not invent new control flow.

### 2.5 The gate test (anti-overfit — mirrors `test_transform_gate.py` / celltype gate)

New `tests/etkl/test_span_gate.py`, built in this order (probe → plan → adversarial review, the same
discipline that caught the median silent-wrong and the nameless-pivot routing):

1. **Regression fixture FIRST:** the narrow-standalone-column layout —
   `[0,100,200,300,400,400+w]`, `w ∈ {40,49,50,51}`, col 4 given its own leaf header in the
   "excluded" cases and header-empty in the "absorbed" cases — built as a probe *before* the plan.
2. **Silent-wrong closed:** with an independent leaf header on col 4, `w=40/49/50` no longer
   silently resolves to `[1,2,3,4]`; it resolves to `[1,2,3]` (corroborated-excluded) or escalates
   `MERGE_AMBIGUOUS` — never asserts the over-absorption.
3. **No-regression:** the pivot's "Prior Visit" header (cc=5, lc=4, rc=5 → extends to col 6) still
   resolves correctly; `w=51` (comparable-width standalone) still excluded.
4. **Gate-pin (the neurosymbolic-gate enforcement reviewers check):** assert that neither the
   `0.25·pitch` tie-band nor the `0.5·pitch` centering tolerance is the *decider* in the flank case —
   perturbing them does not change the flank resolution, which is driven by the proposer +
   corroboration. A `FakeProposer` returning the wrong run must be *rejected* (corroboration
   disagrees) → escalation, proving the oracle disposes rather than the model dictating.

### 2.6 What stays PROCEDURAL (honestly bounded — do not over-semanticize)

`_word_in_column` / `column_of` containment, `_median_pitch` measurement, `_span_center` endpoint
geometry, and the exact ink-extent read — these are raw geometry/extraction feeding the evidence and
the tie-band *detection*, not deciding the span. They remain procedural and are documented as such in
the code (each states why it is irreducible to AXIOM/NEURAL).

### 2.7 Scope boundary (YAGNI)

- Only the **tied narrow-flank case** (one flanking column, narrower than half the median pitch,
  inside the tie-band) routes through the proposer. General merged-header span (`_covers_for_cell`,
  audit C2) is loop **B2**, not this slice.
- No new escalation control flow — reuse `MERGE_AMBIGUOUS`.
- The live BAML path stays env-gated (`BAML_LIVE`) and lazy; all tests run offline via `FakeProposer`
  (the existing `propose.py` discipline).
- Deferred minors carried from B1.1 (typing `repair_coverage`'s `grid: LeafGrid | int`, the
  `_tree_of` `StopIteration` message) are **out of scope** here unless touched incidentally.

### 2.8 Definition of done (the loop CLOSES)

- The narrow-standalone-column fixture proves the silent-wrong is closed end-to-end (resolve or
  escalate, never silent over-absorb), and no B1.1 fixture regresses.
- The gate test pins that no geometric constant and no confidence threshold decides the flank case.
- The deferred B1.2 item is retired (link updated in the deferred doc / CLAUDE.md §8 exemplar list).
- Residue (genuinely ambiguous flanks) is escalated in-band as `MERGE_AMBIGUOUS`, never dropped.
