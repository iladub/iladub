# Handoff — the register serves the arc: tasks 1–4 executed; 5 and 6 wait for the maintainer

**Topic:** register-serves-arc
**Serves:** maintenance — the loop moves no criterion; it changes how the next subject is chosen.
**Date:** 2026-09-11. **Loop shape:** executing (from the plan of PR #203), written under the
150K floor; no working figure was reported this session. **Doc impact: none** (the plan declares
its own; `prog:` is repo-internal).

Part 5 written first.

## 5. The next concrete action

### 5a. ASSERTED — merge this PR, then run tasks 5 and 6 of the plan WITH the maintainer present

Tasks 1–4 of `docs/superpowers/plans/2026-09-11-the-register-serves-the-arc.md` are executed on
this branch, each with its `## FALSIFICATION` arms run (§ 2 below). Tasks 5 (the CLAUDE.md text)
and 6 (the triage pass over the 80 candidates) are gated on the maintainer and were **not started**:
task 5 because CLAUDE.md is Contract-class and is edited on explicit request only; task 6 because
parking is the maintainer's decision, per row, dated, with a reason. The plan carries the CLAUDE.md
text verbatim (task 5) and the triage procedure (task 6). `scripts/residue_graph.py --candidates`
lists the 80.

### 5b. PROPOSED — carried forward unchanged from the plan handoff

The maintainer parks fewer than 40 of the 80. If they park most, PARKED is doing the work a
`closed`-by-ruling state would do and the spec's "never a closure" line should be re-argued. Runs
at task 6.

### 5c. PROPOSED — spec § 3.2's prediction, now measurable

The arc line reads `serves 0/3/34` with this handoff on disk (7-day window: this handoff and its
two predecessors declare `maintenance`; it read `0/2/34` before this file existed; re-measure, the
window slides). Spec § 3.2: the criterion count leaves zero
within three loops, or § 4's fork is the remedy. The first loop that writes `**Serves:**
prog:criterion:<rung>:<slug>` moves the first digit.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the plan | `docs/superpowers/plans/2026-09-11-the-register-serves-the-arc.md` | tasks 1–4 as executed; tasks 5–6 as still to run; § Measured |
| the spec | `docs/superpowers/specs/2026-09-11-the-register-serves-the-arc-design.md` | § 3.1–3.3 the rules; § 4 the maintainer's fork; § 3.2 the prediction 5c carries |
| the code | `scripts/cockpit.py` (`serves()`, `serves_window()`, `parked()`, `_loop_docs()`, `_criterion_ids()`), `scripts/residue_graph.py` (`read_rows()` 4-tuple, `candidates()`, `--candidates`), `tests/test_arc_manifest.py` (`parked_rows()`, M21 branch) | the four commits on this branch, one per task |
| the tests | `tests/test_residue_graph.py` (new), `tests/test_cockpit.py` (+9), `tests/test_residue_register_integrity.py` (+2), `tests/test_arc_manifest.py` (+1), fixture `tests/arc-m21-parked-blocker-leak.ttl` | every plan-supplied test ran RED then GREEN; none was weakened or substituted |
| the predecessor handoff | `docs/superpowers/2026-09-11-the-register-serves-the-arc-the-plan-handoff.md` | its 5b/5c, carried here; its part 4 list, three of which are now measured (§ 4 below) |

## 2. What was measured this session (branch `the-register-serves-the-arc-execute` off `8b3f12c`)

- **Task 1.** RED: `missing [131, 141]`. After the regex: `residue_graph.py`'s printed lines are
  byte-identical before and after (`largest 79 rows R26..R205, 46 open`; hubs R173/R188/R165/
  R166/R187/R174). Falsified: old regex restored → RED with the same two ids.
- **Task 2.** Strip line 1 now `register-serves-ar · maintenance · the-register-serves-the-arc- ·
  …`. Falsified twice: membership check removed → `etkl:99` leaked; the live handoff's field renamed
  to `Server:` → the live test RED naming the file.
- **Task 3.** Strip line 2 ends `frontier 13  ready 15  serves 0/2/34` — the plan's predicted
  figure exactly. Falsified twice: date filter dropped → `(2, 1, 2)`; `(0, 0, 0)` on no manifest →
  both `serves ?` tests RED with `serves 0/0/0` on the arc line.
- **Task 4.** The two integrity fixture tests **passed before any code changed** (the plan
  predicted it: the qualifier is prose to `_INDEX_ROW`). `--candidates | wc -l` → **80**. Strip line
  1 carries `parked 0`. Falsified three ways: `parked()` → 0 fails on the `== 1` line with the
  `(2, 4)` tally assertion above it intact; M21 branch deleted → refusal set `set()`; open-neighbour
  clause dropped → 122 candidates.
- The four files: **62 passed**; `test_source_ownership`, `test_doc_governance`, `test_arc_ablation`:
  **19 passed** with the M21 fixture tracked.
- **One count in the plan's prose was wrong and is not in the code:** task 4 step 3 says "sixteen
  not in SHACL"; fourteen are in SHACL and M19 is the fifteenth elsewhere, so the docstring reads
  "Fifteen of the nineteen refusals are NOT here" and lists six environment questions.

## 3. What was decided, and where that decision is recorded

- **Nothing new.** Every decision is the plan's (its § 3 table in the predecessor handoff);
  this loop executed them. The one judgment call: `test_the_work_line_degrades_on_a_detached_head`
  monkeypatches `serves` too — recorded in the task 2 commit message, as the plan required.
- **Tasks 5 and 6 are skipped, not done** — recorded here and in the PR description.
- **The `cockpit.py` script blocks when run with an open non-tty stdin** (it reads session JSON);
  run it `</dev/null` from a tool harness. Recorded nowhere else.

## 4. Unverified or assumed

- The M21 fixture's `prog:source` pointer (`…-denominator-design.md:423-424`) resolves today (599
  lines) — measured, and the exact-set assertion proved it earns no M10; it will go stale the day
  that spec is edited, as the M7 fixture's will.
- `work()`'s width with a fourth segment is not measured against any renderer limit; line 1 is
  ~165 characters on this tree.
- The plan's predicted `serves 0/2/34` matched; whether the window's population is the 36 docs the
  plan counted was not re-derived (the third bucket is 34, consistent with 36 − 2).
- No full-suite run this session (~61 minutes); CI on the PR is the run of record.

## 6. Tasks 5 and 6 — run 2026-09-11 with the maintainer present (appended; § 5a is now done)

- **Task 5.** Asked in-session; the maintainer said yes. CLAUDE.md § Deferred residues gained the
  plan's two paragraphs verbatim (`diff` against plan lines 654–669 empty). `test_doc_governance.py`:
  7 passed. Commit `0e119ac`.
- **Task 6.** The 80 candidates (`--candidates`, re-measured: still 80) were presented with their
  index lines. **The maintainer parked none today.** No register file changed. Tally before and
  after: `cockpit.residues()[:2]` → `(63, 198)` both times; `parked()` → 0. The four test files:
  62 passed. Strip line 1 reads `… 63/198 closed ▲1.0 parked 0 …`; line 2 ends `serves 0/3/34`.
- **5b, first reading:** 0 of 80 parked is under 40, so the prediction held trivially. It is not
  yet informative: a pass that parks nothing does not test whether PARKED is doing `closed`'s work.
  It becomes informative at the first pass that parks a row. Carried forward, not refuted.
- **5c** is unchanged by this: the loop declares `maintenance`, so the criterion digit stays 0.

## 7. CI on `90f673c` FAILED — the tracked-`.ttl` population trap, again (appended 2026-09-11)

Two tests, one cause: `test_artifact_terms.py` and `test_artifact_declarations.py` pin the `.ttl`
population as a re-measured number (148) and `tests/arc-m21-parked-blocker-leak.ttl` joined it at
`git add` (`assert 149 == 148`; `(151 - 2) == 148`). § 2 above lists the files this loop ran
locally — neither of these was among them, which is exactly the trap [[R179]]'s memory recorded:
a new tracked `.ttl` fails only after `git add`, and only in tests the loop did not think to run.
Re-measured to 149 in both, with the conventional dated comment; both files pass locally (27).
