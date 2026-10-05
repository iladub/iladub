# Handoff: R289 — scope the typed split before specifying it (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R289 is the named blocker on lifting cbh's hold.

**Doc impact: none.**

Written at about 86K working tokens, past the 50K originating floor. Parts 1–4 are pointers. Part 5's
actions were decided at about 66K and are graded one by one. They repeat the evidence note's part 5,
which is the source.

## 5. Next concrete action

1. **PROPOSED, run first:** narrow the harness's "dirty" test to *a `tab:Text` cell in a non-Text data
   column*. Then re-run ons and bfs, and cbh as the positive control.
   - **Prediction:** the 13 header-ink bands still move, and the 4 bfs data-row bands no longer do.
   - **How to run it:** change the `dirty` loop in `scripts/r289_split_blast/harness.py::new_split`.
     `cells.rq` already gives each cell's normalised type `?ct`. Then run
     `.venv/bin/python scripts/r289_split_blast/harness.py <pdf> <out.jsonl>` one document at a time,
     and `analyse.py <out.jsonl>…`.
   - **Cost:** a refutation costs about 15 minutes. In that case, look for the scope in the fragments'
     headerlessness ([[R166]]) instead, and the remedy may be R166's rather than R289's.
2. **PROPOSED, only if 1 holds:** write the R289 spec. Its required contents are in evidence note part 5
   action 2: the `.rq` and its `_ref_hbs` mirror change together; the row-count oracle in
   `tests/test_cbh_e2e.py` (rosters 10/16/14/5, no `Accepted`/`Completed` EntryCell); then a serial
   7-document score sweep.

## 1. Goal

cbh's four port rosters must stop carrying the header's bottom line as a data row, with no regression
elsewhere, so that cbh's hold can be adjudicated again.

## 2. Where the primaries are

- `docs/superpowers/2026-10-05-r289-split-on-a-line-with-no-data.md` holds the evidence for every
  claim here:
  - § 2.1: the predicted cause is refuted.
  - § 2.2: the seam.
  - § 2.3: why the ruled law is not the seam.
  - § 2.4: the blast-radius table, with all 17 changed bands.
- `vocab/queries/header-body-split.rq` is the decision. Read its header comment for the per-column
  `s_col` and the R41 clauses.
- `tests/etkl/test_derivation_equiv.py` (`_ref_hbs`) is the Python mirror that the `.rq` must keep
  equal to.
- `scripts/r289_split_blast/` is the harness. It returns OLD, so it never moves a score.
- R289's full row is in `docs/superpowers/residues-open.md`.

## 3. Decided, and where

- **Maintainer rulings 2026-10-05:**
  - #299 merged;
  - the next loop is R289 with a row-count oracle;
  - the who, ons and apple acceptances stand.

  They are recorded in the evidence note § 3, and only there.
- **The unscoped "first clean candidate row" rule does not ship.** This is an agent conclusion from
  § 2.4 (4 regressions), recorded in the evidence note and in PR #300.

## 4. Unverified or assumed

- The header-ink vs data-row verdicts in § 2.4 come from the line text. Nobody checked them against
  the rendered page.
- It was never measured why the 4 bfs fragments' rows are dirty.
- Whether any of the 17 changed bands is carried rather than escalated is not measured, so the score
  effect is unknown.
- Two bfs bands report `Word.page` 0, which looks wrong.
