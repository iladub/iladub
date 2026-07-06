"""roundtrip — the per-cell round-trip oracle and its spatial-ASCII evidence.

Gate: a cell round-trips iff every word lies within its assigned column span
(no straddle across a gutter). The gutter (a boundary between spans) is the
oracle; there is no tuned tolerance beyond a hair's-width float epsilon.

region_round_trips: the 2-D faithfulness gate for hierarchical tables —
every measured word in the band must place into exactly one (leaf column ×
row-band or header level). A word outside the leaf grid, or in zero or more
than one row/level, fails it. This is the anti-silent-wrong gate for
hierarchical tables.

render_region_ascii: ASCII evidence surface for hierarchical regions —
renders header levels (one line per distinct level, cells centered over their
column span) then body row bands (one line per row, cells placed by x0),
separated by a rule. Legible and row-band-aware; reuses the x-scaling
approach of render_ascii.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from .bands import Band
from .geometry import COORD_EPS
from .regions import Cell


def cell_round_trips(cell: Cell, boundaries: Sequence[float]) -> bool:
    lo, hi = boundaries[cell.col], boundaries[cell.col + 1]
    return all(w.x0 >= lo - COORD_EPS and w.x1 <= hi + COORD_EPS for w in cell.words)


def region_round_trips(region, band) -> bool:
    """Every measured word must place into exactly one (leaf column × row/level).

    Structural gates (no tuned constants):
      - Horizontal: word center must lie within the leaf grid extent
        (b[0] - 0.5 .. b[-1] + 0.5); the 0.5 pt slop absorbs float rounding.
      - Vertical: word must sit in EXACTLY ONE slot — either a header line (top
        within `win` of a known header-line top) OR a body row band (center
        within the row extents padded by 1 pt each side). A word in zero or
        two-or-more slots returns False (the exactly-one / anti-silent-wrong
        invariant).

    `win` is half the minimum gap between distinct header-top lines (dynamic,
    structural), defaulting to 8.0 pt when there is only one header line.
    """
    b = region.grid.boundaries
    # Collect distinct header-line tops (physical lines before body_line).
    header_tops = sorted({round(w.top, 1)
                          for ln in band.lines[:region.body_line]
                          for w in ln.words})
    # Dynamic header window: half the minimum inter-header gap.
    s_tops = sorted(set(header_tops))
    gaps = [hi - lo for lo, hi in zip(s_tops, s_tops[1:])]
    win = (min(gaps) / 2.0) if gaps else 8.0
    # Row extents: padded by 1 pt to absorb float rounding on anchor-cell tops.
    row_extents = [(r.top - 1.0, r.bottom + 1.0) for r in region.rows]
    for ln in band.lines:
        for w in ln.words:
            cx = (w.x0 + w.x1) / 2.0
            # Horizontal gate: must fall within the overall leaf grid.
            if not (b[0] - 0.5 <= cx <= b[-1] + 0.5):
                return False                        # outside the leaf grid
            cy = (w.top + w.bottom) / 2.0
            # Exactly-one vertical slot: header level OR body row, not both, not neither.
            placements = (
                sum(1 for ht in header_tops if abs(w.top - ht) < win)
                + sum(1 for lo, hi in row_extents if lo <= cy <= hi)
            )
            if placements != 1:
                return False                        # zero or double placement
    return True


def render_region_ascii(region, width: int = 80) -> str:
    """Render region header levels + body rows to a monospace canvas.

    Header cells are centered over their column span (derived from region.tree
    covers + grid.boundaries). Body row cells are placed by their x0 coordinate.
    One line of output per header level and per body row; header levels are
    separated from body rows by a dashed rule.
    """
    b = region.grid.boundaries
    x_lo, x_hi = b[0], b[-1]
    span = (x_hi - x_lo) or 1.0

    def _char_pos(x: float) -> int:
        return max(0, min(width - 1, int((x - x_lo) / span * (width - 1))))

    def _place(text: str, char_start: int, row: list[str]) -> None:
        for k, ch in enumerate(text):
            if 0 <= char_start + k < width:
                row[char_start + k] = ch

    lines_out: list[str] = []

    # Header levels: group HeaderNodes by level, render one canvas line per level.
    if region.tree:
        by_level: dict[int, list] = defaultdict(list)
        for node in region.tree:
            by_level[node.level].append(node)

        for lvl in sorted(by_level):
            row: list[str] = [" "] * width
            for node in by_level[lvl]:
                if not node.covers:
                    continue
                col_left = min(node.covers)
                col_right = max(node.covers)
                span_start = _char_pos(b[col_left])
                span_end = _char_pos(b[col_right + 1])
                center_char = (span_start + span_end) // 2
                text_start = center_char - len(node.text) // 2
                _place(node.text, text_start, row)
            lines_out.append("".join(row).rstrip())

        lines_out.append("-" * min(width, 40))

    # Body rows: one canvas line per RowBand, cells placed by x0.
    for rband in region.rows:
        row = [" "] * width
        for cell in rband.cells:
            _place(cell.text, _char_pos(cell.x0), row)
        lines_out.append("".join(row).rstrip())

    return "\n".join(lines_out)


def render_ascii(band: Band, width: int = 80) -> str:
    """Render the band's words to a monospace canvas positioned by x, so a human
    (and a diff) can see the measured layout. Used as escalation surface text."""
    words = [w for ln in band.lines for w in ln.words]
    if not words:
        return ""
    x0 = min(w.x0 for w in words)
    x1 = max(w.x1 for w in words)
    span = (x1 - x0) or 1.0
    tops = sorted({round(ln.top, 1) for ln in band.lines})
    rows: list[list[str]] = [[" "] * width for _ in tops]
    row_of = {t: i for i, t in enumerate(tops)}
    for ln in band.lines:
        r = rows[row_of[round(ln.top, 1)]]
        for w in ln.words:
            start = int((w.x0 - x0) / span * (width - 1))
            for k, ch in enumerate(w.text):
                if start + k < width:
                    r[start + k] = ch
    return "\n".join("".join(r).rstrip() for r in rows)
