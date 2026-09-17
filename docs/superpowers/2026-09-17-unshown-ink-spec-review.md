# Review — the ink the page does not show: attacking the spec's premises

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: none.**

The adversarial review `2026-09-17-unshown-ink-handoff.md` § 5a asserted, run in a fresh session
against `specs/2026-09-17-the-ink-the-page-does-not-show-design.md` (PR #262). The handoff's § 5a
says a reviewer *"should not be limited to"* the spec's own § 7 list of weak parts. **None of the
eight findings below is on that list.** The handoff's § 5b — run O1 on cbh first, before building
anything — was also carried out; it is the last section.

Every figure is instrument output, run on branch `the-ink-the-page-does-not-show` at `e8d1685` with
`./.venv/bin/python`. The probes are in this session's scratchpad; each is reproduced below in the
form that matters — the command, and its output verbatim.

**Verdict: five of the eight findings are blocking for the spec as written.** The term (§ 2), the
carriage (§ 3) and the oracle (§ 4.3, three ways) each name a seam the pipeline does not have. The
*design* — a disagreement between the text layer and a reader of the render — **survives, and is no
longer only proposed**: O1 and O2 were RUN blind (below), O1 did not fire and O2 hit **110 of 110 by
set identity on the first attempt**. What is refuted is where the spec attaches the design, and what
it forgot to ask the worker for.

---

## RF1 — BLOCKING. The term is attached to a class that never reaches the compiled graph

§ 2.3 declares `tab:unshownText` with `rdfs:domain tab:GridCell`. § 2.4 builds the membrane on
`tab:GridCell`, and calls its second clause — *a `tab:UnshownInk` cell may not be the source of an
asserted contract value* — **"R213's whole point and the one shape that must exist"**.

`tab:GridCell` is not in the compiled graph. It is a **transient** classification-evidence class:

```
$ ./.venv/bin/python -c "…compile_document('corpus/ag-trade/graincorp-capacity-2026-08-04.pdf')…"
triples: 5859
  BBox 415   EntryCell 406   Option 46   LeafRow 27   DecisionHolon 18   LeafColumn 16
  HeaderNode 9   LabelCell 9   Process 6   SourceRegion 4   IgnoredBand 4
  HierarchicalTable 1   MembraneValidation 1   SoftwareAgent 1   CompiledDocumentHolon 1

GridCell in compiled graph: 0
gridText triples:           0
```

`celltype.grid_evidence` (`src/iladub/etkl/celltype.py:136-160`) opens a local `Graph()`, mints
`_EV["cell-%d" % i]` — a **positional** IRI, re-minted per call — and the caller discards it. It ran
**11 times on graincorp-capacity and 43 times on cbh-stem** in one compile (instrumented at the
function, not read):

```
cbh-stem-2026-08-03.pdf:           grid_evidence called 43 times, 7642 cell tuples
graincorp-capacity-2026-08-04.pdf: grid_evidence called 11 times, 4135 cell tuples
    text=='0': 1100
```

So a SHACL shape over `tab:GridCell` would validate a graph that is built and thrown away inside
`celltype`, is never seen by `tab:MembraneValidation`, and whose subject IRIs do not survive the
call. **The second clause has no subject at all**: nothing in the output graph can be *the source of*
an asserted contract value via a `tab:GridCell`, because no `tab:GridCell` outlives the classifier.

**The class that does carry it is `tab:EntryCell`** (`tab:EntryCell ⊑ tab:Cell`, `tab.ttl:39` — a
sibling of `tab:GridCell` at `tab.ttl:253`, related to it by nothing):

```
EntryCell count: 406
properties on EntryCell:  type 406  cellText 406  onPage 406  wasDerivedFrom 406
                          hasBBox 406  atRow 406  atColumn 406
EntryCells whose cellText is exactly '0': 110
sample: …/doc/p0#htable3-e13_12
   wasDerivedFrom …/doc/p0#p0-677-255   atColumn …#htable3-c12   atRow …#htable3-r13
   cellText 0   hasBBox N1bd473…   onPage 0
```

**Exactly the 110.** They are in the published graph today, with page provenance, and they are what
the contract reads.

**Where R213's false assertion actually happens** — `src/iladub/feed.py:246-256`:

```python
for e in graph.subjects(RDF.type, TAB.EntryCell):
    …
    txt = str(graph.value(e, TAB.cellText))
    if is_blank(txt):
        continue          # loop K: a placeholder has no content to ground
    …
    concept = SurfaceConcept(header.get(col, ""), txt, region)
```

That `continue` is the existing precedent for *a cell that mints no concept*, on the existing class,
at the site where the tonnage would be grounded. It is where an unshown cell must not pass.

**What this does NOT refute.** The abstention half of § 2.3 is correctly placed: homogeneity is
computed over the transient graph, so a cell that must not vote has to abstain *there*. The finding
is that the spec places the **published term, its property, and the whole membrane** on the transient
side, where none of them can do the work § 2.4 says they do.

## RF2 — BLOCKING. There are two crossings, and § 1.4 measured one

§ 1.4 (and **E5**) concludes: *"a per-cell fact that is not derivable from the text has exactly one
narrow place to cross: `headers._grid_cells`'s tuple, and the `grid_evidence` signature that reads
it."* § 3.1 builds the loop's only carriage on that sentence.

Two corrections, both measured:

1. **`_grid_cells` does not consume `regions.Cell`.** E5's narrative — *"a band cell already carries
   its `Word` objects and loses them at exactly one place"* — reads as though `regions.Cell.words`
   (`regions.py:34-41`) flows into `_grid_cells`. It does not. `_grid_cells(band, grid)`
   (`headers.py:66-81`) re-derives its own cells from `band.lines` and `grid.boundaries` via
   `column_of`, and never sees a `regions.Cell`. The `Word` **is** in scope there (`for w in
   ln.words`), so the seam is real and the fix stands — but the two cell notions are independent, and
   conflating them costs a factor of ten in reach:

   ```
   chars inside a regions.Cell bbox, whole corpus:   5962 / 59705   10.0%
   words inside a band that HAS a grid (_grid_cells): 8923 /  9351   95.4%
   ```

   On graincorp-stem the two differ maximally: **0.0%** by `regions.Cell`, **97.9%** by the seam that
   types. Anything reasoned from the first number is reasoned about the wrong population.

2. **The persisted crossing is a second crossing, and it is the one the contract reads.** RF1's
   `feed.py:246` reads `tab:EntryCell`, minted at `holon.py:45`/`datagrid.py:691`/`holon.py:629` —
   not from `grid_evidence`'s tuples. A fact carried only through `_grid_cells` reaches the
   homogeneity vote and **dies before the graph**. § 3.1's invariants therefore do not cover the
   membrane § 2.4 promises.

## RF3 — BLOCKING. The null control's population is empty exactly where the disposal runs

§ 4.3's oracle has two refusals. The first (an address outside the grid) is arithmetic. The second
is the one the spec argues for, citing R216:

> the **null control**: a worker that reads the page must also find the cells that are *genuinely*
> empty. If its answer set misses the cells the text layer already reads as `tab:Blank`, it is not
> reading the page and the whole region's answer is refused. […] a disposal that only ever accepts
> is not a disposal.

`tab:Blank` fires only on a cell that **is** in `_grid_cells`' output and whose joined text strips to
`""` or a `tab:nilSpelling` (`celltype.py:81-89`). A grid position with no words is never emitted, so
it is never `tab:Blank`. Counted over every gridded region of the corpus:

```
cbh-stem-2026-08-03.pdf      gridded regions= 6 cells= 664 tab:Blank=  0   regions with ZERO Blank: 6
graincorp-capacity…pdf       gridded regions= 2 cells= 408 tab:Blank=  0   regions with ZERO Blank: 2
graincorp-stem…pdf           gridded regions= 6 cells=2234 tab:Blank=357   regions with ZERO Blank: 3
apple-fy2026q3…pdf           gridded regions=11 cells= 305 tab:Blank=  1   regions with ZERO Blank: 10
bfs-population…pdf           gridded regions=41 cells= 847 tab:Blank=  0   regions with ZERO Blank: 41
ons-index-of-services…pdf    gridded regions=45 cells= 711 tab:Blank=  0   regions with ZERO Blank: 45
who-wfa-boys…pdf             gridded regions=11 cells= 763 tab:Blank=  0   regions with ZERO Blank: 11

CORPUS: 122 gridded regions, 5932 cells, 358 tab:Blank cells;
        118 regions (97%) have NO tab:Blank cell at all
```

**357 of the 358 are in one document, graincorp-stem** — and graincorp-stem has zero unshown glyphs,
so the worker never needs to run there. In particular:

- **graincorp-capacity band 3** — the one region that must type the 110 — has **0** `tab:Blank`
  cells of 406.
- **cbh-stem** — where O1 runs — has **0** of 664, in every one of its six gridded regions.

So on both documents the oracle reduces to *"is every address inside the grid?"*. A worker that
returns any in-grid set passes. CLAUDE.md § 8 as amended: **no oracle, no worker.** This is the same
shape the repo has now hit three times (a passing control that does not validate a join; a null
result that is not self-validating; *give every control a null*) — and the spec's own § 4.3 invokes
R216 for exactly this reason, then names a set that is empty where it is needed.

**Constructive: the live population is the UNPOPULATED GRID POSITION, not the `tab:Blank` cell.**

```
cbh  band1 (18 lines x 16 cols): cells with >=1 word 151/288; text-layer-EMPTY positions: 137
gcap band3 (27 lines x 16 cols): cells with >=1 word 406/432; text-layer-EMPTY positions:  26
```

That set is non-empty where it must be. **It is also not clean**, and the plan must say so: 25 of
gcap band 3's 26 empty positions are **column 0**, the spanning year label (`2025/26`, `2026/27`)
that occupies one line and leaves the rest of its column unpopulated — the exact construct
[[R211]] establishes a reader reads as *one* cell. A worker that calls that column "shows a mark"
for the whole span is reading the page correctly and would be refused. **The non-degenerate
population on the region that matters is one cell: (1, 6).**

## RF4 — The O1 control population is mis-identified: 24 glyphs, not 780, and a different colour

The handoff's § 5b, the spec's § 1.1 table and § 5, and **E7** all describe cbh's low-contrast
population as *"780 white-on-pale-blue glyphs … the port codes `ALB`/`ESP`/`GER`/`KWI` beside their
tonnages"*, at ratio **1.6887**. Counted by ink and backdrop:

```
cbh low-contrast chars by (ink, backdrop, ratio):
   ink=(1.0, 1.0, 1.0) on (0.588, 0.588, 0.588)  ratio=2.9601  ->  828 chars
   ink=(1.0, 1.0, 1.0) on (0.6, 0.8, 1.0)        ratio=1.6887  ->   24 chars
```

**828 of 852 are white on GREY at 2.9601** — the four vessel tables' column-heading rows (`VNA #`,
`Vessel Name`, `Time Nominated`, `ETA`, `Commodity`, …; E2's own glyph histogram, `[('e',100),
('m',64),('t',60),('o',52),('i',52),('T',48)]`, is heading words and says so). Only **24** are the
port codes on pale blue at 1.6887. The ratio was read off a printed one-row *sample* and the
population was narrated from it.

It matters twice:

- **O1 as designed tests an easier population than advertised.** The 828 it actually reaches sit at
  2.96, almost at WCAG's line; the spec's argument for O1 rests on 1.6887, *"lower than some visible
  ink would score against a different backdrop"*.
- **The 24 hardest glyphs are unreachable at cell grain** — see RF5. No per-cell question can be
  asked about them.

Rendered and read (220 dpi, `page.crop(...).to_image(...)`), the 828 are **plainly legible white
labels on a grey header strip**, and the crop also shows genuinely empty cells (`Other Port/s`,
most of `Loading Status`) — so the population is real ink and O1 is a real control. Its name and its
figure are wrong, not its existence.

## RF5 — For § 7: the disposal's grain is the cell; the phenomenon's grain is the glyph

§ 4's trichotomy is per cell (*does this cell show a mark?*). Whether that grain can express the
phenomenon is never stated as an assumption. Measured, at the typing seam:

```
== gcap hidden set (110)          low-contrast chars: 110
   PURE  (cell holds ONLY low-contrast ink): 110 cells, 110 chars
   MIXED (cell holds low-contrast AND ordinary ink): 0

== cbh low-contrast control       low-contrast chars: 852
   accounted for inside a typed cell: 836
   PURE : 80 cells, 812 chars
   MIXED:  8 cells,  24 chars
       band9 r1 c1: 'ALB 1 - 15 October'
       band9 r2 c0: 'ALB 129,183 APW1/ASW9/AWW1 27,023 3,345 1,293 160,845'
```

**gcap is the easy case, and that is a property of gcap.** All 110 hidden glyphs are alone in their
cells, so a per-cell answer is lossless there. cbh already holds 8 cells that mix the two, and for
those the per-cell question has no true answer: the cell *does* show marks, and also holds ink it
does not show. Today that is harmless — cbh's low-contrast ink is visible — but it is an existence
proof, in this corpus, that the grain assumption is not free. It belongs in § 7 as a fifth weakness,
and it bounds what the term can ever claim: **`tab:UnshownInk` types a cell all of whose ink is
unshown, and the spec should say so.**

---

## O1 and O2 were RUN, blind — the handoff's § 5b. Both pass, and the run raises three findings

The handoff's § 5b asserted O1 *"before building anything, and before gcap"*. It was run as the
spec's § 4.3 worker: a reader with **no context** — no repo, no spec, no knowledge that hidden ink
exists — given only two 220-dpi region crops, the grid dimensions, and the closed question *which
cells of this grid show no mark at all?* It was given both documents at once, gcap included, so the
control could not be answered by elimination.

### O1 — PASSES. cbh does not over-fire

The reader's verdict on `cbh_b1` (18 × 16, the region holding 828 of the 852 low-contrast glyphs):

> Header row — **yes**, all 20 header cells carry text. It is white on mid-grey (contrast ≈ 2.9:1) —
> the lowest-contrast printed text in this image, but plainly legible.

and, asked directly whether anything is present but unseeable:

> **No.** I checked every blank cell pixel-by-pixel … There is no faint, tinted or
> same-colour-as-fill glyph anywhere in this image.

**The spec's named falsifier did not fire.** § 4 survives its own strongest test.

### O2 — PASSES by SET IDENTITY, 110 of 110, on the first blind run

The reader returned 110 `(row, col)` addresses for gcap band 3. Graded against the pipeline's own
hidden set — the same cell-by-cell identity R213's amendment established, not a matching count:

```
pipeline hidden chars: 110   distinct (row,col) cells: 110
worker addresses: 110
IDENTICAL: True
  worker only (false positives): []
  truth  only (missed):          []
```

It also passed the null control in the repaired form RF3 prescribes: it found all 25 unpopulated
positions of the spanning year column **and** singled out **(1, 6)** — the one navy cell that carries
no glyph, R213's own recorded exception (Fisherman Islands, 2025/26, September 1st Half), which is
the only non-column-0 empty position in that region. It was not told such a cell existed.

### RF6 — BLOCKING for § 4.3. The worker rejected the supplied grid, and the oracle cannot see that

On gcap it accepted the grid (*"the stated grid matches exactly: 27 rows × 16 columns"*) — which is
why O2's identity check is meaningful. On cbh it did not:

> **Caveat on the stated grid.** You described it as 18 rows × 16 columns. What is actually drawn is
> **20 columns** … and, vertically, **13 bands** … I cannot make 18 × 16 out of what is on the page,
> so I report by **column header name** below.

It is not wrong: 21 full-height rules are drawn, and the pipeline read 16 columns. But § 4.3's
contract is *"In: the crop and its grid dimensions. Out: `(row, col)` addresses"*, and its only live
refusal is *"any address outside the grid"*. **A worker answering in a different address space
returns addresses that are all inside the stated grid and all mean different cells** — admitted in
silence. This fired on the first run, on the control document, and it is not the failure mode § 5
predicted. The contract needs a refusal with a direction: the worker must be able to say *"this is
not the grid I see"*, and that abstention must refuse the region.

### RF7 — BLOCKING for § 4.1. The worker answered as an image analyst, not as a reader

The disposal is defined as a disagreement between the text layer and **a reader of the rendered
page**. The whole claim to be threshold-free rests on that word. Unprompted, the reader said how it
actually got the answer:

> I only resolved them by magnifying 4× and stretching the contrast — at which point a "0" is
> unmistakable in each. … I would not have reported them from the image as displayed, and did not,
> until I boosted the contrast.

and, for the blanks:

> Anything I have called "no mark at all" … I confirmed by **pixel uniformity, not by eye**,
> precisely because eyesight is not reliable against a 1.09:1 ratio.

It even reported the glyph and fill RGB values and their contrast ratio (1.09:1) — **§ 1.1's refuted
colour instrument, re-entered through the worker.** The answer is right, and the route is the one
the spec closed. Left unconstrained, a capable vision worker will do image analysis, and then every
§ 1.1 refutation applies to it again: the same enhancement that resolves gcap's 110 at 1.0856 would
resolve cbh's 24 port codes at 1.6887, which are ordinary ink.

**The constraint is satisfiable** — the same run reports what a reader sees, unenhanced:

> To a reader at normal size, *no* row of this image looks fully printed — every row has between 2
> and 6 cells that look empty and are not.

That sentence is the disposal § 4 wants. § 4.3 must ask for it in those terms and forbid
enhancement — and must accept that the prohibition is **unenforceable from the answer alone**, which
is a harder problem than § 7 admits.

### RF8 — minor. The worker returned a value that is on the page

§ 4.3: *"Addresses, not values — nothing the worker returns is a value on the page."* It returned
`14,000` (gcap row 0, column 14) while explaining which column was hidden. Harmless here; the
contract's closed output shape must make it impossible rather than ask for it.

---

## Measured for the plan (§ 7.2's two deferred items, and the cost)

The spec deferred region count and crop legibility to the plan (plan rule 3). Both are cheap and
were taken here, so the plan need not:

- **122 gridded regions** corpus-wide (17 RECORD_TABLE, 44 UNSUPPORTED_TABLE, 61 of 130 NON_TABLE
  bands carry a grid). graincorp-capacity has 2; cbh-stem 6.
- **Render cost: 0.05 s – 0.54 s per region crop** at 220 dpi (`page.crop().to_image()`), the first
  call on a page carrying the page-load cost. Not a gate at this corpus size.
- **Legibility: yes, at region grain.** graincorp-capacity band 3 is 295 pt tall, 27 × 16, and its
  220-dpi crop reads cleanly: every row label, every `Y`/`N`, every tonnage — and the navy cells are
  **visually empty**, as R213 and E7 record. The crop does **not** contain the column headers (they
  are in band 2, a different region), so a per-region ask is addressed by index only, with no column
  labels to check itself against.

## What survives

**The design survives every finding.** A disagreement between the text layer and a reader of the
render is still the only disposal on the table that is threshold-free and generalises beyond one
publisher's palette; § 1.1's refutation of the colour-instrument class is untouched (it is a claim
about glyphs, and RF4 corrects the label on its cbh row, not its arithmetic); § 2.2's fork (a
datatype, not a proposition) is untouched; § 1.2's "no colour in `src/`" is untouched and RF1
strengthens it.

What the spec must move: the term and the membrane from `tab:GridCell` to `tab:EntryCell` (RF1), the
carriage from one crossing to two (RF2), and the null control from `tab:Blank` to the unpopulated
grid position, with the spanning-column confounder stated (RF3).

---

## RF7 tested and CONFIRMED: the reader's answer, unenhanced, is exactly the disposal

RF7 said the worker answered as an image analyst and that the prohibition it needs is *satisfiable
but unenforceable*. The satisfiable half was not left as a proposition. A **second** blind reader was
run on the same two crops with the question reframed — *which cells **appear empty to you***, you
look at that place and see nothing — and with magnification, contrast adjustment and pixel sampling
**explicitly forbidden**. It was told nothing about the first run, about hidden ink, or about what it
was being tested for.

It returned a 136-cell "appears empty" set for graincorp-capacity band 3. Graded against the
pipeline:

```
reader says APPEARS EMPTY: 136 cells
ground truth: 110 hidden-glyph cells + 26 unpopulated = 136 cells a reader should see as empty
  reader set == hidden u unpopulated ?  True
  reader only: []
  missed:      []

THE DISPOSAL: reader-says-empty AND text-layer-has-a-glyph
  110 cells; identical to the 110 hidden cells? True
  false positives: []   missed: []
```

**Exact, both ways.** The reader's unenhanced answer is the union of the hidden cells and the
genuinely unpopulated ones — which is precisely what a reader of the page *should* say — and § 4.1's
disagreement against the text layer resolves it to the 110 with no false positive and nothing missed.
It correctly excluded **(0, 14)**, the one cell of column 14 that prints `14,000`, and correctly
included **(1, 6)**, the navy cell with no glyph, without being told either existed.

Three consequences:

1. **§ 4.1's "a reader of the rendered page" is not a figure of speech, and it is achievable.** The
   spec may ask for the reader's answer and get it. The enhancement route (run 1) and the reading
   route (run 2) reach the same 110 here, but only the second is the one § 1.1 leaves standing.
2. **The repaired null control comes free.** Run 2's answer *is* its own null control: the same set
   carries all 26 unpopulated positions, so nothing separate has to be asked or refused. RF3's
   repair and RF7's reframing are one change, not two.
3. **The prohibition is still unenforceable from the answer alone** — run 1 and run 2 returned the
   same 110 by different routes, so the output cannot distinguish them. What is now known is that the
   *honest* route works, which was the open question. A spec can ask for it and test for it on a
   control page where the two routes would diverge; it cannot detect a defector from one answer.

### RF6 is reinforced: two blind runs disagree with the pipeline AND with each other

Run 2 also rejected cbh's supplied grid, independently:

> I see **16 horizontal bands** of cells and **20 columns**, not 18 × 16.

Run 1 saw **13** bands and 20 columns; run 2 saw **16** bands and 20 columns; the pipeline reads 18
lines and 16 columns. **Both readers agree the page draws 20 columns and neither agrees with the
pipeline's 16, and they do not agree with each other on rows.** Run 2 named the likely cause without
being asked — *"the column-header row is one band, but two lines of text tall … if you counted text
lines rather than cell bands, this is where your extra rows most likely come from"*. A contract that
takes `(row, col)` addresses from a worker, over a grid the worker does not accept, has no sound
address space, and § 4.3's in-grid check cannot see it. On gcap, where the grid does match
(*"27 rows × 16 columns matches what I see"*), both runs were exact — which is the same finding
stated positively: **the address space is only shared when the pipeline's grid is the one the page
draws, and the worker must be able to say when it is not.**

O1 passes at reader grain too: run 2's cbh blanks are `Other Port/s` and the three
`Loading`-completion columns, all genuinely blank, and it reported no hidden ink anywhere.
