"""The route vocabulary, its alignment and its membrane (document-router plan, Task 2).

One worked example that conforms and one negative per shape S1..S5, each of which must fail
with that shape's own message.
"""
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

REPO = Path(__file__).resolve().parent.parent
ONT = REPO / "vocab" / "ontology"
SHAPES = [REPO / "vocab" / "shapes" / "route-shapes.ttl", REPO / "vocab" / "shapes" / "dec-shapes.ttl"]
EXAMPLE = REPO / "examples" / "router" / "route-example.ttl"

MESSAGES = {
    "s1": "must record who decided",
    "s2": "model identifier",
    "s3": "refusal",
    "s4": "contract document needs",
    "s5": "not a contract",
}


def _run(data_path: Path):
    data = Graph().parse(data_path, format="turtle")
    data.parse(ONT / "route.ttl", format="turtle")
    data.parse(ONT / "dec.ttl", format="turtle")
    shapes = Graph()
    for p in SHAPES:
        shapes.parse(p, format="turtle")
    conforms, _, text = validate(data, shacl_graph=shapes, inference="rdfs", advanced=True)
    return conforms, text


def test_example_conforms():
    conforms, text = _run(EXAMPLE)
    assert conforms, text


@pytest.mark.parametrize("shape", sorted(MESSAGES))
def test_negative_fails(shape):
    conforms, text = _run(REPO / "tests" / f"route-negative-{shape}.ttl")
    assert not conforms
    assert MESSAGES[shape] in text.lower(), text


def test_core_module_is_standalone():
    text = (ONT / "route.ttl").read_text()
    for needle in ("w3id.org/holon", "semanticarts", "edmcouncil"):
        assert needle not in text


def test_fibo_alignment_target():
    g = Graph().parse(ONT / "route-align.ttl", format="turtle")
    from rdflib import URIRef
    from rdflib.namespace import RDFS
    R = "https://w3id.org/iladub/route#"
    fibo = URIRef("https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/ContractDocument")
    gist = URIRef("https://w3id.org/semanticarts/ns/ontology/gist/Content")
    assert (URIRef(R + "ContractDocument"), RDFS.subClassOf, fibo) in g
    assert (URIRef(R + "Document"), RDFS.subClassOf, gist) in g
