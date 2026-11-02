"""The form-fill flavour (spec 2026-10-31 § 4.3): values drawn as text over the template's blanks.

None of the four templates has AcroForm fields (measured 2026-10-31: `get_formtype() == 0`, no
widget annotations), so this is the overlay branch for all four. Each value is drawn left-aligned
on its blank, at `x0 + jitter`, jitter in [0, 6] pt seeded from the fill (clamped so the string
stays inside the blank), on a baseline `BASELINE_RISE` of the blank's height above its bottom.

Truth: parts (blanks included) are copied from the map unchanged — the output pages ARE the template
pages, same size, same coordinates. A value's box is the drawn string's own box, by exact
arithmetic: x from `stringWidth`, y from the font's ascent and descent at the drawn size.

Justified PROCEDURAL (CLAUDE.md § 8): this module MAKES a document. JITTER_MAX and BASELINE_RISE
are generation parameters (where to put ink), not reading tolerances; nothing here reads a
document or answers a span/read/group question. No reader may call it (A3).
"""
from __future__ import annotations

import random

from reportlab.pdfbase.pdfmetrics import getFont, stringWidth

from scripts.synthetic_contracts.fills import Fill
from scripts.synthetic_contracts.manifest import Template, template_path, verify
from scripts.synthetic_contracts.maps import Box, PartMap
from scripts.synthetic_contracts.overlay import overlay, to_bytes
from scripts.synthetic_contracts.truth import PartTruth, Truth, ValueTruth

FLAVOUR = "form-fill"
JITTER_MAX = 6.0      # pt, generation parameter
BASELINE_RISE = 0.2   # fraction of the blank's height above its bottom, generation parameter
JITTER_SALT = 0x464F524D  # "FORM": separates this flavour's stream from the fill's own draws


def map_parts(m: PartMap) -> tuple[PartTruth, ...]:
    """The map's parts in output coordinates, unchanged: non-blank parts in map order, then one
    `blank` part per blank (id `blank.<field>`), in the map's blank order."""
    return (tuple(PartTruth(p.id, p.type, p.box, p.parent) for p in m.parts)
            + tuple(PartTruth(f"blank.{b.field}", "blank", (b.box,), b.part) for b in m.blanks))


def place_values(m: PartMap, f: Fill) -> tuple[ValueTruth, ...]:
    """Where each value is drawn — decided once, used both to draw and to record truth."""
    if set(f.values) != {b.field for b in m.blanks}:
        raise ValueError(f"fill {f.id} does not fill exactly the blanks of map {m.template}")
    face = getFont(f.font).face
    asc, desc = face.ascent * f.size / 1000, face.descent * f.size / 1000  # desc < 0
    rng = random.Random(f.seed ^ JITTER_SALT)
    out = []
    for b in m.blanks:
        text = f.values[b.field]
        w = stringWidth(text, f.font, f.size)
        jitter = rng.uniform(0.0, max(0.0, min(JITTER_MAX, (b.box.x1 - b.box.x0) - w)))
        baseline = b.box.bottom - BASELINE_RISE * (b.box.bottom - b.box.top)
        x0 = b.box.x0 + jitter
        out.append(ValueTruth(b.field, text, Box(b.box.page, x0, baseline - asc, x0 + w,
                                                 baseline - desc)))
    return tuple(out)


def render_formfill(t: Template, m: PartMap, f: Fill) -> tuple[bytes, Truth]:
    verify(t)
    if m.template != t.id or f.template != t.id:
        raise ValueError(f"template {t.id}, map {m.template} and fill {f.id} disagree")
    values = place_values(m, f)
    face = getFont(f.font).face

    def draw(c, page_no):
        h = c._pagesize[1]
        c.setFont(f.font, f.size)
        for v in values:
            if v.box.page == page_no:
                baseline = v.box.top + face.ascent * f.size / 1000  # top-left -> baseline
                c.drawString(v.box.x0, h - baseline, v.value)

    pdf = to_bytes(overlay(template_path(t), draw))
    return pdf, formfill_truth(t, m, f, values)


def formfill_truth(t: Template, m: PartMap, f: Fill,
                   values: tuple[ValueTruth, ...] | None = None) -> Truth:
    """The form-fill truth record, from the manifest entry, the map and the fill alone: it needs no
    template file (only `t.sha256` and reportlab's core-font metrics), so CI can check that a
    committed record is still what its map and fill produce."""
    if values is None:
        values = place_values(m, f)
    return Truth(doc_id=f"{f.id}.{FLAVOUR}", flavour=FLAVOUR, templates=(t.sha256,), fills=(f.id,),
                 seed=f.seed, review=m.review, parts=map_parts(m), values=values, transform=None)
