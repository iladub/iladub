"""The author's closed ruled boxes on a page (spec 2026-09-28-box-split-design.md § 2).

A page can draw two tables side by side inside one text band (cbh-stem p0 band 9): each is a
CLOSED RULED BOX with a filled title bar on top. This module reads those boxes off the vector
marks, and nothing else: which band they belong to and how the band is split are decided
elsewhere (spec § 3).

Four steps, each classified per CLAUDE.md § 8 (spec § 6):

- `extract_box_rules` — PROCEDURAL, raw extraction (§ 2.1): source vector marks -> typed rule
  facts. It is irreducible for the same reason `extract_words` is: the marks are only reachable
  through the PDF content stream, and reading them is transcription, not judgement.
- `touches` — PROCEDURAL, exact interval arithmetic (§ 2.2, ruling R-c). The only bound is the
  thinner stroke of the two marks compared, read off the marks themselves; no constant enters.
- `closed_boxes` — PROCEDURAL, exact interval arithmetic (§ 2.3-2.4): connected components of the
  touch graph, the closed-frame condition, the title bar. Decidable and exact; the only bound is
  again a stroke width read off the component's own marks.
- `page_boxes` — the composition; decides nothing of its own.

`geometry.extract_rules` / `extract_hrules` are deliberately not used: they take every edge of
every rect, fills included, which reads a coloured title bar's edges as column rules (§ 7.4).

A miss by this reader fails SAFE — no box forms and the band compiles as it did before the split
existed. The risk it carries is commission (a box that is not there), which is why every
condition below is exact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pdfplumber


@dataclass(frozen=True)
class BoxRule:
    """One ruled mark at its PAINTED extent (page-top y convention, stroke width included)."""
    orient: str        # "H" | "V"
    x0: float
    x1: float
    top: float
    bottom: float

    @property
    def thickness(self) -> float:
        """The stroke width: a horizontal's painted height, a vertical's painted width."""
        return self.bottom - self.top if self.orient == "H" else self.x1 - self.x0


@dataclass(frozen=True)
class Fill:
    """A filled rect whose fill colour is known and not black — a title-bar candidate (§ 2.4)."""
    x0: float
    x1: float
    top: float
    bottom: float


@dataclass(frozen=True)
class Box:
    """A closed ruled box (§ 2.3): the bounding box of its rules' painted extents, its rules, and
    the (x0, x1, top, bottom) of its title bar when it has one (§ 2.4)."""
    x0: float
    x1: float
    top: float
    bottom: float
    verticals: tuple[BoxRule, ...]
    horizontals: tuple[BoxRule, ...]
    title_bar: tuple[float, float, float, float] | None


# --- § 2.1 the rule reader (PROCEDURAL, raw extraction) ------------------------------------------

def _fill_is_black(colour) -> bool | None:
    """True for EXACT black, False for any other colour pdfplumber reports, None when the colour
    is not a device colour we can read (absent, a pattern name, an unknown component count).

    Exact black, per colour space: gray 0; RGB (0, 0, 0); CMYK (0, 0, 0, 1). No near-black:
    a dark fill is not a rule, and a threshold for "dark enough" would be a tuned constant."""
    if isinstance(colour, bool) or colour is None:
        return None
    if isinstance(colour, (int, float)):
        return float(colour) == 0.0
    if not isinstance(colour, (tuple, list)):
        return None
    try:
        comps = tuple(float(c) for c in colour)
    except (TypeError, ValueError):
        return None
    if len(comps) == 1:
        return comps == (0.0,)
    if len(comps) == 3:
        return comps == (0.0, 0.0, 0.0)
    if len(comps) == 4:
        return comps == (0.0, 0.0, 0.0, 1.0)
    return None


def _page_marks(page) -> tuple[list[BoxRule], list[Fill]]:
    """Every rule (§ 2.1) and every title-bar candidate fill (§ 2.4) on one pdfplumber page.

    PROCEDURAL raw extraction. One pass over `page.rects` classifies each filled rect exactly once
    — rule (exact black, not square), candidate fill (a known colour, not black), or neither — so
    no rect is ever both.

    Painted extents: a stroked rect is a closed path, so each edge's ink reaches half the line
    width past the path on every side (the corner is inked by the join). A stroked line's ink
    reaches half the line width to each side of the path; along its length it ends at the path
    (PDF's default butt cap — pdfplumber does not report the cap style). A filled rect's ink is
    the rect itself."""
    rules: list[BoxRule] = []
    fills: list[Fill] = []
    for r in page.rects:
        x0, x1 = float(r["x0"]), float(r["x1"])
        top, bottom = float(r["top"]), float(r["bottom"])
        if r.get("fill"):
            black = _fill_is_black(r.get("non_stroking_color"))
            w, h = x1 - x0, bottom - top
            if black is True and w != h:
                rules.append(BoxRule("H" if w > h else "V", x0, x1, top, bottom))
            elif black is False:
                fills.append(Fill(x0, x1, top, bottom))
        if r.get("stroke"):
            hw = float(r.get("linewidth") or 0.0) / 2.0
            rules += [
                BoxRule("H", x0 - hw, x1 + hw, top - hw, top + hw),
                BoxRule("H", x0 - hw, x1 + hw, bottom - hw, bottom + hw),
                BoxRule("V", x0 - hw, x0 + hw, top - hw, bottom + hw),
                BoxRule("V", x1 - hw, x1 + hw, top - hw, bottom + hw),
            ]
    for ln in page.lines:
        if not ln.get("stroke"):
            continue
        x0, x1 = float(ln["x0"]), float(ln["x1"])
        top, bottom = float(ln["top"]), float(ln["bottom"])
        hw = float(ln.get("linewidth") or 0.0) / 2.0
        if top == bottom and x0 != x1:          # axis-aligned, exactly: a horizontal rule
            rules.append(BoxRule("H", x0, x1, top - hw, bottom + hw))
        elif x0 == x1 and top != bottom:        # a vertical rule
            rules.append(BoxRule("V", x0 - hw, x1 + hw, top, bottom))
        # a diagonal or zero-length line is not a rule
    return rules, fills


def extract_box_rules(pdf_path: str, page_number: int = 0) -> list[BoxRule]:
    """The page's rules at their painted extents (spec § 2.1): a non-square EXACT-black filled
    rect; each edge of a stroked rect; a stroked, axis-aligned line.

    PROCEDURAL raw extraction — irreducible: the marks exist only in the PDF content stream."""
    with pdfplumber.open(pdf_path) as pdf:
        return _page_marks(pdf.pages[page_number])[0]


# --- § 2.2 touch (PROCEDURAL, exact arithmetic under ruling R-c) ---------------------------------

def _gap(a0: float, a1: float, b0: float, b1: float) -> float:
    """The distance between two closed intervals; 0 when they meet or overlap."""
    return max(0.0, max(a0, b0) - min(a1, b1))


def touches(h: BoxRule, v: BoxRule) -> bool:
    """A horizontal and a vertical rule touch when their x-gap AND their y-gap are both at most
    the thinner of the two strokes (spec § 2.2, R-c). A zero-width rule therefore touches only at
    gap 0.

    PROCEDURAL: decidable exact interval arithmetic. The bound is read off the two marks being
    compared; nothing else enters."""
    t = min(h.thickness, v.thickness)
    return _gap(h.x0, h.x1, v.x0, v.x1) <= t and _gap(h.top, h.bottom, v.top, v.bottom) <= t


# --- § 2.3 closed boxes, § 2.4 title bars (PROCEDURAL, exact arithmetic) --------------------------

def _covers(intervals: list[tuple[float, float]], a: float, b: float, bound: float) -> bool:
    """Does the union of `intervals` cover [a, b] with no uncovered gap larger than `bound`?"""
    reach = a
    for s, e in sorted(intervals):
        if s - reach > bound:
            return False
        reach = max(reach, e)
    return b - reach <= bound


def _components(rules: Sequence[BoxRule]) -> list[list[BoxRule]]:
    """Connected components of the H-V touch graph, in first-rule order."""
    parent = list(range(len(rules)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    hs = [i for i, r in enumerate(rules) if r.orient == "H"]
    vs = [i for i, r in enumerate(rules) if r.orient == "V"]
    for i in hs:
        for j in vs:
            if touches(rules[i], rules[j]):
                parent[find(i)] = find(j)
    groups: dict[int, list[BoxRule]] = {}
    for i, r in enumerate(rules):
        groups.setdefault(find(i), []).append(r)
    return list(groups.values())


def _frame_closed(comp: list[BoxRule], x0: float, x1: float, top: float, bottom: float,
                  bound: float) -> bool:
    """Is each side of the component's bounding box covered by ink (spec § 2.3)?

    A side's ink is every rule of the component that reaches that side (within `bound`), in
    EITHER orientation: a vertical's painted extent inks the corner a horizontal stops short of,
    so perpendicular rules count too (§ 7.2 records the check that did not count them, and read
    every cbh box as open)."""
    top_ink = [(r.x0, r.x1) for r in comp if r.top - top <= bound]
    bottom_ink = [(r.x0, r.x1) for r in comp if bottom - r.bottom <= bound]
    left_ink = [(r.top, r.bottom) for r in comp if r.x0 - x0 <= bound]
    right_ink = [(r.top, r.bottom) for r in comp if x1 - r.x1 <= bound]
    return (_covers(top_ink, x0, x1, bound) and _covers(bottom_ink, x0, x1, bound)
            and _covers(left_ink, top, bottom, bound) and _covers(right_ink, top, bottom, bound))


def _title_bar(fills: Sequence[Fill], top_rules: list[BoxRule], left: float, right: float
               ) -> tuple[float, float, float, float] | None:
    """The box's title bar (spec § 2.4): a non-black fill whose x-extent lies within the box's
    outer verticals [left, right], that rises above the top rule, and whose BOTTOM EDGE touches the
    top rule under § 2.2's bound — the thinner of the rule's stroke and the fill's own thickness
    (its smaller dimension). Exactly one such fill, or None: two candidates is no single bar to
    assert, and the choice between them is not this reader's to make."""
    found = []
    for f in fills:
        if not (left <= f.x0 and f.x1 <= right):
            continue
        f_thick = min(f.x1 - f.x0, f.bottom - f.top)
        for h in top_rules:
            t = min(h.thickness, f_thick)
            if (f.top < h.top and _gap(f.x0, f.x1, h.x0, h.x1) <= t
                    and _gap(f.bottom, f.bottom, h.top, h.bottom) <= t):
                found.append((f.x0, f.x1, f.top, f.bottom))
                break
    return found[0] if len(found) == 1 else None


def closed_boxes(rules: Sequence[BoxRule], fills: Sequence[Fill]) -> list[Box]:
    """The closed ruled boxes the rules draw (spec § 2.3), each with its title bar (§ 2.4).

    A box is a connected component of the touch graph with >= 2 horizontals, >= 2 verticals and a
    closed outer frame, the frame judged within the component's THINNEST stroke. Returned sorted
    by the exact (top, x0) of their painted extents — NOT a reading order a caller may rely on:
    two boxes side by side sort by float noise in their tops (cbh-stem p0 band 9: the right box's
    top is 689.6399999999999, the left's 689.64, measured 2026-09-28).

    PROCEDURAL: decidable exact interval arithmetic over extracted marks; the only bound is a
    stroke width read off the component itself."""
    out: list[Box] = []
    for comp in _components(rules):
        hs = [r for r in comp if r.orient == "H"]
        vs = [r for r in comp if r.orient == "V"]
        if len(hs) < 2 or len(vs) < 2:
            continue
        x0, x1 = min(r.x0 for r in comp), max(r.x1 for r in comp)
        top, bottom = min(r.top for r in comp), max(r.bottom for r in comp)
        bound = min(r.thickness for r in comp)
        if not _frame_closed(comp, x0, x1, top, bottom, bound):
            continue
        top_rules = [h for h in hs if h.top - top <= bound]
        bar = _title_bar(fills, top_rules, min(v.x0 for v in vs), max(v.x1 for v in vs))
        out.append(Box(x0, x1, top, bottom,
                       tuple(sorted(vs, key=lambda r: (r.x0, r.top))),
                       tuple(sorted(hs, key=lambda r: (r.top, r.x0))),
                       bar))
    return sorted(out, key=lambda b: (b.top, b.x0))


def page_boxes(pdf_path: str, page_number: int = 0) -> list[Box]:
    """The closed ruled boxes on one page — `closed_boxes` over the page's rules and fills, read
    in one pass. Composition only; decides nothing of its own."""
    with pdfplumber.open(pdf_path) as pdf:
        rules, fills = _page_marks(pdf.pages[page_number])
    return closed_boxes(rules, fills)
