"""span — loop B1.3 NEURAL narrow-flank merge resolution: propose -> tile-oracle -> promote.

§8 gate: this module hosts the NEURAL slice. The reading is NOT decided by geometry here — a
SpanProposer (BAML, injected) proposes it and region_tiles (SHACL) disposes it; a legal reading
is admitted only as a PromotionDecision proposition (§3). build_reading/flank_context are pure
structural rewrites (no geometry constant); the decision lives in the injected proposer + oracle.
"""
from __future__ import annotations

from dataclasses import replace

from .headers import HeaderNode


def build_reading(tree, node_idx, flank, choice):
    """Rewrite the resolved header tree under a proposed reading for the tied flank column.

    absorb     -> the ambiguous node keeps the flank in its covers (clear the ambiguity flags).
    standalone -> drop the flank from the node's covers; the flank becomes a top-level leaf.
                  If a deeper node already covers exactly (flank,) under this node, re-root it
                  (parent=None, level 0); otherwise (a header-empty flank) append a new empty
                  level-0 leaf covering (flank,). assert_hier_region's orphan-promotion then
                  emits it as a standalone leaf, satisfying the tiling shapes.

    Pure structural rewrite — no geometry, no tuned constant. Returns the new tree tuple."""
    out = list(tree)
    n = out[node_idx]
    if choice == "absorb":
        out[node_idx] = replace(n, ambiguous=False, ambiguous_flank=None)
        return tuple(out)
    # standalone
    new_covers = tuple(c for c in n.covers if c != flank)
    out[node_idx] = replace(n, covers=new_covers, ambiguous=False, ambiguous_flank=None)
    for i, m in enumerate(out):
        if m.covers == (flank,) and m.parent == node_idx:
            out[i] = replace(m, parent=None, level=0)
            return tuple(out)
    out.append(HeaderNode(0, (flank,), "", None))
    return tuple(out)


def flank_context(tree, node_idx, flank):
    """Build the SpanProposer inputs from the tree: the spanning label, the neighbouring leaf
    sub-labels (deeper nodes covering a single column under the span, in column order), the
    flank's own leaf label (empty for a header-empty flank), and the flank side."""
    n = tree[node_idx]
    span_cols = [c for c in n.covers if c != flank]
    leaf_labels = []
    for c in sorted(span_cols):
        for m in tree:
            if m.parent == node_idx and m.covers == (c,):
                leaf_labels.append(m.text)
                break
    flank_label = ""
    for m in tree:
        if m.covers == (flank,) and m.parent == node_idx:
            flank_label = m.text
            break
    side = "right" if flank == max(n.covers) else "left"
    return {"span_label": n.text, "leaf_labels": leaf_labels,
            "flank_label": flank_label, "flank_side": side}


def resolve_ambiguous_merge(graph, hreg, band, table_uri, doc_uri, page, proposer):
    """NEURAL propose -> SHACL-oracle dispose -> promote for a narrow-flank merge tie (B1.3).

    For each header node B1.2 flagged with an `ambiguous_flank`, ask the proposer for a reading,
    build that reading, and tile-check it on a scratch graph (region_tiles). ALL flagged nodes
    must resolve legally, or the whole region stays escalated (return None, graph untouched).
    On success, commit the (last) legal reading's region + one promotion per resolved flank into
    `graph` and return (asserted_token_count, (promotion_uri, ...)).

    Legality gates admission — never confidence: a proposal whose scratch region fails region_tiles
    is refused regardless of proposal.confidence."""
    from dataclasses import replace
    from rdflib import Graph
    from .holon import assert_hier_region
    from .tiling import region_tiles
    from .promote import emit_span_promotion

    flagged = [i for i, n in enumerate(hreg.tree) if n.ambiguous_flank is not None]
    if not flagged:
        return None                                  # not a narrow-flank tie -> caller escalates

    tree = hreg.tree
    promos = []
    for idx in flagged:
        flank = tree[idx].ambiguous_flank
        proposal = proposer.propose_header_span(flank_context(tree, idx, flank))
        if proposal is None or proposal.choice not in ("absorb", "standalone"):
            return None                              # abstain / malformed -> escalate
        tree = build_reading(tree, idx, flank, proposal.choice)
        promos.append((idx, flank, proposal))

    reading = replace(hreg, tree=tree)
    scratch = Graph()
    n = assert_hier_region(scratch, reading, band, table_uri, doc_uri, page)
    if n <= 0 or not region_tiles(scratch):
        return None                                  # illegal reading -> oracle refuses -> escalate

    graph += scratch
    promo_uris = tuple(
        emit_span_promotion(graph, table_uri, hreg.tree[idx].text, flank, prop.choice, prop)
        for idx, flank, prop in promos
    )
    return n, promo_uris
