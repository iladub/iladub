"""sectiongraph — the intra-page section-recognition evidence graph + query runner
(loop Q Task 2, spec 2026-08-04 §4.0).

Which ruled bands of a page repeat the SAME author-drawn section shape is a
declarative DERIVATION over a per-page evidence graph (open-world -> SPARQL; the
page is the closure boundary, one fresh Graph per `section_candidates` call — same
shape as classifygraph.py/gridregion.py). This module is the PROCEDURAL layer only:
locating each band's header box (reusing gridregion's `grid_lines`/
`peel_leading_captions` and geometry's `leading_hrule_box`, ALL READ-ONLY — nothing
here peels or welds a band), emitting the transient evidence graph, and invoking
rdflib. No decision logic — the repeat decision lives entirely in
vocab/queries/section-repeat.rq (AXIOM).

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
from .geometry import Rule, leading_hrule_box, leading_box_y_fallback
from .gridregion import grid_lines, enclosed_lines, peel_leading_captions

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


def _leading_box_y(band: Band, rules: Sequence[Rule]) -> tuple[float, float] | None:
    """The header box's Y-extent (top, bottom): `leading_hrule_box`'s exact box
    arithmetic (weld_hrule_boxes' own full-width test — reused VERBATIM, never
    duplicated) when it locates a box; otherwise the fallback below.

    THE DECISION (stated precisely, per CLAUDE.md §8): when the full-width test
    abstains, select the author's first two DISTINCT drawn hrule y-positions,
    X-EXTENT-FREE, as the CANDIDATE header box.

    CLASSIFICATION: PROCEDURAL candidate generation, not a reading. It is a raw,
    mechanical selection over author marks — sort the drawn hrule y's, take the two
    lowest — the same shape as `extract_words`/`extract_rules`: a presence/ordering
    test with zero tuned constant, zero magnitude comparison, zero invented mark
    (every y here was drawn by the author; nothing is synthesised).

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
    and deferred, not ruled out — see residues.md R48. It is real work (widening the
    evidence graph and the query's shape) not yet warranted by a measured document;
    every fixture measured so far has the true header box as one of the first two
    hrule y's, so there is no live case where a WIDER candidate set would change the
    outcome.

    WHY THE FALLBACK EXISTS AT ALL: a doubled/inset outer border (the real-CBH shape
    `multi_section_ruled_pdf` reproduces, spec §4.0) defeats ANY coordinate-tolerance
    x-extent test the same way it defeats grid_lines's interior-x test — see
    gridregion.grid_lines's inertness note; by design, band-LOCAL machinery (weld)
    cannot see past a doubled edge. This module exists precisely to recognize that
    repeated shape at PAGE scope instead, so it must not inherit the same band-local
    blind spot for its own header-box candidate."""
    xs = sorted({round(r.x, 2) for r in rules})
    box = leading_hrule_box(band.hrules, xs)
    if box is not None:
        return box
    # the fallback arithmetic lives in geometry.leading_box_y_fallback (loop Q Task 4
    # factored it there so the repair path's weld reuses it verbatim, never a copy)
    return leading_box_y_fallback(band.hrules)


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
