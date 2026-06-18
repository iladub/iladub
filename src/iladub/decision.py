"""Deterministic M4 accept/decline evaluation on clean concepts, recorded as a
hol:DecisionHolon. This is 'logic application on clean concepts' — the funnel
produced the validated context; here we decide and account for it."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

HOL = Namespace("https://w3id.org/etkl/hol#")
PROV = Namespace("http://www.w3.org/ns/prov#")
TX = Namespace("https://example.org/transplant#")

# ABO donor->recipient compatibility (simplified, synthetic).
_ABO_OK = {
    ("O", "O"), ("O", "A"), ("O", "B"), ("O", "AB"),
    ("A", "A"), ("A", "AB"),
    ("B", "B"), ("B", "AB"),
    ("AB", "AB"),
}


@dataclass
class M4Context:
    donor_abo: str
    recipient_abo: str
    projected_ischemia_minutes: int
    ischemia_limit_minutes: int


@dataclass
class DecisionResult:
    recommendation: str   # "accept" | "decline"
    rejected_option: str  # the option not taken
    reason: str
    abo_compatible: bool
    ischemia_feasible: bool


def evaluate_m4(ctx: M4Context) -> DecisionResult:
    abo_ok = (ctx.donor_abo, ctx.recipient_abo) in _ABO_OK
    feasible = ctx.projected_ischemia_minutes <= ctx.ischemia_limit_minutes
    if abo_ok and feasible:
        return DecisionResult("accept", "decline",
                              "ABO compatible and within cold-ischemia window.",
                              abo_ok, feasible)
    if not feasible:
        reason = (f"projected ischemia {ctx.projected_ischemia_minutes} min "
                  f"> limit {ctx.ischemia_limit_minutes} min")
    else:
        reason = f"ABO incompatible: donor {ctx.donor_abo} -> recipient {ctx.recipient_abo}"
    return DecisionResult("decline", "accept", reason, abo_ok, feasible)


def build_decision_holon(result: DecisionResult,
                         subject: URIRef = TX["m4-decision"],
                         process: URIRef | None = None,
                         agent: URIRef = TX["surgeon-1"],
                         evidence: tuple[URIRef, ...] = (),
                         revisit_if: tuple[str, ...] = ()) -> Graph:
    """Emit the decision as a hol:DecisionHolon that conforms to hol:DecisionHolonShape:
    a deliberated option space (accept + decline), exactly one chosen option, an
    accountable agent, the rejected option's reason, and (optionally) its place in a
    process holarchy."""
    g = Graph()
    accept, decline = TX["opt-accept"], TX["opt-decline"]
    g.add((subject, RDF.type, HOL.DecisionHolon))
    g.add((accept, RDF.type, HOL.Option))
    g.add((decline, RDF.type, HOL.Option))
    g.add((subject, HOL.optionSpace, accept))
    g.add((subject, HOL.optionSpace, decline))

    chosen = accept if result.recommendation == "accept" else decline
    rejected = decline if result.recommendation == "accept" else accept
    g.add((subject, HOL.chosen, chosen))
    g.add((rejected, HOL.rejectedBecause, Literal(result.reason)))
    g.add((subject, HOL.decidedBy, agent))
    g.add((subject, HOL.rationale, Literal(result.reason)))
    for e in evidence:
        g.add((subject, HOL.consideredEvidence, e))
    if process is not None:
        g.add((subject, HOL.withinProcess, process))
    for key in revisit_if:
        g.add((subject, HOL.revisitIf, Literal(key)))
    return g
