"""unshownink — ink the text layer holds that the PAGE DOES NOT SHOW a reader (R213).

THE PHENOMENON. graincorp-capacity p0 carries 110 glyphs the text layer transcribes as "0" and
that no reader of that page can see. Before this module they typed `tab:Numeric`, voted in every
homogeneity judgement, and were grounded as tonnages of zero — asserting of a shipping berth a
capacity the document never showed anyone. That is the § 7 false assertion the term
`tab:UnshownInk` exists to refuse.

THE DECIDABLE FACT IS NOT A COLOUR DISTANCE. It is a DISAGREEMENT between two independent
readings of one cell (spec 2026-09-17 § 4.1):

    the text layer says | a reader of the page says | the cell is
    a glyph is here     | a mark is here            | ordinary ink
    a glyph is here     | NO mark                   | tab:UnshownInk
    no glyph            | no mark                   | tab:Blank (unchanged)
    no glyph            | a mark                    | out of scope — flag, do not type

No colour, no palette, no threshold. The spec's § 1.1 measured the whole class of colour rules
refuted on this corpus, and the disagreement generalises by construction to a specimen no ratio
can separate. **Nothing in this module reads a pixel value.**

§ 8 CLASSIFICATION, part by part:

  * rasterising the page and cropping the region  — PROCEDURAL raw extraction, the class
    `geometry.py` already names for the vector-line reader.
  * reading the text layer's glyph presence       — PROCEDURAL, already shipped (`_grid_cells`).
  * "does this cell show a mark?"                 — NEURAL. It is a perceptual question about
    what a page shows a reader, and § 8 has no other class for it.
  * the disagreement -> the type                  — AXIOM, open-world and evidence-positive:
    BOTH readings must be present for a cell to type `tab:UnshownInk`. A missing or refused
    answer types NOTHING — it never claims a cell is ordinary by absence.

WHAT HAPPENS WHEN RUN n+1 DIFFERS FROM RUN n (spec § 8.9 item 2, unanswered there; this module
is where it is answered). **The readings are never merged. There is deliberately no API to merge
them.** A union would admit a cell only one run ever called empty — asserting more than the
evidence supports (§ 7). An intersection would drop a cell one run missed — inferring absence,
which the open-world clause forbids. A majority vote would need a run count nobody has a reason
to choose, i.e. a tuned constant in all but name. So: **one run, one reading, disposed by the
oracles below and recorded with the run that produced it.** A re-run is a NEW proposal that
supersedes the old one, and any difference between them is a MEASUREMENT to report — never a
tolerance to average away. Non-determinism is tolerated at the proposal and nowhere else,
because the membrane admits the same class of thing either way (the 2026-09-17 ruling).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Protocol

DPI = 220        # the render scale the spec measured legible at region grain (§ 8.7). It is a
                 # RENDER setting, not a decision rule: nothing compares it to anything, and no
                 # answer changes with it except by being easier or harder for a reader to see.


@dataclass(frozen=True)
class Reading:
    """One reader's answer about one region. Addresses and abstentions only — by construction it
    cannot carry a value that is on the page (§ 8.7 / RF8; run 1 of the blind disposal returned
    the string "14,000" because the shape it was given allowed it to)."""
    empty_cells: frozenset[tuple[int, int]]
    refuses_grid: bool = False
    rows_seen: int = 0
    cols_seen: int = 0
    note: str = ""


class RegionReader(Protocol):
    def read_empty_cells(self, crop_png: bytes, nrows: int, ncols: int) -> "Reading | None": ...


@dataclass(frozen=True)
class FakeRegionReader:
    """Deterministic offline reader (the `FakeProposer` precedent). Every oracle below is
    exercised against this, so the disposal is testable without a model or a network."""
    reading: "Reading | None"

    def read_empty_cells(self, crop_png, nrows, ncols):
        return self.reading


def baml_reader_available() -> bool:
    """True only when explicitly enabled AND baml_client is importable — `propose.py`'s gate,
    verbatim, so the corpus battery and every instrument stay offline and deterministic unless a
    run asks for a live reading."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


class BamlRegionReader:
    """Live reader — calls the BAML `ReadEmptyCells` function. Lazy import, as `BamlProposer`."""

    def read_empty_cells(self, crop_png, nrows, ncols):
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.ReadEmptyCells(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            nrows, ncols)
        return Reading(
            empty_cells=frozenset((int(a.row), int(a.col)) for a in r.empty_cells),
            refuses_grid=bool(r.refuses_grid),
            rows_seen=int(r.rows_you_see),
            cols_seen=int(r.cols_you_see),
            note=str(r.note))


def render_region(pdf_path: str, page_number: int, band, dpi: int = DPI) -> bytes:
    """The band's rendered crop, as PNG bytes.

    PROCEDURAL raw extraction, and irreducible for the reason the class exists: turning a page
    description into pixels is a computation, not a judgement. It reads no colour and decides
    nothing — the bytes go to a reader, never to a comparison."""
    import io
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        pad = 2.0
        box = (max(0.0, min(w.x0 for ln in band.lines for w in ln.words) - pad),
               max(0.0, band.top - pad),
               min(float(page.width), max(w.x1 for ln in band.lines for w in ln.words) + pad),
               min(float(page.height), band.bottom + pad))
        im = page.crop(box).to_image(resolution=dpi)
        buf = io.BytesIO()
        im.original.save(buf, format="PNG")
        return buf.getvalue()


def dispose(reading, grid_cells, nrows: int, ncols: int,
            spanned: frozenset[tuple[int, int]] = frozenset()) -> frozenset[tuple[int, int]]:
    """The AXIOM: the disagreement, after three refusals. Returns the addresses that type
    `tab:UnshownInk`, or the EMPTY SET when the region is refused.

    `grid_cells` is `headers._grid_cells`' output — the text layer's reading. `spanned` is the
    set of positions covered by the extent of a spanning cell, which a reader legitimately reads
    as occupied (R211).

    OPEN-WORLD AND EVIDENCE-POSITIVE. A cell types unshown only where BOTH readings are present:
    the text layer holds a glyph AND the reader saw no mark. A refused region types nothing, and
    that is not a claim that its cells are ordinary — it is the absence of a claim.

    THE THREE REFUSALS (§ 8.7), and each refuses the WHOLE region rather than one address:

    1. An address outside the grid. Arithmetic. An answer with an out-of-range address is an
       answer in a different address space, and the in-range members of such an answer are no
       more trustworthy than the out-of-range one that revealed it.

    2. "This is not the grid I see." Not hypothetical: on cbh two independent blind readers both
       rejected the supplied 18 x 16, both counted 20 columns, and disagreed with each other on
       rows (13 vs 16). Without this, an answer in a different address space is admitted in
       SILENCE, because every address in it is *inside* the stated grid.

    3. The null control, which comes free in the reader's own answer: a reader of the page must
       also find the positions that are GENUINELY empty. If the answer misses one, the reader is
       not reading the page and the region is refused. `tab:Blank` is deliberately NOT the
       control — measured, 0 of 406 on the region this loop is about — the live set is the
       text-layer-empty position. It is scoped to positions NOT inside a spanning cell's extent:
       25 of gcap band 3's 26 empty positions are column 0, the spanning year label a reader
       reads as ONE cell, and a reader that reads the span as occupied is reading correctly.
       **The honest strength of this control on gcap is therefore ONE cell, (1, 6)** — recorded
       as a weakness, not a footnote (§ 8.9 item 3).
    """
    if reading is None:
        return frozenset()
    if reading.refuses_grid:
        return frozenset()                                   # refusal 2
    if any(not (0 <= r < nrows and 0 <= c < ncols) for r, c in reading.empty_cells):
        return frozenset()                                   # refusal 1

    has_glyph = {(int(r), int(c)) for r, c, _t in grid_cells}
    all_positions = {(r, c) for r in range(nrows) for c in range(ncols)}
    text_layer_empty = (all_positions - has_glyph) - spanned
    if not text_layer_empty <= reading.empty_cells:           # refusal 3
        return frozenset()

    return frozenset(reading.empty_cells & has_glyph)         # the disagreement


def region_unshown(pdf_path, page_number, band, grid, reader,
                   spanned: frozenset[tuple[int, int]] = frozenset()):
    """One ask per REGION — the cost gate in R249 half (a)'s shape, not one ask per cell.

    Returns the disposed addresses in `_grid_cells`' (row, col) space, ready for `Band.unshown`.
    Every failure path returns the empty set: a reader that cannot be reached, a crop that cannot
    be rendered and a refused region are all "no claim", never "no unshown ink"."""
    from .headers import _grid_cells
    if reader is None or grid is None or not band.lines:
        return frozenset()
    cells = _grid_cells(band, grid)
    nrows, ncols = len(band.lines), grid.ncols
    try:
        crop = render_region(pdf_path, page_number, band)
    except Exception:
        return frozenset()
    return dispose(reader.read_empty_cells(crop, nrows, ncols), cells, nrows, ncols, spanned)
