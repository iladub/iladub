"""The declaration membrane — O1, O4, O5 (spec §7; plan Task 2).

AXIOM, constraint form, closed world (CLAUDE.md §8): `vocab/shapes/query-declaration-shapes.ttl`
decides; this module only feeds it evidence and reads its verdict. The evidence comes from
`tests/query_terms.py` (PROCEDURAL), whose own oracles are `tests/test_query_terms.py`.

`inference="none"` in `_validate` is LOAD-BEARING and MEASURED (plan §0.1 F1). Under
`inference="rdfs"` — which is what `tests/test_vocab_shapes.py:22-27` hard-codes, and why that
helper is deliberately NOT reused here — owlrl adds `?term rdf:type rdfs:Resource` for EVERY
resource in the data graph, so the shape's `FILTER NOT EXISTS { ?term ?p ?o }` can never fire
and this whole instrument is green by not looking:

    # the two-term fixture below, validated twice, changing only `inference`:
    --- inference=rdfs: conforms=True
    --- inference=none: conforms=False
    # and the closure itself:
    triples with Undeclared as subject AFTER rdfs closure:
        (…etkl#Undeclared, rdf-syntax-ns#type, rdf-schema#Resource)

`test_a_query_naming_an_undeclared_term_is_refused` is the standing pin on that measurement:
restore `"rdfs"` and it goes green.
"""
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, Graph

from tests.query_terms import (
    ETKL,
    REPO,
    declaring_graph,
    evidence_graph,
    extract_named_terms,
    query_files,
)

SHAPES = REPO / "vocab" / "shapes" / "query-declaration-shapes.ttl"
LEAK_FIXTURE = Path(__file__).resolve().parent / "query-undeclared-term-leak.rq"
NESTED_FIXTURE = Path(__file__).resolve().parent / "query-nested-bind-exists.rq"

#: The smallest graph that can answer spec §10 seam 5: one query naming two terms, of which
#: exactly one is the subject of a triple. No term list (G3) — a fixture is not a population.
TWO_TERM_FIXTURE = """
@prefix etkl: <https://w3id.org/iladub/etkl#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .

<urn:iladub:query:two-term-fixture>
    a               etkl:QueryArtifact ;
    etkl:namesTerm  etkl:Declared , etkl:Undeclared .

etkl:Declared a owl:Class .
"""


def _validate(data_graph):
    """Validate an evidence graph against the declaration membrane.

    Deliberately NOT `tests/test_vocab_shapes.py::_validate`: that helper hard-codes
    `inference="rdfs"` (`tests/test_vocab_shapes.py:22-27`), which the module docstring
    measures as fatal here. `advanced=True` is required — the constraint is `sh:sparql`.
    """
    conforms, _, text = validate(
        data_graph,
        shacl_graph=Graph().parse(SHAPES, format="turtle"),
        inference="none",
        advanced=True,
    )
    return conforms, text


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
    # The fixture names one DECLARED term too. Without this, the test passes against a
    # membrane that refuses every named term — plan Task 2 Step 6 inversion 2 measured
    # exactly that: with `FILTER NOT EXISTS` deleted, the two assertions above both still
    # hold. Selectivity is the claim; assert it (G6: substitute the satisfiable form
    # carrying the same force, never weaken).
    assert "etkl#SemanticDataContract" not in report


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
    nodes is R97/R99's vacuity, and it passes.

    RE-MEASURED 2026-09-02 (spec §10 seam 6: compute the count, never copy it): 48 -> 49,
    `matrix-body-start.rq` this loop adds (2026-09-02-the-body-starts-at-the-stub-design.md
    § 3.1)."""
    data = evidence_graph() + declaring_graph()
    focus = set(data.subjects(RDF.type, ETKL.QueryArtifact))
    assert len(focus) == len(query_files()) == 49, sorted(focus)


def test_the_leak_fixture_is_not_in_the_population():
    """V5's shape, one directory over: a fixture that joined the population would turn the
    suite permanently red and the instrument permanently meaningless."""
    assert LEAK_FIXTURE not in query_files()
    assert NESTED_FIXTURE not in query_files()
