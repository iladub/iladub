# Handoff — `holon:05` measurements

**SUPERSEDED as the entry point by the spec it fed:**
`docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md`, written the same day.
Read the spec first; this file is the evidence behind its §2, kept for the raw commands and output.
Where the two disagree, the spec is later and carries the corpus sweep this file predates.

**Topic:** process · **Date:** 2026-08-25 · **`main` @ `20a5b0e`** (merge of PR #116,
`holon-05-design-decisions`) · **Shape: originating, stopped at 83,205 tokens** — 1.7× the 50k
floor, logged `stop`.

**Supersedes `docs/superpowers/2026-08-25-holon-05-design-decisions.md` as the standing pointer.**
Open that file for the three design decisions and their rationale (§ *What was decided*), which are
**not** repeated here. Everything below is either a measurement it asked for, or a correction to it.

This is the **second consecutive session to hand off without a spec**, and that is worth naming.
It is not the same failure twice: the previous session stopped with three blocking measurements
*unrun* and named them as the next session's first act. This session ran all three (delegated, so
they cost ~30k rather than the whole budget) and stopped with **nothing left to measure before
authoring**. A third session that does not produce the spec in its first third is a loop failure;
this one is a handoff working as designed.

## Goal

Unchanged: give a compiled document an `etkl:membraneHealth` signal, closing arc criterion
`holon:05` and moving the `holon` rung 4/6 → 5/6.

## Where the primaries are

The 2026-08-25 design-decisions handoff's § *Where the primaries are* table is still accurate and is
**not** restated. Read it there. Corrections and additions measured this session:

| primary | correction / addition |
| --- | --- |
| `src/iladub/etkl/promote.py` | the previous handoff cited this as `src/iladub/promote.py` — **wrong path**. Also `src/iladub/splitkey.py`, not `src/iladub/etkl/splitkey.py` |
| `src/iladub/etkl/holon.py:82-105` | a **third** held-candidate writer the previous handoff missed — the cell-level `ROUND_TRIP_FAIL` emitter (`confidence 0.0`), alongside `escalate_region` at `:424-472` |
| `vocab/shapes/iladub-shapes.ttl:29-30` | `sh:targetClass iladub:CandidateConcept` + `sh:path iladub:status ; sh:hasValue iladub:proposed` — **the membrane REQUIRES every candidate to carry `status proposed`**, promoted or not |
| `vocab/ontology/iladub.ttl:128-129` | `iladub:reviews rdfs:subPropertyOf dec:consideredEvidence`, domain `iladub:PromotionDecision` |
| `tests/etkl/test_vacuity_registry.py:1-40` | the R87 vacuity guard's own two criteria (focus nodes / term reachability) and the measurement that forced criterion 2's wording. `holon:05`'s three vacuity hazards are the **derivation-side** analogue; this docstring is the prior art to cite, not re-derive |
| `src/iladub/feed.py:643` | **a third membrane raise site neither previous handoff names** — a bare `assert conforms` guarding the *grounding* graph. Erased by `python -O`; caught by `tests/test_concept_feed.py:349` |
| `src/iladub/etkl/compile.py:1115` | `graph = Graph()` — the datagrid-withdrawal rebind. "The graph at the raise site" is not always the object created at `:574` |
| `docs/holonic-interaction.md:154-155` | the *"Planned work (not done yet)"* bullet `holon:05` is scored against — it says *"from validation results"*, which is the wording § *The design finding* below turns on |

## Measurement 2 — the held-vs-promoted discriminator: ANSWERED

This was the previous handoff's target #2 and it blocked decision 2's query. Full agent report is
not reproduced; the load-bearing results, each re-runnable:

**The discriminator is `iladub:reviews`, negated:**

```sparql
?c a iladub:CandidateConcept .
FILTER NOT EXISTS { ?pd a iladub:PromotionDecision ; iladub:reviews ?c }
```

**Three patterns that do NOT discriminate, all measured:**

1. **`iladub:status`** — two values repo-wide (`proposed`/`asserted`) as the previous handoff said,
   but the reason it cannot discriminate is stronger than "promote.py also writes proposed":
   `iladub-shapes.ttl:29-30` **mandates** `status proposed` on every `iladub:CandidateConcept`.
   A promoted candidate that dropped it would be refused by the membrane. Measured: 552/552
   candidates carry `proposed`. (`iladub:rejected` is declared at `vocab/ontology/iladub.ttl:44`
   and **written nowhere**.)
2. **`iladub:wasPromotedBy` / `iladub:GroundedNode`** — written only at `src/iladub/ground.py:175-176`
   and `src/iladub/splitkey.py:192-193`. **All three `promote.py` promotions mint neither**, so this
   pattern silently misses them.
3. **`dec:consideredEvidence`** — entailed from `iladub:reviews` under RDFS *and* written directly at
   `promote.py:81,128,172` pointing at **regions**, and at `decisionlog.py:68` at arbitrary evidence.

**Measured partition** — `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` p0, the recipe of
`tests/test_corpus_stem.py:44-54` (`compile_tables` → `ground_document`, `FakeGroundingProposer`
abstaining), ~15s:

```
total candidates 552  =  HELD 385  +  PROMOTED 167
status distribution: proposed 552 / asserted 167   ← status partitions nothing
FeedResult.proposed == 385                          ← independent confirmation
```

**Both held-candidate families are reachable on real documents.** (a) grounding-portal quarantine —
the 385 above, and `tests/corpus-manifest.ttl:44` records *"567 promoted / 1194 quarantined"* for the
full document. (b) region escalation — `corpus/health/who-wfa-boys-zscore-0-5.pdf` p0,
`compile_tables` alone (~15s, no contract): **1 held candidate** (`MATRIX_AMBIGUOUS`, conf 0.4),
**0 `PromotionDecision`s** in the graph; consistent with `tests/corpus-manifest.ttl:129`.

**A trap the spec must state.** `escalate_region`'s `cand_uri` and `decisionlog.BandRecorder`'s
`_regarding` region URI are **the same IRI**, so a *held* candidate was measured carrying **five
incoming `dec:regarding` edges** from decision holons. Being the object of a decision-holon edge
therefore proves nothing about promotion — only `iladub:reviews` from an `iladub:PromotionDecision`
does. Keep the `?pd a iladub:PromotionDecision` type clause: it is currently redundant (all five
`iladub:reviews` writers type their `pd` on the adjacent line) but it is the guard against exactly
this collision.

**MEASURED but not graph-level:** no single graph was produced in which `promote.py`-family
promotions and `escalate_region` candidates coexist — the stem p0 *compile* graph held **0**
candidates, and the 385/167 partition is measured only on the `ground.py` family. The extension to
`promote.py` rests on an exhaustive census of `iladub:reviews` write sites (all five point at a
locally-minted `BNode`; `escalate_region` emits outgoing triples only), which is a **code-level**
argument. The plan should produce the mixed graph.

## The design finding this session adds — `Compromised` is NOT derivable by an AXIOM

The previous handoff's § *The design as it stood*, section 3, proposes *"an AXIOM in
`vocab/queries/membrane-health.rq`, `CONSTRUCT` over the compiled evidence graph."* **That cannot
derive `Compromised`, and it cannot derive `Intact` either** — for the same reason. Non-conformance
is not a fact the evidence graph supports; it is the **membrane's verdict**, computed outside the
graph by pySHACL/rudof and discarded. A `CONSTRUCT` over the compiled graph can see held candidates;
it cannot see whether validation passed. Deriving `Intact` from the *absence* of a violation the
graph never records is inference-by-absence — forbidden by the gate's own words (*"never inferred
from absence"*) and by principle 7.

**The shape that satisfies the gate** — proposed, NOT decided, and the first thing the adversarial
review should attack:

1. **PROCEDURAL** — the membrane emits its verdict as a typed RDF fact into the graph after
   validating (raw extraction: an external engine's output → typed RDF; the irreducibility argument
   is that the verdict is not in the source at all). **Measurement 3 makes this one triple emitted
   from a boolean already in scope** — `conforms` at `compile.py:1171` / `document.py:1624` — so no
   report graph, no engine change, no `_deskolemize` decision. Candidate encoding: a node typed
   `sh:ValidationReport` carrying `sh:conforms true|false`, which needs **no new vocabulary** —
   `sh:` is W3C's, and § Source ownership constrains HGA terms, not SHACL's. Precedent for reading
   that exact pattern already exists at `tests/etkl/test_membrane.py:269-273`; precedent for
   *minting* it into a compiled graph does **not** (exhaustive grep for
   `ValidationReport|sh:conforms|shacl#conforms` over `src/ vocab/ tests/` returns only those lines).
2. **AXIOM** — one `CONSTRUCT` over verdict-fact × held-candidate evidence yields all three values
   through one code path: `conforms=false → Compromised`; `conforms=true` ∧ held → `Weakened`;
   `conforms=true` ∧ no held → `Intact`.

Three things this shape buys, which is why it is worth attacking rather than dismissing:

- **The skip guard falls out for free.** `compile.py:1167-1170` skips validation for a page with no
  `tab:RecordTable`/`tab:HierarchicalTable`; no validation means no verdict fact, means the
  `CONSTRUCT`'s `WHERE` has no support, means **no health triple** — absence, never a fourth state,
  by the open-world rule rather than by a special case. The previous handoff's section 4 asked for
  exactly this behaviour and had to state it as a rule; here it is a consequence.
- **`Compromised` at the raise site stops being a special path.** Mint the verdict fact, run the one
  `CONSTRUCT`, attach the graph to the error, raise. Same query, same code, third value.
- **The `_deskolemize` question shrinks.** `sh:conforms` is one boolean read off the report; only a
  design that carries *result nodes* into the graph has to decide where de-skolemization happens.

**The `Intact`-reachability hazard this exposes, and it is new.** With `Weakened` derived from held
candidates, `Intact` requires a document with **zero** held candidates. Measured: stem p0's *compile*
graph has 0 candidates → `Intact` is reachable at page scope. **At document scope it is unmeasured**,
and `ground.py:102` emits a candidate for *every* concept before the grounded/proposed branch — so
any document that grounds anything at all carries candidate nodes, and whether any real document
leaves none of them held is exactly the question. If none does, the vacuity has merely moved from
`Weakened` to `Intact`. **Measure this before writing the query.**

**And one scope question the previous handoff never raised.** The 385 held candidates live in the
**ground graph** produced by `ground_document`, a step separate from `compile_tables`/
`compile_document`. Which graph the health signal attaches to, and whether that graph contains the
candidates the derivation joins on, is **unmeasured**. A derivation that reads held candidates out of
a graph the compiler never merges them into is vacuous by construction — the R87 class again.

## Measurement 1 — the `sh:closed` question: ANSWERED, **decision 1 survives**

This was the one measurement that could kill the chosen subject outright. **It cannot.** Minting
`<docURI> a etkl:CleanDocumentHolon` + `<docURI> etkl:membraneHealth …` changes no verdict the
membrane produces today. Four independent reasons, each re-runnable:

1. **There is no `sh:closed` in the repo at all.** `grep -rn "sh:closed\|shacl#closed" .
   --exclude-dir=.venv --exclude-dir=.git` returns **four hits, all prose in `.md`** (this repo's
   `CLAUDE.md:121`, and the previous handoff asking the question). Zero in any `.ttl`.
2. **No loaded shape names any `etkl:` term.** The membrane loads exactly five shapes files —
   `tab-shapes.ttl` + `tab-physical-shapes.ttl` (leg `tab`), `dec-shapes.ttl` + `iladub-shapes.ttl` +
   `escalation-shapes.ttl` (leg `dec`), assembled at `src/iladub/etkl/compile.py:398,421,431-439`
   (`_build_membrane`, `:424`) — and a single grep for
   `sh:closed|sh:targetNode|sh:target \[|sh:ignoredProperties|sh:nodeKind|etkl:` across all five
   **returns nothing**. `sh:targetObjectsOf` is **zero** in the loaded set (the repo's only two are
   in `governance-shapes.ttl:28,46`, which no membrane loads). The four `sh:targetSubjectsOf`
   predicates are `tab:hasHeaderNode`, `tab:continuesColumn`, `tab:licenceRefused`,
   `tab:inLogicalColumn` — `etkl:membraneHealth` is none of them.
3. **`etkl-holons.ttl` is not in the ontology graph.** `_FULL_ONT` is exactly `tab.ttl` + `dec.ttl` +
   `iladub.ttl` (`compile.py:441,452,453`, assigned `:501`); `etkl-holons.ttl` is referenced nowhere
   in `src/`. And **inference is off**: `membrane.py:124-125` passes `inference="none"`; the seam
   materialises only `rdfs:subClassOf` type closure from the ont graph (`membrane.subclass_closure`),
   so `etkl:membraneHealth`'s `rdfs:domain` would type nothing even if the file were loaded.
4. **Measured differentially on real compiled graphs** — page scope and document scope, both legs,
   both engines (rudof default and `engine="pyshacl"`), on `graincorp-capacity-2026-08-04.pdf`
   and on `apple-fy2026q3-statements.pdf` p1 with `datagrid_adopt=True`: `conforms=True results=0`
   before and after, `IDENTICAL VERDICTS: True`, and the subclass-closure delta is **exactly the
   added triples, no inferred supertype**. The counterfactual — `etkl-holons.ttl` forced into
   `_FULL_ONT` — adds only `a etkl:DocumentHolon`, which no shape targets, and both legs still
   conform.

**Two corrections this produced, both worth carrying:**

- **The premise "the doc URI is an object of `prov:wasDerivedFrom`" is only sometimes true.** On
  graincorp-capacity at both scopes the doc URI is the object of **`dcterms:isPartOf`**
  (`decisionlog.py:100`); `prov:wasDerivedFrom <docURI>` appears on the **datagrid** path
  (`datagrid.py:627,749`, 4 occurrences on apple p1) and from `escalate_region`
  (`holon.py:463`, and only when a region escalates). Both were tested; both are inert. The
  *"zero subject triples today"* half of the premise held in every run.
- **The one shape that mentions `prov:wasDerivedFrom` is inert by construction**:
  `tab:DerivedRowGroupShape` (`vocab/shapes/tab-shapes.ttl:335-346`) is a property shape on the
  *subject* with `sh:minCount/maxCount` only — no `sh:class`, `sh:node`, or `sh:nodeKind` on that
  path, so the object's type is never inspected. The entire loaded shape set contains exactly one
  `sh:class` (`tab-physical-shapes.ttl:19`).

**Two guards the spec should still name**, because they are the ways a *variant* of decision 1 could
break what this measurement clears: `membrane.audit_literals` (`membrane.py:214+`) inspects typed
`Literal` objects, so a health signal carried as a **typed literal** rather than an IRI would reach
it; and `ESCALATION_FURNISH_RQ` runs over the doc graph *before* the document membrane
(`document.py:1609`) — read in full, it binds none of the holon-health terms and has no
unbound-predicate wildcard, so it is inert, but it is the pre-validation derivation a future variant
would have to re-check.

**Not exhaustive over the corpus**: three runs, not all seven documents. The argument that the
result is document-independent rests on (1)–(3) above being global facts; the cheapest belt-and-braces
check is the 7-document loop in the style of `compile.py:455-500`'s R103 protocol.

**And § The design finding softens the question further**: health triples minted *after* validation
are never themselves validated. It does not vanish — a returned graph re-validated downstream or by a
test would see them, and this measurement is what says that is safe.

## Measurement 3 — raise site, catchers, `.rq` conventions: ANSWERED

**The catcher claim is CONFIRMED — and it was stated over the wrong set of raise sites.**
`grep -rn "except AssertionError" src/ tests/ scripts/ demo/ examples/` returns exactly
`tests/test_corpus.py:129`, which re-raises at `:130`; there is **no bare `except:` anywhere**, no
`BaseException`, no `contextlib.suppress`, and every other `except Exception` was individually
checked and cannot see a compile (`scripts/cockpit.py:125,411,421,431`, `membrane.py:171`,
`test_vacuity_registry.py:274`, `test_source_ownership.py:67`). 168 `compile_document`/
`compile_tables` call sites across 53 files, and `tests/test_corpus.py:127-135` is the only `try`.

**But there is a THIRD membrane raise site neither handoff names — `src/iladub/feed.py:643`:**

```python
assert conforms, f"grounded graph violates the promotion membrane:\n{report}"
```

It is a **bare `assert`**, so `git grep "raise AssertionError" -- src/` (which returns only
`compile.py:1173` and `document.py:1626`) misses it; `git grep "^\s*assert " -- 'src/*'` returns this
one line and nothing else in `src/`. It is caught by `tests/test_concept_feed.py:349`. Two
consequences for decision 3: the **grounding** membrane refuses too — and that is the membrane whose
graph holds the held candidates `Weakened` is derived from — and **`python -O` erases this assert
while leaving the two `raise AssertionError` sites intact**. If `Compromised` is to be minted
uniformly wherever a membrane refuses, that asymmetry is a design question, not an implementation
detail.

**The raise sites carry a graph today: no.** Both raise a bare `AssertionError` with a single
string arg — `f"{subject} failed {', '.join(legs)}: SHACL:\n{text}"` (`compile.py:528-535`). In both
functions the local `graph` at the raise **is the identical object that would otherwise be
returned** (`compile.py:1171` vs `:1175`; `document.py:1624` vs `:1636`).

**The trap in that sentence, measured:** `compile_tables` **rebinds** `graph = Graph()` mid-function
on the datagrid-adoption withdrawal path (`compile.py:1115`). Anything holding a reference captured
earlier — e.g. `ReadingRecorder(graph, …)` at `compile.py:576` — is holding the *old* object on that
path. `document.py:1609` uses in-place `+=`, so identity is preserved there. **Any plan that mints
into "the graph" must say which object, at which line.**

**`CompilationReport` is constructed POSITIONALLY** at `compile.py:1175` (fields at `:363`;
`DocumentReport` at `document.py:236-247` is constructed by keyword at `:1636-1639`). Adding a field
to `CompilationReport` is order-sensitive — this is exactly the R73 defect-3 trap. Also:
`compile_document` is **not** exported from `src/iladub/etkl/__init__.py`; `compile_tables` and
`CompilationReport` are (`:13,32`).

### The skip guard fires on 59% of corpus pages — and it does not bite decision 1

Measured over all 27 corpus pages (per-page standalone compile, `validate_shapes=False`, then the
guard's own condition evaluated on the returned graph; 0 crashes):

```
TOTAL pages=27  validates=11  skips=16      → 59% of pages skip page-scope validation
```

**This is a PAGE-scope guard, and decision 1 puts health at DOCUMENT scope only** — `document.py:1623`
gates on `validate_shapes` alone. So the previous handoff's "fourth vacuity hazard" does not reach
the chosen subject. *(Caveat: the 16/27 is the plain page path; inside `compile_document` a page may
be re-compiled with `carried_header_roles` / `section_repair_bands` / `datagrid_adopt=True`, which can
change whether a `RecordTable` gets typed.)*

**It is replaced by a sharper, UNMEASURED one.** Document scope selects legs via
`_legs_for_document(recognized, section_facts)` (`document.py:1624`). **What `_validate` returns when
that tuple is empty is unmeasured** — if it returns `conforms=True` over zero shapes, an `Intact`
derived from it claims conformance from zero focus nodes, which is **R106 exactly**. Measure this
before writing the query; it is now the sharpest vacuity hazard on the criterion.

### The verdict does NOT need report-graph plumbing — § The design finding gets simpler

Confirmed as the previous handoff suspected: `membrane.validate` returns `(bool, str)`
(`membrane.py:45-46,108`); the pySHACL leg discards the report graph into `_` (`:124-126`); the rudof
leg parses its Turtle report into a `Graph` only to read `sh:conforms` and drops it (`:159-174`,
failing **closed** on an unparseable report); `_deskolemize` operates on the report **string**
(`:297-315`, and its docstring says why: the two engines' reports are different kinds of document —
rudof's Turtle, pySHACL's **prose**).

**That last fact kills the report-graph route and rescues the design finding.** pySHACL's `text` is
prose, so there is no engine-independent structured report to mint from. But **there does not need to
be**: the conformance verdict is already a plain Python `bool` in scope at both raise sites
(`conforms, text, legs = _validate(graph)`). Minting it as an RDF fact needs **no** report graph, no
engine change, and no `_deskolemize` decision at all. The PROCEDURAL step shrinks to one triple
emitted from a boolean the code already holds — which is a far easier irreducibility argument to
write than "widen the seam".

### `.rq` conventions the spec must conform to

45 files (15 `CONSTRUCT`, 27 `SELECT`, 3 `ASK` — form follows the job). Bare SPARQL `PREFIX` lines
after a `#` header, full IRIs, no `BASE`, no `prepareQuery`. `CONSTRUCT`s run through
`interpret.run(query_path, *graphs)` (`src/iladub/etkl/interpret.py:19-30`, whose own docstring
classifies it as PROCEDURAL engine glue); `SELECT`/`ASK` go to `graph.query(text, initBindings=…)`
at the call site.

Three conventions that are **enforced or load-bearing**, not decorative:

- **`# GATE (CLAUDE.md §8):` header** — 20 of 45 carry an explicit gate classification, 16 under a
  labelled heading. Canonical form at `vocab/queries/escalation-furnish.rq:10-12`. Any holon-scoped
  `FILTER NOT EXISTS` is justified **inline** as holon-scoped (`escalation-furnish.rq:44-47`) — which
  is exactly what the `iladub:reviews` negation will need.
- **No bare decimal literal in any query body — LINTED.** `tests/etkl/test_transform_gate.py:26-31`
  globs `vocab/queries/*.rq`, strips comments, and fails on any float. This is the §8 tuned-constant
  gate in executable form. (There is **no** test that merely parses every `.rq`.)
- **The header names the test that pins each claim** (`escalation-furnish.rq:31,34`), and the test is
  written against a **hand-computed fixture** (`tests/test_arc_queries.py:1-42` states the rule).
  A new `.rq` shipping without a fixture-based oracle and a gate header is out of line with the 20
  most recent files.

`sh:severity` re-confirmed at **zero** including the expanded IRIs
(`git grep -n "shacl#Warning\|shacl#Info\|shacl#Violation\|shacl#severity"` → exit 1) — every hit for
"severity" in the tree is `risk:severity`/`dec:maxSeverity`, a different namespace. Every violation
the membrane can produce is `sh:Violation` by default, which is why decision 2 exists.

## What was decided, and where

**Nothing was decided this session.** Decisions 1–3 remain as recorded in
`docs/superpowers/2026-08-25-holon-05-design-decisions.md` § *What was decided* — recorded **there
and nowhere else**, hence reversible. § *The design finding* above is a **proposal**, recorded here
and nowhere else, and it has not been reviewed by anyone.

## Unverified or assumed

- **The full suite is GREEN** — `.venv/bin/python -m pytest -q` on the branch tip (docs-only commits
  above `main` @ `20a5b0e`): `1312 passed, 7 skipped, 1 xfailed, 10 warnings in 2386.82s (0:39:46)`,
  exit 0. This is the baseline §8 item 7 measures against, and it ends the two-session gap in which
  `main`'s green state was unverified. Note `--timeout` is not a valid flag (`pytest-timeout` is not
  installed), and the 40-minute wall time was inflated by concurrent corpus sweeps.
- **All three of the previous handoff's blocking measurements are now ANSWERED** — but they raised
  four new unmeasured questions, and these are what the next session must run first:
  1. **What `compile._validate` returns when `_legs_for_document(...)` selects ZERO legs**
     (`document.py:1624`). If `conforms=True` over zero shapes, `Intact` claims conformance from zero
     focus nodes — **R106 exactly**, and now the sharpest hazard on the criterion.
  2. **`Intact` reachability at document scope** — is there any real document with zero *held*
     candidates? `ground.py:102` emits a candidate for every concept before the branch, so if none
     leaves zero held, the vacuity has merely moved from `Weakened` to `Intact`.
  3. **Which graph carries the candidates the derivation joins on** — the 385 held candidates live in
     the `ground_document` graph, a step separate from `compile_document`. A derivation reading them
     out of a graph the compiler never merges them into is vacuous by construction (the R87 class).
  4. **Whether `feed.py:643`'s grounding-membrane refusal is in scope for `Compromised`** — it is a
     third raise site, it is the membrane guarding the very graph `Weakened` reads, and `python -O`
     erases it.
- **The mixed graph** (`promote.py` promotions + `escalate_region` candidates in one graph) was
  never produced; the discriminator's coverage of the `promote.py` family is a code-level argument.
- **Register tally re-counted 2026-08-25: 24 closed / 116 rows** (`grep -oE "^\| (~~)?R[0-9]+(~~)? \|"`
  over `residues.md`; `residues-open.md` 92 + `residues-closed.md` 24). The previous handoff's
  "24 closed / 91 open" was stale by one. A new row raised now records `(24/116 closed)`.
- **`etkl:Weakened`'s `rdfs:comment` still reads *"Interior conforms but warnings are present"***
  (`vocab/ontology/etkl-holons.ttl:81`), so decision 2 does require the published-vocabulary
  amendment, and `sh:severity` is still absent repo-wide — which is *why* the severity reading is
  unreachable and the held-candidate reading was chosen.
- **The falsifying oracle (previous handoff's section 6) has still never been attacked.** One attack
  is recorded here and is not the review: *"byte-identical re-derivation"* is a category error — RDF
  has no byte identity without canonicalisation, and if the compiler mints by running the same
  `.rq`, strip-and-re-derive compares `f(g)` with `f(g)` and pins determinism, not correctness. It is
  a **not-a-stored-label** check, and the spec should demote it to that and carry a **discrimination**
  oracle (three documents → three different values) as the falsifying one.

## The next concrete action

**The spec is written.** Next: the **adversarial review on the spec, before any plan**, in a fresh
session — a standing requirement since 2026-08-24 and still never run as a named step. Three targets,
because each can still change the design rather than refine it:

1. **§4.2's verdict fact** — is emitting `sh:conforms` into the evidence graph really PROCEDURAL raw
   extraction, or is it a stored label wearing a fact's clothes? O5 is the spec's answer; attack it.
2. **§5.6** — the discriminator is correct and cannot fire on any corpus document. The spec keeps it
   and makes O3 fixture-only. Is that the right call, or should the loop wire a proposer so the
   clause is exercised on real input?
3. **§4.5's `MembraneRefusal`** — a subclass keeps the one measured catcher working, but it makes
   what the error carries part of an interface. Re-run the catcher census first.
