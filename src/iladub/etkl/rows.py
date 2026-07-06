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
