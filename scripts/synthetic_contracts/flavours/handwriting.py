"""The simulated-handwriting flavour (spec 2026-10-31 § 4.3): values written by hand, then scanned.

Each value is drawn glyph by glyph over its blank in one of three handwriting TTFs, chosen per fill,
from the four measured present (shared context item 5): Bradley Hand Bold, Comic Sans MS, Apple
Chancery. Chalkduster is left out: its glyphs drop up to 0.27 em below the font's declared descent
(measured 2026-10-31), the one font of the four that does. Each glyph has its own baseline jitter
(±1.2 pt) and size jitter (±8 %), and is filled and stroked with a 0.5 pt round-joined pen: without
the pen, Apple Chancery's hairlines at 8 pt left as little as 0.2 % new dark pixels in a value's box
after the scan (`usda-ffp-cp-3`, measured 2026-10-31). The page is then scanned by `scan.py`, which
only degrades.

Truth: a value's box is the union of its glyphs' INK boxes — each glyph's own outline bounds, read
from the font's `glyf` table through reportlab's TTF parser, at that glyph's jittered size and
baseline, widened by half the pen. So the box contains what was drawn, not a naive string box:
handwriting glyphs overhang their advance, up to 0.41 em on the left in Bradley Hand and 0.27 em on
the right in Apple Chancery (measured 2026-10-31). `place_glyphs` decides every glyph once; the same
records are drawn and recorded, then every box (parts and values) goes through `affine_box` with the
scan's matrix, which the truth records as `transform`. A value whose ink would not fit its blank
raises `ValueTooLong` where it is placed (CLAUDE.md § Producer-side guards), never overflowing onto
template text.

Justified PROCEDURAL (CLAUDE.md § 8): this module MAKES a document. BASELINE_JITTER, SIZE_JITTER,
LEAD_MAX, PEN_WIDTH and BASELINE_RISE are generation parameters (where to put ink), not reading
tolerances; the glyph bounds are raw extraction from a font file and the fit test is exact
arithmetic. Nothing here reads a document or answers a span/read/group question. No reader may
call it (A3).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from scripts.synthetic_contracts.fills import Fill, ValueTooLong
from scripts.synthetic_contracts.manifest import Template, template_path, verify
from scripts.synthetic_contracts.maps import Box, PartMap
from scripts.synthetic_contracts.overlay import overlay
from scripts.synthetic_contracts.flavours.formfill import map_parts
from scripts.synthetic_contracts.scan import (affine_box, image_pdf, page_matrix, rasterise,
                                              scan_pages, scan_params)
from scripts.synthetic_contracts.truth import PartTruth, Truth, ValueTruth

FLAVOUR = "handwriting-scan"
_SUPP = Path("/System/Library/Fonts/Supplemental")
HAND_FONTS = {  # measured present 2026-10-31 (shared context item 5)
    "Hand-BradleyBold": _SUPP / "Bradley Hand Bold.ttf",
    "Hand-ComicSans": _SUPP / "Comic Sans MS.ttf",
    "Hand-AppleChancery": _SUPP / "Apple Chancery.ttf",
}
BASELINE_JITTER = 1.2  # pt, generation parameter
SIZE_JITTER = 0.08     # fraction of the fill's size, generation parameter
LEAD_MAX = 6.0         # pt of space before the first glyph, generation parameter
PEN_WIDTH = 0.5        # pt, the pen's stroke around each outline, generation parameter
BASELINE_RISE = 0.2    # fraction of the blank's height above its bottom, generation parameter
HAND_SALT = 0x48414E44  # "HAND": separates this flavour's stream from the fill's own draws


@dataclass(frozen=True)
class Glyph:
    page: int
    ch: str
    font: str
    size: float
    x: float         # pen position, points from the left edge
    baseline: float  # points from the top edge


def _font(name: str) -> TTFont:
    try:
        return pdfmetrics.getFont(name)
    except KeyError:
        f = TTFont(name, str(HAND_FONTS[name]))
        pdfmetrics.registerFont(f)
        return f


def _ink(name: str, ch: str) -> tuple[float, float, float, float] | None:
    """The glyph's outline bounds (xMin, yMin, xMax, yMax) in 1/1000 em, y up; None if it has no
    outline (a space). Read from the `glyf` header through reportlab's own TTF parser."""
    face = _font(name).face
    gid = face.charToGlyph.get(ord(ch))
    if gid is None:
        raise ValueError(f"{name} has no glyph for {ch!r}")
    pos = face.glyphPos[gid]
    if face.glyphPos[gid + 1] == pos:
        return None
    face.seek(face.get_table_pos("glyf")[0] + pos)
    face.skip(2)  # numberOfContours
    k = 1000 / face.unitsPerEm
    x0, y0, x1, y1 = (face.read_short() for _ in range(4))
    return x0 * k, y0 * k, x1 * k, y1 * k


def place_glyphs(m: PartMap, f: Fill) -> tuple[tuple[Glyph, ...], tuple[ValueTruth, ...]]:
    """Every glyph of every value, and each value's ink box (pre-scan) — decided once, used both to
    draw and to record truth. Raises `ValueTooLong(field)` if a value's ink is wider than its
    blank."""
    if set(f.values) != {b.field for b in m.blanks}:
        raise ValueError(f"fill {f.id} does not fill exactly the blanks of map {m.template}")
    rng = random.Random(f.seed ^ HAND_SALT)
    font = rng.choice(sorted(HAND_FONTS))
    glyphs: list[Glyph] = []
    values: list[ValueTruth] = []
    for b in m.blanks:
        text = f.values[b.field]
        base = b.box.bottom - BASELINE_RISE * (b.box.bottom - b.box.top)
        pen, drawn, ink = 0.0, [], []
        for ch in text:
            size = f.size * (1 + rng.uniform(-SIZE_JITTER, SIZE_JITTER))
            bl = base + rng.uniform(-BASELINE_JITTER, BASELINE_JITTER)
            drawn.append((ch, size, pen, bl))
            g = _ink(font, ch)
            if g is not None:
                s, r = size / 1000, PEN_WIDTH / 2  # a round-joined stroke reaches r past it
                ink.append((pen + g[0] * s - r, bl - g[3] * s - r, pen + g[2] * s + r,
                            bl - g[1] * s + r))
            pen += pdfmetrics.stringWidth(ch, font, size)
        if not ink:
            raise ValueError(f"fill {f.id}: value for {b.field} draws no ink")
        lo, hi = min(i[0] for i in ink), max(i[2] for i in ink)
        slack = (b.box.x1 - b.box.x0) - (hi - lo)
        if slack < 0:
            raise ValueTooLong(b.field)
        dx = b.box.x0 + rng.uniform(0.0, min(LEAD_MAX, slack)) - lo
        glyphs += [Glyph(b.box.page, ch, font, size, x + dx, bl) for ch, size, x, bl in drawn]
        values.append(ValueTruth(b.field, text, Box(
            b.box.page, lo + dx, min(i[1] for i in ink), hi + dx, max(i[3] for i in ink))))
    return tuple(glyphs), tuple(values)


def _draw(glyphs):
    def draw(c, page_no):
        h = c._pagesize[1]
        c.setLineWidth(PEN_WIDTH)
        c.setLineJoin(1)  # round: the stroke never reaches past PEN_WIDTH / 2 (no miter spikes)
        c.setLineCap(1)
        for g in glyphs:
            if g.page == page_no:
                c.setFont(g.font, g.size)
                c.drawString(g.x, h - g.baseline, g.ch, mode=2)  # fill + stroke: pen ink
    return draw


def ink_only(template_pdf: Path, glyphs, dpi: int = 200):
    """The glyphs alone on white pages of the template's size, undegraded (a test oracle's
    input)."""
    import pypdfium2 as pdfium
    from io import BytesIO
    from reportlab.pdfgen.canvas import Canvas
    sizes = [p.get_size() for p in pdfium.PdfDocument(str(template_pdf))]
    buf = BytesIO()
    c = Canvas(buf, invariant=1)
    draw = _draw(glyphs)
    for n, size in enumerate(sizes, 1):
        c.setPageSize(size)
        draw(c, n)
        c.showPage()
    c.save()
    return rasterise(pdfium.PdfDocument(buf.getvalue()), dpi)


def render_handwriting(t: Template, m: PartMap, f: Fill) -> tuple[bytes, Truth]:
    verify(t)
    if m.template != t.id or f.template != t.id:
        raise ValueError(f"template {t.id}, map {m.template} and fill {f.id} disagree")
    glyphs, values = place_glyphs(m, f)
    doc = overlay(template_path(t), _draw(glyphs))
    sizes = {tuple(doc[i].get_size()) for i in range(len(doc))}
    if len(sizes) != 1:
        raise ValueError(f"template {t.id}: pages of different sizes")
    (size,) = sizes
    params = scan_params(f.seed)
    pages = scan_pages(doc, params)
    mtx = page_matrix(params, pages[0].shape)

    def mv(b: Box) -> Box:
        return affine_box(b, mtx, size)
    parts = tuple(PartTruth(p.id, p.type, tuple(mv(b) for b in p.boxes), p.parent)
                  for p in map_parts(m))
    truth = Truth(doc_id=f"{f.id}.{FLAVOUR}", flavour=FLAVOUR, templates=(t.sha256,), fills=(f.id,),
                  seed=f.seed, review=m.review, parts=parts,
                  values=tuple(ValueTruth(v.field, v.value, mv(v.box)) for v in values),
                  transform=tuple(float(x) for x in mtx.flatten()))
    return image_pdf(pages, size), truth
