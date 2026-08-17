# Loop 8a · denormalization evidence + 3NF inversion — reverse the report back to normalized facts

**LANDED — salvaged onto `main` 2026-08-17 from the parked `aggregation-evidence` branch.** Shipped as `src/iladub/etkl/denormalization.py` (from `ac16401`): `recover_dimensions`, `detect_aggregations`, `verify_group`, `emit_base_facts`, `analyze`. **§4's emission mechanism is superseded** — the 3NF inversion was re-backed onto the declarative `reshape.derive_base` CONSTRUCT (`e6d2fb7`, `ff2a20e`), retiring the nested-`g.add` loop specified here. Read as the design record, not as a description of current behaviour.

**Status:** design (approved 2026-07-09, expanded to structural denormalization 2026-07-09)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** all prior loops — it consumes the compiled holon (leaf rows/cols, **header trees**, entry-cell
values). First of **two** slices: 8a = structural pivot evidence + the exact-arithmetic aggregations + 3NF
emission; 8b (later) = ratio (`%`) + sequence (running total, difference) verifiers on the same framework.

## Why this exists — a report is *denormalized normalized data*; recover the normalization

`tab.ttl` frames a table as an "intentional transformation stack: flat → pivot → cosmetic." A report is built
from normalized (3NF/tidy) facts by **denormalization processes**, and the compiled holon already carries the
fingerprints of two of them:

1. **Structural — a dimension pivoted into the header/stub hierarchy.** When `Region` spans `North / South /
   East / West` as its leaves, the hierarchy *is* the schema of the normalized form: the wide table is a
   **pivot** of one normalized `Region` column. Reversing it is an **unpivot / melt**.
2. **Arithmetic — aggregation rows/columns** (totals, subtotals). These are **derived views**; reversing them
   is a **strip** (they are recomputable from the base facts).

Probed on `main` today (2026-07-09): both a `Region × Quarter × Total` table and a hierarchical
subtotals table compile at score 1.0 — but the header hierarchy is treated only as *tiling* and the total
cells as *ordinary data*. The report's **meaning** (which columns are a pivoted dimension, which numbers are
facts vs. computed views of them) is lost. This loop recovers it and inverts to 3NF.

## §1 — Scope & closing target (decided 2026-07-09)

- **Structural denormalization (the primary 3NF mechanism):** read each header hierarchy (row **and** column
  axis) as a **pivot schema** — dimensions and their values — and **unpivot** it to long form. (§2)
- **Arithmetic denormalization (the exact set):** detect aggregation rows/cols whose cells equal
  `sum|mean|count|min|max|product` over a group, verified across the whole row/col; **strip** them. (§3)
  (Ratios `%` and sequences `running total`, `difference` are **Loop 8b** on the same framework.)
- **3NF emission:** the base cells, unpivoted, as **`qb:`-aligned observations** — one per full
  dimension-value combination × the measure. (§4)
- **Detect-or-escalate:** every recovered dimension / aggregation is either confidently evidenced **or**
  escalated (`AGGREGATION_AMBIGUOUS` / `DIMENSION_AMBIGUOUS`) — never guessed.
- **Closing proof:** (a) a `Region`-over-`{North,South,East,West}` pivot → a `Region` **PivotedDimension** with
  those values, unpivoted to a `Region` column; (b) a `Region/Q1/Q2/Total` table → `Total` col `sum{Q1,Q2}`,
  `Total` row `sum{North,South}`, grand total on both axes, the 4 base facts emitted; (c) a hierarchical
  subtotals table → each subtotal marked `sum` of its row-group.

## §2 — Structural denormalization evidence: header hierarchy → pivot dimensions

Read each axis's header tree as a **stack of dimensions** (this reuses the trees Loops 2/5/6 already build —
no new inference, only interpretation):

- A header **level whose single node spans all its leaves** → that label is a **dimension NAME**; the
  dimension's **values** are the labels at the level(s) below it. (`Region` over `{North,South,East,West}` →
  dimension `Region`, values `{North,South,East,West}`.)
- A header **level with multiple sibling nodes** → those labels are **VALUES** of a dimension at that level;
  the dimension's **name** comes from a spanning parent above (case 1), or a **stub-head** corner label
  (Loop 5's `Region`/`Metric`), or is **unnamed/positional** if neither exists. (`Current Visit` / `Prior
  Visit` → values of the (possibly unnamed) "Visit" dimension.)
- A leaf column/row therefore has a **coordinate** = one value per dimension on its axis (a cross-tab leaf
  `(Q1, Rev)` → `Quarter=Q1, Metric=Rev`).

Emit, per axis, a `tab:PivotedDimension` (name if recoverable, axis, level, and its value set); each leaf's
`tab:EntryCell` gains its dimension coordinate. A level that is neither cleanly a single spanning name nor a
clean value partition escalates `DIMENSION_AMBIGUOUS` (e.g. an irregular header). The flat single-level record
header is the degenerate case: each column label is its own dimension name with the column's cells as the
measure (no pivot to unwind on that axis).

## §3 — Arithmetic denormalization evidence: the aggregation oracle

The strongest oracle in the project — **exact arithmetic**. Build the `{(leaf_row, leaf_col): number}` value
matrix; the **groups** come from the header trees (a node's covered leaves) plus the implicit all-base group.

**Iterated strip** (probe-verified to recover the base facts exactly):
1. A leaf **row** `R` is an aggregation iff a function `f ∈ {sum,mean,count,min,max,product}` and a group `G`
   of other **base** rows satisfy `value(R,c) = f({value(g,c):g∈G})` for **every** leaf column `c`. Candidate
   groups: each row-header node's covered leaf rows (subtotals) + all other base rows (grand total). Mark `R`,
   remove from base.
2. Symmetrically for columns. 3. Repeat to fixpoint (grand total = row×col intersection, carries **both**
   axes). 4. Base rows/cols = remainder; base cells = base × base.

Full-row/column consistency is the safety property: one cell equal to a sum is chance; a whole row every cell
of which equals its column-group's sum is not. **Disambiguation:** over **≥2** operands the functions differ,
so `f` is unique; a **single-operand** group (`sum=mean=min=max`) is resolved by the row/col **label**
(`Total/Sum/Avg/…`) or **escalated `AGGREGATION_AMBIGUOUS`** — never guessed. **Float tolerance:**
`abs(f(G)-target) ≤ 1e-6·max(1,|target|)` (display-faithful, not a tuned knob).

## §4 — 3NF inversion: unpivot + strip → `qb:`-aligned observations

The normalized output = **strip** the aggregation rows/cols (§3) **and unpivot** the pivoted dimensions (§2):

- **Strip:** aggregation rows/cols are removed from the base set (recorded as derivable views — their
  `aggregationFunction` + `aggregates` say exactly how to recompute them).
- **Unpivot:** each base cell becomes one **`tab:BaseFact`** whose dimension values are the full coordinate
  (row-axis dimensions × column-axis dimensions, from §2), and whose `tab:measureValue` is the cell value.
  A `Region`-pivoted wide table thus yields one `Region` dimension column instead of N region columns; a
  cross-tab yields `(row-dims…, Quarter, Metric, value)`.

Alignment to **RDF Data Cube** lives in a new **`vocab/ontology/tab-qb-align.ttl`** module (source-ownership:
external alignment never in core): `tab:BaseFact ⊑ qb:Observation`, `tab:PivotedDimension ⊑ qb:DimensionProperty`,
`tab:measureValue ⊑ …`, `seeAlso` links. Core `tab.ttl` never references `qb:`. The base facts *are* the 3NF/
tidy form; the report becomes a derivable view over them — the inversion the user asked for.

## §5 — Vocabulary (owned `tab:`)

Add to `vocab/ontology/tab.ttl`:
- **Structural:** `tab:PivotedDimension` (a dimension recovered from a header axis) with `tab:dimensionName`
  (string, optional), `tab:onAxis` (`row|column`), `tab:atLevel` (integer), `tab:hasDimensionValue` (→ the
  value labels). `tab:atDimensionValue` links an `EntryCell` / `BaseFact` to a `PivotedDimension` value.
- **Arithmetic:** `tab:AggregationCell ⊑ tab:EntryCell`, `tab:AggregationRow ⊑ tab:LeafRow`,
  `tab:AggregationColumn ⊑ tab:LeafColumn`, `tab:aggregationFunction` (`sum|mean|count|min|max|product`),
  `tab:aggregates` (→ operand `EntryCell`s), `tab:overAxis` (`row|column`).
- **3NF:** `tab:BaseFact` with `tab:measureValue` and its dimension-value links.

`tab.ttl` stays standalone. A `tests/test_tab.py` term-presence test confirms the new terms.

## §6 — SHACL (owned)

Add to `vocab/shapes/tab-shapes.ttl`:
- `tab:AggregationCellShape` — exactly one `aggregationFunction`, ≥1 `aggregates`, ≥1 `overAxis`.
- `tab:PivotedDimensionShape` — ≥1 `hasDimensionValue`, exactly one `onAxis`.
- `tab:BaseFactShape` — ≥1 dimension-value link, exactly one `measureValue`.
Ships with `examples/tables/denormalization-conformant.ttl` (a pivot + a total, correctly evidenced) and
`denormalization-negative.ttl` (an `AggregationCell` missing its function/operands → fails).

## §7 — API & placement

A **post-compile analysis** over the compiled graph (uniform across record/hierarchical/matrix holons — it
reads `EntryCell`/`atColumn`/`atRow`/`cellText` + the header trees):

- `src/iladub/etkl/denormalization.py` (new):
  - `recover_dimensions(graph, table_uri) -> list[PivotedDimension]` (§2 header-tree reading, per axis).
  - a **verifier framework** `verify_group(target, group_per_col) -> str | None` (pluggable; 8b adds `%`/
    running/diff without touching the core).
  - `detect_aggregations(graph, table_uri) -> AggregationEvidence` (§3 iterated strip).
  - `annotate(graph, dims, aggs)` — emit the `tab:PivotedDimension` / `AggregationCell/Row/Column` triples;
    escalate `DIMENSION_AMBIGUOUS` / `AGGREGATION_AMBIGUOUS`.
  - `emit_base_facts(graph, dims, aggs, table_uri)` — the §4 `tab:BaseFact` observations (unpivot + strip).
  - `analyze(report) -> DenormalizationReport` — the public entry point.

`compile_tables` is **unchanged** — this is an explicit, optional stage. The new SHACL validates on demand.

## §8 — Honest limits (documented, not swallowed)

- **Unnamed dimensions:** a value-level with no spanning-parent name and no stub-head yields a positional
  dimension (`dim0/dim1`) — the values are still recovered, only the name is absent (documented).
- **Single-operand aggregation groups** are function-ambiguous and are label-resolved or escalated — never
  guessed.
- **Coincidental aggregation** across a full row/col is astronomically unlikely but not impossible; the
  evidence is the arithmetic itself (`aggregates` is inspectable).
- **Flat records with no text stub** (all-numeric first column) recover column dimensions only; the row
  dimension is positional. A richer identity model is future work.
- **Ratios/sequences** (`%`, running total, difference) are **Loop 8b** — an 8a run will simply not flag them
  (the exact-arithmetic check won't match), never mis-flag them.
- **Structural recovery is only as correct as the upstream header tree.** `recover_dimensions` faithfully reads
  whatever tree the holon carries; it does not re-infer it. A hierarchical table with a **short parent label
  over a wide column span** (e.g. `Region` over four wide numeric columns) can be *under-covered* by Loop 2's
  text-extent span recovery (probe-confirmed) — the dimension then inherits that error. This is an **upstream**
  limitation, not 8a's: it is correct on matrix holons (Loop 6's proximity spans), on wide-label hierarchical
  headers, and on flat records. The §9 suite therefore unit-tests the §2/§3 *logic* on constructed correct
  graphs (decoupled from inference) and integration-tests only on fixtures that compile with a correct tree.

## §9 — Proof of closure (tests)

1. **`test_recover_pivoted_dimension`** — a `Region`-over-`{North,South,East,West}` fixture → a
   `tab:PivotedDimension` name `Region`, values `{North,South,East,West}`, `onAxis column`.
2. **`test_unpivot_to_long_form`** — that fixture's base cells → `tab:BaseFact`s each carrying a `Region`
   dimension value + the measure (one column, not four).
3. **`test_detect_grand_totals`** — `Region/Q1/Q2/Total` → `Total` col `sum{Q1,Q2}`, `Total` row
   `sum{North,South}`, grand-total cell `overAxis` row **and** column.
4. **`test_base_facts_recovered`** — the 4 base facts `(Region=North,Quarter=Q1)=100 … (South,Q2)=130`; no
   `Total` leaks into the base set.
5. **`test_detect_subtotals_over_row_groups`** — hierarchical fixture → each per-group `Total` row `sum` of its
   `coversRow` group.
6. **`test_mean_min_max_count`** (unit) — ≥2-operand groups uniquely resolved to each function.
7. **`test_single_operand_escalates`** — a one-row subtotal with no label → `AGGREGATION_AMBIGUOUS`.
8. **`test_no_false_aggregation`** (guard) — a table with no arithmetic relationship → zero `AggregationCell`s.
9. **`test_tab_denormalization_terms`** + **`test_denormalization_shapes`** — new terms declared; conformant
   passes, negative fails.
10. **No regression** — `compile_tables` output unchanged; full suite green.

## §10 — Showcase (part of the loop)

Add **Part I** to `demo/etkl_1a_showcase.ipynb`: render a `Region × Quarter` report **with totals** first, then
show `analyze` (a) recover the pivoted `Region`/`Quarter` **dimensions** from the header hierarchy, (b) mark
the `Total` row/column as `sum` aggregations, and (c) emit the **base facts** — the tidy/3NF table the report
was built from (a `Region` column, a `Quarter` column, a value; totals gone but recorded as derivable). The
"so what": ET(K)L recovers the *denormalization processes* — the pivot **and** the aggregation — and inverts
them, turning a presentation table back into normalized facts. Re-run to 0 errors.

## §11 — What's notable

Two firsts. **The header hierarchies become a schema, not just a tiling** — a pivoted dimension is *read* from
the tree we already built, so the same structure that certified coverage now names the normalized columns.
And **the arithmetic oracle** — an aggregation is *proven*, not inferred (the numbers add up across the whole
row/column). Together they make the `tab:` thesis (a table is an invertible transformation stack) literal: the
evidence records how each derived cell and each pivoted column was produced, and the base facts are the 3NF
form it started from — aligned to RDF Data Cube, exactly as the canvas set out from Loop 1. The framework
extends cleanly: Loop 8b drops in ratio/sequence verifiers.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/denormalization.py` (create) | `recover_dimensions`, verifier framework, `detect_aggregations`, `annotate`, `emit_base_facts`, `analyze` |
| `src/iladub/etkl/__init__.py` (modify) | export the denormalization API |
| `vocab/ontology/tab.ttl` (modify) | `PivotedDimension` (+ name/onAxis/atLevel/hasDimensionValue/atDimensionValue), `AggregationCell/Row/Column`, `aggregationFunction`, `aggregates`, `overAxis`, `BaseFact`, `measureValue` |
| `vocab/ontology/tab-qb-align.ttl` (create) | `qb:` alignment (`BaseFact ⊑ qb:Observation`, `PivotedDimension ⊑ qb:DimensionProperty`, …), external-only |
| `vocab/shapes/tab-shapes.ttl` (modify) | `AggregationCellShape`, `PivotedDimensionShape`, `BaseFactShape` |
| `examples/tables/` (create) | `denormalization-conformant.ttl`, `denormalization-negative.ttl` |
| `tests/etkl/fixtures.py` (modify) | `region_pivot_pdf`, `totals_table_pdf`, `subtotals_row_group_pdf`, `no_aggregation_pdf` |
| `demo/etkl_demo_data.py` (modify) | `denormalized_report_pdf` |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part I |
| `tests/etkl/test_denormalization.py` (create), `tests/test_tab.py`, `tests/test_vocab_shapes.py` | the §9 proof suite |
