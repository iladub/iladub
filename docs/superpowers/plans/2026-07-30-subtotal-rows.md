# Row de-fusion + arithmetic subtotal rows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop fusing suppressed-key rows into the record above them (the author's hrules are the row delimiters), and stop compiling subtotal rows as fake data records — a sparse row whose measure reconciles arithmetically becomes a `tab:DetectedAggregationRow` with operand edges.

**Architecture:** (1) `cells.group_wrapped` gains an hrule veto — never absorb across an author-drawn horizontal rule (presence test, the row-axis twin of Loops D/G). (2) `rows.detect_aggregation_rows` is a pure PROCEDURAL function (the gate's decidable-exact-arithmetic carve-out): sparse candidates confirm iff their measure equals the token-sum of member rows back to the previous same-or-outer-level aggregation. (3) `holon.assert_hier_region` types confirmed rows (`tab:AggregationRow` + new `tab:DetectedAggregationRow` subclass) with `tab:aggregates` edges; a new SHACL shape guards the subclass **only** (probed: `denormalization.py` emits bare `tab:AggregationRow` rows, so a supertype-targeted shape would break the shipped reshape path); the concept feed skips aggregation rows.

**Tech Stack:** Python 3 (`src/iladub/etkl/`, `src/iladub/feed.py`), `decimal.Decimal`, RDF Turtle, reportlab, pytest.

**Spec:** `docs/superpowers/specs/2026-07-30-subtotal-rows-design.md` — §2's measurements drive everything.

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from `/Volumes/WD Green/dev/git/iladub`.

**Pace:** **targeted** tests per task; the full suite runs **once**, in Task 4 (~165s — set the Bash tool's `timeout` to `400000` ms, FOREGROUND, never background).

**Baseline:** 629 passed, 5 skipped (`main` at `1e48515`). Branch `iladub-subtotal-rows` is checked out (spec at `0ced1a8`).

## Global Constraints

- **No language matching, ever.** The detector never reads label text — `" Total"` is English, and matching it is the tuned constant of natural language. Sparsity, label column, and arithmetic only. One test feeds non-English labels and must confirm identically.
- **The hrule veto is a presence test** — any author hrule strictly inside the gap vetoes absorption. No constant, no tolerance beyond the existing y-rounding idiom (`round(y, 2)`, `+ 0.5` line-inclusion consistent with `compile.py`'s existing band char filter).
- **Detection is PROCEDURAL by the gate's decidable-exact-arithmetic carve-out** — exact `Decimal` sums over a finite ordered row sequence. State this in the docstring. The closed-world check is SHACL.
- **The membrane shape targets `tab:DetectedAggregationRow` ONLY.** Probed: `denormalization.annotate_aggregations` types rows bare `tab:AggregationRow` with no row-level operands; a supertype-targeted shape breaks the shipped reshape path at final validation.
- **Honest failure:** a candidate with a non-numeric measure is never confirmed (blank totals stay ordinary rows); zero-member candidates (the Grand Total shape) are never confirmed; unruled bands keep today's behavior (veto inert without hrules).
- **Never weaken an existing test. No third-party PDF committed.**

---

## File Structure

| File | Responsibility |
| --- | --- |
| `src/iladub/etkl/cells.py` | **Modify** — the hrule veto in `group_wrapped`'s absorption loop. |
| `src/iladub/etkl/rows.py` | **Modify** — add `detect_aggregation_rows` (pure function) + `_numeric_token_sum`. |
| `src/iladub/etkl/holon.py` | **Modify** — `assert_hier_region` types confirmed rows + operand edges. |
| `vocab/ontology/tab.ttl` | **Modify (append)** — `tab:DetectedAggregationRow ⊑ tab:AggregationRow`. |
| `vocab/shapes/tab-shapes.ttl` | **Modify (append)** — `tab:DetectedAggregationRowShape`. |
| `src/iladub/etkl/tiling.py` | **Modify** — add the shape to `_TILING_SHAPE_IRIS` (tenth; prevents our own emission from ever crashing at final validate). |
| `src/iladub/feed.py` | **Modify** — `table_records` skips cells whose `atRow` row is a `tab:AggregationRow`. |
| `tests/etkl/fixtures.py` | **Modify (append)** — `subtotal_hier_table_pdf` (E2E fixture). |
| `tests/etkl/test_row_defusion.py` | **Create** — Task 1 (synthetic Bands, no PDFs). |
| `tests/etkl/test_aggregation_rows.py` | **Create** — Tasks 2–3. |
| `docs/superpowers/residues.md`, spec status | **Modify** — Task 4. |

Task order: 1 → 2 → 3 → 4.

---

## Probed values (measured while planning — assert, do not re-derive)

- **The fusion red case (GrainCorp):** grouped row 4 fuses three source lines → cells `'56817 56787'`, `'20,000 20,000 20,000'`. With the veto: **zero fused cells**; `logical_rows` returns **50 RowBands** (anchor exists); score/cells unchanged 0.9496/509.
- **hrules discriminate perfectly:** 35/54 consecutive line pairs carry an hrule (every real row boundary); the 19 without are exactly the genuine wraps (wrapped header rows + wrapped body cells). Double-drawn hrules (87.0/87.2) are harmless to a veto.
- **The author boxes two Sep Mackay TBA rows together** (no hrule between tops 328.11/334.59; hrules at 327.12 above and 339.96 below) — per the author they are ONE row whose measure cell holds two values. Hence the **token-sum rule**: a measure cell's value = the sum of its numeric tokens (`'20,000 30,000'` → 50,000; identity for single values).
- **Detector dry-run on the de-fused 50 rows** (with token-sum): **17 of 20 sparse candidates confirm**, including two-level nesting (`Jul 26 Total` = 118,000 over 4 data rows with 4 port totals correctly excluded; `Aug 26 Total` over 21; `Sep 26 Total` = 50,000+27,500+0+70,000 = 147,500 through the boxed row; year total = 750,000). **3 honest refusals:** `Port Kembla Total` (measure `'-'`), `Fisherman Islands Total` Sep (measure `'-'`), `Grand Total` (no non-aggregation members after the year total). Confirmed-set cascade matters: an unconfirmed sparse row is a *member* of later sums (contributing its token-sum), which is what lets `Portland Total` reconcile past the blank-total row above it.
- **Level rule verified:** label column encodes the level (port totals label in c2, month totals in c1, year total in c0). Members = non-aggregation rows back to the previous **confirmed** aggregation with label column ≤ L.
- **`atRow` links EntryCell → row URI** (`holon.py:458`), so the feed exclusion is a 2-line raw-graph membership check — no IRI parsing.
- **The shipped `subtotals_row_group_pdf`/`totals_table_pdf` classify RECORD_TABLE** and never reach `assert_hier_region` — loop H changes nothing for them (pin this as unchanged, not accidental).

---

### Task 1: The hrule veto in `group_wrapped`

**Files:**
- Modify: `src/iladub/etkl/cells.py` (the absorption loop + docstring)
- Test: `tests/etkl/test_row_defusion.py` (create)

**Interfaces:**
- Consumes: `Band.hrules` (shipped), `geometry.HRule` — **verified while planning:** fields are `(y, x0, x1)`, the veto reads only `.y`.
- Produces: `group_wrapped` unchanged signature; absorption additionally vetoed when any `band.hrules` y lies in `(tops[j-1], tops[j] + 0.5]`.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_row_defusion.py`:

```python
"""Loop H — the author's hrules are the row delimiters (residue R4, de-fusion half).

group_wrapped absorbs a line as a wrap-continuation when its columns are a proper subset of the
anchor's, it is partial, and the gap < lead. A SUPPRESSED-KEY data row and a subtotal row are both
proper-subset partial rows — the suppressed-key convention IS the false-absorption trigger
(measured on a real report: three source lines fused into one record, '20,000 20,000 20,000' as
one cell). But the author draws every real row boundary: 35/54 line pairs carry an hrule, and the
19 that do not are exactly the genuine wraps. The veto: never absorb across an hrule.
See docs/superpowers/specs/2026-07-30-subtotal-rows-design.md §2.
"""
from iladub.etkl.bands import Band
from iladub.etkl.cells import group_wrapped
from iladub.etkl.geometry import HRule, Line, Word
from iladub.etkl.grid import LeafGrid

GRID = LeafGrid((100.0, 150.0, 200.0, 250.0, 300.0), 4, 50.0, 1.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 8.0)


def _line(words, top):
    return Line(tuple(words), top, top + 8.0)


def _texts(rows):
    return [[c.text for c in row] for row in rows]


def suppressed_key_lines():
    """Anchor row with all 4 columns; then a suppressed-key data row (3 cols, proper subset)
    and a subtotal row (2 cols) — both tight-gapped, i.e. absorbable without the veto."""
    full = _line([_w("Jul", 105, 130, 0.0), _w("Mackay", 155, 190, 0.0),
                  _w("V1", 205, 230, 0.0), _w("100", 255, 280, 0.0)], 0.0)
    data = _line([_w("Gladstone", 155, 195, 10.0), _w("V2", 205, 230, 10.0),
                  _w("200", 255, 280, 10.0)], 10.0)
    sub = _line([_w("Total", 155, 185, 20.0), _w("300", 255, 280, 20.0)], 20.0)
    return full, data, sub


def test_hrule_vetoes_false_absorption():
    # THE FUSION DEFECT: without hrules these three lines fuse into one row.
    full, data, sub = suppressed_key_lines()
    hrules = (HRule(9.0, 100.0, 300.0), HRule(19.0, 100.0, 300.0))
    band = Band((full, data, sub), 0.0, 30.0, (), hrules)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 3, _texts(rows)
    assert _texts(rows)[2] == ["Total", "300"]


def test_without_hrules_behavior_is_unchanged():
    # The veto is inert on unruled bands: today's (defective, documented) fusion persists.
    full, data, sub = suppressed_key_lines()
    band = Band((full, data, sub), 0.0, 30.0)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 1, _texts(rows)          # pins main's current behavior


def test_genuine_wrap_in_hrule_free_gap_still_absorbs():
    # A wrapped body cell has NO hrule inside it (measured: all 19 hrule-free pairs are wraps).
    # hrules elsewhere must not disturb it.
    anchor = _line([_w("Jul", 105, 130, 0.0), _w("Fisherman", 155, 198, 0.0),
                    _w("V1", 205, 230, 0.0), _w("100", 255, 280, 0.0)], 0.0)
    wrap = _line([_w("Islands", 155, 190, 10.0)], 10.0)
    nxt = _line([_w("Aug", 105, 130, 20.0), _w("Portland", 155, 195, 20.0),
                 _w("V2", 205, 230, 20.0), _w("200", 255, 280, 20.0)], 20.0)
    hrules = (HRule(19.0, 100.0, 300.0),)       # hrule AFTER the wrap pair only
    band = Band((anchor, wrap, nxt), 0.0, 30.0, (), hrules)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 2, _texts(rows)
    assert "Fisherman Islands" in " ".join(_texts(rows)[0])


def test_double_drawn_hrule_is_harmless():
    # Real borders render as two segments a fraction apart (measured: 87.0/87.2). Any of them
    # vetoing is enough; duplicates change nothing.
    full, data, sub = suppressed_key_lines()
    hrules = (HRule(9.0, 100, 300), HRule(9.12, 100, 300),
              HRule(19.0, 100, 300), HRule(19.1, 100, 300))
    band = Band((full, data, sub), 0.0, 30.0, (), hrules)
    assert len(group_wrapped(band, GRID)) == 3
```

- [ ] **Step 2: Run to verify the red**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_defusion.py -q`
Expected: `test_hrule_vetoes_false_absorption` and `test_double_drawn_hrule_is_harmless` **FAIL** (rows fuse to 1); the other two pass already (they pin current behavior).

- [ ] **Step 3: Add the veto**

In `src/iladub/etkl/cells.py`, `group_wrapped`: after `lead` is computed, add

```python
    # THE HRULE VETO (loop H): the author's horizontal rules are the ROW DELIMITERS — the
    # row-axis twin of loops D/G's "author structure outranks the derived heuristic". A
    # suppressed-key data row and a subtotal row are both proper-subset partial rows, so
    # conditions 2/3 + gap<lead FUSE them into the record above (measured: three source lines
    # in one record, '20,000 20,000 20,000' as one cell). Measured on the same report: every
    # real row boundary carries an hrule (35/54 pairs) and every hrule-free pair is a genuine
    # wrap — so absorption across an hrule is always wrong, and absorption within an hrule-free
    # gap is exactly the wrap case this function exists for. Presence test, no constant.
    # HONEST LIMIT: unruled bands (no hrules) keep the fusion defect; the veto is inert there.
    hrule_ys = sorted({round(h.y, 2) for h in getattr(band, "hrules", ())})
```

and extend the absorption `while` condition with the veto (the loop currently reads
`while j < len(lines) and (tops[j] - tops[j - 1]) < lead:` — locate it exactly):

```python
        while (j < len(lines) and (tops[j] - tops[j - 1]) < lead
               and not any(tops[j - 1] < y <= tops[j] + 0.5 for y in hrule_ys)):
```

Extend the docstring's condition list with the veto as a fourth condition, quoting the 35/54 // 19-wraps measurement and the unruled honest limit.

- [ ] **Step 4: Run to verify green + targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_defusion.py tests/etkl/test_cells.py tests/etkl/test_hrule_split.py tests/etkl/test_rows.py tests/etkl/test_hierarchical.py tests/etkl/test_headers.py -q`
Expected: all pass (4 new + existing). The `hrule_split` fixtures carry hrules **between header and body** — absorption never crossed those (different rows), so they must be unchanged; if one fails, investigate the veto's bounds, do not adjust the test.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/cells.py tests/etkl/test_row_defusion.py
git commit -m "fix(etkl): never absorb a wrap-continuation across an author hrule (loop H de-fusion)"
```

---

### Task 2: `rows.detect_aggregation_rows`

> **SUPERSEDED IN TWO PLACES by commit `34bf64b` (implementer findings):** (1) the `_row(top, **cells)`
> helper cannot unpack integer keys as kwargs — the committed tests pass the dict positionally;
> (2) the `modal` sparsity bar via `Counter.most_common` is broken on small groups (two sparse rows
> vs one full row → the mode IS the sparse count → detector dead); the committed code uses
> `max(len(rc) …)` — the widest row defines the normal shape. The spec §3.2 carries the same
> correction. The confirmation rule, cascade, token-sum and honest refusals are unchanged.

**Files:**
- Modify: `src/iladub/etkl/rows.py` (append two functions)
- Test: `tests/etkl/test_aggregation_rows.py` (create)

**Interfaces:**
- Consumes: `rows.RowBand` (`.cells`), `grid.LeafGrid`, `regions.column_of`, `headers.is_numeric`.
- Produces: `detect_aggregation_rows(rows, grid) -> dict[int, tuple[int, int, tuple[int, ...]]]` — row index → `(label_col, measure_col, member_indices)`. And `_numeric_token_sum(text) -> Decimal | None` (None when no numeric token).

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_aggregation_rows.py`:

```python
"""Loop H — arithmetic subtotal detection (residue R4, detection half).

A SPARSE row (2 cells vs the modal shape) whose numeric measure equals the token-sum of the
non-aggregation rows above it — back to the previous confirmed aggregation of same-or-outer level
(the label's COLUMN encodes the level) — is an aggregation row, not a data record.

LANGUAGE-INDEPENDENT BY CONSTRUCTION: the label text is never read. A ' Total' suffix test is the
tuned constant of natural language and is expressly forbidden (spec §5).
See docs/superpowers/specs/2026-07-30-subtotal-rows-design.md §2 Findings 4-5.
"""
from iladub.etkl.geometry import Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.rows import RowBand, detect_aggregation_rows

GRID = LeafGrid((0.0, 50.0, 100.0, 150.0, 200.0), 4, 50.0, 1.0)
COLS = {0: (5, 45), 1: (55, 95), 2: (105, 145), 3: (155, 195)}


def _row(top, **cells):
    """cells: col=text. Builds a RowBand with one cell per named column."""
    out = []
    for col, text in sorted(cells.items()):
        x0, x1 = COLS[col]
        w = Word(text, x0, x1, top, top + 8.0)
        from iladub.etkl.cells import _cell_from
        out.append(_cell_from([w], 0))
    return RowBand(top, top + 8.0, tuple(out))


def _rows(*specs):
    return tuple(_row(10.0 * i, **spec) for i, spec in enumerate(specs))


def test_single_level_group_confirms():
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg == {2: (1, 3, (0, 1))}


def test_label_text_is_never_read():
    # Same structure, label in another language entirely — identical result.
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "Zwischensumme", 3: "250"})
    assert detect_aggregation_rows(rows, GRID) == {2: (1, 3, (0, 1))}


def test_two_level_nesting_by_label_column():
    # Port totals label in c1; the month total labels in c0 (outer level) and sums the DATA
    # rows, with the inner aggregations excluded as members.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[1] == (1, 3, (0,))
    assert agg[3] == (1, 3, (2,))
    assert agg[4] == (0, 3, (0, 2))          # data rows only; inner aggs excluded


def test_inner_group_boundary_is_the_previous_same_level_agg():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[3] == (1, 3, (2,))            # stops at row 1 (same level), members = row 2 only


def test_blank_member_contributes_nothing():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "-"},
                 {1: "SUB", 3: "100"})
    assert detect_aggregation_rows(rows, GRID)[2] == (1, 3, (0, 1))


def test_blank_total_is_never_confirmed():
    # The Port Kembla honesty: a candidate with no numeric measure cannot be verified.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "-"},
                 {1: "SUB", 3: "-"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_non_reconciling_sparse_row_is_not_confirmed():
    # A lookup/reference row that happens to be sparse is NOT a subtotal.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "NOTE", 3: "999"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_multi_value_cell_sums_its_tokens():
    # The author may box two lines together (no hrule drawn between them — measured on the
    # real report: two TBA bookings in one box, measure cell '20,000 30,000'). The cell's
    # contribution is the sum of its numeric tokens.
    rows = _rows({0: "Jul", 1: "A", 2: "V1 V2", 3: "100 150"},
                 {1: "SUB", 3: "250"})
    assert detect_aggregation_rows(rows, GRID)[1] == (1, 3, (0,))


def test_unconfirmed_sparse_row_is_a_member_of_later_sums():
    # The cascade: a blank-total row stays a row AND contributes its token-sum (0) to the
    # enclosing group — measured on the real report (Portland Total reconciles past the
    # blank Fisherman total above it).
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "BLANKSUB", 3: "-"},
                 {1: "B", 2: "V2", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert 1 not in agg
    assert agg[3] == (0, 3, (0, 1, 2))
```

- [ ] **Step 2: Run to verify the red**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_aggregation_rows.py -q`
Expected: **collection error** — `ImportError: cannot import name 'detect_aggregation_rows'`.

- [ ] **Step 3: Implement in `src/iladub/etkl/rows.py`**

Append:

```python
def _numeric_token_sum(text):
    """The exact sum of a cell's numeric tokens, or None if it has none.

    Identity for a single value. A multi-line box (the author drew no hrule inside it, so per
    the author it is ONE row) carries one value per boxed line — measured on a real report:
    two TBA bookings share a box whose measure cell reads '20,000 30,000', and the group's own
    printed subtotal (50,000) reconciles exactly with the token-sum. Non-numeric tokens
    (dates, dashes, words) contribute nothing; an all-non-numeric cell returns None.
    Exact decimal arithmetic — never float."""
    from decimal import Decimal
    from .headers import is_numeric
    total = None
    for tok in text.split():
        if is_numeric(tok):
            v = Decimal(tok.replace(",", "").replace("%", ""))
            total = v if total is None else total + v
    return total


def detect_aggregation_rows(rows, grid):
    """Arithmetic subtotal detection (loop H, residue R4). PROCEDURAL — and justified: this is
    the §8 gate's second procedural class, DECIDABLE EXACT ARITHMETIC (exact Decimal sums over
    a finite ordered row sequence; a SPARQL formulation of nested running-sum windows would be
    obfuscation, not a lift). The closed-world check is SHACL
    (tab:DetectedAggregationRowShape); language is NEVER read — a ' Total' suffix test is the
    tuned constant of natural language and is forbidden (spec §5).

    A row is a CANDIDATE iff it has exactly two cells, strictly fewer than the modal
    populated-cell count of the region's rows, one cell with a numeric token-sum (the measure)
    and one without (the label). The label's COLUMN encodes the nesting level (measured: port
    totals carry their label in the Port column, month totals in the Month column).

    A candidate at row i with label column L and measure value v is CONFIRMED iff
    v == the token-sum, in the measure column, of the non-aggregation rows above i back to
    (exclusive) the previous CONFIRMED aggregation row whose label column <= L — and at least
    one member exists. Unconfirmed sparse rows remain ordinary rows AND contribute their
    token-sum to enclosing groups (the measured cascade). Zero-member candidates (a grand
    total directly after a same-level total) are never confirmed — honest refusal.

    Returns {row_index: (label_col, measure_col, member_indices)}.
    """
    from collections import Counter
    b = grid.boundaries
    row_cols = []
    for rb in rows:
        cols = {}
        for c in rb.cells:
            cols[column_of((c.x0 + c.x1) / 2.0, b)] = c.text
        row_cols.append(cols)
    if not row_cols:
        return {}
    modal = Counter(len(rc) for rc in row_cols).most_common(1)[0][0]
    agg = {}
    for i, rc in enumerate(row_cols):
        if len(rc) != 2 or len(rc) >= modal:
            continue
        numeric = [(c, _numeric_token_sum(t)) for c, t in sorted(rc.items())]
        measures = [(c, v) for c, v in numeric if v is not None]
        labels = [c for c, v in numeric if v is None]
        if len(measures) != 1 or len(labels) != 1:
            continue
        mcol, v = measures[0]
        lcol = labels[0]
        members = []
        total = None
        for j in range(i - 1, -1, -1):
            if j in agg:
                if agg[j][0] <= lcol:
                    break                      # previous same-or-outer aggregation: stop
                continue                       # inner aggregation: not a member
            members.append(j)
            t = row_cols[j].get(mcol, "")
            s = _numeric_token_sum(t)
            if s is not None:
                total = s if total is None else total + s
        if members and total is not None and total == v:
            agg[i] = (lcol, mcol, tuple(sorted(members)))
    return agg
```

(`column_of` is already imported at the top of `rows.py`.)

- [ ] **Step 4: Run to verify green**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_aggregation_rows.py -q`
Expected: **9 passed.**

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/rows.py tests/etkl/test_aggregation_rows.py
git commit -m "feat(etkl): arithmetic subtotal detection — sparse rows that reconcile are aggregations (loop H)"
```

---

### Task 3: Emission, membrane, feed exclusion, end-to-end

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append), `vocab/shapes/tab-shapes.ttl` (append), `src/iladub/etkl/tiling.py` (`_TILING_SHAPE_IRIS`), `src/iladub/etkl/holon.py` (`assert_hier_region`), `src/iladub/feed.py` (`table_records`)
- Modify: `tests/etkl/fixtures.py` (append `subtotal_hier_table_pdf`)
- Test: `tests/etkl/test_aggregation_rows.py` (extend)

**Interfaces:**
- Consumes: `rows.detect_aggregation_rows` (Task 2); the de-fused `group_wrapped` (Task 1).
- Produces: confirmed rows typed **both** `tab:AggregationRow` and `tab:DetectedAggregationRow` (the feed reads the raw graph without inference, so both types are written explicitly), with `tab:aggregates` → each member row URI and `tab:aggregationFunction "sum"`.

- [ ] **Step 1: Grep the vocabulary**

```bash
grep -n "DetectedAggregationRow" vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl vocab/queries/*.rq
```
Expected: no output. If found, STOP.

- [ ] **Step 2: Write the failing tests**

Append to `tests/etkl/test_aggregation_rows.py`:

```python
def _hier_region_with_subtotal():
    """A minimal HierRegion whose rows contain one confirmable subtotal (the Task 2 shape)."""
    from iladub.etkl.headers import HeaderNode
    from iladub.etkl.hierarchical import HierRegion
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line

    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    hdr_words = [Word("K", 5, 45, -10.0), Word("Port", 55, 95, -10.0),
                 Word("Ship", 105, 145, -10.0), Word("Qty", 155, 195, -10.0)]
    lines = [Line(tuple(hdr_words), -10.0, -2.0)]
    for rb in rows:
        ws = tuple(w for c in rb.cells for w in c.words)
        lines.append(Line(ws, rb.top, rb.bottom))
    band = Band(tuple(lines), -10.0, 40.0)
    tree = tuple(HeaderNode(0, (i,), t, None, (COLS[i][0] + COLS[i][1]) / 2.0)
                 for i, t in enumerate(["K", "Port", "Ship", "Qty"]))
    return HierRegion(GRID, tree, rows, 1), band


def test_confirmed_rows_are_typed_with_operands():
    from rdflib import Graph, Namespace, RDF, URIRef
    from iladub.etkl.holon import assert_hier_region
    TAB = Namespace("https://w3id.org/iladub/tab#")
    hreg, band = _hier_region_with_subtotal()
    g = Graph()
    t = URIRef("urn:doc#h0")
    n = assert_hier_region(g, hreg, band, t, URIRef("urn:doc"), 0)
    assert n > 0
    agg_rows = list(g.subjects(RDF.type, TAB.DetectedAggregationRow))
    assert len(agg_rows) == 1
    row = agg_rows[0]
    assert (row, RDF.type, TAB.AggregationRow) in g          # supertype written explicitly
    ops = list(g.objects(row, TAB.aggregates))
    assert len(ops) == 2                                      # both member rows
    funcs = [str(o) for o in g.objects(row, TAB.aggregationFunction)]
    assert funcs == ["sum"]


def test_membrane_refuses_an_unexplained_detected_aggregation():
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    from iladub.etkl.tiling import region_tiles
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    r = URIRef("urn:doc#h0-r2")
    g.add((r, RDF.type, TAB.DetectedAggregationRow))          # typed, no operands, no function
    assert region_tiles(g) is False


def test_denormalization_bare_aggregation_rows_still_pass():
    # THE PROBED LANDMINE: denormalization.py types rows bare tab:AggregationRow with no
    # row-level operands. The new shape must NOT fire on the supertype.
    from rdflib import Graph, Namespace, RDF, URIRef
    from iladub.etkl.tiling import region_tiles
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    g.add((URIRef("urn:doc#agg-r1"), RDF.type, TAB.AggregationRow))
    assert region_tiles(g) is True


def test_feed_skips_aggregation_rows(tmp_path):
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.compile import compile_tables
    from iladub.feed import table_records
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions), [r.reason for r in rep.regions]
    recs = table_records(rep.graph)
    joined = [" ".join(sc.value for sc in r.concepts) for r in recs]
    assert not any("250" in j and "SUB" in j for j in joined), joined  # the subtotal is no record
```

- [ ] **Step 3: Run to verify the red**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_aggregation_rows.py -q`
Expected: the four new tests fail — no `DetectedAggregationRow` in vocab, shape absent (`region_tiles` returns True on the unexplained row), fixture missing.

- [ ] **Step 4: Vocabulary + shape + gate wiring**

`vocab/ontology/tab.ttl`, append:

```turtle

# --- detected aggregation rows (loop H, residue R4) ---
tab:DetectedAggregationRow a owl:Class ; rdfs:subClassOf tab:AggregationRow ;
    rdfs:label "Detected aggregation row"@en ;
    rdfs:comment "An aggregation row DETECTED by exact arithmetic in the extraction path (loop H): a sparse body row whose measure equals the token-sum of its member rows. Distinct subclass on purpose: denormalization's reshape path types rows bare tab:AggregationRow without row-level operands, and the operand-requiring shape must not fire on those. Detection never reads label text — sparsity, label column and arithmetic only."@en .
```

`vocab/shapes/tab-shapes.ttl`, append:

```turtle

#################################################################
#  Detected aggregation rows (loop H): a row CLAIMED as a
#  detected aggregation must carry its evidence — operands and
#  the function. Targets the SUBCLASS only: denormalization's
#  reshape path types rows bare tab:AggregationRow with cell-level
#  operands, and must not be judged by this shape.
#################################################################

tab:DetectedAggregationRowShape a sh:NodeShape ;
    sh:targetClass tab:DetectedAggregationRow ;
    sh:property [ sh:path tab:aggregates ; sh:minCount 1 ;
                  sh:message "A detected aggregation row needs at least one operand row." ] ;
    sh:property [ sh:path tab:aggregationFunction ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:message "A detected aggregation row needs exactly one aggregationFunction." ] .
```

`src/iladub/etkl/tiling.py`: add `TAB.DetectedAggregationRowShape` to `_TILING_SHAPE_IRIS` (tenth entry) and bump the docstring's count — the gate must refuse our own emission if it ever desyncs, instead of crashing at final validation (the loop G lesson).

- [ ] **Step 5: Emission in `src/iladub/etkl/holon.py`**

In `assert_hier_region`, the leaf-row block currently reads:

```python
    # Leaf rows
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))
```

Replace with:

```python
    # Leaf rows — with arithmetic aggregation detection (loop H, residue R4). A confirmed
    # subtotal is typed BOTH tab:AggregationRow (so raw-graph consumers like the concept feed
    # can exclude it without rdfs inference) and tab:DetectedAggregationRow (the operand-
    # requiring shape targets only this subclass, sparing denormalization's bare rows).
    from .rows import detect_aggregation_rows
    agg = detect_aggregation_rows(region.rows, region.grid)
    for r, rb in enumerate(region.rows):
        row_uri = URIRef(f"{table_uri}-r{r}")
        g.add((row_uri, RDF.type, TAB.LeafRow))
        g.add((table_uri, TAB.hasLeafRow, row_uri))
        if r in agg:
            _lcol, _mcol, members = agg[r]
            g.add((row_uri, RDF.type, TAB.AggregationRow))
            g.add((row_uri, RDF.type, TAB.DetectedAggregationRow))
            g.add((row_uri, TAB.aggregationFunction, Literal("sum")))
            for m in members:
                g.add((row_uri, TAB.aggregates, URIRef(f"{table_uri}-r{m}")))
```

- [ ] **Step 6: Feed exclusion in `src/iladub/feed.py`**

In `table_records`, where cells are grouped (`row = graph.value(e, TAB.atRow)`), skip aggregation rows:

```python
            row = graph.value(e, TAB.atRow)
            if row is not None and (row, RDF.type, TAB.AggregationRow) in graph:
                continue          # a subtotal is not a record (§7): its cells mint no subject
```

(`RDF` is already imported in `feed.py`; verify and add if not.)

- [ ] **Step 7: The E2E fixture**

Append to `tests/etkl/fixtures.py` (follow the file's reportlab style):

```python
def subtotal_hier_table_pdf(path: str) -> dict:
    """Loop H E2E: a ruled table with a merged 2-level header (forces the hierarchical path),
    suppressed keys, ONE subtotal row, and hrules between all body rows (the author's row
    delimiters — without them the suppressed-key rows fuse into the record above)."""
    c = canvas.Canvas(path, pagesize=(360, 220))
    c.setFont("Helvetica", 9)
    c.drawString(150, 196, "Voyage")                     # merged parent over Ship+Qty
    for x, t in ((60, "Mon"), (110, "Port"), (160, "Ship"), (250, "Qty")):
        c.drawString(x, 182, t)
    body = [("Jul", "Mackay", "V1", "100"), ("", "Mackay", "V2", "150"), ("", "SUB", "", "250"),
            ("Aug", "Gladstone", "V3", "300")]
    y = 166
    ys = []
    for mon, port, ship, qty in body:
        if mon:
            c.drawString(60, y, mon)
        c.drawString(110, y, port)
        if ship:
            c.drawString(160, y, ship)
        c.drawString(250, y, qty)
        ys.append(y)
        y -= 16
    for x in (50, 100, 150, 240, 310):                   # vertical rules
        c.line(x, 30, x, 205)
    for yy in ys:                                        # hrule under EVERY body row
        c.line(50, yy - 4, 310, yy - 4)
    c.line(50, 178, 310, 178)                            # header/body rule
    c.save()
    return {"cols": 4, "subtotal_value": "250"}
```

**Iterate on this fixture until it compiles asserted through the hierarchical path with the subtotal detected** — probe with `compile_tables` + a `DetectedAggregationRow` query, adjusting geometry only (never the detection code). If after genuine effort it classifies down a different path, drive `assert_hier_region` directly in `test_feed_skips_aggregation_rows`'s place and report `DONE_WITH_CONCERNS` naming what the fixture actually does — never fake the assertion.

- [ ] **Step 8: Run to verify green + targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_aggregation_rows.py tests/etkl/test_row_defusion.py tests/etkl/test_tiling_gate.py tests/etkl/test_transform_gate.py tests/etkl/test_tab_vocab.py tests/test_source_ownership.py tests/etkl/test_hier_holon.py tests/etkl/test_denormalization.py tests/etkl/test_denorm_integration.py tests/test_feed.py -q`
(Adjust the feed test path if it lives elsewhere — `grep -rn "table_records" tests/ | head`.)
Expected: all pass; the denormalization suites prove the shape spares the reshape path.

- [ ] **Step 9: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl src/iladub/etkl/tiling.py src/iladub/etkl/holon.py src/iladub/feed.py tests/etkl/fixtures.py tests/etkl/test_aggregation_rows.py
git commit -m "feat(etkl): detected aggregation rows — typed, operand-linked, membrane-guarded, excluded from records (loop H)"
```

---

### Task 4: Verification + residue register

- [ ] **Step 1: Full suite** (timeout 400000, foreground): `. .venv/bin/activate && python3 -m pytest -q`
Expected: **646 passed, 5 skipped** (629 + 4 + 9 + 4). Report real numbers; the fixture-iteration in Task 3 may have added a probe test — account for any delta explicitly.

- [ ] **Step 2: GrainCorp confirmation (LOCAL, uncommitted).** PDF at
`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf`; skip with a note if missing; never copy/commit.

```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from rdflib import Namespace, RDF
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
TAB = Namespace('https://w3id.org/iladub/tab#')
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop = RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'x')
r = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for reg in r.regions:
    if reg.verdict == 'asserted': print(reg.kind, reg.verdict, 'cells=', reg.cells)
print('score=', round(r.score, 4))
vals = [str(o) for _s,_p2,o in r.graph.triples((None, TAB.cellText, None))]
fused = [v for v in vals if v.count('20,000') > 1 or '56817 56787' in v]
print('fused cells:', fused if fused else 'NONE')
det = list(r.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
print('detected aggregation rows:', len(det))
"
```

Expected, and **report what you actually observe**:
- `fused cells: NONE`.
- **`detected aggregation rows: 17`** — the discriminating criterion (probed: 17 of 20 sparse candidates confirm; the 3 honest refusals are the two blank-measure totals and the Grand Total). If the count differs, list which rows confirmed and reconcile against the plan's probed table before touching anything.
- Score/cells expected unchanged (0.9496 / 509) — structural loop.

- [ ] **Step 3: Register + spec status.** `docs/superpowers/residues.md`: close **R4** for ruled documents (de-fusion + first-class subtotals; blank-total subtotals and unruled suppressed-key documents named as the open narrower forms; the row-group hierarchy loop now unblocked). Update the spec's `**Status:**` line with measured numbers, stating any deltas.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-30-subtotal-rows-design.md
git commit -m "docs: loop H measured outcome; R4 closed for ruled documents"
```

---

## Self-Review

**Spec coverage:** §1.1 de-fusion → Task 1; §1.2 detection → Task 2; §3.3 emission+membrane+feed → Task 3; success 1 (zero fused) → T1 + T4; success 2 (every confirmable subtotal typed, nesting + blank members) → T2 tests + T4's 17; success 3 (blank totals refused) → T2 `test_blank_total_is_never_confirmed` + T4's named refusals; success 4 (shipped subtotal fixtures unchanged — they classify RECORD_TABLE and never reach `assert_hier_region`, probed) → pinned by the full suite (their tests unchanged); success 5 (gate) → Global Constraints + docstrings. §4's "shipped-fixture delta asserted not accidental" resolves to *no delta by path* — stated in the probed values.

**Placeholder scan:** none — every step carries complete, copy-ready code and exact expectations. (An earlier draft planted a deliberately-wrong assertion with a fix-it note; removed — Loop F proved that pattern survives into commits.)

**Type consistency:** `detect_aggregation_rows(rows, grid) -> dict[int, (label_col, measure_col, members)]` — Task 2's tests unpack 3-tuples; Task 3's emission unpacks `_lcol, _mcol, members`. `RowBand(top, bottom, cells)` matches `rows.py`. `_cell_from(words, page)` matches `cells.py`. `HierRegion(grid, tree, rows, body_line)` matches `hierarchical.py`. Feed check uses `TAB.AggregationRow` (supertype, written explicitly by emission) — consistent with the both-types decision. `HRule(y, x0, x1)` — Task 1 instructs verifying the field order before writing; the veto reads only `.y`.
