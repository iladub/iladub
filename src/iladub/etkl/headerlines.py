"""headerlines — "how many leading lines of this drawn box are header lines?", asked of a reader.

Box-split spec § 10.3.3 (`docs/superpowers/specs/2026-09-28-box-split-design.md`), plan Task 3d.5
as amended by A2. A box the author drew is compiled positionally: row 0 is its header line. Some
boxes have no boxhead, and whether row 0 is header or data was measured UNDERDETERMINED by style
(§ 10.1), so it is a reading judgement.

§ 8 CLASSIFICATION (spec § 10.4), part by part:

  * the count ("how many leading lines are header")  — NEURAL. `CountHeaderLines`
    (`baml_src/header_lines.baml`) proposes a closed int. It is disposed ONE WAY elsewhere, by
    `row-zero-differs.rq` (`rowzero.py`); this module never decides header-vs-data, and a reader
    that is absent, raises, or answers out of range is NO CLAIM, never a fallback.
  * the question (`listing_of`, `question_key`)       — PROCEDURAL: a rendering of the region's own
    cells and a hash of it. It reads no geometry and has no constant.
  * the closed-answer check (`ask_header_lines`)      — PROCEDURAL exact arithmetic: an int is in
    `0..nlines` or it is not (PR #256).

The stack mirrors `boxhead.py`'s (Fake / Baml / Recorded readers, the question key, the recorded
readings directory) and deliberately imports nothing from it: the two workers ask different
questions and must be free to diverge.

THE LISTING UNIT. A listing line IS a region row, and `nlines` is the region's row count
(`len(region.band.lines)`; `regions.assign_cells` gives every band line its row). A cell whose text
carries a line break stays one row — its lines are joined with a space. Measured 2026-09-30: no
pdfplumber word carries one (`WordExtractor` ends a word on any `isspace()` char), but
`regions.Cell.text` joins `Word.text`s, and the OCR path's `OcrRegion.text` is an unconstrained
`str`, so the type admits it.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HeaderLinesReading:
    """The reader's answer: the count, and a note that is carried to the decision's rationale and
    nowhere else. The note never carries page text (the `ReadBoxhead` rule)."""
    header_lines: int
    note: str


class HeaderLinesReader(Protocol):
    def count_header_lines(self, crop_png: bytes, ncols: int,
                           listing: str) -> "HeaderLinesReading | None": ...


@dataclass(frozen=True)
class FakeHeaderLinesReader:
    """A fixed answer, for tests. PROCEDURAL — it returns what it was built with."""
    reading: "HeaderLinesReading | None"

    def count_header_lines(self, crop_png, ncols, listing):
        return self.reading


def baml_header_lines_available() -> bool:
    """PROCEDURAL — an environment gate: live only under `BAML_LIVE=1` with a generated client."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


# MODULE-GLOBAL, not per instance (plan A2): the ask site calls `default_reader()` once per region,
# and a region is reached on several passes (`p`, `r2`, `adopt`; spec § 10.2), so an instance cache
# would dedupe nothing. One live call per distinct question, keyed like `boxhead._BOXHEAD_CACHE`.
_HEADER_LINES_CACHE: dict = {}


class BamlHeaderLinesReader:
    """The live reader: `CountHeaderLines` on the `Claude` client. NEURAL — the model proposes.
    One call per distinct question for the whole process, keyed on the crop's content, the column
    count and the listing (`boxhead.py:103-104`'s key)."""

    def count_header_lines(self, crop_png, ncols, listing):
        key = (hashlib.sha256(crop_png).hexdigest(), int(ncols),
               hashlib.sha256(listing.encode("utf-8")).hexdigest())
        if key in _HEADER_LINES_CACHE:
            return _HEADER_LINES_CACHE[key]
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.CountHeaderLines(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            int(ncols), listing)
        reading = HeaderLinesReading(header_lines=int(r.header_lines), note=str(r.note or ""))
        _HEADER_LINES_CACHE[key] = reading
        return reading


def _cell_line(text: str) -> str:
    return " ".join(text.splitlines())


def listing_of(region) -> str:
    """The question's text: every region row, numbered `L<k>`, its cells in column order joined by
    ` | ` — the body rows included, because they are part of the question (spec § 10.3.3). Every
    column position of the region's grid is shown, an absent cell as empty, so a row's k-th field
    is column k. PROCEDURAL — a rendering of the region's own cells; it decides nothing."""
    ncols = region.grid.ncols
    text = {(c.row, c.col): _cell_line(c.text) for c in region.cells}
    return "\n".join(
        f"L{k}: " + " | ".join(text.get((k, col), "") for col in range(ncols))
        for k in range(len(region.band.lines)))


# ---------------------------------------------------------------------------------------------
# RECORDED READINGS — the proposal, kept, and range-checked again on every compile
# ---------------------------------------------------------------------------------------------
#
# THE KEY IS THE QUESTION: sha256 of the column count and the listing, `boxhead.question_key`'s
# form. The listing holds every row, so a recording answers exactly one question, and moves when
# any cell of the region does.

READINGS_DIR = pathlib.Path(__file__).resolve().parents[3] / "readings" / "header_lines"


def question_key(ncols: int, listing: str) -> str:
    """PROCEDURAL — sha256 of `f"{ncols}\\n{listing}"`."""
    return hashlib.sha256(f"{int(ncols)}\n{listing}".encode("utf-8")).hexdigest()


@dataclass
class RecordedHeaderLinesReader:
    """Replays a recorded reading; on a miss, asks `live` (if any) and — only when
    `ILADUB_RECORD_READINGS=1` — writes the answer down. With no recording and no live reader it
    returns None: no claim. PROCEDURAL — a lookup; the answer it replays was the reader's.

    `directory` defaults to the module's `READINGS_DIR` AT CALL TIME, so a test that patches the
    module attribute is honoured (a dataclass default would have bound it at import)."""
    live: "HeaderLinesReader | None" = None
    directory: "pathlib.Path | None" = None

    def count_header_lines(self, crop_png, ncols, listing):
        directory = self.directory if self.directory is not None else READINGS_DIR
        path = directory / f"{question_key(ncols, listing)}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return HeaderLinesReading(header_lines=int(d["header_lines"]),
                                      note=str(d.get("note", "")))
        if self.live is None:
            return None
        reading = self.live.count_header_lines(crop_png, ncols, listing)
        if reading is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"header_lines": reading.header_lines,
                                        "note": reading.note}, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        return reading


def default_reader() -> RecordedHeaderLinesReader:
    """Recorded first; the live reader behind it only when `BAML_LIVE=1`. PROCEDURAL wiring."""
    return RecordedHeaderLinesReader(
        live=BamlHeaderLinesReader() if baml_header_lines_available() else None)


def ask_header_lines(region, pdf_path: str, page_number: int,
                     reader: "HeaderLinesReader | None") -> "HeaderLinesReading | None":
    """One ask per region: the region's extent rendered by `unshownink.render_region` (the entry
    point `boxhead.read_grid_boxhead` uses), its column count, and its listing.

    Returns None — NO CLAIM, never a fallback — in four cases: no reader; the reader (or the
    render) raised; the reader returned None; the answer is outside `0..nlines`, `nlines` being the
    region's row count (the closed-answer check, PR #256). PROCEDURAL — it applies a range check
    and decides nothing; the count is the reader's (NEURAL)."""
    if reader is None:
        return None
    from .unshownink import render_region
    nlines = len(region.band.lines)
    try:
        # `render_region` reads the x-extent from `band.lines[*].words` and the y-extent from
        # `band.top`/`band.bottom` (unshownink.py, `def render_region`); a `Band` carries all three,
        # so the region's own band is passed as it is.
        crop = render_region(pdf_path, page_number, region.band)
        reading = reader.count_header_lines(crop, region.grid.ncols, listing_of(region))
    except Exception:
        return None
    if reading is None:
        return None
    if not (0 <= reading.header_lines <= nlines):
        return None
    return reading
