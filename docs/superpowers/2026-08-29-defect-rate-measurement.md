# Is iladub's plan-defect rate a rigour artefact or a real regression?

**Doc impact:** none — this measures the process record; it changes no released artifact.

The maintainer raised the question on 2026-08-29. The handoff after `used as vocabulary`
(`docs/superpowers/2026-08-29-after-used-as-vocabulary-handoff.md` §5) made measuring it the
next concrete action, and made the measurement a **precondition** for two proposals: the
candidate 8th plan rule, and the stronger-model-for-specs hypothesis.

**Answer: rigour, not regression — with one confound that the measurement cannot dissolve, and
one finding that displaces the question.** Detail below; every number is cited.

## 1. What was measured, and by what definition

Three datasets, measured independently in three fresh subagent contexts, so the numbers were not
authored by the session that wanted an answer.

A **plan defect** is a flaw *in the plan or spec text*, discovered during execution: an unmeasured
claim about existing code that proved false, a plan-supplied test that could not pass or pinned
nothing, a self-contradictory instruction, dead wiring the plan named, a constant the plan pinned
that its own tasks moved, a seam the plan called closed that was not. **An implementation bug the
implementer wrote and their own tests caught is NOT one.** Eight ambiguous cases were excluded and
are listed in §5.

Task counts: `grep -cE '^#{2,4} +(Task|TASK)' <plan>`, less two non-task `## Task ordering`
headings (`plans/2026-08-23-the-worktree-that-resolves.md:338`,
`plans/2026-08-25-the-membrane-reports-its-health.md:454`).

## 2. Defects per task, last eight loops

| # | loop (plan date-slug) | shipped as | tasks | plan defects | per task |
|---|---|---|---|---|---|
| L1 | `2026-08-15-escalation-is-a-decision` | PR #105 `540e608` | 6 | 6 | **1.00** |
| L2 | `2026-08-17-the-gate-and-the-label` | PR #106 `96b6dd1` | 4 | 0 | **0.00** |
| L3 | `2026-08-20-the-arc-has-a-denominator` | ff to `main` `b9ec37d` | 8 | 7 | **0.88** |
| L4 | `2026-08-22-the-arc-has-edges` | ff to `main` `8523462` | 7 | 1 | **0.14** |
| L5 | `2026-08-23-the-worktree-that-resolves` | PR #114 `be41973` | 6 | 4 | **0.67** |
| L6 | `2026-08-25-the-membrane-reports-its-health` | PR #123 `a5fa232` | 7 | 5 | **0.71** |
| L7 | `2026-08-28-the-query-names-a-declared-term` | PR #130 `71a6312` | 5 | 4 | **0.80** |
| L8 | `2026-08-29-used-as-vocabulary` | PR #132 `2abc62c` | 8 | 5 | **0.63** |
| | **total** | | **51** | **32** | **0.63** |

Every defect is cited to the commit that hit it in the subagent's ledger; the convention that a
defect is named in the commit that found it held in 7 of 8 loops (L5's task commits carry empty
bodies — see §5).

**The trend, as arithmetic:**

- First four loops: 14 defects / 25 tasks = **0.560**
- Last four loops: 18 defects / 26 tasks = **0.692**
- Movement: **+0.13 defects per task**
- Loop-level standard deviation: **0.440** in the first half, **0.063** in the second — a
  **seven-fold collapse**.

The movement is **0.3 standard deviations of the first half**. It is noise. What actually changed
is not the level but the **variance**: the rate went from swinging 0.00–1.00 to sitting in a
0.17-wide band around 0.7.

**Why the narrative record reads as escalation and the measurement does not.** CLAUDE.md's
§ "Plan authoring discipline" counts defects and never counts tasks: *R73: five defects · the next
loop: a sixth · rules 6 and 7 added · this loop: six.* R73's plan was 919 lines against a 316-line
spec. Normalising by task is the operation that dissolves the escalation, and it had never been
performed.

## 3. The confound the measurement cannot dissolve

**A zero may measure looking, not quality.** The two lowest-rate loops are the two with the
weakest evidence of adversarial attention:

- **L2 (0.00)** ran four tasks with **no adversarial spec review**.
- **L4 (0.14)** raised **14 residues and closed none** — the largest raiser in the register's
  history (§4). Whether it found little in its plan or deferred what it found is not decidable
  from the record.

So the honest form of the answer is asymmetric: the data **refuses** the claim "the per-task defect
rate is rising", and does **not** establish "plan quality is constant". Those are different
statements and only the first was asked.

## 4. The finding that displaces the question

The register, not the plan, is where this process is actually degrading.

- **141 rows, 31 closed (22.0%), 110 open.**
- Closed fraction across the whole recorded series: `R95 = 0.200` → `R151 = 0.220`. Range 3.7
  points wide. **Flat**, stepping up only at four closure events.
- **Raise:close over the last ten loops = 3.93 : 1** (55 raised, 14 closed). Every loop but the
  single-purpose R103 decision loop is net-positive.
- 28 of those 55 raises come from two loops: `the-arc-has-edges` (+14, zero closures) and
  `holon:05` (+14, one).
- Caveat: **84 of 141 rows carry no `(n/m closed)` snapshot** — the convention began at R95
  (2026-08-12), so this trend line covers only the register's most recent 40%.

A defect rate flat at 0.63/task is a process working. A register growing at four rows per closure
is a process accumulating a debt it has never once paid down, and the index it is read through is
already ~2.8k tokens — the size that caused the three-way split in the first place.

## 5. What this measurement does not say

1. **Severity is not normalised.** A missing `Doc impact:` block (L8) and a plan-supplied test
   that pins nothing (L1, L3, L6, L7, L8) are counted alike.
2. **Detection effort is not constant** — §3.
3. **L5 and L6 may undercount.** L5's six task commits have empty bodies; its defects survive only
   in the loop handoff and evidence file, and the per-task subagent reports live in untracked
   `.superpowers/sdd/`, which was not read.
4. **Eight cases were excluded as ambiguous**, listed in the subagent ledger. The largest is L4's
   plan §0, which carries **four measured corrections to a committed spec** — real spec defects,
   but found at plan-authoring time, before execution. Counting them takes L4 from 0.14 to 0.71
   and removes it as an outlier. The exclusion is defensible and it is also the single judgement
   most able to move the result.
5. **The pre-L1 loops are outside the window.** The 2026-08-09 adoption loop — CLAUDE.md's
   five-defect counter-example — was not task-normalised here.

## 6. Consequences

- **The candidate 8th plan rule is NOT adopted.** Its own precondition (§5 of the handoff: adopt
  only if the rate is rising) is not met. It rests on one instance, `bcea2b9`. The register, not
  CLAUDE.md, is where a one-instance pattern belongs until it recurs.
- **The stronger-model-for-specs hypothesis is NOT tested.** Same precondition, explicitly stated
  in the handoff. The defect class in question was *foresight* — the plan author writes in a
  cleared session by design and cannot foresee what execution discovers — and model strength
  closes a foresight gap less than a rule does.
- **The maintainer's answer is: rigour.** The rate is flat within noise once normalised; what rose
  is the consistency of detection.
- **The next thing to fix is the register's raise:close ratio, not the plan discipline.**

## 7. Instrument defect found while measuring (plimslop)

The 2026-08-26 context-regime ruling made one falsifiable prediction: *the override rate falls
below 54%*. Tested against `/Users/francoisrosselet/.claude/plimslop/corpus.jsonl` (739 records,
2026-08-15 → 2026-08-29):

| window | unit | overrides / fired | rate |
|---|---|---|---|
| before 2026-08-26 | working | 17/42 | 40% |
| on/after 2026-08-26 | working | 5/7 | 71% |
| before 2026-08-26 | total | 36/71 | 51% |
| on/after 2026-08-26 | total | 9/11 | 82% |

**The prediction is not yet testable.** The post-ruling arm is 6–7 fired records; `reader.py`
refuses to state a rate below `N_REPORT = 20` and prints `n=6 — this shows nothing`. The raw
counts are not trending in the predicted direction, which is worth knowing and is not evidence.
The `block` gate is correctly held at `warn` (`PLIMSLOP_MODE_ORIGINATING=warn`) until n≥20 so
enforcement strength does not move while the prediction is under test.

**And that small arm is contaminated. `/clear` is not detected anywhere in plimslop**
(`grep -ni clear plimslop/*.py` → no matches). The chain:

1. `plimslop/hook.py:34-42` — the `UserPromptSubmit` hook returns early, writing **no** `turn`
   record, when `session.tokens == 0`. A fresh post-`/clear` session has no assistant `usage` line
   yet, so it is exactly in that state and contributes nothing to the corpus.
2. `plimslop/preflight.py:75-86` — with no `--session`, the session is **inferred from the latest
   `turn` record for this project**: the session that was just cleared. This fallback is
   deliberate and its docstring says so — *"a pre-flight record that cannot be tied to a session
   cannot contribute to a rate"*. **The defect is not the fallback; it is that a `/clear` is
   indistinguishable from a not-yet-measured turn**, so the fallback fires exactly when it is
   wrong and labels the result `measured: true`.
3. `plimslop/preflight.py:89-108` — `working = max(0, tokens + dropped - baseline)` is then read
   off that stale turn, and `preflight.py:52` compares *that* to the floor.

Measured instance, this session: the preflight at `2026-08-29T08:42:34Z` logged
`working: 270265, session_source: "inferred", decision: "overridden"` against a session whose real
context was near zero. The figure belongs to session `3a1c7a94`; the session actually running was
`acdcb012`, and `grep -c acdcb012 corpus.jsonl` = **0**. A milder instance: the preflights of
2026-08-27 and 2026-08-28 carry byte-identical `working 33642` on two different days.

Corrected for it, the post-ruling arm is 4/6 rather than 5/7 — which changes the fraction and not
the sample-size verdict. **The defect inflates override counts on exactly the arm the ruling's
prediction depends on, and it fires on every `/clear`, which is once per loop by design.**

### Repaired the same day — plimslop PR #3

`clear-session-inheritance`, opened 2026-08-29, 136 → 152 tests. The repair does not detect a
`/clear` — it takes the session id the harness names (`CLAUDE_CODE_SESSION_ID`, verified to be the
same id `hook.py` records), which ends every cross-session inheritance at once, including two
sessions open in one project. The same command that produced `270,265 working — OVERRIDE` now reads
`43,128 working — under the floor`.

Two further defects were found by fixing the first, and one by looking:

- `_override` split the observed arm from the counterfactual on the `measured` flag alone. That was
  sound only while every post-repair record carried a measurement — and a legitimately unmeasured
  record becomes scoreable as soon as its session records a turn, because `baselines` is built at
  **read** time. Records now name their own instrument (`unit`).
- The already-contaminated records are counted rather than dropped. **The detector is the signature,
  not the inference**: flagging every inferred record read "47 of 49", which says only that the
  corpus is old. An inherited figure is marked by the inferred session recording *no turn after* the
  decision — a cleared session never speaks again. That reads **11 of 49, and 3 of the 6 in the
  observed arm**.
- `PLIMSLOP_MODE_<SHAPE>`, the documented escape hatch holding the R140 gate at `warn`, had **no
  test**. Now tested end-to-end.

**Consequence for §7 above: the post-ruling arm is not merely thin, it is half suspect** — 3 of its
6 records carry the `/clear` signature. The 2026-08-26 prediction cannot be judged on the corpus as
it stands, and the records that will judge it start accruing from this repair forward.
