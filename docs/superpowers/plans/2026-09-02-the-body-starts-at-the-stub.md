# The body starts at the stub — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make apple's statement headers assert by deriving the matrix body start from the presence
of a stub cell (AXIOM), and refuse a column tree that silently drops header ink (producer-side
guard) — without touching `header_body_split` or its query.

**Architecture:** One new AXIOM derivation (`vocab/queries/matrix-body-start.rq`, open world,
band-scoped `MIN`) run over the typed-cell evidence graph `header_body_split` already builds, with
two bindings (`?split`, `?k`). `classify_matrix` consumes its result where it consumes `split` today.
One producer-side guard in `infer_column_tree_by_proximity` returns `None` when a data-column header
word is carried by no node; the existing `MATRIX_AMBIGUOUS` escalation site handles the refusal. No
new vocabulary, no new escalation reason.

**Tech Stack:** Python 3, rdflib (SPARQL 1.1 with `initBindings`), pdfplumber, reportlab (fixtures),
pytest (`-m corpus` for the real documents).

**Spec:** `docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md` — **read it first
and keep it open.** This plan argues *from* the spec and does not restate it (CLAUDE.md plan-rule 6).
Every "why" is answered there by section number; every "what is NOT done" is spec § 4.

**Doc impact: increment.** Carried from the spec: `tests/corpus-manifest.ttl`'s apple `cor:rationale`
gains a dated second adjudication node superseding the 2026-08-20 census figures, and
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM entry. No released assertion changes;
no contradiction. (`tests/test_doc_governance.py::test_membrane` reads this line — the previous plan
shipped without it and was RED for one commit.)

---

## Global Constraints

Every task's requirements implicitly include this section.

- **CLAUDE.md §8 gate.** Both decisions are classified in spec § 2 — A is AXIOM (derivation, open
  world, holon-scoped `MIN`), B is a closed-world completeness check kept **producer-side** under
  CLAUDE.md § "Producer-side guards vs the membrane" because the dropped ink never enters the graph.
  **No tuned constant, no tolerance, no string test on a label** anywhere in the shipped diff. A
  reviewer finding one fails the task.
- **`header_body_split` and `vocab/queries/header-body-split.rq` are UNTOUCHED** (spec § 3.1, § 4).
  The record and hierarchical paths never see the stub rule. `git diff --stat` on those two files must
  be empty at every commit.
- **`is_matrix_candidate` is UNTOUCHED.** Spec § 3.1 says both callers consume the new result "wherever
  they use `split` today"; MEASURED (`matrix.py:84-92`), `is_matrix_candidate`'s only use of `split` is
  the candidacy count `split >= 2`, and the invariant `matrix_body_start(...) >= split` means the moved
  start can only raise that count. There is nothing for it to consume. Task 3 records this
  reconciliation in its report.
- **Order of operations is spec § 3.3, stated once:** grid → type split → `k` → matrix body start →
  column tree (with guard) → leaf rows → row tree. A task that changes this order re-measures spec
  § 1.2 first.
- **Falsification is mandatory, per task** (CLAUDE.md plan-rule 4). Every task report carries a
  `## FALSIFICATION` block: remove or invert the thing the new test pins, show it **failing**,
  restore, show green. **No falsification evidence ⇒ the task review fails.**
- **Plan-supplied tests are propositions.** If one cannot be made to pass, you have found a plan
  defect. Say so in the task report and substitute the satisfiable form carrying the same force —
  **never weaken an assertion to make a broken contract go green** (plan-rule 1).
- **Reconciled against spec § 4 before shipping** (plan-rule 5). No test here asserts that apple p2
  band 2 asserts, that unruled words are grouped into labels, that the adoption gate is settled, or
  that a new escalation reason exists — all four are scoped OUT.
- **The score is not the oracle** (spec § 1.4; memory `r155-refuted-neural`). apple's document score
  is expected to FALL. A task report that reads a score movement as evidence in either direction
  is a review failure; the oracles are spec § 5 O1–O6.
- **Never lower a corpus floor.** If a battery document lands under its floor, STOP and report the
  measured figure (`tests/test_corpus.py:111-113`).
- **Run everything with the suite's interpreter**, `./.venv/bin/python -m pytest …` — the runner
  trap is recorded in memory `strategy-instrument-loop`. Corpus tests carry `pytest.mark.corpus`
  and `pytest.skip` when the file is absent; CI has no corpus.
- **Downward same-file citations** (plan-rule 7, `R139`): cite a **symbol**, never a line, from a
  comment in `matrix.py` to something below it in `matrix.py`.
- **Source ownership**: no `holon:` IRI becomes a subject. The new query names `tab:` terms only.

---

## File Structure

| file | responsibility |
|---|---|
| **Create** `vocab/queries/matrix-body-start.rq` | A — AXIOM derivation, open world (spec § 3.1) |
| **Modify** `src/iladub/etkl/matrix.py` | `matrix_body_start` (new), `classify_matrix` (consumes it), `infer_column_tree_by_proximity` (guard B) |
| **Modify** `tests/etkl/fixtures.py` | three new synthetic fixtures (geometry in Task 2/4) |
| **Create** `tests/etkl/test_matrix_body_start.py` | O2 + the `None` path + O6 pointer |
| **Modify** `tests/etkl/test_matrix.py` | O1, O3, O4 |
| **Create** `tests/etkl/test_apple_statement_headers.py` | corpus-marked pins for apple p0/p1/p2 band 2 and document scope (O5, apple leg) |
| **Modify** `tests/corpus-manifest.ttl` | apple: second `cor:adjudication` node (Doc impact) |
| **Modify** `docs/superpowers/residues{,-open}.md` | five new rows R160–R164 (spec § 7) |
| **Modify** `docs/wiki/concepts/neurosymbolic-exemplars.md`, `docs/wiki/index.md` | one AXIOM exemplar |

---

## Measured seams (plan-rule 2; the three the spec § 6 names, plus two found while measuring)

All measured 2026-09-02 at `b592ecc` (the spec branch; PR #151 squashed the same tree onto `main` as
`f4fd540`, which this plan's branch starts from), scripts in the session scratchpad (outputs
reproduced here; the scripts are not committed — Task 1 recreates the one that matters).

**S1 — where `split` is consumed inside `classify_matrix`.** `matrix.py:106-132`: three uses,
exactly the spec's — `infer_column_tree_by_proximity(band, grid, split, data_cols)` (`:122`),
`band.lines[split].top` passed to `logical_rows` (`:125`), and `MatrixRegion(..., split)` as
`body_line` (`:132`). `MatrixRegion.body_line` has **no consumer outside `matrix.py`**
(`grep -rn body_line src/iladub/etkl/ | grep -v matrix.py` → only `hierarchical.py`'s own
dataclass). `is_matrix_candidate` (`:84-92`) uses `split` only for `split >= 2`.

**S2 — `run_scalar` bindings reach the query as typed integers, with TWO bindings.** Precedent is
one binding (`rowheaders.py:35`, `Literal(split, datatype=XSD.integer)`). Driven with two, on the
prototype form of spec § 3.1's query:

```
apple p0 band 2: ncols=5 split=2 k=1 nlines=12      two-binding body_start = 3
apple p2 band 2: ncols=3 split=2 k=1 nlines=4       two-binding body_start = 3
crosstab_table_pdf fixture: split=2 k=1             two-binding body_start = 2   (== split)
```

**S3 — `absorb_unit_markers` runs before any band reaches `classify_matrix`.** `compile.py:321-322`,
the last statement of `page_bands`, which `compile_tables` calls before classifying. The guard reads
`band.lines[:body_start]` words after absorption. (Fixtures built through
`detect_bands(text_lines(extract_words(p)))` as `test_matrix.py` does never carry markers.)

**S4 — spec § 1.2 REPRODUCED** (the handoff's asserted item 2). Monkeypatching
`matrix.header_body_split` to return 3 on apple p0 band 2:

```
baseline classify_matrix: None
forced split=3 -> region: True   levels [0,1,2]  nodes 10  leaf_rows 9  entries 28  region_tiles True
```

**S5 — a correction to spec § 1.3's "the band refuses earlier".** apple p2 band 2 at HEAD does
**not** refuse in `classify_matrix`: it returns a region (`body_line 2`, 2 levels, 2 leaf rows,
4 entries) and is escalated at **`region_tiles` → False** in `compile.py`. So today the false
reading is stopped by the tiling oracle, not by `logical_rows`. The consequence for this loop is
unchanged (after A, that band would tile and assert with `Months`, `June`, `June` uncarried; B
refuses it), but a task report must not repeat the spec's wording. Measured under a forced split:

```
apple p2 band 2: L0 ['Nine','Months','Ended']  L1 ['June','27,','June','28,']  L2 ['2026','2025']
rules intersecting: 0     data-column header words: 9     nodes: 6
uncarried: 'Months', 'June', 'June'
```

**S6 — the three fixtures the oracle needs CAN be constructed** (plan-rule 5, setup measured). Drawn
with reportlab Courier/Courier-Bold 9pt through the `test_matrix.py` band path:

```
three_level_numeric_header (O1):     nlines=6 ncols=5 split=2 k=1 body_start=3
   L0 ['Quarter','YTD']  L1 ['Jun','Sep','Jun','Sep']  L2 ['2026','2025','2026','2025']  L3 ['Sales:']
   HEAD classify: None      with body_start: levels [0,1,2] nodes 10 leaf_rows 3 entries 8 tiles True uncarried []
same + corner 'Segment' on L1 (O2 falsifier / O4):  split=2 k=1 body_start=3
   L1 ['Segment','Jun','Sep','Jun','Sep']            with body_start: tiles True uncarried []
unruled_multiword_spanner (O3):      nlines=5 ncols=3 split=2 k=1 body_start=3
   L0 ['Nine','Months','Ended']  L1 ['Jun','Sep']  L2 ['2026','2025']  L3 ['Cash','35,934','29,943']
   with body_start, NO guard: levels [0,1,2] nodes 6 tiles True uncarried ['Months']   <- the false assertion B refuses
```

The O1 fixture deliberately uses **single-token** spanners (`Quarter`/`YTD`, not `Three Months
Ended`): `extract_words` keeps pdfplumber's space-split words (`geometry.py:50`,
`keep_blank_chars=False`), so a multi-word spanner on an unruled fixture is O3's subject, not O1's.
Spec O1 says "ruled"; the ruled property is not load-bearing for A (what is load-bearing is the
numeric third level and the stub-only section row), and the ruled band producer would re-cut the
spanner at any interior rule (`fixtures.py::spanner_with_space_ruled_pdf`). Recorded here as a plan
decision; the spec is not edited.

---

## Task 1: HEAD baseline for the two-sided corpus leg (measurement only — no `src/` change)

**Files:** none tracked. Writes `<scratchpad>/baseline-HEAD.json`.

**Why first:** O5 demands WHO **byte-identical verdicts** and apple's `adopted (1,) → ()`. Both are
two-sided claims and need the HEAD side captured before any `src/` edit, on this machine. Spec
§ 1.4's figures are the prediction; this task is the measurement.

- [ ] **Step 1: Confirm a clean tree at the branch head**

Run: `git status --short && git log --oneline -1`
Expected: no output from status; `b592ecc` (or a later docs-only commit on this branch).

- [ ] **Step 2: Write the capture script** (justified PROCEDURAL glue: it calls the public API and
  serialises the report; it decides nothing)

Save as `<scratchpad>/baseline.py`. It must, for `apple` (`corpus/financial/apple-fy2026q3-statements.pdf`)
and `who` (`corpus/health/who-wfa-boys-zscore-0-5.pdf`): call `iladub.etkl.document.compile_document(path)`,
and record `rep.score`, `list(rep.adopted)`, wall seconds, and
`[[page_index, region_index, r.kind.name, r.verdict, r.reason] for each page's regions]` into JSON
keyed by document. **MEASURE the field names before writing**: `CompilationReport` has no `page`
attribute — enumerate `rep.pages`; `RegionReport` carries `kind`, `verdict`, `reason`
(`compile.py::RegionReport`, `document.py::DocumentReport`).

- [ ] **Step 3: Run it against HEAD**

Run: `./.venv/bin/python <scratchpad>/baseline.py <scratchpad>/baseline-HEAD.json`
Expected — MEASURED 2026-09-02 at `b592ecc` by the plan author with exactly this script (spec § 1.4
agrees); confirm on your machine and paste into the task report:

```
apple  score 0.3587  adopted [1]   35.7 s   26 region reports, MATRIX_AMBIGUOUS x2 (p0 region 2, p2 region 2)
who    score 0.9096  adopted []    41.9 s   18 region reports, MATRIX_AMBIGUOUS x0
apple p1 region 2 at HEAD: superseded / KIND_NOT_SUPPORTED   (the band that asserts after this loop)
```

If apple's HEAD score is not 0.3587 or WHO's is not 0.9096, STOP: the branch is not at the spec's
baseline, and every later two-sided claim would be measured against the wrong side.

- [ ] **Step 4: Record** the two lines and both wall times in the task report. No commit.

---

## Task 2: `matrix-body-start.rq` + `matrix_body_start` (A — AXIOM, open world)

**Files:**
- Create: `vocab/queries/matrix-body-start.rq`
- Modify: `src/iladub/etkl/matrix.py` (new function; `classify_matrix` NOT yet changed)
- Modify: `tests/etkl/fixtures.py` (one new fixture with an optional corner label)
- Create: `tests/etkl/test_matrix_body_start.py`

**Interfaces:**
- Consumes: `headers.header_body_split(band, grid) -> int | None`, `rowheaders.stub_data_split(band, grid) -> int | None`,
  `headers._grid_cells(band, grid)`, `celltype.grid_evidence(cells, ncols)`, `celltype.run_scalar(rq_path, graph, bindings)`.
- Produces: `matrix.matrix_body_start(band, grid, split: int, k: int) -> int | None` — the first
  cell-bearing line index `>= split` that has a cell in a column `< k`; `None` when no such line exists.
  Invariants (spec § 3.1): result `>= split`; result `< len(band.lines)` when not None; equals `split`
  when line `split` itself carries a stub cell.

**The query's contract (spec § 3.1 — the implementer writes the SPARQL):** `PREFIX tab:` only;
bindings `?split` and `?k` (typed `xsd:integer`, supplied via `run_scalar`'s `bindings`);
`SELECT (MIN(?row) AS ?body)` over `tab:GridCell`s with `tab:atGridRow ?row` and
`tab:atGridColumn ?col` filtered `?row >= ?split && ?col < ?k`. Stub cells are identified **by column,
not datatype** — the query must not read `tab:cellDatatype`. The header comment follows the house
style (`stub-data-split.rq`): what it derives, why it is evidence-positive (a line is body because a
stub cell is *present*), that it is band-scoped, that it adds no vocabulary and no constant, and
that `header-body-split.rq` is deliberately untouched. Cite spec § 2 (A).

- [ ] **Step 1: Add the fixture** to `tests/etkl/fixtures.py`

`three_level_numeric_header_pdf(path, corner: str | None = None) -> dict`. Geometry (measured, S6):
stub x = 55; data column centres 200, 270, 380, 450; top = `PAGE_H - 90`; Courier-Bold 9 for the
header, Courier 9 for the body. L0: `Quarter` centred over columns 1–2, `YTD` centred over 3–4.
L1 (top − 13): `Jun`, `Sep`, `Jun`, `Sep` centred on the data columns; when `corner` is given, draw it
left-aligned at the stub x on this line. L2 (top − 26): `2026`, `2025`, `2026`, `2025`. Body from
top − 44 at 16pt pitch: `Sales:` (stub only — the section row), `Products` with `100 90 300 280`,
`Services` with `50 45 150 140`. Return
`{"n_header_levels": 3, "body_line": 3, "corner": corner, "years": ["2026","2025","2026","2025"]}`.
Docstring: cite spec § 1.2 and this plan's S6; say why the spanners are single tokens.

- [ ] **Step 2: Write the failing tests**

```python
# tests/etkl/test_matrix_body_start.py
"""Spec 2026-09-02-the-body-starts-at-the-stub-design.md § 3.1, § 5 O2. The matrix body start
is the first cell-bearing line at/after the TYPE split that carries a STUB cell (AXIOM, open
world, matrix-scoped). header_body_split and its query are untouched by this loop."""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import crosstab_table_pdf, three_level_numeric_header_pdf
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl.rowheaders import stub_data_split
from iladub.etkl.matrix import matrix_body_start


def _prepared(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid)
    k = stub_data_split(band, grid)
    return band, grid, split, k


def test_equals_split_when_the_split_line_carries_a_stub_cell(tmp_path):
    """O2, the invariant every non-apple corpus band rests on (spec § 1.5)."""
    band, grid, split, k = _prepared(crosstab_table_pdf, tmp_path)
    assert (split, k) == (2, 1)                       # measured, plan S2
    assert matrix_body_start(band, grid, split, k) == split


def test_advances_past_a_stubless_numeric_header_level(tmp_path):
    """The apple shape: the years line is typed body but carries no stub cell (spec § 1.1)."""
    band, grid, split, k = _prepared(three_level_numeric_header_pdf, tmp_path)
    assert (split, k) == (2, 1)                       # measured, plan S6
    assert [w.text for w in band.lines[2].words] == ["2026", "2025", "2026", "2025"]
    assert matrix_body_start(band, grid, split, k) == 3
    assert [w.text for w in band.lines[3].words] == ["Sales:"]


def test_a_stub_cell_above_the_split_does_not_pull_the_start_up(tmp_path):
    """The ?split binding is load-bearing: a corner label on a HEADER line is a stub-column cell
    at row 1, and MIN without the ?split bound would return 1. Falsified by dropping the
    ?row >= ?split condition from the query."""
    band, grid, split, k = _prepared(lambda p: three_level_numeric_header_pdf(p, corner="Segment"), tmp_path)
    assert (split, k) == (2, 1)
    assert band.lines[1].words[0].text == "Segment"
    body = matrix_body_start(band, grid, split, k)
    assert body == 3 and body >= split


def test_none_when_no_column_is_a_stub(tmp_path):
    """The None path: with k=0 no cell can satisfy ?col < ?k. (k=0 never leaves stub_data_split,
    which returns k>=1 or None; this pins the contract, not a reachable state.)"""
    band, grid, split, k = _prepared(crosstab_table_pdf, tmp_path)
    assert matrix_body_start(band, grid, split, 0) is None


def test_the_query_names_only_declared_terms():
    """O6 — the declaration instrument covers every tracked .rq; this test exists so the O6
    evidence is local to this loop and not only in the suite-wide sweep."""
    from tests.query_terms import query_files
    from pathlib import Path
    assert Path("vocab/queries/matrix-body-start.rq").resolve() in {p.resolve() for p in query_files()}
```

- [ ] **Step 3: Run to verify they fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix_body_start.py -q`
Expected: `ImportError: cannot import name 'matrix_body_start'` (collection error) — all five fail.

- [ ] **Step 4: Write the query and the function**

`matrix_body_start` mirrors `stub_data_split`'s shape (`rowheaders.py:20-35`): build the evidence
graph from `_grid_cells`, resolve the `.rq` path relative to `__file__` exactly as `headers.py:112`
does, pass **both** bindings as `Literal(..., datatype=XSD.integer)`, return `run_scalar`'s int or
None. Docstring: state the AXIOM classification (spec § 2 A), the three invariants, and that it is
matrix-scoped because "stub" is a two-axis notion (spec § 4). Cite `header_body_split` and
`stub_data_split` by **symbol**, not line (they live in other files, but the habit is the rule).

- [ ] **Step 5: Run to verify they pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix_body_start.py tests/test_query_declarations.py tests/etkl/test_matrix.py -q`
Expected: all pass. `test_query_declarations.py::test_every_authored_query_names_only_declared_terms`
is O6 proper — if it fails, the query names an undeclared term; fix the query, never the instrument.

- [ ] **Step 6: FALSIFICATION** — in the `.rq`, delete the `?row >= ?split` half of the filter; run
  the file; `test_a_stub_cell_above_the_split_does_not_pull_the_start_up` must FAIL with `1 == 3`
  (or `1 >= 2`). Restore; green. Paste both runs in the report.

- [ ] **Step 7: Commit**

```bash
git add vocab/queries/matrix-body-start.rq src/iladub/etkl/matrix.py tests/etkl/fixtures.py tests/etkl/test_matrix_body_start.py
git commit -m "feat(matrix): derive the matrix body start from the first stub-bearing line (AXIOM)"
```

---

## Task 3: `classify_matrix` consumes the derived start (O1)

**Files:**
- Modify: `src/iladub/etkl/matrix.py::classify_matrix` (S1: the three `split` uses)
- Modify: `tests/etkl/test_matrix.py`

**Interfaces:**
- Consumes: `matrix_body_start` (Task 2).
- Produces: `classify_matrix(band) -> MatrixRegion | None` unchanged in signature; `MatrixRegion.body_line`
  now carries the **derived** start; `col_tree` levels are `band.lines[:body_start]`.

- [ ] **Step 1: Write the failing test** (append to `tests/etkl/test_matrix.py`; add
  `three_level_numeric_header_pdf` to its fixture import, and `Graph`, `URIRef`,
  `assert_matrix_region`, `region_tiles` imports)

```python
def test_numeric_third_header_level_is_a_header_level(tmp_path):
    """O1 (spec § 5). The years line is typed body by header-body-split.rq (a Numeric line over
    Currency lines is one Quantity family) but carries no stub cell, so the matrix body cannot
    start there. Reproduces apple p0 band 2 (spec § 1.2: three levels, tiles) on a synthetic.
    Falsified by reverting classify_matrix to the type split: logical_rows finds no anchor
    column and the region is None."""
    p = tmp_path / "x.pdf"; three_level_numeric_header_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    mreg = classify_matrix(band)
    assert mreg is not None
    assert mreg.body_line == 3
    assert sorted({n.level for n in mreg.col_tree}) == [0, 1, 2]
    years = {n.covers: n.text for n in mreg.col_tree if n.level == 2}
    assert years == {(1,): "2026", (2,): "2025", (3,): "2026", (4,): "2025"}
    for n in mreg.col_tree:
        if n.level == 2:
            parent = mreg.col_tree[n.parent]
            assert parent.level == 1 and parent.covers == n.covers
    assert len(mreg.leaf_rows) == 3                    # 'Sales:' section row + two data rows
    g = Graph()
    assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), 0)
    assert region_tiles(g) is True
```

- [ ] **Step 2: Run to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix.py::test_numeric_third_header_level_is_a_header_level -q`
Expected: FAIL at `assert mreg is not None` (S6: HEAD classify is None on this fixture).

- [ ] **Step 3: Wire it in.** In `classify_matrix`, after `k` is derived and `stub_cols`/`data_cols`
  are built, call `matrix_body_start(band, grid, split, k)`; return `None` when it is None; then use
  its result at the three sites S1 names (the column-tree `split` argument, `band.lines[...].top`
  for `logical_rows`, and `MatrixRegion`'s `body_line`). `k` is **not** re-derived (spec § 3.1 third
  invariant, § 8). Update the module docstring's order-of-operations to spec § 3.3, and
  `infer_column_tree_by_proximity`'s docstring where it says `header_body_split returns it` — it now
  receives the matrix body start, and the statement "a header LEVEL IS A BAND LINE" still holds.
  Do NOT touch `is_matrix_candidate` (Global Constraints; record the reconciliation in the report).

- [ ] **Step 4: Run the matrix files**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix.py tests/etkl/test_matrix_body_start.py tests/etkl/test_holon.py tests/etkl/test_tiling_gate.py tests/etkl/test_closing_slice.py tests/etkl/test_section_repair.py -q`
Expected: all pass. The last three exercise `MATRIX_AMBIGUOUS` paths (`grep -rn MATRIX_AMBIGUOUS tests/etkl`)
and must not move; if one does, that is a finding to report, not a test to edit.

- [ ] **Step 5: FALSIFICATION** — in `classify_matrix`, temporarily pass `split` instead of the
  derived start at the `logical_rows` site only; the new test must FAIL at `mreg is not None`.
  Restore; green. Paste both runs.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/matrix.py tests/etkl/test_matrix.py
git commit -m "feat(matrix): classify_matrix starts the body at the first stub-bearing line"
```

---

## Task 4: The uncarried-ink refusal (B — producer-side guard; O3, O4)

**Files:**
- Modify: `src/iladub/etkl/matrix.py::infer_column_tree_by_proximity`
- Modify: `tests/etkl/fixtures.py` (one new fixture)
- Modify: `tests/etkl/test_matrix.py`

**Interfaces:**
- Consumes: `regions.column_of(x_center, boundaries) -> int`; the nodes built inside the function.
- Produces: `infer_column_tree_by_proximity(band, grid, split, data_cols)` — **signature unchanged**;
  returns `None` when any word on a header level (`band.lines[:split]`) whose centre falls in a
  column in `data_cols` is not the `text` of some node. Words whose centre falls in a stub column
  are exempt (spec § 3.2, the WHO `Year: Month` case).

- [ ] **Step 1: Add the fixture**

`unruled_multiword_spanner_pdf(path) -> dict`. Geometry (S6): stub x = 55; data centres 300, 400;
top = `PAGE_H - 90`; Courier-Bold 9 header, Courier 9 body. L0: `Nine Months Ended` drawn as ONE
string centred at 350 (pdfplumber splits it into three words — the test measures this). L1 (top − 13):
`Jun`, `Sep`. L2 (top − 26): `2026`, `2025`. Body from top − 44 at 16pt pitch: `Cash` with
`35,934 29,943`, `Debt` with `1,200 1,100`. **No rules drawn.** Return
`{"spanner_words": ["Nine", "Months", "Ended"], "n_data_cols": 2}`. Docstring: cite spec § 1.3 and
§ 4 (grouping is NEURAL and not this loop) — this is apple p2 band 2's shape.

- [ ] **Step 2: Write the failing tests** (append to `tests/etkl/test_matrix.py`; import the fixture,
  `stub_data_split`, `matrix_body_start`)

```python
def test_a_header_word_carried_by_no_node_refuses_the_tree(tmp_path):
    """O3 (spec § 5; § 1.3 Finding B). On an unruled band a multi-word spanner is three pdfplumber
    words; nearest-centre assignment lets two of them win the two data columns and the third
    ('Months') becomes no node at all. Asserting that tree emits a header with a third of its
    ink gone (CLAUDE.md §7). The guard refuses; compile escalates MATRIX_AMBIGUOUS at the existing
    site. Falsified by deleting the guard: the tree has 6 nodes for 7 data-column header words
    and classify_matrix returns a region that tiles."""
    p = tmp_path / "x.pdf"; unruled_multiword_spanner_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    assert [w.text for w in band.lines[0].words] == ["Nine", "Months", "Ended"]   # measured, not assumed
    assert band.rules == ()
    grid = recover_leaf_grid(band)
    split = header_body_split(band, grid); k = stub_data_split(band, grid)
    body = matrix_body_start(band, grid, split, k)
    assert (split, k, body) == (2, 1, 3)
    assert infer_column_tree_by_proximity(band, grid, body, tuple(range(k, grid.ncols))) is None
    assert classify_matrix(band) is None


def test_a_stub_column_header_does_not_trigger_the_guard(tmp_path):
    """O4 (spec § 5; § 3.2). WHO's 'Year: Month' sits over the STUB column at a header level;
    it is never a column-tree node and must not be counted as dropped ink. Falsified by removing
    the data-column condition from the guard: 'Segment' is uncarried and the band refuses."""
    p = tmp_path / "x.pdf"; three_level_numeric_header_pdf(str(p), corner="Segment")
    band = detect_bands(text_lines(extract_words(str(p))))[-1]
    assert band.lines[1].words[0].text == "Segment"
    mreg = classify_matrix(band)
    assert mreg is not None
    assert "Segment" not in {n.text for n in mreg.col_tree}
    assert sorted({n.level for n in mreg.col_tree}) == [0, 1, 2]
```

- [ ] **Step 3: Run to verify they fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix.py -q -k "no_node or stub_column_header"`
Expected: O3 FAILS at `infer_column_tree_by_proximity(...) is None` (S6: without the guard the tree
has 6 nodes); O4 PASSES already — it is the guard's *exemption* and exists to fail when Step 4 is
written too broadly. Say so in the report; a test that is green before its subject exists is only
useful with its falsification (Step 6).

- [ ] **Step 4: Write the guard.** After the `nodes` list is complete and before parent linking:
  collect every word on `levels` whose centre column (`column_of((w.x0 + w.x1) / 2.0, b)`) is in
  `data_cols`; if any such word's `text` is not the `text` of some node, `return None`. Compare on
  the **word object's text at that level**, not across levels (two levels may legitimately repeat a
  text — apple's `June 27,` appears twice on L1 and is carried twice). The simplest faithful form
  compares per level: the set of data-column word texts on level L must be a subset of the node
  texts at level L. No constant. Docstring: classify it (spec § 2 B), name the CLAUDE.md ruling
  (§ "Producer-side guards vs the membrane") and say in one sentence why the membrane cannot
  enforce it (the dropped ink never enters the graph).

- [ ] **Step 5: Run the matrix files + the two corpus-free `MATRIX_AMBIGUOUS` tests**

Run: `./.venv/bin/python -m pytest tests/etkl/test_matrix.py tests/etkl/test_matrix_body_start.py tests/etkl/test_closing_slice.py tests/etkl/test_section_repair.py tests/etkl/test_vacuity_registry.py -q`
Expected: all pass.

- [ ] **Step 6: FALSIFICATION, two legs** — (a) delete the guard: O3 FAILS (report the node count
  the tree carried and the data-column word count); (b) restore, then drop the `in data_cols`
  condition: O4 FAILS at `mreg is not None`. Restore; green. Paste all three runs.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/matrix.py tests/etkl/fixtures.py tests/etkl/test_matrix.py
git commit -m "feat(matrix): refuse a column tree that carries no node for a data-column header word"
```

---

## Task 5: The corpus leg (O5) — apple pins, WHO byte-identical, the battery, the manifest

**Files:**
- Create: `tests/etkl/test_apple_statement_headers.py` (corpus-marked)
- Modify: `tests/corpus-manifest.ttl` (apple: second `cor:adjudication`)

**Interfaces:**
- Consumes: `compile.page_bands(pdf, page)`, `matrix.classify_matrix`, `holon.assert_matrix_region`,
  `tiling.region_tiles`, `document.compile_document`; Task 1's `baseline-HEAD.json`.

- [ ] **Step 1: Write the corpus-marked test**

```python
# tests/etkl/test_apple_statement_headers.py
"""Spec 2026-09-02-the-body-starts-at-the-stub-design.md § 5 O5, the apple leg. Real document,
gitignored corpus/ — skips when absent, never in CI. Band indices measured 2026-09-02 (plan S4/S5).
These pin READINGS (levels, entries, tiling), never the score (spec § 1.4)."""
import os
import pytest
pytest.importorskip("pdfplumber")
from rdflib import Graph, URIRef
from iladub.etkl.compile import page_bands
from iladub.etkl.matrix import classify_matrix
from iladub.etkl.holon import assert_matrix_region
from iladub.etkl.tiling import region_tiles

pytestmark = pytest.mark.corpus
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")


def _band(page, idx):
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    return page_bands(APPLE, page)[idx]


def _asserted(band, page):
    mreg = classify_matrix(band)
    assert mreg is not None
    g = Graph()
    n = assert_matrix_region(g, mreg, band, URIRef("urn:t"), URIRef("urn:doc"), page)
    assert region_tiles(g) is True
    return mreg, n


def test_p0_income_statement_header_is_three_levels():
    """Spec § 1.2: Three/Nine Months Ended over June 27,/June 28, over 2026/2025; 28 entries."""
    band = _band(0, 2)
    assert [w.text for w in band.lines[2].words] == ["2026", "2025", "2026", "2025"]
    mreg, n = _asserted(band, 0)
    assert mreg.body_line == 3
    assert sorted({x.level for x in mreg.col_tree}) == [0, 1, 2]
    assert len(mreg.leaf_rows) == 9 and n == 28


def test_p1_balance_sheet_header_is_two_levels():
    """Spec § 8 (measured after approval): June 27,/September 27, over 2026/2025; 14 entries."""
    mreg, n = _asserted(_band(1, 2), 1)
    assert mreg.body_line == 2
    assert sorted({x.level for x in mreg.col_tree}) == [0, 1]
    assert n == 14


def test_p2_unruled_header_refuses_rather_than_dropping_ink():
    """Spec § 1.3 Finding B / § 3.2: 'Nine Months Ended' is three pdfplumber words on an unruled
    band; 'Months' and both 'June's would be carried by no node. Honest MATRIX_AMBIGUOUS."""
    band = _band(2, 2)
    assert band.rules == ()
    assert [w.text for w in band.lines[0].words] == ["Nine", "Months", "Ended"]
    assert classify_matrix(band) is None


def test_document_scope_adoption_is_pre_empted_and_recorded():
    """Spec § 1.4: once p1's header band asserts, adoption-candidate.rq's NOT EXISTS tab:EntryCell
    gate refuses the page-1 datagrid adoption. adopted (1,) -> (). Raised as R160, not fixed here.
    The score is printed, never asserted."""
    if not os.path.exists(APPLE):
        pytest.skip("apple corpus document not fetched")
    from iladub.etkl.document import compile_document
    rep = compile_document(APPLE)
    print(f"apple score {rep.score:.4f} adopted {rep.adopted}")
    assert rep.adopted == ()
    reasons = [r.reason for p in rep.pages for r in p.regions]
    assert reasons.count("MATRIX_AMBIGUOUS") == 1          # p2 band 2 only; p0's is now asserted
```

- [ ] **Step 2: Run it**

Run: `./.venv/bin/python -m pytest -m corpus tests/etkl/test_apple_statement_headers.py -q -s`
Expected: 4 passed. The report-side `MATRIX_AMBIGUOUS` count at HEAD is **2** (Task 1: p0 region 2
and p2 region 2; p1 region 2 is `superseded / KIND_NOT_SUPPORTED`, not a matrix escalation). After
this loop p0's asserts and p2's stays, so 1. If your count is not 1, MEASURE which regions carry it
before touching the assertion; a count the spec did not predict is a finding, not a test to edit.

- [ ] **Step 3: Re-run Task 1's script and diff**

Run: `./.venv/bin/python <scratchpad>/baseline.py <scratchpad>/baseline-AFTER.json && diff <(python -m json.tool <scratchpad>/baseline-HEAD.json) <(python -m json.tool <scratchpad>/baseline-AFTER.json)`
Expected: **WHO: no line differs** (score, adopted, every region tuple) — that is O5's byte-identical
leg. apple: `adopted [1] → []`, score down from 0.3587, region verdicts move only on p0 band 2, p1
band 2 and p1's previously-superseded bands (spec § 1.4). Paste the WHO diff (empty) and the apple
diff in the report.

- [ ] **Step 4: Run the full battery** (first run in seven loops — spec § 5 O5; ~5 min per document,
  320 s alarm each)

Run: `./.venv/bin/python -m pytest -m corpus tests/test_corpus.py tests/etkl/test_typing_equiv.py -q -s 2>&1 | tee <scratchpad>/battery.log`
Expected: every document present passes its floor (WHO ≥ 0.90, gstem ≥ 0.95; gcap, ons, cbh, bfs at
their manifest floors). `test_typing_equiv.py` pins apple's page-0 **kind/split** verdicts — those
must not move (`header_body_split` is untouched). Record every printed score. A document under its
floor: STOP, report.

- [ ] **Step 5: The manifest** — append a second `cor:adjudication [ … ]` node to the apple document
  in `tests/corpus-manifest.ttl` (keep the 2026-08-20 node; the register never deletes evidence),
  `cor:on "2026-09-02"^^xsd:date`, `cor:by` naming the agent and the accountable human as the
  existing node does, and a `cor:rationale` that states: still HOLD / `cor:Unadjudicated`, no floor;
  the 2026-08-20 "one double header the matrix reader cannot resolve" is superseded — p0 and p1
  header bands assert (spec § 1.2, § 8), p2 band 2 escalates `MATRIX_AMBIGUOUS` for the honest
  reason (uncarried unruled header words); the page-1 datagrid adoption is pre-empted
  (`adopted (1,) → ()`, R160); the measured score from Step 2. Then:

Run: `./.venv/bin/python -m pytest tests/test_corpus_manifest.py -q`
Expected: pass (the shape allows a second adjudication node — if it refuses, report the message;
do not restructure the shape in this loop).

- [ ] **Step 6: FALSIFICATION** — `git stash` the `src/` changes (Tasks 2–4), run Step 1's file:
  `test_p0_…` FAILS at `mreg is not None`, `test_p2_…` FAILS at `classify_matrix(band) is None`
  (S5: HEAD builds a region there). `git stash pop`; green. Paste.

- [ ] **Step 7: Commit**

```bash
git add tests/etkl/test_apple_statement_headers.py tests/corpus-manifest.ttl
git commit -m "test(corpus): pin apple's statement headers as readings; supersede the 2026-08-20 census note"
```

---

## Task 6: The register, the exemplar, and the suite

**Files:**
- Modify: `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`
- Modify: `docs/wiki/concepts/neurosymbolic-exemplars.md`, `docs/wiki/index.md`

Tally convention (CLAUDE.md § Deferred residues; measured 2026-09-02: 42 closed of 149 rows, last row
R159 `(42/148 closed)`): the five new rows are **R160 (42/149 closed)** through **R164 (42/153
closed)**, denominator incrementing per row. Nothing closes in this loop.

- [ ] **Step 1: Five rows, from spec § 7, each with the four columns filled** (residue · measured ·
  why deferred · what would close it). Index line in `residues.md` (status `open`), full row in
  `residues-open.md`:

  - **R160** — the datagrid adoption gate is pre-empted by one asserting band. Measured: Task 5
    Step 3's diff (`adopted [1] → []`, HEAD 0.3587 → the measured score); mechanism
    `vocab/queries/adoption-candidate.rq`'s `NOT EXISTS tab:EntryCell`. Deferred: a reader-authority
    question touching R73's monotonicity premise; the maintainer chose to accept the drop (spec § 1.4).
    Closes: a stated rule for which reader has authority when a band reader and a whole-page reader
    both apply, plus the apple p1 case as its oracle.
  - **R161** — loop Q's section repair never fires on apple p0/p2 (8 of 11 escalations are
    `REGION_TILING_FAILED`; `DocumentReport.repaired_bands == ()`); cause unmeasured. Measured:
    Task 1/5 JSON. Closes: a measurement of why `sectiongraph.section_candidates` recognizes nothing
    on those pages, then a loop.
  - **R162** — unruled header labels are words: one `Line.words` abstraction carries two granularities
    (ruled cell vs pdfplumber word). Measured: plan S5 (apple p2 band 2, 9 words / 6 nodes) and
    `_build_ruled_band`'s re-extraction on p0. Deferred: grouping is NEURAL by §8's wording and
    [[R155]] measured its geometric half impossible without a constant. Closes: a NEURAL proposer
    under [[R155]]'s five-sided oracle, or a ruling that unruled multi-word spanners stay escalated.
  - **R163** — the guard's refusal carries no named reason: `MATRIX_AMBIGUOUS` now covers both "no
    anchor column" and "uncarried header ink". Measured: `compile.py`'s single escalation site
    (`escalate_region(..., "MATRIX_AMBIGUOUS", ...)`), Task 4. Closes: a `tab:`/`dec:` increment naming
    the reason, with the band recorder's rationale updated.
  - **R164** — spec § 1.5 is a six-band oracle: four non-apple bands agree with the rule, and that
    is LOW power. Measured: spec § 1.5 table. Closes: a corpus band whose type split and first stub
    line differ for a reason other than a numeric header level — or a stated acceptance that the unit
    fixtures (Tasks 2–4) are the falsifying instrument and the corpus is the regression check only.

- [ ] **Step 2: The exemplar.** Add a dated section to `docs/wiki/concepts/neurosymbolic-exemplars.md`
  in the house format (see the Loop P section): `matrix-body-start.rq` as an AXIOM derivation (what
  it derives, evidence-positive, band-scoped, two bindings, no constant) and the uncarried-ink guard
  as a **producer-side guard justified by CLAUDE.md § "Producer-side guards vs the membrane"** — say
  explicitly that it is *not* a third PROCEDURAL exemplar but a closed-world check the membrane
  provably cannot host. Add the `.rq` and `matrix.py` to `sources:`, bump `updated:` to 2026-09-02,
  and update the `updated` cell for this page in `docs/wiki/index.md`.

- [ ] **Step 3: Governance + the full non-corpus suite** (~45 min; memory `used-as-vocabulary-loop`)

Run: `./.venv/bin/python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py tests/test_query_declarations.py -q`
Expected: pass.
Run: `./.venv/bin/python -m pytest -m "not corpus" -q 2>&1 | tail -5`
Expected: all pass. Paste the summary line.

- [ ] **Step 4: FALSIFICATION for a docs task** — none of Step 1–2 pins code; the falsifiable claim
  is the tally. Run `grep -c "^| R[0-9]* | closed" docs/superpowers/residues.md` (expect 42) and
  `grep -o "^| R16[0-4] ([0-9/]* closed)" docs/superpowers/residues-open.md` (expect the five
  denominators 149…153). Paste.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/residues-open.md docs/wiki/concepts/neurosymbolic-exemplars.md docs/wiki/index.md
git commit -m "docs: R160–R164 raised; matrix-body-start recorded as an AXIOM exemplar"
```

Then hand to `superpowers:finishing-a-development-branch`: PR against `main`; the ruleset requires
the `test` check green and `gh pr merge --auto` now waits for it (CLAUDE.md § Branch protection).

---

## Self-Review

**Spec coverage.** § 3.1 → Tasks 2–3. § 3.2 → Task 4. § 3.3 ordering → Task 3 Step 3 + Global
Constraints. § 4 (not done) → Global Constraints reconciliation; no task builds any of it. § 5:
O1 → Task 3; O2 → Task 2; O3, O4 → Task 4; O5 → Tasks 1 + 5; O6 → Task 2 Step 5. § 6 seams → S1–S3
measured above. § 7 → Task 6 Step 1 (five rows). § 8 assumptions: `k` not re-derived → Task 3 Step 3;
`run_scalar` two bindings → S2 measured; the `- 0.5` in `rows.py:28` is consumed and untouched.
Doc impact → header + Task 5 Step 5 + Task 6 Step 2.

**Placeholder scan.** No TBD/TODO. The one thing an implementer must *author* rather than transcribe
is the SPARQL and the two Python bodies — by plan-rule 1, deliberately.

**Type consistency.** `matrix_body_start(band, grid, split: int, k: int) -> int | None` is the same
in Task 2's Produces, Task 3's Consumes and Task 4's test. `three_level_numeric_header_pdf(path,
corner=None)` and `unruled_multiword_spanner_pdf(path)` match between fixture steps and tests.
`MatrixRegion.body_line` is the derived start everywhere it is asserted (3 on the O1 fixture and
apple p0; 2 on apple p1).

**One known tension, stated once.** Spec § 3.1 says `is_matrix_candidate` also consumes the new
result; this plan leaves it untouched, with the measured reason in Global Constraints. If the
implementer or reviewer disagrees, the spec is the file to amend — not the plan.
