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


def test_all_three_internal_vocabularies_exist():
    assert {p.name for p in _internal_files()} == {"prog.ttl", "docgov.ttl", "corpus.ttl"}


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
