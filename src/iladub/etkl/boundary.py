"""boundary — header-confirmed boundary evidence graph + query runner (loop G attempt 2).

Candidate column boundaries (interior gutters the author's rules left out) are CONFIRMED only when
the header region places glyph ink strictly on both sides within the candidate's author interval,
with no header glyph straddling it. The decision lives entirely in
vocab/queries/confirm-boundary.rq (open world, evidence-positive, no numeric literal); this module
is PROCEDURAL engine glue only: emit the transient per-band evidence graph and invoke rdflib. The
band is the closure boundary — a fresh Graph() per call (mirrors headergraph.py, loop B).

Why the header is the oracle: attempt 1 asserted interior gutters directly and was killed by a
counter-example — a monospaced ruled table whose values carry a column-aligned internal space
forms the same blank-run signal, and the manufactured phantom column CRASHED compile_tables at
tab:CoverageShape (a leaf column no header covers). Confirmation consults that same evidence
BEFORE asserting: a boundary the author did not label on both sides is not a column.

Why CHAR glyphs, not Words: the real target's leaf header extracts as ONE word blob
('CompletedCommodityTotal', x 716.3-818.4) which straddles the true boundary 753.7 at word level
and would self-reject; its chars do not straddle (Completed ends 743.6, Commodity begins 764.2).
Space glyphs are not ink (loop F) — the CALLER filters them before passing glyphs here.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:boundary:")     # transient per-band instance namespace

CONFIRM_BOUNDARY_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "confirm-boundary.rq"


def boundary_evidence(header_glyphs, candidates) -> Graph:
    """Fresh Graph() for one band. header_glyphs expose .x0/.x1 (non-space header-region chars);
    candidates are (boundary_x, interval_lo, interval_hi) with each interval a consecutive
    author-rule pair containing the candidate."""
    g = Graph()
    for i, ch in enumerate(header_glyphs):
        n = URIRef(f"{_EV}g{i}")
        g.add((n, RDF.type, TAB.HeaderGlyph))
        g.add((n, TAB.glyphX0, Literal(float(ch.x0), datatype=XSD.double)))
        g.add((n, TAB.glyphX1, Literal(float(ch.x1), datatype=XSD.double)))
    for i, (bx, lo, hi) in enumerate(candidates):
        n = URIRef(f"{_EV}b{i}")
        g.add((n, RDF.type, TAB.CandidateBoundary))
        g.add((n, TAB.boundaryX, Literal(float(bx), datatype=XSD.double)))
        g.add((n, TAB.intervalLo, Literal(float(lo), datatype=XSD.double)))
        g.add((n, TAB.intervalHi, Literal(float(hi), datatype=XSD.double)))
    return g


def confirmed_boundaries(header_glyphs, candidates) -> set[float]:
    """Run confirm-boundary.rq over the band's evidence; return the confirmed boundary x's."""
    if not candidates:
        return set()
    g = boundary_evidence(header_glyphs, candidates)
    q = CONFIRM_BOUNDARY_RQ.read_text(encoding="utf-8")
    return {float(row.bx) for row in g.query(q)}
