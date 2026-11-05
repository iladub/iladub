# Handoff 2026-11-05: the document router, Task 5 done, resume at Task 6

**Serves:** maintenance — project 2 of the contract:01 rescope (router).

Written at ~142K working tokens, under the 150K executing floor. The session stopped here because one
task cycle cost about 30K of controller context, and Task 6 would have crossed the floor. Earlier
state: `docs/superpowers/2026-11-03-document-router-execution-handoff.md`, whose §§ 3–4 still hold.

## 5. Next concrete action (typed)

1. **Asserted** (mechanical): resume superpowers:subagent-driven-development on
   `docs/superpowers/plans/2026-11-02-document-router.md`, branch `document-router-plan`, worktree
   `.claude/worktrees/contract-rung-spec`, PR #388 (DRAFT), at **Task 6**. The ledger
   `.superpowers/sdd/2026-11-02-document-router/progress.md` (gitignored, local) names the completed
   tasks and every ruling. Update the `Claude-Session:` trailer in `common.md` there before the first
   dispatch.
2. **Proposed** (may fail; costs a model pass): Task 9 Step 6, the boundary-oracle falsifier. Nothing
   in this session bears on its outcome.

## 1. Goal

Execute the router plan: split a text PDF into documents and type each one, traced, scored against
bar B1–B6.

## 2. Where the primaries are

- Plan and spec: as in the 2026-11-03 handoff. Tasks 6–10 and spec §§ 4–6 are what remains to read.
- Task 5 code: `src/iladub/route/proposers.py`, `baml_src/route.baml`, `tests/test_route_proposers.py`;
  commits b7b2ac1b, 57fa46a8, 8c8255bd.
- Task 5 report, with TDD and falsification evidence: `task-5-report.md` in the ledger directory.

## 3. What was decided, and where

All of these are recorded in the ledger; the code changes are in the commits above.

- **Reading keys hash every input of the question**, wider than the plan's key: `previous_tail` for
  boundary, the admitted list for doctype, each field length-prefixed. A recording must not replay
  under an input it never saw. Controller ruling; cost if wrong is extra live calls.
- **`default_proposers()`**: a RouterJev entry only if `jev_available()`, then RouterHaiku always, with
  `live=None` when `haiku_available()` is false, so a replay needs no key. Controller ruling.
- **A failed model call is "no answer"** (`None`, nothing recorded, retried next time). A missing
  client, a bad function name or an unknown model id raises. Found by review.

## 4. Unverified or assumed

- **No live call has reached `RouteBoundaryHaiku` or `RouteDoctypeHaiku`.** A test checks the generated
  field names; the prompts themselves first run in Task 9.
- **`proposed_type` is model-written and gets recorded**, so a model could echo page text into
  `readings/`. Nothing checks this yet. Task 9 must, before it commits readings (the no-template-text
  constraint). Deferred in the ledger.
- `tests/etkl/test_vacuity_registry.py::test_every_idle_shape_is_registered`: still not re-measured on
  `main` (2026-11-03 handoff § 4).
- This session ran only `tests/test_route_proposers.py` after the last fix (17 passed), plus the
  declaration, ownership, leak and governance tests at the first commit (35 passed with the models
  test). CI on the pushed branch is not yet read.
- **Task 6 interface notes:** `Proposer.boundary(listing, previous_tail)` and
  `.doctype(listing, admitted)` return `Proposed | None`; `Proposed.model` is the `route:modelId`.
  Proposers do not validate ids; the oracles dispose. The 2026-11-03 handoff's Task 6 notes still bind
  (persist rules to `RULES_PATH` under `--learn`; `check_boundary_split` signature; OTHER admitted by
  `route:ChecklistOracle`). `.ttl`/`.rq` pins are unchanged by Task 5.
- Everything from Task 6 onward.
