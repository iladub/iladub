# R74 stacked grids and tab:01 — Implementation Plan (2026-10-29)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:tab:01. The loop meets tab:01 on its arm (b) and closes R74 by derivation.

**Topic:** tab · **Date:** 2026-10-29

**Execution: subagent-driven.** Start in a fresh session, on a branch off `main` after this plan's PR merges. Spec § 11.4's Q1–Q3 are ruled (spec, "Ruled 2026-10-29 by the maintainer"). A fresh worktree lacks the gitignored `baml_client/`, `corpus/`, `held-out/` and `.venv`. Symlink them from the main checkout before any probe, or every corpus number is wrong.

**Doc impact: contradiction.** Task 2 re-words `tab:StackedGrids` and widens `tab:inStack`'s domain. Both shipped in `v0.0.4` (`git show v0.0.4:vocab/ontology/tab-datagrid.ttl`, `:128-135`). Loop A's R343 classes this kind of edit as contradiction (spec § 11.2 F2). **Ruled 2026-10-29 (Q2): `contradiction`.** It blocks the next release tag until drained.

**Goal:** after this loop:

- `compile_document(cbh)` holds exactly one `tab:StackedGrids`, whose `tab:inStack` members are `p0/r2#htable1`, `#htable3`, `#htable5` and `#htable7` (O4).
- `compile_document(graincorp-stem)` holds none (O5).
- tab:01 is met on its arm (b) with two new collectable oracles (O1–O3).
- R74 is closed.

**Architecture:**

- One SPARQL CONSTRUCT (AXIOM, derivation, open world) reads intra-page `tab:continuesTable` links and each table's `tab:EntryCell` page.
- It runs once in `compile_document`, after the adoption pass and before `_seal`.
- One SHACL shape (AXIOM, constraint, closed world) disposes of what the CONSTRUCT minted.
- tab:01's two tests only read what already exists.

**Tech Stack:** Python 3, rdflib, pySHACL + rudof (`iladub.etkl.membrane.validate`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-28-r74-stacked-grids-design.md`.

- **§ 11 (adversarial review after loop A) overrides §§ 4 and 6 wherever they differ.** This plan cites § 11 in those places.
- The maintainer's rulings (the "Ruled 2026-10-28" section) override § 9.
- Read § 0, § 4, § 7, the rulings and § 11 before any task.

## Global Constraints

- **No implementation source in this plan** (CLAUDE.md § Plan authoring rule 1). Each task states interfaces, invariants and oracles. The bodies, the query and the shape included, are the implementer's.
- **`## FALSIFICATION` block in every task report** (rule 4). Remove or invert the thing the test pins and show the test failing. Restore with `cp` from a saved copy, never by hand, then show the suite green. A task report without the block fails review.
- **Neurosymbolic gate (CLAUDE.md § 8), per spec § 5:**
  - Which tables form a stack: AXIOM, derivation (CONSTRUCT).
  - Whether a stack is well formed: AXIOM, constraint (SHACL).
  - Running the query and merging its triples: PROCEDURAL glue that decides nothing.
  - **No tuned constant and no geometry.** A diff that introduces either fails review.
  - **The derivation never reads an IRI string to decide anything** (spec M7: "same page" is a graph fact). It may *mint* the stack IRI from the head's IRI.
- **A table's page is the page of its `tab:EntryCell`s** (spec § 11.2 F1; ruled 2026-10-29, Q1 arm (a)). It is never the page of "any cell", because a continuation table carries the head page's `tab:LabelCell`s (graincorp-stem: `p1#htable1` holds 17 `LabelCell`s on page 0 and 825 `EntryCell`s on page 1).
- **`is_multi_table_ambiguous`, `_GUTTER_DOMINANCE` and the frame skip are not touched** (spec § 7).
- **No consumer reads `tab:StackedGrids`** (spec § 7). The feed, the scorer and the snapshot do not change.
- **Corpus baseline:** regenerate exactly once, in Task 6, after the last input edit and after `git add` of every new input file (CLAUDE.md § Corpus baseline). Do not edit inputs while it runs. Corpus compiles are serial, one at a time, and never run beside pytest.
- **Never use two heredocs in one Bash call.** macOS has no `timeout`. Read `N passed` from pytest output, not the exit code.
- **Branch and PR only.** The required check is `test`.

## Rule-5 reconciliation (spec § 7 "What is NOT done", as amended by the rulings)

| § 7 bullet | This plan |
|---|---|
| `is_multi_table_ambiguous` not changed | No task edits `segment.py` or the frame skip. Test B's falsification mutates the skip in a scratch copy only. |
| apple p0's T4 panels not typed; `tab:AggregatingGrid` underived | No test asserts any apple stack. Task 5 raises R-new′. |
| No consumer reads `tab:StackedGrids` | No test reads the stack through the feed or the scorer. |
| "tab:04's stale R77 edge and its R80 edge are untouched" | **Overridden by the D4 ruling** (spec § 11.2 F5). Task 5 removes R77 and R74 from tab:04. R80 stays. |
| R289 untouched | No test asserts anything about the r0 header row. |

Every plan-supplied test below was checked against that table. None needs a state the code cannot construct: each synthetic test builds its own graph, and each corpus test reads a measured fact (spec § 11.1).

## Review Focus

These are inputs no oracle O1–O5 exercises. Each line names its owning task.

1. **A cross-page chain whose continuation is then section-stitched on its own page** (page 0 `A` ← page 1 `B` ← page 1 `C`). The stack is `{B, C}`, with head `B`. `A` is not a member, even though `B` carries `A`'s labels on page 0. → Task 3, test (d).
2. **A table with no `tab:EntryCell`.** It has no page, so it is never a member, and the query must not crash. → Task 3, test (e).
3. **`validate_shapes=False`.** The derivation still runs, because it is part of the record, not validation fodder, like the escalation furnish in `_seal`. → Task 4, test (c).
4. **A stack shape over two engines.** rudof cannot bind a blank-node `$this` in `sh:sparql` (`membrane.py`, the `validate` docstring). The stack node is an IRI, but check both engines anyway. → Task 2.

---

### Task 1: tab:01's two oracles (tests only)

**Files:**
- Modify: `tests/test_corpus_baseline.py`. Add Test A.
- Modify: `tests/etkl/test_boxsplit.py`. Add Test B beside `_multi_table_judgement` (`:425`).

**Interfaces:** none produced. Both tests read existing code and committed bytes.

**Test A** — `tests/test_corpus_baseline.py::test_multi_table_ambiguous_fires_nowhere_in_the_baseline` (spec § 4.1, corrected by § 11.2 F8):
- Its source list is `corpus_baseline.DOCUMENTS`, mapped to `BASELINE / f"{Path(p).stem}.json"`, the way `test_the_baseline_holds_exactly_the_listed_documents` maps it. The test refuses an empty list.
- It reads every `pages[*].regions[*].reason`.
- It asserts that none equals `"MULTI_TABLE_AMBIGUOUS"`, and that at least one region was read: a vacuous pass is a failure.
- So the falsification can point at a scratch copy, factor the scan as a module-level helper that takes the baseline directory as an argument.
- MEASURED: `grep -h '"reason"' tests/corpus-baseline/*.json | sort | uniq -c` shows no `MULTI_TABLE_AMBIGUOUS` among 524 reason lines (spec § 11.1).

**Test B** — `tests/etkl/test_boxsplit.py::test_cbh_p0_the_one_corpus_trip_is_a_framed_single_table` (spec § 4.1). Decorate it with the module's `corpus_only`. It asserts that:
- over `page_bands(CBH, 0)`, exactly one band satisfies `is_multi_table_ambiguous(dataclasses.replace(b, frame=None))`;
- that band's `frame is not None`;
- in `compile_tables(CBH, 0)`, that band's `multi_table` judgement (`_multi_table_judgement`) is `"single"` with `"frame"` in the rationale.
- MEASURED: band 10 is the trip, framed `(37.92, 449.33001, 689.64, 730.68)`. Its rationale begins `single table: cut from one closed frame the author drew` (spec § 11.1, M2/M3 rows).
- **Do not hard-code index 10.** Find the band by the predicate, so the test pins the property, not the position.

- [ ] **Step 1:** Write both tests. Run them:
  ```
  PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider \
    "tests/test_corpus_baseline.py::test_multi_table_ambiguous_fires_nowhere_in_the_baseline" \
    "tests/etkl/test_boxsplit.py::test_cbh_p0_the_one_corpus_trip_is_a_framed_single_table"
  ```
  Expect `2 passed`. They pin today's behaviour, so there is no RED phase. Falsification is the evidence.
- [ ] **Step 2: FALSIFICATION.**
  - **A:** copy `tests/corpus-baseline/` to a scratch dir. Set one region's `reason` to `"MULTI_TABLE_AMBIGUOUS"` there. Point the helper at the copy and show it fails. Then show that an empty scratch dir also fails.
  - **B:** save `src/iladub/etkl/compile.py`. Make the `if band.frame is not None:` branch fall through to the gate (replace its condition with `False`). Show B fails on the `"single"` assertion, with the judgement now `"multi"`. Restore with `cp`.
- [ ] **Step 3:** Commit: `test(tab:01): MULTI_TABLE_AMBIGUOUS fires nowhere in the baseline; its one corpus trip is a framed single table`.

### Task 2: the re-worded term and its membrane

**Files:**
- Modify: `vocab/ontology/tab-datagrid.ttl`, at `tab:StackedGrids` and `tab:inStack` (`:137-144` at `123301e`; MEASURE before editing).
- Modify: `vocab/shapes/tab-shapes.ttl`. Append after loop A's grid-index shapes, which end the file (`:664-678`).
- Create: `tests/etkl/test_stacked_grids_shape.py`.

**Ontology contract** (spec § 4.2 and the D1/D3 ruling):
- `tab:StackedGrids`: re-word the comment to "two or more tables on one page, each continuing the one before it (`tab:continuesTable`), sharing logical columns while each keeps its own header, rows and totals".
  - Say that "on one page" means *the page of its entry cells* (spec § 11.2 F1).
  - Say why the data-only wording was withdrawn: under R290's maximality, identical extents cannot yield two grids (M6).
  - Say that the stack is recognised from the author's repeated section shape.
- `tab:inStack`: domain `tab:Table` (it was `tab:DataGrid`).
  - MEASURED: `tab:HierarchicalTable rdfs:subClassOf tab:Table` (`tab.ttl:26`).
  - The membrane never loads `tab-datagrid.ttl` (`compile.py`, the R103 note above `_FULL_ONT = o`), so the widening has no inference effect.

**Shape contract** — `tab:StackedGridsShape`, `sh:targetClass tab:StackedGrids`:
- **(K1)** at least 2 members: `sh:path [ sh:inversePath tab:inStack ]`, `sh:minCount 2`.
- **(K2)** every member is a `tab:Table` (`sh:class tab:Table` on the same path). The membrane's subclass closure makes a `tab:HierarchicalTable` a `tab:Table`. **MEASURE** that `membrane.subclass_closure` reads `tab.ttl`'s `HierarchicalTable ⊑ Table` before relying on it.
- **(K3)** every member has at least one `tab:EntryCell`, and every `tab:EntryCell` of every member lies on one and the same `tab:onPage` value. Use a `sh:sparql` constraint, closed world, scoped to `$this`.
- Each part carries a distinct `sh:message` substring, so a test reads its own verdict (as `tests/etkl/test_grid_index_shape.py` does).
- **No `sh:targetClass` or `sh:class` on `tab:DataGrid`.** `tests/etkl/test_compile_membrane_shapes.py::test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape` fails otherwise ([[R103]]).

**Tests** (`test_stacked_grids_shape.py`; both `ENGINES`, the way `test_grid_index_shape.py` parametrises). Build a minimal hand-built stack: two `tab:HierarchicalTable`s, each with two `tab:EntryCell`s on page 0 and one `tab:LabelCell`, and one `tab:StackedGrids` node with two `tab:inStack` edges. Validate with `membrane.validate(g, shapes, ont, engine=…)`, where `ont` is `tab.ttl`.
- (a) **Worked example:** the stack conforms.
- (b) A one-member stack is refused by K1's message.
- (c) A member on page 1 (a "two-page stack") is refused by K3's message.
- (d) **The F1 miniature:** members whose `tab:EntryCell`s are all on page 0, while one member also holds a `tab:LabelCell` on page 1. This **conforms**. It pins that K3 reads entry cells, not every cell.
- (e) A member with no `tab:EntryCell` is refused by K3's message.

- [ ] **Step 1:** Write the tests. Run them, expecting (a) and (d) to pass and (b), (c) and (e) to fail, because the shape does not exist yet. That is RED.
- [ ] **Step 2:** Write the ontology change and the shape. Run the new file and `tests/etkl/test_compile_membrane_shapes.py`, expecting all green.
- [ ] **Step 3: FALSIFICATION.**
  - Delete K1's `sh:minCount` and show (b) passes as conforming, so its test fails.
  - Re-point K3 at `tab:hasCell` cells and show (d) fails.
  - Restore each with `cp`.
- [ ] **Step 4:** Commit: `feat(tab): re-word tab:StackedGrids to tables on one page linked by continuesTable; StackedGridsShape`.

### Task 3: the derivation query

**Files:**
- Create: `vocab/queries/stacked-grids.rq`.
- Create: `tests/etkl/test_stacked_grids_query.py`.

**Interface:**
- `interpret.run(STACKED_GRIDS_RQ, graph)` returns a graph that holds, per stack, exactly:
  - `(S, rdf:type, tab:StackedGrids)`, and
  - one `(m, tab:inStack, S)` per member.
  - Nothing else: no label and no provenance triple. Spec § 6 predicts exactly 5 triples on cbh.
- `S` is minted from the head's IRI by a fixed suffix, so the same input yields the same IRI. The implementer picks the suffix and states it in the query header.

**Invariants** (spec § 4.2 as corrected by § 11.2 F1 and F4):
- The **evidence** is a `tab:continuesTable` link between two tables whose `tab:EntryCell`s share one `tab:onPage` value. It is open world and evidence-positive: a stack exists only where such a link is *present*.
- The **head** is a table with a same-page successor and no same-page predecessor. That is a query-local `NOT EXISTS`, closed within the page.
- The **members** are the head plus every table reaching it by `tab:continuesTable+` whose entry cells are on the head's page. F4 shows this run is contiguous: chains never fork, and pages never decrease along a chain (`document.py:1757`; loop M pairs page N-1 with page N only). The query does not re-prove this; Task 2's K3 disposes of any violation.
- Use **explicit `rdf:type tab:EntryCell`**. The query runs on the merged graph with no subclass closure. MEASURED: cbh and graincorp-stem cells carry explicit `tab:EntryCell` (spec § 11.2 F1 tables).
- The query is SPARQL-only, reads no IRI substring, and has no `FILTER` on a number other than page equality.

**Tests** (hand-built graphs; no corpus):
- (a) Two tables on page 0, `B continuesTable A` → one stack with head `A` and members `{A, B}`: exactly 3 triples.
- (b) A four-table run on page 0 (cbh's shape) → one stack, 4 `tab:inStack`, 5 triples.
- (c) `B` on page 1 `continuesTable` `A` on page 0, with `B` holding `A`'s `tab:LabelCell`s on page 0 → **no stack**. This is the graincorp-stem miniature (spec § 11.2 F1).
- (d) `A` on page 0 ← `B` on page 1 ← `C` on page 1, with `B` carrying `A`'s labels on page 0 → one stack, `{B, C}`, head `B` (Review Focus 1).
- (e) A link whose earlier table has no `tab:EntryCell` → no stack, no error (Review Focus 2).
- (f) Determinism: running twice gives isomorphic graphs with identical stack IRIs.

- [ ] **Step 1:** Write the tests. They fail RED because the query file is absent.
- [ ] **Step 2:** Write the query. Run the tests, expecting green.
- [ ] **Step 3: FALSIFICATION.**
  - Replace the entry-cell restriction with `tab:hasCell` (the spec's original rule) and show (c) fails.
  - Delete the head's `NOT EXISTS` and show (b) fails, because more than one stack is minted.
  - Restore each with `cp`.
- [ ] **Step 4:** Commit: `feat(tab): derive tab:StackedGrids from intra-page continuesTable runs (stacked-grids.rq)`.

### Task 4: wire the derivation into `compile_document`

**Files:**
- Modify: `src/iladub/etkl/document.py`. Add a query constant beside `ESCALATION_FURNISH_RQ` (`:133`), and one call site.
- Create: `tests/test_corpus_stacked_grids.py`. This is the corpus-marked file for O4 and O5. Look at an existing `tests/test_corpus_*.py` for the marker and skip idiom, and carry `pytest.mark.corpus` (R173, `tests/conftest.py`).

**Seam (spec § 11.2 F3, measured at `123301e`; re-MEASURE before writing the call):**
- The call goes **after the adoption loop and before `_seal(graph, _legs_for_document(recognized, section_facts), validate_shapes)`**.
- It is a `graph += interpret.run(...)`, as the furnish in `_seal` is.
- Before writing it, measure two things:
  - that no statement between the adoption loop's end and `_seal` writes `tab:continuesTable` or `tab:onPage`;
  - that the adoption loop still refuses to withdraw a member of a chain longer than one (the `len(chain) > 1` guard).
- **Comment hazard (rule 7):** the comment block above `_seal` says the adoption branch's `section_facts = True` is "immediately above this comment". Do one of two things:
  - insert the call *after* that comment block and before `_seal`; or
  - re-word the comment by symbol.
  Do not cite any line in this file below the edit. After the edit, re-run `tests/test_source_citations.py`.
- **Unconditional:** the call does not depend on `validate_shapes`.
- **The tab leg covers it.** A same-page link is written only by the stitching loop, which sets `section_facts = True` (F3), so `_legs_for_document` returns `("tab", "dec")` on any document carrying a stack. Do not add a `section_facts` writer; the comment above `_seal` counts four writers.
- The gate classification comment names the call PROCEDURAL glue over an AXIOM (spec § 5) and says why it is irreducible.

**Tests:**
- (a) **O4** (corpus): `compile_document(cbh)`, offline (`BAML_LIVE` unset), holds exactly one `tab:StackedGrids`. Its `tab:inStack` subjects are exactly the four `p0/r2#htable{1,3,5,7}` IRIs, and `len(graph)` is the pre-change 16,154 plus 5. MEASURED: 16,154 at `123301e` (spec § 11.1, M7 row).
- (b) **O5** (corpus): `compile_document(graincorp-stem)` holds no `tab:StackedGrids` and no `tab:inStack`. Its document validation act conforms (`sh:conforms true` on `#membrane-validation`).
- (c) (synthetic or corpus, implementer's choice) With `validate_shapes=False`, cbh still carries the stack (Review Focus 3).

- [ ] **Step 1:** Write the tests and run them. Expect (a) and (c) to fail RED and (b) to pass.
- [ ] **Step 2:** Wire the call. Run the tests, and run `tests/etkl/test_stacked_grids_*.py tests/test_source_citations.py`. Expect green. Run the corpus files one at a time, serially.
- [ ] **Step 3: FALSIFICATION.**
  - Comment out the call and show (a) and (c) fail.
  - Restore. Swap in the `tab:hasCell` variant of the query and show (b) fails. This is the real-input proof of spec § 11.2 F1: the stack is minted and/or the membrane refuses the stem.
  - Restore each with `cp`.
- [ ] **Step 4:** Commit: `feat(etkl): compile_document derives tab:StackedGrids before the seal (R74)`.

### Task 5: manifest, register, pins

**Files:**
- `tests/arc-manifest.ttl`
- `docs/superpowers/residues.md`, `residues-open.md`, `residues-closed.md`
- `tests/etkl/test_datagrid.py`: the R74 pin's docstring only
- `tests/test_residue_graph.py`: the candidate pin
- `tests/test_arc_manifest.py`: the no-line-citation check (D4)
- `docs/superpowers/arc-dependency-landscape.md`: regenerated, never hand-edited

**Manifest** (spec § 4.1 plus the rulings of 2026-10-28 and 2026-10-29):
- **tab:01:**
  - Delete `prog:blockedBy "R74"`. Record it in a `# DELETED <date>` comment naming both reasons: R74 is closed (R108 ruling), and the edge's premise was false (spec M5).
  - Set `prog:met true` and `prog:metOn` to the merge date. Keep `prog:retrospective false`, since `declaredOn` 2026-08-20 is before `metOn` (M4).
  - Add Test A and Test B as further `prog:oracleTest` values, keeping the existing one.
  - Rewrite the comment above the criterion with the recorded reason in spec § 4.1: CORPUS GAP, not dead path.
- **tab:04:** remove `"R74"` and `"R77"` from `prog:blockedBy`, keeping `"R80"`, with a `# DELETED` comment. Update the comment above the criterion, which still names R74 and R77.
- **D4 (ruled 2026-10-29, Q3): all seven stale tab statements, citing the reason string.** In each `prog:statement`, replace the parenthesised `compile.py:NNN` with the reason string's call-site form, e.g. `MULTI_TABLE_AMBIGUOUS (compile.py, the escalate_region call carrying this reason string)`. The statement already opens with the reason string, so the citation needs no inner quotes; if the implementer adds some, they must be `\"`-escaped in Turtle. Use one wording for all seven. Change nothing else in a statement. MEASURED at `123301e`, with `awk '/^prog:criterion:[a-z]+:[0-9]+ a prog:Criterion/{c=$1} /prog:statement/ && /compile\.py:[0-9]/{print c, substr($0, index($0,"\"")+1, 50)}' tests/arc-manifest.ttl`, and the call sites with `grep -rnE '"(MULTI_TABLE_AMBIGUOUS|…|DATAGRID_RESIDUE)"' src/iladub` filtered to `escalate_region` calls:

  | Criterion | Reason | Stale citation | Call sites at `123301e` |
  |---|---|---|---|
  | tab:01 | `MULTI_TABLE_AMBIGUOUS` | `:596` | `compile.py:1301` |
  | tab:02 | `REGION_TILING_FAILED` | `:656, :763, :939` | `:1380`, `:1617`, `:1841` (three sites, one reason) |
  | tab:03 | `TRANSPOSED` | `:688` | `:1420` |
  | tab:04 | `ROW_GROUP_AMBIGUOUS` | `:739` | `:1486` |
  | tab:05 | `MATRIX_AMBIGUOUS` | `:830` | `:1724` |
  | tab:06 | `MERGE_AMBIGUOUS` | `:911` | `:1810` |
  | tab:08 | `DATAGRID_RESIDUE` | `:1145` | `:2215` |

  Every call site is in `compile.py`, and nothing in `scripts/` or `tests/` parses these citations (`grep` for `compile.py:` in `scripts/*.py tests/*.py vocab/queries/arc-*.rq` finds no parser). The landscape renders statements, so its regeneration below picks up the edit. **tab:05 is loop B's criterion, and tab:08 has its own open spec (#380).** If either lane merges a manifest edit to those blocks first, rebase and re-apply only the citation change.
- **Check (add to `tests/test_arc_manifest.py`):** `test_no_tab_statement_cites_a_compile_line`. Parse the live manifest. For every criterion with `prog:ofRung "tab"`, assert its `prog:statement` does not match `compile\.py:\d`, and that at least 7 tab statements were read (no vacuous pass). FALSIFICATION: put `compile.py:596` back into tab:01's statement and show the test fails.

**Register:**
- **Close R74.** Strike the number (`~~R74~~`), move the full row to `residues-closed.md` with its closure evidence, and set the index row to `closed`. This follows R341's closure in loop A. The evidence names the query, the shape and the O4/O5 tests.
- **Raise R-new** (spec § 4.3, D2 ruling). `segment._GUTTER_DOMINANCE = 2.0` is a tuned ratio. Its one real-input verdict (cbh p0 band 10) is a false positive that the frame skip disposes of. The next change to that judgement is a NEURAL proposer behind an oracle (the 2026-09-17 ruling). The row **does not** block tab:01.
- **Raise R-new′** (spec § 4.3). apple p0's three panels are not a stack under the re-worded term: no intra-page `tab:continuesTable` exists there.
- Each new row takes the next free number and carries the tally at raise time as `(c/t closed)`. MEASURE it the way the previous row did: R348 was raised at `97/338` (`residues-open.md`).

**Pins and caches:**
- `test_cbh_p0_table_b_leak_is_pinned_not_hidden`: change only the docstring's "still open as R74" and "does NOT close R74" sentences, to say R74 closed by derivation on `<date>`. The assertion is untouched.
- `tests/test_residue_graph.py`: run `./.venv/bin/python scripts/residue_graph.py --candidates` before and after the register edit, then update the `110` pin. Add a dated comment carrying the controlled diff (ADDED/REMOVED), as loop A did. R261 links [[R74]], so check its candidacy explicitly.
- Regenerate the landscape: `./.venv/bin/python scripts/arc_depends.py`.

- [ ] **Step 1:** Make the edits. Run:
  ```
  PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arc_manifest.py \
    tests/test_arc_landscape.py tests/test_arc_queries.py tests/test_residue_graph.py \
    tests/test_doc_governance.py tests/etkl/test_datagrid.py -k "not corpus or table_b_leak"
  ```
  Expect all green. Read `N passed`.
- [ ] **Step 2: FALSIFICATION.**
  - Restore `prog:blockedBy "R74"` on tab:01 while it is met. Show that `tests/test_arc_manifest.py::test_a_rung_with_no_criteria_conforms_and_is_not_a_refusal` fails with an M8 refusal; that test validates the live manifest against both membrane legs.
  - Restore the landscape from `HEAD` and show the byte-identity gate fails.
  - Restore each with `cp`.
- [ ] **Step 3:** Commit: `chore(arc): tab:01 met on arm (b); R74 closed by derivation; tab:04 loses R74 and R77; seven tab statements cite reason strings; R-new, R-new′ raised`.

### Task 6: the one regenerate, and the blast radius against § 6

**Files:** `tests/corpus-baseline/*` (generated).

- [ ] **Step 1:** Confirm that no input is untracked (`git status --short src vocab readings scripts pyproject.toml`). Then run once, serially, with nothing else compiling:
  ```
  PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate
  ```
  It takes about 24 minutes, unattended.
- [ ] **Step 2:** Read `git diff --stat -- tests/corpus-baseline/` against spec § 6.
  - **Predicted:** `cbh-stem-2026-08-03.json` moves `graph_triples` 16,154 → 16,159 and `graph_sha256`, and nothing else in that file. `inputs.json` fingerprints move. The other ten snapshots are byte-identical. The validation act adds nothing on a conforming document (spec § 11.1, § 8 row).
  - **Any other line refutes the prediction.** Explain it in the PR before merge; do not regenerate it away.
- [ ] **Step 3:** Run `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py verify`, then the full non-corpus suite (`pytest -m "not corpus"`; read `N passed`). Then run, one at a time, the corpus-marked files this loop touched: `tests/test_corpus_stacked_grids.py`, `tests/etkl/test_boxsplit.py`, `tests/etkl/test_datagrid.py`.
- [ ] **Step 4: FALSIFICATION.** `test_the_baseline_was_regenerated_from_this_tree` passes now. Show it fails against the pre-regenerate `inputs.json` (`git show HEAD~:tests/corpus-baseline/inputs.json` into place). Restore with `cp`.
- [ ] **Step 5:** Commit: `test: corpus baseline regenerated — cbh carries one tab:StackedGrids (+5 triples)`. Push, open the PR with `**Serves:** prog:criterion:tab:01`, and do not merge until `test` is green.
- **If loop B merged first and touched an input** (spec § 11.2 F9): rebase, then repeat Steps 1–4 on the rebased tree.

## Unverified (carried, not assumed)

- K2 relies on the membrane's subclass closure seeing `tab:HierarchicalTable ⊑ tab:Table`. That is measured in Task 2, not here.
- Whether rudof evaluates K3's `sh:sparql` on an IRI focus node. The blank-node failure mode is documented; the IRI case is not. Task 2 runs both engines.
- The § 6 byte-identity prediction for the ten other documents rests on reading `_seal` (spec § 11.1). Only Task 6 measures it.
