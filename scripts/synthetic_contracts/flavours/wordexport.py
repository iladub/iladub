"""The Word export flavour (spec 2026-10-31 § 4.3; owner decisions 6 and 10).

The template is rebuilt as a Word document from its own REAL text, extracted at build time, and
exported to PDF by Microsoft Word (`word.export_pdf`). The values are carried inline in that text:
each blank's dot-leader run is replaced by its value, in the font of the line it sits in.

How the template is carried (raw extraction, no reading judgement):
- every template line (pdfplumber words, joined into lines by `top` with pdfplumber's own default
  line tolerance) becomes one Word paragraph, in the template's order, with its words' own font
  family, size, weight and slant; each template page after the first starts with a page break, so
  template page N is output page N or the build refuses (see below);
- each mapped table becomes a Word table on the hand-measured grid of the map (`TableGrid`): column
  widths from the grid, each cell holding the template words whose centre lies in that cell;
- nothing is classified: no line is promoted to a heading (that would be a reading judgement),
  bold text stays bold because the template's glyphs are bold.

Truth is located in Word's output, never predicted (spec § 4.5: "the Word flavour records where its
own layout put each part"), by exact matching of strings this generator wrote (`locate`), which
refuses on 0 or > 1 hits:
- a value's box is `locate(value)` over the whole document; its blank part's box is the same box;
- a sub-page part (a table) is, per page, the union of `locate(first line)` and `locate(last line)`
  of its text on that output page (a table's line = its row's cells' k-th lines, joined);
- a top-level part whose map box is the whole template page is the whole output page, on the same
  page number. That page correspondence is checked, not assumed: the first and the last line of
  every template page must each occur on the output page of the same number exactly as many times as
  the generator wrote that string among that page's lines (usually once; a short last line such as a
  lone word may legitimately recur on its page), and the output must have exactly the template's page
  count; otherwise the build refuses. A line that overflowed to the next page fails the count.

Template text is written only under the gitignored `synthetic/` (the .docx and the PDF), never into
a committed file (spec § 3).

Justified PROCEDURAL (CLAUDE.md § 8): this module MAKES a document. Its two reads are raw extraction
of the template's text layer (at build time) and decidable exact matching of strings it wrote, in
the output it made. LINE_PITCH and the page margin are generation parameters (how to lay text out),
not reading tolerances. No reader may call it (A3).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from io import BytesIO
from pathlib import Path

from pdfplumber.utils import cluster_objects
from pdfplumber.utils.text import DEFAULT_Y_TOLERANCE

from scripts.synthetic_contracts.docx_writer import Block, Page, Paragraph, Run, Table, write_docx
from scripts.synthetic_contracts.fills import Fill
from scripts.synthetic_contracts.flavours.formfill import map_parts
from scripts.synthetic_contracts.locate import hits, locate_in
from scripts.synthetic_contracts.manifest import SYNTH_ROOT, Template, template_path, verify
from scripts.synthetic_contracts.maps import Box, Part, PartMap, TableGrid
from scripts.synthetic_contracts.truth import PartTruth, Truth, ValueTruth

FLAVOUR = "word-export"
WORK_DIR = SYNTH_ROOT / "word"
LINE_PITCH = 1.15   # exact line pitch as a multiple of the line's largest size; generation parameter
MARGIN = 28.0       # pt, page margin of the Word document; generation parameter
LEADERS = frozenset("._…")
# PostScript family names -> the family Word knows them by (fonts absent in Word are substituted
# by Word itself; LiberationMono is a Courier New metric clone).
FAMILY = {"TimesNewRomanPSMT": "Times New Roman", "TimesNewRoman": "Times New Roman",
          "LiberationMono": "Courier New", "SymbolMT": "Symbol", "Wingdings": "Wingdings"}


class BuildRefused(Exception):
    pass


# ------------------------------------------------------------------ raw extraction (build time)

def _inside(w, b: Box) -> bool:
    cx, cy = (w["x0"] + w["x1"]) / 2, (w["top"] + w["bottom"]) / 2
    return b.x0 <= cx <= b.x1 and b.top <= cy <= b.bottom


def _words(page) -> list[dict]:
    return page.extract_words(return_chars=True)


def _lines(words) -> list[list[dict]]:
    """pdfplumber's own line clustering (its default y tolerance), top to bottom, left to right."""
    rows = cluster_objects(words, "top", DEFAULT_Y_TOLERANCE)
    return [sorted(r, key=lambda w: w["x0"]) for r in sorted(rows, key=lambda r: min(w["top"] for w in r))]


def template_lines(pdf, part: Part) -> list[str]:
    """The template's words inside the part's boxes (by word centre), joined into lines by `top`."""
    out = []
    for b in part.box:
        ws = [w for w in _words(pdf.pages[b.page - 1]) if _inside(w, b)]
        out += [" ".join(w["text"] for w in line) for line in _lines(ws)]
    return out


def _cells(g: TableGrid):
    return [[Box(g.page, c0, r0, c1, r1) for c0, c1 in zip(g.col_edges, g.col_edges[1:])]
            for r0, r1 in zip(g.row_edges, g.row_edges[1:])]


def grid_cells(pdf, g: TableGrid) -> list[list[str]]:
    """The text of each hand-measured cell: the template words whose centre lies in it, in lines.

    Words are assigned whole, by centre, rather than cropped char by char: a header word set across
    two grid columns (a merged cell) would otherwise be cut in two (measured on 79B clause 7)."""
    ws = _words(pdf.pages[g.page - 1])
    return [["\n".join(" ".join(w["text"] for w in line)
                       for line in _lines([w for w in ws if _inside(w, c)])) for c in row]
            for row in _cells(g)]


# ------------------------------------------------------------------ building the document

@dataclass(frozen=True)
class _Tok:
    text: str
    font: str
    size: float
    bold: bool
    italic: bool


def _style(char) -> tuple[str, float, bool, bool]:
    name = char["fontname"].split("+", 1)[-1]
    fam, _, style = name.partition("-")
    s = style.lower()
    return (FAMILY.get(fam, FAMILY.get(name, fam)), round(char["size"] * 2) / 2,
            "bold" in s or "black" in s, "italic" in s or "oblique" in s)


def _clean(s: str) -> str:
    return "".join(ch for ch in s if ch >= " " or ch == "\t")


def _tokens(line, blanks, values, used) -> list[_Tok]:
    """A line's words as styled tokens, each blank's leader chars replaced by its value."""
    out = []
    for w in line:
        style = _style(w["chars"][0])
        seg, seg_blank = [], None
        pieces = []  # (text, blank-field or None)
        for ch in w["chars"]:
            mark = None
            if ch["text"] in LEADERS:
                for b in blanks:
                    if _inside(ch, b.box):
                        mark = b.field
                        break
            if mark != seg_blank and seg:
                pieces.append(("".join(seg), seg_blank))
                seg = []
            seg_blank = mark
            seg.append(ch["text"])
        if seg:
            pieces.append(("".join(seg), seg_blank))
        for text, field in pieces:
            if field is None:
                out.append(_Tok(_clean(text), *style))
            else:
                if field in used:
                    raise BuildRefused(f"blank {field}: leader run not contiguous")
                used.add(field)
                out.append(_Tok(values[field], *style))
    return [t for t in out if t.text]


def _paragraph(toks: list[_Tok], page_break: bool) -> tuple[Paragraph, str]:
    runs, text = [], " ".join(t.text for t in toks)
    for i, t in enumerate(toks):
        s = (" " if i else "") + t.text
        key = (t.font, t.size, t.bold, t.italic)
        if runs and (runs[-1].font, runs[-1].size, runs[-1].bold, runs[-1].italic) == key:
            runs[-1] = replace(runs[-1], text=runs[-1].text + s)
        else:
            runs.append(Run(s, *key))
    pitch = round(LINE_PITCH * max(t.size for t in toks), 1)
    return Paragraph(tuple(runs), page_break_before=page_break, line_pt=pitch), text


def _row_lines(cells: list[list[str]]) -> list[str]:
    """A table's text lines as they lay out: per row, the k-th line of each cell, joined."""
    out = []
    for row in cells:
        split = [c.split("\n") if c else [] for c in row]
        for k in range(max((len(c) for c in split), default=0)):
            s = " ".join(c[k] for c in split if len(c) > k)
            if s:
                out.append(s)
    return out


@dataclass(frozen=True)
class _Layout:
    blocks: list[Block]
    page_lines: dict[int, tuple[str, ...]]          # template page -> every line written for it
    table_lines: dict[tuple[str, int], tuple[str, str]]  # (part id, page) -> (first, last)


def build_blocks(pdf, m: PartMap, f: Fill) -> _Layout:
    blanks_by_page: dict[int, list] = {}
    for b in m.blanks:
        blanks_by_page.setdefault(b.box.page, []).append(b)
    tables = {p.id: p for p in m.parts if p.type == "table"}
    used: set[str] = set()
    blocks: list[Block] = []
    page_lines, table_lines = {}, {}
    for n, page in enumerate(pdf.pages, 1):
        ws = _words(page)
        grids = sorted((g for g in m.grids if g.page == n), key=lambda g: g.row_edges[0])
        tboxes = {g.part: next(b for b in tables[g.part].box if b.page == n) for g in grids}
        for g in grids:
            cells = sum(_cells(g), [])
            stray = [w["text"] for w in ws if _inside(w, tboxes[g.part])
                     and not any(_inside(w, c) for c in cells)]
            if stray:
                raise BuildRefused(f"{g.part}: {len(stray)} word(s) in the part but in no grid cell")
        free = [w for w in ws if not any(_inside(w, tb) for tb in tboxes.values())]
        items = [(min(w["top"] for w in line), "line", line) for line in _lines(free)]
        items += [(g.row_edges[0], "table", g) for g in grids]
        texts = []
        first_on_page = True
        for _, kind, obj in sorted(items, key=lambda it: (it[0], it[1])):
            if kind == "line":
                toks = _tokens(obj, blanks_by_page.get(n, []), f.values, used)
                if not toks:
                    continue
                para, text = _paragraph(toks, page_break=(n > 1 and first_on_page))
                blocks.append(para)
                texts.append(text)
            else:
                if first_on_page and n > 1:
                    blocks.append(Paragraph((), page_break_before=True, line_pt=1.0))
                cells = grid_cells(pdf, obj)
                if any(b.box.page == n and _inside_box(b.box, tboxes[obj.part])
                       for b in m.blanks):
                    raise BuildRefused(f"{obj.part}: a blank inside a table is not supported")
                lines = _row_lines(cells)
                if not lines:
                    raise BuildRefused(f"{obj.part}: table has no text")
                table_lines[(obj.part, n)] = (lines[0], lines[-1])
                first = next(w for w in ws if _inside(w, tboxes[obj.part]))
                font, size, _, _ = _style(first["chars"][0])
                widths = tuple(b - a for a, b in zip(obj.col_edges, obj.col_edges[1:]))
                blocks.append(Table(tuple(tuple(tuple(c.split("\n")) if c else () for c in row)
                                          for row in cells), widths, font, size))
                texts += lines
            first_on_page = False
        if not texts:
            raise BuildRefused(f"template page {n} has no text")
        page_lines[n] = tuple(texts)
    missing = sorted({b.field for b in m.blanks} - used)
    if missing:
        raise BuildRefused(f"no leader run found for blank(s): {', '.join(missing)}")
    return _Layout(blocks, page_lines, table_lines)


def _inside_box(a: Box, b: Box) -> bool:
    return b.x0 <= (a.x0 + a.x1) / 2 <= b.x1 and b.top <= (a.top + a.bottom) / 2 <= b.bottom


def _union(a: Box, b: Box) -> Box:
    if a.page != b.page:
        raise BuildRefused(f"first and last line on different output pages ({a.page}, {b.page})")
    return Box(a.page, min(a.x0, b.x0), min(a.top, b.top), max(a.x1, b.x1), max(a.bottom, b.bottom))


# ------------------------------------------------------------------ the flavour

def render_wordexport(t: Template, m: PartMap, f: Fill, work_dir: Path = WORK_DIR
                      ) -> tuple[bytes, Truth]:
    import pdfplumber

    from scripts.synthetic_contracts.word import export_pdf

    verify(t)
    if m.template != t.id or f.template != t.id:
        raise ValueError(f"template {t.id}, map {m.template} and fill {f.id} disagree")
    if set(f.values) != {b.field for b in m.blanks}:
        raise ValueError(f"fill {f.id} does not fill exactly the blanks of map {m.template}")
    doc_id = f"{f.id}.{FLAVOUR}"
    docx, out_pdf = Path(work_dir) / f"{doc_id}.docx", Path(work_dir) / f"{doc_id}.pdf"
    with pdfplumber.open(template_path(t)) as tpl:
        lay = build_blocks(tpl, m, f)
        w, h = tpl.pages[0].width, tpl.pages[0].height
        tsize = {n: (p.width, p.height) for n, p in enumerate(tpl.pages, 1)}
        write_docx(lay.blocks, docx, Page(w, h, MARGIN))
    export_pdf(docx, out_pdf)
    pdf_bytes = out_pdf.read_bytes()
    with pdfplumber.open(BytesIO(pdf_bytes)) as out:
        if len(out.pages) != t.pages:
            raise BuildRefused(f"{doc_id}: Word made {len(out.pages)} pages, template has {t.pages}")
        osize = {n: (p.width, p.height) for n, p in enumerate(out.pages, 1)}
        for n, texts in lay.page_lines.items():  # the page correspondence, checked
            for needle in (texts[0], texts[-1]):
                want = sum(s.count(needle) for s in texts)
                got = len(hits(out, needle, page=n))
                if got != want:
                    raise BuildRefused(f"{doc_id}: template page {n}'s "
                                       f"{'first' if needle == texts[0] else 'last'} line "
                                       f"{needle!r} is on output page {n} {got} time(s), "
                                       f"written {want} time(s) for it")
        values = tuple(ValueTruth(b.field, f.values[b.field], locate_in(out, f.values[b.field]))
                       for b in m.blanks)
        vbox = {v.field: v.box for v in values}
        boxes: dict[str, tuple[Box, ...]] = {}
        for p in m.parts:
            if p.parent is None:
                for b in p.box:
                    if (b.x0, b.top, b.x1, b.bottom) != (0.0, 0.0, *tsize[b.page]):
                        raise BuildRefused(f"top-level part {p.id} is not the whole page {b.page}")
                boxes[p.id] = tuple(Box(b.page, 0.0, 0.0, *osize[b.page]) for b in p.box)
            else:
                got = []
                for b in p.box:
                    if (p.id, b.page) not in lay.table_lines:
                        raise BuildRefused(f"part {p.id} ({p.type}) has no layout on page {b.page}")
                    first, last = lay.table_lines[(p.id, b.page)]
                    got.append(_union(locate_in(out, first, page=b.page),
                                      locate_in(out, last, page=b.page)))
                boxes[p.id] = tuple(got)
    parts = tuple(PartTruth(p.id, p.type, (vbox[p.id.removeprefix("blank.")],)
                            if p.type == "blank" else boxes[p.id], p.parent)
                  for p in map_parts(m))
    truth = Truth(doc_id=doc_id, flavour=FLAVOUR, templates=(t.sha256,), fills=(f.id,), seed=f.seed,
                  review=m.review, parts=parts, values=values, transform=None)
    return pdf_bytes, truth
