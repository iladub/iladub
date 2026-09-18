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


# ---------------------------------------------------------------------------------------------
# RECORDED READINGS — a NEURAL proposal, kept, and disposed again on every compile
# ---------------------------------------------------------------------------------------------
#
# A live reading costs money and differs run to run; a compile must be reproducible offline or no
# score it produces can be pinned as a floor. So a reading is RECORDED once and replayed: the
# recording is the PROPOSAL (addresses only, exactly what the reader returned), and
# `dispose_boxhead` runs against it on every compile — the oracle never trusts the file.
#
# THE KEY IS THE QUESTION, not the pixels: sha256 of the column count and the numbered listing,
# both derived from the text layer. A PNG hash would move with the renderer's version; the
# listing moves only when the document's own header text or the grid's column count does, and
# then the recording SHOULD miss, because it answers a question nobody is asking any more.

import json
import pathlib

READINGS_DIR = pathlib.Path(__file__).resolve().parents[3] / "readings" / "boxhead"


def question_key(ncols: int, listing: str) -> str:
    return hashlib.sha256(f"{int(ncols)}\n{listing}".encode("utf-8")).hexdigest()


def _to_json(r: BoxheadReading) -> dict:
    return {"refuses_grid": r.refuses_grid, "cols_seen": r.cols_seen, "note": r.note,
            "leaf_labels": [[c, [list(a) for a in ws]] for c, ws in r.leaf_labels],
            "spanning_labels": [[a, b, [list(x) for x in ws]] for a, b, ws in r.spanning_labels],
            "other_words": [list(a) for a in r.other_words]}


def _from_json(d: dict) -> BoxheadReading:
    t = lambda ws: tuple((int(a[0]), int(a[1])) for a in ws)             # noqa: E731
    return BoxheadReading(
        leaf_labels=tuple((int(c), t(ws)) for c, ws in d.get("leaf_labels", [])),
        spanning_labels=tuple((int(a), int(b), t(ws)) for a, b, ws in d.get("spanning_labels", [])),
        other_words=t(d.get("other_words", [])),
        refuses_grid=bool(d.get("refuses_grid", False)), cols_seen=int(d.get("cols_seen", 0)),
        note=str(d.get("note", "")))


@dataclass
class RecordedBoxheadReader:
    """Replays a recorded reading; on a miss, asks `live` (if any) and — only when
    `ILADUB_RECORD_READINGS=1` — writes the answer down. With no recording and no live reader it
    returns None, which every caller already treats as NO CLAIM."""
    live: "BoxheadReader | None" = None
    directory: pathlib.Path = READINGS_DIR

    def read_boxhead(self, crop_png, ncols, listing):
        path = self.directory / f"{question_key(ncols, listing)}.json"
        if path.exists():
            return _from_json(json.loads(path.read_text(encoding="utf-8")))
        if self.live is None:
            return None
        reading = self.live.read_boxhead(crop_png, ncols, listing)
        if reading is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            self.directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(_to_json(reading), indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        return reading


def default_reader() -> RecordedBoxheadReader:
    """Recorded first, live behind it only when `BAML_LIVE=1`."""
    return RecordedBoxheadReader(live=BamlBoxheadReader() if baml_boxhead_available() else None)


# ---------------------------------------------------------------------------------------------
# CARRIAGE — the labels into the graph, and their ink into the ledger
# ---------------------------------------------------------------------------------------------

def carried_lines(lines, block, disposed: DisposedBoxhead) -> tuple[int, ...]:
    """Page-line indices of the header lines that were READ IN FULL: every word of the line
    belongs to a label that survived disposal. The adoption ledger is line-granular (spec §5.3),
    so a line with one unread word — a spanner, a title, a dropped label — is not carried and
    stays where the ledger already books it. Never rounds up."""
    kept = {a for ws in disposed.labels.values() for a in ws}
    return tuple(j for k, j in enumerate(block)
                 if lines[j].words and all((k, i) in kept for i in range(len(lines[j].words))))


def emit_boxhead(g, grid_uri, lines, block, disposed: DisposedBoxhead, page: int) -> int:
    """One `tab:HeaderNode` + `tab:LabelCell` per disposed label, in the shape
    `holon.assert_record_region` gives a record table's header: level 0, `tab:coversColumn` the
    grid's own column node, the label's text read back from the TEXT LAYER by address, and a box
    that is the union of its words (provenance to the page; the membrane requires the box of any
    LabelCell that carries text — R179). Returns the number of labels emitted."""
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, XSD
    from .holon import TAB, _bbox_node
    words = {(k, i): w for k, j in enumerate(block) for i, w in enumerate(_ordered(lines[j]))}
    for c, ws in sorted(disposed.labels.items()):
        h, lc = URIRef(f"{grid_uri}-h{c}"), URIRef(f"{grid_uri}-lc{c}")
        own = [words[a] for a in sorted(ws)]
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, URIRef(f"{grid_uri}-c{c}")))
        g.add((grid_uri, TAB.hasHeaderNode, h))
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((grid_uri, TAB.hasCell, lc))
        g.add((lc, TAB.cellText, Literal(" ".join(w.text for w in own))))
        g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
        g.add((lc, TAB.hasBBox, _bbox_node(g, SimpleNamespace(bbox=(
            min(w.x0 for w in own), min(w.top for w in own),
            max(w.x1 for w in own), max(w.bottom for w in own))))))
        g.add((h, TAB.hasLabel, lc))
    return len(disposed.labels)
