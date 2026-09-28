"""boxsplit — the box-split DECISION: which text bands hold two or more of the author's closed
ruled boxes (spec 2026-09-28-box-split-design.md § 3.2, ruling R-d).

`boxes.py` reads WHAT boxes a page draws and decides nothing about bands. This module decides
which bands they belong to and which bands must split — nothing more. Task 3 performs the split
(the word partition and band construction); it is not built here.

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

Mirrors `sectiongraph.run_evidence`'s discipline throughout: one transient `Graph()` per call,
canonical literals, and a band/box pair that carries no fact emits no node at all.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .boxes import Box

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:box:")        # transient per-page box-evidence instance namespace

BAND_BOXES_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "band-boxes.rq"


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
        if box.x0 <= w.x0 and w.x1 <= box.x1 and box.top <= w.top and w.bottom <= box.bottom
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
