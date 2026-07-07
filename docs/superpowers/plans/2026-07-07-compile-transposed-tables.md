# Compile Transposed Tables (axis-flip) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a detected transposed table into a correct, un-inverted `tab:RecordTable` by axis-flip, guarded by a second (coherence) oracle, with provenance-to-the-page preserved.

**Architecture:** The axis-flip is a *logical relabel* over unmoved physical cells — logical column `k` ← physical row `k` (header label = physical col-0 cell), logical row `m` ← physical column `m ≥ 1`, EntryCell (row `m`, col `k`) ← physical cell `O[k][m]` carrying its own measured words. Certification reuses the existing per-cell `cell_round_trips` on the original grid + the existing `tab:` SHACL. A new `transpose_is_coherent` oracle decides compile-vs-escalate, so a false-positive detection escalates instead of asserting an inverted table.

**Tech Stack:** Python 3, rdflib, pdfplumber/reportlab (test fixtures), pyshacl (validation), pytest.

## Global Constraints

- **Source ownership:** `vocab/ontology/tab.ttl` stays standalone — every triple's subject is a `tab:` term; **zero** `w3id.org/holon` references. (CI-enforced by `tests/test_source_ownership.py`.)
- **No silent-wrong / close-or-escalate:** compilation asserts only what round-trips per cell; a cell that straddles a gutter escalates `ROUND_TRIP_FAIL` (never dropped); a detected-but-incoherent region escalates `TRANSPOSED` (never asserts an inverted table).
- **No overfitting:** oracles are structural (type-homogeneity via `headers.is_numeric`, geometric round-trip), never constants tuned to a fixture.
- **Provenance-to-the-page:** every emitted cell's `hasBBox`/`onPage`/`wasDerivedFrom` derives from the *original physical* `Cell` (its measured `words`), never a flipped coordinate.
- **DRY:** the upright and transposed makers share one entry-cell emitter and one round-trip-fail emitter; no verbatim duplication of the emission block.
- The compiled holon's logical kind is `tab:RecordTable` + `tab:sourceOrientation "transposed"` (a plain xsd:string controlled value).

---

### Task 1: `transpose_is_coherent` oracle

**Files:**
- Modify: `src/iladub/etkl/orientation.py`
- Create fixture: `tests/etkl/fixtures.py` (append `false_transposed_pdf`)
- Test: `tests/etkl/test_orientation.py`

**Interfaces:**
- Consumes: `headers.is_numeric(str) -> bool`; a `ClassifiedRegion` with `.cells` (each `Cell` has `.row:int`, `.col:int`, `.text:str`).
- Produces: `transpose_is_coherent(region) -> bool` — True iff **every** physical row's cells in columns `≥ 1` are type-homogeneous (all `is_numeric` or all not). This is the compile gate's second oracle; `looks_transposed` (detection) is unchanged.

**Design note (why ALL rows, including row 0):** in a transposed table every physical row is a *field* (row 0 is the record-identifier field, e.g. `Name → Alice, Bob`). A genuine transposed table has type-coherent field-rows; a coincidentally-flagged upright *record* table has at least one row that mixes a text label/number/unit (fails homogeneity). Rows whose only cell is column 0 (no value columns) are vacuously coherent.

- [ ] **Step 1: Write the failing test**

Append to `tests/etkl/test_orientation.py` (it already imports `transposed_table_pdf`, `simple_table_pdf`, `classify`, and defines `_region`):

```python
from tests.etkl.fixtures import all_text_table_pdf, false_transposed_pdf
from iladub.etkl.orientation import transpose_is_coherent


def test_transposed_is_coherent(tmp_path):
    # every field-row (Name/Age/City) is type-homogeneous across the record columns
    assert transpose_is_coherent(_region(transposed_table_pdf, tmp_path)) is True


def test_normal_record_not_coherent(tmp_path):
    # simple_table rows are records (e.g. "Hemoglobin 13.2 g/dL") -> mixed types -> not coherent
    assert transpose_is_coherent(_region(simple_table_pdf, tmp_path)) is False


def test_false_positive_detected_but_not_coherent(tmp_path):
    # trips looks_transposed (a numeric row, no numeric column) BUT the 'Mix' row
    # is type-mixed (5 numeric, ok text) -> coherence is False -> must NOT compile
    region = _region(false_transposed_pdf, tmp_path)
    assert looks_transposed(region) is True
    assert transpose_is_coherent(region) is False
```

Add `looks_transposed` to the existing import line in the test file if not already imported (it is imported at module top).

- [ ] **Step 2: Add the `false_transposed_pdf` fixture**

Append to `tests/etkl/fixtures.py`:

```python
def false_transposed_pdf(path: str) -> dict:
    """Trips looks_transposed (the 'Count' row is all-numeric across cols, and NO
    column is all-numeric) yet is NOT a genuine transposition: the 'Mix' row is
    type-mixed (5 numeric, ok text), so transpose_is_coherent is False. Guards the
    compile-direction silent-wrong: a false-positive detection must ESCALATE, not
    compile an inverted RecordTable."""
    cols = [72.0, 240.0, 400.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Item", "A", "B"), ("Count", "10", "20"),
            ("Note", "hi", "bye"), ("Mix", "5", "ok")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_orientation.py -q`
Expected: FAIL with `ImportError: cannot import name 'transpose_is_coherent'`.

- [ ] **Step 4: Implement `transpose_is_coherent`**

Append to `src/iladub/etkl/orientation.py`:

```python
def transpose_is_coherent(region) -> bool:
    """True iff EVERY physical row is type-homogeneous across its value columns
    (columns >= 1) — the signature of a genuine transposition, where each row is a
    single-typed field. The second oracle of the compile gate: `looks_transposed`
    detects, `transpose_is_coherent` decides whether to compile.

    A coincidentally-flagged upright record table has rows that mix a text label, a
    number and a unit, so at least one row is not homogeneous and this returns
    False — the region is then escalated (detect-and-escalate stays the floor),
    never compiled into an inverted table. Rows with no value column (only col 0)
    are vacuously coherent.
    """
    rows: dict[int, list[str]] = {}
    for c in region.cells:
        if c.col >= 1:
            rows.setdefault(c.row, []).append(c.text)
    for vals in rows.values():
        if vals and not (all(is_numeric(v) for v in vals)
                         or all(not is_numeric(v) for v in vals)):
            return False
    return True
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_orientation.py -q`
Expected: PASS (all orientation tests, old + new).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/orientation.py tests/etkl/fixtures.py tests/etkl/test_orientation.py
git commit -m "feat(etkl): transpose_is_coherent — the compile-gate's second oracle"
```

---

### Task 2: axis-flip maker + shared emitters + ontology

**Files:**
- Modify: `src/iladub/etkl/holon.py`
- Modify: `vocab/ontology/tab.ttl`
- Test: `tests/etkl/test_holon.py`, `tests/test_tab.py`

**Interfaces:**
- Consumes: `roundtrip.cell_round_trips(cell, boundaries)`; `_bbox_node(g, cell)`, `_region_uri(base, kind, idx)` (existing in `holon.py`); a `ClassifiedRegion` with `.cells` and `.grid.boundaries`.
- Produces:
  - `_emit_entry_cell(g, table_uri, doc_uri, page, e_uri, col_uri, row_uri, cell) -> None` — the shared EntryCell triple block.
  - `_emit_roundtrip_fail_cell(g, doc_uri, page, cc_uri, cell) -> None` — the shared ROUND_TRIP_FAIL CandidateConcept block.
  - `assert_transposed_region(g, region, table_uri, doc_uri, page) -> int` — emits a `tab:RecordTable` (with `tab:sourceOrientation "transposed"`) from the axis-flip; returns the asserted EntryCell count.
  - `tab:sourceOrientation` datatype property in `tab.ttl`.

**Flip mapping (the whole design in one line):** logical column `k` ← physical row `k` (header label = cell `(k, 0)`); logical row `m` ← physical column `m ≥ 1`; EntryCell `(row m, col k)` ← physical cell `(row k, col m)`, carrying that cell's own `words` so bbox/page/provenance are the true physical measurement.

- [ ] **Step 1: Write the failing tests (maker structure, provenance, straddle)**

Append to `tests/etkl/test_holon.py`:

```python
from rdflib import Graph, URIRef, Literal, RDF
from iladub.etkl.geometry import Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.regions import Cell, ClassifiedRegion, RegionKind
from iladub.etkl.holon import assert_transposed_region, TAB, ILADUB, DEC, PROV


def _word(text, x0, x1, top=100.0, bottom=110.0):
    return Word(text=text, x0=x0, x1=x1, top=top, bottom=bottom, page=0)


def _cell(row, col, text, x0, x1, top):
    return Cell(row=row, col=col, words=(_word(text, x0, x1, top, top + 10.0),))


def _transposed_region(straddle=False):
    # 3 physical cols (Field | rec1 | rec2), boundaries at 60/220/380/540.
    grid = LeafGrid(boundaries=(60.0, 220.0, 380.0, 540.0), ncols=3, pitch=160.0, confidence=1.0)
    cells = [
        _cell(0, 0, "Field", 60.0, 110.0, 100.0),
        _cell(0, 1, "Alice", 220.0, 270.0, 100.0),
        _cell(0, 2, "Bob", 380.0, 420.0, 100.0),
        _cell(1, 0, "Age", 60.0, 100.0, 120.0),
        _cell(1, 1, "30", 220.0, 250.0, 120.0),
        _cell(1, 2, "25", 380.0, 410.0, 120.0),
        _cell(2, 0, "City", 60.0, 110.0, 140.0),
        # straddle=True makes this value cross the 380 gutter (x1=420 > 380)
        _cell(2, 1, "NYC", 350.0 if straddle else 220.0, 420.0 if straddle else 270.0, 140.0),
        _cell(2, 2, "LA", 380.0, 410.0, 140.0),
    ]
    return ClassifiedRegion(RegionKind.RECORD_TABLE, None, grid, tuple(cells), "test")


def test_transposed_maker_builds_record_table():
    g = Graph()
    t = URIRef("https://example.org/t")
    n = assert_transposed_region(g, _transposed_region(), t, URIRef("https://example.org/doc"), 0)
    assert (t, RDF.type, TAB.RecordTable) in g
    assert (t, TAB.sourceOrientation, Literal("transposed")) in g
    # header labels come from physical column 0 (read down): Field, Age, City
    labels = {str(o) for s in g.subjects(RDF.type, TAB.LabelCell)
              for o in g.objects(s, TAB.cellText)}
    assert {"Field", "Age", "City"} <= labels
    # 3 logical cols, 2 logical rows (records), 6 entry cells
    assert len(list(g.subjects(RDF.type, TAB.LeafColumn))) == 3
    assert len(list(g.subjects(RDF.type, TAB.LeafRow))) == 2
    assert n == 6


def test_transposed_provenance_is_physical():
    g = Graph()
    t = URIRef("https://example.org/t")
    assert_transposed_region(g, _transposed_region(), t, URIRef("https://example.org/doc"), 0)
    # the entry carrying "30" must keep the PHYSICAL bbox of the "30" word (x0=220),
    # not a flipped coordinate.
    e = next(s for s in g.subjects(RDF.type, TAB.EntryCell)
             if str(next(g.objects(s, TAB.cellText))) == "30")
    bb = next(g.objects(e, TAB.hasBBox))
    assert float(next(g.objects(bb, TAB.x0))) == 220.0
    assert int(next(g.objects(e, TAB.onPage))) == 0


def test_transposed_straddle_escalates_that_cell():
    g = Graph()
    t = URIRef("https://example.org/t")
    n = assert_transposed_region(g, _transposed_region(straddle=True), t,
                                 URIRef("https://example.org/doc"), 0)
    # the straddling value cell is NOT asserted; it becomes a ROUND_TRIP_FAIL proposition
    assert n == 5
    rationales = {str(o) for s in g.subjects(RDF.type, ILADUB.CandidateConcept)
                  for o in g.objects(s, DEC.rationale)}
    assert "ROUND_TRIP_FAIL" in rationales
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py -q -k transposed`
Expected: FAIL with `ImportError: cannot import name 'assert_transposed_region'`.

- [ ] **Step 3: Extract the shared emitters (refactor `assert_record_region`)**

In `src/iladub/etkl/holon.py`, add these two helpers (place them above `assert_record_region`):

```python
def _emit_entry_cell(g: Graph, table_uri: URIRef, doc_uri: URIRef, page: int,
                     e_uri: URIRef, col_uri: URIRef, row_uri: URIRef, cell) -> None:
    """Emit one tab:EntryCell with structural links + provenance. Shared by the
    upright and transposed makers so provenance is single-sourced."""
    g.add((e_uri, RDF.type, TAB.EntryCell))
    g.add((table_uri, TAB.hasCell, e_uri))
    g.add((e_uri, TAB.atColumn, col_uri))
    g.add((e_uri, TAB.atRow, row_uri))
    g.add((e_uri, TAB.cellText, Literal(cell.text)))
    g.add((e_uri, TAB.onPage, Literal(page, datatype=XSD.integer)))
    g.add((e_uri, TAB.hasBBox, _bbox_node(g, cell)))
    x0, top, _, _ = cell.bbox
    g.add((e_uri, PROV.wasDerivedFrom,
           URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))


def _emit_roundtrip_fail_cell(g: Graph, doc_uri: URIRef, page: int,
                              cc_uri: URIRef, cell) -> None:
    """Emit a ROUND_TRIP_FAIL proposition for a data cell whose ink crosses a
    gutter — never silently dropped. Shared by both makers."""
    x0, top, _, _ = cell.bbox
    g.add((cc_uri, RDF.type, ILADUB.CandidateConcept))
    g.add((cc_uri, ILADUB.surfaceText, Literal(cell.text)))
    g.add((cc_uri, DEC.rationale, Literal("ROUND_TRIP_FAIL")))
    g.add((cc_uri, TAB.onPage, Literal(page, datatype=XSD.integer)))
    g.add((cc_uri, TAB.hasBBox, _bbox_node(g, cell)))
    g.add((cc_uri, PROV.wasDerivedFrom,
           URIRef(f"{doc_uri}#p{page}-{int(x0)}-{int(top)}")))
```

Then in `assert_record_region`, replace the body-cell `if not cell_round_trips(...)` block and the trailing EntryCell block with calls to the two helpers. The loop's data-cell branch becomes:

```python
        if not cell_round_trips(cell, b):
            cc = _region_uri(table_uri, f"cc{cell.row}_", cell.col)
            _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
            continue
        e = _region_uri(table_uri, f"e{cell.row}_", cell.col)
        _emit_entry_cell(g, table_uri, doc_uri, page, e, cols[cell.col], rows[cell.row], cell)
        asserted += 1
```

(The header/LabelCell branch at `cell.row == 0` is unchanged.)

- [ ] **Step 4: Verify the refactor is behaviour-preserving**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py tests/etkl/test_closing_slice.py -q`
Expected: PASS (existing record-path tests unchanged — the new transposed tests still fail on the missing maker; that is expected until Step 5).

- [ ] **Step 5: Implement `assert_transposed_region`**

Append to `src/iladub/etkl/holon.py`:

```python
def assert_transposed_region(g: Graph, region: ClassifiedRegion, table_uri: URIRef,
                             doc_uri: URIRef, page: int) -> int:
    """Compile a detected transposed region into an un-inverted tab:RecordTable by
    axis-flip. The flip is a LOGICAL relabel over unmoved physical cells: logical
    column k <- physical row k (header label = cell (k,0)); logical row m <-
    physical column m>=1; EntryCell (row m, col k) <- physical cell (row k, col m),
    carrying that cell's own words so bbox/page/provenance are the true physical
    measurement, never a flipped coordinate. Certification is the SAME per-cell
    round-trip on the ORIGINAL grid; straddling cells escalate ROUND_TRIP_FAIL.
    Returns the asserted EntryCell count.
    """
    g.add((table_uri, RDF.type, TAB.RecordTable))
    g.add((table_uri, TAB.sourceOrientation, Literal("transposed")))
    b = region.grid.boundaries

    by_rc = {(c.row, c.col): c for c in region.cells}
    phys_rows = sorted({c.row for c in region.cells})              # -> logical columns
    phys_cols = sorted({c.col for c in region.cells if c.col >= 1})  # -> logical rows

    cols = {}
    for k in phys_rows:
        col_uri = _region_uri(table_uri, "c", k)
        cols[k] = col_uri
        g.add((col_uri, RDF.type, TAB.LeafColumn))
        g.add((table_uri, TAB.hasLeafColumn, col_uri))
        h = _region_uri(table_uri, "h", k)
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((h, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
        g.add((h, TAB.coversColumn, col_uri))
        g.add((table_uri, TAB.hasHeaderNode, h))
        label = by_rc.get((k, 0))
        if label is not None:
            lc = _region_uri(table_uri, "lc", k)
            g.add((lc, RDF.type, TAB.LabelCell))
            g.add((table_uri, TAB.hasCell, lc))
            g.add((lc, TAB.cellText, Literal(label.text)))
            g.add((lc, TAB.onPage, Literal(page, datatype=XSD.integer)))
            g.add((lc, TAB.hasBBox, _bbox_node(g, label)))
            g.add((h, TAB.hasLabel, lc))

    rows = {}
    for m in phys_cols:
        row_uri = _region_uri(table_uri, "r", m)
        rows[m] = row_uri
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))

    asserted = 0
    for k in phys_rows:
        for m in phys_cols:
            cell = by_rc.get((k, m))
            if cell is None:
                continue
            if cell_round_trips(cell, b):
                e = _region_uri(table_uri, f"e{m}_", k)
                _emit_entry_cell(g, table_uri, doc_uri, page, e, cols[k], rows[m], cell)
                asserted += 1
            else:
                cc = _region_uri(table_uri, f"cc{m}_", k)
                _emit_roundtrip_fail_cell(g, doc_uri, page, cc, cell)
    return asserted
```

Ensure `cell_round_trips` is imported at the top of `holon.py` (it already imports `from .roundtrip import cell_round_trips`).

- [ ] **Step 6: Add `tab:sourceOrientation` to the ontology + refine the TransposedTable comment**

In `vocab/ontology/tab.ttl`, replace the `tab:TransposedTable` comment (line ~89) so it no longer says "not yet compiled", and add the property immediately after:

```turtle
tab:TransposedTable a owl:Class ; rdfs:subClassOf tab:Table ;
    rdfs:label "Transposed table"@en ;
    rdfs:comment "A table whose records run along columns and whose fields run down the first column (rows are attributes). Compiled by axis-flip into a tab:RecordTable with tab:sourceOrientation \"transposed\"; also the escalation anchor when a detected transposition is not confidently compilable."@en .

tab:sourceOrientation a owl:DatatypeProperty ;
    rdfs:domain tab:Table ; rdfs:range xsd:string ;
    rdfs:label "source orientation"@en ;
    rdfs:comment "The physical orientation of the source region a table-holon was recovered from: \"transposed\" when records ran along physical columns and the holon was recovered by axis-flip. Absent means upright. The holon's logical kind is unaffected."@en .
```

- [ ] **Step 7: Add the ontology term-presence test**

Append to `tests/test_tab.py` (follow the file's existing term-check style; adapt the graph-loading fixture already used there):

```python
def test_tab_sourceorientation_term():
    from rdflib import Graph, RDF, RDFS, OWL, Namespace, URIRef
    TAB = Namespace("https://w3id.org/iladub/tab#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    g = Graph().parse("vocab/ontology/tab.ttl", format="turtle")
    assert (TAB.sourceOrientation, RDF.type, OWL.DatatypeProperty) in g
    assert (TAB.sourceOrientation, RDFS.domain, TAB.Table) in g
    assert (TAB.sourceOrientation, RDFS.range, XSD.string) in g
```

If `tests/test_tab.py` already defines a shared graph fixture/loader, reuse it instead of re-parsing.

- [ ] **Step 8: Run tests to verify they pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_holon.py tests/test_tab.py tests/test_source_ownership.py -q`
Expected: PASS (maker structure, provenance-physical, straddle-escalates, term present, ownership intact).

- [ ] **Step 9: Commit**

```bash
git add src/iladub/etkl/holon.py vocab/ontology/tab.ttl tests/etkl/test_holon.py tests/test_tab.py
git commit -m "feat(etkl): assert_transposed_region (axis-flip maker) + tab:sourceOrientation; DRY entry-cell emitters"
```

---

### Task 3: wire the two-oracle compile gate

**Files:**
- Modify: `src/iladub/etkl/compile.py:88-107` (the `looks_transposed` branch inside `RECORD_TABLE`)
- Modify: `src/iladub/etkl/__init__.py` (exports)
- Test: `tests/etkl/test_closing_slice.py` (update the now-contradicting test; add compile/false-positive/provenance tests)

**Interfaces:**
- Consumes: `orientation.looks_transposed`, `orientation.transpose_is_coherent`, `holon.assert_transposed_region`, `roundtrip.cell_round_trips`.
- Produces: `compile_tables` now compiles a coherent transposed region to a `tab:RecordTable` (score by round-tripping value tokens) and still escalates an incoherent one as `TRANSPOSED`.

- [ ] **Step 1: Update the existing test that now contradicts the new behaviour, and add the new tests**

In `tests/etkl/test_closing_slice.py`, **replace** `test_transposed_escalates_not_asserted` (lines ~79-90) with:

```python
def test_transposed_now_compiles(tmp_path):
    # Loop 4: the transposed table Loop 3 escalated now COMPILES by axis-flip.
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl.holon import TAB, ILADUB
    from rdflib import RDF, Literal
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) in report.graph
    t = next(report.graph.subjects(RDF.type, TAB.RecordTable))
    assert (t, TAB.sourceOrientation, Literal("transposed")) in report.graph
    # header recovered from physical column 0: Name, Age, City
    labels = {str(o) for s in report.graph.subjects(RDF.type, TAB.LabelCell)
              for o in report.graph.objects(s, TAB.cellText)}
    assert {"Name", "Age", "City"} <= labels
    # 2 records (Alice, Bob) -> 2 leaf rows; no TRANSPOSED escalation
    assert len(list(report.graph.subjects(RDF.type, TAB.LeafRow))) == 2
    assert (None, None, ILADUB.CandidateConcept) not in report.graph
    assert report.score == 1.0


def test_false_positive_transpose_escalates(tmp_path):
    # a region that trips looks_transposed but is NOT coherent must ESCALATE, not
    # compile an inverted RecordTable (the compile-direction silent-wrong guard).
    from tests.etkl.fixtures import false_transposed_pdf
    from iladub.etkl.holon import TAB, ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "fp.pdf"; false_transposed_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) not in report.graph
    cand = next(report.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert str(next(report.graph.objects(cand, DEC.rationale))) == "TRANSPOSED"


def test_transposed_provenance_survives_flip(tmp_path):
    # Alice's Age value "30" must trace to the PHYSICAL "30" word on the page,
    # proving the flip is a logical relabel, not a coordinate transform.
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl import extract_words
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    word30 = next(w for w in extract_words(str(p)) if w.text == "30")
    report = compile_tables(str(p))
    e = next(s for s in report.graph.subjects(RDF.type, TAB.EntryCell)
             if str(next(report.graph.objects(s, TAB.cellText))) == "30")
    bb = next(report.graph.objects(e, TAB.hasBBox))
    assert abs(float(next(report.graph.objects(bb, TAB.x0))) - word30.x0) < 0.01
    assert int(next(report.graph.objects(e, TAB.onPage))) == 0
```

Leave `test_normal_table_still_compiles` and `test_all_text_record_not_flagged_transposed` unchanged — they are the regression guards.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_closing_slice.py -q -k "transposed or false_positive"`
Expected: FAIL — `test_transposed_now_compiles` finds no RecordTable (still escalates), because the gate isn't wired yet.

- [ ] **Step 3: Wire the two-oracle gate in `compile.py`**

In `src/iladub/etkl/compile.py`, replace the current `looks_transposed` block (the `if looks_transposed(region):` … escalate branch, ~lines 88-98) with:

```python
            from .orientation import looks_transposed, transpose_is_coherent
            if looks_transposed(region):
                if transpose_is_coherent(region):
                    # compile by axis-flip: records run along columns -> a correct,
                    # un-inverted RecordTable (tab:sourceOrientation "transposed").
                    from .holon import assert_transposed_region
                    table_uri = URIRef(f"{_DOC}#ttable{idx}")
                    n = assert_transposed_region(graph, region, table_uri, _DOC, page_number)
                    b = region.grid.boundaries
                    value_cells = [c for c in region.cells if c.col >= 1]
                    asserted_total += sum(len(c.words) for c in value_cells if cell_round_trips(c, b))
                    escalated_total += sum(len(c.words) for c in value_cells if not cell_round_trips(c, b))
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.RecordTable), ascii_view))
                else:
                    # detected but not confidently compilable — escalate (Loop 3 behaviour)
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "TRANSPOSED",
                                    TAB.TransposedTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "TRANSPOSED",
                                                str(TAB.TransposedTable), ascii_view))
            else:
```

(The `else:` opens the existing unchanged upright RECORD_TABLE assert block that follows.)

- [ ] **Step 4: Update `__init__.py` exports**

In `src/iladub/etkl/__init__.py`: change the orientation import to
`from .orientation import looks_transposed, transpose_is_coherent`, add
`from .holon import assert_record_region, assert_transposed_region` (if `assert_record_region` is not already exported, add it too), and add `"looks_transposed", "transpose_is_coherent", "assert_transposed_region"` to `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/ tests/test_tab.py -q`
Expected: PASS (compile, false-positive escalate, provenance, plus all regressions).

- [ ] **Step 6: Full-suite regression check**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS (all green; no pre-existing test broken by the refactor or the gate).

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): two-oracle compile gate — compile coherent transposed tables, escalate the rest"
```

---

### Task 4: showcase Part E (escalate → compile) + canvas increment 4

**Files:**
- Modify: `demo/etkl_1a_showcase.ipynb` (Part E)
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (increments list)

**Interfaces:** Consumes the shipped `compile_tables` behaviour (transposed → compiled RecordTable). No new code.

**Note:** the demo fixture `demo/etkl_demo_data.py::transposed_report_pdf` (Field/Age/Sex/City, mixed types) already compiles under the new gate — Age numeric, Sex/City text, all field-rows homogeneous → coherent. Verify, don't rebuild it.

- [ ] **Step 1: Replace Part E's escalate cell with a compile cell**

In `demo/etkl_1a_showcase.ipynb`, keep the Part E intro markdown and the "render the original PDF first" cell (`tr_pdf`) unchanged. Replace the escalate code cell (the one printing `score` / `RecordTable asserted` / `verdict: escalated`) with this exact cell body — a read-out of the recovered structure:

```python
from iladub.etkl.holon import TAB
from rdflib import RDF
tr = compile_tables(tr_pdf)
rec = next(tr.graph.subjects(RDF.type, TAB.RecordTable))
orientation = str(next(tr.graph.objects(rec, TAB.sourceOrientation)))
labels = sorted(str(o) for s in tr.graph.subjects(RDF.type, TAB.LabelCell)
                for o in tr.graph.objects(s, TAB.cellText))
print(f"score = {tr.score:.2f}   |   RecordTable asserted: True   |   sourceOrientation: {orientation}")
print("recovered header fields:", ", ".join(labels))
print("entry cells:", len(list(tr.graph.subjects(RDF.type, TAB.EntryCell))))
```

- [ ] **Step 2: Update the Part E closing markdown with the "so what"**

Rewrite the Part E closing markdown cell to state: *the same transposed table Loop 3 could only flag, Loop 4 compiles correctly by axis-flip — and every value still traces to its original position on the page (provenance survived the flip). Detection (`looks_transposed`) plus a coherence oracle (`transpose_is_coherent`) gate the compile so a false positive escalates rather than inverting.*

- [ ] **Step 3: Re-run the notebook in place; verify zero errors**

Run:
```bash
PYTHONPATH="$PWD/src:$PWD/demo" jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 --ExecutePreprocessor.kernel_name=python3 \
  demo/etkl_1a_showcase.ipynb
```
Then verify: 0 error outputs, Part E renders the original transposed PDF, and prints `score = 1.00 | RecordTable asserted: True | sourceOrientation: transposed` with the recovered header fields. (Use a JSON scan of the notebook outputs, as in the Loop 3 verification.)

- [ ] **Step 4: Add increment 4 to the loop canvas**

In `docs/loops/2026-07-05-table-holon-loop.md`, add to the Increments list (after increment 3):

```markdown
- [x] **4 — compile transposed tables (axis-flip)** (2026-07-07): a detected transposed table
      now COMPILES into a correct, un-inverted `tab:RecordTable` (`tab:sourceOrientation
      "transposed"`) by axis-flip — a logical relabel over unmoved physical cells, so
      provenance-to-the-page survives. A second oracle (`transpose_is_coherent`: every field-row
      is type-homogeneous) gates the compile against the reverse silent-wrong; a detected-but-
      incoherent region still escalates `TRANSPOSED`. Closes the detect→compile arc opened by
      increment 3. (Delivered by the compile-transposed-tables PR.)
```

And remove "compile transposed tables (axis-flip …)" from the field-of-possibles bullet (the `[ ]` line), leaving row-header hierarchies (`tab:coversRow`) et al.

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_1a_showcase.ipynb docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop4): showcase Part E escalate->compile + canvas increment 4"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §2 coherence gate → Task 1; §3 flip + §5 maker/ontology → Task 2; §4 round-trip + §6 gate/tests → Task 3; §7 showcase → Task 4. §6.1 `test_transposed_now_compiles`, §6.2 `test_transposed_is_coherent`/`test_normal_record_not_coherent`/`test_false_positive_detected_but_not_coherent`, §6.3 `test_false_positive_transpose_escalates`, §6.4 `test_transposed_provenance_*`, §6.5 `test_transposed_straddle_escalates_that_cell`, §6.6 unchanged regression tests, §6.7 `test_tab_sourceorientation_term`. All covered.
- **Type consistency:** `assert_transposed_region(g, region, table_uri, doc_uri, page) -> int` and `transpose_is_coherent(region) -> bool` used identically across tasks; `_emit_entry_cell`/`_emit_roundtrip_fail_cell` signatures match their call sites in both makers.
- **Placeholder scan:** none — every code step shows the exact content to write.
- **Pre-flight conflict (flagged to the human):** `test_transposed_escalates_not_asserted` asserts the Loop 3 escalation; Task 3 Step 1 replaces it with `test_transposed_now_compiles`. This is a deliberate behaviour change, approved by the spec.
