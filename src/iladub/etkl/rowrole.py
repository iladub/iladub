"""rowrole — loop C NEURAL header-region row roles: propose -> tile+conserve oracle -> promote.

§8 gate: this module hosts the NEURAL slice. WHICH role a header-region row has is NOT decided
here — a RowRoleProposer (BAML, injected) proposes it and region_tiles (SHACL: the eight tiling
shapes + HeaderContentConservedShape) disposes it; a legal, lossless reading is admitted only as a
PromotionDecision proposition (§3).

Why NEURAL and not geometry: loop B proved a leaked caption and a genuinely-ambiguous off-center
merge are structurally identical (both are overlapping top rows), so no geometric peel is sound;
and headers.header_rows_of's 0.9x-lead wrap threshold cannot fire when a document's header leading
equals its body leading (measured on GrainCorp: 6.6pt vs 6.5pt). Both are reading judgments.

The honest limit (spec §2 Finding 5): tiling CANNOT discriminate 'furniture' from 'continuation' —
both readings tile, and both conserve (furniture text is carried as a caption). That residue is
irreducibly NEURAL; the epistemics (proposition + accountable promotion + recorded rationale)
govern it, not an oracle. Hence: ONE proposal, ONE disposal, NO search — 'all furniture' is always
legal, so any search over the role space would converge on it and strip real header labels.

row_role_context and build_row_reading are pure structural reads/rewrites: no geometry decision,
no tuned constant.
"""
from __future__ import annotations

from dataclasses import replace

from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .headers import _tree_from_rows
from .regions import column_of

TAB = Namespace("https://w3id.org/iladub/tab#")

ROLES = ("furniture", "continuation", "level")


def row_role_context(header_rows, grid) -> dict:
    """The proposer's inputs, read off the header rows. Reports geometry; decides nothing.

    rows         — the NON-LEAF rows' cell texts, top to bottom.
    leaf_labels  — the leaf (bottom) row's cell texts, left to right.
    row_columns  — per non-leaf cell, the column index containing its ink center (the same
                   half-open containment header-covers.rq uses for leaf labels), so the model can
                   see WHICH label a fragment would complete.
    """
    b = grid.boundaries
    non_leaf = list(header_rows[:-1])
    return {
        "rows": [[c.text for c in row] for row in non_leaf],
        "leaf_labels": [c.text for c in header_rows[-1]],
        "row_columns": [[column_of((c.x0 + c.x1) / 2.0, b) for c in row] for row in non_leaf],
    }


def build_row_reading(header_rows, grid, roles):
    """Rewrite the header tree under a proposed role vector. Pure structural rewrite — no
    geometry decision, no tuned constant. Returns (nodes, captions, source_cells), or None to
    REFUSE (a malformed vector, or a continuation fragment that cannot be placed).

    level        -> the row stays a header level and flows through the UNCHANGED
                    _covers_for_cell + repair_coverage + resolve_narrow_flanks pipeline, so
                    genuine merged parents (the 'Prior Visit' pivot shape) are untouched.
    continuation -> the row contributes NO level; its cells' texts are prefixed, in top-to-bottom
                    source order, onto the leaf label covering the column that contains each
                    cell's ink center. Collected first and applied once, so multiple continuation
                    rows compose in reading order ('Date of Grain' + 'Loading' + 'Commencement').
    furniture    -> the row contributes NO level; its cells become tab:RegionCaption records, so
                    the text is CARRIED, never dropped (CLAUDE.md §5/§7).

    The leaf row is never classified — it is always the leaf, and its covering stays loop B's
    header-covers.rq AXIOM.
    """
    non_leaf = list(header_rows[:-1])
    if len(roles) != len(non_leaf) or any(r not in ROLES for r in roles):
        return None                            # malformed vector -> refuse

    kept = [row for row, role in zip(non_leaf, roles) if role == "level"] + [header_rows[-1]]
    nodes = list(_tree_from_rows(kept, grid))
    leaf_lvl = len(kept) - 1

    # Collect continuation fragments per column FIRST (top-to-bottom), then prefix once.
    b = grid.boundaries
    extra: dict[int, list[str]] = {}
    for row, role in zip(non_leaf, roles):
        if role != "continuation":
            continue
        for cell in row:
            extra.setdefault(column_of((cell.x0 + cell.x1) / 2.0, b), []).append(cell.text)

    for col, texts in extra.items():
        tgt = next((i for i, n in enumerate(nodes)
                    if n.level == leaf_lvl and col in n.covers), None)
        if tgt is None:
            return None                        # unplaceable continuation -> refuse (spec §3.1)
        merged = (" ".join(texts) + " " + nodes[tgt].text).strip()
        nodes[tgt] = replace(nodes[tgt], text=merged)

    captions = tuple((r, cell.text)
                     for r, (row, role) in enumerate(zip(non_leaf, roles))
                     if role == "furniture"
                     for cell in row)
    source_cells = tuple((r, cell.text)
                         for r, row in enumerate(header_rows)
                         for cell in row)
    return tuple(nodes), captions, source_cells


def emit_reading_evidence(g, table_uri, captions, source_cells):
    """Commit the reading's accountability evidence: one tab:RegionCaption per furniture cell
    (so furniture text is carried, not dropped) and one tab:HeaderSourceCell per header-region
    cell — the target of tab:HeaderContentConservedShape, which refuses any reading that loses a
    word. Region-bound; the region is the closure boundary."""
    for k, (row, text) in enumerate(captions):
        cap = URIRef("%s-cap%d" % (table_uri, k))
        g.add((cap, RDF.type, TAB.RegionCaption))
        g.add((cap, TAB.captionText, Literal(text)))
        g.add((cap, TAB.captionRow, Literal(row, datatype=XSD.integer)))
        g.add((table_uri, TAB.hasCaption, cap))
    for k, (row, text) in enumerate(source_cells):
        sc = URIRef("%s-hsc%d" % (table_uri, k))
        g.add((sc, RDF.type, TAB.HeaderSourceCell))
        g.add((sc, TAB.sourceText, Literal(text)))
        g.add((sc, TAB.sourceRow, Literal(row, datatype=XSD.integer)))
        g.add((table_uri, TAB.hasHeaderSourceCell, sc))
