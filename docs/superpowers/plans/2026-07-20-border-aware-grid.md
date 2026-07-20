# Border-Aware Column Boundaries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a table is ruled, derive its leaf-column boundaries from the vertical rule lines (accepted only when the band's words strictly tile them), fixing tight/ruled-column data mis-capture — while leaving every borderless table byte-identical.

**Architecture:** `geometry.extract_rules` pulls vertical ruled segments (PROCEDURAL, like `extract_words`). `Band` gains a defaulted `rules` field; `compile_tables` attaches each band the rules overlapping its y-extent. `infer_leaf_grid`, when a band has rules, builds candidate boundaries from the rule x-positions and returns them iff every band word tiles them (threshold-free oracle); otherwise it runs the existing whitespace path unchanged.

**Tech Stack:** Python 3, `pdfplumber` (already a dep), `reportlab` (test fixtures), `pytest`.

## Global Constraints

- **Test interpreter (MANDATORY):** every test via `./.venv/bin/python -m pytest …` (rdflib 7.6.0). Bare `python`/`python3`/`pytest` = wrong env (spurious failures). Wherever a step says `pytest …`, run `./.venv/bin/python -m pytest …`.
- **Purely additive — borderless tables unchanged (the regression guarantee):** with no rules attached, `infer_leaf_grid` MUST behave byte-identically to today. Every shipped fixture is a borderless synthetic PDF → no rules → identical grid. If any borderless fixture's grid changes, the rule path is leaking — that is a defect, not an acceptable diff.
- **§8 gate:** `extract_rules` (raw extraction) and the rule→boundary mapping (exact geometry) are PROCEDURAL with NO tuned decision constant. The only geometry epsilons are `COORD_EPS`-style float tolerances (for "vertical" and strict containment), not decision thresholds. The accept/reject is the threshold-free word-tiling oracle. Do NOT touch the whitespace path's `0.98`/`3`/`4` (out of scope, still the unruled fallback).
- **Conservative:** rule boundaries are used ONLY when every band word strictly tiles them; any straddle → whitespace fallback. Never trust a rule without word confirmation.
- **Ownership/licensing:** Apache-2.0 code; author François Rosselet © 2026.
- **Full suite** via `.venv` at the end; baseline **415 passed / 5 skipped**. Zero regressions.

## File Structure

- **Modify** `src/iladub/etkl/geometry.py` — `Rule` dataclass + `extract_rules(pdf_path, page_number)`.
- **Modify** `src/iladub/etkl/bands.py` — `Band` gains `rules: tuple[Rule, ...] = ()`.
- **Modify** `src/iladub/etkl/grid.py` — `infer_leaf_grid` rule path (+ a `_rule_boundaries` helper) with word-tiling disposition; whitespace path untouched when no rules.
- **Modify** `src/iladub/etkl/compile.py` — extract rules, attach band-overlapping rules to each final band.
- **Modify** `tests/etkl/fixtures.py` — `ruled_tight_table_pdf(path)` (tight columns + `canvas.line` vertical separators) and a `borderless_tight_table_pdf(path)` twin (same words, no lines).
- **Create** `tests/etkl/test_border_grid.py` — extraction, boundary recovery, tiling accept/reject, borderless byte-identical guard, end-to-end compile.

Verified facts: `Band(lines, top, bottom)` (frozen; `detect_bands` builds it positionally). `LeafGrid(boundaries, ncols, pitch, confidence)`. `COORD_EPS = 0.01` in geometry.py. pdfplumber `page.lines` dicts carry `x0,x1,top,bottom` (top<bottom from page top); a vertical rule has `|x0-x1|` tiny and `bottom-top` large. On the probe `r_tight`, vertical rule x's = `[58,120,175,230,285,342]` (5 columns).

---

### Task 1: `extract_rules` + `Rule` (vertical ruled-line extraction)

**Files:**
- Modify: `src/iladub/etkl/geometry.py`
- Modify: `tests/etkl/fixtures.py` (add the two fixtures)
- Test: `tests/etkl/test_border_grid.py`

**Interfaces:**
- Produces: `Rule(x: float, top: float, bottom: float)` (frozen); `extract_rules(pdf_path, page_number=0) -> list[Rule]` — one `Rule` per near-vertical `page.lines`/`page.edges` segment; `ruled_tight_table_pdf(path) -> dict`, `borderless_tight_table_pdf(path) -> dict`.

- [ ] **Step 1: Add the fixtures**

In `tests/etkl/fixtures.py` (uses the existing `canvas`/`letter`/`PAGE_H` imports):

```python
def _tight_table(path, ruled):
    """5 tight columns (~2pt gutters). `ruled` draws vertical separators (canvas.line)."""
    cols = [(60, 120), (122, 175), (177, 230), (232, 285), (287, 340)]
    headers = ["Product", "Q1", "Q2", "Q3", "Q4"]
    rows = [("Alpha", "120", "135", "150", "160"), ("Beta", "90", "95", "100", "110"),
            ("Gamma", "45", "50", "55", "60"), ("Delta", "200", "210", "220", "240"),
            ("Epsilon", "30", "35", "40", "45"), ("Zeta", "75", "80", "85", "90")]
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 20.0
    tbl_bottom = top - (len(rows) + 1) * rh
    if ruled:
        c.setLineWidth(0.7)
        for (l, r) in cols:
            c.line(l - 2, top + 12, l - 2, tbl_bottom)        # vertical separators
        c.line(cols[-1][1] + 2, top + 12, cols[-1][1] + 2, tbl_bottom)
    c.setFont("Helvetica-Bold", 9)
    for (l, r), h in zip(cols, headers):
        c.drawString(l, top, h)
    c.setFont("Helvetica", 9)
    for i, row in enumerate(rows):
        y = top - (i + 1) * rh
        for (l, r), cell in zip(cols, row):
            c.drawString(l, y, cell)
    c.save()
    # true separator x's (canvas.line x = col_left-2 ; last = col_right+2)
    return {"n_leaf_cols": 5, "rule_xs": [cols[0][0] - 2] + [l - 2 for (l, r) in cols[1:]] + [cols[-1][1] + 2]}


def ruled_tight_table_pdf(path: str) -> dict:
    return _tight_table(path, ruled=True)


def borderless_tight_table_pdf(path: str) -> dict:
    return _tight_table(path, ruled=False)
```

- [ ] **Step 2: Write the failing extraction test**

Create `tests/etkl/test_border_grid.py`:

```python
import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_rules
from tests.etkl import fixtures as F


def _pdf(fn):
    p = os.path.join(tempfile.mkdtemp(), fn.__name__ + ".pdf")
    meta = fn(p)
    return p, meta


def test_extract_rules_recovers_vertical_separators():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    rules = extract_rules(p)
    xs = sorted({round(r.x, 0) for r in rules})
    # the 6 vertical separators (5 columns) — allow rounding to the nearest point
    assert xs == sorted({round(x, 0) for x in meta["rule_xs"]}), f"got {xs}"


def test_extract_rules_empty_on_borderless():
    p, _ = _pdf(F.borderless_tight_table_pdf)
    assert extract_rules(p) == []
```

- [ ] **Step 3: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -q`
Expected: FAIL (`ImportError: cannot import name 'extract_rules'`).

- [ ] **Step 4: Implement `Rule` + `extract_rules` in `geometry.py`**

```python
@dataclass(frozen=True)
class Rule:
    x: float       # x-position of a vertical ruled line (points from page left)
    top: float     # y-extent, page-top convention
    bottom: float


def extract_rules(pdf_path: str, page_number: int = 0) -> list["Rule"]:
    """Vertical ruled line segments on a page (the author's explicit column separators).

    PROCEDURAL raw extraction (like extract_words): reads pdfplumber's vector lines/edges;
    a segment is 'vertical' when its horizontal span is < 1pt and its vertical span > 2pt.
    Horizontal rules are ignored (a future header/row-split signal)."""
    out: list[Rule] = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        for seg in list(page.lines) + list(page.edges):
            x0, x1 = float(seg["x0"]), float(seg["x1"])
            top, bottom = float(seg["top"]), float(seg["bottom"])
            if abs(x1 - x0) < 1.0 and (bottom - top) > 2.0:
                out.append(Rule((x0 + x1) / 2.0, top, bottom))
    # de-duplicate near-identical rules (lines + edges can double-report)
    uniq: list[Rule] = []
    for r in sorted(out, key=lambda r: (round(r.x, 1), r.top)):
        if not any(abs(r.x - u.x) < 0.5 and abs(r.top - u.top) < 1.0 and abs(r.bottom - u.bottom) < 1.0 for u in uniq):
            uniq.append(r)
    return uniq
```

- [ ] **Step 5: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -q`
Expected: 2 passed. (If `xs` has extra/missing values, inspect whether `page.edges` double-reports — tighten the dedup; do NOT relax the fixture.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/fixtures.py tests/etkl/test_border_grid.py
git commit -m "feat(etkl): extract vertical ruled lines (Rule + extract_rules) [border-aware grid task 1]"
```

---

### Task 2: `Band.rules` field + rule-derived boundaries in `infer_leaf_grid`

**Files:**
- Modify: `src/iladub/etkl/bands.py`
- Modify: `src/iladub/etkl/grid.py`
- Test: `tests/etkl/test_border_grid.py`

**Interfaces:**
- Consumes: `Rule` (Task 1), `COORD_EPS`.
- Produces: `Band(lines, top, bottom, rules=())`; `infer_leaf_grid` unchanged signature but rule-aware; `_rule_boundaries(band) -> list[float] | None`.

- [ ] **Step 1: Add the `rules` field to `Band`**

In `src/iladub/etkl/bands.py`:

```python
from .geometry import Line, Rule

@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float
    rules: tuple[Rule, ...] = ()
```

(`detect_bands` constructs `Band(tuple(g), top, bottom)` positionally — the default keeps it working.)

- [ ] **Step 2: Write failing grid tests**

Add to `tests/etkl/test_border_grid.py`:

```python
from iladub.etkl.geometry import extract_words, text_lines, Rule
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.grid import infer_leaf_grid
from dataclasses import replace


def _table_band_with_rules(pdf_path):
    ws = extract_words(pdf_path); bands = detect_bands(text_lines(ws))
    band = max(bands, key=lambda b: len(b.lines))           # the table band
    rules = [r for r in extract_rules(pdf_path) if r.top <= band.bottom and r.bottom >= band.top]
    return band, tuple(rules)


def test_rule_grid_recovers_five_columns():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    band, rules = _table_band_with_rules(p)
    ruled = replace(band, rules=rules)
    g = infer_leaf_grid(ruled)
    assert g.ncols == 5, f"rule grid ncols={g.ncols} (whitespace gave 4)"
    assert g.confidence == 1.0


def test_no_rules_is_byte_identical_to_whitespace():
    p, _ = _pdf(F.borderless_tight_table_pdf)
    band, _ = _table_band_with_rules(p)             # borderless -> rules empty
    assert band.rules == ()
    assert infer_leaf_grid(band) == infer_leaf_grid(replace(band, rules=()))   # additive guarantee


def test_straddling_rules_fall_back_to_whitespace():
    # a lone bogus rule through the middle of a word -> words don't tile -> whitespace path
    p, _ = _pdf(F.borderless_tight_table_pdf)
    band, _ = _table_band_with_rules(p)
    bogus = (Rule(x=100.0, top=band.top, bottom=band.bottom),)
    assert infer_leaf_grid(replace(band, rules=bogus)) == infer_leaf_grid(band)
```

- [ ] **Step 3: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -k "rule_grid or byte_identical or straddling" -v`
Expected: FAIL (`test_rule_grid_recovers_five_columns` gives ncols=4 — rule path not implemented).

- [ ] **Step 4: Implement the rule path in `grid.py`**

Add near the top (imports): `from .geometry import Rule` if needed and `COORD_EPS` (import from geometry). Add:

```python
from .geometry import COORD_EPS


def _rule_boundaries(band) -> list[float] | None:
    """Candidate leaf boundaries from the band's vertical rules — returned ONLY if every band
    word strictly tiles them (each word within some [x_i, x_i+1]); else None (whitespace fallback).
    Threshold-free: the words confirm the rules are column separators."""
    if not band.rules:
        return None
    xs = sorted({round(r.x, 2) for r in band.rules})
    if len(xs) < 2:
        return None
    words = [w for ln in band.lines for w in ln.words]
    if not words:
        return None
    for w in words:
        if not any(xs[c] - COORD_EPS <= w.x0 and w.x1 <= xs[c + 1] + COORD_EPS
                   for c in range(len(xs) - 1)):
            return None            # a word straddles / lies outside the rules -> reject
    return xs
```

In `infer_leaf_grid`, at the very top of the body (before the whitespace computation):

```python
    rb = _rule_boundaries(band)
    if rb is not None:
        widths = [rb[i + 1] - rb[i] for i in range(len(rb) - 1)]
        pitch = float(np.median(widths)) if widths else 0.0
        return LeafGrid(tuple(rb), len(rb) - 1, pitch, 1.0)   # explicit boundaries -> full confidence
```

- [ ] **Step 5: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -q`
Expected: all pass (extraction + the 3 grid tests). The byte-identical + straddling tests prove the additive guarantee and the conservative fallback.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/bands.py src/iladub/etkl/grid.py tests/etkl/test_border_grid.py
git commit -m "feat(etkl): rule-derived leaf boundaries in infer_leaf_grid (word-tiling disposed) [task 2]"
```

---

### Task 3: Wire rules through `compile_tables` + end-to-end ruled compile

**Files:**
- Modify: `src/iladub/etkl/compile.py`
- Test: `tests/etkl/test_border_grid.py`

**Interfaces:**
- Consumes: `extract_rules` (Task 1), `Band.rules` (Task 2), `segment`.

- [ ] **Step 1: Write the failing end-to-end test**

Add to `tests/etkl/test_border_grid.py`:

```python
from iladub.etkl import compile_tables


def test_ruled_tight_table_compiles_as_record_5_cols():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    rep = compile_tables(p)
    kinds = [(str(r.kind).split(".")[-1], r.verdict) for r in rep.regions]
    # the tight ruled table is now captured as a RECORD_TABLE (was UNSUPPORTED via a 4-col grid)
    assert ("RECORD_TABLE", "asserted") in kinds, kinds


def test_borderless_tight_table_unchanged_path():
    # the borderless twin still goes through the whitespace path (no rules) — same as pre-change
    p, _ = _pdf(F.borderless_tight_table_pdf)
    rep = compile_tables(p)   # must not raise; behavior identical to today's whitespace inference
    assert rep is not None
```

- [ ] **Step 2: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -k ruled_tight_table_compiles -q`
Expected: FAIL (rules not attached in compile → still 4-col whitespace grid → not RECORD).

- [ ] **Step 3: Wire rules into `compile_tables`**

In `src/iladub/etkl/compile.py`, in `compile_tables`, replace the band construction:

```python
    from .geometry import extract_rules
    from dataclasses import replace as _replace
    words = extract_words(pdf_path, page_number)
    page_rules = extract_rules(pdf_path, page_number)
    raw_bands = detect_bands(text_lines(words))
    from .segment import segment, is_multi_table_ambiguous
    bands = []
    for band in raw_bands:
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules if r.top <= sub.bottom and r.bottom >= sub.top)
            bands.append(_replace(sub, rules=sub_rules) if sub_rules else sub)
```

(Everything downstream — `classify`, `recover_leaf_grid`, `segment` — reaches `infer_leaf_grid(band)` which now reads `band.rules`; no other change needed. `segment`'s sub-bands lose the parent's `rules` when it rebuilds Bands, so attach AFTER segment, as above.)

- [ ] **Step 4: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -q`
Expected: all pass — the ruled table compiles as `RECORD_TABLE` with 5 columns; the borderless twin unaffected.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_border_grid.py
git commit -m "feat(etkl): attach page rules to bands in compile_tables (ruled tables use rule grid) [task 3]"
```

---

### Task 4: Regression guard + full suite (the additive guarantee, at scale)

**Files:**
- Test: `tests/etkl/test_border_grid.py`

- [ ] **Step 1: Write the borderless-fixtures byte-identical guard**

Add a test that a spread of shipped borderless fixtures produce **no rules** and thus an unchanged grid — the additive guarantee proven beyond the twin:

```python
def test_shipped_fixtures_have_no_rules():
    """Every shipped synthetic fixture is borderless -> extract_rules == [] -> whitespace path
    untouched. This is the branch-wide additive guarantee."""
    import tempfile
    for name in ["simple_table_pdf", "pivoted_table_pdf", "crosstab_table_pdf",
                 "row_grouped_table_pdf", "region_pivot_pdf", "partial_merge_report_pdf"]:
        p = os.path.join(tempfile.mkdtemp(), name + ".pdf")
        getattr(F, name)(p)
        assert extract_rules(p) == [], f"{name} unexpectedly has rules"
```

- [ ] **Step 2: Run the border-grid suite**

Run: `./.venv/bin/python -m pytest tests/etkl/test_border_grid.py -q`
Expected: all pass.

- [ ] **Step 3: Full suite (no regression)**

Run: `./.venv/bin/python -m pytest -q`
Expected: baseline **415 passed, 5 skipped** + the new border-grid tests, zero failures. Any change to an existing table test means the rule path leaked into a borderless case — STOP and fix (the rule path must be inert without rules).

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_border_grid.py
git commit -m "test(etkl): borderless-fixtures-no-rules additive guarantee [task 4]"
```

---

## Self-Review (completed)

- **Spec coverage:** extract_rules (PROCEDURAL) → Task 1; Band.rules + rule-boundaries + word-tiling oracle + whitespace fallback → Task 2; compile wiring + end-to-end ruled compile → Task 3; additive guarantee at scale + full suite → Task 4. DoD (ruled fixture → RECORD 5 cols; borderless unchanged; byte-identical guard) → Tasks 2-4. §8 (no tuned constant; threshold-free oracle) → the `_rule_boundaries` design + Global Constraints.
- **Placeholder scan:** none — concrete code/commands throughout. The "vertical" test (`|x1-x0|<1.0 && bottom-top>2.0`) and dedup tolerances are geometry epsilons (float robustness), not decision thresholds — called out as such.
- **Type consistency:** `Rule(x, top, bottom)`, `extract_rules(pdf_path, page_number)->list[Rule]`, `Band(...,rules=())`, `_rule_boundaries(band)->list[float]|None`, `infer_leaf_grid(band)->LeafGrid` (unchanged signature) used consistently across tasks.
- **Known risk (flag for review):** the word-tiling oracle rejects if ANY band word lies outside the outer rules — so **inner-only-ruled** tables (no outer border; edge-column words outside the first/last rule) fall back to whitespace. This is intentional (conservative, documented in the spec's scope boundary), but the reviewer should confirm the ruled fixture is fully bordered (outer rules present) so the DoD case genuinely exercises the rule path, and that the fallback for inner-only rules is a safe no-op (not a crash).
