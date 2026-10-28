# Handoff: a superseded firing is disposed by publisher truth (design chosen, spec owed)

**Serves:** prog:criterion:tab:05 — and, by the same mechanism, part of tab:02 and tab:09.
`prog:met false` on all three at `087c1ca` (`tests/arc-manifest.ttl`, `prog:criterion:tab:05 a`).

**Doc impact: none** (a handoff; the spec it asks for will carry its own).

Written at ~77K working tokens, **1.5× the originating floor**, so the spec was not started. Parts
1–4 are pointers and records. Part 5 is written first and graded per action.

## 5. The next concrete action (written first)

1. **ASSERTED — write the spec** `docs/superpowers/specs/2026-10-29-<topic>-design.md` in a fresh
   session, from § 3 below, which holds the two maintainer choices and the design shape as presented
   in chat. Do not re-open those two choices. The shape's **mechanics** (step 2) were never approved
   section by section. They are for the spec to settle and the maintainer to review.
2. **PROPOSED — the design shape**, from § 3's last item. It rests on three predictions that each
   must be run before the spec relies on them:
   - **(a)** *Apple p2's adopted grid scores every truth cell `CORRECT` against the 10-Q cash-flow
     table, with no grid cell left unclaimed.* This is falsifiable in minutes once a truth CSV
     exists. If it fails, the disposal is refused **honestly** and tab:05 stays unmet. That is the
     oracle working. The loop then becomes "fix the reading the truth found wrong" instead of
     "meet tab:05". Budget for it.
   - **(b)** *The 10-Q table's row label and column path can be read from markup alone.* There are no
     header ids here, unlike Fed. Headers are `<td colspan>` cells, so the extractor reads the
     table's colspan grid. That is decidable markup, not geometry, but it is **not measured**. A new
     extractor is needed beside `scripts/ground_truth_extract.py`, which reads Fed's `header=` ids.
   - **(c)** *The scorer can report grid cells that no truth cell claims, on unmatched records too.*
     `SPURIOUS` counts only matched rows (spec 2026-10-22 § 3.3). A new count is needed. Its exact
     definition belongs to the spec.

## 1. Goal

Make tab:02, tab:05 and tab:09 satisfiable. Each is stuck on **superseded-only** firings, which
neither arm of the criterion admits today.

## 2. Where the primaries are

- **The firing profile:** `tests/corpus-baseline/*.json`, `pages[].regions[].{reason,verdict}`.
  Re-tally it there; don't trust the table below. At `087c1ca`, `corpus/` only, as live/superseded:

  | reason | criterion | live | superseded |
  | --- | --- | --- | --- |
  | MATRIX_AMBIGUOUS | tab:05 | 0 | 1 (apple p2 r2) |
  | ROUND_TRIP_FAIL | tab:09 | 0 | 10 (bfs p5 ×6, ons p7 ×1 + p8 ×3) |
  | REGION_TILING_FAILED | tab:02 | 3 (bfs p4/p5/p6) | 6 (apple p2 ×4, ons p7 ×2) |
  | DATAGRID_RESIDUE | tab:08 | 4 (apple p2, bfs, ons ×2) | 0 |
  | MULTI_TABLE / TRANSPOSED / ROW_GROUP | 01/03/04 | 0 | 0 |

- **Why superseded-only is stuck:**
  - `cor:DisposalShape` constraint (4) refuses a disposal of a reason with 0 live firings
    (`tests/corpus-shapes.ttl`, comment block above `cor:DisposalShape`).
  - The oracle parametrises over `live_pairs` only (`tests/test_corpus.py`,
    `test_escalation_reasons_are_adjudicated`).
  - Arm (b) needs `live 0 ; superseded 0` (spec `2026-09-18-a-firing-is-not-a-fact-design.md` § 2.1).
- **The criterion text needs no change.** Arm (a) reads "fires on the corpus and every firing
  document carries a dated cor:adjudication … disposing of it". It does not say *live*. The
  restriction is test-side. Re-read the statement to confirm before relying on this.
- **Precedents to reuse:**
  - tab:07's disposal machinery (spec `2026-10-19-the-disposal-carries-its-reading-design.md`;
    `cor:judgedAgainst` snapshots, `tests/corpus_firings.py` `lift_snapshots`).
  - Ground-truth slice one (spec `2026-10-22-ground-truth-slice-one-design.md` §§ 3, 9–11;
    `src/iladub/truth.py` `score_table`; `scripts/corpus_verdict_snapshot.py` `truth_block`;
    `tests/ground-truth/fed-h41-2025-01-02/`).
- **Apple's publisher truth, measured 2026-10-29 by a subagent.** The scratchpad files are gone with
  the session, so the facts are recorded here and should be re-fetched:
  - The corpus PDF's p2 (0-based) is *CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS
    (Unaudited)*, in millions. Columns: Nine Months Ended June 27, 2026 and June 28, 2025. 29 value
    rows (58 values) and 7 section-label rows.
  - The truth source is the Form 10-Q, accession `0000320193-26-000020`, filed 2026-07-31:
    `https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm`. SEC needs
    a User-Agent; the subagent used `iladub-research contact@iladub.dev`.
  - The cash-flow table is the **17th `<table>`** (index 16, 0-based, none nested): a 49,055-byte
    span, sha256 beginning `7999b55068408a58`. All 58 values are `ix:nonFraction`. Parentheses are
    **plain text outside the tag**, and `sign="-"` disagrees with the displayed sign (15 against 29),
    so truth must be the **displayed** value, never the XBRL sign.
  - **The row-for-row comparison found 58 of 58 values equal, every label equal and the same
    periods.** p1 (balance sheet, table index 14) matched 56 of 56. p0 (operations, index 12)
    matched 76 of 76 statement values, but p0's two footnote blocks (net sales by segment and by
    category, 48 values) have **no** row-for-row 10-Q counterpart. Only p2 is needed for tab:05.
- **ONS and BFS publisher truth:** measured by a second subagent. See the appendix below if
  present. If it is absent, it was not measured.

## 3. What was decided, and where it is recorded

- **The next loop is "rule a superseded arm", not tab:08, band-path repair or R340.** The maintainer
  chose this on 2026-10-29, in chat. **It is recorded only in this file.**
- **"Read correctly" is proven by publisher truth: the ground-truth slice extended to the corpus.**
  The maintainer chose this on 2026-10-29, in chat, over an ink-coverage check (rejected because it
  proves coverage, not attachment, and R238's 404 rows without identity would have passed it) and
  over a human-read reading (rejected because the judgement would live in a rationale string).
  **It is recorded only in this file.**
- **The design shape (presented in chat, not approved section by section):**
  - A disposal may name a reason whose firings in its snapshot are superseded.
  - It is admitted only if that snapshot's truth block covers every page carrying such a firing.
  - On each covered page, every truth cell must be `CORRECT` and no asserted cell may be left
    unclaimed.
  - Ink the adoption drops is a **live** `DATAGRID_RESIDUE` firing and stays tab:08's subject, so
    the arms don't overlap.
  - Requiring the **whole** truth table to be perfect avoids any mapping from regions to truth
    cells, which would need geometry. It is a sufficient condition, not a tight one.

## 4. Unverified or assumed

- All three predictions in § 5 item 2.
- That the snapshot JSON's truth block can carry what D2 needs: per-table pages and the new
  unclaimed count. Both are probably additions, and so a 24-minute baseline regenerate.
- That `lift_snapshots` can lift a truth block from a dated blob as it lifts firings.
- That a document with **both** live and superseded firings of one reason needs both kinds of
  evidence. None exists on the corpus at `087c1ca`, so this may be YAGNI.
- R62 looks **stale**. Its subject was apple p0's MATRIX + 4 TILING firings, and p0 now asserts 124
  cells with no escalation. The corresponding firings now sit superseded on **p2**. It was not
  opened beyond its row, and not closed.
- R237 (stale `FIRES n` comments on the tab rung) is still open. This loop's manifest edits are a
  natural moment to fix the three comments it touches.
- Licensing of committing a truth CSV of SEC filing values (public filing). It is not checked
  against the § Open items note on terminology licensing, which is about SNOMED/LOINC, not this.

## Appendix: ONS and BFS publisher truth (measured 2026-10-29 by a subagent; scratchpad gone)

Both sources match the PDFs exactly on every cell they hold. **Neither states the PDF's header
structure.** So `col_path` would come from a code-to-label map that we author, not from markup. That
is a weaker oracle than Apple's, and **whether such a map is admissible is a question for the spec,
not a settled point.**

- **ONS IOS1** (p7–p8):
  - Size: 450 cells (90 rows × 5 columns, in 6 blocks).
  - Matching vintage: `…/datasets/indexofservices/current/previous/v131/ios1.csv`, release
    16-04-2026. The version labels are off by one against their displayed dates. v130 matches only
    129 of 450 cells, because of revisions.
  - Against v131: **425 of 450 exact**, joined by CDID and period. The 25 that miss are the quarterly
    index rows, 2024 Q4 to 2025 Q4. **No machine-readable source holds them.** So a "whole truth
    table perfect" condition **cannot cover** the PDF's full ink here.
  - The xlsx is flat. There are no boxhead labels, and series titles differ from the PDF's wording.
    `S222` heads two blocks, which are distinguished only by period type.
- **BFS T2** (p5, 27 rows × 9 columns): there is no same-layout file.
  - xlsx `su-f-01.02.04.06.01` (`dam-api.bfs.admin.ch/hub/api/dam/assets/32229237/master`):
    **189 of 189 exact** on the 7 shared columns. It splits migration differently.
  - STAT-TAB PxWeb `px-x-0102020000_101`: **216 of 216 exact**, but the PDF's international and
    intercantonal columns are **derived** from it as differences, not stored. Its vintage is today's,
    not pinned to the release.

**Implication (PROPOSED, for the spec to test):**
- Apple p2 is the one clean case: same layout, same labels, stated values. It is the first slice,
  and the whole of tab:05.
- tab:09's superseded firings are all on bfs and ons. tab:02's are on apple and ons. They need either
  an admissible authored code-to-label map or a narrower condition than "every cell of the page's
  truth is CORRECT". Expect the first slice to meet tab:05 at most, not tab:02 or tab:09.
