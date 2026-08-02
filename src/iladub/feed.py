"""feed — the ET(K)L → grounding bridge (closes raw-doc→grounded-graph).

PROCEDURAL raw extraction: reads asserted tab:RecordTable cells out of a compiled
CompilationReport.graph into per-cell SurfaceConcepts (row = record), then grounds them via the
shipped ground_concept oracle (unchanged — no new grounding decision here). RDF reads only; no
tuned constant, no IRI-name parsing. This is the RawDocument→grounding-portal traversal.

Loop M adds the CHAIN-WALK: a table and the tables that `tab:continuesTable` it are read as ONE
logical table (`_logical_tables`), so a document whose table was cut across page breaks feeds
the portal the record sequence its author wrote, not one fragment per page. Undoing pagination
is a READING act — the graph keeps the page-scoped tables and the link the continuation AXIOM
licensed; nothing is rewritten, merged, or re-derived, and the decision that licensed the link
was taken at compile time (vocab/queries/continuation-of.rq), never here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .etkl.celltype import is_blank
from .ground import SurfaceConcept

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


@dataclass(frozen=True)
class Record:
    row_id: str
    concepts: tuple[SurfaceConcept, ...]


def _logical_tables(graph: Graph, tables: set) -> list[tuple]:
    """The document's LOGICAL tables: each head table followed by its continuation chain.

    Loop M. `tab:continuesTable` links a continuation table to the one it continues, so a table
    that HAS a predecessor is never read on its own: its rows belong to the logical table its
    head opens, and they join that table's record sequence in PAGE ORDER (the link direction IS
    the page order — a continuation continues an EARLIER page).

    No decision is made here (§8): the "is this a continuation?" decision was taken at compile
    time by the AXIOM `vocab/queries/continuation-of.rq` and is already an asserted fact in the
    graph. This walk only CONSUMES that fact — RDF reads, no tuned constant.

    Three structural guards, because a record must never be lost or read twice:
      * the predecessor is the LOWEST `tab:continuesTable` object, not an arbitrary one — a
        malformed table naming two predecessors must still read the same way on every run;
      * `seen` — a table reached twice (a malformed graph in which two tables continue the same
        one) is read once, under the first head that reaches it;
      * the sweep-up at the end — every table of a CYCLE has a predecessor, so the cycle has no
        head and its records would vanish. The lowest member is read as the head instead, and
        the rest of the cycle joins it as one logical table.

    ORDER of the logical tables is by the head's PAGE first, string second. Sorting by URI alone
    is only accidentally page order: `p10#t0` sorts before `p2#t0`, so a ten-page document read
    its tables out of order (F7). Pages are read (`tab:onPage`), never parsed out of the IRI, and
    a graph that records none falls back to the `sorted(key=str)` order the pre-chain feed used.
    """
    successors: dict = {}
    heads: list = []
    for t in sorted(tables, key=str):
        prev = min((o for o in graph.objects(t, TAB.continuesTable)
                    if o != t and o in tables), key=str, default=None)
        if prev is not None:
            successors.setdefault(prev, []).append(t)
        else:
            heads.append(t)
    out: list[tuple] = []
    seen: set = set()

    def _walk(head) -> tuple:
        chain, queue = [], [head]
        while queue:
            t = queue.pop(0)
            if t in seen:
                continue
            seen.add(t)
            chain.append(t)
            queue.extend(successors.get(t, ()))
        return tuple(chain)

    for head in sorted(heads, key=lambda t: (_table_page(graph, t), str(t))):
        out.append(_walk(head))
    for t in sorted(tables, key=str):                 # cycle sweep-up: no table goes unread
        if t not in seen:
            out.append(_walk(t))
    return out


def _table_page(graph: Graph, table) -> float:
    """The page a table was read from — its lowest cell `tab:onPage`; `inf` when none records one
    (an unpaged graph then keeps its pre-chain `sorted(key=str)` reading order)."""
    pages = [int(p) for e in graph.objects(table, TAB.hasCell)
             for p in graph.objects(e, TAB.onPage)]
    return float(min(pages)) if pages else float("inf")


def _row_page(graph: Graph, row) -> int | None:
    """The page a row was read from (`tab:onPage`, off its own cells), or None if unrecorded.

    `min` is a deterministic choice, not a judgment: a row whose cells claim two pages is
    malformed (the compile emits one page per region), and the discriminator only has to be
    STABLE for such a row — `table_records`' final uniqueness pass, not this number, is what
    guarantees two rows never share a subject.
    """
    pages = {int(p) for e in graph.subjects(TAB.atRow, row)
             for p in graph.objects(e, TAB.onPage)}
    return min(pages) if pages else None


def _row_discriminator(graph: Graph, row) -> str:
    """The row's opaque discriminator: its URI fragment, PAGE-QUALIFIED — always.

    A fragment is unique inside ONE table and nowhere else. The pages of a document compile
    under page-scoped document URIs (`document.page_doc_uri`), so `p1#htable1-r7` and
    `p2#htable1-r7` are DIFFERENT rows sharing a fragment — measured on the stem, 65 of page 2's
    row fragments also name a page-1 row; measured on the case-1 two-page fixture, a shipping row
    and a lab row both landed on `urn:iladub:record:table0-r1_table0-r1`.

    Qualification is UNCONDITIONAL (F1). Making it conditional on chain membership was the
    defect: an UNCHAINED multi-page document is exactly where nothing else disambiguates the two
    pages, and "byte-identical when unchained" preserved the weld rather than fixing it. The page
    is READ (`tab:onPage`), never parsed out of the IRI.

    A graph recording no page keeps the bare fragment — readable, and NOT the uniqueness
    guarantee: that is `table_records`' final pass, which appends the row's own IRI to any id
    two rows would otherwise share. Nothing here is allowed to be silently wrong (F6/§7).
    """
    frag = str(row).split("#")[-1]
    page = _row_page(graph, row)
    return frag if page is None else f"p{page} {frag}"


def _read_table(graph: Graph, t) -> tuple[list, dict, dict]:
    """One table's reading: `(ordered_rows, {row: [(x0, y0, concept)]}, {row: rid})`.

    Deliberately PER-TABLE, even when the table is one member of a continuation chain (R34's
    third face): every field name here comes from THIS table's own header path, and every group
    key from THIS table's own derived groups over THIS table's own rows. Recognition's evidence
    stops at the LEAF header row, so a licensed chain can span tables whose header blocks differ
    ABOVE it — on the stem the three tables' column paths are label-identical by MEASUREMENT,
    not by law, and where they could differ the per-table reading is the honest one. Scoping the
    read this way also makes cross-member group-key injection structurally impossible: a group
    can only ever reach rows of its own table (measured on the stem: 0 cross-table
    `tab:coversRow`).
    """
    header = _column_header_path(graph, t)
    row_path = _row_header_path(graph, t)
    rows: dict = {}
    row_cols: dict = {}
    for e in graph.subjects(RDF.type, TAB.EntryCell):
        if (t, TAB.hasCell, e) not in graph:
            continue
        row = graph.value(e, TAB.atRow)
        if row is not None and (row, RDF.type, TAB.AggregationRow) in graph:
            continue          # a subtotal is not a record (§7): its cells mint no subject
        col = graph.value(e, TAB.atColumn)
        txt = str(graph.value(e, TAB.cellText))
        if is_blank(txt):
            continue          # loop K: a placeholder has no content to ground — dropping
                              # it also leaves the column OPEN for group-key injection
        prov = graph.value(e, PROV.wasDerivedFrom)
        region = str(prov).split("#")[-1] if prov is not None else str(e).split("#")[-1]
        concept = SurfaceConcept(header.get(col, ""), txt, region)
        x0, y0 = _bbox_xy(graph, e)
        rows.setdefault(row, []).append((x0, y0, concept))
        row_cols.setdefault(row, set()).add(col)
    # Loop K: recovered group keys become groundable concepts. A suppressed key (the
    # author writes Month once per group) never appears among the row's own cells; the
    # derived row group carries it with provenance to the SOURCE cell (§5/§6 — context
    # is carried, to the page). Column-identity-driven, injected only where the record
    # has no non-blank concept at that column, once per column (nested groups can share
    # one label cell). The y-sort key is the ROW's own extent, not the source cell's,
    # so record ordering is untouched.
    for h in graph.objects(t, TAB.hasHeaderNode):
        if (h, RDF.type, TAB.DerivedRowGroup) not in graph:
            continue
        label = graph.value(h, TAB.hasLabel)
        col = graph.value(label, TAB.atColumn) if label is not None else None
        if col is None:
            continue
        key = str(graph.value(label, TAB.cellText))
        prov = graph.value(label, PROV.wasDerivedFrom)
        region = str(prov).split("#")[-1] if prov is not None else str(label).split("#")[-1]
        x0, _ = _bbox_xy(graph, label)
        for row in graph.objects(h, TAB.coversRow):
            if row not in rows or col in row_cols.get(row, set()):
                continue
            own_y = min(y for _, y, _ in rows[row])
            rows[row].append((x0, own_y, SurfaceConcept(header.get(col, ""), key, region)))
            row_cols.setdefault(row, set()).add(col)
    ordered = sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r]))
    rid_of = {row: (row_path[row] if row in row_path
                    else _row_discriminator(graph, row)) for row in ordered}
    return ordered, rows, rid_of


def table_records(graph: Graph) -> list[Record]:
    """Each asserted tab:RecordTable OR tab:HierarchicalTable -> one Record per data row; each data
    cell -> a SurfaceConcept (text=its column's HEADER PATH, value=cell text, region=cell provenance).
    For a flat RecordTable the path reduces to the single column label (backward compatible). RDF
    reads only; no tuned constant, no IRI-name parsing.

    Loop M — a table and its `tab:continuesTable` chain are ONE logical table: the head's rows
    first, then each continuation's, in page order, under one identity space, and a continuation
    table is never read separately (so no row is read twice). What is NOT assumed across a link:
    label identity — see `_read_table`. Undoing pagination is a READING act, not a rewrite: the
    graph keeps three page-scoped tables linked by the fact the AXIOM licensed; the feed reads
    them as the one table the author cut.

    THE IDENTITY INVARIANT, enforced in three passes rather than argued: no two rows of the
    document ever mint the same record id. Pass 3 is what makes that a guarantee instead of a
    property of the emitter's naming — see there.
    """
    out: list[Record] = []
    tables = (set(graph.subjects(RDF.type, TAB.RecordTable))
              | set(graph.subjects(RDF.type, TAB.HierarchicalTable)))
    # Pass 1: build each LOGICAL table's row cells + rid, WITHOUT minting anything yet. The
    # multiplicity count is hoisted ACROSS all tables (loop I final review, I-1): two
    # tables each with a same-named group (e.g. two 'Mackay' groups in different
    # HierarchicalTables) must not mint the SAME record subject — a per-table count missed
    # that cross-table collision entirely.
    per_logical: list[tuple] = []
    multiplicity: dict = {}
    for members in _logical_tables(graph, tables):
        ordered: list = []
        rows: dict = {}
        rid_of: dict = {}
        for t in members:                      # chain order == page order
            m_ordered, m_rows, m_rid = _read_table(graph, t)
            ordered.extend(m_ordered)          # head's rows first, then each continuation's
            rows.update(m_rows)                # row URIs are page-scoped: no key ever clashes
            rid_of.update(m_rid)
        for rid in rid_of.values():
            multiplicity[rid] = multiplicity.get(rid, 0) + 1
        per_logical.append((ordered, rows, rid_of))
    # Pass 2: mint ids using the GLOBAL (cross-table) multiplicity — collision guard
    # (loop I; closes the PR #59 recorded minor): two rows sharing a header path, whether
    # in the same table or across tables, must never mint the same record subject — each
    # colliding row keeps its opaque discriminator appended.
    minted: list[tuple] = []
    for ordered, rows, rid_of in per_logical:
        for row in ordered:
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            rid = rid_of[row]
            if multiplicity[rid] > 1:
                rid = f"{rid} > {_row_discriminator(graph, row)}"
            minted.append((row, rid, tuple(cells)))
    # Pass 3: the guarantee (F1). Everything above is READABILITY — a header path, a page, a
    # fragment — and every one of them is the emitter's naming, which the feed does not control
    # and must not trust: appending a discriminator that EQUALS the id it disambiguates is a
    # no-op, and that is exactly how two pages' `table0-r1` welded a shipping row and a lab row
    # onto one subject (measured on the case-1 fixture). So any id two rows still share is
    # settled by the row's own IRI, which RDF guarantees unique. A collision here means the
    # readable forms ran out, never that a record is lost.
    residual: dict = {}
    for _row, rid, _cells in minted:
        residual[rid] = residual.get(rid, 0) + 1
    for row, rid, cells in minted:
        out.append(Record(f"{rid} > {row}" if residual[rid] > 1 else rid, cells))
    return out


def _bbox_xy(graph: Graph, entry_cell) -> tuple[float, float]:
    """Read (x0, y0) off an EntryCell's tab:hasBBox node; missing bbox sorts as (0.0, 0.0)."""
    bbox = graph.value(entry_cell, TAB.hasBBox)
    if bbox is None:
        return (0.0, 0.0)
    x0 = graph.value(bbox, TAB.x0)
    y0 = graph.value(bbox, TAB.y0)
    return (float(x0) if x0 is not None else 0.0, float(y0) if y0 is not None else 0.0)


def _header_path(graph: Graph, table, cover_pred) -> dict:
    """Map each target (column or row) covered by `table`'s header tree to its HEADER PATH: the
    deepest HeaderNode covering the target (via `cover_pred` = TAB.coversColumn or TAB.coversRow),
    walked up parentHeader to the root, labels joined ' > '. For a flat axis (level-0, single target,
    no parent) this is the single label. Returns {} when no header node covers via `cover_pred`.
    RDF reads only; no tuned constant, no IRI-name parsing."""
    label: dict = {}
    parent: dict = {}
    best: dict = {}                                 # target -> (level, header_node)
    for h in graph.objects(table, TAB.hasHeaderNode):
        lc = graph.value(h, TAB.hasLabel)
        label[h] = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
        parent[h] = graph.value(h, TAB.parentHeader)
        lvl_lit = graph.value(h, TAB.headerLevel)
        lvl = int(lvl_lit) if lvl_lit is not None else 0
        for u in graph.objects(h, cover_pred):
            if u not in best or lvl > best[u][0]:
                best[u] = (lvl, h)
    paths: dict = {}
    for u, (_, h) in best.items():
        parts: list = []
        cur = h
        while cur is not None:
            parts.append(label.get(cur, ""))
            cur = parent.get(cur)
        paths[u] = " > ".join(reversed(parts))
    return paths


def _column_header_path(graph: Graph, table) -> dict:
    """Column paths (deepest coversColumn header walked to root). Single label per column for a flat
    RecordTable (backward compatible)."""
    return _header_path(graph, table, TAB.coversColumn)


def _row_header_path(graph: Graph, table) -> dict:
    """Row paths (deepest coversRow header walked to root) — a cross-tab's row identity. {} when the
    table has no row-header tree (RecordTable / plain hierarchical)."""
    return _header_path(graph, table, TAB.coversRow)


def _record_uri(row_id: str) -> URIRef:
    """Mint a URI-safe record subject from a row id. Preserves an already-safe opaque fragment
    (e.g. 'table0-r1'); slugs a header path ('Region > North' -> 'Region_North')."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", row_id).strip("_") or "record"
    return URIRef("urn:iladub:record:" + slug)


@dataclass(frozen=True)
class FeedResult:
    records: int
    grounded: int
    proposed: int


def ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult:
    """Ground a compiled document's record tables against a contract: one subject per row, each
    cell grounded via the shipped ground_concept oracle (unchanged). Populates `g` with grounded
    nodes + promotion decisions + propositions; returns the grounded/proposed tally."""
    from .ground import ground_concept

    records = table_records(graph)
    grounded = proposed = 0
    for rec in records:
        subject = _record_uri(rec.row_id)
        for concept in rec.concepts:
            status = ground_concept(concept, contract, subject, proposer, terms, shapes, g)
            if status == "grounded":
                grounded += 1
            else:
                proposed += 1
    return FeedResult(len(records), grounded, proposed)
