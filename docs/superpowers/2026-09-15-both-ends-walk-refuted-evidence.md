# The both-ends refusal walk is refuted: it reaches six columns by cutting the boxhead

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity.

**Date:** 2026-09-15. **Tree:** branch `r232-both-ends-refusal-walk`, cut from `main` at `45480de`
(the merge of PR #226, which carries the re-ruling this document answers).

**Doc impact: none.** No released term, vocabulary, shape, contract or instrument changes. This
loop ships evidence and register rows; it deliberately ships **no behaviour**.

**Authored OVER the originating floor.** `plimslop preflight --shape originating --tokens 55000
--decision proceed` logged an OVERRIDE. § 5 is therefore graded per action.

---

## 0. What was ordered, and what this loop did instead

`2026-09-15-two-ended-peel-refuted-handoff.md` § 8e re-ruled: **build the both-ends refusal walk**
(rules-free scope, ≥2-keep guard), on the strength of § 8c's measurement that it fires on exactly
one band corpus-wide with no tuned constant. § 8e also recorded the mechanism as *"no longer a
prediction … measured end to end"*, leaving only the wiring unbuilt.

It was not built. Re-measuring its premises first — CLAUDE.md § Plan authoring discipline rule 2,
and the previous loop's own § 6 order that a failed premise means *"write the refutation and hand
back"* — **refuted it**. Every figure below is this session's own run.

**The one-line finding:** the walk reaches six columns **by cutting the column header off the
band**, and the table it then asserts carries five numbers and a date as its column labels.

---

## 1. The mechanism reproduces exactly as § 8 describes it

§ 8e's four-line repro, re-run verbatim:

```
full 1   T=1 1   L=6 3   both 6
```

A corpus census written from scratch for this loop (`both_ends_walk_census.py`, method in § 6)
reproduces § 8c independently:

```
corpus: 7 documents   pages=27  bands=191  rules-free=106
pages with NO datagrid=11 (carrying 64 rules-free bands -> abstain)
abstentions: all-refused 25, ambiguous-ink 1, keep<2 4, no-op(L=0,T=0) 11

BOTH-ENDS refusal walk, RULES-FREE only, >=2 lines kept
  ons-index-of-services-2026-02.pdf p4 b0 lines=32 L=6 T=1 ncols 1->6 kind NON_TABLE->UNSUPPORTED_TABLE
      FIRST KEPT LINE: 'Jan 2024 -0.1 -0.3 0.2 0.1 -0.2'
rules-free bands cut by the BOTH-ENDS walk: 1
```

**So § 8c is confirmed on its own terms**: one band, no tuned constant, and the ≥2-keep guard is
load-bearing (29 bands abstain through it — 25 `all-refused` plus 4 `keep<2`). Two notes the
earlier census did not carry:

- **`abstain/ambiguous-ink` fires once.** [[R233]]'s translation hazard is **live, not latent**:
  one corpus band has a line that re-identifies to no unique page line. Offset arithmetic would
  have read another line's verdict there silently.
- The 11 grid-less pages carry **64 rules-free** bands (the earlier figure, 78, counts all bands).

## 2. The refutation: four of the seven cut lines are the column header

The cut is `L=6, T=1` — seven lines, **77 of the band's 252 words (31% of its ink)**:

```
CUT 'Table 1: Revisions to month-on-month growth for Index of Services and its sectors'  furniture
CUT 'February 2026 release compared with January 2026 release, percentage growth, …'     furniture
CUT 'Sections G & I - Sections H & J - Sections K to N Sections O to T'                  <- HEADER
CUT 'Date IoS Distribution, Transport, - Business - Government'                          <- HEADER
CUT 'Hotels and Storage and Services and and other'                                      <- HEADER (wrap)
CUT 'Restaurants Communications Finances services'                                       <- HEADER (wrap)
CUT 'Source: Index of Services estimate from the Office for National Statistics'         furniture
```

Lines 3–6 are the four-line wrapped boxhead [[R230]]'s row already describes: *"25 rows x 6 columns
(`Date`, `IoS`, and four SIC section columns) under a four-line wrapped header."* The walk cuts it.

**This is the defect [[R232]] itself records**, now inside the rules-free scope that § 8d declared
safe. § 8d asserted: *"Within that scope the walk fires once and cuts no header anywhere."* On the
single band it fires on, that is **false**.

### 2.1 What the walked table asserts as its column identity

Compiled with the walk wired in at the correct seam, ons p4 region 0 mints `p4#htable0` with six
`tab:HeaderNode`s (`h0..h5`, all `headerLevel 0`). Their labels:

```
h0 'Jan 2024'   h1 '-0.1'   h2 '-0.3'   h3 '0.2'   h4 '0.1'   h5 '-0.2'
```

Five numbers and a date. The region carries `header_reading=None` and asserts **168 cells** under
them. This is [[R166]]'s signature verbatim — *"the record-table reader takes the band's first line
as the header row, and the tiling oracle is satisfied because that 'header' covers every column —
numbers asserted as column labels"* — so the mechanism **manufactures a new instance of an open
defect**, on the one criterion whose subject is column identity.

## 3. The gutters are closed by the FURNITURE, not by the header

§ 8b explains the trailing-only no-op by *"the leading furniture is what closes the gutters."* That
is right about the cause and wrong about the extent. Sweeping the cut depth on the same band
(`infer_leaf_grid` + `classify`, no compile):

```
(L,T)  ncols  kind                reason                       first kept line
(0,0)   1     NON_TABLE           fewer than 2 columns         'Table 1: Revisions to month-on-month…'
(0,1)   1     NON_TABLE           fewer than 2 columns         'Table 1: Revisions to month-on-month…'
(2,0)   3     UNSUPPORTED_TABLE   header has 18 words but 3 c  'Sections G & I - Sections H & J …'
(2,1)   6     UNSUPPORTED_TABLE   header has 18 words but 6 c  'Sections G & I - Sections H & J …'
(3,1)   6     UNSUPPORTED_TABLE   header has 8 words but 6 c   'Date IoS Distribution, Transport, …'
(6,1)   6     UNSUPPORTED_TABLE   header has 7 words but 6 c   'Jan 2024 -0.1 -0.3 0.2 0.1 -0.2'
```

**`(2,1)` reaches the same six columns with the boxhead intact.** Cutting only the two furniture
lines and the trailing `Source:` line closes every gutter. The walk's four extra lines of depth buy
**no additional column** and cost the entire column identity.

## 4. And the honest cut scores WORSE — which is the whole point

Document scope, `compile_document`, all figures this session's own:

```
                       doc score      p4 score   region 0                     cells  denominator
BASELINE       (0,0)   0.7712418301   0.527778   NON_TABLE / ignored            0        765
FURNITURE-ONLY (2,1)   0.7522123894   0.673611   UNSUPPORTED_TABLE/superseded   0       1017
WALK           (6,1)   0.8063829787   0.886256   UNSUPPORTED_TABLE/asserted   168        940
```

The cut that **keeps** the header scores **below baseline**. The cut that **discards** it scores
`+0.0351411487`. The gain is bought by asserting 168 cells under fabricated labels, while the
honest reading books 1017 tokens of denominator and asserts none of them.

**The denominator does not shrink under the walk** (765 → 940; asserted 590 → 758, escalated
175 → 182), so this is *not* the score-rise-is-a-collapse artifact — no ink vanishes from the
ratio. It is worse in kind: the ink is present, and **mislabelled**. A membrane that counts cells
cannot see the difference; § 7 (*only emit what the source supports*) is what refuses it.

`(2,1)`'s `superseded` verdict and its 1017-token denominator are the honest exposure of the real
blocker: a **four-line wrapped boxhead**, 18 words against 6 columns, which the header reader
cannot split. That is [[R226]]/[[R166]] territory, and it is raised as [[R234]].

## 5. No other document moves

All 7 corpus documents, baseline vs walked, `compile_document`:

```
cbh-stem-2026-08-03.pdf             same   0.9095022624 -> 0.9095022624   fired=[]
graincorp-capacity-2026-08-04.pdf   same   1.0000000000 -> 1.0000000000   fired=[]
graincorp-stem-2026-07-31.pdf       same   0.9658886894 -> 0.9658886894   fired=[]
apple-fy2026q3-statements.pdf       same   0.9302325581 -> 0.9302325581   fired=[]
bfs-population-bilan-2023.pdf       same   0.8850746269 -> 0.8850746269   fired=[]
ons-index-of-services-2026-02.pdf   MOVED  0.7712418301 -> 0.8063829787   fired=[(p4, b0, L=6, T=1)]
who-wfa-boys-zscore-0-5.pdf         same   0.9156327543 -> 0.9156327543   fired=[]
```

The safety half of § 8a is therefore **confirmed at document scope**: the walk is inert everywhere
but ons p4. Safety was never the problem. **What it does where it fires is the problem.**

## 6. Method, and a measurement error worth recording

**The seam.** `compile_tables` resolves `page_bands` through `compile`'s own module global
(`compile.py:820`, the only internal call site). `document.py:111` binds its own name at import.
**Patching `document.page_bands` alone fires the walk and changes nothing** — the regions are built
from `compile`'s reference.

This loop made that error first, and it produced a clean, wrong result: `delta = +0.0000000000`
under both carriage variants, which reads exactly like a refutation. It was caught only by dumping
region 0 and noticing its `ascii` still contained the lines the walk reported cutting. **A null
result is not self-validating** — the diagnostic that distinguishes "the mechanism does nothing"
from "the mechanism never ran" is the same diagnostic either way, and it must be run before either
claim is written down.

**Translation** is by `donation._ink_key` with a uniqueness guard ([[R233]]), never `offset + j`; a
band with any non-unique line is abstained whole. **Carriage variants A (drop) and B (leading cut →
`Band.captions`) were measured and are identical** — `0.8063829787`, 168 cells, `tok=168/7` — so
carriage cannot be chosen on score. B additionally types the cut lines `tab:SectionCaption`, which
`feed._table_captions` (`feed.py:411`) reads as candidate-key evidence, so it carries the
stem-pollution risk that scoping was introduced to fix, for no measured gain.

**Two wiring facts, measured, that survive the refutation** (they bind whatever is built next):

- **The merge partition cannot be perturbed.** `sectiongraph.run_evidence` emits a node only for
  bands that carry rules (*"A band with NO rules emits NOTHING"*), and `band-run.rq` matches only
  `tab:RuledBand`. A rules-free band emits nothing, and replacing a band in place preserves count
  and order, so `merge_run_candidates` is unaffected.
- **Any such walk must run before `compile.py:447`.** `absorb_unit_markers` omits a line whose
  words are all markers (`unitmarker.py:116-118`), which would break ink-key translation against
  the raw page lines. [[R233]] measured 0 occurrences corpus-wide; the ordering is required on
  mechanism, not on that count.

## 7. What this loop does NOT claim

- **It does not refute [[R230]]**, whose reading of ons p4 stands and is corroborated here.
- **It does not refute the walk's safety.** § 8a's two questions were confirmed, and § 5 above
  extends that to document scope.
- **It does not establish that `(2,1)` is the right cut.** `(2,1)` was measured, scores *below*
  baseline, and is offered as the diagnosis of the real blocker — not as a remedy to build.
- **It settles nothing about etkl:04.** ons carries no `cor:scoreFloor` and stays
  `cor:Unadjudicated`; its 2026-08-20 HOLD rests on nine pages never having been read against the
  compile and on the document carrying no contract/terms/shapes. None of that changed today.
- **No `cor:reading` was appended** to `tests/corpus-manifest.ttl`: no shipped behaviour changed,
  so the document's reading at HEAD is still `0.7712418301` — re-measured this session and
  identical to the recorded 2026-09-14 value.
