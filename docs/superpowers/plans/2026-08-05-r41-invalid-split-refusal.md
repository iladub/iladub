# R41 — Invalid Header/Body Split Refusal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The `header-body-split.rq` AXIOM refuses a split with zero body rows, turning the apple-document crash (`IndexError` at `headers.py:400`) into the existing honest escalation.

**Architecture:** One validity clause added to an existing open-world SPARQL derivation (`vocab/queries/header-body-split.rq`), mirrored in its committed Python reference (`_ref_hbs` in `tests/etkl/test_derivation_equiv.py`). No new escalation plumbing: an empty query result already returns `None` from `header_body_split`, falls back to `_hrule_split`, and escalates through `classify_hierarchical`'s normal `None` path (`KIND_NOT_SUPPORTED` at `compile.py:596-606`). TDD from a synthetic apple-shaped fixture; the corpus battery's red apple entry is the end-to-end gate.

**Tech Stack:** Python 3 / pytest, rdflib SPARQL, reportlab (test fixtures), pdfplumber (geometry).

**Spec:** `docs/superpowers/specs/2026-08-05-r41-invalid-split-refusal-design.md` — read it first.

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §0.8):** the fix is a clause in an existing AXIOM. Any new procedural Python beyond test fixtures is a defect. No tuned constant anywhere — the clause is presence-based (`?s_col <= MAX(evidence row)`).
- **§7 credibility over completeness:** never make the apple sub-table *read*; it must escalate honestly. Currency-aware cell typing is explicitly OUT OF SCOPE (spec §4).
- **No overfitting (zero tolerance):** the clause is a validity condition, not an apple-shaped special case. The randomized equivalence battery + stem/CBH byte-identity pins are the generalization evidence.
- **Broken system git on this machine:** every git-touching command MUST be run as `export PATH=/opt/homebrew/bin:$PATH && git …` (Xcode CLT shim is broken). This applies to subagents too.
- **Never lower a corpus floor or weaken a pin to force green.** If a measurement disagrees with an expectation, report the measurement.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (note the space in the path — quote it in shell commands).
- **Branch:** work on `loop-r41-invalid-split` off `main` (create it in Task 1, Step 0).

---

### Task 1: Red tests — the crash pinned at three levels

**Files:**
- Modify: `tests/etkl/fixtures.py` (append one fixture function)
- Create: `tests/etkl/test_invalid_split_refusal.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence(cells, ncols)`, `celltype.run_scalar(query_path, graph)` (both existing; see `tests/etkl/test_header_body_split_robust.py` for the idiom), `classify_hierarchical(band)`, `compile_tables(pdf_path, page_number=0)`.
- Produces: fixture `currency_sandwich_pdf(path: str) -> dict` in `tests/etkl/fixtures.py`; test module `tests/etkl/test_invalid_split_refusal.py` with tests `test_axiom_refuses_past_the_end_split`, `test_classify_hierarchical_returns_instead_of_raising`, `test_compile_returns_instead_of_crashing`. Task 2 runs these to green; do not rename them.

- [ ] **Step 0: Branch**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git checkout -b loop-r41-invalid-split main
```

- [ ] **Step 1: Add the PDF fixture to `tests/etkl/fixtures.py`** (append at end of file; follows the module's reportlab idiom — Courier, borderless, exact x/y):

```python
def currency_sandwich_pdf(path: str) -> dict:
    """R41's crash shape, synthetic (no third-party PDF): a caption line over a table whose
    data columns are $-SANDWICHED — first and last body rows Currency ('$ 45,781'-style),
    interior rows bare Numeric. Modal body type = Numeric, so the mismatch scan's
    s_col = MAX(mismatch row)+1 lands one PAST the band in EVERY data column and
    header-body-split.rq (pre-fix) returns split == len(band.lines) — the out-of-range
    index behind the apple-fy2026q3 IndexError (headers.py:400). Measured 2026-08-05:
    the cells-level twin of this layout mints split=7 on 7 lines. Borderless, single band."""
    cols = [72.0, 250.0, 340.0, 430.0, 520.0]     # label col + 4 data cols
    rows = [
        ("(1) Net sales by reportable segment:", "", "", "", ""),
        ("Americas", "$ 45,781", "$ 41,198", "$ 149,403", "$ 134,161"),
        ("Europe", "29,395", "24,014", "95,596", "82,329"),
        ("Greater China", "18,816", "15,369", "64,839", "49,884"),
        ("Japan", "6,554", "5,782", "24,368", "22,067"),
        ("Rest of Asia Pacific", "8,871", "7,673", "30,151", "25,254"),
        ("Total net sales", "$ 109,417", "$ 94,036", "$ 364,357", "$ 313,695"),
    ]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y0 = PAGE_H - 100.0
    for i, row in enumerate(rows):
        y = y0 - i * 14.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_lines": len(rows)}
```

- [ ] **Step 2: Write the failing tests** — create `tests/etkl/test_invalid_split_refusal.py`:

```python
"""R41: a derived header/body split must leave >=1 body row. A $-sandwiched numeric column
(first and last body rows Currency, interior Numeric) pushes s_col = MAX(mismatch row)+1 one
past the band in every data column; pre-fix the AXIOM returned split == len(band.lines) and
every band.lines[split] indexer crashed (the apple-fy2026q3 IndexError, headers.py:400).
See docs/superpowers/specs/2026-08-05-r41-invalid-split-refusal-design.md."""
import os
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
HBS = os.path.join(QDIR, "header-body-split.rq")

# The apple segment-footnote band, cells-level (measured 2026-08-05: split=7 on 7 rows pre-fix).
# Col 0 = caption + text labels; col 1 = the $-sandwiched data column.
SANDWICH_CELLS = [(0, 0, "(1) Net sales by reportable segment:")] + [
    (r, 0, t) for r, t in enumerate(
        ["Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific",
         "Total net sales"], 1)
] + [
    (1, 1, "$ 45,781"), (2, 1, "29,395"), (3, 1, "18,816"),
    (4, 1, "6,554"), (5, 1, "8,871"), (6, 1, "$ 109,417"),
]

# Single-column minimal form (same mechanism, no label column).
SANDWICH_ONE_COL = [
    (0, 0, "Qty"), (1, 0, "$ 45,781"), (2, 0, "29,395"), (3, 0, "18,816"),
    (4, 0, "6,554"), (5, 0, "8,871"), (6, 0, "$ 109,417"),
]


def _split(cells, ncols):
    return celltype.run_scalar(HBS, celltype.grid_evidence(cells, ncols))


def test_axiom_refuses_past_the_end_split():
    # A split at row 7 of a 7-row grid leaves zero body rows: not a label->data
    # transition, refused (None -> caller falls back / escalates). Pre-fix: returns 7.
    assert _split(SANDWICH_CELLS, 2) is None
    assert _split(SANDWICH_ONE_COL, 1) is None


def test_split_still_derived_when_another_column_transitions():
    # Guard: the clause must only DROP past-the-end candidates, never block a valid
    # column's in-range split. Same sandwich column + a clean numeric column whose
    # transition is at row 1 -> MIN over surviving candidates = 1, exactly as today.
    cells = SANDWICH_CELLS + [
        (0, 2, "Qty"), (1, 2, "100"), (2, 2, "200"), (3, 2, "300"),
        (4, 2, "400"), (5, 2, "500"), (6, 2, "600"),
    ]
    assert _split(cells, 3) == 1


def _band(pdf_path):
    """The single band of a borderless one-table fixture page (production geometry path)."""
    from iladub.etkl.geometry import extract_words, text_lines
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.segment import segment
    words = extract_words(pdf_path, 0)
    out = []
    for band in detect_bands(text_lines(words)):
        out.extend(segment(band))
    return max(out, key=lambda b: len(b.lines))


def test_classify_hierarchical_returns_instead_of_raising(tmp_path):
    # Pre-fix this RAISES IndexError (the apple crash path: classify_hierarchical ->
    # infer_header_tree -> header_rows_of -> band.lines[split]). Post-fix it must
    # RETURN — None (escalate) or a HierRegion — never crash. No reading is claimed.
    from tests.etkl.fixtures import currency_sandwich_pdf
    from iladub.etkl.hierarchical import classify_hierarchical
    pdf = str(tmp_path / "sandwich.pdf")
    currency_sandwich_pdf(pdf)
    classify_hierarchical(_band(pdf))   # must not raise; return value unconstrained


def test_compile_returns_instead_of_crashing(tmp_path):
    # The fluent-reader invariant end to end: compile returns a report; every region
    # is asserted or escalated, never a crash. The verdict itself stays unpinned —
    # honest escalation is the expected outcome, but the gate is "returns at all"
    # (the corpus battery's own Unadjudicated gate).
    from tests.etkl.fixtures import currency_sandwich_pdf
    from iladub.etkl import compile_tables
    pdf = str(tmp_path / "sandwich.pdf")
    currency_sandwich_pdf(pdf)
    rep = compile_tables(pdf, page_number=0)
    assert rep.regions, "no regions at all"
    assert all(r.verdict in ("asserted", "escalated") for r in rep.regions)
```

- [ ] **Step 3: Run the new tests — verify they fail for the right reason**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_invalid_split_refusal.py -v`

Expected: `test_axiom_refuses_past_the_end_split` FAILS with `assert 7 is None`; `test_classify_hierarchical_returns_instead_of_raising` and `test_compile_returns_instead_of_crashing` FAIL with `IndexError: tuple index out of range` (the exact apple traceback through `headers.py:400`). `test_split_still_derived_when_another_column_transitions` PASSES already (it pins current correct behavior the fix must preserve).

**If the two PDF-level tests do NOT reproduce the IndexError** (band routed differently than the apple page): adjust the fixture toward the real band — the y-step and font are already apple-like; next knobs are the caption's x (must sit at the label column's left edge, `cols[0]`) and column x-spacing. Do NOT proceed to Task 2 until the IndexError reproduces; the red test is the loop's evidence.

- [ ] **Step 4: Commit the red state**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/fixtures.py tests/etkl/test_invalid_split_refusal.py && git commit -m "test(loop-r41): red — the \$-sandwich split crash pinned at query, region, and compile level

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(The suite is temporarily red by these new tests only — expected mid-loop TDD state; nothing else may be red.)

---

### Task 2: The AXIOM clause + the mirrored Python reference

**Files:**
- Modify: `vocab/queries/header-body-split.rq`
- Modify: `tests/etkl/test_derivation_equiv.py:39-71` (`_ref_hbs`)

**Interfaces:**
- Consumes: Task 1's three red tests (exact names above).
- Produces: the fixed query text (same path, same `SELECT (MIN(?s_col) AS ?split)` contract — callers unchanged); `_ref_hbs(cells, ncols)` with identical semantics (signature unchanged).

- [ ] **Step 1: Edit the query.** In `vocab/queries/header-body-split.rq`, replace the final four lines

```sparql
  BIND(IF(?maxdiff >= 0, ?maxdiff + 1, 1) AS ?s_cand)
  BIND(IF(?maxbody >= 1, ?s_cand, -1) AS ?s_col)     # -1 => no non-Blank body cell, excluded
  FILTER(?s_col >= 1)
}
```

with

```sparql
  { SELECT (MAX(?anyrow) AS ?maxrow) WHERE { ?anycell tab:atGridRow ?anyrow } }
  BIND(IF(?maxdiff >= 0, ?maxdiff + 1, 1) AS ?s_cand)
  BIND(IF(?maxbody >= 1, ?s_cand, -1) AS ?s_col)     # -1 => no non-Blank body cell, excluded
  FILTER(?s_col >= 1 && ?s_col <= ?maxrow)           # R41: a split must leave >=1 body row
}
```

and update the header comment: replace the caveat sentence `(The reference TYPE is a mode, so one off-type bottom row can't flip it; but the all-rows mismatch scan below is NOT in general robust to a trailing off-type NON-Blank footer inside a data column — a lone such column can yield a split past the body instead of escalating; see Loop B/C.)` with:

```text
# (The reference TYPE is a mode, so one off-type bottom row can't flip it. R41, 2026-08-05: a
# column whose mismatch scan lands PAST the last evidence row — e.g. a $-sandwiched numeric
# column whose LAST row is off-modal — never completed its label->data transition and is
# EXCLUDED from the MIN (the `?s_col <= ?maxrow` clause; same treatment as the -1 no-body
# exclusion), so a derived split always leaves >=1 body row. Presence-based, no constant.
# HONEST REMAINDER: an INTERIOR off-type non-Blank footer still shifts the split within
# range — an in-range-but-wrong split is a reading-quality question, not a crash; see Loop B/C.)
```

- [ ] **Step 2: Mirror the reference.** In `tests/etkl/test_derivation_equiv.py`'s `_ref_hbs`, add the bound. After the line `best = None` insert:

```python
    maxrow = max(r for (r, c, t) in cells)   # every line has >=1 cell (text_lines invariant)
```

and change the accumulation

```python
            if s_col >= 1:
                best = s_col if best is None else min(best, s_col)
```

to

```python
            if 1 <= s_col <= maxrow:         # R41: a split must leave >=1 body row
                best = s_col if best is None else min(best, s_col)
```

Also append one line to the `_ref_hbs` docstring: `R41 (2026-08-05): an s_col past the last evidence row is excluded — a valid split leaves >=1 body row (mirrors the query's ?maxrow clause).`

- [ ] **Step 3: Run the Task-1 tests — all green now**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_invalid_split_refusal.py -v`
Expected: 4 PASS (compile fixture escalates or asserts, never crashes).

- [ ] **Step 4: Run the equivalence battery and the split-robust suite**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_derivation_equiv.py::test_header_body_split_new_matches_ref tests/etkl/test_header_body_split_robust.py -v`
Expected: PASS (query and reference changed in lockstep; the robust suite's splits are all in-range and untouched).

- [ ] **Step 5: Measure that the battery actually exercises the refused class** (spec §3.3 requires the check, not the assumption):

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
# Count random-battery grids where the R41 clause changes the outcome: old semantics
# (no bound) vs new (bounded). Non-zero => the generator covers the class.
from tests.etkl.test_derivation_equiv import _rand_grids, _ref_hbs
from iladub.etkl.celltype import _cell_datatype
from collections import Counter
def _ref_unbounded(cells, ncols):
    BLANK = _cell_datatype(""); TEXT = _cell_datatype("Alice")
    by_col = {}
    for (r, c, t) in cells: by_col.setdefault(c, []).append((r, _cell_datatype(t)))
    best = None
    for c, rt in by_col.items():
        nonblank = [(r, dt) for (r, dt) in rt if dt != BLANK]
        body = [(r, dt) for (r, dt) in nonblank if r >= 1]
        if not body: continue
        counts = Counter(dt for _, dt in body); maxn = max(counts.values())
        for D in [dt for dt, n in counts.items() if n == maxn]:
            if D == TEXT: continue
            diffs = [r for (r, dt) in nonblank if dt != D]
            s_col = (max(diffs) + 1) if diffs else 1
            if s_col >= 1: best = s_col if best is None else min(best, s_col)
    return best
n = sum(1 for cells, ncols in _rand_grids(seed=1, n=300)
        if _ref_unbounded(cells, ncols) != _ref_hbs(cells, ncols))
print(f"battery grids where the clause changes the outcome: {n}/300")
assert n > 0, "generator never hits the refused class — extend it (see plan Task 2 Step 5 note)"
EOF
```

Expected: a non-zero count printed. **If the assert fires** (count 0): extend the battery by appending the two directed `SANDWICH_*` cases — add to `test_header_body_split_new_matches_ref` a loop over `[(SANDWICH_CELLS, 2), (SANDWICH_ONE_COL, 1)]` (import them from `tests.etkl.test_invalid_split_refusal`) asserting `_ref_hbs == _run_text(new_text, …)` on each. Record the measured count in the commit message either way.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/queries/header-body-split.rq tests/etkl/test_derivation_equiv.py && git commit -m "fix(loop-r41): AXIOM — a derived header/body split must leave >=1 body row

The \$-sandwiched-column class (apple segment footnote) minted s_col one past the
band; the ?maxrow clause excludes such columns from the MIN, exactly like the -1
no-body exclusion. Python reference mirrored in lockstep; battery coverage of the
refused class measured at <N>/300 grids.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Replace `<N>` with Step 5's measured count.)

---

### Task 3: End-to-end measurement — apple compiles, battery green, no regression

**Files:**
- No source edits expected. Measurement + full-suite verification only. (If a NEW defect is measured, it is REGISTERED in Task 4, not fixed here.)

**Interfaces:**
- Consumes: Task 2's fixed query; `compile_document` (`src/iladub/etkl/document.py`), the corpus battery (`tests/test_corpus.py`).
- Produces: the measured apple compile record (score, per-region verdicts, wall time) pasted into the Task-4 register edit and the final report.

- [ ] **Step 1: Compile the apple document and record the measurement**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/financial/apple-fy2026q3-statements.pdf")
dt = time.monotonic() - t0
print(f"score={rep.score:.4f} pages={len(rep.pages)} chains={[len(c) for c in rep.chains]} wall={dt:.0f}s")
for i, p in enumerate(rep.pages):
    print(f"  p{i}: {[(r.kind.name, r.verdict, r.reason) for r in p.regions]}")
EOF
```

Expected: returns (no exception, no hang). Record the FULL output verbatim — it is the register-row evidence and the Unadjudicated adjudication evidence. If it crashes at a NEW site or hangs: that is a MEASURED second defect — capture the traceback, do NOT fix it here, and carry it to Task 4 as a new register row (spec §3.5).

- [ ] **Step 2: Run the corpus battery test for apple**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest "tests/test_corpus.py::test_expected_verdict[financial/apple-fy2026q3-statements.pdf]" -v -s`
Expected: PASS (the `Unadjudicated` gate is "compile returns at all"), with the `UNADJUDICATED — regions:` print.

- [ ] **Step 3: Run the full suite** (the stem/CBH pins are the no-regression proof — this query runs on every document)

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -x -q 2>&1 | tail -20`
Expected: 0 failed (skips allowed, as on main). Slow (~15+ min: stem compiles + whole-graph SHACL); do not interrupt. Any failure = a regression this loop introduced or a pre-existing red — diagnose which by checking out `main` for that one test before touching anything; never weaken a pin.

- [ ] **Step 4: Commit** (only if anything changed — e.g. Step 5 of Task 2 left battery edits uncommitted; otherwise skip)

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git status --short
```

---

### Task 5: R19 gate extension — the physical shapes join the region gate

**Adjudicated scope extension (François, 2026-08-05).** Task 3 measured that with R41's
IndexError fixed, the apple compile proceeds to page 1 and CRASHES at final validation
(`compile.py:624`, `AssertionError`): `tab:WrappedCellShape` violations on
`p1#mtable4-cc0_2` / `cc1_2` — matrix-path cells carrying a bbox with empty `cellText`.
This is registered residue **R19** exactly (the region gates validate the eleven TILING
shapes only; a physical-shape defect crashes THROUGH every gate), whose own closure
condition — "once any real document can reach the crash" — is now met, measured. The fix
is R19's named closure: extend the gate's CBD extraction with the two physical shapes.

**Files:**
- Modify: `src/iladub/etkl/tiling.py` (`_TILING_SHAPE_IRIS`, `_build_tiling_shapes`, module/function docstrings)
- Create: `tests/etkl/test_physical_gate.py`

**Interfaces:**
- Consumes: `region_tiles(graph)` (unchanged signature); `vocab/shapes/tab-physical-shapes.ttl` (read-only — the shapes are NOT edited, only included).
- Produces: `region_tiles` refusing a region whose scratch graph violates `tab:EntryCellPhysicalShape` or `tab:WrappedCellShape`; every `compile_tables` path then escalates such a region through its existing gate branch (matrix → `MATRIX_AMBIGUOUS`, hier → `REGION_TILING_FAILED`, etc.) instead of crashing at final validation.

- [ ] **Step 1: Write the failing test** — create `tests/etkl/test_physical_gate.py`:

```python
"""R19: the region gate must refuse a PHYSICAL-shape defect, not let it crash compile at
final validation. Measured activation (2026-08-05, loop R41 Task 3): with R41's IndexError
fixed, corpus/financial/apple-fy2026q3-statements.pdf page 1's mtable4 emits matrix cells
carrying a bbox with EMPTY cellText; region_tiles (eleven tiling shapes only) passes the
region, and compile_tables raises AssertionError at final whole-graph validation
(tab:WrappedCellShape, compile.py:624). The gate must include the physical shapes so the
region ESCALATES (fluent-reader invariant: never crash, always at worst escalate)."""
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")


def _bbox(g, cell, n):
    bb = URIRef(f"urn:r19:bb{n}")
    g.add((bb, RDF.type, TAB.BBox))
    g.add((cell, TAB.hasBBox, bb))


def test_gate_refuses_bbox_cell_with_empty_text():
    # The apple p1#mtable4 defect, minimal: a Cell with a bbox and empty cellText.
    # Pre-fix: region_tiles returns True (the tiling shapes don't see it) — RED.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    cell = URIRef("urn:r19:cell0")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("")))
    _bbox(g, cell, 0)
    assert not region_tiles(g)


def test_gate_refuses_entrycell_missing_physical_facts():
    # EntryCellPhysicalShape's other half: an asserted EntryCell must carry text,
    # onPage, and bbox. One missing onPage must now refuse at the gate too.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    cell = URIRef("urn:r19:cell1")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    _bbox(g, cell, 1)          # bbox + text present, onPage missing
    assert not region_tiles(g)


def test_gate_still_passes_a_well_formed_physical_cell():
    # Guard: a complete cell (text + bbox) must not be refused by the extension.
    from iladub.etkl.tiling import region_tiles
    from rdflib.namespace import XSD
    g = Graph()
    cell = URIRef("urn:r19:cell2")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    _bbox(g, cell, 2)
    assert region_tiles(g)
```

- [ ] **Step 2: Run — verify red**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_physical_gate.py -v`
Expected: the two refusal tests FAIL (`region_tiles` returns True — the gate doesn't carry the physical shapes yet); the guard PASSES.

- [ ] **Step 3: Extend the gate** — in `src/iladub/etkl/tiling.py`:

Add after the `_TILING_SHAPE_IRIS` list:

```python
# R19 closure (2026-08-05): the TWO physical shapes join the gate. Measured activation:
# apple-fy2026q3 p1#mtable4 (matrix cells with bbox + empty cellText) crashed compile at
# final validation THROUGH this gate; the physical shapes were only in compile._validate's
# full set. Region defects expressible in the physical layer now refuse HERE, so every
# path's existing escalation branch handles them (never crash, always at worst escalate).
_PHYSICAL_SHAPE_IRIS = [TAB.EntryCellPhysicalShape, TAB.WrappedCellShape]
```

and change `_build_tiling_shapes` to parse both files and extract all thirteen CBDs:

```python
    full = Graph().parse(os.path.join(_VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    full.parse(os.path.join(_VOCAB, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    sub = Graph()
    for s in _TILING_SHAPE_IRIS + _PHYSICAL_SHAPE_IRIS + [TAB.prefixes]:
        sub += full.cbd(s)
    return sub
```

Update the module docstring and `_build_tiling_shapes`/`region_tiles` docstrings: "eleven tiling invariants" → "eleven tiling invariants + the two physical shapes (R19)". Do not edit `vocab/shapes/*.ttl`.

- [ ] **Step 4: Run — verify green + gate cost**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_physical_gate.py tests/etkl/test_invalid_split_refusal.py -v`
Expected: all PASS. Then measure the healthy-gate cost R19's row asks for:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from iladub.etkl.tiling import region_tiles
TAB = Namespace("https://w3id.org/iladub/tab#")
g = Graph()
c = URIRef("urn:r19:t"); g.add((c, RDF.type, TAB.Cell)); g.add((c, TAB.cellText, Literal("x")))
region_tiles(g)                      # warm the cached shapes
t0 = time.monotonic(); [region_tiles(g) for _ in range(10)]
print(f"gate call: {(time.monotonic()-t0)/10:.3f}s (R19 row's pre-extension baseline: ~0.26s)")
EOF
```

Record the number in the report — it goes into the close commit.

- [ ] **Step 5: The apple document end to end** (the measurement Task 3 could not complete):

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/financial/apple-fy2026q3-statements.pdf")
dt = time.monotonic() - t0
print(f"score={rep.score:.4f} pages={len(rep.pages)} chains={[len(c) for c in rep.chains]} wall={dt:.0f}s")
for i, p in enumerate(rep.pages):
    print(f"  p{i}: {[(r.kind.name, r.verdict, r.reason) for r in p.regions]}")
EOF
```

Expected: RETURNS (p1's mtable4 escalated, reason `MATRIX_AMBIGUOUS`). If a THIRD crash site appears: capture the traceback, do NOT fix, report to the controller — it is a register decision, not more scope by default.

- [ ] **Step 6: Battery + regression proof**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest "tests/test_corpus.py::test_expected_verdict[financial/apple-fy2026q3-statements.pdf]" -v -s`
Expected: PASS (prints the UNADJUDICATED region record).
Then the stem + CBH pins (the gate runs on every region of every document — these are the byte-identity proof):
`python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q` — expected: same pass/skip counts as main, stem score 0.9655 unchanged.

- [ ] **Step 7: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/tiling.py tests/etkl/test_physical_gate.py && git commit -m "fix(loop-r41): R19 — the physical shapes join the region gate

Measured activation: apple p1#mtable4 (bbox + empty cellText matrix cells) crashed
compile at final validation through the tiling-only gate. The gate now extracts
tab:EntryCellPhysicalShape + tab:WrappedCellShape CBDs too; the region escalates
MATRIX_AMBIGUOUS and the document compiles end to end. Healthy-gate cost <T>s/call.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Replace `<T>` with Step 4's measured cost.)

---

### Task 6: Full suite — the whole branch has no regression

**Files:** none (measurement only).

- [ ] **Step 1:** Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -8`
Expected: 0 failed (skips as on main). Slow (~15+ min). Any failure: diagnose regression-vs-pre-existing; never weaken a pin.

---

### Task 4: Close the loop — register, docs, merge

**Files:**
- Modify: `docs/superpowers/residues.md` (delete the R41 row; append a new row ONLY if Task 3 measured a new defect)
- Modify: `docs/superpowers/specs/2026-08-05-r41-invalid-split-refusal-design.md` (Status line → closed, with the measured numbers)

**Interfaces:**
- Consumes: Task 3's measured apple record (score/verdicts/wall).
- Produces: the merged loop.

- [ ] **Step 1: Edit the register.** In `docs/superpowers/residues.md`: DELETE the R41 row (the row starting `| R41 | **The compiler CRASHES (not escalates) on a real financial-statements document**`). MARK the R19 row CLOSED in the house style (`| ~~R19~~ | **CLOSED (Loop R41 Task 5, 2026-08-05)** — …`), recording: the measured activation (apple p1#mtable4, bbox + empty cellText, crash at final validation with R41 fixed), the closure (both physical shapes' CBDs join the gate's extraction; the region escalates `MATRIX_AMBIGUOUS`), the measured healthy-gate cost from Task 5 Step 4, and the honest residual R19 itself named (the alternate closure — dropping the bbox from ROUND_TRIP_FAIL candidates — was not needed and not done; a candidate typing as `tab:Cell` via domain inference now REFUSES at the gate rather than crashing, which is the honest direction). If Task 5/6 measured a further defect (third crash site, hang, notable verdict oddity), APPEND a new row `R55` following the house format: what was measured (exact probe/traceback), why deferred, what would close it.

- [ ] **Step 2: Update the spec status line** to `**Status:** closed 2026-08-05 — apple compiles end-to-end (score <measured>, regions <summary>); battery green` with Task 3's real numbers.

- [ ] **Step 3: Run the doc-governance lint** (residues.md and the spec are governed files):

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q`
Expected: PASS.

- [ ] **Step 4: Commit the close**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add docs/superpowers/residues.md docs/superpowers/specs/2026-08-05-r41-invalid-split-refusal-design.md && git commit -m "docs(loop-r41): close — R41 deleted from the register; apple measured end-to-end

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Finish the branch.** Use the superpowers:finishing-a-development-branch skill (PR to `main` per house convention — loops P/Q merged via PRs #86/#87). PR body: the spec's §1 root cause + Task 3's measured record; end with the house PR footer.

---

## Self-Review (run after writing — done 2026-08-05)

- **Spec coverage:** §1 problem → Task 1 red tests; §2 fix → Task 2 Steps 1-2; §3.1 → Task 1; §3.2 → Task 2 Step 1; §3.3 (mirror + battery check) → Task 2 Steps 2, 4, 5; §3.4 (E2E + battery + suite) → Task 3; §3.5 (register) → Task 4; §4 out-of-scope guarded by Global Constraints.
- **Placeholder scan:** `<N>` and `<measured>` are deliberate measurement slots the executing engineer fills with real numbers at commit time — not unknowns.
- **Type consistency:** `currency_sandwich_pdf(path) -> dict`, `_split(cells, ncols)`, `_ref_hbs(cells, ncols)`, test names referenced identically across tasks.
