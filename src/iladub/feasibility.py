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

from .allen import Interval, feasible
from .decision import _ABO_OK


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
