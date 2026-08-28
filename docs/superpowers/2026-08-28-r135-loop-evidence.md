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
