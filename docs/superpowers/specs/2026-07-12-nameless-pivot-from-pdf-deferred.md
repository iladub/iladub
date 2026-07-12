# Deferred: end-to-end nameless-pivot recovery from a PDF

**Date:** 2026-07-12
**Status:** DEFERRED to its own loop. Attempted inside the A2.1 showcase task; reverted after an
adversarial review found a silent-wrong cross-tab regression.

## Why this exists

Loop A2.1 (GenAI-proposed pivot dimension names) is validated on **constructed graphs** where a column
pivot already has `name=None`. Its *showcase* wanted to demonstrate the same end-to-end from a **PDF**. But
the compiler does not currently recover a nameless pivot from a PDF: a layout like `Product | Q1 Q2 Q3 Q4`
(blank spanning header over the quarter columns) is grabbed by the **matrix/cross-tab classifier** (Loop 6),
and Voronoi proximity assigns the stub word ("Product") as the column-group name — so `recover_dimensions`
returns `name='Product'` (and A1 emits base facts) instead of `name=None`.

A showcase subagent made 4 core changes to fix this out of process. An adversarial review returned **FAILS**.

## The real finding (do NOT lose this)

The naive discriminator is **silent-wrong**. A legitimate cross-tab whose corner caption sits on its own
top physical line —

```
Region
           Q1              Q2
        Rev Cost Unit   Rev Cost Unit
North   100  60  5      110  65  6
South   120  70  7      130  75  8
```

— compiles to a correct 2-D matrix on `main` (score 1.0, SHACL conforms), but the attempted change
downgraded it to a **1-D structure that was *asserted, not escalated*** (score 0.609): the North/South row
dimension is destroyed, and it still passes SHACL. Root cause: `is_matrix_candidate` inspected only
`band.lines[0]` and required a data-range word there; a corner-only top line (common in PivotTables, and
triggerable by baseline/font jitter) fails that test. `infer_column_tree_by_proximity`'s stub-word
exclusion broke the same case independently.

## What was clean (reusable when this is done properly)

- **`repair_coverage` synthetic-nameless-node second pass** — groups orphan columns into a
  `HeaderNode(text="", covers=orphans)`. Byte-identical recovery on every existing fixture; a true no-op
  when the tree already tiles. Provenance-correct.
- **`assert_hier_region` skips the LabelCell for empty-text nodes** — a synthetic nameless span has no page
  label, so emitting one would fabricate provenance. SHACL conforms (no shape mandates `tab:hasLabel`).
- Two fresh nameless-pivot layouts (Product×Q1–Q4, Store×Jan/Feb/Mar) recover `name=None` and A2 names them
  — so the capability is achievable and general, not overfit.

## The fix a proper loop must implement

1. `is_matrix_candidate` must test whether any column-group header word **across all header lines above the
   body split** (`band.lines[:split]`), not just `band.lines[0]`, sits over the data range.
2. The stub-word exclusion in `infer_column_tree_by_proximity` must be applied **per-level** while still
   permitting the row axis to be recovered — never null the whole col-tree because only the *topmost* level
   is a corner caption.
3. **Any** nameless-pivot detection that would degrade a 2-D cross-tab to 1-D must **escalate**
   (`MATRIX_AMBIGUOUS`), never silently assert a 1-D structure.

Do this as its own loop: brainstorm → probe (build the corner-on-own-line cross-tab as a regression fixture
FIRST) → plan → adversarial review. The A2.1 showcase (Part J) lands once this ships.

Known pre-existing limitation (NOT caused by any of this): a **numeric-labeled** nameless pivot
(Country × 2019–2023) fails to recover and violates CoverageShape on `main` too — a separate numeric-header gap.
