# Evidence — `Tessin` is read; bfs is still not accepted, and the reason has changed

**Serves:** prog:criterion:etkl:05 — bfs-population-bilan.

**Date:** 2026-09-19. **Branch:** `tessin-trailing-furniture`.

**Doc impact: none.**

---

## 5. Next action — ASSERTED in its subject, PROPOSED in its remedy (written first)

**bfs p5 holds TWO tables and the adopted data grid reads them as ONE.** T1 (by year, 12
columns) and T2 (by canton, 11 columns) share one `p5-datagrid` with one header per column, and
that header is T1's. Measured on the compiled graph: Zurich's *solde migratoire international*,
`26 171`, sits in `p5-datagrid-c6`, whose only `tab:coversColumn` header is T1's. **All 270 of
T2's entries are asserted under T1's column labels.** That is a misread column identity on 270
cells, and it — not `Tessin` — is what now keeps bfs `cor:Unadjudicated`.

- *Asserted:* the defect exists and is the next subject for etkl:05. The measurement is above.
- *Proposed:* the remedy is that a page grid must end where a second boxhead begins — T2's own
  header band (p5 region 8, `REGION_TILING_FAILED`, 20 tokens) sits between the two row blocks
  and is currently booked as residue. Whether the datagrid should split there, or adoption
  should refuse a page with two boxheads and let the band path read T2 by donation as it reads
  p6, is **not measured**. Run both before building either.

## 1. What was wrong

bfs p6's `Tessin` row, its `Source:` line and two footnotes are set at one pitch (gap 3.4pt, the
row pitch), so `detect_bands` returns them as one band. The footnotes run the band's full width
and close every gutter the row's numbers keep open: the band's words arrive as
`'Tessin 357 720 62 877 78 804'`, one word across four columns. The band escalated
`KIND_NOT_SUPPORTED` and even the row ALONE was refused by the donation membrane
(`cell_round_trips` False on the fused word).

## 2. What decides

`datagrid.derive_data_grid` has already ruled on every text line of the page. On p6 the band
reads `A r r r` — `Tessin` admitted, three lines refused. `trailing.cut_trailing_notes` walks a
band from the bottom and cuts a run of refused lines **only where the line directly above it was
admitted**. No constant, no geometry, no reading judgement of its own (§8: PROCEDURAL glue over a
shipped derivation, the `head_line_refusals` shape). The notes keep a band of their own.

Corpus census, every band of ≥ 2 lines on all 7 documents — the walk fires on 5:

| band | verdicts | first line cut |
|---|---|---|
| bfs p5 b5 | `AAAArrrr` | `Sources: OFS - BEVNAT, ESPOP, STATPOP` |
| bfs p5 b13 | `AAAAAArrrr` | `Sources: OFS - BEVNAT, STATPOP` |
| bfs p6 b10 | `Arrr` | `Source: OFS - STATPOP` |
| ons p4 b0 | `rrrrrrA…Ar` | `Source: Index of Services estimate from …` |
| ons p7 b6 | `Ar` | `"` |

Every cut line is a note. No data row is cut.

## 3. What moved (`scripts/corpus_verdict_snapshot.py`, before = the cut patched to identity)

| document | before | after | graph |
|---|---|---|---|
| bfs | 0.897196261682243 | 0.9021428571428571 | 16147 → 16736 triples, chains 8 → 9 |
| ons | 0.8452535760728218 | 0.8463541666666666 | 12348 → 12440 |
| apple, cbh, gcap, gstem, who | — | — | IDENTICAL by canonical hash |

bfs p6: cells 285 → 294 (`Tessin`, 9 entries), asserted ink 312 → 327, escalated 25 → 19. Every
entry row of p6 is now read: 32 rows × 9 + 6 header cells = 294.

**ons rose and nothing on it was fixed — say so beside the figure.** p7's stray `"` line left a
two-line band, where it was escalated, for a one-line band of its own, where it is *ignored*:
escalated 52 → 51, no entry gained. It is one token of furniture and the floor (0.84) is
untouched, but it is a score moving by reclassification and not by reading.

## 4. Falsification

- Remove the admitted-row guard from `trailing_refused` →
  `test_a_band_the_datagrid_admits_nothing_in_is_never_cut` FAILS; restored → green.
- Patch `cut_trailing_notes` to identity → `Tessin` is not asserted
  (`test_FALSIFICATION_without_the_cut_tessin_is_not_read`, corpus-gated).
