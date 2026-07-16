# SHACL-Oracle Region-Admission Gate (Neurosymbolic Loop C) — Design

**Date:** 2026-07-15
**Status:** ✅ **SHIPPED to main 2026-07-16** (PR #45 merged, merge commit c0f35e8). Implemented via subagent-driven development (4 tasks; the final whole-branch review caught a dropped `UnambiguousAccess` leaf-partition invariant → the gate is **eight** shapes, not six, for full parity with the retired exact-partition backstop); plan at `docs/superpowers/plans/2026-07-15-shacl-oracle-region-gate.md`; full suite 358 passed / 5 skipped. (Original status: design approved — retained below as the as-designed record.)
**Governed by:** CLAUDE.md §8 (the neurosymbolic-first gate — **open/closed derivation-vs-constraint split**) + `docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md` (reframe #5 / items D3, E4: redundant Python tiling backstops → the SHACL invariants that already exist).
**Builds on (shipped):** loop one (declarative transform substrate) + loop B (role-derivation axioms). This is the **closed-world mirror** of loop B: loop B lifted *derivation* to open-world SPARQL; loop C lifts a *conformance* check to closed-world SHACL.

---

## 1. Goal

Three Python functions — `matrix.col_tree_tiles`, `matrix.matrix_tiles`, `rowheaders.row_tree_tiles` — **re-implement the tiling invariants that already exist as SHACL** (`tab:CoverageShape` + `tab:NoOverlapShape` + `tab:RefinementShape`, plus the row-axis mirrors). Each checks: *refinement* (`child.covers ⊆ parent.covers`) and *coverage/no-overlap/partition* (`sorted(leaf-header covers) == the full column/row set`). Their own docstrings say *"Catches pathological geometry before it reaches the row SHACL"* — the duplication is acknowledged.

Loop C **deletes the three Python backstops** and replaces them with a **SHACL oracle run over each candidate region's RDF** at the admission point — so the tiling invariant lives **once** (in the shapes), used by both the per-region gate and the final `_validate`. Crucially it **preserves the exact graceful per-region escalation** the backstops provide, which the whole-graph fail-closed `_validate` does not (see §3).

## 2. Gate compliance (CLAUDE.md §8 — the open/closed split)

- **AXIOM — constraint (closed world) → SHACL.** Tiling (coverage / no-overlap / refinement) is a **conformance** check — *"does this header structure conform?"*, not *"what structure is there?"*. It is closed-world (completeness + negative constraints), so it belongs to **SHACL**, not SPARQL. This is the deliberate mirror of loop B (derivation → open-world SPARQL). The **holon is the closure boundary**: SHACL over a single region's scratch graph is conformance scoped to that region-holon.
- **No SPARQL here.** A SPARQL `ASK` would use the open-world query language for a closed-world constraint (the category error §8 forbids) *and* re-express the invariant — defeating the DRY goal. We reuse the existing shapes.
- **PROCEDURAL (justified, each with a why-irreducible note):** (1) emitting a candidate region into a scratch `Graph` (reuses `assert_matrix_region`/`assert_row_hier_region` — raw RDF emission); (2) invoking pySHACL on the scratch graph (engine glue); (3) the merge-or-escalate **disposition** (control flow). No tuned constant (the backstops had none — the check is structural).
- **NEURAL:** none.

## 3. Why the backstops are NOT simply deletable (the disposition the SHACL must preserve)

The two mechanisms are **complementary, not redundant in role**:

| | Python backstop (`matrix_tiles`/`row_tree_tiles`) | SHACL `_validate` (compile.py:55, 226) |
| --- | --- | --- |
| Runs on | the Python geometry tree, **pre-emission** | the emitted RDF graph, **post-emission** |
| Granularity | **per region** | **whole graph** |
| Mis-tile disposition | **escalate that region gracefully**, keep the rest (`escalate_region` → `MATRIX_AMBIGUOUS` / `ROW_GROUP_AMBIGUOUS`) | **`raise AssertionError`** — crashes the entire `compile_tables` call |

A naive deletion (rely on final `_validate`) would turn graceful per-region escalation into a whole-compilation crash — a regression against the loop-definition-of-done ("escalate in-band, no silent gaps"). Loop C therefore keeps the **pre-emission, per-region, graceful** disposition and only changes *how the tiling is checked* (Python-on-tree → SHACL-on-region-RDF).

## 4. Architecture — the SHACL-oracle admission gate

In `compile.py`, at the two admission points, replace the Python-backstop gate with an emit-then-validate-then-dispose oracle:

**Row-hierarchical** (currently compile.py:121 `if rreg is not None and row_tree_tiles(rreg.tree, len(rreg.leaf_rows)):`):
```
rreg = classify_row_hier(band)                                  # unchanged (builds the tree)
if rreg is not None:
    scratch = Graph()
    n = assert_row_hier_region(scratch, rreg, band, table_uri, _DOC, page_number)   # emit to SCRATCH
    if region_tiles(scratch):                                   # SHACL oracle over the region RDF   [AXIOM]
        graph += scratch                                        # admit
        … existing word-fit counting + "asserted" report (unchanged) …
    else:
        escalate_region(graph, cand_uri, _DOC, ascii_view, "ROW_GROUP_AMBIGUOUS", …)   # unchanged
else:
    escalate … (unchanged)
```
**Matrix** (currently compile.py:158 `if mreg is not None and matrix_tiles(mreg):`): the same shape, emitting via `assert_matrix_region`, escalating `MATRIX_AMBIGUOUS`.

`region_tiles(scratch: Graph) -> bool` = pySHACL over the scratch graph against **only the tiling shapes** (see §5), returning `conforms`.

## 5. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `src/iladub/etkl/tiling.py` (create) | `region_tiles(graph) -> bool` — validate a region graph against the cached tiling-shapes set; a module-level cache of the parsed tiling shapes + `tab.ttl` ont | PROCEDURAL (SHACL engine glue) + AXIOM (the shapes) |
| `vocab/shapes/tab-shapes.ttl` (consume) | `tab:CoverageShape`, `NoOverlapShape`, `RefinementShape`, `RowCoverageShape`, `RowNoOverlapShape`, `RowRefinementShape` — already exist; the gate uses **only these six** | AXIOM (owned shapes) |
| `src/iladub/etkl/compile.py` (modify) | the two admission points call `region_tiles(scratch)` instead of `matrix_tiles`/`row_tree_tiles`; emit-to-scratch + merge/escalate | PROCEDURAL (disposition) |
| `src/iladub/etkl/matrix.py` (modify) | **delete** `col_tree_tiles`, `matrix_tiles` | — |
| `src/iladub/etkl/rowheaders.py` (modify) | **delete** `row_tree_tiles` | — |
| `src/iladub/etkl/__init__.py` (modify) | drop the deleted functions from imports + `__all__` | — |
| `src/iladub/etkl/compile.py:_validate` (modify) | reuse the module-level shape/ont cache (perf; no behaviour change) | — |
| `tests/etkl/test_tiling_gate.py` (create) | the differential/equivalence tests (see §6) | test |

**The gate uses only the six tiling shapes** (not all of `tab-shapes.ttl`), so it escalates on *tiling* violations exactly as the backstops did — never a false-escalation on an incidental non-tiling shape (which today would instead crash the whole compile at final `_validate`; loop C changes only the tiling check, nothing else). **DRY-correct subset selection (no duplicate shapes file):** the tiling-shapes graph is built **once at module load** as the union of the *Concise Bounded Descriptions* of the six tiling shape IRIs extracted from the single `vocab/shapes/tab-shapes.ttl` (CBD pulls each `sh:NodeShape` plus its reachable `sh:property`/`sh:sparql`/`sh:message` bnodes). The shapes thus live **once** in `tab-shapes.ttl`; the gate consumes a cached subgraph of them. `_validate` continues to use the full shapes set (also from a module-level cache to avoid re-parsing).

## 6. Testing

- **Shape-level equivalence (anti-overfit):** `test_tiling_gate.py` builds a battery of region RDF graphs — well-tiled + each pathology (coverage gap, sibling overlap, refinement break), both axes (column via `coversColumn`, row via `coversRow`) — and asserts `region_tiles(g)` returns the **same accept/reject the retired backstops gave** (well-tiled → True; each pathology → False). The pathology cases are lifted from the existing `test_col_tree_tiles_rejects_pathology` / `test_row_tree_tiles_rejects_pathology`.
- **Gate integration (no regression):** a real mis-tiled matrix / row-hier region compiled end-to-end **escalates** (`MATRIX_AMBIGUOUS` / `ROW_GROUP_AMBIGUOUS`), keeps other regions, and **does not crash** — the exact behaviour the Python backstop gave.
- **Behavioural spec = the shipped suites, unchanged:** the matrix / row-hier assert + escalate fixtures (`test_matrix.py`, `test_rowheaders.py`, and the end-to-end compile tests) stay green. The retired backstops' *unit* tests (`test_col_tree_tiles_*`, `test_row_tree_tiles_*`, `matrix_tiles`) are **re-expressed** as the shape-level equivalence tests above (they tested the retired Python; supersession, not loosening).
- **No new tuned constant** enters the transform (the gate is SHACL + engine glue; confirm `region_tiles`/`tiling.py` carry no numeric tolerance).

## 7. Source ownership / conventions

- The six tiling shapes are **owned** (`tab:` subjects) and already in `vocab/shapes/tab-shapes.ttl` — consumed, not modified. No HGA/FnO term as a subject. `tiling.py` references only `tab:` shapes + `tab.ttl` + pySHACL.
- pySHACL is already a dependency (used by `_validate`). No new runtime dependency.

## 8. Honest gaps & scope boundaries

- **In scope:** the three tiling backstops (`col_tree_tiles`, `matrix_tiles`, `row_tree_tiles`) → the SHACL-oracle per-region gate, preserving graceful escalation; deleting the Python.
- **Out of scope:**
  - `merge_tiling_ok` (compile.py:186, hierarchical path) — a *different* audit item (C4): a **centering** consistency check carrying a `0.5*pitch` tolerance, which is NEURAL-adjacent (a tuned tolerance), **not** the structural coverage/no-overlap/refinement tiling. It is not touched here.
  - the `compile.py` routing **cascade** itself (K1, hand-ordered `if/elif`) and `regions.classify` (B-family) — separate AXIOM candidates.
  - `is_matrix_candidate` / `classify_matrix` / `classify_row_hier` — the classifiers that *build* the trees are untouched; only the *tiling verification* moves to SHACL.
- **Perf:** pySHACL-per-candidate-region is heavier than the deleted Python check, mitigated by the module-level shape/ont cache (parse once). Matrix/row-hier candidates per page are few; acceptable. Measured against the principle (closed-world → SHACL), the small overhead is the right trade.

## 9. Settled design decisions (for the implementation plan)

- **Mechanism: pySHACL over each candidate region's scratch graph, tiling shapes only, cached** — emit-to-scratch → validate → merge-if-conforms / escalate-if-not. *Not* SPARQL (conformance is closed-world → SHACL, per §8). *Not* a naive delete (§3 — would regress graceful escalation to a whole-compile crash).
- **All three backstops in this slice** (`col_tree_tiles`, `matrix_tiles`, `row_tree_tiles`) + their `__init__` exports deleted.
- **Escalation reasons + word-fit counting preserved byte-identically** (`MATRIX_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`); only the tiling *check* changes.
- **Anti-overfit:** shape-level equivalence over a pathology battery (both axes) + an end-to-end escalation integration test; behavioural suites stay green.

**Resume pointer:** design committed on `main`. **Next action:** invoke `superpowers:writing-plans` on this spec → task-by-task plan (tiling.py + region_tiles with cache → shape-level equivalence battery → rewire the two compile admission points → delete the backstops + re-express their unit tests → supersession verification) → subagent-driven execution. **After C:** B2 (geometry-bound type/boundary via a mid-compile typed-cell evidence graph) and loop two (NEURAL span-perception) remain queued.
