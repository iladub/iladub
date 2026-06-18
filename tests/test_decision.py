from rdflib import Namespace
from rdflib.namespace import RDF
from iladub.decision import evaluate_m4, build_decision_holon, M4Context

HOL = Namespace("https://w3id.org/etkl/hol#")


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
