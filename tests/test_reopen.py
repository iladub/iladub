from rdflib import Namespace
from iladub.decision import M4Context, evaluate_m4, build_decision_holon
from iladub.events import Event
from iladub.reopen import revisit_conditions, should_reopen

HOL = Namespace("https://w3id.org/etkl/hol#")
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
