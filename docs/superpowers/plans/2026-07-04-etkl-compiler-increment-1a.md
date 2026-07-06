# ET(K)L compiler — Increment 1a (geometry · bands · body leaf-grid) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** From a text-layer PDF, deterministically recover the layout **bands** (title / paragraph / table / footnote regions) and, within a table band, the **body leaf-column grid** — measured in PDF points, validated on synthetic fixtures.

**Architecture:** The deterministic *measurement* + *structure-with-invariants* floor of the compiler (the part of the "determinism cursor" that is always deterministic — see `docs/superpowers/specs/2026-07-04-etkl-compiler-design.md`). No models. Words come from pdfplumber in points; bands come from vertical-gap splitting; the leaf grid comes from a column-whitespace occupancy profile computed **from body rows**. Header tiling, the validator, `dec`, and the VLM residue are increments 1b/1c.

**Tech Stack:** Python 3.12, `pdfplumber` (geometry, points), `numpy` (occupancy profiles), `reportlab` (synthetic test PDFs), `pytest`.

**Note on the existing skeleton:** François has a working prior skeleton embodying this same design. This plan builds 1a test-first from scratch so it is self-contained; if the skeleton is pasted, its `extract_words`/band/grid functions can seed Tasks 2–4 directly (same interfaces). The hard part (header tiling) is increment 1b, where we will prefer folding in the skeleton.

---

## File Structure

- `src/iladub/etkl/__init__.py` — subpackage marker + public exports.
- `src/iladub/etkl/geometry.py` — `Word`, `extract_words()`, `Line`, `text_lines()`. *One responsibility: PDF → points geometry → text lines.*
- `src/iladub/etkl/bands.py` — `Band`, `detect_bands()`. *One responsibility: lines → horizontal bands.*
- `src/iladub/etkl/grid.py` — `LeafGrid`, `infer_leaf_grid()`. *One responsibility: a band → column leaf grid + confidence.*
- `tests/etkl/fixtures.py` — reportlab synthetic-PDF builders with known geometry.
- `tests/etkl/test_geometry.py`, `tests/etkl/test_bands.py`, `tests/etkl/test_grid.py`, `tests/etkl/test_foundation.py`.
- `pyproject.toml` — add an `etkl` optional-dependency group.

---

### Task 1: Scaffold the subpackage, deps, and synthetic-PDF fixtures

**Files:**
- Create: `src/iladub/etkl/__init__.py`
- Modify: `pyproject.toml` (optional-dependencies)
- Create: `tests/etkl/__init__.py`, `tests/etkl/fixtures.py`
- Test: `tests/etkl/test_foundation.py` (smoke)

- [ ] **Step 1: Add the `etkl` optional-dependency group to `pyproject.toml`**

Under `[project.optional-dependencies]` (which already has a `baml = [...]` group), add:

```toml
etkl = [
    "pdfplumber>=0.11",
    "numpy>=1.26",
    "reportlab>=4.0",
]
```

- [ ] **Step 2: Install the group**

Run: `python -m pip install -e ".[etkl]"`
Expected: pdfplumber, numpy, reportlab install without error.

- [ ] **Step 3: Create the package + test package markers**

`src/iladub/etkl/__init__.py`:

```python
"""iladub ET(K)L compiler — deterministic multimodal extraction (increment 1a)."""
```

`tests/etkl/__init__.py`: (empty file)

- [ ] **Step 4: Write the synthetic-PDF fixtures**

`tests/etkl/fixtures.py`:

```python
"""Synthetic PDFs with KNOWN geometry, for testing the deterministic engine.

reportlab draws at exact points from the page's bottom-left origin. pdfplumber
reports `top` from the page's TOP, so a string drawn at reportlab y maps to
pdfplumber top = page_height - y (minus font ascent, but tests use tolerances).
"""
from __future__ import annotations
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter  # 612 x 792 points


def simple_table_pdf(path: str) -> dict:
    """A title band + a 3-column table (header row + 3 data rows).

    Returns the ground truth: column x-positions and row y-positions (reportlab
    coords), so tests can assert against known geometry.
    """
    cols = [72.0, 240.0, 400.0]           # left x of each column
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    c.drawString(72.0, PAGE_H - 72.0, "Complete Blood Count")   # title band
    rows = [
        ("Analyte", "Value", "Unit"),
        ("Hemoglobin", "13.2", "g/dL"),
        ("Hematocrit", "39.5", "%"),
        ("Platelets", "250", "x10^9/L"),
    ]
    y0 = PAGE_H - 130.0                     # table starts well below the title
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_body_rows": 3, "n_table_rows": 4,
            "title": "Complete Blood Count"}
```

- [ ] **Step 5: Smoke test — a fixture PDF is created and readable by pdfplumber**

`tests/etkl/test_foundation.py`:

```python
import pdfplumber
from tests.etkl.fixtures import simple_table_pdf


def test_fixture_pdf_is_readable(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    with pdfplumber.open(str(pdf)) as doc:
        text = doc.pages[0].extract_text() or ""
    assert truth["title"] in text
    assert "Hemoglobin" in text
```

- [ ] **Step 6: Run the smoke test**

Run: `pytest tests/etkl/test_foundation.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/iladub/etkl/__init__.py tests/etkl/__init__.py tests/etkl/fixtures.py tests/etkl/test_foundation.py
git commit -m "feat(etkl): scaffold etkl subpackage + synthetic-PDF fixtures"
```

---

### Task 2: `geometry` — words in points, grouped into text lines

**Files:**
- Create: `src/iladub/etkl/geometry.py`
- Test: `tests/etkl/test_geometry.py`

- [ ] **Step 1: Write the failing tests**

`tests/etkl/test_geometry.py`:

```python
from iladub.etkl.geometry import extract_words, text_lines, Word
from tests.etkl.fixtures import simple_table_pdf, PAGE_H


def test_extract_words_returns_points(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    words = extract_words(str(pdf))
    hgb = [w for w in words if w.text == "Hemoglobin"]
    assert len(hgb) == 1
    # x0 is in points, near the first column's left edge (72)
    assert abs(hgb[0].x0 - truth["cols"][0]) < 3.0
    # pdfplumber `top` is measured from the page top
    assert 0 < hgb[0].top < PAGE_H


def test_text_lines_groups_rows(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    lines = text_lines(extract_words(str(pdf)))
    # 1 title line + 4 table rows = 5 lines
    assert len(lines) == 5
    # each table row line has 3 words; sorted left-to-right
    body = [ln for ln in lines if any(w.text == "Hemoglobin" for w in ln.words)][0]
    assert [w.text for w in body.words] == ["Hemoglobin", "13.2", "g/dL"]
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/etkl/test_geometry.py -v`
Expected: FAIL (ImportError: cannot import name 'extract_words').

- [ ] **Step 3: Implement `geometry.py`**

`src/iladub/etkl/geometry.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

import pdfplumber


@dataclass(frozen=True)
class Word:
    text: str
    x0: float   # points, from page left
    x1: float
    top: float  # points, from page TOP (pdfplumber convention)
    bottom: float
    page: int = 0


@dataclass(frozen=True)
class Line:
    words: tuple[Word, ...]
    top: float
    bottom: float


def extract_words(pdf_path: str, page_number: int = 0) -> list[Word]:
    """All text runs on a page, with bounding boxes in PDF points."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        raw = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    return [
        Word(w["text"], float(w["x0"]), float(w["x1"]),
             float(w["top"]), float(w["bottom"]), page_number)
        for w in raw
    ]


def text_lines(words: list[Word], y_tol: float | None = None) -> list[Line]:
    """Group words into lines by vertical proximity of their `top`.

    Two words share a line when their tops differ by less than `y_tol`
    (default: 0.6 x median glyph height). Lines are returned top-to-bottom,
    words within a line left-to-right.
    """
    if not words:
        return []
    ws = sorted(words, key=lambda w: (round(w.top, 1), w.x0))
    med_h = sorted(w.bottom - w.top for w in ws)[len(ws) // 2]
    tol = y_tol if y_tol is not None else 0.6 * med_h
    groups: list[list[Word]] = [[ws[0]]]
    for w in ws[1:]:
        if abs(w.top - groups[-1][0].top) > tol:
            groups.append([])
        groups[-1].append(w)
    lines = []
    for g in groups:
        g = sorted(g, key=lambda w: w.x0)
        lines.append(Line(tuple(g), min(w.top for w in g), max(w.bottom for w in g)))
    return sorted(lines, key=lambda ln: ln.top)
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/etkl/test_geometry.py -v`
Expected: PASS (both tests). If `test_text_lines_groups_rows` finds 6 lines (title split), widen the fixture's title/table gap — it is already 58pt, so this should not happen; if it does, inspect `y_tol`.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/test_geometry.py
git commit -m "feat(etkl): geometry — words in points + text-line grouping"
```

---

### Task 3: `bands` — split lines into horizontal bands by vertical gaps

**Files:**
- Create: `src/iladub/etkl/bands.py`
- Test: `tests/etkl/test_bands.py`

- [ ] **Step 1: Write the failing tests**

`tests/etkl/test_bands.py`:

```python
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from tests.etkl.fixtures import simple_table_pdf


def test_title_splits_from_table(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    bands = detect_bands(text_lines(extract_words(str(pdf))))
    assert len(bands) == 2                         # title band + table band
    title_band, table_band = bands[0], bands[1]
    assert len(title_band.lines) == 1
    assert len(table_band.lines) == 4              # header row + 3 data rows


def test_single_band_when_no_large_gaps(tmp_path):
    # the 4 table rows alone form ONE band (uniform spacing)
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    lines = text_lines(extract_words(str(pdf)))
    table_lines = [ln for ln in lines if ln is not lines[0]]  # drop the title line
    bands = detect_bands(table_lines)
    assert len(bands) == 1
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/etkl/test_bands.py -v`
Expected: FAIL (ImportError: cannot import name 'detect_bands').

- [ ] **Step 3: Implement `bands.py`**

`src/iladub/etkl/bands.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .geometry import Line


@dataclass(frozen=True)
class Band:
    lines: tuple[Line, ...]
    top: float
    bottom: float


def detect_bands(lines: list[Line], gap_factor: float = 1.8) -> list[Band]:
    """Split lines into bands wherever the inter-line gap exceeds
    `gap_factor` x the median inter-line gap. A band is a run of lines with
    regular spacing (a paragraph, a table body, a title)."""
    if not lines:
        return []
    ls = sorted(lines, key=lambda ln: ln.top)
    gaps = [ls[i + 1].top - ls[i].bottom for i in range(len(ls) - 1)]
    positive = [g for g in gaps if g > 0]
    med_gap = median(positive) if positive else 0.0
    groups: list[list[Line]] = [[ls[0]]]
    for i in range(1, len(ls)):
        gap = ls[i].top - ls[i - 1].bottom
        if med_gap > 0 and gap > gap_factor * med_gap:
            groups.append([])
        groups[-1].append(ls[i])
    return [
        Band(tuple(g), min(ln.top for ln in g), max(ln.bottom for ln in g))
        for g in groups
    ]
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/etkl/test_bands.py -v`
Expected: PASS. (If the title does not split: the title→table gap is 58pt vs row gap ~18pt, ratio ~3.2 > 1.8, so it must. If it over-splits the table rows, raise `gap_factor`.)

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/bands.py tests/etkl/test_bands.py
git commit -m "feat(etkl): bands — vertical-gap band detection (layout parse)"
```

---

### Task 4: `grid` — body leaf-column grid from a whitespace occupancy profile

**Files:**
- Create: `src/iladub/etkl/grid.py`
- Test: `tests/etkl/test_grid.py`

- [ ] **Step 1: Write the failing tests**

`tests/etkl/test_grid.py`:

```python
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from iladub.etkl.grid import infer_leaf_grid
from tests.etkl.fixtures import simple_table_pdf


def _table_band(pdf_path):
    bands = detect_bands(text_lines(extract_words(pdf_path)))
    return bands[1]  # band 0 = title, band 1 = table


def test_three_columns_detected(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    assert grid.ncols == 3
    # every column's left boundary sits at or just left of a known column x
    for cx in truth["cols"]:
        assert any(b <= cx + 2.0 for b in grid.boundaries)


def test_confidence_scales_with_rows(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    grid = infer_leaf_grid(_table_band(str(pdf)))
    # 4 rows -> full confidence under the default sample target
    assert 0.0 < grid.confidence <= 1.0
    assert grid.confidence >= 0.9
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/etkl/test_grid.py -v`
Expected: FAIL (ImportError: cannot import name 'infer_leaf_grid').

- [ ] **Step 3: Implement `grid.py`**

`src/iladub/etkl/grid.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bands import Band


@dataclass(frozen=True)
class LeafGrid:
    boundaries: tuple[float, ...]  # x separators in points, len == ncols + 1
    ncols: int
    pitch: float                   # median column width (points)
    confidence: float              # 0..1, from row-sample size


def _column_blank_profile(band: Band, x0: float, x1: float,
                          bin_w: float = 1.0) -> np.ndarray:
    """Per x-bin, the fraction of band rows that are BLANK at that x."""
    nbins = max(1, int(np.ceil((x1 - x0) / bin_w)))
    ink = np.zeros((len(band.lines), nbins), dtype=bool)
    for r, line in enumerate(band.lines):
        for w in line.words:
            a = int((w.x0 - x0) / bin_w)
            b = int(np.ceil((w.x1 - x0) / bin_w))
            ink[r, max(0, a):min(nbins, b)] = True
    return 1.0 - ink.mean(axis=0)  # blank fraction per bin


def infer_leaf_grid(band: Band, gutter_pct: float = 0.98,
                    min_gutter_bins: int = 3, sample_target: int = 4) -> LeafGrid:
    """Column grid from the vertical whitespace profile of the band.

    A gutter is a run of >= `min_gutter_bins` x-bins that are blank on >=
    `gutter_pct` of rows. Boundaries are gutter centers plus the band's ink
    extremes. Confidence scales with the number of rows supporting the profile
    (thin bands -> low confidence -> lower decidability ceiling downstream).
    """
    xs0 = min(w.x0 for ln in band.lines for w in ln.words)
    xs1 = max(w.x1 for ln in band.lines for w in ln.words)
    blank = _column_blank_profile(band, xs0, xs1)
    is_gutter = blank >= gutter_pct

    boundaries = [xs0]
    run_start = None
    for i, g in enumerate(list(is_gutter) + [False]):  # sentinel flush
        if g and run_start is None:
            run_start = i
        elif not g and run_start is not None:
            if (i - run_start) >= min_gutter_bins:
                boundaries.append(xs0 + (run_start + i) / 2.0)  # gutter center
            run_start = None
    boundaries.append(xs1)
    boundaries = sorted({round(b, 2) for b in boundaries})

    ncols = len(boundaries) - 1
    widths = [boundaries[i + 1] - boundaries[i] for i in range(ncols)]
    pitch = float(np.median(widths)) if widths else 0.0
    confidence = min(1.0, len(band.lines) / float(sample_target))
    return LeafGrid(tuple(boundaries), ncols, pitch, confidence)
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/etkl/test_grid.py -v`
Expected: PASS. Likely failure mode: `ncols` comes out as 4 or 2 if the gutter threshold splits/merges columns. If 4, the value column split — raise `min_gutter_bins`; if 2, lower `gutter_pct` to `0.95`. Tune against the fixture, then re-run.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/grid.py tests/etkl/test_grid.py
git commit -m "feat(etkl): grid — body leaf-column grid via whitespace profile + confidence"
```

---

### Task 5: Foundation end-to-end + public exports

**Files:**
- Modify: `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_foundation.py`

- [ ] **Step 1: Add the end-to-end test**

Append to `tests/etkl/test_foundation.py`:

```python
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid


def test_pdf_to_bands_and_grid(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    bands = detect_bands(text_lines(extract_words(str(pdf))))
    assert len(bands) == 2
    grid = infer_leaf_grid(bands[1])
    assert grid.ncols == truth_ncols(truth)


def truth_ncols(truth):
    return len(truth["cols"])
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/etkl/test_foundation.py::test_pdf_to_bands_and_grid -v`
Expected: FAIL (ImportError — the names are not re-exported from the package yet).

- [ ] **Step 3: Re-export the public API in `__init__.py`**

`src/iladub/etkl/__init__.py`:

```python
"""iladub ET(K)L compiler — deterministic multimodal extraction (increment 1a)."""

from .geometry import Word, Line, extract_words, text_lines
from .bands import Band, detect_bands
from .grid import LeafGrid, infer_leaf_grid

__all__ = [
    "Word", "Line", "extract_words", "text_lines",
    "Band", "detect_bands",
    "LeafGrid", "infer_leaf_grid",
]
```

- [ ] **Step 4: Run the whole etkl suite**

Run: `pytest tests/etkl/ -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/__init__.py tests/etkl/test_foundation.py
git commit -m "feat(etkl): public API exports + PDF->bands->grid foundation test"
```

---

## Self-Review

**Spec coverage (1a slice):** geometry-in-points ✓ (Task 2), layout bands ✓ (Task 3), body-only leaf grid + confidence ✓ (Task 4), relative/points measurement ✓ (grid works in points; fractional tuning noted). Deferred to 1b/1c and *out of scope here*: header tiling, validator/round-trip oracle, `dec` verdict, residue-VLM, neutral holon, FHIR — all explicitly later increments in the spec.

**Placeholder scan:** no TBD/TODO; every code step has runnable code; every test has real assertions. Tuning notes (e.g. "raise `min_gutter_bins`") are guidance *after* a concrete default, not placeholders.

**Type consistency:** `Word`/`Line` (geometry) → consumed by `detect_bands` → `Band` consumed by `infer_leaf_grid` → `LeafGrid`. Names match across tasks and the `__init__` re-export.

**Known iteration points (honest):** the three whitespace/gap constants (`gap_factor`, `gutter_pct`, `min_gutter_bins`) are tuned against the fixture under TDD; the plan states the failure direction for each so tuning is mechanical, not guesswork.

---

## Next increments (separate plans)

- **1b — the hard part:** header-band isolation → gutter-crossing span-snapping → containment tree → header-paths → **validator** (tiling invariants + round-trip oracle) → **`dec`** verdict. *Prefer folding in François's existing skeleton here.*
- **1c:** residue-VLM interface (constrained decoding, validated) + neutral **table/region holon** assembly + `compile()` end-to-end.
- Then Layer 2 (FHIR projection), figures, scans, continued tables (per the spec roadmap).
