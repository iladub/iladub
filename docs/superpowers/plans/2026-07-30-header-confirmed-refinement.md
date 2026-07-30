# Header-confirmed rule refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the columns the author's rules left out — and only those — by making interior-gutter boundaries **candidates** that the header must **confirm** before they become columns; and close the crash class that killed attempt 1 by gating the last un-gated region path behind the SHACL membrane.

**Architecture:** Attempt 1's three commits are cherry-picked as the base (candidate generator, `Band.column_xs`, sub-band carry — all reviewer-verified sound). A new AXIOM (`vocab/queries/confirm-boundary.rq` over a per-band evidence graph, engine glue in `src/iladub/etkl/boundary.py`) confirms a candidate only when header-region **char** ink lies strictly on both sides within its author interval with no straddling glyph. `compile.py`'s ruled-band construction is extracted into a callable helper (the real test seam) that wires confirmation in; the plain hierarchical assert gets the same scratch+`region_tiles` gate the matrix/row-hier paths already have.

**Tech Stack:** Python 3 (`src/iladub/etkl/`), rdflib SPARQL, pySHACL (existing `region_tiles`), RDF Turtle, reportlab (fixture), pytest.

**Spec:** `docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md`. Read §2 — every design choice traces to a measurement there, including two refuted alternatives.

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from the repo root, `/Volumes/WD Green/dev/git/iladub`.

**Pace:** **targeted** tests per task; the full suite runs **once**, in Task 5. It takes ~165s and exceeds the default 120s tool timeout — set the Bash tool's `timeout` to `400000` ms and run it in the FOREGROUND. Never background a command.

**Baseline:** 609 passed, 5 skipped (`main` at `3326b8b`). Branch `iladub-header-confirmed-refinement` is already checked out (spec committed at `5573205`).

## Global Constraints

- **The header is the only decider of a candidate's fate.** Confirmation lives entirely in `confirm-boundary.rq` — evidence-positive, open-world, **no numeric literal** (every bound is data; `test_transform_gate.py::test_no_tuned_constant_in_rq_files` covers it automatically). No Python may accept or reject a candidate by geometry or magnitude.
- **CHAR-level ink, never Words.** The real target's leaf header extracts as one word blob (`CompletedCommodityTotal`, x 716.3–818.4) that straddles the true boundary 753.7 at word level and would self-reject; its chars do not straddle. Space glyphs are not ink (Loop F) and are filtered before the evidence graph.
- **Every refusal path degrades to `main`'s measured behavior** — no candidates, no header/body split, none confirmed, membrane refusal. Never a crash, never a new state.
- **`Band.rules` is never synthesised.** Author's marks only; derived boundaries live in `Band.column_xs`. The guard test must call **production code** (attempt 1's guard replicated the logic in the test body and was proven tautological — its C2 finding).
- **Inherited constants, stated:** candidate generation reuses `gutter_pct = 0.98` / `min_gutter_bins = 3` from `infer_leaf_grid`. Do not tune them; do not add any new threshold, width, or tolerance anywhere.
- **The discriminating success criterion is the header-label count** (17 on GrainCorp). Cells/score are secondary only — attempt 1 proved 509 / 0.9496 held identically at the broken and correct grids.
- **Never weaken an existing test.** (Task 3 *replaces* one attempt-1 test that the final review proved tautological with a strictly stronger seam test — that is strengthening, and the commit message must say so.)
- **No third-party PDF committed.**

---

## File Structure

| File | Responsibility |
| --- | --- |
| *(cherry-picked)* `geometry.refine_rule_columns`, `Band.column_xs`, `grid._rule_boundaries`, `cells.recover_leaf_grid` | Attempt 1's base, unchanged code, 10 tests. |
| `src/iladub/etkl/geometry.py` | **Modify** — correct `refine_rule_columns`' docstring (the I1 false attribution + the I3 discontinuity note). |
| `vocab/ontology/tab.ttl` | **Modify (append)** — `tab:HeaderGlyph`, `tab:CandidateBoundary` + 5 properties (transient evidence terms). |
| `vocab/queries/confirm-boundary.rq` | **Create** — the confirmation AXIOM. |
| `src/iladub/etkl/boundary.py` | **Create** — evidence emitter + query runner (PROCEDURAL glue only). |
| `src/iladub/etkl/compile.py` | **Modify** — extract `_build_ruled_band` (the seam), wire confirmation; gate the plain hierarchical assert. |
| `tests/etkl/fixtures.py` | **Modify (append)** — `aligned_space_table_pdf`, the committed counter-example. |
| `tests/etkl/test_boundary_confirmation.py` | **Create** — AXIOM unit tests (Task 2). |
| `tests/etkl/test_header_confirmed_refinement.py` | **Create** — the red parity test + seam test (Task 3) + membrane test (Task 4). |
| `tests/etkl/test_rule_column_refinement.py` | **Modify** — Task 3 removes the tautological guard it replaces. |
| `docs/superpowers/residues.md`, spec status line | **Modify** — Task 5. |

Task order: 1 → 2 → 3 → 4 → 5.

---

## Probed values (measured while planning — assert, do not re-derive)

- Plain `git cherry-pick 9230075 9ff6089 70768fd` applies **cleanly** on this branch (probed).
- **Real GrainCorp leaf-header char runs** in the interval `[715.2, 829.92]` (measured at char level, top 80.5–82): `Completed` 716.3–743.6, `Commodity` 764.2–**793.5**, `Total` 805.8–818.4. Neither candidate (753.7, 798.7) is straddled; both confirm. (An early probe wrongly gave `Commodity` a 800.4 tail and self-rejected 798.7 — the *measured* extent is 793.5. Use the measured numbers.)
- Aligned fixture: header `ID` glyphs 60–65.4, 65.4–70.8; candidate 73.5 in [50, 170] → **one-sided, rejected**. `Tonnes` glyph `n` 310.8–316.2 straddles its interval's candidate → **straddle-rejected** (the fixture exercises both refusal clauses).
- On attempt 1's code, the aligned fixture **raises `AssertionError`** inside `compile_tables` (final SHACL validate, `tab:CoverageShape`); on `main` it compiles `RECORD_TABLE`, 18 cells, score 1.0. That is the red/green pair for Task 3.
- Membrane sabotage (probed on `partial_merge_report_pdf`): setting the last leaf node's `covers=()` passes `merge_tiling_ok` (True — it checks overlap/centering, not coverage), asserts `n=10`, and **fails `region_tiles`** (False). Deterministic red test for Task 4; before the backstop it crashes at final validate.

---

### Task 1: Cherry-pick attempt 1's base + correct its docstring

**Files:**
- Cherry-picked: `src/iladub/etkl/geometry.py`, `bands.py`, `grid.py`, `cells.py`, `compile.py`, `tests/etkl/test_rule_column_refinement.py`
- Modify: `src/iladub/etkl/geometry.py` (docstring of `refine_rule_columns` only)

**Interfaces:**
- Consumes: commits `9230075`, `9ff6089`, `70768fd` (present on the local branch `iladub-rule-column-refinement`).
- Produces: `geometry.refine_rule_columns(chars, rule_xs, gutter_pct=0.98, min_gutter_bins=3) -> list[float]`; `Band.column_xs: tuple[float, ...] = ()`; `_rule_boundaries` preferring `column_xs`; the sub-band carry in `recover_leaf_grid`. **Note:** the cherry-picked `compile.py` wiring asserts refinement unconditionally — that is attempt 1's crash behavior, and Task 3 replaces it. Do not "fix" it in this task.

- [ ] **Step 1: Cherry-pick**

```bash
git cherry-pick 9230075 9ff6089 70768fd
```
Expected: applies cleanly (probed). If a conflict appears anyway, stop and report — do not resolve by hand.

- [ ] **Step 2: Run the carried tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: **10 passed.**

- [ ] **Step 3: Correct the docstring (attempt 1's I1 finding — a false measured claim now in source)**

In `src/iladub/etkl/geometry.py`, `refine_rule_columns`' docstring, replace this paragraph:

```
    THE INTERIOR CONDITION IS LOAD-BEARING — do not drop it. Without it, a blank run at a cell's
    trailing edge (short left-aligned text) reads as a separator: measured, that adds a boundary to
    EVERY interval of ruled_tight_table_pdf, turning 5 columns into 10. With it, both shipped ruled
    fixtures gain ZERO and the real document gains exactly the two it should. It is a presence test
    ("is there ink beyond this run, inside this interval"), not a threshold.
```

with:

```
    TWO independent mechanisms reject trailing padding, and the attribution matters (attempt 1's
    docstring credited the wrong one; the final review measured it):
      - NO-FLUSH: a run still open at the interval's end is never emitted (the run-reset below has
        no end-of-loop flush). Removing the interior condition ALONE leaves both shipped ruled
        fixtures at +0 — the no-flush is what protects them.
      - THE INTERIOR CONDITION (ink on both sides, within the interval) rejects one-sided runs
        that close before the interval ends. The naive +5/+2 over-split reported for the fixtures
        requires removing BOTH mechanisms.
    Both are presence tests, not thresholds. AND the caller must still not trust the output:
    values with COLUMN-ALIGNED internal spaces produce candidates indistinguishable from real
    boundaries here (the attempt-1 counter-example that crashed compile_tables) — which is why
    these are CANDIDATES, confirmed against header ink (boundary.py / confirm-boundary.rq) before
    ever becoming columns.
```

And immediately after the existing "`gutter_pct` and `min_gutter_bins` mirror `infer_leaf_grid`'s existing defaults…" sentence, add:

```
    CAVEAT (measured, attempt 1's I3): with per-interval row counts N, gutter_pct = 0.98 is
    discontinuous at N = 50 — a bin is "blank" iff inked in <= floor(0.02*N) rows: ZERO rows below
    50, ONE row at 50 and above. N here is PER INTERVAL (GrainCorp's one table ran at N = 4..54),
    unlike infer_leaf_grid's per-band N. Tolerable for CANDIDATES only because header confirmation
    disposes misfires; never promote this function's output without confirmation.
```

- [ ] **Step 4: Re-run the carried tests (docstring-only change)**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: **10 passed**, unchanged.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/geometry.py
git commit -m "docs(etkl): refine_rule_columns states the TRUE trailing-run mechanism (attempt 1 I1/I3)"
```

---

### Task 2: The confirmation AXIOM — vocab, query, engine glue

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append at end)
- Create: `vocab/queries/confirm-boundary.rq`
- Create: `src/iladub/etkl/boundary.py`
- Test: `tests/etkl/test_boundary_confirmation.py` (create)

**Interfaces:**
- Consumes: nothing from Task 1 (standalone).
- Produces: `boundary.confirmed_boundaries(header_glyphs, candidates) -> set[float]`, where `header_glyphs` is a sequence of objects exposing `.x0`/`.x1` (non-space chars — the **caller** filters spaces) and `candidates` is a sequence of `(boundary_x, interval_lo, interval_hi)` tuples. Also `boundary.boundary_evidence(...) -> Graph` and `boundary.CONFIRM_BOUNDARY_RQ: Path`.

- [ ] **Step 1: Confirm the new vocabulary does not already exist**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && grep -n "HeaderGlyph\|glyphX0\|glyphX1\|CandidateBoundary\|boundaryX\|intervalLo\|intervalHi" vocab/ontology/tab.ttl vocab/shapes/*.ttl vocab/queries/*.rq
```
Expected: **no output** (exit 1). If anything is found, STOP and report (the B2c lesson).

- [ ] **Step 2: Write the failing test**

Create `tests/etkl/test_boundary_confirmation.py`:

```python
"""Loop G attempt 2 — header confirmation of candidate column boundaries (the AXIOM).

A candidate boundary (an interior gutter the author's rules left out) becomes a column ONLY if the
header region places glyph ink strictly on both sides of it within its author interval, with no
header glyph straddling it. This is the evidence tab:CoverageShape enforced by CRASHING attempt 1
(a phantom column no header covers), consulted eagerly instead.

Coordinates are MEASURED, not invented: the GrainCorp leaf-header char runs are Completed
716.3-743.6, Commodity 764.2-793.5, Total 805.8-818.4, and the candidates are 753.7 and 798.7 in
the author interval [715.2, 829.92]. The aligned-fixture cases are the counter-example that killed
attempt 1. See docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md §2.
"""
from iladub.etkl.boundary import confirmed_boundaries


class _G:
    """Minimal glyph: the runner only reads .x0/.x1."""
    def __init__(self, x0, x1):
        self.x0 = x0
        self.x1 = x1


# real measured GrainCorp leaf-header runs (each run stands in for its chars; extents are what count)
GRAIN = [_G(716.3, 743.6), _G(764.2, 793.5), _G(805.8, 818.4)]
GRAIN_CANDS = [(753.7, 715.2, 829.92), (798.7, 715.2, 829.92)]

# the counter-example's ID header ('I' 60-65.4, 'D' 65.4-70.8); its candidate is 73.5 in [50, 170]
ALIGNED_ID = [_G(60, 65.4), _G(65.4, 70.8)]


def test_both_sided_header_ink_confirms_both_real_boundaries():
    assert confirmed_boundaries(GRAIN, GRAIN_CANDS) == {753.7, 798.7}


def test_one_sided_header_ink_is_rejected():
    # THE COUNTER-EXAMPLE: the author labeled only the left side ('ID'); the phantom column has
    # no header ink, so the split that crashed attempt 1 is refused here.
    assert confirmed_boundaries(ALIGNED_ID, [(73.5, 50.0, 170.0)]) == set()


def test_straddling_glyph_rejects():
    # the fixture's Tonnes column: the 'n' glyph 310.8-316.2 contains the candidate 313.5 —
    # a label cannot be split through a glyph.
    glyphs = [_G(300, 305.4), _G(305.4, 310.8), _G(310.8, 316.2), _G(316.2, 321.6)]
    assert confirmed_boundaries(glyphs, [(313.5, 290.0, 395.0)]) == set()


def test_empty_header_region_confirms_nothing():
    assert confirmed_boundaries([], GRAIN_CANDS) == set()


def test_candidates_are_judged_independently():
    # ink around 753.7 only -> only it confirms; 810.0 has no right-side witness
    glyphs = [_G(716.3, 743.6), _G(764.2, 793.5)]
    assert confirmed_boundaries(glyphs, [(753.7, 715.2, 829.92), (810.0, 715.2, 829.92)]) == {753.7}


def test_no_candidates_short_circuits():
    assert confirmed_boundaries(GRAIN, []) == set()


def test_witness_must_lie_inside_the_interval():
    # header ink LEFT of the interval must not act as a left witness
    glyphs = [_G(30.0, 45.0), _G(764.2, 793.5)]          # left glyph outside [715.2, 829.92]
    assert confirmed_boundaries(glyphs, [(753.7, 715.2, 829.92)]) == set()
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_boundary_confirmation.py -q`
Expected: **collection error** — `ModuleNotFoundError: No module named 'iladub.etkl.boundary'`.

- [ ] **Step 4: Append the vocabulary to `vocab/ontology/tab.ttl`**

Append at the very end:

```turtle

# --- header-confirmed boundary evidence (transient, pre-holon; loop G attempt 2) ---
tab:HeaderGlyph a owl:Class ; rdfs:label "Header glyph"@en ;
    rdfs:comment "A transient header-region character's ink x-extent, evidence for the boundary-confirmation derivation (confirm-boundary.rq); never asserted into a holon. CHAR-level on purpose: the real target's leaf header extracts as one word blob that straddles the true boundary at word level and would self-reject."@en .
tab:glyphX0 a owl:DatatypeProperty ; rdfs:domain tab:HeaderGlyph ; rdfs:range xsd:double ; rdfs:label "glyph x0"@en .
tab:glyphX1 a owl:DatatypeProperty ; rdfs:domain tab:HeaderGlyph ; rdfs:range xsd:double ; rdfs:label "glyph x1"@en .
tab:CandidateBoundary a owl:Class ; rdfs:label "Candidate boundary"@en ;
    rdfs:comment "A transient candidate column boundary — an interior gutter the author's rules left out (geometry.refine_rule_columns). CONFIRMED only when header ink lies strictly on both sides within its author interval with no straddling glyph (confirm-boundary.rq); never asserted into a holon."@en .
tab:boundaryX a owl:DatatypeProperty ; rdfs:domain tab:CandidateBoundary ; rdfs:range xsd:double ; rdfs:label "boundary x"@en .
tab:intervalLo a owl:DatatypeProperty ; rdfs:domain tab:CandidateBoundary ; rdfs:range xsd:double ; rdfs:label "interval lo"@en ;
    rdfs:comment "Left edge of the consecutive author-rule interval containing the candidate."@en .
tab:intervalHi a owl:DatatypeProperty ; rdfs:domain tab:CandidateBoundary ; rdfs:range xsd:double ; rdfs:label "interval hi"@en ;
    rdfs:comment "Right edge of that interval."@en .
```

- [ ] **Step 5: Create `vocab/queries/confirm-boundary.rq`**

```sparql
# confirm-boundary.rq — loop G attempt 2 (AXIOM: derivation, open world, evidence-positive).
#
# A candidate column boundary (an interior gutter the author's rules left out) is CONFIRMED iff
# the header region places glyph ink strictly on BOTH sides of it within its author interval, and
# no header glyph straddles it. "The author labeled both sub-columns" is what distinguishes a real
# un-ruled column boundary from a column-aligned word space: the counter-example that killed
# attempt 1 ('AB CDEFGH' under the header 'ID') has header ink on one side only, and is refused
# here by the same fact tab:CoverageShape would have refused — after crashing the compile.
#
# Threshold-free: every bound is data from the evidence graph; NO numeric literal
# (test_no_tuned_constant_in_rq_files). The NOT EXISTS closure is holon-scoped — the band's own
# fresh evidence graph is the closure boundary.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?bx WHERE {
    ?cb a tab:CandidateBoundary ;
        tab:boundaryX ?bx ;
        tab:intervalLo ?lo ;
        tab:intervalHi ?hi .
    FILTER EXISTS {
        ?gl a tab:HeaderGlyph ; tab:glyphX0 ?lx0 ; tab:glyphX1 ?lx1 .
        FILTER(?lx0 >= ?lo && ?lx1 <= ?bx)
    }
    FILTER EXISTS {
        ?gr a tab:HeaderGlyph ; tab:glyphX0 ?rx0 ; tab:glyphX1 ?rx1 .
        FILTER(?rx0 >= ?bx && ?rx1 <= ?hi)
    }
    FILTER NOT EXISTS {
        ?gs a tab:HeaderGlyph ; tab:glyphX0 ?sx0 ; tab:glyphX1 ?sx1 .
        FILTER(?sx0 < ?bx && ?sx1 > ?bx)
    }
}
```

- [ ] **Step 6: Create `src/iladub/etkl/boundary.py`**

```python
"""boundary — header-confirmed boundary evidence graph + query runner (loop G attempt 2).

Candidate column boundaries (interior gutters the author's rules left out) are CONFIRMED only when
the header region places glyph ink strictly on both sides within the candidate's author interval,
with no header glyph straddling it. The decision lives entirely in
vocab/queries/confirm-boundary.rq (open world, evidence-positive, no numeric literal); this module
is PROCEDURAL engine glue only: emit the transient per-band evidence graph and invoke rdflib. The
band is the closure boundary — a fresh Graph() per call (mirrors headergraph.py, loop B).

Why the header is the oracle: attempt 1 asserted interior gutters directly and was killed by a
counter-example — a monospaced ruled table whose values carry a column-aligned internal space
forms the same blank-run signal, and the manufactured phantom column CRASHED compile_tables at
tab:CoverageShape (a leaf column no header covers). Confirmation consults that same evidence
BEFORE asserting: a boundary the author did not label on both sides is not a column.

Why CHAR glyphs, not Words: the real target's leaf header extracts as ONE word blob
('CompletedCommodityTotal', x 716.3-818.4) which straddles the true boundary 753.7 at word level
and would self-reject; its chars do not straddle (Completed ends 743.6, Commodity begins 764.2).
Space glyphs are not ink (loop F) — the CALLER filters them before passing glyphs here.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:boundary:")     # transient per-band instance namespace

CONFIRM_BOUNDARY_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "confirm-boundary.rq"


def boundary_evidence(header_glyphs, candidates) -> Graph:
    """Fresh Graph() for one band. header_glyphs expose .x0/.x1 (non-space header-region chars);
    candidates are (boundary_x, interval_lo, interval_hi) with each interval a consecutive
    author-rule pair containing the candidate."""
    g = Graph()
    for i, ch in enumerate(header_glyphs):
        n = URIRef(f"{_EV}g{i}")
        g.add((n, RDF.type, TAB.HeaderGlyph))
        g.add((n, TAB.glyphX0, Literal(float(ch.x0), datatype=XSD.double)))
        g.add((n, TAB.glyphX1, Literal(float(ch.x1), datatype=XSD.double)))
    for i, (bx, lo, hi) in enumerate(candidates):
        n = URIRef(f"{_EV}b{i}")
        g.add((n, RDF.type, TAB.CandidateBoundary))
        g.add((n, TAB.boundaryX, Literal(float(bx), datatype=XSD.double)))
        g.add((n, TAB.intervalLo, Literal(float(lo), datatype=XSD.double)))
        g.add((n, TAB.intervalHi, Literal(float(hi), datatype=XSD.double)))
    return g


def confirmed_boundaries(header_glyphs, candidates) -> set[float]:
    """Run confirm-boundary.rq over the band's evidence; return the confirmed boundary x's."""
    if not candidates:
        return set()
    g = boundary_evidence(header_glyphs, candidates)
    q = CONFIRM_BOUNDARY_RQ.read_text(encoding="utf-8")
    return {float(row.bx) for row in g.query(q)}
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_boundary_confirmation.py -q`
Expected: **7 passed.**

- [ ] **Step 8: Gate + vocab regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_transform_gate.py tests/etkl/test_tab_vocab.py tests/test_source_ownership.py -q`
Expected: all pass (`test_no_tuned_constant_in_rq_files` now also covers `confirm-boundary.rq`; no `holon:` subject anywhere).

- [ ] **Step 9: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/queries/confirm-boundary.rq src/iladub/etkl/boundary.py tests/etkl/test_boundary_confirmation.py
git commit -m "feat(etkl): confirm-boundary AXIOM — the header confirms candidate columns (loop G attempt 2)"
```

---

### Task 3: The red fixture + compile rewiring through the seam

**Files:**
- Modify: `tests/etkl/fixtures.py` (append)
- Modify: `src/iladub/etkl/compile.py` (extract `_build_ruled_band`; replace the ruled branch)
- Modify: `tests/etkl/test_rule_column_refinement.py` (remove the tautological guard)
- Test: `tests/etkl/test_header_confirmed_refinement.py` (create)

**Interfaces:**
- Consumes: `boundary.confirmed_boundaries` (Task 2); cherry-picked `refine_rule_columns`, `Band.column_xs` (Task 1).
- Produces: module-level `compile._build_ruled_band(sub, sub_rules, sub_hrules, page_chars) -> Band` — **the seam**; `fixtures.aligned_space_table_pdf(path) -> dict`.

- [ ] **Step 1: Add the fixture**

Append to `tests/etkl/fixtures.py` (follow the file's existing reportlab import/style):

```python
def aligned_space_table_pdf(path: str) -> dict:
    """THE R13 COUNTER-EXAMPLE (attempt 1's killer), committed as the permanent red test.

    A monospaced ruled table whose values carry a COLUMN-ALIGNED internal space ('AB CDEFGH',
    '01 JAN 2026', '12 500'). The aligned spaces form a persistent blank run with ink on both
    sides — the same signal as a real un-ruled column boundary — but the header labels only ONE
    side ('ID', 'Date'; and 'Tonnes' straddles its run), so header confirmation must refuse every
    split and the table must compile exactly as if refinement did not exist: RECORD_TABLE,
    18 cells, score 1.0. Attempt 1 asserted the split and CRASHED compile_tables at
    tab:CoverageShape."""
    c = canvas.Canvas(path, pagesize=(400, 200))
    c.setFont("Courier", 9)
    cols = [60, 180, 300]
    header = ["ID", "Date", "Tonnes"]
    rows = [["AB CDEFGH", "01 JAN 2026", "12 500"], ["CD EFGHIJ", "02 FEB 2026", "13 750"],
            ["EF GHIJKL", "03 MAR 2026", "14 250"], ["GH IJKLMN", "04 APR 2026", "15 100"],
            ["IJ KLMNOP", "05 MAY 2026", "16 300"], ["KL MNOPQR", "06 JUN 2026", "17 800"]]
    y = 170
    for i, h in enumerate(header):
        c.drawString(cols[i], y, h)
    y -= 16
    for r in rows:
        for i, v in enumerate(r):
            c.drawString(cols[i], y, v)
        y -= 16
    for x in (50, 170, 290, 395):
        c.line(x, 20, x, 180)
    c.save()
    return {"cols": 3, "data_cells": 18}
```

- [ ] **Step 2: Write the failing tests**

Create `tests/etkl/test_header_confirmed_refinement.py`:

```python
"""Loop G attempt 2 — header-confirmed refinement, end to end.

The parity test is the loop's reason to exist: attempt 1 CRASHED compile_tables on this fixture
(AssertionError at final SHACL validation, tab:CoverageShape — a phantom column no header covers).
With header confirmation, every candidate in this document is refused (one-sided ink for ID/Date,
a straddling glyph for Tonnes) and the compile must be byte-equal to main's.
See docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.compile import compile_tables
from tests.etkl import fixtures as F


def test_aligned_space_counter_example_compiles_as_on_main(tmp_path):
    p = os.path.join(str(tmp_path), "aligned.pdf")
    F.aligned_space_table_pdf(p)
    rep = compile_tables(p)                                    # must NOT raise
    asserted = [(str(r.kind).split(".")[-1], r.verdict, r.cells)
                for r in rep.regions if r.verdict == "asserted"]
    assert asserted == [("RECORD_TABLE", "asserted", 18)], asserted
    assert rep.score == 1.0


def test_build_ruled_band_never_synthesises_a_rule(tmp_path):
    """Attempt 1's C2 redress: the guard calls the PRODUCTION band builder directly — the
    replicated-copy version it replaces was proven tautological (compile.py could synthesise
    Rules and every test stayed green)."""
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.geometry import extract_chars, extract_rules, extract_words, text_lines
    from iladub.etkl.segment import segment

    p = os.path.join(str(tmp_path), "ruled.pdf")
    F.ruled_tight_table_pdf(p)
    page_rules = extract_rules(p, 0)
    page_chars = extract_chars(p, 0)
    authored = {round(r.x, 2) for r in page_rules}
    assert authored, "fixture must be ruled"

    checked = 0
    for band in detect_bands(text_lines(extract_words(p, 0))):
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules
                              if r.top <= sub.bottom and r.bottom >= sub.top)
            if not sub_rules:
                continue
            b = _build_ruled_band(sub, sub_rules, (), page_chars)
            for r in b.rules:
                assert round(r.x, 2) in authored, "a Rule was synthesised for a derived boundary"
            checked += 1
    assert checked, "no ruled band was exercised"
```

- [ ] **Step 3: Run to verify the red**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_confirmed_refinement.py -q`
Expected: `test_aligned_space_counter_example_compiles_as_on_main` **FAILS with a raised `AssertionError`** from inside `compile_tables` (the cherry-picked attempt-1 wiring asserts the phantom split — this is the crash, reproduced as the red). The seam test fails with `ImportError: cannot import name '_build_ruled_band'`.

- [ ] **Step 4: Extract the seam and wire confirmation in `src/iladub/etkl/compile.py`**

**4a.** Add this module-level function (above `compile_tables`):

```python
def _build_ruled_band(sub, sub_rules, sub_hrules, page_chars):
    """Construct the Band for a RULED sub-band. THE SEAM for the no-synthesised-Rule guard:
    tests call this directly, so the guard exercises production code, not a copy (attempt 1's
    guard replicated this logic in its test body and was proven tautological).

    Flow — every refusal exits to the author-bucketed band, i.e. main's behavior:
      author-bucketed lines -> candidate boundaries (geometry.refine_rule_columns) ->
      provisional grid + header/body split (locates the header region; computed on the
      AUTHOR-bucketed band so confirmation never depends on the candidates it judges) ->
      header-CONFIRMED boundaries (boundary.confirmed_boundaries, the confirm-boundary.rq AXIOM)
      -> re-bucket with author+confirmed and set Band.column_xs.

    sub_rules passes through UNTOUCHED — no Rule is ever synthesised; derived boundaries live
    only in Band.column_xs (the author's marks and the derived list are kept distinct on
    purpose). A single-row band has no header/body split, so nothing is ever confirmable there
    (closes attempt 1's single-row over-split structurally)."""
    from dataclasses import replace as _replace
    from .bands import Band
    from .geometry import refine_rule_columns, rule_aware_lines

    xs = sorted({round(r.x, 2) for r in sub_rules})
    band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
    relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []
    if not relines:
        return _replace(sub, rules=sub_rules, hrules=sub_hrules)
    band = Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules)

    candidates = [x for x in refine_rule_columns(band_chars, xs) if x not in xs]
    if not candidates:
        return band
    from .cells import recover_leaf_grid
    from .headers import header_body_split
    try:
        grid = recover_leaf_grid(band)
    except ValueError:
        return band
    if grid.ncols < 2:
        return band
    split = header_body_split(band, grid)
    if split is None or not (1 <= split < len(band.lines)):
        return band                        # no header region -> nothing can be confirmed
    body_top = band.lines[split].top
    header_glyphs = [c for c in band_chars
                     if c.text.strip() and (c.top + c.bottom) / 2.0 < body_top]
    from .boundary import confirmed_boundaries
    triples = []
    for bx in candidates:
        lo = max(x for x in xs if x < bx)
        hi = min(x for x in xs if x > bx)
        triples.append((bx, lo, hi))
    confirmed = confirmed_boundaries(header_glyphs, triples)
    if not confirmed:
        return band
    col_xs = sorted(set(xs) | confirmed)
    relines2 = rule_aware_lines(band_chars, col_xs)
    if not relines2:
        return band
    return Band(tuple(relines2), sub.top, sub.bottom, sub_rules, sub_hrules, tuple(col_xs))
```

**4b.** In `compile_tables`, replace the cherry-picked ruled branch:

```python
            xs = sorted({round(r.x, 2) for r in sub_rules})
            band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
            # The author's rules are authoritative but not COMPLETE: refine them with any interior
            # gutter they left out, then use the refined list for BOTH cell bucketing and the grid.
            # sub_rules is passed through unchanged — no Rule is ever synthesised.
            col_xs = refine_rule_columns(band_chars, xs) if len(xs) >= 2 else xs
            relines = rule_aware_lines(band_chars, col_xs) if len(col_xs) >= 2 else []
            if relines:
                bands.append(_Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules,
                                   tuple(col_xs)))
            else:
                bands.append(_replace(sub, rules=sub_rules, hrules=sub_hrules))
```

with:

```python
            bands.append(_build_ruled_band(sub, sub_rules, sub_hrules, page_chars))
```

(If the cherry-picked block differs cosmetically, replace the whole `if not sub_rules: … else …` ruled arm's body accordingly — the unruled `continue` arm above it is unchanged. Remove the now-unused `refine_rule_columns` import from `compile_tables`' import line if it becomes unused.)

**4c.** In `tests/etkl/test_rule_column_refinement.py`, **delete** `test_no_rule_is_ever_synthesised_for_a_derived_boundary` (and its now-unused imports, if any). Commit message must state it is replaced by the strictly stronger seam test — the deleted one replicated production code in its body and was proven tautological by the attempt-1 final review.

- [ ] **Step 5: Run to verify green**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_confirmed_refinement.py tests/etkl/test_rule_column_refinement.py tests/etkl/test_boundary_confirmation.py -q`
Expected: **18 passed** (2 + 9 + 7).

- [ ] **Step 6: Targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_border_grid.py tests/etkl/test_rule_grid_authority.py tests/etkl/test_grid.py tests/etkl/test_cells.py tests/etkl/test_geometry.py tests/etkl/test_padding_space_segmentation.py tests/etkl/test_hrule_split.py -q`
Expected: all pass — both shipped ruled fixtures byte-identical (their candidates are all rejected: one-sided or straddled), borderless untouched.

- [ ] **Step 7: Commit**

```bash
git add tests/etkl/fixtures.py tests/etkl/test_header_confirmed_refinement.py tests/etkl/test_rule_column_refinement.py src/iladub/etkl/compile.py
git commit -m "feat(etkl): candidates become columns only when the header confirms them (loop G attempt 2)

The aligned-space counter-example that crashed attempt 1 now compiles in
parity with main (RECORD_TABLE, 18 cells, score 1.0) and is committed as the
permanent red test. Replaces attempt 1's tautological no-synthesised-Rule
guard with a seam test against the production band builder — a strict
strengthening, per the attempt-1 final review's C2 finding."
```

---

### Task 4: The membrane backstop

**Files:**
- Modify: `src/iladub/etkl/compile.py` (the plain hierarchical assert branch only)
- Test: `tests/etkl/test_header_confirmed_refinement.py` (extend)

**Interfaces:**
- Consumes: existing `tiling.region_tiles`, `holon.assert_hier_region`, `holon.escalate_region`.
- Produces: no new API — the plain hierarchical path now escalates `"REGION_TILING_FAILED"` in-band instead of crashing at final validation.

- [ ] **Step 1: Write the failing test**

Append to `tests/etkl/test_header_confirmed_refinement.py`:

```python
def test_defective_hierarchical_region_escalates_in_band_not_crash(tmp_path, monkeypatch):
    """THE CRASH CLASS, closed at the membrane. The plain hierarchical branch was the last
    region path writing directly into the graph — which is why attempt 1's phantom column
    CRASHED compile_tables at final SHACL validation instead of escalating.

    Sabotage (probe-verified deterministic): blanking the last leaf node's covers passes
    merge_tiling_ok (True — it checks overlap/centering, not coverage), asserts n=10, and fails
    region_tiles (False, tab:CoverageShape). Before the backstop this test dies with an
    AssertionError from compile_tables; after, it escalates in-band."""
    from dataclasses import replace

    from iladub.etkl import hierarchical as H

    p = os.path.join(str(tmp_path), "pm.pdf")
    F.partial_merge_report_pdf(p)
    real = H.classify_hierarchical

    def sabotaged(band):
        hreg = real(band)
        if hreg is None:
            return None
        max_lvl = max(n.level for n in hreg.tree)
        leafs = [i for i, n in enumerate(hreg.tree) if n.covers and n.level == max_lvl]
        tree = list(hreg.tree)
        tree[leafs[-1]] = replace(tree[leafs[-1]], covers=())
        return replace(hreg, tree=tuple(tree))

    monkeypatch.setattr(H, "classify_hierarchical", sabotaged)
    rep = compile_tables(p)                                    # must NOT raise
    reasons = [r.reason for r in rep.regions]
    assert "REGION_TILING_FAILED" in reasons, reasons
```

- [ ] **Step 2: Run to verify the red**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_confirmed_refinement.py::test_defective_hierarchical_region_escalates_in_band_not_crash -q`
Expected: **FAILS with a raised `AssertionError`** from inside `compile_tables` (final `_validate` on the whole graph — the crash class, live).

- [ ] **Step 3: Gate the plain hierarchical assert**

In `src/iladub/etkl/compile.py`, replace:

```python
                elif hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    n = assert_hier_region(graph, hreg, band, table_uri, _DOC, page_number)
                    tokens = sum(len(ln.words) for ln in band.lines)
                    asserted_total += n
                    escalated_total += max(0, tokens - n)
                    reports.append(RegionReport(
                        region.kind,
                        "asserted" if n else "escalated",
                        n,
                        None if n else "ROUND_TRIP_FAIL",
                        str(TAB.HierarchicalTable),
                        ascii_view,
                    ))
```

with:

```python
                elif hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    # THE MEMBRANE BACKSTOP (loop G attempt 2): assert into a SCRATCH graph and
                    # let region_tiles dispose it, exactly as the matrix and row-hier paths
                    # already do. This was the last region path that wrote directly into the
                    # graph — which is why a defective region here CRASHED compile_tables at
                    # final validation (attempt 1's counter-example) instead of escalating.
                    from .tiling import region_tiles
                    scratch = Graph()
                    n = assert_hier_region(scratch, hreg, band, table_uri, _DOC, page_number)
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view,
                                        "REGION_TILING_FAILED", TAB.HierarchicalTable, 0.4)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.HierarchicalTable), ascii_view))
                    else:
                        # n == 0 keeps main's behavior byte-identical: assert_hier_region already
                        # wrote its ROUND_TRIP_FAIL escalation into scratch; merge and report as
                        # before. A tiling region merges exactly as it always did.
                        graph += scratch
                        tokens = sum(len(ln.words) for ln in band.lines)
                        asserted_total += n
                        escalated_total += max(0, tokens - n)
                        reports.append(RegionReport(
                            region.kind,
                            "asserted" if n else "escalated",
                            n,
                            None if n else "ROUND_TRIP_FAIL",
                            str(TAB.HierarchicalTable),
                            ascii_view,
                        ))
```

(`Graph` is already imported at the top of `compile.py`.) Safety argument for zero regression, to carry into the commit message: `region_tiles`' nine shapes are a subset of the final full-shape validation, so any region that passes today's final validate necessarily passes the new gate — no currently-asserting fixture can flip.

- [ ] **Step 4: Run to verify green + targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_confirmed_refinement.py tests/etkl/test_hier_holon.py tests/etkl/test_hierarchical.py tests/etkl/test_hier_escalation.py tests/etkl/test_rowrole_integration.py tests/etkl/test_b1_3_merge_resolution.py tests/etkl/test_closing_slice.py -q`
Expected: all pass (3 in the new file; the hierarchical/span/rowrole paths unchanged).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_header_confirmed_refinement.py
git commit -m "fix(etkl): gate the plain hierarchical assert behind region_tiles (loop G attempt 2)

The last region path that wrote directly into the graph now escalates
REGION_TILING_FAILED in-band instead of crashing compile_tables at final
validation. Zero-regression by construction: region_tiles' shapes are a
subset of the final validation, so any region passing today's compile passes
the gate."
```

---

### Task 5: Verification + residue register

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md` (status line)

- [ ] **Step 1: Full suite (the one run this loop)**

Run (timeout 400000, foreground): `. .venv/bin/activate && python3 -m pytest -q`
Expected: **628 passed, 5 skipped** (609 baseline + 10 carried − 1 replaced + 7 AXIOM + 2 Task 3 + 1 Task 4). Report the real numbers; investigate any difference.

- [ ] **Step 2: GrainCorp confirmation (LOCAL, uncommitted)**

Verify the PDF exists at
`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf`.
If missing, say so and skip — it is a confirmation, not a gate. **Never copy or commit it.**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from rdflib import Namespace
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
TAB = Namespace('https://w3id.org/iladub/tab#')
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop = RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption + two wrapped rows')
r = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for reg in r.regions:
    if reg.verdict == 'asserted': print(reg.kind, reg.verdict, 'cells=', reg.cells)
print('score=', round(r.score, 4))
lbl = [str(o) for s,_pp,o in r.graph.triples((None, TAB.cellText, None)) if 'hl' in str(s)]
print('header labels =', len(lbl))
for l in sorted(lbl): print('   ', l)
"
```

Expected, and **report what you actually observe**:
- **`header labels = 17`** with `Date Loading Completed`, `Commodity`, `Total` as three separate labels — **this is the discriminating criterion** (attempt 1 measured cells/score identical at the broken 15-label and correct 17-label states, so those numbers cannot stand in for it).
- Secondary: `cells = 509`, `score = 0.9496`.
- If labels ≠ 17, the confirmation did not reach the grid or refused the real boundaries — investigate (first suspect per attempt 1: a boundary-bearing field dropped somewhere between `Band` and a sub-band); do not report success on cells/score alone.

- [ ] **Step 3: Update the residue register**

In `docs/superpowers/residues.md`:
- **R13** — closed for ruled documents whose missing boundaries the header labels (attempt 2, header-confirmed). Keep one narrower open form: a genuinely unlabeled sub-column (header ink one side only, yet truly two columns) is indistinguishable from the counter-example **by construction** and stays merged — honest, since asserting it would be attempt 1's defect. Reference the "attempt 1" post-mortem section as resolved by attempt 2, and leave that section in place as history.
- **R1** — closed with R13.
- **R4** — one blocker removed (clean numeric `Total` column restored); still blocked on the row de-fusion (`logical_rows`).
- Add a row: **the plain-hierarchical crash class is closed** — note under R13's entry or as a line in the attempt-1 section that the membrane backstop (`REGION_TILING_FAILED`) now guards every region path.

- [ ] **Step 4: Update the spec status line**

Append the measured outcome to the `**Status:**` line, using **your** numbers, stating any difference from the plan explicitly.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md
git commit -m "docs: loop G attempt 2 measured outcome; R13 and R1 closed for the ruled path"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1.1 candidate generation (cherry-picked, demoted to proposer) | Task 1 |
| §1.2 confirmation AXIOM (vocab, query, `boundary.py`) | Task 2 |
| §1.3 attempt-1 plumbing carried | Task 1 |
| §1.4 membrane backstop | Task 4 |
| §1.5 post-mortem debts: C2 seam | Task 3 (seam test + tautology removal) |
| §1.5 post-mortem debts: I1 docstring, I3 discontinuity | Task 1 Step 3 |
| §1 success 1 (red-test parity) | Task 3 Steps 2–5 |
| §1 success 2 (17 labels primary; cells/score secondary) | Task 5 Step 2, with the non-discrimination warning restated |
| §1 success 3 (escalate in-band, never raise) | Task 4 |
| §1 success 4 (every refusal → `main` behavior) | `_build_ruled_band`'s early exits (Task 3) + Task 4's else-branch byte-parity |
| §1 success 5 (no regression) | Task 3 Step 6, Task 4 Step 4, Task 5 Step 1 |
| §1 success 6 (gate: no literal in the rq; inherited constants stated) | Task 2 Steps 5+8, Task 1 Step 3 |
| §2 Findings 1–5 | Encoded in probed values + the tests' measured coordinates |
| §3.1–3.4 components | Tasks 1–4 respectively |
| §4 testing bullets | red fixture (T3), confirmation units (T2), gate (T2 S8), membrane (T4), seam (T3), carried (T1), regression (T3 S6/T4 S4), real-world (T5) |
| §5 gate & discipline | Global Constraints |
| §6 residues | Task 5 Step 3 |

**Deviation from spec, declared:** §3.2 mentions a derived marker `tab:confirmedBoundary`; the implementation returns confirmed boundaries as SELECT bindings instead, exactly as the shipped `header-covers.rq` does (the binding *is* the derivation product; no marker triple is written). Task 5 Step 4's status update should note this as a faithful-to-precedent simplification.

**Placeholder scan:** none — every step carries complete, copy-ready code with exact expected output. Task 3 Step 4b carries an explicit instruction for cosmetic drift in the cherry-picked block rather than assuming byte-exactness.

**Type consistency:**
- `confirmed_boundaries(header_glyphs, candidates) -> set[float]`: Task 2's tests pass `_G` objects (`.x0`/`.x1`) and 3-tuples; Task 3's `_build_ruled_band` passes `Char` objects (which expose `.x0`/`.x1`) and 3-tuples. Consistent — the runner reads only `.x0`/`.x1`.
- `_build_ruled_band(sub, sub_rules, sub_hrules, page_chars) -> Band`: called in `compile_tables` with `(sub, sub_rules, sub_hrules, page_chars)` and in the seam test with `(sub, sub_rules, (), page_chars)` — `sub_hrules` accepts any tuple, `()` is valid.
- `Band(lines, top, bottom, rules, hrules, column_xs)` — six-field construction matches the cherry-picked dataclass; refusal paths return five-field constructions (default `column_xs=()`), identical to `main`'s shape.
- Float identity `x not in xs` in `_build_ruled_band`: safe because `refine_rule_columns` returns the input boundaries verbatim (same rounded floats) plus centres rounded to 2 dp — probed in attempt 1.
- `rep.score == 1.0` exact float compare: score is `asserted/(asserted+escalated)` with `escalated == 0` → exactly `1.0` (matches `main`'s measured output).
