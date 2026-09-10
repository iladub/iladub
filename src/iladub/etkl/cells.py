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
from .grid import LeafGrid, _rule_boundaries, infer_leaf_grid
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
    """Leaf grid = the author's vertical rules when the words confirm them, else the
    most-stable column count across row-suffixes.

    RULES ARE AUTHORITY. If any row-suffix's words strictly tile the band's rules, that
    rule-derived grid is returned immediately — the author drew those separators, so there is
    nothing to vote on (CLAUDE.md §0: recover the author's structure, do not re-derive it).
    Walking suffixes matters: a single leaked caption word straddling a rule vetoes the rules
    for the WHOLE band, but a suffix that skips it accepts them (measured on a real report:
    one word of 472).

    WHITESPACE FALLBACK (unchanged): spanning or verbose header rows cause instability at the
    top of the suffix range — either collapsing the column count (few wide clusters) or
    inflating it (many short tokens whose inter-word gaps look like gutters). The stable leaf
    count is the MODE (most frequent column count) across all qualifying suffixes of >=2 rows.
    Among suffixes achieving the modal count, the longest (most rows = strongest gutter
    evidence) is returned. Falls back to infer_leaf_grid(band) if nothing qualifies (e.g. a
    single-line band).

    KNOWN DEFECT in that mode, deliberately NOT fixed here (residue R3): the suffixes are
    NESTED SUBSETS of one another, not independent witnesses, so the vote systematically
    over-weights the degraded tail. Measured on a real report: the correct grid was found by
    the longest suffix, then outvoted 35-to-16 by shorter ones. Ruled documents now route
    around this; ruleless ones still hit it.
    """
    lines = list(band.lines)
    results: list[tuple[int, int, LeafGrid]] = []  # (ncols, n_rows, grid)
    for start in range(max(1, len(lines) - 1)):
        sub = lines[start:]
        if len(sub) < 2:
            break
        # Carry EVERY boundary-bearing field onto the sub-band. Dropping `rules` here is the
        # exact defect loop D fixed (it silently disabled the whole border-aware path), and
        # dropping `column_xs` recreated it for loop G's derived boundaries — the refinement
        # reached rule_aware_lines but never the grid, so 17 columns compiled as 15. If a new
        # boundary field is ever added to Band, add it here too.
        sub_band = Band(tuple(sub), min(l.top for l in sub), max(l.bottom for l in sub),
                        band.rules, band.hrules, band.column_xs)
        try:
            g = infer_leaf_grid(sub_band)
        except ValueError:
            continue
        if _rule_boundaries(sub_band) is not None:
            return g               # author's rules confirmed by the words -> authority, no vote
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
      - (gap) the vertical gap to the preceding line is strictly less than
        ``tightest_row_gap``, the minimum gap over the band's CERTAIN pairs (below),
        falling back to ``lead`` — the median inter-line gap — when the band certifies
        no row boundary at all,
      - (hrule veto) no author-drawn horizontal rule (``band.hrules``) falls between the
        two lines. Measured on a real report: 35/54 consecutive line pairs carry an hrule —
        every genuine row boundary, including every suppressed-key-data/subtotal boundary —
        and the 19 that do not are exactly the genuine wraps. The author's rule outranks the
        derived gap heuristic (the row-axis twin of loops D/G's rule-outranks-heuristic
        pattern). HONEST LIMIT: an unruled band (no hrules at all) keeps the fusion defect —
        the veto is a presence test, inert where there is nothing to test.

    THE TIGHTEST CERTAIN BOUNDARY ([[R208]], 2026-09-10;
    ``docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md`` § 3).
    Conditions 2/3 and the hrule veto are sound: a consecutive pair (j-1, j) that FAILS the
    structural test — line j tiles as many columns, or a column line j-1 left closed — or that
    an author hrule separates, is a row boundary by construction. Those are the band's
    *certain pairs*, and their gaps are measurements of what a row boundary looks like in this
    band, taken by the same instrument on the same page with the same noise. A candidate
    continues the line above iff ``gap < min(gap over the certain pairs)`` — a wrap must be
    tighter than EVERY row boundary the band certifies. That is the evidence-positive reading
    CLAUDE.md § 8 asks for: a merge is asserted only on positive evidence that the gap is not
    a row gap; a gap indistinguishable from an observed row boundary is a row. The previous
    gate, ``gap < lead`` (B3, 2026-07-22), asserted a wrap whenever the gap was tighter than
    the TYPICAL row, which on a uniform-pitch table is decided by coordinate noise: on
    graincorp-stem every body gap is 6.48 pt and so is the median, and the seven at-pitch
    partial lines (data rows whose month cell the author left blank) fell ~2e-5 pt either
    side of it — 3 welded, 4 did not (``scripts/at_pitch_weld_probe.py``). Under this rule
    all 13 of the document's at-pitch candidates are refused, the corpus's 2 genuine wraps
    still merge, and 0 of its 30 candidates change verdict otherwise (spec § 7).

    Certain pairs are RAW consecutive pairs, enumerated once before the loop (the loop's own
    structural test is anchor-relative, against ``merged_into[i]``), so the threshold is a
    property of the band, not of the loop's state. A vetoed pair counts as certified.

    Where the band has no certain pair — every line a strict subset partial of the one
    above — the rule has no minimum to take and falls back to ``lead``: with nothing
    certified, the median is a comparison among the candidates themselves, the only evidence
    the band offers. Measured: 3 corpus bands (bfs header blocks), byte-identical. The
    refuse-when-nothing-certified arm is named in the spec and not run.

    HONEST LIMITS (spec § 4). (a) A minimum is not jitter-robust where a median is: one
    tight certified boundary refuses every genuine wrap in ``[tightest_row_gap, lead)`` that
    ``gap < lead`` accepted. 0 of 30 corpus candidates lie there — absence on this corpus, not
    evidence of absence — and the residual falls on the side the membrane can see (a refused
    wrap is a partial row with blank cells; a wrongly accepted one is two records fused into
    one that passes tiling). (b) At uniform pitch a noise floor remains, one order of
    magnitude lower: an at-pitch candidate welds iff its gap is the tightest of every gap in
    the band — 1 in ``n_certain + 1`` under exchangeable noise, where ``gap < lead`` was 1 in
    2 — reachable only when the source's coordinates disagree below its stated precision.

    §8 gate — PROCEDURAL, inherited from B3 § 2 on the same argument. ``tightest_row_gap`` is
    a DERIVED statistic of the band (a minimum over a structurally-defined population), as
    ``lead`` was (a median): no constant, no tolerance, no margin, strict comparison. Not
    AXIOM because no evidence graph exists here — this runs on ``Line``s before
    ``classifygraph`` mints a triple; not NEURAL because the question is not "which columns
    does X span" but "is this gap a row gap", which the band's own certain pairs answer
    exactly. The retired ``lead * 0.9`` margin WAS fixture-tuned and stays retired.
    """
    b = grid.boundaries
    lines = list(band.lines)
    if not lines:
        return ()
    tops = [ln.top for ln in lines]
    gaps = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    lead = median([g for g in gaps if g > 0]) if any(g > 0 for g in gaps) else 0.0

    # THE HRULE VETO (loop H): the author's horizontal rules are the ROW DELIMITERS — the
    # row-axis twin of loops D/G's "author structure outranks the derived heuristic". A
    # suppressed-key data row and a subtotal row are both proper-subset partial rows, so
    # conditions 2/3 + gap<lead FUSE them into the record above (measured: three source lines
    # in one record, '20,000 20,000 20,000' as one cell). Measured on the same report: every
    # real row boundary carries an hrule (35/54 pairs) and every hrule-free pair is a genuine
    # wrap — so absorption across an hrule is always wrong, and absorption within an hrule-free
    # gap is exactly the wrap case this function exists for. Presence test, no constant.
    # HONEST LIMIT: unruled bands (no hrules) keep the fusion defect; the veto is inert there.
    hrule_ys = sorted({round(h.y, 2) for h in band.hrules})

    # Build per-line column maps: {col_index: [words]}
    per_line: list[dict[int, list[Word]]] = []
    for ln in lines:
        by_col: dict[int, list[Word]] = {}
        for w in ln.words:
            by_col.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        per_line.append(by_col)

    # THE CERTAIN PAIRS (R208): raw consecutive pairs that fail the structural test or are
    # hrule-vetoed are row boundaries by construction; the tightest of their gaps is the
    # threshold a wrap must beat. Enumerated once, on raw pairs, so it is a band property.
    def _vetoed(j: int) -> bool:
        return any(tops[j - 1] < y <= tops[j] for y in hrule_ys)

    def _partial_of(prev: dict[int, list[Word]], cur: dict[int, list[Word]]) -> bool:
        return bool(cur) and all(c in prev for c in cur) and len(cur) < len(prev)

    certain_gaps = [tops[j] - tops[j - 1] for j in range(1, len(lines))
                    if _vetoed(j) or not _partial_of(per_line[j - 1], per_line[j])]
    # Fallback to `lead` when the band certifies nothing — see the docstring; not a constant.
    tightest_row_gap = min(certain_gaps) if certain_gaps else lead

    merged_into: list[dict[int, list[Word]]] = [dict() for _ in lines]
    consumed = [False] * len(lines)

    for i, by_col in enumerate(per_line):
        if consumed[i]:
            continue
        # Seed the anchor line's accumulated words.
        for col, words in by_col.items():
            merged_into[i].setdefault(col, []).extend(words)
        # Pull wrap-continuations from subsequent contiguous lines.
        # Gate: gap < tightest_row_gap — tighter than every row boundary the band certifies.
        # PROCEDURAL, a derived minimum, no tuned constant — see the docstring.
        j = i + 1
        while (j < len(lines) and (tops[j] - tops[j - 1]) < tightest_row_gap
               and not _vetoed(j)):
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
