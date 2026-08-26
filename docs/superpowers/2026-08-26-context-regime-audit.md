# Audit — the context-budget regime, and whether it inherited or caused what we are finding

**Date:** 2026-08-26 · **Base:** `main` @ `a5fa232` (after PR #123) · **Shape: evidence.**

**Provenance, stated first because it is load-bearing.** The two measurement bodies below (§1, §2)
were produced by **delegated agents in separate contexts** and were **NOT independently re-run** by
the session that commissioned them. Their commands are recorded so they can be. Everything in §0
*was* verified directly in the commissioning session. **Treat §1 and §2 as measured-by-one-party,
not as this repo normally treats a measurement** — re-run before planning against any single number.

The question that prompted this: *"since plimslop we work in smaller contexts — are we now
discovering inherited issues from before, when we shipped brittle work under context rot?"*

**Answer: no, not on the rates. Yes, on the detection latency.** Both halves matter and they point
at different remedies.

---

## §0 Verified directly (commissioning session, 2026-08-26)

The `holon:05` execution phase ran on `main`, not a branch:

```
2026-08-25 12:32:44   Merge pull request #122        <- last PR of the design phase
2026-08-25 13:02:05   plan: the membrane reports its health   <- direct to main, 30 min later
```

- `git log --merges --oneline origin/main..main` → **0**. All 30 commits linear on `main`.
- Nine of the 30 are `handoff: Task N done; the fresh session starts at Task N+1`.
- Contrast PR #114 (`the-worktree-that-resolves`): **88 commits, one branch, one merge.**
- **CI on those 30 commits: `test pass` in 12m18s, `mergeStateStatus: CLEAN`** (PR #123, merged as
  `a5fa232`). The work was sound; only the routing was wrong.

Dated directly, for the five artifacts the R135 findings touch:

| finding | artifact written | vs 2026-08-09 |
|---|---|---|
| R117's dangling-subclass gap | `iladub-hga-align.ttl` **2026-06-23** | inherited |
| `risk:order` undeclared | `risk.ttl` **2026-06-26** | inherited |
| `docgov:` has no ontology | **2026-08-01** | inherited (just) |
| `escalation-furnish.rq` *names* `risk:order` | **2026-08-17** | **post-discipline** |
| `prog:` has no ontology, 9 terms | **2026-08-22** | **post-discipline** |

`risk:order` sat harmlessly undeclared from June; it became a *violation* on 2026-08-17 when a query
written under full discipline named it. **Old latency plus new work — not old brittleness alone.**

---

## §1 Dating every open residue (agent-measured; NOT re-run here)

**104 open rows: 65 pre-2026-08-09, 29 post, 10 unattributable** (declared, not forced onto a file).

**The normalisation is the whole argument.** Eras are 70 days vs 18, and the post era added 15,847
lines against the pre era's 45,389 — 2.7× the daily rate — so calendar-day normalisation penalises
the post era for being more productive.

| normalisation | PRE | POST | |
|---|---|---|---|
| open rows / calendar day | 0.93 | 1.61 | 1.74× worse post |
| **open rows / 1k lines added** | **1.43** | **1.83** | **1.28× worse post** — the fair one |

**Survivorship checked, not assumed:** of 66 rows raised pre-cutoff, 12 are closed (18%); of 63
raised post-cutoff, 13 (21%). Near-identical, so "old rows had longer to close" does not explain it.

**The detection-latency finding — the sharpest thing in the audit:**

| era of artifact | median gap, code written → residue raised | mean |
|---|---|---|
| PRE-cutoff (n=65) | **11 days** | 17.7 |
| POST-cutoff (n=29) | **2 days** | 2.6 |

**All fourteen rows with gaps > 30 days point at pre-cutoff artifacts.** No post-cutoff artifact
exceeds 14. Extremes: R127/R128 84d, R112 83d, R99 76d, R53 63d, R117 60d, R132 50d.

**The class split is where the era difference actually lives:**

| era | code | vocab | instrument | docs |
|---|---|---|---|---|
| PRE (65) | 38 | 21 | 5 | 1 |
| POST (29) | 11 | 1 | **15** | 2 |

**The largest single cluster in the register is post-cutoff work**: the arc-manifest instrument
family (`arc-shapes.ttl`, `test_arc_manifest.py`, `test_arc_ablation.py`, `arc-manifest.ttl`) carries
**13 of the 29 post rows, all created 2026-08-20 → 08-22**, under full discipline.

**Reading.** The discipline did not stop defects being introduced. It changed how fast they are
found — post-cutoff, a residue is essentially raised by the loop that wrote it. The pre-cutoff
backlog is the long tail, and the register is now working through it. *That is the mechanism that
makes the inheritance hypothesis feel true from the inside while the rates say otherwise.*

**Agent's own caveats, kept:** 9 rows (marked ⚠ in its table) had the primary artifact assigned by
judgement, not citation; all 9 land in PRE, and moving them to unattributed would *strengthen* the
anti-hypothesis conclusion. `--diff-filter=A` treats a rename as creation; the 2 open rows affected
were re-measured with `--follow` and no bucket changed.

---

## §2 What the regime actually wired, and what it costs (agent-measured; NOT re-run here)

### §2.1 CLAUDE.md describes a hook that was deleted eleven days ago

`.claude/settings.json` today is 117 bytes and has **no `hooks` key** — only a `statusLine`.

```
2026-08-15 2b33802 chore(hooks): drop the percentage context hook, superseded by plimslop
2026-08-09 d2a40ad feat(harness): enforce the context budget with a UserPromptSubmit hook
```

`scripts/context_budget.py` (87 lines) is **still tracked and orphaned** — nothing invokes it.
`CLAUDE.md:289-293` still names it *"wired as a `UserPromptSubmit` hook in `.claude/settings.json`"*.
`grep -in plimslop CLAUDE.md` → **nothing**.

Under this repo's own § Documentation governance, **CLAUDE.md is Contract class** — and this
contract describes a dead artifact and endorses the unit its replacement was built to reject.

The maintainer already wrote the resolution, in `2b33802`'s own commit message: *"That hook gates on
a percentage of the context window, which is the wrong unit… Leaving both registered would have
injected two different and contradictory context claims on every turn."* **It never reached
CLAUDE.md.**

### §2.2 The refuted unit still renders every turn

`.claude/settings.local.json` (gitignored) composes `~/.claude/statusline-context-gauge.py` above
`scripts/cockpit.py`. That gauge defaults to `HANDOFF_PCT=30 / STOP_PCT=40` against a 1M window and
**soft-imports the orphaned `scripts/context_budget.py` to re-confirm them** — the very coupling
`2b33802` kept so gauge and hook "can never drift apart." The hook is gone; the gauge kept the
numbers. Its docstring line 18 is now false.

At iladub's **median session peak of 183,435 tokens**:

| instrument | reading |
|---|---|
| status-line gauge | **18% — blue, no warning** |
| plimslop originating floor (50K) | **3.7× over** |

**The screen says fine; the gate says override.**

### §2.3 The floor has been eaten by the baseline — this is the serious one

The session baseline (what is in the window before you type a word):

| date | baseline | headroom under the 50K originating floor |
|---|---|---|
| 2026-08-15 | 15,658 | 34,342 |
| 2026-08-20 | ~44,190 | ~5,810 |
| **2026-08-26** | **46,243** | **3,757** |

**A fresh iladub session now starts at 92.5% of the originating floor** — roughly one file read of
headroom. Of **474 recorded turns, three have ever been under 50K.**

Hence the number nobody had computed:

> **Override rate: 54% overall (39/72), 52% iladub-only (35/67). Flat across three weeks — no
> learning curve.** Median override 1.8× the floor; worst 7.7×.

The skill calls this rate *"the only honest measure of whether these floors are usable, and a gate
whose circumvention nobody can count is a gate that will be circumvented."* **`reader.py` never
reads `preflight` records**, so the audit is the first time it was calculated.

**A gate overridden half the time, flat, is not indiscipline — it is unsatisfiable by construction.**

### §2.4 The gate has never blocked

`plimslop/stop.py:50` ships `originating: block`. The local `~/.claude/settings.json` overrides it to
`warn`. **All 44 block-type records carry `action: "warn"`.** The one tier with published evidence
behind it runs at the weaker setting, documented in neither repo.

### §2.5 plimslop's own statement of its validation

`README.md`: *"Status: complete as designed… **Not validated.**"*
`HANDOFF.md`: *"**None of it is validated.** … **No floor has been validated. Not 50K, not 150K.**"*
`tiers.py` labels 150K **"NO SOURCE"** in code.

It also self-reports: the corpus was polluted by its own test suite and purged (17 fabricated records
removed, and *"if any real record was misclassified as synthetic, it is gone"*); *"the corpus has
produced no findings"*; a session's first turn is never recorded, biasing away from the `<50K` band;
and **the skill cannot be maintained under its own constraint** — editing it is originating work, so
improving it crosses the floor in the act, *"evidenced three times."*

**Precedent that the method works:** `TESTS.md § Scenario D` (5 reps × 4 arms, 2026-08-15) measured
two shipped rules and **deleted both** — an under-floor silence rule that *raised* announcements
against its own control (0.4 → 1.0 sentences; *"writing three paragraphs about visibility taught
visibility"*), and a ≤2-sentence budget that failed 5 of 5 agents who had done exactly the right
thing. Its § Limits: *"published before it was tested, in a repo whose own Iron Law is that no
guidance ships without a failing control first. **Half of it backfired.**"*

### §2.6 Fragmentation is real; harm is NOT demonstrated

| | handoff/record commits | median commits/PR | direct-to-main commits |
|---|---|---|---|
| 2026-08 (1–8, pre-rule) | 0 | **10.0** | 4 |
| 2026-08 (9–26, post-rule) | **67 (22.9%)** | **2.0** | **113** |

Zero handoff commits exist in the repo's entire history before 2026-08-15. PR rate barely moved
(2.82 → 2.60 per active day) — **the same rate of much smaller PRs**, not more of them.
13 sessions on 2026-08-25 alone.

**But the causal claim is unsupported, and the agent said so:** *"the correlation between the regime
and smaller PRs is strong and clean; the causal claim that this cost quality is not supported by any
evidence in either repo."* The rework corpus is 6 markers in 11 days, 67% unattributed, 2 in the
band that matters; `plimslop reader curve` prints *"n=3 — this shows nothing"* for the sub-50K band.

**And §0 is a data point against harm:** 30 commits produced across ~13 fragmented sessions passed
full CI on the first attempt.

---

## §3 The contradictions, as a list

1. **Percentage vs absolute tokens.** `CLAUDE.md:279` mandates 40% of the window; the skill and
   `tiers.py` both name 40%-of-1M as the specific error. On a 1M window: **300K/400K vs 50K/150K, a
   6–8× gap.**
2. **CLAUDE.md asserts a hook that does not exist** (deleted 2026-08-15). Contract class.
3. **The status line renders the refuted unit every turn** and soft-imports the orphaned script.
4. **The Stop hook is configured never to enforce** — 44/44 warnings, undocumented.
5. **plimslop's own designed health metric is uncomputed** — `reader.py` never reads `preflight`.
   It is 54%.
6. **plimslop is unmentioned in iladub's Contract.** The true state was recorded correctly in
   `2026-08-15-r87-handoff.md:220` — an immutable Evidence file — and never propagated.
7. **The floors and the observed baseline are incompatible** (§2.3). Neither number was set with
   knowledge of this project's baseline, which has **tripled** since they were fixed.

---

## §4 What this audit does NOT establish

- **That fragmentation cost quality.** §2.6. The evidence is absent, not negative.
- **Any pre-plimslop token baseline.** The corpus starts 2026-08-15. No before/after comparison of
  session token behaviour is possible, ever.
- **Whether the 19 logged `stop` decisions were genuine halts.** Unvalidated. `preflight.py`
  validates `--shape` but **not `--decision`**, and `stop` is undocumented in skill and README —
  so the 54% override rate counts them as compliance and is therefore a **floor**, not a ceiling.
- **That 50K or 150K are the right numbers.** Nobody has validated them, including their author.
- **That the 1.28× post-cutoff residue rate is significant.** No power calculation; n=94 attributed
  rows with 9 judgement calls inside them.
