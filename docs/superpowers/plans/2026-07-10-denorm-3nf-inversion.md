# Denormalization ③ — 3NF Inversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Invert a denormalized report to its 3NF/tidy base facts: **unpivot** the header-encoded dimensions (a `Region`-over-`{N,S,E,W}` pivot → a `Region` column) and **strip** the aggregations, emitting each base cell as a `qb:`-aligned `tab:BaseFact` (dimension coordinates × measure).

**Slice ③ of** [Loop 8a](../specs/2026-07-09-aggregation-evidence-design.md) (§4 3NF). Consumes slice ① (`recover_dimensions`) and ② (`detect_aggregations`), both merged. This is the payoff — the report becomes a derivable view over recovered normalized facts.

**Architecture:** A post-compile read over the graph, extending `denormalization.py`. `compile_tables` unchanged.

## Global Constraints

- **Scope (probe-grounded):** unpivot when there is a **pivoted column dimension** (a named multi-value column dim, e.g. `Region`); its leaf columns are the **measures**, and each measure cell's column-value is that column's leaf label. A leaf column NOT under a pivoted dimension is a **stub** = a row-identity dimension (its header names it; its per-row entry is the value). Aggregation rows/cols (slice ②) are stripped. If there is no pivoted column dimension, `emit_base_facts` returns `[]` (nothing to unpivot — documented; a flat table's 3NF is itself, and row-header-tree coordinates + flat melt are follow-ups).
- **Source ownership:** `tab.ttl` + `tab-shapes.ttl` standalone; ALL `qb:` alignment in the new `vocab/ontology/tab-qb-align.ttl` (external terms as objects only).
- **Reuse** `recover_dimensions`, `detect_aggregations`, `_num`, `_leaf_cols`, `_leaf_rows` (all in `denormalization.py`); holon predicates `coversColumn`, `headerLevel`, `hasLabel`, `atRow`/`atColumn`/`cellText`, `hasCell`, `hasLeafColumn`/`hasLeafRow`.
- **`compile_tables` unchanged** — verify no regression.

**Confirmed by probe (2026-07-10):** `region_pivot` → 8 base facts `(Year=2020,Region=North)=10 … (2021,West)=41`, the Region columns melted, Year (uncovered stub) as the row dimension.

---

### Task 1: `emit_base_facts`

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Test: `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `emit_base_facts(graph, table_uri) -> list` (BaseFact uris); helpers `_col_label_at_level`, `_entry`, `_add_coordinate`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_denormalization.py`:

```python
def test_emit_base_facts_unpivots_region(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import emit_base_facts
    from rdflib import RDF as _RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(_RDF.type, TAB.HierarchicalTable))
    facts = emit_base_facts(rep.graph, t)
    assert len(facts) == 8                                   # 2 years x 4 regions (melted)
    measures = sorted(float(rep.graph.value(f, TAB.measureValue)) for f in facts)
    assert measures == [10, 11, 20, 21, 30, 31, 40, 41]
    # each fact carries a Region coordinate and a Year coordinate
    f0 = next(f for f in facts if float(rep.graph.value(f, TAB.measureValue)) == 10.0)
    coords = {(str(rep.graph.value(co, TAB.dimensionName)), str(rep.graph.value(co, TAB.value)))
              for co in rep.graph.objects(f0, TAB.atDimensionValue)}
    assert ("Region", "North") in coords and ("Year", "2020") in coords


def test_emit_base_facts_strips_aggregation_column():
    """A pivoted table with a Total aggregation column: Total is not a measure column,
    so no base fact references it."""
    from iladub.etkl.denormalization import emit_base_facts
    # constructed: column dim 'Region' over N/S (cols c1,c2) named by a spanning parent;
    # a 'Total' agg column (c3 = N+S); one stub col c0 'Year'; two rows.
    g = Graph(); t = EX.tbl
    c0, c1, c2, c3 = EX.c0, EX.c1, EX.c2, EX.c3
    for c in (c0, c1, c2, c3):
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    # header tree: Region (level 0) spans c1,c2 ; N/S leaf labels (level 1); Year stub label on c0; Total on c3
    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        lc = URIRef(str(u) + "l"); g.add((lc, RDF.type, TAB.LabelCell)); g.add((lc, TAB.cellText, Literal(lbl)))
        g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hReg, 0, "Region", [c1, c2]); hdr(EX.hN, 1, "North", [c1]); hdr(EX.hS, 1, "South", [c2])
    hdr(EX.hYear, 0, "Year", [c0]); hdr(EX.hTot, 0, "Total", [c3])
    rows = ["2020", "2021"]; ru = {r: EX["r" + r] for r in rows}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
    V = {"2020": {c0: "2020", c1: "10", c2: "20", c3: "30"},
         "2021": {c0: "2021", c1: "11", c2: "21", c3: "32"}}
    for r in rows:
        for c in (c0, c1, c2, c3):
            e = EX["e_%s_%s" % (r, str(c)[-2:])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(V[r][c])))
    facts = emit_base_facts(g, t)
    assert len(facts) == 4                                   # 2 years x 2 regions; Total NOT a measure
    # no base fact has a Region coordinate of a value derived from the Total column
    regions = {str(g.value(co, TAB.value)) for f in facts for co in g.objects(f, TAB.atDimensionValue)
               if str(g.value(co, TAB.dimensionName)) == "Region"}
    assert regions == {"North", "South"}
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q -k "emit_base_facts"`
Expected: FAIL (ImportError on `emit_base_facts`).

- [ ] **Step 3: Implement**

In `src/iladub/etkl/denormalization.py`, ensure `from rdflib import BNode` is imported (add to the existing rdflib import line — `Literal`, `URIRef`, `RDF`, `Namespace` are already imported; add `BNode`), then append:

```python
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
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: PASS (slice ①/② tests + the 2 new emit tests — 8 facts melted, Total stripped).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): emit_base_facts — unpivot the pivoted dimension + strip aggregations to 3NF"
```

---

### Task 2: `BaseFact` vocab + `qb:` alignment + SHACL + `analyze` entry point

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`, `src/iladub/etkl/__init__.py`
- Modify: `vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl`
- Create: `vocab/ontology/tab-qb-align.ttl`, `examples/tables/basefact-conformant.ttl`, `examples/tables/basefact-negative.ttl`
- Test: `tests/test_tab.py`, `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `tab:BaseFact` (+ `measureValue`, `atDimensionValue`, `value`); `tab:BaseFactShape`; `tab-qb-align.ttl`; `analyze(report) -> DenormalizationReport(dimensions, evidence, base_facts)` (public entry: recover_dimensions + detect_aggregations + annotate_dimensions + annotate_aggregations + emit_base_facts on the report's graph).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
BF_CONF = os.path.join(EX, "basefact-conformant.ttl")
BF_NEG = os.path.join(EX, "basefact-negative.ttl")


def test_tab_basefact_terms():
    g = _g(TAB_TTL)
    assert (TAB.BaseFact, RDF.type, OWL.Class) in g
    for prop in ["measureValue", "atDimensionValue", "value"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_qb_align_separate_and_core_standalone():
    core = _g(TAB_TTL)
    for _, _, o in core:
        assert "linked-data/cube" not in str(o), "core tab.ttl references qb:"
    align = _g(os.path.join(ONT, "tab-qb-align.ttl"))
    assert any("linked-data/cube" in str(o) for o in align.objects()), "align module missing qb:"


def test_basefact_shapes():
    c, t = _v(BF_CONF); assert c, t
    c, t = _v(BF_NEG); assert not c
```

Append to `tests/etkl/test_denormalization.py`:

```python
def test_analyze_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.denormalization import analyze
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    dr = analyze(rep)
    assert any(d.name == "Region" for d in dr.dimensions)
    assert len(dr.base_facts) == 8
    assert (None, RDF.type, TAB.PivotedDimension) in rep.graph   # evidence annotated in place
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/etkl/test_denormalization.py -q -k "basefact or qb_align or analyze"`
Expected: FAIL (terms/`analyze` missing).

- [ ] **Step 3: Add ontology terms (standalone, no `qb:`)**

Append to `vocab/ontology/tab.ttl`:

```turtle
tab:BaseFact a owl:Class ; rdfs:label "Base fact"@en ;
    rdfs:comment "A normalized (3NF) observation recovered by inverting a report: a dimension-value coordinate and a measure."@en .
tab:measureValue a owl:DatatypeProperty ; rdfs:domain tab:BaseFact ; rdfs:range xsd:decimal ; rdfs:label "measure value"@en .
tab:atDimensionValue a owl:ObjectProperty ; rdfs:domain tab:BaseFact ; rdfs:label "at dimension value"@en ;
    rdfs:comment "A coordinate node: a tab:dimensionName + tab:value the base fact carries."@en .
tab:value a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "value"@en .
```

- [ ] **Step 4: Create the `qb:` alignment module**

Create `vocab/ontology/tab-qb-align.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix qb:  <http://purl.org/linked-data/cube#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Alignment only — tab: subjects, qb: objects.
tab:BaseFact rdfs:subClassOf qb:Observation ; rdfs:seeAlso qb:Observation .
tab:PivotedDimension rdfs:subClassOf qb:DimensionProperty ; rdfs:seeAlso qb:DimensionProperty .
tab:measureValue rdfs:subPropertyOf qb:measureType ; rdfs:seeAlso qb:MeasureProperty .
```

- [ ] **Step 5: Add the SHACL shape + examples**

Append to `vocab/shapes/tab-shapes.ttl`:

```turtle
tab:BaseFactShape a sh:NodeShape ;
    sh:targetClass tab:BaseFact ;
    sh:property [ sh:path tab:measureValue ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A base fact has exactly one measureValue." ] ;
    sh:property [ sh:path tab:atDimensionValue ; sh:minCount 1 ;
                  sh:message "A base fact has at least one dimension coordinate." ] .
```

`examples/tables/basefact-conformant.ttl` — a `tab:BaseFact` with `measureValue` + ≥1 `atDimensionValue [ tab:dimensionName "Region" ; tab:value "North" ]`. `basefact-negative.ttl` — a `BaseFact` missing `atDimensionValue` (or `measureValue`) → fails.

- [ ] **Step 6: Implement `analyze` + exports**

Append to `src/iladub/etkl/denormalization.py`:

```python
@dataclass(frozen=True)
class DenormalizationReport:
    dimensions: tuple
    evidence: object
    base_facts: tuple


def analyze(report):
    """Public entry point: recover dimensions + aggregations, annotate the graph in place,
    and emit 3NF base facts. Returns the first table's DenormalizationReport (or a list
    for a multi-table page)."""
    g = report.graph
    out = []
    for t in (list(g.subjects(RDF.type, TAB.RecordTable))
              + list(g.subjects(RDF.type, TAB.HierarchicalTable))):
        dims = recover_dimensions(g, t)
        ev = detect_aggregations(g, t)
        annotate_dimensions(g, t, dims)
        annotate_aggregations(g, t, ev)
        facts = emit_base_facts(g, t)
        out.append(DenormalizationReport(tuple(dims), ev, tuple(facts)))
    return out[0] if len(out) == 1 else out
```

In `src/iladub/etkl/__init__.py`, add `from .denormalization import emit_base_facts, analyze, DenormalizationReport` and append to `__all__`.

- [ ] **Step 7: Run tests + ownership + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/test_vocab_shapes.py tests/test_source_ownership.py tests/etkl/test_denormalization.py -q` then `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — terms present, `tab.ttl` standalone (qb: only in the align module), shapes pass/fail, `analyze` end-to-end (Region dim + 8 base facts), full suite green.

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/denormalization.py src/iladub/etkl/__init__.py vocab/ontology/tab.ttl vocab/ontology/tab-qb-align.ttl vocab/shapes/tab-shapes.ttl examples/tables/basefact-*.ttl tests/test_tab.py tests/etkl/test_denormalization.py
git commit -m "feat(tab): BaseFact vocab + qb: alignment + BaseFactShape + analyze entry point"
```

---

### Task 3: showcase Part I + canvas increment 8a

**Files:** `demo/etkl_demo_data.py`, `demo/etkl_1a_showcase.ipynb`, `docs/loops/2026-07-05-table-holon-loop.md`.

- [ ] **Step 1:** Add `denormalized_report_pdf` to `demo/etkl_demo_data.py` mirroring `region_pivot_pdf` (a `Region`-pivoted report). Verify `analyze` recovers the Region dimension + emits base facts (Step 3).
- [ ] **Step 2:** Insert **Part I** in the notebook (after Part H): render the pivoted report first, then show `analyze` recover the `Region` **dimension** from the header hierarchy and emit the **base facts** (the tidy `(Year, Region, value)` table the report was built from). "So what": ET(K)L inverts the denormalization — the report becomes a derivable view over normalized facts, aligned to RDF Data Cube.
- [ ] **Step 3:** Re-run the notebook to 0 errors (JSON scan); verify Part I prints the Region dimension + the base-fact count/measures.
- [ ] **Step 4:** Add canvas increment 8a (`[x]`) — denormalization evidence + 3NF inversion delivered in three slices (pivoted dimensions, aggregation evidence, 3NF base facts); note Loop 8b (ratios/sequences) as the follow-on. Commit.

---

## Self-Review (author checklist — completed)

- **Coverage:** §4 unpivot+strip → Task 1; vocab/qb:/shape/analyze → Task 2; showcase → Task 3. Probe-grounded (region_pivot → 8 facts).
- **Scope honesty:** unpivot requires a pivoted column dimension (else empty); flat-melt + row-tree coordinates are documented follow-ups.
- **Source ownership:** `tab.ttl` zero `qb:`; alignment isolated in `tab-qb-align.ttl`; pinned by `test_qb_align_separate_and_core_standalone` + `test_source_ownership`.
- **No regression:** `compile_tables` unchanged; Task 2 Step 7 runs the full suite.
- **Placeholder scan:** complete code inline for `emit_base_facts`, `analyze`, vocab, shapes.
