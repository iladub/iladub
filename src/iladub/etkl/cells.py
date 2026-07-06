"""cells — the shared cell-evidence intermediate + leaf-grid recovery.

The geometry adapter produces SourceCells; recover_leaf_grid finds the TRUE
leaf grid by excluding spanning (merged-header) rows, which otherwise fill
gutters and collapse the column count (a 7-col pivot reads as 5 over all rows).
"""
from __future__ import annotations

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
    """Leaf grid = the most-stable column count across row-suffixes.

    Spanning or verbose header rows cause instability at the top of the suffix
    range — either collapsing the column count (few wide clusters) or inflating
    it (many short tokens whose inter-word gaps look like gutters). The stable
    leaf count is the MODE (most frequent column count) across all qualifying
    suffixes of ≥2 rows. Among suffixes achieving the modal count, the longest
    (most rows = strongest gutter evidence) is returned. Falls back to
    infer_leaf_grid(band) if nothing qualifies (e.g. a single-line band).
    """
    lines = list(band.lines)
    results: list[tuple[int, int, LeafGrid]] = []  # (ncols, n_rows, grid)
    for start in range(max(1, len(lines) - 1)):
        sub = lines[start:]
        if len(sub) < 2:
            break
        try:
            g = infer_leaf_grid(Band(tuple(sub), min(l.top for l in sub), max(l.bottom for l in sub)))
        except ValueError:
            continue
        results.append((g.ncols, len(sub), g))
    if not results:
        return infer_leaf_grid(band)
    # Modal column count — the count that most suffixes agree on.
    # Tie-break toward the higher count (finer grid = more columns revealed).
    freq: dict[int, int] = {}
    for ncols, _, _ in results:
        freq[ncols] = freq.get(ncols, 0) + 1
    modal_count = max(freq, key=lambda k: (freq[k], k))
    # Among all suffixes achieving the modal count, take the longest (strongest evidence).
    best = max((r for r in results if r[0] == modal_count), key=lambda r: r[1])
    return best[2]
