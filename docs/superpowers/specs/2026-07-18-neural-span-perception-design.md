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
| **B1.2** | narrow-flank exclusion by **level-corroboration** — **SLICE 1 (this spec)**, an **AXIOM** (see §2 note) | C3 | header-cell SPARQL derivation + `region_tiles` SHACL guard; header-empty tied flank → escalate |
| **B1.3** | header-empty tied flank — the **NEURAL residual** deferred from B1.2 | C3 | BAML `ProposeHeaderSpan` proposes absorb/exclude; `region_tiles` disposes; else escalate |
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

## Part 2 — Slice 1: narrow-flank exclusion by level-corroboration (loop B1.2)

### 2.0 Design note — this slice is an AXIOM, not NEURAL (the gate-classification decision, 2026-07-18)

Scoping the slice surfaced a gate-classification correction. The distinguishing signal between the
two look-alike cases — *(a)* the pivot (`"Prior Visit"` spanning cols 4–6, where col 6 carries its
own **sub**-header yet genuinely belongs under the parent → **absorb**) and *(b)* the documented
silent-wrong (a narrow standalone col 4 that has its own leaf header and is **not** under the parent
→ **exclude**) — is **not** a lexical "own header token" test (that can't tell them apart and would
break the pivot). It is a **structural** signal: *the level (header row) at which the flank's own
header sits.* A flank whose own header is at the **spanning node's level** is a **sibling leaf**
(exclude `[1..k]`); a flank whose only header is at a **deeper level** (or is header-empty) is a
**child/empty** and is out of this slice.

Because that signal is structural and declarative over the header-cell graph, the correct
classification (CLAUDE.md §8: *do not reach for NEURAL where an AXIOM suffices*) is **AXIOM**, and it
**closes the documented silent-wrong on its own** (the deferred repro's col 4 has its own leaf
header → now excluded structurally). NEURAL is genuinely needed only for the **residual** — a flank
that is **header-empty at the spanning node's level** where geometry ties, so nothing structural
decides — which is deferred to loop **B1.3** (§2.8). This slice ships the AXIOM and **escalates** the
residual; it introduces **no BAML**.

### 2.1 The decision (one sentence)

When a spanning (multi-column, non-leaf) header's centered run is geometrically **tied** between
covering leaf columns `[1..k]` and `[1..k+1]` — because a flanking column narrower than half the
median pitch shifts the endpoint center by less than `_centered_run`'s `0.25·pitch` tie-band — decide
whether that flanking column is a **parentless sibling leaf** (exclude → `[1..k]`) using the level of
its own header, and otherwise **escalate** (defer to B1.3) rather than silently over-absorb.

### 2.2 Why the *resolution* is an AXIOM (the gate justification — stated in code and spec)

Both rival runs sit inside `_centered_run`'s `0.25·pitch` tie-band **and** inside `merge_tiling_ok`'s
`0.5·pitch` centering tolerance (`src/iladub/etkl/headers.py:218,279`) — geometry and the current
centering check are **both blind** to the 3-vs-4 call; the tie-band exists *because geometry cannot
decide*, so the `0.25`/`0.5` constants must not be the decider (CLAUDE.md §8). But the decision is
**not** perceptual: the discriminator is a **declarable fact over the header-cell evidence graph** —
*does column `k+1` bear a header cell at the spanning node's level?* That is an open-world SPARQL
derivation (grow the "flank is an independent same-level leaf" verdict from evidence that is
**present**), exactly the loop-B/B2a/B2c pattern. The tie **detection** (geometry) stays PROCEDURAL;
the tie **resolution** is the AXIOM.

Reproduction (from the deferred doc), boundaries `[0,100,200,300,400,400+w]`, `median_pitch=100`,
band `=25`:

```
col4 width 40 / 49 / 50  -> today: GROUP resolves to [1,2,3,4]  (col 4 SILENTLY over-absorbed, asserted)
col4 width 51            -> today: GROUP resolves to [1,2,3]    (correct; col 4 a parentless leaf)
```

### 2.3 The seam (an AXIOM derivation over a header-cell evidence graph — the loop-B2a/B2c pattern)

Mirrors the shipped evidence-graph axioms (`celltype` / `classifygraph` + a `vocab/queries/*.rq`
SELECT read by a thin Python reader), **not** the A2.1 proposer pattern (no BAML in this slice).

**Step 1 — Evidence graph (thin, per resolving band).** Build a transient RDF graph of the header
cells: for each populated header cell, a `tab:HeaderWord`-style node carrying `tab:atColumn` (the
strict-containment column, via the existing `column_of`) and `tab:headerLevel` (its header row index,
top-to-bottom). Reuse `classifygraph`'s construction style; add only the level. This is a fresh graph
per band (the **band is the closure boundary** — query-local `NOT EXISTS`/`COUNT` stay holon-scoped).

**Step 2 — The derivation (SPARQL SELECT, open world).** New `vocab/queries/flank-sibling.rq`:
a `SELECT ?col` returning every leaf column that **bears its own header cell at a given
`?spanLevel`** (bound by the reader to the spanning node's level). Open-world and evidence-positive:
a flank is named a sibling only when its same-level header cell is *present* — never inferred from
absence. (Absence → the residual → escalate, per §2.0/§2.8.)

**Step 3 — Reader + resolution.** A thin reader (in `headers.py`, beside `repair_coverage`) that,
for a tie-band narrow-flank node:
- runs `flank-sibling.rq` for the flank column at the spanning node's level;
- **flank is a same-level sibling** → resolve the node to `[1..k]` (exclude the flank; the flank
  stays a parentless leaf) — **closes the silent-wrong**;
- **flank is not a same-level sibling** (header-empty at that level) → **escalate `MERGE_AMBIGUOUS`**
  (the B1.3 residual; never silently absorb).

**Step 4 — Structural guard (`region_tiles`, loop-C SHACL).** The resolved header tree is validated
by the already-shipped `tiling.region_tiles` (Coverage/NoOverlap/Refinement/Unambiguous-leaf-access)
before assertion — a closed-world membrane check that the exclusion produced a legal tiling. This is
the **constraint** half of the open/closed split; the derivation grows the tree, the SHACL certifies
what crosses.

### 2.4 Where it plugs in

`repair_coverage` (`headers.py:225`) calls `_centered_run` for every coarse node; `_centered_run`
continues to resolve the unambiguous case unchanged (fast path). The change: when `_centered_run`'s
winning run is inside the tie-band with a rival that differs by **exactly one flanking column narrower
than `0.5·pitch`**, route that node through the Step-3 reader. A same-level-sibling flank resolves to
the exclude run; otherwise the node is marked ambiguous.

Ambiguity surfaces through the **existing** `MERGE_AMBIGUOUS` seam: `HeaderNode` gains an
`ambiguous: bool = False` field; `merge_tiling_ok` (already the compile-level `MERGE_AMBIGUOUS` gate
at `compile.py:201`) returns `False` if any node is `ambiguous`. No new control flow — the slice
reuses the shipped escalate path; it only makes the tie-band resolve *correctly* (exclude) or
*escalate* instead of silently over-absorbing.

### 2.5 The gate test (anti-overfit — mirrors `test_transform_gate.py` / celltype / classifygraph gate)

New `tests/etkl/test_span_gate.py`, built **regression-fixture-first** (probe → plan → adversarial
review — the discipline that caught the median silent-wrong and the nameless-pivot routing):

1. **Regression fixture FIRST:** the narrow-standalone-column layout —
   `[0,100,200,300,400,400+w]`, `w ∈ {40,49,50,51}`, with col 4 given its **own same-level leaf
   header** (the silent-wrong case) — built and probed *before* the plan.
2. **Silent-wrong closed:** with a same-level header on col 4, `w=40/49/50` no longer silently
   resolves to `[1,2,3,4]`; it resolves to `[1,2,3]` (the flank excluded as a sibling leaf).
3. **Residual escalates:** the same layout with col 4 **header-empty at the span level** escalates
   `MERGE_AMBIGUOUS` — never silently absorbs (the B1.3 residual is deferred, not guessed).
4. **No-regression:** the pivot's `"Prior Visit"` header (cc=5, lc=4, rc=5 → extends to col 6, whose
   own header is a **deeper** level) still resolves correctly; `w=51` (comparable-width standalone)
   still excluded.
5. **Gate-pin (the neurosymbolic-gate enforcement reviewers check):** assert that neither the
   `0.25·pitch` tie-band nor the `0.5·pitch` centering tolerance is the *decider* in the flank case —
   perturbing them does not change the flank resolution, which is driven by the `flank-sibling.rq`
   verdict over the header-cell graph, not by a constant. (Parity with the `classifygraph` gate:
   pin that the `.rq` + reader carry the decision, no tuned constant in the resolution path.)

### 2.6 What stays PROCEDURAL (honestly bounded — do not over-semanticize)

`_word_in_column` / `column_of` containment, `_median_pitch` measurement, `_span_center` endpoint
geometry, the exact ink-extent read, and the **tie-band detection itself** — raw geometry/extraction
feeding the evidence graph and *triggering* the resolver, not *deciding* the span. They remain
procedural and each states in-code why it is irreducible to AXIOM. The evidence-graph builder and the
SPARQL runner are PROCEDURAL engine-glue (the `classifygraph`/`celltype` precedent).

### 2.7 Scope boundary (YAGNI)

- Only the **tied narrow-flank case** (one flanking column, narrower than half the median pitch,
  inside the tie-band) routes through the reader. General merged-header span (`_covers_for_cell`,
  audit C2) is loop **B2**, not this slice.
- **No BAML, no proposer, no confidence** in this slice — it is an AXIOM. The `ProposeHeaderSpan`
  seam belongs to loop **B1.3** (§2.8).
- No new escalation control flow — reuse `MERGE_AMBIGUOUS` via the `ambiguous` flag.
- Deferred minors carried from B1.1 (typing `repair_coverage`'s `grid: LeafGrid | int`, the
  `_tree_of` `StopIteration` message) are **out of scope** here unless touched incidentally.

### 2.8 The deferred NEURAL residual (loop B1.3 — its own spec later)

When the tied flank is **header-empty at the spanning node's level**, nothing structural decides
absorb-vs-exclude. That residual is the genuine NEURAL case: BAML `ProposeHeaderSpan` reads the
spanning label + neighbouring leaf labels + ink extent and *proposes*; `region_tiles` disposes;
confidence never promotes; no confident legal reading → escalate `MERGE_AMBIGUOUS`. B1.2 **escalates**
this case (safe, honest), so B1.3 is a pure capability add with no silent-wrong to unwind.

### 2.9 Definition of done (the loop CLOSES)

- The narrow-standalone-column fixture proves the silent-wrong is closed end-to-end: a same-level
  flank resolves to `[1,2,3]` (excluded), a header-empty flank escalates `MERGE_AMBIGUOUS` — never a
  silent over-absorb — and no B1.1 fixture regresses.
- The gate test pins that no geometric constant decides the flank case (the `.rq` + reader do).
- The deferred B1.2 item is retired (link updated in the deferred doc / CLAUDE.md §8 exemplar list),
  and the header-empty residual is recorded as loop B1.3.
- Residue (header-empty tied flanks) is escalated in-band as `MERGE_AMBIGUOUS`, never dropped.
