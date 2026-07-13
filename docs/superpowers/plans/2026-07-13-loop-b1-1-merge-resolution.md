# Loop B1.1 — Merge Resolution (centering-bounded) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close a silent-wrong class in merged-header resolution — a header centered over *part* of the columns is no longer extended over columns its ink does not cover; the label's center position now bounds the span, and an unresolvable residue escalates `MERGE_AMBIGUOUS` instead of asserting a wrong tiling.

**Architecture:** Thread each spanning header cell's ink center (`center_x`) onto `HeaderNode`; replace `repair_coverage`'s greedy orphan-absorption with a **closest-ink-center run selection** (a spanning node resolves to the contiguous run of available columns whose x-midpoint is nearest its ink center); add an explicit **centering oracle** (`merge_tiling_ok`) that escalates when the resolved coarse layout is not center-consistent or overlaps.

**Tech Stack:** Python 3, rdflib, pyshacl, reportlab (synthetic PDF fixtures), pytest. All geometry in PDF points. No new dependency.

## Global Constraints

- **Branch:** `etkl-b1-1-merge-resolution` (already created off `main` @ `a75e359`). Do all work here.
- **Approved spec:** `docs/superpowers/specs/2026-07-12-loop-b1-1-merge-resolution-design.md`. Every task's requirements implicitly include it.
- **No overfitting / general fixes (ZERO TOLERANCE):** the centering tolerance is expressed in units of the local column pitch (half a pitch), never a constant tuned to a fixture. The resolution uses the ink-center oracle, not tuned magic numbers.
- **Out of scope — do NOT touch:** `is_matrix_candidate` and `infer_column_tree_by_proximity` in `src/iladub/etkl/matrix.py` (the deferred nameless-pivot/matrix loop owns those — see `docs/superpowers/specs/2026-07-12-nameless-pivot-from-pdf-deferred.md`); the row-header axis (`rowheaders.py`); B1.2 un-wrap; B1.3 alignment.
- **No-regression contract:** these shipped fixtures MUST keep their exact recovered column trees — `pivoted_report_pdf` ("Current Visit"→[1,2,3], "Prior Visit"→[4,5,6]); `denormalized_report_pdf` / `region_pivot_pdf` ("Region"→[1,2,3,4]); `crosstab_report_pdf` (matrix proximity path, structurally untouched — Q1→[1,2,3], Q2→[4,5,6]); `row_grouped_report_pdf`, `multi_table_report_pdf`, transposed, flat record — unaffected. The full suite (`.venv/bin/pytest tests/ -q`, currently **332 passed / 5 skipped**) is the gate at each task.
- **Serialization/validation:** SHACL via pyshacl, `inference="rdfs"`, `advanced=True` (already wired in `compile_tables`). Every axiom ships a worked example that conforms AND a negative test that must fail.
- **Commits:** end each commit message body with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Run tests with the project venv:** `.venv/bin/pytest` (cwd = repo root).

---

## File structure

- `tests/etkl/fixtures.py` — add `partial_merge_report_pdf` (positive gap fixture) and `offcenter_merge_report_pdf` (negative escalation fixture). Existing reportlab-canvas style, returns a ground-truth dict.
- `tests/etkl/test_merge_resolution.py` — **new**; all B1.1 behavior tests (positive resolution, no-regression column-tree snapshot, negative escalation, oracle unit).
- `src/iladub/etkl/headers.py` — add `center_x` to `HeaderNode`; set it in `infer_header_tree`; add `_median_pitch`, `_centered_run`, rewrite `repair_coverage`; add `merge_tiling_ok`.
- `src/iladub/etkl/compile.py` — in the hierarchical branch, gate assertion on `merge_tiling_ok`; escalate `MERGE_AMBIGUOUS` otherwise.

---

### Task 1: Fixtures + no-regression column-tree snapshot (green baseline)

**Files:**
- Modify: `tests/etkl/fixtures.py` (add `partial_merge_report_pdf`)
- Create: `tests/etkl/test_merge_resolution.py`

**Interfaces:**
- Consumes: `iladub.etkl.compile_tables`; `iladub.etkl.holon.TAB`; existing fixtures `pivoted_table_pdf`/`pivoted_report_pdf`, `region_pivot_pdf`, `crosstab_table_pdf` (in `tests/etkl/fixtures.py`).
- Produces: `partial_merge_report_pdf(path: str) -> dict`; helper `column_tree(graph, table)` in the test module returning `{label: sorted([col ints])}` for spanning header nodes.

- [ ] **Step 1: Add the `partial_merge_report_pdf` fixture**

In `tests/etkl/fixtures.py`, append (match the file's existing reportlab style — `from reportlab.pdfgen import canvas`, `PAGE_H`):

```python
def partial_merge_report_pdf(path: str) -> dict:
    """A partial merge: a 'WIDE' parent CENTERED over three leaf columns (Val,Unit,Flag)
    beside a standalone fourth column 'Note' that has NO parent group. WIDE's ink
    center (x=250) is the midpoint of cols 1-3, NOT of cols 1-4 (x=300). The
    centering convention therefore reads WIDE=[1,2,3] with col 4 a parentless leaf;
    the pre-B1.1 greedy repair wrongly folds col 4 under WIDE ([1,2,3,4]).

    CRITICAL — the data columns are MIXED-TYPE (Val numeric; Unit/Flag/Note text) so
    stub_data_split() returns None and the region routes through the HIERARCHICAL path
    (repair_coverage), the seam B1.1 fixes. An all-numeric body would instead trip
    is_matrix_candidate=True and route through matrix.py's Voronoi (the deferred
    nameless-pivot loop's territory — out of scope here). Verified: mixed body -> htable."""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((leaves[0] + leaves[2]) / 2.0, PAGE_H - 90.0, "WIDE")  # center=250 over cols 1-3
    for x, n in zip(leaves, ["Val", "Unit", "Flag", "Note"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["10", "mg", "LOW", "ok"]),
                                   ("R2", ["50", "kg", "HIGH", "no"])]):  # mixed types -> hierarchical path
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, k)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "WIDE", "parent_cols": [1, 2, 3], "standalone_col": 4,
            "leaves": ["Val", "Unit", "Flag", "Note"], "stub": "Key"}
```

- [ ] **Step 2: Write the no-regression snapshot test (green now)**

Create `tests/etkl/test_merge_resolution.py`:

```python
"""Loop B1.1 — centering-bounded merge resolution. Behavior + no-regression + escalation."""
import os
import tempfile

from rdflib import RDF

from iladub.etkl import compile_tables
from iladub.etkl.holon import TAB, ILADUB
from tests.etkl import fixtures


def _compile(fixture_fn):
    path = os.path.join(tempfile.mkdtemp(), "t.pdf")
    fixture_fn(path)
    return compile_tables(path)


def column_tree(g, t):
    """{label: sorted(col ints)} for every header node of table t that covers columns."""
    def _label(h):
        return " ".join(str(x) for lc in g.objects(h, TAB.hasLabel)
                        for x in g.objects(lc, TAB.cellText))

    def _cols(h):
        return sorted(int(str(c).rsplit("-c", 1)[-1]) for c in g.objects(h, TAB.coversColumn))

    out = {}
    for h in g.objects(t, TAB.hasHeaderNode):
        cols = _cols(h)
        if cols:
            out[_label(h)] = cols
    return out


def _tree_of(fixture_fn):
    rep = _compile(fixture_fn)
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    return column_tree(rep.graph, t)


def test_no_regression_pivoted():
    tree = _tree_of(fixtures.pivoted_table_pdf)
    assert tree["Current Visit"] == [1, 2, 3]
    assert tree["Prior Visit"] == [4, 5, 6]


def test_no_regression_region_pivot():
    tree = _tree_of(fixtures.region_pivot_pdf)
    assert tree["Region"] == [1, 2, 3, 4]


def test_no_regression_crosstab():
    tree = _tree_of(fixtures.crosstab_table_pdf)
    assert tree["Q1"] == [1, 2, 3]
    assert tree["Q2"] == [4, 5, 6]
```

- [ ] **Step 3: Run the snapshot test — verify GREEN (locks current behavior)**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py -q`
Expected: PASS (3 passed). If the exact spans differ, correct the asserted values to the real current output (capture with a one-off print) — these three MUST reflect today's behavior so Task 3 cannot silently regress them.

- [ ] **Step 4: Run the full suite — verify still green**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (was 332 passed / 5 skipped; now +3 → 335 passed / 5 skipped).

- [ ] **Step 5: Commit**

```bash
git add tests/etkl/fixtures.py tests/etkl/test_merge_resolution.py
git commit -m "test(b1.1): partial-merge fixture + no-regression column-tree snapshot"
```

---

### Task 2: Thread the label ink center onto `HeaderNode` (mechanical, no behavior change)

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`HeaderNode`, `infer_header_tree`)

**Interfaces:**
- Consumes: nothing new.
- Produces: `HeaderNode(level, covers, text, parent, center_x=None)` — a new trailing optional field `center_x: float | None`. `infer_header_tree` sets `center_x = (cell.x0 + cell.x1) / 2.0` for every built node.

- [ ] **Step 1: Add the optional `center_x` field to `HeaderNode`**

In `src/iladub/etkl/headers.py`, change the dataclass (keep it frozen, add a trailing default so every existing constructor call stays valid):

```python
@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None
    center_x: float | None = None   # label ink center (pt); None when geometry is unavailable
```

- [ ] **Step 2: Populate `center_x` when building nodes in `infer_header_tree`**

In `infer_header_tree`, the node-build loop currently reads:

```python
    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            covers = _covers_for_cell(cell, b)
            nodes.append(HeaderNode(lvl, covers, cell.text, None))
```

Replace the append with (compute the ink center from the cell's x-extent):

```python
    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            covers = _covers_for_cell(cell, b)
            cx = (cell.x0 + cell.x1) / 2.0
            nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))
```

Also, in the final parent-linking loop, preserve `center_x` when rebuilding nodes. The loop currently ends with:

```python
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx))
```

Replace with:

```python
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx, n.center_x))
```

- [ ] **Step 3: Run the full suite — verify still green (center_x unused so far)**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (335 passed / 5 skipped). No behavior change — `center_x` is populated but not yet read.

- [ ] **Step 4: Commit**

```bash
git add src/iladub/etkl/headers.py
git commit -m "feat(b1.1): thread label ink center (center_x) onto HeaderNode"
```

---

### Task 3: Centering-bounded `repair_coverage` (closes the gap)

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`repair_coverage`, add `_median_pitch`, `_centered_run`; update the call in `infer_header_tree`)
- Modify: `tests/etkl/test_merge_resolution.py` (add the positive resolution test)

**Interfaces:**
- Consumes: `HeaderNode.center_x` (Task 2); `LeafGrid` (has `.boundaries`, `.ncols`).
- Produces: `repair_coverage(nodes: list[HeaderNode], grid: LeafGrid) -> list[HeaderNode]` (signature changes from `(nodes, ncols)` to `(nodes, grid)`); helpers `_median_pitch(b) -> float`, `_centered_run(center_x, avail, b, must_include) -> tuple[int, ...]`.

- [ ] **Step 1: Write the failing positive test**

Append to `tests/etkl/test_merge_resolution.py`:

```python
def test_partial_merge_resolves_by_centering():
    """WIDE centered over cols 1-3 must resolve to [1,2,3]; col 4 is a parentless
    leaf 'Note' — NOT folded under WIDE (the pre-B1.1 silent-wrong [1,2,3,4])."""
    tree = _tree_of(fixtures.partial_merge_report_pdf)
    assert tree["WIDE"] == [1, 2, 3], f"WIDE must stop at its centered span, got {tree['WIDE']}"
    # col 4 is covered only by its own leaf header 'Note' (a parentless leaf), never by WIDE
    assert 4 not in tree["WIDE"]
    assert tree.get("Note") == [4]
```

- [ ] **Step 2: Run it — verify it FAILS (proves the gap)**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py::test_partial_merge_resolves_by_centering -q`
Expected: FAIL — `WIDE` is `[1, 2, 3, 4]` (greedy repair absorbed col 4).

- [ ] **Step 3: Add the centering helpers to `headers.py`**

Insert above `repair_coverage` (no new imports needed — `_span_center` uses only `b`):

```python
def _median_pitch(b: Sequence[float]) -> float:
    """Median data-column width (pitch) in points — the gutter-relative unit for the
    centering tolerance (NOT a fixture-tuned constant). Columns are b[i]..b[i+1];
    column 0 is the stub and is excluded."""
    widths = sorted(b[i + 1] - b[i] for i in range(1, len(b) - 1))
    if not widths:
        return (b[-1] - b[0]) if len(b) >= 2 else 1.0
    return widths[len(widths) // 2]


def _span_center(run: Sequence[int], b: Sequence[float]) -> float:
    """The x-center of a contiguous column run = the ENDPOINT midpoint of its x-range,
    (b[run[0]] + b[run[-1]+1]) / 2 — the true visual center of the span (spec §4).

    (A median of per-column midpoints was tried and REJECTED: for unequal-width columns
    the median collapses to the middle column's midpoint, which sits far from the visual
    center, so the resolver picks a too-narrow run and silently drops a flanking column.
    The endpoint midpoint is the geometric center for any column widths.)"""
    return (b[run[0]] + b[run[-1] + 1]) / 2.0


def _centered_run(center_x: float, avail: set[int], b: Sequence[float],
                  must_include: set[int]) -> tuple[int, ...]:
    """The contiguous column run [lo..hi] (lo >= 1) that (a) lies entirely within
    `avail`, (b) contains every column in `must_include` (the node's ink columns),
    and (c) is best-centered on the label ink center by ENDPOINT midpoint (`_span_center`).

    Selection: among the qualifying runs, take those whose center is within a quarter of
    the median column pitch of the closest run's center (a TIE-BAND: runs that close are
    indistinguishable given gutter-recovery noise), and pick the WIDEST of them (then
    closest, then leftmost). The tie-band + widest recovers the full span for a short
    centered label (e.g. a single ink column tied with its 3-column span -> the span),
    while the quarter-pitch bound stops one column short of over-absorbing an adjacent
    standalone column (whose center is a half-pitch away). The band is gutter-relative
    (a fraction of the measured pitch), NOT a constant tuned to any fixture.

    Returns () if none qualifies (e.g. must_include is empty or not contiguous in avail)."""
    n = len(b) - 1
    cands: list[tuple[tuple[int, ...], float, int]] = []   # (run, |center-ink|, width)
    for lo in range(1, n):
        for hi in range(lo, n):
            run = tuple(range(lo, hi + 1))
            run_set = set(run)
            if not run_set <= avail:
                continue
            if not must_include <= run_set:
                continue
            cands.append((run, abs(_span_center(run, b) - center_x), hi - lo))
    if not cands:
        return ()
    best_d = min(d for _, d, _ in cands)
    band = 0.25 * _median_pitch(b)
    near = [c for c in cands if c[1] - best_d <= band]
    near.sort(key=lambda z: (-z[2], z[1], z[0][0]))        # widest, then closest, then leftmost
    best_run = near[0][0]
    return best_run
```

- [ ] **Step 4: Rewrite `repair_coverage` to be centering-bounded**

Replace the entire body of `repair_coverage` (keep the name; change the second parameter from `ncols: int` to `grid: LeafGrid`):

```python
def repair_coverage(nodes: list[HeaderNode], grid: LeafGrid) -> list[HeaderNode]:
    """Resolve each coarse (non-leaf) spanning node to the contiguous run of AVAILABLE
    columns (its own + orphans, never another node's) whose x-midpoint is closest to
    the node's label ink center. This applies the centering (Merge & Center) convention
    consistently: a short label centered over its full span still recovers that span
    (Region, Q-groups), while a label centered over only PART of the columns stops at
    its centered run instead of greedily absorbing the neighbour (the B1.1 fix).

    Falls back to the pre-B1.1 additive greedy extension for any node lacking geometry
    (`center_x is None`) so non-geometric callers are unchanged.
    """
    if not nodes:
        return nodes
    b = grid.boundaries
    ncols = grid.ncols
    out = list(nodes)
    max_level = max(n.level for n in out)
    for lvl in range(max_level):                      # non-leaf levels only
        for i, n in enumerate(out):
            if n.level != lvl:
                continue
            level_cols: set[int] = set()
            for m in out:
                if m.level == lvl:
                    level_cols |= set(m.covers)
            orphans = {c for c in range(1, ncols) if c not in level_cols}
            avail = set(n.covers) | orphans
            if n.center_x is not None and n.covers:
                run = _centered_run(n.center_x, avail, b, must_include=set(n.covers))
                if run and set(run) != set(n.covers):
                    out[i] = replace(n, covers=tuple(run))
            else:
                # legacy additive greedy extension (no geometry available)
                for c in sorted(orphans):
                    if n.covers and (max(n.covers) == c - 1 or min(n.covers) == c + 1):
                        out[i] = replace(out[i], covers=tuple(sorted(set(out[i].covers) | {c})))
    return out
```

- [ ] **Step 5: Update the call site in `infer_header_tree`**

The line currently reads:

```python
    nodes = repair_coverage(nodes, grid.ncols)   # fill short-parent-over-wide-span coverage gaps
```

Replace with:

```python
    nodes = repair_coverage(nodes, grid)   # centering-bounded span resolution (B1.1)
```

- [ ] **Step 6: Run the positive test — verify it PASSES**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py::test_partial_merge_resolves_by_centering -q`
Expected: PASS — `WIDE == [1, 2, 3]`, `Note == [4]`.

- [ ] **Step 6b: Add the unequal-width no-silent-wrong regression fixture + test**

This is the case a median-of-midpoints statistic silently mis-resolved (dropping a flanking
column). It MUST resolve to the full span `[1,2,3]` (or escalate) — never a proper subset.

In `tests/etkl/fixtures.py`:

```python
def unequal_width_merge_report_pdf(path: str) -> dict:
    """A merged 'GROUP' centered over THREE UNEQUAL-WIDTH columns (col 1 narrow & close,
    col 3 wide & far) — the geometry where a median-of-midpoints centering statistic
    silently resolves GROUP to [2,3], dropping col 1. Correct: GROUP spans all three
    ([1,2,3]) by endpoint-center, or the region escalates — never a column-dropping subset.
    Mixed-type body so it routes the hierarchical path."""
    xs = [120.0, 170.0, 330.0]                                   # unequal spacing -> unequal widths
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((xs[0] + xs[2]) / 2.0, PAGE_H - 90.0, "GROUP")   # visual center of the 3-col span
    for x, n in zip(xs, ["V", "U", "D"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(55.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["1", "aa", "xx"]), ("R2", ["2", "bb", "yy"])]):
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(55.0, y, k)
        for x, v in zip(xs, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "GROUP", "data_cols": [1, 2, 3]}
```

In `tests/etkl/test_merge_resolution.py`:

```python
def test_unequal_width_merge_no_silent_wrong():
    """A GROUP centered over unequal-width columns must span the full [1,2,3] (or escalate) —
    NEVER a proper subset that silently drops a flanking column."""
    rep = _compile(fixtures.unequal_width_merge_report_pdf)
    hts = list(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    if not hts:
        # escalated (also acceptable — honest) ; assert it did not assert a wrong span
        return
    tree = column_tree(rep.graph, hts[0])
    grp = tree.get("GROUP")
    assert grp is None or grp == [1, 2, 3], f"GROUP silently dropped a column: {grp}"
```

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py::test_unequal_width_merge_no_silent_wrong -q`
Expected: PASS — `GROUP == [1, 2, 3]` (with the endpoint statistic + tie-band-widest selection).
With the rejected median statistic this test FAILS (`GROUP == [2, 3]`), which is exactly the
silent-wrong it guards against.

- [ ] **Step 7: Run the no-regression tests — verify still GREEN**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py -q`
Expected: PASS (all no-regression snapshots + the new positive test). If `test_no_regression_region_pivot` or `_pivoted` fail, the centering rule mis-resolved a legit full-span label — STOP and fix `_centered_run` (the full-span run's midpoint must win); do not weaken the snapshot.

- [ ] **Step 8: Run the full suite — verify green**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (335 passed / 5 skipped). Any other header/denorm/matrix test regressing is a real regression — investigate, don't silence.

- [ ] **Step 9: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_merge_resolution.py
git commit -m "feat(b1.1): centering-bounded merge resolution — stop greedy orphan absorption"
```

---

### Task 4: Centering oracle + `MERGE_AMBIGUOUS` escalation (negative case)

**Files:**
- Modify: `src/iladub/etkl/headers.py` (add `merge_tiling_ok`)
- Modify: `src/iladub/etkl/compile.py` (gate the hierarchical assertion on the oracle; escalate `MERGE_AMBIGUOUS`)
- Modify: `tests/etkl/fixtures.py` (add `offcenter_merge_report_pdf`)
- Modify: `tests/etkl/test_merge_resolution.py` (negative + oracle-unit tests)

**Interfaces:**
- Consumes: `merge_tiling_ok(tree: tuple[HeaderNode, ...], grid: LeafGrid) -> bool`; `HierRegion.tree`, `HierRegion.grid` (from `classify_hierarchical`); `escalate_region(g, cand_uri, doc_uri, ascii_text, reason, anchor, confidence)` and `render_region_ascii` (already used in `compile.py`).
- Produces: escalation reason string `"MERGE_AMBIGUOUS"`.

- [ ] **Step 1: Add the `merge_tiling_ok` oracle to `headers.py`**

Append to `headers.py`:

```python
def merge_tiling_ok(tree: Sequence[HeaderNode], grid: LeafGrid) -> bool:
    """Centering oracle for the resolved header tree. A spanning (multi-column, non-leaf)
    node is center-consistent iff its resolved span's x-midpoint is within half a column
    pitch of its label ink center. Also rejects any coarse-level column claimed by two
    nodes (overlap). A node without geometry (center_x is None) is not checked here.
    Returns False → the caller escalates MERGE_AMBIGUOUS rather than assert a guess."""
    b = grid.boundaries
    tol = 0.5 * _median_pitch(b)
    has_child = {n.parent for n in tree if n.parent is not None}
    # overlap check per level
    by_level: dict[int, list[int]] = {}
    for n in tree:
        for c in n.covers:
            by_level.setdefault(n.level, []).append(c)
    for cols in by_level.values():
        if len(cols) != len(set(cols)):
            return False                       # two nodes claim the same column at one level
    # centering check for spanning (has-children) nodes with geometry
    for i, n in enumerate(tree):
        if i in has_child and len(n.covers) > 1 and n.center_x is not None:
            mid = _span_center(tuple(sorted(n.covers)), b)   # same statistic the resolver uses
            if abs(mid - n.center_x) > tol:
                return False
    return True
```

- [ ] **Step 2: Add the negative `offcenter_merge_report_pdf` fixture**

In `tests/etkl/fixtures.py`, append:

```python
def offcenter_merge_report_pdf(path: str) -> dict:
    """Ambiguous merge: two SHORT parent labels 'LEFT' (center x=200) and 'RIGHT'
    (center x=300) whose centering claims collide — the centering resolver gives them
    OVERLAPPING spans (LEFT->[1,2,3], RIGHT->[2,3,4]), so no clean tiling exists.
    B1.1 must ESCALATE MERGE_AMBIGUOUS rather than assert an overlapping/arbitrary tiling.

    MIXED-TYPE body (Val numeric; Unit/Flag/Note text) so it routes the HIERARCHICAL
    path (where merge_tiling_ok gates). Controller-verified: this geometry yields
    merge_tiling_ok()==False via the per-level overlap check. (An all-numeric body would
    route matrix.py Voronoi and never reach the oracle.)"""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(200.0, PAGE_H - 90.0, "LEFT")    # center 200 (midpoint of cols 1-2)
    c.drawCentredString(300.0, PAGE_H - 90.0, "RIGHT")   # center 300 (midpoint of cols 1-4) -> claims collide
    for x, n in zip(leaves, ["Val", "Unit", "Flag", "Note"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["10", "mg", "LOW", "ok"]),
                                   ("R2", ["50", "kg", "HIGH", "no"])]):  # mixed -> hierarchical path
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, k)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"labels": ["LEFT", "RIGHT"], "expect": "MERGE_AMBIGUOUS"}
```

- [ ] **Step 3: Write the failing negative + oracle-unit tests**

Append to `tests/etkl/test_merge_resolution.py`:

```python
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import HeaderNode, merge_tiling_ok


def test_offcenter_merge_escalates():
    """An ambiguous two-parent merge must escalate MERGE_AMBIGUOUS — asserting nothing —
    rather than fabricate a tiling."""
    rep = _compile(fixtures.offcenter_merge_report_pdf)
    reasons = {str(o) for s in rep.graph.subjects(RDF.type, ILADUB.CandidateConcept)
               for o in rep.graph.objects(s, __import__("iladub.etkl.holon", fromlist=["DEC"]).DEC.rationale)}
    assert any("MERGE_AMBIGUOUS" in r for r in reasons), f"expected MERGE_AMBIGUOUS, got {reasons}"
    # nothing asserted as a hierarchical table for this ambiguous region
    # (a genuinely ambiguous merge is escalated, not compiled)


def test_merge_tiling_ok_accepts_centered_full_span():
    b = (55.0, 100.0, 200.0, 300.0, 400.0, 500.0)      # stub + 5 data cols (0..5)
    grid = LeafGrid(b, 5, 100.0, 1.0)
    parent = HeaderNode(0, (1, 2, 3, 4), "P", None, center_x=(b[1] + b[5]) / 2.0)  # centered on full span
    leaf = HeaderNode(1, (1,), "a", 0, center_x=(b[1] + b[2]) / 2.0)
    assert merge_tiling_ok((parent, leaf), grid) is True


def test_merge_tiling_ok_rejects_offcenter_overextension():
    b = (55.0, 100.0, 200.0, 300.0, 400.0, 500.0)
    grid = LeafGrid(b, 5, 100.0, 1.0)
    # parent's ink center is over cols 1-2 (x=200) but its span claims 1-4 (mid x=300): off-center
    parent = HeaderNode(0, (1, 2, 3, 4), "P", None, center_x=200.0)
    leaf = HeaderNode(1, (1,), "a", 0, center_x=150.0)
    assert merge_tiling_ok((parent, leaf), grid) is False
```

Confirm the actual `LeafGrid` field order/name (`from iladub.etkl.grid import LeafGrid`; it is `LeafGrid(boundaries, ncols, pitch, confidence)`); adjust the constructor call if the dataclass signature differs.

- [ ] **Step 4: Run the oracle-unit tests — verify they FAIL (function not wired / negative not escalating yet)**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py -k "tiling_ok or offcenter" -q`
Expected: `test_offcenter_merge_escalates` FAILS (no MERGE_AMBIGUOUS yet); the two `merge_tiling_ok` unit tests PASS once the import resolves (the function exists from Step 1). If the negative fixture actually compiles a (wrong) table, that failure is the point — Step 5 wires the gate.

- [ ] **Step 5: Gate the hierarchical assertion on the oracle in `compile.py`**

In `src/iladub/etkl/compile.py`, the hierarchical branch currently reads (around the `classify_hierarchical` call):

```python
                from .hierarchical import classify_hierarchical
                from .holon import assert_hier_region
                hreg = classify_hierarchical(band)
                if hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    n = assert_hier_region(graph, hreg, band, table_uri, _DOC, page_number)
```

Insert the oracle gate so an ambiguous merge escalates instead of asserting. Replace `if hreg is not None:` with:

```python
                from .headers import merge_tiling_ok
                if hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "MERGE_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "MERGE_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
                elif hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    n = assert_hier_region(graph, hreg, band, table_uri, _DOC, page_number)
```

Verify against the real file: keep the rest of the original `if hreg is not None:` body (the `tokens = ...`, `asserted_total += n`, `reports.append(...)`) inside the `elif` branch exactly as it was; only the escalation `if` is new. Confirm `escalate_region`, `RegionReport`, `ascii_view`, and `TAB` are already in scope in this branch (they are — used by the sibling `MATRIX_AMBIGUOUS` / `KIND_NOT_SUPPORTED` escalations at lines ~175 and ~202).

- [ ] **Step 6: Run the negative + oracle tests — verify PASS**

Run: `.venv/bin/pytest tests/etkl/test_merge_resolution.py -k "tiling_ok or offcenter" -q`
Expected: PASS (escalation fires; oracle units green). If the `offcenter` fixture does not actually trigger the oracle (e.g. it compiles cleanly), adjust the fixture's two label x-positions so both ink centers land in the same inter-column zone — the goal is a genuinely center-ambiguous overlap, not a tuned trip-wire; document the geometry in the fixture docstring.

- [ ] **Step 7: Run the full suite — verify green (no legit table now escalates)**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (was 335; +2 fixtures/tests net → ~337 passed / 5 skipped). Critically, `test_no_regression_*` and every existing hierarchical/matrix/denorm test still pass — a legit centered merge must NEVER escalate.

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/headers.py src/iladub/etkl/compile.py tests/etkl/fixtures.py tests/etkl/test_merge_resolution.py
git commit -m "feat(b1.1): centering oracle + MERGE_AMBIGUOUS escalation for ambiguous merges"
```

---

## Self-review

**Spec coverage:** §2 gap → Task 1 fixture + Task 3 positive test. §3 axiom (centering-bounded span) → Task 3 `_centered_run`/`repair_coverage`. §4 oracle (re-tiling existing SHACL + new centering; escalate residue) → Task 4 `merge_tiling_ok` + `MERGE_AMBIGUOUS`. §5 approach (fix-in-place + thread ink center + oracle safety net) → Tasks 2–4. §6 out-of-scope (matrix untouched, row axis, B1.2/B1.3) → Global Constraints. §7 no-regression contract → Task 1 snapshot + Task 3/4 gates. §8 test plan (probe-first fixture, negative escalate, no-regression, oracle unit) → Tasks 1/3/4. §9 source-ownership (no new authored RDF beyond an escalation reason reusing `iladub:CandidateConcept`) → Task 4 uses existing `escalate_region`.

**Placeholder scan:** none — every code step has complete code; the two "adjust if the real signature/geometry differs" notes (LeafGrid constructor, offcenter x-positions) are verification instructions against the live code, not deferred content.

**Type consistency:** `HeaderNode(level, covers, text, parent, center_x=None)` used consistently (Tasks 2–4). `repair_coverage(nodes, grid)` new signature and its sole caller updated in the same task (Task 3, Steps 4–5). `merge_tiling_ok(tree, grid)` defined Task 4 Step 1, consumed Task 4 Steps 3/5. `_centered_run`/`_median_pitch` defined and used within Task 3. `LeafGrid(boundaries, ncols, pitch, confidence)` — confirm at Task 4 Step 3.
