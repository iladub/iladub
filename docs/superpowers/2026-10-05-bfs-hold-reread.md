# bfs re-read against its hold: the prediction is REFUTED, three things hold it (2026-10-05)

**Serves:** prog:criterion:etkl:05 — re-reads bfs on `main` against the hold reason recorded on 2026-09-19, as `2026-10-05-bfs-hold-handoff.md` part 5 item 1 directed.

**Topic:** bfs-hold · **Date:** 2026-10-05

**Doc impact: none.**

Read-only measurement. No `src/` change. Written at about 76K working tokens, past the 50K
originating floor. Part 5 is graded per action, and it proposes no fix: the next session is a
strategy review with the maintainer, as the handoff recommended.

## 5. Next concrete action (written first)

1. **ASSERTED: hold the strategy review the handoff recommended, using § 2 as its input.** The
   review needs no new measurement. Its sharpest question is now concrete: **R289 and [[R293]]
   may be one defect class**, a multi-line boxhead whose lower lines are carried as data. One is on
   cbh and one on bfs, and they are the only two held documents. Whether they share a *seam* is
   NOT measured (§ 4).
2. **PROPOSED, only if the review picks bfs: record the canton grid's boxhead** with the shipped
   BAML reader (`BAML_LIVE=1 ILADUB_RECORD_READINGS=1`, `readings/boxhead/README.txt`). Prediction:
   the reader labels the 9 value columns and the oracle disposes them. That is uncertain, because
   this header has two spanner levels (`Composantes de l'évolution de la population` over
   `Solde migratoire` over `international` / `intercantonal`), and the Jev spike
   (`2026-09-27-jev-boxhead-spike-evidence.md`) missed every spanner. Even if it lands, bfs is
   still held by [[R293]] and [[R294]].

## 1. Goal

Find out whether fixing #303's recorded reason (p5's single grid spanned two tables) leaves bfs
adjudicable.

## 2. Findings (measured on `bfs-adjudication` = `main` `81a2ca6`)

Compiled with `compile_document`. The score reproduces at **0.9021428571428571**. Every `EntryCell`
on p5 and p6 was dumped as a matrix with its column labels, then read against a pdfplumber
render of each page. The scripts were scratchpad-only and are not committed. Each finding below
names the graph node to re-check it from.

### 2.1 p5 year grid (`#p5-datagrid-2`, 19 × 12, 226 cells): right, except two entries

- Its 11 labels replay onto the new grid and match the printed header, column for column. The
  stub is unlabelled. This settles handoff item 1(c).
- All 226 values match the page.
- **The 2015 row's two population figures are escalated, not asserted** → [[R294]]. On the page,
  `8 237 666` (1 Jan) and `8 327 126` (31 Dec) are typeset half a line ABOVE the `2015` line: top
  190.9 against 197.0 for the rest of the row. The grid leaves 2015's columns 1 and 9 empty.
  Both tokens sit in `#p5-datagrid-residue`, an `iladub:CandidateConcept` with status `proposed`,
  whose `surfaceText` holds them. Nothing is fabricated and nothing is lost. The reading is still
  unread: a reader places both figures in 2015, because each chains to its neighbour (2014's
  31 Dec, 2016's 1 Jan). The row's own balance identity confirms it exactly:
  `8 237 666 + 18 953 + 71 884 − 1 377 = 8 327 126`.

### 2.2 p5 canton grid (`#p5-datagrid`, 27 × 10, 270 cells): right values, no column identity

- All 270 values match the page, row by row: Suisse, then Zurich through Jura.
- **0 labels.** This is the defect ons and apple were accepted only after repairing: grids that
  asserted entries with no column identity (see their 2026-09-18 rationales in
  `tests/corpus-manifest.ttl`). No boxhead question has been recorded for a 10-column canton grid.

### 2.3 p6 (`table2` … `table10`): every entry row read, but the boxhead is carried as data

- All 32 entry rows (Total, 7 regions, 24 cantons) and their 9 values match the page. That
  includes `Tessin`, which the 09-19 loop repaired.
- **`p6 … table2` asserts 6 header words as `tab:EntryCell`s** → [[R293]]: `Cantons`,
  `dépendance`, `dépendance des`, `des jeunes 1`, `personnes`, `âgées 2`. These are lines 2–4 of the
  printed four-line boxhead. They are the same class as [[R289]] on cbh (header ink carried as
  data).
- **Every p6 table's labels are the boxhead's first line only.** Column 0 is `Grandes régions`
  (missing `Cantons`). Columns 7 and 8 are BOTH `Rapport de`, so the two dependency ratios carry
  identical column identity and cannot be told apart.
- A p6 boxhead recording exists (`readings/boxhead/README.txt`: "p6 read but NOT carried — the
  page does not adopt"). The labels above come from the band path, not from that recording.

### 2.4 The 09-19 hold reason is fixed; three others remain

The 09-19 reason (one grid spanning two tables) no longer holds: #303 split the grid. What holds
bfs now: [[R293]] (header words asserted as entries, and two columns sharing one label),
[[R294]] (two entries unread), and the canton grid's missing boxhead (§ 2.2). The first two are
misread or unread entries, which is the standard every bfs hold note has used. So this loop
pins no floor.

## 3. Decided, and where

- bfs stays `cor:Unadjudicated` with no floor. Recorded in `tests/corpus-manifest.ttl` (a comment
  after bfs's last reading) and here.
- [[R293]] and [[R294]] were raised in the register (`residues.md`, `residues-open.md`).
- "Strategy review next, not another loop" is the handoff's recommendation, reaffirmed here. It is
  the maintainer's decision and is recorded nowhere else.

## 4. Unverified or assumed

- That [[R293]] and [[R289]] share a seam. Both are a multi-line boxhead's lower lines carried as
  data, but cbh's spill into a roster's `r0`, while bfs's become a separate record table
  (`table2`). Not measured.
- That the canton grid's boxhead can be recorded and disposed (§ 5 item 2). Not run.
- That p6 would carry its recorded boxhead if it adopted a data grid. Inferred from the README
  line, not measured.
- p0 and p4 were not re-read. Their escalations (the press-release masthead, KIND_NOT_SUPPORTED,
  and a chart caption, REGION_TILING_FAILED) are not entries, and ons and apple were accepted with
  the same classes escalated.

## 2b. Where the primaries are

- `tests/corpus-manifest.ttl`: the bfs `cor:reading` block and its hold comments.
- `2026-10-05-r290-two-grids-evidence.md` § 2.3: the per-grid table this loop re-read.
- `2026-10-05-cbh-carried-grid-read.md`: R289's carried-grid read, the method § 2 repeats.
- `readings/boxhead/README.txt`: what is recorded for bfs p5 and p6.
