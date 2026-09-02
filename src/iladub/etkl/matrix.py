"""matrix — compile a cross-tab (hierarchical columns + stub row axis) by composing
Loop 2's column machinery and Loop 5's row machinery.

The one non-composed piece: infer_header_tree recovers merged spans from a parent
label's TEXT EXTENT, which under-covers short cross-tab labels (Q1 over a wide
numeric group). infer_column_tree_by_proximity instead assigns each data leaf column
to its NEAREST parent-label center (Voronoi) — exact for any label width. This
assumes CENTERED parent merges (a documented convention, the mirror of Loop 2's
centered-merge and Loop 5's blank-below); the SHACL + round-trip certify the result.

Header LEVELS are the band's own lines (band.lines[:split]) — the same grouping
header_rows_of indexes — never re-derived from word tops with a tolerance of this
module's own (R45). What `split` IS, at the call site, has moved (see Order of
operations below): `classify_matrix` passes `infer_column_tree_by_proximity` the
matrix body start, not `header_body_split`'s type split.

Order of operations (spec 2026-09-02-the-body-starts-at-the-stub-design.md § 3.3), stated
once, here, and consumed by classify_matrix without restatement: grid -> type split
(header_body_split) -> stub width (stub_data_split, k) -> matrix body start
(matrix_body_start, consuming split and k unmodified) -> column tree -> leaf rows -> row
tree. `header_body_split` and its query stay the global type-transition rule;
`matrix_body_start` is the matrix-scoped refinement that moves the body start past a
stubless line without re-deriving `k`.
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


def infer_column_tree_by_proximity(band, grid, split, data_cols):
    """Column tree over the DATA columns by nearest-parent-center assignment.

    A header LEVEL IS A BAND LINE: level L is band.lines[L] for L in range(split),
    and level L's labels are exactly that line's words. The `split` argument here is
    the caller's header-level count, not necessarily `header_body_split`'s own return
    value: `classify_matrix` passes it `matrix_body_start`'s result (the matrix body
    start, spec § 3.1), which is >= `header_body_split`'s type split whenever a header
    level carries no stub cell. Either way `split` is a count of band.lines and
    header_rows_of dereferences the same integer as band.lines[body_line].top, so the
    two share one coordinate system. No tolerance is applied here — what a line is has
    already been decided, once, by the band producer.

    For each level, take that line's labels as (text, x_center, word); assign each
    data column to the nearest label center; a node covers the contiguous run
    assigned to it. Parent links: level L -> the level-(L-1) node whose covers
    contain this node's. None if a level has no labels.
    """
    b = grid.boundaries
    centers = {c: (b[c] + b[c + 1]) / 2.0 for c in data_cols}
    levels = band.lines[:split]
    if not levels:
        return None
    nodes: list[ColHeaderNode] = []
    for level, ln in enumerate(levels):
        labels = sorted(((w.text, (w.x0 + w.x1) / 2.0, w) for w in ln.words),
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


def matrix_body_start(band: Band, grid: LeafGrid, split: int, k: int) -> int | None:
    """The first cell-bearing line at/after the header/body TYPE split (`header_body_split`)
    that carries a cell in a STUB column (grid column < the stub width `stub_data_split`
    derives). AXIOM, open-world, evidence-positive: a line is body because a stub cell is
    PRESENT on it, never because something is absent (spec § 2 A). Matrix-scoped because
    "stub" is a two-axis notion that only exists once a stub|data split is derived — it does
    not belong beside `header_body_split` in headers.py, and consumes that split unmodified
    (spec § 4).

    Invariants (spec § 3.1): result >= split always; result < len(band.lines) when not None;
    equals `split` when line `split` itself already carries a stub cell (the common case —
    every non-apple corpus band, spec § 1.5). None when no line at/after `split` has a stub
    cell (e.g. k=0, the contract's edge case, never `stub_data_split`'s own range).
    """
    from .headers import _grid_cells
    from . import celltype
    from rdflib import Literal
    from rdflib.namespace import XSD
    import os
    g = celltype.grid_evidence(_grid_cells(band, grid), grid.ncols)
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "matrix-body-start.rq")
    return celltype.run_scalar(q, g, bindings={
        "split": Literal(split, datatype=XSD.integer),
        "k": Literal(k, datatype=XSD.integer),
    })


def is_matrix_candidate(band: Band) -> bool:
    """A matrix candidate: a multi-level column header (>=2 header lines) over a
    clean text-stub | numeric-data split. (The caller has already established the
    region is UNSUPPORTED_TABLE.)"""
    grid = recover_leaf_grid(band)
    if grid.ncols < 3:
        return False
    split = header_body_split(band, grid)
    return split is not None and split >= 2 and stub_data_split(band, grid) is not None


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
    """Chain the stages into a MatrixRegion (or None), in order (spec § 3.3): grid -> type
    split -> k -> matrix body start -> column tree -> leaf rows -> row tree. Mirror of
    classify_row_hier, with a proximity column tree over the data columns as the extra
    axis."""
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
    body_start = matrix_body_start(band, grid, split, k)
    if body_start is None:
        return None
    col_tree = infer_column_tree_by_proximity(band, grid, body_start, data_cols)
    if col_tree is None:
        return None
    leaf_rows = logical_rows(band, grid, band.lines[body_start].top)
    if not leaf_rows:
        return None
    row_tree = infer_row_header_tree(band, grid, stub_cols, leaf_rows)
    if row_tree is None:
        return None
    return MatrixRegion(grid, col_tree, tuple(row_tree), tuple(leaf_rows),
                        stub_cols, data_cols, body_start)
