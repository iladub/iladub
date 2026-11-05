# Handoff 2026-11-03: the document router is mid-execution (subagent-driven)

**Serves:** maintenance — project 2 of the contract:01 rescope (router).

Written early (controller at ~120K working tokens), updated at ~138K when the session stopped after
Task 4 to stay under the 150K executing floor. **Tasks 1–4 are complete and reviewed; resume at Task 5.**

## 5. Next concrete action (typed)

1. **Asserted** (mechanical): resume superpowers:subagent-driven-development on
   `docs/superpowers/plans/2026-11-02-document-router.md`, branch `document-router-plan`, worktree
   `.claude/worktrees/contract-rung-spec`, PR #388 (DRAFT). The SDD ledger
   `.superpowers/sdd/2026-11-02-document-router/progress.md` (gitignored, local) names every completed
   task and every ruling; resume at the first task without a `Task N: complete` line. If the ledger is
   gone, `git log` on the branch is the record (one `feat(route)` commit per task, plus `fix(route)`).
2. **Proposed** (may fail; costs a model pass): Task 9 Step 6, the boundary-oracle falsifier. The
   oracle was tightened in Task 3 (below), so the plan's prediction was strengthened, not proven.

## 1. Goal

Execute the router plan: split a text PDF into documents and type each one, traced, scored against
bar B1–B6.

## 2. Where the primaries are

- Plan / spec: `docs/superpowers/plans/2026-11-02-document-router.md`, `specs/2026-11-02-document-router-design.md` (merged #387, ee9515e7).
- Code so far: `src/iladub/route/{models,lines,oracle}.py`, `vocab/ontology/route*.ttl`,
  `vocab/shapes/route-shapes.ttl`, `vocab/queries/route-{checklist,boundary}.rq`.
- Worktree setup: `.venv`, `corpus`, `held-out` are symlinks to the main checkout (gitignored).

## 3. What was decided, and where

- PR #387 squash-merged by the controller with the owner's OK (in chat, 2026-11-03).
- **Jev out of this loop**: docs.typesafe.ai documents only a native `POST /v1/systemone` API, no
  OpenAI-compatible endpoint; BAML 0.222 has no TypeSafe provider. `jev_available()` is `False`;
  Haiku decides alone. Recorded in `src/iladub/route/models.py` and the Task 1 commit. Residue owed in Task 10.
- **Split oracle tightened against the plan** (spec § 8 binding): the disjoint-party-lines arm is
  removed (a reviewer reproduced it admitting a single contract's continuation); a same-kind split
  needs a restart whose start-line text occurs nowhere else in either extent (kills running headers).
  Contradictory answers are refused; the two party lines must differ in text. Recorded in
  `vocab/queries/route-boundary.rq` / `route-checklist.rq` header comments and commits 7ec897c9,
  4d6a788d. Cost: two back-to-back different contracts of one kind (m2) are refused, not split.
- "Not a contract" answers are admitted by `route:ChecklistOracle` too (one oracle per doctype
  question): recorded only in the ledger and in Task 6's dispatch.

## 4. Unverified or assumed

- A 2-page PDF with the same header on both pages can still be split at page 2 if both pages pass
  the contract checklist independently (accepted residual).
- `tests/etkl/test_vacuity_registry.py::test_every_idle_shape_is_registered` (corpus-marked) fails on
  `tab:StackedGridsShape` — believed pre-existing from R74, not re-measured on `main`.
- **Task 4 additions** (commits 6b4b4cfd, ed2ef3b1): rules scale (1.44 s at 100 rules / 250 lines,
  not timing-pinned); **extent-level conflict** (controller ruling, recorded in the ledger and
  `vocab/queries/route-extent-conflict.rq`): a learned rule is conflicted when all its cue shas occur
  in a learned extent of the opposite kind, so a boilerplate "not a contract" cue cannot fire on a
  contract. Residual: a contract template never seen in learning is unprotected; Task 9 B3 measures it.
- **Task 6 must persist** the rules graph to `RULES_PATH` (`readings/route/rules.ttl`) under `--learn`;
  `rules.py` write-back mutates only the in-memory graph.
- **Task 6 interface notes:** `check_boundary_split(prev_extent, prev_doctype, next_extent, next_doctype,
  *, admitted_types=frozenset())`; OTHER doctype answers are admitted by `route:ChecklistOracle`
  (membrane S3 requires an `admittedBy` on every non-refused, non-Given decision).
- Pins at handoff: `.ttl` 265, `.rq` 64 (four pin files: `test_artifact_declarations`,
  `test_artifact_terms`, `test_query_terms`, `test_query_declarations`).
- Everything Task 5 onward.
