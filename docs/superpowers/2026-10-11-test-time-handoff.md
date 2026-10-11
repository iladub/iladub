# Handoff: where CI's 22 minutes go (R307) (2026-10-11)

**Serves:** maintenance — R307, raised 2026-10-11 at the maintainer's request.

**Topic:** test time · **Date:** 2026-10-11

Written at about 73K working tokens, over the 50K originating floor. Part 5 was written first and
is graded per action for that reason. Nothing below was designed here; the remedy is the next
session's to choose from a measurement this one did not take.

## 5. The next concrete action, typed

1. **ASSERTED: take the per-file duration table before anything else.** Add `--durations=0
   --durations-min=1.0` to one run (`.github/workflows/ci.yml:26`, or the same command locally)
   and sum by file. The outcome is a table; producing it is the work. Locally the suite is
   memory-fragile in one process (three kills on record, see § 4), so if it is run locally it is
   run one file per process and the per-file wall times are the table.
2. **PROPOSED: most of the time is a small set of files that compile a synthetic PDF per test.**
   Basis: four files timed on 2026-10-11 (R307's row). If the table shows this, the remedy is to
   compile each fixture once per module or session where the tests only read the result. If the
   time is spread evenly across 246 files, that remedy buys little and this proposal is refuted.
   The table answers it in one run.
3. **PROPOSED, and it depends on 2: sharding.** Split the suite across parallel jobs. It is not
   the first move, because it multiplies runner minutes without removing work, and because of the
   two constraints in § 2. Whether 2 or 3 or both is unmeasured.
4. **PROPOSED, low confidence: `pytest-xdist` inside the one job.** GitHub's standard runner has
   few cores and the compiles are memory-heavy. Unmeasured on the runner; the local memory kills
   are the only evidence and they are from full-corpus compiles, not the CI suite.

## 1. Goal

Bring the `test` check's wall time down by a stated amount, with the same tests collected.

## 2. Where the primaries are

- **The row:** `docs/superpowers/residues-open.md`, R307. Every figure in this file is there with
  its command.
- **The workflow:** `.github/workflows/ci.yml`. Establish there: the single job is named `test`,
  the pytest step is `pytest -q`, and `concurrency.cancel-in-progress` is set.
- **The constraint on parallel jobs:** `CLAUDE.md` § Branch protection. The required status check
  is the JOB name `test`, bound to `integration_id: 15368`. A matrix renames its jobs, so it needs
  one aggregating job that keeps the name `test`, or every PR blocks on a check that never
  arrives. Verify with `gh api repos/iladub/iladub/rules/branches/main`, never the branches
  endpoint.
- **What R305 did and did not do:** `docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md`.
  It is about the local corpus pass. The corpus never reaches CI.
- **The run measured:** `gh run view 38144033419 --json jobs`.

## 3. What was decided, and where it is recorded

Nothing was decided. The maintainer asked for the row and this handoff; the row is the record.

## 4. Unverified, assumed, or found on the way

- **No per-test timing was taken.** The four per-file figures in the row are local, on one
  machine, each file in its own process, and say nothing about the other 242 files.
- **The 189 skipped tests were not classified.** Most are presumably corpus-gated; not counted.
- **Whether fixtures can be shared is unread.** Many tests monkeypatch the driver or pass
  different fixture arguments; a compile cached across tests that mutate the report or graph
  would be a correctness defect, not a speed-up. Read before caching.
- **`CLAUDE.md` says "~14-minute CI"** in § Branch protection, where it weighs `strict: false`.
  The last eight green runs are 17 to 23 minutes. That file is Contract class and is edited only
  on explicit request; it was not edited.
- **Runner core count and memory were not read.**
- This branch was first stacked on PR #335 and rebased onto `main` after it merged (`7bb7798`).
