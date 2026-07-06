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

import re
from dataclasses import dataclass
from typing import Sequence

from .bands import Band
from .cells import group_wrapped
from .grid import LeafGrid
from .regions import column_of


def is_numeric(s: str) -> bool:
    """True if s (after stripping commas and percent signs) parses as a float."""
    t = re.sub(r"[,%]", "", s.strip())
    if not t:
        return False
    try:
        float(t)
        return True
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


def header_body_split(band: Band, grid: LeafGrid) -> int | None:
    """First line index at/after which >=1 leaf column is all-numeric.

    Iterates candidate splits from line 1 onward. A split is accepted when at
    least one leaf column has exclusively numeric text from that line to the end
    of the band (the label→data transition). Returns None if no such split exists
    (all-text table or ambiguous) → caller escalates.
    """
    lines = list(band.lines)
    for start in range(1, len(lines)):
        cols = _col_values(lines, grid, start)
        numeric_cols = [i for i, vs in cols.items() if vs and all(is_numeric(v) for v in vs)]
        if numeric_cols:
            return start
    return None


@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None


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
            nodes.append(HeaderNode(lvl, covers, cell.text, None))

    # Link each node to its nearest parent (level − 1 whose covers ⊇ this node's).
    linked: list[HeaderNode] = []
    for n in nodes:
        parent_idx: int | None = None
        for j, m in enumerate(nodes):
            if m.level == n.level - 1 and set(n.covers) <= set(m.covers):
                parent_idx = j
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx))
    return tuple(linked)
