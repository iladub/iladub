"""regions — classify a band into a table kind and assign its words to cells.

The kind gate is HEADER REGULARITY, not raw tiling: a merged header collapses
the profiled grid (infer_leaf_grid reads a 7-column pivot as 5), and under that
coarse grid every word still sits inside a span — so 'does every line tile?'
returns True for the pivot and would silently assert a wrong table. Instead a
band is a RECORD_TABLE only if its header line has exactly `ncols` words, the
i-th within column i's span (one clean label per column).

The kind decision itself is a SPARQL derivation (AXIOM) over the classifygraph
evidence graph (vocab/queries/classify-kind.rq); infer_leaf_grid/_word_in_column
stay PROCEDURAL geometry feeding that graph. The multi-word-header escape still
escalates to UNSUPPORTED (a deferred NEURAL increment), unchanged by the rewire.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .bands import Band
from .geometry import Word, COORD_EPS
from .grid import LeafGrid, infer_leaf_grid
from .classifygraph import classify_evidence, run_kind, CLASSIFY_KIND_RQ, TAB


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


_KIND = {
    str(TAB.RecordTableKind): RegionKind.RECORD_TABLE,
    str(TAB.UnsupportedTableKind): RegionKind.UNSUPPORTED_TABLE,
    str(TAB.NonTableKind): RegionKind.NON_TABLE,
}


def _reason(kind, band, grid, nhw, first_bad):
    """Rebuild the exact legacy reason string from the SPARQL-derived kind + scalars."""
    if kind is RegionKind.NON_TABLE:
        return "fewer than 2 lines" if len(band.lines) < 2 else "fewer than 2 columns"
    if kind is RegionKind.RECORD_TABLE:
        return "flat single-level header"
    # UNSUPPORTED_TABLE
    if nhw != grid.ncols:
        return f"header has {nhw} words but {grid.ncols} columns"
    w = sorted(band.lines[0].words, key=lambda w: w.x0)[first_bad]
    return f"header word {w.text!r} is not aligned 1:1 with column {first_bad}"


def classify(band: Band) -> ClassifiedRegion:
    # PROCEDURAL guard (extraction safety + grid-field fidelity, NOT a kind decision):
    # infer_leaf_grid is undefined on a <2-line band and today's NON_TABLE(<2 lines)
    # branch returns grid=None. The KIND is still derived from tab:lineCount in SPARQL.
    grid = infer_leaf_grid(band) if len(band.lines) >= 2 else None
    kind_iri, nhw, first_bad = run_kind(str(CLASSIFY_KIND_RQ), classify_evidence(band, grid))
    kind = _KIND[kind_iri]
    reason = _reason(kind, band, grid, nhw, first_bad)
    cells = assign_cells(band, grid) if kind is RegionKind.RECORD_TABLE else ()
    return ClassifiedRegion(kind, band, grid, cells, reason)
