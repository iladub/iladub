# ET(K)L's two regimes, and the author-split table — design

**Date:** 2026-08-09 · **Status:** **BLOCKED at adversarial review, 2026-08-09** — see §8 ·
**Specimen:** `corpus/ag-trade/cbh-stem-2026-08-03.pdf` page 0, with `apple` page 0 as the
control · **Builds on:** `2026-08-08-data-grid-types-elements-axioms.md` (the data grid,
closed) · **Revisits:** `2026-08-07-producer-signature-design.md` (blocked — its
`RejoinSectionsOp` was rejected on the wrong specimen; see §6)

**Doc impact:** increment — new owned `tab:` terms for the author split and the unnamed
dimension; a stated architectural boundary. No site page contradicted.

---

## 0. The separation

François, 2026-08-09:

> We should not mix resolving the holon internal state with its projection required by another
> holon at the interface membrane. ET(K)L does 2 things: resolve an agnostic internal state with
> its own transformations, and also the transformations required by the projection induced by a
> contract at the membrane.
>
> The holon does not describe itself with an explicit port attribute for the data grid — the
> notion of port is **implicit**, which is a problem only for a projection another holon needs
> where the port name must be part of the data schema.

```text
DOCUMENT
   │  AGNOSTIC INTERNAL RESOLUTION — runs ONCE, contract-free
   │  de-accommodate · segment · recover grid · absorb unit markers
   │  detect aggregates · group rows · REJOIN author-split panels
   ▼
HOLON   immutable · the maximal PROVABLY recoverable pre-print state
        partially self-describing: complete on structure, partial on vocabulary
   │
   │  CONTRACT-INDUCED PROJECTION — runs PER CONTRACT, N times
   │  derived on demand, never stored; only the decisions persist
   ▼
VIEW
```

**The boundary test: can the transformation be justified by evidence in the document alone?**
`GERALDTON` is ink, so the dimension's *values* are internal. Nothing in the document says
"port", so the *name* is projection.

**"Implicit" is not "missing."** The port is in the holon — a dimension with four values,
asserted, provenanced, constant per panel, bijective with the panels. What is absent is only its
*name as a schema attribute*. The holon is structurally complete and only partially
self-describing, which is honest, and better than inventing a name to appear complete.

### 0.1 Three decisions, settled in brainstorming

1. **The holon un-does authoring operations it can prove.** CLAUDE.md §2b already commits to
   this at one layer (de-accommodate to template coordinates); this extends the same logic
   upward. The holon is not the page — it is what the author had before printing, as far as that
   is provable.
2. **Proof = evidence proposes, the round trip disposes.** Structural evidence generates a
   *candidate* un-doing; the recipe must replay the operation forward and regenerate the observed
   ink, or the un-doing is refused. Neither half suffices: evidence alone fabricates, the round
   trip alone has nothing to test. This is R13's recorded lesson — *the AXIOM disposes, it does
   not generate*.
3. **A projection is derived on demand; only its decisions persist.** The view is a query over
   the holon, never stored — exactly as `risk:RiskAssessment` is a derived `hproj:Projection` and
   never a stored label (SHACL-enforced). But a promotion is an **act**, so the
   `dec:DecisionHolon` that named a dimension *is* recorded. Nothing about contract B can appear
   in a read of contract A's view, because neither view exists as data.

### 0.2 Why the separation is load-bearing, not tidiness

One document compiles **once** and projects **many** times. Two contracts cannot both be right
about a single stored holon: one wants `port` promoted to a column, another never asks. Put the
resolution in the holon and the two contracts collide; put it in the projection and the holon
stays agnostic. This is the same reason `risk:RiskAssessment` may not be stored.

## 1. Why the projection side is already unblocked

`src/iladub/splitkey.py` implements the three-arm naming cascade (loop Q): explicit `Key: Value`
naming (AXIOM), unique-admitting contract field (AXIOM — ground the marker *values* against the
contract's SKOS schemes; exactly one admitting field derives the name, **no LLM**), then a BAML
proposal that can only ever narrow an already-verified set.

Two facts make it fit this architecture exactly, and both were measured:

- **It requires a contract** (`resolve_split_key_name(markers, contract, terms, proposer, graph,
  context)`), so it structurally cannot run at compile time — and `compile_tables` takes no
  contract. The split is already clean in the code.
- **It has no production caller.** It is referenced only from `tests/test_split_key_naming.py`
  and `tests/test_cbh_e2e.py`; its own docstring says *"read before wiring this into feed.py /
  ground_document"*, and that wiring never happened.

So there is nothing to migrate. The projection side is a **first wiring at the moment it was
always meant for** — and it is out of scope here (§7).

## 2. The first slice: the author split, internally

Prove that the author split one table into panels, rejoin them, and emit the suppressed column
as an **unnamed** dimension. Contract-free throughout.

### 2.1 Proposal — three conditions, all presence or ordinal

| # | Condition | Why it is not a heuristic |
| --- | --- | --- |
| A1 | A line is **repeated** *and* is **refused by the every-measure refutation** | Repetition alone is a measured false positive — see §3.2. The refutation already exists, ships, and is what caught cbh's four headers |
| A2 | The panels between repeats **share a column grid** | Measured §3.1 |
| A3 | Each panel carries **exactly one** annotation that is distinct and **centred on the full grid width** | A spanner covers a proper subset of leaf columns; this covers the whole width, which is what a constant column value looks like |

### 2.2 Disposal — the round trip, and what it closes

The candidate rejoin is admitted only if `tab:ReshapeRecipe` can replay the split forward and
regenerate the observed ink, with the conservation shape accounting for every glyph.

**This closes R54 by oracle rather than by rule.** Distinguishing `GERALDTON` from
`BERTH MAY BE UNAVAILABLE…` has been an open residue, and every attempt at it was a heuristic.
It is not a heuristic question: choosing the key is part of *proving the rejoin*. Pick a berth
notice as the dimension value and the forward replay puts that text where `GERALDTON` sits — the
ink does not regenerate, and the conservation shape finds glyphs unaccounted for. A wrong choice
is **refused**, not merely unlikely.

### 2.3 Emission

- One rejoined grid over the four panels' shared columns.
- An **unnamed** `tab:PivotedDimension` carrying the four values, each with provenance to its
  source annotation and the panel it governs. `tab:dimensionName` is **absent** — deliberately,
  and that absence is the honest record of what the document does not say.
- `tab:RejoinSectionsOp` in the recipe, so the split replays and the round trip stays checkable.
- The whole admission recorded as a `dec:DecisionHolon`, as the data grid's already is.

## 3. Premises, measured

### 3.1 The four panels share one column grid — HOLDS

```text
panel 0 (lines  9..23): 10 body rows, modal x-signature (50, 108, 179, 224, 275, 310, 385, 461, 501)
panel 1 (lines 25..46): 16 body rows, modal x-signature (50,  99, 179, 224, 275, 310, 379, 461, 501)
panel 2 (lines 48..66): 14 body rows, modal x-signature (50, 108, 179, 224, 275, 310, 385, 461, 501)
panel 3 (lines 68..84): 10 body rows, modal x-signature (50, 101, 179, 224, 275, 310, 385, 461, 501)
```

Seven of nine positions identical across all four. The two that vary are **left-aligned text
columns** whose ink starts where the text starts — not column boundaries.

### 3.2 Repetition alone is NOT sufficient — the measured false-positive class

```text
cbh   p0: x4  VNA # Vessel Name Time Nominated Date Nominated ...   reprinted HEADER
apple p0: x2  Services 30,739 27,423 91,728 80,408                  repeated DATA row
apple p0: x2  Total net sales $ 109,417 $ 94,036 ...                repeated DATA row
ons   p1: x3  Dataset | Released 16 April 2026                      page furniture
```

apple's segment and category breakdowns legitimately repeat the same figures, so a naive
"repeated line ⇒ reprinted header" rule fires on real data. The discriminator is *repeated **and**
not a data row* — already implemented and already pinned by
`test_cbh_repeated_headers_are_not_data`.

### 3.3 cbh is author-split; apple is not — HOLDS

cbh reprints its header four times (lines 8, 24, 47, 67), one per panel. apple's banding runs
unbroken y=139.56→746.28, so **iladub's own segmenter** split that page. Only cbh is author-split
in the corpus (§3.2's scan), which bounds the blast radius to one document.

### 3.4 The annotation is centred on the full grid width — HOLDS

```text
grid extent x 38.2..1151.4, centre 594.8
GERALDTON / KWINANA / ALBANY / ESPERANCE  centres 595.1-595.3
```

Within half a point of the full table centre, so the annotation is not a spanner over a subset.

**A hypothesis measured and REFUTED on the way:** that keys are centred while notices are
left-aligned. False — the notices are centred on 595.1 too. Centring separates *annotation from
spanner*, not *key from notice*.

### 3.5 NOT measured, and named as such

| # | Premise | Status |
| --- | --- | --- |
| P5 | The round trip actually refuses a wrong key choice | **NOT MEASURED.** It is the crux of §2.2 and cannot be measured without implementing the forward replay. If it turns out the round trip admits a wrong key, this design loses its oracle and falls back to heuristics — the failure mode that blocked three specs |
| P6 | A cbh transcription will agree with the rejoined reading | **NOT MEASURED** — the oracle does not exist yet, and cbh currently reads 46 of 85 lines with no ground truth |
| P7 | The full-width-centred rule generalises | **ONE DOCUMENT.** stem is the natural control: it keeps the port column and ditto-suppresses it instead, so the same information is carried two opposite ways by two authors |

**P5 is the one to attack.** Everything in §2.2 rests on the round trip being decisive, and that
is asserted, not shown.

## 4. Success criteria

- cbh page 0 yields **one** grid over the four panels' shared columns, not four.
- An unnamed `tab:PivotedDimension` carries exactly `{GERALDTON, KWINANA, ALBANY, ESPERANCE}`,
  each provenanced to its annotation and its panel, with **no** `tab:dimensionName`.
- Substituting a berth notice for a port name in the candidate key set is **refused by the round
  trip**, demonstrated by a red test — not merely absent from the output.
- A cbh transcription exists and the rejoined reading is measured against it.
- apple, stem, capacity, who, bfs, ons **byte-identical**; stem's document compile stays
  `0.9654553611484971` and its 0.95 floor holds.
- No tuned constant. A1–A3 are presence, ordinal or containment tests.

## 5. Out of scope

- **The projection side.** Wiring `resolve_split_key_name` at the membrane, the
  contract-requires-a-missing-field trigger, and the metadata lookup. That is the next slice and
  it needs this one first: there is nothing to name until the dimension exists.
- **Naming the dimension.** Deliberately. The holon emits it unnamed.
- **Producer signatures.** Still unmeasurable (stem and capacity carry byte-identical metadata
  and land in different signature classes).
- **R73 adoption**, and the degenerate-score work — both closed or parked elsewhere.

## 6. What this revisits

`RejoinSectionsOp` was recorded as rejected in the producer-signature spec. That rejection was
**correct for apple and over-broad in the record**: apple's banding is unbroken, so no author
operation was performed and there was nothing to invert. cbh's author *did* split, evidenced by
four reprinted headers over one shared grid, so the inverse is real. The residue register and the
blocked spec both need this correction; the producer-signature idea itself stays rejected.

## 7. Global constraints (carried, per CLAUDE.md)

- **§8 gate.** A1–A3 are presence/ordinal/containment tests; the disposal is the shipped
  round-trip oracle. The forward replay is justified PROCEDURAL (regeneration of ink), the
  conditions are AXIOM.
- **§7 only emit what the source supports.** The dimension is emitted *unnamed*, because the
  document does not name it. Where the round trip refuses, the panels stay separate and the
  refusal is recorded.
- **§5 context is carried.** Annotations that are not the key (berth notices, maintenance
  notices) are carried as annotations, never dropped.
- **§0 recover the author's structure.** Rejoining is recovery, not interpretation — which is
  exactly why it must be provable and not merely plausible.
- **Source ownership.** `tab:` is ours; `hproj:` appears only as an alignment object.

---

## 8. Adversarial review — BLOCKED (2026-08-09)

The review attacked P5 as instructed and took the design apart. Findings re-verified by the
controller before acceptance.

### 8.1 BLOCKING — the disposal does not exist, and cannot be built the way §2.2 assumes

`oracle.round_trip` compares `{(row_label, col_leaf_label): cellText}` dictionaries built by
`recipe.grid_values`, which requires `tab:hasCell` and a header tree. **It never touches a
coordinate, a glyph or a page.** The data grid emits `tab:hasDataCell` and reads no header at
all, by design. Run on the cbh data grid:

```text
EntryCells 737 | t hasCell 0 | t hasDataCell 737 | coversColumn 0 | headerLevel 0
grid_values(datagrid) -> 0 entries | recipe ops () | verdict True | BaseFacts 0
```

The oracle returns **True on an empty reading** — it would accept any key choice. And the
ontology has exactly two reshape operations (`UnpivotOp`, `StripAggregationOp`); no split, no
page-level forward replay exists. `denormalization.denormalize`, the only production wrapper
around `certify`, has **no caller** and iterates `RecordTable`/`HierarchicalTable`, which a
`tab:DataGrid` is not.

Worse, the closest shipped analogue — a proposer naming a nameless pivoted dimension, disposed
by `certify_with_proposals` — is **provably invariant to the name**:

```text
name='Quarter'                         oracle_ok=True
name='BERTH MAY BE UNAVAILABLE 2000HRS' oracle_ok=True
name='Zqxjv'                           oracle_ok=True
name=''                                oracle_ok=True
name='Product'                         oracle_ok=False   <- a collision with a stub label, not a semantic check
```

**And the general argument defeats any implementation**, not just the shipped one: a forward
replay must be parameterised by panel extents and the annotation text per panel, which are not
derivable from a rejoined grid and must therefore be stored on the `RejoinSectionsOp`. *If the
op stores enough to replay exactly, it stores the answer and cannot refute; if it stores less,
the replay is not exact for the correct choice either.* **A round trip cannot dispose an
assignment its own recipe records.**

The conservation shape does not rescue it: `tab:HeaderContentConservedShape` targets
`tab:HeaderSourceCell`, of which cbh page 0 has **zero**, and it accepts text surfacing in any
`RegionCaption` — so under §7's own "notices are carried as annotations" rule, *both* readings
conserve. Already on the register as R9 (*conservation shape unreachable*).

### 8.2 BLOCKING — A1–A3 admit a rival key set on the specimen

Re-measured by the controller:

```text
block 0: PORT MAINTENANCE x1 | GERALDTON     block 3: PORT MAINTENANCE x1 | ESPERANCE
block 1: PORT MAINTENANCE x1 | KWINANA       block 4: PORT MAINTENANCE x0 | (none)
block 2: PORT MAINTENANCE x1 | ALBANY
```

`PORT MAINTENANCE SHUTDOWN AM …` occurs once in four of five blocks — **the same distribution as
the port names** — all four strings distinct, and centred *tighter* on the grid axis (dev +0.26
to +0.32 against the ports' +0.37 to +0.47). It satisfies A1–A3 at least as well. The proposal
is genuinely ambiguous and only world knowledge picks the ports.

The review also found an **off-by-one**: annotations are drawn *above* their header, so under
§3.1's own panel ranges `GERALDTON` belongs to no panel, panel 0 is labelled `KWINANA`, and
panel 3 is unlabelled. The bijection §0 claims does not hold.

### 8.3 REFUTED — "only cbh is author-split", by this repo's own closed spec

`2026-08-08-data-grid-types-elements-axioms.md` §3 lists **apple p0 as T4, "three panels sharing
one boxhead"**, with `Total net sales 109,417/94,036/364,357` appearing three times as the
evidence. This spec reinterprets that same repetition as a false positive (§3.2) and infers from
unbroken banding that no author split occurred. **apple p0 has unbroken banding AND three
author-authored panels.** What it lacks is a *reprinted boxhead*, not a split. The blast-radius
claim falls, and §6's "the rejection was correct for apple" inherits the defect.

### 8.4 REFUTED — three factual claims

- **§0.1(1) cites a CLAUDE.md §2b that does not exist.** Verified: zero matches for
  "de-accommodat" or "template coordinate" in CLAUDE.md. The real reference is the 2026-08-04
  cbh-dimension-split spec's §2b. A Contract-class document was said to commit to something it
  does not.
- **§6's "the residue register needs this correction" is false** — there is no `Rejoin` row in
  `residues.md`. And the producer-signature spec was *not* over-broad: it scoped its own P4 as
  "not measured — assumption, blast radius: the loop may target apple only". Amending it would
  also rewrite Evidence, which is immutable after loop close.
- **§2.2's R54 closure does not match the register.** R54's live residual is
  `feed.table_records`' `caps[0][0]` picking the positionally-first caption — which a holon-side
  rejoin never touches — and its recorded closing path is *scheme-membership filtering*, which
  this spec puts out of scope. The register also asks for a counterexample document first.

### 8.5 The real design tension, which the spec routed around

The one disposal that demonstrably separates `{GERALDTON, KWINANA, ALBANY, ESPERANCE}` from
`{PORT MAINTENANCE …}` is **whole-set scheme membership** (`splitkey._admitting_fields`) —
already implemented, already decidable. It is **contract-dependent**.

So the clean holon/projection boundary of §0 puts the only working oracle on the projection side,
while §2 needs it on the holon side. Decision 0.1(1) — *the holon un-does what it can prove* —
may be **empty for this operation**, because without the contract there may be nothing provable
here at all.

The stem control sharpens it: stem *names* `Port` in its own ink, cbh does not. The same
real-world dimension therefore yields a **named** column in one holon and an **unnamed**
dimension in the other, inside one corpus. That is the strongest argument for naming at the
membrane — and it is also why the split itself may not be provable without one.

**What survives:** §1 (fully confirmed — `resolve_split_key_name` is test-only and requires a
contract; `compile_tables` takes none), §3.2's discriminator (confirmed and strengthened — stem
p0 also repeats `Mackay Total 5 0,000` as data), §3.4 (confirmed to the decimal, including its
own refuted centring hypothesis), and P7's stem control.
