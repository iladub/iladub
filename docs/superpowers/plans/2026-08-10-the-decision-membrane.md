# The decision membrane — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md` (read it first —
this plan implements it and does not restate its argument).

**Doc impact:** contradiction — inherited from the spec, and resolved by Task 8 Step 3.
`docs/wiki/concepts/promotion-decision.md:48-49` and `docs/wiki/concepts/decision-holon.md:26`
each assert that the membrane enforces the promotion invariant today; the spec §3 measures both
false. This plan's Task 7 makes them true and Task 8 edits them to name where enforcement
happens.

**Goal:** Make iladub's differentiator claim — every grounded node is the product of an
accountable `iladub:PromotionDecision` — an *enforced* fact about compiled and grounded
documents, by fixing the three producers that violate the shipped shapes and then applying those
shapes at both membranes.

**Architecture:** Three producer fixes (`escalate_region`, `emit_data_grid`, the promotion
emitters) that add only triples read off branches the code already takes, followed by two gate
changes (`compile._validate`, `ground_document`) that apply `dec-shapes.ttl` and
`iladub-shapes.ttl` through the existing `membrane.validate` seam. Producers first, corpus
measured green, gates last — wiring the gate first would turn every pre-existing violation into
a compile crash and conflate "the code is wrong" with "the shape overreaches."

**Tech Stack:** Python 3.12 (`./.venv/bin/python`), rdflib, pySHACL / pyrudof via
`src/iladub/etkl/membrane.py`, pytest. RDF authoring in Turtle.

---

## Global Constraints

Every task's requirements implicitly include this section. A violation is a **review failure**,
not a style note.

1. **NEUROSYMBOLIC-FIRST GATE (CLAUDE.md §8).** Every change in this plan is classified in the
   spec §5.0: the three producer fixes are **PROCEDURAL** (recording, in RDF, decisions the
   surrounding code has already made — `decisionlog.py`'s own classification, inherited on the
   same grounds); the two gate changes are **AXIOM / constraint → SHACL, closed world**. State
   the classification in the code comment you add, as the repo does elsewhere.
2. **NO TUNED CONSTANT, TOLERANCE, OR GEOMETRIC THRESHOLD may appear anywhere in this loop.**
   One appearing is prima facie evidence the decision belongs in AXIOM/NEURAL. There is no
   geometry in this work; if you find yourself writing a number that is not a count, an index,
   or a confidence already computed upstream, stop and report.
3. **THE OPTION SPACE HONESTY CONDITION.** Every `dec:optionSpace` member you emit must be a
   branch the code actually took or could have taken at that point. Inventing an option is a
   domain decision, which would invalidate the PROCEDURAL classification in constraint 1.
4. **NO STUB-TO-SATISFY (spec §5.6).** Every triple added must carry information a consumer can
   act on. A typed-but-empty node, a constant `rdfs:label`, an option whose
   `dec:rejectedBecause` is the same string every time — each turns a shape green while leaving
   the graph as uninformative as before, which is the failure this loop exists to correct. If the
   honest answer is "we cannot say", **say so in the task report and register it** — do not
   invent a value to pass a shape.
5. **THE SHAPES ARE READ-ONLY THIS LOOP.** `vocab/shapes/dec-shapes.ttl` and
   `vocab/shapes/iladub-shapes.ttl` must be **byte-identical** at the end of the loop to what
   they are at its start. The oracle is only meaningful because it was authored by a different
   act than the code it judges. If you believe a shape overreaches on compiled evidence, that is
   a **finding to report**, not an edit to make. `git diff --stat vocab/shapes/` must show these
   two files untouched at every commit.
6. **SOURCE OWNERSHIP (CLAUDE.md).** Only `iladub:`, `etkl:`, `dec:`, `risk:` terms may be the
   subject of a triple you author. No HGA term (`holon:`, `hev:`, `hpol:`, …) may appear as a
   subject anywhere.
7. **PLAN DISCIPLINE (CLAUDE.md § Plan authoring discipline).** Every task report carries a
   `## FALSIFICATION` block beside its TDD evidence: remove or invert the thing the new test
   pins, show the test **failing** (paste the output), restore, show the suite green. **No
   falsification evidence ⇒ the task review fails.** Where this plan supplies a test verbatim,
   that test is a *proposition* until you falsify it — a plan-supplied test that ships without
   its falsification evidence is a rule-1 violation, not merely a rule-4 one.
8. **`cand_uri` VALUES DO NOT CHANGE.** `<doc>#region{idx}` is named by `_emit_unit_markers` and
   by the escalation queries. Adding nodes around it is in scope; renaming it is a consumer break
   this loop has no mandate for.
9. **Python is `./.venv/bin/python`.** Never bare `python`/`pytest`.
10. **Multilingual by construction.** Do not constrain any label/rationale literal to
    `xsd:string` — that rejects `rdf:langString`.

**Baseline this loop must move (measured 2026-08-10, spec §3):**

| scope | closure | refusing focus nodes | validation results |
| --- | --- | --- | --- |
| compile (7 docs) | SHIPPED | 26 | 98 |
| compile (7 docs) | RDFS | 26 | 194 |
| grounding (2 docs) | SHIPPED | 719 | 1438 |
| grounding (2 docs) | RDFS | 719 | 1438 |

**Target: 0 in every cell.**

---

## File Structure

| file | responsibility | tasks |
| --- | --- | --- |
| `scripts/measure_dec_membrane.py` | **create** — the reproducible oracle for O1/O4: compile/ground the corpus, validate against both shape files under both closures, print the §3 tables | 1 |
| `src/iladub/etkl/holon.py:370-376` | **modify** — `escalate_region` emits a proposition, not a decision | 2 |
| `src/iladub/etkl/compile.py` (11 call sites) | **modify** — supply whatever the source-region seam needs | 2 |
| `src/iladub/etkl/datagrid.py:684-698` | **modify** — the admission holon becomes a real decision | 3 |
| `src/iladub/ground.py:126-143` | **modify** — `_emit_grounded` deliberates | 4 |
| `src/iladub/promote.py:33,70,100` | **modify** — the three BAML-path promotion emitters deliberate | 5 |
| `src/iladub/etkl/compile.py:389-399` | **modify** — the compile membrane gains both shape files | 6 |
| `src/iladub/feed.py:577-593` | **modify** — `ground_document` gains `validate_shapes` | 7 |
| `tests/test_corpus.py:168-169` | **modify** — the Python re-implementation of `GroundedNodeShape` is deleted | 7 |
| `docs/superpowers/residues.md` | **modify** — R69/R81/R82 rows deleted, new rows appended | 8 |
| `docs/wiki/concepts/{promotion-decision,decision-holon,assert-propose-promote}.md` | **modify** — the contradiction resolved, with the call site named | 8 |

---

### Task 1: The measurement oracle

The spec's O1 and O4 are only falsifiable if anyone can re-run them. This task promotes the
session's scratchpad harness into the repo and **records the baseline before any code changes** —
so every later task has a before/after it did not author.

**Files:**
- Create: `scripts/measure_dec_membrane.py`
- Create: `docs/loops/2026-08-10-decision-membrane-baseline.md` (the measured before-state)

**Interfaces:**
- Produces: a CLI — `measure_dec_membrane.py --scope compile|grounding|both [--doc <stem>]` —
  printing, per document, per shape file, per closure: `conforms`, the refusing focus-node count,
  the validation-result count, and the top refusal paths with example focus nodes. Exit code 0
  when every scope conforms, non-zero otherwise, so it can be used as a gate.
- Consumes: `iladub.etkl.membrane.subclass_closure` (the SHIPPED closure) and
  `iladub.etkl.membrane.rdfs_closure` (the consumer view) — **both**, because O4 is the falsifier
  for "R69 is closed for consumers, not just for us."

**MEASURED CONTEXT (verify before you rely on it):**
- `membrane.py:60-70` — both engines validate the `subclass_closure`-expanded graph with their
  own inference OFF. `rdfs_closure` is retained as the reference implementation (`membrane.py`,
  docstring "SUPERSEDED for production").
- `compile_document` returns a `DocumentReport` with `.graph` (`document.py:205`);
  `compile_tables` returns a `CompilationReport` with `.graph` (`compile.py:363`).
- `ground_document(graph, contract, proposer, terms, shapes, g)` writes into the
  caller-supplied `g` and returns a `FeedResult` (`feed.py:577-593`).
- The contracted documents and their contract/terms/shapes paths are in
  `tests/corpus-manifest.ttl` under `cor:contract` / `cor:terms` / `cor:shapes`; read them from
  the manifest rather than hard-coding, so a manifest change cannot silently desynchronise the
  oracle from the battery.
- Wall-clock, measured this session: compiling all 7 documents takes ~290 s total
  (graincorp-stem alone 157 s). Grounding the two contracted documents from already-compiled
  graphs takes well under a minute. Cache compiled graphs to disk so a re-run after a producer
  fix does not pay the compile again **unless** the fix changed the compiler — offer
  `--no-cache` and make the cache key the source file's sha256 **plus** the git HEAD of `src/`,
  or simply default to no cache and let the caller opt in. **A stale cache that hides a
  regression is worse than a slow oracle** — if in doubt, do not cache.

- [ ] **Step 1: Write the script**

No body is given here (CLAUDE.md plan rule 1). The contract it must satisfy:
- ontology graph = `vocab/ontology/{dec,iladub,etkl,tab}.ttl`
- shape files = `vocab/shapes/dec-shapes.ttl` and `vocab/shapes/iladub-shapes.ttl`, parsed
  **separately** and reported separately (they are complementary halves; a merged report hides
  which half refuses)
- validation via pySHACL with `inference="none"`, `advanced=True`, over the closure-expanded
  graph — matching `membrane._validate_pyshacl` exactly
- counts read out of the SHACL **results graph** (`sh:ValidationResult` / `sh:focusNode` /
  `sh:resultPath` / `sh:resultMessage`), **never** by string-matching the report text. The repo
  already learned this: `membrane._conforms_from_report` documents that a substring test flipped
  a violating graph to "conforming" because rudof echoes offending literals into `sh:value`.

- [ ] **Step 2: Run it and reproduce the spec's §3 numbers**

Run: `./.venv/bin/python scripts/measure_dec_membrane.py --scope both`
Expected — this is the test: the output must match the spec §3 tables **exactly**:
compile SHIPPED 26 foci / 98 results; compile RDFS 26 / 194; grounding SHIPPED 719 / 1438;
grounding RDFS 719 / 1438. Per-document: apple 11 candidates, bfs 10, who 3, ons 2 admission
holons, graincorp-stem 585 promotions, cbh-stem 134.

**If your numbers differ, STOP and report.** Either the harness is wrong or the tree has moved
since 2026-08-10; both are findings, and neither is fixed by adjusting the expected numbers.

- [ ] **Step 3: Record the baseline**

Write `docs/loops/2026-08-10-decision-membrane-baseline.md` containing the raw output of Step 2
verbatim, with the command and the date. This is Evidence class (immutable after loop close).

- [ ] **Step 4: FALSIFICATION**

The oracle must be shown to be capable of failing. Temporarily add a single triple to a copy of
one corpus graph that violates a shape the corpus currently passes — e.g. give an
already-conformant `dec:DecisionHolon` a second `dec:chosen` (violating `sh:maxCount 1`) — and
show the script's count rise and its exit code go non-zero. Restore. Paste both outputs.

An oracle whose count never moves is the R73 defect-5 failure: a test that passes with its
subject deleted.

- [ ] **Step 5: Commit**

```bash
git add scripts/measure_dec_membrane.py docs/loops/2026-08-10-decision-membrane-baseline.md
git commit -m "test(membrane): the dec/iladub shape oracle, and the measured before-state"
```

---

### Task 2: `escalate_region` emits a proposition, not a decision (R69)

**Files:**
- Modify: `src/iladub/etkl/holon.py:370-376` (`escalate_region`)
- Modify: `src/iladub/etkl/compile.py` — call sites at lines 460, 520, 552, 603, 627, 694, 775,
  803, 842, 1009; and `src/iladub/etkl/holon.py:399` (`assert_hier_region`'s ROUND_TRIP_FAIL path)
- Test: `tests/etkl/test_holon.py` (existing, lines 63-64, 126, 212 read `DEC.rationale` /
  `DEC.confidence` and **will fail until updated — they are part of this change**)
- Test: `tests/etkl/test_closing_slice.py:109,155,236`, `tests/etkl/test_merge_resolution.py:88`
  (same reason)

**Interfaces:**
- Consumes: nothing from Task 1 except its oracle.
- Produces: `escalate_region`'s post-condition, which Tasks 6 and 8 rely on — **every
  `iladub:CandidateConcept` in a compiled graph conforms to `iladub:CandidateConceptShape`, and
  no `dec:` property appears on any `iladub:CandidateConcept`.**

**MEASURED CONTEXT:**
```
holon.py:370-376  escalate_region emits: iladub:surfaceText, iladub:suggestedAnchor,
                  dec:confidence, dec:rationale, prov:wasDerivedFrom.  (read 2026-08-10)
```
Missing, per `iladub:CandidateConceptShape` (`vocab/shapes/iladub-shapes.ttl:16-30`):
`iladub:suggestedBy`, `iladub:confidence`, `iladub:fromRegion`, `iladub:status iladub:proposed`.
Measured effect: 24 refusing focus nodes across apple (11), bfs (10), who (3) under the SHIPPED
closure — spec §3.2.

The conformant pattern already exists in this repo — read `ground._emit_candidate`
(`ground.py:88-103`) before writing anything. It types the suggester
(`g.add((agent, RDF.type, ILADUB.Suggester))`), mints a **separate** `iladub:SourceRegion` node,
and sets `iladub:status iladub:proposed`. Copy its shape, not its identifiers.

**SEAM 1 — MEASURE, DO NOT ASSUME: what identifies the source region?**
`cand_uri` is `<doc>#region{idx}` at all 11 call sites (measured: `compile.py:459,481,519,551,602,626,693,774,802,841`; the twelfth path, `compile.py:1009`, uses
`<doc>#p{page_number}-datagrid-residue`). **The candidate URI *is* the region-identified node**,
so `iladub:fromRegion` pointed at `cand_uri` would be self-referential and would satisfy the
shape while asserting nothing. Measure what distinguishes the source region from the candidate
at each site, and mint the `SourceRegion` as a distinct node. Global constraint 8 forbids
changing `cand_uri` itself.

**SEAM 2 — MEASURE, DO NOT ASSUME: is `page` in scope, and does the SourceRegion carry it?**
CLAUDE.md §6 is provenance-to-the-page; a `SourceRegion` carrying only its type is exactly the
stub global constraint 4 forbids. **Measured so far:** `assert_hier_region` takes `page`
(`holon.py:380-381`) and `compile_tables` takes `page_number` (`compile.py:402`), which is the
enclosing function of all ten `compile.py` sites and of the `:1009` datagrid-residue site.
**Verify this at every site yourself before choosing the signature change**, and name in your
task report any site where it does not hold. If a site cannot supply it, that gap is registered
(Task 8), not papered over.

**THE DESIGN DECISION, already settled in spec §5.1 — do not re-litigate:**
- `iladub:confidence` carries the value now on `dec:confidence`, as `xsd:decimal` in [0,1].
- `iladub:suggestedBy` names a **per-reason rule IRI** typed `iladub:Suggester` — one per
  escalation reason (`ROUND_TRIP_FAIL`, `MULTI_TABLE_AMBIGUOUS`, `TRANSPOSED`,
  `ROW_GROUP_AMBIGUOUS`, `MATRIX_AMBIGUOUS`, `MERGE_AMBIGUOUS`, `DATAGRID_RESIDUE`, and any
  other reason string reaching `escalate_region`). Precedent:
  `ground.py:22 _EXACT_RULE = "urn:iladub:suggester/exact-match-rule"`. **This is where the
  reason goes** — a per-reason suggester makes "which rule proposed this" a join instead of a
  `FILTER regex`. Derive the IRI from the reason string mechanically; do not hand-maintain a
  lookup table that can drift from the call sites.
- The human-readable reason stays on the candidate as `rdfs:label` (as `ground.py:91` does).
- **`dec:confidence` and `dec:rationale` are REMOVED from the candidate.** This is the whole of
  R69: with no `dec:` property on the node, no `rdfs:domain` entailment can type it a
  `dec:DecisionHolon` under any consumer's reasoner.
- `iladub:status iladub:proposed`.
- `iladub:suggestedAnchor`, `iladub:surfaceText`, `prov:wasDerivedFrom` are unchanged.

- [ ] **Step 1: Write the failing test**

Add to `tests/etkl/test_holon.py`. This test is the spec's contract with the implementation; it
is a **proposition until you falsify it in Step 5**. It uses that module's existing `ROOT` / `SH`
constants (`test_holon.py:14-16`) and its existing imports (`Graph`, `URIRef`, `RDF`, `validate`,
`TAB`, `ILADUB`, `DEC` are all already in scope at `test_holon.py:5-12`) — add only
`from iladub.etkl import membrane`.

```python
def test_escalated_candidate_conforms_to_candidate_concept_shape():
    """R69: an escalated region is a PROPOSITION (§3), not a decision. It must satisfy
    iladub:CandidateConceptShape, and must carry NO dec: property — dec:confidence's
    rdfs:domain would otherwise entail it is a dec:DecisionHolon for any consumer."""
    g = Graph()
    doc = URIRef("https://example.org/etkl/doc")
    cand = URIRef(f"{doc}#region0")
    escalate_region(g, cand, doc, "a b c", "ROUND_TRIP_FAIL", TAB.HierarchicalTable, 0.3)

    # (a) no dec: property survives on the candidate
    assert not [p for p in g.predicates(cand, None) if str(p).startswith(str(DEC))], \
        "a proposition must carry no decision vocabulary"

    # (b) the candidate conforms to its own shape, under the SHIPPED closure
    ont = Graph()
    for f in ("dec.ttl", "iladub.ttl", "etkl.ttl", "tab.ttl"):
        ont.parse(os.path.join(ROOT, "vocab", "ontology", f), format="turtle")
    shapes = Graph().parse(os.path.join(SH, "iladub-shapes.ttl"), format="turtle")
    conforms, _, text = validate(membrane.subclass_closure(g, ont), shacl_graph=shapes,
                                 inference="none", advanced=True)
    assert conforms, text

    # (c) the reason is recoverable, and as a JOIN not a string match
    suggester = g.value(cand, ILADUB.suggestedBy)
    assert suggester is not None and (suggester, RDF.type, ILADUB.Suggester) in g
    assert "round-trip" in str(suggester).lower() or "round_trip" in str(suggester).lower()

    # (d) the source region is a DISTINCT node — a self-reference satisfies the shape
    #     while asserting nothing (Global Constraint 4)
    region = g.value(cand, ILADUB.fromRegion)
    assert region is not None and region != cand
    assert (region, RDF.type, ILADUB.SourceRegion) in g
```

- [ ] **Step 2: Run it to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_holon.py::test_escalated_candidate_conforms_to_candidate_concept_shape -v`
Expected: FAIL at assertion (a) — `dec:confidence` and `dec:rationale` are still emitted.

- [ ] **Step 3: Measure the two seams, then implement**

Write your seam measurements into the task report **before** the implementation diff: what
identifies the source region at each of the 11+1 call sites, and whether `page` is in scope at
each. Then change `escalate_region` (and only what the seams require at the call sites).

- [ ] **Step 4: Run the tests**

Run: `./.venv/bin/python -m pytest tests/etkl/ -q`
Then: `./.venv/bin/python -m pytest -q`
The listed existing tests (`test_holon.py:63,64,126,212`, `test_closing_slice.py:109,155,236`,
`test_merge_resolution.py:88`) will fail on `DEC.rationale`/`DEC.confidence`. **Update each to
assert the new property** (`iladub:confidence`, `iladub:suggestedBy`, `rdfs:label`).
**Deleting a failing test instead of updating it is a rule-4 failure.**

- [ ] **Step 5: FALSIFICATION**

Remove the `iladub:fromRegion` emission alone; show the new test failing at (d) and the shape
check failing at (b). Restore. Then remove the `dec:` removal (i.e. re-add `dec:confidence`);
show the test failing at (a). Restore. Paste both failing outputs and the final green run.

- [ ] **Step 6: Re-run the oracle**

Run: `./.venv/bin/python scripts/measure_dec_membrane.py --scope compile`
Expected: the 24 candidate focus nodes are **gone** from both the `iladub-shapes` refusals and
the `dec-shapes` RDFS refusals. Compile scope should now show **2 refusing focus nodes** under
both closures (the ons admission holons, Task 3's subject). Record the numbers.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/holon.py src/iladub/etkl/compile.py tests/etkl/
git commit -m "fix(epistemics): an escalated region is a proposition, not a decision (R69)"
```

---

### Task 3: The data grid's admission holon becomes a real decision (R81)

**Files:**
- Modify: `src/iladub/etkl/datagrid.py:684-698`
- Test: `tests/etkl/` — the data-grid test module (locate it; do not create a parallel one)

**Interfaces:**
- Consumes: `decisionlog._READER_AGENT` (`src/iladub/etkl/decisionlog.py:25` —
  `URIRef("https://w3id.org/iladub/etkl#reader")`), the same agent the DOCUMENT driver already
  names for the adoption path.
- Produces: **every admission holon, from every path that mints one (`datagrid_adopt=True`,
  `datagrid_fallback=True`, and the document driver's adoption), conforms to
  `dec:DecisionHolonShape`.**

**MEASURED CONTEXT:**
```
datagrid.py:620       dec_uri = URIRef(f"{grid_uri}-admission")
datagrid.py:684-698   emits dec:DecisionHolon, dec:chosen grid_uri, dec:optionSpace grid_uri,
                      tab:admittedBy, then one dec:optionSpace per refused row.
                      NO dec:decidedBy.  NO rdfs:label on grid_uri.
emit_data_grid signature (datagrid.py:599-600): (g, grid, lines, doc_uri, page,
                      grid_uri=None) — `page` and `doc_uri` ARE in scope for the label.
```
Measured effect (spec §3.1): `<doc>/p7#p7-datagrid-admission` and `…p8…` refuse `dec:decidedBy`
on `corpus/gov-stats/ons-index-of-services-2026-02.pdf` — **the only corpus refusal the shipped
closure produces for `dec-shapes.ttl`**, on the `datagrid_fallback=True` default path.

**THE THREE FACES (spec §5.2):**
- **(a′) `dec:decidedBy`** naming `_READER_AGENT`. This is the face the corpus refuses.
- **(b) `rdfs:label` on `grid_uri`** — so `vocab/queries/effective-chain.rq`'s
  `OPTIONAL { ?d dec:chosen/rdfs:label ?chosen }` binds and a consumer can read *what* replaced
  the superseded band. It must state what the grid **is** (its shape and page). A constant
  string binds `?chosen` while telling the consumer nothing → global constraint 4.
- **(c) a no-change option, emitted UNCONDITIONALLY** — "refuse the page" — with a
  `dec:rejectedBecause` naming how much ink the grid actually read. Emitting it only when
  `grid.refusals` is empty would make the option space a function of the outcome, which is
  backwards: refusing the page was always available.

`dec:chosen` stays `grid_uri`, which stays in the option space —
`dec:DecisionHolonShape`'s `sh:sparql` (chosen ∈ optionSpace) must still hold.

- [ ] **Step 1: Write the failing test**

Contract for the test you write (no verbatim body given — the fixture setup is yours to choose
from the existing data-grid tests, which already build grids):

1. Build a grid that **refuses at least one row** and one that **refuses none**. Both must exist;
   face (c) is invisible on the first and the corpus contains only the first (spec §3.1 records
   that R81(c) is unobserved on the corpus — your test is the only evidence for it).
2. Assert both admission holons conform to `dec-shapes.ttl` under `membrane.subclass_closure`.
3. Assert `len(list(g.objects(dec_uri, DEC.optionSpace))) >= 2` in **both** cases.
4. Assert the grid's `rdfs:label` differs between two grids of different shape (this is the
   anti-constant-label check — a test that only asserts "a label exists" passes a stub).
5. Assert `effective-chain.rq` binds `?chosen` when run over a graph containing an admission
   holon. Read the query from `vocab/queries/effective-chain.rq`; do not inline a paraphrase of
   it, or you will be testing your paraphrase.

- [ ] **Step 2: Run it to verify it fails**

Run: `./.venv/bin/python -m pytest <the data-grid test module> -v -k admission`
Expected: FAIL on `dec:decidedBy` (assertion 2), on `optionSpace >= 2` for the refusal-free grid
(assertion 3), and on the unbound `?chosen` (assertion 5).

- [ ] **Step 3: Implement**

- [ ] **Step 4: Run the tests**

Run: `./.venv/bin/python -m pytest -q`

- [ ] **Step 5: FALSIFICATION**

Delete the unconditional no-change option; show assertion 3 failing for the refusal-free grid
and passing for the refusing one — **that asymmetry is the proof the test pins face (c) and not
merely face (a′)**. Restore. Then delete `dec:decidedBy`; show assertion 2 failing. Restore.
Paste both.

- [ ] **Step 6: Re-run the oracle**

Run: `./.venv/bin/python scripts/measure_dec_membrane.py --scope compile`
Expected: **0 refusing focus nodes at compile scope, under BOTH closures**, on all 7 documents.
Record the numbers. If anything still refuses, report it — do not proceed to Task 6.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/datagrid.py tests/
git commit -m "fix(datagrid): the admission holon records its agent, its label and its no-change option (R81)"
```

---

### Task 4: `_emit_grounded` deliberates

This is the largest defect in the loop: 719 promotion decisions across the two contracted corpus
documents, every one of them failing `dec:DecisionHolonShape` on `optionSpace` and `chosen`
(spec §3.3). It is unregistered — R69, R81 and R82 do not name it.

**Files:**
- Modify: `src/iladub/ground.py:126-143` (`_emit_grounded`)
- Test: `tests/test_grounding_value_constraints.py` (existing, reads `DEC.rationale` at :76) or
  the nearest existing grounding test module — locate it; do not create a parallel one.

**Interfaces:**
- Consumes: `_grounds_to`'s refusal paths (`ground.py:106-123`) — the three ways grounding can
  refuse: no scheme member, value refused by the SHACL value membrane, bare proposal with no
  oracle.
- Produces: **every `iladub:PromotionDecision` conforms to `dec:DecisionHolonShape`.** Task 7's
  gate depends on this; Task 5 mirrors it for the BAML-path emitters.

**MEASURED CONTEXT:**
```
ground.py:126-143  _emit_grounded emits: rdf:type iladub:PromotionDecision, iladub:reviews,
                   dec:decidedBy, dec:consideredEvidence, dec:confidence, dec:rationale,
                   dec:produced.   NO dec:optionSpace.  NO dec:chosen.
ground.py:147-171  ground_concept branches on `field is None` (→ "proposed") and then on
                   `grounds_to is None` (→ "proposed"), else "grounded".
```
Measured: graincorp-stem 585 PromotionDecision / 585 GroundedNode; cbh-stem 134 / 134; all
refusing both `optionSpace` and `chosen` under the SHIPPED closure.

**THE OPTION SPACE (spec §5.3) — read off the branch, not invented (global constraint 3):**
- option **ground-to-field** — names the contract field the concept grounded to.
- option **quarantine-as-proposition** — the branch not taken, carrying `dec:rejectedBecause`
  that names **which** refusal path in `_grounds_to` would have applied. A single constant
  string here is global-constraint-4 decoration and fails the O3 oracle.
- `dec:chosen` → the branch actually taken.

**SEAM — MEASURE, DO NOT ASSUME: what type are the nodes?** `pd` is a `BNode` in
`_emit_grounded` (`ground.py:127`) and a `URIRef` in `promote.py`. `dec:optionSpace`'s
`rdfs:range` is `dec:Option` (`dec.ttl:64`). Measure both before choosing the option node's
identity — **a URIRef option hung off a BNode decision is not addressable**, and a BNode option
cannot be named by a downstream query. State your choice and its reason in the task report.

- [ ] **Step 1: Write the failing test**

Contract for the test you write:

1. Ground one concept that **grounds** and one that **quarantines**, through the real
   `ground_concept` (not a hand-built graph — the point is to pin the emitter, not a fixture).
2. Assert the grounded one's `PromotionDecision` conforms to `dec-shapes.ttl` under
   `membrane.subclass_closure`.
3. Assert `dec:chosen` is the ground-to-field option **and** that it is a member of
   `dec:optionSpace` (the shape's `sh:sparql` constraint, asserted directly so a failure names
   itself).
4. **The O3 anti-decoration assertion:** ground two concepts that refuse for *different* reasons
   (e.g. one with no scheme member, one whose value the SHACL value membrane refuses) and assert
   their rejected options' `dec:rejectedBecause` **differ**. A hard-coded rejection string passes
   assertions 1-3 and fails this one.

- [ ] **Step 2: Run it to verify it fails**

Expected: FAIL on assertion 2 (`optionSpace` minCount 2, `chosen` minCount 1).

- [ ] **Step 3: Implement**

- [ ] **Step 4: Run the tests**

Run: `./.venv/bin/python -m pytest -q`

- [ ] **Step 5: FALSIFICATION**

Collapse the two `dec:rejectedBecause` values to one constant; show assertion 4 failing while
1-3 still pass — **that is the proof the test pins deliberation and not decoration.** Restore.
Then delete `dec:chosen`; show assertion 2 failing. Restore. Paste both.

- [ ] **Step 6: Re-run the oracle**

Run: `./.venv/bin/python scripts/measure_dec_membrane.py --scope grounding`
Expected: **0 refusing focus nodes**, both documents, both closures. Baseline was 719 / 1438.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/ground.py tests/
git commit -m "fix(promotion): a promotion decision names the options it deliberated"
```

---

### Task 5: `promote.py`'s three emitters deliberate

**Files:**
- Modify: `src/iladub/promote.py` — `emit_promotion` (:33), `emit_span_promotion` (:70),
  `emit_row_role_promotion` (:100)
- Test: `tests/etkl/test_promote.py` (:23 reads `DEC.rationale`),
  `tests/etkl/test_span_promotion.py` (:22, same)

**Interfaces:**
- Consumes: the option-node identity decision made in Task 4's seam — **use the same convention**
  (`pd` is a `URIRef` here, a `BNode` there; the *convention* must be consistent even though the
  types differ).
- Produces: every promotion decision on the BAML/proposer paths conforms to
  `dec:DecisionHolonShape`.

**MEASURED CONTEXT — AND ITS LIMIT (spec §3.5, premise type: FIXTURE):** these three emitters are
reached only under a BAML or Fake proposer. They appear **zero** times in the corpus measurement
(`promotions=0` on all 7 compiled graphs). **This task has no corpus evidence and your report
must say so explicitly** rather than implying the corpus covers it. Their oracle is unit tests.

Each of the three already states its deliberation *in prose* in its `dec:rationale` — read them
(`promote.py:56-58`, `:94-97`, `:129-135`) and derive the option space from what the prose
already says was weighed:
- `emit_promotion`: the reshape round-trips exactly; the **name** is a proposition, not
  oracle-verified.
- `emit_span_promotion`: `region_tiles` confirms the reading is structurally LEGAL but geometry
  could not decide it uniquely.
- `emit_row_role_promotion`: the reading is legal and lossless but not unique — "furniture" and
  "continuation" both tile and both conserve.

In each case the not-chosen option is the alternative the prose names. **Do not invent a
third** (global constraint 3).

- [ ] **Step 1: Write the failing tests** — one per emitter, each asserting shape conformance
  under `membrane.subclass_closure` and that `dec:chosen` ∈ `dec:optionSpace`.
- [ ] **Step 2: Run to verify they fail** — expected: `optionSpace` / `chosen` minCount.
- [ ] **Step 3: Implement all three.**
- [ ] **Step 4: Run** `./.venv/bin/python -m pytest -q`.
- [ ] **Step 5: FALSIFICATION** — for **each** of the three, delete its `dec:optionSpace`
  emission and show its own test failing; restore; paste all three.
- [ ] **Step 6: Commit**

```bash
git add src/iladub/promote.py tests/
git commit -m "fix(promotion): the BAML-path promotions name their deliberated alternative"
```

---

### Task 6: The compile membrane gains both shape files (R82)

**Do not start this task until Task 3's Step 6 showed 0 refusals at compile scope.** Wiring the
gate over a violating corpus is the thing spec §5.4 forbids.

**Files:**
- Modify: `src/iladub/etkl/compile.py:389-399` (`_validate`, `_FULL_SHAPES`, `_FULL_ONT`)
- Test: `tests/etkl/` — a new test asserting the membrane's shape set

**Interfaces:**
- Consumes: Tasks 2 and 3's post-conditions.
- Produces: `_validate` refuses any graph whose `dec:`/`iladub:` payload violates the shapes;
  `compile_tables(..., validate_shapes=True)` raises `AssertionError` (existing contract,
  `compile.py:1035-1037`) rather than returning a report.

**MEASURED CONTEXT:**
```
compile.py:389-399  _FULL_SHAPES = tab-shapes.ttl + tab-physical-shapes.ttl
                    _FULL_ONT    = tab.ttl
grep -c 'dec:' vocab/shapes/tab-shapes.ttl vocab/shapes/tab-physical-shapes.ttl → 0, 0
iladub.ttl:60-61    iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon
```
`_FULL_ONT` **must** gain `dec.ttl` and `iladub.ttl`: the subclass closure needs that axiom or
the promotion shapes never target anything at all.

**SEAM — MEASURE, DO NOT ASSUME: does enlarging `_FULL_ONT` move the TAB verdicts?**
`_validate` validates the tab shapes and the new shapes **in the same call, over the same
closure**. Adding ontologies enlarges the subclass closure for the tab shapes too. **Measure the
tab-shape verdict on all 7 documents before and after the `_FULL_ONT` change, with the new shape
files NOT yet added** — i.e. change the ontology alone, measure, then add the shapes. If any tab
verdict moves, that is a finding to report, not a thing to absorb. This is the direct analogue of
the R73 plan's defect 2 (an ordering assumed from reading rather than measured).

- [ ] **Step 1: Measure the ontology change in isolation**

Add `dec.ttl` + `iladub.ttl` to `_FULL_ONT` **only**. Run the full corpus compile and confirm
every document still compiles and every tab verdict is unchanged. Paste before/after.

- [ ] **Step 2: Write the failing test**

Contract: a test that (a) asserts `_FULL_SHAPES` contains a triple from each of the four shape
files (so the membrane's shape set is pinned by the test, not by a comment), and (b) builds a
minimal graph with one under-furnished `dec:DecisionHolon` and asserts `compile._validate`
returns `conforms=False`. Assertion (b) is the one that matters — (a) alone would pass if the
shapes were parsed and never applied.

- [ ] **Step 3: Run to verify it fails** — expected: `_validate` returns `conforms=True` for the
  under-furnished holon, because the shapes are not in the membrane.

- [ ] **Step 4: Add both shape files to `_FULL_SHAPES`.**

- [ ] **Step 5: Run the full suite and the corpus battery**

```
./.venv/bin/python -m pytest -q
./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
```
Every corpus document must still compile. A document that now raises `AssertionError` is a
producer defect this loop has not yet fixed — **report it; do not remove the shape** (global
constraint 5).

- [ ] **Step 6: FALSIFICATION**

Remove `dec-shapes.ttl` from `_FULL_SHAPES`; show the new test's assertion (b) failing. Restore.
Remove `iladub.ttl` from `_FULL_ONT`; show that a graph with a malformed `iladub:PromotionDecision`
now passes (the shape targets nothing without the subclass axiom) — **this is the proof the
ontology line is load-bearing and not decoration.** Restore. Paste both.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/compile.py tests/
git commit -m "feat(membrane): the compile membrane validates the decision graph too (R82)"
```

---

### Task 7: The grounding membrane, and the Python duplicate it replaces

**Files:**
- Modify: `src/iladub/feed.py:577-593` (`ground_document`)
- Modify: `tests/test_corpus.py:168-169`
- Test: `tests/` — a new test for the gate's refusal behaviour

**Interfaces:**
- Consumes: `membrane.validate(data_graph, shapes_graph, ont_graph) -> (conforms, report_text)`
  (`membrane.py:44`) — **the one place SHACL runs**; do not call pySHACL or pyrudof directly.
- Produces: `ground_document(graph, contract, proposer, terms, shapes, g, validate_shapes=True)`
  — same positional signature as today with one keyword appended, so every existing call site
  (`tests/test_corpus.py:163`, `tests/test_cbh_e2e.py:88`, `tests/test_corpus_stem.py:54`,
  `tests/test_concept_feed.py:147,159,220,274,316`) keeps working unchanged.

**WHY THIS GATE EXISTS AT ALL (spec §5.4):** every compiled graph has `grounded=0,
promotions=0` — `iladub:GroundedNode` and `iladub:PromotionDecision` are minted by
`ground.py`/`splitkey.py`, never by `compile`. Without this gate, `iladub:GroundedNodeShape` —
the shape that *is* the differentiator — stays vacuous no matter what Task 6 does.

**THE PYTHON DUPLICATE:**
```
tests/test_corpus.py:168-169
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1
```
This is a hand-rolled re-implementation of `iladub:GroundedNodeShape`
(`vocab/shapes/iladub-shapes.ttl:37-44`). Under CLAUDE.md §8 the shape is the decision and the
Python that re-states it is the defect. **Delete it and let the membrane verdict stand in its
place** — the surrounding test keeps its `assert grounded, "a contracted document must ground
SOMETHING"`, which is a different claim (non-vacuity) and stays.

- [ ] **Step 1: Write the failing test**

Contract: a test that calls `ground_document` with `validate_shapes=True` over a graph doctored
to contain one `iladub:GroundedNode` with **no** `iladub:wasPromotedBy`, and asserts it raises.
Then the same with `validate_shapes=False` and asserts it does not. The pair is what pins the
flag; either alone does not.

- [ ] **Step 2: Run to verify it fails** — expected: `TypeError` (no such keyword).

- [ ] **Step 3: Implement the gate**, mirroring `compile._validate`'s structure: module-level
  cached shapes/ontology graphs, validation through `membrane.validate`, `AssertionError` with
  the report text on refusal.

- [ ] **Step 4: Delete `tests/test_corpus.py:168-169`** and run the corpus battery

```
./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
```
Both contracted documents must ground and conform.

- [ ] **Step 5: Run the full suite** — `./.venv/bin/python -m pytest -q`

- [ ] **Step 6: FALSIFICATION**

This is the loop's central claim, so falsify it directly: doctor a grounded graph so one
`GroundedNode` loses its `wasPromotedBy`, and show the **membrane** refusing it (not the deleted
Python loop). Then restore and show green. Paste both. **This is the evidence that
`promotion-decision.md:48-49` is now a true sentence.**

- [ ] **Step 7: Commit**

```bash
git add src/iladub/feed.py tests/
git commit -m "feat(membrane): grounding validates the promotion invariant it claims to enforce"
```

---

### Task 8: Close the loop — the register, the wiki contradiction, the final measurement

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/wiki/concepts/promotion-decision.md`, `docs/wiki/concepts/decision-holon.md`,
  `docs/wiki/concepts/assert-propose-promote.md`
- Modify: `docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md` (status line only)
- Create: `docs/loops/2026-08-10-decision-membrane-close.md` (the after-state)

- [ ] **Step 1: Final measurement**

```
./.venv/bin/python scripts/measure_dec_membrane.py --scope both
./.venv/bin/python -m pytest -q
./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
```
Expected: **0 refusing focus nodes in all four cells** of the baseline table. Write the raw
output to `docs/loops/2026-08-10-decision-membrane-close.md` beside the Task 1 baseline.

- [ ] **Step 2: Update the register**

**Delete** the R69, R81 and R82 rows (a loop that closes a residue deletes its row in the same
change). **Append** rows for, at minimum:
- the **quarantine-decision gap** — 1265 + 775 quarantined concepts get no decision holon
  (spec §7); measured at `ground.py:158` (`return "proposed"` with no `pd` emitted).
- any **call site where `page` was not in scope** for the `SourceRegion` (Task 2, Seam 2), with
  the site's `file:line`.
- **`escalation-shapes.ttl` is not in the membrane** — measured clean on apple p0 under both
  closures, unmeasured on the other six (spec §7).
- **`BandRecorder`'s Python guard now duplicates a shape that is enforced at the membrane**
  (`decisionlog.py:44-47`) — with Task 7's deletion as precedent, this is a candidate for the
  same treatment, but it is a *producer-side fail-fast* rather than a test-side duplicate, so it
  is a judgement call and not this loop's to make.

Each row carries **what it is, where it was MEASURED, why deferred, what would close it**.

- [ ] **Step 3: Resolve the wiki contradiction**

`promotion-decision.md:48-49` ("iladub's SHACL membrane hard-fails any grounded node lacking
`wasPromotedBy`") and `decision-holon.md:26` ("the core deliberation shape is enforced, not just
declared") were **false for every compiled and grounded document** when written. They are now
true. Edit each to **name where enforcement happens** — `compile._validate` and
`ground_document`'s gate, by `file:line`. A claim about enforcement that does not name its call
site is how this one survived; that sentence belongs in the page as the lesson.

Update `assert-propose-promote.md` with the measured fact that the proposition half was malformed
on every real document until this loop (24 candidates across 3 corpus documents).

- [ ] **Step 4: Flip the spec status** from `design, awaiting review` to `design, implemented`,
  and change its `Doc impact:` line to record the contradiction as **resolved in this loop**.

- [ ] **Step 5: Verify the shapes are untouched** (global constraint 5)

```bash
git diff --stat main -- vocab/shapes/dec-shapes.ttl vocab/shapes/iladub-shapes.ttl
```
Expected: **empty output.** Any diff here invalidates every measurement in the loop.

- [ ] **Step 6: Commit and open the PR**

```bash
git add docs/
git commit -m "docs: close R69, R81, R82 — the decision membrane is enforced, and says where"
```

---

## Self-Review

**Spec coverage.** §5.1 → Task 2. §5.2 → Task 3. §5.3 → Tasks 4 (corpus-evidenced) and 5
(fixture-only). §5.4 → Tasks 6 (compile) and 7 (grounding + the Python duplicate). §5.5 (refusal
raises) → Task 6's existing-contract note and Task 7 Step 3. §5.6 → global constraint 4, with
O3 realised as Task 4 Step 1 assertion 4 and Task 3 Step 1 assertion 4. §4's O1 → Task 1's
oracle, re-run at Tasks 2, 3, 4 and 8. O2 → the `FALSIFICATION` step in every task. O4 → the
oracle runs both closures at every checkpoint. §6 → Task 1 (harness) + Task 8 Step 1. §7 (what is
not done) → Task 8 Step 2's register rows. §8 → Task 8. §9 → global constraint 7.

**Placeholder scan.** No "TBD"/"handle edge cases"/"similar to Task N". Two tests are given
verbatim (Task 1 has none, Task 2 Step 1 is full); the rest are given as **contracts** — what the
test must pin and what deleting the subject must break — because CLAUDE.md plan rule 1 makes the
body the implementer's to write, and rule 4 makes a plan-supplied test a proposition until
falsified. Every task states its files, its measured context with `file:line`, its seams, and its
falsification.

**Type consistency.** `escalate_region`'s signature is discussed in Task 2 only; `_READER_AGENT`
is named identically in Task 3 and referenced from `decisionlog.py:25`; the option-node identity
convention is decided once (Task 4's seam) and explicitly inherited by Task 5;
`membrane.validate`'s `(conforms, report_text)` return is used identically in Tasks 6 and 7;
`ground_document`'s new keyword is appended, so the eight measured call sites are unaffected.

**One thing this plan deliberately does NOT do:** it does not tell you what the source region is,
what the grid's label should say, or which option node type to use. Those are the three seams
(Task 2 Seam 1/2, Task 3 face (b), Task 4 seam). A plan that answered them from reading would be
making exactly the class of unmeasured load-bearing claim that produced five defects in the R73
plan — and you, at the keyboard, are the one who can measure them in thirty seconds.
