"""unitmarker — the accounting currency-marker column (spec 2026-08-05).

A borderless column whose every non-blank cell is the SAME currency symbol is a unit
marker on its numeric right neighbor, not a column of the table (US accounting style:
`$` at the column edge, value right-aligned beside it, drawn on first/total rows only).
The compiler read it as a 1-2-cell Text column, fabricating grid columns (apple p0:
ncols 9 for a 5-column statement) and failing tiling.

Gate classification (§8): the DECISION ("is column c a unit marker for c+1?") is the
unit-marker-column.rq AXIOM over a dedicated typed-cell evidence graph. This module is
PROCEDURAL only: raw glyph typing (is_currency_glyph — B2b's shipped [$€£¥] symbol
class, reused, no new constant), evidence emission, and (in absorb_unit_markers, task
2) word filtering + re-derivation. The shared celltype._cell_datatype is DELIBERATELY
not extended: a global tab:CurrencyGlyph would change homogeneity verdicts in every
existing query (a bare `$` inside a mixed column would stop being Text); marker-local
typing keeps every existing verdict byte-identical by construction.
"""
from __future__ import annotations

import os

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .celltype import _cell_datatype, is_blank

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")
_RQ = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                   "vocab", "queries", "unit-marker-column.rq")

_CURRENCY_SYMBOLS = frozenset("$€£¥")   # B2b's _CURRENCY symbol class, verbatim


def is_currency_glyph(s: str) -> bool:
    """The cell is exactly one currency symbol (B2b's shipped set). PROCEDURAL raw
    typing, like celltype.is_currency."""
    return s.strip() in _CURRENCY_SYMBOLS


def _marker_datatype(t: str):
    """Marker-local typing: CurrencyGlyph first, else the shared lattice."""
    if not is_blank(t) and is_currency_glyph(t):
        return TAB.CurrencyGlyph
    return _cell_datatype(t)


def marker_evidence(cells, ncols) -> Graph:
    """The dedicated typed-cell evidence graph for the marker AXIOM. Same shape as
    celltype.grid_evidence, with _marker_datatype in place of _cell_datatype."""
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["umcell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, _marker_datatype(t)))
    for c in range(ncols):
        g.add((_EV["umcol-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    return g


def derive_marker_columns(cells, ncols) -> tuple[tuple[int, str], ...]:
    """The derived (column_index, symbol) pairs, sorted by column. Empty when none."""
    g = marker_evidence(cells, ncols)
    with open(_RQ, encoding="utf-8") as f:
        q = f.read()
    return tuple(sorted((int(row[0]), str(row[1])) for row in g.query(q)))
