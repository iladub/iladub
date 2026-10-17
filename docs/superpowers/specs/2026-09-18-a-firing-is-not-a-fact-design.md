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

---

## 8. Amendment, 2026-10-15: firings are derived from the corpus baseline, not authored

**Ruled by the maintainer 2026-10-15, in-session.** Two rulings, recorded here and in
`docs/superpowers/2026-10-15-firing-from-baseline-handoff.md` § 3:

1. **§ 2.3's fork is settled in favour of typed `cor:disposes`.** D2 stands, and the prose sentinel
   is not built.
2. **§ 2.1's authored `cor:Firing` record and § 3's I3 are withdrawn.** This spec predates
   [[R305]]'s corpus baseline (2026-10-10). `tests/corpus-baseline/<doc>.json` is a **generated
   cache** (CLAUDE.md § Corpus baseline; § Documentation governance names this exception). It
   records each region's `reason` and `verdict`, it is committed, and CI's `check` gates it. An
   authored firing record beside it would be a second copy of a fact that already has a gated one,
   and the drift this spec exists to stop would come back.

**Measured 2026-10-15 at `ff2c0de`.** Counted from `tests/corpus-baseline/*.json`, regions whose
`reason` is an upper-case constant, grouped by `(reason, verdict)`. The baseline reproduces the
figure the 2026-10-15 role-oracle handoff carried, which a live compile had produced:
`KIND_NOT_SUPPORTED` is **bfs 3 escalated** and **ons 2 escalated + 2 superseded**. It does not fire
on the other five `corpus/` documents. The verdict values seen are `escalated`, `superseded`,
`asserted` and `ignored`. Non-constant reasons (`"fewer than 2 lines"`, `"fewer than 2 columns"`)
carry verdict `ignored` and are not escalation reasons.

**What changes:**

- `cor:Firing` survives as a **term**, never as authored triples. The oracle lifts it **in memory**
  from the baseline JSON, one firing per (document, reason): `cor:live` = count of verdict
  `escalated`, `cor:superseded` = count of verdict `superseded`. The lift is PROCEDURAL raw
  extraction: JSON to typed RDF, no judgment, no tolerance. The tests then validate D1 and D2 with
  SHACL over manifest ∪ lifted firings (AXIOM, closed world).
- **The scope is the 7 `corpus/` documents only.** That is the criteria's own denominator. The baseline's
  `pdf` field (`corpus/…` vs `held-out/…`) is the discriminator, and it is read, not hard-coded.
- **The join key** between a manifest `cor:Document` and its baseline file must be measured, not
  assumed (seam for the plan).
- **I3 and O4 are replaced** by the existing `corpus_baseline.py regenerate`/`check`/`verify`.
  A changed firing profile now shows up as a committed baseline diff in the PR that caused it.
- **D2 gets stronger:** disposing a reason that fires zero live times on that document is refused,
  even if it has superseded firings. *Superseded is not repaired* (§ 2.1), and a disposal names live
  ink. **PROPOSED, not measured:** whether any existing adjudication would trip this.
- **§ 7's D3a worry is moot:** the oracle reads committed JSON and the manifest, never the corpus,
  so it collects in CI and **must not** be tagged `corpus` (the untagged-form guard from `9d3c73c`, #345; measure its exact
  name in `tests/`).
- **What is still NOT done (§ 6 stands):** no reason is disposed and no `prog:met` moves.

**O5 is unchanged** and is still the close: `oracle_test_census.py` reports the shared node id as no
longer dangling.

### 8.3 Amendment, 2026-10-16: § 2.2 is withdrawn, and four seams are measured

**Ruled by the maintainer 2026-10-16, in-session: § 2.2's closed reason list is withdrawn.**

- **Why the derivation fails.** § 2.2 derives the `sh:in` list from
  `git grep -ho '"[A-Z][A-Z_]\{4,\}"' -- src/iladub/etkl/`. At `04f2a72` that returns **21** strings,
  not 14. They include environment variables (`BAML_LIVE`, `ILADUB_RECORD_READINGS`,
  `ILADUB_MEMBRANE`), region kinds (`RECORD_TABLE`, `NON_TABLE`, `UNSUPPORTED_TABLE`) and BAML answer
  tokens (`CANNOT_TELL`, `OTHER`, `TABLE_TOTAL`, `TOTAL_OF_TOTALS`). The reasons are bare positional
  literals, for example `src/iladub/etkl/compile.py:1880` and `src/iladub/etkl/ruleguard.py:34`.
  There is no enum, so there is nothing to derive the list from, and filtering the grep would be a
  hand-kept exclusion list.
- **Why nothing is lost.** Under § 8 the firings are lifted from the baseline, so the only authored
  reason string left is a `cor:disposes` value. The strengthened D2 refuses any `cor:disposes "X"`
  whose document has no lifted firing of `X` with `cor:live` > 0, so a misspelt reason is refused by
  D2. **O1 becomes:** `cor:disposes "NOT_A_REASON"` on a corpus document is refused by D2.
- **D1 shrinks to the lift's own cardinalities.** Each lifted firing has exactly one `cor:reason`,
  one `cor:live` and one `cor:superseded`, and one `cor:recordedIn`, which is the baseline file's
  repo-relative path. `cor:readAt` and `cor:atCommit` are dropped, because `inputs.json` carries the
  fingerprint.

**Four seams, measured at `04f2a72` for the plan:**

1. **Join key.** For all 7 manifest documents, `"corpus/" + cor:file` equals the baseline's `pdf`
   (`tests/corpus-manifest.ttl:25,47,79,101,117,130,161`). The 4 `held-out/` files have no manifest
   entry. Part 5.2 of the firing-from-baseline handoff holds.
2. **No adjudication can trip the strengthened D2.** `git grep "cor:disposes"` over `tests vocab src
   scripts` returns nothing.
3. **The node id lives in a corpus-tagged module.** `tests/test_corpus.py:22` reads
   `pytestmark = pytest.mark.corpus`. CI runs `pytest -m "not serial"` (`.github/workflows/ci.yml:26`),
   so a tagged oracle would still collect there. The local gate `-m "not corpus"` would deselect it,
   though, which is R173's defect turned inside out. The tag therefore moves from the module onto the
   three tests that read the corpus.
4. **The census does not resolve a parametrised oracle cited bare.** `scripts/oracle_test_census.py:79`
   matches collected ids exactly, and `--collect-only -q` prints `…::name[param]`. M5b already
   resolves both forms (`tests/test_arc_manifest.py:232-236`). Unless the census adopts M5b's rule,
   D3a's parametrisation would leave the id dangling and O5 could never close.

**What the firing profile is at `04f2a72`** (live/superseded, `corpus/` only; constant reasons only):
apple `DATAGRID_RESIDUE` 1/0, `MATRIX_AMBIGUOUS` 0/1, `REGION_TILING_FAILED` 0/4; bfs
`BOXHEAD_EXCEEDS_RECORD` 0/1, `DATAGRID_RESIDUE` 2/0, `KIND_NOT_SUPPORTED` 3/0, `REGION_TILING_FAILED`
2/1, `ROUND_TRIP_FAIL` 0/6; ons `DATAGRID_RESIDUE` 2/0, `KIND_NOT_SUPPORTED` 2/2,
`REGION_TILING_FAILED` 0/2, `ROUND_TRIP_FAIL` 0/4. cbh, both graincorp files and who-wfa fire none.
That gives **six live pairs**, which are D3's parameters. bfs's `ROUND_TRIP_FAIL` is 0 live and 6
superseded, so the strengthened D2 refuses a disposal of it, and it is not a D3 parameter.
