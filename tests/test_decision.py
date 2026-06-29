import os

from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from iladub.decision import evaluate_m4, build_decision_holon, M4Context
from iladub.validate import validate

HOL = Namespace("https://w3id.org/etkl/hol#")
RISK = Namespace("https://w3id.org/etkl/risk#")
TX = Namespace("https://example.org/transplant#")

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


def test_decision_holon_emits_revisit_if_keys():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240)
    g = build_decision_holon(evaluate_m4(ctx), revisit_if=("ischemiaExceeded", "donorDeterioration"))
    keys = {str(o) for o in g.objects(None, HOL.revisitIf)}
    assert keys == {"ischemiaExceeded", "donorDeterioration"}


# --- contextual organ risk: same organ, different recipient context → different decision ---

def test_marginal_organ_declined_for_low_tolerance_recipient():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240,
                    organ_lvef=38, recipient_lvef_floor=45)   # stable recipient, low tolerance
    r = evaluate_m4(ctx)
    assert r.recommendation == "decline"
    assert r.risk_severity == "breach"
    assert "38" in r.reason


def test_same_organ_accepted_for_high_tolerance_recipient():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240,
                    organ_lvef=38, recipient_lvef_floor=30)   # critical recipient, high tolerance
    r = evaluate_m4(ctx)
    assert r.recommendation == "accept"      # SAME organ, ABO, ischemia — context flips the decision
    assert r.risk_severity == "ok"


def test_absolute_contraindication_declines_regardless():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240,
                    absolute_contraindication=True)
    r = evaluate_m4(ctx)
    assert r.recommendation == "decline"
    assert r.risk_severity == "critical"


def test_risk_decline_records_constraint_and_conforms():
    ctx = M4Context(donor_abo="O", recipient_abo="O",
                    projected_ischemia_minutes=95, ischemia_limit_minutes=240,
                    organ_lvef=38, recipient_lvef_floor=45)
    g = build_decision_holon(evaluate_m4(ctx))
    assert (TX["m4-decision"], HOL.constrainedBy, RISK["Breach"]) in g
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    assert validate(g, shapes, knowledge).conforms
