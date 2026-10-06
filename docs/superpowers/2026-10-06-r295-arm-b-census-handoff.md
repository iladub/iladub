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

- **Arm (b) is refuted on the seven and the held-out four.** Recorded here only. It is still the
  maintainer's ruling until it is re-ruled.
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
