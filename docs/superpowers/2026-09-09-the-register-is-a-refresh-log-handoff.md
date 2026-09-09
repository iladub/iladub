# Handoff — R192's census is run: 326 fires, 0 findings, and the register cannot answer the question

**Topic:** action **5a** of `docs/superpowers/2026-09-09-a-claim-lives-in-prose-handoff.md`, graded
ASSERTED, is taken. A **RULING loop — no code ships.** [[R192]] amended: all three arms refuted or
unnecessary, arm (3) taken. [[R198]] and [[R199]] raised.

**Written 2026-09-09**, part 5 first.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. PROPOSED — that [[R198]] is the next loop, and that it is a REGISTER design question, not a field edit

`cor:readAt` records when the corpus register was refreshed, not when a figure was read: 7 distinct
days for 95 figure-bearing documents across six weeks, and **109 occurrences in 43 documents state a
reading whose registered `readAt` post-dates the document**. Until that is repaired, every
date-based judgement about where a figure came from is under-determined — including the one this
loop just made, whose zero is a **lower bound** for exactly this reason.

**Why proposed and not asserted:** the shape of the repair is a guess. The candidate is per-reading
provenance — the commit at which a value was first observed, with `readAt` re-derived from it — and
that is a redesign of `tests/corpus-manifest.ttl` and of `load_readings`, touching the shipped wiki
and code gates. **It fails cheaply if attempted in the right order:** before designing anything, ask
whether the first-observation commit is *recoverable* for the 18 existing readings, or only for
readings taken from here on. If it is only recoverable going forward, the repair cannot validate
itself against the 109 occurrences that motivated it, and the honest loop is a much smaller one —
record provenance for NEW readings and leave the existing rows marked as refresh-dated.

**Do not start it in the same session as anything else.** It is the first change in this area that
touches a HARD gate's inputs.

### 5b. ASSERTED — [[R199]](a) stays unfixed until a truncated quotation is measured in a gated class

Nothing to run. The row carries the number that would change the decision (currently 0 in
`docs/wiki/**`, and the one `code` instance is a mention), and the cost that makes it non-trivial
(truncation is ambiguous at 4 decimals where rounding is unique, so it needs its own separating
precision at 5). **A loop that "fixes" it without that second precision has widened the matching
rule and broken the uniqueness the whole gate rests on.**

### 5c. ASSERTED — [[R199]](b) is not a defect and must not be filed as one

`bfs 0.9401` is invisible because it was never a reading of any commit on main. Refusing to register
it is the register being right. The lesson is a limit to state, not a bug to fix: **the figures most
likely to be wrong are the ones no register will ever carry.** If a future loop proposes registering
"the figures people quote" to close the gap, that is the proposal to refuse.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the census and the ruling | `docs/superpowers/2026-09-09-the-register-is-a-refresh-log.md` | §1 the four disjoint dating classes and the 326/0; §2 the two blind spots; §3 the refresh-log proof; §4 the ruling on all three arms |
| the amended row | [[R192]] in `residues-open.md` | that its harm was real and its CLASS was wrong, and that §1's zero is a lower bound |
| the new rows | [[R198]], [[R199]] in `residues-open.md` | R198's "what would NOT close it"; R199's split into a closable (a) and an unclosable (b) |
| what a gate would fire on | `vocab/queries/docgov-undated-figure.rq` | the `FILTER (?class != "evidence")` this loop declines to remove, and why |

## 2. What changed

One branch, `r192-the-figure-a-handoff-did-not-measure`, off `9716755`. **No source, no shapes, no
queries, no tests** — three markdown files and the register.

- **New:** the loop record; this handoff; [[R198]] and [[R199]] in both register files.
- **Amended:** [[R192]]'s row and index line — not closed, answered.

## 3. What was decided, and where that decision is recorded

- **Arm (3) — leave Evidence ungated — is TAKEN.** Loop record §4, R192's amended row. Ground: 326
  fires, 0 findings, and the gate would be unrepairable by construction under the append-only rule.
- **Arm (2) is unnecessary, not merely unenforceable.** Same. Ground: the class measures zero, and
  the motivating figure was never a register row to restate.
- **The truncation blind spot is NOT fixed.** [[R199]]'s row. Ground: 0 in wiki, 1 in code and that
  a mention; and the fix needs a second separating precision.
- **`cor:readAt` is not repaired here.** [[R198]]'s row. Ground: it is a register redesign.

## 4. Unverified or assumed

- **No test was run in this loop and none was written.** The suite is untouched; the only executable
  claim is the register-integrity test, which passes. **CI is the check that has not run yet.**
- **The census instrument is scratch code, not committed.** It lives only in this session's
  scratchpad. Every number in the loop record is reproducible from the shipped extractor functions
  plus the criteria stated there, but **nothing in the repo re-derives them**, and a future loop
  wanting to re-measure must rewrite it. Deliberate — committing a one-off census as a test would
  make it a gate nobody chose.
- **The hand classification of the residual 3 is a judgement.** Each was read in its file; each
  names its own staleness in the same sentence. A reader who counts a before/after table column as a
  restatement would score 326 fires / 1 finding rather than / 0. The ruling does not turn on it.
- **The 45 "subject is the stale figure" occurrences were excluded by FILENAME pattern**, not by
  reading each one: five document names matched. That is a coarse filter and it is stated as one;
  the 3 residuals were then read individually.
- **`superseded_at` uses a STRICT inequality** on the document's own date, which excludes same-day
  supersession. That choice was made after hand-checking flagged `2026-08-31-who-tree-refutation`
  — a document that measured the improvement on the day it was written. Without it the count is 95
  in 28 documents rather than 48 in 10; the residual 3 is unchanged either way.
- **The 109 "reading taken after the document" occurrences were not individually read.** Four were
  spot-checked and every one is a document reporting its own contemporaneous measurement. The
  inference that `readAt` is a refresh log rests on those four plus the arithmetic of 7 days against
  six weeks.
