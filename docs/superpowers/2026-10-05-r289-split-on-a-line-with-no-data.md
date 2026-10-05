# Evidence + handoff: R289's predicted cause REFUTED — the split lands on a line that carries no data (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R289 is the named blocker on lifting cbh's hold.

**Doc impact: none.**

## 5. Next action (written first)

This part was revised at about 66K working tokens, over the 50K originating floor, after § 2.4 landed.
The first draft was written under the floor. Each action is graded.

1. **PROPOSED — run first, in a fresh session, before any spec.** *Narrow "dirty" to a `tab:Text`
   cell in a non-Text data column.* All 13 header-ink lines that § 2.4 moved are words in numeric or
   date columns: `Accepted`, the CDIDs, `au 1er janvier`. The 4 bfs regressions are presumably dirty
   on numeric fragments (footnote digits, a split `-`). The prediction is that **the narrowed rule
   moves the same 13 bands and none of the 4**. This is a one-line change to the cleanliness test in
   the § 2.4 harness, followed by re-running bfs and ons. The prediction is cheap to refute: if it
   refutes, the scope must come from somewhere else, and the next candidate is the fragments'
   headerlessness itself ([[R166]]). The harness is committed: `scripts/r289_split_blast/` (`harness.py <pdf> <out.jsonl>`,
   then `analyse.py <out.jsonl>…`). It was re-run on cbh from the committed copy and reproduced
   § 2.4's cbh row exactly. The cleanliness test is the `dirty` loop in `harness.py::new_split`.
2. **PROPOSED — conditional on 1 holding.** The R289 spec changes both
   `vocab/queries/header-body-split.rq` and its Python reference `_ref_hbs`
   (`tests/etkl/test_derivation_equiv.py`, compared on 300 random grids). It carries choices (i) and
   (ii) from § 2.4 explicitly. Its oracle is a row-count test in `tests/test_cbh_e2e.py`, beside the
   module-scoped compile there: each roster's carried rows = its page vessel rows (10/16/14/5) and no
   `Accepted`/`Completed` EntryCell. After the change, the 7 corpus scores are re-measured serially
   (CI skips the corpus). If the ons and bfs splits move, `tab:` readings move with them.
3. **ASSERTED.** Do not touch the LOOP L ruled law for R289 (§ 2.3), and do not tune the 0.8 pt
   overhang (§ 2.1). Nothing reads it.

## 1. What was run

All runs are at `014f84e`, with scratch scripts in a session scratchpad (not kept).

- Each reader was wrapped and `compile_tables(cbh, 0)` was run. For all four rosters,
  `ruledroles.resolve_ruled_header_rows` → `None` (the LOOP L header-stack law abstains), and
  `holon.assert_hier_region` carries the roster: `#htable1/3/5/7` → 170/268/228/84 triples.
  So header-vs-body is decided by `hierarchical.classify_hierarchical` → `headers.header_body_split`.
- `classify_hierarchical` was wrapped and each roster's band lines and `body_line` were printed:

  | roster | split line | text at split | top / bottom | header box bottom rule |
  |---|---|---|---|---|
  | GERALDTON | 7 | `Accepted Accepted Completed Completed` | 113.5 / 119.5 | 118.7 |
  | KWINANA | 4 | same | 249.6 / 255.6 | 254.8 |
  | ALBANY | 5 | same | 442.3 / 448.3 | 447.5 |
  | ESPERANCE | 4 | same | 610.6 / 616.6 | 615.8 |

  The line after the split, in every roster, is the first vessel row.

## 2. Findings

### 2.1 The § 5 prediction of `2026-10-05-cbh-carried-grid-read.md` is REFUTED

It said the line becomes body *because its ink crosses the header box's bottom rule*. The decision is
not a rule-containment test. `header_body_split` returns the typed AXIOM
`vocab/queries/header-body-split.rq` whenever that query answers, and it consults no rule.
`_hrule_split` is only its all-text fallback. The 0.8 pt overhang is real on **all four** rosters, but
nothing reads it.

### 2.2 The seam: the split row holds off-type cells in data columns

Per data column the query takes `s_col = (last off-type non-abstaining row) + 1` and returns
`MIN(s_col)`. The `VNA #` column's last off-type cell is the label line, so its `s_col` is the
`Accepted` line, where that column is blank (`tab:Blank` abstains). The Date/Time columns
c4/c5/c18/c19 hold the Text `Accepted`/`Completed` on that very row, so their own `s_col` is one row
later. The outer `MIN` takes the earlier one. A row that is provably not body for four data columns is
returned as the first body row. **Read from the query, not yet traced cell by cell** (§ 4).

### 2.3 The LOOP L ruled law abstains on all four rosters, and it should (measured, subagent)

The law is `vocab/queries/header-row-role.rq`. It derives zero rows for every roster, which
`ruledroles.py:293` turns into `None`, passed up at `:310` and returned at `:534`. Guards P1 and P2
pass: the grid is the ruled grid, with 20 columns. Two clauses each refuse on their own. This was
measured by removing one clause at a time, and each removal alone still gives `[]`.

- **Clause 0 (`.rq:52-54`) needs exactly one header-block rule.** Each roster has two: the port-name
  underline and the rule above `Time Nom` (htable1: y 71.7 and 105.0).
- **Clause 1 (`.rq:67-70`) needs a leaf cell in every ruled column.** The `VNA # …` line has 16 cells
  for 20 columns. c4/c5/c18/c19 have none: their labels are the two-line `Time Nom`/`Accepted` stacks,
  vertically centred, so they take lines 1 and 3.

The law never sees the `Accepted` line: `header_rows_of` cuts at `hreg.body_line` first.
**Counterfactual, measured:** with `body_line + 1` the law still abstains (Accepted has 4 cells for 20
columns). With both clauses removed, it derives a `level` and refuses at `:534`. So no configuration of
this law reads cbh's header. This is a property of the page: no single line is the leaf row. It is not
a defect in the law. **The fix seam is the type split (§ 2.2), not the ruled law.**

### 2.4 Blast radius of the candidate rule: cbh fixed, ons and one bfs band improved, four bfs bands worse (measured, subagent)

**Candidate rule:** NEW = the smallest per-column `s_col` candidate at which no data column holds an
off-type, non-abstaining cell.

**Method:**
- A wrapper on `header_body_split` computed OLD and NEW over the same evidence graph and **returned
  OLD**, so every compile and score was unchanged: cbh 1.0, gstem 0.9996, gcap 1.0, ons 0.8685,
  bfs 0.9021, apple 0.9419, who 0.9963.
- All 7 corpus documents were compiled via `compile_document`, serially.
- The candidates come from a per-column copy of the `.rq`. Its `MIN` equals the shipped query on every
  call (`mirror_mismatch = 0`).
- Choices the spec must make explicitly: (i) data columns that R41 excludes still count for
  cleanliness; (ii) a count-tied column's D is a set.

**Controls:**
- Positive: the cbh rosters go 7→8, 4→5, 5→6, 4→5, from the `Accepted` line to the first vessel line.
  They also go 2→3 on their notice-free re-entries.
- Null: OLD == NEW on 312 of 412 AXIOM-decided calls (66 of 83 bands).
- NEW is never `None`, so the rule causes no new escalations.

| doc | bands changed | lines moved into the header (agent's reading of the text, not measured) |
|---|---|---|
| cbh | 8 of 9 | `Accepted Accepted Completed Completed`: header ink ✔ |
| graincorp-stem, graincorp-capacity, apple, who | 0 | — |
| ons | 4 of 14 (p7 ×2, p8 ×2) | CDID series-ID lines (`S222 S243 KI77 …`): header ink ✔ |
| bfs | 5 of 23 | 1 band: the third boxhead line `au 1er janvier vivantes …` ✔. **4 bands: data rows ✘** (`2011 3 7 870 …`, `Berne 1 051 437 …`, `Bâle-Ville …`/`Bâle-Campagne …`) |

The four bfs regressions are **headerless continuation fragments that OLD already reads wrong**: OLD
puts a data row in the header (`2010 2 …`), which is [[R166]]'s class. In those fragments the "dirty"
rows are probably footnote digits and split minus signs (`- 939`) typed as off-type cells. That is the
agent's guess and is not checked.

The rule is right on 13 bands and wrong on 4, and all 4 were already wrong. **It does not ship
unscoped.** Scoping is the spec's job.

## 3. Decided, and where

- **Maintainer rulings 2026-10-05, at the start of this session.** They are recorded here and nowhere
  else:
  - (a) PR #299 merged (`014f84e`).
  - (b) The next loop is R289, with a row-count oracle.
  - (c) The three acceptances with role defects (who-wfa, ons, apple; see
    `2026-10-05-cbh-carried-grid-read.md` § 7) **stand**, with the defects recorded as residues
    ([[R166]], [[R230]], [[R80]]).

## 4. Unverified or assumed

- That the per-column `s_col` values are exactly as § 2.2 states (VNA → split line, c4 → split line + 1).
  This is inferred from the query and the line text. It has not been dumped from the evidence graph.
- § 2.4's verdicts (header ink vs data row) are the subagent's reading of line text and were not
  checked against the rendered page. Why the 4 bfs fragments' rows are dirty was not measured. The
  page attribution of two bfs bands (they report `Word.page` 0) looks wrong.
- Whether any of the 17 changed bands is *carried* (asserted) rather than escalated downstream was not
  measured. So the score effect of the rule is unknown. The harness returned OLD, so no score moved.
- The stub-section-row prediction ("Current assets:", blank in every data column, stays body) is
  consistent with apple's 0 changed bands, but was not checked band by band.
- § 2.3's page-property reading ("no single line is the leaf row") is the subagent's inference. The
  return sites and the clause removals are its measurements, and its scripts are in a session
  scratchpad (not kept).
