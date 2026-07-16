# Typed-Cell Evidence Graph — Type/Orientation Boundaries (Loop B2a) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift four type/orientation decisions (`headers.header_body_split`, `rowheaders.stub_data_split`, `orientation.looks_transposed`, `orientation.transpose_is_coherent`) from Python-over-geometry to declarative **SPARQL derivations** over a new **typed-cell evidence graph**, keeping behaviour byte-identical (a faithful lift), and emitting cell types as an **open `tab:cellDatatype` lattice** so B2b can extend it without re-architecting.

**Architecture:** A transient, pre-holon RDF graph is built per band/region — `?cell a tab:GridCell ; tab:atGridRow ?r ; tab:atGridColumn ?c ; tab:gridText ?t ; tab:cellDatatype tab:Numeric|tab:Text` — plus a column marker per column index (so empty columns are visible). Each decision runs a fixed `.rq` over that graph via a thin `celltype` runner and returns via its unchanged Python signature. Open-world **derivation** (recover a boundary/count/orientation from evidence — the loop-B side of the gate), never SHACL. The `header_body_split` and `stub_data_split` queries are **feasibility-proven** (2026-07-16) against a Python reference over a battery.

**Tech Stack:** Python 3, rdflib (SPARQL 1.1 `SELECT`/`ASK`, `initBindings`), pytest. Runner is `.venv/bin/python`. No new dependency.

## Global Constraints

From CLAUDE.md §8 (gate, open/closed split) + the spec (`docs/superpowers/specs/2026-07-16-typed-cell-evidence-graph-design.md`). Every task's requirements implicitly include this. **Reviewers enforce it.**

- **AXIOM — derivation (open world) → SPARQL.** Each decision *recovers* a boundary/count/orientation from typed-cell evidence. Standard SPARQL `SELECT`/`ASK` over the evidence graph. **No SHACL** (derivation, not conformance). **No tuned constant** in any `.rq` or `celltype.py`.
- **PROCEDURAL (justified; Python = reference-impl language):** (1) `is_numeric` — raw datatype detection; (2) the evidence-graph **emitter** — raw extraction of `(row, col, text, cellDatatype)` + column markers; (3) the query **runner** — rdflib engine glue + parsing the scalar/boolean back. No decision logic in Python.
- **Faithful lift (byte-identical):** the four functions keep their signatures/returns exactly; a **differential oracle** (frozen Python reference vs the SPARQL, over a battery) is the correctness gate. B2a does **not** change the numeric-homogeneity behaviour or the proxy.
- **Open lattice, NOT a boolean:** emit `tab:cellDatatype tab:Numeric | tab:Text` (a non-`Numeric` cell = `is_numeric` False). Never emit a boolean `tab:isNumeric`.
- **Behavioural suites green unchanged:** `test_headers.py`, `test_rowheaders.py`, `test_orientation.py`, `test_regions.py`, `test_matrix.py`, `test_hierarchical.py`, `test_segment.py`, and the end-to-end compile suites.
- **Source ownership:** `.rq` reference only `tab:` (owned) + standard SPARQL; new evidence terms are owned `tab:` in the standalone `tab.ttl`. No HGA/FnO term as a subject.
- **Scope:** these four decisions only. **Out of scope:** `regions.classify` (B2c); the richer body-signal types Date/Currency/%/Boolean + structured-homogeneity generalization (B2b); `is_numeric` stays PROCEDURAL.

---

## File Structure

**Create:**
- `src/iladub/etkl/celltype.py` — the evidence-graph emitter + query runners. [PROCEDURAL]
- `vocab/queries/header-body-split.rq`, `stub-data-split.rq`, `looks-transposed.rq`, `transpose-coherent.rq` — the four decisions. [AXIOM]
- `tests/etkl/test_celltype.py` — differential oracle (frozen refs + battery) + per-`.rq` unit tests.

**Modify:**
- `vocab/ontology/tab.ttl` — owned evidence terms `tab:GridCell`, `tab:atGridRow`, `tab:atGridColumn`, `tab:gridText`, `tab:cellDatatype`, `tab:columnIndex`, the class `tab:CellDatatype`, and individuals `tab:Numeric`/`tab:Text`.
- `src/iladub/etkl/headers.py` — `header_body_split` body → build evidence + run `header-body-split.rq`. `is_numeric`/`_col_values` unchanged.
- `src/iladub/etkl/rowheaders.py` — `stub_data_split` body → run `stub-data-split.rq`.
- `src/iladub/etkl/orientation.py` — `looks_transposed`/`transpose_is_coherent` bodies → run the two ASK `.rq`.
- `tests/etkl/test_transform_gate.py` — extend the no-tuned-constant scan to the four new `.rq` (glob already covers `vocab/queries/*.rq`) + `celltype.py`.

---

## Task 1: `celltype` foundation + `header_body_split` → SPARQL

Build the evidence-graph emitter + runners + the evidence vocab, promote the proven `header-body-split.rq`, rewire `header_body_split`, and stand up the differential oracle.

**Files:**
- Create: `src/iladub/etkl/celltype.py`, `vocab/queries/header-body-split.rq`, `tests/etkl/test_celltype.py`
- Modify: `vocab/ontology/tab.ttl`, `src/iladub/etkl/headers.py`

**Interfaces:**
- Produces: `celltype.grid_evidence(cells, ncols) -> rdflib.Graph` — `cells` is an iterable of `(row:int, col:int, text:str)`; emits a `tab:GridCell` per cell (`atGridRow`/`atGridColumn`/`gridText`/`cellDatatype`) + a column marker `?n tab:columnIndex ?i` for `i in range(ncols)`. Consumed by Tasks 1–3.
- Produces: `celltype.run_scalar(rq_path, graph, bindings=None) -> int|None` and `celltype.run_ask(rq_path, graph) -> bool`. Consumed by Tasks 1–3.
- Produces: `headers.header_body_split(band, grid) -> int|None` (unchanged signature; body now SPARQL).

- [ ] **Step 1: Write the failing differential test (header/body split)**

Create `tests/etkl/test_celltype.py`:

```python
import re, math
from rdflib import Graph, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


# ---- frozen Python reference (the anti-overfit oracle; survives the rewrite) ----
def _is_numeric(s):
    t = re.sub(r"[,%]", "", s.strip())
    if not t:
        return False
    try:
        return math.isfinite(float(t))
    except ValueError:
        return False


def _ref_header_body_split(grid, ncols):
    """grid = list of rows; each row = list of (col, text). Port of headers.header_body_split."""
    for start in range(1, len(grid)):
        cols = {i: [] for i in range(ncols)}
        for r in range(start, len(grid)):
            for (c, t) in grid[r]:
                cols[c].append(t)
        if any(vs and all(_is_numeric(v) for v in vs) for vs in cols.values()):
            return start
    return None


def _cells(grid):
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


# ---- battery: (name, grid, ncols) ----
HB_BATTERY = [
    ("split@1", [[(0, "Name"), (1, "Score")], [(0, "Alice"), (1, "10")], [(0, "Bob"), (1, "20")]], 2),
    ("split@2", [[(0, "Region"), (1, "Sales")], [(1, "USD")], [(0, "North"), (1, "100")], [(0, "South"), (1, "200")]], 2),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
    ("3col@1", [[(0, "Id"), (1, "Qty"), (2, "Price")], [(0, "a"), (1, "1"), (2, "9.5")], [(0, "b"), (1, "2"), (2, "8.0")]], 3),
]


def test_header_body_split_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in HB_BATTERY:
        g = celltype.grid_evidence(_cells(grid), ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "header-body-split.rq"), g)
        assert got == _ref_header_body_split(grid, ncols), "%s: got %s" % (name, got)
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_header_body_split_matches_reference -v`
Expected: FAIL — `iladub.etkl.celltype` does not exist.

- [ ] **Step 3: Add the evidence vocab to `tab.ttl`**

In `vocab/ontology/tab.ttl`, after the transient-evidence block (near `tab:namesLevel`), add:

```turtle
# --- typed-cell evidence graph (transient, pre-holon; loop B2a) ---
tab:GridCell a owl:Class ; rdfs:label "Grid cell"@en ;
    rdfs:comment "A transient (line, column) cell of a candidate region, with its surface text and recovered datatype. Evidence for the type/orientation derivations; never asserted into a holon."@en .
tab:atGridRow a owl:DatatypeProperty ; rdfs:domain tab:GridCell ; rdfs:range xsd:integer ; rdfs:label "at grid row"@en .
tab:atGridColumn a owl:DatatypeProperty ; rdfs:domain tab:GridCell ; rdfs:range xsd:integer ; rdfs:label "at grid column"@en .
tab:gridText a owl:DatatypeProperty ; rdfs:domain tab:GridCell ; rdfs:range rdfs:Literal ; rdfs:label "grid text"@en .
tab:CellDatatype a owl:Class ; rdfs:label "Cell datatype"@en ;
    rdfs:comment "An OPEN lattice of recovered cell datatypes. B2a: tab:Numeric | tab:Text. B2b extends it (Date/Currency/Percentage/Boolean)."@en .
tab:Numeric a tab:CellDatatype ; rdfs:label "Numeric"@en .
tab:Text    a tab:CellDatatype ; rdfs:label "Text"@en .
tab:cellDatatype a owl:ObjectProperty ; rdfs:domain tab:GridCell ; rdfs:range tab:CellDatatype ; rdfs:label "cell datatype"@en .
tab:columnIndex a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "column index"@en ;
    rdfs:comment "A grid column marker (0..ncols-1) so empty columns are visible to the stub/data derivation."@en .
```

- [ ] **Step 4: Implement `celltype.py`**

Create `src/iladub/etkl/celltype.py`:

```python
"""celltype — the typed-cell evidence graph + query runner (neurosymbolic loop B2a).

The type/orientation boundary decisions (header/body split, stub/data split, transpose) are
declarative DERIVATIONS over per-cell datatype facts (open-world → SPARQL, the loop-B side of the
gate). This module is the PROCEDURAL layer only: raw datatype typing (via is_numeric), emitting the
transient typed-cell evidence graph, and invoking rdflib. No decision logic, no tuned constant —
the decisions live entirely in vocab/queries/*.rq (AXIOM). Irreducible: a SPARQL engine must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD

from .headers import is_numeric

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")


def grid_evidence(cells, ncols):
    """Build the transient typed-cell evidence graph. `cells`: iterable of (row, col, text).
    Emits a tab:GridCell per cell (row/col/text/cellDatatype) + a column marker per index."""
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["cell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, TAB.Numeric if is_numeric(t) else TAB.Text))
    for c in range(ncols):
        g.add((_EV["col-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    return g


def run_scalar(rq_path, graph, bindings=None):
    """Run a SELECT that returns a single integer variable; return int or None (empty result)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    for row in graph.query(q, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None


def run_ask(rq_path, graph):
    """Run an ASK; return bool."""
    q = Path(rq_path).read_text(encoding="utf-8")
    return bool(graph.query(q).askAnswer)
```

- [ ] **Step 5: Implement `header-body-split.rq` (the proven query)**

Create `vocab/queries/header-body-split.rq`:

```sparql
# header-body-split.rq — first body-start row: MIN row s>=1 such that some column is all-Numeric
# from s to the band end. Empty result -> None (caller escalates). Proven vs the Python (2026-07-16).
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?s) AS ?split) WHERE {
  ?anycell tab:atGridRow ?s . FILTER(?s >= 1)
  FILTER EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?r1 . FILTER(?r1 >= ?s)
    FILTER NOT EXISTS { ?cx tab:atGridColumn ?col ; tab:atGridRow ?r2 ; tab:cellDatatype ?d .
                        FILTER(?r2 >= ?s && ?d != tab:Numeric) }
  }
}
```

- [ ] **Step 6: Rewire `header_body_split` to build evidence + run the query**

In `src/iladub/etkl/headers.py`, replace the body of `header_body_split` (keep the signature + docstring). Add a helper that produces the full grid cells `(line-index, col, joined-text)` using the same word-grouping as `_col_values`, then run the query:

```python
def _grid_cells(band, grid):
    """(line, col, joined-text) for every populated cell — the full-grid analogue of _col_values
    (same column word-grouping), used to build the typed-cell evidence graph."""
    b = grid.boundaries
    out = []
    for r, ln in enumerate(band.lines):
        seen = {}
        for w in ln.words:
            seen.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w.text)
        for c, texts in seen.items():
            out.append((r, c, " ".join(texts)))
    return out


def header_body_split(band: Band, grid: LeafGrid) -> int | None:
    """First line index at/after which >=1 leaf column is all-numeric (see design note).

    Declarative derivation (loop B2a): the typed-cell evidence graph + header-body-split.rq.
    """
    from . import celltype
    import os
    g = celltype.grid_evidence(_grid_cells(band, grid), grid.ncols)
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "header-body-split.rq")
    return celltype.run_scalar(q, g)
```

(Keep the existing "Design note — numeric-homogeneity as the operative proxy" text in the docstring — the behaviour is unchanged. `column_of` is already imported in `headers.py`.)

- [ ] **Step 7: Run the tests + behavioural suites**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py tests/etkl/test_headers.py tests/etkl/test_hierarchical.py tests/etkl/test_matrix.py tests/etkl/test_segment.py -v`
Expected: PASS — the differential test green, and every caller of `header_body_split` behaves identically. Then the full etkl suite: `.venv/bin/python -m pytest tests/etkl -q` — PASS. If any behavioural test changes, STOP (supersession defect).

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/celltype.py vocab/queries/header-body-split.rq vocab/ontology/tab.ttl src/iladub/etkl/headers.py tests/etkl/test_celltype.py
git commit -m "feat(etkl): typed-cell evidence graph + header_body_split as SPARQL derivation [B2a task 1]

New pre-holon evidence graph (GridCell: row/col/text/cellDatatype open lattice + column markers);
header_body_split now derives over it via header-body-split.rq (proven vs the Python). is_numeric +
emitter + runner = PROCEDURAL; the decision = AXIOM. Behaviour byte-identical (differential oracle).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `stub_data_split` → SPARQL

Promote the proven `stub-data-split.rq` (contiguous-suffix `k`, column markers, `split` via `initBindings`) and rewire `stub_data_split`.

**Files:**
- Create: `vocab/queries/stub-data-split.rq`
- Modify: `src/iladub/etkl/rowheaders.py`, `tests/etkl/test_celltype.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`/`run_scalar` (Task 1), `headers.header_body_split` (Task 1), `_grid_cells` (Task 1).
- Produces: `rowheaders.stub_data_split(band, grid) -> int|None` (unchanged signature).

- [ ] **Step 1: Write the failing differential test**

Add to `tests/etkl/test_celltype.py`:

```python
def _ref_stub_data_split(grid, ncols):
    """Port of rowheaders.stub_data_split."""
    split = _ref_header_body_split(grid, ncols)
    if split is None:
        return None
    cols = {i: [] for i in range(ncols)}
    for r in range(split, len(grid)):
        for (c, t) in grid[r]:
            cols[c].append(t)
    numeric = [bool(cols[i]) and all(_is_numeric(v) for v in cols[i]) for i in range(ncols)]
    k = next((i for i in range(ncols) if numeric[i]), None)
    if k is None or k == 0:
        return None
    if not all(numeric[i] for i in range(k, ncols)):
        return None
    return k


SD_BATTERY = [
    ("k=2 two stubs", [[(0, "Reg"), (1, "Yr"), (2, "Val")], [(0, "N"), (1, "x"), (2, "5")], [(0, "S"), (1, "y"), (2, "6")]], 3),
    ("k=0 no stub->None", [[(0, "V1"), (1, "V2")], [(0, "1"), (1, "2")], [(0, "3"), (1, "4")]], 2),
    ("text after data->None", [[(0, "A"), (1, "V"), (2, "Note")], [(0, "a"), (1, "1"), (2, "hi")], [(0, "b"), (1, "2"), (2, "yo")]], 3),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
]


def test_stub_data_split_matches_reference():
    from iladub.etkl import celltype
    from rdflib import Literal as _L
    from rdflib.namespace import XSD as _X
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in SD_BATTERY:
        ref = _ref_stub_data_split(grid, ncols)
        split = _ref_header_body_split(grid, ncols)
        if split is None:
            got = None
        else:
            g = celltype.grid_evidence(_cells(grid), ncols)
            got = celltype.run_scalar(os.path.join(QDIR, "stub-data-split.rq"), g,
                                      bindings={"split": _L(split, datatype=_X.integer)})
        assert got == ref, "%s: got %s ref %s" % (name, got, ref)
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_stub_data_split_matches_reference -v`
Expected: FAIL — `stub-data-split.rq` does not exist.

- [ ] **Step 3: Implement `stub-data-split.rq` (proven)**

Create `vocab/queries/stub-data-split.rq` (`?split` is bound by the caller via `initBindings`):

```sparql
# stub-data-split.rq — leading text-stub column count k: the data columns form a contiguous suffix
# [k, ncols), k>=1. A column is DATA iff it has a body cell (row>=?split) and no non-Numeric body
# cell. Column markers make empty columns visible. Empty result -> None. Proven vs the Python.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?k) AS ?stub) WHERE {
  ?km tab:columnIndex ?k . FILTER(?k >= 1)
  # k is a data column
  FILTER EXISTS { ?bc tab:atGridColumn ?k ; tab:atGridRow ?br . FILTER(?br >= ?split) }
  FILTER NOT EXISTS { ?xc tab:atGridColumn ?k ; tab:atGridRow ?xr ; tab:cellDatatype ?xd . FILTER(?xr >= ?split && ?xd != tab:Numeric) }
  # every column >= k is data (no non-data column at/after k)
  FILTER NOT EXISTS {
    ?cm3 tab:columnIndex ?c3 . FILTER(?c3 >= ?k)
    FILTER NOT EXISTS {
      ?bc3 tab:atGridColumn ?c3 ; tab:atGridRow ?br3 . FILTER(?br3 >= ?split)
      FILTER NOT EXISTS { ?xc3 tab:atGridColumn ?c3 ; tab:atGridRow ?xr3 ; tab:cellDatatype ?xd3 . FILTER(?xr3 >= ?split && ?xd3 != tab:Numeric) }
    }
  }
  # k is the MIN data column: no data column below k
  FILTER NOT EXISTS {
    ?cm4 tab:columnIndex ?c4 . FILTER(?c4 < ?k)
    FILTER EXISTS { ?bc4 tab:atGridColumn ?c4 ; tab:atGridRow ?br4 . FILTER(?br4 >= ?split) }
    FILTER NOT EXISTS { ?xc4 tab:atGridColumn ?c4 ; tab:atGridRow ?xr4 ; tab:cellDatatype ?xd4 . FILTER(?xr4 >= ?split && ?xd4 != tab:Numeric) }
  }
}
```

- [ ] **Step 4: Rewire `stub_data_split`**

In `src/iladub/etkl/rowheaders.py`, replace the body of `stub_data_split` (keep the signature/docstring):

```python
def stub_data_split(band: Band, grid: LeafGrid) -> int | None:
    """Number of leading stub (text) columns k; data columns are [k..ncols-1]. (See docstring.)

    Declarative derivation (loop B2a): typed-cell evidence + stub-data-split.rq, gated on the
    header/body split."""
    from .headers import header_body_split, _grid_cells
    from . import celltype
    from rdflib import Literal
    from rdflib.namespace import XSD
    import os
    split = header_body_split(band, grid)
    if split is None:
        return None
    g = celltype.grid_evidence(_grid_cells(band, grid), grid.ncols)
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "stub-data-split.rq")
    return celltype.run_scalar(q, g, bindings={"split": Literal(split, datatype=XSD.integer)})
```

(The old `header_body_split` + `_col_values` import at the top of `rowheaders.py` may now be partly unused — grep and keep only what other functions in the file still use; do not remove names still referenced.)

- [ ] **Step 5: Run the tests + behavioural suites**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py tests/etkl/test_rowheaders.py tests/etkl/test_matrix.py -v`
Expected: PASS. Then full etkl: `.venv/bin/python -m pytest tests/etkl -q` — PASS.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/stub-data-split.rq src/iladub/etkl/rowheaders.py tests/etkl/test_celltype.py
git commit -m "feat(etkl): stub_data_split as SPARQL derivation over the typed-cell evidence graph [B2a task 2]

Contiguous-suffix data columns via stub-data-split.rq (column markers + split binding), proven vs
the Python. Behaviour byte-identical.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: `looks_transposed` + `transpose_is_coherent` → SPARQL (ASK)

Lift the two orientation oracles to ASK queries over the evidence graph (built from `region.cells`).

**Files:**
- Create: `vocab/queries/looks-transposed.rq`, `vocab/queries/transpose-coherent.rq`
- Modify: `src/iladub/etkl/orientation.py`, `tests/etkl/test_celltype.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`/`run_ask` (Task 1).
- Produces: `orientation.looks_transposed(region) -> bool`, `orientation.transpose_is_coherent(region) -> bool` (unchanged signatures).

- [ ] **Step 1: Write the failing differential test**

Add to `tests/etkl/test_celltype.py` frozen reference ports of both functions (over a `region.cells`-style list of `(row, col, text)`, header = row 0), a battery (transposed / upright-numeric / all-text / mixed-row-incoherent), and:

```python
def _ref_looks_transposed(cells):
    rows, cols = {}, {}
    for (r, c, t) in cells:
        if r > 0:
            rows.setdefault(r, {})[c] = t
            cols.setdefault(c, []).append(t)
    typed_row = any(any(cc >= 1 for cc in rm) and all(_is_numeric(rm[cc]) for cc in rm if cc >= 1) for rm in rows.values())
    typed_col = any(vals and all(_is_numeric(v) for v in vals) for vals in cols.values())
    return typed_row and not typed_col


def _ref_transpose_coherent(cells):
    rows = {}
    for (r, c, t) in cells:
        if c >= 1:
            rows.setdefault(r, []).append(t)
    for vals in rows.values():
        if vals and not (all(_is_numeric(v) for v in vals) or all(not _is_numeric(v) for v in vals)):
            return False
    return True


ORI_BATTERY = [
    ("transposed", [(0, 0, "Metric"), (0, 1, "A"), (0, 2, "B"), (1, 0, "Rev"), (1, 1, "10"), (1, 2, "20"), (2, 0, "Cost"), (2, 1, "3"), (2, 2, "4")]),
    ("upright-numeric", [(0, 0, "Name"), (0, 1, "Score"), (1, 0, "Alice"), (1, 1, "10"), (2, 0, "Bob"), (2, 1, "20")]),
    ("all-text", [(0, 0, "A"), (0, 1, "B"), (1, 0, "x"), (1, 1, "y")]),
    ("incoherent-row", [(0, 0, "K"), (0, 1, "V"), (0, 2, "U"), (1, 0, "wt"), (1, 1, "5"), (1, 2, "kg")]),
]


def test_orientation_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells in ORI_BATTERY:
        ncols = max(c for (_r, c, _t) in cells) + 1
        g = celltype.grid_evidence(cells, ncols)
        lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
        tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
        assert lt == _ref_looks_transposed(cells), "%s looks_transposed: got %s" % (name, lt)
        assert tc == _ref_transpose_coherent(cells), "%s coherent: got %s" % (name, tc)
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_orientation_matches_reference -v`
Expected: FAIL — the two `.rq` do not exist.

- [ ] **Step 3: Implement the two ASK queries**

`vocab/queries/looks-transposed.rq`:

```sparql
# looks-transposed.rq — a typed-numeric body ROW (cols>=1 all Numeric) but NO typed-numeric COLUMN
# (any column with all body cells Numeric). Body = row>=1. The transposition signature.
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  # a body row with >=1 cell in col>=1 and no non-Numeric cell in col>=1
  ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol . FILTER(?r >= 1 && ?rcol >= 1)
  FILTER NOT EXISTS { ?rx tab:atGridRow ?r ; tab:atGridColumn ?rxc ; tab:cellDatatype ?rd . FILTER(?rxc >= 1 && ?rd != tab:Numeric) }
  # AND no typed-numeric column (any column all body cells Numeric)
  FILTER NOT EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?cr . FILTER(?cr >= 1)
    FILTER NOT EXISTS { ?cx tab:atGridColumn ?col ; tab:atGridRow ?cxr ; tab:cellDatatype ?cd . FILTER(?cxr >= 1 && ?cd != tab:Numeric) }
  }
}
```

`vocab/queries/transpose-coherent.rq`:

```sparql
# transpose-coherent.rq — TRUE iff every row is type-homogeneous across its value columns (col>=1):
# NOT EXISTS a row with both a Numeric and a non-Numeric cell in col>=1.
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  FILTER NOT EXISTS {
    ?a tab:atGridRow ?r ; tab:atGridColumn ?ac ; tab:cellDatatype tab:Numeric . FILTER(?ac >= 1)
    ?b tab:atGridRow ?r ; tab:atGridColumn ?bc ; tab:cellDatatype ?bd . FILTER(?bc >= 1 && ?bd != tab:Numeric)
  }
}
```

- [ ] **Step 4: Rewire `orientation.py`**

In `src/iladub/etkl/orientation.py`, replace the bodies of `looks_transposed` and `transpose_is_coherent` (keep signatures/docstrings), building the evidence graph from `region.cells`:

```python
def _region_cells(region):
    return [(c.row, c.col, c.text) for c in region.cells]


def _ncols(region):
    return max((c.col for c in region.cells), default=-1) + 1


def looks_transposed(region) -> bool:
    from . import celltype
    import os
    g = celltype.grid_evidence(_region_cells(region), _ncols(region))
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "looks-transposed.rq")
    return celltype.run_ask(q, g)


def transpose_is_coherent(region) -> bool:
    from . import celltype
    import os
    g = celltype.grid_evidence(_region_cells(region), _ncols(region))
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "transpose-coherent.rq")
    return celltype.run_ask(q, g)
```

(The `from .headers import is_numeric` import at the top of `orientation.py` is now unused — remove it. `region.cells` `.text` is a property.)

- [ ] **Step 5: Run the tests + behavioural suites**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py tests/etkl/test_orientation.py -v`
Expected: PASS. Then the compile transpose path + full etkl: `.venv/bin/python -m pytest tests/etkl -q` — PASS (the transposed-table escalate/compile fixtures unchanged).

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/looks-transposed.rq vocab/queries/transpose-coherent.rq src/iladub/etkl/orientation.py tests/etkl/test_celltype.py
git commit -m "feat(etkl): transpose orientation oracle as SPARQL ASK over the typed-cell graph [B2a task 3]

looks_transposed + transpose_is_coherent derive over the evidence graph via ASK queries; behaviour
byte-identical (differential oracle).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Supersession + gate verification

Prove the whole lift, pin the gate, confirm source ownership.

**Files:**
- Modify: `tests/etkl/test_transform_gate.py`

- [ ] **Step 1: Extend the gate test**

Add to `tests/etkl/test_transform_gate.py`:

```python
def test_celltype_queries_present_no_tuned_constant():
    import glob, os, iladub.etkl.celltype as ct
    rqs = {os.path.basename(p) for p in glob.glob(os.path.join(QUERIES, "*.rq"))}
    assert {"header-body-split.rq", "stub-data-split.rq", "looks-transposed.rq", "transpose-coherent.rq"} <= rqs
    body = _strip_comments(open(ct.__file__, encoding="utf-8").read())
    assert not _FLOAT.search(body), "celltype.py must carry no tuned numeric constant"
```

(The existing `test_no_tuned_constant_in_rq_files` already globs `vocab/queries/*.rq`, so the four new `.rq` are auto-scanned — confirm by running it.)

- [ ] **Step 2: Run gate + whole suite + ownership**

Run: `.venv/bin/python -m pytest tests/etkl/test_transform_gate.py -v` — PASS.
Run: `.venv/bin/python -m pytest tests/etkl -q` — PASS.
Run: `.venv/bin/python -m pytest tests/test_source_ownership.py -v` — PASS (the four `.rq` + the `tab.ttl` evidence terms reference only owned `tab:`).
Run: `.venv/bin/python -m pytest -q` — PASS (only pre-existing skips).

- [ ] **Step 3: Commit**

```bash
git add tests/etkl/test_transform_gate.py
git commit -m "test(etkl): gate + supersession verification for the typed-cell evidence graph [B2a task 4]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage** (against `2026-07-16-typed-cell-evidence-graph-design.md`):
- §1/§4 the four decisions → SPARQL over the evidence graph → Tasks 1–3. ✔
- §2 AXIOM derivation (open-world SPARQL), PROCEDURAL emitter/runner/is_numeric, no tuned constant → Global Constraints + Task 4. ✔
- §3 typed-cell evidence graph + open `cellDatatype` lattice + column markers; header/body-split proven → Task 1. ✔
- §5 `celltype.py` + four `.rq` + evidence vocab → Tasks 1–3. ✔
- §7 differential oracle (frozen refs + battery) + behavioural green + gate test → all tasks. ✔
- §8 source ownership (owned `tab:` only) → Task 4. ✔
- §9 faithful lift; out-of-scope (regions.classify, richer types, is_numeric) honoured. ✔ B2b seam (open lattice) present. ✔

**2. Placeholder scan:** Clean. `header-body-split.rq` and `stub-data-split.rq` are feasibility-proven and reproduced verbatim; the two ASK queries and all reader/emitter code are complete; the frozen references are exact ports of the shipped Python. No TBD/TODO.

**3. Type consistency:** `grid_evidence(cells, ncols) -> Graph`, `run_scalar(rq, g, bindings) -> int|None`, `run_ask(rq, g) -> bool` used identically across Tasks 1–3. `_grid_cells(band, grid) -> [(r,c,text)]` (Task 1) reused by Task 2. The four functions keep their exact signatures (`header_body_split(band, grid)`, `stub_data_split(band, grid)`, `looks_transposed(region)`, `transpose_is_coherent(region)`) — every caller (matrix/rowheaders/hierarchical/segment/compile) untouched. `split` passed via `initBindings={"split": Literal(int, XSD.integer)}` consistently.
