"""gridregion — the ruled-band grid-membership evidence graph + query runner (loop P;
loop Q Task 3 adds the repair-scoped ink-witness variant, salvaged from reverted
commit b515283).

Which visual lines of a ruled band are INSIDE the author's grid (vs. full-width
strips above it — key headings, notices) is a declarative DERIVATION over author-mark
facts (open world -> SPARQL; the band is the closure boundary). This module is the
PROCEDURAL layer only: emitting the transient evidence graph (raw geometry, including
the y-centers and the ink-witness facts, so the query stays literal-free) and invoking
rdflib. No decision logic, no tuned constant — the decision lives in
vocab/queries/grid-region.rq (default, AXIOM) or vocab/queries/grid-region-ink.rq
(repair-scoped, AXIOM, `ink_witness=True` only).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from decimal import Decimal
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .geometry import COORD_EPS, Rule

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

GRID_REGION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-region.rq"
GRID_REGION_INK_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-region-ink.rq"
LINE_ENCLOSED_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "line-enclosed.rq"


def grid_evidence(band: Band, rules: Sequence[Rule]) -> Graph:
    """Emit the transient line/rule evidence graph for one band, including the
    ink-witness facts (loop P fixwave A, salvaged loop Q Task 3): for each rule, does
    any band word CENTER lie strictly left (tab:hasInkLeft), resp. right
    (tab:hasInkRight), of its x (beyond COORD_EPS)? Words are the band's ink at this
    layer (the evidence is built from Band.lines, which are word-bucketed at this
    point in the pipeline — see compile.py::_build_ruled_band's docstring); no new
    extraction is needed. A real column separator has ink on both sides; a
    double-drawn outer-border twin does not, however close it sits to another rule x
    (R31: PRESENCE, not distance).

    Emitting these facts unconditionally does not change the DEFAULT (grid-region.rq)
    query's result — that query never references tab:hasInkLeft/hasInkRight — so this
    is byte-identical for every caller that does not read the ink-witness query."""
    g = Graph()
    centers = [(w.x0 + w.x1) / 2.0 for ln in band.lines for w in ln.words]
    for i, ln in enumerate(band.lines):
        u = _EV["line-%d" % i]
        g.add((u, RDF.type, TAB.BandLine))
        g.add((u, TAB.lineIndex, Literal(i, datatype=XSD.integer)))
        cy = (ln.top + ln.bottom) / 2.0
        g.add((u, TAB.lineCenterY, Literal(Decimal(str(round(cy, 2))))))
    for k, r in enumerate(rules):
        u = _EV["rule-%d" % k]
        g.add((u, RDF.type, TAB.RuleSpan))
        g.add((u, TAB.ruleX, Literal(Decimal(str(round(r.x, 2))))))
        g.add((u, TAB.ruleTop, Literal(Decimal(str(round(r.top, 2))))))
        g.add((u, TAB.ruleBottom, Literal(Decimal(str(round(r.bottom, 2))))))
        has_left = any(cx < r.x - COORD_EPS for cx in centers)
        has_right = any(cx > r.x + COORD_EPS for cx in centers)
        g.add((u, TAB.hasInkLeft, Literal(has_left, datatype=XSD.boolean)))
        g.add((u, TAB.hasInkRight, Literal(has_right, datatype=XSD.boolean)))
    return g


def _grid_rows(band: Band, rules: Sequence[Rule], *, ink_witness: bool = False):
    """Shared query execution (idx, [x]) rows, read by both `grid_lines` and
    `interior_rule_xs` — one AXIOM query, two projections. Abstains (empty) when
    fewer than 3 DISTINCT rule x-positions exist: no rule can be interior with fewer
    than an outer pair plus one candidate. `ink_witness` selects which query file is
    read; it never changes the evidence graph built (see `grid_evidence`)."""
    if len({round(r.x, 2) for r in rules}) < 3:
        return []
    g = grid_evidence(band, rules)
    query = (GRID_REGION_INK_RQ if ink_witness else GRID_REGION_RQ).read_text()
    return list(g.query(query))


def grid_lines(band: Band, rules: Sequence[Rule], *, ink_witness: bool = False) -> set[int]:
    """Grid-member line indices. Abstains (empty set) when the evidence cannot
    decide: fewer than 3 DISTINCT rule x-positions means no rule can be interior.

    `ink_witness` (loop Q Task 3, keyword-only, default False): False (the default,
    EVERY caller except the section-repair peel) reads today's shipped
    grid-region.rq — MIN/MAX-x "strictly between the outermost rules" — byte-identical
    to before this parameter existed. True reads grid-region-ink.rq (salvaged from
    reverted b515283): interior = ink on BOTH sides (tab:hasInkLeft/hasInkRight),
    which a double-drawn border twin can never satisfy on its own outboard side. Only
    compile._build_ruled_band's peel passes True, and only when its own
    `section_repair` parameter is True (loop Q Task 4 sets that from the driver's
    recognized, still-escalated repeat groups) — every other call site, and every
    existing caller of this module, is unaffected.

    Inertness marker (F3, final review; still true for ink_witness=False): on the
    real CBH specimen, the default MIN/MAX-x interior test is defeated by doubled
    border rules — the section's outer border is drawn as a pair of near-coincident
    verticals (x=37.92/38.2), so the OUTER border itself gets admitted as "interior"
    and the peel this feeds never fires there. See R42's measured map
    (`docs/superpowers/residues.md`) — the repair is re-homed at SECTION scope
    (loop Q), reachable only through this same-named parameter, never the default."""
    return {int(row.idx) for row in _grid_rows(band, rules, ink_witness=ink_witness)}


def interior_rule_xs(band: Band, rules: Sequence[Rule]) -> list[float]:
    """Ink-interior rule x positions (loop P fixwave A, salvaged loop Q Task 3): the
    vertical rules with ink on BOTH sides — real column separators, never a
    double-drawn outer-border twin (which has no ink on its own outboard side).
    ALWAYS reads grid-region-ink.rq (the ink-witness query is the only one that
    projects ?x) regardless of any caller's own `ink_witness` choice for
    `grid_lines` — this function has no non-ink-witness meaning of its own.

    Exposed for loop Q's repair path; not yet wired into `weld_hrule_boxes` (Task 3's
    scope is the peel only — "everything else, including the leading-box weld, as
    shipped" per the plan). rule_aware_lines' own column bucketing keeps using every
    rule x, including the outer edges, unaffected by this function."""
    return sorted({round(float(row.x), 2)
                   for row in _grid_rows(band, rules, ink_witness=True)})


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
