# tests/test_carriage.py
"""CARRIAGE — what the arc could not see until now: cells carried, not score.

The arc's ten `tab` criteria count escalation REASONS and its seven `etkl` criteria read
the document SCORE. Neither can see a cell-carriage defect. That is measured, not felt:
on 2026-09-16 the alignment-universe gate moved bfs page 5 from 404 placed cells to 496
(+92) and the document from 14251 triples to 15354 (+1103), while the document score held
at 0.8850746269 to ten decimal places — see [[R240]] and PR #239. Work that improves
carriage is therefore invisible to the arc BY CONSTRUCTION, which is why a criterion whose
oracle is CELLS AND TRIPLES exists at all (`prog:criterion:tab:11`).

Gate classification (CLAUDE.md §8): PROCEDURAL. It compiles a document and compares
integers. It decides nothing about any reading, carries no tolerance and no threshold —
the two figures below are a RECORDED MEASUREMENT of a specific tree, not a tuned constant.

THE STRICT XFAIL IS GONE, AND THAT IS THE RECORD OF THE BUILD. Until 2026-09-17 the first
test below carried `@pytest.mark.xfail(strict=True)`: `_boundaries_from_decoration` was
still consulted by `derive_data_grid`, page 5 read 404 cells / 14251 triples, and the
criterion it serves was authored `prog:met false`. The marker was the forcing function —
the day the blanket refusal landed the test XPASSed, and an XPASS under a strict marker is
a SUITE FAILURE, so the switch could not ship while the criterion stayed stale. It was
observed doing exactly that: `[XPASS(strict)] 1 failed, 1 passed` on the tree that first
carried the refusal. Marker and `prog:met` were then flipped in one reviewed act, which is
what keeps `prog:met` a reviewed assertion rather than a side effect (tests/arc-manifest.ttl,
"CODE NEVER WRITES THIS FILE").

Run locally (~5 min, one compile shared by both tests):
    ./.venv/bin/python -m pytest -m corpus tests/test_carriage.py -q
In CI the corpus is absent (`corpus/` is gitignored) and both tests SKIP — so GREEN CI IS
NOT EVIDENCE ABOUT THIS FILE, and a loop that changes carriage must run it by hand.

`prog:criterion:tab:12` (box-split spec 2026-09-28, § 5) — O2 AND C3, below. cbh page 0
raw band 9 (y 683.5-761.5) fuses two side-by-side drawn tables into one `#table9`
`tab:RecordTable`. O2 is the corpus oracle that can SEE the fix: it asserts the region at
y 681-761 compiles as exactly two `tab:RecordTable`s (T1: 7 columns, boxhead `PORT | WHEAT
| MAIN WHEAT GRADES | BARLEY | CANOLA | OTHER | TOTAL`; T2: 2 columns, no boxhead) and ships
under `@pytest.mark.xfail(strict=True)` — the split has not landed yet (Task 4 runs right
after Task 0, before Task 1), so O2 is OBSERVED XFAIL on today's tree by construction: every
O2 test's FIRST assertion is "exactly two RecordTables in the region", which today's fused
single `#table9` always fails (R5). The marker and `prog:met` flip together, in one reviewed
act, once the split (Task 3) lands and O2 is confirmed XPASS (Task 4 Step 4-5) — same
forcing-function discipline as `tab:11` above. C3 is the control: the four cbh rosters
(`#htable1/3/5/7`, all index < 9, unaffected by the split's band-index shift) must keep
identical cells BEFORE and AFTER, and ships with NO xfail — it passes today.

O2's STRICT XFAIL IS GONE TOO (2026-09-30, Task 4 Steps 4-5). With the split (Tasks 3/3b/3c)
and T2's recorded `header_lines` answer (Task 3d) landed, all three O2 tests were observed
`[XPASS(strict)]` — `4 failed, 2 passed`, the fourth being the bfs triple pin below — and the
markers were removed in the same commit that set `tab:12` `prog:met true`. Falsified with the
split's call site reverted: O2 fails on the table count (evidence
`docs/superpowers/2026-09-28-box-split-evidence.md` § 5).
"""
import hashlib
import json
import re

import pytest
from rdflib import RDF, Namespace

from tests.test_corpus import ENTRIES, require_pinned_edition, REPO

pytestmark = pytest.mark.corpus

TAB = Namespace("https://w3id.org/iladub/tab#")

BFS = "gov-stats/bfs-population-bilan-2023.pdf"

#: The reading the switch must produce, fixed by PR #239 (the gate) and PR #241 (identity,
#: 27/27 canton rows). Cells are counted on the ONE adopted RECORD_TABLE region of page 5,
#: which is where every placed cell on that page lives — measured 2026-09-16, `c9270bb`.
P5_CELLS_WHEN_CARRIED = 496
#: 15354 -> 16147 on 2026-09-18, by two LATER readings and not by the switch this file pins:
#: p5's adopted grid now carries its boxhead (11 column labels, replayed from
#: readings/boxhead/) and p6's two lone rows are read (`donation.offer_single_line`). A whole-
#: document triple count moves with every reading the document gains; P5_CELLS is the figure that
#: says the SWITCH still holds, and it is unchanged at 496.
#: 16147 -> 16736 on 2026-09-19: p6's `Tessin` row is read (`trailing.cut_trailing_notes`).
#: 16736 -> 16778 on 2026-09-30: three recorded `header_lines` decisions (box-split Task 3d),
#: 14 triples each (the decision and its two options) = +42 — p5 `#region3-d4` and
#: `#region4-d4` (`no_boxhead`; adoption withdraws their tables, the decisions stay in the log)
#: and p6 `#region2-d4` (`boxhead`). Measured by a probe counting every `header_lines`
#: decision's own and its options' triples: 3 decisions, 42 triples, 16736 + 42 = 16778
#: (evidence 2026-09-28-box-split § 4.5, § 4.6, § 5). P5_CELLS is unchanged at 496.
#: 16778 -> 16940 on 2026-10-05, measured by a run: R265 + R290 + R291. p5 reads two grids
#: (`#p5-datagrid`, 270 cells, and `#p5-datagrid-2`, 226), so P5_CELLS still sums to 496. The
#: R291 fix cuts the year table's notes into a band of their own. The whole delta is under
#: `p5/adopt#…` subjects (canonical N-Triples diff against `4379fbe`, evidence
#: 2026-10-05-r291-trailing-cut-evidence.md § 2.4).
#: 16940 -> 17076 on 2026-10-05, measured by a run: the canton grid's recorded boxhead. +153 / -17,
#: every subject on p5: `#p5-datagrid-h0..h9` and `-lc0..lc9` (40 + 40), their boxes and the grid's
#: own links; out go `p5#region8` (REGION_TILING_FAILED, now the grid's header lines) and its
#: decision. P5_CELLS is unchanged at 496 (evidence 2026-10-05-bfs-canton-boxhead.md § 2).
#: 17076 -> 15611 on 2026-10-05, measured by a whole-corpus snapshot: R293. p6 adopts its data grid
#: (nine record tables superseded by one 32 x 9 grid with nine column labels), and every other
#: corpus document's graph hash is unchanged (evidence 2026-10-05-r293-p6-adopts.md § 5).
#: P5_CELLS is unchanged at 496.
#: 15611 -> 18199 on 2026-10-08, measured by a whole-corpus snapshot on main and the branch: the
#: rule-separated-ink facts (spec 2026-10-08-rule-separated-ink-design.md). All +2588 are
#: `tab:RuleSpan` (192 rules) and `tab:firstGlyphEnd`/`tab:lastGlyphStart` triples; with them
#: stripped, bfs's canonical hash equals main's, and so does every other corpus document's.
#: P5_CELLS is unchanged at 496.
DOC_TRIPLES_WHEN_CARRIED = 18199

#: The control, and it passes TODAY. Page 6 carries 267 cells across six asserted regions
#: and the switch must not move it: a change that alters page 6 is not the change the
#: criterion asks for. Measured 2026-09-16 at `c9270bb`, on the same run as the figures
#: above. A pointwise pin beside a total one is what caught PR #241's mis-specified C2.
#: 267 -> 285 on 2026-09-18: `Total` and `Zurich`, one-line bands that were IGNORED, are now
#: read under band 2's header (9 entries each). The six regions this control was measured on
#: are untouched — what it guards against is the SWITCH moving page 6, and it did not.
#: 285 -> 294 on 2026-09-19: `Tessin` is cut free of the notes set below it and read (9 entries).
#: 294 -> 288 on 2026-10-05, by R293 and not by the switch: p6 adopts its data grid. The 288 are
#: the 294 minus exactly the six boxhead words the band path asserted as entries (`Cantons`,
#: `dépendance`, `dépendance des`, `des jeunes 1`, `personnes`, `âgées 2`); no value moved
#: (multiset diff, evidence 2026-10-05-r293-p6-adopts.md § 2.5).
P6_CELLS = 288
#: 6 -> 8 on 2026-09-18: the `Total` and `Zurich` lone rows are two more asserted regions.
#: 8 -> 9 on 2026-09-19: `Tessin`.
#: 9 -> 1 on 2026-10-05 (R293): the nine record tables are superseded by the one adopted grid.
P6_ASSERTED_REGIONS = 1


@pytest.fixture(scope="module")
def bfs():
    """Compile bfs ONCE for the whole module — the compile is the expensive part."""
    entry = next(e for e in ENTRIES if e["file"] == BFS)
    dest = require_pinned_edition(entry, REPO / "corpus")
    from iladub.etkl.document import compile_document

    return compile_document(str(dest))


def _page_cells(rep, n):
    return sum(r.cells for r in rep.pages[n].regions)


def test_bfs_p5_carries_the_row_label_and_percent_columns(bfs):
    """The row-label column and the final `%` column are CARRIED, not dropped.

    Both lie outside the decoration rectangle (label ends 85.65, `%` starts 516.18, the
    rectangle spans 124.3..495.3), so every row is admitted BECAUSE of ink the emitter
    then never carries — [[R238]], and [[R239]] is the same defect on the other column.
    Judged on cells and triples, NEVER on the score: [[R240]] records that the score is an
    ink-token ratio and did not move a digit while these 92 cells appeared."""
    assert _page_cells(bfs, 5) == P5_CELLS_WHEN_CARRIED
    assert len(bfs.graph) == DOC_TRIPLES_WHEN_CARRIED


def test_bfs_p6_carriage_is_untouched(bfs):
    """THE CONTROL. Page 6 is not a decoration page and must read the same either way.

    Without it the criterion could be met by any change that moves cells ANYWHERE, which
    is how a carriage gauge would rot into the same blindness it was authored to repair."""
    asserted = [r for r in bfs.pages[6].regions if r.verdict == "asserted"]
    assert _page_cells(bfs, 6) == P6_CELLS
    assert len(asserted) == P6_ASSERTED_REGIONS


# ================================== prog:criterion:tab:12 — O2 (flipped 2026-09-30) + C3 ===

CBH = "ag-trade/cbh-stem-2026-08-03.pdf"

#: O2's y-window (box-split spec § 5): band 9's cells lie in this range on cbh page 0.
#: MEASURED (task-4-report.md): today's #table9 has 16 tab:hasCell entries, every one's
#: tab:BBox y0/y1 falls inside [681, 761]; no other asserted region's cells overlap it
#: (the four rosters sit at y0 105..656, all well above).
_Y_LO, _Y_HI = 681, 761

#: The three O2 tests carried `@pytest.mark.xfail(strict=True)` from 2026-09-28 until
#: 2026-09-30, reason: "the split (Task 3) has not landed yet. Today band 9 is ONE fused
#: #table9 RecordTable; O2 needs two." Removed with `tab:12`'s `prog:met true` (module docstring).


@pytest.fixture(scope="module")
def cbh():
    """Compile cbh ONCE for the module — shared by every O2 test and C3."""
    entry = next(e for e in ENTRIES if e["file"] == CBH)
    dest = require_pinned_edition(entry, REPO / "corpus")
    from iladub.etkl.document import compile_document

    return compile_document(str(dest))


def _col_ordinal(uri):
    """`{table_uri}-c{i}` -> i, the column-emission ordinal (holon.py's `_region_uri`
    minting convention — the SAME suffix convention `document.py:_index_suffix` reads)."""
    m = re.search(r"-c(\d+)$", str(uri))
    return int(m.group(1)) if m else None


def _row_ordinal(uri):
    """`{table_uri}-r{i}` -> i, the row-emission ordinal, same convention as columns."""
    m = re.search(r"-r(\d+)$", str(uri))
    return int(m.group(1)) if m else None


def _yband_table_uris(rep, page_idx, y_lo, y_hi):
    """table_uris of ASSERTED regions on `page_idx` whose cells overlap `[y_lo, y_hi]`
    (pt, PDF top-down: `tab:y0` is the top, `tab:y1` the bottom — `holon._bbox_node`).

    MEASURED predicate path (task-4-report.md): `tab:hasCell` / `tab:hasBBox` / `tab:y0` /
    `tab:y1` all return non-empty on today's pre-split `#table9` (16 cells, each with a
    BBox)."""
    g = rep.graph
    out = []
    for r in rep.pages[page_idx].regions:
        if r.verdict != "asserted" or r.table_uri is None:
            continue
        for c in g.objects(r.table_uri, TAB.hasCell):
            bb = g.value(c, TAB.hasBBox)
            if bb is None:
                continue
            y0, y1 = g.value(bb, TAB.y0), g.value(bb, TAB.y1)
            if y0 is None or y1 is None:
                continue
            if float(y0) <= y_hi and float(y1) >= y_lo:
                out.append(r.table_uri)
                break
    return out


def _record_tables(rep, uris):
    """Of `uris`, those the graph types `tab:RecordTable` — MEASURED to return exactly
    [#table9] on today's pre-split tree (task-4-report.md); the two-element case is what
    the split (Task 3) produces."""
    g = rep.graph
    return [u for u in uris if (u, RDF.type, TAB.RecordTable) in g]


def _o2_two_tables(cbh):
    """THE gate (R5), factored so every O2 test calls it FIRST. Asserts exactly two
    RecordTables in band 9's y-window before any content check, so removing the xfail
    marker on ANY O2 test fails HERE, uniformly, on the table count — never on a KeyError
    or a bad-query error further down (fix round 1 review finding 2 confirms this stays
    true after this round's new assertions; see task-4-report.md's FALSIFICATION)."""
    g = cbh.graph
    tables = _record_tables(cbh, _yband_table_uris(cbh, 0, _Y_LO, _Y_HI))
    assert len(tables) == 2, f"expected T1+T2 as two RecordTables, found {len(tables)}: {tables}"
    return g, tables


def _leaf_columns(g, table_uri):
    return list(g.objects(table_uri, TAB.hasLeafColumn))


def _table_by_ncols(g, tables, n):
    matches = [t for t in tables if len(_leaf_columns(g, t)) == n]
    assert len(matches) == 1, (
        f"expected exactly one table with {n} leaf columns among {tables}, "
        f"found {len(matches)}"
    )
    return matches[0]


def _ordered_header_labels(g, table_uri):
    """(column ordinal, label text) for every `tab:hasHeaderNode` whose `tab:coversColumn`
    -> `tab:hasLabel` -> `tab:cellText` resolves, sorted by column ordinal. MEASURED
    (task-4-report.md): today's #table9 has 3 header nodes, each with exactly one
    `tab:hasLabel` -> `tab:cellText` (the two title-bar texts + the maintenance total,
    misread as column headers pre-split — spec § 1)."""
    pairs = []
    for h in g.objects(table_uri, TAB.hasHeaderNode):
        col = g.value(h, TAB.coversColumn)
        if col is None:
            continue
        for lc in g.objects(h, TAB.hasLabel):
            t = g.value(lc, TAB.cellText)
            if t is not None:
                pairs.append((_col_ordinal(col), str(t)))
    pairs.sort(key=lambda p: (p[0] is None, p[0]))
    return [t for _, t in pairs]


def _col_uri_by_header_text(g, table_uri, text):
    for h in g.objects(table_uri, TAB.hasHeaderNode):
        for lc in g.objects(h, TAB.hasLabel):
            if str(g.value(lc, TAB.cellText)) == text:
                return g.value(h, TAB.coversColumn)
    return None


def _cell_text(g, table_uri, col_uri, row_uri):
    for e in g.objects(table_uri, TAB.hasCell):
        if g.value(e, TAB.atColumn) == col_uri and g.value(e, TAB.atRow) == row_uri:
            t = g.value(e, TAB.cellText)
            return str(t) if t is not None else None
    return None


def _column_values_ordered_by_row(g, table_uri, col_uri):
    rows = sorted(g.objects(table_uri, TAB.hasLeafRow), key=_row_ordinal)
    return [_cell_text(g, table_uri, col_uri, r) for r in rows]


def _caption_texts(g, table_uri):
    return [str(g.value(c, TAB.captionText)) for c in g.objects(table_uri, TAB.hasCaption)]


def test_o2_t1_reads_the_seven_column_boxhead(cbh):
    """T1 — box-split spec § 1/§ 5. Every O2 test's FIRST call is `_o2_two_tables` (R5):
    today's fused #table9 always fails its count assertion, so removing the xfail marker
    fails HERE, on the table count, never on a KeyError further down."""
    g, tables = _o2_two_tables(cbh)
    t1 = _table_by_ncols(g, tables, 7)
    assert _ordered_header_labels(g, t1) == [
        "PORT", "WHEAT", "MAIN WHEAT GRADES", "BARLEY", "CANOLA", "OTHER", "TOTAL",
    ]
    port_col = _col_uri_by_header_text(g, t1, "PORT")
    assert port_col is not None
    assert _column_values_ordered_by_row(g, t1, port_col) == ["ALB", "ESP", "GER", "KWI"]
    total_col = _col_uri_by_header_text(g, t1, "TOTAL")
    assert total_col is not None
    rows = sorted(g.objects(t1, TAB.hasLeafRow), key=_row_ordinal)
    kwi_row = next(r for r in rows if _cell_text(g, t1, port_col, r) == "KWI")
    assert _cell_text(g, t1, total_col, kwi_row) == "284,895"
    assert _caption_texts(g, t1) == ["Stock at Port (Main Storage Area) as at 29/07/2026"]


def test_o2_t2_reads_the_two_column_no_boxhead(cbh):
    """T2 — box-split spec § 1/§ 5, named risk 1 (§ 4): T2 must carry ZERO column labels,
    never read its first row (`ALB | 1 - 15 October`) as a boxhead. Gate-first, per R5.

    Fix round 1, finding 2 (controller ruling, promoted from the review's minor): spec §5's
    own falsification line names the known failure mode as page-scoped `page_chars` leaking
    left-box glyphs into T2's FIRST column (spec §7.3: 'PORTWHEATMAIN WHEAT GRADES…' when
    page-scoped) — so this test also asserts T2's port-code column exactly, not only the
    date column. Row order matches the fused pre-split dump (Task 0 evidence §1.3 r1-r4:
    ALB/ESP/GER/KWI top to bottom), the SAME row order as `expected_dates` below."""
    g, tables = _o2_two_tables(cbh)
    t2 = _table_by_ncols(g, tables, 2)
    assert len(list(g.objects(t2, TAB.hasHeaderNode))) == 0
    rows = sorted(g.objects(t2, TAB.hasLeafRow), key=_row_ordinal)
    assert len(rows) == 4
    expected_dates = [
        "1 - 15 October", "1 - 15 August", "24 August - 04 September", "1 - 15 September",
    ]
    expected_ports = ["ALB", "ESP", "GER", "KWI"]
    col_values = [_column_values_ordered_by_row(g, t2, c) for c in _leaf_columns(g, t2)]
    assert expected_dates in col_values, f"no T2 column carries the date sequence: {col_values}"
    assert expected_ports in col_values, (
        f"no T2 column carries the exact port-code sequence (page-scoped-chars leak "
        f"check, spec §7.3/§5): {col_values}"
    )
    assert _caption_texts(g, t2) == ["PORT MAINTENANCE SHUTDOWN DATES - 2026"]


#: Fix round 1, finding 1 (review): spec § 5 says "No cell of either table contains
#: `Note:` OR THE NOTE PROSE" — the shipped test checked only the "Note:" substring, missing
#: the three continuation lines. One DISTINCTIVE fragment per Task 0 evidence § 1.3's
#: fused-#table9 dump, r6-r9 (the four-line Note block), short enough to be robust to
#: whitespace/wrap cosmetics but specific enough that no other cell's real content could
#: contain it by coincidence:
#:   r6 "Note:"
#:   r7 "Dates are based on Daily Transport capacity and assume total capacity is allocated
#:       to grade types required. Dates are subject to change and are only a guide."
#:   r8 "The information provided is only an estimate based on information currently to
#:       hand and dates or order of loading are subject to change in accordance with the
#:       Export Accumulation"
#:   r9 "Guidelines, Port Queue Policy and matters beyond the control of CBH. Reliance on,
#:       use or distribution of the information contained within is at the risk of the
#:       recipient."
_NOTE_FRAGMENTS = [
    "Note:",                     # r6
    "Daily Transport capacity",  # r7
    "Export Accumulation",       # r8
    "Port Queue Policy",         # r9
]


def test_o2_note_block_is_not_carried_as_a_cell(cbh):
    """The Note block (spec § 1's third bullet; Task 0 evidence § 1.3's r6-r9, 4 lines) is
    not a cell of T1 or T2 — not the `Note:` label alone, and not any of its three
    continuation lines either (spec § 5: "or the note prose"). Gate-first, per R5, so
    removing the marker fails on the table count, not a KeyError."""
    g, tables = _o2_two_tables(cbh)
    for t in tables:
        for c in g.objects(t, TAB.hasCell):
            txt = g.value(c, TAB.cellText)
            if txt is None:
                continue
            txt = str(txt)
            for frag in _NOTE_FRAGMENTS:
                assert frag not in txt, f"{t} carries a note-prose cell ({frag!r}): {txt!r}"


#: C3's expected content, hardcoded from Task 0 evidence § 1.3 (`docs/superpowers/
#: 2026-09-28-box-split-evidence.md`). Keyed by table_uri SUFFIX (`#htableN`), never by
#: row-label text — evidence's own trap note: none of these rows carry a `tab:coversRow`
#: label (flat 20-column manifests, no stub column), so a label-keyed dict silently
#: collapses every row to its last. MEASURED here (task-4-report.md) that this keying
#: reproduces evidence's exact 4 hashes on today's tree, confirming the extraction below is
#: the SAME method. Content hash = sha256(json({"column_labels": sorted(set(label texts)),
#: "rows": sorted(tuple(cell texts by ascending column ordinal) for each row)})), first 16
#: hex — order-independent over ROWS, exact over each row's own cell-text tuple.
#:
#: Band-index blast radius (spec § 4 risk 2; evidence § 1.3/§ 1.4): the split lands at raw
#: band 9 and shifts band indices FROM 9 on by +2. All four roster table_uri suffixes
#: (1, 3, 5, 7) are < 9, so none shift — MEASURED, not assumed: evidence § 1.3 confirms
#: "not #table9 ... which is also why they are outside this loop's blast radius". Keying by
#: `#htableN` URI suffix is therefore safe before AND after the split; content-keying is
#: kept anyway (never by label) as the evidence's own worked method.
C3_EXPECTED = {
    "htable1": ("2312d93a98f271db", 20, 11),
    "htable3": ("2ab9c4eeb7977851", 20, 17),
    "htable5": ("478e3fc2457f7085", 20, 15),
    "htable7": ("91d0cf3cd58e17d5", 20, 6),
}


def _roster_content(g, table_uri):
    """The SAME extraction Task 0's evidence § 1.3 used (reproduced and confirmed to give
    the identical 4 hashes, task-4-report.md) — column labels as a sorted set, each row as
    a tuple of cell texts ordered by column ordinal, the row population as a sorted list
    (order-independent across rows, exact within one row)."""
    labels = set()
    for h in g.objects(table_uri, TAB.hasHeaderNode):
        for lc in g.objects(h, TAB.hasLabel):
            t = g.value(lc, TAB.cellText)
            if t is not None:
                labels.add(str(t))
    rows: dict = {}
    for e in g.objects(table_uri, TAB.hasCell):
        if (e, RDF.type, TAB.EntryCell) not in g:
            continue
        row = g.value(e, TAB.atRow)
        col = g.value(e, TAB.atColumn)
        txt = g.value(e, TAB.cellText)
        rows.setdefault(row, []).append((_col_ordinal(col), str(txt) if txt is not None else ""))
    row_tuples = []
    for _row, pairs in rows.items():
        pairs.sort(key=lambda p: (p[0] is None, p[0]))
        row_tuples.append(tuple(t for _, t in pairs))
    row_tuples.sort()
    return sorted(labels), row_tuples


def _content_hash(labels, rows):
    payload = json.dumps({"column_labels": labels, "rows": rows}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def test_c3_the_four_rosters_are_untouched(cbh):
    """THE CONTROL, no xfail — passes BEFORE and AFTER the split (rosters are outside its
    blast radius, comment above). Without this, O2 landing correctly would say nothing
    about whether the split's box-scoped reader corrupted unrelated closed boxes on the
    same page."""
    g = cbh.graph
    for suffix, (expected_hash, expected_cols, expected_rows) in C3_EXPECTED.items():
        uri = next(s for s in g.subjects() if str(s).endswith(f"#{suffix}"))
        labels, rows = _roster_content(g, uri)
        assert len(labels) == expected_cols, f"{suffix}: {len(labels)} column labels"
        assert len(rows) == expected_rows, f"{suffix}: {len(rows)} rows"
        assert _content_hash(labels, rows) == expected_hash, f"{suffix}: content changed"
