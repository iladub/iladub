from rdflib import Namespace
from iladub.decision import M4Context, evaluate_m4, build_decision_holon
from iladub.events import Event
from iladub.reopen import revisit_conditions, should_reopen

DEC = Namespace("https://w3id.org/iladub/dec#")
TX = Namespace("https://example.org/transplant#")


def _prior_decision_graph():
    res = evaluate_m4(M4Context("O", "O", 95, 240))   # accept
    return build_decision_holon(res, subject=TX["m4-decision"],
                                revisit_if=("ischemiaExceeded",))


def test_revisit_conditions_reads_declared_keys():
    g = _prior_decision_graph()
    assert revisit_conditions(g, TX["m4-decision"]) == {"ischemiaExceeded"}


def test_should_reopen_true_on_matching_event():
    g = _prior_decision_graph()
    assert should_reopen(g, TX["m4-decision"], Event("ischemiaExceeded", {})) is True


def test_should_reopen_false_on_unknown_event():
    g = _prior_decision_graph()
    assert should_reopen(g, TX["m4-decision"], Event("weatherAlert", {})) is False


import os
from rdflib import Graph
from rdflib.namespace import RDF
from iladub.reopen import reopen
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _re_evaluate(event):
    # Fold the event payload into a fresh decision input.
    return evaluate_m4(M4Context("O", "O", event.payload["projected_ischemia_minutes"], 240))


def test_reopen_flips_to_decline_with_lineage():
    event = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    outcome = reopen(TX["m4-decision"], event, _re_evaluate, new_subject=TX["m4-decision-2"])
    assert outcome.result.recommendation == "decline"
    assert (TX["m4-decision-2"], DEC.supersedes, TX["m4-decision"]) in outcome.graph
    assert (TX["m4-decision-2"], DEC.triggeredBy, TX["event-1"]) in outcome.graph
    merged = _prior_decision_graph() + outcome.graph
    assert len(set(merged.subjects(RDF.type, DEC.DecisionHolon))) == 2


def test_reopened_lineage_conforms_to_hol_shapes():
    event = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    outcome = reopen(TX["m4-decision"], event, _re_evaluate, new_subject=TX["m4-decision-2"])
    # Validate the MERGED graph: supersedes/triggeredBy ranges (DecisionHolon/Event) mean the
    # prior decision must be fully present, not just referenced, to conform under rdfs inference.
    merged = _prior_decision_graph() + outcome.graph
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")
    result = validate(merged, shapes, knowledge)
    assert result.conforms, result.report_text
