# Hierarchical Table Feed — header-path concepts into grounding

**Date:** 2026-07-23
**Status:** Design — approved for spec (brainstorm 2026-07-23).
**Slice:** Extend the concept feed (`2026-07-22-concept-feed-etkl-to-grounding-design.md`) from flat
`tab:RecordTable` to **`tab:HierarchicalTable`** (merged-header tables), where a data cell's field is a
**path through the header tree** (root → leaf sub-header). Connects the merged-header recovery work
(B1.x) to the grounding pipeline. First of the four "deepen" slices (hierarchical / matrix / enum-E2E /
typed-enum); matrix is a separate later slice.

**Gate context (CLAUDE.md §8):** PROCEDURAL raw extraction — pure RDF reads over the compiled header
tree (`hasHeaderNode`/`coversColumn`/`hasLabel`/`headerLevel`/`parentHeader`), NO tuned constant, NO
IRI-name parsing. NO new grounding decision — `ground_document`/`ground_concept` are reused verbatim; a
header path is just `SurfaceConcept.text`.

---

## 1. The decision (one sentence)

Generalize `feed.table_records` to read **both** `tab:RecordTable` and `tab:HierarchicalTable`, computing
each column's field as the **header path** — the deepest `HeaderNode` covering the column, walked up
`parentHeader` to the root, labels joined `" > "` — which reduces to the single column label for flat
tables (byte-identical output, backward-compatible).

## 2. Why this is sound (feasibility probed, 2026-07-23)

The pivoted CBC table (`pivoted_table_pdf`) compiled to a `tab:HierarchicalTable` and the reconstruction
yielded clean path-concepts:

```
r0 c0  Analyte                     Hemoglobin
r0 c1  Current Visit > Result (SI) 13.2
r0 c4  Prior Visit > Result (SI)   12.8
```

- The header tree carries everything as triples: `HeaderNode headerLevel/coversColumn/hasLabel` +
  `parentHeader` (leaf `Result (SI)` → parent `Current Visit`). No name parsing.
- **The path logic generalizes the flat case**: a `RecordTable`'s headers are all level-0,
  single-column, no parent → path = the single label = current behavior. One unified code path.
- **End-to-end probed**: 5 records (5 analytes); through `ground_document` with an illustrative mapping
  (`"Current Visit > Result (SI)" → ejectionFraction`), 4 cells ground (in-range Current Results via the
  value-constraint oracle) and 26 quarantine (Platelets "252" ∉ [0,100]; unmapped paths) — proving path
  concepts flow through the unchanged oracle and it still gates.

## 3. Components (each single-purpose)

### 3.1 `_column_header_path(graph, table) -> dict[column, str]` (new, `feed.py`)

For each `HeaderNode` of `table`, record `headerLevel` + `hasLabel→cellText` per covered column; keep
the **deepest** (max level) header per column; then walk `parentHeader` to the root and join the labels
root→leaf with `" > "`. Pure RDF reads. For a `RecordTable` (all level-0, single-column, no parent) the
result is the single label per column.

### 3.2 `table_records` generalized (`feed.py`)

Iterate tables of type **`TAB.RecordTable` OR `TAB.HierarchicalTable`**; replace the current inline
single-label header map with `_column_header_path`. Everything else unchanged: `tab:EntryCell` reads
(`atColumn`/`atRow`/`cellText`), row grouping by `atRow`, the bbox-geometry sort (rows by min cell
`y0`, cells by `x0`), and provenance. Each data cell → `SurfaceConcept(text=header-path, value=cellText,
region=cell-provenance)`, grouped by row into `Record`s.

### 3.3 `ground_document` — unchanged

A header path is just `concept.text`. It routes through the existing grounding: no exact match for a
path → the proposer maps the path to a contract field → the oracle disposes. Row = record (each pivoted
row is one entity, e.g. an analyte, with its path-fields). No code change.

## 4. Data flow

```
hierarchical PDF → compile_tables → tab:HierarchicalTable (header tree)
  → table_records → Record(row, (SurfaceConcept("Current Visit > Result (SI)", "13.2", prov), ...))
  → ground_document → propose(path → field) → dispose (scheme / value-constraint) → grounded | proposed
  → g: GroundedNode + PromotionDecision (grounded) + CandidateConcept per cell
```

## 5. Backward compatibility (load-bearing)

The PR#56 `RecordTable` feed output must stay **byte-identical** — guaranteed because `_column_header_path`
yields the single label for flat tables (level-0 / single-column / no parent). Verified by the existing
`tests/test_concept_feed.py` staying green **plus** an explicit assertion that an offer `RecordTable`
record's concept header is `"Organ"` (a label), not a path.

## 6. Testing (offline; `./.venv/bin/python -m pytest`)

Extend `tests/test_concept_feed.py`:

1. **Bridge — hierarchical paths (RED-checked):** on the compiled `pivoted_table_pdf` graph,
   `table_records` returns 5 `Record`s; assert path-concepts — `"Current Visit > Result (SI)"`=13.2,
   `"Prior Visit > Unit"`=g/dL, stub `"Analyte"`=Hemoglobin. **RED:** the shipped `table_records` filters
   only `RecordTable` → 0 records for a hierarchical-only graph.
2. **`_column_header_path` unit:** on the hierarchical graph, a leaf data column → its root→leaf path;
   on the flat offer graph, each column → its single label (the reduction that guarantees backward compat).
3. **Backward compat:** the offer `RecordTable` feed still yields single-label headers — assert a record's
   concept text is `"Organ"` (not a path); existing PR#56 tests stay green.
4. **E2E through `ground_document` (loop-closure, probe-validated):** hierarchical records →
   `ground_document(offer-contract, MappingGroundingProposer{"Current Visit > Result (SI)" →
   ejectionFraction-field}, terms, offer-shapes, g)` → `FeedResult.records == 5`, **grounded > 0**
   (in-range Current-Visit Results ground via the value-constraint oracle through the hierarchical feed),
   **proposed > 0** (out-of-range "252" + unmapped paths quarantine). Robust qualitative split (observed
   4 grounded / 26 proposed), NOT brittle exact counts. The mapping is a **test-local illustrative wiring
   demonstration** — it proves hierarchical path-concepts flow through the oracle, not a domain claim; no
   contract/shape file is modified (offer-shapes reused as-is).

Full `tests/` suite stays green (the change is confined to `feed.table_records` + the new helper;
`ground_document`, `ground_concept`, the etkl compiler, and all shapes are untouched).

## 7. Anti-overfit

The path-walk is pure RDF reads (deepest by `headerLevel`, walk `parentHeader`) — **no tuned constant, no
IRI-name parsing**. Backward compat is guaranteed by the reduction to the single label for flat tables
(not by a special-case branch). The load-bearing guard is the E2E's **quarantine** of out-of-range and
unmapped cells: the oracle still gates through the hierarchical feed — feeding path-concepts does not
rubber-stamp them (§7).

## 8. Scope boundary (YAGNI)

- Handles `tab:HierarchicalTable` + `tab:RecordTable`. **Matrix (cross-tab) is out of scope** — a separate
  later slice (row-header × col-header indexing is a different cell model).
- Path = deepest header walked to root, joined `" > "`; row = record; grounding unchanged.
- Single-token data cells (multi-word / merged data cells out of scope).
- No shared shape / contract changes; the E2E mapping is test-local and illustrative.
- Transposed `RecordTable`s continue to be fed (unchanged; they normalize to `RecordTable`).

## 9. Definition of done (the loop CLOSES for hierarchical tables)

- A merged-header (`HierarchicalTable`) PDF compiles and feeds header-path concepts (root→leaf) —
  `table_records` returns the 5 analyte records with correct paths (RED-checked non-vacuous).
- Those concepts flow through the unchanged `ground_document`: in-range numerics ground via the
  value-constraint oracle, out-of-range/unmapped cells quarantine — `FeedResult(records=5, grounded>0,
  proposed>0)`.
- `RecordTable` output is byte-identical (backward-compatible); full suite green.
- Residue (out-of-range / unmapped cells) quarantined as `CandidateConcept` propositions, never dropped (§7).

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
