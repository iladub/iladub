# tab: ontology — verifier core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the **verifier core** of the tabular-topology ontology — the `tab:` vocabulary plus the two load-bearing SHACL invariants (**header-tree tiling** and the **access function**) — with a conforming hierarchical table-holon example and negative (must-fail) cases, validated by pySHACL.

**Architecture:** Follows the repo's ontology pattern exactly: a **standalone** core `vocab/ontology/tab.ttl` (zero external namespace references — reasoner-free), SHACL shapes in `vocab/shapes/tab-shapes.ttl` (using `sh:sparql` for structural constraints, like `dec-shapes.ttl`), a conforming example in `examples/tables/`, negative cases in `tests/`, and a pytest that calls `pyshacl.validate(..., inference="rdfs", advanced=True)` (like `tests/test_governance.py`). This plan builds the *structural* verifier only; the geometric **round-trip** oracle lives in the compiler loop, and the **kind** shapes + `csvw:`/`qb:`/`prov:`/`holon:` alignment modules + the RealHiTBench/CHiTab harness are **separate follow-on plans**.

**Tech Stack:** RDF Turtle, SHACL (pySHACL, already a core dep), rdflib, pytest. Namespace `tab:` = `https://w3id.org/iladub/tab#`.

**Note on SPARQL constraints:** the `sh:sparql` bodies below are first-cut. They are driven by the conformant-passes / negative-fails tests — **iterate the SPARQL until the tests are green** (the tests are the contract), exactly as the repo's other shapes were built.

---

## File Structure

- `vocab/ontology/tab.ttl` — core `tab:` vocabulary (classes + properties). Standalone. *One responsibility: the terms.*
- `vocab/shapes/tab-shapes.ttl` — the tiling + access-function invariants. *One responsibility: the verifier.*
- `examples/tables/hierarchical-conformant.ttl` — a small 2-level hierarchical table-holon that conforms.
- `tests/tab-uncovered-column-leak.ttl`, `tests/tab-overlap-leak.ttl`, `tests/tab-refinement-leak.ttl`, `tests/tab-ambiguous-access-leak.ttl` — negative cases (each must FAIL exactly one invariant).
- `tests/test_tab.py` — parse/structure checks + pySHACL conformant/negative assertions.

---

### Task 1: `tab.ttl` — the core vocabulary (standalone)

**Files:**
- Create: `vocab/ontology/tab.ttl`
- Test: `tests/test_tab.py`

- [ ] **Step 1: Write the failing test**

`tests/test_tab.py`:

```python
"""Tabular-topology ontology (tab:) — vocabulary + SHACL verifier-core tests."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")
EX = os.path.join(ROOT, "examples", "tables")
TST = os.path.join(ROOT, "tests")

TAB = Namespace("https://w3id.org/iladub/tab#")
TAB_TTL = os.path.join(ONT, "tab.ttl")


def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def test_tab_vocab_parses_and_declares_core_terms():
    g = _g(TAB_TTL)
    for cls in ["Table", "Cell", "LabelCell", "EntryCell", "HeaderNode",
                "LeafColumn", "LeafRow", "HierarchicalTable"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing class tab:{cls}"
    for prop in ["parentHeader", "coversColumn", "headerLevel", "hasHeaderNode",
                 "hasLeafColumn", "hasLeafRow", "hasCell", "atColumn", "atRow"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing property tab:{prop}"


def test_tab_core_is_standalone():
    """Core tab.ttl must not reference external namespaces as SUBJECTS (align-not-import)."""
    g = _g(TAB_TTL)
    forbidden = ("w3id.org/holon", "purl.org/linked-data/cube", "w3.org/ns/csvw",
                 "w3.org/ns/prov")
    for s in set(g.subjects()):
        assert not any(f in str(s) for f in forbidden), f"core references external subject {s}"
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_tab.py -v`
Expected: FAIL (cannot parse — file does not exist).

- [ ] **Step 3: Implement `vocab/ontology/tab.ttl`**

```turtle
@prefix tab:  <https://w3id.org/iladub/tab#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:  <http://purl.org/dc/terms/> .

<https://w3id.org/iladub/tab> a owl:Ontology ;
    rdfs:label "iladub tabular-topology ontology"@en ;
    dct:description "Domain-neutral topology of tables as intentional transformation stacks (flat -> pivot -> cosmetic). Standalone core; alignment to csvw:/qb:/prov:/holon: lives in tab-*-align.ttl."@en ;
    dct:creator "François Rosselet" ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> .

# --- the table (a holon) and its kinds -----------------------------------------
tab:Table a owl:Class ; rdfs:label "Table"@en ;
    rdfs:comment "A table-holon: entries indexed by header paths; not an array."@en .
tab:HierarchicalTable a owl:Class ; rdfs:subClassOf tab:Table ;
    rdfs:label "Hierarchical table"@en ;
    rdfs:comment "A table with a multi-level header tree on a column or row axis."@en .

# --- cells and their roles (Wang: label vs entry) ------------------------------
tab:Cell a owl:Class ; rdfs:label "Cell"@en .
tab:LabelCell a owl:Class ; rdfs:subClassOf tab:Cell ; rdfs:label "Label cell"@en ;
    rdfs:comment "A cell that locates entries (a header or stub label)."@en .
tab:EntryCell a owl:Class ; rdfs:subClassOf tab:Cell ; rdfs:label "Entry cell"@en ;
    rdfs:comment "A cell that carries a fact, addressed by a column path x row path."@en .

# --- header trees and leaves ---------------------------------------------------
tab:HeaderNode a owl:Class ; rdfs:label "Header node"@en ;
    rdfs:comment "A node in a header tree; covers a contiguous run of leaf columns."@en .
tab:LeafColumn a owl:Class ; rdfs:label "Leaf column"@en .
tab:LeafRow a owl:Class ; rdfs:label "Leaf row"@en .

tab:parentHeader a owl:ObjectProperty ; rdfs:label "parent header"@en ;
    rdfs:domain tab:HeaderNode ; rdfs:range tab:HeaderNode ;
    rdfs:comment "Links a header node to its parent (child span must be a subset of the parent's)."@en .
tab:coversColumn a owl:ObjectProperty ; rdfs:label "covers column"@en ;
    rdfs:domain tab:HeaderNode ; rdfs:range tab:LeafColumn ;
    rdfs:comment "A leaf column in this header node's span."@en .
tab:headerLevel a owl:DatatypeProperty ; rdfs:label "header level"@en ;
    rdfs:domain tab:HeaderNode ; rdfs:range xsd:integer ;
    rdfs:comment "Depth of this node (0 = topmost)."@en .

# --- table composition ---------------------------------------------------------
tab:hasHeaderNode a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:HeaderNode .
tab:hasLeafColumn a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:LeafColumn .
tab:hasLeafRow a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:LeafRow .
tab:hasCell a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:Cell .

# --- the access function (Wang's map: entry <- column path x row path) ---------
tab:atColumn a owl:ObjectProperty ; rdfs:label "at column"@en ;
    rdfs:domain tab:EntryCell ; rdfs:range tab:LeafColumn .
tab:atRow a owl:ObjectProperty ; rdfs:label "at row"@en ;
    rdfs:domain tab:EntryCell ; rdfs:range tab:LeafRow .
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/test_tab.py -v`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/tab.ttl tests/test_tab.py
git commit -m "feat(tab): core tabular-topology vocabulary (standalone)"
```

---

### Task 2: the conforming hierarchical example

**Files:**
- Create: `examples/tables/hierarchical-conformant.ttl`
- Modify: `tests/test_tab.py`

- [ ] **Step 1: Add the failing structure test**

Append to `tests/test_tab.py`:

```python
CONFORMANT = os.path.join(EX, "hierarchical-conformant.ttl")


def test_conformant_example_structure():
    g = _g(CONFORMANT)
    # 5 leaf columns, 2 leaf rows, 8 entry cells (cols c1..c4 x rows r0,r1)
    tbl = next(g.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(g.objects(tbl, TAB.hasLeafColumn))) == 5
    assert len(list(g.objects(tbl, TAB.hasLeafRow))) == 2
    assert len(list(g.subjects(RDF.type, TAB.EntryCell))) == 8
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_tab.py::test_conformant_example_structure -v`
Expected: FAIL (file not found).

- [ ] **Step 3: Create `examples/tables/hierarchical-conformant.ttl`**

A 2-level column header over 5 leaf columns — c0 is the stub ("Analyte"), a merged "Current" over (c1,c2) and "Prior" over (c3,c4). Entries fill c1..c4 x rows r0,r1.

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .

ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c0, ex:c1, ex:c2, ex:c3, ex:c4 ;
    tab:hasLeafRow    ex:r0, ex:r1 ;
    tab:hasHeaderNode ex:hAnalyte, ex:hCurrent, ex:hPrior,
                      ex:lResultC, ex:lUnitC, ex:lResultP, ex:lUnitP ;
    tab:hasCell ex:e10, ex:e11, ex:e20, ex:e21, ex:e30, ex:e31, ex:e40, ex:e41 .

ex:c0 a tab:LeafColumn . ex:c1 a tab:LeafColumn . ex:c2 a tab:LeafColumn .
ex:c3 a tab:LeafColumn . ex:c4 a tab:LeafColumn .
ex:r0 a tab:LeafRow .    ex:r1 a tab:LeafRow .

# top level (0): stub + two merged parents — tiles c0..c4, no overlap
ex:hAnalyte a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .
ex:hCurrent a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1, ex:c2 .
ex:hPrior   a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c3, ex:c4 .

# leaf level (1): children refine their parents
ex:lResultC a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hCurrent ; tab:coversColumn ex:c1 .
ex:lUnitC   a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hCurrent ; tab:coversColumn ex:c2 .
ex:lResultP a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hPrior ; tab:coversColumn ex:c3 .
ex:lUnitP   a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hPrior ; tab:coversColumn ex:c4 .

# entries: c1..c4 x r0,r1 (c0 is the stub; its cells are LabelCells, omitted here)
ex:e10 a tab:EntryCell ; tab:atColumn ex:c1 ; tab:atRow ex:r0 .
ex:e11 a tab:EntryCell ; tab:atColumn ex:c1 ; tab:atRow ex:r1 .
ex:e20 a tab:EntryCell ; tab:atColumn ex:c2 ; tab:atRow ex:r0 .
ex:e21 a tab:EntryCell ; tab:atColumn ex:c2 ; tab:atRow ex:r1 .
ex:e30 a tab:EntryCell ; tab:atColumn ex:c3 ; tab:atRow ex:r0 .
ex:e31 a tab:EntryCell ; tab:atColumn ex:c3 ; tab:atRow ex:r1 .
ex:e40 a tab:EntryCell ; tab:atColumn ex:c4 ; tab:atRow ex:r0 .
ex:e41 a tab:EntryCell ; tab:atColumn ex:c4 ; tab:atRow ex:r1 .
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/test_tab.py::test_conformant_example_structure -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add examples/tables/hierarchical-conformant.ttl tests/test_tab.py
git commit -m "feat(tab): conforming hierarchical table-holon example"
```

---

### Task 3: `tab-shapes.ttl` — the header-tree tiling invariants

**Files:**
- Create: `vocab/shapes/tab-shapes.ttl`
- Create: `tests/tab-uncovered-column-leak.ttl`, `tests/tab-overlap-leak.ttl`, `tests/tab-refinement-leak.ttl`
- Modify: `tests/test_tab.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
SHAPES = os.path.join(SH, "tab-shapes.ttl")


def _v(*data):
    c, _, t = validate(_g(*data), shacl_graph=_g(SHAPES), inference="rdfs", advanced=True)
    return c, t


def test_conformant_passes_tiling():
    c, t = _v(CONFORMANT)
    assert c, t


def test_uncovered_column_fails():
    c, _ = _v(os.path.join(TST, "tab-uncovered-column-leak.ttl"))
    assert not c


def test_overlapping_headers_fail():
    c, _ = _v(os.path.join(TST, "tab-overlap-leak.ttl"))
    assert not c


def test_refinement_break_fails():
    c, _ = _v(os.path.join(TST, "tab-refinement-leak.ttl"))
    assert not c
```

- [ ] **Step 2: Create the three negative cases**

`tests/tab-uncovered-column-leak.ttl` — a leaf column `ex:c5` in the table but covered by no header:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .
ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c0, ex:c5 ;
    tab:hasHeaderNode ex:hAnalyte .
ex:c0 a tab:LeafColumn . ex:c5 a tab:LeafColumn .
ex:hAnalyte a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .   # c5 uncovered
```

`tests/tab-overlap-leak.ttl` — two same-level headers covering the same column:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .
ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c1 ;
    tab:hasHeaderNode ex:hA, ex:hB .
ex:c1 a tab:LeafColumn .
ex:hA a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1 .
ex:hB a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1 .   # overlap at level 0
```

`tests/tab-refinement-leak.ttl` — a child covering a column its parent does not:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .
ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c1, ex:c2, ex:c9 ;
    tab:hasHeaderNode ex:hParent, ex:lChild .
ex:c1 a tab:LeafColumn . ex:c2 a tab:LeafColumn . ex:c9 a tab:LeafColumn .
ex:hParent a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1, ex:c2 .
ex:lChild  a tab:HeaderNode ; tab:headerLevel 1 ; tab:parentHeader ex:hParent ;
    tab:coversColumn ex:c1, ex:c9 .   # c9 not in parent's span -> refinement break
```

- [ ] **Step 3: Implement `vocab/shapes/tab-shapes.ttl` (tiling)**

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

tab:prefixes
    sh:declare [ sh:prefix "tab" ; sh:namespace "https://w3id.org/iladub/tab#"^^xsd:anyURI ] .

# Coverage: every leaf column must be covered by at least one header node.
tab:CoverageShape a sh:NodeShape ;
    sh:targetClass tab:LeafColumn ;
    sh:sparql [
        sh:message "Leaf column is not covered by any header node (coverage gap)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                ?tbl tab:hasLeafColumn $this .
                FILTER NOT EXISTS { ?h tab:coversColumn $this }
            }
        """ ] .

# No-overlap: two distinct header nodes at the SAME level must not cover the same column.
tab:NoOverlapShape a sh:NodeShape ;
    sh:targetClass tab:Table ;
    sh:sparql [
        sh:message "Two header nodes at the same level cover the same column (overlap)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:hasHeaderNode ?h1, ?h2 .
                FILTER(str(?h1) < str(?h2))
                ?h1 tab:headerLevel ?l . ?h2 tab:headerLevel ?l .
                ?h1 tab:coversColumn ?c . ?h2 tab:coversColumn ?c .
            }
        """ ] .

# Refinement: a child's covered columns must be a subset of its parent's.
tab:RefinementShape a sh:NodeShape ;
    sh:targetClass tab:HeaderNode ;
    sh:sparql [
        sh:message "A header node covers a column its parent does not (refinement break)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:parentHeader ?p .
                $this tab:coversColumn ?c .
                FILTER NOT EXISTS { ?p tab:coversColumn ?c }
            }
        """ ] .
```

- [ ] **Step 4: Run; iterate the SPARQL until green**

Run: `pytest tests/test_tab.py -v`
Expected: `test_conformant_passes_tiling` PASS; the three leak tests PASS (i.e. the examples are correctly rejected). If the conformant example is wrongly rejected or a leak wrongly passes, **fix the SPARQL** (not the tests) — e.g. the overlap `str(?h1) < str(?h2)` de-duplicates the symmetric pair; adjust if pySHACL's SPARQL dialect needs `STR()` casing. Re-run to green.

- [ ] **Step 5: Commit**

```bash
git add vocab/shapes/tab-shapes.ttl tests/tab-uncovered-column-leak.ttl tests/tab-overlap-leak.ttl tests/tab-refinement-leak.ttl tests/test_tab.py
git commit -m "feat(tab): SHACL header-tree tiling invariants (coverage, no-overlap, refinement)"
```

---

### Task 4: the access-function invariants + end-to-end

**Files:**
- Modify: `vocab/shapes/tab-shapes.ttl`
- Create: `tests/tab-ambiguous-access-leak.ttl`, `tests/tab-orphan-entry-leak.ttl`
- Modify: `tests/test_tab.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tab.py`:

```python
def test_orphan_entry_fails():
    """An entry cell whose column is not a leaf column of the table must fail."""
    c, _ = _v(os.path.join(TST, "tab-orphan-entry-leak.ttl"))
    assert not c


def test_ambiguous_access_fails():
    """A leaf column with two leaf-headers (ambiguous column path) must fail."""
    c, _ = _v(os.path.join(TST, "tab-ambiguous-access-leak.ttl"))
    assert not c


def test_conformant_passes_full_verifier():
    """The conformant example passes ALL shapes together (tiling + access)."""
    c, t = _v(CONFORMANT)
    assert c, t
```

- [ ] **Step 2: Create the two negative cases**

`tests/tab-orphan-entry-leak.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .
ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c1 ;
    tab:hasHeaderNode ex:h1 ;
    tab:hasCell ex:eBad .
ex:c1 a tab:LeafColumn .
ex:h1 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1 .
ex:eBad a tab:EntryCell ; tab:atColumn ex:cX ; tab:atRow ex:r0 .   # cX is not a leaf column of the table
ex:cX a tab:LeafColumn . ex:r0 a tab:LeafRow .
```

`tests/tab-ambiguous-access-leak.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .
ex:tbl a tab:HierarchicalTable ;
    tab:hasLeafColumn ex:c1 ;
    tab:hasHeaderNode ex:lA, ex:lB .
ex:c1 a tab:LeafColumn .
# two LEAF headers (neither has children) both cover c1 -> ambiguous column path
ex:lA a tab:HeaderNode ; tab:headerLevel 1 ; tab:coversColumn ex:c1 .
ex:lB a tab:HeaderNode ; tab:headerLevel 1 ; tab:coversColumn ex:c1 .
```

- [ ] **Step 3: Add the access-function shapes to `vocab/shapes/tab-shapes.ttl`**

Append:

```turtle
# Access cardinality: an entry cell has exactly one column and one row.
tab:EntryCellShape a sh:NodeShape ;
    sh:targetClass tab:EntryCell ;
    sh:property [ sh:path tab:atColumn ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "An entry cell must sit at exactly one leaf column." ] ;
    sh:property [ sh:path tab:atRow ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "An entry cell must sit at exactly one leaf row." ] .

# Orphan: an entry cell's column must be a leaf column of a table that owns the cell.
tab:EntryColumnBoundShape a sh:NodeShape ;
    sh:targetClass tab:EntryCell ;
    sh:sparql [
        sh:message "Entry cell sits at a column that is not a leaf column of its table (orphan)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                ?tbl tab:hasCell $this .
                $this tab:atColumn ?c .
                FILTER NOT EXISTS { ?tbl tab:hasLeafColumn ?c }
            }
        """ ] .

# Unambiguous column path: each leaf column is covered by exactly one LEAF header
# (a header with no children). Zero or two+ leaf-headers => ambiguous/undefined path.
tab:UnambiguousAccessShape a sh:NodeShape ;
    sh:targetClass tab:LeafColumn ;
    sh:sparql [
        sh:message "Leaf column does not have exactly one leaf-header (ambiguous column path)." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                ?tbl tab:hasLeafColumn $this .
                {
                    SELECT $this (COUNT(DISTINCT ?h) AS ?n) WHERE {
                        ?h tab:coversColumn $this .
                        FILTER NOT EXISTS { ?child tab:parentHeader ?h }
                    } GROUP BY $this
                }
                FILTER(?n != 1)
            }
        """ ] .
```

- [ ] **Step 4: Run; iterate the SPARQL until green**

Run: `pytest tests/test_tab.py -v`
Expected: all PASS — the conformant example passes the full verifier; orphan and ambiguous leaks fail. Likely iteration point: the `UnambiguousAccessShape` sub-select only emits rows where a leaf-header exists (n>=1); the zero-leaf-header case (a column with no leaf-header) is caught by `CoverageShape` from Task 3, so the two shapes together cover it — verify a column covered only by a *parent* (with children) is rejected; if not, broaden the sub-select with a `UNION` for the zero case. Do NOT weaken the tests.

- [ ] **Step 5: Run the whole suite + commit**

Run: `pytest tests/test_tab.py -v` (all green) and `pytest tests/ -q --continue-on-collection-errors` (no new failures; pre-existing baml collection errors are unrelated unless `baml-py==0.222.0` is installed).

```bash
git add vocab/shapes/tab-shapes.ttl tests/tab-ambiguous-access-leak.ttl tests/tab-orphan-entry-leak.ttl tests/test_tab.py
git commit -m "feat(tab): SHACL access-function invariants (cardinality, orphan, unambiguous path)"
```

---

## Self-Review

**Spec coverage (verifier-core slice):** core vocabulary §4 ✓ (Task 1); conforming + negative examples per CLAUDE.md convention ✓ (Tasks 2–4); the verifier §8 structural invariants — header-tree tiling (coverage/no-overlap/refinement) ✓ (Task 3) and access-function (cardinality/orphan/unambiguity) ✓ (Task 4). **Deferred to follow-on plans (explicitly out of scope here):** the geometric **round-trip** oracle (lives in the compiler loop); the **kind** shapes §7; the `csvw:`/`qb:`/`prov:`/`holon:` **alignment modules** §10; the **RealHiTBench/CHiTab** harness §11; the three **states** and two **transforms** §5–6.

**Placeholder scan:** no TBD/TODO; every code step has runnable Turtle/SHACL/pytest. The "iterate the SPARQL to green" notes give a concrete default plus the exact failure direction — driven by real tests, not placeholders.

**Type/name consistency:** `tab:` term names (`Table, HierarchicalTable, Cell, LabelCell, EntryCell, HeaderNode, LeafColumn, LeafRow, parentHeader, coversColumn, headerLevel, hasHeaderNode, hasLeafColumn, hasLeafRow, hasCell, atColumn, atRow`) are identical across the vocabulary (Task 1), the example (Task 2), the shapes (Tasks 3–4), and the tests. `tab:prefixes` is declared once (Task 3) and reused (Task 4). Test helpers `_g`/`_v` defined once and reused.

---

## Next plans (separate)
- **tab kinds** — SHACL patterns for record / hierarchical / pivot / key-value (§7).
- **tab alignment** — `tab-csvw-align.ttl` · `tab-qb-align.ttl` · `tab-prov-align.ttl` · `tab-holon-align.ttl` (§10), + a w3id redirect for `tab:`.
- **tab benchmark harness** — RealHiTBench / CHiTab round-trip evaluation (§11).
- **the three states + two transforms** — FlatView/CubeView/PresentedView + Pivot/Present transforms (§5–6), wired into Loop 1's Actions.
