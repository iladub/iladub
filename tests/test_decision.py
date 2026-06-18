import os

from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from iladub.decision import evaluate_m4, build_decision_holon, M4Context
from iladub.validate import validate

HOL = Namespace("https://w3id.org/etkl/hol#")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_accept_when_compatible_and_in_window():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    result = evaluate_m4(ctx)
    assert result.recommendation == "accept"
    assert result.rejected_option == "decline"


def test_decline_when_window_exceeded_records_reason():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=270, ischemia_limit_minutes=240)
    result = evaluate_m4(ctx)
    assert result.recommendation == "decline"
    assert "270" in result.reason and "240" in result.reason


def test_decision_holon_is_a_hol_decision_holon():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx))
    holons = list(g.subjects(RDF.type, HOL.DecisionHolon))
    assert len(holons) == 1


def test_decision_holon_has_two_options_and_one_chosen():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx))
    options = list(g.subjects(RDF.type, HOL.Option))
    chosen = list(g.objects(None, HOL.chosen))
    assert len(options) == 2
    assert len(chosen) == 1
    assert chosen[0] in options


def test_decision_holon_conforms_to_hol_shapes():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx))
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    result = validate(g, shapes, knowledge)
    assert result.conforms, result.report_text


def test_decision_holon_conforms_when_wired_to_process():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx), process=HOL["heart-process"])
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    result = validate(g, shapes, knowledge)
    assert result.conforms, result.report_text
