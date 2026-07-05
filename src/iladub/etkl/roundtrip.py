"""roundtrip — the per-cell round-trip oracle and its spatial-ASCII evidence.

Gate: a cell round-trips iff every word lies within its assigned column span
(no straddle across a gutter). The gutter (a boundary between spans) is the
oracle; there is no tuned tolerance beyond a hair's-width float epsilon.
"""
from __future__ import annotations

from typing import Sequence

from .bands import Band
from .geometry import COORD_EPS
from .regions import Cell


def cell_round_trips(cell: Cell, boundaries: Sequence[float]) -> bool:
    lo, hi = boundaries[cell.col], boundaries[cell.col + 1]
    return all(w.x0 >= lo - COORD_EPS and w.x1 <= hi + COORD_EPS for w in cell.words)


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
