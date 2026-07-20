# SPARQL Derivation Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the super-linear cell-typing SPARQL derivations to a linear aggregation form so the table compiler compiles real multi-row reports (a ~50-row grouped-header table hangs today), with **byte-identical results** guarded by the celltype differential oracle + a randomized new-vs-old test.

**Architecture:** `header-body-split.rq` and `stub-data-split.rq` contain a cell-pair self-join (`?ca … ?cb … FILTER(?cat != ?cbt)`) re-evaluated per candidate split row → O(n²·c²). Replace with a `GROUP BY ?col` aggregation: per column, `T` = the bottom (max-row) cell's `cellDatatype` (a self-join-free groupwise-max), and the column's boundary = `1 + MAX(row of a cell whose type ≠ T)`; the answer is `MIN`/suffix over columns. Linear in cells. **Form changes, decision does not.**

**Tech Stack:** SPARQL 1.1 (rdflib), `pySHACL` unaffected, `pytest`. The evidence graph (`celltype.grid_evidence`) and readers are unchanged.

## Global Constraints

- **Test interpreter (MANDATORY):** run every test via `./.venv/bin/python -m pytest …` (rdflib 7.6.0). Bare `python`/`python3`/`pytest` uses a different env (rdflib 7.1.4) with spurious failures. Wherever a step says `pytest …`, execute `./.venv/bin/python -m pytest …`.
- **Semantics are frozen — form-only change (§8 AXIOM):** every rewritten query MUST return the *same* value as the current one on every input. The equivalence proof is: (1) the shipped celltype differential oracle (`tests/etkl/test_celltype.py`, the `_ref_*` batteries) stays green; (2) a **randomized differential test** — the new query vs the **current (old) query text** — matches on every generated grid (incl. Numeric/Date/Currency/Text, all-Text→None, ragged, empty columns). **If a rewrite changes any result, it is wrong — reconcile the query against the reference; never edit a fixture or the reference to make it pass.**
- **No tuned constant, no procedural leak:** the decision stays entirely in the `.rq`. The evidence-graph builder (`grid_evidence`) is unchanged — do NOT move any decision (bottom-type, homogeneity) into Python; the query must decide.
- **No vocab change:** the queries read the same `tab:` predicates (`atGridRow`, `atGridColumn`, `cellDatatype`, `tab:Text`, `columnIndex`). No new terms.
- **Ownership/licensing:** queries are CC-BY-4.0, `tab:` namespace only. Author François Rosselet © 2026.
- **Full suite** via `.venv` at the end; baseline **406 passed / 5 skipped** (post-grounding-merge). Zero regressions.

## File Structure

- **Modify** `vocab/queries/header-body-split.rq` — aggregation form (Task 1).
- **Create** `tests/etkl/test_derivation_equiv.py` — randomized new-vs-old differential test (Task 1), reused for stub (Task 3).
- **Create** `tests/etkl/test_derivation_perf.py` — the row-count profiling + per-query perf regression guard (Task 2) and the realistic end-to-end report (Task 4).
- **Modify** `vocab/queries/stub-data-split.rq` — aggregation form (Task 3); any other query the audit finds super-linear.
- **No change** to `src/iladub/etkl/celltype.py`, `rowheaders.py`, readers, or any vocab TTL.

Verified facts (read if unsure): `grid_evidence(cells, ncols)` emits `tab:GridCell` with `atGridRow`/`atGridColumn`/`gridText`/`cellDatatype` + `columnIndex` markers; `run_scalar(rq_path, graph, bindings=None) -> int|None` (stub-data-split takes `initBindings={'split': Literal(int)}`); the differential oracle grid format is `list[row]`, `row = list[(col, text)]`, `_cells(grid)` flattens to `(r,c,t)`.

---

### Task 1: Rewrite `header-body-split.rq` to the aggregation form + randomized differential test

**Files:**
- Modify: `vocab/queries/header-body-split.rq`
- Create: `tests/etkl/test_derivation_equiv.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`, `celltype.run_scalar`.
- Produces: the rewritten query (same `?split` scalar result); a reusable `_rand_grids(...)` generator + a query-equivalence assertion.

- [ ] **Step 1: Write the randomized differential test (new query vs OLD query text)**

Create `tests/etkl/test_derivation_equiv.py`. It runs BOTH the committed (old) query text and the new query file against generated grids and asserts equal results. Capture the OLD text NOW (before Step 3 overwrites the file) by embedding it as a string constant.

```python
import os, random
from rdflib import Literal
from rdflib.namespace import XSD
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")

def _run_text(query_text, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    for row in g.query(query_text, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None

# The CURRENT (pre-rewrite) header-body-split.rq, pasted verbatim as the reference oracle.
# (Copy the exact file contents here before Step 3 changes the file.)
OLD_HBS = r"""<PASTE the current vocab/queries/header-body-split.rq verbatim here>"""

_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", ""]   # Numeric/Currency/Date/Text/blank

def _rand_grids(seed, n=200):
    rnd = random.Random(seed)
    for _ in range(n):
        ncols = rnd.randint(1, 4)
        nrows = rnd.randint(1, 9)         # keep small so the O(n^2) OLD query stays fast
        cells = []
        for r in range(nrows):
            for c in range(ncols):
                if rnd.random() < 0.85:   # ~15% missing -> ragged/empty columns
                    cells.append((r, c, rnd.choice(_TYPES)))
        yield cells, ncols

def test_header_body_split_new_matches_old():
    new_path = os.path.join(QDIR, "header-body-split.rq")
    new_text = open(new_path, encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=1):
        old = _run_text(OLD_HBS, cells, ncols)
        new = _run_text(new_text, cells, ncols)
        assert old == new, f"divergence ncols={ncols} cells={cells}: old={old} new={new}"
```

- [ ] **Step 2: Run it — verify it PASSES against the current query (sanity: old==old shape) and will catch divergence**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_equiv.py -q`
Expected: PASS now (the new file still equals OLD). This confirms the harness is sound before you change the query. (If it fails now, the OLD_HBS paste is wrong — fix the paste.)

- [ ] **Step 3: Rewrite `vocab/queries/header-body-split.rq`**

Replace the file with the aggregation form (verified against the shipped `HB_BATTERY`):

```sparql
# header-body-split.rq — MIN body-start row s>=1 such that some column is homogeneous non-Text
# on [s..end]. AGGREGATION FORM (linear in cells): per column, T = the bottom (max-row) cell's
# cellDatatype (self-join-free groupwise-max); a non-Text-bottom column's boundary is
# 1 + MAX(row of a cell whose type != T) (or 1 if none differ); the answer is MIN over columns.
# Equivalent to the prior pairwise form — a column is homogeneous non-Text on [s..end] for all
# s >= s_col — proven by the celltype differential oracle + the randomized new-vs-old test
# (tests/etkl/test_derivation_equiv.py). No pair self-join, no per-split re-evaluation.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?s_col) AS ?split) WHERE {
  {
    SELECT ?col (IF(MAX(?diffrow) >= 0, MAX(?diffrow) + 1, 1) AS ?s_col) WHERE {
      {
        SELECT ?col ?T WHERE {
          ?bc tab:atGridColumn ?col ; tab:atGridRow ?br ; tab:cellDatatype ?T .
          { SELECT ?col (MAX(?r2) AS ?maxr) WHERE {
              ?c2 tab:atGridColumn ?col ; tab:atGridRow ?r2 .
          } GROUP BY ?col }
          FILTER(?br = ?maxr)
        }
      }
      FILTER(?T != tab:Text)
      ?cell tab:atGridColumn ?col ; tab:atGridRow ?crow ; tab:cellDatatype ?ct .
      BIND(IF(?ct != ?T, ?crow, -1) AS ?diffrow)
    } GROUP BY ?col
  }
  FILTER(?s_col >= 1)
}
```

- [ ] **Step 4: Run the equivalence + the shipped celltype differential oracle**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_equiv.py tests/etkl/test_celltype.py -q`
Expected: all PASS. The randomized test now compares the NEW query vs OLD text (must match on all 200 grids); the celltype oracle (`test_header_body_split_matches_reference`, `..._recall_and_precision`) must stay green — that IS the equivalence proof. If any grid diverges, the print shows the exact grid; fix the query (a groupwise-max or an edge like an all-non-Text column), NOT the test.

- [ ] **Step 5: Confirm it scales (the point of the task)**

Run this inline check:
`./.venv/bin/python -c "import time; from iladub.etkl import celltype; import os; QDIR=os.path.join(os.path.dirname(celltype.__file__),'..','..','..','vocab','queries'); cells=[(r,c,('Hdr' if r==0 else str(r))) for r in range(51) for c in range(4)]; g=celltype.grid_evidence(cells,4); t=time.time(); print('split=',celltype.run_scalar(os.path.join(QDIR,'header-body-split.rq'),g),'time=%.3fs'%(time.time()-t))"`
Expected: prints in well under 1s (was >25s / hang for 15+ rows).

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/header-body-split.rq tests/etkl/test_derivation_equiv.py
git commit -m "perf(etkl): header-body-split.rq -> linear aggregation form (equivalence-guarded)"
```

---

### Task 2: Audit every derivation vs row count + perf regression guard

**Files:**
- Create: `tests/etkl/test_derivation_perf.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`, `celltype.run_scalar`/`run_ask`, every `vocab/queries/*.rq`.
- Produces: a profiling helper + a per-query wall-clock regression guard; a recorded profile table (in the report).

- [ ] **Step 1: Write the profiling + perf-guard test**

Create `tests/etkl/test_derivation_perf.py`. Profile each row-count-sensitive query at n=5/20/50; assert the row-count-sensitive ones (header-body-split, stub-data-split, and any the profile flags) return under a generous wall-clock bound at n=50. Queries that read only header words / column markers (not body rows) are noted, not bounded.

```python
import os, time
import pytest
from rdflib import Literal
from rdflib.namespace import XSD
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")

def _grid(nrows, ncols=4):
    # a grouped-header-ish grid: row 0 header (Text), then numeric body
    return [(r, c, ("Hdr%d" % c if r == 0 else str(r * 10 + c))) for r in range(nrows) for c in range(ncols)]

def _time_scalar(q, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    t = time.time()
    celltype.run_scalar(os.path.join(QDIR, q), g, bindings)
    return time.time() - t

# row-count-sensitive queries that read tab:GridCell body rows
_BOUND = [
    ("header-body-split.rq", None),
    ("stub-data-split.rq", {"split": Literal(1, datatype=XSD.integer)}),
]

@pytest.mark.parametrize("q,bindings", _BOUND)
def test_derivation_scales_to_50_rows(q, bindings):
    dt = _time_scalar(q, _grid(50), 4, bindings)
    assert dt < 1.5, f"{q} took {dt:.2f}s at 50 rows (super-linear regression?)"
```

- [ ] **Step 2: Run the audit — record the profile, identify remaining cliffs**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_perf.py -q`
Expected: `header-body-split.rq` PASSES (Task 1 fixed it). `stub-data-split.rq` is EXPECTED TO FAIL here (still the pairwise form) — that is the audit *finding* that Task 3 fixes. Record which queries pass/fail.

Also profile the remaining queries by hand (they are not in `_BOUND` because they read header words / column markers / recipe nodes, not body rows — confirm each is O(header-words) or O(cols), not O(body-rows)):
`./.venv/bin/python -c "import time,os; from iladub.etkl import celltype; QDIR=os.path.join(os.path.dirname(celltype.__file__),'..','..','..','vocab','queries'); [print(f) for f in sorted(os.listdir(QDIR)) if f.endswith('.rq')]"`
For each, note in the report whether its evidence domain scales with body rows (a cliff risk) or not. `classify-kind`/`looks-transposed`/`transpose-coherent` read `tab:HeaderWord` / per-column signals (few); `recover-dimensions`/`name-levels`/`operand-exclusions`/`unpivot-*`/`strip-*` read the header/recipe graph. If any reads body cells with a pair self-join, add it to `_BOUND` and Task 3 fixes it.

- [ ] **Step 3: Leave the perf test with `stub-data-split` in `_BOUND` (it will pass after Task 3). Commit.**

```bash
git add tests/etkl/test_derivation_perf.py
git commit -m "test(etkl): derivation row-count profiling + perf regression guard (audit)"
```

(The suite has one expected-failing test until Task 3; note it in the task report so the controller does not mistake it for a regression. Alternatively mark `stub-data-split` with `pytest.mark.xfail(reason='fixed in Task 3')` and flip it in Task 3 — the implementer chooses, stating which in the report.)

---

### Task 3: Rewrite `stub-data-split.rq` (+ any other cliff found) to the aggregation form

**Files:**
- Modify: `vocab/queries/stub-data-split.rq` (and any other query Task 2 flagged)
- Modify: `tests/etkl/test_derivation_equiv.py` (add the stub new-vs-old randomized test)
- Modify: `tests/etkl/test_derivation_perf.py` (un-xfail stub if it was marked)

**Interfaces:**
- Consumes: `run_scalar` with `initBindings={'split': Literal(int)}`.
- Produces: the linear `stub-data-split.rq`, guarded identically.

**Approach.** `stub-data-split` finds MIN `k>=1` such that every column `>= k` is a data column (has a body cell at row>=`?split`, no Text body cell, ≤1 distinct body `cellDatatype`) and no data column exists below `k`. Reformulate: compute a per-column boolean `isData` by aggregation over body cells (`row>=?split`) — `has body cell` AND `NOT EXISTS Text body cell` AND `COUNT(DISTINCT cellDatatype) = 1` — then `k = 1 + MAX(col>=1 that is NOT isData)` (or 1 if none), requiring ≥1 data column. This drops both nested `NOT EXISTS` pair self-joins. **Because the exact edge semantics (empty columns, ragged, the "no data column below k" clause) are subtle, TDD against the frozen reference — `test_stub_data_split_matches_reference` is the correctness spec; write the query to keep it byte-identical, and add the randomized new-vs-old test. Reconcile any edge against `_ref_stub_data_split`, never the fixture.**

- [ ] **Step 1: Add the stub randomized differential test**

In `tests/etkl/test_derivation_equiv.py`, paste the CURRENT `stub-data-split.rq` verbatim as `OLD_STUB`, and add (stub needs a `split` binding — derive it per grid from the shipped `header-body-split` reference or sweep a few split values):

```python
OLD_STUB = r"""<PASTE the current vocab/queries/stub-data-split.rq verbatim here>"""

def test_stub_data_split_new_matches_old():
    new_text = open(os.path.join(QDIR, "stub-data-split.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=2):
        for split in range(0, 4):
            b = {"split": Literal(split, datatype=XSD.integer)}
            old = _run_text(OLD_STUB, cells, ncols, b)
            new = _run_text(new_text, cells, ncols, b)
            assert old == new, f"stub divergence ncols={ncols} split={split} cells={cells}: old={old} new={new}"
```

- [ ] **Step 2: Run — verify it PASSES against the current file (harness sanity)**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_equiv.py -k stub -q`
Expected: PASS (new file still == OLD_STUB). Confirms the harness before the rewrite.

- [ ] **Step 3: Rewrite `vocab/queries/stub-data-split.rq` to the aggregation form**

Write the linear form per the Approach. (No verbatim query is prescribed here because its edge semantics must be derived against `_ref_stub_data_split`; the two differential tests below are the spec.) Keep the `?split` input binding and the `?stub` output variable name identical.

- [ ] **Step 4: Run both differential guards + the perf test**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_equiv.py tests/etkl/test_celltype.py tests/etkl/test_derivation_perf.py tests/etkl/test_rowheaders.py -q`
Expected: all PASS — `test_stub_data_split_matches_reference` byte-identical, the randomized stub test matches on all grids×splits, the perf guard now passes at 50 rows, and the row-header integration tests are unaffected. Any divergence → fix the query against `_ref_stub_data_split`, not the test.

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/stub-data-split.rq tests/etkl/test_derivation_equiv.py tests/etkl/test_derivation_perf.py
git commit -m "perf(etkl): stub-data-split.rq -> linear aggregation form (equivalence-guarded)"
```

---

### Task 4: Close the loop — a realistic multi-row report compiles end-to-end

**Files:**
- Modify: `tests/etkl/test_derivation_perf.py` (add the end-to-end report compile)

**Interfaces:**
- Consumes: `iladub.etkl.compile_tables` (or the band-level `classify_hierarchical` if a full PDF is heavy), the fixtures helpers.

- [ ] **Step 1: Write the end-to-end realistic-report test**

Build a realistic grouped-header report with ≈50 body rows and compile it, asserting it completes fast and asserts (not escalates on a timeout). Prefer a real `compile_tables` over a synthetic PDF if a reportlab fixture is cheap; otherwise drive the hierarchical band path directly. Add to `tests/etkl/test_derivation_perf.py`:

```python
def test_realistic_multirow_report_compiles_fast():
    """A ~50-row grouped-header table that HANGS on the pre-rewrite queries now compiles quickly."""
    import time
    from iladub.etkl.geometry import Word, Line
    from iladub.etkl.bands import Band
    from iladub.etkl.hierarchical import classify_hierarchical
    def w(t, x0, x1, top): return Word(t, x0, x1, top, top + 10.0)
    header = [w("Region", 150, 350, 0.0)]                       # spanning coarse header
    leaf = [w("Site", 10, 60, 12), w("Q1", 110, 160, 12), w("Q2", 210, 260, 12), w("Q3", 310, 360, 12)]
    rows = []
    for i in range(50):
        top = 24.0 + i * 12.0
        rows.append([w("s%d" % i, 10, 60, top), w(str(i), 110, 160, top),
                     w(str(i + 1), 210, 260, top), w(str(i + 2), 310, 360, top)])
    lines = [Line(tuple(header), 0.0, 10.0), Line(tuple(leaf), 12, 22)] + \
            [Line(tuple(r), 24.0 + i * 12.0, 34.0 + i * 12.0) for i, r in enumerate(rows)]
    band = Band(tuple(lines), 0.0, lines[-1].bottom)
    t = time.time()
    hreg = classify_hierarchical(band)      # runs header_body_split + the maker stages
    dt = time.time() - t
    assert dt < 3.0, f"50-row hierarchical compile took {dt:.2f}s (regression)"
    assert hreg is not None, "the realistic report should classify, not escalate"
```

(If `classify_hierarchical` returns None for geometry reasons, adjust the fixture geometry — more data rows / clearer gutters — until the real pipeline classifies it; do NOT weaken the timing bound. The point is a real ~50-row hierarchical band that completes fast.)

- [ ] **Step 2: Run it**

Run: `./.venv/bin/python -m pytest tests/etkl/test_derivation_perf.py -q`
Expected: all PASS, including the 50-row compile in seconds (it would have hung pre-rewrite).

- [ ] **Step 3: Full suite (no regression)**

Run: `./.venv/bin/python -m pytest -q`
Expected: baseline `406 passed, 5 skipped` + the new perf/equiv tests, zero failures. If any `test_celltype`/`test_rowheaders`/`test_headers` test changed value, the rewrite broke semantics — STOP and reconcile against the reference.

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_derivation_perf.py
git commit -m "test(etkl): realistic 50-row report compiles end-to-end (was hanging)"
```

---

## Self-Review (completed)

- **Spec coverage:** root-cause rewrite (header-body-split) → Task 1; audit all `.rq` vs row count → Task 2; stub-data-split (the confirmed sibling cliff) + any other → Task 3; perf regression guard → Task 2; realistic-report end-to-end close → Task 4; equivalence oracle-pinned (differential + randomized new-vs-old) → Tasks 1 & 3; §8 form-only, no vocab/builder change → Global Constraints + File Structure.
- **Placeholder scan:** two intentional `<PASTE … verbatim>` markers (the OLD query text captured as the reference oracle) — the implementer copies the current file contents before overwriting; this is a real instruction, not a vague placeholder. Task 3's stub query is deliberately not hand-written verbatim (its edge semantics must be derived against the frozen `_ref_stub_data_split` — the differential tests are its spec); this is called out explicitly, not left implicit.
- **Type consistency:** `run_scalar(rq_path, graph, bindings)`, `grid_evidence(cells, ncols)`, `_run_text(query_text, cells, ncols, bindings)`, `_rand_grids(seed, n)` used identically across Tasks 1/2/3. `header-body-split.rq` keeps `?split`; `stub-data-split.rq` keeps `?stub` + the `split` init-binding.
- **Known risk (flag for review):** the header-body-split rewrite's no-differing-cell branch returns `s_col = 1`; verified correct on `HB_BATTERY` and the common case, but a pathological column whose only cell is at row 0 is an edge — the randomized differential test (200 grids incl. ragged/empty) is the backstop, and the reviewer should confirm it exercises single-cell/row-0-only columns.
