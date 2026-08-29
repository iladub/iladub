# Used as vocabulary, not merely named — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the declaration membrane from `.rq` to every tracked `.ttl`, demanding a
declaration only for terms the graph *uses as vocabulary*, and close `R142`, `R143`, `R117`, `R144`.

**Architecture:** One PROCEDURAL step parses tracked `.ttl` into per-file named graphs; two AXIOM
derivations (`CONSTRUCT`, open world) emit `etkl:namesTerm` evidence — D1 from vocabulary role, D2
from align-module subjecthood; the existing SHACL membrane (AXIOM, closed world) validates it with
its `prog:`/`docgov:` exemption deleted. Three authored vocabularies under `vocab/internal/` become
part of the declaring graph.

**Tech Stack:** Python 3, rdflib, pySHACL (`advanced=True`, `inference="none"`), pytest, SPARQL 1.1.

**Doc impact: increment.** Same as the spec's (§ its header): the declaration membrane grows a
second artifact family and a second demand, `docs/wiki/concepts/` gains no page in this loop, and no
released assertion changes. Nothing here contradicts a published page, so this does not block a
release tag. *Added 2026-08-29 during execution — the plan shipped without it, and
`tests/test_doc_governance.py::test_membrane` was RED on `dg:DocImpactShape` from the commit that
introduced the plan (`58f1b27`) until this line. The spec carried its block; the plan did not, and
nothing catches that at authoring time — only the suite does, one commit later.*

**Spec:** `docs/superpowers/specs/2026-08-29-used-as-vocabulary-design.md` — **read it first and
keep it open.** This plan argues *from* the spec and does not restate it (CLAUDE.md plan-rule 6).
Every "why" question is answered there by section number.

---

## Global Constraints

Every task's requirements implicitly include this section.

- **CLAUDE.md §8 gate.** Every step is classified in spec §6. **No tuned constant, no tolerance, no
  string test on a local name, no hand-typed list of owned terms** may appear anywhere. A reviewer
  finding one fails the task. The vocabulary-role *predicate* list (spec §2.1) is RDFS/OWL/SHACL
  standard vocabulary — it is the rule itself, not a list of terms under test; say so in a comment.
- **CLAUDE.md § Source ownership.** No `holon:` IRI may become a subject.
  `tests/test_source_ownership.py` enforces it.
- **Never import `iladub` from an instrument module.** From a worktree the editable install resolves
  it to the MAIN tree (`R114`/`R121`). Locate the repo from `__file__`, as `tests/query_terms.py`
  does.
- **`isinstance(node, URIRef)` guard everywhere.** 18 owned-root-prefixed *literals* exist
  (spec §2.7). Omitting the guard silently inflates every count.
- **`inference="none"` in every pySHACL call here.** Under `rdfs`, owlrl adds
  `?term rdf:type rdfs:Resource` for every resource and `FILTER NOT EXISTS` can never fire
  (`R135` F1). Do **not** reuse `tests/test_vocab_shapes.py::_validate`, which hard-codes `"rdfs"`.
- **Falsification is mandatory, per task** (CLAUDE.md plan-rule 4). Every task report carries a
  `## FALSIFICATION` block: remove or invert the thing the new test pins, show it **failing**,
  restore, show green. **No falsification evidence ⇒ the task review fails.**
- **Plan-supplied tests are propositions.** If one cannot be made to pass, you have found a plan
  defect. Say so in the task report and substitute the satisfiable form carrying the same force —
  **never weaken an assertion to make a broken contract go green** (CLAUDE.md plan-rule 1, G6).
- **Reconciled against spec §9 before shipping** (plan-rule 5). In particular: tests here assert
  that a term **is not demanded**. None asserts that a term "is an instance" or "is correctly
  classified" — spec §9 scopes that claim *out*, and the rule makes no such claim.
- **Downward same-file citations** (plan-rule 7, `R139`): prefer citing a **symbol**; if you cite a
  line below your own comment in the same file, **re-measure after the edit**.

---

## File Structure

| file | responsibility |
|---|---|
| **Create** `tests/artifact_terms.py` | PROCEDURAL: tracked `.ttl` → per-file named graphs; runs the two derivation queries. Decides nothing (spec §4.2) |
| **Create** `vocab/queries/vocabulary-role.rq` | D1 — AXIOM derivation, open world (spec §4.3, §4.4) |
| **Create** `vocab/queries/alignment-subject.rq` | D2 — AXIOM derivation, open world (spec §4.1) |
| **Create** `vocab/internal/prog.ttl` · `docgov.ttl` · `corpus.ttl` | authored repo-internal vocabularies (spec §4.5) |
| **Create** `tests/test_artifact_declarations.py` | O1–O7 over the `.ttl` corpus |
| **Create** `tests/artifact-blank-path-fixture.ttl` | O3 fixture |
| **Create** `tests/artifact-undeclared-term-leak.ttl` | O5 negative fixture |
| **Modify** `tests/query_terms.py` → `declaring_files` | widen to include `vocab/internal/*.ttl` |
| **Modify** `vocab/shapes/query-declaration-shapes.ttl` | delete exemption; target the new class |
| **Modify** `vocab/ontology/etkl.ttl` | declare `etkl:VocabularyArtifact` |
| **Modify** `examples/federation/doc-{a,b}-contract.ttl` | repair 1 (spec §4.8) |
| **Modify** `vocab/ontology/tab.ttl` **or** `tab-fno-align.ttl` | repair 2 — **decided by measurement**, seam 3 |
| **Modify** `docs/superpowers/residues{,-open,-closed}.md` | four closures, two corrections, four new rows |

**Task order is load-bearing.** Tasks 5 → 6 → 7 must run in that order: the internal vocabularies
must exist before the exemption is deleted, or the corpus goes red for 52 uninteresting reasons
instead of the 2 real ones; and O1/O2 must be demonstrated **red** before the repairs land.

---

## Task 1: The artifact dataset (PROCEDURAL)

**Files:**
- Create: `tests/artifact_terms.py`
- Test: `tests/test_artifact_terms.py`

**Interfaces:**
- Consumes: `tests/query_terms.py` → `REPO`, `OWNED_ROOT`, `ETKL` (import; do not re-define).
- Produces:
  - `artifact_files() -> list[Path]` — every tracked `.ttl`, sorted. Enumerated from
    `git ls-files '*.ttl'`, never from a hard-coded list (G3).
  - `artifact_graph_iri(path: Path) -> URIRef` — `urn:iladub:artifact:<repo-relative posix path>`.
    Repo-relative so no absolute local path can reach a failure message.
  - `artifact_dataset() -> Dataset` — one **named graph per file**, keyed by `artifact_graph_iri`.

**Invariants:**
- The module **decides nothing**. It parses and attributes; every question of *which* terms matter
  belongs to the derivations (spec §4.2).
- A parse failure **raises, naming the file** — never a silent skip. A silent skip makes the
  instrument green by not looking.
- Named graphs, not a flat union: role is a **per-graph** property (spec §2.1) and a flat union
  would let a term borrow a vocabulary role from a file it never appears in.
- `git ls-files` is the enumeration, but the **population is what parses** — seam 6.

**MEASURE before writing `artifact_files`:** whether any tracked `.ttl` fails to parse under
rdflib, and whether `git ls-files` output needs `-z` for paths with spaces. The repo path itself
contains a space (`/Volumes/WD Green/…`). Do not assume; run it and quote the output.

- [ ] **Step 1: Write the failing tests**

```python
"""Oracles for the artifact dataset (spec §4.2). PROCEDURAL step: attribution only."""
import subprocess
import pytest
from rdflib import Literal, URIRef

from tests.artifact_terms import artifact_dataset, artifact_files, artifact_graph_iri
from tests.query_terms import OWNED_ROOT, REPO


def test_the_population_is_every_tracked_ttl():
    """Enumerated from git, never typed (G3). Asserted as a NUMBER, not '> 0' (R97/R99)."""
    out = subprocess.run(["git", "ls-files", "-z", "*.ttl"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    tracked = [p for p in out.split("\0") if p]
    assert len(artifact_files()) == len(tracked) == 136


def test_each_file_gets_its_own_named_graph():
    """Role is per-graph (spec §2.1); a flat union would destroy it."""
    ds = artifact_dataset()
    contexts = {c.identifier for c in ds.contexts() if len(c)}
    assert artifact_graph_iri(REPO / "vocab" / "ontology" / "etkl.ttl") in contexts
    assert len(contexts) == len(artifact_files())


def test_the_graph_iri_is_repo_relative():
    """No absolute local path may reach a failure message."""
    iri = artifact_graph_iri(REPO / "vocab" / "ontology" / "etkl.ttl")
    assert iri == URIRef("urn:iladub:artifact:vocab/ontology/etkl.ttl")
    assert str(REPO) not in str(iri)


def test_a_parse_failure_names_the_file(tmp_path, monkeypatch):
    """Never a silent skip: a skipped file is an instrument that is green by not looking."""
    bad = tmp_path / "broken.ttl"
    bad.write_text("@prefix ex: <http://example.org/> .\nex:a ex:b", encoding="utf-8")
    monkeypatch.setattr("tests.artifact_terms.artifact_files", lambda: [bad])
    with pytest.raises(ValueError, match="broken.ttl"):
        artifact_dataset()


def test_owned_prefixed_literals_are_not_mistaken_for_terms():
    """Spec §2.7: 18 owned-root-prefixed LITERALS exist (sh:namespace, vann:*).

    This is the standing pin on the isinstance(node, URIRef) guard. Without it the
    register's own headline count was inflated by 6.
    """
    ds = artifact_dataset()
    literals = {o for _, _, o in ds.quads((None, None, None, None))
                if isinstance(o, Literal) and str(o).startswith(OWNED_ROOT)}
    assert len(literals) >= 12, "expected the sh:namespace literals to be present as LITERALS"
    assert not any(isinstance(x, URIRef) for x in literals)
```

- [ ] **Step 2: Run them and watch every one fail**

Run: `python -m pytest tests/test_artifact_terms.py -v`
Expected: all FAIL — `ModuleNotFoundError: tests.artifact_terms`.

**Seam 1 — MEASURE THE RUNNER FIRST.** `R135` M3 measured that `python3 -m pytest` can resolve the
editable install to the MAIN tree from a worktree. Determine the correct runner for *this*
workspace and quote the command and its output in the task report. Do not inherit `python3` or
`python` from this plan as the answer — this line is the instruction to measure, not the result.

- [ ] **Step 3: Implement `tests/artifact_terms.py`**

Write the module satisfying the interfaces and invariants above. Module docstring must state the
gate classification (PROCEDURAL) and *why it is irreducible* to AXIOM and NEURAL — spec §4.2 and §6
give the argument; state it in the code, do not merely cite it (CLAUDE.md §8 requires the
justification in the code).

- [ ] **Step 4: Run the tests and confirm they pass**

- [ ] **Step 5: FALSIFICATION**

Invert the `isinstance(..., URIRef)` guard so literals are collected as terms; show
`test_owned_prefixed_literals_are_not_mistaken_for_terms` **failing**; restore; show green.
Then delete the `raise` in the parse path and show `test_a_parse_failure_names_the_file` failing.

- [ ] **Step 6: Commit**

```bash
git add tests/artifact_terms.py tests/test_artifact_terms.py
git commit -m "feat(r143): the artifact dataset — one named graph per tracked .ttl"
```

---

## Task 2: D1 — the vocabulary-role derivation (AXIOM, open world)

**Files:**
- Create: `vocab/queries/vocabulary-role.rq`
- Modify: `tests/artifact_terms.py` (add the runner), `vocab/ontology/etkl.ttl`
- Test: `tests/test_artifact_terms.py` (append)

**Interfaces:**
- Produces: `derive_vocabulary_terms() -> Graph` — the union of D1's `CONSTRUCT` over the dataset.
  Emits, per spec §4.3:
  `<urn:iladub:artifact:…> a etkl:VocabularyArtifact ; etkl:namesTerm <owned IRI used as vocabulary> .`
- Produces (`vocab/ontology/etkl.ttl`): `etkl:VocabularyArtifact`, an `owl:Class`, sibling of
  `etkl:QueryArtifact`, with `rdfs:label` and `rdfs:comment`.

**Invariants:**
- **Open world, evidence-positive.** A term is emitted because a triple *shows* it in a vocabulary
  role. Nothing is emitted from an absence. Any `NOT EXISTS` here would be a gate violation — the
  closed-world question belongs to the membrane (spec §4.3, §4.6).
- The role rule is spec §2.1 verbatim: predicate position, or object of one of the 16 named
  RDFS/OWL/SHACL predicates. **`VALUES` is permitted here** — `R135` F3 measured that SHACL forbids
  `VALUES` *inside `sh:sparql`*; this is a standalone `CONSTRUCT` and that restriction does not apply.
  Confirm it runs before relying on it.
- `etkl:VocabularyArtifact` must be declared in **this** task, before any `.rq` names it — otherwise
  the existing `.rq` corpus test (`test_every_authored_query_names_only_declared_terms`) goes red on
  the query this task adds.

- [ ] **Step 1: Write the failing tests**

```python
"""D1 — the role derivation (spec §2.1, §4.3). Numbers are spec §2.2, re-measured there."""
from rdflib import RDF, URIRef

from tests.artifact_terms import derive_vocabulary_terms
from tests.query_terms import ETKL, declaring_graph

PROG = "https://w3id.org/iladub/progress#"


def _demanded():
    g = derive_vocabulary_terms()
    return {str(o) for o in g.objects(None, ETKL.namesTerm)}


def _undeclared_demands():
    declared = {str(s) for s in declaring_graph().subjects()}
    return {t for t in _demanded() if t not in declared}


def test_the_rule_demands_53_undeclared_terms():
    """Spec §2.2, asserted as a NUMBER. This count moves only when the tree does."""
    assert len(_undeclared_demands()) == 53


def test_the_prog_vocabulary_is_21_terms():
    """Spec §2.3 (M3): the role rule reproduces R142's corrected census term-for-term,
    by a method that shares nothing with the lexical scan that produced it."""
    assert len({t for t in _undeclared_demands() if t.startswith(PROG)}) == 21


def test_the_live_etkl_leak_is_demanded():
    """Spec §2.4 (M4) — O1's subject. The ontology declares etkl:SemanticDataContract."""
    assert "https://w3id.org/iladub/etkl#Contract" in _undeclared_demands()


def test_an_arc_instance_iri_is_not_demanded():
    """Spec §2.2. NOTE (plan-rule 5, spec §9): this asserts the term is NOT DEMANDED.
    It does NOT assert the term 'is an instance' — spec §9 scopes that claim out, and
    the rule makes no such claim. Do not strengthen this assertion."""
    assert PROG + "criterion:holon:05" not in _demanded()


def test_a_shacl_shape_node_is_not_demanded():
    """Spec §2.2: no owned IRI is used as a SHACL metaclass, and sh:node with an owned
    object has zero occurrences — so shape nodes fall out on their own, unfiltered."""
    assert "https://w3id.org/iladub/docgov#DocumentShape" not in _demanded()


def test_every_artifact_is_typed_for_the_membrane():
    """O4's precondition: the membrane targets etkl:VocabularyArtifact by class."""
    g = derive_vocabulary_terms()
    assert set(g.subjects(RDF.type, ETKL.VocabularyArtifact))
    assert all(isinstance(s, URIRef) for s in g.subjects(RDF.type, ETKL.VocabularyArtifact))
```

- [ ] **Step 2: Run them and confirm they fail** (`derive_vocabulary_terms` undefined).

- [ ] **Step 3: Declare `etkl:VocabularyArtifact` in `vocab/ontology/etkl.ttl`**

Follow the shape of the existing `etkl:QueryArtifact` declaration in that file.

- [ ] **Step 4: Write `vocab/queries/vocabulary-role.rq` and the runner**

The query header comment must carry the gate classification (AXIOM / derivation / open world) and
the sentence that licenses it: *the rule is positional and evidence-positive; nothing is derived
from an absence.* Note in the comment that the 16-predicate list is standard vocabulary — the rule
itself — and not a list of owned terms under test.

- [ ] **Step 5: Run the tests and confirm they pass**

If `test_the_rule_demands_53_undeclared_terms` returns anything other than 53, **stop and report the
delta with the differing terms listed** — spec §2.2 was measured twice; a third disagreement is a
finding about the tree or about your query, and either way it is evidence, not a number to adjust.

- [ ] **Step 6: FALSIFICATION**

Delete clause **(b)** (object-of-schema-predicate) from the query; show
`test_the_prog_vocabulary_is_21_terms` **failing** (`prog:Criterion`, `prog:Manifest`, `prog:Rung`
are reached only by `rdf:type`/`sh:targetClass`); restore; show green.

- [ ] **Step 7: Commit**

```bash
git add vocab/queries/vocabulary-role.rq tests/artifact_terms.py \
        tests/test_artifact_terms.py vocab/ontology/etkl.ttl
git commit -m "feat(r143): D1 — a term is demanded when the graph uses it as vocabulary"
```

---

## Task 3: SHACL path-expression traversal

**Files:**
- Modify: `vocab/queries/vocabulary-role.rq`
- Create: `tests/artifact-blank-path-fixture.ttl`
- Test: `tests/test_artifact_terms.py` (append)

**Interfaces:** unchanged — this widens what D1 reaches, and changes no signature.

**Invariants:**
- Traverse `sh:alternativePath`, `sh:inversePath`, `sh:zeroOrMorePath`, `sh:oneOrMorePath`,
  `sh:zeroOrOnePath` and RDF list members (`rdf:first`/`rdf:rest`) reachable from `sh:path`.
- **Positional, not heuristic**: a term inside a property path *is* being used as a property. The
  construct set is exhaustively fixed by the SHACL recommendation, so completeness is by
  construction, not by tuning (spec §4.4).
- Measured yield over the tree is **exactly** `docgov:cites` and `docgov:citesExternal` — which is
  also the check that the traversal does not over-reach.

- [ ] **Step 1: Write the fixture**

`tests/artifact-blank-path-fixture.ttl` — a shape whose `sh:path` is
`[ sh:alternativePath ( <a declared owned term> <an undeclared owned term> ) ]`. It must contain
**both** a declared and an undeclared term: without the declared one the test passes against a
derivation that demands everything it sees (the selectivity trap `R135` Task 2 measured).

**The fixture must live outside every population glob.** Seam: `artifact_files()` enumerates
`git ls-files '*.ttl'`, and `tests/` is tracked — so a fixture in `tests/` **would** join the
population and turn the corpus permanently red. **MEASURE this before choosing the path**, and add
the guard test below. This is the same hazard `tests/test_query_declarations.py::
test_the_leak_fixture_is_not_in_the_population` was written for, one directory over.

- [ ] **Step 2: Write the failing tests**

```python
def test_a_term_inside_a_blank_node_path_is_reached():
    """O3 (spec §7). The sole blank-node sh:path in the tree hides docgov:citesExternal
    behind an RDF list (spec §2.3); its sibling docgov:cites survives only by accident,
    because a .rq also names it."""
    assert "https://w3id.org/iladub/docgov#citesExternal" in _demanded()


def test_the_path_traversal_adds_exactly_two_terms():
    """Spec §2.3, MEASURED by running the traversal: 53 without it, 55 with it, and the
    two added are docgov:cites and docgov:citesExternal. Over the .ttl corpus ALONE both
    are hidden — docgov:cites's rescuing occurrence is in the .rq population, which this
    derivation does not read. Asserting the delta as well as the total is what makes this
    a check that the traversal does not OVER-reach."""
    assert len(_undeclared_demands()) == 55
    assert {"https://w3id.org/iladub/docgov#cites",
            "https://w3id.org/iladub/docgov#citesExternal"} <= _undeclared_demands()


def test_the_fixtures_are_not_in_the_population():
    """A fixture that joined the population would turn the suite permanently red and the
    instrument permanently meaningless."""
    from tests.artifact_terms import artifact_files
    names = {p.name for p in artifact_files()}
    assert "artifact-blank-path-fixture.ttl" not in names
    assert "artifact-undeclared-term-leak.ttl" not in names
```

**The 53 → 55 step is measured, not predicted** (spec §2.3, command and output quoted there). Task 2's
`test_the_rule_demands_53_undeclared_terms` asserts 53 and **must keep asserting 53 until this task
lands**; this task changes it to 55 in the same commit that adds the traversal. If you find yourself
adjusting either constant to make a suite go green without having re-run the census, stop — that is
the tuned-constant failure CLAUDE.md §8 calls prima facie evidence of a misplaced decision.

- [ ] **Step 3: Run, confirm failure, implement the traversal, run again**

- [ ] **Step 4: FALSIFICATION**

Remove the path-expression traversal. `test_a_term_inside_a_blank_node_path_is_reached` must
**FAIL** (the validation would conform; the term becomes invisible — spec §7 O3 states it in this
direction deliberately). Restore; show green.

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/vocabulary-role.rq tests/artifact-blank-path-fixture.ttl \
        tests/test_artifact_terms.py
git commit -m "feat(r143): follow SHACL path expressions — the one blank node hid a real term"
```

---

## Task 4: D2 — align-module subjects (AXIOM, open world)

**Files:**
- Create: `vocab/queries/alignment-subject.rq`
- Modify: `tests/artifact_terms.py`
- Test: `tests/test_artifact_terms.py` (append)

**Interfaces:**
- Produces: `derive_alignment_subjects() -> Graph` — same predicate, same artifact class as D1
  (spec §4.3: the demand being made is the same demand).

**Invariants:**
- Scope: graphs whose file name ends `-align.ttl`. Every **owned subject** in one is a term this
  project claims, because that is what an align module is *for* (spec §4.1). This is licensed by
  the file family's purpose, not by triple position — which is why it cannot be folded into D1.
- **Excludes subjects typed `owl:Ontology`** — an ontology document IRI is not a vocabulary term.
  Positional (`a owl:Ontology`), never a name test on `/hga-alignment`. Measured: 9 undeclared align
  subjects before the exclusion, 6 after (spec §4.1).
- D2 reaches **subjects only**. `tab:product` is undeclared and appears only as an *object*; it is
  out of reach by design and is raised as a residue (spec §9, §11). Do not widen D2 to catch it.

- [ ] **Step 1: Write the failing tests**

```python
"""D2 — align subjects (spec §4.1). R117's own sentence, turned into an oracle."""
from tests.artifact_terms import derive_alignment_subjects

TAB = "https://w3id.org/iladub/tab#"


def _align_demands():
    declared = {str(s) for s in declaring_graph().subjects()}
    g = derive_alignment_subjects()
    return {str(o) for o in g.objects(None, ETKL.namesTerm)} - declared


def test_the_six_dangling_aggregation_terms_are_demanded():
    """O2's subject (spec §2.5, M5) — R117's live instance, dangling since
    tab-fno-align.ttl was written."""
    assert _align_demands() == {
        TAB + n for n in
        ("aggFnSum", "aggFnMean", "aggFnMin", "aggFnMax", "aggFnCount", "aggFnProduct")
    }


def test_ontology_document_iris_are_not_demanded():
    """Spec §4.1: 9 before the owl:Ontology exclusion, 6 after. An ontology document IRI
    is not a vocabulary term and no ontology declares it."""
    assert "https://w3id.org/iladub/hga-alignment" not in _align_demands()
    assert "https://w3id.org/iladub/dec/hga-alignment" not in _align_demands()


def test_d2_reaches_something_d1_cannot():
    """The whole justification for a second demand (spec §4.1): the align family has
    ZERO vocabulary-role terms, so D1 is structurally blind here."""
    assert _align_demands() - _undeclared_demands() != set()
```

- [ ] **Step 2: Run, confirm failure, write the query, run again**

- [ ] **Step 3: FALSIFICATION**

Delete the `owl:Ontology` exclusion; show `test_ontology_document_iris_are_not_demanded` **failing**
with 9 demands instead of 6; restore. Then delete D2's `CONSTRUCT` entirely and show
`test_the_six_dangling_aggregation_terms_are_demanded` failing — this is the proof D2 does work D1
cannot.

- [ ] **Step 4: Commit**

```bash
git add vocab/queries/alignment-subject.rq tests/artifact_terms.py tests/test_artifact_terms.py
git commit -m "feat(r117): D2 — an owned subject in an align module is a term we claim"
```

---

## Task 5: The internal vocabularies

**Files:**
- Create: `vocab/internal/prog.ttl`, `vocab/internal/docgov.ttl`, `vocab/internal/corpus.ttl`
- Modify: `tests/query_terms.py` → `declaring_files`
- Test: `tests/test_artifact_declarations.py` (create)

**Interfaces:**
- `declaring_files()` widens to `vocab/ontology/*.ttl` (non-align) **+** `vocab/internal/*.ttl`.
  Its docstring must state the new meaning of "declared" (spec §4.5) and keep the existing sentence
  about why align modules are excluded.

**Invariants — read spec §3 before writing a single triple.**
- **These are AUTHORED vocabularies, not a transcription of the census.** Every term carries a type
  (`owl:Class` / `owl:ObjectProperty` / `owl:DatatypeProperty`), an `rdfs:label` and an
  `rdfs:comment`, with `rdfs:domain`/`rdfs:range` where the modelling supports them. **A generated
  dump is a review failure** — it turns the instrument into a pin on its own registry and destroys
  the propose/dispose independence the loop rests on.
- Each file's header states that it is **repo-internal, unpublished and not w3id-registered**, and
  cites the artifact whose statement it discharges (`tests/arc-shapes.ttl`,
  `vocab/shapes/doc-governance-shapes.ttl`, `tests/corpus-shapes.ttl` — spec §2.8).
- `corpus.ttl` must also declare the **enumerated verdict individuals** (`cor:CompilesAbove`,
  `cor:SemanticEscalation`, `cor:Unadjudicated`, documented at `tests/corpus-manifest.ttl:8-17`).
  The rule does **not** demand them (spec §2.6 class 3) — they are the authored surplus O6 checks
  for, and they are why this task cannot be automated.

**Seam 5 — MEASURE:** whether `mkdocs.yml`, `.github/workflows/release.yml` or
`scripts/release_gate.py` globs `vocab/**` in a way that would publish these files. If one does,
**that is a finding**, not a footnote — report it and stop before committing.

- [ ] **Step 1: Write the failing test (O6)**

```python
"""O6 (spec §7) — the internal vocabularies are authored, not transcribed.

DELIBERATELY WEAK, and spec §7 says so: this detects a dump; it cannot detect a lazily
worded comment. It is the only oracle on spec §3's independence hazard. Do not overclaim it.
"""
from rdflib import Graph, OWL, RDF, RDFS

from tests.query_terms import OWNED_ROOT, REPO

INTERNAL = sorted((REPO / "vocab" / "internal").glob("*.ttl"))
TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.NamedIndividual}


def test_all_three_internal_vocabularies_exist():
    assert {p.name for p in INTERNAL} == {"prog.ttl", "docgov.ttl", "corpus.ttl"}


def test_every_internal_term_is_typed_and_labelled():
    """An authored vocabulary says what its terms ARE and what they MEAN."""
    for path in INTERNAL:
        g = Graph().parse(path, format="turtle")
        subjects = {s for s in set(g.subjects()) if str(s).startswith(OWNED_ROOT)}
        assert subjects, path.name
        for s in subjects:
            assert set(g.objects(s, RDF.type)) & TYPES, f"{path.name}: {s} has no owl: type"
            assert set(g.objects(s, RDFS.label)), f"{path.name}: {s} has no rdfs:label"
            assert set(g.objects(s, RDFS.comment)), f"{path.name}: {s} has no rdfs:comment"


def test_corpus_declares_terms_the_rule_never_demanded():
    """The authored surplus (spec §3, §2.6 class 3). A transcription of the census
    cannot pass this: enumerated individuals are node-role-only and are never demanded."""
    from tests.artifact_terms import derive_vocabulary_terms
    from tests.query_terms import ETKL
    demanded = {str(o) for o in derive_vocabulary_terms().objects(None, ETKL.namesTerm)}
    g = Graph().parse(REPO / "vocab" / "internal" / "corpus.ttl", format="turtle")
    declared = {str(s) for s in set(g.subjects()) if str(s).startswith(OWNED_ROOT)}
    assert declared - demanded, "corpus.ttl declares nothing beyond what the rule demanded"


def test_the_declaring_graph_now_includes_the_internal_vocabularies():
    from tests.query_terms import declaring_files
    assert {p.name for p in declaring_files()} >= {"prog.ttl", "docgov.ttl", "corpus.ttl"}
```

- [ ] **Step 2: Run, confirm failure**

- [ ] **Step 3: Author the three vocabularies** — 21 `prog:` terms, 23 `docgov:`, 18 `corpus:` plus
      its verdict individuals. Term lists are in spec §2.2/§2.3 and in `R142`/`R143`'s rows; the
      **meanings** are yours to write from the artifacts that use them.

- [ ] **Step 4: Widen `declaring_files()`; run the tests; run the existing `.rq` suite too**

Run `tests/test_query_declarations.py` as well — widening the declaring graph must not break it.

- [ ] **Step 5: FALSIFICATION**

Delete one `rdfs:comment` from `prog.ttl`; show `test_every_internal_term_is_typed_and_labelled`
failing and naming that term; restore. Then delete the verdict individuals from `corpus.ttl` and
show `test_corpus_declares_terms_the_rule_never_demanded` failing.

- [ ] **Step 6: Commit**

```bash
git add vocab/internal/ tests/query_terms.py tests/test_artifact_declarations.py
git commit -m "feat(r142): declare the three repo-internal vocabularies, unpublished"
```

---

## Task 6: The membrane — delete the exemption, and go RED

**Files:**
- Modify: `vocab/shapes/query-declaration-shapes.ttl`
- Create: `tests/artifact-undeclared-term-leak.ttl`
- Test: `tests/test_artifact_declarations.py` (append)

**Invariants:**
- The shape's **logic is unchanged**. What changes: the `prog:`/`docgov:` `STRSTARTS` exemption at
  lines 23–28 is **deleted**, the namespace filter becomes the single owned root, and the shape
  targets `etkl:VocabularyArtifact` as well as `etkl:QueryArtifact` (spec §4.6).
- `FILTER NOT EXISTS` stays **holon-scoped**: the data graph handed to the validator is exactly the
  declaring vocabularies. Do not build an "undeclared terms" graph from this — deriving from an
  absence is what CLAUDE.md §8 forbids.
- The exemption comment block goes with the filter. Leaving a comment describing a deleted filter is
  a stale citation.

**This task is expected to END RED and that is the point.** O1 and O2 are those red runs.

- [ ] **Step 1: Write the tests, including the two that must be red before the repairs**

```python
def test_the_membrane_binds_one_focus_node_per_artifact():
    """O4 (spec §7) — asserted as NUMBERS, never '> 0'. A shape binding zero focus nodes
    is R97/R99's vacuity, and it passes."""
    data = evidence() + declaring_graph()
    vocab_nodes = set(data.subjects(RDF.type, ETKL.VocabularyArtifact))
    query_nodes = set(data.subjects(RDF.type, ETKL.QueryArtifact))
    assert len(vocab_nodes) == len(artifact_files())
    assert len(query_nodes) == len(query_files()) == 46


def test_a_ttl_naming_an_undeclared_term_is_refused():
    """O5 (spec §7) — the negative fixture § Serialization requires.

    The fixture also names a DECLARED term. Without that assertion this test passes
    against a membrane that refuses EVERY term; selectivity is the claim, so assert it."""
    conforms, report = _validate(from_fixture(LEAK_FIXTURE) + declaring_graph())
    assert not conforms, report
    assert "etkl#NoSuchTermAnywhere" in report
    assert "etkl#SemanticDataContract" not in report


def test_the_exemption_is_gone():
    """O7 (spec §7). While the filter exists the instrument cannot see those namespaces
    even if a term goes missing — the deletion IS the oracle."""
    text = SHAPES.read_text(encoding="utf-8")
    assert "progress#" not in text
    assert "docgov#" not in text


def test_every_artifact_names_only_declared_terms():
    """O1 + O2 (spec §7). EXPECTED TO FAIL until Task 7 repairs both live defects.
    Mark it xfail(strict=True) in THIS task and remove the marker in Task 7 — a test
    that is simply absent here proves nothing about the red."""
    conforms, report = _validate(evidence() + declaring_graph())
    assert conforms, report
```

- [ ] **Step 2: Run; capture and QUOTE the two red reports**

The task report must quote output naming `examples/federation/doc-a-contract.ttl` +
`etkl:Contract` (**O1**) and `vocab/ontology/tab-fno-align.ttl` + a `tab:aggFn*` term (**O2**).
**These quotes are the loop's evidence that the instrument is not green by not looking.** A task
report without them fails review.

- [ ] **Step 3: Confirm the reds are ONLY those two**

If any third term is refused, **stop and report it** — spec §2.2 predicts exactly 53 demands, all
covered by Task 5's declarations except these two families. A third red is either a new finding or a
defect in Tasks 1–5.

- [ ] **Step 4: FALSIFICATION**

Delete `FILTER NOT EXISTS { ?term ?p ?o }` from the shape and show
`test_a_ttl_naming_an_undeclared_term_is_refused` **failing its selectivity assertion** — with the
filter gone the membrane refuses everything, including the declared term. Restore. Then restore the
old exemption block and show `test_the_exemption_is_gone` failing.

- [ ] **Step 5: Commit** (red, deliberately — the message must say so)

```bash
git add vocab/shapes/query-declaration-shapes.ttl tests/artifact-undeclared-term-leak.ttl \
        tests/test_artifact_declarations.py
git commit -m "feat(r142): delete the namespace exemption — the membrane now reads .ttl

Ends RED on two live defects (O1, O2), repaired in the next commit. The
deletion is the oracle: while the filter existed the instrument could not
see those namespaces even if a term went missing."
```

---

## Task 7: The two repairs

**Files:**
- Modify: `examples/federation/doc-a-contract.ttl:4`, `examples/federation/doc-b-contract.ttl:4`
- Modify: `vocab/ontology/tab.ttl` **or** `vocab/ontology/tab-fno-align.ttl` — **seam 3 decides**
- Modify: `tests/test_artifact_declarations.py` (remove the `xfail` marker)

**Seam 2 — MEASURE BEFORE REWRITING.** Whether any test, fixture or Python path asserts on the exact
string `etkl:Contract`. Name the command and quote its output. A rename that breaks an assertion
elsewhere is a defect this seam exists to catch.

**Seam 3 — MEASURE, THEN DECIDE.** Whether anything consumes the six `tab:aggFn*` terms: search
`src/**`, `vocab/queries/**`, and the `tab-fno-align` design doc. Then either declare them in
`vocab/ontology/tab.ttl` as the aggregation functions they evidently are, **or** delete the dangling
alignment block. **State the measurement in the task report — a preference is not a decision.**
**Do not repair by weakening D2.**

- [ ] **Step 1: Run seams 2 and 3; record both measurements in the task report**
- [ ] **Step 2: Apply repair 1** — `etkl:Contract` → `etkl:SemanticDataContract`, both files
- [ ] **Step 3: Apply repair 2** — per seam 3's measured decision
- [ ] **Step 4: Remove the `xfail(strict=True)` marker; run the full suite green**
- [ ] **Step 5: FALSIFICATION** — restore `etkl:Contract`, show O1 red, restore, show green; then
      restore the dangling `tab:aggFn*` state, show O2 red, restore, show green
- [ ] **Step 6: Commit**

```bash
git commit -am "fix(r117,r143): repair both live defects the membrane found"
```

---

## Task 8: The register

**Files:** `docs/superpowers/residues.md`, `residues-open.md`, `residues-closed.md`

**Invariants — the register's real conventions, which differ from what a plan usually assumes:**
- **The index never strikes an id; the detail row does.** Verify with
  `grep -c "^| ~~R" docs/superpowers/residues.md` → expect `0`. This is the file's practice, not a
  written rule.
- A closing change **strikes the row's number, records closure evidence in place, and moves the full
  row** open → closed. **It does not delete the row** — a deleted row erases the proof of repair and
  shrinks the denominator.
- New rows record the tally **at the moment they were raised**, as a snapshot that is never updated.
  Compute it; do not copy `27/135` from the spec header.

- [ ] **Step 1: Close `R142`, `R143`, `R117`** — strike, evidence in place, move to closed
- [ ] **Step 2: CORRECT `R144` in place, THEN strike it**

Spec §2.5: `R144` records as a *measurement* that `R117` has no live instance. That is false and has
been since `tab-fno-align.ttl` was written. **The correction is the value; the closure is
bookkeeping.** Striking it silently would erase the evidence that the register's own anti-staleness
guard did not hold — which is precisely what `R144` was raised to prevent.

- [ ] **Step 3: Correct `R143`'s headline 209 → 203** (spec §2.7), noting that the 6 are
      `sh:namespace` literals and that the row warns about that contamination while carrying it
- [ ] **Step 4: Append the four new rows of spec §11**, each with its computed tally snapshot
- [ ] **Step 5: Run `python -m pytest tests/test_doc_governance.py -q`**
- [ ] **Step 6: Commit**

---

## Self-Review

**Spec coverage.** §2.1→T2 · §2.3→T3 · §2.4→T7 · §2.5→T4,T8 · §2.7→T8 · §2.8→T5 · §3→T5 (O6) ·
§4.1→T4 · §4.2→T1 · §4.3→T2 · §4.4→T3 · §4.5→T5 · §4.6→T6 · §4.7→T2 · §4.8→T7 · §5→T6 (O4) ·
§7 O1–O7→T6,T2,T3,T6,T6,T5,T6 · §9→Global Constraints (plan-rule 5 line) · §10 seams 1–7→T1,T7,T7,
T2,T5,T6,Global · §11→T8. **No gap found.**

**§4.7's open decision** (`etkl:alignmentSubject` — one predicate or two) is deliberately left to
seam 4 and resolved in Task 4 by writing the shape both ways. That is plan-rule 3 (*name the seam,
not the answer*), not a placeholder.

**Placeholder scan.** No "TBD"/"TODO"/"similar to Task N". Every code block is a **test**, never an
implementation body — CLAUDE.md plan-rule 1 forbids the latter and permits the former, conditional
on the mandatory falsification blocks, which every task carries.

**Type consistency.** `derive_vocabulary_terms()` / `derive_alignment_subjects()` /
`artifact_files()` / `artifact_graph_iri()` / `artifact_dataset()` / `declaring_files()` are used
under exactly these names in every task that references them.

**A contradiction found by this self-review, and SETTLED rather than shipped as a warning.** The
first draft asserted 53 undeclared demands both before and after Task 3, while spec §2.3 implied 54
after traversal. Neither was right. Running the traversal gave **55** — over the `.ttl` corpus alone
it recovers `docgov:cites` *as well as* `docgov:citesExternal`, because the `.rq` occurrence that
rescues `cites` is in a population this derivation does not read. Both documents were corrected
against the measurement (spec §2.3 now quotes the command and its output).

This is plan-rule 2 in its narrowest form: the constant was a load-bearing claim about code, it was
cheap to measure, and the draft that guessed it was wrong twice over. **Task 2 asserts 53 and Task 3
raises it to 55 in the commit that earns it** — two constants, each measured, neither adjusted to
make a suite go green.
