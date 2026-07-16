"""rowheaders — the vertical mirror of headers.py: a row-header tree from stub columns.

Stub columns (leading text columns, left of the numeric data) form the row-header
tree. Each stub column is a level; a stub cell's ROW-span is the blank-below
(forward-fill) run — its row down to (excluding) the next non-blank cell in that
column. Blank-below = ditto-grouping is a documented reading CONVENTION (the mirror
of Loop 2's centered-merge = column-span); the row SHACL + per-cell round-trip
certify the resulting structure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .bands import Band
from .grid import LeafGrid
from .headers import header_body_split
from .regions import column_of


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


@dataclass(frozen=True)
class RowHierRegion:
    grid: LeafGrid
    tree: tuple[RowHeaderNode, ...]
    leaf_rows: tuple
    stub_cols: tuple[int, ...]
    data_cols: tuple[int, ...]
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
