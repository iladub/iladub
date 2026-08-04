"""sectiongraph — the intra-page section-recognition evidence graph + query runner
(loop Q Task 2, spec 2026-08-04 §4.0).

Which ruled bands of a page repeat the SAME author-drawn section shape is a
declarative DERIVATION over a per-page evidence graph (open-world -> SPARQL; the
page is the closure boundary, one fresh Graph per `section_candidates` call — same
shape as classifygraph.py/gridregion.py). This module is the PROCEDURAL layer only:
locating each band's header box (reusing gridregion's `grid_lines`/
`peel_leading_captions`/`interior_rule_xs` and geometry's `hrule_boxes`/
`box_y_fallback_candidates`, ALL READ-ONLY — nothing here peels or welds a band, and
none of it is imported by the default `section_repair=False` compile path),
emitting the transient evidence graph, and invoking rdflib. No decision logic — the
repeat decision lives entirely in vocab/queries/section-repeat.rq (AXIOM).

Recognition is VERDICT-INDEPENDENT (spec §4.0 point 3, as corrected 2026-08-04): the
caller passes ALL ruled bands of the page — escalated and already-asserting alike.
Filtering which members actually get RE-READ is Task 4's job (the membrane's), not
this module's; this module only answers "which bands repeat".

A doubled-edge CBH-style section defeats loop P's band-local grid-region interior-rule
test (see gridregion.grid_lines's inertness note: the doubled outer border itself gets
admitted as "interior", so grid_lines/peel never scope the band correctly there) — that
is precisely why the escalated members need this page-level recognition instead of a
band-local repair.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .geometry import Rule, hrule_boxes, box_y_fallback_candidates
from .gridregion import grid_lines, enclosed_lines, peel_leading_captions, interior_rule_xs

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

SECTION_REPEAT_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "section-repeat.rq"


def _line_text(line) -> str:
    return " ".join(w.text for w in line.words)


def _header_box_text(band: Band, rules: Sequence[Rule]) -> str | None:
    """The leading full-width hrule box's MEMBER line texts, joined with '\\n' — the
    header-box identity (spec §4.0). None (honest abstain) when: the band's grid
    region cannot be located (`grid_lines` abstains — fewer than 3 distinct rule
    x's), no header box exists at all (`_leading_box_y` abstains), or the box
    encloses zero grid-region lines. Grid-region lines = band.lines minus the
    leading ENCLOSED non-grid run (`peel_leading_captions`, called here read-only:
    its return is used to pick which lines to read, nothing is peeled off the band).

    Membership is by Y-CONTAINMENT within the box, not a positional kept[:K] slice:
    when the grid region could not be scoped down (peel is inert — see
    `_leading_box_y`'s docstring for why), `kept` still carries the LEADING
    heading/notice strips ahead of the true header rows, so slicing the first K
    lines would read the wrong (and, worse, PER-SECTION-VARYING) text. Containment
    finds the header rows wherever they sit in `kept`."""
    gset = grid_lines(band, rules)
    if not gset:
        return None
    enclosed = enclosed_lines(band, rules)
    _captions, kept = peel_leading_captions(band.lines, gset, enclosed)
    box = _leading_box_y(band, rules)
    if box is None:
        return None
    lo, hi = box
    box_lines = [ln for ln in kept if lo <= (ln.top + ln.bottom) / 2.0 <= hi]
    if not box_lines:
        return None
    return "\n".join(_line_text(ln) for ln in box_lines)


def _interior_rules(band: Band, rules: Sequence[Rule]) -> list[Rule]:
    """The band's ink-interior Rule OBJECTS (with real y-extents), matched back from
    `gridregion.interior_rule_xs`' x-positions (ink on both sides — never a
    double-drawn outer-border twin, see that function's docstring). READ-ONLY: calls
    the same repair-scoped ink-witness query Task 3 already exposed for the pass-2
    peel; nothing here mutates a band or reruns any query with side effects, so this
    cannot touch the default compile path (`compile._build_ruled_band`'s
    `section_repair=False` branch never imports this module at all)."""
    ixs = {round(x, 2) for x in interior_rule_xs(band, rules)}
    return [r for r in rules if round(r.x, 2) in ixs]


def _overlaps_interior(box: tuple[float, float], interior: Sequence[Rule]) -> bool:
    """STRICT (open-interval) y-overlap: box and rule share more than a single
    boundary point. A box whose edge merely TOUCHES an interior rule's top (the
    exact-coincidence case a synthetic fixture with grid_top as both a box boundary
    AND the interior rules' own top produces) does not count — there is no shared
    row height, only a point, so no real ink co-location. This also matches the real
    specimen's measured small gap (notices box bottom 105.4 vs interior rule top
    105.5 — NOT touching at all) without needing a tuned gap tolerance: strict `<`
    already refuses both the touching AND the near-touching case identically."""
    lo, hi = box
    return any(r.top < hi and lo < r.bottom for r in interior)


def _leading_box_y(band: Band, rules: Sequence[Rule]) -> tuple[float, float] | None:
    """The header box's Y-extent (top, bottom): among ALL candidate boxes — every
    consecutive full-width hrule y-pair (`geometry.hrule_boxes`, y-order, topmost
    first) tried before every consecutive DISTINCT-hrule-y pair, X-EXTENT-FREE
    (`geometry.box_y_fallback_candidates`) — the FIRST one whose y-range is
    ink-interior-CROSSED: at least one of the band's ink-interior vertical rules
    (`_interior_rules`, above) has a y-extent that genuinely overlaps the box
    (`_overlaps_interior`). None (honest abstain) if no candidate qualifies.

    FIX ROUND 2 (task review, 2026-08-04): MEASURED on the real CBH specimen —
    additional full-width strip separators sit ABOVE the true header box (heading
    strip, then a separate notices strip, THEN the header box), so the box-0-only
    selection this function used before now picked the NOTICES box, whose text
    differs per section (the section's own printed notice) — `section_candidates`
    then found no matching signature and silently returned no group on the real
    page. The header box is exactly where the ink-interior column rules BEGIN
    (measured: interior rules span 105.5-199.6; the notices box 71.7-105.4 sits
    entirely above that span; the header box 105.3-119.1 sits inside it) — selecting
    by interior-rule-crossing generalizes past box-0 without introducing any new
    constant: `hrule_boxes`/`box_y_fallback_candidates` are the SAME enumerations
    (extended to expose every candidate, not just the first — see their docstrings
    in geometry.py); `interior_rule_xs` is Task 3's ALREADY-SHIPPED ink-witness
    evidence, read here READ-ONLY (see `_interior_rules`'s docstring: this cannot
    touch the default compile path, which never imports sectiongraph at all).

    THE DECISION (stated precisely, per CLAUDE.md §8): among the ordered candidate
    boxes, select the first one an ink-interior rule's y-extent overlaps.

    CLASSIFICATION: PROCEDURAL candidate SELECTION, not a reading. Every input is a
    raw fact already emitted by an earlier PROCEDURAL/AXIOM layer (drawn hrule y's,
    drawn rule x's, the ink-witness interior test) — this function performs no
    magnitude comparison of its own beyond the zero-tuned-constant overlap test
    above, invents no mark, and reads no new evidence beyond what Task 3 already
    exposed for a different (repair) purpose.

    IRREDUCIBILITY: this candidate is never asserted as a reading — it never answers
    "is this the header box" on its own, and it never reaches the graph as a fact
    about the DOCUMENT's meaning. It reaches the graph only as `tab:headerBoxText`,
    one input to `section-repeat.rq`'s compound match. THAT derivation is the
    disposal: two candidates are treated as the SAME repeated header only when BOTH
    the candidate's line texts AND the band's independent `tab:ruleXsSignature`
    agree, verbatim, across bands. A wrong candidate on a real document produces
    non-matching facts — no group, honest abstain — never a false assertion; it can
    only ever cost RECALL (missing a repeat), never accuracy (fabricating one). This
    is the AXIOM playing the oracle's role that a NEURAL proposal would otherwise
    need a GenAI+SHACL/tiling oracle for — here the oracle is `section-repeat.rq`
    itself, so the candidate needs no separate disposal step of its own.

    WHY NOT AXIOM-only (emit every candidate pair, let the query choose): considered
    and deferred, not ruled out — see residues.md R48 (updated fix round 2: the
    false-candidate risk it flagged materialized once, on this exact box-0-only
    shape, and closes with THIS fix; the row stays open for the residual class the
    interior-crossing test does not cover — a notices strip genuinely CROSSED by an
    interior rule). It remains real, not-yet-warranted work: every candidate box
    this function can now select is disposed by BOTH the interior-crossing test AND
    section-repeat.rq's compound match, two independent checks, not one.

    WHY A FALLBACK TIER EXISTS AT ALL: a doubled/inset outer border (the real-CBH
    shape `multi_section_ruled_pdf` reproduces, spec §4.0) defeats ANY
    coordinate-tolerance x-extent test the same way it defeats grid_lines's
    interior-x test — see gridregion.grid_lines's inertness note; by design,
    band-LOCAL machinery (weld) cannot see past a doubled edge. This module exists
    precisely to recognize that repeated shape at PAGE scope instead, so it must not
    inherit the same band-local blind spot for its own header-box candidate."""
    interior = _interior_rules(band, rules)
    xs = sorted({round(r.x, 2) for r in rules})
    for box in hrule_boxes(band.hrules, xs):
        if _overlaps_interior(box, interior):
            return box
    for box in box_y_fallback_candidates(band.hrules):
        if _overlaps_interior(box, interior):
            return box
    return None


def _rule_xs_signature(rules: Sequence[Rule]) -> str | None:
    """The band's DISTINCT rounded (2dp) rule x-positions, space-joined ascending —
    a canonical string fact for set identity (brief's licensed shape). Deliberately
    ALL of the band's rules, not just the "interior" subset: identity across
    sections is what section-repeat cares about, and `grid_lines`'s interior test is
    exactly the test the doubled-edge shape defeats (see module docstring) — using
    its output here would just reintroduce that defeat one level up. None when the
    band carries no rules at all."""
    xs = sorted({round(r.x, 2) for r in rules})
    if not xs:
        return None
    return " ".join(str(x) for x in xs)


def section_evidence(bands: Sequence[tuple[int, Band, tuple[Rule, ...]]]) -> Graph:
    """Emit the transient per-band signature-fact graph: `tab:headerBoxText` and
    `tab:ruleXsSignature` for every band whose header box is locatable. A band that
    cannot locate one (no full-width hrule box, or the grid region is undecidable)
    emits NO facts — honest abstain; it can never join a group."""
    g = Graph()
    for idx, band, rules in bands:
        text = _header_box_text(band, rules)
        sig = _rule_xs_signature(rules)
        if text is None or sig is None:
            continue
        u = _EV["band-%d" % idx]
        g.add((u, RDF.type, TAB.SectionBand))
        g.add((u, TAB.bandIndex, Literal(idx, datatype=XSD.integer)))
        g.add((u, TAB.headerBoxText, Literal(text)))
        g.add((u, TAB.ruleXsSignature, Literal(sig)))
    return g


def section_candidates(bands: Sequence[tuple[int, Band, tuple[Rule, ...]]]) -> tuple[tuple[int, ...], ...]:
    """Groups (>= 2 members) of band indices whose header-box text AND rule-x
    signature both agree — i.e. the SAME author-drawn section shape repeats
    intra-page. Deterministic: groups sorted ascending by their first (lowest)
    member; members ascending within a group. A band index appearing in no
    repeated pair (a lone shape, or no locatable signature) is simply absent —
    never emitted as its own singleton group."""
    g = section_evidence(bands)
    query = SECTION_REPEAT_RQ.read_text()

    parent: dict[int, int] = {}

    def find(x: int) -> int:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for row in g.query(query):
        union(int(row.a), int(row.b))

    members: dict[int, list[int]] = {}
    for x in parent:
        members.setdefault(find(x), []).append(x)
    groups = sorted(
        (tuple(sorted(m)) for m in members.values() if len(m) >= 2),
        key=lambda t: t[0],
    )
    return tuple(groups)
