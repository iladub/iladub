# R74 and tab:01: stacked panels named, MULTI_TABLE_AMBIGUOUS's silence explained (design, 2026-10-28)

**Serves:** prog:criterion:tab:01 — MULTI_TABLE_AMBIGUOUS disposed, today `prog:met false` and
`prog:blockedBy "R74"` (`tests/arc-manifest.ttl`, the `prog:criterion:tab:01` block).

**Doc impact: increment.** One ontology term (`tab:StackedGrids`) is re-worded and starts being
derived, `tab:inStack`'s domain widens, one query, one shape and three tests are added, and cbh's
corpus snapshot moves. No released meaning changes: `grep -rn StackedGrids docs/ --include=*.md`
outside `docs/superpowers/` and `docs/wiki/` finds nothing (measured 2026-10-28), so no published
site page asserts the old wording.

**Status: DRAFT — not approved.** § 9 lists the decisions that belong to the maintainer. Measured at
`main` `087c1ca` in an isolated worktree, page-scope probes only (no full-corpus compile).

## 0. The oracle, before the design

What would show this design wrong, on real input:

- **O1 — "fires nowhere" is false.** Any region in any of the eleven committed snapshots under
  `tests/corpus-baseline/` carries `"reason": "MULTI_TABLE_AMBIGUOUS"`. Today: 0 of 11 (§ 2, M1).
- **O2 — the corpus-gap reason is false.** On cbh p0, either `is_multi_table_ambiguous` returns
  `False` on the T1 box band with its frame cleared, or it returns `True` on any *unframed* band of
  any corpus or held-out page. The recorded reason (§ 4.1) says the corpus reaches the predicate in
  exactly one place, a framed single table, and nowhere unframed. Today: true on cbh p0 band 10
  only (M2, M3).
- **O3 — the path is dead.** `tests/etkl/test_closing_slice.py::test_multi_table_ambiguous_escalates`
  fails, or `tests/etkl/test_boxsplit.py::test_u7_the_same_content_without_its_frame_still_escalates`
  fails. Today both pass (M4).
- **O4 — the stack derivation is wrong on cbh p0.** After the change, `compile_document(cbh)` does
  not hold exactly one `tab:StackedGrids` whose `tab:inStack` members are exactly
  `p0/r2#htable1`, `#htable3`, `#htable5`, `#htable7`.
- **O5 — the derivation over-fires on real input.** `compile_document(graincorp-stem)` holds any
  `tab:StackedGrids`. Its three tables form a chain across three pages (M6), which is pagination,
  not a stack. This is the real-input negative.

O1–O3 decide tab:01. O4–O5 decide R74. Neither half's oracle reads the other half's output.

## 1. Goal

Meet tab:01 on its arm (b) honestly, and close R74 on its own terms rather than by deleting the
edge that names it.

## 2. Measured (2026-10-28, `087c1ca`)

**M1 — MULTI_TABLE_AMBIGUOUS fires on no committed snapshot.** A scratch script read every
`tests/corpus-baseline/*-*.json`, collecting the `reason` of every `escalated` region:

```
apple            ['DATAGRID_RESIDUE']
arxiv            ['KIND_NOT_SUPPORTED', 'MERGE_AMBIGUOUS', 'ROUND_TRIP_FAIL']
bfs              ['DATAGRID_RESIDUE', 'KIND_NOT_SUPPORTED', 'REGION_TILING_FAILED']
caltrain         ['DATAGRID_RESIDUE']
cbh              []
fed-h41          ['DATAGRID_RESIDUE', 'KIND_NOT_SUPPORTED', 'MATRIX_AMBIGUOUS', 'REGION_TILING_FAILED', 'ROUND_TRIP_FAIL', 'RULE_SEPARATED_INK']
graincorp-cap    []
graincorp-stem   []
ons              ['DATAGRID_RESIDUE', 'KIND_NOT_SUPPORTED']
who-covid        ['DATAGRID_RESIDUE', 'KIND_NOT_SUPPORTED', 'MERGE_AMBIGUOUS']
who-wfa          []
```

**M2 — the predicate trips once on real input, on a single table, and the frame disposes it.**
`page_bands` + `segment.is_multi_table_ambiguous` on every band of all 27 corpus pages and 37
held-out pages, each band tested with its `frame` cleared (`dataclasses.replace(b, frame=None)`):
one `True`, `cbh p0 band 10 framed 'PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL …'`.
Zero errors, zero other trips, framed or not. Band 10 is T1, one table in one closed box. The
box-split spec measured the same trip on 2026-09-28 (`2026-09-28-box-split-design.md` § 9.2:
*"The gate returns `True` on T1 and `False` on T2"*). It called it a false positive, and that is why
the frame skip exists.

**M3 — on the compile, the trip is recorded and overruled, not escalated.**
`compile_tables(cbh, 0)`. Band 10's `multi_table` decision holon chooses `single` with the
rationale `single table: cut from one closed frame the author drew, bbox (x0, x1, top, bottom) =
(37.92, 449.33001, 689.64, 730.68)`, and band 11 records the same. The skip is
`compile.compile_tables`'s `if band.frame is not None:` branch, just above the
`escalate_region(..., "MULTI_TABLE_AMBIGUOUS", ...)` call (compile.py:1298-1310 at `087c1ca`).
**The criterion's `prog:statement` still cites `compile.py:596`, which is stale.** M10 checks
`prog:source` only, so nothing flags it.

**M4 — the path is live on synthetic input.**
`pytest -q tests/etkl/test_closing_slice.py::test_multi_table_ambiguous_escalates
tests/etkl/test_boxsplit.py -k "multi_table or u6 or u7"` → `3 passed, 28 deselected in 7.73s`.

**M5 — the predicate cannot see R74's subject.** `is_multi_table_ambiguous` cuts at
`_widest_gutter_cut`: a vertical gutter, splitting a band's words into `left` and `right` by
`x`-centre. R74 is about tables stacked in `y`. The manifest's comment above tab:01 justifies the
edge with *"R74 measures the cbh data grid leaking one row from a SECOND table on the same page —
which is this reason's exact subject matter"*. That is not the predicate's subject. And the leak
premise was measured FALSE at HEAD on 2026-10-05 (`docs/superpowers/2026-10-05-cbh-carried-grid-read.md`
§ 2.3), which is why the maintainer ruled R74 out of cbh's acceptance the same day.

**M6 — `tab:StackedGrids` as defined has no instance, and cannot have one.**
`derive_data_grids` on every page (27 corpus, 37 held-out): only bfs p5 (`(27,10),(19,12)`), fed p1
(`(14,7),(16,2)`) and fed p6 (`(15,2),(12,6)`) yield two grids, and **no page yields two grids
with identical column extents**. cbh p0 yields **one** grid of 45 rows × 16 columns: all four port
rosters (10 + 16 + 14 + 5 vessel rows) in one rectangle. apple p0 is the typology's T4 instance
(`2026-08-08-data-grid-types-elements-axioms.md` § 3, *"apple p0 (three panels …)"*), and it yields
one grid, (31, 5). This is structural, not a corpus accident. `derive_data_grids` (R290) re-seeds
only on lines no earlier grid admitted, and a panel that shares the first panel's column signature
is admitted by the first, maximal, rectangle. So two grids with *identical* extents is what
maximality rules out. The ontology comment (`tab-datagrid.ttl`, `tab:StackedGrids`) defines a term
the derivation it sits beside can never produce.

**M7 — cbh's stack is already carried, under another name.** `compile_document(cbh)` offline
(`BAML_LIVE` unset; 16,154 triples, the snapshot's own `graph_triples`):

```
HierarchicalTable  r2#htable1, r2#htable3, r2#htable5, r2#htable7
continuesTable     (htable3→htable1) (htable5→htable3) (htable7→htable5)
continuesColumn 60 · inLogicalColumn 80 · hasRepeatedHeader 0
PrintedTotal       printedtotal2/4/6/8 (one per roster) + printedtotal9 aggregating the four
DataGrid / StackedGrids / inStack   0 / 0 / 0
```

The links come from loop Q's intra-page section stitching (`document.compile_document`, the
`page_section_groups` loop, licensed by `vocab/queries/section-repeat.rq`). `tab:continuesTable`'s
own comment says an intra-page section break chains *"into one logical table exactly as pages
do"*. So the four panels are four distinct tables sharing logical columns. That is the
`tab:StackedGrids` comment's *"distinct grids that happen to share an addressing"*, with no
node that says so. Tables carry no `tab:onPage`, but their cells do (EntryCell, LabelCell,
PrintedTotal, RuleSpan). So "same page" is a graph fact, not something read out of an IRI.

**M8 — across the eleven snapshots, there is one intra-page chain and one cross-page chain.**
The intra-page chain is cbh `[p0/r2#htable1 … #htable7]`. The cross-page chain is graincorp-stem
`[p0#htable2, p1#htable1, p2#htable1]`. No other document has a chain of more than one member.

**M9 — the register.** R74 is open. Its closure condition is *"Derive `tab:StackedGrids`"*,
reaffirmed by its 2026-09-30 narrowing (*"this row's closure is the derivation"*). R74 also blocks
`prog:criterion:tab:04`, alongside R77 and R80. **R77 is closed (2026-10-01) and still named
there.** That is a stale edge under the R108 ruling, outside this lane, and it is noted in § 9.
Highest row: R340; tally 96 closed of 330 rows in `residues.md`.

## 3. What the measurements change

1. **R74 does not block tab:01 on the evidence.** The edge's stated reason is false twice over (M5).
   But the M8 arc rule makes the edge binding, and deleting an edge whose residue is still open is a
   maintainer ruling, as it was for etkl:03 on 2026-10-05. So this spec **closes R74** (§ 4.2).
   Under the standing R108 ruling, closing R74 deletes every `prog:blockedBy "R74"`. The false
   premise is recorded beside the deletion, so the edge is not just dropped. § 9 D1 offers the
   other order.
2. **R74 cannot close by deriving the term as worded** (M6). A query for "≥ 2 DataGrids with
   identical extents" would fire on nothing, by construction, and would be a dead path dressed as
   a closure. The term has to be re-worded to the stack the pipeline actually recognises (M7).
3. **The MULTI_TABLE_AMBIGUOUS heuristic has now been refuted once on real input** (M2: its only
   trip is a false positive). The frame skip disposes of it, and correctly. But under the
   2026-09-17 ruling ("one geometric attempt, then NEURAL") the next change to that judgement is a
   NEURAL proposer, not a second heuristic, and that has to be written down (§ 4.3).

## 4. Design

### 4.1 tab:01: arm (b), made collectable

- **Test A (CI, reads committed bytes):**
  `tests/test_corpus_baseline.py::test_multi_table_ambiguous_fires_nowhere_in_the_baseline`. It
  loads every snapshot listed in `tests/corpus-baseline/inputs.json` (and refuses an empty list)
  and asserts that no region's `reason` equals `"MULTI_TABLE_AMBIGUOUS"`. It is valid only
  because the R305 gate forces the snapshots to be regenerated from the current inputs.
  **FALSIFICATION:** edit one snapshot region's reason to the string in a scratch copy and show
  the test fails.
- **Test B (corpus-marked, real input):**
  `tests/etkl/test_boxsplit.py::test_cbh_p0_the_one_corpus_trip_is_a_framed_single_table`. On cbh
  p0 it asserts:
  - exactly one band trips `is_multi_table_ambiguous` with its frame cleared;
  - that band carries a frame;
  - its `multi_table` judgement chooses `single` with `frame` in the rationale.

  The existing `_multi_table_judgement` helper is reused. **FALSIFICATION:** delete the
  `band.frame is not None` branch's skip and show the judgement flips to `multi`.
- **Manifest edit (`tests/arc-manifest.ttl`, tab:01):**
  - drop `prog:blockedBy "R74"`, recorded in a `# DELETED` comment that names both reasons: R74
    closed (R108 ruling) and M5's false premise;
  - set `prog:met true`, `prog:metOn` to the merge date, and `prog:retrospective false`
    (declaredOn 2026-08-20 < metOn);
  - add Tests A and B as further `prog:oracleTest` values (the property is multi-valued; arc-shapes
    A3 comment), keeping `test_multi_table_ambiguous_escalates`;
  - rewrite the comment above the criterion with the **recorded reason**: *CORPUS GAP, not dead
    path. The path is live (O3). The corpus reaches the predicate once, on cbh p0's T1. That is a
    single table the author closed in a box, and the ruled frame skip (box-split § 9, an AXIOM)
    overrules it. No unframed band on 64 pages trips it (M2). The predicate's one real-input
    verdict is a false positive, recorded as R-new (§ 4.3).*
  - The stale `compile.py:596` in `prog:statement` is corrected only if the maintainer allows
    editing a statement (§ 9 D4).

### 4.2 R74: `tab:StackedGrids` re-worded and derived

- **Ontology (`vocab/ontology/tab-datagrid.ttl`, our namespace):**
  - **Re-word `tab:StackedGrids`** to: *two or more tables on one page, each continuing the one
    before it (`tab:continuesTable`), so they share logical columns while each keeps its own
    header, rows and totals.* The comment must say why the data-only wording was withdrawn (M6:
    under maximality, identical extents cannot yield two grids) and that the stack is now
    recognised from the author's repeated section shape, which is metadata that was "not yet
    known" in 2026-08 and now is.
  - **Widen `tab:inStack`'s domain** from `tab:DataGrid` to `tab:Table`. A roster table is not a
    data grid. The membrane reads only `rdfs:subClassOf` (`compile.py`, the R103 note above the
    ontology load), so this is a meaning fix with no inference effect.
- **Derivation, AXIOM, open world (`vocab/queries/stacked-grids.rq`).**
  - It runs over the merged document graph, after intra-page stitching, inside
    `compile_document`.
  - Its evidence is a `tab:continuesTable` link whose two tables have cells sharing one
    `tab:onPage` value.
  - A stack is a connected component of those intra-page links. It mints one `tab:StackedGrids`
    node per component, named from the component's head, and one `tab:inStack` per member.
  - It is evidence-positive: a stack exists only where an intra-page link is *present*. Any
    "head" test is query-local `NOT EXISTS` within the page.
  - A chain that crosses pages contributes only its same-page runs.
  - **Seam the plan must MEASURE, not assume:** where in `compile_document` the stitched links
    and cell `tab:onPage` facts are both final, and whether any later pass (the R7 adoption, the
    `/r2` re-read) can still remove a member table after that point.
- **Constraint, SHACL, closed world (`vocab/shapes/tab-shapes.ttl`):** `tab:StackedGridsShape`.
  - A stack has at least 2 `^tab:inStack` members.
  - Every member's cells lie on one page.
  - Worked example and negative test, per CLAUDE.md: a two-page "stack" and a one-member stack
    must both fail.
- **R74's existing pin stays.** `test_cbh_p0_table_b_leak_is_pinned_not_hidden` still pins the
  leak's absence. Only its docstring's "still open as R74" is updated.

### 4.3 Rows the implementing loop raises

- **R-new — MULTI_TABLE_AMBIGUOUS rests on a tuned constant, and its only real-input verdict is
  wrong.** `segment._GUTTER_DOMINANCE = 2.0` is a tuned ratio, prima facie evidence under § 8.
  Over 64 pages its one trip is cbh T1, a single table (M2). Per the 2026-09-17 ruling, the next
  change is a NEURAL proposer behind an oracle, not a retuned ratio. Whether this row blocks tab:01
  is § 9 D2.
- **R-new′ — apple p0's three panels (the typology's T4 instance) are not a stack under the
  re-worded term.** They are cut-in-headed sections under one boxhead with no repeated header box,
  so no intra-page `tab:continuesTable` exists (M8).

## 5. Gate classification (CLAUDE.md § 8)

| Decision | Class | Why |
|---|---|---|
| Which tables form a stack | **AXIOM, derivation** (SPARQL CONSTRUCT, open world) | Declarative over facts already in the graph (`tab:continuesTable`, cell `tab:onPage`); no geometry, no constant |
| Is a stack well-formed | **AXIOM, constraint** (SHACL, closed world) | Membrane only, never derives |
| Running the query and adding its triples | PROCEDURAL glue | Decides nothing; carries no constant |
| Whether bands repeat the author's section shape | AXIOM, **unchanged** | `section-repeat.rq` |
| Whether a band holds two side-by-side tables | Existing geometric heuristic, **unchanged here** | Refuted once on real input (M2), so R-new; the next attempt is NEURAL |
| "Fires nowhere" (Test A) | Test over committed artifacts | Not decision code |

No tuned constant is introduced.

## 6. Predicted blast radius on `tests/corpus-baseline/`

`vocab/` and `src/` both change, so a regenerate is required.

- **cbh:** `graph_triples` 16,154 → 16,159 (one `rdf:type tab:StackedGrids` triple plus four
  `tab:inStack` triples, and nothing else, if the plan adds no label), and `graph_sha256` moves.
  `pages`, `score` (1.0), `chains` and `adopted` are byte-identical.
- **graincorp-stem:** byte-identical. Its only chain is cross-page (O5).
- **The other nine:** byte-identical. They have no chain longer than one table (M8).
- **`inputs.json`:** fingerprints move.

Any other line in the diff refutes the prediction and must be explained before merge. Arm B
(§ 9 D3) predicts `inputs.json` only.

## 7. What is NOT done

- `is_multi_table_ambiguous` is not changed, re-tuned or replaced (R-new).
- apple p0's T4 panels are not typed (R-new′). `tab:AggregatingGrid` stays underived.
- No consumer (feed, scorer) reads `tab:StackedGrids`. The derivation names what is carried and
  moves no number.
- tab:04's stale R77 edge and its R80 edge are untouched. tab:04 loses its R74 edge only as a
  consequence of R74's closure.
- [[R289]] (cbh header row carried as data) is untouched. It sits inside the very tables the stack
  names, and the stack derivation neither depends on it nor hides it.

## 8. Unverified

- The probes were scratch scripts and are not kept. What they did is described inline in M1–M8.
- The compile was offline (`BAML_LIVE` unset). It reproduces the snapshot's 16,154 triples, but
  whether the snapshots were generated offline was not checked.
- Whether a validation report or membrane-health triple added for the new shape enters the output
  graph of *every* document. If it does, the "nine byte-identical" prediction fails, and the
  regenerate will show it.
- `tab:`'s publication status (w3id registration) was not checked. It decides whether re-wording
  is `increment` or `contradiction`.
- The ordering seam in § 4.2.

## 9. Decisions for the maintainer

- **D1 — order.**
  - **(a) Recommended:** close R74 by the § 4.2 derivation. The tab:01 edge then falls under the
    R108 ruling.
  - **(b)** Rule the tab:01 edge deleted now on M5 alone (the 2026-10-05 etkl:03 precedent), and
    take R74 as its own loop.
- **D2 — does R-new block tab:01?**
  - **Recommended: no.** Arm (b) asks whether the silence is a gap or a dead path. The measured
    answer is a gap: the one real trip is disposed upstream by a ruled AXIOM, not suppressed by a
    flagged defect, which is the line that separates this case from tab:03/R71.
  - If yes, tab:01 waits for the NEURAL loop.
- **D3 — R74's arm.**
  - **(A) Recommended:** derive the re-worded term (§ 4.2).
  - **(B)** Mark `tab:StackedGrids` `owl:deprecated`, with `rdfs:seeAlso tab:continuesTable`, and
    close R74 on M6 + M7. That is no code and no output change, but the row asked for a
    derivation, and B answers it with a deletion.
- **D4:** may the stale `compile.py:596` inside tab:01's `prog:statement` be corrected in place?

## 10. Adversarial pass

- ***"Re-wording the term to match what you can derive is moving the goalposts."*** It would be,
  if the old wording were satisfiable. M6 shows it is not, by the maximality the repo already
  ruled (R290). The re-wording keeps the term's own operative clause, *"distinct grids that share
  an addressing"*, and changes only the evidence it is read from. D3 (B) is offered for a
  maintainer who reads it the other way.
- ***"tab:StackedGrids duplicates `tab:continuesTable`."*** Partly. It is entailed by
  `continuesTable` plus shared `onPage`. But the stored link conflates pagination with
  sectioning, which is exactly what O5 tests, and the repo already materialises entailed
  closures where a consumer would otherwise parse names (`tab:inLogicalColumn`). If the
  maintainer judges a typed node not worth a stored fact, that is D3 (B).
- ***"Corpus gap is a euphemism; the gate is suppressed, as tab:03's is."*** In tab:03 the
  suppressor (R71) is a registered defect protecting false positives. Here the suppressor is a
  ruled AXIOM over the author's drawn box, and the thing suppressed is itself the false positive.
  The honest residue is R-new, raised rather than hidden, and D2 lets the maintainer make it
  binding.
- ***"64 pages is a small denominator for 'no unframed trip'."*** Yes. The claim is scoped to
  these 64 pages, and Test A re-checks it on every regenerate. It is not a claim about documents
  not yet in the corpus.
- ***"Test A reads bytes that CI cannot regenerate."*** True (R305: `check` proves freshness, not
  byte-equality). It is the strongest collectable form available, and Test B carries the
  real-input proof locally.

## Ruled 2026-10-28 by the maintainer (in chat)

- **D1 and D3:** close R74 by deriving the re-worded `tab:StackedGrids`, which means tables on one page linked by `tab:continuesTable`. The derivation is a SPARQL CONSTRUCT, and a SHACL shape checks it. Deprecating the term instead was rejected.
- **D2:** the gate's tuned `_GUTTER_DOMINANCE = 2.0` gets a new residue row. That row records that the next change to the gate is a NEURAL proposer (the 2026-09-17 ruling). It does **not** block tab:01.
- **D4:** stale `file:line` citations in `prog:statement`s are corrected in place. The same change removes tab:04's edge to the closed R77.

## 11. Adversarial review after loop A (2026-10-29)

Re-measured at `main` `123301e` (loop A, PR #382, merged after this spec's `087c1ca`), in an
isolated worktree, with page-scope and single-document probes only: no full-corpus compile and no
`corpus_baseline.py regenerate`. Each finding is typed in this repo's epistemics. An
**assertion** is measured here, with its measurement inline. A **proposition** rests on a
prediction the implementing loop must run. Findings that need the maintainer are collected in
§ 11.4. The rulings above are not re-opened.

### 11.1 Drift since `087c1ca`

Loop A changed compile inputs (`git diff --stat 087c1ca HEAD -- src vocab`):

- `etkl/datagrid.py` (+5): `tab:rowIndex` and `tab:colIndex` are emitted.
- `feed.py` and `truth.py`.
- `tab-datagrid.ttl` (+9): `tab:rowIndex`.
- `tab-shapes.ttl` (+60): four grid-index shapes.

`compile.py`, `segment.py` and `document.py` are untouched, and so is
`tests/corpus-baseline/cbh-stem-2026-08-03.json`.

| Spec claim | At `123301e` | Drift |
|---|---|---|
| M1: no snapshot region carries `MULTI_TABLE_AMBIGUOUS` | `grep -h '"reason"' tests/corpus-baseline/*.json \| sort \| uniq -c` finds 0 such lines. Each document's set of escalated reasons is identical to M1's table | none |
| M2: one trip, on cbh p0 band 10, which is framed; 27 + 37 pages; 0 errors | A scratch probe ran `page_bands`, then `is_multi_table_ambiguous(dataclasses.replace(b, frame=None))` on every band. Output: `pages {'corpus': 27, 'held-out': 37}`, `trips [('cbh-stem-202', 0, 10, True, 'PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL')]`, `errs []` | none |
| M3: bands 10 and 11 choose `single` with the frame rationale; the skip is at compile.py:1298-1310 | Both rationales are reproduced byte for byte. `if band.frame is not None:` is at `compile.py:1282`, and the escalation at `:1301` | none. The spec's range starts at the `else` arm's record; the branch itself is at `:1282` |
| M4: 3 passed | `3 passed, 28 deselected in 9.22s` | none |
| M6: bfs p5, fed p1 and fed p6 each yield two grids; cbh p0 yields (45, 16); apple p0 yields (31, 5) | `derive_data_grids` gives identical tuples on all 64 pages | none |
| M7: cbh offline: 16,154 triples; 4 HierarchicalTables; 3 links; 60/80/0; 0/0/0 | identical (`env -u BAML_LIVE`) | none |
| M8: one intra-page chain (cbh) and one cross-page chain (graincorp-stem) | identical, read from the `chains` of the eleven snapshots | none |
| M9: highest row R340; 96 closed of 330 | Highest row is now **R348**, raised at **97/338** (`residues-open.md`). Loop A closed R341 | **drift**: the implementing loop computes the tally when it raises a row |
| § 8: "whether a validation report … enters every document's graph" | `_seal` writes only the act's `rdf:type`, `prov:used` and `sh:conforms`, plus one `etkl:refusingLeg` per *refusing* leg (`document.py`, `_seal`, the `act = URIRef(...)` block). A new shape that conforms adds no triple to any document | **resolved by reading**. The regenerate confirms it |
| § 8: whether `tab:` is published | see F2 | **resolved, against the spec** |

### 11.2 Findings

**F1 — ASSERTION, blocking. The § 4.2 evidence rule fires on graincorp-stem.** So the design as
written refutes O5, and the § 4.2 shape would then refuse the stem document.

§ 4.2's rule is *"a `tab:continuesTable` link whose two tables have cells sharing one
`tab:onPage` value"*. But a continuation table carries the head page's header labels as its own
`tab:LabelCell`s, and those are measured on page 0. Counting each table's cells by
`(onPage, rdf:type)` over `tab:hasCell`, after an offline `compile_document(graincorp-stem)`:

```
p0#htable2 [(('0','EntryCell'), 586), (('0','LabelCell'), 17)]
p1#htable1 [(('0','LabelCell'), 17), (('1','EntryCell'), 825)]
p2#htable1 [(('0','LabelCell'), 17), (('2','EntryCell'), 741)]
```

The spec's own rule, written as a query:

```
SELECT ?a ?b ?pg WHERE { ?a tab:continuesTable ?b .
  ?a tab:hasCell ?ca . ?ca tab:onPage ?pg . ?b tab:hasCell ?cb . ?cb tab:onPage ?pg }
→ [('p1#htable1','p0#htable2','0'), ('p2#htable1','p1#htable1','0')]
```

Consequences:

- Both cross-page links share page 0. So the spec's derivation mints a three-member stack on
  graincorp-stem, which is exactly what O5 forbids.
- § 4.2's constraint (*"every member's cells lie on one page"*) then fails on `p1#htable1` and
  `p2#htable1`. The document membrane refuses, and `compile_document(graincorp-stem)` raises
  `MembraneRefusal`. The regenerate breaks instead of showing a diff.
- No cell carries two `tab:onPage` values (0 on cbh, 0 on the stem). The defect is in which cells
  the rule reads, not in the data.
- On cbh every cell of every member is on page 0 (`EntryCell` 170/268/228/84, `LabelCell` 20
  each), so cbh cannot tell the two rules apart. Only the stem can, and that is what O5 is for.

**The remedy fits the ruling's words ("tables on one page"), but it decides what a table's page
is, so it is Q1.**

**F2 — ASSERTION. By loop A's own precedent the re-wording is `contradiction`, not
`increment`.** The released tag ships the wording this spec rewrites:

- `git show v0.0.4:vocab/ontology/tab-datagrid.ttl` holds the old `tab:StackedGrids` comment at
  `:128-132`, and `tab:inStack … rdfs:domain tab:DataGrid` at `:134`. v0.0.4 is `1007d48`,
  2026-09-08.
- Loop A raised R343 on the same class of edit: a released `tab:` comment that says something no
  longer true. It recorded: *"A fix rewrites a released assertion, so it is contradiction-class
  (`Doc impact: contradiction` blocks the release tag)"* (`residues-open.md`, R343).
- The spec's `increment` rests only on a grep of the site pages under `docs/`.
- `docs/w3id/iladub-htaccess.md` has no `tab` rewrite rule, so the term is not served by w3id. But
  it is in the release.

This spec's own declared value is frozen (CLAUDE.md § Documentation governance), so the open
question is the plan's value. That is Q2.

**F3 — ASSERTION. The ordering seam § 4.2 asked for is measured, and it is safe.**

- In `compile_document`, intra-page links are written in the `page_section_groups` stitching loop
  (`document.py:1751-1762`). That loop also sets `section_facts = True` at `:1762`.
- No later pass removes a member:
  - The adoption loop refuses to withdraw any table in a chain longer than one
    (`if chain is not None and len(chain) > 1:` at `:1919`).
  - It also refuses any table that a document-level triple points into.
- The `/r2` re-read runs *before* stitching (the `r2_doc` loop, `:1651`), not after.
- So the derivation goes after the adoption loop and before
  `_seal(graph, _legs_for_document(...))` (`:2034`), where the tab leg validates it.
- It cannot fire with the tab leg off. A same-page link exists only where the stitching loop wrote
  one, and that loop sets `section_facts`.
- The spec's "R7 adoption" is the R73 adoption pass.

**Seam hazard for the plan:** the comment block above `_seal` (`:2016-2033`) claims the adoption
write is "immediately above this comment". Code inserted between the two must keep that true, or
re-word it to cite by symbol (CLAUDE.md plan rule 7).

**F4 — ASSERTION. Chains are linear, so a stack is a run, not a general component.**

- The stitching loop refuses to fork the successor map
  (`if cur_uri in links or prev_uri in set(links.values()): continue`, `document.py:1757`).
- Loop M pairs only page N-1 with page N.

So every table has at most one predecessor and one successor, and pages never decrease along a
chain. A same-page run is then:

- its head, a member with a same-page successor and no same-page predecessor;
- plus every table that reaches the head by `tab:continuesTable+` on the same page.

The SHACL constraint disposes of any violation of this, so the derivation need not re-prove it.
§ 4.2's "connected component" is correct, but more general than needed.

**F5 — ASSERTION. The ruled D4 edits contradict § 7.** § 7 says *"tab:04's stale R77 edge and its
R80 edge are untouched"*. The ruling says *"the same change removes tab:04's edge to the closed
R77"*. The ruling prevails. The plan reconciles its tests against § 7 as amended by the ruling
(CLAUDE.md plan rule 5). R80 stays.

**F6 — ASSERTION. D4's scope is wider than tab:01.** Seven tab statements cite `compile.py` lines,
and all seven are stale at `123301e` (`grep -n 'compile.py:[0-9]' tests/arc-manifest.ttl | grep
prog:statement`):

| Criterion | Cites | The reason's call site now |
|---|---|---|
| tab:01 | `:596` | `:1301` |
| tab:02 | `:656, :763, :939` | `:1380`, `:1617`, `:1841` |
| tab:03 | `:688` | `:1420` |
| tab:04 | `:739` | `:1486` |
| MATRIX_AMBIGUOUS | `:830` | `:1724` |
| MERGE_AMBIGUOUS | `:911` | `:1810` |
| DATAGRID_RESIDUE | `:1145` | `:2215`. `:1145` is now an unrelated `printed_total` record |

A line number into a 2,000-line module goes stale whenever anything above it is edited. The reason
literal (`"MULTI_TABLE_AMBIGUOUS"`) does not. Scope and form are Q3.

**F7 — ASSERTION. The spec does not name two generated caches and one pin that move.**

- `docs/superpowers/arc-dependency-landscape.md` is regenerated from the manifest and diffed
  (`tests/test_arc_landscape.py::test_the_tracked_landscape_is_byte_identical_to_a_fresh_regeneration`).
  Regenerate it with `./.venv/bin/python scripts/arc_depends.py`.
- `tests/test_residue_graph.py` pins the count of structural candidates at 110, as loop A last
  measured it. Closing R74 and raising new rows moves that count. R261 is open and links
  [[R74]], so its candidacy may change too.

Neither is an input of the corpus baseline.

**F8 — ASSERTION, minor. Test A reads the wrong list.** `tests/corpus-baseline/inputs.json` lists
PDF paths under `documents`, not snapshots. The neighbouring test reads `corpus_baseline.DOCUMENTS`
and maps each path to its snapshot by stem
(`tests/test_corpus_baseline.py::test_the_baseline_holds_exactly_the_listed_documents`). Test A
should do the same. It should read reasons from `pages[*].regions[*].reason`, where the snapshot
keeps them.

**F9 — PROPOSITION. Loop B may race this loop on `tests/corpus-baseline/`.** A loop-B spec (tab:05
disposal) is being written concurrently. If it touches `scripts/corpus_verdict_snapshot.py` or any
other input, both PRs carry a regenerate. Under `strict: false`, the second to merge can then pass
CI on a stale baseline (CLAUDE.md § Corpus baseline, second gap). The second loop to merge rebases
and regenerates. There is nothing to rule; it is sequencing.

**F10 — ASSERTION. Loop A does not touch this design's premises.**

- Loop A's feed now reads adopted `tab:DataGrid`s (`feed.table_records`). cbh adopts nothing
  (`"adopted": []` in its snapshot) and holds 0 `tab:DataGrid`.
- `grep -rn 'StackedGrids\|inStack' src vocab tests scripts` finds only the ontology lines and the
  docstring of the R74 pin in `tests/etkl/test_datagrid.py`. § 7's "no consumer reads
  `tab:StackedGrids`" still holds.
- Loop A's grid-index shapes target the objects and subjects of `tab:hasGridRow` and
  `tab:hasGridColumn`, which cbh does not carry.
- The R103 pin (`test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape`) covers
  `tab:DataGrid`, `tab:ColumnUniverse` and `tab:SuppressedRepeat`, not `tab:StackedGrids`. So a
  `sh:targetClass tab:StackedGrids` does not reopen R103.

### 11.3 What the implementing loop must therefore do differently

- Read a table's page from its **`tab:EntryCell`s**, not from all its cells (Q1, recommended arm).
  Do so in both the derivation and the shape, so the two close over the same notion.
- Falsify F1 on real input: pointing the query back at `tab:hasCell` (the spec's rule) must make
  the graincorp-stem O5 test fail.
- Declare `Doc impact: contradiction`, unless Q2 rules otherwise.
- Regenerate the arc landscape and re-measure the residue-candidate pin.

### 11.4 Questions for the maintainer

- **Q1 — what is a table's page?**
  - **(a) Recommended:** the one page its `tab:EntryCell`s lie on. This is evidence-positive. A
    cross-page continuation that is then section-stitched on its own page stays stackable.
  - **(b)** The page all its cells lie on, closed by a query-local `NOT EXISTS`. This is simpler,
    but a continuation table that carries head-page labels can never be stacked, even when it has
    a same-page sibling.
  - Both pass O4 and O5 on today's corpus. They differ only on a case no corpus document has.
- **Q2 — the `Doc impact` of the re-wording.** Is it `contradiction`, per R343's precedent and
  v0.0.4's content (F2)? That blocks the next release tag until it is drained. Or is a term with
  no instance in any release (M6) an exception, ruled `increment`?
- **Q3 — the scope and form of D4.**
  - (i) Correct only tab:01 and tab:04, the criteria this change edits, or all seven stale tab
    statements?
  - (ii) Replace each line number with the current line, or with the reason literal (e.g.
    `compile.py, escalate_region(…, "MULTI_TABLE_AMBIGUOUS", …)`), which does not go stale?

## Ruled 2026-10-29 by the maintainer (directly, AskUserQuestion)

- **Q1:** a table's page is the page of its **entry cells** (`tab:EntryCell`), arm (a). This
  holds in both the derivation and the shape.
- **Q2:** the `Doc impact` of the re-wording is **`contradiction`**.
- **Q3:** fix **all seven** stale tab criterion statements (tab:01, :02, :03, :04, :05, :06,
  :08), and cite the **reason string** (e.g. `"MULTI_TABLE_AMBIGUOUS"`), not a `compile.py`
  line number.
