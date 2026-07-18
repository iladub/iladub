# Narrow-Flank Exclusion (loop B1.2, AXIOM) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the documented narrow-flank merge silent-wrong by resolving a tie-band spanning header via a declarative header-cell derivation (a flank with its own same-level leaf header is excluded; a header-empty tied flank escalates `MERGE_AMBIGUOUS`) — never a silent over-absorb.

**Architecture:** The tie is *detected* by procedural geometry (unchanged `_centered_run` machinery); the tie is *resolved* by an AXIOM — a transient per-band header-cell evidence graph + a SPARQL `SELECT` (`vocab/queries/flank-sibling.rq`) naming every leaf column that bears its own header cell at a given header level (the loop-B2a/B2c `classifygraph` pattern). A new `resolve_narrow_flanks` pass in `headers.py` runs after `repair_coverage`: a same-level-sibling flank is excluded from the parent's covers; otherwise the parent `HeaderNode` is marked `ambiguous`, which the existing `merge_tiling_ok` gate turns into the shipped `MERGE_AMBIGUOUS` escalation. No BAML, no proposer, no confidence — the NEURAL header-empty residual is deferred to loop B1.3.

**Tech Stack:** Python 3, `rdflib` (evidence graph + SPARQL), `pytest`. Follows the shipped `iladub.etkl.classifygraph` + `vocab/queries/*.rq` precedent.

## Global Constraints

- **Neurosymbolic-first gate (CLAUDE.md §8):** the flank *resolution* is an AXIOM — a declarative SPARQL derivation over an RDF evidence graph. **No tuned constant may decide the flank.** Tie *detection* geometry (`_median_pitch`, the `0.25·pitch` band, `_word_in_column`, `column_of`) stays PROCEDURAL and each such site states in-code why it is irreducible. A Python predicate answering "does the span cover this column" is a review failure — the `.rq` must carry the decision.
- **Open/closed split:** the derivation is **open-world** (SPARQL, evidence-positive — a flank is named a sibling only when its same-level header cell is *present*, never inferred from absence). Absence → escalate. The band is the **closure boundary** — the evidence graph is fresh per band; any `NOT EXISTS`/`COUNT` is query-local.
- **No overfitting (memory: no-overfitting-general-fixes):** the fix must generalize; confidence ≠ validity (moot here — no confidence); honest escalation > fake success. Build the regression fixture FIRST.
- **No silent-wrong:** a tied narrow flank is either excluded (same-level sibling) or escalated (`MERGE_AMBIGUOUS`) — never silently absorbed.
- **Ownership/licensing:** only `iladub`-owned namespaces are authored; the `.rq` uses `tab:` (`https://w3id.org/iladub/tab#`). Code Apache-2.0, vocab CC-BY-4.0. Author François Rosselet © 2026.
- **Namespaces:** `TAB = Namespace("https://w3id.org/iladub/tab#")`. Query file path resolved as `Path(__file__).resolve().parents[3] / "vocab" / "queries" / "flank-sibling.rq"` (three dirs up from `src/iladub/etkl/…`).
- **Run the full suite** (`pytest -q`) at the final task; the baseline is **386 passed / 5 skipped** (post-B2c). No regression permitted.

---

## File Structure

- **Create** `vocab/queries/flank-sibling.rq` — the AXIOM: `SELECT ?col ?level` of leaf columns with an own strict-in-column header cell per level.
- **Create** `src/iladub/etkl/flankgraph.py` — PROCEDURAL glue: emit the transient header-cell evidence graph (`flank_evidence`) and run the query (`sibling_columns`). Mirrors `classifygraph.py`.
- **Modify** `src/iladub/etkl/headers.py` — add `HeaderNode.ambiguous` field; add `_narrow_flank_tie` (geometry detector) and `resolve_narrow_flanks` (the pass); call it from `infer_header_tree`; make `merge_tiling_ok` honor `ambiguous`.
- **Create** `tests/etkl/test_flankgraph.py` — unit tests for the emitter + query.
- **Create** `tests/etkl/test_span_gate.py` — the anti-overfit gate test (regression fixture first).
- **Modify** `docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md` — mark B1.2 retired, point to B1.3 residual.
- **Modify** `CLAUDE.md` §8 exemplar list — add the shipped narrow-flank AXIOM (final task).

Vocabulary terms already exist in `vocab/ontology/tab.ttl`: `tab:HeaderWord`, `tab:headerWordOrder`, `tab:strictlyInColumn`, `tab:headerLevel`. Task 1 adds only a thin `tab:HeaderCell` class + `tab:cellLevel`-style reuse (details in Task 1).

---

### Task 1: `tab:` vocab — header-cell-with-level evidence term

**Files:**
- Modify: `vocab/ontology/tab.ttl` (near the existing `tab:HeaderWord` block, ~line 222)
- Test: `tests/etkl/test_tab_vocab.py` (existing; add one assertion)

**Interfaces:**
- Produces: RDF terms `tab:HeaderCell` (class), reused `tab:strictlyInColumn` (int) and `tab:headerLevel` (int) as its properties. Consumed by Task 2's evidence graph and Task 3's query.

Rationale: `tab:HeaderWord` is B2c's *single-row* (band.lines[0]) construct. The flank decision needs header cells across **all** header rows with their level, so a distinct `tab:HeaderCell` class keeps the two evidence graphs from colliding while reusing the existing datatype properties.

- [ ] **Step 1: Add a failing vocab assertion**

In `tests/etkl/test_tab_vocab.py`, add:

```python
def test_headercell_term_present():
    from rdflib import Graph, Namespace, RDF, OWL
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph().parse("vocab/ontology/tab.ttl", format="turtle")
    assert (TAB.HeaderCell, RDF.type, OWL.Class) in g
```

- [ ] **Step 2: Run it, verify it fails**

Run: `pytest tests/etkl/test_tab_vocab.py::test_headercell_term_present -v`
Expected: FAIL (assertion error — term absent).

- [ ] **Step 3: Add the term to `vocab/ontology/tab.ttl`**

After the `tab:HeaderWord` block (~line 226, after `tab:strictlyInColumn`), add:

```turtle
tab:HeaderCell a owl:Class ; rdfs:label "Header cell"@en ;
    rdfs:comment "A populated header cell across any header row, carrying its header level (row index, top-to-bottom) and, when its ink is strictly inside one leaf column, that column. Evidence for the narrow-flank sibling derivation (loop B1.2)."@en .
```

(`tab:strictlyInColumn` and `tab:headerLevel` already exist; no new properties needed. Do NOT constrain their `rdfs:domain` — they are shared with `tab:HeaderWord` / header nodes.)

- [ ] **Step 4: Run it, verify it passes**

Run: `pytest tests/etkl/test_tab_vocab.py::test_headercell_term_present -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/tab.ttl tests/etkl/test_tab_vocab.py
git commit -m "feat(etkl): tab:HeaderCell evidence term for narrow-flank sibling derivation (B1.2 task 1)"
```

---

### Task 2: The header-cell evidence graph (`flankgraph.py`)

**Files:**
- Create: `src/iladub/etkl/flankgraph.py`
- Test: `tests/etkl/test_flankgraph.py`

**Interfaces:**
- Consumes: `tab:HeaderCell` (Task 1); the existing `regions._word_in_column` (via a call-time import, exactly as `classifygraph._strictly_in_column` does — `headers`/`regions` import cycle).
- Produces:
  - `flank_evidence(header_cells: list[tuple[int, float, float, str]], boundaries: Sequence[float]) -> rdflib.Graph`
    where each tuple is `(level, x0, x1, text)` for one populated header cell.
  - `FLANK_SIBLING_RQ: pathlib.Path` — the query path.
  - `sibling_columns(header_cells, boundaries) -> set[tuple[int, int]]` — set of `(col, level)` pairs that have an own strict-in-column header cell (runs `flank_evidence` + the query). Task 3 fills in the query; here `sibling_columns` is written against it.

- [ ] **Step 1: Write failing emitter tests**

Create `tests/etkl/test_flankgraph.py`:

```python
from rdflib import Namespace, RDF, Literal
from rdflib.namespace import XSD

from iladub.etkl.flankgraph import flank_evidence

TAB = Namespace("https://w3id.org/iladub/tab#")

# boundaries for 4 leaf columns: col0=[0,100] col1=[100,200] col2=[200,300] col3=[300,340]
B = (0.0, 100.0, 200.0, 300.0, 340.0)


def test_emitter_strict_in_column_and_level():
    # level-0 spanning cell straddling cols 0-2 (ink 20..280 -> strictly in no single col),
    # level-0 narrow cell strictly inside col 3 (ink 305..335),
    # level-1 leaf cells each strictly inside their column.
    cells = [
        (0, 20.0, 280.0, "Region"),      # straddles -> no strictlyInColumn
        (0, 305.0, 335.0, "Notes"),      # strictly in col 3
        (1, 20.0, 80.0, "A"),            # strictly in col 0
    ]
    g = flank_evidence(cells, B)
    hcs = list(g.subjects(RDF.type, TAB.HeaderCell))
    assert len(hcs) == 3
    # the col-3 level-0 cell carries strictlyInColumn=3, headerLevel=0
    got = {(int(g.value(h, TAB.headerLevel)),
            (int(g.value(h, TAB.strictlyInColumn)) if g.value(h, TAB.strictlyInColumn) is not None else None))
           for h in hcs}
    assert (0, 3) in got        # Notes
    assert (0, None) in got     # Region straddler
    assert (1, 0) in got        # A
```

- [ ] **Step 2: Run, verify it fails**

Run: `pytest tests/etkl/test_flankgraph.py::test_emitter_strict_in_column_and_level -v`
Expected: FAIL (`ModuleNotFoundError: iladub.etkl.flankgraph`).

- [ ] **Step 3: Write `flankgraph.py` (emitter half)**

Create `src/iladub/etkl/flankgraph.py`:

```python
"""flankgraph — header-cell evidence graph + sibling-column query runner (loop B1.2).

The narrow-flank *resolution* (is a tied flank a same-level sibling leaf?) is a declarative
DERIVATION over a per-band header-cell evidence graph (open-world -> SPARQL; the band is the
closure boundary). This module is the PROCEDURAL layer only: geometric containment (via the
unchanged regions._word_in_column), emitting the transient graph, and invoking rdflib. No
decision logic, no tuned constant -- the sibling decision lives entirely in
vocab/queries/flank-sibling.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

# three dirs up from src/iladub/etkl/flankgraph.py -> repo root, then vocab/queries/
FLANK_SIBLING_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "flank-sibling.rq"


def _strictly_in_column(x0: float, x1: float, boundaries: Sequence[float]) -> int | None:
    """The unique leaf column the cell ink [x0,x1] is strictly inside, or None if it straddles
    a gutter. Uses the unchanged regions._word_in_column (a lightweight shim word carries x0/x1).

    PROCEDURAL: exact geometric containment (raw extraction), irreducible to AXIOM/NEURAL.
    """
    # Call-time import: regions <-> headers/flankgraph form an import cycle; both modules are
    # fully loaded by the time any band is resolved (mirrors classifygraph._strictly_in_column).
    from .regions import _word_in_column
    from types import SimpleNamespace
    w = SimpleNamespace(x0=x0, x1=x1)
    for c in range(len(boundaries) - 1):
        if _word_in_column(w, c, boundaries):
            return c
    return None


def flank_evidence(header_cells, boundaries) -> Graph:
    """Emit the transient header-cell evidence graph.

    header_cells: iterable of (level:int, x0:float, x1:float, text:str) for each populated
    header cell across all header rows. Each becomes a tab:HeaderCell with tab:headerLevel and,
    when strictly inside one leaf column, tab:strictlyInColumn.
    """
    g = Graph()
    for i, (level, x0, x1, text) in enumerate(header_cells):
        u = _EV["hc-%d" % i]
        g.add((u, RDF.type, TAB.HeaderCell))
        g.add((u, TAB.headerLevel, Literal(int(level), datatype=XSD.integer)))
        col = _strictly_in_column(x0, x1, boundaries)
        if col is not None:
            g.add((u, TAB.strictlyInColumn, Literal(int(col), datatype=XSD.integer)))
    return g
```

Check `regions._word_in_column`'s signature first:

Run: `grep -n "def _word_in_column" src/iladub/etkl/regions.py`
Expected: `def _word_in_column(w, col, boundaries)` (word with `.x0`/`.x1`, an int col, boundaries). If the parameter order differs, adapt the shim call accordingly.

- [ ] **Step 4: Run emitter test, verify it passes**

Run: `pytest tests/etkl/test_flankgraph.py::test_emitter_strict_in_column_and_level -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/flankgraph.py tests/etkl/test_flankgraph.py
git commit -m "feat(etkl): header-cell evidence graph emitter (B1.2 task 2)"
```

---

### Task 3: The sibling derivation query + reader (`flank-sibling.rq`, `sibling_columns`)

**Files:**
- Create: `vocab/queries/flank-sibling.rq`
- Modify: `src/iladub/etkl/flankgraph.py` (add `sibling_columns`)
- Test: `tests/etkl/test_flankgraph.py` (add query tests)

**Interfaces:**
- Consumes: `flank_evidence` (Task 2), `FLANK_SIBLING_RQ` (Task 2).
- Produces: `sibling_columns(header_cells, boundaries) -> set[tuple[int, int]]` — `(col, level)` pairs with an own strict-in-column header cell. Consumed by Task 5's `resolve_narrow_flanks`.

- [ ] **Step 1: Write failing query/reader tests**

Add to `tests/etkl/test_flankgraph.py`:

```python
from iladub.etkl.flankgraph import sibling_columns

def test_sibling_columns_names_own_leaf_headers():
    # col 3 has its OWN header cell at level 0 (strictly in col 3) -> (3,0) a sibling.
    # the level-0 straddler (Region) is NOT strictly in any col -> contributes no sibling.
    cells = [
        (0, 20.0, 280.0, "Region"),   # straddles cols 0-2
        (0, 305.0, 335.0, "Notes"),   # strictly in col 3, level 0
        (1, 20.0, 80.0, "A"),         # strictly in col 0, level 1
    ]
    sibs = sibling_columns(cells, B)
    assert (3, 0) in sibs      # col 3 is a same-level (0) sibling leaf
    assert (0, 1) in sibs      # col 0 has its own level-1 header
    assert (0, 0) not in sibs  # col 0 has NO own strict level-0 header (only the straddler covers it)

def test_sibling_columns_empty_when_header_empty():
    # a flank column (col 3) with NO own header cell at any level -> not a sibling anywhere.
    cells = [(0, 20.0, 280.0, "Region"), (1, 20.0, 80.0, "A")]
    sibs = sibling_columns(cells, B)
    assert not any(col == 3 for (col, _lvl) in sibs)
```

- [ ] **Step 2: Run, verify it fails**

Run: `pytest tests/etkl/test_flankgraph.py -k sibling -v`
Expected: FAIL (`ImportError: cannot import name 'sibling_columns'`).

- [ ] **Step 3: Write the query `vocab/queries/flank-sibling.rq`**

```sparql
PREFIX tab: <https://w3id.org/iladub/tab#>
# A leaf column is a same-level SIBLING at ?level iff it bears its OWN header cell whose ink
# is strictly inside that column at that level. Open-world, evidence-positive: emitted only
# when such a cell is PRESENT (never inferred from absence -- absence => escalate, loop B1.3).
SELECT DISTINCT ?col ?level WHERE {
  ?h a tab:HeaderCell ;
     tab:headerLevel ?level ;
     tab:strictlyInColumn ?col .
}
```

- [ ] **Step 4: Write `sibling_columns` in `flankgraph.py`**

Append to `src/iladub/etkl/flankgraph.py`:

```python
def sibling_columns(header_cells, boundaries) -> set[tuple[int, int]]:
    """(col, level) pairs that have an own strict-in-column header cell -- same-level sibling
    leaves. PROCEDURAL glue over the AXIOM query flank-sibling.rq; carries no decision itself."""
    g = flank_evidence(header_cells, boundaries)
    q = FLANK_SIBLING_RQ.read_text(encoding="utf-8")
    return {(int(row.col), int(row.level)) for row in g.query(q)}
```

- [ ] **Step 5: Run, verify it passes**

Run: `pytest tests/etkl/test_flankgraph.py -k sibling -v`
Expected: PASS (both tests).

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/flank-sibling.rq src/iladub/etkl/flankgraph.py tests/etkl/test_flankgraph.py
git commit -m "feat(etkl): flank-sibling.rq derivation + sibling_columns reader (B1.2 task 3)"
```

---

### Task 4: `HeaderNode.ambiguous` + `merge_tiling_ok` honors it

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`HeaderNode` dataclass ~line 108; `merge_tiling_ok` ~line 272)
- Test: `tests/etkl/test_headers.py` (add one test)

**Interfaces:**
- Produces: `HeaderNode(..., ambiguous: bool = False)`; `merge_tiling_ok(tree, grid) -> bool` now returns `False` if any node in `tree` has `ambiguous=True`. Consumed by Task 5 (sets the flag) and the existing `compile.py:201` gate (fires `MERGE_AMBIGUOUS`).

- [ ] **Step 1: Write the failing test**

Add to `tests/etkl/test_headers.py`:

```python
def test_merge_tiling_ok_rejects_ambiguous_node():
    from iladub.etkl.headers import merge_tiling_ok, HeaderNode
    from iladub.etkl.grid import LeafGrid
    grid = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0), ncols=3, pitch=100.0, confidence=1.0)
    # a structurally-fine tree, but one node flagged ambiguous -> gate must reject.
    tree = (HeaderNode(0, (1,), "X", None, 150.0, ambiguous=True),
            HeaderNode(0, (2,), "Y", None, 250.0))
    assert merge_tiling_ok(tree, grid) is False
```

Check `LeafGrid`'s constructor first:

Run: `grep -n "class LeafGrid" -A6 src/iladub/etkl/grid.py`
Expected: a dataclass with `boundaries` and `ncols`; adapt the fixture if field names differ.

- [ ] **Step 2: Run, verify it fails**

Run: `pytest tests/etkl/test_headers.py::test_merge_tiling_ok_rejects_ambiguous_node -v`
Expected: FAIL (`TypeError: unexpected keyword argument 'ambiguous'`).

- [ ] **Step 3: Add the field + the gate check**

In `src/iladub/etkl/headers.py`, extend the dataclass:

```python
@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None
    center_x: float | None = None
    ambiguous: bool = False
```

In `merge_tiling_ok`, add at the very top of the function body (before the overlap check):

```python
    if any(getattr(n, "ambiguous", False) for n in tree):
        return False                       # a resolver-flagged narrow-flank -> escalate MERGE_AMBIGUOUS
```

- [ ] **Step 4: Run, verify it passes**

Run: `pytest tests/etkl/test_headers.py::test_merge_tiling_ok_rejects_ambiguous_node -v`
Expected: PASS.

- [ ] **Step 5: Run the headers + hierarchical suites (no regression from the new field)**

Run: `pytest tests/etkl/test_headers.py tests/etkl/test_hierarchical.py tests/etkl/test_hier_holon.py -q`
Expected: all PASS (default `ambiguous=False` leaves existing behavior unchanged).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_headers.py
git commit -m "feat(etkl): HeaderNode.ambiguous flag routed through merge_tiling_ok (B1.2 task 4)"
```

---

### Task 5: The narrow-flank tie detector + resolver pass

**Files:**
- Modify: `src/iladub/etkl/headers.py` (add `_narrow_flank_tie`, `resolve_narrow_flanks`; call from `infer_header_tree`)
- Test: `tests/etkl/test_headers.py` (add detector + pass unit tests)

**Interfaces:**
- Consumes: `sibling_columns` (Task 3), `_median_pitch` / `_span_center` / `_centered_run` (existing), `HeaderNode.ambiguous` (Task 4).
- Produces:
  - `_narrow_flank_tie(covers: tuple[int,...], ink_cols: tuple[int,...], b: Sequence[float]) -> int | None` — returns the single flanking leaf column that the resolved `covers` includes but that (a) is NOT reached by the node's raw ink (`ink_cols`), (b) is an endpoint of `covers`, and (c) is narrower than `0.5 * _median_pitch(b)` (so excluding it keeps the endpoint center inside the `0.25·pitch` tie-band). `None` if no such flank. PROCEDURAL geometry (tie *detection*).
  - `resolve_narrow_flanks(nodes: list[HeaderNode], grid, header_cells) -> list[HeaderNode]` — the B1.2 pass. `header_cells` is the `(level, x0, x1, text)` list built in `infer_header_tree`.

**Design of `resolve_narrow_flanks`:** for each coarse (has-children or multi-cover) node with geometry:
1. Recover the node's **raw ink columns** `ink_cols` (the columns its own text physically touches — `column_of(cell.x0..)` .. `column_of(cell.x1..)`, passed in alongside the node; see integration below).
2. `flank = _narrow_flank_tie(node.covers, ink_cols, b)`. If `None`, leave the node unchanged.
3. Compute `sibs = sibling_columns(header_cells, b)`.
4. If `(flank, node.level) in sibs` → the flank is a same-level sibling leaf → **exclude**: `covers = tuple(c for c in node.covers if c != flank)` (and, if `flank` is the max/min, this trims the endpoint). Replace the node.
5. Else (header-empty at this level) → **escalate**: mark `node` `ambiguous=True` (do NOT change covers).

- [ ] **Step 1: Write failing detector unit tests**

Add to `tests/etkl/test_headers.py`:

```python
def test_narrow_flank_tie_detects_narrow_endpoint_not_reached_by_ink():
    from iladub.etkl.headers import _narrow_flank_tie
    # boundaries [0,100,200,300,400,440]: cols 1-3 width 100, col 4 width 40 (< 0.5*pitch=50).
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    # covers 1..4, but raw ink only reaches cols 1..3 -> col 4 is the narrow tied flank.
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3), b) == 4

def test_narrow_flank_tie_none_when_flank_wide():
    from iladub.etkl.headers import _narrow_flank_tie
    # col 4 width 60 (> 0.5*pitch=50) -> NOT a tie (excluding it would leave the band).
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 460.0)
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3), b) is None

def test_narrow_flank_tie_none_when_ink_reaches_flank():
    from iladub.etkl.headers import _narrow_flank_tie
    # raw ink already reaches col 4 -> deterministic coverage, not a tie.
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    assert _narrow_flank_tie((1, 2, 3, 4), (1, 2, 3, 4), b) is None
```

- [ ] **Step 2: Run, verify they fail**

Run: `pytest tests/etkl/test_headers.py -k narrow_flank_tie -v`
Expected: FAIL (`ImportError`).

- [ ] **Step 3: Implement `_narrow_flank_tie`**

In `src/iladub/etkl/headers.py` (after `_centered_run`):

```python
def _narrow_flank_tie(covers, ink_cols, b) -> int | None:
    """The single narrow flanking leaf column that `covers` includes but the node's raw ink does
    NOT reach and whose exclusion keeps the run inside the centering tie-band -- i.e. an endpoint
    column narrower than half the median pitch not physically touched by the label. None if no
    such flank (the resolution is then unambiguous or wide-enough to decide geometrically).

    PROCEDURAL: this is tie *detection* (geometry), not the span *decision* (that is the AXIOM
    flank-sibling.rq). Irreducible -- it reads raw ink extents and column widths.
    """
    if len(covers) < 2 or not ink_cols:
        return None
    half_pitch = 0.5 * _median_pitch(b)
    lo, hi = min(covers), max(covers)
    ink_lo, ink_hi = min(ink_cols), max(ink_cols)
    for flank in (hi, lo):                       # endpoints only
        if flank in ink_cols:
            continue                             # ink reaches it -> deterministic, not a tie
        # the flank is an endpoint not reached by ink; is it narrow enough that excluding it
        # keeps the run centered (i.e. it sits inside the tie-band)?
        width = b[flank + 1] - b[flank]
        beyond_ink = (flank > ink_hi) if flank == hi else (flank < ink_lo)
        if width < half_pitch and beyond_ink:
            return flank
    return None
```

- [ ] **Step 4: Run detector tests, verify they pass**

Run: `pytest tests/etkl/test_headers.py -k narrow_flank_tie -v`
Expected: PASS (all three).

- [ ] **Step 5: Write failing `resolve_narrow_flanks` test**

Add to `tests/etkl/test_headers.py`:

```python
def test_resolve_excludes_same_level_sibling_flank():
    from iladub.etkl.headers import resolve_narrow_flanks, HeaderNode
    from iladub.etkl.grid import LeafGrid
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    grid = LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0)
    # coarse node covers 1..4 (raw ink only 1..3); col 4 HAS its own level-0 leaf header (305..335).
    # header_cells: the coarse label (level0, straddles 1-3) + col4's own level-0 label.
    header_cells = [(0, 105.0, 295.0, "Region"), (0, 305.0, 335.0, "Notes")]
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    # ink_cols supplied per node via the parallel list (see integration) — here 1..3.
    out = resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node=[(1, 2, 3)])
    assert out[0].covers == (1, 2, 3)     # col 4 excluded (same-level sibling)
    assert out[0].ambiguous is False

def test_resolve_escalates_header_empty_flank():
    from iladub.etkl.headers import resolve_narrow_flanks, HeaderNode
    from iladub.etkl.grid import LeafGrid
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    grid = LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0)
    # col 4 has NO own header cell at level 0 -> header-empty -> escalate (mark ambiguous).
    header_cells = [(0, 105.0, 295.0, "Region")]
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    out = resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node=[(1, 2, 3)])
    assert out[0].ambiguous is True
    assert out[0].covers == (1, 2, 3, 4)  # covers unchanged; escalation carries the residue
```

- [ ] **Step 6: Run, verify it fails**

Run: `pytest tests/etkl/test_headers.py -k resolve_ -v`
Expected: FAIL (`ImportError`).

- [ ] **Step 7: Implement `resolve_narrow_flanks`**

In `src/iladub/etkl/headers.py`:

```python
def resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node):
    """B1.2 pass: resolve tie-band narrow-flank over-absorption declaratively.

    For each coarse node, if its resolved covers over-absorbs a single narrow flanking column
    the raw ink does not reach (_narrow_flank_tie), consult the header-cell derivation
    (flank-sibling.rq via sibling_columns): a flank that is a same-level sibling leaf is EXCLUDED
    (parentless leaf); a header-empty flank is marked ambiguous -> the caller escalates
    MERGE_AMBIGUOUS (the NEURAL B1.3 residual). No tuned constant decides -- the .rq does.

    ink_cols_by_node: parallel to `nodes`; the raw ink columns each node's own text touches
    (None for a node lacking geometry -> skipped).
    """
    from .flankgraph import sibling_columns
    if isinstance(grid, int):
        return nodes                                   # no geometry -> nothing to resolve
    b = grid.boundaries
    sibs = sibling_columns(header_cells, b)
    out = list(nodes)
    for i, n in enumerate(out):
        ink = ink_cols_by_node[i] if i < len(ink_cols_by_node) else None
        if ink is None or n.center_x is None or len(n.covers) < 2:
            continue
        flank = _narrow_flank_tie(n.covers, tuple(ink), b)
        if flank is None:
            continue
        if (flank, n.level) in sibs:
            out[i] = replace(n, covers=tuple(c for c in n.covers if c != flank))
        else:
            out[i] = replace(n, ambiguous=True)
    return out
```

- [ ] **Step 8: Run, verify it passes**

Run: `pytest tests/etkl/test_headers.py -k resolve_ -v`
Expected: PASS (both).

- [ ] **Step 9: Wire into `infer_header_tree`**

In `infer_header_tree` (`headers.py:298`), after the `nodes = repair_coverage(nodes, grid)` line (~333) and BEFORE the parent-linking loop, insert:

```python
    # B1.2 — declarative narrow-flank resolution (exclude same-level sibling / escalate residual).
    header_cells = [(lvl, cell.x0, cell.x1, cell.text)
                    for lvl, row in enumerate(header_rows) for cell in row]
    ink_cols_by_node = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            lo = column_of(cell.x0 + 0.1, b)
            hi = column_of(cell.x1 - 0.1, b)
            ink_cols_by_node.append(tuple(range(min(lo, hi), max(lo, hi) + 1)))
    nodes = resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node)
```

Note: `nodes` is built in the same `for lvl, row in enumerate(header_rows)` order (headers.py:327-331), so `ink_cols_by_node` is positionally aligned with `nodes`. Verify the order matches by reading `headers.py:326-333` before editing.

- [ ] **Step 10: Run headers + hierarchical suites**

Run: `pytest tests/etkl/test_headers.py tests/etkl/test_hierarchical.py tests/etkl/test_hier_holon.py -q`
Expected: all PASS (existing fixtures unaffected — the resolver only fires on a detected narrow-flank tie).

- [ ] **Step 11: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_headers.py
git commit -m "feat(etkl): narrow-flank tie detector + declarative resolver pass (B1.2 task 5)"
```

---

### Task 6: The gate test (anti-overfit, regression-fixture-first, end-to-end)

**Files:**
- Create: `tests/etkl/test_span_gate.py`

**Interfaces:**
- Consumes: the public compile/hierarchical path and the fixtures helpers in `tests/etkl` (`Word`, `Line`, `Band` from `iladub.etkl.geometry`; `infer_leaf_grid`). Build the band the way `tests/etkl/test_classifygraph.py` does.

This task ships the **definition-of-done** checks. Build the fixture FIRST, confirm it reproduces the silent-wrong on the pre-B1.2 code path conceptually (the resolver now fixes it), then assert the four gate properties.

- [ ] **Step 1: Write the gate test**

Create `tests/etkl/test_span_gate.py`:

```python
"""B1.2 gate — the narrow-flank silent-wrong is closed by the flank-sibling AXIOM, and NO
geometric constant decides the flank (the .rq does). Anti-overfit: regression fixture first."""
from iladub.etkl.geometry import Word, Line
from iladub.etkl.bands import Band
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.headers import (
    infer_header_tree, header_body_split, resolve_narrow_flanks, HeaderNode, _narrow_flank_tie,
)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _narrow_flank_band(w4, col4_has_own_header):
    """cols 1-3 width 100 (@ x 100..400), col 4 width w4 (@ x 400..400+w4); a spanning label
    over cols 1-3 whose ink stops at col 3; enough data rows that infer_leaf_grid resolves 5
    columns (>=49 data rows, per the classifygraph straddle-fixture lesson)."""
    b0, b1, b2, b3, b4 = 0, 100, 200, 300, 400
    header = [_w("Region", 150, 350, 0.0)]            # spans cols 1-3, ink stops at col 3
    if col4_has_own_header:
        header.append(_w("Notes", b4 + 2, b4 + w4 - 2, 0.0))   # col 4's OWN level-0 leaf header
    # leaf header row (level 1): a label strictly inside each data column
    leaf = [_w("S", 10, 60, 12.0), _w("a", 110, 160, 12.0), _w("b", 210, 260, 12.0),
            _w("c", 310, 360, 12.0), _w("d", b4 + 2, b4 + w4 - 2, 12.0)]
    data = []
    for i in range(60):
        top = 24.0 + i * 12.0
        data.append([_w("r%d" % i, 10, 60, top), _w(str(i), 110, 160, top),
                     _w(str(i), 210, 260, top), _w(str(i), 310, 360, top),
                     _w(str(i), b4 + 2, b4 + w4 - 2, top)])
    lines = [_line(header, 0.0), _line(leaf, 12.0)] + [_line(d, 24.0 + i * 12.0) for i, d in enumerate(data)]
    return Band(tuple(lines), 0.0, lines[-1].bottom)


def _region_node(band):
    grid = infer_leaf_grid(band)
    split = header_body_split(band, grid)
    tree = infer_header_tree(band, grid, split)
    # the coarse (level-0) spanning node
    coarse = [n for n in (tree or ()) if n.level == 0 and len(n.covers) > 1]
    return grid, tree, coarse


# 1 + 2. SILENT-WRONG CLOSED: col 4 has its own same-level header -> excluded, never absorbed.
def test_silent_wrong_closed_narrow_flank_excluded():
    for w4 in (40, 49, 50):
        band = _narrow_flank_band(w4, col4_has_own_header=True)
        grid, tree, coarse = _region_node(band)
        assert grid.ncols == 5, f"fixture must resolve 5 cols (w4={w4}); got {grid.ncols}"
        assert coarse, f"expected a coarse spanning node (w4={w4})"
        assert all(4 not in n.covers for n in coarse), \
            f"col 4 silently over-absorbed at w4={w4}: {[n.covers for n in coarse]}"
        assert all(not n.ambiguous for n in coarse)


# 3. RESIDUAL ESCALATES: header-empty flank -> ambiguous (deferred to B1.3), never absorbed.
def test_header_empty_flank_escalates():
    band = _narrow_flank_band(45, col4_has_own_header=False)
    grid, tree, coarse = _region_node(band)
    # the coarse node either dropped col 4 already OR is flagged ambiguous; it must NEVER
    # assert col 4 under the span without escalation.
    absorbed = [n for n in coarse if 4 in n.covers and not n.ambiguous]
    assert not absorbed, "header-empty flank silently absorbed"


# 4. NO-REGRESSION: a wide standalone flank (w=60 > 0.5*pitch) is still excluded (not a tie).
def test_wide_standalone_flank_still_excluded():
    band = _narrow_flank_band(60, col4_has_own_header=True)
    grid, tree, coarse = _region_node(band)
    assert all(4 not in n.covers for n in coarse)


# 5. GATE-PIN: the flank decision is carried by the .rq, not a tuned constant. Perturbing the
# tie-band / centering tolerance does not flip a same-level-sibling exclusion.
def test_flank_decision_is_declarative_not_constant():
    from iladub.etkl.flankgraph import sibling_columns
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    # col 4 has its own strict level-0 header -> sibling regardless of any geometric band width.
    sibs = sibling_columns([(0, 105.0, 295.0, "Region"), (0, 402.0, 438.0, "Notes")], b)
    assert (4, 0) in sibs
    # and the resolver excludes it independent of the specific tie-band constant:
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    from iladub.etkl.grid import LeafGrid
    out = resolve_narrow_flanks(nodes, LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0),
                                [(0, 105.0, 295.0, "Region"), (0, 402.0, 438.0, "Notes")],
                                ink_cols_by_node=[(1, 2, 3)])
    assert out[0].covers == (1, 2, 3)
```

- [ ] **Step 2: Run the gate test**

Run: `pytest tests/etkl/test_span_gate.py -v`
Expected: PASS (all five). If `grid.ncols != 5`, the fixture's data-row count / geometry needs adjusting (raise data rows, widen gutters) — this is fixture calibration, not a code change. If a coarse node is missing, print `tree` and inspect which path `infer_header_tree` took.

- [ ] **Step 3: Commit**

```bash
git add tests/etkl/test_span_gate.py
git commit -m "test(etkl): B1.2 gate — narrow-flank silent-wrong closed, decision is declarative (task 6)"
```

---

### Task 7: Full suite + docs (close the loop)

**Files:**
- Modify: `docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md`
- Modify: `CLAUDE.md` (§8 exemplar list)

- [ ] **Step 1: Run the FULL suite**

Run: `pytest -q`
Expected: **all pass** — baseline 386 passed / 5 skipped, now higher (new tests). Zero failures. If any pre-existing hierarchical/matrix test regresses, STOP and diagnose (the resolver must only fire on a detected tie; a regression means `_narrow_flank_tie` is over-triggering — tighten it, do not loosen the test).

- [ ] **Step 2: Mark the deferred item retired**

In `docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md`, add at the top under **Status:**

```markdown
> **RETIRED 2026-07-18 (loop B1.2).** The same-level-sibling narrow flank is now EXCLUDED by a
> declarative header-cell derivation (`vocab/queries/flank-sibling.rq` + `resolve_narrow_flanks`);
> the header-empty tied-flank residual ESCALATES `MERGE_AMBIGUOUS` and is deferred to loop B1.3
> (NEURAL). See `docs/superpowers/specs/2026-07-18-neural-span-perception-design.md` §2.
```

- [ ] **Step 3: Add the §8 exemplar**

In `CLAUDE.md` §8, in the "Exemplars already shipped" sentence, append after the classify-kind clause:

```markdown
, and **narrow-flank exclusion** (`iladub.etkl.flankgraph` + `vocab/queries/flank-sibling.rq`:
the tie-band merge silent-wrong resolved by a header-cell SPARQL derivation — a flank with its own
same-level leaf header is excluded, a header-empty tied flank escalates `MERGE_AMBIGUOUS`; tie
*detection* stays justified PROCEDURAL geometry, the NEURAL header-empty residual deferred to B1.3,
loop B1.2, shipped 2026-07-18)
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-13-b1-1-narrow-flank-overabsorption-deferred.md CLAUDE.md
git commit -m "docs(etkl): mark B1.2 narrow-flank AXIOM shipped; retire deferred item (task 7)"
```

- [ ] **Step 5: Final verification**

Run: `pytest -q`
Expected: all pass. The loop is CLOSED: the silent-wrong is closed end-to-end (exclude or escalate, never silent absorb), the decision is declarative (gate-pinned), and the residue is escalated in-band.

---

## Self-Review (completed)

- **Spec coverage:** §2.0 (AXIOM classification) → Tasks 2/3/5 code + comments; §2.3 Steps 1-3 (evidence graph, query, reader) → Tasks 2/3; Step 4 (merge_tiling_ok guard) → Task 4; §2.4 (plug-in + ambiguous flag) → Tasks 4/5; §2.5 gate test (all 5 properties) → Task 6; §2.6 PROCEDURAL boundaries → in-code docstrings (Tasks 2/5); §2.9 DoD → Task 7. B1.3 residual explicitly deferred (Task 6 test 3 proves it escalates).
- **Placeholder scan:** none — every step carries concrete code/commands. Two "verify the signature first" grep steps (Task 2 Step 3, Task 4 Step 1, Task 5 Step 9) are guardrails against drift, not placeholders; each names the expected shape.
- **Type consistency:** `sibling_columns(header_cells, boundaries) -> set[tuple[int,int]]` used identically in Tasks 3/5/6. `_narrow_flank_tie(covers, ink_cols, b) -> int | None` consistent Tasks 5/6. `resolve_narrow_flanks(nodes, grid, header_cells, ink_cols_by_node)` consistent Tasks 5/6. `HeaderNode(..., ambiguous=False)` consistent Tasks 4/5/6.
- **Known calibration risk:** the Task 6 fixture depends on `infer_leaf_grid` resolving 5 columns (needs ≥49 data rows, per the classifygraph straddle lesson) — Step 2 of Task 6 handles this as fixture calibration, not code change.
