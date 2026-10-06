# Handoff: R295 arm (b) census. The widest tiling span cuts spanner headers and data rows (2026-10-06)

**Serves:** maintenance. Loop 1 of the four the maintainer accepted on 2026-10-06
(`2026-10-06-r295-grid-scope-handoff.md` § 3). No `src/` changes.

**Topic:** compile · **Date:** 2026-10-06

**Doc impact: none.**

Written at about 35K working tokens, under the originating floor. Part 5 comes first.

## 5. Next concrete action

1. **A MAINTAINER RULING comes first.** Arm (b) was ruled earlier today
   (`2026-10-06-r295-y-extent-refuted-handoff.md` § 3): *a table's extent is the widest contiguous
   run of lines that the author's rules, drawn within that run, tile.* The ruling rested on four
   Caltrain pages. The census in § 2 runs the same search across the seven and the held-out four.
   **On five documents other than Caltrain, the span it returns is wrong** (§ 2.2). The remaining
   arms:
   - **(e) Escalate, do not split (recommended).** A ruled band whose full extent does not tile, but
     where some proper sub-span of at least 2 lines does, and tiles into **more** columns than the
     band's current leaf grid, has a reading that under-resolves the author's own rules. Such a band
     is not asserted and not ignored: it is escalated (`UNSUPPORTED_TABLE`), and the reason names the
     span and both column counts. No line is moved, so no spanner row or data row can be lost.
     Measured population (§ 2.3): 6 bands move, all held-out. **0 of the seven move.** Caltrain's
     four pages enter the denominator, and page 2 stops asserting its 2-column misread. That meets
     loop 1's definition of done (`2026-10-06-r295-grid-scope-handoff.md` part 5 item 3), but it
     escalates the whole band, title lines included. Loop 2 (Caltrain's header) would still need
     the extent. Its top edge is a **line-role** question, which is Jev's slot once a role oracle
     exists.
   - **(b′) Split, but extend the extent over lines that its own rules enclose in y.** This rescues
     the bfs and who-covid spanners. It still cuts apple p0's *"Three Months Ended / Nine Months
     Ended"* spanner (not enclosed) and who-covid p3's trailing data rows. **Refuted** by the same
     census.
   - **(b) as ruled.** Refuted by § 2.2.
2. **ASSERTED, once (e) is ruled.** Arm (e) is a guard on the classification. It changes no
   partition, so its blast radius is exactly § 2.3's six bands. Test it on a synthetic fixture: a
   ruled band whose title line straddles the rules above a tiling grid. Before the guard the fixture
   gives `NON_TABLE`, after it `UNSUPPORTED_TABLE`. Carry a `## FALSIFICATION` block. Sweep the seven
   locally, one test file per process. The hashes should not move, because § 2.3 predicts zero
   corpus bands. Any hash that moves refutes that prediction, so read it.
3. **PROPOSED.** Whether (e) belongs in `regions.classify` (a reason the classifier emits) or in
   `_build_ruled_band` (a band attribute). The seam to measure is where the band's word lines and
   its rules are both still available unmodified. The production band is re-bucketed by
   `rule_aware_lines`. The census searched the **word** band, built with the same rule filter as
   `_build_sub`, and gated on the **production** band (§ 4).

## 1. Goal

Make Caltrain's ignored timetable pages enter the score's denominator, and stop page 2 asserting a
misread, without moving any of the seven. Unchanged from the previous handoff.

## 2. Where the primaries are, and what was measured

All of it was measured at `f72b00d`, offline, with a scratchpad script that was not committed. Its
logic, enough to rebuild it: for every page with rules, replicate `page_bands` up to the sub-bands
`_build_sub` receives (`detect_bands` → `segment` → `cut_trailing_notes`, skipping box-split bands).
For each sub-band that carries rules:

- build the production band with `_build_ruled_band(sub, rules, hrules, chars)`;
- if `_rule_boundaries` returns a vector for it, record it as **FULL-TILES**;
- otherwise search widths *n* down to 1 for spans *lo..hi*. The oracle for a span is
  `_rule_boundaries` on `Band(lines[lo..hi], rules overlapping that y-range)`, using the same
  overlap predicate as `_build_sub`. Report the widest width, every span that reaches it, the column
  count of the first, and for each line outside it whether some extent rule **encloses** it in y.

Corpus: the seven (`corpus/*/*.pdf`) plus the held-out four (`held-out/*.pdf`).

### 2.1 Populations

- **171** ruled sub-bands. **32** tile in production, and arm (b) leaves every one of them unchanged
  by construction (the widest span is the whole band).
- **139** do not tile. On **34** of those, some sub-span tiles.
- **20** have a unique widest span of at least 2 lines that tiles into more columns than the band's
  current grid (the ordinal gate used in R225 arm B). **8** of those 20 are in the seven: cbh p0
  ×4, apple p0, bfs p5 ×2, ons p8.

### 2.2 What the widest span cuts (the refutation)

| band | current | lines the extent leaves out | what they are |
| --- | --- | --- | --- |
| caltrain p0 to p3 | `NON_TABLE`/1, p2 `RECORD_TABLE`/2 | title ×2, heading, legend above; footer below | furniture. **Correct.** |
| apple p0 | `UNSUPPORTED`/3 → ext 5 | *"Three Months Ended Nine Months Ended"* (not enclosed) | **spanner header row** |
| bfs p5 ×2 | `UNSUPPORTED`/7 → ext 11, 9 | *"(Cantons) État de la / Composantes de l'évolution"* (enclosed) | **spanner header row** |
| who-covid p2 | `UNSUPPORTED`/6 → ext 7 | *"Province/ Daily Cumulative"* (enclosed) | **spanner header row** |
| who-covid p3 | `UNSUPPORTED`/4 → ext 5 | below: *"Eastern Mediterranean Region / Iran … / Kuwait … / Bahrain …"* | **data rows** |
| cbh p0 ×4 | `UNSUPPORTED`/16 → ext 20 | port name plus *"BERTH MAY BE UNAVAILABLE …"* notices | notices. Plausibly correct, but cbh is accepted and would move. |
| who-covid p4 | `NON_TABLE`/1 → ext 5 | footnotes below | furniture. Correct. |
| arxiv p12 to p14 | attention figures | figure labels | a figure, not a table |

A spanner label crosses the leaf rules by design, so a header row with spanners **never** tiles, and
the widest tiling span always stops below it. That is R232/R233's lesson (*the leading cut removes
the boxhead*), reached by a different route. The oracle refuses spans that are too wide. It cannot
tell a title row from a header row, because that distinction is a line role, not geometry.

### 2.3 Arm (e)'s population

Arm (e) uses the same gate as § 2.1's 20, but changes only the classification, and only of a band
that is **not already** `UNSUPPORTED_TABLE`. It also excludes a band whose widest tiling span is the
whole word band. That is ons p8's footnote block, which tiles as words but not after re-bucketing:
a build question, not a scope one. What is left:

- caltrain p0, p1, p3 (`NON_TABLE` → escalated); caltrain p2 (`RECORD_TABLE`/2 misread → escalated)
- who-covid p4 (`NON_TABLE` → escalated); arxiv p13, one band (`NON_TABLE` → escalated, a figure:
  fail-safe, not correct)

**Zero bands in the seven.** cbh, apple and bfs are already `UNSUPPORTED_TABLE`, so the guard does
not touch them. This was counted by reading the census rows. It is not a run of the guard.

## 3. What was decided, and where it is recorded

- **Arm (b) is refuted on the seven and the held-out four.** Recorded here only.
- **RULED by the maintainer, 2026-10-06, in conversation (recorded here and in the commit that
  implements it): arm (e).** It supersedes arm (b). Implemented in this same PR: see § 6.
- **No `src/` change was made**, because the ruled arm failed its census before any code was written.

## 4. Unverified or assumed

- **Arm (e) has not been run.** § 2.3 is read off the census, not off a compile. In particular, the
  claim that the seven's hashes do not move is a prediction.
- **The census searched the word band and gated on the production band.** The two disagree on ons
  p8. Whether they disagree anywhere else in a way that matters to (e) was not checked.
- **cbh's left-out lines are assumed to be notices**, from their text only. They were not rendered.
- **arxiv p13 escalating a figure** is fail-safe under the score, but it is not a correct reading.
- Ties: the census found a unique widest span wherever the width is at least 2, except who-covid p2's
  second band (width 1, many ties), which both gates exclude.

## 6. Arm (e), built after the ruling (same PR)

Written at about 115K working tokens, past the originating floor and under the executing floor.
Every claim below carries the measurement it rests on, and § 7's next action is graded.

- **Code:** `grid.widest_tiling_span` (evidence, PROCEDURAL: the unmodified `_rule_boundaries` searched
  over contiguous runs of at least 2 lines, rules scoped by y-overlap). `classifygraph` emits it as
  `tab:ruledSpanFirstLine`/`LastLine`/`ColumnCount` (`vocab/ontology/tab.ttl`).
  `vocab/queries/classify-kind.rq` derives `?underResolved` and escalates (AXIOM, ordinal, no
  constant). `regions.classify` only names the evidence in the reason:
  *"author rules tile lines lo..hi into k columns but the band grid has n"*.
- **Tests:** `tests/etkl/test_ruled_span_escalates.py`, 9 tests on synthetic fixtures. FALSIFICATION,
  three ways, each restored afterwards:
  - (1) `?kind` bound to `?base`: `test_titled_band_escalates_and_names_the_span` FAILS.
  - (2) the evidence emission replaced by `span = None`: the same test FAILS.
  - (3) the `?base != tab:UnsupportedTableKind` clause dropped:
    `test_an_already_escalated_band_keeps_its_reason` FAILS.

  After restoring, 9/9 pass.
- **Population** (`page_bands` + `classify` over every page of all eleven documents): **9 bands,
  all held-out.** Caltrain p0 to p3 give *"lines 4..36 into 18/19/18/19 columns"*, which is the hand
  span from `2026-10-06-r295-y-extent-refuted-handoff.md` § 2.2, exactly. The others are who-covid p4
  b0 and arxiv p12 b1, p13 b1, p13 b2, p14 b2. The arxiv bands are attention figures: a fail-safe
  escalation, not a correct reading. § 2.3 predicted 6 bands. The difference is all arxiv, because
  the census read sub-bands and this run reads the final bands.
- **The seven:** `corpus_verdict_snapshot.py` was run before (worktree at `c23d232`) and after
  (`cc30648`), then compared with `corpus_snapshot_diff.py`: **0 of 7 documents changed.** Every score
  and every canonical graph hash is identical.
- **Caltrain** (`snapshot()` on the held-out PDF): before, score **1.0**, with p0, p1 and p3
  `ignored` (*fewer than 2 columns*) and p2 `asserted` (28 cells, the 2-column misread). After, score
  **0.0**, with all four pages `escalated` (`KIND_NOT_SUPPORTED`). This is loop 1's definition of
  done: the pages enter the denominator, the misread is gone, and the score falls from a hollow 1.0.

## 7. Next concrete action (after this PR)

1. **ASSERTED.** Loop 2, Caltrain's header, as the maintainer ordered (`2026-10-06-r295-grid-scope-handoff.md`
   § 3). Its input now exists: the escalation reason carries the run *lines 4..36*, the run the
   hand construction used.
2. **PROPOSED.** That run's **top edge is not the table's extent.** On Caltrain it happens to be,
   because the header row "Train No." tiles. On apple p0, bfs p5 and who-covid p2 a spanner row lies
   above the run (§ 2.2). Loop 2 has to decide which lines above the run belong to the boxhead, and
   that is a line-role question with no oracle yet (`2026-09-27-jev-boxhead-spike-evidence.md`). Check the ons boxhead
   reader (`baml_src/boxhead.baml`) against Caltrain's lines 2 to 4 first. If it cannot tell the
   legend "6XX Local" from a header, the role oracle is the thing to build.
