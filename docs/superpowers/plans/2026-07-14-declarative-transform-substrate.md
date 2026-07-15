# Declarative Transform Substrate (Neurosymbolic Loop One) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hand-coded Python interpreter of the reshape recipe (`oracle.replay` + `reshape.recover_base` + `denormalization.emit_base_facts`, three Python twins kept in lockstep by hand) with a single declarative SPARQL `CONSTRUCT` substrate: each recipe op-type gets fixed `.rq` files that read their parameters from the RDF recipe, in both directions, with the flat base carried as a derived `hproj:Projection` RDF graph.

**Architecture:** A thin `interpret.run(query_path, *graphs)` executor loads a version-controlled `.rq` from `vocab/queries/` and runs it via rdflib over (source grid graph + materialized recipe graph). The **inverse** CONSTRUCTs (`grid → base`) produce the derived projection; the **forward** CONSTRUCTs (`base → grid`) reconstruct the grid for the round-trip oracle, which exact-compares to the original `grid_values` in Python. The recipe becomes an actually-executable declarative artifact; the base becomes native RDF (decision B); the Python execution twins are retired.

**Tech Stack:** Python 3, rdflib (existing dependency — SPARQL 1.1 engine + `CONSTRUCT` + aggregates), pytest. No new runtime dependency.

## Global Constraints

Copied verbatim from CLAUDE.md §8 (the neurosymbolic-first gate — a hard Global Constraint) and the spec's §2/§8/§9. **Every task's requirements implicitly include this section. Reviewers enforce it.**

- **AXIOM (the transform):** the transform is **standard SPARQL `CONSTRUCT` + SPARQL 1.1 aggregates** only, consuming standards (SPARQL, F&O/FnO function IRIs, `hproj:Projection`). **No transform logic in Python. No tuned constant or numeric tolerance anywhere in the `.rq` files or in `interpret.py`.** A tuned constant/tolerance in the transform is a review failure.
- **PROCEDURAL (procedural code — Python in this reference implementation; only these three, each with a why-irreducible note in code):** (1) invoking rdflib's SPARQL engine on the query files (`interpret.run` — engine glue); (2) the exact-equality compare in the round-trip (`_close`, `_TOL = 1e-6` — decidable arithmetic, irreducible); (3) `recover_recipe`'s procedural *search* that emits the declarative recipe (its **output** is an axiom).
- **NEURAL:** none in loop one (the span-perception family is loop two).
- **SPARQL-ceiling rule (settled):** use **standard SPARQL only — do NOT extend SPARQL**. Where an op genuinely reaches the expressiveness limit of standard `CONSTRUCT`/aggregates, substituting Python *for that specific piece* is an acceptable, justified PROCEDURAL, shipped with a why-irreducible note. Prefer SPARQL; accept Python *at the ceiling*; never contort or extend SPARQL.
- **Scope: A only.** The CONSTRUCT interpreter for the *existing* op-types (`UnpivotOp`, `StripAggregationOp`), both directions, base as `hproj:Projection`, retiring the three Python twins. **Out of scope:** B (role/type/boundary axiom-lifts), C (redundant-tiling-backstop deletion), the NEURAL span-perception family (loop two).
- **Source ownership (non-negotiable):** the `.rq` files reference `tab:` (owned) + standard function IRIs only. `hproj:` appears only as an object in `tab-hga-align.ttl`; `fn:`/F&O IRIs only as objects in `tab-fno-align.ttl`. New `tab:` properties are added to the owned `tab.ttl` only. Never write an HGA/FnO term as a subject.
- **Behavioural spec = the shipped suites.** `tests/etkl/test_reshape_certify.py`, `test_certify_proposals.py`, `test_denormalization.py`, `test_denorm_integration.py`, `test_oracle.py`, `test_reshape_recover.py`, `test_promote*.py`, `test_recipe*.py`, `test_tab.py` must end green. Where the spec (§9) authorizes it, a **mechanism** test coupled to the retired `list[dict]` representation is *re-expressed* against the SPARQL mechanism — that is supersession, not loosening. A **behavioural** test (asserting `NormalizedBase`/`tab:BaseFact` coords/`oracle_ok`/promotion) that needs editing is a supersession *defect* to investigate, not a test to loosen.
- **Serialization/validation conventions:** RDF Turtle authoring; language-tagged literals allowed (never constrain label/rationale props to `xsd:string`).

---

## File Structure

**Create:**
- `vocab/queries/` — new directory: version-controlled `.rq` CONSTRUCT files, one per op-type-and-direction. First-class declarative artifacts.
  - `vocab/queries/unpivot-inverse.rq` — grid → base facts for a named column pivot (excludes aggregate rows/cols). [AXIOM]
  - `vocab/queries/unpivot-inverse-valueset.rq` — grid → base facts for a *nameless* column pivot, measure columns detected by value-set membership (A2.1). [AXIOM]
  - `vocab/queries/unpivot-forward.rq` — base facts → reconstructed grid cells (re-pivot + stub echo). [AXIOM]
  - `vocab/queries/strip-aggregation-forward-sum.rq` — re-add each `sum` aggregate row/col via a sub-`SELECT (SUM(?v) AS ?t) … GROUP BY …`. [AXIOM]
- `src/iladub/etkl/interpret.py` — thin executor: load a `.rq`, run it via rdflib over the union of the given graphs, return the constructed graph. [PROCEDURAL: engine glue]

**Modify:**
- `vocab/ontology/tab.ttl` — add owned recipe-serialization properties `tab:opTargetLabel`, `tab:opMember`, `tab:opValue` (needed so the `.rq` files can read strip/value-set params from RDF).
- `src/iladub/etkl/reshape.py` — `_materialize_recipe` serializes the new props; `recover_base` → **retired**, replaced by `derive_base(g, t, recipe) -> Graph` (inverse CONSTRUCT); `certify` returns the derived projection graph as `base`; `emit_base_projection` takes the projection graph and merges it; `_named_pivot_recipe_and_base` emits its base via the value-set inverse CONSTRUCT; `certify`/`certify_with_proposals`/`emit_normalized_base` public behaviour unchanged.
- `src/iladub/etkl/oracle.py` — `round_trip` runs the forward CONSTRUCTs via `interpret` (base is now the projection graph); `replay`/`_fmt`/`_FUNCS` → **deleted**; `_close`/`_isnum`/`_TOL` kept (PROCEDURAL compare).
- `src/iladub/etkl/denormalization.py` — `emit_base_facts` re-backed onto `derive_base` (single CONSTRUCT path; public export + its two tests stay green).
- `vocab/ontology/tab-hga-align.ttl` — confirm `tab:NormalizedBase rdfs:subClassOf hproj:Projection` carries the derived base (already present; verified in Task 6).
- `vocab/ontology/tab-fno-align.ttl` — confirm the strip functions map to their F&O IRIs (already present; the forward-sum query references `fn:sum` semantics; verified in Task 6).

**Test files touched:**
- Create: `tests/etkl/test_interpret.py` (new — executor + per-`.rq` unit tests), `tests/etkl/test_transform_gate.py` (new — the neurosymbolic gate test).
- Re-express (mechanism, authorized by spec §9): `tests/etkl/test_oracle.py`, `tests/etkl/test_reshape_recover.py`, and four assertions/monkeypatches coupled to `recover_base`/`list[dict]` in `test_reshape_certify.py` + `test_denorm_integration.py`.
- Stay green unchanged (behavioural): the rest of `test_reshape_certify.py`, all of `test_certify_proposals.py`, `test_denormalization.py`, `test_denorm_integration.py`'s happy path, `test_promote*.py`, `test_recipe*.py`, `test_tab.py`.

---

## Task 1: The `interpret` executor + the unpivot inverse CONSTRUCT (promote the prototype)

Builds the thin SPARQL executor and the first (prototype-validated) inverse query: a named column pivot grid → flat base facts, reading `tab:opDimension`/`tab:opStub` from the RDF recipe op. This is the spec §3 probe promoted to a test.

**Files:**
- Create: `src/iladub/etkl/interpret.py`
- Create: `vocab/queries/unpivot-inverse.rq`
- Test: `tests/etkl/test_interpret.py`

**Interfaces:**
- Produces: `interpret.run(query_path: str, *graphs: rdflib.Graph) -> rdflib.Graph` — loads the `.rq` at `query_path`, runs the `CONSTRUCT` over the union of `graphs`, returns the constructed graph. Later tasks call it for both directions.
- Produces: `vocab/queries/unpivot-inverse.rq` — a `CONSTRUCT` that, given a source grid graph + a recipe graph containing a `tab:UnpivotOp` with `tab:opDimension`/`tab:opStub`, emits `tab:BaseFact` nodes (measure + a dimension coordinate + a stub coordinate). Consumed by `reshape.derive_base` (Task 4).
- Consumes: nothing from earlier tasks.

- [ ] **Step 1: Write the failing test for the executor + the inverse query**

Create `tests/etkl/test_interpret.py`:

```python
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")
QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")


def _named_region_pivot():
    """Region(North/South) pivoted across level-1 leaves under a level-0 'Region' header;
    Year stub column; two data rows 2020/2021. 4 measure cells → 4 base facts."""
    g = Graph(); t = EX.tbl
    c_year, c_north, c_south = EX.cYear, EX.cNorth, EX.cSouth
    for c in (c_year, c_north, c_south):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        if lbl is not None:
            lc = URIRef(str(u) + "l")
            g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(lbl)))
            g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hYear, 0, "Year", [c_year])
    hdr(EX.hRegion, 0, "Region", [c_north, c_south])       # named level-0 spanning header
    hdr(EX.hNorth, 1, "North", [c_north])
    hdr(EX.hSouth, 1, "South", [c_south])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"2020": {c_year: "2020", c_north: "10", c_south: "20"},
            "2021": {c_year: "2021", c_north: "11", c_south: "21"}}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c in (c_year, c_north, c_south):
            e = EX["e_%s_%s" % (r, str(c)[-5:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c))
            g.add((e, TAB.cellText, Literal(vals[r][c])))
    return g, t


def _recipe_graph_unpivot(dimension, stub):
    rg = Graph()
    op = EX.op0
    rg.add((op, RDF.type, TAB.UnpivotOp))
    rg.add((op, TAB.opIndex, Literal(0)))
    rg.add((op, TAB.opAxis, Literal("column")))
    rg.add((op, TAB.opDimension, Literal(dimension)))
    rg.add((op, TAB.opStub, Literal(stub)))
    return rg


def test_run_executes_construct_over_union():
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    facts = list(out.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 4                                  # 2 rows x 2 measure cols


def test_unpivot_inverse_yields_correct_coordinates():
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    # collect (measure, {(dimName, value), ...}) per fact
    got = set()
    for f in out.subjects(RDF.type, TAB.BaseFact):
        m = float(out.value(f, TAB.measureValue))
        coords = frozenset((str(out.value(co, TAB.dimensionName)), str(out.value(co, TAB.value)))
                           for co in out.objects(f, TAB.atDimensionValue))
        got.add((m, coords))
    assert (10.0, frozenset({("Region", "North"), ("Year", "2020")})) in got
    assert (21.0, frozenset({("Region", "South"), ("Year", "2021")})) in got
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/etkl/test_interpret.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'iladub.etkl.interpret'` (and the query file does not exist yet).

- [ ] **Step 3: Implement the executor**

Create `src/iladub/etkl/interpret.py`:

```python
"""interpret — the declarative CONSTRUCT executor (neurosymbolic loop one).

Loads a version-controlled SPARQL CONSTRUCT (.rq) from vocab/queries/ and runs it
via rdflib over the union of the given graphs. This is the ONLY procedural piece of
the transform, and it is PROCEDURAL engine glue: it invokes a standard SPARQL engine
on a standard query. It contains NO transform logic and NO tuned constant — the
transform lives entirely in the .rq files (AXIOM). Irreducible because SPARQL must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph


def run(query_path, *graphs):
    """Execute the CONSTRUCT at `query_path` over the union of `graphs`; return the
    constructed rdflib.Graph."""
    union = Graph()
    for g in graphs:
        union += g
    query = Path(query_path).read_text(encoding="utf-8")
    result = union.query(query)
    out = Graph()
    for triple in result:
        out.add(triple)
    return out
```

- [ ] **Step 4: Implement the unpivot inverse CONSTRUCT**

Create `vocab/queries/unpivot-inverse.rq` (rdflib rejects inline `[ … ]` property-lists in a CONSTRUCT template, so coordinate IRIs are `BIND`-constructed — which also yields stable, dereferenceable coordinate IRIs):

```sparql
# unpivot-inverse.rq  (grid -> base) for a NAMED column pivot.
# Params read from the recipe op node: tab:opDimension (the pivoted dimension's name,
# carried by the level-0 spanning header) and tab:opStub (the row-key column's name).
# Measure columns are exactly the level-1 leaves under the level-0 header whose label
# equals ?dimName; an aggregate column (a different level-0 label, e.g. "Total") is
# therefore excluded automatically. Row-aggregate exclusion is added in Task 2.
PREFIX tab: <https://w3id.org/iladub/tab#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
CONSTRUCT {
  ?bf a tab:BaseFact ;
      tab:measureValue ?mv ;
      tab:atDimensionValue ?coDim , ?coStub .
  ?coDim  tab:dimensionName ?dimName ; tab:value ?colLabel .
  ?coStub tab:dimensionName ?stubName ; tab:value ?stubVal .
}
WHERE {
  ?op a tab:UnpivotOp ; tab:opDimension ?dimName ; tab:opStub ?stubName .

  # measure columns: level-1 leaf under the level-0 header labelled ?dimName
  ?h0 tab:headerLevel 0 ; tab:hasLabel ?h0l ; tab:coversColumn ?c .
  ?h0l tab:cellText ?dimName .
  ?h1 tab:headerLevel 1 ; tab:hasLabel ?h1l ; tab:coversColumn ?c .
  ?h1l tab:cellText ?colLabel .

  # the measure cell at (row ?r, measure col ?c)
  ?e a tab:EntryCell ; tab:atRow ?r ; tab:atColumn ?c ; tab:cellText ?v .
  BIND(xsd:decimal(?v) AS ?mv)

  # the stub column: the level-0 column labelled ?stubName, and this row's stub value
  ?hs tab:headerLevel 0 ; tab:hasLabel ?hsl ; tab:coversColumn ?sc .
  ?hsl tab:cellText ?stubName .
  ?se tab:atRow ?r ; tab:atColumn ?sc ; tab:cellText ?stubVal .

  BIND(IRI(CONCAT(STR(?e), "-bf")) AS ?bf)
  BIND(IRI(CONCAT(STR(?e), "-bf-dim")) AS ?coDim)
  BIND(IRI(CONCAT(STR(?e), "-bf-stub")) AS ?coStub)
}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/etkl/test_interpret.py -v`
Expected: PASS (both tests). If `xsd:decimal(?v)` rejects a value, the failure is a real query bug — fix the query, do not loosen the test.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/interpret.py vocab/queries/unpivot-inverse.rq tests/etkl/test_interpret.py
git commit -m "feat(etkl): CONSTRUCT executor + unpivot-inverse.rq (promote prototype) [A/loop-one task 1]

interpret.run — PROCEDURAL engine glue; the named-pivot inverse CONSTRUCT is AXIOM,
reading tab:opDimension/tab:opStub from the RDF recipe. No transform logic in Python.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Strip-aggregation inverse — aggregate-row exclusion + recipe serialization of strip params

The inverse must exclude aggregate **rows** from the base (aggregate columns are already excluded by the measure-column match in Task 1). Driving the exclusion off the recipe requires serializing each `StripAggregationOp`'s `target_label` and `member_labels` into RDF — which `_materialize_recipe` currently drops. This task adds the owned vocab, extends materialization, and adds the exclusion filter to `unpivot-inverse.rq`.

**Files:**
- Modify: `vocab/ontology/tab.ttl` (add `tab:opTargetLabel`, `tab:opMember`; `tab:opValue` is added here too for Task 5's use)
- Modify: `src/iladub/etkl/reshape.py:126-144` (`_materialize_recipe` — serialize strip params)
- Modify: `vocab/queries/unpivot-inverse.rq` (add the agg-row exclusion filter)
- Test: `tests/etkl/test_interpret.py` (add an agg-row exclusion case), `tests/etkl/test_recipe_vocab.py` (extend if it enumerates op props — verify)

**Interfaces:**
- Produces: three new owned datatype properties `tab:opTargetLabel`, `tab:opMember`, `tab:opValue` on `tab:ReshapeOperation` subtypes.
- Produces: `_materialize_recipe(g, t, recipe) -> URIRef` now emits, for each `StripAggregationOp`: `tab:opAxis`, `tab:opFunction`, `tab:opTargetLabel` (one), `tab:opMember` (repeated). Consumed by the forward strip query (Task 3) and the inverse exclusion filter (this task).

- [ ] **Step 1: Write the failing test — the inverse excludes an aggregate row**

Add to `tests/etkl/test_interpret.py`:

```python
def _recipe_graph_unpivot_with_row_strip(dimension, stub, target_label, members):
    rg = _recipe_graph_unpivot(dimension, stub)
    op = EX.op1
    rg.add((op, RDF.type, TAB.StripAggregationOp))
    rg.add((op, TAB.opIndex, Literal(1)))
    rg.add((op, TAB.opAxis, Literal("row")))
    rg.add((op, TAB.opFunction, Literal("sum")))
    rg.add((op, TAB.opTargetLabel, Literal(target_label)))
    for m in members:
        rg.add((op, TAB.opMember, Literal(m)))
    return rg


def test_unpivot_inverse_excludes_aggregate_row():
    """A 'Total' row (stub value 'Total') declared as a row StripAggregationOp target must
    NOT produce base facts — only the base rows 2020/2021 melt into facts."""
    import os
    from iladub.etkl import interpret
    g, t = _named_region_pivot()
    # add a Total row: stub 'Total', North=21, South=41
    tr = EX.rTotal
    g.add((tr, RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, tr))
    for c, txt in ((EX.cYear, "Total"), (EX.cNorth, "21"), (EX.cSouth, "41")):
        e = EX["e_total_%s" % str(c)[-5:]]
        g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
        g.add((e, TAB.atRow, tr)); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    rg = _recipe_graph_unpivot_with_row_strip("Region", "Year", "Total", ["2020", "2021"])
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse.rq"), g, rg)
    facts = list(out.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 4                                  # Total row excluded; 2020/2021 x North/South
    stubvals = {str(out.value(co, TAB.value))
                for f in facts for co in out.objects(f, TAB.atDimensionValue)
                if str(out.value(co, TAB.dimensionName)) == "Year"}
    assert stubvals == {"2020", "2021"}                     # no "Total" stub coordinate
```

- [ ] **Step 2: Write the failing test — materialization serializes strip params**

Add to `tests/etkl/test_reshape_recover.py` (a unit test, no PDF needed):

```python
def test_materialize_recipe_serializes_strip_params():
    from rdflib import Graph, URIRef, Literal
    from iladub.etkl.reshape import _materialize_recipe
    from iladub.etkl.recipe import Recipe, UnpivotOp, StripAggregationOp
    g = Graph(); t = URIRef("https://example.org/d#tbl")
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    ru = _materialize_recipe(g, t, recipe)
    # find the strip op node
    strip = None
    for op in g.objects(ru, TAB.hasOperation):
        if (op, __import__("rdflib").RDF.type, TAB.StripAggregationOp) in g:
            strip = op
    assert strip is not None
    assert str(g.value(strip, TAB.opTargetLabel)) == "Total"
    assert {str(m) for m in g.objects(strip, TAB.opMember)} == {"North", "South"}
    assert str(g.value(strip, TAB.opFunction)) == "sum"
```

- [ ] **Step 3: Run both tests to verify they fail**

Run: `python -m pytest tests/etkl/test_interpret.py::test_unpivot_inverse_excludes_aggregate_row tests/etkl/test_reshape_recover.py::test_materialize_recipe_serializes_strip_params -v`
Expected: FAIL — the exclusion test still returns 6 facts (Total row melted), and `opTargetLabel`/`opMember` are absent from the materialized recipe.

- [ ] **Step 4: Add the owned vocab to `tab.ttl`**

In `vocab/ontology/tab.ttl`, after the `tab:opFunction` declaration (around line 163), add:

```turtle
tab:opTargetLabel a owl:DatatypeProperty ; rdfs:domain tab:StripAggregationOp ; rdfs:range xsd:string ;
    rdfs:label "operation target label"@en ;
    rdfs:comment "The leaf label of the aggregate row/column this strip op removes and re-derives (e.g. \"Total\")."@en .
tab:opMember a owl:DatatypeProperty ; rdfs:domain tab:StripAggregationOp ; rdfs:range xsd:string ;
    rdfs:label "operation member"@en ;
    rdfs:comment "A base member label the aggregate is computed from (repeated once per member)."@en .
tab:opValue a owl:DatatypeProperty ; rdfs:domain tab:UnpivotOp ; rdfs:range xsd:string ;
    rdfs:label "operation value"@en ;
    rdfs:comment "A pivot value naming a measure column for a NAMELESS column pivot, where measure columns are detected by value-set membership rather than a level-0 dimension-name header (A2.1). Repeated once per value."@en .
```

- [ ] **Step 5: Extend `_materialize_recipe` to serialize the strip params**

In `src/iladub/etkl/reshape.py`, replace the `else:  # StripAggregationOp` branch of `_materialize_recipe` (lines 140-143) with:

```python
        else:  # StripAggregationOp
            g.add((ou, RDF.type, TAB.StripAggregationOp))
            g.add((ou, TAB.opAxis, Literal(op.axis)))
            g.add((ou, TAB.opFunction, Literal(op.function)))
            g.add((ou, TAB.opTargetLabel, Literal(op.target_label)))
            for m in op.member_labels:
                g.add((ou, TAB.opMember, Literal(m)))
```

- [ ] **Step 6: Add the aggregate-row exclusion filter to `unpivot-inverse.rq`**

In `vocab/queries/unpivot-inverse.rq`, immediately after the stub-value line (`?se tab:atRow ?r ; tab:atColumn ?sc ; tab:cellText ?stubVal .`), add a filter that drops any row whose stub value is a declared row-aggregate target:

```sparql
  # exclude aggregate rows: a row whose stub value is a row-strip op's target label
  FILTER NOT EXISTS {
    ?rowStrip a tab:StripAggregationOp ; tab:opAxis "row" ; tab:opTargetLabel ?stubVal .
  }
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python -m pytest tests/etkl/test_interpret.py tests/etkl/test_reshape_recover.py::test_materialize_recipe_serializes_strip_params -v`
Expected: PASS. Then confirm the vocab still parses and any vocab enumeration test passes:
Run: `python -m pytest tests/etkl/test_recipe_vocab.py tests/etkl/test_tab.py -v`
Expected: PASS (adding properties must not break these; if a test asserts a closed property set, that is a behavioural check to update deliberately — investigate before editing).

- [ ] **Step 8: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/queries/unpivot-inverse.rq src/iladub/etkl/reshape.py tests/etkl/test_interpret.py tests/etkl/test_reshape_recover.py
git commit -m "feat(etkl): strip-aggregation inverse — agg-row exclusion + recipe serialization of strip params [A/loop-one task 2]

Adds owned tab:opTargetLabel/opMember/opValue; _materialize_recipe now carries strip
target+members into RDF; unpivot-inverse.rq excludes declared aggregate rows.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: The forward CONSTRUCT pair + oracle rewire (retire `replay`/`_fmt`)

Builds the two forward queries (`base → grid`) and rewires `oracle.round_trip` to reconstruct the grid via SPARQL and exact-compare, deleting the Python interpreter (`replay`/`_fmt`/`_FUNCS`). `test_oracle.py` is re-expressed against the native-RDF base + SPARQL mechanism (spec §9 authorization).

**Files:**
- Create: `vocab/queries/unpivot-forward.rq`, `vocab/queries/strip-aggregation-forward-sum.rq`
- Modify: `src/iladub/etkl/oracle.py` (rewrite `round_trip`; delete `replay`, `_fmt`, `_FUNCS`)
- Test: `tests/etkl/test_oracle.py` (re-expressed), `tests/etkl/test_interpret.py` (forward unit tests)

**Interfaces:**
- Produces: `vocab/queries/unpivot-forward.rq` — base facts → reconstructed grid cells. Each cell is emitted as `?cell tab:reproRow ?rl ; tab:reproCol ?cl ; tab:reproText ?txt` (a reconstruction-only shape read back by Python glue, never merged into the source graph).
- Produces: `vocab/queries/strip-aggregation-forward-sum.rq` — re-adds each `sum` aggregate row/col as repro cells via a grouped sub-`SELECT`.
- Produces: `oracle.round_trip(original: dict, base: rdflib.Graph, recipe: Recipe) -> OracleVerdict` — **same signature**; `base` is now the derived projection graph (decision B); `recipe` is the `Recipe` dataclass (materialized internally). Consumed by `reshape.certify`/`certify_with_proposals` (Tasks 4-5).
- Consumes: `interpret.run` (Task 1); `_materialize_recipe` (Task 2, imported from `reshape`).

Reproduction shape (owned, reconstruction-only — declared inline in the queries via `tab:reproRow`/`tab:reproCol`/`tab:reproText`; add them to `tab.ttl` alongside the op props if a vocab test requires every used term to be declared — otherwise they are query-local reconstruction predicates and need no ontology entry). **Decision:** declare them in `tab.ttl` for cleanliness (see Step 4).

- [ ] **Step 1: Write the failing forward unit tests**

Add to `tests/etkl/test_interpret.py`:

```python
def _projection_graph_region():
    """The 4-fact derived base for the Region×Year pivot, as native RDF (what unpivot-inverse
    produces). Measures: (2020,North)=10 (2020,South)=20 (2021,North)=11 (2021,South)=21."""
    p = Graph()
    facts = [("10", "North", "2020"), ("20", "South", "2020"),
             ("11", "North", "2021"), ("21", "South", "2021")]
    for i, (mv, region, year) in enumerate(facts):
        bf = EX["bf%d" % i]
        p.add((bf, RDF.type, TAB.BaseFact))
        p.add((bf, TAB.measureValue, Literal(mv, datatype=__import__("rdflib").namespace.XSD.decimal)))
        cd = EX["bf%d-dim" % i]; cs = EX["bf%d-stub" % i]
        p.add((bf, TAB.atDimensionValue, cd)); p.add((cd, TAB.dimensionName, Literal("Region"))); p.add((cd, TAB.value, Literal(region)))
        p.add((bf, TAB.atDimensionValue, cs)); p.add((cs, TAB.dimensionName, Literal("Year"))); p.add((cs, TAB.value, Literal(year)))
    return p


def _repro_dict(out):
    d = {}
    for cell in out.subjects(RDF.type, TAB.ReproCell):
        d[(str(out.value(cell, TAB.reproRow)), str(out.value(cell, TAB.reproCol)))] = str(out.value(cell, TAB.reproText))
    return d


def test_unpivot_forward_reconstructs_measure_and_stub_cells():
    import os
    from iladub.etkl import interpret
    p = _projection_graph_region()
    rg = _recipe_graph_unpivot("Region", "Year")
    out = interpret.run(os.path.join(QUERIES, "unpivot-forward.rq"), p, rg)
    d = _repro_dict(out)
    assert float(d[("2020", "North")]) == 10.0
    assert float(d[("2021", "South")]) == 21.0
    assert d[("2020", "Year")] == "2020"                    # stub echo
    assert d[("2021", "Year")] == "2021"


def test_strip_forward_sum_readds_total_column():
    import os
    from iladub.etkl import interpret
    p = _projection_graph_region()
    rg = _recipe_graph_unpivot("Region", "Year")
    strip = EX.op1
    rg.add((strip, RDF.type, TAB.StripAggregationOp)); rg.add((strip, TAB.opIndex, Literal(1)))
    rg.add((strip, TAB.opAxis, Literal("column"))); rg.add((strip, TAB.opFunction, Literal("sum")))
    rg.add((strip, TAB.opTargetLabel, Literal("Total")))
    for m in ("North", "South"):
        rg.add((strip, TAB.opMember, Literal(m)))
    # forward strip runs over the repro grid produced by unpivot-forward
    grid = interpret.run(os.path.join(QUERIES, "unpivot-forward.rq"), p, rg)
    out = interpret.run(os.path.join(QUERIES, "strip-aggregation-forward-sum.rq"), grid, rg)
    d = _repro_dict(out)
    assert float(d[("2020", "Total")]) == 30.0              # 10 + 20
    assert float(d[("2021", "Total")]) == 32.0              # 11 + 21
```

- [ ] **Step 2: Write the re-expressed `test_oracle.py`**

Replace the entire contents of `tests/etkl/test_oracle.py` (the old file tests the retired `replay(list[dict])` — re-express against the native-RDF base + SPARQL `round_trip`, per spec §9):

```python
"""Round-trip oracle over the SPARQL forward CONSTRUCTs (loop one).

Supersedes the old Python-replay tests: the base is now a derived hproj:Projection
RDF graph; round_trip reconstructs the grid via the forward .rq files and exact-compares.
"""
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD
from iladub.etkl.oracle import round_trip
from iladub.etkl.recipe import UnpivotOp, StripAggregationOp, Recipe

TAB = Namespace("https://w3id.org/iladub/tab#"); EX = Namespace("https://example.org/d#")


def _base_region():
    """4-fact native-RDF base for Region×Year."""
    p = Graph()
    facts = [("10", "North", "2020"), ("20", "South", "2020"),
             ("11", "North", "2021"), ("21", "South", "2021")]
    for i, (mv, region, year) in enumerate(facts):
        bf = EX["bf%d" % i]
        p.add((bf, RDF.type, TAB.BaseFact)); p.add((bf, TAB.measureValue, Literal(mv, datatype=XSD.decimal)))
        cd = EX["bf%d-dim" % i]; cs = EX["bf%d-stub" % i]
        p.add((bf, TAB.atDimensionValue, cd)); p.add((cd, TAB.dimensionName, Literal("Region"))); p.add((cd, TAB.value, Literal(region)))
        p.add((bf, TAB.atDimensionValue, cs)); p.add((cs, TAB.dimensionName, Literal("Year"))); p.add((cs, TAB.value, Literal(year)))
    return p


ORIGINAL = {("2020", "North"): "10", ("2020", "South"): "20",
            ("2021", "North"): "11", ("2021", "South"): "21",
            ("2020", "Year"): "2020", ("2021", "Year"): "2021"}


def test_correct_recipe_round_trips():
    v = round_trip(ORIGINAL, _base_region(), Recipe((UnpivotOp("Region", "Year"),)))
    assert v.ok and v.residue == ()


def test_corrupted_base_is_rejected():
    bad = _base_region()
    # corrupt one measure: set bf0 (10 -> 999)
    bad.set((EX.bf0, TAB.measureValue, Literal("999", datatype=XSD.decimal)))
    v = round_trip(ORIGINAL, bad, Recipe((UnpivotOp("Region", "Year"),)))
    assert not v.ok and v.residue


def test_strip_round_trips_total_column():
    original = dict(ORIGINAL)
    original[("2020", "Total")] = "30"; original[("2021", "Total")] = "32"
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    v = round_trip(original, _base_region(), recipe)
    assert v.ok, v.residue
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/etkl/test_interpret.py tests/etkl/test_oracle.py -v`
Expected: FAIL — forward `.rq` files do not exist; `round_trip` still expects a `list[dict]` base and calls `replay`.

- [ ] **Step 4: Declare the reconstruction shape in `tab.ttl`**

In `vocab/ontology/tab.ttl`, after the `tab:opValue` declaration (added in Task 2), add:

```turtle
# --- reconstruction cells (round-trip oracle only; never merged into the source table) ---
tab:ReproCell a owl:Class ; rdfs:label "Reconstruction cell"@en ;
    rdfs:comment "A grid cell regenerated by the forward reshape CONSTRUCTs for round-trip verification; transient, never asserted into a table holon."@en .
tab:reproRow a owl:DatatypeProperty ; rdfs:domain tab:ReproCell ; rdfs:range xsd:string ; rdfs:label "repro row"@en .
tab:reproCol a owl:DatatypeProperty ; rdfs:domain tab:ReproCell ; rdfs:range xsd:string ; rdfs:label "repro column"@en .
tab:reproText a owl:DatatypeProperty ; rdfs:domain tab:ReproCell ; rdfs:range rdfs:Literal ; rdfs:label "repro text"@en .
```

- [ ] **Step 5: Implement `unpivot-forward.rq`**

Create `vocab/queries/unpivot-forward.rq`:

```sparql
# unpivot-forward.rq  (base -> grid). Re-pivots each base fact's measure into its
# (stub value, dimension value) cell and echoes the stub column. Emits ReproCells.
PREFIX tab: <https://w3id.org/iladub/tab#>
CONSTRUCT {
  ?mcell a tab:ReproCell ; tab:reproRow ?stubVal ; tab:reproCol ?dimVal  ; tab:reproText ?mtext .
  ?scell a tab:ReproCell ; tab:reproRow ?stubVal ; tab:reproCol ?stubName ; tab:reproText ?stubVal .
}
WHERE {
  ?op a tab:UnpivotOp ; tab:opDimension ?dimName ; tab:opStub ?stubName .
  ?bf a tab:BaseFact ; tab:measureValue ?mv ;
      tab:atDimensionValue ?coDim , ?coStub .
  ?coDim  tab:dimensionName ?dimName  ; tab:value ?dimVal .
  ?coStub tab:dimensionName ?stubName ; tab:value ?stubVal .
  BIND(STR(?mv) AS ?mtext)
  BIND(IRI(CONCAT(STR(?bf), "-mc")) AS ?mcell)
  BIND(IRI(CONCAT(STR(?bf), "-sc")) AS ?scell)
}
```

- [ ] **Step 6: Implement `strip-aggregation-forward-sum.rq`**

Create `vocab/queries/strip-aggregation-forward-sum.rq`. It runs over the repro grid (ReproCells from `unpivot-forward.rq`) and re-adds each `sum` aggregate row/col:

```sparql
# strip-aggregation-forward-sum.rq  (repro grid -> repro grid + aggregate cells).
# For a column-axis strip: for each row, SUM the member columns -> a Total cell in that row.
# For a row-axis strip: for each column, SUM the member rows -> a Total cell in that column.
# SPARQL 1.1 SUM; the function is 'sum' (F&O fn:sum, per tab-fno-align.ttl). Standard SPARQL
# cannot parameterize the aggregate operator by a bound variable, so 'sum' has its own .rq;
# other functions ship their own file (mean/min/max/count); 'product' is the SPARQL-ceiling
# case (no aggregate operator) -> justified PROCEDURAL if ever needed. Loop one only exercises sum.
PREFIX tab: <https://w3id.org/iladub/tab#>
CONSTRUCT {
  ?cell a tab:ReproCell ; tab:reproRow ?rrow ; tab:reproCol ?rcol ; tab:reproText ?ttext .
}
WHERE {
  {
    # column-axis: group members within each row
    ?op a tab:StripAggregationOp ; tab:opAxis "column" ; tab:opFunction "sum" ; tab:opTargetLabel ?target .
    {
      SELECT ?row (SUM(?vnum) AS ?total) WHERE {
        ?op2 a tab:StripAggregationOp ; tab:opAxis "column" ; tab:opMember ?member .
        ?mc a tab:ReproCell ; tab:reproRow ?row ; tab:reproCol ?member ; tab:reproText ?mtext .
        BIND(xsd:decimal(?mtext) AS ?vnum)
      } GROUP BY ?row
    }
    BIND(?row AS ?rrow) BIND(?target AS ?rcol) BIND(STR(?total) AS ?ttext)
    BIND(IRI(CONCAT("urn:repro:col:", ?rrow, ":", ?target)) AS ?cell)
  }
  UNION
  {
    # row-axis: group members within each column, excluding stub-echo columns is unnecessary
    # here because members name data rows only; the target column set = data columns present.
    ?op a tab:StripAggregationOp ; tab:opAxis "row" ; tab:opFunction "sum" ; tab:opTargetLabel ?target .
    {
      SELECT ?col (SUM(?vnum) AS ?total) WHERE {
        ?op2 a tab:StripAggregationOp ; tab:opAxis "row" ; tab:opMember ?member .
        ?mc a tab:ReproCell ; tab:reproRow ?member ; tab:reproCol ?col ; tab:reproText ?mtext .
        FILTER(?col != ?stubName2 || !BOUND(?stubName2))
        BIND(xsd:decimal(?mtext) AS ?vnum)
        OPTIONAL { ?u a tab:UnpivotOp ; tab:opStub ?stubName2 . FILTER(?col = ?stubName2) }
      } GROUP BY ?col
    }
    BIND(?col AS ?rcol) BIND(?target AS ?rrow) BIND(STR(?total) AS ?ttext)
    BIND(IRI(CONCAT("urn:repro:row:", ?target, ":", ?col)) AS ?cell)
  }
}
```

Note for the implementer: the row-axis stub exclusion is subtle (a row-axis total must not be written into the stub-echo column). If the `OPTIONAL`/`FILTER` form above proves awkward in rdflib, express the exclusion as `FILTER NOT EXISTS { ?u a tab:UnpivotOp ; tab:opStub ?col }` inside the sub-`SELECT`. Drive the choice by the failing test — the behaviour required is "row-axis strip does not produce a cell in any unpivot stub column" (exactly the regression `test_row_axis_strip_excludes_numeric_stub_column` guarded in the retired `test_oracle.py`). Add that regression as a forward unit test if the column path does not already cover it.

Also add `PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>` to the top of this query (used by `xsd:decimal`).

- [ ] **Step 7: Rewrite `oracle.round_trip` to run the forward CONSTRUCTs; delete the Python interpreter**

Replace the whole of `src/iladub/etkl/oracle.py` with:

```python
"""oracle — the round-trip reproduction oracle (loop one, SPARQL executor).

A recipe is certified iff running the FORWARD reshape CONSTRUCTs over the derived base
(a hproj:Projection RDF graph) regenerates the original grid cell values exactly. The
transform is AXIOM (standard SPARQL CONSTRUCT + SPARQL 1.1 aggregates in vocab/queries/);
the ONLY Python here is the exact-equality compare (_close / _TOL), which is decidable
arithmetic and irreducible (PROCEDURAL).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Namespace, RDF

from . import interpret
from .recipe import UnpivotOp, StripAggregationOp

TAB = Namespace("https://w3id.org/iladub/tab#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")
_TOL = 1e-6                    # PROCEDURAL: decidable exact-equality tolerance for the compare,
                              # NOT a transform tuning constant. It never enters the .rq files.


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


def _isnum(s):
    try:
        float(s); return True
    except (TypeError, ValueError):
        return False


@dataclass(frozen=True)
class OracleVerdict:
    ok: bool
    residue: tuple


def _repro_grid(base, recipe):
    """Run the forward CONSTRUCTs over the derived base -> {(row_label, col_label): text}."""
    from .reshape import _materialize_recipe   # local import avoids a cycle
    from rdflib import URIRef, Graph
    recipe_graph = Graph()
    _materialize_recipe(recipe_graph, URIRef("urn:reshape:t"), recipe)
    # 1. unpivot forward: base -> repro measure + stub cells
    grid = interpret.run(os.path.join(_QUERIES, "unpivot-forward.rq"), base, recipe_graph)
    # 2. strip forward (sum): re-add aggregate rows/cols over the repro grid, ordered by opIndex
    strips = [op for op in recipe.operations if isinstance(op, StripAggregationOp)]
    if strips:
        added = interpret.run(os.path.join(_QUERIES, "strip-aggregation-forward-sum.rq"),
                              grid, recipe_graph)
        grid += added
    out = {}
    for cell in grid.subjects(RDF.type, TAB.ReproCell):
        rrow = str(grid.value(cell, TAB.reproRow))
        rcol = str(grid.value(cell, TAB.reproCol))
        out[(rrow, rcol)] = str(grid.value(cell, TAB.reproText))
    return out


def round_trip(original, base, recipe):
    """Run the forward reshape CONSTRUCTs over `base` (the derived hproj:Projection graph)
    and exact-compare to `original` (from grid_values). Numeric cells compare with tolerance;
    text cells compare literally. Signature unchanged from the Python-replay era."""
    repro = _repro_grid(base, recipe)
    residue = []
    for key, want in original.items():
        got = repro.get(key)
        if got is None:
            residue.append("missing %r (want %r)" % (key, want)); continue
        if _isnum(want) and _isnum(got):
            if not _close(float(got), float(want)):
                residue.append("mismatch %r: want %s got %s" % (key, want, got))
        elif got != want:
            residue.append("mismatch %r: want %r got %r" % (key, want, got))
    for key in repro:
        if key not in original:
            residue.append("extra %r = %r" % (key, repro[key]))
    return OracleVerdict(not residue, tuple(residue))
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `python -m pytest tests/etkl/test_interpret.py tests/etkl/test_oracle.py -v`
Expected: PASS. If the strip-forward row-axis exclusion misfires, fix the query per the Step 6 note — the compare is correct; the query is the unit under test.

- [ ] **Step 9: Commit**

```bash
git add vocab/queries/unpivot-forward.rq vocab/queries/strip-aggregation-forward-sum.rq vocab/ontology/tab.ttl src/iladub/etkl/oracle.py tests/etkl/test_interpret.py tests/etkl/test_oracle.py
git commit -m "feat(etkl): forward CONSTRUCT pair + SPARQL round_trip; retire replay/_fmt [A/loop-one task 3]

round_trip now reconstructs the grid via unpivot-forward.rq + strip-aggregation-forward-sum.rq
(AXIOM) and exact-compares in Python (_close, PROCEDURAL). The Python interpreter
(oracle.replay/_fmt/_FUNCS) is deleted; test_oracle re-expressed over the native-RDF base.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: `reshape` inverse rewire — `derive_base` (native-RDF base), `certify`, emit; retire `recover_base`/`emit_base_facts` loops

Replaces the Python base-recovery/emission twins with the inverse CONSTRUCT. `certify` returns the derived projection graph as `base` (decision B); `emit_base_projection` merges it; `emit_base_facts` is re-backed onto the same CONSTRUCT. The named-path mechanism tests coupled to `list[dict]`/`recover_base` are re-expressed; the behavioural projection/strip/order-independence tests stay green unchanged.

**Files:**
- Modify: `src/iladub/etkl/reshape.py` (add `derive_base`; retire `recover_base`; rewrite `certify`, `emit_base_projection`, `emit_normalized_base`)
- Modify: `src/iladub/etkl/denormalization.py:293-327` (`emit_base_facts` re-backed onto `derive_base`)
- Test: `tests/etkl/test_reshape_recover.py`, `tests/etkl/test_reshape_certify.py`, `tests/etkl/test_denorm_integration.py`, `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `reshape.derive_base(g, t, recipe) -> rdflib.Graph` — materializes `recipe` into a recipe graph, runs `vocab/queries/unpivot-inverse.rq` over `(g + recipe_graph)`, returns the projection graph (a set of `tab:BaseFact` nodes with `tab:measureValue` + `tab:atDimensionValue` coordinates). Replaces `recover_base`.
- Produces: `reshape.certify(g, t) -> (Recipe, OracleVerdict, rdflib.Graph)` — third value `base` is now the derived projection graph (empty graph ⇒ falsy ⇒ short-circuits, matching the old `if not base`). Public promotion/oracle behaviour unchanged.
- Produces: `reshape.emit_base_projection(g, t, recipe, base_graph) -> URIRef` — merges `base_graph` into `g`, wraps it with the `tab:NormalizedBase` node (`tab:derivedByRecipe`, `prov:wasDerivedFrom`, `tab:hasBaseFact`). Same return contract.
- Consumes: `interpret.run`, `unpivot-inverse.rq` (Tasks 1-2); `round_trip` (Task 3); `_materialize_recipe` (Task 2).

- [ ] **Step 1: Re-express the named-path mechanism tests (write them first, failing)**

Edit `tests/etkl/test_reshape_recover.py::test_recover_recipe_and_base_region` — the recipe assertion stays; the base assertion moves from `list[dict]` to the native-RDF projection. Replace the base half (lines 19-24) with:

```python
    from iladub.etkl.reshape import recover_recipe, derive_base
    base = derive_base(rep.graph, t, recipe)
    facts = list(base.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 8                                  # 2 years x 4 regions
    measures = sorted(float(base.value(f, TAB.measureValue)) for f in facts)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    coords = {(str(base.value(co, TAB.dimensionName)), str(base.value(co, TAB.value)))
              for f in facts for co in base.objects(f, TAB.atDimensionValue)}
    assert ("Region", "North") in coords and ("Year", "2020") in coords
```

(Update the import line at the top of that test from `recover_base` to `derive_base`, and add `RDF` to the rdflib import if needed.)

In `tests/etkl/test_reshape_certify.py`:
- `test_certify_region_pivot_passes` (line 19): change `assert len(base) == 8` to:
  ```python
      from rdflib import RDF as _RDF
      assert len(list(base.subjects(_RDF.type, TAB.BaseFact))) == 8
  ```
- `test_certify_pivotless_table_no_false_residue` (line 191): change `assert base == []` to `assert not base` (empty projection graph is falsy).
- `test_emit_returns_none_on_oracle_failure` (lines 57-58): change the monkeypatch target from `recover_base` to `derive_base`, dropping one base fact from the returned projection:
  ```python
      orig = reshape.derive_base
      def _drop_one(gg, tt, rr):
          p = orig(gg, tt, rr)
          facts = list(p.subjects(RDF.type, TAB.BaseFact))
          if facts:
              victim = facts[0]
              for pr, o in list(p.predicate_objects(victim)):
                  p.remove((victim, pr, o))
              p.remove((victim, RDF.type, TAB.BaseFact))
          return p
      reshape.derive_base = _drop_one
      try:
          nb = reshape.emit_normalized_base(g, t)
      finally:
          reshape.derive_base = orig
  ```

In `tests/etkl/test_denorm_integration.py::test_analyze_escalates_on_oracle_failure` (lines 34-35): change the monkeypatch from `reshape.recover_base` to `reshape.derive_base` using the same `_drop_one` shape (import `RDF` and `TAB` are already present). Replace lines 34-39 with:

```python
    orig = reshape.derive_base
    def _drop_one(gg, tt, rr):
        p = orig(gg, tt, rr)
        facts = list(p.subjects(RDF.type, TAB.BaseFact))
        if facts:
            victim = facts[0]
            for pr, o in list(p.predicate_objects(victim)):
                p.remove((victim, pr, o))
        return p
    reshape.derive_base = _drop_one
    try:
        dr = analyze(rep)
    finally:
        reshape.derive_base = orig
```

- [ ] **Step 2: Run the re-expressed tests to verify they fail**

Run: `python -m pytest tests/etkl/test_reshape_recover.py::test_recover_recipe_and_base_region tests/etkl/test_reshape_certify.py tests/etkl/test_denorm_integration.py -v`
Expected: FAIL — `reshape.derive_base` does not exist yet.

- [ ] **Step 3: Implement `derive_base`; rewrite `certify`, `emit_base_projection`, `emit_normalized_base`; delete `recover_base`**

In `src/iladub/etkl/reshape.py`:

Add imports at the top (near the existing rdflib import): `import os` and `from . import interpret`, plus `from rdflib import Graph` (extend the existing `from rdflib import ...` line to include `Graph`). Add (note: `reshape.py` sits at `src/iladub/etkl/`, three directories below the repo root, so the path needs **three** `..` — matching the corrected `_QUERIES` in `oracle.py` from Task 3):

```python
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")
```

Delete `recover_base` (lines 80-110) entirely and replace with:

```python
def derive_base(g, t, recipe):
    """The derived flat base as a native-RDF hproj:Projection graph: run the inverse
    reshape CONSTRUCT (vocab/queries/unpivot-inverse.rq) over the source grid + the
    materialized recipe. Returns a graph of tab:BaseFact nodes (measure + coordinates).
    Replaces the retired Python recover_base/emit_base_facts twin. AXIOM (SPARQL);
    the only Python is interpret engine-glue + recipe materialization."""
    recipe_graph = Graph()
    _materialize_recipe(recipe_graph, t, recipe)
    return interpret.run(os.path.join(_QUERIES, "unpivot-inverse.rq"), g, recipe_graph)
```

Rewrite `certify` (lines 113-123):

```python
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
```

Rewrite `emit_base_projection` (lines 147-167) so it merges the projection graph rather than looping a `list[dict]`:

```python
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
```

Update `emit_normalized_base` (lines 170-175) — it already passes `base` through; confirm it reads:

```python
def emit_normalized_base(g, t):
    """A1: if the deterministic recipe round-trips, emit the derived projection; else None."""
    recipe, verdict, base = certify(g, t)
    if not verdict.ok or len(list(base.subjects(RDF.type, TAB.BaseFact))) == 0:
        return None
    return emit_base_projection(g, t, recipe, base)
```

- [ ] **Step 4: Re-back `denormalization.emit_base_facts` onto the CONSTRUCT path**

In `src/iladub/etkl/denormalization.py`, replace the body of `emit_base_facts` (lines 293-327) with a delegation to the single inverse-CONSTRUCT path (keeps the public export and its two tests green, DRY with `derive_base`):

```python
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
```

- [ ] **Step 5: Run the full affected suites to verify green**

Run: `python -m pytest tests/etkl/test_reshape_recover.py tests/etkl/test_reshape_certify.py tests/etkl/test_denorm_integration.py tests/etkl/test_denormalization.py -v`
Expected: PASS — including the behavioural (unchanged) tests: `test_emit_normalized_base_is_derived_projection`, `test_certify_strip_in_composition_round_trips`, `test_certify_stub_selection_is_order_independent`, `test_emit_base_facts_unpivots_region`, `test_emit_base_facts_strips_aggregation_column`, `test_analyze_end_to_end`, `test_analyze_yields_certified_recipe_and_projection`. If any behavioural test needs an assertion change, STOP — that is a supersession defect to investigate, not a test to loosen.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/reshape.py src/iladub/etkl/denormalization.py tests/etkl/test_reshape_recover.py tests/etkl/test_reshape_certify.py tests/etkl/test_denorm_integration.py
git commit -m "feat(etkl): derive_base (native-RDF projection) via inverse CONSTRUCT; retire recover_base + emit_base_facts loop [A/loop-one task 4]

certify returns the derived hproj:Projection graph as base (decision B); emit merges it;
emit_base_facts re-backed onto the single SPARQL path. Named-path mechanism tests
re-expressed; projection/strip/order-independence behaviour unchanged.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: A2.1 nameless value-set pivot — CONSTRUCT-based base (`certify_with_proposals` green)

`_named_pivot_recipe_and_base` builds a `list[dict]` for the nameless-pivot case (measure columns detected by value-set membership). Decision B reworks it so the nameless case emits its base via a **value-set inverse CONSTRUCT**, keeping `certify_with_proposals`'s public behaviour and A2.1's promotion tests green.

**Files:**
- Create: `vocab/queries/unpivot-inverse-valueset.rq`
- Modify: `src/iladub/etkl/reshape.py` (`_named_pivot_recipe_and_base` → CONSTRUCT-based; `certify_with_proposals` passes the projection graph to `emit_base_projection`)
- Test: `tests/etkl/test_certify_proposals.py` (must stay green unchanged), `tests/etkl/test_interpret.py` (value-set unit test)

**Interfaces:**
- Produces: `vocab/queries/unpivot-inverse-valueset.rq` — like `unpivot-inverse.rq`, but measure columns are the leaves whose label is a declared `tab:opValue` on the `tab:UnpivotOp` (nameless pivot), and the coordinate dimension name is the op's `tab:opDimension` (the proposed name). Emits the same `tab:BaseFact` shape.
- Produces: `reshape._named_pivot_recipe_and_base(g, t, dim, name) -> (Recipe, rdflib.Graph)` — the base is now the projection graph (empty graph when ragged/non-invertible). `certify_with_proposals` treats an empty projection as non-invertible (escalate), matching current behaviour.
- Consumes: `interpret.run`, `derive_base` machinery, `round_trip`, `emit_base_projection` (Tasks 1-4).

- [ ] **Step 1: Write the failing value-set unit test**

Add to `tests/etkl/test_interpret.py`:

```python
def _nameless_quarter_pivot():
    """Product stub + nameless Q1..Q4 pivot (spanning parent has no label); 2 rows A/B."""
    g = Graph(); t = EX.tbl2
    cols = [EX["q%d" % i] for i in range(5)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        if lbl is not None:
            lc = URIRef(str(u) + "l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.qstub, 0, "Product", [cols[0]])
    hdr(EX.qspan, 0, None, cols[1:])
    for c, nm in zip(cols[1:], ["Q1", "Q2", "Q3", "Q4"]):
        hdr(URIRef(str(c) + "h"), 1, nm, [c])
    vals = {"A": ["A", "1", "2", "3", "4"], "B": ["B", "5", "6", "7", "8"]}
    for rname in ("A", "B"):
        ru = EX["row" + rname]; g.add((ru, RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru))
        for c, txt in zip(cols, vals[rname]):
            e = EX["e2_%s_%s" % (rname, str(c)[-2:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru)); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    return g, t


def test_valueset_inverse_detects_measures_by_value_set():
    import os
    from iladub.etkl import interpret
    g, t = _nameless_quarter_pivot()
    rg = Graph(); op = EX.vop
    rg.add((op, RDF.type, TAB.UnpivotOp)); rg.add((op, TAB.opIndex, Literal(0)))
    rg.add((op, TAB.opAxis, Literal("column"))); rg.add((op, TAB.opDimension, Literal("Quarter")))
    rg.add((op, TAB.opStub, Literal("Product")))
    for v in ("Q1", "Q2", "Q3", "Q4"):
        rg.add((op, TAB.opValue, Literal(v)))
    out = interpret.run(os.path.join(QUERIES, "unpivot-inverse-valueset.rq"), g, rg)
    facts = list(out.subjects(RDF.type, TAB.BaseFact))
    assert len(facts) == 8                                  # 2 rows x 4 quarters
    coords = {(str(out.value(co, TAB.dimensionName)), str(out.value(co, TAB.value)))
              for f in facts for co in out.objects(f, TAB.atDimensionValue)}
    assert ("Quarter", "Q1") in coords and ("Product", "A") in coords
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/etkl/test_interpret.py::test_valueset_inverse_detects_measures_by_value_set -v`
Expected: FAIL — `unpivot-inverse-valueset.rq` does not exist.

- [ ] **Step 3: Implement `unpivot-inverse-valueset.rq`**

Create `vocab/queries/unpivot-inverse-valueset.rq`:

```sparql
# unpivot-inverse-valueset.rq  (grid -> base) for a NAMELESS column pivot (A2.1).
# Measure columns are the level-1 leaves whose label is a declared tab:opValue on the op;
# the coordinate dimension name is the op's tab:opDimension (the GenAI-proposed name, which
# enters ONLY the recipe + base coordinates, never the source graph).
PREFIX tab: <https://w3id.org/iladub/tab#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
CONSTRUCT {
  ?bf a tab:BaseFact ;
      tab:measureValue ?mv ;
      tab:atDimensionValue ?coDim , ?coStub .
  ?coDim  tab:dimensionName ?dimName ; tab:value ?colLabel .
  ?coStub tab:dimensionName ?stubName ; tab:value ?stubVal .
}
WHERE {
  ?op a tab:UnpivotOp ; tab:opDimension ?dimName ; tab:opStub ?stubName ; tab:opValue ?colLabel .

  # measure column: a leaf whose deepest header label equals a declared pivot value ?colLabel
  ?h1 tab:hasLabel ?h1l ; tab:coversColumn ?c .
  ?h1l tab:cellText ?colLabel .

  ?e a tab:EntryCell ; tab:atRow ?r ; tab:atColumn ?c ; tab:cellText ?v .
  BIND(xsd:decimal(?v) AS ?mv)

  # stub column: the level-0 column labelled ?stubName, and this row's stub value
  ?hs tab:headerLevel 0 ; tab:hasLabel ?hsl ; tab:coversColumn ?sc .
  ?hsl tab:cellText ?stubName .
  ?se tab:atRow ?r ; tab:atColumn ?sc ; tab:cellText ?stubVal .

  BIND(IRI(CONCAT(STR(?e), "-bf")) AS ?bf)
  BIND(IRI(CONCAT(STR(?e), "-bf-dim")) AS ?coDim)
  BIND(IRI(CONCAT(STR(?e), "-bf-stub")) AS ?coStub)
}
```

- [ ] **Step 4: Rewrite `_named_pivot_recipe_and_base` to emit a projection graph via the value-set CONSTRUCT**

In `src/iladub/etkl/reshape.py`, replace `_named_pivot_recipe_and_base` (lines 191-225) with:

```python
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
```

- [ ] **Step 5: Update `certify_with_proposals` to use the projection graph**

In `src/iladub/etkl/reshape.py`, update `certify_with_proposals` (lines 240-247) so the empty-check and oracle use the projection graph:

```python
    recipe, base = _named_pivot_recipe_and_base(g, t, dim, proposal.name)
    # Run the oracle UNCONDITIONALLY: a ragged pivot yields an empty projection, over which
    # round_trip reports every original grid cell missing -> ok=False -> escalate. This matches
    # the retired list[dict] behaviour and keeps test_uninvertible_region_is_rejected_even_with_a_name
    # green (it asserts `not out.oracle_ok` on the ragged case). Do NOT short-circuit the empty
    # case to OracleVerdict(True, ()) — that would report oracle_ok=True and fail that test.
    verdict = round_trip(grid_values(g, t), base, recipe)
    if not verdict.ok:
        return ProposalOutcome(None, (), verdict.ok, verdict.residue)   # not invertible -> escalate
    nb = emit_base_projection(g, t, recipe, base)
    from .promote import emit_promotion
    pd = emit_promotion(g, t, nb, proposal.name, list(dim.values), proposal)
    return ProposalOutcome(nb, (pd,), True, ())
```

(`OracleVerdict` is already imported from `.oracle` at the top of `reshape.py`; confirm the import line reads `from .oracle import OracleVerdict, round_trip`.)

- [ ] **Step 6: Run the A2.1 suites to verify green**

Run: `python -m pytest tests/etkl/test_interpret.py tests/etkl/test_certify_proposals.py -v`
Expected: PASS — all four `test_certify_proposals.py` behavioural tests unchanged: `test_happy_path_names_and_inverts` (8 facts, ("Quarter","Q1")+("Product","A") coords), `test_declined_proposal_escalates`, `test_uninvertible_region_is_rejected_even_with_a_name` (ragged → empty projection → escalate), `test_named_pivot_does_not_call_proposer`.

- [ ] **Step 7: Commit**

```bash
git add vocab/queries/unpivot-inverse-valueset.rq src/iladub/etkl/reshape.py tests/etkl/test_interpret.py
git commit -m "feat(etkl): A2.1 nameless pivot base via value-set inverse CONSTRUCT [A/loop-one task 5]

_named_pivot_recipe_and_base emits its base through unpivot-inverse-valueset.rq (measure
detection = tab:opValue membership); certify_with_proposals public behaviour unchanged.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Gate test + full-suite supersession verification + alignment confirmation

Adds the neurosymbolic-gate test (no tuned constant in the transform), confirms the HGA/FnO alignment carries the derived base, and runs the whole `tests/etkl` suite to prove supersession (behaviour preserved, twins retired).

**Files:**
- Create: `tests/etkl/test_transform_gate.py`
- Verify: `vocab/ontology/tab-hga-align.ttl`, `vocab/ontology/tab-fno-align.ttl` (no edit expected)
- Test: whole `tests/etkl` suite + source-ownership CI test

**Interfaces:**
- Consumes: all prior tasks (the `.rq` files, `interpret.py`, `oracle.py`).

- [ ] **Step 1: Write the gate test**

Create `tests/etkl/test_transform_gate.py`:

```python
"""Neurosymbolic-first gate (CLAUDE.md §8): the transform is AXIOM (SPARQL); no tuned
constant or numeric tolerance may live in the .rq files or in interpret.py. The only
numeric tolerance in the substrate is _TOL in oracle.py — the decidable exact-equality
compare (PROCEDURAL), never a transform tuning knob."""
import os
import re
import glob

HERE = os.path.dirname(__file__)
QUERIES = os.path.join(HERE, "..", "..", "vocab", "queries")
INTERPRET = os.path.join(HERE, "..", "..", "src", "iladub", "etkl", "interpret.py")

# a bare decimal/float literal (a tuned tolerance/constant). RDF header-level integers
# 0/1 have no decimal point and never match; xsd:decimal casts contain no digit.digit.
_FLOAT = re.compile(r"(?<![\w:])\d+\.\d+")


def _strip_comments(text):
    """Drop '#'-to-end-of-line comments (both SPARQL and Python) before scanning, so a
    version reference in a comment (e.g. 'SPARQL 1.1', 'A2.1') is not misread as a tuned
    constant. Only executable transform text is scanned."""
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def test_no_tuned_constant_in_rq_files():
    rqs = glob.glob(os.path.join(QUERIES, "*.rq"))
    assert rqs, "expected the reshape CONSTRUCT files to exist"
    for path in rqs:
        body = _strip_comments(open(path, encoding="utf-8").read())
        assert not _FLOAT.search(body), "tuned float constant in transform query %s" % path


def test_no_tuned_constant_in_interpret():
    body = _strip_comments(open(INTERPRET, encoding="utf-8").read())
    assert not _FLOAT.search(body), "interpret.py (engine glue) must carry no numeric tolerance"


def test_replay_and_fmt_are_retired():
    import iladub.etkl.oracle as oracle
    assert not hasattr(oracle, "replay"), "oracle.replay (Python interpreter) must be retired"
    assert not hasattr(oracle, "_fmt"), "oracle._fmt (float-format twin) must be retired"


def test_recover_base_is_retired():
    import iladub.etkl.reshape as reshape
    assert not hasattr(reshape, "recover_base"), "reshape.recover_base must be retired (use derive_base)"
```

- [ ] **Step 2: Run the gate test to verify it passes**

Run: `python -m pytest tests/etkl/test_transform_gate.py -v`
Expected: PASS. If a `.rq` legitimately needs a numeric literal (it should not in loop one), that is a gate signal to re-examine the design — do not weaken the regex to hide it.

- [ ] **Step 3: Confirm the HGA/FnO alignment carries the derived base**

Read `vocab/ontology/tab-hga-align.ttl` — confirm `tab:NormalizedBase rdfs:subClassOf hproj:Projection` is present (it is). Read `vocab/ontology/tab-fno-align.ttl` — confirm `tab:aggFnSum rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#sum>` is present (it is; `strip-aggregation-forward-sum.rq`'s `SUM` realizes exactly that F&O function). No edit expected. If either is missing, add the single alignment triple (subject = owned `tab:` term, object = HGA/FnO IRI) — never the reverse.

Run: `python -m pytest tests/etkl/test_source_ownership.py -v` (if present under `tests/`) or:
Run: `python -m pytest tests/test_source_ownership.py -v`
Expected: PASS — the new `.rq` files reference only `tab:` + standard function IRIs; no HGA/FnO term appears as a subject in an authored ontology file.

- [ ] **Step 4: Run the whole etkl suite (supersession proof)**

Run: `python -m pytest tests/etkl -v`
Expected: PASS — every behavioural suite green, the mechanism suites green in their re-expressed form, the gate test green. If any behavioural assertion is red, STOP and investigate (supersession defect), do not loosen it.

Then run the full project suite to catch cross-module fallout:
Run: `python -m pytest -q`
Expected: PASS (or only pre-existing unrelated skips — e.g. `pdfplumber`/`reportlab` importorskips when those optional deps are absent).

- [ ] **Step 5: Final commit**

```bash
git add tests/etkl/test_transform_gate.py
git commit -m "test(etkl): neurosymbolic-gate + supersession verification for the CONSTRUCT substrate [A/loop-one task 6]

Asserts no tuned constant in the .rq transform or interpret.py; replay/_fmt/recover_base
retired; whole etkl suite green over the SPARQL substrate. Alignment (hproj:/FnO) confirmed.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage** (against `2026-07-14-declarative-transform-substrate-design.md`):
- §3 unpivot inverse CONSTRUCT (prototype promoted) → Task 1. ✔
- §3 strip-inverse (base excludes aggregate rows/cols) → Task 2 (row exclusion; col exclusion via measure-match in Task 1). ✔
- §3 forward direction (`unpivot-forward` + `strip-aggregation-forward` sub-`SELECT SUM … GROUP BY`, FnO-named) → Task 3. ✔
- §3 round-trip oracle = forward CONSTRUCT + exact-compare; `_fmt` retired → Task 3. ✔
- §4 `interpret.py` (engine glue), `oracle.py` modify, `reshape.py` modify, `.rq` files → Tasks 1,3,4,5. ✔
- §4 base typed `hproj:Projection` (derived); §7 derived-not-stored → Tasks 4 (merge) + 6 (alignment confirmation). ✔
- §4 retired: `oracle.replay`, `emit_base_facts` loop, `emit_base_projection` loop → Tasks 3,4. ✔
- §6 testing: per-CONSTRUCT unit tests (Tasks 1,2,3,5), round-trip oracle test (Task 3), gate test (Task 6). ✔
- §9 decision B native-RDF base; behavioural suites green; mechanism tests re-expressed; A2.1 CONSTRUCT-based → Tasks 4,5. ✔
- §8 SPARQL-ceiling (product = ceiling; per-function `.rq`; only `sum` built — YAGNI) → Task 3 query note. ✔
- Gate compliance in every task via Global Constraints + Task 6 gate test. ✔

**2. Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to Task N". Every code step shows the actual code; every `.rq` is written in full. The one deliberately open sub-choice (row-axis strip stub-exclusion form in Task 3 Step 6) is bounded by a named required behaviour + a concrete alternative and a driving test — not a placeholder.

**3. Type consistency:** `interpret.run(query_path, *graphs) -> Graph` (Task 1) used identically in Tasks 3,4,5. `derive_base(g, t, recipe) -> Graph` (Task 4) is the retirement target for the Task 4 monkeypatches (Task 4 Step 1) — consistent. `round_trip(original, base, recipe)` signature stable across Tasks 3-5. `emit_base_projection(g, t, recipe, base)` takes the projection graph in both callers (Tasks 4,5). Recipe-serialization props `tab:opTargetLabel`/`tab:opMember` (Task 2) are read by `strip-aggregation-forward-sum.rq` (Task 3) and the row-exclusion filter (Task 2); `tab:opValue` (Task 2 vocab) is read by `unpivot-inverse-valueset.rq` (Task 5). `tab:ReproCell`/`reproRow`/`reproCol`/`reproText` produced by the forward queries (Task 3) and consumed by `oracle._repro_grid` (Task 3) — consistent.

**Note on one authorized deviation from a literal spec phrase:** spec §4's component table says `round_trip keeps its signature`. It does — `round_trip(original, base, recipe)` is unchanged; only the runtime *type* of `base` moves from `list[dict]` to the projection `Graph` (that is decision B itself). This is supersession, and the four `list[dict]`-coupled assertions/monkeypatches it forces are re-expressed under the spec §9 authorization (enumerated in Task 4 Step 1), never loosened.
