# Handoff — the question compiler: write its spec (2026-09-27)

**Serves:** maintenance — hands the spec of the chosen Jev architecture to a fresh session; it meets no criterion itself

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `jev-reading-handoff` (PR #275)

**Doc impact: none.**

Written at ~60,000 working tokens (1.2x the 50K originating floor). The session stopped because
the next step, the spec, is originating work. Part 5 was written first, and it grades each claim.

## 5. Next action

**Asserted:** resume `superpowers:brainstorming` (architectural path) at *present design sections*,
then write the spec to `docs/superpowers/specs/2026-09-2x-question-compiler-design.md`. The direction
is ruled (§ 3). Do not re-open the choice of approach and do not re-ask the questions answered below.

**Proposed, each open to refutation while the spec is being written:**

- **Oracle coverage is the spec's hard part, not the worker.** Probe B (evidence note § 2) shows that geometry refuses spanner commissions (R1) at zero false refusals. It does not refuse leaf/title confusion or omissions. The spec must name a non-geometric oracle for omissions. Otherwise §8's *no oracle, no worker* keeps the role question off Jev, and Jev covers less of the pipeline than the architecture assumes. **If no such oracle can be stated, the spec should say which questions stay on today's derivation**, rather than force them.
- **The stub derivation is a defect in its own right.** `GridColumn.is_measure` takes bfs p5's year column for `Quantity` (evidence § 2). R2, and any oracle that needs "the stub", depends on it. Check whether it is already a register row before raising one.
- **Coarse-to-fine rounds are the latency dividend.** Page → regions → structure → roles → grounding, each round a batched Jev call of ≤300 questions. This is argued from ~0.4 s per 50-question call. The number of rounds a page actually needs has not been measured.

## 1. Goal

Specify etkl as a *question compiler*. Jev proposes reading judgements over linearised text in
batched, coarse-to-fine rounds. The host derives each round's closed options, with an explicit
abstain, from the graph. Geometry and SHACL dispose. Vision escalates on disagreement.

## 2. Where the primaries are

- **Both probes of this session:** `docs/superpowers/2026-09-27-jev-spatial-text-and-geometry-refusal-evidence.md`. Its raw data is at `internal/benchmarks/jev-2026-09-27/boxhead-spike/run3-spatial/` and `run4-refusal/` (untracked).
- **The first spike and Jev's measured behaviour:** `2026-09-27-jev-boxhead-spike-evidence.md`, and `2026-09-27-jev-reading-architecture-handoff.md` § 2a.
- **The ruling the spec must satisfy:** CLAUDE.md § 8 (AXIOM/NEURAL/PROCEDURAL; one geometric attempt, then NEURAL; no oracle, no worker).
- **Today's oracles:** `etkl/boxhead.py` (`dispose_boxhead`, centre-in-interval), `etkl/tiling.py`, `etkl/oracle.py`, `ground.py` (`_grounds_to`). Option space: `dec:optionSpace` via `_deliberate`.
- **The benchmark the spec answers to:** corpus N/7 (`tests/arc-manifest.ttl`). Etkl stands at 5/7; cbh and bfs are unmet.

## 3. What was decided, and where

All of the following was decided by the maintainer in session on 2026-09-27. It is recorded **nowhere but this file**,
so it is reversible.

- **Jev's primary evidence is linearised text.** Geometry is secondary: it generates and checks options, and is never read by Jev. Probe A supports this.
- **Vision (Sonnet) is an escalation tier only.** It runs where the text reading and the geometric derivation disagree. The explicit aim is to use Jev's latency so that etkl "gets steroids".
- **The approach is the question compiler** (option 1 of three offered). Cross-examination (both channels read fully, admit on agreement) and bulk verifier (Jev audits the pipeline's output) were offered and not chosen.
- **The geometry-refusal hope was tested first**, at the maintainer's request. It holds only partially (evidence § 2).

## 4. Unverified or assumed

- Everything is measured on 5 pages from 3 documents, with one run per condition and ±0.02 run-to-run noise.
- Sonnet's readings are the reference and are not ground truth. Some disagreements look like Sonnet's errors (the footnote marks on bfs p5).
- "Geometry becomes the oracle and etkl's procedural core shrinks" has not been costed against today's `src/`. Which derivations become oracles, and which stay, is the spec's job.
- **`main` is red since `6d6631f`** (PR #274, 2026-09-20). The failure is `tests/test_first_seen.py::test_readat_never_predates_first_observation`, on two readings registered 2026-09-19 that first appear on `main` 2026-09-20. PR #275 (docs only) inherits it and is `BLOCKED`. Not investigated.
