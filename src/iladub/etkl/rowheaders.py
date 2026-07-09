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
