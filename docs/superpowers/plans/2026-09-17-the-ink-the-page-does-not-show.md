# Plan — the ink the page does not show ([[R213]])

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: increment** (the spec's own, unchanged: one new term, one new
property, one new shape, one amended **published** shape — `tab:WrappedCellShape`).

**The governing text is the spec's § 8 and nothing above it.**
`docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md`. §§ 1.4, 2.3, 2.4, 3.1
and 4.3 of that spec are superseded in place by the append and keep their lines (Evidence is
append-only); a task written from the body without § 8 rebuilds a refuted attachment. Every
invariant below is **cited from § 8, never re-derived** (plan rule 6).

## Global constraints

- **The neurosymbolic gate** (CLAUDE.md § Core design principles 8). Every task states its class.
  The two carriages are **PROCEDURAL** with the justification § 8.6 states and the code must repeat.
  The reading is **NEURAL**, disposed by the text layer. Nothing here is a geometric heuristic and
  **no constant, tuned or cited, is introduced** (spec § 6).
- **Falsification is mandatory, per task** (plan rule 4): remove or invert the thing the new test
  pins, show it RED, restore, show the suite green. No falsification block ⇒ the task review fails.
- **No implementation source in this plan** (plan rule 1). Tests may be given verbatim; a
  plan-supplied test is a proposition until the implementer falsifies it, and an implementer who
  cannot make one pass has found a plan defect — say so in the task report and substitute.
- **Only what the source supports** (§ 7). The 110 transcriptions are recorded, never promoted
  (spec § 6).

---

## 1. The two measurements taken BEFORE this plan, and what each changes

The handoff (`2026-09-17-unshown-ink-respec-handoff.md` §§ 5c–5d) left one PROPOSED item and one
un-taken census. Both were run first, because the plan takes a different shape under each outcome.
The instrument is `scripts/unshown_ink_prov_probe.py`, shipped with this plan.

### M1 — the grounded node's chain does NOT reach the cell. Clause 2 is a producer-side guard, not a shape

Spec § 8.5 offers three outcomes and forbids inventing a path. **Outcome 2, with the string rewrite
of outcome 3 available but unusable.** Measured on graincorp-capacity p0:

```
$ ./.venv/bin/python scripts/unshown_ink_prov_probe.py
== graincorp-capacity-2026-08-04.pdf p0: 5854 triples compiled

   tab:EntryCell: 406   carrying prov:wasDerivedFrom: 406
   distinct prov objects: 406   objects shared by >1 cell: 0
   example: htable3-e0_0  ->  p0-62-111

   records=189 grounded=0 still-quarantined=769 candidate-pool=769

   GroundedNode: 0 nodes, 0 distinct regions reached, 0 reaching NO region

   CandidateConcept: 769 nodes, 413 distinct regions reached, 0 reaching NO region
       region fragments, e.g.: ['htable3-hl2', 'htable3-hl3', 'htable3-hl4']
       fragment IS a cell IRI fragment (outcome 1): 0/413
       fragment IS a prov-object fragment (outcome 3): 406/413
       fragment is NEITHER (outcome 2): 7/413

   -- can a region fragment name ONE cell? --
      prov fragments naming exactly 1 cell: 406 / 406
      max cells behind one prov fragment: 1
```

Three facts, and the third is the decisive one:

1. **The chain never names the cell.** `0/413` region fragments are a cell IRI fragment. What it
   reaches is `urn:iladub:region:<frag>` where `<frag>` is the fragment of the cell's
   `prov:wasDerivedFrom` **object** — a bbox-keyed page IRI (`htable3-e0_0` → `p0-62-111`), minted at
   `ground.py:161-163` from the string `feed.py:257-258` cut. The join is a **string rewrite**
   between two IRI schemes, exactly as § 8.5 suspected.
2. **The rewrite would be injective here** — 406 of 406 prov fragments name exactly one cell, max 1.
   So on gcap the region *does* identify a unique cell. The join is constructible.
3. **And it is unusable, because the two nodes are never in one graph.** The grounding membrane
   validates `g`, the grounded graph, and `g` holds **no `tab:` triple at all**:

```
$ ./.venv/bin/python - <<'PY'   # (inline probe, same fixture)
   grounded graph triples: 6567
   tab:EntryCell in the GROUNDED graph: 0
   any tab: triple in the grounded graph: 0
   tab:EntryCell in the DOCUMENT graph: 406
PY
```

`feed._validate_grounding` (`src/iladub/feed.py:720-730`) puts `g` alone through
`membrane.validate`. A shape over `tab:EntryCell` written into the grounding membrane has **zero
focus nodes, forever** — the R213 failure mode wearing a green suite, which is precisely what § 5c
said to prevent.

**What this decides for the plan.** Spec § 8.5 clause 2 is **NOT written as SHACL**. Its honest
form is the **producer-side guard** at the site that reads the cell (CLAUDE.md § Producer-side
guards vs the membrane; R102 is the case that shows a guard the membrane cannot reach). Clause 1
— structural, over `tab:EntryCell`, in the **document** membrane where 406 focus nodes exist today
— carries the membrane's whole half. **Do not union the two graphs to make clause 2 fireable**:
that is a new coupling between the document graph and the grounding graph, invented to serve one
shape, and § 8.5 forbids inventing a path.

*Secondary, and not load-bearing:* `grounded=0` on gcap under the corpus battery's abstaining
proposer — expected and by design (`tests/test_propose_grounding_context.py:19-21`), not a finding.
The plan must not read it as "nothing grounds from unshown cells today, therefore nothing to guard."

### M2 — the `tab:cellText` consumer census REFUTES spec § 8.2's three readers

§ 8.9 item 5 calls this the plan's first measurement and an `enumerating-before-claiming` job. It
was run as one. **Population:** every reader of `tab:cellText` in `src/`, `vocab/queries/` and
`vocab/shapes/`. **Command:**

```
$ git grep -n "cellText" -- src/ vocab/ | wc -l
      53          # src/ 24, vocab/ 29
```

Every hit was read and classified by its **subject**, because only an `tab:EntryCell`'s
`tab:cellText` is emptied by § 8.2 — a `tab:LabelCell` reached through `tab:hasLabel` is untouched:

| where | reads an **EntryCell**'s `cellText` | reads a LabelCell / is a write / is a comment |
| --- | --- | --- |
| `src/` (24 hits) | **4**: `feed.py:253`, `denormalization.py:168`, `document.py:787`, `recipe.py:37` (via `recipe.py:83,100`) | 6 LabelCell reads (`feed.py:306,363,635`, `denormalization.py:73,274`, `reshape.py:30`); 10 writes (`holon.py:49,144,194,256,288,340,582,633`, `datagrid.py:695`, `ruledroles.py:473`); 4 comments |
| `vocab/queries/` | **4 files**: `row-group-key.rq:15,21`, `row-group-key-logical.rq:57,63`, `unpivot-inverse.rq:27`, `unpivot-inverse-valueset.rq:21,27` | `recover-dimensions.rq` (label only) |
| `vocab/shapes/` | **1 file**: `tab-physical-shapes.ttl` — `tab:EntryCellPhysicalShape:15` (`sh:minCount 1`, satisfied by an empty literal) and `tab:WrappedCellShape:26-42` (RS1) | `tab-shapes.ttl:294` (LabelCell) |

**Spec § 8.2's parenthesis — *"every other reader of `tab:cellText` (`feed.py:246`,
`denormalization.py:163`, `recipe.py:91`)"* — is wrong three ways**, and this is a spec finding the
plan carries rather than repeats silently:

1. **All three line numbers are stale.** The sites are `feed.py:253`, `denormalization.py:168`,
   `recipe.py:37`. They were **miscited at authoring, not drifted**: the last commit touching `src/`
   is `3f6c604` (PR #258, R249 half (a)), which lands *before* the spec's own commit `965f78a`
   (PR #262) — `git log --oneline -3 -- src/`.
2. **It misses a fourth `src/` reader**: `document.py:787` counts the literals on an entry cell and
   **refuses the whole chain walk** on an anomaly (`return None, None, f"{len(texts)} cellText
   literals on {e}"`), then takes `str(texts[0])` as the cell's value at `:790`. Emptying keeps the
   count at 1, so it does not refuse — it silently carries `""` into the chain grid.
3. **It misses the four SPARQL query files entirely, and that is the larger omission.** All four are
   executed from `src/` (`denormalization.py:97`, `reshape.py:92,195`, `document.py:912`), and
   `unpivot-inverse.rq:27` carries the entry cell's text into the **reshaped** graph while
   `recipe.grid_values` (`recipe.py:87-101`) reads the same text off the **source** graph. Those are
   the two sides of the shipped reshape round-trip.

**What this decides for the plan.** Emptying `tab:cellText` is truth-telling and fail-safe by
design (§ 8.2, cited not re-argued), and **nine** consumers — not three — receive that truth. Eight
of the nine want it: a cell whose ink the page does not show has no value to sum, to key, to ground
or to unpivot. The ninth is a **seam the implementer must measure, not assume** (T5, plan rule 3).
It does **not** threaten O3's six-document null: with no unshown facts supplied nothing is emptied,
so the null holds by construction — the blast radius is **gcap-only, and it is 110 cells wide**.

---

## 2. The tasks

Ordered by what blocks what. T1 first because nothing else can land without it (handoff § 5b).

### T1 — amend `tab:WrappedCellShape` so an unshown cell can cross at all

**Blocking.** Measured by `scripts/unshown_ink_seam_census.py --shape` (RS1, spec § 8.3): a
`tab:EntryCell` with an empty `tab:cellText`, a non-empty `tab:unshownText` and a bbox is **refused
today**, and all 406 gcap `EntryCell`s carry a bbox.

- **Interface.** `vocab/shapes/tab-physical-shapes.ttl:26-42`. Widen the guard's proof-of-carriage
  from one property to two: a bbox-carrying `tab:Cell` must have a non-empty `tab:cellText` **or** a
  non-empty `tab:unshownText`. **Class: AXIOM (constraint → SHACL, closed world)** — the membrane.
- **The form is load-bearing and § 8.3 states why once**: a disjunct, never an exemption for cells
  *carrying* the property. Cite § 8.3; do not re-argue it.
- **It is a published, shipped shape**, so it ships with a conforming worked example and a negative
  one that must fail (CLAUDE.md § Serialization).
- **Oracle O6** (§ 8.8): the widened guard **still refuses** (a) a bbox-carrying cell with neither
  property non-empty, and (b) one whose `tab:unshownText` is empty. Widened, not blinded.
- **FALSIFICATION.** Revert the disjunct → the conforming example goes RED. Delete each O6 arm's
  subject → that arm goes RED. Both, then restore.
- **The seam to measure, not assume** (plan rule 3): `tab:WrappedCellShape` targets `tab:Cell`, not
  `tab:EntryCell`. **Measure which classes RDFS-close into `tab:Cell` in the compiled graph before
  writing the disjunct**, and confirm the amendment reaches every one of them —
  `tests/etkl/test_closure_equiv.py`'s full-RDFS leg is the instrument that caught exactly this
  class of surprise for [[R182]] (`tab.ttl:495` records it).

### T2 — the term, and the membrane's half that has a subject

- **Interface.** In `vocab/ontology/tab.ttl`: `tab:UnshownInk a tab:CellDatatype ;
  tab:datatypeAbstains true` (unchanged from § 2.3, whose five decisions survive every finding), and
  `tab:unshownText` with **`rdfs:domain tab:EntryCell`**. In `vocab/shapes/tab-shapes.ttl`: a closed
  `sh:NodeShape` over `tab:EntryCell` carrying **clause 1 only** (§ 8.5) — `tab:unshownText` exactly
  once and non-empty, and `tab:cellText` empty. **Class: AXIOM (constraint → SHACL).**
- **Clause 2 is NOT written here.** M1 measured its subject out of existence in the grounding
  membrane; it becomes T5's producer-side guard.
- **The hazard § 8.2 measured, restated nowhere else in this plan:** do **not** write
  `tab:cellDatatype` (or any `tab:GridCell`-domained property) on the persisted cell — under
  `inference="rdfs"` it infers the cell into `tab:GridCell`. [[R19]] is the recorded precedent on
  this vocabulary.
- **Oracle O4** (§ 5, unchanged): the shape REFUSES a hand-built cell that claims unshown ink and
  carries a non-empty `tab:cellText`. Conforming + negative example, per repo convention.
- **FALSIFICATION.** Remove the `sh:maxCount`/emptiness clause → the negative example conforms
  (RED). Restore.
- **No shape over `tab:GridCell`** — 0 in the compiled graph (RF1).

### T3 — crossing A: the abstention in the transient graph (PROCEDURAL)

- **Interface.** `headers._grid_cells` (`headers.py:66-81`) carries the per-cell unshown fact to
  `celltype.grid_evidence` (`celltype.py:138-160`), which abstains for those cells. Cited from
  § 8.6; not restated.
- **The implementer chooses the shape** — widened tuple or side-map — and **measures which is
  cheaper at the six existing 3-tuple call sites** (`matrix.py:134`, `rowheaders.py:33`,
  `orientation.py:36,59`, `headers.py:111`, `unitmarker.py:59`). The spec does not choose (§ 3.1).
- **Class: PROCEDURAL**, and the code states why it is irreducible: plumbing a fact decided
  elsewhere across a function boundary, taking no decision and reading no geometry.
- **Oracle:** with no unshown facts supplied, every cell types exactly as today (the null, § 3.1).
- **FALSIFICATION.** Supply one unshown fact and delete the abstention → the homogeneity vote
  changes (RED). Restore.

### T4 — crossing B: the persisted cell, and the address spaces checked rather than trusted

- **Interface.** The unshown set reaches the `tab:EntryCell` emitter, which mints an **empty**
  `tab:cellText` and a `tab:unshownText`. **The seam to measure** (§ 8.6, plan rule 3): whether the
  fact rides on the `cell` object the emitter already receives (`holon.py:626`, `holon.py:41`) or on
  a per-region address set consulted at the emitter. **Five minting sites**, enumerated once at
  § 8.4: `holon.py:154,214,314` (via `_emit_entry_cell`, `holon.py:41`), `holon.py:628`, and
  `datagrid.py:691`, which keys its IRI off a different counter.
- **Class: PROCEDURAL**, same justification as T3.
- **Oracle O7** (§ 8.8): **per region**, the populated grid-cell count equals the `tab:EntryCell`
  count, **or the carriage refuses.** RS2's identity is empirical — one region, one document, five
  minting sites (§ 8.4) — so the check fails closed and is never index arithmetic on trust.
- **O7's null, and it must be answered rather than skipped:** find a region in the corpus where the
  two counts **differ** and show it actually refusing; if none exists, **record that none exists**.
  A control that cannot fire is not a control (the repo's own repeated lesson).
- **The invariant § 8.6 adds, stated once:** the two crossings may not disagree. A cell that
  abstains transiently and carries non-empty `tab:cellText` persistently — or the reverse — is a
  defect, not a tolerance.
- **FALSIFICATION.** Make one region's two counts disagree artificially → the carriage refuses
  (RED without the check). Restore.

### T5 — clause 2's honest form, and the nine consumers M2 found

This task exists because of M1 and M2 and has no counterpart in the spec's task shape.

- **Interface.** A producer-side guard at the site that reads the cell for grounding —
  `feed.py:253-255`, where `is_blank("")` already skips (§ 8.2's measured no-new-code path). The
  guard makes the refusal **explicit and attributable at the call site that built the value**,
  which is the whole reason CLAUDE.md § Producer-side guards keeps one the membrane duplicates —
  and here the membrane cannot reach it at all (M1).
- **Class: PROCEDURAL**, and the code states the irreducibility: the grounded graph and the document
  graph are disjoint, so no declarative constraint can see both ends.
- **Disposition of the other eight EntryCell readers M2 enumerated.** For each, the task report
  states *correct as-is* or *needs a guard*, with the reason:
  `denormalization.py:168` (`_num("")` → `None`, cell drops out of the value matrix),
  `document.py:787-790` (carries `""` into the chain grid),
  `recipe.py:37` via `grid_values`/`row_label`,
  `row-group-key.rq`, `row-group-key-logical.rq` (both filter non-blank already),
  `unpivot-inverse.rq`, `unpivot-inverse-valueset.rq`,
  `tab:EntryCellPhysicalShape` (`sh:minCount 1` survives an empty literal — confirm, do not assume).
- **THE SEAM TO MEASURE, and it is the one M2 flagged** (plan rule 3): `unpivot-inverse.rq:27` reads
  the cell text into the **reshaped** graph and `recipe.grid_values` reads it off the **source**
  graph — the two sides of the reshape round-trip. **Measure the round-trip on gcap before and
  after emptying.** Do not assume both sides move together because both read the same property;
  measure it, and if they diverge that is a finding, not a tolerance to widen.
- **FALSIFICATION.** Remove the guard and hand the grounding path a non-empty unshown cell → a
  tonnage grounds that the page does not show (RED). Restore.

### T6 — the worker (NEURAL), with the ask that is a reader's and the three refusals

- **Interface.** One ask **per region** — the cost gate in R249 half (a)'s shape; 122 gridded
  regions, 0.05–0.54 s per 220-dpi crop, gcap band 3 legible at region grain, **all measured in the
  review and none of it to be re-measured**. In: the rendered crop and the grid dimensions.
  **Never** the text layer's transcriptions. Out: a **closed** shape that cannot express a value on
  the page (§ 8.7 — run 1 returned `14,000` because the shape let it).
- **The ask is a READER's and enhancement is forbidden** — magnification, contrast stretching and
  pixel sampling prohibited *in the ask*. § 8.7 states why once and records the blind run that
  works under exactly those terms.
- **Three refusals**, cited from § 8.7: outside the grid; *"this is not the grid I see"* (refuses the
  whole region — cbh's two blind readers both rejected 18 × 16); and the unpopulated grid position,
  which comes free in the reader's answer, **scoped to positions not inside a spanning cell's
  extent** ([[R211]]).
- **Class: NEURAL**, disposed by the text layer (§ 4.1), and it is the repo's first image-input BAML
  function — built for this question, factored for no second caller (§ 6).
- **§ 8.9 item 2 is this task's to answer, and it is unanswered in the spec:** say what happens when
  run *n*+1 differs from run *n*. Non-determinism is tolerated at the proposal and nowhere else; a
  plan that ships without stating the comparison has left the oracle undefined.
- **FALSIFICATION.** Feed the worker a region with no unshown ink → it must return the empty set,
  not a plausible one.

### T7 — run the oracles, in § 5's order

- **O1 first, on cbh-stem — the run that can kill the spec.** Unchanged.
- **O2 by set identity on gcap** (the same 110, cell by cell, never a matching count — R176/R172).
  **Re-run only as a regression against § 8.7's changed ask**; O1 and O2 already PASS blind and must
  not be re-run to *establish* anything (§ 8.8). The `Y`/`N` second witness (E7) checks O2 without a
  worker and **must not be promoted into the disposal** — 5 `N` flags carry no glyph, and no other
  corpus document has a flag column.
- **O3, the six-document null: bit-identical output.** M2 shows why it holds by construction (no
  unshown facts ⇒ nothing emptied), which makes it a **weaker** control than § 5 assumed. Report it
  as such rather than as a passed prediction.
- **O5: state the expected direction of gcap's score movement BEFORE running it.** A score that
  rises is not by itself evidence — R155's *score-rise-is-a-collapse* is the case.

---

## 3. What this plan deliberately does NOT do

Cited from spec § 6, not re-argued: no colour is read in `src/`; no threshold of any kind;
[[R250]]'s derivation is not built; the 110 transcriptions are recorded and never promoted;
`tab:RegionCaption`'s provenance ([[R218]]) is not repaired; no vision infrastructure is generalised.

Added by this plan's own measurements:

- **The two graphs are not unioned** to give clause 2 a SHACL subject (M1).
- **RF5's grain problem is not solved** — cbh holds 8 cells mixing unshown and ordinary ink that no
  per-cell question can answer (§ 8.9 item 7).
- **The fourth case** — ink the page shows, placed outside any cell — stays unaddressed and is still
  not known to be empty (§ 8.9 item 8).
- **The enhancement prohibition stays unenforceable from the answer alone** (§ 8.9 item 1). Do not
  claim a defector can be detected; the control page that would close it does not exist.

## 4. The weakest parts of this plan, in its author's judgement

1. **T6 is the largest task and the least specified**, because § 8.7 specifies an *ask*, not an
   implementation, and `baml_src/` has no image-input precedent. If the loop runs long, T6 is where
   it will.
2. **M1's `grounded=0`** means T5's guard cannot be exercised end-to-end on gcap by the corpus
   battery's abstaining proposer. The falsification arm must therefore construct the grounding
   path, and a constructed path is weaker evidence than an observed one.
3. **O7's null may not exist in this corpus.** The plan requires it to be searched for and its
   absence recorded; an absence is not a control.
4. **M2's ninth consumer — the reshape round-trip — is named and not measured here.** It is T5's
   first measurement, and if it diverges the loop's shape changes at T5, not at T1.

---

*Author: François Rosselet. © 2026. Plan — CC-BY-4.0 with the rest of `docs/`.*
