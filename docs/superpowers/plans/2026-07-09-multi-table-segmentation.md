# Multi-Table Page Segmentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split a page region that fuses multiple tables (side-by-side, or stacked with a repeated header) into single-table sub-regions and compile each — closing the two fusion silent-wrongs — while never splitting a legitimate single table.

**Architecture:** A recursive `segment(band) → list[Band]` pass between `detect_bands` and `classify`. It *proposes* cuts (widest full-height gutter; repeated-header row) and *certifies* each by re-running the existing `classify` on both sides; a certified cut is taken, an uncertain-but-genuine second table escalates `MULTI_TABLE_AMBIGUOUS` (via a threshold-free stub-asymmetry check), and everything else stays one region. All downstream classifiers/makers are unchanged.

**Tech Stack:** Python 3, rdflib, pdfplumber/reportlab (fixtures), pytest.

## Global Constraints

- **No-false-positive invariant (the safety property):** `segment(band)` MUST return a single-element list for every existing single-table fixture — `simple_table`, `pivoted_table`, `all_text_table`, `crosstab_table`, `row_grouped_table`, `transposed_table`. This is tested before any positive split test. A cross-tab must never be split or escalated.
- **Certification over geometry:** a cut is taken only when both sides independently `classify` as `RECORD_TABLE`. No tuned width constants; the discriminators are structural (`classify`, `has_own_stub`, header-equality).
- **No silent-wrong:** the two fusion cases are split-and-compiled; a genuine-but-not-cleanly-splittable second table escalates `MULTI_TABLE_AMBIGUOUS` (never a fused assertion). Sub-regions that don't compile escalate per-region as today.
- **Reuse, don't reimplement:** `detect_bands`, `text_lines`, `Band`, `classify`/`RegionKind`, `infer_leaf_grid`, `column_of`, `headers.is_numeric`/`header_body_split`. The compile pipeline changes by ONE line (iterate segmented sub-bands) plus the ambiguous-escalation gate.
- **Geometric/lexical only:** no model calls, consistent with the whole compiler.

**Confirmed by empirical probes (2026-07-09):** side-by-side records split at the widest gutter (3.5× median) into two `RECORD_TABLE`s; the cross-tab's widest gutter yields two `UNSUPPORTED` halves with `has_own_stub(right)=False` (kept whole); a repeated-header stack splits into two `RECORD_TABLE`s; no single-table fixture repeats its header as a body row; `has_own_stub` is True for a genuine second table's stub, False for a cross-tab's data-only right half.

---

### Task 1: `segment.py` — the cut proposers + stub check

**Files:**
- Create: `src/iladub/etkl/segment.py`
- Modify: `tests/etkl/fixtures.py` (append `side_by_side_pdf`, `stacked_repeated_header_pdf`, `record_plus_stub_hier_pdf`)
- Test: `tests/etkl/test_segment.py` (create)

**Interfaces:**
- Consumes: `bands.Band`, `geometry.text_lines`, `grid.infer_leaf_grid`, `regions.classify`/`RegionKind`/`column_of`, `headers.is_numeric`/`header_body_split`.
- Produces:
  - `find_repeated_header(band) -> list[int]` — body-row indices equal to the header row.
  - `find_table_gutter(band) -> float | None` — the x of a certified side-by-side cut (both sides `RECORD_TABLE`), else None.
  - `has_own_stub(band) -> bool` — the band's leftmost occupied column has majority-text body cells.
  - `_band_from_words(words) -> Band`, `_band_from_lines(lines) -> Band` (helpers).

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_segment.py`:

```python
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import (side_by_side_pdf, stacked_repeated_header_pdf,
                                 simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf)
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.segment import find_repeated_header, find_table_gutter, has_own_stub


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_find_repeated_header_fires(tmp_path):
    reps = find_repeated_header(_band(stacked_repeated_header_pdf, tmp_path))
    assert len(reps) == 1 and reps[0] >= 1


def test_find_repeated_header_none_on_singles(tmp_path):
    for maker in (simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf):
        assert find_repeated_header(_band(maker, tmp_path)) == []


def test_find_table_gutter_certifies_side_by_side(tmp_path):
    assert find_table_gutter(_band(side_by_side_pdf, tmp_path)) is not None


def test_find_table_gutter_none_on_singles(tmp_path):
    # the critical no-false-positive guard, incl. the cross-tab (its halves are not both-RECORD)
    for maker in (simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf):
        assert find_table_gutter(_band(maker, tmp_path)) is None


def test_has_own_stub(tmp_path):
    # side-by-side right half has a text stub; a cross-tab right half is data-only
    from iladub.etkl.grid import infer_leaf_grid
    from iladub.etkl.regions import column_of
    from iladub.etkl.segment import _band_from_words

    def right_half(maker):
        p = tmp_path / "r.pdf"; maker(str(p))
        words = extract_words(str(p)); band = detect_bands(text_lines(words))[-1]
        g = infer_leaf_grid(band); b = g.boundaries
        cw = {}
        for w in words:
            cw.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        ext = {c: (min(w.x0 for w in ws), max(w.x1 for w in ws)) for c, ws in cw.items()}
        gaps = [(c, ext[c + 1][0] - ext[c][1]) for c in range(g.ncols - 1) if c in ext and c + 1 in ext]
        wc, _ = max(gaps, key=lambda z: z[1]); cut = (ext[wc][1] + ext[wc + 1][0]) / 2.0
        return _band_from_words([w for w in words if (w.x0 + w.x1) / 2.0 >= cut])

    assert has_own_stub(right_half(side_by_side_pdf)) is True
    assert has_own_stub(right_half(crosstab_table_pdf)) is False
```

- [ ] **Step 2: Add the fixtures**

Append to `tests/etkl/fixtures.py`:

```python
def side_by_side_pdf(path: str) -> dict:
    """Two independent record tables abreast, separated by a wide full-height gutter.
    detect_bands (1-D) fuses them into one wide table today; segment must split them."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    left = [(72.0, "Analyte"), (150.0, "Value")]
    right = [(330.0, "Item"), (410.0, "Qty")]
    lrows = [("Analyte", "Value"), ("Hb", "13.2"), ("WBC", "7.8")]
    rrows = [("Item", "Qty"), ("Apple", "10"), ("Pear", "5")]
    for i, (lr, rr) in enumerate(zip(lrows, rrows)):
        y = PAGE_H - 120.0 - i * 18.0
        for (x, _), v in zip(left, lr):
            c.drawString(x, y, v)
        for (x, _), v in zip(right, rr):
            c.drawString(x, y, v)
    c.save()
    return {"left_header": ["Analyte", "Value"], "right_header": ["Item", "Qty"]}


def stacked_repeated_header_pdf(path: str) -> dict:
    """Two record tables stacked with NO vertical gap; the second table repeats the
    header row. detect_bands keeps them one band; segment must split at the repeat."""
    cols = [72.0, 240.0, 400.0]
    rows = [("Analyte", "Value", "Unit"), ("Hb", "13.2", "g/dL"), ("WBC", "7.8", "x10^9"),
            ("Analyte", "Value", "Unit"), ("Ca", "9.5", "mg/dL"), ("Na", "140", "mmol/L")]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {"header": ["Analyte", "Value", "Unit"], "repeat_at": 3}


def record_plus_stub_hier_pdf(path: str) -> dict:
    """A record table (left) beside a table with its OWN stub but a MULTI-WORD /
    non-record header (right) — a genuine second table that is not two clean records.
    Used for the MULTI_TABLE_AMBIGUOUS escalation (has_own_stub right = True, but the
    pair is not both-RECORD)."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    for i, (a, v) in enumerate([("Analyte", "Value"), ("Hb", "13"), ("WBC", "8")]):
        y = PAGE_H - 120.0 - i * 16.0
        c.drawString(72.0, y, a); c.drawString(150.0, y, v)
    # right: a merged/2-level header over its own 'Dept' stub -> classifies UNSUPPORTED
    c.setFont("Courier-Bold", 9)
    c.drawCentredString((430.0 + 500.0) / 2.0, PAGE_H - 116.0, "Metrics")   # merged parent (row 0)
    c.setFont("Courier", 9)
    for i, row in enumerate([("Dept", "M1", "M2"), ("Sales", "10", "20"), ("Ops", "30", "40")]):
        y = PAGE_H - 132.0 - i * 16.0
        for x, v in zip([340.0, 430.0, 500.0], row):
            c.drawString(x, y, v)
    c.save()
    return {"right_stub": "Dept"}
```

- [ ] **Step 3: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_segment.py -q`
Expected: FAIL (ImportError on `find_repeated_header`).

- [ ] **Step 4: Implement the proposers**

Create `src/iladub/etkl/segment.py`:

```python
"""segment — split a fused multi-table band into single-table sub-bands.

detect_bands is 1-D (vertical gaps only), so it fuses side-by-side and
stacked-no-gap tables into one region. segment PROPOSES cuts (widest full-height
gutter; repeated-header row) and CERTIFIES each by re-running classify on both
sides. A certified cut is taken; a genuine-but-uncertain second table escalates
MULTI_TABLE_AMBIGUOUS (via the stub asymmetry). No single table is ever split.
"""
from __future__ import annotations

from .bands import Band
from .geometry import text_lines
from .grid import infer_leaf_grid
from .headers import header_body_split, is_numeric
from .regions import classify, RegionKind, column_of


def _band_from_lines(lines) -> Band:
    lines = tuple(lines)
    return Band(lines, min(l.top for l in lines), max(l.bottom for l in lines))


def _band_from_words(words) -> Band:
    return _band_from_lines(text_lines(list(words)))


def _row_tokens(line) -> tuple[str, ...]:
    return tuple(w.text for w in sorted(line.words, key=lambda w: w.x0))


def find_repeated_header(band: Band) -> list[int]:
    """Body-row indices whose token tuple equals the header row (row 0). A single
    table never repeats its exact header as a data row, so this is false-positive
    free."""
    rows = [_row_tokens(ln) for ln in band.lines]
    if len(rows) < 2:
        return []
    hdr = rows[0]
    return [i for i in range(1, len(rows)) if rows[i] == hdr]


def _col_ink_extents(band: Band, grid):
    b = grid.boundaries
    cw: dict[int, list] = {}
    for ln in band.lines:
        for w in ln.words:
            cw.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
    return {c: (min(w.x0 for w in ws), max(w.x1 for w in ws)) for c, ws in cw.items()}


def _widest_gutter_cut(band: Band):
    """(cut_x, left_words, right_words) at the widest inter-column ink gap, or None."""
    if len(band.lines) < 2:
        return None
    grid = infer_leaf_grid(band)
    if grid.ncols < 2:
        return None
    ext = _col_ink_extents(band, grid)
    gaps = [(c, ext[c + 1][0] - ext[c][1]) for c in range(grid.ncols - 1)
            if c in ext and c + 1 in ext]
    if not gaps:
        return None
    wc, _ = max(gaps, key=lambda z: z[1])
    cut = (ext[wc][1] + ext[wc + 1][0]) / 2.0
    words = [w for ln in band.lines for w in ln.words]
    left = [w for w in words if (w.x0 + w.x1) / 2.0 < cut]
    right = [w for w in words if (w.x0 + w.x1) / 2.0 >= cut]
    if not left or not right:
        return None
    return cut, left, right


def find_table_gutter(band: Band) -> float | None:
    """The x of a CERTIFIED side-by-side cut: the widest full-height gutter where
    BOTH sides independently classify RECORD_TABLE. Else None. The both-RECORD rule
    excludes the cross-tab (its halves are UNSUPPORTED) and every single table."""
    got = _widest_gutter_cut(band)
    if got is None:
        return None
    cut, left, right = got
    lk = classify(_band_from_words(left)).kind
    rk = classify(_band_from_words(right)).kind
    if lk is RegionKind.RECORD_TABLE and rk is RegionKind.RECORD_TABLE:
        return cut
    return None


def has_own_stub(band: Band) -> bool:
    """True iff the band's leftmost occupied column has majority-text body cells —
    its own row identity. Distinguishes a self-contained table from a cross-tab's
    data-only right fragment (threshold-free)."""
    if len(band.lines) < 2:
        return False
    grid = infer_leaf_grid(band)
    b = grid.boundaries
    split = header_body_split(band, grid) or 1
    colcells: dict[int, dict[int, list]] = {}
    for r, ln in enumerate(band.lines):
        for w in ln.words:
            colcells.setdefault(column_of((w.x0 + w.x1) / 2.0, b), {}).setdefault(r, []).append(w.text)
    if not colcells:
        return False
    leftcol = min(colcells)
    body = [" ".join(v) for r, v in colcells[leftcol].items() if r >= split]
    if not body:
        return False
    return sum(1 for t in body if not is_numeric(t)) / len(body) > 0.5
```

- [ ] **Step 5: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_segment.py -q`
Expected: PASS (5 tests).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/segment.py tests/etkl/fixtures.py tests/etkl/test_segment.py
git commit -m "feat(etkl): segment proposers — repeated-header + certified table gutter + has_own_stub"
```

---

### Task 2: `segment.py` — recursion + ambiguity

**Files:**
- Modify: `src/iladub/etkl/segment.py`
- Test: `tests/etkl/test_segment.py`

**Interfaces:**
- Consumes: Task 1's proposers + helpers.
- Produces:
  - `segment(band) -> list[Band]` — recursive: vertical (repeated-header) then horizontal (certified gutter); returns `[band]` when no certified cut exists.
  - `is_multi_table_ambiguous(band) -> bool` — a widest gutter where the left is a valid table and `has_own_stub(right)` but the pair is not both-`RECORD_TABLE` (a genuine second table that segment could not cleanly split).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_segment.py`:

```python
from iladub.etkl.segment import segment, is_multi_table_ambiguous
from tests.etkl.fixtures import (all_text_table_pdf, row_grouped_table_pdf,
                                 transposed_table_pdf, record_plus_stub_hier_pdf)


def test_side_by_side_segments_to_two(tmp_path):
    subs = segment(_band(side_by_side_pdf, tmp_path))
    assert len(subs) == 2
    from iladub.etkl.regions import classify, RegionKind
    assert all(classify(s).kind is RegionKind.RECORD_TABLE for s in subs)


def test_stacked_repeated_segments_to_two(tmp_path):
    subs = segment(_band(stacked_repeated_header_pdf, tmp_path))
    assert len(subs) == 2
    # each stack starts with the header, not a fused body
    assert all(tuple(w.text for w in s.lines[0].words) == ("Analyte", "Value", "Unit") for s in subs)


def test_single_tables_never_split(tmp_path):
    # THE invariant — every existing single table segments to exactly one region
    for maker in (simple_table_pdf, pivoted_table_pdf, all_text_table_pdf,
                  crosstab_table_pdf, row_grouped_table_pdf, transposed_table_pdf):
        assert len(segment(_band(maker, tmp_path))) == 1, maker.__name__


def test_multi_table_ambiguous(tmp_path):
    assert is_multi_table_ambiguous(_band(record_plus_stub_hier_pdf, tmp_path)) is True


def test_crosstab_not_ambiguous(tmp_path):
    assert is_multi_table_ambiguous(_band(crosstab_table_pdf, tmp_path)) is False
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_segment.py -q -k "segments_to or never_split or ambiguous"`
Expected: FAIL (ImportError on `segment`).

- [ ] **Step 3: Implement**

Append to `src/iladub/etkl/segment.py`:

```python
def segment(band: Band) -> list[Band]:
    """Recursively split a band into single-table sub-bands. Vertical (repeated
    header) first, then horizontal (certified gutter); returns [band] when no
    certified cut exists. Never splits a single table (certification guarantees it)."""
    reps = find_repeated_header(band)
    if reps:
        cuts = [0] + reps + [len(band.lines)]
        out: list[Band] = []
        for a, z in zip(cuts, cuts[1:]):
            grp = band.lines[a:z]
            if grp:
                out.extend(segment(_band_from_lines(grp)))
        return out
    cut = find_table_gutter(band)
    if cut is not None:
        words = [w for ln in band.lines for w in ln.words]
        left = [w for w in words if (w.x0 + w.x1) / 2.0 < cut]
        right = [w for w in words if (w.x0 + w.x1) / 2.0 >= cut]
        return segment(_band_from_words(left)) + segment(_band_from_words(right))
    return [band]


def is_multi_table_ambiguous(band: Band) -> bool:
    """True iff there is a genuine second table that segment could not cleanly split:
    a widest full-height gutter where the left is a valid table and the right has its
    OWN stub, yet the pair is not both-RECORD (so find_table_gutter declined). The
    cross-tab is excluded because its right half is data-only (has_own_stub False)."""
    if find_repeated_header(band) or find_table_gutter(band) is not None:
        return False                    # cleanly splittable — not ambiguous
    got = _widest_gutter_cut(band)
    if got is None:
        return False
    _, left, right = got
    lk = classify(_band_from_words(left)).kind
    return lk is not RegionKind.NON_TABLE and has_own_stub(_band_from_words(right))
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_segment.py -q`
Expected: PASS (all Task 1 + Task 2 tests, including the no-false-positive invariant).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/segment.py tests/etkl/test_segment.py
git commit -m "feat(etkl): segment recursion + is_multi_table_ambiguous (stub asymmetry)"
```

---

### Task 3: wire the segmentation pass into `compile_tables`

**Files:**
- Modify: `src/iladub/etkl/compile.py`
- Modify: `src/iladub/etkl/__init__.py`
- Test: `tests/etkl/test_closing_slice.py`

**Interfaces:**
- Consumes: `segment.segment`, `segment.is_multi_table_ambiguous`.
- Produces: `compile_tables` compiles each segmented sub-table; a side-by-side page yields multiple table-holons; an ambiguous multi-table band escalates `MULTI_TABLE_AMBIGUOUS`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_closing_slice.py`:

```python
def test_side_by_side_page_compiles_two_tables(tmp_path):
    from tests.etkl.fixtures import side_by_side_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "sxs.pdf"; side_by_side_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.RecordTable))) == 2   # was 1 fused
    assert report.score == 1.0


def test_stacked_repeated_header_compiles_two(tmp_path):
    from tests.etkl.fixtures import stacked_repeated_header_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "stk.pdf"; stacked_repeated_header_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.RecordTable))) == 2


def test_multi_table_ambiguous_escalates(tmp_path):
    from tests.etkl.fixtures import record_plus_stub_hier_pdf
    from iladub.etkl.holon import ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "amb.pdf"; record_plus_stub_hier_pdf(str(p))
    report = compile_tables(str(p))
    rationales = {str(o) for s in report.graph.subjects(RDF.type, ILADUB.CandidateConcept)
                  for o in report.graph.objects(s, DEC.rationale)}
    assert "MULTI_TABLE_AMBIGUOUS" in rationales


def test_crosstab_still_single_table(tmp_path):
    # regression: the cross-tab is neither split nor escalated
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.HierarchicalTable))) == 1
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_closing_slice.py -q -k "side_by_side or stacked_repeated or multi_table"`
Expected: FAIL — currently the side-by-side fuses to 1 RecordTable, the stacked fuses to 1, no MULTI_TABLE_AMBIGUOUS.

- [ ] **Step 3: Wire the pass in `compile.py`**

In `compile_tables`, replace the band iteration setup. The current lines:

```python
    bands = detect_bands(text_lines(extract_words(pdf_path, page_number)))
    graph = Graph()
    ...
    for idx, band in enumerate(bands):
        region = classify(band)
        ascii_view = render_ascii(band)
```

become:

```python
    raw_bands = detect_bands(text_lines(extract_words(pdf_path, page_number)))
    from .segment import segment, is_multi_table_ambiguous
    bands = [sub for band in raw_bands for sub in segment(band)]
    graph = Graph()
    ...
    for idx, band in enumerate(bands):
        ascii_view = render_ascii(band)
        if is_multi_table_ambiguous(band):
            cand_uri = URIRef(f"{_DOC}#region{idx}")
            escalate_region(graph, cand_uri, _DOC, ascii_view, "MULTI_TABLE_AMBIGUOUS",
                            TAB.HierarchicalTable, 0.4)
            escalated_total += sum(len(ln.words) for ln in band.lines)
            reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                        "MULTI_TABLE_AMBIGUOUS", str(TAB.HierarchicalTable), ascii_view))
            continue
        region = classify(band)
```

(Keep the rest of the loop body — the `NON_TABLE` / `RECORD_TABLE` / `UNSUPPORTED_TABLE` handling — exactly as it is. Only the band list is now segmented, and the ambiguous gate runs first. `render_ascii` moves one line up so it is available for the escalation branch; verify it is not referenced before that point.)

- [ ] **Step 4: Update `__init__.py` exports**

Add `from .segment import segment, find_table_gutter, find_repeated_header, has_own_stub, is_multi_table_ambiguous` and append their names to `__all__`.

- [ ] **Step 5: Run the closing tests + full suite**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — the four new tests, and every prior test (each single-table fixture still compiles as one table; the vertically-gapped multi-table page still yields its regions; segmentation of a single-table band is a no-op).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py src/iladub/etkl/__init__.py tests/etkl/test_closing_slice.py
git commit -m "feat(etkl): segment the page before classify — compile each sub-table, escalate ambiguous"
```

---

### Task 4: showcase Part H + canvas increment 7

**Files:**
- Modify: `demo/etkl_demo_data.py` (add `multi_table_report_pdf`)
- Modify: `demo/etkl_1a_showcase.ipynb` (Part H)
- Modify: `docs/loops/2026-07-05-table-holon-loop.md` (increment 7)

**Interfaces:** Consumes the shipped `compile_tables` behaviour. No new code.

- [ ] **Step 1: Add the demo fixture**

Append `multi_table_report_pdf(path)` to `demo/etkl_demo_data.py`: a single page holding TWO side-by-side record tables (e.g. a lab panel beside an inventory list), spaced with a wide full-height gutter, staying one detect_bands band (so segmentation is what separates them). Return a truth dict. Verify empirically it compiles to two tables (Step 3 confirms).

- [ ] **Step 2: Insert Part H cells**

After Part G's cells and before the closing "ladder" markdown, insert three cells:
1. **Markdown intro** — "Part H · one page, many tables — segmentation", explaining `detect_bands` is 1-D so it fused side-by-side/stacked tables; `segment` proposes cuts and certifies each by re-running the classifiers; and the safety property — a single table (the cross-tab) is provably never split.
2. **Code (render original first)** — write the multi-table PDF via `data.multi_table_report_pdf`, render with `viz.render_page`/`viz.show_page`.
3. **Code (compile read-out)** — `compile_tables`, then show the count and headers of the recovered tables:

```python
from iladub.etkl.holon import TAB
from rdflib import RDF
mt = compile_tables(mt_pdf)
tables = list(mt.graph.subjects(RDF.type, TAB.RecordTable)) + list(mt.graph.subjects(RDF.type, TAB.HierarchicalTable))
print(f"score = {mt.score:.2f}   |   tables recovered from ONE page: {len(tables)}")
for t in tables:
    hdrs = sorted(str(o) for s in mt.graph.objects(t, TAB.hasHeaderNode)
                  for lc in mt.graph.objects(s, TAB.hasLabel)
                  for o in mt.graph.objects(lc, TAB.cellText))
    print("  table headers:", hdrs)
print()
print("detect_bands is 1-D (vertical only) and fused these; segment splits the page — horizontally")
print("and vertically — and compiles each, and provably never splits a single table (the cross-tab).")
```

Then update the closing "ladder" markdown to mention page segmentation as the pass that feeds clean single-table regions to the whole ladder; refresh the "next rungs" (key-value, stacked-different-headers, multi-band re-grouping, signal-tagging).

- [ ] **Step 3: Re-run the notebook; verify zero errors**

Run:
```bash
PYTHONPATH="$PWD/src:$PWD/demo" jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 --ExecutePreprocessor.kernel_name=python3 \
  demo/etkl_1a_showcase.ipynb
```
Verify (JSON scan): 0 errors, Part H renders the multi-table PDF, and prints `tables recovered from ONE page: 2` with the two headers.

- [ ] **Step 4: Canvas increment 7**

In `docs/loops/2026-07-05-table-holon-loop.md`, add increment 7 (`[x]`) — multi-table page segmentation: `segment` splits fused side-by-side (certified gutter) and stacked-repeated-header regions and compiles each, escalates `MULTI_TABLE_AMBIGUOUS`, and provably never splits a single table (the no-false-positive invariant); note the documented limits (non-record side-by-side, different-header stacks). Remove nothing from the field-of-possibles that isn't done (segmentation was not previously listed; optionally note "multi-band re-grouping" as the remaining banding gap).

- [ ] **Step 5: Commit**

```bash
git add demo/etkl_demo_data.py demo/etkl_1a_showcase.ipynb docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop7): showcase Part H (multi-table segmentation) + canvas increment 7"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §3 proposers → Task 1; §3 recursion + ambiguity → Task 2; §3 pipeline wiring + §6 closing proof → Task 3; §7 showcase → Task 4. §6 tests distributed to the tasks that own them; the §4 no-false-positive invariant is `test_single_tables_never_split` (Task 2) + `test_find_table_gutter_none_on_singles` (Task 1).
- **Type consistency:** `segment(band) -> list[Band]`, `find_table_gutter(band) -> float | None`, `find_repeated_header(band) -> list[int]`, `has_own_stub(band) -> bool`, `is_multi_table_ambiguous(band) -> bool` used identically across tasks; `_band_from_words`/`_band_from_lines` shared.
- **No-regression made explicit:** Task 1 + Task 2 pin the single-table invariant (incl. the cross-tab) before any wiring; Task 3 Step 5 runs the full suite; the compile loop body is unchanged except the segmented band list + the leading ambiguous gate.
- **Placeholder scan:** none — every code step carries exact content. (Task 4 Step 1's demo fixture is described in prose because it mirrors the Task 1 `side_by_side_pdf` and is verified by the re-run; the compile-readout cell is given verbatim.)
- **Empirical grounding:** every discriminator (both-RECORD gutter, repeated-header, `has_own_stub`, cross-tab exclusion) is confirmed by the 2026-07-09 probes recorded in Global Constraints.
