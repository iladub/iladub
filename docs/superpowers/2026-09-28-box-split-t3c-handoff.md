# Handoff: box-split — Tasks 3b + 3c done; T1 compiles, T2's first row is the open question (2026-09-28)

**Topic:** box-split · **Date:** 2026-09-28

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Doc impact: none.** Authored at ~110K working tokens by the SDD controller: past the originating
floor, under the executing floor. Parts 1–4 are pointers. Part 5 is graded per action.

## 5. Next actions (written first)

- **Proposed, and it may fail:** T2's first row (`ALB | 1 - 15 October`) is read as a boxhead. That
  is spec § 4 risk 1, predicted and now observed. Whether a row is header or data is a reading
  judgement. Under the 2026-09-17 ruling (CLAUDE.md § 8, "one geometric attempt, then NEURAL") that
  makes it a NEURAL question, and the ons boxhead reader (PR #271: a BAML reader, an exact oracle and
  recorded readings) is the candidate to reuse. **Not measured:**
  - which code path classifies T2's row 0 as header;
  - whether the ons reader's question and oracle fit a 2-column, 8-word box band;
  - what oracle would dispose its answer.

  A fresh session MEASURES those three first, then authors spec § 10, classified under § 8, before
  any code. If no oracle can dispose the answer, the rule is "no oracle, no worker", and § 10 says so.
- **Needs a MAINTAINER choice, which may pre-empt the above:** § 8.0 says the branch does not merge
  until O2 XPASSes, and O2 is now partial: the T1 and note-block tests XPASS, and the T2 test
  XFAILs. The alternative to § 10 is to split the criterion. T1 ships compiling, and T2's
  first-row reading becomes a register row blocking a narrower criterion. That call is the
  maintainer's, not a loop's.
- **Asserted, after T2 is decided:** Task 4 Steps 4–5 of `docs/superpowers/plans/2026-09-28-box-split.md`
  flip the O2 markers and `prog:met`, and re-pin the cbh literals from measured values, once. Then
  come Tasks 5 and 6. They are deliberately not run now, so that the literals are pinned only once.

## 1. Goal

Make O2 (`tab:12`) XPASS as a whole, so the box split ships compiling, and then close the loop.

## 2. Where the primaries are

- **Spec:** `docs/superpowers/specs/2026-09-28-box-split-design.md`.
  - § 8.6 is the fusion witness over formed cells.
  - § 9 is the box band that skips the multi-table gate.
  - § 4 risk 1 is T2.
- **Commits this session:**
  - `605c413`: spec § 8.6 and § 9.
  - `221087d`, `d0f24c9`: Task 3b fix rounds 1 and 2.
  - `b8516b5`: the Topic line on the previous handoff.
  - `7263784`: Task 3c, `Band.frame` and the gate skip.
- **SDD workspace** `.superpowers/sdd/2026-09-28-box-split/`: `progress.md` (the ledger),
  `task-3b-report.md` (fix rounds 1–2), `task-3b-fix{1,2}-rereview.md`, `task-3c-report.md` (with
  the O2 diagnosis and the cbh sweep numbers), and `task-3c-review.md`. **It is gitignored, so it is
  not durable.** Part 3 copies what must survive.
- **O2's tests:** `tests/test_carriage.py`, in the `prog:criterion:tab:12` block.

## 3. What was decided, and where it is recorded

The first two are recorded in the spec, the rest in the ledger only.

- **The fusion witness judges the lines the accept path ships.** They are post-re-bucket and
  post-weld, and the band is built from those same lines. Recorded in spec § 8.6 and in the ledger
  ruling on N1 (fix round 2). The corpus flip set is still exactly `{cbh p0 T1}`, measured on both
  the `page_bands` and the `compile_document` paths.
- **A box band carries its frame and skips `is_multi_table_ambiguous`,** recording the skip as a
  `single` judgement that names the frame. `merge_bands` drops the frame. Recorded in spec § 9 and
  in the maintainer ruling in the ledger.
- **The controller dispatched § 8.6 and § 9 without a separate approval round,** because both
  implement rulings already given. Ledger only.
- **Two register rows are owed at Task 5.** Ledger only; recorded here so they survive:
  1. The witness query's cost on large witness-free bands: 30×15 takes 15.7 s and 60×20 takes
     113 s. The whole corpus costs 9.09 s in total.
  2. `weld_hrule_boxes` sends a left-edge cell to the last column on COUNT-ACCEPTED bands. It is
     pre-existing at `c68e437`. Reproducer: rules `[80,110,250,290,330]` with a two-line header ships
     `PORT TOTAL NAME`.
- **Deferred minors for the final review.** Ledger only.
  - The `relines2` post-refinement branch ships cells the witness never judged.
  - Band-global coverage lets two words with no space glyph between them, bridged by another line,
    ship concatenated.
  - The test helpers duplicate `band_chars` and the hrule filter.
  - The `_FLOAT` scan does not strip docstrings.
  - The `test_band_runs` docstring still says "9 fields".
  - The frame rationale prints float noise.
  - Cross-file `file:line` citations into `compile.py` are stale and are now shifted further.

## 4. Unverified or assumed

- **The cbh numbers after `7263784` are the implementer's run.** No reviewer re-ran them.
  - `cbh_e2e` scores 0.9103 (from 0.8738) and has 2 failures.
  - o3 is `43<54`.
  - furnish is `5==4`.
  - typing_equiv [cbh] is unchanged.
- **The local test state is red and not re-pinned.** `tests/test_carriage.py` is red locally
  because the T1 and note-block tests XPASS under strict xfail. CI skips the corpus, so CI cannot
  see it.
- **T2's diagnosis comes from the Task 3c report.** It has not been re-measured.
- **The branch is pushed to PR #284 but is not mergeable.** § 8.0 blocks it.

## Addendum — maintainer ruling (2026-09-28)

**Ruled: keep O2 whole (option 2).** The criterion is not split. The fresh session runs the first
part-5 action: MEASURE the three unmeasured facts (which path reads T2's row 0 as header; whether the
ons boxhead reader's question and oracle fit a 2-column box band; what oracle disposes the answer),
then authors spec § 10 under CLAUDE.md § 8 before any code. The "needs a MAINTAINER choice" action
above is answered and void.
