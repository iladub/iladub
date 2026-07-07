# Transposition Detect & Escalate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect typed transposition and escalate it in-band, instead of silently asserting an inverted `tab:RecordTable`.

**Architecture:** Add a `looks_transposed(region)` type-orientation oracle (a body *row* is all-numeric but no body *column* is) and gate the `RECORD_TABLE` branch of `compile_tables` on it — escalate as `TRANSPOSED` before asserting. A new `tab:TransposedTable` anchor class marks the recognized-but-not-yet-compiled kind. No new SHACL.

**Tech Stack:** Python 3.12, `pdfplumber`, `rdflib`, `pyshacl`, `reportlab` (test), `pytest`.

**Spec:** `docs/superpowers/specs/2026-07-07-transposition-detect-escalate-design.md`

## Global Constraints

- **No silent-wrong:** the whole point — a transposed table must escalate (`iladub:CandidateConcept`, `reason="TRANSPOSED"`), never be asserted as a `RecordTable`.
- **No false positives (the critical guard):** normal tables — anything with a type-homogeneous numeric *column* — must still compile unchanged. A regression here is worse than the bug.
- **No overfitting:** the oracle is `is_numeric`-based structure (a typed row, no typed column), never a constant tuned to one fixture. Text is symmetric and ignored (all-text → not flagged).
- **`tab.ttl` core stays standalone** (no `holon`/`prov`/`csvw`/`qb` subjects). `tab:cellText` etc. unchanged.
- **`reportlab`/`pdfplumber` tests guard with `pytest.importorskip`.**
- **Reuse:** `headers.is_numeric`, `regions.classify`/`Cell`, `holon.escalate_region`/`TAB`, `compile.compile_tables`. Do not duplicate.
- **Namespaces:** `tab:`=`https://w3id.org/iladub/tab#`, `iladub:`=`https://w3id.org/iladub#`, `dec:`=`https://w3id.org/iladub/dec#`.
- **Loop 1/2 stay green:** the record and hierarchical paths are unchanged except for the added pre-assert gate.

## File Structure

| File | Responsibility |
|------|----------------|
| `src/iladub/etkl/orientation.py` (create) | `looks_transposed(region) -> bool` — the type-orientation oracle |
| `tests/etkl/fixtures.py` (modify) | add `transposed_table_pdf` |
| `vocab/ontology/tab.ttl` (modify) | add `tab:TransposedTable ⊑ tab:Table` |
| `src/iladub/etkl/compile.py` (modify) | orientation gate in the `RECORD_TABLE` branch |
| `src/iladub/etkl/__init__.py` (modify) | export `looks_transposed` |
| `tests/etkl/test_orientation.py` (create) | oracle tests |
| `tests/etkl/test_closing_slice.py` (modify) | integration: transposed escalates; normal still compiles |
| `tests/test_tab.py` (modify) | `tab:TransposedTable` term test |

Run one test: `pytest -q "path::name" -v`. Full: `pytest -q tests/etkl tests/test_tab.py`.

---

### Task 1: The `looks_transposed` oracle

**Files:**
- Create: `src/iladub/etkl/orientation.py`
- Modify: `tests/etkl/fixtures.py`
- Test: `tests/etkl/test_orientation.py`

**Interfaces:**
- Consumes: `is_numeric` (from `headers`); `classify`/`RegionKind`/`Cell` (from `regions`); `extract_words`/`text_lines`/`detect_bands`.
- Produces: `looks_transposed(region) -> bool` — over the region's **body** (`cell.row > 0`): returns True iff some body row has all-numeric cells in columns `>= 1` (excluding the first/label column) **and** no leaf column has all-numeric body cells.

- [ ] **Step 1: Add the fixture** — append to `tests/etkl/fixtures.py`:

```python
def transposed_table_pdf(path: str) -> dict:
    """A TRANSPOSED table: field names run down the first column, each other column
    is a record. The 'Age' row is all-numeric ACROSS the record columns, while no
    column is all-numeric — the transposition signature."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 11)
    rows = [("Name", "Alice", "Bob"), ("Age", "30", "25"), ("City", "NYC", "LA")]
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 20.0
        for x, cell in zip((80.0, 240.0, 400.0), row):
            c.drawString(x, y, cell)
    c.save()
    return {"n_cols": 3, "n_rows": 3}
```

- [ ] **Step 2: Write the failing tests** — `tests/etkl/test_orientation.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import transposed_table_pdf, simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.orientation import looks_transposed


def _region(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return classify(band)


def test_transposed_is_flagged(tmp_path):
    # fields down col 0, numeric values run across the 'Age' row -> transposed
    assert looks_transposed(_region(transposed_table_pdf, tmp_path)) is True


def test_normal_numeric_table_not_flagged(tmp_path):
    # simple_table has an all-numeric 'Value' column -> a typed COLUMN -> not transposed
    assert looks_transposed(_region(simple_table_pdf, tmp_path)) is False
```

- [ ] **Step 3: Run to verify they fail**

Run: `pytest -q tests/etkl/test_orientation.py -v`
Expected: FAIL (`No module named 'iladub.etkl.orientation'`).

- [ ] **Step 4: Implement** — `src/iladub/etkl/orientation.py`:

```python
"""orientation — detect a TRANSPOSED table (records along columns, fields down the
first column) via type-orientation.

This is iladub's first SEMANTIC oracle: the 2-D round-trip (geometry) and the tab:
SHACL (structure) both pass on a transposed table, because it is a valid grid — only
the *orientation* of the record axis is wrong. Type-orientation catches it: in a
normal table each column is type-homogeneous (a numeric attribute runs DOWN a
column); in a transposed table a numeric attribute runs ACROSS a row.
"""
from __future__ import annotations

from .headers import is_numeric


def looks_transposed(region) -> bool:
    """True iff the region's body has a type-homogeneous numeric ROW but no
    type-homogeneous numeric COLUMN — the transposition signature.

    Conservative and keyed on numeric typing only: text is symmetric (both axes
    carry labels) and ignored, so an all-text table is never flagged, and a normal
    numeric table (which has a typed column by definition) is never flagged.
    """
    data = [c for c in region.cells if c.row > 0]        # body only; header is row 0
    rows: dict[int, dict[int, str]] = {}
    cols: dict[int, list[str]] = {}
    for c in data:
        rows.setdefault(c.row, {})[c.col] = c.text
        cols.setdefault(c.col, []).append(c.text)

    # a body row whose cells in columns >= 1 (excluding the first/label column) are all numeric
    typed_row = any(
        any(cc >= 1 for cc in rowmap) and all(is_numeric(rowmap[cc]) for cc in rowmap if cc >= 1)
        for rowmap in rows.values()
    )
    # a leaf column whose body cells are all numeric
    typed_col = any(vals and all(is_numeric(v) for v in vals) for vals in cols.values())

    return typed_row and not typed_col
```

- [ ] **Step 5: Run to verify they pass**

Run: `pytest -q tests/etkl/test_orientation.py -v`
Expected: 2 passed (transposed → True; `simple_table` → False). *(Empirically verified while authoring: transposed→True, `record_report`→False, all-text record→False.)*

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/orientation.py tests/etkl/fixtures.py tests/etkl/test_orientation.py
git commit -m "feat(etkl): looks_transposed — type-orientation oracle for transposed tables"
```

---

### Task 2: The `tab:TransposedTable` anchor class

**Files:**
- Modify: `vocab/ontology/tab.ttl`
- Test: `tests/test_tab.py` (append)

**Interfaces:**
- Produces: `tab:TransposedTable` (`owl:Class`, `rdfs:subClassOf tab:Table`) — the escalation `suggestedAnchor` and future compile target.

- [ ] **Step 1: Write the failing test** — append to `tests/test_tab.py`:

```python
def test_tab_transposedtable_term():
    g = _g(TAB_TTL)
    assert (TAB.TransposedTable, RDF.type, OWL.Class) in g
    assert (TAB.TransposedTable, RDFS.subClassOf, TAB.Table) in g
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/test_tab.py::test_tab_transposedtable_term -v`
Expected: FAIL.

- [ ] **Step 3: Add the term** — in `vocab/ontology/tab.ttl`, next to `tab:RecordTable`/`tab:HierarchicalTable`:

```turtle
tab:TransposedTable a owl:Class ; rdfs:subClassOf tab:Table ;
    rdfs:label "Transposed table"@en ;
    rdfs:comment "A table whose records run along columns and whose fields run down the first column (rows are attributes). Recognized but not yet compiled — used as an escalation anchor."@en .
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q "tests/test_tab.py::test_tab_transposedtable_term" "tests/test_tab.py::test_tab_core_is_standalone" -v`
Expected: 2 passed (new term present; standalone constraint still holds — no external subjects added).

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/tab.ttl tests/test_tab.py
git commit -m "feat(tab): TransposedTable class (escalation anchor for transposed tables)"
```

---

### Task 3: The orientation gate in `compile_tables`

**Files:**
- Modify: `src/iladub/etkl/compile.py`, `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_closing_slice.py` (append)

**Interfaces:**
- Consumes: `looks_transposed` (Task 1); `escalate_region`/`TAB` (holon); the existing `RECORD_TABLE` branch.
- Produces: `compile_tables` escalates a transposed region (`reason="TRANSPOSED"`, anchor `tab:TransposedTable`) instead of asserting it; `looks_transposed` exported from `iladub.etkl`.

- [ ] **Step 1: Write the failing tests** — append to `tests/etkl/test_closing_slice.py`:

```python
def test_transposed_escalates_not_asserted(tmp_path):
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl.holon import TAB, ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    report = compile_tables(str(p))
    # the silent-wrong is closed: NO RecordTable asserted; escalated as TRANSPOSED
    assert (None, None, TAB.RecordTable) not in report.graph
    cand = next(report.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert str(next(report.graph.objects(cand, DEC.rationale))) == "TRANSPOSED"
    assert report.score == 0.0


def test_normal_table_still_compiles(tmp_path):
    # the critical no-false-positive guard: a normal numeric record table is unaffected
    from tests.etkl.fixtures import simple_table_pdf
    from iladub.etkl.holon import TAB
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) in report.graph
    assert report.score == 1.0
```

- [ ] **Step 2: Run to verify they fail**

Run: `pytest -q tests/etkl/test_closing_slice.py -k "transposed or still_compiles" -v`
Expected: `test_transposed_escalates_not_asserted` FAILS (today it asserts a RecordTable); `test_normal_table_still_compiles` passes already.

- [ ] **Step 3: Add the gate** — in `src/iladub/etkl/compile.py`, in the `RECORD_TABLE` branch (currently `if region.kind is RegionKind.RECORD_TABLE:` → `assert_record_region(...)` + token scoring), wrap the existing assert logic in an `else`, guarded by the orientation check:

```python
        if region.kind is RegionKind.RECORD_TABLE:
            from .orientation import looks_transposed
            if looks_transposed(region):
                # transposed: records run along columns — asserting a RecordTable here
                # would invert the semantics (a silent-wrong). Escalate in-band instead.
                cand_uri = URIRef(f"{_DOC}#region{idx}")
                escalate_region(graph, cand_uri, _DOC, ascii_view, "TRANSPOSED",
                                TAB.TransposedTable, 0.4)
                escalated_total += sum(len(ln.words) for ln in band.lines)
                reports.append(RegionReport(region.kind, "escalated", 0, "TRANSPOSED",
                                            str(TAB.TransposedTable), ascii_view))
            else:
                # ---- existing RECORD_TABLE assert logic, unchanged, moves here ----
                table_uri = URIRef(f"{_DOC}#table{idx}")
                n = assert_record_region(graph, region, table_uri, _DOC, page_number)
                b = region.grid.boundaries
                data_cells = [c for c in region.cells if c.row > 0]
                asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))
                escalated_total += sum(len(c.words) for c in data_cells if not cell_round_trips(c, b))
                reports.append(RegionReport(region.kind, "asserted", n, None,
                                            str(TAB.RecordTable), ascii_view))
```

**Note:** the `else` block above must match whatever the current RECORD_TABLE assert/scoring code is — read the existing branch and move it verbatim into the `else`, adding only the `if looks_transposed(region):` escalation arm before it. Do not change the existing scoring.

- [ ] **Step 4: Export** — add `looks_transposed` to `src/iladub/etkl/__init__.py` (import from `.orientation`, add to `__all__`).

- [ ] **Step 5: Run to verify they pass + no regression**

Run: `pytest -q tests/etkl/test_closing_slice.py -v` then `pytest -q tests/etkl tests/test_tab.py`
Expected: the two new tests pass; **all** existing etkl + tab tests stay green (record/hierarchy paths unchanged; `record_report`, `simple_table`, the pivot, the record closing-slice all unaffected — none are transposed).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_closing_slice.py
git commit -m "fix(etkl): escalate transposed tables (TRANSPOSED) instead of silently asserting inverted RecordTable"
```

---

### Task 4: Showcase + canvas (the loop's showcase deliverable)

**Files:**
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (if present on branch; else note for the canvas owner)
- Note: the `demo/etkl_*_showcase.ipynb` update is a loop deliverable (per the doctrine), but the notebook lives on `main` — this task records the intent for the controller to apply as a small follow-up on `main`.

- [ ] **Step 1: Record the increment** — the loop canvas is not on this branch (it lives on a separate docs branch/`main`). In your report, note that the controller must, on the canvas's branch: mark **transposition detect+escalate** done in the increments list and add **compile transposed tables** as the explicit next loop. Also note the showcase-notebook follow-up: add a Part showing a transposed table escalating as `TRANSPOSED` (the honest "recognized but not yet compiled" case), per the *showcase-is-part-of-the-loop* doctrine.

- [ ] **Step 2: (No code)** — this task carries no code; it exists so the doctrine deliverables (canvas + showcase) are not silently dropped. Confirm in the report.

---

## Self-Review

**Spec coverage:** §1 scope → Task 3 (`test_transposed_escalates_not_asserted`). §2 oracle → Task 1 (`orientation.py` + tests, empirically verified). §3 gate → Task 3. §4 ontology → Task 2. §5 (first semantic oracle) → captured in `orientation.py` docstring. §6 escalation shape → Task 3 gate (`escalate_region` with surfaceText/anchor/rationale). §7 tests → Tasks 1–3 (oracle unit, transposed-escalates, normal-still-compiles, term test, no-regression). §8 out-of-scope + canvas/showcase → Task 4. **No gaps.**

**Placeholder scan:** none — every step carries runnable code + commands. The one "read the existing branch and move it verbatim" note in Task 3 Step 3 is a precise instruction (the surrounding escalation arm is fully specified), not a placeholder.

**Type consistency:** `looks_transposed(region) -> bool` identical in Tasks 1 and 3; `region.cells` (Cell with `.row`/`.col`/`.text`/`.words`) consumed consistently; `TAB.TransposedTable` used in Tasks 2 and 3; `escalate_region(graph, uri, doc, ascii, reason, anchor, confidence)` matches the Loop 1 signature.
