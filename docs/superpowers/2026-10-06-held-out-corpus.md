# A held-out corpus: does the 7/7 generalise? (2026-10-06)

**Serves:** maintenance — direction (a) of the maintainer's 2026-10-06 ruling, recorded in
`docs/superpowers/2026-10-06-held-out-corpus-handoff.md`.

**Topic:** measurement · **Date:** 2026-10-06

**Doc impact: none.**

## 1. Pre-registration — written before any of the four was compiled

The documents and the prediction below were fixed, and confirmed by the maintainer, **before any of
them was compiled**. Each was fetched to a scratchpad only to confirm the URL resolves, and to read
its page count and producer with `pdfinfo`. No `src/` change is made by this loop.

Selection rule: the layout differs from the seven; not ag-trade, not an ONS or BFS release; public,
domain-neutral, and from a PDF producer the seven do not use. One exception, found when checking
that claim against the register's `cor:producer` values: Caltrain's `Adobe PDF Library 17.0` is the
same family as bfs's `Adobe PDF Library 24.1.163`, at a different major version.

| id | document | pages | producer | why it was chosen |
| --- | --- | --- | --- | --- |
| `fed-h41-2025-01-02` | US Federal Reserve H.4.1, *Factors Affecting Reserve Balances*, release of 2025-01-02 | 11 | Aspose.Words for .NET 21.3.0 | dense ruled balance-sheet tables, a deep row hierarchy (items indented under items), week-over-week change columns, and footnotes |
| `arxiv-1706.03762v7` | Vaswani et al., *Attention Is All You Need*, arXiv v7 | 15 | pdfTeX-1.40.25 | small booktabs tables embedded in two-column scientific prose: the table is a minority of the ink |
| `caltrain-weekend-timetable` | Caltrain weekend printer-friendly schedule | 4 | Adobe PDF Library 17.0 | a stations × trains matrix of clock times: no measure name, and the header is the train number |
| `who-covid-sitrep-41` | WHO COVID-19 situation report 41, 2020-03-01 | 7 | Microsoft® Word 2016 | a per-country case table that runs across several pages, surrounded by prose |

URLs and the sha256 each one was fetched at are pinned in `tests/held-out-manifest.ttl`.

**Prediction (falsifiable):** every one of the four scores well below the seven, all of which are
at or above 0.90. If the four land near the seven, the 7/7 generalises, and that is the finding.

## 2. Where the readings live

**Not** in `tests/corpus-manifest.ttl`. Measured:

- `tests/test_arc_manifest.py::test_etkl_criteria_agree_with_the_corpus_manifest` asserts
  `set(asserted) == set(computed)` over every `cor:Document` in the corpus register. A held-out
  entry there forces an `etkl` criterion into existence, and turns a measurement into a benchmark
  row.
- `scripts/corpus_verdict_snapshot.py` `main` snapshots `CORPUS.rglob("*.pdf")`, so a held-out
  PDF under `corpus/` would silently join every future seven-document sweep.

So the held-out documents get their own register, `tests/held-out-manifest.ttl` (same `cor:`
fields, parsed by nothing that computes the benchmark), and their own gitignored directory,
`held-out/`.

## 3. Readings

Measured at `4d9f5e5` (the `accept-bfs` head, carrying PRs #309 to #311), offline, one document at
a time, through `scripts/corpus_verdict_snapshot.py`'s `snapshot()`. The seven were re-run in the
same session as a control. The snapshot JSONs, the runner and the ink-reach script live in the
session scratchpad and are **not** committed.

| document | score | page words | asserted | escalated | reach | asserted share | wall | peak RSS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fed-h41-2025-01-02 | 0.853 | 4323 | 2902 | 500 | 0.79 | 0.67 | 218 s | 323 MiB |
| arxiv-1706.03762v7 | 0.209 | 2033 | 267 | 1011 | 0.63 | 0.13 | 164 s | 290 MiB |
| caltrain-weekend-timetable | **1.000** | 1982 | 438 | 0 | **0.22** | 0.22 | 27 s | 121 MiB |
| who-covid-sitrep-41 | 0.657 | 2688 | 764 | 399 | 0.43 | 0.28 | 75 s | 252 MiB |
| *control:* apple-fy2026q3 | 0.942 | 756 | 486 | 30 | 0.68 | 0.64 | | |
| *control:* bfs-population-bilan | 0.907 | 3239 | 1469 | 150 | 0.50 | 0.45 | | |
| *control:* cbh-stem | 1.000 | 1243 | 878 | 0 | 0.71 | 0.71 | | |
| *control:* graincorp-capacity | 1.000 | 516 | 406 | 0 | 0.79 | 0.79 | | |
| *control:* graincorp-stem | 1.000 | 2917 | 2227 | 1 | 0.76 | 0.76 | | |
| *control:* ons-index-of-services | 0.868 | 2520 | 667 | 101 | 0.30 | 0.26 | | |
| *control:* who-wfa | 0.996 | 885 | 803 | 3 | 0.91 | 0.91 | | |

*Score* is the compiler's own: asserted / (asserted + escalated) tokens. *Page words* is
`len(extract_words(pdf, page))` summed over pages, the compiler's own extractor. *Reach* is
(asserted + escalated) / page words: the share of the page's ink that enters the score's
denominator at all. Ink in `ignored` regions does not. *Asserted share* is asserted / page words.
Each of the seven clears its `cor:scoreFloor` in this run.

**Reach is an approximate instrument.** On arxiv pages 12 and 14 the region tokens exceed the
page's words (1.67 and 2.29). Most likely, tokens are booked by more than one overlapping region
there. This was not traced. Read reach as a coarse figure, not an exact one.

Escalated regions by reason (page numbers are 0-based, as the compiler numbers them):

- **fed-h41:** KIND_NOT_SUPPORTED, REGION_TILING_FAILED, DATAGRID_RESIDUE (pages 2, 3, 5, 8 and
  10 adopted by the data grid), plus ROUND_TRIP_FAIL ×1 and MATRIX_AMBIGUOUS ×1. Worst page 2
  (0.35).
- **arxiv:** KIND_NOT_SUPPORTED ×43, MERGE_AMBIGUOUS ×2, ROUND_TRIP_FAIL ×2. Most of the escalated
  ink is the reference list and the attention-visualisation pages (10 to 14): **prose and figures
  entering table regions**. Of the paper's tables, Table 1 (page 5) asserts; Table 2 (page 7)
  escalates MERGE_AMBIGUOUS; Table 3 (page 8) escalates ROUND_TRIP_FAIL; Table 4 (page 9) sits on a page with five
  KIND_NOT_SUPPORTED regions and reads at 0.53. Table locations measured with `pdftotext` per page.
- **caltrain:** none. Page 2 asserts one RECORD_TABLE of 28 cells. Pages 0, 1 and 3 are each one
  `NON_TABLE` region, verdict `ignored`, reason *"fewer than 2 columns"*, though every one of the
  four pages is a stations × trains matrix of about 480 to 510 words (`pdftotext -layout`).
- **who-covid:** KIND_NOT_SUPPORTED ×6, MERGE_AMBIGUOUS ×1, DATAGRID_RESIDUE ×1 (page 3 adopted).
  The country table (pages 2 to 4) reads at 0.89 to 1.0; pages 0, 1, 5 and 6 are prose and
  escalate.

## 4. Findings

1. **The prediction holds for two of four, partly for a third, and fails in the worst way for the
   fourth.** arxiv (0.21) and who-covid (0.66) land well below the seven. fed-h41 (0.85) lands
   below every floor but ons's 0.84, not "well below". Caltrain scores **1.0**, at the top of the
   seven, while asserting 22% of its ink.
2. **The score cannot see a table the compiler ignored.** That is by construction: `ignored` ink
   is outside the denominator. Caltrain is the case that makes it matter. Three wholly tabular
   pages are classified as having fewer than two columns, and the document scores perfectly. So
   the score cannot answer this loop's question on its own, and the seven's 7/7 rests on a score
   with this blind spot.
3. **The control shows the blind spot is not specific to Caltrain, but the seven do not show it
   as clearly.** Reach in the seven runs from 0.30 (ons) to 0.91 (who-wfa). Ignored ink is often
   legitimately prose or furniture. cbh's carried-grid read accounted for all 1244 page words
   with 878 in regions. So low reach is not by itself a defect, and nothing here says how much of
   ons's or bfs's ignored ink is table. Caltrain is the clean case only because none of its ink
   is prose.
4. **Prose enters table regions on documents unlike the seven.** That is arxiv's and who-covid's
   loss: KIND_NOT_SUPPORTED on reference lists, figure labels and report prose. It is a different
   failure from Caltrain's, in the opposite direction: ink admitted as table that is not one,
   rather than a table refused.
5. **No reading was checked for correctness.** Every figure above is a token ledger. Whether
   fed-h41's 2902 asserted tokens sit in the right cells is unmeasured, and a score is not an
   acceptance (the graincorp-capacity note's rule).

## 5. Handoff

Written at about 75K working tokens, past the 50K originating floor. Part 5 comes first, and each
action carries its own grade.

**5. Next concrete action.**

- **PROPOSED, and the maintainer's to choose:** the ruled order was (a) held-out, then (b)
  contracts. Finding 2 bears on that order. Contracts measure what *grounds*, and a table the
  compiler ignores never reaches grounding. So either (b) goes ahead as ruled, or [[R295]] comes
  first. Neither is chosen here.
- **PROPOSED, if R295 comes first (the prediction can fail within minutes):** the refusal happens
  at the region classifier's column count, not in band detection. Run the classifier on Caltrain
  page 0 and read which seam emits *"fewer than 2 columns"* before designing anything. If the
  bands themselves are wrong, the subject is band detection and this guess is refuted.

1. **Goal:** find whether the 7/7 generalises to documents the compiler was not tuned on, with no
   `src/` change. Done; § 4 is the answer.
2. **Primaries:** `tests/held-out-manifest.ttl` (the four pinned documents; fetch with
   `.venv/bin/python scripts/fetch_corpus.py tests/held-out-manifest.ttl held-out`); § 3 above
   for the readings; [[R295]] in `residues-open.md`. Re-measure with
   `corpus_verdict_snapshot.snapshot(path)` per document, one at a time.
3. **Decided, and where:** the held-out documents live in their own register and directory, not in
   the corpus register (§ 2, this file). The four documents were confirmed by the maintainer in
   conversation, recorded only in § 1.
4. **Unverified:** the correctness of every asserted reading (finding 5); reach's double counting
   on arxiv pages 12 and 14; how much of the seven's ignored ink is table rather than prose.
