# `holon:05` — the loop ledger (preserved SDD evidence)

**Topic:** the complete decision record of the `holon:05` membrane-health loop — every ruling,
deferred minor, measurement and process failure, across four controlling sessions.

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Class:** Evidence (immutable after loop close).

**What this is.** A verbatim copy of the subagent-driven-development ledger that governed this loop,
taken at the close of the fourth session. The working copy lived at
`.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md`, inside a **git-ignored**
workspace that the SDD process deletes when the loop closes. This copy exists because that deletion
would otherwise destroy the only record of ~20 rulings taken on the maintainer's behalf and ten
measured process failures — including four by the controllers themselves.

**Why it is here and not tracked in place.** `.superpowers/sdd/` carries a deliberate `*` gitignore,
and the documentation-governance membrane requires every tracked markdown file to carry exactly one
class by path (`tests/docgov_extract.py`, `classify()`). A ledger tracked at its working path
classifies as nothing and hard-fails `test_doc_governance.py::test_membrane` — measured, not assumed:

```
Focus Node: …/doc/.superpowers/sdd/…/progress.md
Message: every tracked markdown file must belong to exactly one class (spec §3)
Constraint: MinCountConstraintComponent on dg:docClass
```

`docs/superpowers/` classifies as Evidence, which is what a loop ledger is.

**How to read it.** Tasks with a `Task N: complete` line are done. Lines containing `Ruling:` are
decisions taken without the maintainer present — that set is the most important thing in the file.
Lines containing `minor (deferred):` are findings triaged to the final review. **Re-count rather than
citing any figure in here**: the ledger's own counts are themselves a recorded instance of this
branch's signature failure, a load-bearing claim made from reading rather than measuring.

---

# SDD ledger — plan: docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md

Spec: docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md (reachable, twice amended)
Branch: holon-05-plan. Runner: ./.venv/bin/python -m pytest (NEVER python3).

## Pre-flight conflict scan (2026-08-25)

### Cross-task rows (every pair sharing a file or interface)

| pair | produced vs consumed | finding |
|---|---|---|
| T1 → T2 | `etkl:MembraneValidation`, `etkl:refusingLeg` minted by `_seal` | clean |
| T1 → T3 | `etkl:CompiledDocumentHolon` typed by the `.rq` | clean |
| T1 → T5 | `CompiledDocumentHolon` as `sh:targetClass`; T5 passes `etkl-holons.ttl` as ont graph (M7) | clean |
| T1 → T6 | `iladub:` terms only; T1's terms not in the registry population | clean |
| T1 → T7 | T7 Step 4 rewrites `arc-manifest.ttl:1337`'s citation to `etkl-holons.ttl:75-89` | **CONFLICT — see R-PF1** |
| T2 → T3 | `_seal`, `MEMBRANE_HEALTH_RQ`, the validation act | **AMBIGUITY — see R-PF2** |
| T2 → T4 | `MembraneRefusal(.graph,.legs)`, `_seal`, re-entry idempotence | clean |
| T3 → T4 | health triple + type triple on both paths | clean |
| T3 → T6 | `membrane-health.rq` is row 1 of the query vacuity dict | clean |
| T2/T3/T4 → same test file `tests/etkl/test_membrane_health.py` | T2 creates, T3 and T4 extend; disjoint function names | clean (strictly ordered 2→3→4) |
| T5, T6, T7 pairwise | disjoint files | clean |
| all → T7 | evidence for the manifest flip and the register | clean |

### Per-task self-consistency rows

| task | its tests vs its code, its creates vs its later touches | finding |
|---|---|---|
| T1 | no new test; falsifies the parse arm — self-consistent | clean |
| T2 | 5 tests; all import only what Steps 4-5 produce; `MEMBRANE_HEALTH_RQ` declared but unused until T3 | see R-PF2 |
| T3 | 5 tests; every setup measured constructible in M5 (rows A-G) | clean |
| T4 | 6 tests; asserts against T2/T3 as shipped; one unmeasured string literal | **see R-PF3** |
| T5 | shape + 3 fixtures + 2 functions; note flags the missing `pytest` import | clean |
| T6 | branch on a measurement; fallback named | clean |
| T7 | record only | see R-PF1 |

### Rulings taken before execution

- **R-PF1 (T1↔T7 line drift).** Ruling: Task 7 Step 4's `75-89` range is computed against
  `etkl-holons.ttl` BEFORE Task 1 appended three terms and reworded two `rdfs:comment`s. Task 7 must
  RE-MEASURE the `etkl:MembraneHealth` block's true range in the file as it then stands and write that,
  not transcribe `75-89`. — Why: a correction that is itself stale is worse than the error it fixes.
  — Cost if wrong: an off-by-N citation in a residue row and in `arc-manifest.ttl:1337`; cosmetic,
  correctable in one commit.
- **R-PF2 (T2's `MEMBRANE_HEALTH_RQ` points at a file Task 3 creates).** Ruling: Task 2 declares the
  module-level `Path` constant only; nothing reads the file at import time, so the dangling path is
  inert until Task 3 writes it. Task 2 must NOT run the query and must NOT create a stub `.rq`.
  — Why: `ESCALATION_FURNISH_RQ` at `document.py:130` is the precedent and is a bare `_QUERIES / …`.
  — Cost if wrong: an ImportError/FileNotFoundError surfaces immediately in Task 2 Step 6, and the
  constant moves to Task 3.
- **R-PF3 (T4's refusal-message literal).** `test_the_refusal_carries_the_graph` asserts
  `str(exc.value).startswith("document-level facts failed dec: SHACL:")`. That prefix is NOT among the
  plan's measurements. Ruling: Task 4 MEASURES `_refusal_message`'s actual format before writing the
  assertion and uses the real prefix, keeping the assertion's force (the message is unchanged by the
  subclass). — Why: Global Constraint 7 — a plan-supplied literal is a proposition.
  — Cost if wrong: one red test in Task 4 with an obvious diff.
- **R-PF4 (O11 is defined twice, incompatibly).** § Rule-5 reconciliation says *"O11 asserts the page
  site is UNCHANGED"*; Task 2's test and M9 and the handoff all say O11 is the `MembraneRefusal`
  subclass check. Ruling: **O11 = the subclass check** (three sources against one). No test asserting
  "the page site is unchanged" is owed; the plan's *Not touched, deliberately* list plus the branch
  diff carries that. — Cost if wrong: one absent regression test on `compile.py:1173`, which no task
  edits.

## Progress

Task 1: complete (commit a0dd528, done in the prior session per the handoff; falsification recorded there — deliberate Turtle syntax error made tests/test_source_ownership.py:68 FAIL, restored -> 13 passed in 0.60s)
Task 2: dispatched (implementer opus, agent a7069d1b47eaa2506) — BASE 2529983
R-PF1 RESOLVED (controller measurement, post-Task-1 HEAD 2529983):
  $ sed -n '75p;89p' vocab/ontology/etkl-holons.ttl
  75: etkl:MembraneHealth a owl:Class ;
  89:     rdfs:comment "The membrane-health signal computed for this holon."@en .
  Task 1 appended AFTER the block (new terms at :96,:101,:106) and its two amendments stayed
  single-line, so the block did NOT drift. `75-89` is correct as the plan writes it. Task 7 still
  re-verifies, but the expected answer is now known.
Task 2: implementer DONE_WITH_CONCERNS (commit d6c3d49; 59 passed in 329 s; report task-2-report.md)
  - S6 answered: recognized/section_facts NOT mutated before :1609; the (graph, legs, validate_shapes) signature stands.
  - S3 answered: id(graph) identical at furnish / after += / at DocumentReport / on the returned report, before AND after the extraction.
  - PLAN DEFECT FOUND by the implementer: the brief's O10 test passed with `graph.remove` deleted
    (unmutated re-entry reaches the SAME verdict, and an rdflib Graph is a set, so the duplicate
    collapses). Substituted a form driven by the measured seam-6 lever; original assertion kept under
    the name test_re_entering_an_unmutated_graph_is_a_no_op. Controller read both bodies: the
    substitution is STRONGER, not weaker.
  - Implementer concern 2: plan M2's interceptor count does not reproduce — 7, not 17. The substantive
    claim (all isinstance-based, zero `type(e) is`) holds and is stronger. Recorded, not blocking.
  - Implementer concern 4: one ruff F401 (the brief's own unused `_validate` import, kept for Task 4).
    Controller check: CI runs no linter (.github/workflows/ci.yml has only the pytest step), so this is
    cosmetic. Task 4 consumes the import.
R-PF3 RESOLVED as a side effect: the substituted O10 test asserts
  str(exc).startswith("document-level facts failed dec: SHACL:") and PASSES, so the plan's literal —
  unmeasured at plan time — is measured correct. Task 4 may use it as written.
Task 2: task reviewer dispatched (opus, agent a07f2891d6d907eff) over 2529983..d6c3d49
Task 2: review APPROVED, spec compliant. Reviewer independently reproduced the set-collapse mechanism
  behind the plan defect and confirmed the substitution is strictly stronger; also verified all seven
  moved-comment file:line citations are exact.
Task 2: fix round 1/5 dispatched (resumed implementer a7069d1b47eaa2506) — 1 Important + 2 Minors:
  (1) IMPORTANT: `(act, rdf:type, etkl:MembraneValidation)` and `(act, prov:used, _DOC)` are minted but
      pinned by NO standing test — delete either and all six tests stay green. Task 3's derivation keys
      on the type triple, so this fails upward exactly like B6. Two assertions + their own falsification.
  (2) Minor: the validate_shapes=False early return does not clear a stale act; Task 4 calls _seal
      directly. One-line comment only, behaviour unchanged.
  (3) Minor: the O10 docstring names R127's mechanism but not R127 (GC10 + Task 7's record).
Task 2 minors DEFERRED (in the ledger, not the loop), for the final whole-branch review to triage:
  - Reviewer minor 2: report prose cites pre-change lines :1368/:1572; the diff's uniform +120 offset
    makes them :1366/:1570. Committed comment unaffected. Implementer corrects the prose only.
  - Reviewer minor 6: MembraneRefusal is not reconstructible from `args` (an uncallable pickle). Not
    live: no xdist, no addopts, nothing pickles exceptions across processes here.
Task 2: Ruling — the F401/unused imports (`_validate`, `ILADUB`, `PROV`) in the test file STAY.
  Why: the plan's own Task 3 and Task 4 tests use all three verbatim (test_the_minted_nodes_perturb_no_
  verdict calls _validate; ILADUB and PROV appear in Task 3's discriminate test and Task 4's O3), and CI
  runs no linter. Cost if wrong: three dead imports if Tasks 3-4 are later rewritten to not use them.
Task 2: Ruling — two Minors (2,3) were folded into the round-1 fix dispatch rather than deferred.
  Why: both are one-line comment edits inside the code the Important finding already reopens, so they
  extend no round; and (3) documents Global Constraint 10's coupling, which Task 7 must record anyway.
  Cost if wrong: a slightly larger fix diff for the scoped re-review to read.
Task 2: fix round 1/5 committed d8d22c9 (3 findings claimed closed; falsifications (e) and (f) added:
  each mint line deleted in turn -> `1 failed, 5 passed`, restored green; before the fix both deletions
  produced `6 passed`). Scoped re-review dispatched (sonnet, agent adca772bda5ad5974) over d6c3d49..d8d22c9.
CONTROLLER HANDOFF written at 144k tokens (executing floor 150k, five tasks left):
  docs/superpowers/2026-08-25-holon-05-task-3-handoff.md — points at THIS ledger as the recovery map.
  Tasks 3-7 resume in a FRESH session. All seven briefs are already generated in this directory.
Task 2: fix round 1/5 (3 addressed, 0 open — act type+prov:used now pinned; early-return comment;
  R127 named in the O10 docstring; commits d6c3d49..d8d22c9). Re-review: no new breakage, additive only.
Task 2: complete (commits 2529983..d8d22c9, review clean)
NEXT: Task 3 in a FRESH session. Entry point: docs/superpowers/2026-08-25-holon-05-task-3-handoff.md

## Session 2 (fresh controller, resumed at Task 3)

Task 3: dispatched (implementer opus, agent ae37bf33cf8560755) — BASE f33db9f
Task 3: implementer DONE_WITH_CONCERNS (commits d3fd206, b91e152; 37 passed across
  test_membrane_health.py + test_transform_gate.py + test_document.py; report task-3-report.md)
  - PLAN GAP FOUND (concern 1): M9's replace-don't-accumulate hazard hits the HEALTH triple too, not
    only the act. Measured: a re-entered refused graph carried Weakened AND Compromised at once — the
    exact collision spec §4.3 invariant 3 names, reached by RE-ENTRY rather than by union. Implementer
    added `graph.remove((_DOC, ETKL.membraneHealth, None))`, a pinning test
    (test_re_entering_the_seam_leaves_exactly_one_health_value) and a fourth inversion (d).
  - Concern 4: inversion (b) recorded the silent value — a `false` verdict with a slipped datatype
    reports **Intact** (and Weakened on a real refusing document). B6's failure-upward, confirmed.
  - Concern 3: O5 pins "the stored value equals the derived one", not "it was derived" — the
    implementer's first attempt at inversion (c) stored a hand-coded Python equivalent and all 12
    tests passed. NOT patched: the brief states O5 is explicitly not the falsifying oracle and O1 is
    (inversion (a) proves O1 does its job). Recorded for the final review.
TASK 2 REGRESSION — CONFIRMED BY THE CONTROLLER, not merely reported.
  Concern 2 claimed tests/etkl/test_document.py::test_single_page_document_matches_compile_tables was
  ALREADY failing at f33db9f, i.e. Task 2 shipped it. Verified directly:
    $ git checkout f33db9f -- src/iladub/etkl/document.py tests/etkl/test_document.py
    $ ./.venv/bin/python -m pytest -q tests/etkl/test_document.py::test_single_page_document_matches_compile_tables
    E  AssertionError: assert 329 == 326
    1 failed in 5.26s        (then restored to HEAD; tree clean)
  So Task 2's "complete, review clean" line stands for its own diff but NOT for the branch: its
  scoped review ran nothing wider than its own file, and the +3 validation-act triples broke a
  parity test in another file. CONSEQUENCE: the plan's suite baseline (1312 passed) is NOT a clean
  comparator — Task 7 Step 6 must treat a delta as a finding to attribute, not as noise.
  tests/test_corpus*.py and tests/etkl/test_cbh_e2e.py have still not been run on this branch.
Task 3: Ruling — the pre-existing-failure repair in the SEPARATE commit b91e152 STANDS, and the
  out-of-brief file (tests/etkl/test_document.py) is accepted scope. — Why: the branch cannot be green
  without it; the repair ENUMERATES the five seal triples and subtracts them rather than relaxing the
  equality to `>=`, so it keeps pinning the thing that test exists for; and it is inside the range the
  task review reads. — Cost if wrong: a scope-creep finding on a 24-line test change the reviewer sees
  anyway.
Task 3: Ruling — concern 1's extra `graph.remove` + test + inversion (d) are ACCEPTED as a plan-gap
  repair, not scope creep. — Why: spec §4.3 invariant 3 forbids two health values on one subject, and
  the implementer MEASURED the collision arising by re-entry; the brief's Step 4 wording simply did
  not cover it. — Cost if wrong: one redundant remove line and one redundant test.
Task 3: task reviewer dispatched over f33db9f..b91e152
Task 3: review NEEDS FIXES — 1 Important, 6 Minors. Reviewer measured (not read) that deleting the
  `FILTER NOT EXISTS` from membrane-health.rq leaves ALL 12 tests green: only a REVIEWED candidate
  discriminates (as-shipped Intact vs filter-deleted Weakened) and no test builds one. So spec §4.3
  invariant 2 — the one clause §4.3's last paragraph says explicitly "STAYS" — ships unfalsified, the
  .rq header block that should name its pinning test names none, and the report's traceability row
  for invariant 2 is FALSE. Reviewer also independently confirmed the two controller rulings were
  right: removal-then-mint is above `if not conforms` so both paths are identical, and the TYPE triple
  correctly needs no removal (constant object + graph-is-a-set + the datatype filter cannot fail at
  this site).
Task 3: Ruling — Minors 2, 3 and 6 are FOLDED into the round-1 fix dispatch; Minors 4, 5 and 7 are
  DEFERRED to the final whole-branch review. — Why: 2 (no inversion evidence for `len(seal) == 5`),
  3 (one sentence on the stale-health re-entry) and 6 (a citation pointing at a loop-scoped file) are
  each one line inside files the Important finding already reopens, so they extend no round — the same
  reasoning taken for Task 2's Minors 2 and 3. — Cost if wrong: a slightly larger fix diff.
Task 3: minor (deferred): Minor 4 — the re-entry collision argument is DERIVED three times
  (membrane-health.rq:339-343, document.py:1290-1303, test_membrane_health.py:240-260) instead of once
  plus two citations; document.py grew 37 lines for 2 lines of code. Ruling on why it is deferred and
  not folded: CLAUDE.md rule 6 as written is a SPEC finding about plans, and its prescribed remedy is
  upstream; this is the code-comment analogue, which the rule does not cover and which the final review
  is better placed to weigh across the whole branch. — Cost if wrong: ~30 lines of restated comment
  survive into main.
Task 3: minor (deferred): Minor 5 — test_membrane_health.py:188-189's set-cardinality assertion is
  entailed by the three equality assertions above it; it reads as an independent check and is not one.
  Deferred rather than folded because the line is PLAN-SUPPLIED verbatim and deleting plan text needs
  the final review's whole-branch view.
Task 3: minor (deferred): Minor 7 — O5 pins the QUERY, not `_seal`'s USE of it. Nothing in the suite
  distinguishes "derived by membrane-health.rq" from "a Python reimplementation that agrees"; CLAUDE.md
  §8's gate is the only thing standing there. The reviewer agrees the implementer was right not to
  silently strengthen a brief-declared non-oracle, and states the residual hole precisely.
Task 3: reviewer ⚠️ item, controller-resolved — "every test comparing a document graph to a page graph
  is now off by five, and tests/test_corpus*.py were never run on this branch". NOT closed: controller
  launched tests/test_corpus*.py + test_cbh_*.py in the background at b91e152 to get the first real
  branch-wide reading. Result lands in this ledger before Task 7.
Task 3: fix round 1/5 dispatched (resumed implementer ae37bf33cf8560755) — 1 Important + 3 folded Minors.
Task 3: fix round 1/5 committed b704ccc (Important 1 + folded Minors 2,3,4 claimed closed; 38 passed
  in 36.13 s; inversions (f) and (g) shown failing and restored). Implementer accepted that its own
  invariant-2 traceability row was WRONG and struck-and-corrected it in place — it did not defend it.
  Judgement it was asked to make and did: the new pin is a SEPARATE test,
  test_a_reviewed_candidate_no_longer_weakens_the_membrane, not a fourth graph inside
  test_the_three_values_discriminate — because that test's closing assertion counts three distinct
  values (and is itself under deferred Minor 5), and because a DECIDED proposition no longer being
  held is a different claim in kind. Scoped re-review dispatched (sonnet, agent a0f840056de22db05)
  over b91e152..b704ccc.
CORPUS BASELINE (controller, background): `./.venv/bin/python -m pytest -q tests/test_corpus.py
  tests/test_corpus_stem.py tests/test_cbh_e2e.py tests/test_cbh_contract.py
  tests/test_corpus_battery_unit.py tests/test_corpus_manifest.py` -> **49 passed in 641.44s**.
  CAVEAT, stated because it is load-bearing: the run STARTED at b91e152 and the fix round mutated the
  working tree (including vocab/queries/membrane-health.rq, which `interpret.run` reads at RUNTIME,
  not at import) while it was in flight. So this is INDICATIVE — Task 2's +3 act triples broke nothing
  in the corpus files — and NOT a pinned-commit baseline. Task 7's full-suite run is still the
  measurement of record. Note tests/etkl/test_cbh_e2e.py does not exist; the file is tests/test_cbh_e2e.py.
CONTROLLER HANDOFF written at 125k tokens (executing floor 150k, four tasks left):
  docs/superpowers/2026-08-25-holon-05-task-4-handoff.md — supersedes the task-3 handoff, and points
  at THIS ledger as the recovery map. Tasks 4-7 resume in a FRESH session.
Task 3: fix round 1/5 (4 addressed, 0 open — invariant 2 now pinned by
  test_a_reviewed_candidate_no_longer_weakens_the_membrane, the .rq header names it and carries the
  four-state measurement inline, the false traceability row is STRUCK not overwritten, and Minors 2-4
  closed; commits b91e152..b704ccc). Re-reviewer ran the crux test in isolation (green), confirmed
  FALSIFICATION (f) reproduces the previous reviewer's four-state measurement exactly, and verified
  the three deferred minors were left untouched. New breakage: none — the diff is comment-only in
  document.py and the .rq plus one self-contained test.
Task 3: complete (commits f33db9f..b704ccc, review clean)
NEXT: Task 4. Entry point: docs/superpowers/2026-08-25-holon-05-task-4-handoff.md
Task 4: dispatched (implementer opus, agent a15d2f8eb3763bf82) — BASE b704ccc
  Controller measurement handed over: all three corpus PDFs the brief names are PRESENT
  (ag-trade/graincorp-stem-2026-07-31.pdf, financial/apple-fy2026q3-statements.pdf,
  gov-stats/bfs-population-bilan-2023.pdf), so the two @pytest.mark.corpus legs must RUN, not skip.
  Also handed over: the brief's O7 docstring copies plan M2's WRONG "17 interceptors" — implementer
  told to write 7 with the measuring command, not to transcribe a number known to be false.
CONTROLLER SCOPE (user directive, 2026-08-25, at 155k tokens / 150k executing floor, override logged):
  finish Task 4 — implementer, task review, fix rounds if needed, completion line — then HAND OFF.
  Tasks 5, 6 and 7 are explicitly NOT to be started in this session.
Task 4: implementer DONE_WITH_CONCERNS (commit 8b2aaf6; one file, +251/-0, NO production code;
  19 passed in 217.65 s; the two -m corpus legs RAN, did not skip — 2 passed, 17 deselected in
  202.63 s; six falsifications, each red then restored then green; report task-4-report.md)
  - S1 ANSWERED: apple's R127 lever DOES refuse (legs=('dec',), .graph is g, Compromised). The
    bfs -> apple substitution — the only edit this task authorised — is TAKEN. The two legs share one
    module-scoped compile; the third leg mutates a triple-identical copy.
  - S2 ANSWERED: target read off the graph, sorted(...)[0] of non-superseded dec:escalatedTo subjects
    (apple #region2-d3 of 10; cheap doc #region0-d4 of 1). ZERO region URIs in the committed file.
  - PLAN DEFECT FOUND (concern 1): the brief's `== [ETKL.Intact]` control arm is WRONG on all three
    candidate vehicles — cheap doc, bfs and apple all measure Weakened — and for the cheap doc it
    contradicts a Task-3 assertion one screen up in the same file. Substituted with the stronger
    INVARIANCE form (health before == health after, plus sh:conforms == [True]) plus a measured
    Weakened -> Compromised transition on the apple leg. The reviewer must judge whether the
    substitution is stronger or merely different.
  - Concern 2: FOUR shipped tests now ride R127, not two. Task 7 must record the corrected count —
    Global Constraint 10 says closing R127 without re-homing these turns them red for an invisible
    reason, and the blast radius just doubled.
  - Concern 3 (cosmetic, NOT edited — outside this task's authorisation): the Task-2 docstring's
    census command now returns 9 while its text says 7; the correct 7-reproducing form is in the new
    O7 docstring. Deferred to the final whole-branch review.
Task 4: task reviewer dispatched over b704ccc..8b2aaf6
Task 4: review APPROVED, spec compliant. Reviewer verified independently: zero hardcoded region URIs
  (grep for region[0-9]+-d[0-9]+ -> no matches); the shared apple compile CANNOT leak mutation
  (DocumentReport.graph is a plain rdflib.Graph so `+=` is a total triple copy, and _legs_for_document
  is pure over an immutable tuple); O2's reachability legs still NAME both values (Intact :416,
  Weakened :418); and the R127 coupling count of 4 is right.
Task 4: THE SUBSTITUTION IS STRONGER — ruled by the reviewer, not merely accepted. The re-entry control
  arm at :487-495 is a strict SUPERSET of the brief's: it keeps the no-op verbatim AND names the health
  value at :491 (so the "unchanged is weaker than named" objection does not bite), then adds invariance
  and the conformance verdict the brief never checked. The plan defect is verified real at
  test_membrane_health.py:386 — a SHIPPED Task-3 assertion 81 lines above already asserts
  == [ETKL.Weakened] on the identical vehicle, so the brief contradicted a measurement in its own file
  (CLAUDE.md rule 5's failure mode exactly). One correction to the implementer: its report's claim that
  the Compromised arm carries "strictly more" force is OVERSTATED — Weakened->Compromised and
  Intact->Compromised are structurally identical; the substitution's merit is that it is TRUE.
Task 4: Ruling — the one Important finding is a CARRY-FORWARD to Task 7, not a Task 4 fix round.
  **R127 HAS NO RESIDUE-REGISTER ROW AT ALL.** Controller verified: `grep -c R127
  docs/superpowers/residues.md docs/superpowers/residues-open.md` -> 0 and 0; the register tops out at
  **R126**. So "R127" is a label this loop's own spec and plan invented for a residue that was never
  registered, while Global Constraint 10 says it "must survive this loop intact" and FOUR shipped tests
  now ride it. Task 7 must CREATE the row (not update one), recording 4 coupled tests and naming them,
  because CLAUDE.md directs a maintainer to read residues.md in full and R127 is not in it. — Why a
  carry-forward and not a fix round: Task 4's brief authorises no doc edits and Task 7 is the record
  task; reopening Task 4 to write a register row would put the edit in the wrong commit. — Cost if
  wrong: the row lands one task later than it could have; if Task 7 also misses it, closing R127 later
  turns four tests red for an invisible reason.
Task 4: minor (deferred): the substitution's one ADDED assertion (:495, sh:conforms == [True]) is the
  one with no inversion — falsification (c) was run only under `-m corpus`, which deselects that
  non-corpus test. Cheap to close: re-run (c)'s inversion without `-m`.
Task 4: minor (deferred): the O7 docstring's census of 7 is defined by an exclusion
  (`grep -v test_membrane_health.py`) that hides one GENUINE interceptor at :579. True repo-wide count
  of real isinstance-based sites is **8**; the command returns 7 with the exclusion and 12 without.
  M2's substantive claim (zero `type(e) is`) is unaffected.
Task 4: minor (deferred): :495 partially duplicates a shipped Task-2 assertion at :163-165, which
  slightly deflates the new docstring's claim at :485-486 that the plan "never checked" the verdict —
  the plan didn't, but the file already did.
Task 4: minor (deferred): the Task-2 docstring's census command at :106-108 returns 9 against its
  stated 7 (two of its own lines self-match). Reviewer AGREED with the implementer's call to leave a
  shipped Task-2 docstring alone; belongs to the whole-branch review.
Task 4: complete (commits b704ccc..8b2aaf6, review clean, 1 carry-forward + 4 deferred minors)
NEXT: Task 5, in a FRESH session. Entry point: docs/superpowers/2026-08-25-holon-05-task-5-handoff.md

## Session 3 (fresh controller, resumed at Task 5)

Task 5: dispatched (implementer sonnet, agent ac2202e1f07b64518) — BASE 6ccf1c5
  Model choice: sonnet, not opus. Why: both test functions are supplied verbatim, the shape is
  quoted from spec §4.8, and the only authored artefacts are three small Turtle fixtures. Cost if
  wrong: one weak fix round, escalated to opus at round 4 per the skill's Model Selection.
  Controller measurements handed over so the implementer need not re-derive them: etkl-holons.ttl
  declares MembraneHealth :75, Intact :79, Weakened :81, Compromised :83, membraneHealth :86,
  CompiledDocumentHolon :96; test_vocab_shapes.py imports only os/rdflib.Graph/pyshacl.validate
  (the brief's missing-pytest note is CORRECT); etkl-shapes.ttl already prefixes etkl/sh/xsd/rdfs.
  Told to MEASURE, not trust: M6 (etkl-shapes.ttl not loaded by the compile membrane — the whole
  safety argument for the file choice) and M7 (no glob/parametrize). Also told the four EXISTING
  tests in that file now validate against the new shape and must stay green — if one reddens, the
  brief's vacuity argument is wrong and it is a finding, not something to route around.
CONTROLLER RULING (new, found while Task 5 ran — a pre-flight-scan MISS): **T6 and T7 are NOT
  file-disjoint on the fallback branch.** The pre-flight table's "T5, T6, T7 pairwise disjoint files"
  row assumed Task 6 SHIPS the tripwire. Task 6 Step 2's named fallback (spec §4.9) writes a RESIDUE
  ROW — into docs/superpowers/residues.md + residues-open.md, the same two files Task 7's carry-forward
  R127 row goes in, and Task 6 runs first.
  Ruling: **R127 is RESERVED for the second-`dec:rationale` residue this loop's spec already named.**
  If Task 6 takes the fallback, its row is **R128**, and it must not claim the next free number
  blindly. — Why: "R127" is not a free number, it is a LABEL already cited in 10 committed places —
  tests/etkl/test_membrane_health.py:53,78,203,205,211,369,381,382,434,437 (10 docstring lines across
  the 4 coupled tests), src/iladub/etkl/document.py:1309, and three loop docs. Renumbering it would
  falsify all of them. — Cost if wrong: two register rows land in the opposite order; a one-commit
  renumber, but only if caught before the docstrings are cited elsewhere.
CONTROLLER MEASUREMENT for Task 7 (taken now so Task 7 need not re-derive, but MUST re-verify because
  Task 6 may add a row first): docs/superpowers/residues.md holds **116 rows, 24 closed, 92 open**;
  highest number is **R126**; `grep -c R127 residues.md residues-open.md` -> 0 and 0 (the handoff's
  claim reproduces). The tally snapshot a new row carries is therefore `R127 (24/116 closed)` — unless
  Task 6's fallback lands first, in which case it becomes `(24/117 closed)`.
Task 5: implementer DONE (commit f1a92f5; 5 files, +71; tests/test_vocab_shapes.py 7 passed = 4
  pre-existing + 3 new; test_source_ownership.py + test_doc_governance.py 7 passed). No concerns
  raised. Claims: M6 and M7 both measured TRUE; BOTH plan-supplied test functions satisfiable
  VERBATIM — the first task on this branch to need no substitution; both inversions (delete
  sh:maxCount 1, delete sh:in) shown failing then restored. Report task-5-report.md.
Task 5: task reviewer dispatched (sonnet, agent aa5ee3d6c081538c3) over 6ccf1c5..f1a92f5.
  Attention lens given, beyond the standard constraints: (a) the ont graph MUST be etkl-holons.ttl,
  not etkl.ttl — the brief's own named silent-failure mode, since etkl.ttl does not declare
  CompiledDocumentHolon and the negatives would then pass VACUOUSLY; (b) each negative fixture must
  violate exactly and only the constraint its filename claims; (c) the shape must NOT be wired into
  the compile membrane. No findings were pre-judged.
Task 5: review APPROVED, spec compliant, ZERO Critical and ZERO Important. Reviewer re-verified
  independently rather than re-reading the report: `grep -rn "etkl-shapes\.ttl" src/` returns nothing
  and none of the three shape-file lists (_TAB_SHAPE_FILES/_DEC_SHAPE_FILES at compile.py:398,421,
  _GROUND_SHAPE_FILES at feed.py:586) names it — **M6 HOLDS, §2.1's safety argument is untouched**.
  Also confirmed etkl.ttl declares NEITHER CompiledDocumentHolon NOR membraneHealth, so the brief's
  named silent-failure mode was real and was avoided (test_vocab_shapes.py:98,109 pass etkl-holons.ttl).
  And confirmed each negative fixture trips exactly ONE arm: bad-two-values carries two IN-enum values
  (violates only sh:maxCount 1), bad-outside-enum carries one value in a distinct example.org
  namespace (violates only sh:in). Shape is verbatim §4.8 at etkl-shapes.ttl:144-147.
Task 5: minor (deferred): test_vecab_shapes.py:104-105 — the parametrize list has no `ids=`, so a
  failure names the fixture file rather than the constraint ("maxCount" / "sh:in"). Cosmetic.
Task 5: complete (commits 6ccf1c5..f1a92f5, review clean, 1 deferred minor)
Task 6: dispatched (implementer opus, agent a39450b4b5d86f083) — BASE f1a92f5
  Model choice: opus, not sonnet. Why: unlike Task 5 this brief supplies NO code — Step 1 is a
  measurement over 45 .rq files and Step 2 is a BRANCH on that measurement between shipping a
  tripwire and taking spec §4.9's named fallback. That is the judgment tier. Cost if wrong: an
  expensive implementer on a task that might reduce to a one-row fallback.
  Handed over beyond the brief: the R128-not-R127 ruling above (binds only on the fallback branch);
  the register measurement (116 rows / 24 closed / tops at R126) with an instruction to RE-COUNT;
  explicit authorisation that the fallback branch touches docs/superpowers/residues*.md, which the
  brief's "Modify test_vacuity_registry.py ONLY" line does not list because that line was written for
  the tripwire branch; and the three plan counts already caught wrong on this branch, with an
  instruction to treat the 30/3/28/45/"10 of 45"/360.07s figures as re-measurable rather than fact.
CONTROLLER HANDOFF written at 110k tokens (executing floor 150k, two tasks + the final review left):
  docs/superpowers/2026-08-25-holon-05-task-7-handoff.md — supersedes the task-5 handoff, points at
  THIS ledger as the recovery map, and carries the ten deferred minors for the final review to triage.
CONTROLLER ERROR, recorded because it changes a later command: the handoff was committed (d9eb6ae)
  WHILE Task 6's implementer was running, moving HEAD under it. Harmless to the implementer (its
  commits simply land on top; different files, no index contention) but it INVALIDATES the recorded
  BASE. **Task 6's review package must use BASE d9eb6ae, NOT f1a92f5** — f1a92f5..HEAD would put the
  handoff doc in the reviewer's diff and invite a scope-creep finding against work Task 6 never did.
  Lesson for the rest of this loop: do not commit controller artefacts while an implementer is live.
Task 6: implementer DONE_WITH_CONCERNS (commit 6cae23e; report task-6-report.md).
  **BRANCH TAKEN: THE FALLBACK (spec §4.9's named one).** Measured over a 29-query compile-path
  population: **164 (query, term) unreachable pairs across 24 of 29 queries.** 2 are the intended
  membrane-health.rq row; **162 would register a CATEGORY ERROR as vacuity** — those queries run over
  transient `urn:iladub:evidence:` graphs, never the compiled one. Only 3 of 29 execute against the
  graph compile_document returns, and even that narrowed population yields 3 rows not 2
  (escalation-furnish.rq/risk:Breach is a FALSE POSITIVE: it IS present in 3 graphs, as the object of
  dec:constrainedBy — a position `vocabulary_of` cannot see). So §4.9's criterion — can EVERY row carry
  a measured prose reason within this task? — is answered NO by measurement, not by a threshold. The
  fallback is the correct branch and the count is its reason.
  Falsification: three inversions, each shown moving its number and restored (F1 premise 164->162 and
  the row vanishes; F2 stripper off 164->173; F3 widened vocabulary_of narrow 3->2 with both promotion
  terms surviving). test_vacuity_registry.py left UNTOUCHED and re-run green as baseline: 4 passed,
  4 deselected in 308.81 s. test_doc_governance.py 4 passed.
**CONTROLLER RULING OVERTURNED — MY R128 RULING WAS WRONG, and the implementer was right to refuse it.**
  I ruled the fallback row must take R128 having measured only the register (tops at R126) and R127's
  10 citations. I did NOT read spec §11. Verified now, directly:
    $ sed -n '955,968p' docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md
    7. **`R128` — `dec:supersedes` is constrained by nothing.** …
    8. **`R129` — a non-IRI `suggester_iri` crashes the membrane rather than refusing.** …
    **The next number after this loop is `R130`.**
  And task-7-brief.md:38 Step 5 is "Raise R127, R128, R129". So R128 and R129 are reserved EXACTLY the
  way R127 is, and taking R128 would have collided with a row Task 7 is instructed to write.
  **REVISED RULING: the fallback row is `R130`, as shipped.** — Why: the spec allocates R127-R129 to
  this loop and names R130 as the next free number; the spec is the binding authority and it settles
  this outright. — Cost of my original error, had it stood: two rows numbered R128, one of them
  contradicting the spec §11 text Task 7 copies verbatim.
  **Process note, since it is the fourth instance of this failure mode on this branch:** my ruling was
  a load-bearing claim made from PARTIAL measurement — exactly what CLAUDE.md rule 2 forbids in a plan
  author, and the controller is not exempt. Global Constraint 7 caught it because the implementer was
  told to treat controller input as re-measurable too.
Task 6: Ruling — concern 3 ACCEPTED: the tally snapshot is `(24/116 closed)`, not the `(24/117)` I
  handed over. The implementer measured the register's OWN series (R126 = `24/115` with 116 rows then
  present), showing the parenthetical EXCLUDES the row being added. My figure was off by one.
  — Cost if wrong: a one-character edit in one row.
Task 6: concern 2 recorded (the FIFTH plan count on this branch that does not reproduce): the brief's
  population arithmetic `30`/`27`/`28` measures `32`/`29`. The `3` federate exclusions and the
  "10 of 45 comment-header" figure DO reproduce exactly. Not blocking — the fallback branch does not
  depend on the exact population size, only on 162 >> 0.
Task 6: concern 4 — files touched are docs/superpowers/residues.md + residues-open.md, outside the
  brief's "test_vacuity_registry.py ONLY" list. Pre-authorised by the controller at dispatch for the
  fallback branch; not scope creep.
Task 6: task reviewer dispatched (opus, agent a33b56c9a531546ba) over d9eb6ae..6cae23e.
  Model choice: opus, not sonnet — the central question is a JUDGMENT (was the fallback the right
  branch on §4.9's own criterion, or is it an unbuilt requirement wearing a measurement as cover?),
  not a diff check. Reviewer given §4.9 AND §11 to read, told the R130 substitution is now the
  controller's own ruling and must NOT be reported as a deviation, told the residues.md file touches
  were pre-authorised, and pointed at the implementer's own admission that the narrowed 3-query
  population yields 3 rows with one false positive — i.e. asked to weigh whether that undercuts its
  own case. No findings pre-judged.
Task 6: review NEEDS FIXES — 2 Important, 3 Minors. Reviewer VERIFIED rather than read: it
  independently enumerated `interpret.run(` across src/ and reproduced the category-error argument
  (exactly two sites pass the compile graph — document.py:1229 and :1324; gridregion.py:78-79,
  federate.py:56,99,160, reshape.py:92,195, oracle.py:49,53, adoption.py:104-107 all pass transient
  graphs), and it confirmed the falsification scripts' `_TERM`/`_PREFIX_NS` copies are BYTE-IDENTICAL
  to test_vacuity_registry.py:58-63, so the 164 was produced by the criterion the row claims.
  **The fallback branch is UPHELD for the enumerator and the forward arm.** Also verified: R130 is the
  first number spec §11 does not allocate; the `(24/116 closed)` snapshot is right against the
  register's own series; index line at residues.md:236 and full row at residues-open.md:101 are both
  correctly placed.
Task 6: Ruling — Important 1 is SUSTAINED and the fix is to BUILD THE REVERSE ARM, not to re-word the
  row. — What the reviewer measured: the two escapes R130 rules out (hand-typing the population,
  widening `vocabulary_of`) apply ONLY to the forward arm. The reverse arm's shipped analogue
  `test_no_registered_shape_has_gone_live` (test_vacuity_registry.py:335-346) iterates the registry's
  HAND-TYPED KEYS and consumes no population at all; only the forward arm at :323 needs
  `wired_shape_files`. So a `(query, term)` reverse arm over the single key membrane-health.rq ->
  {iladub:PromotionDecision, iladub:reviews} needs no enumerator, registers no false positive, and
  commits no category error — document.py:1324 is MEASURED to run that query over the graph
  compile_document returns. And the blind spot does not bite: `?pd a iladub:PromotionDecision` is in
  rdf:type-object position and `iladub:reviews` is a predicate, so both are visible to `vocabulary_of`
  as it stands — the implementer's own F3 proves it, showing both terms surviving under BOTH criteria.
  — Why build rather than re-word: the reverse arm is what the brief's Step 3 calls "the point" and
  what R106 asks for; leaving it unbuilt makes the residue prose again, which is the exact condition
  the row itself cites R106 for. It rides the existing module-scoped fixture at zero added runtime.
  — Cost if wrong: ~20 test lines and one more 5-minute corpus run; the branch ruling is NOT reopened,
  because the enumerator and forward arm stay unbuilt and R130 stays open, narrowed to them.
Task 6: Ruling — Important 2 is SUSTAINED, and the remedy is R120's CHEAPER INTERIM (paste the
  commands into the Measured column and date the measurement), NOT committing a census script.
  — Why: the register already carries R120 for precisely this class ("a load-bearing measurement
  cited in shipped source is not reproducible from repo state … the scratch scripts were never
  committed"), and R130 reproduces R120's defect in the act of recording a different one — `164 -> 3`
  is quoted in R130's OWN closure criterion, so a maintainer verifying closure must re-derive 164 from
  prose. But committing a new `--census` module is scope growth in a loop already minting three terms,
  a shape, a register row and now a test arm. — Cost if wrong: the 164 stays a once-measured figure
  with its commands recorded but its script unshipped, which is R120's status quo, not a regression.
Task 6: Ruling — Minors 3, 4 and 5 are FOLDED into the round-1 fix dispatch. — Why: all three are
  one-line corrections INSIDE the row the two Important findings already reopen, so they extend no
  round — the same reasoning taken for Task 2's Minors 2/3 and Task 3's Minors 2/3/6. (3: "§4.9's own
  terms" is an overclaim — §4.9 supports the `vocabulary_of` half, but the hand-typing objection is
  `wired_shape_files`' docstring, i.e. the module's convention, and §4.9's LITERAL fallback trigger was
  measured NOT to hold. 4: "29" is a textual-mention population — a query named only in a docstring
  counts — and the row does not say so. 5: the row states 162 flatly while the report calls it an upper
  bound.) — Cost if wrong: a slightly larger fix diff for the scoped re-review to read.
Task 6: fix round 1/5 dispatched (resumed implementer a39450b4b5d86f083) — FIX_BASE 6cae23e.
Task 6: fix round 1/5 committed f4886e0 (2 Important + 3 folded Minors claimed closed).
  Implementer VERIFIED Important 1's premise before building it (test_no_registered_shape_has_gone_live
  at :337-348 consumes no population; only the forward arm does), then shipped QUERY_VACUITY_REGISTRY
  (2 rows), `strip_rq_comments`, `rq_terms` and `test_no_registered_query_term_has_gone_live` riding
  corpus_graphs; vocabulary_of/_TERM/_PREFIX_NS/CORPUS/corpus_graphs reused UNCHANGED and none of the
  four SHACL-shaped functions touched. Forward arm's absence is a declared in-code limitation citing
  R130; R130 narrowed in BOTH register files. Important 2 took R120's interim as ruled. Tests:
  `-m corpus tests/etkl/test_vacuity_registry.py` -> **5 passed, 4 deselected in 324.37 s** (was 4
  passed, 308.81 s — so the new arm rides the fixture at ~0 added runtime, as predicted);
  test_doc_governance.py 4 passed. Falsifications F4 (register a reachable term -> arm fails naming the
  row + 3 documents) and F5 (delete the promotion clause from membrane-health.rq itself -> arm fails
  naming the removed term), both restored and green.
  **IMPLEMENTER CONCERN 1 — THE RE-REVIEWER MUST CHECK THIS AND IT IS INVISIBLE IN THE DIFF:** mid-round
  the implementer ran `git checkout tests/etkl/test_vacuity_registry.py` to undo falsification F4 and it
  reverted to HEAD, **destroying the 139 new lines**. It re-applied them from exact text and verified
  behaviourally plus by reading back the escape-sensitive scanner lines, and F5 then ran against the
  re-applied file and failed correctly. But the re-application is NOT visible in the final diff, so
  "the committed file is what was tested" is a CLAIM, not a measurement. The scoped re-review must
  satisfy itself of it directly.
  Implementer concern 2: the forward arm is still unbuilt; R130 is now scoped to exactly that.
Task 6: scoped re-review NOT YET DISPATCHED — controller hit the 150k executing floor at 148k.
  FIX_BASE for it is **6cae23e**, HEAD **f4886e0**. This is the FIRST action of the next session.
CONTROLLER HANDOFF written at 148k tokens (executing floor 150k, Task 7 + the final review left):
  docs/superpowers/2026-08-25-holon-05-task-7-handoff.md — REVISED in place (it was first written at
  110k, before Task 6 reported); supersedes the task-5 handoff and points at THIS ledger.

## Session 4 (fresh controller, resumed at Task 6's owed re-review)

Task 6: scoped re-review DISPATCHED (opus, agent a845d3152d0636029) over 6cae23e..f4886e0.
  Model choice: opus, not sonnet. Why: the diff is small but the gate is a JUDGMENT (does the new
  reverse arm actually pin the artifact, or does it pin its own dict?) plus an escape-sensitive
  scanner whose defect mode is precisely CLAUDE.md defect 5 — a test green with its subject deleted.
  Cost if wrong: an expensive seat on a 3-file fix diff.
  Carried beyond the template: the five findings from the ledger's ruling text; the standing R130
  ruling with an instruction NOT to report it as a deviation; and the MANDATORY committed-file check
  below, with an explicit read-only constraint on the tree.
Task 6: the re-review carries ONE check the diff cannot show it — the mid-round
  `git checkout tests/etkl/test_vacuity_registry.py` that reverted to 6cae23e and destroyed the 139
  new lines. The implementer re-applied them from exact text and F5 then ran against the re-applied
  file and failed correctly, but the re-application is invisible in the diff, so "the committed file
  is what was tested" is a CLAIM. Re-reviewer told to satisfy itself directly via the shipped helpers
  over the real vocab/queries/membrane-health.rq (cheap; the corpus leg is ~5.5 min and NOT required),
  and to report VERIFIED / NOT VERIFIED as its own section.
CONTROLLER PREP FOR TASK 7 (read-only, taken at HEAD f4886e0 while the re-review ran):
  **R-PF1 DISCHARGED — re-measured at HEAD, not transcribed.**
    $ grep -n 'etkl:MembraneHealth\b\|etkl:Intact\|etkl:Weakened\|etkl:Compromised\|etkl:membraneHealth' vocab/ontology/etkl-holons.ttl
    75: etkl:MembraneHealth a owl:Class ;      79/81/83: Intact/Weakened/Compromised
    86: etkl:membraneHealth a owl:ObjectProperty ;   89: its closing rdfs:comment (block ends)
    $ git log --oneline $(git merge-base main HEAD)..HEAD -- vocab/ontology/etkl-holons.ttl
    a0dd528   <- Task 1 ONLY; Task 5 edited etkl-shapes.ttl, NOT this file. No drift.
    So the block is **75-89** and the plan's figure is correct at HEAD. Task 7 writes 75-89.
  **THE MANIFEST SITE IS NOT WHERE THE PLAN SAYS, AND SAYS SOMETHING ELSE.** The file is
    `tests/arc-manifest.ttl` (there is no `vocab/arc-manifest.ttl`), and :1337 currently reads
    `etkl-holons.ttl:75-86`, not the `75-89` the plan implies is already there — so Step 4 is a
    75-86 -> 75-89 correction. Its surrounding rationale also still asserts holon:05 "is unmet —
    there is no green oracle to turn red" and "carries no prog:oracleArtifact; its prog:oracleTest
    is a target that does not exist", and the comment above it (:1330-1331) says "nothing DERIVES
    the term". THIS LOOP FALSIFIED ALL THREE. Task 7's flip is that, not only a line range.
  **The "nowhere else in the tree" clause STANDS, on a distinction Task 7 must keep:** the four
    terms are DECLARED only in etkl-holons.ttl, but are now REFERENCED in 8 more files
    (vocab/shapes/etkl-shapes.ttl, vocab/queries/membrane-health.rq, examples/membrane-health-
    conformant.ttl, tests/membrane-health-bad-{two-values,outside-enum}.ttl, and 3 arc fixtures).
    Declared-vs-referenced is the load-bearing word; do not widen it into a false correction.
  **REGISTER TALLY re-counted (the handoff's figure reproduces, with one subtlety it omits):**
    117 rows, **24 closed, 93 open**, topping at R130. R127/R128/R129 have NO rows — their only
    occurrences are mentions inside R130's own row text. Task 7 CREATES all three.
    The snapshot convention (measured by Task 6's implementer, re-verified against R130 = 24/116
    with 117 rows now present) is **count BEFORE adding**. Task 7 adds three rows in sequence, so
    they are NOT all (24/117): R127 -> **(24/117)**, R128 -> **(24/118)**, R129 -> **(24/119)**.
    The handoff states only the R127 figure; the other two follow from the same convention.
**CONTROLLER RULING (new, found in Task 7 prep): SPEC §11 RAISES EIGHT RESIDUES BUT ALLOCATES THREE
  NUMBERS. Items 1-4 get rows R131-R134.**
  What was measured, not read:
    $ sed -n '914,975p' docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md
    §11 lists items 1-5 ("Raised, each with what would close it") with NO numbers, then items 6/7/8
    allocated verbatim as R127/R128/R129, then closes "The next number after this loop is R130."
    That closing arithmetic only balances if items 1-4 issue NO numbers. But task-7-brief.md:38-45
    Step 5 says "Add residues 1-4 of spec §11", and each of the four carries its own *Closes when:*
    clause — the row format exactly.
    Are they already registered (i.e. numberless because they have numbers elsewhere)? NO:
    $ grep -inE "page-scope|preempt|document IRI|_DOC|IndexError|grounding portal" docs/superpowers/residues.md
    -> zero matches for all six probes. They are genuinely new.
  Ruling: **R127/R128/R129 keep their spec-allocated subjects** (R127 is cited in 10 committed places;
  renumbering falsifies all of them). **Items 1-4 take R131, R132, R133, R134** — after R130, because
  numbers are append-only and R130 is committed and cited. Item 5 is ALREADY R130, shipped by Task 6:
  **Task 7 must NOT raise it again.** Snapshots, per the count-before-adding convention:
    R127 (24/117) · R128 (24/118) · R129 (24/119) · R131 (24/120) · R132 (24/121) · R133 (24/122) ·
    R134 (24/123).   **The spec's "next number after this loop is R130" is superseded twice over:
    R130 shipped in Task 6, and after Task 7 the next free number is R135.**
  — Why: CLAUDE.md § Deferred residues is unambiguous ("Every loop that defers something records it in
  the canonical register... Loops append rows"), and the brief says to add them. Two sources against one
  arithmetic line. The asymmetry is what decides it: four measured residues left out of the canonical
  register is EXACTLY the failure this branch is already paying for — R127 is a label the spec named and
  never registered, and it is now blocking the loop's definition of done with four shipped tests riding
  it. Repeating that four more times to protect a closing line is the wrong trade.
  — Cost if wrong: four register rows a later loop would have raised anyway, plus a one-line edit to the
  "next number" statement. Reversible in one commit. The alternative reading — that items 1-4 are scope
  boundaries belonging to holon:06's spec, not rows (items 1 and 4 both close "with holon:06") — is
  recorded here so the maintainer can take it instead; it is arguable, and it is why this is a ruling.
  Task 7 Step 3 line numbers RE-VERIFIED at HEAD (the brief's own correction holds): heading
  "What is built" is `docs/holonic-interaction.md:145`, "Planned work (not done yet)" is `:158`, and
  the membrane-health bullet is **`:160-161`** — the brief is right and the spec's original `:154-155`
  is the done-list above it. Note the bullet's own phrase is *"from validation results"*, the SAME
  phrase Step 2 amends in the manifest's `prog:statement`; Step 3 must reword both consistently with
  Task 1 Step 2, or the loop ships two records disagreeing about what health is derived from.
Task 6: fix round 1/5 (5 addressed, 0 open — reverse arm BUILT at test_vacuity_registry.py:496-528
  with its registry :426-444, strip_rq_comments :446-482, rq_terms :485-493; R130's numbers given
  R120's interim; Minors 3/4/5 corrected in the row; commits 6cae23e..f4886e0). Re-reviewer VERIFIED
  rather than read: it exercised the COMMITTED arm against stand-in graphs and made it FAIL in both
  vocabulary_of-visible positions (iladub:reviews as predicate, iladub:PromotionDecision as rdf:type
  object), so the arm is not vacuous; and it re-ran two of the row's three pasted commands
  (`ls vocab/queries/*.rq | wc -l` -> 46, the src/ .rq grep -> 33), both reproducing exactly.
**Task 6: THE COMMITTED-FILE CHECK IS VERIFIED — the claim is now a measurement.** Three independent
  routes, none relying on the diff: (1) `git rev-parse HEAD:tests/etkl/test_vacuity_registry.py` ==
  `git hash-object` of the working file == 52f6a036…, and `git diff --stat f4886e0 HEAD --` on that
  path is EMPTY; (2) loading the COMMITTED module and calling rq_terms('membrane-health.rq') returns
  exactly the four terms F5's evidence names, with both registry keys resolving True; (3) the
  escape-sensitive scanner checked on real files — strip_rq_comments leaves all six PREFIX lines of
  membrane-health.rq:76-81 intact including `<https://w3id.org/iladub#>`, where a naive
  `line.split('#')[0]` truncates every one. So the 139 re-applied lines ARE what was tested.
  Reviewer left the tree clean (`git status --porcelain` empty before and after).
Task 6: minor (deferred): **an unmeasured claim about existing code, SHIPPED IN SOURCE** —
  test_vacuity_registry.py (~:410-412) says `test_no_registered_shape_has_gone_live` (:337) "iterates
  the registry's own hand-typed keys and consumes no population either". MEASURED FALSE: that test
  calls `idle_shapes(list(corpus_graphs.values()), sg)` at :344 with `sg = shapes_graph()` (:343), and
  shapes_graph (:143-147) calls wired_shape_files() (:133-140). It DOES consume the membrane
  population; what it does not do is derive its ROWS from one. The substantive argument (the reverse
  arm needs no enumerator because its rows are hand-typed) is correct and is what the code does — only
  the phrasing overstates it. **Recorded against myself: this sentence originated in MY OWN Important-1
  ruling ("consumes no population at all"), was carried verbatim into the fix dispatch, and was
  transcribed into shipped source. That is the fifth instance on this branch of a load-bearing claim
  made from partial measurement, and the first one I put into a committed file.** One-line prose fix.
Task 6: minor (deferred): residues-open.md:101 says "§4.9 is silent on where the population comes
  from"; spec :577-578 in fact names one ("a population enumerator over `vocab/queries/*.rq`"). The
  imprecision runs AGAINST the row's own interest (§4.9's glob is 46 files, broader than the 29 used,
  so citing it would strengthen the 164-pair argument), so it changes no conclusion — but it is a new
  unmeasured claim about the spec introduced by the fix.
Task 6: minor (deferred): bare basenames in a measured citation — residues-open.md:101 cites
  `feed.py:13` and `rowgroups.py:5-16`; the real paths are src/iladub/feed.py and
  src/iladub/etkl/rowgroups.py (different directories).
Task 6: re-reviewer out-of-scope observation (ledgered, not blocking): no registry arm — neither the
  three shipped shape arms (:325, :337, :352) nor the new query arm — guards against its registry
  being EMPTIED; an empty dict makes all of them pass vacuously. Pre-existing module convention.
Task 6: register integrity re-checked by the reviewer after the row rewrite: the row now splits into
  10 pipe-delimited cells rather than 7 (three escaped `\|` inside the pasted commands), and this
  breaks NOTHING — escaped pipes were already in use at residues-open.md:47,63,84, and every parser is
  row-anchored regex on the INDEX file (scripts/cockpit.py:150-153, tests/test_arc_manifest.py:243-244);
  nothing column-splits residues-open.md. Index/detail tallies agree: 24 closed / 93 open, 93 rows.
Task 6: complete (commits d9eb6ae..f4886e0, review clean, 4 deferred minors)
NEXT: Task 7.
Task 7: dispatched (implementer opus, agent aabbf8837b45e40cb) — **BASE f4886e0**.
  Model choice: opus, not sonnet. Why: the brief supplies no code, and every step is a judgment about
  what the record should SAY — which numbers are stale, which claims this loop falsified, which tests
  genuinely ride R127. That is where this branch has failed five times. Cost if wrong: an expensive
  seat on a doc-only task.
  Handed over beyond the brief (all four are corrections the brief cannot know, plus one open question):
   (a) R130 is SHIPPED — spec §11 item 5 is already raised; do NOT raise it again;
   (b) the brief's `(24/116 closed)` snapshot is stale — 117 rows / 24 closed / 93 open now, and rows
       added in sequence do NOT share a snapshot; told to RE-COUNT and derive each, not transcribe mine;
   (c) the R131-R134 numbering ruling, WITH the opposing reading handed over as a live option and an
       instruction to argue it rather than silently pick either way;
   (d) the manifest is tests/arc-manifest.ttl and :1337 reads 75-86, not 75-89;
   (e) R-PF1 discharged (75-89 at HEAD, no drift) and Step 3's :160-161 confirmed, with the
       "from validation results" phrase coupling Step 2 and Step 3 that the brief does not state.
  **R127's coupled-test count handed over as a CONTESTED measurement, not a number.** The task-5/7
  handoffs assert "4 coupled tests at :216,:388,:460,:578". My own measurement does not cleanly
  reproduce that list: R127 is cited on 10 docstring lines + document.py:1309 (11 sites), sitting inside
  the fixture apple_report (:51), the helper _one_more_rationale (:77) and 3 tests (:182, :362, :422);
  while the tests that USE the lever are :401, :422 and :552. "Cites R127" and "goes red when R127
  closes" are DIFFERENT SETS and the row must record the second. Implementer told to decide from the
  file, name exactly those, and state its criterion in both the row and the report.
  Also handed over: the non-clean suite baseline with its measured cause (Task 2's +3 triples broke
  test_single_page_document_matches_compile_tables at f33db9f, `assert 329 == 326`; repaired b91e152),
  with the instruction that ANY delta from 1312 is a finding to ATTRIBUTE to a commit and a cause.
  And an explicit DO-NOT-TOUCH list for the ten deferred minors, so they stay in the final review's
  commit and not this one.
CONTROLLER HANDOFF written at ~126k tokens (executing floor 150k, Task 7's review + the final
  whole-branch review left): docs/superpowers/2026-08-25-holon-05-final-review-handoff.md —
  supersedes the task-7 handoff and points at THIS ledger as the recovery map.
  **DELIBERATELY LEFT UNCOMMITTED while Task 7's implementer is live** — this is the lesson recorded
  at Task 6's dispatch (committing a controller artefact mid-task moved HEAD under the implementer and
  invalidated its BASE). It is committed only after Task 7 reports.
  Checked before leaving it in the tree, because Task 7 runs the governance lint: tests/docgov_extract.py
  :109-110 discovers docs via `git ls-files "*.md"` — TRACKED files only — so an untracked handoff is
  invisible to the lint and cannot give Task 7 a spurious red. The brief's Step 7 `git add` also names
  explicit paths (residues*.md), which this filename does not match, so it cannot be swept into Task 7's
  commit either.
**CONTROLLER ERROR, caught before it cost anything: the BASE I recorded for Task 7 was WRONG.** I wrote
  "BASE f4886e0", but HEAD at dispatch was **b314c23** — the PREVIOUS session's handoff commit sits on
  top of f4886e0. Packaging f4886e0..ae5fefd gave **2 commits** and would have put a controller artefact
  in the reviewer's diff, inviting a scope-creep finding against work Task 7 never did. Regenerated at
  b314c23..ae5fefd (1 commit, 124086 bytes) and deleted the stale package. This is the SAME error the
  ledger already records at Task 6's dispatch, made a second time — the lesson "do not commit controller
  artefacts while an implementer is live" was learned, but its corollary "the handoff commit becomes the
  next task's BASE" was not written down. It is now.
Task 7: implementer DONE_WITH_CONCERNS (commit ae5fefd; 6 files, +172/-30; report task-7-report.md)
  **FULL SUITE: `1 failed, 1334 passed, 7 skipped, 1 xfailed in 2521.84s (42:01)`** — 1334 >= the 1312
  baseline, so spec §8 item 9 is met. The one red is attributed to `main`, NOT this branch:
  test_the_live_newest_handoff_declares_a_topic, caused by 9adb4d0 (an ancestor of the merge-base)
  adding a handoff with no `**Topic:**`. Arithmetic offered: 1320 + 23 new ids = 1343 collected;
  1312 + 23 - 1 = 1334 passed, i.e. all 23 tests this branch adds pass. NOT accepted on report —
  handed to the reviewer as claim 4 to verify independently.
  - **CONCERN 1, THE LARGEST: IT DELETED A MANIFEST EDGE.** Flipping the criterion repaired BOTH grounds
    of the `holon:05 -> holon:01` proposition's own rationale (A1 "unmet", A2 "no oracleArtifact"), so
    M17 refused it and only ASSERT or DELETE were membrane-legal. It asserted; **M19 arm 1 then refuted
    the assertion** (deleting etkl-holons.ttl leaves holon:05's oracle green, because membrane-health.rq
    BINDs etkl:Intact/Weakened/Compromised as bare IRIs), so it deleted the edge and kept the reading as
    a measured comment. Second edge this manifest has authored and M19 has killed.
  - CONCERN 2: **the register grew by ELEVEN rows (R127-R137), not the 7 my ruling anticipated.** My
    §11 items 1-4 ruling was UPHELD by the implementer as a spec defect on its own reasoning ("next
    number is R130" is arithmetically impossible against §11's own eight raises). It then added R135
    (M19's finding) and R136/R137 (its own falsification round) on its own initiative. Re-counted
    127 rows / 25 closed / 102 open; next free number now **R138**. It also caught a snapshot subtlety
    I missed: **R126 CLOSES FIRST**, so the first new row is `(25/117)`, not the `(24/117)` I derived.
  - CONCERN 3: it reports TWO things it wrote are **pinned by nothing** and did not paper over it —
    F8 (a criterion can read `met true` while its prog:source points into "Planned work (not done
    yet)") and F9a/b (deleting a register index row, or un-closing a closed one, both stay green; M7
    guards only rows a prog:blockedBy names, confirmed by F9c's control arm). Raised as R136/R137.
  - CONCERN 5: **four more brief/spec values did not reproduce** (the sixth, seventh, eighth and ninth
    on this branch): the second `75-86` no longer exists to correct (it lived in the deleted edge's
    rationale); R132's "5 files" is 6; R129's `_expand` is `_payload_nt`; R134's path is
    src/iladub/feed.py not src/iladub/etkl/feed.py. **R-PF1's `75-89` DID reproduce.**
  - CONCERN 6: **it hit the same `git checkout` trap Task 6 hit**, destroying every manifest edit.
    Re-applied from exact text, `27 passed` re-verified, later restores used a backup copy. It states
    this one IS visible in the final diff, unlike Task 6's.
  - CONCERN 7: self-inflicted, caught by an EXISTING pin — its holon:06 note was first written inside
    the Turtle block, and cockpit's regex walks to the first line ending in `.`, so holon:06 silently
    stopped being counted (`('holon', 5, 5) != ('holon', 5, 6)`). Moved above the block per the file's
    own convention; it did NOT touch cockpit.py to make the test pass.
  - docs/superpowers/arc-dependency-landscape.md regenerated (28->27 edges, 22->21 ready) as a
    consequence of the deletion — outside the brief's file list; handed to the reviewer as claim 5,
    to verify the CLAUDE.md generated-cache gate (regenerate-and-diff) actually exists.
Task 7: task reviewer dispatched (opus, agent ac6df396570fe3421) over b314c23..ae5fefd.
  Model choice: opus. Why: the gate is a judgment about an EVIDENCE-MANIFEST EDGE DELETION and eleven
  register rows, not a diff check. Given all seven concerns unpre-judged, with an explicit instruction
  that concluding the implementer was WRONG is an available verdict, and the ten deferred minors ruled
  out of scope so they stay with the final review.
Task 7: review APPROVED (task quality), spec compliant on all seven steps, **1 Important + 5 Minors**.
  Reviewer VERIFIED rather than read, and in two places produced a STRONGER result than the report:
  - **The edge deletion is UPHELD, on stronger evidence than the implementer offered.** It rebuilt the
    refused proposition in memory and ran the membrane: M17+M18 refuse the proposition form, the
    asserted form conforms — so ASSERT-or-DELETE really was the whole option set, and
    `tests/arc-shapes.ttl:334-336` states that outcome in the shape's OWN comment. It then showed
    M19 arm 1 is **structurally certain, not a flaky run**: `grep -rn "etkl-holons" src/ --include='*.py'`
    returns NOTHING, and neither etkl-holons.ttl nor etkl-shapes.ttl is in _TAB_SHAPE_FILES/
    _DEC_SHAPE_FILES/_FULL_ONT (compile.py:398,421,441-453) — so ablating holon:01's artifact CANNOT
    turn holon:05's oracle red under any input. The refutation is a fact about the code.
  - **The eleven rows check out mechanically on every axis:** 127 index rows / 25 closed / 102 open;
    index ID set == detail ID set; no duplicates; R127-R137 no gaps; snapshots in WRITE ORDER
    R127 (25/117) … R137 (25/126), each +1 with closed pinned at 25; R126 (24/115) and R130 (24/116)
    both preserved un-updated. The ten pre-existing gaps (17,21,22,41,69,70,73,75,81,82) are inherited.
    The three self-raised rows (R135/R136/R137) were ruled RIGHT to raise and not duplicates.
  - Attribution of the red to `main` INDEPENDENTLY VERIFIED: merge-base 18226e7, 9adb4d0 is its
    ancestor, the merge-base tree's newest handoff already has 0 `**Topic:**`. Collected at HEAD = 1343
    and 1334+1+7+1 = 1343 closes exactly.
  - The generated-cache gate EXISTS and passes: tests/test_arc_landscape.py::
    test_the_tracked_landscape_is_byte_identical_to_a_fresh_regeneration regenerates from the committed
    manifest into tmp_path and demands byte identity; reviewer ran it green. So arc-dependency-
    landscape.md satisfies CLAUDE.md's generated-cache exception and regenerating it was MANDATORY.
  - Nineteen sampled file:line citations were all exact.
**Task 7: IMPORTANT FINDING OPEN — NOT FIXED, by the maintainer's explicit instruction.**
  `docs/superpowers/residues.md:261` — R137's INDEX line says M7 "covers only the **~15** rows a
  prog:blockedBy names". Measured by the reviewer:
    $ grep -oE 'prog:blockedBy +"[^"]+"' tests/arc-manifest.ttl | grep -oE 'R[0-9]+' | sort -u
    R43 R44 R45 R71 R74 R79 R97          -> 7 distinct residues
    $ grep -cE 'prog:blockedBy' tests/arc-manifest.ttl   -> 11 statements
  Neither is ~15; the figure overstates the guard's coverage by ~2x. **This is the branch's own named
  failure mode — a count made from reading — committed into an INDEX line, which is precisely the
  artefact CLAUDE.md § Deferred residues says gets consumed as fact (the R87/R88 case).** The DETAIL
  row is clean (qualitative, carries no number). Fix is one token: `~15` -> `7`.
Task 7: minor (deferred): residues.md:260 — R136's index line says the revert left "the suite fully
  green"; the measurement was two modules (test_arc_manifest.py + test_doc_governance.py -> 31 passed).
  Detail row is precise; only the one-liner over-claims.
Task 7: minor (deferred): residues-open.md R132's parenthetical `(14 including docs/)` went stale ON
  COMMIT — the row itself is the 15th file containing the literal (14 at b314c23, 15 at HEAD). The
  load-bearing `6` reproduces exactly. Self-referential drift, not a measurement error.
Task 7: minor (deferred): residues-closed.md:87 — R126's moved row has 8 UNESCAPED pipes in a 5-column
  table, rendering two phantom columns. **PRE-EXISTING** (identical at b314c23) and preserved
  deliberately under "keep the original row text verbatim". Conflicts with nothing the brief mandates.
Task 7: minor (deferred): the report's "not this branch's" UNDERSTATES the Topic red by one step — the
  attribution to main is right, but d9eb6ae ON THIS BRANCH added a second topicless handoff, which is
  now the file _newest_loop_doc() selects. So the branch sustains the red independently of the commit
  that started it. The report's own commit-walk table discloses this; only its prose over-exculpates.
Task 7: reviewer ⚠️ items, controller-resolved:
  (a) the 1334 figure was not re-run (per instruction); both checkable projections hold at HEAD
      (collected 1343; the pass/skip/xfail/fail ledger sums to it). RESOLVED — not a gap.
  (b) the M19 ablation RUN was not reproduced (it needs worktree construction, a mutation the reviewer
      rightly declined); it substituted a STRONGER structural argument reaching the same conclusion.
      RESOLVED — the substitute is better evidence than the run.
  (c) **whether R135's remedy should also close R117 is explicitly a CONTROLLER call, not a Task 7
      defect.** NOT RESOLVED — carried into the final review; see the handoff.
Task 7: reviewer out-of-scope observation (ledgered): register_rows() at tests/test_arc_manifest.py:237
  matches `^\| *(R\d+) *\|`, which would NOT match a struck `~~Rn~~` index row. Harmless today (zero
  struck index rows; all 25 closed rows use the status column) but it is a latent instance of exactly
  the class R137 names.
**Task 7: NO COMPLETION LINE — one Important finding is open and the fix loop was NOT started, on the
  maintainer's explicit instruction ("hand off after the review, don't start the fix loop"). This is a
  maintainer decision, not a breaker adjudication and not a parked finding: the fix is owed and is the
  FIRST action of the next session. Commits b314c23..ae5fefd, review approved, 1 Important open,
  5 Minors deferred.**

## Session 4, continued — Task 7's fix round (maintainer reversed the no-fix-loop instruction for THIS finding only)

MAINTAINER DIRECTIVE (2026-08-25, at 193k tokens / 150k executing floor, override logged): fix the one
  Important finding in THIS session; the final whole-branch review starts fresh. Scope is the single
  finding — nothing else on the branch is reopened.
Task 7: fix round 1/5 dispatched (FRESH implementer haiku, agent a734863aee851e478) — FIX_BASE ab23b53.
  Model choice: haiku, the cheapest tier. Why: the skill's Model Selection puts single-file mechanical
  fixes at the cheapest tier, and this is one token in one prose line with the target value supplied.
  A fresh implementer rather than a resume: Task 7's implementer had ended, and the fix needs the
  finding plus one file — not that agent's 253k-token context.
  Told to RE-MEASURE rather than transcribe the number I handed it (Global Constraint 7), with an
  explicit instruction to STOP and report if its run disagreed; told the detail row is verified clean
  and OUT of scope; told the 15 deferred minors are untouchable; told the inherited Topic red is not
  its concern; and warned off `git checkout <file>`, which two implementers on this branch have used
  to destroy their own work.
Task 7: fix round 1/5 committed **5d01a4c**. Implementer RE-DERIVED the figure independently and
  reproduced both halves — 7 distinct residues (R43 R44 R45 R71 R74 R79 R97) across 11 statements —
  then wrote the DISTINCT-residue count, which is what the sentence ("the rows a prog:blockedBy names")
  is about. Tests: test_doc_governance.py 4 passed; test_arc_manifest.py 27 passed.
  **FALSIFICATION — the honest answer, and the expected one: NOTHING machine-checks this figure.** M7
  verifies that named residues EXIST in the register but does not check any count. The implementer
  reported the absence rather than manufacturing a test — which is correct, and is precisely the hole
  R137 was raised to record. It did not touch cockpit.py or any test to make a guard appear.
Task 7: scoped re-review dispatched (sonnet, agent a7cb2ef4d7fd565f2) over **ab23b53..5d01a4c**.
  Model choice: sonnet, not opus — a 4356-byte diff changing one token; the skill puts scoped
  re-reviews of small fix diffs at the cheap-to-mid tier.
  **BASE CHOICE, and it is the third time this trap has appeared on this branch:** the previous review
  saw ae5fefd, but ab23b53 (the controller's own handoff commit) landed between. Packaging ae5fefd..
  5d01a4c would have put a controller artefact in the re-reviewer's diff for the THIRD time. FIX_BASE
  is ab23b53, so the re-reviewer sees the fix commit alone. The handoff was never part of Task 7's
  reviewed surface — it was untracked during that review and declared out of scope in the dispatch.
  Re-reviewer told to RE-DERIVE the count itself (accepting the replacement on the implementer's word
  would repeat the defect in the act of closing it), and told explicitly that an ABSENT falsification
  is correct here while a MANUFACTURED one is a defect to flag.
Task 7: fix round 1/5 (1 addressed, 0 open — residues.md:261 now states the measured `7`; commits
  ab23b53..5d01a4c). Re-reviewer RE-DERIVED the count itself rather than accepting it (7 distinct /
  11 statements, reproduced verbatim), confirmed the replacement is the DISTINCT-residue count matching
  the sentence's referent, and verified scope: `git diff ab23b53 5d01a4c --stat` -> 1 file, 1 insertion,
  1 deletion. R137's detail row untouched; no tally snapshot moved; **none of the fifteen deferred
  minors was opportunistically fixed**. Row shape still matches BOTH row-anchored parsers
  (cockpit.py:148, test_arc_manifest.py:237). It also verified the implementer ACTUALLY LOOKED for a
  guard rather than asserting the absence — `grep -rn 'R137' tests/` exits 1, and the implementer had
  cited test_arc_manifest.py:119-121 and :330-334 for M7's real scope. Re-ran both modules together:
  31 passed. New breakage: none. Out-of-scope observations: none.
**Task 7: complete (commits b314c23..5d01a4c, review clean, 5 deferred minors)**
**ALL SEVEN TASKS COMPLETE. The loop's implementation is done. What remains is the FINAL WHOLE-BRANCH
  REVIEW, which is ORIGINATING work and starts in a FRESH session — entry point
  docs/superpowers/2026-08-25-holon-05-final-review-handoff.md, revised in place at 5d01a4c.**
  Not done and deliberately so: the final review, its one fix wave, and the merge decision.
FINAL WHOLE-BRANCH REVIEW dispatched (opus, agent a258ec119c93f0aa0) over **18226e7..298b54f**
  (merge-base..HEAD; 21 commits, 335053 bytes). Maintainer directed the dispatch from THIS session at
  214k tokens (override logged) rather than deferring it to the fresh one.
  Given, beyond the standard reviewer template: the ledger with an explicit instruction that triaging
  its **16** `minor (deferred):`/parked lines and auditing its **22** `Ruling:` lines is a PRIMARY task,
  not background; CLAUDE.md's binding constraints spelled out (the neurosymbolic gate, source ownership,
  plan-rules 1-6 esp. 4 and 6, R89's producer-guard rule, doc governance, the langString trap); and the
  six KNOWN-STATE items to JUDGE rather than rediscover — the inherited-but-branch-sustained Topic red,
  the non-clean 1312 baseline, the never-pinned corpus suite, Task 7's manifest EDGE DELETION, the
  measurably-false claim shipped at test_vacuity_registry.py:~410-412 (which originated in a controller
  ruling), and the open R135/R117 call. Told the two handoff commits are process artefacts, not scope
  creep. Asked for four explicit answers: mergeable?, the 16-way triage, the ruling audit, and
  cross-task coherence — the last being the thing no per-task review could see.
FINAL WHOLE-BRANCH REVIEW: **YES WITH FIXES. Zero Critical. ZERO CODE FINDINGS.** Read the 335 KB diff
  in four passes plus the ledger, spec and plan, and ran nine independent verifications.
  **Every blocking item is ONE LINE OF PROSE in a committed file, and each is this branch's own named
  failure mode — a load-bearing claim made from reading.** ~20 minutes of edits.
  THE SEVEN BLOCKING FIXES:
   1. tests/etkl/test_vacuity_registry.py:414-416 AND docs/superpowers/residues-open.md:103 — delete the
      false "consumes no population" claim (I1). Ship the CORRECT wording: the arm needs no ENUMERATOR
      because its ROWS are hand-typed.
   2. src/iladub/etkl/document.py:137-138 — "does not run it yet; that wiring is the next task's" is
      FALSE at HEAD (:1324 runs it). A Task-2 comment Task 3 invalidated; no per-task review could see
      both. It also leaks SDD process vocabulary into production source.
   3. src/iladub/etkl/document.py:1747-1750 — five citations ALL OFF BY 50, under the words "MEASURED,
      not assumed", and `recognized` has TWO writers where the comment names one. Substantive claim
      survives (last write :1743 < the _seal call :1751).
   4. src/iladub/etkl/document.py:1208 — :1486/:1690 are :1536/:1740. Authored by this branch.
   5. tests/etkl/test_membrane_health.py:105-107 — the pasted command returns **12**, not the stated 7
      (and the honest repo-wide count is 8; :579 is a genuine interceptor the exclusion hides).
   6. docs/superpowers/residues.md:260 — R136's INDEX line says "the suite fully green"; it was two
      modules / 31 passed. Same defect the branch already fixed one row away in 5d01a4c.
   7. docs/superpowers/2026-08-25-holon-05-task-7-handoff.md + 3 sibling handoffs — add `**Topic:**`.
  **KNOWN STATE 3 IS FALSE AS I STATED IT, and this is a controller error: `tests/test_corpus*.py` HAS
  been run on a pinned commit.** pyproject.toml:96-101 declares the `corpus` marker but sets NO
  `addopts`, so nothing is deselected by default; collection at HEAD is 1343, the 49 corpus tests are
  inside it, and 1334+1+7+1 = 1343 closes exactly. The "never run on a pinned commit" line I carried
  through three handoffs was wrong. NOT a merge blocker; the corpus modules are covered.
  **KNOWN STATE 1 (the Topic red) — the branch can cheaply stop sustaining it.** Merging introduces no
  red (merge-base's newest doc is already topicless), but d9eb6ae's task-7-handoff now sorts top under
  `max()` (cockpit.py:283-292) and 4 of the 5 handoffs this branch adds are topicless while
  final-review-handoff.md HAS a Topic — so the convention was known and applied inconsistently. Spec §8
  item 9 wants a green suite. Fix is four lines.
  **NEW MINOR THE PER-TASK REVIEWS COULD NOT SEE — a genuine SPEC GAP:** vocab/ontology/etkl-holons.ttl
  :79-80, `etkl:Intact`'s comment was NOT amended with the model and no longer DISCRIMINATES. It still
  reads "Interior fully conforms to the membrane," which under the shipped model is equally true of
  Weakened (which also requires ?conforms = true). The distinguishing fact — nothing is HELD — is in
  MembraneHealth's and Weakened's new comments but not Intact's. **§4.6's four-artifact set omitted it.
  Fix upstream in the spec, then in the file.**
  WHAT IT VERIFIED GREEN, independently: 39 passed across membrane-health/vocab-shapes/source-ownership/
  transform-gate WITH the corpus legs running; 59 passed + the 1 Topic red across the manifest/cockpit/
  governance/landscape/ablation modules; **O9 falsified by hand** (each negative trips exactly one arm);
  **source ownership CLEAN** (no HGA-prefixed term as a subject anywhere; prov: only as an object);
  **the neurosymbolic gate CLEAN** — no tuned constant or tolerance anywhere in the new code, no SHACL
  derives anything, no Python answers a span/read/group/role question; **compile.py has ZERO changes on
  this branch**, so R-PF4's premise holds by the diff.
  **RULING AUDIT: all ~20 rulings reach SOUND OUTCOMES. Exactly one reached the right conclusion from a
  FALSE PREMISE — my own Task 6 Important-1 ruling** ("consumes no population at all"), which is I1.
  "Fix the reason, keep the ruling." It also flagged R-PF2 as sound-but-unmanaged: it authorised the
  "not run yet" comment and carried no rider requiring Task 3 to update it — that is I2.
  **The §11 / R131-R134 ruling was the one it scrutinised hardest and it is SOUND** — §11's own heading
  is "Raised", each item carries a *Closes when:*, and two authorities beat one arithmetic line.
  **R135/R117 CALL TAKEN (the one I owed the maintainer): plan ONE instrument, close both in the same
  act ONLY if it demonstrably covers iladub-hga-align.ttl; do NOT merge the rows now.** Same failure
  class, but R117 carries a scoping question R135 does not — what *declared* means at the ALIGNMENT
  seam. Later loop's work; NOT a merge consideration.
  CROSS-TASK COHERENCE: **coherent on the substance**, two prose drifts (I2, and Intact's stale gloss).
  The five artefacts tell one story; prog:source resolves to exactly the moved bullet; the flip block's
  two greps both now answer the other way and were reproduced.
**CONTROLLER ERROR the review caught: THE LEDGER'S OWN COUNTS DO NOT REPRODUCE — the tenth instance of
  this branch's signature failure, in the artefact that catalogues the other nine, and it is mine.** I
  told the reviewer "16 minor (deferred) lines and 22 Ruling: lines". Measured: the 16 includes the
  dispatch line self-matching, so there are **15** findings + **2** in the Task-2 block = **17**; and
  `grep -c 'Ruling:'` returns **7**, not 22 — my 22 came from the broader `grep -c 'Ruling\|RULING'`,
  a different query than the one I reported. I stated a figure from one command and labelled it as
  another. Cost: the reviewer triaged 17 items correctly anyway, having re-counted rather than trusting
  me — which is the discipline working.
