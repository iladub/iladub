# Handoff — the ruling is now an enforcement, and two contract claims were wrong

**Topic:** branch protection applied as a ruleset, the verification recipe it invalidated, and the
loop work that is still queued behind it

**This handoff SUPERSEDES NOTHING.** `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` is
still the entry point for the *work*; this one covers only what happened after it merged. Read that
one first — its part 5 is the loop menu and is reproduced here by citation, not by restatement.

Authored at **~225,000 working tokens — 4.5× the 50,000 originating floor**, `handoff` logged as an
override. That figure is the reason part 5 below is mostly a **pointer to another document's part 5**
rather than fresh reasoning: the 2026-08-30 table was written at 1.56× and re-deriving it here would
replace better reasoning with worse. Parts 1–4 are pointers and records, which CLAUDE.md § Loop &
context hygiene says may be appended at any cost.

## 5. The next concrete action — TYPED

### ASSERTED — unchanged, and NOT re-derived here

**The loop menu is `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5.** Three mechanical
rows — `R152` (the `sh:nodeKind` guard), `R138` (spec §4.5's citations → symbols), `R137` (the
register's own integrity test) — each with its oracle. **`R137` first**, and that handoff states why.
Nothing since has changed any of it. Do not plan from this paragraph; open that table.

### ASSERTED — new, from this session

| what | oracle that must go RED first |
|---|---|
| **Guard the `test` job name.** The ruleset requires a check literally named `test`; `.github/workflows/ci.yml:11` supplies it as a JOB name. Rename that job and **every PR blocks forever on a check that never arrives** — CLAUDE.md says so in prose and nothing enforces it. A ~10-line test asserting `ci.yml` defines a job named `test`, citing the ruleset as the reason | rename the job in a scratch copy of `ci.yml` → the test fails; restore → green. It is green on arrival, so falsification is the only evidence it pins anything |

**This was drafted PROPOSED and PROMOTED after being run, which is the point of the grade.** The
prediction was *"the gap may already be covered by something in `tests/`"*. Measured before this
handoff shipped: `grep -rn "ci.yml\|workflows" tests/ --include="*.py"` returns ONE hit, a docstring
in `tests/test_arc_landscape.py:11` citing `ci.yml:26-27` for what the CI command is — not the job
name. Nothing asserts it. `grep -n "^jobs:" -A 3 .github/workflows/ci.yml` → `jobs:` / `test:` at
`:10-11`. The gap is real and the row is now mechanical.

### PROPOSED — none

Nothing else from this session rests on a prediction. The branch-protection arc closed itself:
applied, verified behaviourally, corrected twice, and the open item it left behind was deleted
because it named a rule that does not exist.

## 1. Goal (of this session, not the next)

Not a loop. PR #135 was the loop; #136 and #137 are contract records. See part 3.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` | **The real entry point.** Loop menu, measurements, and what `R131` half (b) still is |
| `CLAUDE.md` § Branch protection — every change goes through a PR | The rule, now with an APPLIED block and the corrected verification |
| `CLAUDE.md` § Open items, first entry | The measured ruleset payload and the endpoint that actually answers the question |
| PRs #135 / #136 / #137 | The loop; the application record; the correction |

## 3. What was decided, and where that decision is recorded

- **Branch protection is APPLIED, 2026-08-31, as a repository RULESET** (`main-requires-green-pr`,
  id 21898723, `enforcement: active`, `bypass_actors: null`, required check `test` bound to
  `integration_id: 15368`, `strict: false`, approvals 0). `allow_auto_merge` → `true`. Recorded in
  CLAUDE.md § Open items, PR #136.
- **It is PROVEN BEHAVIOURALLY, not only read.** PR #136 reported `mergeStateStatus: BLOCKED` while
  `test` was pending and `CLEAN` once it passed; PR #135, merged hours earlier under the same
  `.protected: true`, reported `UNSTABLE`. That contrast is the evidence. Recorded in the same entry.
- **CLAUDE.md's own verification recipe was a FALSE NEGATIVE and is corrected.** It prescribed
  `branches/main -q '.protection.required_status_checks.contexts'` → `["test"]`; under a ruleset that
  returns `[]`, so a session running the contract's own recipe would have concluded the ruling was
  never applied. Now `repos/iladub/iladub/rules/branches/main`. PR #136.
- **The explanation UNDER that correction was itself wrong, and is corrected again.** #136 blamed a
  leftover inert classic rule. There is none: `.protection.enabled` is `false`, the owner sees only
  the ruleset in the UI, and of 5 branches only `main` reports `protected`, matching
  `~DEFAULT_BRANCH`. The mechanism is that `.protected` accounts for rulesets while `.protection`
  reports classic protection only. PR #137. **The maintainer caught this, not the session** — it was
  asserted from a plausible reading of one API response rather than measured, which is plan-rule 2's
  exact failure mode.
- **Admin on this repo cannot be granted to a collaborator.** `iladub` is a **User** account, not an
  Organization, so its repos have one collaborator permission level and no role dropdown. A future
  session hitting 404 on a protection endpoint should hand the action to the owner rather than hunt
  for a permission to escalate. Recorded in CLAUDE.md § Branch protection.

## 4. Unverified or assumed

- **PR #137 was still PENDING when this was written.** Its CI had not reported. If it went red, the
  correction in part 3 bullet 4 is not on `main` and CLAUDE.md still carries the wrong mechanism.
  **Check `gh pr view 137` before trusting that bullet.**
- **The absence of a classic rule is INFERRED, not read.** `branches/main/protection` 404s for a
  non-admin token, so three agreeing signals stand in for a direct read. Stated at that strength in
  CLAUDE.md too.
- **`--auto` has never been exercised under the ruleset.** `allow_auto_merge` is `true` and the rule
  now blocks, so `gh pr merge --auto` should finally mean what it says — but every merge this session
  was done by hand after watching CI. Unproven.
- **A local suite run does not predict the `git ls-files` populations.** Measured the hard way this
  session: 1357 passed locally, then CI failed on `assert 144 == 139`, because five new `.ttl` files
  were unstaged when the suite ran. Now written into `tests/test_artifact_terms.py` and
  `tests/test_artifact_declarations.py`. **Stage before you claim green.**
- **The corpus-marked suite has not been run in full** since PR #135. Only the 7-document compile.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.
