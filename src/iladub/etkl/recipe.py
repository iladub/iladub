"""recipe — the reshape recipe model + grid extraction (Loop A1 core).

A Recipe is an ordered list of inverse report-authoring operations that, replayed
FORWARD over a flat base, regenerate the original grid. grid_values() is the
reproduction target the round-trip oracle compares against.
"""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import RDF, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


@dataclass(frozen=True)
class UnpivotOp:
    dimension: str            # e.g. "Region" — the pivoted dimension's name
    stub: str                 # e.g. "Year" — the stub key that indexes rows
    axis: str = "column"


@dataclass(frozen=True)
class StripAggregationOp:
    axis: str                 # "row" | "column"
    function: str             # "sum" | "mean" | "min" | "max" | "count" | "product"
    member_labels: tuple      # the base members the aggregate is computed from
    target_label: str         # the aggregate row/col's own leaf label (e.g. "Total")


@dataclass(frozen=True)
class Recipe:
    operations: tuple         # forward order: unpivot(s) then strip(s)


def _text(g, cell):
    return str(g.value(cell, TAB.cellText)) if cell is not None else None


def col_leaf_label(g, c):
    """Deepest header label covering exactly leaf column c (the single-covering node).

    A column may legitimately have more than one single-covering header (e.g. a
    level-0 spanning header that happens to span only one column *and* its level-1
    leaf child).  Among all single-covering headers, we return the label of the one
    with the highest ``tab:headerLevel`` value — the deepest node in the header tree.
    Iteration order is therefore irrelevant; the result is deterministic.
    """
    best_label = None
    best_level = -1
    for h in g.subjects(TAB.coversColumn, c):
        if len(list(g.objects(h, TAB.coversColumn))) == 1:
            level = int(g.value(h, TAB.headerLevel))
            if level > best_level:
                best_level = level
                best_label = _text(g, g.value(h, TAB.hasLabel))
    return best_label


def _stub_cols(g, t):
    """Columns whose leaf label is not a pivoted measure — used to key rows.
    A stub column is one that covers a single leaf and sits at header level 0
    (no deeper leaf under a spanning parent). Heuristic-free: any column whose
    only covering header is level 0 is a stub."""
    stubs = []
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0:
            stubs.append(c)
    return stubs


def row_label(g, t, r, exclude_labels=()):
    """A row's identity: the text of its entry in the first stub column whose leaf label is
    NOT in `exclude_labels`, else the URI tail. Excluding aggregation-target labels (e.g.
    "Total") keeps a level-0 Total column from being picked as the row key — which would
    otherwise depend on column insertion order."""
    for sc in _stub_cols(g, t):
        if col_leaf_label(g, sc) in exclude_labels:
            continue
        for e in g.subjects(TAB.atRow, r):
            if (t, TAB.hasCell, e) in g and g.value(e, TAB.atColumn) == sc:
                return _text(g, e)
    return str(r).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def grid_values(g, t, exclude_labels=()):
    """{(row_label, col_leaf_label): cell_text} for every entry cell of table t. `exclude_labels`
    is forwarded to row_label so aggregation columns are never used as the row key."""
    out = {}
    for e in g.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow); c = g.value(e, TAB.atColumn)
        if r is None or c is None:
            continue
        col_lbl = col_leaf_label(g, c)
        if col_lbl is None:
            continue  # M2: bare/spanning-only column has no leaf label; skip to avoid None-key merges
        out[(row_label(g, t, r, exclude_labels), col_lbl)] = _text(g, e)
    return out
