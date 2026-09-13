# The span the author drew — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:etkl:02 — Layers A and B are [[R211]]'s two arms. R211 closes when
graincorp-capacity's records carry port names, verified against the page by the maintainer; etkl:02
needs a pinned floor and an adjudication after that. R166 is the criterion's declared
`prog:blockedBy` (`tests/arc-manifest.ttl:215`; the block is `:210-219`).

**Goal:** the nine port labels the author drew on a band of their own become the column headers of
the 27-row table beneath them, each heading the two leaf columns its drawn interval contains; the
grounding portal then reads each spanning label as a key rather than a field name, splitting one row
into one record per port; and the page's own title and footer reach the proposer, so the machine —
not the contract author — derives the unlabelled measure's name.

**Architecture:** two layers with two oracles, because *which columns does `Mackay` head* is a
question about the author's drawing and *is `Mackay` a key or a field name* is a question about the
destination (spec § 3). Layer A is compile-side and contract-free; Layer B is portal-side and reads
the compiled structure against a contract. A third task group hands the carrier's furniture text to
the proposer and authors the contract.

**Tech Stack:** Python 3, rdflib, pySHACL, pytest, reportlab (synthetic fixtures), BAML. RDF Turtle
for vocabulary, shapes, contract and terms; SPARQL for the derivations.

**Spec:** `docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md`. **§ 0 governs
wherever the body disagrees with it** — the body was drafted on a reading the maintainer refuted on
2026-09-12 (the machine derives the measure's name).

**Evidence this plan is built on** — `docs/superpowers/2026-09-13-the-span-the-author-drew-evidence.md`.
Read the section before the task that cites it; **no task re-derives one.**

| § | what it settles |
| --- | --- |
| 1 | the relation refuses graincorp on exactly one clause, `?n` |
| 2 | **both shipped covering oracles are REFUTED** — the spec's § 3.1 reuse assumption fails |
| 3 | variant C is constructible: partition `1,1,2,2,2,2,2,2,2`, `region_tiles` → True, tolerance INERT |
| 4 | the full page membrane accepts donor-sourced label geometry; document scope is UNVERIFIED |
| 5 | `region_round_trips` never sees the donor and is largely vacuous at `body_line = 0` |
| 6 | the ink ledger does not move: 406, the figure already pinned |
| 7 | ink-center and ordinal agree on ONE donor — a decision with a falsifier, not a fact |
| 8 | Layer B's five splice sites, the dropped column, the injection precedent, the `tab:covers` decoy |
| 9 | `marker_field`'s single gate, and the negative pin that constrains how it may widen |
| 10 | the proposer's blank subject, and two page-context slots the repo declared and left dead |
| 11 | the seam's cost, measured both ways: 2 call sites against 5 + 35 |
| 12 | the contract carries a licence pointer for free; where it may point, by declared range |
| 13 | what is pinned on graincorp-capacity today |

**Doc impact: increment.** New `tab:` terms and a new `etkl`-family example contract are declared in
published, CC-BY artifacts (`vocab/ontology/tab.ttl`, `examples/shipping/*`);
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM entry. No released assertion is
contradicted, so **nothing blocks a release tag**.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **The neurosymbolic gate (CLAUDE.md §8).** Layer A's covering is **AXIOM, derivation, open
   world**: set containment of drawn x's, expressed in SPARQL over a transient evidence graph, with
   the query free of numeric literals (template: `vocab/queries/header-covers.rq`). Its one closed
   clause — *no drawn x of D is missing from R* — is closed **within the band pair**, which is the
   holon-scoped guard §8 permits. **The tolerance is INERT and must stay inert**: evidence § 3
   measured `eps=0.01` and `eps=0.0` identical, because every donor x appears verbatim in the
   recipient vector at 2dp. **A tolerance doing work anywhere in the shipped diff is a review
   failure**, not a tuning opportunity. The 2dp rounding is inherited from
   `sectiongraph._distinct_rule_xs` (`:188`), never re-tuned.
2. **Source ownership (CLAUDE.md § Source ownership).** Every new term is `tab:` or `etkl:`, ours.
   No `w3id.org/holon` IRI enters any file this plan touches; no HGA term is ever a subject
   (`tests/test_source_ownership.py`, CI-enforced).
3. **Plan rules 1–7 (CLAUDE.md § Plan authoring discipline).** No function body appears in this plan.
   Tests are given as **contracts and exact assertions**, never as transcribed fixtures; coordinates
   and fixture geometry are the implementer's to measure. **A supplied assertion is a proposition** —
   one that cannot be made to pass has found a plan or spec defect; say so in the task report and
   substitute the satisfiable form carrying the same force, **never a weaker one**. **Every task ships
   a `## FALSIFICATION` block** (rule 4); no falsification evidence ⇒ the task review fails.
4. **`corpus/` is gitignored** (`.gitignore:52`). A fresh worktree has no corpus and every
   corpus-gated test **skips green**. Symlink first and verify `ls corpus/ag-trade` lists the
   graincorp PDFs. **A green CI is not evidence for any corpus arm of this plan.**
5. **macOS has no `timeout`** and `pytest --timeout` is not installed: wrapping a run in either runs
   nothing and exits 0. **Read the output, never the exit code.**
6. **The full suite runs in-band, never in a background subagent, and in chunks.** The R212 loop had
   three runs killed by the system for low memory; `tests/etkl` must be run in segments of roughly
   eight files, each redirected to its own log on disk. A run piped into `tail` loses its own
   evidence when killed.
7. **Population gates move at `git add`, not at file creation.** `test_artifact_terms.py` and
   `test_artifact_declarations.py` count tracked `.ttl` outside the fixture directory, so every local
   run is green while new fixtures are untracked and only the committed tree fails. Re-baseline them
   as a **set** (added/removed), not as a count. Current baseline: **157**.
8. **The vacuity registry is two-sided** (`tests/etkl/test_vacuity_registry.py`): a shape that is idle
   and unregistered fails, **and a registered shape that has gone live fails too** — "a stale
   registration is how a guard rots into a rubber stamp." Any shape this plan ships is either live on
   the corpus or registered with a measured reason.
9. **Branch protection.** Branch first; `main` is reachable only through a PR whose `test` check is
   green. Branch `span-donation-plan`, cut from `main` at `4e5ef50`.

---

## The invariant, stated ONCE (plan rule 6)

> **Layer A changes which columns the author's labels head. It moves no ink.**

`assert_hier_region` on the variant-C reading returns **406**, exactly the figure
`tests/etkl/test_run_merge_seam.py:163` already pins for `("graincorp-capacity-2026-08-04", 0)`
(evidence § 6). The donor's own words are booked by nobody today and are booked by nobody after:
`_book_recovered_ink` (`compile.py:276`, called at `:1041-1043`) iterates the **recipient's**
`band.lines`, and the ignored branch touches no counter (`compile.py:814-829`).

Every task below cites this line. **No task re-derives it**; Task 3 re-runs it on the shipped seam
rather than on the probe.

---

## The seven decisions this plan takes

Stated once here; **cited** from the tasks.

### DECISION A — the covering is derived from the donor's DRAWN INTERVALS, in its own evidence graph

Neither shipped oracle can produce the reading (evidence § 2): both are ink-overlap derivations, and
a one-row donor makes `leaf_lvl = 0` (`headers.py:445`) so every label takes the single-column leaf
rule. The covering is therefore **new** — a derivation asking *which recipient columns lie inside this
donor interval* — authored on the `header-covers.rq` template: geometry emitted as evidence, the
decision entirely in the query, **no numeric literal in the query**.

It gets its **own transient graph and its own population**, not an extension of `tab:DonorBand`.
`tab.ttl:336` states the rule and the reason: *"each is emitted into its OWN transient graph — never
merged, because a node read under the wrong population's query answers a question its facts were not
emitted for."* Today the recipient reaches the donor relation only as an `initBindings` **count**
(`donation.py:76-83`); a covering needs its **boundaries**, which is a different question about a
different subject.

### DECISION B — a label belongs to the interval containing its ink center; ordinal is the FALSIFIER

Half-open containment, `d[i] <= cx < d[i+1]`, the same convention `regions.column_of` and
`header-covers.rq` use (and which `header-covers.rq`'s header records as load-bearing). Evidence § 7
measured ink-center and ordinal agreeing on **all 9** labels — of **one** donor, on one page. That is
not evidence they agree generally, so the plan **chooses** ink-center and pins ordinal as the
falsifier: a synthetic donor whose label ink center falls outside its own drawn interval must make
the relation **refuse**, not choose. A donor with a label matching zero intervals, or more than one,
donates nothing.

### DECISION C — the reading is a `HierRegion` with the donor's tree and the recipient's rows

`HierRegion(grid=recipient_grid, tree=donor_tree, rows=logical_rows(recipient, recipient_grid,
recipient.lines[0].top), body_line=0)`, asserted by `assert_hier_region`. This is legal and measured
(evidence § 3, § 5): `assert_hier_region` references `band` exactly once, at `holon.py:542`, and that
one gate never dereferences `region.tree`. **There are no level-1 nodes** — a header node with no ink
behind it would be invented (§7).

**The disposal is the shipped membrane, unchanged:** `region_tiles`, measured **True** on this exact
reading (evidence § 3), and `tab:UnambiguousAccessShape:141` *defines* a leaf header as one nothing
points at via `parentHeader` — so nine childless spanning nodes are the canonical shape it asks for,
not a shape it tolerates. **No new shape is authored for Layer A**, and consequently no vacuity
registry row is owed (Global Constraint 8).

### DECISION D — clause (d) is ADDED, and `same_ncols` is narrowed, never deleted

The relation admits a donor on **(a)** earlier, **(b)** wholly drawn, **(c)** the R203 licence,
**(d)** `drawn(D) ⊊ drawn(R)` at 2dp — a **strict** subset — and **(e)** exactly one qualifying donor.
Equal-count donation stays grid donation's, unchanged and still refusing graincorp as an equal-count
donor, which it is right to do. Grid donation's only measured null control is preserved by
narrowing rather than deletion (spec § 3.1). Clause (e) reuses the shipped Python uniqueness rule at
`donation.py:226` and **adds no ordering rule**.

### DECISION E — Layer B routes a NEW population to the SAME oracle, via a sibling flag

`marker_field` is gated by one line, `ground.py:113`, and admits on unique scheme membership
(evidence § 9). Layer B's key candidates are the same *kind* of concept — text that **is** its value,
which `exact_field` can never place — so they must reach the same oracle. But they are a **different
population**, and widening `is_section_marker`'s meaning would fight an existing negative pin:
`tests/test_corpus_stem.py:263` asserts that no record may carry a furniture-sourced marker.

So: a **sibling flag** on `SurfaceConcept`, and `marker_field`'s gate becomes a two-population
disjunction. **One oracle, two populations, both pins keep meaning what they meant.** The spec's
"must not add a second oracle" is honoured literally: `marker_field`'s body is untouched.

### DECISION F — the proposer seam is a defaulted PARAMETER, not a field on `SurfaceConcept`

Measured both ways (evidence § 11): a defaulted parameter threaded `ground_document → ground_concept →
propose_grounding` touches **2** production call sites and leaves 24 test call sites working; a fifth
field on the frozen `SurfaceConcept` touches 5 src + 35 test construction sites and changes
`__eq__`/`__hash__` at three comparing sites.

`ProposeGrounding` gains an optional page-context parameter, following `ProposeDimensionName`'s
`table_title: string?` precedent (`reshape_propose.baml:7`). **And it must actually be filled** —
evidence § 10 measured that this repo has declared such a slot twice and left both dead, which is
exactly how the previous two attempts failed. A test that asserts the slot is non-empty for a real
compiled document is therefore part of Task 6, not optional polish.

Because `baml_client` is gitignored and regenerated in CI on every PR (`ci.yml:23-24`), a signature
change cannot ship stale — but **no drift pin exists for `ProposeGrounding`** (one exists only for
`ProposeHeaderRowRoles`, `tests/etkl/test_rowrole_proposer.py:37-89`). Task 6 adds one on that model.

### DECISION G — provenance points at the source REGION, not at the band node

`dec:consideredEvidence` is `rdfs:subPropertyOf prov:used` with range `prov:Entity` (`dec.ttl:54-56`).
`etkl:IgnoredBand` is a bare `owl:Class` with no `rdfs:subClassOf` (`etkl.ttl:190`) and is **not** a
`prov:Entity`; its source region is (`iladub:SourceRegion ⊑ prov:Entity`, `iladub.ttl:70-72`), minted
by the carrier at `{doc}#ignored{idx}-source` (`holon.py:511, :520`). The evidence link targets the
region node. Nothing would refuse the triple either way — there is no `sh:closed` in the repo — which
is exactly why the declared range is the thing that decides it.

---

## File Structure

```
vocab/ontology/tab.ttl                        MODIFY  span-covering evidence terms (DECISION A)
vocab/queries/span-covers.rq                  NEW     the covering derivation (AXIOM, open world)
src/iladub/etkl/spangraph.py                  NEW     the evidence emitter + runner (PROCEDURAL glue)
src/iladub/etkl/donation.py                   MODIFY  clause (d), the spanning reading (DECISION C, D)
src/iladub/etkl/compile.py                    MODIFY  the seam at the hierarchical leg (Task 3)
examples/span-donation-conformant.ttl         NEW     the worked example that conforms
tests/span-donation-*-leak.ttl                NEW     two negatives that must fail
tests/test_vocab_shapes.py                    MODIFY  +1 conformant, +2 negative
tests/etkl/test_span_covers_query.py          NEW     the derivation, incl. DECISION B's falsifier
tests/etkl/test_span_donation_reading.py      NEW     the reading + the disposal
tests/etkl/test_span_donation_seam.py         NEW     the seam, the ledger, the decision record
src/iladub/feed.py                            MODIFY  the key split (Task 4)
src/iladub/ground.py                          MODIFY  the sibling flag's gate ONLY (DECISION E)
tests/test_feed_key_split.py                  NEW     the split, its negatives, the quarantine arm
src/iladub/propose_ground.py                  MODIFY  the threaded parameter (DECISION F)
baml_src/ground_propose.baml                  MODIFY  the optional page-context parameter
tests/test_propose_grounding_context.py       NEW     the slot is FILLED + the drift pin
examples/shipping/capacity-contract.ttl       NEW     the contract
examples/shipping/capacity-terms.ttl          NEW     the port scheme, borrowed from stem-terms
examples/shipping/capacity-shapes.ttl         NEW     the value constraint on capacity
tests/corpus-manifest.ttl                     MODIFY  cor:contract / cor:terms / cor:shapes
docs/wiki/concepts/neurosymbolic-exemplars.md MODIFY  one AXIOM entry
docs/superpowers/residues*.md                 MODIFY  R221; rows the executing loop raises
```

---

## Task 1: The span-covering vocabulary, evidence emitter, and derivation

**Files:** `vocab/ontology/tab.ttl`, `vocab/queries/span-covers.rq`, `src/iladub/etkl/spangraph.py`,
`examples/span-donation-conformant.ttl`, `tests/span-donation-*-leak.ttl`,
`tests/test_vocab_shapes.py`, `tests/etkl/test_span_covers_query.py`

**Interfaces:**
- Produces: an emitter taking the donor's boundary vector and the recipient's leaf grid and returning
  a fresh `Graph` (DECISION A — its own population, never merged into `tab:DonorBand`'s); a runner
  returning `{interval_index: tuple(column indices)}`, mirroring `headergraph.run_covers`.
- Consumes: `grid._rule_boundaries`, `cells.recover_leaf_grid`. Nothing else.

**What must stay true, and where it is pinned:**
- The query contains **no numeric literal** (Global Constraint 1), exactly as `header-covers.rq` does
  not. Containment is a comparison between emitted values.
- The emitter rounds to 2dp **by inheritance** from `sectiongraph._distinct_rule_xs`, and does not
  re-tune (`tab.ttl:355` records why `tab:donorBoundaryX` is not `tab:bandRuleX`).
- The covering must partition: every recipient column covered **exactly once** — no duplicate, no
  omission. On graincorp this is `1,1,2,2,2,2,2,2,2` (evidence § 3).

**MEASURE before writing** (plan rule 3): whether `tab:GridColumn` may be reused for the recipient's
columns or whether this population needs its own class. `tab:GridColumn` is already emitted by
`headergraph.header_evidence` into the `urn:iladub:header:` namespace and is documented as "never
asserted into a holon" — decide by reading both comments, and **record the decision and its reason in
the task report**, because `tab.ttl:336`'s population rule is what governs it.

- [ ] **Step 1: Write the failing tests.** Assertions this test module must make, at minimum:
  - the derivation returns a total, non-overlapping partition of the recipient's columns for a donor
    whose vector is a strict subset;
  - **DECISION B's falsifier**: a donor with a label whose ink center lies outside its own drawn
    interval yields **no** covering for that label, and the relation therefore refuses;
  - a donor vector that is **not** a subset yields no covering at all;
  - the tolerance is inert — the same input at `eps = 0` gives the identical map (evidence § 3).
- [ ] **Step 2: Implement to green.**
- [ ] **Step 3: The conformant example and two negatives**, wired into `tests/test_vocab_shapes.py`.

### FALSIFICATION — Task 1
Delete the containment filter from the query; the partition test must go RED. Restore; green.

---

## Task 2: The relation and the spanning reading

**Files:** `src/iladub/etkl/donation.py`, `tests/etkl/test_span_donation_reading.py`

**Interfaces:** a sibling of `offer` that returns the spanning reading or `None`. **`offer`'s own
signature and behaviour are unchanged** — equal-count donation keeps working exactly as shipped
(DECISION D).

**What must stay true:**
- Clause (e) reuses `donation.py:226`'s uniqueness rule; **no ordering rule is added**.
- The reading is DECISION C's `HierRegion`; **no level-1 nodes**.
- The disposal is `region_tiles`, unchanged, measured True (evidence § 3). **No new shape.**
- bfs p6's seven strict-subset pairs stay **refused by clause (c)**, as they are today (R211's row,
  and the grid-donation loop's census). This is the corpus negative and it must not move.

**MEASURE before writing:** `classify_hierarchical` returns `None` for a 1-line band at
`hierarchical.py:33`, and `header_rows_of` raises `IndexError` on one (evidence § 2's note). The
donor's header row therefore comes from `group_wrapped(donor_band, recipient_grid)`, not from the
`classify_hierarchical` path — confirm that on the fixture before writing the call.

- [ ] **Step 1: Write the failing tests** — the graincorp shape (corpus-gated), the two synthetics
  S1 (one extra drawn x in the donor ⇒ refused by (d)) and S2 (`drawn(D) = drawn(R)` ⇒ **not this
  arm's**, stays grid donation's), and DECISION B's refusal.
- [ ] **Step 2: Implement to green.**

### FALSIFICATION — Task 2
Delete clause (d); S1 must be admitted and its test go RED. Restore; green.

---

## Task 3: The seam, the ledger, and the document-scope membrane

**Files:** `src/iladub/etkl/compile.py`, `tests/etkl/test_span_donation_seam.py`

**Interfaces:** `compile_tables`' signature unchanged. The spanning offer is made where the band's own
reading would otherwise proceed, after the band's own `looks_transposed` / `looks_row_grouped` have
run — a band that would escalate under its own reading is not offered a donation (grid donation's
DECISION B, and the same rule here).

**What must stay true, and where it is pinned:**
- **The invariant, stated once above**: `("graincorp-capacity-2026-08-04", 0)` stays **406** in
  `tests/etkl/test_run_merge_seam.py:163`.
- The decision record is minted **only on acceptance**; a refused donation is invisible — no triple,
  no record, no report (`donation.py:28-29`).
- `graincorp-capacity` keeps compiling: `test_expected_verdict` requires, for `cor:Unadjudicated`,
  that compile return at all (evidence § 13). Its score may move and **no floor is pinned**.

**MEASURE before writing** (plan rule 3, and this closes evidence § 4's stated UNVERIFIED): whether a
**whole document** compile carrying a spanning donation conforms at document scope. The document-scope
TAB leg runs only when `recognized or section_facts` (`document.py:1162`), unlike page scope which
runs it whenever the page holds a table (`compile.py:1446-1450`). Run the full `compile_document` with
`validate_shapes=True` and read the report. If a shape refuses, it is undeclared rather than wrong —
report it and decide in this task, do not silently widen a shape.

- [ ] **Step 1: Write the failing tests.**
- [ ] **Step 2: Implement to green.**
- [ ] **Step 3: Re-run the invariant on the shipped seam**, not on the probe: the 7-document corpus
  battery, reporting every score and the per-page ledger.

### FALSIFICATION — Task 3
Remove the offer at the seam; the graincorp reading test must go RED while the ledger test stays
green — that separation is the proof the seam changed the reading and not the ink.

---

## Task 4: The key split in the feed

**Files:** `src/iladub/feed.py`, `tests/test_feed_key_split.py`

**Interfaces:** `table_records`' return type is unchanged — a list of `Record`. What changes is how
many records one row yields.

**The condition**, read off the compiled graph: a level-0 `tab:HeaderNode` covering **more than one**
leaf column and being the `tab:parentHeader` of **no** node. Note `holon.py:570`'s orphan promotion —
"level 0" in a compiled graph means *no parent*, not a syntactic level.

**What must stay true:**
- `Year` and `Elevation Period` each span one column, so they **do not** split and stay field names.
- The eight shipped multi-column level-0 nodes (apple 2, who 6) **all have children** and must stay
  unsplit; evidence § 8 measured the childless combination at **0 of 7 documents**, so before Layer A
  this condition fires on nothing at all.
- The coverage predicate is `tab:coversColumn`. **`tab:covers` is a decoy** (evidence § 8).

**MEASURE before writing:** the record id today is a `" > "`-joined string built by up to four
concatenations (evidence § 8's splice sites). Measure what `_record_uri` slugs it to for a split id
**before** choosing the separator, and confirm no collision with the existing multiplicity and
residual discriminators.

- [ ] **Step 1: Write the failing tests** — one record per spanning childless parent; non-covered
  columns copied into each record; the two negatives above.
- [ ] **Step 2: Implement to green.**

### FALSIFICATION — Task 4
Delete *covers more than one*; `Year` must become a key and its test go RED. Restore; green.

---

## Task 5: The oracle — one oracle, two populations

**Files:** `src/iladub/ground.py` (the gate at `:113` **only**), `src/iladub/feed.py`,
`tests/test_feed_key_split.py`

**What must stay true:**
- `marker_field`'s **body is untouched** — only its gate admits the second population (DECISION E).
- `tests/test_corpus_stem.py:263` stays green **and keeps its meaning**: no record carries a
  furniture-sourced `is_section_marker` concept.
- A key no scheme admits, or one several admit, is **quarantined** and the records stay split.

### FALSIFICATION — Task 5
Revert the gate to the single flag; the split keys must quarantine and the grounding test go RED.

---

## Task 6: The proposer is handed the page

**Files:** `baml_src/ground_propose.baml`, `src/iladub/propose_ground.py`, `src/iladub/ground.py`,
`src/iladub/feed.py`, `tests/test_propose_grounding_context.py`

**What must stay true:**
- The threaded parameter is **defaulted**, so all 24 test call sites keep working (DECISION F).
- **The slot is filled, and a test proves it** — for a real compiled document the page context reaching
  `ProposeGrounding` contains the title and footer text the carrier put in the graph. Evidence § 10 is
  why this assertion exists rather than being assumed.
- The furniture is read from `etkl:IgnoredBand` / `etkl:bandText` on the document-scope graph, which
  `ground_document` is already handed (measured: the nodes survive `compile_document`, and nothing on
  the grounding path reads them today).
- A drift pin for `ProposeGrounding` on the model of `tests/etkl/test_rowrole_proposer.py:37-89`,
  including its **skip-not-fail** behaviour when `baml_client` is absent.

### FALSIFICATION — Task 6
Hard-code the context to `None`, as `reshape.py:207` does for `table_title`; the slot-is-filled test
must go RED. That is the exact failure this task exists to prevent.

---

## Task 7: The capacity contract

**Files:** `examples/shipping/capacity-{contract,terms,shapes}.ttl`, `tests/corpus-manifest.ttl`

**What must stay true:**
- Fields `year`, `elevationPeriod`, `port` (scheme-bound) and `capacity`. **There is no field for the
  flag** — `Y`/`N` fails the value constraint and quarantines, which is the ruling's second half and
  falls out of the membrane with no special case (spec § 3.3).
- The port scheme's `skos:prefLabel`s match the page's seven labels **exactly**; `scheme_member` is
  exact string equality, not normalised.
- `capacity`'s pattern is `ship:total`'s, `^[0-9]{1,3}(,[0-9]{3})*$`. Measured against the page: it
  admits `10,000` / `12,500` / `14,000` and refuses `Available`, `On Application`, `Y`, `N` — **and it
  admits bare `0`**, which is [[R213]]'s invisible-glyph hazard. Under the abstaining battery proposer
  no leaf grounds at all, so the hazard is not live in CI; **say so in the task report rather than
  leaving it implicit.**
- The contract may carry a provenance triple naming the furniture node the measure's name was derived
  from (DECISION G); `load_contract` ignores it, measured (evidence § 12).

**This is where P2 is decided** (handoff § 5b): adding the three manifest triples puts graincorp under
`test_grounding_where_contracted` for the first time, which ends `assert grounded, "a contracted
document must ground SOMETHING"`. **Run that probe as soon as Task 4 mints its first record — do not
wait for this task.** If nothing grounds, report it; **do not swap in a live proposer to make the gate
green** (spec § 3.3's last bullet).

---

## Task 8: The register, the wiki, the suite, the PR

- [ ] R221 is already raised by the loop that wrote this plan. Raise the rows this loop's own findings
  earn, **recomputing the tally rather than copying it**.
- [ ] One AXIOM entry in `docs/wiki/concepts/neurosymbolic-exemplars.md` — the drawn-interval covering,
  with its inert tolerance stated as the reason it is AXIOM and not a tuned heuristic. The wiki figure
  gate is HARD: any decimal figure needs a date in its own block.
- [ ] The full suite, in-band, in ~8-file chunks, each to its own log (Global Constraint 6).
- [ ] Re-baseline the two population gates as a **set** (Global Constraint 7).

---

## Self-review against the spec

- § 3.1's relation: clauses (a)–(e) — Task 2, DECISION D. **Its reuse assumption is refuted and
  replaced** — DECISION A, evidence § 2.
- § 3.1's two named seams: both measured — evidence § 5 (`region_round_trips` sees the recipient and
  is vacuous at `body_line = 0`) and § 6 (`_book_recovered_ink` books the donor nowhere).
- § 3.1's prediction (9 nodes over 16 leaves, no numeric label cell): measured, evidence § 3.
- § 3.2's condition and its negatives: Task 4. Its census of 0 is confirmed and strengthened — the
  childless combination is novel corpus-wide, 0 of 8 (evidence § 8).
- § 3.3's measures, and § 0's ruling that the machine derives the name: Tasks 6 and 7.
- § 3.4's year: **not repaired**, [[R215]], the maintainer's call at etkl:02's read.
- § 4's scope boundaries: bfs p6 stays refused; the battery's proposer is unchanged; no `tab:covers`
  reuse; no level-1 node invented.
