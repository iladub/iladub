"""reshape — recover a reshape recipe from a compiled table and replay-verify it (Loop A1 core).

Recovery reuses Loop 8a's procedural search (recover_dimensions / detect_aggregations) —
the legitimately-algorithmic part — but its output is a declarative Recipe that the
round-trip oracle must certify before any NormalizedBase projection is emitted.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from . import denormalization as dn
from . import interpret
from .oracle import OracleVerdict, round_trip
from .recipe import UnpivotOp, StripAggregationOp, Recipe, col_leaf_label, row_label, grid_values

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")

_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


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
        members = [row_label(g, t, m, agg_col_labels) for m in ev.base_rows]
        ops.append(StripAggregationOp("row", ev.funcs[r], tuple(m for m in members if m),
                                      row_label(g, t, r, agg_col_labels)))
    return Recipe(tuple(ops))


def derive_base(g, t, recipe):
    """The derived flat base as a native-RDF hproj:Projection graph: run the inverse
    reshape CONSTRUCT (vocab/queries/unpivot-inverse.rq) over the source grid + the
    materialized recipe. Returns a graph of tab:BaseFact nodes (measure + coordinates).
    Replaces the retired Python recover_base/emit_base_facts twin. AXIOM (SPARQL);
    the only Python is interpret engine-glue + recipe materialization."""
    recipe_graph = Graph()
    _materialize_recipe(recipe_graph, t, recipe)
    return interpret.run(os.path.join(_QUERIES, "unpivot-inverse.rq"), g, recipe_graph)


def certify(g, t):
    """Recover recipe + derive the base (native-RDF projection) and run the round-trip
    oracle. Returns (recipe, verdict, base_graph). A table with no pivoted base to invert
    (empty base graph) is NOT a reproduction failure: it is out of A1's base-emitting
    scope, so it returns a clean ok verdict — nothing is emitted downstream (emit guards on
    an empty base)."""
    recipe = recover_recipe(g, t)
    base = derive_base(g, t, recipe)
    if len(list(base.subjects(RDF.type, TAB.BaseFact))) == 0:
        return recipe, OracleVerdict(True, ()), base
    verdict = round_trip(grid_values(g, t, _agg_col_labels(recipe)), base, recipe)
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
            g.add((ou, TAB.opTargetLabel, Literal(op.target_label)))
            for m in op.member_labels:
                g.add((ou, TAB.opMember, Literal(m)))
    return ru


def emit_base_projection(g, t, recipe, base):
    """Emit the derived NormalizedBase projection from a validated (recipe, base graph):
    merge the derived base facts into g and wrap them with the NormalizedBase node.
    `base` is the projection graph from derive_base. Shared by A1 (emit_normalized_base)
    and A2 (certify_with_proposals)."""
    ru = _materialize_recipe(g, t, recipe)
    nb = URIRef("%s-normbase" % t)
    g.add((nb, RDF.type, TAB.NormalizedBase))
    g.add((nb, TAB.derivedByRecipe, ru))
    g.add((nb, PROV.wasDerivedFrom, t))
    for triple in base:
        g.add(triple)
    for bf in base.subjects(RDF.type, TAB.BaseFact):
        g.add((nb, TAB.hasBaseFact, bf))
    return nb


def emit_normalized_base(g, t):
    """A1: if the deterministic recipe round-trips, emit the derived projection; else None."""
    recipe, verdict, base = certify(g, t)
    if not verdict.ok or len(list(base.subjects(RDF.type, TAB.BaseFact))) == 0:
        return None
    return emit_base_projection(g, t, recipe, base)


@dataclass(frozen=True)
class ProposalOutcome:
    normalized_base: object     # URIRef | None
    promotions: tuple           # PromotionDecision uris (Task 3); () until then
    oracle_ok: bool
    residue: tuple


def _nameless_col_pivots(g, t):
    return [d for d in dn.recover_dimensions(g, t)
            if d.axis == "column" and d.name is None and len(d.values) > 1]


def _named_pivot_recipe_and_base(g, t, dim, name):
    """Build (recipe, base_graph) for a nameless column pivot given a proposed name. Measure
    columns are identified by VALUE-SET membership (leaf label in dim.values), expressed in the
    inverse CONSTRUCT via tab:opValue. The name enters ONLY the recipe and the base coordinates.

    Returns (recipe, empty graph) when the pivot is ragged (any measure cell missing): a ragged
    pivot cannot be cleanly inverted, and the empty projection signals non-invertibility to
    certify_with_proposals so the oracle can flag it."""
    valset = set(dim.values)
    measure_cols = [c for c in g.objects(t, TAB.hasLeafColumn) if col_leaf_label(g, c) in valset]
    stub = _first_stub_name(g, t, valset)
    recipe = Recipe((UnpivotOp(dimension=name, stub=stub, axis="column"),))
    # Rectangularity: every (row x measure_col) cell must be present, else non-invertible.
    all_rows = list(g.objects(t, TAB.hasLeafRow))
    for r in all_rows:
        for c in measure_cols:
            if dn._entry(g, t, r, c) is None:
                return recipe, Graph()                       # ragged -> empty projection
    # materialize the recipe + the value set, then run the value-set inverse CONSTRUCT
    recipe_graph = Graph()
    ru = _materialize_recipe(recipe_graph, t, recipe)
    op = next(recipe_graph.objects(ru, TAB.hasOperation))
    for v in dim.values:
        recipe_graph.add((op, TAB.opValue, Literal(v)))
    base = interpret.run(os.path.join(_QUERIES, "unpivot-inverse-valueset.rq"), g, recipe_graph)
    return recipe, base


def certify_with_proposals(g, t, proposer):
    """A2 augmenting pass: for a nameless column pivot, ask the proposer for the dimension
    name, build the named recipe+base (value-set detection), and run A1's round-trip oracle.
    On success emit the derived projection (+ promotion in Task 3); else escalate."""
    pivots = _nameless_col_pivots(g, t)
    if not pivots:
        return ProposalOutcome(None, (), True, ())     # nothing nameless → A1 owns it; proposer untouched
    dim = pivots[0]
    context = {"stub": _first_stub_name(g, t, set(dim.values)), "title": None}
    proposal = proposer.propose_dimension_name(list(dim.values), context)
    if proposal is None:
        return ProposalOutcome(None, (), True, ())     # declined → escalate, nothing asserted
    recipe, base = _named_pivot_recipe_and_base(g, t, dim, proposal.name)
    empty = len(list(base.subjects(RDF.type, TAB.BaseFact))) == 0
    # Run the oracle even on an empty projection: a ragged pivot yields an empty base, so the
    # round-trip reproduces nothing against a non-empty grid and reports it as non-invertible
    # (ok=False). This is the docstring's "so the oracle can flag it"; the `empty` guard below
    # is a belt-and-braces escalation for the degenerate empty-grid case.
    verdict = round_trip(grid_values(g, t), base, recipe)
    if not verdict.ok or empty:
        return ProposalOutcome(None, (), verdict.ok, verdict.residue)   # not invertible -> escalate
    nb = emit_base_projection(g, t, recipe, base)
    from .promote import emit_promotion
    pd = emit_promotion(g, t, nb, proposal.name, list(dim.values), proposal)
    return ProposalOutcome(nb, (pd,), True, ())


def _first_stub_name(g, t, valset):
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0 and col_leaf_label(g, c) not in valset:
            return col_leaf_label(g, c)
    return None
