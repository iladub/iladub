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

from rdflib import BNode, RDF, Literal, Namespace, URIRef
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
            if len(target) < 2:          # need >=2 numeric evidence cells: a single
                continue                 # cell can match count()=len(others) by chance
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
            if len(target) < 2:          # need >=2 numeric evidence cells (see row loop)
                continue
            fn = verify_group(target, grp)
            if fn:
                agg_cols.append(C); funcs[C] = fn; operands[C] = tuple(others)
                base_cols.remove(C); changed = True; break
    return AggregationEvidence(tuple(agg_rows), tuple(agg_cols), tuple(base_rows),
                               tuple(base_cols), funcs, operands)


def _find_entry(g, t, r, c):
    for e in g.subjects(TAB.atRow, r):
        if (t, TAB.hasCell, e) in g and g.value(e, TAB.atColumn) == c:
            return e
    return None


def annotate_aggregations(g, t, ev):
    """Write aggregation evidence: type the aggregation leaf rows/cols, and mark each of
    their entry cells with overAxis + aggregationFunction + aggregates (operands)."""
    for a in ev.agg_rows:
        g.add((a, RDF.type, TAB.AggregationRow))
    for a in ev.agg_cols:
        g.add((a, RDF.type, TAB.AggregationColumn))
    ax_of = {a: "row" for a in ev.agg_rows}
    ax_of.update({a: "column" for a in ev.agg_cols})
    for e in list(g.subjects(RDF.type, TAB.EntryCell)):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow)
        c = g.value(e, TAB.atColumn)
        axes = [ax for key, ax in ax_of.items() if key in (r, c)]
        if not axes:
            continue
        g.add((e, RDF.type, TAB.AggregationCell))
        for ax in axes:
            src = r if ax == "row" else c
            g.add((e, TAB.overAxis, Literal(ax)))
            g.add((e, TAB.aggregationFunction, Literal(ev.funcs[src])))
            for m in ev.operands[src]:
                op = _find_entry(g, t, (m if ax == "row" else r), (c if ax == "row" else m))
                if op is not None:
                    g.add((e, TAB.aggregates, op))


def _col_label_at_level(g, c, level):
    """The label of the header node at `level` that covers leaf column `c` (or None)."""
    for h in g.subjects(TAB.coversColumn, c):
        if int(g.value(h, TAB.headerLevel)) == level:
            lc = g.value(h, TAB.hasLabel)
            return str(g.value(lc, TAB.cellText)) if lc is not None else None
    return None


def _entry(g, t, row, col):
    for e in g.subjects(TAB.atRow, row):
        if (t, TAB.hasCell, e) in g and g.value(e, TAB.atColumn) == col:
            return e
    return None


def _add_coordinate(g, bf, name, value):
    if name is None or value is None:
        return
    co = BNode()
    g.add((bf, TAB.atDimensionValue, co))
    g.add((co, TAB.dimensionName, Literal(name)))
    g.add((co, TAB.value, Literal(value)))


def emit_base_facts(g, t):
    """Invert the report to 3NF base facts: unpivot the pivoted column dimension(s) and
    strip the aggregations. Returns the tab:BaseFact uris. Empty if there is no pivoted
    column dimension to unwind."""
    dims = recover_dimensions(g, t)
    ev = detect_aggregations(g, t)
    col_pivots = [d for d in dims if d.axis == "column" and d.name and len(d.values) > 1]
    if not col_pivots:
        return []
    pivot_names = {d.name for d in col_pivots}
    leaf_cols = list(g.objects(t, TAB.hasLeafColumn))
    measure_cols = [c for c in leaf_cols
                    if _col_label_at_level(g, c, 0) in pivot_names and c not in ev.agg_cols]
    stub_cols = [c for c in leaf_cols if c not in measure_cols and c not in ev.agg_cols]
    base_rows = [r for r in g.objects(t, TAB.hasLeafRow) if r not in ev.agg_rows]
    facts = []
    for row in base_rows:
        for col in measure_cols:
            e = _entry(g, t, row, col)
            if e is None:
                continue
            v = _num(str(g.value(e, TAB.cellText)))
            if v is None:
                continue
            bf = URIRef("%s-fact-%s-%s" % (t, str(row).rsplit('-', 1)[-1], str(col).rsplit('-', 1)[-1]))
            g.add((bf, RDF.type, TAB.BaseFact))
            g.add((bf, TAB.measureValue, Literal(round(v, 6), datatype=XSD.decimal)))
            for d in col_pivots:                    # column coordinate: this column's value on each pivot dim
                _add_coordinate(g, bf, d.name, _col_label_at_level(g, col, d.level))
            for sc in stub_cols:                    # row coordinate: each stub's header name + this row's entry
                se = _entry(g, t, row, sc)
                if se is not None:
                    _add_coordinate(g, bf, _col_label_at_level(g, sc, 0), str(g.value(se, TAB.cellText)))
            facts.append(bf)
    return facts
