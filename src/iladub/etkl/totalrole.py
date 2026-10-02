"""totalrole — "what role does this number play — a table's own total, or a total that sums
several tables' totals?", asked of a reader, of the DERIVED crop over every candidate total's
operands (R261 loop (b), spec § 3, `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md`).

A grand total sits beneath several per-table totals with identical typography — arithmetic alone
(`totals.match_totals`) cannot tell "sums the operand totals" from "is one more table total" or "is
a value inside a table." That is a reading judgement a person makes at a glance (CLAUDE.md § 8, "One
geometric attempt, then NEURAL"), so it is asked of `AskTotalRole` (`baml_src/total_role.baml`) and
disposed by the arithmetic that must ALSO hold — the same conjunction shape as `printedtotal.py`'s
table level (ruling R-a), never a fallback (ruling R3: a reader absent, raising, or answering outside
the closed set is NO CLAIM).

**Two questions, two stacks (spec § 3): this module mirrors `printedtotal.py`'s reader stack name
for name — frozen reading, reader protocol, fake reader, process cache, BAML reader, recorded reader,
`question_key`, `READINGS_DIR`, late-bound `default_reader` — and deliberately IMPORTS NOTHING from
it.** A shared stack would couple a measured instrument (table level, corpus-validated) to an
unmeasured one (this level); the small pieces (`_line_text`, the key formula) are duplicated on
purpose.

§ 8 CLASSIFICATION (spec § 9), part by part:

  * the answer ("what role does this number play")     — NEURAL. `AskTotalRole` proposes a closed
    `table_total | total_of_totals | other | cannot_tell`, disposed by the arithmetic oracle
    (`totals.match_totals`) and vice versa: neither binds alone (a later task's binding, not here).
  * the question (`listing_of`, `question_key`)         — PROCEDURAL: a rendering of the cropped
    lines' own words and a hash of it. It reads no geometry and has no constant.
  * the crop and its red box (`crop_box`, `render_crop`) — PROCEDURAL raw extraction (page ->
    pixels): `crop_box` is pure geometry over already-extracted `Operand`s and the candidate line
    (D-e/N8, `scripts/r261_grand_total_role_probe.py` `derived_box`) — no PDF read, no tuned
    constant beyond the measured instrument's 4 pt margin, carried unchanged. `render_crop` is raw
    pixel extraction at the measured instrument's 150 dpi / 2 pt stroke; it is the ONLY place the
    red box exists — the box is ink not on the page, never stored, never compared, never reaching
    the graph (spec § 3).
  * the closed-answer check (`TotalRoleReading`)        — PROCEDURAL: a string is in the closed set
    or it is not.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import pathlib
from dataclasses import dataclass
from typing import Literal, Protocol

ANSWERS = ("table_total", "total_of_totals", "other", "cannot_tell")

# The BAML function's name. It namespaces `question_key`, so `AskPrintedTotal`'s recordings for the
# same (value, listing) cannot replay here, and this question's cannot replay there.
QUESTION = "AskTotalRole"


@dataclass(frozen=True)
class TotalRoleReading:
    """The reader's answer, and nothing else: a closed enum with NO note field (spec § 3 — the same
    never-quote discipline as `PrintedTotalReading`, P1's note leaked page values). Constructing one
    outside the closed set raises, so an answer that is not one of `ANSWERS` can never exist as a
    reading. PROCEDURAL."""
    answer: Literal["table_total", "total_of_totals", "other", "cannot_tell"]

    def __post_init__(self):
        if self.answer not in ANSWERS:
            raise ValueError(f"not a closed answer: {self.answer!r} (expected one of {ANSWERS})")


class TotalRoleReader(Protocol):
    def ask(self, crop_png: bytes, value: str, listing: str) -> "TotalRoleReading | None": ...


@dataclass(frozen=True)
class FakeTotalRoleReader:
    """A fixed answer, for tests. PROCEDURAL — it returns what it was built with."""
    reading: "TotalRoleReading | None"

    def ask(self, crop_png, value, listing):
        return self.reading


def baml_total_role_available() -> bool:
    """PROCEDURAL — an environment gate: live only under `BAML_LIVE=1` with a generated client."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


# MODULE-GLOBAL, not per instance (the `printedtotal._PRINTED_TOTAL_CACHE` precedent): the binding
# calls `default_reader()` once per band, and the same page is compiled again by section repair's
# pass 2, so an instance cache would dedupe nothing. One live call per distinct question.
_TOTAL_ROLE_CACHE: dict = {}

# The generated `TotalRoleAnswer(str, Enum)` member VALUES are the uppercase NAMES
# (`baml_client/types.py`), not the `@alias(...)` the prompt renders (measured in Task 1, mirroring
# `printedtotal._FROM_BAML`). Translate before comparing against `ANSWERS`.
_FROM_BAML = {"TABLE_TOTAL": "table_total", "TOTAL_OF_TOTALS": "total_of_totals",
              "OTHER": "other", "CANNOT_TELL": "cannot_tell"}


class BamlTotalRoleReader:
    """The live reader: `AskTotalRole` on the `Claude` client. NEURAL — the model proposes.
    One call per distinct question for the whole process, keyed on the crop's content, the value
    and the listing — the same key shape as `printedtotal.BamlPrintedTotalReader`. The listing is
    NOT sent to the model: it exists to key the recording (`question_key`)."""

    def ask(self, crop_png, value, listing):
        key = (hashlib.sha256(crop_png).hexdigest(), str(value),
               hashlib.sha256(listing.encode("utf-8")).hexdigest())
        if key in _TOTAL_ROLE_CACHE:
            return _TOTAL_ROLE_CACHE[key]
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.AskTotalRole(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            str(value))
        raw = getattr(r.answer, "value", r.answer)
        reading = TotalRoleReading(answer=_FROM_BAML.get(str(raw), str(raw)))
        _TOTAL_ROLE_CACHE[key] = reading
        return reading


def _line_text(line) -> str:
    """One line's words, left to right. PROCEDURAL — a rendering of words the extractor already
    placed, reused (not imported, module docstring) from `printedtotal.py`'s precedent; it decides
    nothing and carries no constant."""
    return " ".join(w.text for w in sorted(line.words, key=lambda w: w.x0))


@dataclass(frozen=True)
class Operand:
    """One candidate total's operand: the table band it is printed beneath (intact — only the
    operand's OWN total line is carved out of a band, never the table above it), its printed value,
    and its own `tab:PrintedTotal`'s box. By the time a grand-total candidate is reached, the
    operand's total LINE has already been carved out of its band (N4: `bands[j]` keeps only
    `top`/`bottom`) — its extent survives only as `tab:hasBBox`, read off the graph as `xsd:decimal`
    literals and converted to `float` ONCE here, at construction, never re-converted per use.
    PROCEDURAL — a data carrier; it decides nothing."""
    table_band: "object"
    total_text: str
    total_box: "tuple[float, float, float, float]"

    def __post_init__(self):
        object.__setattr__(self, "total_box", tuple(float(c) for c in self.total_box))


def crop_box(page_width: float, page_height: float, operands: "list[Operand]", line) -> \
        "tuple[float, float, float, float]":
    """N8's `derived_box` rule (`scripts/r261_grand_total_role_probe.py`), generalised from real
    table-band words (the probe, pre-carve) to the post-carve shape this module actually has: each
    operand's table band is intact (its words are read directly), but the operand's OWN total line
    is gone, so its extent is read from `total_box` instead of from words. Top = the minimum
    operand table-band `top`, minus the measured instrument's 4 pt margin. Bottom = the maximum of
    every operand's `total_box` bottom and the candidate `line`'s bottom, plus 4 pt. Left/right =
    the extreme x of every operand table-band word, every `total_box`, and every candidate word,
    minus/plus 4 pt. Clamped to the page. PROCEDURAL raw extraction (page -> pixels): pure geometry
    over already-extracted data, no PDF read, no tuned constant beyond the measured 4 pt margin
    (`printedtotal.crop_table`'s docstring: a rendering parameter of the image a reader sees, not a
    tolerance on any decision); it returns a box and renders nothing."""
    xs0: list[float] = []
    xs1: list[float] = []
    tops: list[float] = []
    bottoms: list[float] = []
    for op in operands:
        tops.append(op.table_band.top)
        xs0.append(op.total_box[0])
        xs1.append(op.total_box[2])
        bottoms.append(op.total_box[3])
        for ln in op.table_band.lines:
            for w in ln.words:
                xs0.append(w.x0)
                xs1.append(w.x1)
    for w in line.words:
        xs0.append(w.x0)
        xs1.append(w.x1)
    bottoms.append(line.bottom)
    return (max(0.0, min(xs0) - 4), max(0.0, min(tops) - 4),
            min(float(page_width), max(xs1) + 4), min(float(page_height), max(bottoms) + 4))


def render_crop(pdf_path: str, page_no: int, box: "tuple[float, float, float, float]",
                word) -> bytes:
    """The DERIVED crop, annotated with the red box on the candidate `word`, as PNG — N8's
    rendering: 150 dpi, red rect `word` ± 2 pt, stroke width 2, saved from `im.annotated` exactly as
    `scripts/r261_grand_total_role_probe.py` draws it. PROCEDURAL raw extraction (page -> pixels):
    it reads no colour off the page and decides nothing; the bytes go to a reader, never to a
    comparison. THE ONLY PLACE THE RED BOX EXISTS — it is ink not on the page, a pointer like the
    value string in the prompt, never stored, never compared, never reaching the graph (spec § 3)."""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        im = page.crop(box).to_image(resolution=150)
        im.draw_rect((word.x0 - 2, word.top - 2, word.x1 + 2, word.bottom + 2),
                     fill=None, stroke="red", stroke_width=2)
        buf = io.BytesIO()
        im.annotated.save(buf, format="PNG")
        return buf.getvalue()


def listing_of(operands: "list[Operand]", band, line_no: int, line) -> str:
    """The question's text facts, in operand order (D6, a caller concern — this function takes
    `operands` already ordered): each operand's table-band lines, THEN that operand's own total text
    (its `tab:cellText`, since the total LINE itself is carved away and has no `Line` to render) —
    for every operand in turn — THEN the candidate's own band's lines `0..line_no-1` (the LISTING
    carries them too, the `printedtotal.listing_of` fix carried here — NOT the crop: `crop_box`
    never includes their x extent, so over-listing only makes the recording key stricter, never
    the image wider), THEN the candidate line itself —
    numbered `L<k>`, words left to right. PROCEDURAL — a rendering of the cropped lines' own words;
    it decides nothing. It keys the recording; it is not sent to the model."""
    lines_text: list[str] = []
    for op in operands:
        for ln in op.table_band.lines:
            lines_text.append(_line_text(ln))
        lines_text.append(op.total_text)
    for ln in band.lines[:line_no]:
        lines_text.append(_line_text(ln))
    lines_text.append(_line_text(line))
    return "\n".join(f"L{k}: {t}" for k, t in enumerate(lines_text))


# ---------------------------------------------------------------------------------------------
# RECORDED READINGS — the proposal, kept, and re-checked against the closed set on every compile
# ---------------------------------------------------------------------------------------------
#
# THE KEY IS THE QUESTION: sha256 of the question's name, the value and the listing — text facts
# only, NEVER the PNG. The listing holds every operand table band's lines plus the candidate's, so
# a recording answers exactly one question, and moves when any word of any operand table, or of the
# candidate line, changes.

READINGS_DIR = pathlib.Path(__file__).resolve().parents[3] / "readings" / "total_role"


def question_key(value: str, listing: str) -> str:
    """PROCEDURAL — sha256 of `f"{QUESTION}\\n{value}\\n{listing}"`."""
    return hashlib.sha256(f"{QUESTION}\n{value}\n{listing}".encode("utf-8")).hexdigest()


@dataclass
class RecordedTotalRoleReader:
    """Replays a recorded reading; on a miss, asks `live` (if any) and — only when
    `ILADUB_RECORD_READINGS=1` — writes the answer down. With no recording and no live reader it
    returns None: no claim. PROCEDURAL — a lookup; the answer it replays was the reader's.

    `directory` defaults to the module's `READINGS_DIR` AT CALL TIME, so a test that patches the
    module attribute is honoured (a dataclass default would have bound it at import) —
    `printedtotal.RecordedPrintedTotalReader`'s precedent."""
    live: "TotalRoleReader | None" = None
    directory: "pathlib.Path | None" = None

    def ask(self, crop_png, value, listing):
        directory = self.directory if self.directory is not None else READINGS_DIR
        path = directory / f"{question_key(value, listing)}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return TotalRoleReading(answer=str(d["answer"]))
        if self.live is None:
            return None
        reading = self.live.ask(crop_png, value, listing)
        if reading is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"answer": reading.answer}, indent=1, sort_keys=True)
                            + "\n", encoding="utf-8")
        return reading


def default_reader() -> RecordedTotalRoleReader:
    """Recorded first; the live reader behind it only when `BAML_LIVE=1`. PROCEDURAL wiring.
    The caller looks it up on this module at call time, so a test's patch reaches it."""
    return RecordedTotalRoleReader(
        live=BamlTotalRoleReader() if baml_total_role_available() else None)


def ask_total_role(pdf_path: str, page_number: int, operands: "list[Operand]", band, line_no: int,
                   line, value: str, reader: "TotalRoleReader | None") -> "TotalRoleReading | None":
    """One ask per arithmetic match (a later task's binding calls this only when
    `totals.match_totals` holds): the derived crop with the red box on the candidate's own word, the
    printed value as the page prints it, and the listing.

    Returns None — NO CLAIM, never a fallback (ruling R3) — in four cases: no reader; the reader (or
    the crop/render) raised, which includes an answer outside the closed set, since
    `TotalRoleReading` refuses to construct one; the reader returned None; the reader returned
    something that is not a `TotalRoleReading`. PROCEDURAL — it decides nothing; the answer is the
    reader's (NEURAL), and the binding applies it."""
    if reader is None:
        return None
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_number]
            box = crop_box(float(page.width), float(page.height), operands, line)
        word = line.words[0]
        crop = render_crop(pdf_path, page_number, box, word)
        reading = reader.ask(crop, value, listing_of(operands, band, line_no, line))
    except Exception:
        return None
    if not isinstance(reading, TotalRoleReading):
        return None
    return reading
