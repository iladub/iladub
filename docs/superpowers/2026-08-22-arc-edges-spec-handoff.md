# Handoff — the dependency-graph spec is written; the plan is not

**Topic:** process · **Date:** 2026-08-22 · **Branch `the-arc-has-edges` @ `1397c04`**, branched
from `main` @ `fd6c81b`, **not pushed** · **Shape: originating, written at ~110k — 2.2× the 50k
floor.** The spec was authored here because its design was settled and approved in-session;
the **plan was deliberately not started**.

## Goal

Give the arc a dependency graph at **criterion** scope, graded by whether the edge can be grounded,
so "what must land before X" is a derivation rather than a reading.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md` | **the spec.** §2 carries six measurements taken before any design; §4 the five preconditions and the two-sided ablation; §5 refusals M12–M19; §6 the monitor and the one maintainer decision; §7 the correction to the origin handoff |
| `docs/superpowers/2026-08-22-next-loop-handoff.md` | the origin. Read § CHOSEN DIRECTION. **§7 of the spec contradicts its subsumption claim** |
| `tests/arc-manifest.ttl` · `tests/arc-shapes.ttl` · `tests/test_arc_manifest.py` | the manifest the edges go into, the membrane M12–M18 extends, and the environment leg M19 joins |
| `vocab/queries/arc-orphan.rq` header | why `prog:blockedBy` is a plain string and the register is not in the graph — the rejected alternative this spec keeps rejected |
| `tests/docgov_extract.py:36-51` · `vocab/shapes/doc-governance-shapes.ttl:74-96` | classification is by **path prefix**, and what `docs/wiki/` would demand of a generated file |

## What was decided, and where each decision is recorded

- **Two predicates, not one predicate with a grade property** — maintainer, in-session; recorded in
  **spec §3**, with the closure argument that settles it.
- **The ablation runs in CI on a `git worktree`, not as a recorded measurement** — maintainer,
  in-session; recorded in **spec §4**.
- **The monitor is a reader-of-record query plus a regenerate-and-diff-gated generated file; the
  cockpit is not touched** — maintainer, in-session; recorded in **spec §6**.
- **A4 demoted from strict to non-strict, direction moved to a two-sided ablation** — decided by
  measurement Q3 *after* the three answers above, and recorded in **spec §2 Q3 and §4**. The
  maintainer saw the revision stated but has **not** separately confirmed it.
- **A6 (distinct artifact files) added** — found by the spec's own self-review, recorded in
  **spec §2 Q6 and §4**. Never reviewed by anyone but its author.
- **`docs/superpowers/arc-dependency-landscape.md` as the generated file's home** — recorded in
  **spec §6**. No longer contingent: the `CLAUDE.md` clause it needed was **requested and GRANTED
  by the maintainer, 2026-08-22**, and is **recorded in `CLAUDE.md` § Documentation governance
  itself** — evidence-immutability now names two exceptions, `residues.md` and a gated generated
  cache. The grant is *to a gated cache*; an ungated derived file remains forbidden.

## Unverified or assumed

- **Nothing in the spec has been implemented or run.** No edge has been authored, no refusal
  written, no ablation attempted. Every claim about how M19 will behave is a design claim.
- **The worktree seam is UNMEASURED** — spec §4 carries an explicit MEASURE box. Whether an oracle
  test passes with `cwd` in a bare `git worktree` and no local `.venv` is unknown; the repo has
  **no** existing worktree usage (measured: 0 hits) and one tool that already *refuses* a shallow
  second checkout (`tests/test_docgov_extract.py:83-88`).
- **The 59/74 orphan figure in spec §7 is quoted from the origin handoff, not re-measured.**
- **Q1–Q6 are facts about `fd6c81b`.** Q1 and Q4 move the moment any criterion flips to met. The
  implementer must re-run them before authoring edges; the spec says so in §2's reproduction note.
- **Acyclicity is not known.** The spec is built so that M14 answers it; nobody has asked yet.
- **The suite was not run on this branch.** Only `tests/test_doc_governance.py` was executed
  (4 passed, 2 warnings), because the spec is a dated file under `specs/` and that is the leg that
  gates its `Doc impact:` block.

## The next concrete action

In a **fresh session**: invoke `superpowers:writing-plans` against the spec. The maintainer has
reviewed it and granted the one clause it asked for; nothing else is waiting on them.

The plan's **first task is spec §4's MEASURE box** — whether an oracle test passes with `cwd` in a
bare `git worktree` and no local `.venv`. M19's whole design rests on that answer and nobody has it.
Do not let the plan assert it from reading (CLAUDE.md § Plan authoring, rule 2).

**Two things in the spec have been reviewed by nobody but their author** and deserve a plan author's
adversarial pass before anything is built: **A4's demotion** to non-strict (§2 Q3, §4) and **A6**
(§2 Q6, §4).
