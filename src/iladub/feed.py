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

Loop N carries that to the ROW AXIS: a chain's row groups and row identities are read off the
whole logical table (`_inject_group_keys`, `_logical_row_paths`), because the compile now
derives them there — over the document-confirmed arithmetic, attached to the chain's head, with
`tab:coversRow` edges that cross member tables. Still no decision here: the groups, their keys
and their nesting are AXIOM derivations already asserted in the graph, and the correspondence
between a member's column and the head's is the asserted `tab:continuesColumn` — read, never
parsed out of an IRI.
"""
from __future__ import annotations

import os
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


def _logical_column(graph: Graph, col):
    """The HEAD table's column this one continues — `tab:continuesColumn` walked to its end.

    The logical column identity across a chain, READ from the graph (loop N). A member table
    mints its own column nodes, so "the Month column" is a different URI on every page; the
    compile commits the correspondence as `tab:continuesColumn` at the same moment, and on the
    same licence, as `tab:continuesTable` (see `document._link_columns`). Nothing is parsed out
    of an IRI here — the feed's standing rule.

    The compile MATERIALIZES that closure as `tab:inLogicalColumn` (one hop, straight to the
    chain's head — see `document._link_columns`), so the normal path is a single lookup. The
    pairwise walk stays as the fallback for a graph that records only `tab:continuesColumn`: the
    two agree by construction, and the fallback is what lets a hand-built fixture (or a graph
    compiled before the closure was materialized) read identically.

    A column with no link at all is its own logical column, so every unchained graph behaves
    exactly as before. A malformed cycle terminates on `seen` rather than spinning: the first
    repeat wins, deterministically.

    DEGRADES DIFFERENTLY FROM THE QUERY (task 4 carry-in (a), stated so the two are never
    confused): on a graph carrying NEITHER `tab:inLogicalColumn` NOR `tab:continuesColumn` for a
    column, THIS function falls back all the way to returning the column itself — a column with
    no link is its own logical column, by the same reading convention loop M already used for an
    unlinked table. `row-group-key-logical.rq` has no such fallback: it requires the
    `tab:inLogicalColumn` edge to exist as a triple, and REFUSES (zero rows) in its absence. The
    two are not required to agree here — this function is a per-record READ that must always
    return *some* column identity so the feed can group cells table by table, while the query is
    an AXIOM deciding whether the KEY is grounded at all, and honest refusal is the right answer
    when the correspondence was never asserted. Both readings agree on every graph the compiler
    actually produces, because `document._link_columns` always asserts both predicates together.
    """
    canonical = min(graph.objects(col, TAB.inLogicalColumn), key=str, default=None)
    if canonical is not None:
        return canonical
    seen = set()
    while col is not None and col not in seen:
        seen.add(col)
        nxt = min((o for o in graph.objects(col, TAB.continuesColumn) if o not in seen),
                  key=str, default=None)
        if nxt is None:
            return col
        col = nxt
    return col


def _read_table(graph: Graph, t) -> tuple[list, dict, dict]:
    """One table's CELL reading: `(ordered_rows, {row: [(x0, y0, concept)]},
    {row: {logical_column}})`.

    Deliberately PER-TABLE, even when the table is one member of a continuation chain (R34's
    third face): every field name here comes from THIS table's own header path. Recognition's
    evidence stops at the LEAF header row, so a licensed chain can span tables whose header
    blocks differ ABOVE it — on the stem the three tables' column paths are label-identical by
    MEASUREMENT, not by law, and where they could differ the per-table reading is the honest
    one.

    GROUP KEYS ARE NO LONGER READ HERE (loop N). They were, per table, and the note that used to
    stand at this spot said cross-member injection was structurally impossible — true then,
    because loop I could only derive a group inside one page's window. The document-level pass
    now derives a chain's groups over the LOGICAL table and attaches them to its HEAD, so the
    keys must reach every member's rows; `_inject_group_keys` does that at the logical level and
    states the reading in full. R34's third face is unchanged in substance: a chain's keys still
    come from THIS logical table's own derivation, and each row's FIELD NAME still comes from
    its own member table's header path.
    """
    header = _column_header_path(graph, t)
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
        row_cols.setdefault(row, set()).add(_logical_column(graph, col))
    ordered = sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r]))
    return ordered, rows, row_cols


def _inject_group_keys(graph: Graph, members, rows: dict, row_cols: dict, owner: dict) -> None:
    """Inject every derived row group's KEY into the records it covers — logical-table scoped.

    Loop K: recovered group keys become groundable concepts. A suppressed key (the author writes
    Month once per group) never appears among the row's own cells; the derived row group carries
    it with provenance to the SOURCE cell (§5/§6 — context is carried, to the page).
    Column-identity-driven, injected only where the record has no non-blank concept at that
    column, once per column (nested groups can share one label cell). The y-sort key is the
    ROW's own extent, not the source cell's, so record ordering is untouched — and this pass now
    runs AFTER each member's rows were ordered, so it cannot perturb the order even in principle.

    LOOP N — WHY THE SCOPE IS THE LOGICAL TABLE. A chain's groups are derived over the logical
    table and attached to its HEAD (`document._derive_document_row_groups`), with `coversRow`
    edges that deliberately cross member tables: the whole point is that a subtotal on page 2
    keys rows on pages 0-2. Reading groups per member would leave every non-head member's rows
    keyless. So the sources are ALL members' group nodes — which is not a widening of what may
    reach a row, because a group still reaches exactly the rows it COVERS, and covering is an
    asserted fact, never inferred from membership of the chain. Every member is read (not just
    the head) so that a chain the arithmetic pass ABSTAINED on — whose members therefore keep
    their page-local groups — loses no key it had.

    THE COLUMN IDENTITY is logical (`_logical_column`): the group's label cell may sit on a
    different page from the row being keyed, where "the same column" is a different node. The
    occupancy test and the once-per-column guard both run on the logical column, so a row can
    never receive a key at a column where it already wrote a value.

    THE FIELD NAME stays the row's OWN table's header path (R34's third face): the label may
    come from page 0, but a page-2 record's field is named by page 2's reading of that column.
    `locals_by_table` inverts each member's leaf columns onto their logical column, so the row's
    own node is what the header path is looked up by; where the graph records no correspondence
    (an unchained table, a fixture with no leaf columns) that falls back to the label's own
    column — exactly what the per-table reading used.
    """
    headers = {t: _column_header_path(graph, t) for t in members}
    locals_by_table = {}
    for t in members:
        locals_by_table[t] = {_logical_column(graph, c): c
                              for c in graph.objects(t, TAB.hasLeafColumn)}
    for t in members:
        for h in sorted(graph.objects(t, TAB.hasHeaderNode), key=str):
            if (h, RDF.type, TAB.DerivedRowGroup) not in graph:
                continue
            label = graph.value(h, TAB.hasLabel)
            col = graph.value(label, TAB.atColumn) if label is not None else None
            if col is None:
                continue
            lcol = _logical_column(graph, col)
            key = str(graph.value(label, TAB.cellText))
            prov = graph.value(label, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(label).split("#")[-1]
            x0, _ = _bbox_xy(graph, label)
            for row in graph.objects(h, TAB.coversRow):
                if row not in rows or lcol in row_cols.get(row, set()):
                    continue
                own = owner.get(row)
                local = locals_by_table.get(own, {}).get(lcol, col)
                own_y = min(y for _, y, _ in rows[row])
                rows[row].append((x0, own_y,
                                  SurfaceConcept(headers.get(own, {}).get(local, ""),
                                                 key, region)))
                row_cols.setdefault(row, set()).add(lcol)


def _table_captions(graph: Graph, table) -> list[tuple[str, str]]:
    """A table's `tab:SectionCaption`s (a `tab:RegionCaption` SUBCLASS), ordered POSITIONALLY
    (`tab:captionRow`, the caption node as a deterministic tie-break) — `[(text, region), ...]`.
    Empty for the vast majority of tables, which assert no `tab:hasCaption` at all (every table
    before loop Q, and every table loop Q's section repair never touched).

    Loop Q (spec §4.0-§4.2): a repaired section table's leading strips (the KEY line plus any
    berth-notice furniture) are peeled and committed as `tab:RegionCaption` + `tab:SectionCaption`
    at compile time (`compile._emit_band_captions`), then survive `document._band_subgraph`'s
    adoption merge for free — that function copies every triple reachable from the table's own
    URI, and `hasCaption`/`captionText`/`captionRow`/`rdf:type` are exactly such triples
    (measured on the real CBH fixture: both adopted section tables carry their captions
    post-adoption). This function only READS what compile already asserted — no new decision, §8.

    SCOPED TO `tab:SectionCaption` ONLY (fix round, 2026-08-04 — the real stem's own furniture
    was measured injected as a false candidate key before this scoping existed): a PLAIN
    `tab:RegionCaption` with no `tab:SectionCaption` type is loop C's reading-furniture shape
    (`rowrole.emit_reading_evidence` — a print-timestamp/title line found inside a table's
    header region, carried so its text is never lost) and was NEVER a section key; measured on
    the real GrainCorp stem, its own furniture captions ('Friday, 31'/'July 2026') were being
    read here before this filter existed, injecting false candidates and prefixing every
    record's identity with print-timestamp text (`still-quarantined` drifted 1265→1341). Every
    caption `compile._emit_band_captions` emits carries BOTH types (it is the one emitter for
    the peeled-leading-strip mechanism), so the section-repair path is unaffected by this scope.

    `region` is the caption node's OWN fragment: a `RegionCaption` asserts no separate
    `prov:wasDerivedFrom` (compile.py commits captionText/captionRow directly on it), so this
    is the SAME fallback `_read_table` and `_inject_group_keys` already use when a node names
    its own provenance rather than pointing at one — not a new provenance convention."""
    caps = []
    for cap in graph.objects(table, TAB.hasCaption):
        if (cap, RDF.type, TAB.SectionCaption) not in graph:
            continue
        text = graph.value(cap, TAB.captionText)
        if text is None:
            continue
        row_lit = graph.value(cap, TAB.captionRow)
        row = int(row_lit) if row_lit is not None else 0
        caps.append((row, str(cap), str(text)))
    caps.sort(key=lambda t: (t[0], t[1]))
    return [(text, str(cap).split("#")[-1]) for _, cap, text in caps]


def _inject_section_captions(graph: Graph, members, rows: dict, owner: dict) -> None:
    """Inject every captioned member table's captions into EVERY record it owns — loop Q §4.2,
    imitating `_inject_group_keys`'s SHAPE (one SurfaceConcept appended per row, provenanced to
    the SOURCE node, the row's own extent as the y-sort key so record ORDER is untouched) over
    a NEW evidence source that is table-wide rather than column-scoped.

    NO OCCUPANCY GUARD (the one deliberate divergence from `_inject_group_keys`): a suppressed
    group key fills a specific COLUMN a row might already have written; a caption names no
    column at all — 'GERALDTON' is not a value ANY of the section's own cells could already
    carry, so there is nothing to avoid overwriting. Every record of a captioned table gets
    every one of that table's captions, undiscriminated (key-vs-notice is §4.3's job, not this
    layer's — feed injects ALL captions as candidates; §7's honest refusal quarantines the
    non-members downstream).

    ORDER: captions are given NEGATIVE x0 (by caption index, so multiple captions keep their
    OWN positional order) — they read as the heading evidence the record's cells sit under,
    ahead of the record's own leftmost cell, never interleaved among them."""
    for t in members:
        caps = _table_captions(graph, t)
        if not caps:
            continue
        for row, cells in rows.items():
            if owner.get(row) != t:
                continue
            own_y = min(y for _, y, _ in cells)
            for k, (text, region) in enumerate(caps):
                cells.append((-1000.0 + k, own_y,
                             SurfaceConcept(text, text, region, is_section_marker=True)))


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
        row_cols: dict = {}
        owner: dict = {}
        for t in members:                      # chain order == page order
            m_ordered, m_rows, m_cols = _read_table(graph, t)
            ordered.extend(m_ordered)          # head's rows first, then each continuation's
            rows.update(m_rows)                # row URIs are page-scoped: no key ever clashes
            row_cols.update(m_cols)
            owner.update({r: t for r in m_ordered})
        # Group keys and row identities are read at the LOGICAL level, after every member's
        # rows exist and are ordered: a chain's groups hang off its HEAD and cover rows on
        # every page (loop N). Injection cannot perturb the order — `ordered` is already fixed.
        _inject_group_keys(graph, members, rows, row_cols, owner)
        _inject_section_captions(graph, members, rows, owner)
        row_path = _logical_row_paths(graph, members)
        # Loop Q §4.2: a captioned member's FIRST caption (positionally) prefixes every one of
        # ITS OWN rows' identity — "GERALDTON > p0 table0-r0" — before anything has decided
        # what to CALL that value (§4.3's cascade names the field later; attribution never
        # waits for naming). A table with no captions computes an empty list here and every one
        # of its rows keeps exactly today's identity — the byte-identity guarantee for every
        # table loop Q never touched.
        #
        # CAVEAT (reviewer's minor, task-5 review 2026-08-04; AMENDED final-review F3 — the
        # "unreachable" claim below is now false): the prefixed id is a STRING, " > "-joined
        # like every other rid this function mints — nothing in feed.py itself parses it back
        # apart, and production reads `rid` only as an opaque grounding-portal subject key
        # (`_record_uri` slugs it whole). But `tests/test_cbh_e2e.py` DOES now parse it, at
        # three sites (:159 `" > " in r.row_id`, :162 `rid.split(" > ")[0]`, :191
        # `r.row_id.split(" > ")[0]`) — an e2e-only MARKER-DERIVATION pattern, recovering the
        # section-key set for its cascade assertions, not a production consumer. The SAFE
        # DIRECTION: this function inserts exactly one " > " and the key is always the
        # LEFTMOST segment, so `split(" > ")[0]` recovers the key regardless of how many
        # further " > " sequences the BASE (a row path / discriminator) happens to contain.
        # The one case this does NOT cover — an honestly-named, unmitigated DEGRADATION, not a
        # guard that exists: a caption whose own text contains the literal substring " > "
        # would make `[0]` return only the caption's own prefix, silently truncating the
        # recovered key instead of the whole caption. No specimen has produced such a caption;
        # named here so a future consumer does not assume `split(" > ")[0]` is a general-purpose
        # row_id parser, or that today's e2e usage proves it safe in general. A caption text
        # that happened to look like `_row_discriminator`'s own output shape (`^p\d+ \S+$`,
        # e.g. a caption literally reading "p0 table0-r0") remains a second, separate way the
        # prefixed id can be ambiguous to a pattern-matching parser, as originally noted.
        section_key = {t: (caps[0][0] if (caps := _table_captions(graph, t)) else None)
                       for t in members}
        rid_of = {}
        for row in ordered:
            base = row_path[row] if row in row_path else _row_discriminator(graph, row)
            key = section_key.get(owner.get(row))
            rid_of[row] = f"{key} > {base}" if key is not None else base
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


def _header_path(graph: Graph, tables, cover_pred) -> dict:
    """Map each target (column or row) covered by `tables`' header trees to its HEADER PATH: the
    deepest HeaderNode covering the target (via `cover_pred` = TAB.coversColumn or TAB.coversRow),
    walked up parentHeader to the root, labels joined ' > '. For a flat axis (level-0, single target,
    no parent) this is the single label. Returns {} when no header node covers via `cover_pred`.
    RDF reads only; no tuned constant, no IRI-name parsing.

    `tables` is a SEQUENCE (loop N) so a continuation chain's row identities can be read off the
    whole logical table at once: the document-level groups hang off the head but cover member
    rows, and the deepest-header selection must then compare candidates ACROSS members rather
    than per table — merging per-table results would pick a shallower header whenever two members
    covered one row. Column paths stay single-table (R34's third face).

    THE TIE-BREAK IS DETERMINISTIC, AND IT IS NOT A SEMANTIC CLAIM (loop N review). Two derived
    groups can cover ONE row at the SAME level — R18's co-resident case, which the nesting query
    creates by REFUSING to link groups with identical member sets (§7: refusal over a guess).
    Measured on the stem after the document-level derivation: 7 of 132 covered rows, up from 2,
    e.g. `p1#htable1-r66` covered by both `Mar 27` and `Portland` at level 1. R18 already records
    what happens then — the deepest-cover selection keeps ONE and silently drops the other, a §5
    context loss. What it did NOT record is that the survivor was whichever the graph handed over
    first, i.e. rdflib's iteration order: the SAME document could mint DIFFERENT record subjects
    on a different run, store or rdflib version. That is a reproducibility defect independent of
    the context loss, and it is what this ordering fixes: among equal levels the lexicographically
    first (label, node) wins. Which one wins carries NO meaning — neither group is more the row's
    header than the other — but it is now the same one every time, everywhere. The §5 loss itself
    stands as R18 describes it."""
    label: dict = {}
    parent: dict = {}
    best: dict = {}                                 # target -> (level, header_node)
    for h in (h for t in tables for h in graph.objects(t, TAB.hasHeaderNode)):
        lc = graph.value(h, TAB.hasLabel)
        label[h] = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
        parent[h] = graph.value(h, TAB.parentHeader)
        lvl_lit = graph.value(h, TAB.headerLevel)
        lvl = int(lvl_lit) if lvl_lit is not None else 0
        for u in graph.objects(h, cover_pred):
            held = best.get(u)
            if held is None or lvl > held[0] or (
                    lvl == held[0]
                    and (label[h], str(h)) < (label[held[1]], str(held[1]))):
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
    RecordTable (backward compatible). ONE table, always — a member's fields are named by its own
    reading (R34's third face)."""
    return _header_path(graph, (table,), TAB.coversColumn)


def _row_header_path(graph: Graph, table) -> dict:
    """Row paths (deepest coversRow header walked to root) — a cross-tab's row identity. {} when the
    table has no row-header tree (RecordTable / plain hierarchical)."""
    return _header_path(graph, (table,), TAB.coversRow)


def _logical_row_paths(graph: Graph, members) -> dict:
    """Row paths over a whole LOGICAL table (loop N): the chain's members read as one row axis.

    A chain's row groups are derived over the logical table and attached to its HEAD, so a
    member's rows are covered by a header node belonging to another table — read per member,
    those rows would fall back to an opaque discriminator and the document would carry two kinds
    of record identity. Identical to `_row_header_path` for a single-member logical table."""
    return _header_path(graph, tuple(members), TAB.coversRow)


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


_GROUND_SHAPES = None
_GROUND_ONT = None

# The grounding membrane's shape set (spec 2026-08-10 §5.4). `iladub:GroundedNodeShape` is the
# differentiator itself — "every grounded node must be produced by a promotion decision" — and
# `dec-shapes.ttl` is what makes that decision accountable rather than a bare link. The
# ontology carries `iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon`, without which
# the dec shapes target nothing.
_GROUND_SHAPE_FILES = ("iladub-shapes.ttl", "dec-shapes.ttl")
_GROUND_ONT_FILES = ("iladub.ttl", "dec.ttl")


def _build_ground_membrane():
    global _GROUND_SHAPES, _GROUND_ONT
    from rdflib import Graph
    from .etkl.compile import _repo_vocab       # the walk-up locator, not a relative path

    v = _repo_vocab()
    s = Graph()
    for f in _GROUND_SHAPE_FILES:
        s.parse(os.path.join(v, "shapes", f), format="turtle")
    o = Graph()
    for f in _GROUND_ONT_FILES:
        o.parse(os.path.join(v, "ontology", f), format="turtle")
    _GROUND_SHAPES, _GROUND_ONT = s, o


def _validate_grounding(g) -> tuple[bool, str]:
    if _GROUND_SHAPES is None:
        _build_ground_membrane()
    from .etkl import compile as _compile
    from .etkl import membrane
    # The engine pin is read from `compile` at call time rather than restated here: it encodes
    # ONE measured incapacity (rudof raises on an sh:sparql constraint with a blank-node focus,
    # see membrane.validate), and two copies of it could drift apart. This membrane needs it
    # even more than the compile one — `ground._emit_grounded` mints BOTH the candidate and the
    # decision as blank nodes (ground.py:90,145), so EVERY promotion here is a blank-node focus.
    return membrane.validate(g, _GROUND_SHAPES, _GROUND_ONT, engine=_compile._DEC_ENGINE)


def ground_document(graph, contract, proposer, terms, shapes, g,
                    validate_shapes: bool = False) -> FeedResult:
    """Ground a compiled document's record tables against a contract: one subject per row, each
    cell grounded via the shipped ground_concept oracle (unchanged). Populates `g` with grounded
    nodes + promotion decisions + propositions; returns the grounded/proposed tally.

    `validate_shapes=True` puts `g` through the grounding membrane before returning, raising
    `AssertionError` with the report rather than handing back a graph that violates the
    promotion invariant. It defaults to False so every existing positional call site is
    unchanged; the corpus battery and the contracted paths pass it explicitly.
    """
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
    if validate_shapes:
        conforms, report = _validate_grounding(g)
        assert conforms, f"grounded graph violates the promotion membrane:\n{report}"
    return FeedResult(len(records), grounded, proposed)
