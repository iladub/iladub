"""Draw a layer over a template PDF without touching its content (spec 2026-10-31 § 4.3). Apache-2.0.

`overlay` draws one reportlab page per template page (same size), then builds a new document in
which every page is the template page and the overlay page, each placed as a Form XObject
(pypdfium2 `page_as_xobject` -> `as_pageobject` -> `insert_obj`, then `gen_content`). The template's
text is carried as-is, at the same coordinates; nothing is retyped. No pypdf: it is not installed
and is not added.

Justified PROCEDURAL (CLAUDE.md § 8): PDF assembly — document generation, no decision, no
tolerance. It never reads the template's text. No reader may call it (A3).
"""
from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pypdfium2 as pdfium
from reportlab.pdfgen.canvas import Canvas


def overlay(template_pdf: Path, draw: Callable[[Canvas, int], None]) -> pdfium.PdfDocument:
    """`draw(canvas, page_no)` is called once per template page, 1-based, on a canvas the page's size
    (reportlab's bottom-left origin)."""
    src = pdfium.PdfDocument(str(template_pdf))
    sizes = [src[i].get_size() for i in range(len(src))]
    buf = BytesIO()
    c = Canvas(buf, pagesize=sizes[0], invariant=1)
    for n, (w, h) in enumerate(sizes, 1):
        c.setPageSize((w, h))
        draw(c, n)
        c.showPage()
    c.save()
    layer = pdfium.PdfDocument(buf.getvalue())
    out = pdfium.PdfDocument.new()
    for i, (w, h) in enumerate(sizes):
        page = out.new_page(w, h)
        for doc in (src, layer):
            page.insert_obj(doc.page_as_xobject(i, out).as_pageobject())
        page.gen_content()
    out._keep = (src, layer, buf)  # the XObjects reference both sources; keep them alive
    return out


def to_bytes(doc: pdfium.PdfDocument) -> bytes:
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
