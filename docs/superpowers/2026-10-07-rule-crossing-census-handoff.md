# Handoff: loop 3, the membrane guard. The membrane cannot see a rule, and only fed-h41 merges ruled columns (2026-10-07)

**Serves:** maintenance — loop 3 of the four the maintainer ordered on 2026-10-06
(`2026-10-06-r295-grid-scope-handoff.md` § 3): a membrane guard so an asserted table cannot merge
columns the author separated with rules, then fed-h41's asserted cells checked against it.

**Topic:** compile · **Date:** 2026-10-07

**Doc impact: none.**

This loop measured and did not design. The census came back at about the 50K originating floor, so
the spec is left to a fresh session. Part 5 was written first, after the census, and each action
carries its own grade. No `src/` change.

## 5. Next concrete action

0. **ASSERTED (measured, § 2).** The guard cannot be a SHACL shape over the graph the membrane
   validates today, because that graph holds no rule. Of 68 `_validate` calls across the eleven
   documents, 0 saw a predicate or type naming a rule. graincorp-capacity p0 validates 5,854
   triples while its page carries 523 vertical rules. A shape therefore needs the author's rules
   carried into the page graph first, as evidence the membrane can join against `tab:hasBBox`.
   Carrying them moves every document's hash, so the spec must say so and the snapshot must show
   that only the hashes move.
1. **PROPOSED, and the spec's hard question. Refutable in minutes; run it BEFORE writing the spec.**
   The crossing predicate. The strict test (`cell.x0 < rule.x < cell.x1` with a positive-length y
   overlap) fires on 146 cells of three ACCEPTED documents (apple 19, who-covid 109, who-wfa 18).
   In every one, the rule sits less than 0.2 pt inside the cell's right edge: the last glyph's box
   runs past the centre line of the rule that closes the column. Those are correct reads. A guard
   on the strict test would refuse three accepted documents. Candidate, with no tolerance: *a rule
   separates a cell's ink when at least one of the cell's glyphs lies wholly left of the rule
   (`glyph.x1 <= rule.x`) and at least one lies wholly right of it (`glyph.x0 >= rule.x`).*
   **Prediction:** it fires on fed-h41 p7's 12 cells (the `+`/`-` sign glyph right of the rule)
   and on p5's `Total assets (0) 6,852,491`, and on none of the 146. Check it with the page's
   `chars` on the four documents that have crossings, using `scripts/rule_crossing_probe.py`'s
   output to locate the cells. If it fails, the predicate is the subject, not the shape.
2. **PROPOSED.** Glyph boxes are not in the validated graph either. What the page graph has to carry
   (rules alone, or rules plus a per-cell "ink on both sides" fact) depends on action 1's answer.
   It is a § 8 classification: the membrane check is a SHACL constraint (closed world, the holon's
   boundary). The facts it reads come from PROCEDURAL raw extraction (glyph and rule geometry).
   Compare at one precision: the bbox is 2dp and `geometry.extract_rules` is raw. fed-h41 p5's
   crossing scores "partial" only because the rule bottom 413.069 falls 0.001 below the rounded
   y1 413.07. `tab:ruleX` already rounds to 2dp (`gridregion.py:59`), so reuse that rounding and
   do not choose a new one.
3. **ASSERTED.** The definition of done, unchanged from the order: the guard ships on a synthetic
   fixture with its `## FALSIFICATION` block. It refuses fed-h41 p7's and p5's merged tables, so
   both escalate. The seven stay at or above their floors with 0 verdicts moved. Sweep the corpus
   locally, one test file per process, because CI skips the corpus.
4. **PROPOSED, separate.** [[R300]] (an asserted report names a table URI that has no triples) is
   not on the guard's path: the guard runs on the page graph. It is raised, not fixed.

## 1. Goal

Measure, before designing, what a rule-crossing membrane guard would see and what it would refuse.

## 2. Where the primaries are, and what was measured

All of it was measured at `542116d` (src and vocab byte-identical on this branch: `git diff --stat main -- src vocab` is empty).

- **The probe:** `scripts/rule_crossing_probe.py <pdf> <out.json>`, one document per process,
  serially (fed-h41: 203 s, about 320 MiB). It wraps `compile._validate` and `document._validate`.
  It compiles with defaults, takes every table node in the final document graph that carries
  `tab:hasCell` or `tab:hasDataCell`, and tests each cell's `tab:hasBBox` against
  `geometry.extract_rules(pdf, page)`, the extraction the compiler uses (`compile.py:518`).
  - **The population includes DataGrids.** Their cells hang off `tab:hasDataCell`
    (`datagrid.py:739`), not `tab:hasCell`, so a guard that targets `tab:hasCell` alone would miss
    every DataGrid.
- **Where the rules go.** `tab:RuleSpan`/`tab:ruleX`/`tab:ruleTop`/`tab:ruleBottom` are emitted at
  `gridregion.py:58-61` into a local graph inside `grid_evidence()`, which is queried and then
  discarded. `tab:bandRuleX` and `tab:ruleXsSignature` (`sectiongraph.py`) are likewise local.
  The page graph is built separately (`compile.py`, `graph = Graph()` beside `donor_ev`). Page
  scope validates at `compile.py` `_validate(graph)`, and document scope at `document.py`
  `_validate(graph, legs)`. Both are found by grep.
- **Census** (the strict test, no tolerance):

  | document | tables | cells | cells crossed | full / partial | depth inside the nearer edge |
  |---|---|---|---|---|---|
  | **fed-h41** | 17 | 1076 | 13 | 12 / 2 | 4.7 to 148.9 pt |
  | arxiv | 16 | 187 | 0 | – | – |
  | caltrain | 0 | 0 | 0 | – | – |
  | who-covid | 2 | 470 | 109 | 109 / 0 | 0.026 to 0.086 pt, right edge |
  | graincorp-capacity | 1 | 415 | 0 | – | – |
  | graincorp-stem | 3 | 2203 | 0 | – | – |
  | cbh-stem | 6 | 873 | 0 | – | – |
  | apple | 3 | 359 | 19 | 19 / 0 | 0.16 to 0.20 pt, right edge |
  | bfs | 3 | 814 | 0 | – | – |
  | ons | 3 | 568 | 0 | – | – |
  | who-wfa | 10 | 783 | 18 | 18 / 0 | 0.009 to 0.069 pt, right edge |

  Touching-only (zero-length y overlap) is 0 everywhere.
  - **fed-h41 p7, `#p7-datagrid`:** all 12 crossings are full-height and in one row. Each is a value
    with a sign glued on, read as one cell across the rule, for example `96,127+` at
    [407.54, 252.48, 439.94, 260.48] against the rule at x 433.25 (y 112.675 to 280.674).
  - **fed-h41 p5, `#htable3`:** the label cell `Total assets (0) 6,852,491`
    [35.0, 405.07, 400.65, 413.07] is crossed by the rules at x 251.75 and 332.75.
  - **The three right-edge documents:** examples are who-covid p2 `2` (x1 556.4, rule 556.324),
    apple p1 `$ 383,266` (x1 488.86, rule 488.68) and who-wfa p0 `Median` (x1 583.56,
    rule 583.491).

## 3. What was decided, and where it is recorded

- **The spec is deferred to a fresh session.** Reason: the floor. Recorded here only.
- **The strict crossing test is not the guard's predicate.** It would refuse three accepted
  documents (§ 2). Recorded here only; action 1 proposes the replacement.
- **[[R300]] raised.** Recorded in `residues-open.md`.

## 4. Unverified or assumed

- **That fed-h41's 13 cells are misreads was not confirmed by rendering the page.** The glued
  `+`/`-` signs and a label cell that holds a value make that very likely, but no one looked.
- **Which producer emitted fed-h41 p5's and p7's tables, and whether arm (e) (`classify-kind.rq`)
  ever saw those bands, was not traced.** Both are adopted or data-grid tables. If arm (e) cannot
  reach them, that is why the merges survive it, but it is unmeasured.
- **The glyph-side predicate (action 1) has not been run.**
- **graincorp-stem: 34 cells carry a `tab:onPage` that differs from the page in their table's URI.**
  Their rules were looked up on the `onPage` page, and none crossed. Whether that mismatch is a
  defect was not judged, and no row was raised.
- **One run per document, with no null control.** No PDF was given an injected crossing.
  fed-h41's crossings show the probe can fire, and the eight zero rows show it can stay silent.
  That is weaker than a control.
