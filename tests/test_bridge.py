import os
from rdflib import Graph
from iladub.bridge import generate_baml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
GENERATED = os.path.join(ROOT, "baml_src", "generated_types.baml")


def _baml():
    contract = Graph().parse(os.path.join(TXD, "offer-contract.ttl"), format="turtle")
    terms = Graph().parse(os.path.join(TXD, "transplant-terms.ttl"), format="turtle")
    return generate_baml(contract, terms)


def test_emits_codedconcept_and_agent_classes():
    out = _baml()
    assert "class CodedConcept" in out
    assert "class DonorClinical" in out
    assert "class Immunology" in out
    assert "class Logistics" in out


def test_abo_field_uses_generated_enum_of_admissible_values():
    out = _baml()
    assert "enum AboGroup" in out
    for v in ("O", "A", "B", "AB"):
        assert v in out


def test_generated_file_is_in_sync_with_ontology():
    with open(GENERATED, encoding="utf-8") as fh:
        committed = fh.read()
    assert committed == _baml(), "baml_src/generated_types.baml is stale; regenerate it"
