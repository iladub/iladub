# Spec: a region the producer guard refused is furnished for escalation (R303)

**Serves:** maintenance. This is [[R303]], continuing `docs/superpowers/2026-10-09-r303-handoff.md`
(PR #326). Part 5 of that handoff was PROPOSED and was run first in this session. It held (§ 1).

**Date:** 2026-10-09. **Branch:** `r303-furnish-measure`, cut from `main` at `0dfe4af`.

**Doc impact: increment.** `vocab/queries/escalation-furnish.rq` is a published query (CC-BY-4.0).
The set of chosen-option labels it reads as evidence of an escalation grows from `{"escalated"}` to
`{"escalated", "refuse"}`. No vocabulary term or shape changes, and no released assertion is
contradicted. A consumer running the released query on a graph with a refusal gets one more
`dec:ExpansionRequest`, which is what the term already means.

**Global Constraint: the neurosymbolic gate (CLAUDE.md § 8).** The one change is classified in § 3
before any code. A tuned constant anywhere in the shipped diff is a review failure.

---

## 0. The concern, first

R301 made the producer withdraw a table whose cell an author's rule separates. It records a
refusal decision and escalates the region. **The escalation reaches no human.** Every other escalated
band on fed-h41 raises a `dec:ExpansionRequest`. The two withdrawn tables, `p5#region3` and
`p7#region3`, raise none, because the furnish query only reads a decision that chose `"escalated"`,
and a refusal chooses `"refuse"`. Spec R301 § 8 S3 forbids relabelling the refusal's option to fit
the query. So the query is what moves.

## 1. Measured (this session, at `0dfe4af`)

**M1. The handoff's prediction holds at corpus scale.** Command (scratchpad script, one process):
`compile_document("held-out/fed-h41-2025-01-02.pdf", validate_shapes=True)`, 218 s, 21,434 triples.

```
ExpansionRequests: 12      (one each on p0#region1,2  p1#region1,3  p2#region1,4
                            p4#region1,9  p5#region1  p6#region2,4  p8#region1)
p5#region3: 0 requests     p7#region3: 0 requests     control p5#region1 (same page): 1
```

Predicted 0, 0, ≥ 1. The R303 row's *"predicted at corpus scale, not measured there"* is now
measured. The fix appends to the row and does not edit it.

**M2. One furnish path exists.** `grep -rn ExpansionRequest src/ vocab/queries/` returns a minting
site only at `vocab/queries/escalation-furnish.rq:68`. Every Python hit is a comment. The query has
one caller, `src/iladub/etkl/document.py` (`graph += interpret.run(ESCALATION_FURNISH_RQ, …)`; find
it with `grep -n 'interpret.run(ESCALATION_FURNISH_RQ'`). This discharges handoff § 4's second
bullet.

**M3. Only the guard ever chooses `"refuse"`.** `grep -rnw refuse src/iladub` shows that the only
code minting an option labelled `refuse` is `ruleguard.mint_refusal` (`for name in ("admit",
"refuse")`). The census on fed-h41's graph, by chosen label × decision label × superseded-or-head:

```
12 ('escalated', 'verdict', 'head')
 7 ('escalated', 'verdict', 'superseded')
 2 ('refuse',    'refusal', 'head')
```

The 12 live "escalated" heads are exactly the 12 requests. Both refusals are chain heads.

**M4. The two refusals' chains differ.** `p5#region3-refusal` supersedes `p5#region3-d5`, a verdict
that chose `"asserted"`. `p7#region3-refusal` is the only decision regarding `p7#region3`. Its head
was an appended grid's `{t}-admission`, which carries no `dec:regarding` (ruleguard `chain_head`).
Neither superseded decision chose "escalated", so widening cannot furnish a region twice.

**M5. The proposed query, run on M1's saved graph** (scratch copy of the query with the evidence set
widened, `interpret.run` with `_escalation_vocab()`, then pySHACL over `dec-shapes.ttl` plus
`escalation-shapes.ttl`, ontology `dec.ttl` ∪ `risk.ttl` ∪ `etkl.ttl`, `inference="rdfs"`,
`advanced=True`):

```
baseline query re-run adds 0 new triples        (idempotent today)
widened: new triples 12, requests 12 -> 14
  new …/p5#region3-refusal-expansion  regarding …/p5#region3
  new …/p7#region3-refusal-expansion  regarding …/p7#region3
widened re-run adds 0                           (still idempotent)
dec+escalation shapes conform: True
```

That is 12 triples, 6 per refusal: three on the decision and three on the request. The carried
vocabulary triples were already present.

## 2. The design

**One change.** In `escalation-furnish.rq`'s `WHERE`, the chosen option's label is bound from a
closed set, `VALUES ?label { "escalated" "refuse" }` with `?o rdfs:label ?label`, in place of the
literal `"escalated"`. Nothing else in the `WHERE` or the `CONSTRUCT` moves. The supersession guard,
the required `dec:regarding`, the bound ordinals and `?req = {d}-expansion` all stay as they are.

**Why a refusal is an escalation, stated once.** The query's subject is *"a region the reader
could not read, stated as the decision it is"* (its first line). A verdict that chose `"escalated"` is
the reader declining to read. A refusal that chose `"refuse"` is the reader withdrawing a reading it
had made. Either way the region stands unread at reader scope, and that is the condition
`dec:EscalationShape` obliges to escalate. The chosen option's label stays the evidence, as the
query's header already argues (*"THE LABEL, never the option URI's suffix … the chosen option is
the evidence"*). The set of labels that count as evidence is written once, in `VALUES`, and the
header comment names both labels and cites R301 § 8 S3 for why the second exists.

**Invariants it must preserve** (each already pinned, § 5):
- **Single-hop supersession.** A refusal supersedes its head, so the head is never furnished, and
  the refusal is a head by construction (M3).
- **Idempotence.** `?req` stays a function of `?d`. M5 re-ran it and it added 0.
- **No `dec:regarding`, nothing derived.** The refusal carries `dec:regarding`, set by
  `mint_refusal`.
- **A bounded carry.** The three vocabulary triples are unchanged (T2.4).
- **§ 8 AXIOM.** A derivation: open world and evidence-positive. The `VALUES` set is a closed
  enumeration of evidence labels, not a tolerance.

## 3. Classification (CLAUDE.md § 8)

| decision | class | why |
| --- | --- | --- |
| a refusal's region is furnished for escalation | **AXIOM**, derivation (`SELECT`/`CONSTRUCT`), open world | it reads two present facts (a chosen `"refuse"` option and a `dec:regarding`) and grows the graph. The holon-scoped `NOT EXISTS` is the existing supersession guard, unchanged. |

No procedural code changes. `ruleguard.py` and `document.py` are untouched.

## 4. Alternatives rejected, with the measurement that rejects them

- **Handoff arm (b): furnish from the region's escalation rather than from a decision.** The region
  is an `iladub:CandidateConcept` that by design carries **no `dec:` property** (`holon.
  escalate_region` docstring, R69). `dec:EscalationShape` targets `dec:DecisionHolon`, so the
  furnish has to name a decision anyway. Picking *which* decision from the region side needs the
  decisions' own `rdfs:label` (`verdict`, `refusal`), which is a private spelling. That is the
  dependency the query's header already refuses for option IRIs. `p5#region3` has seven decisions
  regarding it, six of them unsuperseded (`-d0` to `-d4` and the refusal), so "not superseded" does
  not single one out.
- **Arm (a) plus a conjunct `?r a iladub:CandidateConcept` on the refusal branch.** It is
  evidence-positive, but it has **zero power on the corpus**: the null control on M1's graph adds
  12 triples with the conjunct and the same 12 without it (`equal True`). Worse, it fails in the
  wrong direction. A refusal whose region was *not* escalated would be a producer defect (R89), and
  the conjunct would hide it by furnishing nothing. Without the conjunct, the defect reaches a
  human. Rejected.
- **Relabel the refusal's option to `"escalated"`.** Forbidden by spec R301 § 8 S3.

## 5. Oracles

- **O1 (corpus pin, the close condition).** In `tests/test_r301_fed_h41.py`: on fed-h41 compiled
  with validation on, `p5#region3` and `p7#region3` each have exactly one `dec:ExpansionRequest`
  regarding them, each is the `dec:escalatedTo` of the region's `-refusal`, and the document has
  14 requests over 14 distinct regions. It is corpus-gated, so green CI is not evidence for it; it
  runs locally (memory: CI skips the corpus).
- **O2 (synthetic, in CI).** In `tests/etkl/test_ruleguard.py`, on `_minted_page` after
  `ruleguard.guard` and the furnish, the guard-escalated `#region0` gets exactly 1
  `dec:escalatedTo`, from its refusal. This turns the R303 row's measurement into a pin.
- **O3 (falsification, mandatory).** Remove `"refuse"` from `VALUES`, and O1 and O2 fail.
  Restore it, and they pass.
- **O4 (blast radius).** The other ten documents (7 corpus and 3 held-out) are unchanged. By M3 and
  R301's O4 no other document carries a refusal, so this is predicted. It must be **run**: serial
  before/after `scripts/corpus_verdict_snapshot.py --pdf`, plus `test_escalation_furnish.py -m
  corpus` (bfs `requests == live`, cbh). Never two corpus compiles at once.
- **O5 (unchanged synthetic contract).** `tests/etkl/test_escalation_furnish.py` and
  `test_escalation_wiring.py` stay green unmodified. If one has to change, that is a finding to
  report, not a test to weaken.
- **O6 (declaration).** `tests/query_terms.py`'s instrument stays green, since the query names no
  new term.

## 6. Unverified

- **`_census` in `test_escalation_furnish.py` counts only `"escalated"`.** On bfs that is harmless,
  because bfs has no refusal (by M3). Whether `_census` should also count refusals so that it states
  the same evidence set as the query is a choice for the executor to measure and report. It is not
  ruled here.
- **The vacuity registry** (`tests/etkl/test_vacuity_registry.py::corpus_graphs`) compiles the 7
  corpus documents. fed-h41 is held-out, so `dec:EscalationShape`'s per-document binding count there
  is predicted not to move. That is not measured.
- **The wiki exemplar catalogue** (`docs/wiki/concepts/neurosymbolic-exemplars.md`) may cite
  `escalation-furnish.rq`'s evidence label. Not read.

## 7. What is NOT done

- No change to `ruleguard.py`, to the refusal's shape, or to any membrane shape.
- No `dec:` term for "an option that obliges escalation". A typed option class would replace the
  label set with a type. That is a vocabulary change for HGA alignment to weigh, and is not needed to
  close R303.
- R302 and the three R301 rulings awaiting ratification are untouched.

## 8. Execution

The diff is one `WHERE` line, its header comment, two pins and a register close. **No plan is
proposed**, on the precedent of R208, whose spec was executed without one. That is a proposition
for the maintainer. If a plan is wanted, its seams are § 6's three bullets.
