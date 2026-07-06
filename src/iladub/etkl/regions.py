"""regions — classify a band into a table kind and assign its words to cells.

The kind gate is HEADER REGULARITY, not raw tiling: a merged header collapses
the profiled grid (infer_leaf_grid reads a 7-column pivot as 5), and under that
coarse grid every word still sits inside a span — so 'does every line tile?'
returns True for the pivot and would silently assert a wrong table. Instead a
band is a RECORD_TABLE only if its header line has exactly `ncols` words, the
i-th within column i's span (one clean label per column).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .bands import Band
from .geometry import Word, COORD_EPS
from .grid import LeafGrid, infer_leaf_grid


class RegionKind(Enum):
    RECORD_TABLE = "RECORD_TABLE"
    UNSUPPORTED_TABLE = "UNSUPPORTED_TABLE"
    NON_TABLE = "NON_TABLE"


@dataclass(frozen=True)
class Cell:
    row: int                      # 0 = header line, 1..N = data lines
    col: int
    words: tuple[Word, ...]

    @property
    def text(self) -> str:
        return " ".join(w.text for w in sorted(self.words, key=lambda w: w.x0))

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        return (min(w.x0 for w in self.words), min(w.top for w in self.words),
                max(w.x1 for w in self.words), max(w.bottom for w in self.words))


@dataclass(frozen=True)
class ClassifiedRegion:
    kind: RegionKind
    band: Band
    grid: LeafGrid | None
    cells: tuple[Cell, ...]
    reason: str


def column_of(x_center: float, boundaries: Sequence[float]) -> int:
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= x_center < boundaries[i + 1]:
            return i
    return len(boundaries) - 2


def assign_cells(band: Band, grid: LeafGrid) -> tuple[Cell, ...]:
    b = grid.boundaries
    out: list[Cell] = []
    for row, line in enumerate(band.lines):
        by_col: dict[int, list[Word]] = {}
        for w in line.words:
            by_col.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        for col, ws in sorted(by_col.items()):
            out.append(Cell(row, col, tuple(ws)))
    return tuple(out)


def _word_in_column(w: Word, col: int, boundaries: Sequence[float]) -> bool:
    return w.x0 >= boundaries[col] - COORD_EPS and w.x1 <= boundaries[col + 1] + COORD_EPS


def classify(band: Band) -> ClassifiedRegion:
    if len(band.lines) < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, None, (), "fewer than 2 lines")
    grid = infer_leaf_grid(band)
    if grid.ncols < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, grid, (), "fewer than 2 columns")
    header = band.lines[0]
    b = grid.boundaries
    # A flat record header must have exactly one single-word label per column.
    # This is a deliberate SAFETY proxy, not an arbitrary limit: a multi-word
    # header label is geometrically indistinguishable from two columns whose
    # gutter collapsed (see wide_cell_table_pdf), so admitting multi-word headers
    # would risk silently asserting a merged-column table. Multi-word / multi-level
    # headers are therefore escalated by design (a future field-of-possibles increment).
    # header regularity: exactly ncols words, the i-th (left-to-right) within column i
    if len(header.words) != grid.ncols:
        return ClassifiedRegion(
            RegionKind.UNSUPPORTED_TABLE, band, grid, (),
            f"header has {len(header.words)} words but {grid.ncols} columns")
    for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
        if not _word_in_column(w, i, b):
            return ClassifiedRegion(
                RegionKind.UNSUPPORTED_TABLE, band, grid, (),
                f"header word {w.text!r} is not aligned 1:1 with column {i}")
    return ClassifiedRegion(RegionKind.RECORD_TABLE, band, grid,
                            assign_cells(band, grid), "flat single-level header")
