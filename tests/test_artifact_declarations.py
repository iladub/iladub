"""The declaration membrane over the `.ttl` corpus — O1–O7 (spec §7; plan Tasks 5–7).

AXIOM, constraint form, closed world (CLAUDE.md §8): `vocab/shapes/query-declaration-shapes.ttl`
decides; this module only feeds it evidence and reads its verdict. The evidence comes from
`tests/artifact_terms.py` (PROCEDURAL) and the two `CONSTRUCT` derivations in `vocab/queries/`
(AXIOM, derivation form, open world), whose own oracles are `tests/test_artifact_terms.py`.

`inference="none"` is LOAD-BEARING and inherited from R135 F1: under `inference="rdfs"` owlrl
adds `?term rdf:type rdfs:Resource` for EVERY resource in the data graph, so the shape's
`FILTER NOT EXISTS { ?term ?p ?o }` can never fire and the whole instrument is green by not
looking. `tests/test_vocab_shapes.py::_validate` hard-codes `"rdfs"` and is deliberately NOT
reused here.
"""
from rdflib import Graph, OWL, RDF, RDFS

from tests.query_terms import OWNED_ROOT, REPO

INTERNAL_DIR = REPO / "vocab" / "internal"
TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.NamedIndividual}
CORPUS = "https://w3id.org/iladub/corpus#"


def _internal_files():
    return sorted(INTERNAL_DIR.glob("*.ttl"))


def _declared_subjects(graph: Graph) -> set:
    """Owned subjects that are TERMS — the ontology DOCUMENT IRI is not one.

    The exclusion is positional (`?s a owl:Ontology`), never a name test, and it is the same
    exclusion `vocab/queries/alignment-subject.rq` makes for the same reason (spec §4.1).
    SUBSTITUTED from the plan's unfiltered `set(g.subjects())` (G6, plan rule 1): that form
    is unsatisfiable, because an ontology header carries `dcterms:title`, not `rdfs:label`,
    and `owl:Ontology` is not one of the four term types. Same force — every TERM is checked.
    """
    return {s for s in set(graph.subjects())
            if str(s).startswith(OWNED_ROOT)
            and (s, RDF.type, OWL.Ontology) not in graph}


def test_all_four_internal_vocabularies_exist():
    """RE-MEASURED 2026-08-31 (R139's instrument half): three -> four. `srccite.ttl` declares the
    terms of the source-comment citation lint, and it is under `vocab/internal/` for the reason
    `docgov.ttl`'s own header gives — the namespace is unregistered at w3id, so `vocab/ontology/`,
    the published surface, would contradict that statement."""
    assert {p.name for p in _internal_files()} == {
        "prog.ttl", "docgov.ttl", "corpus.ttl", "srccite.ttl"}


def test_every_internal_term_is_typed_and_labelled():
    """O6, first half (spec §7) — an authored vocabulary says what its terms ARE and what
    they MEAN. DELIBERATELY WEAK, and spec §7 says so: this detects a dump; it cannot detect
    a lazily worded comment. Do not overclaim it."""
    for path in _internal_files():
        g = Graph().parse(path, format="turtle")
        subjects = _declared_subjects(g)
        assert subjects, path.name
        for s in sorted(subjects):
            assert set(g.objects(s, RDF.type)) & TYPES, f"{path.name}: {s} has no owl: type"
            assert set(g.objects(s, RDFS.label)), f"{path.name}: {s} has no rdfs:label"
            assert set(g.objects(s, RDFS.comment)), f"{path.name}: {s} has no rdfs:comment"


def test_corpus_declares_terms_the_rule_never_demanded():
    """O6, second half — the authored surplus (spec §3, §2.6 class 3). A transcription of
    the census cannot pass this: enumerated individuals are node-role-only, so no positional
    rule reaches them, and an author must supply them anyway.

    This is the ONLY oracle on spec §3's independence hazard — that authoring the disposer's
    new half from a census of the proposer turns the instrument into a pin on its own
    registry.
    """
    from tests.artifact_terms import derive_vocabulary_terms
    from tests.query_terms import ETKL
    demanded = {str(o) for o in derive_vocabulary_terms().objects(None, ETKL.namesTerm)}
    g = Graph().parse(INTERNAL_DIR / "corpus.ttl", format="turtle")
    declared = {str(s) for s in _declared_subjects(g)}
    surplus = declared - demanded
    assert surplus, "corpus.ttl declares nothing beyond what the rule demanded"
    # STRENGTHENED beyond the plan's form, which could not be falsified as the plan asked
    # (G6). "Some surplus exists" has several independent sources here, so deleting the
    # verdict individuals — the plan's own falsification instruction — left it green. The
    # individuals are spec §4.5's NAMED requirement and §2.6 class 3's measured case, so
    # pin them by name; now deleting them turns this red, which is what a falsification
    # block is for.
    assert {CORPUS + n for n in ("CompilesAbove", "SemanticEscalation", "Unadjudicated")} <= surplus


def test_the_declaring_graph_now_includes_the_internal_vocabularies():
    from tests.query_terms import declaring_files
    assert {p.name for p in declaring_files()} >= {"prog.ttl", "docgov.ttl", "corpus.ttl"}


# =========================================================================================
# The membrane over the `.ttl` corpus — O1, O2, O4, O5, O7 (spec §7).
# =========================================================================================

import pytest
from pyshacl import validate

from tests.artifact_terms import (
    FIXTURE_DIR,
    artifact_files,
    derive_alignment_subjects,
    derive_vocabulary_terms,
    from_fixture,
)
from tests.query_terms import ETKL, declaring_graph, evidence_graph, query_files

SHAPES = REPO / "vocab" / "shapes" / "query-declaration-shapes.ttl"
LEAK_FIXTURE = FIXTURE_DIR / "artifact-undeclared-term-leak.ttl"


def _validate(data_graph):
    """`inference="none"` is LOAD-BEARING — see the module docstring. `advanced=True` is
    required because the constraint is `sh:sparql`."""
    conforms, _, text = validate(
        data_graph,
        shacl_graph=Graph().parse(SHAPES, format="turtle"),
        inference="none",
        advanced=True,
    )
    return conforms, text


def evidence() -> Graph:
    """The whole evidence graph the membrane validates: both artifact families, both demands."""
    return derive_vocabulary_terms() + derive_alignment_subjects() + evidence_graph()


def test_the_membrane_binds_one_focus_node_per_artifact():
    """O4 (spec §7) — asserted as NUMBERS, never '> 0'. A shape binding zero focus nodes is
    R97/R99's vacuity, and it passes. Both counts RE-MEASURED, never copied from the spec
    (§10 seam 6): the `.ttl` population grew to 139 when this loop authored three
    vocabularies, and the `.rq` population to 48 when it authored two derivations.

    RE-MEASURED 2026-08-30 (R128's closure): the `.ttl` population is **144** — the five added
    are `examples/supersession.ttl` and the four `tests/supersession-*.ttl` negatives, which
    bind a focus node like any other artifact and name declared terms only. The `.rq`
    population is unchanged at 48. See `test_artifact_terms.py`'s own note for why a green
    local suite run does not predict this count: the population is `git ls-files`, so a new
    `.ttl` joins it at `git add`, not at creation.

    RE-MEASURED 2026-08-31 (R139's instrument half): the `.ttl` population is **146** — the two
    added are `vocab/internal/srccite.ttl` and `vocab/shapes/source-citation-shapes.ttl`, the
    declaration and the membrane of the source-comment citation lint. The `.rq` population is
    unchanged at 48: that lint derives nothing, so it authored no query.

    RE-MEASURED 2026-09-02 (spec §10 seam 6: compute the count, never copy it): the `.rq`
    population is **49** — `vocab/queries/matrix-body-start.rq`, the AXIOM derivation the
    2026-09-02 the-body-starts-at-the-stub loop adds (spec
    `2026-09-02-the-body-starts-at-the-stub-design.md` § 3.1). The `.ttl` population is
    unchanged at 146: that loop authored no vocabulary.

    RE-MEASURED 2026-09-04: the `.rq` population is **50** — `vocab/queries/band-run.rq`, the
    adjacent-subsumption run derivation the R165 the-run-is-one-band loop adds (spec
    `2026-09-04-the-run-is-one-band-design.md` § 3.4). The `.ttl` population is unchanged at
    146: that loop declares its four new terms inside the existing `vocab/ontology/tab.ttl`."""
    data = evidence() + declaring_graph()
    vocab_nodes = set(data.subjects(RDF.type, ETKL.VocabularyArtifact))
    query_nodes = set(data.subjects(RDF.type, ETKL.QueryArtifact))
    assert len(vocab_nodes) == len(artifact_files()) == 146
    assert len(query_nodes) == len(query_files()) == 50


def test_a_ttl_naming_an_undeclared_term_is_refused():
    """O5 (spec §7) — the negative fixture § Serialization requires.

    The fixture also names a DECLARED term. Without that assertion this test passes against
    a membrane that refuses EVERY term; selectivity is the claim, so assert it.
    """
    data = derive_vocabulary_terms(from_fixture(LEAK_FIXTURE)) + declaring_graph()
    conforms, report = _validate(data)
    assert not conforms, report
    assert "artifact-undeclared-term-leak.ttl" in report
    assert "etkl#NoSuchTermAnywhere" in report
    assert "etkl#SemanticDataContract" not in report


def test_a_blank_node_path_fixture_is_refused():
    """O3 (spec §7) at the MEMBRANE, not only at the derivation. Stated in this direction
    deliberately: remove the path-expression traversal and the validation CONFORMS, so this
    test FAILS — 'must pass' is ambiguous between those and they are opposites here."""
    from tests.artifact_terms import BLANK_PATH_FIXTURE
    data = derive_vocabulary_terms(from_fixture(BLANK_PATH_FIXTURE)) + declaring_graph()
    conforms, report = _validate(data)
    assert not conforms, report
    assert "etkl#NoSuchPathTermAnywhere" in report
    assert "etkl#SemanticDataContract" not in report


def test_the_exemption_is_gone():
    """O7 (spec §7). While the filter existed the instrument could not see those namespaces
    even if a term went missing — the deletion IS the oracle."""
    text = SHAPES.read_text(encoding="utf-8")
    assert "progress#" not in text
    assert "docgov#" not in text


def test_every_artifact_names_only_declared_terms():
    """O1 + O2 (spec §7) — the instrument, over the whole authored corpus, both families.

    This shipped RED, deliberately and in its own commit (36ab900), carrying an
    `xfail(strict=True)` marker and the eight quoted refusals: `etkl:Contract` in both
    federation contracts (O1) and the six `tab:aggFn*` in `tab-fno-align.ttl` (O2). The
    marker came off in the commit that repaired them. A membrane that was green on its first
    run would never have been shown to read the new files at all — that is `R143`'s own
    warning, and this is the answer to it.
    """
    conforms, report = _validate(evidence() + declaring_graph())
    assert conforms, report
