# The box that covers one line — R178's ruling, and the third instrument correction

**Topic:** [[R178]], ruled and CLOSED. Its own population — 12 orphan word-groups, measured
2026-09-07 after [[R177]] unblinded the prober — turns out to be **two different things**, and only
one of them is R178's subject. 8 of the 12 are ink the reading **did** carry, into a
`tab:cellText` whose `tab:hasBBox` covers only the last of the three source lines it was joined
from. That is a provenance defect at the emitter, not unread ink, and it is raised as [[R181]].
The 4 that remain are captions outside the table proper, which is what R178 said in the first
place.

**Written 2026-09-07**, in the loop that ran action **5a** of
`docs/superpowers/2026-09-07-r179-handoff.md` — an action typed **ASSERTED**: a ruling, with
nothing to build.

**Doc impact: none.**

---

## 0. Classification (CLAUDE.md § Core design principles 8)

**None.** No decision is implemented here. This loop writes a ruling and two register rows; it
adds no code, no shape and no query. [[R181]] will need a classification when it is designed;
this document deliberately does not pre-empt it (§ 4).

---

## 1. What the handoff asked, and why the answer was not the one it offered

`2026-09-07-r179-handoff.md` § 5a put the fork as: *close R178 as "measured, and 12 words across
2 documents does not justify a reading change", **or** split it into two rows with two different
sites.* The row itself argued for the split:

> What is left is genuinely two questions, and they should not be answered by one rule: the
> caption is a *placement* question at the matrix site, the graincorp fragments are a *coverage*
> question at the hierarchical site.

**Neither option is right, and the row's own framing of the second half is refuted.** The
graincorp fragments are not a coverage question. The header tree carried every one of those words
into a label's `tab:cellText`; what it did not carry is a box that contains them. So R178 closes
whole — both survivors are the same caption/banner shape — and the graincorp half leaves the row
entirely, because it was never about ink the reading failed to read.

**The instrument was still lying, a third time.** § 1.1 of
`2026-09-07-the-label-cell-that-cannot-be-found-design.md` records the first correction (111 → 12,
after R177 gave label cells their boxes). This is the second one on the same prober and it has the
same shape: `_covered` decides an orphan by **containment in an emitted cell's bbox**
(`scripts/unbooked_ink_fate.py:54-57`), so ink that a cell's *text* carries but its *box* does not
cover is indistinguishable from ink the reading dropped. R177 fixed the *presence* of the box.
Nothing checked its *extent*.

## 2. The measurement

### 2.1 graincorp-stem p0 — 8 of the 9 are carried text with an under-covering box

The band's header is **three physical lines**, wrapped. Every word of the first two lines is an
orphan; every word of the third is inside an emitted `tab:LabelCell` box:

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_fate.py corpus/ag-trade/graincorp-stem-2026-07-31.pdf 0
page 0: score=0.9575163398692811 asserted=586 escalated=26 | EntryCells=586 LabelCells=17 (no bbox: 0/0)
  b2  UNSUPPORTED_TABLE  ink=612   booked=612   unbooked=0    || entry=586   label=17    orphan=9
      orphans: Friday, 31 July 2026 Date of Grain Unique Slot Loading Date Nomination Time Nomination Date Nomination Time Nomination Date Loading
```

The nine orphans are nine **word-groups**, not nine words, and the joined print above hides where
they break. Their boxes, and the third header line's, read (band 2, `w.top < 90`):

```
'Friday, 31 July 2026'   x0=398.28 top=61.23 x1=447.56 bot=66.51    <- line 1 (a banner)
'Date of Grain'          x0=376.32 top=67.83 x1=409.30 bot=73.11    <- line 2
'Unique Slot'            x0=158.04 top=74.43 x1=187.30 bot=79.71    <- line 3
'Loading'                x0=376.32 top=74.43 x1=396.81 bot=79.71
'Date Nomination'        x0=474.72 top=74.43 x1=516.69 bot=79.71
'Time Nomination'        x0=522.60 top=74.43 x1=565.53 bot=79.71
'Date Nomination'        x0=570.48 top=74.43 x1=612.45 bot=79.71
'Time Nomination'        x0=618.36 top=74.43 x1=661.29 bot=79.71
'Date Loading'           x0=714.12 top=74.43 x1=747.44 bot=79.71
'GC Fin Year'            x0= 14.16 top=81.03 x1= 44.15 bot=86.31    <- line 4, ALL 17 carried
'Reference Number'       x0=158.04 top=81.03 x1=204.87 bot=86.31
'Commencement'           x0=376.32 top=81.03 x1=417.58 bot=86.31
'Received' 'Received' 'Accepted' 'Accepted' 'Completed'  … (top=81.03, bot=86.31 throughout)
```

and the 17 emitted `tab:LabelCell`s carry the **joined** text with a **single-line** box:

```
'Date of Grain Loading Commencement'  ('376.32', '81.03', '417.58', '86.31')
'Unique Slot Reference Number'        ('158.04', '81.03', '204.87', '86.31')
'Date Nomination Received'            ('474.72', '81.03', '497.73', '86.31')
'Time Nomination Received'            ('522.60', '81.03', '545.61', '86.31')
'Date Nomination Accepted'            ('570.48', '81.03', '593.98', '86.31')
'Time Nomination Accepted'            ('618.36', '81.03', '641.86', '86.31')
'Date Loading Completed'              ('714.12', '81.03', '741.48', '86.31')
```

`'Date of Grain Loading Commencement'`'s box is **byte-identical to the word `'Commencement'`'s
own box**. It contains one of the three lines whose text it carries.

Every orphan fragment is present in a carried label's text — measured, not read off:

```
banner in graph:    []
'Date of Grain'  -> ['Date of Grain Loading Commencement']
'Unique Slot'    -> ['Unique Slot Reference Number']
'Loading'        -> ['Date Loading Completed', 'Date of Grain Loading Commencement']
'Date Nomination'-> ['Date Nomination Accepted', 'Date Nomination Received']
'Time Nomination'-> ['Time Nomination Accepted', 'Time Nomination Received']
'Date Loading'   -> ['Date Loading Completed']
```

**8 of the 9 are carried. The 9th, `Friday, 31 July 2026`, is not in the graph at all** — a date
banner above the table, and the only genuinely dropped ink on the page.

**The wrap-join is the RIGHT reading, and that matters for how R181 is framed.** `Date of Grain /
Loading / Commencement` is one column header wrapped over three lines, not a three-level
hierarchy; flattening it to one leaf carrying the joined string is correct. The defect is
localised entirely in the box.

### 2.2 who-wfa p0/p1/p2 — genuinely dropped, and genuinely a caption

```
  b2  UNSUPPORTED_TABLE  ink=98  booked=98  unbooked=0  || entry=77  label=20  orphan=1
      orphans: Year: Month                                      (p0; p1 b2 and p2 b1 identical)
```

One word-group per page. It is not the `Month` column header — that is carried, and the two are
**separate word-groups on the same line**:

```
'Year: Month'  (63.11, 118.71, 124.49, 129.69)   <- orphan
'Month'        (136.37, 118.71, 168.15, 129.69)  <- carried, as a tab:LabelCell with that exact box
```

and the string is absent from the graph:

```
cellText containing 'Year': []
any literal containing 'Year:': []
```

*(Absence-from-graph was measured on p0 only; p1 and p2 were measured through the prober, whose
orphan text is identical on all three pages.)*

### 2.3 Scope of the "nowhere else" claim

The corpus run reports orphan ink on **4 pages of 27** (who-wfa p0/p1/p2, graincorp-stem p0), and
per-page runs above account for every orphan on all four. So graincorp-stem p0 is the **only** page
in the corpus exhibiting the under-covering box.

**That claim is scoped to asserted bands.** `unbooked_ink_fate.fate` skips every region whose
verdict is not `asserted` (`scripts/unbooked_ink_fate.py:88`), so an escalated band with a wrapped
header would not appear. The instrument cannot see it, and this document does not claim it does.

## 3. The ruling — R178 CLOSES

**Measured, and not worth a reading change.** After the correction, R178's genuine population is
**4 word-groups in 2 of 7 documents**:

| what | where | words |
| --- | --- | --- |
| `Year: Month` — the row-axis caption at the matrix site | who-wfa p0, p1, p2 | 3 groups |
| `Friday, 31 July 2026` — a date banner above the header | graincorp-stem p0 | 1 group |

Both are **out-of-table captions**: ink on the page, inside the band, belonging to no row and no
column of the matrix. That is exactly the shape R178 was raised with and predicted — *"small and
caption-shaped"* — and it is now the whole population rather than 25% of it. Two instrument
corrections were needed to get back to the row's first sentence.

Carrying them would mean minting a structure the table does not have: a caption is not a header
node (it spans no columns), not a data cell, and not a row header (it names the axis, not a row).
Inventing one for 4 word-groups is a reading change with the [[R166]] blast radius and no
document demanding it. **The row closes as measured and deliberately not carried.** They remain
booked `escalated` by [[R176]], so the score continues to count them as unread, which is honest.

**What would REOPEN it** — and this is the falsifiable half: a corpus document where out-of-table
caption ink is *load-bearing* rather than decorative (an axis caption that carries the unit, a
banner that carries the as-of date the rows are only meaningful against). Nothing in the present
7 documents does. `Friday, 31 July 2026` is the closest, and it is a print date, not a datum.

## 4. What is raised instead — [[R181]]

**A `tab:LabelCell` whose `tab:cellText` is a wrap-join across N source lines carries a
`tab:hasBBox` covering only 1 of them.** Measured at 8 of 17 labels on graincorp-stem p0 (§ 2.1).

Not fixed here, for three reasons, each of which is a scope boundary rather than a preference:

1. **It changes emitted geometry**, so it needs the corpus diff and the ~14-minute suite that
   [[R179]] paid for — an executing loop, not a ruling.
2. **The site is not yet established.** `headers.py:458` builds a `HeaderNode` from one
   `SourceCell` and takes `x0/top/x1/bottom` from it; `cells._cell_from` (`cells.py:96-103`)
   already unions its words' bounds correctly. So the joined text and the single-line box do not
   come from the same place, and *which* site joins the three lines is unmeasured. Naming it here
   from reading would be exactly the CLAUDE.md § Plan authoring discipline rule 2 failure.
3. **No shape enforces box-covers-text in either direction.** `tab:WrappedCellShape` is
   bbox ⇒ non-empty text; `tab:EntryCellPhysicalShape` and [[R179]]'s
   `tab:LabelCellPhysicalShape` require the box's **presence**. Whether the remedy is an emitter
   fix, a containment shape, or both is the design question R181 opens.

`rowrole.py:182` — named in the R179 handoff's *Unverified* section as a **row**-header analogue
of this (`replace(nodes[tgt], text=merged)` keeps the target's box) — is a **sibling site, not the
same one**. R181's measurement is on column headers. Whether the two are one defect is open.

## 5. What this loop deliberately did NOT do

- **Did not split R178.** The row asked for a split into a placement question and a coverage
  question; the coverage question does not exist. Splitting would have carried the refuted framing
  forward into a new row.
- **Did not design or implement R181.** § 4.
- **Did not fix the prober.** `_covered`'s containment test is what made both corrections
  necessary, and a third confound of the same family is plausible (a cell whose box covers text it
  does *not* carry would go unnoticed in the other direction). Not raised as a row: no instance is
  measured, and [[R139]]'s census is the precedent for not raising an instrument row on suspicion.
- **Did not re-run the 27-page corpus driver.** Four per-page runs (~20 s each) account for every
  orphan the last corpus run reported, at the same commit's behaviour; a 9-minute re-run would
  restate them.
