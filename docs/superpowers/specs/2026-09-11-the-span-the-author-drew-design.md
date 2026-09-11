# Spec — the span the author drew: graincorp's spanning header, read as a key

**Residue:** [[R211]] (under [[R166]]), from `docs/superpowers/2026-09-11-etkl-02-waits-on-r166-handoff.md` § 9b.
**Serves:** prog:criterion:etkl:02
**Written 2026-09-11**, off `0ca29b0`, branch `etkl-02-spanning-donor-spec`, by a fresh session.

**Doc impact: none.** This loop ships no term and no behaviour. The plan that implements § 3 carries
its own block.

---

## 0. The ruling this spec rests on

Handoff § 9b left one choice to the maintainer: under a key reading, each port on graincorp-capacity
leaves two measures that carry no printed name, a tonnage and a Y/N. Asked in session on 2026-09-11,
with the page's own text in front of them (title `ELEVATION CAPACITY TABLE`; footer `GrainCorp
advise that the tonnages shown are indicative only and are subject to change.`), the maintainer chose:

> **Split.** Name the first measure from the title and footer (elevation capacity, a tonnage) and
> keep the Y/N column as a quarantined proposition (`iladub:CandidateConcept`). Only what the page
> supports is asserted (§7).

**Where it is recorded:** here, and nowhere else yet. It is reversible, and § 6 names the one
reading of it that the maintainer should confirm at review.

## 1. What is already measured

Pointers, not restatements. Each was run by an earlier session on this subject.

| fact | where |
| --- | --- |
| band 2's drawn x's ⊂ band 3's, spans `1,1,2,2,2,2,2,2,2`; the within-band routes fail | R211's row, `residues-open.md` |
| 8 strict-subset pairs corpus-wide; R203's licence refuses the 7 on bfs p6; the subset clause has no corpus negative | handoff § 7 |
| a hand-built two-level region tiles; the feed collapses 16 columns to 9 paths, and two measures land on one property | handoff § 8 |
| all 7 spanning labels are uniquely admitted by `ship:port`; `Year` and `Elevation Period` by none | handoff § 9a |

## 2. Measured this session, on `0ca29b0`

**2.1 — The licence has no carrier in the graph.** `compile_document` on the page gives 5710 triples.
A literal-substring search over every object for `ELEVATION`, `CAPACITY TABLE`, `tonnages`,
`indicative`, `GrainCorp Operations` and `As At` finds **0 hits for each**. The mechanism is the
`NON_TABLE` branch of `compile_tables` (`src/iladub/etkl/compile.py:805-815`): it writes unit markers
when a band carries them, then a `RegionReport`, and **no triple carries the band's text**. The title
and the footer are both ignored bands. → [[R212]].

**2.2 — The proposer is asked without the page.** `ProposeGrounding(surface_text, value,
field_labels)` (`baml_src/ground_propose.baml:8`) is called with `concept.text`, `concept.value` and
the field labels (`BamlGroundingProposer`, `src/iladub/propose_ground.py`). An unlabelled leaf
arrives with `surface_text = ""`. Nothing about the title reaches it.

**2.3 — The corpus battery abstains.** `test_grounding_where_contracted` grounds with an abstaining
`FakeGroundingProposer` (`tests/test_corpus.py:159`). Under the battery, only `exact_field`
(`src/iladub/ground.py:80-85`) and `marker_field` (`:96-117`) can ground a concept. Every concept
that needs a proposal is quarantined.

**2.4 — The shipped unpivot is shaped the other way round, and it is not on the grounding path.**
`vocab/queries/unpivot-inverse.rq` reads the level-0 label as the dimension's **name**
(`?h0l tab:cellText ?dimName`) and the level-1 labels as its **values** (`?h1l tab:cellText
?colLabel`), and casts each measure cell with `xsd:decimal`. graincorp's level 0 carries the
*values* (ports), and its level 1 carries nothing. Separately, `ground_document`
(`src/iladub/feed.py`, the function body) reads `table_records` and calls `ground_concept`, and
nothing else. Reshape is reached only through `denormalization`, which it never calls.

A scratch probe rebuilt handoff § 8's region in both variants. It is not committed; the scripts are
`spanning_region_{reshape,inverse}.py` in this session's scratchpad. Both variants tile and
round-trip. On the table node, the shipped machinery gives:

```
recover_dimensions   A: one column dim, level 0, name=None, 9 values INCLUDING 'Year', 'Elevation Period'
                     B: the same, plus a level-1 dim, name=None, values=('',)
recover_recipe       no UnpivotOp (the dimension has no name, reshape.py:69);
                     8 StripAggregationOp, all function 'min': 4 columns (c6, c8, c10, c12, the tonnage
                     columns of four ports) and 4 rows ('August 1st Half', 'August 2nd Half',
                     'October 2nd Half', 'November 1st Half')
certify              ok=True, residue=(), 0 tab:BaseFact  <- the empty-base short-circuit, reshape.py:103-104
```

To see what a base *would* carry, the probe ran `unpivot-inverse-valueset.rq` directly, with the 7
ports as `opValue` and `Elevation Period` as the stub. It gave 377 BaseFacts. **All 168 coordinate
groups have more than one member** (147 of size 2, 20 of size 4, 1 of size 3). The size-2 groups are
a port's two leaves: a BaseFact's coordinates are one dimension value and one stub value
(`unpivot-inverse*.rq`, the CONSTRUCT template), and nothing in them tells the tonnage column from
the flag column. Only the 110 `0` cells cast to a `tab:measureValue`. So, three findings:

- the shipped reading has no recipe for this pivot;
- its oracle passes vacuously;
- its aggregation detector reads zeros as `min` subtotals.

None of these is on the grounding path, which is why this spec does not build on reshape. → [[R214]].

**2.5 — The tonnage column is not all tonnage.** `pdftotext -layout` over the page, 27 rows × 7 ports:

```
tonnage cells  189 = 149 numerals (110 of them `0`) + 1 blank + 24 `Available` + 15 `On Application`
flag cells     189 = 78 `Y` + 111 `N`
```

Most of the 110 zeros are the invisible glyph in the dark cells (handoff § 2, fourth bullet). The one
blank is Fisherman Islands, 2025/26, September 1st Half. → [[R213]].

## 3. The reading, in two layers

*Which columns does `Mackay` head* is a question about the author's drawing. *Is `Mackay` a key or a
field name* is a question about the destination. They belong to different holons. The compiled
document carries the author's structure. The grounding portal reads that structure against a
contract. If compile decided "key", it would decide semantics without the knowledge module (§1). If
compile consulted the contract, the compiled holon would change with its destination. So the spec
has two layers, and each has its own oracle.

### 3.1 Layer A (etkl, compile): spanning donation, which carries the span

**The relation.** An earlier band `D` on the same page donates a spanning header to a band `R` that
the record-table branch reads iff all of these hold:

- **(a) earlier:** `D` is earlier than `R`.
- **(b) wholly drawn:** every boundary of `_rule_boundaries(D)` is an x the author drew, at 2dp. This
  is grid donation's `drawn` clause, unchanged.
- **(c) licensed:** `D`'s line 0 re-identifies uniquely by ink, and the page datagrid refuses it
  `HeterogeneousColumn/every-measure`. This is [[R203]]'s licence, as grid donation's DECISION C
  emits it.
- **(d) coarser:** `drawn(D) ⊊ drawn(R)` at 2dp, a strict subset. With `R`'s leaf grid equal to
  `drawn(R)`, every interval of `D` is a union of consecutive `R` columns. Equality is grid
  donation's case (`same_ncols`), not this arm's.
- **(e) unique:** exactly one `D` qualifies, as in grid donation's DECISION E.

**Class.** AXIOM, derivation, open world. Its one closed clause, *no drawn x of `D` is missing from
`R`*, is closed within the band pair. The 2dp rounding is inherited from
`sectiongraph._distinct_rule_xs` and `_rule_boundaries`, not tuned (grid-donation plan, Global
Constraint 2).

**The reading.** A `tab:HierarchicalTable` whose level-0 header nodes are `D`'s labels, carrying
`D`'s word boxes. Each covers the `R` columns inside its interval. There are **no level-1 nodes**:
this is variant A of handoff § 8, because a header node with no ink behind it would be invented. `R`'s
line 0 is a data row.

**The disposal.** `region_tiles` and the round-trip, the shipped membrane, as in grid donation.
**The plan must measure two seams before writing a call** (plan rule 3), because handoff § 8a left
both open. Which band's words does `region_round_trips` see? And where does `_book_recovered_ink`
book the donor labels' ink? `D` is `ignored` today and contributes none.

**What happens to grid donation's control.** `same_ncols` still refuses graincorp as an
*equal-count* donation, and it is still right to. The grid-donation spec's § 3(c) control is not
deleted, it is narrowed: a coarser donor is not an equal-count donor, and (d) admits graincorp on its
own evidence. The grid-donation plan runs unchanged.

**Negatives.**

- **Corpus:** the 7 bfs p6 strict-subset pairs, all refused by (c) (handoff § 7b).
- **Synthetic (the subset clause has no corpus negative):**
  - **S1:** a licensed, wholly drawn donor with one drawn x that `R` lacks, refused by (d).
  - **S2:** a licensed donor with `drawn(D) = drawn(R)`, which this arm must not claim. It stays grid
    donation's.
- **Falsifier:** delete (d), and S1 is admitted.

**Prediction for the plan to measure, not run here.** graincorp p0 carries 27 data rows (26 today),
9 level-0 nodes over 16 leaf columns, and header labels equal to the 9 printed labels. No label cell
is numeric.

### 3.2 Layer B (grounding portal, feed): the key split, which reads the span against the contract

**The condition**, read off the compiled graph: a level-0 header node `H` that covers more than one
leaf column and has no child header node. *No child* closes within one table's header tree, which
§8 allows.

**The reading.** Each data row of such a table yields **one record per such `H`**, with record id
`<row id> > <H's label>`. Each record carries:

- the cells of every column that no such `H` covers (graincorp's `Year` and `Elevation Period`),
  copied into each record;
- **`H`'s label as a key candidate**, a concept whose text *is* its value. That is the same kind of
  concept R207 grounds, so `marker_field`'s unique-admission rule is its oracle. Today that rule is
  gated on `is_section_marker`, and the flag's docstring ties it to peeled section captions. **The
  plan measures every reader of that flag first**, then either widens its meaning or names a sibling.
  It must not add a second oracle;
- `H`'s leaf cells, each with an **empty** header text. Nothing is invented.

**The disposal.** `marker_field`:

- **one scheme field admits `H`'s label:** it grounds, as graincorp's ports do to `ship:port`;
- **none or several admit it:** the key candidate is quarantined, and the records stay split.

The split is the author's structure. The key's grounding is the contract's.

**This repairs handoff § 8b's collapse at the record level.** A port's two measures now sit in their
own record, not beside thirteen other columns under a shared path. They still share an empty text,
so neither can be placed by `exact_field`. § 3.3 disposes them.

**Negatives.**

- **Same page:** `Year` and `Elevation Period` each span one column, so they do not split and stay
  field names.
- **Synthetic:** a spanning childless parent that no scheme admits yields split records with a
  quarantined key, never a field name.
- **Falsifier:** delete *covers more than one*, and `Year` becomes a key.

**Census on today's compile, 2026-09-11 on `0ca29b0`.** A subagent measured it; the script is not
committed. Over `compile_document` of the 7 corpus documents, count the level-0 `tab:HeaderNode`s
that cover more than one column and are the `tab:parentHeader` of no node:

```
graincorp-stem 0   graincorp-capacity 0   cbh-stem 0   ons 0   bfs 0   apple 0   who 0
multi-column level-0 nodes WITH children: apple 2 ('Three Months Ended', 'Nine Months Ended'),
who 6 (the caption 'Z-scores (weight in' / 'kg)' split across two siblings, on each of 3 pages)
```

**So Layer B fires on nothing that compiles today.** Every split it will make comes from Layer A.
Those 8 nodes are the *childless* clause's corpus negative: delete that clause, and apple's and who's
column groups split into records.

### 3.3 The measures: what the Split ruling makes true

- **The contract.** Author `examples/shipping/capacity-contract.ttl` with shapes, and borrow the terms
  from `stem-terms.ttl`: GrainCorp's own port scheme, matched exactly (handoff § 9a). The fields are
  `year`, `elevationPeriod`, `port` (with `ship:scheme-port` as its admissible scheme) and
  `capacity`. `capacity` has a value constraint: the numeral pattern that `stem-shapes.ttl` already
  declares for `ship:total`. **There is no field for the flag.**
- **The licence.** The contract author names `capacity` from the page's title and footer (§ 0) and
  records that on the field, quoting both lines. This is §1: the knowledge module names the measure,
  and the compiler does not.
- **The binding.** An unlabelled leaf reaches `capacity` only by proposal, because neither
  `exact_field` nor `marker_field` can place it (§ 2.2). The proposal is disposed by `_grounds_to`'s
  value-constraint branch (`ground.py:160-167`). A deterministic "the one field whose constraint
  admits this value" rule is **refused**. `marker_field`'s own docstring says why: grounding a data
  cell by its value alone lets the value decide the field instead of the author's structure (§0).
- **What it asserts:**
  - **Tonnage:** numerals that pass `capacity`'s pattern ground.
  - **Flag:** `Y`/`N` fails the pattern and is **quarantined**, which is the ruling's second half,
    and it falls out of the membrane with no special case.
  - **`Available`/`On Application`:** the 39 cells fail the pattern too, and are quarantined. They
    describe availability, not a tonnage.
- **What the corpus battery sees** (§ 2.3). Its proposer abstains, so **no leaf grounds**, and all
  378 leaf cells are propositions. The keys and stubs ground. That is the honest outcome, and this
  spec does **not** change the battery's proposer to make it greener.
- **What a live proposer sees today.** `surface_text = ""` and the value, not the title the licence
  rests on (§ 2.1, § 2.2). For the machine to consume the licence, the ignored bands' text must be
  carried ([[R212]]) and the proposer must be handed it. Neither is this spec's work.

### 3.4 The year

**Not repaired here, and the maintainer's read will see it.** The author prints `2025/26` and
`2026/27` once per group. Once donated, the body has column 0 filled only on rows 0 and 3. The one
shipped route that hands a suppressed key to the rows below it is `_inject_group_keys`, and it reads
`tab:DerivedRowGroup`. That type has exactly one emitter, `rowgroups.derive_row_groups_over`, and
both of its callers take their witnesses from **arithmetic aggregation rows**
(`holon.py:608-610`, `document.py:902-922`). graincorp has no subtotals, and the probe measured 0
`DerivedRowGroup` in both variants. So **25 of 27 records will carry no year**.

That is a §5 loss. It is not a §7 false assertion: nothing wrong is carried, and something true is
missing. Recovering it means reading a blank as "same as above". That is an inference from
**absence**, which §8 forbids a derivation to make unless the evidence is present. So the question is
genuinely open, and it belongs to its own row → [[R215]]. Whether etkl:02 can be adjudicated with
years missing is the maintainer's call at step 3 of § 5.

## 4. What this loop does NOT do

- It ships no code and no plan. This spec is written in the first third of the session. A plan is a
  fresh session's work.
- It does not execute `plans/2026-09-11-grid-donation.md`. That plan goes first (§ 5), unchanged.
- It does not close [[R166]], [[R211]] or etkl:02. R211 closes when graincorp's records carry port
  names and the maintainer has verified them against the page. etkl:02 needs a pinned floor and an
  adjudication after that.
- It does not name the flag, and it does not carry the title or footer ([[R212]]).
- It does not change which proposer the corpus battery uses.
- It does not touch bfs p6: its 7 strict-subset donors are refused by (c) today and stay refused.

## 5. Sequence

1. **Execute the grid-donation plan as written.** Layer A reuses its evidence emitter, licence fact
   and seam (DECISIONS B and C), and those must be *shipped* before a plan can measure against them
   (plan rule 2).
2. **Write one plan for Layers A and B together, plus the capacity contract**, as two task groups.
   Layer B has nothing to split until Layer A mints a spanning node, and Layer A alone changes
   graincorp's records without making them groundable.
3. **The maintainer reads the carried records against the page**, which is route step 3 in the
   manifest's hold note (`tests/corpus-manifest.ttl:57`).

## 6. Unverified or assumed

- **One reading of the ruling needs the maintainer's confirmation.** This spec reads "name from the
  title and footer" as *the contract author names the field, with that text as the licence*. If the
  intent was that the **machine** derives the name from the title, then [[R212]] and a proposer input
  carrying the table's furniture become prerequisites of this spec, not later work.
- **Layer B's population is measured on today's compile, not on the post-Layer-A one.** That is
  § 3.2's census, and it counts 0 matches. After Layer A, graincorp is predicted to be the only
  match. That prediction is not run.
- **§ 3.1's prediction is not run.** The seams named there are open.
- **The contract borrows the stem's port scheme.** It matches graincorp-capacity's labels exactly
  (handoff § 9a). Whether it is the right *authority* for a capacity table is a vocabulary question.
- **What `Y`/`N` means is a reading, not a fact.** Nothing here asserts it, and the quarantine is
  what keeps it so.
- **Putting the split in the feed rests on § 3's argument, not on a measurement.** The alternative is
  the compile side, with a contract-free structural key. It was considered and refused, for the
  reason given there.

## 7. Residues raised

- **[[R212]]:** an ignored `NON_TABLE` band's text reaches no triple (§ 2.1).
- **[[R213]]:** the invisible `0` glyph in dark cells. It has been carried unregistered through two
  handoffs (§ 2.5).
- **[[R214]]:** the shipped unpivot reads name-over-values only, and a value-over-measures pivot like
  graincorp's has no recipe. Its oracle passes vacuously on an empty base, and its aggregation
  detector reads zeros as `min` subtotals (§ 2.4).
- **[[R215]]:** a key the author prints once per group reaches only its first row when the table has
  no subtotals, because row groups are derived from arithmetic witnesses alone (§ 3.4).
