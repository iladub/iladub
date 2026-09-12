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
