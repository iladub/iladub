"""boxhead — the column identity of a data grid, proposed by a reader and disposed by the grid.

THE GAP. `datagrid.py` derives a table's ENTRIES and no header, by design (R71: reading the
header first is circular). So an adopted grid asserts cells with coordinates and no column
identity. Measured 2026-09-18 on ons-index-of-services: **552 data cells, 0 column labels**, and
every one of the document's 175 escalated tokens is header metadata nothing reads.

THE EVIDENCE THAT IT IS GENERAL (`scripts/grid_boxhead_spike.py`, all 7 documents): the refused
lines directly above a grid's first admitted row label nearly every column on all 16
grid-deriving pages — who 12 of 13, bfs p5 11 of 12, graincorp 14 of 15 (the unlabelled one is the
stub). 71% of those words sit inside exactly one column; **23% cross a boundary** — spanners,
titles, wide labels.

§ 8 CLASSIFICATION, part by part:

  * the header block (which lines)            — PROCEDURAL. The contiguous run of lines the grid
    itself REFUSED, directly above its first admitted row. Set arithmetic over the grid's own
    `rows` and `refusals`; no geometry, no tolerance.
  * leaf label / spanning label / not a header — NEURAL. A reading judgement. The one geometric
    attempt — strict containment of a word in a column — is already refuted on the page that
    suggested it: ons p7's "Total Distribution Transport, …" line carries a word whose extent
    overflows its column while it plainly heads it. Per CLAUDE.md § "One geometric attempt, then
    NEURAL", the next instrument is a worker, and the effort goes into its disposal.
  * the disposal                              — AXIOM-shaped exact checks, below.

THE READER ANSWERS IN ADDRESSES, never text: a header word is (line, word) into the listing it
was given, so the answer cannot carry a value that is on the page and cannot invent a label.

THE DISPOSAL — two whole-reading refusals and one per-label one:

  1. ADDRESS SPACE. Any address outside the listing, or any column index outside the grid, refuses
     the WHOLE reading: an answer in a different address space is not partly right.
  2. TOTAL ACCOUNTING — the null control, and it comes free. Every listed word must appear in
     exactly one list. A reader that skips a word or uses one twice is not reading the header,
     and the reading is refused. Silence is never read as "not a header".
  3. PLACEMENT, per label. A leaf label stands only if EVERY one of its words has its centre
     inside the claimed column's own interval — `column_of(centre)`, the assignment rule this
     codebase uses for every cell. A label that fails is DROPPED, the rest stand: two independent
     readings (the reader's, the text layer's geometry) must agree, label by label.

A spanning label's geometry is NOT disposed beyond range and order: a spanner is typically
centred over its group and its ink covers a fraction of it, so extent proves nothing. Spanners
are therefore REPORTED and not yet carried — what would dispose them is the open question here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Protocol

Address = tuple[int, int]            # (line index within the block listing, word index)


@dataclass(frozen=True)
class BoxheadReading:
    leaf_labels: tuple[tuple[int, tuple[Address, ...]], ...] = ()
    spanning_labels: tuple[tuple[int, int, tuple[Address, ...]], ...] = ()
    other_words: tuple[Address, ...] = ()
    refuses_grid: bool = False
    cols_seen: int = 0
    note: str = ""


@dataclass(frozen=True)
class DisposedBoxhead:
    """`labels` maps a grid column to its label's addresses, top to bottom. `refused` names why a
    WHOLE reading was refused (then `labels` is empty); `dropped` lists the columns whose label
    failed placement while the rest stood."""
    labels: dict = field(default_factory=dict)
    spanners: tuple = ()
    dropped: tuple[int, ...] = ()
    refused: str | None = None


class BoxheadReader(Protocol):
    def read_boxhead(self, crop_png: bytes, ncols: int, listing: str) -> "BoxheadReading | None": ...


@dataclass(frozen=True)
class FakeBoxheadReader:
    reading: "BoxheadReading | None"

    def read_boxhead(self, crop_png, ncols, listing):
        return self.reading


def baml_boxhead_available() -> bool:
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


_BOXHEAD_CACHE: dict = {}


class BamlBoxheadReader:
    """Live reader. One ask per distinct question, keyed on the crop's content plus the listing —
    the `CachingRegionReader` rule, for the reason recorded there (page_bands runs 2-3x)."""

    def read_boxhead(self, crop_png, ncols, listing):
        key = (hashlib.sha256(crop_png).hexdigest(), int(ncols),
               hashlib.sha256(listing.encode("utf-8")).hexdigest())
        if key in _BOXHEAD_CACHE:
            return _BOXHEAD_CACHE[key]
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.ReadBoxhead(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            int(ncols), listing)
        addr = lambda ws: tuple((int(a.line), int(a.word)) for a in ws)   # noqa: E731
        reading = BoxheadReading(
            leaf_labels=tuple((int(l.col), addr(l.words)) for l in r.leaf_labels),
            spanning_labels=tuple((int(s.first_col), int(s.last_col), addr(s.words))
                                  for s in r.spanning_labels),
            other_words=addr(r.other_words),
            refuses_grid=bool(r.refuses_grid), cols_seen=int(r.cols_you_see),
            note=str(r.note or ""))
        _BOXHEAD_CACHE[key] = reading
        return reading


def header_block(lines, grid) -> tuple[int, ...]:
    """Page-line indices of the header block: the contiguous run of lines the grid REFUSED,
    directly above its first admitted row, top to bottom. PROCEDURAL — set arithmetic over the
    grid's own `rows` and `refusals`."""
    if grid is None or not grid.rows:
        return ()
    j, out = min(grid.rows) - 1, []
    while j >= 0 and j in grid.refusals:
        out.append(j)
        j -= 1
    return tuple(reversed(out))


def _ordered(line):
    return sorted(line.words, key=lambda w: w.x0)


def listing_of(lines, block) -> str:
    """The numbered listing the reader answers against: `L<k>: [0]word [1]word …`, where k is the
    line's position IN THE BLOCK (not its page index) and words run left to right."""
    return "\n".join(
        f"L{k}: " + " ".join(f"[{i}]{w.text}" for i, w in enumerate(_ordered(lines[j])))
        for k, j in enumerate(block))


def dispose_boxhead(reading, lines, block, grid) -> DisposedBoxhead:
    """The three checks of the module docstring. `lines` are the page's text lines; `block` is
    `header_block`'s output; `grid` is the derived DataGrid whose `columns` carry (x0, x1)."""
    if reading is None:
        return DisposedBoxhead(refused="no reading")
    if reading.refuses_grid:
        return DisposedBoxhead(refused="the reader does not see this grid")
    words = {(k, i): w for k, j in enumerate(block) for i, w in enumerate(_ordered(lines[j]))}
    ncols = len(grid.columns)

    claimed: list[Address] = list(reading.other_words)
    for _c, ws in reading.leaf_labels:
        claimed.extend(ws)
    for _a, _b, ws in reading.spanning_labels:
        claimed.extend(ws)
    if any(a not in words for a in claimed):
        return DisposedBoxhead(refused="an address outside the listing")
    if any(not (0 <= c < ncols) for c, _ in reading.leaf_labels) or any(
            not (0 <= a <= b < ncols) for a, b, _ in reading.spanning_labels):
        return DisposedBoxhead(refused="a column index outside the grid")
    if len(claimed) != len(set(claimed)):
        return DisposedBoxhead(refused="a word used twice")
    if set(claimed) != set(words):
        return DisposedBoxhead(refused="a listed word left unaccounted for")
    if len({c for c, _ in reading.leaf_labels}) != len(reading.leaf_labels):
        return DisposedBoxhead(refused="two leaf labels claim one column")

    labels, dropped = {}, []
    for c, ws in reading.leaf_labels:
        col = grid.columns[c]
        if ws and all(col.x0 <= (words[a].x0 + words[a].x1) / 2.0 < col.x1 for a in ws):
            labels[c] = tuple(sorted(ws))
        else:
            dropped.append(c)
    return DisposedBoxhead(labels=labels, spanners=tuple(reading.spanning_labels),
                           dropped=tuple(sorted(dropped)))


def label_text(lines, block, addresses) -> str:
    """A disposed label's text, read back from the TEXT LAYER by address — the reader never
    supplied it."""
    words = {(k, i): w for k, j in enumerate(block) for i, w in enumerate(_ordered(lines[j]))}
    return " ".join(words[a].text for a in sorted(addresses))


def read_grid_boxhead(pdf_path: str, page_number: int, lines, grid, reader,
                      data_rows_shown: int = 3) -> DisposedBoxhead:
    """One ask per grid. The crop runs from the top of the header block through the grid's first
    few data rows, so the reader sees which columns the labels head. Every failure path is NO
    CLAIM — a reader that cannot be reached, raises, or is refused labels nothing."""
    block = header_block(lines, grid)
    if reader is None or not block:
        return DisposedBoxhead(refused="no header block" if reader is not None else "no reader")
    from .unshownink import render_region
    shown = [lines[j] for j in block] + [lines[j] for j in sorted(grid.rows)[:data_rows_shown]]
    region = SimpleNamespace(lines=shown, top=min(ln.top for ln in shown),
                             bottom=max(ln.bottom for ln in shown))
    try:
        crop = render_region(pdf_path, page_number, region)
        reading = reader.read_boxhead(crop, len(grid.columns), listing_of(lines, block))
    except Exception:
        return DisposedBoxhead(refused="the reader raised")
    return dispose_boxhead(reading, lines, block, grid)
