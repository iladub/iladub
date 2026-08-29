# `R135` loop evidence — the query names a declared term

**Plan:** `docs/superpowers/plans/2026-08-28-the-query-names-a-declared-term.md`
**Spec:** `docs/superpowers/specs/2026-08-26-the-query-names-a-declared-term-design.md`
**Branch:** `the-query-names-a-declared-term` · **Base:** `main` @ `63892ae`

Every command below was run with `./.venv/bin/pytest` / `./.venv/bin/python` (G1 — system
`python3` is not the runner and produces a false red, spec §2.3 / M3).

---

## Task 1 — the extractor and its own oracles

### Seam 3 (spec §10 seam 3): where a fixture may live, MEASURED before the paths were chosen

```
$ ls vocab/queries/*.rq | wc -l
      46
$ ls tests/*.rq
(eval):1: no matches found: tests/*.rq
$ grep -rn "glob(.*\.rq" --include='*.py' .   # (.venv excluded)
tests/test_arc_queries.py:616:    found = sorted(p.name for p in QUERIES.glob("arc-*.rq"))
tests/etkl/test_transform_gate.py:27,52,72,94:  glob.glob(os.path.join(QUERIES, "*.rq"))
```

`test_transform_gate.py`'s `QUERIES` is `vocab/queries` (`:10`). So nothing in the tree globs
`tests/*.rq`, and that namespace is empty — the plan §0.2 claim reproduces, and both fixtures
go in `tests/`.

### Seam 1 (Task 1): the walk measured against method B over all 46 files, BEFORE any test

Prototype run (session scratchpad, not shipped — it is measurement, not code):

```
files=46 extract_time=0.93s disagreements=0 distinct_owned=171
  https://w3id.org/iladub#               named=  6
  https://w3id.org/iladub/dec#           named= 14
  https://w3id.org/iladub/docgov#        named= 12
  https://w3id.org/iladub/etkl#          named= 12
  https://w3id.org/iladub/progress#      named=  9
  https://w3id.org/iladub/risk#          named=  2
  https://w3id.org/iladub/tab#           named=116
triples: 371 namesTerm: 325
```

M7's `171 / 0 disagreements` and M8's per-namespace table reproduce at `b380d9d`.

### Seam 3 of Task 1: the shipped `evidence_graph()` wall clock

```
$ ./.venv/bin/python -c "…from tests.query_terms import evidence_graph…"
evidence_graph() 0.77s over 46 files: 371 triples, 46 focus nodes, 325 namesTerm, 171 distinct owned
declaring files: ['dec.ttl', 'etkl-holons.ttl', 'etkl.ttl', 'iladub.ttl', 'risk.ttl', 'tab-datagrid.ttl', 'tab.ttl']
```

**0.77s — identical to the plan's prototype figure, and the seam is answered: this is a
seconds-scale integrity test, not a 4m12s one (spec §10 seam 1).** The 325 `namesTerm` over 46
focus nodes is the number Task 1 predicted (the plan's prototype scoped inside the extractor and
emitted 317; this one scopes in the shape, as designed). The seven declaring files are exactly
the non-align set of §0.

### RED

```
$ ./.venv/bin/pytest tests/test_query_terms.py -q
tests/test_query_terms.py:8: in <module>
    from tests.query_terms import (
E   ModuleNotFoundError: No module named 'tests.query_terms'
ERROR tests/test_query_terms.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.07s
```

### GREEN

```
$ ./.venv/bin/pytest tests/test_query_terms.py -q --durations=5
....                                                                     [100%]
0.91s call     tests/test_query_terms.py::test_both_extractors_agree_on_every_authored_query
0.80s call     tests/test_query_terms.py::test_every_authored_query_parses
0.03s call     tests/test_query_terms.py::test_a_term_nested_in_bind_exists_is_reported
4 passed in 2.07s
```

## FALSIFICATION — Task 1 (G6)

Two inversions, both on the traversal, because F2 showed the naive form has two faces.

**Inversion 1 — restrict the walk to `CompValue.items()` (+ sequences), no `__dict__`**
(spec §2.4's form):

```
$ ./.venv/bin/pytest tests/test_query_terms.py -q
FAILED tests/test_query_terms.py::test_a_term_nested_in_bind_exists_is_reported
FAILED tests/test_query_terms.py::test_both_extractors_agree_on_every_authored_query
2 failed, 2 passed in 1.99s
```

Both named tests fail, as the plan requires. 12 files disagree, 161 distinct owned.

**Inversion 2 — `__dict__` walk restored, but the dict branch `return`s early** (F2's form):

```
$ ./.venv/bin/pytest tests/test_query_terms.py -q
FAILED tests/test_query_terms.py::test_a_term_nested_in_bind_exists_is_reported
FAILED tests/test_query_terms.py::test_both_extractors_agree_on_every_authored_query
2 failed, 2 passed in 2.12s

$ ./.venv/bin/python -c "…named_terms_by_algebra vs named_terms_by_text…"
   DISAGREE continuation-of.rq ['/tab#boundaryAgreesWith', '/tab#leafCellText', '/tab#originAgreesWith']
   DISAGREE header-row-role.rq ['/tab#sharesAlignmentOriginWith']
   DISAGREE looks-transposed.rq ['/tab#Text', '/tab#datatypeAbstains']
   DISAGREE membrane-health.rq ['#PromotionDecision', '#reviews']
   DISAGREE transpose-coherent.rq ['/tab#datatypeAbstains']
   DISAGREE unit-marker-column.rq ['/tab#Blank', '/tab#Quantity', '/tab#datatypeAbstains']
```

**The six files, term for term, are exactly those quoted in plan §0.1 F2** — the falsification
reproduces the measurement it was written from.

**Restored; green:**

```
$ ./.venv/bin/pytest tests/test_query_terms.py -q
....                                                                     [100%]
4 passed in 2.08s
```

---

## Task 2 — the membrane, disposed against a two-term fixture

The 46-file corpus is deliberately untouched here (spec §10 seam 5). Task 3 wires it.

### Seam 3, re-measured before the fixture path was chosen (§0.2 requires confirming the glob)

```
$ ls vocab/queries/*.rq | wc -l
      46
$ ls tests/*.rq
tests/query-nested-bind-exists.rq          # Task 1's fixture; nothing else
$ grep -rn "glob(.*\.rq\|\*\.rq" --include='*.py' tests/ src/ scripts/
tests/query_terms.py:48:    return sorted(QUERY_DIR.glob("*.rq"))          # the population
tests/test_arc_queries.py:616:    found = sorted(p.name for p in QUERIES.glob("arc-*.rq"))
tests/etkl/test_transform_gate.py:27,52,72,94: glob.glob(os.path.join(QUERIES, "*.rq"))
```

No glob reaches `tests/*.rq`. `tests/query-undeclared-term-leak.rq` is outside the population,
and `test_the_leak_fixture_is_not_in_the_population` pins it there.

### Step 3 — red, for the right reason

```
$ ./.venv/bin/pytest tests/test_query_declarations.py -q
E  FileNotFoundError: [Errno 2] No such file or directory:
   '…/vocab/shapes/query-declaration-shapes.ttl'
FAILED tests/test_query_declarations.py::test_a_declared_and_an_undeclared_term_are_told_apart
FAILED tests/test_query_declarations.py::test_a_query_naming_an_undeclared_term_is_refused
2 failed, 1 passed in 0.95s
```

### Step 5 — green

```
$ ./.venv/bin/pytest tests/test_query_declarations.py tests/test_source_ownership.py -q
......                                                                   [100%]
6 passed in 1.25s
```

`test_source_ownership.py` is run here because the new shape file joins its population
(`tests/test_source_ownership.py:62` globs `vocab/shapes/*.ttl`) the moment it lands (G5).

The refusal, in full — the message names **both** the query and the term:

```
$ ./.venv/bin/python -c "…_validate(extract_named_terms(LEAK_FIXTURE) + declaring_graph())…"
conforms = False
Constraint Violation in SPARQLConstraintComponent:
	Source Shape: etkl:QueryArtifactShape
	Focus Node: <urn:iladub:query:tests/query-undeclared-term-leak.rq>
	Message: urn:iladub:query:tests/query-undeclared-term-leak.rq names
	         https://w3id.org/iladub/etkl#NoSuchTermAnywhere, which no owned ontology declares
```

One violation, not two: the fixture also names `etkl:SemanticDataContract`, which is declared.

### A plan-supplied expectation that did not hold, and what replaced it (G6)

Plan Step 6 inversion 2 asserts that deleting the `FILTER NOT EXISTS` makes **both** tests fail.
As the plan wrote O5, it does not: with the filter gone the shape refuses *every* named term, so
`not conforms`, `"…leak.rq" in report` and `"etkl#NoSuchTermAnywhere" in report` all still hold
and O5 goes **green against a membrane that refuses everything**. This is defect-5's shape — an
assertion too weak to fail — surviving into a second loop.

The fixture was already built to answer it (one declared term, one undeclared), so O5 gained the
assertion that was missing rather than losing the one that was wrong:

```python
assert "etkl#SemanticDataContract" not in report
```

Selectivity is the claim O5 was making implicitly; it is now asserted, and inversion 2 bites it
at `tests/test_query_declarations.py:96`. **Strengthened, not weakened** (G6).

### Step 6 — FALSIFICATION, three inversions

**Inversion 1 — `inference="none"` → `"rdfs"`** (the standing pin on §0.1 F1):

```
$ sed -i '' 's/inference="none",/inference="rdfs",/' tests/test_query_declarations.py
$ grep -n 'inference="rdfs",$' tests/test_query_declarations.py
63:        inference="rdfs",
$ ./.venv/bin/pytest tests/test_query_declarations.py -q
FAILED tests/test_query_declarations.py::test_a_declared_and_an_undeclared_term_are_told_apart
FAILED tests/test_query_declarations.py::test_a_query_naming_an_undeclared_term_is_refused
2 failed, 1 passed in 0.79s
```

Both fail — F1 is **pinned**, not merely commented. Restored: `3 passed in 0.67s`.

**Inversion 2 — the `FILTER NOT EXISTS` line deleted from the shape:**

```
$ sed -i '' '/FILTER NOT EXISTS { ?term ?p ?o }/d' vocab/shapes/query-declaration-shapes.ttl
$ ./.venv/bin/pytest tests/test_query_declarations.py -q
tests/test_query_declarations.py:96: AssertionError
FAILED tests/test_query_declarations.py::test_a_declared_and_an_undeclared_term_are_told_apart
FAILED tests/test_query_declarations.py::test_a_query_naming_an_undeclared_term_is_refused
2 failed, 1 passed in 0.65s
```

Both fail, and O5 fails **at line 96** — the assertion added above. Restored: `3 passed in 0.70s`.

**Inversion 3 — `progress#` added to the `STRSTARTS` disjunction, leak fixture pointed at
`prog:blockedBy`** (a term `vocab/queries/arc-frontier.rq:43` really names):

```
conforms = False
Message: urn:iladub:query:tests/query-undeclared-term-leak.rq names
         https://w3id.org/iladub/progress#blockedBy, which no owned ontology declares
```

and then, with the **scope reverted** while the fixture still names `prog:blockedBy`:

```
conforms = True
```

The same term, the same extractor, the same evidence graph — refused with `progress#` in the
disjunction, admitted without it. **The `prog:`/`docgov:` exemption is a choice this shape makes,
in this file, with a date on it — not an accident of what the extractor happened to emit** (spec
§8 item 7). Both reverted.

**Restored; green across the four modules Task 2 can touch:**

```
$ ./.venv/bin/pytest tests/test_query_declarations.py tests/test_query_terms.py \
                     tests/test_source_ownership.py tests/test_vocab_shapes.py -q
.................                                                        [100%]
17 passed in 3.21s
```

---

## Task 3 — wire the corpus: O1 red, the repair, green

### Step 1 — RED. This is O1 (spec §7), and it is the sentence that makes the loop vertical

The two corpus tests were added to `tests/test_query_declarations.py` against the tree exactly as
it stood at `b56ceb8`. Verbatim, one violation:

```
$ ./.venv/bin/pytest tests/test_query_declarations.py -q --durations=5
E       AssertionError: Validation Report
E         Conforms: False
E         Results (1):
E         Constraint Violation in SPARQLConstraintComponent:
E         	Severity: sh:Violation
E         	Source Shape: etkl:QueryArtifactShape
E         	Focus Node: <urn:iladub:query:vocab/queries/escalation-furnish.rq>
E         	Message: urn:iladub:query:vocab/queries/escalation-furnish.rq names
E         	         https://w3id.org/iladub/risk#order, which no owned ontology declares
1.83s call tests/test_query_declarations.py::test_every_authored_query_names_only_declared_terms
1 failed, 4 passed in 3.39s
```

Exactly the one violation the spec (§4.6) and plan §0 predicted, on the file they predicted, for
the term they predicted — found by the shipped instrument rather than by a prototype. **O4 was
already green at this step** (46 focus nodes), which is the point of Step 4's second inversion
below: O4 cannot tell a working membrane from an idle one.

### A plan number that did not hold — 371 evidence triples, not 325 (G6, reported honestly)

Task 3's MEASURED block predicts the shipped `evidence_graph()` emits **325** triples where the
prototype emitted 317. It emits **371**. Measured, and fully reconciled — there is no defect:

```
$ ./.venv/bin/python -c "…evidence_graph()…"
rdf:type triples : 46
namesTerm triples: 325
total            : 371 = 46 + 325
out-of-scope (prog:/docgov:) namesTerm triples: 54
in-scope namesTerm triples: 271
```

The plan reached 325 as `317 + 8`, and 325 *is* the true `namesTerm` count — but by coincidence,
not by that arithmetic. The real decomposition:

* prototype, scoped **inside** the extractor: `46 type + 271 in-scope namesTerm = 317` ✓
* shipped, scoped **in the shape** (spec §4.3 — the extractor decides nothing): the same 317 plus
  the **54** `prog:`/`docgov:` `namesTerm` triples the extractor must now emit and the shape must
  now exclude = **371**.

So the 8 the plan added was a distinct-term delta (9 `prog:` + 12 `docgov:` distinct terms, plan
§0) used where a per-occurrence delta was needed. The shipped extractor is correct on the number
the plan actually derived; the total was mislabelled. Recorded because a reviewer checking `325`
against the tree will find `371` and should not have to re-derive why.

### A wording drift between plan and shipped shape (not a defect)

Task 3's MEASURED block quotes the message as *"which no **non-align** owned ontology declares"*.
The shape shipped in Task 2 says *"which no owned ontology declares"* — which is what plan §0.1 F1
itself measured. The prototype's older wording survived into Task 3's block. No test asserts the
sentence, and the exclusion of align modules is documented where it is enforced
(`tests/query_terms.py::declaring_files`), so the shipped wording was kept.

### Step 2 — the repair: `risk:order` declared in `vocab/ontology/risk.ttl`

Placed in a section of its own, immediately beside its four uses (`risk.ttl:62,64,66,68`) rather
than in `Properties — context & sensitivity`; plan Step 2 permits either. `rdfs:domain
risk:Severity` is measured from those four uses, all `a risk:Severity`, not guessed;
`rdfs:range xsd:integer` mirrors `dec:order` (`vocab/ontology/dec.ttl:136-138`). The
`rdfs:comment` is written fresh — `dec:`'s sentence names milestones — and says the thing this
ontology needs said: an order is a **position, never a magnitude**, so severities may be ordered
but never summed. `git diff --stat` = 8 insertions, no deletions.

### Step 3 — green

```
$ ./.venv/bin/pytest tests/test_query_declarations.py tests/test_risk.py \
                     tests/test_vocab_shapes.py tests/test_source_ownership.py -q --durations=5
....................                                                     [100%]
1.78s call tests/test_query_declarations.py::test_every_authored_query_names_only_declared_terms
0.84s call tests/test_query_declarations.py::test_the_membrane_binds_one_focus_node_per_query_file
20 passed in 3.87s
```

### Step 4 — FALSIFICATION (G6), two inversions

**Inversion 1 — the `risk:order` declaration removed again.** O1 returns, with its message:

```
$ ./.venv/bin/pytest tests/test_query_declarations.py -q
E         	Focus Node: <urn:iladub:query:vocab/queries/escalation-furnish.rq>
E         	Message: urn:iladub:query:vocab/queries/escalation-furnish.rq names
E         	         https://w3id.org/iladub/risk#order, which no owned ontology declares
1 failed, 4 passed in 3.35s
```

Restored (`git diff --stat` back to 8 insertions): `5 passed in 3.29s`. **The repair is what makes
O1 green** — not the extractor's scope, not the shape's namespace filter.

**Inversion 2 — `sh:targetClass etkl:QueryArtifact` deleted from the shape.** The plan predicts O1
goes green with nothing checked while O4 still passes, and asks for the result reported honestly.
It does, and the honest result is **stronger than the plan claimed**:

```
$ ./.venv/bin/pytest tests/test_query_declarations.py -q --no-header -rA
PASSED  test_every_authored_query_names_only_declared_terms      <- O1, GREEN ON AN IDLE MEMBRANE
PASSED  test_the_membrane_binds_one_focus_node_per_query_file    <- O4, counts data, not targets
PASSED  test_the_leak_fixture_is_not_in_the_population
FAILED  test_a_declared_and_an_undeclared_term_are_told_apart    <- seam-5 fixture
FAILED  test_a_query_naming_an_undeclared_term_is_refused        <- O5
2 failed, 3 passed in 2.54s
```

Restored (empty `git diff`): `5 passed in 2.99s`.

**What this measures.** With no target the shape binds no focus node, validates nothing, and
conforms — V1's hazard exactly, and **O1 and O4 together cannot see it**. O4 is not a non-idleness
oracle: it counts `etkl:QueryArtifact` subjects in the *data* graph, which the extractor put there
and no shape edit can remove. The plan named O5 as the one thing that bites; **two** tests bite —
O5 *and* the two-term seam-5 fixture — because each carries a negative that a silent membrane
cannot satisfy. This is the concrete argument for CLAUDE.md's negative-test rule: the corpus test
that looks like the instrument is the one that cannot police itself.

### Step 5 — the full suite (G1), foreground

```
$ ./.venv/bin/pytest -q
1344 passed, 7 skipped, 1 xfailed, 10 warnings in 2480.68s (0:41:20)
[exited with code 0]
```

Nothing else in the tree moved: the `risk:order` declaration is additive (8 insertions, no
deletions), and the two new tests are the only additions to the count. Plan Step 5 says do not
background this run; the 41-minute wall clock exceeded the 600s tool cap and the harness detached
it, so it was **blocked on to completion in-turn** rather than left to run unattended — the
summary line above is from the finished process, not a partial read.

---

## Task 4 — re-author `holon:05 → holon:01` on a measured refusal

### The seams, measured before the manifest was touched

**Seam 1 — A6 (shared artifact file) stays satisfied, and no `prog:oracleArtifact` was added.**
A6 (`tests/arc-shapes.ttl`, the `sh:sparql` carrying the `M16: A6` message) compares the two ends'
`prog:oracleArtifact` values with any `:line` suffix stripped. `holon:05` names
`vocab/queries/membrane-health.rq`, `holon:01` names `vocab/ontology/etkl-holons.ttl` — disjoint,
and this task adds **no** artifact to either end, so the sets are unchanged. A3 (no shared
`prog:oracleTest`) likewise holds: the new test is in `tests/test_query_declarations.py`, and
`grep -n 'test_query_declarations' tests/arc-manifest.ttl` returned **0** lines before the edit.

**Seam 2 — the control run.** Task 3 is committed at `c0f5152`, so `_ablate`'s checkout of `HEAD`
carries the extractor, the shape and the corpus test. The ablation ran without raising the
vacuous-artifact error, and `_run_control` passed — quoted in step 4 below.

**Seam 3 — comment placement.** The rationale is written **above** the edge block, never inside a
criterion block, because `scripts/cockpit.py` walks a block to the first line ending in `.`.
`tests/test_cockpit.py` is in the step 2 run and passes.

**Seam 4 — CLAUDE.md plan-rule 7 (downward same-file citation).** The comment written in step 3
carries **no `file:line` citation into `tests/arc-manifest.ttl` itself**. Its references are two
commit hashes (`44c04ae`, `ae5fefd`), a spec path with a **§ number** rather than a line, and two
paths into other files. There is therefore nothing in it that the act of writing it could shift.

### Step 1 — the second oracle test

`prog:criterion:holon:05` now carries, in addition to its membrane-health oracle:

```
    prog:oracleTest "tests/test_query_declarations.py::test_every_authored_query_names_only_declared_terms" .
```

### Step 2 — the manifest membrane did NOT force the assertion, and the plan predicted it might

```
$ ./.venv/bin/pytest tests/test_arc_manifest.py tests/test_cockpit.py tests/test_arc_landscape.py -q
47 passed in 25.55s
```

The plan says *"M17 may now force the edge's assertion — it did exactly that on 2026-08-25."* **It
did not, and could not.** M17 refuses a `prog:proposedDependsOn` that satisfies A1–A4+A6, and after
the 2026-08-25 refutation there is **no edge of either grade** to refuse — `grep -n
"criterion:holon:05" tests/arc-manifest.ttl` finds the criterion block, the rung membership and a
comment, and nothing else. `git log -S"criterion:holon:05 prog:dependsOn"` returns **no commits at
all**: the forced assertion of 2026-08-25 was refuted and deleted inside its own loop and never
reached the tracked file. So step 3 is a hand authoring, not a membrane-forced one. The plan's
"may" is correct; its parenthetical is the part that does not transfer.

### Step 3 — the edge, asserted with its rationale

`prog:criterion:holon:05 prog:dependsOn prog:criterion:holon:01 .`, under a comment that states the
reading once, cites spec §4.7 for the second-oracle ruling rather than re-arguing it (plan-rule 6),
and names the two prior authorings so the next reader does not read this as a first attempt.

**A seam the plan did not name — the generated cache.** The first run of step 2 after the assertion
failed, correctly:

```
Failed: docs/superpowers/arc-dependency-landscape.md has DRIFTED from its source at line 22:
  tracked:     … 6 of its 27 edges are grounded by a two-sided ablation and 21 are propositions.
  regenerated: … 7 of its 28 edges are grounded by a two-sided ablation and 21 are propositions.
This file is a generated cache, never hand-edited: run `./.venv/bin/python scripts/arc_depends.py`.
```

Regenerated from its source (3 insertions, 2 deletions); the run then went `47 passed in 20.35s`.
This is the documentation-governance generated-cache gate doing exactly its job — the count 6→7 and
27→28 is the arc's own record of this edge landing, and it is derived, never hand-written.

### Step 4 — O2, the real two-sided ablation

```
$ ./.venv/bin/python -c "from rdflib import Graph
from tests.test_arc_ablation import MANIFEST, ablation_refusals
g = Graph().parse(MANIFEST, format='turtle')
[print(r) for r in ablation_refusals(g)]"
(no output)
```

**No `M19: arm 1 refutes holon:05 …` line — and no other refusal either**, over the whole manifest,
not merely the new edge. Nothing is filtered from that quote; the command printed nothing.

```
$ ./.venv/bin/pytest tests/test_arc_ablation.py -q
9 passed in 42.00s
```

### Step 5 — FALSIFICATION (G6)

The second `prog:oracleTest` removed from `holon:05`, the asserted edge left in place, O2 re-run:

```
M19: arm 1 refutes …#criterion:holon:05 prog:dependsOn …#criterion:holon:01 — with
…#criterion:holon:01's artifacts ['vocab/ontology/etkl-holons.ttl'] removed, every one of
…#criterion:holon:05's oracle tests still passes
({'tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health': 'passed'}),
so …#criterion:holon:05 does not consume …#criterion:holon:01
```

That is the **2026-08-25 message, verbatim in substance**, produced again on demand. Restored, O2 is
silent again (no output).

**This is the whole content of the re-authoring.** The reading did not change and the membrane did
not change; `holon:05`'s **oracle set** did, and the ablation can now see a dependency that was
real all along but unobservable. The two authorings M19 killed were killed for the honest reason
that nothing in the tree read declarations — R135's hole. Closing the hole is what makes the third
authoring survive, and the inversion above is the only thing that distinguishes it from the two
that did not.

---

## Task 5 — close `R135`, raise what this loop defers, close the loop

### The five oracles (spec §7), each with the command that produced it

| Oracle | What it disposes | Where it is quoted above | Result |
| --- | --- | --- | --- |
| **O1** | the live violation — the RED that starts the loop | Task 3 Step 1 (`./.venv/bin/pytest tests/test_query_declarations.py -q`) | RED on `risk:order`, a **real** leak in the shipped tree; green after the declaration |
| **O2** | the two-sided ablation — the re-authoring oracle | Task 4 Step 4 (`ablation_refusals(g)` over the parsed manifest) | **no output** — no refusal of the new edge, and none anywhere else in the manifest |
| **O3** | extractor completeness — a term nested inside `BIND`/`EXISTS` | Task 1 (`tests/query-nested-bind-exists.rq`, the algebra walk vs. the text cross-check) | 7 terms that the early `dict`-branch `return` lost are recovered; 0 disagreements over 46 files |
| **O4** | the shape is not idle — 46 focus nodes, one per `.rq` | Task 3 Step 3 / the falsification | passes, **and is measured NOT to be a non-idleness oracle** — see Task 3 inversion 2 |
| **O5** | the negative fixture the conventions require | Task 2 / Task 3 (`tests/query-undeclared-term-leak.rq`) | refuses, and is one of the two tests that bite when the membrane is made idle |

Falsification blocks: Task 1 (§ FALSIFICATION — Task 1), Task 2 (Step 6, three inversions), Task 3
(Step 4, two inversions), Task 4 (Step 5, the oracle removed and restored). Full suite, Task 3
Step 5, foreground: **`1344 passed, 7 skipped, 1 xfailed, 10 warnings in 2480.68s`**.

### `R135` closed, on its own "what would close it"

The row asked for two things and got both: *"a membrane (or a test) refuses a `.rq` that names a
term no loaded ontology declares, with a negative fixture that must fail"* — and *"then, and only
then, re-author `holon:05 → holon:01`"*. The index row now reads `closed`; the detail row is struck
(`~~R135~~`), moved to `residues-closed.md` with its closure evidence in place and its original text
kept under `ORIGINAL ROW FOLLOWS`, and the `(25/124 closed)` snapshot it was raised with is
untouched.

**`R117` is NOT struck.** Spec §9 forbids it and the reason is not a formality: this instrument
reads `.rq` files, and `R117` is about the subjects of subclass axioms in a `.ttl`. `R144` records
that `R117` is open on its oracle with **no live instance**, so the next reader does not mistake an
unrealized hypothetical for a stale row.

### Raised: `R142`–`R145`

Numbering starts at `R142`, not the spec's `R140` — `R140` and `R141` landed after the spec was
written. Each snapshot was measured with the register's own command at the moment the row was
written, and is never updated afterwards:

```
$ awk -F'|' '/^\| R[0-9]+ /{n++; s=$3; gsub(/ /,"",s); if (s ~ /^closed/) c++} END{print n, c}' \
      docs/superpowers/residues.md
131 26      <- before this task
131 27      <- after R135 closed; R142 raised here
135 27      <- after all four rows
```

- **`R142`** — `prog:` (9 terms) and `docgov:` (12 terms) have no ontology file at all, so the
  in-scope filter must exclude them. The sharp edge: `prog:` is the **arc instrument's own**
  vocabulary, so the register's measuring apparatus is itself undeclared. Closes when the two files
  exist **and the filter is deleted**.
- **`R143`** — the population is `.rq` only; `vocab/shapes/`, `examples/` and `tests/*.ttl` are
  unchecked **and uncensused**. `R130`'s warning is carried into the row: census first, then
  enumerate. This is the row that would subsume `R117`.
- **`R144`** — `R117` open, no live instance, recorded as a measurement rather than left to a later
  reader's inference.
- **`R145`** — the row this **plan** found, which the spec did not have: a whole-tree integrity test
  used as a criterion's oracle broadens what the ablation reads as a dependency.

**A plan number this task corrected.** Plan Step 3 says the broad oracle makes `holon:05` fail under
ablation of *"any of the seven non-align ontologies."* Measured, by ablating each from the declaring
graph and validating the corpus:

```
dec.ttl → conforms=False   etkl-holons.ttl → False   etkl.ttl → False   iladub.ttl → False
risk.ttl → False           tab.ttl → False           tab-datagrid.ttl → conforms=TRUE
```

**Six of seven, not seven.** No authored query names a term that only `tab-datagrid.ttl` declares.
The hazard the row records is unchanged — the artifact dependency is still the whole directory, not
one file — but the number in the row is the measured one.

### The suite, re-run at the loop's head (§Done item 5)

```
$ ./.venv/bin/pytest -q
1344 passed, 7 skipped, 1 xfailed, 10 warnings in 2582.73s (0:43:02)
[exited with code 0]
```

Run in the background and **blocked on to completion in-turn** — the 43-minute wall clock exceeds
the 600s tool cap, so the summary line above is read from the finished process, not from a partial
log. The counts are **identical** to Task 3 Step 5's run, which is the expected result: Task 4 added
a `prog:oracleTest` reference to an existing test and Task 5 touched only documentation, so neither
adds a test to the population. A changed count here would have been the finding.
