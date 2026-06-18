"""Allen's interval algebra over event start/end pairs.

The thirteen relations emerge from comparing the four endpoints of two intervals
(EventBasedModeling: a relation between a start event and an end event). `feasible`
is the supply-chain predicate: the carried thing reaches its terminus before the
critical window closes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    start: int
    end: int


def relation(a: Interval, b: Interval) -> str:
    """Return Allen's relation of interval ``a`` to interval ``b``."""
    if a.end < b.start:
        return "before"
    if a.start > b.end:
        return "after"
    if a.end == b.start:
        return "meets"
    if a.start == b.end:
        return "met-by"
    if a.start == b.start and a.end == b.end:
        return "equals"
    if a.start == b.start:
        return "starts" if a.end < b.end else "started-by"
    if a.end == b.end:
        return "finishes" if a.start > b.start else "finished-by"
    if a.start > b.start and a.end < b.end:
        return "during"
    if a.start < b.start and a.end > b.end:
        return "contains"
    if a.start < b.start and a.end > b.start and a.end < b.end:
        return "overlaps"
    return "overlapped-by"


def feasible(window: Interval, transport: Interval) -> bool:
    """True if the transport/prep interval terminates within the critical window."""
    return transport.end <= window.end
