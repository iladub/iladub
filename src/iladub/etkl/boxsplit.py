"""boxsplit — the box-split DECISION: which text bands hold two or more of the author's closed
ruled boxes (spec 2026-09-28-box-split-design.md § 3.2, ruling R-d).

`boxes.py` reads WHAT boxes a page draws and decides nothing about bands. This module decides
which bands they belong to and which bands must split (`bands_to_split`), and then applies that
decision (`partition_words`, `split_band` — spec § 3.3-3.6), which decides nothing further.

BAND INDEX SPACE (R2, stated precisely because it is load-bearing): every index this module
reads or returns — `bands`' own position, `tab:boxBandIndex`, `bands_to_split`'s dict keys — is
an index into `compile.page_bands`' RAW band list, `detect_bands(text_lines(words))`, BEFORE
`segment`, `cut_trailing_notes` and the ruled-run merge. It is explicitly NOT `tab:bandIndex`'s
index space (`tab:PageBand`'s own property): that one names a band's position in whatever list
`page_bands` ultimately RETURNS, after every one of those per-band rebuilds. The caller
(`page_bands`' own `for band in raw_bands:` loop, Task 3's site) needs the pre-rebuild index, so
reusing `tab:bandIndex` here would silently claim the wrong population — the same reasoning
`tab:bandRuleX` already sets as precedent for this ontology.

CLAUDE.md §8 CLASSIFICATION, per function:

- `_box_owner` — PROCEDURAL, exact set membership (spec § 3.2, I-2a): "every page word inside
  the box's bbox is a word of that band" is decidable by exact interval containment over each
  word's and the box's own already-measured (x0, x1, top, bottom) — no threshold, no perceptual
  judgement, nothing underdetermined, so it is irreducible to NEURAL and does not belong in
  SPARQL either: AXIOM's open-world derivation presupposes an evidence graph of ALREADY-EMITTED
  RDF facts to derive over (band-boxes.rq's own precondition), and producing that first fact from
  raw coordinates is exactly the step that has none yet to read — the same reason
  `sectiongraph._rule_xs_signature` computes its signature procedurally before `band-run.rq` ever
  sees a triple. `bands` — `compile.page_bands`' own `detect_bands` output — is assumed to
  partition every page word into exactly one band. It decides no table question; it only answers
  a fact about geometry.
- `box_evidence` — PROCEDURAL raw extraction: `_box_owner`'s facts, turned into typed RDF. It
  decides nothing further; the emitter's only judgement is I-2a's abstain, already made by
  `_box_owner` returning `None`.
- `bands_to_split` — the AXIOM decision (I-2b) plus PROCEDURAL glue that reads its answer.
  "This band holds >= 2 tables" is `vocab/queries/band-boxes.rq`, a SPARQL `SELECT`, open-world,
  closed only within the band (the holon-scoped `HAVING`) — never Python arithmetic on a count.
  Reassembling each selected band's boxes from the query's band indices is PROCEDURAL: it applies
  the already-derived membership, deciding nothing new.
- `_extent`, `_contains`, `partition_words`, `split_band` — PROCEDURAL (spec § 6, "word partition + band
  construction"): they APPLY the decision `bands_to_split` already made, by exact interval
  containment and by calling the unchanged builders; they decide no table question of their own.

Mirrors `sectiongraph.run_evidence`'s discipline throughout: one transient `Graph()` per call,
canonical literals, and a band/box pair that carries no fact emits no node at all.
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import replace
from typing import Callable, Sequence

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .boxes import Box
from .geometry import Char, HRule, Line, Rule, Word, text_lines

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:box:")        # transient per-page box-evidence instance namespace

BAND_BOXES_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "band-boxes.rq"


def _extent(item: Word | Char | Rule | HRule) -> tuple[float, float, float, float]:
    """(x0, x1, top, bottom) of a word, a glyph, a vertical `Rule` (a zero-width segment at x)
    or an `HRule` (a zero-height segment at y) — each as its own coordinates state it.
    PROCEDURAL: a coordinate projection, no arithmetic beyond reading the fields."""
    if isinstance(item, Rule):
        return (item.x, item.x, item.top, item.bottom)
    if isinstance(item, HRule):
        return (item.x0, item.x1, item.y, item.y)
    return (item.x0, item.x1, item.top, item.bottom)


def _contains(rect: tuple[float, float, float, float], item: Word | Char | Rule | HRule) -> bool:
    """True when `item`'s extent lies inside `rect` = (x0, x1, top, bottom).

    PROCEDURAL: exact interval containment, no tolerance. The ONE containment test of this
    module — a box's membership (I-2a), the word partition (I-3a), the glyph clip (I-3b) and the
    residue's scope all read it, so a word that belongs to a box, the glyphs that box is built
    from, and the ink its residue is refused can never be judged by two different rules."""
    x0, x1, top, bottom = rect
    ix0, ix1, itop, ibottom = _extent(item)
    return x0 <= ix0 and ix1 <= x1 and top <= itop and ibottom <= bottom


def _box_owner(box: Box, bands: Sequence[Band]) -> int | None:
    """The 0-based index of the ONE band `box` belongs to, or None (spec § 3.2, I-2a).

    PROCEDURAL: exact set membership, no tolerance. A box belongs to a band when every page
    word inside its painted bbox is a word of that band — equivalently, when the set of band
    indices owning some word inside the box collapses to exactly one. `bands` is assumed to
    partition every word on the page (compile.page_bands' own `detect_bands` guarantee), so
    checking each band's own words in turn IS checking against the whole page: a word inside
    the box that is not this band's must be some other band's, and disqualifies every band it
    does not belong to. A box with no words inside it (`owners` empty) and a box whose words
    span more than one band (`owners` has >= 2 members) both return None — the same "belongs to
    no band" answer, for the two different reasons I-2a names.
    """
    owners = {
        idx
        for idx, band in enumerate(bands)
        for line in band.lines
        for w in line.words
        if _contains((box.x0, box.x1, box.top, box.bottom), w)
    }
    return owners.pop() if len(owners) == 1 else None


def box_evidence(bands: Sequence[Band], boxes: Sequence[Box]) -> Graph:
    """The transient per-call box-evidence graph for band-boxes.rq: one `tab:ClosedBox` node
    per box that belongs to a band (I-2a), carrying `tab:boxBandIndex`.

    PROCEDURAL raw extraction over `_box_owner`'s already-decided facts. A box with no owner
    (no words inside it, or words spanning more than one band) emits NOTHING — no node, no
    triple — exactly the abstain `sectiongraph.run_evidence` makes for a band with no rules:
    the query cannot defend against a node carrying no `tab:boxBandIndex` fact, so the emitter
    must never mint one.
    """
    g = Graph()
    for i, box in enumerate(boxes):
        owner = _box_owner(box, bands)
        if owner is None:
            continue
        u = _EV["box-%d" % i]
        g.add((u, RDF.type, TAB.ClosedBox))
        g.add((u, TAB.boxBandIndex, Literal(owner, datatype=XSD.integer)))
    return g


def bands_to_split(bands: Sequence[Band], boxes: Sequence[Box]) -> dict[int, tuple[Box, ...]]:
    """Band index -> its closed boxes (ordered by (top, x0)), for every band band-boxes.rq
    selects — i.e. every band holding >= 2 closed boxes that belong to it (I-2b, ruling R-d).

    The AXIOM decision is entirely the query's: this only builds its evidence, runs it, and
    reassembles each selected band's boxes by re-applying `_box_owner` (PROCEDURAL — it decides
    nothing the query has not already settled, it only recovers the objects the query's band
    indices name). `boxes` is assumed already sorted by (top, x0) (`boxes.page_boxes`' own
    contract), so filtering it band by band, order preserved, needs no re-sort. A page with no
    selected band returns {}.
    """
    g = box_evidence(bands, boxes)
    selected = {int(row.band) for row in g.query(BAND_BOXES_RQ.read_text())}
    if not selected:
        return {}
    owner_of = [_box_owner(box, bands) for box in boxes]
    return {
        idx: tuple(box for box, owner in zip(boxes, owner_of) if owner == idx)
        for idx in sorted(selected)
    }


# --- Task 3: the split (spec § 3.3-3.6) — applies the decision above, decides nothing ------------

def _rect(box: Box) -> tuple[float, float, float, float]:
    """A box's painted bbox as (x0, x1, top, bottom). PROCEDURAL: a field projection only."""
    return (box.x0, box.x1, box.top, box.bottom)


def partition_words(band: Band, boxes: Sequence[Box]
                    ) -> tuple[list[list[Word]], list[list[Word]], tuple[Line, ...]]:
    """The word partition of spec § 3.3 (I-3a): per box, the band's words inside it; per box,
    the band's words inside its title bar; and the RESIDUE — the band's own lines with those
    words removed (a line left with no word is dropped).

    PROCEDURAL — exact containment (`_contains`), deciding nothing. Each word is claimed at most
    once, box interiors first and title bars second, each in `boxes`' own order, so the three
    parts are a partition of the band's words by construction. A box left with no word claims
    no title words either (it builds no band, `split_band`), so they fall to the residue. The residue keeps the raw band's
    OWN line grouping (the page-level `text_lines` that `detect_bands` read) rather than
    re-grouping its words: re-running `text_lines` on the subset would re-derive its y tolerance
    from a different word population, and I-3d asks for the residue to go through the existing
    path "exactly as a raw band does today".
    """
    claimed: set[int] = set()
    box_words: list[list[Word]] = []
    for box in boxes:
        mine = [w for ln in band.lines for w in ln.words
                if id(w) not in claimed and _contains(_rect(box), w)]
        claimed.update(id(w) for w in mine)
        box_words.append(mine)
    title_words: list[list[Word]] = []
    for box, inside in zip(boxes, box_words):
        # A box left wordless builds no band (split_band), so it claims no title either.
        mine = ([w for ln in band.lines for w in ln.words
                 if id(w) not in claimed and _contains(box.title_bar, w)]
                if box.title_bar is not None and inside else [])
        claimed.update(id(w) for w in mine)
        title_words.append(mine)
    residue: list[Line] = []
    for ln in band.lines:
        kept = tuple(w for w in ln.words if id(w) not in claimed)
        if kept:
            residue.append(Line(kept, min(w.top for w in kept), max(w.bottom for w in kept)))
    return box_words, title_words, tuple(residue)


def _box_band(box: Box, words: Sequence[Word], title: Sequence[Word],
              page_chars: Sequence[Char]) -> Band:
    """One box band (spec § 3.4-3.5): the box's words -> `text_lines` -> the UNCHANGED
    `compile._build_ruled_band`, fed ONLY box-scoped inputs (I-3b) — the box's own verticals as
    `Rule(x=centre, top, bottom)`, its own horizontals as `HRule(y=centre, x0, x1)`, and the page
    glyphs clipped to the box's x- AND y-extent. No page-wide rule list is consulted. The title
    words become captions AFTER the build (I-3c): `_build_ruled_band` replaces `captions` on
    every return path with its own peel, so they are prepended to what it returns. The band
    carries `frame = _rect(box)` (spec § 9.3): the author's closed frame, which `compile_tables`
    admits in place of the multi-table gate's proxy.

    PROCEDURAL — construction only. The centre of a painted extent is exact arithmetic on the
    mark itself, the same reduction `geometry.extract_rules` makes of a pdfplumber edge; it is
    not a tolerance."""
    # Imported at call time, so this module can be imported without loading compile. Nothing
    # forces it today: compile.page_bands imports boxsplit lazily, inside the function.
    from .compile import _build_ruled_band
    lines = text_lines(list(words))
    sub = Band(tuple(lines), min(ln.top for ln in lines), max(ln.bottom for ln in lines))
    sub_rules = tuple(Rule(x=(v.x0 + v.x1) / 2.0, top=v.top, bottom=v.bottom)
                      for v in box.verticals)
    sub_hrules = tuple(HRule(y=(h.top + h.bottom) / 2.0, x0=h.x0, x1=h.x1)
                       for h in box.horizontals)
    box_chars = [c for c in page_chars if _contains(_rect(box), c)]
    built = _build_ruled_band(sub, sub_rules, sub_hrules, box_chars, section_repair=False)
    # `frame` (spec § 9.3): the box's own bbox, carried as read -- the ONLY site that sets it.
    return replace(built, captions=tuple(text_lines(list(title))) + tuple(built.captions),
                   frame=_rect(box))


def _band_key(band: Band) -> tuple[float, float]:
    """(top, x0) of a band (I-3e): its own top, and the leftmost x0 of its words.
    PROCEDURAL: exact min over the band's own coordinates; it orders, it decides nothing."""
    return (band.top, min(w.x0 for ln in band.lines for w in ln.words))


def split_band(band: Band, boxes: Sequence[Box], page_chars: Sequence[Char],
               pdf_path: str, page_number: int, *,
               build_sub: Callable[[Band, Callable[[object], bool]], tuple[Band, tuple | None]]
               ) -> list[tuple[Band, tuple | None]]:
    """Split one raw band `bands_to_split` selected into its box bands and ONE residue
    (spec § 3.3), each paired with its `page_bands` specs entry, ordered by (top, x0) (I-3e).

    Box bands carry the spec `None` (§ 3.6): they are never rebuilt with `section_repair=True`,
    whose rebuild would read page-scoped chars again. The residue — words in no box and no title
    bar — goes through `cut_trailing_notes(segment(residue), pdf_path, page_number)` and then
    `build_sub`, which IS `page_bands`' own per-sub-band code (I-3d): no residue logic is
    duplicated here, and each residue sub-band carries exactly the (band, spec) that code
    produces for it. `build_sub` is a keyword argument because that code reads the page's
    rules, which only `page_bands` holds.

    THE RESIDUE'S INPUTS ARE SCOPED TOO — the one addition to I-3d, and § 3.4's own principle.
    `build_sub(sub, keep)` hands the existing code only the page rules, horizontals and glyphs
    `keep` admits: those inside NO region a box band was built from (its bbox, its title bar).
    Without it the existing code filters rules and glyphs by y alone, so a residue whose
    y-range crosses the boxes re-reads their ink — measured on cbh p0, where `1,951,264` sits
    beside the boxes on the title line: the residue came back as the whole fused band (10
    lines, 26 rules), every box glyph carried twice. The residue's words are already scoped by
    the partition; this scopes the marks and glyphs it is re-read from, by the same `_contains`.

    A box the partition leaves wordless (possible only if two selected boxes nest, and the
    inner one claims every word first) builds no band; its title words, unclaimed, stay in the
    residue, so I-3a holds either way.

    PROCEDURAL — it applies the decision `bands_to_split` made; it decides nothing.
    """
    from .segment import segment
    from .trailing import cut_trailing_notes
    box_words, title_words, residue_lines = partition_words(band, boxes)
    out: list[tuple[Band, tuple | None]] = []
    built_from: list[tuple[float, float, float, float]] = []
    for box, words, title in zip(boxes, box_words, title_words):
        if words:
            out.append((_box_band(box, words, title, page_chars), None))
            built_from.append(_rect(box))
            if box.title_bar is not None:
                built_from.append(box.title_bar)
    if residue_lines:
        residue = Band(residue_lines, min(ln.top for ln in residue_lines),
                       max(ln.bottom for ln in residue_lines))

        def keep(item) -> bool:
            """True for a rule, horizontal or glyph outside every region a box band was built
            from. KNOWN LIMIT: a residue word that STRADDLES a box edge (not wholly inside, so
            the partition leaves it in the residue) keeps its words-path text but loses its
            in-box glyphs on a chars rebuild (a ruled residue's `rule_aware_lines`). The corpus
            has no such word."""
            return not any(_contains(rect, item) for rect in built_from)

        out.extend(build_sub(sub, keep)
                   for sub in cut_trailing_notes(segment(residue), pdf_path, page_number))
    return sorted(out, key=lambda pair: _band_key(pair[0]))
