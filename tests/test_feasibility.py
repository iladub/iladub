"""Feasible-recipient search — the maritime feasible-destination engine, recast for transplant.

Worked example: a heart (240-min cold-ischemia window, O blood group) offered to several
candidate centres. Which can it reach in time and admissibly? The feasible set is the
"for-orders" candidate cloud; per-recipient organ risk then decides the nomination.
"""
import os
import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from iladub.feasibility import Organ, Candidate, feasible_recipients, nominate
from iladub.decision import M4Context, evaluate_m4
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def _hol_conforms(g):
    shapes = Graph().parse(os.path.join(ROOT, "vocab", "shapes", "hol-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")
    return validate(g, shapes, knowledge).conforms


def _heart():
    return Organ(abo="O", ischemia_limit_minutes=240)


def test_feasible_set_under_window_and_abo():
    feas, infeas = feasible_recipients(_heart(), [
        Candidate("zurich", abo="O", transport_minutes=95),     # reachable
        Candidate("paris",  abo="A", transport_minutes=120),    # reachable + ABO ok (O->A)
        Candidate("tokyo",  abo="O", transport_minutes=600),    # too far
        Candidate("madrid", abo="AB", transport_minutes=80, ready=False),  # not ready
    ])
    names = {f.recipient for f in feas}
    assert names == {"zurich", "paris"}
    reasons = {i.recipient: i.reason for i in infeas}
    assert "window" in reasons["tokyo"]
    assert "not ready" in reasons["madrid"]


def test_abo_incompatible_is_infeasible_with_reason():
    feas, infeas = feasible_recipients(
        Organ(abo="A", ischemia_limit_minutes=240),
        [Candidate("recipient-o", abo="O", transport_minutes=60)],   # A donor -> O recipient: incompatible
    )
    assert feas == []
    assert "ABO incompatible" in infeas[0].reason


def test_feasible_recipients_ranked_by_slack():
    feas, _ = feasible_recipients(_heart(), [
        Candidate("far",  abo="O", transport_minutes=200),   # slack 40
        Candidate("near", abo="O", transport_minutes=60),    # slack 180
    ])
    assert [f.recipient for f in feas] == ["near", "far"]    # most slack first
    assert feas[0].slack_minutes == 180


def test_elapsed_time_shrinks_the_window():
    # 100 min already on the clock: a 160-min transport no longer fits a 240-min window.
    feas, infeas = feasible_recipients(
        Organ(abo="O", ischemia_limit_minutes=240, elapsed_minutes=100),
        [Candidate("centre", abo="O", transport_minutes=160)],
    )
    assert feas == []
    assert "window" in infeas[0].reason


def test_candidate_cloud_then_risk_aware_nomination():
    """The feasible set (candidate cloud) → per-recipient risk-aware decision (#2):
    the SAME marginal organ (LVEF 38) is declined for a low-tolerance centre and
    accepted for a high-tolerance one."""
    feas, _ = feasible_recipients(_heart(), [
        Candidate("stable-centre",   abo="O", transport_minutes=90),
        Candidate("critical-centre", abo="O", transport_minutes=110),
    ])
    floors = {"stable-centre": 45, "critical-centre": 30}   # each centre's risk tolerance
    decisions = {}
    for f in feas:
        ctx = M4Context(donor_abo="O", recipient_abo="O",
                        projected_ischemia_minutes=f.transport_minutes, ischemia_limit_minutes=240,
                        organ_lvef=38, recipient_lvef_floor=floors[f.recipient])
        decisions[f.recipient] = evaluate_m4(ctx).recommendation
    assert decisions == {"stable-centre": "decline", "critical-centre": "accept"}


# --- nomination: the candidate cloud → an accountable decision that grounds one ---

def test_nominate_grounds_chosen_recipient_and_conforms():
    feas, _ = feasible_recipients(_heart(), [
        Candidate("zurich", abo="O", transport_minutes=95),
        Candidate("paris",  abo="A", transport_minutes=120),
    ])
    g = nominate(feas, chosen="zurich", agent="surgeon-1",
                 rationale="most slack and best clinical fit")
    assert (TX["nomination"], RDF.type, HOL.DecisionHolon) in g
    assert (TX["nomination"], HOL.chosen, TX["recipient-zurich"]) in g
    assert (TX["nomination"], HOL.produced, TX["recipient-zurich"]) in g   # the grounded destination
    assert (TX["recipient-paris"], HOL.rejectedBecause, None) in g
    assert _hol_conforms(g)


def test_nominate_can_decline_all():
    feas, _ = feasible_recipients(_heart(), [Candidate("zurich", abo="O", transport_minutes=95)])
    g = nominate(feas, chosen="nobody", agent="surgeon-1",
                 rationale="hold for a better-matched organ")
    assert (TX["nomination"], HOL.chosen, TX["opt-no-allocation"]) in g
    assert len(list(g.triples((None, HOL.produced, None)))) == 0          # nothing grounded
    assert (TX["recipient-zurich"], HOL.rejectedBecause, None) in g
    assert _hol_conforms(g)


def test_nominate_requires_a_feasible_recipient():
    with pytest.raises(ValueError):
        nominate([], chosen="x", agent="surgeon-1", rationale="—")
