"""denormalization — read a compiled holon's header hierarchies as a pivot schema.

A dimension pivoted into a header axis is recovered here (recover_dimensions): a header
level whose single node spans all its leaves NAMES the dimension of the level below; a
level with multiple sibling nodes holds the VALUES of a dimension. No re-inference of the
tree — it is read as-is. (Aggregation evidence and 3NF emission are later slices.)
"""
from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass

from rdflib import BNode, RDF, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from . import interpret

TAB = Namespace("https://w3id.org/iladub/tab#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def _num(s):
    try:
        v = float(re.sub(r"[,%$]", "", s.strip()))
        return v if math.isfinite(v) else None
    except (ValueError, AttributeError):
        return None


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


def _read_dimensions(dimgraph, g, t):
    """PROCEDURAL reconstruction glue: map the derived tab:PivotedDimension RDF into the
    PivotedDimension dataclasses. Value ORDER (presentation, not a role decision) is
    re-derived by the same key as the retired _axis_dimensions — the minimum covered leaf
    (by IRI) per label — so the dataclass is reproduced exactly."""
    dims = []
    for dn in dimgraph.subjects(RDF.type, TAB.PivotedDimension):
        # scope to t: recover-dimensions.rq keys each dim IRI as STR(?T)+"-dim-"+axis+"-"+L,
        # so the full table IRI precedes the literal "-dim-" separator — two distinct table
        # IRIs necessarily differ before "-dim-", making this prefix filter collision-safe.
        if not str(dn).startswith(str(t) + "-dim-"):
            continue
        axis = str(dimgraph.value(dn, TAB.onAxis))
        level = int(dimgraph.value(dn, TAB.atLevel))
        name = dimgraph.value(dn, TAB.dimensionName)
        name = str(name) if name is not None else None
        labels = {str(v) for v in dimgraph.objects(dn, TAB.hasDimensionValue)}
        cp = TAB.coversColumn if axis == "column" else TAB.coversRow

        def _minleaf(lbl, cp=cp, level=level):
            best = None
            for h in g.subjects(TAB.headerLevel, Literal(level)):
                if (t, TAB.hasHeaderNode, h) not in g:
                    continue
                lc = g.value(h, TAB.hasLabel)
                if lc is None or str(g.value(lc, TAB.cellText)) != lbl:
                    continue
                m = min((str(c) for c in g.objects(h, cp)), default=None)
                if m is not None and (best is None or m < best):
                    best = m
            return best or lbl

        values = tuple(sorted(labels, key=_minleaf))
        dims.append(PivotedDimension(axis, level, name, values))
    # column dims first (level order), then row dims (level order) — matches recover_dimensions
    return ([d for d in sorted(dims, key=lambda z: z.level) if d.axis == "column"]
            + [d for d in sorted(dims, key=lambda z: z.level) if d.axis == "row"])


def recover_dimensions(g, t):
    """Recover pivoted dimensions from BOTH header axes via the declarative two-pass
    derivation (name-levels -> recover-dimensions, AXIOM), read back into PivotedDimension
    dataclasses. Replaces the set-algebra _axis_dimensions body; signature unchanged."""
    marks = interpret.run(os.path.join(_QUERIES, "name-levels.rq"), g)
    dimgraph = interpret.run(os.path.join(_QUERIES, "recover-dimensions.rq"), g, marks)
    return _read_dimensions(dimgraph, g, t)


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
    excluded_operand_cols: frozenset = frozenset()   # non-measure cols barred as operands


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


def _operand_exclusions(g, t):
    """Columns barred as aggregation OPERANDS (level-0 single-leaf stubs/totals in a pivoted
    table), derived by operand-exclusions.rq. Signature/return unchanged. The CONSTRUCT is
    NOT table-scoped (it marks columns across the whole graph), so intersect with `t`'s own
    leaf columns to preserve the original per-t contract when a graph holds multiple tables."""
    marks = interpret.run(os.path.join(_QUERIES, "operand-exclusions.rq"), g)
    barred = set(marks.subjects(TAB.barredAsOperand, Literal(True)))
    return barred & set(g.objects(t, TAB.hasLeafColumn))


def detect_aggregations(g, t):
    """Iterated strip: a leaf row/col is an aggregation iff a function reproduces it from
    a group of >=2 OTHER base rows/cols across every column/row. Grand total = the row x
    col intersection (both axes). Only exact-arithmetic, >=2-operand groups are flagged."""
    rows, cols, V = _value_matrix(g, t)
    base_rows = list(rows)
    base_cols = list(cols)
    excl = _operand_exclusions(g, t)
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
            others = [c for c in base_cols if c != C and c not in excl]
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
                               tuple(base_cols), funcs, operands,
                               excluded_operand_cols=frozenset(excl))


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
    """Invert the report to 3NF base facts via the declarative inverse CONSTRUCT: recover the
    recipe, derive the base projection, merge it into g, and return the tab:BaseFact uris.
    Empty if there is no pivoted column dimension to unwind. (Re-backed onto reshape.derive_base
    — the single SPARQL path; the old nested-g.add loop is retired.)"""
    from . import reshape
    recipe = reshape.recover_recipe(g, t)
    base = reshape.derive_base(g, t, recipe)
    facts = list(base.subjects(RDF.type, TAB.BaseFact))
    for triple in base:
        g.add(triple)
    return facts


@dataclass(frozen=True)
class DenormalizationReport:
    dimensions: tuple
    evidence: object
    base_facts: tuple
    recipe: object            # reshape.Recipe
    oracle_ok: bool
    residue: tuple
    normalized_base: object   # URIRef | None


def analyze(report):
    """Public entry point: recover dimensions + aggregations, annotate the graph in place
    (Loop 8a evidence), then certify the reshape recipe with the round-trip oracle and emit
    the derived NormalizedBase projection. A recipe that does not round-trip escalates as
    residue (oracle_ok=False, normalized_base=None) — nothing is asserted."""
    from . import reshape
    g = report.graph
    out = []
    for t in (list(g.subjects(RDF.type, TAB.RecordTable))
              + list(g.subjects(RDF.type, TAB.HierarchicalTable))):
        dims = recover_dimensions(g, t)
        ev = detect_aggregations(g, t)
        annotate_dimensions(g, t, dims)
        annotate_aggregations(g, t, ev)
        recipe, verdict, _base = reshape.certify(g, t)
        nb = reshape.emit_normalized_base(g, t) if verdict.ok else None
        facts = list(g.objects(nb, TAB.hasBaseFact)) if nb is not None else []
        out.append(DenormalizationReport(tuple(dims), ev, tuple(facts), recipe,
                                         verdict.ok, verdict.residue, nb))
    return out[0] if len(out) == 1 else out
