# Evidence — the ignored band carries its text (R212 closed)

**Serves:** prog:criterion:etkl:02 — R212 is a **prerequisite** of that criterion's measures,
ruled 2026-09-12; it is not a criterion of its own.
**Date:** 2026-09-12. **Branch:** `r212-the-ignored-band-carries`, cut from `main` at `eb74caa`.
**Plan:** `docs/superpowers/plans/2026-09-12-the-ignored-band-carries-its-text.md`.
**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.

**Doc impact: increment.** Four new `etkl:` terms in `vocab/ontology/etkl.ttl` and one NodeShape in
`vocab/shapes/etkl-shapes.ttl` (both CC-BY, published artifacts), plus one PROCEDURAL entry in
`docs/wiki/concepts/neurosymbolic-exemplars.md`. No released assertion is contradicted, so nothing
blocks a release tag.

Every number below was run in this session unless it names an earlier one.

## 1. The five decisions, as executed

| decision | outcome |
| --- | --- |
| A — the terms | `etkl:IgnoredBand`, `etkl:bandText`, `etkl:bandIndex`, `etkl:ignoredBecause` |
| B — is the classifier's reason total? | **MEASURED TOTAL** (§ 2) → `sh:minCount 1` in the shape |
| C — the subject | `{doc}#ignored{idx}`, disjoint from `{doc}#region{idx}`; falsified separately (§ 5) |
| D — the membrane | NOT wired; enforced by a test on a real compiled graph. Focus-node census in § 6 |
| E — `band_text`'s home | moved to `bands.py`, public; four references followed it |

## 2. DECISION B — the reason is TOTAL, by enumeration

The plan required an enumeration of every `NON_TABLE` return site in `src/iladub/etkl/regions.py`,
not an assumption.

```
$ grep -rn "ClassifiedRegion(" src/
src/iladub/etkl/regions.py:110:    return ClassifiedRegion(kind, band, grid, cells, reason)
src/iladub/etkl/donation.py:165:    return ClassifiedRegion(RegionKind.RECORD_TABLE, bands[idx], grid, head + body, "donated")
```

Two construction sites in `src/`, and only `regions.py:110` can produce a `NON_TABLE`. Its `reason`
comes from `_reason` (`regions.py:88-98`), whose NON_TABLE arm is a total expression over two
non-empty strings:

```python
if kind is RegionKind.NON_TABLE:
    return "fewer than 2 lines" if len(band.lines) < 2 else "fewer than 2 columns"
```

`ClassifiedRegion.reason` is declared `reason: str` with **no default** (`regions.py:55`), so no
construction can omit it. → the reason is total, and `etkl:ignoredBecause` is **required** in
`etkl:IgnoredBandShape`. No placeholder reason was invented (§7).

**Term-collision check (DECISION A, required before writing).** `grep` over `vocab/`, `src/`,
`tests/`, `examples/` for `bandText|bandIndex|IgnoredBand|ignoredBecause`: no collision for three of
the four names. `tab:bandIndex` **does** exist (`vocab/ontology/tab.ttl:339`, `rdfs:domain
tab:PageBand`) — a different property, in a different namespace, on a different class, carrying the
same fact for the transient intra-page evidence population. `etkl:bandIndex`'s `rdfs:comment` says so
explicitly, so a reader is not left to wonder which one they are holding.

## 3. Task 1 — the vocabulary, the shape, the examples

RED first, and the failure read rather than assumed: with the examples written but no terms and no
shape, both negatives failed on their **assertion** (`set()` — no violation fired at all), not on a
parse error. The conformant case passed **vacuously**, which is the expected shape of a RED state
for a positive: with no shape targeting the class, everything conforms.

```
2 failed, 1 passed, 8 deselected
```

After the terms and the shape: `14 passed` for the whole of `tests/test_vocab_shapes.py` (the new
shape shares its file with `DocumentProjectionShape` and `MembraneHealthShape`, so the file was run
whole, not only the new cases), and `tests/test_source_ownership.py` green alongside it.
`tests/test_artifact_terms.py`, `test_artifact_declarations.py`, `test_query_declarations.py`,
`test_query_terms.py` and `test_doc_governance.py` — the vocabulary-surface membrane the four new
terms have to pass — ran green too: `43 passed`.

**One deviation from the plan's letter, and why.** The plan said to register the three examples
"following the existing `_validate(...)` idiom". The two **negatives** use a new `_messages(...)`
helper instead. The reason is the hazard `_violations`' own docstring records one case further down
the same file: the page requirement is a **sequence path** (`iladub:fromRegion / iladub:onPage`),
which pySHACL reports as a blank-node list in `sh:resultPath` — nothing a test can spell. Without
pinning *which* constraint fired, both negatives would read as "a MinCount violation at the same
focus node" and neither would pin its own subject. A `sh:message` is authored per property shape, so
it names the constraint as precisely as a path would. The conformant case uses `_validate` unchanged.

**Second deviation.** The four terms are declared as a self-contained section at the **end** of
`etkl.ttl` rather than immediately after the core-classes block. The file's own recent convention
(`etkl:readerScope`, `etkl:QueryArtifact`/`etkl:VocabularyArtifact`) is a titled section keeping a
class and its properties together; the plan's placement would have split the class from its three
properties across two distant blocks.

### FALSIFICATION — Task 1

| arm | removed | result |
| --- | --- | --- |
| text | `sh:minCount 1` on `etkl:bandText` | `ignored-band-textless-leak.ttl` **passes validation**; the negative test fails (`set()`) |
| page | `sh:minCount 1` on the `( iladub:fromRegion iladub:onPage )` sequence path | `ignored-band-pageless-leak.ttl` **passes validation**; that negative fails |

Restored after each: `11 passed`.

## 4. Task 2 — the RED state, reproduced on the shipped fixture

The plan's fixture (`reportlab`: a one-line title, a ruled 3-column table, a one-line footer) bands
**exactly** as evidence § 3 measured independently, including the triple count:

```
bands: 3
  b0 lines=1 NON_TABLE [fewer than 2 lines]    'ELEVATION CAPACITY TABLE'
  b1 lines=5 RECORD_TABLE [flat single-level header] 'Year Period Mackay | 2026 Jan-Mar 845870 | …'
  b2 lines=1 NON_TABLE [fewer than 2 lines]    'GrainCorp advise that the tonnages shown are indicative only.'
triples: 420  score: 1.0
  probe 'ELEVATION CAPACITY TABLE'             hits=0
  probe 'GrainCorp advise that the tonnages'   hits=0
  probe 'ELEVATION'                            hits=0
  probe 'indicative'                           hits=0
  probe 'tonnages'                             hits=0
```

**Assertion 5's fixture is constructible through the real pipeline**, which the plan left to the
implementer to find. `absorb_unit_markers` runs at `compile.py:394`, i.e. over the band list
**before** `compile_tables` enumerates it, so a band reaching the NON_TABLE branch has already been
through absorption. A borderless two-line `$ 845870 / $ 365844` block therefore yields one band that
is *both* ignored and marker-carrying — the only shape of band on which DECISION C's two subjects
could collide:

```
b0 lines=2 NON_TABLE [fewer than 2 columns] markers=(('$', 142.7, (…)),) '845870 | 365844'
```

`band_text`'s move (DECISION E) is behaviour-neutral: `tests/etkl/test_document.py` **15 passed**,
`tests/etkl/test_continuation_licence.py` **14 passed**, and `grep -rn "_band_text" src/ tests/`
returns no reference (its only hit is the substring inside this loop's own test *name*). All four
references followed the move, the two prose mentions included.

### FALSIFICATION — Task 2

**Arm (a), the emitter's call deleted from the NON_TABLE branch:**

```
FAILED test_ignored_bands_carry_their_exact_text
FAILED test_carried_bands_keep_their_band_index
FAILED test_the_record_table_band_mints_no_carried_node
FAILED test_the_carrier_and_the_unit_marker_hanger_are_disjoint
4 failed, 1 passed
```

The one pass is `test_the_fixture_bands_as_measured`, which asserts the *banding*, not carriage —
correct, and the reason it is a separate test.

**A defect this falsification caught in the plan's own assertion 4, and the fix.** As first written,
assertion 4 was `1 not in carried` — the plan's wording. That passes **vacuously** on a graph with no
carried bands at all, so with the emitter deleted it stayed green while pinning nothing: CLAUDE.md
§ Plan authoring defect 5, in assertion form. The test now pins the population non-empty first
(`len(carried) == 2`) and *then* excludes band 1, and it is in the failing list above because of
that change. This is recorded rather than quietly fixed, because the falsification arm is the only
thing that could have found it.

**Arm (b), the emitter pointed at `{doc}#region{idx}` (DECISION C):**

```
FAILED test_the_carrier_and_the_unit_marker_hanger_are_disjoint
1 failed, 4 passed
```

Exactly one test fails, and it is the disjointness one — which is the point: it proves DECISION C is
pinned by an assertion of its own, and that the other four do not depend on the subject choice. An
arm that only removed the call would not have tested DECISION C at all.

Restored after both arms: `6 passed`, `git diff --stat` back to the shipped diff.

## 5. Task 3 — the membrane, on a real compiled graph

Per DECISION D the shape is wired into no membrane set, so the test **is** the enforcement. A real
compiled page graph validated against the whole of `vocab/shapes/etkl-shapes.ttl` with
`inference="rdfs", advanced=True` **conforms**.

**Step 2 — the vacuity registry, run in full and not skipped.** DECISION D predicted that not wiring
the shape leaves `tests/etkl/test_vacuity_registry.py` untouched: its forward arm enumerates *wired*
shapes only, and its reverse arm (`:352`) *forbids* a registry row for an unwired one. Both hold.

```
$ PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_vacuity_registry.py -q
9 passed in 408.32s (0:06:48)
```

The run time is the evidence that it ran: that file is corpus-marked, the corpus is present in this
checkout, and it compiled all seven documents rather than skipping green (plan Global Constraint 5).
No registry row was added, and none was needed.

### 6. The focus-node census DECISION D required

The seam the plan named: validating a compiled graph against the whole file also loads
`DocumentProjectionShape` and `MembraneHealthShape`, and *expected* is not *measured*.

```
compiled page graph: 438 triples

focus nodes per NodeShape in etkl-shapes.ttl (sh:targetClass):
  DocumentProjectionShape      targetClass=DocumentProjection         focus=0
  ExtractionShape              targetClass=Extraction                 focus=0
  FieldShape                   targetClass=Field                      focus=0
  IgnoredBandShape             targetClass=IgnoredBand                focus=2
  MembraneHealthShape          targetClass=CompiledDocumentHolon      focus=0
  SemanticDataContractShape    targetClass=SemanticDataContract       focus=0
  SourceDocumentShape          targetClass=SourceDocument             focus=0
  TransformationShape          targetClass=Transformation             focus=0

conforms: True
```

`etkl:IgnoredBandShape` is the only shape with focus nodes, and the census is pinned as a test rather
than left in this document.

**This CONFIRMS the previous handoff's § 5b prediction** — *"a compiled PAGE graph carries no `etkl:`
triple today, so the carrier's node will be the first"* — which was reasoned from a grep over
`compile.py` and is now measured against a compiled graph. The prediction was scoped to **page**
graphs, and that scoping holds: at document scope `MembraneHealthShape` would fire, because
`document.py` does mint `etkl:` terms. The test says so in its docstring so a later document-scope
reader does not misread it as a defect.

**What is NOT confirmed, and must not be reported as such.** The handoff *before* last predicted
that *a wired carrier shape costs zero vacuity-registry rows*. This loop declines the wiring arm, so
that prediction is **untested by design** — not confirmed. `tests/etkl/test_vacuity_registry.py`'s
reverse arm (`:352`) *forbids* a registry row for an unwired shape, so the correct outcome here is
that the registry is untouched.

## 7. The corpus arm — R212's actual subject, and what closes the row

Not in CI, and a green CI is not evidence for it (spec § 5 arm 5). Run locally on the shipped
emitter, with the same instrument the row's original measurement used — `compile_document(...).graph`
searched for literal substrings:

```
$ PYTHONPATH=src .venv/bin/python  … compile_document("corpus/ag-trade/graincorp-capacity-2026-08-04.pdf")
triples: 5746   score: 1.0

--- literal-substring search over every object (the row's original probe) ---
  'ELEVATION'                hits=1
  'CAPACITY TABLE'           hits=1
  'tonnages'                 hits=1
  'indicative'               hits=1
  'GrainCorp Operations'     hits=1
  'As At'                    hits=1

--- every etkl:IgnoredBand carried, verbatim ---
  p0 b0 [fewer than 2 lines]   'GrainCorp Operations Ltd ABN 52003875401'
  p0 b1 [fewer than 2 columns] 'ELEVATION CAPACITY TABLE\nAs At Tuesday, 4 August 2026'
  p0 b2 [fewer than 2 lines]   'Year Elevation Period Mackay Gladstone Fisherman Islands Carrington Port Kembla Geelong Portland'
  p0 b4 [fewer than 2 lines]   'GrainCorp advise that the tonnages shown are indicative only and are subject to change. 1'

carried ignored bands: 4
```

Every probe the row measured at **0 hits in 5710 triples** now hits, and the four bands spec § 2.2
listed verbatim are the four bands carried — b0, b1, b2 and b4, in that index space, with the
classifier's own reason on each. The document is 5746 triples, **+36 on 5710**, which is 4 bands ×
9 triples: the emitter is live and uniform.

b2 is the page's real header, carried as text and still ignored — spec § 4's first line, held: this
loop does not make any ignored band a header, and [[R166]]/[[R211]] Layer A is untouched.

## 8. The invariant arm — carriage moves no number that grades a document

Evidence § 1 confirmed this on a **throwaway** emitter. This is the **shipped** one. Two readings of
all seven documents with `scripts/corpus_verdict_snapshot.py`: one in a worktree at the branch point
(`eb74caa`), one in this tree, then diffed on per-document score, per-page `(asserted, escalated)`,
**every** per-region verdict (kind, reason, verdict, cells, anchor, table), the document-level
decisions (`recognized`, `chains`, `refused_licences`, `repaired_bands`, `adopted`, `notes`) and the
canonical graph hash.

```
document                                  score  ledger  verdicts  doclvl   hash  ignored  Δtriples  Δ/band
------------------------------------------------------------------------------------------------------------
apple-fy2026q3-statements                  SAME    SAME      SAME    SAME  MOVED        6        54    9.00
bfs-population-bilan-2023                  SAME    SAME      SAME    SAME  MOVED       46       414    9.00
cbh-stem-2026-08-03                        SAME    SAME      SAME    SAME  MOVED        5        45    9.00
graincorp-capacity-2026-08-04              SAME    SAME      SAME    SAME  MOVED        4        36    9.00
graincorp-stem-2026-07-31                  SAME    SAME      SAME    SAME  MOVED        7        63    9.00
ons-index-of-services-2026-02              SAME    SAME      SAME    SAME  MOVED       70       630    9.00
who-wfa-boys-zscore-0-5                    SAME    SAME      SAME    SAME  MOVED        8        72    9.00
------------------------------------------------------------------------------------------------------------
scores SAME:    7/7      ledgers SAME:   7/7      verdicts SAME:  7/7
doc-level SAME: 7/7      hashes MOVED:   7/7

total ignored bands: 146   total Δtriples: 1314
triples per ignored band: [9.0]  -> UNIFORM

VERDICT: the invariant HOLDS on the shipped emitter
```

**Step 4's stop-gate is not triggered: no score moved.** Nothing was adjusted to make this pass, and
no pinned floor was touched.

**Step 2 — the delta is a uniform constant, and it is a DIFFERENT constant from the throwaway's.**
The throwaway emitter wrote 3 triples per band; the shipped one writes **9** (type, text, index,
reason, `iladub:fromRegion`, `prov:wasDerivedFrom`, then the region's type, page and
`prov:wasDerivedFrom`), which is DECISION A + B + C costed out. It is 9.00 on every one of the seven
documents — a non-uniform figure would have meant the emitter was conditional somewhere it should
not be, and it is not.

**The instrument could have lied by not running, and did not.** An unmoved hash from a silently
no-op emitter reads as a refutation when it is an instrument failure (evidence § 1 records the
hazard), so the diff prints the delta and the carried-band count *before* the SAME columns and exits
non-zero on a zero delta. The delta is 1314 triples and every hash moved, so the emitter is
demonstrably live on the corpus pass whose scores are reported unchanged.

**The 146 reproduces spec § 2.1's census independently.** That census was taken by a separate
instrument (`scratchpad/ignored_band_census.py`, replicating `compile_tables`' band ordering by
reading); this count comes from the shipped emitter's own output, per document, and agrees on the
total **and** on all seven per-document figures — ons 70, bfs 46, who-wfa 8, graincorp-stem 7,
apple 6, cbh 5, graincorp-capacity 4. Spec § 6 flagged the census's band-ordering replication as
"replicated by reading, not proven equal"; this is the proof it was owed.

### FALSIFICATION — Task 3

The membrane arm proves the shape reaches real products, not only the hand-written example. The
emitter was made to drop `etkl:bandText` on band 0 only — a *partial* defect, not a total absence:

```
Source Shape: [ sh:datatype xsd:string ; sh:message Literal("An ignored band must carry the band's
              exact surface text — that text is the whole reason the node exists.") ;
              sh:minCount Literal("1", datatype=xsd:integer) ; sh:path etkl:bandText ]
Focus Node:   <https://example.org/etkl/doc#ignored0>
Result Path:  etkl:bandText
FAILED test_a_real_compiled_graph_conforms_to_the_whole_etkl_shape_file
```

Restored: `8 passed`.

## 9. What this loop leaves exposed

**[[R212]] is CLOSED** on § 7's corpus output — not on a green CI, which spec § 5 arm 5 explicitly
refuses as evidence for that arm. Its row moves to `residues-closed.md` with the closure evidence in
place; the row is not deleted, and its raise-time snapshot `(63/202 closed)` is preserved unchanged.

**[[R220]] raised** `(66/210 closed)` — recomputed, not copied from R219's `(65/209 closed)`: the
register stood at 209 rows / 65 closed, closing R212 makes 66, and R220 itself is the 210th row.

*One ignored band that carries marker ink becomes TWO unlinked nodes.* The carrier mints
`{doc}#ignored{idx}` and the unit-marker path mints `{doc}#region{idx}` for the **same** band, and no
triple relates them — so a consumer asking *what ink did this band carry* must parse the index out of
two IRI spellings and join on it. That is a string join standing in for a graph join. It is the
direct cost of DECISION C, which is still the right call (fusing them would put two vocabularies the
membrane governs separately onto one node), and the disjointness test pins the separation while
pinning no edge, because there is none. How many corpus bands are both ignored and marker-carrying is
**not measured** — the population may be zero, which is why the row asks for that census first.

**[[R219]] updated, not closed.** Its band-vs-distinct-text confound is untouched and the 2935-word
figure is still an upper bound — but the instrument it needed now ships: with `etkl:bandText` on all
146 ignored bands, distinct-vs-repeated furniture text becomes a query over the compiled graph rather
than a census to re-run.

**[[R218]] untouched.** `tab:RegionCaption` still carries no page, no bbox and no
`prov:wasDerivedFrom`, and no shape targets it. This loop deliberately did not reuse or repair it
(spec § 3's second refusal, § 4's last line); `etkl:IgnoredBandShape` exists precisely so the new
carrier cannot repeat that decay.

**Left untested BY DESIGN, and not to be reported as confirmed.** The handoff before last predicted
that *a wired carrier shape costs zero vacuity-registry rows*. This loop declines the wiring arm
(DECISION D), so that prediction is untested here. What *was* measured is the complement: the
registry's reverse arm forbids a row for an unwired shape, and the file passes untouched (§ 5).

**Spec § 4's scope boundaries all held.** No shipped test asserts that an ignored band becomes a
header (graincorp b2 is carried as text and stays ignored), that the text reaches the proposer, or
that the capacity contract exists. No `iladub:CandidateConcept` is minted for an ignored band — which
matters, because doing so would have made § 2.8's registered 3-of-7 into 7-of-7 and falsified it. No
`tab:RegionCaption` is reused and no transient `tab:*Block` term is promoted.

**One finding this loop did not go looking for.** Deleting `_band_text` from `document.py` shifted
every line below it by 11 and broke two citations in a comment **this loop did not write**: they named
`section_facts`' writers by line, and the last of those lines moved from above the comment to below
it, tripping `tests/test_source_citations.py::test_no_tracked_comment_cites_a_line_below_itself`.
That is R139's exact mechanism, arriving from the direction CLAUDE.md plan rule 7 does not emphasise —
not an edit invalidating its *own* citation, but an unrelated deletion invalidating someone else's.
Re-measured: all four cited numbers were stale (`:1561/:1573/:1605/:1743` against the actual
`:1551/:1563/:1595/:1733`). Repaired by naming the writers by **symbol** rather than re-numbering,
which removes the hazard instead of re-arming it, and the comment now records why. `recognized`'s
inherited "TWO writers" claim was re-measured too and holds (`:1385` initialiser, `:1411` its only
`append`).
