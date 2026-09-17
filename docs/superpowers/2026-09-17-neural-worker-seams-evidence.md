# Evidence — the NEURAL worker foundation's three seams, measured before the spec

**Serves:** maintenance — the measurements behind `specs/2026-09-17-neural-worker-foundation-design.md`

**Date:** 2026-09-17. **Tree:** branch `neural-worker-foundation-spec`, cut from `main` at `2e2d33b`.

**Doc impact: none.**

The handoff (`2026-09-17-neural-workers-handoff.md`) typed three of its five next actions
PROPOSED and named a seam to measure before each: § 5b (*is each shipped proposer's answer
closed?*), § 5c (*what does dropping `rationale`/`confidence` cost?*), § 5e (*does one tool belt
serve two judgements?*). All three were run first. **A fourth measurement the handoff did not ask
for turned out to be the load-bearing one (§ 4): how often each seam is reached at all.**

---

## 1. § 5b — the five proposers, classified

Read from `baml_src/*.baml` and the host call sites; the "reached from" column is
`grep -rn "<entry>" --include='*.py' src scripts` excluding `def` lines and the defining module.

| proposer | wire return | is the answer closed? | what disposes it | reached from |
| --- | --- | --- | --- | --- |
| `ProposeHeaderRowRoles` | `string[]` described as `furniture\|continuation\|level` | **closed** (an enum sent as free strings) | `region_tiles` + lossless round-trip (`etkl/rowrole.py`) | `compile_tables(row_role_proposer=)` — **no production caller passes one** |
| `ProposeHeaderSpan` | `choice: absorb\|standalone` (per `SpanProposal`) | **closed** | `region_tiles` (`etkl/span.py`) | same; **the BAML function does not exist** (`grep -rn ProposeHeaderSpan baml_src` → 0; added by `03b5e36` on the Python side only) |
| `ProposeGrounding` | `field_iri: string?` holding a field **label** | **closed** — a choice among the `field_labels` the host enumerated, or none. The host maps the label back and **silently drops** any unmatched string (`propose_ground.py:53-59`) | `_grounds_to` — SHACL/scheme verification (`ground.py`) | `ground_document` → `ground_concept`; callers: tests, `reach_probe.py`, `measure_dec_membrane.py` (both with an **abstaining** fake) |
| `ProposeSplitKeyName` | `ScoredKeyCandidate[]`, free `name` | **closed in the arm that can admit** (≥ 2 admitting fields: the host matches the name against the VERIFIED set, `splitkey.py:257-294`); **open in the 0-admitting arm, which can only quarantine** | whole-set membership, run **before** the proposer — the Loop Q pattern | `resolve_split_key_name`; callers: **tests only** |
| `ProposeDimensionName` | free `name` | **open** — a name that is on no page | `round_trip` — which is **blind to the name** (§ 2) | `certify_with_proposals`; callers: **tests only** |

**Verdict on the handoff's grain** (*one worker = one closed question*): it survives four of
five, and two of those four are closed questions **sent over the wire as open strings** —
`ProposeGrounding` and `ProposeSplitKeyName` both ask the model to spell back an option the
host already enumerated, then string-match it. The fifth, `ProposeDimensionName`, is not a
different kind of worker with a different oracle: **it is a worker with no oracle for its
answer.** Under the 2026-09-17 ruling (*no oracle, no worker*) that is a finding, not a
variant.

## 2. The dimension-name oracle admits any name

`certify_with_proposals` run on the shipped test fixture (`tests/etkl/test_certify_proposals.py::_nameless_pivot`,
a `Product` stub over a nameless `Q1..Q4` pivot) with a `FakeProposer` returning each name:

```
'Quarter'              admitted=True ok=True promos=1
'Banana'               admitted=True ok=True promos=1
'Colour of the sky'    admitted=True ok=True promos=1
'Product'              admitted=False ok=False promos=0
control ragged 'Quarter' admitted=False ok=False
```

`round_trip` certifies the **reshape**, and the reshape's invertibility does not depend on what
the dimension is called; it refuses only a name that collides with an existing column
(`Product`). The ragged control refuses as designed, so the oracle is live — it is simply not an
oracle for the name. **The shipped code already says so honestly**: `promote.py:85-87` writes
*"the name is a model proposition, not oracle-verified"* into `dec:rationale`, and mints a
`CandidateConcept` for it. So nothing is being passed off as verified. What the ruling changes is
whether a model call is justified at all for an answer nothing disposes.

Also found: `reshape.py:207` hard-codes `"title": None`, so the page furniture [[R212]] carries
into the graph never reaches this prompt.

## 3. § 5c — what `rationale` and `confidence` are bound to

- **No shape requires `dec:rationale`.** `grep -rn rationale vocab/shapes/` → nothing;
  `dec.ttl:76` declares it with range `rdfs:Literal` and no cardinality.
- **`iladub:confidence` is REQUIRED on every `iladub:CandidateConcept`**
  (`vocab/shapes/iladub-shapes.ttl:24`, `sh:minCount 1`), and `dec:confidence` is optional and
  bounded to `[0,1]` (`dec-shapes.ttl:40`). Every NEURAL path mints a candidate, so a confidence
  is load-bearing for principle 3 and cannot simply be dropped from the proposal.
- **No test pins a model-written sentence.** The tests that read `dec:rationale` assert on
  host-composed text: `test_promote.py:23` (`"proposition"`, the host prefix at `promote.py:86`),
  `test_span_promotion.py:23` (`"standalone"`, `"tied"`), `test_ground_section_marker.py:115`
  and `test_grounding_value_constraints.py:76` (AXIOM arms, no model involved).

So the choice § 5c asked for is open on the rationale and closed on the confidence: a
procedurally composed rationale breaks no shape and no test; a proposal without a confidence
breaks `iladub-shapes.ttl:24` on the first candidate it mints.

## 4. How often each seam is reached — the population

**Instrument:** `scripts/neural_seam_population.py` (committed here). Abstaining, counting
proposers injected into `compile_document(span_proposer=, row_role_proposer=)` on all 7 corpus
documents, and into `ground_document(proposer=)` on the documents whose manifest names a
contract; one document per process. Run 2026-09-17 on this branch:

```
   doc   score  span rowrole MERGE_AMB identity grounding  ctx
 apple  0.9302     0       0         0       ok         -    0
   bfs  0.8851     0       0         0       ok         -    0
   cbh  0.9095     0       0         0       ok       725  725
  gcap  1.0000     0       0         0       ok       377  377
 gstem  0.9659     0       0         0       ok      1262 1262
   ons  0.7712     0       0         0       ok         -    0
   who  0.9156     0       0         0       ok         -    0
 total             0       0                         2364
grounding calls with empty surface text: 377; distinct surface texts: 39
```

**The identity column is a null control, and 0 = 0 proves nothing about wiring**, so the counter
was also run on a fixture that must reach the seam — `offcenter_merge_report_pdf`, which
`test_b1_3_merge_resolution.py::test_offcenter_overlap_never_enters_resolution` pins as escalating
`MERGE_AMBIGUOUS` with a proposer present:

```
POSITIVE CONTROL: span=0 rowrole=1 MERGE_AMBIGUOUS=1
```

The counter is wired; the corpus zero is real. (Span stays 0 on the fixture too: its resolver
needs an explicit `ambiguous_flank`, a strictly narrower trigger.)

**What it establishes.**

- **The two seams that could move a document score are reached on no corpus band.** Every
  corpus band is routed elsewhere before the `not merge_tiling_ok` branch; *which* branch takes
  each band was not measured here ([[R234]] is one documented instance of the lockout, on a cut
  the corpus does not produce). A row-role or span worker, however good, changes no corpus figure
  today.
- **Grounding is the only seam with a population: 2,364 calls over 3 documents — and only 39
  distinct questions.** Broken down:

  ```
  cbh   725 calls, 27 distinct surface texts, 5 contract fields
  gcap  377 calls,  1 distinct surface text ('' x 377), 4 contract fields
  gstem 1262 calls, 11 distinct surface texts, 5 contract fields
  ```

  The question *"which contract field does this column ground to?"* is a property of the
  **column**, and it is asked once per **cell** (`feed.py:752-756`, one call per concept per
  record). The rendered request differs per cell only by the value, so a cache keyed on the
  request would not collapse them. gcap's 377 are the [[R212]] unlabelled-measure case: the
  surface text is empty on every one, so text alone cannot even say how many columns they span.
- The closed choice is tiny: 4 or 5 options plus none.

**Not established.** Whether the per-cell value ever changes the right field for a column (the
value-constraint oracle is per cell and stays so; only the *proposal* is in question). Run with
`ground_document(validate_shapes=False)`; the counts are proposer calls, which precede the
membrane.

## 5. § 5e — one tool belt, on paper

The evidence each shipped prompt receives, read from its signature and call site:

| judgement | evidence pushed today |
| --- | --- |
| row roles | header rows' text, their column indices, merge candidates, cell counts, leaf labels |
| span | span label, leaf labels, flank label, flank side |
| grounding | surface text, value, contract field labels, page furniture (`_page_context`) |
| split-key name | section markers, a document-context sketch |
| dimension name | pivot column labels, stub label, title (**always `None`**, § 2) |

Four read-only queries would supply all of it: **(T1)** the page's ignored-band text;
**(T2)** the header stack over a column; **(T3)** the values in a column or under a marker;
**(T4)** the contract's field labels and schemes. T1 serves three judgements, T2 three, T4 two.
**So the reuse is not an illusion at the evidence level.** What is NOT shown is the *need*: the
largest prompt measured is 969 input tokens (evidence of the prior loop, § 2), and the handoff
gives "evidence too large to push" as the agent's reason to exist. No such instance is known.
*Paper only; nothing was built.*
