"""Artifact-term extractor — PROCEDURAL (CLAUDE.md §8 gate; spec §4.2, §6).

Justification, stated here and not merely cited, because §8 requires the justification to
live in the code: this module reads tracked Turtle source text and turns it into an RDF
dataset with per-file attribution. It is IRREDUCIBLE TO AXIOM because there is no evidence
graph to derive over until it has run — it is the step that MAKES one; a `CONSTRUCT` cannot
parse a file it cannot yet see. It is IRREDUCIBLE TO NEURAL because nothing here is
perceptual or underdetermined: a file either parses or raises, and a path either is tracked
by git or is not. No threshold, tolerance or tuned constant appears in this module.

THIS MODULE DECIDES NOTHING. It parses and attributes. Every question of WHICH terms matter
belongs to the two derivations in `vocab/queries/` (AXIOM, derivation form, open world), and
the question of which of those must be declared belongs to the membrane in
`vocab/shapes/query-declaration-shapes.ttl` (AXIOM, constraint form, closed world).

NAMED GRAPHS, NOT A FLAT UNION, for a stated reason: vocabulary role is a PER-GRAPH property
(spec §2.1). Under a flat union a term could borrow a vocabulary role from a file it never
appears in, and provenance-to-the-file (CLAUDE.md §6) would not survive into the failure
message.

It never imports `iladub`: from a worktree the editable install resolves that package to the
MAIN tree (R114/R121), so an instrument that imports it can be silently re-opened by the tree
it is meant to be measuring. The repo is located from `__file__`, as `tests/query_terms.py`
does.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from rdflib import RDF, Dataset, Graph, URIRef

from tests.query_terms import ETKL, OWNED_ROOT, REPO  # noqa: F401  (ETKL/OWNED_ROOT re-exported)

QUERY_DIR = REPO / "vocab" / "queries"

#: Fixtures that are DELIBERATELY invalid under this membrane. They are tracked (§ Serialization
#: requires a negative test that must fail, and it must be committed), and the population is
#: every tracked `.ttl` — so without a carve-out they would join their own population and turn
#: the corpus permanently red. The carve-out is one NAMED DIRECTORY, which is a population
#: definition of exactly the kind `query_files()`'s `vocab/queries/*.rq` is — not a term filter,
#: not a name pattern, not a tuned constant. `test_the_fixtures_are_not_in_the_population` pins it.
FIXTURE_DIR = REPO / "tests" / "artifact-fixtures"

#: Minted subjects for the evidence graph. Not an owned namespace, so an artifact IRI can never
#: collide with a term under test; repo-relative, so no absolute local path reaches a failure
#: message.
_ARTIFACT_IRI_BASE = "urn:iladub:artifact:"


def artifact_files() -> list[Path]:
    """The population: every tracked `.ttl` outside `FIXTURE_DIR`, sorted.

    Enumerated from `git ls-files`, never from a hard-coded list (G3). `-z` because a tracked
    path is allowed to contain a space; MEASURED 2026-08-29 — none currently does, and the
    repo's own containing directory (`/Volumes/WD Green/…`) never reaches this output because
    `git ls-files` prints repo-relative paths.

    `git ls-files` is the ENUMERATION; the population is what `artifact_dataset()` can parse,
    and a file that fails to parse raises there rather than being dropped here.
    """
    out = subprocess.run(
        ["git", "ls-files", "-z", "*.ttl"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    paths = [REPO / p for p in out.split("\0") if p]
    return sorted(p for p in paths if FIXTURE_DIR not in p.parents)


def artifact_graph_iri(path: Path) -> URIRef:
    """`urn:iladub:artifact:<repo-relative posix path>`."""
    return URIRef(_ARTIFACT_IRI_BASE + Path(path).resolve().relative_to(REPO).as_posix())


def artifact_dataset() -> Dataset:
    """Every artifact parsed into its OWN named graph, keyed by `artifact_graph_iri`.

    A parse failure RAISES, naming the file (spec §4.2). Never a silent skip: a skipped file
    is an instrument that is green by not looking.
    """
    dataset = Dataset()
    for path in artifact_files():
        try:
            dataset.graph(artifact_graph_iri(path)).parse(path, format="turtle")
        except Exception as exc:                   # noqa: BLE001 — re-raised, never swallowed
            raise ValueError(f"{path}: Turtle parse failed: {exc}") from exc
    return dataset


def from_fixture(path: Path) -> Dataset:
    """One fixture file as a one-graph dataset, so a derivation can be run over it alone."""
    dataset = Dataset()
    dataset.graph(artifact_graph_iri(path)).parse(path, format="turtle")
    return dataset


# --------------------------------------------------------------------------------------
# The derivations. These are AXIOM steps and live in `vocab/queries/*.rq`; the code below
# only RUNS them and attributes their results. It states no rule of its own.
# --------------------------------------------------------------------------------------

VOCABULARY_ROLE_QUERY = QUERY_DIR / "vocabulary-role.rq"


def _run_construct(query_path: Path, dataset: Dataset | None = None) -> Graph:
    """Run one authored `CONSTRUCT` over the artifact dataset and return its product."""
    dataset = artifact_dataset() if dataset is None else dataset
    graph = Graph()
    for triple in dataset.query(query_path.read_text(encoding="utf-8")):
        graph.add(triple)
    return graph


def derive_vocabulary_terms(dataset: Dataset | None = None) -> Graph:
    """D1 (spec §4.3): every owned IRI an artifact USES AS VOCABULARY.

    The `a etkl:VocabularyArtifact` typing is added here for EVERY file in the population,
    not only for those the derivation found a term in: being in the population is what makes
    a file a vocabulary artifact, and that is attribution, not a decision. Which TERMS it
    names is the query's answer and only the query's — exactly as `extract_named_terms`
    types a `.rq` in Python and takes its terms from the extractor.
    """
    dataset = artifact_dataset() if dataset is None else dataset
    graph = _run_construct(VOCABULARY_ROLE_QUERY, dataset)
    for context in dataset.graphs():
        if len(context) and isinstance(context.identifier, URIRef):
            graph.add((context.identifier, RDF.type, ETKL.VocabularyArtifact))
    return graph
