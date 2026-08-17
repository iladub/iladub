# Coverage is not liveness — the R97–R104 loop

**Date:** 2026-08-17 · **Tree:** `main` @ `ddc45b6` · **Rows:** R97, R98, R99, R100, R101,
R102, R103, R104

**Doc impact: increment.** One new wiki concept page (`docs/wiki/concepts/coverage-vs-liveness.md`)
and an addition to `docs/wiki/concepts/neurosymbolic-exemplars.md`. No site page changes; no
release-blocking contradiction. Two **evidence-class** documents are corrected-by-supersession
rather than edited, per doc governance: `specs/2026-08-13-escalation-is-a-decision-design.md`
§3's M7 table (already flagged by R98) and its §4.5.

**Authoring caveat, stated because the rule exists.** This spec was written at 125K tokens,
2.5× the originating floor, on the maintainer's explicit instruction after the floor was
reported. CLAUDE.md § Loop & context hygiene predicts that a spec written this late is a draft
to re-derive. **It must get an adversarial read against its own measurements before any plan is
written from it** — the load-bearing claims below all carry inline citations precisely so that
read is cheap.

---

## §1 The question

Eight rows were raised as eight problems. They are one, and R87's own guard already contains
two-thirds of the answer while asking the wrong question of it.

`tests/etkl/test_vacuity_registry.py` asks, per shape: **can this check refuse at all?** That is
*liveness*. What every one of these rows is actually about is: **what did this check actually
see, compared to what it was wired to see?** That is *coverage*, and liveness is only its
degenerate case — the case where effective scope is empty.

The distinction is not rhetorical. It is measured, three times, this session:

- A shape can be **live and uncovering**: `dec:DecisionHolonShape` has 119 focus nodes on apple
  and **316 of 769** minted decision holons are never validated by it (R102, `residues-open.md:82`).
- A shape can be **idle in the guard's graph set and exercised outside it**: `tab:BaseFactShape`
  has 0 focus nodes on all 7 corpus documents and **8** in `tests/test_zero_etl_export.py`'s
  post-`analyze()` graph (M-A, `docs/superpowers/2026-08-17-m-a-basefact-measurement.md`).
- A shape can be **reported live by aggregation while unreachable on half its inputs**:
  `dec:EscalationShape` is term-reachable on **2 of 4** document-leg calls and reads as live
  because `idle_shapes` intersects across graphs (M-B,
  `docs/superpowers/2026-08-17-m-b-leg-liveness-measurement.md`).

### 1.1 The four axes, each measured

"Scope" turned out not to be one thing. Every axis below is a *different* reason a wired check
sees less than it appears to, and all four are live in this codebase today:

| axis | what narrows the scope | measured at |
| --- | --- | --- |
| **gate** | the tab-fact conditions on both `_validate` call sites | `compile.py:1097-1100`, `document.py:1584`; 316/769 holons (R102) |
| **phase** | the membrane runs *before* `analyze()` mints the facts some shapes validate | `_validate` saw 405 triples / **0** `tab:BaseFact`; `analyze(` occurs in 3 test files + the notebook and **nowhere under `src/`** (M-A) |
| **leg** | page-scope graphs cannot, in principle, carry certain terms | `tab:continuesColumn`/`inLogicalColumn` written only at `document.py:736-737`; `dec:Event`/`ExpansionRequest` only at `document.py:1575` (M-B) |
| **graph set** | the guard measures 7 final `rep.graph`s; the document membrane validates **4** of them | `test_vacuity_registry.py:316-317` vs M-B's call census (3 of 7 documents never open the doc gate) |

R101 adds a fifth notation in a different medium (CI job × test module) and R103 a sixth
(ontology file × membrane). R104 is **not** a coverage row at all — see §4.6.

### 1.2 The four questions the handoff left, answered

The prior handoff (`2026-08-17-r97-r104-handoff.md` § The next concrete action) asked four.

1. **Is the instrument keyed by `(check, scope)`, and which axes does it cover?**
   Yes. It covers **gate**, **leg** and **graph set** by construction, because all three fall out
   of recording what `_validate` was actually called with. It covers **phase** only as a
   *declared* fact, not a measured one — see §7.1, which is the most important limitation here.
2. **Do `tab:AggregationCellShape` and `tab:SectionTotalShape` adjudicate as gap or deletion?**
   **Neither, in this loop.** They are the only two of R97's four that remain genuinely
   uncovered on every axis, and adjudicating them needs corpus specimens this repo does not
   have. R97 closes; a new, narrower row opens for exactly these two (§8).
3. **Where does R99's membrane-composition question stop?** At the ledger. §4.3.
4. **Is the CI arm the same instrument or a sibling?** **Sibling.** M-C settles it: a shape's
   scope is a *graph set*; a test module's scope is a *construct*, and the two constructs behave
   differently (`importorskip` collapses 59 tests into 1 skip line at
   `tests/etkl/test_datagrid.py:218`; `pytestmark = skipif` stays proportional at 31 lines in
   `tests/etkl/test_membrane_equiv.py:19`). They share a vocabulary, not a mechanism. §5.

---

## §2 What proposes, what disposes, and why they are independent

R76 requires these come from different sources. Today's registry satisfies that (hand-authored
rows vs. computed measurement) but its measurement chooses its **own** graph set, which is the
defect in axis 4. The new arrangement:

| | proposes | disposes |
| --- | --- | --- |
| **coverage** | the **runtime ledger** — RDF facts emitted by the membrane during a real corpus compile, recording what each `_validate` call was handed | the **coverage expectation registry** — hand-authored rows declaring intended scope — plus a SHACL membrane over the ledger |
| **CI skips** | the **collection census** — facts extracted from pytest collection and module AST | the **skip expectation registry** — hand-authored rows, one per module-scope guard |

Independence is structural in both: the proposing side is produced by *running the system*, the
disposing side is *written by a person*. Neither is derivable from the other, and a change to
either alone breaks the guard — which is the property R76 exists to protect and the property
today's fixed-graph-set measurement quietly lacks.

---

## §3 The instrument

### 3.1 What it is

**A coverage ledger: an RDF record, emitted per compile run, of what each membrane invocation
actually validated.** For each `_validate` call it records the call site (leg), the graph's
identity and size, and per wired shape the focus-node count and the unreachable-term set.

The ledger is then judged declaratively against an authored registry of expected coverage. A
check whose effective coverage is narrower than its declared coverage, without a registered
reason, **fails the guard**.

Liveness becomes a query over the ledger rather than a separate mechanism: a shape is idle
exactly when its coverage is empty across every recorded call.

### 3.2 The invariants it must preserve

These are the contract. An implementation satisfying them is correct regardless of how it is
written.

- **I1 — the ledger records calls, never reconstructs them.** Every row corresponds to one
  actual `_validate` invocation. A ledger that *infers* what would have been validated is the
  defect this loop exists to remove.
- **I2 — the graph set is taken from the runtime, never chosen by the guard.** No fixed corpus
  list may appear in the coverage computation. (This is what axis 4 breaks today.)
- **I3 — both `_validate` references are instrumented.** `document.py:110` binds its own name at
  import (`from .compile import … _validate`); instrumenting `compile._validate` alone misses the
  document leg entirely. **MEASURED — M-B hit exactly this and had to patch both.**
- **I4 — two arms, as today.** Coverage narrower than declared fails; coverage *wider* than a
  registered-narrow row also fails, until the row is deleted. Every close is two edits. The
  existing coupling is at `test_vacuity_registry.py:337-348`.
- **I5 — aggregation is explicit.** Where a verdict is formed across several graphs, the rule
  (union / intersection / per-graph) is stated in the row, not implied by the code. M-B's finding
  that `idle_shapes` silently intersects unreachable-term sets is what this invariant forbids.
- **I6 — the ledger is scoped to one compile run.** The run is the holon and the closure
  boundary; see §6.

### 3.3 What replaces `VACUITY_REGISTRY`

It is **generalized, not deleted**. Each existing row becomes a coverage row whose declared scope
is ∅ with the same reason. Two rows change their *stated reason*, because M-A measured them
wrong:

- `TAB.BaseFactShape` (`test_vacuity_registry.py:108`) and `TAB.PivotedDimensionShape` (`:121`)
  say *"corpus does not exercise it"*. **The corpus does not; `tests/test_zero_etl_export.py`
  does** — 8 and 1 focus nodes respectively, and that test has run in CI on every push since
  `09b96a8`. The correct reason is the **phase** axis.

This is the same class of defect R98 records against spec §3's M7 table: the number was right and
the cause was wrong. A registry of reasons whose reasons are unverified is the failure mode this
whole loop is about, so §4.1's oracle checks the *reason*, not only the count.

---

## §4 The rows, and how each closes

### 4.1 R102 — first, largest, and the one R89 depends on

**Measured:** 769 decision holons minted, 453 ever validated, **316 never**; 16 of 27 corpus pages
carry holons no membrane sees (`residues-open.md:82`). Cause: both `_validate` sites are gated on
tab-facts (`compile.py:1097-1100`, `document.py:1584`).

**Closes by:** ungating the `dec` leg from the tab-fact condition so every minted decision holon
is validated, **and measuring the cost**. The row permits an alternative — a proof that the 316
cannot violate `dec:DecisionHolonShape` by construction — which this spec **declines**: it would
have to be re-proved after every emitter change, whereas the ungating is checked continuously by
the ledger.

**Named seam the implementer must measure, not assume:** the two gates guard *both* legs, not
just the dec leg. Ungating must not also un-gate the `tab` shapes onto graphs with no tab facts.
**MEASURE which shape sets each gate actually guards at `compile.py:453-465` before writing the
call** — `_validate` runs both sets under one condition today, so "ungate the dec leg" requires
splitting a call that is currently atomic. Do not assume the split is free; the comment at
`:457-459` argues for the combined report and that argument must be answered, not bypassed.

**Cost is unmeasured and must be reported:** the 41% are the documents with *no* tab facts, so the
added validations are on graphs nobody has timed. R57 and R60 are standing perf residues in this
area; if the cost is material, say so and raise a row rather than tuning anything.

**R89 resolves here, not separately.** Its adopted rule — *delete a producer-side guard only when
the membrane provably validates every product of that producer* — becomes satisfiable for
`BandRecorder.record` once R102 is fixed. Whether to then delete the guard is **out of scope**
(§7.4); the rule goes into CLAUDE.md as loop work.

### 4.2 R97 — closes, and splits

**BaseFact / PivotedDimension:** re-registered with the measured **phase** reason (§3.3).
**AggregationCell / SectionTotal:** coverage ∅ on every axis; a new narrower row (§8) carries the
gap-vs-dead adjudication forward. R97's own question — *corpus gap or dead shape* — is answered
for all four: for two the answer is "neither, and here is the third category"; for two it is
"still unknown, and here is the reduced question".

### 4.3 R99 — closes, and this is where the composition question stops

`iladub:NoLeakShape` has 11 focus nodes and names `iladub:asserted`, which no compiled graph
contains (`residues-open.md:79`). **The boundary this spec sets: the loop records the shape's
effective coverage on the compile membrane and registers it. It does NOT move the shape, and does
NOT decide which membrane it belongs on.** Moving a shape between membranes changes what crosses
which boundary, and that is a contract change requiring its own loop. The ledger makes the
question *answerable later* by making the shape's real coverage visible on both membranes — which
is strictly more than exists today, and less than R99's row contemplates. Stated so the next
session does not read this as the composition question having been settled.

### 4.4 R98 and R100 — close as ledger rows

**R98:** the behaviour at `document.py:1246-1253` is correct and stays. What closes is the
*record*: the shape's declared coverage is ∅-by-emitter-design, with the measured reason (who-wfa
does refuse a licence on pair (1,2); the graph fact is withheld deliberately). **The row's
prohibition holds: do not write `tab:licenceRefused` unconditionally.**

**R100:** its cheap close is **refuted, with evidence** — five shapes' liveness differs by leg, not
one, and `dec:EscalationShape` differs by criterion 2 rather than by focus nodes (M-B). So the
`(shape, leg)` key is *necessary*, and the ledger provides it as a by-product of I1: leg is
recorded because calls are recorded. The row closes on the measurement plus the key.

**Correct while here:** R100's row and the comment at `compile.py:408-409` both cite
`compile.py:1083` for the page call; at HEAD `:1083` is `if denom:`. The call is `:1101`.

### 4.5 R103 — closes its mechanical half only

**Load `tab-datagrid.ttl` into the probe** (`scripts/probe_emitter_typing.py:111` parses `tab.ttl`
only) and **report the count** of domain/range disagreements it surfaces. The row is explicit that
this and the membrane question are two questions and only the first is mechanical.

**Do NOT add `tab-datagrid.ttl` to `_FULL_ONT` in this loop.** `compile.py:443-447` records a
measurement that enlarging the ontology moved no tab verdict — that measurement was taken for
`dec.ttl`+`iladub.ttl` and **does not transfer**. Enlarging the closure again requires re-running
it, and the row wants R61 settled first so the probe is not rewritten twice. R61 is deferred by
maintainer decision (§7.4).

**Do not close this by fixing `tab:universeSource` alone** — the row says so explicitly; the
instance is not the residue.

### 4.6 R104 — the warm-up, and not part of the instrument

`_validate` collapses both legs into one `(bool, str)` at `compile.py:462-465`, and the raise
sites interpolate a hardcoded `"tab:"` (`compile.py:1103`, `document.py:1587`). A dec-leg refusal
reads as a tab-leg failure.

**Closes by:** carrying the leg identity through `_validate` and interpolating it at both raise
sites, plus a test that a dec-leg refusal's message names `dec` and not `tab`.

**One wrinkle no row records, found first-hand this session:** when both legs conform, `_validate`
returns `tab_report` only (`:463`) and discards the dec report entirely. Whether that matters is a
judgment for the implementer to state; it is not silently in scope.

This row is deliberately **not** an instance of the instrument — it is a mislabel, not a coverage
gap. It is in the loop because it is an hour's work in the same file and closing it moves the
tally, not because it shares the diagnosis.

---

## §5 The CI sibling (R101)

Same vocabulary, different mechanism, **separate guard**.

**Measured (M-C, `docs/superpowers/2026-08-17-m-c-skip-guard-census.md`):** 45 files / 390 collected
tests behind module-scope guards, of 1227 collected. **Nothing is accidental today.** R101's own
"48 modules / 8 `pytestmark`" figures verified correct; 37 of the 48 evaluate at import time.

**What closes it:** a registered expectation per module-scope guard — reason, and which construct.
The construct column is load-bearing and is M-C's finding, not R101's: `importorskip` at import
time **collapses** (59 → 1 at `tests/etkl/test_datagrid.py:218`), `pytestmark = skipif` stays
**proportional** (31 lines at `test_membrane_equiv.py:19`). Only the first is invisible in a CI
summary, and a registry that does not record which construct a module uses cannot tell the
maintainer which of its rows are dangerous.

**Two prohibitions carried:** do **not** close it by adding `demo` to the CI install line (R101's
row); and do **not** resolve the CI *policy* question — whether CI should install every extra —
which R101 explicitly did not open.

**Two specific findings the guard must make visible, both from M-C:**
- `test_datagrid.py`'s seven decorators claim to guard 7 tests, guard 59, and their `skipif` half
  is **dead code** (`pytest.importorskip(...) is None` is always `False` on success). Fixing the
  decorators is optional; **recording the true number is not**.
- `rapidocr`'s exclusion from CI is **inferred and written down nowhere** — which is exactly the
  evidence available for `pandas` before R101, where it was wrong. Its row must state the intent
  explicitly, following `pyproject.toml:49-53`, the only guard in the repo whose intent is
  recorded.

**Loop-boundary clause, used honestly:** the prior handoff wrote that this loop may conclude it is
two. It does — *partially*. §4 is one vertical slice (a real defect in R102, fixed, with a ledger
proving it stays fixed); §5 is a second. **If the session's budget is exhausted after §4, §5 is a
legitimate loop boundary and R101 stays open.** That is a planned stopping point, not a failure.

---

## §6 The neurosymbolic gate (CLAUDE.md §8)

Every decision classified, as the gate requires. **The gate is why the ledger is RDF rather than a
Python data structure**: the coverage judgment is declarative and must stay so.

| decision | class | justification |
| --- | --- | --- |
| recording what each `_validate` call was handed | **PROCEDURAL** | raw extraction — runtime events → typed RDF facts. Irreducible: no declarative form can observe an invocation that has not been recorded. The code must state this. |
| pytest collection + module AST → skip facts | **PROCEDURAL** | same class, same justification. |
| "what is this check's effective coverage?" | **AXIOM — SPARQL `SELECT`, open world** | derived from evidence that is *present* in the ledger; monotonic; never inferred from absence. |
| "is coverage narrower than declared / has a registered-narrow check gone live?" | **AXIOM — SHACL, closed world** | this is a membrane: it validates what crosses into the accepted-coverage holon. Cardinality and completeness are exactly SHACL's job. |
| R104's leg label | **PROCEDURAL** | not a decision at all — it reports the identity of a component that has already decided. |

**The closed-world guard is holon-scoped, as §8 requires.** The ledger for **one compile run** is
the holon and the closure boundary (I6); `COUNT`/`NOT EXISTS` close *within* that run while the
graph stays open. A coverage claim across runs would be closed-world derivation and is forbidden.

**No tuned constants.** There is no threshold anywhere in this design: coverage is compared to a
*declared* value, never to a tolerance. A percentage cutoff appearing in a plan derived from this
spec is a review failure.

---

## §7 What this loop deliberately does NOT do

Rule 5 makes this section load-bearing: a plan-supplied test asserting anything below is a
contradiction the plan author must catch.

1. **It does not measure the phase axis.** The ledger records what the membrane *was called
   with*. It cannot know that `analyze()` would later mint 8 base facts, because nothing on the
   compile path calls `analyze()` at all. Phase is therefore a **declared** reason on a registry
   row, backed by M-A's measurement — not a computed one. **A test asserting the guard detects
   phase-narrowing automatically cannot be written.**
2. **It does not extend any membrane to the post-`analyze()` phase.** That would make the compile
   membrane validate a graph produced by an opt-in call, which is a contract change.
3. **It does not move `iladub:NoLeakShape`, or decide membrane composition** (§4.3).
4. **It does not touch R61, and does not delete `BandRecorder.record`'s guards.** Both are
   maintainer-deferred: R61 until R103 has produced its count; the guard deletion because R89's
   adopted rule makes it *permissible* after R102, not *required*.
5. **It does not add `tab-datagrid.ttl` to `_FULL_ONT`** (§4.5).
6. **It does not resolve CI extras policy, or add `demo` to the install line** (§5).
7. **It does not run the pySHACL leg comparison.** Standing since R87; every verdict figure
   inherited from that loop is the rudof leg. M-A/M-B/M-C focus-node figures are computed in
   rdflib and are leg-independent, so this does not undermine them — but it stays unrun, and
   stays a standing item.
8. **It does not adjudicate `tab:AggregationCellShape` / `tab:SectionTotalShape`** (§4.2, §8).
9. **It does not build general observability.** The ledger records membrane invocations. Not
   timings, not the grounding leg (`feed.py`'s `_GROUND_SHAPE_FILES`, a third leg M-B did not
   measure), not anything outside `compile._validate`.

---

## §8 Residues this loop will raise

Stated in advance so they are escalated in-band rather than discovered at close. Tally at time of
writing: **94 rows, 18 closed.**

1. **Gap-vs-dead for exactly two shapes** — `tab:AggregationCellShape`, `tab:SectionTotalShape`.
   The reduced remainder of R97; needs corpus specimens the repo does not have.
2. **`idle_shapes` aggregates by silent intersection** — `test_vacuity_registry.py:190-205`.
   `dec:EscalationShape` is term-unreachable on 2 of 4 doc-leg calls and reads as live. The
   docstring argues the aggregation for the focus-node case (`:196-198`) and is **silent on
   criterion 2**. I5 forbids this going forward; whether the historical verdict was wrong is a
   separate adjudication. **Raise even if the new instrument makes it moot** — it is the evidence
   for why I5 exists.
3. **`src/iladub/readers.py`'s subsystem has no tests at all** (M-C, incidental). `openpyxl`,
   `python-docx`, `bs4`, `pdfminer` appear in no test file. A coverage gap of a different kind —
   no skip census would ever surface it, because there is nothing to skip.
4. **Whatever R103's widened probe counts.** Unknown until run; R103 predicts at least one
   instance (`tab-datagrid.ttl:261` vs `datagrid.py:625-626`).
5. **R102's measured cost**, if material.

---

## §9 The falsifying oracles

Named per slice, before implementation, as the loop discipline requires. **Every task report
carries a `## FALSIFICATION` block** (CLAUDE.md plan rule 4): remove or invert the thing the test
pins, show it **failing**, restore, show green.

- **O1 — coverage narrowing is caught.** Invert the tab-fact gate at `compile.py:1097` so a leg
  stops being called. The ledger's effective coverage shrinks and the guard **must fail**.
  Restore → green. *This is the oracle for I1 and I2: a guard with a hardcoded graph set passes
  this test unchanged, and must not.*
- **O2 — the go-live arm still bites.** Make a registered-∅ check acquire coverage; the guard
  **must fail** until its row is deleted. Generalizes `test_no_registered_shape_has_gone_live`
  (`:337-348`).
- **O3 — R102 is actually fixed.** The count of minted-but-never-validated decision holons must
  read **0**, measured the way R102 measured it (union of holons any `_validate` call saw, across
  all 7 documents). The falsification is the pre-fix number, **316**.
- **O4 — R104 names the right leg.** A dec-leg refusal's message contains `dec` and not `tab`.
  Falsify by reverting the leg parameter; the test must fail. *Note: a test asserting only "the
  message mentions dec" passes if the message names both. Assert the absence too.*
- **O5 — the skip census is real.** Block a dependency at import and assert the registry's
  recorded test-count for that module matches what is actually lost — **59 for
  `test_datagrid.py`, not 7, and not 1**. M-C demonstrated this end to end with an import-blocking
  plugin; the guard must reproduce it.

**O1 and O5 are the two that matter**, because they are the only ones that fail against the
*current* design as well as against a broken implementation. O3 and O4 pin specific fixes; O2 is
inherited.

---

## §10 Sequence

1. **R104** — warm-up, closes a row, ~1 hour. (§4.6, O4)
2. **R102** — the largest, with the gate split measured first and the cost reported. (§4.1, O3)
3. **R89's rule into CLAUDE.md** — one paragraph, adopted by the maintainer, currently recorded
   only in a handoff.
4. **The coverage ledger + registry**, closing R97, R98, R99, R100. (§3, §4.2–4.4, O1, O2)
5. **R103's probe half**, reporting its count. (§4.5)
6. **R101's CI sibling.** (§5, O5) — **legitimate stopping point before this step.**

Steps 1–2 are a shippable vertical slice on their own: a real defect, fixed, on real corpus input.
Step 4 is the second. Nothing here is a horizontal layer.
