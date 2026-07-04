"""grid — body leaf-column grid from a whitespace occupancy profile.

Single responsibility: given a table Band, infer the leaf-column grid via a
vertical whitespace occupancy profile computed over the band's rows, plus a
confidence from row-sample size. No header / tiling logic here (increment 1b).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bands import Band


@dataclass(frozen=True)
class LeafGrid:
    boundaries: tuple[float, ...]  # x separators in points, len == ncols + 1
    ncols: int
    pitch: float                   # median column width (points)
    confidence: float              # 0..1, from row-sample size


def _column_blank_profile(band: Band, x0: float, x1: float,
                          bin_w: float = 1.0) -> np.ndarray:
    """Per x-bin, the fraction of band rows that are BLANK at that x."""
    nbins = max(1, int(np.ceil((x1 - x0) / bin_w)))
    ink = np.zeros((len(band.lines), nbins), dtype=bool)
    for r, line in enumerate(band.lines):
        for w in line.words:
            a = int((w.x0 - x0) / bin_w)
            b = int(np.ceil((w.x1 - x0) / bin_w))
            ink[r, max(0, a):min(nbins, b)] = True
    return 1.0 - ink.mean(axis=0)  # blank fraction per bin


def infer_leaf_grid(band: Band, gutter_pct: float = 0.98,
                    min_gutter_bins: int = 3, sample_target: int = 4) -> LeafGrid:
    """Column grid from the vertical whitespace profile of the band.

    A gutter is a run of >= `min_gutter_bins` x-bins that are blank on >=
    `gutter_pct` of rows. Boundaries are gutter centres plus the band's ink
    extremes. Confidence scales with the number of rows supporting the profile
    (thin bands -> low confidence -> lower decidability ceiling downstream).

    Tuning guidance:
      - ncols too high (column split): raise min_gutter_bins (e.g. 5 or 6).
      - ncols too low (columns merged): lower gutter_pct (e.g. 0.95).
    """
    xs0 = min(w.x0 for ln in band.lines for w in ln.words)
    xs1 = max(w.x1 for ln in band.lines for w in ln.words)
    blank = _column_blank_profile(band, xs0, xs1)
    is_gutter = blank >= gutter_pct

    boundaries = [xs0]
    run_start = None
    for i, g in enumerate(list(is_gutter) + [False]):  # sentinel flush
        if g and run_start is None:
            run_start = i
        elif not g and run_start is not None:
            if (i - run_start) >= min_gutter_bins:
                boundaries.append(xs0 + (run_start + i) / 2.0)  # gutter centre
            run_start = None
    boundaries.append(xs1)
    boundaries = sorted({round(b, 2) for b in boundaries})

    ncols = len(boundaries) - 1
    widths = [boundaries[i + 1] - boundaries[i] for i in range(ncols)]
    pitch = float(np.median(widths)) if widths else 0.0
    confidence = min(1.0, len(band.lines) / float(sample_target))
    return LeafGrid(tuple(boundaries), ncols, pitch, confidence)
