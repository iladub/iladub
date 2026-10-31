"""Find where a string the generator wrote landed in an exported PDF (spec 2026-10-31 § 4.3, § 4.5).

`locate(pdf, needle)` searches the PDF's text layer (pdfplumber, literal, case-sensitive, one line
at a time — a needle split across two output lines is NOT found) and returns the one hit's box.
Zero hits raise `NotFound`, more than one raise `Ambiguous`: the build refuses rather than guess.
`page=` narrows the search to one output page; the same 0 / > 1 rule applies there.

Justified PROCEDURAL (CLAUDE.md § 8): decidable exact string matching of strings the generator
itself wrote, over raw extraction of the text layer. No tolerance, no similarity, no choice among
hits. It answers no span/read/group question about a document it did not make. No reader may call
it (A3).
"""
from __future__ import annotations

from pathlib import Path

from scripts.synthetic_contracts.maps import Box


class NotFound(Exception):
    def __init__(self, needle: str, page: int | None = None):
        where = f" on page {page}" if page else ""
        super().__init__(f"not found{where}: {needle!r}")
        self.needle, self.page = needle, page


class Ambiguous(Exception):
    def __init__(self, needle: str, n: int, page: int | None = None):
        where = f" on page {page}" if page else ""
        super().__init__(f"{n} hits{where}: {needle!r}")
        self.needle, self.n, self.page = needle, n, page


def hits(pdf, needle: str, page: int | None = None) -> list[Box]:
    """Every literal hit of `needle`, on an open pdfplumber document."""
    out = []
    pages = [pdf.pages[page - 1]] if page else pdf.pages
    for p in pages:
        for h in p.search(needle, regex=False, case=True, return_chars=False):
            out.append(Box(p.page_number, h["x0"], h["top"], h["x1"], h["bottom"]))
    return out


def locate_in(pdf, needle: str, page: int | None = None) -> Box:
    """`locate` on an already open pdfplumber document."""
    if not needle.strip():
        raise ValueError("refusing to locate an empty needle")
    found = hits(pdf, needle, page)
    if not found:
        raise NotFound(needle, page)
    if len(found) > 1:
        raise Ambiguous(needle, len(found), page)
    return found[0]


def locate(pdf: Path, needle: str, page: int | None = None) -> Box:
    import pdfplumber
    with pdfplumber.open(Path(pdf)) as doc:
        return locate_in(doc, needle, page)
