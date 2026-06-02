"""End-to-end test of the reference ET(K)L pipeline on a synthetic admission note."""
import os

from rdflib import Namespace
from rdflib.namespace import RDF

from iladub.contract import SemanticDataContract
from iladub.pipeline import Pipeline

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXM = os.path.join(ROOT, "examples")
EX = Namespace("https://example.org/demo#")
SUBJECT = EX["extracted-resource"]


def _contract():
    return SemanticDataContract.from_files(
        os.path.join(EXM, "patient-contract.ttl"),
        os.path.join(EXM, "patient-shapes.ttl"),
        os.path.join(EXM, "patient-knowledge.ttl"),
    )


def test_pipeline_runs_and_conforms():
    graph, result = Pipeline(_contract()).run(os.path.join(EXM, "sample-admission.txt"))
    assert result.conforms, result.report_text
    names = [str(o) for o in graph.objects(SUBJECT, EX["name"])]
    assert any("Erika" in n for n in names), names


def test_pipeline_types_the_target_class():
    graph, _ = Pipeline(_contract()).run(os.path.join(EXM, "sample-admission.txt"))
    assert (SUBJECT, RDF.type, EX["Patient"]) in graph


def test_pipeline_extracts_all_declared_fields():
    graph, _ = Pipeline(_contract()).run(os.path.join(EXM, "sample-admission.txt"))
    assert str(graph.value(SUBJECT, EX["mrn"])) == "CH-4471"
    assert str(graph.value(SUBJECT, EX["birthDate"])) == "1958-03-22"
