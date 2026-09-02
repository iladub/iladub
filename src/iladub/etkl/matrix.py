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
from .regions import column_of
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

    Uncarried-ink guard (spec § 2 B, § 3.2): a closed-world completeness check —
    "every header word over a DATA column is carried by exactly one node" — kept
    PRODUCER-SIDE under CLAUDE.md § "Producer-side guards vs the membrane" because
    the membrane cannot enforce it: a word that wins no column is never emitted as a
    node, so the dropped ink never enters the graph for any shape to see. Refuses
    (returns None) when a label whose centre falls in a DATA column has an index that
    is not a key of that level's `assign` — i.e. it won no column and so becomes no
    node. The test is on the label INDEX, never on its text: header texts repeat both
    across levels and WITHIN one level (apple p0 L1 is `June 27, | June 28, | June 27,
    | June 28,`), so a text-subset test lets a duplicate-text label that wins nothing
    pass on its twin's node — dropping its ink silently, the exact CLAUDE.md §7
    violation this guard exists to refuse. A label centred in a STUB column is exempt
    (WHO's `Year: Month`, spec § 1.5) — the guard is scoped to `data_cols` only.
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
        for j, (_, x_center, _) in enumerate(labels):        # the uncarried-ink guard
            if j not in assign and column_of(x_center, b) in data_cols:
                return None
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
    """A matrix candidate: a multi-level column header (>=2 header lines, counted at the
    DERIVED matrix body start, not the type split — spec § 3.1, controller ruling 2026-09-02
    task 3b) over a clean text-stub | numeric-data split. (The caller has already established
    the region is UNSUPPORTED_TABLE.) The type split can undercount a matrix's own header
    levels (apple p1 band 2, spec § 8: type split 1, derived start 2) whenever a header line
    carries no stub cell and is typed body by `header_body_split`; `matrix_body_start` is >=
    `split` always, so this widens candidacy, never narrows it."""
    grid = recover_leaf_grid(band)
    if grid.ncols < 3:
        return False
    split = header_body_split(band, grid)
    if split is None:
        return False
    k = stub_data_split(band, grid)
    if k is None:
        return False
    body_start = matrix_body_start(band, grid, split, k)
    return body_start is not None and body_start >= 2


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
    """Chain the stages into a MatrixRegion (or None). Order of operations: see the module
    docstring, spec § 3.3 — stated once there and not restated here. Mirror of
    classify_row_hier, with a proximity column tree over the data columns as the extra
    axis.

    The `< 2` header-level-count gate is tested against the DERIVED `matrix_body_start`, not
    against the type `split` (spec § 3.1, controller ruling 2026-09-02 task 3b): `split is
    None` still short-circuits before `k` is derived (nothing to widen without a type split at
    all), but a type split of 0 or 1 no longer refuses a band whose stub-bearing body starts
    at line >= 2 (apple p1 band 2, spec § 8)."""
    from .rows import logical_rows
    from .rowheaders import infer_row_header_tree
    grid = recover_leaf_grid(band)
    if grid.ncols < 3:
        return None
    split = header_body_split(band, grid)
    if split is None:
        return None
    k = stub_data_split(band, grid)
    if k is None:
        return None
    stub_cols = tuple(range(k))
    data_cols = tuple(range(k, grid.ncols))
    body_start = matrix_body_start(band, grid, split, k)
    if body_start is None or body_start < 2:
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
