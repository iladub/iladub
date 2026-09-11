# Handoff — etkl:02 waits on R166: the 1.0000 is a misread header

**Topic:** etkl-02-waits-on-r166
**Serves:** prog:criterion:etkl:02 — continues `2026-09-11-etkl-02-graincorp-capacity-handoff.md`
and refutes its 5c.
**Date:** 2026-09-11. **Loop shape:** measurement only. No spec, no compiler change. The session
went past the 50K originating floor while measuring (about 60K working tokens when this was
written), and the maintainer chose to record the finding and stop. **Doc impact: none**.

Part 5 was written first. It is graded per action, because the session was past the floor.

## 5. The next concrete action

### 5a. ASSERTED: etkl:02 is not a contract loop. It waits on R166

`tests/arc-manifest.ttl` now carries `prog:criterion:etkl:02 prog:blockedBy "R166"`, with the
measurement written above the block. After the edge, the strip reads `frontier 14  ready 8`; before
it, `frontier 13  ready 9`. The next loop that moves etkl:02 closes R166 for this document. It is
not an authoring loop for `cor:contract`/`cor:terms`/`cor:shapes`. The earlier handoff's three-step
route still stands, but only after the header is read correctly. Its step 3, the maintainer's read
against the page, would fail today at the first row.

### 5b. PROPOSED: grid donation repairs this document's header

The real header line (`Year | Elevation Period | Mackay | Gladstone | Fisherman Islands |
Carrington | Port Kembla | Geelong | Portland`) is a band of its own, and the compiler ignores it as
`NON_TABLE` with the reason `fewer than 2 lines`. That is the shape R201's resolved arm addresses:
a header comes from a band the author ruled. The plan exists and has not been executed:
`plans/2026-09-11-grid-donation.md`.

The prediction is that executing that plan carries the port names onto this table. **It is not
measured**: `grep -i capacity` over that plan returns nothing. **Refuted in minutes** by checking
whether the donation relation admits this donor. The donor is a one-line band that the kind
judgement already disposed as `NON_TABLE`. Also, the header names one label per port while the body
carries two columns per port: a tonnage column and an unlabelled Y/N column. A donor with fewer
labels than the recipient has columns may be refused by design. If it is, capacity needs its own
arm under R166, and the spec says so.

### 5c. PROPOSED: once the header is right, the contract is a design question, not a 20-line file

Grounding picks a field in two ways only (`src/iladub/ground.py`):

- `exact_field`, which matches the column's header text against a field name;
- `marker_field`, which is for section markers only (R207).

Here the ports are **column headers**, not cell values, and they are the page's main dimension. A
contract with one field per port (`gc:mackay`, `gc:gladstone`, …) would ground, but it would do so
by flattening a dimension into field names. CLAUDE.md §2 forbids that. The honest contract needs a
header label to ground as a member of a port scheme, and no path in `ground.py` does that today. The
spec's first question is whether R207's arm extends to column headers. **Refuted or confirmed by
reading `ground.py` against the repaired graph.** It cannot be settled before 5b.

## 1. Where the primaries are

| what | where |
| --- | --- |
| the edge and its measurement | `tests/arc-manifest.ttl`, the comment above `prog:criterion:etkl:02` |
| R166's census row for this document | `specs/2026-09-10-the-header-is-assumed-design.md`, census row 2: "NO — a data row" |
| the grid donation plan | `plans/2026-09-11-grid-donation.md` |
| the source page | `corpus/ag-trade/graincorp-capacity-2026-08-04.pdf` (gitignored; `scripts/fetch_corpus.py`) |

## 2. What was measured this session

These are on `512f82e`, and the edge is on this branch.

- The score re-measured at 1.0000 (the earlier handoff's 5b holds), with the same five regions.
- **The carried header is the first data row.** Running `table_records(compile_document(pdf).graph)`
  gives 26 records. Their header paths are
  `{'August 2nd Half': 26, '0': 103, 'N': 104, '10,000': 26, 'Y': 78, 'On Application': 26,
  '14,000': 26, '2025/26': 1}`. No record carries a port name. The page has 27 data rows: 26 are
  carried and 1 is consumed as the header.
- **The Year row group is lost as well.** `2025/26` is a header label, and only `p0 table3-r3`
  carries `2026/27`. The other 2026/27 rows carry no year.
- **The page has hidden text that the maintainer's read should know about.** Every dark (navy) cell
  on the rendered page looks empty, but `pdftotext -layout` reads a `0` glyph in it. There is one
  exception: Fisherman Islands, 2025/26, September 1st Half carries no glyph at all. So a human
  reads an empty cell, and the machine reads `0` in all but one of them. Both are consistent with
  the Y/N flag. Nothing in the carried grid tells a drawn `0` from an invisible one.
- **Neither class has a register row.** No residue in the index mentions wide tables or headers as
  dimensions (`grep -iE "pivot|crosstab|wide table|dimension"`), nor hidden or invisible text.

## 3. What was decided, and where that decision is recorded

- **Record it and stop, rather than override the floor** for an R166 spec. The maintainer chose
  this in session. The record is the edge, its comment, and this file.
- **The edge is R166, not R201 or R203.** R166 is the row whose symptom this is, and the row whose
  census names this document. R201 and R203 are its successors on the donation route. Whether they
  cover this document is 5b, which is unmeasured.

## 4. Unverified or assumed

- **The tracked manifest has not been put through its own membrane in the suite.** That is R209. It
  was validated by hand this session, with the edge in place: `validate_manifest` on
  `tests/arc-manifest.ttl` returned `conforms: True`, and `environment_refusals` returned `[]`.
- `test_no_stuck_verdict_is_computed_anywhere` failed on this branch's first name,
  `etkl-02-blocked-by-r166`, because the strip renders the branch name. Raised as R210, and the
  branch was renamed.
- The earlier handoff (PR #206) was still waiting on CI when this was written. Its 5c is refuted
  here, not edited there: that file is Evidence.

## 6. Addendum: 5b measured (a fresh session, 2026-09-11)

Appended, not edited: parts 1-5 above stand as written. This session started fresh on `536b0d3`
and ran only measurements. The record is [[R211]], raised here.

### 6a. ASSERTED: 5b is refuted as written. Grid donation refuses this donor, and the spec already said so

Of the donation relation's four positive facts, three hold on graincorp p0 band 2 → band 3: it is
earlier on the page, it is wholly drawn (10 rule x's), and the page datagrid refuses its line
(page line 3) `every-measure` (`scripts/donor_header_criterion.py`). The fourth, `same_ncols`,
fails: 9 against 16. Part 5b called this "unmeasured" because `grep -i capacity` over the plan
returned nothing. The refusal is recorded in the spec the plan was written from:
`specs/2026-09-10-the-grid-the-author-drew-design.md` census row 2 and § 3(c), where this page is
the relation's null control. The grep searched the wrong file.

### 6b. ASSERTED: the refused donor is a coarser partition of the recipient, not a wrong one

Every x drawn on band 2 is also drawn on band 3 (exact, at `_rule_boundaries`' 2dp), and each of
the 7 port labels spans exactly 2 of band 3's columns. The spec's reason for the control, *"a
9-column header onto a 16-column table"*, is true of a donation that keeps equal counts, and says
nothing about one that respects the spans. Merging the bands does not help either:
`classify_hierarchical` on `merge_bands(bands, 2, 3)` gives each port ONE column and leaves every
Y/N column unheaded, because the merge carries no drawn rules. Full figures in R211.

### 6c. PROPOSED: the next etkl:02 loop is a spec for a spanning-donor arm, and it starts with a census

The prediction to run before anything is designed: *across the corpus, every (earlier, later)
ruled-band pair on a page whose drawn x's satisfy `drawn(donor) ⊂ drawn(recipient)` (strict) is a
spanning header.* It is refuted in minutes by enumerating those pairs with `_rule_boundaries` over
the 7 documents and reading each one. If graincorp is the only pair, the arm has one positive
and no control. That is R211's second question: the spec must build a synthetic negative rather
than borrow a control from the page it is trying to admit. If other pairs exist and any is not a
header, the subset relation is not sufficient, and that census is the spec's § 2.

The hidden-glyph finding (part 2, fourth bullet) still has no register row. This session did not
raise one.

## 7. Addendum: 6c run (the same fresh session, 2026-09-11)

### 7a. ASSERTED: 6c is refuted. A strict subset of drawn rules is not sufficient

The census walked every page of the 7 corpus documents: `page_bands`, then `_rule_boundaries` at
2dp on each band with ≥ 3 x's. It found 14 ruled bands and **8 strict-subset pairs**
(`drawn(earlier) ⊂ drawn(later)`, same page), not one:

| page | donor | recipient(s) | ncols | donor line 0 | a header? |
| --- | --- | --- | --- | --- | --- |
| graincorp-capacity p0 | band 2 (1 line, NON_TABLE) | band 3 | 9 → 16, spans `1,1,2,2,2,2,2,2,2` | `Year \| Elevation Period \| Mackay \| …` | yes |
| bfs p6 | band 3 (1 line, NON_TABLE) | bands 4, 5, 6, 8, 9 | 3 → 9, spans `7,1,1` | `Total 8 962 258 … \| 32.9 \| 31.8` | no, a data row |
| bfs p6 | band 7 (1 line, NON_TABLE) | bands 8, 9 | 3 → 9, spans `7,1,1` | `Zurich 1 605 508 … \| 31.4 \| 27.5` | no, a data row |

The two bfs donors are the 3-column-ruled data rows that the grid-donation spec § 2.2 already
names as straddling every candidate grid.

### 7b. ASSERTED: R203's licence separates them, 1 against 7

The page datagrid's verdict on each donor's line 0, re-identified by ink as
`scripts/donor_header_criterion.py` does:

```
graincorp-capacity p0 band2: page-line=[3]  datagrid: refused HeterogeneousColumn/every-measure
bfs p6 band3:                page-line=[7]  datagrid: body row
bfs p6 band7:                page-line=[22] datagrid: body row
```

So a relation of *strict subset of drawn rules* AND *R203 licence* admits graincorp and refuses
all 7 bfs pairs. That answers R211's second question: the arm does **not** lose its control, and
the corpus supplies 7 negatives, none of them synthetic. What it does not answer: **all 7 are
refused by the licence, and none by the subset clause.** The subset clause has no negative of its
own in this corpus, and its only positive is the page it was invented for. The spec must say that,
and its synthetic fixture should aim at the subset clause (a donor that passes the licence and is
not a coarsening).

### 7c. PROPOSED: the spec can now be written, and its first open question is the leaves

The relation is measured on 8 corpus pairs. What remains is the reading: parent = donor label
spanning its interval, leaves = the recipient's columns inside it. Graincorp's leaves carry no
printed label (a tonnage column and a Y/N column per port), so §7 allows a spanned parent over
unlabelled leaves and nothing invented. Whether `holon.py`'s record-region emitter and grounding
(`exact_field`) can carry an unlabelled leaf under a labelled parent is **unmeasured**. It is
refuted or confirmed by reading `assert_record_region` and `ground.py` against a hand-built
two-level region, and that is the spec's § 2, before any design.

One discrepancy, not chased: this census counts only **3** equal-set pairs, while grid donation
fires on 5 bfs p6 bands with donor band 2. The census compares drawn sets and donation compares
counts plus tiling, so the two populations need not agree. It is recorded here only so that nobody
reads the 3 as a contradiction of the 5.
