# Spec — a firing is not a fact: the record five `tab` criteria are waiting on

**Serves:** prog:criterion:tab:09 — and, through one shared oracle, `tab:02`, `tab:05`, `tab:07`,
`tab:08`.

**Date:** 2026-09-18. **Branch:** `a-firing-is-not-a-fact`, cut from `main` at `2f3fc76`.

**Doc impact: increment.** Terms added to `cor:` (`vocab/internal/corpus.ttl`), which is internal
test-harness vocabulary, not published `iladub:`/`etkl:`/`dec:`/`risk:` — no site page describes
it, and nothing here contradicts a released assertion.

**Written in the session's first third, before any implementation.** Every load-bearing claim
carries its measurement, in `docs/superpowers/2026-09-18-a-firing-is-not-a-fact-evidence.md`; this
file cites those sections and does not re-derive them (CLAUDE.md § Plan authoring discipline,
rule 6).

---

## 0. What this loop is, and the two rulings it obeys

The previous handoff's § 5c offered the maintainer a fork and named its second bullet the standing
direction: *return to the arc — `etkl:05` (bfs) through [[R44]], three bounded sub-loops*. This
spec is what a session discovers when it walks that road: **every one of those sub-loops ends at
the same closed door**, and the door is not in the reading code.

Two rulings bind the design:

- **CLAUDE.md § 8, the gate.** Everything proposed here is AXIOM or PROCEDURAL; § 4.2 classifies
  each part and says why. Nothing here is a reading judgment, so nothing here is NEURAL.
- **CLAUDE.md § Documentation governance.** A derived file committed to this repo is a stored
  label unless a regenerate-and-diff gate makes it exactly what its source produces. The firing
  record proposed in § 2 is **not** derived — it is a dated measurement, on the `cor:Reading`
  precedent — and § 2.4 states what makes that legitimate rather than a stored label by another
  name.

## 1. The gap, stated once

Five criteria (`tab:02`, `tab:05`, `tab:07`, `tab:08`, `tab:09`) name one `prog:oracleTest` that
does not exist, and `holon:06` names a second (evidence § 1). M5b refuses `prog:met true` on a
criterion whose named test does not collect, so **those five cannot be flipped until the test is
written, whatever happens to R43, R44, R62, R71, R79, R83 or R84** — 5 of the 9 unmet criteria on
the arc's worst rung.

The test cannot be written as the criteria state it, because the three things it must read are not
facts: *which reason fires on which document*, *which reason an adjudication names*, and *whether
that adjudication disposes or holds* (evidence § 2 — 31 declared `cor:` terms, none of them these).
All three live inside `cor:rationale` string literals, and that prose has already drifted in three
measured places (evidence § 3), including one census figure that was corrected by [[R44]] on
2026-09-15 and is still wrong in a Turtle comment three files away.

**This loop builds the record. It disposes nothing.**

## 2. The terms

### 2.1 `cor:Firing` — a dated, traceable, verdict-classed measurement of one reason on one document

Modelled on `cor:Reading` deliberately: the register already has a term for *"a figure this repo
measured, on a date, at a commit, recorded somewhere a reader can open"*, and a firing is that kind
of thing. New terms in `vocab/internal/corpus.ttl`:

| term | shape |
| --- | --- |
| `cor:firing` | `cor:Document → cor:Firing`, multi-valued |
| `cor:Firing` | a class |
| `cor:reason` | `cor:Firing → xsd:string`, exactly 1, from the closed list of § 2.2 |
| `cor:live` | `cor:Firing → xsd:nonNegativeInteger`, exactly 1 — firings still escalating |
| `cor:superseded` | `cor:Firing → xsd:nonNegativeInteger`, exactly 1 — firings replaced by an adoption, **not** repaired |
| `cor:readAt`, `cor:atCommit`, `cor:recordedIn` | reused verbatim from `cor:Reading` |

**Two counts, never one.** A single `cor:count` is the defect this whole loop is about: bfs's
`ROUND_TRIP_FAIL` is 5 with 4 superseded, and an instrument that reported the live figure alone
would show an 80% improvement where nothing was repaired (evidence § 3.3). The split is the fact;
collapsing it is a judgment, and the register does not make judgments.

**A zero is recordable and is not the same as silence.** `cor:live 0 ; cor:superseded 0` asserts
*measured, does not fire*; no `cor:Firing` at all asserts *not measured*. The criteria's second arm
("fires nowhere on the corpus") needs the first and must never be satisfied by the second.

### 2.2 The reason vocabulary is derived from source, not authored

`sh:in` over a list is the membrane's closed-world half. The list itself must equal the escalation
reason constants the compiler actually emits — 14 at HEAD, enumerable
(`git grep -ho '"[A-Z][A-Z_]\{4,\}"' -- src/iladub/etkl/`, evidence § 2). A second test asserts the
`sh:in` list equals that enumeration, so **the machine derives the vocabulary and the author only
transcribes it**. A reason retired in source and left in the shape is then a red test, not a
silent survival.

### 2.3 `cor:disposes` — and the rival design, which is real

`cor:disposes`: `cor:Adjudication → xsd:string`, multi-valued, each value a reason from § 2.2.
Present = *this adjudication disposes this reason*. Absent = *holds*. The asymmetry is deliberate:
every adjudication in the register today holds everything, and silence should mean the status quo.

**The rival, named because it is cheaper and this repo has shipped its kind before.** The oracle
could read the existing prose: require each `cor:rationale` to carry a canonical sentinel
(`DISPOSES: ROUND_TRIP_FAIL`) and grep for it. That is exactly the shape of the shipped figure
gates ([[R187]], [[R189]]), which are HARD and which read claims out of prose, so it cannot be
dismissed as unprincipled.

**Why this spec proposes typed facts anyway, in one sentence that is falsifiable:** a sentinel can
say *disposed* but cannot be refused when it disposes a reason the document does not fire, and
that refusal — § 3's D2 — is the only guard against the failure this loop actually measured, which
was a census claiming a firing profile the document no longer had. If a reviewer judges D2 not
worth a vocabulary, the sentinel design is the fallback and the rest of this spec survives it
almost unchanged. **This is a fork for the maintainer, not a settled decision.**

### 2.4 Why a hand-authored firing record is not a stored label

The corpus is `.gitignore`d, so CI cannot compile it and no gate can regenerate this record. It is
therefore a *measurement*, in the class `cor:Reading` already occupies — dated, commit-stamped,
pointing at the evidence file that produced it — and not a *derivation*, which would be forbidden
uncached. A refresh instrument (§ 3, I3) reprints it from a live run and diffs; drift is then a
visible non-zero exit, not a silent lie. **That is the same trust model the register runs on
today**, and this loop's § 4 of the evidence is what happens without it.

## 3. What the loop builds — interfaces and invariants, not bodies

**D1 — the shapes (`tests/corpus-shapes.ttl`).** `cor:FiringShape` requires exactly one
`cor:reason` from the § 2.2 list, exactly one `cor:live` and one `cor:superseded`, and the
`cor:readAt` / `cor:atCommit` / `cor:recordedIn` triple that `cor:Reading` already requires
(`test_refuses_reading_without_a_date`, `…without_a_value`, `…untraceable_reading` are the three
negatives to mirror).

**D2 — the disposal guard.** An adjudication carrying `cor:disposes "X"` on a document with no
`cor:Firing` for `"X"` is REFUSED. *You cannot dispose what you have not measured.* This is the
one constraint the rival design of § 2.3 cannot express, and § 5's O2 is its negative.

**D3 — the oracle, `tests/test_corpus.py::test_escalation_reasons_are_adjudicated`.** The node id
five criteria already name. Per (document, reason) pair the register records as firing: the
document's `cor:adjudication` must `cor:disposes` that reason. **It fails today for every recorded
firing, and that is correct** — the criteria are unmet.

**D3a — how it stays honest without turning CI red.** Each undisposed pair is
`pytest.mark.xfail(strict=True)`, parametrised per (document, reason), with the expectation read
from the manifest. Strict is the forcing function: the loop that disposes a reason and does **not**
record it gets an unexpected PASS and a red build. The marker must be generated from the manifest's
own `cor:disposes` absence — never from a hand-kept Python list, which would be a third copy of the
fact this loop exists to stop copying.

**I3 — the refresh instrument, `scripts/escalation_census.py`.** Compiles the corpus (or `--doc`
one document), prints each reason's live/superseded counts per document, and **diffs against the
recorded `cor:Firing` set**, exiting non-zero on any difference. `scripts/bfs_reason_triage.py` is
its one-document ancestor and its control legs are the model; this one must read every figure it
checks from a committed source, which is precisely what that script could not do for its cell count
(evidence § 4).

**Not built:** no adjudication is rewritten, no `prog:met` moves, no reason is disposed. See § 6.

## 4. § 8 classification, part by part

| part | class | why it is irreducible to the classes above it |
| --- | --- | --- |
| D1, D2 | **AXIOM / constraint (SHACL, closed world)** | membrane validation of what may cross into the register — cardinality, closed vocabulary, a required co-occurrence. Textbook § 8 constraint. |
| D3 | **PROCEDURAL** | pytest parametrisation and node-id identity are runner facts; no RDF derivation can answer "does this node id collect" (evidence § 1's instrument header carries the same argument). |
| D3a | **PROCEDURAL** | marker generation is mechanical transcription from the graph. It decides nothing: the expectation is the graph's. |
| I3 | **PROCEDURAL** | irreducible raw extraction — the input is a compile run, not a store. It counts what `snapshot()` returns and compares two multisets. No tolerance, no threshold, no reading judgment. |

**No NEURAL part, and no tuned constant anywhere.** Every number in the design is a cardinality or
a count read off a run.

## 5. The falsifying oracles — run in this order

**O1, the vocabulary null, FIRST — it can kill § 2.2.** A hand-built `cor:Firing` with
`cor:reason "NOT_A_REASON"` must be REFUSED by D1, and a firing naming each of the 14 real
constants must be ADMITTED. If the `sh:in` list and the source enumeration disagree at HEAD, the
derivation of § 2.2 is wrong and the spec's closed vocabulary is not closed.

**O2, the disposal negative — the reason § 2.3 chose facts over prose.** An adjudication that
`cor:disposes "TRANSPOSED"` on bfs, which records no `TRANSPOSED` firing, must be REFUSED by D2.
If it is admitted, D2 is not wired and the rival design is strictly cheaper — adopt it.

**O3, the strict-xfail flip.** Add `cor:disposes` for one recorded firing and its parameter must go
from xfail to PASS; add it for a firing that is **not** recorded and O2 must refuse the manifest
before the test runs at all. Delete a recorded firing and the parameter must disappear rather than
silently pass.

**O4, the refresh re-finds today's measurement.** `scripts/escalation_census.py --doc bfs` must
reprint exactly the multiset measured at `2f3fc76` and recorded in the evidence § 3:
`DATAGRID_RESIDUE 1/0`, `KIND_NOT_SUPPORTED 3/1`, `REGION_TILING_FAILED 2/0`, `ROUND_TRIP_FAIL 1/4`
(live/superseded), and exit 0 against the record this loop writes. A run that cannot re-find a
figure measured hours earlier is low-power and must say so before anything is built on it.

**O5, the census closes.** `./.venv/bin/python scripts/oracle_test_census.py` must report
`tests/test_corpus.py::test_escalation_reasons_are_adjudicated` as no longer dangling, with its
three controls still PASS. That is the loop's end-to-end close: 6 dangling ids become 5, and
`holon:06`'s and the substrate three remain, correctly, as declared targets.

## 6. What this loop deliberately does NOT do

1. **It disposes no reason.** Turning bfs's `HOLD` into a disposal is a judgment about a reading,
   and [[R44]] records that the round-trip half is a *reporting* defect on evidence measured
   2026-09-16 — the strongest candidate, and still a separate decision with its own loop.
2. **It moves no `prog:met`.** Every one of the five criteria stays blocked on its residues; this
   removes the *second*, invisible blocker only.
3. **It does not compile the full corpus.** Only bfs was re-measured (evidence § 3). The initial
   `cor:Firing` record for the other six documents is I3's first run, and that run is the
   execution loop's first task, not this spec's claim.
4. **It does not touch `holon:06`'s oracle or the substrate three.** Different work, honestly
   future, correctly reported by the census as absent.
5. **It writes no new `# FIRES` comment.** The five that exist are evidence of the problem; the
   execution loop deletes them only if it can point every reader at the fact that replaced them.

## 7. The weakest parts, in the author's own judgement

- **§ 2.3's fork is the spec's real risk.** If the maintainer prefers the prose sentinel, D2 goes,
  and with it the only measured argument for new vocabulary. I have stated the falsifier (O2) so
  the choice is decidable rather than aesthetic, but I did not build both.
- **The record's freshness rests on a human running I3.** Same as `cor:reading` today, and
  `cor:reading` drifted for bfs across six recorded values before anyone noticed. A dated record
  that nobody refreshes is a slower prose.
- **"Fires on the corpus" is a 7-document claim measured on 1.** § 6.3 is honest about it, but the
  execution loop inherits a ~47-minute serial run it must not split across parallel compiles
  (three memory kills are already on record for that mistake).
- **I have not verified that D3a's parametrisation can read the manifest at collection time**
  without importing rdflib into a module that CI collects under memory pressure. If it cannot, the
  marker generation needs a different seam and D3a is the part to re-measure first.

---

*Author: François Rosselet. © 2026. Spec — CC-BY-4.0 with the rest of `docs/`.*
