# A superseded firing is disposed by publisher truth — Implementation Plan (loop B, tab:05)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:tab:05 — loop B of two; meets tab:05, moves tab:02, meets neither tab:02 nor tab:09.

**Topic:** tab · **Date:** 2026-10-30

**Doc impact: none.** Same ground as the spec: every new term goes in `vocab/internal/corpus.ttl`
(repo-internal, unpublished). No drain is owed.

**Goal:** A `cor:disposes` judged against a snapshot whose firings of that reason are all
superseded is admitted iff that snapshot's publisher truth is perfect on every page the reason fired
on. Apple then disposes MATRIX_AMBIGUOUS and REGION_TILING_FAILED, and tab:05 is met.

**Architecture:** The snapshot writer records each truth table's pages (PROCEDURAL). The lift carries
pages and truth into RDF (PROCEDURAL). `cor:DisposalShape` constraint (4) gains a superseded arm
(AXIOM, closed world, holon-scoped). The oracle test is widened to live ∪ superseded pairs. No compile
change: nothing under `src/` moves.

**Tech Stack:** Python 3, rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), pytest, git.

**Spec:** `docs/superpowers/specs/2026-10-29-a-superseded-firing-disposed-by-truth-design.md` (PR
#383, `929b3c2`). This plan cites its § numbers and does not re-derive them (plan rule 6).

## Global Constraints

- CLAUDE.md § 8: each task names its class. The lift and the writer are PROCEDURAL raw extraction.
  The disposal rule is a SHACL constraint (AXIOM, closed world, **holon-scoped**: every `NOT EXISTS`
  binds the one `?snap` that `$this cor:judgedAgainst` names). No tuned constant anywhere.
- Spec § 2 rule: a superseded firing is disposed **only** by truth proving the adopted reading,
  never by counting it absent.
- Spec R1: page coverage is read from the **dated snapshot blob**, never from `provenance.json` at
  HEAD.
- The reason join stays SPARQL value equality `?reason = ?value` (shape comment, `corpus-shapes.ttl`
  above `cor:DisposalShape`).
- The three M4 tests (spec § 3 M4) stay **byte-unchanged** and green. They are the control.
- **Corpus-baseline inputs** (CLAUDE.md § Corpus baseline): `scripts/corpus_verdict_snapshot.py` and
  `vocab/internal/corpus.ttl` are inputs. Task 3 regenerates **once**, after Tasks 1–2. **No task after
  Task 3 may edit a path under `src/`, `vocab/`, `readings/`, `pyproject.toml`, or the two `scripts/`
  inputs.** If one must, stop and regenerate again; CI's `check` refuses otherwise.
- Every task report carries `## FALSIFICATION` (CLAUDE.md plan rule 4).
- macOS: there is no `timeout`. Read pytest's `N passed` line, never the exit code alone (memory:
  macos-has-no-timeout-command).
- Run tests with `PYTHONPATH=src .venv/bin/python -m pytest …`.

## Measured at `main` `bbac3de` (this session, 2026-10-30) — the seams the spec left open

- **M6 → the JSON shape.** Measured with `git grep -n -E "truth['\"]?\]|\[['\"]truth" -- tests scripts
  src ':!tests/corpus-baseline'`. The readers are `tests/test_ground_truth_floor.py:34-40`, which
  indexes `counts["CORRECT"]` and `counts[k] for k in SIX`, and `tests/test_ground_truth_score.py:297`,
  which indexes named keys. **Neither iterates a table's dict.** Also, `truth_block`'s return value is
  pinned as `{table: {outcome: n}}` by `tests/test_ground_truth_snapshot.py:51` (`["table-1"]["REFUSED"]`).
  **Decision:** the pages go in a **top-level sibling key** `"truth_pages": {"<table>": [<int>, …]}`,
  and `"truth"` stays byte-identical. Nested pages would be safe for today's readers, but they put a
  non-outcome key where any future `for k in counts` reads it as an outcome. A sibling cannot. Each
  snapshot is written with `json.dumps(snap, indent=2, sort_keys=True)`
  (`scripts/corpus_verdict_snapshot.py:153,165`), so the key lands right after `"truth"` and no other
  line moves.
- **M7 → R62 is not this firing, and its subject is gone.** The apple PDF's `cor:sha256` has one
  commit in its history (`06c6b39`, 2026-08-04), so the file never changed. R62's own spec
  (`specs/2026-08-06-quantity-typing-design.md:6,172`) worked on page index 0. The 08-20 census
  (`2026-08-20-escalation-reason-census.md:115`) found `REGION_TILING_FAILED ×4 on p0 and ×4 on p2`,
  which is two sets. Today's apple baseline reads: page 0 score `1.0`, regions
  `{ignored: 2, asserted: 1}`, **no constant-reason region**. All 1 MA + 4 RTF are at index 2,
  superseded. **R62's p0 regions no longer exist; today's p2 set only shares their counts.** Task 7
  closes R62 on that measurement. Per the 2026-08-22 R108 ruling, closing it deletes **both** edges
  that name it: `tests/arc-manifest.ttl:1285` (tab:02) and `:1348` (tab:05).
- **One PR carries everything.** `_durable` (`tests/corpus_firings.py`, `_durable`) returns True
  first when `git rev-parse HEAD:<path>` equals the blob. On the PR branch, HEAD's apple baseline
  **is** the regenerated blob. After a squash-merge, `main`'s first-parent history carries it.
  **The trap:** any later regenerate inside this PR changes HEAD's blob and makes the adjudication
  non-durable (M3). That is why Task 7's blob is read **after** Task 3, and nothing regenerates after
  it.
- **The spec's § 5.5 citation fix is already done.** R74 (`bbac3de`) rewrote tab:05's
  `prog:statement` to "compile.py, every escalate_region call carrying this reason string"
  (`tests/arc-manifest.ttl:1343`). Task 7 does not touch it.
- **Existing disposals carry no truth.** The only `cor:judgedAgainst` snapshots in the manifest are
  bfs and ons (`tests/corpus-manifest.ttl:485,492`). Only apple and Fed have `tests/ground-truth/`
  directories. A shape over lifted truth tables therefore has no existing focus node to break.
- **The term names are free.** `git grep -w` finds 0 hits for `cor:`/`corpus:` + `onPage`, `truth`,
  `TruthTable`, `coversPage`, `outcomeCount`, `OutcomeCount`, `outcome`, `count`.
- **`FiringShape` is not `sh:closed`.** `grep -n sh:closed tests/corpus-shapes.ttl` returns nothing,
  so a new `cor:onPage` on a firing breaks no existing constraint.

## Reconciliations with the spec (plan rule 5) — read before Task 5

1. **O1's first case contradicts O2. The plan resolves it this way.** Spec § 4 O1 asks that a
   superseded-only disposal on a snapshot **with no truth block** refuse "with the arm's own message".
   But `test_refuses_disposal_of_superseded_only_ink` is exactly that case: bfs ROUND_TRIP_FAIL, 0
   live / 6 superseded, and bfs has no truth. It must stay `== {M4}` unchanged (O2, § 5.3 "the
   existing message stays for a reason that fails both arms"). Both cannot hold. **Resolution:** (4b)
   is *engaged* only when the snapshot carries at least one lifted `cor:TruthTable`. With no truth,
   the refusal is `M4` alone. O1's no-truth case is tested as `== {M4}`, which is the control that
   proves the new arm does not swallow the old refusal.
2. **"There is a covering table" (§ 5.3) is weaker than the maintainer's rule (§ 2, "on each covered
   page **every** truth cell is CORRECT").** If a page is covered by two tables and one is imperfect,
   § 5.3's existential would admit it, and the § 2 rule refuses it. **The ruling prevails:** every
   table covering a firing page must be perfect, and at least one must cover it. Apple has one table,
   so the real disposal is the same under both readings. Review Focus 1 pins the difference.
3. **Six new parameters, not four.** O5 counts "the four *other*" superseded-only pairs. The widened
   set adds **six** parameters: apple MA and apple RTF (green after Task 7), plus bfs
   BOXHEAD_EXCEEDS_RECORD, bfs ROUND_TRIP_FAIL, ons REGION_TILING_FAILED and ons ROUND_TRIP_FAIL
   (strict xfail). Both statements agree once the apple pair is counted.

## Review Focus

1. **Two truth tables on one firing page, one perfect and one not.** The disposal is refused with
   the imperfect-table message. Pinned in Task 5.
2. **An old blob: `"truth"` present, `"truth_pages"` absent** (every apple/Fed blob before Task 3).
   The lift emits no `cor:TruthTable`, so the disposal is refused with `M4`, never admitted on missing
   pages. Pinned in Tasks 4 and 5.
3. **`"truth_pages"` names a table `"truth"` lacks, or the reverse.** The lift raises `ValueError`
   naming the snapshot (a producer-side guard, CLAUDE.md § Producer-side guards: the membrane never
   sees the JSON). Pinned in Task 4.
4. **A "benign-looking" outcome above 0: `MARKED_LABEL: 1`.** Refused as imperfect. The perfect
   condition is "CORRECT > 0 and **every** other recorded outcome is 0", read generically over
   whatever outcomes the blob holds, so a future outcome key blocks rather than slips through.
   Pinned in Task 5.
5. **A reason that fires live on one page and superseded on another.** (4a) admits it as today, and
   no (4b) message fires. Pinned in Task 5.

---

### Task 1: The snapshot records each truth table's pages (PROCEDURAL)

**Files:**
- Modify: `scripts/corpus_verdict_snapshot.py` (`truth_block`, `snapshot`)
- Test: `tests/test_ground_truth_snapshot.py`

**Interfaces:**
- Produces: `snapshot(pdf_path)` returns a dict that, when a truth directory exists, carries
  `"truth"` (unchanged: `{table: {outcome: int}}`) **and** `"truth_pages"`: `{table: [int, …]}`, with
  the same table keys and the pages exactly as `iladub.truth.load_truth` returns them. If no truth
  directory exists, neither key appears.
- `truth_block(stem, rep, root)`'s return type is **unchanged** (pinned at
  `test_ground_truth_snapshot.py:51`). How the pages reach `snapshot` is the implementer's choice: a
  second function, or a tuple-returning helper both call. Two invariants: `load_truth` stays the
  only reader of `provenance.json`, and the tables' key sets are equal by construction.

- [ ] **Step 1: Write the failing tests** in `tests/test_ground_truth_snapshot.py`, reusing its
  `_rep()` and tmp-dir conventions (read `:1-55` first):
  - a truth directory with `table-1.csv` and `provenance.json` `{"pages": [2]}` → the pages function
    gives `{"table-1": [2]}`;
  - two CSVs with `provenance.json` `{"pages": [0, 3]}` → both tables map to `[0, 3]`;
  - no truth directory → `None`, matching `truth_block`.
- [ ] **Step 2: Run them, expect FAIL** (name not defined).
  `PYTHONPATH=src .venv/bin/python -m pytest tests/test_ground_truth_snapshot.py -v`
- [ ] **Step 3: Implement.** Also wire `snapshot()` to set `snap["truth_pages"]` beside
  `snap["truth"]`. Write the docstring's class line as CLAUDE.md § 8 asks: *PROCEDURAL, it
  serialises a Python result and decides nothing* (spec § 5.1).
- [ ] **Step 4: Run** the file plus `tests/test_ground_truth_floor.py tests/test_ground_truth_score.py`.
  Expect all passed. The floor and score tests still read the **old** committed baseline, which is
  the point: they don't depend on the new key.
- [ ] **Step 5: FALSIFICATION.** Make the pages function return `[]` for every table. Show the
  `[2]` test failing. Restore with `cp` from a saved copy (memory: falsification-and-ci-mechanics)
  and show the file green.
- [ ] **Step 6: Commit** `feat(snapshot): the truth block's pages are recorded beside it (loop B, tab:05)`.

### Task 2: Declare the eight terms (vocabulary, before the regenerate)

**Files:**
- Modify: `vocab/internal/corpus.ttl` (a new section after `#  Snapshots …`, around `:280`)
- Modify, **only if Step 3 shows it moved**: `tests/test_artifact_terms.py` (the census constants
  and their dated comment, about `:440`)

**Interfaces — Produces** (spec § 5.2; each `rdfs:comment` cites the spec path and says *LIFTED,
NEVER AUTHORED* as `corpus:Firing`'s comment does at `:247`):

| term | kind | domain → range |
|---|---|---|
| `corpus:onPage` | DatatypeProperty | `corpus:Firing` → `xsd:nonNegativeInteger`. A 0-based page index of the blob's `pages` list (spec M2) holding a firing of this reason, of any verdict. |
| `corpus:truth` | ObjectProperty | `corpus:Snapshot` → `corpus:TruthTable` |
| `corpus:TruthTable` | Class | one publisher truth table as scored in a dated snapshot blob |
| `corpus:coversPage` | DatatypeProperty | `corpus:TruthTable` → `xsd:nonNegativeInteger` |
| `corpus:outcomeCount` | ObjectProperty | `corpus:TruthTable` → `corpus:OutcomeCount` |
| `corpus:OutcomeCount` | Class | one (outcome, count) pair of a truth table |
| `corpus:outcome` | DatatypeProperty | `corpus:OutcomeCount` → `rdfs:Literal`. The outcome key exactly as the blob spells it (`"CORRECT"`, `"UNCLAIMED"`, …). |
| `corpus:count` | DatatypeProperty | `corpus:OutcomeCount` → `xsd:nonNegativeInteger` |

**Why pairs, not one property per outcome (spec § 5.2 leaves it to the plan):** the membrane's
"no other outcome above 0" must hold over outcomes nobody has named yet. A property per outcome
silently admits a tenth outcome the shape doesn't list. A pair is refused by the generic
`?o != "CORRECT"` test. Say this in `corpus:OutcomeCount`'s comment.

- [ ] **Step 1: Write** the section. Parse check:
  `.venv/bin/python -c "import rdflib;rdflib.Graph().parse('vocab/internal/corpus.ttl')"`.
- [ ] **Step 2: Run** `PYTHONPATH=src .venv/bin/python -m pytest tests/test_artifact_terms.py tests/test_artifact_declarations.py tests/test_source_ownership.py tests/test_doc_governance.py -q`.
- [ ] **Step 3: MEASURE, don't predict.** If a census assertion fails, record the measured
  before/after numbers in the dated comment block, in the house form (`# N / M since loop B task 2
  (MEASURED): …`, naming which terms moved which count and why). **Do not adjust a number you didn't
  see fail.** Task 4 and Task 5 add `sh:path` uses of these terms to `tests/corpus-shapes.ttl`, which
  can move the *historical* count again. Each of those tasks re-runs this step.
- [ ] **Step 4: FALSIFICATION.** Delete `corpus:coversPage`'s declaration and run the census tests.
  If they still pass, record that the term is not yet demanded (it will be after Task 4). Restore.
- [ ] **Step 5: Commit** `vocab(corpus): truth tables and firing pages, lifted never authored (loop B, tab:05)`.

### Task 3: Regenerate the corpus baseline once (PROCEDURAL, 24 minutes, serial)

**Files:** `tests/corpus-baseline/*.json`, `tests/corpus-baseline/inputs.json`

- [ ] **Step 1: Preconditions.** `git status --porcelain` prints nothing, and Tasks 1–2 are
  committed (`regenerate` refuses untracked inputs). `baml_client/` resolves in this checkout: a fresh worktree lacks it, so symlink it
  first, or the numbers are wrong (memory: resume, session 8). Nothing else compiles the corpus on
  this machine (memory: corpus-runs-are-serial). No pytest is running.
- [ ] **Step 2: Run** `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` in the
  background, and block on its completion in-turn (memory: controller-never-idles).
- [ ] **Step 3: O6, the blast radius.** Run `git diff --stat -- tests/corpus-baseline/`. **Expected
  (PROPOSED, spec § 8):** exactly three files change. These are `apple-fy2026q3-statements.json` and
  `fed-h41-2025-01-02.json`, each gaining one `"truth_pages"` key and nothing else, and
  `inputs.json`. Check the first two with
  `git diff -U0 -- tests/corpus-baseline/apple-fy2026q3-statements.json` and Fed's equivalent.
  Expected values: apple `"truth_pages": {"table-1": [2]}`, Fed `{"table-1": [0]}`. **If any other
  byte moves, stop. Do not commit. Diagnose:** nothing this loop touched compiles, so a moved
  region is either nondeterminism or a missing `baml_client`.
- [ ] **Step 4:** `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py check`. Expect OK.
- [ ] **Step 5: Commit** `baseline: truth pages recorded (loop B, tab:05) — O6 blast radius: 2 truth_pages keys + inputs.json`,
  with the `--stat` output in the body.
- [ ] **Step 6: Record** the new apple blob for Task 7:
  `git rev-parse HEAD:tests/corpus-baseline/apple-fy2026q3-statements.json`.

FALSIFICATION for this task is the O6 diff itself: it is a prediction that could have failed and
was read, not assumed.

### Task 4: The lift carries pages and truth (PROCEDURAL)

**Files:**
- Modify: `tests/corpus_firings.py` (`_count_firings`, `_emit_firings`, `lift_snapshots`, and the
  module docstring's class paragraph)
- Modify: `tests/corpus-shapes.ttl` (well-formedness only: `cor:onPage` on `cor:FiringShape`, and a
  new `cor:TruthTableShape` and `cor:OutcomeCountShape`)
- Test: `tests/test_corpus_firings.py`

**Interfaces:**
- Consumes: the blob keys `"truth"` and `"truth_pages"` (Task 1), and the terms (Task 2).
- Produces:
  - `_count_firings(pdf, data)` additionally yields, per reason, the **set** of page indices
    (`enumerate(data["pages"])`, spec M2) carrying a firing of any verdict. The return arity is the
    implementer's choice, but **both** lifts consume it (spec § 5.2: the two must not drift).
  - `_emit_firings` emits one `cor:onPage` literal (`xsd:nonNegativeInteger`) per page index on each
    `cor:Firing`. `lift_firings` therefore gains `cor:onPage` too, and gains **no** truth.
  - `lift_snapshots`, per snapshot whose blob has both keys, emits for each table a `cor:TruthTable`
    bnode via `?snap cor:truth ?t`. Each one carries one `cor:coversPage` per page and one
    `cor:outcomeCount [ a cor:OutcomeCount ; cor:outcome "<KEY>" ; cor:count n ]` per key of that
    table's counts.
  - Blob with `"truth"` and no `"truth_pages"`: **no** `cor:TruthTable` (Review Focus 2). Blob with
    `"truth_pages"` alone, or key sets that differ: `ValueError` naming `f"{path}@{blob}"` (Review
    Focus 3). A count that is not a non-negative int: `ValueError`.
- Shapes: `FiringShape` gains `sh:property [ sh:path cor:onPage ; sh:datatype xsd:nonNegativeInteger ]`
  with **no `sh:minCount`**. The authored `FIRING`/`OK_FIRING` fixtures in
  `tests/test_corpus_manifest.py:106-116` carry no page, and `test_admits_a_well_formed_firing` must
  stay green. `TruthTableShape` (`sh:targetClass cor:TruthTable`): `cor:coversPage` minCount 1,
  datatype nonNegativeInteger; `cor:outcomeCount` minCount 1. `OutcomeCountShape`: exactly one
  `cor:outcome`, exactly one `cor:count` (nonNegativeInteger).

- [ ] **Step 1: Write the failing tests** in `tests/test_corpus_firings.py`. Add a module-level helper
  `_commit_json(repo, data, msg)` beside `_commit` (`:154`). It writes an arbitrary dict to `_PATH`
  and returns the blob. Tests:
  - a blob with two pages, `R_X` escalated on page 0 and superseded on page 1 → the snapshot firing
    for `R_X` has `cor:onPage` exactly `{0, 1}`;
  - `lift_firings` on the real baseline: apple's `MATRIX_AMBIGUOUS` firing has `cor:onPage` exactly
    `{2}` (real input, spec § 6 second bullet);
  - a blob with `"truth": {"t": {"CORRECT": 3, "LOST": 0}}` and `"truth_pages": {"t": [1]}` → one
    `cor:TruthTable` on the snapshot, `coversPage {1}`, outcome pairs exactly
    `{("CORRECT", 3), ("LOST", 0)}`;
  - Review Focus 2: the same blob without `"truth_pages"` → zero `cor:truth` triples;
  - Review Focus 3: `"truth_pages": {"other": [1]}` → `pytest.raises(ValueError, match=…@…)`;
  - **real blob:** inject a `cor:judgedAgainst` for apple at `HEAD:` its baseline path, the way
    `tests/test_corpus_manifest.py::_with_disposal` does. Apple's snapshot then lifts one
    `cor:TruthTable` covering `{2}`, with `("CORRECT", 57)` and every other pair count 0;
  - `test_real_lift_conforms_to_firing_shape` (`:130`) stays green with the new shapes.
- [ ] **Step 2: Run, expect FAIL.** `PYTHONPATH=src .venv/bin/python -m pytest tests/test_corpus_firings.py -v`
- [ ] **Step 3: Implement.** Update the module docstring: `lift_snapshots` now also emits the blob's
  truth tables. It is the same PROCEDURAL class for the same reason, and it judges nothing.
- [ ] **Step 4: Run** `tests/test_corpus_firings.py tests/test_corpus_manifest.py tests/test_corpus.py -q`.
  Expect all passed, with the same xfail count as before. Then re-run Task 2 Step 3's census.
- [ ] **Step 5: FALSIFICATION** (two). (a) Make `_count_firings` record only the first page of each
  reason, and show the `{0, 1}` test failing. (b) Delete the "truth without truth_pages → nothing"
  branch so it emits a table with no pages. Show the Review-Focus-2 test failing **and**
  `TruthTableShape`'s minCount refusing it. Restore each with `cp`; show green.
- [ ] **Step 6: Commit** `feat(corpus): the lift carries firing pages and the snapshot's truth (loop B, tab:05)`.

### Task 5: Constraint (4) gains a superseded arm (AXIOM, constraint, closed world)

**Files:**
- Modify: `tests/corpus-shapes.ttl` (`cor:DisposalShape` constraint (4), and its comment block above
  `:115`)
- Test: `tests/test_corpus_manifest.py`

**Interfaces — the contract the SHACL must satisfy.** The SPARQL is the implementer's to write.
Every closed-world guard binds `?snap` via `$this cor:judgedAgainst ?snap`. The reason join is
`?reason = ?value`. Write `F(v)` for "the snapshot's firing whose reason equals `v`".

| message | refuses `cor:disposes ?value` iff |
|---|---|
| `M4` (**text unchanged**) | no `F(?value)` has `cor:live > 0`, **and** (no `F(?value)` has `cor:superseded > 0`, **or** `?snap` has no `cor:truth`) |
| `M4U` | no live `F`, a superseded `F`, `?snap` has ≥ 1 `cor:truth`, and some `cor:onPage ?p` of `F` is `cor:coversPage`d by **no** truth table of `?snap` |
| `M4I` | no live `F`, a superseded `F`, `?snap` has ≥ 1 `cor:truth`, and some `cor:onPage ?p` of `F` is covered by a truth table of `?snap` that is **imperfect**: it has no pair `("CORRECT", n>0)`, **or** it has a pair `(o, n>0)` with `o != "CORRECT"` |

Message strings, verbatim (the tests pin them):

```
M4U = "cor:disposes names a reason whose ink in the snapshot is superseded only, on a page no truth table of that snapshot covers"
M4I = "cor:disposes names a reason whose ink in the snapshot is superseded only, on a page covered by a truth table that is not perfect (CORRECT is 0, or another outcome is above 0)"
```

Each is its own `sh:sparql` constraint, so `_d2_refusals` reports which one refused. Rewrite the
comment block as a **dated addendum** (*"(4) gained a superseded arm 2026-10-30, spec
2026-10-29-a-superseded-firing…, § 5.3 + this plan's Reconciliations 1–2"*), stating that the arm
derives nothing (§ 8: it is a membrane on what may count as disposed). Its sentence *"one whose ink
is all superseded … refused by (4)"* is now true only without truth, so append the correction, don't
rewrite it.

- [ ] **Step 1: Write the failing tests.** Add to `tests/test_corpus_manifest.py`:
  - `M4U`/`M4I` constants as above.
  - A helper `_apple_variant(tmp_path, mutate)`. It loads the **committed** apple baseline JSON
    (post-Task-3, so it carries `truth_pages`), sets `"pdf"` to `"corpus/fam/a.pdf"`, applies
    `mutate(data)`, commits it via `tests.test_corpus_firings._commit_json` into `_repo(tmp_path)`,
    and `_publish`es. It returns the lifted graph of a synthetic manifest whose `urn:d:a`
    adjudication disposes `"MATRIX_AMBIGUOUS"` judged against that blob. Generalise `_synthetic` with
    a `reason` parameter defaulting to `"R_X"`, so every existing caller is byte-unchanged in
    behaviour.
  - Cases, each asserting `_d2_refusals(g) == {…}` exactly:

    | case | mutate | expected |
    |---|---|---|
    | O3 control, real blob | identity | `set()` |
    | O1 no truth | drop `"truth"` and `"truth_pages"` | `{M4}` (Reconciliation 1) |
    | RF2 old blob | drop `"truth_pages"` only | `{M4}` |
    | O1 uncovered | `truth_pages["table-1"] = [0]` | `{M4U}` |
    | O1 non-CORRECT | `truth["table-1"]["WRONG_VALUE"] = 1` | `{M4I}` |
    | O1 UNCLAIMED | `truth["table-1"]["UNCLAIMED"] = 1` | `{M4I}` |
    | O1 CORRECT 0 | `truth["table-1"]["CORRECT"] = 0` | `{M4I}` |
    | RF4 | `truth["table-1"]["MARKED_LABEL"] = 1` | `{M4I}` |
    | RF1 two tables | add `"table-2"`: apple's counts with `LOST: 1`, pages `[2]` | `{M4I}` |
    | RF5 live elsewhere | append to page 0 one region `{"reason": "MATRIX_AMBIGUOUS", "verdict": "escalated"}` (copy the other keys from an existing region) | `set()` |

  - The three M4 tests (`:210`, `:214`, `:264`) are **not edited**.
- [ ] **Step 2: Run, expect FAIL** on O3, RF5 and every M4U/M4I case:
  `PYTHONPATH=src .venv/bin/python -m pytest tests/test_corpus_manifest.py -v`
- [ ] **Step 3: Implement** the three constraints.
- [ ] **Step 4: Run** `tests/test_corpus_manifest.py tests/test_corpus_firings.py tests/test_corpus.py -q`.
  Expect all passed, with the xfail count unchanged. Re-run Task 2 Step 3's census.
- [ ] **Step 5: FALSIFICATION** (the spec's own, § 6, and one more). (a) Delete (4b)'s "has a
  `CORRECT` pair with n > 0" conjunct. Show **O1 CORRECT 0** failing (it admits). (b) Turn the
  "every covering table perfect" condition into an existential, and show **RF1** failing. Restore each
  with `cp`; show green.
- [ ] **Step 6: Commit** `feat(corpus): a superseded firing is disposed only by perfect publisher truth (loop B, tab:05)`.

### Task 6: The oracle sees superseded firings (test code)

**Files:**
- Modify: `tests/corpus_firings.py` (add `firing_pairs`)
- Modify: `tests/test_corpus.py` (`:199-234`)

**Interfaces:**
- Produces: `firing_pairs(graph) -> list[tuple[str, str]]`, which returns sorted (document IRI,
  reason) pairs with `cor:live + cor:superseded > 0`. It skips non-`URIRef` subjects for the same
  reason `live_pairs` does (snapshots are not documents). `live_pairs` stays; check with `git grep`
  whether it still has callers, and delete it if it has none.
- `test_escalation_reasons_are_adjudicated` parametrises over `firing_pairs(ADJUDICATED)`. Its
  docstring, the xfail reason (`"fires live on"` → `"fires on"`) and the assertion message stop
  saying LIVE.

- [ ] **Step 1: Write the failing test** in `tests/test_corpus.py`:
  `test_the_oracle_covers_every_firing_pair`. It asserts that
  `set(firing_pairs(ADJUDICATED)) - set(live_pairs(ADJUDICATED))` is exactly the six pairs of
  Reconciliation 3 (apple MA, apple RTF, bfs BOXHEAD_EXCEEDS_RECORD, bfs ROUND_TRIP_FAIL, ons
  REGION_TILING_FAILED, ons ROUND_TRIP_FAIL, using full `urn:iladub:corpus:` IRIs). If `live_pairs`
  is deleted in Step 3, compute the live set inline with the same SPARQL-free loop.
- [ ] **Step 2: Run, expect FAIL** (`firing_pairs` undefined).
- [ ] **Step 3: Implement.** Move the parametrisation.
- [ ] **Step 4: Run** `PYTHONPATH=src .venv/bin/python -m pytest tests/test_corpus.py -k "adjudicated or oracle_covers" -v -rx`.
  **Expected (O5):** six new parameters, **all six strict xfail** (apple's adjudication lands in
  Task 7). Every parameter that existed before keeps its outcome; compare against a `-rx` run saved
  before Step 3.
- [ ] **Step 5: FALSIFICATION.** Make `firing_pairs` return `live_pairs`'s set. Show
  `test_the_oracle_covers_every_firing_pair` failing. Restore.
- [ ] **Step 6: Commit** `test(corpus): the adjudication oracle covers superseded firings (loop B, tab:05; spec R2)`.

### Task 7: Apple's adjudication, R62, and tab:05 met

**Files:**
- Modify: `tests/corpus-manifest.ttl` (append a new dated section **at the end**, as the 2026-10-19
  section does at `:473-480`, so no earlier line moves)
- Modify: `tests/arc-manifest.ttl` (tab:05 block `:1339-1349`; the tab:02 `prog:blockedBy` at `:1285`)
- Modify: `docs/superpowers/residues.md` (strike R62's index line)
- Modify: `docs/superpowers/residues-open.md`, `docs/superpowers/residues-closed.md`, and whatever
  tests pin residue state. **MEASURE the closure pattern first:**
  `git show bbac3de -- docs/superpowers/residues*.md tests/test_residue_graph.py`. R74 is the most
  recent closure; copy its form exactly, including whether `residues-open.md` loses or keeps the
  row (it is Evidence, append-only, CLAUDE.md § Documentation governance).

**Interfaces:**
- Consumes: the apple blob from Task 3 Step 6 (re-read it now and confirm it equals
  `git rev-parse HEAD:tests/corpus-baseline/apple-fy2026q3-statements.json`).
- The adjudication: `cor:by` names the agent and François Rosselet's review-and-merge as the sign-off
  (house form, `:483`); `cor:on "2026-10-30"^^xsd:date`;
  `cor:disposes "MATRIX_AMBIGUOUS" , "REGION_TILING_FAILED"`;
  `cor:judgedAgainst [ a cor:Snapshot ; cor:recordedIn "tests/corpus-baseline/apple-fy2026q3-statements.json" ; cor:blob "<Task 3 blob>" ]`;
  `cor:recordedIn` the spec path. The rationale states the proof, measured: 1 MA + 4 RTF, all
  superseded, all page 2; `truth.table-1` 57 CORRECT, every other outcome 0, pages [2]. It also states
  what it does **not** dispose: DATAGRID_RESIDUE live on p2 (tab:08), and the whole-table condition
  being sufficient but not tight (spec § 7).

- [ ] **Step 1:** Run
  `PYTHONPATH=src .venv/bin/python -m pytest tests/test_corpus.py -k adjudicated -rx` and confirm
  the two apple parameters are strict xfail **before** the change.
- [ ] **Step 2: Append** the adjudication. Run the same command plus
  `tests/test_corpus_manifest.py::test_manifest_conforms`. **Expected (O3, O4):** both apple
  parameters pass, the other four stay xfail, and the manifest conforms. Add one explicit test to
  `tests/test_corpus_manifest.py`: over the real manifest plus both lifts, `_d2_refusals(g, focus=<apple's
  new adjudication>) == set()`.
- [ ] **Step 3: R62 closure** (M7 above). The closure evidence: the PDF's sha has one commit;
  apple p0 now scores `1.0` with no constant-reason region; today's p2 firings are a different set
  that shares the counts, disposed by the new adjudication. Delete **both** `"R62"` edges (`:1285`
  tab:02 keeps R43 and R44; `:1348` tab:05 loses its only edge). Leave a `# DELETED 2026-10-30` comment
  at each site in the form tab:01's `:1255` uses.
- [ ] **Step 4: tab:05.** `prog:met true` plus `prog:metOn "2026-10-30"^^xsd:date` (copy tab:01's
  exact predicate spelling from its block). Append a dated comment above the block saying how it is
  met: arm (a) apple, disposed by publisher truth, with this plan's path. **Do not repair** the
  2026-08-20 lines above it (`:1339-1340` "kept, not repaired" practice), or the `# FIRES n` comments
  (R237).
- [ ] **Step 5: Run** `tests/test_arc_manifest.py tests/test_residue_graph.py tests/test_corpus.py tests/test_corpus_manifest.py tests/test_doc_governance.py -q`.
  If the manifest test's M8 or a "met criteria" pin moves, read the failure and update the pin with a
  dated comment. Never loosen it.
- [ ] **Step 6: FALSIFICATION (O4)**, in three parts.
  - (a) Delete `cor:disposes "MATRIX_AMBIGUOUS"` from the new adjudication. The xfail mark is
    computed from the manifest at collection (`_adjudication_param`), so the parameter must flip
    from `PASSED` to `XFAIL`. Show that flip in `-rx` output. A flip is the only signal a strict-xfail
    oracle gives, so a run still reading `PASSED` means the oracle cannot see the disposal.
  - (b) With the mark forced off (temporarily replace `marks` with `()` in `_adjudication_param`),
    show the same parameter **failing** its assertion.
  - (c) Restore the disposal and point `cor:blob` at the pre-Task-3 apple blob,
    `git rev-parse main:tests/corpus-baseline/apple-fy2026q3-statements.json` (exact as long as the
    branch is cut from `main` before Task 3). Show the apple adjudication's `_d2_refusals` returning
    `{M4}`: the old blob has `truth` but no `truth_pages`, so the lift emits no table. That is R1 and
    Review Focus 2 on real input.

  Restore each with `cp`; show green.
- [ ] **Step 7: Commit** `feat(tab): apple's superseded matrix firing is disposed by publisher truth — tab:05 met; R62 closed (loop B)`.

### Final: the whole branch

- [ ] `PYTHONPATH=src .venv/bin/python -m pytest -q` (the CI selection). Read the `N passed, M xfailed` line.
- [ ] `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py check` → OK, and `verify` →
  12/12 byte-equal. `verify` compiles; it is serial and takes about 24 minutes.
- [ ] `git diff main --stat -- src/` is **empty** (spec § 7: no compile change).
- [ ] Whole-branch review (superpowers:requesting-code-review). Then push, open the PR with
  `**Serves:** prog:criterion:tab:05` and the O6 `--stat` in the body, and set auto-merge (squash).
  If merge slips past 2026-10-30, fix the date in the adjudication's `cor:on`, tab:05 `metOn`, the
  DELETED comments and the R62 closure.
