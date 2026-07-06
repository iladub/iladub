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
