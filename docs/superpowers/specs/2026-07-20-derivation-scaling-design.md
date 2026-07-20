# SPARQL Derivation Scaling — make the table compiler handle real row counts

**Date:** 2026-07-20
**Status:** Design — approved (brainstorm 2026-07-20).
**Scope:** an efficiency reformulation of the shipped B2a/B2b cell-typing AXIOMs so the table
compiler scales to realistic report sizes. Same decisions, same results — **form, not semantics,
changes**. Prerequisite for compiling real human-made tabular reports (§0: *human-addressed*
tabular structure, not "unstructured"). No new capability, no vocab change.

## The problem (measured on `main`, 2026-07-20)

`header_body_split` is super-linear in band row count:

```
n=  5 rows → 0.9s      n= 10 rows → 7.4s      n= 15 rows → TIMEOUT >25s      n≥15 → hangs
```

Any hierarchical / grouped-header table with ~15+ rows **hangs `compile_tables`**. Real tabular
reports routinely have dozens of rows, so today the compiler cannot compile them at all. This is the
binding blocker between the current small-synthetic-fixture state and real reports.

## Root cause

`vocab/queries/header-body-split.rq` (and its vertical mirror `stub-data-split.rq`) contain:

1. **A cell-pair self-join** — `FILTER NOT EXISTS { ?ca …atGridColumn ?col… ; cellDatatype ?cat . ?cb …atGridColumn ?col… ; cellDatatype ?cbt . FILTER(?cat != ?cbt) }` compares **every pair of cells** in a column → O(cells²) per column.
2. **Per-candidate-split re-evaluation** — `?anycell tab:atGridRow ?s` binds once per cell-bearing row and the inner `EXISTS`/`NOT EXISTS` re-runs for each → the pair self-join runs O(rows) times.

Combined ≈ **O(n²·c²)**. `stub-data-split.rq` nests the same pair self-join inside two `NOT EXISTS`
blocks — the same cliff, worse constant.

## The fix — an equivalent aggregation form (linear in cells)

The homogeneity test *"column has no Text cell and no two cells of different `cellDatatype` on
`[s..end]`"* has a closed form that needs **no pair self-join and no per-split iteration**.

### `header-body-split.rq` — MIN body-start row

The decision: *MIN row `s ≥ 1` such that some column is homogeneous non-Text on `[s..end]`.* Per
column, let `T` = the `cellDatatype` of the column's **bottom** (max-row) cell:
- if `T = tab:Text` → the column never qualifies (its suffix always contains Text at the bottom);
- else the column's boundary is `s_col = 1 + MAX(row of any cell in the column whose type ≠ T)`
  (all cells at row ≥ `s_col` then share type `T`, non-Text). If no cell differs from `T`,
  `s_col` = the column's minimal cell row (≥1).

The answer is **`MIN(s_col)`** over qualifying columns. Equivalence: a column is homogeneous non-Text
on `[s..end]` for **all** `s ≥ s_col`, so `∃column homogeneous at s ⇔ s ≥ min_col(s_col)`; the MIN `s`
with the property is exactly `min_col(s_col)`. Realized as a `GROUP BY ?col` sub-`SELECT` computing
the per-column bottom type and `MAX` differing-row, then an outer `MIN` — **O(cells)**, no self-join.

### `stub-data-split.rq` — leading text-stub count k

The decision: *MIN `k ≥ 1` such that every column `≥ k` is a data column* (homogeneous non-Text body).
Reformulate with a per-column boolean `isData(col)` = `(bottom body-cell type ≠ Text)` **and**
`(COUNT(DISTINCT body cellDatatype) ≤ 1)` — computed per column by `GROUP BY` aggregation. Then the
data columns form a suffix and **`k = 1 + MAX(col ≥ 1 that is NOT isData)`** (or `k = 1` if none),
provided ≥1 data column exists. No nested `NOT EXISTS`, no pair self-join.

### Why this stays an AXIOM (§8)

The rewrite changes the query's **form, not its decision**: still a declarative SPARQL derivation
over the same `tab:` cell-typing evidence graph, no tuned constant, no procedural leakage. It is a
pure efficiency reformulation of shipped axioms.

## Semantics guard — equivalence is oracle-pinned, not assumed

The shipped **celltype differential oracle** (`tests/etkl/test_celltype.py`, the frozen-Python `_ref_`
battery) and the B2a/B2b query tests pin `header_body_split` / `stub_data_split` to **byte-identical**
results. The rewrite must keep every one of those green — that IS the equivalence proof. Additionally,
a **randomized differential test**: for a battery of generated typed-cell grids (varied rows/cols/type
mixes incl. Date/Currency/Text and all-Text/ragged edge cases), assert the new query returns the
**same** value as the current query on every grid (run the *old* query text as the reference). This
catches any divergence the fixed fixtures miss, before the old query is deleted.

## The audit — profile every derivation, fix any other cliff

Profile each `vocab/queries/*.rq` against row count (n = 5/20/50/100 typed-cell grids), timing each:
`header-body-split`, `stub-data-split` (known cliffs); `classify-kind`, `looks-transposed`,
`transpose-coherent`, `recover-dimensions`, `name-levels`, `operand-exclusions`,
`unpivot-forward`/`-inverse`/`-inverse-valueset`, `strip-aggregation-forward-sum`. Any that is
super-linear in row count gets the same aggregation-form treatment (guarded by *its* differential
oracle / tests). Record the profile table in the plan; queries that are already linear (or run over
few header words, not body rows — e.g. `classify-kind` over `tab:HeaderWord`) are noted and left.

## Perf regression guard (so a future query can't silently reintroduce a cliff)

A new `tests/etkl/test_derivation_perf.py`: build a realistic typed-cell grid (**50 data rows**, a
grouped/spanning header, mixed body types) and assert each row-count-sensitive derivation returns in
under a wall-clock bound (e.g. **< 1.5s** each; generous enough to be machine-independent, tight
enough to catch an O(n²) regression). Uses the same `.venv` interpreter discipline.

## Definition of done (the loop CLOSES on a real-sized report)

- A realistic multi-row tabular report (**≈50 rows, grouped header**) that **hangs on `main`** now
  compiles end-to-end via `compile_tables` in reasonable wall-clock time — demonstrated by a test
  that builds/renders such a report and asserts it compiles (not escalates on timeout) with a sane
  score.
- `header-body-split.rq` and `stub-data-split.rq` (and any other cliff the audit finds) are the
  aggregation form; the **celltype differential oracle + all B2a/B2b tests stay green** (equivalence
  proof), plus the randomized differential test passes.
- The perf regression guard is in place.
- Full suite green via `./.venv/bin/python -m pytest` (baseline 406 passed / 5 skipped after the
  grounding loop merged; no regressions).
- **Gate (§8):** the derivations remain declarative AXIOMs — form-only change, no tuned constant, no
  procedural decision introduced.

## File structure (for the plan)

- **Modify** `vocab/queries/header-body-split.rq` — aggregation form.
- **Modify** `vocab/queries/stub-data-split.rq` — aggregation form.
- **Modify** (only if the audit finds them super-linear) other `vocab/queries/*.rq`.
- **Create** `tests/etkl/test_derivation_perf.py` — the profile-driven perf guard + the realistic
  end-to-end report compile.
- **Create/extend** a randomized differential test (in `test_celltype.py` or a new
  `tests/etkl/test_derivation_equiv.py`) — new query vs old query text on generated grids.
- **No change** to `celltype.py` / `rowheaders.py` readers, the evidence graph, or any vocab term —
  the queries read the same graph and return the same scalars; only the query bodies change.

## Scope boundary (YAGNI)

- **Efficiency only.** No new typing, no new decision, no capability change. If a rewrite would change
  any result on any fixture, it is wrong — stop and reconcile, do not "fix" the fixture.
- Real-PDF-messiness robustness (merged cells, borders, footnotes, fonts) is a **separate** later
  slice; this one removes the perf wall so such a slice can even run.
- The `strip-aggregation-forward-sum.rq` known single-strip limitation (documented, deferred) is out
  of scope; only its row-count scaling is profiled.
