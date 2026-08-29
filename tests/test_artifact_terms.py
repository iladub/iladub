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
from tests.query_terms import OWNED_ROOT, REPO


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
