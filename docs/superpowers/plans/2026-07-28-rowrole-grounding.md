# Grounding the row-role proposal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the NEURAL row-role proposer the band-local structural evidence a human reader uses — what each fragment would merge into, and how few cells a row has against how many columns the table has — without changing anything that disposes its answer.

**Architecture:** Two small, independent changes. `rowrole.row_role_context` gains three reported keys (pure structural reads, no new decision). `baml_src/header_rowrole.baml` and `propose.BamlRowRoleProposer` grow matching parameters. `build_row_reading`, both SHACL oracles, the promotion path, the no-search rule and every refusal path are **untouched**.

**Tech Stack:** Python 3 (`src/iladub/etkl/`), BAML (`baml_src/`), pytest.

**Spec:** `docs/superpowers/specs/2026-07-28-rowrole-grounding-design.md` (read §2 before starting — it explains why this is evidence and not a rule).

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from the repo root, `/Volumes/WD Green/dev/git/iladub`.

**Baseline:** 584 passed, 5 skipped (Loop C close, `main` at `1b7ba80`). Branch `iladub-rowrole-grounding` is already checked out.

## Global Constraints

Copied from the spec's §5 gate. **Every task's requirements implicitly include this section.**

- **Evidence is reported, never acted on.** No Python may branch on the new keys to select or override a role. `row_role_context` stays a pure structural read; `build_row_reading` still only executes or refuses a given vector.
- **No behaviour change.** `build_row_reading`, `resolve_header_row_roles`, `emit_reading_evidence`, both oracles, and every refusal path must be byte-identical in behaviour. Only what the proposer *sees* changes.
- **No fabricated evidence.** Do **not** report either cover set on the parent path. `_covers_for_cell` symmetrizes around a cell's centre column and so can over-span (measured: 5 of 10 GrainCorp non-leaf cells widen beyond their ink columns); for `Date of Grain` it returns just the ink column, and it is the DOWNSTREAM `repair_coverage`/`_centered_run` run extension (`headers.py`), one stage later, that widened it to `covers 1..12`. Reporting either would hand the model a derived span in place of evidence. Only exact, underived values.
- **No tuned constant, no new numeric literal** encoding a decision. Counts and string concatenation only.
- **Band-local only.** No reading of neighbouring bands; the band remains the closure boundary.
- **Legality gates admission, never confidence.** Unchanged — introduce no comparison on confidence.
- **Placement must reuse `_column_containing`**, never `regions.column_of` (which clamps out-of-range x onto the last column — the Critical defect fixed in Loop C).
- **Never weaken an existing test.** The full suite stays green.

---

## File Structure

| File | Responsibility |
| --- | --- |
| `src/iladub/etkl/rowrole.py` | **Modify** — `row_role_context` reports three new keys. No other function changes. |
| `tests/etkl/test_rowrole_grounding.py` | **Create** — the context-shape, out-of-grid, and agreement tests. |
| `baml_src/header_rowrole.baml` | **Modify** — three new function parameters; two new prompt sentences. |
| `src/iladub/etkl/propose.py` | **Modify** — `BamlRowRoleProposer` forwards the three new keys. |
| `tests/etkl/test_rowrole_proposer.py` | **Modify** — extend the existing BAML/Python arity check. |

Task order: 1 → 2. Task 2 consumes Task 1's context keys.

---

## Verified expected values

Probed against the current code during planning — **assert these, do not re-derive them.**

For `caption_and_wrap_band()` with `header_rows_of(band, GRID, 3)` (grid boundaries `100/150/200/250/300`, leaf labels `Item|Ref|Qty|Cost` at columns `0|1|2|3`):

```python
merge_candidates == [
    [{"column": 2, "leaf_label": "Qty",  "merged": "Monday Qty"},
     {"column": 3, "leaf_label": "Cost", "merged": "5 May Cost"}],
    [{"column": 1, "leaf_label": "Ref",  "merged": "Unit Ref"}],
]
row_cell_counts   == [2, 1]
leaf_column_count == 4
```

For `out_of_grid_caption_band()` with `header_rows_of(band, GRID, 2)` (its single non-leaf cell `Report` has ink `[20, 60]`, centre 40, outside the grid entirely):

```python
merge_candidates  == [[None]]
row_cell_counts   == [1]
leaf_column_count == 4
```

Both fixtures already exist in `tests/etkl/test_rowrole_reading.py` and are importable.

---

### Task 1: `row_role_context` reports the evidence

**Files:**
- Modify: `src/iladub/etkl/rowrole.py` (the `row_role_context` function only)
- Test: `tests/etkl/test_rowrole_grounding.py` (create)

**Interfaces:**
- Consumes: `rowrole._column_containing(x, boundaries) -> int | None` (already shipped); `headers.header_rows_of(band, grid, body_line) -> list`; the two fixtures in `tests/etkl/test_rowrole_reading.py`.
- Produces: `row_role_context(header_rows, grid) -> dict` with the existing keys `rows`, `leaf_labels`, `row_columns` **plus** `merge_candidates: list[list[dict | None]]`, `row_cell_counts: list[int]`, `leaf_column_count: int`. Each non-null `merge_candidates` entry is `{"column": int, "leaf_label": str, "merged": str}`.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rowrole_grounding.py`:

```python
"""Loop C.1 — band-local evidence reported to the NEURAL row-role proposer.

The proposer previously saw only row texts, leaf labels and column indices. Three structural
tests (tiling, coverage, ink span) all fail to separate furniture/continuation/level, so the
judgment is correctly NEURAL — but the model was never shown WHAT a fragment would merge into.
These keys close that gap. They are REPORTED evidence: nothing branches on them.
See docs/superpowers/specs/2026-07-28-rowrole-grounding-design.md.
"""
from iladub.etkl.headers import header_rows_of
from iladub.etkl.rowrole import build_row_reading, row_role_context
from tests.etkl.test_rowrole_reading import (GRID, caption_and_wrap_band,
                                             out_of_grid_caption_band)


def _ctx(band, split):
    return row_role_context(header_rows_of(band, GRID, split), GRID)


def test_merge_candidates_show_what_each_fragment_would_become():
    # The loop's whole thesis, stated by the fixture: "Unit Ref" reads as a column name and
    # "Monday Qty" / "5 May Cost" do not. That contrast is only available if it is reported.
    assert _ctx(caption_and_wrap_band(), 3)["merge_candidates"] == [
        [{"column": 2, "leaf_label": "Qty", "merged": "Monday Qty"},
         {"column": 3, "leaf_label": "Cost", "merged": "5 May Cost"}],
        [{"column": 1, "leaf_label": "Ref", "merged": "Unit Ref"}],
    ]


def test_row_cell_counts_and_leaf_column_count():
    # The solitary-parent signal in raw form: one cell over four leaf columns. Reported as
    # counts, NOT as a derived cover set from the parent path — repair_coverage/_centered_run
    # widened "Date of Grain"'s single ink column to covers 1..12 on the real document.
    ctx = _ctx(caption_and_wrap_band(), 3)
    assert ctx["row_cell_counts"] == [2, 1]
    assert ctx["leaf_column_count"] == 4


def test_out_of_grid_cell_yields_no_merge_candidate():
    # Regression guard for the Loop C clamp defect, re-asserted at the context layer: a cell
    # whose ink centre lies outside every column must report None, never a fabricated merge
    # onto the rightmost label.
    ctx = _ctx(out_of_grid_caption_band(), 2)
    assert ctx["merge_candidates"] == [[None]]
    assert ctx["row_columns"] == [[-1]]


def test_merge_candidate_agrees_with_build_row_reading():
    # The context can never disagree with the rewrite: whatever it reports as the merged text
    # must appear in the label build_row_reading actually produces for that column.
    band = caption_and_wrap_band()
    rows = header_rows_of(band, GRID, 3)
    ctx = row_role_context(rows, GRID)
    cand = ctx["merge_candidates"][1][0]           # the "Unit" -> "Ref" continuation
    nodes, _caps, _src = build_row_reading(rows, GRID, ("furniture", "continuation"))
    label = next(n.text for n in nodes if cand["column"] in n.covers)
    assert cand["merged"] in label, (cand, label)


def test_existing_keys_are_unchanged():
    # The added keys must not disturb what the shipped code already reports.
    ctx = _ctx(caption_and_wrap_band(), 3)
    assert ctx["rows"] == [["Monday", "5 May"], ["Unit"]]
    assert ctx["leaf_labels"] == ["Item", "Ref", "Qty", "Cost"]
    assert ctx["row_columns"] == [[2, 3], [1]]


def test_empty_header_rows_reports_empty_evidence():
    # The shipped empty-input contract extends to the new keys — no IndexError, no None.
    ctx = row_role_context([], GRID)
    assert ctx["merge_candidates"] == []
    assert ctx["row_cell_counts"] == []
    assert ctx["leaf_column_count"] == 0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_grounding.py -q`
Expected: **4 failures** (`KeyError: 'merge_candidates'` / `'row_cell_counts'` / `'leaf_column_count'`). `test_existing_keys_are_unchanged` and `test_merge_candidate_agrees_with_build_row_reading` may already pass — that is fine, they are guards, not new behaviour.

- [ ] **Step 3: Replace `row_role_context` in `src/iladub/etkl/rowrole.py`**

Replace the whole existing `row_role_context` function with:

```python
def row_role_context(header_rows, grid) -> dict:
    """The proposer's inputs, read off the header rows. Reports geometry; decides nothing.

    rows              — the NON-LEAF rows' cell texts, top to bottom.
    leaf_labels       — the leaf (bottom) row's cell texts, left to right.
    row_columns       — per non-leaf cell, the column index containing its ink center, using the
                        same half-open containment header-covers.rq uses for leaf labels (no
                        clamp), so the model can see WHICH label a fragment would complete. -1
                        means the cell's ink center lies outside every column (e.g. a
                        page-margin-flush leaked line).
    merge_candidates  — parallel to `rows`: per non-leaf cell, what a 'continuation' reading would
                        produce ({column, leaf_label, merged}), or None when the cell's ink center
                        lies in no column or that column carries no leaf label. This is the
                        evidence that separates the otherwise indistinguishable pair: a genuine
                        short merged parent ('WIDE' over 'Unit') and a wrap fragment ('Date of
                        Grain' over 'Commencement') have IDENTICAL geometry — both have
                        single-column ink above a leaf label in that column — and differ only in
                        whether the joined text reads as one column name (spec §2 Finding 3).
    row_cell_counts   — cells per non-leaf row.
    leaf_column_count — number of leaf cells. With row_cell_counts this carries the
                        solitary-parent reasoning in RAW form: one cell over many columns is more
                        often a title than a group label.

    Deliberately NOT reported: either cover set on the parent path. _covers_for_cell alone
    reports only the ink column ('Date of Grain' -> a single column); it is the DOWNSTREAM
    repair_coverage/_centered_run symmetrized-run extension (headers.py) that turned that single
    ink column into 'covers 1..12' one stage later. Reporting either would hand the proposer an
    artefact that misleads. Counts are exact and underived.

    `merged` is computed per cell IN ISOLATION. When several continuation rows land in the same
    column, build_row_reading composes them top-to-bottom ('Date of Grain' + 'Loading' +
    'Commencement'), so a single cell's `merged` is a FRAGMENT of the final label, not the final
    label — hence 'candidates'.

    Returns empty lists for an empty header_rows (nothing to read, nothing to decide).
    """
    if not header_rows:
        return {"rows": [], "leaf_labels": [], "row_columns": [],
                "merge_candidates": [], "row_cell_counts": [], "leaf_column_count": 0}
    b = grid.boundaries
    non_leaf = list(header_rows[:-1])
    leaf_row = header_rows[-1]

    # column -> leaf label, placed by the same containment rule build_row_reading uses.
    leaf_by_col: dict[int, str] = {}
    for c in leaf_row:
        col = _column_containing((c.x0 + c.x1) / 2.0, b)
        if col is not None:
            leaf_by_col[col] = c.text

    row_columns = []
    merge_candidates = []
    for row in non_leaf:
        cols = []
        cands = []
        for c in row:
            col = _column_containing((c.x0 + c.x1) / 2.0, b)
            cols.append(-1 if col is None else col)
            if col is None or col not in leaf_by_col:
                cands.append(None)          # unplaceable -> no candidate, never a guess
            else:
                label = leaf_by_col[col]
                cands.append({"column": col, "leaf_label": label,
                              "merged": (c.text + " " + label).strip()})
        row_columns.append(cols)
        merge_candidates.append(cands)

    return {
        "rows": [[c.text for c in row] for row in non_leaf],
        "leaf_labels": [c.text for c in leaf_row],
        "row_columns": row_columns,
        "merge_candidates": merge_candidates,
        "row_cell_counts": [len(row) for row in non_leaf],
        "leaf_column_count": len(leaf_row),
    }
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_grounding.py -q`
Expected: **6 passed.**

- [ ] **Step 5: Verify no behaviour changed**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_reading.py tests/etkl/test_rowrole_resolution.py tests/etkl/test_rowrole_integration.py tests/etkl/test_conservation_shape.py tests/etkl/test_rowrole_proposer.py -q`
Expected: all pass, unchanged counts. `row_role_context` is read-only, so any failure here means the rewrite disturbed an existing key — re-read Step 3 and fix. Do not adjust a test.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/rowrole.py tests/etkl/test_rowrole_grounding.py
git commit -m "feat(etkl): report merge candidates + row/leaf counts to the row-role proposer (loop C.1)"
```

---

### Task 2: The BAML function and the live proposer carry the evidence

**Files:**
- Modify: `baml_src/header_rowrole.baml`
- Modify: `src/iladub/etkl/propose.py` (the `BamlRowRoleProposer.propose_header_row_roles` method only)
- Test: `tests/etkl/test_rowrole_proposer.py` (extend)

**Interfaces:**
- Consumes: the three keys Task 1 added to `row_role_context`.
- Produces: `ProposeHeaderRowRoles(rows: string[][], leaf_labels: string[], row_columns: int[][], merge_candidates: string[][], row_cell_counts: int[], leaf_column_count: int) -> HeaderRowRoleProposal`. `BamlRowRoleProposer` forwards them in that order.

**Note on the `merge_candidates` wire type:** BAML gets `string[][]` — the `merged` text per cell, with `""` for a null candidate — not the dict. The dict's `column` and `leaf_label` are already visible to the model via `row_columns` and `leaf_labels`, so sending the object would duplicate them and complicate the schema for no gain (YAGNI). The Python context keeps the dict because the agreement test in Task 1 needs `column`.

- [ ] **Step 1: Write the failing test**

Append to `tests/etkl/test_rowrole_proposer.py`:

```python
def test_baml_function_and_python_proposer_agree_on_arity():
    """The check Loop C added after finding BamlSpanProposer calls a ProposeHeaderSpan that was
    never authored in baml_src/. The live path is env-gated off, so a mismatch would surface only
    in production — pin it here instead."""
    import os
    import re
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    baml = open(os.path.join(root, "baml_src", "header_rowrole.baml"), encoding="utf-8").read()
    sig = re.search(r"function ProposeHeaderRowRoles\((.*?)\)", baml, re.S).group(1)
    params = [p.split(":")[0].strip() for p in sig.split(",")]
    assert params == ["rows", "leaf_labels", "row_columns",
                      "merge_candidates", "row_cell_counts", "leaf_column_count"]

    src = open(os.path.join(root, "src", "iladub", "etkl", "propose.py"), encoding="utf-8").read()
    call = re.search(r"sync_client\.b\.ProposeHeaderRowRoles\((.*?)\n\s*\)\s*\n\s*return",
                     src, re.S).group(1)
    args = [a.strip() for a in call.split(",") if a.strip()]
    # six positional arguments, in the SAME order as the BAML signature above
    assert len(args) == 6, args
    assert args[0] == 'context.get("rows")', args
    assert args[1] == 'context.get("leaf_labels")', args
    assert args[2] == 'context.get("row_columns")', args
    assert args[4] == 'context.get("row_cell_counts")', args
    assert args[5] == 'context.get("leaf_column_count")', args
    # args[3] is the locally-built merged-text list (dicts are flattened before the wire)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_proposer.py::test_baml_function_and_python_proposer_agree_on_arity -q`
Expected: FAIL — the BAML signature still has three parameters, so the `params ==` assertion fails.

- [ ] **Step 3: Update `baml_src/header_rowrole.baml`**

Replace the `function ProposeHeaderRowRoles(...)` signature line and add two prompt sentences. The `HeaderRowRoleProposal` class is unchanged. The full function becomes:

```baml
function ProposeHeaderRowRoles(
  rows: string[][], leaf_labels: string[], row_columns: int[][],
  merge_candidates: string[][], row_cell_counts: int[], leaf_column_count: int
) -> HeaderRowRoleProposal {
  client Claude
  prompt #"
    A table's header region was read as several rows of text. The BOTTOM row holds the
    column labels (one per column): {{ leaf_labels }}. The table has {{ leaf_column_count }}
    columns.

    The rows ABOVE it are: {{ rows }}, and for each of their cells the column index the cell
    sits over is: {{ row_columns }}. Each of those rows has this many cells: {{ row_cell_counts }}.

    If a cell were read as a "continuation", joining it to the label below would produce:
    {{ merge_candidates }} (an empty string means the cell sits over no column that has a label,
    so it CANNOT be a continuation).

    Classify EACH row above the bottom row, top to bottom, as exactly one of:
      - "furniture"    — not part of the table: a report date, a title, a page number.
      - "continuation" — a wrapped fragment of the column label below it; joining it to that
                         label (fragment first) produces the real column name.
      - "level"        — a genuine hierarchical group label spanning several columns, where the
                         labels below it are its sub-columns.

    Judge each candidate join on whether it READS AS A SINGLE COLUMN NAME. "Date of Grain" joined
    to "Commencement" gives "Date of Grain Loading Commencement" — a real column name, so that row
    is a "continuation". "Monday" joined to "Qty" gives "Monday Qty" — two unrelated things, so
    that row is not. This is the decisive evidence: a short merged group label and a wrapped
    fragment have IDENTICAL geometry, and only the language tells them apart.

    A row with a single cell over a table of many columns is more likely a title than a group
    label — UNLESS it plausibly groups a subset of the columns beneath it (a lone "Region" over
    four direction columns beside a "Year" stub IS a genuine group label). Weigh
    {{ row_cell_counts }} against {{ leaf_column_count }} with that exception in mind.

    Use the column indices to see WHICH label a fragment would complete. A column index of -1
    means the cell's ink sits outside every column of the table — a strong signal that the row is
    "furniture", not a "continuation". Prefer "continuation" over "furniture" whenever a fragment
    plausibly reads as part of a label — "furniture" discards text from the table, so it is the
    lossy answer and must be reserved for lines that genuinely are not header content.

    Return one role per row above the bottom row, in order.
    {{ ctx.output_format }}
  "#
}
```

- [ ] **Step 4: Update `BamlRowRoleProposer` in `src/iladub/etkl/propose.py`**

Replace the `propose_header_row_roles` method body's call with:

```python
    def propose_header_row_roles(self, context):
        from baml_client import sync_client
        # merge_candidates goes over the wire as the merged TEXT per cell ("" when the cell has no
        # candidate). column/leaf_label are already visible via row_columns/leaf_labels, so sending
        # the object would duplicate them for no gain.
        merged = [[(c["merged"] if c else "") for c in row]
                  for row in context.get("merge_candidates", [])]
        r = sync_client.b.ProposeHeaderRowRoles(
            context.get("rows"),
            context.get("leaf_labels"),
            context.get("row_columns"),
            merged,
            context.get("row_cell_counts"),
            context.get("leaf_column_count"),
        )
        return RowRoleProposal(
            roles=tuple(r.roles),
            confidence=r.confidence,
            rationale=r.rationale,
            suggester_iri="urn:iladub:suggester/baml.ProposeHeaderRowRoles",
        )
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_proposer.py -q`
Expected: all pass (the 5 shipped tests plus the new arity check).

- [ ] **Step 6: Confirm the wire transform is correct**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from iladub.etkl.headers import header_rows_of
from iladub.etkl.rowrole import row_role_context
from tests.etkl.test_rowrole_reading import GRID, caption_and_wrap_band, out_of_grid_caption_band
for band, split in ((caption_and_wrap_band(), 3), (out_of_grid_caption_band(), 2)):
    ctx = row_role_context(header_rows_of(band, GRID, split), GRID)
    print([[(c['merged'] if c else '') for c in row] for row in ctx['merge_candidates']])
"
```
Expected exactly:
```
[['Monday Qty', '5 May Cost'], ['Unit Ref']]
[['']]
```
If the second line is anything other than `[['']]`, the null-candidate case is not mapping to the empty string and the model would receive a fabricated join — fix before committing.

- [ ] **Step 7: Full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q` (set the Bash tool's `timeout` parameter to `400000` ms — the suite takes ~155s and will otherwise auto-background).
Expected: **591 passed, 5 skipped** (584 baseline + 6 from Task 1 + 1 from Task 2). Report the real numbers.

- [ ] **Step 8: Confirm GrainCorp is unchanged**

The new keys must not alter any outcome, since the local confirmation uses `FakeRowRoleProposer`, which ignores its context entirely.

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop=RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption + two wrapped rows')
r=compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for reg in r.regions: print(reg.kind, reg.verdict, 'cells=', reg.cells, 'reason=', reg.reason)
print('score=', round(r.score,4))
"
```
Expected: region 2 `UNSUPPORTED_TABLE asserted cells= 447 reason= None`, `score= 0.947` — identical to Loop C. **Do NOT commit the PDF.** If the file is missing, say so and skip this step; it is a confirmation, not a gate.

- [ ] **Step 9: Commit**

```bash
git add baml_src/header_rowrole.baml src/iladub/etkl/propose.py tests/etkl/test_rowrole_proposer.py
git commit -m "feat(etkl): ProposeHeaderRowRoles carries the merge/count evidence (loop C.1)"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1 in-scope: `merge_candidates`, `row_cell_counts`, `leaf_column_count` | Task 1 Step 3 |
| §1 in-scope: BAML params + two prompt sentences | Task 2 Steps 3 |
| §1 in-scope: `BamlRowRoleProposer` forwards them | Task 2 Step 4 |
| §1 success 1 (fixture values) | Task 1 Step 1, `test_merge_candidates_show_what_each_fragment_would_become` + `test_row_cell_counts_and_leaf_column_count` |
| §1 success 2 (out-of-grid → null) | Task 1 `test_out_of_grid_cell_yields_no_merge_candidate`; wire form in Task 2 Step 6 |
| §1 success 3 (no behaviour change, suite green) | Task 1 Step 5, Task 2 Steps 7–8 |
| §1 success 4 (BAML/Python arity agree) | Task 2 Step 1 |
| §1 success 5 (gate) | Global Constraints |
| §3.1 the "deliberately NOT `_covers_for_cell`" decision | Global Constraints + the docstring in Task 1 Step 3 |
| §3.1 multi-row composition caveat | Documented in the Task 1 Step 3 docstring; `test_merge_candidate_agrees_with_build_row_reading` asserts substring, not equality, precisely because of it |
| §3.2 BAML | Task 2 Step 3 |
| §3.3 proposer | Task 2 Step 4 |
| §4 all five test bullets | Task 1 Step 1 (four) + Task 2 Step 1 (arity) |
| §5 gate | Global Constraints |
| §6 deferred items | No task — correctly out of scope |

**Gap found and closed during review:** §4's "agreement with `build_row_reading`" bullet needed the substring form, not equality, because multi-row continuations compose — the test and the spec now say so consistently.

**Placeholder scan:** none. Every step carries complete, copy-ready code and exact expected output. Task 2 Step 8's PDF path has an explicit skip instruction because the file is local-only and uncommittable.

**Type consistency:**
- `row_role_context` returns `merge_candidates: list[list[dict | None]]` (Task 1); Task 2's wire transform maps `dict | None → str` and is the only place that flattening happens. Consistent.
- `_column_containing(x, boundaries) -> int | None` used identically for leaf placement and non-leaf placement (Task 1 Step 3), which is what makes `test_merge_candidate_agrees_with_build_row_reading` hold — `build_row_reading` uses the same function.
- `row_cell_counts: list[int]`, `leaf_column_count: int` in Python; `int[]` and `int` in BAML. Consistent.
- The six BAML parameter names in Task 2 Step 1's assertion exactly match the signature written in Step 3 and the forwarding order in Step 4.
- `RowRoleProposal(roles, confidence, rationale, suggester_iri)` unchanged — Task 2 touches only the call, not the dataclass.
