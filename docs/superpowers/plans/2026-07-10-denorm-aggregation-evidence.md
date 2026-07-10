# Denormalization ② — Aggregation Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Detect aggregation rows/columns (totals, subtotals) in a compiled holon by **exact arithmetic** over the header-defined groups, and record the evidence (`tab:AggregationCell/Row/Column` + `aggregationFunction` + `aggregates` + `overAxis`).

**Slice ② of** [Loop 8a — denormalization evidence + 3NF inversion](../specs/2026-07-09-aggregation-evidence-design.md) (§3 arithmetic, §5 vocab, §6 SHACL). Slice ① (pivoted dimensions) is merged; slice ③ (3NF/`qb:` emission) follows — it consumes both.

**Architecture:** A post-compile read over the graph. Detection is the strongest oracle in the project — real arithmetic verified across a WHOLE row/column (coincidence ~0). `compile_tables` unchanged; extends the existing `src/iladub/etkl/denormalization.py`.

## Global Constraints

- **Exact-arithmetic oracle:** an aggregation must hold across the whole row/column for a function `f ∈ {sum, mean, count, min, max, product}` over a group of ≥ 2 base members. Float tol `abs(f(G)-target) ≤ 1e-6·max(1,|target|)`. The full-row/column consistency is the safety property (`test_no_false_aggregation` guards it).
- **≥2-operand groups only:** a single-member "subtotal" is `sum=mean=min=max=the value` — indistinguishable, so it is NOT flagged (documented; a 1-row group is skipped). No function is ever guessed.
- **Source ownership:** `tab.ttl` + `tab-shapes.ttl` stay standalone (subjects are `tab:` terms; no `qb:`/`holon:`).
- **Reuse** the holon predicates: `TAB.EntryCell/atColumn/atRow/cellText`, `hasCell`, `hasLeafColumn/hasLeafRow`. Extend `denormalization.py` (do not create a new module).
- **`compile_tables` unchanged** — verify no regression.

**Confirmed by probe (2026-07-09):** the iterated-strip algorithm recovers the total row/column and marks the grand total on both axes, on the `Region × Quarter × Total` matrix.

---

### Task 1: verifier framework + `detect_aggregations`

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Modify: `tests/etkl/fixtures.py` (append `totals_table_pdf`, `subtotals_row_group_pdf`, `no_aggregation_pdf`)
- Test: `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `verify_group(target, group_per_col) -> str | None`; `AggregationEvidence(agg_rows, agg_cols, base_rows, base_cols, funcs, operands)` (frozen); `detect_aggregations(graph, table_uri) -> AggregationEvidence`; `_value_matrix`, `_num` (helpers).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_denormalization.py`:

```python
def _matrix_graph(rows, cols, V):
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


def test_verify_group_functions():
    from iladub.etkl.denormalization import verify_group
    assert verify_group([6.0], [[1.0, 2.0, 3.0]]) == "sum"
    assert verify_group([2.0], [[1.0, 2.0, 3.0]]) == "mean"
    assert verify_group([1.0], [[1.0, 2.0, 3.0]]) == "min"
    assert verify_group([100.0], [[7.0, 3.0]]) is None      # no function matches


def test_detect_grand_totals():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    assert ru["Total"] in ev.agg_rows and ev.funcs[ru["Total"]] == "sum"
    assert cu["Total"] in ev.agg_cols and ev.funcs[cu["Total"]] == "sum"
    assert set(ev.base_rows) == {ru["North"], ru["South"]}
    assert set(ev.base_cols) == {cu["Q1"], cu["Q2"]}


def test_no_false_aggregation():
    from iladub.etkl.denormalization import detect_aggregations
    rows = ["A", "B", "C"]; cols = ["X", "Y", "Z"]
    V = {"A": {"X": 3, "Y": 7, "Z": 2}, "B": {"X": 9, "Y": 1, "Z": 5},
         "C": {"X": 4, "Y": 8, "Z": 6}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
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
    assert ev.agg_rows and ev.agg_cols
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
    """Row-grouped (Region: North/South) with a per-group Total row = sum of members."""
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

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q -k "verify_group or grand_totals or no_false or totals_fixture"`
Expected: FAIL (ImportError on `verify_group` / `detect_aggregations`).

- [ ] **Step 4: Implement**

In `src/iladub/etkl/denormalization.py`, re-add the numeric parser to the top imports (it was removed as a slice-① placeholder) and append the framework + detection. Add `import math` and `import re` at the top, then:

```python
def _num(s):
    try:
        v = float(re.sub(r"[,%$]", "", s.strip()))
        return v if math.isfinite(v) else None
    except (ValueError, AttributeError):
        return None
```

Append at the end of the module:

```python
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
            target = [V.get((R, c)) for c in cols]
            if any(tv is None for tv in target):
                continue
            grp = [[V[(o, c)] for o in others if (o, c) in V] for c in cols]
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
            if any(tv is None for tv in target):
                continue
            grp = [[V[(r, o)] for o in others if (r, o) in V] for r in rows]
            fn = verify_group(target, grp)
            if fn:
                agg_cols.append(C); funcs[C] = fn; operands[C] = tuple(others)
                base_cols.remove(C); changed = True; break
    return AggregationEvidence(tuple(agg_rows), tuple(agg_cols), tuple(base_rows),
                               tuple(base_cols), funcs, operands)
```

**Termination:** each `changed` iteration removes one leaf from a finite base set; the `continue` after a row strip re-evaluates columns against the reduced base (the grand-total column is confirmed only once the total row is gone).

- [ ] **Step 5: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: PASS (slice-① tests + the new detection tests). If `test_totals_fixture_end_to_end` does not detect both, inspect: the `Total` row's col-0 cell is the text `"Total"` (no numeric value → simply absent from `V`), so the row/col are still matched on their numeric cells — confirm both are found.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/fixtures.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): verifier framework + detect_aggregations (exact-arithmetic iterated strip)"
```

---

### Task 2: vocabulary + SHACL + `annotate_aggregations` + exports

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`, `src/iladub/etkl/__init__.py`
- Modify: `vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl`
- Create: `examples/tables/aggregation-conformant.ttl`, `examples/tables/aggregation-negative.ttl`
- Test: `tests/test_tab.py`, `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `tab:AggregationCell/Row/Column`, `tab:aggregationFunction`, `tab:aggregates`, `tab:overAxis`; `tab:AggregationCellShape`; `annotate_aggregations(graph, table_uri, ev) -> None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
AGG_CONF = os.path.join(EX, "aggregation-conformant.ttl")
AGG_NEG = os.path.join(EX, "aggregation-negative.ttl")


def test_tab_aggregation_terms():
    g = _g(TAB_TTL)
    for cls in ["AggregationCell", "AggregationRow", "AggregationColumn"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing tab:{cls}"
    for prop in ["aggregationFunction", "aggregates", "overAxis"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_aggregation_shapes():
    c, t = _v(AGG_CONF); assert c, t
    c, t = _v(AGG_NEG); assert not c
```

Append to `tests/etkl/test_denormalization.py`:

```python
def test_annotate_marks_aggregations():
    from iladub.etkl.denormalization import detect_aggregations, annotate_aggregations
    rows = ["North", "South", "Total"]; cols = ["Q1", "Q2", "Total"]
    V = {"North": {"Q1": 100, "Q2": 110, "Total": 210},
         "South": {"Q1": 120, "Q2": 130, "Total": 250},
         "Total": {"Q1": 220, "Q2": 240, "Total": 460}}
    g, t, ru, cu = _matrix_graph(rows, cols, V)
    ev = detect_aggregations(g, t)
    annotate_aggregations(g, t, ev)
    assert (ru["Total"], RDF.type, TAB.AggregationRow) in g
    assert (cu["Total"], RDF.type, TAB.AggregationColumn) in g
    # the grand-total cell carries both axes
    e = next(e for e in g.subjects(RDF.type, TAB.AggregationCell)
             if g.value(e, TAB.atRow) == ru["Total"] and g.value(e, TAB.atColumn) == cu["Total"])
    assert {str(o) for o in g.objects(e, TAB.overAxis)} == {"row", "column"}
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/etkl/test_denormalization.py -q -k "aggregation or annotate_marks"`
Expected: FAIL (terms / `annotate_aggregations` missing).

- [ ] **Step 3: Add the ontology terms**

In `vocab/ontology/tab.ttl` (standalone — no `qb:`):

```turtle
tab:AggregationCell a owl:Class ; rdfs:subClassOf tab:EntryCell ; rdfs:label "Aggregation cell"@en ;
    rdfs:comment "A derived (computed) entry cell — an aggregate of a group of base cells."@en .
tab:AggregationRow a owl:Class ; rdfs:subClassOf tab:LeafRow ; rdfs:label "Aggregation row"@en .
tab:AggregationColumn a owl:Class ; rdfs:subClassOf tab:LeafColumn ; rdfs:label "Aggregation column"@en .
tab:aggregationFunction a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "aggregation function"@en ;
    rdfs:comment "sum | mean | count | min | max | product."@en .
tab:aggregates a owl:ObjectProperty ; rdfs:domain tab:AggregationCell ; rdfs:range tab:EntryCell ; rdfs:label "aggregates"@en ;
    rdfs:comment "An operand cell this aggregation is computed from."@en .
tab:overAxis a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "over axis"@en ;
    rdfs:comment "row | column — the axis the aggregation runs along (a grand total carries both)."@en .
```

- [ ] **Step 4: Add the SHACL shape**

Append to `vocab/shapes/tab-shapes.ttl`:

```turtle
tab:AggregationCellShape a sh:NodeShape ;
    sh:targetClass tab:AggregationCell ;
    sh:property [ sh:path tab:aggregationFunction ; sh:minCount 1 ;
                  sh:message "An aggregation cell needs an aggregationFunction." ] ;
    sh:property [ sh:path tab:aggregates ; sh:minCount 1 ;
                  sh:message "An aggregation cell needs at least one operand." ] ;
    sh:property [ sh:path tab:overAxis ; sh:minCount 1 ;
                  sh:message "An aggregation cell needs at least one overAxis." ] .
```

- [ ] **Step 5: Create examples**

`examples/tables/aggregation-conformant.ttl` — a `tab:AggregationCell` with `aggregationFunction "sum"`, ≥1 `aggregates` (an `EntryCell`), and `overAxis "row"`. `aggregation-negative.ttl` — an `AggregationCell` missing `aggregationFunction` + `aggregates` → fails the shape. Mirror the existing example ttls.

- [ ] **Step 6: Implement `annotate_aggregations` + exports**

Append to `src/iladub/etkl/denormalization.py`:

```python
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
```

In `src/iladub/etkl/__init__.py`, add `from .denormalization import detect_aggregations, annotate_aggregations, verify_group, AggregationEvidence` and append to `__all__`.

- [ ] **Step 7: Run tests + ownership + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/test_vocab_shapes.py tests/test_source_ownership.py tests/etkl/test_denormalization.py -q` then `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — terms present, shapes pass/fail correctly, `tab.ttl` standalone, full suite green (compile_tables unchanged).

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/denormalization.py src/iladub/etkl/__init__.py vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl examples/tables/aggregation-*.ttl tests/test_tab.py tests/etkl/test_denormalization.py
git commit -m "feat(tab): AggregationCell vocab + shape + annotate_aggregations"
```

---

## Self-Review (author checklist — completed)

- **Coverage:** verify_group + detect_aggregations (§3) → Task 1; vocab/SHACL/annotate (§5/§6) → Task 2.
- **Oracle correctness:** ≥2-operand exact arithmetic across the whole row/col; `test_no_false_aggregation` guards coincidence.
- **Source ownership:** `tab.ttl` gets zero `qb:` refs; pinned by `test_source_ownership`.
- **No regression:** `compile_tables` unchanged; Task 2 Step 7 runs the full suite.
- **Placeholder scan:** all code inline; `_num` re-added at the top (it was a slice-① cleanup removal).
