"""donation — grid donation (R201/R203): the donor relation's reader, and (Task 3) the
donated reading and its disposal.

CLAUDE.md §8 CLASSIFICATION, per function, stated here and restated on each:

- `donors_for` — PROCEDURAL glue over an AXIOM. The relation itself is
  `vocab/queries/grid-donation.rq` (derivation, open world); this function builds no
  facts and takes no decision. It binds the continuation band and its leaf-column count,
  runs the query, and returns the derived donor indices ascending. The precedent is
  `sectiongraph.section_candidates` / `merge_run_candidates`: the query decides, Python
  assembles.

The split this module exists to keep is the one the §8 gate turns on. The DERIVATION
enumerates candidates on present facts; the DISPOSAL is the shipped closed-world membrane
(Task 3). A refused donation is INVISIBLE — no triple, no decision record, no report — so
that a page whose donation is refused is isomorphic to a page where none was ever proposed
(R165 spec § 3.2).
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import XSD

GRID_DONATION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-donation.rq"


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
