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
    tracked = _tracked_ttl()
    carved = [p for p in tracked if p.startswith(FIXTURE_DIR.relative_to(REPO).as_posix() + "/")]
    assert len(artifact_files()) == len(tracked) - len(carved) == 136


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

        occurrences 18   (sh:namespace 11, vann:preferredNamespaceUri 7)
        distinct values 7

    (§2.7's sub-breakdown "×12, ×8" does not reproduce; the total 18 does. Recorded as a
    correction, not adjusted away.) Asserted here as EXACT NUMBERS rather than the plan's
    floor — a floor cannot detect the guard silently collecting fewer, which is the failure
    this test exists to catch.
    """
    ds = artifact_dataset()
    occurrences = [o for _, _, o, _ in ds.quads((None, None, None, None))
                   if isinstance(o, Literal) and str(o).startswith(OWNED_ROOT)]
    assert len(occurrences) == 18
    assert len({str(o) for o in occurrences}) == 7
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
    from tests.query_terms import declaring_graph
    return {str(s) for s in declaring_graph().subjects()}


def _undeclared_demands() -> set[str]:
    declared = _declared()
    return {t for t in _demanded() if t not in declared}


def test_the_rule_demands_55_undeclared_terms():
    """Spec §2.2 measured 53 before the SHACL path traversal of spec §4.4; §2.3 measured
    55 after it. Asserted as a NUMBER. This count moves only when the tree does — and the
    step from 53 to 55 was EARNED, in the commit that added the traversal, never adjusted
    to make a suite go green. `test_the_path_traversal_adds_exactly_two_terms` holds the
    delta and names the two terms."""
    assert len(_undeclared_demands()) == 55


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
    """Spec §2.3, MEASURED by running the traversal: 53 without it, 55 with it, and the
    two added are docgov:cites and docgov:citesExternal. Over the .ttl corpus ALONE both
    are hidden — docgov:cites's rescuing occurrence is in the .rq population, which this
    derivation does not read. Asserting the delta as well as the total is what makes this
    a check that the traversal does not OVER-reach."""
    assert len(_undeclared_demands()) == 55
    assert {DOCGOV + "cites", DOCGOV + "citesExternal"} <= _undeclared_demands()


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


def _align_demands() -> set[str]:
    from tests.artifact_terms import derive_alignment_subjects
    g = derive_alignment_subjects()
    return {str(o) for o in g.objects(None, ETKL.namesTerm)} - _declared()


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
