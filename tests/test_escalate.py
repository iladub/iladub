import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from iladub.decision import M4Context, evaluate_m4, build_decision_holon
from iladub.escalate import requires_escalation, escalate, _SEVERITY_ORDER
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")

DEC = Namespace("https://w3id.org/iladub/dec#")
RISK = Namespace("https://w3id.org/iladub/risk#")
TX = Namespace("https://example.org/transplant#")


def test_requires_escalation_compares_ordinals():
    assert requires_escalation("critical", "breach") is True
    assert requires_escalation("breach", "breach") is False
    assert requires_escalation("breach", "critical") is False


def test_severity_order_mirrors_risk_ttl():
    g = Graph().parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    from_ttl = {}
    for sev, order in g.subject_objects(RISK.order):
        label = str(g.value(sev, Namespace("http://www.w3.org/2000/01/rdf-schema#").label))
        from_ttl[label] = int(order)
    assert from_ttl == _SEVERITY_ORDER


def test_escalate_emits_lineage_and_apex_decision():
    out = escalate(TX["m4-decision"], "critical",
                   new_subject=TX["board-decision"], scope=TX["scope-board"])
    g = out.graph
    assert (TX["m4-decision"], DEC.escalatedTo, TX["board-decision"]) in g
    assert (TX["board-decision"], RDF.type, DEC.DecisionHolon) in g
    assert (TX["board-decision"], DEC.constrainedBy, RISK.Critical) in g
    assert (TX["board-decision"], DEC.withinScope, TX["scope-board"]) in g
    assert len(list(g.objects(TX["board-decision"], DEC.triggeredBy))) == 1
    assert out.apex_subject == TX["board-decision"]
    assert len(list(g.objects(TX["board-decision"], DEC.optionSpace))) == 2
    assert len(list(g.objects(TX["board-decision"], DEC.chosen))) == 1


def test_escalate_override_flips_chosen():
    confirm = escalate(TX["d"], "critical", new_subject=TX["b1"], scope=TX["s"]).chosen
    override = escalate(TX["d"], "critical", new_subject=TX["b2"], scope=TX["s"],
                        override=True).chosen
    assert confirm != override


def test_escalated_graph_conforms():
    # Local decision (declines under a constitutional Critical) + a Breach-ceiling scope.
    local = build_decision_holon(evaluate_m4(M4Context("O", "O", 95, 240,
                                 absolute_contraindication=True)),
                                 subject=TX["m4-decision"])
    local.add((TX["m4-decision"], DEC.withinScope, TX["scope-recipient"]))
    local.add((TX["scope-recipient"], DEC.maxSeverity, RISK.Breach))
    out = escalate(TX["m4-decision"], "critical",
                   new_subject=TX["board-decision"], scope=TX["scope-board"])
    data = local + out.graph
    data.add((TX["scope-board"], DEC.maxSeverity, RISK.Critical))
    data.parse(os.path.join(ONT, "risk.ttl"), format="turtle")  # risk:order for the SPARQL

    shapes = Graph()
    shapes.parse(os.path.join(SH, "dec-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ONT, "dec.ttl"), format="turtle")
    res = validate(data, shapes, knowledge)
    assert res.conforms, res.report_text
