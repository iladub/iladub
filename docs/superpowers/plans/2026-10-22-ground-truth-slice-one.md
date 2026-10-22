# Ground truth, slice one: implementation plan (2026-10-22)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance. It proposes `prog:criterion:tab:13` (spec § 9.2 item 6).

**Doc impact: increment.** The same as the spec's: a `truth` block in one baseline file, a floor test,
and one arc criterion. No released meaning changes.

**Goal:** Score the carried cells of Fed H.4.1 2025-01-02 table 1 against the publisher's HTML, and
make that score a committed number that CI gates.

**Architecture:** A stdlib extractor turns the pinned HTML table into a committed truth CSV. A pure
scorer in `src/iladub/truth.py` compares `table_records()` output with that CSV. `snapshot()` writes a
`truth` block for any document that has a `tests/ground-truth/<stem>/` directory, so the R305 gate
covers the score. A CI test checks the committed block against a hand-ratcheted floor.

**Tech Stack:** Python stdlib (`html.parser`, `csv`, `hashlib`, `unicodedata`), rdflib, pytest.

**Spec:** `docs/superpowers/specs/2026-10-22-ground-truth-slice-one-design.md`, §§ 1-8 as amended by
§ 9 and § 10. **Where § 9 or § 10 supersedes an earlier section, the later one wins.** The plan cites
the spec and does not restate its rules. Read § 3.2, § 9.2 and § 10 before any task.

## Global Constraints

- CLAUDE.md § 8 gate: every decision here is PROCEDURAL (spec § 4). No geometry, no x0, no
  `text-indent`, no tolerance, and no tuned constant. Each new module's docstring states why it is
  irreducible, in the form of `scripts/corpus_verdict_snapshot.py:34-38`.
- Normalisation is exactly spec § 3.2's three rules. It has no fourth rule.
- The extractor uses stdlib `html.parser` only. `beautifulsoup4` is not in CI's extras (spec § 10.4).
- Pin: SHA-256 of the 2nd `<table` … its `</table>`, inclusive, which must equal
  `964e62c8ed5f3742b24df41f846950b3bcde45e97bbff92664cb84cda89a00fa` (78,874 bytes) (spec § 10.1).
- The CSV's `col_path` joins header texts with ` › `. The scorer compares parts joined with ASCII
  `" > "`. The extractor refuses a header text that contains ` › ` (spec § 10.3).
- Candidate records are selected by concept `region` page prefix (`p<page>` then `-` or `#`), never by
  `row_id` (spec § 10.2).
- No compiler change, no second document, no fix of R332 (spec § 5a).
- Every task report carries a `## FALSIFICATION` block (CLAUDE.md plan rule 4).
- Branch `ground-truth-slice1`. It reaches `main` only through a PR with a green `test` check.

## Review Focus

1. **The 10 other baseline files must not change.** A document with no `tests/ground-truth/<stem>/`
   gets no `truth` key at all, not an empty one. Pinned in Task 3 (unit test) and Task 4 (the
   regeneration diff touches only `fed-h41-2025-01-02.json` and `inputs.json`).
2. **A record with two concepts whose value equals the label matches nothing.** It must not match by
   taking the first. Pinned in Task 2.
3. **A value that repeats on one row.** Each compiled cell is claimed at most once, and every
   `CORRECT`/`WRONG_VALUE` step runs before any `MISATTACHED` step (spec § 9.2 item 4). Pinned in Task 2.
4. **A `header` attribute naming an id that is not in the table, or a header text that contains ` › `.**
   The extractor raises and writes nothing. Pinned in Task 1.
5. **The fingerprint test's input classifier.** `tests/test_corpus_baseline.py:65` treats every
   `tests/` path as not an input. Adding `tests/ground-truth` to `INPUTS` breaks that test unless the
   test learns the new class. Pinned in Task 3.

---

## Seams measured for this plan (2026-10-22, at `41f4354`)

- `INPUTS` is `scripts/corpus_baseline.py:56-57`:
  `("src", "vocab", "readings", "pyproject.toml", "scripts/corpus_baseline.py", "scripts/corpus_verdict_snapshot.py")`.
  `src/iladub/truth.py` is an input because it lives under `src`. `tests/ground-truth` is not, and
  Task 3 adds it.
- `snapshot(pdf_path)` is `scripts/corpus_verdict_snapshot.py:66-95`. It holds `rep` (from
  `compile_document`) and returns a dict. `rep.graph` is the merged graph (`:94`), and `rep.pages[i].regions`
  are `RegionReport`s.
- `RegionReport` (`src/iladub/etkl/compile.py:753-765`) carries `verdict` (`"asserted" | "escalated" |
  "ignored" | "superseded"`) and `text: str`.
- `Record` is `row_id: str, concepts: tuple[SurfaceConcept, ...]` (`src/iladub/feed.py:73-76`).
  `SurfaceConcept` is `text, value, region` plus defaulted flags (`src/iladub/ground.py:63-66`).
  `table_records(graph, *, per_cell=False)` is `src/iladub/feed.py:502`.
- Fixture builders for `table_records` already exist: `_table(g, table, page, headers, rows)` at
  `tests/test_feed_chain_walk.py:28` and `tests/test_feed_section_keys.py:27`.
- The `tab` rung's criterion list is `tests/arc-manifest.ttl:1225-1229`. The last criterion is
  `tab:12` (`:1526-1537`).
- The truth counts on today's compile are measured, not predicted (handoff "Fifth session"): CORRECT 0,
  MISATTACHED 71, LOST 45, MISSING 8, REFUSED 4, WRONG_VALUE 0; sum 128; MARKED_LABEL 17;
  SPURIOUS 57.

## One point where this plan reads a different source than the spec names (FOR RULING)

Spec § 9.2 item 4 check (ii) takes a non-asserted region's text from `etkl:bandText` or
`iladub:surfaceText`. In the graph, `etkl:bandText` exists only on `etkl:IgnoredBand`
(`vocab/ontology/etkl.ttl:226-227`, emitted at `src/iladub/etkl/holon.py:639`). `iladub:surfaceText`
sits on candidate concepts, not on regions (`holon.py:588`, `to_rdf.py:83`). **Nothing in the graph
marks an escalated region as non-asserted.** `RegionReport` carries both facts directly: `verdict`
and `text`.

**The plan's choice (recommended):** the scorer takes `refused_texts: Sequence[str]` from its caller.
`snapshot()` supplies the `text` of each `RegionReport` on a listed page whose `verdict` is not
`"asserted"`. The scorer stays pure, and the source is the compiler's own verdict, not an inference.
Task 3's oracle (REFUSED = 4, from `p0#ignored4`'s `Total factors supplying reserve funds`) checks it.
**If the maintainer rejects this, check (ii) needs a spec amendment before Task 2 starts.**

---

### Task 1: The truth extractor and the committed truth file

**Files:**
- Create: `scripts/ground_truth_extract.py`
- Create: `tests/ground-truth/fed-h41-2025-01-02/table-1.csv`
- Create: `tests/ground-truth/fed-h41-2025-01-02/provenance.json`
- Test: `tests/test_ground_truth_extract.py`

**Interfaces:**
- Produces: `extract_table(html: bytes, ordinal: int, expected_sha256: str) -> list[TruthRow]`.
  `TruthRow` is a frozen dataclass with fields `row_label, row_label_marked, row_occurrence: int,
  col_path, value`, in that order, which is also the CSV's column order.
  `TableSpanMismatch(ValueError)` is raised when the span hash differs. `TruthMarkupError(ValueError)`
  is raised for an unknown header id or a header text that contains ` › `.
- Produces the CLI `python scripts/ground_truth_extract.py <html> <out-dir>`, which writes
  `table-1.csv` (UTF-8, header row) and leaves `provenance.json` to be written by hand.
- `provenance.json` keys: `url`, `retrieved` (ISO date), `table_ordinal` (2, 1-based, as § 10.1 counts
  it), `span_sha256`, `span_bytes`, `pages` (`[0]`), `source_note` (one sentence: a US Federal Reserve
  release, public).

**Rules the code satisfies** (cited, not restated): field meanings, spec § 3.1. Empty normalised
values are not emitted, and `<br>` becomes one space, spec § 9.2 item 1. `header` values are split on
whitespace (they end with a space; handoff "Fifth session"). The cell's `t1r…` id is never the row,
spec § 9.1. `row_label` comes from the row's first cell. Normalisation is applied to every emitted
field (`src/iladub/truth.py::normalise`, Task 2). **Order note:** Task 1 needs `normalise`, so write
`normalise` and its test first, in `src/iladub/truth.py`, as Task 1's opening step. Task 2 extends that
module.

- [ ] **Step 1: `normalise` and its test.** In `tests/test_ground_truth_score.py`:

```python
from iladub.truth import normalise

def test_normalise_is_exactly_the_three_declared_rules():
    assert normalise("  Week ended\n  Jan 1, 2025 ") == "Week ended Jan 1, 2025"
    assert normalise("-    20,940") == "-20,940"
    assert normalise("+ 62") == "+62"
    assert normalise("a - b") == "a - b"          # a sign is stripped only when leading and before a digit
    assert normalise("Ｒeserve") == "Reserve"      # NFKC
    assert normalise("Reserve") != normalise("reserve")  # no case folding
```

Run it, see it FAIL (ImportError), implement, and see it PASS.

- [ ] **Step 2: The fixture test (spec § 5 test 1).** In `tests/test_ground_truth_extract.py`, put a
  hand-written HTML fragment of one page: a decoy `<table>` first, then a target table with a
  two-level header (a `colspan=2` top cell over two `<br>`-split cells), three body rows (one whose
  label carries `<span style="vertical-align:super">1</span>`, two with the same label `Others`), one
  empty spacer row, and data cells carrying `header="t1r1c1 t1h1c2 t1h2c1 "` (trailing space). Compute
  `expected_sha256` in the test from the fragment's own span. Assert the exact list of `TruthRow`s,
  including `row_occurrence` 0 and 1 for the two `Others` rows, the marked label `Label1`, `col_path`
  `Top › Week ended Jan 1, 2025`, and no row from the spacer.

- [ ] **Step 3: The refusal tests (spec § 5 test 4 and Review Focus 4).** One test each:
  `TableSpanMismatch` when the hash is `"0" * 64`; `TruthMarkupError` when a cell names `t1h9c9`;
  `TruthMarkupError` when a header text contains ` › `. Each asserts that nothing is returned.

- [ ] **Step 4: Run, FAIL, implement `extract_table` with `html.parser`, run, PASS.**
  Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_ground_truth_extract.py tests/test_ground_truth_score.py -q`

- [ ] **Step 5: Produce the real truth file.** Fetch
  `https://www.federalreserve.gov/releases/h41/20250102/` into the scratchpad (never into the repo).
  Run the CLI, then write `provenance.json` by hand.
  **Oracle, all MEASURED against the output:** 128 rows; exactly 4 distinct `col_path`s; 32 distinct
  `row_label`s, all with `row_occurrence` 0; 17 rows' labels where `row_label_marked != row_label`
  (17 labels, so 68 cells); a row `Total factors supplying reserve funds`; a row whose label begins
  `Net portfolio holdings of MS Facilities 2020 LLC`. Any mismatch with spec § 9.1 is a stop: report
  it and do not commit.

- [ ] **Step 6: FALSIFICATION.** (a) Delete the super-span handling and show Step 2's test FAIL.
  (b) Make the hash check a no-op and show the mismatch test FAIL. Restore with `cp` from a saved
  copy, and show green.

- [ ] **Step 7: Commit** `scripts/ground_truth_extract.py`, `src/iladub/truth.py`, the two test files,
  and `tests/ground-truth/fed-h41-2025-01-02/{table-1.csv,provenance.json}`.
  Message: `ground truth slice one: truth extractor and Fed H.4.1 table 1 truth file`.
  **Do not regenerate the baseline yet.** `src/` changed, so `test_the_baseline_was_regenerated_from_this_tree`
  goes red here and stays red until Task 4. That is expected, and it is the one test allowed to be red
  between tasks.

### Task 2: The scorer

**Files:**
- Modify: `src/iladub/truth.py`
- Test: `tests/test_ground_truth_score.py`

**Interfaces:**
- Consumes: `TruthRow` (Task 1). `Record`/`SurfaceConcept` and `table_records` from `iladub.feed`.
- Produces: `load_truth(table_dir: Path, table: str) -> tuple[list[TruthRow], list[int]]`, which
  returns the CSV's rows and the `pages` from `provenance.json`.
- Produces: `score_table(graph, truth: Sequence[TruthRow], pages: Sequence[int], refused_texts:
  Sequence[str]) -> dict[str, int]`. The keys are always all eight: `CORRECT, WRONG_VALUE,
  MISATTACHED, LOST, MISSING, REFUSED, SPURIOUS, MARKED_LABEL`. It calls
  `table_records(graph, per_cell=True)` itself (spec § 3.3).
- **Invariant:** `CORRECT + WRONG_VALUE + MISATTACHED + LOST + MISSING + REFUSED == len(truth)`. Every
  truth cell gets exactly one outcome.

**Rules** (cited, not restated): candidate records, spec § 10.2. Label matching, `row_occurrence`, and
two-concept refusal, § 9.2 item 3. The outcome ladder, claiming, ordering and the unmatched-row checks
(i)-(iii), § 9.2 item 4, with check (ii)'s texts from `refused_texts` (see FOR RULING above).
`col_path` comparison: the truth's ` › ` parts joined with `" > "`, compared with the normalised concept
`text`, § 10.3. SPURIOUS and MARKED_LABEL, § 3.3.

**MEASURE before writing:** how `_table` in `tests/test_feed_chain_walk.py:28` mints regions (the
scorer's page filter reads `SurfaceConcept.region`) and whether its header nodes give a `text` that
joins with `" > "`. If the helper cannot build a two-level header, build the fixture graph with a
single-level header, and record that the `" > "` join is pinned only by Task 3's real run.

- [ ] **Step 1: The outcome test (spec § 5 test 2, as amended).** Build one graph with the
  compiler's own `tab:` terms, via a local copy of the `_table` helper, on page 0 plus one row on
  page 1. Assert the exact eight-key dict when each of these happens once:
  CORRECT (equal path, equal value); WRONG_VALUE (equal path, other value); MISATTACHED (value under a
  wrong header); LOST (value nowhere on the row); MISSING by check (i) (a truth label that is a
  concept's `text`, so a consumed header); REFUSED (a label found in `refused_texts`); MISSING by
  check (iii). Also: a page-1 record with a truth label must not be a candidate; MARKED_LABEL 1 for a
  row matched only through `row_label_marked`; SPURIOUS equal to the unclaimed cells of matched rows.
- [ ] **Step 2: Review Focus 2 and 3.** One test in which a record has two concepts whose value equals
  the label, so its cells score as an unmatched row. One test with a value repeated on a row, where the
  equal-path cell is CORRECT and the second truth cell with that value is MISATTACHED to the other
  compiled cell, never to the claimed one.
- [ ] **Step 3: Run, FAIL, implement, run, PASS.**
  Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_ground_truth_score.py -q`
- [ ] **Step 4: FALSIFICATION.** (a) Run every MISATTACHED step before CORRECT and show Step 2's
  repeat test FAIL. (b) Select candidates by `row_id` prefix instead of region and show the page-1 or
  region assertion FAIL. (c) Drop check (i) and show the exact-dict assertion FAIL. Build the fixture so
  that this label also appears in `refused_texts`, which makes dropping (i) turn MISSING into REFUSED. Restore and show green.
- [ ] **Step 5: Commit.** Message: `ground truth slice one: scorer`.

### Task 3: The snapshot hook, the inputs, and the first real score

**Files:**
- Modify: `scripts/corpus_verdict_snapshot.py` (`snapshot()`, `:66-95`)
- Modify: `scripts/corpus_baseline.py:56-57` (`INPUTS`)
- Modify: `tests/test_corpus_baseline.py:43-67` (the classifier at `:65`)
- Test: `tests/test_ground_truth_snapshot.py`

**Interfaces:**
- Consumes: `load_truth`, `score_table` (Task 2).
- Produces: `truth_block(stem: str, rep, root: Path) -> dict | None`. It returns `None` when
  `root / "tests/ground-truth" / stem` does not exist. Otherwise it returns `{<table>: <eight-key
  dict>}` for each `<table>.csv` in that directory. `snapshot()` adds the key `"truth"` **only when the
  block is not None** (Review Focus 1). `stem` is `pathlib.Path(pdf_path).stem`.
- `refused_texts` is the `text` of every `RegionReport` on a listed page whose `verdict != "asserted"`.

- [ ] **Step 1: Unit tests on `truth_block`, with a stub `rep`** (a namespace object with a `graph` and
  `pages`): `None` for a stem with no directory; one key per CSV when a directory exists.
- [ ] **Step 2: Add `"tests/ground-truth"` to `INPUTS`.** Extend the fingerprint test's file map with
  `"tests/ground-truth/d/t.csv"`, and make its classifier treat that prefix as an input. Every other
  `tests/` path stays a non-input.
- [ ] **Step 3: Run, FAIL, implement, run, PASS.**
  Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_ground_truth_snapshot.py tests/test_corpus_baseline.py -q`
  (`test_the_baseline_was_regenerated_from_this_tree` stays red until Task 4. Read its failure message,
  which should say the fingerprint differs, and treat it as expected.)
- [ ] **Step 4: The first real score (the measured oracle).** One process, nothing else running
  (memory: corpus runs are serial), offline (`BAML_LIVE` and `ILADUB_RECORD_READINGS` unset):
  `PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py <scratch> --pdf held-out/fed-h41-2025-01-02.pdf`
  The truth block must equal **CORRECT 0, WRONG_VALUE 0, MISATTACHED 71, LOST 45, MISSING 8,
  REFUSED 4, SPURIOUS 57, MARKED_LABEL 17**, and every non-`truth` field must equal
  `tests/corpus-baseline/fed-h41-2025-01-02.json`. **Any difference is a stop.** Report which count
  moved and which spec rule produced it; do not adjust the scorer to fit.
- [ ] **Step 5: FALSIFICATION.** Make `truth_block` return `{}` instead of `None` for a missing
  directory and show Step 1's test FAIL. Remove the new prefix from `INPUTS` and show the fingerprint
  test FAIL. Restore and show green.
- [ ] **Step 6: Commit.** Message: `ground truth slice one: truth block in the corpus snapshot`.

### Task 4: Regenerate the baseline, the floor, the criterion

**Files:**
- Regenerate: `tests/corpus-baseline/` (all of it, via the script)
- Create: `tests/ground-truth/fed-h41-2025-01-02/floor.json`
- Create: `tests/test_ground_truth_floor.py`
- Modify: `tests/arc-manifest.ttl` (rung list at `:1225-1229`, plus a `tab:13` block after `:1537`)

**Interfaces:**
- `floor.json` is `{"table-1": {"CORRECT": 0}, "notes": []}`. A note is `{"date", "from", "to", "why"}`.
  Raising the floor needs no note. Lowering it needs one (spec § 3.4).

- [ ] **Step 1: The floor test (spec § 5 test 3).** For every `tests/ground-truth/<stem>/floor.json`:
  the committed `tests/corpus-baseline/<stem>.json` has a `truth` block; for each table, CORRECT ≥ the
  floor; and the six outcome counts sum to that table's CSV row count. (The rule that lowering a floor
  needs a dated note is enforced by review, not by this test.) Run it: FAIL, because no `truth` block
  is committed yet.
- [ ] **Step 2: Regenerate.** `git add` every new input file first, because the script refuses
  untracked inputs. Then `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`, one
  serial pass of about 24 minutes, with no edits while it runs.
  **Oracle:** `git diff --stat -- tests/corpus-baseline/` lists exactly `fed-h41-2025-01-02.json` and
  `inputs.json`. In the fed file, the only change is the added `truth` key (Review Focus 1). Anything
  else is a stop.
- [ ] **Step 3: Run the floor test, PASS.** Then run the full gate:
  `PYTHONPATH=src .venv/bin/python -m pytest -q`. Read `N passed`, not the exit code (memory:
  phantom greens).
- [ ] **Step 4: The criterion.** Add `prog:criterion:tab:13` to the rung list and write a block in
  `tab:12`'s form: statement from spec § 6 ("carried table cells are scored against independent truth,
  and the score is a committed, CI-gated number"; met by the instrument existing, not by a high score),
  `prog:source` the spec, `declaredOn` and `metOn` the merge-day date, `met true`, `oracleArtifact`
  `tests/test_ground_truth_floor.py`, and `oracleTest`s naming the floor test, Task 1's fixture and
  refusal tests, and Task 2's outcome test. **MEASURE what `tests/test_arc_manifest.py` requires of a
  `tab` criterion** (oracle tests must exist, plus any `met` and `blockedBy` rules) before writing it.
  Run `tests/test_arc_manifest.py`.
- [ ] **Step 5: FALSIFICATION.** Set the floor to `1` and show the floor test FAIL. Delete the
  `truth` key from the committed fed snapshot (on a copy put back with `cp`) and show it FAIL.
  Remove `tab:13` from the rung list and show the arc-manifest test FAIL, if it pins rung membership.
  If it does not, say so. Restore and show green.
- [ ] **Step 6: Commit, push, PR.** Message: `ground truth slice one: baseline truth block, floor, tab:13`.
  The PR body records the truth counts, the regeneration diff stat, and that CLAUDE.md § Corpus
  baseline's list of inputs now misses `tests/ground-truth/`. CLAUDE.md is the Contract class, so that
  edit is the maintainer's to make or authorise. Update the handoff and the RESUME memory.

## Self-review (done at authoring)

- Spec coverage: § 3.1 → T1; § 3.2 → T1 step 1; § 3.3 / § 9.2 / § 10.2-3 → T2; § 3.4 → T3-T4;
  § 5 tests 1-4 → T1 s2, T2 s1, T4 s1, T1 s3; § 6 / § 9.2.6 → T4 s4; § 10.1 → T1 s3/s5; § 10.4 → Global.
- § 9.3's second unverified item (`row_occurrence` with a repeated label) is pinned by Task 1's fixture
  and Task 2's page-1 candidate test only. Table 1 has no repeated label, as § 9.3 says.
- The one deviation is in "FOR RULING" above and nowhere else.
