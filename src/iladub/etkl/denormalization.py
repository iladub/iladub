"""denormalization — read a compiled holon's header hierarchies as a pivot schema.

A dimension pivoted into a header axis is recovered here (recover_dimensions): a header
level whose single node spans all its leaves NAMES the dimension of the level below; a
level with multiple sibling nodes holds the VALUES of a dimension. No re-inference of the
tree — it is read as-is. (Aggregation evidence and 3NF emission are later slices.)
"""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import RDF, Literal, Namespace, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")


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
        multi = [ln for ln in level_nodes if len(ln[2]) > 1]
        singles_cov = set().union(*[ln[2] for ln in level_nodes if len(ln[2]) == 1]) if any(len(ln[2]) == 1 for ln in level_nodes) else set()
        leafset = set(leaves)
        if len(multi) == 1 and (multi[0][2] | singles_cov) >= leafset and not (multi[0][2] & singles_cov):
            pending_name = multi[0][1]           # a spanning parent (modulo single-leaf stubs) names the level below
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


def annotate_dimensions(g, t, dims):
    """Write PivotedDimension evidence into the graph; return the dimension node uris."""
    out = []
    for d in dims:
        du = URIRef("%s-dim-%s-%d" % (t, d.axis, d.level))
        g.add((du, RDF.type, TAB.PivotedDimension))
        g.add((du, TAB.onAxis, Literal(d.axis)))
        g.add((du, TAB.atLevel, Literal(d.level, datatype=XSD.integer)))
        if d.name:
            g.add((du, TAB.dimensionName, Literal(d.name)))
        for v in d.values:
            g.add((du, TAB.hasDimensionValue, Literal(v)))
        out.append(du)
    return out
