"""reshape — recover a reshape recipe from a compiled table and replay-verify it (Loop A1 core).

Recovery reuses Loop 8a's procedural search (recover_dimensions / detect_aggregations) —
the legitimately-algorithmic part — but its output is a declarative Recipe that the
round-trip oracle must certify before any NormalizedBase projection is emitted.
"""
from __future__ import annotations

from rdflib import RDF, BNode, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from . import denormalization as dn
from .oracle import OracleVerdict, round_trip
from .recipe import UnpivotOp, StripAggregationOp, Recipe, col_leaf_label

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _leaf_label_level0(g, leaf, covers_pred):
    for h in g.subjects(covers_pred, leaf):
        if int(g.value(h, TAB.headerLevel)) == 0:
            lc = g.value(h, TAB.hasLabel)
            return str(g.value(lc, TAB.cellText)) if lc is not None else None
    return None


def _stub_col_names(g, t, exclude=()):
    """Level-0 label of each stub column (a column whose max covering level is 0), skipping
    any column in `exclude` (e.g. aggregation columns — a level-0 Total must never be picked
    as the row-key stub, which would otherwise depend on column insertion order)."""
    names = []
    for c in g.objects(t, TAB.hasLeafColumn):
        if c in exclude:
            continue
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0:
            lbl = _leaf_label_level0(g, c, TAB.coversColumn)
            if lbl is not None:
                names.append(lbl)
    return names


def _agg_col_labels(recipe):
    """Leaf labels of the recipe's column-aggregation targets (e.g. {'Total'}). A column
    with one of these labels is an aggregate, never a row-key stub."""
    return {op.target_label for op in recipe.operations
            if isinstance(op, StripAggregationOp) and op.axis == "column"}


def _row_key(g, t, r, exclude_labels=()):
    """Order-independent row identity: the text of row r's entry in the FIRST level-0
    single-leaf stub column whose leaf label is NOT an aggregation target — so a Total
    column (also level-0) never becomes the row key regardless of column insertion order.
    Falls back to the row URI tail. (reshape's agg-column-safe replacement for
    recipe.row_label, which keys on the first level-0 column unconditionally.)"""
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if not (levels and max(levels) == 0):
            continue
        if col_leaf_label(g, c) in exclude_labels:
            continue
        e = dn._entry(g, t, r, c)
        if e is not None:
            return str(g.value(e, TAB.cellText))
    return str(r).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def _grid_target(g, t, exclude_labels=()):
    """Reproduction target {(row_key, col_leaf_label): text} for the oracle — mirrors
    recipe.grid_values but keys rows via the agg-column-safe _row_key so the target and the
    recovered base agree on row identity even when a Total column precedes the stub."""
    out = {}
    for e in g.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow); c = g.value(e, TAB.atColumn)
        if r is None or c is None:
            continue
        col_lbl = col_leaf_label(g, c)
        if col_lbl is None:
            continue  # M2: bare/spanning-only column has no leaf label; skip
        out[(_row_key(g, t, r, exclude_labels), col_lbl)] = str(g.value(e, TAB.cellText))
    return out


def recover_recipe(g, t):
    dims = dn.recover_dimensions(g, t)
    ev = dn.detect_aggregations(g, t)
    ops = []
    stubs = _stub_col_names(g, t, exclude=ev.agg_cols)
    stub = stubs[0] if stubs else None
    # non-measure columns (numeric stubs / totals) are never aggregation operands — the
    # same exclusion detect_aggregations applies, so the strip's member set matches the
    # operands the total was actually detected from (else replay folds a numeric stub echo
    # into the recomputed total, and the round-trip fails).
    excl = ev.excluded_operand_cols
    for d in dims:
        if d.axis == "column" and d.name and len(d.values) > 1:
            ops.append(UnpivotOp(dimension=d.name, stub=stub, axis="column"))
    # strip ops: aggregation columns, then rows
    agg_col_labels = {col_leaf_label(g, c) for c in ev.agg_cols}   # e.g. {"Total"}
    for c in ev.agg_cols:
        members = [col_leaf_label(g, m) for m in ev.base_cols if m not in excl]
        ops.append(StripAggregationOp("column", ev.funcs[c],
                                      tuple(m for m in members if m), col_leaf_label(g, c)))
    for r in ev.agg_rows:
        members = [_row_key(g, t, m, agg_col_labels) for m in ev.base_rows]
        ops.append(StripAggregationOp("row", ev.funcs[r], tuple(m for m in members if m),
                                      _row_key(g, t, r, agg_col_labels)))
    return Recipe(tuple(ops))


def recover_base(g, t, recipe):
    """The flat base rows in oracle-ready dict form: one per (base data row x pivoted
    measure column). Keys = each unpivot dimension + stub; plus '__measure__'."""
    dims = dn.recover_dimensions(g, t)
    ev = dn.detect_aggregations(g, t)
    col_pivots = [d for d in dims if d.axis == "column" and d.name and len(d.values) > 1]
    pivot_names = {d.name for d in col_pivots}
    stubs = _stub_col_names(g, t, exclude=ev.agg_cols)
    stub = stubs[0] if stubs else None
    measure_cols = [c for c in g.objects(t, TAB.hasLeafColumn)
                    if _leaf_label_level0(g, c, TAB.coversColumn) in pivot_names
                    and c not in ev.agg_cols]
    base_rows = [r for r in g.objects(t, TAB.hasLeafRow) if r not in ev.agg_rows]
    agg_col_labels = {col_leaf_label(g, c) for c in ev.agg_cols}
    out = []
    for r in base_rows:
        rlab = _row_key(g, t, r, agg_col_labels)
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
    """Recover recipe + base and run the round-trip oracle. Returns (recipe, verdict, base).
    A table with no pivoted base to invert (base == []) is NOT a reproduction failure: it is
    simply out of A1's base-emitting scope, so it returns a clean ok verdict with empty residue
    (nothing is emitted downstream, because emit_normalized_base also guards on empty base)."""
    recipe = recover_recipe(g, t)
    base = recover_base(g, t, recipe)
    if not base:
        return recipe, OracleVerdict(True, ()), base
    verdict = round_trip(_grid_target(g, t, _agg_col_labels(recipe)), base, recipe)
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
