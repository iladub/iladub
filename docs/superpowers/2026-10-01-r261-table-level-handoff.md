# Handoff: R261 table level shipped — the grand total is loop (b) (2026-10-01)

**Topic:** r261-totals-family · **Date:** 2026-10-01

**Serves:** prog:criterion:etkl:03 — the table level of the R261 totals family shipped; the criterion stays unmet.

**Doc impact: none.**

Authored at about 115K working tokens: below the executing floor (150K), above the originating
floor (50K). Per CLAUDE.md § "The handoff's next action is TYPED", part 5 was written first and each
action is graded.

## 5. Next actions (written first)

- **Asserted — mechanical, and comes first if the controller session ended before it.** The final
  whole-branch review returned *"with fixes"*: two Important findings (I1 `tab:totalOf` claims an
  `sh:class` it lacks — ruling R9 adds it, without `sh:minCount`; I2 `printedtotal.listing_of` omits
  candidate-band lines 0..k-1) plus triaged minors and two new register rows. The full list is in
  the ledger `progress.md` under "Final fix wave"; the fixer reports to `final-fix-report.md` there.
  **Update at session end: the fix commit EXISTS — `0981cd3`** (R284, R285 raised; item 5's
  span-donation refusal case was not constructible synthetically and is folded into R284; R283's
  script moved to `scripts/r261_task6_sweep.py`). The scoped re-review over `9f6fdeb..0981cd3` has
  NOT been run. So: run ONE scoped re-review over it
  (`re-review-prompt.md`), then `superpowers:finishing-a-development-branch`. If it shows nothing and
  the tree is dirty, the fixer died mid-wave: read `git diff` and re-dispatch one fixer with the same
  list. **Before the PR:** delete repo-root `scratchpad/` (untracked; R283's script is meant to move
  to `scripts/` first) and commit this handoff.
- **Asserted — the outcome is known; doing it is the work.** The maintainer reviews and merges the
  `r261-totals` PR. That branch was cut from `r261-totals-plan` (PR #289, the plan, still open), so
  it carries the plan commit too. Merge #289 first, or let the `r261-totals` PR carry it and close
  #289 as superseded. That choice is the maintainer's; nothing else depends on it.
- **Proposed — loop (b): re-spec the grand total.** The maintainer chose "(a) then (b)" on
  2026-10-01. This document records that choice; the session's ledger does too, but the ledger is
  gitignored. **The prediction is unmade.** P3 refuted one closed question at one crop (evidence
  § 6, n = 1 grand total and 4 nulls, × 3). It did **not** show that no oracle can dispose a total
  of totals. The fresh session starts `superpowers:brainstorming` at *"what proposes, what disposes,
  and are they independent"* for `1,951,264`. The first thing it does is **run** whatever new
  question it proposes against the same 1 + 4 population before writing a spec. If that run fails,
  the grand total is a ruling the maintainer has to make, not a loop. Grade: proposed. A session
  that builds on it before the run will be ambushed.

## 1. Goal

Ship the table level of the R261 totals family. A printed number binds as a table's total only when
a NEURAL worker says yes AND exact Decimal arithmetic holds (R47's fork, ruled 2026-10-01).

## 2. Where the primaries are

- **Branch `r261-totals`.** Tasks 0–7 are in `git log main..r261-totals`, and Task 8 is the PR.
- **Plan:** `docs/superpowers/plans/2026-10-01-r261-totals-family.md`.
- **Spec:** `docs/superpowers/specs/2026-10-01-r261-totals-family-design.md`.
  - **Stale on two points under P3:** § 5.4's furnish-pin 1→0 prediction (the pin did not move), and
    the totals-level parts of §§ 2–3.
- **Evidence:** `docs/superpowers/2026-10-01-r261-totals-family-evidence.md`.
  - § 6: P3.
  - § 7: the corpus sweep. Only cbh moved, 0.9103232534 → 0.9106957425 and 13427 → 13624 triples;
    the other 6 documents are byte-identical.
- **Code:**
  - `src/iladub/etkl/totals.py` (PROCEDURAL; `match_totals` is unwired);
  - `src/iladub/etkl/printedtotal.py` (the NEURAL worker, reader, cache and D7 crop);
  - `baml_src/printed_total.baml`;
  - `compile.py` (the binding at band dispatch);
  - `document.py` (R7: section-repair adoption of bound totals);
  - `holon.py` (`emit_printed_total`).
- **Readings:** `readings/printed_total/*.json`. Four entries, all `yes`.
- **Register:** R261 (amended), R47, R77, and the rows Task 7 raised. See `residues.md`.

## 3. Decided, and where recorded

- **Fork (a) then (b):** the maintainer, 2026-10-01. Recorded here and in the ledger.
- **Controller rulings R0–R7:** recorded only in the gitignored ledger
  `.superpowers/sdd/2026-10-01-r261-totals-family/progress.md` and in the PR body, so they are
  reversible. The load-bearing one:
  - **R7:** the spec never measured section repair. cbh's tables assert only in pass 2, and pass-2
    PrintedTotals were being discarded. When repair adopts a table, it now also adopts every pass-2
    band whose PrintedTotal is `tab:totalOf` that table, keyed by the graph link and never by
    adjacency.
  - **R4:** table level only. No totals-level BAML function ships, because its wording was refuted.
- **cbh stays held:** a hold-note adjudication in `tests/corpus-manifest.ttl` (Task 7).

## 4. Unverified or assumed

- **"Worker says no" and "two equal-sum columns" are pinned only synthetically.** The corpus never
  exercises either.
- **The disjointness control is vacuous:** the corpus carries 0 `tab:SectionTotal`.
- **Deferred minors from the task reviews** are in the ledger and the PR body. One is a latent
  `IndexError` if a carved-to-empty band is ever chosen as a span or donation donor, at
  `compile.py` around `donor_ev`; its reachability was never measured.
- **Reader gates fall silently offline** if `baml_client` cannot be imported (register row). Any
  live run must use `PYTHONPATH="$PWD"`.
