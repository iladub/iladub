# tests/etkl/test_recipe_vocab.py
from rdflib import Graph, Namespace, RDFS
from pathlib import Path

TAB = Namespace("https://w3id.org/iladub/tab#")
HPROJ = Namespace("http://w3id.org/holon/projection/")
VOCAB = Path(__file__).resolve().parents[2] / "vocab" / "ontology"


def _g(*names):
    g = Graph()
    for n in names:
        g.parse(VOCAB / n, format="turtle")
    return g


def test_recipe_terms_present_and_standalone():
    g = _g("tab.ttl")                       # core must parse standalone
    for c in ["ReshapeRecipe", "ReshapeOperation", "UnpivotOp",
              "StripAggregationOp", "NormalizedBase"]:
        assert (TAB[c], None, None) in g, c
    assert (TAB.UnpivotOp, RDFS.subClassOf, TAB.ReshapeOperation) in g
    assert (TAB.StripAggregationOp, RDFS.subClassOf, TAB.ReshapeOperation) in g
    # standalone core: no HGA / FnO leakage
    assert "w3id.org/holon" not in g.serialize(format="turtle")
    assert "xpath-functions" not in g.serialize(format="turtle")


def test_hga_alignment_projection():
    g = _g("tab.ttl", "tab-hga-align.ttl")
    assert (TAB.NormalizedBase, RDFS.subClassOf, HPROJ.Projection) in g


def test_fno_alignment_maps_sum():
    g = _g("tab.ttl", "tab-fno-align.ttl")
    fn_sum = "http://www.w3.org/2005/xpath-functions#sum"
    assert fn_sum in g.serialize(format="turtle")
