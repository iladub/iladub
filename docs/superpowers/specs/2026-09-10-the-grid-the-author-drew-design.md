# Spec — the grid the author drew: R201's fork resolved, and the merge arm refuted

**Residue:** [[R201]] (`docs/superpowers/residues-open.md`), the three-arm design fork left by
`docs/superpowers/2026-09-10-the-header-is-assumed-handoff.md` § 5b.
**Written 2026-09-10**, off `93fa7ce`, branch `r201-the-grid-the-author-drew`.

**Doc impact: none.** No published term changes; the instrument and the census are evidence.

---

## 1. The fork, and the thing all three arms were missing

R201 left three arms, none costed: **(1)** escalate the record-table branch where the label row
carries no evidence; **(2)** merge the page's bands and re-enter classification from the top;
**(3)** extend the carriage seam so a record-table assertion can mint a reading.

They are not three answers to one question. They are three *consumers* of a primitive that does not
exist: **a decidable, threshold-free relation that says "these bands are one table."** Arm 2 would
use it to choose the run; arm 3 to choose whose header carries; arm 1 is what is left when it does
not hold. [[R166]]'s spec § 3 proved no **in-band** signal separates a data row from a header row,
so the primitive must be cross-band or the reading is NEURAL (CLAUDE.md §8).

This spec measures whether the author's own drawn column rules supply it. They do, on 5 of the 12
bands, with a **unique** donor and **no false donor on this corpus** — and the measurement also
refutes arm 2 outright.

## 2. Arm 2 is REFUTED on the instance it was raised for

Every figure here is from `corpus/gov-stats/bfs-population-bilan-2023.pdf` page 6 at `93fa7ce`.

**2.1 — The page today.** `compile_tables(PDF, page_number=6)`, band by band:

```
 band 0: ignored   NON_TABLE          cells=  0   'Communiqué de presse OFS'
 band 1: escalated UNSUPPORTED_TABLE  cells=  0   KIND_NOT_SUPPORTED
 band 2: asserted  RECORD_TABLE       cells=  6   'Grandes régions | Total | 0-19 ans | …'   <- the TRUE header
 band 3: ignored   NON_TABLE          cells=  0   'Total8 962 258 …'  (fewer than 2 lines)
 band 4: asserted  RECORD_TABLE       cells= 27   'Région lémanique 1 736 124 …'
 band 5: asserted  RECORD_TABLE       cells= 45   'Espace Mittelland …'
 band 6: asserted  RECORD_TABLE       cells= 27   'Suisse du Nord-Ouest …'
 band 7: ignored   NON_TABLE          cells=  0   'Zurich1 605 508 …'  (fewer than 2 lines)
 band 8: asserted  RECORD_TABLE       cells= 63   'Suisse orientale …'
 band 9: asserted  RECORD_TABLE       cells= 54   'Suisse centrale …'
 band 10: escalated UNSUPPORTED_TABLE cells=  0   KIND_NOT_SUPPORTED
 band 11: ignored   NON_TABLE         cells=  0   the page footer
 total cells today: 222
```

**2.2 — The merge collapses the page.** `merge_bands(bands, 2, 10)` (the constructor [[R165]]
promoted into `src/iladub/etkl/compile.py`) then `regions.classify`:

```
merge 2..10: lines=39  kind=UNSUPPORTED_TABLE  reason='header has 9 words but 2 columns'
merge 3..10: lines=35  kind=UNSUPPORTED_TABLE  reason='header has 3 words but 2 columns'
merge 2..9 : lines=35  kind=UNSUPPORTED_TABLE  reason='header has 9 words but 3 columns'
```

Nine bands each read as a 9- or 3-column table; merged, the page reads as **two columns**. All 222
cells are destroyed. This is not a near miss to be tuned — it is a different reading of the page.

**2.3 — Why, exactly.** `infer_leaf_grid` prefers `_rule_boundaries(band)` and falls back to the
whitespace profile. On the merged band `_rule_boundaries` returns `None`, so the fallback profiles
39 heterogeneous lines and finds two gutters:

```
band 2 : nrules=20  _rule_boundaries=[71.47, 139.7,  187.29, 234.87, 282.46, 330.05, 377.63, 425.22, 472.81, 523.84]
band 4 : nrules=15  _rule_boundaries=[71.47, 139.97, 198.47, 246.47, 293.97, 341.47, 390.97, 425.22, 472.81, 523.26]
band 8 : nrules=15  _rule_boundaries=[71.47, 140.47, 198.47, 246.47, 293.97, 341.47, 390.97, 425.22, 472.81, 523.26]
merged : nrules=124 _rule_boundaries=None
          infer_leaf_grid(merged).ncols = 2   boundaries=[72.0, 431.1, 522.9]
```

`merge_bands` takes `column_xs` from *the run's first band that has any* — and **band 2's
`column_xs` is empty**, so the merged band is judged against band 4's vector, on which band 2's
header word `80 ans ou plus` (x0=383.4, x1=423.8) straddles the boundary at 390.97.
`_rule_boundaries`' word-tiling test then refuses, correctly. **The author's own marks lose to a
derived estimate because the band that carries them carries nothing else.**

**2.4 — And the repair does not rescue the arm.** A vector on which the whole run tiles *does*
exist — band 2's — and it is not enough, because the merge needs **contiguity** and bands 3 and 7
sit inside the run. Straddler counts against each candidate vector:

```
                                      band2 band3 band4 band5 band6 band7 band8 band9 band10
band 2's drawn rules   (HDR)            0     1     0     0     0     1     0     0     4
band 4's derived vector (DAT)           1     1     0     0     0     1     0     0     4
```

Bands 3 and 7 straddle **every** candidate, and the cause is upstream of any merge policy:
`Line.words` on a ruled band carries **cells cut by that band's own rule grid** ([[R162]]), and
bands 3 and 7 are ruled at 3 columns, so their entire data row is already one cell spanning
`72.6 → 424.1` before a merge could see the words. **A merge inherits a cut it cannot undo.**
Arm 2 therefore needs three changes stacked — the run relation (band 2 is excluded from R165's
proposed run `3..10` by a single rounded rule x, `523.26`), the `column_xs` policy, and R162's word
granularity — and it exposes [[R168]]'s 976 unguarded cells on the way. It is the expensive arm and
it is refused here.

## 3. The relation, MEASURED corpus-wide: the donor is the band the author RULED

`PYTHONPATH=. .venv/bin/python scripts/grid_agreement_census.py` over all 7 documents / 27 pages.
For every band the record-table branch reads, it asks of each **earlier** band on the page:

- `donor = grid._rule_boundaries(earlier)` — the shipped derivation, never reimplemented. It
  returns a vector *only if the donor band's own words tile it*, so a donor is by construction a
  grid its author drew and its own ink confirms;
- **tiles** — every word of *this* band lies strictly inside some `[donor_i, donor_i+1]`;
- **same_ncols** — `len(donor) - 1` equals this band's own leaf-column count;
- **drawn** — every boundary of the donor is an x the author actually drew
  (`round(x,2) ∈ {round(r.x,2) for r in earlier.rules}`), not a gutter this compiler inferred.
  `_rule_boundaries` prefers `band.column_xs` — *author rules **plus** the interior gutters the
  rules left out* — so this clause is what separates a ruled band from a guessed one.

| # | document | page | band | ncols | qualifying donors | the donor's line 0 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | cbh-stem | 0 | 9 | 3 | — | |
| 2 | graincorp-capacity | 0 | 3 | 16 | — (band 2 is drawn and tiles, but **ncols=9 ≠ 16**) | |
| 3 | apple | 2 | 6 | 3 | — | |
| 4 | bfs | 5 | 13 | 2 | — | |
| 5 | bfs | 6 | 2 | 9 | — | *(it is the head)* |
| 6 | bfs | 6 | 4 | 9 | **[2]** | `Grandes régions Total 0-19 ans 20-39 ans …` |
| 7 | bfs | 6 | 5 | 9 | **[2]** | same |
| 8 | bfs | 6 | 6 | 9 | **[2]** | same |
| 9 | bfs | 6 | 8 | 9 | **[2]** | same |
| 10 | bfs | 6 | 9 | 9 | **[2]** | same |
| 11 | who | 0 | 4 | 13 | — (`vrules=0`: the author drew nothing) | |
| 12 | who | 1 | 4 | 13 | — | |

```
TOTAL record-table bands: 12; with a wholly-drawn, same-ncols, tiling donor earlier on the
page: 5; of those, with MORE THAN ONE such donor (i.e. the donor is not unique): 0
```

**Three things this measures, and one it does not.**

**(a) Recall 5 of 11, precision 5 of 5.** The five are exactly bfs p6's false headers — 5 of the
corpus's 11 false label rows and 40 of its 73 numeric label cells. The other six false headers get
no donor and are untouched: apple p2 band 6 has no header anywhere on its page ([[R165]]), who's two
bands are **unruled** (`vrules=0` — the author drew no column separators, so this relation has no
evidence and must abstain), cbh and graincorp have no same-ncols ruled predecessor.

**(b) The donor is UNIQUE, on evidence, with no ordering rule.** Bands 4, 5, 6 and 8 also tile each
other at the same column count — the first cut of this census picked "the earliest qualifying
donor", an ordinal rule that happened to be right. The `drawn` clause makes it unnecessary: bands
4-9's interior boundaries (`198.47, 246.47, 293.97 …`) are inferred gutters, ~11.4pt right of the
rules the author drew at `187.29, 234.87, 282.46 …`, so every one of them reads `drawn=no` and the
count of qualifying donors is **1** in all five cases, measured (`multi = 0` above).

**(c) graincorp p0 is the null control, and it fires.** Band 2 is wholly drawn and band 3's words
tile it with **zero** straddlers — the relation's two easy clauses both pass — and `same_ncols`
refuses it, 9 against 16. A relation that accepted it would have carried a 9-column header onto a
16-column table.

**(d) What it does NOT measure: that the donor's line 0 is a header.** The relation says *one
table*; that the head of that table begins with its labels is the record-table branch's existing
by-position assumption, and on bfs p6 it is right (band 2's line 0 *is* the header — [[R166]]'s
spec § 2 row 5). This is the load-bearing gap and § 6 raises it.

## 4. The ruling: arm 3, re-specified — grid donation, not header carriage

**Arm 3 is chosen, and the handoff's description of it is wrong in a way that matters.** R201 says
*"extend the carriage seam so a record-table assertion can mint a reading."* Read
`carried_roles_for` (`src/iladub/etkl/ruledroles.py`) before planning that: it requires *"every one
of this page's header rows [to have] an EXACTLY text-identical counterpart in the carried block …
the block was redrawn, not rearranged."* It answers **"is this page's header the same header
redrawn?"** bfs p6 bands 4-9 redraw nothing — they have **no header at all**. The matcher is
structurally the wrong instrument, and reusing it would mean weakening a text-identity rule whose
own docstring records why each clause is load-bearing.

What is chosen is narrower and shares only the *idea* of carriage:

> **Grid donation.** A band whose ink tiles the wholly-drawn column grid of an earlier band on the
> same page, at the same leaf-column count, is a **continuation of that band's table**: it has no
> header row of its own, its line 0 is data, and its labels are the donor's.

- **AXIOM by CLAUDE.md §8, derivation half** — a `SELECT`/`CONSTRUCT` over the evidence graph,
  open world and evidence-positive: it fires on a *present* word inside a *present* interval and
  never infers from absence. The `drawn` clause reads author marks; the tiling clause reads ink.
  **No tolerance, no tuned constant** — `COORD_EPS` is the shipped float-comparison epsilon and
  must not be repurposed as a width (`_rule_boundaries`' own docstring, and it is right).
- **Disposed by the shipped membrane**, exactly as [[R165]]'s run proposal is: the re-read
  continuation must `region_tiles` and must not lose ink. A proposal the oracle refuses leaves the
  band compiling as it does today.
- **It does not merge, so it needs no contiguity** — which is precisely why it survives bands 3
  and 7 where arm 2 dies (§ 2.4). Band indices do not renumber, `#rtable4` stays `#rtable4`, and
  [[R168]]'s 976 cells are not touched.

**The closure-scope question, answered rather than assumed.** `_rule_boundaries`' docstring warns:
*"A caller that ever widened that scope (asking across bands, or across a page) would break the
rule."* That warning is about the **collapse** — dropping a boundary because no ink occupies the
interval — which is a closed-world absence guard and stays holon-scoped: donation asks nothing
about empty intervals. The clause donation widens is the **tiling test**, which is evidence-positive.
A plan must keep them apart; a donation that ever dropped a donor boundary for want of ink in *this*
band would be inferring by absence and is forbidden.

## 5. What this loop does NOT do, and why

**It ships no compiler behaviour.** Donation moves 45 label cells to their true labels and turns 5
label rows into data rows on one page; that re-baselines bfs's document score and every corpus pin
that reads it. That is a plan's work against this spec, in a fresh session — the same shape
[[R165]] took (spec loop → plan loop → execution loop), and for the same reason.

**It does not close [[R166]] or [[R201]].** R201's closure condition is that bands 4/5/6/8/9 read
under band 2's header or escalate, and none has. R166 needs apple p2 band 6, which has **no donor**
and is not reachable by this relation at all.

**It does not touch the six donor-less bands.** For who's two unruled bands the author drew no
evidence and §8 sends the reading to NEURAL-under-an-oracle, not to a Python fallback. Arm 1
(escalate) remains the honest §7 answer for them and is deliberately left open — see
`docs/superpowers/2026-09-10-the-header-is-assumed-handoff.md` § 5c, still unplanned.

**It does not repair band 2's own body.** Band 2 asserts 6 cells whose "data" rows are the header's
own wrapped continuation lines (`Cantons` / `dépendance` / `dépendance des`). Donation makes that
worse, not better: the donated labels are line 0 only, so the wrap rows stay misread. [[R203]].

## 6. Residues to raise

- **`R203`** — *the donor's own header is still assumed.* Donation transfers the donor's line-0
  labels to a continuation band, and nothing in it asks whether line 0 of the **donor** is a header;
  it inherits `classifygraph.py:53`'s by-position choice, which [[R166]] measured wrong 11 times in
  12. On bfs p6 the donor is right, so the relation is safe on this corpus and unproven off it.
  Related: band 2's lines 1-3 are the header's wrapped continuation asserted as data (§ 5).
  Closed by a derivation of the donor's header row, or by a demonstration that a wrong donor cannot
  pass the membrane.
- **`R204`** — *`merge_bands` prefers a derived `column_xs` over the author's drawn rules.* Measured
  § 2.3: bfs p6's merge is judged against band 4's inferred gutters while band 2's drawn vector,
  the one every data band tiles, is discarded because band 2's `column_xs` is empty. This loop does
  not fix it — the fix has no consumer once arm 2 is refused, and it would change [[R165]]'s two
  accepted apple merges. Closed by a policy that prefers drawn marks, measured against apple p0/p1.
- **`R205`** — *a band's cells are cut before any cross-band reading can see its words.* Bands 3 and
  7 of bfs p6 are ruled at 3 columns, so their whole 9-column data row is one cell spanning
  `72.6 → 424.1` and straddles every candidate grid (§ 2.4). Two real data rows (the grand total
  `Total 8 962 258 …` and `Zurich …`) are `ignored`, 0 cells, and no cross-band remedy can reach
  them. A sharper, cheaper instance of [[R162]]. Closed by a re-cut at the point a donor grid is
  accepted, or by a demonstration that the raw words are unrecoverable there.

## 7. Unverified or assumed

- **Nothing in § 4 is implemented or run.** There is no donation code; § 3 measures the relation
  with an instrument that reads compile results after the fact, and what it costs is unmeasured.
  **The seam it would extend IS identified, and it is not the one a reader would guess.**
  `classifygraph.classify_evidence` is single-band and carries only `tab:lineCount`,
  `tab:gridColumnCount` and the header words (`src/iladub/etkl/classifygraph.py:48-60`) — a
  cross-band clause cannot be written over it at all. The page-scoped graph is
  `sectiongraph.run_evidence` (`:223`), [[R165]]'s, which already emits one `tab:RuledBand` per
  ruled band with `tab:bandIndex` and one `tab:bandRuleX` per distinct rounded x, and whose AXIOM
  is `vocab/queries/band-run.rq`. Donation needs two facts it does not emit — the band's
  `column_xs` (for `drawn`) and its word boxes (for tiling) — and one structural change: that
  graph carries `tab:prevBandIndex`, which restricts every join to the **adjacent** predecessor,
  and donation joins any earlier band on the page. None of that is built or costed here.
- **The corpus is 7 documents.** "No false donor" is a statement about 12 bands on 27 pages, and the
  clause carrying it — `same_ncols` — fired exactly **once** (graincorp p0). One control is one
  control.
- **The judgement that band 2's line 0 is the true header is a READING**, [[R166]]'s spec § 2 row 5,
  made from the printed rows and `pdfplumber.extract_text`. Every donation figure rests on it.
- **`wholly_drawn` compares at 2dp**, inherited from `_rule_boundaries`' own
  `round(r.x, 2)` and `_rule_xs_signature`'s rounding. It is not re-derived here and a donor whose
  `column_xs` coincided with its rules to within 0.005 would read `drawn=yes` spuriously; none does
  on this corpus, unmeasured off it.
- **No score, no wall clock, no suite run beyond the new module.** This loop changes no compiler
  behaviour, so no before/after pair exists.
- **[[R202]] is not touched.** The census avoids it by construction — it pairs nothing, reading
  `page_bands` and `regions.classify` directly rather than indexing `res.regions` — which is also
  why its population count (12) is an independent re-derivation of [[R166]]'s spec § 2, not a copy.
