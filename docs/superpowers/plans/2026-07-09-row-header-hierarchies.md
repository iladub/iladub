# Row-Header Hierarchies Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a table with a flat column header and a hierarchical row header (grouped stub columns, blank-below encoding) into a `tab:HierarchicalTable` with a row-header tree (`tab:coversRow`), instead of flattening it to a record.

**Architecture:** The vertical mirror of Loop 2. Stub columns form the row-header tree (each stub column = a level; a cell's row-span = the blank-below forward-fill run); only data columns are entry-bearing leaf columns (Design A: qb:/Wang). A new `rowheaders.py` mirrors `headers.py`; a new `assert_row_hier_region` reuses Loop 4's shared entry emitters; a new `tab:coversRow` + four guarded row SHACL shapes mirror the column side. Blank-below = ditto-grouping is a documented *reading convention* (like Loop 2's centered-merge); the row SHACL + per-cell round-trip certify the structure.

**Tech Stack:** Python 3, rdflib, pdfplumber/reportlab (fixtures), pyshacl, pytest.

## Global Constraints

- **Source ownership:** `vocab/ontology/tab.ttl` and `vocab/shapes/tab-shapes.ttl` stay standalone — every subject a `tab:` term; ZERO `w3id.org/holon` references. (CI: `tests/test_source_ownership.py`.)
- **No regression from the new row shapes:** row `Coverage` and `UnambiguousRowAccess` MUST be guarded to fire only for tables that have a row axis (`∃ ?h tab:coversRow ?r`). A flat/column-only table (leaf rows, no row-headers) must still pass. Verify the existing tab example suite stays green.
- **No silent-wrong:** the flat-record `else` branch in `compile.py` stays byte-for-byte unchanged; an entry that fails the per-cell round-trip escalates `ROUND_TRIP_FAIL`; a row-group whose tree does not tile escalates `ROW_GROUP_AMBIGUOUS`.
- **No overfitting:** oracles are structural (type-homogeneity, blank-below runs, tiling), not constants tuned to a fixture. Blank-below-as-grouping is a documented convention, not a claimed semantic proof.
- **Provenance-to-the-page:** every emitted cell (entries AND row-header LabelCells) carries bbox/onPage from its physical source cell.
- **Design A (settled):** leaf columns = data columns only; stub columns are the row-header axis; `North` encoded once as a row-header node.

**Confirmed by empirical probe (2026-07-09):** a row-grouped fixture (`Region|Metric|Value`, blank stub cells) classifies as `RECORD_TABLE` with a clean 3-column grid; `looks_transposed` is False; `header_body_split` = 1; `logical_rows` recovers 5 leaf rows anchored on the populated `Metric` column; `_col_values` reports col0=[North,South] (blanks skipped), col1 fully populated, col2 all-numeric.

---

### Task 1: `rowheaders.py` — stub/data split + row-grouping detection

**Files:**
- Create: `src/iladub/etkl/rowheaders.py`
- Modify: `tests/etkl/fixtures.py` (append `row_grouped_table_pdf`, `single_stub_blank_pdf`)
- Test: `tests/etkl/test_rowheaders.py` (create)

**Interfaces:**
- Consumes: `headers.header_body_split`, `headers.is_numeric`, `headers._col_values`; `rows.logical_rows`; `regions.column_of`; a `ClassifiedRegion` with `.band`, `.grid`, `.cells`.
- Produces:
  - `stub_data_split(band, grid) -> int | None` — number of leading stub columns `k` (data columns = `[k..ncols-1]`); `None` if no clean text|numeric split.
  - `_present_rows(leaf_rows, grid, col) -> list[int]` — leaf-row indices whose RowBand has a cell in `col`.
  - `looks_row_grouped(region) -> bool` — the blank-below detection signature.

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_rowheaders.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import (row_grouped_table_pdf, simple_table_pdf,
                                 all_text_table_pdf, single_stub_blank_pdf)
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.rowheaders import stub_data_split, looks_row_grouped


def _region(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return classify(band), band


def test_stub_data_split_row_grouped(tmp_path):
    reg, band = _region(row_grouped_table_pdf, tmp_path)
    assert stub_data_split(band, reg.grid) == 2   # cols 0,1 stub; col 2 data


def test_stub_data_split_flat_record(tmp_path):
    # simple_table: Analyte | Value(num) | Unit -> first data col is 1, but col 2 is
    # text -> not all cols from k are numeric -> None (not a stub/data table).
    reg, band = _region(simple_table_pdf, tmp_path)
    assert stub_data_split(band, reg.grid) is None


def test_looks_row_grouped_true(tmp_path):
    reg, _ = _region(row_grouped_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is True


def test_flat_record_not_row_grouped(tmp_path):
    reg, _ = _region(simple_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is False


def test_all_text_not_row_grouped(tmp_path):
    reg, _ = _region(all_text_table_pdf, tmp_path)
    assert looks_row_grouped(reg) is False


def test_single_stub_blank_not_row_grouped(tmp_path):
    # one stub column with blanks but NO fully-populated finer stub -> leaf rows
    # unidentifiable -> not row-grouped (stays on record path).
    reg, _ = _region(single_stub_blank_pdf, tmp_path)
    assert looks_row_grouped(reg) is False
```

- [ ] **Step 2: Add the fixtures**

Append to `tests/etkl/fixtures.py`:

```python
def row_grouped_table_pdf(path: str) -> dict:
    """A ROW-header hierarchy: 'Region' groups (North/South) run DOWN the first stub
    column via the blank-below (forward-fill) encoding; 'Metric' is a fully-populated
    finer stub; 'Value' is the numeric data column. North spans Revenue/Cost/Margin;
    South spans Revenue/Cost. Today this flattens to a RecordTable; the loop compiles
    the row-header tree."""
    cols = [72.0, 200.0, 360.0]           # Region, Metric, Value
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Region", "Metric", "Value"),
            ("North", "Revenue", "100"),
            ("", "Cost", "60"),
            ("", "Margin", "40"),
            ("South", "Revenue", "120"),
            ("", "Cost", "70")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_leaf_rows": 5, "n_data_cols": 1,
            "groups": {"North": 3, "South": 2}}


def single_stub_blank_pdf(path: str) -> dict:
    """One stub column ('Region') with blank-below, but NO fully-populated finer stub
    column — just Region + Value(numeric). The sub-rows have no identity, so this must
    NOT be detected as row-grouped (leaf rows unidentifiable)."""
    cols = [72.0, 300.0]                   # Region, Value
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Region", "Value"), ("North", "100"), ("", "60"), ("South", "120")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_rowheaders.py -q`
Expected: FAIL with `ImportError: cannot import name 'stub_data_split'`.

- [ ] **Step 4: Implement the module core**

Create `src/iladub/etkl/rowheaders.py`:

```python
"""rowheaders — the vertical mirror of headers.py: a row-header tree from stub columns.

Stub columns (leading text columns, left of the numeric data) form the row-header
tree. Each stub column is a level; a stub cell's ROW-span is the blank-below
(forward-fill) run — its row down to (excluding) the next non-blank cell in that
column. Blank-below = ditto-grouping is a documented reading CONVENTION (the mirror
of Loop 2's centered-merge = column-span); the row SHACL + per-cell round-trip
certify the resulting structure.
"""
from __future__ import annotations

from .bands import Band
from .grid import LeafGrid
from .headers import header_body_split, is_numeric, _col_values
from .regions import column_of


def stub_data_split(band: Band, grid: LeafGrid) -> int | None:
    """Number of leading stub (text) columns k; data columns are [k..ncols-1].

    On body rows (below header_body_split), a column is 'data' iff its non-blank
    cells are all numeric. The split k = the first data column; requires k >= 1 (at
    least one stub) and every column from k rightward is data. None if no such clean
    text|numeric boundary (falls through to the record path).
    """
    split = header_body_split(band, grid)
    if split is None:
        return None
    cols = _col_values(list(band.lines), grid, split)   # {col: [non-blank body texts]}
    ncols = grid.ncols
    numeric = [bool(cols[i]) and all(is_numeric(v) for v in cols[i]) for i in range(ncols)]
    k = next((i for i in range(ncols) if numeric[i]), None)
    if k is None or k == 0:
        return None                       # no data column, or no stub column
    if not all(numeric[i] for i in range(k, ncols)):
        return None                       # a text column sits after the data — not a clean split
    return k


def _present_rows(leaf_rows, grid: LeafGrid, col: int) -> list[int]:
    """Leaf-row indices whose RowBand has a cell mapping to `col`."""
    b = grid.boundaries
    out = []
    for i, rb in enumerate(leaf_rows):
        if any(column_of((c.x0 + c.x1) / 2.0, b) == col for c in rb.cells):
            out.append(i)
    return out


def looks_row_grouped(region) -> bool:
    """True iff a coarse stub column is under-populated (blank-below grouping) while
    the RIGHTMOST stub column is fully populated (one label per leaf row, so leaf
    rows are individually identified). A flat record (every stub cell present) -> False;
    an all-text table (no data column) -> stub_data_split None -> False.
    """
    from .rows import logical_rows
    band, grid = region.band, region.grid
    if band is None or grid is None:
        return False
    k = stub_data_split(band, grid)
    if k is None:
        return False
    split = header_body_split(band, grid)
    leaf_rows = logical_rows(band, grid, band.lines[split].top)
    if not leaf_rows:
        return False
    n = len(leaf_rows)
    if len(_present_rows(leaf_rows, grid, k - 1)) != n:
        return False                      # finest stub not fully populated -> leaf rows unidentifiable
    return any(len(_present_rows(leaf_rows, grid, s)) < n for s in range(k - 1))
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_rowheaders.py -q`
Expected: PASS (6 tests).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/rowheaders.py tests/etkl/fixtures.py tests/etkl/test_rowheaders.py
git commit -m "feat(etkl): rowheaders — stub/data split + looks_row_grouped detection"
```

---

### Task 2: `rowheaders.py` — the row-header tree + tiling backstop

**Files:**
- Modify: `src/iladub/etkl/rowheaders.py`
- Test: `tests/etkl/test_rowheaders.py`

**Interfaces:**
- Consumes: Task 1's `stub_data_split`, `_present_rows`; `cells.recover_leaf_grid`; `rows.logical_rows`, `rows.RowBand`; `regions.column_of`.
- Produces:
  - `RowHeaderNode(level, covers_rows, text, parent, x0, top, x1, bottom, page)` (frozen dataclass).
  - `infer_row_header_tree(band, grid, stub_cols, leaf_rows) -> tuple[RowHeaderNode, ...] | None`.
  - `row_tree_tiles(tree, n_leaf_rows) -> bool` — the structural backstop.
  - `RowHierRegion(grid, tree, leaf_rows, stub_cols, data_cols, body_line)` (frozen dataclass).
  - `classify_row_hier(band) -> RowHierRegion | None` — chains the stages (mirror of `classify_hierarchical`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_rowheaders.py`:

```python
from iladub.etkl.rowheaders import (RowHeaderNode, infer_row_header_tree,
                                    row_tree_tiles, classify_row_hier)


def test_infer_row_tree_groups(tmp_path):
    reg, band = _region(row_grouped_table_pdf, tmp_path)
    rreg = classify_row_hier(band)
    assert rreg is not None
    tree = rreg.tree
    # level-0 groups: North covers 3 leaf rows, South covers 2
    l0 = {n.text: n.covers_rows for n in tree if n.level == 0}
    assert l0["North"] == (0, 1, 2)
    assert l0["South"] == (3, 4)
    # level-1 leaves: one row each, parented to their group
    l1 = [n for n in tree if n.level == 1]
    assert len(l1) == 5
    north_idx = next(i for i, n in enumerate(tree) if n.text == "North")
    assert all(tree[n.parent].text == "North" for n in l1 if n.covers_rows[0] < 3)
    assert any(n.parent == north_idx for n in l1)


def test_row_tree_tiles_true(tmp_path):
    _, band = _region(row_grouped_table_pdf, tmp_path)
    rreg = classify_row_hier(band)
    assert row_tree_tiles(rreg.tree, len(rreg.leaf_rows)) is True


def test_row_tree_tiles_rejects_pathology():
    # a gap (row 2 uncovered by any leaf) and an overlap (two leaves share row 0)
    def node(level, covers, parent):
        return RowHeaderNode(level, covers, "x", parent, 0.0, 0.0, 1.0, 1.0, 0)
    gap = (node(0, (0,), None), node(0, (1,), None))            # 3 rows, row 2 uncovered
    assert row_tree_tiles(gap, 3) is False
    overlap = (node(0, (0,), None), node(0, (0, 1), None))      # both leaves cover row 0
    assert row_tree_tiles(overlap, 2) is False


def test_classify_row_hier_flat_is_none(tmp_path):
    _, band = _region(simple_table_pdf, tmp_path)
    assert classify_row_hier(band) is None
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_rowheaders.py -q -k "tree or classify_row"`
Expected: FAIL (ImportError on `RowHeaderNode`).

- [ ] **Step 3: Implement the tree + tiling + classify**

Append to `src/iladub/etkl/rowheaders.py`:

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RowHeaderNode:
    level: int
    covers_rows: tuple[int, ...]
    text: str
    parent: int | None
    x0: float
    top: float
    x1: float
    bottom: float
    page: int


def infer_row_header_tree(band, grid, stub_cols, leaf_rows):
    """A row-header node per non-blank stub cell; its row-span = the blank-below run
    (its row down to, excluding, the next non-blank cell in that stub column). Parent
    = the nearest coarser (level-1) node whose row-covers contain this node's. Mirror
    of headers.infer_header_tree on the vertical axis. None if no node is found.
    """
    b = grid.boundaries
    n = len(leaf_rows)
    nodes: list[RowHeaderNode] = []
    for level, s in enumerate(stub_cols):
        present = _present_rows(leaf_rows, grid, s)
        for idx, r in enumerate(present):
            end = present[idx + 1] if idx + 1 < len(present) else n
            covers = tuple(range(r, end))
            cell = next(c for c in leaf_rows[r].cells
                        if column_of((c.x0 + c.x1) / 2.0, b) == s)
            nodes.append(RowHeaderNode(level, covers, cell.text, None,
                                       cell.x0, cell.top, cell.x1, cell.bottom, cell.page))
    if not nodes:
        return None
    linked: list[RowHeaderNode] = []
    for nd in nodes:
        pidx = None
        for j, m in enumerate(nodes):
            if m.level == nd.level - 1 and set(nd.covers_rows) <= set(m.covers_rows):
                pidx = j
                break
        linked.append(replace(nd, parent=pidx))
    return tuple(linked)


def row_tree_tiles(tree, n_leaf_rows: int) -> bool:
    """Structural backstop: the leaf-level row-headers (no children) must partition
    {0..n_leaf_rows-1} exactly, and every child's row-covers must be a subset of its
    parent's. Catches pathological geometry before it reaches the row SHACL.
    """
    for nd in tree:
        if nd.parent is not None and not set(nd.covers_rows) <= set(tree[nd.parent].covers_rows):
            return False
    has_child = {nd.parent for nd in tree if nd.parent is not None}
    covered: list[int] = []
    for i, nd in enumerate(tree):
        if i not in has_child:                     # a leaf row-header
            covered.extend(nd.covers_rows)
    return sorted(covered) == list(range(n_leaf_rows))


@dataclass(frozen=True)
class RowHierRegion:
    grid: object
    tree: tuple
    leaf_rows: tuple
    stub_cols: tuple
    data_cols: tuple
    body_line: int


def classify_row_hier(band):
    """Chain the stages into a RowHierRegion (or None -> escalate). Mirror of
    hierarchical.classify_hierarchical."""
    from .cells import recover_leaf_grid
    from .rows import logical_rows
    grid = recover_leaf_grid(band)
    if grid.ncols < 2:
        return None
    split = header_body_split(band, grid)
    if split is None:
        return None
    k = stub_data_split(band, grid)
    if k is None:
        return None
    leaf_rows = logical_rows(band, grid, band.lines[split].top)
    if not leaf_rows:
        return None
    stub_cols = tuple(range(k))
    data_cols = tuple(range(k, grid.ncols))
    tree = infer_row_header_tree(band, grid, stub_cols, leaf_rows)
    if tree is None:
        return None
    return RowHierRegion(grid, tree, tuple(leaf_rows), stub_cols, data_cols, split)
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_rowheaders.py -q`
Expected: PASS (all Task 1 + Task 2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/rowheaders.py tests/etkl/test_rowheaders.py
git commit -m "feat(etkl): row-header tree (blank-below runs) + row_tree_tiles + classify_row_hier"
```

---

### Task 3: ontology `tab:coversRow` + four guarded row SHACL shapes + examples

**Files:**
- Modify: `vocab/ontology/tab.ttl`
- Modify: `vocab/shapes/tab-shapes.ttl`
- Create: `examples/tables/row-hierarchy-conformant.ttl`, `examples/tables/row-hierarchy-negative.ttl`
- Test: `tests/test_tab.py`

**Interfaces:**
- Produces: `tab:coversRow` (HeaderNode → LeafRow); `tab:RowCoverageShape`, `tab:RowNoOverlapShape`, `tab:RowRefinementShape`, `tab:UnambiguousRowAccessShape`.

**CRITICAL (no-regression):** `RowCoverageShape` and `UnambiguousRowAccessShape` MUST be guarded with `FILTER EXISTS { ?tbl tab:hasHeaderNode ?any . ?any tab:coversRow ?anyrow }` so they fire ONLY for tables that have a row axis — otherwise every existing flat/column example (leaf rows with no row-headers) fails. `RowNoOverlapShape`/`RowRefinementShape` need no guard (they only match when `coversRow` triples exist).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
ROW_CONFORMANT = os.path.join(EX, "row-hierarchy-conformant.ttl")
ROW_NEGATIVE = os.path.join(EX, "row-hierarchy-negative.ttl")


def test_tab_coversrow_term():
    g = _g(TAB_TTL)
    assert (TAB.coversRow, RDF.type, OWL.ObjectProperty) in g
    assert (TAB.coversRow, RDFS.domain, TAB.HeaderNode) in g
    assert (TAB.coversRow, RDFS.range, TAB.LeafRow) in g


def test_row_hierarchy_conformant_passes():
    c, t = _v(ROW_CONFORMANT)
    assert c, t


def test_row_hierarchy_negative_fails():
    c, t = _v(ROW_NEGATIVE)
    assert not c


def test_existing_column_examples_still_pass_with_row_shapes():
    # the guarded row shapes must NOT break a table that has leaf rows but no row axis
    c, t = _v(CONFORMANT)
    assert c, t
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py -q -k "coversrow or row_hierarchy"`
Expected: FAIL (term missing / example files absent).

- [ ] **Step 3: Add `tab:coversRow` to the ontology**

In `vocab/ontology/tab.ttl`, immediately after the `tab:coversColumn` declaration, add:

```turtle
tab:coversRow a owl:ObjectProperty ; rdfs:label "covers row"@en ;
    rdfs:domain tab:HeaderNode ; rdfs:range tab:LeafRow ;
    rdfs:comment "A leaf row in this header node's (vertical) span — the row-axis mirror of tab:coversColumn."@en .
```

- [ ] **Step 4: Add the four guarded row shapes**

Append to `vocab/shapes/tab-shapes.ttl`:

```turtle
#################################################################
#  Row-axis mirror of the column tiling invariants. Coverage and
#  UnambiguousRowAccess are GUARDED to fire only for tables that
#  have a row axis (>=1 coversRow), so flat/column-only tables
#  (leaf rows, no row-headers) still pass.
#################################################################

tab:RowCoverageShape a sh:NodeShape ;
    sh:targetClass tab:LeafRow ;
    sh:sparql [
        sh:message "Leaf row is not covered by any row-header of its table (row coverage gap)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                ?tbl tab:hasLeafRow $this .
                FILTER EXISTS { ?tbl tab:hasHeaderNode ?any . ?any tab:coversRow ?anyrow }
                FILTER NOT EXISTS { ?tbl tab:hasHeaderNode ?h . ?h tab:coversRow $this }
            }
        """ ] .

tab:RowNoOverlapShape a sh:NodeShape ;
    sh:targetSubjectsOf tab:hasHeaderNode ;
    sh:sparql [
        sh:message "Two header nodes at the same level cover the same row (row overlap)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:hasHeaderNode ?h1 .
                $this tab:hasHeaderNode ?h2 .
                FILTER(str(?h1) < str(?h2))
                ?h1 tab:headerLevel ?l .
                ?h2 tab:headerLevel ?l .
                ?h1 tab:coversRow ?r .
                ?h2 tab:coversRow ?r .
            }
        """ ] .

tab:RowRefinementShape a sh:NodeShape ;
    sh:targetClass tab:HeaderNode ;
    sh:sparql [
        sh:message "A header node covers a row its parent does not (row refinement break)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:parentHeader ?p .
                $this tab:coversRow ?r .
                FILTER NOT EXISTS { ?p tab:coversRow ?r }
            }
        """ ] .

tab:UnambiguousRowAccessShape a sh:NodeShape ;
    sh:targetClass tab:LeafRow ;
    sh:sparql [
        sh:message "Leaf row does not have exactly one leaf-header of its table (ambiguous row path)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                ?tbl tab:hasLeafRow $this .
                FILTER EXISTS { ?tbl tab:hasHeaderNode ?any . ?any tab:coversRow ?anyrow }
                {
                    SELECT ?tbl $this (COUNT(DISTINCT ?h) AS ?n) WHERE {
                        ?tbl tab:hasLeafRow $this .
                        OPTIONAL {
                            ?tbl tab:hasHeaderNode ?h .
                            ?h tab:coversRow $this .
                            FILTER NOT EXISTS { ?child tab:parentHeader ?h }
                        }
                    } GROUP BY ?tbl $this
                }
                FILTER(?n != 1)
            }
        """ ] .
```

- [ ] **Step 5: Create the conformant example**

Create `examples/tables/row-hierarchy-conformant.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .

# Region groups (North/South) over a fully-populated Metric leaf level; Value is the
# sole data leaf column. Row headers use coversRow; the flat column header uses coversColumn.
ex:rtbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:cVal ;
    tab:hasLeafRow ex:r0, ex:r1, ex:r2, ex:r3, ex:r4 ;
    tab:hasHeaderNode ex:hVal, ex:hNorth, ex:hSouth,
                      ex:mRev0, ex:mCost1, ex:mMar2, ex:mRev3, ex:mCost4 ;
    tab:hasCell ex:e0, ex:e1, ex:e2, ex:e3, ex:e4 .

ex:cVal a tab:LeafColumn .
ex:r0 a tab:LeafRow . ex:r1 a tab:LeafRow . ex:r2 a tab:LeafRow .
ex:r3 a tab:LeafRow . ex:r4 a tab:LeafRow .

# flat column header over the single data column
ex:hVal a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:cVal .

# row-header tree, level 0 (groups) — tiles r0..r4, no overlap
ex:hNorth a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversRow ex:r0, ex:r1, ex:r2 .
ex:hSouth a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversRow ex:r3, ex:r4 .

# row-header tree, level 1 (leaves) — each covers one row, refines its parent
ex:mRev0  a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hNorth ; tab:coversRow ex:r0 .
ex:mCost1 a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hNorth ; tab:coversRow ex:r1 .
ex:mMar2  a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hNorth ; tab:coversRow ex:r2 .
ex:mRev3  a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hSouth ; tab:coversRow ex:r3 .
ex:mCost4 a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hSouth ; tab:coversRow ex:r4 .

# entries: Value x r0..r4
ex:e0 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r0 .
ex:e1 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r1 .
ex:e2 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r2 .
ex:e3 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r3 .
ex:e4 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r4 .
```

- [ ] **Step 6: Create the negative example**

Create `examples/tables/row-hierarchy-negative.ttl` (leaf row `r0` covered by TWO leaf row-headers → fails `UnambiguousRowAccessShape`):

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .

ex:ntbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:cVal ;
    tab:hasLeafRow ex:r0, ex:r1 ;
    tab:hasHeaderNode ex:hVal, ex:mA, ex:mDup, ex:mB ;
    tab:hasCell ex:e0, ex:e1 .

ex:cVal a tab:LeafColumn .
ex:r0 a tab:LeafRow . ex:r1 a tab:LeafRow .
ex:hVal a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:cVal .

# r0 is covered by TWO leaf row-headers (mA, mDup) -> ambiguous row path
ex:mA   a tab:HeaderNode ; tab:headerLevel 1 ; tab:coversRow ex:r0 .
ex:mDup a tab:HeaderNode ; tab:headerLevel 1 ; tab:coversRow ex:r0 .
ex:mB   a tab:HeaderNode ; tab:headerLevel 1 ; tab:coversRow ex:r1 .

ex:e0 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r0 .
ex:e1 a tab:EntryCell ; tab:atColumn ex:cVal ; tab:atRow ex:r1 .
```

- [ ] **Step 7: Run tests + the full tab/shape/ownership suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/test_vocab_shapes.py tests/test_source_ownership.py -q`
Expected: PASS — new term + examples pass, the negative fails validation (asserted by `assert not c`), and every pre-existing tab example still passes (the guard works).

- [ ] **Step 8: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl examples/tables/row-hierarchy-conformant.ttl examples/tables/row-hierarchy-negative.ttl tests/test_tab.py
git commit -m "feat(tab): tab:coversRow + four guarded row-axis SHACL shapes + examples"
```

---

### Task 4: `assert_row_hier_region` maker

**Files:**
- Modify: `src/iladub/etkl/cells.py` (add `SourceCell.bbox` property)
- Modify: `src/iladub/etkl/holon.py`
- Test: `tests/etkl/test_holon.py`

**Interfaces:**
- Consumes: `_emit_entry_cell`, `_emit_roundtrip_fail_cell`, `_bbox_node`, `_region_uri` (holon.py); `regions.column_of`; a `RowHierRegion` (Task 2).
- Produces:
  - `SourceCell.bbox` property → `(x0, top, x1, bottom)` (so the shared emitters work for SourceCells).
  - `assert_row_hier_region(g, rreg, band, table_uri, doc_uri, page) -> int` — emits a `tab:HierarchicalTable` with a row-header tree; returns the asserted entry count.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_holon.py`:

```python
def test_row_hier_maker_builds_row_tree(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.rowheaders import classify_row_hier
    from iladub.etkl.holon import assert_row_hier_region, TAB
    from rdflib import Graph, URIRef, RDF, Literal

    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    rreg = classify_row_hier(band)
    g = Graph(); t = URIRef("https://example.org/t")
    n = assert_row_hier_region(g, rreg, band, t, URIRef("https://example.org/doc"), 0)

    assert (t, RDF.type, TAB.HierarchicalTable) in g
    assert len(list(g.objects(t, TAB.hasLeafColumn))) == 1          # Value only (Design A)
    assert len(list(g.objects(t, TAB.hasLeafRow))) == 5
    assert n == 5                                                   # 5 entries (Value x 5 rows)
    # row-header tree: North covers 3 rows, South covers 2
    def covers(text):
        h = next(s for s in g.subjects(RDF.type, TAB.HeaderNode)
                 if (s, TAB.hasLabel, None) in g
                 and str(next(g.objects(next(g.objects(s, TAB.hasLabel)), TAB.cellText))) == text)
        return len(list(g.objects(h, TAB.coversRow)))
    assert covers("North") == 3
    assert covers("South") == 2


def test_row_hier_provenance_is_physical(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.rowheaders import classify_row_hier
    from iladub.etkl.holon import assert_row_hier_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    words = extract_words(str(p))
    north = next(w for w in words if w.text == "North")
    band = detect_bands(text_lines(words))[-1]
    rreg = classify_row_hier(band)
    g = Graph(); t = URIRef("https://example.org/t")
    assert_row_hier_region(g, rreg, band, t, URIRef("https://example.org/doc"), 0)
    # the 'North' row-header LabelCell keeps the physical bbox of the 'North' word
    lc = next(s for s in g.subjects(RDF.type, TAB.LabelCell)
              if str(next(g.objects(s, TAB.cellText))) == "North")
    bb = next(g.objects(lc, TAB.hasBBox))
    assert abs(float(next(g.objects(bb, TAB.x0))) - north.x0) < 0.01
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py -q -k row_hier`
Expected: FAIL (ImportError on `assert_row_hier_region`).

- [ ] **Step 3: Add `SourceCell.bbox`**

In `src/iladub/etkl/cells.py`, add to the `SourceCell` dataclass (beside the `n_lines` property):

```python
    @property
    def bbox(self) -> tuple[float, float, float, float]:
        return (self.x0, self.top, self.x1, self.bottom)
```

- [ ] **Step 4: Implement `assert_row_hier_region`**

Append to `src/iladub/etkl/holon.py`:

```python
def assert_row_hier_region(g: Graph, rreg, band, table_uri: URIRef,
                           doc_uri: URIRef, page: int) -> int:
    """Emit a tab:HierarchicalTable with a ROW-header tree (Design A: stub columns are
    the row-header axis; only data columns are leaf columns). Returns the asserted
    entry count. Reuses the shared entry/round-trip emitters; row-header LabelCells and
    entries both carry physical provenance.
    """
    from .regions import column_of
    g.add((table_uri, RDF.type, TAB.HierarchicalTable))
    b = rreg.grid.boundaries

    # header line labels, by column (flat single-level column header assumed)
    header_by_col: dict[int, str] = {}
    if band.lines:
        for w in band.lines[0].words:
            header_by_col[column_of((w.x0 + w.x1) / 2.0, b)] = w.text

    # data leaf columns + flat column header nodes
    col_uris = {}
    for c in rreg.data_cols:
        cu = _region_uri(table_uri, "c", c)
        col_uris[c] = cu
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, cu))
        h = _region_uri(table_uri, "ch", c)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, cu))
        g.add((table_uri, TAB.hasHeaderNode, h))
        if c in header_by_col:
            lc = _region_uri(table_uri, "clc", c)
            g.add((lc, RDF.type, TAB.LabelCell))
            g.add((table_uri, TAB.hasCell, lc))
            g.add((lc, TAB.cellText, Literal(header_by_col[c])))
            g.add((h, TAB.hasLabel, lc))

    # leaf rows
    row_uris = {}
    for i in range(len(rreg.leaf_rows)):
        ru = _region_uri(table_uri, "r", i)
        row_uris[i] = ru
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, ru))

    # row-header tree (coversRow + parentHeader + LabelCell with physical provenance)
    node_uris = {}
    for idx, nd in enumerate(rreg.tree):
        h = _region_uri(table_uri, "rh", idx)
        node_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for rr in nd.covers_rows:
            g.add((h, TAB.coversRow, row_uris[rr]))
        lc = _region_uri(table_uri, "rlc", idx)
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(nd.text)))
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((bb, TAB.x0, Literal(round(nd.x0, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y0, Literal(round(nd.top, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.x1, Literal(round(nd.x1, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y1, Literal(round(nd.bottom, 2), datatype=XSD.decimal)))
        g.add((lc, TAB.hasBBox, bb))
        g.add((h, TAB.hasLabel, lc))
    for idx, nd in enumerate(rreg.tree):
        if nd.parent is not None:
            g.add((node_uris[idx], TAB.parentHeader, node_uris[nd.parent]))

    # entries: (data column x leaf row), certified per-cell by the round-trip
    asserted = 0
    for i, rb in enumerate(rreg.leaf_rows):
        by_col = {column_of((c.x0 + c.x1) / 2.0, b): c for c in rb.cells}
        for c in rreg.data_cols:
            cell = by_col.get(c)
            if cell is None:
                continue
            fits = all(b[c] - 0.5 <= w.x0 and w.x1 <= b[c + 1] + 0.5 for w in cell.words)
            if fits:
                e = _region_uri(table_uri, f"e{i}_", c)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, col_uris[c], row_uris[i], cell)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{i}_", c)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
    return asserted
```

Ensure `BNode` and `XSD` are already imported at the top of `holon.py` (they are).

- [ ] **Step 5: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py tests/etkl/test_cells.py -q`
Expected: PASS (row-hier structure + provenance; `SourceCell.bbox` doesn't break cell tests).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/cells.py src/iladub/etkl/holon.py tests/etkl/test_holon.py
git commit -m "feat(etkl): assert_row_hier_region (row-header tree holon) + SourceCell.bbox"
```

---

### Task 5: wire the compile gate + exports + closing/regression tests

**Files:**
- Modify: `src/iladub/etkl/compile.py` (insert the `elif looks_row_grouped` branch)
- Modify: `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_closing_slice.py`

**Interfaces:**
- Consumes: `rowheaders.looks_row_grouped`, `rowheaders.classify_row_hier`, `rowheaders.row_tree_tiles`, `holon.assert_row_hier_region`.
- Produces: `compile_tables` compiles a coherent row-grouped table to a `tab:HierarchicalTable`, escalates `ROW_GROUP_AMBIGUOUS` when the tree does not tile.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_closing_slice.py`:

```python
def test_row_grouped_compiles(tmp_path):
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    tbl = next(report.graph.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(report.graph.objects(tbl, TAB.hasLeafColumn))) == 1   # Value (Design A)
    assert len(list(report.graph.objects(tbl, TAB.hasLeafRow))) == 5
    # a row-header tree exists (coversRow), and it's not the flat-record flattening
    assert (None, TAB.coversRow, None) in report.graph
    assert report.score == 1.0


def test_row_grouped_not_a_flat_record(tmp_path):
    # the closing point: it must NOT compile as a flat RecordTable
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) not in report.graph
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_closing_slice.py -q -k row_grouped`
Expected: FAIL — currently compiles to `RecordTable` (flattened), so `HierarchicalTable`/`coversRow` absent.

- [ ] **Step 3: Insert the gate in `compile.py`**

In `src/iladub/etkl/compile.py`, the `RECORD_TABLE` branch currently ends with `else:` (the upright record assert). Change that final `else:` into `elif looks_row_grouped(region):` + the row-hier logic, then keep the upright assert as a NEW trailing `else:` — VERBATIM unchanged. Concretely, replace the line `            else:` that opens the "existing RECORD_TABLE assert logic, unchanged" block with:

```python
            elif looks_row_grouped(region):
                from .rowheaders import classify_row_hier, row_tree_tiles
                from .holon import assert_row_hier_region
                rreg = classify_row_hier(band)
                if rreg is not None and row_tree_tiles(rreg.tree, len(rreg.leaf_rows)):
                    table_uri = URIRef(f"{_DOC}#rhtable{idx}")
                    n = assert_row_hier_region(graph, rreg, band, table_uri, _DOC, page_number)
                    b = rreg.grid.boundaries
                    value_words = sum(len(c.words) for rb in rreg.leaf_rows for c in rb.cells
                                      if column_of((c.x0 + c.x1) / 2.0, b) in rreg.data_cols)
                    asserted_total += value_words           # entries all round-trip in the tiling case
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view))
                else:
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "ROW_GROUP_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "ROW_GROUP_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing RECORD_TABLE assert logic, unchanged ----
                ... (leave every line below here exactly as-is) ...
```

Add the imports needed at the top of the branch: change the existing `from .orientation import looks_transposed, transpose_is_coherent` line to also pull row grouping — add `from .rowheaders import looks_row_grouped` beside it (or import inside the branch as the transposed code does). Add `from .regions import column_of` at module top if not present (it is used by the score line).

For an entry that does NOT round-trip in the tiling case, `assert_row_hier_region` already escalates it per-cell; the score line above counts all value words as asserted. To keep the score exact when a straddle occurs, compute `asserted_total`/`escalated_total` from the per-cell fit instead:

```python
                    b = rreg.grid.boundaries
                    for rb in rreg.leaf_rows:
                        for c in rb.cells:
                            col = column_of((c.x0 + c.x1) / 2.0, b)
                            if col in rreg.data_cols:
                                fits = all(b[col] - 0.5 <= w.x0 and w.x1 <= b[col + 1] + 0.5 for w in c.words)
                                (asserted_total, escalated_total) = (
                                    (asserted_total + len(c.words), escalated_total) if fits
                                    else (asserted_total, escalated_total + len(c.words)))
```

Use this per-cell accounting (replacing the single `value_words` line) so the score mirrors the record path exactly.

- [ ] **Step 4: Update `__init__.py` exports**

In `src/iladub/etkl/__init__.py`, add:
`from .rowheaders import looks_row_grouped, classify_row_hier, row_tree_tiles, RowHierRegion, RowHeaderNode`
and `from .holon import assert_row_hier_region`; append their names to `__all__`.

- [ ] **Step 5: Run the closing tests + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — `test_row_grouped_compiles`, `test_row_grouped_not_a_flat_record`, all regressions, and the SHACL validation inside `compile_tables` (which now includes the row shapes) conforms on the emitted holon.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): compile row-header hierarchies (gate) — HierarchicalTable with coversRow, else escalate"
```

---

### Task 6: showcase Part F + canvas increment 5

**Files:**
- Modify: `demo/etkl_demo_data.py` (add `row_grouped_report_pdf`)
- Modify: `demo/etkl_1a_showcase.ipynb` (Part F)
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (increment 5)

**Interfaces:** Consumes the shipped `compile_tables` behaviour. No new code.

- [ ] **Step 1: Add the demo fixture**

Append `row_grouped_report_pdf(path)` to `demo/etkl_demo_data.py`, mirroring `tests/etkl/fixtures.py::row_grouped_table_pdf` but richer (a title band above + 2 data columns is fine as long as it stays one band and both data columns are numeric). Keep it a clean row-grouped table: a grouped `Region` stub, a fully-populated `Department` stub, and a numeric `Headcount` (+ optionally `Budget`) data column. Return a truth dict. Verify empirically it compiles (Step 3 will confirm).

- [ ] **Step 2: Insert Part F cells**

After the Part E cells and before the closing "ladder" markdown, insert three cells:
1. **Markdown intro** — "Part F · the vertical mirror — a *row*-header hierarchy", explaining blank-below = ditto-grouping is the row-axis mirror of Part C's merged column header, and that stub columns become the row-header axis (Design A).
2. **Code (render original first)** — write the row-grouped PDF via `data.row_grouped_report_pdf`, render it with `viz.render_page`/`viz.show_page` (original document first, always).
3. **Code (compile read-out)** — `compile_tables`, then print the recovered row-header tree and one addressed entry:

```python
from iladub.etkl.holon import TAB
from rdflib import RDF
rh = compile_tables(rg_pdf)
tbl = next(rh.graph.subjects(RDF.type, TAB.HierarchicalTable))
groups = []
for h in rh.graph.subjects(RDF.type, TAB.HeaderNode):
    rows = list(rh.graph.objects(h, TAB.coversRow))
    lbl = rh.graph.value(rh.graph.value(h, TAB.hasLabel), TAB.cellText)
    if len(rows) > 1 and lbl is not None:
        groups.append((str(lbl), len(rows)))
print(f"score = {rh.score:.2f}   |   HierarchicalTable   |   leaf columns:",
      len(list(rh.graph.objects(tbl, TAB.hasLeafColumn))))
print("row-header groups:", ", ".join(f"{g}->{n} rows" for g, n in sorted(groups)))
print("leaf rows:", len(list(rh.graph.objects(tbl, TAB.hasLeafRow))),
      "| entry cells:", len(list(rh.graph.subjects(RDF.type, TAB.EntryCell))))
```

Then update the closing "ladder" markdown to mention the row hierarchy as the vertical mirror of the column pivot, and refresh the "next rungs" to matrix/cross-tab (both axes).

- [ ] **Step 3: Re-run the notebook; verify zero errors**

Run:
```bash
PYTHONPATH="$PWD/src:$PWD/demo" jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 --ExecutePreprocessor.kernel_name=python3 \
  demo/etkl_1a_showcase.ipynb
```
Verify (JSON scan of outputs, as in Loop 4): 0 errors, Part F renders the row-grouped PDF, and prints `HierarchicalTable` with `North->3 rows, South->2 rows` (or the demo's groups) and the leaf-column/row counts.

- [ ] **Step 4: Canvas increment 5**

In `docs/loops/2026-07-05-table-holon-loop.md`, add increment 5 (`[x]`) describing the row-header hierarchy compile (vertical mirror of Loop 2; `tab:coversRow`; blank-below convention; row SHACL), and remove "row-header hierarchies (…needs `tab:coversRow`…)" from the field-of-possibles bullet, leaving matrix/cross-tab et al.

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_demo_data.py demo/etkl_1a_showcase.ipynb docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop5): showcase Part F (row-header hierarchy) + canvas increment 5"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §4.1 `stub_data_split` + §4.2 `looks_row_grouped` → Task 1; §5 tree/`row_tree_tiles`/`classify_row_hier` → Task 2; §7 `coversRow` + guarded row shapes + examples → Task 3; §6 `assert_row_hier_region` (+ `SourceCell.bbox`) → Task 4; §4 gate + §2 closing proof → Task 5; §9 showcase + §canvas → Task 6. §8 tests distributed across the tasks that own them.
- **Type consistency:** `RowHierRegion`/`RowHeaderNode` fields and `assert_row_hier_region(g, rreg, band, table_uri, doc_uri, page) -> int` used identically across Tasks 2/4/5; `looks_row_grouped(region)`, `classify_row_hier(band)`, `row_tree_tiles(tree, n)` signatures stable.
- **No-regression guardrails made explicit:** Task 3 Step 4 guards the two row shapes with `FILTER EXISTS { … coversRow … }`, and Task 3 Step 7 + Task 5 Step 5 re-run the full existing suite. The flat-record `else` in `compile.py` is preserved VERBATIM (Task 5 Step 3).
- **Placeholder scan:** none — every code step carries the exact content. (Task 6 Step 1 describes the demo fixture in prose because it mirrors the Task 1 fixture and is verified by the re-run; the compile-readout cell is given verbatim.)
- **Empirical grounding:** the fixture geometry and classification path are confirmed by the 2026-07-09 probe recorded in Global Constraints.
