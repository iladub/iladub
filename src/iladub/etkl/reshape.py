"""reshape — recover a reshape recipe from a compiled table and replay-verify it (Loop A1 core).

Recovery reuses Loop 8a's procedural search (recover_dimensions / detect_aggregations) —
the legitimately-algorithmic part — but its output is a declarative Recipe that the
round-trip oracle must certify before any NormalizedBase projection is emitted.
"""
from __future__ import annotations

from rdflib import RDF, BNode, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from . import denormalization as dn
from .oracle import round_trip
from .recipe import (UnpivotOp, StripAggregationOp, Recipe,
                     col_leaf_label, row_label, grid_values)

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _leaf_label_level0(g, leaf, covers_pred):
    for h in g.subjects(covers_pred, leaf):
        if int(g.value(h, TAB.headerLevel)) == 0:
            lc = g.value(h, TAB.hasLabel)
            return str(g.value(lc, TAB.cellText)) if lc is not None else None
    return None


def _stub_col_names(g, t):
    """Level-0 label of each stub column (a column whose max covering level is 0)."""
    names = []
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0:
            lbl = _leaf_label_level0(g, c, TAB.coversColumn)
            if lbl is not None:
                names.append(lbl)
    return names


def recover_recipe(g, t):
    dims = dn.recover_dimensions(g, t)
    ev = dn.detect_aggregations(g, t)
    ops = []
    stubs = _stub_col_names(g, t)
    stub = stubs[0] if stubs else None
    for d in dims:
        if d.axis == "column" and d.name and len(d.values) > 1:
            ops.append(UnpivotOp(dimension=d.name, stub=stub, axis="column"))
    # strip ops: aggregation columns, then rows
    for c in ev.agg_cols:
        members = [col_leaf_label(g, m) for m in ev.base_cols]
        ops.append(StripAggregationOp("column", ev.funcs[c],
                                      tuple(m for m in members if m), col_leaf_label(g, c)))
    for r in ev.agg_rows:
        members = [row_label(g, t, m) for m in ev.base_rows]
        ops.append(StripAggregationOp("row", ev.funcs[r],
                                      tuple(m for m in members if m), row_label(g, t, r)))
    return Recipe(tuple(ops))


def recover_base(g, t, recipe):
    """The flat base rows in oracle-ready dict form: one per (base data row x pivoted
    measure column). Keys = each unpivot dimension + stub; plus '__measure__'."""
    dims = dn.recover_dimensions(g, t)
    ev = dn.detect_aggregations(g, t)
    col_pivots = [d for d in dims if d.axis == "column" and d.name and len(d.values) > 1]
    pivot_names = {d.name for d in col_pivots}
    stubs = _stub_col_names(g, t)
    stub = stubs[0] if stubs else None
    measure_cols = [c for c in g.objects(t, TAB.hasLeafColumn)
                    if _leaf_label_level0(g, c, TAB.coversColumn) in pivot_names
                    and c not in ev.agg_cols]
    base_rows = [r for r in g.objects(t, TAB.hasLeafRow) if r not in ev.agg_rows]
    out = []
    for r in base_rows:
        rlab = row_label(g, t, r)
        for c in measure_cols:
            e = dn._entry(g, t, r, c)
            if e is None:
                continue
            v = dn._num(str(g.value(e, TAB.cellText)))
            if v is None:
                continue
            row = {"__measure__": v}
            if stub is not None:
                row[stub] = rlab
            for d in col_pivots:
                row[d.name] = col_leaf_label(g, c)
            out.append(row)
    return out


def certify(g, t):
    """Recover recipe + base and run the round-trip oracle. Returns (recipe, verdict, base)."""
    recipe = recover_recipe(g, t)
    base = recover_base(g, t, recipe)
    verdict = round_trip(grid_values(g, t), base, recipe)
    return recipe, verdict, base


def _materialize_recipe(g, t, recipe):
    ru = URIRef("%s-recipe" % t)
    g.add((ru, RDF.type, TAB.ReshapeRecipe))
    g.add((ru, TAB.recipeForTable, t))
    for i, op in enumerate(recipe.operations):
        ou = URIRef("%s-op-%d" % (t, i))
        g.add((ru, TAB.hasOperation, ou))
        g.add((ou, TAB.opIndex, Literal(i, datatype=XSD.integer)))
        if isinstance(op, UnpivotOp):
            g.add((ou, RDF.type, TAB.UnpivotOp))
            g.add((ou, TAB.opAxis, Literal(op.axis)))
            g.add((ou, TAB.opDimension, Literal(op.dimension)))
            if op.stub is not None:
                g.add((ou, TAB.opStub, Literal(op.stub)))
        else:  # StripAggregationOp
            g.add((ou, RDF.type, TAB.StripAggregationOp))
            g.add((ou, TAB.opAxis, Literal(op.axis)))
            g.add((ou, TAB.opFunction, Literal(op.function)))
    return ru


def emit_normalized_base(g, t):
    """If the recipe round-trips, emit the derived NormalizedBase projection + its base
    facts and return its uri; else assert nothing and return None."""
    recipe, verdict, base = certify(g, t)
    if not verdict.ok or not base:
        return None
    ru = _materialize_recipe(g, t, recipe)
    nb = URIRef("%s-normbase" % t)
    g.add((nb, RDF.type, TAB.NormalizedBase))
    g.add((nb, TAB.derivedByRecipe, ru))
    g.add((nb, PROV.wasDerivedFrom, t))
    for i, row in enumerate(base):
        bf = URIRef("%s-fact-%d" % (t, i))
        g.add((bf, RDF.type, TAB.BaseFact))
        g.add((nb, TAB.hasBaseFact, bf))
        g.add((bf, TAB.measureValue, Literal(round(row["__measure__"], 6), datatype=XSD.decimal)))
        for k, v in row.items():
            if k == "__measure__":
                continue
            co = BNode()
            g.add((bf, TAB.atDimensionValue, co))
            g.add((co, TAB.dimensionName, Literal(k)))
            g.add((co, TAB.value, Literal(v)))
    return nb
