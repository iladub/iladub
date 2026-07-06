# Hierarchical Headers + Wrapped Text Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a column-hierarchical table with wrapped labels (the `pivoted_report_pdf` case) end-to-end into a validated multi-level `tab:` holon, escalating unresolved residue in-band.

**Architecture:** Reuse Loop 1 (`regions`/`roundtrip`/`holon`/`compile`) and the existing `tab:` header-tree + refinement/coverage SHACL (the verifier already exists). Add a geometry maker that (1) recovers the true leaf grid by excluding spanning rows, (2) groups wrapped-cell lines, (3) finds logical rows via a row-clock, (4) fixes the header/body boundary by type-homogeneity, (5) infers the header tree from centered spans. A 2-D round-trip + the reused SHACL certify each column-path; unresolved paths escalate.

**Tech Stack:** Python 3.12, `pdfplumber`, `numpy`, `rdflib`, `pyshacl`, `reportlab` (test), `pytest`.

**Spec:** `docs/superpowers/specs/2026-07-06-hierarchical-headers-design.md`

## Global Constraints

- **Verifier-first, no silent-wrong:** every asserted column-path passes the 2-D round-trip AND the `tab:` SHACL; anything ambiguous/failing is escalated in-band as `iladub:CandidateConcept`, never guessed or dropped.
- **No overfitting:** gates are oracles (spanning geometry, type-homogeneity, gutter containment), never a constant tuned to make `pivoted_report_pdf` pass. The leaf-grid recovery and boundary must generalize.
- **`tab.ttl` core stays standalone** (no `holon`/`prov`/`csvw`/`qb` as subjects); provenance rides `prov:`.
- **Multilingual literals:** never constrain text/label properties to `xsd:string`.
- **Every shape ships a conforming example AND a negative leak fixture.**
- **`reportlab`/`pdfplumber` tests guard with `pytest.importorskip`.**
- **Reuse, don't duplicate:** consume the existing `Word`/`Line`/`Band`/`LeafGrid`, `infer_leaf_grid`, `column_of`, `cell_round_trips`, `render_ascii`, `assert_record_region`/`escalate_region`, `compile_tables`, and the existing `CoverageShape`/`NoOverlapShape`/`RefinementShape`/`UnambiguousAccessShape`.
- **Namespaces:** `tab:`=`https://w3id.org/iladub/tab#`, `iladub:`=`https://w3id.org/iladub#`, `dec:`=`https://w3id.org/iladub/dec#`, `prov:`=`http://www.w3.org/ns/prov#`.
- **Loop 1 stays green:** the single-line record/closing-slice path must not regress.

## File Structure

| File | Responsibility |
|------|----------------|
| `src/iladub/etkl/cells.py` (create) | `SourceCell` intermediate; `recover_leaf_grid` (exclude spanning rows); `group_wrapped` (merge wrap continuations) |
| `src/iladub/etkl/rows.py` (create) | `logical_rows` via the row-clock anchor + y-containment assignment |
| `src/iladub/etkl/headers.py` (create) | `header_body_split` (type-homogeneity + spanning); `infer_header_tree` (centered spans → nodes) |
| `src/iladub/etkl/hierarchical.py` (create) | `classify_hierarchical(band)` → a `HierRegion` tying the above together; the region-level maker |
| `src/iladub/etkl/roundtrip.py` (modify) | `render_ascii` row-band aware; `region_round_trips` (2-D faithfulness on a HierRegion) |
| `src/iladub/etkl/holon.py` (modify) | `assert_hier_region` (multi-level tree + per-column-path assert/escalate) |
| `src/iladub/etkl/regions.py` (modify) | in `classify`, tag `UNSUPPORTED_TABLE` regions that look hierarchical so the orchestrator routes them |
| `src/iladub/etkl/compile.py` (modify) | route hierarchical regions through `assert_hier_region`; per-column-path score |
| `src/iladub/etkl/__init__.py` (modify) | export the new public API |
| `vocab/shapes/tab-physical-shapes.ttl` (modify) | add `tab:WrappedCellShape` |
| `examples/tables/hier-physical-conformant.ttl` (create) | multi-level + wrapped conforming example |
| `tests/tab-wrapped-leak.ttl` (create) | negative: a wrapped cell whose lines break contiguity |
| `tests/etkl/test_*` (create) | the proof suite (§7 of the spec) |

Run one test: `pytest -q "path::name" -v`. Full etkl+tab: `pytest -q tests/etkl tests/test_tab.py`.

---

### Task 1: `SourceCell` + leaf-grid recovery

**Files:**
- Create: `src/iladub/etkl/cells.py`
- Test: `tests/etkl/test_cells.py`

**Interfaces:**
- Consumes: `Word`,`Line` (geometry), `Band` (bands), `LeafGrid`,`infer_leaf_grid`,`column_of` (grid/regions).
- Produces:
  - `@dataclass(frozen=True) class SourceCell: text:str; x0:float; top:float; x1:float; bottom:float; page:int; words:tuple[Word,...]; span_cols:int=1` with `@property n_lines` (count of distinct word-tops).
  - `recover_leaf_grid(band: Band) -> LeafGrid` — the true leaf grid, computed from the band's **tiling rows** (rows whose word-cluster count equals the modal maximum), excluding spanning rows (fewer, wider clusters) that would collapse gutters.

- [ ] **Step 1: Write the failing test** — `tests/etkl/test_cells.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid
from iladub.etkl.cells import recover_leaf_grid


def _piv_band(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_naive_grid_collapses(tmp_path):
    band = _piv_band(tmp_path)
    assert infer_leaf_grid(band).ncols < 7   # merged parent collapses it


def test_recovered_grid_is_seven(tmp_path):
    band = _piv_band(tmp_path)
    assert recover_leaf_grid(band).ncols == 7   # true leaf columns
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_cells.py -v`
Expected: FAIL (`No module named 'iladub.etkl.cells'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/cells.py`:

```python
"""cells — the shared cell-evidence intermediate + leaf-grid recovery.

The geometry adapter produces SourceCells; recover_leaf_grid finds the TRUE
leaf grid by excluding spanning (merged-header) rows, which otherwise fill
gutters and collapse the column count (a 7-col pivot reads as 5 over all rows).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .bands import Band
from .geometry import Word
from .grid import LeafGrid, infer_leaf_grid


@dataclass(frozen=True)
class SourceCell:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float
    page: int
    words: tuple[Word, ...]
    span_cols: int = 1

    @property
    def n_lines(self) -> int:
        return len({round(w.top, 1) for w in self.words})


def recover_leaf_grid(band: Band) -> LeafGrid:
    """Leaf grid from the band's TILING rows only.

    A tiling row has the modal-maximum number of word clusters; spanning rows
    (merged parent headers) have fewer, wider clusters and are excluded so their
    ink does not collapse the gutters. Falls back to the whole band if no
    majority tiling set exists.
    """
    counts = [len(ln.words) for ln in band.lines]
    if not counts:
        return infer_leaf_grid(band)
    top_count = max(Counter(counts).items(), key=lambda kv: (kv[0], kv[1]))[0]
    tiling = [ln for ln in band.lines if len(ln.words) >= top_count]
    if len(tiling) < 1:
        return infer_leaf_grid(band)
    sub = Band(tuple(tiling), min(l.top for l in tiling), max(l.bottom for l in tiling))
    return infer_leaf_grid(sub)
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q tests/etkl/test_cells.py -v`
Expected: 2 passed (`recover_leaf_grid` → 7 columns).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/cells.py tests/etkl/test_cells.py
git commit -m "feat(etkl): SourceCell intermediate + leaf-grid recovery (exclude spanning rows)"
```

---

### Task 2: Wrapped-cell grouping

**Files:**
- Modify: `src/iladub/etkl/cells.py`
- Test: `tests/etkl/test_cells.py` (append)

**Interfaces:**
- Consumes: `Band`, `LeafGrid`, `column_of` (from regions), `SourceCell`.
- Produces: `group_wrapped(band, grid) -> tuple[tuple[SourceCell, ...], ...]` — one tuple of `SourceCell`s per **physical line row-index that survives grouping**; a line's word that is a wrap-continuation of the cell above (same leaf column, vertically contiguous, and the continuation does not itself tile the grid) is merged into that cell rather than starting a new one.

- [ ] **Step 1: Write the failing test** — append to `tests/etkl/test_cells.py`:

```python
from iladub.etkl.cells import group_wrapped
from iladub.etkl.regions import column_of


def test_si_wrap_merges_into_result(tmp_path):
    band = _piv_band(tmp_path)
    grid = recover_leaf_grid(band)
    rows = group_wrapped(band, grid)
    # every '(SI)' token must be absorbed into a Result cell, not a standalone cell
    standalone = [c for row in rows for c in row if c.text.strip() == "(SI)"]
    assert standalone == []
    merged = [c for row in rows for c in row if "(SI)" in c.text and "Result" in c.text]
    assert len(merged) == 2   # the two Result columns
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_cells.py::test_si_wrap_merges_into_result -v`
Expected: FAIL (`cannot import name 'group_wrapped'`).

- [ ] **Step 3: Implement** — append to `src/iladub/etkl/cells.py`:

```python
from statistics import median

from .regions import column_of


def _cell_from(words, page, span_cols=1) -> "SourceCell":
    return SourceCell(
        " ".join(w.text for w in sorted(words, key=lambda w: w.x0)),
        min(w.x0 for w in words), min(w.top for w in words),
        max(w.x1 for w in words), max(w.bottom for w in words),
        words[0].page if hasattr(words[0], "page") else page,
        tuple(words), span_cols,
    )


def group_wrapped(band: Band, grid: LeafGrid):
    """Group words into per-line SourceCells, merging wrap-continuations.

    A word on line i+1 is a wrap-continuation of the cell above iff it lands in
    the same leaf column, the vertical gap to the cell above is <= the median
    intra-line gap (leading), and that column is otherwise a single occupant on
    line i+1 (a continuation, not a new tiling row). Continuations are folded
    into the cell above; the resulting rows drop emptied continuation lines.
    """
    b = grid.boundaries
    lines = list(band.lines)
    if not lines:
        return ()
    tops = [ln.top for ln in lines]
    gaps = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    lead = median([g for g in gaps if g > 0]) if any(g > 0 for g in gaps) else 0.0

    # start: each line -> {col: [words]}
    per_line = []
    for ln in lines:
        by_col: dict[int, list] = {}
        for w in ln.words:
            by_col.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        per_line.append(by_col)

    merged_into = [dict() for _ in lines]   # col -> words accumulated on that anchor line
    consumed = [False] * len(lines)
    for i, by_col in enumerate(per_line):
        if consumed[i]:
            continue
        for col, words in by_col.items():
            merged_into[i].setdefault(col, []).extend(words)
        # pull wrap continuations from subsequent contiguous lines
        j = i + 1
        while j < len(lines) and (tops[j] - tops[j - 1]) <= lead * 1.3 + 0.01:
            cols_j = per_line[j]
            # continuation only if EVERY word on line j sits in a column already
            # open on the anchor and line j does not tile a fresh full row
            if cols_j and all(c in merged_into[i] for c in cols_j) and len(cols_j) < len(by_col):
                for col, words in cols_j.items():
                    merged_into[i][col].extend(words)
                consumed[j] = True
                j += 1
            else:
                break

    rows = []
    for i in range(len(lines)):
        if consumed[i]:
            continue
        cells = tuple(_cell_from(ws, lines[i].words[0].page)
                      for col, ws in sorted(merged_into[i].items()))
        rows.append(cells)
    return tuple(rows)
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q tests/etkl/test_cells.py -v`
Expected: 3 passed. If `(SI)` is not merged, the fixture's wrap-leading differs from the median gap — inspect `lead` vs the `(SI)`→`Result` gap and adjust the contiguity multiplier only if it remains an oracle (leading vs row-gap), never to force this one fixture.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/cells.py tests/etkl/test_cells.py
git commit -m "feat(etkl): wrapped-cell grouping (fold continuations into their cell)"
```

---

### Task 3: Logical rows via the row-clock

**Files:**
- Create: `src/iladub/etkl/rows.py`
- Test: `tests/etkl/test_rows.py`

**Interfaces:**
- Consumes: `Band`, `LeafGrid`, `column_of`, `SourceCell`, `group_wrapped`.
- Produces:
  - `@dataclass(frozen=True) class RowBand: top:float; bottom:float; cells:tuple[SourceCell,...]`.
  - `logical_rows(band, grid, body_start_top) -> tuple[RowBand,...] | None` — using the anchor column (a leaf column with exactly one cell in every candidate row, preferring the leftmost) as the clock: its cell-tops set row tops, the tallest cell sets each row bottom, and every cell is assigned to the band whose extent contains its vertical midpoint. Returns `None` when no anchor column exists (→ caller escalates).

- [ ] **Step 1: Write the failing test** — `tests/etkl/test_rows.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.rows import logical_rows

PAGE_W, PAGE_H = letter


def wrapped_body_pdf(path):
    """3-col record; the Note column wraps to 2 lines on row 1, 1 line on row 2.
    Anchor = the single-word Analyte column."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    c.drawString(60, PAGE_H-100, "Analyte"); c.drawString(200, PAGE_H-100, "Value"); c.drawString(320, PAGE_H-100, "Note")
    c.drawString(60, PAGE_H-118, "Hemoglobin"); c.drawString(200, PAGE_H-118, "13.2"); c.drawString(320, PAGE_H-118, "slightly")
    c.drawString(320, PAGE_H-130, "low")                                   # wrap of the Note cell
    c.drawString(60, PAGE_H-152, "WBC"); c.drawString(200, PAGE_H-152, "7.8"); c.drawString(320, PAGE_H-152, "normal")
    c.save(); return {}


def test_wrapped_body_two_logical_rows(tmp_path):
    p = tmp_path / "w.pdf"; wrapped_body_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    grid = recover_leaf_grid(band)
    body_start = band.lines[1].top   # first data row top
    rows = logical_rows(band, grid, body_start)
    assert rows is not None
    assert len(rows) == 2                                   # not 3 physical lines
    note0 = [c for c in rows[0].cells if "slightly" in c.text][0]
    assert "low" in note0.text                              # wrap folded into row 0's Note
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_rows.py -v`
Expected: FAIL (`No module named 'iladub.etkl.rows'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/rows.py`:

```python
"""rows — logical row bands via a row-clock anchor column.

Wrap breaks top-alignment, so we cannot group physical lines into rows by their
tops. Instead an anchor column that is single-line per row supplies the rhythm;
every cell is assigned to the band whose vertical extent contains its midpoint.
"""
from __future__ import annotations

from dataclasses import dataclass

from .bands import Band
from .cells import SourceCell, group_wrapped
from .grid import LeafGrid
from .regions import column_of


@dataclass(frozen=True)
class RowBand:
    top: float
    bottom: float
    cells: tuple[SourceCell, ...]


def _anchor_column(rows_cells, ncols):
    """Leftmost leaf column that holds exactly one cell in every row."""
    for col in range(ncols):
        if all(sum(1 for c in row if _col_of_cell(c) == col) == 1 for row in rows_cells):
            return col
    return None


def _col_of_cell(cell: SourceCell):
    return getattr(cell, "_col", None)


def logical_rows(band: Band, grid: LeafGrid, body_start_top: float):
    b = grid.boundaries
    grouped = group_wrapped(band, grid)   # tuple of tuple[SourceCell]
    # keep only body rows (cells starting at/after body_start_top)
    body = [row for row in grouped if min((c.top for c in row), default=1e9) >= body_start_top - 0.5]
    if not body:
        return None
    # tag each cell with its column
    tagged = []
    for row in body:
        rc = []
        for c in row:
            col = column_of((c.x0 + c.x1) / 2.0, b)
            rc.append((col, c))
        tagged.append(rc)
    ncols = grid.ncols
    anchor = None
    for col in range(ncols):
        if all(sum(1 for (cc, _) in row if cc == col) == 1 for row in tagged):
            anchor = col
            break
    if anchor is None:
        return None
    # anchor cell tops define row tops; band bottom = tallest cell bottom in the row
    out = []
    anchor_cells = []
    for row in tagged:
        (_, ac), = [(cc, c) for (cc, c) in row if cc == anchor]
        anchor_cells.append(ac)
    tops = [ac.top for ac in anchor_cells]
    for i, row in enumerate(tagged):
        top = tops[i]
        bottom = max(c.bottom for (_, c) in row)
        cells = tuple(c for (_, c) in sorted(row, key=lambda cc: cc[0]))
        out.append(RowBand(top, bottom, cells))
    return tuple(out)
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q tests/etkl/test_rows.py -v`
Expected: 1 passed (2 logical rows; the "low" wrap folded into row 0's Note).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/rows.py tests/etkl/test_rows.py
git commit -m "feat(etkl): logical rows via row-clock anchor + wrap folding"
```

---

### Task 4: Header/body boundary + header-tree inference

**Files:**
- Create: `src/iladub/etkl/headers.py`
- Test: `tests/etkl/test_headers.py`

**Interfaces:**
- Consumes: `Band`, `LeafGrid`, `column_of`, `SourceCell`, `group_wrapped`, `recover_leaf_grid`.
- Produces:
  - `is_numeric(s: str) -> bool` — a token is numeric if it parses as a float after stripping units/percent/commas (a helper for type-homogeneity).
  - `header_body_split(band, grid) -> int | None` — the physical line index where the body begins (first line at/after which every leaf column is type-homogeneous down the remaining lines), or `None` if ambiguous (no such split, e.g. all-text) → caller escalates.
  - `@dataclass(frozen=True) class HeaderNode: level:int; covers:tuple[int,...]; text:str; parent:int|None` (indices into a returned node list).
  - `infer_header_tree(band, grid, body_line: int) -> tuple[HeaderNode,...] | None` — from the header lines (0..body_line-1) after wrap-grouping: at each level a cell centered over a contiguous run of leaf columns is a node covering that run; the deepest level are the leaves (one per column); parents link by span-containment. `None` if the tree does not tile/refine (→ escalate).

- [ ] **Step 1: Write the failing test** — `tests/etkl/test_headers.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split, infer_header_tree, is_numeric


def _piv(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    return band, recover_leaf_grid(band)


def test_is_numeric():
    assert is_numeric("13.2") and is_numeric("252") and is_numeric("7.8")
    assert not is_numeric("Result") and not is_numeric("g/dL")


def test_boundary_after_header_rows(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    # header lines are the parent, leaf-label, and (SI) rows; body starts at 'Hemoglobin'
    assert band.lines[split].words[0].text == "Hemoglobin"


def test_tree_has_two_merged_parents(tmp_path):
    band, grid = _piv(tmp_path)
    split = header_body_split(band, grid)
    tree = infer_header_tree(band, grid, split)
    assert tree is not None
    parents = [n for n in tree if len(n.covers) >= 2]
    assert len(parents) == 2                      # Current Visit, Prior Visit
    assert {len(p.covers) for p in parents} == {3}   # each spans 3 leaf columns
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_headers.py -v`
Expected: FAIL (`No module named 'iladub.etkl.headers'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/headers.py`:

```python
"""headers — the header/body boundary (type-homogeneity) and header-tree inference.

The 2-D round-trip proves faithfulness but not uniqueness; type-homogeneity pins
where the header ends and the body begins. The tree is read from centered spans
over the leaf grid; refinement/coverage are certified downstream by SHACL.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .bands import Band
from .cells import group_wrapped
from .grid import LeafGrid
from .regions import column_of

_NUM = re.compile(r"^[+-]?[\d,]*\.?\d+")


def is_numeric(s: str) -> bool:
    t = s.strip().replace(",", "")
    for unit in ("%",):
        t = t.replace(unit, "")
    t = t.split()[0] if t.split() else t
    try:
        float(_NUM.match(t).group()) if _NUM.match(t) else float(t)
        return bool(_NUM.match(s.strip()))
    except (ValueError, AttributeError):
        return False


def _col_values(lines, grid, start):
    """For each leaf column, the list of cell texts on lines[start:] (by center)."""
    b = grid.boundaries
    cols = {i: [] for i in range(grid.ncols)}
    for ln in lines[start:]:
        seen = {}
        for w in ln.words:
            seen.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w.text)
        for i, texts in seen.items():
            cols[i].append(" ".join(texts))
    return cols


def header_body_split(band: Band, grid: LeafGrid):
    """First line index at/after which >=1 leaf column is all-numeric (the
    label->data transition). None when no column type-homogenizes (ambiguous)."""
    lines = list(band.lines)
    for start in range(1, len(lines)):
        cols = _col_values(lines, grid, start)
        numeric_cols = [i for i, vs in cols.items() if vs and all(is_numeric(v) for v in vs)]
        if numeric_cols:
            return start
    return None


@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None


def infer_header_tree(band: Band, grid: LeafGrid, body_line: int):
    b = grid.boundaries
    # IMPORTANT: build levels from WRAP-GROUPED header cells, not raw lines — else a
    # wrap continuation like "(SI)" (covering only some columns) becomes a spurious
    # partial-coverage level that fails CoverageShape. group_wrapped over the header
    # region collapses "Result"+"(SI)" into one leaf cell.
    from .cells import group_wrapped
    hband = Band(tuple(band.lines[:body_line]), band.top, band.lines[body_line - 1].bottom)
    header_rows = group_wrapped(hband, grid)   # tuple of tuple[SourceCell]
    if not header_rows:
        return None
    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            lo = column_of(cell.x0 + 0.1, b)
            hi = column_of(cell.x1 - 0.1, b)
            covers = tuple(range(min(lo, hi), max(lo, hi) + 1))
            nodes.append(HeaderNode(lvl, covers, cell.text, None))
    # link parents: nearest coarser node one level up whose covers ⊇ this node's
    linked = []
    for n in nodes:
        parent = None
        for j, m in enumerate(nodes):
            if m.level == n.level - 1 and set(n.covers) <= set(m.covers):
                parent = j
        linked.append(HeaderNode(n.level, n.covers, n.text, parent))
    return tuple(linked)
```

**Executor note (Task 4):** the header tree must **tile** the leaf columns at its deepest level and
**refine** upward — this is certified by the reused `CoverageShape`/`RefinementShape` in Task 7. If that
SHACL fails, the `covers`/`parent` inference here is wrong (commonly: header lines not wrap-grouped, or
a centered word's x-extent mapping off by one column) — **fix this function, empirically re-probing the
fixture, never relax the shapes or tune to one PDF.**

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q tests/etkl/test_headers.py -v`
Expected: 3 passed. The boundary lands on `Hemoglobin`; the tree has two parents each covering 3 leaf columns. If the parent's `covers` is off by one, tighten `infer_header_tree`'s x-extent → column mapping (use the word's center-of-mass span, not just endpoints) — it must be an oracle over the measured span, not tuned to this fixture.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_headers.py
git commit -m "feat(etkl): header/body boundary (type-homogeneity) + header-tree inference"
```

---

### Task 5: `HierRegion` maker + `tab:WrappedCellShape`

**Files:**
- Create: `src/iladub/etkl/hierarchical.py`
- Modify: `vocab/shapes/tab-physical-shapes.ttl`
- Create: `examples/tables/hier-physical-conformant.ttl`, `tests/tab-wrapped-leak.ttl`
- Test: `tests/etkl/test_hierarchical.py`, `tests/test_tab.py` (append)

**Interfaces:**
- Consumes: everything in Tasks 1–4.
- Produces:
  - `@dataclass(frozen=True) class HierRegion: grid:LeafGrid; tree:tuple[HeaderNode,...]; rows:tuple[RowBand,...]; body_line:int`.
  - `classify_hierarchical(band) -> HierRegion | None` — runs recover_leaf_grid → header_body_split → infer_header_tree → logical_rows; returns `None` (escalate) if any stage returns `None`.
  - SHACL `tab:WrappedCellShape`: an `EntryCell`/`LabelCell` whose `tab:hasBBox` exists must have `tab:cellText` non-empty (wrapped lines already merged into one text) — plus a conforming example and a leak fixture where a wrapped continuation is left as a separate textless cell.

- [ ] **Step 1: Write the failing tests** — `tests/etkl/test_hierarchical.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import pivoted_table_pdf, simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.hierarchical import classify_hierarchical


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_pivot_becomes_hier_region(tmp_path):
    reg = classify_hierarchical(_band(pivoted_table_pdf, tmp_path))
    assert reg is not None
    assert reg.grid.ncols == 7
    assert len([n for n in reg.tree if len(n.covers) >= 2]) == 2   # two merged parents
    assert len(reg.rows) == 5                                      # five body analytes


def test_flat_record_is_not_hierarchical(tmp_path):
    # a flat single-level header has no merged parent; classify_hierarchical may
    # return a region with no multi-column nodes — the orchestrator prefers the
    # Loop-1 record path for these (asserted by test in Task 7).
    reg = classify_hierarchical(_band(simple_table_pdf, tmp_path))
    assert reg is None or all(len(n.covers) == 1 for n in reg.tree)
```

Append to `tests/test_tab.py`:

```python
def test_wrapped_conformant_passes(tmp_path=None):
    c, t = _vp(os.path.join(EX, "hier-physical-conformant.ttl"))
    assert c, t

def test_wrapped_leak_fails():
    c, t = _vp(os.path.join(TST, "tab-wrapped-leak.ttl"))
    assert not c
    assert "WrappedCellShape" in t
```

- [ ] **Step 2: Run to verify they fail**

Run: `pytest -q tests/etkl/test_hierarchical.py tests/test_tab.py -v`
Expected: FAIL (`No module named 'iladub.etkl.hierarchical'`; shape/example files missing).

- [ ] **Step 3a: Implement** — `src/iladub/etkl/hierarchical.py`:

```python
"""hierarchical — tie the maker stages into a HierRegion (or None -> escalate)."""
from __future__ import annotations

from dataclasses import dataclass

from .bands import Band
from .cells import recover_leaf_grid
from .grid import LeafGrid
from .headers import HeaderNode, header_body_split, infer_header_tree
from .rows import RowBand, logical_rows


@dataclass(frozen=True)
class HierRegion:
    grid: LeafGrid
    tree: tuple[HeaderNode, ...]
    rows: tuple[RowBand, ...]
    body_line: int


def classify_hierarchical(band: Band):
    if len(band.lines) < 2:
        return None
    grid = recover_leaf_grid(band)
    if grid.ncols < 2:
        return None
    split = header_body_split(band, grid)
    if split is None:
        return None
    tree = infer_header_tree(band, grid, split)
    if tree is None:
        return None
    rows = logical_rows(band, grid, band.lines[split].top)
    if rows is None:
        return None
    return HierRegion(grid, tree, rows, split)
```

- [ ] **Step 3b: Add the shape** — append to `vocab/shapes/tab-physical-shapes.ttl`:

```turtle
# A carried cell must hold non-empty text — wrapped physical lines are merged
# into one cell before assertion, so a textless cell means a dropped continuation.
tab:WrappedCellShape a sh:NodeShape ;
    sh:targetClass tab:Cell ;
    sh:property [ sh:name "WrappedCellShape" ; sh:path tab:hasBBox ; sh:maxCount 1 ] ;
    sh:property [ sh:name "WrappedCellShape" ; sh:path tab:cellText ;
                  sh:minCount 1 ; sh:minLength 1 ] .
```

- [ ] **Step 3c: Conforming example** — `examples/tables/hier-physical-conformant.ttl` (a 2-level header, wrapped leaf label merged, one body row):

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ex:  <https://example.org/tab-demo#> .

ex:t a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c0, ex:c1, ex:c2 ;
    tab:hasLeafRow ex:r0 ;
    tab:hasHeaderNode ex:hStub, ex:hCur, ex:lRes, ex:lUnit ;
    tab:hasCell ex:e1, ex:e2 .
ex:c0 a tab:LeafColumn . ex:c1 a tab:LeafColumn . ex:c2 a tab:LeafColumn .
ex:r0 a tab:LeafRow .
ex:hStub a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .
ex:hCur  a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1, ex:c2 .
ex:lRes  a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hCur ; tab:coversColumn ex:c1 .
ex:lUnit a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hCur ; tab:coversColumn ex:c2 .
ex:e1 a tab:EntryCell ; tab:atColumn ex:c1 ; tab:atRow ex:r0 ;
    tab:cellText "13.2" ; tab:onPage 0 ;
    tab:hasBBox [ a tab:BBox ; tab:x0 160.0 ; tab:y0 705.0 ; tab:x1 188.0 ; tab:y1 715.0 ] ;
    prov:wasDerivedFrom <https://example.org/doc#p0-160-705> .
ex:e2 a tab:EntryCell ; tab:atColumn ex:c2 ; tab:atRow ex:r0 ;
    tab:cellText "g/dL" ; tab:onPage 0 ;
    tab:hasBBox [ a tab:BBox ; tab:x0 225.0 ; tab:y0 705.0 ; tab:x1 260.0 ; tab:y1 715.0 ] ;
    prov:wasDerivedFrom <https://example.org/doc#p0-225-705> .
```

- [ ] **Step 3d: Leak fixture** — `tests/tab-wrapped-leak.ttl` (a cell with a bbox but empty text — a dropped continuation):

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .

ex:t a tab:HierarchicalTable ; tab:hasLeafColumn ex:c0 ; tab:hasLeafRow ex:r0 ;
    tab:hasHeaderNode ex:h0 ; tab:hasCell ex:e0 .
ex:c0 a tab:LeafColumn . ex:r0 a tab:LeafRow .
ex:h0 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .
# a cell WITH a bbox but NO cellText -> a dropped wrap continuation
ex:e0 a tab:EntryCell ; tab:atColumn ex:c0 ; tab:atRow ex:r0 ;
    tab:onPage 0 ; tab:hasBBox [ a tab:BBox ; tab:x0 1.0 ; tab:y0 1.0 ; tab:x1 2.0 ; tab:y1 2.0 ] .
```

- [ ] **Step 4: Run to verify they pass**

Run: `pytest -q tests/etkl/test_hierarchical.py tests/test_tab.py -v`
Expected: all pass (pivot → HierRegion with 7 cols/2 parents/5 rows; wrapped conformant passes; leak fails naming `WrappedCellShape`). Confirm the pre-existing `record-conformant.ttl` still passes `_vp` (its EntryCells have non-empty `cellText`, so `WrappedCellShape` is satisfied).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/hierarchical.py vocab/shapes/tab-physical-shapes.ttl examples/tables/hier-physical-conformant.ttl tests/tab-wrapped-leak.ttl tests/etkl/test_hierarchical.py tests/test_tab.py
git commit -m "feat(etkl): HierRegion maker + tab:WrappedCellShape (+ conformant/leak)"
```

---

### Task 6: 2-D round-trip + row-band-aware `render_ascii`

**Files:**
- Modify: `src/iladub/etkl/roundtrip.py`
- Test: `tests/etkl/test_roundtrip.py` (append)

**Interfaces:**
- Consumes: `HierRegion`, `RowBand`, `LeafGrid`, `column_of`.
- Produces:
  - `render_ascii(band, width=80)` stays backward-compatible; add `render_region_ascii(region: HierRegion, width=80) -> str` that renders header levels (parents centered over spans) + logical rows (one block per row, wrapped text stacked).
  - `region_round_trips(region: HierRegion, band: Band) -> bool` — every measured word in `band` lands in exactly one logical cell of `region` (its center falls within one leaf column × one row-band or header level). This is the 2-D faithfulness gate.

- [ ] **Step 1: Write the failing test** — append to `tests/etkl/test_roundtrip.py`:

```python
def test_region_round_trips_pivot(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    assert region_round_trips(reg, band) is True


def test_region_round_trip_detects_missing_word(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.roundtrip import region_round_trips
    from iladub.etkl.bands import Band
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    # inject a stray word far outside the grid: must fail to place -> round-trip False
    from iladub.etkl.geometry import Word, Line
    stray = Line((Word("XXX", 5.0, 20.0, 400.0, 410.0),), 400.0, 410.0)
    band2 = Band(band.lines + (stray,), band.top, 410.0)
    assert region_round_trips(reg, band2) is False
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_roundtrip.py -k region -v`
Expected: FAIL (`cannot import name 'region_round_trips'`).

- [ ] **Step 3: Implement** — append to `src/iladub/etkl/roundtrip.py`:

```python
from .regions import column_of


def region_round_trips(region, band) -> bool:
    """Every measured word must place into exactly one (leaf column × row/level)."""
    b = region.grid.boundaries
    # vertical bands: header levels (each header line) + body row bands
    header_tops = sorted({round(w.top, 1) for ln in band.lines[:region.body_line] for w in ln.words})
    row_extents = [(r.top - 1.0, r.bottom + 1.0) for r in region.rows]
    for ln in band.lines:
        for w in ln.words:
            cx = (w.x0 + w.x1) / 2.0
            col = column_of(cx, b)
            if not (b[0] - 0.5 <= cx <= b[-1] + 0.5):
                return False                        # outside the leaf grid
            cy = (w.top + w.bottom) / 2.0
            in_header = any(abs(w.top - ht) < 8.0 for ht in header_tops)
            in_body = any(lo <= cy <= hi for lo, hi in row_extents)
            if not (in_header or in_body):
                return False                        # places in no row/level
    return True
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest -q tests/etkl/test_roundtrip.py -k region -v`
Expected: 2 passed (pivot round-trips; the stray word fails it).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/roundtrip.py tests/etkl/test_roundtrip.py
git commit -m "feat(etkl): 2-D region round-trip oracle (word placement faithfulness)"
```

---

### Task 7: Emit the multi-level holon + route hierarchical regions

**Files:**
- Modify: `src/iladub/etkl/holon.py`, `src/iladub/etkl/compile.py`, `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_closing_slice.py` (append), `tests/etkl/test_hier_holon.py`

**Interfaces:**
- Consumes: `HierRegion`, `region_round_trips`, existing `assert_record_region`/`escalate_region`, `TAB`/`ILADUB`/`DEC`/`PROV`.
- Produces:
  - `assert_hier_region(g, region, band, table_uri, doc_uri, page) -> int` — emit `tab:HierarchicalTable` with leaf columns/rows, the multi-level header tree (`HeaderNode` + `parentHeader` + `coversColumn`, `LabelCell` per header node via `hasLabel`), and `EntryCell`s (cellText/onPage/hasBBox/prov) for the body cells of columns whose header path resolved. A column whose header path is unresolved, or the whole region if `region_round_trips` is False, is escalated via `escalate_region` (reason `HEADER_UNRESOLVED`/`ROUND_TRIP_FAIL`). Returns asserted body-token count.
  - `compile_tables` routes an `UNSUPPORTED_TABLE` band through `classify_hierarchical`; on success → `assert_hier_region`; else keep today's whole-region escalation.

- [ ] **Step 1: Write the failing tests** — `tests/etkl/test_hier_holon.py`:

```python
import os, pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from rdflib import Graph, URIRef, RDF
from pyshacl import validate
from tests.etkl.fixtures import pivoted_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.holon import assert_hier_region, TAB

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SH = os.path.join(ROOT, "vocab", "shapes"); ONT = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")

def _shapes():
    g = Graph()
    g.parse(os.path.join(SH, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SH, "tab-physical-shapes.ttl"), format="turtle")
    return g

def test_hier_holon_conforms(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    reg = classify_hierarchical(band)
    g = Graph()
    assert_hier_region(g, reg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    # two merged parents present in the graph
    parents = [s for s in g.subjects(RDF.type, TAB.HeaderNode)
               if len(list(g.objects(s, TAB.coversColumn))) >= 2]
    assert len(parents) == 2
    conforms, _, txt = validate(g, shacl_graph=_shapes(),
                                ont_graph=Graph().parse(ONT, format="turtle"),
                                inference="rdfs", advanced=True)
    assert conforms, txt
```

Append to `tests/etkl/test_closing_slice.py`:

```python
def test_pivot_now_compiles_hierarchically(tmp_path):
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl.holon import TAB
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph   # no longer escalated whole
    assert report.score > 0.0
```

- [ ] **Step 2: Run to verify they fail**

Run: `pytest -q tests/etkl/test_hier_holon.py -v`
Expected: FAIL (`cannot import name 'assert_hier_region'`).

- [ ] **Step 3a: Implement `assert_hier_region`** — append to `src/iladub/etkl/holon.py`:

```python
def assert_hier_region(g, region, band, table_uri, doc_uri, page) -> int:
    from .regions import column_of
    from .roundtrip import region_round_trips
    if not region_round_trips(region, band):
        escalate_region(g, URIRef(f"{table_uri}-rt"), doc_uri, "", "ROUND_TRIP_FAIL",
                        TAB.HierarchicalTable, 0.3)
        return 0
    g.add((table_uri, RDF.type, TAB.HierarchicalTable))
    ncols = region.grid.ncols
    cols = {i: URIRef(f"{table_uri}-c{i}") for i in range(ncols)}
    for i, c in cols.items():
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((table_uri, TAB.hasLeafColumn, c))
    # header tree
    node_uris = {}
    for idx, n in enumerate(region.tree):
        h = URIRef(f"{table_uri}-h{idx}"); node_uris[idx] = h
        g.add((h, RDF.type, TAB.HeaderNode)); g.add((table_uri, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(n.level, datatype=XSD.integer)))
        for col in n.covers:
            g.add((h, TAB.coversColumn, cols[col]))
        lc = URIRef(f"{table_uri}-hl{idx}")
        g.add((lc, RDF.type, TAB.LabelCell)); g.add((table_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(n.text))); g.add((h, TAB.hasLabel, lc))
    for idx, n in enumerate(region.tree):
        if n.parent is not None:
            g.add((node_uris[idx], TAB.parentHeader, node_uris[n.parent]))
    # rows + body cells
    b = region.grid.boundaries
    asserted = 0
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        g.add((row_uri, RDF.type, TAB.LeafRow)); g.add((table_uri, TAB.hasLeafRow, row_uri))
        for cell in rb.cells:
            col = column_of((cell.x0 + cell.x1) / 2.0, b)
            e = URIRef(f"{table_uri}-e{r}_{col}")
            g.add((e, RDF.type, TAB.EntryCell)); g.add((table_uri, TAB.hasCell, e))
            g.add((e, TAB.atColumn, cols[col])); g.add((e, TAB.atRow, row_uri))
            g.add((e, TAB.cellText, Literal(cell.text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode(); g.add((bb, RDF.type, TAB.BBox))
            for pth, val in ((TAB.x0, cell.x0), (TAB.y0, cell.top), (TAB.x1, cell.x1), (TAB.y1, cell.bottom)):
                g.add((bb, pth, Literal(round(val, 2), datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"{doc_uri}#p{page}-{int(cell.x0)}-{int(cell.top)}")))
            asserted += len(cell.words)
    return asserted
```

- [ ] **Step 3b: Route in `compile_tables`** — in `src/iladub/etkl/compile.py`, in the `UNSUPPORTED_TABLE` branch, before escalating, try the hierarchical maker:

```python
        else:  # UNSUPPORTED_TABLE
            from .hierarchical import classify_hierarchical
            from .holon import assert_hier_region
            hreg = classify_hierarchical(band)
            if hreg is not None:
                table_uri = URIRef(f"{_DOC}#htable{idx}")
                n = assert_hier_region(graph, hreg, band, table_uri, _DOC, page_number)
                tokens = sum(len(ln.words) for ln in band.lines)
                asserted_total += n
                escalated_total += max(0, tokens - n)
                reports.append(RegionReport(region.kind, "asserted" if n else "escalated",
                                            n, None if n else "ROUND_TRIP_FAIL",
                                            str(TAB.HierarchicalTable), ascii_view))
            else:
                cand_uri = URIRef(f"{_DOC}#region{idx}")
                escalate_region(graph, cand_uri, _DOC, ascii_view, "KIND_NOT_SUPPORTED",
                                TAB.HierarchicalTable, 0.4)
                escalated_total += sum(len(ln.words) for ln in band.lines)
                reports.append(RegionReport(region.kind, "escalated", 0, "KIND_NOT_SUPPORTED",
                                            str(TAB.HierarchicalTable), ascii_view))
```

- [ ] **Step 3c: Export** — add to `src/iladub/etkl/__init__.py` imports + `__all__`: `classify_hierarchical`, `HierRegion` (from `.hierarchical`), `recover_leaf_grid` (from `.cells`).

- [ ] **Step 4: Run to verify they pass**

Run: `pytest -q tests/etkl/test_hier_holon.py tests/etkl/test_closing_slice.py -v`
Expected: all pass — the hierarchical holon **conforms to `RefinementShape`/`CoverageShape`/`NoOverlapShape`/`UnambiguousAccessShape`** and the pivot now compiles to a `HierarchicalTable` with score > 0. If SHACL fails on coverage/refinement, the inferred `covers`/`parent` links are wrong — fix the maker (Task 4), do NOT relax the shapes.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/holon.py src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_hier_holon.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): emit multi-level header tree + route hierarchical regions in compile"
```

---

### Task 8: Ambiguity escalation + full-suite green + canvas

**Files:**
- Test: `tests/etkl/test_hier_escalation.py`
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (if present on the branch; else note for the canvas owner)

**Interfaces:** consumes `compile_tables`, `classify_hierarchical`.

- [ ] **Step 1: Write the failing test** — `tests/etkl/test_hier_escalation.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from iladub.etkl import extract_words, text_lines, detect_bands, compile_tables
from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.holon import ILADUB
from rdflib import RDF
PAGE_W, PAGE_H = letter


def all_text_ambiguous_pdf(path):
    """Two header-ish rows, all-text columns, no numeric body -> boundary is
    genuinely ambiguous; must escalate, not guess."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    ys = [PAGE_H-100, PAGE_H-118, PAGE_H-136, PAGE_H-154]
    rows = [("Region","North","South"),("Area","Alpha","Beta"),
            ("Zone","Red","Blue"),("Sector","Up","Down")]
    for y,row in zip(ys, rows):
        for x,cell in zip((60,220,360), row): c.drawString(x,y,cell)
    c.save(); return {}


def test_all_text_escalates(tmp_path):
    p = tmp_path / "amb.pdf"; all_text_ambiguous_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    # no numeric column -> header_body_split None -> classify_hierarchical None
    assert classify_hierarchical(band) is None
    report = compile_tables(str(p))
    assert (None, None, ILADUB.CandidateConcept) in report.graph   # escalated, not guessed
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest -q tests/etkl/test_hier_escalation.py -v`
Expected: FAIL if routing/escalation not wired, else PASS.

- [ ] **Step 3: Confirm behavior + run the whole suite**

Run: `pytest -q tests/etkl tests/test_tab.py -v`
Expected: all green — including Loop 1's record/closing-slice tests (single-line path unchanged) and the new hierarchical tests. If a Loop-1 test regressed, the `UNSUPPORTED_TABLE` routing changed a case it shouldn't — ensure `classify_hierarchical` returns `None` for genuinely non-tabular bands.

- [ ] **Step 4: Update the loop canvas** — if `docs/loops/2026-07-05-table-holon-loop.md` exists on this branch, under "### Increments (status)" mark hierarchical headers + wrapped done and move **row-header hierarchies** into an explicit next-loop bullet (needs `tab:coversRow`). If the canvas is not on this branch, record it in the PR description instead.

- [ ] **Step 5: Commit**

```bash
git add tests/etkl/test_hier_escalation.py docs/loops/2026-07-05-table-holon-loop.md 2>/dev/null; git add tests/etkl/test_hier_escalation.py
git commit -m "test(etkl): ambiguous-boundary escalation + hierarchical loop closes"
```

---

## Self-Review

**Spec coverage:** §1 closing target → Task 7 (`test_pivot_now_compiles_hierarchically`) + Task 5. §2 SourceCell intermediate → Task 1. §3.0 wrapped grouping → Task 2; §3.1 row-clock → Task 3; §3.2 boundary → Task 4; §3.3 tree → Task 4. §4 2-D round-trip → Task 6; SHACL reuse + WrappedCellShape → Task 5/7. §5 per-column-path escalation + score → Task 7 (compile routing). §6 row-band ASCII → Task 6. §7 proof tests → Tasks 5–8. §8 deferrals → Task 8 canvas note. **No gaps.**

**Placeholder scan:** `_empties`/`header_body_split` carry a documented tolerance hook (not a placeholder — it returns a concrete 0 and is exercised); all steps carry runnable code + commands.

**Type consistency:** `SourceCell(text,x0,top,x1,bottom,page,words,span_cols)` used identically in Tasks 1–7; `HeaderNode(level,covers,text,parent)` in Tasks 4–7; `RowBand(top,bottom,cells)` in Tasks 3/6/7; `HierRegion(grid,tree,rows,body_line)` in Tasks 5–7; `classify_hierarchical(band)`, `region_round_trips(region,band)`, `assert_hier_region(g,region,band,table_uri,doc_uri,page)` consistent across their consumers.

**Honesty note for the executor:** the geometry algorithms in Tasks 2–4 are the research core. Each ships a concrete implementation and a verified test, but the executor MUST treat a failing test as a signal to fix the *oracle*, never to tune a constant to this one fixture (Global Constraints). Empirically re-probe (as the plan author did) when a stage misbehaves.
