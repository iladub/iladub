# Denormalization ① — Pivoted Dimensions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Read a compiled holon's header hierarchies as a **pivot schema** — recover the dimensions a report pivoted into the headers (a spanning parent names a dimension; sibling labels are its values) — and record them as `tab:PivotedDimension` evidence.

**Slice of** [Loop 8a — denormalization evidence + 3NF inversion](../specs/2026-07-09-aggregation-evidence-design.md) (§2 structural, §5 vocab, §6 SHACL). Slices ② aggregation evidence and ③ 3NF emission follow separately. Prerequisite (merged): the header-span `repair_coverage` fix, so a single-spanning-parent pivot compiles with a correct tree.

**Architecture:** A post-compile read over the graph. No new inference; interpret the trees Loops 2/5/6 build. `compile_tables` unchanged.

## Global Constraints

- **Reading rule (settled):** a header level whose SINGLE node spans all its leaves → a dimension NAME for the level below; a level with multiple sibling nodes → VALUES of a dimension (named by a spanning parent above, or unnamed). Each value-level = one dimension; its value set = distinct labels.
- **Faithful to the tree:** `recover_dimensions` reads the tree as-is (correctness of §2 logic unit-tested on constructed graphs; integration on fixtures that compile with a correct tree — `region_pivot` now does, via `repair_coverage`).
- **Source ownership:** `tab.ttl` + `tab-shapes.ttl` stay standalone (subjects are `tab:` terms).
- **Detect-or-escalate:** a level that is neither a clean single-spanning-name nor a clean value partition is skipped (no dimension emitted) rather than guessed.
- **Reuse** the holon predicates: `TAB.hasHeaderNode/headerLevel/coversColumn/coversRow/parentHeader/hasLabel/LabelCell/cellText`, `hasLeafColumn/hasLeafRow`.

---

### Task 1: `denormalization.py` — `recover_dimensions`

**Files:**
- Create: `src/iladub/etkl/denormalization.py`
- Modify: `tests/etkl/fixtures.py` (append `column_pivot_pdf` — a two-level column pivot for integration)
- Test: `tests/etkl/test_denormalization.py` (create)

**Interfaces:**
- Produces: `PivotedDimension(axis: str, level: int, name: str | None, values: tuple[str, ...])` (frozen); `recover_dimensions(graph, table_uri) -> list[PivotedDimension]`; helpers `_label`, `_leaf_cols`, `_leaf_rows`.

- [ ] **Step 1: Write the failing tests (unit on constructed graphs + one integration)**

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


def _cols(g, t, n):
    cols = [EX["c%d" % i] for i in range(n)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))
    return cols


def test_spanning_parent_names_dimension():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, cols)
    for c, nm in zip(cols, ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    d = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    assert len(d) == 1 and d[0].name == "Region"
    assert set(d[0].values) == {"North", "South", "East", "West"}


def test_sibling_parents_are_values_unnamed():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hQ1, 0, "Q1", TAB.coversColumn, cols[:2])
    _hdr(g, t, EX.hQ2, 0, "Q2", TAB.coversColumn, cols[2:])
    for c, nm in zip(cols, ["Rev", "Cost", "Rev", "Cost"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = {d.level: d for d in recover_dimensions(g, t) if d.axis == "column"}
    assert dims[0].name is None and set(dims[0].values) == {"Q1", "Q2"}
    assert set(dims[1].values) == {"Rev", "Cost"}


def test_flat_level_is_value_dimension():
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 3)
    for c, nm in zip(cols, ["Analyte", "Value", "Unit"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 0, nm, TAB.coversColumn, [c])
    d = [d for d in recover_dimensions(g, t) if d.axis == "column"]
    assert len(d) == 1 and set(d[0].values) == {"Analyte", "Value", "Unit"}


def test_region_pivot_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from rdflib import RDF as _RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(_RDF.type, TAB.HierarchicalTable))
    region = next(d for d in recover_dimensions(rep.graph, t) if d.name == "Region")
    assert set(region.values) == {"North", "South", "East", "West"}   # unblocked by repair_coverage
```

(`region_pivot_pdf` already exists in `tests/etkl/fixtures.py` from the 8-pre loop — no new fixture needed for the integration test. The `column_pivot_pdf` fixture in the Files list is optional; skip if `region_pivot_pdf` suffices.)

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: FAIL (ImportError on `recover_dimensions`).

- [ ] **Step 3: Implement**

Create `src/iladub/etkl/denormalization.py`:

```python
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

from rdflib import RDF, Namespace

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
        if len(level_nodes) == 1 and len(level_nodes[0][2]) == n:
            pending_name = level_nodes[0][1]          # a spanning parent names the level below
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
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_denormalization.py -q`
Expected: PASS (4 tests, including `region_pivot` end-to-end — proving the 8-pre unblock).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/test_denormalization.py
git commit -m "feat(etkl): recover_dimensions — read header hierarchy as a pivot schema"
```

---

### Task 2: vocabulary + SHACL + `annotate_dimensions` + exports

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Modify: `src/iladub/etkl/__init__.py`
- Modify: `vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl`
- Create: `examples/tables/pivoted-dimension-conformant.ttl`, `examples/tables/pivoted-dimension-negative.ttl`
- Test: `tests/test_tab.py`, `tests/etkl/test_denormalization.py`

**Interfaces:**
- Produces: `tab:PivotedDimension` (+ `dimensionName`, `onAxis`, `atLevel`, `hasDimensionValue`); `tab:PivotedDimensionShape`; `annotate_dimensions(graph, table_uri, dims) -> list` (writes the triples; returns the dimension node uris).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
PIVDIM_CONF = os.path.join(EX, "pivoted-dimension-conformant.ttl")
PIVDIM_NEG = os.path.join(EX, "pivoted-dimension-negative.ttl")


def test_tab_pivoted_dimension_terms():
    g = _g(TAB_TTL)
    assert (TAB.PivotedDimension, RDF.type, OWL.Class) in g
    for prop in ["dimensionName", "onAxis", "atLevel", "hasDimensionValue"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing tab:{prop}"


def test_pivoted_dimension_shapes():
    c, t = _v(PIVDIM_CONF); assert c, t
    c, t = _v(PIVDIM_NEG); assert not c
```

Append to `tests/etkl/test_denormalization.py`:

```python
def test_annotate_dimensions_writes_triples():
    from iladub.etkl.denormalization import recover_dimensions, annotate_dimensions
    g = Graph(); t = EX.tbl; cols = _cols(g, t, 4)
    _hdr(g, t, EX.hRegion, 0, "Region", TAB.coversColumn, cols)
    for c, nm in zip(cols, ["North", "South", "East", "West"]):
        _hdr(g, t, URIRef(str(c) + "-h"), 1, nm, TAB.coversColumn, [c])
    dims = recover_dimensions(g, t)
    annotate_dimensions(g, t, dims)
    du = next(g.subjects(RDF.type, TAB.PivotedDimension))
    assert str(g.value(du, TAB.dimensionName)) == "Region"
    assert {str(v) for v in g.objects(du, TAB.hasDimensionValue)} == {"North", "South", "East", "West"}
    assert str(g.value(du, TAB.onAxis)) == "column"
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/etkl/test_denormalization.py -q -k "pivoted or annotate"`
Expected: FAIL (terms/`annotate_dimensions` missing).

- [ ] **Step 3: Add the ontology terms**

In `vocab/ontology/tab.ttl` (keep it free of `qb:` — alignment is a later slice):

```turtle
tab:PivotedDimension a owl:Class ; rdfs:label "Pivoted dimension"@en ;
    rdfs:comment "A dimension recovered from a header axis: a normalized column/attribute a report pivoted into the header hierarchy."@en .
tab:dimensionName a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:string ; rdfs:label "dimension name"@en .
tab:onAxis a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "on axis"@en ;
    rdfs:comment "row | column."@en .
tab:atLevel a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:integer ; rdfs:label "at level"@en .
tab:hasDimensionValue a owl:DatatypeProperty ; rdfs:domain tab:PivotedDimension ; rdfs:range xsd:string ; rdfs:label "has dimension value"@en .
```

- [ ] **Step 4: Add the SHACL shape**

Append to `vocab/shapes/tab-shapes.ttl`:

```turtle
tab:PivotedDimensionShape a sh:NodeShape ;
    sh:targetClass tab:PivotedDimension ;
    sh:property [ sh:path tab:hasDimensionValue ; sh:minCount 1 ;
                  sh:message "A pivoted dimension needs at least one value." ] ;
    sh:property [ sh:path tab:onAxis ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A pivoted dimension sits on exactly one axis." ] .
```

- [ ] **Step 5: Create examples**

`examples/tables/pivoted-dimension-conformant.ttl` — a `PivotedDimension` with `onAxis "column"` + ≥1 `hasDimensionValue`. `pivoted-dimension-negative.ttl` — a `PivotedDimension` missing `onAxis` (or `hasDimensionValue`) → fails the shape. Mirror the style of the existing example ttls.

- [ ] **Step 6: Implement `annotate_dimensions` + exports**

Append to `src/iladub/etkl/denormalization.py`:

```python
from rdflib import Literal, URIRef
from rdflib.namespace import XSD


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
```

In `src/iladub/etkl/__init__.py`, add `from .denormalization import recover_dimensions, annotate_dimensions, PivotedDimension` and append to `__all__`.

- [ ] **Step 7: Run tests + ownership + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/test_tab.py tests/test_vocab_shapes.py tests/test_source_ownership.py tests/etkl/test_denormalization.py -q` then `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — terms present, shapes pass/fail correctly, `tab.ttl` standalone, full suite green (no regression; `compile_tables` unchanged).

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/denormalization.py src/iladub/etkl/__init__.py vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl examples/tables/pivoted-dimension-*.ttl tests/test_tab.py tests/etkl/test_denormalization.py
git commit -m "feat(tab): PivotedDimension vocab + shape + annotate_dimensions"
```

---

## Self-Review (author checklist — completed)

- **Coverage:** recover_dimensions (§2) → Task 1; vocab/SHACL/annotate (§5/§6) → Task 2. The `region_pivot` end-to-end test proves the 8-pre unblock.
- **Decoupled from inference:** §2 logic unit-tested on constructed graphs; one integration test on `region_pivot` (which compiles correctly post-`repair_coverage`).
- **Source ownership:** `tab.ttl` gets zero `qb:` refs (alignment is slice ③); pinned by `test_source_ownership`.
- **No regression:** `compile_tables` unchanged; Task 2 Step 7 runs the full suite.
- **Placeholder scan:** Task 1 Step 3 references the exact code in the Loop 8a plan (already written verbatim there) rather than duplicate it; all other steps are complete inline.
