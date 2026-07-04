"""geometry — words in PDF points, grouped into text lines.

Responsibilities (single):
  - extract_words: pull all text runs from one page, returning Word objects
    with bboxes in PDF points (x0/x1 from page left, top/bottom from page TOP,
    matching pdfplumber's coordinate convention).
  - text_lines: group those words into Line objects by vertical proximity.

No bands, no grid logic — those live in later tasks.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

import pdfplumber


@dataclass(frozen=True)
class Word:
    text: str
    x0: float   # points, from page left
    x1: float
    top: float  # points, from page TOP (pdfplumber convention)
    bottom: float
    page: int = 0


@dataclass(frozen=True)
class Line:
    words: tuple[Word, ...]
    top: float
    bottom: float


def extract_words(pdf_path: str, page_number: int = 0) -> list[Word]:
    """All text runs on a page, with bounding boxes in PDF points."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        raw = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    return [
        Word(w["text"], float(w["x0"]), float(w["x1"]),
             float(w["top"]), float(w["bottom"]), page_number)
        for w in raw
    ]


def text_lines(words: list[Word], y_tol: float | None = None) -> list[Line]:
    """Group words into lines by vertical proximity of their `top`.

    Two words share a line when their tops differ by at most `y_tol`
    (default: 0.6 x median glyph height). Lines are returned top-to-bottom,
    words within a line left-to-right.

    Note: grouping compares each word's `top` to the group leader's `top`; for
    very small fonts (tol below accumulated intra-line y-drift) a long line can
    over-split — acceptable for a 1pt-precision floor, revisit with a
    sliding-window median if needed.
    """
    if not words:
        return []
    ws = sorted(words, key=lambda w: (round(w.top, 1), w.x0))
    med_h = median(w.bottom - w.top for w in ws)
    tol = y_tol if y_tol is not None else 0.6 * med_h
    groups: list[list[Word]] = [[ws[0]]]
    for w in ws[1:]:
        if abs(w.top - groups[-1][0].top) > tol:
            groups.append([])
        groups[-1].append(w)
    lines = []
    for group in groups:
        ordered = sorted(group, key=lambda w: w.x0)
        lines.append(Line(tuple(ordered), min(w.top for w in ordered), max(w.bottom for w in ordered)))
    return sorted(lines, key=lambda ln: ln.top)
