"""The membrane seam: one place any SHACL runs (spec 2026-08-06-membrane-engine-swap-design.md).

Task 1 establishes the seam over pySHACL with NO behaviour change; later tasks swap the
engine underneath it. The point of the seam is that `tiling.region_tiles` and
`compile._validate` stop constructing their own pyshacl.validate calls."""
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES = os.path.join(ROOT, "vocab", "shapes")
ONT = os.path.join(ROOT, "vocab", "ontology")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT, "tab.ttl"), format="turtle")


def test_membrane_reports_conformance_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    cell = URIRef("urn:m:cell")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is True, report
    assert isinstance(report, str)


def test_membrane_catches_a_core_violation():
    # UnitMarkerShape: a tab:UnitMarker needs >=1 tab:markerRegion.
    from iladub.etkl import membrane
    g = Graph()
    um = URIRef("urn:m:um")
    g.add((um, RDF.type, TAB.UnitMarker))
    g.add((um, TAB.markerSymbol, Literal("$")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "markerRegion" in report or "UnitMarkerShape" in report


def test_membrane_catches_a_sparql_constraint_violation():
    # WrappedCellShape (sh:sparql): a bbox-carrying tab:Cell needs non-empty cellText.
    from iladub.etkl import membrane
    g = Graph()
    cell, bb = URIRef("urn:m:c"), URIRef("urn:m:bb")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((cell, TAB.hasBBox, bb))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "cellText" in report or "WrappedCellShape" in report


def test_membrane_applies_rdfs_inference():
    """The R19 mechanism: a node typed tab:Cell ONLY via tab:hasBBox's rdfs:domain must
    still be validated. This pins that the seam preserves inference="rdfs" semantics."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:m:inf"), URIRef("urn:m:infbb")
    g.add((node, TAB.hasBBox, bb))          # NO explicit rdf:type
    g.add((bb, RDF.type, TAB.BBox))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False, "inference must type the node as tab:Cell and fire WrappedCellShape"


def test_engine_name_is_reported():
    from iladub.etkl import membrane
    assert membrane.engine_name() in ("pyshacl", "rudof")


def test_call_sites_use_the_seam():
    """Structural pin: neither call site may construct its own pyshacl.validate."""
    import inspect
    from iladub.etkl import tiling
    import iladub.etkl.compile as C
    assert "membrane" in inspect.getsource(tiling.region_tiles)
    assert "membrane" in inspect.getsource(C._validate)


# ---------------------------------------------------------------- closure

def test_rdfs_closure_materializes_subclass_and_domain_types():
    """Closure must reproduce what inference='rdfs' gives pySHACL today: subclass closure
    (EntryCell -> Cell, which sh:targetClass needs) AND domain typing (the R19 mechanism)."""
    from iladub.etkl import membrane
    g = Graph()
    ec, node, bb = URIRef("urn:c:ec"), URIRef("urn:c:n"), URIRef("urn:c:bb")
    g.add((ec, RDF.type, TAB.EntryCell))     # subclass of tab:Cell in tab.ttl
    g.add((node, TAB.hasBBox, bb))           # rdfs:domain tab:Cell
    out = membrane.rdfs_closure(g, _ont())
    assert (ec, RDF.type, TAB.Cell) in out, "subclass closure missing"
    assert (node, RDF.type, TAB.Cell) in out, "domain typing missing (R19 mechanism)"


def test_rdfs_closure_drops_literal_subject_triples():
    """owlrl emits `"307.47"^^xsd:decimal rdf:type rdfs:Resource` — illegal RDF that rdflib
    tolerates and a strict parser refuses. The closure must remove every such triple."""
    from iladub.etkl import membrane
    from rdflib.namespace import XSD
    g = Graph()
    c = URIRef("urn:c:cell")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.x0, Literal("307.47", datatype=XSD.decimal)))
    out = membrane.rdfs_closure(g, _ont())
    bad = [s for s in out.subjects() if isinstance(s, Literal)]
    assert bad == [], f"literal-subject triples survived: {bad[:3]}"


def test_rdfs_closure_does_not_mutate_its_input():
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:c:x"), RDF.type, TAB.EntryCell))
    before = len(g)
    membrane.rdfs_closure(g, _ont())
    assert len(g) == before, "rdfs_closure must return a NEW graph"


def test_rdfs_closure_injects_only_ontology_axioms():
    """rdfs_closure must mix the ontology in the way pySHACL's inoculate() does: only
    RDFS/OWL axioms cross into the merged graph, not arbitrary triples the ontology graph
    happens to carry. A full graph union would leak the latter into what rudof sees, making
    the Task 4 engine differential compare two different graphs, not two engines."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    sub, sup, thing = URIRef("urn:o:Sub"), URIRef("urn:o:Super"), URIRef("urn:o:thing")
    ont.add((sub, RDFS.subClassOf, sup))                              # a real RDFS axiom
    ont.add((thing, URIRef("urn:o:randomPredicate"), Literal("x")))   # NOT an axiom
    data = Graph()
    data.add((URIRef("urn:c:d"), RDF.type, sub))
    out = membrane.rdfs_closure(data, ont)
    assert (URIRef("urn:c:d"), RDF.type, sup) in out, "axiom's subclass closure missing"
    assert (thing, URIRef("urn:o:randomPredicate"), Literal("x")) not in out, \
        "non-axiom ontology triple leaked through — full union, not inoculate()"


# ---------------------------------------------------------------- rudof engine

import pytest

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


@needs_rudof
def test_rudof_engine_agrees_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    c = URIRef("urn:r:c")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("Americas")))
    ok_p, _ = membrane._validate_pyshacl(g, _shapes(), _ont())
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_p == ok_r is True


@needs_rudof
def test_rudof_engine_catches_a_sparql_constraint_violation():
    from iladub.etkl import membrane
    g = Graph()
    c, bb = URIRef("urn:r:c2"), URIRef("urn:r:bb2")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((c, TAB.hasBBox, bb))
    ok_r, report = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is False
    assert "cellText" in report or "WrappedCellShape" in report


@needs_rudof
def test_rudof_engine_sees_inferred_types():
    """rudof does NO inference of its own — this passes only because the seam runs
    rdfs_closure first. Pins the R19 mechanism end to end on the new engine."""
    from iladub.etkl import membrane
    g = Graph()
    n, bb = URIRef("urn:r:inf"), URIRef("urn:r:infbb")
    g.add((n, TAB.hasBBox, bb))
    g.add((bb, RDF.type, TAB.BBox))
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is False


@needs_rudof
def test_engine_switch_selects_rudof(monkeypatch):
    from iladub.etkl import membrane
    monkeypatch.setenv("ILADUB_MEMBRANE", "rudof")
    assert membrane.engine_name() == "rudof"
    monkeypatch.setenv("ILADUB_MEMBRANE", "pyshacl")
    assert membrane.engine_name() == "pyshacl"
