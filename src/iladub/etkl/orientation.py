"""orientation — detect a TRANSPOSED table (records along columns, fields down the
first column) via type-orientation.

This is iladub's first SEMANTIC oracle: the 2-D round-trip (geometry) and the tab:
SHACL (structure) both pass on a transposed table, because it is a valid grid — only
the *orientation* of the record axis is wrong. Type-orientation catches it: in a
normal table each column is type-homogeneous (a structured, non-Text attribute runs
DOWN a column); in a transposed table a structured attribute runs ACROSS a row.
"""
from __future__ import annotations

import os


def _region_cells(region):
    return [(c.row, c.col, c.text) for c in region.cells]


def _ncols(region):
    return max((c.col for c in region.cells), default=-1) + 1


def looks_transposed(region) -> bool:
    """True iff the region's body has a type-homogeneous structured ROW but no
    type-homogeneous structured COLUMN — the transposition signature.

    A body row is "structured" when its value cells (columns >= 1) are homogeneous
    in a single non-Text type (Numeric, Date, or Currency). Conservative and keyed
    on structured (non-Text) typing: plain text is symmetric (both axes carry
    labels) and ignored, so an all-text table is never flagged, and a normal
    structured table (which has a typed column by definition) is never flagged.
    """
    from . import celltype
    g = celltype.grid_evidence(_region_cells(region), _ncols(region))
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "looks-transposed.rq")
    return celltype.run_ask(q, g)


def transpose_is_coherent(region) -> bool:
    """True iff EVERY physical row is type-exact-homogeneous across its value
    columns (columns >= 1) — the signature of a genuine transposition, where each
    row is a single-typed field. The second oracle of the compile gate:
    `looks_transposed` detects, `transpose_is_coherent` decides whether to compile.

    Type-exact: each value row's cells must share a single concrete type (Numeric,
    Date, or Currency) — a row mixing, say, a Date cell and a Currency cell is
    incoherent, not just "all structured vs. all not". A coincidentally-flagged
    upright record table has rows that mix a text label, a number and a unit, so at
    least one row is not homogeneous and this returns False — the region is then
    escalated (detect-and-escalate stays the floor), never compiled into an
    inverted table. Rows with no value column (only col 0) are vacuously coherent.
    """
    from . import celltype
    g = celltype.grid_evidence(_region_cells(region), _ncols(region))
    q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries", "transpose-coherent.rq")
    return celltype.run_ask(q, g)
