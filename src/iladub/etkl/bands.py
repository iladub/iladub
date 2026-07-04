"""bands — split lines into horizontal bands by vertical gaps.

Single responsibility: detect layout bands (title, table body, paragraph, etc.)
by finding inter-line gaps that are significantly larger than the median gap.
No grid/table logic lives here.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .geometry import Line


@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float


def detect_bands(lines: list[Line], gap_factor: float = 1.8) -> list[Band]:
    """Split lines into bands wherever the inter-line gap exceeds
    `gap_factor` x the median inter-line gap. A band is a run of lines with
    regular spacing (a paragraph, a table body, a title)."""
    if not lines:
        return []
    ls = sorted(lines, key=lambda ln: ln.top)
    gaps = [ls[i + 1].top - ls[i].bottom for i in range(len(ls) - 1)]
    positive = [g for g in gaps if g > 0]
    med_gap = median(positive) if positive else 0.0
    groups: list[list[Line]] = [[ls[0]]]
    for i in range(1, len(ls)):
        gap = gaps[i - 1]
        if med_gap > 0 and gap > gap_factor * med_gap:
            groups.append([])
        groups[-1].append(ls[i])
    return [
        Band(tuple(g), min(ln.top for ln in g), max(ln.bottom for ln in g))
        for g in groups
    ]
