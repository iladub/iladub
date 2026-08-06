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
