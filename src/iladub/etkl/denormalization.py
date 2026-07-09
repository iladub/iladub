"""denormalization — read a compiled holon's header hierarchies as a pivot schema.

A dimension pivoted into a header axis is recovered here (recover_dimensions): a header
level whose single node spans all its leaves NAMES the dimension of the level below; a
level with multiple sibling nodes holds the VALUES of a dimension. No re-inference of the
tree — it is read as-is. (Aggregation evidence and 3NF emission are later slices.)
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from rdflib import RDF, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


def _num(s):
    try:
        v = float(re.sub(r"[,%$]", "", s.strip()))
        return v if math.isfinite(v) else None
    except (ValueError, AttributeError):
        return None


def _label(g, node):
    lc = g.value(node, TAB.hasLabel)
    return str(g.value(lc, TAB.cellText)) if lc is not None else None


def _leaf_cols(g, t):
    return sorted(g.objects(t, TAB.hasLeafColumn), key=str)


def _leaf_rows(g, t):
    return sorted(g.objects(t, TAB.hasLeafRow), key=str)


@dataclass(frozen=True)
class PivotedDimension:
    axis: str                 # "row" | "column"
    level: int
    name: str | None
    values: tuple[str, ...]   # distinct value labels at this level, in leaf order


def _axis_dimensions(g, t, axis, covers_pred, leaves):
    """Read one axis's header tree into PivotedDimensions (see module docstring rule)."""
    n = len(leaves)
    if n == 0:
        return []
    nodes = [h for h in g.objects(t, TAB.hasHeaderNode)
             if any(True for _ in g.objects(h, covers_pred))]
    if not nodes:
        return []
    by_level = {}
    for h in nodes:
        lvl = int(g.value(h, TAB.headerLevel))
        cov = frozenset(g.objects(h, covers_pred))
        by_level.setdefault(lvl, []).append((h, _label(g, h), cov))
    dims, pending_name = [], None
    for lvl in sorted(by_level):
        level_nodes = by_level[lvl]
        if len(level_nodes) == 1 and len(level_nodes[0][2]) == n:
            pending_name = level_nodes[0][1]          # a spanning parent names the level below
            continue
        ordered = sorted(level_nodes, key=lambda z: min(str(c) for c in z[2]))
        seen, values = set(), []
        for _, lbl, _cov in ordered:
            if lbl is not None and lbl not in seen:
                seen.add(lbl); values.append(lbl)
        dims.append(PivotedDimension(axis, lvl, pending_name, tuple(values)))
        pending_name = None
    return dims


def recover_dimensions(g, t):
    """Recover pivoted dimensions from BOTH header axes (column via coversColumn, row via
    coversRow). A flat single-level axis yields one value-level dimension."""
    return (_axis_dimensions(g, t, "column", TAB.coversColumn, _leaf_cols(g, t))
            + _axis_dimensions(g, t, "row", TAB.coversRow, _leaf_rows(g, t)))
