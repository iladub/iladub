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

from rdflib import RDF, Literal, Namespace, URIRef
from rdflib.namespace import XSD

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


_TOL = 1e-6


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


# verifier registry — slice ③/8b append ratio/sequence verifiers without touching the core.
_EXACT_FUNCS = {
    "sum": sum,
    "mean": lambda xs: sum(xs) / len(xs),
    "min": min,
    "max": max,
    "count": lambda xs: float(len(xs)),
    "product": lambda xs: math.prod(xs),
}


def verify_group(target, group_per_col):
    """Return the function name reproducing `target` (per column) from the per-column
    operand lists `group_per_col`, or None. Every column with a non-empty operand list
    must satisfy target == f(operands)."""
    pairs = [(t, xs) for t, xs in zip(target, group_per_col) if xs]
    if not pairs:
        return None
    for name, f in _EXACT_FUNCS.items():
        if all(_close(f(xs), t) for t, xs in pairs):
            return name
    return None


@dataclass(frozen=True)
class AggregationEvidence:
    agg_rows: tuple
    agg_cols: tuple
    base_rows: tuple
    base_cols: tuple
    funcs: dict          # axis_uri -> function name
    operands: dict       # axis_uri -> tuple of member axis_uris


def _value_matrix(g, t):
    rows = _leaf_rows(g, t)
    cols = _leaf_cols(g, t)
    V = {}
    for e in g.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow)
        c = g.value(e, TAB.atColumn)
        v = _num(str(g.value(e, TAB.cellText)))
        if r is not None and c is not None and v is not None:
            V[(r, c)] = v
    return rows, cols, V


def detect_aggregations(g, t):
    """Iterated strip: a leaf row/col is an aggregation iff a function reproduces it from
    a group of >=2 OTHER base rows/cols across every column/row. Grand total = the row x
    col intersection (both axes). Only exact-arithmetic, >=2-operand groups are flagged."""
    rows, cols, V = _value_matrix(g, t)
    base_rows = list(rows)
    base_cols = list(cols)
    funcs, operands, agg_rows, agg_cols = {}, {}, [], []
    changed = True
    while changed:
        changed = False
        for R in list(base_rows):
            others = [r for r in base_rows if r != R]
            if len(others) < 2:
                continue
            target_all = [V.get((R, c)) for c in cols]
            grp_all = [[V[(o, c)] for o in others if (o, c) in V] for c in cols]
            # restrict to columns where the target has a numeric value
            # (text stub cells are simply absent from V — skip them, not the whole row)
            target = [tv for tv in target_all if tv is not None]
            grp = [xs for tv, xs in zip(target_all, grp_all) if tv is not None]
            fn = verify_group(target, grp)
            if fn:
                agg_rows.append(R); funcs[R] = fn; operands[R] = tuple(others)
                base_rows.remove(R); changed = True; break
        if changed:
            continue
        for C in list(base_cols):
            others = [c for c in base_cols if c != C]
            if len(others) < 2:
                continue
            target_all = [V.get((r, C)) for r in rows]
            grp_all = [[V[(r, o)] for o in others if (r, o) in V] for r in rows]
            # restrict to rows where the target has a numeric value
            target = [tv for tv in target_all if tv is not None]
            grp = [xs for tv, xs in zip(target_all, grp_all) if tv is not None]
            fn = verify_group(target, grp)
            if fn:
                agg_cols.append(C); funcs[C] = fn; operands[C] = tuple(others)
                base_cols.remove(C); changed = True; break
    return AggregationEvidence(tuple(agg_rows), tuple(agg_cols), tuple(base_rows),
                               tuple(base_cols), funcs, operands)
