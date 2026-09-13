"""donation — grid donation (R201/R203): the donor relation's reader, and (Task 3) the
donated reading and its disposal.

CLAUDE.md §8 CLASSIFICATION, per function, stated here and restated on each:

- `donors_for` — PROCEDURAL glue over an AXIOM. The relation itself is
  `vocab/queries/grid-donation.rq` (derivation, open world); this function builds no
  facts and takes no decision. It binds the continuation band and its leaf-column count,
  runs the query, and returns the derived donor indices ascending. The precedent is
  `sectiongraph.section_candidates` / `merge_run_candidates`: the query decides, Python
  assembles.
- `head_line_refusals` — PROCEDURAL glue over two shipped derivations. It re-identifies a
  band's line 0 among the page's text lines BY INK and reads the page datagrid's own
  verdict on it. It derives nothing and carries no constant; every value it returns was
  written by `derive_data_grid`.
- `donated_region` — PROCEDURAL region construction, the same one every branch of
  `compile_tables` does (`assign_cells` under a grid). It decides nothing: WHICH donor,
  and whether the result may be read at all, are settled elsewhere.
- `donation_admissible` — the shipped closed-world MEMBRANE, reused and not copied
  (`compile.merged_run_admissible` is the precedent, down to the placeholder doc URI).
  This is the disposal the §8 gate requires of a proposal.
- `offer` — PROCEDURAL composition. It takes no reading judgement of its own: it requires
  the derivation to name exactly one donor (DECISION E) and the membrane to accept the
  reading, and returns None otherwise.

The split this module exists to keep is the one the §8 gate turns on. The DERIVATION
enumerates candidates on present facts; the DISPOSAL is the shipped closed-world membrane
(Task 3). A refused donation is INVISIBLE — no triple, no decision record, no report — so
that a page whose donation is refused is isomorphic to a page where none was ever proposed
(R165 spec § 3.2).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping, Sequence

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD

from .bands import Band
from .grid import _rule_boundaries, infer_leaf_grid
from .regions import Cell, ClassifiedRegion, RegionKind, assign_cells

GRID_DONATION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-donation.rq"

# The scratch document a DONATION proposal is offered against. It never reaches a graph
# that survives, exactly as compile._RUN_PROPOSAL_DOC does not (compile.py:449-453, where
# the same placeholder was measured across all 14 corpus runs against three unrelated
# (doc, fragment) pairs with 0 verdicts differing). RE-MEASURED for this disposal — see the
# task report — because "no stage reads the URI" is a claim about THIS chain, not that one.
_DONATION_PROPOSAL_DOC = URIRef("urn:iladub:donation-proposal")


def donors_for(evidence: Graph, idx: int, ncols: int) -> tuple[int, ...]:
    """The band indices of every donor `grid-donation.rq` derives for the continuation
    band `idx` reading `ncols` leaf columns — ascending, and EVERY one of them.

    PROCEDURAL glue over an AXIOM (module docstring). The four clauses live in the query;
    nothing here filters, orders or prefers. Returning every qualifying donor rather than
    one is deliberate: spec § 3(b) refused an ordinal rule, and `offer` requires
    uniqueness (DECISION E), so a page with two qualifying donors must be visible AS two
    here or that refusal could not be pinned.

    `idx` and `ncols` are bound per-call rather than emitted as facts for every band: the
    leaf-column count is already derived once per band by the compile loop, and emitting
    it up front would run `infer_leaf_grid` a second time per band — the duplication R168
    records. MEASURED (plan rule 3, rdflib 7.6.0): `initBindings` binds `?b` even though
    it appears only inside `FILTER(?a < ?b)`, so no `VALUES` clause is needed; the null
    control is that a binding which matches nothing returns nothing rather than being
    ignored.

    Both literals are minted with an explicit `xsd:integer` datatype because the emitter
    mints `tab:bandIndex` and `tab:leafColumnCount` that way, and `?n`'s join is a TERM
    match — an untyped binding would silently match nothing."""
    rows = evidence.query(
        GRID_DONATION_RQ.read_text(),
        initBindings={
            "b": Literal(idx, datatype=XSD.integer),
            "n": Literal(ncols, datatype=XSD.integer),
        },
    )
    return tuple(sorted(int(row.a) for row in rows))


def _ink_key(line) -> str:
    """A line's identity BY INK: its words' text concatenated in x order, whitespace
    removed ([[R202]], Global Constraint 5).

    NEVER by index. A band's words are word GROUPS (`1 736 124` is one word) while a
    page's are raw, so raw word-tuple equality re-identified 0 of 12 bands in
    `scripts/donor_header_criterion.py`, whose `key` this reproduces exactly."""
    return "".join(w.text for w in sorted(line.words, key=lambda w: w.x0)).replace(" ", "")


def head_line_refusals(pdf_path: str, page_number: int,
                       bands: Sequence[Band]) -> dict[int, str]:
    """For each band that owns a leaf-boundary vector, the page datagrid's refusal string
    for the page text line that band's line 0 re-identifies to BY INK — where there is one.

    This is the R203 licence's carrier (DECISION C). It reads two shipped derivations and
    decides nothing: the refusal string is the datagrid's own, and the caller
    (`sectiongraph.donor_evidence`) copies it verbatim.

    FOUR WAYS TO ABSTAIN, all silent, none inferring: no datagrid on the page; a line 0
    whose ink key matches no page line or MORE THAN ONE (a non-unique match emits nothing,
    Global Constraint 5); a line the datagrid ADMITTED as a body row (a body-row verdict
    is not a refusal and must never be read as one); and a line it neither admitted nor
    recorded a refusal for. In every case the band simply carries no licence and the query
    refuses it.

    LAZY BY M1's MEASUREMENT: returns `{}` WITHOUT calling `derive_data_grid` when no band
    on the page owns a vector. The datagrid costs 4.6 s over all 27 corpus pages against
    35.8 s of band-building, and only 7 bands corpus-wide own a vector, so the whole cost
    is avoided on every page that could not donate anyway.

    The page-line list is EXACTLY `derive_data_grid`'s own (`datagrid.py:321-322`), and it
    has to be: `grid.rows` and `grid.refusals` are keyed by position in that list, so a
    differently-built list would silently read another line's verdict."""
    from .datagrid import derive_data_grid
    from .geometry import extract_words, text_lines

    donors = [i for i, b in enumerate(bands)
              if b.lines and _rule_boundaries(b) is not None]
    if not donors:
        return {}
    grid = derive_data_grid(pdf_path, page_number)
    if grid is None:
        return {}
    lines = [l for l in sorted(text_lines(extract_words(pdf_path, page_number)),
                               key=lambda l: l.top) if l.words]
    keys = [_ink_key(l) for l in lines]

    out: dict[int, str] = {}
    for i in donors:
        k = _ink_key(bands[i].lines[0])
        hits = [j for j, kk in enumerate(keys) if kk == k]
        if len(hits) != 1 or hits[0] in grid.rows:
            continue
        refusal = grid.refusals.get(hits[0])
        if refusal is not None:
            out[i] = refusal
    return out


def donated_region(bands: Sequence[Band], donor_idx: int, idx: int) -> ClassifiedRegion:
    """The reading a donation proposes: band `idx`'s ink, read under band `donor_idx`'s
    grid and labels, with every one of its own lines shifted down one row (DECISION D).

    The continuation KEEPS ITS OWN BAND. The donor's line 0 becomes row 0 (the labels),
    carrying the DONOR's word boxes, and the continuation's line 0 — which today is
    mis-read as a header — becomes row 1, a data row.

    NOT the spike's construction. `scripts/grid_donation_spike.py` prepends the donor's
    `Line` to the continuation band, which would put the donor's 9 words inside five
    different bands' ink and book them five times under R176's ledger (`compile.py:276`,
    `_book_recovered_ink` reads THIS band's words). Here the label cells carry bboxes that
    lie outside the continuation band entirely, so that ledger books 0 recovered words for
    them.

    `Cell` is frozen, so the shift is `dataclasses.replace`, never mutation."""
    grid = infer_leaf_grid(bands[donor_idx])
    head = tuple(c for c in assign_cells(bands[donor_idx], grid) if c.row == 0)
    body = tuple(replace(c, row=c.row + 1) for c in assign_cells(bands[idx], grid))
    return ClassifiedRegion(RegionKind.RECORD_TABLE, bands[idx], grid, head + body, "donated")


def donation_admissible(region: ClassifiedRegion, page_number: int) -> bool:
    """Does the SHIPPED membrane accept the donated reading? The disposal, and the whole
    of it.

    A single named module-level function so a test can patch it, exactly as
    `compile.merged_run_admissible` is (`compile.py:456`). It offers `region` to
    `assert_record_region` on a SCRATCH graph that is discarded either way, and requires
    both `region_tiles` and that every DATA cell round-trips into its own leaf column.

    THE TILING CLAUSE LIVES HERE, NOT IN THE DERIVATION (DECISION A). Deriving it in
    SPARQL would put `COORD_EPS` into a query as a numeric literal — which the §8 gate
    forbids — to evaluate a predicate with zero degrees of freedom. The corpus measures
    the two formulations identical (plan M3: the same 5 pairs accepted either way), and
    the synthetic straddling page pins that a straddle is refused HERE rather than by the
    query.

    Row 0 is excluded from the round-trip because it is the DONOR's ink, measured against
    the donor's own grid by construction; the question this asks is whether the
    CONTINUATION's words place into that grid.

    A refusal costs nothing observable: the scratch graph is dropped, no decision record
    is minted, no report is written (Global Constraint 6)."""
    from .holon import assert_record_region
    from .roundtrip import cell_round_trips
    from .tiling import region_tiles

    scratch = Graph()
    assert_record_region(scratch, region, URIRef(f"{_DONATION_PROPOSAL_DOC}#table"),
                         _DONATION_PROPOSAL_DOC, page_number)
    if not region_tiles(scratch):
        return False
    return all(cell_round_trips(c, region.grid.boundaries)
               for c in region.cells if c.row > 0)


@dataclass(frozen=True)
class Donation:
    """An ACCEPTED donation: the reading to compile, and the donor it came from. It exists
    only on acceptance — a refusal returns None and leaves no trace at all."""
    region: ClassifiedRegion
    donor_index: int


def offer(bands: Sequence[Band], idx: int, region: ClassifiedRegion, evidence: Graph,
          page_number: int) -> Donation | None:
    """Propose the donated reading for band `idx`, or None.

    THE DONOR MUST BE UNIQUE (DECISION E). `donors_for` returns every qualifying donor;
    two of them is a page this relation cannot read, and the band then compiles exactly as
    it does today. Spec § 3(b) measured uniqueness on the corpus (`multi = 0`) and REFUSED
    an ordinal rule — taking "the first" or "the nearest" would be inventing a reading the
    evidence does not support.

    This function composes and judges nothing: the derivation named the candidates, the
    membrane disposed of the reading, and both are visible above it."""
    if region.kind is not RegionKind.RECORD_TABLE or region.grid is None:
        return None
    donors = donors_for(evidence, idx, region.grid.ncols)
    if len(donors) != 1:
        return None
    donated = donated_region(bands, donors[0], idx)
    if not donation_admissible(donated, page_number):
        return None
    return Donation(donated, donors[0])


# =============================================================================================
# SPAN donation (R211) — the SECOND relation. Grid donation carries a header at the SAME leaf
# column count; this one carries a COARSER header, each of whose drawn intervals spans a run of
# the continuation's columns. Same evidence graph, same licence, one clause different.
#
# CLAUDE.md §8 CLASSIFICATION, per function, as above:
#   `span_donors_for`      PROCEDURAL glue over an AXIOM (vocab/queries/span-donation.rq).
#   `span_tree`            PROCEDURAL assembly over an AXIOM (vocab/queries/span-covers.rq) —
#                          the query decides WHICH columns each label heads; this joins the
#                          words the query placed in one interval and reads their geometry.
#   `span_region`          PROCEDURAL region construction. It decides nothing.
#   `span_donation_admissible`  the shipped closed-world MEMBRANE, reused and not copied.
#   `span_offer`           PROCEDURAL composition; uniqueness (DECISION E) and nothing else.
# =============================================================================================

SPAN_DONATION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "span-donation.rq"


def span_donors_for(evidence: Graph, idx: int) -> tuple[int, ...]:
    """Every band `span-donation.rq` derives as a SPANNING donor for band `idx` — ascending.

    PROCEDURAL glue over an AXIOM. The four clauses live in the query; nothing here filters,
    orders or prefers, and `span_offer` requires uniqueness, so a page with two qualifying
    donors must be visible AS two here or that refusal could not be pinned.

    NO `ncols` BINDING, and its absence is the whole difference from `donors_for`: grid
    donation binds the continuation's leaf-column count because its relation joins on equality
    of counts, while this relation compares the two bands' drawn BOUNDARY SETS, and both sets
    are already facts in the evidence graph. The count is not merely unnecessary here — binding
    it would re-impose the equality the strict-subset clause exists to replace."""
    rows = evidence.query(
        SPAN_DONATION_RQ.read_text(),
        initBindings={"b": Literal(idx, datatype=XSD.integer)},
    )
    return tuple(sorted(int(row.a) for row in rows))


def span_tree(donor: Band, recipient_grid, page: int) -> tuple:
    """The donor's labels as level-0 childless header nodes over the recipient's leaf columns.

    THE GROUPING IS THE QUERY'S, NOT `group_wrapped`'s, and that is a correction measured
    before this call was written. `cells.group_wrapped(donor, recipient_grid)` groups the
    donor's words by the RECIPIENT's columns, which splits the single label 'Port Kembla' into
    two cells in two different columns — and a tree built from that emits TWO header nodes over
    one drawn interval, the reading `tests/tab-span-doubled-label-leak.ttl` exists to refuse.
    Words are therefore grouped by the interval `span-covers.rq` placed them in: same covers
    tuple, same label. The decision stays in the query; only the join is here.

    NO LEVEL-1 NODES (DECISION C). The donor drew one row of labels and the recipient's own
    line 0 is a data row, so a second header level would be a node with no ink behind it —
    which CLAUDE.md § Core design principles 7 forbids. `tests/tab-span-invented-child-leak.ttl`
    is the negative for what the membrane does if one is minted anyway.

    `page` is PASSED, never read off a Word: a `Word` may or may not carry `.page` (the
    synthetic bands tests build do not), and defaulting to 0 would silently assert page 0 for a
    band compiled from page 5. Provenance to the page (CLAUDE.md §6) is not a place to guess.

    Returns () when the derivation placed no label — the honest abstain, which `span_region`
    turns into a refusal."""
    from .headers import HeaderNode
    from .spangraph import SPAN_COVERS_RQ, run_span_covers, span_evidence

    if not donor.lines:
        return ()
    covers = run_span_covers(SPAN_COVERS_RQ, span_evidence(donor, recipient_grid))
    if not covers:
        return ()
    words = sorted(donor.lines[0].words, key=lambda w: w.x0)
    by_span: dict[tuple[int, ...], list] = {}
    for k, cols in covers.items():
        by_span.setdefault(cols, []).append(words[k])

    nodes = []
    for cols in sorted(by_span, key=lambda c: c[0]):
        ws = sorted(by_span[cols], key=lambda w: w.x0)
        x0 = min(w.x0 for w in ws)
        x1 = max(w.x1 for w in ws)
        nodes.append(HeaderNode(
            0, cols, " ".join(w.text for w in ws), None, (x0 + x1) / 2.0,
            x0=x0, top=min(w.top for w in ws), x1=x1,
            bottom=max(w.bottom for w in ws), page=page))
    return tuple(nodes)


def span_region(bands: Sequence[Band], donor_idx: int, idx: int, page: int):
    """The reading a span donation proposes: band `idx`'s ink read under its OWN leaf grid,
    with band `donor_idx`'s labels as the column header tree (DECISION C).

    A `HierRegion`, not a `ClassifiedRegion`: the labels SPAN, so the reading is hierarchical
    even though the tree is one level deep. `body_line=0` because the recipient's line 0 is a
    data row — the donor supplied the only header row there is.

    THE GRID IS `recover_leaf_grid`'s, the same one `classify_hierarchical` uses, never
    `classify`'s `infer_leaf_grid`: the covering was derived against the recipient's leaf
    boundaries and the reading must be asserted against the same ones, or the columns a label
    was measured to head would not be the columns it is emitted over.

    NO PARTITION CHECK HERE, deliberately. Whether every leaf column ends up headed exactly
    once is the MEMBRANE's question (`tab:CoverageShape`, `tab:UnambiguousAccessShape`), and
    `span_donation_admissible` below asks it on the real emitted graph. A Python re-check would
    be a second opinion that could drift from the shape, and the clause that actually keeps a
    half-covered reading off the page is clause (d) in the relation, which refuses such a donor
    before a tree is ever built.

    None when the donor placed no label, or the recipient has no body rows to read."""
    from .cells import recover_leaf_grid
    from .hierarchical import HierRegion
    from .rows import logical_rows

    recipient = bands[idx]
    if not recipient.lines:
        return None
    grid = recover_leaf_grid(recipient)
    tree = span_tree(bands[donor_idx], grid, page)
    if not tree:
        return None
    rows = logical_rows(recipient, grid, recipient.lines[0].top)
    if rows is None:
        return None
    return HierRegion(grid=grid, tree=tree, rows=rows, body_line=0)


def span_donation_admissible(region, band: Band, page_number: int) -> bool:
    """Does the SHIPPED membrane accept the spanning reading? The disposal, and the whole of it.

    The sibling of `donation_admissible`, and patchable at module level for the same reason. It
    offers the reading to `assert_hier_region` on a SCRATCH graph that is discarded either way,
    and requires both that entries were asserted at all and that `region_tiles` accepts.

    THE ENTRY COUNT IS PART OF THE TEST, not decoration: `assert_hier_region` escalates the
    whole region and returns 0 when the round-trip refuses it, and a graph carrying only an
    escalation can still tile vacuously. `compile_tables` guards its own record-table path the
    same way (`tiles = region_tiles(scratch) if n else None`).

    NO NEW SHAPE IS AUTHORED FOR THIS READING (DECISION C). Three childless spanning nodes over
    six leaf columns is precisely the shape `tab:UnambiguousAccessShape` defines as correct — it
    calls a leaf header one that nothing points at via `tab:parentHeader` — so the shipped
    tiling membrane already accepts the reading and already refuses both ways it can go wrong
    (`examples/tables/span-donation-conformant.ttl` and its two negatives).

    A refusal costs nothing observable: the scratch graph is dropped, no decision record is
    minted, no report is written."""
    from .holon import assert_hier_region
    from .tiling import region_tiles

    scratch = Graph()
    asserted = assert_hier_region(scratch, region, band,
                                  URIRef(f"{_DONATION_PROPOSAL_DOC}#table"),
                                  _DONATION_PROPOSAL_DOC, page_number)
    return bool(asserted) and region_tiles(scratch)


@dataclass(frozen=True)
class SpanDonation:
    """An ACCEPTED span donation: the hierarchical reading to compile, and the donor it came
    from. It exists only on acceptance — a refusal returns None and leaves no trace at all."""
    region: object                 # a hierarchical.HierRegion
    donor_index: int


def span_offer(bands: Sequence[Band], idx: int, evidence: Graph,
               page_number: int) -> "SpanDonation | None":
    """Propose the spanning reading for band `idx`, or None.

    THE DONOR MUST BE UNIQUE (DECISION E, reused verbatim from grid donation). `span_donors_for`
    returns every qualifying donor; two of them is a page this relation cannot read, and the
    band then compiles exactly as it does today. No ordinal rule is added — taking "the first"
    or "the nearest" would be inventing a reading the evidence does not support.

    It takes no `region`, unlike `offer`: grid donation reads the continuation's leaf-column
    count off the already-classified region to bind its equality clause, and this relation has
    no such clause. The caller's classification still governs WHERE the offer is made — the
    seam in `compile_tables` offers it only on a band whose own reading would otherwise
    proceed — but it is not an input to the relation.

    This function composes and judges nothing: the derivation named the candidates, the covering
    derivation placed the labels, and the membrane disposed of the reading."""
    donors = span_donors_for(evidence, idx)
    if len(donors) != 1:
        return None
    region = span_region(bands, donors[0], idx, page_number)
    if region is None:
        return None
    if not span_donation_admissible(region, bands[idx], page_number):
        return None
    return SpanDonation(region, donors[0])
