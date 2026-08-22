# Handoff — the arc loop's four closing items are discharged; only the merge is left

**Topic:** process · **Date:** 2026-08-22 · **Branch:** `arc-denominator` @ `bc6c5cc` (from `main` @
`f436a8c`) · **Shape: executing** · **Status: items 1-3 of the close DONE. Item 4 — the merge — is the
maintainer's and is the only thing left.** Nothing is pushed.

## Goal

Close the loop that gave every rung of the arc a countable denominator: raise what the branch held
only in prose, get the branch reviewed whole, run both suite legs at the head, and hand over the
merge.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | the SDD ledger — Rulings 1-21, every task's evidence, and this session's Session 6 entry. **Git-ignored: `git clean -fdx` destroys it** |
| `.superpowers/sdd/.../whole-branch-review.md` | the whole-branch review: verdict, the B1 finding, the **~42-minor triage table** (0 BLOCK / ~28 DEFER / ~13 VOID), the four independent re-derivations of `17/43`. **Also git-ignored** — its three actionable clusters were lifted into R109/R110/R111 for exactly that reason; the rest of the table dies with the directory |
| `docs/superpowers/residues.md` + `residues-open.md` | R107-R112, the six rows this close raised. **Tracked** — this is where the branch's findings actually survive |
| `docs/superpowers/2026-08-22-arc-loop-close-handoff.md` | the previous handoff. Current on the eight tasks; its four "remaining items" are what this file discharges. **One correction: its `scripts/review-package PLAN f436a8c HEAD` does not exist** — no such script in the repo or on the machine. The package is a plain `git diff a..b > review-a..b.diff` |
| `scratchpad/warning-attribution.md` | the 10 warnings, attributed site by site. Scratch, not tracked; the durable half is R112 |

## What was decided, and where each decision is recorded

- **B1 was fixed, not deferred** — nine stale `<path>:<line>` citations from Task 8's docstring
  rewrite, two of them in `vocab/`, one inside a live `sh:message`. Recorded in commit `c957bd5` with
  the `git show f436a8c:…` measurement inline. Taken on the maintainer's behalf because it is ten
  mechanical comment edits and because shipping the branch that closed R105 while re-opening R105's
  failure mode is a coherence defect. **The reviewer recommended the commit; the call to make it here
  rather than raise a row is this seat's.**
- **R107-R112 raised** rather than left in the two git-ignored files. Commits `6efc032`, `ce16fa5`,
  `bc6c5cc`, each carrying its measurement in the message.
- **R109's four faces were NOT fixed.** Out of scope for a close; the row states why one shared
  `split_pointer()` is the fix and why closing them face by face is the trap.
- **The corpus leg at the final head was judged unnecessary.** It is green at `6efc032`; the three
  commits since touch only comments, `tests/`, `vocab/` comments and `docs/`, and no `src/` has
  changed since `170be91`. **This is a judgment, not a measurement** — see below.
- **Nothing is pushed and no merge was performed.**

## Unverified or assumed

- **The corpus leg has not run at `bc6c5cc`** (green at `6efc032`: 43 passed, 19m45s). Reasoning
  above; if you want it strict, run it — the worktree recipe is in the previous handoff.
- **The non-corpus leg at `ce16fa5` was launched and its result is not in this file.** It is green at
  `6efc032` (1235 passed / 7 skipped / 1 xfailed / 10 warnings, 20m34s — the first run covering both
  Tasks 6-8 *and* the corpus leg since `170be91`). The four modules that read the register were re-run
  green after every subsequent commit (50 + 33 + 17 passed).
- **The review's minor triage is not independently re-measured.** This seat re-measured B1, R107,
  R108 and all four faces of R109 itself; the remaining ~28 DEFER / ~13 VOID verdicts rest on the
  reviewer's own measurements, which are quoted inline in its report — **and that report is
  git-ignored**.
- **`holon:03` would be false-refused by a literal M11** (R106's remedy): it is an
  *existence-of-shape* claim citing the shape file, which has 0 focus nodes by construction. Carry
  this into M11's design; it is recorded nowhere tracked except here.
- **Two decisions are the maintainer's and neither is recorded anywhere as taken:** R108's
  error-vs-warning policy, and **I-1** — `.claude/settings.local.json` composes the context gauge with
  cockpit, so the live strip is **three rows and nobody has seen it rendered**. The fallback (compact
  single line, fractions behind `--verbose`, never abbreviated rung names) exists only in a test
  docstring.
- **"Exactly 10 warnings" is data-dependent** — 8 rdflib + 2 doc-governance queue warnings, so it
  becomes 8 when a release drains the wiki promotion queue. A future leg reporting 8 is not a
  regression.

## The next concrete action

`superpowers:finishing-a-development-branch` — the merge/push decision, which is the maintainer's.
