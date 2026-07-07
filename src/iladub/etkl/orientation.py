"""orientation — detect a TRANSPOSED table (records along columns, fields down the
first column) via type-orientation.

This is iladub's first SEMANTIC oracle: the 2-D round-trip (geometry) and the tab:
SHACL (structure) both pass on a transposed table, because it is a valid grid — only
the *orientation* of the record axis is wrong. Type-orientation catches it: in a
normal table each column is type-homogeneous (a numeric attribute runs DOWN a
column); in a transposed table a numeric attribute runs ACROSS a row.
"""
from __future__ import annotations

from .headers import is_numeric


def looks_transposed(region) -> bool:
    """True iff the region's body has a type-homogeneous numeric ROW but no
    type-homogeneous numeric COLUMN — the transposition signature.

    Conservative and keyed on numeric typing only: text is symmetric (both axes
    carry labels) and ignored, so an all-text table is never flagged, and a normal
    numeric table (which has a typed column by definition) is never flagged.
    """
    data = [c for c in region.cells if c.row > 0]        # body only; header is row 0
    rows: dict[int, dict[int, str]] = {}
    cols: dict[int, list[str]] = {}
    for c in data:
        rows.setdefault(c.row, {})[c.col] = c.text
        cols.setdefault(c.col, []).append(c.text)

    # a body row whose cells in columns >= 1 (excluding the first/label column) are all numeric
    typed_row = any(
        any(cc >= 1 for cc in rowmap) and all(is_numeric(rowmap[cc]) for cc in rowmap if cc >= 1)
        for rowmap in rows.values()
    )
    # a leaf column whose body cells are all numeric
    typed_col = any(vals and all(is_numeric(v) for v in vals) for vals in cols.values())

    return typed_row and not typed_col
