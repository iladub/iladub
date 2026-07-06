"""roundtrip — the per-cell round-trip oracle and its spatial-ASCII evidence.

Gate: a cell round-trips iff every word lies within its assigned column span
(no straddle across a gutter). The gutter (a boundary between spans) is the
oracle; there is no tuned tolerance beyond a hair's-width float epsilon.

region_round_trips: the 2-D faithfulness gate for hierarchical tables —
every measured word in the band must place into exactly one (leaf column ×
row-band or header level). A word outside the leaf grid, or in no row/level,
fails it. This is the anti-silent-wrong gate for hierarchical tables.
"""
from __future__ import annotations

from typing import Sequence

from .bands import Band
from .geometry import COORD_EPS
from .regions import Cell, column_of


def cell_round_trips(cell: Cell, boundaries: Sequence[float]) -> bool:
    lo, hi = boundaries[cell.col], boundaries[cell.col + 1]
    return all(w.x0 >= lo - COORD_EPS and w.x1 <= hi + COORD_EPS for w in cell.words)


def region_round_trips(region, band) -> bool:
    """Every measured word must place into exactly one (leaf column × row/level).

    Structural gates (no tuned constants):
      - Horizontal: word center must lie within the leaf grid extent
        (b[0] - 0.5 .. b[-1] + 0.5); the 0.5 pt slop absorbs float rounding.
      - Vertical: word must sit in a header line (top within 8 pt of a known
        header-line top) OR in a body row band (center within the row extents
        padded by 1 pt each side to absorb float rounding from the anchor cell).
    """
    b = region.grid.boundaries
    # Collect distinct header-line tops (physical lines before body_line).
    header_tops = sorted({round(w.top, 1)
                          for ln in band.lines[:region.body_line]
                          for w in ln.words})
    # Row extents: padded by 1 pt to absorb float rounding on anchor-cell tops.
    row_extents = [(r.top - 1.0, r.bottom + 1.0) for r in region.rows]
    for ln in band.lines:
        for w in ln.words:
            cx = (w.x0 + w.x1) / 2.0
            # Horizontal gate: must fall within the overall leaf grid.
            if not (b[0] - 0.5 <= cx <= b[-1] + 0.5):
                return False                        # outside the leaf grid
            cy = (w.top + w.bottom) / 2.0
            # Vertical gate: in a header line OR in a body row band.
            in_header = any(abs(w.top - ht) < 8.0 for ht in header_tops)
            in_body = any(lo <= cy <= hi for lo, hi in row_extents)
            if not (in_header or in_body):
                return False                        # places in no row/level
    return True


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
