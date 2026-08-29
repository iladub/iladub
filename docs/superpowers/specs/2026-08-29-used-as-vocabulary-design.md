# Used as vocabulary, not merely named — closing `R142`, `R143`, `R117`, `R144`

**Date:** 2026-08-29 · **Branch base:** `register-corrects-r142-r143` at `b2fd60e`
**Predecessor:** `docs/superpowers/specs/2026-08-26-the-query-names-a-declared-term-design.md` (`R135`,
merged PR #130)
**Register at authoring:** 27 closed / 135 rows

**Doc impact: increment.** The declaration membrane grows a second artifact family and a second
demand; `docs/wiki/concepts/` gains no page in this loop, and no released assertion changes. Nothing
here contradicts a published page, so this does not block a release tag.

---

## §1 The question

`R135` shipped a membrane that refuses an authored SPARQL query naming a term no owned ontology
declares. Its population is `vocab/queries/*.rq` and nothing else, so a shape, an example, a test
fixture or an alignment module naming an undeclared owned term is invisible to it — the same defect
class the instrument was built to catch, in the file families it does not look at (`R143`).

Extending the population to `.ttl` is not a one-line change, and the reason is the loop's subject:

> **What licenses a membrane to demand that an owned IRI be declared?**

Naively, *occurrence*: the term appears in a tracked file, so demand a declaration. Measured over the
tree that yields 203 demands, and roughly three quarters of them are category errors — the arc mints
`prog:criterion:holon:05` inside its own vocabulary namespace, `vocab/shapes` names 63 SHACL shape
nodes, `sh:declare` mints 10 prefix nodes. None of these is vocabulary; none should ever need an
ontology declaration. A membrane that demanded them would be refused on sight, and the obvious
remedy — filter the ones that "look like" instances — is a tuned heuristic answering a
classification question, which CLAUDE.md §8 makes a defect by its own words.

**The answer this loop adopts is positional: a term must be declared when the graph USES it as
vocabulary.** Vocabulary-ness is not a property of a name, a namespace or a file; it is a *role* a
term occupies in a triple, and RDF already expresses it.

A second question falls out of the first and is answered separately in §4.1, because the first
answer provably cannot reach it: an alignment module's owned term is always a **subject**
(`etkl:CleanDocumentHolon rdfs:subClassOf holon:DataHolon`), so it occupies no vocabulary role at
all. That is `R117`, and §2.5 shows it has a live instance.

---

## §2 What is measured before anything is designed

Every figure below was produced by a script under the session scratchpad and **re-run by the spec
author independently of the subagent that first produced it**. Commands are quoted; nothing here is
read off the register.

The population, fixed once:

```
$ git ls-files '*.ttl' | wc -l      136        # ontology 13 (6 align), shapes 11, tests 62,
$ git ls-files '*.rq'  | wc -l       48        #   examples 48, demo 2 ;  queries 46 + tests 2
```

### §2.1 The role rule, stated before it was run (M1)

An owned IRI occupies a **vocabulary role** in a graph if either

* **(a)** it appears in the **predicate** position of any triple; or
* **(b)** it appears in the **object** position of a triple whose predicate is one of
  `rdf:type`, `rdfs:subClassOf`, `rdfs:subPropertyOf`, `rdfs:domain`, `rdfs:range`,
  `owl:equivalentClass`, `owl:equivalentProperty`, `owl:onProperty`, `owl:someValuesFrom`,
  `owl:allValuesFrom`, `sh:targetClass`, `sh:path`, `sh:targetSubjectsOf`, `sh:targetObjectsOf`,
  `sh:class`, `sh:datatype`.

Otherwise it occupies **node role only** in that graph. Role is per-graph; vocabulary role is a
union over files (`∃ file`). No name pattern, no string test on the local name, no threshold.

### §2.2 The rule's yield over the whole tree (M2)

```
tracked .ttl = 136   tracked .rq = 48
declaring files = 7   declared owned terms = 354
distinct owned IRIs over all .ttl = 557
VOCAB-ROLE and UNDECLARED = 53
Counter({'…/progress#': 21, '…/corpus#': 18, '…/docgov#': 13, '…/etkl#': 1})
```

**53 demands, against 203 under naive occurrence.** 150 of the 203 (73.9%) collapse to node role
only: 63 SHACL shape nodes, 61 arc instance IRIs, 10 `sh:declare` prefix nodes, 4 ontology/named-graph
IRIs, and 12 that need judgement (§2.6).

**Zero false positives were found.** Five owned IRIs reach vocabulary role solely as the object of
`rdf:type`; four are declared `owl:Class`, the fifth is the live leak of §2.4. Six more reach it via
`sh:targetSubjectsOf`/`sh:class` and all six are declared. No owned IRI is used as a SHACL metaclass
anywhere, and `sh:node` with an owned object has **zero** occurrences — so `X a sh:NodeShape` puts
nothing owned into vocabulary role, which is why the 63 shape nodes fall out on their own rather
than by being filtered.

### §2.3 The rule reproduces `prog:`'s 21 by an independent method (M3)

`R142`'s corrected row states the `prog:` vocabulary is 21 terms and the `docgov:` vocabulary 23,
derived by a hand census over prefixed names. The role rule returns **21 for `prog:`, term for
term** — the same set, from graph structure rather than from lexical scanning. This matters more
than the number: the census proposed, the rule disposed, and they agree without sharing a method.

For `docgov:` the rule returns 22, not 23. **The census is right and the rule is one term short**,
for a reason that is measured and repaired in §4.4: the sole blank-node `sh:path` in the whole tree,
`vocab/shapes/doc-governance-shapes.ttl:93`

```turtle
sh:path [ sh:alternativePath ( dg:cites dg:citesExternal ) ] ;
```

hides `docgov:citesExternal` behind a list. Its sibling `docgov:cites` survives only by accident,
because `docgov-staleness-*.rq` also names it.

### §2.4 A live leak, found by the rule (M4)

```
$ git grep -n "etkl:Contract\b"
examples/federation/doc-a-contract.ttl:4:tx:contract-a a etkl:Contract ;
examples/federation/doc-b-contract.ttl:4:tx:contract-b a etkl:Contract ;
```

The ontology declares `etkl:SemanticDataContract` (`vocab/ontology/etkl.ttl:37`). `etkl:Contract` is
declared nowhere and referenced nowhere else in tracked non-evidence files. **This is the RED the
loop starts from**, and it is the `R143` defect class with a real instance, in the family the `.rq`
instrument cannot see.

### §2.5 `R117` has a live instance — `R144` is wrong (M5)

```
$ sed -n '13,18p' vocab/ontology/tab-fno-align.ttl
tab:aggFnSum     rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#sum> .
tab:aggFnMean    rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#avg> .
tab:aggFnMin     rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#min> .
tab:aggFnMax     rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#max> .
tab:aggFnCount   rdfs:seeAlso <http://www.w3.org/2005/xpath-functions#count> .
tab:aggFnProduct rdfs:seeAlso tab:product .

$ git grep -ln "aggFn"
docs/superpowers/plans/2026-07-10-loop-a1-core-reshape-recipe-oracle.md      # evidence class
docs/superpowers/plans/2026-07-14-declarative-transform-substrate.md         # evidence class
vocab/ontology/tab-fno-align.ttl
```

Six owned IRIs whose **only** occurrence in any non-evidence tracked file is a dangling alignment.
No non-align ontology declares them; no Python and no query names them.

**`R144` states, as a measurement, that `R117`'s hypothetical is unrealized — "the oracle gap is
real, the leak is absent." That is false, and has been since `tab-fno-align.ttl` was written.**
`R144` must be **corrected in place and then struck**, not merely struck: a row that recorded an
absence which was never absent is exactly the stale-row failure `R144` was raised to prevent, and
striking it silently would erase the evidence that the register's own guard did not hold. The
correction is the value; the closure is bookkeeping.

`R144`'s premise was not careless — `R135`'s M5 looked for the instance and did not find it. It
looked with an `.rq`-shaped instrument, in the one family that instrument cannot read.

### §2.6 Where the rule stops — the refutation of its negative half (M6)

**`vocabulary role ⇒ must be declared` is sound. `node role only ⇒ need not be declared` is NOT**,
and three measured classes refute it:

1. **Align subjects** (§2.5). Align family vocabulary-role terms: **0**. Node-role-only and
   undeclared: **10**. That 10 reconciles with §4.1's 9 exactly, and the arithmetic is worth
   stating so a reviewer does not read a contradiction: 9 are undeclared owned **subjects** (6
   `tab:aggFn*` + 3 `owl:Ontology` document IRIs), and the tenth is `tab:product`, undeclared and
   appearing only as an **object** — which is why §9 records it as reached by neither demand. The
   rule is structurally blind here; §4.1 adds the second demand.
2. **Blank-node SHACL paths** (§2.3). One occurrence, two terms, repaired positionally in §4.4.
3. **Enumerated individuals.** `corpus:CompilesAbove`, `corpus:SemanticEscalation`,
   `corpus:Unadjudicated` are documented as terms at `tests/corpus-manifest.ttl:8-17` and are node
   role only, because an enum member appears only as the object of an ordinary property or inside an
   `sh:in` list. This is not an exotic case: **46 already-declared owned IRIs are enumerated
   individuals** (`GridAxiom` ×11, `CellDatatype` ×7, `Severity` ×4, `MembraneHealth` ×3,
   `RegionKind` ×3, …), all node role only. **No positional rule reaches them**, and §9 declines to
   invent one.

A further 124 owned IRIs are declared `owl:Class`/`owl:ObjectProperty`/`owl:DatatypeProperty` and
node role only across the tracked `.ttl` corpus — mostly `tab:` terms whose graphs Python builds at
runtime and never commits as Turtle. They are declared, so they raise no demand; they are quoted
here because they are the quantitative reason the negative half cannot be believed.

**This is a feature, not a gap to patch.** "No triple shows this term used as vocabulary, therefore
it is not vocabulary" is inference by absence, forbidden by CLAUDE.md §8 for derivations and by §7
generally. The rule is a **sound lower bound** on what the membrane may demand, and lower-bound-ness
is the correct epistemic shape for an open-world derivation.

### §2.7 The register's own number is contaminated (M7)

`R143`'s row states 209 undeclared owned terms across four families. It reproduces as **203**
URIRefs plus **6 distinct `sh:namespace` literals** (`vocab/shapes` +4: `dec#`, `risk#`, `iladub#`,
`tab#`; `tests` +2: `progress#`, `corpus#`), whose lexical form starts with the owned root.

The row itself warns about this contamination — *"an extractor walking `all_nodes()` without an
`isinstance(n, URIRef)` guard reports the bare namespace IRI as an undeclared term"* — **while its own
headline figure carries it.** A warning written for future counts, falsified by the count it was
written in. 18 owned-root-prefixed literals exist in total (`sh:namespace` ×12,
`vann:preferredNamespaceUri` ×8).

### §2.8 Three repo-internal namespaces, and R142's closure contradicts the artifacts (M8)

```
$ git grep -hoE "@prefix (cor|dg|prog):[[:space:]]*<[^>]+>" -- '*.ttl' | sort -u
@prefix cor:  <https://w3id.org/iladub/corpus#>
@prefix dg:   <https://w3id.org/iladub/docgov#>
@prefix prog: <https://w3id.org/iladub/progress#>
```

Three artifacts, written by three different loops, record that these are deliberately unpublished:

| file:line | statement |
|---|---|
| `tests/arc-shapes.ttl:27` | "`prog:` … is repo-internal and unpublished, exactly as `cor:` and `dg:` are: not w3id-registered, **never in vocab/ontology/**" |
| `vocab/shapes/doc-governance-shapes.ttl:8` | "The `dg:` namespace is repo-internal governance vocabulary. It is NOT part of the published … ontologies and is NOT registered at w3id." |
| `tests/corpus-shapes.ttl:2` | "`cor:` is repo-internal (like `dg:`) — not published, not w3id-registered." |

**`R142`'s stated closure — "`vocab/ontology/prog.ttl` and `vocab/ontology/docgov.ttl` declare the
terms" — contradicts all three.** It would turn test scaffolding into published, CC-BY,
w3id-registered vocabulary, which is a change of posture and not a bookkeeping repair.

And there are **three** such namespaces, not the two `R142` names. `cor:` is invisible today only
because it appears in no `.rq`; it carries 18 vocabulary-role undeclared terms and joins the problem
the moment the population reads `.ttl`.

**Ruled by the maintainer, 2026-08-29:** declare them internally (§4.5). IRIs unchanged, nothing
published, all three statements honoured.

---

## §3 What proposes, what disposes, and why they are independent

| | |
|---|---|
| **Proposes** | the authored artifact corpus — 136 tracked `.ttl` and 48 `.rq`, hand-written, using terms in roles |
| **Disposes** | the owned vocabulary — 7 published non-align ontologies plus, after §4.5, the `vocab/internal/` declarations |

Different files, edited in different acts, for different reasons. Neither is generated from the
other. A term enters the proposer's set because someone wrote a shape or a manifest that *uses* it;
it enters the disposer's set because someone wrote a vocabulary. The instrument fires exactly when
those two acts fall out of step — which is what `etkl:Contract` and the six `tab:aggFn*` terms are.

**The hazard this loop introduces, named here so a reviewer can hold it against the plan.** `R135`
could say *"no list of terms is typed anywhere in this loop"* because both sides were enumerated
from shipped artifacts. This loop **authors the disposer's new half**, from a census of the
proposer. If `vocab/internal/prog.ttl` is a transcription of the 21 terms the rule reported, the
instrument pins its own registry and the independence is theatre.

The requirement, and it is a review gate: **the internal ontologies are AUTHORED vocabularies —
typed (`owl:Class` / `owl:ObjectProperty` / `owl:DatatypeProperty`), labelled, commented, with
domains and ranges where the modelling supports them.** The census says *where the gap is*; the
author decides *what the terms mean*. A generated dump is a review failure. §7's O6 is the oracle
that makes the difference observable: an authored ontology declares terms the rule did not demand
(the enumerated individuals of §2.6 class 3), and a transcription cannot.

**A second, inner independence, inherited and preserved:** the extractor's completeness is disposed
by a different extractor (`named_terms_by_algebra` vs `named_terms_by_text`, `R135` §2.4). This loop
adds no `.rq` parsing and does not touch that pair.

---

## §4 The design

### §4.1 Two demands, and why one is not enough

| | demand | reaches | gate class |
|---|---|---|---|
| **D1** | a term used in a **vocabulary role** in any tracked artifact must be declared | 53 terms, incl. `etkl:Contract` | AXIOM / derivation, open world |
| **D2** | an owned term that is a **subject in an align module** must be declared | 6 terms, `tab:aggFn*` | AXIOM / derivation, open world |

D2 is not a special case of D1 and cannot be folded into it: an aligned term occupies no vocabulary
role by construction (§2.6 class 1, measured at 0). D2 is licensed by the *purpose of the file
family* rather than by triple position — an align module exists to relate **terms this project owns**
to external ones, so every owned subject in one is a term the project claims. That is `R117`'s own
sentence, and D2 is its oracle.

**D2 excludes subjects typed `owl:Ontology`** — MEASURED, and the measurement is why the exclusion
exists rather than being assumed:

```
align subjects, undeclared, before the exclusion  = 9
  …/hga-alignment  …/dec/hga-alignment  …/risk/hga-alignment      # ontology document IRIs
  tab:aggFnSum  aggFnMean  aggFnMin  aggFnMax  aggFnCount  aggFnProduct
after excluding subjects typed owl:Ontology       = 6
```

An ontology document IRI is not a vocabulary term and no ontology declares it. The exclusion is
positional (`a owl:Ontology`), not a name test on `/hga-alignment`.

### §4.2 The artifact dataset — PROCEDURAL

`.ttl` source text is not yet an evidence graph with file attribution. One step parses each tracked
`.ttl` into its **own named graph**, `urn:iladub:artifact:<repo-relative posix path>`, and unions
them into a dataset.

**Irreducible to AXIOM**: there is no graph to derive over until this has run — it is the step that
makes one. **Irreducible to NEURAL**: nothing is perceptual; a file either parses or raises.
**Named graphs, not a flat union**, for a stated reason: provenance-to-the-file (CLAUDE.md §6) must
survive into the failure message, and role is a *per-graph* property (§2.1) that a flat union would
destroy — a term could borrow a vocabulary role from a file it never appears in.

This module **decides nothing**, exactly as `tests/query_terms.py` decides nothing. It never imports
`iladub` (worktree hazard, `R114`/`R121`); it locates the repo from `__file__`. A parse failure
raises and names the file — never a silent skip, which would make the instrument green by not
looking.

### §4.3 The derivation — AXIOM, derivation form, OPEN WORLD

D1 and D2 are two SPARQL `CONSTRUCT` queries over the dataset, emitting the evidence the membrane
validates:

```
<urn:iladub:artifact:…>  a  etkl:VocabularyArtifact ;
                         etkl:namesTerm  <every owned IRI it USES as vocabulary> .
```

Open world and **evidence-positive throughout**: a term is emitted because a triple *shows* it in a
vocabulary role or as an align subject — never because something is absent. The `owl:Ontology`
exclusion of §4.1 is a positive test on the subject's type, evaluated inside the one graph that
holds it, and is therefore holon-scoped in CLAUDE.md §8's sense.

`etkl:namesTerm` is reused deliberately: the membrane of §4.6 already consumes it, and the demand
being made is the same demand. `etkl:VocabularyArtifact` is a new sibling of `etkl:QueryArtifact`
(§4.7).

### §4.4 Traversing SHACL path expressions

`sh:path` may carry a blank node holding a path expression. Reading only its direct object loses the
terms inside (§2.3). The derivation follows `sh:alternativePath`, `sh:inversePath`,
`sh:zeroOrMorePath`, `sh:oneOrMorePath`, `sh:zeroOrOnePath` and RDF list members, and treats every
owned IRI reached as occupying a vocabulary role.

This is **positional**, not a heuristic: a term inside a property path is being used as a property.
It is exhaustively specified by the SHACL recommendation, so the traversal is complete by
construction rather than by tuning. Measured yield over the tree: exactly `docgov:cites` and
`docgov:citesExternal`, and nothing else — which is also the check that it is not over-reaching.

### §4.5 `vocab/internal/` — the declaring source for repo-internal vocabulary

A new directory, `vocab/internal/`, holding `prog.ttl` (21 terms), `docgov.ttl` (23) and
`corpus.ttl` (18 vocabulary-role terms **plus** the enumerated verdict individuals of §2.6, which
the rule does not demand and an author must supply anyway).

`declaring_files()` widens from *"`vocab/ontology/*.ttl` that is not `*-align.ttl`"* to that **plus
`vocab/internal/*.ttl`**. The concept "declared" stops meaning "appears in the published ontology
tree" and starts meaning "declared by an owned vocabulary this repo authors" — the honest meaning,
and the one the three recorded statements of §2.8 always implied.

Each internal file states, in its header, that it is repo-internal, unpublished and not
w3id-registered, and cites the artifact whose statement it discharges. `vocab/LICENSE` is CC-BY-4.0
and covers `vocab/**`; §10 asks the plan to confirm no release or site-build step globs
`vocab/**/*.ttl` in a way that would publish these by accident.

### §4.6 The membrane — AXIOM, constraint form, CLOSED WORLD, and the exemption DELETED

`vocab/shapes/query-declaration-shapes.ttl` keeps its logic unchanged: for each artifact focus node,
every `etkl:namesTerm` object under an owned namespace must be the subject of some triple in the
declaring graph. `FILTER NOT EXISTS` stays holon-scoped — the data graph handed to it is exactly the
union of the declaring vocabularies.

**The `prog:`/`docgov:` `STRSTARTS` exemption at lines 23–28 is deleted**, and the namespace filter
becomes the single owned root. The deletion is the point: while the filter exists the instrument
cannot see those namespaces even if a term goes missing.

`inference="none"` remains load-bearing and remains pinned (`R135` F1: under `rdfs`, owlrl adds
`?term rdf:type rdfs:Resource` for every resource and the `NOT EXISTS` can never fire).

### §4.7 The owned vocabulary this loop adds

In `vocab/ontology/etkl.ttl`: `etkl:VocabularyArtifact` (an artifact whose triples use owned terms),
and `etkl:alignmentSubject` if the plan finds D2's evidence is clearer as a distinct predicate than
as a second producer of `etkl:namesTerm`. §10 seam 4 asks the plan to decide this **against the
shape**, not in prose.

### §4.8 The repairs

1. **`etkl:Contract` → `etkl:SemanticDataContract`** in `examples/federation/doc-a-contract.ttl:4`
   and `doc-b-contract.ttl:4`. §10 seam 2 requires the plan to measure whether any test or Python
   path asserts on the string `etkl:Contract` before rewriting it.
2. **The six `tab:aggFn*` terms.** Two admissible repairs, and the plan must choose *with evidence*
   rather than by preference: declare them in `vocab/ontology/tab.ttl` as the aggregation functions
   they evidently are, **or** delete the dangling alignment block. §10 seam 3 names the measurement
   that decides it — whether any FnO consumer, in this repo or in the `tab-fno-align` design, needs
   them to exist. **Do not repair by weakening D2.**

### §4.9 The `.rq` half is deliberately unchanged

The existing extractor emits every owned IRI a query names, regardless of role, and the corpus is
green under that rule today. Measured: no `.rq` names an instance IRI — the 9 `prog:` and 12
`docgov:` terms visible to it are all genuine vocabulary — so deleting the exemption does not make
the `.rq` population demand a category error. Role **is** partially recoverable from the SPARQL
algebra (143 of 173 owned IRIs get a role from BGP positions), and §11 raises that as a residue
rather than building it here: it is a second extractor's worth of work, it changes no verdict today,
and this loop already carries two demands and three new vocabularies.

---

## §5 The vacuity hazards, and how each is answered

| hazard | answer |
|---|---|
| The membrane binds zero focus nodes and passes (`R97`/`R99`) | O4 asserts the focus-node count as a **number**: one per tracked `.ttl` plus one per `.rq`, both stated exactly, never `> 0` |
| The instrument is green on its first run, so it was never shown to read the new files (`R143`'s own warning) | It is **not** green: `etkl:Contract` (D1) and six `tab:aggFn*` (D2) are live. O1 and O2 are those RED runs, quoted |
| The internal ontologies are transcribed from the census, so the instrument pins its own registry (§3) | O6: the authored vocabularies declare terms the rule never demanded; a transcription cannot |
| `inference="rdfs"` makes `NOT EXISTS` unfireable | Inherited pin, `R135` F1; the negative fixture goes green if `rdfs` is restored |
| The rule is tuned until the count looks right | Every threshold-free claim in §2 is reproduced by two independent methods (§2.3), and the one disagreement was resolved **in favour of the method that found more** (§2.3, §4.4) |

---

## §6 Gate classification (CLAUDE.md §8) — summary

| step | class | why irreducible |
|---|---|---|
| Parse tracked `.ttl` into per-file named graphs | **PROCEDURAL** | raw extraction; there is no evidence graph until it runs (§4.2) |
| D1 role derivation, incl. SHACL path traversal | **AXIOM** / derivation, open world | declarative over the evidence graph; evidence-positive; no constant (§4.3, §4.4) |
| D2 align-subject derivation | **AXIOM** / derivation, open world | same; the `owl:Ontology` exclusion is a positive type test (§4.1) |
| The declaration membrane | **AXIOM** / constraint, closed world | the contract membrane; holon-scoped `NOT EXISTS` (§4.6) |
| Authoring `vocab/internal/*.ttl` | **not code** | authored vocabulary; the census locates the gap, the author decides the meaning (§3) |

**No NEURAL step.** Nothing here is perceptual or underdetermined: a term either occupies a role in
a triple or does not. **No tuned constant appears anywhere in this loop**; one would be a defect by
§8's own words, and a reviewer finding a tolerance, a name-pattern test on a local name, or a
hand-typed term list in the implementation should fail the review.

---

## §7 The falsifying oracles — named BEFORE the design was written

**O1 — the D1 leak (RED).** With the derivation and the deleted exemption in place and **no repair**,
the instrument fails, naming `examples/federation/doc-a-contract.ttl` and `etkl:Contract`. Quote the
failing output.

**O2 — the D2 dangler (RED).** Same state: the instrument fails naming `tab-fno-align.ttl` and at
least one `tab:aggFn*`. **Falsify by deleting D2's `CONSTRUCT`: this must go green**, which is the
only proof D2 is doing work D1 cannot.

**O3 — the blank-node path.** A fixture shape whose `sh:path` is `[ sh:alternativePath ( … ) ]` over
one declared and one undeclared owned term is refused, naming the undeclared one. **Falsify by
removing the path-expression traversal: this must pass** — the term becomes invisible, which is
§2.3's measurement turned into a standing pin.

**O4 — the membrane is not idle.** The validation binds exactly one focus node per tracked `.ttl`
and per `.rq`, asserted as two numbers.

**O5 — the negative fixture.** Inherited and preserved: a synthetic artifact naming
`etkl:NoSuchTermAnywhere` is refused, and a **declared** term named in the same fixture is **not**
reported. Selectivity is the claim; assert it. The fixture lives outside every population glob, and
a test asserts that it does.

**O6 — the internal vocabularies are authored, not transcribed.** Each of `prog.ttl`, `docgov.ttl`,
`corpus.ttl` declares at least one term the role rule never demanded, and every declared term carries
a type and a label. This is the only oracle on §3's independence hazard, and it is deliberately weak
— it can detect a dump, it cannot detect a lazily-worded comment. Say so rather than overclaim.

**O7 — the exemption is gone.** `grep -c "progress#\|docgov#" vocab/shapes/query-declaration-shapes.ttl`
→ 0, and the corpus test is green with no namespace exclusion beyond the owned root.

**Falsification per CLAUDE.md plan-rule 4:** every task report carries a `## FALSIFICATION` block.
For the repair tasks specifically: restore `etkl:Contract`, show O1 red, restore, show green; restore
the dangling `tab:aggFn*` state, show O2 red, restore, show green.

---

## §8 Definition of done

1. The role derivation, the align derivation and the artifact dataset ship, with O1–O7 evidenced by
   quoted output.
2. `vocab/internal/{prog,docgov,corpus}.ttl` are authored; `declaring_files()` includes them.
3. The `prog:`/`docgov:` exemption is deleted from the shape.
4. Both live defects are repaired, each with its falsification block.
5. The whole suite is green, run by the correct runner (`R135` M3: `python3` is the wrong runner
   here — §10 seam 1).
6. The register records: **`R142`, `R143`, `R117` struck with closure evidence in place; `R144`
   CORRECTED in place (§2.5) and then struck; `R143`'s 209 corrected to 203** (§2.7). New rows from
   §11 appended with their tally snapshots.

---

## §9 What this loop does NOT do

*Read this section against every plan-supplied test before it ships — CLAUDE.md plan-rule 5.*

- **It does not decide the three-way split in general.** It settles the *positive* half — what a
  membrane may demand — and measures the negative half as undecidable by position (§2.6). A test
  asserting that some node-role-only term is "correctly classified as an instance" contradicts this
  section: the rule makes no such claim.
- **It does not demand enumerated individuals.** 46 declared ones exist and no positional rule
  reaches them. `corpus:` gains its verdict individuals by authorship, not by the membrane. → §11.
- **It does not reach `tab:product`**, undeclared, appearing only as the *object* of an
  `rdfs:seeAlso` in an align module — reached by neither D1 nor D2. Named here so its survival is a
  recorded limit rather than an oversight. → §11.
- **It does not extract role from SPARQL** (§4.9). → §11.
- **It does not publish the internal namespaces**, register them at w3id, or move any IRI.
- **It does not touch HGA.** No `holon:` term becomes a subject anywhere
  (`tests/test_source_ownership.py` enforces it).
- **It does not change `.rq` extraction**, the algebra/text cross-check, or `inference="none"`.

---

## §10 The seams the plan must MEASURE, not assume

1. **The runner.** `R135` M3 measured that `python3 -m pytest` resolves the editable install to the
   MAIN tree from a worktree. Measure the runner *before* quoting any green suite; do not inherit
   this sentence as the answer.
2. **`etkl:Contract`'s call sites.** Before rewriting the two examples, measure whether any test,
   fixture or Python path asserts on that exact string. Name the command and its output.
3. **The `tab:aggFn*` repair, decided by evidence.** Measure whether anything consumes them —
   `src/**`, `vocab/queries/**`, the `tab-fno-align` design doc — then declare or delete. State the
   measurement in the task report; a preference is not a decision.
4. **`etkl:alignmentSubject` — one predicate or two?** Decide by writing the shape both ways and
   reading which failure message names the file and the term more directly. Do not settle it in
   prose (§4.7).
5. **The `vocab/internal/` glob.** Measure whether `mkdocs.yml`, `.github/workflows/release.yml` or
   `scripts/release_gate.py` globs `vocab/**` in a way that would publish these files. If one does,
   that is a finding, not a footnote.
6. **The focus-node counts of O4.** Compute them; do not copy 136 and 48 from §2. A file can fail to
   parse, and `git ls-files` is not the population until the extractor agrees it is.
7. **Downward same-file citations.** Every `file:line` this loop writes into a comment that points
   *below itself in the same file* must be re-measured **after** the edit (CLAUDE.md plan-rule 7,
   `R139`). Prefer citing a symbol.

---

## §11 The residues this loop raises, and the four it closes

**Closes:** `R142` (on the corrected terms and the corrected declaring source, §2.8/§4.5),
`R143` (population extended to all tracked `.ttl`, headline corrected to 203),
`R117` (D2, with its live instance finally named), `R144` (corrected in place, then struck).

**Raises:**

- **Enumerated individuals are unreachable by any positional demand.** 46 declared, 3 undeclared in
  `corpus:` before this loop authors them. What would close it: a demand licensed by the enumeration
  itself — once `cor:Verdict owl:oneOf ( … )` is declared, membership becomes positive evidence — or
  a ruling that individuals are out of the membrane's scope. Measured at §2.6 class 3.
- **`tab:product`: a dangling align OBJECT.** D2 reaches subjects only. One live instance (§9).
- **`.rq` terms are demanded without role.** 30 of 173 are genuinely unknown-role
  (`BIND`/`FILTER`/property paths/CONSTRUCT templates); 143 are recoverable from BGP positions.
  Harmless today (§4.9), and it would become a defect the moment an authored query names an instance
  IRI. What would close it: a second algebra walk emitting role, disposed by the text scan.
- **`R143`'s warning did not bind its own author** (§2.7). The register has no mechanism that makes a
  row's stated caveat apply to the row's own numbers. What would close it: nothing mechanical is
  proposed — this is raised as an observation about the register, and a loop that invents a
  lint for it should first measure how often it would have fired.
