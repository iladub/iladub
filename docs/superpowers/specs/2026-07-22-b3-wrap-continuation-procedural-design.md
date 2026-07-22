# B3 Wrap-Continuation — retire the tuned `0.9·lead` margin (PROCEDURAL)

**Date:** 2026-07-22
**Status:** Design — approved for spec (brainstorm 2026-07-22).
**Slice:** Retire the fixture-tuned wrap-continuation constant in `group_wrapped`. Honestly classified
**PROCEDURAL**, not NEURAL — see §2.

**Gate context (CLAUDE.md §8):** the audit (`2026-07-14-recovery-layer-neurosymbolic-audit.md` C5) tagged
`infer_header_tree` wrap-continuation as the header family's *strongest "tuned to the document"* constant
(`gap < lead * 0.9`, docstring reasoned in fixture point-magnitudes 14/12.6/13/18/16.2 pt). The roadmap
pencilled it in as a NEURAL slice (B3). **Empirical scoping disproved that classification** — see §2.

---

## 1. The decision (one sentence)

In `group_wrapped` (`src/iladub/etkl/cells.py`), replace the tuned margin `gap < lead * 0.9` with the
un-margined adaptive test `gap < lead` — the wrap-vs-row-pitch boundary is the document's own median
inter-line gap (`lead`), a derived statistic with **no magic constant** — keeping the two sound
structural conditions (subset-columns, partial-row) that already gate a continuation.

## 2. Why PROCEDURAL, not NEURAL (the gate justification — the B1.2 lesson repeats)

The roadmap listed B3 as a NEURAL propose→oracle→dispose slice. Scoping it against the real code + a
probe **disproved that**, mirroring B1.2's finding (*don't reach for NEURAL/AXIOM where existing
structure already suffices*):

1. **The tuned part is only the `0.9`.** `group_wrapped` merges line *j* into the anchor iff **three**
   conditions hold: (a) `gap < lead * 0.9`; (b) every word on *j* sits in an already-open column
   (`cols_j ⊆ open`); (c) *j* occupies fewer columns than the anchor (`len(cols_j) < len(anchor)`).
   Conditions (b) and (c) are **sound structural tests** (subset + partial) — not tuned. Only the
   `0.9` margin is a fixture-tuned tolerance.

2. **An adaptive statistic already suffices (probed, zero-regression).** Replacing `lead * 0.9` with
   `lead` passes **all** header/hierarchical/span/merge fixtures (28/28). `lead` is the median of the
   document's own gaps — adaptive, like the already-accepted-PROCEDURAL `_median_pitch`. The magic
   `0.9` is **not** load-bearing.

3. **Removing the gap entirely regresses (the gap IS load-bearing).** Probed: dropping the gap gate
   collapses the pivot's 5 body rows into 2 (the while-loop over-pulls normal-pitch body rows as
   "continuations"). So an "oracle-only, no gap" default is **unsound** — a gap signal is required.

4. **No sound oracle to make it NEURAL.** `region_tiles` cannot discriminate wrap-vs-distinct-level:
   a fragment merged into its parent, or promoted to a refining child level, **both tile**. So a model
   proposal here would be a guess admitted on legality alone (the confidence≠validity trap). Building a
   propose→oracle wrap-resolver would be **structurally redundant** (the adaptive gap decides it) and
   would need a *synthetic* residual fixture to justify — overfitting-in-reverse, forbidden by the
   project's no-overfitting rule.

**Conclusion:** the honest classification is **PROCEDURAL** — retire the tuned `0.9` with the adaptive
`lead`; keep conditions (b)/(c) as the sound structural filter. This is the third span-family slice
(after B1.2 and the B2 reconsideration) to collapse to "sound version is procedural / ambitious version
is gate-violating-or-synthetic," reinforcing that the sound NEURAL frontier is **not** table-span
perception but the iladub epistemic core (knowledge grounding) — pivot tracked separately (§5).

## 3. Honest tradeoff (recorded, not hidden)

The `0.9` margin also gave a mild **jitter guard**: it required a continuation to be *clearly* tighter
than the median (≤ 0.9·lead), so a body-row gap that noise nudges just under the median could not be
mis-merged. Dropping to `gap < lead` **relaxes** this — a gap in `[0.9·lead, lead)` now counts as a
continuation. On the shipped fixtures this never fires (body pitch **equals** `lead`, excluded by strict
`<`), hence zero regression; on a real document with jittery spacing a body gap slightly below the median
could in principle mis-merge. This is a **residual imperfection, not a silent-wrong class**: the median
is inherently jitter-robust (a few noisy gaps don't move it), the subset+partial conditions still guard,
and the downstream round-trip / tiling validation is the backstop (a mis-merge that breaks structure
escalates). We accept `gap < lead` as the minimal principled fix; a distribution-aware bimodal split
(continuation-cluster vs pitch-cluster) is a **deferred** refinement, only if a real jittery document
demonstrates the need (no synthetic fixture).

## 4. Change + tests

**Change (`src/iladub/etkl/cells.py`, `group_wrapped`):**
- The while-loop gate `(tops[j] - tops[j - 1]) < lead * 0.9` → `(tops[j] - tops[j - 1]) < lead`.
- Rewrite the docstring: remove the fixture point-magnitude reasoning and the false "the margin is
  structural, not tuned" claim; state the §8 classification (PROCEDURAL: adaptive `lead`, no tuned
  constant), name conditions (b)/(c) as the sound structural filter, and record the §3 tradeoff.

**Tests (`tests/etkl/test_wrap_continuation.py`, new):**
1. **Constant-free regression (the fix):** the pivot band (`pivoted_table_pdf`) still yields 5 body
   rows and 2 merged parents through `classify_hierarchical` — i.e. `gap < lead` preserves the shipped
   grouping. (RED-check: the probe already proved dropping the gap entirely gives 2 rows; this pins that
   `gap < lead` does *not* collapse.)
2. **Wrap still absorbed:** a fixture with a tight partial sub-line (a `(SI)`-style continuation, gap
   `< lead`) merges into its anchor cell (one leaf, not an extra level).
3. **Distinct row not absorbed:** a full-pitch partial line (gap `== lead`) is NOT merged (strict `<`),
   staying a distinct row — pins the boundary.
- Plus the full `tests/etkl` suite stays green (the real no-regression proof).

## 5. Pivot (tracked, separate brainstorm)

The genuine NEURAL layer pivots **away** from table-span perception (oracle-poor: B1.2 procedural, B2
≈already-done-or-gate-violating, B3 procedural) to the **iladub epistemic core**, where the contract
*verifies* (a sound oracle). Candidate first NEURAL-grounding slices (from the knowledge-grounding
follow-ups, `2026-07-19-knowledge-first-grounding-design.md`): **(a)** wire the ET(K)L table /
M4-extraction output as the concept **feed** into `ground_or_propose`; **(b)** extend contract-disposal
to fields with **value-constraining shapes** (datatype + pattern/enum), not just SKOS schemes. Scoped in
its own brainstorm next.

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
