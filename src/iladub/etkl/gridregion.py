"""gridregion — the ruled-band grid-membership evidence graph + query runner (loop P).

Which visual lines of a ruled band are INSIDE the author's grid (vs. full-width
strips above it — key headings, notices) is a declarative DERIVATION over author-mark
facts (open world -> SPARQL; the band is the closure boundary). This module is the
PROCEDURAL layer only: emitting the transient evidence graph (raw geometry, including
the y-centers, so the query stays literal-free) and invoking rdflib. No decision
logic, no tuned constant — the decision lives in vocab/queries/grid-region.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .geometry import Rule

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

GRID_REGION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-region.rq"


def grid_evidence(band: Band, rules: Sequence[Rule]) -> Graph:
    """Emit the transient line/rule evidence graph for one band."""
    g = Graph()
    for i, ln in enumerate(band.lines):
        u = _EV["line-%d" % i]
        g.add((u, RDF.type, TAB.BandLine))
        g.add((u, TAB.lineIndex, Literal(i, datatype=XSD.integer)))
        cy = (ln.top + ln.bottom) / 2.0
        g.add((u, TAB.lineCenterY, Literal(round(cy, 2), datatype=XSD.decimal)))
    for k, r in enumerate(rules):
        u = _EV["rule-%d" % k]
        g.add((u, RDF.type, TAB.RuleSpan))
        g.add((u, TAB.ruleX, Literal(round(r.x, 2), datatype=XSD.decimal)))
        g.add((u, TAB.ruleTop, Literal(round(r.top, 2), datatype=XSD.decimal)))
        g.add((u, TAB.ruleBottom, Literal(round(r.bottom, 2), datatype=XSD.decimal)))
    return g


def grid_lines(band: Band, rules: Sequence[Rule]) -> set[int]:
    """Grid-member line indices. Abstains (empty set) when the evidence cannot
    decide: fewer than 3 DISTINCT rule x-positions means no rule can be interior."""
    if len({round(r.x, 2) for r in rules}) < 3:
        return set()
    g = grid_evidence(band, rules)
    query = GRID_REGION_RQ.read_text()
    return {int(row.idx) for row in g.query(query)}
