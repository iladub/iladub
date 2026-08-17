# Refining coarse rules with interior gutters Implementation Plan

**EXECUTED AND LANDED — salvaged onto `main` 2026-08-17 from the parked `iladub-rule-column-refinement` branch.** All three tasks shipped (`9427137`, `1425d90`, `4ddfdc3`); R13 is closed in `residues-closed.md`. **The unticked `- [ ]` boxes below are done** — they record the plan as written, not outstanding work. See the design doc for how `main` has since moved past it.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop compiling three real columns as one. The author's vertical rules are authoritative but not *complete* — where a rule interval contains a persistent blank run with ink on both sides, that run is an additional column boundary.

**Architecture:** A new pure function `geometry.refine_rule_columns` derives the extra boundaries from char-level ink. `compile.py` calls it once per ruled band and uses the result for two things: `rule_aware_lines` bucketing, and a new derived `Band.column_xs` field. `grid._rule_boundaries` prefers `column_xs` when present. `Band.rules` keeps its meaning — the marks the author actually drew — so no synthesised `Rule` is ever constructed.

**Tech Stack:** Python 3 (`src/iladub/etkl/`), numpy, pytest.

**Spec:** `docs/superpowers/specs/2026-07-30-rule-column-refinement-design.md` — read §2 Finding 3, which is why the interior condition exists.

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from the repo root, `/Volumes/WD Green/dev/git/iladub`.

**Pace:** **targeted** tests per task; the full suite runs **once**, in Task 3. It takes ~165s and exceeds the default 120s tool timeout — set the Bash tool's `timeout` to `400000` ms and run it in the FOREGROUND. Never background a command.

**Baseline:** 609 passed, 5 skipped (`main` at `181ccdc`). Branch `iladub-rule-column-refinement` is already checked out.

## Global Constraints

- **The interior condition is load-bearing — do not drop it.** A blank run counts only if there is ink on **both** sides of it *within the same rule interval*. Measured: without it, `ruled_tight_table_pdf` gains a boundary in **every** interval (5 columns → 10) because short left-aligned text leaves a blank run at each cell's trailing edge. With it, both ruled fixtures gain **zero**.
- **Additive only.** Refinement may only *add* boundaries inside an interval. It must never remove, move, or reorder a boundary the author drew.
- **Never synthesise a `Rule`.** `Band.rules` is what the author drew; derived boundaries go in the new `Band.column_xs`. Loop D's review rejected fake `Rule` objects and this exists to honour that.
- **Inherited constants, not new ones.** Reuse `gutter_pct = 0.98` and `min_gutter_bins = 3`, matching `infer_leaf_grid`'s existing defaults. Do **not** invent a new threshold, and do **not** tune these — the spec states plainly that this path inherits them.
- **`Band` is a frozen dataclass** — the new field must have a default so every existing construction site keeps working.
- **Never weaken an existing test.**
- **No third-party PDF committed.**

---

## File Structure

| File | Responsibility |
| --- | --- |
| `src/iladub/etkl/geometry.py` | **Modify** — add `refine_rule_columns`. No other function changes. |
| `src/iladub/etkl/bands.py` | **Modify** — `Band` gains `column_xs: tuple[float, ...] = ()`. |
| `src/iladub/etkl/grid.py` | **Modify** — `_rule_boundaries` prefers `band.column_xs`. |
| `src/iladub/etkl/compile.py` | **Modify** — call the refinement; feed both consumers. |
| `tests/etkl/test_rule_column_refinement.py` | **Create** — the refinement's behaviour + the no-synthesised-Rule guard. |

Task order: 1 → 2 → 3. Task 2 consumes Task 1's function.

---

## Probed values (measured while planning — assert, do not re-derive)

**The unit fixtures**, probed against a candidate implementation. Rule interval `[100.0, 200.0]`, four rows:

| rows contain | result |
| --- | --- |
| ink at 105–140 **and** 160–195 (interior gutter) | `[100.0, 150.0, 200.0]` — boundary added |
| ink at 105–140 only (trailing padding) | `[100.0, 200.0]` — **no** boundary |
| ink at 160–195 only (leading padding) | `[100.0, 200.0]` — **no** boundary |
| 3 rows full 105–195, 1 row gapped (not persistent) | `[100.0, 200.0]` — **no** boundary |
| no chars at all | `[100.0, 200.0]` |

**The real document.** Interval `[715.2, 829.92]`, 54 inked rows → blank runs at `744.2–763.2` and `789.2–808.2` (19 bins each) → boundaries **753.7** and **798.7**. Shipped fixtures gain **0** boundaries.

**End-to-end:** grid 15 → **17** columns; 17 correct header labels including `Date Loading Completed`, `Commodity`, `Total` as separate labels; **cells 447 → 509**, **score 0.947 → 0.9496**.

---

### Task 1: `refine_rule_columns`

**Files:**
- Modify: `src/iladub/etkl/geometry.py` (add one function; nothing else changes)
- Test: `tests/etkl/test_rule_column_refinement.py` (create)

**Interfaces:**
- Consumes: `geometry.Char`.
- Produces: `geometry.refine_rule_columns(chars: list[Char], rule_xs: list[float]) -> list[float]` — the input boundaries plus any interior-gutter centres, sorted and de-duplicated.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rule_column_refinement.py`:

```python
"""Loop G — the author's rules are authoritative but not COMPLETE (residue R13).

An author may rule some column boundaries and leave others to whitespace. GrainCorp's measure
column holds 'Date Loading Completed | Commodity | Total' with no interior rule, so three real
columns compiled as one at confidence 1.0.

A persistent blank run inside a rule interval is an extra boundary — but ONLY if there is ink on
BOTH sides of it within that interval. Measured: without that condition the naive rule adds a
boundary to EVERY interval of ruled_tight_table_pdf (5 columns become 10), because short
left-aligned text leaves a blank run at each cell's trailing edge.
See docs/superpowers/specs/2026-07-30-rule-column-refinement-design.md §2 Finding 3.
"""
from iladub.etkl.geometry import Char, refine_rule_columns

RULES = [100.0, 200.0]


def _c(x0, x1, top):
    return Char("X", x0, x1, top, top + 8.0)


def _rows(spans, n=4):
    """n rows, each carrying ink over every (x0, x1) span given."""
    return [_c(a, b, 10.0 * r) for r in range(n) for (a, b) in spans]


def test_an_interior_gutter_adds_a_boundary():
    # Ink on BOTH sides of the blank run -> a real separator the author did not rule.
    assert refine_rule_columns(_rows([(105, 140), (160, 195)]), RULES) == [100.0, 150.0, 200.0]


def test_trailing_padding_does_not_add_a_boundary():
    # THE CASE THAT KILLS THE NAIVE RULE. Short left-aligned text leaves the interval's right
    # side blank; there is no ink to the right of the run, so it is padding, not a separator.
    assert refine_rule_columns(_rows([(105, 140)]), RULES) == [100.0, 200.0]


def test_leading_padding_does_not_add_a_boundary():
    # The mirror case: right-aligned text, no ink to the LEFT of the run.
    assert refine_rule_columns(_rows([(160, 195)]), RULES) == [100.0, 200.0]


def test_a_gutter_must_be_persistent():
    # One gapped row among four is not a column separator.
    chars = _rows([(105, 195)], 3) + [_c(105, 140, 30.0), _c(160, 195, 30.0)]
    assert refine_rule_columns(chars, RULES) == [100.0, 200.0]


def test_no_chars_leaves_the_boundaries_alone():
    assert refine_rule_columns([], RULES) == [100.0, 200.0]


def test_refinement_is_additive():
    # Every author-drawn boundary survives, in order — refinement only ADDS.
    rules = [100.0, 200.0, 300.0]
    out = refine_rule_columns(_rows([(105, 140), (160, 195)]) + _rows([(205, 295)]), rules)
    assert set(rules) <= set(out)
    assert out == sorted(out)


def test_space_glyphs_are_not_ink():
    # A cell padded with space glyphs must still read as blank there.
    chars = _rows([(105, 140), (160, 195)]) + [Char(" ", 141.0, 159.0, 0.0, 8.0)]
    assert refine_rule_columns(chars, RULES) == [100.0, 150.0, 200.0]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: **collection error** — `ImportError: cannot import name 'refine_rule_columns' from 'iladub.etkl.geometry'`.

- [ ] **Step 3: Add the function to `src/iladub/etkl/geometry.py`**

Insert immediately above `def rule_aware_lines(`. **`numpy` is NOT currently imported in this module** (verified while planning — `geometry.py` imports only `dataclass`, `median` and `pdfplumber`). Add `import numpy as np` alongside `import pdfplumber` first.

```python
def refine_rule_columns(chars: list["Char"], rule_xs: list[float],
                        gutter_pct: float = 0.98, min_gutter_bins: int = 3) -> list[float]:
    """The author's rule boundaries, plus any column boundary the rules LEFT OUT.

    Rules are authoritative but not COMPLETE: an author may rule some boundaries and leave others
    to whitespace. Inside each rule interval, a run of x-bins that is blank on >= gutter_pct of the
    interval's inked rows, at least min_gutter_bins wide, AND with ink on BOTH sides of it within
    that interval, is an additional column boundary (its centre).

    THE INTERIOR CONDITION IS LOAD-BEARING — do not drop it. Without it, a blank run at a cell's
    trailing edge (short left-aligned text) reads as a separator: measured, that adds a boundary to
    EVERY interval of ruled_tight_table_pdf, turning 5 columns into 10. With it, both shipped ruled
    fixtures gain ZERO and the real document gains exactly the two it should. It is a presence test
    ("is there ink beyond this run, inside this interval"), not a threshold.

    ADDITIVE ONLY: every input boundary is preserved; nothing is moved or removed. The author's
    marks are never contradicted, only supplemented. Callers keep the raw marks in Band.rules and
    put this function's output in Band.column_xs, so provenance stays honest.

    gutter_pct and min_gutter_bins mirror infer_leaf_grid's existing defaults — pre-existing tuned
    constants this path INHERITS rather than invents. Space glyphs are not ink.
    """
    xs = sorted(rule_xs)
    if len(xs) < 2:
        return xs
    ink = [c for c in chars if c.text.strip()]
    out = [xs[0]]
    for i in range(len(xs) - 1):
        lo, hi = xs[i], xs[i + 1]
        nbins = int(np.ceil(hi - lo))
        seg = [c for c in ink if lo <= (c.x0 + c.x1) / 2.0 < hi]
        if seg and nbins >= min_gutter_bins:
            rows = sorted({round(c.top, 1) for c in seg})
            row_of = {t: k for k, t in enumerate(rows)}
            grid = np.zeros((len(rows), nbins), dtype=bool)
            for c in seg:
                a = int(c.x0 - lo)
                b = int(np.ceil(c.x1 - lo))
                grid[row_of[round(c.top, 1)], max(0, a):min(nbins, b)] = True
            blank = 1.0 - grid.mean(axis=0)
            any_ink = grid.any(axis=0)
            run = None
            for k, frac in enumerate(blank):
                if frac >= gutter_pct:
                    run = k if run is None else run
                    continue
                if (run is not None and k - run >= min_gutter_bins
                        and any_ink[:run].any() and any_ink[k:].any()):
                    out.append(round(lo + (run + k) / 2.0, 2))
                run = None
            # a run still open at the interval's end has no ink to its right -> never interior
        out.append(hi)
    return sorted(set(out))
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: **7 passed.**

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/test_rule_column_refinement.py
git commit -m "feat(etkl): refine_rule_columns — an interior gutter is a boundary the rules left out (loop G)"
```

---

### Task 2: Wire it in — `Band.column_xs`, `compile.py`, `_rule_boundaries`

**Files:**
- Modify: `src/iladub/etkl/bands.py` (the `Band` dataclass)
- Modify: `src/iladub/etkl/grid.py` (`_rule_boundaries`, the `xs = …` line only)
- Modify: `src/iladub/etkl/compile.py` (the ruled branch)
- Test: `tests/etkl/test_rule_column_refinement.py` (extend)

**Interfaces:**
- Consumes: `geometry.refine_rule_columns(chars, rule_xs) -> list[float]` (Task 1).
- Produces: `Band.column_xs: tuple[float, ...] = ()` — derived column boundaries, distinct from `Band.rules` (author-drawn). `_rule_boundaries` prefers it when non-empty.

- [ ] **Step 1: Write the failing test**

Append to `tests/etkl/test_rule_column_refinement.py`:

```python
def test_no_rule_is_ever_synthesised_for_a_derived_boundary(tmp_path):
    """Provenance stays honest: Band.rules is what the AUTHOR drew, Band.column_xs is derived.

    Loop D's review rejected synthesising fake Rule objects for derived boundaries. There is no
    band-level seam on compile_tables, so this replicates its ruled-band construction (the same
    dozen lines) and asserts directly that every Rule x was drawn in the document.
    """
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.bands import Band, detect_bands
    from iladub.etkl.geometry import (extract_chars, extract_rules, extract_words,
                                      rule_aware_lines, text_lines)
    from iladub.etkl.segment import segment
    from tests.etkl import fixtures as F

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
            xs = sorted({round(r.x, 2) for r in sub_rules})
            band_chars = [c for c in page_chars
                          if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
            col_xs = refine_rule_columns(band_chars, xs)
            relines = rule_aware_lines(band_chars, col_xs)
            if not relines:
                continue
            b = Band(tuple(relines), sub.top, sub.bottom, sub_rules, (), tuple(col_xs))
            for r in b.rules:
                assert round(r.x, 2) in authored, "a Rule was synthesised for a derived boundary"
            assert set(xs) <= set(b.column_xs), "derived list must preserve every author boundary"
            checked += 1
    assert checked, "no ruled band was exercised"


def test_rule_boundaries_prefers_the_derived_list():
    """_rule_boundaries must use Band.column_xs when present, so the refinement reaches the grid."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Rule, Word
    from iladub.etkl.grid import _rule_boundaries

    def _w(t, x0, x1, top):
        return Word(t, x0, x1, top, top + 8.0)

    rows = tuple(Line((_w("a", 105, 140, 10.0 * r), _w("b", 160, 195, 10.0 * r)),
                      10.0 * r, 10.0 * r + 8.0) for r in range(4))
    author = (Rule(100.0, 0, 50), Rule(200.0, 0, 50))

    coarse = Band(rows, 0.0, 40.0, author)
    assert _rule_boundaries(coarse) is None, "2 boundaries = no interior separator (Loop D guard)"

    refined = Band(rows, 0.0, 40.0, author, (), (100.0, 150.0, 200.0))
    assert _rule_boundaries(refined) == [100.0, 150.0, 200.0]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: `test_rule_boundaries_prefers_the_derived_list` **FAILS** with `TypeError: Band.__init__() takes from 4 to 6 positional arguments but 7 were given` — `column_xs` does not exist yet.

- [ ] **Step 3: Add the field to `src/iladub/etkl/bands.py`**

```python
@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float
    rules: tuple[Rule, ...] = ()
    hrules: tuple[HRule, ...] = ()
    column_xs: tuple[float, ...] = ()
```

Add a comment above `column_xs`: derived column boundaries (author rules **plus** interior gutters the rules left out — see `geometry.refine_rule_columns`). `rules` stays what the author drew; keeping them separate is deliberate, so a derived boundary is never mistaken for a mark in the document.

- [ ] **Step 4: Prefer it in `src/iladub/etkl/grid.py`**

In `_rule_boundaries`, replace

```python
    xs = sorted({round(r.x, 2) for r in band.rules})
```

with

```python
    # Prefer the DERIVED boundaries (author rules + interior gutters the rules left out) when the
    # caller supplied them; fall back to the raw author marks. Band.rules is never synthesised.
    xs = (sorted(band.column_xs) if band.column_xs
          else sorted({round(r.x, 2) for r in band.rules}))
```

Leave the `if not band.rules: return None` guard above it exactly as it is — a band with derived boundaries but no author rules is not a ruled band.

- [ ] **Step 5: Wire `src/iladub/etkl/compile.py`**

In the ruled branch, replace

```python
            xs = sorted({round(r.x, 2) for r in sub_rules})
            band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
            relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []
            if relines:
                bands.append(_Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules))
```

with

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
```

Add `refine_rule_columns` to the existing `from .geometry import …` line at the top of `compile_tables` (it already imports `rule_aware_lines` from there).

- [ ] **Step 6: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_column_refinement.py -q`
Expected: **9 passed.**

- [ ] **Step 7: Targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_border_grid.py tests/etkl/test_rule_grid_authority.py tests/etkl/test_grid.py tests/etkl/test_cells.py tests/etkl/test_geometry.py tests/etkl/test_padding_space_segmentation.py -q`
Expected: all pass. These exercise the ruled path. A failure means the refinement changed a shipped ruled fixture's grid — investigate; **do not adjust a test**. Measured expectation: both ruled fixtures gain **zero** boundaries.

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/bands.py src/iladub/etkl/grid.py src/iladub/etkl/compile.py tests/etkl/test_rule_column_refinement.py
git commit -m "feat(etkl): carry derived column boundaries on the Band and prefer them in the grid (loop G)"
```

---

### Task 3: Verification + residue register

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/superpowers/specs/2026-07-30-rule-column-refinement-design.md` (status line)

**Interfaces:** none — verification and documentation only.

- [ ] **Step 1: Full suite (the one run this loop)**

Run (timeout 400000, foreground): `. .venv/bin/activate && python3 -m pytest -q`
Expected: **618 passed, 5 skipped** (609 baseline + 9 new). Report the real numbers.

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
- `cells = 509` and `score = 0.9496`. **This loop SHOULD move the score** (447/0.947 before) because the merged blob now yields three cells per row. A *different* number — including an unchanged one — is a failure signal in either direction; investigate rather than accept it.
- `header labels = 17`, with `Date Loading Completed`, `Commodity` and `Total` as **three separate labels**.

- [ ] **Step 3: Update the residue register**

In `docs/superpowers/residues.md`:
- **R13** — mark closed for the ruled path with interior evidence. Note the one narrower form still open: an interval whose sub-columns are separated by **neither** a rule **nor** a persistent gutter (e.g. a single-row table). No measured document exhibits it.
- **R1** — mark closed with R13; it was the same defect.
- **R4** — record that **one of its two blockers is now removed** (a clean numeric `Total` column exists). It remains blocked on the row de-fusion: `logical_rows` absorbs each subtotal line into the preceding data row.

- [ ] **Step 4: Update the spec status line**

Append the measured outcome to the `**Status:**` line of the spec, using **your** numbers, and state any difference from the plan explicitly.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-30-rule-column-refinement-design.md
git commit -m "docs: loop G measured outcome; R13 and R1 closed for the ruled path"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1/§3.1 `refine_rule_columns` | Task 1 |
| §1/§3.2 `Band.column_xs` | Task 2 Step 3 |
| §1/§3.3 `compile.py` wiring | Task 2 Step 5 |
| §1/§3.4 `_rule_boundaries` prefers derived | Task 2 Step 4 |
| §1 success 1 (15→17, three labels separate) | Task 3 Step 2 |
| §1 success 2 (**score moves to 509 / 0.9496**) | Task 3 Step 2, stated as a two-sided failure condition |
| §1 success 3 (no over-splitting) | Task 1 `test_trailing_padding_…`, `test_leading_padding_…`; Task 2 Step 7 |
| §1 success 4 (no regression) | Task 2 Step 7, Task 3 Step 1 |
| §1 success 5 (no synthesised `Rule`) | Task 2 `test_no_rule_is_ever_synthesised_for_a_derived_boundary` |
| §2 Findings 1–4 | Probed-values section + the fixtures |
| §4 all seven test bullets | Task 1 Step 1 (seven) + Task 2 Step 1 (two) + Step 7 + Task 3 Step 2 |
| §5 gate (incl. inherited constants) | Global Constraints + the `refine_rule_columns` docstring |
| §6 residues | Task 3 Step 3 |

**Gap found and closed during review:** §5's "additive, never contradicting" had no test — it is now `test_refinement_is_additive`, asserting every author boundary survives and the output stays sorted. Also added `test_space_glyphs_are_not_ink`, since Loop F established that space glyphs are present in these documents and treating them as ink would hide a real gutter.

**Two planning errors caught by self-review and fixed:** the plan first claimed `numpy` was already
imported in `geometry.py` — it is not, so Task 1 Step 3 now says to add it. And the no-synthesised-`Rule`
test relied on a `compile._bands_for_test` seam that does not exist, so its fallback branch would have
fired **every** time, making the test vacuous. It now replicates `compile.py`'s ruled-band construction
and asserts directly, with a `checked` counter so it cannot pass by exercising nothing.

**Placeholder scan:** none. Every step carries complete, copy-ready code and exact expected output. Task 3 Step 2's PDF path has an explicit skip instruction because the file is local-only.

**Type consistency:**
- `refine_rule_columns(chars: list[Char], rule_xs: list[float]) -> list[float]` — called in `compile.py` with `band_chars` (a `list[Char]`) and `xs` (a `list[float]`), result passed to `rule_aware_lines(chars, rule_xs)` whose second parameter is `list[float]`, and to `_Band(..., tuple(col_xs))`.
- `Band.column_xs: tuple[float, ...]` — a **tuple** on the dataclass (frozen/hashable), while `refine_rule_columns` returns a **list**; the conversion happens once, at the `_Band(...)` construction in `compile.py`. Task 2's direct-construction test passes a tuple, matching.
- `_rule_boundaries(band) -> list[float] | None` — signature unchanged; it now sorts either `band.column_xs` or the rule set, both yielding `list[float]`.
- `Char(text, x0, x1, top, bottom)` and `Rule(x, top, bottom)` — verified against `geometry.py`; the `_c`/`_w` helpers match.
