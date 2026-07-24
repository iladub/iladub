# Matrix (cross-tab) Feed — row-header path as record identity

**Date:** 2026-07-23
**Status:** Design — approved for spec (brainstorm 2026-07-23).
**Slice:** Extend the concept feed to fully handle **cross-tabs** — a `tab:HierarchicalTable` with BOTH a
column-header tree and a **row-header tree** (`coversRow`). The PR#58 hierarchical feed already reads a
cross-tab's column paths; this slice carries the **row-header path as the record identity** so cross-tab
records get meaningful subjects instead of opaque row ids. Second of the four "deepen" slices.

**Gate context (CLAUDE.md §8):** PROCEDURAL raw extraction — pure RDF reads over the row-header tree
(`hasHeaderNode`/`coversRow`/`hasLabel`/`headerLevel`/`parentHeader`); NO tuned constant, NO IRI-name
parsing. NO new grounding decision — a row-header path is just a subject label.

---

## 1. The decision (one sentence)

Add `_row_header_path(graph, table)` (mirror of `_column_header_path`, via `coversRow`) and use it as a
record's `row_id` when the table has a row-header tree; tables without one (`RecordTable`, plain
hierarchical) keep the opaque row-URI fragment — unchanged.

## 2. Why (findings from probe, 2026-07-23)

`assert_matrix_region` emits a **`tab:HierarchicalTable`** carrying a column tree (`coversColumn` +
`parentHeader`) AND a **row tree** (`coversRow` + `parentHeader`), with entries at `(atColumn, atRow)`.
Probed on `crosstab_table_pdf`:

- Column tree: `Q1 → {Rev, Cost, Unit}`, `Q2 → {…}` → column paths `"Q1 > Rev"` etc. (already read by
  the PR#58 feed).
- Row tree: `North` (`coversRow=[r0]`), `South` (`coversRow=[r1]`) → row paths `"North"`, `"South"` —
  **ignored** by the PR#58 feed, so cross-tab records currently get opaque `row_id`s (`mtable0-r0`).
- **End-to-end probed** with the row-header path as `row_id`: 2 records (`North`, `South`), each with 6
  column-path concepts; through `ground_document` (mapping `"Q1 > Unit" → ejectionFraction`), subjects
  mint as `urn:iladub:record:North` / `…:South`, 2 grounded / 10 proposed. The row identity is the
  cross-tab-specific improvement; everything else already works from PR#58.

## 3. Components (each single-purpose)

### 3.1 `_row_header_path(graph, table) -> dict[leaf_row, str]` (new, `feed.py`)

Mirror of `_column_header_path` but over `coversRow`: for each `HeaderNode`, record `headerLevel` +
`hasLabel→cellText` + `parentHeader`; keep the deepest header per `LeafRow`; walk `parentHeader` to the
root and join labels root→leaf with `" > "`. Returns `{}` when the table declares no `coversRow` (i.e. a
`RecordTable` or plain hierarchical table). Pure RDF reads.

### 3.2 `table_records` — row identity (`feed.py`)

After grouping cells by `atRow`, the record's `row_id` is the row-header path if the row has one
(`_row_header_path[row]`), else the current opaque URI fragment. Column-path concepts (PR#58),
`EntryCell` reads, the bbox-geometry sort, and provenance are unchanged.

### 3.3 `ground_document` — URI-safe subject minting (`feed.py`)

Mint the per-record subject from a URI-safe slug of `row_id` (`urn:iladub:record:<slug>`) so a
multi-level row path (`"Region > North"`) yields a clean URI; a bare row id (`"North"`, `"mtable0-r0"`)
is already safe. This is the only change to `ground_document` (a one-line slug); the grounding logic is
untouched.

## 4. Data flow

```
crosstab PDF → compile_tables → tab:HierarchicalTable (column tree + row tree)
  → table_records → Record(row_id="North", (SurfaceConcept("Q1 > Rev", "120", prov), ...))
  → ground_document → subject urn:iladub:record:North; per cell: ground_concept(...) → grounded | proposed
  → g: two OrganOffer subjects (North, South) with grounded column-path fields + propositions
```

## 5. Backward compatibility (load-bearing)

`RecordTable` and plain hierarchical tables (the pivoted CBC fixture has **no** `coversRow` — its rows
are a stub *data* column, not a row-header tree) → `_row_header_path` returns `{}` → the opaque row-URI
fragment `row_id`, **byte-identical**. Verified by the PR#56/#58 concept-feed tests staying green + an
explicit `_row_header_path(offer/pivoted) == {}` assertion.

## 6. Testing (offline; `./.venv/bin/python -m pytest`)

Extend `tests/test_concept_feed.py`:

1. **Bridge — cross-tab row identity (RED-checked):** on the compiled `crosstab_table_pdf` graph,
   `table_records` returns 2 records whose `row_id`s are `"North"` and `"South"` (not opaque
   `mtable0-r…`), each carrying column-path concepts (`"Q1 > Rev"`, `"Q2 > Cost"`, …). **RED:** the
   shipped feed gives opaque `row_id`s.
2. **`_row_header_path` unit:** the crosstab graph → `{leaf_row: "North"|"South"}`; the offer
   (`RecordTable`) and pivoted (hierarchical) graphs → `{}` (no row tree).
3. **Backward compat:** the offer `RecordTable` and pivoted hierarchical `row_id`s are unchanged (opaque
   fragments) — plus the PR#56/#58 tests stay green.
4. **E2E through `ground_document` (probe-validated):** crosstab →
   `ground_document(offer-contract, MappingGroundingProposer{"Q1 > Unit" → ejectionFraction}, …)` → the
   grounded graph has exactly two `tx:OrganOffer` subjects named `urn:iladub:record:North` and
   `…:South`; `FeedResult.records == 2`, `grounded > 0`, `proposed > 0` (in-range Units ground via the
   value-constraint oracle; larger values / unmapped paths quarantine). The mapping is a test-local
   illustrative wiring demonstration; no shape/contract file changed.

Full `tests/` suite stays green (the change is confined to `feed.py`; `ground_concept`, the etkl
compiler, and all shapes are untouched).

## 7. Anti-overfit

`_row_header_path` is pure RDF reads (deepest by `headerLevel`, walk `parentHeader`) — no tuned constant,
no IRI-name parsing. Backward compat is guaranteed by the empty-map reduction for tables without a row
tree (not a special-case branch). The E2E's quarantine of out-of-range/unmapped cells is the load-bearing
guard that the oracle still gates through the cross-tab feed (§7).

## 8. Scope boundary (YAGNI)

- The row-header path becomes the record **identity** (subject), NOT a groundable concept — row headers
  are bare labels (`North`) with no natural row-axis field name. Grounding the row-axis label as a
  concept is a possible future extension, out of scope.
- Handles cross-tabs (`HierarchicalTable` with a `coversRow` tree) + everything PR#56/#58 handled.
  Matrix-with-merged-row-headers (multi-level row tree) works by the same walk (probed shape is flat but
  the walk generalizes); no special-casing.
- Single-token data cells (multi-word / merged data cells out of scope — a later slice).
- No shared shape / contract changes; the E2E mapping is test-local and illustrative.

## 9. Definition of done (the loop CLOSES for cross-tabs)

- A cross-tab PDF compiles and feeds records **identified by their row-header path** (`North`, `South`),
  each carrying column-path concepts — `table_records` returns 2 named records (RED-checked non-vacuous).
- Those records ground through the unchanged `ground_document` into two meaningfully-named subjects
  (`urn:iladub:record:North` / `…:South`), in-range cells grounding via the value-constraint oracle,
  others quarantined — `FeedResult(records=2, grounded>0, proposed>0)`.
- `RecordTable` / hierarchical output byte-identical (backward-compatible); full suite green.
- Residue (out-of-range / unmapped cells) quarantined as `CandidateConcept` propositions, never dropped (§7).

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
