"""tab:bodyStartsAt — the header/body boundary, carried as evidence rather than assumed
(spec 2026-08-07-harden-transposition-oracles-design.md §2.1/§2.2).

The DEFAULT of 1 is load-bearing: it reproduces the behaviour every caller had before this
term existed, so rowheaders, header_body_split and the existing suites are unchanged by
construction rather than by inspection.
"""
from rdflib import Namespace, Literal
from rdflib.namespace import RDF, XSD

TAB = Namespace("https://w3id.org/iladub/tab#")

CELLS = [(0, 0, "Region"), (0, 1, "Value"), (1, 0, "North"), (1, 1, "10")]


def _band_node(g):
    nodes = list(g.subjects(RDF.type, TAB.ClassifyBand))
    assert len(nodes) == 1, f"expected exactly one band node, got {nodes}"
    return nodes[0]


def test_the_default_records_a_body_start_of_one():
    """Today's assumption, now stated in the evidence instead of hidden in a query."""
    from iladub.etkl import celltype
    g = celltype.grid_evidence(CELLS, 2)
    assert (_band_node(g), TAB.bodyStartsAt, Literal(1, datatype=XSD.integer)) in g


def test_an_explicit_body_start_is_carried():
    from iladub.etkl import celltype
    g = celltype.grid_evidence(CELLS, 2, body_starts_at=4)
    assert (_band_node(g), TAB.bodyStartsAt, Literal(4, datatype=XSD.integer)) in g


def test_the_cells_are_unchanged_by_the_new_parameter():
    """The parameter adds evidence; it must not filter or renumber cells."""
    from iladub.etkl import celltype
    a = celltype.grid_evidence(CELLS, 2)
    b = celltype.grid_evidence(CELLS, 2, body_starts_at=4)
    cells_a = set(a.subject_objects(TAB.gridText))
    cells_b = set(b.subject_objects(TAB.gridText))
    assert cells_a == cells_b, "cell evidence must be identical regardless of body_starts_at"


def test_the_term_is_declared_in_the_ontology():
    import os
    from rdflib import Graph
    from rdflib.namespace import RDFS
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    g = Graph().parse(os.path.join(root, "vocab", "ontology", "tab.ttl"), format="turtle")
    assert (TAB.bodyStartsAt, RDFS.domain, TAB.ClassifyBand) in g
    assert (TAB.bodyStartsAt, RDFS.range, XSD.integer) in g
