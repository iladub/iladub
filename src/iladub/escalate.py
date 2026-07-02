"""Apex escalation: when a decision realizes a severity beyond its declared autonomy
scope, it cannot resolve the matter locally — it escalates to a binding higher-authority
(apex) decision. The vertical (authority-holarchy) analog of reopen.py's temporal lineage.
Standalone: evaluate_m4 and the M4 pipeline are untouched."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

DEC = Namespace("https://w3id.org/iladub/dec#")
RISK = Namespace("https://w3id.org/iladub/risk#")
TX = Namespace("https://example.org/transplant#")

# Mirrors risk:order in risk.ttl (kept honest by test_severity_order_mirrors_risk_ttl).
_SEVERITY_ORDER = {"ok": 0, "watch": 1, "breach": 2, "critical": 3}
_SEVERITY_IRI = {"ok": RISK.Ok, "watch": RISK.Watch, "breach": RISK.Breach,
                 "critical": RISK.Critical}


def requires_escalation(realized: str, scope_ceiling: str) -> bool:
    """True when a realized severity exceeds the autonomy scope's ceiling."""
    return _SEVERITY_ORDER[realized] > _SEVERITY_ORDER[scope_ceiling]


@dataclass
class EscalationOutcome:
    apex_subject: URIRef
    chosen: URIRef
    graph: Graph


def escalate(local_subject: URIRef, realized_severity: str, *,
             new_subject: URIRef, scope: URIRef,
             agent: URIRef = TX["role-board"],
             event_subject: URIRef = TX["constitutional-event"],
             condition: str = "absoluteContraindication",
             override: bool = False) -> EscalationOutcome:
    """Build the binding apex dec:DecisionHolon and wire authority-holarchy lineage.

    The apex option space is {confirm-decline, override}; chosen = confirm-decline by default
    (override=True selects override, with the other rejectedBecause). The apex decision is
    constrainedBy the realized severity, triggeredBy a constitutional dec:Event, decidedBy the
    board agent, and withinScope `scope`; local_subject dec:escalatedTo new_subject.
    """
    g = Graph()
    confirm = URIRef(str(new_subject) + "-opt-confirm-decline")
    over = URIRef(str(new_subject) + "-opt-override")
    g.add((new_subject, RDF.type, DEC.DecisionHolon))
    g.add((confirm, RDF.type, DEC.Option))
    g.add((over, RDF.type, DEC.Option))
    g.add((new_subject, DEC.optionSpace, confirm))
    g.add((new_subject, DEC.optionSpace, over))

    chosen = over if override else confirm
    rejected = confirm if override else over
    rejected_reason = ("decline overridden by board judgment" if override
                       else "override rejected: a constitutional contraindication is absolute")
    g.add((new_subject, DEC.chosen, chosen))
    g.add((rejected, DEC.rejectedBecause, Literal(rejected_reason)))
    g.add((new_subject, DEC.decidedBy, agent))
    g.add((new_subject, DEC.rationale,
           Literal(f"constitutional matter ({condition}) escalated to the board apex")))
    g.add((new_subject, DEC.constrainedBy, _SEVERITY_IRI[realized_severity]))
    g.add((new_subject, DEC.withinScope, scope))

    g.add((event_subject, RDF.type, DEC.Event))
    g.add((event_subject, DEC.condition, Literal(condition)))
    g.add((new_subject, DEC.triggeredBy, event_subject))

    g.add((local_subject, DEC.escalatedTo, new_subject))
    return EscalationOutcome(apex_subject=new_subject, chosen=chosen, graph=g)
