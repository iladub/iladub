# Spec — only a REFUSAL admits the model: GLiNER2 enters the pipeline at three post-hoc seams, and edits no deterministic line

**Origin:** no residue. This design was reached across three sessions of conversation (2026-09-08 →
2026-09-10) whose only prior record is `HANDOFF.md` in the probe repo
(`/Volumes/WD Green/dev/git/iladub-gliner2-probes`, commit `d09c747`) and the probes beside it.
**Written 2026-09-10**, off `93fa7ce`, branch `only-a-refusal-admits-the-model`.

**Doc impact: one new term.** `iladub:supersededBy` (§3.3), plus the shape that constrains it.
Nothing else published changes.

**Nothing here has been executed.** No GLiNER2 model has been loaded or run in any of the three
sessions. Every behavioural claim about GLiNER2 below is read off its source or its tutorials.
§6 is the list of things that must be measured before any of this is believed, and §6.6 admits the
outcome in which the whole design is refuted.

---

## 1. What GLiNER2 is, what it is not, and the rule that places it

GLiNER2 is a schema-conditioned span tagger and text classifier over **flat text**. It is not a
document-structure engine and not a Docling or Textract substitute. It reads a string and a schema
and returns labelled spans, a label, or a record.

Two consequences, both load-bearing:

**Spatial layout is a no-op as GLiNER2 input.** `probes/probe_final.py` in the probe repo renders a
band as spatial ASCII and as plain text and counts the same 525 tokens either way. That figure is
itself suspect — §6, T7 — but the direction is not: the model has no channel through which column
geometry could reach it. **iladub's existing structure layer is therefore kept in full.** Nothing in
this design proposes GLiNER2 as a reader of tables. `region_round_trips` keeps failing loudly.

**Deterministic-first, AI-third governs placement** (`CLAUDE.md` §8; the AXIOM→AXIOM→NEURAL
precedent is set out in `src/iladub/splitkey.py`'s module docstring). GLiNER2 is a NEURAL tier. It
is cheaper than BAML — *asserted, and the first thing §6 measures* — so within the neural tier it
runs first:

```
exact_field  (AXIOM)  →  GLiNER2  (NEURAL, cheap)  →  BAML  (NEURAL, dear)
```

**The governing rule of this whole design, and the reason for its title:** every one of the three
placements below is a **post-hoc pass over material the deterministic layer already refused**. Not
one line of the deterministic path is edited. The model never sees a cell the oracle could have
grounded, never runs before a refusal, and never withdraws a decision the deterministic layer made.
Where that rule and convenience conflict, the rule wins — §3.2 and §3.3 are both shaped by losing
that argument.

### 1.1 The three placements, named

- **A — field binding.** A cell whose header did not match any contract field by exact label.
  GLiNER2 classifies the cell against the contract's field labels. Existing proposer seam.
- **B — cell splitting.** A cell that was emitted as a `status proposed` candidate because it
  carries two or more values fused into one string. GLiNER2 splits it into fragments; each fragment
  is re-grounded independently.
- **C — record extraction.** An escalated region — text the structure layer could not read as a
  table at all. GLiNER2 reads it in record mode against the contract.

---

## 2. Types: where they live, and how abstention is manufactured

### 2.1 The seam modules own the types; `iladub/gliner2.py` owns only the implementations

Dataclasses, `Protocol`s and `Fake*` implementations go in the **existing** seam modules —
`src/iladub/propose_ground.py` and `src/iladub/etkl/propose.py`. Only the three GLiNER2
implementations and the shared model handle go in the new `src/iladub/gliner2.py`.

This is what makes the offline test suite possible without the dependency: a test constructs a
`Fake*` from the seam module and never touches `iladub.gliner2`, exactly as the shipped BAML tests
do (`tests/etkl/test_propose.py`).

**A adds no types.** It reuses `GroundingProposal` (`propose_ground.py:16`) and `GroundingProposer`
(`:24`) unchanged, and is tested with the shipped `FakeGroundingProposer` (`:30`).

**B adds** `FragmentProposal`, `CellSplitProposal` and the `CellSplitProposer` Protocol to
`propose_ground.py`. Fragments carry character offsets into the cell's text. **Non-overlapping and
in-bounds is enforced by the implementation before it returns** — a malformed split is an
abstention, not an error and not a caller's problem.

**C adds** `ProposedRecordField`, `RecordProposal` and the `RecordProposer` Protocol to
`etkl/propose.py`, matching the `X | None` decline idiom its neighbours already use (`Proposal`
`:15`, `SpanProposal` `:56`, `RowRoleProposal` `:103`). `anchor_field` is carried on the proposal.

### 2.2 Abstention is manufactured, because GLiNER2 classification cannot abstain

`classify_text` returns a label. There is no null label and no "none of these" — argmax always
lands somewhere. Placement A therefore builds abstention out of two parts:

1. a **sentinel label** appended to the contract-field label set, and
2. a **confidence floor τ**.

Either firing yields `GroundingProposal(field_iri=None, ...)`, which is the shipped signal for "no
field" — `ground_concept` already routes it to a quarantined proposition (`ground.py:199-200`).

**The floor is a routing decision, not a truth decision.** It decides only whether BAML is asked
next. It never promotes anything: `_grounds_to` (`ground.py:107`) still adjudicates every binding
against a scheme or a SHACL value constraint, and a high GLiNER2 confidence buys no admission
whatsoever. A cell bound by GLiNER2 to a field with no oracle behind it is quarantined exactly as a
BAML proposal would be.

*This amends the §1 of the conversational design, which spoke of A "falling through to BAML on
abstention" as though abstention were native to the model. It is not; it is built here.*

**The sentinel is the riskiest assumption in this document.** If it never wins argmax, τ is the only
defence and A either binds wrongly or routes everything to BAML — losing the cheap tier it exists to
provide. §6 T2 and T3 measure exactly this pair, and T2 failing alone is survivable (A ships
floor-only); both failing drops A.

---

## 3. Seams: three post-hoc passes

### 3.1 A — the existing proposer seam, contract-gated

A is a `GroundingProposer`. It needs no new attachment point: `ground_concept` already takes a
proposer and already calls it only after `exact_field` returned `None`.

**`ground_concept` and `ground_document` are NOT modified.** The cascade is a
`CascadingGroundingProposer` composite assembled **by whoever constructs the proposer that
`ground_document` is handed** (`feed.py:618`, third positional argument): a tuple of proposers tried
in order, the first proposal with a non-`None` `field_iri` wins, and a member is never called once
an earlier one bound. Passing
`CascadingGroundingProposer((Gliner2FieldProposer(), BamlGroundingProposer()))` where a bare
`BamlGroundingProposer()` goes today is the entire wiring change — no signature moves.

**A is contract-gated.** `_grounds_to` refuses a non-exact match on a field that has neither an
`admissibleScheme` nor a SHACL value constraint — its own docstring (`ground.py:107-115`) says a
bare proposal on such a field "has no oracle → None (quarantine)". A proposal onto such a field can
therefore never be admitted, so producing one is pure cost. A filters `contract.fields` to
**oracle-bearing fields only** before building its label set, and **abstains without loading the
model** when that set is empty.

### 3.2 B — a second pass over the emitted graph, not over `_read_table`

The tempting seam is `feed._read_table`, which mints one `SurfaceConcept` per cell
(`feed.py:227`) — split the string there and the rest of the pipeline needs no knowledge of it.

**That seam is rejected.** At `_read_table` the trigger is not yet observable: nothing there knows
whether the cell will ground. Splitting on suspicion would put the model *before* the refusal, which
is the one thing §1's rule forbids. It would also mean editing the deterministic path.

**B is instead a second pass over the emitted graph**, reading the `status proposed` candidates
`_emit_candidate` wrote (`ground.py:103`) and re-running the **unmodified** `ground_concept` once
per fragment. The refusal has happened, it is in the graph, and B reads it there.

### 3.3 Withdrawal is SUPERSESSION, not deletion

Decision 8 of the conversational design said the fragments "replace" the whole-cell concept — one
cell, one accounting. It did not say by what mechanism. Deletion is the wrong one: it destroys the
record of what the deterministic layer actually did.

**The whole-cell candidate keeps every triple it has and gains an `iladub:supersededBy` edge to each
admitted fragment.** Accounting counts only non-superseded candidates. The refusal remains legible;
it is merely no longer counted.

`iladub:supersededBy` does not exist yet. It needs an ontology declaration and a shape. **Measured
this session: no file under `vocab/shapes/` uses `sh:closed`** — so an undeclared predicate passes
the grounding membrane (`feed.py:605`) in silence. The shape is therefore not defensive polish; it
is the only thing that can make a wrong supersession fail. §5.5 states what it must reject.

### 3.4 C — a pass over escalation-suggested candidates, not an attachment beside `escalate_region`

`escalate_region` (`etkl/holon.py:434`, per `HANDOFF.md`; not re-read this session) writes
`surfaceText = ascii_text`, `status proposed` and `fromRegion`. `etkl/compile.py` calls it from 13
sites.

**C attaches to none of those 13 sites.** It is a pass over candidates whose `suggestedBy` is an
escalation suggester, reading `surfaceText` back off the graph. `escalate_region` is not edited and
the 13 call sites are not touched — which is also what keeps C from having to be correct 13 times.

**C never withdraws an escalation.** It emits `CandidateConcept`s at `status proposed` and nothing
else. An escalation is the structure layer's honest report that it could not read something; a
neural pass producing a guess does not make that report false.

### 3.5 Where the B and C passes are invoked — an open choice, with the constraint that binds it

A needs no caller: it is a proposer, and the existing one already calls it. B and C are passes, and
a pass needs somewhere to be run from.

Each is a function taking the emitted graph and its proposer, and returning its own tally. **The
binding constraint, not the choice:** neither may run inside `ground_document` — decision 11 of the
conversational design keeps that function unmodified, and §1's rule requires both to run *after* the
refusals they read have been written. So both are invoked by the same caller that invokes
`ground_document`, immediately after it returns, in the order B then C.

**Which module hosts the two functions is left to the implementation plan.** It is a placement
question with no design consequence: any host satisfying the constraint above yields the same
graph and the same tallies. It is named here rather than omitted so the plan is required to answer
it rather than to discover it.

---

## 4. Packaging: local inference, pinned, gated, one handle

### 4.1 Local inference only; `from_api()` is rejected

`GLiNER2.from_api()` exists and is **rejected**, recorded here as rejected so it is not rediscovered
as an option. User instruction, 2026-09-10: *"reduce dependence on external services to the minimum
and only when there is no other choice."* There is another choice — the local model.

### 4.2 The extra pins a commit SHA, not a branch

A new `gliner2` extra in `pyproject.toml`, parallel to the shipped `baml` / `etkl` / `demo` extras:

```
gliner2 = [
  "gliner2[local] @ git+https://github.com/adsharma/GLiNER2@f26b0aef105d42e87936eb8a9aab3c545361df06",
]
```

`[local]` is what pulls torch — the counterpart of §4.1's rejection. The SHA is pinned rather than
the branch because GLiNER2 is actively evolving: `gliner25_cleanup` moved under this design during
the sessions that produced it, and `docs/boundary_architecture.md` — which the record-mode tutorial
cites for its semantics — is absent from the tree at this SHA. A branch pin would make the design's
behaviour a function of when it was installed.

### 4.3 Gate and handle

`gliner2_available()` returns true only when `GLINER2_LIVE == "1"` **and** `gliner2` is importable —
character for character the shipped `baml_grounding_available()` (`propose_ground.py:41`).

The model handle is a module-level `_MODEL` in `iladub/gliner2.py`. **`gliner2` is imported inside
`_model()`, never at module top**, so constructing any of the three proposers neither pulls torch
nor loads weights. The model id comes from `ILADUB_GLINER2_MODEL`, defaulting to
`fastino/gliner2.5-base-v1`. Single process, no lock. The schema is built once per contract, not
once per cell.

---

## 5. Testing

### 5.1 The seam is the test surface

**No offline test imports `gliner2`.** Each placement is exercised through its Protocol with a
`Fake*` living beside it in the seam module (§2.1), following `FakeGroundingProposer`
(`propose_ground.py:30`) and `FakeProposer` / `FakeSpanProposer` / `FakeRowRoleProposer`
(`etkl/propose.py:27,72,125`).

A needs no new fake. What is new for A is the composite, and it is tested for the two behaviours
that define it, using two `FakeGroundingProposer`s:

- a proposal with `field_iri=None` falls through to the next member;
- a bound proposal short-circuits, and the later member is **never called**.

B gets `FakeCellSplitProposer`, C gets `FakeRecordProposer`.

### 5.2 Gate tests, copied from the shipped ones

Mirroring `tests/etkl/test_propose.py:16-24`:

- `gliner2_available()` is `False` with `GLINER2_LIVE` unset (`monkeypatch.delenv`);
- constructing each of the three proposers does **not** import `gliner2`. This carries more weight
  than its BAML counterpart: the import pulls torch.

Plus one the BAML tests have no analogue for: **two proposer constructions share one `_MODEL`
handle** (§4.3).

### 5.3 Live tests — first contact

`@pytest.mark.skipif(os.environ.get("GLINER2_LIVE") != "1", reason="set GLINER2_LIVE=1 to load the model")`,
the shipped idiom at `tests/test_baml_smoke.py:37`. One test per untested assumption:

- the sentinel wins argmax on a cell that fits no field (§2.2);
- `structure()` is well-formed on a 2–3 token cell (all of B rests on it);
- record mode on an ETA/ETC/ETD band (C's predicted failure).

**These are written as runnable falsifications.** A failure is a result, not a broken test — §6 says
what each one costs.

They are **not** the measured run. Each is a single-case smoke test establishing that the behaviour
exists at all; §6 is the corpus-scale measurement, with thresholds, that the implementation plan
takes as its step 1. A passing test in §5.3 says the mechanism fires once. Only §6 says whether it
fires often enough to be worth having.

### 5.4 The accounting invariant

**The relevant ledger is `feed.ground_document` (`feed.py:618`)**, which counts one `grounded` or
`proposed` per cell concept and returns `FeedResult`. It is *not* `etkl/adoption.py`'s
`build_ledger` (`:43`), which accounts for lines and tokens on an adopted page against grid rows and
bands and never sees a `CandidateConcept` at all. `HANDOFF.md` § 5 points at `build_ledger`; that
pointer is wrong and this paragraph is the correction.

The group-by key is `iladub:fromRegion`, which `_emit_candidate` stamps from `concept.region`
(`ground.py:100`), itself derived from the cell's `prov:wasDerivedFrom` fragment (`feed.py:226`).
**A prior test must establish that `fromRegion` is cell-unique on the fixture** — it is cell-unique
only if `prov:wasDerivedFrom` is cell-scoped rather than page- or band-scoped, and that has not been
checked. The invariant means nothing until it is.

**Invariant 1.** Grouped by `iladub:fromRegion`, the count of non-superseded `CandidateConcept`s is
**1** (B declined, or its fragments were refused) or **N** (N fragments admitted) — never 1 + N.

**Invariant 2.** B runs after `ground_document` has returned, so `FeedResult.proposed` is stale. B
returns its own delta, and the test asserts
`proposed_before − superseded + admitted == recount(graph)`.

### 5.5 The shape test

`iladub:supersededBy` gets an ontology declaration and a shape in `vocab/shapes/iladub-shapes.ttl`.
The test asserts the grounding membrane **rejects** a `supersededBy` whose object is not a candidate
from the same region. Per §3.3 there is no `sh:closed` anywhere, so without this shape there is
nothing to assert and supersession is unenforced.

---

## 6. Falsification targets

### 6.0 The form

Each target is pre-registered **here, before the run**: claim, measurement, threshold, and the
consequence if refuted — so the run cannot be read afterwards as confirmation. A target without a
threshold is not a target. **The thresholds are judgements, not derivations**, and they are the part
of this section most worth arguing with.

### 6.1 The premise target — gates everything

**T1.** *Claim (§1):* GLiNER2 is a **cheap** tier before BAML.
*Measure:* median wall-clock per cell, local torch, warm model — model load time reported
separately — against a BAML `ProposeGrounding` call over the same cells.
*Threshold:* ≥ 10× cheaper.
*If refuted:* the AXIOM→GLiNER2→BAML ordering has no justification. The cascade collapses back to
the shipped AXIOM→BAML and **all three placements are withdrawn.**

T1 runs first because it can end this design before a single accuracy question is asked.

### 6.2 Gating placement A

**T2.** *Claim:* with a sentinel appended, argmax picks the sentinel on a cell whose column has no
fitting oracle-bearing field.
*Measure:* win rate over ≥ 30 hand-labelled such cells. *Threshold:* ≥ 0.8.
*If refuted:* A falls back to the floor alone — which is T3.

**T3.** *Claim:* a τ exists that separates correct from wrong bindings.
*Measure:* both confidence distributions over ≥ 50 labelled cells, with the mangled headers
(`Noiaed`, `Acetd`) as a **named stratum** — that is where miscalibration was predicted.
*Threshold:* some τ giving ≥ 0.9 precision at ≥ 0.5 recall.
*If refuted:* **A is dropped.**

T2 failing while T3 holds means A ships floor-only and the sentinel is struck from §2.2.

### 6.3 Gating placement B

**T4.** *Claim:* `structure()` returns parseable JSON with in-bounds, non-overlapping spans on 2–3
token cells.
*Measure:* over ≥ 100 short cells. *Threshold:* ≥ 0.95 — B's implementation refuses the rest
(§2.1), so a lower rate means B mostly abstains and earns nothing.

**T5.** *Claim:* fragments land on a `prefLabel` exactly.
*Measure:* admission rate of proposed fragments against the real term graph. *Threshold:* ≥ 0.5.
*If refuted:* **the fix is not normalisation.** `scheme_member` (`ground.py:81`) is bare
`str(lbl) == value` — no `_norm`, and `prefLabel` only, never `altLabel` — and §1's rule forbids
editing it. B is then restricted to fields carrying a SHACL value constraint, or dropped.

0.5 is a low bar for shipping. It is set at *earns more than it costs* rather than *is reliable*,
because B costs nothing when it abstains.

### 6.4 Gating placement C

**T6.** *Claim:* record mode with `anchor=` separates ETA / ETC / ETD.
*Measure:* per-field accuracy on escalated bands carrying ≥ 2 of the three.
*Threshold:* ≥ 0.8 per field.
*If refuted:* C is restricted to single-date bands, or dropped.
`docs/boundary_architecture.md` is absent at the pinned SHA (§4.2), so this measures behaviour with
no specification behind it.

**T7.** *Replaces the chunk arithmetic, which is void.* `HANDOFF.md` compares "525 tokens/band"
against `chunk_size=384`. **Measured this session at `f26b0ae`:** `split_text_into_chunks`
(`gliner2/inference/chunking.py:44`) splits into overlapping **word** windows — default 384 words,
64 overlap — so the comparison is a unit mismatch and asserts nothing. Further, chunking happens
only on the explicit long-text path (`gliner2/inference/runtime.py:1238`); plain `extract` /
`structure` pass `max_len` to `ExtractorCollator` (`runtime.py:115`) and **truncate**.
*Measure:* using GLiNER2's own tokenizer — not `probes/probe_final.py`'s reimplementation of the
regex — whether any band exceeds the collator's `max_len`, and whether the loss is silent.
*If it truncates silently:* C must chunk explicitly, or split bands before submission. The
525-token figure is discarded and re-measured either way.

### 6.5 Corpus

One page of one PDF has ever been examined. **The corpus is fixed before the run:**
`CBH Shipping Stem 26092025.pdf`, plus at least one document each from Bunge, GrainCorp and Cargill.
Scanned documents are excluded — OCR is deferred by user instruction and nothing in this design
accounts for it.

**T8.** *Claim:* the rigid-grid finding (8 columns, 33/33 rows) generalises.
*Measure:* the same extraction on the other three issuers.
*If refuted:* B and C may not be **reachable** on those documents at all. That is a scope finding
rather than a design refutation, but it must be recorded before any plan claims coverage.

### 6.6 Stopping rule

If **T1** fails, stop — nothing else is worth measuring.

Otherwise run T2–T8 to completion even as early ones fail: once the model is loaded the marginal
measurements are cheap, and a dropped placement is a result.

**If all three placements are refuted, this design is refuted, and that outcome is the spec's
conclusion.** The implementation plan must not be written such that this ending is unreachable.

---

## 7. What this design does NOT do

- It does not modify `ground_concept`, `ground_document`, `feed._read_table`,
  `etkl/holon.escalate_region`, or any of the 13 `escalate_region` call sites in `etkl/compile.py`.
- It does not replace, bypass or weaken the structure layer. `region_round_trips` still fails loudly.
- It does not let GLiNER2 promote anything. Confidence routes; oracles admit.
- It does not withdraw an escalation (§3.4) or delete a refusal (§3.3).
- It does not address OCR or scanned documents.
- It does not call `GLiNER2.from_api()`, now or later (§4.1).
