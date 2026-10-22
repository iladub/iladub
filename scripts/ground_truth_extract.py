"""Extract the truth cells of one publisher-marked-up HTML table into a CSV.

Used for the ground-truth slice one (spec 2026-10-22, sections 3.1, 9.1, 10.1):

    python scripts/ground_truth_extract.py <html> <out-dir>

writes `<out-dir>/table-1.csv` (UTF-8, header row). `provenance.json` is written by hand.

Gate classification (CLAUDE.md section 8): PROCEDURAL, raw extraction (source -> typed facts).
It reads only the publisher's own markup: `id`, `header`, `<br>` and `vertical-align:super`. It
reads no geometry, no `text-indent`, and carries no tolerance or tuned constant. Irreducible to
AXIOM because the input is HTML bytes, not yet an RDF evidence graph (this is the step that
makes the facts); irreducible to NEURAL because nothing is underdetermined: the publisher
states which header ids a cell sits under. The only check is an exact SHA-256 of the table's
byte span, which refuses a table that is not the one the oracle was measured on.
"""
from __future__ import annotations

import csv
import hashlib
import pathlib
import re
import sys
from html.parser import HTMLParser

from iladub.truth import TableSpanMismatch, TruthMarkupError, TruthRow, normalise

SEP = " › "
_HEADER_ID = re.compile(r"^t\d+h\d+c\d+$")


class _Cell:
    def __init__(self, attrs: dict):
        self.id = attrs.get("id") or ""
        self.header = (attrs.get("header") or "").split()
        self.plain: list[str] = []
        self.sup: list[str] = []
        self.marked: list[str] = []


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[_Cell]] = []
        self._cell: _Cell | None = None
        self._spans: list[bool] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.rows.append([])
        elif tag == "td":
            self._cell = _Cell(a)
            self._spans = []
            self.rows[-1].append(self._cell)
        elif tag == "span" and self._cell is not None:
            style = (a.get("style") or "").replace(" ", "")
            self._spans.append("vertical-align:super" in style)
        elif tag == "br" and self._cell is not None:
            self._cell.plain.append(" ")
            self._cell.marked.append(" ")

    def handle_endtag(self, tag):
        if tag == "td":
            self._cell = None
        elif tag == "span" and self._spans:
            self._spans.pop()

    def handle_data(self, data):
        c = self._cell
        if c is None:
            return
        if any(self._spans):
            c.sup.append(data)
            c.marked.append(data)
        else:
            c.plain.append(data)
            c.marked.append(data)


def _span(html: bytes, ordinal: int) -> bytes:
    i = -1
    for _ in range(ordinal):
        i = html.find(b"<table", i + 1)
        if i < 0:
            raise TableSpanMismatch(f"no table number {ordinal}")
    j = html.find(b"</table>", i)
    if j < 0:
        raise TableSpanMismatch("unterminated table")
    return html[i : j + len(b"</table>")]


def extract_table(html: bytes, ordinal: int, expected_sha256: str) -> list[TruthRow]:
    """Truth cells of the `ordinal`-th `<table` (1-based) in `html`, pinned by span hash."""
    span = _span(html, ordinal)
    if hashlib.sha256(span).hexdigest() != expected_sha256:
        raise TableSpanMismatch(
            f"table {ordinal}: span sha256 {hashlib.sha256(span).hexdigest()} != {expected_sha256}"
        )
    p = _TableParser()
    p.feed(span.decode("utf-8"))
    headers: dict[str, str] = {}
    body: list[list[_Cell]] = []
    for row in p.rows:
        for c in row:
            if _HEADER_ID.match(c.id):
                headers[c.id] = normalise("".join(c.plain))
        if row and not all(_HEADER_ID.match(c.id) for c in row):
            body.append(row)
    for t in headers.values():
        if SEP in t:
            raise TruthMarkupError(f"header text contains {SEP!r}: {t!r}")
    out: list[TruthRow] = []
    seen: dict[str, int] = {}
    for row in body:
        label_cell, cells = row[0], row[1:]
        label = normalise("".join(label_cell.plain))
        marked = normalise("".join(label_cell.marked))
        occ = seen.get(label, 0) if label else 0
        if label:
            seen[label] = occ + 1
        for c in cells:
            hids = [h for h in c.header if _HEADER_ID.match(h)]
            for h in hids:
                if h not in headers:
                    raise TruthMarkupError(f"cell {c.id} names unknown header {h}")
            value = normalise("".join(c.marked))
            if not value:
                continue
            out.append(TruthRow(label, marked, occ, SEP.join(headers[h] for h in hids), value))
    return out


def main(argv: list[str]) -> int:
    html_path, out_dir = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    rows = extract_table(html_path.read_bytes(), 2,
                         "964e62c8ed5f3742b24df41f846950b3bcde45e97bbff92664cb84cda89a00fa")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "table-1.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row_label", "row_label_marked", "row_occurrence", "col_path", "value"])
        for r in rows:
            w.writerow([r.row_label, r.row_label_marked, r.row_occurrence, r.col_path, r.value])
    print(f"{len(rows)} rows -> {out_dir / 'table-1.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
