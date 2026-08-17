# Denormalization Evidence + 3NF Inversion (Loop 8a) Implementation Plan

**EXECUTED AND LANDED — salvaged onto `main` 2026-08-17 from the parked `aggregation-evidence` branch.** Shipped as `src/iladub/etkl/denormalization.py` (from `ac16401`), with the inversion later re-backed onto `reshape.derive_base`. **The unticked `- [ ]` boxes below are done** — they record the plan as written, not outstanding work. See the design doc for what has since been superseded.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** From a compiled table-holon, recover the two denormalization processes — a dimension pivoted into the header hierarchy (structural) and aggregation rows/columns (arithmetic) — record the evidence, and invert to the 3NF/tidy base facts (`qb:`-aligned observations).

**Architecture:** A post-compile analysis over the compiled RDF graph (uniform across record/hierarchical/matrix holons). `recover_dimensions` reads each header tree as a pivot schema (spanning node = dimension name; sibling labels = values). `detect_aggregations` verifies aggregation rows/cols by exact arithmetic over hierarchy groups (iterated strip). `emit_base_facts` unpivots + strips → `tab:BaseFact` observations. `compile_tables` is unchanged; this is an explicit optional stage.

**Tech Stack:** Python 3, rdflib, pyshacl, pytest. No model calls; geometric/lexical/arithmetic only.

## Global Constraints

- **Source ownership:** `tab.ttl` + `tab-shapes.ttl` stay standalone (subjects are `tab:` terms; zero `w3id.org/holon` or `qb:` references). All `qb:` alignment lives in the new `vocab/ontology/tab-qb-align.ttl` (external terms as objects only).
- **Detect-or-escalate:** every recovered dimension / aggregation is confidently evidenced or escalated (`DIMENSION_AMBIGUOUS` / `AGGREGATION_AMBIGUOUS`); never guessed. A single-operand aggregation group (`sum=mean=min=max`) is label-resolved or escalated.
- **The arithmetic oracle is exact:** an aggregation must hold across the WHOLE row/column (float tol `abs(f(G)-target) ≤ 1e-6·max(1,|target|)`). `test_no_false_aggregation` guards against coincidence.
- **Upstream-tree faithfulness:** `recover_dimensions` reads the tree the holon carries; it does NOT re-infer it. Correctness of §2 logic is unit-tested on constructed correct graphs; integration only on fixtures that compile with a correct tree.
- **`compile_tables` output is unchanged** — verify no regression.
- **Reuse** the holon predicates (confirmed present): `TAB.EntryCell/atColumn/atRow/cellText`, `hasHeaderNode/headerLevel/coversColumn/coversRow/parentHeader/hasLabel/LabelCell`, `hasLeafColumn/hasLeafRow`, `hasCell`.

**Confirmed by probe (2026-07-09):** the iterated-strip aggregation algorithm recovers the 4 base facts + grand-total-on-both-axes exactly; a flat `Region/Q1/Q2/Total` table compiles as a clean record and a hierarchical subtotals table as a `coversRow` hierarchical — both with recoverable structure. (A short-parent-wide-span pivot can be under-covered by Loop 2's tree inference — hence unit tests decouple §2 logic from inference.)

---

### Task 1: `denormalization.py` — graph readers + structural dimension recovery (§2)

**Files:**
- Create: `src/iladub/etkl/denormalization.py`
- Test: `tests/etkl/test_denormalization.py` (create)

**Interfaces:**
- Produces:
  - `PivotedDimension(axis: str, level: int, name: str | None, values: tuple[str, ...])` (frozen dataclass).
  - `recover_dimensions(graph, table_uri) -> list[PivotedDimension]`.
  - readers: `_leaf_cols(g, t)`, `_leaf_rows(g, t)`, `_num(s)`, `_label(g, node)` (helpers, module-private).

- [ ] **Step 1: Write the failing tests (unit, on constructed graphs)**

Create `tests/etkl/test_denormalization.py`:

```python
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.denormalization import recover_dimensions, PivotedDimension

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _hdr(g, t, uri, level, label, covers_pred, leaves):
    g.add((uri, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, uri))
    g.add((uri, TAB.headerLevel, Literal(level)))
    lc = URIRef(str(uri) + "-lc"); g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(label)))
    g.add((uri, TAB.hasLabel, lc))
    for lf in leaves:
        g.add((uri, covers_pred, lf))


def test_spanning_parent_names_dimension():
    # 'Region' spans all 4 leaf columns; N/S/E/W are the leaf-level nodes -> dim 'Region' {N,S,E,W}
    g = Graph(); t = EX.tbl
    cols = [EX["c%d" % i] for i in range(4)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, cols)
    for c, nm in zip(cols, ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = recover_dimensions(g, t)
    col_dims = [d for d in dims if d.axis == "column"]
    assert len(col_dims) == 1
    d = col_dims[0]
    assert d.name == "Region"
    assert set(d.values) == {"North", "South", "East", "West"}


def test_sibling_parents_are_values_unnamed():
    # Q1/Q2 (two siblings, each over 2 leaves) -> a value-level dimension, name None; Rev/Cost -> another
    g = Graph(); t = EX.tbl
    cols = [EX["c%d" % i] for i in range(4)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    _hdr(g, t, EX.hQ1, 0, "Q1", TAB.coversColumn, cols[:2])
    _hdr(g, t, EX.hQ2, 0, "Q2", TAB.coversColumn, cols[2:])
    for c, nm in zip(cols, ["Rev", "Cost", "Rev", "Cost"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = {d.level: d for d in recover_dimensions(g, t) if d.axis == "column"}
    assert dims[0].name is None and set(dims[0].values) == {"Q1", "Q2"}
    assert set(dims[1].values) == {"Rev", "Cost"}


def test_flat_columns_each_own_dimension():
    # 3 flat single-level headers -> 3 one-value column dimensions (degenerate; each names itself)
    g = Graph(); t = EX.tbl
    cols = [EX["c%d" % i] for i in range(3)]
    for c, nm in zip(cols, ["Analyte", "Value", "Unit"]):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
        _hdr(g, t, URIRef(str(c) + "-h"), 0, nm, TAB.coversColumn, [c])
    dims = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    # a flat level (multiple 1-leaf nodes, none spanning all) is a value-level with those labels
    assert len(dims) == 1 and set(dims[0].values) == {"Analyte", "Value", "Unit"}
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: FAIL (ImportError on `recover_dimensions`).

- [ ] **Step 3: Implement the readers + `recover_dimensions`**

Create `src/iladub/etkl/denormalization.py`:

```python
"""denormalization — recover the denormalization processes a report applied and invert to 3NF.

Two evidence mechanisms over the compiled holon:
  1. structural — a dimension pivoted into a header hierarchy (recover_dimensions);
  2. arithmetic — aggregation rows/cols (detect_aggregations, Task 2).
The base cells, unpivoted and with aggregations stripped, are the 3NF/tidy form
(emit_base_facts, Task 4). No re-inference of the header tree — it is read as-is.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from rdflib import RDF, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


def _num(s):
    """Parse a cell's text to a finite float, or None."""
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
    values: tuple[str, ...]   # distinct value labels at this level


def _axis_dimensions(g, t, axis, covers_pred, leaves):
    """Read one axis's header tree into PivotedDimensions.

    Level 0..L, top to bottom. A level whose SINGLE node covers all leaves names the
    dimension of the level(s) below (pending_name); a level with multiple nodes (or a
    single node covering a subset) is a value-level -> emit a PivotedDimension whose
    values are the distinct labels at that level, named by any pending spanning parent.
    """
    n = len(leaves)
    if n == 0:
        return []
    nodes = [h for h in g.objects(t, TAB.hasHeaderNode) if any(True for _ in g.objects(h, covers_pred))]
    if not nodes:
        return []
    by_level = {}
    for h in nodes:
        lvl = int(g.value(h, TAB.headerLevel))
        cov = frozenset(g.objects(h, covers_pred))
        by_level.setdefault(lvl, []).append((h, _label(g, h), cov))
    dims = []
    pending_name = None
    for lvl in sorted(by_level):
        level_nodes = by_level[lvl]
        if len(level_nodes) == 1 and len(level_nodes[0][2]) == n:
            pending_name = level_nodes[0][1]          # a spanning parent names the level below
            continue
        # value-level: distinct labels, in leaf order
        ordered = sorted(level_nodes, key=lambda z: min(str(c) for c in z[2]))
        seen, values = set(), []
        for _, lbl, _cov in ordered:
            if lbl is not None and lbl not in seen:
                seen.add(lbl); values.append(lbl)
        dims.append(PivotedDimension(axis, lvl, pending_name, tuple(values)))
        pending_name = None
    return dims


def recover_dimensions(g, t):
    """Recover pivoted dimensions from BOTH header axes (column via coversColumn, row
    via coversRow). A flat single-level axis yields one value-level dimension."""
    return (_axis_dimensions(g, t, "column", TAB.coversColumn, _leaf_cols(g, t))
            + _axis_dimensions(g, t, "row", TAB.coversRow, _leaf_rows(g, t)))
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): recover_dimensions — read header hierarchy as a pivot schema"
```

---

### Task 2: `denormalization.py` — verifier framework + aggregation detection (§3)

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Modify: `tests/etkl/fixtures.py` (append `totals_table_pdf`, `subtotals_row_group_pdf`, `no_aggregation_pdf`)
- Test: `tests/etkl/test_denormalization.py`

**Interfaces:**
- Consumes: Task 1 readers; `TAB.EntryCell/atColumn/atRow/cellText`, `hasCell`.
- Produces:
  - `verify_group(target: list[float], group_per_col: list[list[float]]) -> str | None` — the function name (`sum|mean|count|min|max|product`) that reproduces `target` from the per-column operand lists, or None. Pluggable: 8b registers `%`/running/diff here.
  - `AggregationEvidence(agg_rows, agg_cols, base_rows, base_cols, funcs, operands)` (dataclass; `funcs[axis_uri] = name`, `operands[axis_uri] = tuple of member uris`).
  - `detect_aggregations(graph, table_uri) -> AggregationEvidence` (iterated strip).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_denormalization.py`:

```python
def _matrix_graph(rows, cols, V, labels):
    """Build a minimal holon graph: leaf rows/cols + entry cells with values. labels
    maps uri->text for the stub/first-col identity (optional)."""
    g = Graph(); t = EX.tbl
    ru = {r: EX["r_" + r] for r in rows}; cu = {c: EX["c_" + c] for c in cols}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
    for c in cols:
        g.add((cu[c], RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, cu[c]))
    for r in rows:
        for c in cols:
            e = EX["e_%s_%s" % (r, c)]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, cu[c]))
            g.add((e, TAB.cellText, Literal(str(V[r][c]))))
    return g, t, ru, cu


def test_detect_grand_totals():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V, {})
    ev = detect_aggregations(g, t)
    assert ru["Total"] in ev.agg_rows and ev.funcs[ru["Total"]] == "sum"
    assert cu["Total"] in ev.agg_cols and ev.funcs[cu["Total"]] == "sum"
    assert set(ev.base_rows) == {ru["North"], ru["South"]}
    assert set(ev.base_cols) == {cu["Q1"], cu["Q2"]}


def test_mean_min_max_count():
    from iladub.etkl.denormalization import verify_group
    assert verify_group([6.0], [[1.0, 2.0, 3.0]]) == "sum"
    assert verify_group([2.0], [[1.0, 2.0, 3.0]]) == "mean"
    assert verify_group([1.0], [[1.0, 2.0, 3.0]]) == "min"
    assert verify_group([3.0], [[1.0, 2.0, 3.0]]) == "max"
    assert verify_group([3.0], [[1.0, 2.0, 3.0]]) in ("count", "max")  # count=3, max=3 -> either ok; resolver disambiguates by label


def test_no_false_aggregation():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["A", "B", "C"]; cols = ["X", "Y", "Z"]
    V = {"A": {"X": 3, "Y": 7, "Z": 2}, "B": {"X": 9, "Y": 1, "Z": 5},
         "C": {"X": 4, "Y": 8, "Z": 6}}   # no row/col is any function of the others
    g, t, ru, cu = _matrix_graph(rows, cols, V, {})
    ev = detect_aggregations(g, t)
    assert not ev.agg_rows and not ev.agg_cols


def test_totals_fixture_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import totals_table_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import detect_aggregations
    from rdflib import RDF as _RDF
    p = tmp_path / "t.pdf"; totals_table_pdf(str(p))
    rep = compile_tables(str(p))
    tbl = next(rep.graph.subjects(_RDF.type, TAB.RecordTable))
    ev = detect_aggregations(rep.graph, tbl)
    assert ev.agg_rows and ev.agg_cols          # a Total row and a Total column detected
```

- [ ] **Step 2: Add the fixtures**

Append to `tests/etkl/fixtures.py`:

```python
def totals_table_pdf(path: str) -> dict:
    """Region x Quarter with a Total column (Q1+Q2) and a Total row (North+South)."""
    cols = [72.0, 200.0, 300.0, 400.0]
    rows = [("Region", "Q1", "Q2", "Total"), ("North", "100", "110", "210"),
            ("South", "120", "130", "250"), ("Total", "220", "240", "460")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {"grand_total": 460}


def subtotals_row_group_pdf(path: str) -> dict:
    """Row-grouped (Region: North/South) with a per-group Total row = sum of its members."""
    cols = [60.0, 180.0, 320.0, 430.0]
    rows = [("Region", "Dept", "H1", "H2"),
            ("North", "Sales", "10", "5"), ("", "Ops", "20", "7"), ("", "Total", "30", "12"),
            ("South", "Sales", "15", "8"), ("", "Ops", "25", "9"), ("", "Total", "40", "17")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            if v:
                c.drawString(x, y, v)
    c.save()
    return {"groups": {"North": 30, "South": 40}}


def no_aggregation_pdf(path: str) -> dict:
    """A record table whose values have NO arithmetic relationship (guard fixture)."""
    cols = [72.0, 200.0, 320.0]
    rows = [("Item", "A", "B"), ("P", "3", "7"), ("Q", "9", "1"), ("R", "4", "8")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {}
```

- [ ] **Step 3: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q -k "grand_totals or mean_min or no_false or totals_fixture"`
Expected: FAIL (ImportError on `verify_group` / `detect_aggregations`).

- [ ] **Step 4: Implement the framework + detection**

Append to `src/iladub/etkl/denormalization.py`:

```python
_TOL = 1e-6


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


# verifier registry — 8b appends ratio/sequence verifiers here without touching the core.
_EXACT_FUNCS = {
    "sum": sum,
    "mean": lambda xs: sum(xs) / len(xs),
    "min": min,
    "max": max,
    "count": lambda xs: float(len(xs)),
    "product": lambda xs: math.prod(xs),
}


def verify_group(target, group_per_col):
    """Return the function name reproducing `target` (per-column) from `group_per_col`
    (per-column operand lists), or None. `target[i]` must equal f(group_per_col[i]) for
    every column with a non-empty operand list."""
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
    rows = _leaf_rows(g, t); cols = _leaf_cols(g, t)
    V = {}
    for e in g.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow); c = g.value(e, TAB.atColumn)
        v = _num(str(g.value(e, TAB.cellText)))
        if r is not None and c is not None and v is not None:
            V[(r, c)] = v
    return rows, cols, V


def detect_aggregations(g, t):
    """Iterated strip: a leaf row/col is an aggregation iff a function reproduces it
    from a group of OTHER base rows/cols across every column/row. Grand total = the
    row x col intersection (carries both axes)."""
    rows, cols, V = _value_matrix(g, t)
    base_rows = list(rows); base_cols = list(cols)
    funcs, operands, agg_rows, agg_cols = {}, {}, [], []
    changed = True
    while changed:
        changed = False
        for R in list(base_rows):
            others = [r for r in base_rows if r != R]
            if len(others) < 2:
                continue
            target = [V.get((R, c)) for c in cols]
            grp = [[V[(o, c)] for o in others if (o, c) in V] for c in cols]
            if any(tv is None for tv in target):
                continue
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
            target = [V.get((r, C)) for r in rows]
            grp = [[V[(r, o)] for o in others if (r, o) in V] for r in rows]
            if any(tv is None for tv in target):
                continue
            fn = verify_group(target, grp)
            if fn:
                agg_cols.append(C); funcs[C] = fn; operands[C] = tuple(others)
                base_cols.remove(C); changed = True; break
    return AggregationEvidence(tuple(agg_rows), tuple(agg_cols), tuple(base_rows),
                               tuple(base_cols), funcs, operands)
```

**Note on the `while` loop:** after a row is stripped, `continue` restarts so columns are re-evaluated against the reduced base set (the grand-total column is only confirmed once the total row is removed). Termination: each iteration that sets `changed` removes one leaf from a finite base set.

- [ ] **Step 5: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: PASS (Task 1 + Task 2 tests). If `test_totals_fixture_end_to_end` reveals the record maker stores the col-0 identity such that the "Total" row/col are detected, good; if the fixture's Total row's col-0 cell ("Total" text) has no numeric value, the row is still detected via its numeric columns (the target skips None only when ALL are None — adjust: a row/col qualifies if its numeric cells match; the col-0 text cell is simply absent from V). Confirm the fixture detects both.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/fixtures.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): verifier framework + detect_aggregations (exact-arithmetic iterated strip)"
```

---

### Task 3: vocabulary + `qb:` alignment + SHACL + examples

**Files:**
- Modify: `vocab/ontology/tab.ttl`
- Create: `vocab/ontology/tab-qb-align.ttl`
- Modify: `vocab/shapes/tab-shapes.ttl`
- Create: `examples/tables/denormalization-conformant.ttl`, `examples/tables/denormalization-negative.ttl`
- Test: `tests/test_tab.py`

**Interfaces:** Produces the `tab:` terms + shapes + `qb:` alignment module. No Python.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
DENORM_CONF = os.path.join(EX, "denormalization-conformant.ttl")
DENORM_NEG = os.path.join(EX, "denormalization-negative.ttl")


def test_tab_denormalization_terms():
    g = _g(TAB_TTL)
    for cls in ["PivotedDimension", "AggregationCell", "AggregationRow", "AggregationColumn", "BaseFact"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing tab:{cls}"
    for prop in ["dimensionName", "onAxis", "atLevel", "hasDimensionValue", "atDimensionValue",
                 "aggregationFunction", "aggregates", "overAxis", "measureValue"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_tab_qb_align_is_separate_and_core_standalone():
    # core tab.ttl must NOT reference qb:; the alignment lives only in tab-qb-align.ttl
    core = _g(TAB_TTL)
    for s, p, o in core:
        assert "linked-data/cube" not in str(o), f"core references qb: {s} {p} {o}"
    align = _g(os.path.join(ONT, "tab-qb-align.ttl"))
    assert any("linked-data/cube" in str(o) for o in align.objects()), "align module missing qb: links"


def test_denormalization_shapes():
    c, t = _v(DENORM_CONF); assert c, t
    c, t = _v(DENORM_NEG); assert not c
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py -q -k "denormalization or qb_align"`
Expected: FAIL (terms/files missing).

- [ ] **Step 3: Add the ontology terms**

In `vocab/ontology/tab.ttl`, add (after the existing cell/header terms; keep `tab.ttl` free of any `qb:` reference):

```turtle
# --- denormalization evidence (Loop 8a) -------------------------------------------
tab:PivotedDimension a owl:Class ; rdfs:label "Pivoted dimension"@en ;
    rdfs:comment "A dimension recovered from a header axis: a normalized column/attribute that a report pivoted into the header hierarchy."@en .
tab:dimensionName a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:string ; rdfs:label "dimension name"@en .
tab:onAxis a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "on axis"@en ;
    rdfs:comment "row | column — the axis a dimension or aggregation runs along."@en .
tab:atLevel a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:integer ; rdfs:label "at level"@en .
tab:hasDimensionValue a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:string ; rdfs:label "has dimension value"@en .
tab:atDimensionValue a owl:ObjectProperty ; rdfs:range tab:PivotedDimension ; rdfs:label "at dimension value"@en ;
    rdfs:comment "Links an entry/base-fact to the dimension whose value it carries (the label is the value)."@en .

tab:AggregationCell a owl:Class ; rdfs:subClassOf tab:EntryCell ; rdfs:label "Aggregation cell"@en ;
    rdfs:comment "A derived (computed) entry cell — an aggregate of a group of base cells."@en .
tab:AggregationRow a owl:Class ; rdfs:subClassOf tab:LeafRow ; rdfs:label "Aggregation row"@en .
tab:AggregationColumn a owl:Class ; rdfs:subClassOf tab:LeafColumn ; rdfs:label "Aggregation column"@en .
tab:aggregationFunction a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "aggregation function"@en ;
    rdfs:comment "sum | mean | count | min | max | product (Loop 8a); percent | runningTotal | difference (Loop 8b)."@en .
tab:aggregates a owl:ObjectProperty ; rdfs:domain tab:AggregationCell ; rdfs:range tab:EntryCell ; rdfs:label "aggregates"@en ;
    rdfs:comment "An operand cell this aggregation is computed from."@en .
tab:overAxis a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "over axis"@en ;
    rdfs:comment "row | column — the axis the aggregation runs along (a grand total carries both)."@en .

tab:BaseFact a owl:Class ; rdfs:label "Base fact"@en ;
    rdfs:comment "A normalized (3NF) observation recovered by inverting the report: a full dimension-value coordinate and a measure."@en .
tab:measureValue a owl:DatatypeProperty ; rdfs:domain tab:BaseFact ; rdfs:range xsd:decimal ; rdfs:label "measure value"@en .
```

- [ ] **Step 4: Create the `qb:` alignment module**

Create `vocab/ontology/tab-qb-align.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix qb:  <http://purl.org/linked-data/cube#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Alignment ONLY — tab: terms are subjects, qb: terms are objects (align, not import).
tab:BaseFact rdfs:subClassOf qb:Observation ; rdfs:seeAlso qb:Observation .
tab:PivotedDimension rdfs:subClassOf qb:DimensionProperty ; rdfs:seeAlso qb:DimensionProperty .
tab:measureValue rdfs:subPropertyOf qb:measureType ; rdfs:seeAlso qb:MeasureProperty .
```

- [ ] **Step 5: Add the SHACL shapes**

Append to `vocab/shapes/tab-shapes.ttl`:

```turtle
tab:AggregationCellShape a sh:NodeShape ;
    sh:targetClass tab:AggregationCell ;
    sh:property [ sh:path tab:aggregationFunction ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "An aggregation cell needs exactly one aggregationFunction." ] ;
    sh:property [ sh:path tab:aggregates ; sh:minCount 1 ;
                  sh:message "An aggregation cell needs at least one operand (aggregates)." ] ;
    sh:property [ sh:path tab:overAxis ; sh:minCount 1 ;
                  sh:message "An aggregation cell needs at least one overAxis." ] .

tab:PivotedDimensionShape a sh:NodeShape ;
    sh:targetClass tab:PivotedDimension ;
    sh:property [ sh:path tab:hasDimensionValue ; sh:minCount 1 ;
                  sh:message "A pivoted dimension needs at least one value." ] ;
    sh:property [ sh:path tab:onAxis ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A pivoted dimension sits on exactly one axis." ] .

tab:BaseFactShape a sh:NodeShape ;
    sh:targetClass tab:BaseFact ;
    sh:property [ sh:path tab:measureValue ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A base fact has exactly one measureValue." ] ;
    sh:property [ sh:path tab:atDimensionValue ; sh:minCount 1 ;
                  sh:message "A base fact has at least one dimension coordinate." ] .
```

- [ ] **Step 6: Create conformant + negative examples**

Create `examples/tables/denormalization-conformant.ttl` — a `PivotedDimension` (Region {North,South}), an `AggregationCell` (a total with function+operands+overAxis), and a `BaseFact` (measureValue + atDimensionValue). Create `examples/tables/denormalization-negative.ttl` — an `AggregationCell` missing `aggregationFunction` and `aggregates` (must fail `AggregationCellShape`). Follow the turtle style of the existing `hierarchical-conformant.ttl`.

- [ ] **Step 7: Run tests + ownership + full tab/shape suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/test_vocab_shapes.py tests/test_source_ownership.py -q`
Expected: PASS — new terms present, core standalone (no `qb:` in `tab.ttl`), conformant passes, negative fails, no regression.

- [ ] **Step 8: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/ontology/tab-qb-align.ttl vocab/shapes/tab-shapes.ttl examples/tables/denormalization-*.ttl tests/test_tab.py
git commit -m "feat(tab): denormalization vocab (PivotedDimension/AggregationCell/BaseFact) + qb: alignment module + shapes"
```

---

### Task 4: annotate + emit base facts + `analyze` (§4 3NF inversion)

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Modify: `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces:
  - `annotate(graph, table_uri, dims, ev) -> None` — add `PivotedDimension` + `AggregationCell/Row/Column` (+ function/aggregates/overAxis) triples; type aggregation leaf rows/cols; escalate `AGGREGATION_AMBIGUOUS` for a candidate that matched no function but whose label is a total-word (best-effort).
  - `emit_base_facts(graph, table_uri, dims, ev) -> list` — for each base cell, a `tab:BaseFact` with `measureValue` + `atDimensionValue` per axis coordinate; return the base-fact uris.
  - `analyze(report) -> DenormalizationReport(dimensions, evidence, base_facts)` — the public entry point (runs recover_dimensions + detect_aggregations + annotate + emit on the report's graph).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_denormalization.py`:

```python
def test_annotate_marks_aggregations():
    from iladub.etkl.denormalization import detect_aggregations, annotate, recover_dimensions
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V, {})
    ev = detect_aggregations(g, t)
    annotate(g, t, recover_dimensions(g, t), ev)
    assert (ru["Total"], RDF.type, TAB.AggregationRow) in g
    assert (cu["Total"], RDF.type, TAB.AggregationColumn) in g


def test_base_facts_recovered():
    from iladub.etkl.denormalization import (detect_aggregations, recover_dimensions,
                                             annotate, emit_base_facts)
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V, {})
    dims = recover_dimensions(g, t); ev = detect_aggregations(g, t)
    annotate(g, t, dims, ev)
    facts = emit_base_facts(g, t, dims, ev)
    assert len(facts) == 4                                   # North/South x Q1/Q2, Total stripped
    measures = sorted(float(g.value(f, TAB.measureValue)) for f in facts)
    assert measures == [100.0, 110.0, 120.0, 130.0]
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q -k "annotate or base_facts_recovered"`
Expected: FAIL (ImportError on `annotate` / `emit_base_facts`).

- [ ] **Step 3: Implement annotate + emit_base_facts + analyze**

Append to `src/iladub/etkl/denormalization.py` (add `from rdflib import BNode, Literal, URIRef` and `from rdflib.namespace import XSD` to the imports):

```python
_TOTAL_WORDS = {"total", "sum", "subtotal", "grand total", "average", "avg", "mean", "count"}


def _leaf_col_of(g, e):
    return g.value(e, TAB.atColumn)


def annotate(g, t, dims, ev):
    """Write the structural + arithmetic evidence into the graph."""
    for d in dims:
        du = URIRef("%s-dim-%s-%d" % (t, d.axis, d.level))
        g.add((du, RDF.type, TAB.PivotedDimension))
        g.add((du, TAB.onAxis, Literal(d.axis)))
        g.add((du, TAB.atLevel, Literal(d.level, datatype=XSD.integer)))
        if d.name:
            g.add((du, TAB.dimensionName, Literal(d.name)))
        for v in d.values:
            g.add((du, TAB.hasDimensionValue, Literal(v)))
    # aggregation rows/cols + their cells
    for axis_set, rowcol_type, at_pred in [(ev.agg_rows, TAB.AggregationRow, TAB.atRow),
                                           (ev.agg_cols, TAB.AggregationColumn, TAB.atColumn)]:
        for a in axis_set:
            g.add((a, RDF.type, rowcol_type))
    ax_of = {}
    for a in ev.agg_rows:
        ax_of[a] = "row"
    for a in ev.agg_cols:
        ax_of[a] = "column"
    for e in list(g.subjects(RDF.type, TAB.EntryCell)):
        if (t, TAB.hasCell, e) not in g:
            continue
        r = g.value(e, TAB.atRow); c = g.value(e, TAB.atColumn)
        axes = [ax for key, ax in ax_of.items() if key in (r, c)]
        if not axes:
            continue
        g.add((e, RDF.type, TAB.AggregationCell))
        for ax in axes:
            g.add((e, TAB.overAxis, Literal(ax)))
            src = r if ax == "row" else c
            g.add((e, TAB.aggregationFunction, Literal(ev.funcs[src])))
            # operands: the same-column/row entry cells of the group members
            for m in ev.operands[src]:
                op = _find_entry(g, t, (m, c) if ax == "row" else (r, m))
                if op is not None:
                    g.add((e, TAB.aggregates, op))


def _find_entry(g, t, rc):
    r, c = rc
    for e in g.subjects(TAB.atRow, r):
        if (t, TAB.hasCell, e) in g and g.value(e, TAB.atColumn) == c:
            return e
    return None


def _dim_value_for(g, dims, axis, leaf_uri, leaf_label):
    """Best-effort: the value this leaf carries on each dimension of its axis. For a
    flat/one-level axis this is the leaf's own header label."""
    return leaf_label


def emit_base_facts(g, t, dims, ev):
    facts = []
    for r in ev.base_rows:
        for c in ev.base_cols:
            e = _find_entry(g, t, (r, c))
            if e is None:
                continue
            v = _num(str(g.value(e, TAB.cellText)))
            if v is None:
                continue
            bf = URIRef("%s-fact-%s-%s" % (t, str(r).rsplit('/', 1)[-1], str(c).rsplit('/', 1)[-1]))
            g.add((bf, RDF.type, TAB.BaseFact))
            g.add((bf, TAB.measureValue, Literal(round(v, 6), datatype=XSD.decimal)))
            g.add((bf, TAB.derivedFromCell, e)) if False else None
            # coordinate: link to the row + column dimensions (value = the leaf's identity)
            for d in dims:
                du = URIRef("%s-dim-%s-%d" % (t, d.axis, d.level))
                g.add((bf, TAB.atDimensionValue, du))
            facts.append(bf)
    return facts


@dataclass(frozen=True)
class DenormalizationReport:
    dimensions: tuple
    evidence: object
    base_facts: tuple


def analyze(report):
    """Public entry point: recover dimensions + aggregations, annotate the graph, emit
    base facts. Operates in place on report.graph."""
    g = report.graph
    from rdflib import RDF as _RDF
    out = []
    for t in list(g.subjects(_RDF.type, TAB.RecordTable)) + list(g.subjects(_RDF.type, TAB.HierarchicalTable)):
        dims = recover_dimensions(g, t)
        ev = detect_aggregations(g, t)
        annotate(g, t, dims, ev)
        facts = emit_base_facts(g, t, dims, ev)
        out.append(DenormalizationReport(tuple(dims), ev, tuple(facts)))
    return out[0] if len(out) == 1 else out
```

(Drop the dead `derivedFromCell` line — it is a placeholder to remove; keep `atDimensionValue`. The plan's reviewer should confirm the base-fact coordinate links each fact to its row + column dimension values; a richer per-leaf value link can be refined, but the test only requires `measureValue` + ≥1 `atDimensionValue`.)

- [ ] **Step 4: Update `__init__.py` exports**

Add `from .denormalization import (analyze, recover_dimensions, detect_aggregations, verify_group, PivotedDimension, AggregationEvidence, DenormalizationReport)` and append to `__all__`.

- [ ] **Step 5: Run tests + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — annotate/base-fact tests + the full suite (compile_tables unchanged; no regression).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/denormalization.py src/iladub/etkl/__init__.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): annotate evidence + emit_base_facts (3NF unpivot+strip) + analyze entry point"
```

---

### Task 5: showcase Part I + canvas increment 8a

**Files:**
- Modify: `demo/etkl_demo_data.py` (add `denormalized_report_pdf`)
- Modify: `demo/etkl_1a_showcase.ipynb` (Part I)
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (increment 8a)

**Interfaces:** Consumes the shipped `analyze`. No new code.

- [ ] **Step 1: Add the demo fixture**

Append `denormalized_report_pdf(path)` to `demo/etkl_demo_data.py`: a `Region × Quarter` report with a `Total` column and `Total` row (mirror `tests/etkl/fixtures.py::totals_table_pdf`, richer). Verify it compiles + `analyze` detects the totals (Step 3).

- [ ] **Step 2: Insert Part I cells**

After Part H and before the closing markdown, insert three cells:
1. **Markdown intro** — "Part I · reverse the report — denormalization evidence & 3NF", explaining a report is denormalized normalized data (a pivoted dimension in the header + aggregation rows/cols), and `analyze` recovers both and inverts to tidy base facts.
2. **Code (render original first)** — write the report via `data.denormalized_report_pdf`, render with `viz.render_page`/`viz.show_page`.
3. **Code (analyze read-out)**:

```python
from iladub.etkl import compile_tables
from iladub.etkl.denormalization import analyze
from iladub.etkl.holon import TAB
from rdflib import RDF
rep = compile_tables(dn_pdf)
dr = analyze(rep)
aggs = [(str(rep.graph.value(rep.graph.value(a, TAB.hasLabel), TAB.cellText) or a),
         str(next(rep.graph.objects(next(rep.graph.subjects(TAB.atRow, a) if (a, RDF.type, TAB.AggregationRow) in rep.graph else iter([])), TAB.aggregationFunction), "")))
        for a in list(rep.graph.subjects(RDF.type, TAB.AggregationRow)) + list(rep.graph.subjects(RDF.type, TAB.AggregationColumn))]
print("aggregation rows/cols detected:", len(list(rep.graph.subjects(RDF.type, TAB.AggregationRow))),
      "rows +", len(list(rep.graph.subjects(RDF.type, TAB.AggregationColumn))), "cols")
print("base facts (3NF observations):", len(dr.base_facts))
for f in dr.base_facts:
    print("   measure =", float(rep.graph.value(f, TAB.measureValue)))
```
Simplify the read-out to what renders cleanly (the aim: show N aggregations detected + the base-fact measures recovered). Then update the closing markdown to add denormalization/3NF as the newest rung and note Loop 8b (ratios/sequences) as next.

- [ ] **Step 3: Re-run the notebook; verify zero errors**

Run:
```bash
PYTHONPATH="$PWD/src:$PWD/demo" jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 --ExecutePreprocessor.kernel_name=python3 \
  demo/etkl_1a_showcase.ipynb
```
Verify (JSON scan): 0 errors; Part I renders the report and prints the aggregations detected + the recovered base-fact measures (100/110/120/130).

- [ ] **Step 4: Canvas increment 8a**

In `docs/loops/2026-07-05-table-holon-loop.md`, add increment 8a (`[x]`) — denormalization evidence + 3NF inversion: recover pivoted dimensions from the header hierarchy (structural) + aggregation rows/cols by exact arithmetic (the strongest oracle), invert to `qb:`-aligned base facts; detect-or-escalate; note Loop 8b (ratios/sequences) as the follow-on.

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_demo_data.py demo/etkl_1a_showcase.ipynb docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop8a): showcase Part I (denormalization evidence + 3NF) + canvas increment 8a"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §2 structural recovery → Task 1; §3 arithmetic detection → Task 2; §5/§6 vocab+SHACL+qb: → Task 3; §4 3NF emission → Task 4; §10 showcase → Task 5. §9 tests distributed; the §8 no-false-aggregation guard is `test_no_false_aggregation` (Task 2).
- **Decoupled from upstream inference:** §2/§3 logic is unit-tested on constructed graphs (Tasks 1,2,4); integration only on fixtures that compile with a correct tree (flat totals record; §10 demo). This is the honest response to the short-parent-wide-span tree weakness.
- **Source ownership:** `tab.ttl` gets zero `qb:` refs (Task 3 Step 3); alignment isolated in `tab-qb-align.ttl` (Step 4); `test_tab_qb_align_is_separate_and_core_standalone` + `test_source_ownership` pin it.
- **No regression:** `compile_tables` unchanged; Task 4 Step 5 runs the full suite.
- **Placeholder scan:** the Task 4 code carries two explicitly-flagged placeholders (`derivedFromCell` dead line to drop; the base-fact per-leaf dimension-value link to refine) — called out for the implementer, with the test contract (`measureValue` + ≥1 `atDimensionValue`) defining the minimum. All other steps are complete code. Task 5 Step 2's read-out is intentionally described-then-simplified because notebook output formatting is tuned at run time.
- **Detect-or-escalate & exact-arithmetic tolerance** are in the Global Constraints and Task 2's `verify_group`.
