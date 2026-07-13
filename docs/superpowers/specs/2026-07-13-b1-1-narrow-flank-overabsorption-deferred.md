# Deferred (B1.2): narrow-flank over-absorption in centering-bounded merge resolution

**Date:** 2026-07-13
**Status:** DEFERRED to a follow-up loop (B1.2). Surfaced by the Loop B1.1 final whole-branch
review; not a blocker for B1.1 (no regression vs `main`), recorded here so it is not lost.

## The residual

Loop B1.1 resolves a merged (spanning) header to the contiguous column run whose ENDPOINT
center best matches the label's ink center, breaking near-ties (within a quarter of the median
column pitch) toward the widest run (`_centered_run` in `src/iladub/etkl/headers.py`).

Absorbing one more flanking column shifts a run's endpoint center by `(that column's width)/2`.
The tie-band therefore admits — and `merge_tiling_ok` then blesses (the shift stays under its
half-pitch centering tolerance) — any adjacent **standalone column narrower than half the median
pitch**. Such a column is silently folded into the group and asserted, with no `MERGE_AMBIGUOUS`
escalation.

Reproduced (boundaries `[0,100,200,300,400,400+w]`, cols 1-3 width 100, standalone col 4 width `w`,
`median_pitch=100`, band=25):

```
col4 width 40 / 49 / 50  -> GROUP resolves to [1,2,3,4]   (col 4 over-absorbed, asserted)
col4 width 51            -> GROUP resolves to [1,2,3]     (correct; col 4 a parentless leaf)
```

## Why it is NOT a B1.1 blocker

`main`'s greedy `repair_coverage` absorbed an adjacent orphan of **any** width, so `main` produces
`[1,2,3,4]` here too (and also for wide columns, which B1.1 now correctly rejects). B1.1 is
therefore **strictly better-or-equal** than `main`: it closes the median silent-wrong and the
comparable-/wider-width over-absorption, leaving only the narrow-flanking residual at `main`'s
level. It introduces nothing worse.

## The fix a proper B1.2 loop should implement

1. Bound absorption per-column: only absorb column `c` into a run if the label's ink extent
   actually reaches toward `c` (not merely if the endpoint center stays within the band), OR
2. When a would-be-absorbed flanking column is narrower than the band can distinguish and has its
   own leaf header, leave it a parentless leaf; if that makes the grouping genuinely ambiguous,
   ESCALATE `MERGE_AMBIGUOUS` rather than assert `[1,2,3,4]`.

Build the narrow-standalone-column layout as a regression fixture FIRST (probe → plan → adversarial
review), the same discipline that caught the median silent-wrong and the nameless-pivot routing.

## Also carried (deferred minors from B1.1 per-task reviews)

- `repair_coverage(nodes, grid)` — `grid` is annotated bare to admit the legacy `int` callers in
  `tests/test_headers.py`; type it `LeafGrid | int` in a cleanup.
- `_tree_of` test helper raises an opaque `StopIteration` if a fixture regresses to the matrix
  path; wrap with a clear assertion message.
