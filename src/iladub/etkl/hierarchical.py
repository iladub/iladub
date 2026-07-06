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


def classify_hierarchical(band: Band) -> HierRegion | None:
    """Chain all maker stages; return None (escalate) if any stage returns None.

    Pipeline:
      1. recover_leaf_grid  — stable leaf-column grid excluding spanning header rows.
      2. header_body_split  — first line at/after which ≥1 column is all-numeric.
      3. infer_header_tree  — header nodes with column-span + parent links.
      4. logical_rows       — body row bands keyed off an anchor column.

    A single-line band or a grid with fewer than 2 columns is escalated immediately
    (no meaningful header/body distinction possible).
    """
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
