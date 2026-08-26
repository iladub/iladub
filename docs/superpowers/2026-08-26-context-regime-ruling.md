# Ruling — the unit the context floor is denominated in

**Date:** 2026-08-26 · **Base:** `main` @ `595c5ef` · **Shape: ruling (originating).**
**Authorized by the maintainer in-session**, including the Contract edit that follows from it.

**Budget disclosure, first, because this file is an instance of what it rules on.** This ruling was
made at ~61K tokens — **1.2× the 50K originating floor** — and the override is logged in the corpus.
The decision to proceed rather than hand off again was taken *in advance and in writing*, as
`2026-08-26-context-regime-handoff.md` § "The trap this work sets for itself" demands: a second
session would start at the same ~46K baseline with the same ~4K of headroom and would have to re-read
the same files to reach the same point. **Recursive handoff is not a remedy for an unsatisfiable
floor; it is the floor's failure mode wearing a procedure's clothes.**

---

## §1 What was already ruled, and by whom

The handoff frames the unit as an open three-way question — absolute, percentage, or something else.
**One branch was already closed, by the maintainer, in writing**, eleven days before the audit:

```
$ git log -1 --format=%B 2b33802
chore(hooks): drop the percentage context hook, superseded by plimslop

… That hook gates on a percentage of the context window, which is the wrong unit:
on the 1M window it runs against, R76's 40% permits 400,000 tokens, roughly an
order of magnitude past where multi-step reasoning is already compromised.
```

**Percentage is dead and is not reopened here.** What `2b33802` did *not* do was propagate itself
into the Contract, which is contradiction §3.2 and §3.6 of the audit.

So the live question is not *percentage vs absolute*. It is: **absolute tokens of what?**

## §2 The measurements this ruling rests on

All four of the audit's §2 claims were **independently re-run** in a separate context on 2026-08-26
and **all four REPRODUCED** — the full report, with every command and its raw output, is
`2026-08-26-context-regime-remeasure.md`. This closes the handoff's largest caveat ("§1 and §2 were
produced by delegated agents and NOT independently re-run").

| claim | audit | re-measured | verdict |
|---|---|---|---|
| baseline series | 15,658 → ~44,190 → 46,243 | 15,658 → 44,164–44,194 → **46,243** | REPRODUCED |
| override rate | 54% (39/72), 52% (35/67), 19 stops | 54.2%, 52.2%, 19 | REPRODUCED |
| turns under 50K | 3 of 474 | **3 of 482** (denominator +8; all 8 additions ≥50K) | REPRODUCED |
| block records all `warn` | 44/44 | 44/44 | REPRODUCED |

**Two facts the audit did not report, measured here, and both load-bearing:**

**(a) The baseline is not this repo's to cut.**

```
CLAUDE.md   35,573 chars  ~8,893 tok
MEMORY.md    9,187 chars  ~2,296 tok
```

Together **under a quarter** of the 46,243 baseline. The remainder is harness — system prompt, tool
schemas, skill listings, MCP instructions. **Halving CLAUDE.md would recover ~4.5K of 46K.**

**(b) plimslop already models the baseline, already detects this exact failure, and is 3,757 tokens
away from firing on it.**

```python
# plimslop/stop.py:68-73
    if session.baseline >= LOWEST_FLOOR:
        return "warn", (
            f"Baseline is {session.baseline:,} tokens, already at or above the "
            f"{LOWEST_FLOOR:,} originating floor before any conversation. The gate "
            "cannot be satisfied in this configuration, so it is not enforced. "
            "Reduce the baseline or revise the tier.")
```

`measure.py:80` computes `baseline` as the first turn's total; every `turn` record in the corpus
already carries `tokens` **and** `baseline` as distinct fields. The guard has **never fired here** —
re-measured: *"block records with baseline >= 50000: 0 of 44, max baseline among them 46,243."*

**iladub therefore sits in the worst available position: 92.5% of the floor.** Not satisfiable, and
not recognised as unsatisfiable either. The guard that would have named this problem is 3,757 tokens
from tripping, and the baseline has grown ~30,600 tokens in eleven days.

## §3 The ruling

plimslop states its own remedy set, in its own words: **"Reduce the baseline or revise the tier."**
§2(a) measures reduce-the-baseline as unavailable — the mass is harness, not repo. **So revise the
tier is the only remaining option, and the question is only which form it takes.**

> **RULED: the floor stays denominated in absolute tokens, and is measured on work accumulated
> ABOVE the session baseline — `working = tokens − baseline` — not on total window occupancy.**
> The `originating` floor stays 50,000 and `executing` stays 150,000, now read in that unit.

Why this form and not a larger constant:

- **It keeps `2b33802`'s ruling intact.** The unit is still absolute tokens. A percentage would
  re-open a question the maintainer closed.
- **It is satisfiable by construction.** A fresh session starts at `working = 0` with the full
  50,000 available — which is what the floor was always meant to describe.
- **It does not go stale.** The baseline tripled in eleven days (15,658 → 46,243) for reasons outside
  this repo. Any static raised floor — 96K, say — is this same fix with a shelf life, and would need
  re-ruling the next time a harness release adds tool schemas.
- **It completes something plimslop half-built** rather than inventing a mechanism. The field is
  measured, recorded per-record, and already consulted at `stop.py:68`. Nothing computes the
  subtraction.

## §4 The assumption that could sink this, stated as unverified

**This ruling presumes that baseline tokens cost multi-step reasoning less than working tokens do.
That is NOT established.** The published anchor behind the 50K figure — NoLiMa (11 of 13 models below
half their baseline at 32K), Chroma (decline begins immediately, no cliff) — measures **total**
context length. Neither separates *instructions the model is meant to follow* from *haystack it must
search*. The iladub baseline is the former; the subtraction assumes that distinction matters.

**If it does not, this ruling is wrong** and the correct remedy was to cut the baseline anyway, or to
accept a gate that fires at turn one. Recorded here, not buried, because it is the single premise the
whole ruling stands on.

## §5 What would show it wrong

The audit's own bar: *"A remedy that only moves the numbers is unfalsifiable unless it says what would
show the new ones wrong."*

> **PREDICTION: the override rate falls materially below 54%, and the fall shows up within roughly
> three weeks of corpus.** The rate has been **flat at 54% across three weeks** — no learning curve —
> which is the signature of a gate that cannot be met rather than one that is being flouted.

- **If the rate falls** → the floor was unsatisfiable, as ruled.
- **If it stays flat near 54%** → the unit was never the problem, §4's assumption is the likely
  culprit, and this ruling is refuted by its own instrument.
- **The measurement already exists** and needs no new code beyond the subtraction: `preflight`
  records carry `shape`, `tokens` and the floor; `turn` records carry `baseline`.

**Caveat that weakens the instrument, carried from the audit:** the 54% figure counts 19 logged `stop`
decisions as compliance, and `preflight.py` validates `--shape` but not `--decision`. **54% is a
floor, not a ceiling**, so the post-change comparison must be computed the same way to stay honest.

## §6 What this ruling does NOT decide

- **It does not change plimslop.** That is a separate repo; the subtraction at `stop.py:58` and
  `preflight` is **proposed, not made** — see §7. Until it lands, plimslop keeps gating on total
  tokens and the recorded override rate keeps its old meaning.
- **It does not validate 50,000 or 150,000.** `tiers.py` still labels 150K `NO SOURCE`. This ruling
  changes what the numbers are measured against, not whether they are right.
- **It does not settle the Stop-hook enforcement gap** (audit §2.4 / §3.4): 44/44 block records ran
  as `warn` because `~/.claude/settings.json` sets `PLIMSLOP_MODE_ORIGINATING=warn` inline on the
  hook, undocumented in either repo. **Re-measured and confirmed.** Left open deliberately —
  restoring `block` under a floor that was unsatisfiable would have been the wrong order.
- **It does not establish that fragmentation cost quality.** Audit §2.6 and §4. Correlation is clean;
  causation has no evidence. Do not let this ruling be cited for it.

## §7 What follows, in order

1. **`CLAUDE.md` § Loop & context hygiene** — rewritten in this branch. Contract class; authorized in
   session. Replaces the 40%-of-window mandate and the deleted-hook sentence.
2. **`~/.claude/statusline-context-gauge.py`** — renders the ruled unit, and its docstring stops
   repeating the false *"iladub does, wired as a UserPromptSubmit hook"* claim. **User-scope, not in
   this repo** — the audit places this file in the tree; it is not there, so no iladub commit can fix
   it and none should be expected to.
3. **`scripts/context_budget.py`** — deletion is behaviourally a no-op once (2) lands: its constants
   are 30/40/1M, identical to the gauge's own defaults, and the soft import is existence-gated.
   Deferred, not done, so that (2) can be verified first.
4. **plimslop** — proposed: subtract the baseline at `stop.py:58` and in `preflight`, and teach
   `reader.py` to read `preflight` records so the override rate is computed by code rather than by an
   audit. Not made here.

**Doc impact:** `none` — this is Evidence, and the CLAUDE.md change is Contract, not the published
site.

---

## §8 Verification of the gauge conversion (done in this session)

`~/.claude/statusline-context-gauge.py` now renders the ruled unit. It is **user-scope**, so this
evidence is the only record of the change inside this repo.

**Eight failure modes, all exit 0** (empty payload, garbage stdin, missing transcript, fresh session,
handoff zone, post-compaction, 40-column terminal, no `context_window` block). The status line never
breaks the TUI; a missing transcript degrades to `baseline = 0`, which reports `working == used` —
wrong in the conservative direction.

**FALSIFICATION.** The same two moments, rendered by the pre-change gauge and the post-change gauge:

| moment | OLD gauge | NEW gauge |
|---|---|---|
| fresh session, 46,243 tokens | `5%` **blue, no warning** | `0k/50k` **blue** — the floor is available |
| median session peak, 183,435 | `18%` **blue, no warning** | `137k/50k` **STOP** |

The 183,435 row **independently reproduces audit §2.2's claim** (*"the gauge reads 18%, blue, no
warning"*) from the artifact itself rather than from the audit's report of it.

And the subtraction is load-bearing rather than decorative — with `working = max(0, used - baseline)`
replaced by `working = used`, a fresh session that has done no work reads:

```
ctx ██████████████████░░ 46k/50k handoff   46k ctx, base 46k
```

**Amber before a word is typed.** That is the unsatisfiability of §2, now visible in the instrument
instead of only in the corpus.

**Not verified:** that the gauge and plimslop agree in the live path. They share the `_total`
definition by construction (copied identically from `measure.py`), but plimslop still gates on total
tokens, so the bar and the gate now disagree by exactly the baseline until R141 lands. **The bar is
the ruled unit; the gate is not yet.**
