# Handoff — the body starts at the stub (spec written, no plan yet)

**Topic:** apple's double header. The predecessor (`2026-09-01-corpus-reach-measured-handoff.md`
§ 5) sent this loop to `infer_column_tree_by_proximity`; the tree was dumped and is **correct**. The
defect is the header/body split typing the years line as body. Spec:
`docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md`.

**Part 5 written first, under the floor** (working figure estimated ~55–65K at the time of
writing; `plimslop preflight` reported "unmeasured, no turn recorded", so this is an estimate and
graded as over). Per CLAUDE.md § "The handoff's next action is TYPED".

**Doc impact: increment** (carried from the spec).

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical

1. **The spec is APPROVED by the maintainer (2026-09-02, in session; recorded here only). Start a FRESH session and invoke `superpowers:writing-plans` on it** — this session stopped at ~98K working tokens, twice the originating floor, and did not write the plan. No plan exists. The spec's
   § 5 names six oracles and § 6 names the three seams the plan must measure before writing a call.
2. **Reproduce § 1.2 before building** (~1 minute): monkeypatch `matrix.header_body_split` to return
   3 on apple p0 band 2 and confirm `region_tiles` is True with a three-level tree. Every figure in
   the spec came from scratchpad scripts that no longer exist; the spec carries their outputs inline.

### PROPOSED — predictions the spec makes that the loop must RUN

- ~~**apple p1's header band asserts a CORRECT reading under the stub rule.**~~ **MEASURED after
  approval, same session — CONFIRMED** (spec § 8 carries the tree: two levels, every data-column
  header word carried, 14 entries, tiles). The accepted drop is honest; the choice stands.
- **`k` from the type split equals `k` from the moved body start on every corpus band.** Measured
  on apple only.
- **The guard (§ 3.2) fires on NO currently-asserted corpus region.** Predicted from WHO's stub
  header being in column 0; the battery (O5) is the test.

### PROPOSED — the maintainer's choice, recorded here and in the spec only

"(A) + (B) refusal, accept the drop" was chosen over settling the adoption gate (C) and over the
eight section-band tiling failures. Reversible; see spec § 4 and § 7.

---

## 1. Goal

Make apple's statement headers assert by deriving the matrix body start from the presence of a
stub cell (AXIOM), and refuse a column tree that drops header ink (producer-side guard).

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md` | The measurements (§ 1), the §8 argument (§ 2), design (§ 3), what is NOT done (§ 4), oracle (§ 5) |
| `src/iladub/etkl/headers.py:84` + `vocab/queries/header-body-split.rq` | The type transition that places the years line in the body. **Untouched by this loop** |
| `src/iladub/etkl/matrix.py:39` (`infer_column_tree_by_proximity`) | Where the guard goes; the tree is otherwise correct on apple p0 |
| `src/iladub/etkl/rows.py:24` (`logical_rows`) | Why the wrong split refuses: the anchor column |
| `vocab/queries/adoption-candidate.rq` | The `NOT EXISTS tab:EntryCell` gate that costs page 1 its adoption |
| `tests/corpus-manifest.ttl` (apple, `cor:rationale`) | Carries the census figures this loop supersedes — the Doc impact increment |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The subject moved from the column tree to the matrix body start | spec § 1; this file; nowhere else yet |
| A: AXIOM derivation, matrix-scoped, `header-body-split.rq` untouched | spec § 2, § 3.1 |
| B: producer-side guard, justified by CLAUDE.md § Producer-side guards | spec § 2, § 3.2 |
| C: the score drop is accepted; the adoption gate becomes a residue | spec § 1.4, § 7 — **maintainer's choice, this session** |
| No new escalation reason, no label grouping | spec § 4 |

## 4. Unverified or assumed

- Everything in spec § 8.
- The full corpus battery has not run in seven loops; the spec's O5 is the first run.
- The `-m "not corpus"` suite was not run this session (no `src/` change yet).
- The working-token figure above is an estimate.

---

## Session 2 (2026-09-02, fresh context) — the plan is WRITTEN; part 5 re-typed

**Plan:** `docs/superpowers/plans/2026-09-02-the-body-starts-at-the-stub.md`, on branch
`the-body-starts-at-the-stub-build` (off `main` at `f4fd540`, PR #151's squash). Written under the
originating floor (`plimslop preflight` at session start reported "unmeasured"; the plan was the
first artefact of the session, after ~40K tokens of reading and measurement).

**Everything the session-1 part 5 asked for was done before the plan:** § 1.2 REPRODUCED (forced
split=3 on apple p0 band 2 → 3 levels, 28 entries, tiles), the two-binding `run_scalar` seam driven
(returns 3 / 3 / 2 on apple p0, apple p2, the crosstab fixture), `absorb_unit_markers` placed
(`page_bands`' last statement), the three synthetic fixtures the oracle needs CONSTRUCTED and
measured, and the HEAD baseline captured (apple 0.3587 `adopted [1]` 35.7 s; WHO 0.9096 `adopted []`
41.9 s). All in the plan's "Measured seams" S1–S6.

**One correction to the spec, recorded in the plan (S5), not edited into the spec:** apple p2 band 2
at HEAD does not refuse in `classify_matrix`; it builds a 2-level region and is stopped by
`region_tiles` → False. The loop's consequence is unchanged.

**One plan decision that departs from the spec's wording (plan Global Constraints):**
`is_matrix_candidate` is left untouched — its only use of `split` is the `>= 2` count, which the
moved start (invariant `>= split`) can only raise.

### 5. The next concrete action — TYPED

**ASSERTED — executing shape (150K working floor):** run the plan, task by task, with
`superpowers:subagent-driven-development`. Task 1 is a measurement whose expected output is already
in the plan; Tasks 2–4 are unit-fixture TDD with their tests supplied verbatim and falsification
mandatory; Task 5 is the corpus leg; Task 6 the register.

**PROPOSED — what the run may refute:** (a) the report-side `MATRIX_AMBIGUOUS` count lands at 1
(plan Task 5 Step 2); (b) `test_typing_equiv.py`'s apple page-0 pins do not move; (c) the manifest
shape accepts a second `cor:adjudication` node. Each is checked in minutes by the task that meets it.

---

## Session 2, close — execution STARTED and handed off at the executing floor

Execution began in the plan-writing session under `superpowers:subagent-driven-development`; the
context gate then reported **167,732 working tokens, 1.1× the 150K executing floor**, and the session
handed off (logged by `plimslop preflight`, decision `handoff`). State on disk, all of it:

| where | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-09-02-the-body-starts-at-the-stub/progress.md` (git-ignored, this checkout) | the SDD ledger: pre-flight scan table, rulings, Task 1 complete, Task 2 status and its review verdict |
| same directory: `task-N-brief.md`, `task-2-report.md`, `review-78f9dec..11d0588.diff`, `global-constraints.md` | briefs for all six tasks; Task 2's implementer report and review package |
| branch `the-body-starts-at-the-stub-build`, commits `78f9dec` (plan) and `11d0588` (Task 2) | the work itself; pushed |
| `<scratchpad>/baseline-HEAD.json` from session 2 (path in the ledger) | Task 5's HEAD side; if that scratchpad is gone, re-run Task 1 (35 s + 42 s) |

### 5. The next concrete action — TYPED

**ASSERTED — executing shape, in a FRESH session:** open the ledger, confirm Task 2's line reads
`complete` (or resume its fix loop at the round the ledger names), then invoke
`superpowers:subagent-driven-development` on the plan and continue at **Task 3**. The plan's task
text is the brief; nothing needs re-deriving.

**PROPOSED (unchanged from the section above):** the three predictions the run may refute are
listed there; each is checked in minutes by the task that meets it.
