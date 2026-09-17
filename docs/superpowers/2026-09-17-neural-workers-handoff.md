# Handoff — the NEURAL worker foundation

**Topic:** The maintainer ruled that a reading judgement gets one geometric attempt, not three. This
hands a fresh session the shared foundation every later proposer will stand on.

**Serves:** maintenance — the foundation under the etkl rung's four ready criteria (`etkl:03`–`06`); it meets none of them itself

**Date:** 2026-09-17. **Tree:** branch `neural-workers-handoff`, cut from `main` at `b7dd468`.

**Doc impact: none.**

**Authored over the floor.** This session ran a benchmark arm, a BAML demonstration and three
explanations before this file; its working-token figure was not read, and it is certainly past the
50K originating floor. **So part 5 is graded per action below, and the design decisions in it are
PROPOSED on purpose** — a fresh session under the floor is the one that should settle them.

---

## 5. The next concrete action

### 5a. ASSERTED — the subject: a foundation loop, spec first, in a fresh session

Mechanical, because its four parts are named and each already has a measured basis
(`2026-09-17-neural-workers-evidence.md`):

1. **A typed, closed, lean output for every proposer** — aliased enums and bare return types where
   the answer is a choice (evidence § 2, `outonly`).
2. **Async dispatch** — proposals for independent questions go out together through BAML's
   generated `async_client`; the oracle disposes them in order (evidence § 2; every call site is
   `sync_client` today, evidence § 3).
3. **A response cache keyed on the rendered request**, so a compile is replayable and CI stays
   offline. The model id is recorded on the decision holon.
4. **An eval harness whose metric is the ORACLE'S acceptance rate over recorded contexts** — no
   hand labels. This is the part that makes every later prompt change measurable instead of felt.

*Confidence: high on the list, because each item was measured or is a plain gap. It is a spec-sized
loop; write the spec in the first third of the session.*

### 5b. PROPOSED — the grain of a worker, which is the real design question

**Typed PROPOSED: it is a design claim this session argued for and did not test.**

The maintainer's framing (§ 2) is that the unit is a *mini worker answering a trivial thing* — a
question a human answers at a glance and a heuristic cannot. The proposed grain, to be attacked
before it is adopted:

- **One worker = one closed question over one already-recovered structure.** Its return type is an
  enum, a list of enums, or an index into options the caller enumerated. **A worker never returns a
  value that is on the page** — labels and numbers come from PROCEDURAL extraction, bound to their
  ink. That is what makes the dense-page failure (evidence § 1: real values, wrong row)
  *unconstructible* rather than merely unlikely.
- **A worker exists only where an oracle can dispose its answer.** No oracle, no worker: the gap is
  the oracle, and building it comes first. *The oracles are few and the heuristics are unbounded —
  that asymmetry is the point of the ruling.*
- **Non-determinism is tolerated at the proposal and nowhere else.** Two runs may propose
  differently; the membrane admits the same class of thing either way.

**THE SEAM TO MEASURE FIRST:** *for each of the five shipped proposers, is its answer actually
closed?* `HeaderRowRole` is. `ProposeDimensionName` and `ProposeSplitKeyName` return a **free
name** — an open answer by nature (evidence § 3 lists the shapes). Either they are a different kind
of worker with a different oracle, or the grain above is too narrow. **Do not force them into the
enum mould to make the rule look universal.**

*If this is wrong, the next session finds out in an hour: classify the five return types and see
whether "closed question" survives contact with two of them.*

### 5c. PROPOSED — dropping `rationale`/`confidence` from the wire is NOT free

**Typed PROPOSED because it changes what a decision holon records.**

Measured (evidence § 3): both are consumed, and `rationale` flows into `dec:rationale` on the
promotion decision. Principle 3 also requires a proposition to carry *a confidence*. So the ~95%
output saving has a price, and the spec must choose, not assume:

- a rationale **composed procedurally from the oracle's verdict** — arguably truer than a sentence
  the model wrote after deciding, since the shipped schema orders `rationale` after `roles`; or
- a rationale requested **only for proposals the oracle accepted**; or
- keep it, and take the saving only on `roles`.

**MEASURE before choosing:** which shapes require `dec:rationale` or a confidence on a
`PromotionDecision`/`CandidateConcept`, and whether any test pins the model's sentence.

### 5e. PROPOSED — beyond a prompt: a generic micro-agent whose tools are the AXIOM layer

**Typed PROPOSED: raised by the maintainer after 5a–5d were written; nothing here was built or
measured.** *"We can go beyond smart prompts and provide tools to produce generic and reusable
micro agents."*

The shape: instead of each proposer hand-rendering its whole context into one prompt, the model
**asks** for evidence through typed tool calls and then returns the same closed answer. In BAML a
tool is a class in a union return type (`GetColumnStack | RowText | SumRange | Final`), and the loop
is host code — orchestration, not a decision, so it is a justified PROCEDURAL step.

- **The tools are read-only SPARQL `SELECT`s over the ONE holon's evidence graph.** The derivations
  already written become the tool belt; the holon stays the closure boundary (principle 8). Only a
  promotion decision ever writes.
- **The oracle is NOT in the tool belt.** An agent that may call the oracle can search until
  something passes, and proposer and disposer stop being independent — with a weak oracle (R47's
  arithmetic, which can hold by coincidence) it *will* find the coincidence. The oracle disposes
  after the `Final`. Any retry is bounded (one, by default) and **each attempt is its own decision
  holon** with a typed `dec:rejectedBecause`.
- **It is the escalation, not the default.** Ladder: AXIOM → single-shot closed worker → micro-agent,
  and only when the single shot was refused or the evidence is too large to push. A loop multiplies
  calls, and the small tier is measurably weaker over several steps (evidence § 2: nano fails one).

**THE SEAM TO MEASURE FIRST:** *does ONE tool belt actually serve different judgements?* Take two
shipped proposers, list the evidence each prompt pushes today, and see whether the same three or
four tools would have supplied both. If each judgement needs its own belt, the reuse is an illusion
and this is five prompts with extra round trips.

*If this is wrong, the next session finds out in an hour, on paper, before any agent is written.*

### 5d. ASSERTED — what must NOT be done

- **Do not compress a shipped prompt's instructions** without the eval harness of 5a.4. Twice
  measured: tokens fell ~60% and accuracy fell to 0–1 of 8 (evidence § 2).
- **Do not use a `...` reasoning scaffold as a substitute for a rule.** Measured: the model reasons
  first, and wrongly.
- **Do not target nano.** Below the floor on the shipped prompt. Haiku / mini is the tier.
- **Do not treat the demo as an evaluation.** One hand-built input, which is the shipped prompt's
  own worked example.
- **Do not pick the first new proposer in this loop.** R234 and the furniture peel (R230–R233) were
  named in conversation as candidates **from their index lines only** — no full row was opened.
  Open the rows before planning against either.

---

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| **MAINTAINER RULING 2026-09-17:** a reading judgement gets at most ONE geometric attempt; on its first refutation the next loop writes a NEURAL proposer, not a second heuristic | `CLAUDE.md` § Core design principles 8, amended in this PR |
| Zero-AI is not a constraint on etkl; the constraint is *what is necessary, as low as possible* | same |
| The effort goes into ORACLES — few and bounded — not heuristics, which are unbounded | same; § 5b |
| The tier is Haiku / mini, not nano | evidence § 2 |
| On a dense ruled page docling-graph carries 13 of 45 rows and misattributes 3; "no fabrication" was the wrong question there | evidence § 1; [[R247]] |

**The ruling, in the maintainer's words** (2026-09-17, in session): *"We focus on the oracle, the
number will be smaller than heuristics that can and will explode. We have to find out the right
grain to use LLM as mini async workers to tell us trivial things which are however extremely
challenging seen as heuristics. If we are crystal clear on what we expect from this worker in terms
of strongly typed and shaped output, we can tolerate non-deterministic steps. Heuristics pull us
back to a machine problem, not something that the human sees or understands, and this is a trap."*

## 1. Where the primaries are

- **Evidence** — `2026-09-17-neural-workers-evidence.md`: § 1 the dense page, § 2 the four
  renderings, § 3 the shipped proposers' shapes and the dangling call.
- **Instruments** — `scripts/neural_worker_demo/` (`demo.py` + three `.baml` variants);
  `scripts/thirdparty/docling_benchmark/dense_page_row_check.py`,
  `graincorp_induced_template.py` (+ spec); the extended `docling_strict_schema_patch.py`.
- **The shipped proposers** — `baml_src/{header_rowrole,reshape_propose,split_key_name,ground_propose}.baml`;
  call sites `src/iladub/etkl/propose.py`, `src/iladub/propose_ground.py`.
- **The exemplars** — `docs/wiki/concepts/neurosymbolic-exemplars.md`, Loop Q: a NEURAL that only
  narrows a set an AXIOM already verified. That is the existing pattern this foundation generalises.

## 3. Unverified or assumed

- **That the etkl rung's slowness is mostly the geometric-refutation cycle.** Argued from the
  register's recent rows (R155, R208, R230–R233, R239, R47/R77) read at index level; not counted.
- **That an oracle exists for the judgements that matter.** Known counter-cases: the bfs p6 donor
  header (the membrane cannot refuse a wrong header), and possibly R47's ordinal column, where the
  arithmetic holds by coincidence.
- **Everything in evidence § 2 on Haiku.** The session's `ANTHROPIC_API_KEY` returned 401; the
  models measured were OpenAI's. **Fix the key before the fresh session starts.**
- **`ProposeHeaderSpan`** is called at `etkl/propose.py:88` and defined nowhere (evidence § 3).
  Not investigated; the foundation loop will trip over it.
- **The harness in `/private/tmp`** (docling venv) is purgeable; rebuild recipe in
  `2026-09-17-docling-graph-benchmark-handoff.md` § 5a.

## 4. What this session did

Ran the prior handoff's seam (PR #254), explained the docling findings, ran docling-graph on a dense
graincorp page and found a second schema defect in it, demonstrated four BAML renderings of one
proposer on two small models, and took the maintainer's ruling. No production code touched.
