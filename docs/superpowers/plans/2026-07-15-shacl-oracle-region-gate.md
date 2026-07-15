# SHACL-Oracle Region-Admission Gate (Loop C) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three Python tiling backstops (`matrix.col_tree_tiles`, `matrix.matrix_tiles`, `rowheaders.row_tree_tiles`) — which re-implement `tab:CoverageShape`+`NoOverlapShape`+`RefinementShape` (and row mirrors) in Python — with a declarative **SHACL oracle over each candidate region's RDF**, deleting the Python while preserving the exact graceful per-region escalation.

**Architecture:** A `region_tiles(graph) -> bool` oracle (feasibility-proven 2026-07-15) runs pySHACL over a candidate region's RDF against **only the six tiling shapes**, extracted **once** from the single `vocab/shapes/tab-shapes.ttl` as the union of the CBDs of the six shape IRIs + `tab:prefixes` (DRY — no duplicate shapes file), cached module-level. In `compile.py` the two admission points emit each candidate to a **scratch `Graph`**, call `region_tiles(scratch)`, and **merge (assert) if it conforms, else escalate that region** (`MATRIX_AMBIGUOUS` / `ROW_GROUP_AMBIGUOUS`) — byte-identical disposition to today. This is the closed-world (SHACL) mirror of loop B's open-world (SPARQL) derivation.

**Tech Stack:** Python 3, rdflib (CBD extraction), pySHACL (already a dependency, used by `_validate`), pytest. No new dependency.

## Global Constraints

Copied verbatim from CLAUDE.md §8 (the gate, open/closed split) and the spec (`docs/superpowers/specs/2026-07-15-shacl-oracle-region-gate-design.md`). Every task's requirements implicitly include this section. **Reviewers enforce it.**

- **AXIOM — constraint (closed world) → SHACL.** Tiling (coverage / no-overlap / refinement) is a *conformance* check, closed-world → **SHACL**, reusing the existing shapes. **No SPARQL `ASK`** (that would misuse the open-world tool for a closed-world constraint *and* re-duplicate the invariant, per §8). **No tuned constant** anywhere in `tiling.py`/the gate (the backstops had none — the check is structural).
- **PROCEDURAL (justified, each with a why-irreducible note):** (1) emitting a candidate region into a scratch `Graph` (raw RDF emission via the existing `assert_*_region`); (2) invoking pySHACL (engine glue); (3) the merge-or-escalate **disposition** (control flow). No transform/role logic in Python.
- **Preserve the disposition byte-identically:** the backstops give **pre-emission, per-region, graceful** escalation; the whole-graph `_validate` **raises `AssertionError`** on any violation. Loop C keeps the graceful per-region escalation — a naive delete would regress it to a whole-compile crash (against loop-definition-of-done). Escalation reasons (`MATRIX_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`), the `escalate_region(...)` call, and the word-fit `asserted_total`/`escalated_total` counting are unchanged; only the tiling *check* moves from Python to SHACL.
- **DRY:** the tiling shapes live **once** in `vocab/shapes/tab-shapes.ttl`. The gate consumes a cached CBD subgraph of the six; it does **not** copy them into a new file.
- **Anti-overfit:** shape-level equivalence over a *battery* of region graphs — well-tiled + each pathology (coverage gap, sibling overlap, refinement break), both axes — asserting `region_tiles` matches the retired backstops' accept/reject; plus an end-to-end escalation integration test. Never tuned to one fixture.
- **Behavioural spec = the shipped suites, unchanged:** the matrix / row-hier assert + escalate fixtures (`test_matrix.py`, `test_rowheaders.py`, end-to-end compile tests) stay green. The retired backstops' *unit* tests are re-expressed as shape-level equivalence tests (supersession, not loosening).
- **Source ownership:** the six tiling shapes are owned `tab:` terms in `tab-shapes.ttl` (consumed, not modified); `tiling.py` references only `tab:` shapes + `tab.ttl` + pySHACL. No HGA/FnO term as a subject.
- **Scope:** ONLY the three tiling backstops → SHACL gate. **Out of scope:** `merge_tiling_ok` (compile.py:186 — a *centering* check with a `0.5*pitch` tuned tolerance, NEURAL-adjacent, a different audit item); the `compile.py` routing cascade (K1); `regions.classify`; and the tree *classifiers* (`is_matrix_candidate`/`classify_matrix`/`classify_row_hier`) — only the tiling *verification* moves.

---

## File Structure

**Create:**
- `src/iladub/etkl/tiling.py` — `region_tiles(graph) -> bool` + the module-level cached tiling-shapes graph (CBD subset) + `tab.ttl` ont. [PROCEDURAL glue over AXIOM shapes]
- `tests/etkl/test_tiling_gate.py` — shape-level equivalence battery + the end-to-end escalation integration test + the retirement gate assertions.

**Modify:**
- `src/iladub/etkl/compile.py` — the matrix (≈:158) and row-hier (≈:121) admission points call `region_tiles(scratch)` instead of `matrix_tiles`/`row_tree_tiles`; emit-to-scratch + merge/escalate. `_validate` reuses a module-level full-shapes/ont cache (perf; no behaviour change).
- `src/iladub/etkl/matrix.py` — delete `col_tree_tiles`, `matrix_tiles`.
- `src/iladub/etkl/rowheaders.py` — delete `row_tree_tiles`.
- `src/iladub/etkl/__init__.py` — drop the three deleted names from imports + `__all__`.
- `tests/etkl/test_matrix.py`, `tests/etkl/test_rowheaders.py` — remove the retired backstops' unit tests (their coverage moves to `test_tiling_gate.py`).

---

## Task 1: `tiling.py` — `region_tiles` oracle + shape-level equivalence battery

Build and prove the SHACL oracle. The `region_tiles` body + CBD extraction below are **feasibility-proven** (2026-07-15): the CBD subset of the six shapes + `tab:prefixes` is a self-contained 6-NodeShape graph, and `region_tiles` accepts a well-tiled region and rejects each pathology.

**Files:**
- Create: `src/iladub/etkl/tiling.py`
- Create: `tests/etkl/test_tiling_gate.py`

**Interfaces:**
- Produces: `tiling.region_tiles(graph: rdflib.Graph) -> bool` — True iff `graph` conforms to the six tiling shapes (`CoverageShape`/`NoOverlapShape`/`RefinementShape` + row mirrors). Consumed by `compile.py` (Task 2).

- [ ] **Step 1: Write the failing shape-level battery test**

Create `tests/etkl/test_tiling_gate.py`:

```python
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _region(cover, axis="column"):
    """cover: {header-uri: (level, parent-or-None, [leaves])}. Leaves c1..c3 on `axis`."""
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    cls = TAB.LeafColumn if axis == "column" else TAB.LeafRow
    g = Graph(); t = EX.t
    for c in (EX.c1, EX.c2, EX.c3):
        g.add((c, RDF.type, cls)); g.add((t, lp, c))
    for h, (lvl, parent, cols) in cover.items():
        g.add((h, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(lvl)))
        if parent is not None:
            g.add((h, TAB.parentHeader, parent))
        for c in cols:
            g.add((h, cp, c))
    return g


def _battery(axis):
    well = _region({EX.h0: (0, None, [EX.c1, EX.c2, EX.c3]),
                    EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2]), EX.h3: (1, EX.h0, [EX.c3])}, axis)
    gap = _region({EX.h0: (0, None, [EX.c1, EX.c2]),
                   EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2])}, axis)              # c3 uncovered
    overlap = _region({EX.h0: (0, None, [EX.c1, EX.c2, EX.c3]),
                       EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c1, EX.c2]),          # h1,h2 share c1 @ lvl1
                       EX.h3: (1, EX.h0, [EX.c3])}, axis)
    refine = _region({EX.h0: (0, None, [EX.c1, EX.c2]),                                       # parent misses c3
                      EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2]), EX.h3: (1, EX.h0, [EX.c3])}, axis)
    return {"well": (well, True), "gap": (gap, False), "overlap": (overlap, False), "refine": (refine, False)}


def test_region_tiles_matches_backstop_semantics():
    from iladub.etkl.tiling import region_tiles
    for axis in ("column", "row"):
        for name, (g, expect) in _battery(axis).items():
            assert region_tiles(g) is expect, "%s-%s: got %s expect %s" % (axis, name, region_tiles(g), expect)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/etkl/test_tiling_gate.py::test_region_tiles_matches_backstop_semantics -v`
Expected: FAIL — `ModuleNotFoundError: iladub.etkl.tiling`.

- [ ] **Step 3: Implement `tiling.py` (the proven oracle)**

Create `src/iladub/etkl/tiling.py`:

```python
"""tiling — the SHACL-oracle region-admission gate (neurosymbolic loop C).

Tiling (coverage / no-overlap / refinement) is a CONFORMANCE check — closed-world — so it
belongs to SHACL, reusing the existing tab: tiling shapes (the closed-world mirror of loop B's
open-world SPARQL derivation). The ONLY Python here is PROCEDURAL engine glue: build the tiling
shapes subset once, and invoke pySHACL. No transform logic, no tuned constant. Irreducible
because a SHACL engine must be invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

import os

from rdflib import Graph, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")
_VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab")
# Eight shapes: Coverage/NoOverlap/Refinement + row mirrors, PLUS the two Unambiguous shapes.
# The retired backstops checked EXACT leaf-partition, which implies "exactly one LEAF header per
# column/row" — i.e. UnambiguousAccessShape. Dropping it (final-review Critical) let a parent-only-
# covered column pass the gate, merge, and crash the whole compile at final _validate. All eight
# already exist in tab-shapes.ttl (pure reuse).
_TILING_SHAPE_IRIS = [TAB.CoverageShape, TAB.NoOverlapShape, TAB.RefinementShape,
                      TAB.RowCoverageShape, TAB.RowNoOverlapShape, TAB.RowRefinementShape,
                      TAB.UnambiguousAccessShape, TAB.UnambiguousRowAccessShape]


def _build_tiling_shapes():
    """The six tiling shapes extracted from the single tab-shapes.ttl as CBDs (+ tab:prefixes,
    which the sh:sparql shapes reference). Keeps ONE source of the shapes — no duplicate file."""
    full = Graph().parse(os.path.join(_VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    sub = Graph()
    for s in _TILING_SHAPE_IRIS + [TAB.prefixes]:
        sub += full.cbd(s)
    return sub


_TILING_SHAPES = _build_tiling_shapes()               # cached at import — parsed once
_ONT = Graph().parse(os.path.join(_VOCAB, "ontology", "tab.ttl"), format="turtle")


def region_tiles(graph):
    """True iff `graph` (one candidate region's RDF) conforms to the six tiling invariants
    (coverage / no-overlap / refinement, both axes). PROCEDURAL glue over the AXIOM shapes."""
    from pyshacl import validate
    conforms, _, _ = validate(graph, shacl_graph=_TILING_SHAPES, ont_graph=_ONT,
                              inference="rdfs", advanced=True)
    return conforms
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/etkl/test_tiling_gate.py::test_region_tiles_matches_backstop_semantics -v`
Expected: PASS — all 8 cases (both axes × well/gap/overlap/refine). If a pathology conforms (should reject) or well-tiled fails, the CBD subset is incomplete — verify `tab:prefixes` is included and the six shapes are present (`len(list(_TILING_SHAPES.subjects(RDF.type, SH.NodeShape))) == 6`).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/tiling.py tests/etkl/test_tiling_gate.py
git commit -m "feat(etkl): region_tiles SHACL oracle + shape-level equivalence battery [C task 1]

Tiling = closed-world conformance -> SHACL. region_tiles validates a candidate region against the
six tiling shapes, extracted once from tab-shapes.ttl as CBDs (DRY, no duplicate file). Proven to
accept well-tiled and reject coverage-gap/overlap/refinement-break, both axes.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Rewire the two `compile.py` admission points to the oracle

Replace `matrix_tiles`/`row_tree_tiles` at the admission points with emit-to-scratch → `region_tiles` → merge/escalate, preserving disposition byte-identically. Refactor `_validate` to reuse a module-level cache.

**Files:**
- Modify: `src/iladub/etkl/compile.py`

**Interfaces:**
- Consumes: `tiling.region_tiles` (Task 1); the existing `assert_matrix_region`/`assert_row_hier_region(g, reg, band, table_uri, doc, page)`, `escalate_region`, `column_of`.

- [ ] **Step 1: Rewire the row-hierarchical admission point**

In `src/iladub/etkl/compile.py`, replace the row-hier block (currently ≈ lines 117-141, the `elif looks_row_grouped(region):` body). Change the import and the gate from `row_tree_tiles(rreg.tree, len(rreg.leaf_rows))` to the scratch-emit oracle:

```python
            elif looks_row_grouped(region):
                from .rowheaders import classify_row_hier
                from .holon import assert_row_hier_region
                from .tiling import region_tiles
                rreg = classify_row_hier(band)
                table_uri = URIRef(f"{_DOC}#rhtable{idx}")
                scratch = Graph()
                if rreg is not None:
                    n = assert_row_hier_region(scratch, rreg, band, table_uri, _DOC, page_number)
                if rreg is not None and region_tiles(scratch):
                    graph += scratch
                    b = rreg.grid.boundaries
                    for rb in rreg.leaf_rows:
                        for c in rb.cells:
                            col = column_of((c.x0 + c.x1) / 2.0, b)
                            if col in rreg.data_cols:
                                fits = all(b[col] - 0.5 <= w.x0 and w.x1 <= b[col + 1] + 0.5 for w in c.words)
                                (asserted_total, escalated_total) = (
                                    (asserted_total + len(c.words), escalated_total) if fits
                                    else (asserted_total, escalated_total + len(c.words)))
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view))
                else:
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "ROW_GROUP_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "ROW_GROUP_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
```

(`Graph` is already imported in `compile.py`. Note the region is emitted into `scratch`; on conformance it is merged with `graph += scratch`, on non-conformance `scratch` is discarded and the region escalated — exactly the old assert-vs-escalate outcome, now gated by SHACL.)

- [ ] **Step 2: Rewire the matrix admission point**

In `src/iladub/etkl/compile.py`, replace the matrix block (currently ≈ lines 152-179, the `if is_matrix_candidate(band):` body). Change the gate from `matrix_tiles(mreg)` to the scratch-emit oracle:

```python
        else:  # UNSUPPORTED_TABLE
            from .matrix import is_matrix_candidate
            if is_matrix_candidate(band):
                from .matrix import classify_matrix
                from .holon import assert_matrix_region
                from .tiling import region_tiles
                mreg = classify_matrix(band)
                table_uri = URIRef(f"{_DOC}#mtable{idx}")
                scratch = Graph()
                if mreg is not None:
                    n = assert_matrix_region(scratch, mreg, band, table_uri, _DOC, page_number)
                if mreg is not None and region_tiles(scratch):
                    graph += scratch
                    b = mreg.grid.boundaries
                    for rb in mreg.leaf_rows:
                        for sc in rb.cells:
                            col = column_of((sc.x0 + sc.x1) / 2.0, b)
                            if col in mreg.data_cols:
                                fits = all(b[col] - 0.5 <= w.x0 and w.x1 <= b[col + 1] + 0.5 for w in sc.words)
                                if fits:
                                    asserted_total += len(sc.words)
                                else:
                                    escalated_total += len(sc.words)
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view))
                else:
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "MATRIX_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "MATRIX_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing Loop 2 hierarchical path, UNCHANGED (merge_tiling_ok stays) ----
```

(Leave the `else:` hierarchical path — including `merge_tiling_ok` — untouched; it is out of scope.)

- [ ] **Step 3: Refactor `_validate` to reuse a module-level full-shapes cache (perf, no behaviour change)**

In `src/iladub/etkl/compile.py`, replace the body of `_validate` (currently re-parses shapes+ont every call) with a cached version:

```python
_FULL_SHAPES = None
_FULL_ONT = None


def _validate(graph: Graph) -> tuple[bool, str]:
    from pyshacl import validate
    global _FULL_SHAPES, _FULL_ONT
    if _FULL_SHAPES is None:
        v = _repo_vocab()
        s = Graph()
        s.parse(os.path.join(v, "shapes", "tab-shapes.ttl"), format="turtle")
        s.parse(os.path.join(v, "shapes", "tab-physical-shapes.ttl"), format="turtle")
        _FULL_SHAPES = s
        _FULL_ONT = Graph().parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(graph, shacl_graph=_FULL_SHAPES, ont_graph=_FULL_ONT,
                                 inference="rdfs", advanced=True)
    return conforms, text
```

- [ ] **Step 4: Run the behavioural suites**

Run: `python3 -m pytest tests/etkl/test_matrix.py tests/etkl/test_rowheaders.py tests/etkl/test_closing_slice.py tests/etkl/test_hier_escalation.py -v`
Expected: PASS — matrix/row-hier assert fixtures still assert (the well-tiled regions conform → merged), escalate fixtures still escalate. (`test_matrix.py`/`test_rowheaders.py` still reference the not-yet-deleted backstops; those unit tests are removed in Task 3. If an import of the still-present `col_tree_tiles` etc. is unaffected, they pass; the *rewire* is what this task verifies.)

Run the full etkl suite: `python3 -m pytest tests/etkl -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/compile.py
git commit -m "refactor(etkl): compile admission points gate on the SHACL region_tiles oracle [C task 2]

Matrix + row-hier candidates emit to a scratch graph, validate against the tiling shapes, and
merge-if-conforms / escalate-if-not (MATRIX_AMBIGUOUS / ROW_GROUP_AMBIGUOUS) — graceful per-region
disposition preserved. _validate now reuses a module-level shapes/ont cache.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Delete the three Python backstops + re-express their unit tests

The backstops are now dead (compile no longer calls them). Delete them, their exports, and re-express their unit tests as the shape-level equivalence coverage (already in `test_tiling_gate.py`).

**Files:**
- Modify: `src/iladub/etkl/matrix.py`, `src/iladub/etkl/rowheaders.py`, `src/iladub/etkl/__init__.py`, `tests/etkl/test_matrix.py`, `tests/etkl/test_rowheaders.py`

- [ ] **Step 1: Delete the backstop functions**

- In `src/iladub/etkl/matrix.py`: delete `col_tree_tiles` (≈:79-90) and `matrix_tiles` (≈:144-149).
- In `src/iladub/etkl/rowheaders.py`: delete `row_tree_tiles` (≈:119-132).

- [ ] **Step 2: Drop the deleted names from `__init__.py`**

In `src/iladub/etkl/__init__.py`, remove `col_tree_tiles`, `matrix_tiles`, `row_tree_tiles` from the `from .matrix import (...)` / `from .rowheaders import (...)` lines AND from `__all__` (lines ≈17,19-20,37,39-40). Verify no other module imports them (grep).

- [ ] **Step 3: Remove the retired backstops' unit tests**

- In `tests/etkl/test_matrix.py`: remove `test_col_tree_tiles*` and the `matrix_tiles` assertion in `test_matrix_tiles*` (the tiling coverage now lives in `test_tiling_gate.py`). Keep the classifier/proximity tests. Update the top-level import to drop `col_tree_tiles`, `matrix_tiles`.
- In `tests/etkl/test_rowheaders.py`: remove `test_row_tree_tiles_true` and `test_row_tree_tiles_rejects_pathology`; drop `row_tree_tiles` from the import.

- [ ] **Step 4: Run the suites**

Run: `python3 -m pytest tests/etkl/test_matrix.py tests/etkl/test_rowheaders.py tests/etkl/test_tiling_gate.py -v`
Expected: PASS (no import errors for the deleted names; the remaining classifier tests + the tiling battery green).

Run: `python3 -m pytest tests/etkl -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/matrix.py src/iladub/etkl/rowheaders.py src/iladub/etkl/__init__.py tests/etkl/test_matrix.py tests/etkl/test_rowheaders.py
git commit -m "refactor(etkl): delete Python tiling backstops (col_tree_tiles/matrix_tiles/row_tree_tiles) [C task 3]

Superseded by the region_tiles SHACL oracle; the invariant now lives once, in the shapes. Their
unit tests are re-expressed as the shape-level equivalence battery in test_tiling_gate.py.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: End-to-end escalation integration test + supersession/gate verification

Prove the disposition end-to-end (a real mis-tiled region escalates gracefully, no crash) and pin the retirement + the gate.

**Files:**
- Modify: `tests/etkl/test_tiling_gate.py`, `tests/etkl/test_transform_gate.py`

- [ ] **Step 1: Add the end-to-end escalation integration test**

No real PDF fixture naturally mis-tiles (the classifiers build well-tiled trees from valid geometry), so the disposition is tested deterministically by making the oracle reject a normally-asserting region and asserting graceful escalation. This exercises the exact Task-2 else-branch (`CompilationReport.regions` holds `RegionReport(verdict, reason, …)`; `row_grouped_table_pdf` compiles into an asserted row-hier table via the `ROW_GROUP` path).

Add to `tests/etkl/test_tiling_gate.py`:

```python
import pytest


def test_gate_reject_escalates_gracefully(tmp_path, monkeypatch):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import compile_tables
    import iladub.etkl.tiling as tiling
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))

    # Positive path: normally this row-grouped region tiles and is asserted.
    rep_ok = compile_tables(str(p))
    assert any(r.verdict == "asserted" for r in rep_ok.regions)

    # Disposition: when the SHACL oracle REJECTS the region, compile must escalate THAT region
    # gracefully (ROW_GROUP_AMBIGUOUS) — NOT raise, NOT crash the whole compile.
    monkeypatch.setattr(tiling, "region_tiles", lambda g: False)
    rep_esc = compile_tables(str(p))                                 # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "ROW_GROUP_AMBIGUOUS" for r in rep_esc.regions)
```

(`compile.py` does `from .tiling import region_tiles` locally inside the admission block, so `monkeypatch.setattr(tiling, "region_tiles", …)` is picked up at call time. This is the definitive disposition test: gate-reject → graceful per-region escalation, no whole-compile crash — the behaviour a naive delete would have lost.)

- [ ] **Step 2: Add the retirement + gate assertions**

Add to `tests/etkl/test_transform_gate.py`:

```python
def test_tiling_backstops_retired_and_gate_present():
    import iladub.etkl.matrix as m, iladub.etkl.rowheaders as rh, iladub.etkl.tiling as tl
    assert not hasattr(m, "col_tree_tiles") and not hasattr(m, "matrix_tiles"), "matrix tiling backstops retired"
    assert not hasattr(rh, "row_tree_tiles"), "row tiling backstop retired"
    assert hasattr(tl, "region_tiles"), "the SHACL region-admission oracle must exist"
```

Also add a no-tuned-constant assertion for `tiling.py` (mirror the `.rq` one): strip `#` comments, assert no `\d+\.\d+` float literal in `tiling.py`.

- [ ] **Step 3: Run gate + whole suite**

Run: `python3 -m pytest tests/etkl/test_tiling_gate.py tests/etkl/test_transform_gate.py -v`
Expected: PASS.

Run: `python3 -m pytest tests/etkl -q`, then the source-ownership test (`python3 -m pytest tests/test_source_ownership.py -v`), then the full project suite `python3 -m pytest -q`.
Expected: PASS (only pre-existing skips).

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_tiling_gate.py tests/etkl/test_transform_gate.py
git commit -m "test(etkl): end-to-end mis-tile escalation + retirement/gate for the SHACL region oracle [C task 4]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage** (against `2026-07-15-shacl-oracle-region-gate-design.md`):
- §1/§4 the three backstops → SHACL oracle per region, preserving escalation → Tasks 1-3. ✔
- §2 AXIOM constraint (closed-world SHACL), PROCEDURAL glue, no tuned constant → Global Constraints + Task 1/4. ✔
- §3 disposition preserved byte-identically (reasons, word-fit counting, per-region graceful) → Task 2. ✔
- §5 `tiling.py` + `region_tiles` + CBD subset + cache; `_validate` cache reuse → Tasks 1-2. ✔
- §5 DRY (CBD subset, no duplicate file) → Task 1 `_build_tiling_shapes`. ✔
- §6 shape-level equivalence battery (both axes) + end-to-end escalation + behavioural green + re-express backstop unit tests → Tasks 1,3,4. ✔
- §7 source ownership → Task 4 (source-ownership test). ✔
- §8 out-of-scope (`merge_tiling_ok`, cascade, classifiers) → Global Constraints + Task 2 note. ✔

**2. Placeholder scan:** Clean — the Task-4 integration test is fully concrete (monkeypatch `region_tiles→False` on the real `row_grouped_table_pdf` fixture, `CompilationReport.regions` / `RegionReport.verdict`/`reason` confirmed against the source). No placeholders; `tiling.py`, the battery, and the compile rewire are complete and feasibility-proven.

**3. Type consistency:** `region_tiles(graph: Graph) -> bool` (Task 1) used identically in the two admission points (Task 2). `assert_matrix_region`/`assert_row_hier_region(g, reg, band, table_uri, doc, page) -> int` reused as-is (emitting to `scratch`). The module-level caches (`_TILING_SHAPES`, `_FULL_SHAPES`) are parse-once Graphs. `_battery(axis)` / `_region(cover, axis)` consistent across Task-1 and Task-4 tests.
