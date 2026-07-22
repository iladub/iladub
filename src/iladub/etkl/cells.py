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

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        return (self.x0, self.top, self.x1, self.bottom)


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

    A word on line i+1 is a wrap-continuation of the cell above iff ALL hold:
      - (cond 2) it lands in a leaf column already open on the anchor line
        (``cols_j ⊆ open``) — a SOUND structural test,
      - (cond 3) line i+1 occupies FEWER columns than the anchor
        (``len(cols_j) < len(anchor)``), i.e. it does not tile a fresh full row —
        a SOUND structural test,
      - (gap) the vertical gap to the preceding line is strictly less than ``lead``,
        the median of the document's own inter-line gaps.

    §8 gate — PROCEDURAL, not NEURAL (B3, 2026-07-22).  The wrap-vs-row-pitch boundary
    is ``lead`` — a DERIVED statistic (the median gap, adaptive by construction, like
    ``_median_pitch``), carrying NO tuned constant.  The previous ``lead * 0.9`` margin
    WAS fixture-tuned (its docstring reasoned in specific point magnitudes) and is
    retired: an empirical probe showed the bare ``gap < lead`` passes every fixture,
    whereas dropping the gap entirely collapses the pivot's body rows — so the adaptive
    gap is load-bearing but the magic 0.9 was not.  Conditions 2/3 are the sound
    structural filter that keeps only partial subset lines as candidates (a full row can
    never be a continuation regardless of gap), which is why relaxing 0.9→1.0 is safe:
    it only lets a partial sub-line whose gap is just under the pitch (0.9·lead–lead) be
    recognised as the continuation it structurally already is.  See
    ``docs/superpowers/specs/2026-07-22-b3-wrap-continuation-procedural-design.md`` for
    the classification + the accepted jitter tradeoff (a distribution-aware bimodal split
    is deferred until a real jittery document demonstrates the need — no synthetic fixture).
    The ultimate guard against a mis-grouping remains the downstream round-trip and SHACL
    validation, not this threshold alone.
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
        # Gate: gap < lead (the adaptive median inter-line gap). PROCEDURAL, no tuned
        # constant — see the docstring for why the retired 0.9 margin was fixture-tuned.
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
