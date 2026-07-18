# Declarative Kind Classification (Loop B2c) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift `iladub.etkl.regions.classify`'s entire kind decision (NON_TABLE / UNSUPPORTED / RECORD) from a Python geometry cascade into a SPARQL derivation over a new pre-holon band-classification evidence graph — a byte-identical faithful lift gated by a differential oracle.

**Architecture:** A thin PROCEDURAL emitter (`classifygraph.py`) turns a band + its leaf grid into an RDF evidence graph (`tab:ClassifyBand` line/column counts + one `tab:HeaderWord` per header word with its strict-containment column). One holon-scoped SPARQL `SELECT` (`classify-kind.rq`) derives the kind plus two auxiliary scalars (`nhw`, `firstBad`) the reader uses to rebuild the exact legacy reason string. `classify` is rewired to emit → query → rebuild reason → (RECORD) `assign_cells`; all geometry (`infer_leaf_grid`, `_word_in_column`, `column_of`, `assign_cells`) and the `ClassifiedRegion`/`RegionKind`/`Cell` shapes are unchanged.

**Tech Stack:** Python 3, rdflib (SPARQL 1.1), pytest. Reference impl language = Python.

## Global Constraints

- **CLAUDE.md §8 (neurosymbolic-first gate):** the kind decision is **AXIOM** — it lives entirely in `vocab/queries/classify-kind.rq` (standard SPARQL 1.1, no bespoke functions, **no tuned constant**). The emitter/runner is **PROCEDURAL** engine glue with no decision logic. `_word_in_column`/`column_of`/`infer_leaf_grid` stay **PROCEDURAL** (raw geometric extraction — the audit's "Honest PROCEDURAL boundaries" names `_word_in_column` explicitly). Open-world derivation, not SHACL: the band **is** the holon; all `COUNT`/`NOT EXISTS`/`MIN` are query-local (holon-scoped closure).
- **Faithful lift — behaviour must NOT change.** `classify` feeds the whole compile; its output (`kind`, `grid`, `cells`, `reason`) must be byte-identical to today's for every band. Any downstream test diff is a regression to investigate, never to accept.
- **Source ownership:** every new term is an owned `tab:` individual/class in the standalone `vocab/ontology/tab.ttl` (zero `w3id.org/holon` references). Every triple's subject is a `tab:`/`_ev:` term we own; the `.rq` references only `tab:` + standard SPARQL.
- **The one permitted procedural guard:** `grid = infer_leaf_grid(band) if len(band.lines) >= 2 else None`. `infer_leaf_grid` raises on a 0-line band and today's `<2 lines` branch returns `grid=None` without computing it — so this guard is extraction-safety + grid-field fidelity, **not** a kind decision (the kind is still derived from `tab:lineCount` in SPARQL). Documented in code.
- Namespaces: `tab:` = `https://w3id.org/iladub/tab#`; evidence graph uses `urn:iladub:evidence:` (matching `celltype.py`).
- Run tests with `.venv/bin/python -m pytest`.

---

### Task 1: Owned vocabulary terms for the evidence graph

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append after the typed-cell evidence block, ~line 214)
- Test: `tests/etkl/test_tab_vocab.py` (create if absent; else add to the existing tab.ttl parse test)

**Interfaces:**
- Consumes: nothing.
- Produces: the terms `tab:ClassifyBand`, `tab:lineCount`, `tab:gridColumnCount`, `tab:HeaderWord`, `tab:headerWordOrder`, `tab:strictlyInColumn`, `tab:RegionKind`, `tab:RecordTable`, `tab:UnsupportedTable`, `tab:NonTable` — consumed by Tasks 2 and 3.

- [ ] **Step 1: Write the failing test**

Check whether a tab.ttl parse test already exists: `ls tests/etkl/test_tab_vocab.py 2>/dev/null`. If it exists, add the function below to it (and skip creating the file). Otherwise create `tests/etkl/test_tab_vocab.py`:

```python
from pathlib import Path
from rdflib import Graph, Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")
_TTL = Path(__file__).resolve().parents[2] / "vocab" / "ontology" / "tab.ttl"


def _graph():
    g = Graph()
    g.parse(_TTL, format="turtle")
    return g


def test_classify_evidence_terms_present():
    g = _graph()
    subjects = set(g.subjects())
    for local in ("ClassifyBand", "lineCount", "gridColumnCount", "HeaderWord",
                  "headerWordOrder", "strictlyInColumn", "RegionKind",
                  "RecordTable", "UnsupportedTable", "NonTable"):
        assert TAB[local] in subjects, f"missing tab:{local}"


def test_region_kinds_are_regionkind_individuals():
    g = _graph()
    for local in ("RecordTable", "UnsupportedTable", "NonTable"):
        assert (TAB[local], None, TAB.RegionKind) in ((s, None, o) for s, p, o in g.triples((TAB[local], None, None))), \
            f"tab:{local} is not a tab:RegionKind"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_tab_vocab.py -v`
Expected: FAIL (terms missing).

- [ ] **Step 3: Add the terms to `tab.ttl`**

Append after the typed-cell evidence block (after the `tab:columnIndex` definition, ~line 214):

```turtle
# --- band-classification evidence graph (transient, pre-holon; loop B2c) ---
tab:ClassifyBand a owl:Class ; rdfs:label "Classify band"@en ;
    rdfs:comment "A transient candidate band being classified into a region kind. Evidence for the kind derivation (regions.classify); never asserted into a holon."@en .
tab:lineCount a owl:DatatypeProperty ; rdfs:domain tab:ClassifyBand ; rdfs:range xsd:integer ; rdfs:label "line count"@en .
tab:gridColumnCount a owl:DatatypeProperty ; rdfs:domain tab:ClassifyBand ; rdfs:range xsd:integer ; rdfs:label "grid column count"@en ;
    rdfs:comment "grid.ncols from infer_leaf_grid; 0 when the band has fewer than 2 lines (grid undefined)."@en .
tab:HeaderWord a owl:Class ; rdfs:label "Header word"@en ;
    rdfs:comment "A word on the band's header line (line 0), for the 1:1 clean-tiling test."@en .
tab:headerWordOrder a owl:DatatypeProperty ; rdfs:domain tab:HeaderWord ; rdfs:range xsd:integer ; rdfs:label "header word order"@en ;
    rdfs:comment "The word's 0-based left-to-right position among the header words (sorted by x0)."@en .
tab:strictlyInColumn a owl:DatatypeProperty ; rdfs:domain tab:HeaderWord ; rdfs:range xsd:integer ; rdfs:label "strictly in column"@en ;
    rdfs:comment "The unique column index the word is strictly inside (per _word_in_column); OMITTED when the word straddles a gutter."@en .
tab:RegionKind a owl:Class ; rdfs:label "Region kind"@en ;
    rdfs:comment "The kind a band is classified as."@en .
tab:RecordTable a tab:RegionKind ; rdfs:label "Record table"@en .
tab:UnsupportedTable a tab:RegionKind ; rdfs:label "Unsupported table"@en .
tab:NonTable a tab:RegionKind ; rdfs:label "Non table"@en .
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/etkl/test_tab_vocab.py -v`
Expected: PASS.

- [ ] **Step 5: Confirm source-ownership CI still green**

Run: `.venv/bin/python -m pytest tests/test_source_ownership.py -v`
Expected: PASS (all new subjects are `tab:`; no `holon:` term touched).

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/tab.ttl tests/etkl/test_tab_vocab.py
git commit -m "feat(etkl): tab: band-classification evidence terms (loop B2c task 1)"
```

---

### Task 2: The evidence-graph emitter, the kind query, and the runner

**Files:**
- Create: `src/iladub/etkl/classifygraph.py`
- Create: `vocab/queries/classify-kind.rq`
- Test: `tests/etkl/test_classifygraph.py`

**Interfaces:**
- Consumes: `tab:` terms from Task 1; `Band` (`iladub.etkl.bands`), `LeafGrid` (`iladub.etkl.grid`), `_word_in_column` (`iladub.etkl.regions`, unchanged).
- Produces:
  - `classify_evidence(band: Band, grid: LeafGrid | None) -> rdflib.Graph`
  - `run_kind(rq_path: str, graph: rdflib.Graph) -> tuple[str, int, int | None]` returning `(kind_iri, nhw, first_bad)`
  - module constant `CLASSIFY_KIND_RQ: pathlib.Path` (the resolved path to `classify-kind.rq`)
  - Consumed by Task 3.

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_classifygraph.py`:

```python
from rdflib import Namespace, RDF, Literal
from rdflib.namespace import XSD

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Word, Line
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.classifygraph import classify_evidence, run_kind, CLASSIFY_KIND_RQ

TAB = Namespace("https://w3id.org/iladub/tab#")


def _line(words):
    return Line(tuple(words), 0.0, 10.0)


def _band(lines):
    return Band(tuple(lines), 0.0, 10.0)


def _hdr(*spans):
    # spans: (text, x0, x1)
    return _line([Word(t, x0, x1, 0.0, 10.0) for (t, x0, x1) in spans])


def _grid_of(band):
    return infer_leaf_grid(band) if len(band.lines) >= 2 else None


# --- emitter unit tests ---

def test_emitter_counts_and_header_words():
    # header words each cleanly inside their column; a data line to make it a 2-line band
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160), ("C", 210, 260)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 210, 260))])
    grid = _grid_of(band)
    g = classify_evidence(band, grid)
    b = next(g.subjects(RDF.type, TAB.ClassifyBand))
    assert g.value(b, TAB.lineCount) == Literal(2, datatype=XSD.integer)
    assert g.value(b, TAB.gridColumnCount) == Literal(grid.ncols, datatype=XSD.integer)
    hw = list(g.subjects(RDF.type, TAB.HeaderWord))
    assert len(hw) == 3
    orders = sorted(int(g.value(w, TAB.headerWordOrder)) for w in hw)
    assert orders == [0, 1, 2]
    # each header word strictly inside its own column
    for w in hw:
        o = int(g.value(w, TAB.headerWordOrder))
        assert int(g.value(w, TAB.strictlyInColumn)) == o


def test_emitter_omits_strictlyInColumn_for_straddler():
    # 3 columns from the data rows, but the middle header word straddles the gutter
    band = _band([_hdr(("A", 10, 60), ("STRADDLE", 150, 230), ("C", 300, 350)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 300, 350)),
                  _hdr(("4", 10, 60), ("5", 110, 160), ("6", 300, 350))])
    grid = _grid_of(band)
    g = classify_evidence(band, grid)
    straddlers = [w for w in g.subjects(RDF.type, TAB.HeaderWord)
                  if g.value(w, TAB.strictlyInColumn) is None]
    assert len(straddlers) == 1


def test_emitter_grid_none_for_short_band():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160))])  # 1 line
    g = classify_evidence(band, None)
    b = next(g.subjects(RDF.type, TAB.ClassifyBand))
    assert g.value(b, TAB.lineCount) == Literal(1, datatype=XSD.integer)
    assert g.value(b, TAB.gridColumnCount) == Literal(0, datatype=XSD.integer)
    assert list(g.subjects(RDF.type, TAB.HeaderWord)) == []


# --- query tests (synthetic graphs built by the emitter) ---

def _kind(band):
    grid = _grid_of(band)
    return run_kind(str(CLASSIFY_KIND_RQ), classify_evidence(band, grid))


def test_query_record_table():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160), ("C", 210, 260)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 210, 260))])
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.RecordTable)
    assert nhw == 3 and fb is None


def test_query_non_table_short():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160))])
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.NonTable)


def test_query_unsupported_straddle_first_bad():
    band = _band([_hdr(("A", 10, 60), ("STRADDLE", 150, 230), ("C", 300, 350)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 300, 350)),
                  _hdr(("4", 10, 60), ("5", 110, 160), ("6", 300, 350))])
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.UnsupportedTable)
    assert fb == 1  # the straddler is the second (order 1) header word
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/etkl/test_classifygraph.py -v`
Expected: FAIL with `ModuleNotFoundError: iladub.etkl.classifygraph`.

- [ ] **Step 3: Write `vocab/queries/classify-kind.rq`** (copy verbatim — feasibility-proven)

```sparql
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?kind ?nhw ?firstBad WHERE {
  ?b a tab:ClassifyBand ; tab:lineCount ?nl ; tab:gridColumnCount ?nc .
  { SELECT (COUNT(?hw) AS ?nhw) WHERE { ?hw a tab:HeaderWord } }
  BIND(EXISTS {
      ?w a tab:HeaderWord ; tab:headerWordOrder ?o .
      FILTER NOT EXISTS { ?w tab:strictlyInColumn ?o }
  } AS ?mis)
  BIND(IF(?nl < 2 || ?nc < 2, tab:NonTable,
       IF(?nhw = ?nc && !?mis, tab:RecordTable, tab:UnsupportedTable)) AS ?kind)
  OPTIONAL {
    SELECT (MIN(?o2) AS ?firstBad) WHERE {
      ?w2 a tab:HeaderWord ; tab:headerWordOrder ?o2 .
      FILTER NOT EXISTS { ?w2 tab:strictlyInColumn ?o2 }
    }
  }
}
```

- [ ] **Step 4: Write `src/iladub/etkl/classifygraph.py`**

```python
"""classifygraph — the band-classification evidence graph + kind-query runner (loop B2c).

regions.classify's kind decision (NON_TABLE / UNSUPPORTED / RECORD) is a declarative
DERIVATION over a per-band evidence graph (open-world -> SPARQL; the band is the closure
boundary). This module is the PROCEDURAL layer only: geometric containment (via the
unchanged _word_in_column), emitting the transient evidence graph, and invoking rdflib.
No decision logic, no tuned constant -- the kind decision lives entirely in
vocab/queries/classify-kind.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

from .bands import Band
from .grid import LeafGrid
from .regions import _word_in_column  # unchanged geometric containment (PROCEDURAL)

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

# three dirs up from src/iladub/etkl/classifygraph.py -> repo root, then vocab/queries/
CLASSIFY_KIND_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "classify-kind.rq"


def _strictly_in_column(w, boundaries):
    """The unique column index the word is strictly inside (via _word_in_column), or None."""
    for c in range(len(boundaries) - 1):
        if _word_in_column(w, c, boundaries):
            return c
    return None


def classify_evidence(band: Band, grid: LeafGrid | None) -> Graph:
    """Emit the transient band-classification evidence graph.

    grid is None iff the band has < 2 lines (grid undefined); gridColumnCount is then 0
    and no header words are emitted -- the SPARQL derives NonTable from lineCount anyway.
    """
    g = Graph()
    b = _EV["band"]
    g.add((b, RDF.type, TAB.ClassifyBand))
    g.add((b, TAB.lineCount, Literal(len(band.lines), datatype=XSD.integer)))
    ncols = grid.ncols if grid is not None else 0
    g.add((b, TAB.gridColumnCount, Literal(int(ncols), datatype=XSD.integer)))
    if grid is not None and band.lines:
        header = band.lines[0]
        for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
            u = _EV["hw-%d" % i]
            g.add((u, RDF.type, TAB.HeaderWord))
            g.add((u, TAB.headerWordOrder, Literal(i, datatype=XSD.integer)))
            col = _strictly_in_column(w, grid.boundaries)
            if col is not None:
                g.add((u, TAB.strictlyInColumn, Literal(col, datatype=XSD.integer)))
    return g


def run_kind(rq_path, graph):
    """Run classify-kind.rq; return (kind_iri: str, nhw: int, first_bad: int | None)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    for row in graph.query(q):
        fb = row.firstBad
        return (str(row.kind), int(row.nhw), None if fb is None else int(fb))
    return (str(TAB.NonTable), 0, None)  # defensive: empty graph (no band)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/etkl/test_classifygraph.py -v`
Expected: PASS (all).

Note on `parents[3]`: `classifygraph.py` is at `src/iladub/etkl/`, so `parents[0]=etkl, [1]=iladub, [2]=src, [3]=repo root`. If the path resolves wrong, the tests using `CLASSIFY_KIND_RQ` fail immediately — verify the `.rq` is found. (Do **not** assume; the test proves it.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/classifygraph.py vocab/queries/classify-kind.rq tests/etkl/test_classifygraph.py
git commit -m "feat(etkl): band-classification evidence graph + kind derivation (loop B2c task 2)"
```

---

### Task 3: Rewire `classify` + reason rebuild + the differential oracle

**Files:**
- Modify: `src/iladub/etkl/regions.py:75-100` (the `classify` function body only)
- Test: `tests/etkl/test_classifygraph.py` (add the differential-oracle battery)
- Verify: `tests/etkl/test_regions.py` and the full suite stay green

**Interfaces:**
- Consumes: `classify_evidence`, `run_kind`, `CLASSIFY_KIND_RQ` (Task 2); the unchanged `infer_leaf_grid`, `assign_cells`, `RegionKind`, `ClassifiedRegion`, `Cell`.
- Produces: a `classify(band) -> ClassifiedRegion` with **identical** public behaviour (kind, grid, cells, reason) — no signature change.

- [ ] **Step 1: Write the failing differential-oracle battery**

Add to `tests/etkl/test_classifygraph.py`. `_ref_classify` is a **frozen verbatim copy of today's `classify` decision logic** (it reuses the unchanged helpers, which do not change):

```python
# --- differential oracle: frozen reference vs the rewired classify ---
from iladub.etkl.regions import classify, RegionKind, ClassifiedRegion, assign_cells, _word_in_column as _wic


def _ref_classify(band):
    """FROZEN copy of regions.classify's pre-B2c logic. Do not edit -- the anti-overfit oracle."""
    if len(band.lines) < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, None, (), "fewer than 2 lines")
    grid = infer_leaf_grid(band)
    if grid.ncols < 2:
        return ClassifiedRegion(RegionKind.NON_TABLE, band, grid, (), "fewer than 2 columns")
    header = band.lines[0]
    b = grid.boundaries
    if len(header.words) != grid.ncols:
        return ClassifiedRegion(RegionKind.UNSUPPORTED_TABLE, band, grid, (),
                                f"header has {len(header.words)} words but {grid.ncols} columns")
    for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
        if not _wic(w, i, b):
            return ClassifiedRegion(RegionKind.UNSUPPORTED_TABLE, band, grid, (),
                                    f"header word {w.text!r} is not aligned 1:1 with column {i}")
    return ClassifiedRegion(RegionKind.RECORD_TABLE, band, grid, assign_cells(band, grid),
                            "flat single-level header")


def _assert_equivalent(band):
    got, ref = classify(band), _ref_classify(band)
    assert got.kind == ref.kind, (got.reason, ref.reason)
    assert got.reason == ref.reason
    assert (got.grid is None) == (ref.grid is None)
    if got.grid is not None:
        assert got.grid.ncols == ref.grid.ncols
        assert got.grid.boundaries == ref.grid.boundaries
    assert [(c.row, c.col, c.text) for c in got.cells] == [(c.row, c.col, c.text) for c in ref.cells]


# shape battery -- one band per classify branch
_DATA3 = [_hdr(("1", 10, 60), ("2", 110, 160), ("3", 210, 260)),
          _hdr(("4", 10, 60), ("5", 110, 160), ("6", 210, 260))]


def _battery():
    return {
        "empty": _band([]),
        "one-line": _band([_hdr(("A", 10, 60), ("B", 110, 160))]),
        "one-col": _band([_hdr(("A", 10, 60)), _hdr(("x", 10, 60)), _hdr(("y", 10, 60))]),
        "clean-3col": _band([_hdr(("A", 10, 60), ("B", 110, 160), ("C", 210, 260))] + _DATA3),
        "clean-2col": _band([_hdr(("A", 10, 60), ("B", 110, 160)),
                             _hdr(("x", 10, 60), ("y", 110, 160))]),
        "too-few-words": _band([_hdr(("A", 10, 60), ("B", 110, 160))] + _DATA3),
        "too-many-words": _band([_hdr(("A", 10, 40), ("X", 45, 60), ("B", 110, 160), ("C", 210, 260))] + _DATA3),
        "straddle-mid": _band([_hdr(("A", 10, 60), ("STRAD", 150, 230), ("C", 210, 260))] + _DATA3),
        "wrong-col": _band([_hdr(("A", 10, 60), ("B", 210, 260), ("C", 210, 260))] + _DATA3),
    }


import pytest


@pytest.mark.parametrize("name", list(_battery().keys()))
def test_differential_oracle(name):
    _assert_equivalent(_battery()[name])
```

Note: the implementer must **verify each battery band actually exercises the intended branch** before relying on it (build the band, print `_ref_classify(band).kind`/`.reason`) — hand-authored geometry fixtures have repeatedly been wrong. Adjust the `x0/x1` spans (not the assertions) if a band lands on the wrong branch, and confirm both `classify` and `_ref_classify` agree. If a synthetic band cannot cleanly hit a branch (e.g. `infer_leaf_grid` reads a different ncols than intended), fix the spans; the oracle asserts equivalence, so a mislabeled band still passes if both sides agree — but coverage intent must be met.

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_classifygraph.py -k differential -v`
Expected: FAIL — the current `classify` and `_ref_classify` are identical, so this passes trivially *until* Step 3 rewires `classify`; run it now to confirm the battery is wired and green against the un-rewired code (baseline), then Step 3's rewire must keep it green. (This is a faithful lift: the oracle's job is to stay green across the rewrite. The "failing test first" here is the emitter/query tests of Task 2; this battery is the regression lock.)

- [ ] **Step 3: Rewire `classify` in `regions.py`**

Replace the `classify` function body (lines 75-100) with the version below. Keep the module docstring, imports, `RegionKind`, `Cell`, `ClassifiedRegion`, `column_of`, `assign_cells`, `_word_in_column` **unchanged**. Add the two new imports at the top of the file (after the existing `from .grid import ...`):

```python
from .classifygraph import classify_evidence, run_kind, CLASSIFY_KIND_RQ, TAB
```

New `classify`:

```python
_KIND = {
    str(TAB.RecordTable): RegionKind.RECORD_TABLE,
    str(TAB.UnsupportedTable): RegionKind.UNSUPPORTED_TABLE,
    str(TAB.NonTable): RegionKind.NON_TABLE,
}


def _reason(kind, band, grid, nhw, first_bad):
    """Rebuild the exact legacy reason string from the SPARQL-derived kind + scalars."""
    if kind is RegionKind.NON_TABLE:
        return "fewer than 2 lines" if len(band.lines) < 2 else "fewer than 2 columns"
    if kind is RegionKind.RECORD_TABLE:
        return "flat single-level header"
    # UNSUPPORTED_TABLE
    if nhw != grid.ncols:
        return f"header has {nhw} words but {grid.ncols} columns"
    w = sorted(band.lines[0].words, key=lambda w: w.x0)[first_bad]
    return f"header word {w.text!r} is not aligned 1:1 with column {first_bad}"


def classify(band: Band) -> ClassifiedRegion:
    # PROCEDURAL guard (extraction safety + grid-field fidelity, NOT a kind decision):
    # infer_leaf_grid is undefined on a <2-line band and today's NON_TABLE(<2 lines)
    # branch returns grid=None. The KIND is still derived from tab:lineCount in SPARQL.
    grid = infer_leaf_grid(band) if len(band.lines) >= 2 else None
    kind_iri, nhw, first_bad = run_kind(str(CLASSIFY_KIND_RQ), classify_evidence(band, grid))
    kind = _KIND[kind_iri]
    reason = _reason(kind, band, grid, nhw, first_bad)
    cells = assign_cells(band, grid) if kind is RegionKind.RECORD_TABLE else ()
    return ClassifiedRegion(kind, band, grid, cells, reason)
```

Also update the module docstring's second paragraph to note the kind decision is now a SPARQL derivation (AXIOM) over the `classifygraph` evidence graph, with `_word_in_column`/`infer_leaf_grid` as the PROCEDURAL geometry and the multi-word-header escape still escalating to UNSUPPORTED (deferred NEURAL). Keep it to ~4 lines.

- [ ] **Step 4: Run the differential oracle + regions tests**

Run: `.venv/bin/python -m pytest tests/etkl/test_classifygraph.py tests/etkl/test_regions.py -v`
Expected: PASS (all) — the rewire is byte-identical for every battery band and every real-fixture band.

- [ ] **Step 5: Run the full behavioural suite (the faithful-lift gate)**

Run: `.venv/bin/python -m pytest`
Expected: PASS with the same pass/skip counts as before B2c (368 passed / 5 skipped baseline, +the new B2c tests). **Any** pre-existing test that changed outcome is a regression — stop and investigate; do not adjust downstream assertions.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/regions.py tests/etkl/test_classifygraph.py
git commit -m "feat(etkl): classify kind decision -> SPARQL derivation, differential-oracle gated (loop B2c task 3)"
```

---

## Self-Review (completed during planning)

- **Spec coverage:** §1 goal → Task 3 rewire; §3 evidence graph → Tasks 1+2; §4 query (verbatim, proven) → Task 2 Step 3; §5 components → all three tasks; §7 differential oracle → Task 3 battery + full-suite gate; §9 deferred (multi-word escape stays UNSUPPORTED) → preserved by the faithful lift (no admission change). Covered.
- **Placeholder scan:** none — every step has complete code/commands.
- **Type consistency:** `classify_evidence(band, grid|None)`, `run_kind(rq_path, graph) -> (str, int, int|None)`, `CLASSIFY_KIND_RQ: Path` used identically in Tasks 2 and 3. `_KIND` maps the three `str(TAB.*)` IRIs to the three `RegionKind` members. `nhw`/`first_bad` names consistent between query, runner, and `_reason`.
- **The `parents[3]` path** is flagged for in-test verification (Task 2 Step 5) — the recurring `_QUERIES` path bug from earlier loops.
- **The battery-band correctness** is flagged for implementer verification (Task 3 Step 1 note) — the recurring hand-authored-fixture bug.
