"""printedtotal — "is this number, printed beneath a table, that table's total?", asked of a reader.

R261 spec § 3.2 (`docs/superpowers/specs/2026-10-01-r261-totals-family-design.md`). A lone number
printed beneath a table binds as its total only under a CONJUNCTION (ruling R-a): exact `Decimal`
arithmetic over one of the table's columns holds (`totals.py`, PROCEDURAL, the sole enforcement of
the sum, R89) AND a reader answers *yes* to a closed question. Arithmetic runs first; this module is
asked only on a match. This module asks the TABLE-LEVEL question only: the total-of-totals wording
of it was refuted by P3 (evidence § 6.4, controller ruling R4), so there is no `level` anywhere in
this module. The totals level (R261 loop (b), `docs/superpowers/specs/2026-10-02-r261-grand-total-
design.md`) asks a different, separately measured question in its own stack, `totalrole.py`
(`AskTotalRole`), which imports nothing from here.

§ 8 CLASSIFICATION (spec § 7), part by part:

  * the answer ("is it the table's total")            — NEURAL. `AskPrintedTotal`
    (`baml_src/printed_total.baml`) proposes a closed `yes | no | cannot_tell`. It is disposed by
    the arithmetic oracle, and the arithmetic by it: neither binds alone. A reader that is absent,
    raises, or answers outside the closed set is NO CLAIM, never a fallback (ruling R3).
  * the question (`listing_of`, `question_key`)       — PROCEDURAL: a rendering of the cropped
    lines' own words and a hash of it. It reads no geometry and has no constant.
  * the crop (`crop_table`)                           — PROCEDURAL raw extraction (page -> pixels),
    D7: the WHOLE table band through the candidate's own line, no line-count constant.
  * the closed-answer check (`PrintedTotalReading`)   — PROCEDURAL: a string is in the closed set
    or it is not.

The stack mirrors `headerlines.py`'s (Fake / Baml / Recorded readers, the question key, the
recorded readings directory, the late-bound `default_reader`) and deliberately imports nothing from
it: the workers ask different questions and must be free to diverge.
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

ANSWERS = ("yes", "no", "cannot_tell")

# The BAML function's name. It namespaces `question_key`, so another question over the same
# (value, listing) — `totalrole.QUESTION`, the totals level's `AskTotalRole` — cannot replay
# this question's recordings.
QUESTION = "AskPrintedTotal"


@dataclass(frozen=True)
class PrintedTotalReading:
    """The reader's answer, and nothing else: a closed enum with NO note field (spec § 3.2 — P1
    measured the note leaking page values). Constructing one outside the closed set raises, so an
    answer that is not `yes | no | cannot_tell` can never exist as a reading. PROCEDURAL."""
    answer: Literal["yes", "no", "cannot_tell"]

    def __post_init__(self):
        if self.answer not in ANSWERS:
            raise ValueError(f"not a closed answer: {self.answer!r} (expected one of {ANSWERS})")


class PrintedTotalReader(Protocol):
    def ask(self, crop_png: bytes, value: str, listing: str) -> "PrintedTotalReading | None": ...


@dataclass(frozen=True)
class FakePrintedTotalReader:
    """A fixed answer, for tests. PROCEDURAL — it returns what it was built with."""
    reading: "PrintedTotalReading | None"

    def ask(self, crop_png, value, listing):
        return self.reading


def baml_printed_total_available() -> bool:
    """PROCEDURAL — an environment gate: live only under `BAML_LIVE=1` with a generated client."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


# MODULE-GLOBAL, not per instance (the `headerlines._HEADER_LINES_CACHE` precedent): the binding
# calls `default_reader()` once per band, and the same page is compiled again by section repair's
# pass 2, so an instance cache would dedupe nothing. One live call per distinct question.
_PRINTED_TOTAL_CACHE: dict = {}

_FROM_BAML = {"YES": "yes", "NO": "no", "CANNOT_TELL": "cannot_tell"}


class BamlPrintedTotalReader:
    """The live reader: `AskPrintedTotal` on the `Claude` client. NEURAL — the model proposes.
    One call per distinct question for the whole process, keyed on the crop's content, the value
    and the listing. The listing is NOT sent to the model: P1 measured the wording with the image
    and the value only, and the listing exists to key the recording (`question_key`)."""

    def ask(self, crop_png, value, listing):
        key = (hashlib.sha256(crop_png).hexdigest(), str(value),
               hashlib.sha256(listing.encode("utf-8")).hexdigest())
        if key in _PRINTED_TOTAL_CACHE:
            return _PRINTED_TOTAL_CACHE[key]
        import base64
        from baml_py import Image
        from baml_client import sync_client
        r = sync_client.b.AskPrintedTotal(
            Image.from_base64("image/png", base64.b64encode(crop_png).decode("ascii")),
            str(value))
        raw = getattr(r.answer, "value", r.answer)
        reading = PrintedTotalReading(answer=_FROM_BAML.get(str(raw), str(raw)))
        _PRINTED_TOTAL_CACHE[key] = reading
        return reading


def _line_text(line) -> str:
    return " ".join(w.text for w in sorted(line.words, key=lambda w: w.x0))


def listing_of(table_band, band, line_no, line) -> str:
    """The question's text facts: every line the crop shows — the table band's lines, THEN the
    candidate's own band's lines 0..line_no-1 (the crop spans `table_band.top` through
    `line.bottom`, so it shows them too when the candidate sits at `line_no > 0` in its own band),
    THEN the candidate's line itself — numbered `L<k>`, words left to right. PROCEDURAL — a
    rendering of the cropped lines' own words; it decides nothing. It keys the recording; it is not
    sent to the model. `band.lines[:line_no]` is `()` when `line_no == 0`, so this reduces to the
    pre-fix listing exactly in that case — the only case the corpus has recorded (final review
    finding, item 2)."""
    lines = list(table_band.lines) + list(band.lines[:line_no]) + [line]
    return "\n".join(f"L{k}: {_line_text(ln)}" for k, ln in enumerate(lines))


def crop_table(pdf_path, page_no, band, line) -> bytes:
    """D7 table level: the WHOLE previous (table) band through the candidate's own line, as PNG.
    No tail-line constant. PROCEDURAL raw extraction (page -> pixels): it reads no colour and
    decides nothing; the bytes go to a reader, never to a comparison.

    MOVED VERBATIM from `scripts/r261_total_question_probe.py` (controller ruling R2), which now
    imports it: P1 was measured on exactly this crop (evidence § 6.5), so the 4 pt margin and the
    150 dpi render are the measured instrument's, carried unchanged rather than re-chosen. They are
    rendering parameters of the image a reader sees, not a tolerance on any decision —
    `unshownink.render_region` carries the same kind of margin."""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        words = [w for ln in band.lines for w in ln.words] + list(line.words)
        top, bot = band.top, line.bottom
        box = (max(0, min(w.x0 for w in words) - 4), max(0, top - 4),
               min(float(page.width), max(w.x1 for w in words) + 4), min(float(page.height), bot + 4))
        im = page.crop(box).to_image(resolution=150)
        buf = io.BytesIO(); im.original.save(buf, format="PNG"); return buf.getvalue()


# ---------------------------------------------------------------------------------------------
# RECORDED READINGS — the proposal, kept, and re-checked against the closed set on every compile
# ---------------------------------------------------------------------------------------------
#
# THE KEY IS THE QUESTION: sha256 of the question's name, the value and the listing — text facts
# only, NEVER the PNG (a render can differ by a byte across library versions while the question
# is the same). The listing holds every cropped line, so a recording answers exactly one
# question, and moves when any word of the table or of the candidate line does.

READINGS_DIR = pathlib.Path(__file__).resolve().parents[3] / "readings" / "printed_total"


def question_key(value: str, listing: str) -> str:
    """PROCEDURAL — sha256 of `f"{QUESTION}\\n{value}\\n{listing}"`."""
    return hashlib.sha256(f"{QUESTION}\n{value}\n{listing}".encode("utf-8")).hexdigest()


@dataclass
class RecordedPrintedTotalReader:
    """Replays a recorded reading; on a miss, asks `live` (if any) and — only when
    `ILADUB_RECORD_READINGS=1` — writes the answer down. With no recording and no live reader it
    returns None: no claim. PROCEDURAL — a lookup; the answer it replays was the reader's.

    `directory` defaults to the module's `READINGS_DIR` AT CALL TIME, so a test that patches the
    module attribute is honoured (a dataclass default would have bound it at import)."""
    live: "PrintedTotalReader | None" = None
    directory: "pathlib.Path | None" = None

    def ask(self, crop_png, value, listing):
        directory = self.directory if self.directory is not None else READINGS_DIR
        path = directory / f"{question_key(value, listing)}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return PrintedTotalReading(answer=str(d["answer"]))
        if self.live is None:
            return None
        reading = self.live.ask(crop_png, value, listing)
        if reading is not None and os.environ.get("ILADUB_RECORD_READINGS") == "1":
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"answer": reading.answer}, indent=1, sort_keys=True)
                            + "\n", encoding="utf-8")
        return reading


def default_reader() -> RecordedPrintedTotalReader:
    """Recorded first; the live reader behind it only when `BAML_LIVE=1`. PROCEDURAL wiring.
    `compile.py` looks it up on this module at call time, so a test's patch reaches it."""
    return RecordedPrintedTotalReader(
        live=BamlPrintedTotalReader() if baml_printed_total_available() else None)


def ask_printed_total(pdf_path: str, page_number: int, table_band, band, line_no: int, line,
                      value: str,
                      reader: "PrintedTotalReader | None") -> "PrintedTotalReading | None":
    """One ask per arithmetic match: the D7 crop, the printed value as the page prints it, and
    the listing. `band` is the candidate's OWN band (`totals.candidate_lines` was run over it) and
    `line_no` is the candidate's index within `band.lines` — both needed so `listing_of` can
    include the candidate band's own lines before the candidate (final review finding, item 2).

    Returns None — NO CLAIM, never a fallback (ruling R3) — in four cases: no reader; the reader
    (or the render) raised, which includes an answer outside the closed set, since
    `PrintedTotalReading` refuses to construct one; the reader returned None; the reader returned
    something that is not a `PrintedTotalReading`. PROCEDURAL — it decides nothing; the answer is
    the reader's (NEURAL), and the binding (`compile._bind_printed_totals`) applies it."""
    if reader is None:
        return None
    try:
        crop = crop_table(pdf_path, page_number, table_band, line)
        reading = reader.ask(crop, value, listing_of(table_band, band, line_no, line))
    except Exception:
        return None
    if not isinstance(reading, PrintedTotalReading):
        return None
    return reading
