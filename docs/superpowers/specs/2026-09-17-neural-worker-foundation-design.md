# Spec — the NEURAL worker foundation: one contract, one live wire, one honest scoreboard

**Serves:** maintenance — the foundation under the etkl rung's ready criteria (`etkl:03`–`06`); it
meets none of them itself, and § 1d says why it cannot.

**Date:** 2026-09-17. **Branch:** `neural-worker-foundation-spec`, cut from `main` at `2e2d33b`.

**Doc impact: none.** No released term changes. The one vocabulary touch (W5 in § 2, the suggester
IRI's shape) is a URN convention inside existing `iladub:suggestedBy` / `dec:decidedBy` values,
not a new term.

**Authored over the floor.** The spec was drafted after the four measurements, at roughly 110K
working tokens (estimated from the session's token counter, not read from plimslop): past the 50K
originating floor, and not in the first third. **§ 1 is measured and stands. §§ 2–5 are design
and are PROPOSED**: the next session attacks them (adversarial review, per the repo's practice)
before any plan is written against them. The weakest, in the author's own judgement: § 3.2's
per-column grain (its column key is unmeasured) and § 3.4's null proposer (a uniformly random
pick over 4–5 options is a strong null, which may make every oracle look discriminating).

Every load-bearing claim cites `2026-09-17-neural-worker-seams-evidence.md` (**E**) or
`2026-09-17-neural-workers-evidence.md` (**E0**), where the command and its output are recorded.

## 0. The ruling this spec executes

CLAUDE.md principle 8, amended 2026-09-17: *a reading judgement gets at most one geometric attempt;
then a NEURAL worker.* A worker answers one small question a human answers at a glance, returns a
**strongly typed, closed** shape, never returns a value that is on the page, and exists only where
an oracle disposes its answer — **no oracle, no worker.** The handoff
(`2026-09-17-neural-workers-handoff.md` § 5a) named four parts: lean typed outputs, async
dispatch, a response cache, an eval harness scored by oracle acceptance.

## 1. What was measured, and what it changes

### 1a. Four of the five shipped proposers ask a closed question; two send it as an open string (E § 1)

`ProposeHeaderRowRoles` and the Python-side `ProposeHeaderSpan` are enums. `ProposeGrounding` and
`ProposeSplitKeyName` ask the model to **spell back** an option the host enumerated, then
string-match it — and `propose_ground.py:53-59` silently drops a spelling that matches nothing.
**The grain survives; the wire format is the defect.**

### 1b. `ProposeDimensionName` has no oracle for its answer (E § 2)

`round_trip` admitted `Banana` and `Colour of the sky` as the name of a `Q1..Q4` pivot, each with a
promotion decision. The shipped code records this honestly (`promote.py:85-87`: *"the name is a
model proposition, not oracle-verified"*). It is out of this loop's scope (§ 6), and raised.

### 1c. No production path runs a live proposer (E § 1, § 4)

Every `compile_document` / `compile_tables` call in `src/` and `scripts/` passes no proposer; the
`Baml*Proposer` classes are constructed only in tests. **Every corpus figure this repo has ever
recorded is a zero-model figure.** NEURAL in iladub today is a set of seams with fakes behind them.

### 1d. The population: two seams reach nothing; one reaches 2,364 cells asking 39 questions (E § 4)

With counting, abstaining proposers over all 7 corpus documents: **row-role 0, span 0** (positive
control on a fixture: row-role 1 = MERGE_AMBIGUOUS 1, so the zero is real), **grounding 2,364**
on the three contracted documents — **39 distinct surface texts**. Three consequences, each
load-bearing below:

1. **An eval harness has a population for grounding only.** A harness for row roles would score
   an empty set; building one now is building against nothing.
2. **The grounding question is asked at the wrong grain.** Which field a column grounds to is a
   property of the column; it is asked per cell. The right unit is **one proposal per (table,
   column)**, disposed per cell by the unchanged oracle. That is up to a ~60× cut in calls (an upper bound: gcap's 377 empty-text cells may span several columns) before async or
   caching buy anything, and it is what the handoff's "trivial for a human" grain means here: a
   human reads a header once.
3. **This foundation moves no document score** (grounding is outside the ink ratio,
   `document.py:1582`). It serves the rung by making the next NEURAL proposer cheap to add and
   measurable on arrival, not by lifting a figure.

## 2. The worker contract — the grain, settled

A **worker** is a BAML function plus a host adapter satisfying all of:

- **W1 — closed answer.** The return type is an enum, a list of enums, or a choice among options
  the host enumerated in the same call (a BAML dynamic enum built with `TypeBuilder`, with short
  `@alias` codes — E0 § 2 `outonly`). **Never a string the host must match.** A worker whose
  answer cannot be closed is not a worker under this contract (§ 1b).
- **W2 — a named oracle.** Each worker's adapter names the oracle that disposes its answer, in
  code and in the decision holon (`dec:consideredEvidence` already carries the evidence; the
  oracle's verdict becomes the composed rationale, W4). The oracle is never callable by the model.
- **W3 — no page values out.** Labels, numbers and names that are on the page come from PROCEDURAL
  extraction bound to their ink. The dense-page failure (E0 § 1: real values, wrong row) must be
  *unconstructible*, not unlikely.
- **W4 — confidence on the wire, rationale composed.** `iladub:confidence` is required on every
  `CandidateConcept` (`iladub-shapes.ttl:24`), so a worker returns one. `rationale` is **dropped
  from the wire** and composed by the host from the options, the choice and the oracle's verdict:
  no shape requires `dec:rationale` and no test pins a model-written sentence (E § 3). The saving
  is the ~95% of output tokens E0 § 2 measured, and the composed sentence describes what was
  *checked*, which a sentence the model writes after deciding does not.
- **W5 — the model is on the record.** The suggester IRI becomes
  `urn:iladub:suggester/baml.<Function>@<model-id>`, so two runs on two models are two agents in
  the graph, and the cache key (§ 3.3) includes the same model id.
- **W6 — abstention is typed.** A worker may abstain (the host's `None`). A response that fails to
  parse is **abstention, recorded as such** — never an exception that escapes a compile, never a
  retry loop.

**Non-determinism is tolerated at the proposal and nowhere else**: the membrane admits the same
class of thing either way.

## 3. The four parts

### 3.1 Lean closed outputs — the three workers that are reached or dangling

- `ProposeGrounding` → returns `{choice: FieldChoice, confidence: float}` where `FieldChoice` is a
  dynamic enum over the concept's contract fields plus `NONE`. Its `anchor_iri` is today a **free
  string** (`ground_propose.baml:3`) written unchecked into `iladub:suggestedAnchor`, which the
  membrane requires only to exist (`iladub-shapes.ttl:20`, `sh:minCount 1`, no class or value
  constraint) — an open answer, so it violates W1. It becomes the host's constant `gist:Category`
  (`ground.py:27`), which every AXIOM arm already writes (`ground.py:252`). **Dropping the model's
  anchor loses a suggestion nothing validates**; a closed anchor choice over named gist classes is
  a later worker, if a consumer of `suggestedAnchor` ever appears.
- `ProposeHeaderRowRoles` → return type `HeaderRowRole[]` with aliased codes (E0 § 2 `outonly`)
  plus `confidence`. **The prompt text is not changed** (§ 6).
- `ProposeHeaderSpan` → **authored**, since the Python seam has called it since `03b5e36` and it
  meets W1–W2 (a two-way choice disposed by `region_tiles`). Its prompt is new text and is
  therefore a proposition until § 3.4's harness has a population for it — which it does not
  (§ 1d). It ships behind the same gate as every other worker and makes no score claim.
- `ProposeSplitKeyName` → `{choice: KeyChoice, confidence}` over the VERIFIED admitting fields in
  the ≥ 2 arm. In the 0-admitting arm no oracle can admit anything; **the worker is not asked** and
  the arm quarantines as it would on an empty proposal (W2, *no oracle, no worker*).

### 3.2 Grain, then async dispatch

**Grain first (§ 1d.2).** Grounding proposals are asked once per **column question**, not once per
cell: the worker's inputs are the column's header path, the contract's field options, the page
furniture, and **a small sample of the column's values** (so the worker still sees what the values
look like — the unlabelled gcap measures have nothing else). Every cell of that column is then
disposed by the unchanged per-cell oracle, using the one proposal.

**THE SEAM TO MEASURE FIRST:** `SurfaceConcept` (`ground.py:37`) carries `text`, `value` and
`region` — **no column identity**. `table_records` (`feed.py:457`) builds it from the graph, where
the column is known. The plan must measure which graph fact identifies "the same column" across
records — including across a continuation chain (`_logical_tables`, `feed.py:77`) and for gcap's
377 cells whose `text` is `''` — and must not key the question on `text` alone, which would fuse
distinct unlabelled columns into one question.

**Then async.** The column questions are independent; they go out together through
`baml_client.async_client` (`asyncio.gather`, bounded concurrency). **Disposal stays sequential
and in the original order**, so the graph written is byte-identical to a sequential run given the
same answers.

**MEASURE before restructuring `ground_document`:** does `ground_concept` decide whether to ask
the proposer (`exact_field`, `marker_field`) without mutating `g`? If yes, a two-phase loop —
collect the column questions that will be asked, gather their proposals, then run the unchanged
`ground_concept` per cell with a proposer that serves the pre-fetched answer — preserves order and
output. If no, name the mutation and stop.

The oracle for this part: **a whole-corpus canonical graph hash (`corpus_verdict_snapshot.py`) is
identical between the sequential and gathered paths under a replayed cache.**

### 3.3 Response cache

Keyed on `sha256(function name, model id, rendered request body)` — the body from BAML's
`b.request.<Fn>(...)`, so the key is what was actually sent. The stored value is the raw response
text; replay goes through the generated parser (`baml_client/parser.py`), so a cached answer is
parsed by the same code as a live one. One JSON file per key under a directory the caller names;
**`BAML_LIVE=1` with a cache miss calls the model and writes; without it, a miss is an abstention**
(W6). CI never calls a model.

### 3.4 The eval harness — oracle acceptance, WITH A NULL

Over a recorded population (§ 1d), per worker, report the disposal classes: `admitted`,
`refused by oracle`, `abstained`, `unparseable`.

**The acceptance rate alone is not a metric.** § 1b is the counter-example: an oracle that admits
anything scores 100%. So the harness runs, beside the model, a **null proposer** that picks a
uniformly random option (seeded), and reports both rates. The figure of merit is the gap. **A
worker whose model rate is within the null's rate is not being measured by its oracle**, and the
harness says so in its output rather than printing a number.

The recorded population is the census's context set, persisted by the cache: the first live run
fills it; every later run (prompt change, model change) replays the *requests* and re-scores.

### 3.5 The live wire

One entry point constructs live workers: `compile_document(..., workers=live_workers(cache_dir))`
when `BAML_LIVE=1`, and nothing otherwise. No default changes: the corpus battery stays
zero-model unless a caller opts in. **Which caller opts in first is a maintainer's decision**, not
this spec's (§ 6).

## 4. Invariants

- I1. With `BAML_LIVE` unset, every compile's canonical graph hash is unchanged on all 7 corpus
  documents (the foundation changes no zero-model reading).
- I2. A replayed cache yields the same graph as the live run that filled it.
- I3. Gathered and sequential grounding yield the same graph (§ 3.2).
- I4. No worker's return type contains a free `string` field (a test over `baml_src/`'s worker
  functions — a lint in the same family as `test_baml_function_and_python_proposer_agree_on_arity`).
- I5. Every `sync_client.b.X` / `async_client.b.X` referenced under `src/` names a function
  declared in `baml_src/` — the check that would have caught `ProposeHeaderSpan` in July.

## 5. Oracles and falsification

Each invariant ships with a test and that test's falsification (CLAUDE.md plan rule 4): I4 must
fail against today's `ProposeGrounding`; I5 must fail against today's tree; I3 must fail when the
gathered path reorders disposal; the null proposer's row must be present and non-trivial in the
harness's own test on a fixture with a known answer.

## 6. What is NOT done

- **No new proposer** beyond authoring the dangling `ProposeHeaderSpan`. R234 and the furniture
  peel stay unpicked (handoff § 5d).
- **No micro-agents** (handoff § 5e). The shared tool belt is plausible on paper (E § 5); the need
  — evidence too large to push — has no known instance.
- **No prompt text is compressed** (E0 § 2, twice refuted).
- **`ProposeDimensionName` is not reworked** — raised as a residue (§ 1b). Candidate remedy for its
  own loop: ground the name as a closed choice among contract fields, which has an oracle.
- **No corpus caller is switched to live.** § 3.5 builds the wire; turning it on is a ruling.
- **No score claim.** Grounding is outside the document score (`document.py:1582`, ink ratio), and
  the two seams that feed the score are reached on no corpus band (§ 1d).

## 7. Blockers the maintainer must clear

- **`ANTHROPIC_API_KEY` is unset in this shell** (checked 2026-09-17: `[ -n "$ANTHROPIC_API_KEY" ]`
  false). The repo's only client is `claude-haiku-4-5-20251001` (`baml_src/clients.baml`). § 3.4's
  first live run needs it.

## 8. Gate classification (principle 8)

| piece | class | why |
| --- | --- | --- |
| worker answers | NEURAL | the reading judgements § 1a lists; disposed by their named oracles |
| oracles | AXIOM | unchanged (`region_tiles`, `_grounds_to`, membership) |
| async dispatch, cache, harness tally, null proposer | PROCEDURAL | orchestration and counting; they decide nothing about any document and carry no tolerance |
| composed rationale | PROCEDURAL | string assembly from recorded facts |

## 9. Review appended 2026-09-17

Reviewed adversarially in `2026-09-17-neural-worker-spec-review.md`. **§ 1d.1 and § 3.4 are
REFUTED as stated**: of 2,364 grounding asks, 2,215 can be admitted under no answer at all, and
the other 149 are one column whose oracle is a number pattern ([[R249]]). Read the review before
planning from this spec.
