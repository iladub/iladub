# The membrane reports its health — closing `holon:05`

**Date:** 2026-08-25 · **Criterion:** `prog:criterion:holon:05` (`tests/arc-manifest.ttl:352-359`) ·
**Rung:** `holon` 4/6 → 5/6 · **Branch:** `holon-05-spec-revision`

> **REVISION 2026-08-25.** This spec was adversarially reviewed before any plan was written, and
> **did not survive unchanged**. It is rewritten here from
> `docs/superpowers/2026-08-25-holon-05-adversarial-review.md` (findings B1–B8, P1–P3, five
> bookkeeping errors) and the two ruling files that decide what the review left open:
> `2026-08-25-holon-05-b1-ruling.md` (**B1**) and `2026-08-25-holon-05-b2-b3-b7-p1-rulings.md`
> (**B2, B3, B7, P1**). **Those files are cited, never re-derived** (rule 6).
>
> Six things the reader of the first version must un-learn: the subject is **not** an
> `etkl:CleanDocumentHolon` (§4.1); the verdict fact is **not** an `sh:ValidationReport` (§4.2);
> `Weakened`'s amendment is **not** one comment (§4.6); `Compromised` reports **document-scope
> refusals only** (§4.5); **O3 is not fixture-only** (§5.6); and `_validate` returns **three**
> elements, the third being the legs that *refused* (§2.3).

**Doc impact: increment.** Larger than the first version stated. Published surfaces that change:
`etkl:Weakened`'s `rdfs:comment` (`vocab/ontology/etkl-holons.ttl:82`), `etkl:MembraneHealth`'s
`rdfs:comment` (`:77`), **three new owned terms** (`etkl:CompiledDocumentHolon`,
`etkl:MembraneValidation`, `etkl:refusingLeg`), **one new shape**
(`etkl:MembraneHealthShape` in `vocab/shapes/etkl-shapes.ttl`), the `owl:versionInfo` bump
`0.1.0` → `0.2.0` (`:33`), and `docs/holonic-interaction.md:160-161` — whose first *"Planned work
(not done yet)"* bullet (the heading is at `:158`) is the sentence this loop makes true. *The first
version cited `:154-155` for that bullet; that is the done-list above it, and is a sixth bookkeeping
error the review did not catch.* Queue for the next release; none of it blocks the loop.

**Evidence this spec is written from:** `docs/superpowers/2026-08-25-holon-05-measurements.md`,
`docs/superpowers/2026-08-25-holon-05-design-decisions.md`, the adversarial review, and the two
ruling files. §2 states each load-bearing fact **once**; every later section cites §2.x rather than
re-deriving it (CLAUDE.md § Plan authoring discipline, rule 6).

---

## §1 The question

`holon:05` asks for *"a membrane-health check that computes and reports a compiled document's
cleanliness (`etkl:membraneHealth` → Intact / Weakened / Compromised) **from validation results**"*
(`docs/holonic-interaction.md:160-161`, quoted verbatim by the criterion's `prog:statement` at
`tests/arc-manifest.ttl:354`).

The vocabulary has existed since 2026-06-23 and **nothing derives it** (`tests/arc-manifest.ttl:345-351`,
that manifest's own grep). The question is not "can we write the triple" — it is:

> **Can all three values be *derived*, from evidence that is actually present, without any of them
> being unreachable by construction?**

Three vacuity hazards stack on this criterion; a fourth was found writing this spec and then measured
away (§5.4). A three-valued property with unmintable values is the R106 class the arc manifest was
already caught by once. §5 answers each one; §7 pins each answer with an oracle.

**And one thing this loop must not let the vocabulary claim.** `etkl:membraneHealth` is **not** the
compilation score. `graincorp-stem` scores `0.9655` — 77 escalated tokens of unread ink — and this
design labels it `Intact`, correctly, because nothing is *held at the membrane*. Two different
signals; §4.6 makes the published comment say so (review B8).

---

## §2 What is measured before anything is designed

Each fact is stated once, here, with its evidence. Full commands and raw output are in
`docs/superpowers/2026-08-25-holon-05-measurements.md`; facts re-measured during the review or this
revision are marked **RE-MEASURED**.

### §2.1 The subject can be minted safely — decision 1 survives

Typing the document URI and hanging `etkl:membraneHealth` off it changes **no** verdict the membrane
produces. Four independent reasons: there is **no `sh:closed` in any `.ttl` in the repo**; **no
loaded shape names any `etkl:` term** (the five loaded files are `tab-shapes.ttl`,
`tab-physical-shapes.ttl`, `dec-shapes.ttl`, `iladub-shapes.ttl`, `escalation-shapes.ttl`, assembled
at `src/iladub/etkl/compile.py:398,421,431-439`); `etkl-holons.ttl` is **not** in `_FULL_ONT`
(`compile.py:441,452,453`); and inference is **off** (`membrane.py:124-125`, `inference="none"`).
Measured differentially on real compiled graphs — page and document scope, both legs, both engines —
`IDENTICAL VERDICTS: True`, closure delta exactly the added triples.

**RE-MEASURED, and the review's caveat is carried:** this holds because
`vocab/shapes/etkl-shapes.ttl` — the one shape file with 22 `etkl:` references — **is not loaded**,
not because no shape file mentions `etkl:`. That is exactly why §4.8 puts the new
`MembraneHealthShape` in *that* file: it inherits the same non-loading and leaves this argument
untouched.

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

### §2.3 `_validate` returns THREE elements, and the third is the legs that REFUSED

**RE-MEASURED this revision — the first version of this spec got the return contract wrong**, and
B2's design depends on it. Verbatim, `src/iladub/etkl/compile.py:504-525`:

```python
def _validate(graph: Graph,
              legs: tuple[str, ...] = ("tab", "dec")) -> tuple[bool, str, tuple[str, ...]]:
    """R104: the third element carries the LEG IDENTITY of every leg in `legs` that refused, in
    `legs`' own order …"""
    …
    refusing = tuple(leg for leg in legs if not verdicts[leg][0])
    if not refusing:
        text = verdicts["tab"][1] if "tab" in verdicts else verdicts[legs[0]][1]
        return True, text, ()                                            # ← :524
    return False, "\n".join(verdicts[leg][1] for leg in refusing), refusing   # ← :525
```

So `legs` in `conforms, text, legs = _validate(…)` (`document.py:1624`) is **the refusing legs, not
the requested ones**, and it is **`()` on every conforming validation** (`:524`). §4.2 carries it
verbatim, and §4.2 states what that means for the conforming path.

There is otherwise **no engine-independent structured report, and none is needed.**
`membrane.validate` returns `(bool, str)` (`membrane.py:45-46,108`); the pySHACL leg discards the
report graph into `_` (`:124-126`) and its `text` is **prose**, not Turtle; the rudof leg parses its
Turtle report only to read `sh:conforms` and drops the graph (`:159-174`); `_deskolemize` operates on
the report **string** and says why (`:297-315`: the two engines' reports are different kinds of
document). Both raise sites hold the verdict as a plain Python `bool` (`compile.py:1171`,
`document.py:1624`).

### §2.4 The raise sites, the catchers, and the graph identity

Both sites raise a bare `AssertionError` with one string arg
(`compile.py:1173`, `document.py:1626`; message built by `_refusal_message`, `compile.py:528-535`)
and attach **no** graph. In both functions the local `graph` at the raise **is** the object that
would otherwise be returned (`compile.py:1171`/`:1175`; `document.py:1624`/`:1636`).

**The catcher census, RE-MEASURED and widened** (the first version said *"Exhaustively … the only"*;
that word is withdrawn — review P2):

| command (over `src/ tests/ scripts/`) | result |
|---|---|
| `git grep -n "except AssertionError"` | **1 hit** — `tests/test_corpus.py:129`, which **re-raises** at `:130` |
| `git grep -n "except BaseException"` | exit 1 |
| `git grep -n "except\s*:"` | exit 1 |
| `git grep -n "suppress("` | exit 1 |
| `git grep -n "pytest.raises(AssertionError" -- tests/` | **6 hits, none counted before** |

**`pytest.raises` is a catcher, and the six were missed.** Every one was individually checked: none
has a `compile_tables`/`compile_document` call inside its `with` block —
`test_arc_ablation.py:698,704` (manifest linting, no compile anywhere in the block);
`test_corpus_battery_unit.py:79,91,103` (the compile is deliberately *outside*, at `:90` and `:102`);
`test_concept_feed.py:349` (the **grounding** membrane, `feed.py:643`; its compile happened at `:346`,
outside). **The conclusion survives: a subclass of `AssertionError` breaks nothing.** The one site to
remember is `test_concept_feed.py:349` — it is precisely what would have to change if §9's
grounding-leg scope-out is ever revisited.

**A third membrane raise exists — `src/iladub/feed.py:643`**, a bare `assert conforms` guarding the
*grounding* graph, invisible to `grep "raise AssertionError"` and erased by `python -O`. §9 scopes it
out, and §4.4 explains why that is principled rather than expedient.

**Two traps:** `compile_tables` **rebinds** `graph = Graph()` on the datagrid-withdrawal path
(`compile.py:1115`), so "the graph at the raise site" is not always the object created at `:574`; and
`CompilationReport` is constructed **positionally** at `compile.py:1175` (fields at `:363`), the R73
defect-3 trap. `DocumentReport` is constructed **entirely by keyword** (`document.py:1636-1639`), so
that trap does not bite at document scope.

### §2.5 `sh:severity` is absent, which is why decision 2 exists

Zero `sh:severity`/`sh:Warning`/`sh:Info`/`sh:Violation` anywhere in the authored tree, including the
expanded IRIs. **RE-MEASURED with the scope the review demanded** — the first version pasted an
unscoped `git grep` that now matches this spec's own text, and a grep sweeping `docs/` cannot be
pasted as evidence *into* `docs/`:

```
$ git grep -n "shacl#Warning\|shacl#Info\|shacl#Violation\|shacl#severity" -- vocab/ src/ tests/ examples/
exit 1
$ git grep -n "sh:severity\|sh:Warning\|sh:Info\|sh:Violation" -- vocab/ src/ tests/ examples/
exit 1
$ git grep -l "sh:NodeShape" -- vocab/ src/ tests/ examples/ | wc -l      # positive control
      22
```

The positive control matters: 22 files in that same scope declare an `sh:NodeShape` and **not one**
declares a severity. Every violation the membrane can produce is `sh:Violation` by default.
**`etkl:Weakened` as published — "Interior conforms but warnings are present" (`etkl-holons.ttl:82`)
— is underivable**, and that is the finding that forces §4.6.

### §2.6 The skip guard is page-scope; the document-scope hazard is different

`compile.py:1167-1170` skips validation for a page with no `tab:RecordTable`/`tab:HierarchicalTable`
— **16 of 27 corpus pages (59%)**. Document scope gates on `validate_shapes` alone
(`document.py:1623`) and selects legs via `_legs_for_document(recognized, section_facts)`. Because
§4.1 puts health at **document scope only**, the page-scope guard does not reach the signal.

**But the page-scope *raise* does reach it, by preempting it — see §4.5's asymmetry (review B5).**
`compile_document` passes `validate_shapes` straight down to all three page compiles
(`document.py:1274,1337,1474`, RE-MEASURED), and those run at `:1274` etc. while document validation
is at `:1624`.

### §2.7 `.rq` conventions this spec must conform to — RE-MEASURED, and the first version was wrong

45 files under `vocab/queries/`. The first version claimed *"a `# GATE (CLAUDE.md §8):` header … (20
of 45; canonical form at `escalation-furnish.rq:10-12`)"*. **20 of 45 is the count of files
containing the word `AXIOM`**, which is a different population; 12 of those 20 carry no `CLAUDE.md §8`
header at all. The header convention actually measures:

```
$ grep -lF '# GATE (CLAUDE.md §8):' vocab/queries/*.rq | wc -l                 → 1   (escalation-furnish.rq)
$ grep -lF '# GATE CLASSIFICATION (CLAUDE.md §8):' vocab/queries/*.rq | wc -l  → 7   (the arc-* seven)
$ grep -l '# GATE' vocab/queries/*.rq | wc -l                                  → 8 of 45
$ grep -l 'AXIOM'  vocab/queries/*.rq | wc -l                                  → 20 of 45
```

**Two spellings exist and nothing enforces either.** `membrane-health.rq` adopts the **`# GATE
(CLAUDE.md §8):`** form of `escalation-furnish.rq:10-12`, whose header this spec's §4.3 mirrors —
chosen because that file is also the precedent for the two things `membrane-health.rq` needs: an
**inline holon-scoped justification** for `FILTER NOT EXISTS` (`:44-47`) and an explicit **SITE
CONSTRAINT on the caller** (`:48-49`).

Two further conventions, both real: **no bare decimal literal in any query body, LINTED** by
`tests/etkl/test_transform_gate.py:26-31` — which **globs `vocab/queries/*.rq` with no explicit file
list** (`:27`), so a new `.rq` is covered with **zero wiring**, and which **strips comments before
matching** (`:19-23`), so the header cannot satisfy or trip it. And a header that **names the test
pinning each claim** (`escalation-furnish.rq:31,34`), the test being written against a
**hand-computed fixture** (`tests/test_arc_queries.py:1-42`).

**No test enforces the presence of a GATE header** (`grep -rn '# GATE\|GATE (CLAUDE' --include='*.py' .`
→ no output). The header is a convention the reviewer enforces, not the suite.

`CONSTRUCT`s execute through `interpret.run(query_path, *graphs)` (`src/iladub/etkl/interpret.py:19-30`),
which copies every input graph into a fresh union — one call over the 29,999-triple stem is a full
30k-triple copy (review B7, incidental; §5.5's cost model carries it).

### §2.8 The vacuity registry's contract — MEASURED, because P1's ruling turns on it

`tests/etkl/test_vacuity_registry.py` (479 lines) implements **two** criteria over SHACL node shapes:
**criterion 1**, focus-node counting (`focus_nodes`, `:154-163`, resolving `sh:targetClass` /
`sh:targetSubjectsOf` / `sh:targetObjectsOf` only), and **criterion 2**, term reachability
(`unreachable_terms`, `:184-187` — *"body terms that appear NOWHERE in the data"*), applied only to
shapes carrying `sh:sparql` (`:202`). Registration is a **literal Python dict**, `VACUITY_REGISTRY`
(`:87-127`, nine entries), each valued by a measured prose reason. Three arms guard it:
`test_every_idle_shape_is_registered` (`:325`), the bidirectional
`test_no_registered_shape_has_gone_live` (`:337-349`), and
`test_the_registry_has_no_rows_for_shapes_that_are_not_wired` (`:352`).

**The population is NOT a glob.** `wired_shape_files` (`:133-140`) reads it *from the compile
membrane* — `compile_mod._TAB_SHAPE_FILES | _DEC_SHAPE_FILES`, five files of the ten in
`vocab/shapes/`.

**Therefore the P1 extension needs new machinery, and the ruling required this spec to say so from a
measurement rather than assume.** Four independent blocks, each measured:

| the registry's seam | why a `.rq` cannot pass through it |
|---|---|
| `shapes_graph` (`:143-147`) | `parse(format="turtle")` — a `.rq` does not parse |
| `node_shapes` (`:150-151`) | enumerates `sh:NodeShape` subjects — a `.rq` has none |
| `focus_nodes` (`:154-163`) | reads `sh:target*` off the shapes graph — a standalone query declares no target |
| `body_terms` (`:166-175`) | reads `sh:sparql` → `sh:select` off the shapes graph — a `.rq`'s text is unreachable that way |

**What IS reusable:** `vocabulary_of` (`:178-181`, predicates ∪ `rdf:type` objects of a data graph),
the set-difference of `unreachable_terms` (`:187`), the `_TERM` regex (`:63`) — which matches over
**text**, so it applies to a `.rq` body unchanged — and, decisively, the `corpus_graphs` fixture,
already `@pytest.mark.corpus` at ~5.5 min. §4.9 rules the extension **in**, at term level, riding
that fixture at **zero added runtime**, and names the fallback.

*One thing criterion 2 as built does not model:* it pronounces a whole **shape** idle. The clause
this loop needs to register does not make its query idle — `membrane-health.rq` fires and produces
health on every corpus document; only its **promotion clause** is unexercised. §4.9's registry is
therefore keyed by *(query, term)*, not by query, which is the honest shape of the claim and is what
`unreachable_terms`' own semantics already compute.

---

## §3 What proposes, what disposes, and why they are independent

**Proposes:** `vocab/queries/membrane-health.rq` — a `CONSTRUCT` that reads two kinds of evidence
already in the compiled graph (the validation act of §4.2, the held candidates of §2.2) and states
the health value that follows.

**Disposes:** `tests/etkl/test_membrane_health.py`, whose expected values are **hand-computed against
fixtures built by hand**, per §2.7 — never by running the query and recording what it said.

**Why they are independent, and the trap this avoids.** The oracle the previous handoff proposed —
*strip the health triple, re-run the `.rq`, assert byte-identical re-derivation* — is **not** a
disposer of the proposer. If the compiler mints by running that same query, strip-and-re-derive
compares `f(g)` with `f(g)`: it pins determinism, not correctness, and it is the R73 defect-5 shape.
*"Byte-identical"* is also a category error — RDF has no byte identity without canonicalisation.

That check is **kept and demoted**: it is the *not-a-stored-label* check (§7 O5). **The falsifying
oracle is discrimination** (§7 O1): three graph states that must yield three *different* values, each
expected value computed by hand from the fixture.

**One limit of O2 that the first version claimed too much for** (review P3). `graincorp-stem →
Intact` and `apple → Weakened` (§5.5) were produced by running *the same held-candidate pattern*
§4.3 uses. O2 is therefore a **reachability** check, not an independence check: if §2.2's
discriminator is the wrong reading of "held", the query and its expectations share the error. O1 is
what carries independence, and O2 must say in its own docstring that it does not.

---

## §4 The design

### §4.1 The subject and the scope

The document URI is typed **`etkl:CompiledDocumentHolon`**, a new concrete class
`⊑ etkl:DocumentHolon` — **ruled 2026-08-25**, see `docs/superpowers/2026-08-25-holon-05-b1-ruling.md`
for the decision and its rejected alternatives. It sits inside `etkl:membraneHealth`'s declared
`rdfs:domain` (`etkl-holons.ttl:88`), which is the abstract parent (`:45` — the first version cited
`:44`, which is the label). Safe to mint by §2.1.

**Document scope only.** Page-scope graphs (`{_DOC}/p{n}`) get no health triple, so a document's
signal is unambiguous. The Raw holon and the portal are `holon:06`; this loop does not touch them.

This is the first instance data the `etkl` doc-holon fabric has ever had — **it closes the
instantiation half of `R126`** (0 of 326 triples had the doc URI as a subject; 0 of 11 `rdf:type`
values were `etkl:`; the row's own citation `etkl-holons.ttl:74-88` should read `75-89`, and a third
citation of the same block at `tests/arc-manifest.ttl:1337` reads `75-86` — both are corrected by
this loop).

**What it does NOT close, stated here so no later section has to** (review B7): the subject IRI is
`_DOC = "https://example.org/etkl/doc"` (`compile.py:22`), **one constant shared by every document**,
carrying no other statement in either compiled graph. `compile_tables` and `page_doc_uri` both accept
a `doc_uri` (`compile.py:572`, `document.py:268`); `compile_document` does not (`document.py:1165`).
Threading one is **ruled out of this loop** and raised as a residue — see the B7 ruling. The two
consequences this design must carry instead are §4.3's site constraint and §4.8's shape.

### §4.2 The validation act — PROCEDURAL

**Ruled 2026-08-25 (B2):** the node records the validation **act**, not the graph's conformance
*status*. Immediately after `_validate` returns at document scope, and **before** either returning or
raising, mint into `graph`:

```
<{doc}#membrane-validation> a etkl:MembraneValidation ;
    prov:used      <{doc}> ;
    sh:conforms    <the bool, as xsd:boolean> ;
    etkl:refusingLeg "tab" , "dec" .        # 0..n — present ONLY on refusal
```

- **Why PROCEDURAL, and why it is irreducible** (CLAUDE.md §8 requires this in the code *and* the
  spec): the conformance verdict is not in the source document and not derivable from the evidence
  graph — it is the output of an external validation engine. Emitting an engine's output as typed
  RDF is *raw extraction*, the one thing CLAUDE.md §8 reserves PROCEDURAL for. It is **one triple-group from
  values already in scope** (§2.3): no engine change, no report graph, no `_deskolemize` decision.
- **THE DATATYPE IS PINNED AT THE MINT SITE** (review B6, the one finding that fails *upward*). The
  literal is built from the Python `bool` `_validate` returned — rdflib types a Python `bool` as
  `xsd:boolean` — and **never** from `str(conforms)`. A `Literal("false")` with no datatype, or with
  `xsd:string`, was measured to make a *refusing* membrane report **`Intact`**, silently, because
  SPARQL's effective boolean value of a non-empty string is `true`. §4.3 carries the second half of
  this fix and §7 O8 pins both.
- **`etkl:refusingLeg` carries `_validate`'s third element verbatim**, which §2.3 measured as the
  legs that *refused* — so a **conforming** validation carries no leg at all, and that is correct
  rather than a gap: a leg appears only when it has something to say. Range `xsd:string`, because
  the leg identity is a code-level key (`{"tab","dec"}`, `compile.py:516`); minting individuals for
  the two legs would be a vocabulary claim this loop has no use for.
- **This is the compile graph's first `prov:Activity`.** MEASURED: `prov:Activity`, `prov:used` and
  `prov:wasAssociatedWith` are minted **nowhere** in `src/`; the only PROV class ever typed is
  `prov:SoftwareAgent` (`datagrid.py:707`, `decisionlog.py:86`), every other use being the
  `prov:wasDerivedFrom` predicate. The pattern is nonetheless the repo's own norm — CLAUDE.md
  § Serialization: `dec:DecisionHolon ⊑ prov:Activity`, evidence via `prov:used`, *"don't reinvent
  provenance."*
- **Minted after validation, so never itself validated.** §2.1 is what makes that safe for a graph
  re-validated downstream, and §4.8 is what governs it instead. Contrast the established pattern one
  line above the mint site: `document.py:1609` runs `escalation-furnish.rq` **before** validation
  precisely so the membrane can refuse what it writes. Health cannot be minted there — it is derived
  *from* the verdict — so it is deliberately outside the membrane, and §4.8 owes an answer for that.

### §4.3 The derivation — AXIOM

`vocab/queries/membrane-health.rq`, a `CONSTRUCT`, run through `interpret.run` (§2.7):

```sparql
CONSTRUCT { ?doc a etkl:CompiledDocumentHolon ; etkl:membraneHealth ?health }
WHERE {
  ?act a etkl:MembraneValidation ; sh:conforms ?conforms ; prov:used ?doc .
  FILTER(datatype(?conforms) = xsd:boolean)
  BIND(EXISTS { ?cand a iladub:CandidateConcept .
                FILTER NOT EXISTS { ?pd a iladub:PromotionDecision ; iladub:reviews ?cand } }
       AS ?held)
  BIND(IF(?conforms = false, etkl:Compromised, IF(?held, etkl:Weakened, etkl:Intact)) AS ?health)
}
```

The implementer writes the file; the shape above is the contract, not the text. **Five** invariants it
must satisfy, each pinned in §7:

1. **Evidence-positive.** Every value is derived from evidence that is *present*: `Compromised` from
   a validation act saying `false`, `Weakened` from a candidate that exists, `Intact` from an act
   saying `true`. **`Intact` is never derived from the absence of a violation** — that violation is
   not in the graph, and inferring from its absence is what the gate forbids in its own words.
2. **Closed-world only within the holon.** The `FILTER NOT EXISTS` closes over `iladub:reviews`
   scoped to a bound `?cand`, and `EXISTS` closes over the graph. Licensed by *"the holon is the
   closure boundary"*.
3. **THE SITE CONSTRAINT, and its real reason** (review B7). The query is run over **one document's
   graph, never a union**. The first version justified this as closed-world scoping, which is true
   and insufficient. The binding reason is **subject-IRI collision**: `_DOC` is the same IRI for
   every document (§4.1), so a union puts two health values on one subject — measured, three triples
   on one `?doc`, `Compromised` *and* `Intact`. The header states this as a caller constraint, in the
   form `escalation-furnish.rq:48-49` already uses.
4. **Idempotent, and it never reads its own product.** No pattern in the `WHERE` mentions
   `etkl:membraneHealth` or `etkl:CompiledDocumentHolon`, so re-running over a graph that already
   carries the health triple re-derives exactly it.
5. **THE QUERY REFUSES TO GUESS** (review B6, second half). `?conforms = false` replaces `!?conforms`
   so no effective-boolean-value coercion ever runs, and the `datatype(?conforms) = xsd:boolean`
   filter makes a slipped datatype yield **no health triple at all** rather than a wrong one. Note
   the direction: the first version failed *upward* (a refusing membrane reported `Intact`); this
   fails *downward*, into the silence §4.5's third row already licenses.

**No bare decimal literal** — trivially satisfied, and enforced by the lint of §2.7 with no wiring.

The `?pd a iladub:PromotionDecision` type clause **stays** even though it is currently redundant: it
is the guard against the IRI collision of §2.2.

### §4.4 Why held candidates are the right reading of `Weakened` — and why the grounding portal is not this membrane

A candidate concept sitting in the compiled graph is a proposition **held at the document membrane**,
and that is what `Weakened` now means. *The first version grounded this in
`docs/holonic-interaction.md:55` and that citation is withdrawn entirely* (review B3): `:55` is the
`crossed ✔ — assertion` edge, the held edge is `:56`, and **both are fed by `PORTAL ==> MEM` at
`:51`** — the grounding portal's output, which this section excludes by design. The design cannot
claim as warrant a diagram edge depicting the thing it excludes. The warrant is the measurement
below, which is stronger.

**MEASURED.** `feed.py:643` lives in `ground_document` (`feed.py:618-644`), whose `validate_shapes`
**defaults to `False`**. No module under `src/iladub/etkl/` imports `feed` at all — so
`compile_document`/`compile_tables` cannot reach it; grounding is a step the caller invokes
afterwards, taking the compiled graph in and filling a **fresh** graph `g`. `ground_document` returns
a `FeedResult` of three ints (`feed.py:571-575,619`), not a graph, and **no merge site between the
two graphs exists anywhere** (exhaustive `+=` and add-loop greps over `src/ tests/ scripts/` → no
hits; corroborating `docs/superpowers/2026-08-15-r87-ruling-handoff.md:73`).

**The compile graph and the grounded graph are disjoint artifacts.** The candidates the derivation
reads are therefore exactly the region-escalation family (`holon.py:451-467`, and the cell-level
`ROUND_TRIP_FAIL` emitter at `holon.py:82-105`) — the correct population for *this* membrane, and the
reason §4.3's graph-scoped `EXISTS` is sound rather than over-capturing. Excluding the portal's
quarantine is the holon boundary being respected; the portal's own health is `holon:06`.

**And the words matter, because one of them ships** (review B8). `Weakened`/`Intact` say **nothing**
about how much of the document was read. `graincorp-stem` books 77 escalated tokens across three
`UNSUPPORTED_TABLE` bands whose verdict is nonetheless `asserted`, mints **zero** `CandidateConcept`s,
and is correctly `Intact`. So the gloss *"not everything that reached the boundary crossed it"* is
**false as stated** and must not appear in §4.6's published comment. `Intact` means **nothing is held
at the membrane**, never "fully read" — `score` (`compile.py:367-368`, token counts) and
`membraneHealth` are two different signals.

### §4.5 Where health is minted — three sites, one query, and one asymmetry

| site | verdict | what happens |
|---|---|---|
| `document.py:1624`, conforming | `true` | mint validation act → run query → add result to `graph` → return `DocumentReport` |
| `document.py:1626`, refusing | `false` | mint validation act → run query → add result to `graph` → **raise, carrying the graph** |
| validation not run (`validate_shapes=False`) | — | **no validation act, therefore no health triple** |

The third row is the design's answer to the reachability rule, and it is a *consequence* rather than
a special case: no validation means no act means the `WHERE` has no support means no health triple.
**Absence, never a fourth state** — the open-world rule doing the work.

**THE ASYMMETRY, stated out loud** (review B5, which the first version left as an unnoticed hole).
`compile_document` passes `validate_shapes` straight down to every page compile
(`document.py:1274,1337,1474`, §2.6), and the page gate raises a bare `AssertionError` at
`compile.py:1173` — **before** document validation at `:1624` is ever reached. §9 deliberately keeps
that site unchanged, and the catcher census (§2.4) confirms nothing between them intercepts it.
**Therefore: `Compromised` reports DOCUMENT-scope refusals only. A page-level violation aborts the
document first — no validation act, no health triple, no carried graph, and a bare `AssertionError`
rather than `MembraneRefusal`.** That is the *more* likely refusal of the two, since page shapes
(`tab`) are where the violations live while the document leg is `dec` plus `tab` over merged content.
It is a **named residue** (§11), not a gap, and it does not require minting health at page scope.

**The refusal carries the graph via a subclass, not a softened raise.** Introduce
`membrane.MembraneRefusal(AssertionError)` with `.graph` and `.legs`, and raise it at
`document.py:1626` in place of the bare `AssertionError`. Because it is a **subclass**, the one
measured catcher (§2.4) keeps working unchanged. The guard is **not** softened, downgraded, or made
conditional: CLAUDE.md § Producer-side guards licenses deleting a guard only when the membrane
provably validates every product of that producer, and here it demonstrably cannot — a refusing
product never becomes a returned `DocumentReport` at all. This is the opposite of the R102 pattern:
not a guard that looks redundant, but the only thing between a non-conforming graph and its caller.

### §4.6 The vocabulary amendment — four artifacts, one act

**Ruled 2026-08-25 (B3):** the re-reading of `Weakened` is a **semantic amendment to the health
model**, not a comment tweak, and it is carried completely. `etkl:CleanDocumentHolon`'s comment
(`:65`) is **not** in the set — B1 removed it, because the loop no longer claims the compile graph is
one.

| # | artifact | why it is in the set |
|---|---|---|
| 1 | `etkl:Weakened`'s `rdfs:comment` (`etkl-holons.ttl:82`) | *"warnings are present"* is underivable — §2.5 |
| 2 | `etkl:MembraneHealth`'s `rdfs:comment` (`:77`) | *"the result of validating its interior against its membrane"* contradicts the design too |
| 3 | `docs/holonic-interaction.md:160-161` | the criterion's own `prog:source`; §8 item 7 already moves this bullet, so **word it in the same act** |
| 4 | `tests/arc-manifest.ttl:354`'s `prog:statement` | a verbatim join of (3) — *"from validation results"* excludes held candidates |

All four are worded per §4.4's last paragraph: **held propositions**, never *everything that reached
the boundary*. `owl:versionInfo` `0.1.0` → `0.2.0` (`:33`) covers these plus §4.7's three new terms.

**Amending a criterion's `prog:statement` in the very loop that flips it to `met true` gets its own
comment in the manifest saying so**, in the MEASURED form the file already uses (`dec:16`'s block at
`:838-856` is the exemplar). A silent edit here would be indistinguishable from moving the goalposts.

### §4.7 The three new owned terms

`etkl:CompiledDocumentHolon` (§4.1), `etkl:MembraneValidation` and `etkl:refusingLeg` (§4.2), all in
`vocab/ontology/etkl-holons.ttl`. Per the B1 ruling, `CompiledDocumentHolon`'s `rdfs:comment` says
what the compile-scope product *is* and, per B8, **must not claim the graph is fully read**.

**MEASURED, so the plan need not re-derive it:** `@prefix prov:` is **already declared** at
`etkl-holons.ttl:9` and used by **no triple** in the file, so `⊑ prov:Activity` is its first real use
and needs no prefix edit. `tests/test_source_ownership.py`'s three assertions are **HGA-specific
only** — no test restricts which external vocabularies a core ontology may reference, and none
constrains which file a term lives in — so all three stay green. The one live risk is that test's
parse arm (`:67-68`): a Turtle syntax error surfaces there as an `AssertionError`.

### §4.8 The health signal's own shape

**Ruled 2026-08-25 (B7).** The health signal is minted *after* validation and is therefore governed
by nothing — for a project whose §3 principle is SHACL-enforced epistemics, that is worth a decision
rather than a silence. Ship a minimal shape in **`vocab/shapes/etkl-shapes.ttl`**:

```
etkl:MembraneHealthShape a sh:NodeShape ;
    sh:targetClass etkl:CompiledDocumentHolon ;
    sh:property [ sh:path etkl:membraneHealth ; sh:maxCount 1 ;
                  sh:in ( etkl:Intact etkl:Weakened etkl:Compromised ) ] .
```

- **That file, deliberately.** It is the one shape file with `etkl:` references and it is **not
  loaded** by the compile membrane (§2.1) — so the shape inherits the non-loading, and §2.1's safety
  argument is untouched. **It is validated in the test, NOT wired into the membrane**: wiring it
  would re-open §2.1 *and* be vacuous anyway, since health does not exist when validation runs.
- **`owl:FunctionalProperty` is rejected**, not merely unused: inference is off
  (`membrane.py:124-125`), so it would do nothing; and under a reasoner it would *entail
  `owl:sameAs`* between two health values rather than refuse them — B6's failure direction again.
- **The conforming example and the negative case must be hand-wired.** MEASURED:
  `tests/test_vocab_shapes.py` (66 lines) enforces the CLAUDE.md pair rule with **four hard-coded
  paths and no discovery** — no glob, no `parametrize` — and `etkl-holons.ttl` has **no conformance
  pair there at all** (`etkl-shapes.ttl` is validated against `etkl.ttl`). **Nothing will demand the
  pair; the loop must add both files and the two test functions explicitly**, or the shape ships
  unexercised and becomes its own vacuity row.

### §4.9 The promotion clause's vacuity tripwire

**Ruled 2026-08-25 (P1): in scope**, and §2.8 measured what that costs. The extension is **term
level**, keyed by *(query file, term)*, and lives **in `tests/etkl/test_vacuity_registry.py`** so it
rides the existing `@pytest.mark.corpus` `corpus_graphs` fixture at **zero added runtime**.

What it reuses, unchanged: `vocabulary_of` (`:178-181`), the set-difference of `unreachable_terms`
(`:187`), and the `_TERM` regex (`:63`) — which matches over text, so a `.rq` body needs no new
extractor. What is genuinely new: a population enumerator over `vocab/queries/*.rq` and a second
registry dict with its own two arms, mirroring `test_every_idle_shape_is_registered` and
`test_no_registered_shape_has_gone_live` (`:325`, `:337`).

The row this loop registers: `membrane-health.rq` names `iladub:PromotionDecision` and
`iladub:reviews`, **neither of which appears in any compiled graph** (§5.6). The bidirectional arm
then fails the suite the day a proposer is wired into the corpus sweep and those terms go live —
forcing de-registration rather than leaving the residue to a human's memory. R106's row says *"the
rule that catches it is prose"*; this is the instrument that stops it being the second instance.

**THE FALLBACK, named per the ruling:** if the enumerator plus second registry cannot be built
without touching `shapes_graph`, `node_shapes`, `focus_nodes` or `body_terms` — the four seams §2.8
measured as SHACL-shaped — **stop, and take a register row instead.** Rewriting the existing
machinery is out of scope for a loop already minting three terms and a shape.

### §4.10 The criterion

`tests/arc-manifest.ttl:352-359`: flip `prog:met false` → `true` with a MEASURED comment block in the
`dec:16` form (`:838-856`); **add `prog:metOn`** and derive `prog:retrospective` from `declaredOn
2026-06-23` vs `metOn`, as that convention requires. Keep the pre-declared
`prog:oracleTest "tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health"`
**exactly as written** (`:359`) and make it exist. **Add `prog:oracleArtifact "vocab/queries/membrane-health.rq"`**,
which this criterion has never had. Amend `prog:statement` per §4.6 row 4, with its own comment.

---

## §5 The vacuity hazards, and how each is answered

| # | hazard | answer |
|---|---|---|
| 1 | **`Weakened` unreachable** — no `sh:severity` anywhere (§2.5) | re-read as held propositions (§4.4), which are measured to exist on real documents |
| 2 | **The domain is uninstantiated** (`R126`) — nothing is ever an `etkl:` type | §4.1 mints the subject, safely per §2.1 |
| 3 | **`Compromised` unreachable** — a refusing membrane raises, so no report a caller can hold ever carries it | §4.5 mints *before* the raise and the error carries the graph — **for document-scope refusals only**, per that section's asymmetry |
| 4 | **`Intact` vacuous over zero shapes** — §5.4 | REFUTED: the `dec` leg is unconditional |
| 5 | **The promotion clause never fires** — §5.6 | O3 exercises it on a real path; §4.9 registers the corpus-sweep residual as a machine tripwire |

### §5.4 The zero-legs hazard — MEASURED, and REFUTED

The fear was: if `_legs_for_document` can return an empty tuple and `_validate` then reports
`conforms=True` over zero shapes, an `Intact` derived from it claims conformance from zero focus
nodes — `R106` exactly. **It cannot.**

`_legs_for_document` is a one-line total function (`document.py:1142-1162`):

```python
return ("tab", "dec") if (recognized or section_facts) else ("dec",)
```

Two possible values, and **`"dec"` is unconditional** — that is R102's fix. The only leg that can be
dropped is `tab`. Pinned exhaustively over all four input combinations by
`tests/etkl/test_document_membrane_gate.py:22-33`, and called from nowhere else in `src/` or `tests/`.

And the empty case is not a silent pass anyway — it is a **loud latent crash**.
**RE-MEASURED as ONE run on ONE graph** (the first version pasted two lines the review showed could
not have come from a single run; the review was right that the pasted form was not reproducible, and
**wrong that it could never be** — its own repro used an *empty* graph, where
`_validate(g, ("dec",))` dies earlier at `membrane.py:195` with `ValueError: … input is empty`. On a
graph with **one arbitrary triple**, both lines are one run):

```
$ .venv/bin/python scratch/zero_legs.py     # g = Graph(); g.add((urn:ex:s, urn:ex:p, urn:ex:o))
graph size = 1
_validate(g, ("dec",)) -> (True, '@prefix sh: <http://www.w3.org/ns/shacl#> .\n_:1 a sh:ValidationReport ;\n\tsh:conforms true .\n', ())
_validate(g, ())       RAISED: IndexError tuple index out of range     # compile.py:523
```

`compile.py:523` is `text = verdicts["tab"][1] if "tab" in verdicts else verdicts[legs[0]][1]`: with
`legs=()`, `verdicts={}` and `refusing=()`, so control reaches the conforming branch and indexes
`legs[0]` on an empty tuple. **The plan must paste this run, not this quotation** (rule 2).

**So `Intact` at document scope is always backed by at least the `dec` leg.** Measured on real input:
`graincorp-capacity` → `('dec',)`; `who-wfa-boys` → `('tab','dec')`. Consistent with the R102 closure
row (`docs/superpowers/residues-closed.md:26`). Five of seven corpus documents are inferred from that
row rather than re-run — §10 seam 1.

**Consequence for the design: none — §4.2 mints unconditionally at document scope**, and the third row
of §4.5's table is reached only by `validate_shapes=False`. **O4 keeps its `validate_shapes` form and
drops the zero-legs extension**; there is nothing there to pin.

*The residual is not a vacuity but a latent crash:* `_validate` on an empty legs tuple raises
`IndexError` rather than refusing or conforming. Unreachable today, guarded by one total function.
A residue row (§11), not a fix in this loop.

### §5.5 `Intact` and `Weakened` reachability — MEASURED across the whole corpus

All 27 corpus pages and **all seven documents** compiled; 0 raised. Document scope, held candidates
by the §2.2 pattern:

| document | triples | held | → |
|---|---|---|---|
| `graincorp-stem-2026-07-31` | 29,999 | **0** | `Intact` |
| `cbh-stem-2026-08-03` | 12,153 | **0** | `Intact` |
| `ons-index-of-services-2026-02` | 11,076 | **0** | `Intact` |
| `graincorp-capacity-2026-08-04` | 5,705 | **0** | `Intact` |
| `apple-fy2026q3-statements` | 3,788 | **11** | `Weakened` |
| `bfs-population-bilan-2023` | 8,244 | **10** | `Weakened` |
| `who-wfa-boys-zscore-0-5` | 8,098 | **3** | `Weakened` |

**Both values are reachable on real input, 4 documents to 3.** The two `Intact`/`Weakened` rows were
**independently reproduced during the review, to the triple** (`graincorp-stem` 29,999/0 in 164.9 s;
`apple` 3,788/11 in 36.1 s), so the table is measured twice by two sessions.

**The cost this imposes on O2, and the cheaper vehicle** (review P3). Those two specimens add
**~3.5 minutes** to a suite whose baseline is 2386.82 s. The caption-wrap fixture compiles at document
scope in **1.9–2.6 s** — 15–70× cheaper — and is the right vehicle for every leg that does *not*
specifically require a corpus document. O2 requires corpus documents for `Intact` and `Weakened`
because reachability *on real input* is the whole claim; nothing else should reach for one.

### §5.6 The discriminator at compile scope — and the consequence the first version got wrong

**`promoted = 0` in all 34 measurements** (27 pages + 7 documents). In every compile-only graph, held
count and total candidate count are the **same number**: no `iladub:PromotionDecision` exists there at
all. The 385/167 partition of §2.2 arises only *after* `ground_document`, in the graph §4.4 measured
as disjoint.

**The cause is confirmed exactly:** the `promote.py` emitters (`:79,126,170`, reached from
`reshape.py:221`, `span.py:79`, `rowrole.py:230`) are **proposer-driven**, and a bare
`compile_tables`/`compile_document` call passes no `span_proposer`/`row_role_proposer`. So §4.3's
`FILTER NOT EXISTS` cannot fire **on the default corpus sweep**.

It is **not dead code**, and it must not be dropped: removing it would be correct on today's corpus
and **wrong the first time a proposer is wired**, silently reporting `Weakened` for a document whose
propositions were all promoted.

> **WITHDRAWN (review P1).** The first version concluded *"O3 is a fixture-only oracle … it cannot be
> pinned on real input, and the plan must not pretend otherwise by reaching for a corpus document."*
> **That conflated *corpus document* with *real execution path*.** A test already exists that compiles
> with a proposer wired, at the default `validate_shapes=True`, and asserts the promotion in the
> committed graph: `tests/etkl/test_rowrole_integration.py:106`
> (`test_caption_wrap_report_asserts_with_a_resolving_proposer`). At **document** scope — which no
> existing test does, but `compile_document`'s signature supports (`document.py:1165`) — the review
> measured **`PromotionDecision: 2, held: 0, promoted: 2` in 2.6 s**, through the real membrane.

**O3 uses that vehicle** (§7). The true residual is narrower than the first version claimed: the
clause is unexercised **on the corpus sweep**, and §4.9 turns that into a machine tripwire rather than
prose.

### §5.7 Document health is NOT the union of page healths — and that is correct

MEASURED: `cbh-stem` has **4** held candidates at page scope and **0** at document scope;
`graincorp-stem` 0+1+1 → **0**; `apple` 5+5+5 = 15 → **11**.

Cause measured for cbh: the page-scope candidates are `doc#region1,3,5,7`; the document report's
`repaired_bands` are `((0,1),(0,3),(0,5),(0,7))` and those four regions come back
`verdict='asserted'` — the **section-repair pass** (`document.py:1337`) re-compiles the band and its
assertion replaces the proposition in the merged graph. (Apple's 15 → 11 was not traced.)

**A page-scope `Weakened` can therefore become a document-scope `Intact`, and that is the right
answer**: the proposition was promoted into an assertion by repair, so it is no longer held at the
membrane. It is also the second reason §4.1 puts health at document scope only — a per-page signal
would report a weakness the document no longer has.

---

## §6 Gate classification (CLAUDE.md §8)

| step | class | justification |
|---|---|---|
| validation act (§4.2) | **PROCEDURAL** | raw extraction: an external engine's output → typed RDF. Not derivable from evidence; not a reading judgement. One triple-group from values already in scope. Stated in the code and here, as CLAUDE.md §8 requires |
| health derivation (§4.3) | **AXIOM**, derivation form | `CONSTRUCT` over an RDF evidence graph, open world, evidence-positive, idempotent. Its one closed-world guard is holon-scoped and justified inline |
| `MembraneHealthShape` (§4.8) | **AXIOM**, constraint form | closed-world, and correctly so: it validates what a *finished* health signal may look like (cardinality + enumeration). Not a derivation — it never infers a value from absence |
| `MembraneRefusal` + wiring (§4.5) | **PROCEDURAL** | exception plumbing; no decision is taken in it |
| the vacuity tripwire (§4.9) | **not gated** | it is test machinery asserting a property of the suite, not a decision about a document. Stated so a reviewer does not have to ask |

**No NEURAL step.** Nothing here is a perceptual or underdetermined reading judgement. **No tuned
constant appears anywhere in this design** — and the `.rq` lint of §2.7 enforces it mechanically, with
no wiring.

---

## §7 The falsifying oracles

All in `tests/etkl/test_membrane_health.py` unless stated. Every one carries a `## FALSIFICATION`
block: remove or invert what it pins, show it **failing**, restore, show green. **No falsification
evidence ⇒ the task review fails.**

- **O1 — DISCRIMINATION (the falsifying oracle).** Three hand-built fixture graphs — conforming with
  no candidates, conforming with one held candidate, non-conforming — must yield **three different**
  values. Expected values computed by hand from the fixture, never by running the query first.
  *Falsify:* collapse the `IF` to a constant; O1 must fail.
- **O2 — REACHABILITY on real input.** Each of the three values is produced by at least one **real**
  execution path, not only by a fixture: `Intact` from `graincorp-stem-2026-07-31`, `Weakened` from
  `apple-fy2026q3-statements` (11 held) — both specimens measured twice (§5.5) — and `Compromised`
  from a forced non-conforming graph at the real raise site (**§10 seam 6: the vehicle does not exist
  yet**). This is the R87 vacuity-registry question asked of a derivation instead of a shape. **If a
  value cannot be produced from real input, this test fails and says which — it does not fall back to
  a fixture.** Its docstring must state that O2 is a *reachability* check and **not** an independence
  check, because its expectations were derived with the pattern under test (§3).
- **O3 — PROMOTION IS NOT HELD, on a real execution path.** A candidate reviewed by an
  `iladub:PromotionDecision` must not make a document `Weakened`. **Vehicle: the caption-wrap fixture
  compiled at document scope with a proposer wired**, per §5.6 — *not* a hand-built graph, and *not*
  a corpus document. *Falsify:* delete the `FILTER NOT EXISTS`; O3 must fail. This pins §2.2's
  discriminator, and it is the reason O1 alone is not enough — a query that ignores promotion passes
  O1.
- **O4 — ABSENCE, NOT A FOURTH STATE.** A document compiled with `validate_shapes=False` carries
  **no** `etkl:membraneHealth` triple and **no** `etkl:CompiledDocumentHolon` type. `validate_shapes`
  is the only route into this state — §5.4 refuted the zero-legs one. *Falsify:* mint the validation
  act unconditionally; O4 must fail.
- **O5 — NOT A STORED LABEL.** Strip the health triple and the type triple from a compiled graph,
  re-run the `.rq`, and assert the re-derived triples equal what was stripped, compared **as sets of
  triples** (not bytes — §3). This answers the stored-label objection for the *health* triple and
  nothing else; it is explicitly **not** the falsifying oracle, and it does not speak to the
  validation act, which §4.2 makes immutable by construction rather than by test.
- **O6 — THE MINTED NODES PERTURB NOTHING.** Re-validating a graph that carries the health triple, the
  type triple and the validation act yields the same verdict as before they were added, on both legs.
  This is §2.1 held as a regression rather than a one-off measurement.
- **O7 — THE REFUSAL CARRIES THE GRAPH.** A forced non-conforming document raises `MembraneRefusal`;
  the raised object's `.graph` contains `<doc> etkl:membraneHealth etkl:Compromised`; and
  `except AssertionError` still catches it. *Falsify:* revert to a bare `AssertionError`; O7 must fail.
  **Shares §10 seam 6 with O2's third leg** — this is the highest-risk oracle in the set.
- **O8 — THE DATATYPE CANNOT SLIP (review B6, both halves).** *Mint side:* the conformance literal in
  a real compiled graph is `xsd:boolean`. *Read side:* a graph whose validation act carries
  `Literal("false")` — no datatype, or `xsd:string` — yields **no health triple**, and specifically
  **not `Intact`**. *Falsify:* replace the mint with `Literal(str(conforms))` and drop §4.3's
  `datatype` filter; O8 must fail, and the failure must be the silent-`Intact` one. This is the only
  finding in the review that failed *upward*.
- **O9 — THE SHAPE REFUSES A MALFORMED SIGNAL** (in `tests/test_vocab_shapes.py`, hand-wired per
  §4.8). A worked example conforms; a negative example carrying two health values, and one carrying a
  value outside the three individuals, **must fail**. *Falsify:* delete `sh:maxCount 1` / `sh:in`; O9
  must fail.

---

## §8 Definition of done

1. All nine oracles green, each with its falsification evidence.
2. `vocab/queries/membrane-health.rq` exists, with a `# GATE (CLAUDE.md §8):` header (§2.7's n=1 form)
   naming its classification, its holon-scoped-negation justification, its **caller site constraint
   with the collision as its reason** (§4.3.3), and **the test that pins each claim**.
3. `tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health` exists under
   **exactly** the pre-declared name (`arc-manifest.ttl:359`) and is green.
4. `tests/arc-manifest.ttl` `holon:05` flipped to `prog:met true` with its MEASURED comment block,
   `prog:metOn`, a derived `prog:retrospective`, the new `prog:oracleArtifact`, and the amended
   `prog:statement` carrying its own comment (§4.10, §4.6).
5. Three new terms declared, `etkl:Weakened`'s and `etkl:MembraneHealth`'s comments amended,
   `owl:versionInfo` bumped `0.1.0` → `0.2.0` (§4.6, §4.7).
6. `etkl:MembraneHealthShape` shipped **with its conformance pair hand-wired into
   `tests/test_vocab_shapes.py`** (§4.8) — nothing discovers it.
7. `docs/holonic-interaction.md:160-161` moves out of *"Planned work"* (heading at `:158`) **and is
   reworded in the same act** (§4.6 row 3).
8. §4.9's tripwire shipped, **or** its named fallback taken and recorded — not silently dropped.
9. **Full suite green**, run in the repo venv (`.venv/bin/python -m pytest -q`; note `pytest-timeout`
   is not installed, so `--timeout` is not a valid flag, and `timeout` is not on this machine's PATH).
   **Baseline measured 2026-08-25 before any implementation: `1312 passed, 7 skipped, 1 xfailed` in
   2386.82 s.** The loop's own run must match or exceed the passed count.
10. §11's residues appended, and **`R126` struck as closed with its evidence recorded in place** — not
    deleted (CLAUDE.md § Deferred residues).

---

## §9 What this loop does NOT do

- **It does not give the grounding portal a health signal.** `feed.py:643`'s membrane guards a
  different graph behind a different boundary (§4.4), and `python -O` erases it. `holon:06` territory,
  and a residue this loop raises.
- **It does not give page-scope graphs health** (§4.1), does not mint health at the page-scope raise
  site (`compile.py:1173`), and does not touch the page-scope skip guard (§2.6). **The consequence is
  §4.5's asymmetry, and it is stated rather than left to be discovered.**
- **It does not fix the shared `_DOC` document IRI** (§4.1) — the fix is a signature change to
  `compile_document`, ruled out and raised as a residue.
- **It does not widen `membrane.validate`'s `(bool, str)` return, and it does not resolve where
  `_deskolemize` would run on a graph.** §2.3 makes both unnecessary.
- **It does not rewrite the vacuity registry's SHACL-shaped machinery** (§2.8) — §4.9 adds beside it
  or takes the fallback.
- **It does not score the `holon:05 → holon:01` proposed edge.** Adding `prog:oracleArtifact` (§4.10)
  may make the edge groundable — it was failing A1 and A2 — but measuring that is the arc instrument's
  job. Note it; do not act on it.
- **It does not fix the latent `IndexError`** in `_validate` on an empty legs tuple (§5.4).
- **It does not add a fourth health value**, and it does not report health where nothing was validated
  (§4.5, O4).

---

## §10 The seams the plan must MEASURE, not assume

Named per rule 3 — **which fact to measure, not the answer**:

1. **The five corpus documents whose legs tuple is inferred, not measured** (§5.4). The two that were
   run agree with the R102 closure row; the other five are read off it. ~320 s to close.
2. **The catcher census, re-run** (§2.4, §4.5). `MembraneRefusal` changes an interface, and *"the only
   catcher today"* is exactly the claim `enumerating-before-claiming` exists to make you re-run. It has
   now been missed **once** already — the six `pytest.raises(AssertionError)` sites.
3. **Which object `graph` names at the raise site.** `compile.py:1115` rebinds it on one path (§2.4);
   `document.py:1609` uses in-place `+=`. Measure at `document.py:1624` specifically — do **not** carry
   the page-scope answer across.
4. **Whether `DocumentReport` construction is still by keyword** (`document.py:1636-1639`) and
   `CompilationReport` still positional (`compile.py:1175`). Re-check before adding anything to either.
5. **Whether the four `Intact` documents and three `Weakened` ones still split that way** when O2 is
   written (§5.5). The counts are small and the section-repair interaction of §5.7 moves them; re-run
   the two specimens rather than trusting the table.
6. **THE REFUSAL VEHICLE — the highest-risk seam in this spec, and the first version was silent on it**
   (review B4). O2's `Compromised` leg and O7 both need a document that **really refuses**, and
   **MEASURED: no test in the tree drives `compile_tables` or `compile_document` to raise**
   (`grep -rn -B3 "compile_tables(\|compile_document(" tests/ | grep -i raises` → no output). Every
   near-precedent avoids the raise site: `test_membrane_equiv.py:108,152` compiles with
   `validate_shapes=False` and mutates afterwards; `test_compile_membrane_shapes.py:95,123` calls
   `_validate` directly on hand-built graphs; `test_escalation_wiring.py` asserts on graph contents.
   **The fact to measure:** *what is the smallest real graph mutation that makes the document leg refuse
   at `document.py:1624`, and is it reachable without `validate_shapes=False`?* The candidates are
   `test_membrane_equiv.py:115-145`'s `_mutations` (`drop-onPage`, `blank-cellText`, `drop-bbox`,
   `orphan-unit-marker`) — but they are applied *after* a bypassing compile, and the plan must establish
   whether any can be applied *before* validation on a real path.
   **The trap to refuse:** monkeypatching `validate`/`_validate` to return `False` is the R73 defect-5
   shape — a test that passes with its subject deleted, because nothing real produced the refusal.
7. **Whether §4.9's enumerator can be built without touching `shapes_graph`, `node_shapes`,
   `focus_nodes` or `body_terms`** (§2.8). If it cannot, take the named fallback — do not rewrite them.

---

## §11 The residues this loop raises, and the one it closes

Tally snapshot **`(24/116 closed)`**, re-counted 2026-08-25 against `docs/superpowers/residues.md`
(116 rows, 24 with status `closed`; the index uses a status column, **not** `~~strikethrough~~`, which
returns 0 and is the wrong instrument). Ten numbers between R1 and R96 were never issued, so **the next
number to issue is R127**.

**Closed by this loop:** **`R126`** — *"the whole `etkl` doc-holon fabric is declared vocabulary with
ZERO instance data"*. §4.1 mints the first instance datum. Strike the number, record the evidence in
the row, **do not delete it**. Its two mis-cited line ranges (`etkl-holons.ttl:74-88` in the row,
`75-86` at `arc-manifest.ttl:1337`) are corrected to `75-89` in the same act.

**Raised, each with what would close it:**

1. **Page-scope refusal preempts document-scope refusal** (§4.5, review B5). `Compromised` reports
   document-scope refusals only; a page-level violation aborts the document first and escapes as a bare
   `AssertionError` from `compile.py:1173`. *Closes when:* the page-scope site either mints health or
   raises `MembraneRefusal` too — which requires deciding whether a page graph is a holon with its own
   membrane health, i.e. `holon:06`.
2. **Every compiled document shares one document IRI** (§4.1, review B7). `_DOC` is a constant;
   `compile_document` takes no `doc_uri`; the health subject carries no link to the `…/doc/p{n}` URIs
   holding all the content. *Closes when:* `compile_document` threads a `doc_uri` — 5 files hardcode the
   literal, so the blast radius is measured and small, but it is a URI-identity change.
3. **`_validate` raises `IndexError` on an empty legs tuple** (§5.4). Unreachable today, guarded by one
   total function. *Closes when:* `_validate` refuses or conforms explicitly on `legs=()`.
4. **The grounding portal has no health signal** (§9). *Closes with* `holon:06`.
5. **The promotion clause is unexercised on the corpus sweep** (§5.6) — **raised ONLY if §4.9's fallback
   is taken.** If the tripwire ships, this is a machine guard and not a residue, and the spec says so
   rather than opening a row that is already closed.
