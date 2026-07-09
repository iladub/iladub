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
