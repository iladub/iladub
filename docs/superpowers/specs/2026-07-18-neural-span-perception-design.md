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
| **B1.2** | narrow-flank orphan tie → **escalate** — **SLICE 1 (this spec)**, a **PROCEDURAL** honest-escalate (see §2.0 rework note; shipped as a tie-detect→escalate, **not** an AXIOM) | C3 | none — geometry *detects* the tie, escalates `MERGE_AMBIGUOUS`; B1.1 `repair_coverage` already handles sibling/orphan protection |
| **B1.3** | resolve an escalated narrow-orphan flank (absorb-under-span vs standalone leaf) — the **NEURAL residual** deferred from B1.2 | C3 | BAML `ProposeHeaderSpan` proposes; `region_tiles` disposes; else escalate |
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

## Part 2 — Slice 1: narrow-flank orphan tie → escalate (loop B1.2, PROCEDURAL)

### 2.0 Design note — what implementation taught us: this slice is PROCEDURAL, not an AXIOM (2026-07-18)

This slice was **designed as an AXIOM** (a header-cell SPARQL derivation, `flank-sibling.rq`, deciding
"is the tied flank a same-level sibling → exclude, or header-empty → escalate"). Building it and
gate-testing it end-to-end **disproved that classification**, and the slice was deliberately
simplified. The decision trail is kept here because the reasoning is the point.

**What the AXIOM was going to decide, and why it turned out redundant.** The intended discriminator
was *the level at which a tied flank has its own header* — same level → sibling (exclude), deeper →
child (absorb), none → orphan (escalate). But B1.1's shipped `repair_coverage` **already** answers
sibling-vs-orphan: its per-level "orphan" set (`avail = own covers | {columns no node at this level
covers}`) structurally **never absorbs a column that has its own same-level header** — a genuine
same-level sibling is, by construction, *not an orphan*, so `_centered_run` can never pull it into the
span. The gate test's RED-check confirmed it: disabling the resolver changes **only** the
header-empty (orphan) case; the "exclude a same-level sibling" branch is **unreachable through the
full `infer_header_tree` pipeline** and fires only if the resolver is called directly.

Consequently the SPARQL sibling-derivation could only ever re-derive a fact `repair_coverage` had
already used — it was **structurally redundant**, always returning "not a sibling" for any flank that
actually reached it (those are all orphans). Making it the *active* decider would have required
tearing out `repair_coverage`'s procedural protection and reimplementing it declaratively — but
`level_cols` (which protects columns under a **spanning** parent that have no own leaf header) is
**not** equivalent to `sibling_columns` (strict-in-column leaf headers only), so a clean swap
**regresses the pivot**. Reworking that safely is real surgery on shipped, correct B1.1 code to close
a **synthetic** silent-wrong (surfaced by review, reproduced only with hand-built geometry).

**The gate-classification lesson (the mirror of §8's NEURAL rule).** Just as §8 says *don't reach for
NEURAL where an AXIOM suffices*, the corollary holds: **don't reach for an AXIOM where existing
structure already suffices.** Here the honest classification is **PROCEDURAL** — geometry *detects*
an ambiguity the tie-band cannot resolve, and the slice **escalates** (honest failure > fake success)
instead of silently over-absorbing. No evidence graph, no SPARQL, no BAML.

### 2.1 The decision (one sentence)

When a spanning (multi-column, non-leaf) header's centered run over-absorbs a **narrow flanking
column that the label's raw ink does not reach** (an endpoint column narrower than half the median
pitch, inside `_centered_run`'s `0.25·pitch` tie-band), **escalate `MERGE_AMBIGUOUS`** rather than
silently assert the over-absorbed span — because geometry provably cannot decide whether that orphan
flank belongs under the span, and B1.1 already protects genuine same-level siblings.

### 2.2 Why it is PROCEDURAL escalate (the gate justification — stated in code and spec)

The over-absorbed rival runs both sit inside `_centered_run`'s `0.25·pitch` tie-band **and** inside
`merge_tiling_ok`'s `0.5·pitch` centering tolerance (`src/iladub/etkl/headers.py`) — geometry is
**blind** to whether the orphan flank belongs under the span. There is no *symbolic* fact that decides
it (a header-empty orphan has no evidence to derive from — deriving "it belongs / it doesn't" from the
*absence* of a header would violate §7, assert only what the source supports), and it is not (yet) a
perceptual NEURAL slice. The only honest action is to **stop and escalate**: mark the node ambiguous
so the existing `MERGE_AMBIGUOUS` seam quarantines the region rather than asserting a guess. The
tie **detection** (`_narrow_flank_tie`: median pitch, tie-band, raw ink extent) is irreducibly
PROCEDURAL geometry, and it does not *decide* the span — it only recognizes that geometry can't.

Reproduction (from the deferred doc), boundaries `[0,100,200,300,400,400+w]`, `median_pitch=100`,
band `=25`:

```
col4 width 40 / 49 / 50  -> BEFORE: GROUP silently resolves to [1,2,3,4]  (orphan col 4 over-absorbed, asserted)
                            AFTER : node marked ambiguous -> region escalates MERGE_AMBIGUOUS (never silently asserted)
col4 width 51            -> unchanged: [1,2,3] (comparable-width flank correctly left out by B1.1)
```

### 2.3 The seam (procedural detect → escalate; reuses the shipped `MERGE_AMBIGUOUS` path)

Two small pieces in `src/iladub/etkl/headers.py`, plus the shipped escalation seam:

**`_narrow_flank_tie(covers, ink_cols, b) -> int | None`** — PROCEDURAL geometry. Returns the single
endpoint flank column that `covers` includes, the node's raw ink does **not** reach, and that is
narrower than `0.5·_median_pitch` (so it sits inside the tie-band). `None` otherwise. This is tie
*detection*; each constant is documented in-code as detection geometry, not a span decision.

**`resolve_narrow_flanks(nodes, grid, ink_cols_by_node) -> list[HeaderNode]`** — for each coarse node
with geometry, if `_narrow_flank_tie` fires, mark the node `ambiguous=True`. That's it: **detect →
escalate**. No sibling derivation, no header-cell graph, no per-flank query.

**Escalation** rides the **existing** `MERGE_AMBIGUOUS` seam: `HeaderNode.ambiguous: bool = False`;
`merge_tiling_ok` (the compile-level gate at `compile.py:201`) returns `False` if any node is
`ambiguous`; the region escalates in-band exactly as the shipped centering/overlap failures already
do. No new control flow. (The parent-linking reconstruction in `infer_header_tree` must carry the
`ambiguous` field through — otherwise escalation is a silent no-op; this was fixed during Task 5.)

### 2.4 Where it plugs in

`infer_header_tree` (`headers.py`) builds nodes, runs `repair_coverage` (B1.1 centering, unchanged),
then calls `resolve_narrow_flanks(nodes, grid, ink_cols_by_node)` before parent-linking.
`ink_cols_by_node` is built positionally aligned with `nodes` (same `for lvl, row in
enumerate(header_rows): for cell in row:` order; verified — `repair_coverage` only ever `replace()`s
in place, never reorders). Unambiguous spans pass through untouched; only a detected narrow-flank
orphan tie flips a node to `ambiguous`.

### 2.5 The gate test (anti-overfit — `tests/etkl/test_span_gate.py`)

Built **regression-fixture-first** (probe the real pipeline before asserting). Because `infer_leaf_grid`
needs ≥~48 data rows to resolve the 5-column grid **and** the shipped `header-body-split.rq` is
super-linear in row count (see §2.7 note), the fixture infers the grid on a wide (~60-row) band and
runs split/tree on a small band sharing the identical column layout (a `LeafGrid` is an immutable
value; this is sound reuse, not a weakened test).

1. **Silent-wrong closed (the real proof):** a narrow **orphan** flank (`w=25` real-resolved,
   header-empty at the span level) makes the coarse node `ambiguous=True` and the region escalate
   `MERGE_AMBIGUOUS` — it is **never** silently asserted as `[1,2,3,4]`. Proven non-vacuous by a
   RED-check: disabling `resolve_narrow_flanks` makes exactly this test fail.
2. **No-regression:** a wide standalone flank (real width > `0.5·pitch`) is untouched; the multi-level
   pivot (`"Prior Visit"`, deeper-level sub-headers) still resolves; all shipped `test_headers.py` /
   `test_hierarchical.py` fixtures stay green.
3. **Detection-is-geometry, not a decision:** `_narrow_flank_tie` is unit-tested for the narrow / wide
   / ink-reaches cases directly, pinning that it fires only on the genuine tie.

(The earlier draft's "same-level sibling excluded" and "declarative decision" tests are **removed** —
the sibling case is handled by B1.1, not this slice, and there is no declarative decision to pin.)

### 2.6 What stays PROCEDURAL / justified (honestly bounded)

`_narrow_flank_tie` (`_median_pitch`, the `0.5·pitch` width test, the raw ink-extent read) is tie
*detection* geometry — it recognizes that the tie-band cannot decide and hands off to escalation; it
never asserts a span. `_word_in_column` / `column_of` / `_span_center` are unchanged raw geometry.
There is **no AXIOM and no NEURAL** in this slice by design — the honest decision is "escalate on
detected ambiguity."

### 2.7 Scope boundary + carried notes (YAGNI)

- Only the **tied narrow-flank orphan** case (one endpoint column, narrower than half the median
  pitch, ink-unreached) flips a node to ambiguous. General merged-header span (`_covers_for_cell`,
  audit C2) is loop **B2**.
- **No BAML, no SPARQL, no evidence graph, no confidence** — this slice is procedural detect→escalate.
- No new escalation control flow — reuse `MERGE_AMBIGUOUS` via the `ambiguous` flag.
- **Carried for a follow-up (out of scope here):** `header-body-split.rq` (shipped B2a) is
  **super-linear in band row count** (empirically hangs past ~15 rows via rdflib's nested
  `FILTER (NOT) EXISTS`) — a latent performance risk for any real spanning-header table with ~15+
  rows in `compile_tables`. Discovered while building the B1.2 gate fixture; a separate B2a
  performance loop.

### 2.8 The deferred NEURAL residual (loop B1.3 — its own spec later)

B1.2 **escalates** every detected narrow-orphan-flank tie (safe, honest). Loop **B1.3** is the genuine
NEURAL slice that *resolves* those escalations: for a header-empty tied flank, BAML `ProposeHeaderSpan`
reads the spanning label + neighbouring leaf labels + ink extent and *proposes* absorb-vs-standalone;
`region_tiles` disposes; confidence never promotes; no confident legal reading → stay escalated. B1.2
leaves a clean, quarantined input for it (no silent-wrong to unwind).

### 2.9 Definition of done (the loop CLOSES)

- The narrow-orphan-flank fixture proves the silent-wrong is closed end-to-end: the node is marked
  `ambiguous` and the region escalates `MERGE_AMBIGUOUS` — never a silent over-absorb — and no B1.1
  fixture regresses. RED-check proves the escalation test is non-vacuous.
- The slice is honestly classified PROCEDURAL (detect→escalate); no AXIOM/NEURAL machinery ships.
- The deferred B1.2 item is retired (link updated in the deferred doc), and the header-empty
  resolution is recorded as the NEURAL loop **B1.3**.
- Residue (narrow-orphan tied flanks) is escalated in-band as `MERGE_AMBIGUOUS`, never dropped.
