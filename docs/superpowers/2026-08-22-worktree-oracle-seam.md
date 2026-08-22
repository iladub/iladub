# The worktree/oracle seam, measured over all 17 met criteria

Task 1 of the arc-has-edges plan (`docs/superpowers/plans/2026-08-22-the-arc-has-edges.md`,
argued from `docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md`). Spec §4 carries a
MEASURE box: before designing M19's runner, establish whether every met criterion's oracle
test(s) actually resolve and pass — or fail for the right reason — when run with `cwd` inside a
bare `git worktree` that has no `.venv` of its own. §0/C5 measured **six** probes on four
worktrees; this note measures all **seventeen** met criteria and the **272-pair** ablation
question Task 3 needs to design M19's grouping and Task 4 needs to author edges against.

Tree: `the-arc-has-edges` @ `dcd45fd`, `tests/arc-manifest.ttl` byte-identical to `main` @
`fd6c81b` (`git diff --stat fd6c81b HEAD -- tests/arc-manifest.ttl` → empty; confirmed 2026-08-22).
Runner: `./.venv/bin/python` (rdflib 7.6.0), never `python3` (Global Constraint 1).

---

## Step 1 — Q1–Q6 re-run, set semantics

Re-parsed `tests/arc-manifest.ttl` with rdflib, reading `prog:met`, `prog:metOn`,
`prog:oracleTest`, `prog:oracleArtifact` off all 43 `prog:Criterion` subjects (multi-valued,
via `graph.objects()`, never `graph.value()`).

| figure | value |
| --- | --- |
| criteria | 43 |
| met | 17 |
| unmet | 26 |
| met, carries ≥1 `prog:oracleArtifact` | 17 / 17 |
| unmet, carries `prog:oracleArtifact` (Q1's "unmet-with-artifact") | 7 (`etkl:02–07`, `tab:10`) |
| unmet, no artifact | 19 |
| distinct artifact files across the met set, line-suffix stripped (`_LINE_SUFFIX`) | **28** |
| distinct artifact files via `Graph.value()` (historical single-valued Q5 method) | 11 |
| A4 strict (`metOn(Y) < metOn(X)`, date filter only) | **123** |
| A4 non-strict (`metOn(Y) ≤ metOn(X)`, date filter only) | **149** |
| non-strict + A3 (distinct `prog:oracleTest` **sets**) | **140** |
| non-strict + A3 + A6 (distinct `prog:oracleTest` sets **and** distinct artifact-file sets) | **130** |
| … of which intra-`holon` | 10 |
| … of which intra-`dec` | 45 |
| never-source (non-strict+A3+A6) | `dec:07`, `dec:10` (both `metOn 2026-05-31`, the earliest) |
| never-target (non-strict+A3+A6) | `tab:06` (`metOn 2026-08-20`, the latest) |

**Every figure reproduces §0/C1's numbers exactly** (43 / 17 / 28 / 123 / 149 / 140 / 130,
intra-holon 10, intra-dec 45) — the tree has not moved since C1 was measured on `b3ffaa1`. This
confirms C1's method (set disjointness, not `Graph.value()`) rather than superseding it.

**Q2** (shared oracle test) and **Q3** (metOn clustering) also reproduce §0/C1 and the spec's own
figures unchanged: `dec:16`/`holon:03`/`holon:04` share both `test_hga_alignment.py` tests;
`dec:08`/`dec:10` share `test_boundary.py::test_promotion_grounds`; five dates carry >1 criterion,
the widest being `2026-06-23` (`dec:16`, `holon:01–04`, five criteria).

**Per-criterion multiplicity** (met set, `(tests, raw-artifacts, distinct-files)`) — confirms
§0/C1's count verbatim: `dec:01,03,04,05,06,07,08,11,14,16` → `(2,3,3)`; `dec:10` → `(2,4,4)`;
`holon:02,03` → `(2,1,1)`; `holon:04` → `(2,2,2)`; `etkl:01`, `holon:01`, `tab:06` → `(1,1,1)`.

**Files shared by >1 met criterion** (the Q6 set, 8 files, 18 of the 28 involved criterion-slots):
`vocab/shapes/dec-shapes.ttl` (`dec:01,03,04,05`), `vocab/shapes/iladub-shapes.ttl`
(`dec:07,08,10`), `vocab/shapes/iladub-hga-shapes.ttl` (`dec:16`, `holon:03`),
`examples/promotion.ttl` (`dec:01,08,10`), `examples/proposal.ttl` (`dec:07,08,10`),
`tests/leak-attempt.ttl` (`dec:07,10`), `examples/holon-grounding-conformant.ttl` and
`tests/holon-grounding-leak.ttl` (`dec:16`, `holon:04`).

Reproduction script: `/private/tmp/.../scratchpad/step1_q1q6.py` (scratch, not committed).

---

## Step 2 — does each of the 17 met criteria's own oracle run clean in a bare worktree?

For each met criterion, `git worktree add --detach <wt> HEAD`, `cwd = <wt>`, interpreter
`REPO/.venv/bin/python` (absolute — the worktree has none of its own), run **only that
criterion's own `prog:oracleTest` ids**, before any deletion.

**Result: all 17 run clean.** 16 report every own test `PASSED`; `etkl:01` reports `SKIPPED`
(`corpus/` is gitignored and therefore absent from a worktree — `test_corpus.py`'s own
`require_pinned_edition` skips visibly rather than compiling, exactly as it does on a machine
that has not run `scripts/fetch_corpus.py`; this is the test's documented behavior, not a
worktree defect).

| criterion | `worktree add` | step-2 wall-clock | outcome |
| --- | --- | --- | --- |
| `dec:01` | 0.42s | 0.52s | 2 PASSED |
| `dec:03` | 0.21s | 0.42s | 2 PASSED |
| `dec:04` | 0.22s | 0.38s | 2 PASSED |
| `dec:05` | 0.21s | 0.39s | 2 PASSED |
| `dec:06` | 0.21s | 0.57s | 2 PASSED |
| `dec:07` | 0.25s | 0.50s | 2 PASSED |
| `dec:08` | 0.20s | 0.92s | 2 PASSED |
| `dec:10` | 0.19s | 0.45s | 2 PASSED |
| `dec:11` | 0.22s | 0.48s | 2 PASSED |
| `dec:14` | 0.30s | 0.53s | 2 PASSED |
| `dec:16` | 0.19s | 0.54s | 2 PASSED |
| `etkl:01` | 0.20s | 0.33s | 1 SKIPPED (`corpus/` absent, by design) |
| `holon:01` | 0.22s | 0.34s | 1 PASSED |
| `holon:02` | 0.21s | 0.68s | 2 PASSED |
| `holon:03` | 0.18s | 0.62s | 2 PASSED |
| `holon:04` | 0.21s | 0.58s | 2 PASSED |
| `tab:06` | 0.20s | 1.24s | 1 PASSED |

`git worktree add` never exceeded 0.42s; step-2 wall-clock never exceeded 1.24s. **No oracle
refused a worktree** in the sense `tests/test_docgov_extract.py:83-88` refuses a shallow clone
(`git worktree add` is a full second checkout, not a shallow one — the refusal that module
guards against does not apply here, and this was verified rather than assumed: see § below).

---

## Step 3 — the ablation matrix: 17 worktrees × the union of all 25 oracle tests

**Grouping (per §0/C2): one worktree per criterion, all of that criterion's artifact files
removed at once, the UNION of the met set's 25 distinct `prog:oracleTest` ids run once inside
it** — not 272 per-edge worktrees, not 28 per-file worktrees. `_LINE_SUFFIX` stripped before
deletion (per `tests/test_arc_manifest.py:63`).

### An instrument defect found and fixed during this task

The first implementation passed all 25 test ids to **one** `pytest` invocation per worktree.
MEASURED: when the module named by one explicit node id fails to *import* (its own artifact was
just deleted — e.g. `tests/etkl/fixtures.py` for `tab:06`, `tests/corpus-manifest.ttl` for
`etkl:01`), pytest exits `rc=4` ("1 error in 0.1xs") **without running any of the other
explicitly-named ids at all** — even `--continue-on-collection-errors` does not rescue them.
Verified directly (both orderings, and with only the surviving id alongside the broken one:
still "0 items" run). This is specific to **explicit node-id selection**, not to
`--continue-on-collection-errors` in general. Left unfixed, this would have silently reported
"no data" for 16 unrelated tests in the `etkl:01` and `tab:06` rows — a false claim about the
instrument, not a limit of the seam.

**Re-measured 2026-08-22 (fix round 1), transcript below — a throwaway worktree off `HEAD`
(`43815c4`), `tests/corpus-manifest.ttl` removed (the same artifact `etkl:01`'s row removes),
two explicit node ids: the now-unimportable `tests/test_corpus.py::test_expected_verdict[...]`
and a healthy, unrelated sibling `tests/test_boundary.py::test_leak_rejected`.**

```
$ cd "/Volumes/WD Green/dev/git/iladub"
$ WT=/private/.../scratchpad/wt-repro
$ git worktree add --detach "$WT" HEAD
Preparing worktree (detached HEAD 43815c4)
$ rm "$WT/tests/corpus-manifest.ttl"
$ cd "$WT"

$ "/Volumes/WD Green/dev/git/iladub/.venv/bin/python" -m pytest \
    "tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf]" \
    "tests/test_boundary.py::test_leak_rejected" \
    -v --tb=line
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-9.0.3, pluggy-1.6.0 -- .../.venv/bin/python
collecting ... ERROR: found no collectors for .../tests/test_corpus.py::test_expected_verdict

collected 1 item / 1 error

==================================== ERRORS ====================================
____________________ ERROR collecting tests/test_corpus.py _____________________
E   FileNotFoundError: [Errno 2] No such file or directory: '.../tests/corpus-manifest.ttl'
=========================== short test summary info ============================
ERROR tests/test_corpus.py - FileNotFoundError: [Errno 2] No such file or dir...
=============================== 1 error in 0.14s ===============================
EXIT_CODE=4
```

**No `PASSED`/`FAILED` line for `tests/test_boundary.py::test_leak_rejected` appears anywhere in
that output** — "collected 1 item" refers to the healthy node id, but it is never executed; the
run terminates at the collection error with `rc=4`. Adding `--continue-on-collection-errors` to
the same combined invocation produces byte-identical output (same `rc=4`, same missing sibling
result) — the flag does not rescue an explicit node id in a sibling module:

```
$ "/Volumes/WD Green/dev/git/iladub/.venv/bin/python" -m pytest \
    "tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf]" \
    "tests/test_boundary.py::test_leak_rejected" \
    -v --tb=line --continue-on-collection-errors
[... identical: collected 1 item / 1 error, 1 error in 0.09s, EXIT_CODE=4 ...]
```

The same two node ids as **separate invocations** (the fix actually shipped) both report:

```
$ "/Volumes/WD Green/dev/git/iladub/.venv/bin/python" -m pytest \
    "tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf]" -v --tb=line
collected 0 items / 1 error
ERROR tests/test_corpus.py - FileNotFoundError: [Errno 2] No such file or directory: '.../tests/corpus-manifest.ttl'
=============================== 1 error in 0.07s ===============================
EXIT_CODE=4

$ "/Volumes/WD Green/dev/git/iladub/.venv/bin/python" -m pytest \
    "tests/test_boundary.py::test_leak_rejected" -v --tb=line
collecting ... collected 1 item

tests/test_boundary.py::test_leak_rejected PASSED                        [100%]

============================== 1 passed in 0.21s ===============================
EXIT_CODE=0
```

```
$ cd "/Volumes/WD Green/dev/git/iladub"
$ git worktree remove --force "$WT" && git worktree prune
$ git status --porcelain      # clean — real tree untouched
```

The reproduction uses the repo's own modules (`test_corpus.py`, `test_boundary.py`) and the
repo's own artifact (`tests/corpus-manifest.ttl`), not a synthetic throwaway — it is the exact
pair that produced the `etkl:01` row's `COLLECT_ERROR` in the Step 3 sweep, isolated down to two
node ids so the collection-error/sibling-loss mechanism is visible on its own.

**Fix:** one `pytest` subprocess **per test module** (13 modules span the 25 tests), merged into
one outcome map per worktree. A module whose import fails is recorded `COLLECT_ERROR` for every
test id it contains; every other module runs in its own subprocess, unaffected. This is a finding
about **the sweep's own plumbing**, filed here so Task 3 does not reproduce it when building
M19's real runner (M19 must invoke pytest per-module, or per surviving id, when a removed
artifact breaks a shared module's import — never one combined explicit-node-id call across
modules whose fixtures may vanish).

### Positive control (spec's own requirement on Step 3)

**Every one of the 17 criteria's own oracle test(s) FAIL or ERROR when that criterion's own
artifacts are removed.** No criterion's oracle stayed green under self-ablation — so no oracle
in the met set "does not read its own artifact" (the finding the brief names as a possible
outcome, §9.3). `etkl:01` and `tab:06` report `COLLECT_ERROR` rather than `FAILED` — a stronger
signal (the test's own module cannot even import once its artifact is gone), and it counts as a
positive-control pass under the same logic.

### The fail-matrix (criterion whose artifacts were removed → which of the 25 union tests fail/error)

| removed (row) | files removed | union tests that FAIL/ERROR |
| --- | --- | --- |
| `dec:01` | `examples/promotion.ttl`, `tests/dec-bad.ttl`, `vocab/shapes/dec-shapes.ttl` | `test_boundary.py::test_promotion_grounds`, `test_escalation_shacl.py::test_escalation_conformant_passes`, `test_event_shacl.py::*` (2), `test_expansion_request.py::*` (2), `test_timeline_shacl.py::*` (2), `test_vocab_shapes.py::*` (2) — 10 |
| `dec:03` | `examples/transplant/heart-timeline-{conformant,leak}.ttl`, `vocab/shapes/dec-shapes.ttl` | `test_escalation_shacl.py::test_escalation_conformant_passes`, `test_event_shacl.py::*` (2), `test_expansion_request.py::*` (2), `test_timeline_shacl.py::*` (2), `test_vocab_shapes.py::*` (2) — 9 |
| `dec:04` | `examples/transplant/event-{conformant,leak}.ttl`, `vocab/shapes/dec-shapes.ttl` | same shape as `dec:03`'s row — 9 |
| `dec:05` | `examples/expansion-request.ttl`, `tests/expansion-request-leak.ttl`, `vocab/shapes/dec-shapes.ttl` | same shape — 9 |
| `dec:06` | `examples/transplant/transplant-escalation{,-leak}.ttl`, `vocab/shapes/escalation-shapes.ttl` | `test_escalation_shacl.py::*` (2) — own oracle only |
| `dec:07` | `examples/proposal.ttl`, `tests/leak-attempt.ttl`, `vocab/shapes/iladub-shapes.ttl` | `test_boundary.py::*` (3), `test_grounding.py::test_neg_grounded_without_promotion_fails`, `test_hga_alignment.py::test_governed_grounding_conformant` — 5 |
| `dec:08` | `examples/promotion.ttl`, `examples/proposal.ttl`, `vocab/shapes/iladub-shapes.ttl` | `test_boundary.py::*` (3), `test_grounding.py::*`, `test_hga_alignment.py::test_governed_grounding_conformant`, `test_vocab_shapes.py::test_hol_decision_conformant` — 6 |
| `dec:10` | `examples/promotion.ttl`, `examples/proposal.ttl`, `tests/leak-attempt.ttl`, `vocab/shapes/iladub-shapes.ttl` | same as `dec:08`'s row — 6 |
| `dec:11` | `examples/transplant/transplant-risk.ttl`, `tests/risk-leak.ttl`, `vocab/shapes/risk-shapes.ttl` | `test_risk.py::*` (2) — own oracle only |
| `dec:14` | `examples/transplant/transplant-governance.ttl`, `tests/transplant-governance-leak.ttl`, `vocab/shapes/governance-shapes.ttl` | `test_governance.py::*` (2) — own oracle only |
| `dec:16` | `examples/holon-grounding-conformant.ttl`, `tests/holon-grounding-leak.ttl`, `vocab/shapes/iladub-hga-shapes.ttl` | `test_hga_alignment.py::test_{governed,ungoverned}*` (2) — own oracle only |
| `etkl:01` | `tests/corpus-manifest.ttl` | `test_corpus.py::test_expected_verdict[...]` — own oracle only (COLLECT_ERROR) |
| `holon:01` | `vocab/ontology/etkl-holons.ttl` | `test_hga_alignment.py::test_holons_module_standalone` (own) + `test_governed_grounding_conformant`, `test_ungoverned_grounding_rejected` — 3 |
| `holon:02` | `vocab/ontology/iladub-hga-align.ttl` | `test_hga_alignment.py::test_alignment_axioms_present` — own oracle only |
| `holon:03` | `vocab/shapes/iladub-hga-shapes.ttl` | `test_hga_alignment.py::test_{governed,ungoverned}*` (2) — own oracle only |
| `holon:04` | `examples/holon-grounding-conformant.ttl`, `tests/holon-grounding-leak.ttl` | `test_hga_alignment.py::test_{governed,ungoverned}*` (2) — own oracle only |
| `tab:06` | `tests/etkl/fixtures.py` | `test_merge_resolution.py::test_offcenter_merge_escalates` — own oracle only (COLLECT_ERROR) |

Full per-test JSON (17 rows × 25 columns, raw outcomes) reproduced by
`/private/tmp/.../scratchpad/sweep.py` + `analyze.py` (scratch, not committed — re-runnable from
this note's commands).

### The blast-radius finding — A6 (file-disjointness) is necessary but NOT sufficient

Cross-checking the matrix against **each OTHER met criterion's own oracle test(s)** (not just the
ablated criterion's own) finds **44 ordered pairs** `(X removed → Y's own oracle fails)` with
`X ≠ Y`. **26 of the 44 share a `prog:oracleArtifact` file already** — A6 would refuse those
pairs as edges on file grounds alone, so the blast radius there is expected and inert. But
**18 of the 44 do NOT share any declared `prog:oracleArtifact` file** — A6 would **not** catch
these, yet removing X's artifacts still breaks Y's own oracle test. Two distinct causes, both
measured:

1. **A conformant-example test loads a wider shape graph than its own criterion's declared
   artifact.** `tests/test_escalation_shacl.py::test_escalation_conformant_passes` (`dec:06`'s
   *second* oracle test) loads `vocab/shapes/dec-shapes.ttl` **and**
   `vocab/shapes/escalation-shapes.ttl` (`tests/test_escalation_shacl.py:28-31`), while
   `test_escalation_leak_fails` loads only `escalation-shapes.ttl`. So `dec:01`/`dec:03`/`dec:04`/
   `dec:05` (all declaring `dec-shapes.ttl`) each break `dec:06`'s conformant test but not its
   leak test — visible directly in the matrix (`dec:06`'s own row lists both of its tests as
   failing on self-ablation, but `dec:01`'s row shows only
   `test_escalation_shacl.py::test_escalation_conformant_passes`, not the leak test).
2. **`test_hga_alignment.py`'s tests build a knowledge/shape graph wider than any one criterion's
   declared artifact.** Removing `holon:01`'s `vocab/ontology/etkl-holons.ttl`, or `dec:07`'s/
   `dec:08`'s/`dec:10`'s `vocab/shapes/iladub-shapes.ttl`, breaks `test_governed_grounding_conformant`
   and/or `test_ungoverned_grounding_rejected` — the shared oracle tests Q2 already named for
   `dec:16`/`holon:03`/`holon:04` — even though none of those four criteria declares
   `etkl-holons.ttl` or `iladub-shapes.ttl` as their own artifact.

**Consequence for Task 3/4, not resolved here:** among the 130 pairs that satisfy A1–A4+A6, some
will still fail A5's arm 2 (`Y`'s oracle must PASS when `X`'s artifact is removed) for this
reason — not because `Y` truly depends on `X`, but because their oracles share a wider knowledge
graph than their declared artifacts disclose. **This is A5 doing its job** (spec §9, item 2): the
reading was wrong, or under-specified at file granularity (spec §4's stated limitation), and the
edge is refuted rather than asserted. It is named here as a *quantity* (18 pairs, listed above)
so Task 3 does not have to rediscover it while designing M19, and Task 4 should expect a
non-trivial refutation rate from exactly this cause, on top of Q2's shared-test refusals.

---

## Every oracle that could not run in a worktree

**None.** All 17 met criteria's own oracle tests ran to completion (PASS, SKIP, or the expected
ablation FAIL/ERROR) inside a bare `git worktree`, both before and after their own artifacts were
removed. `tests/test_docgov_extract.py:83-88`'s shallow-clone refusal does not fire here because
`git worktree add` produces a full working tree sharing the origin repository's object store —
not a shallow clone — and no oracle in the met set calls `git log` in a way `extract()` does.

The two `COLLECT_ERROR` rows (`etkl:01`, `tab:06`) are **not** environment failures: they are the
correct ablation signal (a test whose own fixture module was just deleted cannot even import,
which is a stronger "fail" than a runtime assertion failure) and are counted as such in the
positive control above. The one real seam this task found is the **plumbing** one recorded above
(explicit multi-module node-id invocations abort entirely on one broken import) — a fact about
how M19 must invoke pytest, not about whether the environment supports the oracle.

---

## Cost bound

Full sweep (17 worktrees, `git worktree add` + step-2 own-test run + artifact removal + step-3
union run over 13 modules + `git worktree remove --force`, sequential, this machine):

**124.91s total** (`git worktree prune` afterward: 0 leftover worktrees, real tree `git status
--porcelain` clean throughout and after). Breakdown: `worktree add` 0.18–0.42s/criterion (≈3.7s
total), step-2 own-oracle run 0.32–1.24s/criterion (≈8.8s total), step-3 13-module union run
5.79–7.08s/criterion (≈112s total, the dominant cost — one pytest subprocess per module, 13
modules × 17 worktrees = 221 subprocess spawns).

An earlier, INCORRECT single-invocation-per-worktree design measured 39.74–40.44s total — faster,
but silently wrong (see the instrument-defect section above): its speed is not a usable baseline.
**124.91s is the true cost of a correct sweep**, and it is the number Task 3 should carry forward:
this leg is affordable on every push and every reviewer's machine, at roughly two minutes,
dominated by process-spawn count rather than any single oracle's runtime.

---

## FALSIFICATION

The instrument is the ablation itself (Global Constraint 8, and this task's own FALSIFICATION
requirement): show it can report a **negative** — an unrelated criterion's oracle still passing
after another criterion's artifacts are removed. §0/C5 already produced one such row
(`dec:14 → dec:11`, `pytest tests/test_governance.py -q` → 5 passed). This task produces a
**different** pair, `dec:01 → dec:11`, both from the matrix above and reproduced fresh in an
isolated worktree:

```
$ cd "/Volumes/WD Green/dev/git/iladub"
$ git status --porcelain                                    # clean before starting
$ WT=/private/.../scratchpad/wt-falsify
$ git worktree add --detach "$WT" HEAD
Preparing worktree (detached HEAD dcd45fd)
$ rm "$WT/vocab/shapes/dec-shapes.ttl" "$WT/examples/promotion.ttl" "$WT/tests/dec-bad.ttl"
$ cd "$WT"
$ "/Volumes/WD Green/dev/git/iladub/.venv/bin/python" -m pytest tests/test_risk.py -v --tb=short
tests/test_risk.py::test_risk_vocab_parses_with_core_terms PASSED        [ 20%]
tests/test_risk.py::test_risk_module_is_standalone PASSED                [ 40%]
tests/test_risk.py::test_risk_alignment_axioms_present PASSED            [ 60%]
tests/test_risk.py::test_transplant_contextual_risk_conformant PASSED    [ 80%]
tests/test_risk.py::test_empiric_risk_stamp_rejected PASSED              [100%]
========================== 5 passed in 0.33s ==========================
$ cd "/Volumes/WD Green/dev/git/iladub"
$ git worktree remove --force "$WT" && git worktree prune
$ git status --porcelain                                    # clean after — real tree untouched
```

`dec:11`'s own two oracle tests (`test_transplant_contextual_risk_conformant`,
`test_empiric_risk_stamp_rejected`) both **PASS** with `dec:01`'s three artifact files deleted.
The instrument does not fail every cell — it discriminates, which is the property the brief's
FALSIFICATION paragraph requires: *"a matrix in which every cell fails is an instrument that is
measuring the worktree, not the edge."* This matrix does not do that: of 272 ordered pairs in the
met set, only 44 show any cross-criterion blast radius at all (Step 3 above), and the other 228
— including this one — show clean discrimination.

**Positive-control counterpart** (same instrument, the other direction): `dec:01`'s **own**
oracle tests (`test_vocab_shapes.py::test_hol_decision_conformant`,
`test_hol_rubber_stamp_rejected`) both **FAIL** under the same removal (Step 3 fail-matrix,
`dec:01` row) — the instrument reports a positive exactly where the artifact was removed and a
negative everywhere it is genuinely unrelated.

---

## Review gate note (spec §4's MEASURE box)

Zero oracles refused a worktree, so this task does not weaken A5 and finds no criterion whose
edges must be demoted to proposition on environmental grounds alone. The 18-pair blast-radius
finding above is a *different* kind of caution — file-declared A6 disjointness does not imply
oracle-level independence — and it is handed to Task 3/4 as measured input, not resolved here.
