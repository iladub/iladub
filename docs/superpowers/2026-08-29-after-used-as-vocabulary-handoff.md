# Handoff — after `used as vocabulary` (PR #132, merged `2abc62c`)

**This is a set of POINTERS. It does not restate the primaries, and nothing in it is settled
because it appears here.** Open what it points at.

## 1. Goal

Decide whether iladub's spec/plan defect rate is a rigour artefact or a real regression — the
maintainer raised it on 2026-08-29 — and act on the answer.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/specs/2026-08-29-used-as-vocabulary-design.md` + `plans/2026-08-29-used-as-vocabulary.md` | The loop that just merged. §10 lists 7 seams; the plan's Self-Review claims "no gap found" — six defects were nonetheless found in execution |
| `git log 87bf8cf..2abc62c` (11 commits) | Every defect is named in the commit that hit it. **Read the commit messages, not this file**, for what each was |
| `CLAUDE.md` § "Plan authoring discipline" | The seven rules and their worked counter-examples, loop by loop, with dates. This is the raw material for the defect-rate measurement |
| `docs/superpowers/residues.md` (index, ~2.8k tokens — read in full) | 31 closed / 141 rows. Tally snapshots in each row's `(n/m closed)` are a trend line when read down the column |
| `docs/superpowers/residues-open.md` rows `R146`–`R151` | The six this loop raised. `R151` is the one with a live next action |
| plimslop corpus (`/dev/git/plimslop`, user-scope install) | Every turn's token figure and every preflight decision, including overrides. The override-rate prediction of the 2026-08-26 ruling is testable here |

## 3. What was decided, and where that decision is recorded

- **Vocabulary-ness is positional, not lexical** — a term is demanded when the graph *uses it as
  vocabulary*. Recorded in `vocab/queries/vocabulary-role.rq`'s header and spec §2.1. Settled.
- **`prog:`/`docgov:`/`corpus:` are declared INTERNALLY**, not published. Ruled by the maintainer
  2026-08-29; recorded in spec §2.8 and in each `vocab/internal/*.ttl` header. Settled.
- **`etkl:alignmentSubject` was NOT added** — seam 4 decided by writing the shape both ways and
  running it. Recorded in `vocab/shapes/query-declaration-shapes.ttl`'s header and commit `72d0cff`.
- **`tab:aggFn*` declared rather than deleted** — because `vocab/ontology/tab.ttl:163` cites the
  align module for those names. Recorded in commit `bcea2b9` and in `tab.ttl`'s new section comment.
- **Candidate 8th plan rule — RECORDED NOWHERE BUT THIS FILE, therefore reversible and unadopted:**
  *a plan may not pin a derived total that its own tasks will move; pin the delta and the named set
  instead.* It is plan-rule 7 at a different scale (a measurement falsified by the act that depends
  on it) and would subsume it. **Do not add it to CLAUDE.md on this file's say-so** — it rests on one
  loop. Measure first (§5).

## 4. Unverified or assumed

- **CI on `2abc62c` shows `cancelled`, and that is EXPECTED — do not read it as a failure.**
  `.github/workflows/ci.yml:7-9` sets `concurrency: cancel-in-progress: true`, so pushing this very
  handoff commit (`43318c1`) cancelled the merge-commit run. The replacement run is on `43318c1`,
  whose tree is `2abc62c` plus a docs-only commit — a strict superset. **That run is the one to
  read:** `gh run list --branch main --limit 3`. The identical tree passed locally
  (`1371 passed, 7 skipped, 1 xfailed`, 45:49), and **the `43318c1` run came back
  `completed/success` (run `33243170653`)** — so the merged tree IS verified green on CI, by the
  superset run rather than by its own.
  *Second-order consequence worth knowing: any push to `main` cancels the CI run of the commit
  before it, so a run seen green is only ever the run for HEAD.*
- **The merge bypassed CI unintentionally.** `gh pr merge --auto` is a no-op on this repo — there is
  no branch protection requiring checks, so it merged immediately rather than waiting. Assumed, not
  verified: that adding a required-check rule is desirable. Someone should decide.
- **"The defect rate is flat" is an IMPRESSION, not a measurement.** It comes from reading
  CLAUDE.md's own record (R73: 5 defects; next loop: a 6th; rules 6 and 7 added; this loop: 6). It
  has not been counted per *task*, which is the normalisation that might dissolve it entirely.
- **`R150` may not deserve a row.** One live instance, already declared in the same loop. If the
  register is to converge rather than accrete, this is the row to cut. Recorded as a judgement made
  at ~240k working tokens.
- **Census constants were re-measured four times** (53→55→57→56, and 55→54 restricted). Each step is
  attributed to the commit that caused it and the deltas are asserted by name, but this is the part
  of the loop most worth an adversarial read. **Check the deltas, not the totals.**
- The 150K executing floor remains labelled `NO SOURCE` in `tiers.py`. This session ran to ~259k
  working tokens against it.

## 5. The next concrete action

**Measure the defect rate before changing any rule.** One fresh session, all data local:

- defects per plan **per task** across the last ~8 loops, from the task reports in `git log`;
- register raise:close ratio over time, from the `(n/m closed)` snapshots read down the index;
- closures per loop — the velocity number that matters, not commits per day.

If it is flat or falling per task, the answer to the maintainer is "rigour, not regression" and the
8th rule is optional. If it is rising, that is when to test the stronger-model-for-specs hypothesis —
**not before**, because this loop's defect class was *foresight* (the plan author writes in a cleared
session by design and cannot foresee what execution discovers), and model strength closes a foresight
gap less than the 8th rule does.

Deferred, and independent of the above: **`R151`** — re-author `holon:02 → holon:01`. Its row carries
a falsifiable prediction that must be run *first*: the ablation that refuted the edge on 2026-08-22
should now **fail to reproduce**, because the membrane this loop shipped refuses what it used to pass.
