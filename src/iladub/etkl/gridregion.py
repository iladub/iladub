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
LINE_ENCLOSED_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "line-enclosed.rq"


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
    decide: fewer than 3 DISTINCT rule x-positions means no rule can be interior.

    Inertness marker (F3, final review): on the real CBH specimen, this MIN/MAX-x
    interior test is defeated by doubled border rules — the section's outer border is
    drawn as a pair of near-coincident verticals (x=37.92/38.2), so the OUTER border
    itself gets admitted as "interior" and the peel this feeds never fires there. See
    R42's measured map (`docs/superpowers/residues.md`) — the repair is re-homed at
    SECTION scope (loop Q), not this band-local MIN/MAX test."""
    if len({round(r.x, 2) for r in rules}) < 3:
        return set()
    g = grid_evidence(band, rules)
    query = GRID_REGION_RQ.read_text()
    return {int(row.idx) for row in g.query(query)}


def enclosed_lines(band: Band, rules: Sequence[Rule]) -> set[int]:
    """Line indices ENCLOSED by at least one rule's y-extent (any rule — interior or
    outer). A leading strip only qualifies as document furniture (peelable) when it is
    itself enclosed by some rule, typically the section's own outer border — proving it
    lies INSIDE the same author-drawn section as the grid. A header-hierarchy label
    with NO rule anywhere near it (a merged parent row drawn above a boxed sub-header)
    is not enclosed by anything and must never be peeled (loop P fix round 2)."""
    g = grid_evidence(band, rules)
    query = LINE_ENCLOSED_RQ.read_text()
    return {int(row.idx) for row in g.query(query)}


def peel_leading_captions(lines: Sequence, gset: set[int],
                          enclosed: set[int] = frozenset()) -> tuple[tuple, tuple]:
    """Split `lines` into (captions, kept): captions is the LEADING prefix strictly
    before the first grid-member index (min(gset)); kept is everything from there on,
    UNCHANGED. Loop P fix round 2 (regression repair): the peel's scope is strips
    ABOVE the grid only (spec §3) — an INTERIOR or TRAILING non-grid line (e.g. a
    below-grid subtotal/total row) is never peeled, only a leading run is. Peeling
    every non-grid line (the original Task-2 shape) swallowed page-local subtotal
    rows that loop H/N's arithmetic derivations must see, breaking
    test_continuation_licence/test_logical_arithmetic on real fixtures.

    A second guard, ALSO required (measured — "leading-only" alone was insufficient:
    page_local_group_two_page_pdf's/case3_with_subtotals_pdf's "Voyage" merged parent
    header row is itself the sole LEADING non-grid line, so restricting to a leading
    run still swallowed it, flipping the region's classification away from
    HierarchicalTable and breaking the very same two tests): every leading candidate
    line must be ENCLOSED by some rule's y-extent (`enclosed_lines`) — a floating
    header-hierarchy label with no rule anywhere near it is not document furniture and
    is never peeled. Passing no `enclosed` (the default, empty set) is the conservative
    abstain: nothing is peeled, byte-identical to "no peel".

    Returns ((), tuple(lines)) whenever gset is empty, its minimum is already 0, or the
    leading run is not fully enclosed — no partial/ambiguous peel is ever produced."""
    lines = tuple(lines)
    if not gset:
        return (), lines
    first = min(gset)
    if first <= 0:
        return (), lines
    if not all(i in enclosed for i in range(first)):
        return (), lines
    return lines[:first], lines[first:]
