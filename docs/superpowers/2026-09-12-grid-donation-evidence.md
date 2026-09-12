# Grid donation — R201 + R203 closed: the datagrid derives the donor's header

**Serves:** prog:criterion:etkl:05 — `gov-stats/bfs-population-bilan-2023.pdf`
(`tests/arc-manifest.ttl:243`). Not etkl:02, which the previous three loops served and which this
loop does not touch.
**Date:** 2026-09-12. **Branch:** `grid-donation`, cut from `0ca29b0`.
**Plan:** `docs/superpowers/plans/2026-09-11-grid-donation.md`, executed as written.
**Spec:** `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md`.

**Doc impact: increment.** `tests/corpus-manifest.ttl` gains one `cor:reading` on the bfs entry
(append-only); `docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM section, three cited
code sources and an `updated:` bump; five `tab:` terms are declared. No released assertion changes —
**no contradiction**, so nothing blocks a release tag.

> The plan names this file `2026-09-11-grid-donation-evidence.md`. It is dated **2026-09-12**, the
> day the loop ran; the new `cor:reading`'s `cor:recordedIn` points at this filename.

Part 5 was written first.

## 5. The next concrete action

### 5a. ASSERTED: the etkl:02 spec's § 5 step 2 is now the gate — R212's carrier, then the proposer path

A consequence, not a discovery. At review on 2026-09-12 the maintainer **refuted** the reading that
`specs/2026-09-11-the-span-the-author-drew-design.md` was drafted on: the **machine**, not the
contract author, derives the capacity measure's name from the page's title and footer. That is
recorded in that spec's § 0, § 3.3, § 5 and § 6, and in [[R212]]'s row (PR #209, `f1df625`), and it
promotes R212 from a deferred §5 loss to a **prerequisite**: the licence has no carrier in the graph
(0 hits in 5710 triples) and the proposer is called with `surface_text = ""`.

Mechanical only in the sense that it is *named*. It still needs a spec, because "which ignored bands
carry text, and what provenanced carrier do their lines get" is a design question with a corpus
census in front of it.

### 5b. PROPOSED: spanning donation (Layer A) reuses this loop's three artifacts with one clause swapped — RUN THE PREDICTION FIRST

Layer A is this loop's relation with **(d) `drawn(D) ⊊ drawn(R)`** replacing `same_ncols`, and no
level-1 header nodes. The emitter, the query and the seam shipped here are what it would extend.
**That is a prediction, not a plan.** The spec's § 3.1 names what must be measured before any task
is written:

1. graincorp p0 under Layer A: 27 data rows, 9 level-0 nodes over 16 leaf columns, no numeric label.
2. Which band does `region_round_trips` see, and where does `_book_recovered_ink` book the donor's
   labels? `D` is `ignored` today and contributes no ink.

**Refuted in minutes if the donor's ink cannot be conserved**, and Layer A then needs its own design
pass. Do not write tasks against this until it has been run.

### 5c. What this loop deliberately leaves exposed

[[R216]] and [[R217]]. Neither blocks a merge; both exist because the loop's corpus evidence is
one-sided — the disposal has no *corpus* refusal, and the R203 licence is exercised on one donor.

## 1. Where the primaries are

| what | where |
| --- | --- |
| the derivation (AXIOM) | `vocab/queries/grid-donation.rq` |
| the evidence emitter | `sectiongraph.donor_evidence` |
| the reading, the licence carrier, the disposal | `src/iladub/etkl/donation.py` |
| the seam | `src/iladub/etkl/compile.py`, the RECORD_TABLE assert leg |
| the five terms | `vocab/ontology/tab.ttl` |
| the pins | `tests/etkl/test_{donor_evidence,grid_donation_query,grid_donation_disposal,grid_donation_seam}.py` |
| the census instrument | `scripts/grid_donation_design_census.py` |

## 2. What was measured

**The headline.** bfs p6 reads **222 → 267 entries**, every donated table labelled by band 2's drawn
header and carrying `tab:headerDonatedBy`. Confirmed under `validate_shapes=True` as well as with
validation off.

**The ledger did not move.** `(asserted, escalated) == (276, 25)`; per-band tokens 36/54/36/72/63
unchanged. DECISION D's prediction, run rather than asserted.

**The whole corpus.** Six of seven documents **byte-identical**. bfs differs in 27 diff lines and
nowhere else:

```
26,27c26,27   graph_sha256 08de89c867f6… -> de1d1073efb7… ; graph_triples 8249 -> 8919
521c521  "cells": 27 -> 36        553c553  "cells": 63 -> 72
529c529  "cells": 45 -> 54        561c561  "cells": 54 -> 63
537c537  "cells": 27 -> 36
```

Five `cells` bumps of exactly +9 (+45 = 222 → 267) on the five bands the seam tests name, and +670
triples for the donated header nodes, label cells and provenance links. No verdict changed, no
reason changed, `adopted` is `[]` both sides. Step 1's contract — *"a difference anywhere else is a
finding"* — is met with **zero findings**.

**The re-baseline list is empty.** 63 passed / 2 skipped across the six corpus-gated modules
(`test_decision_queries`, `test_decisionlog`, `test_typing_equiv`, `test_membrane_health`,
`test_adoption_document`, `test_document_membrane_gate`). The plan warned that minting a decision
record shifts later `-d{n}` numbering on that band; **no pin reads those URIs**, so nothing moved.
The loop's entire numeric footprint is one re-baselined entry count in `test_run_merge_seam`.

**The wall clock — call counts first, seconds second**, per the instrument's own docstring, one
reading per tree:

```
                              BEFORE (0ca29b0)     AFTER (b2bdbbe)
page_bands calls / doc        3 2 6 6 16 18 6      3 2 6 6 16 18 6     IDENTICAL
TOTAL wall                       332.62s              343.29s          +10.67s
TOTAL page_bands                  75.53s               78.18s          + 2.65s
bfs alone                         24.06s               26.69s          + 2.63s
graincorp-capacity                11.71s               15.51s          + 3.80s  <- noise
```

**The call counts are identical per document** — the structural, noise-free figure — so donation
introduces no new `page_bands` call anywhere. The seconds must not be over-read, and this run
supplies its own proof of why: graincorp-capacity is **+32% on a document whose compiled graph is
byte-identical before and after**, so it cannot have been slowed by this change, and it alone
accounts for +3.80s of the +10.67s. The only delta attributable to the loop is bfs's **+2.63s** —
the one page that derives a datagrid and disposes five donations. Against M1's bound,
`derive_data_grid` costs 4.6s over all 27 corpus pages and is now called only on a page carrying a
donor-vector band. **No cache was built** — [[R168]] and R172 are the rows that say why.

## 3. The document score did not move, and that is the honest headline

bfs reads **0.40331491712707185 before and after**. Forty-five more cells are asserted, under the
author's real labels instead of a regional subtotal row, and the score is unchanged — because the
score is **token**-based and those tokens were already counted as asserted data. What changed is
*which labels they hang under*, which the score cannot see.

That is not buried: it is exactly the case [[R198]] names — *"append it anyway: the register is a
refresh log, and an unchanged figure under a changed reading is the fact worth dating."* The new
`cor:reading` is appended for that stated reason.

## 4. Unverified, assumed, or one-sided

- [[R216]]: `donation_admissible` refuses only on a **synthetic** page. M3 measured 5 structural
  pairs and 5 acceptances, so the corpus exercises the disposal in the accepting direction only.
- [[R217]]: the R203 licence is exercised on **one** donor corpus-wide, and a page TITLE as a
  donor's line 0 is a case the forward direction cannot separate — bfs p5/p6 titles are refused
  `every-measure` exactly as headers are.
- [[R166]]'s six donor-less bands are untouched (apple p2 band 6, who p0/p1 band 4, cbh p0 band 9,
  graincorp p0 band 3, bfs p5 band 13). `test_a_headerless_band_asserts_its_first_data_row_as_the_column_header`
  is still green and still describes that shape — **measured, not inferred**: its module contains no
  `.line(` / `setLineWidth` / `Rule(` at all, so no band there owns a boundary vector, no donor node
  is emitted, and donation cannot fire on it.
- [[R205]]: bfs p6 bands 3 and 7 remain `ignored` at 0 cells after donation.

## 6. Four plan defects, found by running rather than reading

Each was reported and substituted with a form carrying the same force; none was worked around
silently, and none was in an implementer's work.

1. **Task 1 arm (b) is inert.** "Round the boundary at 3dp" cannot fail: `_rule_boundaries` already
   rounds its rule-derived branch to 2dp (`grid.py:74`), so the emitter's rounding is load-bearing
   only for the `column_xs` branch, which no fixture exercises unrounded. Substitute: mint
   `tab:bandRuleX` from the raw rule x — `bounds == rules` then dies on `Literal('72.004')`.
2. **Task 2 Step 4's prediction is refuted.** The two query gates do not "pick up the new file
   automatically": the population is globbed but the **count is pinned**. Re-baselined 51 → 52 in
   both, each saying what its own number means.
3. **Task 4 arm (b) is unsatisfiable as phrased.** `offer` returns `None` identically whether the
   membrane refused or the derivation was suppressed, so a record on every `None` appears in both
   arms of the isomorphism comparison and they stay isomorphic. Substitute: record a refusal *that
   followed a named donor*.
4. **Task 5 Step 5's arm is inert.** `cor:ReadingShape` requires **at least one of**
   `cor:atCommit` / `cor:recordedIn`, so removing `cor:atCommit` alone leaves the disjunction
   satisfied. Substitutes: the `cor:readAt` `sh:minCount 1` arm (which bites alone) and the
   both-properties arm.

Also caught before writing: the plan's new register rows **R209/R210 collide** with live rows — the
plan predates three loops — and ship as **R216/R217**.

## 7. Falsification evidence

Every task's arms, with the outputs, are in `## FALSIFICATION` form below.

**Task 1** — (a) deleting the emitter's abstain fails `test_a_band_with_no_vector_emits_no_node_at_all`
*and* `test_band_index_is_the_position_in_the_passed_list` (two tests pin it, not one); (b) inert, see
§ 6; (b′) minting `tab:bandRuleX` from the raw rule x fails the 2dp test with
`Extra items in the right set: Literal('72.004')`. Restored, 5 passed, file IDENTICAL to backup.

**Task 2** — (a) deleting the drawn clause admits the inferred-gutter donor (`Left contains one more
item: 0`); (b) deleting the `tab:headLineRefusal` pattern admits an unlicensed donor; (c) deleting
the term's declaration fails the declaration membrane by IRI: *"urn:iladub:query:vocab/queries/grid-donation.rq
names https://w3id.org/iladub/tab#headLineRefusal, which no owned ontology declares"*. Restored, 23
passed, both files IDENTICAL.

**Task 3** — (a) dropping the round-trip conjunct fails the straddling test, so the conjunct is
load-bearing and stays (the plan required deleting it as dead code had it stayed green); (b)
accepting the first donor instead of requiring exactly one fails the uniqueness test; (c) not
shifting the rows fails the donated-region test. Restored, 16 passed, IDENTICAL.

**Task 4** — (a) skipping the `headerDonatedBy` triple fails the 267 test on its provenance
assertion; (b) recording a refusal that followed a named donor breaks the isomorphism; (c) emitting
the link and decision without taking `donated.region` fails the headerless test (`cells=9`).
Restored, 5 synthetic pins green, IDENTICAL.

**Task 5** — three arms against `tests/test_corpus_manifest.py`, the module that applies
`tests/corpus-shapes.ttl`.

**(a) THE PLAN'S ARM, and it is INERT — predicted before running, then confirmed.** Step 5 says
*"remove the appended `cor:atCommit` from the new node and show the manifest membrane failing"*:

```
########## ARM (a): remove cor:atCommit alone. EXPECT still green => INERT
10 passed in 0.91s
```

`cor:ReadingShape` pins a **disjunction** — `FILTER(NOT EXISTS {…atCommit…} && NOT EXISTS
{…recordedIn…})` — and Step 4 requires the node to carry `cor:recordedIn` as well, so deleting one
of the two leaves the constraint satisfied. The plan names one input to a rule that needs both
removed to bite. Two substitutes carry the force the shape actually states:

**(b) Remove `cor:readAt` — the single-property arm the plan did not name, which bites alone:**

```
E  Constraint Violation in MinCountConstraintComponent:
E    Source Shape: [ sh:datatype xsd:date ; sh:minCount Literal("1") ; sh:path cor:readAt ]
E    Message: Less than 1 values on [ cor:atCommit Literal("b2bdbbe") ; cor:recordedIn
E             Literal("docs/superpowers/2026-09-12-grid-donation-evidence.md") ; cor:value
E             Literal("0.40331491712707185", datatype=xsd:decimal) ; rdf:type cor:Reading ]->cor:readAt
FAILED tests/test_corpus_manifest.py::test_manifest_conforms
1 failed, 9 passed in 1.01s
```

**(c) Remove BOTH provenance properties — the disjunction arm:**

```
E  Message: a reading must carry at least one of cor:atCommit / cor:recordedIn —
E           an untraceable number is not evidence
FAILED tests/test_corpus_manifest.py::test_manifest_conforms
1 failed, 9 passed in 1.05s
```

**Restored, IDENTICAL to backup, 10 passed.**

A process note worth keeping, because it is the failure mode this repo names *phantom green*: the
first attempt at these arms ran `tests/test_corpus.py` under `-k "shape or manifest or membrane or
reading"`, which **deselected all 10 tests** and produced three green-looking results that asserted
nothing — while the discovery step in the same script had already printed
`tests/test_corpus_manifest.py` as the module applying the shapes. Green from an empty selection is
not evidence, and the arms above are the re-run against the correct module.

## 8. Measurements the loop rests on

- The design census reproduces: same 5 ACCEPTs with entry counts 36/54/36/72/63, `donor-vector
  bands: 7; line0 identity unique=7 multi=0 none=0`, `structural pairs 5; accepted by disposal: 5`.
- The declaration membrane requires only that a term be **declared** (`FILTER NOT EXISTS { ?term ?p
  ?o }`), not that it carry `rdfs:domain`/`range`; all five carry both anyway.
- rdflib 7.6.0 binds `initBindings` on a variable appearing **only inside a FILTER**, with a null
  control showing a non-matching binding returns nothing rather than being ignored — so no `VALUES`
  fallback was needed.
- `derive_data_grid` returns a grid on the synthetic fixture and refuses its head line
  `every-measure`, so the plan's reserved monkeypatch was **deleted** in both tests that carried it
  and the real refusal map carries the licence end to end.
- The disposal's placeholder doc URI is inert **for this chain**, re-measured rather than inherited:
  one distinct verdict vector across three unrelated doc URIs.
- `tab:headerDonatedBy` survives the document membrane: no authored shape in `vocab/shapes` closes
  any class, and bfs p6 compiles clean under `validate_shapes=True` at 267 entries.
