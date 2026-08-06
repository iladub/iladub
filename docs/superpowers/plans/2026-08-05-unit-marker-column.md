# Unit-Marker Column Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A borderless column whose every non-blank cell is the same currency symbol is recognized (AXIOM), absorbed as a unit marker on its numeric right neighbor (carried with provenance, never dropped), and the grid re-derived — measured on apple p0 (ncols 9 → 5, ≥ 1 band flips to asserted).

**Doc impact:** none for this plan file itself — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-05-unit-marker-column-design.md`), which queues the wiki concept note.

**Architecture:** A new focused module `src/iladub/etkl/unitmarker.py` owns the two-pass absorption: pass-1 grid (`recover_leaf_grid`) → dedicated typed-cell evidence (marker-local `tab:CurrencyGlyph` typing — deliberately NOT added to the shared `celltype._cell_datatype`, so every existing query's verdicts stay byte-identical by construction) → new AXIOM `vocab/queries/unit-marker-column.rq` derives marker columns → marker words filtered out of the band, markers carried on a new `Band.unit_markers` field (the `Band.captions` precedent) → grid re-derives downstream as usual. Wired once in `page_bands` (the single band seam both compile and continuation recognition read), borderless bands only. At assert time a new `_emit_unit_markers` in `compile.py` attaches `tab:hasUnitMarker` → `tab:UnitMarker` node (symbol + provenance regions) to the surviving neighbor column URI, alongside the existing `_emit_band_captions` calls.

**Tech Stack:** Python 3 / pytest, rdflib SPARQL, pySHACL, reportlab (fixtures).

**Spec:** `docs/superpowers/specs/2026-08-05-unit-marker-column-design.md` — read it first.

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §0.8):** the recognition decision lives ONLY in `unit-marker-column.rq` (AXIOM). `unitmarker.py` may contain raw typing (`is_currency_glyph` — a symbol-set membership test reusing B2b's shipped `[$€£¥]`, no new constant) and engine glue (evidence emission, word filtering, grid re-derivation). Any decision logic in Python, or any tuned constant/tolerance, is a defect.
- **Byte-identity by construction:** the shared `celltype._cell_datatype` is NOT modified (a bare `$` stays `tab:Text` in every existing query's evidence). Bands with `band.rules` are NEVER absorbed (the ruled path is untouched). Any band with no derived marker column passes through `absorb_unit_markers` unchanged (same object or equal Band).
- **The R19 domain-inference trap:** the marker node's provenance MUST use the new property `tab:markerRegion` — NEVER `tab:hasBBox`, whose RDFS domain types its subject as `tab:Cell` and would trip the gate's `tab:WrappedCellShape` (bbox + no cellText) on every marker node.
- **§5/§7:** marker ink is carried (symbol + provenance regions), never silently dropped; bands still blocked by the spec §6 classes keep escalating honestly; never tune anything toward the apple score — record the measured number.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …` (applies to subagents).
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (space in path — quote it).
- **Branch:** `loop-unit-marker` off `main` (created in Task 1, Step 0).
- **Never lower a corpus floor or weaken a pin.** Stem 0.9655 / CBH 0.9047 must be byte-identical.

---

### Task 1: The recognition AXIOM — evidence emitter + query, cells-level TDD

**Files:**
- Create: `src/iladub/etkl/unitmarker.py`
- Create: `vocab/queries/unit-marker-column.rq`
- Create: `tests/etkl/test_unit_marker.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`-style evidence building (but with its OWN datatype function), `celltype._cell_datatype` (fallback for non-glyph cells), `TAB` namespace (`https://w3id.org/iladub/tab#`).
- Produces (Task 2 relies on these exact names): `unitmarker.is_currency_glyph(s: str) -> bool`; `unitmarker.marker_evidence(cells, ncols) -> rdflib.Graph` (cells = `(row, col, text)` triples, the same shape `headers._grid_cells` returns); `unitmarker.derive_marker_columns(cells, ncols) -> tuple[tuple[int, str], ...]` (sorted `(column_index, symbol)` pairs, empty tuple when none).

- [ ] **Step 0: Branch**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git checkout -b loop-unit-marker main
```

- [ ] **Step 1: Write the failing cells-level tests** — create `tests/etkl/test_unit_marker.py`:

```python
"""The accounting currency-marker column (spec 2026-08-05-unit-marker-column-design.md).

A borderless column whose every non-blank cell is the SAME currency symbol is a unit
marker on its numeric right neighbor, not a column of the table. Recognition is the
unit-marker-column.rq AXIOM over a DEDICATED typed-cell evidence graph (marker-local
tab:CurrencyGlyph typing — the shared celltype lattice is deliberately untouched so
every existing query stays byte-identical). Measured driver: apple p0, where `$`
columns fabricate ncols=9 for a 5-column statement."""
from iladub.etkl.unitmarker import derive_marker_columns

# The apple accounting shape: label col 0, `$` marker col 1 (first + total rows only),
# numeric value col 2.
APPLE_SHAPE = [
    (0, 0, "Net sales:"),
    (1, 0, "Products"), (1, 1, "$"), (1, 2, "78,678"),
    (2, 0, "Services"),              (2, 2, "30,739"),
    (3, 0, "Total net sales"), (3, 1, "$"), (3, 2, "109,417"),
]


def test_same_symbol_column_with_numeric_neighbor_is_derived():
    assert derive_marker_columns(APPLE_SHAPE, 3) == ((1, "$"),)


def test_footnote_star_column_is_refused():
    # `*` is not a currency symbol — the column stays an ordinary column.
    cells = [(r, c, t if t != "$" else "*") for (r, c, t) in APPLE_SHAPE]
    assert derive_marker_columns(cells, 3) == ()


def test_mixed_symbols_are_refused():
    # $ and € in one column: not the SAME symbol -> no absorption.
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "10"), (2, 1, "€"), (2, 2, "20")]
    assert derive_marker_columns(cells, 3) == ()


def test_symbol_column_without_numeric_neighbor_is_refused():
    cells = [(0, 0, "x"), (1, 1, "$"), (1, 2, "abc"), (2, 1, "$"), (2, 2, "def")]
    assert derive_marker_columns(cells, 3) == ()


def test_column_with_any_non_symbol_cell_is_refused():
    # One stray text cell among the symbols disqualifies the whole column.
    cells = APPLE_SHAPE + [(2, 1, "note")]
    assert derive_marker_columns(cells, 3) == ()


def test_blank_cells_do_not_disqualify():
    # Blanks are wildcards, exactly as in the split query's Blank convention.
    cells = APPLE_SHAPE + [(2, 1, "-")]
    assert derive_marker_columns(cells, 3) == ((1, "$"),)


def test_two_marker_columns_both_derive():
    cells = [
        (0, 0, "A"), (0, 1, "$"), (0, 2, "10"), (0, 3, "$"), (0, 4, "20"),
        (1, 0, "B"), (1, 1, "$"), (1, 2, "11"), (1, 3, "$"), (1, 4, "21"),
    ]
    assert derive_marker_columns(cells, 5) == ((1, "$"), (3, "$"))
```

- [ ] **Step 2: Run — verify red**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.etkl.unitmarker'`.

- [ ] **Step 3: Write the query** — create `vocab/queries/unit-marker-column.rq`:

```sparql
# unit-marker-column.rq — the accounting currency-marker column (AXIOM, open world).
# A grid column ?col is a UNIT MARKER for its right neighbor iff:
#   (1) it has >=1 tab:CurrencyGlyph cell, and every non-Blank cell in it is a
#       CurrencyGlyph carrying the SAME symbol text (Blank cells are wildcards,
#       the split query's convention);
#   (2) the right neighbor column (?col + 1) carries >=1 Numeric or Currency cell.
# Presence-based: no distance, no count, no tolerance. The symbol set lives in the
# emitter's is_currency_glyph (B2b's shipped [$€£¥] class, reused — no new constant);
# this query reads only the emitted tab:CurrencyGlyph datatype facts.
# Consumed by unitmarker.derive_marker_columns; evidence = unitmarker.marker_evidence.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT DISTINCT ?col ?sym WHERE {
  ?c1 tab:atGridColumn ?col ; tab:cellDatatype tab:CurrencyGlyph ; tab:gridText ?sym .
  FILTER NOT EXISTS {
    ?cx tab:atGridColumn ?col ; tab:cellDatatype ?dx .
    FILTER(?dx != tab:CurrencyGlyph && ?dx != tab:Blank)
  }
  FILTER NOT EXISTS {
    ?cy tab:atGridColumn ?col ; tab:cellDatatype tab:CurrencyGlyph ; tab:gridText ?sy .
    FILTER(STR(?sy) != STR(?sym))
  }
  BIND(?col + 1 AS ?nc)
  FILTER EXISTS {
    ?cn tab:atGridColumn ?nc ; tab:cellDatatype ?dn .
    FILTER(?dn = tab:Numeric || ?dn = tab:Currency)
  }
}
ORDER BY ?col
```

- [ ] **Step 4: Write the module** — create `src/iladub/etkl/unitmarker.py`:

```python
"""unitmarker — the accounting currency-marker column (spec 2026-08-05).

A borderless column whose every non-blank cell is the SAME currency symbol is a unit
marker on its numeric right neighbor, not a column of the table (US accounting style:
`$` at the column edge, value right-aligned beside it, drawn on first/total rows only).
The compiler read it as a 1-2-cell Text column, fabricating grid columns (apple p0:
ncols 9 for a 5-column statement) and failing tiling.

Gate classification (§8): the DECISION ("is column c a unit marker for c+1?") is the
unit-marker-column.rq AXIOM over a dedicated typed-cell evidence graph. This module is
PROCEDURAL only: raw glyph typing (is_currency_glyph — B2b's shipped [$€£¥] symbol
class, reused, no new constant), evidence emission, and (in absorb_unit_markers, task
2) word filtering + re-derivation. The shared celltype._cell_datatype is DELIBERATELY
not extended: a global tab:CurrencyGlyph would change homogeneity verdicts in every
existing query (a bare `$` inside a mixed column would stop being Text); marker-local
typing keeps every existing verdict byte-identical by construction.
"""
from __future__ import annotations

import os

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .celltype import _cell_datatype, is_blank

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")
_RQ = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                   "vocab", "queries", "unit-marker-column.rq")

_CURRENCY_SYMBOLS = frozenset("$€£¥")   # B2b's _CURRENCY symbol class, verbatim


def is_currency_glyph(s: str) -> bool:
    """The cell is exactly one currency symbol (B2b's shipped set). PROCEDURAL raw
    typing, like celltype.is_currency."""
    return s.strip() in _CURRENCY_SYMBOLS


def _marker_datatype(t: str):
    """Marker-local typing: CurrencyGlyph first, else the shared lattice."""
    if not is_blank(t) and is_currency_glyph(t):
        return TAB.CurrencyGlyph
    return _cell_datatype(t)


def marker_evidence(cells, ncols) -> Graph:
    """The dedicated typed-cell evidence graph for the marker AXIOM. Same shape as
    celltype.grid_evidence, with _marker_datatype in place of _cell_datatype."""
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["umcell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, _marker_datatype(t)))
    for c in range(ncols):
        g.add((_EV["umcol-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    return g


def derive_marker_columns(cells, ncols) -> tuple[tuple[int, str], ...]:
    """The derived (column_index, symbol) pairs, sorted by column. Empty when none."""
    g = marker_evidence(cells, ncols)
    with open(_RQ, encoding="utf-8") as f:
        q = f.read()
    return tuple(sorted((int(row[0]), str(row[1])) for row in g.query(q)))
```

- [ ] **Step 5: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py -v`
Expected: 7 PASS.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/unitmarker.py vocab/queries/unit-marker-column.rq tests/etkl/test_unit_marker.py && git commit -m "feat(loop-unitmarker): unit-marker-column AXIOM + marker-local evidence (cells-level TDD)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Absorption — word filtering, the Band carry, the page_bands wiring

**Files:**
- Modify: `src/iladub/etkl/bands.py` (one field on `Band`)
- Modify: `src/iladub/etkl/unitmarker.py` (add `absorb_unit_markers`)
- Modify: `src/iladub/etkl/compile.py` (`page_bands` — wire the absorption, borderless bands only)
- Modify: `tests/etkl/fixtures.py` (one fixture)
- Modify: `tests/etkl/test_unit_marker.py` (band-level + compile-level tests)

**Interfaces:**
- Consumes: Task 1's `derive_marker_columns`; `cells.recover_leaf_grid(band)`; `headers._grid_cells(band, grid)`; `dataclasses.replace`.
- Produces: `Band.unit_markers: tuple = ()` — entries `(symbol: str, neighbor_x: float, regions: tuple[tuple[float, float, float, float], ...])` where `neighbor_x` is the midpoint of the neighbor column's pass-1 interval and each region is the marker word's `(x0, top, x1, bottom)`; `unitmarker.absorb_unit_markers(band) -> Band` (identity for ruled bands, bands with `ncols < 2`, and bands with no derived marker). Task 3 reads `band.unit_markers` at emit time.

- [ ] **Step 1: Add the Band field** — in `src/iladub/etkl/bands.py`, after the `captions` field:

```python
    # Absorbed currency-marker columns (spec 2026-08-05-unit-marker-column-design.md):
    # (symbol, neighbor_x, regions) per absorbed column — the marker ink CARRIED (§5),
    # emitted at assert time as tab:hasUnitMarker on the neighbor column. Default empty
    # so every existing constructor stands (the Band.captions precedent).
    unit_markers: tuple = ()
```

- [ ] **Step 2: Write the failing band-level tests** — append to `tests/etkl/test_unit_marker.py`:

```python
# ---------------------------------------------------------------- absorption

def _mkband(rows, cols):
    """A synthetic borderless Band: rows = list of {col_index: text}, cols = left x
    per column (Courier-ish 40pt-wide words at exact x positions)."""
    from iladub.etkl.geometry import Word, Line
    from iladub.etkl.bands import Band
    lines = []
    for r, row in enumerate(rows):
        top = 100.0 + r * 14.0
        words = tuple(Word(text=t, x0=cols[c], x1=cols[c] + max(8.0, 6.0 * len(t)),
                           top=top, bottom=top + 10.0)
                      for c, t in sorted(row.items()))
        lines.append(Line(words=words, top=top, bottom=top + 10.0))
    return Band(tuple(lines), lines[0].top, lines[-1].bottom)


APPLE_BAND_ROWS = [
    {0: "Label", 2: "Amount", 4: "Total"},
    {0: "Products", 1: "$", 2: "78,678", 3: "$", 4: "272,629"},
    {0: "Services", 2: "30,739", 4: "91,728"},
    {0: "Other", 2: "11,729", 4: "34,035"},
    {0: "Sum", 1: "$", 2: "121,146", 3: "$", 4: "398,392"},
]
APPLE_BAND_COLS = {0: 72.0, 1: 220.0, 2: 260.0, 3: 380.0, 4: 420.0}


def test_absorb_removes_marker_words_and_carries_them():
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = _mkband(APPLE_BAND_ROWS, APPLE_BAND_COLS)
    out = absorb_unit_markers(band)
    texts = [w.text for ln in out.lines for w in ln.words]
    assert "$" not in texts                       # the glyphs left the word stream
    assert len(out.unit_markers) == 2             # one per absorbed column
    syms = sorted(m[0] for m in out.unit_markers)
    assert syms == ["$", "$"]
    # provenance: each marker carries one region per absorbed glyph (2 rows drew $)
    assert all(len(m[2]) == 2 for m in out.unit_markers)
    # neighbor_x falls inside the value column's x-range
    assert any(260.0 <= m[1] <= 380.0 for m in out.unit_markers)


def test_absorb_is_identity_without_markers():
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = _mkband([{0: "A", 1: "10"}, {0: "B", 1: "20"}, {0: "C", 1: "30"}],
                   {0: 72.0, 1: 200.0})
    out = absorb_unit_markers(band)
    assert out.unit_markers == ()
    assert [w.text for ln in out.lines for w in ln.words] == \
           [w.text for ln in band.lines for w in ln.words]


def test_absorb_is_identity_for_ruled_bands():
    from dataclasses import replace
    from iladub.etkl.geometry import Rule
    from iladub.etkl.unitmarker import absorb_unit_markers
    band = replace(_mkband(APPLE_BAND_ROWS, APPLE_BAND_COLS),
                   rules=(Rule(x=250.0, top=100.0, bottom=170.0),))
    assert absorb_unit_markers(band) is band
```

NOTE for the implementer: check `geometry.Word`, `geometry.Line`, and `geometry.Rule`'s actual constructor signatures before running (Read `src/iladub/etkl/geometry.py`) and adapt the helper's keyword names to the real dataclass fields — the SHAPE of the test (marker words removed, two markers carried, identity cases) is the requirement, the constructor spelling is not.

- [ ] **Step 3: Run — verify red**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py -v`
Expected: the three new tests FAIL (`absorb_unit_markers` not defined); Task 1's seven still PASS.

- [ ] **Step 4: Implement `absorb_unit_markers`** — append to `src/iladub/etkl/unitmarker.py`:

```python
def absorb_unit_markers(band):
    """Two-pass absorption (the loop-G candidates pattern): pass-1 grid -> AXIOM ->
    marker words filtered out, markers carried on Band.unit_markers -> downstream
    re-derives the grid on the remainder. Identity for ruled bands (the author drew
    those columns), narrow grids, and bands with no derived marker. PROCEDURAL
    engine glue; the decision is the query's."""
    from dataclasses import replace
    from .cells import recover_leaf_grid
    from .headers import _grid_cells

    if band.rules:
        return band
    grid = recover_leaf_grid(band)
    if grid.ncols < 2:
        return band
    cells = _grid_cells(band, grid)
    derived = derive_marker_columns(cells, grid.ncols)
    if not derived:
        return band

    b = grid.boundaries
    markers = []
    drop = set()
    for col, sym in derived:
        regions = []
        for ln in band.lines:
            for w in ln.words:
                cx = (w.x0 + w.x1) / 2.0
                if b[col] <= cx < b[col + 1] and w.text.strip() == sym:
                    drop.add(id(w))
                    regions.append((w.x0, w.top, w.x1, w.bottom))
        neighbor_x = (b[col + 1] + b[col + 2]) / 2.0
        markers.append((sym, neighbor_x, tuple(regions)))

    new_lines = []
    for ln in band.lines:
        kept = tuple(w for w in ln.words if id(w) not in drop)
        if kept:
            new_lines.append(replace(ln, words=kept))
    return replace(band, lines=tuple(new_lines), unit_markers=tuple(markers))
```

(If `Line` derives fields from `words` in `__post_init__` or is not a plain frozen dataclass, adapt the rebuild to the real class — the invariant is: same lines minus the marker words, empty lines dropped, all other Band fields preserved.)

- [ ] **Step 5: Wire into `page_bands`** — in `src/iladub/etkl/compile.py`, inside `page_bands`, at the point where the final band list is assembled (after section repair / ruled-band construction — find the `return` of the band list), map each band through the absorption:

```python
    from .unitmarker import absorb_unit_markers
    bands = [absorb_unit_markers(b) for b in bands]
```

Placement rule: AFTER every existing band-construction step (so ruled bands already carry `rules` and are skipped by the identity guard) and BEFORE the return — `page_bands` is the single seam both `compile_tables` and the document driver's continuation recognition read, so both see the absorbed bands consistently. Preserve the existing variable names; if the function returns an expression rather than a named list, introduce the local.

- [ ] **Step 6: Run — verify green + no regression in the near suite**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py tests/etkl/test_grid_region.py tests/etkl/test_header_stack.py tests/etkl/test_invalid_split_refusal.py -q`
Expected: all PASS (the identity guards keep every existing fixture byte-identical).

- [ ] **Step 7: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/unitmarker.py src/iladub/etkl/bands.py src/iladub/etkl/compile.py tests/etkl/test_unit_marker.py && git commit -m "feat(loop-unitmarker): absorb marker columns at the page_bands seam, carried on Band.unit_markers

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Vocabulary, emission, membrane, example pair, compile-level fixture

**Files:**
- Modify: `vocab/ontology/tab.ttl` (new terms)
- Modify: `vocab/shapes/tab-shapes.ttl` (`tab:UnitMarkerShape`)
- Modify: `src/iladub/etkl/compile.py` (`_emit_unit_markers` + calls at the five assert sites)
- Create: `examples/tables/unit-marker.ttl`
- Modify: `tests/etkl/fixtures.py` (`currency_marker_column_pdf`)
- Modify: `tests/etkl/test_unit_marker.py` (emission + membrane + compile tests)

**Interfaces:**
- Consumes: Task 2's `Band.unit_markers`; `regions.column_of(x, boundaries)`; the `TAB` namespace in `compile.py`.
- Produces: graph facts `<{table}-c{col}> tab:hasUnitMarker <{table}-um{k}>`; `tab:UnitMarker` node with `tab:markerSymbol` (literal) and ≥1 `tab:markerRegion` → `tab:BBox` node (`tab:x0/y0/x1/y1` — mirror the exact coordinate property names `holon.py`'s existing BBox emission uses; Read it first). NEVER `tab:hasBBox` on the marker node (Global Constraints: the R19 trap).

- [ ] **Step 1: Vocabulary** — in `vocab/ontology/tab.ttl`, mirroring the file's existing declaration style (Read the `tab:Numeric`/`tab:RegionCaption` declarations first and copy their idiom):
  - `tab:CurrencyGlyph` — declared exactly as the other `tab:cellDatatype` values (`tab:Numeric`, `tab:Blank`, …) are declared, with a comment: "a cell that is exactly one currency symbol; emitted only by the unit-marker evidence (unitmarker.py), deliberately absent from the shared celltype lattice".
  - `tab:UnitMarker` a class ("an absorbed currency-marker column: unit evidence carried on its neighbor column, spec 2026-08-05").
  - `tab:hasUnitMarker` a property (subject: a leaf column; object: `tab:UnitMarker`).
  - `tab:markerSymbol` a datatype property.
  - `tab:markerRegion` a property (object: `tab:BBox`) with the comment: "deliberately NOT tab:hasBBox — that property's domain would RDFS-type the marker as tab:Cell and trip tab:WrappedCellShape at the gate (the R19 mechanism)".

- [ ] **Step 2: Membrane shape** — in `vocab/shapes/tab-shapes.ttl`, following the file's house style:

```turtle
tab:UnitMarkerShape a sh:NodeShape ;
    sh:targetClass tab:UnitMarker ;
    sh:property [ sh:name "UnitMarkerShape" ; sh:path tab:markerSymbol ;
                  sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:name "UnitMarkerShape" ; sh:path tab:markerRegion ;
                  sh:minCount 1 ] .
```

(It joins `compile._validate`'s full-set validation automatically — `tab-shapes.ttl` is parsed whole; it is NOT added to the region gate's `_TILING_SHAPE_IRIS`/`_PHYSICAL_SHAPE_IRIS` lists.)

- [ ] **Step 3: Failing emission + membrane + compile tests** — append to `tests/etkl/test_unit_marker.py`:

```python
# ---------------------------------------------------------------- emission + membrane

def test_marker_facts_emitted_with_provenance(tmp_path):
    from rdflib import Namespace, RDF
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import currency_marker_column_pdf
    TAB = Namespace("https://w3id.org/iladub/tab#")
    pdf = str(tmp_path / "marker.pdf")
    currency_marker_column_pdf(pdf)
    rep = compile_tables(pdf, page_number=0)
    assert any(r.verdict == "asserted" for r in rep.regions), \
        [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    markers = list(rep.graph.subjects(RDF.type, TAB.UnitMarker))
    assert markers, "no tab:UnitMarker emitted"
    for m in markers:
        assert list(rep.graph.objects(m, TAB.markerSymbol)) == \
               [x for x in rep.graph.objects(m, TAB.markerSymbol)]  # present
        assert list(rep.graph.objects(m, TAB.markerRegion)), "marker without provenance"
        assert not list(rep.graph.objects(m, TAB.hasBBox)), \
            "R19 trap: marker must never carry tab:hasBBox"
        cols = list(rep.graph.subjects(TAB.hasUnitMarker, m))
        assert len(cols) == 1, "marker must hang off exactly one column"


def test_unit_marker_shape_negative():
    # The membrane refuses a marker without provenance (the example pair's negative half).
    from pyshacl import validate
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    m = URIRef("urn:um:bad")
    g.add((m, RDF.type, TAB.UnitMarker))
    g.add((m, TAB.markerSymbol, Literal("$")))          # no markerRegion
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, _ = validate(g, shacl_graph=shapes, advanced=True)
    assert not conforms


def test_example_pair_conforms():
    from pyshacl import validate
    from rdflib import Graph
    g = Graph().parse("examples/tables/unit-marker.ttl", format="turtle")
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, report = validate(g, shacl_graph=shapes, advanced=True)
    assert conforms, report
```

- [ ] **Step 4: The PDF fixture** — append to `tests/etkl/fixtures.py`:

```python
def currency_marker_column_pdf(path: str) -> dict:
    """The accounting $-marker column, synthetic (spec 2026-08-05): a borderless
    record table whose value columns carry a `$` glyph column on the first and last
    data rows only (US financial-statement style). Pre-loop the glyph columns
    fabricate grid columns and the band fails tiling / mis-reads; post-loop the
    markers absorb, the grid recovers the true 3 columns, and the band asserts with
    tab:hasUnitMarker facts."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    rows = [
        ("Item",     "",  "Amount",  "",  "Total"),
        ("Products", "$", "78,678",  "$", "272,629"),
        ("Services", "",  "30,739",  "",  "91,728"),
        ("Other",    "",  "11,729",  "",  "34,035"),
        ("Overall",  "$", "121,146", "$", "398,392"),
    ]
    xs = [72.0, 220.0, 260.0, 380.0, 420.0]
    y0 = PAGE_H - 100.0
    for i, row in enumerate(rows):
        y = y0 - i * 14.0
        for x, t in zip(xs, row):
            if t:
                c.drawString(x, y, t)
    c.save()
    return {"cols": xs, "n_rows": len(rows)}
```

- [ ] **Step 5: Run — verify red** (emission tests fail: no emitter yet; the compile test may already partially pass on assertion but MUST fail on the missing `tab:UnitMarker` facts)

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py -v`

- [ ] **Step 6: The emitter** — in `src/iladub/etkl/compile.py`, next to `_emit_band_captions`:

```python
def _emit_unit_markers(graph, table_uri, band, boundaries):
    """Spec 2026-08-05 §4 carry: one tab:UnitMarker per absorbed currency-marker
    column, attached to the SURVIVING neighbor column's URI (resolved against the
    FINAL grid boundaries via the carried neighbor_x). Provenance rides
    tab:markerRegion -> tab:BBox — deliberately NOT tab:hasBBox, whose rdfs:domain
    would type the marker as tab:Cell and trip WrappedCellShape at the gate (R19)."""
    from rdflib import Literal, RDF, URIRef
    from rdflib.namespace import XSD
    from .regions import column_of
    for k, (sym, neighbor_x, regions) in enumerate(getattr(band, "unit_markers", ()) or ()):
        col = column_of(neighbor_x, boundaries)
        um = URIRef("%s-um%d" % (table_uri, k))
        graph.add((um, RDF.type, TAB.UnitMarker))
        graph.add((um, TAB.markerSymbol, Literal(sym)))
        for j, (x0, top, x1, bottom) in enumerate(regions):
            bb = URIRef("%s-um%d-r%d" % (table_uri, k, j))
            graph.add((bb, RDF.type, TAB.BBox))
            graph.add((bb, TAB.x0, Literal(float(x0), datatype=XSD.decimal)))
            graph.add((bb, TAB.y0, Literal(float(top), datatype=XSD.decimal)))
            graph.add((bb, TAB.x1, Literal(float(x1), datatype=XSD.decimal)))
            graph.add((bb, TAB.y1, Literal(float(bottom), datatype=XSD.decimal)))
            graph.add((um, TAB.markerRegion, bb))
        graph.add((URIRef("%s-c%d" % (table_uri, col)), TAB.hasUnitMarker, um))
```

FIRST verify against `holon.py`: (a) the BBox coordinate property names (`tab:x0/y0/x1/y1` — Read the existing BBox emission and mirror it exactly), and (b) that every assert path mints leaf-column URIs as `{table_uri}-c{index}` — if any path differs, resolve the column URI from the scratch graph (`tab:hasLeafColumn` + index order) instead of string-minting, and say so in the report.

- [ ] **Step 7: Call it at the five assert sites** — in `compile_tables`, immediately after each existing `_emit_band_captions(graph, table_uri, band)` call (transposed, row-hier, record, matrix, hierarchical — including the ruled-reading branch), add:

```python
                    _emit_unit_markers(graph, table_uri, band, <that branch's grid>.boundaries)
```

where `<that branch's grid>` is the branch's own region/mreg/rreg/hreg grid (each branch already has it in scope — e.g. `region.grid`, `mreg.grid`, `hreg.grid`). The ruled-reading branch uses `hreg.grid`.

- [ ] **Step 8: The example pair** — create `examples/tables/unit-marker.ttl` (conformant half; the negative half is `test_unit_marker_shape_negative`):

```turtle
@prefix tab: <https://w3id.org/iladub/tab#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Worked example — the accounting currency-marker column (spec 2026-08-05).
# A `$` column absorbed as unit evidence on its value column: the marker carries its
# symbol and provenance to the source glyphs; the column carries the marker.
<urn:example:um:table0-c1> tab:hasUnitMarker <urn:example:um:table0-um0> .
<urn:example:um:table0-um0> a tab:UnitMarker ;
    tab:markerSymbol "$" ;
    tab:markerRegion <urn:example:um:table0-um0-r0> .
<urn:example:um:table0-um0-r0> a tab:BBox ;
    tab:x0 220.0 ; tab:y0 692.0 ; tab:x1 228.0 ; tab:y1 702.0 .
```

(Adapt the coordinate property names to whatever Step 6's holon.py check found.)

- [ ] **Step 9: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_unit_marker.py -q`
Expected: all PASS.

- [ ] **Step 10: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl src/iladub/etkl/compile.py examples/tables/unit-marker.ttl tests/etkl/fixtures.py tests/etkl/test_unit_marker.py && git commit -m "feat(loop-unitmarker): tab:UnitMarker vocabulary, emission with provenance, membrane shape + example pair

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Measurement + no-regression + close

**Files:**
- Modify: `docs/superpowers/specs/2026-08-05-unit-marker-column-design.md` (status line with measured numbers)
- Modify: `docs/superpowers/residues.md` (ONLY if a §6 class is measured blocking a band that would otherwise now read — then a new row per the house format)

- [ ] **Step 1: The apple measurement**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/financial/apple-fy2026q3-statements.pdf")
print(f"score={rep.score:.4f} (pre-loop 0.0106) wall={time.monotonic()-t0:.0f}s")
for i, p in enumerate(rep.pages):
    print(f"  p{i} score={p.score:.4f}: {[(r.kind.name, r.verdict, r.reason, r.cells) for r in p.regions]}")
EOF
```

Expected (the spec §7 floor): document score strictly > 0.0106; on p0 at least one section band asserted (band 4.0's `Operating income…Net income` block, 31 cells, was the measured pre-verified floor). Record the FULL output verbatim in the report. If the score does NOT move, that is a measured result — report it, do not tune anything.

- [ ] **Step 2: Battery + pins**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest "tests/test_corpus.py::test_expected_verdict[financial/apple-fy2026q3-statements.pdf]" -v -s && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q`
Expected: apple passes (Unadjudicated gate) with the new region record printed; stem/CBH pin counts identical to main (stem 0.9655, CBH 0.9047 — byte-identity is the no-regression proof; the absorption runs on every borderless band of every document).

- [ ] **Step 3: Full suite**

Run: `export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6`
Expected: 0 failed attributable to the branch (the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag` failure is pre-existing — bare env dict without PATH hits the broken local git shim; verify nothing NEW is red). Slow (~20 min); export the PATH prefix so the git-subprocess docgov tests run.

- [ ] **Step 4: Spec status + (conditional) register rows**

Update the spec's `**Status:**` line to `closed 2026-08-05 — apple <measured score> (pre-loop 0.0106), p0 <N> bands asserted, ncols 9→5; stem/CBH byte-identical` with the real numbers. If Step 1's measurement shows a band now blocked ONLY by a spec-§6 class (the one-word `$ 45,781` homogeneity form, `(171)` accounting negatives, the detached-header/caption class beyond what is already registered, R16), add a register row for any such class that has no existing row (R16 and the caption class have rows/coverage — check before adding; the homogeneity form and `(171)` do not). House format: measured evidence, why deferred, what would close it.

- [ ] **Step 5: Doc-governance lint + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/specs/2026-08-05-unit-marker-column-design.md docs/superpowers/residues.md && git commit -m "docs(loop-unitmarker): close — apple measured, spec status, register rows per measurement

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 6: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-05)

- **Spec coverage:** §3 AXIOM → Task 1; §4 two-pass + carry + emission → Tasks 2–3; §4 membrane/example pair → Task 3; §5 guards → Task 1's negative tests + Task 2's identity tests; §7 success criteria → Task 4; §6 out-of-scope → Task 4 Step 4's conditional register rows.
- **Placeholder scan:** the constructor-adaptation notes in Tasks 2/3 are deliberate verify-against-source instructions (the geometry/holon dataclass spellings must be read, not guessed), each with the invariant stated; no TBDs.
- **Type consistency:** `derive_marker_columns(cells, ncols) -> tuple[tuple[int, str], ...]` (Task 1) consumed in Task 2; `Band.unit_markers` entries `(symbol, neighbor_x, regions)` (Task 2) consumed by `_emit_unit_markers` (Task 3); fixture name `currency_marker_column_pdf` consistent between Task 3 Steps 3/4.
