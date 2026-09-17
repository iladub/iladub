# Measurement — the false-positive denominator ([[R47]], [[R77]])

**Serves:** prog:criterion:tab:04 — [[R77]] is one of its three blockers

**Date:** 2026-09-17 · **Tree:** branch `the-false-positive-denominator`, cut from `main` at
`e85aefc`, working tree clean · **Runner:** `./.venv/bin/python` · **Class:** evidence.

**Doc impact: none.**

This loop was handed the previous handoff's § 5a as its first action, typed PROPOSED. It ran it,
and § 5a is **refuted twice over** — its prescribed remedy cannot be built, and the hole it was
meant to close does not exist. What replaced it is a corrected census at the scope that can
actually contain the true positives.

---

## 1. § 5a's prescribed remedy CANNOT BE BUILT

`2026-09-17-section-total-is-in-its-own-band-handoff.md` § 5a prescribed, verbatim:

> replace the index-based region↔band mapping with a y-overlap match (a region's band is the one
> whose `[top, bottom]` it falls inside), re-run, and report `true/false` with **zero** pages
> skipped.

There is nothing to overlap *with*. `RegionReport` (`compile.py:547-577`) carries exactly
`kind, verdict, cells, reason, anchor, ascii, table_uri, header_reading, tokens_asserted,
tokens_escalated` — **no y-extent and no band reference**. `anchor` is a class IRI string
(`str(TAB.RecordTable)` etc., e.g. `compile.py:955-956`), not geometry. `CompilationReport`
(`compile.py:581-589`) carries `score, regions, graph, asserted, escalated` and never exposes the
band list it used.

The y-extent lives on the **band** side only (`Band.top`/`.bottom`, `bands.py:15-34`), which is why
every y-test in the repo is line→band and never region→band (`grid_band_overlap_census.py:42`,
`ledger_contract_census.py:52`).

**The prescribed mechanism was un-writable at the moment it was prescribed.** It was typed PROPOSED,
ordered to be run first, and cost minutes to refute — CLAUDE.md § "The handoff's next action is
TYPED" working exactly as intended, for the second consecutive loop.

## 2. § 5a's PREMISE is false — there is no correspondence hole

The index correspondence § 5a treats as defective is a **documented contract**: `compile.py:845`
iterates `for idx, band in enumerate(bands)` over the exact list `page_bands` returned
(`compile.py:823`), and `compile.py:842` states *"Every branch appends exactly one report per band"*.
`document.py:1521` repeats it for document scope: *"region report index IS band index"*.

Measured at HEAD on the six pages § 5a called unmeasurable, plus cbh p0 as control, at **both**
`datagrid_fallback` settings:

```
apple-fy2026q3-stateme  p0 fallback=True  bands=  3 regions=  3  ALIGNED
apple-fy2026q3-stateme  p1 fallback=True  bands=  3 regions=  3  ALIGNED
apple-fy2026q3-stateme  p2 fallback=True  bands=  8 regions=  8  ALIGNED
bfs-population-bilan-2  p5 fallback=True  bands= 15 regions= 15  ALIGNED
ons-index-of-services-  p7 fallback=True  bands= 16 regions= 16  ALIGNED
ons-index-of-services-  p8 fallback=True  bands=  9 regions=  9  ALIGNED
cbh-stem-2026-08-03     p0 fallback=True  bands= 10 regions= 10  ALIGNED
```

| page | § 5a reported | measured at HEAD |
| --- | --- | --- |
| apple p0 | 8 bands, 3 regions | **3 / 3** |
| apple p1 | 8, 3 | **3 / 3** |
| apple p2 | 8, 10 | **8 / 8** |
| bfs p5 | 15, 17 | **15 / 15** |
| ons p7 | 16, 18 | **16 / 16** |
| ons p8 | 9, 11 | **9 / 9** |

**Not one of the six mismatches reproduces.** The measurement hole was in the instrument, not the
pipeline.

## 3. The instrument's defect, identified: a PRE-MERGE band source

`page_bands` (`compile.py:377`) is not `detect_bands` (`bands.py:37`). It re-segments, attaches
rules, re-extracts ruled cells, and **may merge a run of bands into one index**
(`compile.py:398-407`). Raw `detect_bands` output therefore does not index-align with region
reports; `page_bands` output does.

Testing the prior figures against both sources:

```
document                 pg  prior   raw  page_bands  explains?
apple-fy2026q3-statemen   0      8     8           3  RAW matches prior
apple-fy2026q3-statemen   1      8     8           3  RAW matches prior
apple-fy2026q3-statemen   2      8     8           8  both match
bfs-population-bilan-20   5     15    15          15  both match
ons-index-of-services-2   7     16    16          16  both match
ons-index-of-services-2   8      9     9           9  both match
cbh-stem-2026-08-03       0     10    10          10  both match
```

apple p0/p1 is the only discriminating case, and it discriminates cleanly: raw `detect_bands`
returns the prior loop's 8, `page_bands` returns 3. **The prior census counted pre-merge bands
against post-merge regions.** Its `−5` mismatch is that, exactly.

**The `+2` half is NOT established.** Extra regions beyond one-per-band are appended only on
datagrid-**adopting** pages (the grid region at index `len(bands)`, plus a `DATAGRID_RESIDUE`;
`compile.py:1591-1604`), which is a document-scope phase — consistent with the prior census having
run at document scope, but the prior script was never committed (`e85aefc` landed evidence, handoff
and register rows only), so this stays a **reconstruction, not a finding**. What is measured is that
`+2` does not occur at page scope under either fallback setting.

**The committed instrument carries the same construct, and it is DEAD there — recorded because this
loop first suspected otherwise.** `scripts/grid_band_overlap_census.py:38` refuses a page on
`len(rep.regions) != len(bands)`, the identical skip rule. But it calls
`compile_tables(..., validate_shapes=False, datagrid_fallback=False)` at page scope (`:31`), and
extra regions are appended only by the datagrid fallback (`compile.py:1427`) or by document-scope
adoption (`compile.py:1591-1604`) — neither reachable under those options. Its counts cannot
disagree, so the branch never fires and its published figures are unaffected. It also takes its
bands from `page_bands` (`:32`), not `detect_bands`, so it does not share the § 3 defect either.
**A construct that looks like a defect is not one until its call site is measured.**

## 4. Scope is the population question, and the first corrected pass got it wrong

A page-scope census over all 27 pages returned `PAGES SEEN 27 SKIPPED 0 MATCHES 2`, both FALSE,
`true=0`. That is a **defect in that census, not a result**: on cbh p0 the four roster regions are
`UNSUPPORTED_TABLE`/**escalated** at page scope, so a filter of `verdict == "asserted"` cannot see
them. They are asserted only at **document** scope, where section repair adopts
`repaired_bands ((0,1),(0,3),(0,5),(0,7))` (`document.py:1565`, semantics `:227-232` — only ADOPTED
bands ever appear).

**A census that cannot contain the true positives cannot measure a false-positive rate.** Recorded
because it is the same page-vs-document scope trap this corpus has sprung before, and it was caught
by the true count going to zero rather than by reading the code.

## 5. The two surviving false positives are ORDINAL-column coincidences

Both reproduce, and both are the same shape. who-wfa p0/p1 region[4] (`RECORD_TABLE`, asserted):

```
  c0: ['1:', '1:', '1:', '1:', '1:']
  c1: ['2', '3', '4', '5', '6']   <-- the matching column, sum 20, 5 members
  c2: ['14', '15', '16', '17', '18']
```

`c1` sums to exactly 20, and the immediately-following band prints the token `20` — itself an
ordinal, continuing the `c2` sequence (`14–18` on p0, `38–42` on p1). **The sum of a
consecutive-integer index column equalling an index value printed below it.** cbh's true positives
sit on a measure column (col 13).

Prior's other two who-wfa false positives (`value=17`, `table_band=3`) have **no counterpart**: at
the correct indices region[3] is `c1=50(5)`, and no `17` appears in its following band. They are
band-source artifacts of § 3. **Prior's `false=4` is 2 reproducible instances plus 2 artifacts.**

**NOT ADOPTED, deliberately.** An ordinal-column filter is keyed on what the column *is* rather than
on the cbh-fitted 1-line shape — but it stands at n=2 on one document, which is the same evidentiary
footing the 2026-09-17 evidence § 10 refused for the 1-line/6-line discriminator. It is carried as a
recorded flag in the corrected census so it can be **falsified corpus-wide**, not fitted. An
incidental datum already weakens the 1-line rival: 1-line following bands exist outside cbh
(who-wfa band [6], both pages) and simply carry no numerics.

## 6. Independent confirmation of [[R47]]'s window gate

`_confirm_section_total` reads the table's own last row below its closing rule
(`document.py:1136-1151`) — *inside* the band. cbh's totals are in the *following* band. Arrived at
from the API surface rather than from R47's own evidence, and agreeing with it.

## 7. What this does NOT establish

- **The `+2` half of the prior mismatch** — reconstruction only; the script was never committed (§ 3).
- **The ordinal-column discriminator** — n=2, one document, recorded to be falsified (§ 5).
- ~~Whether prior's `true=4` reproduces at document scope~~ — **ANSWERED in § 8: it does, exactly.**
- **Why vessel row 26 is `unplaceable`** — the other half of [[R243]], untouched, as before.
- **Nothing here designs a remedy.** The § 5c fork (widen `_confirm_section_total`'s window vs
  build R47's trailing-strip peel/carry) remains named and unchosen.
- **THE CENSUS REPORTS MATCHES BUT NOT ITS OWN OPPORTUNITY POPULATION — stated as a limitation of
  this loop's instrument, by the loop whose subject is exactly that.** It prints every
  (asserted table, following band) pair that *matched*, and never the number of pairs it
  *examined*. A false-positive count without the population it was drawn from is the same
  unaudited-denominator claim this loop was convened to repair — one level up, in the instrument
  rather than in the pipeline. It is recorded rather than fixed because adding it costs a second
  whole-corpus pass (measured: ~72 s/page, 27 pages), and the figure it would refine is not the
  figure the handoff asked for. **Any remedy justified on "only N false positives" must obtain
  this denominator first.**
- **The run prints matches only at exit**, so a memory kill discards them (four such kills are on
  this repo's record for corpus runs). Not a finding; a property of the evidence behind §§ 4 and 8.

## 8. The corrected census — `true=4 false=2`, ZERO pages skipped

Document scope (`compile_document(path, validate_shapes=False)`), all 7 documents, all 27 pages:

```
[cbh-stem-2026-08-03            ]  1 pages  repaired=4  adopted=0   29.1s
[graincorp-capacity-2026-08-04  ]  1 pages  repaired=0  adopted=0   18.1s
[graincorp-stem-2026-07-31      ]  3 pages  repaired=0  adopted=0  217.4s
[apple-fy2026q3-statements      ]  3 pages  repaired=0  adopted=1   55.7s
[bfs-population-bilan-2023      ]  7 pages  repaired=0  adopted=1   63.4s
[ons-index-of-services-2026-02  ]  9 pages  repaired=0  adopted=2   49.2s
[who-wfa-boys-zscore-0-5        ]  3 pages  repaired=0  adopted=0   52.4s

PAGES SEEN 27   SKIPPED 0   MATCHES 6
NO PAGE SKIPPED -- the denominator is complete.

cls   document                   pg  tbl  nxt       value  col  mem  ordinal nxt_ln
TRUE  cbh-stem-2026-08-03         0    1    2     374,904   13   10    False      1
TRUE  cbh-stem-2026-08-03         0    3    4     737,289   13   16    False      1
TRUE  cbh-stem-2026-08-03         0    5    6     660,363   13   14    False      1
TRUE  cbh-stem-2026-08-03         0    7    8     178,708   13    5    False      1
FALSE who-wfa-boys-zscore-0-5     0    4    5          20    1    5     True      6
FALSE who-wfa-boys-zscore-0-5     1    4    5        20.0    1    5     True      6

TOTALS  true=4  false=2
```

Three pages adopt a datagrid (`apple` 1, `bfs` 1, `ons` 2), so `len(regions) != len(bands)` there by
design; the `anchor == str(TAB.DataGrid)` filter excludes those regions and **no page is refused**.

The four true positives land on **column 13** with member counts **10/16/14/5** — the same operands
the 2026-09-17 evidence § 7 obtained by a different route, and the same member sets the grid path
found independently (`aggregates {20:10, 42:16, 63:14, 74:5}`, `test_datagrid.py:611`). **Three
independent paths agree on the operands.**

**§ 5a's PREDICTION IS REFUTED.** It predicted the six unmeasured pages would *"add more false
positives than the measured ones did"*, and that if it held, *"the honest product of the next loop is
a recorded refusal, not a remedy."* They add **zero**. The surface did not grow — it **shrank**, from
prior's `false=4` to `false=2`, because two of prior's four were the § 3 band-source artifacts. The
figure prior called *"a floor, not a count"* was not a floor. **The refusal § 5a anticipated is
therefore not this loop's product**, and a remedy is not blocked by the false-positive surface.

## 9. TWO rival discriminators separate all six instances perfectly — which is why NEITHER may be adopted

| discriminator | on the 4 TRUE | on the 2 FALSE | separation |
| --- | --- | --- | --- |
| summed column is ORDINAL (consecutive integers) | 0 of 4 | 2 of 2 | perfect |
| following band has 1 line (vs 6) | 4 of 4 at 1 line | 2 of 2 at 6 lines | perfect |

The second is the cbh-fitted shape the 2026-09-17 evidence § 10 already refused to key a rule on,
*"fitted to this page by construction"*. The first is better founded — it is keyed on what the
column **is** (an index is not a measure) rather than on a page's typography. But both fit the same
six instances with zero errors, and **a corpus that cannot distinguish two rival rules cannot
justify either.** The evidence available for the better candidate is precisely the evidence already
ruled insufficient for the worse one.

**Neither is adopted here.** Recording the symmetry is the finding: it converts *"a discriminator is
visible in the data"* from an argument **for** adopting one into an argument for adopting **neither**
until the population grows or a principled ground is supplied.
