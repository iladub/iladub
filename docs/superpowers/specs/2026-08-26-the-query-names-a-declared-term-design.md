# The query names a declared term — closing `R135`

**Date:** 2026-08-26 · **Residue:** `R135` (`docs/superpowers/residues-open.md:108`) ·
**Related, deliberately NOT closed:** `R117` (`residues-open.md:93`) ·
**Base:** `main` @ `0d82736` · **Branch:** `the-query-names-a-declared-term`

**Doc impact:** increment — one new owned property and one new owned class in `etkl.ttl`,
one new shape file, and one repaired declaration in `risk.ttl`. No published assertion is
contradicted; the increment queues for the next release.

**Every measurement in this spec was taken on 2026-08-26 against `0d82736` and is recorded in
`docs/superpowers/2026-08-26-r135-premise-evidence.md`.** That file is the primary; this spec
cites it (M1–M8) and does not re-derive it. Where a number appears here it is quoted from
there, not recomputed by hand.

---

## §1 The question

`vocab/queries/membrane-health.rq` names `etkl:Intact`, `etkl:Weakened`, `etkl:Compromised`,
`etkl:CompiledDocumentHolon`, `etkl:MembraneValidation` and `etkl:membraneHealth` as bare IRIs.
rdflib resolves an IRI whether or not any ontology declares it. So **deleting the file that
declares all six changes nothing**, and `holon:05`'s oracle stays green over a query that now
names six classes that exist nowhere.

That is not a bug in `membrane-health.rq`. It is the absence of an instrument: **nothing in the
tree asks whether a term an authored query names is declared anywhere.**

The question this loop answers is exactly one sentence:

> **Does every owned-namespace term named by an authored SPARQL query resolve to a declaration
> in the owned ontology tree?**

Today the answer is *no*, once, for a real reason — and that single live violation is what makes
this loop verifiable rather than hypothetical.

---

## §2 What is measured before anything is designed

### §2.1 The ablation reproduces (M1)

In a detached worktree at `0d82736`, `rm vocab/ontology/etkl-holons.ttl`, then:

```
tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health
    file present -> 1 passed in 1.70s
    file DELETED -> 1 passed in 1.40s
```

`holon:02`'s two oracles, same ablated tree: `2 passed in 0.13s`.

**The `PYTHONPATH` seam is load-bearing and the plan must not skip it.** The editable install
resolves `iladub` to the **main tree** from inside a worktree — measured, `_repo_vocab()` returned
`/Volumes/WD Green/dev/git/iladub/vocab` until `PYTHONPATH="$PWD/src"` was set. An ablation run
without that pin measures nothing. This is `R114`/`R121`'s seam; see M1.

### §2.2 The structural half (M2)

`grep -rn "etkl-holons" src/ --include='*.py'` returns nothing. `_build_membrane`
(`compile.py:426-453`) loads `tab.ttl`, `dec.ttl`, `iladub.ttl` and no more.
`tests/etkl/test_membrane_health.py` asserts against rdflib `Namespace` constants, so **no
ontology is loaded anywhere on the path from query to assertion.**

### §2.3 The runner trap (M3) — the plan will hit this

```
python3   -m pytest tests/etkl/test_membrane_health.py -q  ->  5 failed, 12 passed, 2 errors
.venv/bin/pytest    tests/etkl/test_membrane_health.py -q  ->  19 passed in 252.96s
```

System `python3` is not the runner. `main` **is** green for this module. The module takes 4m12s
while the declared oracle test alone takes 1.7s — run the single test when iterating.

### §2.4 A naive algebra walk is INCOMPLETE (M7) — this is the spec's sharpest finding

Walking only `CompValue.items()` over the translated algebra finds **7 of `membrane-health.rq`'s
9** owned terms. It misses `iladub:PromotionDecision` and `iladub:reviews`, both nested inside
`BIND(EXISTS { … FILTER NOT EXISTS { … } })`.

**An incomplete extractor is a silently vacuous instrument** — it would report a clean tree by
failing to look. This was caught only by cross-checking against a second, independent method.
That cross-check is therefore not a convenience; §4.3 makes it part of the shipped design.

An exhaustive traversal (dict / sequence / `__dict__`, cycle-guarded) agrees with an independent
text scan on **all 46 files, 0 disagreements, 171 distinct owned IRIs** (M7).

### §2.5 The population, and the day-one failure count (M8)

Declaring set = subjects of the **non-align** `vocab/ontology/*.ttl` files.

| ns | named | declared | UNDECLARED |
|---|---|---|---|
| `tab:` | 116 | 116 | 0 |
| `dec:` | 14 | 14 | 0 |
| `etkl:` | 12 | 12 | 0 |
| `iladub:` | 6 | 6 | 0 |
| `risk:` | 2 | 1 | **1** |
| `prog:` | 9 | 0 | 9 |
| `docgov:` | 12 | 0 | 12 |
| **total** | **171** | **149** | **22** |

### §2.6 The one live violation, verified independently (M4)

`https://w3id.org/iladub/risk#order`, named by `vocab/queries/escalation-furnish.rq`.

```
as subject: []
as predicate, count: 4
dec:order as subject: [rdf:type, rdfs:label, rdfs:domain, rdfs:range, rdfs:comment]
```

`risk.ttl:62,64,66,68` use `risk:order` as a predicate on the four severities. Nothing declares
it. Its exact analogue `dec:order` is declared with type, label, domain, range and comment.
`escalation-furnish.rq` leans on it in the CONSTRUCT template (`:73-74`) and in the WHERE driving
`FILTER(?so > ?co)` (`:91,93`) — so it is load-bearing, not decorative.

No align file rescues it (checked separately against the align subjects; M8).

### §2.7 R117 has no live instance (M5)

All 19 term subjects across the four `*-hga-align.ttl` files **are** declared in the owned tree.
The only undeclared subjects are the three modules' own `owl:Ontology` metadata IRIs, which are
not dangling terms.

`tests/test_hga_alignment.py:39` parses `iladub-hga-align.ttl` **alone** — `ONTS` (`:33`) is never
loaded into that graph. `tests/test_source_ownership.py:77` is a prefix check on subject strings
and never cross-references the owned tree. Both modules: `9 passed in 0.59s`.

**So R135 is a hole with a leak; R117 is the same hole with none.** §9 rules on the consequence.

---

## §3 What proposes, what disposes, and why they are independent

| | |
|---|---|
| **Proposes** | the authored `.rq` corpus — 46 files, written by hand, naming terms |
| **Disposes** | the owned ontology tree — 13 `.ttl` files, written by hand, declaring terms |

These are **different files, edited in different acts, for different reasons**. Neither is
generated from the other, and no registry mediates them. A term enters the proposer's set by
someone writing a query; it enters the disposer's set by someone writing an ontology. The
instrument fires exactly when those two acts fall out of step — which is what happened to
`risk:order`.

**This is the property the loop must not lose.** The trap named in the `holon:05` handoff — *"an
instrument that pins its own hand-typed registry rather than the artifact is vacuous"* — is
avoided here structurally: **no list of terms is typed anywhere in this loop.** Both sides are
enumerated from the shipped artifacts. If a reviewer finds a hand-maintained term list in the
implementation, that is a review failure, not a style note.

**A second, inner independence** (§2.4): the extractor's own completeness is disposed by a
*different* extractor. The parser proposes; the text scan disposes; disagreement is a failure.
Neither is trusted alone, because the naive version of the first one was measurably wrong.

---

## §4 The design

### §4.1 Scope — five namespaces, two exclusions, one reason

**In scope:** `etkl:` `iladub:` `dec:` `risk:` `tab:` — the namespaces that have an ontology file
in `vocab/ontology/`. 150 of the 171 named IRIs (M8).

**Excluded:** `prog:` (`…/progress#`, 9 terms) and `docgov:` (`…/docgov#`, 12 terms).

**One reason, not two special cases:** neither namespace has an ontology file *at all*. They are
not dangling terms in a declared vocabulary; they are undeclared vocabularies. Authoring them is a
different act from checking declarations, and folding it in would make this two loops wearing one
name (§ Loop & context hygiene). The exclusion is **a named, dated exemption carried in the shape
file itself**, not an omission — and it raises a residue (§11) so the hole is tracked rather than
invisible.

> **SCOPE AMENDED 2026-08-26, after the maintainer's ruling and because of M8.** The ruling taken
> was *"the four owned namespaces, `prog:` explicitly excluded with a recorded reason."* M8 was
> measured afterwards and reported two facts the ruling could not have accounted for: `tab:` is a
> 116-term population that is **entirely clean**, so including it costs nothing and is the largest
> single block of coverage; and `prog:` is **not** the only namespace with no ontology file —
> `docgov:` is a second. Including `tab:` and excluding both empty namespaces under one stated
> reason is the same ruling applied to the measured facts.
>
> **CONFIRMED by the maintainer, 2026-08-26, after the amendment and its evidence were put to them.**
> Five namespaces is now a taken decision, not this spec's proposal, and re-opening it needs a
> reason rather than a preference. Recorded here and in the loop's evidence file; nowhere else.
> For the record of what was decided against: dropping `tab:` would change the list in §4.1 and
> nothing else in this spec — the day-one failure count is `risk:order` either way.

### §4.2 What "declared" means

> An IRI is **declared** iff it is the subject of at least one triple in the union of the
> **non-align** files of `vocab/ontology/*.ttl`.

Three consequences, each deliberate:

1. **Any triple counts** — `rdfs:label` alone declares. This is not laxity: `etkl:Intact` is an
   *individual* (`etkl:Intact a etkl:MembraneHealth`, `etkl-holons.ttl:78`), not a class, so a
   rule demanding `a owl:Class` would refuse the very terms R135 is about.
2. **Align files do NOT declare.** `iladub-hga-align.ttl` makes `etkl:CleanDocumentHolon` a
   subject; if that counted, a term declared *only* in an align file would pass — which is
   precisely R117's dangling case. Excluding them keeps this instrument from being fooled by the
   hole next door.
3. **Predicate-position use does not declare.** This is exactly what `risk:order` does, and it is
   why it is the violation (§2.6).

### §4.3 The extractor — PROCEDURAL, and why it is irreducible

**Interface (the plan implements the body, not this spec):**

```
extract_named_terms(query_path) -> Graph
```

The returned graph contains, for one query file:

```
<query-iri>  a            etkl:QueryArtifact ;
             etkl:namesTerm  <every owned-namespace IRI the query names> .
```

**Gate justification, required in the code as well as here (CLAUDE.md §8):** SPARQL source text is
not RDF. Turning a `.rq` file into typed RDF facts is **raw extraction — source → typed RDF
facts**, the first of the two sanctioned PROCEDURAL cases. It is irreducible to AXIOM because there
is no evidence graph to derive over until this step has run: it is the step that *makes* one.

**The extractor decides nothing.** It reports which IRIs appear. Whether that is acceptable is
§4.4's question, and is not answered here. If the plan finds itself writing a threshold, a
tolerance, or a judgement in this function, it has misplaced the boundary.

**Invariants the implementation must preserve:**

- **I1 — Completeness.** Every owned IRI reachable in the query's algebra is reported, including
  IRIs nested inside `BIND`, `EXISTS`, `FILTER NOT EXISTS`, `OPTIONAL`, `MINUS`, `VALUES`, property
  paths, and the `CONSTRUCT` template. §2.4 measured a version that failed this on the shipped
  corpus; a version that passes the corpus is not thereby correct, which is what I2 is for.
- **I2 — Cross-method agreement.** A second, independent, text-based extraction runs over the same
  file, and **disagreement in either direction is a failure**. This ships; it is not scaffolding.
  Rationale in §2.4 and §3.
- **I3 — Total.** Every one of the 46 files parses. A parse failure is a loud failure, never a
  skipped file — a skipped file is a silently narrowed population, which is the same defect class
  as I1.
- **I4 — No hand-typed term list anywhere.** §3.

### §4.4 The constraint — AXIOM, constraint form (SHACL), closed world

A new shape file, `vocab/shapes/query-declaration-shapes.ttl`, validating the union of

- the evidence graph from §4.3 (all 46 files), and
- the non-align owned ontologies (the declaring set, §4.2),

with a shape that **refuses an `etkl:QueryArtifact` naming a term that is the subject of no triple
in that union**, and whose message names **both** the query and the term.

The constraint needs "the value node is the subject of ≥ 1 triple", which plain SHACL core cannot
express — so it is an `sh:sparql` constraint with a `FILTER NOT EXISTS`, under
`advanced=True` as the repo already runs pySHACL (§ Serialization & stack conventions).

**Gate classification, ruled (CLAUDE.md §8).** This is **AXIOM, constraint form — closed world**,
and the split is load-bearing here rather than incidental:

- It is **not** a derivation. It grows no graph and states no new fact about the document domain.
  It decides what may **cross** into the authored vocabulary tree: a query naming a term.
  That is a membrane, and the membrane half of §8 is the closed-world half.
- The `FILTER NOT EXISTS` is legitimate **because the closure boundary is the vocabulary holon** —
  the union of the owned ontology files — which §8 names explicitly as the licensed pattern:
  *"query-local `NOT EXISTS`/`COUNT` closes within the one holon while the graph stays open."*
  "Is this term declared?" is a **complete** question inside that holon and an incomplete one
  outside it, which is exactly the condition the licence attaches to.
- **The forbidden alternative, named so the plan does not drift into it:** deriving
  `?term a etkl:UndeclaredTerm` with an open-world `CONSTRUCT` would be inferring a fact from an
  absence — §8's *"never use closed-world/SHACL to derive"*, wearing SPARQL's clothes. The
  refusal must stay a refusal. **Do not build an "undeclared terms" graph.**

### §4.5 The owned vocabulary this loop adds — two terms, in `etkl.ttl`

`etkl:QueryArtifact` (class) and `etkl:namesTerm` (object property, domain `etkl:QueryArtifact`).

They are added to `vocab/ontology/etkl.ttl` — not `etkl-holons.ttl`, whose subject is the doc-holon
fabric. **Both are themselves in scope of the instrument** the moment the shape file names them,
which is the correct reflexivity and not a circularity: the shape is a `.ttl`, the instrument reads
`.rq` files, and the two sets do not intersect. §10 seam 4 asks the plan to confirm that.

### §4.6 The repair — `risk:order` is declared

`vocab/ontology/risk.ttl` gains a declaration for `risk:order`, modelled on `dec:order`, which
already carries type, label, domain, range and comment (§2.6). Range is `xsd:integer`; domain is
`risk:Severity`. **The plan must MEASURE `dec:order`'s exact shape and mirror it rather than
inventing one** — §10 seam 2.

This repair is what turns the loop vertical: the instrument ships **red on the tree as it stands**,
the repair turns it green, and §7's falsification removes the repair to show it red again.

### §4.7 The manifest — re-authoring `holon:05 → holon:01`

R135's row says: *"Then, and only then, re-author `holon:05 → holon:01`."*

Once shipped, ablating `vocab/ontology/etkl-holons.ttl` makes the new instrument **fail**, because
`membrane-health.rq`'s six `etkl:` terms lose their declarations. M19 arm 1 no longer refutes the
edge.

**But it only holds if the new test is declared as an oracle of `holon:05`**, because M19 ablates
against a criterion's `prog:oracleTest` set, and `test_compiled_document_reports_membrane_health`
still passes ablated (§2.1). So the manifest edit is: add the new test as a second
`prog:oracleTest` on `prog:criterion:holon:05`, then re-author the edge with its rationale.

> **RULING, and it is contestable — flagged for review rather than buried.** Is a declaration test
> an oracle *of holon:05's statement*? holon:05 says *"a membrane-health check that computes and
> reports a compiled document's cleanliness (`etkl:membraneHealth → Intact/Weakened/Compromised`)"*.
> A check reporting a value that names an undeclared class is not reporting that statement's
> subject — so yes, defensibly. **The alternative is a new criterion of its own** on the `etkl` or
> `holon` rung, with the edge authored from that instead. I rule for the second `prog:oracleTest`
> because it is the smaller act and because R135's row asks for the edge specifically. **If the
> plan's author disagrees, say so in the plan and take the alternative** — it changes one manifest
> block and nothing else in this spec.

---

## §5 The vacuity hazards, and how each is answered

| # | Hazard | Answer |
|---|---|---|
| V1 | The extractor under-reports, so the instrument is green by not looking (**measured real**, §2.4) | I2's independent cross-method check, shipped, plus O3 |
| V2 | The instrument passes because the corpus happens to be clean | It does **not** pass today — `risk:order` (§2.6). The loop ships red and is turned green by a repair |
| V3 | The shape binds zero focus nodes (`R97`/`R99`'s class) | O4 asserts the focus-node count equals the file count, 46, and is never 0 |
| V4 | A hand-typed term list makes both sides the same source | Forbidden by I4 and §3; a reviewer checks for it |
| V5 | A parse failure silently narrows the population | I3 — loud failure, never a skip. Note `R101`: a module-level skip guard hides a whole module behind one line |
| V6 | The test passes with its subject deleted (defect 5's class) | O1 and O2, which are falsifications, not assertions |

---

## §6 Gate classification (CLAUDE.md §8) — summary

| step | class | justification |
|---|---|---|
| `.rq` text → evidence graph | **PROCEDURAL** | raw extraction, source → typed RDF facts; no evidence graph exists until it runs (§4.3) |
| independent cross-check | **PROCEDURAL** | same class, same reason; it is a second extraction, not a decision |
| "is this term declared?" | **AXIOM, constraint form (SHACL), closed world** | a membrane on what crosses into the vocabulary tree; `NOT EXISTS` is holon-scoped to the vocabulary holon (§4.4) |
| — | **NEURAL** | **none.** Nothing here is perceptual or underdetermined. If the plan reaches for BAML, it has misread the loop |

**No tuned constant appears anywhere in this loop.** There is no threshold, no tolerance and no
geometry. If one appears in the implementation it is a defect by §8's own words.

---

## §7 The falsifying oracles — named BEFORE the design was written

**O1 — the live violation (the RED that starts the loop).** On `0d82736` with only the extractor
and the shape added and **no repair**, the instrument **fails**, and its message names
`escalation-furnish.rq` and `risk:order`. Evidence: the failing output, quoted.

**O2 — the ablation, which is the whole point (the re-authoring oracle).** In a worktree with
`PYTHONPATH` pinned (§2.1), `rm vocab/ontology/etkl-holons.ttl` and the instrument **fails**,
naming `membrane-health.rq` and at least one of the six `etkl:` terms. Before this loop the same
ablation left every oracle green (M1). **This is the measurement that re-authors
`holon:05 → holon:01`, and it must be run and quoted, not asserted.**

**O3 — extractor completeness.** A fixture query nesting an owned term inside
`BIND(EXISTS { … FILTER NOT EXISTS { … } })` — the construct the naive walk measurably missed
(§2.4) — is reported by the extractor. **Falsify by substituting the naive `items()`-only walk:
this test must fail.** This is the only oracle that can pin I1.

**O4 — the shape is not idle.** The validation binds exactly 46 focus nodes, one per `.rq` file.
Asserted as a number, not as "> 0".

**O5 — the negative fixture (§ Serialization & stack conventions requires one).** A synthetic `.rq`
naming `etkl:NoSuchTermAnywhere` is refused. It lives outside `vocab/queries/` so it does not
pollute the population; §10 seam 3 asks the plan to measure where.

**Falsification, per CLAUDE.md plan-rule 4, task by task:** each task's report carries a
`## FALSIFICATION` block. For the repair task specifically, the falsification is *remove the
`risk:order` declaration and show O1 red again, restore, show green.*

---

## §8 Definition of done

1. The instrument exists, is wired into `pytest`, and is **green on the repaired tree**.
2. O1–O5 all run, with output quoted in the loop's evidence file.
3. `risk:order` is declared in `risk.ttl`, mirroring `dec:order` (§10 seam 2).
4. `tests/arc-manifest.ttl` carries the new `prog:oracleTest` on `holon:05` and the re-authored
   `holon:05 prog:dependsOn holon:01` edge, with M19 arm 1 **passing** (quoted).
5. The full suite is green under `.venv/bin/pytest` — **not `python3`** (§2.3).
6. `R135` is struck in all three register files, with closure evidence recorded in place, and the
   row moved to `residues-closed.md`. `R117` is **not** struck (§9).
7. The `prog:`/`docgov:` exemption is carried in the shape file with its date and reason, and its
   residue row exists (§11).

---

## §9 What this loop does NOT do

- **It does not close `R117`, and that is a ruling, not an omission.** The handoff's standing call
  was *"close both in the same act only if the shipped instrument demonstrably covers
  `iladub-hga-align.ttl`."* It does not: this instrument reads `.rq` files, and R117 is about the
  **subjects of subclass axioms in a `.ttl`**. §4.2's exclusion of align files from the declaring
  set is a guard against being fooled by R117 — it is not a check of R117. **R117 stays open, and
  §11 records that the generalization is one shape away.**
- **It does not author a `prog:` or `docgov:` ontology** (§4.1).
- **It does not extend to `vocab/shapes/`, `examples/`, or `tests/*.ttl`.** Those populations are
  uncensused; the widest scope was offered and not taken. `R130`'s blocker is the standing warning
  about starting an enumeration whose population has not been measured.
- **It does not build an "undeclared terms" graph** (§4.4) — that would be deriving from absence.
- **It does not touch `R130`'s forward arm**, although both build a `(query, term)` extraction. The
  questions differ: R130 asks whether a term is *reachable in compiled data*; this asks whether it
  is *declared in the vocabulary*. A shared extractor is plausible future work and is **not** in
  scope; noted so a later loop can find it.
- **It does not fix `R53`** (`groundsTo` presence-not-resolution), the same defect shape one
  namespace over, named in R117's own row.

---

## §10 The seams the plan must MEASURE, not assume

1. **Where the instrument's test module lives, and whether it is fast.** `test_membrane_health.py`
   takes 4m12s (§2.3); this one should be seconds. Measure it and say so — a slow integrity test
   gets skipped.
2. **`dec:order`'s exact declaration** before writing `risk:order`'s (§4.6). Quote it. Do not
   invent a shape from memory.
3. **Where O5's negative fixture can live** such that it is *not* picked up by the 46-file
   population. Measure the glob the extractor actually uses before choosing the path — a fixture
   inside the population turns the suite permanently red.
4. **Whether the new shape file's own terms create a cycle** (§4.5). Establish that the instrument's
   population is `.rq` only and that no `.ttl` is read as a proposer.
5. **The exact `sh:sparql` form that expresses "subject of ≥ 1 triple"** under this repo's pySHACL
   pin. `R92`/`R94` are the standing evidence that engine behaviour here is not obvious; measure
   the constraint against a two-term fixture before wiring it to 171.
6. **M19's arm-1 invocation**, before claiming §8 item 4. Read how `test_arc_ablation.py` selects a
   criterion's oracle tests, rather than assuming the second `prog:oracleTest` is picked up.

---

## §11 The residues this loop raises, and the one it closes

**Closes:** `R135`, on its own stated terms — *"a membrane (or a test) refuses a `.rq` that names a
term no loaded ontology declares, with a negative fixture that must fail"*, plus the re-authoring
of `holon:05 → holon:01`.

**Raises (numbering starts at `R140`; the tally snapshot goes in each row when written):**

- **Two owned namespaces have no ontology file at all** — `prog:` (9 terms, 7 `arc-*.rq` files and
  `tests/arc-manifest.ttl`) and `docgov:` (12 terms, the `docgov-*.rq` files). Measured M8. This is
  the §4.1 exemption's tracked cost. Note the sharper edge: `prog:` is the **arc instrument's own**
  vocabulary, so the register's measuring apparatus is itself undeclared.
- **The instrument's population is `.rq` only** — `vocab/shapes/`, `examples/` and `tests/*.ttl`
  name owned terms too and are unchecked and uncensused (§9). This is the row a later loop opens to
  generalize, and it is the row that would subsume **`R117`**.
- **`R117` remains open with no live instance** (§2.7). Worth recording explicitly, because a
  reviewer reading R117's row will find its hypothetical unrealized today and may mistake that for
  the row being stale. It is not: the oracle gap is real, only the leak is absent.
