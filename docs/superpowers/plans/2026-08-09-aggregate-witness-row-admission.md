# The aggregate witness as a row-admission axiom (R75) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Admit a measure-only row into the data grid when its printed value equals the exact
`Decimal` sum of the rows it stands over, closing R75 and moving the cbh oracle from 45/49 to
49/49 entry rows.

**Architecture:** A third, strictly-additive pass in `derive_data_grid`, running *after* the
grid is closed so the column universe, the measure set and `key_col` are already fixed. The
proposer is placement geometry (places into ≥1 measure column, no key ink, no index ink); the
disposer is exact arithmetic over cell values. They are independent — the proposer never reads
a value, the disposer never reads a position. The emitted row reuses the existing
`tab:DetectedAggregationRow` class from loop H; no new vocabulary is minted.

**Tech Stack:** Python 3.12, `rdflib`, `pdfplumber`, `pytest`, `reportlab` (synthetic
fixtures), exact `decimal.Decimal` arithmetic.

**Spec:** `docs/superpowers/specs/2026-08-09-aggregate-witness-row-admission-design.md`

## Global Constraints

- **The neurosymbolic gate (CLAUDE.md §8).** This work is **AXIOM**: a presence-and-equality
  test, open world, evidence-positive. **No tuned constant and no tolerance may be introduced.**
  Exact `Decimal` only, never float. A tuned constant here is a review failure.
- **Label text is NEVER read.** No `"Total"` suffix test, no language-specific token. Detection
  is sparsity, column position and arithmetic only.
- **Assert only what the source supports.** A row is admitted only when its supporting sum is
  *present*. Never infer an aggregate from absence.
- **The guard that must survive:** apple page 0 line 5, `2026 2025 2026 2025`, must stay refused.
- **The floor that must not move:** stem's document compile is `0.9654553611484971`.
- **The four existing oracles must not move:** apple p0 31/31, apple p1 28/28, stem p0 57/57,
  ons p7 46/46.
- **Run everything with Homebrew git on PATH:** prefix git commands with
  `PATH=/opt/homebrew/bin:$PATH` — this machine's system git shim is broken.
- **Corpus tests are skipped without the corpus.** Verify `corpus/` is populated before
  claiming a green run; a skipped oracle is not a passing oracle.

---

## File Structure

| file | responsibility | change |
| --- | --- | --- |
| `src/iladub/etkl/datagrid.py` | the grid derivation and its RDF emission | modify — 3 new module-level functions, 1 new `DataGrid` field, 1 param on `place_indexed`, the witness pass, the emission block |
| `tests/etkl/test_datagrid.py` | the grid's tests and its five transcribed oracles | modify — new unit tests, the two falsifiers, the inverted cbh pin |
| `vocab/ontology/tab-datagrid.ttl` | the grid ontology | modify — `tab:AggregateWitness` gains its second consequence |
| `docs/wiki/concepts/data-grid.md` | LLM-maintained synthesis | modify — increment |
| `docs/superpowers/residues.md` | the canonical residue register | modify — delete R75, amend R74, add the extraction-path row |

Everything lands in `datagrid.py`; no new module. The three new functions are pure and
module-level (not closures) precisely so the falsifiers can reach them without a PDF.

---

### Task 1: The two pure axiom functions, and the mutation falsifier (F1)

The disposer and the member rule, as pure functions over values and ordinals. Module-level so
that F1 can feed them cbh's **real** numbers without going through a PDF.

**Files:**
- Modify: `src/iladub/etkl/datagrid.py` (add after `reconciles`, ~line 226)
- Test: `tests/etkl/test_datagrid.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `_decimal(text) -> Decimal | None`
  - `aggregate_members(i: int, admitted: set[int], aggregates: set[int]) -> tuple[int, ...]`
  - `confirms_aggregate(cells: dict[int, str], member_cells: list[dict[int, str]]) -> bool`

- [ ] **Step 1: Write the failing tests**

Add to `tests/etkl/test_datagrid.py`, after the existing `test_reconciles_is_exact` (~line 73):

```python
# --- G8 as a ROW-ADMISSION axiom (spec 2026-08-09) ---------------------------------
# The member values below are the REAL cbh page-0 column-13 cells, read off the page.
# Panel 1 is lines 10-19; panel 4 is lines 69-73.
CBH_PANEL1_MEMBERS = ["30,000", "50,000", "48,904", "50,000", "50,000",
                      "22,727", "36,000", "27,273", "25,000", "35,000"]
CBH_PANEL1_TOTAL = "374,904"
CBH_PANEL4_MEMBERS = ["54,000", "5,850", "36,000", "60,000", "22,858"]
CBH_PANEL4_TOTAL = "178,708"


def test_decimal_reads_thousands_separators_and_unit_markers():
    from decimal import Decimal
    from iladub.etkl.datagrid import _decimal
    assert _decimal("374,904") == Decimal("374904")
    assert _decimal("8 962 258") == Decimal("8962258")     # SI/ISO 31-0 separator
    assert _decimal("$ 78,678") == Decimal("78678")
    assert _decimal("-1,200") == Decimal("-1200")
    assert _decimal("Mackay") is None
    assert _decimal("") is None
    assert _decimal(None) is None


def test_aggregate_members_stops_at_the_previous_aggregate():
    """Rule B of spec 2026-08-09 §2.1: the admitted rows above i, back to the previous
    aggregate row, EXCLUSIVE. Ordinal only — no geometry and no values."""
    from iladub.etkl.datagrid import aggregate_members
    admitted = set(range(10, 20)) | set(range(26, 42))
    assert aggregate_members(20, admitted, set()) == tuple(range(10, 20))
    # once line 20 is an aggregate, the next candidate must not re-count panel 1
    assert aggregate_members(42, admitted | {20}, {20}) == tuple(range(26, 42))


def test_aggregate_members_is_empty_at_the_top_of_a_page():
    """A boxhead has nothing above it, and a vacuous sum never confirms."""
    from iladub.etkl.datagrid import aggregate_members
    assert aggregate_members(5, {7, 8, 9}, set()) == ()


def test_confirms_aggregate_on_the_real_cbh_panels():
    """The premise R75 rests on, at the level of the disposer: cbh's printed panel totals
    equal the exact sum of the real member cells."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{13: v} for v in CBH_PANEL1_MEMBERS]
    assert confirms_aggregate({13: CBH_PANEL1_TOTAL}, members)
    members4 = [{13: v} for v in CBH_PANEL4_MEMBERS]
    assert confirms_aggregate({13: CBH_PANEL4_TOTAL}, members4)


def test_f1_tampering_the_real_total_by_one_refuses_the_row():
    """FALSIFIER F1 (spec §4). The arithmetic must be LOAD-BEARING for admission, not
    decorative: the corpus sweep found it refuses nothing on real evidence, so it is
    exercised here against the real cbh members with the printed total off by exactly one.
    Same tamper pattern as tests/etkl/fixtures.py:1711."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{13: v} for v in CBH_PANEL1_MEMBERS]
    assert not confirms_aggregate({13: "374,905"}, members)
    assert not confirms_aggregate({13: "374,903"}, members)


def test_confirms_aggregate_refuses_a_vacuous_sum():
    """Zero members is an honest refusal, never a 0 == 0 confirmation — the same rule
    `reconciles` makes."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({13: "0"}, [])
    assert not confirms_aggregate({13: "374,904"}, [])


def test_confirms_aggregate_refuses_a_non_numeric_cell():
    """A measure-only row of words is a reprinted boxhead, not an aggregate."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({4: "Accepted", 5: "Accepted"},
                                  [{4: "Accepted", 5: "Accepted"}])


def test_confirms_aggregate_requires_every_occupied_cell_to_reconcile():
    """A universal quantifier, not a count: one column reconciling is not a witness.
    This is what refuses a period header whose first column happens to sum."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{1: "100", 2: "10"}, {1: "200", 2: "20"}]
    assert confirms_aggregate({1: "300", 2: "30"}, members)
    assert not confirms_aggregate({1: "300", 2: "31"}, members)


def test_confirms_aggregate_refuses_a_column_with_no_summable_member():
    """A cell whose column no member populates has no witness — refuse, never treat the
    missing members as zero."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({1: "300", 3: "50"},
                                  [{1: "100"}, {1: "200"}])
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "/Volumes/WD Green/dev/git/iladub"
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "decimal or aggregate_members or confirms_aggregate or f1_tamper" -v
```

Expected: FAIL — `ImportError: cannot import name '_decimal' from 'iladub.etkl.datagrid'`.

- [ ] **Step 3: Write the implementation**

In `src/iladub/etkl/datagrid.py`, insert immediately after `reconciles` (which ends at line
225, just before `_boundaries_from_alignment`):

```python
def _decimal(text) -> Decimal | None:
    """A cell's value as an exact Decimal, or None when it is not a number.

    Thousands separators are stripped by the SAME convention `_SPACED_NUMBER` encodes
    (a space inside a digit run is an SI/ISO 31-0 separator), and a leading currency glyph
    is a tab:UnitMarker rather than part of the value. Exact Decimal, never float, never a
    tolerance — a tolerance here would be the tuned constant the §8 gate forbids."""
    if text is None:
        return None
    t = str(text).strip().replace(",", "").replace(" ", "").lstrip("$€£¥")
    try:
        return Decimal(t)
    except InvalidOperation:
        return None


def aggregate_members(i: int, admitted: set, aggregates: set) -> tuple[int, ...]:
    """G8's member rows: the admitted rows above `i`, back to the previous aggregate row,
    EXCLUSIVE. Ordinal only — it reads no geometry and no value.

    Rule B of spec 2026-08-09 §2.1. Measured INDISTINGUISHABLE from 'the maximal contiguous
    run of admitted rows above' on the whole corpus (both admit exactly cbh's four panel
    totals), and chosen because `rows.detect_aggregation_rows` already uses this shape, so
    the repo carries ONE member rule rather than two. Recorded as a reuse decision because
    the evidence does not choose between them."""
    stop = max((a for a in aggregates if a < i), default=-1)
    return tuple(j for j in range(stop + 1, i) if j in admitted)


def confirms_aggregate(cells: dict, member_cells: list) -> bool:
    """G8 tab:AggregateWitness as a ROW-ADMISSION disposer: EVERY occupied cell is numeric
    and equals the exact Decimal sum of that column over the member rows.

    Arithmetic only — it reads no position and never reads label text ('Total' is the tuned
    constant of natural language and is forbidden). The quantifier is UNIVERSAL, not a
    count: one column reconciling is not a witness, which is what refuses a period header
    whose leading column happens to sum.

    Two honest refusals, both deliberate: no members at all (a vacuous 0 == 0 never
    confirms, the same rule `reconciles` makes), and a cell whose column no member
    populates (a missing member is never read as a zero)."""
    if not cells or not member_cells:
        return False
    for k, text in cells.items():
        total = _decimal(text)
        if total is None:
            return False
        vals = [v for v in (_decimal(mc.get(k)) for mc in member_cells) if v is not None]
        if not vals or sum(vals) != total:
            return False
    return True
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "decimal or aggregate_members or confirms_aggregate or f1_tamper" -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
PATH=/opt/homebrew/bin:$PATH git add src/iladub/etkl/datagrid.py tests/etkl/test_datagrid.py
PATH=/opt/homebrew/bin:$PATH git commit -m "feat(datagrid): G8's disposer and member rule as pure functions, with F1

The falsifier first, per spec 2026-08-09 §4: the corpus sweep measured that the
arithmetic refuses NOTHING on real evidence, so it is exercised here against cbh's
real panel members with the printed total off by exactly one.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: The witness pass — wire the axiom into `derive_data_grid`

**Files:**
- Modify: `src/iladub/etkl/datagrid.py` — `DataGrid` (line 108), `place_indexed` (line 317),
  the admission block (lines 419-476)
- Test: `tests/etkl/test_datagrid.py` — the inverted cbh pin

**Interfaces:**
- Consumes: `aggregate_members`, `confirms_aggregate` from Task 1.
- Produces: `DataGrid.aggregates: dict[int, tuple[int, ...]]` — admitted line index → member
  line indices, consumed by Task 4's emission.

- [ ] **Step 1: Write the failing test**

In `tests/etkl/test_datagrid.py`, **replace** `test_cbh_p0_known_defects_are_pinned_not_hidden`
(lines 684-698) with the following two tests. The `MISS` half of that pin is what R75 closes;
the `LEAK` half stays exactly as it was.

```python
@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_table_b_leak_is_pinned_not_hidden():
    """LEAK, still open as R74: line 75 belongs to the SECOND table on the page (stock at
    port) and is admitted into the roster's grid. Recorded in the data-grid spec §8.4 as
    'cbh's rectangle spans a stacked panel'; tab:StackedGrids is defined and not derived.

    Its measure is in fact table A's exact grand total (374,904 + 737,289 + 660,363 +
    178,708 = 1,951,264 — spec 2026-08-09 §3.6), so the line carries two tables' ink."""
    g = derive_data_grid(CBH, 0)
    assert set(g.rows) & CBH_P0_TABLE_B == {75}, "the table-B leak changed"


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_admits_the_four_panel_totals_by_arithmetic():
    """R75 CLOSED. The four per-panel volume totals carry a measure and no key, so the
    placement floor refused them as unplaceable. G8's aggregate witness admits them: each
    printed value is the EXACT Decimal sum of the rows it stands over.

    No label text is read — 'Total' is never printed on these lines at all."""
    g = derive_data_grid(CBH, 0)
    admitted = set(g.rows)
    missed = sorted(CBH_P0_PANEL_TOTALS - admitted)
    assert not missed, f"panel totals missed: {missed}"
    # the member counts are the four panels' vessel-row counts, and they sum to 45
    assert {k: len(v) for k, v in g.aggregates.items()} == {20: 10, 42: 16, 63: 14, 74: 5}
    assert sum(len(v) for v in g.aggregates.values()) == len(CBH_P0_VESSEL_ROWS) == 45
    # every entry row of table A, aggregates included
    assert CBH_P0_DATA <= admitted, f"missed: {sorted(CBH_P0_DATA - admitted)}"
    assert len(CBH_P0_DATA) == 49
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "cbh_p0" -v
```

Expected: `test_cbh_p0_admits_the_four_panel_totals_by_arithmetic` FAILS with
`panel totals missed: [20, 42, 63, 74]`. The other three cbh tests PASS.

- [ ] **Step 3: Add the `aggregates` field to `DataGrid`**

In `src/iladub/etkl/datagrid.py`, in the `DataGrid` dataclass (line 108), add after
`refusals`:

```python
    aggregates: dict = field(default_factory=dict)  # line index -> member line indices
```

- [ ] **Step 4: Add the per-call floor override to `place_indexed`**

Change the signature (line 317) and the floor line (line 351):

```python
    def place_indexed(rs: list[Run], measure_cols: set,
                      min_cells: int | None = None) -> dict | None:
```

```python
        floor = min_cells if min_cells is not None else (1 if outside else 2)
```

Leave the docstring's existing text and add this paragraph to the end of it:

```
        `min_cells` is a PER-CALL override used only by the aggregate-witness pass, which
        must see single-cell candidates. G2's own call site passes nothing, so no line
        reaches RowAddressability that does not reach it today — the floor is not lowered,
        it is by-passed for candidates the arithmetic then has to justify (spec §5.1).
```

- [ ] **Step 5: Write the witness pass**

In `derive_data_grid`, the block currently reads:

```python
    if not rows:
        return None
    for i in range(len(lines)):
        refusals.setdefault(i, "unplaceable") if i not in set(rows) else None
```

Replace it with:

```python
    if not rows:
        return None

    # --- G8 tab:AggregateWitness, as a ROW-ADMISSION axiom (spec 2026-08-09).
    #
    # STRICTLY ADDITIVE, and it runs AFTER the grid is closed: the column universe, the
    # measure set and key_col are already fixed, so this pass cannot change the grid's
    # identity and §8.5's non-convergence hazard cannot arise. Members always lie ABOVE
    # their candidate, so ONE top-down pass suffices — no iteration, no fixed point.
    #
    # The proposer is placement geometry and reads no value; the disposer is exact
    # arithmetic and reads no position. Neither can manufacture the other's evidence.
    #
    # Measured over the whole corpus (27 pages): 86 lines proposed, 4 admitted — exactly
    # cbh page 0's four panel totals, zero false admissions.
    cells_by_line = {}
    for i in range(len(lines)):
        h = place_indexed(runs[i], measures, min_cells=1)
        if h:
            cells_by_line[i] = h
    aggregates: dict = {}
    admitted = set(rows)
    for i in range(len(lines)):
        if i in admitted:
            continue
        h = cells_by_line.get(i)
        # PROPOSER: places into at least one measure column, carries no ink in the key
        # column and none in the index block outside the rectangle.
        if not h or key_col in h or index_ink(runs[i]):
            continue
        occupied = {k: t for k, t in h.items() if not is_blank(t)}
        if not (measures & set(occupied)):
            continue
        members = aggregate_members(i, admitted, set(aggregates))
        # DISPOSER: exact arithmetic over the member rows' cells.
        if confirms_aggregate(occupied, [cells_by_line[m] for m in members
                                         if m in cells_by_line]):
            aggregates[i] = members
            admitted.add(i)
            rows.append(i)
            refusals.pop(i, None)
        elif members and all(_decimal(t) is not None for t in occupied.values()):
            # The arithmetic actually SPOKE, so the record names the rule that decided.
            # Every other candidate keeps the reason that already refused it, which is why
            # apple's boxhead stays 'RowAddressability/no-key' and stem's carried-refusal
            # count is unchanged.
            refusals[i] = "AggregateWitness/no-reconciliation"
    rows.sort()

    for i in range(len(lines)):
        refusals.setdefault(i, "unplaceable") if i not in set(rows) else None
```

- [ ] **Step 6: Record the axiom in `conforms` and carry `aggregates` onto the grid**

In the `return DataGrid(...)` at the end of `derive_data_grid`, add `"AggregateWitness"` to
the `conforms` tuple and pass the new field:

```python
    return DataGrid(
        rows=tuple(rows),
        columns=tuple(columns),
        universe=universe,
        conforms=("ColumnHomogeneity", "NonDegeneracy", "RowAddressability",
                  "ColumnAlignment", "SeedFollowsUniverse", "AggregateWitness"),
        refusals=refusals,
        aggregates=aggregates,
    )
```

- [ ] **Step 7: Run the cbh oracle**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "cbh_p0" -v
```

Expected: 4 passed — the four panel totals admitted with member counts
`{20: 10, 42: 16, 63: 14, 74: 5}`, no metadata leaked, the table-B pin unchanged.

- [ ] **Step 8: Run the whole grid suite for regressions**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -v
```

Expected: all pass. The four other oracles (apple p0 31/31, apple p1 28/28, stem p0 57/57,
ons p7 46/46) and stem's refusal count are unchanged — if any of them moves, **stop**: the
pass is not additive and the cause is upstream, not in the assertion.

- [ ] **Step 9: Commit**

```bash
PATH=/opt/homebrew/bin:$PATH git add src/iladub/etkl/datagrid.py tests/etkl/test_datagrid.py
PATH=/opt/homebrew/bin:$PATH git commit -m "feat(datagrid): admit aggregate rows by exact arithmetic — cbh 45/49 -> 49/49

R75. A third, strictly-additive pass after the grid is closed, so the columns and
key_col cannot move. The placement floor is by-passed per call for candidates the
arithmetic then has to justify; G2's own call site is untouched.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: The negative fixture (F2) and the worked example that conforms

`tests/etkl/test_datagrid.py` builds synthetic pages with `reportlab` — follow
`_conforming_page` (line 94) exactly. CLAUDE.md requires every vocabulary to ship with a
worked example that conforms **and** a negative that must fail; this task ships both for the
new axiom.

**The falsifier's whole point:** apple's period header is currently refused because it sits
*above* every data row, not because its sum fails. F2 puts a bare period header *below*
admitted rows so position can no longer save the guard, and asserts the **refusal reason** —
which only exists once the arithmetic is the decider. Asserting mere absence from `g.rows`
would pass vacuously and prove nothing.

**Files:**
- Test: `tests/etkl/test_datagrid.py`

**Interfaces:**
- Consumes: `DataGrid.aggregates` and the `AggregateWitness/no-reconciliation` refusal reason
  from Task 2.
- Produces: nothing consumed later.

- [ ] **Step 1: Write the failing tests**

Add to `tests/etkl/test_datagrid.py`, after `test_worked_example_conforms` (line 125):

```python
def _aggregating_page(tmp_path, total="1200"):
    """A register with a measure-only total row: no label anywhere on the line, the value
    alone under the first quantity column. The rows sum to 1200 and 1240."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / f"aggregating-{total}.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(60, 780, "QUARTERLY REGISTER")            # title -> metadata
    for i, (name, a, b) in enumerate([("North", "120", "130"), ("South", "240", "250"),
                                      ("East", "360", "370"), ("West", "480", "490")]):
        y = 720 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    c.drawString(200, 720 - 4 * 20, total)                 # the measure-only total row
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_worked_example_admits_a_measure_only_aggregate(tmp_path):
    """The worked example that CONFORMS for G8-as-row-admission: 120+240+360+480 = 1200,
    exactly, so the label-less row is a row of the grid."""
    g = derive_data_grid(_aggregating_page(tmp_path, total="1200"), 0)
    assert g is not None
    assert len(g.rows) == 5, f"4 data rows + the aggregate, got {g.rows}"
    assert len(g.aggregates) == 1
    (line, members), = g.aggregates.items()
    assert len(members) == 4
    assert "AggregateWitness" in g.conforms


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_negative_example_refuses_a_total_that_does_not_reconcile(tmp_path):
    """The negative that MUST fail: one off by a single unit. Exact, never a tolerance."""
    g = derive_data_grid(_aggregating_page(tmp_path, total="1201"), 0)
    assert len(g.rows) == 4, f"the non-reconciling row must stay out, got {g.rows}"
    assert not g.aggregates
    assert "no-reconciliation" in str(g.refusals.get(5)), g.refusals


def _period_header_below_data_page(tmp_path):
    """FALSIFIER F2 (spec §4). A bare period header REPRINTED BELOW the data rows, so it
    has a non-empty member run and its position can no longer refuse it. Only the
    arithmetic can, and it must."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "period-header-below.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(60, 780, "CONDENSED STATEMENTS OF OPERATIONS")
    for i, (name, a, b) in enumerate([("Products", "120", "130"), ("Services", "240", "250"),
                                      ("Total net sales", "360", "380")]):
        y = 750 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    y = 750 - 3 * 20
    c.drawString(200, y, "2026")           # the bare period header, BELOW the data
    c.drawString(300, y, "2025")
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_f2_a_period_header_below_the_data_is_refused_by_the_arithmetic(tmp_path):
    """FALSIFIER F2. Measured on the real corpus, every bare period header is refused
    because it sits ABOVE every data row — the arithmetic refuses nothing at all, so its
    refusal branch would ship unexercised (spec §3.3).

    Here the header has 3 admitted rows above it, so only the sum can refuse it. The
    assertion is on the REASON, not on absence: absence would pass vacuously even if the
    witness were never consulted.

    measured-on-fixture: no real corpus document reprints a period header below its data."""
    path = _period_header_below_data_page(tmp_path)
    g = derive_data_grid(path, 0)
    assert g is not None
    # locate the header by its CONTENT, not by assuming it is the last line
    lines = [l for l in sorted(text_lines(extract_words(path, 0)), key=lambda l: l.top)
             if l.words]
    header_line = next(i for i, l in enumerate(lines)
                       if [w.text for w in sorted(l.words, key=lambda w: w.x0)] == ["2026", "2025"])
    assert g.refusals[header_line] == "AggregateWitness/no-reconciliation", g.refusals
    assert not g.aggregates
    assert len(g.rows) == 3, f"only the three data rows, got {g.rows}"
```

- [ ] **Step 2: Run the tests**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "measure_only_aggregate or does_not_reconcile or f2_a_period_header" -v
```

Expected: 3 passed. If `test_f2_...` fails on the refusal *reason* while the row is still
absent from `g.rows`, the arithmetic was never consulted — that is the vacuous pass this test
exists to detect. Debug the proposer's conditions before touching the assertion.

- [ ] **Step 3: Prove F2 is not vacuous**

Temporarily comment out the `elif members and all(...)` branch in `derive_data_grid`, re-run
`test_f2_a_period_header_below_the_data_is_refused_by_the_arithmetic`, confirm it **FAILS**,
then restore the branch. Do not commit the mutation. This is the mutation check the data-grid
loop's lesson 3 requires of every guard.

- [ ] **Step 4: Commit**

```bash
PATH=/opt/homebrew/bin:$PATH git add tests/etkl/test_datagrid.py
PATH=/opt/homebrew/bin:$PATH git commit -m "test(datagrid): F2 and the worked example for G8-as-row-admission

F2 puts a bare period header BELOW the data so position cannot refuse it and only
the arithmetic can — the branch the corpus never reaches. Asserts the refusal
REASON, since asserting absence would pass vacuously. Mutation-checked.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Emission — reuse `tab:DetectedAggregationRow`

**Files:**
- Modify: `src/iladub/etkl/datagrid.py` — `emit_data_grid` (lines 523-546)
- Test: `tests/etkl/test_datagrid.py`

**Interfaces:**
- Consumes: `DataGrid.aggregates` from Task 2.
- Produces: `tab:DetectedAggregationRow` / `tab:aggregationFunction` / `tab:aggregates`
  triples on the emitted grid.

- [ ] **Step 1: Write the failing test**

Add to `tests/etkl/test_datagrid.py`, after
`test_emitted_grid_answers_why_from_the_graph_alone`:

```python
@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_emitted_aggregate_rows_reuse_the_loop_h_class():
    """No new class is minted: an aggregate row of the grid is typed with the SAME
    tab:DetectedAggregationRow the extraction path already uses, carrying its operands, so
    tab:DetectedAggregationRowShape is satisfied as that shape already stands."""
    from rdflib import Graph, URIRef
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(CBH, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(CBH, 0)
    g = Graph()
    uri = emit_data_grid(g, grid, lines, URIRef("urn:test:cbh"), 0)

    agg = set(g.subjects(
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("https://w3id.org/iladub/tab#DetectedAggregationRow")))
    assert len(agg) == 4, f"expected the four panel totals, got {len(agg)}"
    for a in agg:
        funcs = list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregationFunction")))
        assert [str(f) for f in funcs] == ["sum"], funcs
        ops = list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregates")))
        assert len(ops) >= 1, "a detected aggregation row needs at least one operand"
        # every operand is a row of THIS grid
        assert all(str(o).startswith(str(uri) + "-r") for o in ops), ops
    counts = sorted(len(list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregates"))))
                    for a in agg)
    assert counts == [5, 10, 14, 16]


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_emitted_aggregate_rows_satisfy_their_shape():
    """The closed-world membrane: pySHACL over the emitted grid, against the shipped
    tab:DetectedAggregationRowShape — unedited by this loop."""
    from rdflib import Graph, URIRef
    from pyshacl import validate
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(CBH, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(CBH, 0)
    g = Graph()
    emit_data_grid(g, grid, lines, URIRef("urn:test:cbh"), 0)
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, text = validate(g, shacl_graph=shapes, inference="rdfs", advanced=True)
    assert conforms, text
```

- [ ] **Step 2: Run to verify it fails**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "loop_h_class or satisfy_their_shape" -v
```

Expected: FAIL — `expected the four panel totals, got 0`.

- [ ] **Step 3: Implement the emission**

In `emit_data_grid`, replace the row-emission loop header (line 523) so the row URIs are
resolvable by line index before the loop body runs, and add the aggregate typing.

Replace:

```python
    for r_i, line_idx in enumerate(grid.rows):
        line = lines[line_idx]
        r_uri = URIRef(f"{grid_uri}-r{r_i}")
        g.add((r_uri, RDF.type, TAB.LeafRow))
```

with:

```python
    row_uri_by_line = {line_idx: URIRef(f"{grid_uri}-r{r_i}")
                       for r_i, line_idx in enumerate(grid.rows)}
    for r_i, line_idx in enumerate(grid.rows):
        line = lines[line_idx]
        r_uri = row_uri_by_line[line_idx]
        g.add((r_uri, RDF.type, TAB.LeafRow))
        # G8: an aggregate row is typed with the class the extraction path ALREADY uses
        # (tab.ttl:379, loop H) and carries its member rows as operands, so the shipped
        # tab:DetectedAggregationRowShape is satisfied without being edited. No new class
        # is minted for the grid-side case — it is the label-less case of one rule.
        for m in grid.aggregates.get(line_idx, ()):
            g.add((r_uri, RDF.type, TAB.DetectedAggregationRow))
            g.add((r_uri, TAB.aggregationFunction, Literal("sum")))
            if m in row_uri_by_line:
                g.add((r_uri, TAB.aggregates, row_uri_by_line[m]))
```

- [ ] **Step 4: Run to verify it passes**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -k "loop_h_class or satisfy_their_shape" -v
```

Expected: 2 passed.

- [ ] **Step 5: Run the full grid suite**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
PATH=/opt/homebrew/bin:$PATH git add src/iladub/etkl/datagrid.py tests/etkl/test_datagrid.py
PATH=/opt/homebrew/bin:$PATH git commit -m "feat(datagrid): emit aggregate rows as tab:DetectedAggregationRow

Reuses loop H's class and properties rather than minting a grid-side twin: the
grid case is the label-less case of one rule. The shipped shape is satisfied
unedited, and pySHACL proves it.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: The ontology, the register, and the wiki

**Files:**
- Modify: `vocab/ontology/tab-datagrid.ttl` (line 318, `tab:AggregateWitness`)
- Modify: `docs/superpowers/residues.md` (rows R74 and R75)
- Modify: `docs/wiki/concepts/data-grid.md` (line 84 and frontmatter)

**Interfaces:**
- Consumes: the behaviour shipped in Tasks 2 and 4.
- Produces: nothing consumed later.

- [ ] **Step 1: Extend `tab:AggregateWitness` with its second consequence**

In `vocab/ontology/tab-datagrid.ttl`, the `tab:AggregateWitness` comment currently ends with:

```
HONEST LIMIT: a grouping level with no totals has no witness under this axiom and stays in the
grid. The axiom is sound, not complete."""@en .
```

Replace that closing paragraph with:

```
SECOND CONSEQUENCE — ROW ADMISSION (2026-08-09). The same arithmetic admits a ROW: a
measure-only row (ink in at least one tab:MeasureColumn, none in the key column and none in
the index block) is an aggregate row of the grid when EVERY occupied cell equals the exact
Decimal sum of that column over its member rows — the admitted rows above it, back to the
previous aggregate row, exclusive. One axiom, two uses: totals recognise the key column, and
totals recognise themselves.

Measured on the CBH shipping stem page 0: the four per-panel volume totals (374,904 / 737,289
/ 660,363 / 178,708) carry no label at all, so tab:RowAddressability never sees them and the
placement floor refuses them. The witness admits all four, over 10, 16, 14 and 5 member rows
respectively. Corpus-wide, 86 rows are proposed and exactly these 4 are admitted.

Such a row is typed tab:DetectedAggregationRow — the class the extraction path already uses —
never a grid-side twin.

HONEST LIMIT: a grouping level with no totals has no witness under this axiom and stays in the
grid, and a multi-level total whose members are themselves totals will not reconcile against a
member run containing both levels, so it is refused. The axiom is sound, not complete."""@en .
```

- [ ] **Step 2: Verify the ontology still parses and ownership holds**

```bash
.venv/bin/python -m pytest tests/test_source_ownership.py tests/etkl/test_tab_vocab.py -v
```

Expected: all pass. (The edit touches only a `tab:` subject, which is a namespace we own.)

- [ ] **Step 3: Close R75 and amend R74 in the register**

In `docs/superpowers/residues.md`:

**Delete the entire R75 row** — the loop that closes a residue deletes its row in the same
change.

**Amend the R74 row.** Its "where it was measured" cell currently ends with
`Recorded in prose at `2026-08-08-data-grid-types-elements-axioms.md` §8.4 (*'cbh's rectangle
spans a stacked panel'*) but never given a register row`. Append to that same cell:

```
. AMENDED 2026-08-09 (loop-aggregate-witness): line 75's measure is table A's EXACT grand total — 374,904 + 737,289 + 660,363 + 178,708 = 1,951,264 — so the line carries TWO tables' ink (table B's title and table A's grand total) rather than being a stray table-B row. Whoever derives `tab:StackedGrids` must split the LINE, not merely exclude it
```

**Add a new row** after R76:

```
| R77 | **cbh's four panel totals are missed on the SCORE path too, for the identical no-label reason** — `rows.detect_aggregation_rows` (loop H) requires exactly two occupied columns, one numeric and one not, so a label-less total is not even a candidate | loop-aggregate-witness, 2026-08-09. The data grid now admits all four (R75 closed), but the grid is NOT on cbh page 0's score path: `compile_tables` reports `asserted=66, escalated=879, score=0.0698`, and `datagrid_fallback` fires only when `asserted == 0 and escalated == 0`. So the four rows are read by the grid and still unread by the compile | Scope: R75's residue was measured on the transcribed grid oracle, and loop H's nesting rule ("back to the previous CONFIRMED aggregation row whose label column <= L") is keyed on the label column a label-less candidate does not have — relaxing it is its own slice with its own oracle | Give `detect_aggregation_rows` a label-less candidate shape whose nesting level comes from something other than the label column, and re-measure cbh p0. Expected movement is small and real: 4 cells of 945, 0.0698 -> ~0.074 |
```

- [ ] **Step 4: Verify the register still lints**

```bash
.venv/bin/python -m pytest tests/test_doc_governance.py -v
```

Expected: all pass.

- [ ] **Step 5: Increment the wiki page**

In `docs/wiki/concepts/data-grid.md`, the G8 bullet (line 84) currently reads
"a column is an index column when rows exist whose measures…". Extend that bullet to state
both consequences:

```markdown
- **G8 `tab:AggregateWitness`** — a column is an index column when rows exist whose measures
  reconcile exactly with the rows sharing a value in it; and, by the **same arithmetic**, a
  *measure-only row* is an aggregate row of the grid when every occupied cell equals the exact
  `Decimal` sum over the rows it stands over (the admitted rows above it, back to the previous
  aggregate, exclusive). One axiom, two uses. Measured on cbh page 0: the four label-less panel
  totals (374,904 / 737,289 / 660,363 / 178,708) are admitted over 10, 16, 14 and 5 members;
  corpus-wide 86 rows are proposed and exactly those 4 admitted. Such a row is typed with loop
  H's existing `tab:DetectedAggregationRow`, not a grid-side twin. *(confidence: high — five
  transcribed oracles, mutation-checked.)*
```

Update the frontmatter: set `updated: 2026-08-09` and add
`docs/superpowers/specs/2026-08-09-aggregate-witness-row-admission-design.md` to `sources:`.

- [ ] **Step 6: Commit**

```bash
PATH=/opt/homebrew/bin:$PATH git add vocab/ontology/tab-datagrid.ttl docs/superpowers/residues.md docs/wiki/concepts/data-grid.md
PATH=/opt/homebrew/bin:$PATH git commit -m "docs(R75): close the residue, amend R74, record G8's second consequence

R75's row is deleted by the loop that closes it. R74 is amended with the grand-total
arithmetic so tab:StackedGrids starts from a corrected premise. R77 escalates the
extraction-path counterpart rather than letting it look covered.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Prove the loop closed — the full regression gate

The loop-definition-of-done gate. Nothing here is asserted from reading; every number is run.

**Files:**
- No production changes. Any failure sends you back to the task that caused it.

- [ ] **Step 1: Confirm the corpus is present**

```bash
ls corpus/ag-trade corpus/financial corpus/gov-stats corpus/health
```

Expected: 6 PDFs. A skipped oracle is **not** a passing oracle — if the corpus is missing,
fetch it with `.venv/bin/python scripts/fetch_corpus.py` before continuing.

- [ ] **Step 2: The five oracles**

```bash
.venv/bin/python -m pytest tests/etkl/test_datagrid.py -v
```

Expected: all pass, including apple p0 31/31, apple p1 28/28, stem p0 57/57, ons p7 46/46
unchanged, and cbh 49/49 with `{20: 10, 42: 16, 63: 14, 74: 5}`.

- [ ] **Step 3: The adjudicated floor**

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from iladub.etkl.document import compile_document
r = compile_document('corpus/ag-trade/graincorp-stem-2026-07-31.pdf', validate_shapes=False)
print(repr(r.score))
assert r.score == 0.9654553611484971, r.score
print('stem floor holds')
"
```

Expected: `0.9654553611484971` exactly. If it moved, **stop and report** — this is the only
adjudicated floor and it outranks the new axiom.

- [ ] **Step 4: cbh's score is unchanged, as §3.4 predicts**

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from iladub.etkl.compile import compile_tables
r = compile_tables('corpus/ag-trade/cbh-stem-2026-08-03.pdf', 0, validate_shapes=False)
print('score', r.score, 'asserted', r.asserted, 'escalated', r.escalated)
assert r.score == 0.06984126984126984, r.score
print('unchanged, as predicted — the grid is not on this score path (R77)')
"
```

Expected: `0.06984126984126984`. A *change* here is the surprise worth investigating, not the
constancy — the grid is not on this page's score path.

- [ ] **Step 5: The full suite**

```bash
.venv/bin/python -m pytest -q 2>&1 | tail -20
```

Expected: green. Report the exact pass/fail/skip counts — do not summarise as "tests pass".

- [ ] **Step 6: Commit any test-count adjustments and report**

If nothing changed, there is nothing to commit. Report, with the real numbers:

- cbh oracle recall before → after
- the four other oracles, unchanged
- stem's document floor, verbatim
- cbh's page score, unchanged, and why that is expected
- the full-suite counts

---

## Self-Review

**Spec coverage:**

| spec section | task |
| --- | --- |
| §2 proposer / disposer | Task 2 Step 5 |
| §2.1 member rule B | Task 1 (`aggregate_members`) |
| §3.1 the four totals reconcile | Task 1, Task 2 |
| §3.3 the weakness | Tasks 1 (F1) and 3 (F2) |
| §3.5 reuse `tab:DetectedAggregationRow` | Task 4 |
| §3.6 R74 amendment | Task 5 Step 3 |
| §4 F1 | Task 1 Step 1 |
| §4 F2 | Task 3 Step 1, mutation-checked at Step 3 |
| §5.1 third pass, `min_cells` per call | Task 2 Steps 4-5 |
| §5.2 emission | Task 4 Step 3 |
| §5.3 refusal names the deciding rule | Task 2 Step 5 (`elif` branch), asserted in Task 3 |
| §5.4 AXIOM classification | Global Constraints + Task 1 docstrings |
| §5.5 honest limit | Task 5 Step 1 (ontology comment) |
| §6 verification | Task 6 |
| §7 R77 escalation | Task 5 Step 3 |
| §8 what gets recorded | Task 5 |

**Placeholder scan:** none. Every code step carries the actual code; every test carries real
values read off the corpus (`CBH_PANEL1_MEMBERS`, `CBH_PANEL4_MEMBERS`).

**Type consistency:** `aggregate_members(i, admitted, aggregates) -> tuple[int, ...]` and
`confirms_aggregate(cells, member_cells) -> bool` are defined in Task 1 and called with those
exact signatures in Task 2. `DataGrid.aggregates` is `dict[int, tuple[int, ...]]` in Task 2 and
read as such in Tasks 3 and 4. `Literal("sum")` matches `document.py:925` and `holon.py:455`.
