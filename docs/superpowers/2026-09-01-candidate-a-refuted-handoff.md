# Handoff — candidate A refuted, candidate D refuted, and the corpus is the remaining suspect

**Topic:** the progress-census menu. Two of its four candidates are now closed by measurement; the
successor finding is `R158`.

**This handoff's part 5 was written FIRST, at 39,084 working tokens — under the 50K originating
floor**, per `CLAUDE.md` § "The handoff's next action is TYPED". Parts 1–4 were appended after.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

**Re-derive the two committed figures before building anything on them.** Both are measurements this
session took and neither is pinned by a test:

- the cost table in `2026-09-01-cost-per-loop-measurement.md` — the script is described in that file
  and the corpus is outside the repo, so it will have grown;
- the 8-of-9 bucket counts in `2026-09-01-candidate-a-refuted.md` — 2 of its 11 classifications were
  re-verified here, 9 were not.

This is cheap and it is the honest first move; neither file claims otherwise.

### PROPOSED — R158's framing is a REFRAMING, not a measurement, and it must be run before it is built on

`R158` asserts that five register rows and two loop findings are *"five framings of one fact — the
corpus does not enter the code under test."* **That is exactly the kind of claim this session was
too invested in to grade itself**, and R158's own row says building the reach instrument before
establishing it would be the expensive wrong remedy `R157` warns about.

**The falsifiable form, to be RUN, not assumed:** take the changed function from each of the last ~6
`src/`-touching loops and count, per corpus document, how many times it executes on a full compile.

> **Prediction: most changed functions are reached by 3 or fewer of the 7 documents.**
> **If refuted** — if most changed functions execute on most documents — **R158 collapses**, R45 and
> #109 were two unlucky narrow changes rather than a corpus property, and the menu reduces to B and C
> with nothing new added.

**Cost matters here and is why this is proposed rather than planned:** a full DOCUMENT-scope battery
is minutes per document (`R157`'s row), so 6 functions × 7 documents is not a cheap probe, and
whoever runs it should first check whether one instrumented compile per document can count all six
functions in a single pass. **Measure that before scoping the run.**

### What is NOT recommended, with the reason recorded

- **A's remedy — extending plan-rule 4 to the negative half — should not be adopted.** 89% of loops
  already do it unprompted, and `plans/2026-08-17-the-gate-and-the-label.md:256` did it in August
  without a rule. See `2026-09-01-candidate-a-refuted.md` § "Why the remedy is not adopted".
- **Candidate D is closed** by `2026-09-01-cost-per-loop-measurement.md`. Do not re-open it on the
  "12 of 20 loops changed nothing" figure alone; that figure was always compatible with D, and cost
  is what settled it.

---

## 1. Goal

Run candidate A's own falsification before building A's remedy, and measure the cost denominator the
progress census made every other candidate conditional on.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-09-01-cost-per-loop-measurement.md` | The cost figures, the instrument, and why D falls. Its § "Unverified" lists what the numbers do not support |
| `docs/superpowers/2026-09-01-candidate-a-refuted.md` | The 11-loop census, the two claims re-verified by hand, and why A's remedy is declined |
| `docs/superpowers/residues-open.md` `R158` | The successor finding and what would close it |
| `docs/superpowers/2026-09-01-progress-census-handoff.md` | The menu this loop consumed. **B and C are untouched and still stand** |
| `specs/2026-08-31-a-header-level-is-a-band-line-design.md:143-170` | The only reach probe this repo has ever written, and it is prose in a spec — not a tool |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| Candidate D refuted — loops are expensive, median 122,419 working tokens | `2026-09-01-cost-per-loop-measurement.md`, commit `f1d512a` |
| Candidate A refuted — 8 of 9 loops carried power evidence | `2026-09-01-candidate-a-refuted.md`, commit `24b3005` |
| A's rule change declined | same file, § "Why the remedy is not adopted" — **nowhere else**, so it is reversible, not settled |
| Corpus reach raised as a property, not per-feature rows | `R158`, index + `residues-open.md` |
| Candidate A was chosen over B, C and a cost-cutting loop | **the conversation only.** The maintainer picked A from a four-way question; that choice is not recorded in any file, and A is now dead |

## 4. Unverified or assumed

- **9 of the census's 11 classifications were not re-verified.** The refutation rests on the 2 that
  were. Attacking the other 9 is how the refutation gets overturned.
- **"POWERED" is documentary**, recording that a loop published reach or ablation evidence — not that
  the evidence was re-run. No corpus battery was run for the census.
- **`R158`'s premise is unmeasured**, by its own row. Part 5 turns on it.
- **The cost figures are peak-minus-baseline**, one defensible choice among several, chosen because
  it is what the gate measures. The session-to-production-code attribution (802K vs 1.83M) is
  timestamp containment and is directional only.
- **The 11-loop and 19-session windows are both ~2 weeks and neither was compared to an earlier
  period.** The progress census carried the same caveat and it is not discharged.
- **Nothing in this loop touched `src/`.** It is a diagnosis loop, and by the cost measurement's own
  finding that makes it one of the sessions that spends tokens without moving the compiler — a fact
  worth carrying, not hiding.
