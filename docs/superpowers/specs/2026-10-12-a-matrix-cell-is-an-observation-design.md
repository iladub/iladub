# Spec: a matrix cell is an observation — the contract declares roles, the feed reads one record per cell

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding), picked
by the maintainer on 2026-10-12. Follows `docs/superpowers/2026-10-12-contracts-candidate-measured-handoff.md` § 5.

**Date:** 2026-10-12. **Branch:** `contracts-candidate-measured`, on `main` at `f976a82`.

**Doc impact: increment.** Adds one property, one class and three individuals to `etkl:`, one
shape, and a worked example under `examples/finance/`. No existing term changes meaning.

**Global Constraint: the neurosymbolic gate (CLAUDE.md § 8).** Every decision this spec adds is
classified in § 3.6. No NEURAL worker is added and no tuned constant appears.

**Authored at about 62K working tokens, over the 50K originating floor** (override logged). The
two design forks were ruled by the maintainer before drafting (§ 2); everything else in § 3 is this
session's and is graded in § 8.

---

## 0. The concern, first

A contract for apple's income statement can ground today only if it declares one property per
printed period. That is a contract for one edition of one filing. **This spec lets one contract
name a line item, a period and a value, and survive the next quarter's filing.** It does so
without naming anything from page furniture, so it neither builds nor depends on [[R250]].

## 1. What was measured

All on `f976a82`, `compile_document("corpus/financial/apple-fy2026q3-statements.pdf")`, score
0.9419. Scripts are throwaway and were not committed; the commands are the bodies quoted in the
session, and each number below is reproducible from the named function.

| # | claim | measurement |
| --- | --- | --- |
| M1 | The handoff's § 5.1 prediction holds: grounding works, the record shape is the gap | A generated contract with six fields, one per distinct column header path, under the abstaining proposer and `validate_shapes=True`: `FeedResult(records=59, grounded=180, proposed=0)`. 31 records × 4 paths + 28 × 2 = 180 |
| M2 | apple's records come from two tables, both `tab:HierarchicalTable` | `p0#mtable2` (31 records) and `p1#mtable2` (28). One `tab:DataGrid` (p2) contributes none |
| M3 | Every record's row has a row header path, and the row tree is flat | `feed._row_header_path`: 38 covered rows per table, 0 paths containing ` > ` |
| M4 | A row label does not identify its row | Shared paths: p0 `Products`×2, `Services`×3, `Total net sales`×2, `Basic`×2, `Diluted`×2; p1 `Marketable securities`×2, `Term debt`×2. 15 of 59 records, 52 of 180 cells |
| M5 | Every cell has its own provenance region and a non-empty value | 180 distinct `region`s over 180 concepts; 0 empty values |
| M6 | The shipped unpivot cannot supply the record | `reshape.certify` on both tables: every recovered dimension has `name=None`, so no `UnpivotOp`; 0 `tab:BaseFact`; verdict `ok=True` on an empty base. Same class as [[R214]] |
| M7 | The default record shape has 64 call sites | `grep -rn "table_records(" src tests scripts`, less the definition |

M4 is the finding the handoff did not have. `Products` under *Net sales* and `Products` under
*Cost of sales* are two rows with one label, because the section captions are not parents in the
row tree.

## 2. What the maintainer ruled, 2026-10-12, in session

Recorded here and nowhere else.

1. **An open-valued key is admitted by a SHACL value constraint.** A reporting period is not a
   member of any scheme that outlives an edition. The key is carried as printed; it is not
   normalised to a date.
2. **The contract declares each field's structural role.** Role picks the field. The scheme or
   value constraint stays the oracle that admits or quarantines the value. Rejected: unique
   admission by value alone (a period pattern and a numeral pattern can both admit `2026`), and
   building [[R250]] first (one firing document, and apple's matrix mixes dollar amounts,
   per-share figures and share counts, so no single derived measure name is true of every cell).

## 3. Design

### 3.1 Vocabulary (`vocab/ontology/etkl.ttl`, owned)

- `etkl:FieldRole` — a class.
- `etkl:fieldRole` — object property, domain `etkl:Field`, range `etkl:FieldRole`.
- `etkl:RowKey`, `etkl:ColumnKey`, `etkl:CellValue` — the three individuals.

A field with no `etkl:fieldRole` means what it means today. `etkl.ttl` stays standalone: the
alignment to `qb:DimensionProperty` / `qb:MeasureProperty`, if wanted, goes in an align module
and is not part of this loop.

**Contract shape** (closed world, `vocab/shapes/`): a contract that declares any role declares
exactly one `etkl:CellValue` field and at most one field per key role, and a field carries at most
one role. Ships with a conforming example (§ 4) and a negative that must fail (two `CellValue`
fields).

### 3.2 The contract in memory

`ground.ContractField` gains `role: str | None = None`, read by `load_contract` from
`etkl:fieldRole`. Defaulted, so every existing construction site is untouched.

### 3.3 The feed: one record per cell

`feed.table_records` gains a keyword, default off, under which the two existing branches are
unchanged and a third applies **per row**:

> A row that has a row header path, in a table whose columns have column header paths, mints one
> `Record` per entry cell instead of one per row.

Each such record carries up to three concepts:

| concept | `text` and `value` | `region` | role |
| --- | --- | --- | --- |
| row key | the row's header path labels, root to leaf, joined by one space | the row header's label cell | `RowKey` |
| column key | the column's header path labels, root to leaf, joined by one space | the deepest column header's label cell | `ColumnKey` |
| cell | `text=""`, `value` = the cell's text | the cell's own region, as today | `CellValue` |

- **Joined by a space, not ` > `.** ` > ` is the feed's separator, not the author's ink, and a
  contract's value constraint must be writable against what the page says
  (`Three Months Ended June 27, 2026`). `row_id` keeps ` > `, as every id does.
- **The role is a new defaulted field on `SurfaceConcept`**, a sibling of `is_split_key` and not
  a widening of it. The reason is the one recorded at `ground.py` beside `is_split_key`: an
  existing pin keeps meaning what it meant.
- **The record id** is the row's existing id with the column key appended, then the existing
  pass-3 guarantee. No two cells may mint one subject.
- **A row with no row header path** is not given one. It keeps today's row record.
- **`ground_document` turns the keyword on** exactly when the contract declares a `CellValue`
  field. graincorp's contract declares no role and reads as it does today.

### 3.4 A shared row label is not a key (M4)

A row whose header path is shared by another row of the same logical table mints its row-key
concept **with no role**. It then reaches the portal as an ordinary unplaceable concept and is
quarantined as a candidate: carried, never dropped, never grounded.

Why not ground it: two observations would carry the same line item and the same period with
different values, and nothing in the grounded graph would say they are different lines. The label
is the author's; the identity is not. The record's column key and value still ground. The count
is a closed-world guard scoped to one logical table, which is the holon (§ 8 of CLAUDE.md), and it
reuses the multiplicity `table_records` already computes for ids.

Recorded as [[R308]]: what would make these rows keys is a row tree that reads the section
captions as parents. That is a reading change and not this loop's.

### 3.5 Grounding by role

`ground_concept` gains one branch, tried first: a concept with a role, in a contract with a field
of that role, takes that field. It is then disposed by `_grounds_to` exactly as an exact match is:
scheme membership for a scheme-bound field, the SHACL value constraint where one is declared,
field identity otherwise. The suggester is a new rule IRI naming the declared role, and the
rationale says the contract declared it and no proposer was asked.

A concept with a role and no field of that role falls through to the existing branches unchanged.

### 3.6 The gate

| decision | class | why |
| --- | --- | --- |
| which field a keyed concept belongs to | **AXIOM** | declared in the contract; read, not inferred |
| whether a value may ground | **AXIOM, closed world** | the shipped `_grounds_to` oracles, unchanged |
| a contract's roles are well-formed | **AXIOM, closed world** | SHACL shape, § 3.1 |
| a shared row label is not a key | **AXIOM**, holon-scoped count | § 3.4; no tolerance, equality of strings within one table |
| one record per cell | **PROCEDURAL** | a reading of RDF already in the graph into the feed's in-memory `Record`, the same class as the shipped key split (`feed.py`, [[R211]] Layer B). It decides nothing: which cells are entries, which headers cover them and what the paths are were all asserted at compile |

## 4. The worked example

`examples/finance/statement-{contract,terms,shapes}.ttl`, illustrative and authored here:

- `fin:lineItem` — `RowKey`, scheme-bound to a small `fin:scheme-line-item` whose `prefLabel`s
  are generic statement lines (`Gross margin`, `Operating income`, `Net income`, `Total assets`, …).
- `fin:period` — `ColumnKey`, with an `sh:pattern` for a printed period.
- `fin:value` — `CellValue`, with an `sh:pattern` for a printed numeral.

The scheme is deliberately short. Line items it does not carry quarantine, so the example shows
both halves of assert/propose on one document. apple gains the contract in
`tests/corpus-manifest.ttl`, which puts it under `test_grounding_where_contracted`.

## 5. Oracles and predictions

Run before anything is built on them. All are counts on apple under the abstaining proposer.

- **P1, identity.** Records = 180. Concepts = 540. `grounded + proposed = 540`.
- **P2, the column key.** 180 grounded iff the period pattern admits all six header paths. A
  pattern that admits 5 of 6 shows as exactly 31 or 28 missing.
- **P3, the shared label.** Exactly 52 row-key concepts carry no role, and none of those 52
  grounds (M4). Falsified by removing § 3.4: with `Products` in the scheme, two subjects ground
  `fin:lineItem` to one concept under one period.
- **P4, the value.** Grounded values = the cells whose text the numeral pattern admits; the
  remainder is listed by text, not summarised.
- **P5, nothing else moves.** The 64 default call sites return what they returned; the corpus
  baseline diff is empty for the ten documents with no role-declaring contract. Whether the
  baseline records grounding at all is a seam for the plan to measure.
- **P6, the membrane.** `validate_shapes=True` conforms: every grounded node is behind one
  promotion decision.

A CI arm is needed beside the corpus arm, because the corpus never reaches CI: a synthetic 2×2
matrix with one repeated row label, built in the test.

## 6. What is NOT done

- **No measure name, no unit.** `(In millions, except …)` is furniture; reading it is [[R250]]'s
  class. `fin:value` is the printed numeral and the line item says what it measures.
- **No period normalisation.** The period is its printed text (§ 2.1).
- **No `tab:DataGrid`.** apple's p2 cash-flow grid (87 cells) contributes no record, as today.
- **No change to the row tree.** The 15 shared-label rows stay partly quarantined ([[R308]]).
- **No `tab:BaseFact`.** The observation is a reading the feed makes for the portal. Nothing new
  is stored in the compiled graph (M6 is why the stored route is not used).
- **No record for a refusing concept beyond what exists.** A quarantined concept gets a
  candidate and no decision holon, as today.
- **No second document.** who-wfa, bfs and ons are not contracted here.

## 7. Residues

- **Raised: [[R308]]** — a row label does not identify its row on apple (M4).
- **Cited, not amended: [[R214]]** — M6 is a second instance of the vacuous unpivot verdict.
  Also seen and not chased: on `p1#mtable2`, `recover_recipe` returns a `max` strip over 37 rows
  onto `mtable2-r15`.
- **Untouched: [[R250]]**, [[R166]] (`respectively` as a row on p1 is one of the 28).

## 8. Unverified or assumed

- **§ 3.3's region for a key is assumed to exist.** That a row header's and a column header's
  label cell both carry a provenance region the feed can read was not measured. `_spanning_keys`
  returns one for split keys; whether the same read serves a row header is the first thing the
  plan measures.
- **§ 3.4 is this session's decision, not a ruling.** Quarantining only the row key, and not the
  whole record, is recorded only here and is reversible.
- **Space-joined key text is this session's decision.** A header label that wraps across lines
  may already be joined some other way upstream; not measured.
- **The patterns in § 4 are not written.** P2 and P4 are stated against patterns that do not
  exist yet, so their counts are open by construction.
- **Other role-shaped documents were not looked at.** The design is argued from apple and from
  graincorp's precedent. Whether who-wfa's 19 well-labelled records have row header paths was
  not measured.
- **`src/iladub/contract.py` was not opened.** If it also loads contracts, § 3.2 has a second site.

## 9. Seams ruled before the plan (appended 2026-10-12)

Measured in `docs/superpowers/2026-10-12-matrix-cell-plan-seams-handoff.md` § 2a (S1–S8). The
maintainer ruled the three recommendations of its § 5 in session on 2026-10-12 with "go ahead".
Recorded here and nowhere else. **This section overrides any earlier sentence it contradicts.**
It was written at about 67K working tokens, over the originating floor (override logged); the
wording of each rule below is this session's and is graded where it goes beyond the ruling.

### 9.1 A key's region is its label cell, named by page (overrides § 3.3's region column, closes § 8 item 1)

No header label cell carries `prov:wasDerivedFrom` (S1), so there is no region to read. A row key's
and a column key's `region` names the label cell itself: the cell's `tab:onPage` value and the
cell's own IRI fragment. Both are RDF reads. The compile-side fact is raised as [[R309]] and is
not repaired here.

- **Invariant:** no two key concepts of one document that come from different label cells carry
  the same `region`, and no key concept's `region` equals an entry cell's.
- **Oracle on apple:** the distinct key regions number 59 row-side at most and 6 column-side, and
  none of the 42 cross-page fragment collisions survives.
- **Graded, this session's:** the exact string that joins page and fragment is not ruled. The
  plan names the seam (what `tab:onPage` holds on a label cell, measured against the page) and
  the implementer chooses a form the invariant holds for.
- **`_spanning_keys` is not changed.** Its fallback has the same defect on a multi-page document;
  that is [[R309]]'s, and graincorp-capacity is one page.

### 9.2 A shared row label is refused by rule (overrides § 3.4's "with no role")

A role-less concept reaches the proposer, and a proposer that names the line-item field gets it
grounded by scheme membership (S2). So:

- The role field on `SurfaceConcept` takes a value for a shared row key that **no contract can
  declare**: it is not an `etkl:FieldRole` individual and `load_contract` never produces it.
- `ground_concept` gains a second branch, beside § 3.5's and tried before `exact_field`: such a
  concept is emitted as a candidate under a new rule suggester IRI and returns `proposed`. No
  proposer is asked and `_admissible_fields` is not consulted.
- **Gate (§ 3.6 gains a row):** AXIOM. Nothing can dispose a proposal here, because the scheme
  admits the label and that admission is the defect. No oracle, no worker.
- **P3 is restated:** exactly 52 row-key concepts carry the shared value, and none grounds
  **under a proposer that names the row-key field**, with the label in the scheme. The
  abstaining arm proves nothing (S2) and is not the test. Falsified by deleting the branch: the
  concept grounds.
- As § 6 already says, the refused concept gets a candidate and no decision holon.

### 9.3 The shared-label count is per logical table, over the row header path (overrides § 3.4's reuse clause)

"Shared" means: two or more rows of one logical table (a head and its `tab:continuesTable` chain)
have equal row header paths. The clause "reuses the multiplicity `table_records` already
computes" is withdrawn: that count spans every table of the document and is keyed on the row id,
which carries the section-caption prefix (S3). Record ids keep using it, unchanged.

- **Oracle on apple:** 11 rows on p0 and 4 on p1, as M4.
- **Not constructed:** a document where the two scopes differ. The CI arm of § 5 carries it: two
  tables, one label unique in each and present in both, and both row keys keep their role.

### 9.4 What § 8 still leaves open

Items 2 to 4 of § 8 stand. Item 5 is answered for who-wfa (S7) and item 6 is closed (S4): only
`ground.load_contract` builds a `ContractField`. For § 4's numeral pattern, S8 lists the seven
digit shapes of apple's 180 cells; 40 carry `$ ` inside the cell text, and whether the pattern
admits them is the example author's choice, to be stated beside P4's count.
