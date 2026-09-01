# Handoff — the progress census: 20 loops, 7 days, one compiler improvement

**Topic:** not a residue. The maintainer raised a concern on 2026-09-01 — *"we are not making
progress and I am now very concerned"* — and this handoff is the **measurement** of that concern, not
its diagnosis. Two censuses were run: the loop-by-loop record of the last 20 merged PRs, and the
corpus-score time series over the whole recorded history.

**The concern is CORRECT, and sharper than it was stated.** Instrument and governance work is moving;
the thing that reads documents moved once in twelve days.

**This handoff was authored at ~165K working tokens — 3.3× the originating floor and past the
executing floor.** Per `CLAUDE.md` § "The handoff's next action is TYPED", part 5 is graded per
action, and the grading is load-bearing here: **the whole of part 5 is PROPOSED.** Parts 1–4 are
pointers and measurements and do not degrade.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### PROPOSED — everything in this section. Nothing here is a plan; it is a menu with a required first measurement.

**Do not start by choosing a remedy.** Four candidate diagnoses are listed below; they are not
ranked, and the ranking is exactly the originating judgement this session was too deep to make
honestly. A fresh session must pick, and picking requires one thing that was NOT measured.

**WHAT MUST BE RUN FIRST — the missing denominator.** Every figure in §3 counts *loops* and *scores*.
Nobody has measured **cost**: how much of a session each loop consumed. Without it, "20 loops in 7
days produced one compiler improvement" cannot be read — 20 cheap loops with one win is a healthy
exploration rate, and 20 expensive ones is the problem the maintainer is describing. `plimslop`'s
corpus holds per-turn token records for this project (`plimslop reader override`; the audit in
`R141` reads it). **Measure cost-per-loop before ranking any remedy below.** If the loops are cheap,
candidate D is the answer and A–C are premature.

#### Candidate A — oracle POWER is the failure mode, not spec/plan/implementation

Two independent instances in three days, both of which passed every check the process requires:

- **R45 (PR #145, 2026-08-31)** — its corpus oracle was **low power**. A reach probe counted the
  changed function's calls: gstem 0 · gcap 0 · bfs 0 · ons 0 · cbh 0 · apple 2 · who 3. **Five of six
  "unchanged, therefore safe" rows were vacuous.** Recorded in `residues-closed.md` `~~R45~~`.
- **R155 (PR #147, 2026-09-01)** — its oracle was **scoped narrower than the rule**: page 0, for a
  rule that runs on every page. It reported "byte-identical by construction" while bfs page 6 was
  going 324 → 53 cells. Recorded as `R157`.

Both loops followed spec discipline, TDD, and falsification, and both produced a confident wrong
answer. **If this is the diagnosis, the remedy is upstream of the plan rules: an oracle must be shown
to have POWER — to fire when the change is ablated — before it is trusted to say "nothing regressed".**
That is `CLAUDE.md` plan-rule 4 (falsification) applied to the *negative* half of an oracle, which it
currently does not cover: rule 4 proves the new test pins its subject, and says nothing about whether
the "nothing else moved" evidence could have detected movement.

**What would falsify A:** census the last ~10 loops' negative oracles for power. If most were
adequate, two instances is a coincidence, not a pattern.

#### Candidate B — five of seven documents have no target

Only **gstem** carried an accepted verdict and score floor (0.95) for most of this history; **who**
was accepted at 0.90 on 2026-08-31. The other five are `cor:Unadjudicated` / HOLD. **For most of the
corpus there is no defined target to make progress toward**, which makes "are we progressing" formally
unanswerable for those documents and makes every score movement arguable after the fact.

#### Candidate C — the metric changed under the series

**On 2026-08-08 (closing R72) the score's semantics changed**: before it, a zero denominator scored
1.0 unconditionally, and **11 of 27 pages scored a degenerate 1.0** — including two real tables that
produced zero cells. `specs/2026-08-08-data-grid-types-elements-axioms.md:1105-1146` warns in its own
words that readers "need to know which of the two they are looking at." **cbh's +0.839 and ons's
+0.530 — the two largest gains in the record — straddle that change and have never been re-baselined.**
The historical series in §3 may therefore overstate how much was ever gained.

#### Candidate D — nothing is wrong except the accounting

12 of 20 loops changed neither code nor tests, but many are legitimately handoffs, register passes and
CLAUDE.md rulings — one commit each, by the branch-protection rule. **Commit granularity is not
session count.** 10 of the 16 closures in the window were *pre-existing* debt, and the tally trend
went from flat-at-20% (46 rows) to 27.9% in the last 16 rows. On that reading the recent period is the
*healthiest* in the register's history and the corpus is simply hard. **This candidate is why the cost
measurement must come first.**

---

## 1. Goal

Answer, with instruments rather than opinion: *is this project making progress?* — and leave the
diagnosis to a session able to author it.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| §3 below | The two censuses. These are the measurements; everything else is pointing at them |
| `docs/superpowers/2026-09-01-marked-content-is-not-a-label-handoff.md` | The loop that triggered the concern; its §5 has the R155/R157 detail |
| `residues-open.md` `R157` | The oracle-scope finding, candidate A's second instance |
| `residues-closed.md` `~~R45~~` | The low-power-oracle finding, candidate A's first instance |
| `specs/2026-08-08-data-grid-types-elements-axioms.md:1105-1146` | Candidate C — the metric change, in the file that made it |
| `plimslop reader override` | The cost corpus part 5 requires. **Not yet queried for this question** |

## 3. The measurements

### 3.1 Loop record — 20 merged PRs, 2026-08-26 → 2026-09-01

| metric | value |
| --- | --- |
| changed production code (`src/`+`vocab/`+`scripts/`) | **7 / 20** |
| changed tests | 7 / 20 (not the same seven) |
| changed neither | **12 / 20 (60%)** |
| net production lines | +1,256 |
| residues closed : opened | **16 : 18 = 0.89** |
| of the 16 closures, raised inside this window | 6 — the other **10 were pre-existing debt** |
| register, window start → head | 129 rows / 25 closed (19.4%) → **147 / 41 (27.9%)** |

**Tally trend, all `(N/M closed)` snapshots R95 → R157:** flat in a 19.1–21.6% band for 46 rows
(R95 = 17/85 ≈ R141 = 25/130), then rising steeply over the last 16 rows to 27.9%.

`scripts/` was touched by none of the 20.

### 3.2 Corpus scores — DOCUMENT scope, whole recorded history 2026-08-04 → 2026-09-01

| doc | first | latest | delta | since the 08-20 census |
| --- | --- | --- | --- | --- |
| cbh | 0.0698 | 0.9092 | **+0.839** | +0.0045 † |
| ons | 0.4419 | 0.9720 | **+0.530** | 0 |
| who | 0.5597 | 0.9096 | **+0.350** | **+0.3499 (genuine — R45)** |
| apple | crash → 0.0106 | 0.3587 | **+0.348** | +0.0031 † |
| bfs | 0.3438 | 0.3464 | +0.0026 | +0.0026 † |
| gstem | 0.96546 | 0.96589 | +0.00043 | +0.00043 † |
| gcap | 1.0 | 1.0 | 0 | 0 |

† **flagged by the repo's own documents as a denominator effect** — welding cells removes tokens from
the denominator, so the score rises without better reading
(`2026-08-31-r154-closed-handoff.md:48-50`, `specs/2026-08-31-a-boundary-that-cuts-ink-design.md:137-139`).

**Strip the denominator effects and there is exactly ONE genuine capability gain in the twelve days
to 2026-09-01: R45.** R154's fidelity repair is real but score-neutral by design.

**No corpus score exists anywhere before 2026-08-04**, when the battery was built.

## 4. Unverified or assumed

- **Cost per loop is NOT measured.** Part 5 turns on it. This is the single largest gap.
- **The 20-loop window is 7 days and may not be representative.** No comparison was made to any
  earlier window.
- **Candidate A rests on n=2.** Two oracle failures in three days is a pattern or a coincidence and
  nothing here distinguishes them.
- **The pre/post-2026-08-08 metric discontinuity was not quantified**, only located. How much of
  cbh's +0.839 and ons's +0.530 survives a re-baseline is unknown, and re-running the 08-04 battery
  under today's metric would answer it.
- **ons's 0.4419 → 0.9720 has no recorded cause.** The 2026-08-21 errata establishes 0.9720 is the
  measured figure and that 0.4419 "appears nowhere in the measurement" — it does not say the score
  ever moved. It may be a correction, not a gain.
- **Both censuses were run by subagents** from the descriptions above, against the tracked tree at
  `4a60023`. Their commands are recorded in their reports but **the figures are not pinned by any
  test**, and re-deriving them is a fresh session's first cheap check.
- **`residues.md`'s header was 31 rows and 17 closures stale** and is corrected in this branch.
  Nothing machine-checks that line — `test_residue_register_integrity.py` pins index/detail
  correspondence, not the header's arithmetic. **Not raised as a row**, deliberately, given the
  concern is about rows opened exceeding rows closed; a fresh session may disagree.
- **PR #143 was closed unmerged**, and **five commits reached `main` outside any PR** on 2026-08-29
  (the ones that motivated the branch-protection ruling). Neither is counted in §3.1's rows.
- **R154's tally snapshot was lost in transit** between `residues-open.md` and `residues-closed.md`.
