"""Oracles for the artifact dataset and the two demands (spec §4.1–§4.4, plan Tasks 1–4).

PROCEDURAL step under test in this first block: `tests/artifact_terms.py` attributes and
parses; it decides nothing. The deciding is done by the two `CONSTRUCT` derivations
(AXIOM, open world) and by the membrane (AXIOM, closed world, `tests/test_artifact_declarations.py`).
"""
import subprocess

import pytest
from rdflib import Literal, URIRef

from tests.artifact_terms import (
    FIXTURE_DIR,
    artifact_dataset,
    artifact_files,
    artifact_graph_iri,
)
from tests.query_terms import ETKL, OWNED_ROOT, REPO


def _tracked_ttl() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "*.ttl"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def test_the_population_is_every_tracked_ttl_outside_the_fixture_directory():
    """Enumerated from git, never typed (G3). Asserted as a NUMBER, not '> 0' (R97/R99).

    SUBSTITUTED from the plan's `len(artifact_files()) == len(tracked) == 136` (G6, plan
    rule 1: a plan-supplied test is a proposition). That form is unsatisfiable from Task 3
    onward: the corpus is EVERY tracked `.ttl`, so the negative fixtures this loop must
    commit would join their own population and turn it permanently red. They are carved out
    by DIRECTORY — a population definition, exactly as `query_files()`'s
    `vocab/queries/*.rq` is one — and this test asserts the carve-out arithmetic rather
    than assuming the directory is empty. Same force: the population is git's answer, minus
    a named directory, and both halves are counted.
    """
    # RE-MEASURED after Task 5 (spec §10 seam 6: compute the count, never copy it):
    # 136 -> 139, the three authored vocabularies under vocab/internal/. They are artifacts
    # like any other and are read by the same rule that reads the rest.
    #
    # RE-MEASURED AGAIN 2026-08-30 (R128's closure): 139 -> 144, `git ls-files "*.ttl"` = 146
    # minus the 2 carved. The five are `examples/supersession.ttl` and the four
    # `tests/supersession-*.ttl` negatives. They are NOT carved out and must not be: the
    # carve-out is by DIRECTORY (`tests/artifact-fixtures/`) and exists only for fixtures that
    # would fail THIS membrane by design. These four are negatives for `dec-shapes.ttl` and
    # name declared terms only, so they belong in the population like
    # `tests/expansion-request-leak.ttl` before them.
    #
    # RE-MEASURED AGAIN 2026-08-31 (R139's instrument half): 144 -> 146, `vocab/internal/
    # srccite.ttl` and `vocab/shapes/source-citation-shapes.ttl` — the declaration and the
    # membrane of the source-comment citation lint. Both are artifacts like any other.
    #
    # WHY CI CAUGHT THIS AND A LOCAL RUN DID NOT: the population is `git ls-files`, so a new
    # `.ttl` joins it at `git add`, not at creation. A full local suite run against an
    # uncommitted tree is green on a count this test will fail the moment the files are staged.
    tracked = _tracked_ttl()
    carved = [p for p in tracked if p.startswith(FIXTURE_DIR.relative_to(REPO).as_posix() + "/")]
    assert len(artifact_files()) == len(tracked) - len(carved) == 146


def test_each_file_gets_its_own_named_graph():
    """Role is per-graph (spec §2.1); a flat union would destroy it."""
    ds = artifact_dataset()
    contexts = {c.identifier for c in ds.graphs() if len(c)}
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
    """Spec §2.7: owned-root-prefixed LITERALS exist (sh:namespace, vann:preferredNamespaceUri).

    This is the standing pin on the `isinstance(node, URIRef)` guard. Without it the
    register's own headline count was inflated by 6.

    SUBSTITUTED from the plan's `len(literals) >= 12` (G6, plan rule 1). That assertion is
    unsatisfiable and its subject was the wrong set: distinct `Literal` TERMS number 11, not
    12, because the same namespace string appears both as `xsd:anyURI` (sh:namespace) and as
    a plain string (vann:preferredNamespaceUri) and those are two distinct terms. Spec §2.7's
    figure is 18, and 18 is the OCCURRENCE count — MEASURED 2026-08-29 over this population:

        occurrences 18   (sh:namespace 11, vann:preferredNamespaceUri 7)   [136 artifacts]
        distinct values 7

    RE-MEASURED after Task 5, which authors three more artifacts each carrying its own
    `vann:preferredNamespaceUri`:

        occurrences 21   distinct values 8   [139 artifacts]

    The eighth distinct value is `https://w3id.org/iladub/docgov#`, present now as a plain
    string as well as the `xsd:anyURI` a shape already carried.

    RE-MEASURED 2026-08-31 (R139's instrument half), which authors a fourth internal
    vocabulary carrying its own `vann:preferredNamespaceUri`:

        occurrences 22   distinct values 9   [146 artifacts]

    The ninth is `https://w3id.org/iladub/srccite#`. It appears ONCE, not twice as `docgov#`
    does: `source-citation-shapes.ttl` writes full IRIs inside its `sh:select` rather than
    declaring an `sh:namespace`, so no `xsd:anyURI` twin exists.

    (§2.7's sub-breakdown "×12, ×8" does not reproduce; the total 18 does. Recorded as a
    correction, not adjusted away.) Asserted here as EXACT NUMBERS rather than the plan's
    floor — a floor cannot detect the guard silently collecting fewer, which is the failure
    this test exists to catch.
    """
    ds = artifact_dataset()
    occurrences = [o for _, _, o, _ in ds.quads((None, None, None, None))
                   if isinstance(o, Literal) and str(o).startswith(OWNED_ROOT)]
    assert len(occurrences) == 22
    assert len({str(o) for o in occurrences}) == 9
    assert not any(isinstance(o, URIRef) for o in occurrences)


# =========================================================================================
# D1 — the vocabulary-role derivation (spec §2.1, §4.3). AXIOM, derivation form, open world.
# Numbers below are spec §2.2/§2.3, re-measured here.
# =========================================================================================

PROG = "https://w3id.org/iladub/progress#"


def _demanded() -> set[str]:
    from tests.artifact_terms import derive_vocabulary_terms
    return {str(o) for o in derive_vocabulary_terms().objects(None, ETKL.namesTerm)}


def _declared() -> set[str]:
    """Everything the disposer declares TODAY: published ontologies + vocab/internal."""
    from tests.query_terms import declaring_graph
    return {str(s) for s in declaring_graph().subjects()}


def _declared_by_published_only() -> set[str]:
    """The disposer as it stood BEFORE this loop widened it — the PUBLISHED, w3id-registered
    ontologies alone.

    Two different questions were being asked under one name, and Task 5 forced them apart
    (recorded here as a plan defect, G6). "How many terms does the rule DEMAND that no
    published ontology declares?" is the CENSUS — spec §2.2's 53 and §2.3's 55 — and it is a
    property of the rule and the tree, fixed for good. "How many demands are still
    undischarged?" is the INSTRUMENT's live reading, and authoring vocab/internal/ is exactly
    what was supposed to drive it to the two real defects. Measuring the first against the
    widened disposer collapses it to the second and destroys the census; the plan's Task 2 and
    Task 3 tests did that, because they were written before Task 5 existed.
    """
    from rdflib import Graph
    from tests.query_terms import ONTOLOGY_DIR
    graph = Graph()
    for path in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        if not path.name.endswith("-align.ttl"):
            graph.parse(path, format="turtle")
    return {str(s) for s in graph.subjects()}


def _census() -> set[str]:
    """The rule's yield against the published ontologies — spec §2.2/§2.3's question."""
    return _demanded() - _declared_by_published_only()


#: The commit at which the 136-artifact tree below was the whole tree: the parent of the commit
#: that added `vocab/internal/`. `git log --diff-filter=A -- vocab/internal/docgov.ttl` names the
#: adder, `435049f8`, and `git ls-tree -r --name-only 72d0cffc | grep -c '\.ttl$'` is 137, minus
#: the one fixture = **136**. RE-MEASURED 2026-08-31.
_PRE_INTERNAL_COMMIT = "72d0cffcecf8081ed1c1b3905a3dbbd51c2a0c19"


def _pre_loop_artifacts():
    """The 136 tracked `.ttl` spec §2.2/§2.3 measured, i.e. before vocab/internal/ existed.

    RECONSTRUCTED FROM GIT, not proxied. This used to be `artifact_files()` minus
    `vocab/internal/`, which was exact when written and silently drifts afterwards: EVERY later
    loop's non-internal `.ttl` joins a population that is supposed to be a fixed historical tree.
    It had already drifted to 141 by R128's five `supersession-*.ttl`, and stayed green only
    because those five happen to name no undeclared owned term — so the defect was invisible
    until a loop added one that does (R139's `srccite:Citation`, 2026-08-31, which is exactly
    what exposed it). Naming the commit removes the hazard instead of guarding it; a file
    deleted since is simply absent from `artifact_files()` and drops out on its own.
    """
    tracked_then = set(subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", _PRE_INTERNAL_COMMIT],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.split())
    return [p for p in artifact_files() if p.relative_to(REPO).as_posix() in tracked_then]


def _census_over(files) -> set[str]:
    """The census restricted to a chosen sub-population, so the two trees stay comparable."""
    from rdflib import Dataset
    from tests.artifact_terms import artifact_graph_iri, derive_vocabulary_terms
    dataset = Dataset()
    for path in files:
        dataset.graph(artifact_graph_iri(path)).parse(path, format="turtle")
    demanded = {str(o) for o in derive_vocabulary_terms(dataset).objects(None, ETKL.namesTerm)}
    return demanded - _declared_by_published_only()


def _undeclared_demands() -> set[str]:
    """What the instrument still refuses TODAY, against the full declaring graph."""
    return _demanded() - _declared()


CORPUS = "https://w3id.org/iladub/corpus#"

#: The two artifacts the census is measured over, and why there are two. Spec §2.2/§2.3
#: measured the rule's yield over the 136 tracked `.ttl` that existed BEFORE this loop
#: authored three more; those three are themselves artifacts, read by the same rule.
#:
#: EXTENDED 2026-08-31 (R139's instrument half). The set is the difference between the census
#: over the live tree and the census over the 136-artifact tree, so EVERY later loop that
#: authors an owned term outside that historical tree belongs in it. `srccite:Citation` is
#: R139's. The O6 AUTHORSHIP CLAIM below is unchanged and is about the first two only: those
#: are the terms an author supplied that no positional rule demanded.
SRCCITE = "https://w3id.org/iladub/srccite#"
_SURPLUS_IN_CENSUS = {
    CORPUS + "Verdict", CORPUS + "Adjudication",   # 2026-08-30, R128's loop
    SRCCITE + "Citation",                          # 2026-08-31, R139's loop
}


def test_the_census_chain_from_53_to_57_with_every_step_earned():
    """Every step of the census is a NUMBER, and every step was EARNED by a named change in
    the commit that caused it — never adjusted to make a suite go green:

        53   spec §2.2, over the 136 tracked .ttl, before the SHACL path traversal
        55   + the path traversal of §4.4 (docgov:cites, docgov:citesExternal)
        57   + vocab/internal/ joining the population as three more artifacts
        56   - etkl:Contract, repaired; and 54 over the 136-artifact tree
        57   + srccite:Citation, R139's citation membrane (2026-08-31)

    THAT LAST STEP IS ONE TERM, NOT EIGHT: `source-citation-shapes.ttl` names
    `srccite:Citation` as an `sh:targetClass` OBJECT, and its seven properties appear only
    inside the `sh:select` STRING, where they are a run of characters and not RDF nodes at
    all. R150's class, live again — and the reason `srccite.ttl` declares all eight anyway.

    The plan pinned 53 and 55 and stopped there, so Tasks 5 and 7 each invalidated a constant
    the plan had written as fixed (G6, recorded rather than quietly retuned). That is not a
    tuned constant: a census is a measurement OF A TREE, and this loop changes the tree twice
    — once by authoring vocabulary, once by repairing a leak. Both deltas are asserted below.

    Measured against the PUBLISHED ontologies: this is the CENSUS question — what the rule
    demands that no published ontology declares — and it is a property of the rule and the
    tree. It is NOT the instrument's live reading, which `test_the_only_undeclared_demands_
    left_are_the_two_live_defects` holds. Conflating the two destroys the census, and the
    plan's Task 2 and Task 3 tests did exactly that, having been written before Task 5 existed.

    THE DELTA IS THE AUTHORSHIP EVIDENCE, and this is a second and sharper O6 (spec §7).
    Authoring the three internal vocabularies moved the census by exactly two, and the two
    are `corpus:Verdict` and `corpus:Adjudication` — classes the pre-loop tree NEVER demanded,
    which exist because an author decided what the verdict individuals and the adjudication
    nodes ARE. A transcription of the census cannot move the census.
    """
    assert len(_census_over(_pre_loop_artifacts())) == 54
    assert len(_census()) == 57
    assert _census() - _census_over(_pre_loop_artifacts()) == _SURPLUS_IN_CENSUS


def test_the_prog_vocabulary_is_21_terms():
    """Spec §2.3 (M3): the role rule reproduces R142's corrected census term-for-term,
    by a method that shares nothing with the lexical scan that produced it."""
    assert len({t for t in _census() if t.startswith(PROG)}) == 21


def test_the_etkl_leak_is_repaired_and_nothing_is_left_undeclared():
    """Spec §2.4 (M4) — O1's subject, AFTER the repair.

    Written as a pin on the repair rather than on the defect, because Task 7 removes the
    defect and a test asserting `etkl:Contract in _undeclared_demands()` — which is what the
    plan supplied — cannot survive its own loop (G6). The evidence that the defect was real
    is the RED commit 36ab900, which quotes the eight refusals, and the FALSIFICATION block
    that restores `etkl:Contract` and shows O1 red again.

    The second assertion is the stronger claim: after both repairs NOTHING the two demands
    reach is undeclared. That is the state the membrane is now holding.
    """
    from tests.query_terms import REPO
    for name in ("doc-a-contract.ttl", "doc-b-contract.ttl"):
        text = (REPO / "examples" / "federation" / name).read_text(encoding="utf-8")
        assert "etkl:SemanticDataContract" in text
        assert "etkl:Contract " not in text and "etkl:Contract;" not in text
    assert _undeclared_demands() == set()


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
    from rdflib import RDF
    from tests.artifact_terms import derive_vocabulary_terms
    g = derive_vocabulary_terms()
    typed = set(g.subjects(RDF.type, ETKL.VocabularyArtifact))
    assert len(typed) == len(artifact_files())
    assert all(isinstance(s, URIRef) for s in typed)


# =========================================================================================
# Task 3 — SHACL property-path traversal (spec §2.3, §4.4). Positional, not heuristic: a term
# inside a property path IS being used as a property, and the construct set is exhaustively
# fixed by the SHACL recommendation, so completeness is by construction, not by tuning.
# =========================================================================================

DOCGOV = "https://w3id.org/iladub/docgov#"


def test_a_term_inside_a_blank_node_path_is_reached():
    """O3 (spec §7). The sole blank-node sh:path in the tree hides docgov:citesExternal
    behind an RDF list (spec §2.3); its sibling docgov:cites survives only by accident,
    because a .rq also names it."""
    assert DOCGOV + "citesExternal" in _demanded()


def test_the_path_traversal_adds_exactly_two_terms():
    """Spec §2.3, MEASURED by running the traversal rather than predicting it: over the
    136-artifact tree the census was 53 without it and 55 with it, and the two added are
    docgov:cites and docgov:citesExternal. Over the .ttl corpus ALONE both are hidden —
    docgov:cites's rescuing occurrence is in the .rq population, which this derivation does
    not read. Asserting the DELTA as well as the total is what makes this a check that the
    traversal does not OVER-reach.

    The total here is 54, not 55: repairing etkl:Contract removed one term from the same
    tree (see `test_the_census_chain_from_53_to_57_with_every_step_earned` for the full
    chain). The two terms this test is about are unaffected, and are asserted by name — the
    number alone was never the claim."""
    assert len(_census_over(_pre_loop_artifacts())) == 54
    assert {DOCGOV + "cites", DOCGOV + "citesExternal"} <= _census()


def test_the_fixture_path_hides_an_undeclared_term_from_a_naive_reading():
    """The traversal, isolated on the fixture, WITH its selectivity asserted.

    Both owned terms sit behind the same blank node and the same RDF list, so a derivation
    that reads only the direct object of sh:path sees NEITHER. One of them is declared and
    one is not, so a derivation that demands everything it reaches would fail this too.
    """
    from tests.artifact_terms import (
        BLANK_PATH_FIXTURE,
        derive_vocabulary_terms,
        from_fixture,
    )
    demanded = {str(o) for o in
                derive_vocabulary_terms(from_fixture(BLANK_PATH_FIXTURE)).objects(None, ETKL.namesTerm)}
    assert "https://w3id.org/iladub/etkl#NoSuchPathTermAnywhere" in demanded
    assert "https://w3id.org/iladub/etkl#SemanticDataContract" in demanded
    assert demanded - _declared() == {"https://w3id.org/iladub/etkl#NoSuchPathTermAnywhere"}
    assert demanded - _declared_by_published_only() == {"https://w3id.org/iladub/etkl#NoSuchPathTermAnywhere"}


def test_the_fixtures_are_not_in_the_population():
    """A fixture that joined the population would turn the suite permanently red and the
    instrument permanently meaningless."""
    names = {p.name for p in artifact_files()}
    assert "artifact-blank-path-fixture.ttl" not in names
    assert "artifact-undeclared-term-leak.ttl" not in names


# =========================================================================================
# D2 — align-module subjects (spec §4.1). R117's own sentence, turned into an oracle.
# AXIOM, derivation form, open world; licensed by the PURPOSE of the file family rather than
# by triple position, which is exactly why it cannot be folded into D1.
# =========================================================================================

TAB = "https://w3id.org/iladub/tab#"


def _align_demanded() -> set[str]:
    """Everything D2 demands, before any disposer is consulted."""
    from tests.artifact_terms import derive_alignment_subjects
    return {str(o) for o in derive_alignment_subjects().objects(None, ETKL.namesTerm)}


def _align_demands() -> set[str]:
    """What D2 demands that nothing declares — the instrument's live reading."""
    return _align_demanded() - _declared()


#: R117's live instance, dangling from the day tab-fno-align.ttl was written until 2026-08-29.
AGG_FNS = {TAB + n for n in
           ("aggFnSum", "aggFnMean", "aggFnMin", "aggFnMax", "aggFnCount", "aggFnProduct")}


def test_the_six_aggregation_terms_are_demanded_and_now_declared():
    """O2's subject (spec §2.5, M5) — R117's live instance, and its repair.

    D2 still DEMANDS all six: that is the demand R117 asked for and it must not weaken.
    What changed is the disposer — vocab/ontology/tab.ttl declares them — so the demand is
    now discharged rather than dangling. Asserting both halves is what keeps this a test of
    the instrument and not merely of the repair: `_align_demanded()` is the raw demand,
    `_align_demands()` is what survives the declaring graph.
    """
    assert AGG_FNS <= _align_demanded()
    assert _align_demands() == set()


def test_ontology_document_iris_are_not_demanded():
    """Spec §4.1: 9 before the owl:Ontology exclusion, 6 after. An ontology document IRI
    is not a vocabulary term and no ontology declares it."""
    assert "https://w3id.org/iladub/hga-alignment" not in _align_demanded()
    assert "https://w3id.org/iladub/dec/hga-alignment" not in _align_demanded()


def test_d2_reaches_something_d1_cannot():
    """The whole justification for a second demand (spec §4.1), measured WHERE IT IS TRUE:
    over the align family itself.

    Spec §2.6 class 1 measures the align family's vocabulary-role count at ZERO — an aligned
    term is always a SUBJECT, so D1 is structurally blind there. Restricted to
    `tab-fno-align.ttl`, D1 reaches nothing and D2 reaches all six.

    RESTRICTED to that one file rather than asserting over the whole tree (G6): since Task 7
    declared the six in tab.ttl, D1 now reaches them THERE, as the objects of their own
    `rdf:type` triples. That is real and harmless, and it would silently hollow out the
    whole-tree form of this assertion — which is exactly the kind of test that passes while
    pinning nothing.
    """
    from rdflib import Dataset
    from tests.artifact_terms import (artifact_graph_iri, derive_alignment_subjects,
                                      derive_vocabulary_terms)
    from tests.query_terms import ONTOLOGY_DIR
    align = ONTOLOGY_DIR / "tab-fno-align.ttl"
    ds = Dataset()
    ds.graph(artifact_graph_iri(align)).parse(align, format="turtle")
    d1 = {str(o) for o in derive_vocabulary_terms(ds).objects(None, ETKL.namesTerm)}
    d2 = {str(o) for o in derive_alignment_subjects(ds).objects(None, ETKL.namesTerm)}
    assert d1 == set()
    assert d2 == AGG_FNS
