# Handoff: box-split Task 3d, SDD mid-flight (2026-09-30)

**Topic:** box-split · **Date:** 2026-09-30

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff).

Written at ~111K working tokens (plimslop hook), as an umbrella under the 150K executing floor —
before it was needed. The SDD ledger is the live record; this file only points at it.

## 5. Next action (written first)

- **Asserted.** Resume `superpowers:subagent-driven-development` on
  `docs/superpowers/plans/2026-09-28-box-split.md`, Task 3d, from the ledger's **"Session 10"**
  block in `.superpowers/sdd/2026-09-28-box-split/progress.md` (gitignored). Its last lines say
  which sub-task is complete, which is mid-review, and which fix round is queued. Briefs are built by
  `bash .superpowers/sdd/2026-09-28-box-split/mkbrief.sh 3d.N` (the 3d.2, 3d.6 and 3d.7 briefs carry
  appended controller rulings — regenerate only 3d.3–3d.5 if the plan changes, or re-append).
- **Proposed, and it may fail:** 3d.7's T2 answers `0`. A `1` is O2's finding (plan 3d.7 Step 1),
  and it also leaves four shapes idle in `test_vacuity_registry` (plan amendments, 3d.1).

## 1. Goal

Task 3d executed and reviewed, 3d.0 → 3d.7, then Task 4 Steps 4–5, 5, 6.

## 2. Where the primaries are

- **Plan:** Task 3d plus "Task 3d — amendments after review (2026-09-30)" (`f41ff6d`).
- **Spec:** `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.5, § 10.7.
- **Ledger:** `.superpowers/sdd/2026-09-28-box-split/progress.md`, "Session 10" block — pre-flight
  scan table, rulings, per-sub-task status. Reports and reviews sit beside it
  (`task-3d.N-{brief,report,review}.md`).
- **Evidence:** `docs/superpowers/2026-09-28-box-split-evidence.md` § 3 (3d.0's baseline, `84827f5`).

## 3. What was decided, and where it is recorded

- **A6 split in time** (controller ruling): 3d.2 measures merge-in with a band's pre-existing
  decisions; the statement-carrying U14 merge-in case is 3d.6's. Ledger + the 3d.2/3d.6 briefs.
- **`BoxheadAbsenceDecidedShape` also requires the `header_lines` judgement** (controller ruling,
  from 3d.1's review M1). Ledger only — reversible.
- Everything else is in the plan's amendments block.

## 4. Unverified or assumed

- Whether band decisions reach the document graph on `/r2` / `/adopt` merge-in (A6) — 3d.2's
  measure, pending when this was written.
- The 89 `tests/etkl` files outside 3d.1's measured set have not been run since `bf7057f`.
- Pre-existing red at `84827f5`, claimed by 3d.1's implementer, not re-run by the controller:
  `test_o3_no_page_loses_asserted_ink_to_a_merge` (cbh 43 < 54), `test_typing_equiv[cbh]`.
- Traps: implementers stall when they background pytest; corpus runs serial; `uv.lock` appears
  under `uv run`; two concurrent writers must never share this checkout.

## Addendum — handed off at ~145K working tokens (2026-09-30)

- **Done and reviewed clean:** 3d.0 (`84827f5`), 3d.1 (`bf7057f`, fix `b26457f`), 3d.2 (`8636883`,
  A6 does not land), 3d.3 (`4e6a284`, `e8416fe`). Ledger "Session 10" block has every ruling and
  deferred minor.
- **Next action (asserted):** SDD 3d.4, then 3d.5 — sequentially, since both add tests; then 3d.6,
  3d.7. Briefs exist; 3d.6 and 3d.7 carry appended controller notes (A6 case, the
  `_band_reading_subgraph` seam, C1).
- **Proposed, and it may fail — C1:** a table stated headerless could still carry a
  `tab:DerivedRowGroup` header node from chain derivation; possibly unrefused because the per-page
  membrane runs before the document pass. One query on the final corpus graphs in 3d.7 settles it.
- **Known-red corpus set** (not this task's): `test_o3…` cbh 43<54, `test_typing_equiv[cbh]`,
  furnish 5==4; vacuity red on 4 shapes by design until 3d.7.

## Addendum 2 — session 11 (2026-09-30), written at ~113K working tokens

**Next action (asserted):** if the ledger shows 3d.6 complete, dispatch 3d.7 from its brief (the brief
now carries session-11 controller notes); else finish 3d.6's review loop first. Then the final
whole-branch review.

- **Done:** 3d.4 `adfe828` (review clean), 3d.5 `8bf083e` (review clean), 3d.6 `9891f79` (review
  pending at time of writing). Every ruling and deferred minor is in the ledger, "Session 11" lines.
- **Where decided:** ledger `.superpowers/sdd/2026-09-28-box-split/progress.md` (gitignored — the
  commits above are the durable record); 3d.7's carried notes are appended to `task-3d.7-brief.md`.
- **Known-red set corrected:** it is 9 tests, not 5 — add `test_carriage` O2 ×2 (XPASS strict
  since Task 3c) and `test_cbh_e2e` ×2.
- **One live Haiku call was made** during 3d.5's falsification run (a synthetic fixture, nothing
  recorded). The tests were hardened afterwards. `ANTHROPIC_API_KEY` is set in the shell, so run
  tests with `env -u ANTHROPIC_API_KEY -u BAML_LIVE`.

**Unverified / proposed:**
- 3d.6 reports that a table asked on `/adopt` never reaches the document graph (the adopt pass
  rebuilds the page graph from the grid). If that holds, A6's merge-in exists only for `/r2`.
  Reviewer verdict pending.
- The reviewer's spec observation on 3d.4: condition 2 leaves rect fill blind to a shaded header
  over an unshaded body. The controller ruled that the spec stands. This is for the maintainer.
- `header_lines.baml`'s prompt ("count only") contradicts the required `note` field. 3d.7 must
  reword it before the first live call.

## Addendum 3 — session 11 end (2026-09-30), written at ~148K working tokens

**Next action (asserted):** dispatch the scoped re-review of 3d.7 fix round 1 (`fb3aca7..c65d545`,
docs only; the finding is in `task-3d.7-review.md` "Important 1"). If it is ADDRESSED, write
`Task 3d.7: complete` in the ledger, then continue SDD with Task 4 Steps 4–5 (O2 marker flip, cbh
re-pins **and** the bfs `DOC_TRIPLES_WHEN_CARRIED` 16736→16778 re-pin — evidence § 4.8 item 7),
then Tasks 5 and 6, then the final whole-branch review.

- **Done this session:** 3d.4 `adfe828`, 3d.5 `8bf083e`, 3d.6 `9891f79` (all reviewed clean);
  3d.7 `7fa2b22` + `fb3aca7` + fix `c65d545`. **T2 answered `0` live; O2's three tests XPASS(strict);
  vacuity is green.** Census = § 10.5's seven questions. Record: `docs/superpowers/2026-09-28-box-split-evidence.md` § 4.
- **Where decided:** ledger `Session 11` lines (gitignored); durable halves are in the evidence
  file § 4.6/§ 4.8 and the commits above.
- **Known-red now:** o3 cbh 43<54, typing_equiv[cbh], furnish 5==4, carriage O2 ×3 (XPASS strict,
  Task 4 flips), cbh_e2e ×2, carriage bfs_p5 16778≠16736 (Task 4 re-pins).
- **Controller rulings for the maintainer** (full list with costs in the ledger): the spec stands on
  condition 2 (rect fill is blind to a shaded header over an unshaded body); A6's `/adopt` half is
  empty by construction; 3d.7's sweep was cut to a targeted set (five files listed in § 4.8 item 9
  must join the Task 5 sweep).

**Unverified:**
- The rect-fill-under-unshown count is 0 but VACUOUS: `band.unshown` is empty offline.
- On headerless tables the `kind` decision's rationale still says "flat single-level header" (Task 5 list).
- `BAML_LIVE=1` also enables R213's region reader (Sonnet 5) and boxhead's live half. The plan's
  recipe does not say so.

## Addendum 4 — session 12 (2026-10-01), written at ~124K working tokens

**Next action (asserted):** Task 6's sweep and the final whole-branch review. Dispatch both from
`848925a` or later. The sweep brief is `.superpowers/sdd/2026-09-28-box-split/task-6-sweep-brief.md`
and expects **0 failed**. The final review goes to the most capable model and must triage the
ledger's `minor (deferred)` lines. Two are flagged must-triage: Task 4 M1 and 3d.4 M1. After that:
one fix wave, one scoped re-review, the PR corpus comment, and `finishing-a-development-branch`
(PR #284).

- **Done this session:**
  - 3d.7 fix round re-reviewed clean.
  - Task 4 Steps 4–5 (`14e4dab`, `4e04c29`, `9f50e03`): O2 flipped and `tab:12` met, the bfs pin
    moved to 16778, and o3 was re-pinned 54→43 (accounted).
  - Task 4 rulings (`d943519`, `8459473`, `caebd2b`): box title captions are `tab:RegionCaption`
    only (spec § 1). The residue (`1,951,264` + Note) is accepted as escalated
    KIND_NOT_SUPPORTED (spec § 4), and `typing_equiv` and furnish were re-pinned.
  - Task 5 (`5bfcb77`, `848925a`): C1 = 1 band. C2: apple and graincorp×2 match Task 0, and
    bfs/ons/who match the 3d.7 hashes. R261–R274 raised; R74 and R156 narrowed in place.
- **Where decided:** the ledger's session-12 `Ruling:` lines (gitignored) and evidence § 5–§ 6
  (tracked).
- **Known-red now:** none expected. The sweep is what shows it.

**Unverified:**
- The full suite has not been run since `9891f79`, and the Task 4 `src/` change (`Band.title_captions`)
  has only had targeted runs.
- CLAUDE.md names only `residues.md` as a mutable Evidence exception, while § Deferred residues
  prescribes in-place row edits in `residues-open.md`. This is a contract gap only the maintainer
  can resolve (Task 5 review M1).
