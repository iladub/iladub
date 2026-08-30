# Handoff — four rows closed by repair; the membrane answers instead of crashing

**Topic:** the membrane returns a verdict — `R133`, `R129`, `R131`(a), `R128` closed by repair, and
what the closing measurements changed

**Pointers, plus the measurements that have no other home (§3).** Nothing here is settled because it
appears here.

Authored at **~78,000 working tokens — 1.56× the 50,000 originating floor**, `handoff` logged as an
override. Part 5 was written last, not first, and **that is a deviation from the rule this repo added
on 2026-08-29** (CLAUDE.md § Loop & context hygiene). It is recorded rather than hidden, and it is the
reason every part-5 row below carries a grade: **the grading is doing the work the ordering was
supposed to do, and it is the weaker of the two.**

## 5. The next concrete action — TYPED, per action

Branch off `main` once the PR for this loop is merged.

### ASSERTED — the outcome is known; doing it *is* the work

| row | the change | oracle that must go RED first |
|---|---|---|
| `R152` | the guard that makes `_payload_nt`'s own premise machine-checked: a test over `wired_shape_files()` asserting no wired shape uses `sh:nodeKind` and no `sh:sparql` body names `isBlank`/`isIRI`/`isURI`/`BNODE` | add a throwaway `sh:nodeKind` to a wired shape → the test fails; remove it → green. The premise is TRUE at HEAD (`grep -rn nodeKind vocab/shapes/` → no output), so the test is green on arrival and its falsification is the only evidence it pins anything |
| `R138` | re-measure spec §4.5's five `document.py:1624`/`:1626` citations, or replace them with SYMBOL references (`_seal`'s membrane-health derivation, its refusing branch) that cannot drift. **Prefer symbols** — plan-rule 7 is about exactly this class | the cited lines resolve into `_seal` (`:1175-1332`), not into the `# ---- ADOPTION` comment at `:1609-1636` |
| `R137` | the register's own integrity test: every index row has exactly one detail row, in the file its status column names; every detail row has an index row; a struck `~~Rn~~` detail row appears only in `residues-closed.md` | the row already ships its falsification recipe — delete an index row leaving its detail orphaned; flip a `closed` row back to `open`. Both are green today |

All three are mechanical. **`R137` is the one to do first**, and this loop is the reason: it moved
three rows between three files by script, and nothing in the suite would have caught a half-done move.

### PROPOSED — rests on a decision that could change the loop; NOT scoped here

- **`R132`** (one `_DOC` for every document). The row is explicit that the hard part is an
  **identity/merge ruling**, not the edit — two graphs merged today silently unify their health
  values. Its blast radius reproduced during the 2026-08-29 loop at **6** non-docs files.
- **`R127`** (uncapped `dec:rationale`). Still coupled: its closure requires **four shipped oracles in
  `tests/etkl/test_membrane_health.py` (`:182`, `:362`, `:422`, `:552`) to be re-homed IN THE SAME
  ACT**, and forbids deleting them. Unchanged by this loop.

## 1. Goal

Close four register rows by repair. Done: `R133`, `R129`, `R128` closed; `R131` half (a) closed with
the half recorded, per the row's own instruction not to strike it. One new row raised (`R152`).
Register moves **31/141 → 34/142 closed**.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/residues-closed.md`, rows `~~R128~~`/`~~R129~~`/`~~R133~~` | The closure evidence, each with its falsification counts. The index line is a pointer — open the row |
| `docs/superpowers/residues-open.md`, row `R131` | The **PARTIAL** record: what (a) closed, what (b) still is, and the seam measurement |
| `docs/superpowers/residues-open.md`, row `R152` | The new row, and why the constraint was written and then removed rather than shipped |
| `vocab/shapes/dec-shapes.ttl` (tail) | The two supersession shapes and the two comment blocks that state, with the measurement, why there is no `sh:maxCount` on the arc and no `sh:nodeKind` on the object |
| `src/iladub/etkl/membrane.py` `suggester_agent` | The R129 guard and its gate classification |
| `tests/test_supersession.py`, `tests/test_suggester_guard.py`, `tests/etkl/test_page_scope_refusal.py` | The oracles. Every one has a recorded falsification (§3) |

## 3. What was decided, and where that decision is recorded

- **`legs=()` REFUSES rather than conforms.** The row left the choice open; it is decided in
  `compile.py`'s `if not legs:` comment and in `~~R133~~`'s closure. Ground: CLAUDE.md §7.
- **The `dec:supersedes` cardinality is on the IN-degree, not the arc.** Recorded in
  `dec-shapes.ttl`'s comment block and in `~~R128~~`. Decided by measurement, not preference — see
  the numbers below.
- **`sh:nodeKind sh:IRI` was written, measured, and REMOVED.** Recorded in `dec-shapes.ttl`'s second
  comment block, in `~~R128~~`, and as `R152`.
- **`R129` raises `AssertionError`, not `MembraneRefusal`.** Recorded in `suggester_agent`'s
  docstring: `MembraneRefusal.legs` is documented as never invented, and no SHACL leg refused here.
- **The corpus measurements have no other home, so they are recorded here rather than pointed at.**
  All 7 tracked documents, compiled at document scope with the subclass closure applied (the
  `corpus_graphs` recipe of `tests/etkl/test_vacuity_registry.py`), 2026-08-30, on this branch —
  i.e. **with all four repairs already wired in**, which is also the evidence that none of them
  breaks the corpus:

  ```
  dec:supersedes          9 triples total   (cbh-stem 4, apple 5; 5 of 7 documents have NONE)
    max OUT-degree        5                 apple  .../p1/adopt#p1-datagrid-admission
    max IN-degree         1                 corpus-wide
    untyped subj/obj      0 / 0             blank nodes 0    self-loops 0

  _validate at PAGE scope   14 calls, 0 refusing     (14, not one per page: the site is guarded
  _validate at DOC  scope    7 calls, 0 refusing      by validate_shapes AND a table being present)
  ```

  The two scopes partition exactly — `document.py` holds its own import-time binding of `_validate`,
  so wrapping the two separately is a clean split, confirmed by a caller-frame histogram showing
  only the two call sites.

- **Falsification evidence, per row** (CLAUDE.md plan-rule 4):

  ```
  R133  test written first, RED with the exact IndexError at compile.py:523   → 7 passed
  R131a raise reverted to bare AssertionError → 2 failed, 1 passed            → 3 passed
  R129  guard body replaced by `return URIRef(...)` → 8 failed, 2 passed      → 10 passed
  R128  both shapes deleted → 11 failed, 6 passed                             → 17 passed
  ```

  In each case the tests that survived the ablation are the ones correctly independent of it, and
  that is stated in the closure rows rather than left to be re-derived.

- **`sh:inversePath` is the FIRST in `vocab/`.** Both engines were measured on it before the shape
  shipped — pySHACL and rudof agree on the refusing and the conforming case. Recorded in
  `tests/test_supersession.py::test_both_engines_agree_on_every_negative`.

- **The index lines for the three closures were written SHORT, deliberately.** The 2026-08-29 handoff
  measured the index at 3.08× its post-split size and named the cause: closure evidence written into
  the index line as well as the detail file. Nobody has ruled whether that is a defect, so this loop
  did not change the convention — it wrote pointers, which is what CLAUDE.md defines an index line to
  be. **Recorded here and nowhere else — reversible.**

## 4. Unverified or assumed

- **`R131`'s oracle INJECTS its refusal, and that is a weaker claim than a driven one.** It pins the
  type and payload of the raise, not that any real input reaches it; a regression making the page
  gate unreachable would not fail it. The seam question was measured and the answer was no (§3).
- **`dec:SupersededOnceShape` encodes an assumption as a constraint.** Max IN-degree 1 is measured
  over **9 edges in 2 of 7 documents** — a small population. An iterative-repair pipeline that both
  section-repairs a band and then adopts a data grid over it would give one verdict two superseders
  and **refuse the whole document**. That is the intended behaviour (it is the state
  `why-escalated.rq:18-24` says it cannot answer correctly), but the day it fires the fix is to rule
  the lineage semantics, not to delete the shape. Said in the shape's own comment too.
- **`R152` is raised on one measured instance, not a survey.** No wired shape uses `sh:nodeKind`
  today, so the hazard is prospective; the *vacuity* is not — it was measured on a real fixture.
- **The full fast suite (`-m "not corpus"`) is GREEN** — `1357 passed, 7 skipped, 46 deselected,
  1 xfailed` in 20:56. It was run twice: once with only `R133`/`R131`(a)/`R129` landed (**1340
  passed**) and once with `R128` added (**1357**), and the difference is exactly `test_supersession.py`'s
  17 tests. **The corpus-marked suite was NOT run in full** — only the 7-document compile in §3, which
  exercises the same code paths but is not the same population. That is the gap to close before
  merging if CI does not cover it.
- **Branch protection is still NOT applied** — unchanged since 2026-08-29. `gh api
  repos/iladub/iladub/branches/main -q .protected` → verify; `--auto` remains a no-op if it is `false`.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.
