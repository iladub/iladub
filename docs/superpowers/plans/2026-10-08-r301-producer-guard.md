# R301 producer guard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance — [[R301]].

**Doc impact: none.** It is inherited from the spec: no vocabulary term, shape or published query
changes.

**Goal:** fed-h41 compiles with validation on. Each table whose cell an author's rule separates is
withdrawn and escalated at the site that admitted it, and its ink is booked once.

**Architecture:** a new module, `ruleguard.py`, runs `tab:RuleSeparatedInkShape`'s own `sh:select`
over the page graph. For each owner table it withdraws the table's extent, mints one refusal
decision that supersedes the chain head, escalates the region and moves the report's tokens.
`compile_tables` calls it at two sites: before the adoption gate, and over adoption's new graph
before anything is installed. If it fires at the second site, adoption is refused whole.
`build_ledger` joins appended regions to their own lines (I2). `CompilationReport` reports the
adoption outcome, so the document driver stops inferring it.

**Tech Stack:** Python, rdflib, pySHACL/rudof through `membrane`, and pytest (`-m corpus` for
held-out runs).

**Spec:** `docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md`. §§ 2–7 apply, and
**§ 8 overrides any earlier sentence it contradicts.** Seams:
`docs/superpowers/2026-10-08-r301-plan-seams-handoff.md` § 1 (U1, U2, U4, M1–M9).

**Measured base.** Every `file:line` below was re-read on `main` at `8e36e0c`.
`git diff --stat cb21b49 main -- src vocab` is empty, so the spec's `cb21b49` baseline and the
handoff's `6442818` line numbers both hold. Re-measure any line before writing against it, if
`main` has moved.

## Global Constraints

- **CLAUDE.md § 8 gate.** The select is AXIOM and is **read from** `tab:RuleSeparatedInkShape`'s
  `sh:select` (`vocab/shapes/tab-shapes.ttl:597-616`), never copied into Python or a `.rq`.
  Everything else is PROCEDURAL glue and carries **no constant**. The one literal, confidence
  `0.0`, cites `holon.py:164-167`.
- **R89, the membrane stays the backstop.** No shape is weakened, exempted or skipped. A graph that
  bypasses the guard is still refused (O3).
- **No new vocabulary.** If any step needs a `dec:`/`tab:` term that does not exist, **stop**:
  that is a spec change (spec § 7).
- **Spec § 8 S2: the refusal is written directly**, never through `ReadingRecorder`/`BandRecorder`.
  - IRI: `{doc}#region{i}-refusal`.
  - `rdfs:label "refusal"`.
  - `dec:order`: the head's order + 1, or `0` when the head has none. That is § 8's flagged
    interpretation, adopted here.
  - `dec:regarding {doc}#region{i}`, plus `dec:rationale` and `dec:decidedBy etkl:reader`
    (`decisionlog.py:24`).
  - Options `admit` and `refuse`, with `dec:chosen` → `refuse`.
  - `dec:supersedes` → the chain head.
- **Raise when there is no head.** The guard raises when no standing decision exists (spec § 2.3,
  R89 producer-side).
- **`_band_subgraph` is not changed** (spec § 2.2, § 7).
- **Function-local imports only** between `compile` and `document`/`ruleguard` (U4: a top-level
  `from .document import …` in `compile.py` is circular).
- **Corpus runs are serial: one full-document compile per process, never two at once.** The memory
  kills are recorded. Held-out tests carry `pytest.mark.corpus` and `skipif` on the file
  (`tests/test_corpus_stem.py:8-14`).
- **Falsification is mandatory per task** (CLAUDE.md § Plan authoring rule 4). Every task report
  carries a `## FALSIFICATION` block: remove or invert the subject, show the pinning test fail,
  restore it, and show the suite green.
- **A plan-supplied test is a proposition.** If one cannot be made to pass, report it as a plan
  defect and substitute the satisfiable form with the same force. Never weaken an assertion.

## Review Focus

1. **A band whose `verdict` is not its last judgement.** S3 requires the refusal to be the chain's
   **last** row. The order is head + 1, but a band can record judgements after `verdict` (for
   example `transposed` and `row_grouped` at `compile.py:1339,1420`, which may follow it). If
   another decision regarding the region carries an order ≥ head + 1, the refusal is not last, or
   it ties. Task 3's chain test pins the synthetic case, and Task 6's O2 pins fed-h41. **If O2
   fails for this reason, stop and re-rule.** Do not change the order rule; it is § 8's.
2. **A sibling grid, or the residue, under a withdrawn table's prefix** (S1). This is pinned in
   Task 3. No corpus page exercises it (handoff § 4).
3. **A refused cell whose owner maps to zero reports, or to several.** The guard must leave the
   graph untouched so that the membrane refuses loudly. This is pinned in Task 3. It is unreached on
   the corpus (U3).
4. **Adoption after a fallback grid was withdrawn, where the re-derived grid is not refused.** The
   adopted grid then appends after the escalated fallback region. Spec § 7 does not adopt grid by
   grid, and nothing on the corpus reaches this (U1: the re-derived grid is the refused one). The
   driver must not crash. Its existing `grid_uri is None` branch stays, and its note now names the
   observed outcome (Task 6).
5. **A page with no rule.** `carry_from_pdf` adds nothing, the select returns nothing, and the guard
   must be the identity byte for byte (O4). This is pinned by every existing test, and by the Task 7
   sweep.

---

### Task 0: Record the baseline (no source change)

**Files:**
- Create: `tests/data/r301-fed-h41-baseline.json`. It holds per-page, per-region
  `(verdict, reason, cells, tokens_asserted, tokens_escalated)`, page `asserted`/`escalated`, and
  `adopted`. **No `ascii`, no cell text**: the held-out document's content is not committed, only
  derived counts.
- Modify: `scripts/corpus_verdict_snapshot.py`. Add `--pdf <path>`, so that one document per
  process can be snapshotted into `<out-dir>`. Today it compiles every `corpus/**/*.pdf` in one
  process (`scripts/corpus_verdict_snapshot.py`, `main`).

**Interfaces:**
- Produces: the baseline JSON that Task 6's O1 test reads, and `<scratch>/before/` snapshots of
  all 11 documents for Task 7.

- [ ] **Step 1.** On this branch, before any `src/` change, compile fed-h41 with
  `compile_document("held-out/fed-h41-2025-01-02.pdf", validate_shapes=False)`. With validation
  on it raises `MembraneRefusal`, which is the defect. Write the JSON.
  - Expected document figure: 2902/500 (0.8530), with adopted = [2, 3, 5, 8, 10] (G1).
  - **If either differs, stop.** The spec's baseline does not hold.
- [ ] **Step 2.** Snapshot every corpus and held-out document, one process each and serially, into
  the scratchpad (`before/`). fed-h41 is skipped in `before/`: it aborts under
  validation, and Step 1's JSON is its baseline. Record each figure in the task report.
- [ ] **Step 3.** Commit the JSON and the script change.

---

### Task 1: An appended region carries its lines and its text (spec § 2.4 d; I2's carrier)

**Files:**
- Modify: `src/iladub/etkl/compile.py`:
  - add the field after `supersedes` (`:785-788`);
  - change the fallback report (`:1918-1920`).
- Test: `tests/etkl/test_r301_appended_region.py`.

**Interfaces:**
- Produces: `RegionReport.line_indices: tuple[int, ...] = ()`. These are the indices into the
  page's `_lines` (the fallback's `text_lines(...)` filtered on `ln.words` and sorted by `top`)
  that this **appended** region read. It is set to `tuple(_grid.rows)` on the fallback branch, and
  it stays `()` on every band report.
- Produces: the fallback report's `ascii`, which becomes
  `roundtrip.render_ascii(Band(lines=tuple(_lines[i] for i in _grid.rows), top=…, bottom=…))`.
  `render_ascii` reads `band.lines` only (`roundtrip.py:137-150`).
- Invariant: the field is **defaulted and appended last**. All 23 positional `RegionReport(`
  calls in `compile.py`, plus `tests/etkl/test_printed_total.py:573`, stand unchanged (M6).

**MEASURE before writing the test:** find an existing synthetic fixture that reaches the fallback
branch (`compile.py:1900`, `asserted_total == 0 and escalated_total == 0`) and yields an appended
`tab:DataGrid` region. Start with `grep -rn "datagrid_fallback\|DataGrid" tests/etkl/ | head`.
The R224 D2 tests are the likely home. If none exists, stop and report: building one is a scope
question.

- [ ] **Step 1: Write the failing test.** On that fixture, assert that the appended report's
  `line_indices` equals the derived grid's `rows`, and that its `ascii` is non-empty and equals
  `render_ascii` over those lines. Also assert that every band report has `line_indices == ()`.
- [ ] **Step 2.** Run it, and expect a FAIL: no field yet, and `ascii == ""` (F7).
- [ ] **Step 3.** Implement it.
- [ ] **Step 4.** Run the test plus `tests/etkl/test_adoption_ledger.py`,
  `tests/etkl/test_printed_total.py` and every test that greps `RegionReport(`. Expect a PASS.
- [ ] **Step 5.** Write the FALSIFICATION block: restore `ascii=""` and watch the test fail.
- [ ] **Step 6.** Commit.

---

### Task 2: `build_ledger` books every line at most once (I2, spec § 2.4 e)

**Files:**
- Modify: `src/iladub/etkl/adoption.py:43-120` (`build_ledger`, and its docstring's "TOUCHED"
  paragraph).
- Test: `tests/etkl/test_adoption_ledger.py`. Extend `_R` with `line_indices: tuple = ()` and add
  the test below.

**Interfaces:**
- Consumes: `RegionReport.line_indices` (Task 1).
- Signature unchanged: `build_ledger(lines, grid_rows, bands, reports) -> LineLedger`.
- Invariant (I2): region `i` **covers** a set of lines.
  - For `i < len(bands)`, it is the lines inside the band's bounds, as today (`_inside`).
  - For `i >= len(bands)`, it is `reports[i].line_indices`, with out-of-range indices dropped, as
    `admitted` already drops them.
- `touched` ranges over **every** report index whose cover meets `admitted`. Today it ranges over
  `range(len(bands))`, an asymmetry with `booked_bands` (M3); that is G3.
- Residue and both token terms keep their present form over the cover join. With no appended
  region the result is identical to today's for every input, which the existing tests pin.

- [ ] **Step 1: Write the failing test** (verbatim, a proposition until falsified):

```python
def test_an_appended_region_the_grid_rereads_is_touched_not_double_booked():
    """R301 I2 (spec § 2.4 e, G3). A fallback grid region appended after the bands, whose ink the
    guard has since escalated, is re-read by adoption's grid. The ledger must touch it through its
    OWN lines, never book its tokens beside the lines the grid admits."""
    lines = [_line(2, 0.0), _line(3, 10.0), _line(4, 20.0)]           # 9 tokens on the page
    bands = [_B(0.0, 1.5)]                                             # band 0 covers line 0 only
    reports = [_R("ignored"),                                          # booked nothing
               _R("escalated", tokens_escalated=7, line_indices=(1, 2))]   # appended, lines 1-2
    led = build_ledger(lines, (1, 2), bands, reports)
    assert led.touched == frozenset({1})
    assert led.residue == ()
    assert (led.asserted_tokens, led.escalated_tokens) == (7, 0)
    assert led.asserted_tokens + led.escalated_tokens <= sum(len(l.words) for l in lines)
```

- [ ] **Step 2.** Run it. Expect a FAIL on `touched == frozenset()`, with escalated tokens = 7
  (the G3 double count in miniature).
- [ ] **Step 3.** Implement it.
- [ ] **Step 4.** Run `tests/etkl/test_adoption_ledger.py` in full, then
  `PYTHONPATH=src .venv/bin/python scripts/ledger_contract_census.py`, the third caller (M3).
  Record its output. It must equal its output on `main`, which you record first.
- [ ] **Step 5.** Write the FALSIFICATION block: restore `range(len(bands))`, watch the new test
  fail and the old ones pass, then restore.
- [ ] **Step 6.** Commit.

---

### Task 3: `ruleguard` — select, extent, head, refusal (spec §§ 2.2, 2.3, § 8 S1–S2)

**Files:**
- Create: `src/iladub/etkl/ruleguard.py`, with a module docstring carrying the § 8 classification
  table (spec § 3), cited and not restated.
- Test: `tests/etkl/test_ruleguard.py`, synthetic graphs only.

**Interfaces (Produces):**
- `rule_separated_cells(g: Graph) -> frozenset[URIRef]`.
  - It runs the `sh:select` read from `tab:RuleSeparatedInkShape` in `vocab/shapes/tab-shapes.ttl`.
    The shapes graph is parsed once and cached, as `compile._TAB_SHAPES` is.
  - It replaces `$this` with `?this` and builds the prefix header from the shape's
    `sh:prefixes`/`sh:declare`. The idiom is `tests/etkl/test_vacuity_registry.py:305-317`; there is
    **no `src/` reader of `sh:select` today** (M1), so this is the first.
  - It returns the `?this` bindings.
- `owner_tables(g: Graph, cells) -> frozenset[URIRef]`. These are the subjects of
  `ruleink._CELL_PREDS` (`ruleink.py:18`) whose object is a returned cell.
- `withdrawal_extent(g: Graph, t: URIRef, others: Iterable[URIRef], residue: URIRef) -> Graph`.
  - Roots and closure are those of spec § 2.2, **as amended by § 8 S1**.
  - `others` are the other reports' `table_uri`s.
  - `residue` is `{doc}#p{page}-datagrid-residue`.
  - The function is pure: it does not mutate `g`.
- `chain_head(g: Graph, doc: URIRef, idx: int, t: URIRef) -> URIRef`.
  - It starts at `document._verdict_decision(g, doc, idx)` (`document.py:1113`). If that finds
    nothing, it starts at `URIRef(f"{t}-admission")` when that node is typed `dec:DecisionHolon`
    (M9).
  - It then walks with `document._effective_verdict` (`document.py:1128`), imported function-locally
    (U4).
  - If neither start exists it raises `RuntimeError`, with a message naming `t` and `idx` (spec
    § 2.3).
- `mint_refusal(g: Graph, doc: URIRef, idx: int, head: URIRef, rationale: str) -> URIRef`: exactly
  the S2 properties in Global Constraints. Option IRIs are `{refusal}-opt-admit` and
  `{refusal}-opt-refuse`, the slug form `BandRecorder` uses (`decisionlog.py:59`).
- `guard(graph, reports, asserted_total, escalated_total, doc, page_number) -> tuple[list, int, int]`.
  - It applies spec § 2.2's four steps per owner table: extent removal, `mint_refusal`, then
    `holon.escalate_region(g, URIRef(f"{doc}#region{i}"), doc, r.ascii, "RULE_SEPARATED_INK", anchor, 0.0, page_number)`
    (`holon.py:557`), then the report move.
  - The report move sets `verdict="escalated"`, `reason="RULE_SEPARATED_INK"`, `cells=0` and
    `table_uri=None`, and moves `tokens_asserted` into `tokens_escalated`. `line_indices`, `kind`,
    `anchor` and `ascii` stay.
  - It also moves the same count between the two totals. It mutates `graph` in place and returns
    the new reports and totals.
  - For an owner named by zero reports, or by several, it changes nothing.
  - The rationale names the rule (`tab:RuleSeparatedInkShape`) and every crossing cell's IRI,
    sorted.
  - Invariant: `sum(r.tokens_asserted) == asserted_total` and `sum(r.tokens_escalated) ==
    escalated_total` hold after the guard if they held before.

**Test fixture.** Reuse the one-cell page in `tests/test_rule_separated_ink.py:31-52` (`_page`),
importing it. Add what each test needs: a `dec:DecisionHolon` head with `rdfs:label "verdict"` at
`{DOC}#region0-d1`, with `dec:order 1` and `dec:regarding {DOC}#region0`; an owner `#t` reported at
index 0; and so on.

- [ ] **Step 1: Write the failing tests.** Each one is named for what it pins:
  1. `rule_separated_cells` returns `{#c}` on `_page(80, 90, rule_x=85)` and `∅` on
     `_page(80, 90, rule_x=200)`. This is the shape's own fixture pair; the select is the shape's.
  2. **S1:** with subjects `#t`, `#t-r0c0`, `#t-2-r0c0` (as `others=[#t-2]`) and
     `#p0-datagrid-residue` present, plus a blank-node bbox under `#t-r0c0`, the extent of `#t`
     holds `#t`, `#t-r0c0` and the bnode's triples, and **nothing** of `#t-2…` or the residue. A
     `#t-admission` typed `dec:DecisionHolon` is excluded.
  3. **S2:** after `mint_refusal`:
     - `_verdict_decision(g, DOC, 0)` still returns the original `-d1`;
     - the refusal's order is 2;
     - `effective-chain.rq`, with `?region` bound to `{DOC}#region0`, returns the refusal as its
       **last** row, with judgement `refusal` and chosen `refuse` (S3);
     - `compile._validate(g, legs=("dec",))` (`compile.py:934-935`) returns `conforms=True`.
  4. `chain_head` on an `{t}-admission` head with no `dec:order` gives the refusal `dec:order 0`
     (§ 8 interpretation), and `effective-chain.rq` returns it (branch B, M9).
  5. `chain_head` raises `RuntimeError` when neither a verdict nor an admission exists.
  6. `guard` on an owner named by two reports leaves the graph and reports byte-identical. Compare
     the canonical N-Triples set and the reports' tuple.
  7. `guard` on the happy path:
     - the cell is gone from the graph;
     - the report reads escalated with the moved tokens;
     - the totals moved by exactly `tokens_asserted`;
     - `{DOC}#region0` is escalated with reason `RULE_SEPARATED_INK` and confidence `0.0`.
- [ ] **Step 2.** Run them and expect a FAIL: the module does not exist.
- [ ] **Step 3.** Implement it.
- [ ] **Step 4.** Run `tests/etkl/test_ruleguard.py` and `tests/test_rule_separated_ink.py`, and
  expect a PASS. Then run
  `python -c "import iladub.etkl.ruleguard"` in a fresh process, which shows there is no import
  cycle (U4).
- [ ] **Step 5.** Write the FALSIFICATION block, one per pin:
  - drop S1's `others` exclusion and watch test 2 fail;
  - label the refusal `verdict` and watch test 3 fail;
  - remove the raise and watch test 5 fail.
- [ ] **Step 6.** Commit.

---

### Task 4: The pre-adoption guard (spec § 2.1 steps 3–4)

**Files:**
- Modify: `src/iladub/etkl/compile.py`. The insertion goes after the differencing block
  (`:1922-1927`) and before `if datagrid_adopt and escalated_total > 0:` (`:2000`).
- Modify: `tests/etkl/test_header_stack.py:214-241` (M7). It is **rewritten, not deleted**.

**Interfaces:**
- Consumes: `ruleguard.guard`, and `ruleink.carry_from_pdf` (already imported at `:2167`, and G4
  measured it idempotent).
- Order, verbatim from spec § 2.1: `carry_from_pdf(graph, str(doc), pdf_path)`, then
  `reports, asserted_total, escalated_total = guard(...)`.
- The existing `carry_from_pdf` at `:2167-2168` stays.
- Invariant I1, first half: the band graph holds no cell that the select returns once this step
  ends.

- [ ] **Step 1: Rewrite the M7 assertion** (verbatim; it replaces the `pytest.raises` block at
  `:234-240`, and the A/B below it is unchanged):

```python
    # R301 (spec 2026-10-08-r301-producer-guard-design.md): the PRODUCER now escalates the table the
    # membrane used to refuse. Same page, same rule at x=110; the shape is unchanged, the guard runs
    # its select first. Feeding the shape's own fixture to the producer is the spec § 5 pin.
    rep = compile_tables(pdf)
    assert any(r.verdict == "escalated" and r.reason == "RULE_SEPARATED_INK"
               for r in rep.regions), [(r.verdict, r.reason) for r in rep.regions]
    from iladub.etkl.ruleguard import rule_separated_cells
    assert rule_separated_cells(rep.graph) == frozenset()
    fix = compile_tables(pdf, validate_shapes=False)
```

- [ ] **Step 2.** Run it. Expect a FAIL with `MembraneRefusal`, which is the old behaviour.
- [ ] **Step 3.** Implement it.
- [ ] **Step 4.** Run:
  - `tests/etkl/test_header_stack.py`, `tests/etkl/test_ruleguard.py` and
    `tests/test_rule_separated_ink.py`. The last is O3: the bypass fixture is still refused by the
    membrane, because the guard is not on that path.
  - The full non-corpus suite, in chunks of about 8 files per process (memory kills are recorded).
  - Everything should be green.
- [ ] **Step 5.** Write the FALSIFICATION block:
  - delete the guard call, and Step 1's test raises `MembraneRefusal` again;
  - with the guard deleted, O3 still refuses, so the pin does not depend on the guard.
- [ ] **Step 6.** Commit.

---

### Task 5: The adoption guard and the reported outcome (spec § 2.1 step 5, § 2.5)

**Files:**
- Modify: `src/iladub/etkl/compile.py`:
  - `CompilationReport` (`:790-800`), for the new field;
  - the adoption branch (`:2000-2159`);
  - the return (`:2203`).
- Test: `tests/etkl/test_r301_adoption_outcome.py`, synthetic. Corpus pins go to
  `tests/test_r301_fed_h41.py` (Task 6).

**Interfaces:**
- Produces: `CompilationReport.adoption: str = "not_opened"`. It is the last field and defaulted,
  so the one positional `src` constructor (`:2203`) stands (M6). It takes exactly one of four
  values:
  - `"not_opened"`: `datagrid_adopt` is false, or `escalated_total == 0`, or **no grid was
    derived**. The plan reads a page with no grid as a gate that did not open: no ledger was built,
    so none compared anything. *Flagged interpretation, not ruled.*
  - `"ledger_refused"`: a ledger was built and `_led.escalated_tokens >= escalated_total`.
  - `"guard_refused"`: see the step-5 invariant below.
  - `"adopted"`.
- Step-5 invariant (spec § 2.1): after the `_emitted` loop (`:2079-2087`), and **before** `graph`,
  `reports`, `asserted_total` or `escalated_total` is reassigned, the branch runs `carry_from_pdf`
  on the **new** graph and then `rule_separated_cells`. If that is non-empty:
  - the old graph, reports and totals stand untouched;
  - `adoption = "guard_refused"`.
- **MEASURE the seam:** today `graph = Graph()` at `:2075` *is* the install. Graph, totals and
  reports are rebound in sequence through `:2159`. The new graph must be built under a local name
  and installed only after the select is empty. Name every rebinding you move.
- I1, second half: the graph that reaches validation never holds a select-returned cell.

- [ ] **Step 1: Write the failing tests.**
  - On a plain page with no grid, `adoption == "not_opened"`.
  - On the existing synthetic adopting fixture (memory: R173 5a, "synthetic adopting fixture",
    PR #163; find it with `grep -rn "datagrid_adopt=True" tests/`),
    `compile_tables(..., datagrid_adopt=True).adoption == "adopted"`, and its regions and score are
    unchanged from `main`.
  - Monkeypatch `ruleguard.rule_separated_cells` to return a non-empty set **only on the second
    call**. Then `adoption == "guard_refused"`, and `regions`/`score` equal the
    `datagrid_adopt=False` compile of the same fixture.
  - **MEASURE first** that the monkeypatch reaches the call site: the import is function-local, so
    patch the module attribute.
- [ ] **Step 2.** Run them. Expect a FAIL: there is no attribute yet.
- [ ] **Step 3.** Implement it.
- [ ] **Step 4.** Run the new file and every test that passes `datagrid_adopt=True` (grep for
  them). Expect a PASS.
- [ ] **Step 5.** Write the FALSIFICATION block: delete the step-5 select, and the `guard_refused`
  test fails.
- [ ] **Step 6.** Commit.

---

### Task 6: The driver states the observed cause; the fed-h41 oracles (spec § 2.5, O1, O2, O6)

**Files:**
- Modify: `src/iladub/etkl/document.py:1786-1821`.
- Test: `tests/test_r301_fed_h41.py`. It carries `pytestmark = pytest.mark.corpus` and `skipif`
  when `held-out/fed-h41-2025-01-02.pdf` is absent (M8). It uses **one** module-scoped compile of
  about 215 s (G1's run time).

**Interfaces:**
- `grid_idx = len(band_lists[p])`. `band_lists[p] = page_bands(pdf_path, p)` is already in hand
  (`document.py:1492`, `:1509-1510`; M5). It replaces `len(pages[p].regions)`, which counts
  appended regions (F3).
- When `rep_a.adoption != "adopted"`, the note is
  `f"page {p}: adoption refused — {cause}"`, with one fixed `cause` string per outcome. The guard
  outcome's string contains `"rule-separated ink"`. The `continue` follows.
- The existing `grid_uri is None` and "superseded no escalated band" branches stay for the
  `"adopted"` outcome (Review Focus 4).

- [ ] **Step 1: Write the failing corpus tests.** All figures are from spec § 5 and handoff G1.
  - **O1:**
    - `compile_document(PDF, validate_shapes=True)` completes;
    - p5 is 187/64 and p7 is 0/137, and the document is 2739/663;
    - `sorted(rep.adopted) == [2, 3, 5, 8, 10]`;
    - for every page except 5 and 7, the region tuples equal Task 0's JSON.
  - **O2 (as amended by § 8 S3):**
    - `rule_separated_cells(rep.graph) == frozenset()`;
    - for every region IRI `R` that some `dec:DecisionHolon` labelled `refusal` regards, there is
      exactly one such decision;
    - `effective-chain.rq` bound to `R` returns it as its last row, with chosen `refuse`.
    - **Record the set of `R`.** PROPOSED: it is `p5#region3`, `p5/adopt#region3` and p7's
      fallback region index. Measure it; do not assert it before the run.
  - **O6:** some `rep.notes` line starts with `"page 7: adoption refused"` and contains
    `"rule-separated ink"`, and **no** note says `"no data grid region"` for page 7.
- [ ] **Step 2.** Run with `-m corpus`. Expect a FAIL. Tasks 1–5 already pass O1 and O2; record
  whether they do. O6 fails until this task.
- [ ] **Step 3.** Implement the driver change.
- [ ] **Step 4.** Run `-m corpus tests/test_r301_fed_h41.py` and expect a PASS. Also run the
  existing driver tests that read `notes` (grep for `adoption refused`).
- [ ] **Step 5.** Write the FALSIFICATION block, using spec § 5's list:
  - with the pre-adoption guard deleted, O1 p5 reverts to 213/38 and O2 fails;
  - with the refusal mint deleted, O2's chain check fails;
  - with `grid_idx` reverted, O6's note goes back to the false cause.
  - Each is one process, run serially.
- [ ] **Step 6.** Commit.

---

### Task 7: O4 and O5 across the corpus (run and record; no source change)

**Files:**
- Create: `docs/superpowers/2026-10-08-r301-o4-o5-record.md`, an Evidence record. It is written
  once and its `Doc impact: none`.

- [ ] **Step 1: O4.** Snapshot all 11 documents into `after/`, one process each and serially (Task
  0's `--pdf`). Then run
  `PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py before after`.
  - Expected: only fed-h41 moves.
  - **Any other document moving refutes spec § 6.** Stop and report it; do not adjust anything.
- [ ] **Step 2: O5.** For every page that the snapshots record as adopted, assert
  `ledger.asserted + ledger.escalated <=` the page's token count, with p7's `/adopt` re-compile
  included. Record the per-page figures.
- [ ] **Step 3.** Strike `~~R301~~` in `docs/superpowers/residues.md`, and record the closure
  evidence in place in `residues-open.md`/`residues-closed.md`. The closure condition is spec § 7:
  O1–O3 and O5 hold, and O4 has been run and recorded.
- [ ] **Step 4.** Commit and open the PR. CI's `test` job does not run `-m corpus`, so the PR body
  carries the Task 6 and Task 7 local run outputs (memory: CI skips the corpus).

---

## Self-review (run against the spec, 2026-10-08)

- **Coverage.** Each spec item maps to a task:
  - § 2.1 steps 3–4 → T4; step 5 → T5;
  - § 2.2 and § 8 S1 → T3;
  - § 2.3 and § 8 S2 → T3;
  - § 2.4 d → T1, and e → T2;
  - § 2.5 → T5 and T6;
  - O1, O2 and O6 → T6; O3 → T4; O4 and O5 → T7;
  - § 7's close condition → T7.
- **Interpretations flagged, not ruled.** There are two: `dec:order 0` for an admission head
  (§ 8's own flag), and no grid derived ⇒ `"not_opened"` (T5).
- **Spec "NOT done" reconciliation (rule 5).** No task adopts grid by grid, edits
  `_band_subgraph`, cleans empty `RuleSpan`s, touches R300's two dangling tables, or adds
  vocabulary. Review Focus 4 is the § 7 edge, and it is handled by a note, not by adoption.
