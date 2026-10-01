# R261 totals family — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:etkl:03 — cbh's one live escalation is the totals family ([[R261]]).

**Goal:** a lone number printed beneath a table binds as a `tab:PrintedTotal` when a NEURAL worker
answers *yes* **and** exact `Decimal` arithmetic holds. Then cbh p0's four port totals and their
grand total `1,951,264` are carried, and cbh is adjudicated.

**Architecture:** a binding step at the top of each band iteration in `compile_tables`, before
`classify`. Arithmetic runs first, the worker is asked only on a match, and a bound line is carved
out of the band. The membrane gets one new closed shape. No published term changes meaning.

**Tech Stack:** Python 3, rdflib, pySHACL, BAML 0.222.0 (Haiku 4.5 via the `Claude` client), pytest.

**Spec:** `docs/superpowers/specs/2026-10-01-r261-totals-family-design.md` (approved 2026-10-01,
PR #288). Cite it by §; do not re-derive it (CLAUDE.md § Plan authoring, rule 6). Its rulings
R-a…R-d (§ 0) are not re-opened.

**Doc impact: none** (this plan; the spec declares the increment).

**This plan is a contract, not code** (CLAUDE.md § Plan authoring, rules 1–7). It gives signatures,
invariants, the seams to measure, and the falsifying oracles. **No function body appears here.**
Every task report carries a `## FALSIFICATION` block. **A report without one fails review.**

**Measurements cited below** were taken at `ed4fe61` on 2026-10-01 by read-only measurement agents
(grep/sed/Read, plus one `python3 -c` run for § M6). They were **read, not run**, except where
marked. The implementer re-measures any `file:line` before writing against it. Line numbers drift.

---

## Measured seams (the facts this plan builds on)

- **M1 — loop anchors.** `compile.py`:
  - `def compile_tables` is at :990, `bands = page_bands(...)` at :1025, and `donor_ev =
    donor_evidence(bands, …)` at :1034. `donor_ev` is built from the **uncarved** bands, before the
    loop.
  - `for idx, band in enumerate(bands):` is at :1047. It is followed by
    `band_marks.append((asserted_total, escalated_total))` at :1048, `brec = recorder.band(idx)` at
    :1049, `render_ascii(band)` at :1050, the multi-table gate at :1051–1080, `classify(band)` at
    :1081, and `brec.record("kind", …)` at :1083.
- **M2 — `reports[-1]` is band `idx − 1`.**
  - There are three `continue`s (:1080, :1114, :1339), and each appends a report first (:1078,
    :1112, :1336).
  - There is no `break` or `return` in the loop body, and every other leaf appends exactly one
    report (comment at :1043–1044).
  - `RegionReport` is at :750, with `verdict: str` at :758 (`asserted|escalated|ignored|superseded`)
    and `table_uri` at :766 (None = nothing asserted).
  - **Caveat:** at :1146 and :1359 a record report can be `asserted` with `cells == 0` and a
    `table_uri` set.
- **M3 — URIs come from `idx`**, never from band identity:
  - `#region{idx}`, the `#…table` family, and `#ignored{idx}` (`holon.py:631`).
  - The decision prefix `f"{doc}#region{idx}"` (`decisionlog.py:103`).
  - `Band` is `@dataclass(frozen=True)` (`bands.py:16`), and nothing compares bands by identity.
  - **But `bands[idx]` is read directly** by:
    - `donated_region` (`donation.py:164`)
    - `offer_single_line`'s guard (`donation.py:271`)
    - `span_region` (:378) and `span_offer` (:452)
  - `document.py:1456` re-derives its own `band_lists` through `page_bands`, and those lists feed
    `_confirm_section_total` (:1650).
- **M4 — `Band`/`Line`/`Word`.**
  - `Band.lines: tuple[Line, …]`, along with `top`, `bottom`, `rules`, `hrules`, `column_xs`,
    `captions`, `unit_markers`, `unshown`, `frame` and `title_captions`.
  - `Line(words, top, bottom)` (`geometry.py:35`) and `Word(text, x0, x1, top, bottom, page)` (:25).
  - The existing subset pattern is `dataclasses.replace(sub, lines=…, top=…)` (`compile.py:149`).
    `segment._band_from_lines` drops the extra fields and fails on empty input, so **do not use
    it**.
  - An empty `lines` is tolerated: `classify` (`regions.py:105`) and `render_ascii`
    (`roundtrip.py:141`) both handle it.
- **M5 — `_book_recovered_ink(band, booked, recovered_extents) -> (asserted, escalated)`**
  (`compile.py:361`). It is extent-exact with no tolerance. Callers: :419, :1176, :1241, :1401,
  :1456.
- **M6 — the numeric parse.** `rows._numeric_token_sum(text)` (`rows.py:62`) is built on
  `headers.is_numeric(s)` (`headers.py:36`). Run with `python3 -c`, it gives:

  | input | result |
  |---|---|
  | `1,951,264` | 1951264 |
  | `21` | 21 |
  | `1.5%` | 1.5 (the `%` is dropped) |
  | `1e3` | 1E+3 |
  | `(12)`, `-`, `–`, `2..6` | not numeric |

  **The census script parsed differently** (`scripts/r261_total_question_probe.py:71`, `as_decimal`:
  `(12)` → −12, `$` stripped, and every word of the next band tried, not lone lines). Task 0
  measures whether that difference changes the corpus match set.
- **M7 — `offer_single_line`** (`donation.py:249`) is called only at `compile.py:1095`. That call
  comes after `classify` and is gated on `NON_TABLE and len(band.lines) == 1 and donor_ev is not
  None` (:1089).
- **M8 — no in-memory grid survives a band.** Column cells are read back from `graph`, as the probe
  does: `tab:hasCell` → `tab:atColumn` + `tab:cellText` (`r261_total_question_probe.py:87–108`).
- **M9 — the worker template** is `src/iladub/etkl/headerlines.py`:
  - `HeaderLinesReading` :41, the Protocol :49, `FakeHeaderLinesReader` :54, and
    `baml_header_lines_available()` :63 (`BAML_LIVE=="1"` and `baml_client` importable).
  - The module-global cache is at :72, and the BAML reader at :75.
  - `READINGS_DIR` :120, `question_key` :123 (text facts only, **never the PNG**), and
    `RecordedHeaderLinesReader` :128. The recorded reader replays, writes only under
    `ILADUB_RECORD_READINGS=="1"`, and never raises on a miss.
  - `default_reader()` :157 is late-bound from compile (`compile.py:448`) so that tests can patch
    it.
  - Test isolation is the autouse fixture in `tests/etkl/test_header_lines.py:32–57`.
  - `baml_client/` is gitignored and generated by `baml-cli generate --from baml_src`
    (`ci.yml:23`).
  - **No existing worker returns a closed enum.**
- **M10 — vocabulary and shapes.**
  - `tab:EntryCellShape` (`tab-shapes.ttl:79–84`) requires `tab:atColumn` and `tab:atRow`, exactly
    1 each. `tab:AggregationCellShape` (:241) requires `aggregationFunction`, `aggregates` and
    `overAxis`. **⇒ `tab:PrintedTotal` cannot subclass `AggregationCell`** (spec § 4's seam,
    settled here): it is `⊑ tab:Cell` (`tab.ttl:35`, itself `⊑ tab:PageLocated`).
  - Under `tab:Cell`, only `tab:WrappedCellShape` (`tab-physical-shapes.ttl:43`) binds. It sets
    `hasBBox` maxCount 1 and requires a non-empty `cellText` when a bbox is present.
  - `tab:aggregates` (`tab.ttl:156`) has no domain or range, **on purpose**.
  - The membrane (`membrane.py:45`) uses `inference="none"` over a subclass closure (:448, :125).
    It is skipped on tableless pages (`compile.py:1885–1889`).
- **M11 — the decision link.**
  - `dec:produced` (`dec.ttl:84`, ⊑ `prov:generated`) is constrained by **no** membrane shape. The
    only constraint is in `iladub-hga-shapes.ttl:36`, which the compile membrane does not load.
  - The tab precedent for "product of a decision" is `tab:BoxheadAbsenceDecidedShape`
    (`tab-shapes.ttl:502–519`). It is a SPARQL check on `rdfs:label` of the judgement and of the
    chosen option.
  - `BandRecorder.record(judgement, options, chosen, rationale, rejected=None, evidence=None) ->
    URIRef` (`decisionlog.py:39`) raises if there are fewer than 2 options or if the choice is not
    among them.
- **M12 — pins a new term can trip.**
  - `tests/etkl/test_vacuity_registry.py:343/355`: idle shapes must be registered, and a registered
    shape that goes live fails.
  - `tests/test_artifact_terms.py:111` and `tests/test_artifact_declarations.py:245` both pin the
    tracked `.ttl` count at `== 168`.
  - `tests/etkl/test_domain_range_agreement.py`.
  - `tiling.py:35,56` are the gate shape lists. `PrintedTotalShape` is **not** added to them,
    because it is not a grid shape.

## Decisions this plan takes where the spec is silent (each one is reversible; review them)

- **D1** `tab:PrintedTotal ⊑ tab:Cell` (M10).
- **D2** The decision link is **`?d dec:produced $this`** (M11). It is the standard PROV product
  link, so no new property is needed. The shape mirrors `BoxheadAbsenceDecidedShape`:
  - the judgement label is `printed_total`;
  - the chosen option label is `total`.
- **D3 Exactly one matching column, or no bind.** Spec § 2.2 says *"every column"*. Two columns
  with equal sums would make `tab:aggregates` assert a sum for a column it may not total, so the
  case is refused. Task 0 counts how often it occurs.
- **D4 Table level first.** A candidate is tried at the total-of-totals level only when no column
  matches. That gives one worker question per candidate.
- **D5 Binding site:** after `brec = recorder.band(idx)` (:1049) and before `render_ascii` (:1050).
  `band_marks` (:1048) has already recorded the pre-band totals, so booking the carved word inside
  this iteration attributes it to band `idx`.
- **D6 An emptied band still appends exactly one `RegionReport`** (M2's invariant). It carries:
  - `verdict "asserted"`
  - `table_uri None`
  - `cells 0`
  - the carved word in `tokens_asserted`

  No band node goes into the graph (spec § 2.4). Task 4 measures `document.py:1611`, which reads
  `verdict == "asserted"` **without** checking `table_uri`, before relying on this.
- **D7 The crop has no line-count constant.** Table level crops the **whole** previous band through
  the candidate line. Total-of-totals crops the union of the operand totals' lines and the candidate
  line. P1 was measured on the probe's 8-line tail crop, so Task 1 re-runs P1 on this crop.
- **D8 The carve replaces `bands[idx]`** in the loop's list as well as the local `band` (M3).

## Global Constraints

- **CLAUDE.md § 8 gate.** No tuned constant and no tolerance. The classification is spec § 7,
  verbatim. Every new function's docstring states its class and, for PROCEDURAL, why it is
  irreducible.
- **The arithmetic check is the sole enforcement** of the sum property. It is a PROCEDURAL producer
  guard (spec § 4; CLAUDE.md § Producer-side guards, R89), and the code says so where it is
  checked.
- **One parser:** `headers.is_numeric` + `rows._numeric_token_sum` (M6). Never a second one.
- **The worker output is a closed enum `yes | no | cannot_tell` with no note field** (spec § 3.2).
- Rationales come from arithmetic facts, never model text (spec § 2.4).
- **The corpus is gitignored.** CI skips `-m corpus`, so **green CI is not evidence** for Tasks 0,
  1, 6 or 7.
- **Local runs:**
  - one test file per process, launched from a `.sh` under `bash` (zsh leaves the args unsplit,
    which gives a phantom green);
  - full-corpus compiles run serially, never two at once;
  - the suite runs in ~8-file chunks;
  - macOS has no `timeout`.
- **`git add` before running any gate.** Gates read tracked files.
- **The ink score is never an oracle.** Record it before and after as a fact (spec § 5.5).
- Evidence files under `docs/superpowers/**` are append-only after loop close.

## Review Focus

1. **Two columns with equal sums** matching one candidate: no bind (D3). Owned by Task 3.
2. **A lone number after a table that asserted 0 cells** (M2 caveat): no columns means no match.
   Owned by Task 3.
3. **A lone number directly after a bound total**: its `reports[-1]` has `table_uri None` (D6), so
   there is no table level. It may bind at total-of-totals level only over ≥ 2 bound totals. Owned
   by Task 4.
4. **A percentage column** (`100%` printed beneath a column of percentages): M6 drops the `%`, so it
   can bind. That is correct only if the worker says yes. The test pins that the conjunction, not
   the parse, decides. Owned by Task 4.
5. **A band whose single line binds and that `offer_single_line` would also have taken**: binding
   wins and no donation is attempted (D5 precedes :1095). Owned by Task 4.

## File structure

| file | responsibility |
|---|---|
| `baml_src/printed_total.baml` (new) | Two functions over one closed enum (spec § 3.2) |
| `src/iladub/etkl/printedtotal.py` (new) | Reading, reader protocol, fake, cache, BAML + recorded readers, `default_reader`, crop |
| `src/iladub/etkl/totals.py` (new) | PROCEDURAL: candidates, column operands, the two matches |
| `src/iladub/etkl/compile.py` (modify) | One binding call at D5; the carve; the emptied-band report |
| `src/iladub/etkl/holon.py` (modify) | `emit_printed_total` beside `emit_ignored_band` (:607) |
| `vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl` (modify) | Spec § 4 terms + `tab:PrintedTotalShape` |
| `readings/printed_total/*.json` (new, recorded) | Replayed worker answers |
| `scripts/r261_total_question_probe.py` (modify) | P3 + P1 on the D7 crop |
| `tests/etkl/test_printed_total.py` (new) | Worker, operands, conjunction, carve |
| `tests/test_tab.py` + `tests/tab-printed-total-*.ttl` (new fixtures) | Shape positive and negatives |
| `docs/superpowers/<date Task 0 runs>-r261-totals-family-evidence.md` (new) | Baseline, P3, sweep, cells dump, adjudication evidence |

---

### Task 0: Baseline and census, before any `src/` change

**Files:** create the evidence file (§ 1).

- [ ] **Step 1:** Compile all 7 corpus documents serially and record, for each:
  - the canonical graph hash (`to_canonical_graph`, then sha256 over the sorted N-Triples);
  - the triple count;
  - the score.

  These are the "before" of Task 6's C2.
- [ ] **Step 2: the census under the production rule.** Restate the census (Addendum 1: 24 pairs,
  5 matches, 4 true + 1 false) using **M6's parser** and **lone-line candidates only** (spec
  § 2.1). Over every asserted table followed by a band with lone numeric lines, record:
  - each candidate;
  - its matching columns;
  - how many columns match (D3);
  - whether who-wfa p0 `21` is a lone-line candidate.

  **If who-wfa's `21` is not a lone-line candidate**, the corpus never exercises the "worker says
  no" arm. Say so: that arm is then pinned only synthetically (Task 4).

  **Any divergence from the census's 5 is a finding**, recorded before Task 3. It may come from the
  parser difference (M6) or from the lone-line restriction.
- [ ] **Step 3:** Commit the evidence file.

### Task 1: P3 — the total-of-totals wording (a proposition; it may fail) — spec § 5.1

**Files:** `scripts/r261_total_question_probe.py`, evidence § 2.

- [ ] **Step 1:** Extend the probe:
  - add the **D7 crops**;
  - add the closed output, with **no `note`** in the JSON contract;
  - add a second wording for total-of-totals. Draft, a proposition and not fixed:

    > *The image shows part of a page on which several tables each have a total printed beneath
    > them. The number {value} is also printed. READ IT AS A PERSON READS THE PAGE. Is {value} the
    > total of those tables' totals — a grand total? Answer exactly one of: yes / no / cannot_tell.*

  The worker is **not** given the operands' values. It answers the role question, and arithmetic
  answers the sum.
- [ ] **Step 2: P3.** Run on `1,951,264` with the D7 total-of-totals crop. Use 3 repeats, Haiku 4.5,
  and `env -u BAML_LIVE`.
  - **Null control:** each of the four port totals, asked the same grand-total question. Expect
    *no*.
  - **Decision rule, fixed before the run:** the grand total binds in this loop only if
    `1,951,264` gets *yes* ×3 **and** no null gets *yes*.
  - **Otherwise:** record the result, do **not** reword (spec § 5.1), and drop the total-of-totals
    level from Tasks 3–4. cbh is then not accepted by this loop (Task 7 records why).
- [ ] **Step 3: P1 on the D7 table-level crop.** Ask about the same 5 matches and 7 nulls, ×3.
  - **It holds** if all 4 port totals get *yes* ×3, `21` gets *no*, and no null gets *yes*.
  - **If it does not hold**, stop and report to the maintainer. Do not quietly restore the 8-line
    crop: that is a constant chosen because it passed.
- [ ] **Step 4:** Commit the probe and evidence § 2.

### Task 2: Vocabulary and membrane — spec § 4

**Files:** `vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl`, `tests/test_tab.py`, new
`tests/tab-printed-total-*.ttl`.

**Produces:** `tab:PrintedTotal ⊑ tab:Cell` (D1); `tab:totalOf` (domain `tab:PrintedTotal`, range
`tab:Table`); `tab:PrintedTotalShape`; `tab:aggregates`' comment amended to name its third usage
(subject a PrintedTotal, objects column cells or PrintedTotals). **Domain and range stay
undeclared** (M10).

**`tab:PrintedTotalShape` constraints:**

| path | constraint |
|---|---|
| `tab:cellText` | exactly 1 |
| `tab:aggregates` | `minCount 2` |
| `tab:totalOf` | `maxCount 1` |
| `tab:hasBBox` | exactly 1, class `tab:BBox` |
| `tab:onPage` | exactly 1, `xsd:integer` |

Plus one SPARQL constraint (D2): some `?d` with `dec:produced $this`, typed `dec:DecisionHolon`,
labelled `printed_total`, whose `dec:chosen` is labelled `total`.

- [ ] **Step 1: tests first.** Write:
  - one conforming fixture;
  - **one negative fixture per constraint**, each asserting `not conforms` **and** the shape's name
    in the report, as in `test_orphan_entry_fails` (`tests/test_tab.py:102`);
  - a negative where the decision chose `not_total`;
  - a negative where the producing decision's judgement is not `printed_total`.
- [ ] **Step 2:** Run them and see them fail (no terms yet). Then add the terms and shape, and see
  them pass.
- [ ] **Step 3: MEASURE the pins (M12) before touching them.**
  - Run `test_artifact_terms.py` and `test_artifact_declarations.py`. If the `.ttl` count moves,
    re-pin with the **measured** count and say why in the commit.
  - Run `test_domain_range_agreement.py`.
  - Run `test_vacuity_registry.py`. `PrintedTotalShape` goes live only on cbh, under `-m corpus`.
    Measure how the registry treats a shape that is idle in CI and live on the corpus, and follow
    its existing convention.
- [ ] **Step 4: FALSIFICATION.** Delete each constraint in turn and show its negative test turn
  green-wrongly (it now conforms). Restore each. Then commit.

### Task 3: Operands and candidates — `totals.py` (PROCEDURAL)

**Interfaces (produces):**
- `candidate_lines(band) -> list[tuple[int, Line, Decimal]]`
  - Returns the lines of exactly one word with `is_numeric(word.text)`, valued by
    `_numeric_token_sum`.
  - The int is the line's index in the band.
- `column_operands(graph, table_uri) -> dict[URIRef, tuple[Decimal, list[URIRef]]]`
  - Maps each column to (exact sum, entry-cell URIs). Only cells whose `cellText` `is_numeric`
    count.
- `match_table(value, operands) -> tuple[URIRef, list[URIRef]] | None`
  - Returns the column and its cells only when **exactly one** column's sum equals `value` (D3) and
    that column has ≥ 2 members.
- `match_totals(value, bound: list[tuple[URIRef, Decimal]]) -> list[URIRef] | None`
  - Compares the **whole** set's sum, never a subset (spec § 2.2), and needs ≥ 2 members.

- [ ] **Step 1: tests first.** Write unit tests over a hand-built graph:
  - a single matching column;
  - two equal-sum columns → None;
  - a 0-cell table → None;
  - a non-numeric cell skipped;
  - `match_totals` with 1 bound total → None;
  - a subset sum that equals the value while the whole set does not → None.

  Run them, see them fail, implement, see them pass.
- [ ] **Step 2: corpus oracle (`-m corpus`, local).** `candidate_lines` + `column_operands` +
  `match_table` over the corpus must reproduce **Task 0 Step 2's** match set exactly. This is an
  independent oracle, because the census computed its matches from a separate script.
- [ ] **Step 3: FALSIFICATION.** Do each of the following, show the test that turns red, then
  restore:
  - replace "exactly one column" with "any column";
  - make `match_totals` search subsets;
  - drop the ≥ 2 guard.

  Then commit.

### Task 4: The worker and the binding — spec §§ 2, 3.2

**Files:** `baml_src/printed_total.baml`, `printedtotal.py`, `holon.py`, `compile.py`,
`tests/etkl/test_printed_total.py`.

**Interfaces:**
- `PrintedTotalReading(answer: Literal["yes","no","cannot_tell"])`: frozen, with **no other field**.
- A reader protocol with `ask(crop_png: bytes, level: str, value: str, listing: str) ->
  PrintedTotalReading | None`, where `level` is `"table" | "totals"`.
- A fake, a module-global cache, a BAML reader, `RecordedPrintedTotalReader` and `default_reader()`,
  all copying M9's semantics exactly.
- `question_key(level, value, listing)`: hashes text facts only, **never the PNG**.
- The readings live at `readings/printed_total/{key}.json`.
- `emit_printed_total(g, doc_uri, idx, line_no, word, page, value_text, operands, table_uri | None,
  decision) -> URIRef`. It writes everything `PrintedTotalShape` requires, plus `decision
  dec:produced total`.
  - The URI is derived from `idx` and the line's index **in the uncarved band**.
  - **MEASURE** how `#region{idx}` is scoped per page (M3) before choosing the URI string, so that
    no two pages collide.

**The binding (D5).** It runs on every candidate of `band`:
- **Arithmetic first.** Use `match_table` against `reports[-1]` when that report is `asserted` with
  a `table_uri`. Otherwise use `match_totals` over this page's bound totals (D4).
- **Then the worker**, and only on a match.
- **Bind iff the answer is `yes`.** On a bind:
  - `brec.record("printed_total", ["total", "not_total"], "total", rationale)`. The rationale comes
    from the level, the column or operand count, and the member count.
  - emit the total;
  - carve the line;
  - book its word through `_book_recovered_ink` with the word's own extent;
  - replace `band` **and `bands[idx]`** (D8).

  When the worker answers anything else, record the decision as `not_total` and leave the band
  untouched.
- **After binding,** an empty band appends one report (D6) and `continue`s. A non-empty band flows
  into the existing loop unchanged from :1050.

**MEASURE first** (write the result in the task report):
- **(a)** `document.py:1611`'s use of an `asserted` report with `table_uri None`;
- **(b)** whether `_band_subgraph`'s log boundary (box-split plan 3d.2) handles a `dec:produced`
  edge into a tab node;
- **(c)** that the emptied band's tokens reach the score exactly once. Count every word of the
  uncarved band in exactly one bucket.

- [ ] **Step 1: tests first.** The synthetic PDF fixture (spec § 5.2) is a table, a lone total
  line, a second table with its total, a total-of-totals line, and a prose remainder. Use the fake
  reader through `monkeypatch.setattr(printedtotal, "default_reader", …)`, with M9's isolation
  fixture copied. Assert the spec § 5.2 table, row by row:
  - yes + holds → bound;
  - yes + fails → not bound;
  - no + holds → not bound;
  - cannot_tell + holds → not bound.

  Also assert:
  - total-of-totals binds only over bound totals;
  - the remainder is classified alone;
  - an empty remainder emits no band node **and** still appends one report;
  - the graph conforms to `PrintedTotalShape`;
  - every uncarved word is booked exactly once.

  Add Review Focus items 3–5 as tests in this task.
- [ ] **Step 2:** Run, fail, implement, pass. Then run `baml-cli generate --from baml_src`.
- [ ] **Step 3: FALSIFICATION.** Do each of the following, show the red, then restore:
  - delete the worker check (arithmetic binds alone);
  - delete the arithmetic check (the worker binds alone);
  - skip the `bands[idx]` replacement;
  - skip the emptied-band report.

  Then commit.

### Task 5: Record the readings

- [ ] Run cbh and who-wfa with `BAML_LIVE=1 ILADUB_RECORD_READINGS=1` (key via the zshrc prefix,
  serially), and commit `readings/printed_total/*.json`.
- [ ] Re-run with both env vars unset and confirm the replay gives the identical graph hash.
- [ ] **Every recorded answer must equal Task 1's majority answer** for the same question.
  Otherwise it is a finding.

### Task 6: Corpus sweep — spec § 5.3

- [ ] **C2.** Recompile all 7 serially and compare with Task 0 Step 1. **Only cbh may move.** Any
  other hash difference is a finding to diagnose before the PR, not a number to re-pin.
- [ ] **Disjointness control.** No word is both a `tab:SectionTotal` row cell and a
  `PrintedTotal` (M3: `_confirm_section_total` sees the uncarved bands).
- [ ] **Pins that move (spec § 5.4):** re-read
  `test_corpus_cbh_furnishes_exactly_one_request_for_its_one_live_escalation_the_residue`
  (`tests/etkl/test_escalation_furnish.py:274`). Its live count goes 1 → 0. Re-pin it with the
  residue **re-read** and stated.
- [ ] **Dump cbh's cells before accepting** (2026-09-28 rule): every table, every `PrintedTotal`
  with its operands, and where the Note landed. Then record the score before and after.

### Task 7: Adjudication and register — spec §§ 5.5, 6

- [ ] **`tests/corpus-manifest.ttl`** (cbh at :78–92): append a **new** `cor:adjudication`. Do not
  edit the 2026-08-20 hold. Switch `cor:expectedVerdict` to `cor:CompilesAbove` and set a
  `cor:scoreFloor` with R194's reasoning (see the graincorp-capacity note at :76). The rationale
  **repeats spec § 0's concern**: ≈ 85 of the gained tokens are the Note **ignored, not read**.
  - **If Task 1 dropped the grand total,** do none of this. Write a hold note instead.
- [ ] **`tests/arc-manifest.ttl`:** set `prog:criterion:etkl:03` `prog:met true` only if the
  adjudication holds.
- [ ] **Register:**
  - close R261 with ✎ R-a;
  - add ✎ to R47 for the ruling;
  - re-read R77 and close or amend it **as measured**;
  - raise a new row: cbh's Note is uncarried table context (principle 5), with a raise-time tally
    counted from the index.

  Run `test_doc_governance.py` and `test_source_citations.py`, then commit.

### Task 8: Finish

- [ ] Run the full suite in chunks and the corpus files locally and serially. Post the local corpus
  results as a PR comment, since CI cannot see them.
- [ ] Update the memory pointer. Write the handoff with part 5 first, typed asserted or proposed.
- [ ] `superpowers:finishing-a-development-branch`. A PR is required, with `test` green.
