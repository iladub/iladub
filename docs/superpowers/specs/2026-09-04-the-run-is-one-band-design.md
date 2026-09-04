# The run is one band — the split at a section heading is a PROPOSAL, and the tiling membrane disposes of it

**Date:** 2026-09-04. **Branch:** `the-run-is-one-band`. **Measured at:** `0d2ccb2` (HEAD of `main`).
Every figure below is either cited to `docs/superpowers/2026-09-04-one-band-matrix-spike.md` (this
loop's predecessor, whose instrument is committed at `scripts/one_band_matrix_spike.py`) or
re-measured in this session from a scratch script whose path is given at the measurement; **no repo
file was changed by any measurement.**

**Predecessors, in the order they must be read:**
`docs/superpowers/2026-09-04-one-band-matrix-handoff.md` § 5 (the four-part design shape, graded
PROPOSED, whose second item this spec was required to MEASURE before designing) →
`docs/superpowers/2026-09-04-one-band-matrix-spike.md` § 7 (the licence census) and § 8 (the band
index). `R165` is the row; `R160`, `R166`, `R167` are its neighbours.

**Doc impact: increment.** `tests/corpus-manifest.ttl`'s apple entry is an append-only rationale
register whose last note pins the measured score `0.18950437317784258` (`corpus-manifest.ttl:118`);
this loop moves it and must **append** a new note rather than repair that one in place.
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM derivation. No released assertion
changes; **no contradiction**, so nothing blocks a release tag.

**Global Constraint — the neurosymbolic gate (CLAUDE.md §8).** Every decision in this loop is
classified in § 2 before any code. A tuned constant or tolerance anywhere in the shipped diff is a
review failure. Reviewers enforce it.

---

## 1. What was asked, and what is already measured

### 1.1 The subject

`R165` measured that apple's escalated statement bands are **header-less intra-page continuations
of one table**: all eight `REGION_TILING_FAILED` refusals are `CoverageShape` — *"leaf column is not
covered by any header node of its table"* — because the statement's single column header sits in
band 2 at the top of the page and the section bands below it (`Operating expenses:`,
`Earnings per share:`, …) are body continuations of that same grid, split off it by whitespace and
a heading line.

Two remedies were proposed and the first was refuted. Carriage (`carried_header_roles`) **cannot**
close the row: apple mints no `CarriedHeaderReading` anywhere, and the seam matches a *redrawn*
header, it never supplies a missing one (`docs/superpowers/2026-09-03-r165-forced-carriage-spike.md`).
The second — *do not split at the section heading in the first place* — was RUN 2026-09-04 and is
**CONFIRMED**: merging apple p0 bands 2..7 into one `Band` yields a `MatrixRegion` that passes
`region_tiles` with **124 entries** where 48 entry-cells are asserted today; p1 2..7 yields **56**
where 14 are asserted today; both pages reach a page score of **1.0000** with zero escalated tokens
and the apple **document** score goes **0.1895 → 0.6289**
(`docs/superpowers/2026-09-04-one-band-matrix-spike.md` § 2–3, § 8.4).

**So the reading is not in question. What is in question is how `page_bands` decides not to split** —
and that is the whole of this loop.

### 1.2 What the predecessor already refuted, and this spec must not re-propose

`R165` named its own licence: *a maximal contiguous run of bands sharing one `tab:ruleXsSignature`
is one band*. Run on all 7 documents and 27 pages, it is **REFUTED** (spike doc § 7) in three
independent ways, each of which is a constraint on the design rather than a detail:

| refutation | where | what it forces |
| --- | --- | --- |
| **UNDERSHOOTS.** apple p1 has 3 distinct signatures over its 6 ruled bands, so set *equality* stops the run at 2..3 → 26 entries, not the 56 measured for 2..7 | § 7.1 | the band-forming relation is **not** signature equality |
| **MISSES THE HEADER.** apple p2's `Nine Months Ended` band is unruled, signature `None`, so no signature relation of any strength reaches it | § 7.2 | an unruled header band joining a ruled run is a **separate** rule (and p2 is out of scope, § 4) |
| **DESTROYS INK.** bfs p6's run 3..10 spans six `asserted` bands totalling **216 cells**, and the merged band is not even a matrix candidate; same shape at ons p7 | § 7.3 | the merge **cannot be an unconditional `page_bands` change** |

The third is the load-bearing one, and it is what makes this loop an application of CLAUDE.md §3
rather than a geometry change: **the merge is a PROPOSAL, and the tiling membrane already in the
compile is its disposer.**

### 1.3 What the band index costs, and the one case with no evidence

Spike doc § 8 measured the renumbering. On this corpus **not one band renumbers**, because every run
the oracle accepts is a page **tail** — indices are only removed, never shifted. That is a corpus
accident, not a property of the design, and § 8.5 lists why it matters if it ever stops holding:

- the index is minted into the **shipped** graph (`#table{idx}`, `#region{idx}`, `#mtable{idx}`,
  every decision-log node) and onward into the **grounded** graph, where `ground.py:100` mints
  `urn:iladub:region:<fragment>` node IRIs from it — a renumbering is an **identity change in
  published output**, not an internal detail;
- **three** two-pass flows use pass-1 indices against pass-2 results (section repair, carriage
  replay, adoption), and every step of each is a valid list operation, so a mismatch is **silent**;
- adoption is the one this loop touches directly: `grid_idx = len(pages[p].regions)`
  (`document.py:1657`) goes **8 → 3** on the two merged apple pages.

**The design must therefore be correct for a non-tail accepted merge, and no corpus document can
exercise that case.** § 5 supplies the fixture instead.

---

## 2. Classification under §8 — argued for THIS subject, not inherited

There are exactly two decisions in this loop, and they are classified separately because they sit on
opposite sides of the assert/propose line.

### D1 — *"which contiguous bands are candidates for one table?"* → **AXIOM, derivation, open world**

The naive reading of CLAUDE.md §8 sends this to NEURAL: it is a *"which rows does X group"* question,
and §8 says such judgements are GenAI-via-BAML proposing under a semantic oracle, **never** a Python
geometry heuristic with a tuned tolerance. That reading is wrong here, and the reason is worth
stating rather than assuming, because it is the one place this spec could quietly violate the gate.

**The judgement §8 sends to NEURAL is the one that DISPOSES.** What NEURAL forbids is *deciding* a
span/read/group question in procedural geometry — settling it, so the answer reaches the graph
unchallenged. D1 settles nothing. It **enumerates candidates** that D2 then disposes of by the same
membrane every other band reading passes. A proposal that a closed-world oracle refuses cannot put a
false fact in the graph; it can only fail to put a true one there. That is exactly the shape
`section_candidates` already ships (`sectiongraph.py:211-245` → `vocab/queries/section-repeat.rq`,
whose header states the same open-world/one-page-closure argument verbatim), and this loop reuses it
rather than inventing a second idiom.

The derivation is therefore:

- **evidence-positive** — a run extends because rules the author drew are *present* at shared x
  positions, never because ink is absent from a page;
- **holon-scoped** — one transient `Graph` per page, exactly like `section-repeat.rq`,
  `classify-kind.rq` and `grid-region.rq`. Any `NOT EXISTS` closes *within* that page graph while the
  document graph stays open;
- **free of any numeric literal** — the only rounding is the 2dp already performed by
  `sectiongraph._rule_xs_signature` at fact-emission time (`sectiongraph.py:178-189`), which this
  loop does not touch and does not re-tune. **A new constant in the `.rq` is a review failure.**

**What would falsify this classification and send D1 to NEURAL:** a corpus case where the membrane
accepts a proposed run that is *wrong* — i.e. where D2 cannot dispose. § 1.2's third refutation is
the near-miss (bfs p6, 216 asserted cells), and it is refused at `is_matrix_candidate`, before any
graph is built. § 3.4 states the measurement that keeps this honest, and § 5's oracle O3 is the test
that fails if it ever stops holding.

### D2 — *"is the merged reading admissible?"* → the EXISTING membrane; no new oracle

`classify_matrix` → `assert_matrix_region` → `region_tiles` (`compile.py:817-840`) is already the
closed-world disposer for every matrix reading in the compile: eleven tiling invariants plus the two
physical shapes (`tiling.region_tiles`, `tiling.py:63-71`). **This loop adds no oracle and no shape.**
The merged band is offered to the identical chain, and a refusal falls back to today's bands.

This is the closed-world half of §8's world-split, and it is where it belongs — at the membrane, on
what may *cross* into the asserted graph, not in the derivation that proposed it.

### The one thing that is NOT classified here

**Attaching an unruled header band to a ruled run beneath it** (§ 1.2's second refutation, apple p2)
is a different decision with a different evidence base, and it is **out of scope** — see § 4.

---

## 3. Design

### 3.0 The seam: the merge lives in `page_bands`, and nowhere else

`page_bands` (`compile.py:270-323`) is *"the page's bands, exactly as `compile_tables` reads them
(band i here IS band i there)"* — its docstring pins the band-index enumeration as the load-bearing
contract for `section_repair_bands`, the per-band decision log, and every `#tableN` / `#regionN` /
`#mtableN` URI. `compile_tables` calls it and enumerates the returned list **unmodified**
(`compile.py:602`, `:615`), and `document.compile_document` calls it once per page for its own
inventory (`document.py:1410-1411`).

**Therefore the merged list must be what `page_bands` RETURNS.** Any other placement — trying the
merged reading inside `compile_tables`'s band loop, or merging in the driver — creates a second
indexing scheme beside the pinned one, which is precisely the silent-mismatch class § 1.3 describes.
Two consequences follow for free, and they are the reason this placement is not merely tidy:

- **Adoption stays correct without being touched.** `grid_idx = len(pages[p].regions)`
  (`document.py:1657`) is the driver's band count used to index the re-compile's report list. Because
  both sides read the *same* `page_bands` output, both move together: 8 → 3 on apple p0/p1, and the
  correspondence `grid_idx == len(bands)` that `compile.py:1052-1054` appends the datagrid region at
  is preserved by construction. **The plan MUST verify this by running the adoption tests, not by
  re-reading this paragraph** — § 1.3's point is that every step of that flow is a valid list
  operation, so a mismatch does not raise.
- **Continuation recognition reads the merged bands.** `document.py:1410-1425` feeds
  `licence_evidence(prev_bands, prev_idx, bands, cur_idx, …)` from the same call. A merged page has
  different band identities, so the page-to-page licence sees a different pair. On apple this is
  inert (no `CarriedHeaderReading` is minted anywhere — forced-carriage spike § 5), but it is a real
  behavioural surface and § 5's oracle O4 pins it.

### 3.1 INVARIANT M1 — the partition does not depend on `section_repair_bands`

`page_bands` takes `section_repair_bands` and forwards it to `_build_ruled_band`, and the driver
calls it with `None` in pass 1 and with a candidate set in pass 2 (`document.py:1507-1511`). If the
merge partition could differ between those two calls, pass-1 indices would be applied to a pass-2 list
of different length — § 1.3's silent mismatch, in the flow this loop is most likely to trip.

**Half of this is already free, and it is measured.** `_build_ruled_band`'s docstring states
*"`sub_rules` passes through UNTOUCHED — no Rule is ever synthesised"* (`compile.py:73-106`), and the
`section_repair` flag reaches only `_grid_lines(..., ink_witness=…)` and the hrule weld
(`compile.py:126`, `:146-152`) — both of which change **cells and column boundaries**, never the
band's rules or its extent. So any relation derived from *rule x positions* is section-repair
invariant by construction.

**The other half is not free**: D2's disposal (`classify_matrix` → `region_tiles`) consumes cells, so
an accepted/refused verdict *could* differ between a repaired and an unrepaired build.

> **M1 (the invariant the implementation must uphold):** the run partition `page_bands` applies is a
> pure function of the band list built with `section_repair=False`, for every value of
> `section_repair_bands`. It is decided on the unrepaired build; the repair flag is then applied to
> the constituent bands *within* that fixed partition.

M1 makes the index space identical across passes by construction rather than by corpus accident.
**Name the seam, not the answer** (plan rule 3): the implementer must MEASURE what `page_bands` costs
under M1 when `section_repair_bands` is non-empty — a second build of the page's ruled bands — and
whether that is one extra `_build_ruled_band` per named band or a whole second page build. Do not
assume; § 3.4's budget is what it has to fit inside.

### 3.2 The fallback is the whole of D2

For each candidate run, in a page-local order the implementation must make deterministic:

1. build the merged `Band` (the spike's `merge_bands`, `scripts/one_band_matrix_spike.py:37-55`, is
   the measured constructor — lines in document order, extent the run's, rules/hrules/captions/
   unit_markers concatenated, and `column_xs` taken from the first band that carries any, **never
   unioned**, because `column_xs` is a boundary vector and mixing two invents boundaries no band
   derived);
2. offer it to `is_matrix_candidate` → `classify_matrix` → `assert_matrix_region` → `region_tiles`
   on a **scratch** graph — the identical chain `compile.py:817-840` runs, reused, not copied;
3. **accept** → the run's bands are replaced by the merged band in the returned list;
   **refuse at any stage** → the run's bands are returned exactly as they are today, byte-identical.

A refusal must cost nothing observable: no triple, no decision-log node, no report. **The scratch
graph is discarded.** This is what makes the change safe on bfs p6 and ons p7 (§ 1.2, third
refutation) with no per-document knowledge anywhere.

**Overlap.** Two accepted runs cannot share a band. The implementation must state and pin its
resolution rule; the obvious one is *longest run first, then leftmost*, but it is a **decision, not a
default** — say which, and why, in the plan.

### 3.3 The relation: ADJACENT SUBSUMPTION over the band's rule x-positions — MEASURED

The handoff ordered this measured before it was designed. It was, this session, over all 7 documents
and all 27 pages (`scripts/band_run_census.py`, **committed by this loop** so the tables below are re-runnable rather
than pasted — the predecessor's census was scratch and had to be re-derived, § 1.2. It **imports**
`merge_bands` from `scripts/one_band_matrix_spike.py` and `_rule_xs_signature` from `sectiongraph`;
nothing is copied). Relation **A = equality** reproduces spike § 7's census row-for-row, which is the
cross-check that the instrument is the same one.

> **The relation.** A run extends from band *i* to band *i+1* when both bands carry rules and one's
> set of distinct rule x-positions is a **subset of the other's, in either direction**. Runs are the
> maximal contiguous chains under that adjacent relation. An unruled band never joins.

**Q1 — the handoff's own question, answered.** apple p1:

```
band 2 |set|= 9   band 3 |set|= 9   band 4 |set|=10   band 5 |set|= 9   band 6 |set|= 7   band 7 |set|= 9
set5 − set6 = ['488.68','562.36']   set6 − set5 = ∅     → band 6 ⊂ band 5   YES
set4 − set3 = ['560.44']            set3 − set4 = ∅     → band 4 ⊃ band 3   YES
pair 2→3 equal · 3→4 sub · 4→5 sup · 5→6 sup · 6→7 sub
```

**Q2 — does the relation produce exactly 2..7 on apple p1? YES**, a single run replacing equality's
`(2,3)`. apple p0 (`2..7`) and p2 (`3..7`) are unchanged from equality. **A and B differ on 6 of 27
pages**, and two of those differences are new information § 7 could not see:

```
graincorp-capacity p0: only-A=[]        only-B=[(1,3)]    ← NEW run, covers 390 asserted cells
graincorp-stem     p0: only-A=[]        only-B=[(1,2)]    ← NEW run, covers 586 asserted cells
apple              p1: only-A=[(2,3)]   only-B=[(2,7)]    ← the target extension
bfs                p5: only-A=[(3,5)]   only-B=[(2,5),(7,8)]
ons                p7: only-A=[(2,14)]  only-B=[(2,15)]
ons                p8: only-A=[(1,7)]   only-B=[(0,8)]
```

**Q3 — the disposal of all 14 runs the relation produces. Two are accepted, both apple:**

```
document              pg    run   candidate  classify       entries  tiles  cells today  DESTROYS?
graincorp-capacity     0   1..3   False      None              None   None          390   no
graincorp-stem         0   1..2   False      None              None   None          586   no
apple                  0   2..7   True       MatrixRegion       124   True           48   no
apple                  1   2..7   True       MatrixRegion        56   True           14   no
apple                  2   3..7   False      None              None   None            3   no
bfs                    3   3..5   False      None              None   None            0   no
bfs                    5   2..5   False      None              None   None            0   no
bfs                    5   7..8   False      None              None   None            0   no
bfs                    6  3..10   False      None              None   None          216   no
ons                    0   0..1   False      None              None   None            0   no
ons                    1  8..11   False      None              None   None            0   no
ons                    5  9..12   False      None              None   None            0   no
ons                    7  2..15   False      None              None   None            0   no
ons                    8   0..8   False      None              None   None            0   no
```

**No run the oracle accepts destroys a cell asserted today.** The two accepted runs both gain
(124 vs 48; 56 vs 14). The six `ign`-only runs spike § 7.4 left untested are now measured — every one
refused at `is_matrix_candidate`.

**Q4 — every accepted run is still a page tail, and the relation makes the index picture strictly
BETTER.** Under equality, apple p1's accepted run was `2..3`, a **non-tail** with four bands after it.
Under subsumption it is `2..7`, a tail. So every accepted run on the corpus now ends at the last band
of its page, indices are only removed and never shifted, and the merged band mints `#mtable2` — the
IRI band 2 already mints today.

**THE RISK THIS MEASUREMENT SURFACED, and it is the sharpest thing in this spec.**
`is_matrix_candidate` is refusing the two new graincorp runs, and those runs cover **976 asserted
cells between them**. Read the graincorp-stem p0 case directly:

```
band 1: ignored  cells=  0  |set|= 5   'SHIPPING STEM'
band 2: asserted cells=586  |set|=20   'Friday, 31 July 2026'
```

A *title* band whose five rule x's are a strict subset of the table's twenty. The relation joins them;
only the oracle keeps the 586 cells. **`is_matrix_candidate` was never designed for that job**, and
nothing measured here forbids a future document where a title⊂table run *is* a matrix candidate.

**This spec deliberately does NOT add a runtime no-regression guard**, and the reason is that the
guard is not implementable where the decision lives: `page_bands` decides the partition *before*
anything is compiled, so it cannot know what the constituent bands would have asserted without
compiling both readings. Designing that against a hazard no document exhibits would be designing
against a hypothesis. Instead the hazard is made **falsifiable rather than guarded**: § 5's oracle
**O3** is a corpus-wide per-page no-regression assertion that fails the moment any document loses
asserted tokens to a merge, and **R168** (§ 7) records that the safety currently rests on a refusal
that was never specified to provide it.

### 3.4 Where the derivation lives — the `section_candidates` idiom, reused

The repo already ships this exact shape, and this loop copies its structure rather than inventing a
second one: `sectiongraph.section_evidence` emits a **transient per-page evidence graph**,
`vocab/queries/section-repeat.rq` derives **pairs** over it, and `sectiongraph.section_candidates`
(`sectiongraph.py:211-245`) assembles the pairs into maximal groups in Python. `section-repeat.rq`'s
own header states the open-world/one-page-closure argument this spec's § 2 restates for D1.

- **The facts.** Equality is expressible over the existing `tab:ruleXsSignature` string; **subsumption
  is not** — a space-joined string supports `=` and nothing else. The emitter therefore also emits one
  fact per distinct rounded x position. That is **one new declared term** in `vocab/ontology/tab.ttl`
  beside `tab:ruleXsSignature` (`tab.ttl:306`); the rounding is `_rule_xs_signature`'s existing 2dp
  and is **not re-tuned** (§ 2). A new term is mandatory rather than optional: `tests/test_query_
  declarations.py` and `tests/test_query_terms.py` fail on a query naming an undeclared term.
- **The derivation.** A new `vocab/queries/*.rq` deriving adjacent comparable pairs — adjacency as an
  index relation, subsumption as a holon-scoped `FILTER NOT EXISTS { ?a tab:ruleX ?x . FILTER NOT
  EXISTS { ?b tab:ruleX ?x } }` closing **within the one page graph**. **It contains no numeric
  literal.**
- **The assembly.** Maximal contiguous chains, in Python, over the derived pairs — the same
  procedural role `section_candidates` already plays. Deterministic ordering is required (§ 3.2's
  overlap rule).

### 3.5 The cost, measured, and the budget the implementation must fit

Enumerating *all* contiguous runs of ≥2 ruled bands and letting the oracle dispose of them — the
design in which no relation is needed at all — was priced and **rejected on measurement**
(`scripts/band_run_cost.py`, committed by this loop):

```
TOTAL contiguous runs of >=2 ruled bands over the corpus: 266     (ons p7 alone: 120; bfs p6: 36)
page_bands cost today, per page: 0.03s – 3.93s
```

266 runs × (`classify_matrix` + `assert_matrix_region` + a pySHACL `region_tiles` validation), against
**14** runs under the relation. The relation is a **pruner**, and that is its whole justification —
it is not a licence, because it settles nothing (§ 2, D1).

**The budget:** `page_bands` is called at least twice per page in a document compile
(`document.py:1410` for the inventory, `compile.py:602` inside `compile_tables`) and a third time on a
repair pass, with **no caching anywhere** (`grep -rn lru_cache src/iladub/etkl/*.py` → no output). The
plan must MEASURE the corpus-suite wall-clock before and after and report both; a disposal run per
`page_bands` call is the thing to watch.

---

## 4. What is NOT done — deliberately

1. **apple p2 stays refused.** Two blockers, neither of them the merge (spike doc § 4): a single
   em-dash `—` (U+2014) types as `tab:Text` and moves the stub|data split (`R167`), and p2's header
   band is unruled so `Nine Months Ended` is three `Line.words` that the uncarried-ink guard refuses
   (`R162`, ruled NEURAL, out of scope). **The unruled-header-joins-a-ruled-run rule of § 1.2 is
   therefore not designed here**: it would close nothing on its own, and designing it against a page
   that refuses for two other reasons is designing against an unmeasurable target.
2. **`R167` is not fixed here.** It is a one-line change to `celltype.is_blank` with a corpus
   regression run, it unblocks nothing on p0/p1, and bundling it would make this loop's diff answer
   two questions at once.
3. **`R160` is not ruled.** Spike doc § 8.4 supplies the numbers (`adopted=()` in both the baseline
   and the merged run — the one-band reading makes adoption *unnecessary* on p0/p1 rather than
   restoring it), and the maintainer deferred the ruling pending exactly that measurement. **This
   spec may cite § 8.4; it must not rule the reader-authority question in passing.** If the
   implementation makes the row moot, say so in the loop's evidence and leave the row open.
4. **`R166` is not closed by fiat.** Its p0 half (band 4 asserting `Operating income 35,695 …` as a
   column header) is *disposed of* by the merged reading, because that line becomes a leaf row — but
   its p2 half survives, so the row stays open with its subject narrowed.
5. **No new vocabulary, no new SHACL shape.** D2 reuses the tiling membrane verbatim (§ 2).
6. **No change to `_rule_xs_signature`'s rounding, and no second signature abstraction.** The facts
   this loop derives over are emitted by the existing emitter or by a sibling of it.

---

## 5. The oracle — falsifying, two-sided, per task

Every task ships a `## FALSIFICATION` block (CLAUDE.md plan rule 4): remove or invert the thing the
new test pins, show it **failing**, restore, show the suite green. **No falsification evidence ⇒ the
task review fails.** These are the tests the plan may supply verbatim (plan rule 1) — and each is a
**proposition until the implementer makes it pass**; one that cannot be made to pass has found a spec
defect, and the correct response is to say so in the task report and substitute the satisfiable form
carrying the same force, never to weaken the assertion (plan rules 1, 5).

**O1 — the relation joins what equality cannot, and joins the dangerous case too (two-sided).**
apple p1's ruled bands form **one** run `2..7`, where equality gives `2..3`; and graincorp-stem p0
bands `1..2` **do** form a run (the title band's 5 x's are a strict subset of the table's 20).
*Falsifier:* replace subsumption with equality → apple p1 collapses to `2..3`. The graincorp half is
the one that matters: a test that only pins apple would pass for a relation that special-cases it.

**O2 — the fallback is what saves the ink, and it is proven by deleting it.**
After this loop, graincorp-stem p0 still asserts **586** cells, graincorp-capacity p0 **390**, bfs p6
**216**, apple p2 **3**. *Falsifier:* accept every proposed run unconditionally (delete the
`is_matrix_candidate`/`region_tiles` gate) → all four fail. This is the test that pins § 2's D2 and
§ 3.2, and it is the reason the change is safe on 5 of the 7 documents.

**O3 — corpus-wide, per page: a merge never loses asserted ink.** For every corpus document and
page, `RegionReport.tokens_asserted` summed over the page must be **≥** the pre-merge baseline.
*Falsifier:* force-accept a run that loses ink (bfs p6's `3..10` is the measured 216-cell case) → the
assertion fails on that page. **This is the standing oracle for `R168`**: it generalises to any
document later added to the corpus, which is exactly what a runtime guard tuned to today's evidence
would not.

**O4 — the index space is single and consistent.** On apple p0 and p1, `page_bands` returns **3**
bands; the merged band occupies index 2 and mints `#mtable2`; every `RegionReport`'s position equals
the `tab:bandIndex` on its decision-log nodes; `tests/etkl/test_typing_equiv.py`'s `EXPECTED_VERDICTS
["apple"]` becomes a **3**-entry list (it is an 8-entry positional list today, `:70-79`) and its
`stem` / `cbh` / `capacity` lists are **unchanged**. *Falsifier:* leave the merge out of `page_bands`
and apply it inside `compile_tables`' loop instead → the driver's inventory and the report list
disagree, and the `tab:bandIndex` equality fails.

**O5 — the NON-TAIL merge, which no corpus document exhibits (§ 1.3).** The fixture is not a new PDF:
the repo ships **no** synthetic-PDF capability (`find tests -name '*.pdf'` → nothing; no
reportlab/fpdf dependency), so inventing one is a dependency decision this loop should not make.
Force it on a **real** page instead by patching the **disposal**, never the geometry: bfs p5 produces
runs `(2,5)` and `(7,8)` on a **15-band** page, both non-tail (9 and 6 bands would renumber), and both
are refused today. With `region_tiles`/`is_matrix_candidate` patched to accept `(2,5)` for that one
call, assert that `page_bands` returns **12** bands, that band indices are `0..11` with no gap, that
every minted `#tableN`/`#regionN`/`#mtableN` fragment matches its report position, and that a
document-scope `compile_document` over bfs completes with adoption's `grid_idx ==` the page's band
count. *Falsifier:* merge into a copy that preserves the original indices → the gap check fails.

**MEASURE, do not assume, before writing O4 and O5** (plan rule 3): **20 test files pin a band
index** (spike § 8.5(d)). Run them and report which actually change; do not infer the list from
reading them, which is how § 8.5(d) itself was produced and is flagged unverified there.

---

## 6. Interfaces — signatures and invariants only (plan rule 1)

No function body appears in this spec or in the plan written from it.

**Vocabulary — two new declared terms, both in a namespace we own** (`tab:` =
`https://w3id.org/iladub/tab#`, under the `iladub` root; CLAUDE.md § Source ownership):

- `tab:RuledBand` — the evidence-graph class for a band carrying rules. **Not** `tab:SectionBand`:
  that class's producer (`sectiongraph.section_evidence`) abstains for any band whose header box is
  not locatable, so the two populations differ and conflating them under one class would make the
  new derivation silently inherit that abstention.
- `tab:ruleX` — one distinct rounded rule x-position. Declared beside `tab:ruleXsSignature`
  (`vocab/ontology/tab.ttl:306`), same 2dp rounding, **no new constant**.

Both **must** be declared: `tests/test_query_declarations.py` / `tests/test_query_terms.py` fail on a
query naming an undeclared term.

**Derivation** — one new `vocab/queries/*.rq`, `SELECT ?a ?b`, adjacent (`?b = ?a + 1`) comparable
pairs; subsumption as a page-local `FILTER NOT EXISTS { … FILTER NOT EXISTS { … } }`. **No numeric
literal.**

**Python:**

| symbol | contract |
| --- | --- |
| `sectiongraph.run_evidence(bands) -> Graph` | sibling of `section_evidence`; one `tab:RuledBand` per band **that carries rules**, with its `tab:bandIndex` and one `tab:ruleX` per distinct rounded x. A band with no rules emits nothing and can never join a run. |
| `sectiongraph.merge_run_candidates(bands) -> tuple[tuple[int,int], ...]` | maximal contiguous runs as `(first,last)`, **disjoint**, ascending by `first`, deterministic. Mirrors `section_candidates`' union/assembly role over the derived pairs. |
| `compile.merge_bands(bands, first, last) -> Band` | promoted from `scripts/one_band_matrix_spike.py:37-55` **with its docstring's contract intact** — lines in document order, extent the run's, rules/hrules/captions/unit_markers concatenated, `column_xs` from the run's first band that carries any and **never unioned**. |
| the disposal | offers the merged band to the chain at `compile.py:817-840` on a **scratch** graph. **Reuse that chain; do not copy it** — a copy is a second reading path that can drift, which is the defect `page_bands`' own docstring exists to prevent. |
| `compile.page_bands` | **signature unchanged.** Returns the merged list. Upholds **M1** (§ 3.1): the partition is a pure function of the `section_repair=False` build. Its docstring's band-index contract must be extended to say what a band index now names — a band, or a merged run of bands — because that docstring is what three other modules are written against. |

**Invariants:** M1 (§ 3.1) · one index space, `page_bands`' returned list (§ 3.0) · a refused run
leaves the page byte-identical to today (§ 3.2) · accepted runs are disjoint (§ 3.2).

---

## 7. Residues to raise (register rows, numbered by the plan)

- **`R168`** — *`is_matrix_candidate` is the sole guard on 976 asserted cells it was never specified
  to guard.* Under the § 3.3 relation, graincorp-capacity p0 `1..3` (390 cells) and graincorp-stem p0
  `1..2` (586 cells) become proposed runs joining a **title** band to the page's main table on a
  strict-subset rule signature; only `is_matrix_candidate`'s refusal keeps them. Measured this
  session (§ 3.3, Q3). Deferred because the runtime guard is not implementable where the decision
  lives (§ 3.3) and no document exhibits the failure. Closed by either a demonstration that the
  refusal is principled for this class, or a no-regression comparison at a seam that can afford it.
  **O3 is its standing detector.**
- **`R169`** — *the non-tail accepted merge is still corpus-unevidenced.* O5 forces it by patching
  the disposal, which pins the index machinery but is **not** a document that exhibits the case.
  Closed by a corpus document whose accepted run is not a page tail.
- **`R170`** — *entry count and cell count are different counters.* "124 entries vs 48 cells today"
  compares `assert_matrix_region`'s return against `RegionReport.cells`; **no content diff has ever
  been run**, so nothing shows the 48 cells asserted today are all present among the 124. O3's token
  ledger bounds the ink but does not identify the cells. Closed by a content-level diff of the two
  readings on apple p0.

---

## 8. Unverified or assumed

- **Nothing in § 3 is implemented or run.** Every disposal figure in § 3.3 comes from an instrument
  that merges bands **after** `page_bands` returned; nothing shows `page_bands` can be
  restructured to propose a run and fall back cleanly, and nothing shows what M1 costs.
- **No document score was measured in this session.** The `0.1895 → 0.6289` headline is spike § 8.4's,
  measured with `validate_shapes=False` — **the membrane was never exercised on a merged band.**
- **The 20 index-pinning tests were not run against a merged compile**, here or in the predecessor.
  § 8.5(d)'s list is read off their source.
- **The relation is adjacent and transitively chained, never pairwise-total.** apple p1 bands 4 (10
  x's) and 6 (7 x's) are joined *through* band 5; `set6 ⊂ set4` happens to hold but the relation never
  checks it. A page whose chain drifts through incomparable endpoints is **unmeasured** — none occurs
  on this corpus.
- **`merge_bands`' `column_xs` provenance was not audited** for the longer runs the new relation
  produces (e.g. ons p8 band 0 vs band 1): only the end-to-end refusal was observed.
- **`page_bands` cost is measured; the merged cost is not.** § 3.5 prices today's calls and the
  rejected full-enumeration design, not the shipped one.
- **The 2dp rounding in `_rule_xs_signature` is inherited, not justified here.** It predates this loop
  and this loop does not re-derive it; a subsumption relation is more sensitive to it than equality
  was, and that sensitivity is unmeasured.
- **`R160` is not ruled** (§ 4 item 3) and **`R166` is not closed** (§ 4 item 4).
- Suite state: nothing was run beyond the two scratch measurement scripts. **The full suite takes
  ~45 minutes; budget for it, and do not run it in a background subagent** (a measured trap — see
  `docs/superpowers/2026-09-02-the-body-starts-at-the-stub-handoff.md`).
