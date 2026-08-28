# The query names a declared term — implementation plan (`R135`)

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** ship an instrument that refuses an authored SPARQL query naming an owned-namespace term
no owned ontology declares — red today on `risk:order`, green after the repair — and re-author the
`holon:05 → holon:01` edge that `M19` killed for want of it.

**Architecture:** a PROCEDURAL extractor turns each `.rq` into typed RDF facts
(`etkl:QueryArtifact` / `etkl:namesTerm`); a SHACL `sh:sparql` constraint, closed over the
vocabulary holon, refuses a named term that is the subject of no triple in the non-align owned
ontologies. Two independent extractors cross-check each other, because the naive one was measurably
incomplete.

**Tech Stack:** Python 3, `rdflib` 7.6.0, `pySHACL` 0.31.0 (`advanced=True`), pytest.

**Spec:** `docs/superpowers/specs/2026-08-26-the-query-names-a-declared-term-design.md`
**Premise evidence:** `docs/superpowers/2026-08-26-r135-premise-evidence.md` (M1–M8)
**Residue:** `R135` — index `docs/superpowers/residues.md:259`, full row in `residues-open.md`

**Base:** `main` @ `63892ae` · **Branch:** `the-query-names-a-declared-term`

**Doc impact:** increment — one new owned class and one new owned property in `etkl.ttl`, one new
shape file, one repaired declaration in `risk.ttl`. No published assertion is contradicted; the
increment queues for the next release.

---

## §0 The spec's premises still hold at `63892ae` — re-measured 2026-08-28

The spec measured `0d82736`; `main` has moved to `63892ae`. Every load-bearing number was
**re-derived from scratch today** with a throwaway prototype (kept out of the repo, in the session
scratchpad — it is measurement, not shipped code):

```
files=46 extract_time=0.77s disagreements=0 distinct_owned=171
non-align ontology files: ['dec.ttl','etkl-holons.ttl','etkl.ttl','iladub.ttl','risk.ttl','tab-datagrid.ttl','tab.ttl']
  https://w3id.org/iladub#            named=  6 declared=  6 UNDECLARED= 0  in_scope=True
  https://w3id.org/iladub/dec#        named= 14 declared= 14 UNDECLARED= 0  in_scope=True
  https://w3id.org/iladub/docgov#     named= 12 declared=  0 UNDECLARED=12  in_scope=False
  https://w3id.org/iladub/etkl#       named= 12 declared= 12 UNDECLARED= 0  in_scope=True
  https://w3id.org/iladub/progress#   named=  9 declared=  0 UNDECLARED= 9  in_scope=False
  https://w3id.org/iladub/risk#       named=  2 declared=  1 UNDECLARED= 1  in_scope=True
  https://w3id.org/iladub/tab#        named=116 declared=116 UNDECLARED= 0  in_scope=True
IN-SCOPE VIOLATIONS: [('escalation-furnish.rq', 'https://w3id.org/iladub/risk#order')]
```

M7's `171 / 0 disagreements` and M8's per-namespace table reproduce exactly, and `risk:order` is
still the single in-scope violation. **The spec is safe to build from.**

---

## Global Constraints

Every task's requirements implicitly include this section. Each constraint is stated **here once**;
tasks cite it rather than re-deriving it (CLAUDE.md plan-rule 6).

- **G1 — The runner is `./.venv/bin/pytest`. `python3 -m pytest` is NOT the runner** and produces a
  false red (spec §2.3, M3). Every command in this plan uses `./.venv/bin/pytest`.
- **G2 — Neurosymbolic gate (CLAUDE.md §8), already ruled in spec §6.** Extraction is **PROCEDURAL**
  (raw extraction, source → typed RDF facts) and must carry that justification *in the module
  docstring*, in the shape of `tests/docgov_extract.py:1-9`. The declaration decision is **AXIOM,
  constraint form (SHACL), closed world**. **Nothing here is NEURAL.** No threshold, tolerance or
  tuned constant appears anywhere; one would be a defect by §8's own words.
- **G3 — No hand-typed term list, anywhere** (spec §3, I4). Both sides are enumerated from shipped
  artifacts: the proposer from `vocab/queries/*.rq`, the disposer from the non-align
  `vocab/ontology/*.ttl`. A reviewer finding a literal list of terms fails the task. The **namespace
  scope list** in the shape file is not a term list and is explicitly permitted (§4.1, Task 2).
- **G4 — The instrument must never import `iladub`.** It locates the repo as
  `Path(__file__).resolve().parent.parent`, the way `tests/test_arc_manifest.py:58` does. Reason:
  from a worktree the editable install resolves `iladub` to the **main** tree (spec §2.1;
  R114/R121). `_run_module` now prefixes `PYTHONPATH` with the worktree's `src`
  (`tests/test_arc_ablation.py:123-134`), which closes the import route — but an instrument that
  never imports the package cannot be re-opened by it. Task 4's ablation depends on this.
- **G5 — Source ownership (CLAUDE.md § Source ownership).** No HGA IRI is ever a subject.
  `tests/test_source_ownership.py::test_no_authored_file_redefines_an_hga_term` parses
  `vocab/shapes/*.ttl` (`tests/test_source_ownership.py:62`), so the new shape file is in its
  population from the moment it lands.
- **G6 — `## FALSIFICATION` block per task** (CLAUDE.md plan-rule 4): remove or invert the thing the
  new test pins, show the test **failing**, restore, show green. **No falsification evidence ⇒ the
  task review fails.** Every verbatim test in this plan is a **proposition**: if it cannot be made
  to pass, you have found a plan defect — say so in the task report and substitute the satisfiable
  form carrying the same force. Never weaken an assertion to make a broken contract go green.
- **G7 — Evidence file.** Each task appends its quoted commands and output to
  `docs/superpowers/2026-08-28-r135-loop-evidence.md` (create it in Task 1). Spec §8 item 2 requires
  O1–O5's output to be quoted there.

---

## §0.1 Two findings the spec did not have. Both change the implementation.

**MEASURED 2026-08-28. Read these before Task 1 — each one silently voids the instrument.**

### F1 — `inference="rdfs"` makes this instrument VACUOUS

The repo's standard validation helper uses `inference="rdfs"`
(`tests/test_vocab_shapes.py:22-27`). Copying it here ships a permanently green instrument.
RDFS closure adds `?term rdf:type rdfs:Resource` for **every** resource in the graph, so
`FILTER NOT EXISTS { ?term ?p ?o }` can never fire:

```
# a two-term fixture (one declared, one not), validated twice, changing only `inference`:
--- inference=rdfs: conforms=True
--- inference=none: conforms=False
    Focus Node: <file:///q1>
    Message: file:///q1 names https://w3id.org/iladub/etkl#Undeclared, which no owned ontology declares
```

and the closure itself, printed directly:

```
triples with Undeclared as subject AFTER rdfs closure:
    (…etkl#Undeclared, rdf-syntax-ns#type, rdf-schema#Resource)
```

**The validation call passes `inference="none"`, with this measurement cited in a comment beside
it.** O5 (Task 2) is the standing pin: with `rdfs` restored, the negative fixture goes green.
This is hazard V1's class — an instrument that is green by not looking — arriving through a
different door than §2.4's.

### F2 — "exhaustive traversal" is not enough: a `dict` branch that `return`s loses 7 terms

Spec §2.4 measured that a naive `CompValue.items()` walk finds 7 of `membrane-health.rq`'s 9 owned
terms. **A traversal that handles dicts *and* `__dict__` still fails if the dict branch returns
early**, because `rdflib`'s `CompValue` **is** a `dict` subclass and carries its own `__dict__`
alongside its items. The first prototype written today did exactly that:

```
files=46 extract_time=0.93s disagreements=6 distinct_owned=164
   DISAGREE continuation-of.rq   ['tab#boundaryAgreesWith','tab#leafCellText','tab#originAgreesWith']
   DISAGREE header-row-role.rq   ['tab#sharesAlignmentOriginWith']
   DISAGREE looks-transposed.rq  ['tab#Text','tab#datatypeAbstains']
   DISAGREE membrane-health.rq   ['iladub#PromotionDecision','iladub#reviews']
   DISAGREE transpose-coherent.rq['tab#datatypeAbstains']
   DISAGREE unit-marker-column.rq['tab#Blank','tab#Quantity','tab#datatypeAbstains']
```

Walking `__dict__` **in addition to** the items — not instead of, and not after a `return` — gives
`disagreements=0 distinct_owned=171`, matching M7. **This is what O3 pins**, and it is a sharper
falsification target than the spec's: substituting *either* the `items()`-only walk *or* the
early-returning dict branch must make O3 fail.

### F3 — SHACL forbids `VALUES` inside an `sh:sparql` constraint

Measured while looking for a declarative home for the namespace scope list:

```
Validation Failure - A SPARQL Constraint must not contain a VALUES clause.
```

So the five in-scope namespaces are expressed as an ORed `STRSTARTS` filter (Task 2). This is the
spec §10 seam 5 answer: measured against a two-term fixture before being wired to 171.

---

## §0.2 File structure

| file | responsibility |
|---|---|
| `tests/query_terms.py` **(new)** | PROCEDURAL extraction: `.rq` → evidence graph; both methods; the declaring graph. No decisions. |
| `tests/test_query_terms.py` **(new)** | O3, I2, I3 and the population pin — the extractor's own oracles. |
| `vocab/shapes/query-declaration-shapes.ttl` **(new)** | AXIOM, constraint form: the membrane, plus the dated `prog:`/`docgov:` exemption. |
| `tests/test_query_declarations.py` **(new)** | O1, O4, O5 — the instrument. Carries the manifest's oracle node id. |
| `tests/query-nested-bind-exists.rq` **(new)** | O3's completeness fixture. Outside the population. |
| `tests/query-undeclared-term-leak.rq` **(new)** | O5's negative fixture. Outside the population. |
| `vocab/ontology/etkl.ttl` **(modify)** | `etkl:QueryArtifact`, `etkl:namesTerm`. |
| `vocab/ontology/risk.ttl` **(modify)** | the `risk:order` declaration (§4.6). |
| `tests/arc-manifest.ttl` **(modify)** | second `prog:oracleTest` on `holon:05`; the re-authored edge. |
| register + evidence + `docs/superpowers/2026-08-28-r135-loop-evidence.md` | Task 5. |

**Why `tests/` and not `src/`:** this is repo-integrity machinery, not runtime library code, and
`tests/docgov_extract.py` is the shipped precedent — a PROCEDURAL extractor living in `tests/`,
imported by four test modules (`tests/test_doc_governance.py:11`, `test_docgov_queries.py:8`,
`test_docgov_shapes.py:9`, `test_docgov_extract.py:10`). G4 is the second reason.

**No cycle, and this is spec §10 seam 4's answer.** The instrument's population is `.rq` only —
`test_the_population_is_every_file_in_vocab_queries` (Task 1) pins it as *identical to*
`vocab/queries/*.rq`, so no `.ttl` is ever read as a proposer. `etkl:QueryArtifact` and
`etkl:namesTerm` are therefore named by the shape file and by nothing the instrument reads: the
reflexivity is real (they are in scope the moment a query names one) and the circularity is not.
**Confirm this from the glob you implement, not from this paragraph.**

**Fixture placement — spec §10 seam 3, MEASURED.** The population glob is `vocab/queries/*.rq`.
Nothing else in the tree globs `.rq` except `tests/test_arc_queries.py:616`
(`QUERIES.glob("arc-*.rq")`), and `ls tests/*.rq` returns *no matches* today. So `tests/*.rq` is a
free, empty namespace for fixtures, and `tests/…-leak.rq` follows the existing `tests/*-leak.ttl`
naming. **Confirm the glob you actually implement matches this before choosing the paths.**

---

## Task 1: the extractor and its own oracles

**Files:**
- Create: `tests/query_terms.py`
- Create: `tests/test_query_terms.py`
- Create: `tests/query-nested-bind-exists.rq`
- Create: `docs/superpowers/2026-08-28-r135-loop-evidence.md`

**Interfaces — produced by this task, consumed by Tasks 2–4:**

```
QUERY_DIR                                   -> Path            (vocab/queries)
query_files()                               -> list[Path]      (sorted, the population)
query_iri(path)                             -> URIRef          ("urn:iladub:query:" + repo-relative posix path)
extract_named_terms(query_path)             -> Graph           (spec §4.3's interface, unchanged)
named_terms_by_text(query_path)             -> set[str]        (method B, independent)
evidence_graph()                            -> Graph           (union over query_files())
declaring_graph()                           -> Graph           (non-align vocab/ontology/*.ttl)
```

`extract_named_terms` returns, for one file, exactly the shape spec §4.3 fixes:

```
<query-iri>  a               etkl:QueryArtifact ;
             etkl:namesTerm  <every owned-namespace IRI the query names> .
```

**The query IRI is `urn:iladub:query:vocab/queries/<name>.rq`** — repo-relative, so no absolute
local path ever reaches a failure message (`tests/test_arc_landscape.py:98` already refuses absolute
repo paths in a tracked artifact, for the same reason), and in no owned namespace, so a minted
subject can never collide with a term under test.

**`etkl:namesTerm` carries EVERY owned-namespace IRI — all 171, `prog:` and `docgov:` included.**
The extractor decides nothing (spec §4.3); scope is the shape's decision (Task 2). Measured: this
yields **325 `namesTerm` triples over 46 focus nodes**.

**Invariants (spec §4.3):** I1 completeness · I2 cross-method agreement, **shipped** · I3 total, a
parse failure is loud and never a skip · I4 no hand-typed list (G3).

**SEAMS TO MEASURE — do not assume:**
1. **Read `§0.1 F2` before writing the traversal.** Then measure your own walk against method B over
   all 46 files *before* writing any test. If it does not report `disagreements=0`, the walk is
   wrong, not the corpus.
2. **Method B is not a rewrite of method A.** It must read the file as *text*: PREFIX map, PREFIX
   lines removed from the body, `#` comments stripped, prefixed names expanded, plus longhand
   `<https://w3id.org/iladub…>`. If it shares code with method A the cross-check is theatre.
3. Measure the wall-clock of `evidence_graph()`. Today's prototype: **0.77s for 46 files.** If yours
   is materially slower, say so in the task report (spec §10 seam 1 — a slow integrity test gets
   skipped).

- [ ] **Step 1: write `tests/query-nested-bind-exists.rq`**

A syntactically valid SPARQL query that nests an owned term inside
`BIND(EXISTS { … FILTER NOT EXISTS { … } })` — the construct §2.4 and F2 both measured as lost.
Use `iladub:PromotionDecision` and `iladub:reviews` nested that way, mirroring the real shape in
`vocab/queries/membrane-health.rq`. The fixture must also name at least one term **outside** any
nested construct, so a walk that finds nothing at all is distinguishable from one that finds only
the easy terms.

- [ ] **Step 2: write the failing tests**

```python
def test_a_term_nested_in_bind_exists_is_reported():
    """O3 — the only oracle that can pin I1 (spec §7).

    MEASURED 2026-08-28 (plan §0.1 F2): a walk that handles dicts and returns loses
    iladub:PromotionDecision and iladub:reviews from membrane-health.rq, and 5 tab: terms
    from 5 other files — 164 distinct instead of 171, 6 files disagreeing with method B.
    """
    g = extract_named_terms(NESTED_FIXTURE)
    named = {str(o) for o in g.objects(query_iri(NESTED_FIXTURE), ETKL.namesTerm)}
    assert "https://w3id.org/iladub#PromotionDecision" in named, named
    assert "https://w3id.org/iladub#reviews" in named, named


def test_both_extractors_agree_on_every_authored_query():
    """I2 — SHIPPED, not scaffolding (spec §2.4, §3). The parser proposes; the text scan
    disposes; disagreement in EITHER direction is a failure."""
    disagreements = {}
    for path in query_files():
        by_algebra = {str(o) for o in extract_named_terms(path).objects(None, ETKL.namesTerm)}
        by_text = named_terms_by_text(path)
        if by_algebra != by_text:
            disagreements[path.name] = sorted(by_algebra ^ by_text)
    assert not disagreements, disagreements


def test_every_authored_query_parses():
    """I3 — a parse failure is LOUD, never a skipped file. A skipped file is a silently
    narrowed population, which is I1's defect wearing a different hat (spec §5, V5)."""
    for path in query_files():
        extract_named_terms(path)          # raises, and the raise names the file


def test_the_population_is_every_file_in_vocab_queries():
    """The population is enumerated from the directory, never typed (G3). 46 today; this
    asserts the identity with the glob, not the number, so adding a query does not break it."""
    assert query_files() == sorted(QUERY_DIR.glob("*.rq"))
    assert len(query_files()) == 46, len(query_files())
```

The `== 46` is deliberate alongside the identity assertion: it is the number every other oracle in
this loop is stated over (O4), so a change to it must be a conscious edit, not a silent drift.

- [ ] **Step 3: run them and watch them fail**

```bash
./.venv/bin/pytest tests/test_query_terms.py -q
```
Expected: collection error / `ImportError` — `tests/query_terms.py` does not exist.

- [ ] **Step 4: implement `tests/query_terms.py`**

Module docstring carries the **PROCEDURAL gate justification** (G2), in the shape of
`tests/docgov_extract.py:1-9`: raw extraction, source → typed RDF facts; irreducible to AXIOM
because there is no evidence graph to derive over until this step has run — it is the step that
makes one; irreducible to NEURAL because nothing here is perceptual.

- [ ] **Step 5: run to green, and record the timing**

```bash
./.venv/bin/pytest tests/test_query_terms.py -q --durations=5
```

- [ ] **Step 6: FALSIFICATION (G6)**

Two inversions, both on the traversal, because F2 showed the naive form has two faces:
1. restrict the walk to `CompValue.items()` only (spec §2.4's form) →
   `test_a_term_nested_in_bind_exists_is_reported` **and**
   `test_both_extractors_agree_on_every_authored_query` must fail;
2. restore the `__dict__` walk but `return` out of the dict branch (F2's form) → the same two tests
   must fail, and the disagreement list must name the six files quoted in §0.1.

Restore; show green. Quote all of it in the evidence file.

- [ ] **Step 7: commit**

```bash
git add tests/query_terms.py tests/test_query_terms.py tests/query-nested-bind-exists.rq \
        docs/superpowers/2026-08-28-r135-loop-evidence.md
git commit -m "feat(r135): extract the owned terms an authored query names, cross-checked"
```

---

## Task 2: the membrane, disposed against a two-term fixture

**Files:**
- Modify: `vocab/ontology/etkl.ttl`
- Create: `vocab/shapes/query-declaration-shapes.ttl`
- Create: `tests/query-undeclared-term-leak.rq`
- Create: `tests/test_query_declarations.py`

**Consumes:** everything Task 1 produced.
**Produces:** `vocab/shapes/query-declaration-shapes.ttl` and a `_validate(data_graph)` helper
private to `tests/test_query_declarations.py`, used by Task 3.

**This task deliberately does NOT touch the 46-file corpus.** Spec §10 seam 5: measure the
constraint against a two-term fixture *before* wiring it to 171. Task 3 wires it.

**The two owned terms (spec §4.5):** `etkl:QueryArtifact` (class) and `etkl:namesTerm` (object
property, domain `etkl:QueryArtifact`), added to `vocab/ontology/etkl.ttl` — **not**
`etkl-holons.ttl`, whose subject is the doc-holon fabric. Follow the file's existing section shape:
a `####`-fenced heading then the terms, as at `vocab/ontology/etkl.ttl:141-143`.

**The shape.** `etkl:QueryArtifactShape`, `sh:targetClass etkl:QueryArtifact`, one
`sh:SPARQLConstraint` whose `sh:message` names **both** the query and the term. Its `sh:select`:

- binds `$this etkl:namesTerm ?term`;
- filters `?term` to the five in-scope namespaces with **ORed `STRSTARTS`** — `VALUES` is
  **forbidden** in an `sh:sparql` constraint (§0.1 F3, measured);
- refuses with `FILTER NOT EXISTS { ?term ?p ?o }`.

**The exemption lives here, and this is why it can (spec §8 item 7).** Because the extractor emits
all 171 IRIs and the shape chooses, the `prog:`/`docgov:` exclusion is a visible, dated, declarative
omission in this file rather than an invisible one in Python. Carry it as a comment above the
filter: *"`prog:` (…/progress#, 9 terms) and `docgov:` (…/docgov#, 12 terms) are excluded 2026-08-26
under one reason — neither namespace has an ontology file at all, so they are undeclared
vocabularies rather than dangling terms in a declared one; authoring them is a different act
(spec §4.1). Tracked as a residue, not an omission."*

**Gate note in the file (G2):** AXIOM, constraint form, closed world — the `NOT EXISTS` is
holon-scoped to the vocabulary holon, which is what licenses it. **Do not build an "undeclared
terms" graph**; deriving `?term a etkl:UndeclaredTerm` from an absence is precisely what CLAUDE.md
§8 forbids (spec §4.4).

- [ ] **Step 1: write `tests/query-undeclared-term-leak.rq`**

A valid SPARQL query naming `etkl:NoSuchTermAnywhere`. It lives in `tests/`, outside the
`vocab/queries/*.rq` population — re-measure that before choosing the path (§0.2).

- [ ] **Step 2: write the failing tests**

```python
def test_a_declared_and_an_undeclared_term_are_told_apart():
    """Spec §10 seam 5, on the smallest graph that can answer it: two terms, one declared.

    inference="none" is LOAD-BEARING and measured (plan §0.1 F1): under inference="rdfs",
    owlrl adds `?term rdf:type rdfs:Resource` for every resource, the NOT EXISTS never
    fires, and this instrument is green by not looking.
    """
    g = Graph().parse(data=TWO_TERM_FIXTURE, format="turtle")   # one declared, one not
    conforms, report = _validate(g)
    assert not conforms, report
    assert "etkl#Undeclared" in report
    assert "etkl#Declared" not in report


def test_a_query_naming_an_undeclared_term_is_refused():
    """O5 (spec §7) — the negative fixture CLAUDE.md § Serialization requires, and the
    standing pin on F1: restore inference="rdfs" and this test goes green."""
    data = extract_named_terms(LEAK_FIXTURE) + declaring_graph()
    conforms, report = _validate(data)
    assert not conforms, report
    assert "query-undeclared-term-leak.rq" in report
    assert "etkl#NoSuchTermAnywhere" in report


def test_the_leak_fixture_is_not_in_the_population():
    """V5's shape, one directory over: a fixture that joined the population would turn the
    suite permanently red and the instrument permanently meaningless."""
    assert LEAK_FIXTURE not in query_files()
    assert NESTED_FIXTURE not in query_files()
```

`_validate` wraps `pyshacl.validate(..., shacl_graph=<the new shape file>, inference="none",
advanced=True)` and returns `(conforms, report_text)`. It does **not** reuse
`tests/test_vocab_shapes.py::_validate` — that helper hard-codes `inference="rdfs"`
(`tests/test_vocab_shapes.py:22-27`), which §0.1 F1 measured as fatal here.

- [ ] **Step 3: run to red**

```bash
./.venv/bin/pytest tests/test_query_declarations.py -q
```

- [ ] **Step 4: add the two terms to `etkl.ttl`, then write the shape file**

- [ ] **Step 5: run to green**

```bash
./.venv/bin/pytest tests/test_query_declarations.py tests/test_source_ownership.py -q
```
`test_source_ownership.py` is run here, not later, because the new shape file enters its population
the moment it lands (G5).

- [ ] **Step 6: FALSIFICATION (G6)**

Three inversions:
1. `inference="none"` → `"rdfs"`: `test_a_declared_and_an_undeclared_term_are_told_apart` **and**
   O5 must fail. This is the only proof F1 is pinned rather than merely commented.
2. Delete the `FILTER NOT EXISTS` line: both must fail (the shape now refuses nothing).
3. Add `https://w3id.org/iladub/progress#` to the `STRSTARTS` disjunction and point the leak fixture
   at a `prog:` term: it must be **refused**, proving the exemption is a choice the shape makes and
   not an accident of the extractor. Revert.

Restore; show green.

- [ ] **Step 7: commit**

```bash
git add vocab/ontology/etkl.ttl vocab/shapes/query-declaration-shapes.ttl \
        tests/query-undeclared-term-leak.rq tests/test_query_declarations.py \
        docs/superpowers/2026-08-28-r135-loop-evidence.md
git commit -m "feat(r135): a SHACL membrane refusing a query term no owned ontology declares"
```

---

## Task 3: wire the corpus — O1 red, the repair, green

**Files:**
- Modify: `tests/test_query_declarations.py`
- Modify: `vocab/ontology/risk.ttl`

**Why the repair is in this task and not its own.** The instrument is red on the tree as it stands
(spec §4.6) and every commit must leave the suite green. Splitting them would land a knowingly-red
commit. The red is captured *within* the task as TDD's RED phase and quoted in the evidence file —
which is what spec §7's O1 asks for — and the falsification below re-creates it on demand.

**MEASURED, so you know what green looks like before you start** (2026-08-28, `63892ae`):

```
evidence build 0.76s; focus nodes 46; evidence triples 317; data 1770
validate 0.17s conforms=False
    Focus Node: <urn:iladub:query:vocab/queries/escalation-furnish.rq>
    Message: urn:iladub:query:vocab/queries/escalation-furnish.rq names
             https://w3id.org/iladub/risk#order, which no non-align owned ontology declares
```

Exactly one violation, ~1s end to end. (The prototype scoped inside the extractor and so emitted
317 triples; yours scopes in the shape and emits **325** — see Task 1. The violation is the same.)

**SEAM — spec §10 seam 2, MEASURED here so you mirror rather than invent.** `dec:order`, verbatim
from `vocab/ontology/dec.ttl:136-138`:

```turtle
dec:order a owl:DatatypeProperty ;
    rdfs:label "order"@en ; rdfs:domain dec:Milestone ; rdfs:range xsd:integer ;
    rdfs:comment "Position of the milestone in the process sequence." .
```

`risk:order`'s analogue takes `rdfs:domain risk:Severity` and `rdfs:range xsd:integer`. Its four
uses are `vocab/ontology/risk.ttl:62,64,66,68` — `risk:Ok 0`, `risk:Watch 1`, `risk:Breach 2`,
`risk:Critical 3`, all `a risk:Severity` — so the domain is measured, not guessed. Write your own
`rdfs:comment`; do not copy `dec:`'s sentence, which names milestones. Place it in the
`Properties — context & sensitivity` section whose header sits at `vocab/ontology/risk.ttl:71-73`, or open a
section of its own; either is consistent with the file.

- [ ] **Step 1: add the two corpus tests, and run to RED**

```python
def test_every_authored_query_names_only_declared_terms():
    """O1 (spec §7) — the instrument, over the whole authored corpus.

    THIS NODE ID IS holon:05'S SECOND prog:oracleTest (Task 4). Ablating
    vocab/ontology/etkl-holons.ttl must make it FAIL; that failure is what re-authors
    holon:05 -> holon:01, and M19 arm 1 refutes an edge only when EVERY one of the source's
    oracle tests passes (tests/test_arc_ablation.py, `ablation_refusals`, arm 1).
    """
    conforms, report = _validate(evidence_graph() + declaring_graph())
    assert conforms, report


def test_the_membrane_binds_one_focus_node_per_query_file():
    """O4 (spec §7) — asserted as a NUMBER, never as "> 0". A shape that binds zero focus
    nodes is R97/R99's vacuity, and it passes."""
    data = evidence_graph() + declaring_graph()
    focus = set(data.subjects(RDF.type, ETKL.QueryArtifact))
    assert len(focus) == len(query_files()) == 46, sorted(focus)
```

Expected at this step: `test_every_authored_query_names_only_declared_terms` **FAILS**, and its
report names `escalation-furnish.rq` and `risk#order`. **Quote that output verbatim in the evidence
file — it is O1**, and it is the sentence that makes this loop vertical rather than hypothetical.

- [ ] **Step 2: declare `risk:order` in `vocab/ontology/risk.ttl`**

- [ ] **Step 3: run to green**

```bash
./.venv/bin/pytest tests/test_query_declarations.py tests/test_risk.py \
                   tests/test_vocab_shapes.py tests/test_source_ownership.py -q --durations=5
```

- [ ] **Step 4: FALSIFICATION (G6) — spec §7's named form for this task**

Remove the `risk:order` declaration → `test_every_authored_query_names_only_declared_terms` fails
with O1's message. Restore → green. Then, separately, delete the `sh:targetClass` line from the
shape → `test_the_membrane_binds_one_focus_node_per_query_file` still passes (it counts data, not
targets) but O1 goes **green with nothing checked**; restore. Report that second result honestly:
it shows O4 alone does not pin non-idleness, and O5 (Task 2) is what does.

- [ ] **Step 5: run the full suite** (G1)

```bash
./.venv/bin/pytest -q
```
Record the summary line. Spec §2.3 measured `tests/etkl/test_membrane_health.py` alone at 4m12s, so
budget for a long run and do **not** background it.

- [ ] **Step 6: commit**

```bash
git add tests/test_query_declarations.py vocab/ontology/risk.ttl \
        docs/superpowers/2026-08-28-r135-loop-evidence.md
git commit -m "fix(r135): declare risk:order, and turn the declaration membrane green"
```

---

## Task 4: re-author `holon:05 → holon:01`

**Files:**
- Modify: `tests/arc-manifest.ttl`

**The ruling this task takes, and the one it declines.** Spec §4.7 rules for a **second
`prog:oracleTest` on `prog:criterion:holon:05`** rather than a new criterion, flags the ruling as
contestable, and says: *"if the plan's author disagrees, say so in the plan and take the
alternative."* **This plan concurs**, for the spec's reason plus one it did not have: a new
criterion would need its own `prog:oracleArtifact`, and the only candidate is the new shape file —
which would make the arc's own dependency graph assert that the membrane depends on itself. The
second oracle is the smaller and more honest act.

**MEASURED — the mechanism, so the claim in §8 item 4 is not asserted from reading:**

- `oracle_rows` (`tests/test_arc_manifest.py:91-102`) yields **every** `prog:oracleTest` object of a
  criterion, so a second one is picked up with no code change.
- Arm 1 refutes an edge only when **all** of the source's oracle tests pass in the ablated worktree
  — `if all(r == PASSED for r in results.values())` in `ablation_refusals`
  (`tests/test_arc_ablation.py`, the arm-1 branch of its scoring loop). One failing oracle therefore
  withdraws the refutation. **This is the whole mechanism of the re-authoring.**
- The declaring set is a glob over `vocab/ontology/*.ttl`, so an ablated file is simply not parsed —
  it degrades to *fewer declarations*, never to a crash. Simulated today by rebuilding the declaring
  graph without `etkl-holons.ttl`:

  ```
  ABLATED etkl-holons.ttl -> conforms = False
      … escalation-furnish.rq names risk#order …
      … membrane-health.rq names etkl#CompiledDocumentHolon …
      … membrane-health.rq names etkl#Compromised …
      … membrane-health.rq names etkl#Intact …
      … membrane-health.rq names etkl#MembraneValidation …
      … membrane-health.rq names etkl#Weakened …
      … membrane-health.rq names etkl#membraneHealth …
  ```

  — exactly the six `etkl:` terms spec §1 names. **This is a graph-level simulation, not O2.** O2 is
  the real two-sided ablation and must be **run and quoted**, not inferred from this.

**Current state, measured:** `prog:criterion:holon:05` at `tests/arc-manifest.ttl:393-402` carries
`prog:oracleArtifact "vocab/queries/membrane-health.rq"` and one `prog:oracleTest`.
`prog:criterion:holon:01` at `tests/arc-manifest.ttl:293-302` carries
`prog:oracleArtifact "vocab/ontology/etkl-holons.ttl"` and
`prog:oracleTest "tests/test_hga_alignment.py::test_holons_module_standalone"`.
A1–A4 and A6 were all satisfied at the moment M17 forced the assertion, and the manifest records why
in the comment block above the deleted edge — **do not re-derive that; cite it.**

**SEAMS TO MEASURE — spec §10 seam 6:**
1. **Do not add a `prog:oracleArtifact` to `holon:05`.** Read M16's A6 (shared artifact file) in
   `tests/arc-shapes.ttl` and confirm that the artifact sets stay disjoint before you edit anything.
2. **The control run comes first.** `_run_control` (`tests/test_arc_ablation.py`) runs the union of
   both ends' oracle ids in an **un-ablated** worktree and raises if any is not `PASSED`. Your new
   test must pass there, which means Task 3 must be committed — `_ablate` checks out `HEAD`, and an
   uncommitted artifact makes the ablation vacuous (it raises and says so).
3. **Comment placement is load-bearing.** `scripts/cockpit.py`'s reader walks a criterion block to
   the first line ending in `.`, so a comment sentence placed *inside* a block silently truncates
   it. The manifest records this failure in the note above `holon:05`. Put your comment **above**
   the block, and run `tests/test_cockpit.py`.
4. **CLAUDE.md plan-rule 7.** Any comment you write citing `file:line` *below itself in the same
   file* must be **re-measured after the edit**, not only before — adding a line shifts every target.
   Prefer citing a symbol. `R139` is the row that exists because this was got wrong while fixing it.

- [ ] **Step 1: add the second oracle test to `prog:criterion:holon:05`**

`prog:oracleTest "tests/test_query_declarations.py::test_every_authored_query_names_only_declared_terms"`

- [ ] **Step 2: run the manifest membrane**

```bash
./.venv/bin/pytest tests/test_arc_manifest.py tests/test_cockpit.py tests/test_arc_landscape.py -q
```
M17 may now *force* the edge's assertion — it did exactly that on 2026-08-25 and the manifest
records the message. If it does, that is the membrane doing Step 3 for you; record it.

- [ ] **Step 3: assert the edge, with its rationale**

`prog:criterion:holon:05 prog:dependsOn prog:criterion:holon:01 .`

The comment above it states the reading in one derivation — *membrane health is reported in the
terms `etkl-holons.ttl` declares; the new instrument refuses a query naming an undeclared term;
so removing that file now breaks `holon:05`'s oracle set* — and **cites** spec §4.7 rather than
re-arguing it (plan-rule 6). It also records that this is the edge's **third** authoring and names
the two prior refutations, so the next reader does not mistake it for a first attempt.

- [ ] **Step 4: run O2 — the real two-sided ablation, and QUOTE it**

```bash
./.venv/bin/python -c "from rdflib import Graph
from tests.test_arc_ablation import MANIFEST, ablation_refusals
g = Graph().parse(MANIFEST, format='turtle')
[print(r) for r in ablation_refusals(g)]"
```
Expected: **no `M19: arm 1 refutes holon:05 prog:dependsOn holon:01` line.** Any other refusal in
the output is a finding — report it; do not filter it out of the quote.

Then the full arc suite:

```bash
./.venv/bin/pytest tests/test_arc_ablation.py -q
```

- [ ] **Step 5: FALSIFICATION (G6)**

Remove the second `prog:oracleTest` from `holon:05`, re-run the O2 command, and show arm 1 refuting
the edge again with the 2026-08-25 message. Restore; show it silent. **That is the measurement that
re-authors the edge**, and it is the only thing that distinguishes this authoring from the two that
were killed.

- [ ] **Step 6: commit**

```bash
git add tests/arc-manifest.ttl docs/superpowers/2026-08-28-r135-loop-evidence.md
git commit -m "feat(r135): holon:05 consumes holon:01 — re-authored on a measured refusal"
```

---

## Task 5: close `R135`, raise what this loop defers, and close the loop

**Files:**
- Modify: `docs/superpowers/residues.md`, `residues-open.md`, `residues-closed.md`
- Modify: `docs/superpowers/2026-08-28-r135-loop-evidence.md`

**MEASURED — the register's state today, and the command that re-measures it:**

```
$ awk -F'|' '/^\| R[0-9]+ /{n++; s=$3; gsub(/ /,"",s); if (s ~ /^closed/) c++} END{print n, c}' \
      docs/superpowers/residues.md
131 26
```

**Run that command yourself at the moment you write the rows** and use its output for each new row's
`(N/M closed)` snapshot — the number moves as this task edits the file, and the snapshot is *never*
updated afterwards (CLAUDE.md § Deferred residues). Do not copy `26/131` from this plan.

**Numbering starts at `R142`.** `R140` and `R141` are taken (`docs/superpowers/residues.md:264-265`)
— spec §11 says "starts at R140", written before those landed. Correcting a stale number is not a
scope change.

- [ ] **Step 1: close `R135`**

Index row → status `closed`, with the closure evidence. Full row: strike the number (`~~R135~~`),
record the closure evidence **in place**, move the row from `residues-open.md` to
`residues-closed.md`. The row is never deleted. Closure evidence = O1's red, the repair, O2's
silence, and the re-authored edge.

**`R117` is NOT struck** (spec §9). If you are tempted, re-read spec §2.7: this instrument reads
`.rq` files; R117 is about the subjects of subclass axioms in a `.ttl`.

- [ ] **Step 2: raise the three rows spec §11 names**

1. **Two owned namespaces have no ontology file at all** — `prog:` (9 terms; 7 `arc-*.rq` files and
   `tests/arc-manifest.ttl`) and `docgov:` (12 terms; the `docgov-*.rq` files). Measured M8,
   reproduced at `63892ae` in §0 above. The sharp edge: `prog:` is the arc instrument's **own**
   vocabulary, so the register's measuring apparatus is itself undeclared. This is the §4.1
   exemption's tracked cost.
2. **The instrument's population is `.rq` only** — `vocab/shapes/`, `examples/` and `tests/*.ttl`
   name owned terms too, and are unchecked and **uncensused**. This is the row a later loop opens to
   generalize, and the row that would subsume **`R117`**. Note `R130`'s standing warning: do not
   start an enumeration whose population has not been measured.
3. **`R117` remains open with no live instance** (spec §2.7, M5) — recorded explicitly so a reviewer
   finding its hypothetical unrealized does not mistake that for the row being stale. The oracle gap
   is real; only the leak is absent.

- [ ] **Step 3: raise the row this PLAN found, which the spec did not have**

**A criterion's oracle can be a whole-tree integrity test, and that broadens what the ablation reads
as a dependency.** `test_every_authored_query_names_only_declared_terms` reads *every* non-align
ontology file and *every* authored query. As `holon:05`'s oracle it makes `holon:05` fail under
ablation of **any** of the seven non-align ontologies — not only `etkl-holons.ttl`. For the edge
this loop authors that is correct and is the point. For any **future** edge out of `holon:05` it is
a hazard in M19's one forbidden direction: arm 1 refutes only when every oracle passes, so a broad
oracle **withholds refutations** and admits edges that were never really tested. Measured
consequence, not speculation: the declaring set is a glob, so the oracle's artifact dependency is
the whole directory.

Record what would close it: either a per-file parameterisation whose node ids let a criterion name
the one query it depends on, or an M19 guard that refuses an oracle whose read-set is broader than
its criterion's declared artifacts.

- [ ] **Step 4: finish the evidence file**

O1–O5 each quoted with the command that produced them, plus the falsification blocks from Tasks 1–4,
plus the full-suite summary line from Task 3 Step 5.

- [ ] **Step 5: verify the whole tree, then commit**

```bash
./.venv/bin/pytest -q
git add docs/superpowers/residues.md docs/superpowers/residues-open.md \
        docs/superpowers/residues-closed.md docs/superpowers/2026-08-28-r135-loop-evidence.md
git commit -m "docs(r135): close R135 on its own terms; raise R142-R145"
```

---

## §Done — the definition this plan is measured against (spec §8)

1. The instrument exists, is wired into `pytest`, and is green on the repaired tree. *(Task 3)*
2. O1–O5 all run, output quoted in the evidence file. *(Tasks 1–4, collated in Task 5)*
3. `risk:order` is declared in `risk.ttl`, mirroring `dec:order`. *(Task 3)*
4. `tests/arc-manifest.ttl` carries the new `prog:oracleTest` on `holon:05` and the re-authored
   edge, with M19 arm 1 **passing** and quoted. *(Task 4)*
5. The full suite is green under `./.venv/bin/pytest`. *(Task 3 Step 5, re-run in Task 5)*
6. `R135` struck in all three register files, evidence in place, row moved; `R117` **not** struck.
   *(Task 5)*
7. The `prog:`/`docgov:` exemption is carried in the shape file with its date and reason, and its
   residue row exists. *(Task 2, Task 5)*

## §Not done — carried from spec §9, so no task goes looking for it

`R117` · a `prog:` or `docgov:` ontology · `vocab/shapes/`, `examples/`, `tests/*.ttl` ·
an "undeclared terms" graph · `R130`'s forward arm · `R53`.

**Any plan-supplied test above that would require one of these is a plan defect** (CLAUDE.md
plan-rule 5) — report it and substitute rather than weakening the assertion.
