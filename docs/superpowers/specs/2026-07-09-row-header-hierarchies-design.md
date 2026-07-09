# Loop 5 · compile row-header hierarchies — the vertical mirror of Loop 2

**Status:** design (approved 2026-07-09)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** Loop 2 (column-header tree: `headers`, `rows`, `hierarchical`, `assert_hier_region`) +
Loop 1 (record path, round-trip) + Loop 4 (the detect→certify→compile-else-escalate pattern)

## Why this exists — a flattened row hierarchy is a mis-profiled kind

A **row-header hierarchy** puts grouped labels *down* the stub columns:

```
Region   Metric    Value
North    Revenue   100
         Cost       60
         Margin     40
South    Revenue   120
         Cost       70
```

`North` is a **merged row header** spanning three sub-rows, encoded — as report tables almost always do —
by a label in the stub column with **blank cells below it** (the blanks belong to the group above). This is
the exact vertical mirror of a merged *column* header, whose centered horizontal extent spans a run of leaf
columns.

Compiled on `main` today, this header line (`Region Metric Value` — 3 words, 3 columns, 1:1 aligned) is
*regular*, so it classifies as `RECORD_TABLE` and is **flattened**: the `Cost`/`Margin` rows lose their
`North` grouping, the access function cannot answer "all metrics for North", and the table's true **kind** —
a 2-level row hierarchy — is silently mis-profiled as a flat record. Neither existing oracle catches it: the
round-trip (geometry) and the `tab:` SHACL (column tiling) both pass on the flattened reading. The row-header
tree is a **topology** the current model does not represent.

This loop **detects** the blank-below grouping, **compiles** the correct row-header tree, and — when the
grouping does not tile — **escalates** rather than flatten.

## §1 — The mirror (this is the whole design)

| Column-header tree (Loop 2) | Row-header tree (Loop 5) |
|---|---|
| built from header **rows** (above the body) | built from stub **columns** (left of the data) |
| each header **row** = a level | each stub **column** = a level (leftmost = coarsest = level 0) |
| a cell's **column-span** from its centered horizontal extent | a cell's **row-span** from the *blank-below* (forward-fill) run |
| `tab:coversColumn` (HeaderNode → LeafColumn) | **new `tab:coversRow`** (HeaderNode → LeafRow) |
| Coverage · NoOverlap · Refinement · UnambiguousAccess (columns) | the same four shapes, mirrored onto rows |
| leaf columns are entry-bearing | leaf **rows** are entry-bearing; **stub columns are the row-header axis** |

## §2 — Scope & closing target

- **Closing proof:** a `row_grouped_report` fixture (2 stub columns — a grouped `Region`, a fully-populated
  `Metric` — + a numeric `Value` data column) that today compiles to a flat `RecordTable` now compiles to a
  `tab:HierarchicalTable` with a **row-header tree** (`North`/`South` at level 0 covering their leaf-row
  runs; `Revenue`/`Cost`/`Margin` at level 1 covering one leaf row each), certified by the new row SHACL;
  every flat record still compiles unchanged.
- **In scope:** the stub/data split, the `looks_row_grouped` detection oracle, the row-header tree builder
  with the blank-below row-span rule, the `row_tree_tiles` pre-assert gate, the `assert_row_hier_region`
  maker, `tab:coversRow` + four row SHACL shapes, and the compile/escalate gate.
- **Out of scope (escalated, on the canvas):** a table whose **column** header is *also* hierarchical (both
  axes → matrix/cross-tab, a later loop); a **vertically-centered** merged row cell (only the blank-below
  encoding is handled); a stub with **no** fully-populated finest column (leaf rows unidentifiable);
  aggregation/subtotal rows. Column-only hierarchies remain Loop 2's `assert_hier_region`, untouched.

## §3 — Modeling decision (settled) — stub columns are the row-header axis

The compiled holon (Design A, chosen 2026-07-09; matches RDF Data Cube `qb:` dimensions / Wang's label
model):

- **Leaf columns = the data columns only** (here `{Value}`). The flat **column** header (`Value`) covers
  them via `coversColumn`, exactly as Loop 1.
- **Stub columns = the row-header tree**, not leaf columns. Each stub column is a row-header **level**; its
  non-blank cells become `tab:HeaderNode`s carrying `tab:coversRow` + a `tab:LabelCell` (text + bbox + page).
  `North` is encoded **once**, as a level-0 row-header covering `{lr0, lr1, lr2}`.
- **Leaf rows = the body rows** (`Revenue, Cost, Margin, Revenue, Cost` — 5 leaf rows). Each is covered by
  exactly one **leaf** row-header (its finest-stub node) and by its coarser ancestors.
- **Entry cells** sit at (data leaf column × leaf row): `EntryCell 100  atColumn Value  atRow lr0`, whose
  row-path is `North → Revenue`.
- **Stub-head labels** (`Region`, `Metric` on the header line, sitting over stub columns) are the *names of
  the row-header levels*. For v1 they are carried as `tab:LabelCell`s on the table (`tab:hasCell`) with their
  geometry — context preserved, never dropped — but formal dimension-naming structure is **out of scope**
  (a future refinement). Only labels over **data** columns become column `HeaderNode`s.

Reuses `tab:HeaderNode`, `tab:parentHeader`, `tab:headerLevel`, `tab:hasLabel` unchanged — the node type is
axis-neutral; the only new predicate is `tab:coversRow`. (`tab:HierarchicalTable`'s comment already reads "a
column **or row** axis".)

## §4 — Detection, the reading convention, and the structural backstop

**Honest framing (corrected after an empirical probe, 2026-07-09).** Blank-below in a stub column is read as
*ditto-grouping* — this is a **table-authoring convention**, the exact vertical analog of Loop 2's
"centered-merge means column-span" convention (`headers.py` documents that it *assumes* centered merges and
puts other alignments out of scope). It is **not** a fact a structural oracle can prove: a stub column of
genuinely *missing* labels is geometrically identical to ditto-grouping, so the two are not deterministically
separable without external evidence — the same class of irreducible ambiguity as Loop 4's fully-numeric
transposition. The compiler therefore *applies the convention* and certifies the **structure** it produces;
it does not claim to divine authorial intent. This risk is bounded by three requirements below (finest-stub
populated + tiling backstop + SHACL), and documented in §Honest limits.

What the oracles actually do:

1. **`stub_data_split(band, grid) -> int | None`** — the vertical mirror of `header_body_split`. On body
   rows only (below `header_body_split`), find the boundary `k` where columns transition from text (stub) to
   all-numeric (data): stub columns `[0..k-1]`, data columns `[k..ncols-1]`. Require `k ≥ 1` (a stub) and
   `k < ncols` (a data column), and every data column all-numeric where present. `None` → not a row-header
   candidate (falls through to the existing record path).

2. **`looks_row_grouped(region) -> bool`** — detects the blank-below signature: **some** stub column has
   **fewer non-blank body cells than there are leaf rows** (a forward-fill run), **and** the **rightmost**
   stub column is **fully populated** (one label per leaf row — so leaf rows are individually identified).
   A flat record (every stub cell populated) → `False` → record path unchanged. All-text tables (no data
   column) → `stub_data_split` is `None` → `False`.

3. **`row_tree_tiles(tree, n_leaf_rows) -> bool`** — the pre-assert **structural backstop**: the leaf-level
   row-headers must partition the leaf rows (each leaf row covered by exactly one leaf row-header; every
   child's row-covers ⊆ its parent's; no same-level overlap; full coverage). Its job is to catch *pathological
   geometry* (an irregular blank pattern that would produce a gap/overlap and make the emitted holon fail the
   row SHACL) and escalate `ROW_GROUP_AMBIGUOUS` rather than emit-then-crash `_validate`. **It is not the
   grouping-vs-missing discriminator** — given the finest-populated precondition, a well-formed forward-fill
   always tiles, so this is a safety assertion, not the primary gate. The **row SHACL is the final certifier**
   of the emitted tree's structure.

**Gate placement (`compile.py`, `RECORD_TABLE` branch):**

```
if looks_transposed(region):
    ... (Loop 4, unchanged)
elif looks_row_grouped(region):
    build the row-header tree + leaf rows
    if row_tree_tiles(tree, n_leaf_rows) and region entries round-trip:
        assert_row_hier_region(...)                # compile -> HierarchicalTable
    else:
        escalate_region(..., "ROW_GROUP_AMBIGUOUS", TAB.HierarchicalTable, 0.4)
else:
    ... existing upright RECORD_TABLE assert (VERBATIM unchanged)
```

The final `else` (the flat-record assert) stays byte-for-byte unchanged; only a new `elif` is inserted
between the transposed branch and it.

## §5 — Maker (`rowheaders.py`, mirror of `headers.py`)

New module `src/iladub/etkl/rowheaders.py`:

- `stub_data_split(band, grid) -> int | None` (§4.1).
- `looks_row_grouped(region) -> bool` (§4.2).
- `RowHeaderNode(level, covers_rows, text, parent, x0, top, x1, bottom, page)` — a row-header node carrying
  its leaf-row span **and** the stub cell's geometry (for the LabelCell provenance).
- `infer_row_header_tree(band, grid, stub_cols, leaf_rows) -> tuple[RowHeaderNode, ...] | None` — mirror of
  `infer_header_tree`: for each stub column `s` (level = its index among stub columns), each **non-blank**
  cell opens a node covering the contiguous run of leaf rows from its row **down to (excluding) the next
  non-blank cell** in column `s` (the blank-below rule). Parent links: a node at level `L` → the node at
  level `L-1` whose `covers_rows ⊇` this node's. `None` if no node is found.
- `row_tree_tiles(tree, n_leaf_rows) -> bool` (§4.3).

Leaf rows come from the **existing** `rows.logical_rows` (its anchor picks the fully-populated finest stub or
the data column; the grouped stub column, having blanks, is correctly rejected as anchor). No change to
`rows.py`.

## §6 — Holon maker (`holon.py`)

`assert_row_hier_region(g, region, band, tree, leaf_rows, stub_cols, data_cols, table_uri, doc_uri, page) -> int`
emits a `tab:HierarchicalTable`:

- **data leaf columns** (`data_cols`): `tab:LeafColumn` + a flat level-0 column `HeaderNode` (`coversColumn`
  + `hasLabel` from the header line's label over that column).
- **leaf rows**: one `tab:LeafRow` per body row.
- **row-header tree**: one `HeaderNode` per `RowHeaderNode` — `headerLevel`, `tab:coversRow` → each covered
  `LeafRow`, `tab:parentHeader`, and a `tab:LabelCell` (`cellText`/`onPage`/`hasBBox` from the stub cell's
  geometry — provenance-to-the-page for row headers too).
- **entry cells**: for each (data column × leaf row), an `EntryCell` (`atColumn`/`atRow`/`cellText`/`onPage`/
  `hasBBox`/`wasDerivedFrom`) via the **shared `_emit_entry_cell`** from Loop 4. A body entry that fails
  `cell_round_trips` escalates `ROUND_TRIP_FAIL` via the shared `_emit_roundtrip_fail_cell` — cell-level
  honesty, reused.
- **stub-head labels**: each header-line label over a stub column → a `tab:LabelCell` on the table (context
  carried).

Returns the asserted entry count. `assert_hier_region` (Loop 2, column axis) is untouched.

## §7 — Ontology & SHACL (mirror the column side)

**`vocab/ontology/tab.ttl`** — add one predicate:

```turtle
tab:coversRow a owl:ObjectProperty ; rdfs:label "covers row"@en ;
    rdfs:domain tab:HeaderNode ; rdfs:range tab:LeafRow ;
    rdfs:comment "A leaf row in this header node's (vertical) span — the row-axis mirror of tab:coversColumn."@en .
```

`tab.ttl` stays standalone. A `tests/test_tab.py` term-presence test confirms `tab:coversRow`.

**`vocab/shapes/tab-shapes.ttl`** — add the four row shapes, each a verbatim mirror of its column shape with
`coversColumn→coversRow`, `LeafColumn→LeafRow`, `hasLeafColumn→hasLeafRow`:

- `tab:RowCoverageShape` (targetClass `tab:LeafRow`) — every leaf row covered by ≥1 row-header of its table.
- `tab:RowNoOverlapShape` (targetSubjectsOf `tab:hasHeaderNode`) — no two same-level headers share a
  `coversRow`.
- `tab:RowRefinementShape` (targetClass `tab:HeaderNode`) — a child's `coversRow` ⊆ its parent's.
- `tab:UnambiguousRowAccessShape` (targetClass `tab:LeafRow`) — each leaf row covered by exactly one
  **leaf** row-header (a header with no `parentHeader` children) of its table.

The column shapes are untouched and do not interfere: they key on `coversColumn`/`LeafColumn`; row headers
carry only `coversRow`. `headerLevel` is shared across axes but the shapes never mix the two predicates, so a
flat column header at level 0 and row headers at level 0 coexist without false overlaps. Ships with a
row-hierarchy **conformant** example and a **negative** example (a non-tiling row tree that must fail
`UnambiguousRowAccessShape`).

## §8 — Proof of closure (tests)

1. **`test_row_grouped_compiles`** — `row_grouped_report` → a `tab:HierarchicalTable` with row `HeaderNode`s:
   `North`/`South` (level 0) `coversRow` their 3/2 leaf rows; `Revenue`/`Cost`/`Margin` (level 1) one leaf
   row each; `parentHeader` links; leaf columns = `{Value}`; entries at (Value × leaf row); SHACL conforms;
   the flat-record flattening is gone (`Cost` row now grouped under `North`).
2. **`test_looks_row_grouped_oracle`** (unit) — grouped region → True; a flat record → False; an all-text
   table → False.
3. **`test_row_tree_tiles_rejects_pathology`** (unit, the backstop) — a constructed non-partitioning tree
   (a gap: a leaf row covered by no leaf header; and an overlap: two same-level nodes sharing a row) →
   `row_tree_tiles` False. Plus **`test_single_stub_not_row_grouped`** — a table with one stub column whose
   labels have blanks (no fully-populated finer stub) → `looks_row_grouped` False → stays on the record path
   (leaf rows unidentifiable; not mis-compiled). These together show the preconditions + backstop, not a
   claimed semantic discriminator.
4. **`test_row_header_provenance`** — the `North` row-header `LabelCell` has `onPage` and a `hasBBox` equal to
   the physical `"North"` word's measured bbox; an entry cell traces to its physical value word.
5. **`test_row_tree_tiles_unit`** — a partitioning tree → True; a gappy/overlapping tree → False.
6. **`test_normal_tables_still_compile`** (regression) — `simple_table` / `record_report` compile flat,
   unchanged; `looks_row_grouped` False for both.
7. **`test_tab_coversrow_term`** + **`test_row_shapes`** (in `tests/test_tab.py`, beside the existing
   `hierarchical-conformant` checks) — `tab:coversRow` declared; the `examples/tables/row-hierarchy-conformant.ttl`
   example passes all four row shapes and `row-hierarchy-negative.ttl` fails `UnambiguousRowAccessShape`.
8. **No regression** — full etkl + tab + shapes suite green.

## §8b — Honest limits (documented, not swallowed)

- **Blank-below is read as ditto-grouping — a convention, not a proof.** A stub column of genuinely *missing*
  labels is geometrically identical and would be read as groups. This mirrors Loop 2's centered-merge
  convention and Loop 4's fully-numeric ambiguity: irreducible without external evidence (a contract /
  signal-tagging). Bounded by the finest-populated requirement (leaf rows must be individually identified),
  the tiling backstop, and the row SHACL. A signal-tagging or contract-driven override is a future increment.
- **Finest stub must be fully populated.** A lone grouped stub with no per-row finer column (sub-rows lack
  identity) is left on the record path — not mis-compiled, but the grouping is not captured. Out of scope.
- **Flat column header only.** A table hierarchical on *both* axes is matrix/cross-tab (a later loop); this
  loop compiles a hierarchical *row* header over a *flat* column header. Vertically-centered (non-blank-fill)
  row merges and subtotal/aggregation rows are out of scope.
- **Cell-level honesty holds regardless:** an entry that fails the per-cell round-trip escalates
  `ROUND_TRIP_FAIL` (reused from the record path), so a mis-placed value is never silently asserted.

## §9 — Showcase (part of the loop)

Add **Part F** to `demo/etkl_1a_showcase.ipynb`: render the row-grouped PDF first (original document, always),
then show it compile — print the recovered **row-header tree** (`North → {Revenue, Cost, Margin}`,
`South → {Revenue, Cost}`), the single leaf column (`Value`), and one addressed entry (`(North, Cost) = 60`),
with the "so what": the same grouping a flat parser drops, ET(K)L captures as a first-class row-header
dimension — the vertical mirror of the pivot in Part C. Re-run the notebook to 0 errors.

## §10 — What's notable

Row and column hierarchies are now the **same machinery reflected across the diagonal** — one `HeaderNode`
tree abstraction, two `covers*` predicates, one set of tiling invariants applied to each axis. That symmetry
is the groundwork for **matrix/cross-tab** (both axes hierarchical at once), which becomes "run both builders
and let the access function `atColumn × atRow` compose" rather than a new mechanism. The honesty here is the
same shape as Loop 2 and Loop 4: the compiler **applies a documented reading convention** (blank-below =
ditto-grouping, the mirror of centered-merge = column-span) and **certifies the resulting structure** with the
row SHACL + per-cell round-trip, rather than pretending a structural oracle can recover authorial intent from
geometrically-ambiguous input.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/rowheaders.py` (create) | `stub_data_split`, `looks_row_grouped`, `RowHeaderNode`, `infer_row_header_tree`, `row_tree_tiles` |
| `src/iladub/etkl/holon.py` (modify) | add `assert_row_hier_region` (reuses `_emit_entry_cell`/`_emit_roundtrip_fail_cell`) |
| `src/iladub/etkl/compile.py` (modify) | insert the `elif looks_row_grouped` gate in the `RECORD_TABLE` branch |
| `src/iladub/etkl/__init__.py` (modify) | export the new oracles + maker |
| `vocab/ontology/tab.ttl` (modify) | add `tab:coversRow` |
| `vocab/shapes/tab-shapes.ttl` (modify) | add the four row shapes |
| `examples/tables/` (create) | `row-hierarchy-conformant.ttl` + `row-hierarchy-negative.ttl` (beside `hierarchical-conformant.ttl`) |
| `demo/etkl_demo_data.py` (modify) | add `row_grouped_report_pdf` |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part F |
| `tests/etkl/`, `tests/test_tab.py`, `tests/test_vocab_shapes.py` | the §8 proof suite |
