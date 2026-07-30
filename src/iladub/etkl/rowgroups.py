"""rowgroups — loop I: row groups derived from confirmed aggregation rows (AXIOM).

A confirmed tab:DetectedAggregationRow witnesses its group: label column = level,
tab:aggregates = members, and the KEY = the unique distinct non-blank member value in the
label column (row-group-key.rq). Nesting = strict member-set containment
(row-group-nesting.rq). §8: both decisions are SPARQL derivations (open world; the
uniqueness/containment guards are query-local NOT EXISTS — the table holon is the closure
boundary). This module is ENGINE GLUE only (bindings, triple merge, a parentHeader depth
walk) — the interpret.run pattern; it decides nothing.

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
    the hierarchical path is gated). Returns the number of groups constructed."""
    key_q = _query_text("row-group-key.rq")
    made = 0
    for i in sorted(agg):
        label_col, _mcol, _members = agg[i]
        arow = URIRef(f"{table_uri}-r{i}")
        lcol_uri = URIRef(f"{table_uri}-c{label_col}")
        hit = list(g.query(key_q, initBindings={"agg": arow, "lcol": lcol_uri}))
        if not hit:
            continue                    # no unique non-blank key -> no group (§7)
        _v, cell = hit[0]
        grp = URIRef(f"{table_uri}-rg{i}")
        g.add((grp, RDF.type, TAB.HeaderNode))
        g.add((grp, RDF.type, TAB.DerivedRowGroup))
        g.add((table_uri, TAB.hasHeaderNode, grp))
        g.add((grp, TAB.hasLabel, cell))
        g.add((grp, PROV.wasDerivedFrom, arow))
        for m in g.objects(arow, TAB.aggregates):
            g.add((grp, TAB.coversRow, m))
        made += 1
    if made:
        parents = {}
        for child, parent in g.query(_query_text("row-group-nesting.rq"),
                                     initBindings={"tbl": table_uri}):
            g.add((child, TAB.parentHeader, parent))
            parents[child] = parent
        for grp in set(g.subjects(RDF.type, TAB.DerivedRowGroup)):
            if (table_uri, TAB.hasHeaderNode, grp) not in g:
                continue
            level, cur = 0, parents.get(grp)
            while cur is not None:
                level += 1
                cur = parents.get(cur)
            g.add((grp, TAB.headerLevel, Literal(level, datatype=XSD.integer)))
    return made
