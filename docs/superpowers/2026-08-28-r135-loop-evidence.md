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
