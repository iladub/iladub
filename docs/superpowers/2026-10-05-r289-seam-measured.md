# R289 and R293 are two seams, not one: the strategy review's subject is re-ruled to R289 (2026-10-05)

**Serves:** prog:criterion:etkl:03 — cbh's acceptance. The strategy review ruled R74 out of it, which leaves R289 as cbh's only blocker. This note measures R289's seam.

**Topic:** r289-seam · **Date:** 2026-10-05

**Doc impact: none.**

Read-only measurement plus two maintainer rulings. No `src/` change. Written at about 62K working
tokens, past the 50K originating floor, so part 5 is graded per action. The spec belongs to a fresh
session.

## 5. Next concrete action (written first)

1. **ASSERTED: in a fresh session, write the R289 spec** from § 2.1. The cause is measured, not
   predicted: `vocab/queries/header-body-split.rq` takes `MIN(?s_col)` over columns, and on every
   cbh roster the columns whose header reaches one line lower (c5, c18) are out-voted by the
   columns whose last label sits one line higher.
2. **PROPOSED, and its prediction must be RUN before the spec commits to it: "use MAX instead of
   MIN" is not the fix.** The graincorp-stem control (§ 2.3) has columns with `s_col` = 23, 53 and
   58 beside the ones that set its correct split of 3 or 4, so MAX would put most of that body into
   the header. The prediction is that any column-aggregate rewrite of the query either regresses
   graincorp-stem or needs a tuned threshold. Under CLAUDE.md § 8 ("one geometric attempt, then
   NEURAL") the typed split *is* the geometric attempt, so the spec's default arm is to ask the
   shipped BAML boxhead reader how many header lines the band has, and let an oracle dispose the
   answer. **Measure first** whether the hierarchical path (`compile.py:1699 classify_hierarchical`)
   can consult a boxhead reading at all. Today only the record path does (`compile.py:455`
   `_header_lines_decision`). Also measure what oracle could refuse a split that leaves `Accepted`
   in the body. A cell-type witness cannot, because `Accepted` and `Completed` are Text in Date
   columns, which is exactly why they produce no `s_col`. The 0.8 pt rule overhang is NOT the
   cause: `_hrule_split` is never reached, because the query answers.
3. **ASSERTED: R293 stays registered as its own subject**, unchanged by this loop (§ 2.2).

## 1. Goal

The strategy review (this session, with the maintainer) chose R289 + R293 as one subject, on the
handoff's unmeasured premise that they share a seam (`2026-10-05-bfs-hold-reread.md` § 4). The
first step was to measure that premise.

## 2. Findings (measured on `main` `81a2ca6`, `src/` identical at `4fe9209`)

Each `compile_document` run was traced by wrapping the watched functions and returning their real
results unchanged. Runs were serial, one document per process, with readings replayed. The traces
reproduce bfs 0.9021428571428571 and cbh 1.0. The scripts were scratchpad-only and are not
committed. Spot-checked in this session: `compile.py:455-463`, `holon.py:206-208` and
`header-body-split.rq:31`.

### 2.1 cbh (R289): the typed split's MIN chooses the row

- The header and the body share one band. `classify` calls it `UNSUPPORTED_TABLE` ("header has 1
  words but 16 columns"). It then goes `compile.py:1699 classify_hierarchical` →
  `hierarchical.py:38 header_body_split` → `header-body-split.rq` `MIN(?s_col)`.
  `resolve_ruled_header_rows` returns None, so `compile.py:1792 assert_hier_region` mints the cells.
  The same holds in both passes (`p0#htable1/3/5/7`, then `p0/r2`).
- The trace for GERALDTON:

  ```
  [header_body_split] band 18L 65.4-199.1 L0='GERALDTON' ncols=20 -> split=7 (rq=7; None=>_hrule_split)
     per-column (col, D, s_col): [(0,'Quantity',7), (3,'Date',7), (5,'Date',8), (8,'Date',7), (10,'Date',7),
                                  (12,'Date',7), (13,'Quantity',7), (14,'Quantity',7), (18,'Date',8)]
     line7 [113.5-119.5] BODY Accepted Accepted Completed Completed
  ```

  KWINANA has split 4 (c5 and c18 vote 5), and ALBANY has split 5 (c5 votes 6). The same shape
  holds on every roster. In the `p0/r2` pass the splits are 2/2/2/2.
- c4 and c19 contribute no `s_col`. That is presumably because their modal type is Text, which was
  not measured.

### 2.2 bfs (R293): the boxhead is a band of its own, and the record path keeps at most one header line

- `bands.py:73 detect_bands` cuts at any gap larger than 1.8 × the median positive gap. On p6 that
  median is 3.441, so the threshold is 6.194. The gaps inside the boxhead are 2.30, 0.97 and 0.97,
  but the gap from `âgées 2` (bottom 127.5) to `Total` (top 136.4) is 8.92. Band 2 is therefore the
  four-line boxhead alone, with no body.
- `classify` → `RECORD_TABLE`. The recorded reader answers `header_lines=3`. `compile.py:463` maps
  any answer above 1 to 1, as spec § 10.6 designed, and `holon.py:207` refuses anything outside
  {0, 1}. Rows 1–3 are minted as entries.
- `table3`…`table10` take their labels from `donation.offer` (donor band 2), which passes donor
  row 0 only. That is why c7 and c8 are both `Rapport de`.
- The same detached-boxhead cut happens on p5's canton grid (`p5#htable8`, 3 lines, all text, so
  `_hrule_split` returns 1). The page's adoption drops it from the final graph, so it is hidden.

### 2.3 Controls

- **cbh: graincorp-stem p1, same path, header kept correctly.** `split=3`, per-column
  `[(3,'Quantity',23), (7,'Date',3), (8,'Date',3), (9,'Date',23), (11,'Date',23), (16,'Quantity',3)]`.
  Its lowest header line spans the columns that set the MIN. On cbh, the lowest line has cells only
  in c4/c5/c18/c19, and none of them sets the MIN. That is the difference that flips the outcome.
  The control also shows MIN is load-bearing (§ 5 item 2).
- **bfs: no control.** The record path cannot keep more than one header line. In the corpus
  readings, 6 boxhead answers are `0` and 1 is `3`, which is this one.

### 2.4 Verdict

**DIFFERENT seams.** They share no function. cbh's cause is a typed `MIN` split inside a band that
holds both header and body. bfs's causes are a gap-based band cut that strands the boxhead, then a
one-line header cap on the record path. Only the symptom is shared: boxhead ink is minted as
`tab:EntryCell`.

## 3. Decided, and where

- **R74 does not stand between cbh and acceptance.** Ruled by the maintainer and recorded as a
  `cor:adjudication` appended to `tests/corpus-manifest.ttl`. cbh's only blocker is R289.
- **The subject is re-ruled from "R289 + R293 as one" to R289 alone**, after § 2.4 refuted the
  premise. The maintainer chose it over R293 and over two sequenced loops. It is recorded here.

## 4. Unverified or assumed

- Why c4 and c19 produce no `s_col`.
- What `header_body_split` would return if bfs's boxhead were joined to its body.
- Whether 3 or 4 is the right header-line count for the bfs p6 reading.
- Whether the hierarchical path could consult a boxhead reading (§ 5 item 2).

## 2b. Where the primaries are

- `docs/superpowers/residues-open.md`, rows R289 and R293.
- `docs/superpowers/2026-10-05-cbh-carried-grid-read.md`, R289's carried-grid read.
- `docs/superpowers/2026-10-05-bfs-hold-reread.md`, R293's re-read.
- `vocab/queries/header-body-split.rq`, `src/iladub/etkl/hierarchical.py`, and
  `src/iladub/etkl/compile.py` `_header_lines_decision`.
