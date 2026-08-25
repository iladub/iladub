# The membrane reports its health — closing `holon:05`

**Date:** 2026-08-25 · **Criterion:** `prog:criterion:holon:05` (`tests/arc-manifest.ttl:346-359`) ·
**Rung:** `holon` 4/6 → 5/6 · **Branch:** `holon-05-measurements`

**Doc impact: increment.** Two published surfaces change: `etkl:Weakened`'s `rdfs:comment` in
`vocab/ontology/etkl-holons.ttl:81-82` (a **semantic** amendment to a published term — see §4.6, and
bump `owl:versionInfo` `0.1.0` → `0.2.0` at `:33`), and `docs/holonic-interaction.md:154-155`, whose
first *"Planned work (not done yet)"* bullet is the sentence this loop makes true. Queue both for the
next release; neither blocks the loop.

**Evidence this spec is written from:** `docs/superpowers/2026-08-25-holon-05-measurements.md`
(three blocking measurements, all answered) and `docs/superpowers/2026-08-25-holon-05-design-decisions.md`
(decisions 1–3). §2 states each load-bearing fact **once**; every later section cites §2.x rather
than re-deriving it (CLAUDE.md § Plan authoring discipline, rule 6).

---

## §1 The question

`holon:05` asks for *"a membrane-health check that computes and reports a compiled document's
cleanliness (`etkl:membraneHealth` → Intact / Weakened / Compromised) **from validation results**"*
(`docs/holonic-interaction.md:160-161`, quoted by the criterion's `prog:statement`).

The vocabulary has existed since 2026-06-23 and **nothing derives it**
(`tests/arc-manifest.ttl:344-345`, that manifest's own grep). The question is not "can we write the
triple" — it is:

> **Can all three values be *derived*, from evidence that is actually present, without any of them
> being unreachable by construction?**

Three vacuity hazards stack on this criterion; a fourth was found writing this spec and then
measured away (§5.4). A
three-valued property with unmintable values is the R106 class the arc manifest was already caught
by once. §5 answers each one; §7 pins each answer with an oracle.

---

## §2 What is measured before anything is designed

Each fact is stated once, here, with its evidence. Full commands and raw output are in
`docs/superpowers/2026-08-25-holon-05-measurements.md`.

### §2.1 The subject can be minted safely — decision 1 survives

`<docURI> a etkl:CleanDocumentHolon` + `<docURI> etkl:membraneHealth …` changes **no** verdict the
membrane produces. Four independent reasons: there is **no `sh:closed` in any `.ttl` in the repo**;
**no loaded shape names any `etkl:` term** (the five loaded files are `tab-shapes.ttl`,
`tab-physical-shapes.ttl`, `dec-shapes.ttl`, `iladub-shapes.ttl`, `escalation-shapes.ttl`, assembled
at `src/iladub/etkl/compile.py:398,421,431-439`); `etkl-holons.ttl` is **not** in `_FULL_ONT`
(`compile.py:441,452,453`); and inference is **off** (`membrane.py:124-125`, `inference="none"`).
Measured differentially on real compiled graphs — page and document scope, both legs, both engines —
`IDENTICAL VERDICTS: True`, closure delta exactly the added triples.

### §2.2 The held-vs-promoted discriminator is `iladub:reviews`, negated

```sparql
?c a iladub:CandidateConcept .
FILTER NOT EXISTS { ?pd a iladub:PromotionDecision ; iladub:reviews ?c }
```

Three patterns that do **not** discriminate: `iladub:status` (the membrane **mandates**
`status proposed` on every candidate — `vocab/shapes/iladub-shapes.ttl:29-30` — so a promoted
candidate that dropped it would be refused); `iladub:wasPromotedBy`/`iladub:GroundedNode` (written
only at `ground.py:175-176`, `splitkey.py:192-193` — **all three `promote.py` promotions mint
neither**); `dec:consideredEvidence` (entailed from `iladub:reviews` via
`vocab/ontology/iladub.ttl:128`, and written directly at `promote.py:81,128,172` pointing at
*regions*). Measured partition on a real document: **552 candidates = 385 held + 167 promoted**;
status partitions nothing (552 `proposed`).

**The collision that forces the type clause:** `escalate_region`'s `cand_uri` and
`decisionlog.BandRecorder`'s `_regarding` region URI are the **same IRI**, so a *held* candidate was
measured carrying five incoming `dec:regarding` edges. Being the object of a decision-holon edge
proves nothing about promotion; only `iladub:reviews` from an `iladub:PromotionDecision` does.

### §2.3 The verdict is a `bool` already in scope — no report-graph plumbing

`membrane.validate` returns `(bool, str)` (`membrane.py:45-46,108`); the pySHACL leg discards the
report graph into `_` (`:124-126`) and its `text` is **prose**, not Turtle; the rudof leg parses its
Turtle report only to read `sh:conforms` and drops the graph (`:159-174`); `_deskolemize` operates on
the report **string** and says why (`:297-315`: the two engines' reports are different kinds of
document).

**There is therefore no engine-independent structured report — and none is needed.** Both raise sites
already hold the verdict as a plain Python `bool`: `conforms, text, legs = _validate(graph)` at
`compile.py:1171` and `document.py:1624`.

### §2.4 The raise sites, the catchers, and the graph identity

Both sites raise a bare `AssertionError` with one string arg
(`compile.py:1173`, `document.py:1626`; message built at `compile.py:528-535`) and attach **no**
graph. In both functions the local `graph` at the raise **is** the object that would otherwise be
returned (`compile.py:1171`/`:1175`; `document.py:1624`/`:1636`).

**Exhaustively, `tests/test_corpus.py:129` is the only `except AssertionError` in the tree and it
re-raises at `:130`** — no bare `except:`, no `BaseException`, no `suppress`, and every other
`except Exception` was individually checked and cannot see a compile. 168 call sites across 53 files;
one `try`.

**A third membrane raise exists — `src/iladub/feed.py:643`**, a bare `assert conforms` guarding the
*grounding* graph, invisible to `grep "raise AssertionError"` and erased by `python -O`. §9 scopes it
out, and §4.4 explains why that is principled rather than expedient.

**Two traps:** `compile_tables` **rebinds** `graph = Graph()` on the datagrid-withdrawal path
(`compile.py:1115`), so "the graph at the raise site" is not always the object created at `:574`; and
`CompilationReport` is constructed **positionally** at `compile.py:1175` (fields at `:363`), the R73
defect-3 trap.

### §2.5 `sh:severity` is absent, which is why decision 2 exists

Zero `sh:severity`/`sh:Warning`/`sh:Info` anywhere, including the expanded IRIs
(`git grep "shacl#Warning\|shacl#Info\|shacl#Violation\|shacl#severity"` → exit 1). Every violation
the membrane can produce is `sh:Violation` by default. **`etkl:Weakened` as published — "Interior
conforms but warnings are present" (`etkl-holons.ttl:81-82`) — is underivable**, and that is the
finding that forces §4.6.

### §2.6 The skip guard is page-scope; the document-scope hazard is different

`compile.py:1167-1170` skips validation for a page with no `tab:RecordTable`/`tab:HierarchicalTable`
— **16 of 27 corpus pages (59%)**. Document scope gates on `validate_shapes` alone
(`document.py:1623`) and selects legs via `_legs_for_document(recognized, section_facts)`. Because
§4.1 puts health at **document scope only**, the page-scope guard does not reach the signal. The
zero-legs question that *could* have reached it is §5.4, where it is refuted.

### §2.7 `.rq` conventions this spec must conform to

45 files under `vocab/queries/`. Three enforced or load-bearing conventions: a
`# GATE (CLAUDE.md §8):` header with the classification (20 of 45; canonical form at
`escalation-furnish.rq:10-12`), with any `FILTER NOT EXISTS` justified **inline** as holon-scoped
(`escalation-furnish.rq:44-47`); **no bare decimal literal in any query body, LINTED** by
`tests/etkl/test_transform_gate.py:26-31`; and a header that **names the test pinning each claim**
(`escalation-furnish.rq:31,34`), the test being written against a **hand-computed fixture**
(`tests/test_arc_queries.py:1-42`). `CONSTRUCT`s execute through
`interpret.run(query_path, *graphs)` (`src/iladub/etkl/interpret.py:19-30`).

---

## §3 What proposes, what disposes, and why they are independent

**Proposes:** `vocab/queries/membrane-health.rq` — a `CONSTRUCT` that reads two kinds of evidence
already in the compiled graph (the verdict fact of §4.2, the held candidates of §2.2) and states the
health value that follows.

**Disposes:** `tests/etkl/test_membrane_health.py`, whose expected values are **hand-computed against
fixtures built by hand**, per §2.7 — never by running the query and recording what it said.

**Why they are independent, and the trap this avoids.** The oracle the previous handoff proposed —
*strip the health triple, re-run the `.rq`, assert byte-identical re-derivation* — is **not** a
disposer of the proposer. If the compiler mints by running that same query, strip-and-re-derive
compares `f(g)` with `f(g)`: it pins determinism, not correctness, and it is the R73 defect-5 shape
(a test whose subject could be wrong in exactly the way the test cannot see). *"Byte-identical"* is
also a category error — RDF has no byte identity without canonicalisation.

That check is **kept and demoted**: it is the *not-a-stored-label* check (§7 O5), which is a real and
different claim. **The falsifying oracle is discrimination** (§7 O1): three graph states that must
yield three *different* values, each expected value computed by hand from the fixture.

---

## §4 The design

### §4.1 The subject and the scope

The document URI is typed `etkl:CleanDocumentHolon` — the concrete class — so the health triple sits
inside `etkl:membraneHealth`'s declared `rdfs:domain` (`etkl-holons.ttl:88`) with no exception to
justify, and `etkl:DocumentHolon`'s own comment declares itself abstract (`:44`). Safe by §2.1.

**Document scope only.** Page-scope graphs (`{_DOC}/p{n}`) get no health triple, so a document's
signal is unambiguous. The Raw holon and the portal are `holon:06`; this loop does not touch them.

This is the first instance data the `etkl` doc-holon fabric has ever had — **it closes the
instantiation half of `R126`** (0 of 326 triples had the doc URI as a subject; 0 of 11 `rdf:type`
values were `etkl:`).

### §4.2 The verdict fact — PROCEDURAL

Immediately after `_validate` returns at document scope, and **before** either returning or raising,
mint into `graph`:

```
<{doc}#membrane-report> a sh:ValidationReport ;
    sh:conforms "true"^^xsd:boolean ;      # or false
    prov:wasDerivedFrom <{doc}> .
```

- **Why PROCEDURAL, and why it is irreducible** (CLAUDE.md §8 requires this in the code *and* the
  spec): the conformance verdict is not in the source document and not derivable from the evidence
  graph — it is the output of an external validation engine. Emitting an engine's output as typed
  RDF is *raw extraction*, the one thing §8 reserves PROCEDURAL for. It is **one triple-group from a
  boolean already in scope** (§2.3): no engine change, no report graph, no `_deskolemize` decision.
- **No new vocabulary.** `sh:` is W3C's; § Source ownership constrains HGA terms, and the subject
  here is an IRI we mint. Precedent for *reading* this pattern is `tests/etkl/test_membrane.py:269-273`;
  there is no precedent for minting it, so §7 O6 pins that it does not perturb anything.
- **Minted after validation, so never itself validated.** §2.1 is what makes that safe for a graph
  re-validated downstream.

### §4.3 The derivation — AXIOM

`vocab/queries/membrane-health.rq`, a `CONSTRUCT`, run through `interpret.run` (§2.7):

```sparql
CONSTRUCT { ?doc a etkl:CleanDocumentHolon ; etkl:membraneHealth ?health }
WHERE {
  ?report a sh:ValidationReport ; sh:conforms ?conforms ; prov:wasDerivedFrom ?doc .
  BIND(EXISTS { ?cand a iladub:CandidateConcept .
                FILTER NOT EXISTS { ?pd a iladub:PromotionDecision ; iladub:reviews ?cand } }
       AS ?held)
  BIND(IF(!?conforms, etkl:Compromised, IF(?held, etkl:Weakened, etkl:Intact)) AS ?health)
}
```

The implementer writes the file; the shape above is the contract, not the text. Four invariants it
must satisfy, each pinned in §7:

1. **Evidence-positive.** Every value is derived from evidence that is *present*: `Compromised` from
   a verdict fact saying `false`, `Weakened` from a candidate that exists, `Intact` from a verdict
   fact saying `true`. **`Intact` is never derived from the absence of a violation** — that
   violation is not in the graph, and inferring from its absence is what the gate forbids in its own
   words.
2. **Closed-world only within the holon.** The `FILTER NOT EXISTS` closes over `iladub:reviews`
   scoped to a bound `?cand`, and `EXISTS` closes over the graph. This is licensed by *"the holon is
   the closure boundary"* — and it imposes a **site constraint the query header must state**: the
   query is run over **one document's graph**, never a union of documents. This is the same kind of
   caller constraint `escalation-furnish.rq:48-49` already carries.
3. **Idempotent, and it never reads its own product.** No pattern in the `WHERE` mentions
   `etkl:membraneHealth` or `etkl:CleanDocumentHolon`, so re-running over a graph that already
   carries the health triple re-derives exactly it.
4. **No bare decimal literal** — trivially satisfied, and enforced by the lint of §2.7.

The `?pd a iladub:PromotionDecision` type clause **stays** even though it is currently redundant: it
is the guard against the IRI collision of §2.2.

### §4.4 Why held candidates are the right reading of `Weakened` — and why the grounding portal is not this membrane

The compiled graph **is** the CleanDocumentHolon's interior; the document membrane is what validates
it. A candidate concept sitting in that graph is a proposition **held at that membrane** — literally
the dotted *"held at the membrane"* edge in `docs/holonic-interaction.md:55`. That is what `Weakened`
now means: *the interior conforms, but not everything that reached the boundary crossed it.*

The grounding-portal quarantine (`ground.py`, the 385 of §2.2) lives in a **different** graph behind
a **different** membrane (`feed.py:643`). Excluding it is not a gap in coverage — it is the holon
boundary being respected. The portal's own health is `holon:06`.

**MEASURED, so this is not merely an argument.** `feed.py:643` lives in `ground_document`
(`feed.py:618-644`), whose `validate_shapes` **defaults to `False`**. No module under
`src/iladub/etkl/` imports `feed` at all — `grep -rn "import feed\|from .feed\|from iladub.feed" src/`
returns nothing — so `compile_document`/`compile_tables` cannot reach it; grounding is a step the
caller invokes afterwards, taking the compiled graph in and filling a **fresh** graph `g`.
`ground_document` returns a `FeedResult` of three ints (`feed.py:571-575,619`), not a graph, and
**no merge site between the two graphs exists anywhere** (exhaustive `+=` and add-loop greps over
`src/ tests/ scripts/` → no hits; corroborating
`docs/superpowers/2026-08-15-r87-ruling-handoff.md:73`).

**The compile graph and the grounded graph are disjoint artifacts.** The candidates the derivation
reads are therefore exactly the region-escalation family (`holon.py:451-467`, and the cell-level
`ROUND_TRIP_FAIL` emitter at `holon.py:82-105`) — which is the correct population for *this*
membrane, and the reason §4.3's graph-scoped `EXISTS` is sound rather than over-capturing.

### §4.5 Where health is minted — three sites, one query

| site | verdict | what happens |
| --- | --- | --- |
| `document.py:1624`, conforming | `true` | mint verdict fact → run query → add result to `graph` → return `DocumentReport` |
| `document.py:1626`, refusing | `false` | mint verdict fact → run query → add result to `graph` → **raise, carrying the graph** |
| validation not run (`validate_shapes=False`) | — | **no verdict fact, therefore no health triple** |

The third row is the design's answer to the reachability rule, and it is a *consequence* rather than
a special case: no validation means no verdict fact means the `WHERE` has no support means no health
triple. **Absence, never a fourth state** — the open-world rule doing the work.

**The refusal carries the graph via a subclass, not a softened raise.** Introduce
`membrane.MembraneRefusal(AssertionError)` with `.graph` and `.legs`, and raise it at
`document.py:1626` in place of the bare `AssertionError`. Because it is a **subclass**, the one
measured catcher (§2.4) keeps working unchanged. The guard is **not** softened, downgraded, or made
conditional: CLAUDE.md § Producer-side guards licenses deleting a guard only when the membrane
provably validates every product of that producer, and here it demonstrably cannot — a refusing
product never becomes a returned `DocumentReport` at all. This is the opposite of the R102 pattern:
not a guard that looks redundant, but the only thing between a non-conforming graph and its caller.

**The seam this creates:** what the error carries is now part of an interface. The implementer must
**re-measure** the catcher census of §2.4 before wiring it — *"only catcher today"* is exactly the
claim `enumerating-before-claiming` exists to make you re-run.

### §4.6 The vocabulary amendment

`etkl:Weakened`'s `rdfs:comment` (`etkl-holons.ttl:81-82`) currently reads *"Interior conforms but
warnings are present."* By §2.5 that is **underivable** — there are no warnings, anywhere, by
construction. Amend it to state the held-proposition reading of §4.4, and bump `owl:versionInfo`.
This is vocabulary we own; it is also **published**, hence the Doc impact block.

### §4.7 The criterion

`tests/arc-manifest.ttl:346-359`: flip `prog:met false` → `true`, with the `met true` justified by
the measurement comment convention the file already uses; keep the pre-declared
`prog:oracleTest "tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health"`
**exactly as written** and make it exist; and **add `prog:oracleArtifact "vocab/queries/membrane-health.rq"`**,
which the criterion has never had.

---

## §5 The vacuity hazards, and how each is answered

| # | hazard | answer |
| --- | --- | --- |
| 1 | **`Weakened` unreachable** — no `sh:severity` anywhere (§2.5) | re-read as held propositions (§4.4), which are measured to exist on real documents |
| 2 | **The domain is uninstantiated** (`R126`) — nothing is ever an `etkl:` type | §4.1 mints the subject, safely per §2.1 |
| 3 | **`Compromised` unreachable** — a refusing membrane raises, so no report a caller can hold ever carries it | §4.5 mints *before* the raise and the error carries the graph |
| 4 | **`Intact` vacuous over zero shapes** — §5.4 | the query must not fire when nothing was validated |

### §5.4 The zero-legs hazard — MEASURED, and REFUTED

The fear was: if `_legs_for_document(recognized, section_facts)` (`document.py:1624`) can return an
empty tuple and `_validate` then reports `conforms=True` over zero shapes, an `Intact` derived from
it claims conformance from zero focus nodes — `R106` exactly. **It cannot.**

`_legs_for_document` is a one-line total function (`document.py:1142-1162`):

```python
return ("tab", "dec") if (recognized or section_facts) else ("dec",)
```

Two possible values, and **`"dec"` is unconditional** — that is R102's fix. The only leg that can be
dropped is `tab`. Pinned exhaustively over all four input combinations by
`tests/etkl/test_document_membrane_gate.py:22-33`, and called from nowhere else in `src/` or `tests/`.

And the empty case is not a silent pass anyway — it is a **loud latent crash**. `_validate`
(`compile.py:504-525`) reaches `verdicts[legs[0]][1]` at `:523`:

```
$ .venv/bin/python …/q1b.py
_validate(g, ()) RAISED: IndexError tuple index out of range
_validate(g, ("dec",)) -> (True, '@prefix sh: …sh:conforms true .\n', ())
```

**So `Intact` at document scope is always backed by at least the `dec` leg.** Measured on real input:
`graincorp-capacity` → `('dec',)` (`recognized=[] section_facts=False`); `who-wfa-boys` →
`('tab','dec')` (`recognized=[(1, 2)]`). Consistent with the R102 closure row
(`docs/superpowers/residues-closed.md:26`). Five of seven corpus documents are inferred from that row
rather than re-run (~320 s to close; the spy script is the cheapest path).

**Consequence for the design: none — §4.2 mints unconditionally at document scope**, and the
third row of §4.5's table is reached only by `validate_shapes=False`. **O4 keeps its `validate_shapes`
form and drops the zero-legs extension**; there is nothing there to pin.

*The residual is not a vacuity but a latent crash:* `_validate` on an empty legs tuple raises
`IndexError` rather than refusing or conforming. Unreachable today, guarded by one total function.
Worth a residue row, not a fix in this loop (§9).

### §5.5 `Intact` reachability

`Weakened` is measured reachable (`corpus/health/who-wfa-boys-zscore-0-5.pdf` p0: 1 held candidate,
0 `PromotionDecision`s). `Intact` requires a document whose compiled graph carries **zero held
candidates**; graincorp-stem p0's *compile* graph had 0 candidates, so it is reachable at page scope.
**At document scope it is being measured as this spec is written** — if no real document reaches it,
the vacuity has merely moved from `Weakened` to `Intact`, and §7 O2 is the oracle that says so out
loud rather than letting it pass.

---

## §6 Gate classification (CLAUDE.md §8)

| step | class | justification |
| --- | --- | --- |
| verdict fact (§4.2) | **PROCEDURAL** | raw extraction: an external engine's output → typed RDF. Not derivable from evidence; not a reading judgement. One triple-group from a boolean already in scope. Stated in the code and here, as §8 requires |
| health derivation (§4.3) | **AXIOM**, derivation form | `CONSTRUCT` over an RDF evidence graph, open world, evidence-positive, idempotent. Its one closed-world guard is holon-scoped and justified inline |
| `MembraneRefusal` + wiring (§4.5) | **PROCEDURAL** | exception plumbing; no decision is taken in it |

**No NEURAL step.** Nothing here is a perceptual or underdetermined reading judgement. **No tuned
constant appears anywhere in this design** — and the `.rq` lint of §2.7 enforces it mechanically.

---

## §7 The falsifying oracles

All in `tests/etkl/test_membrane_health.py`. Every one carries a `## FALSIFICATION` block: remove or
invert what it pins, show it **failing**, restore, show green. **No falsification evidence ⇒ the task
review fails.**

- **O1 — DISCRIMINATION (the falsifying oracle).** Three hand-built fixture graphs — conforming with
  no candidates, conforming with one held candidate, non-conforming — must yield **three different**
  values. Expected values computed by hand from the fixture, never by running the query first.
  *Falsify:* collapse the `IF` to a constant; O1 must fail.
- **O2 — REACHABILITY on real input.** Each of the three values is produced by at least one **real**
  execution path, not only by a fixture: `Intact` and `Weakened` from named corpus documents,
  `Compromised` from a forced non-conforming graph at the real raise site. This is the R87
  vacuity-registry question (*"can it fire at all"* — `tests/etkl/test_vacuity_registry.py:1-40`)
  asked of a derivation instead of a shape. **If a value cannot be produced from real input, this
  test fails and says which — it does not fall back to a fixture.**
- **O3 — PROMOTION IS NOT HELD.** A candidate reviewed by an `iladub:PromotionDecision` must not
  make a document `Weakened`. *Falsify:* delete the `FILTER NOT EXISTS`; O3 must fail. This is what
  pins §2.2's discriminator, and the reason O1 alone is not enough — a query that ignores promotion
  passes O1.
- **O4 — ABSENCE, NOT A FOURTH STATE.** A document compiled with `validate_shapes=False` carries
  **no** `etkl:membraneHealth` triple and **no** `etkl:CleanDocumentHolon` type. `validate_shapes`
  is the only route into this state — §5.4 refuted the zero-legs one. *Falsify:* mint the verdict
  fact unconditionally; O4 must fail.
- **O5 — NOT A STORED LABEL.** Strip the health triple and the type triple from a compiled graph,
  re-run the `.rq`, and assert the re-derived triples equal what was stripped, compared **as sets of
  triples** (not bytes — §3). This answers the stored-label objection and nothing else; it is
  explicitly **not** the falsifying oracle.
- **O6 — THE VERDICT FACT PERTURBS NOTHING.** Re-validating a graph that carries the health triples,
  the type triple and the report node yields the same verdict as before they were added, on both
  legs. This is §2.1 held as a regression rather than a one-off measurement, and it is what makes the
  minting of a `sh:ValidationReport` node safe (§4.2).
- **O7 — THE REFUSAL CARRIES THE GRAPH.** A forced non-conforming document raises
  `MembraneRefusal`; the raised object's `.graph` contains
  `<doc> etkl:membraneHealth etkl:Compromised`; and `except AssertionError` still catches it.
  *Falsify:* revert to a bare `AssertionError`; O7 must fail.

---

## §8 Definition of done

1. All seven oracles green, each with its falsification evidence.
2. `vocab/queries/membrane-health.rq` exists, with a `# GATE (CLAUDE.md §8):` header naming its
   classification, its holon-scoped-negation justification, its caller site constraint (§4.3.2), and
   **the test that pins each claim** (§2.7).
3. `tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health` exists under
   **exactly** the pre-declared name and is green.
4. `tests/arc-manifest.ttl` holon:05 flipped to `prog:met true` with its measurement comment, and
   carrying the new `prog:oracleArtifact` (§4.7).
5. `etkl:Weakened`'s comment amended, `owl:versionInfo` bumped (§4.6).
6. `docs/holonic-interaction.md:154-155` — the bullet moves out of *"Planned work"*.
7. **Full suite green**, run in the repo venv (`.venv/bin/python -m pytest -q`; note
   `pytest-timeout` is not installed, so `--timeout` is not a valid flag).
8. The residues this loop opens are appended to the register, each recording the tally snapshot at
   the moment it was raised — **`(24/116 closed)` as re-counted 2026-08-25**.

---

## §9 What this loop does NOT do

- **It does not give the grounding portal a health signal.** `feed.py:643`'s membrane guards a
  different graph behind a different boundary (§4.4), and `python -O` erases it. That is `holon:06`
  territory and a **residue this loop raises**, not a gap it leaves silently.
- **It does not give page-scope graphs health** (§4.1), and it does not touch the page-scope skip
  guard, which §2.6 measured at 16/27 pages but which cannot reach a document-scope signal.
- **It does not widen `membrane.validate`'s `(bool, str)` return, and it does not resolve where
  `_deskolemize` would run on a graph.** §2.3 makes both unnecessary; the design question the
  previous handoff named as unanalysed stays unanalysed **and unneeded**.
- **It does not score the `holon:05 → holon:01` proposed edge.** Adding `prog:oracleArtifact` (§4.7)
  may make the edge groundable — it was failing A1 and A2 — but measuring that is the arc
  instrument's job, not this loop's. Note it; do not act on it.
- **It does not fix the latent `IndexError`** in `_validate` on an empty legs tuple (§5.4) — unreachable today; a residue row, not a fix.
- **It does not add a fourth health value**, and it does not report health where nothing was
  validated (§4.5, O4).
- **It does not mint health at the page-scope raise site** (`compile.py:1173`), which keeps that
  site's bare `AssertionError` unchanged.

---

## §10 The seams the plan must MEASURE, not assume

Named per rule 3 — **which fact to measure, not the answer**:

1. **The five corpus documents whose legs tuple is inferred, not measured** (§5.4). The two that were
   run agree with the R102 closure row; the other five are read off that row. ~320 s to close.
2. **The catcher census, re-run** (§2.4, §4.5). `MembraneRefusal` changes an interface.
3. **Which object `graph` names at the raise site.** `compile.py:1115` rebinds it on one path
   (§2.4); `document.py:1609` uses in-place `+=`. Measure at `document.py:1624` specifically — do
   not carry the page-scope answer across.
4. **Whether `DocumentReport` construction is positional.** `CompilationReport` is
   (`compile.py:1175`); `DocumentReport` was measured as keyword (`document.py:1636-1639`). Re-check
   before adding anything to either.
5. **Whether any real document reaches `Intact` at document scope** (§5.5). O2 is the test; the plan
   must know the answer before it writes O2's expected values.
