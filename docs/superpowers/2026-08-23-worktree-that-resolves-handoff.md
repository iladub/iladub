# Handoff — the spec is written and approved; the PLAN is not written, and that is deliberate

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-worktree-that-resolves`
**Runner:** `./.venv/bin/python`, never `python3`.
**Shape: originating, stopped at 114k** — 2.3× the 50k originating floor. The spec was written
under one logged override; a second override to write the plan is exactly the failure CLAUDE.md
§ Plan authoring records (a 919-line plan written late, five defects in the plan text itself).

## §1 Goal

Close [[R121]] and ship an M19 that refuses to judge what it cannot see. **Next action: write the
implementation plan from the spec, in a fresh session, having read the spec cold.**

## §2 Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-23-the-worktree-that-resolves-design.md` | **the spec** — approved by the maintainer 2026-08-23. §2 every measurement with its command, §4 the five changes, §7 the falsifications, §8 done, §9 what it does not do, §10 what it reuses from the abandoned spec |
| `docs/superpowers/specs/2026-08-23-the-faithful-worktree-design.md` | the **abandoned** spec. Read it only for its Appendix (six rejected designs, still standing) and the §10 provenance map. Its corpus/CI half is reversed |
| `docs/superpowers/2026-08-23-faithful-worktree-handoff.md` §3bis | why that spec died. The `.pth` shadow, measured |
| `tests/test_arc_ablation.py` | `_run_module:197`, `_scores:214`, `_ablate:253`, `ablation_refusals:291`, limitation 4 at `:87-111`, `_SKIPS_WITH_A_REASON:434` used at `:460` |
| `docs/superpowers/residues.md` → rows R113, R118, R120, R121 | the four this loop touches. **Open the full rows; never plan against an index line** |

## §3 What was decided, and where each decision is recorded

| decision | recorded where | status |
| --- | --- | --- |
| The loop's headline is instrument honesty, not graph yield | spec §1, §9 | **maintainer choice, 2026-08-23** |
| R121 closes by `PYTHONPATH=<wt>/src`, not a per-worktree install or an audit hook | spec §2.1–§2.3, §4.1 | **settled by measurement** — commands and output inline |
| The corpus is NOT materialised; the abandoned spec's CI ruling is REVERSED | spec §2.5, §6 item 2 | **settled by measurement** (`_SKIPS_WITH_A_REASON` fan-out) |
| The hermeticity probe is dropped; the question it asked goes to the register instead | spec §8 item 4, §9 final bullet | **maintainer choice, 2026-08-23** |
| A newly grounding pair is a **finding**, authored in a later loop — never this one | spec §8 item 2 | **settled 2026-08-23 by precedent + R113**; nowhere but the spec — reversible |
| No new M-number: control failure, disjointness collision and an unattributable ERROR are instrument failures | spec §5 | settled — same distinction the previous loop drew |

**Nothing is implemented.** The branch contains the spec and this file. Two commits: `87c3e6b`
(spec), `efe0cc6` (drop §5), plus this handoff.

## §4 Unverified or assumed — not empty

1. **Two numbers are carried from elsewhere, not measured this session**: §2.6's *1293 collected,
   6 errors → 1314, 0 errors* (from the previous handoff) and §2.4's *29 distinct artifact files*
   (from the abandoned spec §11.2). Both are marked MEASURE in spec §8 item 7. **Re-derive them;
   do not cite them.**
2. **The `--tb=no` seam is named, not solved.** Spec §4.5 requires reading a collection ERROR's
   exception, and `_run_module:206` currently prints none. Which flag yields a parseable exception
   is unmeasured — measure before writing the rule, not after.
3. **`_run_module`'s inherited `PYTHONPATH` is unexamined.** The subprocess passes no `env=` today.
   What the inherited value already carries was never checked (spec §4.1, named seam).
4. **The §2.2/§2.3 probe used a hand-built worktree, not the shipped `_ablate` path.** It proves
   the mechanism; it does not prove the mechanism survives materialisation and deletion ordering.
5. **Whether §4.1 flips any live pair is unknown.** Nobody has run `ablation_refusals` since. The
   spec predicts zero new edges (§9) — that is a prediction, not a measurement.
6. **The spec was single-sourced.** One reading measured the premise, framed the design and wrote
   it. The maintainer overrode one element (dropping §5). No adversarial review has run.

## §5 The next concrete action

Invoke `superpowers:writing-plans` against the spec, **in a fresh session**, reading the spec cold
first. The plan states interfaces, invariants and the falsifying oracle per §7 — **no function
bodies**, and every load-bearing claim about `test_arc_ablation.py` re-measured with `file:line`
and the command inline.
