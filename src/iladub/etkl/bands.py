"""bands — split lines into horizontal bands by vertical gaps.

Single responsibility: detect layout bands (title, table body, paragraph, etc.)
by finding inter-line gaps that are significantly larger than the median gap.
No grid/table logic lives here.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .geometry import Line, Rule, HRule


@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float
    rules: tuple[Rule, ...] = ()
    hrules: tuple[HRule, ...] = ()
    # Derived column boundaries (author rules PLUS interior gutters the rules left out — see
    # geometry.refine_rule_columns). `rules` stays exactly what the author drew; keeping them
    # separate is deliberate, so a derived boundary is never mistaken for a mark in the document.
    column_xs: tuple[float, ...] = ()
    # Full-width strip lines peeled from ABOVE a ruled grid (key headings, notices —
    # loop P). Kept word-based (never rule-re-extracted) and CARRIED to the asserted
    # table as tab:RegionCaption; default empty so every existing constructor stands.
    captions: tuple[Line, ...] = ()
    # Absorbed currency-marker columns (spec 2026-08-05-unit-marker-column-design.md):
    # (symbol, neighbor_x, regions) per absorbed column — the marker ink CARRIED (§5),
    # emitted at assert time as tab:hasUnitMarker on the neighbor column. Default empty
    # so every existing constructor stands (the Band.captions precedent).
    unit_markers: tuple = ()


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


def band_text(band) -> str:
    """A band's exact surface text: words left-to-right, lines top-to-bottom, newline-joined.

    Raw extraction, and the whole of it — no normalisation, no case folding, no stripping. Two
    renderings of one furniture block on two pages produce the same string exactly when the
    renderer drew the same words; anything softer would be the pipeline deciding that two
    different blocks are "the same enough", which is a judgment the law does not make.
    """
    return "\n".join(" ".join(w.text for w in ln.words) for ln in band.lines)
