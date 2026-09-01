# Candidate A is refuted — negative-oracle power is measured 8 times in 9, without a rule

**Doc impact: none.**

`docs/superpowers/2026-09-01-progress-census-handoff.md` §5 offered four candidate diagnoses for the
maintainer's concern and ranked none of them, deliberately. This loop took **A** — *"oracle POWER is
the failure mode"* — and ran **A's own falsification first**, which A itself specified at
`2026-09-01-progress-census-handoff.md:54`:

> **What would falsify A:** census the last ~10 loops' negative oracles for power. If most were
> adequate, two instances is a coincidence, not a pattern.

**Most were adequate. A is refuted, and its remedy should NOT be adopted.**

## The census

11 merged PRs touching `src/` back to 2026-08-13, found with
`git diff-tree --no-commit-id --name-only -r -m --first-parent <sha> | grep '^src/'`. Each was
classified on whether it made a *negative claim* ("documents I did not target are unchanged,
therefore this is safe") and whether it carried *power evidence* — a reach probe, an ablation, or a
demonstration that the oracle's scope covers the changed rule's domain.

| bucket | count | loops |
| --- | --- | --- |
| **POWERED** | **8** | #146, #145, #135, #123, #106, #105, #104, #103 |
| UNPOWERED | 1 | #109 — and ambiguous with NO-CLAIM; its `src/` diff is comment-only |
| NARROW (whole-loop) | 0 | two loops carry a narrow *sub*-oracle, both self-reported |
| NO-CLAIM | 2 | #142, #140 — comment-only `src/` diffs |

**Of the 9 loops that made a negative claim, 8 carried power evidence — 89%.**

## The two claims this turns on, verified independently of the census

The census was run by a subagent. Its conclusion is a proposition until checked, and its two
load-bearing claims were re-measured here directly.

**1. R45's reach probe was authored BEFORE the fix, not discovered afterwards.** The progress census
presents R45 as a loop whose vacuous rows were found later. Branch commit order says otherwise:

```
$ git log 5743af3 --not 22263a2 --format='%h %cI %s'
5743af3 2026-08-31T16:08:53+02:00 Merge pull request #145 …
afbcbee 2026-08-31T15:16:32+02:00 docs(handoff): the unit suite is green …
ebee8d3 2026-08-31T14:54:42+02:00 fix(R45): a header level is a band line …      ← the fix
796c0ec 2026-08-31T13:07:29+02:00 docs(handoff): the subject relocated a third time …
e95ae7b 2026-08-31T12:56:08+02:00 spec(R45): the corpus oracle is WEAKER than its table …  ← the probe
1d56133 2026-08-31T12:47:14+02:00 spec(R45): a header level is a band line …
```

The probe precedes the fix by **two hours**. And its text is far stronger than "noted a caveat" —
`specs/2026-08-31-a-header-level-is-a-band-line-design.md` §3.4.1, read at the merge commit, states
the consequence for its own oracle and forbids the citation:

> Five of the six "PASS" rows in §3.4 therefore assert nothing about this change and **must not be
> cited as if they did.** … **Consequence for §7's oracle 3, stated here once:** re-running the six
> inert documents is a regression guard of low power.

**R45 is the process working, not a hole in it.**

**2. A corpus-wide negative ablation was PRESCRIBED by a plan in August, with no rule requiring it.**
`plans/2026-08-17-the-gate-and-the-label.md:256`:

> **Required: 0.** **Falsification: re-gate the dec leg and reproduce 316.** Both numbers in the
> report, both from runs you performed.

## Why the remedy is not adopted

A proposed extending `CLAUDE.md` plan-rule 4 to the negative half of an oracle. **A rule enforcing a
practice already observed at 89% costs every future loop and buys the remaining 11%** — and the one
loop in the gap (#109) is the ambiguous, comment-only case, not a loop that shipped false safety.
Rules in this file are paid for by every session that reads them; § Plan authoring discipline rule 6
condemns exactly this shape of addition — restating an invariant the artefacts already carry.

## The successor finding — and it is NOT candidate B as B was stated

The census's sharpest result is not the count. It is that the two oracles in the window that
genuinely **could not fire** failed for the same upstream reason, and it is neither process nor
rigour:

> the corpus contains only two documents that exercise the cross-tab path at all
> — `specs/2026-08-31-a-header-level-is-a-band-line-design.md:167` (§3.4.1)

**The corpus does not reach the code.** R45's five vacuous rows were vacuous because five documents
never enter the changed function; #109's "0 triples, all 27 pages" was inert because no ontology
subject reaches an engine at all. Both loops *measured* this and published it. Neither could fix it,
because it is a property of the corpus, not of the change.

**This is distinct from candidate B**, which is about *adjudication* — five of seven documents carry
no accepted verdict or score floor. A document can have a floor and still never enter the code path
under test; reach and target are independent. B would give the corpus targets; it would not give it
reach.

**And the register has been filing this one instance at a time for a month** — `R68` (no real
document exercises the transposed path), `R97` (four wired `tab:` shapes, 0 focus nodes each), `R99`
(11 focus nodes, unreachable body term), plus R45's and #109's findings, which got no row of their
own. Five instances, five framings, never once stated as a property of the corpus. Raised here as
**R158**.

## Unverified or assumed

- **The census covered 11 loops in one window** (2026-08-13 → 2026-09-01) and inherits the progress
  census's own caveat: no comparison was made to any earlier period. 89% is a rate over 9 loops.
- **Two of the census's eleven classifications were re-verified here; nine were not.** The two chosen
  are the ones the refutation rests on. A reviewer wanting to overturn the refutation should attack
  the other nine, and the bucket definitions are in the report, not in this file.
- **"POWERED" is a documentary judgement, not an empirical one.** It records that a loop published
  reach or ablation evidence — not that the evidence was independently re-run here. No corpus
  battery was run for this census.
- **#146 and #123 are defensibly classifiable otherwise.** #146 is POWERED *and* exhibits the R155
  narrow-scope pattern in the same loop (self-detected, raised as `R156(b)`); #123's differential leg
  is 2-of-7. A reviewer applying the bucket definitions literally could move either, and moving both
  still leaves 6 of 9.
- **R158's claim that the five instances are "the same property" is a REFRAMING, not a measurement.**
  Nobody has measured corpus reach as a corpus-wide quantity — that is precisely what R158 asks for,
  so its own premise is the thing still to be established.
