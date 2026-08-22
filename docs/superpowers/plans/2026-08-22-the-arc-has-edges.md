# The arc has edges — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `tests/arc-manifest.ttl` a criterion→criterion dependency graph, graded into an
asserted half that a two-sided ablation grounds and a proposed half that carries a rationale, so
*"what must land before X"* is a derivation and not a reading.

**Architecture:** Two predicates over the existing manifest (`prog:dependsOn`,
`prog:proposedDependsOn`); seven new closed-world refusals in `tests/arc-shapes.ttl` (M12–M18); one
open-world procedural leg (M19) that grounds direction by deleting a file inside a throwaway
`git worktree` and reading a pytest exit code; three new SPARQL derivations; one generated,
regenerate-and-diff-gated landscape file.

**Tech Stack:** rdflib 7.6.0 + pySHACL (`inference="rdfs"`, `advanced=True`), pytest, `git worktree`,
`./.venv/bin/python` **only**.

**Spec:** `docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md`
**Origin handoff:** `docs/superpowers/2026-08-22-arc-edges-spec-handoff.md`

**Doc impact: increment.** One generated artifact enters the tracked tree
(`docs/superpowers/arc-dependency-landscape.md`, Task 6), under the generated-cache exception
`CLAUDE.md` § Documentation governance already carries. No Assertion-class page changes, no
release-blocking contradiction.

---

## §0 The plan author's adversarial pass — four corrections to the spec, each MEASURED

The origin handoff asked for this pass explicitly. All four findings were measured on branch
`the-arc-has-edges` @ `b3ffaa1`, whose `tests/arc-manifest.ttl` is **byte-identical to `main` @
`fd6c81b`** (`git diff --stat fd6c81b HEAD -- tests/arc-manifest.ttl` → empty), so they bear
directly on the spec's own tree.

### C1 — Spec §2 Q5 and Q6 are wrong: the met set names **28** distinct artifact files, not 11

`prog:oracleArtifact` and `prog:oracleTest` are **multi-valued** — eleven of the seventeen met
criteria carry 2 tests and 3–4 artifacts each. Q5's figure comes from a single-valued read
(rdflib's `Graph.value()` returns one arbitrary object of many).

```
$ ./.venv/bin/python  # rdflib 7.6.0, tests/arc-manifest.ttl
criteria 43 met 17
distinct files via objects(): 28
distinct files via value()  : 11
```

Per-criterion multiplicity, measured: `dec:01,03,04,05,06,07,08,11,14,16` → 2 tests / 3 artifacts;
`dec:10` → 2 / 4; `holon:02,03` → 2 / 1; `holon:04` → 2 / 2; `etkl:01`, `holon:01`, `tab:06` → 1 / 1.

Three consequences, and they are load-bearing:

1. **A3 and A6 must be defined over SETS, not scalars.** "`oracleTest(X) ≠ oracleTest(Y)`" has no
   meaning when both sides are sets of two. The reading that carries A3's *argument* (a shared test
   makes both ablation arms fail for the same reason) is **disjointness**: refuse if X and Y share
   **any** oracle test. Same for A6 at file granularity: refuse if they share **any** artifact file.
2. **The assertable envelope moves.** Measured under set semantics over the 17 met criteria
   (272 ordered pairs): A4 strict **123**, A4 non-strict **149**, non-strict + A3 **140**,
   non-strict + A3 + A6 **130** — of which intra-`holon` **10**, intra-`dec` **45**. The spec's
   142/132 were computed single-valued; the shape of its conclusion survives (the membrane is a
   filter, not a wall) and the numbers do not.
3. **Q5's cost model is superseded — see C2.**

### C2 — the ablation groups by **criterion**, not by file: ≤ 17 worktrees, not 28

Spec §4 groups worktrees by removed artifact *file* (Q5: "11 worktrees"). With 28 files that is
worse, not better. The correct grouping falls out of what the two arms actually ask:

> One worktree per criterion **C that appears as an endpoint of an asserted edge**, with **all** of
> C's artifact files removed at once. Inside it: arm 1 runs the oracle tests of every X with
> `X dependsOn C`; arm 2 runs the oracle tests of every Y with `C dependsOn Y`.

A6 guarantees the removed set is disjoint from the artifacts of every criterion whose tests run
there, so nothing is conflated. The bound is **the number of endpoint criteria, ≤ 17**, whatever the
edge count. Task 3 builds this grouping; Task 1 measures its cost.

### C3 — `prog:dependencyRationale` as spec'd has **no subject to attach to**

Spec §3 gives `prog:dependencyRationale xsd:string, on propositions only`, and M18 wants *exactly
one per proposition*. A proposition is a plain triple `X prog:proposedDependsOn Y`; a literal hung
on `X` cannot say **which** proposed edge it explains, and a criterion with two proposed targets
makes "exactly one" unstatable. RDF-star would break the property paths §3's whole argument rests on.

**The plan's resolution, and it changes no argument in §3:** the rationale rides a standard
`rdf:Statement` reification node beside the direct triple. The direct triple stays, so
`(prog:dependsOn|prog:proposedDependsOn)+` is untouched:

```turtle
prog:criterion:tab:07 prog:proposedDependsOn prog:criterion:tab:06 .

[] a rdf:Statement ;
   rdf:subject   prog:criterion:tab:07 ;
   rdf:predicate prog:proposedDependsOn ;
   rdf:object    prog:criterion:tab:06 ;
   prog:dependencyRationale "reading: … ; ungroundable because …" .
```

Reification is the W3C form for exactly this and is not new vocabulary (CLAUDE.md § Holonic
interaction model: align, don't reinvent). M18 becomes a statement about these nodes (Task 2).

### C4 — a **refuted** edge cannot be demoted; deletion is the only membrane-legal outcome

Spec §9.2 says a refuted edge may be *"deleted or demoted with a rationale"*. **M17 forbids the
demotion.** If X and Y satisfy A1–A4 + A6 — which they must have, or A5 never ran — then a
`prog:proposedDependsOn` between them is precisely what M17 refuses. So for a refuted edge the only
legal outcome is **deletion**, and the refutation is recorded in the loop's evidence file, never in
the graph (spec §3 already forbids a stored `prog:ablation` record for the same reason).

This is not a hole to patch: a refuted reading is *disproved*, not merely ungrounded, and CLAUDE.md
§3's "never dropped" governs propositions, not disproved claims. But the loop **must** write each
refutation down where a later author will find it, or the same edge gets re-authored and
re-refuted. Task 4 requires it.

### What §0 does NOT change

A4 stays **non-strict** (Q3's argument is untouched by any of the above, and C5 below is direct
evidence for it). A6 stays. The two-predicate split stays. Nothing here weakens a refusal.

### C5 — a measured existence proof: at least one edge IS groundable, and it is intra-rung

The risk this plan most needed to retire is *"the ablation refutes everything and the asserted graph
ships empty."* MEASURED 2026-08-22, four throwaway worktrees off `HEAD`, `.venv` interpreter by
absolute path, `cwd` inside the worktree:

| probe | command (inside the worktree) | result |
| --- | --- | --- |
| worktree is usable at all | `git worktree add --detach $WT HEAD` | **0.4s**, no `.venv` inside it |
| an oracle runs there | `pytest tests/test_hga_alignment.py -q` | **6 passed in 0.29s** |
| ablation bites | `rm vocab/shapes/iladub-hga-shapes.ttl` then the same | **2 failed, 4 passed** |
| **arm 1 for `holon:03 → holon:01`** | `rm vocab/ontology/etkl-holons.ttl`; `pytest tests/test_hga_alignment.py tests/test_source_ownership.py -q` | **3 failed, 6 passed** — including both of `holon:03`'s oracles |
| arm 2 for the same edge | `rm vocab/shapes/iladub-hga-shapes.ttl`; `pytest tests/test_hga_alignment.py -q` | `holon:01`'s oracle `test_holons_module_standalone` **passes** |
| a heavy oracle in a worktree | `pytest tests/etkl/test_merge_resolution.py -q` (`tab:06`) | **8 passed in 13.56s** |

`holon:03` and `holon:01` are both met **on the same date, 2026-06-23** — so this edge exists
**only** because A4 is non-strict. Q3's demotion is now evidenced, not merely argued.

And one measured **negative**, which is the instrument working: `dec:14 → dec:11` is **refuted** —
with `vocab/shapes/risk-shapes.ttl`, `examples/transplant/transplant-risk.ttl` and
`tests/risk-leak.ttl` all removed, `pytest tests/test_governance.py -q` → **5 passed**. Expect many
such refutations (spec §9.2); this repo's oracles are largely self-contained per shape file.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **The runner is `./.venv/bin/python -m pytest`. NEVER `python3`** — it carries rdflib 7.1.4 and
   no pyrudof and reports false reds; M5c is the refusal that exists for it
   (`tests/test_arc_manifest.py:37`).
2. **Neurosymbolic gate (CLAUDE.md §8), stated per artifact in the artifact itself:**
   M12–M18 are **AXIOM / constraint, closed world** (SHACL over one hand-authored file);
   `arc-depends.rq`, `arc-ready.rq`, `arc-reach.rq` are **AXIOM / derivation, open world,
   evidence-positive**; M19 and `scripts/arc_depends.py` are **PROCEDURAL** and each must say in
   its own docstring *why it is irreducible* (a filesystem mutation and a subprocess exit code are
   not triples; a markdown rendering is not a derivation).
3. **No tuned constant, threshold or tolerance anywhere.** A timeout on a subprocess is a liveness
   bound, not a decision — if you need one, state that it can only turn a pass into an error, never
   a fail into a pass.
4. **Code never writes `tests/arc-manifest.ttl`** (`arc-manifest.ttl:16-18`). Edges are hand-authored
   in reviewed commits. `scripts/arc_depends.py` writes *only* `docs/superpowers/arc-dependency-landscape.md`.
5. **No HGA IRI enters any file this loop touches** (CLAUDE.md § Source ownership;
   `tests/test_source_ownership.py` enforces it).
6. **M11 is reserved for R106 and must not be reused** (spec §5; MEASURED: 0 hits in `src/ tests/
   scripts/ vocab/ baml_src/`).
7. **Every fixture trips EXACTLY ONE refusal**, asserted through the existing helpers
   `_refused_by_shacl` / `_refused_by_environment` (`tests/test_arc_manifest.py:333-357`).
8. **FALSIFICATION IS MANDATORY, per task** (CLAUDE.md § Plan authoring, rule 4): remove or invert
   the thing the new test pins, show it **failing**, restore, show green. A task report without a
   `## FALSIFICATION` block fails review.
9. **A plan-supplied test is a proposition.** If one cannot be made to pass, you have found a plan
   defect — say so in the task report and substitute the satisfiable form carrying the same force.
   Never weaken an assertion to make a broken contract go green (CLAUDE.md § Plan authoring, rule 5).
10. **Residue rows record the tally snapshot at the moment they are raised** (`| R113 (n/m closed) |`),
    counted from `docs/superpowers/residues.md` at that moment. Next free number is **R113**
    (measured: the index ends at R112).
11. Run the whole suite before every commit that touches `tests/arc-*`:
    `./.venv/bin/python -m pytest -q`. CI is **`pytest -q` and nothing else**
    (`.github/workflows/ci.yml:26-27`) — a gate that is not a pytest test does not run in CI.

---

## §File structure

| file | status | responsibility |
| --- | --- | --- |
| `tests/arc-shapes.ttl` | modify | M12–M18, closed world, beside M1–M9b |
| `tests/arc-manifest.ttl` | modify | the authored edges + reification rationale nodes |
| `tests/test_arc_manifest.py` | modify | one test per new SHACL refusal, using the existing helpers |
| `tests/arc-m12…m18-*-leak.ttl` | create (7) | one fixture per refusal, each tripping exactly one |
| `tests/test_arc_ablation.py` | create | M19: the two-sided ablation, PROCEDURAL |
| `tests/arc-m19-false-edge-leak.ttl` | create | an edge that satisfies A1–A4+A6 and that A5 refutes |
| `vocab/queries/arc-depends.rq` | create | the reader of record: graded transitive closure |
| `vocab/queries/arc-ready.rq` | create | unmet criteria whose **direct** dependencies are all met |
| `vocab/queries/arc-reach.rq` | create | how many criteria a residue's closure gates |
| `tests/test_arc_queries.py` | modify | fixture-computed answers + the three new shape tuples |
| `scripts/arc_depends.py` | create | renders the landscape by RUNNING the `.rq` files |
| `docs/superpowers/arc-dependency-landscape.md` | create (generated) | the gated cache |
| `tests/test_arc_landscape.py` | create | the regenerate-and-diff gate |
| `docs/superpowers/2026-08-2X-arc-edges-*.md` | create | Task 1's measurement; Task 7's close |

---

## Task 1: The worktree seam — measured, over every met criterion

Spec §4 carries a MEASURE box and the handoff names this the first task. §0's C5 measured **six**
probes; this task measures **all seventeen** met criteria and produces the table Task 3 designs
against.

**Files:**
- Create: `docs/superpowers/2026-08-22-worktree-oracle-seam.md` (evidence class, undated-dir rules
  do not apply: it is directly under `docs/superpowers/`, not under `specs/` or `plans/`, so no
  `Doc impact:` block is required — `tests/docgov_extract.py:91`, `_DATED`)
- Create (throwaway, **never committed**): a scratch script under the session scratchpad

**Interfaces:**
- Produces: for every met criterion, `(criterion, [oracle tests], runs-clean-in-worktree?,
  wall-clock)` and, for every criterion, `(artifacts removed → which oracle tests then fail)`.
  Task 3 consumes both; Task 4 consumes the second as its authoring input.

- [ ] **Step 1: Re-run spec §2's Q1–Q6 on the current tree and record the numbers.**
      The spec says so itself ("Q1 and Q4 move the moment any criterion flips to met"), and §0/C1
      shows the published figures were computed single-valued. Report: criteria, met, per-criterion
      test/artifact multiplicity, distinct artifact files, and the four envelope figures (strict,
      non-strict, +A3, +A3+A6) computed with **set disjointness**. If your numbers differ from
      §0/C1's (43 / 17 / 28 / 123 / 149 / 140 / 130), the tree moved — say so and use yours.

- [ ] **Step 2: For each of the 17 met criteria, run its oracle tests inside a bare worktree.**
      `git worktree add --detach <tmp> HEAD` from the repo, `cwd` inside it, interpreter
      `sys.executable` (absolute — the worktree has no `.venv`; measured). Record pass/fail and
      wall-clock per criterion.
      **This is the seam, and it is why the task exists:** `tests/test_docgov_extract.py:83-88`
      proves this repo already has a tool that *refuses* a second checkout, and `baml_client` is
      gitignored so it does not exist in a fresh worktree at all. Do not assume either way — the
      `tab:06` probe passed in 13.56s (§0/C5), which tells you nothing about the other sixteen.

- [ ] **Step 3: For each of the 17, remove ALL of that criterion's artifact files in a worktree and
      record which oracle tests across the whole met set then fail.** This is the ablation matrix,
      and it is the *positive control* for step 2: a criterion whose own oracle does not fail when
      its own artifact is deleted has an oracle that does not read its artifact, and that is a
      finding about the oracle (spec §9.3). Strip the `:line` suffix before removing
      (`_LINE_SUFFIX`, `tests/test_arc_manifest.py:63`).

- [ ] **Step 4: Write the measurement note.** The 17×17 fail-matrix, the per-criterion timings, the
      total wall-clock of a full sweep, and — under its own heading — **every oracle that could not
      run in a worktree**, with the error. State the sweep's cost bound plainly: Task 3's leg runs
      on every push and every reviewer's machine.

- [ ] **Step 5: Commit** the note only. Nothing under `tests/` changes in this task.

**FALSIFICATION for this task:** the instrument is the ablation itself, so falsify it by showing it
can report a negative: pick one criterion, delete an **unrelated** criterion's artifacts, and show
its oracle still passes (§0/C5's `dec:14 → dec:11` row is one such measurement; produce your own).
A matrix in which every cell fails is an instrument that is measuring the worktree, not the edge.

**Review gate:** if **any** oracle cannot run in a worktree, do not weaken A5 (spec §4's MEASURE box
says so). Record it, and note that every edge touching that criterion is a proposition in Task 4.

---

## Task 2: The vocabulary and the closed-world membrane — M12 to M18

**Files:**
- Modify: `tests/arc-shapes.ttl` (append; the file's header comment must be updated to say it now
  carries M1–M4, M6, M8, M9/M9b **and M12–M18**, and that M19 cannot be here)
- Modify: `tests/test_arc_manifest.py` (7 tests, one per refusal, via `_refused_by_shacl`)
- Create: `tests/arc-m12-dangling-target-leak.ttl`, `arc-m13-self-edge-leak.ttl`,
  `arc-m14-cycle-leak.ttl`, `arc-m15-met-depends-on-unmet-leak.ttl`,
  `arc-m16-ungrounded-assertion-leak.ttl`, `arc-m17-hidden-groundable-leak.ttl`,
  `arc-m18-rationale-cardinality-leak.ttl`

**Interfaces:**
- Produces, and every later task depends on these exact names:
  `prog:dependsOn` (Criterion → Criterion, asserted), `prog:proposedDependsOn` (Criterion →
  Criterion, proposition), `prog:dependencyRationale` (xsd:string, on an `rdf:Statement` node —
  §0/C3), and refusal messages that all begin `"M12: "` … `"M18: "` so the existing `_REFUSAL`
  regex (`tests/test_arc_manifest.py:330`) picks them up unchanged.

**The seven refusals, as contracts. Each is one `sh:sparql` on `prog:CriterionShape` unless stated:**

| | refuses | the invariant, stated so it can be checked |
| --- | --- | --- |
| M12 | a dependency target, either grade, that is not a declared `prog:Criterion` — including a blank-node or literal target | for every `?y` reachable by either predicate: `?y a prog:Criterion` and `isIRI(?y)` |
| M13 | `$this` depending on itself, either grade | — |
| M14 | any `$this` with `$this (prog:dependsOn\|prog:proposedDependsOn)+ $this` | a global refusal that no local rule sees (spec §5) |
| M15 | `$this prog:met true` depending, either grade, on a `prog:met false` target | the analogue of M8 |
| M16 | a `prog:dependsOn` failing **any** of A1, A2, A3, A4, A6 | see below |
| M17 | a `prog:proposedDependsOn` satisfying **all** of A1–A4 and A6 | the forcing function: propose only where you cannot ground |
| M18 | a `prog:proposedDependsOn` whose reification-node count ≠ 1, or a `prog:dependsOn` with any | exactly one rationale per proposition, none per assertion |

**A1–A6, in the set semantics §0/C1 requires** (X = `$this`, Y = the target):

- **A1** both `prog:met true`.
- **A2** both carry ≥ 1 `prog:oracleArtifact` and ≥ 1 `prog:oracleTest`.
- **A3** X and Y share **no** `prog:oracleTest` value.
- **A4** `metOn(Y) <= metOn(X)` — **non-strict**; §0/C5 is the measured reason.
- **A6** X and Y share **no** `prog:oracleArtifact` **file**: compare with the `:line` suffix
  stripped. `REPLACE(STR(?a), ":[0-9]+(-[0-9]+)?$", "")` is the SPARQL form; it must agree with
  `_LINE_SUFFIX` at `tests/test_arc_manifest.py:63`, which is `r":\d+$"` — **MEASURE which forms
  actually occur** in `prog:oracleArtifact` before choosing the regex (R109 is open precisely
  because this repo already has two divergent `<path>:<line>` parsers; do not add a third silently).

**Steps:**

- [ ] **Step 1: Write the seven fixtures first, and hand-verify each trips exactly one refusal.**
      Every fixture must otherwise be a *valid* manifest fragment — a criterion missing
      `prog:declaredOn` earns M1 as well and is then evidence about nothing (that discipline is
      already load-bearing at `tests/test_arc_manifest.py:333-343`). Copy real criterion blocks out
      of `tests/arc-manifest.ttl` so the fields are complete.
      Two fixtures that are easy to get wrong, with measured constructions:
      - **M14**: `holon:01 prog:dependsOn holon:03` **and** `holon:03 prog:dependsOn holon:01`.
        Both are met, both `metOn 2026-06-23` (so A4 non-strict holds **both ways**), their oracle
        tests are disjoint and their artifact files are disjoint — so M16 does not fire, M15 does
        not fire, and **only M14 can**. Verify that claim rather than trusting this sentence.
      - **M17**: a `prog:proposedDependsOn` on a pair that satisfies A1–A4+A6 — `holon:03 → holon:01`
        is exactly such a pair (§0/C5).
- [ ] **Step 2: Run the fixtures against the CURRENT membrane and show them all admitted.**
      `Conforms: True` for all seven is the RED state; record it in the task report. This is what
      makes step 4's green mean something.
- [ ] **Step 3: Declare the three terms and write M12–M18 in `tests/arc-shapes.ttl`.**
      Keep the file's existing conventions: every `sh:message` opens with its refusal number; each
      `sh:sparql` names `sh:prefixes prog:prefixes`; comments state *why* a constraint exists, not
      what it does. Add `rdf:` to the prefix block for M18.
- [ ] **Step 4: Add the seven tests** to `tests/test_arc_manifest.py` beside the M1–M9b block, each
      one line of `_refused_by_shacl(fixture, "M1n")`, with a docstring stating the invariant.
      Run: `./.venv/bin/python -m pytest tests/test_arc_manifest.py -q` → all pass.
- [ ] **Step 5: MEASURE the cockpit seam before you commit.** `scripts/cockpit.py` reads the
      manifest with a line regex anchored at column 0 (`cockpit.py:188`) under a contract that
      forbids rdflib. Nothing in this task edits `tests/arc-manifest.ttl` yet — but Task 4 will add
      indented `prog:dependsOn` lines and **top-level blank-node `[] a rdf:Statement` blocks**, and
      the reader's state machine has never seen either. Add a `[] a rdf:Statement …` block and a
      `prog:dependsOn` line to a **scratch copy**, point the reader at it, and record whether the
      per-rung counts change. Run `./.venv/bin/python -m pytest tests/test_cockpit.py -q`.
      If the reader miscounts, that is a finding to fix **here**, before 43 criteria are edited.
- [ ] **Step 6: Full suite, then commit.** `./.venv/bin/python -m pytest -q`.

**FALSIFICATION:** for each of M12–M18, delete that one `sh:sparql` (or invert its filter) and show
its test **failing**; restore; show the suite green. Seven blocks, and M14's is the one that matters
most — a cycle refusal that passes with the constraint deleted has pinned nothing.

---

## Task 3: M19 — the two-sided ablation, and the direction it grounds

**Files:**
- Create: `tests/test_arc_ablation.py`
- Create: `tests/arc-m19-false-edge-leak.ttl`
- Modify: `tests/test_arc_manifest.py` (module docstring only — one line pointing at the new module,
  so the M-numbering stays discoverable from one place)

**Why a separate module, decided here:** the environment leg in `tests/test_arc_manifest.py` runs in
under a second; this one creates worktrees and runs pytest subprocesses. Mixing them changes the
membrane module's cost profile for every developer who runs it. The split is by cost, not by
concern, and the docstring must say exactly that.

**Interfaces:**
- Consumes: Task 1's fail-matrix and timings; Task 2's `prog:dependsOn`.
- Produces: `ablation_refusals(graph) -> list[str]`, each string opening `"M19: "`, empty == admitted.
  Mirrors `environment_refusals` (`tests/test_arc_manifest.py:284`) deliberately, so the fixture
  helper pattern transfers.

**The contract:**

1. Read every `prog:dependsOn (X, Y)` from the graph handed in.
2. Group by **endpoint criterion** (§0/C2), not by file: one worktree per criterion whose artifacts
   are removed.
3. In each worktree: `git worktree add --detach <tmp_path> HEAD` **from the repo**, delete all of
   that criterion's `prog:oracleArtifact` files (`:line` stripped), then, with `cwd` in the worktree
   and `sys.executable` as the interpreter:
   - **arm 1** — for each X with `X dependsOn C`: run X's oracle tests; **at least one must fail**.
     A pass means X does not consume C and the edge is refuted.
   - **arm 2** — for each Y with `C dependsOn Y`: run Y's oracle tests; **all must pass**. A fail
     means the coupling is symmetric and the edge is refuted rather than demoted (spec §4).
4. Always `git worktree remove --force` in a `finally`. The real tree is never mutated — that is the
   safety property, and a crashed subprocess must not be able to break the repo.
5. A **stated limitation the docstring must carry:** the worktree is checked out at `HEAD`, so M19
   validates the **committed** tree. Uncommitted edits to an artifact are invisible to it.

**Steps:**

- [ ] **Step 1: Write `tests/arc-m19-false-edge-leak.ttl` — an edge that the membrane admits and the
      ablation refutes.** MEASURED 2026-08-22 and ready to use: `prog:criterion:dec:11
      prog:dependsOn prog:criterion:dec:03`. It satisfies A1 (both met), A2, A3 (`test_risk.py` vs
      `test_timeline_shacl.py`, disjoint), A4 (`2026-06-26 ≥ 2026-06-18`) and A6 (risk artifacts vs
      dec-shapes/heart-timeline artifacts, disjoint) — **and arm 1 passes**: with `dec:03`'s three
      artifacts removed, `pytest tests/test_risk.py -q` → `5 passed`. So Task 2's membrane admits it
      and only M19 can refuse it, which is precisely the `_refused_by_environment` shape.
- [ ] **Step 2: Show the fixture is SHACL-clean.** `validate_manifest(fixture)` → `Conforms: True`.
      If it is not, the membrane and the ablation are refusing the same thing and one of them is
      redundant — report that as a finding rather than editing the fixture until it goes quiet.
- [ ] **Step 3: Write the runner to the contract above.** Gate classification in the docstring:
      **PROCEDURAL, irreducible** — it mutates a filesystem and reads a subprocess exit code, and
      neither is a triple. State that it derives nothing into either manifest.
- [ ] **Step 4: The test that pins refutation.** `ablation_refusals` over the fixture returns exactly
      one refusal, opening `"M19:"` and naming both ends and the arm that failed.
- [ ] **Step 5: The live leg.** `ablation_refusals` over `tests/arc-manifest.ttl` is **empty**. It is
      trivially green today (no edges) and becomes the loop's real gate in Task 4 — say so in the
      test's docstring, so a later reader does not mistake a vacuous pass for evidence.
- [ ] **Step 6: Record the wall-clock** of the live leg with Task 4's edges in place, in the task
      report. If it exceeds Task 1's projection, say by how much.
- [ ] **Step 7: Full suite, commit.**

**FALSIFICATION:** invert arm 1's expectation (accept a pass as evidence of dependence) and show
`test_arc_ablation.py`'s fixture test **failing**; restore. Then do the same for arm 2. Two
inversions, because an ablation with one working arm grounds adjacency and not direction — which is
Q2's entire finding.

---

## Task 4: Author the edges — all 43 criteria, and answer the acyclicity question

This is the loop's substance. Spec §10.1: **a full sweep**, because a partial dependency graph
answers the maintainer's question with a partial landscape.

**Files:**
- Modify: `tests/arc-manifest.ttl`
- Create: `docs/superpowers/2026-08-22-arc-edges-authored.md` — the reading, the refutations, and the
  acyclicity answer

**Steps:**

- [ ] **Step 1: Read all 43 criteria and write down, in the evidence file, every dependency you
      believe exists** — before consulting the membrane. Reading first, grading second: an author who
      checks A1–A6 while reading will only ever "find" edges the membrane already permits, and the
      proposition half of the graph is then empty for the wrong reason.
- [ ] **Step 2: Grade each edge by the membrane's rules, not by taste.** Both ends met with distinct
      oracle tests and distinct artifact files ⇒ **you must assert it** (M17 leaves no choice).
      Everything else ⇒ `prog:proposedDependsOn` + exactly one `rdf:Statement` rationale node
      (§0/C3) saying *what you read* and *which precondition it fails*.
- [ ] **Step 3: Run the membrane.** `./.venv/bin/python -m pytest tests/test_arc_manifest.py -q`.
      Fix authoring errors; **never relax a refusal to admit an edge**.
- [ ] **Step 4: Answer M14 — and report the answer whichever way it comes out** (spec §9.1). If a
      cycle exists, resolve it by splitting a criterion that is doing two jobs, or by deleting the
      weaker direction. **Never by relaxing M14.** An unresolved cycle ships as a residue row with
      the cycle printed in it.
- [ ] **Step 5: Run M19 over the real manifest and expect refutations.** Each refuted edge is
      **deleted** — not demoted (§0/C4) — and each deletion is recorded in the evidence file with the
      arm that failed and the command that showed it. A loop where A5 refutes nothing should be
      suspected of having authored only safe edges (spec §9.2).
- [ ] **Step 6: Re-run the membrane and the cockpit.** `./.venv/bin/python -m pytest -q` plus
      `./.venv/bin/python scripts/cockpit.py --refresh --no-color` — the strip must still render and
      its per-rung counts must be unchanged, because no `prog:met` was touched (spec §8).
- [ ] **Step 7: Commit** the manifest and the evidence file together.

**FALSIFICATION:** the graph is data, not code, so falsify the *authoring*: take one asserted edge,
reverse it in a scratch copy, and show M19 refusing the reversal (arm 2 fails, or arm 1 passes).
An edge whose reversal is also admitted is an edge whose direction nothing grounded.

**Review gate:** the reviewer counts asserted vs proposed edges against Task 1's re-run envelope. An
asserted count of zero is a legitimate measured result **only** if §0/C5's `holon:03 → holon:01` was
itself refuted on this tree — otherwise something is wrong with the runner, not with the arc.

---

## Task 5: The three derivations

**Files:**
- Create: `vocab/queries/arc-depends.rq`, `arc-ready.rq`, `arc-reach.rq`
- Modify: `tests/test_arc_queries.py`

**Interfaces (the `SHAPES` contract at `tests/test_arc_queries.py:47-52` — a rewrite that renames or
reorders a projected variable is a breaking change and that tuple is where it is caught):**

- `arc-depends.rq` → `("dependency", "grade")`, `?criterion` **supplied by the caller** — the
  `arc-orphan.rq` / `adoption-candidate.rq` idiom. `grade` is `"asserted"` where the dependency is
  reachable by `prog:dependsOn+` and `"proposed"` otherwise, so a reader sees where the chain stops
  being grounded. Both closures are computed **in the query**; nothing downstream recomputes them.
- `arc-ready.rq` → `("rungKey", "criterion", "statement")` — deliberately the same tuple as
  `arc-unblocked.rq`, and it is **not** that query: this one knows only about criteria, that one
  only about register rows.
- `arc-reach.rq` → `("residue", "gated")`, `?residue` supplied by the caller (the register is a
  markdown file that is not in the graph — `arc-orphan.rq`'s header states the seam and M7 is why).

**Two constraints on the SPARQL, both from CLAUDE.md §8:**

- `arc-ready.rq`'s negation is over **one criterion's own outgoing edges** — holon-scoped, exactly
  as `arc-unblocked.rq:60-66` argues. **Direct dependencies only, never the transitive cone**
  (spec §6): closing over a chain is a larger closure claim than this repo has licensed.
- Nothing here derives `met`. Met is read, never inferred from an absence.

**Steps:**

- [ ] **Step 1: Extend the fixture** at `tests/test_arc_queries.py:70+` with dependency edges of both
      grades, including one two-hop chain where the second hop is proposed (so `grade` has something
      to distinguish) and one unmet criterion depending on an unmet criterion (so `arc-ready.rq` has
      a negative). Keep the file's rule: **the fixture is deliberately not membrane-valid**, and
      every expected answer is computed **by hand from the fixture text**, never by running the query
      and recording what came out.
- [ ] **Step 2: Write the three queries**, each with the header this directory uses: the gate
      classification, the seam, the caller-binding contract where there is one, and — for
      `arc-depends.rq` — why the two closures are reported separately rather than merged.
- [ ] **Step 3: Add the three shape tuples to `SHAPES`** and the per-query row tests.
- [ ] **Step 4: The live arm** (spec §10.4): run `arc-depends.rq` and `arc-ready.rq` over
      `tests/arc-manifest.ttl` and print, in the task report, **the answer to "what must land before
      the next unmet criterion"**. Do not pin a live row count in a test — the manifest changes every
      loop, and `tests/test_arc_queries.py:13-17` states that rule.
- [ ] **Step 5: Full suite, commit.**

**FALSIFICATION:** for each query, break the thing it pins — drop the `grade` distinction so both
closures return the same set; change `arc-ready.rq` to transitive; unbind `arc-reach.rq`'s subject —
and show the corresponding test **failing** each time. `arc-depends.rq`'s is the pointed one: a
grade test that passes when every edge is labelled `"asserted"` has pinned nothing.

---

## Task 6: The generated landscape and its gate

**Files:**
- Create: `scripts/arc_depends.py`, `tests/test_arc_landscape.py`
- Create (generated, committed): `docs/superpowers/arc-dependency-landscape.md`

**The two invariants, and the second is what earns the file its right to exist:**

1. **One reader of record.** `scripts/arc_depends.py` **runs the `.rq` files** from
   `vocab/queries/`; it must not reimplement the closure in Python. A second reader of a derived
   fact is the M9/M9b defect-generator the spec names in §6.
2. **Regenerate-and-diff.** `tests/test_arc_landscape.py` regenerates into `tmp_path` and asserts
   **byte identity** with the tracked file. MEASURED: CI runs `pytest -q` and nothing else
   (`.github/workflows/ci.yml:26-27`), so the gate must be a pytest test — a Makefile target or a
   new CI step would not run. **Shipping the file without this gate is forbidden by `CLAUDE.md`
   § Documentation governance**, which grants the exception to a *gated* cache only.

**Steps:**

- [ ] **Step 1: Write the gate test first, against a landscape file that does not exist yet.** It
      must fail with "file missing", not error. That failure is the RED state; record it.
- [ ] **Step 2: Write the generator.** Docstring states: **PROCEDURAL, and why** (rendering markdown
      is not a derivation; the derivation is in the `.rq` files it runs). Deterministic output —
      sorted rows, no timestamp, no run-dependent content, or the gate can never be green twice.
- [ ] **Step 3: Generate, commit the output, show the gate green.**
- [ ] **Step 4: Show the gate BITES.** Hand-edit one character of the tracked landscape; the test
      must fail. Restore. This is the gate's whole value and is also its falsification block.
- [ ] **Step 5: Confirm governance is satisfied, not evaded.** `./.venv/bin/python -m pytest
      tests/test_doc_governance.py -q` must pass, and the task report must state that the file
      classifies as `evidence` by path prefix (`tests/docgov_extract.py:36-51`), carries no
      frontmatter obligation, and was **not** routed around governance via the `.databook.md` or
      `.txt` exemptions the spec §6 names and declines.
- [ ] **Step 6: Full suite, commit.**

---

## Task 7: Close the loop

**Files:**
- Modify: `docs/superpowers/residues.md`, `residues-open.md`
- Create: `docs/superpowers/2026-08-2X-arc-edges-close-handoff.md`

- [ ] **Step 1: Raise the residue rows this loop knowingly leaves open**, tally snapshot in each
      (next free number **R113**):
      - ablation is grounded to **file** granularity; line-granularity ablation is the upgrade
        (spec §4's stated limitation, §8's last-but-one bullet)
      - any oracle Task 1 found that cannot run in a worktree (spec §9.3)
      - an unresolved cycle, if Task 4 found one, **with the cycle printed in the row**
      - the **80% orphan question stays open** — spec §7 corrects the origin handoff's subsumption
        claim, and a criterion→criterion edge gives a residue nowhere new to attach
- [ ] **Step 2: Record §0's four corrections where a later session will find them.** They are
      corrections to a committed spec, so they belong in the loop's evidence file and in the handoff,
      not as edits to the spec (evidence is immutable after loop close; the two exceptions are
      `residues.md` and a gated cache, and a spec is neither).
- [ ] **Step 3: Write the handoff** per `managing-context-budget` § Handoff: goal, where the
      primaries are, what was decided and **where each decision is recorded**, an *Unverified or
      assumed* heading even if empty, and one next concrete action.
- [ ] **Step 4: State the definition-of-done audit explicitly**, item by item against spec §10.1–§10.6,
      with the acyclicity answer (§10.6) stated as a **measurement**, whichever way it came out.
- [ ] **Step 5: Full suite green, then merge per `superpowers:finishing-a-development-branch`.**

---

## Self-review — spec coverage

| spec | covered by |
| --- | --- |
| §2 Q1–Q6 re-run | Task 1 step 1 (+ §0/C1 corrects Q5/Q6) |
| §3 two predicates + rationale | Task 2 (+ §0/C3 gives the rationale a subject) |
| §4 A1–A4, A6 preconditions | Task 2 M16 |
| §4 A5 two-sided ablation + MEASURE box | Task 1, Task 3 (+ §0/C2 regroups it) |
| §5 M12–M18 | Task 2 |
| §5 M19 | Task 3 |
| §6 arc-depends / arc-ready / arc-reach | Task 5 |
| §6 generated landscape + gate; cockpit untouched | Task 6 |
| §7 the 80% question stays open | Task 7 step 1 |
| §8 what this loop does not do | Global Constraints 4, 5; Task 4 step 6 |
| §9 falsifying oracle + per-task falsification | every task's FALSIFICATION block; Task 3's is A5's |
| §10.1–§10.6 definition of done | Task 4 (1), Task 2 (2), Task 3 (3), Task 5 (4), Task 6 (5), Task 7 (6) |

**Known gaps, stated rather than hidden:** `arc-reach.rq` is the spec's own cuttable item (§6) and is
in Task 5 — cut it there if the loop runs long, and say so in the handoff. The plan supplies **no**
verbatim test bodies; it supplies fixtures, contracts and expected refusals, because CLAUDE.md
§ Plan authoring rule 1 makes the body the implementer's to write and defects 2 and 5 of that
section were both plan-authored tests.
