# Handoff — the unshown-ink spec is reviewed: the design holds, respec the three seams

**Topic:** [[R213]]'s spec was attacked in a fresh session per its handoff's § 5a, and O1/O2 were run
blind per § 5b. **Both oracles pass — the disposal works** — and five of the eight findings are
blocking, all of them about *where* the spec attaches the design rather than the design itself. The
next session respecs §§ 2.3, 2.4, 3.1 and 4.3 against measured seams.

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: none.**

Written with part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". **plimslop reports
no measured turn for this project this session**, so the working-token figure is absent rather than
withheld — as it was in the predecessor handoff. The review itself is measurement and reporting, not
originating work; the respec below is deliberately *not* started here for that reason.

## 5. The next concrete action

### 5a. ASSERTED — respec §§ 2.3 / 2.4 / 3.1 onto `tab:EntryCell` and two crossings

Mechanical: the review measured where every piece actually lives, so the outcome is known and doing
it *is* the work. `2026-09-17-unshown-ink-spec-review.md` §§ RF1–RF2 carry the figures.

- The published term's property and the **entire membrane** move from `tab:GridCell` (transient,
  **0** of graincorp-capacity's 5859 compiled triples, positional IRIs minted 11 times per compile
  and discarded) to **`tab:EntryCell`** (**406** on that page, **exactly 110** carrying
  `tab:cellText "0"`, with `atRow`/`atColumn`/`hasBBox`/`onPage`/`wasDerivedFrom` already on it).
- § 2.4's second clause — *may not be the source of an asserted contract value* — becomes
  constructible for the first time, because `feed.py:246-256` is the site that reads `tab:EntryCell`
  and mints the `SurfaceConcept`. Its `if is_blank(txt): continue` is the existing precedent for *a
  cell that mints no concept*, on the existing class.
- § 3.1 keeps its `_grid_cells` carriage — the **abstention** half genuinely belongs in the transient
  graph, since that is where homogeneity is computed — and gains a **second** crossing for the
  persisted cell. § 1.4's *"exactly one narrow place to cross"* is false and must be struck.

### 5b. ASSERTED — repair § 4.3's oracle in four named places, and only those

Each has its measurement in the review; none needs re-deriving.

1. **The null control's set is the UNPOPULATED GRID POSITION, not `tab:Blank`** (RF3). `tab:Blank`
   is empty on 118 of 122 gridded regions, **0 of 406** on gcap band 3 and **0 of 664** across cbh —
   357 of its 358 corpus instances are in graincorp-stem, which has no hidden ink. The live set is 26
   positions on gcap band 3 and 137 on cbh band 1. **State the confounder in the spec**: 25 of gcap's
   26 are column 0, the spanning year label ([[R211]]'s construct), so the non-degenerate population
   on the region that matters is **one cell, (1, 6)**.
2. **Add a grid-disagreement abstention** (RF6). The blind worker rejected the supplied grid on cbh
   (*"you described it as 18 × 16; what is actually drawn is 20 columns"*) and answered by column
   name. Addresses in another address space are all *inside* the stated grid, so the only live
   refusal admits them silently. The worker must be able to return *"this is not the grid I see"*,
   and that must refuse the region.
3. **Forbid image enhancement in the ask** (RF7) — see 5c, which is the part that is not mechanical.
4. **Make the output shape address-only** (RF8). The worker returned `14,000`, a value on the page,
   against § 4.3's own *"addresses, not values"*. A closed shape should make it impossible rather
   than request it.

### 5c. ASSERTED — the enhancement prohibition is SATISFIABLE; it was tested and confirmed here

§ 4.1 defines the disposal as a disagreement between the text layer and **a reader of the rendered
page**. The whole claim to be threshold-free rests on that word, and run 1 did not read: it
*"resolved them by magnifying 4× and stretching the contrast"*, confirmed blanks *"by pixel
uniformity, not by eye"*, and reported the 1.09:1 ratio back — § 1.1's refuted colour instrument,
re-entered through the worker.

**A second blind reader settled it, and the result is exact.** Forbidden to magnify, stretch contrast
or sample pixels, asked *which cells appear empty to you*, told nothing about run 1 or about hidden
ink, it returned a **136-cell** set **identical to hidden ∪ unpopulated**, and the disagreement with
the text layer is **exactly the 110 — zero false positives, nothing missed** — correctly excluding
`(0, 14)` and including `(1, 6)`. Review, final section.

So the respec **asks for the reader's answer in those terms**, and gets RF3's repaired null control
free in the same reply: run 2's set already carries all 26 unpopulated positions, so nothing separate
need be asked or refused. **Fold RF3 and RF7 into one change, not two.**

**What is still open, and § 7 must say so:** the prohibition is **unenforceable from the answer
alone** — both runs returned the same 110 by different routes, so the output cannot tell a reader
from an analyst. The honest route is now known to work, which was the question; detecting a defector
is not solved and should not be claimed. A control page on which the two routes *would* diverge is
the instrument that would close it, and none exists.

### 5d. ASSERTED — what must NOT be redone

- **Do not re-run O1.** It passed, blind, recorded: the reader called cbh's 2.96-ratio heading rows
  *"plainly legible"* and found no hidden ink anywhere in that image. The spec's named falsifier did
  not fire.
- **Do not re-run O2 to establish the set.** 110 addresses, **identical cell by cell** to the
  pipeline's 110, first attempt, blind — plus **(1, 6)** found independently. Re-run it as a
  regression against a *changed* ask (5c), never to re-establish the number.
- **Do not re-open the term or the fork.** `tab:UnshownInk`, a `tab:CellDatatype` that abstains, and
  a datatype rather than a proposition. Untouched by every finding; spec § 2.2 and § 2.3's last
  bullet carry the arguments.
- **Do not carry a colour into `src/`.** RF1 and RF7 both strengthen § 1.2, they do not weaken it.
- **Do not re-measure region count, crop cost or crop legibility.** All three were taken here: 122
  gridded regions, 0.05–0.54 s per 220-dpi region crop, and gcap band 3's crop reads cleanly at
  region grain. § 7.2 is answered.
- **Do not build [[R250]]'s derivation** and do not re-litigate R213 option (c).

## 1. Where the primaries are

- **The review, with every command and its output:**
  `docs/superpowers/2026-09-17-unshown-ink-spec-review.md`. Findings RF1–RF8, then the blind O1/O2
  run in its own section.
- **The spec**, now carrying a refutation banner and five inline `REFUTED`/`AMEND` section markers:
  `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md`.
- **The instrument**, four modes, one per finding:
  `scripts/unshown_ink_seam_census.py --regions | --blank | --grain | --graph <pdf>`. Every figure in
  the review re-runs from it. Its sibling `scripts/ink_contrast_probe.py` (previous loop) carries the
  colour census.
- **The predecessor evidence**, with an appended RF4 correction:
  `docs/superpowers/2026-09-17-unshown-ink-evidence.md`.
- **The rows:** [[R213]] (amended twice today — the spec, then this review) and [[R251]].
- **The seams that matter now**, all measured: `feed.py:246-256` (the assertion site),
  `celltype.grid_evidence` at `celltype.py:136-160` (transient), `headers._grid_cells` at
  `headers.py:66-81` (re-derives its own cells), `tab:EntryCell` at `tab.ttl:39` versus
  `tab:GridCell` at `tab.ttl:253` — siblings, related by nothing.

## 2. What was decided, and where it is recorded

- **The design is no longer only proposed** — O1 and O2 were run blind and both pass. Recorded in the
  review's run section, the spec's banner, and R213's row.
- **Five blocking findings, three of which move a seam** (RF1, RF2, RF3) and two of which add a
  refusal the spec never had (RF6, RF7). Recorded in all three places above.
- **E7's cbh population was mis-identified** and is corrected in place by an appended note: 828
  white-on-**grey** at 2.9601, not 780 white-on-pale-blue at 1.6887; only 24 are the port codes.
  § 1.1's arithmetic is unaffected.
- **Nothing was implemented, and no `src/` file was touched.** This loop added one `scripts/`
  instrument and four documents' worth of prose.

## 3. Unverified or assumed

- **5c's second run LANDED and is exact** — but it is one run, on one region, by one reader. Non-determinism is tolerated at the proposal (CLAUDE.md § 8), so a re-run may differ; the spec must say how a re-run is compared (spec § 7.3 already raises this and is unanswered).
- **Detecting a worker that enhances is unsolved**, and no control page exists on which the reading route and the analysis route would diverge.
- **The blind reader is not the shipped worker.** It is a general agent with a Read tool, not a BAML
  image function; `baml_src/` still holds five text functions and no image input. What was
  established is that *a* vision reader answers this question correctly, not that the one this repo
  will ship does.
- **n is still 1 for the positive case.** 110 glyphs, one page, one publisher — and RF5 records that
  gcap is the *easy* case: its 110 are each alone in their cell, which is a property of gcap. cbh
  already holds 8 cells mixing unshown and ordinary ink that no per-cell question can answer.
- **The fourth case of § 7.4** (ink the page shows, placed outside any cell) is still unaddressed and
  still not known to be empty.
- **`tab:EntryCell`'s own coverage** was measured only on graincorp-capacity (406/406). Whether every
  region that can hold unshown ink mints `EntryCell`s is not established corpus-wide.

## 4. What this session did

Read the spec and its evidence, then measured rather than reasoned: located the low-contrast
populations per band and per cell, found that `regions.Cell` and `headers._grid_cells` are two
different cell notions differing tenfold in reach, instrumented a real compile to see which cells are
actually typed, probed the compiled graph and found `tab:GridCell` absent and `tab:EntryCell` at 406
with exactly 110 zeros, counted the null control's population across all 122 gridded regions, split
cbh's low-contrast set by ink and backdrop, rendered and read the crops, and ran O1 and O2 blind.
Then wrote the review, amended the spec and R213's row, corrected E7 in place, and shipped the
census. PR #262.
