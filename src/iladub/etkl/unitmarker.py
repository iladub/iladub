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

from .celltype import _cell_datatype, _emit_datatype_declarations, is_blank

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
    celltype.grid_evidence, with _marker_datatype in place of _cell_datatype — including the
    SAME datatypeAbstains/inDatatypeFamily declarations (loop-quantity-typing task 2), since
    this graph is transient exactly like celltype.grid_evidence's and unit-marker-column.rq's
    neighbor check normalises through tab:inDatatypeFamily (?tn = tab:Quantity) rather than
    enumerating tab:Numeric/tab:Currency. Without these triples here too the normalisation
    would silently no-op for this query specifically, even though grid_evidence emits them —
    the two evidence-graph builders are separate by design (marker-local typing, see the
    module docstring), so each must carry its own copy."""
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
    _emit_datatype_declarations(g)
    return g


def derive_marker_columns(cells, ncols) -> tuple[tuple[int, str], ...]:
    """The derived (column_index, symbol) pairs, sorted by column. Empty when none."""
    g = marker_evidence(cells, ncols)
    with open(_RQ, encoding="utf-8") as f:
        q = f.read()
    return tuple(sorted((int(row[0]), str(row[1])) for row in g.query(q)))


def absorb_unit_markers(band):
    """Two-pass absorption (the loop-G candidates pattern): pass-1 grid -> AXIOM ->
    marker words filtered out, markers carried on Band.unit_markers -> downstream
    re-derives the grid on the remainder. Identity for ruled bands (the author drew
    those columns), narrow grids, and bands with no derived marker. PROCEDURAL
    engine glue; the decision is the query's."""
    from dataclasses import replace
    from .cells import recover_leaf_grid
    from .headers import _grid_cells

    if band.rules:
        return band
    grid = recover_leaf_grid(band)
    if grid.ncols < 2:
        return band
    cells = _grid_cells(band, grid)
    derived = derive_marker_columns(cells, grid.ncols)
    if not derived:
        return band

    b = grid.boundaries
    markers = []
    drop = set()
    for col, sym in derived:
        regions = []
        for ln in band.lines:
            for w in ln.words:
                cx = (w.x0 + w.x1) / 2.0
                if b[col] <= cx < b[col + 1] and w.text.strip() == sym:
                    drop.add(id(w))
                    regions.append((w.x0, w.top, w.x1, w.bottom))
        neighbor_x = (b[col + 1] + b[col + 2]) / 2.0
        markers.append((sym, neighbor_x, tuple(regions)))

    new_lines = []
    for ln in band.lines:
        kept = tuple(w for w in ln.words if id(w) not in drop)
        if kept:
            new_lines.append(replace(ln, words=kept))
    return replace(band, lines=tuple(new_lines), unit_markers=tuple(markers))
