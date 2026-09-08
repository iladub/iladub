# Handoff — R187 is closed: the figure gate ships HARD, on a design the census moved twice

**Topic:** action **5a** of `docs/superpowers/2026-09-08-a-figure-carries-its-date-handoff.md` is
taken — the plan was written from the spec and executed end to end. [[R187]] is **closed**. The
handoff's **5b, graded PROPOSED, is CONFIRMED** — and only because O3 was run before any code, which
is what 5b said to do and what moved the design.

**Written 2026-09-08**, under the originating floor, **part 5 first**.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. PROPOSED — extend the figure scope to tracked `.py` / `.ttl`, and let a census decide the disposition

[[R189]] names three statements of a superseded corpus score outside any gate
(`src/iladub/etkl/compile.py:1288,1302`, `tests/etkl/test_datagrid.py:1085`). The machinery to catch
them **now exists and needs no design**: `_figure_facts` takes text and emits occurrences, and the
denotation rule is content-blind.

**Why this is proposed and not asserted** — R189's own row warns *"do NOT inherit markdown's
disposition: a `.py` file's decimals are mostly parameters"*, and that prediction is **untested**.
My reasoning is that the register-driven rule already answers it: a parameter only becomes a finding
if it round-matches a registered corpus reading at ≥4 decimals uniquely, which `0.5` or `1e-5` cannot
do. But that is reasoning, and this loop's whole lesson is that the census disagreed with the
reasoning **twice**.

**Run the census first, exactly as this loop did** — the script pattern is in the plan §0.1, and the
instrument now emits the facts directly, so it is one walk over `git ls-files '*.py' '*.ttl' '*.rq'`
and a hand classification of every denoting occurrence. **It fails cheaply:** if the count is small
and clean, the extension is an afternoon; if `.py` files are full of denoting decimals, R189's
warning was right and the disposition is a warning at most. **What is NOT transferable is the block
scope** — a Python file has no markdown blocks, and *"what dates a claim in code"* is an unanswered
design question, not a parameter to reuse.

### 5b. ASSERTED — the capability line is now checkable, and must be quoted from the register

`graincorp 0.9654 / bfs 0.9401 / WHO 0.9096 / apple 0.6289` is wrong in all four figures (spec §1.4),
and `bfs 0.9401` was never a reading of any commit on `main`. It is now **mechanical** to check: every
figure a document states can be matched against `tests/corpus-manifest.ttl`. Quote the register, or
re-measure and append a row. **`bfs 0.9401` is deliberately absent from the register** and the
manifest's own comment says why — do not add it.

This does not make the gate catch it: handoffs are `evidence`, which is exempt, and [[R192]] is that
question.

### 5c. PROPOSED — that [[R192]]'s population is bigger than n=1

Carried verbatim from the predecessor, **still unrun**: how many Evidence documents restate a corpus
figure they did not themselves measure? If the answer is "the capability line and nothing else",
R192 is one bad sentence, not a class. **This loop made that census one query instead of a grep** —
461 evidence occurrences already denote a registered reading, and `dg:blockDated` is already computed
for every one of them. The count is a filter away.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the plan, and the O3 census | `docs/superpowers/plans/2026-09-08-a-figure-carries-its-date.md` §0 | why the hard gate is licensed; the two corrections the census forced; `sep`'s derivation table; the price, stated before it was built (§0.4) |
| the spec | `docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md` | unchanged this loop. §1.4 is still the only current reading of the seven scores |
| the register | `tests/corpus-manifest.ttl` § Readings (appended) | 18 rows, dated, append-only, one node per distinct value; what is deliberately NOT in it |
| the gate | `tests/test_doc_governance.py::test_no_wiki_page_states_an_undated_reading` | the hard disposition and its message |
| the derived-precision rule | `tests/docgov_extract.py::separating_precision` + `denotes` | the one place a tuned constant could have entered and did not |
| the new rows | [[R193]] [[R194]] in `residues-open.md` | read the row, never the index line |

## 2. What changed

One branch, `a-figure-carries-its-date-gate`, on top of PR #179's spec commit.

- **New:** `vocab/queries/docgov-undated-figure.rq`, the plan.
- **Extended:** `vocab/internal/corpus.ttl` (7 reading terms), `tests/corpus-shapes.ttl`
  (`cor:ReadingShape`), `tests/corpus-manifest.ttl` (18 reading nodes, appended — no existing line
  touched), `tests/docgov_extract.py` (blocks / is_dated / separating_precision / denotes /
  load_readings / `_figure_facts`, and one read hoisted so no file is opened twice),
  `tests/test_doc_governance.py` (+2), `tests/test_docgov_extract.py` (+7),
  `tests/test_docgov_queries.py` (+3), `tests/test_corpus_manifest.py` (+3),
  `vocab/internal/docgov.ttl` (11 `dg:` figure terms), `tests/test_artifact_terms.py` and
  `tests/test_artifact_declarations.py` (the earned counts, re-measured not copied).

**The two declaration instruments caught real omissions, and both did it only after `git add`** —
the populations are `git ls-files`, so a new artifact is invisible until staged. `.rq` population
50→51. Census: 59→66 and 62→69 from the seven `cor:` terms (**both** numbers, same 7, the drain
terms' shape), then 69→**71** from `docgov:FigureOccurrence` and `docgov:Reading` — **live only**, so
the 136-artifact-tree number stays 66 and `_SURPLUS_IN_CENSUS` grows by two. Measured why only the
two classes move it: `_demanded()` collects terms named as OBJECTS, so a class is demanded by the
`rdfs:domain`/`rdfs:range` around it while a property is named by nothing but its own declaration.
- **Repaired:** `docs/wiki/concepts/data-grid.md` and `neurosymbolic-exemplars.md` — 8 claims dated,
  **no figure rewritten**; both `updated:` moved to 2026-09-08.

Instrument runtime: **~12 s** for `extract()` over the whole tree (the figure walk is new I/O and did
not dominate); `pytest tests/test_doc_governance.py` **6 passed, 2 warnings, ~24 s**.

## 3. What was decided, and where that decision is recorded

- **Arm A** for the register — `tests/corpus-manifest.ttl`, not a new file. Plan §1 D-A. Not escalated:
  no Contract-class file is touched, and the spec had already recommended it.
- **`cor:notQuotable` filters FINDINGS, not the register.** Plan §1 D-C and
  `vocab/internal/corpus.ttl`'s term comment. Ground: dropping a row shrinks the extension `sep` is
  computed over and can promote a different literal to uniqueness.
- **The disposition lives in the test, not in a SHACL shape.** `_undated`'s docstring. Ground: this
  instrument's own split — `staleAgainstEvidence` is a test-side gate over a derivation,
  `ContradictionDrainShape` is shape-side because it validates a register's integrity.
- **One reading node per distinct VALUE, with repeatable `cor:readAt`.** `corpus:reading`'s comment.
  Ground: two nodes bearing one value make that value ambiguous to every consumer, and a
  re-confirmation is not a new reading.
- **`bfs 0.9401` is not registered.** The manifest's § Readings comment. Nowhere else.

## 4. Unverified or assumed

- **The full suite has not reported at the time of writing.** An earlier whole-suite run was
  started and then **killed deliberately**: files changed underneath it, so its result would have
  described a tree that no longer exists. Nothing was learned from it and nothing should be. `tests/test_doc_governance.py`,
  `test_docgov_extract.py`, `test_docgov_queries.py`, `test_corpus_manifest.py`,
  `test_artifact_terms.py`, `test_source_ownership.py`, `test_docgov_shapes.py` are green; the
  whole-suite run and CI are the checks that have not.
- **The register's historical rows are transcribed from evidence documents, not re-measured.** Only
  the 2026-09-08 seven were compiled in this arc (spec §1.4). A prior row's value is as good as the
  document `cor:recordedIn` names — which is why every row names one.
- **Two dates in the register are inferred rather than stated.** `graincorp-stem`'s
  `0.9654553611484971` is dated 2026-08-03 from the manifest note that records it **at four
  decimals**; the full-precision form appears undated in `compile.py`. Same shape for apple's
  `0.06068601583113457` (2026-08-09, from the adoption spec).
- **O3 was a census over tracked MARKDOWN.** `.py`, `.ttl` and `.rq` were never enumerated — that is
  5a, and its false-positive rate is unmeasured.
- **`sep == 4` is asserted by value and nothing predicts when it will move.** [[R193]].
- **My own hand census was wrong on `table-holon-compilation.md`** — it read a window instead of the
  block, and predicted 10 findings where the instrument found 8. The instrument was right. Any figure
  in this handoff taken from a hand count rather than the instrument deserves the same suspicion.
