# Adversarial review — the NEURAL worker foundation spec

**Serves:** maintenance — reviews `specs/2026-09-17-neural-worker-foundation-design.md` (PR #256)

**Date:** 2026-09-17. **Tree:** branch `neural-worker-spec-review`, cut from `main` at `a5ce874`.

**Doc impact: none.**

**Run in the same session that wrote the spec, past the originating floor, at the maintainer's
request** (CLAUDE.md wants a fresh session for this). To limit the damage, every verdict below
rests on a measurement, and the one design proposal (§ 4) is typed PROPOSED.

---

## 1. The attack that landed: the grounding oracle never chooses between fields

The spec made grounding the harness's first subject (§ 1d.1) because it is the only seam with a
population: 2,364 asks. **But an ask is not a disposable question.** `_grounds_to(is_exact=False)`
(`ground.py:164`) admits a *proposed* field only by scheme membership or by the field's SHACL
value constraint, and refuses outright any field with neither. So for each ask, the set of fields
the oracle *would* admit, A, decides what a worker can possibly do:

| |A| | what the worker can do |
| --- | --- | --- |
| 0 | nothing — every answer quarantines |
| 1 | only "that field or none"; the oracle checks the value, not the choice |
| ≥ 2 | choose among options the oracle cannot separate |

**Instrument:** `scripts/grounding_oracle_power.py` (committed). It calls the shipped
`_grounds_to` for every contract field on every ask, with results memoised per (value, field).

```
   cbh: cells by |A| {0: 725}
  gcap: cells by |A| {0: 228, 1: 149}
 gstem: cells by |A| {0: 1262}
```

**Positive control** (exact-matched concepts, whose field is known): constrained fields are in A
(`volume`, `commodity`, `month`, `port`, `status`), and unconstrained ones are correctly absent
(`client`, `year`, `elevationPeriod`), since a proposal can never admit those. The instrument sees
what the oracle does.

**What it establishes.**

- **2,215 of 2,364 asks (94%) cannot be admitted, whatever the model answers.** On cbh and gstem
  every asked column (`Vessel Name`, `ETA`, `Exporter`, `Name Of Ship`, the berth notices, …) is a
  column the contract does not cover, so NONE is the right answer and the only possible outcome.
- **The other 149 are one column: gcap's unlabelled tonnage column, with A = {capacity}.** Its
  oracle is `sh:pattern "^[0-9]{1,3}(,[0-9]{3})*$"` (`examples/shipping/capacity-shapes.ttl:28-29`).
  That pattern would pass any integer column. It also passes a bare `0`, and
  `capacity-shapes.ttl:10-18` records that this column's zeros are [[R213]]'s 110 invisible glyphs,
  a hazard that *"becomes live the first time a real proposer runs against this contract."*
- **|A| ≥ 2 occurs nowhere on the corpus.** The worker's *choice* between fields is never what
  an oracle disposes.

## 2. Verdicts, section by section

| spec § | claim | verdict |
| --- | --- | --- |
| 1a–1c | measured facts | **stand** |
| 1d.1 | the harness has a population for grounding | **REFUTED as stated.** The disposable population is one question (§ 1 above), and its oracle is a number pattern. |
| 1d.2 | per-column grain gives up to 60× fewer calls | **SUPERSEDED.** Computing A before asking removes 94% of calls with no model, no async and no cache (§ 4). The column-key seam still matters in general, but on the corpus it concerns one column. |
| 2 W1 | closed answers | **stands**, but the choice among options only matters when \|A\| ≥ 2, and that never happens here |
| 2 W2 | "a named oracle" | **too weak.** § 1b (R248) and § 1 above are two oracles that are named yet cannot separate the options. The test must be *does the oracle separate the options*, measured as \|A\|. |
| 2 W4–W6 | rationale off the wire, model id, typed abstention | not attacked; still PROPOSED |
| 3.1 | lean grounding wire | stands; low value, given § 1 |
| 3.2 | `ground_concept` decides whether to ask without mutating `g` | **holds** as far as read: `ground.py:247-251` calls `exact_field` then `marker_field` before any write. `marker_field`'s purity was not checked line by line. |
| 3.2 | async dispatch | moot for the corpus: after § 4, 149 asks remain, all one question |
| 3.3 | cache via `b.request` | not attacked |
| 3.4 | eval harness scored by oracle acceptance, with a random null | **REFUTED as a first subject.** Over the only disposable question, acceptance measures "did the model say *capacity*". The null gets it about 1 time in 5, and every acceptance includes R213's zeros. That is not a scoreboard. |
| 3.5 | live wire, opt-in | **hazard:** turning it on for gcap grounds R213's invisible zeros as capacities. It must not be enabled on that contract before R213 is ruled. |
| 4 I5 | lint: every called BAML function exists | stands; independent of all the above |
| BAML | dynamic enums for W1 | feasible: `TypeBuilder.add_enum` exists in baml-py 0.222.0 (`type_builder.py:102`). Using one as a return type needs a `@@dynamic` declaration in `baml_src` — a plan seam, not checked here. |

## 3. What the spec got right, confirmed rather than assumed

- The Loop Q pattern (decide membership first; let NEURAL only narrow) is the shipped precedent
  in `splitkey.py`. The review's remedy (§ 4) is that pattern applied to grounding, not a new idea.
- *No oracle, no worker* was the right rule. The spec applied it to R248 and then failed to apply
  it to its own chosen subject.

## 4. PROPOSED — what the foundation loop should be instead

*Typed PROPOSED: a design claim made past the floor. Each item says how it could fail.*

1. **An AXIOM pre-filter on grounding:** compute A before asking. With |A| = 0, do not call the
   proposer; quarantine with a rejection reason naming the empty set. This is the ruling's
   preferred class and removes 94% of calls.
   **Failure to check:** the abstaining battery writes the proposal's suggester, anchor and
   confidence onto the candidate (`ground.py:266`), so skipping the call changes those triples. I1
   ("zero-model output unchanged") would be violated by design, and the plan must name the new
   suggester and re-pin whatever reads it.
2. **|A| = 1 with a pattern oracle is a maintainer ruling, not a worker.** Asking a model whether
   gcap's unlabelled column is a capacity adds evidence the oracle lacks, and nothing then checks
   that evidence. R212's ruling (*the machine derives the measure name*) and R213's hazard meet
   here.
3. **I5 (the dangling-function lint) and authoring `ProposeHeaderSpan`** stand alone and can ship.
4. **Defer async, cache and harness** until some seam has a population with |A| ≥ 2, or a
   score-moving seam is reachable. Today row-role and span reach 0 corpus bands. Making them
   reachable is the [[R234]] lockout family, and choosing that as the subject is the maintainer's call.

**If (1) is wrong, it shows in the plan's first measurement:** count what reads the abstaining
candidate's suggester (`grep -rn "suggester/fake\|seam-census\|mapping-proposer"` over `tests/`
and the corpus manifests) before writing a line.
