"""rowgroups — loop I: row groups derived from confirmed aggregation rows (AXIOM).

A confirmed tab:DetectedAggregationRow witnesses its group: label column = level,
tab:aggregates = members, and the KEY = the unique distinct non-blank member value in the
label column (row-group-key.rq). Nesting = strict member-set containment
(row-group-nesting.rq). §8: both decisions are SPARQL derivations (open world; the
uniqueness/containment guards are query-local NOT EXISTS — the table holon is the closure
boundary). This module is ENGINE GLUE only (bindings, triple merge, a parentHeader depth
walk) — the interpret.run pattern; it decides nothing.

LOOP N adds no law and changes no triple the page-local path writes: it splits the entry
point in two so the SAME derivation can run over a LOGICAL table (a continuation chain).
`derive_row_groups` mints its URIs from one table + indices as it always did;
`derive_row_groups_over` takes them as arguments, because on a chain the witness row, its
label column and its members can live in three different member tables. The KEY law then
runs in its logical formulation (row-group-key-logical.rq — the label column reached over
`tab:continuesColumn*` instead of bound directly), and the groups attach to the head.

Group nodes reuse the shipped row-header vocabulary (tab:HeaderNode + hasHeaderNode +
coversRow + parentHeader + headerLevel) so feed._row_header_path reads them unchanged, and
are ALSO typed tab:DerivedRowGroup: the membrane shape targets the subclass, and the
row-tiling triggers exclude derived-only trees (derived groups are carried annotations —
§5 — not a claimed row partition; coverage is honestly PARTIAL: aggregation rows and rows
of unconfirmed groups stay uncovered). hasLabel points at the SOURCE EntryCell that carries
the key — provenance to the page (§6) with no text duplication."""
from __future__ import annotations

import os
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
_QDIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def _query_text(name: str) -> str:
    return Path(os.path.join(_QDIR, name)).read_text(encoding="utf-8")


def derive_row_groups(g: Graph, table_uri: URIRef, agg: dict) -> int:
    """Derive one group node per confirmed aggregation row whose key is unique.

    `agg` is detect_aggregation_rows' return: {row_index: (label_col, measure_col,
    member_indices)}. Reads/writes `g` (the scratch graph inside the loop G backstop when
    the hierarchical path is gated). Returns the number of groups constructed.

    THE PAGE-LOCAL ENTRY POINT (loop I, unchanged behaviour): every URI it needs is a
    function of `table_uri` and a row/column INDEX, because a page-local aggregation's
    witness, label column and members all live in the one table. `derive_row_groups_over`
    is the same derivation with those URIs handed IN — see there for why the logical table
    (loop N) cannot mint them from indices."""
    witnesses = tuple((URIRef(f"{table_uri}-r{i}"),
                       URIRef(f"{table_uri}-c{agg[i][0]}"),
                       URIRef(f"{table_uri}-rg{i}")) for i in sorted(agg))
    return derive_row_groups_over(g, table_uri, witnesses)


def derive_row_groups_over(g: Graph, attach_to: URIRef, witnesses, key_query: str =
                           "row-group-key.rq") -> int:
    """The same loop-I derivation, URI-keyed: `witnesses` = ((agg_row, label_col, group), …).

    WHY THIS SHAPE (loop N). Over a continuation chain the confirmed aggregation row, its
    label column and its member rows can each live in a DIFFERENT member table, so nothing
    is a function of one table URI and an index any more: the caller resolves the three
    URIs (document.reconcile_chain_arithmetic does, from the merged graph) and the
    derivation is unchanged. `attach_to` is the table the group nodes hang off — the CHAIN'S
    HEAD at document level, the table itself page-locally — and it is also the holon the
    nesting query closes over (`row-group-nesting.rq` scopes every guard by `?tbl`), which
    is exactly right: one group set per LOGICAL table, whatever pages its members sit on.

    `key_query` selects which formulation of the KEY law runs — `row-group-key.rq` when the
    label column is one node, `row-group-key-logical.rq` when it is a `tab:continuesColumn`
    chain of them. Same law, different holon; both are AXIOMs and neither is a heuristic.
    `tab:coversRow` is always taken from the witness's CURRENT `tab:aggregates` edges, so a
    re-derivation after the document window rewrote an operand set can never carry a stale
    member (loop-N task 2 report, appendix (d)).

    `witnesses` is an ORDERED sequence: derivation is per-group independent, but iterating a
    fixed order keeps the run reproducible triple-for-triple."""
    key_q = _query_text(key_query)
    made = 0
    for arow, lcol_uri, grp in witnesses:
        hit = list(g.query(key_q, initBindings={"agg": arow, "lcol": lcol_uri}))
        if not hit:
            continue                    # no unique non-blank key -> no group (§7)
        _v, cell = hit[0]
        g.add((grp, RDF.type, TAB.HeaderNode))
        g.add((grp, RDF.type, TAB.DerivedRowGroup))
        g.add((attach_to, TAB.hasHeaderNode, grp))
        g.add((grp, TAB.hasLabel, cell))
        g.add((grp, PROV.wasDerivedFrom, arow))
        for m in g.objects(arow, TAB.aggregates):
            g.add((grp, TAB.coversRow, m))
        made += 1
    if made:
        parents = {}
        for child, parent in g.query(_query_text("row-group-nesting.rq"),
                                     initBindings={"tbl": attach_to}):
            g.add((child, TAB.parentHeader, parent))
            parents[child] = parent
        for grp in set(g.subjects(RDF.type, TAB.DerivedRowGroup)):
            if (attach_to, TAB.hasHeaderNode, grp) not in g:
                continue
            level, cur = 0, parents.get(grp)
            while cur is not None:
                level += 1
                cur = parents.get(cur)
            g.add((grp, TAB.headerLevel, Literal(level, datatype=XSD.integer)))
    return made
