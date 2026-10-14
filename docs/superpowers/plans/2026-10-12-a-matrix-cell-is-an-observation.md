# A matrix cell is an observation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding).

**Doc impact: increment.** Inherited from the spec: one property, one class and three individuals
in `etkl:`, one shape, one worked example under `examples/finance/`.

**Goal:** one contract that names a line item, a period and a value grounds apple's two
statements, one record per cell, and nothing else in the corpus moves.

**Architecture:** the contract declares each field's structural role (`etkl:fieldRole`).
`feed.table_records` gains a default-off keyword under which a row with a row header path mints
one record per entry cell, carrying a row key, a column key and the cell, each with its role.
`ground_concept` gains two branches ahead of `exact_field`: a role picks its field and the shipped
`_grounds_to` oracle disposes the value; a shared row label is refused by rule.
`ground_document` turns the keyword on when the contract declares a `CellValue` field.

**Tech Stack:** Python, rdflib, pySHACL/rudof through `iladub.validate` and `membrane`, pytest
(`-m corpus` for apple; the corpus never reaches CI).

**Spec:** `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md`. §§ 2–7
apply, and **§ 9 overrides any earlier sentence it contradicts.** Seams S1–S8:
`docs/superpowers/2026-10-12-matrix-cell-plan-seams-handoff.md` § 2a.

**Measured base.** `origin/main` at `94dc60c`. `git diff --stat f976a82 94dc60c -- src vocab` is
empty, so the spec's and the seams handoff's measurements hold. Code is cited by **symbol**, not
line. Re-read a symbol before writing against it.

**This plan carries no function body and no verbatim test** (CLAUDE.md § Plan authoring, rule 1).
Each task names its interface, its invariants, the seam to measure and the tests by what they
pin. Every task report carries a `## FALSIFICATION` block (rule 4); the inversion to perform is
named per task.

## Global Constraints

- **The neurosymbolic gate (CLAUDE.md § 8).** Classification is spec § 3.6 plus § 9.2's row. No
  NEURAL worker, no tuned constant, no geometry. A string comparison with a tolerance, or a regex
  in `src/` that decides a role, is a review failure.
- **Default off.** `table_records(graph)` with no keyword returns what it returns today, for all
  64 call sites (`grep -rn "table_records(" src tests scripts`, less the definition: 64).
- **Source ownership.** `etkl.ttl` stays standalone: no `w3id.org/holon` IRI, no `qb:` IRI.
- **Nothing is stored in the compiled graph** (spec § 6). The per-cell record is a reading the
  feed makes; `compile_document`'s output is byte-identical.
- **Only emit what the source supports.** A key's text is the author's labels joined by one
  space. No period is normalised, no unit is read, no row is given a path it does not have.
- **The corpus baseline is regenerated once, after the last `src/` or `vocab/` edit** (Task 5).
- **Every count pinned in a test is measured by the implementer, then compared with the
  prediction here.** A prediction that fails is reported, not adjusted to pass.

## Decisions this plan makes

The spec is silent on each. They are this plan's, recorded only here, and reversible. None is
exercised by apple (measured 2026-10-12, both `mtable2`s: `_spanning_keys` returns `()`; 180
cells, 0 with `col is None`, 0 under a column with no header path, 0 same-row pairs sharing a
column path; 0 section markers in 59 records), so **only the CI arm can pin them.**

- **D1. A table with spanning keys keeps the key split.** The per-cell branch applies only to a
  row whose owner table has no spanning key. Reason: spec § 3.3 says the two existing branches
  are unchanged, and graincorp-capacity under a role contract must not change shape silently.
- **D2. A row's non-cell concepts ride on every record minted from it.** An injected group key or
  section marker (`col is None`) is carried on each cell's record, role-less, as the key split
  already carries them onto each key's record (`table_records` pass 2).
- **D3. A cell whose column has no header path mints its record without a column key.** Its id
  must still be unique (D4).
- **D4. The pass-3 guarantee is per record, not per row.** Today pass 3 settles a residual
  collision by appending the row's IRI. Two cells of one row share that IRI, so under the keyword
  the residual must be settled by something unique to the cell.
- **D5. "Shared" is counted over every row of the logical table that has a row header path**,
  including rows that mint no record. Spec § 9.3 says "rows of one logical table". On apple both
  populations give 11 and 4 (38 covered rows per table, 31 and 28 minting).
- **D6. One rule suggester IRI for the role branch**, with the role named in the rationale. Spec
  § 3.5's "a new rule IRI naming the declared role" could also be read as one IRI per role.
- **D7. PROPOSED: the example's numeral pattern admits a leading `$ `.** 40 of apple's 180 cells
  carry it inside the cell text (S8). The value is carried as printed (spec § 2.1 applies the
  same rule to the period). The alternative quarantines the first row of every block for the
  author's typography. The count is stated beside P4 either way.

## Review Focus

Inputs the spec implies and apple does not exercise. Each is pinned by a named test below.

1. **Two cells of one row under equal column paths** (or with no column path): two records, two
   subjects. Task 2, `test_two_cells_of_one_row_never_share_an_id`.
2. **Two distinct record ids that slug to one `_record_uri`.** `_record_uri` maps every run of
   non-alphanumerics to `_`, and a per-cell id is long and punctuated. One subject would then
   carry two values for one property. Task 4 pins 180 distinct subjects on apple; Task 2 pins it
   on the synthetic matrix.
3. **A contract with two fields of one role, or a role that is not one of the three
   individuals.** Nothing validates a contract at load today (`grep -rn etkl-shapes src` is
   empty; only tests read that file). Task 1, `test_load_contract_refuses_what_the_shape_refuses`.
4. **A proposer that answers for a shared row label.** Spec § 9.2. Task 3,
   `test_a_shared_row_key_is_refused_whatever_the_proposer_says`.
5. **A role contract over a document whose tables have no row header path** (graincorp, a
   `tab:RecordTable`): every row keeps today's row record, and the cells reach the portal with
   no role. Task 2, `test_a_row_without_a_row_header_path_keeps_its_row_record`.

---

### Task 1: The role vocabulary, its shape, and the contract in memory

**Files:**
- Modify: `vocab/ontology/etkl.ttl` (beside `etkl:Field`, `etkl:hasField`)
- Modify: `vocab/shapes/etkl-shapes.ttl` (beside `etkl:FieldShape`)
- Modify: `src/iladub/ground.py` (`SurfaceConcept`, `ContractField`, `load_contract`)
- Create: `tests/test_contract_roles.py`, one negative fixture `.ttl` for the shape

**Interfaces (produces):**
- `etkl:FieldRole` (class), `etkl:fieldRole` (object property, domain `etkl:Field`, range
  `etkl:FieldRole`), `etkl:RowKey`, `etkl:ColumnKey`, `etkl:CellValue` (individuals). Each typed,
  labelled and commented as its neighbours are.
- A contract-role shape targeting `etkl:SemanticDataContract`: a contract with any role-carrying
  field has exactly one `CellValue` field and at most one field per key role; a field has at most
  one `etkl:fieldRole`, and its value is one of the three individuals.
- `ground.ROLE_ROW_KEY`, `ROLE_COLUMN_KEY`, `ROLE_CELL_VALUE`: the three individuals' IRIs as
  `str`. `ground.SHARED_ROW_KEY`: a `str` equal to none of them.
- `ContractField.role: str | None = None` (fourth field). `SurfaceConcept.role: str | None = None`
  (after `is_split_key`, with a comment in the form of the two above it).
- `load_contract` reads `etkl:fieldRole` into `ContractField.role` and refuses, with an error
  naming the contract path, a contract the role shape refuses.

**Invariants:**
- Every existing three-argument `ContractField(...)` and `SurfaceConcept(...)` site is untouched
  and still compares equal by value (`grep -rn "ContractField(" src tests scripts`: 1 in `src`,
  6 in `tests`, 1 in `scripts`; none passes a role).
- `load_contract` never returns a `ContractField` whose role is `SHARED_ROW_KEY`.
- The refusal at load is the shape's verdict, not a Python recount of it (gate: constraint is
  SHACL). `load_contract` on the three shipped `examples/shipping/*-contract.ttl` returns what
  it returns today, with `role is None` on every field.

**Seams to measure before writing:**
- What validating a contract at load costs. `load_contract` is called per corpus test; run the
  shape once per call and time `tests/test_stem_contract.py` before and after. If the cost is
  visible, say so in the report; do not replace the shape with Python.
- `tests/test_vocab_shapes.py` and `tests/test_federation.py` validate examples against
  `etkl-shapes.ttl`. A new shape on `etkl:SemanticDataContract` must leave them conforming:
  run both files.
- `tests/test_artifact_terms.py` and `tests/test_artifact_declarations.py` pin populations as
  numbers (`== 181`, `== 72`, `== 67`, `== 21`; `git ls-files "*.ttl" | wc -l` is 183 today).
  A new tracked `.ttl` and five new `etkl:` terms may move them. Where the negative fixture
  lives decides whether it joins the population (`FIXTURE_DIR` is carved out). Run both files;
  re-measure any pin that moves and extend its comment as the earlier re-measurements do.

**Tests (`tests/test_contract_roles.py`), by what each pins:**
- `test_a_role_contract_conforms`: a three-field contract built in the test conforms.
- `test_two_cell_value_fields_are_refused`: the negative fixture fails on the role shape.
- `test_a_field_with_two_roles_is_refused`, `test_an_unknown_role_is_refused`.
- `test_a_contract_with_no_role_is_untouched`: `examples/shipping/capacity-contract.ttl`
  conforms and loads with `role is None` on all four fields.
- `test_load_contract_reads_the_role`: three roles land on three `ContractField`s.
- `test_load_contract_refuses_what_the_shape_refuses` (Review Focus 3).

**Falsification:** delete the `CellValue` cardinality from the shape and show
`test_two_cell_value_fields_are_refused` and `test_load_contract_refuses_what_the_shape_refuses`
fail; restore.

- [ ] Measure the three seams; record the outputs in the task report
- [ ] Write the tests; run `pytest tests/test_contract_roles.py`; see them fail
- [ ] Add the vocabulary, the shape, the fields and the load
- [ ] Run `tests/test_contract_roles.py`, `test_vocab_shapes.py`, `test_federation.py`,
      `test_artifact_terms.py`, `test_artifact_declarations.py`, `test_stem_contract.py`,
      `test_source_ownership.py`, each in its own process
- [ ] Falsify, restore, commit

---

### Task 2: The feed reads one record per cell

**Files:**
- Modify: `src/iladub/feed.py` (`table_records`; `_read_table` and `_header_path` as the seams
  below require)
- Create: `tests/test_feed_matrix_cell.py`

**Interfaces:**
- Consumes: `SurfaceConcept.role`, `ROLE_*`, `SHARED_ROW_KEY` (Task 1).
- Produces: `table_records(graph, *, per_cell: bool = False) -> list[Record]`.

**The reading, under `per_cell=True`** (spec § 3.3, § 9.1, § 9.3; D1–D5). A row that has a row
header path, whose owner table has no spanning key, mints one `Record` per entry cell:

| concept | `text` and `value` | `region` | `role` |
| --- | --- | --- | --- |
| row key | the row's header-path labels, root to leaf, joined by one space | spec § 9.1 | `ROLE_ROW_KEY`, or `SHARED_ROW_KEY` when the path is shared (§ 9.3, D5) |
| column key (absent under D3) | the column's header-path labels, joined by one space | spec § 9.1 | `ROLE_COLUMN_KEY` |
| cell | `text=""`, `value` = the cell's text | the cell's region, as `_read_table` reads it today | `ROLE_CELL_VALUE` |

Record id: the row's id as passes 1–2 compute it today, then ` > `, then the column's ` > `-joined
path. Every other row keeps its existing branch.

**Invariants:**
- I1. With `per_cell=False`, the function's result is unchanged. Not argued: the existing suite
  is the oracle, and no existing test is edited in this task.
- I2. No two records of one call share a `row_id`, and no two share `_record_uri(row_id)`.
- I3. Spec § 9.1's invariant on key regions, verbatim.
- I4. A key's `text` contains no ` > ` that the feed inserted. A label that itself contains
  ` > ` keeps it.
- I5. The gate: this branch decides nothing. Which cells are entries, which header covers them
  and what the paths are were asserted at compile. A `PROCEDURAL` comment at the branch says so
  and says why it is irreducible (spec § 3.6, last row).

**Seams to measure before writing:**
- `_header_path` returns one ` > `-joined string per target and discards the deepest header
  node. § 3.3 needs the labels as a sequence (I4: replacing ` > ` in the joined string is lossy
  when a label contains it) and § 9.1 needs the deepest node's label cell. Decide how both
  reach `table_records` without changing what `_column_header_path`, `_row_header_path` and
  `_logical_row_paths` return to their other callers. **MEASURE the callers first**
  (`grep -n "_header_path\|_logical_row_paths" src/iladub/*.py src/iladub/etkl/*.py`).
- The deepest node is chosen by `_header_path`'s tie-break. The key's region must come from the
  node that selection chose, not from a second selection.
- `_read_table` carries `(x0, y0, concept, col)` per cell and drops the cell's IRI. D4 needs
  something unique per cell. MEASURE whether the cell's region is unique per cell in general
  (it falls back to the cell's IRI fragment when `prov:wasDerivedFrom` is absent, and that
  fragment collides across pages per [[R309]]'s mechanism) before choosing it.
- § 9.1: on apple a label cell's `tab:onPage` is an `xsd:integer` literal (0 and 1) and its
  fragment has the form `mtable2-chl0`; an entry region has the form `p0-305-143`. MEASURE a
  label cell with no `tab:onPage` on a synthetic graph and state what the region is then.
- `ordered` holds only rows that mint. D5's population is `_logical_row_paths`' whole result.

**Tests (`tests/test_feed_matrix_cell.py`).** Graphs are built in the test, as
`tests/test_feed_chain_walk.py` builds `tab:coversRow` groups and `tests/test_feed_key_split.py`
builds header nodes (`_table`). **Construct each setup and print its default-mode records before
asserting anything** (rule 5): a setup the reader does not see as a matrix proves nothing.
- `test_a_2x2_matrix_mints_four_records_of_three_concepts`: texts, values, roles; key text
  space-joined over a two-level column tree.
- `test_default_mode_is_untouched`: the same graph, no keyword, equals the row reading.
- `test_a_repeated_row_label_carries_the_shared_role`: both rows' keys are `SHARED_ROW_KEY`;
  their column keys and cells keep their roles.
- `test_a_label_unique_in_each_of_two_tables_keeps_its_role` (spec § 9.3's unconstructed case).
- `test_a_label_shared_with_a_row_that_mints_nothing_is_shared` (D5).
- `test_a_chain_is_one_logical_table_for_the_count`: the label on the head and on its
  continuation is shared.
- `test_two_cells_of_one_row_never_share_an_id` (D3, D4; Review Focus 1): two columns with equal
  header paths, and one with none.
- `test_no_two_records_share_a_subject` (I2 on `_record_uri`; Review Focus 2).
- `test_key_regions_are_page_qualified_and_disjoint_from_cell_regions` (I3): the same label-cell
  fragment on two pages gives two regions.
- `test_a_row_without_a_row_header_path_keeps_its_row_record` (Review Focus 5).
- `test_a_table_with_spanning_keys_keeps_the_key_split` (D1).
- `test_an_injected_concept_rides_on_every_cell_record` (D2).
- `test_an_aggregation_row_mints_nothing`, `test_a_blank_cell_mints_nothing`: both are
  `_read_table`'s today; pinned here because a per-cell loop is where they would be lost.

**The corpus prediction (P1, and § 9's oracles), run at the end of this task, before Task 3:**
`table_records(apple, per_cell=True)` gives 180 records and 540 concepts; 52 row keys carry
`SHARED_ROW_KEY` (44 on p0, 8 on p1) and 128 carry `ROLE_ROW_KEY`; 180 distinct `row_id`s and 180
distinct `_record_uri`s; at most 59 distinct row-key regions and exactly 6 column-key regions;
no key region equals any of the 180 cell regions; the six column-key texts are the six paths
with spaces (`Three Months Ended June 27, 2026`, …, `September 27, 2025`). **PROPOSED, all of
it.** If any count differs, stop and report before Task 3.

**Falsification:** (a) make the shared test use the document-wide `multiplicity` and show
`test_a_label_unique_in_each_of_two_tables_keeps_its_role` fail; (b) drop the page from the key
region and show the I3 test fail; (c) settle the residual by row IRI and show Review Focus 1's
test fail. Restore each.

- [ ] Measure the seams; record outputs
- [ ] Build and print the synthetic setups; write the tests; see them fail
- [ ] Implement
- [ ] Run `tests/test_feed_matrix_cell.py`, then every `tests/test_feed*.py` and
      `tests/test_cbh_e2e.py`, `tests/test_stem_contract.py`, one file per process
- [ ] Run the corpus prediction on apple; record the counts beside the predictions
- [ ] Falsify (a), (b), (c); restore; commit

---

### Task 3: Grounding by role, and the refusal by rule

**Files:**
- Modify: `src/iladub/ground.py` (`ground_concept`, two rule IRIs)
- Create: `tests/test_ground_field_role.py`

**Interfaces:**
- Consumes: `ContractField.role`, `SurfaceConcept.role`, `SHARED_ROW_KEY` (Task 1).
- Produces: `_DECLARED_ROLE_RULE` and `_SHARED_ROW_LABEL_RULE`, two `urn:iladub:suggester/…-rule`
  IRIs in the form of the three beside them. `ground_concept`'s signature is unchanged.

**The branches, in this order, ahead of `exact_field`:**
1. `concept.role == SHARED_ROW_KEY`: emit the candidate under `_SHARED_ROW_LABEL_RULE` and return
   `"proposed"`. No proposer call, no `_admissible_fields` call, no decision holon (spec § 9.2).
2. `concept.role` is set and the contract has a field of that role: that field, with the
   suggester `_DECLARED_ROLE_RULE`, confidence 1.0, a rationale naming the role and saying no
   proposer was asked, then disposed by `_grounds_to` **as an exact match is** (spec § 3.5).
3. Otherwise the four existing branches, unchanged.

**Invariants:**
- A concept with `role is None` takes exactly the path it takes today. No existing grounding
  test is edited.
- The role picks the field; it never admits the value. A `RowKey` value outside the scheme and a
  `CellValue` the pattern refuses both return `"proposed"`, with a candidate and no decision.
- A role-grounded node satisfies the grounding membrane (`feed._validate_grounding`): one
  promotion decision, two options, `dec:rejectedBecause` on the option not taken.
- Each new branch carries its gate classification in a comment: AXIOM, and for branch 1 the
  reason no worker exists (the scheme admits the label and that admission is the defect).

**Seams to measure before writing:**
- `_grounds_to(…, is_exact=True)` on a field with no scheme and **no** value constraint grounds
  by field identity. A `CellValue` field declared without a pattern would therefore ground every
  cell. State in the report whether that is acceptable for a role field or whether the role
  shape of Task 1 should require a constraint; do not decide it silently. This plan's reading:
  it is the contract author's choice, as for any exact match today.
- `ground_concept` appends "[grounded via SHACL value-constraint admissibility, weaker than
  scheme-identity]" to the rationale only when `not is_exact`. Under branch 2 a pattern-admitted
  period is `is_exact`. Confirm the recorded rationale and `dec:rejectedBecause` read truthfully
  for a role-picked, pattern-admitted value.
- `_emit_candidate` writes `rdfs:label` from `concept.text`, which is `""` for a cell. The key
  split already produces such candidates; confirm the membrane conforms on one.

**Tests (`tests/test_ground_field_role.py`), contract and terms built in the test:**
- `test_a_row_key_grounds_to_its_scheme_concept`, `test_a_row_key_outside_the_scheme_is_quarantined`.
- `test_a_column_key_grounds_when_the_pattern_admits_it`, `…_is_quarantined_when_it_does_not`.
- `test_a_cell_value_grounds_under_the_value_field_with_an_empty_text`.
- `test_the_role_wins_over_an_exact_name_match`: a row key whose text normalises to another
  field's name still takes the `RowKey` field.
- `test_a_role_with_no_field_of_that_role_falls_through`.
- `test_a_shared_row_key_is_refused_whatever_the_proposer_says` (Review Focus 4): the label is in
  the scheme and a `FakeGroundingProposer` names the row-key field; the result is `"proposed"`,
  the candidate's suggester is `_SHARED_ROW_LABEL_RULE`, the graph holds no
  `iladub:PromotionDecision`, and the proposer was not called (a proposer that raises).
- `test_a_role_grounded_graph_conforms_to_the_membrane`.
- `test_no_proposer_is_asked_for_a_role_concept`.

**Falsification:** delete branch 1 and show the Review Focus 4 test fail by *grounding* (spec
§ 9.2's stated falsifier, S2's measurement). Delete branch 2 and show the row-key test fail.
Restore each.

- [ ] Measure the seams; record outputs
- [ ] Write the tests; see them fail
- [ ] Implement
- [ ] Run `tests/test_ground_field_role.py`, `tests/test_grounding.py`,
      `tests/test_ground_section_marker.py`, `tests/test_feed_key_split.py`,
      `tests/test_stem_contract.py`, `tests/test_cbh_contract.py`, one file per process
- [ ] Falsify both; restore; commit

---

### Task 4: The worked example, the switch, and apple

**Files:**
- Create: `examples/finance/statement-contract.ttl`, `statement-terms.ttl`, `statement-shapes.ttl`
- Modify: `src/iladub/feed.py` (`ground_document`)
- Modify: `tests/corpus-manifest.ttl` (apple's entry: `cor:contract`, `cor:terms`, `cor:shapes`)
- Create: `tests/test_finance_contract.py` (CI), `tests/test_corpus_apple_contract.py` (`corpus`)

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: `ground_document` calls `table_records(graph, per_cell=True)` exactly when a field of
  the contract has `role == ROLE_CELL_VALUE`. Its signature and return type are unchanged.
- The example (spec § 4): `fin:lineItem` (`RowKey`, bound to `fin:scheme-line-item`),
  `fin:period` (`ColumnKey`, `sh:pattern`), `fin:value` (`CellValue`, `sh:pattern`). Illustrative,
  synthetic, CC-BY header and author metadata as `examples/shipping/capacity-contract.ttl` carries.

**Invariants:**
- The scheme holds generic statement lines and **includes `Total net sales`**, which is shared on
  apple (×2 on p0). Without a shared label in the scheme the corpus arm of § 9.2 cannot fail.
- The scheme is short on purpose: some unshared apple lines are absent from it and quarantine.
- The period pattern admits apple's six printed paths and refuses a line-item label. The numeral
  pattern admits apple's seven digit shapes (S8) under D7 and refuses `Y`, a blank, and a word.
  Both are written against the text **as the feed delivers it** (Task 2's recorded outputs).
- No file under `examples/finance/` names Apple or copies its figures.

**Seams to measure before writing:**
- List apple's 128 unshared row-key texts (distinct) from Task 2's run, then choose the scheme.
  State in the report which labels were chosen and how many of the 128 concepts they cover.
- `tests/test_artifact_terms.py` again: three more tracked `.ttl` files, with `fin:` terms.
  Re-measure any pin that moves.
- `test_grounding_where_contracted` parametrises on entries that carry `cor:contract`. Confirm
  apple joins it and that its abstaining proposer is never asked (a role contract leaves nothing
  for it only if every concept has a role; D2 concepts would reach it).

**Tests:**
- `tests/test_finance_contract.py` (CI): the contract loads with three roles and conforms to the
  role shape; each pattern admits and refuses the listed strings through `_value_conforms`; a
  synthetic 2×2 matrix with one repeated row label goes through `ground_document` with
  `validate_shapes=True` and gives the counts the test derives in a comment (spec § 5's CI arm);
  a contract with no role sends the same graph through the row reading
  (`test_a_roleless_contract_does_not_turn_the_keyword_on`).
- `tests/test_corpus_apple_contract.py` (`corpus`), predictions **PROPOSED**:
  - P1: records 180; `grounded + proposed == 540`.
  - P2: 180 `fin:period` values grounded.
  - P3 (§ 9.2 form): under a proposer that names `fin:lineItem`'s field, 0 of the 52 shared row
    keys ground, and no subject carries two `fin:lineItem` values.
  - P4: grounded `fin:value` count, predicted 180 under D7; any refused text is listed in the
    assertion message.
  - P6: `validate_shapes=True` conforms.
  - 180 distinct record subjects (Review Focus 2).
  - Row keys grounded: the number the scheme choice implies, derived in a comment from the list
    above, not copied from the run.

**Falsification:** (a) force the switch off and show P1 fail at 59; (b) on the corpus arm, delete
Task 3's branch 1 and show P3 fail with `Total net sales` grounded on two subjects per period;
(c) remove `September` from the period pattern and show P2 fail by exactly 28, the cells of
p1's second column (spec § 5 P2's stated signature). Restore each.

- [ ] Measure the seams; record outputs
- [ ] Write the example files and both test files; see the tests fail
- [ ] Implement the switch; add the manifest triples
- [ ] Run `tests/test_finance_contract.py`, `test_artifact_terms.py`,
      `test_artifact_declarations.py`; then, serially, `-m corpus`
      `tests/test_corpus_apple_contract.py` and
      `tests/test_corpus.py -k "grounding_where_contracted"` (four documents now)
- [ ] Falsify (a), (b), (c); restore; commit

---

### Task 5: Nothing else moves, and the record

**Files:**
- Modify: `tests/corpus-baseline/` (regenerated), `docs/superpowers/residues-open.md` and
  `residues.md` only if a row's evidence changed
- Create: the loop's handoff under `docs/superpowers/`

**Steps and their oracles:**
- [ ] `git add` every new input file, then
      `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` (one serial pass,
      about 24 minutes; edit no input while it runs).
- [ ] **P5, PROPOSED:** `git diff --stat -- tests/corpus-baseline/` shows `inputs.json` and
      nothing else. The baseline's keys carry no grounding (S5), and no compile path changed. Any
      snapshot that moves is a defect in Tasks 1–4, not a diff to commit.
- [ ] The full suite, chunked as the repo runs it (about eight files per process), and
      `-m corpus` serially. Report failures with their output.
- [ ] [[R308]] and [[R309]] stay open. Append to each the measurement this loop adds (R308: the
      refusal now exists and what it quarantines; R309: the feed no longer uses the colliding
      fragment for a role key, `_spanning_keys` still does). Neither is struck.
- [ ] Write the handoff, part 5 first and typed. It records D1–D7 as decisions held only in this
      plan, and what Task 3's first seam concluded.
- [ ] Open the PR. Merge only on a green `test`.

## What this plan does not do

Spec § 6, unchanged. In addition: `_spanning_keys`' fragment fallback is not repaired (§ 9.1);
no role is added to graincorp's, cbh's or the stem's contract; who-wfa is not contracted (S7).

## Unverified or assumed

- **No per-cell reading has been run.** Every count in Tasks 2 and 4 is a prediction from counts
  of the row reading (P1 from M1, 52 from M4).
- **D1–D6 rest on no corpus document.** Apple exercises none of them.
- **The cost of validating a contract at load** (Task 1) is unmeasured.
- **Whether `tests/test_feed_chain_walk.py`'s construction yields a table `_logical_row_paths`
  reads as a flat row tree with one header per row** was read, not run. Task 2 builds and prints
  the setup before asserting for that reason.
- **That apple's six column-key texts carry single spaces** is inferred from S6 (three header
  nodes per path, no double space in a row label); column labels were not checked for one.
