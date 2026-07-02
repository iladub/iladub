"""Runs the Swiss FHIR demo end-to-end and checks the assembled graph.

Light validation (per design): assert the demo runs and produces a connected
FHIR graph with the expected resources and the decision holon over it.
"""
import os
import subprocess
import sys

from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "demo")
OUT = os.path.join(DEMO, "out", "consultation-fhir.ttl")

FHIR = Namespace("http://hl7.org/fhir/")
DEC = Namespace("https://w3id.org/iladub/dec#")
EX = Namespace("https://example.org/clinical#")


def _run_demo():
    r = subprocess.run([sys.executable, os.path.join(DEMO, "assemble_fhir.py")],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    g = Graph().parse(OUT, format="turtle")
    return g


def test_demo_assembles_expected_fhir_resources():
    g = _run_demo()
    for cls in (FHIR.Patient, FHIR.Practitioner, FHIR.Encounter, FHIR.Composition,
                FHIR.Condition, FHIR.Observation, FHIR.MedicationRequest):
        assert (None, RDF.type, cls) in g, f"missing {cls}"


def test_demo_attaches_decision_holon():
    g = _run_demo()
    dh = EX["decision-switch-insulin"]
    assert (dh, RDF.type, DEC.DecisionHolon) in g
    # the chosen option must be the insulin switch, and it must be in the option space
    assert (dh, DEC.chosen, EX["opt-switch-insulin"]) in g
    assert (dh, DEC.optionSpace, EX["opt-switch-insulin"]) in g
    assert (dh, DEC.optionSpace, EX["opt-keep-metformin"]) in g
    # the decision produced the insulin MedicationRequest
    assert (dh, DEC.produced, None) in g


def test_demo_only_emits_supported_resources():
    g = _run_demo()
    # the report supports a renal condition; the insulin request cites it as reason
    reqs = list(g.subjects(RDF.type, FHIR.MedicationRequest))
    assert reqs, "expected a MedicationRequest"
    assert any((r, FHIR["MedicationRequest.reasonReference"], None) in g for r in reqs)
