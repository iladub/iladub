# Spec — the ink the page does not show: R213's third absence term

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on this row.

**Date:** 2026-09-17. **Branch:** `the-ink-the-page-does-not-show`, cut from `main` at `96009f5`.

**Doc impact: increment.** One new published term in `tab:` (§ 2), one amended `rdfs:comment`, one
new SHACL shape. No released term changes meaning.

**Written in the session's first third, before any implementation.** Every load-bearing claim cites
`2026-09-17-unshown-ink-evidence.md` (**E**), where the command and its output are recorded.
§§ 1–3 are **measured**. §§ 4–6 are **design and are PROPOSED**: the fork this spec resolves was
left open by the ruling, and the disposal in § 4 has never been run.

> **REVIEWED 2026-09-17, in a fresh session, per the handoff's § 5a — and three sections are
> REFUTED.** `2026-09-17-unshown-ink-spec-review.md` carries the measurements. The **design**
> survives: a disagreement between the text layer and a reader of the render is still the disposal.
> **Where it attaches does not.**
>
> - **RF1 — § 2.3 and § 2.4 name `tab:GridCell`, which never reaches the compiled graph.** It is a
>   transient classification class (0 in graincorp-capacity's 5859-triple output; `grid_evidence`
>   mints positional IRIs 11 times per compile and discards them). The persisted class is
>   `tab:EntryCell` — 406 on that page, **exactly 110 carrying `tab:cellText "0"`** — and the false
>   assertion happens at `feed.py:246-256`, beside the `is_blank` `continue` that is its precedent.
> - **RF2 — § 1.4's "exactly one narrow place to cross" is false: there are two.** `_grid_cells`
>   re-derives its own cells from `band.lines` and never sees a `regions.Cell` (the two notions
>   differ 10.0% vs 95.4% in reach). A fact carried only through it reaches the homogeneity vote and
>   dies before the graph.
> - **RF3 — § 4.3's null control is EMPTY where the disposal runs.** 358 `tab:Blank` cells corpus-
>   wide, **357 of them in graincorp-stem**; 118 of 122 gridded regions have none; graincorp-capacity
>   band 3 has **0 of 406** and cbh-stem **0 of 664**. The oracle reduces to "is the address in the
>   grid?". *No oracle, no worker.* The live set is the **unpopulated grid position** (26 on gcap
>   band 3, 137 on cbh band 1) — of which 25 of gcap's 26 are the spanning year-label column.
> - **RF4 — the O1 control population is 828 white-on-GREY at ratio 2.9601**, the vessel tables'
>   heading rows; only **24** are the pale-blue port codes at 1.6887. § 1.1's table row and § 5's
>   argument name the 24's colour with the 828's count.
> - **RF5 — a fifth weakness for § 7:** the disposal's grain is the cell, the phenomenon's is the
>   glyph. gcap's 110 are each alone in their cell; cbh already holds 8 cells that mix unshown and
>   ordinary ink, which a per-cell question cannot answer.
>
> - **RF6 — § 4.3's contract has no refusal for the case that actually fired.** On cbh the blind
>   worker **rejected the supplied grid** (*"you described it as 18 × 16; what is actually drawn is
>   20 columns … I cannot make 18 × 16 out of what is on the page"*) and answered by column NAME.
>   Addresses in a different address space are all *inside* the stated grid, so the oracle admits
>   them in silence. The worker needs a way to say *"this is not the grid I see"*, and that
>   abstention must refuse the region.
> - **RF7 — § 4.1's "a reader of the rendered page" was answered by an image analyst.** Unprompted:
>   *"I only resolved them by magnifying 4× and stretching the contrast … I would not have reported
>   them from the image as displayed"*, and blanks *"confirmed by pixel uniformity, not by eye"* —
>   with the 1.09:1 ratio reported back. That is § 1.1's refuted colour instrument re-entering
>   through the worker. **TESTED AND CONFIRMED:** a SECOND blind reader, forbidden to magnify,
>   stretch contrast or sample pixels and asked *which cells appear empty to you*, returned a
>   136-cell set **identical to hidden ∪ unpopulated**, whose disagreement with the text layer is
>   **exactly the 110 — no false positive, nothing missed** — correctly excluding `(0,14)` and
>   including `(1,6)`. So § 4.1's *reader of the rendered page* is achievable, and RF3's repaired
>   null control **comes free** in the same answer. The prohibition remains unenforceable from the
>   answer alone (both routes return the same 110), which is what § 7 must admit.
> - **RF8 — minor:** the worker returned `14,000`, a value on the page, against § 4.3's *"addresses,
>   not values"*. The output shape must make that impossible rather than request it.
>
> **§ 5's O1 AND O2 WERE RUN, BLIND, and both PASS.** A reader with no context, given only the two
> 220-dpi crops and the grid dimensions: on cbh it called the 2.96-ratio headings *"plainly
> legible"* and reported no hidden ink anywhere — **O1 did not fire**; on gcap it returned 110
> addresses that are **IDENTICAL to the pipeline's 110 hidden cells, cell by cell, first attempt**,
> and independently singled out **(1, 6)** as the one navy cell carrying no glyph — R213's own
> recorded exception, which it was never told about. § 4's disposal is no longer only proposed.
>
> Also measured there, so the plan need not: **122 gridded regions** corpus-wide, **0.05–0.54 s** per
> region crop at 220 dpi, and gcap band 3's crop **is legible** at region grain (§ 7.2 answered).

## 0. The ruling this spec executes, and the one it obeys

**R213, ruled 2026-09-13 by the maintainer, option (c):** an invisible glyph is carried as a **typed
absence or a proposition** — the reading says *there is a glyph here that the page does not show*
rather than asserting the value it hides. Option (a) (carry the `0`) was refused under § 7 (a false
assertion), option (b) (emit nothing) under § 5 (a loss). `residues-open.md:146` is the row. This
spec does not re-open it.

**CLAUDE.md § 8, amended 2026-09-17:** a reading judgement gets **at most one geometric attempt**;
on its first refutation the next loop writes a NEURAL proposer and does not try a second heuristic.
A worker answers one small question a human answers at a glance, returns a **strongly typed, closed**
shape, never returns a value that is on the page, and exists only where an oracle disposes it —
**no oracle, no worker.**

R213's colour discriminator **was** the one geometric attempt. § 1 is its refutation.

## 1. What is measured, and what it retires

### 1.1 The discriminator survives replication and loses to its own principled variant

R213's luminance-gap instrument replicates exactly: 110 chars, all `0`, all graincorp-capacity
page 0, separated from every other char in the corpus by an empty band — **0.42174 wide** under this
probe's containment rule against the 0.1935 R213 recorded (**E1**; the disagreement is recorded, not
resolved, and nothing below turns on it).

Then the instrument was swapped for the one constant that would **not** be tuned — WCAG 2.2's
published 3:1 minimum for large text, an external normative source *cited* rather than chosen, which
is the move this repo makes everywhere else. It fires on **858 glyphs that a reader sees perfectly
well** (**E2**): 78 green `Y` ticks on white at ratio 2.8773, and cbh-stem's entire 780-glyph white-
on-pale-blue heading band at 1.6887 — *lower* than some visible ink would score against a different
backdrop.

| glyph population | WCAG ratio | luminance gap | a reader sees it |
| --- | --- | --- | --- |
| gcap navy-on-navy (110 × `0`) | 1.0856 | 0.00648 | **no** |
| cbh white-on-pale-blue (780) | 1.6887 | 0.4282 | yes |
| gcap green `Y`-on-white (78) | 2.8773 | 0.686 | yes |

**This is the result the spec is built on.** The two instruments disagree about 858 glyphs; which
one is right is settled by *looking at the page*, which is a reading judgement and not a formula. So
the tuned parameter is not the constant but **the choice of instrument**, one level above where § 8
was looking — and picking the number more carefully cannot reach it. Three structural
(threshold-free) rules were tried against the same census and all three are refuted on the page they
were invented for, one of them undefined on cbh outright (**E3**). The class is closed.

### 1.2 The handoff's § 5c is retired: no colour is carried

`2026-09-17-r213-term-handoff.md` § 5c called extending extraction to carry each glyph's colour
"the loop's real work". **It is not this loop's work at all**, for two measured reasons:

1. § 1.1 removes the consumer. Nothing downstream may decide visibility from a colour.
2. The obvious route breaks the reading anyway. `extra_attrs=['non_stroking_color']` **splits words
   wherever the attribute changes**: 11 extra words across 4 of the corpus's 27 pages (bfs p2,
   ons p1/p2/p5), on two documents with **zero** hidden glyphs (**E4**). `geometry.extract_words`
   (`src/iladub/etkl/geometry.py:41-50`) is the single seam every reader goes through, so those
   words would reach every downstream judgement.

`scripts/ink_contrast_probe.py` ships as a **measurement instrument only** — the census that argues
§ 1.1 — and no `src/` module imports it. The grep that proves the shipped reader is colour-free
(**E6**) stays true after this loop.

### 1.3 The handoff's § 5e is refuted: the corpus does hold a second specimen

§ 5e says the generality limit is n = 1 and *"no corpus document can lift it"*, predicting that a
second specimen "in mid-grey on light-grey" would land inside the empty band. cbh-stem's 780
white-on-pale-blue glyphs **are** that specimen — they land inside the WCAG instrument's decision
region and outside the luminance instrument's — and they are in the corpus today. The prediction was
right about the shape of the failure and wrong that the corpus could not show it.

### 1.4 The seam a per-cell fact must cross — **REFUTED (RF2): there are two seams**

Measured at **E5**: a band cell already carries its `Word` objects (`regions.Cell.words`,
`regions.py:34-41`) and loses them at exactly one place — `headers._grid_cells`
(`headers.py:66-81`) flattens each cell to `(r, c, " ".join(texts))`, with the `Word` in scope one
line above the join. `celltype.grid_evidence` (`celltype.py:138-150`) consumes those 3-tuples and
`celltype._cell_datatype` (`celltype.py:81-93`) sees **only the text**. That tuple, and the
`grid_evidence` signature reading it, is the whole crossing.

## 2. The term, and the fork the ruling left open

### 2.1 The gap, stated once

`tab:Blank` covers **two** cases in its own published comment (`vocab/ontology/tab.ttl:260-261`):
*ink that is absent*, and *a nil MARKER the author wrote to mean "nothing here"* (the markers
enumerated as `tab:nilSpelling`, `tab.ttl:303`). The third case — **ink that is present and that the
page does not show** — has no term, so today gcap's 110 glyphs type `tab:Numeric`, vote in every
homogeneity judgement, and are grounded as tonnages of zero.

### 2.2 The fork: a datatype, not a proposition

The ruling says *typed absence **or** a proposition* and leaves the choice to the spec. **It is a
datatype.** Three reasons, in decreasing strength:

1. **A proposition would be the wrong register.** `iladub:CandidateConcept` quarantines content that
   cannot be **grounded in a vocabulary** — an unmatched *term*. The hidden `0` is not ungroundable:
   `ship:capacity` accepts a tonnage and `0` is a well-formed one
   (`examples/shipping/capacity-contract.ttl:39`, `ship:f-cap-capacity etkl:fillsProperty ship:capacity`). Its defect is **evidential**, not
   terminological. Filing 110 numbers in a register built for terms would also demand 110
   `iladub:PromotionDecision`s on one page, each weighing evidence that is already recorded on the
   cell — an accountable act with nothing to decide.
2. **The lattice is the layer that already carries this judgement.** `tab:CellDatatype` is declared
   OPEN (`tab.ttl:259`), it is what every homogeneity derivation reads, and `tab:Blank` and
   `tab:ParenthesizedNumber` are the two precedents for a member that abstains. Putting the third
   member of a trichotomy anywhere else states it in two places.
3. The handoff's own objection — *"a datatype that abstains still loses the fact that ink exists"*
   (§ 5d) — is answered by not letting the datatype be the only carrier (§ 2.3), not by taking the
   other branch.

### 2.3 `tab:UnshownInk` — **AMEND (RF1): the domain is `tab:EntryCell`, not `tab:GridCell`**

```turtle
tab:UnshownInk a tab:CellDatatype ; rdfs:label "Unshown ink"@en ;
    tab:datatypeAbstains true ;
    rdfs:comment "..." .
tab:unshownText a owl:DatatypeProperty ; rdfs:domain tab:GridCell ; rdfs:range rdfs:Literal ;
    rdfs:label "unshown text"@en ; rdfs:comment "..." .
```

Five decisions, each with its reason:

- **It abstains** (`tab:datatypeAbstains true`). Not inherited by resemblance to `tab:Blank` — § 3
  of the handoff flagged that gap. The reason is the same reason `tab:ParenthesizedNumber` abstains:
  the cell's reading is genuinely undetermined, so it must neither vote in a modal computation nor
  count as a mismatch. A cell whose ink a reader cannot see is not evidence that its column is
  numeric.
- **It is NOT in `tab:Quantity`**, and in no family. A family says *counts as the same kind of
  thing*; unshown ink is not a kind of quantity, whatever it transcribes.
- **It is not a `tab:nilSpelling`.** A nil spelling is an *authoring act a reader can see* — the
  author wrote `—` and a reader reads "nothing here". Unshown ink is the opposite: the reader sees
  nothing and the author wrote something. Merging them would put the two ends of the trichotomy in
  one term.
- **`tab:unshownText` carries the transcription** the text layer holds (`"0"`), on the cell, so § 5
  loses nothing and a later loop can promote it by decision if a reason ever appears. The cell's
  `tab:gridText` is **empty**, because `gridText` is what the region reads and the region reads
  nothing there.
- **The name says what the document does, not what a reader's eye does.** Not `HiddenInk` (imputes
  an intent to hide that no evidence supports) and not `InvisibleInk` — § 5d's second failure mode
  is a term named after a rendering accident. *Unshown* is a property of the page: this document
  does not show this ink. That is exactly what § 4's disposal decides and no more.

`tab:Blank`'s comment is amended to **cite** `tab:UnshownInk` as the third member rather than
restate the trichotomy — the `tab:nilSpelling` precedent, whose own comment exists because a rule
written in two places drifts (R167).

### 2.4 The membrane — **REFUTED (RF1): `tab:GridCell` is not in the compiled graph**

A new `sh:NodeShape` in `vocab/shapes/tab-shapes.ttl`, closed-world, refusing what may cross:

- a `tab:GridCell` typed `tab:UnshownInk` must carry `tab:unshownText` exactly once and must carry
  **no** non-empty `tab:gridText` — a cell cannot simultaneously be read and not read;
- a `tab:UnshownInk` cell may not be the source of an asserted contract value. **This is R213's
  whole point and the one shape that must exist**: the § 7 false assertion the ruling refused is a
  tonnage grounded from a glyph the page does not show.

Ships with a conforming worked example and a negative example that must fail (repo convention).

## 3. What the loop builds — interfaces and invariants, not bodies

### 3.1 Carriage (PROCEDURAL — irreducible) — **INCOMPLETE (RF2): covers one of two crossings**

`headers._grid_cells` widens its tuple from `(r, c, text)` to carry a per-cell unshown flag and the
suppressed transcription, and `celltype.grid_evidence` accepts it. **§ 8 class: PROCEDURAL**, and
the justification the code must state: it is plumbing a fact already decided elsewhere across a
function boundary; it takes no decision and reads no geometry.

**Invariants:**
- `grid_evidence`'s existing 3-tuple callers keep working — six call sites at `matrix.py:134`,
  `rowheaders.py:33`, `orientation.py:36,59`, `headers.py:111`, and `unitmarker.py:59` consumes the
  same shape (E5). The implementer **measures** whether widening or an optional side-map is cheaper
  at those six; the spec does not choose for them.
- With no unshown facts supplied, every cell types exactly as it does today. This is the null:
  the change must be a no-op on six of seven corpus documents (§ 5).

### 3.2 The absence of a colour reader

Nothing in `src/` reads a colour after this loop, as before it (E6). **This is an invariant with a
test**: the grep at E6 becomes a repo gate, in the shape the citation lint and the figure gate
already use. It is the only thing standing between a future loop and the refuted instrument.

## 4. The disposal — PROPOSED, and the part that has never been run

### 4.1 Two independent readings of one cell

The decidable fact is not a colour distance. It is a **disagreement**:

| the text layer says | a reader of the rendered page says | the cell is |
| --- | --- | --- |
| a glyph is here | a mark is here | ordinary ink |
| a glyph is here | **no mark** | **`tab:UnshownInk`** |
| no glyph | no mark | `tab:Blank` (unchanged) |
| no glyph | a mark | out of scope — flag, do not type (vector or scanned text) |

No colour, no threshold, no palette. The rule generalises to § 5e's mid-grey-on-light-grey specimen
**by construction**, which is the reason to prefer it over any survivor of § 1.1.

### 4.2 § 8 classification, part by part

- **Rasterising the page and cropping a region** — PROCEDURAL raw extraction, the class
  `geometry.py:79` already names for the vector-line reader.
- **Reading the text layer's glyph presence per cell** — PROCEDURAL, already shipped
  (`extract_words`).
- **"Does this cell show a mark?"** — **NEURAL**. It is a perceptual question about what a page
  shows a reader; § 8 has no other class for it, and § 1.1 is the measured proof that the symbolic
  alternatives are exhausted.
- **The disagreement → the type** — **AXIOM**, a SPARQL derivation over the two evidence sets,
  open-world and evidence-positive: both readings must be PRESENT for a cell to type `UnshownInk`.
  A missing worker answer types nothing.
- **The membrane (§ 2.4)** — SHACL, closed world, holon-scoped.

### 4.3 The worker's contract — **the null control is REFUTED (RF3): its population is empty**

One ask **per region**, not per cell — the cost gate, in the shape of R249 half (a) (skip the ask
where no answer could be admitted). The question is closed and structural:

- **In:** the rendered crop of the region, and its grid dimensions. **Never** the text layer's
  transcriptions — the worker must not be shown the value it would be tempted to return.
- **Out:** a list of `(row, col)` addresses that show no mark. Strongly typed, closed, bounded by
  the grid. **Addresses, not values** — nothing the worker returns is a value on the page.

**The oracle refuses**, and its refusals are the test that it is live:
- any address outside the grid;
- the **null control**: a worker that reads the page must also find the cells that are *genuinely*
  empty. If its answer set misses the cells the text layer already reads as `tab:Blank`, it is not
  reading the page and the whole region's answer is refused. (R216's lesson — a disposal that only
  ever accepts is not a disposal; this one has a direction that fires on a worker that is merely
  agreeable.)

## 5. The falsifying oracles — run in this order

**O1, the control, FIRST, on cbh-stem — the run that can kill the spec.** cbh's 780
white-on-pale-blue glyphs are ordinary visible ink (E2). If the worker reports them as showing no
mark, `tab:UnshownInk` over-fires on a document it was never about, and § 4 is refuted. Run it
before gcap. The maintainer's read of the rendered page is the ground truth, and it is the only
ground truth this thread has ever had.

**O2, set identity on gcap.** Exactly the 110 cells type `tab:UnshownInk` — **the same 110, cell by
cell, not a matching count.** R176 and R172 each turned out to be hiding a coinciding count, and
R213's own amendment established its 110 by set identity for that reason. **A second witness exists
and costs nothing** (**E7**): every port on that page occupies a tonnage sub-column and a `Y`/`N`
availability flag, and 110 of 110 hidden glyphs sit immediately left of an `N` while 0 of 80 `Y`
flags have one. Use it to check O2 without running a worker — but **not as the rule**: the
implication runs one way (5 `N` flags have no glyph at all), and no other corpus document has a flag
column. A plan that quietly promotes this witness into the disposal has replaced a general reading
with one table's contract.

**O3, the six-document null.** graincorp-stem and who-wfa carry adjudication floors (0.95, 0.90) and
have zero unshown glyphs under either instrument. Their compiled output must be **bit-identical**,
not merely above floor. apple, bfs, ons likewise. **This is a prediction that can fail** — the
worker runs on all seven documents, so O3 is a real control and not a formality.

**O4, the membrane's negative.** The § 2.4 shape must REFUSE a hand-built cell that is typed
`tab:UnshownInk` and carries a non-empty `tab:gridText`, and must refuse a contract value asserted
from one. Per CLAUDE.md plan rule 4, the falsification arm shows each test RED with its subject
removed.

**O5, gcap's own reading moves, and how it moves is the point.** 110 cells leaving `tab:Numeric`
changes column homogeneity on that page, so gcap's score **will** move; it is `Unadjudicated`
(floor `None`), so nothing gates it. The plan states the direction it expects **before** running it.
A score that rises is not by itself evidence — R155's "score-rise-is-a-collapse" is the case.

## 6. What this loop deliberately does NOT do

- **No colour is read in `src/`.** § 1.1 and § 3.2. The instrument ships under `scripts/` only.
- **No threshold, of any kind, cited or chosen.** § 1.1 refutes the cited one, which was the best
  available.
- **[[R250]]'s derivation is not built** (it is blocked on this row;
  `2026-09-17-r250-furniture-field-names-evidence.md`).
- **The 110 transcriptions are not promoted.** `tab:unshownText` records them; nothing reads it.
  Whether a hidden `0` ever becomes an asserted zero is a promotion decision with no proposer and
  no consumer today, and inventing one here would re-open the ruling § 0 settled.
- **`tab:RegionCaption`'s provenance is not repaired** ([[R218]]), and the new cell carries page
  provenance only to the extent `tab:GridCell` already does. Widening the transient evidence graph's
  provenance is a different subject.
- **No vision infrastructure is generalised.** The worker in § 4.3 is the first image-input BAML
  function in this repo (`baml_src/` holds five text functions today); it is built for this question
  and nothing is factored for a second caller that does not exist.

## 7. The weakest parts, in the author's own judgement

1. **§ 4 has never been run.** Every figure in § 1 is instrument output; § 4 is a design. O1 is
   placed first for that reason.
2. **The per-region ask assumes a region crop a worker can read.** Region count and crop legibility
   are unmeasured (E, *What this evidence does not establish*); the plan measures both at the call
   site before writing it (plan rule 3).
3. **`tab:UnshownInk` is defined by a disagreement between two readers, one of which is
   non-deterministic.** Two runs may type a cell differently. That is tolerated at the proposal and
   nowhere else (§ 8 as amended), but it means O2's set identity is a claim about a *disposed* set,
   not about a stable one, and the plan must say how a re-run is compared.
4. **The trichotomy may not be a trichotomy.** A fourth case — ink the page shows but places outside
   any cell — is not addressed and is not known to be empty.

---

## 8. RESPEC, 2026-09-17 — the amended sections

**Appended, not edited in.** `docs/superpowers/**` is append-only after loop close (CLAUDE.md
§ Documentation governance), so §§ 1.4, 2.3, 2.4, 3.1 and 4.3 above keep their text and their
banner markers. **Where this section conflicts with the body above it, this section governs.**

It absorbs RF1–RF8 of `2026-09-17-unshown-ink-spec-review.md` and executes that review's handoff
§§ 5a–5c. Everything not named below stands unchanged and is **cited, never restated**: § 0 (the two
rulings), §§ 1.1–1.3 (the colour instrument's refutation and what it retires), §§ 2.1–2.2 (the gap,
and the fork resolved to a datatype), §§ 4.1–4.2 (the disagreement, and its § 8 classification),
§ 6 (what the loop does not do).

Three measurements were taken **for this respec** and are recorded inline per plan rule 2. One of
them — **RS1** — blocks the review's own prescribed remedy, and one — **RS2** — is the load-bearing
claim the whole re-attachment rests on.

### 8.1 (replaces § 1.4) There are two crossings, and they live in different graphs

Review RF2, measured there; not re-derived here.

- **Crossing A — transient.** `headers._grid_cells` (`headers.py:66-81`) flattens each populated
  grid position to `(r, c, " ".join(texts))`, with the `Word` in scope one line above the join;
  `celltype.grid_evidence` (`celltype.py:138-160`) consumes those 3-tuples. This is where the
  **abstention** belongs, because homogeneity is computed here — and only here.
- **Crossing B — persisted.** The `tab:EntryCell` emitters mint the cells the contract actually
  reads. A fact carried only through crossing A reaches the homogeneity vote and **dies before the
  graph** (RF1: `tab:GridCell` is 0 of graincorp-capacity's 5859 compiled triples).

`_grid_cells` re-derives its own cells from `band.lines` and never sees a `regions.Cell`; the two
notions differ 10.0% vs 95.4% in reach corpus-wide (RF2). § 3.1 built the loop's only carriage on
crossing A; § 8.6 below builds both.

### 8.2 (replaces § 2.3) Where the term attaches: the lattice keeps the datatype, the persisted cell keeps the transcription

`tab:UnshownInk a tab:CellDatatype ; tab:datatypeAbstains true` is **unchanged** — its five decisions
in § 2.3 (it abstains; it is in no family; it is not a `tab:nilSpelling`; it names what the document
does; `tab:Blank`'s comment cites it rather than restating the trichotomy) survive every finding.
It stays on the **transient** side, which is where a datatype that must not vote has to abstain.

Two amendments:

1. **`tab:unshownText` has `rdfs:domain tab:EntryCell`**, not `tab:GridCell` (RF1). It carries the
   transcription the text layer holds (`"0"`), on the class that reaches the graph with page
   provenance, and its **presence is the assertion that this cell's ink is unshown**.
2. **`tab:cellDatatype` is NOT written on the persisted cell**, and no other GridCell-domained
   property is either. Measured hazard: `tab:cellDatatype rdfs:domain tab:GridCell`
   (`vocab/ontology/tab.ttl:273`) and this repo validates with `inference="rdfs"` (CLAUDE.md
   § Serialization), so asserting it on a `tab:EntryCell` **infers that cell into `tab:GridCell`** —
   a class whose own published comment says *"never asserted into a holon"* (`tab.ttl:254`) — and
   hands it to every GridCell-targeting shape. **R19 is the recorded precedent for exactly this
   mechanism**, in this repo, on this vocabulary: writing `tab:onPage`/`tab:hasBBox` on a
   proposition made it a `tab:Cell` and handed it to every cell shape (`src/iladub/etkl/holon.py:64-70`).
   The datatype and the persisted marker are therefore two properties in two graphs, not one
   property in two places.

**The persisted cell's `tab:cellText` is EMPTY.** The transcription moves to `tab:unshownText`; the
cell keeps its bbox, page, row, column and `prov:wasDerivedFrom`. The reason is fail-safe, and it is
the difference between a design that needs one guard and one that needs a guard per consumer:

```
$ ./.venv/bin/python -c "from iladub.etkl.celltype import is_blank; print(is_blank(''), is_blank('0'))"
True False
```

`feed.py:254-255`'s `if is_blank(txt): continue` — § 2.4's own named precedent — then refuses to
ground the cell **with no new procedural code**, and every other reader of `tab:cellText`
(`feed.py:246`, `denormalization.py:163`, `recipe.py:91`) gets the truthful answer, *the page shows
nothing here*, by default. The alternative — keep `"0"` and add a skip at each grounding site —
**fails open**: every consumer that does not yet know the new term grounds the tonnage, which is
precisely the § 7 false assertion the ruling refused.

### 8.3 RS1 — BLOCKING, new: an empty `tab:cellText` is refused today, by a shipped shape

The review's remedy is not constructible as written. Measured here, on a hand-built pair:

```
$ ./.venv/bin/python scripts/unshown_ink_seam_census.py --shape
   conforms: False   (c1 = unshown, c2 = ordinary ink)
  Source Shape: tab:WrappedCellShape
  Focus Node: <urn:c1>
  Message: A tab:Cell with a hasBBox must have non-empty cellText (drop-continuation guard).
```

`c1` is a `tab:EntryCell` with `tab:cellText ""`, `tab:unshownText "0"` and a bbox; `c2` is an
ordinary cell with `tab:cellText "10,000"` and a bbox. **Only the unshown one is refused.**

`tab:WrappedCellShape` (`vocab/shapes/tab-physical-shapes.ttl:26-42`) refuses **any** `tab:Cell` with
a bbox and no non-empty `tab:cellText`, because a textless bbox-carrying cell signals a dropped
wrapped continuation. All 406 of graincorp-capacity's `tab:EntryCell`s carry `tab:hasBBox` (RF1's
property census), so every unshown cell would hit it. `tab:EntryCellPhysicalShape`'s
`sh:minCount 1` on `tab:cellText` is satisfied by an empty literal and does **not** fire; this is the
one shape to amend.

**The amendment: widen the guard's proof-of-carriage from one property to two** — a bbox-carrying
cell must have a non-empty `tab:cellText` **or** a non-empty `tab:unshownText`. An unshown cell is
not what the guard is for: a dropped continuation carries neither property, and is still refused.

**The form matters, and the near-miss is refused.** Adding a separate exemption for *"cells carrying
`tab:unshownText`"* would pass a cell carrying an **empty** `tab:unshownText` — carriage claimed and
not delivered, which is the very thing the guard exists to catch. The disjunct keeps the shape's
question (*does this cell carry its text somewhere?*) and only adds the second place the text may
live.

This is an amendment to a **published, shipped** shape, so it ships with a conforming example and a
negative one that must fail (repo convention), and it is O6 in § 8.8.

### 8.4 RS2 — measured, new: the two address spaces coincide on the region that matters — and only there is it measured

The worker answers in grid space (`(row, col)` of the region's grid). The membrane and the contract
read `tab:EntryCell`s. **Nothing in the review establishes that an address in one is an address in
the other.** Measured, on graincorp-capacity:

```
$ ./.venv/bin/python scripts/unshown_ink_seam_census.py --address
   band 1: 2 lines x 1 cols, 2 populated cells
   band 3: 27 lines x 16 cols, 406 populated cells
   grid-space cells whose joined text is '0': 110
   EntryCells parsed: 406  unparsed IRI shape: 0
   persisted cells whose cellText is '0': 110
   table 3 vs band 3: |P|=110 |G|=110 identical=True  P-only=[] G-only=[]
   ALL cells, table 3 vs band 3: 406 each, identical=True
```

The persisted `…#htable3-e{r}_{c}` indices **are** `_grid_cells`' `(r, c)` for band 3 — 406 of 406
populated positions and 110 of 110 zeros, cell by cell, set identity and not a matching count
(R176's and R172's lesson, which § 5 already applies to O2).

**It is empirical, not structural, and the plan must treat it as such.** `holon.py:628` enumerates
`region.rows` / `rb.cells` — a `regions.Cell` notion — while `_grid_cells` re-derives from
`band.lines`, and RF2 measured those two notions differing 10.0% vs 95.4% corpus-wide. They coincide
here; nothing says they coincide elsewhere. There are **five** minting sites — `holon.py:154`,
`holon.py:214`, `holon.py:314` (all through `_emit_entry_cell`, `holon.py:41`), `holon.py:628`, and
`datagrid.py:691`, which keys its IRI `…-r{r_i}c{k}` off a different counter entirely.

**The invariant this buys:** the disposal's addresses are never resolved onto persisted cells by
index arithmetic on trust. **Per region, the carriage refuses unless the two address spaces are
checked to agree.** The cheapest check that fails closed is the populated-cell count (406 == 406 on
gcap); the plan measures whether a per-address check costs more than that, and enumerates the five
sites rather than assuming gcap's IRI shape generalises. This is O7 in § 8.8.

### 8.5 (replaces § 2.4) The membrane, on the class that reaches the graph

A new `sh:NodeShape` in `vocab/shapes/tab-shapes.ttl`, closed-world, over **`tab:EntryCell`**:

- **Clause 1 (structural).** A `tab:EntryCell` carrying `tab:unshownText` carries it exactly once and
  non-empty, and its `tab:cellText` is empty — a cell cannot simultaneously be read and not read.
  This clause has a subject today: 406 `tab:EntryCell`s on the page in question, 110 of them the
  ones at issue.
- **Clause 2 (the one R213 exists for).** No asserted contract value may be sourced from such a cell.
  **The seam the implementer MEASURES before writing it** (plan rule 3): whether the grounded node's
  `prov:wasDerivedFrom` chain reaches the `tab:EntryCell` at all. `feed.py:257-258` derives its
  `region` string from the cell's `prov:wasDerivedFrom` **object**, so the concept may carry the
  region and not the cell — in which case **clause 2 has no subject in SHACL** and must not be
  written as one. Its honest form is then the producer-side guard at the site that reads the cell
  (CLAUDE.md § Producer-side guards vs the membrane), with § 8.2's empty `tab:cellText` making the
  grounding structurally impossible and clause 1 carrying the membrane's half. **Measure, then
  choose; do not invent a path.**
- Ships with a conforming worked example and a negative example that must fail (repo convention).

**No shape is written over `tab:GridCell`.** It is not in the compiled graph, `tab:MembraneValidation`
never sees it, and its subject IRIs do not survive the call that mints them (RF1).

### 8.6 (replaces § 3.1) Carriage — both crossings, and they must not disagree

**Crossing A (transient, the abstention).** Unchanged from § 3.1 and cited, not restated: the
`(r, c, text)` tuple widens or gains a side-map, `grid_evidence` accepts it, the six existing
3-tuple call sites (`matrix.py:134`, `rowheaders.py:33`, `orientation.py:36,59`, `headers.py:111`,
`unitmarker.py:59`) keep working, the implementer measures which shape is cheaper, and with no
unshown facts supplied every cell types exactly as it does today.

**Crossing B (persisted, the membrane's subject).** The unshown set must reach the emitter so the
cell mints an empty `tab:cellText` and a `tab:unshownText`. **The seam to measure** (plan rule 3):
whether the fact rides on the `cell` object the emitter already receives (`rb.cells` at
`holon.py:626`, `cell` at `holon.py:41`) or on a per-region address set consulted at the emitter.
Five sites, enumerated in § 8.4.

**§ 8 class, both crossings: PROCEDURAL**, with the justification § 3.1 already states and the code
must repeat — plumbing a fact decided elsewhere across a function boundary, taking no decision and
reading no geometry.

**New invariant: the two crossings may not disagree.** A cell that abstains in the transient graph
and is asserted with non-empty `tab:cellText` in the persisted graph — or the reverse — is a defect,
not a tolerance. § 8.4's per-region count identity is the check that sees it.

### 8.7 (replaces § 4.3) The worker's contract — the reader's ask, and three refusals

One ask **per region** (the cost gate, in R249 half (a)'s shape): 122 gridded regions corpus-wide,
0.05–0.54 s per 220-dpi crop, and gcap band 3's crop is legible at region grain — all measured in
the review, none of it to be re-measured.

- **In:** the rendered crop of the region and its grid dimensions. **Never** the text layer's
  transcriptions.
- **The ask is a READER's, and enhancement is forbidden** (RF7). The question is *which cells appear
  empty to you* — you look at that place and see nothing — at normal size, with magnification,
  contrast stretching and pixel sampling **prohibited in the ask**. This is not aspirational: a
  blind reader under exactly those terms returned a 136-cell set identical to hidden ∪ unpopulated,
  whose disagreement with the text layer is **exactly the 110, zero false positives, nothing
  missed** (review, final section). Without the prohibition a capable worker does image analysis —
  run 1 magnified 4×, stretched contrast, and reported the 1.09:1 ratio back — and then every § 1.1
  refutation applies to the worker instead of to the code.
- **Out:** a closed shape that **cannot express a value on the page** (RF8). Addresses and
  abstentions only; run 1 returned `14,000` because the shape let it.
- **Refusal 1 — outside the grid.** Arithmetic, unchanged.
- **Refusal 2 — "this is not the grid I see"** (RF6). The worker must be able to reject the supplied
  dimensions, and that abstention **refuses the whole region**. It is not a hypothetical: on cbh two
  independent blind readers both rejected 18 × 16, both counted 20 columns, and disagreed with each
  other on rows (13 vs 16). Without it, an answer in a different address space is admitted in
  silence, because every such address is *inside* the stated grid. A refused region types nothing —
  § 4.2's AXIOM clause is open-world and evidence-positive, so a missing answer is not an absence
  claim.
- **Refusal 3 — the null control, which is the UNPOPULATED GRID POSITION and comes free** (RF3 folded
  into RF7). `tab:Blank` is **not** the control: 358 corpus-wide, 357 of them in graincorp-stem,
  118 of 122 gridded regions with none, **0 of 406** on gcap band 3 and **0 of 664** on cbh. The live
  set is the text-layer-empty position — 26 on gcap band 3, 137 on cbh band 1 — and the reader's
  "appears empty" answer already contains it, so nothing separate is asked. If the answer misses
  those positions the worker is not reading the page and the region is refused.
- **The confounder, stated rather than buried.** 25 of gcap band 3's 26 empty positions are column 0,
  the spanning year label R211 establishes a reader reads as **one** cell. So refusal 3 is scoped to
  *text-layer-empty positions not inside the extent of a spanning cell*: run 2 satisfies it (it
  returned all 26, a superset), and a reader that instead reads the span as occupied is reading
  correctly and must not be refused for it. **With the exemption, the non-degenerate control on the
  region that matters is one cell — (1, 6).** That is the honest strength of the control on gcap,
  and § 8.9 carries it as a weakness rather than a footnote.

### 8.8 (amends § 5) The oracles, after the review

**O1 and O2 are RUN and PASS, blind, and must not be re-run to establish anything** (review's run
section). O1 did not fire on cbh's 2.96-ratio headings; O2 returned the 110 by set identity on the
first attempt, plus `(1, 6)` unprompted. **Re-run O2 only as a regression against § 8.7's changed
ask** — never to re-establish the number.

**O3** (six-document null, bit-identical output), **O4** (the membrane's negative) and **O5** (gcap's
score moves, with the direction stated before the run) stand exactly as § 5 writes them.

Two new oracles, one per new finding:

- **O6 — the widened guard still refuses.** A bbox-carrying cell with neither a non-empty
  `tab:cellText` nor a non-empty `tab:unshownText` must still be refused by `tab:WrappedCellShape`,
  and so must one whose `tab:unshownText` is empty. The guard is widened, not blinded. Falsification
  per plan rule 4: show each test RED with its subject removed.
- **O7 — the address spaces are checked, not assumed.** Per region, the populated grid-cell count
  equals the `tab:EntryCell` count, or the carriage refuses. Its null: a region where they differ
  must actually refuse, and the plan finds one or records that none exists in the corpus.

### 8.9 (amends § 7) The weakest parts, after the review

§ 7's four items stand. Item 1 is **partly discharged** — § 4's disposal has now been run twice,
blind, and passes — and items 2 (crop legibility) and 3 (non-determinism) are updated:

1. **The enhancement prohibition is unenforceable from the answer alone.** Run 1 (analysis) and run 2
   (reading) returned the same 110 by different routes, so the output cannot tell a reader from a
   defector. What is known is that the honest route works; detecting a defector is **not solved and
   must not be claimed**. The instrument that would close it is a control page on which the two
   routes diverge, and none exists.
2. **How a re-run is compared is still unanswered** (§ 7.3). Two runs may type a cell differently;
   O2's set identity is a claim about a disposed set, not a stable one. The plan must say what it
   does when run *n*+1 differs.
3. **The control's real strength on gcap is one cell**, not 26 (§ 8.7's confounder).
4. **RS2's address identity is empirical.** Measured on one region of one document; five minting
   sites, two cell notions differing tenfold in reach corpus-wide.
5. **Emptying `tab:cellText` is a suppression whose consumer census has not been taken.** Three
   readers are named in § 8.2 (`feed.py:246`, `denormalization.py:163`, `recipe.py:91`); a full
   enumeration — every reader of `tab:cellText` in `src/`, in `vocab/queries/` and in
   `vocab/shapes/` — is the plan's first measurement, and it is an `enumerating-before-claiming`
   job, not a grep-and-glance.
6. **`tab:EntryCell`'s coverage is established on graincorp-capacity only** (406/406). Whether every
   region that can hold unshown ink mints `EntryCell`s is not known corpus-wide.
7. **RF5's grain problem is untouched**: the disposal's grain is the cell, the phenomenon's is the
   glyph. gcap's 110 are each alone in their cell; cbh already holds 8 cells mixing unshown and
   ordinary ink that no per-cell question can answer.
8. **The fourth case** — ink the page shows, placed outside any cell — is still unaddressed and still
   not known to be empty.
