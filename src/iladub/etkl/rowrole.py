"""rowrole — loop C NEURAL header-region row roles: propose -> tile+conserve oracle -> promote.

§8 gate: this module hosts the NEURAL slice. WHICH role a header-region row has is NOT decided
here — a RowRoleProposer (BAML, injected) proposes it and region_tiles (SHACL: the nine tiling
shapes, including HeaderContentConservedShape) disposes it; a legal, lossless reading is admitted
only as a PromotionDecision proposition (§3).

Why NEURAL and not geometry: loop B proved a leaked caption and a genuinely-ambiguous off-center
merge are structurally identical (both are overlapping top rows), so no geometric peel is sound;
and even headers.header_rows_of's adaptive `gap < lead` wrap gate (the tuned `0.9 x lead` margin
was already retired in B3, 2026-07-22, commit 947f6fa) cannot fire when a document's header
leading equals its body leading (measured on GrainCorp: 6.6pt wrap gaps vs a 6.48pt band `lead`,
so `6.6 < 6.48` is false). Both are reading
judgments — a threshold, adaptive or not, cannot decide them.

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

TAB = Namespace("https://w3id.org/iladub/tab#")

ROLES = ("furniture", "continuation", "level")


def _column_containing(x: float, boundaries) -> int | None:
    """The column whose half-open [b[i], b[i+1]) contains x, or None if x lies outside the grid.

    Deliberately NOT regions.column_of: that function CLAMPS an out-of-range x onto the last
    column, which would silently weld a page-margin caption fragment onto the rightmost label
    (a guessed placement the tiling and conservation oracles both miss, because covers are
    unchanged and the label still CONTAINS the text). This mirrors header-covers.rq exactly —
    pure containment, no fallback — so a fragment outside every column is refused, not placed.
    """
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= x < boundaries[i + 1]:
            return i
    return None


def row_role_context(header_rows, grid) -> dict:
    """The proposer's inputs, read off the header rows. Reports geometry; decides nothing.

    rows              — the NON-LEAF rows' cell texts, top to bottom.
    leaf_labels       — the leaf (bottom) row's cell texts, left to right.
    row_columns       — per non-leaf cell, the column index containing its ink center, using the
                        same half-open containment header-covers.rq uses for leaf labels (no
                        clamp), so the model can see WHICH label a fragment would complete. -1
                        means the cell's ink center lies outside every column (e.g. a
                        page-margin-flush leaked line).
    merge_candidates  — parallel to `rows`: per non-leaf cell, what a 'continuation' reading would
                        produce ({column, leaf_label, merged}), or None when the cell's ink center
                        lies in no column or that column carries no leaf label. This is the
                        evidence that separates the otherwise indistinguishable pair: a genuine
                        short merged parent ('WIDE' over 'Val') and a wrap fragment ('Date of
                        Grain' over 'Commencement') have IDENTICAL geometry — both have
                        single-column ink above a leaf label in that column — and differ only in
                        whether the joined text reads as one column name (spec §2 Finding 3).
    row_cell_counts   — cells per non-leaf row.
    leaf_column_count — number of leaf cells. With row_cell_counts this carries the
                        solitary-parent reasoning in RAW form: one cell over many columns is more
                        often a title than a group label.

    Deliberately NOT reported: _covers_for_cell's symmetrized cover set. That is the function that
    fabricated 'Date of Grain -> covers 1..12' from ink touching one column, so reporting it would
    hand the proposer the very artefact that misleads. Counts are exact and underived.

    `merged` is computed per cell IN ISOLATION. When several continuation rows land in the same
    column, build_row_reading composes them top-to-bottom ('Date of Grain' + 'Loading' +
    'Commencement'), so a single cell's `merged` is a FRAGMENT of the final label, not the final
    label — hence 'candidates'.

    Returns empty lists for an empty header_rows (nothing to read, nothing to decide).
    """
    if not header_rows:
        return {"rows": [], "leaf_labels": [], "row_columns": [],
                "merge_candidates": [], "row_cell_counts": [], "leaf_column_count": 0}
    b = grid.boundaries
    non_leaf = list(header_rows[:-1])
    leaf_row = header_rows[-1]

    # column -> leaf label, placed by the same containment rule build_row_reading uses.
    leaf_by_col: dict[int, str] = {}
    for c in leaf_row:
        col = _column_containing((c.x0 + c.x1) / 2.0, b)
        if col is not None:
            leaf_by_col.setdefault(col, c.text)

    row_columns = []
    merge_candidates = []
    for row in non_leaf:
        cols = []
        cands = []
        for c in row:
            col = _column_containing((c.x0 + c.x1) / 2.0, b)
            cols.append(-1 if col is None else col)
            if col is None or col not in leaf_by_col:
                cands.append(None)          # unplaceable -> no candidate, never a guess
            else:
                label = leaf_by_col[col]
                cands.append({"column": col, "leaf_label": label,
                              "merged": (c.text + " " + label).strip()})
        row_columns.append(cols)
        merge_candidates.append(cands)

    return {
        "rows": [[c.text for c in row] for row in non_leaf],
        "leaf_labels": [c.text for c in leaf_row],
        "row_columns": row_columns,
        "merge_candidates": merge_candidates,
        "row_cell_counts": [len(row) for row in non_leaf],
        "leaf_column_count": len(leaf_row),
    }


def build_row_reading(header_rows, grid, roles):
    """Rewrite the header tree under a proposed role vector. Pure structural rewrite — no
    geometry decision, no tuned constant. Returns (nodes, captions, source_cells), or None to
    REFUSE (an empty header_rows, a malformed vector, or a continuation fragment that cannot be
    placed — its ink center lies in no column at all, or in a column no leaf label covers).

    level        -> the row stays a header level and flows through the UNCHANGED
                    _covers_for_cell + repair_coverage + resolve_narrow_flanks pipeline, so
                    genuine merged parents (the 'Prior Visit' pivot shape) are untouched.
    continuation -> the row contributes NO level; its cells' texts are prefixed, in top-to-bottom
                    source order, onto the leaf label covering the column that CONTAINS each
                    cell's ink center (no clamp — a cell outside every column refuses the whole
                    reading rather than being welded onto an unrelated label). Collected first
                    and applied once, so multiple continuation rows compose in reading order
                    ('Date of Grain' + 'Loading' + 'Commencement').
    furniture    -> the row contributes NO level; its cells become tab:RegionCaption records, so
                    the text is CARRIED, never dropped (CLAUDE.md §5/§7).

    The leaf row is never classified — it is always the leaf, and its covering stays loop B's
    header-covers.rq AXIOM.
    """
    if not header_rows:
        return None                            # nothing to read -> refuse

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
            col = _column_containing((cell.x0 + cell.x1) / 2.0, b)
            if col is None:
                return None                    # ink center outside every column -> refuse
            extra.setdefault(col, []).append(cell.text)

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


def resolve_header_row_roles(graph, hreg, band, table_uri, doc_uri, page, proposer):
    """NEURAL propose -> SHACL-oracle dispose -> promote for a header region whose geometric tree
    does not tile (loop C). The direct analogue of span.resolve_ambiguous_merge.

    ONE proposal, ONE disposal, NO search (see the module docstring: 'all furniture' is always
    legal, so search would converge on it and strip real header labels). Returns
    (asserted_token_count, (promotion_uri, ...)) on success, or None -> the caller escalates
    MERGE_AMBIGUOUS with `graph` untouched.

    Legality gates admission, never confidence: a reading whose scratch region fails region_tiles
    (any of the nine tiling shapes, including HeaderContentConservedShape) is refused regardless
    of proposal.confidence.
    """
    from dataclasses import replace as _replace
    from rdflib import Graph
    from .headers import header_rows_of
    from .holon import assert_hier_region
    from .promote import emit_row_role_promotion
    from .tiling import region_tiles

    header_rows = header_rows_of(band, hreg.grid, hreg.body_line)
    if len(header_rows) < 2:
        return None                            # no non-leaf row to classify -> caller escalates

    proposal = proposer.propose_header_row_roles(row_role_context(header_rows, hreg.grid))
    if proposal is None:
        return None                            # abstain -> escalate

    roles = tuple(proposal.roles)
    built = build_row_reading(header_rows, hreg.grid, roles)
    if built is None:
        return None                            # malformed / unplaceable -> escalate
    nodes, captions, source_cells = built

    scratch = Graph()
    n = assert_hier_region(scratch, _replace(hreg, tree=nodes), band, table_uri, doc_uri, page)
    emit_reading_evidence(scratch, table_uri, captions, source_cells)
    if n <= 0 or not region_tiles(scratch):
        return None                            # illegal or lossy -> oracle refuses -> escalate

    graph += scratch
    promo_uris = tuple(
        emit_row_role_promotion(graph, table_uri, r, role, [c.text for c in header_rows[r]], proposal)
        for r, role in enumerate(roles)
    )
    return n, promo_uris
