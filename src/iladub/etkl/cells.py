"""cells — the shared cell-evidence intermediate + leaf-grid recovery.

The geometry adapter produces SourceCells; recover_leaf_grid finds the TRUE
leaf grid by excluding spanning (merged-header) rows, which otherwise fill
gutters and collapse the column count (a 7-col pivot reads as 5 over all rows).
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .bands import Band
from .geometry import Word
from .grid import LeafGrid, infer_leaf_grid
from .regions import column_of


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


def _cell_from(words: list[Word], page: int, span_cols: int = 1) -> "SourceCell":
    return SourceCell(
        " ".join(w.text for w in sorted(words, key=lambda w: w.x0)),
        min(w.x0 for w in words), min(w.top for w in words),
        max(w.x1 for w in words), max(w.bottom for w in words),
        words[0].page if hasattr(words[0], "page") else page,
        tuple(words), span_cols,
    )


def group_wrapped(band: Band, grid: LeafGrid) -> tuple[tuple["SourceCell", ...], ...]:
    """Group words into per-line SourceCells, merging wrap-continuations.

    A word on line i+1 is a wrap-continuation of the cell above iff:
      - it lands in the same leaf column as a cell already open on the anchor line,
      - the vertical gap to the preceding line is strictly less than the median
        inter-line gap (i.e. the continuation is tighter than the typical row pitch),
      - and line i+1 does not itself tile a fresh full row (it has fewer occupied
        columns than the anchor).

    Using ``gap < lead`` (strictly less than the median) is the structural oracle:
    wrap-continuation lines are typeset tighter than row-to-row spacing.  Using
    ``gap <= lead * k`` for k > 1 (as in the original brief) incorrectly admits
    rows whose spacing equals the median, causing body rows with missing data cells
    to be absorbed into the row above.
    """
    b = grid.boundaries
    lines = list(band.lines)
    if not lines:
        return ()
    tops = [ln.top for ln in lines]
    gaps = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    lead = median([g for g in gaps if g > 0]) if any(g > 0 for g in gaps) else 0.0

    # Build per-line column maps: {col_index: [words]}
    per_line: list[dict[int, list[Word]]] = []
    for ln in lines:
        by_col: dict[int, list[Word]] = {}
        for w in ln.words:
            by_col.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        per_line.append(by_col)

    merged_into: list[dict[int, list[Word]]] = [dict() for _ in lines]
    consumed = [False] * len(lines)

    for i, by_col in enumerate(per_line):
        if consumed[i]:
            continue
        # Seed the anchor line's accumulated words.
        for col, words in by_col.items():
            merged_into[i].setdefault(col, []).extend(words)
        # Pull wrap-continuations from subsequent contiguous lines.
        # Oracle: gap < lead — continuation lines are typeset tighter than row pitch.
        j = i + 1
        while j < len(lines) and (tops[j] - tops[j - 1]) < lead:
            cols_j = per_line[j]
            # Continuation only if every word on line j sits in a column already open
            # on the anchor, AND line j does not tile a fresh full row (fewer cols).
            if (cols_j
                    and all(c in merged_into[i] for c in cols_j)
                    and len(cols_j) < len(by_col)):
                for col, words in cols_j.items():
                    merged_into[i][col].extend(words)
                consumed[j] = True
                j += 1
            else:
                break

    rows: list[tuple["SourceCell", ...]] = []
    for i in range(len(lines)):
        if consumed[i]:
            continue
        cells = tuple(
            _cell_from(ws, lines[i].words[0].page)
            for col, ws in sorted(merged_into[i].items())
        )
        rows.append(cells)
    return tuple(rows)
