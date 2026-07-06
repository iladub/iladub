# Table-Holon Closing Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Loop 1: compile a flat record-table PDF end-to-end into a validated `tab:` table-holon with a score, escalating every other region in-band as an `iladub:CandidateConcept`.

**Architecture:** Reuse #31 (geometry → bands → leaf-grid) and #32 (`tab:` SHACL). Add four small modules — `regions.py` (classify + assign), `roundtrip.py` (per-cell gate + spatial-ASCII), `holon.py` (RDF assert/propose mapper), `compile.py` (orchestrator + report). The kind classifier is **header-regularity** (line 0 = exactly `ncols` words, one per column), not raw tiling — empirically required (a merged header collapses the profiled grid so raw tiling misclassifies the pivot).

**Tech Stack:** Python 3.12, `pdfplumber`, `numpy`, `rdflib`, `pyshacl`, `reportlab` (dev/test only), `pytest`.

**Spec:** `docs/superpowers/specs/2026-07-05-table-holon-closing-slice-design.md`

## Global Constraints

- **Licensing:** code Apache-2.0; vocabulary CC-BY-4.0. Author: François Rosselet, © 2026.
- **Core `tab.ttl` stays standalone:** zero `w3id.org/holon`, `prov`, `csvw`, `qb` references as **subjects** (align-not-import; enforced by `tests/test_tab.py::test_tab_core_is_standalone`).
- **Multilingual literals:** never constrain label/text properties to `xsd:string` (rejects `rdf:langString`). `tab:cellText` range is `rdfs:Literal`.
- **Provenance reuse:** provenance rides `prov:` (`prov:wasDerivedFrom`), not a bespoke property.
- **Every shape ships a conforming example AND a negative test that must fail.**
- **`reportlab`/`pdfplumber` tests guard with `pytest.importorskip`.**
- **No overfitting:** the gate is an oracle (header regularity + gutter containment), never a tuned constant tuned to make one fixture pass.
- **Namespaces:** `tab:` = `https://w3id.org/iladub/tab#`, `iladub:` = `https://w3id.org/iladub#`, `dec:` = `https://w3id.org/iladub/dec#`, `prov:` = `http://www.w3.org/ns/prov#`.

## File Structure

| File | Responsibility |
|------|----------------|
| `vocab/ontology/tab.ttl` (modify) | add Physical layer: `tab:cellText`, `tab:onPage`, `tab:hasBBox`/`tab:BBox`/`x0..y1`, `tab:RecordTable` |
| `vocab/shapes/tab-physical-shapes.ttl` (create) | `tab:EntryCellPhysicalShape` — separate file so topology-only examples don't need geometry |
| `examples/tables/record-conformant.ttl` (create) | flat record holon **with** physical props — doubles as expected compiler output |
| `tests/tab-missing-physical-leak.ttl` (create) | negative: an `EntryCell` missing `cellText` |
| `src/iladub/etkl/regions.py` (create) | `RegionKind`, `Cell`, `ClassifiedRegion`, `column_of`, `assign_cells`, `classify` |
| `src/iladub/etkl/roundtrip.py` (create) | `cell_round_trips`, `render_ascii` |
| `src/iladub/etkl/holon.py` (create) | `assert_record_region`, `escalate_region` (rdflib) |
| `src/iladub/etkl/compile.py` (create) | `RegionReport`, `CompilationReport`, `compile_tables` |
| `src/iladub/etkl/__init__.py` (modify) | export the new public API |
| `tests/etkl/fixtures.py` (modify) | add `pivoted_table_pdf`, `wide_cell_table_pdf` |
| `tests/test_tab.py` (modify) | physical terms + physical shape conformant/leak |
| `tests/etkl/test_regions.py` (create) | classifier + assignment unit tests |
| `tests/etkl/test_roundtrip.py` (create) | cell-gate + ascii unit tests |
| `tests/etkl/test_holon.py` (create) | mapper + SHACL unit tests |
| `tests/etkl/test_closing_slice.py` (create) | the proof-of-closure integration suite |

Run the whole suite with `pytest -q`. Run one test with `pytest -q path::name -v`.

---

### Task 1: `tab:` Physical-layer ontology terms

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append after the access-function section, ~line 79)
- Test: `tests/test_tab.py` (append)

**Interfaces:**
- Produces: classes `tab:RecordTable`, `tab:BBox`; properties `tab:cellText`, `tab:onPage`, `tab:hasBBox`, `tab:x0`, `tab:y0`, `tab:x1`, `tab:y1`.

- [ ] **Step 1: Write the failing test** — append to `tests/test_tab.py`:

```python
def test_tab_physical_terms_present():
    g = _g(TAB_TTL)
    for cls in ["RecordTable", "BBox"]:
        assert (TAB[cls], RDF.type, OWL.Class) in g, f"missing class tab:{cls}"
    for prop in ["cellText", "onPage", "hasBBox", "x0", "y0", "x1", "y1"]:
        assert (TAB[prop], RDF.type, None) in g, f"missing property tab:{prop}"

def test_tab_recordtable_is_table_subclass():
    g = _g(TAB_TTL)
    assert (TAB.RecordTable, RDFS.subClassOf, TAB.Table) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_tab.py::test_tab_physical_terms_present -v`
Expected: FAIL (`missing class tab:RecordTable`).

- [ ] **Step 3: Add the terms** — append to `vocab/ontology/tab.ttl`:

```turtle
# --- kinds (v1) ----------------------------------------------------------------
tab:RecordTable a owl:Class ; rdfs:subClassOf tab:Table ;
    rdfs:label "Record table"@en ;
    rdfs:comment "A flat table: a single-level header with one label per leaf column, and rows of entries."@en .

# --- physical layer (geometry + surface text; needed for round-trip + provenance) ---
tab:cellText a owl:DatatypeProperty ; rdfs:label "cell text"@en ;
    rdfs:domain tab:Cell ; rdfs:range rdfs:Literal ;
    rdfs:comment "The surface text a cell carries. Language-tagged literals are allowed; NOT constrained to xsd:string."@en .
tab:onPage a owl:DatatypeProperty ; rdfs:label "on page"@en ;
    rdfs:domain tab:Cell ; rdfs:range xsd:integer ;
    rdfs:comment "Zero-based index of the page the cell was measured on."@en .
tab:hasBBox a owl:ObjectProperty ; rdfs:label "has bbox"@en ;
    rdfs:domain tab:Cell ; rdfs:range tab:BBox ;
    rdfs:comment "The measured bounding box of the cell, in PDF points."@en .
tab:BBox a owl:Class ; rdfs:label "Bounding box"@en ;
    rdfs:comment "A rectangle in PDF points: x0/x1 from the page left, y0/y1 (top/bottom) from the page top."@en .
tab:x0 a owl:DatatypeProperty ; rdfs:domain tab:BBox ; rdfs:range xsd:decimal ; rdfs:label "x0"@en .
tab:y0 a owl:DatatypeProperty ; rdfs:domain tab:BBox ; rdfs:range xsd:decimal ; rdfs:label "y0"@en .
tab:x1 a owl:DatatypeProperty ; rdfs:domain tab:BBox ; rdfs:range xsd:decimal ; rdfs:label "x1"@en .
tab:y1 a owl:DatatypeProperty ; rdfs:domain tab:BBox ; rdfs:range xsd:decimal ; rdfs:label "y1"@en .
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q "tests/test_tab.py::test_tab_physical_terms_present" "tests/test_tab.py::test_tab_recordtable_is_table_subclass" "tests/test_tab.py::test_tab_core_is_standalone" -v`
Expected: 3 passed (standalone test still green — no `prov`/HGA subjects added).

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/tab.ttl tests/test_tab.py
git commit -m "feat(tab): physical layer — cellText, onPage, hasBBox/BBox, RecordTable"
```

---

### Task 2: Physical-layer SHACL shape + conformant/leak fixtures

**Files:**
- Create: `vocab/shapes/tab-physical-shapes.ttl`
- Create: `examples/tables/record-conformant.ttl`
- Create: `tests/tab-missing-physical-leak.ttl`
- Test: `tests/test_tab.py` (append)

**Interfaces:**
- Produces: `tab:EntryCellPhysicalShape` (targets `tab:EntryCell`, requires `cellText`+`onPage`+`hasBBox`). Kept in a **separate** shapes file so the topology-only examples (`hierarchical-conformant.ttl`) still pass `tab-shapes.ttl` unchanged.
- Consumes: the physical terms from Task 1.

- [ ] **Step 1: Write the failing test** — append to `tests/test_tab.py`:

```python
PHYS_SH = os.path.join(SH, "tab-physical-shapes.ttl")

def _vp(*data_paths):
    """Validate data against topology + physical shapes together."""
    data = _g(*data_paths)
    shapes = _g(os.path.join(SH, "tab-shapes.ttl"), PHYS_SH)
    conforms, _, text = validate(data, shacl_graph=shapes, ont_graph=_g(TAB_TTL),
                                 inference="rdfs", advanced=True)
    return conforms, text

def test_record_conformant_passes_physical():
    c, t = _vp(os.path.join(EX, "record-conformant.ttl"))
    assert c, t

def test_missing_physical_fails():
    c, t = _vp(os.path.join(TST, "tab-missing-physical-leak.ttl"))
    assert not c
    assert "EntryCellPhysicalShape" in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_tab.py::test_record_conformant_passes_physical -v`
Expected: FAIL (files/shape not found).

- [ ] **Step 3a: Create the shape** — `vocab/shapes/tab-physical-shapes.ttl`:

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix tab:  <https://w3id.org/iladub/tab#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://w3id.org/iladub/tab/shapes/physical> a <http://www.w3.org/2002/07/owl#Ontology> ;
    dcterms:title "tab physical-layer SHACL shapes"@en ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    dcterms:creator "François Rosselet" .

# An asserted EntryCell must carry its measured geometry and surface text —
# so the holon can be round-tripped and traced to the page (provenance-to-page).
tab:EntryCellPhysicalShape a sh:NodeShape ;
    sh:targetClass tab:EntryCell ;
    sh:property [ sh:name "EntryCellPhysicalShape" ; sh:path tab:cellText ; sh:minCount 1 ] ;
    sh:property [ sh:name "EntryCellPhysicalShape" ; sh:path tab:onPage ;
                  sh:minCount 1 ; sh:datatype xsd:integer ] ;
    sh:property [ sh:name "EntryCellPhysicalShape" ; sh:path tab:hasBBox ;
                  sh:minCount 1 ; sh:class tab:BBox ] .
```

- [ ] **Step 3b: Create the conformant example** — `examples/tables/record-conformant.ttl`:

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ex:  <https://example.org/tab-demo#> .

# A flat 3-column record table: single-level header, one label per column.
ex:t a tab:RecordTable ;
    tab:hasLeafColumn ex:c0, ex:c1, ex:c2 ;
    tab:hasLeafRow    ex:r0 ;
    tab:hasHeaderNode ex:h0, ex:h1, ex:h2 ;
    tab:hasCell ex:e0, ex:e1, ex:e2 .

ex:c0 a tab:LeafColumn . ex:c1 a tab:LeafColumn . ex:c2 a tab:LeafColumn .
ex:r0 a tab:LeafRow .

# flat header: one node per column at level 0 (tiles c0..c2, no overlap, no parents)
ex:h0 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .
ex:h1 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c1 .
ex:h2 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c2 .

# one data row of entries, each carrying text + page + bbox + provenance
ex:e0 a tab:EntryCell ; tab:atColumn ex:c0 ; tab:atRow ex:r0 ;
    tab:cellText "Hemoglobin" ; tab:onPage 0 ;
    tab:hasBBox [ a tab:BBox ; tab:x0 72.0 ; tab:y0 662.0 ; tab:x1 130.0 ; tab:y1 672.0 ] ;
    prov:wasDerivedFrom <https://example.org/doc#p0-72-662> .
ex:e1 a tab:EntryCell ; tab:atColumn ex:c1 ; tab:atRow ex:r0 ;
    tab:cellText "13.2" ; tab:onPage 0 ;
    tab:hasBBox [ a tab:BBox ; tab:x0 240.0 ; tab:y0 662.0 ; tab:x1 268.0 ; tab:y1 672.0 ] ;
    prov:wasDerivedFrom <https://example.org/doc#p0-240-662> .
ex:e2 a tab:EntryCell ; tab:atColumn ex:c2 ; tab:atRow ex:r0 ;
    tab:cellText "g/dL" ; tab:onPage 0 ;
    tab:hasBBox [ a tab:BBox ; tab:x0 400.0 ; tab:y0 662.0 ; tab:x1 428.0 ; tab:y1 672.0 ] ;
    prov:wasDerivedFrom <https://example.org/doc#p0-400-662> .
```

- [ ] **Step 3c: Create the leak** — `tests/tab-missing-physical-leak.ttl` (an EntryCell with no `cellText`):

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix ex:  <https://example.org/tab-demo#> .

ex:t a tab:RecordTable ;
    tab:hasLeafColumn ex:c0 ; tab:hasLeafRow ex:r0 ;
    tab:hasHeaderNode ex:h0 ; tab:hasCell ex:e0 .
ex:c0 a tab:LeafColumn . ex:r0 a tab:LeafRow .
ex:h0 a tab:HeaderNode ; tab:headerLevel 0 ; tab:coversColumn ex:c0 .
# EntryCell missing cellText/onPage/hasBBox — must fail EntryCellPhysicalShape
ex:e0 a tab:EntryCell ; tab:atColumn ex:c0 ; tab:atRow ex:r0 .
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q tests/test_tab.py -v`
Expected: all pass, including the pre-existing `test_conformant_passes_full_verifier` (topology-only example untouched — the physical shape lives in a separate file).

- [ ] **Step 5: Commit**

```bash
git add vocab/shapes/tab-physical-shapes.ttl examples/tables/record-conformant.ttl tests/tab-missing-physical-leak.ttl tests/test_tab.py
git commit -m "feat(tab): EntryCell physical-layer shape + conformant/leak fixtures"
```

---

### Task 3: `regions.py` — assignment + header-regularity classifier

**Files:**
- Create: `src/iladub/etkl/regions.py`
- Modify: `tests/etkl/fixtures.py` (add `pivoted_table_pdf`, `wide_cell_table_pdf`)
- Test: `tests/etkl/test_regions.py`

**Interfaces:**
- Consumes: `Band`, `Line`, `Word` (from `bands`/`geometry`); `LeafGrid`, `infer_leaf_grid` (from `grid`).
- Produces:
  - `class RegionKind(Enum)` with `RECORD_TABLE`, `UNSUPPORTED_TABLE`, `NON_TABLE`.
  - `@dataclass(frozen=True) class Cell: row: int; col: int; words: tuple[Word, ...]` with `.text -> str` (words joined by space, x-order) and `.bbox -> tuple[float,float,float,float]` (x0, top, x1, bottom, over its words).
  - `@dataclass(frozen=True) class ClassifiedRegion: kind: RegionKind; band: Band; grid: LeafGrid | None; cells: tuple[Cell, ...]; reason: str` (cells include row 0 = header; empty for NON_TABLE).
  - `column_of(x_center: float, boundaries: Sequence[float]) -> int`.
  - `assign_cells(band: Band, grid: LeafGrid) -> tuple[Cell, ...]` — group each line's words by column into `Cell`s (row index = line index).
  - `classify(band: Band) -> ClassifiedRegion`.

- [ ] **Step 1: Add fixtures** — append to `tests/etkl/fixtures.py`:

# NOTE: this geometry is a faithful copy of demo/etkl_demo_data.py::pivoted_report_pdf,
# empirically verified (2026-07-05) to keep the merged parent header + sub-header +
# (SI) line + 5 body rows in ONE band, so the classifier sees the merged header and
# escalates. Do NOT change the spacing without re-verifying it stays a single band —
# if the body bands away from its header it could be misread as a clean record table.
def pivoted_table_pdf(path: str) -> dict:
    """A pivoted table: two merged, centered parent headers over leaf columns —
    the case the record-table slice must ESCALATE, not assert."""
    leaves = [(50.0, 150.0, "left"), (160.0, 215.0, "right"), (225.0, 280.0, "left"),
              (290.0, 335.0, "center"), (365.0, 420.0, "right"), (430.0, 485.0, "left"),
              (495.0, 545.0, "center")]
    parents = [("Current Visit", 1, 3), ("Prior Visit", 4, 6)]
    subs = ["Analyte", "Result", "Unit", "Flag", "Result", "Unit", "Flag"]
    body = [("Hemoglobin", "13.2", "g/dL", "LOW", "12.8", "g/dL", "LOW"),
            ("Hematocrit", "39.5", "%", "LOW", "38.1", "%", "LOW"),
            ("WBC", "7.8", "x10^9/L", "", "9.2", "x10^9/L", "HIGH"),
            ("Platelets", "252", "x10^9/L", "", "248", "x10^9/L", ""),
            ("MCV", "88.4", "fL", "", "87.9", "fL", "")]

    def place(c, text, left, right, align, y):
        if not text:
            return
        if align == "right":
            c.drawRightString(right, y, text)
        elif align == "center":
            c.drawCentredString((left + right) / 2.0, y, text)
        else:
            c.drawString(left, y, text)

    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 14)
    c.drawString(50.0, PAGE_H - 55.0, "SERIAL CBC")
    top = PAGE_H - 95.0
    c.setFont("Courier-Bold", 10)
    for label, i, j in parents:
        c.drawCentredString((leaves[i][0] + leaves[j][1]) / 2.0, top, label)
    for (l, r, align), name in zip(leaves, subs):
        place(c, name, l, r, "center" if name != "Analyte" else "left", top - 15.0)
    for idx in (1, 4):
        l, r, _ = leaves[idx]
        c.drawCentredString((l + r) / 2.0, top - 28.0, "(SI)")
    c.setFont("Courier", 10)
    for i, row in enumerate(body):
        y = top - 50.0 - i * 18.0
        for (l, r, align), cell in zip(leaves, row):
            place(c, cell, l, r, align, y)
    c.save()
    return {"n_leaf_cols": 7, "title": "SERIAL CBC"}


def wide_cell_table_pdf(path: str) -> dict:
    """A clean 3-col header, but one data value is wide enough to fill the
    gutter — collapses the profiled grid; must escalate the whole region."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    cols = [72.0, 240.0, 400.0]
    rows = [("Analyte", "Value", "Unit"),
            ("Hemoglobin", "13.2", "g/dL"),
            ("Note", "THIS_CELL_IS_FAR_TOO_WIDE_AND_FILLS_THE_GUTTER", "x")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}
```

- [ ] **Step 2: Write the failing tests** — `tests/etkl/test_regions.py`:

```python
import pytest
pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf, wide_cell_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify, RegionKind, assign_cells, column_of
from iladub.etkl.grid import infer_leaf_grid


def _bands(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))


def test_column_of_picks_span():
    assert column_of(80.0, [72.0, 186.0, 335.0, 442.0]) == 0
    assert column_of(250.0, [72.0, 186.0, 335.0, 442.0]) == 1


def test_simple_table_body_is_record(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[1]
    r = classify(band)
    assert r.kind is RegionKind.RECORD_TABLE, r.reason
    assert r.grid.ncols == 3


def test_title_band_is_non_table(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[0]
    assert classify(band).kind is RegionKind.NON_TABLE


def test_pivot_band_is_unsupported(tmp_path):
    # the band holding the merged parent header must NOT be read as a record table
    bands = _bands(pivoted_table_pdf, tmp_path)
    kinds = {classify(b).kind for b in bands}
    assert RegionKind.RECORD_TABLE not in kinds, "pivot silently asserted!"
    assert RegionKind.UNSUPPORTED_TABLE in kinds


def test_wide_cell_collapses_to_unsupported(tmp_path):
    bands = _bands(wide_cell_table_pdf, tmp_path)
    assert RegionKind.RECORD_TABLE not in {classify(b).kind for b in bands}


def test_assign_cells_groups_by_column(tmp_path):
    band = _bands(simple_table_pdf, tmp_path)[1]
    cells = assign_cells(band, infer_leaf_grid(band))
    header = [c for c in cells if c.row == 0]
    assert {c.col for c in header} == {0, 1, 2}
    assert next(c for c in header if c.col == 0).text == "Analyte"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest -q tests/etkl/test_regions.py -v`
Expected: FAIL (`No module named 'iladub.etkl.regions'`).

- [ ] **Step 4: Implement** — `src/iladub/etkl/regions.py`:

```python
"""regions — classify a band into a table kind and assign its words to cells.

The kind gate is HEADER REGULARITY, not raw tiling: a merged header collapses
the profiled grid (infer_leaf_grid reads a 7-column pivot as 5), and under that
coarse grid every word still sits inside a span — so 'does every line tile?'
returns True for the pivot and would silently assert a wrong table. Instead a
band is a RECORD_TABLE only if its header line has exactly `ncols` words, the
i-th within column i's span (one clean label per column).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .bands import Band
from .geometry import Word
from .grid import LeafGrid, infer_leaf_grid

_EPS = 0.01


class RegionKind(Enum):
    RECORD_TABLE = "RECORD_TABLE"
    UNSUPPORTED_TABLE = "UNSUPPORTED_TABLE"
    NON_TABLE = "NON_TABLE"


@dataclass(frozen=True)
class Cell:
    row: int                      # 0 = header line, 1..N = data lines
    col: int
    words: tuple[Word, ...]

    @property
    def text(self) -> str:
        return " ".join(w.text for w in sorted(self.words, key=lambda w: w.x0))

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        return (min(w.x0 for w in self.words), min(w.top for w in self.words),
                max(w.x1 for w in self.words), max(w.bottom for w in self.words))


@dataclass(frozen=True)
class ClassifiedRegion:
    kind: RegionKind
    band: Band
    grid: LeafGrid | None
    cells: tuple[Cell, ...]
    reason: str


def column_of(x_center: float, boundaries: Sequence[float]) -> int:
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= x_center < boundaries[i + 1]:
            return i
    return len(boundaries) - 2


def assign_cells(band: Band, grid: LeafGrid) -> tuple[Cell, ...]:
    b = grid.boundaries
    out: list[Cell] = []
    for row, line in enumerate(band.lines):
        by_col: dict[int, list[Word]] = {}
        for w in line.words:
            by_col.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        for col, ws in sorted(by_col.items()):
            out.append(Cell(row, col, tuple(ws)))
    return tuple(out)


def _word_in_column(w: Word, col: int, boundaries: Sequence[float]) -> bool:
    return w.x0 >= boundaries[col] - _EPS and w.x1 <= boundaries[col + 1] + _EPS


def classify(band: Band) -> ClassifiedRegion:
    if len(band.lines) < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, None, (), "fewer than 2 lines")
    grid = infer_leaf_grid(band)
    if grid.ncols < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, grid, (), "fewer than 2 columns")
    header = band.lines[0]
    b = grid.boundaries
    # header regularity: exactly ncols words, the i-th (left-to-right) within column i
    if len(header.words) != grid.ncols:
        return ClassifiedRegion(
            RegionKind.UNSUPPORTED_TABLE, band, grid, (),
            f"header has {len(header.words)} words but {grid.ncols} columns")
    for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
        if not _word_in_column(w, i, b):
            return ClassifiedRegion(
                RegionKind.UNSUPPORTED_TABLE, band, grid, (),
                f"header word {w.text!r} is not aligned 1:1 with column {i}")
    return ClassifiedRegion(RegionKind.RECORD_TABLE, band, grid,
                            assign_cells(band, grid), "flat single-level header")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest -q tests/etkl/test_regions.py -v`
Expected: all pass. In particular `test_pivot_band_is_unsupported` proves no silent assert.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/regions.py tests/etkl/fixtures.py tests/etkl/test_regions.py
git commit -m "feat(etkl): region classifier — header-regularity gate + cell assignment"
```

---

### Task 4: `roundtrip.py` — per-cell gate + spatial-ASCII evidence

**Files:**
- Create: `src/iladub/etkl/roundtrip.py`
- Test: `tests/etkl/test_roundtrip.py`

**Interfaces:**
- Consumes: `Cell` (from `regions`), `Band` (from `bands`), `LeafGrid` (from `grid`).
- Produces:
  - `cell_round_trips(cell: Cell, boundaries: Sequence[float]) -> bool` — every word of the cell lies within `[boundaries[cell.col], boundaries[cell.col+1]]`.
  - `render_ascii(band: Band, width: int = 80) -> str` — a monospace layout of the band's words by x-position (the evidence / escalation surface text).

- [ ] **Step 1: Write the failing tests** — `tests/etkl/test_roundtrip.py`:

```python
from iladub.etkl.geometry import Word, Line
from iladub.etkl.bands import Band
from iladub.etkl.regions import Cell
from iladub.etkl.roundtrip import cell_round_trips, render_ascii

BND = [72.0, 186.0, 335.0, 442.0]   # 3 columns


def test_contained_word_round_trips():
    w = Word("13.2", 240.0, 268.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w,)), BND) is True


def test_straddling_word_fails():
    # a word crossing the c1/c2 boundary (335.0) must fail — the oracle bites
    w = Word("TOOWIDE", 300.0, 360.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w,)), BND) is False


def test_multiword_cell_round_trips():
    w1 = Word("13.2", 240.0, 260.0, 100.0, 110.0)
    w2 = Word("mg", 265.0, 285.0, 100.0, 110.0)
    assert cell_round_trips(Cell(1, 1, (w1, w2)), BND) is True


def test_render_ascii_places_words_left_to_right():
    line = Line((Word("A", 72.0, 82.0, 100.0, 110.0),
                 Word("B", 400.0, 410.0, 100.0, 110.0)), 100.0, 110.0)
    out = render_ascii(Band((line,), 100.0, 110.0), width=40)
    assert out.index("A") < out.index("B")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest -q tests/etkl/test_roundtrip.py -v`
Expected: FAIL (`No module named 'iladub.etkl.roundtrip'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/roundtrip.py`:

```python
"""roundtrip — the per-cell round-trip oracle and its spatial-ASCII evidence.

Gate: a cell round-trips iff every word lies within its assigned column span
(no straddle across a gutter). The gutter (a boundary between spans) is the
oracle; there is no tuned tolerance beyond a hair's-width float epsilon.
"""
from __future__ import annotations

from typing import Sequence

from .bands import Band
from .regions import Cell

_EPS = 0.01


def cell_round_trips(cell: Cell, boundaries: Sequence[float]) -> bool:
    lo, hi = boundaries[cell.col], boundaries[cell.col + 1]
    return all(w.x0 >= lo - _EPS and w.x1 <= hi + _EPS for w in cell.words)


def render_ascii(band: Band, width: int = 80) -> str:
    """Render the band's words to a monospace canvas positioned by x, so a human
    (and a diff) can see the measured layout. Used as escalation surface text."""
    words = [w for ln in band.lines for w in ln.words]
    if not words:
        return ""
    x0 = min(w.x0 for w in words)
    x1 = max(w.x1 for w in words)
    span = (x1 - x0) or 1.0
    tops = sorted({round(ln.top, 1) for ln in band.lines})
    rows: list[list[str]] = [[" "] * width for _ in tops]
    row_of = {t: i for i, t in enumerate(tops)}
    for ln in band.lines:
        r = rows[row_of[round(ln.top, 1)]]
        for w in ln.words:
            start = int((w.x0 - x0) / span * (width - 1))
            for k, ch in enumerate(w.text):
                if start + k < width:
                    r[start + k] = ch
    return "\n".join("".join(r).rstrip() for r in rows)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q tests/etkl/test_roundtrip.py -v`
Expected: 4 passed. `test_straddling_word_fails` is the anti-silent-wrong proof.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/roundtrip.py tests/etkl/test_roundtrip.py
git commit -m "feat(etkl): round-trip oracle (gutter-containment gate) + spatial-ASCII"
```

---

### Task 5: `holon.py` — RDF assert / propose mapper

**Files:**
- Create: `src/iladub/etkl/holon.py`
- Test: `tests/etkl/test_holon.py`

**Interfaces:**
- Consumes: `ClassifiedRegion`, `Cell`, `RegionKind` (from `regions`); `cell_round_trips` (from `roundtrip`).
- Produces:
  - Namespaces `TAB`, `ILADUB`, `DEC`, `PROV` (rdflib `Namespace`).
  - `assert_record_region(g: Graph, region: ClassifiedRegion, table_uri: URIRef, doc_uri: URIRef, page: int) -> int` — emit `tab:RecordTable` + columns/rows/headers/entries for cells that round-trip; return the count of asserted **data** cells. Header cells (row 0) become `tab:LabelCell` + one `tab:HeaderNode` per column (`headerLevel 0`), not scored.
  - `escalate_region(g: Graph, cand_uri: URIRef, doc_uri: URIRef, ascii_text: str, reason: str, anchor: URIRef, confidence: float) -> None` — emit an `iladub:CandidateConcept`.

- [ ] **Step 1: Write the failing tests** — `tests/etkl/test_holon.py`:

```python
import os
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph, URIRef, RDF
from pyshacl import validate
from tests.etkl.fixtures import simple_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.regions import classify
from iladub.etkl.holon import (assert_record_region, escalate_region,
                               TAB, ILADUB, PROV)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONT = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")
SH = os.path.join(ROOT, "vocab", "shapes")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SH, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SH, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _record_region(tmp_path):
    p = tmp_path / "x.pdf"; simple_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[1]
    return classify(band)


def test_assert_produces_conforming_holon(tmp_path):
    g = Graph()
    n = assert_record_region(g, _record_region(tmp_path),
                             URIRef("urn:t"), URIRef("urn:doc"), page=0)
    assert n == 9   # 3 data rows x 3 columns
    assert (URIRef("urn:t"), None, None) in g
    conforms, _, text = validate(g, shacl_graph=_shapes(),
                                 ont_graph=Graph().parse(ONT, format="turtle"),
                                 inference="rdfs", advanced=True)
    assert conforms, text


def test_asserted_entry_has_text_and_bbox(tmp_path):
    g = Graph()
    assert_record_region(g, _record_region(tmp_path),
                         URIRef("urn:t"), URIRef("urn:doc"), page=0)
    texts = {str(o) for o in g.objects(None, TAB.cellText)}
    assert "Hemoglobin" in texts and "13.2" in texts
    assert any(True for _ in g.triples((None, TAB.hasBBox, None)))
    assert any(True for _ in g.triples((None, PROV.wasDerivedFrom, None)))


def test_escalate_produces_candidate():
    g = Graph()
    escalate_region(g, URIRef("urn:reg"), URIRef("urn:doc"),
                    ascii_text="Current Visit  Prior Visit",
                    reason="KIND_NOT_SUPPORTED", anchor=TAB.HierarchicalTable,
                    confidence=0.4)
    assert (URIRef("urn:reg"), RDF.type, ILADUB.CandidateConcept) in g
    assert any(True for _ in g.triples((None, ILADUB.surfaceText, None)))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest -q tests/etkl/test_holon.py -v`
Expected: FAIL (`No module named 'iladub.etkl.holon'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/holon.py`:

```python
"""holon — map classified regions to RDF: assert faithful structure, propose the rest.

Assert: a tab: RecordTable with columns/rows/single-level header + EntryCells
carrying text, page, bbox and prov:wasDerivedFrom (structural facts; domain
grounding is a later loop, so no PromotionDecision here).
Propose: an iladub:CandidateConcept for regions the loop cannot validate.
"""
from __future__ import annotations

from rdflib import Graph, Namespace, Literal, BNode, URIRef, RDF
from rdflib.namespace import XSD

from .regions import ClassifiedRegion
from .roundtrip import cell_round_trips

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _bbox_node(g: Graph, cell) -> BNode:
    x0, y0, x1, y1 = cell.bbox
    n = BNode()
    g.add((n, RDF.type, TAB.BBox))
    g.add((n, TAB.x0, Literal(round(x0, 2), datatype=XSD.decimal)))
    g.add((n, TAB.y0, Literal(round(y0, 2), datatype=XSD.decimal)))
    g.add((n, TAB.x1, Literal(round(x1, 2), datatype=XSD.decimal)))
    g.add((n, TAB.y1, Literal(round(y1, 2), datatype=XSD.decimal)))
    return n


def _region_uri(base: URIRef, kind: str, idx: int) -> URIRef:
    return URIRef(f"{base}-{kind}{idx}")


def assert_record_region(g: Graph, region: ClassifiedRegion, table_uri: URIRef,
                         doc_uri: URIRef, page: int) -> int:
    g.add((table_uri, RDF.type, TAB.RecordTable))
    ncols = region.grid.ncols
    cols = {i: _region_uri(table_uri, "c", i) for i in range(ncols)}
    for i, c in cols.items():
        g.add((c, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, c))
        h = _region_uri(table_uri, "h", i)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, c))
        g.add((table_uri, TAB.hasHeaderNode, h))

    data_rows = sorted({cell.row for cell in region.cells if cell.row > 0})
    rows = {r: _region_uri(table_uri, "r", r) for r in data_rows}
    for r in rows.values():
        g.add((r, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, r))

    asserted = 0
    b = region.grid.boundaries
    for cell in region.cells:
        if cell.row == 0:
            continue  # header labels are structural, not scored facts
        if not cell_round_trips(cell, b):
            continue  # a straddling cell is not asserted (would be escalated per-cell)
        e = _region_uri(table_uri, f"e{cell.row}_", cell.col)
        g.add((e, RDF.type, TAB.EntryCell))
        g.add((table_uri, TAB.hasCell, e))
        g.add((e, TAB.atColumn, cols[cell.col]))
        g.add((e, TAB.atRow, rows[cell.row]))
        g.add((e, TAB.cellText, Literal(cell.text)))
        g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
        g.add((e, TAB.hasBBox, _bbox_node(g, cell)))
        x0, top, _, _ = cell.bbox
        g.add((e, PROV.wasDerivedFrom,
               URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))
        asserted += 1
    return asserted


def escalate_region(g: Graph, cand_uri: URIRef, doc_uri: URIRef, ascii_text: str,
                    reason: str, anchor: URIRef, confidence: float) -> None:
    g.add((cand_uri, RDF.type, ILADUB.CandidateConcept))
    g.add((cand_uri, ILADUB.surfaceText, Literal(ascii_text)))
    g.add((cand_uri, ILADUB.suggestedAnchor, anchor))
    g.add((cand_uri, DEC.confidence, Literal(round(confidence, 2), datatype=XSD.decimal)))
    g.add((cand_uri, DEC.rationale, Literal(reason)))
    g.add((cand_uri, PROV.wasDerivedFrom, doc_uri))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q tests/etkl/test_holon.py -v`
Expected: 3 passed — the asserted holon conforms to topology + physical SHACL.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/holon.py tests/etkl/test_holon.py
git commit -m "feat(etkl): RDF holon mapper — assert record region, propose escalations"
```

---

### Task 6: `compile.py` — orchestrator, report, score

**Files:**
- Create: `src/iladub/etkl/compile.py`
- Test: `tests/etkl/test_closing_slice.py`

**Interfaces:**
- Consumes: everything above; `extract_words`, `text_lines`, `detect_bands`.
- Produces:
  - `@dataclass(frozen=True) class RegionReport: kind: RegionKind; verdict: str; cells: int; reason: str | None; anchor: str | None; ascii: str`.
  - `@dataclass(frozen=True) class CompilationReport: score: float; regions: tuple[RegionReport, ...]; graph: Graph` with `to_turtle() -> str`.
  - `compile_tables(pdf_path: str, page_number: int = 0, validate_shapes: bool = True) -> CompilationReport`.
  - `RegionKind` re-exported for callers.

- [ ] **Step 1: Write the failing tests** — `tests/etkl/test_closing_slice.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph
from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf
from iladub.etkl import compile_tables, RegionKind
from iladub.etkl.holon import TAB, ILADUB


def test_record_table_closes_score_one(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    assert report.score == 1.0
    assert any(r.kind is RegionKind.RECORD_TABLE and r.verdict == "asserted"
               for r in report.regions)
    # the holon conforms (compile_tables ran SHACL internally when validate_shapes=True)
    assert (None, None, TAB.RecordTable) in report.graph


def test_pivot_escalates_in_band(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert any(r.verdict == "escalated" and r.reason == "KIND_NOT_SUPPORTED"
               for r in report.regions), report.regions
    assert (None, None, ILADUB.CandidateConcept) in report.graph
    assert report.score < 1.0
    # never a fake assertion of the pivot
    assert not any(r.kind is RegionKind.RECORD_TABLE for r in report.regions)


def test_title_excluded_from_score(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    non = [r for r in report.regions if r.kind is RegionKind.NON_TABLE]
    assert non and all(r.cells == 0 for r in non)
    # score is 1.0 despite the title band existing -> prose excluded
    assert report.score == 1.0


def test_report_serializes_and_reparses(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    ttl = report.to_turtle()
    assert Graph().parse(data=ttl, format="turtle")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest -q tests/etkl/test_closing_slice.py -v`
Expected: FAIL (`cannot import name 'compile_tables'`).

- [ ] **Step 3: Implement** — `src/iladub/etkl/compile.py`:

```python
"""compile — the closing slice: PDF -> classify -> round-trip -> score + holon.

compile_tables runs the whole loop on one page and returns a CompilationReport
whose score is asserted_cells / (asserted + escalated) over table-candidate
regions. Non-table regions are reported but excluded from the ratio. Residue is
never dropped: every table-candidate region is asserted or escalated in-band.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, URIRef

from .geometry import extract_words, text_lines
from .bands import detect_bands
from .regions import classify, RegionKind
from .roundtrip import cell_round_trips, render_ascii
from .holon import assert_record_region, escalate_region, TAB

_DOC = URIRef("https://example.org/etkl/doc")


@dataclass(frozen=True)
class RegionReport:
    kind: RegionKind
    verdict: str                 # "asserted" | "escalated" | "ignored"
    cells: int                   # asserted entry-cell count (0 otherwise)
    reason: str | None
    anchor: str | None
    ascii: str


@dataclass(frozen=True)
class CompilationReport:
    score: float
    regions: tuple[RegionReport, ...]
    graph: Graph

    def to_turtle(self) -> str:
        return self.graph.serialize(format="turtle")


def _repo_vocab():
    """Locate vocab/ by walking up from this file (works in-repo/dev checkout)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        cand = os.path.join(d, "vocab")
        if os.path.isdir(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError("vocab/ not found (needed for SHACL validation)")


def _validate(graph: Graph) -> tuple[bool, str]:
    from pyshacl import validate
    v = _repo_vocab()
    shapes = Graph()
    shapes.parse(os.path.join(v, "shapes", "tab-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(v, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    ont = Graph().parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(graph, shacl_graph=shapes, ont_graph=ont,
                                 inference="rdfs", advanced=True)
    return conforms, text


def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True) -> CompilationReport:
    bands = detect_bands(text_lines(extract_words(pdf_path, page_number)))
    graph = Graph()
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    for idx, band in enumerate(bands):
        region = classify(band)
        ascii_view = render_ascii(band)

        if region.kind is RegionKind.NON_TABLE:
            reports.append(RegionReport(region.kind, "ignored", 0,
                                        region.reason, None, ascii_view))
            continue

        if region.kind is RegionKind.RECORD_TABLE:
            table_uri = URIRef(f"{_DOC}#table{idx}")
            n = assert_record_region(graph, region, table_uri, _DOC, page_number)
            total = sum(1 for c in region.cells if c.row > 0)
            escalated_here = total - n
            asserted_total += n
            escalated_total += escalated_here
            reports.append(RegionReport(region.kind, "asserted", n, None,
                                        str(TAB.RecordTable), ascii_view))
        else:  # UNSUPPORTED_TABLE
            cand_uri = URIRef(f"{_DOC}#region{idx}")
            escalate_region(graph, cand_uri, _DOC, ascii_view,
                            reason="KIND_NOT_SUPPORTED",
                            anchor=TAB.HierarchicalTable, confidence=0.4)
            tokens = sum(len(ln.words) for ln in band.lines)
            escalated_total += tokens
            reports.append(RegionReport(region.kind, "escalated", 0,
                                        "KIND_NOT_SUPPORTED",
                                        str(TAB.HierarchicalTable), ascii_view))

    denom = asserted_total + escalated_total
    score = 1.0 if denom == 0 else asserted_total / denom

    if validate_shapes and (None, None, TAB.RecordTable) in graph:
        conforms, text = _validate(graph)
        if not conforms:
            raise AssertionError(f"asserted holon failed tab: SHACL:\n{text}")

    return CompilationReport(score, tuple(reports), graph)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q tests/etkl/test_closing_slice.py -v`
Expected: 4 passed — the loop closes (score 1.0 on the record table, pivot escalated in-band, prose excluded, serializes).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): compile_tables — closing slice (score + in-band escalation)"
```

---

### Task 7: Public API exports + full-suite green

**Files:**
- Modify: `src/iladub/etkl/__init__.py`
- Test: whole suite

**Interfaces:**
- Produces: `compile_tables`, `CompilationReport`, `RegionReport`, `RegionKind`, `Cell` exported from `iladub.etkl`.

- [ ] **Step 1: Write the failing test** — `tests/etkl/test_api.py`:

```python
def test_public_api_exports():
    import iladub.etkl as e
    for name in ["compile_tables", "CompilationReport", "RegionReport",
                 "RegionKind", "Cell"]:
        assert hasattr(e, name), f"missing export: {name}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q tests/etkl/test_api.py -v`
Expected: FAIL (`missing export: compile_tables`).

- [ ] **Step 3: Update exports** — replace `src/iladub/etkl/__init__.py`:

```python
"""iladub ET(K)L compiler — deterministic multimodal extraction.

increment 1a: geometry -> bands -> body leaf-grid.
closing slice: classify -> round-trip -> validated table-holon + score.
"""

from .geometry import Word, Line, extract_words, text_lines
from .bands import Band, detect_bands
from .grid import LeafGrid, infer_leaf_grid
from .regions import RegionKind, Cell, ClassifiedRegion, classify, assign_cells, column_of
from .roundtrip import cell_round_trips, render_ascii
from .compile import compile_tables, CompilationReport, RegionReport

__all__ = [
    "Word", "Line", "extract_words", "text_lines",
    "Band", "detect_bands",
    "LeafGrid", "infer_leaf_grid",
    "RegionKind", "Cell", "ClassifiedRegion", "classify", "assign_cells", "column_of",
    "cell_round_trips", "render_ascii",
    "compile_tables", "CompilationReport", "RegionReport",
]
```

- [ ] **Step 4: Run the whole suite**

Run: `pytest -q`
Expected: all etkl + tab tests pass. (Pre-existing BAML tests may error on the local `baml-py` version drift — unrelated to this work; confirm no NEW failures in `tests/etkl` or `tests/test_tab.py`.)

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/__init__.py tests/etkl/test_api.py
git commit -m "feat(etkl): export the closing-slice public API"
```

---

### Task 8: Update the loop canvas (close the paper trail)

**Files:**
- Modify: `docs/loops/2026-07-05-table-holon-loop.md`

**Interfaces:** none (docs).

- [ ] **Step 1: Record the closed increment** — under the `## Rollout` section, mark L1 done for the record kind and list the field-of-possibles remaining (so nothing is a silent gap):

```markdown
### Increments (status)
- [x] **1 — record-table closing slice** (2026-07-05): flat record table compiled end-to-end to a
      validated `tab:` holon with a score; every other region escalated in-band as an
      `iladub:CandidateConcept`. Closes the loop at L1 for the record kind.
- [ ] Field of possibles (each a future increment, escalated today): multi-level/merged headers
      (pivot/hierarchical) · matrix/cross-tab · key-value · stacked · multi-word headers ·
      **multi-band tables (header banded away from body — needs band-grouping)** ·
      measured-vs-reconstructed ASCII diff view · domain grounding (value → LOINC/UCUM) ·
      retry/repair control · cross-run STATE ledger.
```

- [ ] **Step 2: Commit**

```bash
git add docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loops): mark record-table closing slice done; list field-of-possibles"
```

---

## Self-Review

**Spec coverage:** §1 scope → Task 6 tests. §2 architecture → Tasks 3–6 (one module each). §3 header-regularity gate + per-cell → Task 3 (`classify`) + Task 4 (`cell_round_trips`, unit-proven). §4 physical layer → Task 1 (terms) + Task 2 (shape). §5 assert/propose RDF → Task 5. §6 score (token-based, prose excluded) → Task 6 (`compile_tables`, `test_title_excluded_from_score`). §7 six proofs → Tasks 4/6 tests (record closes, pivot escalates, cell-gate bites, wide-cell collapses, serializes, physical-shape negative). §8 out-of-scope → Task 8 canvas list. **No gaps.**

**Placeholder scan:** none — every step carries full code and exact commands.

**Type consistency:** `Cell(row, col, words)` and `.text`/`.bbox` used identically in Tasks 3/4/5. `classify → ClassifiedRegion(kind, band, grid, cells, reason)` consumed unchanged in Task 6. `cell_round_trips(cell, boundaries)` signature identical in Tasks 4/5. `TAB/ILADUB/DEC/PROV` defined once in `holon.py`, imported elsewhere. `compile_tables(pdf_path, page_number=0, validate_shapes=True) → CompilationReport(score, regions, graph)` consistent across Task 6/7.
