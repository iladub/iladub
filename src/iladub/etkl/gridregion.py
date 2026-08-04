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
from .geometry import COORD_EPS, Rule

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

GRID_REGION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-region.rq"
LINE_ENCLOSED_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "line-enclosed.rq"


def grid_evidence(band: Band, rules: Sequence[Rule]) -> Graph:
    """Emit the transient line/rule evidence graph for one band, including the
    ink-witness facts (loop P fixwave A): for each rule, does any band word CENTER
    lie strictly left (tab:hasInkLeft), resp. right (tab:hasInkRight), of its x
    (beyond COORD_EPS)? Words are the band's ink at this layer (the evidence is
    built from Band.lines, which are word-bucketed at this point in the pipeline —
    see compile.py::_build_ruled_band's docstring); no new extraction is needed. A
    real column separator has ink on both sides; a double-drawn outer-border twin
    does not, however close it sits to another rule x (R31: PRESENCE, not distance)."""
    g = Graph()
    centers = [(w.x0 + w.x1) / 2.0 for ln in band.lines for w in ln.words]
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
        has_left = any(cx < r.x - COORD_EPS for cx in centers)
        has_right = any(cx > r.x + COORD_EPS for cx in centers)
        g.add((u, TAB.hasInkLeft, Literal(has_left, datatype=XSD.boolean)))
        g.add((u, TAB.hasInkRight, Literal(has_right, datatype=XSD.boolean)))
    return g


def _grid_rows(band: Band, rules: Sequence[Rule]):
    """Shared grid-region.rq execution (idx, x) rows, read by both grid_lines and
    interior_rule_xs — one AXIOM query, two projections. Abstains (empty) when
    fewer than 3 DISTINCT rule x-positions exist: no rule can be interior with
    fewer than an outer pair plus one candidate."""
    if len({round(r.x, 2) for r in rules}) < 3:
        return []
    g = grid_evidence(band, rules)
    query = GRID_REGION_RQ.read_text()
    return list(g.query(query))


def grid_lines(band: Band, rules: Sequence[Rule]) -> set[int]:
    """Grid-member line indices. Abstains (empty set) when the evidence cannot
    decide: fewer than 3 DISTINCT rule x-positions means no rule can be interior."""
    return {int(row.idx) for row in _grid_rows(band, rules)}


def interior_rule_xs(band: Band, rules: Sequence[Rule]) -> list[float]:
    """Ink-interior rule x positions (loop P fixwave A §2): the vertical rules with
    ink on BOTH sides — real column separators, never a double-drawn outer-border
    twin (which has no ink on its own outboard side). Reads the SAME grid-region.rq
    query result as grid_lines, projecting ?x instead of ?idx. Feeds
    weld_hrule_boxes' full-width test; rule_aware_lines' column bucketing keeps
    using ALL rule xs, unchanged — the author's outer edges are still real column
    boundaries for bucketing, just never eligible to be grid-interior."""
    return sorted({round(float(row.x), 2) for row in _grid_rows(band, rules)})


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
