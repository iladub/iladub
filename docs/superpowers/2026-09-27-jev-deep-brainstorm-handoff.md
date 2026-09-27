# Handoff — a deep, possibly disruptive brainstorm on integrating Jev (2026-09-27)

**Serves:** maintenance — the brainstorm that decides how Jev enters etkl; it meets no criterion itself

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `jev-reading-handoff` (PR #275)

**Doc impact: none.**

Written at ~52,000 working tokens (1.04x the 50K originating floor), at the maintainer's request for
a cleared context. Part 5 is written first and graded.

## 5. Next action — PROPOSED

**Open a fresh session and run `superpowers:brainstorming` as a deep, architectural brainstorm on
how etkl should integrate Jev. The maintainer explicitly allows a disruptive answer, one that is not
a continuation of today's seams:** *"We might be creative and eventually rethink how to integrate
jev, this might be disruptive and not continuous."* So do **not** start from the three approaches
this session offered (§ 3). They were drawn inside today's architecture: a veto-only reviewer, a
proposer behind oracles built first, and a BAML v1 migration. Treat them as one family of answers,
not as the option space.

Why this is graded PROPOSED: the brainstorm's direction is open by design. The one thing it must do
early, because it can be refuted in minutes, is state which of its premises rests on a
**measurement** (§ 2) and which on a **hope**, and test the cheapest hope before designing on it.

## 1. Goal

Decide with the maintainer how Jev (typed answers only, text only, cheap, no abstention unless
offered, weak at arithmetic) should reshape etkl's reading of human-addressed documents, including
answers that restructure the pipeline instead of plugging Jev into existing seams.

## 2. Where the primaries are

- **Intent and Jev's measured behaviour:** `docs/superpowers/2026-09-27-jev-reading-architecture-handoff.md`, § 3 (the maintainer's scope, quoted) and § 2a (Jev input/output, limits, cost, strong and weak zones, BAML status).
- **This session's spike:** `docs/superpowers/2026-09-27-jev-boxhead-spike-evidence.md`. It covers Jev on the 5 recorded boxhead questions, per-word placement against role-only, and what `dispose_boxhead` can and cannot see. Raw data is at `internal/benchmarks/jev-2026-09-27/boxhead-spike/` (untracked).
- **The ruling any design must satisfy:** CLAUDE.md § 8, *"One geometric attempt, then NEURAL"*: no oracle, no worker; typed, closed output; the effort goes into oracles.
- **The oracle-power measurement:** `scripts/grounding_oracle_power.py` and the evidence behind PR #257. The grounding oracle's admissible set is 0 on 2,215 of 2,364 asks, 1 on 149, and ≥2 nowhere. So today no live decision gives any worker a real choice.
- **Seams inventory:** `docs/superpowers/2026-09-17-neural-worker-seams-evidence.md`, and the handoff above § 2. The only live workers in a production compile are `ReadBoxhead` and `ReadEmptyCells`, and both read images.
- **Where the maintainer's broader direction lives** (for placement, not scope): the kisal holon-engine specs D18/D19 (the handoff above § 2), and the Quarter15 convergence pause (memory `quarter15-convergence-pause`).

## 3. What was decided, and where

- **The spike's result** is recorded in the evidence note above (§§ 2–5). Per-word placement from text geometry is refuted. Role-only answers agree with Sonnet on 79–94% of words, but Jev misses every spanning label, and the oracle cannot see a role error.
- **A deep brainstorm on a cleared context, with a disruptive answer allowed.** The maintainer decided this 2026-09-27 in session, and it is recorded **nowhere but this file**.
- **Three incremental approaches were offered and not chosen.** (A) Jev as a veto-only reviewer that can only demote. (B) Jev as proposer, with oracles built first, on a shared question layer (options derived from `dec:optionSpace`, probabilities, record/replay, rationale as the derivation's IRI, no prose). (C) A BAML v1 migration. They are recorded only here and in the session. None was ruled out; the maintainer asked to widen the space instead.

## 4. Unverified or assumed

- **This session's framing claim is argued, not measured:** *the constraint on etkl is oracles with refusal power, not worker cost.* It rests on the grounding |A| measurement and the spike, which cover one seam each.
- Approach A's premise, that a demote-only worker needs no oracle, **was never put to the maintainer**. The veto check that would test it on Sonnet's 33 recorded labels **was not run**.
- Whether a line-level or label-level role question, rather than a per-word one, recovers the spanners: not measured.
- Sonnet's recorded readings served as the reference, and they are not ground truth.
- The spike covered 5 pages from 3 documents, and Jev's answers vary by ±0.02 from run to run.
- PR #275's CI (`test`) was in progress when this was written.
