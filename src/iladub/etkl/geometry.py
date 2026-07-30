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

import numpy as np
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
    """All text runs on a page, with bounding boxes in PDF points.

    Text-layer first: when pdfplumber finds words (a born-digital page), they are returned
    exactly. When the page has NO text layer (a scan/image), fall back to OCR — but ONLY if
    the optional `ocr` extra is importable; absent it, return [] and let the pipeline escalate
    (unchanged behaviour). OCR never competes with a present text layer."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        raw = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    words = [
        Word(w["text"], float(w["x0"]), float(w["x1"]),
             float(w["top"]), float(w["bottom"]), page_number)
        for w in raw
    ]
    if words:
        return words
    # No text layer -> OCR. The `.ocr` module ships with the package, but its engine
    # (pypdfium2 / rapidocr) is lazy-imported *inside* the call, so a missing `ocr` extra
    # surfaces as an ImportError at call time, not at module import. Catch both so an
    # absent extra escalates (returns []) instead of crashing.
    try:
        from .ocr import render_page_to_words
        return render_page_to_words(pdf_path, page_number)
    except ImportError:
        return []


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
class HRule:
    y: float       # y-position (page-top convention) of a horizontal ruled line
    x0: float      # x-extent
    x1: float


def extract_hrules(pdf_path: str, page_number: int = 0) -> list["HRule"]:
    """Horizontal ruled line segments on a page (author-drawn header/body & row separators).

    PROCEDURAL raw extraction, mirror of extract_rules: a segment is 'horizontal' when its vertical
    span is < 1pt and its horizontal span > 2pt. Vertical rules are handled by extract_rules."""
    out: list[HRule] = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        for seg in list(page.lines) + list(page.edges):
            x0, x1 = float(seg["x0"]), float(seg["x1"])
            top, bottom = float(seg["top"]), float(seg["bottom"])
            if abs(bottom - top) < 1.0 and (x1 - x0) > 2.0:
                out.append(HRule((top + bottom) / 2.0, x0, x1))
    uniq: list[HRule] = []
    for h in sorted(out, key=lambda h: (round(h.y, 1), h.x0)):
        if not any(abs(h.y - u.y) < 0.5 and abs(h.x0 - u.x0) < 1.0 and abs(h.x1 - u.x1) < 1.0 for u in uniq):
            uniq.append(h)
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


def _cell_text(glyphs: list["Char"]) -> str:
    """One cell's text, built from its NON-SPACE glyphs.

    A space is inserted between consecutive non-space glyphs only when BOTH hold:
      1. a space glyph lies between them — either within [a.x1, b.x0], or contained in the span
         of a or b (the overlapping-padding case); and
      2. they are actually apart (b.x0 - a.x1 > 0).

    Both are PRESENCE tests. There is no magnitude comparison and no unit, so no tuned constant
    (CLAUDE.md §8). That matters because the obvious magnitude rules were measured and REFUTED:
      - "a space overlapping a non-space glyph is padding" — the legitimate space in 'CARPE DIEM'
        also overlaps its neighbours E and D;
      - "split where the gap >= the font's median space width (1.46pt)" — yields 'CARPEDIEM',
        'ReferenceNumber', '10:00:00AM', because adjacent glyphs kern INTO the space, so the
        measured gap is far smaller than the space's own width.
    It works because the three regimes are disjoint. Measured over ALL 4114 consecutive non-space
    glyph pairs on a real page: intra-token kerning -0.19..+0.30, real word space 1.15..2.04,
    inter-column 4.95..189. The margin is 0.30 vs 1.15. (An earlier note here claimed -0.08..+0.11
    and 1.38-1.39 — those came from sampling a few cells and are WRONG by ~3x on one bound; the
    conclusion survives, the numbers did not.) A contiguous '20,000' has ZERO positive gaps, while
    padding glyphs overlap the digits they pad. Note the rule uses none of these magnitudes — they
    only explain WHY two presence tests suffice.

    `between` is provably SUBSUMED by `inside` for any glyph wider than COORD_EPS, and on the real
    page it fires on zero pairs that `inside` does not (deleting it leaves output byte-identical).
    It is retained only to state the strictly-between case explicitly; `inside` is what actually
    does the work — real word spaces OVERLAP both neighbours (by ~0.04), so `between` fails for
    them. Do not delete `inside` thinking `between` covers it: that mutant destroys every word
    space in the document while passing every test but one.

    A large gap with NO space glyph ANYWHERE in the cell does not split: that is a COLUMN gap
    (residue R13), and rule_aware_lines emits one Word per rule column. Narrower than it sounds —
    a padding space inside `a` licenses a split at a later large gap, since `inside` tests the
    whole span [a.x0, b.x1]. Zero occurrences on the measured document.
    """
    gl = sorted(glyphs, key=lambda c: c.x0)
    ns = [c for c in gl if c.text.strip()]
    if not ns:
        return ""
    sp = [c for c in gl if not c.text.strip()]
    parts = [ns[0].text]
    for a, b in zip(ns, ns[1:]):
        between = any(a.x1 - COORD_EPS <= s.x0 and s.x1 <= b.x0 + COORD_EPS for s in sp)
        inside = any(s.x0 >= a.x0 and s.x1 <= b.x1 for s in sp)
        if (b.x0 - a.x1) > 0 and (between or inside):
            parts.append(" ")
        parts.append(b.text)
    return "".join(parts).strip()


def refine_rule_columns(chars: list["Char"], rule_xs: list[float],
                        gutter_pct: float = 0.98, min_gutter_bins: int = 3) -> list[float]:
    """The author's rule boundaries, plus any column boundary the rules LEFT OUT.

    Rules are authoritative but not COMPLETE: an author may rule some boundaries and leave others
    to whitespace. Inside each rule interval, a run of x-bins that is blank on >= gutter_pct of the
    interval's inked rows, at least min_gutter_bins wide, AND with ink on BOTH sides of it within
    that interval, is an additional column boundary (its centre).

    THE INTERIOR CONDITION IS LOAD-BEARING — do not drop it. Without it, a blank run at a cell's
    trailing edge (short left-aligned text) reads as a separator: measured, that adds a boundary to
    EVERY interval of ruled_tight_table_pdf, turning 5 columns into 10. With it, both shipped ruled
    fixtures gain ZERO and the real document gains exactly the two it should. It is a presence test
    ("is there ink beyond this run, inside this interval"), not a threshold.

    ADDITIVE ONLY: every input boundary is preserved; nothing is moved or removed. The author's
    marks are never contradicted, only supplemented. Callers keep the raw marks in Band.rules and
    put this function's output in Band.column_xs, so provenance stays honest.

    gutter_pct and min_gutter_bins mirror infer_leaf_grid's existing defaults — pre-existing tuned
    constants this path INHERITS rather than invents. Space glyphs are not ink.
    """
    xs = sorted(rule_xs)
    if len(xs) < 2:
        return xs
    ink = [c for c in chars if c.text.strip()]
    out = [xs[0]]
    for i in range(len(xs) - 1):
        lo, hi = xs[i], xs[i + 1]
        nbins = int(np.ceil(hi - lo))
        seg = [c for c in ink if lo <= (c.x0 + c.x1) / 2.0 < hi]
        if seg and nbins >= min_gutter_bins:
            rows = sorted({round(c.top, 1) for c in seg})
            row_of = {t: k for k, t in enumerate(rows)}
            grid = np.zeros((len(rows), nbins), dtype=bool)
            for c in seg:
                a = int(c.x0 - lo)
                b = int(np.ceil(c.x1 - lo))
                grid[row_of[round(c.top, 1)], max(0, a):min(nbins, b)] = True
            blank = 1.0 - grid.mean(axis=0)
            any_ink = grid.any(axis=0)
            run = None
            for k, frac in enumerate(blank):
                if frac >= gutter_pct:
                    run = k if run is None else run
                    continue
                if (run is not None and k - run >= min_gutter_bins
                        and any_ink[:run].any() and any_ink[k:].any()):
                    out.append(round(lo + (run + k) / 2.0, 2))
                run = None
            # a run still open at the interval's end has no ink to its right -> never interior
        out.append(hi)
    return sorted(set(out))


def rule_aware_lines(chars: list[Char], rule_xs: list[float], y_tol: float | None = None) -> list[Line]:
    """Re-group characters into cells by ruled columns: rows by vertical proximity (as text_lines),
    then within each row a cell per rule-column (char CENTER within [rule_xs[i], rule_xs[i+1]]);
    each non-empty cell becomes one Word at its char-span bbox. The cell's text drops padding space
    glyphs (see `_cell_text`) and the bbox is taken from non-space glyphs. Chars outside all rule
    columns are dropped (they lie beyond the table's outer rules). Deterministic containment
    assignment — no tuned constant. This splits a pdfplumber-merged blob at the author's exact
    boundaries."""
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
            text = _cell_text(gl)
            if not text:
                continue
            # bbox from the NON-space glyphs: a cell padded with leading spaces must not report
            # ink it does not have.
            ink = [c for c in gl if c.text.strip()]
            words.append(Word(text, min(c.x0 for c in ink), max(c.x1 for c in ink),
                              min(c.top for c in ink), max(c.bottom for c in ink)))
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
