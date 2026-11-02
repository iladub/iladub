"""A minimal WordprocessingML (.docx) writer: stdlib `zipfile` + XML text (spec 2026-10-31 § 4.3).

Three block kinds — `Heading`, `Paragraph` (runs with font, size, bold, italic; exact line spacing;
an optional page break before it) and `Table` (cells of one or more lines, fixed column widths in
points) — on one page size with fixed margins. No python-docx: it is not installed and is not added.
The writer is byte-deterministic (fixed zip timestamps, fixed member order).

Justified PROCEDURAL (CLAUDE.md § 8): document generation — serialising blocks the generator built
into the OOXML container. No decision, no reading; the page geometry defaults are generation
parameters, not tolerances. No reader may call it (A3).
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class Run:
    text: str
    font: str | None = None
    size: float | None = None  # points; written as half-points
    bold: bool = False
    italic: bool = False


@dataclass(frozen=True)
class Paragraph:
    runs: tuple[Run, ...]
    page_break_before: bool = False
    line_pt: float | None = None  # exact line pitch in points; None = Word's single spacing


@dataclass(frozen=True)
class Heading:
    text: str
    level: int = 1


@dataclass(frozen=True)
class Table:
    cells: tuple[tuple[tuple[str, ...], ...], ...]  # rows -> cells -> lines
    col_widths: tuple[float, ...]                   # points
    font: str | None = None
    size: float | None = None


Block = Heading | Paragraph | Table


@dataclass(frozen=True)
class Page:
    width: float = 595.32
    height: float = 841.92
    margin: float = 28.0


def _tw(pt: float) -> int:
    return int(round(pt * 20))


def _rpr(font, size, bold, italic) -> str:
    out = []
    if font:
        f = escape(font, {'"': "&quot;"})
        out.append(f'<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:cs="{f}" w:eastAsia="{f}"/>')
    if bold:
        out.append("<w:b/>")
    if italic:
        out.append("<w:i/>")
    if size:
        hp = int(round(size * 2))
        out.append(f'<w:sz w:val="{hp}"/><w:szCs w:val="{hp}"/>')
    return f"<w:rPr>{''.join(out)}</w:rPr>" if out else ""


def _run(text: str, rpr: str) -> str:
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def _spacing(line_pt) -> str:
    line = f' w:line="{_tw(line_pt)}" w:lineRule="exact"' if line_pt else ""
    return f'<w:spacing w:before="0" w:after="0"{line}/>'


def _paragraph(p: Paragraph) -> str:
    brk = '<w:r><w:br w:type="page"/></w:r>' if p.page_break_before else ""
    runs = "".join(_run(r.text, _rpr(r.font, r.size, r.bold, r.italic)) for r in p.runs)
    return f"<w:p><w:pPr>{_spacing(p.line_pt)}</w:pPr>{brk}{runs}</w:p>"


def _heading(h: Heading) -> str:
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading{h.level}"/>{_spacing(None)}</w:pPr>'
            f"{_run(h.text, '')}</w:p>")


def _table(t: Table) -> str:
    border = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                     for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{_tw(w)}"/>' for w in t.col_widths)
    rpr = _rpr(t.font, t.size, False, False)
    rows = []
    for row in t.cells:
        tcs = []
        for w, lines in zip(t.col_widths, row, strict=True):
            paras = "".join(f"<w:p><w:pPr>{_spacing(None)}</w:pPr>{_run(s, rpr)}</w:p>"
                            for s in lines) or f"<w:p><w:pPr>{_spacing(None)}</w:pPr></w:p>"
            tcs.append(f'<w:tc><w:tcPr><w:tcW w:w="{_tw(w)}" w:type="dxa"/></w:tcPr>{paras}</w:tc>')
        rows.append(f"<w:tr>{''.join(tcs)}</w:tr>")
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{_tw(sum(t.col_widths))}" w:type="dxa"/>'
            f'<w:tblLayout w:type="fixed"/><w:tblBorders>{border}</w:tblBorders>'
            '<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
            f"</w:tblCellMar></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{''.join(rows)}</w:tbl>")


def document_xml(blocks: list[Block], page: Page = Page()) -> str:
    body = []
    for b in blocks:
        if isinstance(b, Paragraph):
            body.append(_paragraph(b))
        elif isinstance(b, Heading):
            body.append(_heading(b))
        elif isinstance(b, Table):
            body.append(_table(b))
            body.append(f"<w:p><w:pPr>{_spacing(1.0)}</w:pPr></w:p>")  # Word needs a p after a tbl
        else:
            raise TypeError(f"not a block: {b!r}")
    m = _tw(page.margin)
    sect = (f'<w:sectPr><w:pgSz w:w="{_tw(page.width)}" w:h="{_tw(page.height)}"/>'
            f'<w:pgMar w:top="{m}" w:right="{m}" w:bottom="{m}" w:left="{m}" w:header="0" '
            'w:footer="0" w:gutter="0"/></w:sectPr>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document {_NS}>'
            f"<w:body>{''.join(body)}{sect}</w:body></w:document>")


_STYLES = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:styles {_NS}>'
           '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" '
           'w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="20"/></w:rPr>'
           '</w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" '
           'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
           '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
           "</w:style>"
           + "".join(f'<w:style w:type="paragraph" w:styleId="Heading{n}"><w:name w:val="heading {n}"/>'
                     f'<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
                     f'<w:pPr><w:outlineLvl w:val="{n - 1}"/></w:pPr><w:rPr><w:b/>'
                     f'<w:sz w:val="{30 - 4 * n}"/></w:rPr></w:style>' for n in (1, 2, 3))
           + "</w:styles>")

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.styles+xml"/></Types>')

_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
         'relationships/officeDocument" Target="word/document.xml"/></Relationships>')

_DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
             'relationships/styles" Target="styles.xml"/></Relationships>')


def write_docx(blocks: list[Block], path: Path, page: Page = Page()) -> None:
    members = (("[Content_Types].xml", _CONTENT_TYPES), ("_rels/.rels", _RELS),
               ("word/_rels/document.xml.rels", _DOC_RELS), ("word/styles.xml", _STYLES),
               ("word/document.xml", document_xml(blocks, page)))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            z.writestr(zipfile.ZipInfo(name, _ZIP_TIME), data.encode("utf-8"),
                       compress_type=zipfile.ZIP_DEFLATED)
