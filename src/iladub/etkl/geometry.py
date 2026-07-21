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

# Sub-point float tolerance for boundary containment checks.
COORD_EPS: float = 0.01


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


@dataclass(frozen=True)
class Rule:
    x: float       # x-position of a vertical ruled line (points from page left)
    top: float     # y-extent, page-top convention
    bottom: float


def extract_rules(pdf_path: str, page_number: int = 0) -> list["Rule"]:
    """Vertical ruled line segments on a page (the author's explicit column separators).

    PROCEDURAL raw extraction (like extract_words): reads pdfplumber's vector lines/edges;
    a segment is 'vertical' when its horizontal span is < 1pt and its vertical span > 2pt.
    Horizontal rules are ignored (a future header/row-split signal)."""
    out: list[Rule] = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        for seg in list(page.lines) + list(page.edges):
            x0, x1 = float(seg["x0"]), float(seg["x1"])
            top, bottom = float(seg["top"]), float(seg["bottom"])
            if abs(x1 - x0) < 1.0 and (bottom - top) > 2.0:
                out.append(Rule((x0 + x1) / 2.0, top, bottom))
    # de-duplicate near-identical rules (lines + edges can double-report)
    uniq: list[Rule] = []
    for r in sorted(out, key=lambda r: (round(r.x, 1), r.top)):
        if not any(abs(r.x - u.x) < 0.5 and abs(r.top - u.top) < 1.0 and abs(r.bottom - u.bottom) < 1.0 for u in uniq):
            uniq.append(r)
    return uniq


@dataclass(frozen=True)
class Char:
    text: str
    x0: float
    x1: float
    top: float
    bottom: float


def extract_chars(pdf_path: str, page_number: int = 0) -> list[Char]:
    """All characters on a page with per-glyph bboxes (PROCEDURAL raw extraction, like
    extract_words). Used to re-group text into cells by ruled columns when pdfplumber's
    proximity word-grouping fuses tight adjacent cells into one blob."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        return [Char(c["text"], float(c["x0"]), float(c["x1"]), float(c["top"]), float(c["bottom"]))
                for c in page.chars]


def rule_aware_lines(chars: list[Char], rule_xs: list[float], y_tol: float | None = None) -> list[Line]:
    """Re-group characters into cells by ruled columns: rows by vertical proximity (as text_lines),
    then within each row a cell per rule-column (char CENTER within [rule_xs[i], rule_xs[i+1]]);
    each non-empty cell becomes one Word at its char-span bbox. Chars outside all rule columns are
    dropped (they lie beyond the table's outer rules). Deterministic containment assignment — no
    tuned constant. This splits a pdfplumber-merged blob at the author's exact boundaries."""
    if not chars or len(rule_xs) < 2:
        return []
    xs = sorted(rule_xs)
    # §7 no-data-loss: extend the column RANGE to the char ink extent so a char beyond the
    # outermost rules (an interior-only-ruled table with no bounding rectangle) folds into an edge
    # column instead of being dropped. Fully-bounded tables (chars within the rules) are unchanged.
    lo = min(c.x0 for c in chars)
    hi = max(c.x1 for c in chars)
    if lo < xs[0] - COORD_EPS:
        xs = [lo] + xs
    if hi > xs[-1] + COORD_EPS:
        xs = xs + [hi]
    cs = sorted(chars, key=lambda c: (round(c.top, 1), c.x0))
    med_h = median(c.bottom - c.top for c in cs)
    tol = y_tol if y_tol is not None else 0.6 * med_h
    rows: list[list[Char]] = [[cs[0]]]
    for c in cs[1:]:
        if abs(c.top - rows[-1][0].top) > tol:
            rows.append([])
        rows[-1].append(c)
    lines: list[Line] = []
    for row in rows:
        buckets: dict[int, list[Char]] = {}
        for c in row:
            cx = (c.x0 + c.x1) / 2.0
            col = next((i for i in range(len(xs) - 1) if xs[i] <= cx < xs[i + 1]), None)
            if col is not None:
                buckets.setdefault(col, []).append(c)
        words: list[Word] = []
        for col in sorted(buckets):
            gl = sorted(buckets[col], key=lambda c: c.x0)
            text = "".join(c.text for c in gl).strip()
            if not text:
                continue
            words.append(Word(text, min(c.x0 for c in gl), max(c.x1 for c in gl),
                              min(c.top for c in gl), max(c.bottom for c in gl)))
        if words:
            lines.append(Line(tuple(words), min(w.top for w in words), max(w.bottom for w in words)))
    return sorted(lines, key=lambda ln: ln.top)


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
