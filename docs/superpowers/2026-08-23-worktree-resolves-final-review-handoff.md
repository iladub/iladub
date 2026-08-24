# Handoff — all six tasks reviewed clean; whole-branch review DONE; ONE fix wave in flight

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-worktree-that-resolves`
**Runner:** `./.venv/bin/python`, never `python3`.
**Shape: executing, written at 126k** against the 150k executing floor.
The ledger, not this file, is the resumption state:
`.superpowers/sdd/2026-08-23-the-worktree-that-resolves/progress.md`.

## §1 Where the loop stands

**All six tasks of `docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` are
complete, each with a clean task review.** HEAD `57ed10a`, tree clean, one worktree.

| task | commits | verdict |
| --- | --- | --- |
| 1 — probe module + explicit `PYTHONPATH` on `_run_module` | `256955b..7e4f84c` | clean |
| 2 — materialise `baml_client` + disjointness collision guard | `6f977b6..2d08f06` | clean |
| 3 — `_run_control`, the un-ablated control run | `2d08f06..95bfb9a` | clean |
| 4 — a collection ERROR must name the removed artifact (R118) | `5816384..5f2cad9` | clean |
| 5 — limitation-4 rewrite + register rows | `5f2cad9..bde884a` | clean after 1 fix round |
| 6 — the live run, evidence file, R122/R123 | `bde884a..57ed10a` | clean |

**The result the loop existed to produce:**

```
ablation_refusals(LIVE MANIFEST) = []
len: 0
```

Spec §9's up-front prediction, returned by the **first** run, nothing tuned. DoD item 3 also met:
**1320 collected / 0 collection errors** in a worktree the shipped `_ablate` creates, down from
M3's 6. Full suite `1312 passed, 7 skipped, 1 xfailed` in 36:41, exit 0.

## §2 The only thing outstanding — SUPERSEDED, see §6

**The whole-branch review is dispatched (opus) and its result has not been seen.** Package:
`.superpowers/sdd/2026-08-23-the-worktree-that-resolves/review-b03efb6..57ed10a.diff`
(16 commits, 312 KB, merge-base `b03efb6`).

It was framed around the one question no task-scoped reviewer could answer: **was `[]` earned or
engineered?** The cheap half is already settled — `tests/arc-manifest.ttl` and
`tests/arc-shapes.ttl` are byte-identical to `main` across the whole branch, so no edge was
authored or deleted. The half it is answering is whether the **instrument's own logic** drifted
toward `[]` across Tasks 1–4, with §4.5 named as where a suppression would hide (narrowing what
counts as evidence is exactly that shape).

It also carries four deferred minors to triage and the twice-deferred process finding (§4 below).

**If it returns findings:** ONE fix dispatch with the complete list, then exactly one scoped
re-review (`review-package PLAN FIX_BASE HEAD`), then adjudicate residuals into the ledger. There
is no second fix wave. Then `rm -rf` the workspace and use
`superpowers:finishing-a-development-branch`.

## §3 What this loop measured that its own plan had wrong

These are the loop's corrections to itself and they are the substance, not bookkeeping:

- **Task 4's census is REFUTED by Task 6.** "Zero of the 29 declared artifacts are `.py`" is
  false — two are (`tests/etkl/fixtures.py` at `tab:06`, `tests/etkl/test_vacuity_registry.py` at
  `tab:10`). `fixtures.py` is imported at **module scope** by `tab:01`/`tab:03`'s oracle, and
  driven through the shipped instrument `_ablate` **raises**
  (`ModuleNotFoundError: No module named 'tests.etkl.fixtures'`). Bounded by a second measurement:
  a function-scope import of the same file scores an ordinary `failed`. Latent (neither criterion
  is an edge endpoint) and safe in direction. **Filed as R123.** This finding would have died if
  it had been left to the final fix wave.
- **The plan's Task 4 Step 5 rationale stands refuted.** The live manifest produces **0**
  collection ERRORs across 13 `_scores` invocations / 4 modules, so §4.5 is dormant live and
  `test_m19_the_live_manifest_carries_no_refuted_edge` cannot notice a never-matching rule. The
  true positive rests on the new test's first half plus falsification direction B.
- **Seam S2 closed** (`--tb=line`): the old docstring claim is confirmed in shape but refuted
  where it matters — the short-summary tail clips to terminal width, and on the import-error shape
  carries no exception at all.
- **"A newly grounding pair" is UNFALSIFIED, not refuted.** Outside the 6 asserted edges plus
  `holon:02 → holon:01` (re-probed in memory, still refuted for R117's oracle-gap reason), no pair
  has ever been run through `ablation_refusals` on either instrument version. Stated in the
  shipped evidence file, not only in a report.

## §4 Carried forward — do not let these die here

**Deferred minors, handed to the whole-branch review to triage:**

1. Task 2: the `ablation_refusals` collision guard sits after the pre-existing
   `dangling`/`testless` assertions rather than literally first. Both filesystem-free; wording gap.
2. Task 4: the report's Direction-A falsification prose describes inverting a variable inlined
   during self-review. Report-only cosmetic.
3. Task 6: `tests/test_arc_ablation.py:832,911` — a stale line range was replaced with a **fresh**
   line range, re-creating the fragility it repaired. The durable form names the raise by content.
   Adjacent to R119/R120's class, covered by neither.
4. Task 6: the evidence file's verbatim quote of spec §7 elides `(§9)` inside quotation marks.
   **This one is fix-now-or-never** — `docs/superpowers/**` is Evidence class, immutable after
   loop close.

**The twice-deferred process finding, still unruled by the maintainer:** the plan is **1168 lines
against a 338-line spec** — a worse ratio than the 919-line plan CLAUDE.md holds up as its own
counter-example. The standing claim is that it contains no function bodies (verified: zero
non-test `def`s) and the bulk is measurement transcripts plus verbatim tests, so it is not the
rule-1 violation the ratio suggests. The whole-branch review was asked for a verdict.

**Never adversarially reviewed:** no adversarial review has run on the spec. PF-4 and Task 4's two
findings all came from that class of reading, so the gap is live.

## §5 The controller lesson this loop paid for

**I asserted a line range from a ledger note instead of measuring the file, and was wrong.** I
told Task 6 to correct the stale `_scores:219-226` docstring reference to `:412-418`. It shipped
`:440-446` and argued from content; its reviewer opened the file and confirmed the implementer:
`:440-446` **is** the unresolved-node-id raise that both docstring sentences describe, while
`:412-418` is Task 4's §4.5 collection-ERROR raise — the wrong raise **and** an off-by-one span
(it actually spans 411-419), and at site `:911` it would have been circular. This is CLAUDE.md
plan-authoring rule 2 landing on the controller rather than on a plan author.

Two other process facts worth keeping:

- **The controller does not commit while an implementer is live.** Violated once in the prior
  session (`5816384`), verified harmless, but it shifted Task 4's review base.
- **A long suite run piped through `tail` loses everything if the environment kills it.** Task 6's
  first full-suite attempt died at ~68 minutes with zero bytes written. Redirect to a file and
  read the tail afterwards.

---

## §6 UPDATE (supersedes §2) — the review is done; one fix wave is mid-flight

**Written at 143.7k, at the 150k executing floor. This section is the resumption state.**

### The verdict

**`[]` was EARNED, not engineered.** Five independent lines, all re-derived by the reviewer rather
than read from reports. The strongest was not something this controller thought to ask for:
`assert ablation_refusals(g) == []` was **already the shipped gate on `main`, and already passed**
— a suppression story needs a non-empty starting point, and there wasn't one. Per-arm analysis
shows the changes are not monotone toward `[]` (§4.1 *opens* the arm-2 refusal direction), and
**no code path converts a refusal into silence** — the worst §4.5 does is convert one into a loud
stop. Six falsifications reproduced in a throwaway worktree. Gate (CLAUDE.md §8) clean: no tuned
constant, tolerance, retry or timeout. GC2/GC4/GC7 verified empirically.

**Zero Critical. One Important, three Minors.** Full detail in the ledger.

### The fix wave — STALLED TWICE, TREE LEFT DIRTY (read the ledger tail first)

One fix dispatch (sonnet) is live. It was killed by the machine sleeping mid-response — the
**third** environment failure in this loop — and resumed rather than re-dispatched, per the same
ruling used for Task 5.

State at the interrupt: **Fix 1 applied, `tests/test_arc_ablation.py` 9 passed.** Outstanding:

1. **Fix 1 (Important) — DONE, needs verifying.** Four sites across three files
   (`tests/test_arc_ablation.py` guard docstring ~`:345-350` and test docstring ~`:804`,
   `tests/arc-m19-materialised-artifact.ttl:24-30`) claimed materialisation copies a file back
   **after** deletion, so the deletion is pre-empted. **False**: `_materialise` runs at ~`:468`,
   the unlink loop at ~`:469-477` — materialise BEFORE unlink, deletion effective, no false green.
   The guard is still right to exist for the **unstated** reason that materialisation smuggles an
   uncommitted, gitignored file past `_ablate`'s committed-tree refusal. This is the R120 shape,
   shipped by the loop whose own §6 exists to correct that shape.
2. **Fix 2 — outstanding.** Restore the elided `(§9)` in the verbatim spec §7 quote at
   `docs/superpowers/2026-08-23-worktree-that-resolves-evidence.md:394`. Fix-now-or-never: the file
   is Evidence class, immutable after loop close.
3. **Fix 3 — outstanding.** Two register rows: (A) spec §4.4's stated mechanism is superseded by
   the measured ordering — the spec is immutable so the correction lives in code plus this row;
   (B) the **pre-existing** GC2 exposure — nothing constrains a `prog:oracleArtifact` path's shape
   (no `sh:pattern`), so a declared `../../x` would unlink outside the worktree, with `_scores`'
   bare substring containment (~`:411`) as context.

### The next concrete action

1. Confirm the resumed fixer committed, and re-read its report at
   `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/final-fix-report.md`.
2. **Run exactly one scoped re-review** of the fix wave: `review-package PLAN 57ed10a HEAD`, then
   `re-review-prompt.md` with the three findings above. **There is no second fix wave** — adjudicate
   residuals into the ledger and surface them.
3. Then `rm -rf .superpowers/sdd/2026-08-23-the-worktree-that-resolves/` and use
   `superpowers:finishing-a-development-branch`.

### Two things that need the maintainer, not another loop

- **The rule-6 candidate**, offered by the whole-branch review after the plan-ratio finding was
  deferred a third time and then finally ruled: *state the invariant once; a plan that argues the
  same point in three places is a spec that was not finished.* The ratio itself (1212 vs 368,
  3.3:1) was ruled **not** a plan-authoring violation and **not** a merge blocker — CLAUDE.md
  condemns its counter-example for five content defects, not for length, and this plan has none of
  them. But the defence on record ("the bulk is transcripts plus verbatim tests") is **false**:
  310 of 1212 lines are fenced; ~900 are prose. The real residual is context budget, not rule 1.
- **No adversarial review has ever run on this spec.** PF-4 and Task 4's two findings all came from
  that class of reading, so the gap is live.

### The environment failure this loop kept paying for

Three kills from the machine sleeping mid-response (Task 5, Task 6, the fix wave). Each time the
right move was to **resume the same agent and tell it to re-read `git diff` first**, never to
dispatch fresh onto a dirty tree. Also: Task 6's first full-suite run was piped through `tail` and
lost all 68 minutes of output when it was killed. **Redirect to a file; read the tail afterwards.**

---

## §7 FINAL STATE — the tree is DIRTY and the fix wave is UNCOMMITTED

The resumed fixer stalled a second time (watchdog, 600s no progress) — the **fourth** environment
failure of this loop — just as it was about to re-run its tests. **The controller stopped at 153.2k,
past the 150k executing floor, and did not fix anything itself** (that would skip review).

**Measured at the stop, HEAD still `57ed10a`:**

```
 M docs/superpowers/2026-08-23-worktree-that-resolves-evidence.md   (1)   Fix 2 — the (§9)
 M docs/superpowers/residues-open.md                                (+2)  Fix 3 — two rows
 M docs/superpowers/residues.md                                     (11)  index + headline + awk
 M tests/arc-m19-materialised-artifact.ttl                          (14)  Fix 1 — fixture comment
 M tests/test_arc_ablation.py                                       (41)  Fix 1 — two docstrings
 ?? docs/superpowers/2026-08-23-worktree-resolves-final-review-handoff.md   (this file)
```

No `final-fix-report.md`. Tests **not** re-run after the edits. One worktree, nothing leaked.
All three fixes *look* applied by the diffstat — **that is a diffstat, not a verification.**

### Do these in order

1. **Read the uncommitted `git diff` in full and verify each fix is complete and correct.** Fix 1
   is the one to scrutinise: it must state the *real* hazard (materialisation smuggles an
   uncommitted, gitignored file past `_ablate`'s committed-tree refusal) and must no longer claim
   the deletion is pre-empted. Re-measure the `_materialise`-before-unlink ordering yourself.
2. `./.venv/bin/python -m pytest tests/test_arc_ablation.py -q` (expect 9 passed) and
   `tests/test_doc_governance.py -q` (expect 4 passed, 2 pre-existing warnings). Re-run the
   register's own `awk` self-check and confirm the headline agrees.
3. Write `final-fix-report.md` and commit.
4. **ONE scoped re-review**, `review-package PLAN 57ed10a HEAD`. There is no second fix wave.
5. Commit this handoff, `rm -rf` the workspace, `superpowers:finishing-a-development-branch`.
