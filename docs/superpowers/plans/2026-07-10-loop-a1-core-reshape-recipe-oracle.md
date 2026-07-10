# Loop A1 (core) — Deterministic Reshape: Recipe + Round-Trip Oracle + Unpivot + Strip — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-model Loop 8a's Python denormalization as an oracle-gated, declarative *reshape recipe*: recover the inverse-authoring operations (unpivot, strip-aggregation) as an ordered RDF recipe, certify it with a round-trip reproduction oracle, and emit the flat base as a *derived* projection — superseding Loop 8a's directly-trusted `tab:BaseFact` emission.

**Architecture:** Recovery stays procedural (reuse Loop 8a's `recover_dimensions` / `detect_aggregations` — the legitimately-algorithmic search), but its output is no longer trusted directly: it produces a declarative `tab:ReshapeRecipe` (ordered `tab:UnpivotOp` / `tab:StripAggregationOp`), the **round-trip oracle** replays that recipe *forward* over the recovered base and requires it to regenerate every original grid cell exactly, and only an oracle-passing recipe yields a `tab:NormalizedBase` — a **derived** projection (`rdfs:subClassOf hproj:Projection`), never stored ground truth. A recipe that fails the oracle escalates as residue; it is never asserted. Operation *functions* are FnO/F&O-named (`fn:sum` etc.); the arithmetic is verified, not labelled.

**Tech Stack:** Python 3, rdflib, pytest. RDF Turtle vocab. No BAML/GenAI, no network — A1 is deterministic only. SPARQL 1.1 aggregate semantics are mirrored by the exact-arithmetic verifier already in `verify_group`; forward replay of positional reshapes is Python (the "no other choice" body of an FnO-declared op).

## Global Constraints

- **Supersede, keep tests green.** Loop 8a's tests (`tests/etkl/test_denormalization.py`, `tests/test_tab.py`) are the behavioural spec. Every one must still pass at the end. Do **not** delete `src/iladub/etkl/denormalization.py`'s recovery functions (`recover_dimensions`, `detect_aggregations`, `verify_group`, `annotate_dimensions`, `annotate_aggregations`) — they are reused as the recovery layer.
- **Oracle is the correctness gate, not a label.** An operation is accepted iff replaying the recipe reproduces the original grid cell values exactly (float tol `abs(a-b) <= 1e-6*max(1,|b|)`, matching `denormalization._close`). No confidence scores. A non-round-tripping recipe → residue, never an assertion.
- **Derived, never stored.** The flat base is a `tab:NormalizedBase` typed `rdfs:subClassOf hproj:Projection`, linked `tab:derivedByRecipe` to its recipe and `prov:wasDerivedFrom` the source table. `tab:BaseFact`s are members of that projection, not free-floating stored triples.
- **Source ownership (CI-enforced by `tests/test_source_ownership.py`).** In every authored `.ttl`, every triple subject is an owned term (`tab:`/`iladub:`/`etkl:`/`dec:`). HGA terms (`hproj:Projection`) and other external terms (`fn:`, `qb:`, `prov:`) appear ONLY as objects, and only inside `*-align.ttl` modules. `tab.ttl` stays standalone (no `holon`/`hproj`/`fn`/`qb` references).
- **Alignment target is the verified in-repo term.** Use `hproj:Projection` (`http://w3id.org/holon/projection/`), mirroring `risk:RiskAssessment rdfs:subClassOf hproj:Projection` in `vocab/ontology/risk-hga-align.ttl`. Do NOT introduce `holon:ProjectionGraph` (unverified).
- **Function IRIs.** Map `sum→fn:sum`, `mean→fn:avg`, `min→fn:min`, `max→fn:max`, `count→fn:count` where `fn: = http://www.w3.org/2005/xpath-functions#`; `product` has no `fn:` term — keep it owned (`tab:product`) and note it. FnO/F&O alignment lives in `vocab/ontology/tab-fno-align.ttl`.
- **Showcase closes the loop.** Part I of `demo/etkl_1a_showcase.ipynb` must be updated to the recipe/oracle framing and the notebook re-run to 0 errors, leading with the rendered original PDF (standing directive).
- **A1.5 (denormalize/join), A1.3 (group-flatten), A1.4 (transpose) are OUT of this plan.** Transpose/group-flatten are a separate A1 plan; denormalize/join is deferred per the design.

---

### Task 1: Reshape-recipe vocabulary + alignment modules

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append after the `tab:value` line, end of file)
- Create: `vocab/ontology/tab-hga-align.ttl`
- Create: `vocab/ontology/tab-fno-align.ttl`
- Test: `tests/etkl/test_recipe_vocab.py`

**Interfaces:**
- Produces (RDF terms used by all later tasks): classes `tab:ReshapeRecipe`, `tab:ReshapeOperation`, `tab:UnpivotOp ⊑ tab:ReshapeOperation`, `tab:StripAggregationOp ⊑ tab:ReshapeOperation`, `tab:NormalizedBase`; properties `tab:hasOperation`, `tab:opIndex` (xsd:integer), `tab:opDimension` (xsd:string), `tab:opStub` (xsd:string), `tab:opAxis` (xsd:string), `tab:opFunction` (xsd:string), `tab:recipeForTable` (object), `tab:derivedByRecipe` (object), `tab:hasBaseFact` (object). Alignment: `tab:NormalizedBase rdfs:subClassOf hproj:Projection`.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_recipe_vocab.py
from rdflib import Graph, Namespace, RDFS
from pathlib import Path

TAB = Namespace("https://w3id.org/iladub/tab#")
HPROJ = Namespace("http://w3id.org/holon/projection/")
VOCAB = Path(__file__).resolve().parents[2] / "vocab" / "ontology"


def _g(*names):
    g = Graph()
    for n in names:
        g.parse(VOCAB / n, format="turtle")
    return g


def test_recipe_terms_present_and_standalone():
    g = _g("tab.ttl")                       # core must parse standalone
    for c in ["ReshapeRecipe", "ReshapeOperation", "UnpivotOp",
              "StripAggregationOp", "NormalizedBase"]:
        assert (TAB[c], None, None) in g, c
    assert (TAB.UnpivotOp, RDFS.subClassOf, TAB.ReshapeOperation) in g
    assert (TAB.StripAggregationOp, RDFS.subClassOf, TAB.ReshapeOperation) in g
    # standalone core: no HGA / FnO leakage
    assert "w3id.org/holon" not in g.serialize(format="turtle")
    assert "xpath-functions" not in g.serialize(format="turtle")


def test_hga_alignment_projection():
    g = _g("tab.ttl", "tab-hga-align.ttl")
    assert (TAB.NormalizedBase, RDFS.subClassOf, HPROJ.Projection) in g


def test_fno_alignment_maps_sum():
    g = _g("tab.ttl", "tab-fno-align.ttl")
    fn_sum = "http://www.w3.org/2005/xpath-functions#sum"
    assert fn_sum in g.serialize(format="turtle")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_recipe_vocab.py -v`
Expected: FAIL (files/terms missing).

- [ ] **Step 3: Append recipe vocabulary to `vocab/ontology/tab.ttl`**

```turtle
# --- reshape recipe (inverse report-authoring grammar; Loop A1) ----------------
tab:ReshapeRecipe a owl:Class ; rdfs:label "Reshape recipe"@en ;
    rdfs:comment "An ordered sequence of inverse report-authoring operations that regenerate a report from its flat base. Certified by round-trip reproduction."@en .
tab:ReshapeOperation a owl:Class ; rdfs:label "Reshape operation"@en ;
    rdfs:comment "One operation in a reshape recipe (unpivot, strip-aggregation, ...)."@en .
tab:UnpivotOp a owl:Class ; rdfs:subClassOf tab:ReshapeOperation ; rdfs:label "Unpivot operation"@en ;
    rdfs:comment "Inverse of pivot: a named dimension whose values were rotated into a header axis is folded back into one column."@en .
tab:StripAggregationOp a owl:Class ; rdfs:subClassOf tab:ReshapeOperation ; rdfs:label "Strip-aggregation operation"@en ;
    rdfs:comment "Inverse of add-subtotal/total: a derived row/column proven by exact arithmetic is removed (re-derivable)."@en .
tab:hasOperation a owl:ObjectProperty ; rdfs:domain tab:ReshapeRecipe ; rdfs:range tab:ReshapeOperation ; rdfs:label "has operation"@en .
tab:recipeForTable a owl:ObjectProperty ; rdfs:domain tab:ReshapeRecipe ; rdfs:label "recipe for table"@en .
tab:opIndex a owl:DatatypeProperty ; rdfs:domain tab:ReshapeOperation ; rdfs:range xsd:integer ; rdfs:label "operation index"@en ;
    rdfs:comment "Position in the recipe; forward replay applies operations in ascending order."@en .
tab:opDimension a owl:DatatypeProperty ; rdfs:domain tab:UnpivotOp ; rdfs:range xsd:string ; rdfs:label "operation dimension"@en .
tab:opStub a owl:DatatypeProperty ; rdfs:domain tab:UnpivotOp ; rdfs:range xsd:string ; rdfs:label "operation stub"@en .
tab:opAxis a owl:DatatypeProperty ; rdfs:domain tab:ReshapeOperation ; rdfs:range xsd:string ; rdfs:label "operation axis"@en ;
    rdfs:comment "row | column."@en .
tab:opFunction a owl:DatatypeProperty ; rdfs:domain tab:StripAggregationOp ; rdfs:range xsd:string ; rdfs:label "operation function"@en ;
    rdfs:comment "sum | mean | count | min | max | product — FnO/F&O-named in tab-fno-align.ttl."@en .

# --- normalized base (derived projection; re-models the stored BaseFact set) ----
tab:NormalizedBase a owl:Class ; rdfs:label "Normalized base"@en ;
    rdfs:comment "The flat (3NF) facts a report was built from — a DERIVED projection produced by an oracle-certified recipe, never stored as ground truth."@en .
tab:derivedByRecipe a owl:ObjectProperty ; rdfs:domain tab:NormalizedBase ; rdfs:range tab:ReshapeRecipe ; rdfs:label "derived by recipe"@en .
tab:hasBaseFact a owl:ObjectProperty ; rdfs:domain tab:NormalizedBase ; rdfs:range tab:BaseFact ; rdfs:label "has base fact"@en .
```

- [ ] **Step 4: Create `vocab/ontology/tab-hga-align.ttl`**

```turtle
@prefix tab:   <https://w3id.org/iladub/tab#> .
@prefix hproj: <http://w3id.org/holon/projection/> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .

#################################################################
#  Alignment ONLY — tab: subjects, HGA objects. Never import.
#  Anchor: HGA hproj: (mirrors risk:RiskAssessment ⊑ hproj:Projection).
#  The normalized base is a DERIVED projection of the table-holon,
#  not a stored dataset.
#################################################################
tab:NormalizedBase rdfs:subClassOf hproj:Projection ; rdfs:seeAlso hproj:Projection .
```

- [ ] **Step 5: Create `vocab/ontology/tab-fno-align.ttl`**

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix fn:  <http://www.w3.org/2005/xpath-functions#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

#################################################################
#  Alignment ONLY — tab: subjects, F&O function IRIs as objects.
#  The aggregation a StripAggregationOp inverts is named by its
#  standard XPath/SPARQL function IRI (shared by SPARQL & FnO),
#  so "column = SUM(...)" is a verifiable rule, not an opaque string.
#  'product' has no fn: term — kept owned as tab:product.
#################################################################
tab:aggFnSum   rdfs:seeAlso fn:sum .
tab:aggFnMean  rdfs:seeAlso fn:avg .
tab:aggFnMin   rdfs:seeAlso fn:min .
tab:aggFnMax   rdfs:seeAlso fn:max .
tab:aggFnCount rdfs:seeAlso fn:count .
tab:aggFnProduct rdfs:seeAlso tab:product .
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_recipe_vocab.py -v`
Expected: PASS (3 tests).
Also run `.venv/bin/pytest tests/test_source_ownership.py -v` — Expected: PASS (new align modules keep HGA/fn as objects only).

- [ ] **Step 7: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/ontology/tab-hga-align.ttl vocab/ontology/tab-fno-align.ttl tests/etkl/test_recipe_vocab.py
git commit -m "feat(tab): reshape-recipe vocabulary + hproj:/FnO alignment (Loop A1 core)"
```

---

### Task 2: Recipe model + grid extraction (`recipe.py`)

**Files:**
- Create: `src/iladub/etkl/recipe.py`
- Test: `tests/etkl/test_recipe.py`

**Interfaces:**
- Consumes: the compiled grid model — `tab:hasLeafColumn`/`hasLeafRow`, `tab:EntryCell` with `tab:atRow`/`atColumn`/`cellText`, header nodes with `tab:coversColumn`, `tab:headerLevel`, `tab:hasLabel`→`tab:cellText`.
- Produces:
  - `@dataclass(frozen=True) UnpivotOp(dimension: str, stub: str, axis: str = "column")`
  - `@dataclass(frozen=True) StripAggregationOp(axis: str, function: str, member_labels: tuple[str, ...], target_label: str)`
  - `@dataclass(frozen=True) Recipe(operations: tuple)` — operations ordered as applied *forward* (unpivot then strips).
  - `grid_values(g, t) -> dict[tuple[str, str], str]` — `{(row_label, col_leaf_label): cell_text}` for every entry cell; `row_label` = the row's stub entry text if present else the row URI tail; `col_leaf_label` = the deepest (single-covering) header label of the column.
  - `col_leaf_label(g, c) -> str | None`, `row_label(g, t, r) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_recipe.py
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.recipe import (UnpivotOp, StripAggregationOp, Recipe,
                                 grid_values, col_leaf_label)

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _grid():
    """Year stub + Region(N/S) pivot; 2 rows. Values: 2020->10,20 ; 2021->11,21."""
    g = Graph(); t = EX.tbl
    cols = [EX.c0, EX.c1, EX.c2]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hYear, 0, "Year", [cols[0]]); hdr(EX.hReg, 0, "Region", cols[1:])
    hdr(EX.hN, 1, "North", [cols[1]]); hdr(EX.hS, 1, "South", [cols[2]])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"2020": ["2020", "10", "20"], "2021": ["2021", "11", "21"]}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c, txt in zip(cols, vals[r]):
            e = EX["e_%s_%s" % (r, str(c)[-1])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    return g, t


def test_col_leaf_label():
    g, t = _grid()
    assert col_leaf_label(g, EX.c1) == "North"
    assert col_leaf_label(g, EX.c0) == "Year"


def test_grid_values():
    g, t = _grid()
    gv = grid_values(g, t)
    assert gv[("2020", "North")] == "10"
    assert gv[("2021", "South")] == "21"
    assert gv[("2020", "Year")] == "2020"
    assert len(gv) == 6                                   # 2 rows x 3 cols


def test_recipe_is_ordered():
    r = Recipe((UnpivotOp("Region", "Year"), StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    assert [type(o).__name__ for o in r.operations] == ["UnpivotOp", "StripAggregationOp"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_recipe.py -v`
Expected: FAIL (`No module named 'iladub.etkl.recipe'`).

- [ ] **Step 3: Implement `src/iladub/etkl/recipe.py`**

```python
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
    """Deepest header label covering exactly leaf column c (the single-covering node)."""
    best = None
    for h in g.subjects(TAB.coversColumn, c):
        if len(list(g.objects(h, TAB.coversColumn))) == 1:
            best = _text(g, g.value(h, TAB.hasLabel))
    return best


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


def row_label(g, t, r):
    """A row's identity: the text of its entry in the first stub column, else the URI tail."""
    stubs = _stub_cols(g, t)
    for sc in stubs:
        for e in g.subjects(TAB.atRow, r):
            if (t, TAB.hasCell, e) in g and g.value(e, TAB.atColumn) == sc:
                return _text(g, e)
    return str(r).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def grid_values(g, t):
    """{(row_label, col_leaf_label): cell_text} for every entry cell of table t."""
    out = {}
    for e in g.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow); c = g.value(e, TAB.atColumn)
        if r is None or c is None:
            continue
        out[(row_label(g, t, r), col_leaf_label(g, c))] = _text(g, e)
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_recipe.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/recipe.py tests/etkl/test_recipe.py
git commit -m "feat(etkl): reshape recipe model + grid extraction (Loop A1 core)"
```

---

### Task 3: Round-trip reproduction oracle (`oracle.py`)

**Files:**
- Create: `src/iladub/etkl/oracle.py`
- Test: `tests/etkl/test_oracle.py`

**Interfaces:**
- Consumes: `Recipe`, `UnpivotOp`, `StripAggregationOp` from `recipe.py`; a *base* as `list[dict]` where each dict maps dimension/stub names → value strings plus a `"__measure__"` float.
- Produces:
  - `@dataclass(frozen=True) OracleVerdict(ok: bool, residue: tuple)` — `residue` is a tuple of human-readable mismatch descriptors (empty iff `ok`).
  - `replay(base: list[dict], recipe: Recipe) -> dict[tuple[str, str], str]` — forward-apply the recipe to regenerate `{(row_label, col_leaf_label): text}`.
  - `round_trip(original: dict, base: list[dict], recipe: Recipe) -> OracleVerdict` — replay then exact-compare against `original` (from `grid_values`).
  - Float tolerance identical to `denormalization._close`.

- [ ] **Step 1: Write the failing test** (lifts the validated prototype)

```python
# tests/etkl/test_oracle.py
from iladub.etkl.recipe import UnpivotOp, StripAggregationOp, Recipe
from iladub.etkl.oracle import replay, round_trip

BASE = [{"Year": "2020", "Region": "North", "__measure__": 10.0},
        {"Year": "2020", "Region": "South", "__measure__": 20.0},
        {"Year": "2021", "Region": "North", "__measure__": 11.0},
        {"Year": "2021", "Region": "South", "__measure__": 21.0}]

ORIGINAL = {("2020", "North"): "10", ("2020", "South"): "20",
            ("2021", "North"): "11", ("2021", "South"): "21",
            ("2020", "Year"): "2020", ("2021", "Year"): "2021"}


def test_replay_unpivot_regenerates_grid():
    grid = replay(BASE, Recipe((UnpivotOp("Region", "Year"),)))
    assert grid[("2020", "North")] == "10"
    assert grid[("2021", "South")] == "21"
    assert grid[("2020", "Year")] == "2020"


def test_correct_recipe_round_trips():
    v = round_trip(ORIGINAL, BASE, Recipe((UnpivotOp("Region", "Year"),)))
    assert v.ok and v.residue == ()


def test_corrupted_base_is_rejected():
    bad = [dict(x) for x in BASE]; bad[0]["__measure__"] = 999.0
    v = round_trip(ORIGINAL, bad, Recipe((UnpivotOp("Region", "Year"),)))
    assert not v.ok and v.residue                          # mismatch surfaces as residue


def test_strip_replay_readds_total_column():
    # base with a strip op: forward replay must re-add the Total column = sum(North,South)
    original = dict(ORIGINAL)
    original[("2020", "Total")] = "30"; original[("2021", "Total")] = "32"
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    v = round_trip(original, BASE, recipe)
    assert v.ok, v.residue
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_oracle.py -v`
Expected: FAIL (`No module named 'iladub.etkl.oracle'`).

- [ ] **Step 3: Implement `src/iladub/etkl/oracle.py`**

```python
"""oracle — the round-trip reproduction oracle (Loop A1 core).

A recipe is certified iff replaying it FORWARD over the flat base regenerates the
original grid cell values exactly. This is the anti-overfit gate: a recovered
operation that does not reproduce the report is residue, never an assertion.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .recipe import UnpivotOp, StripAggregationOp

_TOL = 1e-6
_FUNCS = {
    "sum": sum,
    "mean": lambda xs: sum(xs) / len(xs),
    "min": min,
    "max": max,
    "count": lambda xs: float(len(xs)),
    "product": math.prod,
}


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


def _fmt(x):
    """Render a computed float the way source cells read: integral floats without '.0'."""
    return str(int(round(x))) if abs(x - round(x)) <= _TOL else repr(x)


@dataclass(frozen=True)
class OracleVerdict:
    ok: bool
    residue: tuple


def replay(base, recipe):
    """Forward-apply the recipe → {(row_label, col_leaf_label): text}."""
    grid = {}
    unpivots = [op for op in recipe.operations if isinstance(op, UnpivotOp)]
    strips = [op for op in recipe.operations if isinstance(op, StripAggregationOp)]
    # 1. unpivot: place each base row's measure into the (stub_value, dimension_value) cell,
    #    and echo the stub column (col label == stub name).
    for op in unpivots:
        for row in base:
            key = row.get(op.stub)
            dim = row.get(op.dimension)
            if key is None or dim is None:
                continue
            grid[(key, dim)] = _fmt(row["__measure__"])
            grid[(key, op.stub)] = key
    # 2. strip-inverse: re-add each aggregate row/column from its members.
    #    numeric grid view keyed by (row_label, col_label).
    def numeric():
        return {k: v for k, v in grid.items() if _isnum(v)}
    for op in strips:
        num = numeric()
        f = _FUNCS[op.function]
        if op.axis == "column":
            rows = sorted({r for (r, _c) in num})
            for r in rows:
                operands = [float(num[(r, m)]) for m in op.member_labels if (r, m) in num]
                if operands:
                    grid[(r, op.target_label)] = _fmt(f(operands))
        else:  # row aggregate
            cols = sorted({c for (_r, c) in num})
            for c in cols:
                operands = [float(num[(m, c)]) for m in op.member_labels if (m, c) in num]
                if operands:
                    grid[(op.target_label, c)] = _fmt(f(operands))
    return grid


def _isnum(s):
    try:
        float(s); return True
    except (TypeError, ValueError):
        return False


def round_trip(original, base, recipe):
    """Replay then exact-compare against `original` (from grid_values). Numeric cells
    compare with tolerance; text cells compare literally."""
    repro = replay(base, recipe)
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

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_oracle.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/oracle.py tests/etkl/test_oracle.py
git commit -m "feat(etkl): round-trip reproduction oracle (Loop A1 core)"
```

---

### Task 4: Recover the recipe from a compiled table (`reshape.py` — recovery adapter)

**Files:**
- Create: `src/iladub/etkl/reshape.py`
- Test: `tests/etkl/test_reshape_recover.py`

**Interfaces:**
- Consumes: `denormalization.recover_dimensions(g, t)` → `[PivotedDimension(axis, level, name, values)]`; `denormalization.detect_aggregations(g, t)` → `AggregationEvidence(agg_rows, agg_cols, base_rows, base_cols, funcs, operands)`; `recipe.col_leaf_label`, `recipe.row_label`, `recipe.grid_values`.
- Produces:
  - `recover_recipe(g, t) -> Recipe` — build the ordered recipe: one `UnpivotOp` per named column pivot dimension (dimension = its name, stub = the first stub column's level-0 label), then one `StripAggregationOp` per aggregation column and row (function from `ev.funcs`, member_labels from the base rows/cols' leaf labels, target_label from the aggregate's own leaf label).
  - `recover_base(g, t, recipe) -> list[dict]` — the flat base rows as dicts keyed by each unpivot's `dimension` + `stub`, plus `"__measure__"`. One base row per (base data row × pivoted measure column), excluding aggregation rows/cols. (This is the data `emit_base_facts` produced, in oracle-ready form.)

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_reshape_recover.py
import pytest
from rdflib import RDF, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


def test_recover_recipe_and_base_region(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.recipe import UnpivotOp
    from iladub.etkl.reshape import recover_recipe, recover_base
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    recipe = recover_recipe(rep.graph, t)
    unpivots = [o for o in recipe.operations if isinstance(o, UnpivotOp)]
    assert any(o.dimension == "Region" and o.stub == "Year" for o in unpivots)
    base = recover_base(rep.graph, t, recipe)
    assert len(base) == 8                                  # 2 years x 4 regions
    measures = sorted(row["__measure__"] for row in base)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    north_2020 = next(r for r in base if r["Region"] == "North" and r["Year"] == "2020")
    assert north_2020["__measure__"] == 10


def test_recover_strip_ops_from_totals(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import totals_table_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.recipe import StripAggregationOp
    from iladub.etkl.reshape import recover_recipe
    p = tmp_path / "t.pdf"; totals_table_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.RecordTable))
    recipe = recover_recipe(rep.graph, t)
    strips = [o for o in recipe.operations if isinstance(o, StripAggregationOp)]
    assert strips and any(o.function == "sum" for o in strips)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_reshape_recover.py -v`
Expected: FAIL (`No module named 'iladub.etkl.reshape'`).

- [ ] **Step 3: Implement `src/iladub/etkl/reshape.py`** (recovery adapter portion)

```python
"""reshape — recover a reshape recipe from a compiled table and replay-verify it (Loop A1 core).

Recovery reuses Loop 8a's procedural search (recover_dimensions / detect_aggregations) —
the legitimately-algorithmic part — but its output is a declarative Recipe that the
round-trip oracle must certify before any NormalizedBase projection is emitted.
"""
from __future__ import annotations

from rdflib import RDF, Namespace

from . import denormalization as dn
from .recipe import (UnpivotOp, StripAggregationOp, Recipe,
                     col_leaf_label, row_label, grid_values)

TAB = Namespace("https://w3id.org/iladub/tab#")


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_reshape_recover.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/reshape.py tests/etkl/test_reshape_recover.py
git commit -m "feat(etkl): recover reshape recipe + flat base from a compiled table (Loop A1 core)"
```

---

### Task 5: Oracle-gate the recipe + emit the derived `NormalizedBase` projection

**Files:**
- Modify: `src/iladub/etkl/reshape.py` (add `certify` and `emit_normalized_base`)
- Test: `tests/etkl/test_reshape_certify.py`

**Interfaces:**
- Consumes: `recover_recipe`, `recover_base`, `grid_values` (this module); `oracle.round_trip`; the vocab terms from Task 1.
- Produces:
  - `certify(g, t) -> tuple[Recipe, OracleVerdict, list[dict]]` — recover recipe + base, run the round-trip oracle against `grid_values(g, t)`.
  - `emit_normalized_base(g, t) -> URIRef | None` — if the oracle passes, add a `tab:NormalizedBase` (typed `hproj:Projection` via the align module at reasoning time; the instance carries `tab:derivedByRecipe` + `prov:wasDerivedFrom t`), materialize the recipe operations as RDF (`tab:ReshapeRecipe`/`tab:hasOperation`/typed ops with `tab:opIndex`/params), and emit one `tab:BaseFact` per base row (reusing `tab:measureValue`/`tab:atDimensionValue`/`tab:dimensionName`/`tab:value`) linked by `tab:hasBaseFact`. If the oracle FAILS, add nothing and return `None` (residue escalates — see Task 6).

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_reshape_certify.py
import pytest
from rdflib import RDF, Namespace, URIRef
TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def test_certify_region_pivot_passes(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.reshape import certify
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    recipe, verdict, base = certify(rep.graph, t)
    assert verdict.ok, verdict.residue
    assert len(base) == 8


def test_emit_normalized_base_is_derived_projection(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.reshape import emit_normalized_base
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p)); g = rep.graph
    t = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    nb = emit_normalized_base(g, t)
    assert nb is not None
    assert (nb, RDF.type, TAB.NormalizedBase) in g
    assert (nb, PROV.wasDerivedFrom, t) in g               # derivation, not stored ground truth
    assert g.value(nb, TAB.derivedByRecipe) is not None
    facts = list(g.objects(nb, TAB.hasBaseFact))
    assert len(facts) == 8
    measures = sorted(float(g.value(f, TAB.measureValue)) for f in facts)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    # coordinates preserved (supersedes emit_base_facts behaviour)
    f0 = next(f for f in facts if float(g.value(f, TAB.measureValue)) == 10.0)
    coords = {(str(g.value(co, TAB.dimensionName)), str(g.value(co, TAB.value)))
              for co in g.objects(f0, TAB.atDimensionValue)}
    assert ("Region", "North") in coords and ("Year", "2020") in coords


def test_emit_returns_none_on_oracle_failure(tmp_path):
    """If recovery is corrupted so the recipe cannot reproduce the grid, nothing is
    asserted (residue escalates instead)."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl import reshape
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p)); g = rep.graph
    t = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    # monkeypatch recover_base to drop a fact → replay can't reproduce that cell
    orig = reshape.recover_base
    reshape.recover_base = lambda gg, tt, rr: orig(gg, tt, rr)[:-1]
    try:
        nb = reshape.emit_normalized_base(g, t)
    finally:
        reshape.recover_base = orig
    assert nb is None
    assert (None, RDF.type, TAB.NormalizedBase) not in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_reshape_certify.py -v`
Expected: FAIL (`certify`/`emit_normalized_base` undefined).

- [ ] **Step 3: Extend `src/iladub/etkl/reshape.py`**

Add these imports at the top (merge with existing):

```python
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import XSD

from .oracle import round_trip

PROV = Namespace("http://www.w3.org/ns/prov#")
```

Append:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_reshape_certify.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/reshape.py tests/etkl/test_reshape_certify.py
git commit -m "feat(etkl): oracle-gate recipe + emit derived NormalizedBase projection (Loop A1 core)"
```

---

### Task 6: Integrate into `analyze()` — recipe/oracle/projection alongside 8a evidence, residue escalation

**Files:**
- Modify: `src/iladub/etkl/denormalization.py` (extend `DenormalizationReport` + `analyze`)
- Test: `tests/etkl/test_denorm_integration.py`

**Interfaces:**
- Consumes: `reshape.certify`, `reshape.emit_normalized_base`.
- Produces: `DenormalizationReport` gains three fields — `recipe`, `oracle_ok: bool`, `residue: tuple`, `normalized_base` (uri or None). `analyze()` still recovers/annotates dimensions + aggregations in place (8a behaviour, tests depend on it), THEN certifies + emits the derived projection when the oracle passes; when it fails, it leaves `oracle_ok=False`, `residue=<descriptors>`, `normalized_base=None`, and asserts no base facts (in-band escalation — the caller sees the residue).

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_denorm_integration.py
import pytest
from rdflib import RDF, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


def test_analyze_yields_certified_recipe_and_projection(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import analyze
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    dr = analyze(rep)
    assert dr.oracle_ok and dr.residue == ()
    assert dr.normalized_base is not None
    assert (dr.normalized_base, RDF.type, TAB.NormalizedBase) in rep.graph
    # 8a behaviour preserved
    assert any(d.name == "Region" for d in dr.dimensions)
    assert len(dr.base_facts) == 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_denorm_integration.py -v`
Expected: FAIL (`DenormalizationReport` has no `oracle_ok`).

- [ ] **Step 3: Edit `src/iladub/etkl/denormalization.py`**

Replace the `DenormalizationReport` dataclass and `analyze` function (lines 306-327) with:

```python
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
```

- [ ] **Step 4: Run the FULL denormalization suite (supersession check)**

Run: `.venv/bin/pytest tests/etkl/test_denormalization.py tests/etkl/test_denorm_integration.py tests/test_tab.py -v`
Expected: PASS. Note: `test_analyze_end_to_end` in `test_denormalization.py` asserts `len(dr.base_facts) == 8` and a `PivotedDimension` was annotated — both still hold (base facts now come from the certified projection; annotation unchanged). If `test_emit_base_facts_*` call `emit_base_facts` directly, that function is retained unchanged.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/test_denorm_integration.py
git commit -m "feat(etkl): analyze() certifies recipe + emits derived projection; residue escalates (Loop A1 core)"
```

---

### Task 7: Showcase — Part I recast to recipe + oracle + derived projection

**Files:**
- Modify: `demo/etkl_1a_showcase.ipynb` (Part I cells)
- Test: manual re-run to 0 errors (notebook is not in the pytest suite)

**Interfaces:**
- Consumes: `denormalization.analyze` (now returns `recipe`, `oracle_ok`, `residue`, `normalized_base`).

- [ ] **Step 1: Read the current Part I cells**

Run: `.venv/bin/jupyter nbconvert --to script --stdout demo/etkl_1a_showcase.ipynb | sed -n '/Part I/,/ladder/p'` (or open the notebook) to find the Part I readout cell that calls `analyze` and prints base facts.

- [ ] **Step 2: Rewrite the Part I readout cell**

The cell must (a) still render the original denormalized PDF first (existing `dn_pdf` render cell is unchanged — keep leading with the rendered original PDF), (b) print the recovered **recipe** (the ordered operations), (c) print the **oracle verdict** (round-trips: True), and (d) print the derived base facts from `dr.normalized_base`. Replace the readout cell source with:

```python
from iladub.etkl.denormalization import analyze
from iladub.etkl.holon import TAB
rep = compile_tables(dn_pdf)
dr = analyze(rep)

print("RECOVERED RECIPE (inverse report-authoring operations):")
for op in dr.recipe.operations:
    print("   ", type(op).__name__, vars(op))
print()
print(f"ROUND-TRIP ORACLE — the recipe replayed forward reproduces the report exactly: {dr.oracle_ok}")
if dr.residue:
    print("   residue (escalated, not asserted):", dr.residue)
print()
print(f"DERIVED NORMALIZED BASE ({dr.normalized_base}) — a projection, not stored ground truth:")
for f in sorted(dr.base_facts, key=lambda f: float(rep.graph.value(f, TAB.measureValue))):
    coords = {str(rep.graph.value(co, TAB.dimensionName)): str(rep.graph.value(co, TAB.value))
              for co in rep.graph.objects(f, TAB.atDimensionValue)}
    m = float(rep.graph.value(f, TAB.measureValue))
    print(f"    (Year={coords.get('Year')}, Region={coords.get('Region')}) = {m:g}")
print()
print("The report is a DERIVABLE VIEW: the recipe is the transformation that built it, certified by")
print("exact reconstruction; the base facts are a derived projection (tab:NormalizedBase ⊑ hproj:Projection).")
```

- [ ] **Step 3: Update the Part I intro markdown**

Adjust the Part I intro prose to name the mechanism: "ET(K)L recovers the *recipe* — the ordered inverse of the pivot + aggregation operations a human applied — and **certifies it by round-trip reproduction**: replayed forward, the recipe regenerates the report exactly, or it is rejected as residue. The flat base is a *derived projection* of the table-holon, never stored ground truth." Keep the closing "ladder and invariant" markdown, adding one clause: "...and now inverted to a **certified recipe** whose base facts are a derived projection."

- [ ] **Step 4: Re-run the whole notebook to 0 errors**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace demo/etkl_1a_showcase.ipynb --ExecutePreprocessor.timeout=300`
Expected: exit 0, no cell errors.

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_1a_showcase.ipynb
git commit -m "docs(demo): showcase Part I — certified reshape recipe + round-trip oracle + derived projection (Loop A1 core)"
```

---

## Self-Review

**1. Spec coverage (design §3, §4, §6 A1.1/A1.2, §7, §9):**
- Consumed-standards stack — FnO/F&O function IRIs (Task 1 `tab-fno-align.ttl`), exact-arithmetic verify (reused `verify_group`), derived `hproj:Projection` (Task 1 `tab-hga-align.ttl`, Task 5). ✓
- Owned artifacts — thin recipe vocabulary (Task 1), projection-derivation via `tab:derivedByRecipe` + `prov:wasDerivedFrom` (Task 5). ✓
- Three-tier disposition — ASSERT (deterministic recovery), the oracle gate, and ESCALATE (Task 5 `emit` returns None on failure; Task 6 residue in the report). PROMOTE (GenAI) is out of scope for A1 by design. ✓
- A1.1 STRIP + A1.2 UNPIVOT with round-trip oracle (Tasks 3-5). ✓ A1.3/A1.4/A1.5 explicitly deferred. ✓
- Round-trip oracle as first-class test (Tasks 3, 5) + negative/escalation test (Task 5 `test_emit_returns_none_on_oracle_failure`). ✓
- Supersede 8a keeping tests green (Task 6 runs the full suite). ✓
- Showcase leads with rendered original PDF, re-run to 0 errors (Task 7). ✓
- Source-ownership CI (Task 1 Step 6). ✓

**2. Placeholder scan:** No TBD/TODO; every code step shows complete code; commands have expected output. ✓

**3. Type consistency:** `UnpivotOp(dimension, stub, axis)` / `StripAggregationOp(axis, function, member_labels, target_label)` / `Recipe(operations)` used identically in Tasks 2-6. `grid_values → dict[(str,str),str]`, `round_trip → OracleVerdict(ok, residue)`, `certify → (Recipe, OracleVerdict, list[dict])`, `emit_normalized_base → URIRef|None` consistent across tasks. Base dict shape `{dim: str, stub: str, "__measure__": float}` consistent between `recover_base` (Task 4) and `replay` (Task 3). ✓

**Note on an accepted risk:** `_stub_col_names` / `row_label` assume the stub column carries the row key at header level 0 — true for the pivoted fixtures 8a targets. A table with no stub column yields `stub=None` (base rows still keyed by dimension); the oracle then compares only measure/echo cells, which is correct. If a real fixture needs a multi-stub key, that surfaces as oracle residue (honest failure), not a silent wrong — and becomes a follow-on inner loop.
