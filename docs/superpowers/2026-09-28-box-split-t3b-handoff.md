# Handoff: box-split, Task 3b — the under-resolution guard refuses cbh T1 (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Topic:** box-split · **Date:** 2026-09-28 · **Doc impact: none.**
**Authored at:** ~66K working tokens by the controller of the subagent-driven execution. That is
over the 50K originating floor, which is why the design below is handed off rather than written
here. Parts 1–4 are pointers. Part 5 is graded per action.

## 5. Next action (written first)

- **Asserted:** in a fresh session, invoke `superpowers:subagent-driven-development` on
  `docs/superpowers/plans/2026-09-28-box-split.md`, workspace `.superpowers/sdd/2026-09-28-box-split/`.
  Read `progress.md` there first. Tasks 0, 1, 2 and 3 are complete (commits to `5ab01ad`, and
  Task 3's review is clean after one fix round). Do not re-dispatch them.
- **Asserted (maintainer ruling, 2026-09-28):** the loop is EXTENDED with a **Task 3b** that fixes
  `_build_ruled_band`'s under-resolution guard for the case below. The plan's Global Constraint
  "`_build_ruled_band` is not modified" is lifted for **that guard only**. The branch does not
  merge until O2 XPASSes. **Do not re-pin** `BASELINE_ASSERTED[("cbh-stem-2026-08-03",0)]` (54 → 8
  measured) or `EXPECTED_VERDICTS["cbh"]`. Those move only once T1 reads.
- **The fresh session AUTHORS Task 3b** (originating work): a spec addendum to
  `docs/superpowers/specs/2026-09-28-box-split-design.md`, classified under CLAUDE.md § 8 before
  any code. Then it executes 3b, then Task 4 Steps 4–5, Task 5 and Task 6 as the handoff
  `2026-09-28-box-split-execution-handoff.md` § 5 describes.
- **Proposed, and it may fail:** that fixing the guard makes T1 a RecordTable and flips O2 to
  XPASS. It was measured only that the rule re-bucket puts T1's header words into the right 7
  cells. The full classify → compile → membrane path with the guard relaxed has **not** been run.
  Spec § 4 risk 1 (T2's first row read as a boxhead) is still unrun on the real tree. T2 is already
  a RecordTable (`#table11`), so that risk has at least not fired.
- **Proposed:** the design direction. The guard compares a **rules-free gutter count** (`_word_column_count`
  → `infer_leaf_grid(...).ncols` = 9 on T1) with the rule columns (7). **Measured**
  (`2026-09-28-box-split-t3b-measurements.md` M1): header line alone → 7, body lines alone → 7,
  both together → 9. In the WHEAT and TOTAL cells the header word sits wholly right of the body
  numbers, so the union of gutters invents two columns. Two directions to weigh, neither chosen:
  - (a) judge under-resolution on BODY lines only;
  - (b) treat "does this header cell span these words" as a reading judgement, which CLAUDE.md
    § 8's one-geometric-attempt ruling (2026-09-17) routes to NEURAL.

  The guard's gutter count **is** a geometric attempt, and cbh T1 is its refutation. Weigh that
  before writing a second heuristic.

## 1. Goal

Make cbh p0's T1 box band read as a 7-column RecordTable, so that O2 (`tab:12`) XPASSes and the
split ships compiling.

## 2. Where the primaries are

- **Ledger** `.superpowers/sdd/2026-09-28-box-split/progress.md`: every `Ruling:` line, including
  the maintainer's extension ruling and the Task 3 review outcome.
- **Task 3 report** `.superpowers/sdd/2026-09-28-box-split/task-3-report.md`: concern 1 (the
  guard), concern 2 (the AT-RISK re-measurements), the per-file Step 3 results, and FALSIFICATION
  (i)–(v).
- **The guard:** `src/iladub/etkl/compile.py`, `def _word_column_count` and the `_under_resolved`
  assignment inside `def _build_ruled_band`. Cited by symbol, not by line, since this file moves.
  Its placement rationale (why it must not return early and skip `refine_rule_columns`, R13) is in
  the comment above it. Read that before touching it.
- **The split:** `src/iladub/etkl/boxsplit.py` `def split_band`, wired in `def page_bands`.
- **Controller probe** (scratchpad, not tracked): T1 after the split has rules x `38.2, 76.0, 154.5,
  216.5, 259.5, 302.4, 345.4, 449.1` and header words `PORT 50.9 | WHEAT 106.6 | MAIN 158.5 WHEAT
  173.9 GRADES 193.4 | BARLEY 229.3 | CANOLA 271.1 | OTHER 316.0 | TOTAL 389.8`. Every word falls
  in exactly one rule interval, and the 7 header cells are correct. Re-run it to reproduce: call
  `page_bands(cbh, 0)` and select the band with 8 rule boundaries.
- **Red locally, blind in CI** (corpus-marked):
  - `tests/etkl/test_typing_equiv.py` (cbh);
  - `tests/etkl/test_run_merge_seam.py` (cbh floor 54);
  - `tests/etkl/test_escalation_furnish.py::test_corpus_a_wholly_superseded_document_furnishes_nothing`
    (missed by evidence § 2.3; add it there).

  `tests/test_cbh_e2e.py` has not been run post-split.

## 3. What was decided, and where it is recorded

- **Extend the loop with 3b; lift the constraint for the guard only; no re-pin.** Maintainer
  ruling, recorded in the ledger (`Ruling (MAINTAINER, 2026-09-28 …)`) and in this file.
- **Task 3's deviations are accepted** (the `build_sub` callback, the residue scoped outside the
  boxes, the 4-tuple `specs`). Recorded in the ledger. The residue scope is to be recorded as a spec
  § 3.3.2 amendment in the evidence file at Task 5. Nowhere else yet.
- **The 3b design is handed off, not written, because of the context floor.** Recorded in the
  ledger and in plimslop's pre-flight log.

## 4. Unverified or assumed

- **Measured since, and pointed to rather than restated:** `2026-09-28-box-split-t3b-measurements.md`
  (M1: the 9 columns; M2: corpus census of all 100 `_build_ruled_band` calls with a control, 36
  refused — ons 21, bfs 14, cbh 1 — including **8 bfs p6 bands with cbh T1's shape, 6 rule cols vs
  9 word cols**; M3: guard introduced `d588412`, R225 D1, spec
  `specs/2026-09-14-the-gate-not-the-predicate-design.md` § 1e; **no test names the guard**).
- **Not yet run:** what a relaxed guard does to those 35 other refusals. Only the 24 prose-citing
  R225 D1 tests were run guard-off (all pass). `test_o3_no_page_loses_asserted_ink_to_a_merge` and
  the full suite were not. The bfs p6 bands are the population a 3b change must be judged on.
- Whether `page_boxes` on every page has a measurable corpus runtime cost: unmeasured (deferred minor).
- Whether the residue (`1,951,264` + the Note block, 86 tokens) should read as notes: out of scope
  by spec § 4, and recorded, not engineered.
