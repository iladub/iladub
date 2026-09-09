# Handoff — the fifteen are classified: 329 fires, 2 findings, and R192 is fully counted

**Topic:** action **5a** of `docs/superpowers/2026-09-09-first-observation-is-recoverable-handoff.md`,
graded ASSERTED, is taken. [[R192]]'s census is now completely classified. No code shipped and none
was needed.

**Written 2026-09-09**, part 5 first.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — nothing about [[R192]] remains to measure; do not re-open it

The row is finished as a counting exercise. 329 undated Evidence occurrences, 48 superseded under
`readAt`, 63 under first observation, 15 movers, 6 excluded by R192's own filename filter, 9 hand-read,
**2 findings**. Every arm has been ruled and every number has been taken.

**What a future loop must NOT do:** re-run the census hoping for a different verdict, or propose arm (1)
again on the ground that "2 is not 0". 2 of 329 is a 99.4% false-positive rate, and the append-only
ground refutes the gate independently of any hit rate. If someone wants to argue for gating Evidence,
the argument has to be about `5743af3` and repairability, not about the count.

**Why asserted:** the outcome is on disk and reproducible in ~40s (§2 gives the script's shape).

### 5b. RUN, and it settles: [[R199]](a)'s gated population is ONE occurrence, and it is a mention

This was drafted PROPOSED — a prediction that must be run and can fail. **It was run in the same
session, because the cheap check it named is a single `sed`, and reading is ungated.**

R199(a) — truncation is not rounding, so `0.9654` denotes nothing — is deferred on *"the population
of true findings is zero"*, and that zero was measured at `9716755` by the same instrument family
this loop just showed to be date-blind. But the dating defect cannot touch it: truncation is a
**matching** question, not a currency one. And §6's ruling leaves Evidence ungated, so of R199(a)'s
22 truncated occurrences (21 `evidence`, 1 `code`) the gated population is **one**:

```
tests/etkl/test_adoption_document.py:371
    BOTH are pinned (final review m1). `> 0.0606…` alone lets the headline measurement regress
```

**MEASURED: it is a mention of a pin's threshold, and R199's row was right from reading.** The
sentence is about what the test asserts, not about what the corpus reads; and the full-precision
value with its date sits two lines above it in the same docstring (`:369`, *"Measured 2026-08-09:
0.06068601583113457 before this loop"*), so even a truncation arm with its own separating precision
would find the block dated and pass it.

**R199(a) therefore stays open as a MEASURED refusal, not an asserted one** — the same grade as
[[R200]]. Its close criterion is unchanged and unmet: it closes when a truncated quotation is
measured **in a gated class**, and today there is one candidate and it is not a claim.

### 5b-next. UNDECIDED — the next loop's subject is deliberately not named here

The three figure-gate residues are now all measured refusals ([[R192]] arm 1 at 329/2, [[R199]](a) at
1/0, [[R200]] at 7/0), so the obvious successor queue is empty and choosing the next subject is
**originating work**. This session is at **1.8× the originating floor** and will not do it from here;
naming a loop badly is exactly the [[R151]] failure this format's part-5 typing exists to prevent.

**What a fresh session should do first:** read `docs/superpowers/residues.md` in full — it is the
index and it is ~2.8k tokens — and pick from what is open, rather than inheriting a subject invented
by a tired session. [[R199]](b) is explicitly *not closable* and must not be picked.

### 5c. ASSERTED — [[R200]] and [[R199]](b) stay unbuilt, and their rows are the record of why

Unchanged from the predecessor handoff's 5b. A date-correctness gate measures 7 fires / 0 findings;
an unregistered figure is invisible to any register-based gate by construction and that is the register
being right, not a defect. **If a future loop proposes closing R200 by widening the accepted date set,
refuse it** — that moves the denominator and finds nothing.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the classification, and every measurement | `docs/superpowers/2026-09-09-the-fifteen-classified.md` | §1 the 15 reproduced and why the denominator is 329; §2 the 6/9 arithmetic correction; **§3 the exculpation criterion and where it is derived from** — read this before disputing any verdict; §4 the nine in a table; §5 the two findings and the `data-grid.md` misdirection; §5.1 the steelman; §6 what it does to the ruling |
| the finished row | [[R192]] in `residues-open.md` | the full amendment. **The index line in `residues.md` is a pointer and still carries the superseded "10 of the 15 stay unclassified" text ahead of the correction** — open the row |
| the two findings themselves | `2026-09-08-after-the-two-counts-handoff.md:76`, `2026-09-08-two-loops-handoff.md:77` | that each accounts for the capability line figure by figure and assigns `apple 0.6289` no status |
| the figure that was already known | `2026-09-07-r176-handoff.md:113`, `tests/etkl/test_adoption_document.py:380` | `0.71875` entered `main` on 2026-09-07, a day before both findings were written |
| the dating primitive | `scripts/first_seen.py` | unchanged this loop; it is what makes §1 reproducible |

## 2. What changed

One branch, `r192-the-fifteen-classified`, off `d0db4ac`. **No code, no vocabulary, no tests.**

- **New:** `docs/superpowers/2026-09-09-the-fifteen-classified.md`, this handoff.
- **Register:** [[R192]] amended in place in `residues-open.md` (full) and `residues.md` (short pointer).
- **NOT modified, deliberately:** `docs/superpowers/specs/2026-09-09-first-observation-is-recoverable-design.md`.
  Its §4 says "5 of the 15" and "the other 10", both off by one. It is Evidence introduced after
  `5743af3` and [[R186]]'s rule forbids modifying an existing line, so the correction lives in a new
  document and in the register. **This is the first time that rule has bound a correction in this repo**,
  and it cost nothing: a reader lands on the row, not the stale sentence.
- **A NULL CONTROL was run** and is recorded in the loop record §1: the identical script with
  `cor:readAt` on both sides scores **0 movers**. The 15 are produced by the dating change and nothing
  else. §1 also carries the one-step-on figure (338/88 with this loop's own documents tracked, movers
  still 15).
- **The census instrument is scratch code again, and stays uncommitted** — same reasoning as both prior
  loops. It is ~60 lines over `tests/docgov_extract.extract` + `scripts/first_seen.first_seen`; §1 of the
  loop record states its five steps precisely enough to rewrite.

## 3. What was decided, and where that decision is recorded

- **The exculpation criterion is figure-specific, not block-specific.** Loop record §3. Ground: all three
  of R192's own published exculpations name the specific figure; none is a blanket caution over a block.
  §5.1 states the losing reading and what it would have scored (0 instead of 2).
- **Arm (3) stands, now on both grounds.** Loop record §6. The hit-rate ground, withdrawn as uncomputed
  by the predecessor loop, returns at 2/329 and points the same way as the append-only ground.
- **The two findings are not repaired.** Loop record §7. Ground: Evidence is append-only; this document
  is the repair the rule permits.
- **The predecessor spec is not corrected in place.** §2 above.

## 4. Unverified or assumed

- **The full suite has NOT been run in this session.** `tests/test_doc_governance.py` (7 passed, 35s),
  `tests/test_first_seen.py` and `tests/test_source_ownership.py` (11 passed, 12s) were run and are the
  only tests any of this change could touch — the diff is three markdown files. **CI is the check.**
- **`0.71875` is apple's DOCUMENT score, verified, not assumed.** `specs/2026-09-08-a-figure-carries-its-date-design.md:120`
  measures it at `9eb5cd0` beside `0.6288659793814433` as the last recorded reading, and its §1.4 table
  calls `apple 0.6289` *"superseded, newly measured here"*. The supersession relation the census uses is
  therefore the same one the R187 spec asserts by hand.
- **The 6-vs-5 count is measured at `d0db4ac`, and `4b886a9` is inferred to agree.** `d0db4ac` touched
  only `scripts/first_seen.py` (`git show --stat`), so no Evidence line moved between them. The two
  commits were not both run.
- **Method parity with R192's census remains INFERRED**, exactly as the predecessor handoff recorded —
  its instrument was never committed. The denominator reconciles exactly at each step (326 → 328 → 329,
  each gap being the loop record a census could not see), which is strong evidence and is not the same
  as running both instruments side by side.
- **The two findings turn on a reading of English**, and §5.1 says so rather than hiding it. A reviewer
  who reads *"part-stale"* in a heading as exculpating the whole block gets 0 findings. Nothing
  downstream turns on 0 versus 2 — §6's ruling is identical either way — which is why this was recorded
  as a fork rather than argued to a single number.
- **`cor:recordedIn` for `0.71875` names one of three sites in the tree.** Noted in §5 as the mechanism,
  not raised as a residue: the property's own definition (`vocab/internal/corpus.ttl:229`) calls it *"the
  provenance of the ROW, not of the measurement"*, so it is not contracted to be exhaustive, and
  [[R198]]'s closure already supplies the derived answer.
