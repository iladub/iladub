# Header→column Reconciliation Implementation Plan (Loop B)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the hierarchical header tree TILE for real reports whose header is a wrapped multi-word structure over a body-derived column grid contaminated by a leading caption line — closing the GrainCorp `MERGE_AMBIGUOUS` escalation.

**Architecture:** Two changes inside `infer_header_tree` (nothing in `compile.py`). (A) The **leaf** header row's column covering becomes an evidence-positive SPARQL AXIOM: a per-band header evidence graph (`headergraph.py`) + `vocab/queries/header-covers.rq` derives "leaf label covers column C iff C's center-x ∈ the label's ink extent" — no symmetrization. Parent rows keep the existing B1.1 `_covers_for_cell`+`repair_coverage`. (B) The tree is built from the **maximal body-adjacent contiguous suffix of header rows that passes `merge_tiling_ok`** (peel the top row and retry) — the tiling oracle disposes caption/fragment rows; no threshold.

**Tech Stack:** Python 3.12, rdflib 7.6.0 (SPARQL over an in-memory `Graph`), pytest. Test ONLY via `. .venv/bin/activate && python3 -m pytest` (bare `python3` uses rdflib 7.1.4 → ~60 spurious SPARQL failures).

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §8):** the leaf covering is an evidence-positive open-world SPARQL derivation — NO tuned constant, NO tolerance, NO symmetrization. The caption peel is disposed by the existing `merge_tiling_ok` oracle — NO threshold. The parent path (`_covers_for_cell`/`repair_coverage`) is unchanged justified PROCEDURAL geometry.
- **Honest escalation preserved:** if no header-row suffix tiles, `infer_header_tree` returns the full-header tree unchanged → the caller still escalates `MERGE_AMBIGUOUS`. Never assert a guess.
- **Source ownership:** every new term is owned `tab:` vocab (`https://w3id.org/iladub/tab#`); declared only in `vocab/ontology/tab.ttl`. No HGA/Fluree terms.
- **No overfitting:** validated on synthetic fixtures + a differential oracle, never tuned to GrainCorp bytes. All existing header/tiling/pivot tests + differential oracles + the full suite stay green.
- **No third-party PDF committed.** GrainCorp is a LOCAL confirmation only (`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf`).
- Query path convention: `Path(__file__).resolve().parents[3] / "vocab" / "queries" / "<name>.rq"` (mirrors `classifygraph.CLASSIFY_KIND_RQ`).

---

## File Structure

- **Create** `src/iladub/etkl/headergraph.py` — the header evidence graph + the covers runner (the PROCEDURAL layer for the AXIOM; mirrors `celltype.py`/`classifygraph.py`).
- **Create** `vocab/queries/header-covers.rq` — the leaf-row center-in-ink covering derivation (AXIOM).
- **Modify** `vocab/ontology/tab.ttl` — declare the new owned `tab:` terms.
- **Modify** `src/iladub/etkl/headers.py` — `infer_header_tree`: leaf covering via SPARQL + the caption-peel suffix loop.
- **Create** `tests/etkl/test_headergraph.py` — Task 1 unit tests.
- **Create** `tests/etkl/test_header_column_reconciliation.py` — Task 2 (wide-label red) + Task 4 (caption) integration tests.
- **Modify** `tests/etkl/test_derivation_equiv.py` — add `_ref_header_covers` + the differential oracle.

---

### Task 1: Header evidence graph + `header-covers.rq` + differential oracle (foundation)

**Files:**
- Create: `src/iladub/etkl/headergraph.py`
- Create: `vocab/queries/header-covers.rq`
- Modify: `vocab/ontology/tab.ttl` (add owned terms after the loop-B2c block)
- Test: `tests/etkl/test_headergraph.py` (new)
- Test: `tests/etkl/test_derivation_equiv.py` (add `_ref_header_covers` + oracle)

**Interfaces:**
- Consumes: `iladub.etkl.grid.LeafGrid` (`.boundaries: tuple[float,...]` len ncols+1, `.ncols: int`); header cells are any objects exposing `.text: str`, `.x0: float`, `.x1: float` (production: `iladub.etkl.cells.SourceCell`).
- Produces: `headergraph.header_evidence(header_rows, grid) -> rdflib.Graph`; `headergraph.run_covers(rq_path, graph) -> dict[tuple[int,int], tuple[int,...]]` keyed `(header_row_index, cell_index) -> sorted covered column indices` (LEAF row only); `headergraph.HEADER_COVERS_RQ: Path`.

- [ ] **Step 1: Grep tab.ttl to confirm the new terms are free**

Run: `grep -nE "tab:(HeaderCell|GridColumn|covers|atHeaderRow|headerText|inkX0|inkX1|colIndex|colCenterX|cellIndex)\b" vocab/ontology/tab.ttl || echo FREE`
Expected: `FREE` (none exist — the B2c lesson: never re-declare an existing term).

- [ ] **Step 2: Declare the owned terms in `vocab/ontology/tab.ttl`**

Add this block immediately AFTER the existing loop-B2c "band-classification evidence graph" block (after the `tab:RegionKind` region and its members; place it before the next `#####` section divider):

```turtle
# --- header-covering evidence graph (transient, pre-holon; loop B) ---
tab:HeaderCell a owl:Class ; rdfs:label "Header cell"@en ;
    rdfs:comment "A transient header-region cell (row, text, ink x-extent), evidence for the leaf-row column-covering derivation (header-covers.rq); never asserted into a holon."@en .
tab:GridColumn a owl:Class ; rdfs:label "Grid column"@en ;
    rdfs:comment "A transient leaf column (index + center-x), evidence for the covering derivation; never asserted into a holon."@en .
tab:atHeaderRow a owl:DatatypeProperty ; rdfs:domain tab:HeaderCell ; rdfs:range xsd:integer ; rdfs:label "at header row"@en ;
    rdfs:comment "0-based header-region row index (0 = topmost). The leaf row is MAX(atHeaderRow)."@en .
tab:headerText a owl:DatatypeProperty ; rdfs:domain tab:HeaderCell ; rdfs:range rdfs:Literal ; rdfs:label "header text"@en .
tab:cellIndex a owl:DatatypeProperty ; rdfs:domain tab:HeaderCell ; rdfs:range xsd:integer ; rdfs:label "cell index"@en ;
    rdfs:comment "0-based left-to-right position of the cell within its header row."@en .
tab:inkX0 a owl:DatatypeProperty ; rdfs:domain tab:HeaderCell ; rdfs:range xsd:double ; rdfs:label "ink x0"@en .
tab:inkX1 a owl:DatatypeProperty ; rdfs:domain tab:HeaderCell ; rdfs:range xsd:double ; rdfs:label "ink x1"@en .
tab:colIndex a owl:DatatypeProperty ; rdfs:domain tab:GridColumn ; rdfs:range xsd:integer ; rdfs:label "col index"@en .
tab:colCenterX a owl:DatatypeProperty ; rdfs:domain tab:GridColumn ; rdfs:range xsd:double ; rdfs:label "col center x"@en ;
    rdfs:comment "The x-midpoint of the column: (boundaries[i] + boundaries[i+1]) / 2."@en .
tab:covers a owl:ObjectProperty ; rdfs:domain tab:HeaderCell ; rdfs:range tab:GridColumn ; rdfs:label "covers"@en ;
    rdfs:comment "Derived: a LEAF header cell covers a grid column iff the column's center-x falls within the cell's ink x-extent (header-covers.rq). Evidence-positive, no symmetrization."@en .
```

- [ ] **Step 3: Write `vocab/queries/header-covers.rq`**

```sparql
# header-covers.rq (loop B, AXIOM) — LEAF-row header→column covering by exact center-in-ink.
# The leaf header row is the row nearest the body: MAX(?atHeaderRow). A leaf header cell covers a
# grid column iff that column's center-x falls within the cell's ink x-extent [inkX0, inkX1] —
# evidence-positive (coverage only where a column center is present under the label ink), open-world,
# NO symmetrization and NO tuned constant. This is the body-grounded fix for wide single-column
# labels (e.g. "Reference Number") that the old ink-extent "Merge & Center" symmetrization over-spans.
# Parent (upper) rows are NOT handled here — they keep the centering-bounded run extension in headers.py.
# Returns (?hrow ?cellIdx ?cidx): for each leaf header cell (row, cell-index), each covered column index.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?hrow ?cellIdx ?cidx WHERE {
  { SELECT (MAX(?r) AS ?leaf) WHERE { ?hc a tab:HeaderCell ; tab:atHeaderRow ?r } }
  ?cell a tab:HeaderCell ; tab:atHeaderRow ?hrow ; tab:cellIndex ?cellIdx ;
        tab:inkX0 ?x0 ; tab:inkX1 ?x1 .
  FILTER(?hrow = ?leaf)
  ?gc a tab:GridColumn ; tab:colIndex ?cidx ; tab:colCenterX ?cx .
  FILTER(?cx >= ?x0 && ?cx <= ?x1)
}
```

- [ ] **Step 4: Write `src/iladub/etkl/headergraph.py`**

```python
"""headergraph — the header-covering evidence graph + query runner (neurosymbolic loop B).

The LEAF header row's column covering is a declarative DERIVATION over per-cell ink extents and
per-column centers (open-world → SPARQL, the loop-B side of the gate; vocab/queries/header-covers.rq).
This module is the PROCEDURAL layer only: emitting the transient evidence graph and invoking rdflib.
No decision logic, no tuned constant — the covering decision lives entirely in header-covers.rq.
The band is the closure boundary: a fresh Graph() per call (mirrors classifygraph.py, loop B2c).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .grid import LeafGrid

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:header:")     # transient per-band instance namespace

# three dirs up from src/iladub/etkl/headergraph.py -> repo root, then vocab/queries/
HEADER_COVERS_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "header-covers.rq"


def header_evidence(header_rows: Sequence[Sequence[object]], grid: LeafGrid) -> Graph:
    """Fresh Graph() for one band's header region. `header_rows` is top-to-bottom; each cell exposes
    .text/.x0/.x1. Emits one tab:GridColumn per leaf column (colIndex + colCenterX) and one
    tab:HeaderCell per cell (atHeaderRow = row index, cellIndex = position in row, headerText,
    inkX0/inkX1). The leaf row is MAX(atHeaderRow)."""
    g = Graph()
    b = grid.boundaries
    for i in range(grid.ncols):
        col = URIRef(f"{_EV}col{i}")
        g.add((col, RDF.type, TAB.GridColumn))
        g.add((col, TAB.colIndex, Literal(i, datatype=XSD.integer)))
        g.add((col, TAB.colCenterX, Literal((b[i] + b[i + 1]) / 2.0, datatype=XSD.double)))
    for r, row in enumerate(header_rows):
        for j, cell in enumerate(row):
            hc = URIRef(f"{_EV}r{r}c{j}")
            g.add((hc, RDF.type, TAB.HeaderCell))
            g.add((hc, TAB.atHeaderRow, Literal(r, datatype=XSD.integer)))
            g.add((hc, TAB.cellIndex, Literal(j, datatype=XSD.integer)))
            g.add((hc, TAB.headerText, Literal(cell.text)))
            g.add((hc, TAB.inkX0, Literal(float(cell.x0), datatype=XSD.double)))
            g.add((hc, TAB.inkX1, Literal(float(cell.x1), datatype=XSD.double)))
    return g


def run_covers(rq_path, graph: Graph) -> dict:
    """Run header-covers.rq; return {(header_row_index, cell_index): tuple(sorted col indices)} for
    the LEAF row only (the query returns matches only, so cells covering no column are absent)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    out: dict[tuple[int, int], list[int]] = {}
    for row in graph.query(q):
        key = (int(row.hrow), int(row.cellIdx))
        out.setdefault(key, []).append(int(row.cidx))
    return {k: tuple(sorted(v)) for k, v in out.items()}
```

- [ ] **Step 5: Write `tests/etkl/test_headergraph.py`**

```python
"""Loop B foundation: the header-covering evidence graph + center-in-ink SPARQL derivation."""
from types import SimpleNamespace

from iladub.etkl.grid import LeafGrid
from iladub.etkl.headergraph import HEADER_COVERS_RQ, header_evidence, run_covers


def _cell(text, x0, x1):
    return SimpleNamespace(text=text, x0=x0, x1=x1)


def test_header_evidence_emits_columns_and_cells():
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("A", 110, 140), _cell("Reference", 170, 205), _cell("C", 210, 240)]]
    g = header_evidence(rows, grid)
    from rdflib import Namespace, RDF
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert len(list(g.subjects(RDF.type, TAB.GridColumn))) == 3
    assert len(list(g.subjects(RDF.type, TAB.HeaderCell))) == 3


def test_wide_label_covers_only_its_own_column():
    # boundaries 100,150,200,250 -> col centers 125,175,225. "Reference" ink [170,205] contains
    # ONLY col1's center (175); cols 0 and 2 sit under A/C -> covers {1}, NOT the symmetrized {0,1,2}.
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("A", 110, 140), _cell("Reference", 170, 205), _cell("C", 210, 240)]]
    covers = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
    assert covers == {(0, 0): (0,), (0, 1): (1,), (0, 2): (2,)}


def test_only_leaf_row_is_covered():
    # A parent row (row 0) and a leaf row (row 1); the query targets MAX(atHeaderRow) = 1 only.
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("Parent", 120, 230)],
            [_cell("A", 110, 140), _cell("B", 160, 190), _cell("C", 210, 240)]]
    covers = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
    assert set(k[0] for k in covers) == {1}          # only leaf row 1
    assert covers[(1, 0)] == (0,) and covers[(1, 2)] == (2,)
```

- [ ] **Step 6: Run the foundation tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_headergraph.py -q`
Expected: 3 passed.

- [ ] **Step 7: Add the differential oracle to `tests/etkl/test_derivation_equiv.py`**

At the top of the file add (near the other imports):

```python
from types import SimpleNamespace
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headergraph import HEADER_COVERS_RQ, header_evidence, run_covers
```

Then add the reference + oracle test:

```python
def _ref_header_covers(header_rows, grid):
    """Python reference for header-covers.rq: for the LEAF row (max index), a cell covers the columns
    whose center-x is within [inkX0, inkX1]. Returns {(leaf_row, cell_idx): tuple(cols)} for cells that
    cover >=1 column (the SPARQL query returns matches only)."""
    b = grid.boundaries
    centers = [(b[i] + b[i + 1]) / 2.0 for i in range(grid.ncols)]
    if not header_rows:
        return {}
    leaf = len(header_rows) - 1
    out = {}
    for j, cell in enumerate(header_rows[leaf]):
        cols = tuple(i for i, cx in enumerate(centers) if cell.x0 <= cx <= cell.x1)
        if cols:
            out[(leaf, j)] = cols
    return out


def test_header_covers_new_matches_ref():
    import random
    rnd = random.Random(20260726)
    for _ in range(200):
        ncols = rnd.randint(2, 6)
        # strictly-increasing boundaries, each column >= 5 pt wide
        b = [0.0]
        for _i in range(ncols):
            b.append(b[-1] + rnd.uniform(5.0, 90.0))
        grid = LeafGrid(tuple(b), ncols, (b[-1] - b[0]) / ncols, 1.0)
        rows = []
        for _r in range(rnd.randint(1, 3)):
            cells = []
            for _c in range(rnd.randint(1, ncols)):
                x0 = rnd.uniform(b[0], b[-1])
                x1 = x0 + rnd.uniform(1.0, 140.0)
                cells.append(SimpleNamespace(text="t", x0=x0, x1=x1))
            rows.append(cells)
        got = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
        assert got == _ref_header_covers(rows, grid)
```

- [ ] **Step 8: Run the oracle**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_derivation_equiv.py::test_header_covers_new_matches_ref -q`
Expected: 1 passed (SPARQL == python reference over 200 random shapes).

- [ ] **Step 9: Commit**

```bash
git add src/iladub/etkl/headergraph.py vocab/queries/header-covers.rq vocab/ontology/tab.ttl tests/etkl/test_headergraph.py tests/etkl/test_derivation_equiv.py
git commit -m "feat(etkl): header-covering evidence graph + header-covers.rq (loop B foundation)"
```

---

### Task 2: Wide single-column label — failing integration test (TDD red)

**Files:**
- Create: `tests/etkl/test_header_column_reconciliation.py`

**Interfaces:**
- Consumes: `iladub.etkl.geometry.{Word,Line}`, `iladub.etkl.bands.Band`, `iladub.etkl.grid.LeafGrid`, `iladub.etkl.headers.{infer_header_tree, merge_tiling_ok}`.
- Produces: a correctness test asserting a wide-label header tree TILES. Fails on current (symmetrizing) code; passes after Task 3.

- [ ] **Step 1: Write the failing test**

This uses a hand-built `Band` + explicit `LeafGrid` (bypassing `infer_leaf_grid`, which needs ~48 data rows to resolve columns whose gutters wide header ink straddles — see `tests/etkl/test_span_gate.py`). Coordinates are VERIFIED to reproduce the bug: `Reference` symmetrizes to covers (0,1,2), overlapping `A`(0) and `C`(2) → `merge_tiling_ok` False today.

```python
"""Loop B — header→column reconciliation: wide single-column labels + leading caption line.
See docs/superpowers/specs/2026-07-26-header-column-reconciliation-design.md."""
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import infer_header_tree, merge_tiling_ok


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


# 3 narrow columns: boundaries 100,150,200,250 -> centers 125,175,225. A single header row where
# the middle label "Reference" has wide ink [170,205] that straddles the col1/col2 gutter but whose
# CENTER-in-ink hits only col1. Old symmetrization -> covers(0,1,2) -> overlaps A(0)/C(2) -> escalate.
_GRID = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)


def _wide_label_band():
    header = [_w("A", 110, 140, 0.0), _w("Reference", 170, 205, 0.0), _w("C", 210, 240, 0.0)]
    d1 = [_w("a", 110, 140, 12.0), _w("56", 170, 205, 12.0), _w("c", 210, 240, 12.0)]
    d2 = [_w("a2", 110, 140, 24.0), _w("57", 170, 205, 24.0), _w("c2", 210, 240, 24.0)]
    return Band((_line(header, 0.0), _line(d1, 12.0), _line(d2, 24.0)), 0.0, 34.0)


def test_wide_single_column_label_tiles():
    # split=1: row 0 is the header, rows 1-2 are data. The wide "Reference" label must NOT be
    # over-spanned; the tree must tile (each column claimed by exactly one leaf label).
    tree = infer_header_tree(_wide_label_band(), _GRID, 1)
    assert tree is not None
    assert merge_tiling_ok(tree, _GRID) is True
```

- [ ] **Step 2: Run it to verify it fails (documents the bug)**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_column_reconciliation.py -q`
Expected: FAIL — `merge_tiling_ok` returns False because `Reference` symmetrizes to covers (0,1,2), overlapping `A` and `C` at level 0. Record the observed covers in the report.

- [ ] **Step 3: Commit the red test**

```bash
git add tests/etkl/test_header_column_reconciliation.py
git commit -m "test(etkl): failing wide-single-column-label header tree case (loop B red)"
```

---

### Task 3: Leaf covering via SPARQL in `infer_header_tree` (green, Cause A)

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`infer_header_tree`)

**Interfaces:**
- Consumes: `headergraph.header_evidence`, `headergraph.run_covers`, `headergraph.HEADER_COVERS_RQ`.
- Produces: `infer_header_tree` where the LEAF row's covers come from `header-covers.rq` (parents unchanged).

- [ ] **Step 1: Add the headergraph import to `headers.py`**

Near the other `from .` imports at the top of `src/iladub/etkl/headers.py`:

```python
from .headergraph import HEADER_COVERS_RQ, header_evidence, run_covers
```

- [ ] **Step 2: Replace the node-building block in `infer_header_tree`**

Find this block (currently after `header_rows` is computed and the `if not header_rows: return None` guard):

```python
    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            covers = _covers_for_cell(cell, b)
            cx = (cell.x0 + cell.x1) / 2.0
            nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))

    nodes = repair_coverage(nodes, grid)   # centering-bounded span resolution (B1.1)
```

Replace it with (LEAF row from the SPARQL derivation; parents unchanged):

```python
    # LEAF row (row nearest the body) covering is a body-grounded AXIOM: a leaf label covers a
    # column iff the column's center-x is within the label's ink extent (header-covers.rq). This
    # replaces the "Merge & Center" ink-extent symmetrization for leaves only, which over-spanned
    # wide single-column labels (e.g. "Reference Number"). Parent rows keep _covers_for_cell +
    # repair_coverage (the centering-bounded run extension, B1.1).
    leaf_lvl = len(header_rows) - 1
    covers_map = run_covers(HEADER_COVERS_RQ, header_evidence(header_rows, grid))

    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for j, cell in enumerate(row):
            cx = (cell.x0 + cell.x1) / 2.0
            if lvl == leaf_lvl:
                covers = covers_map.get((lvl, j), ())    # SPARQL leaf covering (may be empty)
            else:
                covers = _covers_for_cell(cell, b)        # parent path, unchanged
            nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))

    nodes = repair_coverage(nodes, grid)   # non-leaf levels only (B1.1); leaf covers preserved
```

- [ ] **Step 3: Run Task 2's wide-label test — verify it now passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_column_reconciliation.py -q`
Expected: PASS (`Reference` now covers (1) only → clean partition → tiles).

- [ ] **Step 4: Run the full suite; decide the uncovered-column fallback empirically**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass. In particular the pivot/hierarchical fixtures (`test_hierarchical.py`, `test_hier_holon.py`, `test_headers.py`, `test_span_gate.py`, `test_merge_resolution.py`, `test_b1_3_merge_resolution.py`) must stay green — the leaf change only narrows over-spanned leaves; genuine parents are untouched.

**Decision (empirical, per spec §3.2):**
- **If the suite is fully green:** the strict center-in-ink rule suffices — do nothing more; note in the report that no fallback was needed.
- **If (and only if) a fixture regresses because a leaf column is now uncovered** (a leaf label whose ink no longer reaches its column center, so `covers_map` omits that column → a coverage gap), apply the threshold-free nearest-center Voronoi fallback: insert this immediately AFTER the `covers_map = run_covers(...)` line in Step 2:

```python
    # Voronoi fallback (body-grounded, threshold-free): a leaf column whose center falls under no
    # leaf label's ink is assigned to the leaf label whose center-x is nearest. Still a partition,
    # no tolerance. Added only because a real fixture needed it (see report).
    if header_rows:
        leaf_row = header_rows[leaf_lvl]
        covered = {c for cols in covers_map.values() for c in cols}
        leaf_centers = [((cell.x0 + cell.x1) / 2.0, j) for j, cell in enumerate(leaf_row)]
        for i in range(grid.ncols):
            if i not in covered and leaf_centers:
                colc = (b[i] + b[i + 1]) / 2.0
                _, j = min((abs(colc - cc), jj) for cc, jj in leaf_centers)
                covers_map[(leaf_lvl, j)] = tuple(sorted(covers_map.get((leaf_lvl, j), ()) + (i,)))
```

Re-run the suite; confirm green. Document either outcome (fallback applied or not) in the report.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/headers.py
git commit -m "feat(etkl): leaf header covering by center-in-ink SPARQL derivation (loop B, Cause A)"
```

---

### Task 4: Caption / non-header-row peel (green, Cause B)

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`infer_header_tree` — wrap tree assembly in a suffix loop)
- Test: `tests/etkl/test_header_column_reconciliation.py` (add caption case)

**Interfaces:**
- Consumes: `merge_tiling_ok` (same module).
- Produces: `infer_header_tree` returns the largest body-adjacent header-row suffix whose tree tiles; else the full tree (→ honest escalation).

- [ ] **Step 1: Write the failing caption test**

Add to `tests/etkl/test_header_column_reconciliation.py`:

```python
def _caption_band():
    # row 0 = caption ("Friday 2026" spanning wide); row 1 = clean leaf header (A,B,C); rows 2-3 data.
    cap = [_w("Friday", 120, 190, 0.0), _w("2026", 205, 240, 0.0)]
    leaf = [_w("A", 110, 140, 12.0), _w("B", 160, 190, 12.0), _w("C", 210, 240, 12.0)]
    d1 = [_w("a", 110, 140, 24.0), _w("b", 160, 190, 24.0), _w("c", 210, 240, 24.0)]
    d2 = [_w("a2", 110, 140, 36.0), _w("b2", 160, 190, 36.0), _w("c2", 210, 240, 36.0)]
    return Band((_line(cap, 0.0), _line(leaf, 12.0), _line(d1, 24.0), _line(d2, 36.0)), 0.0, 46.0)


def test_leading_caption_is_peeled_and_tiles():
    # split=2: rows 0-1 are the header region (0 = caption, 1 = real leaf header); rows 2-3 data.
    # The caption row cannot tile (it overlaps at level 0); the peel keeps the leaf-row suffix.
    tree = infer_header_tree(_caption_band(), _GRID, 2)
    assert tree is not None
    assert merge_tiling_ok(tree, _GRID) is True
    # the caption text must not survive as a header node
    assert all("Friday" not in n.text and "2026" not in n.text for n in tree)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_column_reconciliation.py::test_leading_caption_is_peeled_and_tiles -q`
Expected: FAIL — the caption row's cells overlap at level 0 (`Friday`→covers(0,1,2) vs `2026`→col 2), so `merge_tiling_ok` is False.

- [ ] **Step 3: Refactor `infer_header_tree` to build the tree from a suffix, then peel**

Wrap the node-building + repair + narrow-flank + parent-linking into an inner function `_build(rows)` and iterate suffixes. Replace everything from the `leaf_lvl = ...` line (Step 2 of Task 3) THROUGH the final `return tuple(linked)` with:

```python
    def _build(rows):
        """Assemble a header tree from `rows` (top-to-bottom header rows). Leaf covers via the
        SPARQL AXIOM; parents via _covers_for_cell + repair_coverage. Returns tuple[HeaderNode,...]."""
        leaf_lvl = len(rows) - 1
        covers_map = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))

        nodes: list[HeaderNode] = []
        for lvl, row in enumerate(rows):
            for j, cell in enumerate(row):
                cx = (cell.x0 + cell.x1) / 2.0
                if lvl == leaf_lvl:
                    covers = covers_map.get((lvl, j), ())
                else:
                    covers = _covers_for_cell(cell, b)
                nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))

        nodes = repair_coverage(nodes, grid)

        ink_cols_by_node = []
        for lvl, row in enumerate(rows):
            for cell in row:
                lo = column_of(cell.x0 + 0.1, b)
                hi = column_of(cell.x1 - 0.1, b)
                ink_cols_by_node.append(tuple(range(min(lo, hi), max(lo, hi) + 1)))
        nodes = resolve_narrow_flanks(nodes, grid, ink_cols_by_node)

        linked: list[HeaderNode] = []
        for n in nodes:
            parent_idx = None
            for k, m in enumerate(nodes):
                if m.level == n.level - 1 and set(n.covers) <= set(m.covers):
                    parent_idx = k
                    break
            linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx,
                                     n.center_x, n.ambiguous, n.ambiguous_flank))
        return tuple(linked)

    # Caption / non-header-row peel (Cause B): keep the MAXIMAL body-adjacent contiguous suffix of
    # header rows whose tree tiles. A genuine top parent row joins the tiling (its covers = unions of
    # leaf runs); a caption/fragment row cannot join -> it is peeled. Disposed by merge_tiling_ok, no
    # threshold. If nothing tiles, return the full-header tree unchanged (caller escalates -> honest).
    for k in range(len(header_rows)):
        candidate = _build(header_rows[k:])
        if merge_tiling_ok(candidate, grid):
            return candidate
    return _build(header_rows)
```

Note: if you added the Voronoi fallback in Task 3, move it inside `_build` immediately after its `covers_map = run_covers(...)` line (using `rows`/`leaf_lvl` local to `_build`). Keep `merge_tiling_ok` imported/defined in this module (it already is).

- [ ] **Step 4: Run the caption test + the wide-label test**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_column_reconciliation.py -q`
Expected: 2 passed (wide-label tiles; caption peeled and tiles, no `Friday`/`2026` nodes).

- [ ] **Step 5: Run the full suite (no regression)**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass. Genuine hierarchical/pivot fixtures still tile (a real top parent row is never peeled because it joins the tiling); honest escalations (no tiling suffix) unchanged.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_header_column_reconciliation.py
git commit -m "feat(etkl): oracle-disposed caption/non-header-row peel (loop B, Cause B)"
```

---

### Task 5: Full-suite verification + GrainCorp end-to-end confirmation

**Files:**
- None committed (verification only).

- [ ] **Step 1: Full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior total + the new Task 1/2/4 tests). Confirm zero regressions in header/tiling/pivot fixtures, `region_tiles`, and the differential oracles (`test_derivation_equiv.py`). If any regresses, read it and reconcile (do NOT weaken a test) — a genuine merged-header fixture must still assert with its hierarchy intact; if a leaf column regressed to uncovered, the Task 3 Voronoi fallback is the fix.

- [ ] **Step 2: GrainCorp real-world confirmation (LOCAL, not committed)**

Run:
```bash
. .venv/bin/activate && python3 -c "
from iladub.etkl.compile import compile_tables
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
r=compile_tables(p)
for reg in r.regions:
    print(reg.kind, reg.verdict, 'cells=', reg.cells, 'reason=', reg.reason, 'anchor=', reg.anchor)
print('score=', r.score)
"
```
Expected: the big table region is no longer `escalated`/`MERGE_AMBIGUOUS` — it **asserts** `tab:HierarchicalTable` with cells > 0 and the overall score > 0. Record the observed region line(s) in the report. Do NOT commit the PDF. (If GrainCorp still escalates on a *different*, newly-exposed reason — e.g. row-grouping/subtotals or the split-number cells — record that reason verbatim; it defines Loop C and is out of scope here. Cause A + Cause B closing means the header tree tiles; a residual downstream escalation on the `… Total` rows is acceptable and named.)

- [ ] **Step 3: Commit (only if a regression fix was needed in Step 1; otherwise skip)**

```bash
git add -A && git commit -m "fix(etkl): <describe any regression fix>"
```

---

## Self-Review

**Spec coverage:**
- §1/§3.1 header evidence graph (`headergraph.py`) + owned `tab:` terms → Task 1.
- §1/§3.2 `header-covers.rq` leaf center-in-ink AXIOM → Task 1 (query) + Task 3 (wired into `infer_header_tree`); the uncovered-column Voronoi fallback → Task 3 Step 4 (empirical, both outcomes spelled out).
- §1/§3.3 caption peel (maximal body-adjacent tiling suffix) → Task 4.
- §3.4 differential oracle (`_ref_header_covers`) → Task 1 Step 7.
- §4 committed synthetic fixtures (wide-label red, caption) → Tasks 2, 4; genuine-merged-parent regression guard → covered by the existing pivot fixtures re-run in Task 3 Step 4 / Task 4 Step 5 / Task 5 Step 1; GrainCorp local confirmation → Task 5 Step 2.
- §5 gate (AXIOM leaf covering, oracle-disposed peel, parents unchanged, honest escalation, source ownership, no PDF) → constraints threaded through Tasks 1/3/4/5.

**Placeholder scan:** none — full code for `headergraph.py`, the `.rq`, the `tab.ttl` terms, the `infer_header_tree` edits, and every test is given; the one conditional (Voronoi fallback) carries its exact code and an explicit apply/skip criterion.

**Type consistency:** `header_evidence(header_rows, grid) -> Graph`, `run_covers(rq, graph) -> dict[(int,int), tuple[int,...]]`, `HEADER_COVERS_RQ: Path`, `_ref_header_covers` same key shape, `infer_header_tree(band, grid, body_line) -> tuple[HeaderNode,...]|None` unchanged signature, `HeaderNode(level, covers, text, parent, center_x, ambiguous, ambiguous_flank)` — consistent across Tasks 1/3/4. The leaf key `(leaf_lvl, j)` matches between `run_covers` output and the node loop.

**Note (verified during planning):** the wide-label fixture coordinates (boundaries 100/150/200/250; `Reference` ink [170,205]) were probed against the current code and DO reproduce the bug (`Reference`→covers(0,1,2), `merge_tiling_ok` False); center-in-ink yields covers(1). The caption fixture likewise reproduces a level-0 overlap. The peel operates on the `header_rows` list inside `infer_header_tree` (NOT by rebuilding a Band — that breaks `group_wrapped`/`body_top`).
