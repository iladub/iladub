"""caption — a data grid's own title and unit lines, proposed by a reader and disposed exactly (R336).

THE GAP. `boxhead.dispose_boxhead` files every header-block word as a leaf label, a spanner, or
`other_words`. A line made only of `other_words` is not carried (`boxhead.carried_lines`), so a
table's own title and unit line stay uncarried even when the boxhead beneath them is read in full.
Some of those lines are the table's caption; others belong to the page.

§ 8 CLASSIFICATION (spec 2026-10-24 § 4), part by part:

  | decision                                  | class      | why                                    |
  |-------------------------------------------|------------|----------------------------------------|
  | which lines are the table's own caption   | NEURAL     | *what a title is* is a reading         |
  |                                           | (this      | judgement, never line position         |
  |                                           | worker)    |                                        |
  | caption disposal                          | PROCEDURAL | address-space, contiguity and          |
  |                                           | (disposal) | adjacency checks, all exact            |

  The candidate lines (`candidate_lines`) and the listing (`listing_of`) are PROCEDURAL renderings
  of the disposed boxhead and the text layer: set membership and coordinates, no judgement. No
  geometric attempt is made at all — "the lines above the boxhead" is forbidden by the 2026-09-17
  ruling — and no tuned constant appears anywhere.

THE READER ANSWERS IN INDICES, never text: `caption_lines` are numbers into the candidate listing
it was given, so it cannot return a value that is on the page.

THE DISPOSAL (`dispose_captions`), all exact; anything else is NO CLAIM, the status quo:

  1. A refusing reading claims nothing.
  2. ADDRESS SPACE. Every index is a candidate (`range(len(candidates))`), none twice.
  3. NON-EMPTY.
  4. CONTIGUOUS IN PAGE ORDER. The block positions, not the candidate indices, are consecutive: a
     non-candidate line between two candidates (a dropped spanner's, say) breaks the run.
  5. ADJACENT. The last line is the block position directly above the topmost block line that
     holds a word of a surviving leaf or surviving spanner. A grid with no surviving label has no
     such line, and claims no caption.

CARRIAGE (`emit_captions`): one `tab:RegionCaption` per disposed line — NEVER `tab:SectionCaption`,
whose text `feed.py` reads as candidate section keys — with text, block row and page, and NO box:
`tab:hasBBox rdfs:domain tab:Cell` would type the caption a cell, and `tab:WrappedCellShape` refuses
a cell with a box and no `cellText` (plan M2, a deviation from spec § 3.3 flagged to the maintainer).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
from dataclasses import dataclass
from typing import Protocol

from .boxhead import Address, DisposedBoxhead, _ordered, boxhead_region, header_block


@dataclass(frozen=True)
class CaptionReading:
    caption_lines: tuple[int, ...] = ()
    refuses: bool = False
    note: str = ""


class CaptionReader(Protocol):
    def read_caption(self, crop_png: bytes, ncols: int, listing: str) -> "CaptionReading | None": ...


@dataclass(frozen=True)
class FakeCaptionReader:
    reading: "CaptionReading | None"

    def read_caption(self, crop_png, ncols, listing):
        return self.reading


def baml_caption_available() -> bool:
    """PROCEDURAL — an environment gate: live only under `BAML_LIVE=1` with a generated client."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


# MODULE-GLOBAL, keyed like `boxhead._BOXHEAD_CACHE`: one live call per distinct question for the
# whole process, because the ask site is reached on several passes.
_CAPTION_CACHE: dict = {}


class BamlCaptionReader:
    """The live reader: `ReadCaption` on the `Claude` client. NEURAL — the model proposes."""

    def read_caption(self, crop_png, ncols, listing):
        key = (hashlib.sha256(crop_png).hexdigest(), int(ncols),
               hashlib.sha256(listing.encode("utf-8")).hexdigest())
        if key in _CAPTION_CACHE:
            return _CAPTION_CACHE[key]
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.ReadCaption(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            int(ncols), listing)
        reading = CaptionReading(caption_lines=tuple(int(i) for i in r.caption_lines),
                                 refuses=bool(r.refuses), note=str(r.note or ""))
        _CAPTION_CACHE[key] = reading
        return reading


# ---------------------------------------------------------------------------------------------
# THE QUESTION — candidates and their listing
# ---------------------------------------------------------------------------------------------

def candidate_lines(lines, block, disposed: DisposedBoxhead) -> tuple[int, ...]:
    """Block positions (not page indices) of the header-block lines whose every word the disposed
    boxhead filed as `other_words`, top to bottom; `()` for a refused disposal. Such a line holds
    no spanner word, surviving or dropped, because `dispose_boxhead` accounts for every listed word
    exactly once (plan M3). PROCEDURAL — set membership."""
    if disposed.refused:
        return ()
    other = set(disposed.other_words)
    return tuple(k for k, j in enumerate(block)
                 if lines[j].words and all((k, i) in other for i in range(len(lines[j].words))))


def listing_of(lines, block, candidates) -> str:
    """`C<i>: [0]word@x0-x1 …` per candidate, `i` its index in `candidates`; words left to right with
    their page extents, as `boxhead.listing_of` renders them. PROCEDURAL — a rendering."""
    return "\n".join(
        f"C{i}: " + " ".join(f"[{n}]{w.text}@{w.x0:.0f}-{w.x1:.0f}"
                             for n, w in enumerate(_ordered(lines[block[k]])))
        for i, k in enumerate(candidates))


def _labelled_lines(disposed: DisposedBoxhead) -> set[int]:
    kept: set[Address] = {a for ws in disposed.labels.values() for a in ws}
    kept |= {a for _a, _b, ws in disposed.spanners for a in ws}
    return {a[0] for a in kept}


def dispose_captions(reading, candidates, block, lines, disposed: DisposedBoxhead) -> tuple[int, ...]:
    """The five exact checks of the module docstring. Returns the disposed caption lines as block
    positions, top to bottom, or `()` for NO CLAIM. `block` and `lines` are the arguments
    `candidate_lines` was given; PROCEDURAL — integer comparisons, no geometry, no tolerance."""
    if reading is None or reading.refuses:
        return ()
    idx = tuple(reading.caption_lines)
    if not idx or len(set(idx)) != len(idx):
        return ()
    if any(not (0 <= i < len(candidates)) for i in idx):
        return ()
    rows = sorted(candidates[i] for i in idx)
    if any(b != a + 1 for a, b in zip(rows, rows[1:])):
        return ()
    labelled = _labelled_lines(disposed)
    if not labelled or rows[-1] != min(labelled) - 1:
        return ()
    return tuple(rows)


# ---------------------------------------------------------------------------------------------
# THE ASK
# ---------------------------------------------------------------------------------------------

def _render_crop(pdf_path, page_number, region) -> bytes:
    """The seam to the renderer — `unshownink.render_region`, the entry point `read_grid_boxhead`
    uses. PROCEDURAL raw extraction (pixels from a page description)."""
    from .unshownink import render_region
    return render_region(pdf_path, page_number, region)


def read_grid_captions(pdf_path: str, page_number: int, lines, grid, disposed: DisposedBoxhead,
                       reader: "CaptionReader | None") -> tuple[int, ...]:
    """One ask per grid that has candidate lines, over the crop `read_grid_boxhead` renders
    (`boxhead.boxhead_region`). Returns the disposed caption lines as PAGE-LINE indices. Asks
    nothing when there is no reader or no candidate; every exception is NO CLAIM, `()`."""
    try:
        block = header_block(lines, grid)
        candidates = candidate_lines(lines, block, disposed)
        if reader is None or not candidates:
            return ()
        crop = _render_crop(pdf_path, page_number, boxhead_region(lines, grid))
        reading = reader.read_caption(crop, len(grid.columns), listing_of(lines, block, candidates))
        return tuple(block[k] for k in dispose_captions(reading, candidates, block, lines, disposed))
    except Exception:
        return ()


# ---------------------------------------------------------------------------------------------
# RECORDED READINGS — the proposal, kept, and disposed again on every compile
# ---------------------------------------------------------------------------------------------
#
# THE KEY IS THE QUESTION: sha256 of `"caption\n" + ncols + "\n" + listing`. The `caption\n` prefix
# keeps a caption key from ever colliding with a boxhead key over the same text; the second `\n`
# mirrors `boxhead.question_key`'s separator between the count and the listing.

READINGS_DIR = pathlib.Path(__file__).resolve().parents[3] / "readings" / "caption"


def question_key(ncols: int, listing: str) -> str:
    """PROCEDURAL — sha256 of `"caption\\n" + str(ncols) + "\\n" + listing`."""
    return hashlib.sha256(f"caption\n{int(ncols)}\n{listing}".encode("utf-8")).hexdigest()


def _to_json(r: CaptionReading) -> dict:
    return {"caption_lines": list(r.caption_lines), "refuses": r.refuses, "note": r.note}


def _from_json(d: dict) -> CaptionReading:
    return CaptionReading(caption_lines=tuple(int(i) for i in d.get("caption_lines", [])),
                          refuses=bool(d.get("refuses", False)), note=str(d.get("note", "")))


@dataclass
class RecordedCaptionReader:
    """Replays a recorded reading; on a miss, asks `live` (if any) and — only when
    `ILADUB_RECORD_READINGS=1` — writes the answer down. With no recording and no live reader it
    returns None: no claim. PROCEDURAL — a lookup; the answer it replays was the reader's.

    `directory` defaults to the module's `READINGS_DIR` AT CALL TIME, so a test that patches the
    module attribute is honoured (the `headerlines.RecordedHeaderLinesReader` precedent)."""
    live: "CaptionReader | None" = None
    directory: "pathlib.Path | None" = None

    def read_caption(self, crop_png, ncols, listing):
        directory = self.directory if self.directory is not None else READINGS_DIR
        path = directory / f"{question_key(ncols, listing)}.json"
        if path.exists():
            return _from_json(json.loads(path.read_text(encoding="utf-8")))
        if self.live is None:
            return None
        reading = self.live.read_caption(crop_png, ncols, listing)
        if reading is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(_to_json(reading), indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        return reading


def default_reader() -> RecordedCaptionReader:
    """Recorded first; the live reader behind it only when `BAML_LIVE=1`. PROCEDURAL wiring."""
    return RecordedCaptionReader(live=BamlCaptionReader() if baml_caption_available() else None)


# ---------------------------------------------------------------------------------------------
# CARRIAGE
# ---------------------------------------------------------------------------------------------

def emit_captions(g, grid_uri, lines, caption_page_lines, page: int, block) -> int:
    """One `tab:RegionCaption` per disposed caption line, URI `<grid>-cap<k>`: `tab:captionText` the
    line's words left to right from the TEXT LAYER (the reader supplied none), `tab:captionRow` its
    BLOCK position (`tab.ttl`: the header-region row, 0 = topmost), `tab:onPage`, and
    `grid tab:hasCaption cap`. Never `tab:SectionCaption`, never `tab:hasBBox` (module docstring,
    M2). `block` is `header_block`'s output, which `caption_page_lines` index into. PROCEDURAL — raw
    extraction of a decision already disposed. Returns the number of captions emitted."""
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, XSD
    from .holon import TAB
    for k, j in enumerate(caption_page_lines):
        cap = URIRef(f"{grid_uri}-cap{k}")
        g.add((cap, RDF.type, TAB.RegionCaption))
        g.add((cap, TAB.captionText, Literal(" ".join(w.text for w in _ordered(lines[j])))))
        g.add((cap, TAB.captionRow, Literal(block.index(j), datatype=XSD.integer)))
        g.add((cap, TAB.onPage, Literal(page, datatype=XSD.integer)))
        g.add((grid_uri, TAB.hasCaption, cap))
    return len(caption_page_lines)
