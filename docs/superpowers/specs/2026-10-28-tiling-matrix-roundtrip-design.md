# Tiling, matrix, round trip — meeting tab:02, tab:05 and tab:09 honestly (design, 2026-10-28)

**Serves:** prog:criterion:tab:02 — also tab:05 and tab:09, which share its blockers. `prog:met false`
re-verified on all three at `087c1ca` (`tests/arc-manifest.ttl:1266`, `:1322`, `:1411`).

**Doc impact: none.** Manifest rows (`tests/corpus-manifest.ttl`), criterion rows
(`tests/arc-manifest.ttl`), register rows, and at most one test fixture. No released artifact changes
meaning, and nothing under `src/`, `vocab/` or `readings/` changes in the recommended path (§ 6), so
the corpus baseline does not move.

**Status: DRAFT for the maintainer.** Section 11 lists the decisions this spec does not take.

## 1. Goal, and a correction to the brief's denominator

Each criterion is met when its reason is *disposed*: on arm (a), every corpus document it fires live
on carries a dated `cor:adjudication` that names and disposes of it; on arm (b), it fires nowhere on
the corpus and names a collectable `prog:oracleTest` that exercises the path, plus a recorded reason
that separates a corpus gap from a dead path (`tests/arc-manifest.ttl:1263`, `:1319`, `:1408`). M8
refuses a met criterion that still carries any `prog:blockedBy` edge (`tests/arc-shapes.ttl:150-153`).

**The brief counted 11 live firings: tab:02 ×7 (bfs, fed), tab:05 ×1 (fed), tab:09 ×3 (arxiv, fed).
Only 3 of the 11 are in the criteria's denominator.** The denominator is the 7 `corpus/` documents.
That was ruled in spec 2026-09-18 ("The scope is the 7 `corpus/` documents only. That is the
criteria's own denominator", `specs/2026-09-18-a-firing-is-not-a-fact-design.md:254`). The lift
enforces it by skipping every baseline whose `pdf` does not start with `corpus/`
(`tests/corpus_firings.py`, `lift_firings`). fed and arxiv are `held-out/` and have no manifest entry.

```
$ .venv/bin/python -m pytest tests/test_corpus.py::test_escalation_reasons_are_adjudicated --collect-only -q
…[apple-fy2026q3-statements-DATAGRID_RESIDUE]
…[bfs-population-bilan-2023-DATAGRID_RESIDUE]
…[bfs-population-bilan-2023-KIND_NOT_SUPPORTED]
…[bfs-population-bilan-2023-REGION_TILING_FAILED]
…[ons-index-of-services-2026-02-DATAGRID_RESIDUE]
…[ons-index-of-services-2026-02-KIND_NOT_SUPPORTED]
6 tests collected
```

That leaves one live pair across the three criteria, **bfs × REGION_TILING_FAILED**, which fires on 3
bands. MATRIX_AMBIGUOUS and ROUND_TRIP_FAIL fire live on no corpus document; on the corpus they fire
only as `superseded`. The 8 held-out firings are measured and classified in § 4.2, because the brief
asked for them and because they are evidence about whether the paths are live. No arm of any criterion
reads them, and this design does not dispose of them.

## 2. Oracles first

| Criterion | Arm | Oracle | State at `087c1ca` |
|---|---|---|---|
| tab:02 | (a) | `tests/test_corpus.py::test_escalation_reasons_are_adjudicated[bfs-population-bilan-2023-REGION_TILING_FAILED]`: strict xfail until a bfs adjudication carries `cor:disposes "REGION_TILING_FAILED"`, then it passes by derivation (`_adjudication_param`) | xfail (4 xfailed, 2 passed) |
| tab:02 | (a) | `cor:DisposalShape` (D2, `tests/corpus-shapes.ttl`): refuses a disposal of a reason with 0 live firings in its judged snapshot (M4 of D2, `tests/test_corpus_manifest.py:211,215`) | live |
| tab:05 | (b) | `tests/etkl/test_r318_exact_surface_text.py::test_escalated_surface_text_is_band_text[duplicate_text_header_pdf-MATRIX_AMBIGUOUS]`. A reportlab fixture compiled end to end that reaches MATRIX_AMBIGUOUS **without a monkeypatch**. Its `assert hits and cands, "fixture drift"` asserts both the escalated report and the graph-side `rdfs:label "MATRIX_AMBIGUOUS"` | passes (10 passed) |
| tab:09 | (b) | **No natural oracle exists.** The only end-to-end test forces the refusal: `test_round_trip_fail_carries_band_text_not_the_refuted_reading` monkeypatches `roundtrip.region_round_trips` to `False`, and its docstring records "No fixture fails the round trip on its own (measured 2026-10-15)". `tests/etkl/test_roundtrip.py` shows the predicate returning `False` on constructed regions, but nothing composes the two | the gap this spec names (§ 6.3) |
| all | — | `tests/arc-shapes.ttl` M8 / M15, `tests/test_arc_manifest.py` M5b (collectable) and M7 (residue exists) | live |

**Falsification owed by the implementer.** This spec ran none of these. tab:05: invert the
`"MATRIX_AMBIGUOUS"` literal at the escalation site in `compile_tables` (today `compile.py:1724`).
The R318 parameter must then fail on `fixture drift`. Restore it and show the suite green. tab:02:
remove `cor:disposes` from the new node. The parameter must return to xfail, and under strict xfail a
passing body without a disposal fails.

## 3. Classification gate (CLAUDE.md § 8)

| Decision | Class | Why |
|---|---|---|
| Which reasons fire live on which corpus document | PROCEDURAL, already built | `lift_firings`: JSON → RDF raw extraction, no tolerance (its docstring) |
| Is a (document, reason) pair disposed | AXIOM, already built | SPARQL ASK `_DISPOSED` plus `cor:DisposalShape` (closed world, at the membrane) |
| Is this band a table, and is its refusal right | **Human adjudication** (accountable act, § 3 epistemics) | No oracle can dispose "is this a table" for an arbitrary band. The register exists so that a human signs this judgement, as tab:07 did |
| Does the region-level round-trip path execute on a natural fixture | Test (an oracle, not a decision) | No new decision code anywhere in this design |
| Recommended path's `src/` changes | **None** | Nothing here adds a geometric constant, a heuristic or a worker |

Option D (§ 6.1) would re-ask a recorded boxhead. That is a NEURAL worker which already exists,
disposed by its existing oracle (`dispose_boxhead`). It writes a new recording and no new code.

## 4. Measured facts

Probes are page-scope `compile_tables(pdf, page, validate_shapes=True, datagrid_adopt=True)` at
`087c1ca`, run from the worktree with `PYTHONPATH=src:.`. Every region's index, reason and verdict
below matches the document-scope baseline. One page-scope difference outside this spec's subject was
seen (§ 8).

### 4.1 In scope: bfs × REGION_TILING_FAILED, 3 live bands

```
$ probe.py corpus/gov-stats/bfs-population-bilan-2023.pdf 4 5 6
=== p4  r0  UNSUPPORTED_TABLE escalated REGION_TILING_FAILED esc=36
     TEXT: Communiqué de presse OFS / G1 Composantes de l'évolution démographique, de 1971 à 2023 /
           G2 Population résidante permanente étrangère selon la nationalité, au 31.12.2023 /
           OFFICE FÉDÉRAL DE LA STATISTIQUE OFS, ESPACE DE L'EUROPE 10, CH-2010 NEUCHÂTEL 5
=== p5  r8  UNSUPPORTED_TABLE escalated REGION_TILING_FAILED esc=20
     TEXT: Cantons État de la Composantes de l'évolution de la population État de la Variation 2 /
           population Naissances Décès Accroissement Solde migratoire population au en nombres en % /
           au 1er janvier vivantes naturel international 1 intercantonal 31 décembre absolus
=== p6  r11 UNSUPPORTED_TABLE escalated REGION_TILING_FAILED esc=3
     TEXT: Source: OFS - STATPOP / 1 Nombre de personnes de moins de 20 ans pour 100 personnes de 20 à 64 ans /
           2 Nombre de personnes de 65 ans ou plus pour 100 personnes de 20 à 64 ans
```

**p5 r8 was not live when bfs was accepted.** Its verdict flipped from `superseded` to `escalated` in
R166 (`0ffa420`, #369, 2026-10-24), and nothing records the flip. The commit message does not name it,
and the R166 handoff lists "the bfs and ons differences are sampling variance" as unverified
(`2026-10-22-ground-truth-set-handoff.md:396`). History of the in-scope firings:

```
$ hist.py tests/corpus-baseline/bfs-population-bilan-2023.json fc0c24a ff2c0de 0ffa420 087c1ca
fc0c24a 0.9074  p4r0:REG:esc … p5r8:REG:sup … p6r11:REG:esc
ff2c0de 0.9074  p4r0:REG:esc … p5r8:REG:sup … p6r11:REG:esc
0ffa420 0.9144  p4r0:REG:esc … p5r8:REG:esc … p6r11:REG:esc
087c1ca 0.9255  p4r0:REG:esc … p5r8:REG:esc … p6r11:REG:esc
```

**Why p5 r8 is live.** The ledger spy wraps `adoption.build_ledger` and changes nothing:

```
band 8: top=356.05 bottom=376.48 reason=REGION_TILING_FAILED tok_esc=20 touched=False
   line 30 admitted=False n=15: Cantons État de la Composantes de l'évolution de la population État de la Variation 2
   line 31 admitted=False n=12: population Naissances Décès Accroissement Solde migratoire population au en nombres en %
   line 32 admitted=False n=11: au 1er janvier vivantes naturel international 1 intercantonal 31 décembre absolus
```

Yet the canton grid does carry the boxhead's leaves:

```
#p5-datagrid 10 [h0 'Cantons', h1 'État de la population au 1er janvier', h2 'Naissances vivantes',
  h3 'Décès', h4 'Accroissement naturel', h5 'international', h6 'intercantonal',
  h7 'État de la population au 31 décembre', h8 'en nombres absolus', h9 'en %']
```

`boxhead.carried_lines` admits a header line only when **every** word on it belongs to a surviving
label. Three spanners are absent: *Composantes de l'évolution de la population*, *Solde migratoire*
and *Variation*. The footnote marks `2` and `1` are filed as other words (R166's re-ask, per
`tests/test_carriage.py`'s 2026-10-22 note). So no line of band 8 is admitted. Band 8 is untouched,
keeps its own report, and books its 20 tokens escalated, while the grid asserts 10 labels read from
those same lines. Nothing is fabricated and no entry is misread. The cost is header ink present twice
in the graph (a `CandidateConcept` with the band's `surfaceText` beside 10 `tab:LabelCell`s) and
booked escalated.

**Classification:**

| Band | What it is on the page | Class |
|---|---|---|
| p4 r0 (36 tok) | Release footer, captions of charts G1 and G2, office address and page number. No table on the page reaches the band path | **(a)** correct refusal. Not a table, so the claim "a hierarchical table that failed to tile" is wrong |
| p6 r11 (3 tok) | T3's source line and its two footnotes | **(a)** correct refusal. Not a table. Footnotes qualify T3 and do not reach it: a § 5 defect, the same one tab:07 recorded for p5's footnotes |
| p5 r8 (20 tok) | T2 canton table's three-line boxhead, whose 10 leaf labels the grid carries | **(c)** the refusal is right, because a header-only band does not tile as a table. The *booking* is a carriage defect: spanners not in the recording, and footnote marks as other words |

### 4.2 Held out (outside every arm): 8 live firings, measured because the brief asked

```
fed p1 r3  REGION_TILING_FAILED esc=15  "Total factors, other than reserve balances, / absorbing reserve funds 3,820,435 + 130,431 - 663,545 4,010,579"
fed p2 r4  ROUND_TRIP_FAIL      esc=93  footnotes 1-4 (prose: "1. Includes securities and U.S. Treasury STRIPS at face value, …")
fed p4 r1  REGION_TILING_FAILED esc=15  "3. Supplemental Information on Mortgage-Backed Securities / Millions of dollars / Account name Wednesday / Jan 1, 2025"
fed p4 r9  MATRIX_AMBIGUOUS     esc=46  Credit Facilities LLC table: 3-level header, one row "MS Facilities 2020 LLC (Main Street Lending Program) 3,583 3,738 4,522 8,260", Note
fed p6 r2  REGION_TILING_FAILED esc=101 "Liabilities" section, 11 rows of label + 3 values
fed p6 r4  REGION_TILING_FAILED esc=20  "Capital accounts" section, 3 rows of label + 3 values
arxiv p8 r3 ROUND_TRIP_FAIL     esc=21  Table 3 rows of group (A): "1 512 512 5.29 24.9 / (A) 4 128 128 5.00 25.5 / …"
arxiv p8 r6 ROUND_TRIP_FAIL     esc=13  Table 3 rows of group (D): "0.0 5.77 24.6 / (D) 0.2 4.95 25.5 / …"
```

| Class | Firings |
|---|---|
| (a) correct refusal, not a table | fed p2 r4 |
| (c) not a table itself, but it is the title, unit and boxhead of the table beside it, and is not carried (R336's class) | fed p4 r1 |
| **(b) real reading defect: entry values escalated, none misread** | fed p1 r3, p4 r9, p6 r2, p6 r4, arxiv p8 r3, p8 r6 |

**Six of the eight are real defects.** They are what the held-out set exists to find, and they are
evidence that all three paths are live on real documents. For ROUND_TRIP_FAIL the spy confirms a
genuine refusal, not a mislabel of an empty body: `region_round_trips` returned `False` for both
arxiv bands and for fed p2's footnote band (`rt.py`). fed p2's candidate is absent from the
page-scope graph because the adoption rebuild drops untouched bands' candidates there, which is
R83's documented page-scope gap (`compile.py`, "NOT REPAIRED HERE").

### 4.3 Superseded-only firings on the corpus (tab:05, tab:09)

```
apple HEAD  p2r2:MAT:sup p2r3:REG:sup p2r4:REG:sup p2r5:REG:sup p2r7:REG:sup
ons   HEAD  p7r5:ROU:sup p7r14:REG:sup p7r15:REG:sup p8r4:ROU:sup p8r5:ROU:sup p8r7:ROU:sup
bfs   HEAD  p5r2:ROU:sup p5r10..r14:ROU:sup (6 ROUND_TRIP_FAIL, all superseded)
```

On the corpus MATRIX_AMBIGUOUS fires 0 live and 1 superseded, and ROUND_TRIP_FAIL fires 0 live and 9
superseded. **Both emitters execute on natural corpus input. Their output is replaced by grid
adoption every time.** This is neither a corpus gap nor a dead path, and § 11 asks the maintainer to
name it.

### 4.4 The three blockers

| Row | Its subject | Measured today | Verdict |
|---|---|---|---|
| **R43** | ONS: 1 live REGION_TILING_FAILED, plus "UNSUPPORTED_TABLE with verdict asserted" as an oddity | Tiling half: dead since 2026-09-13 (the row's own re-measure). ons has 0 live, 2 superseded today (§ 4.3). Oddity: **by design**. `compile_tables` dispatches every non-RECORD, non-NON_TABLE band to `else:  # UNSUPPORTED_TABLE` (`compile.py:1666`), which hosts the matrix and hierarchical readers. The kind is the flat classifier's verdict, so an UNSUPPORTED kind that the hierarchical reader asserts is the normal path. Count across baselines: apple 2, cbh 4, graincorp-stem 3, ons 1, who-wfa 8, plus held-out fed 10 and arxiv 1. Four of those corpus documents are accepted | **Stale: closable** with this evidence |
| **R62** | Apple p0: 1 MATRIX_AMBIGUOUS and 4 REGION_TILING_FAILED remain | apple fires neither reason on p0. The 2026-09-18 acceptance records p0 asserting 124 cells through the band path, and today's baseline holds only p2 firings, all superseded (§ 4.3) | **Stale: closable.** Its premise is false |
| **R44** | bfs: the KIND_NOT_SUPPORTED, REGION_TILING_FAILED, ROUND_TRIP_FAIL and DATAGRID_RESIDUE shares | KIND_NOT_SUPPORTED: disposed (tab:07). ROUND_TRIP_FAIL: 0 live; ruled a *reporting* defect on 2026-09-16, with the grid reading 27 of 27 rows correctly. REGION_TILING_FAILED: **3 live, not 2** (p5 r8 rejoined in R166). DATAGRID_RESIDUE: tab:08's subject (R79, R83, R84) | **Open in name only** once § 6.1 lands. Every share has a home. Close it or delete the edges (§ 11) |

## 5. Smaller findings (recorded here, not acted on)

- **The criterion statements cite stale lines.** `compile.py:656, :763, :939, :830` and `holon.py:493,
  :55` are now `compile.py:1380, :1617, :1841` (REGION_TILING_FAILED), `:1724` (MATRIX_AMBIGUOUS),
  `holon.py:731` (region-level ROUND_TRIP_FAIL) and `holon.py:155-168` (cell-level). Plan rule 7's
  remedy applies: cite the symbol. Whether `prog:statement` may be edited is the maintainer's call.
- **Ruled-band tokens are counted per cell.** bfs p6 band 11 books `tok_esc=3` for 38 page words,
  because its band `Word`s are whole ruled cells (`bandwords=3`). If that holds generally, a ruled
  escalated band under-books its ink and inflates the score. Unverified beyond this band. It is a
  candidate residue, not this design's subject.

## 6. Design: the fastest honest path, per criterion

### 6.1 tab:02: one disposal, one new row, three register moves

1. **Append one `cor:adjudication` to bfs** (append-only, at file end, as tab:07 did) carrying
   `cor:disposes "REGION_TILING_FAILED"` and `cor:judgedAgainst [ a cor:Snapshot ; cor:recordedIn
   "tests/corpus-baseline/bfs-population-bilan-2023.json" ; cor:blob
   "7ae169c2c531c8a2f092d653128172aedb20e184" ]`, which is `HEAD:` of that file at `087c1ca`. **SEAM:
   re-measure the blob after any intervening merge to `main`**, because D2 needs it durable on
   first-parent history. The rationale disposes **band by band**, quoting § 4.1's text:
   - p4 r0 and p6 r11: **not tables**. The claim the reason makes is wrong, and the refusal stands.
     Record the § 5 defect as tab:07 did: T3's footnotes and source do not reach T3.
   - p5 r8: **a table's boxhead, not a table**. The band refusal is right. **Record the defect in the
     same note, not excused:** the grid reads its 10 leaves, but the band's lines are never carried in
     full (3 spanners, 2 footnote marks), so its 20 tokens stay escalated and the ink appears twice.
     State that the flip happened at `0ffa420` and was unrecorded.
2. **Raise one residue** for the p5 r8 carriage defect and its unrecorded flip, linking R336, R334 and
   R242.
3. **R43 and R62: strike, with § 4.4's closure evidence in place**, and delete `prog:blockedBy "R43"`
   and `"R62"` from tab:02 (R62 from tab:05 too), per the 2026-08-22 R108 ruling (a closing residue
   deletes every edge naming it).
4. **R44:** see § 11 decision 2.
5. Set tab:02 `prog:met true`, `prog:metOn` the merge date, and `prog:retrospective false`.

**Option D, not recommended for this criterion.** Re-ask p5's canton boxhead under R334's spanner
question. *Proposed:* line 31 would then be carried in full, band 8 is touched, and its verdict
returns to `superseded`. That would move 20 tokens from REGION_TILING_FAILED into DATAGRID_RESIDUE
(lines 30 and 32 still carry footnote marks). It hides the firing and repairs nothing: *superseded is
not repaired*. It also edits `readings/`, which costs a 24-minute regeneration. It belongs to the
R336 / tab:08 lane.

### 6.2 tab:05: arm (b), with an existing natural oracle

- `prog:oracleTest` becomes the R318 parameter in § 2. Falsification is owed (§ 2).
- The recorded reason, as a register row or the criterion's comment (§ 11 decision 3): **the path is
  live**. It fires naturally on the oracle fixture, on apple p2 (superseded) and on held-out fed p4
  (live, a real defect, § 4.2). It is absent live from the corpus because apple p2's grid adoption
  supersedes it.
- Delete `prog:blockedBy "R62"` with R62's closure (§ 6.1.3). Retrospective: the oracle landed
  2026-10-15, after the 2026-08-20 declaration, so the value is `false`. **MEASURE M4's rule before
  writing it** (`tests/arc-m4-unlabelled-grandfathering-leak.ttl`).

### 6.3 tab:09: arm (b). The oracle is the work

The recorded reason has the same shape as tab:05's: the path is live (9 superseded on the corpus, 3
live held-out), and adoption supersedes every corpus instance. **The honest gap is the oracle.** Two
options:

- **(i) Fastest.** Name `test_round_trip_fail_carries_band_text_not_the_refuted_reading` together with
  `tests/etkl/test_roundtrip.py`. One forces the refusal and proves the escalation half. The other
  proves the predicate refuses constructed regions. **Weakness:** no single test drives a natural
  refusal end to end, which is exactly what tab:06's oracle does (`test_offcenter_merge_escalates`).
- **(ii) Recommended.** A new reportlab fixture whose band fails `region_round_trips` with no patch.
  It is a synthetic table whose ink crosses a column boundary, the shape `test_roundtrip.py:86-101`
  constructs by hand. Add one test asserting, graph-side, a `CandidateConcept` labelled
  `ROUND_TRIP_FAIL` at `…#htable{i}-rt` and no `tab:HierarchicalTable` asserted. **MEASURE FIRST**
  whether `classify_hierarchical` admits such a band at all. The 2026-10-15 measurement found no
  existing fixture that reaches the refusal. `tests/` is not a corpus-baseline input, so this does not
  regenerate the baseline.

Either way, delete `prog:blockedBy "R44"` (§ 11 decision 2). The cell-level emitter keeps its own
oracle, `tests/etkl/test_holon.py::test_straddling_cell_is_proposed_not_asserted`, and stays
corpus-dead as the statement already says.

## 7. What is NOT done

- No held-out firing is disposed or fixed. The six (b) defects in § 4.2 are recorded in one new
  residue row, not repaired here.
- p5 r8's carriage is not repaired, and Option D is not run.
- No `cor:` per-reason disposal term (the arc-manifest header leaves that open).
- No fix for the § 5 findings.
- No guard for R326, under which a disposal covers future firings of its pair (§ 9).

## 8. Unverified

- Page scope versus document scope: every one of the 11 regions agrees. bfs p6 r1 KIND_NOT_SUPPORTED
  reads `superseded` at page scope against the tab:07 disposal's `live`. That is not this spec's
  subject and was not reconciled.
- Option D's prediction (§ 6.1) was not run.
- That `classify_hierarchical` admits a synthetic band that refuses the round trip (§ 6.3 (ii)).
- M4's retrospective rule for tab:05 and tab:09.
- The § 5 per-cell booking beyond bfs p6 band 11.

## 9. Predicted blast radius

- Recommended path: `tests/corpus-manifest.ttl` (+1 node), `tests/arc-manifest.ttl` (3 rows, edges
  deleted), `docs/superpowers/residues*.md` (R43 and R62 struck, 2 new rows, and R44 per the ruling),
  and with (ii) `tests/etkl/fixtures.py` plus one test. **Corpus baseline: no change**, because no
  input under `src/`, `vocab/` or `readings/` is touched.
- Oracle: 3 passed and 3 xfailed, from today's 2 passed and 4 xfailed. The bfs REGION_TILING_FAILED
  parameter turns green by derivation.
- Arc: 3 more `tab` rows met. M8 and M15 must stay green, so **MEASURE** that no met criterion has a
  `proposedDependsOn` edge to these three still asserting what was withdrawn (see the etkl:05 note at
  `tests/arc-manifest.ttl:1819-1828`).

## 10. Adversarial pass on my own premises

1. *"Held-out is outside the denominator" is a convenience.* It is the 2026-09-18 ruling and the
   lift's code, not my choice. But meeting three criteria while six real defects sit on held-out
   documents could read as the corpus flattering the compiler. The new residue row (§ 7) keeps them
   visible. Whether the arc should ever count held-out documents is the maintainer's question, not
   this loop's.
2. *Disposing p5 r8 adjudicates away a defect.* The disposal judges the **reason's** claim. The defect
   (carriage) is named in the same note and in a new row, which is the tab:07 pattern. If the
   maintainer reads a disposal as "nothing wrong here", p5 r8 should wait for the carriage fix, and
   tab:02 waits with it. That is decision 1.
3. *"Superseded" might be read as arm (b)'s "fires nowhere".* The corpus does exercise both reasons.
   Calling it a "corpus gap" would be false. Calling it a "dead path" would be false. So § 6.2 and
   § 6.3 record the third state explicitly instead of picking one of the two words. D2 makes arm (a)
   structurally unavailable for 0-live reasons (M4), so arm (b) is the only arm. The maintainer must
   accept that it covers this state.
4. *R326 cuts against the disposal.* A REGION_TILING_FAILED disposal on bfs would also cover a future
   real-table firing on bfs. `cor:judgedAgainst` pins the reading, but `_DISPOSED` does not compare
   counts. This is a standing weakness that tab:07 shares. It is not new.
5. *The R43 "by design" reading* rests on one dispatch line (`compile.py:1666`) plus 29 instances
   across accepted documents. It does not rest on an author's statement of intent. If the maintainer
   wants the oddity characterised by a test, R43 stays open and tab:02 loses that edge only by
   argument.

## 11. Decisions for the maintainer

1. **p5 r8:** dispose now with the defect recorded (recommended), or hold tab:02 until carriage is
   fixed.
2. **R44:** close it (every share has a home: KIND_NOT_SUPPORTED disposed, REGION_TILING_FAILED
   disposed, ROUND_TRIP_FAIL a reporting defect ruled 2026-09-16, DATAGRID_RESIDUE handed to tab:08),
   or keep it open and delete the edges by argument, as tab:07 did.
3. **Arm (b) for superseded-only reasons:** does "fires nowhere" mean "nowhere live"? And where is the
   recorded third-state reason kept: a new register row, or the criterion's comment?
4. **tab:09's oracle:** (i) the forced test plus the unit predicate, or (ii) a natural fixture.
5. **Stale `prog:statement` line citations:** edit them to symbols, or leave them.
6. **Held-out (b) defects:** one register row (recommended), or a separate loop now.

## Ruled 2026-10-28 by the maintainer (in chat)

1. **bfs p5 r8:** dispose of it now. The bfs adjudication disposes `REGION_TILING_FAILED` band by band. The header-carriage defect, 20 tokens of a header whose labels are carried but whose lines never count as read, is recorded in that note and in a new residue row.
2. **Refusals superseded by adoption:** a reason whose emitters run on corpus documents, and whose every output adoption replaces, counts as **"fires nowhere"**. The recorded reason is "superseded by adoption: neither a corpus gap nor a dead path". It is stated on the criterion.
3. **tab:09's oracle:** a new natural synthetic fixture that reaches ROUND_TRIP_FAIL with no patching. The forced test is not used.
4. **The six real held-out defects:** one new residue row now, not a loop.
5. **Criterion statements:** stale `file:line` citations are corrected in place.
6. **R44:** follows from 1. It closes once the bfs disposal lands, and its edges are removed. R43 and R62 are struck as stale.
