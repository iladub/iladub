"""Lines of a PDF, as the router reads them (document-router plan, Task 3).

PROCEDURAL — raw extraction (CLAUDE.md § 8): PDF bytes -> typed line records -> RDF facts. Irreducible
to AXIOM because there is no evidence graph until this step makes one; irreducible to NEURAL because
nothing here is a reading judgement: a line is exactly what pdfium's own text stream delimits.

No grouping tolerance. Lines are split where pdfium's text emits a `\\r` or `\\n` char, never by
comparing char positions (so `etkl/geometry.text_lines`, whose `0.6 x median` is a tuned constant, is
deliberately not reused). MEASURED 2026-11-03 on pypdfium2 5.11.0: the generated `\\r\\n` between two
lines are counted by `count_chars()` and carry a zero-area box; pinned by
`tests/test_route_lines.py::test_pdfium_line_breaks_are_counted_chars_with_zero_area_boxes`.
Measured limit of the same rule: pdfium generates no break between two consecutive ONE-char lines,
so they read as one line (`test_two_one_char_lines_get_no_pdfium_break`).

A line's box is the union of its non-whitespace char boxes, turned top-down (distance from the page
top); a run of chars with no non-whitespace char is not a line. The graph stores each line's text
only as its sha256 (`route:textSha`), never the text.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

ROUTE = Namespace("https://w3id.org/iladub/route#")

_BREAKS = frozenset("\r\n")


@dataclass(frozen=True)
class Line:
    page: int            # counted from 1
    index: int           # position within its page, counted from 0
    text: str
    top: float           # distance from the page top, points
    bottom: float
    x0: float
    x1: float

    @property
    def sha(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _page_lines(page, page_no: int) -> list[Line]:
    height = page.get_height()
    textpage = page.get_textpage()
    out: list[Line] = []
    run: list[tuple[str, tuple[float, float, float, float]]] = []

    def close() -> None:
        inked = [box for ch, box in run if not ch.isspace()]
        if inked:
            text = "".join(ch for ch, _ in run).strip()
            out.append(Line(
                page=page_no, index=len(out), text=text,
                top=height - max(b[3] for b in inked), bottom=height - min(b[1] for b in inked),
                x0=min(b[0] for b in inked), x1=max(b[2] for b in inked),
            ))
        run.clear()

    for i in range(textpage.count_chars()):
        ch = textpage.get_text_range(i, 1)
        if ch in _BREAKS:
            close()
        else:
            run.append((ch, textpage.get_charbox(i)))   # (left, bottom, right, top), bottom-up
    close()
    return out


def extract_lines(pdf: bytes) -> list[Line]:
    """Every line of the PDF in reading order: page by page, then in pdfium's text order."""
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf)
    try:
        return [ln for n in range(len(doc)) for ln in _page_lines(doc[n], n + 1)]
    finally:
        doc.close()


def line_iri(pdf_sha: str, line: Line) -> URIRef:
    return URIRef(f"urn:iladub:route:{pdf_sha[:12]}:p{line.page}:l{line.index}")


def _decimal(x: float) -> Literal:
    """The float's shortest repr as an xsd:decimal lexical form (no exponent, no rounding)."""
    return Literal(format(Decimal(repr(x)), "f"), datatype=XSD.decimal)


def lines_graph(lines: list[Line], pdf_sha: str) -> Graph:
    """The lines as `route:Line` facts. Text is stored only as its hash."""
    g = Graph()
    g.bind("route", ROUTE)
    for ln in lines:
        node = line_iri(pdf_sha, ln)
        g.add((node, RDF.type, ROUTE.Line))
        g.add((node, ROUTE.onPage, Literal(ln.page, datatype=XSD.integer)))
        g.add((node, ROUTE.lineIndex, Literal(ln.index, datatype=XSD.integer)))
        g.add((node, ROUTE.top, _decimal(ln.top)))
        g.add((node, ROUTE.bottom, _decimal(ln.bottom)))
        g.add((node, ROUTE.textSha, Literal(ln.sha)))
    return g
