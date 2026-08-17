# The gate and the label — Loop 1 of the R97–R104 split

**Date:** 2026-08-17 · **Tree:** `main` @ `e3f447a` · **Rows:** R102 (closes), R104 (closes),
R89 (amends — rule recorded, application still open), R103 (measures its mechanical half; does
**not** close)

**Doc impact: increment.** Two increments, both named in §6: R89's adopted rule into CLAUDE.md
(a Contract edit, explicitly requested by the maintainer 2026-08-17), and one wiki line recording
that the `dec` leg is unconditional at document scope. No contradiction: nothing on the released
site describes either membrane gate.

**Provenance.** This spec is written from two completed reviews and takes **no new measurement as
a precondition**. Its inputs are [`../2026-08-17-loop-split-decision.md`](../2026-08-17-loop-split-decision.md)
§ Loop 1 (including amendments E1–E4), [`../2026-08-17-empirical-review-findings.md`](../2026-08-17-empirical-review-findings.md),
and the superseded [`2026-08-17-coverage-is-not-liveness-design.md`](2026-08-17-coverage-is-not-liveness-design.md)
§4.1 seam plus oracles O3/O4, which both reviewers confirmed. Every measurement quoted below
carries its source; **none of it was re-derived in this session**, and nothing in it needs to be.

---

## §0 Global constraints

- **The neurosymbolic gate (CLAUDE.md §8) binds.** §5 classifies every change. A tuned constant or
  a Python heuristic answering a span/read/group/role question is a review failure.
- **Plan-authoring rules 1–5 bind.** No implementation source in the plan. Every load-bearing claim
  about existing code carries its measurement inline. Named seams, not answers. A `## FALSIFICATION`
  block per task. Plan-supplied tests reconciled against §7.
- **A loop is a session.** The plan goes in a fresh one.
- **Source ownership.** Nothing here touches an HGA term. No `.ttl` is authored at all.

## §1 What this loop is

**A gate, a label, a contract paragraph, a register pass, and one independent measurement.** It is
the vertical slice of the R97–R104 split: a real defect fixed on real corpus input, closing two
rows. It builds **no vocabulary and no instrument** — the coverage ledger is Loop 2's, the CI
census is Loop 3's.

The two code changes are in the same file and do not interact. They are:

| # | change | row |
| --- | --- | --- |
| 1 | the `dec` leg of the compile membrane runs unconditionally at **document** scope | R102 |
| 2 | `_validate` carries which leg refused, and the raise sites stop hardcoding `"tab:"` | R104 |

---

## §2 R102 — ungate the `dec` leg at the document gate

### 2.1 The measured defect

**769 decision holons minted across the 7 corpus documents, 453 ever validated, 316 never**
(ons 203/218, bfs 113/232, the other five 0). Reproduced independently — empirical review
§ Verified, bullet 4. `dec:DecisionHolonShape` is **live**, not idle (119 focus nodes on apple):
this is not vacuity, it is a live shape most of the corpus never reaches.

Cause, both call sites gated: `compile.py:1097-1100` runs `_validate` only
`if validate_shapes and (any tab:RecordTable or any tab:HierarchicalTable)`;
`document.py:1584` only `if validate_shapes and (recognized or section_facts)`.
`_validate` (`compile.py:453-465`) then runs `_TAB_SHAPES` at `:460` and `_DEC_SHAPES` at `:461`
**unconditionally, under that one gate** — empirical review § Verified, bullet 1.

The 316 are **not** documents without tab facts. They are ons and bfs, which *do* open the page
gate (ons page-calls=1, bfs page-calls=2, M-B) and never open the **document** gate. Correcting
that premise is split-decision D11; E2 completes it — **three** documents never open the document
gate (`graincorp-capacity` too), the third contributing 0 never-validated holons and non-zero cost.

### 2.2 WHICH GATE — the document one, `dec` leg only

**This is the load-bearing decision the empirical review found unstated (E2). It is settled here.**

> **Ungate the `dec` leg at the DOCUMENT gate (`document.py:1584`) only. The page gate
> (`compile.py:1097-1100`) is left exactly as it is, and the `tab` leg is ungated nowhere.**

Why the document gate suffices: the merged document graph accumulates every page graph
(`document.py:1245`, E2), so a decision holon minted on any page is present in its document's
merged graph. Ungating the document gate therefore covers **all 316** — E2 states this directly.

Why not the page gate as well: ungating it adds **14 further page-leg validations** (E2) and **no
new coverage** — every holon they would see is already seen at the document leg. That is pure
addition to the membrane redundancy R57 already records, bought for nothing.

Why not the `tab` leg: the document gate's condition *is* the claim "this document has
document-level tab facts". Running the tab shapes where that condition is false is exactly what
the §4.1 seam warns against, and is redundant with the page leg besides.

### 2.3 The §4.1 seam — reused verbatim, and its argument answered

Carried unchanged from the superseded spec, reviewer-confirmed:

> **MEASURE which shape sets each gate actually guards at `compile.py:453-465` before writing the
> call.** `_validate` runs both sets under one condition today, so "ungate the dec leg" requires
> splitting a call that is currently atomic. Do not assume the split is free; the comment at
> `:457-459` argues for the combined report and **that argument must be answered, not bypassed**.

**The answer this spec gives, for the implementer to check rather than accept:** the `:457-459`
comment argues that when the membrane runs, *both* legs must run, so a page carrying both a tab
defect and a promotion defect is not reported as only the first. That argument is about the legs
run **together**; it says nothing about a leg running **alone where the other has no claim to
make**. So the invariant to preserve is *"whenever a leg runs, every leg requested runs, even after
one refuses"* — see I-B in §3.2 — and the gate-open path keeps its combined report unchanged.

### 2.4 Cost — measured, and to be re-measured through the compile path

E2 validated the full merged graph of each never-gated document against both shape sets at HEAD:

```
graincorp-capacity: triples=5705   holons=18    DEC conforms=True (0.6s)  TAB conforms=True (0.6s)
bfs:                triples=8244   holons=232   DEC conforms=True (0.6s)  TAB conforms=True (0.8s)
ons:                triples=11076  holons=218   DEC conforms=True (0.8s)  TAB conforms=True (0.8s)
```

**The `dec`-leg column is the one this loop adds: ~2.0 s across three documents.** E2's headline
"~1.4 s per document (~4 s total)" is the *both-legs* figure and must not be quoted as the cost of
this change.

**Seam:** those timings are a standalone validate, not a validate through `compile_document`. The
task report must state the **measured wall-clock delta of the corpus suite** before and after, from
a run it performed. If the delta is material, say so and raise a row — **tune nothing.** R57 and
R60 are the standing perf residues in this area.

### 2.5 The branch the split decision flagged as unplanned — now measured, still answered

At HEAD, **both legs conform on all three never-gated documents** (E2's table above), so
**ungating does not turn the corpus red.** The risk is measured away, not argued away.

The response is still specified, because the gate is the thing that was hiding the answer:

- If the ungated path **refuses** on any document, the compile raises `AssertionError` and the
  corpus suite goes red. **That is the new membrane finding a real defect**, and the response is
  to report the offending decision-holon URIs from the SHACL report and **stop for adjudication**.
- **It is not** to re-gate, weaken a shape, or add an exception. Either is a §7-violating repair
  (assert only what the source supports) dressed as a green suite.
- **D16 applies to the task report:** distinguish *"the guard failed"* from *"the compile raised"*.
  They are different events and only one of them is a test result.

### 2.6 D7 — why this membrane change is in scope while R99's is not

The split decision requires the principle be stated or the R99 deferral stop being called
principled. It is:

> **A gate change is in scope; a wiring change is not.** Ungating alters *when* an already-wired
> shape set runs over graphs it already targets — the membrane's composition is untouched and
> coverage can only grow. R99 asks whether `iladub:NoLeakShape` belongs on the compile membrane
> **at all**, which changes what that membrane *is* and requires deciding where `iladub:asserted`
> is written. Same vocabulary, different act.

R102's row calls its own fix "a membrane-composition question." Under this principle it is not
one, and the row should be amended to say so when it is struck (§4).

### 2.7 The scope boundary this creates, and its seam

Coverage after this change is **document-scope**. A caller that runs `compile_tables` alone, with
the page gate false, still validates no decision holon. Loop 1 accepts that boundary and states it
rather than leaving it to be discovered.

**Seam, before the close is claimed:** MEASURE whether any **production** caller invokes
`compile_tables` outside `compile_document`. If one exists, the 316→0 close is narrower than it
reads and a row must be raised for the page-scope residual. If none does — tests, scripts and the
notebook aside — record that as the reason the boundary is acceptable, **in the register row, not
only in the task report.**

---

## §3 R104 — carry the leg identity

### 3.1 The measured defect

`compile.py:462-465` concatenates both legs' reports into one string, and both raise sites
hardcode the label: `compile.py:1103` raises `f"asserted holon failed tab: SHACL:\n{text}"`,
`document.py:1587` the same for document-level facts. **A `dec:DecisionHolonShape` violation
surfaces as a `tab:` failure** — empirical review § Verified, bullet 3, which also confirms the
`:463` wrinkle (when both legs conform, the dec report is discarded).

### 3.2 The contract

`_validate` gains an explicit leg selection and returns **which legs refused**:

- **Signature:** `_validate(graph, legs=("tab", "dec")) -> tuple[bool, str, tuple[str, ...]]`.
- **I-A** — conforming ⇒ the third element is `()`. Refusing ⇒ it lists exactly the refusing legs.
- **I-B** — every leg in `legs` runs, always, even after an earlier one refuses (§2.3).
- **I-C** — the default runs both legs, so no existing caller changes behaviour.
- **I-D** — the raise message names exactly the legs in the third element and **no other leg**.

**Why the third element and not a prefixed report string.** A cheaper design — leave the 2-tuple
and prefix each leg's report text with its name — was considered and rejected: O4 must assert the
**absence** of `tab`, and a substring search over a whole SHACL report body is not a reliable pin
(report text can carry `tab`-namespaced IRIs for reasons unrelated to the label). The label must be
a structured value the test can read, not a substring of a diagnostic.

**The `:463` wrinkle is ruled on, not left silent:** the conforming path's returned text stays the
first-run leg's report, unchanged. The label defect is fixed by I-A/I-D without touching it, and
nothing reads a conforming report. **Out of scope; deliberately, and this sentence is the record.**

### 3.3 The call-site set — six references, three of which are edits

E3 corrected the "~1 hour, two sites" scoping. Enumerated at `e3f447a`, `grep -rn '_validate' src
tests scripts`, filtered to `compile._validate` (the many `membrane._validate_pyshacl` /
`_validate_rudof` / `feed._validate_grounding` hits are different functions and out of scope):

| site | what it does | edit? |
| --- | --- | --- |
| `src/iladub/etkl/compile.py:453` | the definition | **yes** |
| `src/iladub/etkl/compile.py:1101` + `:1103` | page-scope call and its hardcoded `tab:` raise | **yes** |
| `src/iladub/etkl/document.py:1585` + `:1587` | document-scope call and its hardcoded `tab:` raise; also §2's gate | **yes** |
| `src/iladub/etkl/document.py:110` | binds `_validate` by name at import (I3, verified) | no — but the plan must not assume `compile._validate` alone is reachable |
| `tests/etkl/test_compile_membrane_shapes.py:94,:122,:143` | unpack a 2-tuple | **yes, three** |
| `tests/etkl/test_compile_membrane_shapes.py:35` | calls `_validate(seed)`, discards the return | no |
| `tests/etkl/test_membrane.py:92` | `assert "membrane" in inspect.getsource(C._validate)` | no — but it **pins the source text**, so check it, don't assume |

**No script and no other module calls it.** That enumeration is the claim §3's plan must not
restate from memory: re-run the grep and paste it.

---

## §4 The register-honesty pass

**E1 is already fixed, outside this spec** — `residues-open.md:82` no longer says "16 of 27
corpus pages"; it says 27 pages / 14 gate-FALSE / 13 genuinely unseen, with the correction marked
in place and the empirical review cited. The superseded spec's banner carries the same correction.
A wrong number in the canonical register does not queue behind a spec.

The pass this loop owes (split-decision D5, downgrade-or-carry):

1. **`docs/superpowers/residues.md:6`** still says a closing loop *"deletes its row in the same
   change."* CLAUDE.md § Deferred residues explicitly reverses this. **Fix the preamble** (E4).
2. **R100's row and `compile.py:408-409`** both cite `compile.py:1083` for the page-scope call; at
   HEAD `:1083` is `if denom:` and the call is at `:1101`. The citation has drifted. Correct both —
   the comment is in a file this loop edits anyway.
3. **R102 and R104 close: strike the number (`~~R102~~`), record the closure evidence in place, do
   NOT delete the row.** R102's strike carries §2.6's amendment (it is a gate change, not a
   composition question) and §2.7's boundary.
4. **R89 amends, it does not close.** The rule is adopted and recorded (§6); whether
   `BandRecorder.record`'s guard is then deleted is **out of scope** (§7). The row must say which
   half moved.
5. **The rule for the pass, applied to anything else found:** a row whose stated fact has been
   refuted is corrected **in place with the refuting measurement cited**, or downgraded and marked
   as such. Never silently edited, never deleted.
6. **Tally.** 94 rows / 18 closed at `e3f447a` (empirical review, verified). Any new row records
   its own snapshot `(n/m closed)` per CLAUDE.md and never updates it afterwards.

---

## §5 The neurosymbolic gate (CLAUDE.md §8)

| change | class | justification |
| --- | --- | --- |
| the `dec` leg becomes unconditional at document scope | **AXIOM (closed-world / SHACL membrane)** — and strictly *more* so than today | The change **removes** a procedural predicate from the path that decides whether the contract membrane runs. Nothing is added: the constraint stays in `dec-shapes.ttl`, and the holon remains the closure boundary. This is the §8-preferred direction of travel. |
| the `tab` leg's gate condition (`recognized or section_facts`, and the page gate) | **unclassified — deliberately untouched** | This is split-decision **D8(a)**, and it is **Loop 2's**. Loop 1 neither classifies nor changes it. Saying so here is the record that it was not overlooked. |
| leg identity through `_validate` + the raise labels | **PROCEDURAL, irreducible** | Formatting a diagnostic string about which shape set refused is not a decision over an evidence graph. The *verdict* is SHACL's; only its label is code. The plan must state this in the code, per §8. |
| widening the R61 probe to a second ontology file (§6) | **PROCEDURAL, irreducible** — raw extraction | The probe reads domain/range rules out of a `.ttl` and compiles corpus pages to check them. It is an offline measurement instrument, not a production decision; R61's own probe carries the same classification. |

**No tuned constant, tolerance, or geometric threshold appears anywhere in this loop.** If one
appears in the plan, the plan is wrong.

---

## §6 The contract paragraph — R89's adopted rule

Adopted by the maintainer 2026-08-17 and **recorded nowhere but a handoff**
(`2026-08-17-r97-r104-handoff.md:28-31`), which is exactly the failure mode this project has paid
for twice. It goes into CLAUDE.md as a short subsection immediately after § Core design principles'
principle 8 block:

> **Producer-side guards vs the membrane (adopted 2026-08-17, R89).** *Delete a producer-side guard
> only when the membrane provably validates **every** product of that producer.* A producer-side
> guard that a membrane also enforces is not automatically a duplicate: it fails fast at the call
> site that built the bad value, with that call site on the stack, where the membrane refuses
> thousands of triples later. The duplicate-deletion argument that applies to a *test* asserting
> something about a finished graph does not transfer to a producer-side raise. The condition is
> **provable total coverage of that producer's output** — and R102 is the case that shows why:
> `BandRecorder.record`'s two guards were the sole enforcement for 316 of 769 decision holons,
> while looking like duplicates of `dec:DecisionHolonShape`.

**Scope note, to be written into the register and not into CLAUDE.md:** this loop makes the rule's
condition *satisfiable* for `BandRecorder.record` (§2 closes the coverage hole at document scope).
**Whether to then delete that guard is out of scope** — see §7.

The second increment is one wiki line stating that the `dec` leg is unconditional at document
scope. **Seam:** grep `docs/wiki/` for the page that states the membrane gate rather than assuming
one exists; if none does, the increment is the CLAUDE.md paragraph alone and the `Doc impact:`
block in the plan says so.

---

## §7 What this loop deliberately does NOT do

Named here so that a plan-supplied test asserting any of it is caught as a contradiction before it
ships (plan rule 5).

- **No coverage ledger, no vocabulary, no registry.** Loop 2. Nothing in this loop emits RDF.
- **No CI-scope work**, no `pytestmark`/`importorskip` census, no change to the CI install line.
  Loop 3 — including the finding that R87's vacuity guard has never run in CI.
- **The page gate is not ungated** (§2.2) and the `tab` leg is not ungated anywhere.
- **`BandRecorder.record`'s guards are not deleted.** The rule is recorded; applying it to that
  guard is a separate decision, and R89's row stays open for it.
- **R103 does not close.** §8 widens the probe and reports a count; whether `tab-datagrid.ttl`
  belongs in the membrane ontology is untouched, and R61's modelling question stays deferred.
- **No emitter or ontology is corrected** on the strength of §8's count. *"Do not close this by
  fixing `tab:universeSource` alone"* — R103's row.
- **The conforming path's returned report is unchanged** (§3.2's `:463` ruling).
- **The pySHACL leg stays unrun.** Standing since R87; every figure here is the rudof leg. Focus-node
  counts are pure rdflib and engine-independent; verdicts are not.

---

## §8 R103's mechanical half — an independent measurement, not part of the slice

**Widen `scripts/probe_emitter_typing.py` to parse `vocab/ontology/tab-datagrid.ttl` alongside
`tab.ttl` (`:111`, verified as `tab.ttl`-only by the empirical review) and report the count.**

Why it is safe to carry here, and why it is *not* in the slice:

- The probe is invoked by **no test and no CI job** — enumerated at `e3f447a`,
  `grep -rn probe_emitter_typing` returns only documentation hits. So widening it cannot turn CI
  red, and its output is a number in a task report, not a gate.
- It compiles with `validate_shapes=False` (`scripts/probe_emitter_typing.py`, the corpus loop in
  `main`), so **§2's gate change cannot move its result.** The two halves of this loop are
  independent by construction, which is the reason they can share a session.
- It requires the corpus, which is gitignored — this is a **local** measurement, exactly as R61's
  original probe run was.

**Deliverable:** the count of violated rules and violating nodes attributable to
`tab-datagrid.ttl`, split as R61's probe splits them (live hazard = the class is shape-targeted, vs
inert), appended to **R103's row as a carry** — the row is not struck.

`tab-datagrid.ttl:261` declares `tab:universeSource rdfs:domain tab:ColumnUniverse` while
`datagrid.py:625-626` hangs it on the grid node: expect at least that instance to appear. **Report
it; do not fix it.**

---

## §9 The falsifying oracles

Named before implementation. **Every task report carries a `## FALSIFICATION` block** (CLAUDE.md
plan rule 4): remove or invert the thing the test pins, show it **failing**, restore, show green.
**No falsification evidence ⇒ the task review fails.**

- **O3 — R102 is actually fixed.** The count of minted-but-never-validated decision holons reads
  **0**, measured the way R102 measured it: spy both `_validate` references (`document.py:110`
  binds its own name — I3), take the union of decision holons any call saw, across all 7 corpus
  documents. **The falsification is the pre-fix number, 316.** Re-gate the dec leg and the count
  must return to 316.
  *Reported alongside it, not asserted by it:* the corpus wall-clock delta (§2.4).
- **O4 — R104 names the right leg.** A dec-leg refusal's message contains `dec` and **not** `tab`.
  **Assert the absence, not only the presence** — a test that only checks "the message mentions
  dec" passes when the message names both. Falsify by reverting the leg parameter; the test must
  fail. The setup is constructible: `_under_furnished_promotion()`
  (`tests/etkl/test_compile_membrane_shapes.py:98`) already builds a graph that violates **only**
  `dec:DecisionHolonShape`, and `:122` already drives it through `_validate`.
- **O4b — the both-legs label is still honest.** A graph refusing on both legs must produce a
  message naming both. This is the assertion that stops the label fix from becoming a mislabel in
  the other direction, and it is the one I-D exists for.

**Neither O3 nor O4 fails against the current *design*** — they pin specific fixes, which is all
Loop 1 claims. That is a deliberate difference from the superseded spec's O1/O5, and it is why this
loop is a slice rather than an instrument.

---

## §10 Order, and where it may stop

Three stopping points, each leaving the tree green and shippable:

1. **R104** (§3) — the label. Smallest, self-contained, one test file. Closes a row.
2. **R102** (§2) — the gate, with §2.3's seam measured **before** the call is written, §2.4's cost
   reported, §2.5's response ready. Closes the largest row in the loop.
3. **The contract paragraph and the register pass** (§6, §4) — no code. Then **§8's measurement**,
   which is independent of all of the above and may be dropped without affecting the slice.

R104 first is deliberate: it changes `_validate`'s signature, and R102 changes the call site that
signature is read from. Doing R102 first means editing `document.py:1585` twice.
