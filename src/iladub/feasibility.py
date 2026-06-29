"""Feasible-recipient search — the maritime feasible-destination engine, recast for
transplant.

Maritime asks: from here, with this fuel/time budget, which ports can the vessel reach
(under draught/chokepoint admissibility)? Transplant asks the same shape: with this
cold-ischemia budget, which candidate recipients can the organ reach in time, and are
they admissible (ABO-compatible, ready)? The feasible set is a candidate cloud — the
"for-orders" analog: an organ offered to several centres before one is nominated. Nominating
one is a promotion (the M4 decision, ``decision.evaluate_m4``); per-recipient organ risk
(``decision._organ_risk``) is then the downstream filter.

Reuses the same primitives as the rest of the engine: ``allen.feasible`` for the
window/transport interval check and ``decision._ABO_OK`` for compatibility — same engine,
retargeted. Infeasible candidates are returned *with reasons* (explainable, not a black box).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from rdflib import Graph, Literal, Namespace

from rdflib.namespace import RDF

from .allen import Interval, feasible
from .decision import _ABO_OK

HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


@dataclass
class Organ:
    abo: str
    ischemia_limit_minutes: int        # the cold-ischemia window for this organ class
    elapsed_minutes: int = 0           # time already on the clock (since cross-clamp)


@dataclass
class Candidate:
    recipient: str                     # recipient/centre id or IRI
    abo: str
    transport_minutes: int             # door-to-door transport time to this centre
    ready: bool = True                 # centre/recipient admitted and ready


@dataclass
class FeasibleRecipient:
    recipient: str
    transport_minutes: int
    slack_minutes: int                 # remaining window after arrival (window.end - arrival)


@dataclass
class Infeasible:
    recipient: str
    reason: str


def feasible_recipients(organ: Organ,
                        candidates: List[Candidate]
                        ) -> Tuple[List[FeasibleRecipient], List[Infeasible]]:
    """Partition ``candidates`` into those the organ can reach in time and admissibly,
    and those it cannot (each with a reason). Feasible recipients are ranked by slack
    (most remaining window first) — illustrative; real allocation priority is policy-driven."""
    window = Interval(organ.elapsed_minutes, organ.ischemia_limit_minutes)
    feas: List[FeasibleRecipient] = []
    infeas: List[Infeasible] = []
    for c in candidates:
        if not c.ready:
            infeas.append(Infeasible(c.recipient, "recipient/centre not ready"))
            continue
        if (organ.abo, c.abo) not in _ABO_OK:
            infeas.append(Infeasible(c.recipient,
                                     f"ABO incompatible: donor {organ.abo} -> recipient {c.abo}"))
            continue
        transport = Interval(organ.elapsed_minutes, organ.elapsed_minutes + c.transport_minutes)
        if not feasible(window, transport):
            infeas.append(Infeasible(
                c.recipient,
                f"transport {c.transport_minutes} min exceeds the remaining cold-ischemia window "
                f"({window.end - window.start} min)"))
            continue
        feas.append(FeasibleRecipient(c.recipient, c.transport_minutes,
                                      window.end - transport.end))
    feas.sort(key=lambda f: f.slack_minutes, reverse=True)
    return feas, infeas


def nominate(feasible_set: List[FeasibleRecipient], chosen: str, *,
             agent: str, rationale: str, subject=None) -> Graph:
    """Nominate a recipient from the feasible cloud, as a hol:DecisionHolon — the SAME
    accountable decision model M4 uses.

    The feasible-recipient cloud is the deliberated **option space** (candidate
    destinations — propositions, the "for-orders" cloud). The nominated recipient is
    ``hol:chosen`` and becomes the **grounded destination** (``hol:produced``); every other
    option is rejected with a reason. A 'no allocation' option is always deliberated, so a
    real choice is recorded even with a single feasible recipient, and if ``chosen`` is not
    among the feasible recipients the decision declines (nothing is grounded). The membrane
    crossing that grounds a proposition is, here too, an accountable decision.

    Requires at least one feasible recipient (else there is nothing to nominate)."""
    if not feasible_set:
        raise ValueError("no feasible recipients to nominate among")
    subj = subject if subject is not None else TX["nomination"]
    decline = TX["opt-no-allocation"]
    options = {"_decline_": decline}
    slack = {}
    for f in feasible_set:
        options[f.recipient] = TX[f"recipient-{f.recipient}"]
        slack[f.recipient] = f.slack_minutes

    g = Graph()
    g.add((subj, RDF.type, HOL.DecisionHolon))
    g.add((subj, HOL.decidedBy, TX[agent]))
    g.add((subj, HOL.rationale, Literal(rationale)))
    for opt in options.values():
        g.add((opt, RDF.type, HOL.Option))
        g.add((subj, HOL.optionSpace, opt))

    chosen_key = chosen if chosen in options else "_decline_"
    chosen_opt = options[chosen_key]
    g.add((subj, HOL.chosen, chosen_opt))

    for key, opt in options.items():
        if opt == chosen_opt:
            continue
        reason = ("a feasible recipient was available and nominated" if key == "_decline_"
                  else f"not nominated (slack {slack[key]} min)")
        g.add((opt, HOL.rejectedBecause, Literal(reason)))

    if chosen_key != "_decline_":
        g.add((subj, HOL.produced, chosen_opt))  # the nominated recipient = the grounded destination
    return g
