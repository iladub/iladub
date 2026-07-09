# Matrix / Cross-Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a cross-tab (hierarchical column header + stub row axis, numeric data matrix) into a `tab:HierarchicalTable` with BOTH a column tree (`coversColumn`) and a row tree (`coversRow`), entries at (data-col × leaf-row), instead of losing the row axis.

**Architecture:** Compose Loop 2's column machinery + Loop 5's row machinery. The only new algorithm is a **proximity (Voronoi) column-span builder** — Loop 2's text-extent `infer_header_tree` under-covers short cross-tab labels (`Q1` over a wide group), so we assign each data column to its nearest parent-label center. No new ontology or SHACL: the union of the existing column + row tiling shapes certifies the holon.

**Tech Stack:** Python 3, rdflib, pdfplumber/reportlab (fixtures), pyshacl, pytest.

## Global Constraints

- **No new vocab/SHACL:** `tab:coversColumn`/`coversRow` and both shape sets already exist (Loops 2 + 5). Do NOT add ontology terms or shapes.
- **No silent-wrong:** a mis-inferred tree escalates `MATRIX_AMBIGUOUS` (the pre-check `matrix_tiles` guards against `_validate` raising); a straddling entry escalates `ROUND_TRIP_FAIL`. The existing Loop 2 `classify_hierarchical` path in the `UNSUPPORTED_TABLE` branch stays byte-for-byte unchanged (wrapped in a new `else`).
- **No overfitting:** proximity assignment is structural (nearest parent-label center). It assumes CENTERED parent merges (a documented convention, the mirror of Loop 2's centered-merge and Loop 5's blank-below); left/right-aligned parents are out of scope. `col_tree_tiles` is a structural backstop, not a semantic discriminator (Voronoi always partitions).
- **Provenance-to-the-page:** entries AND both axes' LabelCells carry physical bbox/onPage. (This gives the column-header LabelCells provenance that Loop 2's `assert_hier_region` omits — a step forward, via geometry-carrying nodes.)
- **Design A (settled):** stub columns are the row axis; only data columns are leaf columns. Detection separates matrix from Loop 2 (covered stub / `stub_data_split` None) and Loop 5 (flat column header / RECORD_TABLE).
- **Reuse:** `headers.header_body_split`, `rowheaders.stub_data_split`/`infer_row_header_tree`/`row_tree_tiles`, `rows.logical_rows`, `cells.recover_leaf_grid`, `regions.column_of`, and holon's `_emit_entry_cell`/`_emit_roundtrip_fail_cell`/`_region_uri`. Do NOT reimplement.

**Confirmed by empirical probe (2026-07-09):** a `crosstab` fixture (stub `North`/`South` + `Q1`/`Q2` each over `Rev`/`Cost`/`Unit`, numeric body) classifies UNSUPPORTED with ncols=7, `header_body_split`=2, `stub_data_split`=1, stub col 0 uncovered; proximity recovers `Q1→{1,2,3}`, `Q2→{4,5,6}`, leaves one-each; the row tree is `North→(0,)`, `South→(1,)` and tiles. Loop 2's pivot has `stub_data_split` None (stub covered) → never enters this path.

---

### Task 1: `matrix.py` — proximity column-span builder + detection

**Files:**
- Create: `src/iladub/etkl/matrix.py`
- Modify: `tests/etkl/fixtures.py` (append `crosstab_table_pdf`)
- Test: `tests/etkl/test_matrix.py` (create)

**Interfaces:**
- Consumes: `cells.recover_leaf_grid`, `headers.header_body_split`, `rowheaders.stub_data_split`, `regions.column_of`, `grid.LeafGrid`.
- Produces:
  - `ColHeaderNode(level, covers, text, parent, x0, top, x1, bottom, page)` (frozen dataclass; `covers` = tuple of data-column indices).
  - `infer_column_tree_by_proximity(band, grid, split, data_cols) -> tuple[ColHeaderNode, ...] | None`.
  - `col_tree_tiles(tree, data_cols) -> bool`.
  - `is_matrix_candidate(band) -> bool`.

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_matrix.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import crosstab_table_pdf, pivoted_table_pdf, simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl.matrix import (infer_column_tree_by_proximity, col_tree_tiles,
                                is_matrix_candidate, ColHeaderNode)


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_proximity_column_tree(tmp_path):
    band = _band(crosstab_table_pdf, tmp_path)
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    data_cols = tuple(range(1, grid.ncols))              # col 0 is the stub
    tree = infer_column_tree_by_proximity(band, grid, split, data_cols)
    l0 = {n.text: n.covers for n in tree if n.level == 0}
    assert l0["Q1"] == (1, 2, 3)                          # short label, wide span — proximity recovers it
    assert l0["Q2"] == (4, 5, 6)
    leaves = [n for n in tree if n.level == 1]
    assert len(leaves) == 6 and all(len(n.covers) == 1 for n in leaves)
    assert col_tree_tiles(tree, data_cols) is True


def test_col_tree_tiles_rejects_pathology():
    def node(level, covers, parent):
        return ColHeaderNode(level, covers, "x", parent, 0.0, 0.0, 1.0, 1.0, 0)
    gap = (node(0, (1,), None), node(0, (2,), None))       # data_cols {1,2,3}, col 3 uncovered
    assert col_tree_tiles(gap, (1, 2, 3)) is False
    overlap = (node(0, (1,), None), node(0, (1, 2), None))
    assert col_tree_tiles(overlap, (1, 2)) is False


def test_is_matrix_candidate(tmp_path):
    assert is_matrix_candidate(_band(crosstab_table_pdf, tmp_path)) is True
    # Loop 2 pivot: stub_data_split is None (mixed data cols) -> not a matrix
    assert is_matrix_candidate(_band(pivoted_table_pdf, tmp_path)) is False
    # flat single-level table: header_body_split 1 -> not a matrix
    assert is_matrix_candidate(_band(simple_table_pdf, tmp_path)) is False
```

- [ ] **Step 2: Add the fixture**

Append to `tests/etkl/fixtures.py` (geometry probe-verified to stay one band, classify UNSUPPORTED, and tile):

```python
def crosstab_table_pdf(path: str) -> dict:
    """A cross-tab: hierarchical COLUMN header (Q1/Q2 each over Rev/Cost/Unit) + a
    flat stub ROW axis (North/South) + a numeric data matrix. Short column-group
    labels over wide numeric groups — the case Loop 2's text-extent span recovery
    under-covers and proximity handles. Blank corner (the stub has no header)."""
    stub_x = 55.0
    data_x = [140.0, 210.0, 280.0, 380.0, 450.0, 520.0]   # Q1:Rev,Cost,Unit | Q2:Rev,Cost,Unit
    top = PAGE_H - 90.0
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 9)
    c.drawCentredString((data_x[0] + data_x[2]) / 2.0, top, "Q1")
    c.drawCentredString((data_x[3] + data_x[5]) / 2.0, top, "Q2")
    for x, name in zip(data_x, ["Rev", "Cost", "Unit", "Rev", "Cost", "Unit"]):
        c.drawCentredString(x, top - 13.0, name)
    c.setFont("Courier", 9)
    body = [("North", ["100", "60", "5", "110", "65", "6"]),
            ("South", ["120", "70", "7", "130", "75", "8"])]
    for i, (lbl, vals) in enumerate(body):
        y = top - 30.0 - i * 16.0
        c.drawString(stub_x, y, lbl)
        for x, v in zip(data_x, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"n_data_cols": 6, "n_leaf_rows": 2,
            "col_groups": {"Q1": [1, 2, 3], "Q2": [4, 5, 6]},
            "row_axis": ["North", "South"]}
```

- [ ] **Step 3: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_matrix.py -q`
Expected: FAIL (ImportError on `infer_column_tree_by_proximity`).

- [ ] **Step 4: Implement the module core**

Create `src/iladub/etkl/matrix.py`:

```python
"""matrix — compile a cross-tab (hierarchical columns + stub row axis) by composing
Loop 2's column machinery and Loop 5's row machinery.

The one non-composed piece: infer_header_tree recovers merged spans from a parent
label's TEXT EXTENT, which under-covers short cross-tab labels (Q1 over a wide
numeric group). infer_column_tree_by_proximity instead assigns each data leaf column
to its NEAREST parent-label center (Voronoi) — exact for any label width. This
assumes CENTERED parent merges (a documented convention, the mirror of Loop 2's
centered-merge and Loop 5's blank-below); the SHACL + round-trip certify the result.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .bands import Band
from .cells import recover_leaf_grid
from .grid import LeafGrid
from .headers import header_body_split
from .rowheaders import stub_data_split


@dataclass(frozen=True)
class ColHeaderNode:
    level: int
    covers: tuple[int, ...]        # data leaf-column indices
    text: str
    parent: int | None
    x0: float
    top: float
    x1: float
    bottom: float
    page: int


def _level_tops(band: Band, split: int) -> list[float]:
    return sorted({round(w.top, 1) for ln in band.lines[:split] for w in ln.words})


def infer_column_tree_by_proximity(band, grid, split, data_cols):
    """Column tree over the DATA columns by nearest-parent-center assignment.

    For each header level (top to bottom = 0..), take that line's labels as
    (text, x_center, word); assign each data column to the nearest label center; a
    node covers the contiguous run assigned to it. Parent links: level L -> the
    level-(L-1) node whose covers contain this node's. None if a level has no labels.
    """
    b = grid.boundaries
    centers = {c: (b[c] + b[c + 1]) / 2.0 for c in data_cols}
    tops = _level_tops(band, split)
    if not tops:
        return None
    nodes: list[ColHeaderNode] = []
    for level, t in enumerate(tops):
        labels = sorted(
            ((w.text, (w.x0 + w.x1) / 2.0, w)
             for ln in band.lines[:split] for w in ln.words if abs(round(w.top, 1) - t) < 0.5),
            key=lambda z: z[1])
        if not labels:
            return None
        assign: dict[int, list[int]] = {}
        for c in data_cols:
            k = min(range(len(labels)), key=lambda j: abs(labels[j][1] - centers[c]))
            assign.setdefault(k, []).append(c)
        for k, cols in assign.items():
            text, _, w = labels[k]
            nodes.append(ColHeaderNode(level, tuple(sorted(cols)), text, None,
                                       w.x0, w.top, w.x1, w.bottom, w.page))
    linked: list[ColHeaderNode] = []
    for nd in nodes:
        pidx = None
        for j, m in enumerate(nodes):
            if m.level == nd.level - 1 and set(nd.covers) <= set(m.covers):
                pidx = j
                break
        linked.append(replace(nd, parent=pidx))
    return tuple(linked)


def col_tree_tiles(tree, data_cols) -> bool:
    """Structural backstop: leaf-level column-headers (no children) partition
    data_cols exactly, and every child's covers ⊆ its parent's."""
    for nd in tree:
        if nd.parent is not None and not set(nd.covers) <= set(tree[nd.parent].covers):
            return False
    has_child = {nd.parent for nd in tree if nd.parent is not None}
    covered: list[int] = []
    for i, nd in enumerate(tree):
        if i not in has_child:
            covered.extend(nd.covers)
    return sorted(covered) == sorted(data_cols)


def is_matrix_candidate(band: Band) -> bool:
    """A matrix candidate: a multi-level column header (>=2 header lines) over a
    clean text-stub | numeric-data split. (The caller has already established the
    region is UNSUPPORTED_TABLE.)"""
    grid = recover_leaf_grid(band)
    if grid.ncols < 3:
        return False
    split = header_body_split(band, grid)
    return split is not None and split >= 2 and stub_data_split(band, grid) is not None
```

- [ ] **Step 5: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_matrix.py -q`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/matrix.py tests/etkl/fixtures.py tests/etkl/test_matrix.py
git commit -m "feat(etkl): matrix — proximity column-span builder + is_matrix_candidate"
```

---

### Task 2: `matrix.py` — `classify_matrix` + `matrix_tiles`

**Files:**
- Modify: `src/iladub/etkl/matrix.py`
- Test: `tests/etkl/test_matrix.py`

**Interfaces:**
- Consumes: Task 1's `infer_column_tree_by_proximity`, `col_tree_tiles`; `rows.logical_rows`, `rowheaders.infer_row_header_tree`, `rowheaders.row_tree_tiles`.
- Produces:
  - `MatrixRegion(grid, col_tree, row_tree, leaf_rows, stub_cols, data_cols, body_line)` (frozen dataclass).
  - `classify_matrix(band) -> MatrixRegion | None` (chains stages; mirror of `classify_row_hier`).
  - `matrix_tiles(mreg) -> bool` — both axes tile.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_matrix.py`:

```python
from iladub.etkl.matrix import classify_matrix, matrix_tiles, MatrixRegion


def test_classify_matrix_composes_both_axes(tmp_path):
    mreg = classify_matrix(_band(crosstab_table_pdf, tmp_path))
    assert mreg is not None
    assert mreg.stub_cols == (0,)
    assert mreg.data_cols == (1, 2, 3, 4, 5, 6)
    assert len(mreg.leaf_rows) == 2
    l0c = {n.text: n.covers for n in mreg.col_tree if n.level == 0}
    assert l0c["Q1"] == (1, 2, 3) and l0c["Q2"] == (4, 5, 6)
    row_texts = {n.text for n in mreg.row_tree}
    assert {"North", "South"} <= row_texts
    assert matrix_tiles(mreg) is True


def test_classify_matrix_none_on_flat_header(tmp_path):
    # simple_table has a single-level header (header_body_split 1) -> not a matrix
    assert classify_matrix(_band(simple_table_pdf, tmp_path)) is None


def test_classify_matrix_none_on_pivot(tmp_path):
    # Loop 2 pivot: stub_data_split None -> not a matrix
    assert classify_matrix(_band(pivoted_table_pdf, tmp_path)) is None
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_matrix.py -q -k classify_matrix`
Expected: FAIL (ImportError on `classify_matrix`).

- [ ] **Step 3: Implement**

Append to `src/iladub/etkl/matrix.py`:

```python
@dataclass(frozen=True)
class MatrixRegion:
    grid: LeafGrid
    col_tree: tuple[ColHeaderNode, ...]
    row_tree: tuple
    leaf_rows: tuple
    stub_cols: tuple[int, ...]
    data_cols: tuple[int, ...]
    body_line: int


def classify_matrix(band):
    """Chain the stages into a MatrixRegion (or None). Mirror of classify_row_hier,
    with a proximity column tree over the data columns as the extra axis."""
    from .rows import logical_rows
    from .rowheaders import infer_row_header_tree
    grid = recover_leaf_grid(band)
    if grid.ncols < 3:
        return None
    split = header_body_split(band, grid)
    if split is None or split < 2:
        return None
    k = stub_data_split(band, grid)
    if k is None:
        return None
    stub_cols = tuple(range(k))
    data_cols = tuple(range(k, grid.ncols))
    col_tree = infer_column_tree_by_proximity(band, grid, split, data_cols)
    if col_tree is None:
        return None
    leaf_rows = logical_rows(band, grid, band.lines[split].top)
    if not leaf_rows:
        return None
    row_tree = infer_row_header_tree(band, grid, stub_cols, leaf_rows)
    if row_tree is None:
        return None
    return MatrixRegion(grid, col_tree, tuple(row_tree), tuple(leaf_rows),
                        stub_cols, data_cols, split)


def matrix_tiles(mreg) -> bool:
    """Both axes tile: the column tree partitions the data columns AND the row tree
    partitions the leaf rows. Structural backstop before emission."""
    from .rowheaders import row_tree_tiles
    return (col_tree_tiles(mreg.col_tree, mreg.data_cols)
            and row_tree_tiles(mreg.row_tree, len(mreg.leaf_rows)))
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_matrix.py -q`
Expected: PASS (all Task 1 + Task 2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/matrix.py tests/etkl/test_matrix.py
git commit -m "feat(etkl): classify_matrix (compose column + row trees) + matrix_tiles"
```

---

### Task 3: `assert_matrix_region` maker

**Files:**
- Modify: `src/iladub/etkl/holon.py`
- Test: `tests/etkl/test_holon.py`

**Interfaces:**
- Consumes: `_emit_entry_cell`, `_emit_roundtrip_fail_cell`, `_region_uri`, `TAB/XSD/BNode` (holon.py); `regions.column_of`; a `MatrixRegion` (Task 2).
- Produces: `assert_matrix_region(g, mreg, band, table_uri, doc_uri, page) -> int` — emits a `tab:HierarchicalTable` with a column tree + a row tree + entries at (data-col × leaf-row); returns the asserted entry count.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_holon.py`:

```python
def test_matrix_maker_builds_both_axes(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.matrix import classify_matrix
    from iladub.etkl.holon import assert_matrix_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    mreg = classify_matrix(band)
    g = Graph(); t = URIRef("https://example.org/t")
    n = assert_matrix_region(g, mreg, band, t, URIRef("https://example.org/doc"), 0)

    assert (t, RDF.type, TAB.HierarchicalTable) in g
    assert len(list(g.objects(t, TAB.hasLeafColumn))) == 6      # data columns only (Design A)
    assert len(list(g.objects(t, TAB.hasLeafRow))) == 2
    assert n == 12                                              # 6 data cols x 2 rows
    assert (None, TAB.coversColumn, None) in g                  # column tree
    assert (None, TAB.coversRow, None) in g                     # row tree
    # a column-group header 'Q1' covers 3 leaf columns
    q1 = next(s for s in g.subjects(RDF.type, TAB.HeaderNode)
              if (s, TAB.hasLabel, None) in g
              and str(next(g.objects(next(g.objects(s, TAB.hasLabel)), TAB.cellText))) == "Q1")
    assert len(list(g.objects(q1, TAB.coversColumn))) == 3


def test_matrix_provenance_is_physical(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.matrix import classify_matrix
    from iladub.etkl.holon import assert_matrix_region, TAB
    from rdflib import Graph, URIRef, RDF

    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    words = extract_words(str(p))
    north = next(w for w in words if w.text == "North")
    band = detect_bands(text_lines(words))[-1]
    mreg = classify_matrix(band)
    g = Graph(); t = URIRef("https://example.org/t")
    assert_matrix_region(g, mreg, band, t, URIRef("https://example.org/doc"), 0)
    lc = next(s for s in g.subjects(RDF.type, TAB.LabelCell)
              if str(next(g.objects(s, TAB.cellText))) == "North")
    bb = next(g.objects(lc, TAB.hasBBox))
    assert abs(float(next(g.objects(bb, TAB.x0))) - north.x0) < 0.01
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py -q -k matrix`
Expected: FAIL (ImportError on `assert_matrix_region`).

- [ ] **Step 3: Implement**

Append to `src/iladub/etkl/holon.py`:

```python
def assert_matrix_region(g: Graph, mreg, band, table_uri: URIRef,
                         doc_uri: URIRef, page: int) -> int:
    """Emit a tab:HierarchicalTable for a cross-tab: a column tree (coversColumn) over
    the data leaf columns + a row tree (coversRow) over the leaf rows, entries at
    (data-col x leaf-row). Composes the Loop 2 column-header and Loop 5 row-header
    emission patterns; reuses the shared entry emitters. Both axes' LabelCells carry
    physical bbox/onPage. Returns the asserted entry count."""
    from .regions import column_of
    g.add((table_uri, RDF.type, TAB.HierarchicalTable))
    b = mreg.grid.boundaries

    def _label(uri_key, idx, text, x0, top, x1, bottom):
        lc = _region_uri(table_uri, uri_key, idx)
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(text)))
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((bb, TAB.x0, Literal(round(x0, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y0, Literal(round(top, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.x1, Literal(round(x1, 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y1, Literal(round(bottom, 2), datatype=XSD.decimal)))
        g.add((lc, TAB.hasBBox, bb))
        return lc

    # data leaf columns
    col_uris = {}
    for c in mreg.data_cols:
        cu = _region_uri(table_uri, "c", c)
        col_uris[c] = cu
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, cu))

    # column-header tree (coversColumn + parentHeader + LabelCell)
    cnode_uris = {}
    for idx, nd in enumerate(mreg.col_tree):
        h = _region_uri(table_uri, "ch", idx)
        cnode_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for c in nd.covers:
            g.add((h, TAB.coversColumn, col_uris[c]))
        g.add((h, TAB.hasLabel, _label("chl", idx, nd.text, nd.x0, nd.top, nd.x1, nd.bottom)))
    for idx, nd in enumerate(mreg.col_tree):
        if nd.parent is not None:
            g.add((cnode_uris[idx], TAB.parentHeader, cnode_uris[nd.parent]))

    # leaf rows
    row_uris = {}
    for i in range(len(mreg.leaf_rows)):
        ru = _region_uri(table_uri, "r", i)
        row_uris[i] = ru
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, ru))

    # row-header tree (coversRow + parentHeader + LabelCell)
    rnode_uris = {}
    for idx, nd in enumerate(mreg.row_tree):
        h = _region_uri(table_uri, "rh", idx)
        rnode_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(nd.level, datatype=XSD.integer)))
        for rr in nd.covers_rows:
            g.add((h, TAB.coversRow, row_uris[rr]))
        g.add((h, TAB.hasLabel, _label("rhl", idx, nd.text, nd.x0, nd.top, nd.x1, nd.bottom)))
    for idx, nd in enumerate(mreg.row_tree):
        if nd.parent is not None:
            g.add((rnode_uris[idx], TAB.parentHeader, rnode_uris[nd.parent]))

    # entries at (data column x leaf row)
    asserted = 0
    for i, rb in enumerate(mreg.leaf_rows):
        by_col = {column_of((sc.x0 + sc.x1) / 2.0, b): sc for sc in rb.cells}
        for c in mreg.data_cols:
            sc = by_col.get(c)
            if sc is None:
                continue
            # column-specific containment (NOT cell_round_trips, which checks full-table extent)
            fits = all(b[c] - 0.5 <= w.x0 and w.x1 <= b[c + 1] + 0.5 for w in sc.words)
            if fits:
                e = _region_uri(table_uri, f"e{i}_", c)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, col_uris[c], row_uris[i], sc)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{i}_", c)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, sc)
    return asserted
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py -q -k matrix`
Expected: PASS (structure + provenance).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/holon.py tests/etkl/test_holon.py
git commit -m "feat(etkl): assert_matrix_region — column tree + row tree + (col x row) entries"
```

---

### Task 4: wire the compile gate + exports + closing/regression tests

**Files:**
- Modify: `src/iladub/etkl/compile.py` (the `UNSUPPORTED_TABLE` branch)
- Modify: `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_closing_slice.py`

**Interfaces:**
- Consumes: `matrix.is_matrix_candidate`, `matrix.classify_matrix`, `matrix.matrix_tiles`, `holon.assert_matrix_region`.
- Produces: `compile_tables` compiles a cross-tab to a `tab:HierarchicalTable`; a non-matrix UNSUPPORTED table still goes to Loop 2's `classify_hierarchical` unchanged.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_closing_slice.py`:

```python
def test_crosstab_compiles(tmp_path):
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    tbl = next(report.graph.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(report.graph.objects(tbl, TAB.hasLeafColumn))) == 6   # data-only
    assert len(list(report.graph.objects(tbl, TAB.hasLeafRow))) == 2
    assert (None, TAB.coversColumn, None) in report.graph                 # column tree
    assert (None, TAB.coversRow, None) in report.graph                    # row tree
    assert report.score == 1.0


def test_pivot_still_column_hierarchy(tmp_path):
    # regression: Loop 2's pivot is NOT stolen by the matrix gate (stub_data_split None)
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    assert (None, TAB.coversRow, None) not in report.graph                # column-only, no row axis
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_closing_slice.py -q -k "crosstab or pivot_still"`
Expected: FAIL — `test_crosstab_compiles` currently produces no HierarchicalTable with `coversRow` (the matrix isn't wired; it hits Loop 2's path and loses the row axis).

- [ ] **Step 3: Wire the gate in `compile.py`**

In the `UNSUPPORTED_TABLE` branch (`else:  # UNSUPPORTED_TABLE — try the hierarchical maker first`), wrap the ENTIRE existing body in a new `else`, with the matrix gate as the leading `if`:

```python
        else:  # UNSUPPORTED_TABLE
            from .matrix import is_matrix_candidate
            if is_matrix_candidate(band):
                from .matrix import classify_matrix, matrix_tiles
                from .holon import assert_matrix_region
                mreg = classify_matrix(band)
                if mreg is not None and matrix_tiles(mreg):
                    table_uri = URIRef(f"{_DOC}#mtable{idx}")
                    n = assert_matrix_region(graph, mreg, band, table_uri, _DOC, page_number)
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
                # ---- existing Loop 2 hierarchical path, UNCHANGED ----
                from .hierarchical import classify_hierarchical
                ... (every line of the existing UNSUPPORTED body, verbatim) ...
```

Keep every line of the existing Loop 2 body (from `from .hierarchical import classify_hierarchical` through the final `reports.append(... "KIND_NOT_SUPPORTED" ...)`) byte-for-byte inside the new `else:`. `column_of` is already imported at module top (added in Loop 5).

- [ ] **Step 4: Update `__init__.py` exports**

Add: `from .matrix import (is_matrix_candidate, classify_matrix, matrix_tiles, infer_column_tree_by_proximity, col_tree_tiles, MatrixRegion, ColHeaderNode)` and `from .holon import assert_matrix_region`; append their names to `__all__`.

- [ ] **Step 5: Run the closing tests + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — `test_crosstab_compiles` (with live column+row SHACL conforming inside `compile_tables`), `test_pivot_still_column_hierarchy`, and every prior test (Loop 2/5 fixtures unchanged).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): compile matrix/cross-tab (gate) — HierarchicalTable with column + row trees"
```

---

### Task 5: showcase Part G + canvas increment 6

**Files:**
- Modify: `demo/etkl_demo_data.py` (add `crosstab_report_pdf`)
- Modify: `demo/etkl_1a_showcase.ipynb` (Part G)
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (increment 6)

**Interfaces:** Consumes the shipped `compile_tables` behaviour. No new code.

- [ ] **Step 1: Add the demo fixture**

Append `crosstab_report_pdf(path)` to `demo/etkl_demo_data.py`, mirroring `tests/etkl/fixtures.py::crosstab_table_pdf` (a titled cross-tab: hierarchical column header `Q1/Q2 × Rev/Cost/Unit` + flat stub `North/South` + numeric body). Keep it one band (tight header/body spacing). Return a truth dict. Verify empirically it compiles (Step 3 confirms).

- [ ] **Step 2: Insert Part G cells**

After Part F's cells and before the closing "ladder" markdown, insert three cells:
1. **Markdown intro** — "Part G · both axes at once — a matrix / cross-tab", explaining it composes Part C's column pivot and Part F's row hierarchy; a value is addressed by `(column-path × row-path)`; no new vocabulary — the union of the column and row shapes certifies it.
2. **Code (render original first)** — write the cross-tab PDF via `data.crosstab_report_pdf`, render with `viz.render_page`/`viz.show_page`.
3. **Code (compile read-out)** — `compile_tables`, then print the column tree, the row axis, and one doubly-addressed cell:

```python
from iladub.etkl.holon import TAB
from rdflib import RDF
mx = compile_tables(ct_pdf)
tbl = next(mx.graph.subjects(RDF.type, TAB.HierarchicalTable))
col_groups, row_axis = [], []
for h in mx.graph.subjects(RDF.type, TAB.HeaderNode):
    lbl = mx.graph.value(mx.graph.value(h, TAB.hasLabel), TAB.cellText)
    ncol = len(list(mx.graph.objects(h, TAB.coversColumn)))
    nrow = len(list(mx.graph.objects(h, TAB.coversRow)))
    if ncol > 1 and lbl is not None: col_groups.append((str(lbl), ncol))
    if nrow >= 1 and lbl is not None and ncol == 0: row_axis.append(str(lbl))
print(f"score = {mx.score:.2f}   |   HierarchicalTable (2-D matrix)")
print("column groups:", ", ".join(f"{g} over {n} cols" for g, n in sorted(col_groups)))
print("row axis:", ", ".join(sorted(set(row_axis))))
print("leaf columns:", len(list(mx.graph.objects(tbl, TAB.hasLeafColumn))),
      "| leaf rows:", len(list(mx.graph.objects(tbl, TAB.hasLeafRow))),
      "| entry cells:", len(list(mx.graph.subjects(RDF.type, TAB.EntryCell))))
print()
print("Both header axes are first-class: each value is addressed by (column-path x row-path).")
print("Part C (column pivot) and Part F (row hierarchy) compose — no new vocabulary needed.")
```

Then update the closing "ladder" markdown: the matrix is the culmination — column and row hierarchies composing into a 2-D access function; refresh the "next rungs" (e.g. key-value, stacked, multi-band, signal-tagging).

- [ ] **Step 3: Re-run the notebook; verify zero errors**

Run:
```bash
PYTHONPATH="$PWD/src:$PWD/demo" jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 --ExecutePreprocessor.kernel_name=python3 \
  demo/etkl_1a_showcase.ipynb
```
Verify (JSON scan): 0 errors, Part G renders the cross-tab PDF, and prints `HierarchicalTable (2-D matrix)` with the column groups (`Q1 over 3 cols`, `Q2 over 3 cols`) and row axis (`North, South`).

- [ ] **Step 4: Canvas increment 6**

In `docs/loops/2026-07-05-table-holon-loop.md`, add increment 6 (`[x]`) — matrix/cross-tab compiled by composing the column tree + row tree (`atColumn × atRow`), the proximity column-span builder, no new vocab/SHACL, escalate `MATRIX_AMBIGUOUS`; and remove "matrix/cross-tab (both axes hierarchical at once …)" from the field-of-possibles bullet.

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_demo_data.py demo/etkl_1a_showcase.ipynb docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop6): showcase Part G (matrix/cross-tab) + canvas increment 6"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §4 proximity builder + §3 detection → Task 1; §5 `classify_matrix`/`matrix_tiles` → Task 2; §6 `assert_matrix_region` → Task 3; §7 gate + §8 closing proof → Task 4; §9 showcase + canvas → Task 5. §8 tests distributed to the tasks that own them.
- **Type consistency:** `ColHeaderNode`/`MatrixRegion` fields and `assert_matrix_region(g, mreg, band, table_uri, doc_uri, page) -> int`, `classify_matrix(band)`, `matrix_tiles(mreg)`, `is_matrix_candidate(band)`, `col_tree_tiles(tree, data_cols)` used identically across tasks.
- **No-regression made explicit:** Task 4 Step 3 wraps the entire existing Loop 2 UNSUPPORTED body verbatim in a new `else`; Task 4 Step 5 runs the full suite; `test_pivot_still_column_hierarchy` + `test_row_grouped_*` (existing) guard against case-stealing. No ontology/SHACL changes (union of existing shapes).
- **Placeholder scan:** none — every code step carries exact content. (Task 5 Step 1 describes the demo fixture in prose because it mirrors the Task 1 fixture and is verified by the re-run; the compile-readout cell is given verbatim.)
- **Empirical grounding:** the fixture geometry, classification path, proximity spans, and row-tree tiling are all confirmed by the 2026-07-09 probes recorded in Global Constraints.
