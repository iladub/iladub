# Loop 6 · compile matrix / cross-tab tables — both axes at once

**Status:** design (approved 2026-07-09)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** Loop 2 (column-header tree: `headers.HeaderNode`, `infer_header_tree`, `assert_hier_region`) +
Loop 5 (row-header tree: `rowheaders.infer_row_header_tree`, `row_tree_tiles`, `tab:coversRow`, guarded row
shapes) + Loop 4 (shared entry emitters).

## Why this exists — the row axis of a cross-tab is unmodeled

A **matrix / cross-tab** has a hierarchical **column** header over the data columns *and* a **stub row axis**
down the left, with body cells at the cross-product `(column-path × row-path)`:

```
          Q1              Q2                <- column parents
     Rev  Cost  Unit  Rev  Cost  Unit       <- column leaves
North 100  60    5    110   65    6          <- stub row axis (flat)
South 120  70    7    130   75    8
```

**Probed on `main` today (2026-07-09):** this classifies as `UNSUPPORTED_TABLE` (merged header) and routes
to Loop 2's `classify_hierarchical`, which builds a column tree over the data columns **but leaves the stub
column (col 0) uncovered** — so `North`/`South` are lost (the stub becomes a phantom uncovered leaf column →
coverage failure / escalation, the row axis unmodeled). Both existing oracles are blind to it: the geometry
round-trips and the *column* SHACL never asks about a row axis.

This loop models the stub as a **row-header axis** and compiles the full 2-D holon.

## §1 — The composition (and the one new algorithm)

The vocabulary and SHACL are **already done** — Loop 2 gave `coversColumn` + column tiling shapes, Loop 5
gave `coversRow` + guarded row tiling shapes. A matrix is largely their **composition**: a column tree over
the data columns + a row tree over the stub columns, entries at `(data-col × leaf-row)`, certified by the
**union** of the existing shapes. **No new ontology, no new SHACL.**

**The one thing that does *not* compose (found by probing):** Loop 2's `infer_header_tree` recovers a merged
span from the parent label's **text extent**, so a *short* label (`Q1`) over a *wide* numeric group
**under-covers** — the probe showed `Q1` covering only its center column `(2,)` instead of `(1,2,3)`. Loop 2
sidestepped this with wide labels (`"Current Visit"`); real cross-tabs have short categorical labels
(`Q1`, `2023`, `M/F`). So the matrix needs a **proximity-based** column-span builder (below). This is the
loop's one genuinely new algorithm; Loop 2's builder is **not** touched.

## §2 — Scope & closing target

- **Closing target (settled 2026-07-09):** a hierarchical **column** header (`Q1`/`Q2` each over
  `Rev`/`Cost`/`Unit`) + a **flat stub** row axis (`North`/`South`) + a numeric data matrix →
  `tab:HierarchicalTable` with **both** a column tree (`coversColumn`) and a row tree (`coversRow`), entries
  at `(data-col × leaf-row)`, certified by the union of the column + row SHACL. A **grouped** stub composes
  for free via `infer_row_header_tree` but is a follow-up, not the proof fixture.
- **In scope:** the proximity column-span builder, matrix detection, the `assert_matrix_region` maker, the
  compile/escalate gate. **No** ontology/SHACL changes.
- **Out of scope (escalated / other loops):** a stub *with* a header label (that is Loop 2's covered-stub
  column-hierarchy — `stub_data_split` is `None` there, so it never enters this path); non-numeric measures;
  a matrix banded apart by large vertical gaps (that is the *multi-band* problem — the closing fixture is
  spaced to stay one band, exactly as Loop 2's pivot fixture is).

## §3 — Detection (reusing existing signals)

A region is a matrix candidate iff **all** hold (probe-confirmed values in brackets):

1. `classify(band).kind is UNSUPPORTED_TABLE` — a merged / multi-row column header (a flat header would be
   Loop 5's row-hier, handled in the `RECORD_TABLE` branch). [✓]
2. `header_body_split(band, grid) >= 2` — the column header genuinely has ≥ 2 levels. [2]
3. `stub_data_split(band, grid) is not None` — a clean **text-stub | numeric-data** split (Loop 5's
   function): the leading column(s) are the row axis, the trailing block are numeric data columns. [1]

This cleanly separates the three kinds (probe-confirmed):

| kind | classify | `stub_data_split` | stub covered by column tree? |
|---|---|---|---|
| Loop 2 column-hierarchy (pivot) | UNSUPPORTED | `None` (mixed data) | **yes** (`Analyte` header) |
| Loop 5 row-hierarchy | RECORD | not None | (flat column header) |
| **Loop 6 matrix** | UNSUPPORTED | **not None** | **no** (blank corner) |

The gate sits in the `UNSUPPORTED_TABLE` branch of `compile.py`, **before** `classify_hierarchical`.

## §4 — The proximity column-span builder (`matrix.py`)

`infer_column_tree_by_proximity(band, grid, split, data_cols) -> tuple[HeaderNode, ...] | None`

Reuses Loop 2's `headers.HeaderNode` dataclass. For each header level `L` (physical header line, top to
bottom = level 0..split-1):

- collect the level's labels as `(text, x_center)` from the words on that header line;
- assign **each data leaf column** to the **nearest** level-`L` label by `x_center` (Voronoi split at the
  midpoint between adjacent label centers) — this recovers the full span regardless of label width;
- a `HeaderNode` covers the contiguous run of data columns assigned to it (probe: `Q1 → {1,2,3}`,
  `Q2 → {4,5,6}`; `Rev/Cost/Unit → one each`);
- parent links: a level-`L` node → the level-`(L-1)` node whose covered columns ⊇ its own (mirrors
  `infer_header_tree`'s parent rule).

`None` if a level has no labels or the assignment is degenerate. Only the **data** columns are assigned; the
stub column(s) get no column-header node (they are the row axis).

**Why proximity, not text-extent (no overfitting):** proximity uses the *structural* fact that a centered
parent label marks the center of its span; nearest-center assignment is exact for any label width, whereas
text-extent recovery is a heuristic that only works when the label happens to be wide. This is a more robust
oracle, not a constant tuned to the fixture.

## §5 — `classify_matrix(band) -> MatrixRegion | None`

Chains the stages (mirror of `classify_hierarchical` / `classify_row_hier`):

1. `recover_leaf_grid` (ncols ≥ 3: ≥ 1 stub + ≥ 2 data, so the column header can be hierarchical);
2. `header_body_split` (≥ 2, else None);
3. `stub_data_split` → `k` (stub cols `[0..k-1]`, data cols `[k..ncols-1]`; None → not a matrix);
4. `infer_column_tree_by_proximity` over the data columns → `col_tree` (None → escalate);
5. `logical_rows` → `leaf_rows`;
6. `infer_row_header_tree` over the stub columns → `row_tree` (Loop 5; flat stub → degenerate one-node-per-row
   tree).

Returns `MatrixRegion(grid, col_tree, row_tree, leaf_rows, stub_cols, data_cols, body_line)`.

**Tiling backstop:** `matrix_tiles(col_tree, row_tree, data_cols, leaf_rows)` = the column tree partitions the
data columns (a column analog of `row_tree_tiles`) **and** `row_tree_tiles(row_tree, len(leaf_rows))`. Both
must tile → compile; else escalate `MATRIX_AMBIGUOUS`. The union of column + row SHACL is the final certifier
(a mis-inferred tree fails a shape → the pre-check escalates rather than letting `_validate` raise).

## §6 — `assert_matrix_region(g, mreg, band, table_uri, doc_uri, page) -> int` (`holon.py`)

Emits a `tab:HierarchicalTable` (composition of the two existing emission patterns):

- **data leaf columns** (`data_cols`): a `tab:LeafColumn` each; the **column** tree as `tab:HeaderNode`s
  (`headerLevel`, `coversColumn` → each covered data LeafColumn, `parentHeader`, `hasLabel` LabelCell with
  physical bbox/onPage — reusing the Loop 2 column-header emission).
- **leaf rows**: a `tab:LeafRow` per body row; the **row** tree as `tab:HeaderNode`s (`coversRow`,
  `parentHeader`, `hasLabel` from the stub cell geometry — reusing `assert_row_hier_region`'s row-header
  emission).
- **entries**: for each `(data column × leaf row)`, an `EntryCell` (`atColumn` data-leaf-col, `atRow`
  leaf-row) via the **shared `_emit_entry_cell`**; a straddling entry escalates `ROUND_TRIP_FAIL` via
  `_emit_roundtrip_fail_cell`.
- **corner / stub-head labels** (if any in the corner over the stub columns): carried as `tab:LabelCell`s on
  the table (context preserved). The canonical cross-tab has a blank corner.

Returns the asserted entry count. `assert_hier_region` (Loop 2) and `assert_row_hier_region` (Loop 5) are
untouched — the matrix maker composes their patterns without editing them.

## §7 — Gate placement (`compile.py`, `UNSUPPORTED_TABLE` branch)

Currently the branch tries `classify_hierarchical` (Loop 2) then escalates. Insert the matrix gate **before**
it:

```
else:  # UNSUPPORTED_TABLE
    if is_matrix_candidate(region, band):          # UNSUPPORTED already true here
        mreg = classify_matrix(band)
        if mreg is not None and matrix_tiles(mreg...):
            assert_matrix_region(...)              # compile -> HierarchicalTable
        else:
            escalate_region(..., "MATRIX_AMBIGUOUS", TAB.HierarchicalTable, 0.4)
    else:
        ... existing classify_hierarchical / escalate (VERBATIM unchanged) ...
```

`is_matrix_candidate` = `header_body_split(band, grid) >= 2 and stub_data_split(band, grid) is not None`
(kind is already `UNSUPPORTED_TABLE` in this branch). The existing Loop 2 hierarchical path stays
byte-for-byte unchanged in the `else`.

## §8 — Proof of closure (tests)

1. **`test_crosstab_compiles`** — the `crosstab_report` fixture → a `tab:HierarchicalTable` with a **column**
   tree (`Q1`/`Q2` level 0 `coversColumn` their 3 data cols; `Rev`/`Cost`/`Unit` level 1 one each) **and** a
   **row** tree (`North`/`South` level 0 `coversRow` one leaf row each); 6 data leaf columns; 2 leaf rows; 12
   entry cells at `(data-col × row)`; SHACL (column + row shapes) conforms; score 1.0.
2. **`test_proximity_column_tree`** (unit) — `infer_column_tree_by_proximity` recovers `Q1 → {1,2,3}`,
   `Q2 → {4,5,6}`, `Rev/Cost/Unit → one each`, regardless of the (short) label width — the case
   `infer_header_tree` under-covers.
3. **`test_matrix_detection_boundary`** — the crosstab fixture is a matrix candidate; **Loop 2's pivot**
   (`pivoted_table_pdf`, `stub_data_split` None) is **not** (stays on the Loop 2 path); **Loop 5's**
   `row_grouped_table_pdf` (RECORD_TABLE) is **not**.
4. **`test_matrix_provenance`** — an entry (`North`×`Q1/Rev` = 100) and both a column LabelCell (`Q1`) and a
   row LabelCell (`North`) carry physical bbox/onPage matching their measured words.
5. **`test_matrix_ambiguous_escalates`** — a fixture whose column tree does not tile (overlapping/short-gap
   parents) → escalates `MATRIX_AMBIGUOUS`, no HierarchicalTable.
6. **`test_loop2_pivot_still_compiles` / `test_row_grouped_still_compiles`** (regression) — Loops 2 and 5
   fixtures compile exactly as before; the matrix gate does not steal them.
7. **No regression** — full suite green; the Loop 2 hierarchical `else` branch is byte-for-byte unchanged.

## §9 — Showcase (part of the loop)

Add **Part G** to `demo/etkl_1a_showcase.ipynb`: render the cross-tab PDF first (original document, always),
then show it compile — print the **column** tree (`Q1 → Rev/Cost/Unit`, `Q2 → …`), the **row** axis
(`North`, `South`), and one doubly-addressed cell (`(North, Q1·Rev) = 100`), with the "so what": both header
axes are now first-class, and a value is addressed by `(column-path × row-path)` — the culmination of the
column pivot (Part C) and the row hierarchy (Part F) composing into a true 2-D matrix. Re-run to 0 errors.

## §10 — What's notable

The payoff of "one machinery across the diagonal": the matrix reuses **both** trees, **both** `covers*`
predicates, and the **union** of the tiling shapes with **zero** new vocabulary — the access function
`atColumn × atRow` was designed for exactly this from Loop 1. The single new algorithm, proximity span
recovery, is a *more robust* column-span oracle than text-extent (it will likely retire Loop 2's fragile
method in a later housekeeping pass, once the matrix path proves it). And the honesty is unchanged: both axes
must tile (existing SHACL) and every entry must round-trip, else escalate — a mis-read matrix is escalated,
never asserted.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/matrix.py` (create) | `infer_column_tree_by_proximity`, `MatrixRegion`, `classify_matrix`, `col_tree_tiles`, `matrix_tiles`, `is_matrix_candidate` |
| `src/iladub/etkl/holon.py` (modify) | add `assert_matrix_region` (composes column + row emission; reuses shared emitters) |
| `src/iladub/etkl/compile.py` (modify) | matrix gate in the `UNSUPPORTED_TABLE` branch, before `classify_hierarchical` |
| `src/iladub/etkl/__init__.py` (modify) | export the new matrix API |
| `tests/etkl/fixtures.py` (modify) | `crosstab_table_pdf` (tiling), `matrix_ambiguous_pdf` (non-tiling) |
| `demo/etkl_demo_data.py` (modify) | `crosstab_report_pdf` |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part G |
| `tests/etkl/test_matrix.py` (create), `tests/etkl/test_closing_slice.py`, `tests/etkl/test_holon.py` | the §8 proof suite |
