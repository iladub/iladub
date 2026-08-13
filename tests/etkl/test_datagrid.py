"""The data grid, tested against a TRANSCRIBED oracle — not against its own output.

Every recall number before this file was produced by eyeballing exclusion lists, which
cannot falsify anything. APPLE_P0_METADATA below is a hand transcription of the page:
each of its 44 lines read and classified as entries (data) or categories (metadata).

CLAUDE.md requires every vocabulary to ship with a worked example that conforms AND a
negative that must fail; both are here, synthetic and offline.
"""
import os

import pytest

from iladub.etkl.datagrid import (
    DataGrid, GAP, GridColumn, absorb_unit_markers, aggregate_members, confirms_aggregate,
    derive_data_grid, drawn_rules, family_of, ink_runs, is_contiguous, reconciles,
    _decimal,
)
from iladub.etkl.geometry import Line, Word, extract_words, text_lines

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
APPLE = os.path.join(CORPUS, "financial", "apple-fy2026q3-statements.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not fetched")

# --- THE ORACLE -------------------------------------------------------------------
# apple-fy2026q3-statements.pdf page 0, transcribed line by line (44 lines).
# METADATA = the title block, the boxhead, and the cut-in headings that carry a label
# but no entry. Everything else is an entry row, INCLUDING aggregate rows: a subtotal
# is a row of the grid (it mints no record, per §7, but it is data).
APPLE_P0_METADATA = {
    0,   # Apple Inc.                                        title
    1,   # CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS    title
    2,   # (In millions, except number of shares...)          unit note
    3,   # Three Months Ended  Nine Months Ended              boxhead spanner
    4,   # June 27, June 28, June 27, June 28,                boxhead leaf
    5,   # 2026 2025 2026 2025                                boxhead leaf, 2nd line
    6,   # Net sales:                                         cut-in heading
    10,  # Cost of sales:                                     cut-in heading
    15,  # Operating expenses:                                cut-in heading
    24,  # Earnings per share:                                cut-in heading
    27,  # Shares used in computing earnings per share:       cut-in heading
    30,  # (1) Net sales by reportable segment:               cut-in heading / panel
    37,  # (1) Net sales by category:                         cut-in heading / panel
}
APPLE_P0_LINES = 44
APPLE_P0_DATA = set(range(APPLE_P0_LINES)) - APPLE_P0_METADATA   # 31 rows


def _line(*words):
    ws = tuple(Word(t, x0, x1, top, top + 8.0) for t, x0, x1, top in words)
    return Line(ws, min(w.top for w in ws), max(w.bottom for w in ws))


# --- unit tests on the axioms -----------------------------------------------------

def test_contiguity_is_adjacency_not_order():
    """G9 needs no order relation: descending values are still groupable."""
    assert is_contiguous(["c", "c", "b", "a", "a"])
    assert is_contiguous([3, 3, 1, 2])
    assert not is_contiguous(["a", "b", "a"])          # 'a' resumes -> not grouped


def test_contiguity_is_relative_to_the_parent():
    """The stem's port level: NOT contiguous across the page, contiguous within month."""
    page = ["Mackay", "Gladstone", "Mackay", "Gladstone"]
    assert not is_contiguous(page)
    for month in (["Mackay", "Gladstone"], ["Mackay", "Gladstone"]):
        assert is_contiguous(month)


def test_aggregate_witness_is_exact():
    assert reconciles("76000", ["20000", "30000", "26000"])
    assert not reconciles("76001", ["20000", "30000", "26000"])
    assert not reconciles("76000", [])                 # a vacuous 0 == 0 never confirms


# --- G8 as a ROW-ADMISSION axiom (spec 2026-08-09) ---------------------------------
# The member values below are the REAL cbh page-0 column-13 cells, read off the page.
# Panel 1 is lines 10-19; panel 4 is lines 69-73.
CBH_PANEL1_MEMBERS = ["30,000", "50,000", "48,904", "50,000", "50,000",
                      "22,727", "36,000", "27,273", "25,000", "35,000"]
CBH_PANEL1_TOTAL = "374,904"
CBH_PANEL4_MEMBERS = ["54,000", "5,850", "36,000", "60,000", "22,858"]
CBH_PANEL4_TOTAL = "178,708"


def test_decimal_reads_thousands_separators_and_unit_markers():
    from decimal import Decimal
    from iladub.etkl.datagrid import _decimal
    assert _decimal("374,904") == Decimal("374904")
    assert _decimal("8 962 258") == Decimal("8962258")     # SI/ISO 31-0 separator
    assert _decimal("$ 78,678") == Decimal("78678")
    assert _decimal("-1,200") == Decimal("-1200")
    assert _decimal("Mackay") is None
    assert _decimal("") is None
    assert _decimal(None) is None


def test_aggregate_members_stops_at_the_previous_aggregate():
    """Rule B of spec 2026-08-09 §2.1: the admitted rows above i, back to the previous
    aggregate row, EXCLUSIVE. Ordinal only — no geometry and no values."""
    from iladub.etkl.datagrid import aggregate_members
    admitted = set(range(10, 20)) | set(range(26, 42))
    assert aggregate_members(20, admitted, set()) == tuple(range(10, 20))
    # once line 20 is an aggregate, the next candidate must not re-count panel 1
    assert aggregate_members(42, admitted | {20}, {20}) == tuple(range(26, 42))


def test_aggregate_members_is_empty_at_the_top_of_a_page():
    """A boxhead has nothing above it, and a vacuous sum never confirms."""
    from iladub.etkl.datagrid import aggregate_members
    assert aggregate_members(5, {7, 8, 9}, set()) == ()


def test_confirms_aggregate_on_the_real_cbh_panels():
    """The premise R75 rests on, at the level of the disposer: cbh's printed panel totals
    equal the exact sum of the real member cells."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{13: v} for v in CBH_PANEL1_MEMBERS]
    assert confirms_aggregate({13: CBH_PANEL1_TOTAL}, members)
    members4 = [{13: v} for v in CBH_PANEL4_MEMBERS]
    assert confirms_aggregate({13: CBH_PANEL4_TOTAL}, members4)


def test_f1_tampering_the_real_total_by_one_refuses_the_row():
    """FALSIFIER F1 (spec §4). The arithmetic must be LOAD-BEARING for admission, not
    decorative: the corpus sweep found it refuses nothing on real evidence, so it is
    exercised here against the real cbh members with the printed total off by exactly one.
    Same tamper pattern as tests/etkl/fixtures.py:1711."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{13: v} for v in CBH_PANEL1_MEMBERS]
    assert not confirms_aggregate({13: "374,905"}, members)
    assert not confirms_aggregate({13: "374,903"}, members)


def test_confirms_aggregate_refuses_a_vacuous_sum():
    """Zero members is an honest refusal, never a 0 == 0 confirmation — the same rule
    `reconciles` makes."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({13: "0"}, [])
    assert not confirms_aggregate({13: "374,904"}, [])


def test_confirms_aggregate_refuses_a_non_numeric_cell():
    """A measure-only row of words is a reprinted boxhead, not an aggregate."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({4: "Accepted", 5: "Accepted"},
                                  [{4: "Accepted", 5: "Accepted"}])


def test_confirms_aggregate_requires_every_occupied_cell_to_reconcile():
    """A universal quantifier, not a count: one column reconciling is not a witness.
    This is what refuses a period header whose first column happens to sum."""
    from iladub.etkl.datagrid import confirms_aggregate
    members = [{1: "100", 2: "10"}, {1: "200", 2: "20"}]
    assert confirms_aggregate({1: "300", 2: "30"}, members)
    assert not confirms_aggregate({1: "300", 2: "31"}, members)


def test_confirms_aggregate_refuses_a_column_with_no_summable_member():
    """A cell whose column no member populates has no witness — refuse, never treat the
    missing members as zero."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert not confirms_aggregate({1: "300", 3: "50"},
                                  [{1: "100"}, {1: "200"}])


def test_confirms_aggregate_drops_an_unparseable_member_cell():
    """The stated asymmetry, PINNED so it cannot drift silently: a member cell that is
    present but unparseable (a suppression marker) is dropped from the sum rather than
    refusing. The failure direction is toward refusal — a suppressed member makes the
    printed total exceed the computed sum — so this is recorded, not relied on."""
    from iladub.etkl.datagrid import confirms_aggregate
    assert confirms_aggregate({1: "300"}, [{1: "100"}, {1: "200"}, {1: ".."}])
    # the candidate side stays strict: one unparseable occupied cell refuses the row
    assert not confirms_aggregate({1: ".."}, [{1: "100"}, {1: "200"}])


def test_unit_marker_is_absorbed_not_kept_as_a_column():
    runs = ink_runs(_line(("Products", 59, 110, 143), ("$", 305, 311, 143),
                          ("78,678", 329, 363, 143)))
    assert [r.text for r in runs] == ["Products", "$", "78,678"]
    absorbed = absorb_unit_markers(runs)
    assert [r.text for r in absorbed] == ["Products", "78,678"]
    assert absorbed[1].x0 == 305                       # the marker's ink is carried, not dropped


def test_text_is_a_legal_column_family():
    """Excluding Text excluded every record table — a vessel name is data."""
    assert not GridColumn(0, 10, "Text").is_measure
    assert GridColumn(0, 10, "Quantity").is_measure
    assert not GridColumn(0, 10, None).is_measure


# --- the worked example that conforms ---------------------------------------------

def _conforming_page(tmp_path):
    """A three-column register: one text key, two quantity measures, plus a title and a
    cut-in heading that must both be refused."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "conforming.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(60, 780, "QUARTERLY REGISTER")            # title      -> metadata
    c.drawString(60, 750, "Region:")                       # cut-in     -> metadata
    for i, (name, a, b) in enumerate([("North", "120", "130"), ("South", "240", "250"),
                                      ("East", "360", "370"), ("West", "480", "490")]):
        y = 720 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_worked_example_conforms(tmp_path):
    g = derive_data_grid(_conforming_page(tmp_path), 0)
    assert g is not None, "the conforming example must yield a grid"
    assert len(g.columns) == 3
    assert [c.family for c in g.columns] == ["Text", "Quantity", "Quantity"]
    assert g.measures == (1, 2)
    assert g.grid_type == "UniformGrid"
    assert len(g.rows) == 4, f"expected the 4 data rows, got {g.rows}"
    assert g.universe == "alignment"
    assert "ColumnHomogeneity" in g.conforms


def _aggregating_page(tmp_path, total="1200"):
    """A register with a measure-only total row: no label anywhere on the line, the value
    alone under the first quantity column. The rows sum to 1200 and 1240."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / f"aggregating-{total}.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(60, 780, "QUARTERLY REGISTER")            # title -> metadata
    for i, (name, a, b) in enumerate([("North", "120", "130"), ("South", "240", "250"),
                                      ("East", "360", "370"), ("West", "480", "490")]):
        y = 720 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    c.drawString(200, 720 - 4 * 20, total)                 # the measure-only total row
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_worked_example_admits_a_measure_only_aggregate(tmp_path):
    """The worked example that CONFORMS for G8-as-row-admission: 120+240+360+480 = 1200,
    exactly, so the label-less row is a row of the grid."""
    g = derive_data_grid(_aggregating_page(tmp_path, total="1200"), 0)
    assert g is not None
    assert len(g.rows) == 5, f"4 data rows + the aggregate, got {g.rows}"
    assert len(g.aggregates) == 1
    (line, members), = g.aggregates.items()
    assert len(members) == 4
    assert "AggregateWitness" in g.conforms


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_negative_example_refuses_a_total_that_does_not_reconcile(tmp_path):
    """The negative that MUST fail: one off by a single unit. Exact, never a tolerance."""
    g = derive_data_grid(_aggregating_page(tmp_path, total="1201"), 0)
    assert len(g.rows) == 4, f"the non-reconciling row must stay out, got {g.rows}"
    assert not g.aggregates
    assert "no-reconciliation" in str(g.refusals.get(5)), g.refusals


def _period_header_below_data_page(tmp_path):
    """FALSIFIER F2 (spec §4). A bare period header REPRINTED BELOW the data rows, so it
    has a non-empty member run and its position can no longer refuse it. Only the
    arithmetic can, and it must."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "period-header-below.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(60, 780, "CONDENSED STATEMENTS OF OPERATIONS")
    for i, (name, a, b) in enumerate([("Products", "120", "130"), ("Services", "240", "250"),
                                      ("Total net sales", "360", "380")]):
        y = 750 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    y = 750 - 3 * 20
    c.drawString(200, y, "2026")           # the bare period header, BELOW the data
    c.drawString(300, y, "2025")
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_f2_a_period_header_below_the_data_is_refused_by_the_arithmetic(tmp_path):
    """FALSIFIER F2. Measured on the real corpus, every bare period header is refused
    because it sits ABOVE every data row — the arithmetic refuses nothing at all, so its
    refusal branch would ship unexercised (spec §3.3).

    Here the header has 3 admitted rows above it, so only the sum can refuse it. The
    assertion is on the REASON, not on absence: absence would pass vacuously even if the
    witness were never consulted.

    measured-on-fixture: no real corpus document reprints a period header below its data."""
    path = _period_header_below_data_page(tmp_path)
    g = derive_data_grid(path, 0)
    assert g is not None
    # locate the header by its CONTENT, not by assuming it is the last line
    lines = [l for l in sorted(text_lines(extract_words(path, 0)), key=lambda l: l.top)
             if l.words]
    header_line = next(i for i, l in enumerate(lines)
                       if [w.text for w in sorted(l.words, key=lambda w: w.x0)] == ["2026", "2025"])
    assert g.refusals[header_line] == "AggregateWitness/no-reconciliation", g.refusals
    assert not g.aggregates
    assert len(g.rows) == 3, f"only the three data rows, got {g.rows}"


def _prose_page(tmp_path):
    """Four rows of two aligned TEXT columns: the shape of a grid, none of the substance."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "prose.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    for i, (a, b) in enumerate([("alpha", "beta"), ("gamma", "delta"),
                                ("epsilon", "zeta"), ("eta", "theta")]):
        c.drawString(60, 720 - i * 20, a)
        c.drawString(300, 720 - i * 20, b)
    c.save()
    return path


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_negative_prose_must_be_refused(tmp_path):
    """A rectangle of text columns alone is aligned prose, and must NOT be a data grid."""
    assert derive_data_grid(_prose_page(tmp_path), 0) is None


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_a_measure_column_admits_one_value_only(tmp_path):
    """The stub may hold several address levels in one column; a MEASURE may not.

    Built because mutation testing showed the guard was unreachable on all three real
    oracles — no corpus row happens to put two runs in a measure cell. An unreachable
    guard is an unproven one, so this fixture reaches it: the last row carries a stray
    second number inside the first measure column, and must be refused rather than have
    the two silently joined into one cell."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = str(tmp_path / "double_measure.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 10)
    for i, (name, a, b) in enumerate([("North", "120", "130"), ("South", "240", "250"),
                                      ("East", "360", "370"), ("West", "480", "490")]):
        y = 720 - i * 20
        c.drawString(60, y, name)
        c.drawString(200, y, a)
        c.drawString(300, y, b)
    y = 720 - 4 * 20
    c.drawString(60, y, "Stray")
    c.drawString(200, y, "555")
    c.drawString(235, y, "666")          # a second value inside the SAME measure column
    c.drawString(300, y, "777")
    c.save()

    g = derive_data_grid(path, 0)
    assert g is not None
    lines = [l for l in sorted(text_lines(extract_words(path, 0)), key=lambda l: l.top)
             if l.words]
    stray = next(i for i, l in enumerate(lines)
                 if " ".join(w.text for w in l.words).startswith("Stray"))
    assert stray not in set(g.rows), "two runs in one measure column must refuse the row"
    assert len(g.rows) == 4, "the four well-formed rows still stand"


@pytest.mark.skipif(pytest.importorskip("reportlab") is None, reason="reportlab missing")
def test_non_degeneracy_is_a_redundant_backstop(tmp_path):
    """G1b is UNREACHABLE as a distinct refusal, and this pins the fact rather than
    hiding it.

    Found by mutation: deleting the `if not measures: return None` guard leaves the whole
    suite green, because the two conditions are entangled by construction — if no column
    is a measure then no row can carry a measure, so tab:RowAddressability refuses every
    row and the grid is empty anyway. No page can exist on which G1b is the only refuser.

    G1b is therefore kept as an explicit early exit and documented as a backstop, the
    disposition R9 already established for the conservation shape. This test fails if a
    future change to RowAddressability makes G1b load-bearing, which is exactly when
    someone needs to know."""
    from iladub.etkl.datagrid import GAP as _  # noqa: F401  (module import guard)
    import iladub.etkl.datagrid as dg

    path = _prose_page(tmp_path)
    assert dg.derive_data_grid(path, 0) is None

    # ... and it is still refused with the guard removed, which is the redundancy claim.
    src_guard = "if not measures:"
    import inspect
    assert src_guard in inspect.getsource(dg.derive_data_grid), (
        "the G1b guard has moved; re-derive whether it is still redundant")


# --- the oracle -------------------------------------------------------------------

@corpus_only
def test_drawn_rules_exclude_fills():
    """apple page 0 has 2 drawn vertical rules, not the 678 an edge-based reader sees."""
    assert len(drawn_rules(APPLE, 0)) == 2


@corpus_only
def test_apple_p0_admits_no_metadata():
    """SOUNDNESS: not one transcribed metadata line may enter the grid.

    This is the half that matters most — a metadata row admitted as data is a silent
    wrong reading, which §7 ranks worse than an honest miss."""
    g = derive_data_grid(APPLE, 0)
    assert g is not None
    admitted = set(g.rows)
    leaked = sorted(admitted & APPLE_P0_METADATA)
    assert not leaked, f"metadata admitted as data: lines {leaked}"


@corpus_only
def test_apple_p0_recall_against_the_transcription():
    """COMPLETENESS, measured against the oracle and PINNED at what is achieved today.

    The assertion is a floor, not an aspiration: it fails if a change silently loses
    rows. The gap to 31 is real and named in the spec, not smoothed over here."""
    g = derive_data_grid(APPLE, 0)
    admitted = set(g.rows)
    recovered = admitted & APPLE_P0_DATA
    missed = sorted(APPLE_P0_DATA - admitted)
    assert len(recovered) == len(APPLE_P0_DATA), (
        f"recall regressed: {len(recovered)}/{len(APPLE_P0_DATA)}; missed {missed}")


# --- the second oracle: the reference document ------------------------------------
STEM = os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf")
stem_only = pytest.mark.skipif(not os.path.exists(STEM), reason="corpus not fetched")

# graincorp-stem-2026-07-31.pdf page 0, transcribed (65 lines). METADATA is the title
# block, the three-line wrapped header, and the footnote. Every vessel row AND every
# Total row is data — an aggregate is a row of the grid.
STEM_P0_METADATA = {
    0,   # GRAINCORP SHIPPING STEM                      title
    1,   # GrainCorp Operations Ltd ABN 52003875401     title
    2,   # SHIPPING STEM                                title
    3,   # Friday, 31 July 2026                         date caption
    4,   # Date of Grain                                header block, wrapped line 1
    5,   # Unique Slot Loading Date Nomination ...      header block, wrapped line 2
    6,   # GC Fin Year Month Port Reference Number ...  header leaf row
    64,  # GrainCorp advise that the load dates ...     footnote
}
STEM_P0_LINES = 65
STEM_P0_DATA = set(range(STEM_P0_LINES)) - STEM_P0_METADATA   # 57 rows


@stem_only
def test_stem_p0_admits_no_metadata():
    """SOUNDNESS on the reference document — the one with an adjudicated 0.95 floor."""
    g = derive_data_grid(STEM, 0)
    assert g is not None
    leaked = sorted(set(g.rows) & STEM_P0_METADATA)
    assert not leaked, f"metadata admitted as data: lines {leaked}"


@stem_only
def test_stem_p0_recall_against_the_transcription():
    """COMPLETE: all 57 entry rows, including the month and season totals whose label
    lives out in the index block, left of the rectangle."""
    g = derive_data_grid(STEM, 0)
    recovered = set(g.rows) & STEM_P0_DATA
    assert len(recovered) == len(STEM_P0_DATA), (
        f"recall regressed: {len(recovered)}/{len(STEM_P0_DATA)}")


# --- the third oracle: a different document class (time-series panels) -------------
ONS = os.path.join(CORPUS, "gov-stats", "ons-index-of-services-2026-02.pdf")
ons_only = pytest.mark.skipif(not os.path.exists(ONS), reason="corpus not fetched")

# ons-index-of-services page 7, transcribed (68 lines). METADATA is the title, the
# five-line wrapped boxhead, the section captions, the series-code rows, and the
# footnote block. The weights row (8) is data: it is a row of values.
ONS_P7_METADATA = {
    0,                       # IOS1 IOS: Index of Services 1            title
    1, 2,                    # subtitle / 'Industry sections (SIC2007)'
    3, 4, 5, 6, 7,           # the five-line wrapped boxhead + 'Section G-T ...'
    9, 37, 44,               # series-code rows (S2KU S2MV KI7B ...)
    15, 36, 43,              # panel captions
    60, 61, 62, 63, 64, 65,  # footnotes 1-4
    66, 67,                  # sources / contact block
}
ONS_P7_LINES = 68
ONS_P7_DATA = set(range(ONS_P7_LINES)) - ONS_P7_METADATA   # 46 rows


@ons_only
def test_ons_p7_admits_no_metadata():
    """This transcription found three REAL leaks on a page previously reported as fine:
    the title and both footnote lines, each occupying exactly one measure column and
    contradicting it. They were admitted by a ">= 2 measure columns" carve-out that had
    been justified by row counts on pages with no oracle."""
    g = derive_data_grid(ONS, 7)
    assert g is not None
    leaked = sorted(set(g.rows) & ONS_P7_METADATA)
    assert not leaked, f"metadata admitted as data: lines {leaked}"


@ons_only
def test_ons_p7_recall_against_the_transcription():
    """COMPLETE: all 46 entry rows, once the stub is read as an addressing axis with
    levels ('2024 Q4 ...' places year and quarter as two levels of one address)."""
    g = derive_data_grid(ONS, 7)
    recovered = set(g.rows) & ONS_P7_DATA
    assert len(recovered) == len(ONS_P7_DATA), (
        f"recall regressed: {len(recovered)}/{len(ONS_P7_DATA)}")


CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_repeated_headers_are_not_data():
    """A PARTIAL oracle: cheap soundness without a full transcription.

    cbh reprints its header once per port section. Four such rows were being admitted as
    data, and were only caught when the every-measure refutation landed and the row count
    FELL — which I first read as a regression. Row count is not a quality measure; this
    test is, for the part it covers."""
    g = derive_data_grid(CBH, 0)
    assert g is not None
    lines = [l for l in sorted(text_lines(extract_words(CBH, 0)), key=lambda l: l.top)
             if l.words]
    headers = {i for i, l in enumerate(lines)
               if " ".join(w.text for w in l.words).startswith("VNA #")}
    assert headers, "fixture drift: the repeated header rows are gone"
    leaked = sorted(set(g.rows) & headers)
    assert not leaked, f"repeated header rows admitted as data: {leaked}"


@corpus_only
def test_apple_p0_shape():
    g = derive_data_grid(APPLE, 0)
    assert g.grid_type == "UniformGrid"
    assert len(g.measures) == 4, "the four period columns"
    assert g.universe == "alignment", "apple is borderless: 2 drawn rules, no usable universe"


# --- emission: the grid as an asserted object with an auditable admission ----------

@corpus_only
def test_emitted_grid_answers_why_from_the_graph_alone():
    """The record François asked for: 'I found the data grid because it conforms to this,
    this and this, and refuted this, this and this.'

    Answerable by SPARQL over the emitted graph, with no Python in the loop — which is
    the whole point of the grid being an asserted object rather than a transient."""
    from rdflib import Graph, URIRef
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(APPLE, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(APPLE, 0)
    g = Graph()
    doc = URIRef("urn:test:apple")
    uri = emit_data_grid(g, grid, lines, doc, 0)

    conformed = {str(r[0]).rsplit("#", 1)[1] for r in g.query(
        "SELECT ?a WHERE { ?grid <https://w3id.org/iladub/tab#conformsTo> ?a }")}
    assert "ColumnHomogeneity" in conformed and "RowAddressability" in conformed

    # `?o a tab:RefusedRow` is load-bearing, not decoration (R81 face (c)): the option space
    # also carries the no-change option — "refuse the page", which was available whatever the
    # grid found and is rejected for reading ink, not for being an unreadable line. Counting
    # every rejected OPTION would count it as a refused LINE, which is not what this
    # assertion claims. The sibling test below binds the same type for the same reason.
    refused = [str(r[0]) for r in g.query("""
        SELECT ?why WHERE {
          ?d a <https://w3id.org/iladub/dec#DecisionHolon> ;
             <https://w3id.org/iladub/dec#chosen> ?grid ;
             <https://w3id.org/iladub/dec#optionSpace> ?o .
          ?o a <https://w3id.org/iladub/tab#RefusedRow> ;
             <https://w3id.org/iladub/dec#rejectedBecause> ?why }""")]
    assert len(refused) == len(APPLE_P0_METADATA), (
        f"every refused line must be carried: {len(refused)} vs {len(APPLE_P0_METADATA)}")

    cells = list(g.query(
        "SELECT ?c WHERE { ?grid <https://w3id.org/iladub/tab#hasDataCell> ?c }"))
    assert len(cells) == 31 * 5, f"31 rows x 5 columns of entries, got {len(cells)}"

    kinds = {str(r[0]) for r in g.query(
        f"SELECT ?t WHERE {{ <{uri}> a ?t }}")}
    assert "https://w3id.org/iladub/tab#DataGrid" in kinds
    assert "https://w3id.org/iladub/tab#UniformGrid" in kinds


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_emitted_aggregate_rows_reuse_the_loop_h_class():
    """No new class is minted: an aggregate row of the grid is typed with the SAME
    tab:DetectedAggregationRow the extraction path already uses, carrying its operands, so
    tab:DetectedAggregationRowShape is satisfied as that shape already stands."""
    from rdflib import Graph, URIRef
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(CBH, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(CBH, 0)
    g = Graph()
    uri = emit_data_grid(g, grid, lines, URIRef("urn:test:cbh"), 0)

    agg = set(g.subjects(
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("https://w3id.org/iladub/tab#DetectedAggregationRow")))
    assert len(agg) == 4, f"expected the four panel totals, got {len(agg)}"
    for a in agg:
        assert (a, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef("https://w3id.org/iladub/tab#AggregationRow")) in g, (
            "the SUPERTYPE must be a direct triple: feed.py:217 tests it without inference")
        funcs = list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregationFunction")))
        assert [str(f) for f in funcs] == ["sum"], funcs
        ops = list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregates")))
        assert len(ops) >= 1, "a detected aggregation row needs at least one operand"
        # every operand is a row of THIS grid
        assert all(str(o).startswith(str(uri) + "-r") for o in ops), ops
    counts = sorted(len(list(g.objects(a, URIRef("https://w3id.org/iladub/tab#aggregates"))))
                    for a in agg)
    assert counts == [5, 10, 14, 16]


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_emitted_aggregate_rows_satisfy_their_shape():
    """The closed-world membrane: pySHACL over the emitted grid, against the shipped
    tab:DetectedAggregationRowShape — unedited by this loop."""
    from rdflib import Graph, URIRef
    from pyshacl import validate
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(CBH, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(CBH, 0)
    g = Graph()
    emit_data_grid(g, grid, lines, URIRef("urn:test:cbh"), 0)
    shapes = Graph().parse("vocab/shapes/tab-shapes.ttl", format="turtle")
    conforms, _, text = validate(g, shacl_graph=shapes, inference="rdfs", advanced=True)
    assert conforms, text


@corpus_only
def test_emission_carries_every_refused_line_with_its_reason():
    """§5: context is carried, not discarded. A refused line keeps its provenance."""
    from rdflib import Graph, URIRef
    from iladub.etkl.datagrid import emit_data_grid

    lines = [l for l in sorted(text_lines(extract_words(STEM, 0)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(STEM, 0)
    g = Graph()
    emit_data_grid(g, grid, lines, URIRef("urn:test:stem"), 0)
    rows = list(g.query("""
        SELECT ?o ?why ?src WHERE {
          ?o a <https://w3id.org/iladub/tab#RefusedRow> ;
             <https://w3id.org/iladub/dec#rejectedBecause> ?why ;
             <http://www.w3.org/ns/prov#wasDerivedFrom> ?src }"""))
    assert len(rows) == len(STEM_P0_METADATA), (
        f"{len(rows)} refusals carried, expected {len(STEM_P0_METADATA)}")
    assert all(str(r[2]).startswith("urn:test:stem#p0-line") for r in rows)


@corpus_only
@pytest.mark.parametrize("path,page", [
    (APPLE, 0),
    (os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf"), 0),
    (os.path.join(CORPUS, "gov-stats", "ons-index-of-services-2026-02.pdf"), 7),
])
def test_emitted_graph_crosses_the_membrane(path, page):
    """The emitted grid must survive the SAME closed-world membrane the pipeline uses.

    This is the gate wiring will face, so it is measured now rather than discovered
    later: the first emission failed it 155 times, every entry cell lacking the
    tab:hasBBox that tab:EntryCellPhysicalShape requires."""
    from rdflib import Graph, URIRef
    from iladub.etkl import membrane
    from iladub.etkl.datagrid import emit_data_grid

    if not os.path.exists(path):
        pytest.skip("corpus not fetched")
    lines = [l for l in sorted(text_lines(extract_words(path, page)), key=lambda l: l.top)
             if l.words]
    grid = derive_data_grid(path, page)
    g = Graph()
    emit_data_grid(g, grid, lines, URIRef("urn:test:doc"), page)

    vocab = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")
    shapes = Graph()
    shapes.parse(os.path.join(vocab, "shapes", "tab-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(vocab, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    ont = Graph().parse(os.path.join(vocab, "ontology", "tab.ttl"), format="turtle")
    ok, report = membrane.validate(g, shapes, ont)
    assert ok, report[:2000]


# --- the admission holon is a real decision (R81) ---------------------------------
#
# The oracle here is `vocab/shapes/dec-shapes.ttl`, which this loop may not edit: it was
# authored by a different act than the emitter it judges, and that is the only reason its
# verdict means anything. Measured before-state (docs/loops/2026-08-10-decision-membrane-
# baseline.md): `<ons>/p7#p7-datagrid-admission` and `…p8…` refuse `dec:decidedBy` under
# BOTH closures — the only corpus refusal `dec-shapes.ttl` produced at compile scope.

VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")


def _synthetic_grid(n_rows, n_cols, refused=0):
    """A grid built by hand — because the refusal-FREE case cannot come off the corpus.

    `derive_data_grid` records a refusal for every page line it did not admit
    (datagrid.py:582-583), so every derived grid refuses something and R81(c) — the
    unconditional no-change option — stays invisible on real documents. The spec records it
    as unobserved for exactly this reason; this fixture is its only evidence."""
    cols = tuple(GridColumn(10.0 + 40 * k, 50.0 + 40 * k, "Numeric") for k in range(n_cols))
    lines = [_line(*[(f"r{r}c{k}", 15.0 + 40 * k, 45.0 + 40 * k, 100.0 + 20 * r)
                     for k in range(n_cols)])
             for r in range(n_rows + refused)]
    grid = DataGrid(rows=tuple(range(n_rows)), columns=cols, universe="alignment",
                    conforms=("ColumnHomogeneity", "RowAddressability"),
                    refusals={n_rows + i: "unplaceable" for i in range(refused)})
    return grid, lines


def _emit_synthetic(n_rows, n_cols, refused=0, page=0):
    """(graph, grid_uri, admission_uri) for a synthetic grid."""
    from rdflib import Graph, URIRef
    from iladub.etkl.datagrid import emit_data_grid

    grid, lines = _synthetic_grid(n_rows, n_cols, refused)
    g = Graph()
    uri = emit_data_grid(g, grid, lines, URIRef("urn:test:doc"), page)
    return g, uri, URIRef(f"{uri}-admission")


def _dec_membrane(g):
    """(conforms, text) against the SHIPPED closure, through `membrane._payload` — matching
    `membrane._validate_pyshacl` exactly (spec 2026-08-13-membrane-parity-design.md §3: since
    parity, that function validates `_payload`'s re-parsed graph, not `subclass_closure`'s
    live one, and this helper must track it or the claim is false). Called directly rather
    than through `membrane.validate` because these fixtures mint blank-node decision holons
    and rudof cannot evaluate dec-shapes.ttl's sh:sparql constraint on a blank-node focus
    (membrane.validate's own docstring)."""
    from rdflib import Graph
    from pyshacl import validate
    from iladub.etkl import membrane

    ont = Graph()
    for f in ("dec.ttl", "iladub.ttl", "etkl.ttl", "tab.ttl"):
        ont.parse(os.path.join(VOCAB, "ontology", f), format="turtle")
    shapes = Graph().parse(os.path.join(VOCAB, "shapes", "dec-shapes.ttl"), format="turtle")
    expanded, _ = membrane._payload(g, ont)
    conforms, _, text = validate(expanded, shacl_graph=shapes,
                                 inference="none", advanced=True)
    return bool(conforms), text


@pytest.mark.parametrize("refused,case", [(0, "refusal-free"), (2, "refusing")])
def test_the_admission_holon_is_a_real_decision(refused, case):
    """R81 (a′) and (c). Every admission holon — from EVERY path that mints one — must be a
    decision `dec:DecisionHolonShape` recognises: >= 2 deliberated options, exactly one
    chosen and in the space, and an accountable agent.

    The two cases are not redundant. A grid that refused rows already clears `minCount 2` on
    its refused rows alone; only the refusal-free grid can show that the no-change option is
    emitted UNCONDITIONALLY rather than as a function of the outcome."""
    from rdflib import Namespace
    from iladub.etkl.decisionlog import _READER_AGENT
    DEC = Namespace("https://w3id.org/iladub/dec#")

    g, uri, dec_uri = _emit_synthetic(3, 2, refused=refused)

    conforms, text = _dec_membrane(g)
    assert conforms, f"[{case}] {text}"

    options = list(g.objects(dec_uri, DEC.optionSpace))
    assert len(options) >= 2, f"[{case}] a real decision deliberates >= 2 options: {options}"
    assert list(g.objects(dec_uri, DEC.chosen)) == [uri], f"[{case}] chosen is the grid"
    assert uri in options, f"[{case}] the chosen option must be in the option space"
    assert list(g.objects(dec_uri, DEC.decidedBy)) == [_READER_AGENT], (
        f"[{case}] the admission names the same automated reader that decided every verdict "
        f"it supersedes")


def test_the_no_change_option_names_the_ink_the_grid_read():
    """R81 (c), the anti-decoration half. "Refuse the page" was available whatever the grid
    found, so it belongs in the space in both cases — but an option whose
    `dec:rejectedBecause` says the same thing every time is decoration, not deliberation
    (Global Constraint 4). The oracle: two grids that read DIFFERENT amounts of ink must
    reject it for different reasons."""
    from rdflib import Namespace
    DEC = Namespace("https://w3id.org/iladub/dec#")

    def _no_change(n_rows, n_cols, refused):
        g, uri, dec_uri = _emit_synthetic(n_rows, n_cols, refused=refused)
        opts = [o for o in g.objects(dec_uri, DEC.optionSpace)
                if o != uri and not str(o).startswith(f"{uri}-refused")]
        assert len(opts) == 1, f"exactly one no-change option, got {opts}"
        why = list(g.objects(opts[0], DEC.rejectedBecause))
        assert len(why) == 1, f"the no-change option must say why it was rejected: {why}"
        return str(why[0])

    small = _no_change(2, 2, 0)          # 2 rows x 2 columns admitted
    large = _no_change(5, 3, 1)          # 5 rows x 3 columns admitted
    assert small != large, (
        f"the no-change option says the same thing whatever the grid read: {small!r}")


def test_the_grid_label_states_what_the_grid_is():
    """R81 (b). `effective-chain.rq` reads `?d dec:chosen/rdfs:label ?chosen`, so an
    unlabelled grid leaves a consumer knowing that something replaced the superseded band
    but not what. A CONSTANT label binds `?chosen` and tells them just as little — so the
    oracle is that the label MOVES with what the grid is: its shape and its page."""
    from rdflib.namespace import RDFS

    def _label(n_rows, n_cols, page):
        g, uri, _ = _emit_synthetic(n_rows, n_cols, page=page)
        lab = g.value(uri, RDFS.label)
        assert lab is not None, "the grid carries no rdfs:label"
        return str(lab)

    base = _label(3, 2, 0)
    other_shape = _label(2, 3, 0)
    other_page = _label(3, 2, 4)
    assert len({base, other_shape, other_page}) == 3, (
        f"the label does not state both shape and page: {base!r} / {other_shape!r} / "
        f"{other_page!r}")


def test_effective_chain_binds_chosen_for_the_admission_verdict():
    """The gap `document.py:1473-1476` names and hands over: "the query's `?chosen` is
    UNBOUND on the row this record produces, because `emit_data_grid`'s dec:chosen names the
    grid itself and the grid carries no rdfs:label … it belongs with whoever owns
    emit_data_grid."

    The four triples added below are the DRIVER's (document.py:1497-1503), reproduced so the
    query's precondition holds off-corpus; this test owns none of them. The only thing under
    test is the label on the grid."""
    from rdflib import Literal, Namespace
    from rdflib.namespace import RDFS, XSD
    DEC = Namespace("https://w3id.org/iladub/dec#")

    g, uri, admission = _emit_synthetic(3, 2)
    g.add((admission, DEC.regarding, uri))
    g.add((admission, DEC.order, Literal(0, datatype=XSD.integer)))
    g.add((admission, RDFS.label, Literal("verdict")))
    g.add((admission, DEC.rationale, Literal("the data grid's reading was adopted")))

    q = open(os.path.join(VOCAB, "queries", "effective-chain.rq"), encoding="utf-8").read()
    rows = [r.asdict() for r in g.query(q, initBindings={"region": uri})]
    assert rows, "effective-chain.rq returned nothing for the admission verdict"
    assert all(r.get("chosen") is not None for r in rows), (
        f"?chosen is UNBOUND — the consumer learns that something replaced the band, not "
        f"what: {rows}")
    assert str(rows[0]["chosen"]) == str(g.value(uri, RDFS.label))


# --- wiring: the fallback, and what it must NOT touch -----------------------------

ONS_P = os.path.join(CORPUS, "gov-stats", "ons-index-of-services-2026-02.pdf")


@pytest.mark.skipif(not os.path.exists(ONS_P), reason="corpus not fetched")
def test_fallback_fires_only_where_the_page_produced_nothing_at_all():
    """ons page 7 asserted nothing AND escalated nothing — a degenerate 1.0 over an empty
    reading. The data grid gives it 276 real cells.

    The gate is nothing-at-all, not merely nothing-asserted. A page that ESCALATED has
    already accounted for its ink, so appending a reading there masks an honest
    escalation and double-counts the same tokens on both sides of the ratio. Both were
    measured: apple page 1 reported 0.5941 under the broader gate, and four
    escalation-path tests failed because a second region appeared where they had pinned
    exactly one."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(ONS_P, 7, validate_shapes=False, datagrid_fallback=False)
    on = compile_tables(ONS_P, 7, validate_shapes=False, datagrid_fallback=True)
    assert off.asserted == 0 and off.escalated == 0
    assert sum(r.cells for r in off.regions) == 0
    assert sum(r.cells for r in on.regions) == 276


@corpus_only
def test_fallback_never_masks_an_escalation():
    """apple page 1 escalates. The fallback must leave it alone — an escalation is a
    result, and filling it in silently is what §7 forbids."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(APPLE, 1, validate_shapes=False, datagrid_fallback=False)
    on = compile_tables(APPLE, 1, validate_shapes=False, datagrid_fallback=True)
    assert off.escalated > 0, "fixture drift: this page is supposed to escalate"
    assert on.score == off.score
    assert len(on.regions) == len(off.regions)


@stem_only
def test_fallback_leaves_the_adjudicated_document_byte_identical():
    """The stem carries the corpus's only adjudicated verdict (cor:CompilesAbove, floor
    0.95). The fallback must not move it by a single cell — it fires only on a page that
    asserts nothing, and this page asserts 586."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(STEM, 0, validate_shapes=False, datagrid_fallback=False)
    on = compile_tables(STEM, 0, validate_shapes=False, datagrid_fallback=True)
    assert on.score == off.score
    assert sum(r.cells for r in on.regions) == sum(r.cells for r in off.regions) == 586


@corpus_only
def test_fallback_output_passes_full_shacl_through_the_production_path():
    """validate_shapes=True is the gate the pipeline applies to any asserted holon."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(ONS_P, 7, validate_shapes=True, datagrid_fallback=True)
    assert sum(r.cells for r in rep.regions) == 276


# --- R72: an empty reading must not score perfect ---------------------------------

@corpus_only
def test_grid_gate_separates_prose_from_table_pages():
    """The page-level verdict the score consults: 17 of 27 corpus pages carry a table."""
    from iladub.etkl.datagrid import page_has_table

    assert page_has_table(APPLE, 0)
    bfs = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
    if os.path.exists(bfs):
        assert not page_has_table(bfs, 0), "bfs page 0 is a press release, not a table"
        assert page_has_table(bfs, 6)


@pytest.mark.skipif(not os.path.exists(os.path.join(
    CORPUS, "gov-stats", "ons-index-of-services-2026-02.pdf")), reason="corpus not fetched")
def test_an_unread_table_page_no_longer_scores_perfect():
    """R72. `score = 1.0 if denom == 0` gave a page that read NOTHING a perfect score,
    whether it held prose or a table nobody could read — 11 of 27 corpus pages.

    Now the grid gate decides: prose keeps 1.0 (nothing to read), a table that yielded no
    cells scores 0.0 (failed to read). Which is also what finally makes the data grid's
    contribution visible as a score."""
    from iladub.etkl.compile import compile_tables

    p = os.path.join(CORPUS, "gov-stats", "ons-index-of-services-2026-02.pdf")
    unread = compile_tables(p, 7, validate_shapes=False, datagrid_fallback=False)
    assert unread.asserted == 0 and unread.escalated == 0
    assert unread.score == 0.0, "a table page that read nothing must not score 1.0"

    read = compile_tables(p, 7, validate_shapes=False, datagrid_fallback=True)
    assert sum(r.cells for r in read.regions) == 276
    assert read.score == 1.0

    prose = compile_tables(p, 0, validate_shapes=False, datagrid_fallback=False)
    assert prose.asserted == 0 and prose.escalated == 0
    assert prose.score == 1.0, "a prose page has nothing to read and is not a failure"


# --- the fourth oracle: a page the pipeline ESCALATES ------------------------------
# apple page 1, transcribed (43 lines). Chosen because compile_tables asserts NOTHING
# here and escalates instead — so it is the case R73 turns on: is a data-grid reading
# actually better than the escalation it would replace?
#
# METADATA is the title block, the two-line boxhead, the cut-in headings, and three
# rows that carry no entry at all:
#   34  'Commitments and contingencies'  a line item with its values omitted, which is
#                                        standard balance-sheet practice
#   36, 37                               wrap continuations of the 'Common stock ...'
#                                        label, whose values land on line 38
# A data row is a row WITH entries; a label fragment is not one.
APPLE_P1_METADATA = {0, 1, 2, 3, 4, 5, 6, 14, 21, 22, 29, 34, 35, 36, 37}
APPLE_P1_DATA = set(range(43)) - APPLE_P1_METADATA          # 28 rows


@corpus_only
def test_apple_p1_is_complete_and_sound():
    """The page the pipeline escalates: the data grid reads all 28 entry rows, none of
    the 15 metadata lines. This is the measured warrant for R73 — replacing this
    escalation with this reading is an improvement, not a swap."""
    g = derive_data_grid(APPLE, 1)
    assert g is not None
    admitted = set(g.rows)
    assert not sorted(admitted & APPLE_P1_METADATA), "metadata admitted as data"
    assert admitted & APPLE_P1_DATA == APPLE_P1_DATA, (
        f"missed {sorted(APPLE_P1_DATA - admitted)}")


@corpus_only
def test_the_pipeline_escalates_the_page_the_grid_reads_completely():
    """The R73 gap, stated as a test: the shipped reader asserts zero cells on a page the
    data grid reads completely. The fallback cannot help here, because filling in an
    escalation would mask it and double-count its tokens."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(APPLE, 1, validate_shapes=False, datagrid_fallback=True)
    assert rep.asserted == 0, "fixture drift: this page is supposed to assert nothing"
    assert rep.escalated > 0
    assert len(derive_data_grid(APPLE, 1).rows) == 28


# --- R73: adoption, and what it may and may not withdraw ---------------------------

@corpus_only
def test_adoption_is_off_by_default_at_page_scope():
    """Page scope is not where the decision belongs (spec 2026-08-09 §5.1).

    The register's original reason — 'compile_document compiles each page standalone before
    re-compiling continuation pages' — is MEASURED FALSE: the driver makes one pass and the
    carried reading is an INPUT to page p's compile.

    The real reason the page-scope flag stays off is the refusal branch, whose first half is
    structural: a single-page compile cannot chain AT ALL (`CompilationReport` carries no chain
    concept), so it would never see the other two pages, whatever it scored. The score
    corroborates it SAME-PAGE: stem p1 standalone adopts at 811 FLAT cells and scores 0.9588,
    against 0.9706 for the driver's own reading of that same page 1 (Loop M, recorded at
    docs/superpowers/residues.md R29) — page scope reads it WORSE. The counts are NOT
    comparable (R29's 825 is tokens under the driver; 811 is standalone cells); only the scores
    share a scale. At document scope the whole stem is one chain of 3, 2152 cells, at
    0.9654553611484971. See tests/test_corpus_stem.py's
    test_page_scope_adoption_would_have_taken_the_page_the_driver_reads."""
    from iladub.etkl.compile import compile_tables

    default = compile_tables(APPLE, 1, validate_shapes=False)
    explicit = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=False)
    assert default.score == explicit.score == 0.0
    assert default.escalated > 0


@corpus_only
def test_adoption_withdraws_only_the_escalation_of_ink_it_READ():
    """Line-granular, both directions pinned (spec §5.3).

    Not 1.0000: the section labels the grid never admitted keep escalating.
    Not 0.594: the lines the grid DID read are not counted on both sides."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=False)
    on = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=True)
    assert off.asserted == 0 and off.escalated > 0
    assert on.asserted > 0
    assert 0 < on.escalated < off.escalated, "residue must survive, and must shrink"
    assert on.score < 1.0, "an adopted page must never score 1.0000 by construction"
    assert on.score > off.score
    print(f"\napple p1 adopted: {on.asserted}/{on.escalated} score={on.score:.4f}")
    grid_cells = sum(r.cells for r in on.regions)
    assert grid_cells == 28 * 3, "28 entry rows x 3 columns"


@corpus_only
def test_adoption_keeps_the_band_index_contract():
    """Region report index IS band index (page_bands' pinned enumeration contract). The
    driver reads it at five sites; adoption used to collapse the tuple to length 1."""
    from iladub.etkl.compile import compile_tables, page_bands

    bands = page_bands(APPLE, 1)
    on = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=True)
    assert len(on.regions) >= len(bands) + 1
    assert on.regions[len(bands)].table_uri is not None, "the grid region carries its URI"
    assert on.asserted == sum(r.tokens_asserted for r in on.regions)
    assert on.escalated == sum(r.tokens_escalated for r in on.regions)
    # The rewrite is a RELABEL, not just a zeroing: a band whose ink the grid read no longer
    # claims to have escalated it. Task 4's driver branches on the verdict string.
    assert any(r.verdict == "superseded" for r in on.regions[:len(bands)])
    assert all(r.tokens_escalated == 0 for r in on.regions if r.verdict == "superseded")


@corpus_only
def test_adoption_never_touches_a_page_that_read_something():
    """apple page 0 asserts 20 cells. A partial reading is not a total failure, and
    adoption is scoped to total failure only."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(APPLE, 0, validate_shapes=False, datagrid_adopt=False)
    on = compile_tables(APPLE, 0, validate_shapes=False, datagrid_adopt=True)
    assert off.asserted > 0
    assert on.score == off.score
    assert sum(r.cells for r in on.regions) == sum(r.cells for r in off.regions) == 20


# --- the fifth oracle: cbh, a DECORATION-universe page with two tables --------------
# cbh-stem-2026-08-03.pdf page 0, transcribed (85 lines). Chosen because it is the only
# corpus page whose columns come from the DECORATION universe rather than alignment, so
# the drawn-rule path had no oracle at all until now.
#
# The page carries TWO tables:
#   A  the ship roster — four port panels, each with a 3-line header and vessel rows
#   B  a stock-at-port table (lines 75-80) with its own header and its own columns
#
# ENTRY ROWS of table A are the 45 vessel rows, PLUS the four per-panel volume totals
# (20, 42, 63, 74) — an aggregate is a row of the grid, the convention used for apple.
CBH_P0_VESSEL_ROWS = set(range(10, 20)) | set(range(26, 42)) | set(range(49, 63)) | set(range(69, 74))
CBH_P0_PANEL_TOTALS = {20, 42, 63, 74}
CBH_P0_TABLE_B = {75, 76, 77, 78, 79, 80}
CBH_P0_DATA = CBH_P0_VESSEL_ROWS | CBH_P0_PANEL_TOTALS          # 49 rows
CBH_P0_METADATA = set(range(85)) - CBH_P0_DATA - CBH_P0_TABLE_B  # 30 lines


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_reads_all_four_panels_as_one_grid():
    """The four panels are read as ONE grid — every vessel row across all four, from a
    single page-wide decoration universe. This is the shipped answer to 'one grid or
    four', and it needed no rejoin operation and no knowledge that the annotations name
    ports."""
    g = derive_data_grid(CBH, 0)
    assert g is not None and g.universe == "decoration"
    admitted = set(g.rows)
    missed = sorted(CBH_P0_VESSEL_ROWS - admitted)
    assert not missed, f"vessel rows missed: {missed}"
    assert len(CBH_P0_VESSEL_ROWS) == 45


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_admits_no_metadata():
    """SOUNDNESS: no title, notice, port annotation or reprinted header may enter."""
    g = derive_data_grid(CBH, 0)
    leaked = sorted(set(g.rows) & CBH_P0_METADATA)
    assert not leaked, f"metadata admitted as data: {leaked}"


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_table_b_leak_is_pinned_not_hidden():
    """LEAK, still open as R74: line 75 belongs to the SECOND table on the page (stock at
    port) and is admitted into the roster's grid. Recorded in the data-grid spec §8.4 as
    'cbh's rectangle spans a stacked panel'; tab:StackedGrids is defined and not derived.

    Its measure is in fact table A's exact grand total (374,904 + 737,289 + 660,363 +
    178,708 = 1,951,264 — spec 2026-08-09 §3.6), so the line carries two tables' ink."""
    g = derive_data_grid(CBH, 0)
    assert set(g.rows) & CBH_P0_TABLE_B == {75}, "the table-B leak changed"


@pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")
def test_cbh_p0_admits_the_four_panel_totals_by_arithmetic():
    """R75 CLOSED. The four per-panel volume totals carry a measure and no key, so the
    placement floor refused them as unplaceable. G8's aggregate witness admits them: each
    printed value is the EXACT Decimal sum of the rows it stands over.

    No label text is read — 'Total' is never printed on these lines at all."""
    g = derive_data_grid(CBH, 0)
    admitted = set(g.rows)
    missed = sorted(CBH_P0_PANEL_TOTALS - admitted)
    assert not missed, f"panel totals missed: {missed}"
    # the member counts are the four panels' vessel-row counts, and they sum to 45
    assert {k: len(v) for k, v in g.aggregates.items()} == {20: 10, 42: 16, 63: 14, 74: 5}
    assert sum(len(v) for v in g.aggregates.values()) == len(CBH_P0_VESSEL_ROWS) == 45
    # every entry row of table A, aggregates included
    assert CBH_P0_DATA <= admitted, f"missed: {sorted(CBH_P0_DATA - admitted)}"
    assert len(CBH_P0_DATA) == 49
