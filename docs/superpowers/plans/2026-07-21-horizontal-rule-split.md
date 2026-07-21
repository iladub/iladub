# Horizontal-Rule Header/Body Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When the type-homogeneity header/body split returns `None` (all-text tables), fall back to the author's horizontal rule under the header — capturing all-text hierarchical tables that escalate at score 0.00 today — while leaving every typed table byte-identical.

**Architecture:** `geometry.extract_hrules` pulls horizontal ruled segments (PROCEDURAL, mirrors `extract_rules`). `Band` gains a defaulted `hrules`; `compile_tables` attaches band-overlapping hrules. `header_body_split` computes the type-based split as today and, ONLY when it is `None`, returns the first line below the topmost interior horizontal rule (≥1 header line and ≥1 body line, else `None`). Downstream `classify_hierarchical` disposes (region forms or escalates).

**Tech Stack:** Python 3, `pdfplumber`, `reportlab` (fixtures), `pytest`.

## Global Constraints

- **Test interpreter (MANDATORY):** every test via `./.venv/bin/python -m pytest …` (rdflib 7.6.0). Bare `python`/`python3`/`pytest` = wrong env. Wherever a step says `pytest …`, run `./.venv/bin/python -m pytest …`.
- **Cannot regress typed tables (the guarantee):** the rule-derived split runs ONLY on the `None` branch of `header_body_split`. When the type split is non-`None`, `header_body_split` returns it unchanged — the hrules are never consulted. A typed table with a horizontal rule present must return the SAME split as today.
- **Purely additive:** no horizontal rules (every shipped borderless fixture) → `header_body_split` and the whole pipeline byte-identical. `Band.hrules` defaults to `()`.
- **§8 gate:** `extract_hrules` (raw extraction) and "first line below the interior rule y" (decidable geometry) are PROCEDURAL with NO tuned DECISION constant. The `1.0`/`2.0`/dedup literals are geometry epsilons. The type-based `header-body-split.rq` AXIOM is UNCHANGED.
- **Conservative:** a wrong/ambiguous horizontal rule must at worst leave the table escalated (downstream region-formation is the oracle), never assert a mis-split.
- **Full suite** via `.venv` at the end; baseline **427 passed / 5 skipped**. Zero regressions.

## File Structure

- **Modify** `src/iladub/etkl/geometry.py` — `HRule` dataclass + `extract_hrules(pdf_path, page_number)`.
- **Modify** `src/iladub/etkl/bands.py` — `Band` gains `hrules: tuple[HRule, ...] = ()`.
- **Modify** `src/iladub/etkl/headers.py` — `header_body_split` rule-fallback + `_hrule_split(band)` helper.
- **Modify** `src/iladub/etkl/compile.py` — extract page hrules; attach band-overlapping hrules.
- **Modify** `tests/etkl/fixtures.py` — `all_text_hier_ruled_pdf(path)` + `all_text_hier_borderless_pdf(path)`.
- **Create** `tests/etkl/test_hrule_split.py` — extraction, split derivation, precedence, end-to-end, additive guard.

Verified facts: `header_body_split(band, grid) -> int|None` (headers.py) runs `header-body-split.rq` via `celltype.run_scalar`. `extract_rules` (vertical) is the pattern to mirror (geometry.py). `Band(lines, top, bottom, rules=())` already has a defaulted `rules` — add `hrules` after it. The validated mechanic: for the failing fixture, an hrule at `y=108` gives split = first line with `top>108` = index 2, and `infer_header_tree`/`logical_rows` then succeed.

---

### Task 1: `extract_hrules` + `HRule` + fixtures

**Files:**
- Modify: `src/iladub/etkl/geometry.py`
- Modify: `tests/etkl/fixtures.py`
- Test: `tests/etkl/test_hrule_split.py`

**Interfaces:**
- Produces: `HRule(y, x0, x1)` frozen; `extract_hrules(pdf_path, page_number=0) -> list[HRule]`; `all_text_hier_ruled_pdf(path)->dict`, `all_text_hier_borderless_pdf(path)->dict`.

- [ ] **Step 1: Add the fixtures**

In `tests/etkl/fixtures.py`:

```python
def _all_text_hier(path, ruled):
    """All-TEXT hierarchical table: 'Contact' spans Email+Phone; text body. `ruled` draws a
    horizontal rule under the header (the only header/body signal, since no column is non-Text)."""
    leaves = [(60.0, 150.0), (170.0, 320.0), (340.0, 470.0)]
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 18.0
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, top, "Name")
    c.drawCentredString((170 + 470) / 2.0, top, "Contact")          # spanning parent (text)
    c.drawString(170, top - 14, "Email")
    c.drawString(340, top - 14, "Phone")
    if ruled:
        c.setLineWidth(0.7)
        c.line(55, top - 18, 480, top - 18)                         # horizontal rule under header
    rows = [("Alice", "alice@x.com", "555-0101"), ("Bob", "bob@y.org", "555-0102"),
            ("Carol", "carol@z.net", "555-0103"), ("Dave", "dave@w.io", "555-0104"),
            ("Eve", "eve@v.co", "555-0105"), ("Frank", "frank@u.dev", "555-0106")]
    c.setFont("Helvetica", 10)
    for i, row in enumerate(rows):
        y = top - 28 - i * rh
        for (l, r), cell in zip(leaves, row):
            c.drawString(l, y, cell)
    c.save()
    return {"n_leaf_cols": 3}


def all_text_hier_ruled_pdf(path: str) -> dict:
    return _all_text_hier(path, ruled=True)


def all_text_hier_borderless_pdf(path: str) -> dict:
    return _all_text_hier(path, ruled=False)
```

- [ ] **Step 2: Write the failing extraction test**

Create `tests/etkl/test_hrule_split.py`:

```python
import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_hrules
from tests.etkl import fixtures as F


def _pdf(fn):
    p = os.path.join(tempfile.mkdtemp(), fn.__name__ + ".pdf")
    return p, fn(p)


def test_extract_hrules_finds_the_under_header_rule():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    hr = extract_hrules(p)
    assert len(hr) >= 1
    # the under-header rule sits in the upper region of the table (near y ~108 in page-top coords)
    assert any(90 < h.y < 130 for h in hr), [round(h.y, 1) for h in hr]


def test_extract_hrules_empty_on_borderless():
    p, _ = _pdf(F.all_text_hier_borderless_pdf)
    assert extract_hrules(p) == []
```

- [ ] **Step 3: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -q`
Expected: FAIL (`ImportError: cannot import name 'extract_hrules'`).

- [ ] **Step 4: Implement `HRule` + `extract_hrules` in `geometry.py`**

```python
@dataclass(frozen=True)
class HRule:
    y: float       # y-position (page-top convention) of a horizontal ruled line
    x0: float      # x-extent
    x1: float


def extract_hrules(pdf_path: str, page_number: int = 0) -> list["HRule"]:
    """Horizontal ruled line segments on a page (author-drawn header/body & row separators).

    PROCEDURAL raw extraction, mirror of extract_rules: a segment is 'horizontal' when its vertical
    span is < 1pt and its horizontal span > 2pt. Vertical rules are handled by extract_rules."""
    out: list[HRule] = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        for seg in list(page.lines) + list(page.edges):
            x0, x1 = float(seg["x0"]), float(seg["x1"])
            top, bottom = float(seg["top"]), float(seg["bottom"])
            if abs(bottom - top) < 1.0 and (x1 - x0) > 2.0:
                out.append(HRule((top + bottom) / 2.0, x0, x1))
    uniq: list[HRule] = []
    for h in sorted(out, key=lambda h: (round(h.y, 1), h.x0)):
        if not any(abs(h.y - u.y) < 0.5 and abs(h.x0 - u.x0) < 1.0 and abs(h.x1 - u.x1) < 1.0 for u in uniq):
            uniq.append(h)
    return uniq
```

- [ ] **Step 5: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -q`
Expected: 2 passed. (If the ruled fixture's y is off, print `[h.y for h in extract_hrules(p)]` and adjust the assertion window to the actual under-header y — do NOT relax the borderless `== []` check.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/fixtures.py tests/etkl/test_hrule_split.py
git commit -m "feat(etkl): extract horizontal ruled lines (HRule + extract_hrules) [hrule-split task 1]"
```

---

### Task 2: `Band.hrules` + rule-derived fallback in `header_body_split`

**Files:**
- Modify: `src/iladub/etkl/bands.py`
- Modify: `src/iladub/etkl/headers.py`
- Test: `tests/etkl/test_hrule_split.py`

**Interfaces:**
- Consumes: `HRule` (Task 1).
- Produces: `Band(..., rules=(), hrules=())`; `header_body_split` rule-aware on the `None` branch; `_hrule_split(band) -> int | None`.

- [ ] **Step 1: Add `hrules` to `Band`**

In `src/iladub/etkl/bands.py`:

```python
from .geometry import Line, Rule, HRule

@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float
    rules: tuple[Rule, ...] = ()
    hrules: tuple[HRule, ...] = ()
```

(Trailing defaulted field — every existing positional `Band(lines, top, bottom)` / `Band(..., rules=...)` construction still works.)

- [ ] **Step 2: Write failing split tests**

Add to `tests/etkl/test_hrule_split.py`:

```python
from iladub.etkl.geometry import extract_words, text_lines, HRule
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.headers import header_body_split
from dataclasses import replace


def _table_band(pdf_path):
    return max(detect_bands(text_lines(extract_words(pdf_path))), key=lambda b: len(b.lines))


def test_hrule_split_used_when_type_split_none():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    band = _table_band(p)
    grid = infer_leaf_grid(band)
    assert header_body_split(band, grid) is None                    # all-text -> type split None
    hr = tuple(h for h in extract_hrules(p) if band.top <= h.y <= band.bottom)
    ruled = replace(band, hrules=hr)
    split = header_body_split(ruled, grid)
    assert split is not None and split >= 1                          # rule gives the split
    # split is the first body line (below the under-header rule): a header line and a body line exist
    assert 0 < split < len(band.lines)


def test_type_split_wins_when_present_even_with_hrule():
    # a NUMERIC table with an hrule: the type split must be returned unchanged (hrule ignored)
    from iladub.etkl.geometry import Word, Line
    def w(t, x0, x1, top): return Word(t, x0, x1, top, top + 8)
    lines = [Line((w("Name", 60, 90, 0), w("Score", 160, 195, 0)), 0, 8),
             Line((w("Alice", 60, 90, 20), w("10", 160, 175, 20)), 20, 28),
             Line((w("Bob", 60, 85, 40), w("20", 160, 175, 40)), 40, 48)]
    band = Band(tuple(lines), 0, 48)
    grid = infer_leaf_grid(band)
    base = header_body_split(band, grid)
    assert base is not None                                          # numeric col -> type split
    ruled = replace(band, hrules=(HRule(y=14.0, x0=55, x1=200),))    # an hrule that would imply split=1 too
    assert header_body_split(ruled, grid) == base                   # UNCHANGED — type split wins
```

- [ ] **Step 3: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -k "hrule_split or type_split_wins" -v`
Expected: FAIL (`test_hrule_split_used_when_type_split_none` — split still `None`).

- [ ] **Step 4: Implement the fallback in `headers.py`**

Add a helper and extend `header_body_split`:

```python
def _hrule_split(band) -> int | None:
    """The header/body split from the topmost INTERIOR horizontal rule: the first line index whose
    top is below that rule, provided >=1 header line and >=1 body line result. None if no interior
    rule qualifies. PROCEDURAL geometry (raw rule + line ordering); no tuned constant."""
    hrules = getattr(band, "hrules", ())
    if not hrules or len(band.lines) < 2:
        return None
    first_top = band.lines[0].top
    last_top = band.lines[-1].top
    interior = sorted(h.y for h in hrules if first_top < h.y < last_top)
    for ry in interior:                                   # topmost interior rule first
        split = next((i for i, ln in enumerate(band.lines) if ln.top > ry), None)
        if split is not None and 1 <= split < len(band.lines):
            return split
    return None
```

In `header_body_split`, replace the final `return`:

```python
    split = celltype.run_scalar(q, g)
    if split is not None:
        return split                       # typed table -> the B2a AXIOM decides (unchanged)
    return _hrule_split(band)              # all-text -> fall back to the author's horizontal rule
```

- [ ] **Step 5: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -q` then `./.venv/bin/python -m pytest tests/etkl/test_headers.py tests/etkl/test_hierarchical.py tests/etkl/test_celltype.py -q`
Expected: all pass. `test_type_split_wins_when_present_even_with_hrule` proves typed tables are untouched; the existing header/hierarchical/celltype suites prove no regression.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/bands.py src/iladub/etkl/headers.py tests/etkl/test_hrule_split.py
git commit -m "feat(etkl): header_body_split falls back to horizontal-rule split when type split is None [task 2]"
```

---

### Task 3: Wire hrules through `compile_tables` + end-to-end capture

**Files:**
- Modify: `src/iladub/etkl/compile.py`
- Test: `tests/etkl/test_hrule_split.py`

**Interfaces:**
- Consumes: `extract_hrules` (Task 1), `Band.hrules` (Task 2).

- [ ] **Step 1: Write the failing end-to-end test**

Add to `tests/etkl/test_hrule_split.py`:

```python
from iladub.etkl import compile_tables


def test_all_text_hier_ruled_is_captured_not_escalated():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    rep = compile_tables(p)
    verdicts = [r.verdict for r in rep.regions if r.verdict in ("asserted", "escalated")]
    assert "asserted" in verdicts, [(str(r.kind).split(".")[-1], r.verdict, r.reason) for r in rep.regions]
    assert rep.score > 0.0, "the all-text hierarchical table should now capture data (was 0.00)"


def test_all_text_hier_borderless_still_escalates():
    # the honest demonstration: without the rule, the type split is None -> escalate (as today)
    p, _ = _pdf(F.all_text_hier_borderless_pdf)
    rep = compile_tables(p)
    assert rep.score == 0.0, "borderless all-text hierarchical has no header/body signal -> escalates"
```

- [ ] **Step 2: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -k "ruled_is_captured" -q`
Expected: FAIL (hrules not attached in compile → type split None → escalate).

- [ ] **Step 3: Wire hrules into `compile_tables`**

In `src/iladub/etkl/compile.py`, alongside the existing vertical-rule attachment, extract and attach hrules. Extend the imports and the band loop:

```python
    from .geometry import extract_rules, extract_chars, rule_aware_lines, extract_hrules
    ...
    page_rules = extract_rules(pdf_path, page_number)
    page_hrules = extract_hrules(pdf_path, page_number)
    page_chars = extract_chars(pdf_path, page_number) if page_rules else []
    ...
    for band in raw_bands:
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules if r.top <= sub.bottom and r.bottom >= sub.top)
            sub_hrules = tuple(h for h in page_hrules if sub.top <= h.y <= sub.bottom)
            # ... (existing vertical-rule / re-extraction branch produces `new_band`) ...
            # attach sub_hrules to whichever Band is appended for this sub:
```

Concretely: after computing `sub_rules`/`sub_hrules`, build the band and attach both. Rework the existing branch so every appended band carries `hrules=sub_hrules`. E.g. replace the `bands.append(...)` calls in that loop so the final Band is `_replace(the_band, hrules=sub_hrules)` when `sub_hrules` is non-empty (and, for the rule-re-extracted `_Band(...)`, pass `hrules=sub_hrules` in its construction). A band with neither rules nor hrules is appended unchanged.

**Read the current `compile_tables` band loop (it has the vertical-rule re-extraction branch from the border-aware-grid loop) and thread `sub_hrules` through each append path.** Keep it minimal: `_replace(sub, hrules=sub_hrules)` for the plain/rule-attached paths; `_Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules)` for the re-extracted path.

- [ ] **Step 4: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -q`
Expected: all pass — the ruled all-text hierarchical table captures (asserted, score > 0); the borderless twin escalates (score 0.0).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_hrule_split.py
git commit -m "feat(etkl): attach page hrules to bands; all-text hierarchical tables capture via rule split [task 3]"
```

---

### Task 4: Additive guarantee guard + full suite

**Files:**
- Test: `tests/etkl/test_hrule_split.py`

- [ ] **Step 1: Write the no-hrules additive guard**

```python
def test_shipped_fixtures_have_no_hrules():
    """Every shipped synthetic fixture is borderless -> extract_hrules == [] -> header_body_split
    never consults a rule -> byte-identical. The branch-wide additive guarantee."""
    for name in ["simple_table_pdf", "pivoted_table_pdf", "crosstab_table_pdf",
                 "row_grouped_table_pdf", "region_pivot_pdf", "partial_merge_report_pdf"]:
        p = os.path.join(tempfile.mkdtemp(), name + ".pdf")
        getattr(F, name)(p)
        assert extract_hrules(p) == [], f"{name} unexpectedly has horizontal rules"
```

- [ ] **Step 2: Run the hrule suite**

Run: `./.venv/bin/python -m pytest tests/etkl/test_hrule_split.py -q`
Expected: all pass.

- [ ] **Step 3: Full suite (no regression)**

Run: `./.venv/bin/python -m pytest -q`
Expected: baseline **427 passed, 5 skipped** + the new hrule tests, zero failures. Any change to an existing header/hierarchical test means the fallback leaked onto a non-`None` type split — STOP and fix (the fallback runs only when the type split is `None`).

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_hrule_split.py
git commit -m "test(etkl): shipped-fixtures-have-no-hrules additive guarantee [hrule-split task 4]"
```

---

## Self-Review (completed)

- **Spec coverage:** extract_hrules (PROCEDURAL) → Task 1; Band.hrules + `_hrule_split` fallback on the `None` branch + type-split-precedence → Task 2; compile wiring + end-to-end capture + borderless-escalates → Task 3; additive guard + full suite → Task 4. DoD (all-text hierarchical captures; borderless escalates; typed split unchanged; no-hrules byte-identical) → Tasks 2-4.
- **Placeholder scan:** Task 3 Step 3 says "read the current `compile_tables` band loop and thread `sub_hrules` through each append path" rather than a single verbatim block — this is because the loop was rewritten by the border-aware-grid loop (rule re-extraction branch) and the implementer must thread hrules through its actual current shape; the exact per-path edits are named (`_replace(sub, hrules=...)` / `_Band(..., sub_rules, sub_hrules)`). Not a vague placeholder — a precise instruction against live code.
- **Type consistency:** `HRule(y, x0, x1)`, `extract_hrules(pdf_path, page_number)->list[HRule]`, `Band(..., rules=(), hrules=())`, `_hrule_split(band)->int|None`, `header_body_split(band, grid)->int|None` (unchanged signature) used consistently across tasks.
- **Known risk (flag for review):** `header_body_split` now reads `band.hrules` via `getattr(band, "hrules", ())` — confirm all callers pass a `Band` (which has the field) or the `getattr` default keeps non-Band/legacy callers safe; and confirm the fallback truly never runs when the type split is non-`None` (the `if split is not None: return split` guard).
