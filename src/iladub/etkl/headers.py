"""headers — header/body boundary (type-homogeneity) + header-tree inference.

The 2-D round-trip proves faithfulness but not uniqueness; type-homogeneity pins
where the header ends and the body begins. The tree is read from centered spans
over the leaf grid; refinement/coverage are certified downstream by SHACL.

Key design decision: group_wrapped is called on the FULL band (not just the header
sub-band) so that the body-row pitch governs the wrap-continuation threshold. With
only the header lines, the lead (median gap) ≈ 14 pt and the threshold (0.9×lead)
≈ 12.6 pt is below the actual sub-header → (SI) gap (≈ 13 pt), leaving (SI) as a
spurious third level that would fail CoverageShape / RefinementShape in Task 7.
Using the full band, lead ≈ 18 pt (body row pitch), threshold ≈ 16.2 pt, and
13 pt < 16.2 pt so (SI) is correctly absorbed into the sub-header cells.

Column-span oracle: merged PDF headers are centered over their span. The physical
text extent may not reach the rightmost column boundary (a common rendering artifact
when the text is narrower than the span it covers). We symmetrize around the cell's
center column: if the left span (cc − lc) exceeds the right span (rc − cc), we
extend rc to cc + (cc − lc), and vice versa. This is an oracle over the centering
invariant of merged headers, not a constant tuned to a specific fixture.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from typing import Sequence

from .bands import Band
from .cells import group_wrapped
from .grid import LeafGrid
from .regions import column_of


def is_numeric(s: str) -> bool:
    """True if s (after stripping commas and percent signs) parses as a finite float.

    Strings that parse as float but are not finite numbers — "nan", "inf", "-inf" —
    return False. These are common missing-data sentinels that must not be treated as
    numeric data values (e.g. "nan" would otherwise pass float() and be misclassified
    as a body-column value, corrupting the header/body split).
    """
    t = re.sub(r"[,%]", "", s.strip())
    if not t:
        return False
    try:
        return math.isfinite(float(t))
    except ValueError:
        return False


def _col_values(lines, grid: LeafGrid, start: int) -> dict[int, list[str]]:
    """Per leaf column, list of non-empty cell texts on lines[start:]."""
    b = grid.boundaries
    cols: dict[int, list[str]] = {i: [] for i in range(grid.ncols)}
    for ln in lines[start:]:
        seen: dict[int, list[str]] = {}
        for w in ln.words:
            seen.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w.text)
        for i, texts in seen.items():
            cols[i].append(" ".join(texts))
    return cols


def _grid_cells(band, grid):
    """(line, col, joined-text) for every populated cell — the full-grid analogue of _col_values
    (same column word-grouping), used to build the typed-cell evidence graph."""
    b = grid.boundaries
    out = []
    for r, ln in enumerate(band.lines):
        seen = {}
        for w in ln.words:
            seen.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w.text)
        for c, texts in seen.items():
            out.append((r, c, " ".join(texts)))
    return out


def header_body_split(band: Band, grid: LeafGrid) -> int | None:
    """First line index at/after which >=1 leaf column is all-numeric.

    Iterates candidate splits from line 1 onward. A split is accepted when at
    least one leaf column has exclusively numeric text from that line to the end
    of the band (the label→data transition). Returns None if no such split exists
    (e.g. an all-text table) → caller escalates.

    Design note — numeric-homogeneity as the operative proxy:
    This function uses numeric-column homogeneity as the intentional operative proxy
    for the spec's "type-homogeneous" header/body boundary: returns the first line
    index at/after which at least one leaf column is all-numeric down the remaining
    lines. This correctly yields None-escalation for all-text tables (no column ever
    homogenizes to numeric), which is the desired behavior — the caller (or downstream
    SHACL) handles the ambiguity rather than guessing a boundary.

    Declarative derivation (loop B2a): the typed-cell evidence graph + header-body-split.rq.
    """
    from . import celltype
    import os
    g = celltype.grid_evidence(_grid_cells(band, grid), grid.ncols)
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "header-body-split.rq")
    return celltype.run_scalar(q, g)


@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None
    center_x: float | None = None


def _covers_for_cell(cell, b: Sequence[float]) -> tuple[int, ...]:
    """Leaf columns covered by a spanning header cell.

    Uses center-of-mass symmetrization: find the center column from the cell's
    midpoint, find the leftmost and rightmost columns from the physical x-extent,
    then extend the shorter side to match the longer. This oracle handles the
    common PDF artifact where the text of a merged header doesn't physically
    reach all the column boundaries it logically spans (because the text is
    narrower than the full span width).

    For single-column cells the left and right extents are equal and no
    extension occurs.

    Design note — centered-merge assumption:
    This symmetrization assumes merged headers are centered over their span
    (i.e. the PDF was authored with "Merge & Center"). A narrow centered label
    correctly recovers its full column run. Corner cases that are NOT in scope:
    - A single word that merely straddles one gutter (an anomaly) may be
      over-spanned by one column. This is caught downstream by NoOverlapShape /
      CoverageShape and correctly ESCALATES — it is not asserted wrong.
    - A left- or right-aligned merge (not centered) is out of scope for this
      oracle; such alignment is uncommon in formal report tables.
    Do NOT add a `cc != lc and cc != rc` guard: it would block the pivot's
    "Prior Visit" header (cc=5, lc=4, rc=5) from extending to col 6.
    """
    ncols = len(b) - 1
    cx = (cell.x0 + cell.x1) / 2.0
    cc = column_of(cx, b)                     # center column
    lc = column_of(cell.x0 + 0.1, b)         # leftmost column touched by text
    rc = column_of(cell.x1 - 0.1, b)         # rightmost column touched by text

    # Symmetrize: if one side extends further than the other, mirror it.
    left_span = cc - lc
    right_span = rc - cc
    if left_span > right_span:
        rc = min(ncols - 1, cc + left_span)
    elif right_span > left_span:
        lc = max(0, cc - right_span)

    return tuple(range(lc, rc + 1))


def _median_pitch(b: Sequence[float]) -> float:
    """Median data-column width (pitch) in points — the gutter-relative unit for the
    centering tolerance (NOT a fixture-tuned constant). Columns are b[i]..b[i+1];
    column 0 is the stub and is excluded."""
    widths = sorted(b[i + 1] - b[i] for i in range(1, len(b) - 1))
    if not widths:
        return (b[-1] - b[0]) if len(b) >= 2 else 1.0
    return widths[len(widths) // 2]


def _span_center(run: Sequence[int], b: Sequence[float]) -> float:
    """The x-center of a contiguous column run = the ENDPOINT midpoint of its x-range,
    (b[run[0]] + b[run[-1]+1]) / 2 — the true visual center of the span (spec §4).

    (A median of per-column midpoints was tried and REJECTED: for unequal-width columns
    the median collapses to the middle column's midpoint, which sits far from the visual
    center, so the resolver picks a too-narrow run and silently drops a flanking column.
    The endpoint midpoint is the geometric center for any column widths.)"""
    return (b[run[0]] + b[run[-1] + 1]) / 2.0


def _centered_run(center_x: float, avail: set[int], b: Sequence[float],
                  must_include: set[int]) -> tuple[int, ...]:
    """The contiguous column run [lo..hi] (lo >= 1) that (a) lies entirely within
    `avail`, (b) contains every column in `must_include` (the node's ink columns),
    and (c) is best-centered on the label ink center by ENDPOINT midpoint (`_span_center`).

    Selection: among the qualifying runs, take those whose center is within a quarter of
    the median column pitch of the closest run's center (a TIE-BAND: runs that close are
    indistinguishable given gutter-recovery noise), and pick the WIDEST of them (then
    closest, then leftmost). The tie-band + widest recovers the full span for a short
    centered label (e.g. a single ink column tied with its 3-column span -> the span).
    The band is gutter-relative (a fraction of the measured pitch), NOT a constant tuned
    to any fixture.

    KNOWN LIMITATION (deferred to B1.2 — see
    docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md):
    absorbing an adjacent column shifts the endpoint center by (that column's width)/2, so
    a flanking standalone column NARROWER than half the median pitch still falls inside the
    band and is over-absorbed. This is no worse than the prior greedy repair (which absorbed
    an adjacent orphan of ANY width); a comparable-or-wider standalone column is correctly
    left out. Tightening the per-column absorption test (or escalating the narrow-flank case)
    is a B1.2 follow-up.

    Returns () if none qualifies (e.g. must_include is empty or not contiguous in avail)."""
    n = len(b) - 1
    cands: list[tuple[tuple[int, ...], float, int]] = []   # (run, |center-ink|, width)
    for lo in range(1, n):
        for hi in range(lo, n):
            run = tuple(range(lo, hi + 1))
            run_set = set(run)
            if not run_set <= avail:
                continue
            if not must_include <= run_set:
                continue
            cands.append((run, abs(_span_center(run, b) - center_x), hi - lo))
    if not cands:
        return ()
    best_d = min(d for _, d, _ in cands)
    band = 0.25 * _median_pitch(b)
    near = [c for c in cands if c[1] - best_d <= band]
    near.sort(key=lambda z: (-z[2], z[1], z[0][0]))        # widest, then closest, then leftmost
    best_run = near[0][0]
    return best_run


def repair_coverage(nodes: list[HeaderNode], grid) -> list[HeaderNode]:
    """Resolve each coarse (non-leaf) spanning node to the contiguous run of AVAILABLE
    columns (its own + orphans, never another node's) whose x-midpoint is closest to
    the node's label ink center. This applies the centering (Merge & Center) convention
    consistently: a short label centered over its full span still recovers that span
    (Region, Q-groups), while a label centered over only PART of the columns stops at
    its centered run instead of greedily absorbing the neighbour (the B1.1 fix).

    Falls back to the pre-B1.1 additive greedy extension for any node lacking geometry
    (`center_x is None`) so non-geometric callers are unchanged.

    Accepts `grid` as either a `LeafGrid` (full geometric path) or a plain `int`
    (legacy ncols — backward-compatible for callers that have no boundary data;
    the centering path is silently skipped since `center_x` is None in that case).
    """
    if not nodes:
        return nodes
    if isinstance(grid, int):
        b = None
        ncols = grid
    else:
        b = grid.boundaries
        ncols = grid.ncols
    out = list(nodes)
    max_level = max(n.level for n in out)
    for lvl in range(max_level):                      # non-leaf levels only
        for i, n in enumerate(out):
            if n.level != lvl:
                continue
            level_cols: set[int] = set()
            for m in out:
                if m.level == lvl:
                    level_cols |= set(m.covers)
            orphans = {c for c in range(1, ncols) if c not in level_cols}
            avail = set(n.covers) | orphans
            if b is not None and n.center_x is not None and n.covers:
                run = _centered_run(n.center_x, avail, b, must_include=set(n.covers))
                if run and set(run) != set(n.covers):
                    out[i] = replace(n, covers=tuple(run))
            else:
                # legacy additive greedy extension (no geometry available)
                for c in sorted(orphans):
                    if n.covers and (max(n.covers) == c - 1 or min(n.covers) == c + 1):
                        out[i] = replace(out[i], covers=tuple(sorted(set(out[i].covers) | {c})))
    return out


def merge_tiling_ok(tree: Sequence[HeaderNode], grid: LeafGrid) -> bool:
    """Centering oracle for the resolved header tree. A spanning (multi-column, non-leaf)
    node is center-consistent iff its resolved span's x-midpoint is within half a column
    pitch of its label ink center. Also rejects any coarse-level column claimed by two
    nodes (overlap). A node without geometry (center_x is None) is not checked here.
    Returns False → the caller escalates MERGE_AMBIGUOUS rather than assert a guess."""
    b = grid.boundaries
    tol = 0.5 * _median_pitch(b)
    has_child = {n.parent for n in tree if n.parent is not None}
    # overlap check per level
    by_level: dict[int, list[int]] = {}
    for n in tree:
        for c in n.covers:
            by_level.setdefault(n.level, []).append(c)
    for cols in by_level.values():
        if len(cols) != len(set(cols)):
            return False                       # two nodes claim the same column at one level
    # centering check for spanning (has-children) nodes with geometry
    for i, n in enumerate(tree):
        if i in has_child and len(n.covers) > 1 and n.center_x is not None:
            mid = _span_center(tuple(sorted(n.covers)), b)   # same statistic the resolver uses
            if abs(mid - n.center_x) > tol:
                return False
    return True


def infer_header_tree(band: Band, grid: LeafGrid, body_line: int) -> tuple[HeaderNode, ...] | None:
    """Header-tree from the header lines (0..body_line-1).

    Calls group_wrapped on the FULL band so the body-row pitch (not the narrow
    header-only pitch) governs the wrap-continuation threshold — correctly absorbing
    tight (SI) lines into their parent sub-header cells rather than producing a
    spurious extra level.

    For each header row (ordered by level from top to bottom), each cell's column
    span is determined by center-of-mass symmetrization (see _covers_for_cell).
    Parent links are set to the nearest same-or-coarser node one level up whose
    covers contain this node's covers.

    Returns None if no header rows are identified (ambiguous → escalate).
    """
    b = grid.boundaries
    # Use the FULL band so lead = body-row pitch ≈ 18 pt → threshold ≈ 16.2 pt,
    # which absorbs the (SI) gap (≈ 13 pt) correctly.
    all_rows = group_wrapped(band, grid)
    body_top = band.lines[body_line].top

    # Header rows: wrapped rows whose first cell's top precedes the body line.
    # Using row[0].top (not max) is safe because header rows are compact; if the
    # first (leftmost-column) cell precedes body_top, the row is a header row.
    header_rows = [row for row in all_rows if row and row[0].top < body_top]
    if not header_rows:
        return None

    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            covers = _covers_for_cell(cell, b)
            cx = (cell.x0 + cell.x1) / 2.0
            nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))

    nodes = repair_coverage(nodes, grid)   # centering-bounded span resolution (B1.1)

    # Link each node to its nearest parent (level − 1 whose covers ⊇ this node's).
    # Break after the first match so the first qualifying parent wins deterministically
    # (nodes are ordered top-to-bottom, left-to-right, so "first" = leftmost ancestor
    # at the parent level whose covers contain this node's covers).
    linked: list[HeaderNode] = []
    for n in nodes:
        parent_idx: int | None = None
        for j, m in enumerate(nodes):
            if m.level == n.level - 1 and set(n.covers) <= set(m.covers):
                parent_idx = j
                break
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx, n.center_x))
    return tuple(linked)
